#!/usr/bin/env python3
"""E150: post-E149 interpreter for the pending E144 public feedback.

E145 pre-registered score bands for E144. E148 added target/component
attribution. E149 added anchor geometry and downgraded the framing from
"broad successor law" to "branch-pruned residual sensor".

This script combines those three guardrails into a single decision table. It
does not generate a submission. With --score, it classifies an observed public
LB into the pre-registered band and prints the allowed next action.
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

E144_SUBMISSION = "submission_e144_activeboundary_d7b4b331.csv"
E143_SUBMISSION = "submission_e143_activeq2s3repair_68ca656f.csv"
E142_SUBMISSION = "submission_e142_transferclip_09a92236.csv"

E145_IN = OUT / "e145_e144_public_feedback_decoder.csv"
E148_RATES_IN = OUT / "e148_e144_public_outcome_attribution_rates.csv"
E148_TOP_IN = OUT / "e148_e144_public_outcome_top_responsibility.csv"
E149_SUMMARY_IN = OUT / "e149_e144_anchor_geometry_summary.csv"

SUMMARY_OUT = OUT / "e150_e144_postfeedback_interpreter_summary.csv"
REPORT_OUT = OUT / "e150_e144_postfeedback_interpreter_report.md"
OBSERVED_OUT = OUT / "e150_e144_observed_score_decision.csv"

FOCUS_PRIORS = ["global", "subject", "nearest_hard085"]
FOCUS_GROUP_KINDS = ["target", "component"]


OVERRIDES: dict[str, dict[str, str]] = {
    "breakthrough_win": {
        "branch_status": "validated_large",
        "allowed_next": "Promote E144, add it as a new anchor, rerun exact-delta branch audits before testing less-pruned variants.",
        "candidate_to_test": "",
        "forbidden": f"Do not submit {E142_SUBMISSION} immediately; a big E144 win validates pruning first, not unpruned residual movement.",
        "belief_update": "E142/E143 residual branch is public-real, but E149 still says this is branch geometry rather than a broad JEPA breakthrough.",
    },
    "clean_win": {
        "branch_status": "validated_readable",
        "allowed_next": "Promote E144 to frontier and rerun E142/E143/E144 audits with E144 as anchor.",
        "candidate_to_test": "",
        "forbidden": "Do not relax the active/Q2S3 veto before a fresh exact-delta audit.",
        "belief_update": "Fine active-boundary pruning is public-real at readable scale.",
    },
    "micro_win": {
        "branch_status": "validated_micro",
        "allowed_next": "Promote E144, but spend the next experiment on an independent representation signal, not another same-family micro-tweak.",
        "candidate_to_test": "",
        "forbidden": "Do not call this 0.54-path evidence or a broad representation breakthrough.",
        "belief_update": "Branch-pruned residual geometry is alive but still frontier-scale small.",
    },
    "tie": {
        "branch_status": "ambiguous",
        "allowed_next": "Keep E95 as practical frontier; pause same-family submissions unless deliberately buying an information-only contrast.",
        "candidate_to_test": "",
        "forbidden": f"Do not auto-submit {E143_SUBMISSION}; a tie is not evidence that E143 is better.",
        "belief_update": "E144 did not resolve whether the branch is public-positive.",
    },
    "fine_loss_branch_alive": {
        "branch_status": "conditional_alive",
        "allowed_next": "Do not auto-submit a follow-up. Use attribution: E143 is allowed only if the observed read points specifically to fine-tail/S3 retention rather than inherited-body/Q3/S2 or broad branch failure.",
        "candidate_to_test": f"conditional:{E143_SUBMISSION}",
        "forbidden": f"Do not submit {E143_SUBMISSION} from score band alone; E148/E149 require target/component attribution first.",
        "belief_update": "E144 fine retained tail or a target-local slice may be too optimistic, but the scalar band alone does not identify the culprit.",
    },
    "branch_loss": {
        "branch_status": "weak_rejected",
        "allowed_next": "Block E143/E142 automatic rescue. Re-audit why the branch underperformed the resolved E101 negative sensor.",
        "candidate_to_test": "",
        "forbidden": f"Do not rescue with {E143_SUBMISSION} or {E142_SUBMISSION} before explaining E101 underperformance.",
        "belief_update": "E101-conditioned transfer-budget branch is likely overfit as a selector.",
    },
    "hard_fail": {
        "branch_status": "rejected",
        "allowed_next": "Close E142/E143/E144 as public-sensor overfit and return to hidden representation search.",
        "candidate_to_test": "",
        "forbidden": "Do not tune top counts, keep factors, active/Q2S3 masks, or nearby same-family variants.",
        "belief_update": "The transfer-budget residual branch failed as public-safe probability movement.",
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
        one = focus[focus["prior"].eq(prior)].sort_values("rank").head(4)
        if one.empty:
            continue
        groups = []
        for rec in one.to_dict("records"):
            groups.append(f"{rec['group_kind']}={rec['group']}")
        parts.append(f"{prior}: " + ", ".join(groups))
    return " | ".join(parts)


def rate_summary(rates: pd.DataFrame, outcome: str) -> dict[str, float]:
    out: dict[str, float] = {}
    focus = rates[rates["outcome"].eq(outcome)]
    for prior in FOCUS_PRIORS:
        one = focus[focus["prior"].eq(prior)]
        if one.empty:
            out[f"{prior}_world_rate"] = np.nan
            out[f"{prior}_mean_delta"] = np.nan
        else:
            row = one.iloc[0]
            out[f"{prior}_world_rate"] = float(row["world_rate"])
            out[f"{prior}_mean_delta"] = float(row["mean_delta_vs_e95"])
    return out


def load_geometry() -> dict[str, float]:
    summary = pd.read_csv(E149_SUMMARY_IN).set_index("name")
    e144 = summary.loc["e144"]
    return {
        "cos_e101_loss_axis": float(e144["cos_e101_loss_axis"]),
        "cos_e72_fail_axis": float(e144["cos_e72_fail_axis"]),
        "cos_e142_branch_axis": float(e144["cos_e142_branch_axis"]),
        "cos_e143_branch_axis": float(e144["cos_e143_branch_axis"]),
        "resid_ratio_vs_e142_axis": float(e144["resid_ratio_vs_e142_axis"]),
        "resid_ratio_vs_e143_axis": float(e144["resid_ratio_vs_e143_axis"]),
        "q2s3_share": float(e144["q2s3_share"]),
    }


def build_interpreter() -> pd.DataFrame:
    bands = pd.read_csv(E145_IN)
    rates = pd.read_csv(E148_RATES_IN)
    top = pd.read_csv(E148_TOP_IN)
    geom = load_geometry()

    rows: list[dict[str, Any]] = []
    for rec in bands.to_dict("records"):
        outcome = str(rec["outcome"])
        override = OVERRIDES[outcome]
        row: dict[str, Any] = {
            "outcome": outcome,
            "delta_vs_e95_lo_exclusive": rec["delta_vs_e95_lo_exclusive"],
            "delta_vs_e95_hi_inclusive": rec["delta_vs_e95_hi_inclusive"],
            "public_lb_lo_exclusive": rec["public_lb_lo_exclusive"],
            "public_lb_hi_inclusive": rec["public_lb_hi_inclusive"],
            "branch_status": override["branch_status"],
            "allowed_next": override["allowed_next"],
            "candidate_to_test": override["candidate_to_test"],
            "forbidden": override["forbidden"],
            "belief_update": override["belief_update"],
            "top_attribution_focus": collapse_top_groups(top, outcome),
            "geometry_read": (
                f"E144 is near E143/E142 branch axes "
                f"(cos_e143={geom['cos_e143_branch_axis']:.9f}, "
                f"cos_e142={geom['cos_e142_branch_axis']:.9f}) and away from "
                f"E101/E72 axes (cos_e101={geom['cos_e101_loss_axis']:.9f}, "
                f"cos_e72={geom['cos_e72_fail_axis']:.9f})."
            ),
            "kill_claim": "E144 public score is the smallest experiment that can validate or kill this branch-pruned residual world.",
        }
        row.update(rate_summary(rates, outcome))
        rows.append(row)
    return pd.DataFrame(rows)


def classify_score(summary: pd.DataFrame, score: float) -> pd.DataFrame:
    delta = float(score) - E95_PUBLIC
    mask = (
        (delta > summary["delta_vs_e95_lo_exclusive"].astype(float))
        & (delta <= summary["delta_vs_e95_hi_inclusive"].astype(float))
    )
    if int(mask.sum()) != 1:
        raise RuntimeError(f"Score {score} maps to {int(mask.sum())} bands")
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
        "candidate_to_test",
        "allowed_next",
    ]
    evidence_cols = [
        "outcome",
        "global_world_rate",
        "subject_world_rate",
        "nearest_hard085_world_rate",
        "top_attribution_focus",
    ]
    guard_cols = ["outcome", "belief_update", "forbidden"]
    geom = load_geometry()

    report = f"""# E150 E144 Post-Feedback Interpreter

## Question

After E149, E144 should not be interpreted as a broad new law. How should the
future public LB for `{E144_SUBMISSION}` update the world model and the next
submission decision?

## Strangest Point

E144 is visible-prior supported, but geometrically it is almost the same branch
as E143: cosine with E143 is `{geom['cos_e143_branch_axis']:.9f}` and residual
ratio versus E143 is `{geom['resid_ratio_vs_e143_axis']:.9f}`. At the same time,
it is nearly orthogonal to the resolved E101 loss axis
(`{geom['cos_e101_loss_axis']:.9f}`) and E72 fail axis
(`{geom['cos_e72_fail_axis']:.9f}`).

## Current World Model

The live world is not "new broad representation found". It is:

`E95 hardtail is the current public law. E144 tests whether a transfer-budget
residual branch can be added after active/Q2S3 pruning, while avoiding the
known E72/E101 public-negative axes.`

## Interpreter Table

{md_table(summary[compact_cols], ".9f")}

## Attribution Priors

{md_table(summary[evidence_cols], ".9f")}

## Guardrails

{md_table(summary[guard_cols], ".9f")}

## Smallest Kill Experiment

Submit `{E144_SUBMISSION}` and run:

```bash
python3 analysis_outputs/e150_e144_postfeedback_interpreter.py --score <PUBLIC_LB>
```

This classifies the score without changing the rules after the fact.

## Decision

No submission is created by E150. E144 remains the next file. The main correction
to E145 is that `fine_loss_branch_alive` is no longer enough to auto-submit
E143; E148/E149 require target/component attribution first.
"""
    REPORT_OUT.write_text(report)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--score", type=float, default=None, help="Observed E144 public LB to classify.")
    args = parser.parse_args()

    summary = build_interpreter()
    summary.to_csv(SUMMARY_OUT, index=False)
    write_report(summary)

    print({"summary": str(SUMMARY_OUT), "report": str(REPORT_OUT), "rows": int(len(summary))})
    print(summary[["outcome", "public_lb_lo_exclusive", "public_lb_hi_inclusive", "branch_status", "candidate_to_test"]].to_string(index=False))

    if args.score is not None:
        decision = classify_score(summary, args.score)
        decision.to_csv(OBSERVED_OUT, index=False)
        print("\nObserved decision")
        print(
            decision[
                [
                    "observed_public_lb",
                    "observed_delta_vs_e95",
                    "outcome",
                    "branch_status",
                    "allowed_next",
                    "candidate_to_test",
                    "forbidden",
                ]
            ].to_string(index=False)
        )


if __name__ == "__main__":
    main()
