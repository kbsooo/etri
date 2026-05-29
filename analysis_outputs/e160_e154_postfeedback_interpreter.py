#!/usr/bin/env python3
"""E160: post-feedback interpreter for E154 public LB.

E158 maps a future E154 public score to score bands. E159 maps those bands to
target/component responsibility. This script combines them into one executable
decision table so a future public score cannot be interpreted from the scalar
band alone.

It creates no submission. With --score, it writes the observed decision row for
`submission_e154_s3repair_9f2e2e73.csv`.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

E95_PUBLIC = 0.5762913298
E101_PUBLIC = 0.5763003660
MIXMIN_PUBLIC = 0.5763066405

E154_SUBMISSION = "submission_e154_s3repair_9f2e2e73.csv"
E155_SUBMISSION = "submission_e155_bodytemp_d27e7965.csv"
E157_SUBMISSION = "submission_e157_lowbodypareto_bd67930d.csv"
E156_SUBMISSION = "submission_e156_targetaxis_757546d2.csv"
E144_SUBMISSION = "submission_e144_activeboundary_d7b4b331.csv"

BANDS_IN = OUT / "e158_repaired_branch_public_decoder_bands.csv"
E158_CANDIDATES_IN = OUT / "e158_repaired_branch_public_decoder_candidates.csv"
E158_PAIRWISE_IN = OUT / "e158_repaired_branch_public_decoder_pairwise.csv"
E159_RATES_IN = OUT / "e159_e154_public_outcome_attribution_rates.csv"
E159_GROUP_IN = OUT / "e159_e154_public_outcome_group_attribution.csv"
E159_TOP_IN = OUT / "e159_e154_public_outcome_top_responsibility.csv"

SUMMARY_OUT = OUT / "e160_e154_postfeedback_interpreter_summary.csv"
REPORT_OUT = OUT / "e160_e154_postfeedback_interpreter_report.md"
OBSERVED_OUT = OUT / "e160_e154_observed_score_decision.csv"

FOCUS_PRIORS = ["global", "subject", "nearest_hard085"]
FOCUS_GROUP_KINDS = ["target", "component"]
WIN_OUTCOMES = {"breakthrough_win", "clean_win", "micro_win"}
ADDED_COMPONENTS = {"e154_adjustment_on_e144_body", "e154_extra_body"}


OVERRIDES: dict[str, dict[str, str]] = {
    "breakthrough_win": {
        "branch_status": "validated_large",
        "allowed_next": "Promote E154 as a new public anchor and rerun exact-delta audits before spending any slot on sibling controls.",
        "candidate_to_test": "",
        "forbidden": f"Do not immediately submit {E155_SUBMISSION}, {E157_SUBMISSION}, or {E156_SUBMISSION}; a large win changes the anchor geometry first.",
        "belief_update": "The repaired all-four branch is public-real at larger than frontier micro scale.",
    },
    "clean_win": {
        "branch_status": "validated_readable",
        "allowed_next": "Promote E154. Use E155 only as a private-risk amplitude audit, not as the next automatic public file.",
        "candidate_to_test": "",
        "forbidden": "Do not target-axis tune before rebuilding the branch with E154 as an anchor.",
        "belief_update": "E95 plus repaired S3 active-boundary residual movement transfers at readable scale.",
    },
    "micro_win": {
        "branch_status": "validated_micro",
        "allowed_next": "Promote E154 cautiously; next local work should seek a non-collinear representation rather than sibling micro-controls.",
        "candidate_to_test": "",
        "forbidden": "Do not call this evidence for a broad 0.54 path; it remains calibration-scale.",
        "belief_update": "The repaired branch is alive but still constrained by frontier-scale public resolution.",
    },
    "tie": {
        "branch_status": "ambiguous",
        "allowed_next": "Keep E95 as practical frontier. E155 is allowed only as an information-only amplitude contrast if attribution blames E154-added body.",
        "candidate_to_test": f"conditional:{E155_SUBMISSION}",
        "forbidden": f"Do not submit {E157_SUBMISSION} or {E156_SUBMISSION}; their deltas versus E155 are below public-readable scale.",
        "belief_update": "E154 did not resolve whether repaired body is public-positive.",
    },
    "small_loss": {
        "branch_status": "conditional_alive",
        "allowed_next": "Use component attribution first. E155 is the clean follow-up only if added-body overextension is the culprit; otherwise use E144 as unrepaired contrast or pause.",
        "candidate_to_test": f"conditional:{E155_SUBMISSION}",
        "forbidden": "Do not treat small loss as automatic lower-amplitude rescue; E159 often assigns loss to inherited E144 body.",
        "belief_update": "The branch lost but not worse than the E101 negative sensor. The culprit matters more than the scalar band.",
    },
    "branch_loss": {
        "branch_status": "weak_rejected",
        "allowed_next": "Default to no same-family rescue. Use E144 only as an explicit unrepaired-branch contrast if that question is worth a public slot.",
        "candidate_to_test": f"information_only:{E144_SUBMISSION}",
        "forbidden": f"Do not rescue with {E157_SUBMISSION} or {E156_SUBMISSION}; do not use E155 unless added-body blame is unexpectedly dominant.",
        "belief_update": "The repaired branch is weaker than the resolved E101 negative sensor and close to losing the E95 gain.",
    },
    "hard_fail": {
        "branch_status": "rejected",
        "allowed_next": "Close repaired-branch siblings and return to representation search or, at most, use E144 as a final information-only branch contrast.",
        "candidate_to_test": "",
        "forbidden": f"Do not submit {E155_SUBMISSION}, {E157_SUBMISSION}, or {E156_SUBMISSION}.",
        "belief_update": "The repaired branch gave back the E95 gain; nearby controls are suspect.",
    },
}


def md_table(frame: pd.DataFrame, floatfmt: str = ".6f") -> str:
    if frame.empty:
        return "_empty_"
    lines = [
        "| " + " | ".join(str(c) for c in frame.columns) + " |",
        "| " + " | ".join(["---"] * len(frame.columns)) + " |",
    ]
    for rec in frame.to_dict("records"):
        vals: list[str] = []
        for col in frame.columns:
            value = rec[col]
            if pd.isna(value):
                vals.append("")
            elif isinstance(value, (float, np.floating)):
                if np.isposinf(value):
                    vals.append("inf")
                elif np.isneginf(value):
                    vals.append("-inf")
                else:
                    vals.append(format(float(value), floatfmt))
            else:
                vals.append(str(value))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def collapse_top_groups(top: pd.DataFrame, outcome: str) -> str:
    focus = top[
        top["prior"].isin(FOCUS_PRIORS)
        & top["outcome"].eq(outcome)
        & top["group_kind"].isin(FOCUS_GROUP_KINDS)
    ].copy()
    if focus.empty:
        return ""
    parts: list[str] = []
    for prior in FOCUS_PRIORS:
        one = focus[focus["prior"].eq(prior)].sort_values("rank").head(5)
        if one.empty:
            continue
        groups = [f"{rec['group_kind']}={rec['group']}" for rec in one.to_dict("records")]
        parts.append(f"{prior}: " + ", ".join(groups))
    return " | ".join(parts)


def component_read(group: pd.DataFrame, outcome: str) -> dict[str, Any]:
    focus = group[
        group["prior"].isin(FOCUS_PRIORS)
        & group["outcome"].eq(outcome)
        & group["group_kind"].eq("component")
    ].copy()
    is_win = outcome in WIN_OUTCOMES
    top_components: dict[str, str] = {}
    top_deltas: dict[str, float] = {}
    for prior in FOCUS_PRIORS:
        one = focus[focus["prior"].eq(prior)].copy()
        if one.empty:
            top_components[prior] = ""
            top_deltas[prior] = np.nan
            continue
        one = one.sort_values("conditional_delta_per_all", ascending=is_win)
        row = one.iloc[0]
        top_components[prior] = str(row["group"])
        top_deltas[prior] = float(row["conditional_delta_per_all"])
    inherited_top = sum(1 for value in top_components.values() if value == "inherited_e144_body")
    added_top = sum(1 for value in top_components.values() if value in ADDED_COMPONENTS)

    if outcome in WIN_OUTCOMES:
        e155_gate = "not_needed"
        e155_reason = "A win promotes E154; sibling controls should wait for exact-delta rebuild."
    elif outcome in {"tie", "small_loss"} and added_top >= 2 and inherited_top == 0:
        e155_gate = "allowed"
        e155_reason = "Added E154 body is the dominant component read across focus priors."
    elif outcome in {"tie", "small_loss"} and added_top >= 1:
        e155_gate = "information_only"
        e155_reason = "At least one focus prior points to added-body blame, but the read is not dominant."
    elif outcome in {"branch_loss"} and added_top >= 2:
        e155_gate = "information_only"
        e155_reason = "Added-body blame is unusually strong even in branch-loss; use E155 only as an overextension test."
    else:
        e155_gate = "not_recommended"
        e155_reason = "Loss/tie responsibility is not mainly E154-added body; lower-amplitude E155 cannot address inherited-body failure."

    return {
        "component_top_global": top_components.get("global", ""),
        "component_top_subject": top_components.get("subject", ""),
        "component_top_nearest_hard085": top_components.get("nearest_hard085", ""),
        "component_top_delta_global": top_deltas.get("global", np.nan),
        "component_top_delta_subject": top_deltas.get("subject", np.nan),
        "component_top_delta_nearest_hard085": top_deltas.get("nearest_hard085", np.nan),
        "component_inherited_top_count": inherited_top,
        "component_added_top_count": added_top,
        "e155_gate": e155_gate,
        "e155_gate_reason": e155_reason,
    }


def rate_summary(rates: pd.DataFrame, outcome: str) -> dict[str, float]:
    out: dict[str, float] = {}
    focus = rates[rates["outcome"].eq(outcome)]
    for prior in FOCUS_PRIORS:
        one = focus[focus["prior"].eq(prior)]
        if one.empty:
            out[f"{prior}_world_rate"] = np.nan
            out[f"{prior}_mean_delta"] = np.nan
            out[f"{prior}_support_flip_share"] = np.nan
        else:
            row = one.iloc[0]
            out[f"{prior}_world_rate"] = float(row["world_rate"])
            out[f"{prior}_mean_delta"] = float(row["mean_delta_vs_e95"])
            out[f"{prior}_support_flip_share"] = float(row["support_flip_share_mean"])
    return out


def load_geometry() -> dict[str, float]:
    candidates = pd.read_csv(E158_CANDIDATES_IN).set_index("tag")
    pairwise = pd.read_csv(E158_PAIRWISE_IN)
    e154 = candidates.loc["e154"]
    pairs: dict[str, float] = {}
    for right in ["e155", "e157", "e156", "e144"]:
        row = pairwise[(pairwise["left"].eq("e154")) & (pairwise["right"].eq(right))].iloc[0]
        pairs[f"e154_minus_{right}_local_gap"] = float(row["local_all_minus_delta_left_minus_right"])
        pairs[f"e154_minus_{right}_local_readable"] = bool(row["local_delta_readable"])
    return {
        "e154_cos_vs_e144": float(e154["cos_vs_e144"]),
        "e154_q_share": float(e154["q_share"]),
        "e154_s_share": float(e154["s_share"]),
        "e154_changed_cells": float(e154["changed_cells_vs_e95_computed"]),
        "e154_changed_rows": float(e154["changed_rows_vs_e95_computed"]),
        **pairs,
    }


def build_interpreter() -> pd.DataFrame:
    bands = pd.read_csv(BANDS_IN)
    rates = pd.read_csv(E159_RATES_IN)
    group = pd.read_csv(E159_GROUP_IN)
    top = pd.read_csv(E159_TOP_IN)
    geom = load_geometry()

    rows: list[dict[str, Any]] = []
    for rec in bands.to_dict("records"):
        outcome = str(rec["outcome"])
        override = OVERRIDES[outcome]
        row: dict[str, Any] = {
            "outcome": outcome,
            "delta_lo_exclusive": rec["delta_lo_exclusive"],
            "delta_hi_inclusive": rec["delta_hi_inclusive"],
            "public_lb_lo_exclusive": rec["public_lb_lo_exclusive"],
            "public_lb_hi_inclusive": rec["public_lb_hi_inclusive"],
            "branch_status": override["branch_status"],
            "allowed_next": override["allowed_next"],
            "candidate_to_test": override["candidate_to_test"],
            "forbidden": override["forbidden"],
            "belief_update": override["belief_update"],
            "top_attribution_focus": collapse_top_groups(top, outcome),
            "geometry_read": (
                f"E154 is E144-branch geometry (cos_vs_e144={geom['e154_cos_vs_e144']:.9f}), "
                f"changes {int(geom['e154_changed_cells'])} cells over {int(geom['e154_changed_rows'])} rows, "
                f"and differs readably from E144 but not from E155 "
                f"(gap_e154_e144={geom['e154_minus_e144_local_gap']:.9f}, "
                f"gap_e154_e155={geom['e154_minus_e155_local_gap']:.9f})."
            ),
            "kill_claim": "E154 public score kills or validates the repaired all-four branch only after E159 component responsibility is read.",
        }
        row.update(rate_summary(rates, outcome))
        row.update(component_read(group, outcome))
        rows.append(row)
    return pd.DataFrame(rows)


def classify_score(summary: pd.DataFrame, score: float) -> pd.DataFrame:
    delta = float(score) - E95_PUBLIC
    mask = (
        (delta > summary["delta_lo_exclusive"].astype(float))
        & (delta <= summary["delta_hi_inclusive"].astype(float))
    )
    if int(mask.sum()) != 1:
        raise RuntimeError(f"Score {score} maps to {int(mask.sum())} E158 bands")
    decision = summary[mask].copy()
    decision.insert(0, "observed_public_lb", score)
    decision.insert(1, "observed_delta_vs_e95", delta)
    decision.insert(2, "observed_delta_vs_e101", score - E101_PUBLIC)
    decision.insert(3, "observed_delta_vs_mixmin", score - MIXMIN_PUBLIC)
    return decision


def write_report(summary: pd.DataFrame) -> None:
    compact_cols = [
        "outcome",
        "public_lb_lo_exclusive",
        "public_lb_hi_inclusive",
        "branch_status",
        "e155_gate",
        "candidate_to_test",
        "allowed_next",
    ]
    evidence_cols = [
        "outcome",
        "global_world_rate",
        "subject_world_rate",
        "nearest_hard085_world_rate",
        "component_top_global",
        "component_top_subject",
        "component_top_nearest_hard085",
        "e155_gate",
        "e155_gate_reason",
    ]
    guard_cols = ["outcome", "belief_update", "forbidden"]
    geom = load_geometry()

    report = f"""# E160 E154 Post-Feedback Interpreter

## Question

After E158 and E159, a future public LB for `{E154_SUBMISSION}` must update the
world model without turning into score-only leaderboard tuning. Which actions
are allowed for each possible score band?

## Strangest Point

E154 is the most informative next public sensor, but it is still almost the same
geometry as E144: cosine `{geom['e154_cos_vs_e144']:.9f}`. Its local edge over
E155 is only `{geom['e154_minus_e155_local_gap']:.9f}`, below the public-readable
guardrail, while its edge over E144 is `{geom['e154_minus_e144_local_gap']:.9f}`.
So E154 is first because it is readable against E144 and asks the full repaired
all-four question, not because its siblings are clearly worse.

## Current World Model

E95 found a real S-heavy hardtail law. E101 showed Q2/S3 rollback was close but
not frontier. E144/E154 try to add transfer-budget-neutral residual movement
without reviving E72/E101 negative axes. The repaired branch is live, but its
public feedback must be interpreted by component responsibility: inherited E144
body failure and E154 added-body overextension imply different next files.

## Decision Table

{md_table(summary[compact_cols], ".9f")}

## Attribution Evidence

{md_table(summary[evidence_cols], ".9f")}

## Guardrails

{md_table(summary[guard_cols], ".9f")}

## Usage

Run:

```bash
python3 analysis_outputs/e160_e154_postfeedback_interpreter.py --score <PUBLIC_LB>
```

The resulting row is written to `{OBSERVED_OUT.name}`.

## Decision

Keep `{E154_SUBMISSION}` as the next public sensor. If feedback is tie or
small-loss, `{E155_SUBMISSION}` is allowed only when this interpreter reports an
added-body blame read. If feedback is branch-loss or hard-fail with inherited
body blame, do not rescue with `{E155_SUBMISSION}`, `{E157_SUBMISSION}`, or
`{E156_SUBMISSION}`.
"""
    REPORT_OUT.write_text(report)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--score", type=float, default=None, help="Observed public LB for E154.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = build_interpreter()
    summary.to_csv(SUMMARY_OUT, index=False)
    write_report(summary)

    print({"summary": str(SUMMARY_OUT), "report": str(REPORT_OUT), "rows": len(summary)})
    print(
        summary[
            [
                "outcome",
                "branch_status",
                "e155_gate",
                "component_top_global",
                "component_top_subject",
                "component_top_nearest_hard085",
            ]
        ].to_string(index=False)
    )

    if args.score is not None:
        decision = classify_score(summary, float(args.score))
        decision.to_csv(OBSERVED_OUT, index=False)
        print({"observed_decision": str(OBSERVED_OUT)})
        cols = [
            "observed_public_lb",
            "observed_delta_vs_e95",
            "outcome",
            "branch_status",
            "e155_gate",
            "allowed_next",
            "forbidden",
        ]
        print(decision[cols].to_string(index=False))


if __name__ == "__main__":
    main()
