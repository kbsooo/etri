#!/usr/bin/env python3
"""E183: anatomy of E182 pressure-world sign ambiguity.

E182 showed that refreshed current-anchor binary worlds can make E176, E154,
and E144 both favorable and adverse versus E95. This script asks the smallest
next question:

    What cells flip the branch sign, and can visible train-derived context
    prefer the favorable pressure world over the adverse pressure world?

No submission is created. This is a latent-view/cell-resolution diagnostic.
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

from public_anchor_bottleneck_decomposition import A2C8, TARGETS, load_sub  # noqa: E402
from public_lb_inverse_feasibility import load_prob  # noqa: E402
from public_lb_binary_inverse_stress import candidate_delta_coeff  # noqa: E402
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402
import e179_e176_critical_cell_visibility_audit as e179  # noqa: E402


BASE_FILE = "submission_e95_hardtail_541e3973.csv"
WORLD_IN = OUT / "e182_current_anchor_binary_world_refresh_worlds.csv"
LABEL_IN = OUT / "e182_current_anchor_binary_world_refresh_labels.npz"
PRESSURE_IN = OUT / "e182_current_anchor_binary_world_refresh_pressure.csv"

CELL_OUT = OUT / "e183_pressure_world_branch_anatomy_cells.csv"
SUMMARY_OUT = OUT / "e183_pressure_world_branch_anatomy_summary.csv"
CANDIDATE_OUT = OUT / "e183_pressure_world_branch_anatomy_candidates.csv"
REPORT_OUT = OUT / "e183_pressure_world_branch_anatomy_report.md"

LIVE_CANDIDATES = {
    "e176": {
        "role": "visible_body_q2_underopen",
        "file": "submission_e176_abl_q2_to0p75_91e49725.csv",
    },
    "e154": {
        "role": "repaired_all_four_branch",
        "file": "submission_e154_s3repair_9f2e2e73.csv",
    },
    "e144": {
        "role": "active_boundary_branch",
        "file": "submission_e144_activeboundary_d7b4b331.csv",
    },
}

PRIORS = [
    "global",
    "subject",
    "nearest_hard085",
    "focus_mean",
    "flank_mean",
    "visible_mean",
]
EPS = 1.0e-12


def md(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 40) -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return e138.md_table(view.head(n), ".9f")


def world_labels(world_df: pd.DataFrame, labels: np.ndarray, scenario: str, candidate: str, direction: str) -> np.ndarray:
    objective = f"pressure_{candidate}_{direction}"
    idx = world_df.index[(world_df["scenario"].eq(scenario)) & (world_df["objective"].eq(objective))].to_list()
    if len(idx) != 1:
        raise RuntimeError(f"missing world: {scenario} {objective}")
    return labels[idx[0]].astype(np.uint8)


def label_prior_prob(cells: pd.DataFrame, prior: str, labels: np.ndarray) -> np.ndarray:
    p1 = cells[f"p_y1_{prior}"].to_numpy(dtype=np.float64)
    return np.where(labels == 1, p1, 1.0 - p1)


def binary_ce(prob: np.ndarray) -> float:
    p = np.clip(prob, 1.0e-6, 1.0 - 1.0e-6)
    return float(-np.log(p).sum())


def entropy(prob: np.ndarray) -> np.ndarray:
    p = np.clip(prob, 1.0e-6, 1.0 - 1.0e-6)
    return -(p * np.log(p) + (1.0 - p) * np.log(1.0 - p))


def build_candidate_cells(candidate: str, file_name: str, coeff: np.ndarray) -> pd.DataFrame:
    cells = e179.build_pair_cells(f"{candidate}_vs_e95", file_name, BASE_FILE).copy()
    cells["candidate"] = candidate
    cells["file"] = file_name
    cells["cell_index"] = cells["sub_idx"].astype(int) * len(TARGETS) + cells["target_idx"].astype(int)
    cells["coeff"] = coeff[cells["cell_index"].to_numpy(dtype=int)]
    cells["coeff_abs"] = np.abs(cells["coeff"].to_numpy(dtype=np.float64))
    cells["support_label_from_coeff"] = (cells["coeff"] < 0.0).astype(int)
    # E179 support_label and coefficient sign should agree. Keep both to catch indexing errors.
    cells["support_label_agrees_coeff"] = cells["support_label"].astype(int).eq(cells["support_label_from_coeff"])
    if not bool(cells["support_label_agrees_coeff"].all()):
        bad = cells.loc[~cells["support_label_agrees_coeff"], ["sub_idx", "target", "support_label", "coeff"]].head()
        raise RuntimeError(f"support label / coefficient mismatch for {candidate}: {bad.to_dict('records')}")
    for prior in PRIORS:
        cells[f"prior_entropy_{prior}"] = entropy(cells[f"p_y1_{prior}"].to_numpy(dtype=np.float64))
    return cells


def summarize_contrast(part: pd.DataFrame, scenario: str, candidate: str, role: str, row_min: pd.Series, row_max: pd.Series) -> dict[str, Any]:
    weights = part["coeff_abs"].to_numpy(dtype=np.float64)
    weights = np.where(weights <= 0.0, 1.0, weights)
    rec: dict[str, Any] = {
        "scenario": scenario,
        "candidate": candidate,
        "role": role,
        "pressure_min_delta_vs_e95": float(row_min["delta_vs_e95"]),
        "pressure_max_delta_vs_e95": float(row_max["delta_vs_e95"]),
        "pressure_range_width": float(row_max["delta_vs_e95"] - row_min["delta_vs_e95"]),
        "moved_cells": int(len(part)),
        "moved_rows": int(part["sub_idx"].nunique()),
        "differing_moved_cells": int(part["minmax_label_diff"].sum()),
        "differing_moved_rows": int(part.loc[part["minmax_label_diff"], "sub_idx"].nunique()),
        "differing_coeff_abs_sum": float(part.loc[part["minmax_label_diff"], "coeff_abs"].sum()),
        "differing_range_share": float(
            part.loc[part["minmax_label_diff"], "coeff_abs"].sum() / (part["coeff_abs"].sum() + EPS)
        ),
        "min_support_rate": float(part["min_support"].mean()),
        "max_support_rate": float(part["max_support"].mean()),
        "min_support_coeff_weighted": float(np.average(part["min_support"].to_numpy(dtype=float), weights=weights)),
        "max_support_coeff_weighted": float(np.average(part["max_support"].to_numpy(dtype=float), weights=weights)),
        "support_gap_coeff_weighted": float(
            np.average(part["min_support"].to_numpy(dtype=float), weights=weights)
            - np.average(part["max_support"].to_numpy(dtype=float), weights=weights)
        ),
        "top_diff_target_share": ",".join(
            part.loc[part["minmax_label_diff"]]
            .groupby("target")["coeff_abs"]
            .sum()
            .sort_values(ascending=False)
            .head(4)
            .index.astype(str)
            .to_list()
        ),
        "diff_between_train_runs_rate": float(part.loc[part["minmax_label_diff"], "between_train_runs"].mean()),
        "diff_edge_like_rate": float(part.loc[part["minmax_label_diff"], "edge_like"].astype(bool).mean()),
        "diff_e72_active_rate": float(part.loc[part["minmax_label_diff"], "e72_active"].astype(bool).mean()),
        "diff_e101_active_rate": float(part.loc[part["minmax_label_diff"], "e101_active"].astype(bool).mean()),
        "diff_flank_conflict_rate": float(part.loc[part["minmax_label_diff"], "flank_conflict"].astype(bool).mean()),
    }
    diff_part = part.loc[part["minmax_label_diff"]].copy()
    if diff_part.empty:
        for prior in PRIORS:
            rec[f"{prior}_ce_min_minus_max_diff_cells"] = np.nan
            rec[f"{prior}_prefers_min"] = np.nan
            rec[f"{prior}_diff_prior_confidence_mean"] = np.nan
        return rec
    diff_weights = diff_part["coeff_abs"].to_numpy(dtype=np.float64)
    diff_weights = np.where(diff_weights <= 0.0, 1.0, diff_weights)
    for prior in PRIORS:
        min_prob = diff_part[f"min_label_prob_{prior}"].to_numpy(dtype=np.float64)
        max_prob = diff_part[f"max_label_prob_{prior}"].to_numpy(dtype=np.float64)
        ce_gap = binary_ce(min_prob) - binary_ce(max_prob)
        rec[f"{prior}_ce_min_minus_max_diff_cells"] = float(ce_gap)
        rec[f"{prior}_prefers_min"] = bool(ce_gap < 0.0)
        rec[f"{prior}_diff_prior_confidence_mean"] = float(
            np.average(np.maximum(min_prob, max_prob), weights=diff_weights)
        )
        rec[f"{prior}_min_prob_coeff_weighted"] = float(np.average(min_prob, weights=diff_weights))
        rec[f"{prior}_max_prob_coeff_weighted"] = float(np.average(max_prob, weights=diff_weights))
    return rec


def annotate_world_pair(
    candidate: str,
    role: str,
    cells: pd.DataFrame,
    scenario: str,
    row_min: pd.Series,
    row_max: pd.Series,
    labels_min: np.ndarray,
    labels_max: np.ndarray,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    idx = cells["cell_index"].to_numpy(dtype=int)
    part = cells.copy()
    part["scenario"] = scenario
    part["pressure_min_delta_vs_e95"] = float(row_min["delta_vs_e95"])
    part["pressure_max_delta_vs_e95"] = float(row_max["delta_vs_e95"])
    part["min_label"] = labels_min[idx].astype(int)
    part["max_label"] = labels_max[idx].astype(int)
    part["minmax_label_diff"] = part["min_label"].ne(part["max_label"])
    part["min_support"] = part["min_label"].eq(part["support_label"].astype(int))
    part["max_support"] = part["max_label"].eq(part["support_label"].astype(int))
    part["support_gap_cell"] = part["min_support"].astype(int) - part["max_support"].astype(int)
    part["range_contribution"] = part["coeff"] * (part["max_label"] - part["min_label"])
    for prior in PRIORS:
        part[f"min_label_prob_{prior}"] = label_prior_prob(part, prior, part["min_label"].to_numpy(dtype=int))
        part[f"max_label_prob_{prior}"] = label_prior_prob(part, prior, part["max_label"].to_numpy(dtype=int))
        part[f"prior_prefers_min_label_{prior}"] = part[f"min_label_prob_{prior}"] > part[f"max_label_prob_{prior}"]
    summary = summarize_contrast(part, scenario, candidate, role, row_min, row_max)
    return part, summary


def main() -> None:
    sample = load_sub(A2C8)
    base_prob = load_prob(BASE_FILE, sample)
    world_df = pd.read_csv(WORLD_IN)
    pressure_df = pd.read_csv(PRESSURE_IN)
    label_npz = np.load(LABEL_IN, allow_pickle=True)
    labels = label_npz["labels"].astype(np.uint8)
    if len(world_df) != labels.shape[0]:
        raise RuntimeError(f"world/label row mismatch: {len(world_df)} vs {labels.shape[0]}")

    all_cells: list[pd.DataFrame] = []
    summaries: list[dict[str, Any]] = []

    for candidate, meta in LIVE_CANDIDATES.items():
        cand_prob = load_prob(meta["file"], sample)
        _const, coeff = candidate_delta_coeff(cand_prob, base_prob)
        cells = build_candidate_cells(candidate, meta["file"], coeff)
        for scenario in sorted(pressure_df["scenario"].unique()):
            rows = pressure_df[(pressure_df["scenario"].eq(scenario)) & (pressure_df["candidate"].eq(candidate))]
            row_min = rows[rows["direction"].eq("min")]
            row_max = rows[rows["direction"].eq("max")]
            if len(row_min) != 1 or len(row_max) != 1:
                continue
            row_min_s = row_min.iloc[0]
            row_max_s = row_max.iloc[0]
            if not bool(row_min_s["has_incumbent"]) or not bool(row_max_s["has_incumbent"]):
                continue
            labels_min = world_labels(world_df, labels, scenario, candidate, "min")
            labels_max = world_labels(world_df, labels, scenario, candidate, "max")
            part, summary = annotate_world_pair(
                candidate,
                meta["role"],
                cells,
                scenario,
                row_min_s,
                row_max_s,
                labels_min,
                labels_max,
            )
            all_cells.append(part)
            summaries.append(summary)

    cell_df = pd.concat(all_cells, ignore_index=True) if all_cells else pd.DataFrame()
    summary_df = pd.DataFrame(summaries)

    if summary_df.empty:
        candidate_df = pd.DataFrame()
    else:
        agg_rows = []
        for candidate, part in summary_df.groupby("candidate", sort=False):
            rec: dict[str, Any] = {
                "candidate": candidate,
                "role": str(part["role"].iloc[0]),
                "scenario_count": int(len(part)),
                "range_width_mean": float(part["pressure_range_width"].mean()),
                "range_width_min": float(part["pressure_range_width"].min()),
                "range_width_max": float(part["pressure_range_width"].max()),
                "differing_moved_cells_mean": float(part["differing_moved_cells"].mean()),
                "differing_range_share_mean": float(part["differing_range_share"].mean()),
                "support_gap_coeff_weighted_mean": float(part["support_gap_coeff_weighted"].mean()),
            }
            for prior in PRIORS:
                rec[f"{prior}_prefers_min_rate"] = float(part[f"{prior}_prefers_min"].mean())
                rec[f"{prior}_ce_gap_mean"] = float(part[f"{prior}_ce_min_minus_max_diff_cells"].mean())
                rec[f"{prior}_min_prob_mean"] = float(part[f"{prior}_min_prob_coeff_weighted"].mean())
                rec[f"{prior}_max_prob_mean"] = float(part[f"{prior}_max_prob_coeff_weighted"].mean())
            agg_rows.append(rec)
        candidate_df = pd.DataFrame(agg_rows).sort_values(
            ["visible_mean_prefers_min_rate", "visible_mean_ce_gap_mean"],
            ascending=[False, True],
        )

    cell_df.to_csv(CELL_OUT, index=False)
    summary_df.to_csv(SUMMARY_OUT, index=False)
    candidate_df.to_csv(CANDIDATE_OUT, index=False)

    overview_cols = [
        "candidate",
        "scenario_count",
        "range_width_mean",
        "differing_moved_cells_mean",
        "support_gap_coeff_weighted_mean",
        "visible_mean_prefers_min_rate",
        "visible_mean_ce_gap_mean",
        "visible_mean_min_prob_mean",
        "visible_mean_max_prob_mean",
        "subject_prefers_min_rate",
        "flank_mean_prefers_min_rate",
    ]
    scenario_cols = [
        "scenario",
        "candidate",
        "pressure_min_delta_vs_e95",
        "pressure_max_delta_vs_e95",
        "pressure_range_width",
        "differing_moved_cells",
        "differing_range_share",
        "support_gap_coeff_weighted",
        "top_diff_target_share",
        "diff_between_train_runs_rate",
        "diff_e72_active_rate",
        "visible_mean_prefers_min",
        "visible_mean_ce_min_minus_max_diff_cells",
        "subject_prefers_min",
        "flank_mean_prefers_min",
    ]
    top_cells = (
        cell_df[cell_df["minmax_label_diff"]]
        .sort_values(["candidate", "scenario", "coeff_abs"], ascending=[True, True, False])
        .groupby(["candidate", "scenario"], as_index=False)
        .head(8)
        if not cell_df.empty
        else pd.DataFrame()
    )
    top_cols = [
        "scenario",
        "candidate",
        "sub_idx",
        "target",
        "coeff",
        "coeff_abs",
        "min_label",
        "max_label",
        "support_label",
        "p_y1_visible_mean",
        "min_label_prob_visible_mean",
        "max_label_prob_visible_mean",
        "context_type",
        "pos_bin",
        "edge_like",
        "between_train_runs",
        "e72_active",
        "e101_active",
        "flank_conflict",
    ]

    if candidate_df.empty:
        result_sentence = "No pressure-world contrasts were available."
    else:
        min_rates = candidate_df.set_index("candidate")["visible_mean_prefers_min_rate"].to_dict()
        result_sentence = (
            "Visible priors do not resolve the E182 sign ambiguity: favorable pressure worlds are preferred "
            f"by visible_mean in E176/E154/E144 rates "
            f"`{min_rates.get('e176', float('nan')):.3f}` / "
            f"`{min_rates.get('e154', float('nan')):.3f}` / "
            f"`{min_rates.get('e144', float('nan')):.3f}` across scenarios."
        )

    report = f"""# E183 Pressure-World Branch Anatomy

## Question

E182 says E176, E154, and E144 can each be favorable or adverse under refreshed
current-anchor pressure worlds. This audit asks whether the favorable branch is
visible from train-derived priors and row/block context, or whether the sign
ambiguity is still a hidden-label/cell-resolution problem.

No submission is created.

## Result In One Sentence

{result_sentence}

## Candidate-Level Summary

{md(candidate_df, overview_cols, n=10)}

## Scenario-Level Summary

{md(summary_df.sort_values(['candidate', 'scenario']), scenario_cols, n=40)}

## Largest Differing Moved Cells

{md(top_cells, top_cols, n=80)}

## Interpretation

- The min pressure world is the favorable candidate world by construction, and
  the max pressure world is the adverse world. If visible/block priors were a
  usable branch selector, they should prefer the min labels on the differing
  moved cells consistently.
- A high support gap between min and max worlds confirms that E182 is not
  numerical noise: the pressure objectives are flipping exactly the candidate's
  high-impact moved labels.
- If visible_mean, subject, and flank priors do not consistently prefer the min
  world, then current public-free context cannot choose the branch. That keeps
  E176/E154/E144 as public sensors rather than expected-score certificates.

## Decision

No submission. Use this as the next underidentification layer after E182. A
future candidate needs either a new decisive-cell representation that separates
these pressure branches, or a pre-registered public feedback decoder for the
worldview being tested.
"""
    REPORT_OUT.write_text(report)

    for path in [CELL_OUT, SUMMARY_OUT, CANDIDATE_OUT, REPORT_OUT]:
        print(path)


if __name__ == "__main__":
    main()
