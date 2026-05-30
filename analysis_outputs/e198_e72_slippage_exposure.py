#!/usr/bin/env python3
"""E198: separate algebraic E72 slippage risk from E72 shape exposure.

E197 showed that E176 survives ordinary public-slippage analogues and loses
only when the hidden public labels behave like the E72 failures. E191/E192
separately found a boundary-clean shape-only E72 detector and showed that live
E176 branches score almost zero on that detector.

This script joins those two views. The question is deliberately narrow:

    "If E176 loses only under E72-like adverse slippage, do its moved cells also
    look structurally E72-like under the clean shape diagnostic?"

No submission is created. The output is a risk/explanation table for the next
public sensor decision.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

PROFILE_IN = OUT / "e197_public_support_mass_candidate_profiles.csv"
STRESS_IN = OUT / "e197_public_support_mass_slippage_stress.csv"
KNOWN_PAIR_IN = OUT / "e197_public_support_mass_known_pairs.csv"
BRANCH_SHAPE_IN = OUT / "e192_shape_e72_score_anatomy_branch_audit.csv"
E191_SUMMARY_IN = OUT / "e191_boundary_aware_e72_score_summary.csv"

SUMMARY_OUT = OUT / "e198_e72_slippage_exposure_summary.csv"
BRANCH_JOIN_OUT = OUT / "e198_e72_slippage_exposure_branch_join.csv"
REPORT_OUT = OUT / "e198_e72_slippage_exposure_report.md"


def fmt(x: Any) -> str:
    if x is None:
        return "NA"
    if isinstance(x, str):
        return x
    try:
        if pd.isna(x):
            return "NA"
    except TypeError:
        pass
    if isinstance(x, (float, np.floating)):
        return f"{float(x):.9g}"
    return str(x)


def markdown_table(frame: pd.DataFrame, n: int = 40) -> str:
    if frame.empty:
        return "_empty_"
    view = frame.head(n).copy()
    for col in view.columns:
        view[col] = view[col].map(fmt).astype(str).str.replace("|", "\\|", regex=False)
    header = "| " + " | ".join(view.columns) + " |"
    sep = "| " + " | ".join(["---"] * len(view.columns)) + " |"
    rows = ["| " + " | ".join(row.astype(str).tolist()) + " |" for _, row in view.iterrows()]
    return "\n".join([header, sep, *rows])


def required(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(path)


def e72_detector_health(summary: pd.DataFrame) -> pd.Series:
    rows = summary[
        summary["feature_view"].eq("shape_target_context_abs")
        & summary["score_spec"].eq("plain_logit_c025")
        & summary["split"].eq("loo_pair_id")
        & summary["boundary_clean_gate"].astype(bool)
    ]
    if rows.empty:
        raise RuntimeError("missing boundary-clean E191 detector row")
    return rows.iloc[0]


def shape_band(prob: float, p95: float, p99: float, positive_floor: float) -> str:
    if not np.isfinite(prob):
        return "not_scored"
    if prob >= positive_floor:
        return "known_positive_scale"
    if prob >= p99:
        return "non_e72_p99_tail"
    if prob >= p95:
        return "non_e72_p95_tail"
    return "below_non_e72_p95"


def combined_verdict(row: pd.Series) -> str:
    candidate = str(row["candidate"])
    shape = str(row["shape_e72_band"])
    visible_e72_loss = bool(row["visible_e72_like_causes_loss"])
    focus_e72_loss = bool(row["focus_e72_like_causes_loss"])
    thin = bool(row["thin_visible_margin"])

    if shape == "not_scored":
        return "needs_shape_score_if_prioritized"
    if shape == "known_positive_scale":
        return "e72_like_shape_supported"
    if candidate == "e176" and visible_e72_loss and shape == "below_non_e72_p95":
        return "failure_algebraic_not_shape_supported"
    if candidate == "e176" and focus_e72_loss and shape == "below_non_e72_p95":
        return "focus_failure_algebraic_not_shape_supported"
    if thin and shape.endswith("tail"):
        return "thin_margin_plus_shape_tail_alarm"
    if thin:
        return "thin_margin_not_e72_shape"
    if shape.endswith("tail"):
        return "shape_tail_alarm_without_positive_scale"
    return "not_e72_shape_exposed"


def main() -> None:
    for path in [PROFILE_IN, STRESS_IN, KNOWN_PAIR_IN, BRANCH_SHAPE_IN, E191_SUMMARY_IN]:
        required(path)

    profiles = pd.read_csv(PROFILE_IN)
    stress = pd.read_csv(STRESS_IN)
    known = pd.read_csv(KNOWN_PAIR_IN)
    branch_shape = pd.read_csv(BRANCH_SHAPE_IN)
    e191 = pd.read_csv(E191_SUMMARY_IN)

    detector = e72_detector_health(e191)

    thresholds = branch_shape[
        ["known_non_e72_p95", "known_non_e72_p99", "known_min_positive", "known_mean_positive"]
    ].iloc[0]
    p95 = float(thresholds["known_non_e72_p95"])
    p99 = float(thresholds["known_non_e72_p99"])
    positive_floor = float(thresholds["known_min_positive"])

    branch_agg = (
        branch_shape.groupby("candidate", as_index=False)
        .agg(
            shape_e72_prob_max=("shape_e72_prob", "max"),
            shape_e72_prob_mean=("shape_e72_prob", "mean"),
            shape_e72_prob_min=("shape_e72_prob", "min"),
            shape_scenarios=("scenario", "nunique"),
            scenarios_above_non_e72_p95=("above_non_e72_p95", "sum"),
            scenarios_above_non_e72_p99=("above_non_e72_p99", "sum"),
            scenarios_above_positive_floor=("above_min_positive", "sum"),
        )
        .sort_values("candidate")
    )
    for col in [
        "shape_e72_prob_max",
        "shape_e72_prob_mean",
        "shape_e72_prob_min",
        "scenarios_above_non_e72_p95",
        "scenarios_above_non_e72_p99",
        "scenarios_above_positive_floor",
    ]:
        branch_agg[col] = branch_agg[col].astype(float)

    e72_slippage = known[known["pair"].isin(["e72_vs_e95", "e72_vs_mixmin"])].copy()
    e72_slippage = e72_slippage[
        [
            "pair",
            "actual_delta",
            "q_tie",
            "q_observed",
            "q_visible_mean",
            "slippage_vs_visible_mean",
            "q_focus_mean",
            "slippage_vs_focus_mean",
        ]
    ]

    stress_e72 = stress[stress["analogue_pair"].isin(["e72_vs_e95", "e72_vs_mixmin"])].copy()
    stress_e72["causes_loss"] = ~stress_e72["beats_e95"].astype(bool)
    stress_pivot = stress_e72.pivot_table(
        index=["candidate", "prior"],
        columns="analogue_pair",
        values=["delta_vs_e95", "outcome", "causes_loss", "q_after_slippage"],
        aggfunc="first",
    )
    stress_pivot.columns = [f"{metric}_{pair}" for metric, pair in stress_pivot.columns]
    stress_pivot = stress_pivot.reset_index()
    visible = stress_pivot[stress_pivot["prior"].eq("visible_mean")].drop(columns=["prior"])
    focus = stress_pivot[stress_pivot["prior"].eq("focus_mean")].drop(columns=["prior"])
    visible = visible.rename(columns={c: f"visible_{c}" for c in visible.columns if c != "candidate"})
    focus = focus.rename(columns={c: f"focus_{c}" for c in focus.columns if c != "candidate"})

    summary = profiles[
        [
            "candidate",
            "world",
            "n_cells",
            "n_rows",
            "targets",
            "swing_sum",
            "q_tie",
            "q_visible_mean",
            "surplus_to_tie_visible_mean",
            "q_focus_mean",
            "surplus_to_tie_focus_mean",
            "pred_delta_visible_mean",
            "pred_delta_focus_mean",
        ]
    ].copy()
    summary = summary.merge(visible, on="candidate", how="left").merge(focus, on="candidate", how="left")
    summary = summary.merge(branch_agg, on="candidate", how="left")

    for col in [
        "shape_e72_prob_max",
        "shape_e72_prob_mean",
        "shape_e72_prob_min",
        "shape_scenarios",
        "scenarios_above_non_e72_p95",
        "scenarios_above_non_e72_p99",
        "scenarios_above_positive_floor",
    ]:
        if col in summary:
            summary[col] = summary[col].fillna(np.nan)

    summary["known_non_e72_p95"] = p95
    summary["known_non_e72_p99"] = p99
    summary["known_positive_floor"] = positive_floor
    summary["shape_e72_band"] = summary["shape_e72_prob_max"].map(
        lambda v: shape_band(float(v), p95, p99, positive_floor) if pd.notna(v) else "not_scored"
    )

    summary["visible_e72_like_causes_loss"] = summary[
        "visible_causes_loss_e72_vs_e95"
    ].fillna(False).astype(bool) | summary["visible_causes_loss_e72_vs_mixmin"].fillna(False).astype(bool)
    summary["focus_e72_like_causes_loss"] = summary[
        "focus_causes_loss_e72_vs_e95"
    ].fillna(False).astype(bool) | summary["focus_causes_loss_e72_vs_mixmin"].fillna(False).astype(bool)
    summary["thin_visible_margin"] = summary["surplus_to_tie_visible_mean"].le(0.02)
    summary["e72_slippage_needed_visible"] = -summary["surplus_to_tie_visible_mean"]
    summary["e72_slippage_needed_focus"] = -summary["surplus_to_tie_focus_mean"]
    summary["verdict"] = summary.apply(combined_verdict, axis=1)

    order = {
        "failure_algebraic_not_shape_supported": 0,
        "focus_failure_algebraic_not_shape_supported": 1,
        "thin_margin_plus_shape_tail_alarm": 2,
        "thin_margin_not_e72_shape": 3,
        "shape_tail_alarm_without_positive_scale": 4,
        "not_e72_shape_exposed": 5,
        "needs_shape_score_if_prioritized": 6,
        "e72_like_shape_supported": 7,
    }
    summary["verdict_order"] = summary["verdict"].map(order).fillna(99).astype(int)
    summary = summary.sort_values(["verdict_order", "candidate"]).reset_index(drop=True)

    branch_join = branch_shape.merge(
        profiles[["candidate", "world", "surplus_to_tie_visible_mean", "surplus_to_tie_focus_mean"]],
        on="candidate",
        how="left",
    )
    branch_join["shape_e72_band"] = branch_join["shape_e72_prob"].map(
        lambda v: shape_band(float(v), p95, p99, positive_floor)
    )

    summary.drop(columns=["verdict_order"]).to_csv(SUMMARY_OUT, index=False)
    branch_join.to_csv(BRANCH_JOIN_OUT, index=False)

    report_cols = [
        "candidate",
        "world",
        "surplus_to_tie_visible_mean",
        "surplus_to_tie_focus_mean",
        "visible_outcome_e72_vs_e95",
        "visible_outcome_e72_vs_mixmin",
        "focus_outcome_e72_vs_e95",
        "focus_outcome_e72_vs_mixmin",
        "shape_e72_prob_max",
        "shape_e72_band",
        "scenarios_above_non_e72_p95",
        "verdict",
    ]
    report = [
        "# E198 E72 Slippage Exposure",
        "",
        "## Question",
        "",
        "E197 says E176 only loses under E72-like adverse public slippage. Does E176 also look",
        "E72-like under the boundary-clean E191/E192 shape diagnostic, or is that failure only",
        "an algebraic stress case?",
        "",
        "## Detector Health",
        "",
        (
            "- Boundary-clean detector: `shape_target_context_abs / plain_logit_c025 / loo_pair_id` "
            f"with AUC `{fmt(detector['auc'])}`, AP `{fmt(detector['avg_precision'])}`, "
            f"top-k recall `{fmt(detector['topk_recall'])}`, exact E95/E101 mean probability "
            f"`{fmt(detector['exact_e95_e101_mean_prob'])}`."
        ),
        (
            f"- Branch anatomy thresholds: non-E72 p95 `{fmt(p95)}`, non-E72 p99 `{fmt(p99)}`, "
            f"known positive floor `{fmt(positive_floor)}`."
        ),
        "",
        "## Known E72 Slippage",
        "",
        markdown_table(e72_slippage),
        "",
        "## Candidate Join",
        "",
        markdown_table(summary[report_cols]),
        "",
        "## Interpretation",
        "",
        "- E176 still has an E72-like algebraic failure mode: visible-prior stress loses under both E72 analogues, and focus-prior stress loses under the harsher E72-vs-mixmin analogue.",
        "- But E176's maximum clean shape E72 probability is far below the non-E72 p95 and far below the known-positive floor. That means the E72 failure mode is not structurally supported by the only boundary-clean E72 detector we have.",
        "- E154 remains a thin-margin repaired-branch counterworld rather than an E72-contaminated branch. It fails easily because its support-mass surplus is small, not because the clean E72 shape detector lights up.",
        "- E144 is the only scored branch with a mild non-E72-p95 tail alarm, but it still sits below p99 and nowhere near positive scale; this is tail-risk anatomy, not E72 certification.",
        "- Candidates not scored by E192 should not be promoted solely from E197. If one of them becomes next, it needs a direct shape-anatomy score first.",
        "",
        "## Decision",
        "",
        "No new submission is created. E198 strengthens the current read: keep E176 as the next public sensor, but if it fails, interpret the failure by the pre-registered LB band rather than by claiming E176 was structurally E72-like before feedback.",
        "",
    ]
    REPORT_OUT.write_text("\n".join(report), encoding="utf-8")

    print(f"Wrote {SUMMARY_OUT}")
    print(f"Wrote {BRANCH_JOIN_OUT}")
    print(f"Wrote {REPORT_OUT}")
    print(summary[report_cols].to_string(index=False))


if __name__ == "__main__":
    main()
