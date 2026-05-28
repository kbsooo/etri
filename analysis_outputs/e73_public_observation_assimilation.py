#!/usr/bin/env python3
"""Assimilate the public LB observation for the E73 sparse Q2/S3 sensor.

E73 was submitted after E72 opened the first non-none deployable Q2/S3 sparse
gate. The public score worsened versus mixmin. This script treats that public
LB as a sensor, not as a leaderboard rank, and asks what label-support
constraints the E73 movement implies.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, load_sub, logit  # noqa: E402
import mixmin_hard_raw_world_probe as e56  # noqa: E402
import q2_s3_public_like_rowblock_amplitude_probe as e79  # noqa: E402


MIXMIN_PUBLIC_LB = 0.5763066405
E73_PUBLIC_LB = 0.5764077772
LOCAL_E73_DELTA = -0.0000105458
E73_FILE = OUT / "submission_e72_topabs50_q2s3_gate_4e48cba2.csv"

SUMMARY_OUT = OUT / "e73_public_observation_assimilation_summary.csv"
TARGET_OUT = OUT / "e73_public_observation_assimilation_target_summary.csv"
CONTEXT_OUT = OUT / "e73_public_observation_assimilation_context_summary.csv"
ACTIVE_OUT = OUT / "e73_public_observation_assimilation_active_cell_summary.csv"
REPORT_OUT = OUT / "e73_public_observation_assimilation_report.md"


def loss_delta_terms(old: np.ndarray, new: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    old = np.clip(old, 1.0e-6, 1.0 - 1.0e-6)
    new = np.clip(new, 1.0e-6, 1.0 - 1.0e-6)
    delta_if_one = -np.log(new / old)
    delta_if_zero = -np.log((1.0 - new) / (1.0 - old))
    return delta_if_zero, delta_if_one


def common_beneficial_fraction(min_sum: float, max_sum: float, observed_sum: float) -> float:
    denom = max_sum - min_sum
    if abs(denom) <= 1.0e-12:
        return np.nan
    return float((max_sum - observed_sum) / denom)


def summarize_group(name: str, d0: np.ndarray, d1: np.ndarray, moved: np.ndarray, observed_sum: float) -> dict[str, Any]:
    idx = np.asarray(moved, dtype=bool)
    if not idx.any():
        return {
            "group": name,
            "active_cells": 0,
            "min_loss_sum_all_beneficial": 0.0,
            "max_loss_sum_all_adverse": 0.0,
            "zero_loss_common_benefit_frac": np.nan,
            "implied_common_benefit_frac_if_all_public_delta_from_group": np.nan,
        }
    min_terms = np.minimum(d0[idx], d1[idx])
    max_terms = np.maximum(d0[idx], d1[idx])
    min_sum = float(min_terms.sum())
    max_sum = float(max_terms.sum())
    return {
        "group": name,
        "active_cells": int(idx.sum()),
        "min_loss_sum_all_beneficial": min_sum,
        "max_loss_sum_all_adverse": max_sum,
        "zero_loss_common_benefit_frac": common_beneficial_fraction(min_sum, max_sum, 0.0),
        "implied_common_benefit_frac_if_all_public_delta_from_group": common_beneficial_fraction(
            min_sum,
            max_sum,
            observed_sum,
        ),
        "observed_sum_if_full_250x7_public": float(observed_sum),
        "observed_sum_position_0beneficial_1adverse": float((observed_sum - min_sum) / (max_sum - min_sum))
        if abs(max_sum - min_sum) > 1.0e-12
        else np.nan,
    }


def build_active_cells(sample: pd.DataFrame, mixmin: np.ndarray, e73: np.ndarray, ctx: pd.DataFrame) -> pd.DataFrame:
    old_logit = logit(mixmin)
    new_logit = logit(e73)
    logit_delta = new_logit - old_logit
    d0, d1 = loss_delta_terms(mixmin, e73)
    rows: list[dict[str, Any]] = []
    for row_idx in range(mixmin.shape[0]):
        for target_idx, target in enumerate(TARGETS):
            if abs(float(logit_delta[row_idx, target_idx])) <= 1.0e-12:
                continue
            direction = "increase" if logit_delta[row_idx, target_idx] > 0 else "decrease"
            beneficial_label = 1 if direction == "increase" else 0
            rows.append(
                {
                    "row_idx": row_idx,
                    "target": target,
                    "subject_id": str(sample.loc[row_idx, "subject_id"]),
                    "sleep_date": str(sample.loc[row_idx, "sleep_date"]),
                    "lifelog_date": str(sample.loc[row_idx, "lifelog_date"]),
                    "mixmin": float(mixmin[row_idx, target_idx]),
                    "e73": float(e73[row_idx, target_idx]),
                    "prob_delta": float(e73[row_idx, target_idx] - mixmin[row_idx, target_idx]),
                    "logit_delta": float(logit_delta[row_idx, target_idx]),
                    "direction": direction,
                    "beneficial_label": beneficial_label,
                    "loss_delta_if_y0": float(d0[row_idx, target_idx]),
                    "loss_delta_if_y1": float(d1[row_idx, target_idx]),
                    "beneficial_loss_delta": float(min(d0[row_idx, target_idx], d1[row_idx, target_idx])),
                    "adverse_loss_delta": float(max(d0[row_idx, target_idx], d1[row_idx, target_idx])),
                }
            )
    active = pd.DataFrame(rows)
    if active.empty:
        return active
    ctx_cols = [
        "subject_id",
        "subject_sub_frac",
        "sub_block_pos",
        "sub_block_n",
        "sub_block_frac",
        "near_any_train_gap",
        "flank_q2_mean",
        "flank_s3_mean",
        "subject_q2_rate",
        "subject_s3_rate",
    ]
    ctx2 = ctx.reset_index().rename(columns={"index": "row_idx"})[["row_idx", *ctx_cols]]
    return active.merge(ctx2, on=["row_idx", "subject_id"], how="left")


def context_summary(active: pd.DataFrame) -> pd.DataFrame:
    if active.empty:
        return pd.DataFrame()
    return (
        active.groupby(["subject_id", "target", "direction"], dropna=False)
        .agg(
            active_cells=("row_idx", "size"),
            mean_abs_logit_delta=("logit_delta", lambda x: float(np.abs(x).mean())),
            mean_prob_delta=("prob_delta", "mean"),
            beneficial_loss_sum=("beneficial_loss_delta", "sum"),
            adverse_loss_sum=("adverse_loss_delta", "sum"),
            subject_q2_rate=("subject_q2_rate", "first"),
            subject_s3_rate=("subject_s3_rate", "first"),
            flank_q2_mean=("flank_q2_mean", "mean"),
            flank_s3_mean=("flank_s3_mean", "mean"),
            near_train_gap_mean=("near_any_train_gap", "mean"),
        )
        .reset_index()
        .sort_values(["target", "active_cells", "subject_id"], ascending=[True, False, True])
    )


def target_summary(active: pd.DataFrame, d0: np.ndarray, d1: np.ndarray, moved: np.ndarray, observed_sum: float) -> pd.DataFrame:
    qs_moved = np.zeros_like(moved, dtype=bool)
    qs_moved[:, [TARGETS.index("Q2"), TARGETS.index("S3")]] = moved[:, [TARGETS.index("Q2"), TARGETS.index("S3")]]
    non_qs_moved = moved & ~qs_moved
    rows = [
        summarize_group("all_moved", d0, d1, moved, observed_sum),
        summarize_group("Q2+S3", d0, d1, qs_moved, observed_sum),
        summarize_group("non_Q2S3", d0, d1, non_qs_moved, observed_sum),
    ]
    for target in ["Q2", "S3"]:
        t_idx = TARGETS.index(target)
        rows.append(summarize_group(target, d0[:, t_idx], d1[:, t_idx], moved[:, t_idx], observed_sum))
    target_df = pd.DataFrame(rows)
    if not active.empty:
        shape = (
            active.groupby("target")
            .agg(
                increased=("direction", lambda x: int((x == "increase").sum())),
                decreased=("direction", lambda x: int((x == "decrease").sum())),
                mean_abs_logit_delta=("logit_delta", lambda x: float(np.abs(x).mean())),
                mean_abs_prob_delta=("prob_delta", lambda x: float(np.abs(x).mean())),
                beneficial_loss_sum=("beneficial_loss_delta", "sum"),
                adverse_loss_sum=("adverse_loss_delta", "sum"),
            )
            .reset_index()
            .rename(columns={"target": "group"})
        )
        target_df = target_df.merge(shape, on="group", how="left")
    return target_df


def write_report(summary: pd.DataFrame, target: pd.DataFrame, active: pd.DataFrame, context: pd.DataFrame) -> None:
    public_delta = E73_PUBLIC_LB - MIXMIN_PUBLIC_LB
    lines = [
        "# E73 Public Observation Assimilation",
        "",
        "## Observe",
        "",
        f"`submission_e72_topabs50_q2s3_gate_4e48cba2.csv` scored public LB `{E73_PUBLIC_LB:.10f}`.",
        f"The active frontier `submission_mixmin_0c916bb4.csv` remains `{MIXMIN_PUBLIC_LB:.10f}`.",
        "",
        "## Wonder",
        "",
        "What does the public worsening say about the sparse Q2/S3 latent, beyond simply calling the file worse?",
        "",
        "## Result",
        "",
        e56.markdown_table(summary),
        "",
        "## Target Constraint",
        "",
        e56.markdown_table(target),
        "",
        "## Active Cell Summary",
        "",
        e56.markdown_table(active.head(80)),
        "",
        "## Context Summary",
        "",
        e56.markdown_table(context.head(80)),
        "",
        "## Interpretation",
        "",
        f"- Public delta vs mixmin: `{public_delta:+.10f}`.",
        f"- Local all-combo proxy had expected delta `{LOCAL_E73_DELTA:+.10f}`, so the public response reversed sign and was `{abs(public_delta / LOCAL_E73_DELTA):.3f}x` the local edge magnitude.",
        "- The submitted file is not a pure Q2/S3 graft: it moves all seven targets versus mixmin. Therefore the public result rejects the combined E72 base plus sparse Q2/S3 file, not the isolated Q2/S3 sign by itself.",
        "- E74/E75 should not be submitted next as simple amplitude follow-ups until their non-Q2/S3 base movement is separated from their Q2/S3 movement.",
        "- The remaining live question is whether a pure mixmin-anchored Q2/S3 graft preserves the local signal without the broad base movement that public just punished.",
        "",
        "## Outputs",
        "",
        f"- `{SUMMARY_OUT.relative_to(ROOT)}`",
        f"- `{TARGET_OUT.relative_to(ROOT)}`",
        f"- `{CONTEXT_OUT.relative_to(ROOT)}`",
        f"- `{ACTIVE_OUT.relative_to(ROOT)}`",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    mixmin = load_sub(e56.MIXMIN_FILE, sample)[TARGETS].to_numpy(dtype=np.float64)
    e73 = load_sub(E73_FILE, sample)[TARGETS].to_numpy(dtype=np.float64)
    public_delta = E73_PUBLIC_LB - MIXMIN_PUBLIC_LB
    observed_sum = public_delta * mixmin.size

    logit_delta = logit(e73) - logit(mixmin)
    moved = np.abs(logit_delta) > 1.0e-12
    d0, d1 = loss_delta_terms(mixmin, e73)
    ctx = e79.build_row_context(sample)
    active = build_active_cells(sample, mixmin, e73, ctx)
    target = target_summary(active, d0, d1, moved, observed_sum)
    context = context_summary(active)
    summary = pd.DataFrame(
        [
            {
                "submission": E73_FILE.name,
                "mixmin_public_lb": MIXMIN_PUBLIC_LB,
                "e73_public_lb": E73_PUBLIC_LB,
                "public_delta_vs_mixmin": public_delta,
                "local_all_combo_delta_vs_mixmin": LOCAL_E73_DELTA,
                "public_to_local_edge_ratio": abs(public_delta / LOCAL_E73_DELTA),
                "test_rows": int(mixmin.shape[0]),
                "targets": int(mixmin.shape[1]),
                "total_cells_if_full_public": int(mixmin.size),
                "active_moved_cells": int(moved.sum()),
                "active_rows": int((moved.any(axis=1)).sum()),
                "active_targets": ",".join([t for i, t in enumerate(TARGETS) if moved[:, i].any()]),
                "observed_loss_sum_if_full_250x7_public": observed_sum,
            }
        ]
    )
    summary.to_csv(SUMMARY_OUT, index=False)
    target.to_csv(TARGET_OUT, index=False)
    context.to_csv(CONTEXT_OUT, index=False)
    active.to_csv(ACTIVE_OUT, index=False)
    write_report(summary, target, active, context)
    print(
        f"public_delta={public_delta:+.10f} active_cells={int(moved.sum())} "
        f"active_rows={int((moved.any(axis=1)).sum())} wrote={REPORT_OUT.relative_to(ROOT)}",
        flush=True,
    )


if __name__ == "__main__":
    main()
