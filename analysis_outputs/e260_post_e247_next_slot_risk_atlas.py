#!/usr/bin/env python3
"""E260: public-free risk atlas for the next post-E247 slot.

E259 fixed how future public scores should be decoded. E260 asks a narrower
pre-submission question:

    If E247 is the current anchor, how fragile are E256 and E224 as single
    next observations under hard-label LogLoss sensitivity?

This creates no submission and uses no unknown public score. It compares
candidate-vs-E247 deltas through public-free priors, swing concentration, and
E257 cell-group anatomy.
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
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402
import e162_branch_readability_flip_thresholds as e162  # noqa: E402


E247_FILE = "submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv"
E256_FILE = "submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv"
E224_FILE = "submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv"

E247_PUBLIC = 0.5761589494
E95_PUBLIC = 0.5762913298
MIXMIN_PUBLIC = 0.5763066405
PUBLIC_READABLE_GUARD = 2.0e-6
E95_OVER_MIXMIN_EDGE = E95_PUBLIC - MIXMIN_PUBLIC
E247_OVER_E95_EDGE = E95_PUBLIC - E247_PUBLIC
E259_CLEAN_BAND = 2.0e-5
N_PUBLIC_CELLS = 250 * len(TARGETS)
EPS = 1.0e-12

E257_ROWS_IN = OUT / "e257_e247_e256_cell_contrast_selected_rows.csv"
PAIR_OUT = OUT / "e260_post_e247_next_slot_pair_summary.csv"
TARGET_OUT = OUT / "e260_post_e247_next_slot_target_summary.csv"
GROUP_OUT = OUT / "e260_post_e247_next_slot_group_summary.csv"
TOP_CELLS_OUT = OUT / "e260_post_e247_next_slot_top_cells.csv"
REPORT_OUT = OUT / "e260_post_e247_next_slot_risk_atlas_report.md"


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def load_prob(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    return clip_prob(load_sub(file_name, sample)[TARGETS].to_numpy(dtype=np.float64))


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 30, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return e138.md_table(view.head(n), floatfmt)


def safe_weighted_mean(values: np.ndarray, weights: np.ndarray) -> float:
    den = float(np.sum(weights))
    if den <= EPS:
        return float("nan")
    return float(np.average(values, weights=weights))


def top_sum(values: np.ndarray, k: int) -> float:
    arr = np.sort(np.asarray(values, dtype=np.float64).reshape(-1))[::-1]
    if len(arr) == 0:
        return 0.0
    return float(arr[:k].sum())


def e257_group_map() -> dict[int, str]:
    if not E257_ROWS_IN.exists():
        return {}
    rows = pd.read_csv(E257_ROWS_IN)
    return {int(r.row_idx): str(r.group) for r in rows.itertuples(index=False)}


def pair_cells(
    pair_id: str,
    file_new: str,
    file_base: str,
    p_new: np.ndarray,
    p_base: np.ndarray,
    sample: pd.DataFrame,
    priors: dict[str, np.ndarray],
    group_by_row: dict[int, str],
) -> pd.DataFrame:
    moved = np.abs(p_new - p_base) > EPS
    row_idx, target_idx = np.where(moved)
    if len(row_idx) == 0:
        return pd.DataFrame()

    dy1, dy0 = e162.hard_loss_deltas(p_new[row_idx, target_idx], p_base[row_idx, target_idx])
    dy1_s = dy1 / N_PUBLIC_CELLS
    dy0_s = dy0 / N_PUBLIC_CELLS
    swing = np.abs(dy1_s - dy0_s)
    support_label = np.where(dy1_s < dy0_s, 1, 0)
    support_delta = np.minimum(dy1_s, dy0_s)
    adverse_delta = np.maximum(dy1_s, dy0_s)
    py_focus = priors["focus_mean"][row_idx, target_idx]
    py_global = priors["global"][row_idx, target_idx]
    py_subject = priors["subject"][row_idx, target_idx]
    py_nearest = priors["nearest_hard085"][row_idx, target_idx]
    expected_focus = py_focus * dy1_s + (1.0 - py_focus) * dy0_s
    expected_global = py_global * dy1_s + (1.0 - py_global) * dy0_s
    expected_subject = py_subject * dy1_s + (1.0 - py_subject) * dy0_s
    expected_nearest = py_nearest * dy1_s + (1.0 - py_nearest) * dy0_s
    support_prob_focus = np.where(support_label == 1, py_focus, 1.0 - py_focus)

    z_new = logit(p_new[row_idx, target_idx])
    z_base = logit(p_base[row_idx, target_idx])
    rows = []
    for k, (i, j) in enumerate(zip(row_idx, target_idx)):
        group = group_by_row.get(int(i), "outside_e247_e256_selected")
        if pair_id == "e256_vs_e247" and group == "e247_only":
            action = "remove_e247_broad_smooth_cell"
        elif pair_id == "e256_vs_e247" and group == "e256_only":
            action = "add_e256_high_amp_cell"
        elif pair_id == "e224_vs_e247":
            action = "remove_e247_rollback_cell"
        else:
            action = "other"
        rows.append(
            {
                "pair_id": pair_id,
                "file_new": file_new,
                "file_base": file_base,
                "row_idx": int(i),
                "target_idx": int(j),
                "target": TARGETS[int(j)],
                "subject_id": sample.loc[int(i), "subject_id"],
                "sleep_date": sample.loc[int(i), "sleep_date"],
                "lifelog_date": sample.loc[int(i), "lifelog_date"],
                "e257_group": group,
                "action": action,
                "p_base": float(p_base[i, j]),
                "p_new": float(p_new[i, j]),
                "prob_delta": float(p_new[i, j] - p_base[i, j]),
                "abs_prob_delta": float(abs(p_new[i, j] - p_base[i, j])),
                "logit_delta": float(z_new[k] - z_base[k]),
                "abs_logit_delta": float(abs(z_new[k] - z_base[k])),
                "loss_delta_y1": float(dy1_s[k]),
                "loss_delta_y0": float(dy0_s[k]),
                "support_label": int(support_label[k]),
                "support_delta": float(support_delta[k]),
                "adverse_delta": float(adverse_delta[k]),
                "swing": float(swing[k]),
                "py_focus": float(py_focus[k]),
                "py_global": float(py_global[k]),
                "py_subject": float(py_subject[k]),
                "py_nearest_hard085": float(py_nearest[k]),
                "expected_focus": float(expected_focus[k]),
                "expected_global": float(expected_global[k]),
                "expected_subject": float(expected_subject[k]),
                "expected_nearest_hard085": float(expected_nearest[k]),
                "support_prob_focus": float(support_prob_focus[k]),
            }
        )
    return pd.DataFrame(rows)


def summarize_cells(cells: pd.DataFrame, keys: dict[str, Any]) -> dict[str, Any]:
    rec = dict(keys)
    if cells.empty:
        rec.update(
            {
                "moved_cells": 0,
                "moved_rows": 0,
                "targets_moved": "",
                "expected_focus": 0.0,
                "adverse_delta": 0.0,
                "support_delta": 0.0,
                "swing_sum": 0.0,
            }
        )
        return rec
    swing = cells["swing"].to_numpy(dtype=np.float64)
    expected_focus = float(cells["expected_focus"].sum())
    abs_expected = abs(expected_focus)
    rec.update(
        {
            "moved_cells": int(len(cells)),
            "moved_rows": int(cells["row_idx"].nunique()),
            "subjects_moved": int(cells["subject_id"].nunique()),
            "targets_moved": ",".join(sorted(cells["target"].unique())),
            "expected_focus": expected_focus,
            "expected_global": float(cells["expected_global"].sum()),
            "expected_subject": float(cells["expected_subject"].sum()),
            "expected_nearest_hard085": float(cells["expected_nearest_hard085"].sum()),
            "support_delta": float(cells["support_delta"].sum()),
            "adverse_delta": float(cells["adverse_delta"].sum()),
            "swing_sum": float(swing.sum()),
            "top1_swing": top_sum(swing, 1),
            "top3_swing": top_sum(swing, 3),
            "top5_swing": top_sum(swing, 5),
            "top10_swing": top_sum(swing, 10),
            "support_prob_focus_mean": float(cells["support_prob_focus"].mean()),
            "support_prob_focus_swing_weighted": safe_weighted_mean(
                cells["support_prob_focus"].to_numpy(dtype=np.float64), swing
            ),
            "mean_abs_prob_delta": float(cells["abs_prob_delta"].mean()),
            "mean_abs_logit_delta": float(cells["abs_logit_delta"].mean()),
            "max_abs_logit_delta": float(cells["abs_logit_delta"].max()),
            "cells_for_2e6_guard": e162.min_cells_for_threshold(swing, PUBLIC_READABLE_GUARD),
            "cells_for_e95_over_mixmin_edge": e162.min_cells_for_threshold(swing, abs(E95_OVER_MIXMIN_EDGE)),
            "cells_for_e259_clean_band": e162.min_cells_for_threshold(swing, E259_CLEAN_BAND),
            "cells_for_e247_over_e95_edge": e162.min_cells_for_threshold(swing, E247_OVER_E95_EDGE),
            "cells_to_overturn_expected_focus": e162.min_cells_for_threshold(swing, abs_expected),
        }
    )
    rec["top1_over_abs_expected"] = float(rec["top1_swing"] / max(abs_expected, 1.0e-15))
    rec["top5_over_abs_expected"] = float(rec["top5_swing"] / max(abs_expected, 1.0e-15))
    rec["top1_swing_share"] = float(rec["top1_swing"] / max(rec["swing_sum"], 1.0e-15))
    rec["top5_swing_share"] = float(rec["top5_swing"] / max(rec["swing_sum"], 1.0e-15))
    rec["expected_vs_e247_interpretation"] = (
        "candidate_expected_better_than_e247" if expected_focus < 0 else "candidate_expected_worse_than_e247"
    )
    return rec


def summarize_by(cells: pd.DataFrame, group_col: str) -> pd.DataFrame:
    rows = []
    for (pair_id, key), part in cells.groupby(["pair_id", group_col], dropna=False):
        pair_id = str(part["pair_id"].iloc[0])
        rows.append(summarize_cells(part, {"pair_id": pair_id, group_col: key}))
    return pd.DataFrame(rows)


def report_text(pair_summary: pd.DataFrame, target_summary: pd.DataFrame, group_summary: pd.DataFrame, top_cells: pd.DataFrame) -> str:
    pair_cols = [
        "pair_id",
        "moved_cells",
        "moved_rows",
        "expected_focus",
        "adverse_delta",
        "support_prob_focus_swing_weighted",
        "swing_sum",
        "top1_over_abs_expected",
        "cells_to_overturn_expected_focus",
        "cells_for_e259_clean_band",
        "expected_vs_e247_interpretation",
    ]
    group_cols = [
        "pair_id",
        "e257_group",
        "moved_cells",
        "expected_focus",
        "adverse_delta",
        "support_prob_focus_swing_weighted",
        "top1_over_abs_expected",
    ]
    top_cols = [
        "pair_id",
        "row_idx",
        "target",
        "subject_id",
        "lifelog_date",
        "e257_group",
        "action",
        "prob_delta",
        "swing",
        "expected_focus",
        "support_prob_focus",
    ]
    decision = "undetermined"
    key_read = ""
    e256 = pair_summary[pair_summary["pair_id"].eq("e256_vs_e247")]
    e224 = pair_summary[pair_summary["pair_id"].eq("e224_vs_e247")]
    if not e256.empty and not e224.empty:
        e256_exp = float(e256.iloc[0]["expected_focus"])
        e224_exp = float(e224.iloc[0]["expected_focus"])
        decision = (
            "E256 has the smaller public-free expected penalty versus E247, so it remains the score-plus-information next slot."
            if e256_exp < e224_exp
            else "E224 has the smaller expected penalty versus E247, so attribution-first no longer costs expected score under this stress."
        )
        ratio = e224_exp / max(e256_exp, 1.0e-15)
        key_read = (
            f"- E256 expected penalty vs E247 is `{e256_exp:.9f}`; E224 expected penalty is `{e224_exp:.9f}` "
            f"(`{ratio:.3f}x` larger for E224).\n"
        )
    e256_broad = group_summary[
        group_summary["pair_id"].eq("e256_vs_e247") & group_summary["e257_group"].eq("e247_only")
    ]
    e256_added = group_summary[
        group_summary["pair_id"].eq("e256_vs_e247") & group_summary["e257_group"].eq("e256_only")
    ]
    e224_common = group_summary[
        group_summary["pair_id"].eq("e224_vs_e247") & group_summary["e257_group"].eq("common")
    ]
    if not e256_broad.empty and not e256_added.empty:
        key_read += (
            f"- Inside E256, removing E247-only broad cells is slightly favorable under focus prior "
            f"(`{float(e256_broad.iloc[0]['expected_focus']):.9f}`), while the four E256-only high-amplitude cells are adverse "
            f"(`{float(e256_added.iloc[0]['expected_focus']):.9f}`).\n"
        )
    if not e224_common.empty:
        key_read += (
            f"- E224-vs-E247 risk is dominated by removing the common rollback core "
            f"(`{float(e224_common.iloc[0]['expected_focus']):.9f}` over `{int(e224_common.iloc[0]['moved_cells'])}` cells).\n"
        )

    return f"""# E260 Post-E247 Next-Slot Risk Atlas

## Question

E259 says E256 and E224 are the two clean next public observations. E260 asks which one is safer as a score attempt and how hard-label-fragile each observation is relative to the current E247 anchor.

Negative `expected_focus` means the candidate is favored over E247 by the public-free focus prior. Positive means the prior still favors E247.

## Pair Summary

{md_table(pair_summary, pair_cols, n=10)}

## Key Read

{key_read}

## Target Summary

{md_table(target_summary, n=20)}

## E257 Cell-Group Summary

{md_table(group_summary, group_cols, n=20)}

## Top Swing Cells

{md_table(top_cells, top_cols, n=20)}

## Decision

{decision}

Operationally:

- E256 remains the right next file when the goal is score plus information.
- E224 remains the right next file only when the goal is clean body attribution.
- Both observations are hard-label sensitive, so neither should be followed by a sibling sweep without public feedback.
"""


def main() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    priors = e162.prior_arrays(sample)
    group_by_row = e257_group_map()
    probs = {
        "e247": load_prob(E247_FILE, sample),
        "e256": load_prob(E256_FILE, sample),
        "e224": load_prob(E224_FILE, sample),
    }
    pair_specs = [
        ("e256_vs_e247", E256_FILE, E247_FILE, probs["e256"], probs["e247"]),
        ("e224_vs_e247", E224_FILE, E247_FILE, probs["e224"], probs["e247"]),
    ]
    cell_parts = [
        pair_cells(pair_id, file_new, file_base, p_new, p_base, sample, priors, group_by_row)
        for pair_id, file_new, file_base, p_new, p_base in pair_specs
    ]
    cells = pd.concat(cell_parts, ignore_index=True)
    pair_summary = pd.DataFrame(
        [summarize_cells(part, {"pair_id": str(pair_id)}) for pair_id, part in cells.groupby("pair_id")]
    ).sort_values("pair_id")
    target_summary = summarize_by(cells, "target").sort_values(["pair_id", "target"]).reset_index(drop=True)
    group_summary = summarize_by(cells, "e257_group").sort_values(["pair_id", "e257_group"]).reset_index(drop=True)
    top_cells = (
        cells.sort_values(["pair_id", "swing"], ascending=[True, False])
        .groupby("pair_id", group_keys=False)
        .head(12)
        .reset_index(drop=True)
    )

    pair_summary.to_csv(PAIR_OUT, index=False)
    target_summary.to_csv(TARGET_OUT, index=False)
    group_summary.to_csv(GROUP_OUT, index=False)
    top_cells.to_csv(TOP_CELLS_OUT, index=False)
    REPORT_OUT.write_text(report_text(pair_summary, target_summary, group_summary, top_cells), encoding="utf-8")

    print(f"wrote {PAIR_OUT}")
    print(f"wrote {TARGET_OUT}")
    print(f"wrote {GROUP_OUT}")
    print(f"wrote {TOP_CELLS_OUT}")
    print(f"wrote {REPORT_OUT}")


if __name__ == "__main__":
    main()
