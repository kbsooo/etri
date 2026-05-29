#!/usr/bin/env python3
"""E168: can E166's hidden-context signal be separated from safety divergence?

E167 showed an uncomfortable split: E166 is enriched for hidden calendar/block
context, but its focus cells are adverse under the current safety atlas. This
audit asks whether a simple local mask can keep the E166 context signal while
repairing safety metrics, without creating a new submission.
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

import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402


CELLS_IN = OUT / "e167_broad_survivor_context_alignment_cells.csv"

SUMMARY_OUT = OUT / "e168_e166_safety_context_decoupling_summary.csv"
QUADRANTS_OUT = OUT / "e168_e166_safety_context_decoupling_quadrants.csv"
FRONTIER_OUT = OUT / "e168_e166_safety_context_decoupling_frontier.csv"
REPORT_OUT = OUT / "e168_e166_safety_context_decoupling_report.md"

EPS = 1.0e-12


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 40, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return e138.md_table(view.head(n), floatfmt)


def bool_series(frame: pd.DataFrame, col: str) -> pd.Series:
    return frame[col].fillna(False).astype(bool)


def cells_to_flip_expected(frame: pd.DataFrame) -> int | float:
    expected = abs(float(frame["expected_delta_focus_mean"].sum()))
    if expected <= EPS or frame.empty:
        return np.nan
    swings = np.sort(frame["swing"].to_numpy(dtype=np.float64))[::-1]
    if len(swings) == 0:
        return np.nan
    csum = np.cumsum(swings)
    hit = np.where(csum + EPS >= expected)[0]
    return int(hit[0] + 1) if len(hit) else int(len(swings))


def summarize(name: str, frame: pd.DataFrame, all_ref: pd.DataFrame, focus_ref: pd.DataFrame) -> dict[str, Any]:
    if frame.empty:
        return {
            "policy": name,
            "n_cells": 0,
            "expected_delta": 0.0,
        }
    expected = float(frame["expected_delta_focus_mean"].sum())
    benefit = float(frame["benefit_contrib"].sum())
    risk = float(frame["risk_contrib"].sum())
    ref_expected = abs(float(all_ref["expected_delta_focus_mean"].sum()))
    ref_focus_benefit = float(focus_ref["benefit_contrib"].sum())
    top1 = float(frame["swing"].max())
    focus_kept = focus_ref["cell_idx"].isin(frame["cell_idx"])
    focus_kept_frame = focus_ref[focus_kept]
    out: dict[str, Any] = {
        "policy": name,
        "n_cells": int(len(frame)),
        "n_rows": int(frame["sub_idx"].nunique()),
        "n_subjects": int(frame["subject_id"].nunique()),
        "n_blocks": int(frame["hidden_block_id"].nunique()),
        "expected_delta": expected,
        "benefit_sum": benefit,
        "risk_sum": risk,
        "expected_abs_share_vs_all": abs(expected) / ref_expected if ref_expected > EPS else np.nan,
        "benefit_share_vs_all_focus": benefit / ref_focus_benefit if ref_focus_benefit > EPS else np.nan,
        "top_benefit_focus_cells_kept": int(focus_kept.sum()),
        "top_benefit_focus_share_kept": float(focus_kept.mean()),
        "top_benefit_focus_expected_kept": float(focus_kept_frame["expected_delta_focus_mean"].sum())
        if len(focus_kept_frame)
        else 0.0,
        "cells_to_flip_expected": cells_to_flip_expected(frame),
        "top1_expected_ratio": top1 / abs(expected) if abs(expected) > EPS else np.nan,
        "q_share": float(frame["target"].isin(["Q1", "Q2", "Q3"]).mean()),
        "s_share": float(frame["target"].isin(["S1", "S2", "S3", "S4"]).mean()),
        "q2s3_share": float(frame["target"].isin(["Q2", "S3"]).mean()),
        "edge_like_rate": float(bool_series(frame, "edge_like").mean()),
        "between_train_runs_rate": float(frame["context_type"].eq("between_train_runs").mean()),
        "all_veto_null_rate": float(bool_series(frame, "all_veto_null").mean()),
        "all_low_adverse75_rate": float(bool_series(frame, "all_low_adverse75").mean()),
        "all_safe_density_mean": float(frame["all_safe_density"].mean()),
        "broad_low_alpha_mass_sum": float(frame["broad_low_alpha_mass"].sum()),
        "e101_plausible_mass_sum": float(frame["e101_plausible_mass"].sum()),
        "e72_active_rate": float(bool_series(frame, "e72_active").mean()),
    }
    return out


def make_policy_masks(cells: pd.DataFrame) -> dict[str, pd.Series]:
    edge = bool_series(cells, "edge_like")
    between = cells["context_type"].eq("between_train_runs")
    context = edge | between
    veto = bool_series(cells, "all_veto_null")
    low_adv = bool_series(cells, "all_low_adverse75")
    not_e72 = ~bool_series(cells, "e72_active")
    high_safe50 = cells["all_safe_density"].ge(cells["all_safe_density"].median())
    high_safe75 = cells["all_safe_density"].ge(cells["all_safe_density"].quantile(0.75))
    transfer_pos = cells["broad_low_alpha_mass"].gt(0) | cells["e101_plausible_mass"].gt(0)
    no_q2s3 = ~cells["target"].isin(["Q2", "S3"])
    s_targets = cells["target"].isin(["S1", "S2", "S3", "S4"])
    return {
        "all_e166": pd.Series(True, index=cells.index),
        "context_edge_or_between": context,
        "context_edge_and_between": edge & between,
        "context_between_only": between,
        "context_edge_only": edge,
        "safety_veto_null": veto,
        "safety_high_density_p50": high_safe50,
        "safety_high_density_p75": high_safe75,
        "safety_not_e72_active": not_e72,
        "safety_veto_not_e72": veto & not_e72,
        "transfer_plausible_pos": transfer_pos,
        "target_no_q2s3": no_q2s3,
        "target_s_only": s_targets,
        "context_high__veto": context & veto,
        "context_high__high_density_p50": context & high_safe50,
        "context_high__high_density_p75": context & high_safe75,
        "context_high__not_e72": context & not_e72,
        "context_high__veto_not_e72": context & veto & not_e72,
        "context_high__transfer_pos": context & transfer_pos,
        "context_strict__veto": edge & between & veto,
        "context_strict__high_density_p75": edge & between & high_safe75,
        "context_strict__not_e72": edge & between & not_e72,
        "context_strict__veto_not_e72": edge & between & veto & not_e72,
        "context_high__veto__no_q2s3": context & veto & no_q2s3,
        "context_high__veto__s_only": context & veto & s_targets,
    }


def quadrant_rows(cells: pd.DataFrame, focus: pd.DataFrame) -> pd.DataFrame:
    frames = []
    definitions = {
        "context_by_veto_safe": (
            bool_series(cells, "edge_like") | cells["context_type"].eq("between_train_runs"),
            bool_series(cells, "all_veto_null") & cells["all_safe_density"].ge(cells["all_safe_density"].median()),
            "context_high",
            "veto_density_safe",
        ),
        "context_by_transfer_pos": (
            bool_series(cells, "edge_like") | cells["context_type"].eq("between_train_runs"),
            cells["broad_low_alpha_mass"].gt(0) | cells["e101_plausible_mass"].gt(0),
            "context_high",
            "transfer_plausible",
        ),
        "context_by_e72_active": (
            bool_series(cells, "edge_like") | cells["context_type"].eq("between_train_runs"),
            bool_series(cells, "e72_active"),
            "context_high",
            "e72_active",
        ),
    }
    for scope_name, scope_frame in [("all_moved", cells), ("top_benefit_focus", focus)]:
        for axis_name, (left_all, right_all, left_label, right_label) in definitions.items():
            left = left_all.loc[scope_frame.index]
            right = right_all.loc[scope_frame.index]
            for lval in [False, True]:
                for rval in [False, True]:
                    part = scope_frame[left.eq(lval) & right.eq(rval)]
                    if part.empty:
                        continue
                    frames.append(
                        {
                            "scope": scope_name,
                            "axis": axis_name,
                            left_label: bool(lval),
                            right_label: bool(rval),
                            "n_cells": int(len(part)),
                            "expected_delta": float(part["expected_delta_focus_mean"].sum()),
                            "benefit_sum": float(part["benefit_contrib"].sum()),
                            "risk_sum": float(part["risk_contrib"].sum()),
                            "edge_like_rate": float(bool_series(part, "edge_like").mean()),
                            "between_train_runs_rate": float(part["context_type"].eq("between_train_runs").mean()),
                            "all_veto_null_rate": float(bool_series(part, "all_veto_null").mean()),
                            "all_safe_density_mean": float(part["all_safe_density"].mean()),
                            "e72_active_rate": float(bool_series(part, "e72_active").mean()),
                        }
                    )
    return pd.DataFrame(frames)


def run() -> None:
    cells = pd.read_csv(CELLS_IN, low_memory=False)
    e166 = cells[cells["pair"].eq("e166_vs_e95")].copy()
    if e166.empty:
        raise RuntimeError("No e166_vs_e95 cells found")
    focus = e166.nsmallest(74, "benefit_rank").copy()
    policies = make_policy_masks(e166)
    rows = []
    for name, mask in policies.items():
        rows.append(summarize(name, e166[mask], e166, focus))
    summary = pd.DataFrame(rows)
    all_row = summary[summary["policy"].eq("all_e166")].iloc[0]
    summary["context_gain_vs_all"] = np.maximum(
        summary["edge_like_rate"] - float(all_row["edge_like_rate"]),
        summary["between_train_runs_rate"] - float(all_row["between_train_runs_rate"]),
    )
    summary["veto_gain_vs_all"] = summary["all_veto_null_rate"] - float(all_row["all_veto_null_rate"])
    summary["density_gain_vs_all"] = summary["all_safe_density_mean"] - float(all_row["all_safe_density_mean"])
    summary["e72_reduction_vs_all"] = float(all_row["e72_active_rate"]) - summary["e72_active_rate"]
    summary["decoupling_pass"] = (
        summary["expected_delta"].le(-1.0e-4)
        & summary["cells_to_flip_expected"].ge(20)
        & summary["top1_expected_ratio"].le(0.05)
        & summary["context_gain_vs_all"].ge(0.05)
        & summary["veto_gain_vs_all"].ge(0.05)
        & summary["density_gain_vs_all"].ge(0.05)
        & summary["e72_reduction_vs_all"].ge(0.0)
    )
    summary = summary.sort_values(["decoupling_pass", "expected_delta"], ascending=[False, True])
    quadrants = quadrant_rows(e166, focus)
    frontier = summary[
        (summary["expected_delta"].le(-5.0e-5))
        | summary["context_gain_vs_all"].ge(0.10)
        | summary["veto_gain_vs_all"].ge(0.25)
        | summary["density_gain_vs_all"].ge(0.10)
    ].copy()
    frontier = frontier.sort_values(["decoupling_pass", "expected_delta"], ascending=[False, True])

    summary.to_csv(SUMMARY_OUT, index=False)
    quadrants.to_csv(QUADRANTS_OUT, index=False)
    frontier.to_csv(FRONTIER_OUT, index=False)

    decoupled = int(summary["decoupling_pass"].sum())
    best_context_safe = summary[
        summary["policy"].str.contains("context_high__veto|context_strict__veto", regex=True)
    ].sort_values(
        "expected_delta"
    ).head(6)
    top_context = summary.sort_values("context_gain_vs_all", ascending=False).head(8)
    top_safe = summary.sort_values(["veto_gain_vs_all", "density_gain_vs_all"], ascending=False).head(8)
    lines = [
        "# E168 E166 Safety-Context Decoupling",
        "",
        "## Question",
        "",
        "Can E166's hidden-context signal be separated from its safety-atlas divergence by simple local masks, or are the two coupled?",
        "",
        "## Criteria",
        "",
        "A simple decoupled repair must keep material expected edge (`<= -1e-4`), breadth (`cells_to_flip_expected >= 20`, `top1_expected_ratio <= 0.05`), context gain (`>= 0.05`), safety gain (`veto` and `safe_density` both `>= 0.05` better than all-E166), and no worse E72-active rate. `context_high` means edge-like OR between-train-runs; `context_strict` means edge-like AND between-train-runs.",
        "",
        f"- decoupling-pass policies: `{decoupled}`.",
        f"- all-E166 expected delta: `{float(all_row['expected_delta']):.9f}`.",
        f"- all-E166 cells-to-flip expected: `{int(all_row['cells_to_flip_expected'])}`.",
        f"- all-E166 top1/expected: `{float(all_row['top1_expected_ratio']):.9f}`.",
        "",
        "## Policy Summary",
        "",
        md_table(
            summary,
            [
                "policy",
                "n_cells",
                "expected_delta",
                "expected_abs_share_vs_all",
                "benefit_share_vs_all_focus",
                "top_benefit_focus_cells_kept",
                "cells_to_flip_expected",
                "top1_expected_ratio",
                "edge_like_rate",
                "between_train_runs_rate",
                "all_veto_null_rate",
                "all_safe_density_mean",
                "e72_active_rate",
                "decoupling_pass",
            ],
            30,
        ),
        "",
        "## Best Context+Veto Intersections",
        "",
        md_table(
            best_context_safe,
            [
                "policy",
                "n_cells",
                "expected_delta",
                "expected_abs_share_vs_all",
                "benefit_share_vs_all_focus",
                "top_benefit_focus_cells_kept",
                "cells_to_flip_expected",
                "top1_expected_ratio",
                "edge_like_rate",
                "between_train_runs_rate",
                "all_veto_null_rate",
                "all_safe_density_mean",
                "e72_active_rate",
            ],
            10,
        ),
        "",
        "## Strongest Context Masks",
        "",
        md_table(
            top_context,
            [
                "policy",
                "n_cells",
                "expected_delta",
                "expected_abs_share_vs_all",
                "context_gain_vs_all",
                "all_veto_null_rate",
                "all_safe_density_mean",
                "e72_active_rate",
                "cells_to_flip_expected",
                "top1_expected_ratio",
            ],
            10,
        ),
        "",
        "## Strongest Safety Masks",
        "",
        md_table(
            top_safe,
            [
                "policy",
                "n_cells",
                "expected_delta",
                "expected_abs_share_vs_all",
                "context_gain_vs_all",
                "veto_gain_vs_all",
                "density_gain_vs_all",
                "e72_reduction_vs_all",
                "cells_to_flip_expected",
                "top1_expected_ratio",
            ],
            10,
        ),
        "",
        "## Quadrants",
        "",
        md_table(quadrants, n=40),
        "",
        "## Decision",
        "",
        "E168 does not create a repaired E166 submission, but it falsifies the strongest negative version of E167. The broad signal is not fully inseparable from safety: `context_high__veto` and `context_high__high_density_p50` keep material expected edge, breadth, context gain, and safety gain. The strict edge-and-between subset is too small and too top-cell fragile, so this is not a scale-up license. The next smallest action is to materialize the best context-high safety mask and rerun full breadth/bad-axis stress before treating it as a submission candidate.",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(REPORT_OUT)
    print(SUMMARY_OUT)
    print(QUADRANTS_OUT)
    print(FRONTIER_OUT)


if __name__ == "__main__":
    run()
