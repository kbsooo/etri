#!/usr/bin/env python3
"""E79 public-like row/block Q2/S3 amplitude gate probe.

E78 rejected source-subset reliability masks as an E75 amplitude repair. This
probe asks a different question before adding models: is E75's Q2/S3 sparse
amplitude safe only on row/block contexts implied by the observed train/test
calendar and nearest train-label flanks?

No submission is written by default.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "analysis_outputs"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, load_sub, logit  # noqa: E402
import gradient_consensus_posterior_probe as e63  # noqa: E402
import mixmin_hard_posterior_distillation_probe as e58  # noqa: E402
import mixmin_hard_raw_world_probe as e56  # noqa: E402
import q2_s3_localized_amplitude_gate_probe as e78  # noqa: E402
import q2_s3_sparse_gate_stability_probe as e74  # noqa: E402
import q2_s3_strict_cell_amplitude_probe as e69  # noqa: E402
import q2_s3_strict_cell_consensus_probe as e70  # noqa: E402
import q2_s3_target_amplitude_ridge_probe as e75  # noqa: E402
import q2_s3_target_amplitude_stability_probe as e76  # noqa: E402
import q2_s3_unified_strict_cell_consensus_probe as e71  # noqa: E402
import raw_block_target_dependency_probe as e55  # noqa: E402


SCAN_OUT = OUT / "q2_s3_public_like_rowblock_amplitude_probe_scan.csv"
SUMMARY_OUT = OUT / "q2_s3_public_like_rowblock_amplitude_probe_summary.csv"
MASK_OUT = OUT / "q2_s3_public_like_rowblock_amplitude_probe_mask_summary.csv"
CONTEXT_OUT = OUT / "q2_s3_public_like_rowblock_amplitude_probe_context_summary.csv"
REPORT_OUT = OUT / "q2_s3_public_like_rowblock_amplitude_probe_report.md"

Q2_IDX = TARGETS.index("Q2")
S3_IDX = TARGETS.index("S3")
QS_IDXS = e70.QS_IDXS

Q2_ALPHAS = [0.0, 4.0, 8.0, 12.0, 16.0, 20.0]
S3_ALPHAS = [16.0, 20.0, 24.0, 28.0, 32.0, 36.0]
LOCALIZATIONS = ["both", "q2_local_s3_full", "s3_local_q2_full"]
EPS = 1e-12


def stable_tag(pred: np.ndarray, prefix: str) -> str:
    return e76.e72.e68_tag(pred, prefix)


def base_qs_mask(full_unit: np.ndarray) -> np.ndarray:
    mask = np.zeros_like(full_unit, dtype=bool)
    mask[:, QS_IDXS] = np.abs(full_unit[:, QS_IDXS]) > EPS
    return mask


def target_mask_from_weights(full_unit: np.ndarray, q2_w: np.ndarray, s3_w: np.ndarray) -> np.ndarray:
    valid = base_qs_mask(full_unit)
    mask = np.zeros_like(full_unit, dtype=np.float64)
    mask[:, Q2_IDX] = np.clip(np.asarray(q2_w, dtype=np.float64), 0.0, 1.0) * valid[:, Q2_IDX]
    mask[:, S3_IDX] = np.clip(np.asarray(s3_w, dtype=np.float64), 0.0, 1.0) * valid[:, S3_IDX]
    return mask


def finite_gap(x: float) -> float:
    return float(x) if np.isfinite(x) else np.nan


def _norm_keys(df: pd.DataFrame) -> pd.DataFrame:
    return df[KEYS].astype(str).reset_index(drop=True)


def build_row_context(sample: pd.DataFrame) -> pd.DataFrame:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    sub = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    sub = sub.sort_values(KEYS).reset_index(drop=True)
    if not _norm_keys(sub).equals(_norm_keys(sample)):
        raise ValueError("submission sample key order differs from anchor sample")

    train_keys = train[KEYS + ["Q2", "S3"]].copy()
    train_keys["split"] = "train"
    train_keys["sub_order"] = -1
    sub_keys = sub[KEYS].copy()
    sub_keys["Q2"] = np.nan
    sub_keys["S3"] = np.nan
    sub_keys["split"] = "sub"
    sub_keys["sub_order"] = np.arange(len(sub_keys), dtype=int)
    combined = (
        pd.concat([train_keys, sub_keys], ignore_index=True)
        .sort_values(["subject_id", "lifelog_date", "sleep_date", "split"])
        .reset_index(drop=True)
    )

    subject_prior = train.groupby("subject_id")[["Q2", "S3"]].mean().rename(columns={"Q2": "subject_q2_rate", "S3": "subject_s3_rate"})
    rows: list[dict[str, Any]] = []
    for subject_id, group in combined.groupby("subject_id", sort=False):
        g = group.reset_index(drop=True)
        n = len(g)
        splits = g["split"].to_numpy()
        dates = pd.to_datetime(g["lifelog_date"]).to_numpy()
        q2 = g["Q2"].to_numpy(dtype=float)
        s3 = g["S3"].to_numpy(dtype=float)

        run_id = np.zeros(n, dtype=int)
        run_start = np.zeros(n, dtype=int)
        run_len = np.zeros(n, dtype=int)
        starts = [0]
        for i in range(1, n):
            if splits[i] != splits[i - 1]:
                starts.append(i)
        starts.append(n)
        for rid, (start, end) in enumerate(zip(starts[:-1], starts[1:])):
            run_id[start:end] = rid
            run_start[start:end] = start
            run_len[start:end] = end - start

        prev_train_gap = np.full(n, np.inf)
        next_train_gap = np.full(n, np.inf)
        prev_train_q2 = np.full(n, np.nan)
        next_train_q2 = np.full(n, np.nan)
        prev_train_s3 = np.full(n, np.nan)
        next_train_s3 = np.full(n, np.nan)

        last_date: np.datetime64 | None = None
        last_q2 = np.nan
        last_s3 = np.nan
        for i in range(n):
            if last_date is not None:
                prev_train_gap[i] = float((dates[i] - last_date) / np.timedelta64(1, "D"))
                prev_train_q2[i] = last_q2
                prev_train_s3[i] = last_s3
            if splits[i] == "train":
                last_date = dates[i]
                last_q2 = q2[i]
                last_s3 = s3[i]

        next_date: np.datetime64 | None = None
        nxt_q2 = np.nan
        nxt_s3 = np.nan
        for i in range(n - 1, -1, -1):
            if next_date is not None:
                next_train_gap[i] = float((next_date - dates[i]) / np.timedelta64(1, "D"))
                next_train_q2[i] = nxt_q2
                next_train_s3[i] = nxt_s3
            if splits[i] == "train":
                next_date = dates[i]
                nxt_q2 = q2[i]
                nxt_s3 = s3[i]

        subject_sub_counter = 0
        subject_sub_total = int((splits == "sub").sum())
        for i in range(n):
            if splits[i] != "sub":
                continue
            block_pos = i - run_start[i]
            block_n = int(run_len[i])
            prev_gap = np.inf if i == 0 else float((dates[i] - dates[i - 1]) / np.timedelta64(1, "D"))
            next_gap = np.inf if i == n - 1 else float((dates[i + 1] - dates[i]) / np.timedelta64(1, "D"))
            flank_q2_vals = [v for v in [prev_train_q2[i], next_train_q2[i]] if not np.isnan(v)]
            flank_s3_vals = [v for v in [prev_train_s3[i], next_train_s3[i]] if not np.isnan(v)]
            rows.append(
                {
                    "sub_order": int(g.loc[i, "sub_order"]),
                    "subject_id": subject_id,
                    "lifelog_date": pd.Timestamp(dates[i]),
                    "subject_sub_pos": subject_sub_counter,
                    "subject_sub_n": subject_sub_total,
                    "subject_sub_frac": subject_sub_counter / max(subject_sub_total - 1, 1),
                    "sub_run_id": int(run_id[i]),
                    "sub_block_pos": int(block_pos),
                    "sub_block_n": block_n,
                    "sub_block_frac": block_pos / max(block_n - 1, 1),
                    "prev_split": "none" if i == 0 else str(splits[i - 1]),
                    "next_split": "none" if i == n - 1 else str(splits[i + 1]),
                    "prev_gap_days": finite_gap(prev_gap),
                    "next_gap_days": finite_gap(next_gap),
                    "prev_train_gap": finite_gap(prev_train_gap[i]),
                    "next_train_gap": finite_gap(next_train_gap[i]),
                    "has_prev_train": bool(np.isfinite(prev_train_gap[i])),
                    "has_next_train": bool(np.isfinite(next_train_gap[i])),
                    "near_any_train_gap": finite_gap(min(prev_train_gap[i], next_train_gap[i])),
                    "prev_train_q2": prev_train_q2[i],
                    "next_train_q2": next_train_q2[i],
                    "prev_train_s3": prev_train_s3[i],
                    "next_train_s3": next_train_s3[i],
                    "flank_q2_mean": float(np.mean(flank_q2_vals)) if flank_q2_vals else np.nan,
                    "flank_s3_mean": float(np.mean(flank_s3_vals)) if flank_s3_vals else np.nan,
                }
            )
            subject_sub_counter += 1

    ctx = pd.DataFrame(rows).sort_values("sub_order").reset_index(drop=True)
    ctx = ctx.join(subject_prior, on="subject_id")
    if not np.array_equal(ctx["sub_order"].to_numpy(), np.arange(len(sample))):
        raise ValueError("row context failed to align with sample rows")
    return ctx


def add_mask(
    masks: list[dict[str, Any]],
    ctx: pd.DataFrame,
    full_unit: np.ndarray,
    source_name: str,
    mask_mode: str,
    q2_w: np.ndarray,
    s3_w: np.ndarray | None = None,
    threshold: float | None = None,
) -> None:
    if s3_w is None:
        s3_w = q2_w
    mask = target_mask_from_weights(full_unit, q2_w, s3_w)
    if np.abs(mask[:, QS_IDXS]).mean() <= EPS:
        return
    row_active = np.abs(mask[:, QS_IDXS]).max(axis=1) > 0.0
    if not row_active.any():
        return
    masks.append(
        {
            "source_name": source_name,
            "mask_mode": mask_mode,
            "mask": mask,
            "threshold": np.nan if threshold is None else float(threshold),
            "row_count": int(row_active.sum()),
            "row_coverage": float(row_active.mean()),
            "subjects": int(ctx.loc[row_active, "subject_id"].nunique()),
        }
    )


def qmask(ctx: pd.DataFrame, cond: pd.Series | np.ndarray) -> np.ndarray:
    return np.asarray(cond, dtype=np.float64)


def quantile_flags(x: np.ndarray, q: float, high: bool, positive_only: bool = False) -> tuple[np.ndarray, float]:
    vals = x[np.isfinite(x)]
    if positive_only:
        vals = vals[vals > EPS]
    if len(vals) == 0:
        return np.zeros_like(x, dtype=np.float64), np.nan
    thr = float(np.quantile(vals, q))
    return ((x >= thr) if high else (x <= thr)).astype(np.float64), thr


def build_rowblock_masks(ctx: pd.DataFrame, full_unit: np.ndarray) -> tuple[list[dict[str, Any]], pd.DataFrame, pd.DataFrame]:
    masks: list[dict[str, Any]] = []
    n = len(ctx)
    ones = np.ones(n, dtype=np.float64)
    add_mask(masks, ctx, full_unit, "control", "identity", ones)

    energy = np.abs(full_unit[:, QS_IDXS]).mean(axis=1)
    high_energy, high_thr = quantile_flags(energy, 0.70, True, positive_only=True)
    mid_high_energy, mid_thr = quantile_flags(energy, 0.50, True, positive_only=True)
    low_energy, low_thr = quantile_flags(energy, 0.50, False, positive_only=True)
    soft_energy_rank = np.zeros_like(energy, dtype=np.float64)
    positive_energy = energy > EPS
    soft_energy_rank[positive_energy] = pd.Series(energy[positive_energy]).rank(pct=True).to_numpy()
    add_mask(masks, ctx, full_unit, "unit_energy", "top30", high_energy, threshold=high_thr)
    add_mask(masks, ctx, full_unit, "unit_energy", "top50", mid_high_energy, threshold=mid_thr)
    add_mask(masks, ctx, full_unit, "unit_energy", "low50", low_energy, threshold=low_thr)
    add_mask(masks, ctx, full_unit, "unit_energy", "soft_rank_positive", soft_energy_rank)

    topology: list[tuple[str, np.ndarray]] = [
        ("two_flank_train", qmask(ctx, ctx["has_prev_train"] & ctx["has_next_train"])),
        ("one_flank_train", qmask(ctx, ctx["has_prev_train"] ^ ctx["has_next_train"])),
        ("near_train_le1", qmask(ctx, ctx["near_any_train_gap"].le(1))),
        ("near_train_le2", qmask(ctx, ctx["near_any_train_gap"].le(2))),
        ("near_train_le3", qmask(ctx, ctx["near_any_train_gap"].le(3))),
        ("block_edge", qmask(ctx, (ctx["sub_block_pos"].eq(0)) | (ctx["sub_block_pos"].eq(ctx["sub_block_n"] - 1)))),
        ("block_inner", qmask(ctx, (ctx["sub_block_pos"].gt(0)) & (ctx["sub_block_pos"].lt(ctx["sub_block_n"] - 1)))),
        ("block_first2", qmask(ctx, ctx["sub_block_pos"].le(1))),
        ("block_last2", qmask(ctx, (ctx["sub_block_n"] - 1 - ctx["sub_block_pos"]).le(1))),
        ("block_first_half", qmask(ctx, ctx["sub_block_frac"].le(0.50))),
        ("block_second_half", qmask(ctx, ctx["sub_block_frac"].ge(0.50))),
        ("short_block_le5", qmask(ctx, ctx["sub_block_n"].le(5))),
        ("long_block_ge10", qmask(ctx, ctx["sub_block_n"].ge(10))),
        ("subject_early_half", qmask(ctx, ctx["subject_sub_frac"].le(0.50))),
        ("subject_late_half", qmask(ctx, ctx["subject_sub_frac"].ge(0.50))),
    ]
    for name, weights in topology:
        add_mask(masks, ctx, full_unit, "topology", name, weights)
        add_mask(masks, ctx, full_unit, "topology_x_energy", f"{name}_energy_top50", weights * mid_high_energy)

    q2_prior_hi, q2_prior_thr = quantile_flags(ctx["subject_q2_rate"].to_numpy(dtype=float), 0.50, True)
    q2_prior_lo, _ = quantile_flags(ctx["subject_q2_rate"].to_numpy(dtype=float), 0.50, False)
    s3_prior_hi, s3_prior_thr = quantile_flags(ctx["subject_s3_rate"].to_numpy(dtype=float), 0.50, True)
    s3_prior_lo, _ = quantile_flags(ctx["subject_s3_rate"].to_numpy(dtype=float), 0.50, False)
    add_mask(masks, ctx, full_unit, "subject_prior", "q2_high", q2_prior_hi, threshold=q2_prior_thr)
    add_mask(masks, ctx, full_unit, "subject_prior", "q2_low", q2_prior_lo, threshold=q2_prior_thr)
    add_mask(masks, ctx, full_unit, "subject_prior", "s3_high", s3_prior_hi, threshold=s3_prior_thr)
    add_mask(masks, ctx, full_unit, "subject_prior", "s3_low", s3_prior_lo, threshold=s3_prior_thr)
    add_mask(masks, ctx, full_unit, "subject_prior_target", "q2_low_s3_high", q2_prior_lo, s3_prior_hi)
    add_mask(masks, ctx, full_unit, "subject_prior_target", "q2_high_s3_low", q2_prior_hi, s3_prior_lo)

    for subject_id in sorted(ctx["subject_id"].unique()):
        weights = qmask(ctx, ctx["subject_id"].eq(subject_id))
        add_mask(masks, ctx, full_unit, "subject_id", str(subject_id), weights)

    flank_q2 = ctx["flank_q2_mean"].to_numpy(dtype=float)
    flank_s3 = ctx["flank_s3_mean"].to_numpy(dtype=float)
    has_q2_flank = np.isfinite(flank_q2).astype(np.float64)
    has_s3_flank = np.isfinite(flank_s3).astype(np.float64)
    q2_flank_hi = (np.nan_to_num(flank_q2, nan=-1.0) >= 0.50).astype(np.float64)
    q2_flank_lo = (np.nan_to_num(flank_q2, nan=2.0) <= 0.50).astype(np.float64)
    s3_flank_hi = (np.nan_to_num(flank_s3, nan=-1.0) >= 0.50).astype(np.float64)
    s3_flank_lo = (np.nan_to_num(flank_s3, nan=2.0) <= 0.50).astype(np.float64)
    q2_flank_strong_hi = (np.nan_to_num(flank_q2, nan=-1.0) >= 1.0).astype(np.float64)
    q2_flank_strong_lo = (np.nan_to_num(flank_q2, nan=2.0) <= 0.0).astype(np.float64)
    s3_flank_strong_hi = (np.nan_to_num(flank_s3, nan=-1.0) >= 1.0).astype(np.float64)
    s3_flank_strong_lo = (np.nan_to_num(flank_s3, nan=2.0) <= 0.0).astype(np.float64)
    add_mask(masks, ctx, full_unit, "flank_prior", "has_q2_or_s3_flank", np.maximum(has_q2_flank, has_s3_flank))
    add_mask(masks, ctx, full_unit, "flank_prior", "q2_high", q2_flank_hi)
    add_mask(masks, ctx, full_unit, "flank_prior", "q2_low", q2_flank_lo)
    add_mask(masks, ctx, full_unit, "flank_prior", "s3_high", s3_flank_hi)
    add_mask(masks, ctx, full_unit, "flank_prior", "s3_low", s3_flank_lo)
    add_mask(masks, ctx, full_unit, "flank_prior", "q2_low_s3_high", q2_flank_lo * s3_flank_hi)
    add_mask(masks, ctx, full_unit, "flank_prior", "q2_high_s3_low", q2_flank_hi * s3_flank_lo)
    add_mask(masks, ctx, full_unit, "flank_prior_target", "q2_low_s3_high", q2_flank_lo, s3_flank_hi)
    add_mask(masks, ctx, full_unit, "flank_prior_target", "q2_strong_low_s3_strong_high", q2_flank_strong_lo, s3_flank_strong_hi)
    add_mask(masks, ctx, full_unit, "flank_prior_target", "q2_strong_high_s3_strong_low", q2_flank_strong_hi, s3_flank_strong_lo)

    rows = []
    valid = base_qs_mask(full_unit)
    for item in masks:
        mask = item["mask"]
        q2_valid = valid[:, Q2_IDX]
        s3_valid = valid[:, S3_IDX]
        row_active = np.abs(mask[:, QS_IDXS]).max(axis=1) > 0.0
        rows.append(
            {
                "source_name": item["source_name"],
                "mask_mode": item["mask_mode"],
                "threshold": item["threshold"],
                "row_count": item["row_count"],
                "row_coverage": item["row_coverage"],
                "subjects": item["subjects"],
                "mask_mean_q2": float(mask[:, Q2_IDX][q2_valid].mean()) if q2_valid.any() else 0.0,
                "mask_mean_s3": float(mask[:, S3_IDX][s3_valid].mean()) if s3_valid.any() else 0.0,
                "mask_active_q2": float((mask[:, Q2_IDX][q2_valid] > 0.0).mean()) if q2_valid.any() else 0.0,
                "mask_active_s3": float((mask[:, S3_IDX][s3_valid] > 0.0).mean()) if s3_valid.any() else 0.0,
                "active_subjects": ",".join(sorted(ctx.loc[row_active, "subject_id"].unique())),
            }
        )
    context_summary = (
        ctx.groupby("subject_id")
        .agg(
            rows=("subject_id", "size"),
            sub_blocks=("sub_run_id", "nunique"),
            mean_block_n=("sub_block_n", "mean"),
            q2_rate=("subject_q2_rate", "first"),
            s3_rate=("subject_s3_rate", "first"),
            flank_q2_mean=("flank_q2_mean", "mean"),
            flank_s3_mean=("flank_s3_mean", "mean"),
            near_train_le2=("near_any_train_gap", lambda x: float((x <= 2).mean())),
        )
        .reset_index()
    )
    return masks, pd.DataFrame(rows), context_summary


def localized_unit(full_unit: np.ndarray, mask: np.ndarray, localization: str) -> np.ndarray:
    out = np.zeros_like(full_unit)
    if localization == "both":
        out[:, QS_IDXS] = full_unit[:, QS_IDXS] * mask[:, QS_IDXS]
        return out
    if localization == "q2_local_s3_full":
        out[:, Q2_IDX] = full_unit[:, Q2_IDX] * mask[:, Q2_IDX]
        out[:, S3_IDX] = full_unit[:, S3_IDX]
        return out
    if localization == "s3_local_q2_full":
        out[:, Q2_IDX] = full_unit[:, Q2_IDX]
        out[:, S3_IDX] = full_unit[:, S3_IDX] * mask[:, S3_IDX]
        return out
    raise KeyError(localization)


def add_pred(preds: list[np.ndarray], seen: dict[str, int], pred: np.ndarray, prefix: str) -> tuple[int, str]:
    tag = stable_tag(pred, prefix)
    if tag in seen:
        return seen[tag], tag
    idx = len(preds)
    seen[tag] = idx
    preds.append(pred)
    return idx, tag


def build_candidates(
    base_pred: np.ndarray,
    base_logit: np.ndarray,
    full_unit: np.ndarray,
    masks: list[dict[str, Any]],
    mask_summary: pd.DataFrame,
) -> tuple[pd.DataFrame, list[np.ndarray]]:
    preds: list[np.ndarray] = []
    seen: dict[str, int] = {}
    bidx, base_tag = add_pred(preds, seen, base_pred, "e79_base_full_pool_")
    summary_lookup = {
        (str(row.source_name), str(row.mask_mode)): row
        for row in mask_summary.itertuples(index=False)
    }

    rows: list[dict[str, Any]] = []
    for item in masks:
        source_name = str(item["source_name"])
        mask_mode = str(item["mask_mode"])
        localizations = ["both"] if mask_mode == "identity" else LOCALIZATIONS
        summary = summary_lookup[(source_name, mask_mode)]
        for localization in localizations:
            unit = localized_unit(full_unit, item["mask"], localization)
            if np.abs(unit[:, QS_IDXS]).mean() <= EPS:
                continue
            for alpha_q2 in Q2_ALPHAS:
                for alpha_s3 in S3_ALPHAS:
                    if alpha_q2 == 0.0 and alpha_s3 == 0.0:
                        continue
                    move = np.zeros_like(unit)
                    move[:, Q2_IDX] = float(alpha_q2) * unit[:, Q2_IDX]
                    move[:, S3_IDX] = float(alpha_s3) * unit[:, S3_IDX]
                    if np.abs(move[:, QS_IDXS]).mean() <= EPS:
                        continue
                    pred = e70.clip_prob(e70.sigmoid(base_logit + move))
                    prefix = f"e79_{source_name}_{mask_mode}_{localization}_q2{alpha_q2:.1f}_s3{alpha_s3:.1f}_"
                    pred_index, tag = add_pred(preds, seen, pred, prefix)
                    rows.append(
                        {
                            "pred_index": pred_index,
                            "base_index": bidx,
                            "tag": tag,
                            "base_tag": base_tag,
                            "source_name": source_name,
                            "mask_mode": mask_mode,
                            "localization": localization,
                            "threshold": float(item["threshold"]) if pd.notna(item["threshold"]) else np.nan,
                            "alpha_q2": float(alpha_q2),
                            "alpha_s3": float(alpha_s3),
                            "alpha_sum": float(alpha_q2 + alpha_s3),
                            "alpha_max": float(max(alpha_q2, alpha_s3)),
                            "alpha_gap": float(abs(alpha_q2 - alpha_s3)),
                            "dominant_axis": e78.dominant_axis(float(alpha_q2), float(alpha_s3)),
                            "row_count": int(summary.row_count),
                            "row_coverage": float(summary.row_coverage),
                            "subjects": int(summary.subjects),
                            "mask_mean_q2": float(summary.mask_mean_q2),
                            "mask_mean_s3": float(summary.mask_mean_s3),
                            "mask_active_q2": float(summary.mask_active_q2),
                            "mask_active_s3": float(summary.mask_active_s3),
                            "unit_abs_q2": float(np.abs(unit[:, Q2_IDX]).mean()),
                            "unit_abs_s3": float(np.abs(unit[:, S3_IDX]).mean()),
                            "move_abs_q2": float(np.abs(move[:, Q2_IDX]).mean()),
                            "move_abs_s3": float(np.abs(move[:, S3_IDX]).mean()),
                            "move_abs_q2s3": float(np.abs(move[:, QS_IDXS]).mean()),
                        }
                    )
    return pd.DataFrame(rows), preds


def score_candidates(
    rows: pd.DataFrame,
    preds: list[np.ndarray],
    sample: pd.DataFrame,
    mixmin: np.ndarray,
    labels: np.ndarray,
    worlds: pd.DataFrame,
    views: dict[str, np.ndarray],
    state: e55.BaseState,
) -> pd.DataFrame:
    scan = e76.score_rows(rows, preds, sample, mixmin, labels, worlds, views, state)
    scan["beats_e75_local_all"] = scan["all_delta_vs_mixmin"] < e78.E75_LOCAL_DELTA
    scan["beats_e74_local_all"] = scan["all_delta_vs_mixmin"] < e78.E74_LOCAL_DELTA
    scan["beats_e73_local_all"] = scan["all_delta_vs_mixmin"] < e78.E73_LOCAL_DELTA
    return scan


def summarize(scan: pd.DataFrame) -> pd.DataFrame:
    rows = []
    group_cols = ["source_name", "mask_mode", "localization"]
    for key, group in scan.groupby(group_cols, sort=False):
        best = group.sort_values("all_delta_vs_mixmin").iloc[0]
        deploy = group[group["deployable_gate"]]
        strict = group[group["strict_gate"]]
        rows.append(
            {
                "source_name": key[0],
                "mask_mode": key[1],
                "localization": key[2],
                "rows": int(len(group)),
                "strict": int(group["strict_gate"].sum()),
                "deployable": int(group["deployable_gate"].sum()),
                "loose": int(group["loose_gate"].sum()),
                "beats_e75_local_all": int(group["beats_e75_local_all"].sum()),
                "deployable_beats_e75": int((group["deployable_gate"] & group["beats_e75_local_all"]).sum()),
                "best_all_delta_vs_mixmin": float(best["all_delta_vs_mixmin"]),
                "best_all_minus_base": float(group["all_minus_base"].min()),
                "best_worst_set_delta": float(group["worst_set_delta_vs_mixmin"].min()),
                "best_hidden_q2s3_minus_base": float(group["hidden_q2s3_mean_minus_base"].min()),
                "best_world_support_minus_base": float(group["world_support_minus_base"].min()),
                "best_block_win_rate": float(group["block_q2s3_beats_base_rate"].max()),
                "best_alpha_q2": float(best["alpha_q2"]),
                "best_alpha_s3": float(best["alpha_s3"]),
                "row_count": int(best["row_count"]),
                "subjects": int(best["subjects"]),
                "mask_active_q2": float(best["mask_active_q2"]),
                "mask_active_s3": float(best["mask_active_s3"]),
                "best_deployable_delta": float(deploy["all_delta_vs_mixmin"].min()) if len(deploy) else np.nan,
                "best_strict_delta": float(strict["all_delta_vs_mixmin"].min()) if len(strict) else np.nan,
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["deployable_beats_e75", "deployable", "strict", "loose", "best_all_delta_vs_mixmin"],
        ascending=[False, False, False, False, True],
    )


def write_report(scan: pd.DataFrame, summary: pd.DataFrame, mask_summary: pd.DataFrame, context_summary: pd.DataFrame) -> None:
    best = scan.sort_values("all_delta_vs_mixmin").head(30)
    deployable = scan[scan["deployable_gate"]].sort_values("all_delta_vs_mixmin").head(30)
    by_source = (
        scan.groupby("source_name")
        .agg(
            rows=("tag", "size"),
            strict=("strict_gate", "sum"),
            deployable=("deployable_gate", "sum"),
            loose=("loose_gate", "sum"),
            beats_e75=("beats_e75_local_all", "sum"),
            deployable_beats_e75=("deployable_gate", lambda x: int((x & scan.loc[x.index, "beats_e75_local_all"]).sum())),
            best_all=("all_delta_vs_mixmin", "min"),
            best_hidden=("hidden_q2s3_mean_minus_base", "min"),
            best_world=("world_support_minus_base", "min"),
            best_block=("block_q2s3_beats_base_rate", "max"),
        )
        .reset_index()
        .sort_values(["deployable_beats_e75", "deployable", "strict", "loose", "best_all"], ascending=[False, False, False, False, True])
    )
    lines = [
        "# E79 Public-Like Row/Block Q2/S3 Amplitude Probe",
        "",
        "## Observe",
        "",
        "E75's full-pool Q2/S3 sparse amplitude is still the best local all-combo amplitude sensor, while E76-E78 rejected source-subset consensus and posterior averaging as reliable amplitude repairs.",
        "",
        "The remaining oddity is that the actual data are not iid rows: submission rows appear in subject-specific calendar runs bracketed by train rows, so the context can include row position, flanking train labels, subject priors, and latent movement energy.",
        "",
        "## Wonder",
        "",
        "Is the E75 amplitude direction valid, but only on public-like row/block/flank contexts rather than across all Q2/S3 sparse cells?",
        "",
        "## Hypothesis",
        "",
        "H75: a hidden public-like subset is better approximated by row/block topology and nearest train-label flanks than by E76 source-subset reliability. If true, some rowblock-localized amplitude candidates should beat E75 local all-combo under the same deployable stress gates.",
        "",
        "## Method",
        "",
        f"- Base movement: E75 full-pool `{e74.POOL_NAME}` / `{e74.GATE}` unit delta.",
        f"- Q2 alpha grid: `{Q2_ALPHAS}`.",
        f"- S3 alpha grid: `{S3_ALPHAS}`.",
        "- Masks: topology, topology x E75 unit energy, subject priors, subject ids, nearest flanking train target priors, and target-specific Q2/S3 flank gates.",
        "- Stress: the same all-combo, hidden, world, block, raw-energy, strict/deployable gates used by E76-E78.",
        "",
        "## Context Summary",
        "",
        e56.markdown_table(context_summary),
        "",
        "## Mask Summary",
        "",
        e56.markdown_table(mask_summary.head(80)),
        "",
        "## Source Stress Summary",
        "",
        e56.markdown_table(by_source),
        "",
        "## Best Mask/Localization Rows",
        "",
        e56.markdown_table(summary.head(60)),
        "",
        "## Best Rows",
        "",
        e56.markdown_table(
            best[
                [
                    "source_name",
                    "mask_mode",
                    "localization",
                    "alpha_q2",
                    "alpha_s3",
                    "dominant_axis",
                    "row_count",
                    "subjects",
                    "all_delta_vs_mixmin",
                    "all_minus_base",
                    "worst_set_delta_vs_mixmin",
                    "sets_beating_base",
                    "sets_tail_neutral",
                    "hidden_q2s3_mean_minus_base",
                    "world_support_minus_base",
                    "block_q2s3_beats_base_rate",
                    "raw_energy_q_p90_minus_base",
                    "strict_gate",
                    "deployable_gate",
                    "loose_gate",
                    "beats_e75_local_all",
                ]
            ]
        ),
        "",
        "## Best Deployable Rows",
        "",
        e56.markdown_table(
            deployable[
                [
                    "source_name",
                    "mask_mode",
                    "localization",
                    "alpha_q2",
                    "alpha_s3",
                    "dominant_axis",
                    "row_count",
                    "subjects",
                    "all_delta_vs_mixmin",
                    "all_minus_base",
                    "worst_set_delta_vs_mixmin",
                    "sets_beating_base",
                    "sets_tail_neutral",
                    "hidden_q2s3_mean_minus_base",
                    "world_support_minus_base",
                    "block_q2s3_beats_base_rate",
                    "raw_energy_q_p90_minus_base",
                    "beats_e75_local_all",
                ]
            ]
        )
        if len(deployable)
        else "_None._",
        "",
        "## Decision",
        "",
    ]
    deploy_beats = int((scan["deployable_gate"] & scan["beats_e75_local_all"]).sum())
    strict_beats = int((scan["strict_gate"] & scan["beats_e75_local_all"]).sum())
    if deploy_beats:
        lines.append(f"- H75 remains live: `{deploy_beats}` deployable rows and `{strict_beats}` strict rows beat E75 local all-combo.")
    elif int(scan["deployable_gate"].sum()):
        lines.append("- H75 is weakened: row/block masks create deployable variants, but none beat E75 local all-combo.")
    else:
        lines.append("- H75 is strongly weakened: row/block masks do not create deployable variants under the current stress gate.")
    lines.extend(
        [
            "- This probe writes no submission by default. Materialize only if a candidate beats E75 and has a clearer stress profile than E72/E74/E75.",
            "",
            "## Outputs",
            "",
            f"- `{SCAN_OUT.relative_to(ROOT)}`",
            f"- `{SUMMARY_OUT.relative_to(ROOT)}`",
            f"- `{MASK_OUT.relative_to(ROOT)}`",
            f"- `{CONTEXT_OUT.relative_to(ROOT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    mixmin = load_sub(e56.MIXMIN_FILE, sample)[TARGETS].to_numpy(dtype=np.float64)
    a2c8 = load_sub(A2C8, sample)[TARGETS].to_numpy(dtype=np.float64)
    raw_prior, _ = e56.raw_prior_from_e54(sample)
    labels = np.load(e56.LABEL_NPZ_OUT, allow_pickle=True)["labels"].astype(np.float64)
    worlds = pd.read_csv(e56.WORLD_OUT)
    state = e55.build_base_state()
    if not state.sample[KEYS].reset_index(drop=True).equals(sample[KEYS].reset_index(drop=True)):
        raise ValueError("sample key mismatch between anchor sample and hidden-rate state")
    views, _ = e63.hidden_row_views(state, sample, mixmin, a2c8)
    components = e58.posterior_components(labels, worlds, raw_prior, mixmin)
    print("loaded shared state", flush=True)

    strict = e69.strict_rows()
    cells = e71.unique_strict_cells(strict)
    bases, _cands, deltas = e71.reconstruct_unified_arrays(cells, sample, mixmin, raw_prior, views, components)
    _e75_rows, e75_preds, meta = e75.build_target_alpha_candidates(cells, bases, deltas)
    full_unit = meta["gated_delta"]
    base_pred = e75_preds[0]
    base_logit = logit(base_pred)
    print(f"loaded E75 unit cells={len(meta['pool_idxs'])}", flush=True)

    ctx = build_row_context(sample)
    masks, mask_summary, context_summary = build_rowblock_masks(ctx, full_unit)
    rows, preds = build_candidates(base_pred, base_logit, full_unit, masks, mask_summary)
    print(f"built rowblock rows={len(rows)} masks={len(masks)} unique_preds={len(preds)}", flush=True)

    scan = score_candidates(rows, preds, sample, mixmin, labels, worlds, views, state)
    summary = summarize(scan)
    scan.to_csv(SCAN_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    mask_summary.to_csv(MASK_OUT, index=False)
    context_summary.to_csv(CONTEXT_OUT, index=False)
    write_report(scan, summary, mask_summary, context_summary)
    print(
        f"rows={len(scan)} strict={int(scan['strict_gate'].sum())} "
        f"deployable={int(scan['deployable_gate'].sum())} "
        f"loose={int(scan['loose_gate'].sum())} "
        f"deployable_beats_e75={int((scan['deployable_gate'] & scan['beats_e75_local_all']).sum())} "
        f"best_all={float(scan['all_delta_vs_mixmin'].min()):.6g} "
        f"wrote={REPORT_OUT.relative_to(ROOT)}",
        flush=True,
    )


if __name__ == "__main__":
    main()
