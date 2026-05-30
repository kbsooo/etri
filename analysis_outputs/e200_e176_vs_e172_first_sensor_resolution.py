#!/usr/bin/env python3
"""Resolve whether E172 should replace E176 as the first public sensor.

E199 made E172 look slightly cleaner than E176 on direct clean-shape E72
exposure. This script asks the narrower decision question: does that safety
advantage justify spending the first public slot on E172 instead of E176?
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


OUT = Path(__file__).resolve().parent
E95_PUBLIC = 0.5762913298
MIXMIN_PUBLIC = 0.5763066405
E95_EDGE_VS_MIXMIN = MIXMIN_PUBLIC - E95_PUBLIC


def read_csv(name: str) -> pd.DataFrame:
    path = OUT / name
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def fmt(value: object) -> str:
    if value is None:
        return "NA"
    if isinstance(value, float) and np.isnan(value):
        return "NA"
    if isinstance(value, (float, np.floating)):
        return f"{value:.9g}"
    if isinstance(value, (int, np.integer)):
        return str(int(value))
    return str(value)


def markdown_table(df: pd.DataFrame) -> str:
    safe = df.copy()
    for col in safe.columns:
        safe[col] = safe[col].map(fmt).str.replace("|", "\\|", regex=False)
    header = "| " + " | ".join(safe.columns) + " |"
    sep = "| " + " | ".join(["---"] * len(safe.columns)) + " |"
    rows = ["| " + " | ".join(row.astype(str).tolist()) + " |" for _, row in safe.iterrows()]
    return "\n".join([header, sep, *rows])


def pair_row(pairwise: pd.DataFrame, new: str, base: str) -> pd.Series:
    row = pairwise.loc[pairwise["new"].eq(new) & pairwise["base"].eq(base)]
    if row.empty:
        raise KeyError(f"missing pair row: {new} vs {base}")
    return row.iloc[0]


def candidate_row(df: pd.DataFrame, candidate: str) -> pd.Series:
    row = df.loc[df["candidate"].eq(candidate)]
    if row.empty:
        raise KeyError(f"missing candidate row: {candidate}")
    return row.iloc[0]


def build_candidate_comparison() -> pd.DataFrame:
    pairwise = read_csv("e177_e176_public_feedback_decoder_pairwise.csv")
    support = read_csv("e197_public_support_mass_candidate_profiles.csv")
    shape = read_csv("e199_candidate_shape_e72_exposure_summary.csv")

    e176_vs_e95 = pair_row(pairwise, "e176_q2_underopen", "e95")
    e176_vs_e172 = pair_row(pairwise, "e176_q2_underopen", "e172_tail_repair")
    e176_vs_e174 = pair_row(pairwise, "e176_q2_underopen", "e174_full_q2")

    e176_delta = float(e176_vs_e95["expected_delta_focus_mean"])
    e176_minus_e172 = float(e176_vs_e172["expected_delta_focus_mean"])
    e176_minus_e174 = float(e176_vs_e174["expected_delta_focus_mean"])
    e172_delta = e176_delta - e176_minus_e172
    e174_delta = e176_delta - e176_minus_e174

    deltas = {"e172": e172_delta, "e176": e176_delta, "e174": e174_delta}
    roles = {
        "e172": "same_family_safety_after_tie_or_small_loss",
        "e176": "first_sensor_broad_q2_underopen",
        "e174": "full_q2_reopen_max_edge_contrast",
    }

    rows = []
    for cand in ["e172", "e176", "e174"]:
        sup = candidate_row(support, cand)
        shp = candidate_row(shape, cand)
        rows.append(
            {
                "candidate": cand,
                "file": sup["file"],
                "role": roles[cand],
                "focus_expected_delta_vs_e95": deltas[cand],
                "edge_fraction_of_e95_mixmin": abs(deltas[cand]) / E95_EDGE_VS_MIXMIN,
                "surplus_to_tie_visible": float(sup["surplus_to_tie_visible_mean"]),
                "surplus_to_tie_focus": float(sup["surplus_to_tie_focus_mean"]),
                "direct_shape_e72_prob": float(shp["direct_shape_e72_prob"]),
                "direct_shape_e72_band": shp["direct_shape_e72_band"],
                "visible_e72_vs_e95_outcome": shp["visible_outcome_e72_vs_e95"],
                "visible_e72_vs_mixmin_outcome": shp["visible_outcome_e72_vs_mixmin"],
                "focus_e72_vs_e95_outcome": shp["focus_outcome_e72_vs_e95"],
                "focus_e72_vs_mixmin_outcome": shp["focus_outcome_e72_vs_mixmin"],
            }
        )
    return pd.DataFrame(rows)


def build_decision_metrics() -> pd.DataFrame:
    pairwise = read_csv("e177_e176_public_feedback_decoder_pairwise.csv")
    support = read_csv("e197_public_support_mass_candidate_profiles.csv")
    shape = read_csv("e199_candidate_shape_e72_exposure_summary.csv")

    e176_vs_e172 = pair_row(pairwise, "e176_q2_underopen", "e172_tail_repair")
    e176_vs_e154 = pair_row(pairwise, "e176_q2_underopen", "e154")
    e176_vs_e95 = pair_row(pairwise, "e176_q2_underopen", "e95")

    e172_support = candidate_row(support, "e172")
    e176_support = candidate_row(support, "e176")
    e172_shape = candidate_row(shape, "e172")
    e176_shape = candidate_row(shape, "e176")

    e176_edge_over_e172 = -float(e176_vs_e172["expected_delta_focus_mean"])
    e172_visible_surplus_adv = (
        float(e172_support["surplus_to_tie_visible_mean"])
        - float(e176_support["surplus_to_tie_visible_mean"])
    )
    e172_focus_surplus_adv = (
        float(e172_support["surplus_to_tie_focus_mean"]) - float(e176_support["surplus_to_tie_focus_mean"])
    )
    e172_shape_adv = float(e176_shape["direct_shape_e72_prob"]) - float(e172_shape["direct_shape_e72_prob"])

    same_family_delta_abs = abs(float(e176_vs_e172["expected_delta_focus_mean"]))
    counterworld_delta_abs = abs(float(e176_vs_e154["expected_delta_focus_mean"]))

    metrics = [
        {
            "metric": "e176_expected_edge_over_e172",
            "value": e176_edge_over_e172,
            "scale": "logloss",
            "read": "E176 is lower than E172 by this focus-prior expected amount.",
        },
        {
            "metric": "e176_edge_as_fraction_of_e95_mixmin_edge",
            "value": e176_edge_over_e172 / E95_EDGE_VS_MIXMIN,
            "scale": "ratio",
            "read": "Choosing E172 first gives up about this fraction of the current E95-over-mixmin public edge.",
        },
        {
            "metric": "e172_visible_surplus_advantage",
            "value": e172_visible_surplus_adv,
            "scale": "support_mass",
            "read": "E172 is safer than E176 under the visible support-mass lens by this amount.",
        },
        {
            "metric": "e172_focus_surplus_advantage",
            "value": e172_focus_surplus_adv,
            "scale": "support_mass",
            "read": "E172 is safer than E176 under the focus support-mass lens by this amount.",
        },
        {
            "metric": "e172_clean_shape_e72_advantage",
            "value": e172_shape_adv,
            "scale": "probability",
            "read": "E172 has this tiny lower clean-shape E72 probability; both are far below non-E72 p95.",
        },
        {
            "metric": "same_family_contrast_cells",
            "value": int(e176_vs_e172["moved_cells"]),
            "scale": "cells",
            "read": "E176-vs-E172 is a narrow rollback contrast.",
        },
        {
            "metric": "counterworld_contrast_cells",
            "value": int(e176_vs_e154["moved_cells"]),
            "scale": "cells",
            "read": "E176-vs-E154 is the broad counter-world contrast.",
        },
        {
            "metric": "same_family_to_counterworld_delta_ratio",
            "value": same_family_delta_abs / counterworld_delta_abs,
            "scale": "ratio",
            "read": "E172-first mostly tests a narrow same-family safety rollback, not the broad world conflict.",
        },
        {
            "metric": "e176_cells_for_e95_edge",
            "value": int(e176_vs_e95["cells_for_e95_edge"]),
            "scale": "cells",
            "read": "E176 is still hard-label fragile at public-edge scale.",
        },
        {
            "metric": "e176_vs_e172_cells_for_e95_edge",
            "value": int(e176_vs_e172["cells_for_e95_edge"]),
            "scale": "cells",
            "read": "The E176/E172 difference is public-readable but very thin.",
        },
    ]
    return pd.DataFrame(metrics)


def build_policy_table() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "choice": "E176 first",
                "worldview_bet": "pair/shape/broad-body plus Q2-underopen is public-real and not E72-shaped",
                "what_it_resolves": "validates or demotes the current broad Q2-underopen worldview",
                "main_downside": "slightly lower support-mass surplus than E172; E72-like slippage can small/branch-lose",
                "followup_if_good": "promote E176; decompose non-Q2/S3/S2/S1 responsibility",
                "followup_if_bad": "route by E177: E172 after tie/small-loss, E154/search after branch/hard-loss",
                "decision": "keep_first",
            },
            {
                "choice": "E172 first",
                "worldview_bet": "same-family visible-tail safety matters more than the extra E176 edge",
                "what_it_resolves": "tests safer tail-repair rollback but leaves E176 Q2-underopen mostly unobserved",
                "main_downside": "gives up most of the E176-over-E172 edge and asks a lower-information question first",
                "followup_if_good": "E176 still remains untested unless a second slot is spent",
                "followup_if_bad": "broad family becomes suspicious, but E176 can still be the better unresolved branch",
                "decision": "conditional_after_e176_tie_or_small_loss",
            },
        ]
    )


def write_report(
    comparison: pd.DataFrame, metrics: pd.DataFrame, policy: pd.DataFrame
) -> Path:
    metric = metrics.set_index("metric")["value"]
    e176_edge = float(metric["e176_expected_edge_over_e172"])
    edge_frac = float(metric["e176_edge_as_fraction_of_e95_mixmin_edge"])
    visible_adv = float(metric["e172_visible_surplus_advantage"])
    focus_adv = float(metric["e172_focus_surplus_advantage"])
    shape_adv = float(metric["e172_clean_shape_e72_advantage"])
    same_ratio = float(metric["same_family_to_counterworld_delta_ratio"])

    path = OUT / "e200_e176_vs_e172_first_sensor_resolution_report.md"
    body = f"""# E200 E176 vs E172 First-Sensor Resolution

## Question

E199 made E172 slightly cleaner than E176 on direct clean-shape E72 exposure. Should E172 replace E176 as the next public file, or should it stay a conditional fallback after E176 feedback?

## Result

E172 should not replace E176 as the first sensor.

The safety gain is real but too small and too narrow for the first slot. E172 has higher visible/focus support surplus by `{visible_adv:.9g}` / `{focus_adv:.9g}` and a slightly lower clean-shape E72 probability by `{shape_adv:.9g}`. But choosing E172 first gives up E176's expected focus edge of `{e176_edge:.9g}`, which is `{edge_frac:.3f}x` of the entire E95-over-mixmin public edge. It also converts the first public question from the broad E176-vs-E154 worldview conflict into a narrow E176-vs-E172 rollback contrast.

Recommended first sensor remains:

`analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`

E172 remains the correct same-family safety follow-up if E176 lands in the E177 tie/small-loss bands.

## Candidate Comparison

{markdown_table(comparison)}

## Decision Metrics

{markdown_table(metrics)}

## Policy Table

{markdown_table(policy)}

## Interpretation

- E172's safety advantage is not imaginary. It is cleaner under support-mass and clean-shape E72 diagnostics.
- The advantage is not first-slot decisive. The clean-shape difference is tiny in absolute probability, and both E172/E176 are far below the non-E72 p95 threshold from E199.
- E176-vs-E172 moves only `75` cells, and its focus expected delta is only `{same_ratio:.3f}x` of the E176-vs-E154 counter-world contrast. That makes E172 a follow-up contrast, not the main worldview test.
- E172-first is coherent only if the chosen objective is private-risk minimization or same-family safety before information. The current goal is public-sensor information and frontier challenge, so E176 stays first.

## Decision

No new submission is created. Keep the conditional order:

1. E176 first.
2. If E176 ties or small-loses, E172 is the same-family safety contrast.
3. If E176 branch-loses or hard-fails, E154 is the repaired-branch counter-world.
"""
    path.write_text(body)
    return path


def main() -> None:
    comparison = build_candidate_comparison()
    metrics = build_decision_metrics()
    policy = build_policy_table()

    comparison.to_csv(OUT / "e200_e176_vs_e172_first_sensor_comparison.csv", index=False)
    metrics.to_csv(OUT / "e200_e176_vs_e172_first_sensor_metrics.csv", index=False)
    policy.to_csv(OUT / "e200_e176_vs_e172_first_sensor_policy.csv", index=False)
    report = write_report(comparison, metrics, policy)
    print(f"Wrote {report}")


if __name__ == "__main__":
    main()
