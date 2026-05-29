#!/usr/bin/env python3
"""E163: candidate-universe edge breadth and hidden-label fragility.

E162 showed that the repaired E154 sibling branch is one-cell fragile. This
audit asks whether that is a local branch artifact or a broader plateau law.

For selected known-public anchors and live post-E95 candidates, measure the
hard-label swing concentration of each file-to-file move. If the actual public
delta or local expected edge is smaller than one or a few top cell swings, then
candidate ranking is underresolved without new public feedback.
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

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, load_sub, locate  # noqa: E402
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402
import e162_branch_readability_flip_thresholds as e162  # noqa: E402


SUMMARY_OUT = OUT / "e163_candidate_edge_breadth_summary.csv"
TOP_CELLS_OUT = OUT / "e163_candidate_edge_breadth_top_cells.csv"
REPORT_OUT = OUT / "e163_candidate_edge_breadth_report.md"

PUBLIC_READABLE_GUARD = 2.0e-6
E95_EDGE_OVER_MIXMIN = 0.0000153107
N_PUBLIC_CELLS = 250 * len(TARGETS)
EPS = 1.0e-12


PUBLIC_LB = {
    "a2c8": 0.5774393210,
    "raw05": 0.5775263072,
    "mixmin": 0.5763066405,
    "e72": 0.5764077772,
    "e95": 0.5762913298,
    "e101": 0.5763003660,
}

CANDIDATES = {
    "a2c8": A2C8,
    "raw05": "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv",
    "mixmin": "submission_mixmin_0c916bb4.csv",
    "e72": "submission_e72_topabs50_q2s3_gate_4e48cba2.csv",
    "e85": "submission_e85_inverse_conflict_pruned_58b23ed1.csv",
    "e86": "submission_e86_e85_consensus_a3f7c96f.csv",
    "e89": "submission_e89_e72decontam_00d7807f.csv",
    "e90": "submission_e90_e72pareto_28925de5.csv",
    "e95": "submission_e95_hardtail_541e3973.csv",
    "e101": "submission_e101_q2s3tail_177569bc.csv",
    "e142": "submission_e142_transferclip_09a92236.csv",
    "e143": "submission_e143_activeq2s3repair_68ca656f.csv",
    "e144": "submission_e144_activeboundary_d7b4b331.csv",
    "e154": "submission_e154_s3repair_9f2e2e73.csv",
    "e155": "submission_e155_bodytemp_d27e7965.csv",
    "e156": "submission_e156_targetaxis_757546d2.csv",
    "e157": "submission_e157_lowbodypareto_bd67930d.csv",
}

PAIR_SPECS = [
    ("known_transition", "mixmin", "a2c8"),
    ("known_transition", "raw05", "a2c8"),
    ("known_transition", "e95", "mixmin"),
    ("known_transition", "e101", "e95"),
    ("known_transition", "e101", "mixmin"),
    ("known_transition", "e72", "mixmin"),
    ("known_transition", "e72", "e95"),
    ("pre_e95_live_vs_mixmin", "e85", "mixmin"),
    ("pre_e95_live_vs_mixmin", "e86", "mixmin"),
    ("pre_e95_live_vs_mixmin", "e89", "mixmin"),
    ("pre_e95_live_vs_mixmin", "e90", "mixmin"),
    ("post_e95_live_vs_e95", "e142", "e95"),
    ("post_e95_live_vs_e95", "e143", "e95"),
    ("post_e95_live_vs_e95", "e144", "e95"),
    ("post_e95_live_vs_e95", "e154", "e95"),
    ("post_e95_live_vs_e95", "e155", "e95"),
    ("post_e95_live_vs_e95", "e156", "e95"),
    ("post_e95_live_vs_e95", "e157", "e95"),
    ("repaired_sibling", "e154", "e144"),
    ("repaired_sibling", "e154", "e155"),
    ("repaired_sibling", "e157", "e155"),
    ("repaired_sibling", "e156", "e155"),
]


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def load_aligned(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    return clip_prob(load_sub(file_name, sample)[TARGETS].to_numpy(dtype=np.float64))


def sign(x: float) -> int:
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0


def cells_for_threshold(swings: np.ndarray, threshold: float) -> int:
    return e162.min_cells_for_threshold(swings, threshold)


def md_table(frame: pd.DataFrame, cols: list[str], n: int = 40, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    keep = [c for c in cols if c in frame.columns]
    return e138.md_table(frame[keep].head(n), floatfmt)


def pair_metrics(
    pair_group: str,
    name_new: str,
    name_base: str,
    p_new: np.ndarray,
    p_base: np.ndarray,
    priors: dict[str, np.ndarray],
) -> tuple[dict[str, Any], pd.DataFrame]:
    moved = np.abs(p_new - p_base) > EPS
    row_idx, target_idx = np.where(moved)
    record: dict[str, Any] = {
        "pair_group": pair_group,
        "new": name_new,
        "base": name_base,
        "file_new": CANDIDATES[name_new],
        "file_base": CANDIDATES[name_base],
        "public_new": PUBLIC_LB.get(name_new, np.nan),
        "public_base": PUBLIC_LB.get(name_base, np.nan),
        "actual_public_delta": np.nan,
        "moved_cells": int(len(row_idx)),
    }
    if name_new in PUBLIC_LB and name_base in PUBLIC_LB:
        record["actual_public_delta"] = float(PUBLIC_LB[name_new] - PUBLIC_LB[name_base])
        record["actual_abs_delta"] = abs(float(record["actual_public_delta"]))
        record["actual_delta_vs_e95_edge_abs_ratio"] = float(record["actual_abs_delta"] / E95_EDGE_OVER_MIXMIN)
    else:
        record["actual_abs_delta"] = np.nan
        record["actual_delta_vs_e95_edge_abs_ratio"] = np.nan

    if len(row_idx) == 0:
        return record, pd.DataFrame()

    dy1, dy0 = e162.hard_loss_deltas(p_new[row_idx, target_idx], p_base[row_idx, target_idx])
    dy1_s = dy1 / N_PUBLIC_CELLS
    dy0_s = dy0 / N_PUBLIC_CELLS
    swing = np.abs(dy1_s - dy0_s)
    total_swing = float(swing.sum())
    top_sorted = np.sort(swing)[::-1]
    support_label = np.where(dy1_s < dy0_s, 1, 0)
    support_delta = np.minimum(dy1_s, dy0_s)
    adverse_delta = np.maximum(dy1_s, dy0_s)

    record.update(
        {
            "moved_rows": int(len(np.unique(row_idx))),
            "targets_moved": ",".join(TARGETS[j] for j in sorted(set(target_idx))),
            "all_support_delta": float(support_delta.sum()),
            "all_adverse_delta": float(adverse_delta.sum()),
            "total_swing": total_swing,
            "top1_swing": float(top_sorted[0]) if len(top_sorted) else 0.0,
            "top3_swing": float(top_sorted[:3].sum()) if len(top_sorted) else 0.0,
            "top5_swing": float(top_sorted[:5].sum()) if len(top_sorted) else 0.0,
            "top10_swing": float(top_sorted[:10].sum()) if len(top_sorted) else 0.0,
            "top25_swing": float(top_sorted[:25].sum()) if len(top_sorted) else 0.0,
            "top1_swing_share": float(top_sorted[0] / total_swing) if total_swing > 0 and len(top_sorted) else 0.0,
            "top5_swing_share": float(top_sorted[:5].sum() / total_swing) if total_swing > 0 else 0.0,
            "cells_for_2e6_guard": cells_for_threshold(swing, PUBLIC_READABLE_GUARD),
            "cells_for_e95_edge": cells_for_threshold(swing, E95_EDGE_OVER_MIXMIN),
        }
    )
    actual_abs = float(record["actual_abs_delta"]) if np.isfinite(record["actual_abs_delta"]) else np.nan
    if np.isfinite(actual_abs):
        record["cells_for_actual_abs_delta"] = cells_for_threshold(swing, actual_abs)
        record["top1_over_actual_abs_delta"] = float(record["top1_swing"] / max(actual_abs, 1.0e-15))
        record["top5_over_actual_abs_delta"] = float(record["top5_swing"] / max(actual_abs, 1.0e-15))
        record["actual_abs_as_total_swing_share"] = float(actual_abs / max(total_swing, 1.0e-15))
        record["one_cell_can_flip_actual_delta"] = bool(record["top1_swing"] >= actual_abs)
        record["five_cells_can_flip_actual_delta"] = bool(record["top5_swing"] >= actual_abs)
    else:
        record["cells_for_actual_abs_delta"] = np.nan
        record["top1_over_actual_abs_delta"] = np.nan
        record["top5_over_actual_abs_delta"] = np.nan
        record["actual_abs_as_total_swing_share"] = np.nan
        record["one_cell_can_flip_actual_delta"] = np.nan
        record["five_cells_can_flip_actual_delta"] = np.nan

    for prior_name, arr in priors.items():
        py = arr[row_idx, target_idx]
        expected = py * dy1_s + (1.0 - py) * dy0_s
        support_prob = np.where(support_label == 1, py, 1.0 - py)
        expected_sum = float(expected.sum())
        record[f"expected_delta_{prior_name}"] = expected_sum
        record[f"cells_to_flip_expected_{prior_name}"] = cells_for_threshold(swing, abs(expected_sum))
        record[f"support_prob_mean_{prior_name}"] = float(support_prob.mean())
        record[f"support_prob_swing_weighted_{prior_name}"] = (
            float(np.average(support_prob, weights=swing)) if total_swing > 0 else np.nan
        )
    if np.isfinite(record["actual_public_delta"]):
        record["actual_focus_sign_match"] = bool(
            sign(float(record["actual_public_delta"])) == sign(float(record["expected_delta_focus_mean"]))
        )
    else:
        record["actual_focus_sign_match"] = np.nan

    top = pd.DataFrame(
        {
            "pair_group": pair_group,
            "new": name_new,
            "base": name_base,
            "sub_idx": row_idx.astype(int),
            "target": [TARGETS[j] for j in target_idx],
            "target_idx": target_idx.astype(int),
            "delta_y1": dy1_s,
            "delta_y0": dy0_s,
            "swing": swing,
            "support_label": support_label.astype(int),
            "support_delta": support_delta,
            "adverse_delta": adverse_delta,
            "p_y1_focus_mean": priors["focus_mean"][row_idx, target_idx],
            "p_y1_subject": priors["subject"][row_idx, target_idx],
            "p_y1_nearest_hard085": priors["nearest_hard085"][row_idx, target_idx],
        }
    ).sort_values("swing", ascending=False)
    top["swing_rank"] = np.arange(1, len(top) + 1)
    return record, top.head(20)


def load_predictions(sample: pd.DataFrame) -> dict[str, np.ndarray]:
    preds: dict[str, np.ndarray] = {}
    missing: list[str] = []
    for name, file_name in CANDIDATES.items():
        if locate(file_name) is None:
            missing.append(f"{name}:{file_name}")
            continue
        preds[name] = load_aligned(file_name, sample)
    if missing:
        print({"missing_candidates": missing})
    return preds


def write_report(summary: pd.DataFrame, top_cells: pd.DataFrame) -> None:
    known = summary[summary["pair_group"].eq("known_transition")].copy()
    live = summary[summary["pair_group"].eq("post_e95_live_vs_e95")].copy()
    siblings = summary[summary["pair_group"].eq("repaired_sibling")].copy()
    public_known = known[known["actual_public_delta"].notna()].copy()

    one_cell_known = int(public_known["one_cell_can_flip_actual_delta"].fillna(False).sum())
    five_cell_known = int(public_known["five_cells_can_flip_actual_delta"].fillna(False).sum())
    live_one_cell_guard = int((live["cells_for_2e6_guard"] == 1).sum())
    live_count = int(len(live))

    lines = [
        "# E163 Candidate Edge Breadth Audit",
        "",
        "## Question",
        "",
        "Was E162's one-cell fragility only an E154 sibling artifact, or is the current post-E95 plateau broadly hidden-label-resolution limited?",
        "",
        "## Summary",
        "",
        f"- known public transitions audited: `{len(public_known)}`.",
        f"- known transitions whose whole actual public delta can be moved by one top hard-label cell: `{one_cell_known}/{len(public_known)}`.",
        f"- known transitions whose whole actual public delta can be moved by five top hard-label cells: `{five_cell_known}/{len(public_known)}`.",
        f"- live post-E95 candidates with one-cell `2e-6` readability fragility: `{live_one_cell_guard}/{live_count}`.",
        "",
        "## Known Public Transitions",
        "",
        md_table(
            known.sort_values("actual_abs_delta", ascending=False),
            [
                "new",
                "base",
                "actual_public_delta",
                "actual_delta_vs_e95_edge_abs_ratio",
                "moved_cells",
                "expected_delta_focus_mean",
                "top1_swing",
                "top5_swing",
                "cells_for_actual_abs_delta",
                "top1_over_actual_abs_delta",
                "top5_over_actual_abs_delta",
                "actual_focus_sign_match",
                "targets_moved",
            ],
            30,
        ),
        "",
        "## Live Post-E95 Candidates Versus E95",
        "",
        md_table(
            live.sort_values(["expected_delta_focus_mean", "top1_swing"]),
            [
                "new",
                "base",
                "moved_cells",
                "moved_rows",
                "expected_delta_focus_mean",
                "support_prob_swing_weighted_focus_mean",
                "top1_swing",
                "top5_swing",
                "cells_for_2e6_guard",
                "cells_for_e95_edge",
                "cells_to_flip_expected_focus_mean",
                "targets_moved",
            ],
            40,
        ),
        "",
        "## Repaired Sibling Controls",
        "",
        md_table(
            siblings.sort_values("top1_swing", ascending=False),
            [
                "new",
                "base",
                "moved_cells",
                "expected_delta_focus_mean",
                "top1_swing",
                "top5_swing",
                "cells_for_2e6_guard",
                "cells_to_flip_expected_focus_mean",
                "targets_moved",
            ],
            40,
        ),
        "",
        "## Top Swing Cells",
        "",
        md_table(
            top_cells.sort_values(["pair_group", "new", "base", "swing_rank"]),
            [
                "pair_group",
                "new",
                "base",
                "swing_rank",
                "sub_idx",
                "target",
                "swing",
                "delta_y1",
                "delta_y0",
                "support_label",
                "p_y1_focus_mean",
            ],
            80,
        ),
        "",
        "## Decision",
        "",
        "E162 is not just an E154-local curiosity. The mixmin breakthrough is broad, but the post-mixmin/E95 frontier refinements live at a scale where one or a few hidden row-target labels can dominate the measured public delta. This supports the plateau diagnosis: candidate selection is hard-label-resolution and calibration-tail limited, not model-capacity limited.",
        "",
        "No new submission is created by E163. The next public sensor remains `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv`, because it asks the repaired all-four branch question. E155/E157/E156 remain post-feedback instruments.",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    preds = load_predictions(sample)
    priors = e162.prior_arrays(sample)

    rows: list[dict[str, Any]] = []
    top_frames: list[pd.DataFrame] = []
    for pair_group, new, base in PAIR_SPECS:
        if new not in preds or base not in preds:
            continue
        rec, top = pair_metrics(pair_group, new, base, preds[new], preds[base], priors)
        rows.append(rec)
        if not top.empty:
            top_frames.append(top)
    summary = pd.DataFrame(rows)
    top_cells = pd.concat(top_frames, ignore_index=True) if top_frames else pd.DataFrame()
    summary.to_csv(SUMMARY_OUT, index=False)
    top_cells.to_csv(TOP_CELLS_OUT, index=False)
    write_report(summary, top_cells)

    known = summary[summary["pair_group"].eq("known_transition")].copy()
    live = summary[summary["pair_group"].eq("post_e95_live_vs_e95")].copy()
    print(
        {
            "pairs": int(len(summary)),
            "known_transitions": int(len(known)),
            "known_one_cell_actual": int(known["one_cell_can_flip_actual_delta"].fillna(False).sum()),
            "known_five_cell_actual": int(known["five_cells_can_flip_actual_delta"].fillna(False).sum()),
            "live_post_e95_pairs": int(len(live)),
            "live_one_cell_guard": int((live["cells_for_2e6_guard"] == 1).sum()),
        }
    )
    print(
        summary[
            [
                "pair_group",
                "new",
                "base",
                "actual_public_delta",
                "moved_cells",
                "expected_delta_focus_mean",
                "top1_swing",
                "top5_swing",
                "cells_for_actual_abs_delta",
                "cells_for_2e6_guard",
                "cells_for_e95_edge",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
