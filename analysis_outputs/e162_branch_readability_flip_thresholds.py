#!/usr/bin/env python3
"""E162: branch readability as hidden-label flip thresholds.

E158/E161 say repaired-branch controls are too close to rank as independent
pre-feedback submissions. This audit translates that into the actual object
LogLoss sees: row-target hard labels.

For each pair of branch candidates, measure:

- how many row-target cells differ;
- expected deltas under public-free priors from E159;
- how concentrated the pairwise hard-label swing is;
- how many top swing cells are enough to move the score by the public-readable
  guardrail (`2e-6`) or by the E95-over-mixmin frontier edge.

If only a few cells can move the public score by the full sibling gap, ordinary
CV/model/blend ranking cannot be trusted at this branch scale.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, load_sub  # noqa: E402
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402
import e161_e154_inherited_body_pruning_audit as e161  # noqa: E402


SEGMENTS_IN = OUT / "e159_e154_public_outcome_attribution_cells.csv"
E161_SCAN_IN = OUT / "e161_e154_inherited_body_pruning_scan.csv"
PAIRWISE_OUT = OUT / "e162_branch_readability_pairwise.csv"
TOP_CELLS_OUT = OUT / "e162_branch_readability_top_cells.csv"
REPORT_OUT = OUT / "e162_branch_readability_report.md"

N_PUBLIC_CELLS = 250 * len(TARGETS)
PUBLIC_READABLE_GUARD = 2.0e-6
E95_EDGE_OVER_MIXMIN = 0.0000153107
EPS = 1.0e-12


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def hard_loss_deltas(p_new: np.ndarray, p_base: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    p_new = clip_prob(p_new)
    p_base = clip_prob(p_base)
    delta_y1 = -np.log(p_new) + np.log(p_base)
    delta_y0 = -np.log(1.0 - p_new) + np.log(1.0 - p_base)
    return delta_y1, delta_y0


def load_aligned(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    return clip_prob(load_sub(file_name, sample)[TARGETS].to_numpy(dtype=np.float64))


def min_cells_for_threshold(swings: np.ndarray, threshold: float) -> int:
    if threshold <= 0:
        return 0
    arr = np.sort(np.asarray(swings, dtype=np.float64).reshape(-1))[::-1]
    arr = arr[arr > 0]
    if len(arr) == 0:
        return -1
    csum = np.cumsum(arr)
    idx = int(np.searchsorted(csum, threshold, side="left"))
    if idx >= len(arr):
        return -1
    return idx + 1


def train_global_priors() -> dict[str, float]:
    train_path = DATA / "ch2026_metrics_train.csv"
    if not train_path.exists():
        return {target: 0.5 for target in TARGETS}
    train = pd.read_csv(train_path)
    out: dict[str, float] = {}
    for target in TARGETS:
        if target in train:
            out[target] = float(train[target].mean())
        else:
            out[target] = 0.5
    return out


def prior_arrays(sample: pd.DataFrame) -> dict[str, np.ndarray]:
    segments = pd.read_csv(SEGMENTS_IN, low_memory=False)
    defaults = train_global_priors()
    arrays = {
        name: np.zeros((len(sample), len(TARGETS)), dtype=np.float64)
        for name in ["global", "subject", "nearest_hard085"]
    }
    for idx, target in enumerate(TARGETS):
        for arr in arrays.values():
            arr[:, idx] = defaults[target]

    unique = (
        segments.sort_values("unique_cell_idx")
        .drop_duplicates(["sub_idx", "target_idx"], keep="first")
        .copy()
    )
    for row in unique.itertuples(index=False):
        i = int(row.sub_idx)
        j = int(row.target_idx)
        arrays["global"][i, j] = float(getattr(row, "p_y1_global"))
        arrays["subject"][i, j] = float(getattr(row, "p_y1_subject"))
        arrays["nearest_hard085"][i, j] = float(getattr(row, "p_y1_nearest_hard085"))
    arrays["focus_mean"] = np.mean(
        np.stack([arrays["global"], arrays["subject"], arrays["nearest_hard085"]], axis=0),
        axis=0,
    )
    return arrays


def reconstruct_e161_preds(sample: pd.DataFrame, refs: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    scan = pd.read_csv(E161_SCAN_IN, low_memory=False)
    variants = scan[scan["strategy"].eq("risk_prune")].copy()
    chosen: dict[str, str] = {}
    control_grade = variants[variants["e161_control_grade"].fillna(False).astype(bool)].copy()
    if not control_grade.empty:
        chosen["e161_best_control_grade"] = str(
            control_grade.sort_values(["local_delta_vs_e154", "focus_expected_delta_vs_e154"], ascending=[True, True])
            .iloc[0]["tag"]
        )
    chosen["e161_best_local_any"] = str(
        variants.sort_values(["local_delta_vs_e154", "focus_expected_delta_vs_e154"], ascending=[True, True]).iloc[0]["tag"]
    )
    chosen["e161_best_risk_any"] = str(
        variants.sort_values(["focus_expected_delta_vs_e154", "local_delta_vs_e154"], ascending=[True, True]).iloc[0]["tag"]
    )

    segments = pd.read_csv(e161.SEGMENTS_IN, low_memory=False)
    cells = e161.build_cell_table(segments, len(sample))
    rows, preds = e161.build_candidates(sample, refs, cells)
    tag_to_pred: dict[str, np.ndarray] = {}
    for row in rows.itertuples(index=False):
        tag = str(row.tag)
        if tag in chosen.values() and tag not in tag_to_pred:
            tag_to_pred[tag] = preds[int(row.pred_index)]
    missing = [tag for tag in chosen.values() if tag not in tag_to_pred]
    if missing:
        raise RuntimeError(f"Could not reconstruct E161 tags: {missing}")
    return {name: tag_to_pred[tag] for name, tag in chosen.items()}


def pair_metrics(
    name_new: str,
    name_base: str,
    p_new: np.ndarray,
    p_base: np.ndarray,
    priors: dict[str, np.ndarray],
) -> tuple[dict[str, Any], pd.DataFrame]:
    moved = np.abs(p_new - p_base) > EPS
    row_idx, target_idx = np.where(moved)
    if len(row_idx) == 0:
        return {
            "new": name_new,
            "base": name_base,
            "moved_cells": 0,
        }, pd.DataFrame()

    dy1, dy0 = hard_loss_deltas(p_new[row_idx, target_idx], p_base[row_idx, target_idx])
    dy1_s = dy1 / N_PUBLIC_CELLS
    dy0_s = dy0 / N_PUBLIC_CELLS
    swing = np.abs(dy1_s - dy0_s)
    support_label = np.where(dy1_s < dy0_s, 1, 0)
    support_delta = np.minimum(dy1_s, dy0_s)
    adverse_delta = np.maximum(dy1_s, dy0_s)
    total_swing = float(swing.sum())
    top_sorted = np.sort(swing)[::-1]
    records: dict[str, Any] = {
        "new": name_new,
        "base": name_base,
        "moved_cells": int(len(row_idx)),
        "moved_rows": int(len(np.unique(row_idx))),
        "targets_moved": ",".join(TARGETS[j] for j in sorted(set(target_idx))),
        "all_support_delta": float(support_delta.sum()),
        "all_adverse_delta": float(adverse_delta.sum()),
        "total_swing": total_swing,
        "top1_swing": float(top_sorted[0]) if len(top_sorted) else 0.0,
        "top3_swing": float(top_sorted[:3].sum()) if len(top_sorted) else 0.0,
        "top5_swing": float(top_sorted[:5].sum()) if len(top_sorted) else 0.0,
        "top10_swing": float(top_sorted[:10].sum()) if len(top_sorted) else 0.0,
        "top1_swing_share": float(top_sorted[0] / total_swing) if total_swing > 0 and len(top_sorted) else 0.0,
        "top5_swing_share": float(top_sorted[:5].sum() / total_swing) if total_swing > 0 else 0.0,
        "cells_for_2e6_guard": min_cells_for_threshold(swing, PUBLIC_READABLE_GUARD),
        "cells_for_e95_edge": min_cells_for_threshold(swing, E95_EDGE_OVER_MIXMIN),
    }

    for prior_name, arr in priors.items():
        py = arr[row_idx, target_idx]
        expected = py * dy1_s + (1.0 - py) * dy0_s
        hard = np.where(py >= 0.5, dy1_s, dy0_s)
        support_prob = np.where(support_label == 1, py, 1.0 - py)
        records[f"expected_delta_{prior_name}"] = float(expected.sum())
        records[f"hard_delta_{prior_name}"] = float(hard.sum())
        records[f"support_prob_mean_{prior_name}"] = float(support_prob.mean())
        records[f"support_prob_swing_weighted_{prior_name}"] = (
            float(np.average(support_prob, weights=swing)) if total_swing > 0 else np.nan
        )
        records[f"cells_to_flip_expected_{prior_name}"] = min_cells_for_threshold(
            swing,
            abs(float(expected.sum())),
        )

    top = pd.DataFrame(
        {
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
    return records, top.head(25)


def md_table(frame: pd.DataFrame, cols: list[str], n: int = 40, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    keep = [c for c in cols if c in frame.columns]
    return e138.md_table(frame[keep].head(n), floatfmt)


def write_report(pairwise: pd.DataFrame, top_cells: pd.DataFrame) -> None:
    focus = pairwise.sort_values(["cells_for_2e6_guard", "moved_cells"], ascending=[True, True]).copy()
    branch = pairwise[pairwise["new"].isin(["e154", "e155", "e157", "e156"]) | pairwise["base"].isin(["e154", "e155", "e157", "e156"])].copy()
    lines = [
        "# E162 Branch Readability Flip Thresholds",
        "",
        "## Question",
        "",
        "When branch candidates differ by frontier-scale micro edges, how many hidden row-target labels are enough to move the public score by a readable amount?",
        "",
        "## Summary",
        "",
        md_table(
            focus,
            [
                "new",
                "base",
                "moved_cells",
                "moved_rows",
                "expected_delta_focus_mean",
                "hard_delta_focus_mean",
                "support_prob_swing_weighted_focus_mean",
                "total_swing",
                "top1_swing",
                "top5_swing_share",
                "cells_for_2e6_guard",
                "cells_for_e95_edge",
                "cells_to_flip_expected_focus_mean",
                "targets_moved",
            ],
            80,
        ),
        "",
        "## Sibling Branch Pairs",
        "",
        md_table(
            branch,
            [
                "new",
                "base",
                "moved_cells",
                "expected_delta_focus_mean",
                "support_prob_swing_weighted_focus_mean",
                "top1_swing",
                "top5_swing",
                "cells_for_2e6_guard",
                "cells_to_flip_expected_focus_mean",
                "targets_moved",
            ],
            80,
        ),
        "",
        "## Top Swing Cells",
        "",
        md_table(
            top_cells.sort_values(["new", "base", "swing_rank"]),
            [
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
        "E154 remains the first public sensor. Sibling controls and E161 pruning rows are too cell-fragile to rank before feedback; their differences can be moved by a small number of high-swing hidden labels rather than by a broad stable world law.",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    preds: dict[str, np.ndarray] = {
        "e95": load_aligned("submission_e95_hardtail_541e3973.csv", sample),
        "e144": load_aligned("submission_e144_activeboundary_d7b4b331.csv", sample),
        "e154": load_aligned("submission_e154_s3repair_9f2e2e73.csv", sample),
        "e155": load_aligned("submission_e155_bodytemp_d27e7965.csv", sample),
        "e157": load_aligned("submission_e157_lowbodypareto_bd67930d.csv", sample),
        "e156": load_aligned("submission_e156_targetaxis_757546d2.csv", sample),
    }
    refs = {
        **preds,
        "mixmin": load_aligned("submission_mixmin_0c916bb4.csv", sample),
        "failed_e72": load_aligned("submission_e72_topabs50_q2s3_gate_4e48cba2.csv", sample),
        "e101": load_aligned("submission_e101_q2s3tail_177569bc.csv", sample),
    }
    preds.update(reconstruct_e161_preds(sample, refs))
    priors = prior_arrays(sample)

    pairs = [
        ("e154", "e95"),
        ("e154", "e144"),
        ("e154", "e155"),
        ("e154", "e157"),
        ("e154", "e156"),
        ("e155", "e144"),
        ("e157", "e155"),
        ("e156", "e155"),
        ("e161_best_control_grade", "e154"),
        ("e161_best_local_any", "e154"),
        ("e161_best_risk_any", "e154"),
        ("e161_best_control_grade", "e155"),
        ("e161_best_control_grade", "e144"),
    ]
    rows: list[dict[str, Any]] = []
    top_frames: list[pd.DataFrame] = []
    for new, base in pairs:
        rec, top = pair_metrics(new, base, preds[new], preds[base], priors)
        rows.append(rec)
        if not top.empty:
            top_frames.append(top)
    pairwise = pd.DataFrame(rows)
    top_cells = pd.concat(top_frames, ignore_index=True) if top_frames else pd.DataFrame()
    pairwise.to_csv(PAIRWISE_OUT, index=False)
    top_cells.to_csv(TOP_CELLS_OUT, index=False)
    write_report(pairwise, top_cells)

    print(
        {
            "pairs": int(len(pairwise)),
            "min_cells_for_2e6": int(pairwise["cells_for_2e6_guard"].replace(-1, np.nan).min()),
            "max_top5_swing_share": float(pairwise["top5_swing_share"].max()),
            "e154_e155_cells_for_2e6": int(
                pairwise.loc[(pairwise["new"] == "e154") & (pairwise["base"] == "e155"), "cells_for_2e6_guard"].iloc[0]
            ),
            "e154_e144_cells_for_2e6": int(
                pairwise.loc[(pairwise["new"] == "e154") & (pairwise["base"] == "e144"), "cells_for_2e6_guard"].iloc[0]
            ),
        }
    )
    print(
        pairwise[
            [
                "new",
                "base",
                "moved_cells",
                "expected_delta_focus_mean",
                "top1_swing",
                "top5_swing_share",
                "cells_for_2e6_guard",
                "cells_to_flip_expected_focus_mean",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
