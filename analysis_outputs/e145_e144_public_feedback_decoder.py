#!/usr/bin/env python3
"""E145: pre-register how to interpret the pending E144 public LB.

E144 is the current next sensor. This script does not infer labels and does not
generate a submission. It turns the future public score for E144 into explicit
world-model branch decisions before that score is known.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

E95_PUBLIC = 0.5762913298
E101_PUBLIC = 0.5763003660
MIXMIN_PUBLIC = 0.5763066405

E144_FRONTIER = OUT / "e144_e143_active_boundary_refine_frontier.csv"
DECODER_OUT = OUT / "e145_e144_public_feedback_decoder.csv"
REPORT_OUT = OUT / "e145_e144_public_feedback_decoder_report.md"

E144_SUBMISSION = "submission_e144_activeboundary_d7b4b331.csv"
E143_SUBMISSION = "submission_e143_activeq2s3repair_68ca656f.csv"
E142_SUBMISSION = "submission_e142_transferclip_09a92236.csv"

E101_DELTA = E101_PUBLIC - E95_PUBLIC
MIXMIN_DELTA = MIXMIN_PUBLIC - E95_PUBLIC


BANDS: list[dict[str, Any]] = [
    {
        "outcome": "breakthrough_win",
        "delta_lo_exclusive": -np.inf,
        "delta_hi_inclusive": -2.0e-5,
        "world_update": "E144 wins by more than the current E95-over-mixmin edge scale. The residual decoder is public-real and local stress likely underestimates its upside.",
        "next_action": "Add E144 as the new public anchor, rerun exact-delta residual-branch audits, then consider whether E142 or a less-pruned neighbor is the next information sensor.",
        "candidate_to_test": E142_SUBMISSION,
        "forbidden_action": "Do not jump to broad model/blend escalation; first check whether the same transfer-budget law explains the larger-than-expected win.",
    },
    {
        "outcome": "clean_win",
        "delta_lo_exclusive": -2.0e-5,
        "delta_hi_inclusive": -7.0e-6,
        "world_update": "E144 beats E95 at a readable frontier scale. The fine active/Q2S3 boundary is likely public-real.",
        "next_action": "Promote E144 to frontier and rerun branch audits with E144 as the anchor before testing any less-pruned successor.",
        "candidate_to_test": "",
        "forbidden_action": "Do not submit E142 immediately; E144's win would validate pruning, not unpruned residual movement.",
    },
    {
        "outcome": "micro_win",
        "delta_lo_exclusive": -7.0e-6,
        "delta_hi_inclusive": -2.0e-6,
        "world_update": "E144 beats E95 but only at a micro-edge scale. The fine boundary is alive, but the branch remains a narrow calibration/tail repair.",
        "next_action": "Promote E144, but use the next experiment to find an independent representation signal rather than another tiny same-family boundary tweak.",
        "candidate_to_test": "",
        "forbidden_action": "Do not interpret a micro-win as evidence for 0.54 progress or for relaxing the active/Q2S3 veto.",
    },
    {
        "outcome": "tie",
        "delta_lo_exclusive": -2.0e-6,
        "delta_hi_inclusive": 2.0e-6,
        "world_update": "E144 is indistinguishable from E95 at the current sensor scale. The residual branch is neither validated nor killed.",
        "next_action": "Keep E95 as the practical frontier; use E143 only as a deliberate boundary contrast, not an automatic next submission.",
        "candidate_to_test": "",
        "forbidden_action": "Do not post-hoc claim the fine boundary worked; the observation is too close to zero.",
    },
    {
        "outcome": "fine_loss_branch_alive",
        "delta_lo_exclusive": 2.0e-6,
        "delta_hi_inclusive": E101_DELTA,
        "world_update": "E144 loses to E95 but stays no worse than the resolved E101 negative sensor. The retained keep0.15 active tail may be too optimistic, while the conservative boundary remains testable.",
        "next_action": "If spending another public slot on this branch, submit E143 as the clean contrast; otherwise pause same-family refinements and inspect the exact E144-minus-E143 retained cells.",
        "candidate_to_test": E143_SUBMISSION,
        "forbidden_action": "Do not submit E142 before E143; the first question after this loss is fine-tail retention, not unpruned residual upside.",
    },
    {
        "outcome": "branch_loss",
        "delta_lo_exclusive": E101_DELTA,
        "delta_hi_inclusive": MIXMIN_DELTA,
        "world_update": "E144 is worse than E101 but still no worse than mixmin. The transfer-budget branch is weaker than the earlier negative Q2/S3 rollback sensor.",
        "next_action": "Do not auto-submit E143/E142. Re-audit whether E101-conditioned transfer gates have become public-overfit selectors.",
        "candidate_to_test": "",
        "forbidden_action": "Do not rescue the branch with a nearby same-family file before explaining why it underperformed E101.",
    },
    {
        "outcome": "hard_fail",
        "delta_lo_exclusive": MIXMIN_DELTA,
        "delta_hi_inclusive": np.inf,
        "world_update": "E144 gives back all E95 gain and more. The transfer-budget residual branch is not public-safe as a selector.",
        "next_action": "Close E142/E143/E144 as public-sensor overfit and return to hidden representation search rather than local boundary repair.",
        "candidate_to_test": "",
        "forbidden_action": "Do not tune top counts, keep factors, or active/Q2S3 masks on this branch.",
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


def lb_bound(delta: float) -> float:
    return E95_PUBLIC + float(delta)


def load_local_context() -> dict[str, Any]:
    frontier = pd.read_csv(E144_FRONTIER)
    e144 = frontier[frontier["e144_submit"].astype(bool)].sort_values("all_minus_base").iloc[0]
    e143 = frontier[frontier["strategy"].eq("control_e143")].iloc[0]
    e142 = frontier[frontier["strategy"].eq("control_e142")].iloc[0]
    return {
        "e144_tag": e144["tag"],
        "e144_mask": e144["mask_name"],
        "e144_keep_factor": float(e144["keep_factor"]),
        "e144_rollback_cells": int(e144["rollback_cells"]),
        "e144_changed_cells_vs_e95": int(e144["changed_cells_vs_e95"]),
        "e144_all_minus_e95": float(e144["all_minus_base"]),
        "e144_post101_p95": float(e144["post101_p95_vs_e95_e101_sensor"]),
        "e144_post101_mean": float(e144["post101_mean_vs_e95_e101_sensor"]),
        "e143_all_minus_e95": float(e143["all_minus_base"]),
        "e143_post101_p95": float(e143["post101_p95_vs_e95_e101_sensor"]),
        "e142_all_minus_e95": float(e142["all_minus_base"]),
        "e142_post101_p95": float(e142["post101_p95_vs_e95_e101_sensor"]),
    }


def build_decoder(local: dict[str, Any]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for band in BANDS:
        lo = float(band["delta_lo_exclusive"])
        hi = float(band["delta_hi_inclusive"])
        rows.append(
            {
                "outcome": band["outcome"],
                "delta_vs_e95_lo_exclusive": lo,
                "delta_vs_e95_hi_inclusive": hi,
                "public_lb_lo_exclusive": lb_bound(lo) if np.isfinite(lo) else -np.inf,
                "public_lb_hi_inclusive": lb_bound(hi) if np.isfinite(hi) else np.inf,
                "beats_e95": hi < 0,
                "beats_e101": (lb_bound(hi) < E101_PUBLIC) if np.isfinite(hi) else False,
                "beats_mixmin": (lb_bound(hi) < MIXMIN_PUBLIC) if np.isfinite(hi) else False,
                "e144_local_minus_e95": local["e144_all_minus_e95"],
                "e144_minus_e143_local": local["e144_all_minus_e95"] - local["e143_all_minus_e95"],
                "world_update": band["world_update"],
                "next_action": band["next_action"],
                "candidate_to_test": band["candidate_to_test"],
                "forbidden_action": band["forbidden_action"],
            }
        )
    return pd.DataFrame(rows)


def write_report(decoder: pd.DataFrame, local: dict[str, Any]) -> None:
    compact = decoder[
        [
            "outcome",
            "public_lb_lo_exclusive",
            "public_lb_hi_inclusive",
            "beats_e95",
            "beats_e101",
            "beats_mixmin",
            "next_action",
            "candidate_to_test",
        ]
    ].copy()
    detail = decoder[
        [
            "outcome",
            "world_update",
            "forbidden_action",
        ]
    ].copy()
    report = f"""# E145 E144 Public Feedback Decoder

## Question

E144 is the current next public sensor:

- file: `{E144_SUBMISSION}`
- intent: test whether E143's active/Q2S3 repair boundary is fine rather than a full-rollback cliff.
- current public frontier: `submission_e95_hardtail_541e3973.csv` at `{E95_PUBLIC:.10f}`
- resolved negative comparison: `submission_e101_q2s3tail_177569bc.csv` at `{E101_PUBLIC:.10f}`
- previous frontier comparison: `submission_mixmin_0c916bb4.csv` at `{MIXMIN_PUBLIC:.10f}`

E145 pre-registers how to interpret the future E144 public LB before seeing it.

## Local Context

| item | value |
| --- | --- |
| selected tag | `{local['e144_tag']}` |
| selected mask | `{local['e144_mask']}` |
| keep factor | `{local['e144_keep_factor']:.6f}` |
| rollback cells | `{local['e144_rollback_cells']}` |
| changed cells vs E95 | `{local['e144_changed_cells_vs_e95']}` |
| E144 local all-minus-E95 | `{local['e144_all_minus_e95']:.12f}` |
| E143 local all-minus-E95 | `{local['e143_all_minus_e95']:.12f}` |
| E144 minus E143 local | `{local['e144_all_minus_e95'] - local['e143_all_minus_e95']:.12f}` |
| E144 post-E101 p95 | `{local['e144_post101_p95']:.12f}` |
| E143 post-E101 p95 | `{local['e143_post101_p95']:.12f}` |

## Decoder Bands

{md_table(compact)}

## World Updates And Guardrails

{md_table(detail)}

## Decision Rules

- Win by more than `7e-6`: E144 becomes a meaningful new public anchor; rerun exact-delta audits before testing less-pruned variants.
- Micro-win: promote E144 but do not claim a structural breakthrough or relax the active/Q2S3 veto.
- Tie: keep E95 as practical frontier; E144 did not give enough public information to justify post-hoc claims.
- Loss that stays no worse than E101: E143 is the only same-family contrast worth considering, because it removes the retained fine active tail.
- Worse than E101: do not auto-submit E143 or E142; first explain why E144 underperformed a resolved negative sensor.
- Worse than mixmin: close the E142/E143/E144 branch as selector overfit.

## Submission Status

No submission is created by E145. It is a public-feedback interpretation artifact for `{E144_SUBMISSION}`.
"""
    REPORT_OUT.write_text(report)


def main() -> None:
    local = load_local_context()
    decoder = build_decoder(local)
    decoder.to_csv(DECODER_OUT, index=False)
    write_report(decoder, local)
    print({"decoder": str(DECODER_OUT), "report": str(REPORT_OUT), "rows": int(len(decoder))})
    print(decoder[["outcome", "public_lb_lo_exclusive", "public_lb_hi_inclusive", "next_action"]].to_string(index=False))


if __name__ == "__main__":
    main()
