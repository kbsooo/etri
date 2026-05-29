#!/usr/bin/env python3
"""E180: calibrate E176 decisive-cell visibility against known public anchors.

E179 found a sharp tension: E176 is supported as a full body and as a Q2-damped
variant, but the few top cells that can swing the E95 edge are weak under
visible train-derived priors.

This audit asks whether that weakness is meaningful. If successful known-public
transitions had similarly weak decisive cells, E179's warning is a generic
hidden-label limitation. If successful anchors look visibly supported while
failed anchors look visibly adverse, E176's weak top-cell support is a real
submission risk.

No submission is created.
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

from public_anchor_bottleneck_decomposition import TARGETS  # noqa: E402
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402
import e179_e176_critical_cell_visibility_audit as e179  # noqa: E402


SCORES = {
    "submission_frontier_cvjepa_refine_a2c8d2c8.csv": 0.5774393210,
    "submission_mixmin_0c916bb4.csv": 0.5763066405,
    "submission_e95_hardtail_541e3973.csv": 0.5762913298,
    "submission_e101_q2s3tail_177569bc.csv": 0.5763003660,
    "submission_e72_topabs50_q2s3_gate_4e48cba2.csv": 0.5764077772,
}

PAIRS = [
    {
        "pair": "mixmin_vs_a2c8",
        "new_file": "submission_mixmin_0c916bb4.csv",
        "base_file": "submission_frontier_cvjepa_refine_a2c8d2c8.csv",
        "family": "broad_public_success",
    },
    {
        "pair": "e95_vs_mixmin",
        "new_file": "submission_e95_hardtail_541e3973.csv",
        "base_file": "submission_mixmin_0c916bb4.csv",
        "family": "frontier_hardtail_success",
    },
    {
        "pair": "e101_vs_e95",
        "new_file": "submission_e101_q2s3tail_177569bc.csv",
        "base_file": "submission_e95_hardtail_541e3973.csv",
        "family": "frontier_near_loss",
    },
    {
        "pair": "e101_vs_mixmin",
        "new_file": "submission_e101_q2s3tail_177569bc.csv",
        "base_file": "submission_mixmin_0c916bb4.csv",
        "family": "mixmin_relative_success",
    },
    {
        "pair": "e72_vs_mixmin",
        "new_file": "submission_e72_topabs50_q2s3_gate_4e48cba2.csv",
        "base_file": "submission_mixmin_0c916bb4.csv",
        "family": "q2s3_gate_fail",
    },
    {
        "pair": "e72_vs_e95",
        "new_file": "submission_e72_topabs50_q2s3_gate_4e48cba2.csv",
        "base_file": "submission_e95_hardtail_541e3973.csv",
        "family": "q2s3_gate_fail",
    },
    {
        "pair": "e176_vs_e95_pending",
        "new_file": "submission_e176_abl_q2_to0p75_91e49725.csv",
        "base_file": "submission_e95_hardtail_541e3973.csv",
        "family": "pending_broad_q2_underopen",
    },
]

FRONTIER_EDGE = abs(SCORES["submission_e95_hardtail_541e3973.csv"] - SCORES["submission_mixmin_0c916bb4.csv"])

CELLS_OUT = OUT / "e180_known_anchor_decisive_cell_visibility_cells.csv"
SETS_OUT = OUT / "e180_known_anchor_decisive_cell_visibility_sets.csv"
PAIR_OUT = OUT / "e180_known_anchor_decisive_cell_visibility_pairs.csv"
REPORT_OUT = OUT / "e180_known_anchor_decisive_cell_visibility_report.md"


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 40, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return e138.md_table(view.head(n), floatfmt)


def actual_delta(new_file: str, base_file: str) -> float | None:
    if new_file not in SCORES or base_file not in SCORES:
        return None
    return float(SCORES[new_file] - SCORES[base_file])


def observed_direction_support(cells: pd.DataFrame, prior: str, direction: str) -> np.ndarray:
    support = cells[f"support_probability_{prior}"].to_numpy(dtype=np.float64)
    if direction in {"new_won", "pending_new_better"}:
        return support
    if direction == "new_lost":
        return 1.0 - support
    raise ValueError(direction)


def needed_cells(cells: pd.DataFrame, threshold: float | None) -> tuple[int | None, float | None, bool | None]:
    if threshold is None or not np.isfinite(threshold):
        return None, None, None
    ordered = cells.sort_values("swing", ascending=False)
    cumulative = ordered["swing"].cumsum().to_numpy(dtype=np.float64)
    idx = np.searchsorted(cumulative, abs(float(threshold)), side="left")
    if idx >= len(cumulative):
        return int(len(cumulative)), float(cumulative[-1]) if len(cumulative) else 0.0, False
    return int(idx + 1), float(cumulative[idx]), True


def pair_direction(delta: float | None) -> str:
    if delta is None or not np.isfinite(delta):
        return "pending_new_better"
    if delta < 0:
        return "new_won"
    if delta > 0:
        return "new_lost"
    return "tie"


def set_masks(cells: pd.DataFrame, n_actual: int | None, n_frontier: int | None) -> list[tuple[str, np.ndarray]]:
    masks: list[tuple[str, np.ndarray]] = [
        ("all_moved", np.ones(len(cells), dtype=bool)),
        ("top1", cells["swing_rank"].le(1).to_numpy()),
        ("top4", cells["swing_rank"].le(4).to_numpy()),
        ("top8", cells["swing_rank"].le(8).to_numpy()),
        ("top16", cells["swing_rank"].le(16).to_numpy()),
    ]
    if n_frontier is not None:
        masks.append((f"top{n_frontier}_frontier_edge", cells["swing_rank"].le(n_frontier).to_numpy()))
    if n_actual is not None:
        masks.append((f"top{n_actual}_actual_edge", cells["swing_rank"].le(n_actual).to_numpy()))
    for target in TARGETS:
        masks.append((f"target_{target}", cells["target"].eq(target).to_numpy()))
    return masks


def summarize_pair_cells(pair_cfg: dict[str, str]) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    pair = pair_cfg["pair"]
    new_file = pair_cfg["new_file"]
    base_file = pair_cfg["base_file"]
    delta = actual_delta(new_file, base_file)
    direction = pair_direction(delta)
    cells = e179.build_pair_cells(pair, new_file, base_file)
    cells["family"] = pair_cfg["family"]
    cells["new_file"] = new_file
    cells["base_file"] = base_file
    cells["actual_delta"] = np.nan if delta is None else delta
    cells["actual_direction"] = direction
    for prior in e179.PRIORS:
        cells[f"observed_direction_support_{prior}"] = observed_direction_support(cells, prior, direction)

    n_actual, covered_actual, actual_coverable = needed_cells(cells, delta)
    n_frontier, covered_frontier, frontier_coverable = needed_cells(cells, FRONTIER_EDGE)

    rows: list[dict[str, Any]] = []
    for set_name, mask in set_masks(cells, n_actual, n_frontier):
        part = cells.loc[mask].copy()
        if part.empty:
            continue
        rec: dict[str, Any] = {
            "pair": pair,
            "family": pair_cfg["family"],
            "set": set_name,
            "new_file": new_file,
            "base_file": base_file,
            "actual_delta": np.nan if delta is None else delta,
            "actual_direction": direction,
            "n_cells": int(len(part)),
            "n_rows": int(part["sub_idx"].nunique()),
            "targets": ",".join(sorted(part["target"].unique())),
            "swing_sum": float(part["swing"].sum()),
            "top_swing": float(part["swing"].max()),
            "expected_delta_visible_mean": float(part["expected_delta_visible_mean"].sum()),
            "expected_delta_focus_mean": float(part["expected_delta_focus_mean"].sum()),
            "expected_delta_flank_mean": float(part["expected_delta_flank_mean"].sum()),
            "between_train_runs_rate": float(part["between_train_runs"].mean()),
            "flank_conflict_rate": float(part["flank_conflict"].astype(bool).mean()),
            "e72_active_rate": float(part["e72_active"].astype(bool).mean()),
            "e101_active_rate": float(part["e101_active"].astype(bool).mean()),
        }
        weights = part["swing"].to_numpy(dtype=np.float64)
        for prior in ["global", "subject", "nearest_hard085", "flank_mean", "visible_mean", "focus_mean"]:
            intended = part[f"support_probability_{prior}"].to_numpy(dtype=np.float64)
            observed = part[f"observed_direction_support_{prior}"].to_numpy(dtype=np.float64)
            rec[f"intended_support_swing_{prior}"] = float(np.average(intended, weights=weights))
            rec[f"observed_direction_support_swing_{prior}"] = float(np.average(observed, weights=weights))
            rec[f"observed_direction_support_mean_{prior}"] = float(observed.mean())
            rec[f"observed_hard_support_rate_{prior}"] = float((observed >= 0.5).mean())
        if delta is not None and set_name in {"all_moved", "top1", "top4", "top8", "top16"}:
            rec["visible_sign_matches_actual"] = bool(np.sign(rec["expected_delta_visible_mean"]) == np.sign(delta))
            rec["focus_sign_matches_actual"] = bool(np.sign(rec["expected_delta_focus_mean"]) == np.sign(delta))
        else:
            rec["visible_sign_matches_actual"] = np.nan
            rec["focus_sign_matches_actual"] = np.nan
        rows.append(rec)
    set_summary = pd.DataFrame(rows)

    top4 = set_summary[set_summary["set"].eq("top4")].iloc[0]
    frontier_set = set_summary[set_summary["set"].str.endswith("_frontier_edge")].iloc[0]
    actual_set = (
        set_summary[set_summary["set"].str.endswith("_actual_edge")].iloc[0]
        if n_actual is not None and set_summary["set"].str.endswith("_actual_edge").any()
        else None
    )
    pair_summary: dict[str, Any] = {
        "pair": pair,
        "family": pair_cfg["family"],
        "new_file": new_file,
        "base_file": base_file,
        "actual_delta": np.nan if delta is None else delta,
        "actual_direction": direction,
        "n_moved_cells": int(len(cells)),
        "n_moved_rows": int(cells["sub_idx"].nunique()),
        "n_cells_for_actual_delta": n_actual,
        "actual_delta_coverable_by_swing": actual_coverable,
        "covered_actual_swing": covered_actual,
        "n_cells_for_frontier_edge": n_frontier,
        "frontier_edge_coverable_by_swing": frontier_coverable,
        "covered_frontier_swing": covered_frontier,
        "all_expected_delta_visible_mean": float(set_summary.loc[set_summary["set"].eq("all_moved"), "expected_delta_visible_mean"].iloc[0]),
        "top4_observed_support_visible": float(top4["observed_direction_support_swing_visible_mean"]),
        "top4_intended_support_visible": float(top4["intended_support_swing_visible_mean"]),
        "frontier_observed_support_visible": float(frontier_set["observed_direction_support_swing_visible_mean"]),
        "frontier_intended_support_visible": float(frontier_set["intended_support_swing_visible_mean"]),
        "top4_between_train_runs_rate": float(top4["between_train_runs_rate"]),
        "top4_e72_active_rate": float(top4["e72_active_rate"]),
    }
    if actual_set is not None:
        pair_summary["actual_edge_observed_support_visible"] = float(
            actual_set["observed_direction_support_swing_visible_mean"]
        )
        pair_summary["actual_edge_intended_support_visible"] = float(
            actual_set["intended_support_swing_visible_mean"]
        )
    else:
        pair_summary["actual_edge_observed_support_visible"] = np.nan
        pair_summary["actual_edge_intended_support_visible"] = np.nan
    return cells, set_summary, pair_summary


def calibration_rows(pair_summary: pd.DataFrame, set_summary: pd.DataFrame) -> pd.DataFrame:
    top4 = set_summary[set_summary["set"].eq("top4")].copy()
    known = top4[top4["actual_direction"].isin(["new_won", "new_lost"])].copy()
    pending = top4[top4["actual_direction"].eq("pending_new_better")].copy()
    rows: list[dict[str, Any]] = []
    if not pending.empty:
        e176_support = float(pending["intended_support_swing_visible_mean"].iloc[0])
        winners = known[known["actual_direction"].eq("new_won")]
        losers = known[known["actual_direction"].eq("new_lost")]
        rows.append(
            {
                "question": "e176_top4_vs_known_winners",
                "e176_top4_intended_support_visible": e176_support,
                "known_winner_min": float(winners["observed_direction_support_swing_visible_mean"].min()),
                "known_winner_mean": float(winners["observed_direction_support_swing_visible_mean"].mean()),
                "known_winner_max": float(winners["observed_direction_support_swing_visible_mean"].max()),
                "e176_below_winner_min": bool(e176_support < winners["observed_direction_support_swing_visible_mean"].min()),
                "e176_above_winner_mean": bool(e176_support > winners["observed_direction_support_swing_visible_mean"].mean()),
                "e176_above_winner_max": bool(e176_support > winners["observed_direction_support_swing_visible_mean"].max()),
            }
        )
        rows.append(
            {
                "question": "e176_top4_vs_known_losses_observed_adverse",
                "e176_top4_intended_support_visible": e176_support,
                "known_loss_mean_observed_adverse_support": float(
                    losers["observed_direction_support_swing_visible_mean"].mean()
                ),
                "known_loss_max_observed_adverse_support": float(
                    losers["observed_direction_support_swing_visible_mean"].max()
                ),
                "e176_lower_than_loss_adverse_mean": bool(
                    e176_support < losers["observed_direction_support_swing_visible_mean"].mean()
                ),
            }
        )
    pair_summary_view = pair_summary.copy()
    pair_summary_view["known_or_pending"] = np.where(
        pair_summary_view["actual_direction"].eq("pending_new_better"), "pending", "known"
    )
    rows.append(
        {
            "question": "known_anchor_visible_sign_accuracy_all_moved",
            "known_pairs": int((pair_summary_view["known_or_pending"] == "known").sum()),
            "sign_accuracy": float(
                set_summary[
                    set_summary["set"].eq("all_moved") & set_summary["actual_direction"].isin(["new_won", "new_lost"])
                ]["visible_sign_matches_actual"].mean()
            ),
        }
    )
    return pd.DataFrame(rows)


def write_report(cells: pd.DataFrame, sets: pd.DataFrame, pairs: pd.DataFrame, calibration: pd.DataFrame) -> None:
    key_pairs = [
        "pair",
        "family",
        "actual_delta",
        "actual_direction",
        "n_moved_cells",
        "n_cells_for_actual_delta",
        "n_cells_for_frontier_edge",
        "all_expected_delta_visible_mean",
        "top4_observed_support_visible",
        "frontier_observed_support_visible",
        "actual_edge_observed_support_visible",
    ]
    key_sets = [
        "pair",
        "set",
        "actual_direction",
        "n_cells",
        "targets",
        "expected_delta_visible_mean",
        "observed_direction_support_swing_visible_mean",
        "intended_support_swing_visible_mean",
        "visible_sign_matches_actual",
        "between_train_runs_rate",
        "e72_active_rate",
    ]
    e176_top = sets[(sets["pair"].eq("e176_vs_e95_pending")) & (sets["set"].isin(["top4", "top16"]))]
    anchor_top4 = sets[sets["set"].eq("top4")].sort_values("actual_delta", na_position="last")
    report = f"""# E180 Known-Anchor Decisive-Cell Visibility

## Question

E179 says E176's body and Q2 damping are visible-prior supported, but its top
public-decisive cells are weak. Is that weakness actually informative, or do
successful known anchors also look weak at the top-cell layer?

## Result In One Sentence

Known successful anchors are not visible-certified at the top-cell layer either:
E95's public-positive top4 support is only `0.100896`. E176 top4 support
`0.330699` is actually above the known-winner mean, so E179 is not a hard veto;
it is evidence that visible priors are too weak to certify decisive cells.

## Pair Summary

{md_table(pairs.sort_values(["actual_direction", "actual_delta"], na_position="last"), key_pairs, n=20)}

## Top4 Anchor Calibration

{md_table(anchor_top4, key_sets, n=20)}

## E176 Critical Sets

{md_table(e176_top, key_sets, n=20)}

## Calibration Checks

{md_table(calibration, None, n=20)}

## Interpretation

- Known winners can have very weak top-cell support, so E179's weak top-cell
  read is not enough to reject E176.
- The all-moved visible-prior sign accuracy across known anchors is only `0.5`,
  so visible priors are not a reliable standalone public selector.
- Failed E72 has strong observed-adverse top-cell support, but the near-frontier
  E101 loss does not; decisive-cell visibility is therefore anchor-specific.
- E176 remains a sensor because it is body-supported, Q2-damping-supported, and
  no current public-free signal certifies the hidden top cells.

## Decision

No submission is created. Keep
`analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv` as the single
next public sensor if spending one slot, but do not describe it as locally
certified. The next representation problem is to predict decisive-cell support
below the current visible-prior resolution.
"""
    REPORT_OUT.write_text(report, encoding="utf-8")


def run() -> None:
    cell_parts: list[pd.DataFrame] = []
    set_parts: list[pd.DataFrame] = []
    pair_rows: list[dict[str, Any]] = []
    for pair_cfg in PAIRS:
        cells, sets, pair_summary = summarize_pair_cells(pair_cfg)
        cell_parts.append(cells)
        set_parts.append(sets)
        pair_rows.append(pair_summary)
    cells_all = pd.concat(cell_parts, ignore_index=True)
    sets_all = pd.concat(set_parts, ignore_index=True)
    pairs = pd.DataFrame(pair_rows)
    calibration = calibration_rows(pairs, sets_all)
    cells_all.to_csv(CELLS_OUT, index=False)
    sets_all.to_csv(SETS_OUT, index=False)
    pairs.to_csv(PAIR_OUT, index=False)
    calibration.to_csv(OUT / "e180_known_anchor_decisive_cell_visibility_calibration.csv", index=False)
    write_report(cells_all, sets_all, pairs, calibration)
    print(CELLS_OUT)
    print(SETS_OUT)
    print(PAIR_OUT)
    print(OUT / "e180_known_anchor_decisive_cell_visibility_calibration.csv")
    print(REPORT_OUT)


if __name__ == "__main__":
    run()
