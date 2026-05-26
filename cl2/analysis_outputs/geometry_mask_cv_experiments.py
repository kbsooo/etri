from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss

sys.path.append(str(Path(__file__).resolve().parent))
import block_rate_smoother_experiments as brs  # noqa: E402
import breakthrough_structure_probe as bsp  # noqa: E402
import calibration_experiments as cal  # noqa: E402
import deep_dive_analysis as d  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
TARGETS = d.TARGETS
KEY = d.KEY


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1 - 1e-5)


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([log_loss(y[:, j], clip(pred[:, j]), labels=[0, 1]) for j in range(y.shape[1])]))


def per_target_loss(y: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    return {target: float(log_loss(y[:, j], clip(pred[:, j]), labels=[0, 1])) for j, target in enumerate(TARGETS)}


@dataclass(frozen=True)
class BridgeConfig:
    name: str
    shrink: float
    alpha: float
    tau: float
    source: str
    use_subject: bool = True
    same_boost: float = 0.0


def actual_submission_lengths(train: pd.DataFrame, sub: pd.DataFrame) -> dict[str, list[int]]:
    blocks = bsp.split_block_summary(train, sub)
    hidden = blocks[blocks["split"].eq("submission")]
    lengths: dict[str, list[int]] = {}
    for sid, g in hidden.groupby("subject_id", sort=False):
        lengths[str(sid)] = [int(x) for x in g["n"].to_numpy()]
    return lengths


def non_overlapping_mask(n: int, lengths: list[int], rng: np.random.Generator, target_frac: float) -> np.ndarray:
    target_n = max(1, int(round(n * target_frac)))
    order = list(rng.permutation(lengths))
    mask = np.zeros(n, dtype=bool)
    attempts = 0
    while int(mask.sum()) < target_n and attempts < max(80, 8 * len(order)):
        attempts += 1
        length = int(order[attempts % len(order)])
        length = max(1, min(length, max(1, n - 2)))
        if n - length <= 2:
            start = 0
        else:
            start = int(rng.integers(1, n - length))
        end = start + length
        lo = max(0, start - 1)
        hi = min(n, end + 1)
        if mask[lo:hi].any():
            continue
        mask[start:end] = True
    if not mask.any():
        mask[int(rng.integers(0, n))] = True
    return mask


def geometry_folds(
    train: pd.DataFrame,
    sub: pd.DataFrame,
    n_repeats: int = 8,
    target_frac: float = 0.22,
    seed: int = 260526,
) -> list[tuple[np.ndarray, np.ndarray, str]]:
    lengths = actual_submission_lengths(train, sub)
    rows = train.sort_values(KEY).copy()
    pos_by_index = {idx: pos for pos, idx in enumerate(rows.index.to_numpy(dtype=int))}
    folds: list[tuple[np.ndarray, np.ndarray, str]] = []
    for repeat in range(n_repeats):
        rng = np.random.default_rng(seed + repeat)
        val_positions: list[int] = []
        for sid, g in rows.groupby("subject_id", sort=False):
            locs = [pos_by_index[idx] for idx in g.index.to_numpy(dtype=int)]
            sid_lengths = lengths.get(str(sid)) or [max(1, int(round(len(locs) * target_frac)))]
            mask = non_overlapping_mask(len(locs), sid_lengths, rng, target_frac)
            val_positions.extend([locs[i] for i, is_val in enumerate(mask) if is_val])
        val_idx = rows.iloc[sorted(val_positions)].index.to_numpy(dtype=int)
        tr_idx = train.index.difference(val_idx).to_numpy(dtype=int)
        folds.append((tr_idx, val_idx, f"geom_r{repeat:02d}"))
    return folds


def row_bridge(ref: pd.DataFrame, rows: pd.DataFrame, cfg: BridgeConfig) -> np.ndarray:
    subj = cal.subject_prior(ref, rows, cfg.shrink)
    pred = subj.copy() if cfg.use_subject else np.full_like(subj, ref[TARGETS].mean().to_numpy(dtype=float))
    ref_by_subject = {
        str(sid): g.sort_values("lifelog_date").reset_index(drop=True)
        for sid, g in ref.groupby("subject_id", sort=False)
    }
    for i, row in rows.reset_index(drop=True).iterrows():
        sid = str(row["subject_id"])
        day = pd.Timestamp(row["lifelog_date"])
        hist = ref_by_subject.get(sid)
        if hist is None or hist.empty:
            continue
        before = hist[hist["lifelog_date"] < day].tail(1)
        after = hist[hist["lifelog_date"] > day].head(1)
        values = []
        weights = []
        if not before.empty and cfg.source in {"both", "prev"}:
            gap = max(int((day - before.iloc[-1]["lifelog_date"]).days), 1)
            values.append(before.iloc[-1][TARGETS].to_numpy(dtype=float))
            weights.append(float(np.exp(-gap / cfg.tau)))
        if not after.empty and cfg.source in {"both", "next"}:
            gap = max(int((after.iloc[0]["lifelog_date"] - day).days), 1)
            values.append(after.iloc[0][TARGETS].to_numpy(dtype=float))
            weights.append(float(np.exp(-gap / cfg.tau)))
        if not values:
            continue
        local = np.average(np.vstack(values), weights=np.asarray(weights), axis=0)
        if cfg.same_boost > 0.0 and len(values) == 2:
            prev = values[0]
            nxt = values[1]
            same = prev == nxt
            local = np.where(same, (1.0 - cfg.same_boost) * local + cfg.same_boost * prev, local)
        pred[i] = (1.0 - cfg.alpha) * pred[i] + cfg.alpha * local
    return clip(pred)


def bridge_configs() -> list[BridgeConfig]:
    out: list[BridgeConfig] = []
    for alpha in [0.15, 0.25, 0.35, 0.50, 0.70]:
        for tau in [3.0, 7.0, 14.0]:
            out.append(BridgeConfig(f"bridge_both_a{alpha:g}_tau{tau:g}", 16.0, alpha, tau, "both"))
            out.append(BridgeConfig(f"bridge_prev_a{alpha:g}_tau{tau:g}", 16.0, alpha, tau, "prev"))
    for alpha in [0.25, 0.35, 0.50]:
        for same_boost in [0.20, 0.35, 0.50]:
            out.append(BridgeConfig(f"bridge_same_a{alpha:g}_boost{same_boost:g}", 16.0, alpha, 7.0, "both", True, same_boost))
    return out


def evaluate_geometry_cv(train: pd.DataFrame, sub: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    folds = geometry_folds(train, sub)
    y = train[TARGETS].to_numpy(dtype=int)
    preds: dict[str, np.ndarray] = {
        "subject_prior_s16": np.zeros_like(y, dtype=float),
        "temporal_base": np.zeros_like(y, dtype=float),
    }
    cfg_map = {cfg.name: cfg for cfg in bridge_configs()}
    for name in cfg_map:
        preds[name] = np.zeros_like(y, dtype=float)
    block_cfgs = {
        "block_s32_a0.9_w10_eq": brs.parse_config("s32_a0.9_w10_eq_boost0"),
        "block_s32_a0.5_w10_eq": brs.parse_config("s32_a0.5_w10_eq_boost0"),
        "block_s16_a0.35_w10_gap_boost0.2": brs.parse_config("s16_a0.35_w10_gap_boost0.2"),
    }
    for name in block_cfgs:
        preds[name] = np.zeros_like(y, dtype=float)

    fold_rows = []
    for tr_idx, val_idx, fold_name in folds:
        ref = train.iloc[tr_idx].copy().reset_index(drop=True)
        val = train.iloc[val_idx].copy().reset_index(drop=True)
        preds["subject_prior_s16"][val_idx] = cal.subject_prior(ref, val, 16.0)
        preds["temporal_base"][val_idx] = cal.temporal_base(ref, val)
        for name, cfg in cfg_map.items():
            preds[name][val_idx] = row_bridge(ref, val, cfg)
        for name, cfg in block_cfgs.items():
            preds[name][val_idx] = brs.block_smoother(ref, val, cfg)
        fold_rows.append({"fold": fold_name, "train_rows": len(tr_idx), "val_rows": len(val_idx)})
        print(f"[geometry cv] {fold_name} train={len(tr_idx)} val={len(val_idx)}", flush=True)

    rows = []
    covered = np.zeros(len(train), dtype=bool)
    for _, val_idx, _ in folds:
        covered[val_idx] = True
    if not covered.all():
        print(f"[geometry cv] scoring repeated-mask rows={int(covered.sum())}/{len(train)}", flush=True)
    for name, pred in preds.items():
        row = {"model": name, "mean": mean_loss(y[covered], pred[covered])}
        row.update(per_target_loss(y[covered], pred[covered]))
        rows.append(row)
    result = pd.DataFrame(rows).sort_values("mean")
    fold_summary = pd.DataFrame(fold_rows)
    return result, fold_summary


def make_geometry_bridge_submission(train: pd.DataFrame, sub: pd.DataFrame, result: pd.DataFrame) -> pd.DataFrame:
    base_path = OUT / "submission_hybrid_0p598_repro.csv"
    out = pd.read_csv(base_path, parse_dates=["sleep_date", "lifelog_date"])
    out = out.sort_values(KEY).reset_index(drop=True)
    top = result[~result["model"].isin(["subject_prior_s16", "temporal_base"])].iloc[0]
    model_name = str(top["model"])
    if model_name.startswith("bridge_"):
        cfg = {cfg.name: cfg for cfg in bridge_configs()}[model_name]
        geom = row_bridge(train, sub, cfg)
    elif model_name.startswith("block_"):
        cfg_lookup = {
            "block_s32_a0.9_w10_eq": brs.parse_config("s32_a0.9_w10_eq_boost0"),
            "block_s32_a0.5_w10_eq": brs.parse_config("s32_a0.5_w10_eq_boost0"),
            "block_s16_a0.35_w10_gap_boost0.2": brs.parse_config("s16_a0.35_w10_gap_boost0.2"),
        }
        geom = brs.block_smoother(train, sub, cfg_lookup[model_name])
    else:
        raise ValueError(model_name)

    # Only write an audit candidate for targets where the geometry-mask CV beats
    # the 0.598 OOF source by at least a visible margin. This file is not a new
    # default unless the report says so.
    baseline = pd.read_csv(OUT / "hybrid_0p598_repro_cv_estimate.csv")
    base_loss = dict(zip(baseline["target"], baseline["cv_loss"]))
    replaced = []
    for target in TARGETS:
        if float(top[target]) + 0.002 < float(base_loss[target]):
            out[target] = geom[:, TARGETS.index(target)]
            replaced.append(target)
    out[TARGETS] = out[TARGETS].clip(1e-5, 1 - 1e-5)
    out.to_csv(OUT / "submission_geometry_bridge_audit.csv", index=False)
    pd.DataFrame([{"model": model_name, "replaced_targets": ",".join(replaced)}]).to_csv(
        OUT / "geometry_bridge_submission_note.csv", index=False
    )
    return out


def main() -> None:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    sub = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    train = train.sort_values(KEY).reset_index(drop=True)
    sub = sub.sort_values(KEY).reset_index(drop=True)
    result, folds = evaluate_geometry_cv(train, sub)
    result.to_csv(OUT / "geometry_mask_cv_results.csv", index=False)
    folds.to_csv(OUT / "geometry_mask_cv_folds.csv", index=False)
    out = make_geometry_bridge_submission(train, sub, result)
    print(result.head(20).round(6).to_string(index=False))
    print("wrote", OUT / "geometry_mask_cv_results.csv")
    print("audit submission", OUT / "submission_geometry_bridge_audit.csv", out.shape)


if __name__ == "__main__":
    main()
