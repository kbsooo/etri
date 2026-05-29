#!/usr/bin/env python3
"""E116 E101 public feedback decoder.

E115 says E101 is the highest-actionability public sensor. This script makes
the next external observation operational: once a public LB for E101 is known,
which world-model branch should be considered alive, and which tempting followup
should be blocked?

It does not infer labels and does not generate a submission. It converts a
future public score into pre-registered branch decisions.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

E95_PUBLIC = 0.5762913298
MIXMIN_PUBLIC = 0.5763066405
E95_EDGE_VS_MIXMIN = E95_PUBLIC - MIXMIN_PUBLIC

E115_OUTCOMES = OUT / "e115_public_sensor_information_outcomes.csv"
E107_SCENARIOS = OUT / "e107_e101_feedback_decision_map_scenarios.csv"

DECODER_OUT = OUT / "e116_e101_public_feedback_decoder.csv"
REPORT_OUT = OUT / "e116_e101_public_feedback_decoder_report.md"


BANDS = [
    {
        "outcome": "strong_win",
        "delta_lo_exclusive": -np.inf,
        "delta_hi_inclusive": -3.0e-5,
        "world_update": "E101 wins beyond the calibrated edge/small-win family; Q2/S3 rollback direction is alive but public world is more aggressive than the E107 normal band.",
        "next_action": "Rerun E107/E115 with the exact delta, then consider the risk E108 amp050 file as an upside sensor.",
        "candidate_to_test": "analysis_outputs/submission_e108_if_e101win_amp050_079aab57.csv",
        "forbidden_action": "Do not treat the strong win as proof that all E89/E86 structure should be restored; the win is still an active Q2/S3/S3-heavy event.",
    },
    {
        "outcome": "edge_win",
        "delta_lo_exclusive": -3.0e-5,
        "delta_hi_inclusive": -1.1e-5,
        "world_update": "E95 structural law was mostly right, but Q2/S3 hard-tail cells were over-amplified around the same scale as the E95 public edge.",
        "next_action": "Use E108 amp050 for upside or E108 strict amp038 if the next slot must preserve E101-pass stress.",
        "candidate_to_test": "analysis_outputs/submission_e108_if_e101win_amp050_079aab57.csv or analysis_outputs/submission_e108_if_e101win_strict_amp038_64514c53.csv",
        "forbidden_action": "Do not jump to full E89; E101 specifically says the smaller active-cell rollback explained the edge first.",
    },
    {
        "outcome": "small_win",
        "delta_lo_exclusive": -1.1e-5,
        "delta_hi_inclusive": -3.0e-6,
        "world_update": "Q2/S3 rollback direction is public-real but small; amplitude is live, downside control still matters.",
        "next_action": "Prefer E108 strict amp038 if risk control matters; amp050 remains an upside sensor only.",
        "candidate_to_test": "analysis_outputs/submission_e108_if_e101win_strict_amp038_64514c53.csv",
        "forbidden_action": "Do not widen to broad Q/Q3/S4 or raw-context movement; the signal is narrow and active-cell-local.",
    },
    {
        "outcome": "tie",
        "delta_lo_exclusive": -3.0e-6,
        "delta_hi_inclusive": 3.0e-6,
        "world_update": "E101 did not falsify E95 strongly. The active-cell rollback world is at best weak and should not be amplified without rebuilding the scenario model.",
        "next_action": "Keep E95 as frontier and rebuild E99/E101 worlds using the exact near-zero observation.",
        "candidate_to_test": "",
        "forbidden_action": "Do not submit E108, E104 higher-alpha, E106 masks, or full E89 as automatic rescue.",
    },
    {
        "outcome": "small_loss",
        "delta_lo_exclusive": 3.0e-6,
        "delta_hi_inclusive": 2.0e-5,
        "world_update": "E101 active-cell support labels did not realize; the same rollback line is contradicted.",
        "next_action": "Keep E95 as frontier, mark E101 branch as model tension, and rebuild the public-world model before any same-family file.",
        "candidate_to_test": "",
        "forbidden_action": "Do not submit E108, subject-prior gates, active-restored E89/E85, or non-active grafts as automatic followups.",
    },
    {
        "outcome": "large_loss",
        "delta_lo_exclusive": 2.0e-5,
        "delta_hi_inclusive": np.inf,
        "world_update": "E101 is strongly incompatible with the realized public hard-label world; E99/E101 abstraction missed a key public structure.",
        "next_action": "Stop the E101 family and return to broader hidden-block/public-subset diagnosis.",
        "candidate_to_test": "",
        "forbidden_action": "Do not tune amplitude on the same active cells; the direction failed, not just the scale.",
    },
]


def md_table(frame: pd.DataFrame, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    headers = [str(c) for c in frame.columns]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for rec in frame.to_dict("records"):
        vals: list[str] = []
        for col in frame.columns:
            value = rec[col]
            if pd.isna(value):
                vals.append("")
            elif isinstance(value, (float, np.floating)):
                vals.append(format(float(value), floatfmt))
            else:
                vals.append(str(value))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def lb_bound(delta: float) -> float:
    return E95_PUBLIC + float(delta)


def build_decoder() -> pd.DataFrame:
    e115 = pd.read_csv(E115_OUTCOMES)
    e107 = pd.read_csv(E107_SCENARIOS)
    rows: list[dict[str, Any]] = []
    for band in BANDS:
        outcome = band["outcome"]
        e115_row = e115[(e115["sensor"].eq("control_e101")) & (e115["outcome"].eq(outcome))]
        e107_row = e107[e107["outcome"].str.contains(outcome.replace("strong_win", "strong_win"), regex=False)]
        # E107 has richer names for win/loss buckets.
        if outcome == "edge_win":
            e107_row = e107[e107["outcome"].eq("e95_edge_win")]
        elif outcome == "small_win":
            e107_row = e107[e107["outcome"].eq("small_win_5e_minus6")]
        elif outcome == "tie":
            e107_row = e107[e107["outcome"].eq("tie")]
        elif outcome == "small_loss":
            e107_row = e107[e107["outcome"].eq("small_loss_1e_minus5")]
        elif outcome == "large_loss":
            e107_row = e107[e107["outcome"].eq("large_loss_4e_minus5")]
        elif outcome == "strong_win":
            e107_row = e107[e107["outcome"].eq("strong_win_5e_minus5")]

        e115_rec = e115_row.iloc[0].to_dict() if len(e115_row) else {}
        e107_rec = e107_row.iloc[0].to_dict() if len(e107_row) else {}
        lo = float(band["delta_lo_exclusive"])
        hi = float(band["delta_hi_inclusive"])
        rows.append(
            {
                "outcome": outcome,
                "delta_vs_e95_lo_exclusive": lo,
                "delta_vs_e95_hi_inclusive": hi,
                "public_lb_lo_exclusive": lb_bound(lo) if np.isfinite(lo) else -np.inf,
                "public_lb_hi_inclusive": lb_bound(hi) if np.isfinite(hi) else np.inf,
                "beats_e95": hi < 0,
                "beats_mixmin": (lb_bound(hi) < MIXMIN_PUBLIC) if np.isfinite(hi) else False,
                "e115_scenario_rate": e115_rec.get("rate", np.nan),
                "e115_n_scenarios": e115_rec.get("n_scenarios", np.nan),
                "e115_delta_mean": e115_rec.get("delta_mean", np.nan),
                "e107_selection_mode": e107_rec.get("selection_mode", ""),
                "e107_model_tension": e107_rec.get("model_tension", np.nan),
                "world_update": band["world_update"],
                "next_action": band["next_action"],
                "candidate_to_test": band["candidate_to_test"],
                "forbidden_action": band["forbidden_action"],
            }
        )
    return pd.DataFrame(rows)


def write_report(decoder: pd.DataFrame) -> None:
    compact = decoder[
        [
            "outcome",
            "public_lb_lo_exclusive",
            "public_lb_hi_inclusive",
            "e115_scenario_rate",
            "e107_selection_mode",
            "e107_model_tension",
            "next_action",
            "candidate_to_test",
        ]
    ].copy()
    report = f"""# E116 E101 Public Feedback Decoder

## Question

E115 says `submission_e101_q2s3tail_177569bc.csv` is the next public sensor.
E116 pre-registers how to interpret its public LB before seeing it.

Current frontier:

- E95 file: `submission_e95_hardtail_541e3973.csv`
- E95 public LB: `{E95_PUBLIC:.10f}`
- mixmin public LB: `{MIXMIN_PUBLIC:.10f}`
- E95 edge versus mixmin: `{E95_EDGE_VS_MIXMIN:.10f}`

## Decoder

{md_table(compact)}

## Decision Rules

- Strong/edge/small win: E101 direction is public-real. Consider E108 only
  after using the exact observed delta to rerun the conditional branch map.
- Tie: keep E95 as frontier and rebuild the E99/E101 world model. Do not
  amplify the same line.
- Small/large loss: the active-cell rollback support world failed. Do not use
  E108, E104 higher alpha, E106 subject-prior masks, active-restored E89/E85,
  or non-active grafts as automatic followups.

## Submission Status

No submission is materialized by E116. It is a public-feedback interpretation
artifact for `submission_e101_q2s3tail_177569bc.csv`.
"""
    REPORT_OUT.write_text(report)


def main() -> None:
    decoder = build_decoder()
    decoder.to_csv(DECODER_OUT, index=False)
    write_report(decoder)
    print(f"wrote {DECODER_OUT}")
    print(f"wrote {REPORT_OUT}")


if __name__ == "__main__":
    main()
