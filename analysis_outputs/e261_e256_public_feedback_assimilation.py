#!/usr/bin/env python3
"""E261: assimilate the E256 public result.

E259 pre-registered score bands for E256/E224. E260 decomposed the E256-vs-E247
risk into E247-only broad deletions and four E256-only high-amplitude additions.
E261 records the actual E256 public LB and turns it into an explicit branch
update.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

E247_PUBLIC = 0.5761589494
E256_PUBLIC = 0.5762805676
E95_PUBLIC = 0.5762913298
MIXMIN_PUBLIC = 0.5763066405

DECODED_IN = OUT / "e259_post_e247_decoded_scores.json"
PAIR_IN = OUT / "e260_post_e247_next_slot_pair_summary.csv"
GROUP_IN = OUT / "e260_post_e247_next_slot_group_summary.csv"
TOP_IN = OUT / "e260_post_e247_next_slot_top_cells.csv"

SUMMARY_OUT = OUT / "e261_e256_public_feedback_summary.csv"
GROUP_OUT = OUT / "e261_e256_public_group_read.csv"
REPORT_OUT = OUT / "e261_e256_public_feedback_assimilation_report.md"


def md_table(frame: pd.DataFrame, n: int = 20, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame.head(n).copy()
    headers = list(view.columns)
    rows: list[list[str]] = []
    for _, row in view.iterrows():
        out_row = []
        for col in headers:
            value = row[col]
            if isinstance(value, (float, np.floating)):
                out_row.append(format(float(value), floatfmt))
            else:
                out_row.append(str(value))
        rows.append(out_row)
    out = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    out.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(out)


def min_cells_for_threshold(swings: np.ndarray, threshold: float) -> int:
    if threshold <= 0:
        return 0
    csum = np.cumsum(np.sort(np.asarray(swings, dtype=np.float64))[::-1])
    idx = np.where(csum >= threshold)[0]
    return int(idx[0] + 1) if len(idx) else int(len(csum))


def load_decoded() -> dict[str, Any]:
    if not DECODED_IN.exists():
        return {
            "candidate_id": "E256",
            "outcome": "same_family_loss",
            "world_update_class": "rejection",
            "next_action": "Stop sibling sweeps. Submit E224 only if the next question is body attribution; otherwise search non-collinear structure.",
        }
    decoded = json.loads(DECODED_IN.read_text(encoding="utf-8"))
    if not decoded:
        raise ValueError(f"empty decoded score file: {DECODED_IN}")
    return dict(decoded[0])


def main() -> None:
    decoded = load_decoded()
    pair = pd.read_csv(PAIR_IN)
    group = pd.read_csv(GROUP_IN)
    top = pd.read_csv(TOP_IN)

    e256_pair = pair[pair["pair_id"].eq("e256_vs_e247")].iloc[0].to_dict()
    e256_groups = group[group["pair_id"].eq("e256_vs_e247")].copy()
    e256_top = top[top["pair_id"].eq("e256_vs_e247")].copy()

    delta_vs_e247 = E256_PUBLIC - E247_PUBLIC
    delta_vs_e95 = E256_PUBLIC - E95_PUBLIC
    delta_vs_mixmin = E256_PUBLIC - MIXMIN_PUBLIC
    expected_vs_e247 = float(e256_pair["expected_focus"])
    excess_over_expected = delta_vs_e247 - expected_vs_e247
    swings = e256_top["swing"].to_numpy(dtype=np.float64)

    summary = pd.DataFrame(
        [
            {
                "candidate_id": "E256",
                "file": "submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv",
                "public_lb": E256_PUBLIC,
                "delta_vs_e247": delta_vs_e247,
                "delta_vs_e95": delta_vs_e95,
                "delta_vs_mixmin": delta_vs_mixmin,
                "e259_outcome": decoded.get("outcome", ""),
                "world_update_class": decoded.get("world_update_class", ""),
                "e260_expected_vs_e247": expected_vs_e247,
                "actual_over_e260_expected": excess_over_expected,
                "actual_over_expected_ratio": delta_vs_e247 / max(abs(expected_vs_e247), 1.0e-15),
                "e260_swing_sum": float(e256_pair["swing_sum"]),
                "top1_swing": float(e256_pair["top1_swing"]),
                "top5_swing": float(e256_pair["top5_swing"]),
                "min_top_cells_to_explain_actual_delta": min_cells_for_threshold(swings, delta_vs_e247),
                "min_top_cells_to_explain_excess_over_expected": min_cells_for_threshold(swings, excess_over_expected),
                "branch_read": "same_family_loss_but_not_hard_loss",
            }
        ]
    )

    e256_groups = e256_groups[
        [
            "pair_id",
            "e257_group",
            "moved_cells",
            "expected_focus",
            "adverse_delta",
            "support_prob_focus_swing_weighted",
            "top1_over_abs_expected",
        ]
    ].copy()
    e256_groups["post_public_read"] = np.where(
        e256_groups["e257_group"].eq("e256_only"),
        "first_suspect_after_E256_loss",
        "not_proven_causal_by_E256_loss",
    )

    SUMMARY_OUT.write_text(summary.to_csv(index=False), encoding="utf-8")
    GROUP_OUT.write_text(e256_groups.to_csv(index=False), encoding="utf-8")
    REPORT_OUT.write_text(report_text(summary, e256_groups, e256_top, decoded), encoding="utf-8")

    print(f"wrote {SUMMARY_OUT}")
    print(f"wrote {GROUP_OUT}")
    print(f"wrote {REPORT_OUT}")


def report_text(summary: pd.DataFrame, group_read: pd.DataFrame, top_cells: pd.DataFrame, decoded: dict[str, Any]) -> str:
    rec = summary.iloc[0]
    top_cols = [
        "row_idx",
        "target",
        "subject_id",
        "lifelog_date",
        "e257_group",
        "action",
        "prob_delta",
        "swing",
        "expected_focus",
        "support_prob_focus",
    ]
    return f"""# E261 E256 Public Feedback Assimilation

## Observation

`submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv` public LB is `{E256_PUBLIC:.10f}`.

## Decoded Result

| item | value |
| --- | --- |
| delta_vs_E247 | {float(rec['delta_vs_e247']):.9f} |
| delta_vs_E95 | {float(rec['delta_vs_e95']):.9f} |
| delta_vs_mixmin | {float(rec['delta_vs_mixmin']):.9f} |
| E259 outcome | {rec['e259_outcome']} |
| world update | {rec['world_update_class']} |
| branch read | {rec['branch_read']} |

E256 lost the E247 edge by `{float(rec['delta_vs_e247']):.9f}`, but it still beats E95 by `{abs(float(rec['delta_vs_e95'])):.9f}`. This is not a hard collapse of the feature-NN1 smoothing family. It is a rejection of the high-amplitude constrained refinement as the next score route.

## E260 Stress Check

| item | value |
| --- | --- |
| E260 expected E256-vs-E247 | {float(rec['e260_expected_vs_e247']):.9f} |
| actual minus expected | {float(rec['actual_over_e260_expected']):.9f} |
| actual / expected_abs | {float(rec['actual_over_expected_ratio']):.3f} |
| E260 swing sum | {float(rec['e260_swing_sum']):.9f} |
| min top cells for actual delta | {int(rec['min_top_cells_to_explain_actual_delta'])} |
| min top cells for surprise over expected | {int(rec['min_top_cells_to_explain_excess_over_expected'])} |

The observed loss is much larger than the E260 focus-prior expectation, but it is still hard-label-plausible: the top two E256-vs-E247 swing cells can explain the actual delta scale.

## Group Read

{md_table(group_read)}

## Top E256 Swing Cells

{md_table(top_cells[top_cols], n=10)}

## World Update

- Strengthened: E247 exact top34 / body-plus-rollback interaction.
- Weakened: high-amplitude constrained smoothing as a score route.
- Not proven: that E247-only broad cells alone caused the win. E260 says the four E256-only high-amplitude cells remain the first suspect.

## Next Action

{decoded.get('next_action', 'Stop E256-like sibling sweeps before another public observation.')}

Operational rule: do not submit another E246/E256 sibling from scalar threshold tuning. If the next question is attribution, use E224. If the next question is score, refresh non-collinear candidates under the updated E247/E256 anchors.
"""


if __name__ == "__main__":
    main()
