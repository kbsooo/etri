from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))
import geometry_mask_cv_experiments as geom  # noqa: E402
import label_powerset_prior_audit as lp  # noqa: E402
import quiet_feature_logit_postprocess_probe as qlp  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "sleep_date", "lifelog_date"]
SORT_KEY = ["subject_id", "lifelog_date"]


@dataclass(frozen=True)
class GateConfig:
    prior: lp.PriorConfig
    targets: tuple[str, ...]

    @property
    def name(self) -> str:
        return f"{'_'.join(self.targets)}__{self.prior.name}"


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1.0 - 1e-5)


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    yy = y.astype(float)
    pp = clip(p)
    return float(-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp)).mean())


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([loss_col(y[:, j], pred[:, j]) for j in range(len(TARGETS))]))


def gate_grid() -> list[GateConfig]:
    masks = [
        ("S2",),
        ("S2", "S4"),
        ("S2", "S3"),
        ("S1", "S2"),
        ("S1", "S2", "S3", "S4"),
        ("Q3", "S2"),
        ("Q1", "S2"),
        tuple(TARGETS),
    ]
    priors = []
    for mode in ["global_joint", "subject_joint", "global_qs", "subject_qs"]:
        for alpha in [0.15, 0.30, 0.50]:
            for weight in [0.08, 0.12, 0.18, 0.25]:
                for shrink in ([8.0, 16.0, 32.0] if mode.startswith("subject") else [0.0]):
                    priors.append(lp.PriorConfig(mode, alpha, weight, shrink))
    return [GateConfig(prior, mask) for prior in priors for mask in masks]


def apply_gate(ref: pd.DataFrame, rows: pd.DataFrame, pred: np.ndarray, cfg: GateConfig) -> np.ndarray:
    adjusted = lp.apply_prior(ref, rows, pred, cfg.prior)
    out = pred.copy()
    for target in cfg.targets:
        j = TARGETS.index(target)
        out[:, j] = adjusted[:, j]
    return clip(out)


def oof_gate(rows: pd.DataFrame, base: np.ndarray, cfg: GateConfig) -> np.ndarray:
    out = base.copy()
    for tr_idx, val_idx in qlp.make_subject_blocks(rows.reset_index(drop=True)):
        ref = rows.iloc[tr_idx].reset_index(drop=True)
        val = rows.iloc[val_idx].reset_index(drop=True)
        out[val_idx] = apply_gate(ref, val, base[val_idx], cfg)
    return clip(out)


def fixed_outer(train: pd.DataFrame, sub: pd.DataFrame, base: np.ndarray, repeats: int, prefix: str) -> pd.DataFrame:
    y = train[TARGETS].to_numpy(dtype=int)
    rows = []
    for cfg in gate_grid():
        deltas = []
        target_deltas = {target: [] for target in TARGETS}
        for tr_idx, val_idx, _fold in geom.geometry_folds(train, sub, n_repeats=repeats):
            ref = train.iloc[tr_idx].reset_index(drop=True)
            val = train.iloc[val_idx].reset_index(drop=True)
            pred = apply_gate(ref, val, base[val_idx], cfg)
            deltas.append(mean_loss(y[val_idx], pred) - mean_loss(y[val_idx], base[val_idx]))
            for j, target in enumerate(TARGETS):
                target_deltas[target].append(loss_col(y[val_idx, j], pred[:, j]) - loss_col(y[val_idx, j], base[val_idx, j]))
        row = {
            "config": cfg.name,
            "targets": ",".join(cfg.targets),
            "prior_mode": cfg.prior.mode,
            "alpha": cfg.prior.alpha,
            "weight": cfg.prior.weight,
            "subject_shrink": cfg.prior.subject_shrink,
            "outer_delta_mean": float(np.mean(deltas)),
            "outer_delta_median": float(np.median(deltas)),
            "outer_win_rate": float((np.asarray(deltas) < 0.0).mean()),
        }
        for target in TARGETS:
            row[f"{target}_delta_mean"] = float(np.mean(target_deltas[target]))
        rows.append(row)
    out = pd.DataFrame(rows).sort_values(["outer_delta_mean", "outer_win_rate"], ascending=[True, False])
    out.to_csv(OUT / f"{prefix}_fixed_outer.csv", index=False)
    return out


def save_candidate(prefix: str, row: pd.Series, train: pd.DataFrame, base: np.ndarray, base_submission: Path) -> Path:
    cfg = GateConfig(
        lp.PriorConfig(str(row["prior_mode"]), float(row["alpha"]), float(row["weight"]), float(row["subject_shrink"])),
        tuple(str(row["targets"]).split(",")),
    )
    sub = pd.read_csv(base_submission, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    assert sub[KEY].equals(sample[KEY])
    pred = apply_gate(train.reset_index(drop=True), sub.reset_index(drop=True), sub[TARGETS].to_numpy(dtype=float), cfg)
    out = sub.copy()
    out[TARGETS] = pred
    assert out[TARGETS].isna().sum().sum() == 0
    assert out.duplicated(KEY).sum() == 0
    file_path = OUT / f"submission_{prefix}_{cfg.name}.csv"
    out.to_csv(file_path, index=False)
    oof = oof_gate(train.reset_index(drop=True), base, cfg)
    np.save(OUT / f"final_{prefix}_{cfg.name}_oof.npy", oof)
    y = train[TARGETS].to_numpy(dtype=int)
    cv_rows = [
        {
            "target": target,
            "base_loss": loss_col(y[:, j], base[:, j]),
            "candidate_loss": loss_col(y[:, j], oof[:, j]),
            "delta": loss_col(y[:, j], oof[:, j]) - loss_col(y[:, j], base[:, j]),
        }
        for j, target in enumerate(TARGETS)
    ]
    cv_rows.append({"target": "mean", "base_loss": mean_loss(y, base), "candidate_loss": mean_loss(y, oof), "delta": mean_loss(y, oof) - mean_loss(y, base)})
    pd.DataFrame(cv_rows).to_csv(OUT / f"{prefix}_{cfg.name}_cv_estimate.csv", index=False)
    return file_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-oof", type=Path, default=OUT / "final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy")
    parser.add_argument("--base-submission", type=Path, default=OUT / "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv")
    parser.add_argument("--prefix", default="label_prior_gate_stage2")
    parser.add_argument("--outer-repeats", type=int, default=8)
    args = parser.parse_args()

    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(SORT_KEY).reset_index(drop=True)
    sub = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(SORT_KEY).reset_index(drop=True)
    base = clip(np.load(args.base_oof))
    assert base.shape == (len(train), len(TARGETS))

    result = fixed_outer(train, sub, base, args.outer_repeats, args.prefix)
    top = result.iloc[0]
    submission = ""
    if float(top["outer_delta_mean"]) < -0.00025 and float(top["outer_win_rate"]) >= 0.75:
        submission = str(save_candidate(args.prefix, top, train, base, args.base_submission))
    summary = pd.DataFrame(
        [
            {
                "best_config": str(top["config"]),
                "best_targets": str(top["targets"]),
                "best_outer_delta_mean": float(top["outer_delta_mean"]),
                "best_outer_win_rate": float(top["outer_win_rate"]),
                "submission": submission,
            }
        ]
    )
    summary.to_csv(OUT / f"{args.prefix}_summary.csv", index=False)
    print("[summary]")
    print(summary.round(9).to_string(index=False))
    print("\n[top]")
    print(result.head(30).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
