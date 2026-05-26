from __future__ import annotations

import argparse
import itertools
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))
import geometry_mask_cv_experiments as geom  # noqa: E402
import quiet_feature_logit_postprocess_probe as qlp  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "sleep_date", "lifelog_date"]
SORT_KEY = ["subject_id", "lifelog_date"]

Q_IDX = np.array([0, 1, 2], dtype=int)
S_IDX = np.array([3, 4, 5, 6], dtype=int)
ALL_PATTERNS = np.asarray(list(itertools.product([0, 1], repeat=7)), dtype=int)
Q_PATTERNS = np.asarray(list(itertools.product([0, 1], repeat=3)), dtype=int)
S_PATTERNS = np.asarray(list(itertools.product([0, 1], repeat=4)), dtype=int)


@dataclass(frozen=True)
class PriorConfig:
    mode: str
    alpha: float
    weight: float
    subject_shrink: float
    min_inner_delta: float = -0.0001

    @property
    def name(self) -> str:
        return f"{self.mode}_a{self.alpha:g}_w{self.weight:g}_sh{self.subject_shrink:g}"


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1.0 - 1e-5)


def logsumexp(x: np.ndarray, axis: int = 1) -> np.ndarray:
    m = np.max(x, axis=axis, keepdims=True)
    return np.squeeze(m, axis=axis) + np.log(np.exp(x - m).sum(axis=axis))


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    yy = y.astype(float)
    pp = clip(p)
    return float(-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp)).mean())


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([loss_col(y[:, j], pred[:, j]) for j in range(len(TARGETS))]))


def pattern_index(y: np.ndarray) -> np.ndarray:
    powers = (2 ** np.arange(y.shape[1] - 1, -1, -1)).astype(int)
    return (y.astype(int) @ powers).astype(int)


def pattern_probs(y: np.ndarray, n_patterns: int, laplace: float = 0.5) -> np.ndarray:
    counts = np.bincount(pattern_index(y), minlength=n_patterns).astype(float)
    probs = (counts + laplace) / (counts.sum() + laplace * n_patterns)
    return probs


def subject_pattern_probs(ref: pd.DataFrame, cols: list[str], n_patterns: int, shrink: float) -> dict[str, np.ndarray]:
    y = ref[cols].to_numpy(dtype=int)
    global_probs = pattern_probs(y, n_patterns)
    out = {}
    for sid, g in ref.groupby("subject_id", sort=False):
        yy = g[cols].to_numpy(dtype=int)
        counts = np.bincount(pattern_index(yy), minlength=n_patterns).astype(float)
        probs = (counts + shrink * global_probs) / (counts.sum() + shrink)
        out[str(sid)] = probs
    out["__global__"] = global_probs
    return out


def posterior_marginals(p: np.ndarray, patterns: np.ndarray, prior: np.ndarray, alpha: float) -> np.ndarray:
    pp = clip(p)
    log_ind = patterns[None, :, :] * np.log(pp[:, None, :]) + (1 - patterns[None, :, :]) * np.log(1.0 - pp[:, None, :])
    score = log_ind.sum(axis=2) + alpha * np.log(np.maximum(prior[None, :], 1e-12))
    score = score - logsumexp(score, axis=1)[:, None]
    post = np.exp(score)
    return clip(post @ patterns)


def apply_prior(ref: pd.DataFrame, rows: pd.DataFrame, pred: np.ndarray, cfg: PriorConfig) -> np.ndarray:
    pred = clip(pred)
    adjusted = pred.copy()
    if cfg.mode == "global_joint":
        prior = pattern_probs(ref[TARGETS].to_numpy(dtype=int), len(ALL_PATTERNS))
        adjusted = posterior_marginals(pred, ALL_PATTERNS, prior, cfg.alpha)
    elif cfg.mode == "subject_joint":
        priors = subject_pattern_probs(ref, TARGETS, len(ALL_PATTERNS), cfg.subject_shrink)
        for sid in rows["subject_id"].astype(str).unique():
            mask = rows["subject_id"].astype(str).eq(sid).to_numpy()
            prior = priors.get(str(sid), priors["__global__"])
            adjusted[mask] = posterior_marginals(pred[mask], ALL_PATTERNS, prior, cfg.alpha)
    elif cfg.mode in {"global_qs", "subject_qs"}:
        if cfg.mode == "global_qs":
            q_global = pattern_probs(ref[["Q1", "Q2", "Q3"]].to_numpy(dtype=int), len(Q_PATTERNS))
            s_global = pattern_probs(ref[["S1", "S2", "S3", "S4"]].to_numpy(dtype=int), len(S_PATTERNS))
            adjusted[:, Q_IDX] = posterior_marginals(pred[:, Q_IDX], Q_PATTERNS, q_global, cfg.alpha)
            adjusted[:, S_IDX] = posterior_marginals(pred[:, S_IDX], S_PATTERNS, s_global, cfg.alpha)
        else:
            q_priors = subject_pattern_probs(ref, ["Q1", "Q2", "Q3"], len(Q_PATTERNS), cfg.subject_shrink)
            s_priors = subject_pattern_probs(ref, ["S1", "S2", "S3", "S4"], len(S_PATTERNS), cfg.subject_shrink)
            for sid in rows["subject_id"].astype(str).unique():
                mask = rows["subject_id"].astype(str).eq(sid).to_numpy()
                q_prior = q_priors.get(str(sid), q_priors["__global__"])
                s_prior = s_priors.get(str(sid), s_priors["__global__"])
                row_idx = np.where(mask)[0]
                adjusted[np.ix_(row_idx, Q_IDX)] = posterior_marginals(pred[mask][:, Q_IDX], Q_PATTERNS, q_prior, cfg.alpha)
                adjusted[np.ix_(row_idx, S_IDX)] = posterior_marginals(pred[mask][:, S_IDX], S_PATTERNS, s_prior, cfg.alpha)
    else:
        raise ValueError(cfg.mode)
    return clip((1.0 - cfg.weight) * pred + cfg.weight * adjusted)


def config_grid() -> list[PriorConfig]:
    configs = []
    for mode in ["global_joint", "subject_joint", "global_qs", "subject_qs"]:
        for alpha in [0.15, 0.30, 0.50, 0.80, 1.20]:
            for weight in [0.03, 0.05, 0.08, 0.12, 0.18, 0.25]:
                for shrink in ([8.0, 16.0, 32.0] if mode.startswith("subject") else [0.0]):
                    configs.append(PriorConfig(mode, alpha, weight, shrink))
    return configs


def oof_apply(rows: pd.DataFrame, base: np.ndarray, cfg: PriorConfig) -> np.ndarray:
    out = np.zeros_like(base)
    for tr_idx, val_idx in qlp.make_subject_blocks(rows.reset_index(drop=True)):
        ref = rows.iloc[tr_idx].reset_index(drop=True)
        val = rows.iloc[val_idx].reset_index(drop=True)
        out[val_idx] = apply_prior(ref, val, base[val_idx], cfg)
    return clip(out)


def select_inner(inner: pd.DataFrame, inner_base: np.ndarray) -> tuple[PriorConfig | None, float, float, pd.DataFrame]:
    y = inner[TARGETS].to_numpy(dtype=int)
    base_loss = mean_loss(y, inner_base)
    rows = []
    best_cfg: PriorConfig | None = None
    best_loss = base_loss
    for cfg in config_grid():
        pred = oof_apply(inner, inner_base, cfg)
        loss = mean_loss(y, pred)
        rows.append({"config": cfg.name, "mode": cfg.mode, "alpha": cfg.alpha, "weight": cfg.weight, "subject_shrink": cfg.subject_shrink, "inner_loss": loss, "inner_delta": loss - base_loss})
        if loss < best_loss:
            best_loss = loss
            best_cfg = cfg
    detail = pd.DataFrame(rows).sort_values("inner_loss")
    if best_cfg is None or (best_loss - base_loss) > best_cfg.min_inner_delta:
        return None, base_loss, best_loss, detail
    return best_cfg, base_loss, best_loss, detail


def fixed_config_outer(train: pd.DataFrame, sub: pd.DataFrame, base: np.ndarray, outer_repeats: int, prefix: str) -> pd.DataFrame:
    y = train[TARGETS].to_numpy(dtype=int)
    rows = []
    for cfg in config_grid():
        deltas = []
        target_deltas = {target: [] for target in TARGETS}
        for tr_idx, val_idx, _fold in geom.geometry_folds(train, sub, n_repeats=outer_repeats):
            ref = train.iloc[tr_idx].reset_index(drop=True)
            val = train.iloc[val_idx].reset_index(drop=True)
            pred = apply_prior(ref, val, base[val_idx], cfg)
            deltas.append(mean_loss(y[val_idx], pred) - mean_loss(y[val_idx], base[val_idx]))
            for j, target in enumerate(TARGETS):
                target_deltas[target].append(loss_col(y[val_idx, j], pred[:, j]) - loss_col(y[val_idx, j], base[val_idx, j]))
        row = {
            "config": cfg.name,
            "mode": cfg.mode,
            "alpha": cfg.alpha,
            "weight": cfg.weight,
            "subject_shrink": cfg.subject_shrink,
            "outer_delta_mean": float(np.mean(deltas)),
            "outer_delta_median": float(np.median(deltas)),
            "outer_win_rate": float((np.asarray(deltas) < 0.0).mean()),
        }
        for target in TARGETS:
            row[f"{target}_delta_mean"] = float(np.mean(target_deltas[target]))
        rows.append(row)
    out = pd.DataFrame(rows).sort_values(["outer_delta_mean", "outer_win_rate"], ascending=[True, False])
    out.to_csv(OUT / f"{prefix}_fixed_config_outer.csv", index=False)
    return out


def nested_outer(train: pd.DataFrame, sub: pd.DataFrame, base: np.ndarray, outer_repeats: int, prefix: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    y = train[TARGETS].to_numpy(dtype=int)
    folds = []
    selected_rows = []
    inner_details = []
    for tr_idx, val_idx, fold in geom.geometry_folds(train, sub, n_repeats=outer_repeats):
        inner = train.iloc[tr_idx].reset_index(drop=True)
        holdout = train.iloc[val_idx].reset_index(drop=True)
        cfg, inner_base_loss, inner_best_loss, detail = select_inner(inner, base[tr_idx])
        detail.insert(0, "fold", fold)
        inner_details.append(detail)
        if cfg is None:
            pred = base[val_idx].copy()
            cfg_name = "identity"
        else:
            pred = apply_prior(inner, holdout, base[val_idx], cfg)
            cfg_name = cfg.name
        base_loss = mean_loss(y[val_idx], base[val_idx])
        cand_loss = mean_loss(y[val_idx], pred)
        row = {
            "fold": fold,
            "selected_config": cfg_name,
            "inner_base_loss": inner_base_loss,
            "inner_best_loss": inner_best_loss,
            "inner_delta": inner_best_loss - inner_base_loss,
            "base_loss": base_loss,
            "candidate_loss": cand_loss,
            "outer_delta": cand_loss - base_loss,
        }
        for j, target in enumerate(TARGETS):
            row[f"{target}_delta"] = loss_col(y[val_idx, j], pred[:, j]) - loss_col(y[val_idx, j], base[val_idx, j])
        folds.append(row)
        selected_rows.append({"fold": fold, "selected_config": cfg_name})
        print(f"[{fold}] selected={cfg_name} inner_delta={row['inner_delta']:.6f} outer_delta={row['outer_delta']:.6f}", flush=True)
    fold_df = pd.DataFrame(folds)
    selected = pd.DataFrame(selected_rows)
    detail_df = pd.concat(inner_details, ignore_index=True)
    fold_df.to_csv(OUT / f"{prefix}_nested_folds.csv", index=False)
    selected.to_csv(OUT / f"{prefix}_nested_selected.csv", index=False)
    detail_df.to_csv(OUT / f"{prefix}_nested_inner_details.csv", index=False)
    return fold_df, selected, detail_df


def save_submission(prefix: str, cfg: PriorConfig, train: pd.DataFrame, sub_file: Path) -> None:
    sub = pd.read_csv(sub_file, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    assert sub[KEY].equals(sample[KEY])
    pred = apply_prior(train.reset_index(drop=True), sub.reset_index(drop=True), sub[TARGETS].to_numpy(dtype=float), cfg)
    out = sub.copy()
    out[TARGETS] = pred
    assert out[TARGETS].isna().sum().sum() == 0
    assert out.duplicated(KEY).sum() == 0
    out.to_csv(OUT / f"submission_{prefix}_{cfg.name}.csv", index=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-oof", type=Path, default=OUT / "final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy")
    parser.add_argument("--base-submission", type=Path, default=OUT / "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv")
    parser.add_argument("--prefix", default="label_powerset_prior_stage2")
    parser.add_argument("--outer-repeats", type=int, default=5)
    args = parser.parse_args()

    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(SORT_KEY).reset_index(drop=True)
    sub_sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(SORT_KEY).reset_index(drop=True)
    base = clip(np.load(args.base_oof))
    assert base.shape == (len(train), len(TARGETS))

    nested_folds, _selected, _detail = nested_outer(train, sub_sample, base, args.outer_repeats, args.prefix)
    fixed = fixed_config_outer(train, sub_sample, base, args.outer_repeats, args.prefix)
    summary = pd.DataFrame(
        [
            {
                "base_loss": float(nested_folds["base_loss"].mean()),
                "nested_loss": float(nested_folds["candidate_loss"].mean()),
                "nested_delta_mean": float(nested_folds["outer_delta"].mean()),
                "nested_win_rate": float((nested_folds["outer_delta"] < 0.0).mean()),
                "best_fixed_config": str(fixed.iloc[0]["config"]),
                "best_fixed_outer_delta_mean": float(fixed.iloc[0]["outer_delta_mean"]),
                "best_fixed_outer_win_rate": float(fixed.iloc[0]["outer_win_rate"]),
            }
        ]
    )
    summary.to_csv(OUT / f"{args.prefix}_summary.csv", index=False)

    best = fixed.iloc[0]
    if float(best["outer_delta_mean"]) < -0.00025 and float(best["outer_win_rate"]) >= 0.75:
        cfg = PriorConfig(str(best["mode"]), float(best["alpha"]), float(best["weight"]), float(best["subject_shrink"]))
        save_submission(args.prefix, cfg, train, args.base_submission)

    print("\n[summary]")
    print(summary.round(9).to_string(index=False))
    print("\n[fixed top]")
    print(fixed.head(20).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
