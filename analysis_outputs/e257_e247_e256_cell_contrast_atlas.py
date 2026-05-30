#!/usr/bin/env python3
"""E257: cell-level atlas for the E247/E256 follow-up question.

E247 is public-positive. E256 is the first controlled post-E247 follow-up:
it keeps the feature-NN1 smoothing idea but constrains the selected rows to the
high-amplitude subset.

This script decomposes the exact cell groups:

- common: selected by both E247 and E256
- e247_only: broad smoothness cells removed by E256
- e256_only: high-amplitude cells added by E256

No public LB is used and no new submission is created.
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

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, load_sub  # noqa: E402
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402
import e162_branch_readability_flip_thresholds as e162  # noqa: E402
import e222_e211_support_tail_audit as e222  # noqa: E402
import e230_e224_support_tail_prune_audit as e230  # noqa: E402
import e237_cell_decisive_jepa_target as e237  # noqa: E402
import e247_feature_nn1_smoothing_materializer as e247  # noqa: E402


ROWS_IN = OUT / "e246_feature_nn1_smoothing_selector_rows.csv"
SUMMARY_IN = OUT / "e246_feature_nn1_smoothing_selector_summary.csv"
GROUP_SUMMARY_OUT = OUT / "e257_e247_e256_cell_contrast_group_summary.csv"
SELECTED_ROWS_OUT = OUT / "e257_e247_e256_cell_contrast_selected_rows.csv"
REPORT_OUT = OUT / "e257_e247_e256_cell_contrast_atlas_report.md"

E247_SELECTOR = "nn_smooth_sum_top34"
E256_SELECTOR = "top50_amp_then_smooth25"
Q3_IDX = TARGETS.index("Q3")
GROUP_ORDER = ["common", "e247_only", "e256_only", "e247_all", "e256_all", "neither"]


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 40, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return e138.md_table(view.head(n), floatfmt)


def parse_rows(value: Any) -> set[int]:
    if pd.isna(value):
        return set()
    return {int(x) for x in str(value).split() if str(x).strip()}


def selector_sets() -> tuple[set[int], set[int]]:
    summary = pd.read_csv(SUMMARY_IN)
    e247_part = summary[summary["candidate_id"].eq(E247_SELECTOR)]
    e256_part = summary[summary["candidate_id"].eq(E256_SELECTOR)]
    if e247_part.empty or e256_part.empty:
        raise RuntimeError("required selector rows are missing")
    return parse_rows(e247_part.iloc[0]["row_idx_list"]), parse_rows(e256_part.iloc[0]["row_idx_list"])


def base_rows(e247_set: set[int], e256_set: set[int]) -> pd.DataFrame:
    rows = pd.read_csv(ROWS_IN).sort_values("row_idx").reset_index(drop=True).copy()
    row_ids = rows["row_idx"].astype(int)
    in247 = row_ids.isin(e247_set)
    in256 = row_ids.isin(e256_set)
    rows["in_e247"] = in247
    rows["in_e256"] = in256
    rows["group"] = "neither"
    rows.loc[in247 & in256, "group"] = "common"
    rows.loc[in247 & ~in256, "group"] = "e247_only"
    rows.loc[~in247 & in256, "group"] = "e256_only"
    return rows


def add_aggregate_groups(frame: pd.DataFrame) -> pd.DataFrame:
    parts = [frame]
    e247_all = frame[frame["in_e247"].astype(bool)].copy()
    e247_all["group"] = "e247_all"
    e256_all = frame[frame["in_e256"].astype(bool)].copy()
    e256_all["group"] = "e256_all"
    parts.extend([e247_all, e256_all])
    return pd.concat(parts, ignore_index=True)


def safe_weighted_mean(x: pd.Series, w: pd.Series) -> float:
    xx = x.to_numpy(dtype=np.float64)
    ww = w.to_numpy(dtype=np.float64)
    den = float(np.sum(ww))
    if den <= 0.0:
        return float("nan")
    return float(np.average(xx, weights=ww))


def hardtail_cells(rows: pd.DataFrame) -> pd.DataFrame:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    priors = e162.prior_arrays(sample)
    e154 = e230.load_prob(e237.E154_FILE, sample)
    e224 = e230.load_prob(e237.E224_FILE, sample)
    spec = e222.Candidate(
        candidate_id="e224_q3_cells",
        file_name=e237.E224_FILE,
        anchor_file=e237.E154_FILE,
        family="e257_e247_e256_contrast",
        status="diagnostic",
        note="Per-cell E224-vs-E154 Q3 anatomy for E247/E256 contrast.",
    )
    cells = e222.cell_table(spec, "graft_vs_e154", e224, e154, e237.E154_FILE, priors, sample)
    q3 = cells[cells["target"].eq("Q3")].copy()
    q3 = q3.merge(rows[["row_idx", "group", "in_e247", "in_e256"]], on="row_idx", how="left")
    q3["group"] = q3["group"].fillna("neither")
    return q3


def roughness_delta(rows: pd.DataFrame, selected: set[int]) -> dict[str, Any]:
    return e247.pair_smoothing_delta(rows, np.array(sorted(selected), dtype=int))


def summarize_group(rows: pd.DataFrame, cells: pd.DataFrame, group: str, row_set: set[int]) -> dict[str, Any]:
    part = rows[rows["group"].eq(group)].copy()
    cell_part = cells[cells["group"].eq(group)].copy()
    if group == "e247_all":
        part = rows[rows["in_e247"].astype(bool)].copy()
        cell_part = cells[cells["in_e247"].astype(bool)].copy()
    elif group == "e256_all":
        part = rows[rows["in_e256"].astype(bool)].copy()
        cell_part = cells[cells["in_e256"].astype(bool)].copy()

    rec: dict[str, Any] = {
        "group": group,
        "n_rows": int(len(part)),
        "rollback_amp_sum": float(part["rollback_amp_abs"].sum()) if not part.empty else 0.0,
        "rollback_amp_mean": float(part["rollback_amp_abs"].mean()) if not part.empty else np.nan,
        "smooth_gain_sum": float(part["single_row_smooth_gain_sum"].sum()) if not part.empty else 0.0,
        "smooth_gain_mean": float(part["single_row_smooth_gain_sum"].mean()) if not part.empty else np.nan,
        "pair_delta_sum": float(part["single_row_pair_delta_sum"].sum()) if not part.empty else 0.0,
        "nn_dist_mean": float(part["nn_dist"].mean()) if not part.empty else np.nan,
        "amp_rank_mean": float(part["amp_rank"].mean()) if not part.empty else np.nan,
        "smooth_rank_mean": float(part["smooth_sum_rank"].mean()) if not part.empty else np.nan,
        "e237_overlap": int(part["e237_drop"].sum()) if "e237_drop" in part else 0,
        "e230_swing_overlap": int(part["e230_swing25"].sum()) if "e230_swing25" in part else 0,
        "e230_risk_overlap": int(part["e230_risk21"].sum()) if "e230_risk21" in part else 0,
        "near_test_edge2_rate": float(part["near_test_edge_2"].mean()) if "near_test_edge_2" in part and not part.empty else np.nan,
        "gap_adjacent2_rate": float(part["gap_adjacent_2"].mean()) if "gap_adjacent_2" in part and not part.empty else np.nan,
    }
    if not part.empty:
        rec.update(roughness_delta(rows, set(part["row_idx"].astype(int))))
    else:
        rec.update(
            {
                "global_pair_abs_delta": np.nan,
                "affected_pair_abs_delta": np.nan,
                "affected_pair_count": 0,
                "positive_pair_delta_share": np.nan,
            }
        )

    if cell_part.empty:
        rec.update(
            {
                "expected_focus_sum": np.nan,
                "adverse_sum": np.nan,
                "support_delta_sum": np.nan,
                "support_prob_focus_weighted": np.nan,
                "swing_sum": np.nan,
                "top1_over_abs_expected": np.nan,
            }
        )
    else:
        expected = float(cell_part["expected_focus"].sum())
        swing = cell_part["swing"].to_numpy(dtype=np.float64)
        rec.update(
            {
                "expected_focus_sum": expected,
                "adverse_sum": float(cell_part["adverse_delta"].sum()),
                "support_delta_sum": float(cell_part["support_delta"].sum()),
                "support_prob_focus_weighted": safe_weighted_mean(cell_part["support_prob_focus"], cell_part["swing"]),
                "swing_sum": float(swing.sum()),
                "top1_over_abs_expected": float(np.max(swing) / max(abs(expected), 1.0e-15)),
            }
        )
    return rec


def group_summary(rows: pd.DataFrame, cells: pd.DataFrame) -> pd.DataFrame:
    out = []
    for group in GROUP_ORDER:
        out.append(summarize_group(rows, cells, group, set()))
    return pd.DataFrame(out)


def selected_rows(rows: pd.DataFrame) -> pd.DataFrame:
    out = rows[rows["group"].isin(["common", "e247_only", "e256_only"])].copy()
    cols = [
        "group",
        "row_idx",
        "subject_id",
        "lifelog_date",
        "nn_row_idx",
        "nn_dist",
        "rollback_amp_abs",
        "single_row_smooth_gain_sum",
        "e237_drop",
        "e230_swing25",
        "e230_risk21",
        "amp_rank",
        "smooth_sum_rank",
        "near_test_edge_2",
        "gap_adjacent_2",
    ]
    return out[[c for c in cols if c in out.columns]].sort_values(["group", "single_row_smooth_gain_sum"], ascending=[True, False])


def main() -> None:
    e247_set, e256_set = selector_sets()
    rows = base_rows(e247_set, e256_set)
    cells = hardtail_cells(rows)
    summary = group_summary(rows, cells)
    selected = selected_rows(rows)
    summary.to_csv(GROUP_SUMMARY_OUT, index=False)
    selected.to_csv(SELECTED_ROWS_OUT, index=False)

    common = summary[summary["group"].eq("common")].iloc[0]
    e247_only = summary[summary["group"].eq("e247_only")].iloc[0]
    e256_only = summary[summary["group"].eq("e256_only")].iloc[0]
    e247_all = summary[summary["group"].eq("e247_all")].iloc[0]
    e256_all = summary[summary["group"].eq("e256_all")].iloc[0]
    lines = [
        "# E257 E247/E256 Cell Contrast Atlas",
        "",
        "## Question",
        "",
        "E247 won public. Does E256 keep the right public signal by replacing broad smoothness cells with high-amplitude smooth cells?",
        "",
        "## Group Summary",
        "",
        md_table(summary, n=10),
        "",
        "## Selected Rows",
        "",
        md_table(selected, n=80),
        "",
        "## Interpretation",
        "",
        f"- E247 has `{int(e247_all['n_rows'])}` Q3 rollback cells; E256 has `{int(e256_all['n_rows'])}`.",
        f"- Common cells: `{int(common['n_rows'])}`; E247-only cells: `{int(e247_only['n_rows'])}`; E256-only cells: `{int(e256_only['n_rows'])}`.",
        f"- E247-only cells carry smoothness mass `{float(e247_only['smooth_gain_sum']):.9f}` but relatively low amplitude mean `{float(e247_only['rollback_amp_mean']):.9f}`.",
        f"- E256-only cells carry smoothness mass `{float(e256_only['smooth_gain_sum']):.9f}` with higher amplitude mean `{float(e256_only['rollback_amp_mean']):.9f}`.",
        f"- E247 all affected-pair roughness delta `{float(e247_all['affected_pair_abs_delta']):.9f}`; E256 all `{float(e256_all['affected_pair_abs_delta']):.9f}`.",
        f"- E247 all expected focus `{float(e247_all['expected_focus_sum']):.9f}`; E256 all `{float(e256_all['expected_focus_sum']):.9f}`.",
        "",
        "## Decision",
        "",
        "- E256 is a clean public sensor because it changes the cell composition without leaving the E247 mechanism family.",
        "- If E256 beats E247, prefer high-amplitude smooth cells and shrink broad smoothness.",
        "- If E256 is worse but close, E247-only broad smoothness cells are public-useful despite lower amplitude.",
        "- If E256 fails hard, public may depend on E247's exact top34 nonlocal set or E224-body interaction.",
        "- No public LB is used and no submission is created.",
        "",
    ]
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")
    print("[E257 group summary]")
    print(summary.round(9).to_string(index=False))
    print(f"\nwrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
