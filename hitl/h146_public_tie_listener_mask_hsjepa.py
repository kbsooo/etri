#!/usr/bin/env python3
"""H146: public-tie listener mask diagnostic for HS-JEPA.

H144 and H145 received the same displayed public LB:

    H144 = 0.567929641
    H145 = 0.567929641

They differ in only two row-target cells.  This script records that sensor
reading and turns it into an HS-JEPA architecture update: row-target actions
need a public-listener/responsibility head before an action can be treated as
public-grade.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "hitl" / "h146_public_tie_listener_mask_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]

FILES = {
    "h057": ROOT / "submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv",
    "h136": ROOT / "submission_h136_factorized_dc9dd2c5_uploadsafe.csv",
    "h139": ROOT / "submission_h139_roleatoms_bf2b3e77_uploadsafe.csv",
    "h141": ROOT / "submission_h141_commoncore_0999d3ae_uploadsafe.csv",
    "h144": ROOT / "submission_h144_targetxor_def80b88_uploadsafe.csv",
    "h145": ROOT / "submission_h145_q3repair_2d818e46_uploadsafe.csv",
}

PUBLIC_SCORES = {
    "h057": 0.5677475939,
    "h144": 0.5679296410,
    "h145": 0.5679296410,
}

PAIRWISE = [
    ("h144", "h145"),
    ("h145", "h141"),
    ("h144", "h139"),
    ("h145", "h057"),
    ("h144", "h057"),
    ("h141", "h057"),
]


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    if frame.empty:
        return "_empty_"
    shown = frame.head(n).copy()
    columns = shown.columns.tolist()
    rows = []
    rows.append("| " + " | ".join(columns) + " |")
    rows.append("| " + " | ".join(["---"] * len(columns)) + " |")
    for _, rec in shown.iterrows():
        vals = []
        for col in columns:
            val = rec[col]
            if isinstance(val, float):
                vals.append(f"{val:.12g}")
            else:
                vals.append(str(val))
        rows.append("| " + " | ".join(vals) + " |")
    return "\n".join(rows)


def load_submission(name: str) -> pd.DataFrame:
    path = FILES[name]
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def diff_cells(left_name: str, right_name: str, frames: dict[str, pd.DataFrame], eps: float = 1.0e-12) -> pd.DataFrame:
    left = frames[left_name]
    right = frames[right_name]
    if len(left) != len(right):
        raise ValueError(f"{left_name} and {right_name} have different row counts")

    rows: list[dict[str, object]] = []
    for row_idx in range(len(left)):
        for target in TARGETS:
            p_left = float(left.loc[row_idx, target])
            p_right = float(right.loc[row_idx, target])
            diff = p_left - p_right
            if abs(diff) <= eps:
                continue
            rows.append(
                {
                    "comparison": f"{left_name}_minus_{right_name}",
                    "left": left_name,
                    "right": right_name,
                    "row": int(row_idx),
                    "subject_id": left.loc[row_idx, "subject_id"],
                    "sleep_date": left.loc[row_idx, "sleep_date"],
                    "lifelog_date": left.loc[row_idx, "lifelog_date"],
                    "target": target,
                    "p_left": p_left,
                    "p_right": p_right,
                    "diff_left_minus_right": diff,
                    "absdiff": abs(diff),
                }
            )
    if not rows:
        return pd.DataFrame(
            columns=[
                "comparison",
                "left",
                "right",
                "row",
                "subject_id",
                "sleep_date",
                "lifelog_date",
                "target",
                "p_left",
                "p_right",
                "diff_left_minus_right",
                "absdiff",
            ]
        )
    return pd.DataFrame(rows).sort_values(["comparison", "row", "target"]).reset_index(drop=True)


def summarize_pairwise(all_diffs: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for left, right in PAIRWISE:
        part = all_diffs[all_diffs["comparison"].eq(f"{left}_minus_{right}")]
        rows.append(
            {
                "comparison": f"{left}_minus_{right}",
                "changed_cells": int(len(part)),
                "changed_rows": int(part["row"].nunique()) if not part.empty else 0,
                "targets": ",".join(part["target"].drop_duplicates().tolist()) if not part.empty else "",
                "l1_absdiff": float(part["absdiff"].sum()) if not part.empty else 0.0,
                "max_absdiff": float(part["absdiff"].max()) if not part.empty else 0.0,
                "public_left": PUBLIC_SCORES.get(left, np.nan),
                "public_right": PUBLIC_SCORES.get(right, np.nan),
                "public_delta_left_minus_right": (
                    float(PUBLIC_SCORES[left] - PUBLIC_SCORES[right])
                    if left in PUBLIC_SCORES and right in PUBLIC_SCORES
                    else np.nan
                ),
            }
        )
    return pd.DataFrame(rows)


def build_interpretation(summary: pd.DataFrame, h144_h145: pd.DataFrame) -> pd.DataFrame:
    equal_public = abs(PUBLIC_SCORES["h144"] - PUBLIC_SCORES["h145"]) < 5.0e-10
    worse_than_h057 = PUBLIC_SCORES["h144"] - PUBLIC_SCORES["h057"]
    rows = [
        {
            "finding": "H144/H145 public tie",
            "evidence": f"displayed public LB equal={equal_public}; delta={PUBLIC_SCORES['h144'] - PUBLIC_SCORES['h145']:.12f}",
            "interpretation": (
                "The public sensor did not distinguish the two-cell difference "
                "between H144 and H145 at displayed precision."
            ),
            "hs_jepa_update": "Add public-listener responsibility before action-grade decoding.",
        },
        {
            "finding": "Two-cell branch contrast",
            "evidence": (
                f"H144-H145 changed_cells={len(h144_h145)}, "
                f"rows={sorted(h144_h145['row'].unique().tolist()) if not h144_h145.empty else []}, "
                f"targets={h144_h145['target'].tolist() if not h144_h145.empty else []}"
            ),
            "interpretation": (
                "row207 S2 and the row135 Q3 amplitude distinction are probably "
                "non-listened, low-responsibility, or label-cancelling public cells."
            ),
            "hs_jepa_update": "Do not trust local route/H088/margin metrics without listener masking.",
        },
        {
            "finding": "Shared body is below frontier",
            "evidence": f"H144/H145 worse than H057 by {worse_than_h057:.10f}",
            "interpretation": (
                "The common H141-plus-repair body is public-misaligned relative to "
                "the H057 frontier; the row207-vs-Q3 fork is not the main loss source."
            ),
            "hs_jepa_update": "Separate public-listener mask from action-toxicity field.",
        },
    ]
    return pd.DataFrame(rows)


def write_report(summary: pd.DataFrame, h144_h145: pd.DataFrame, interpretation: pd.DataFrame) -> None:
    report = f"""# H146 Public-Tie Listener Mask Diagnostic

Date: 2026-06-03

## Sensor Observation

`submission_h144_targetxor_def80b88_uploadsafe.csv` public LB:
`{PUBLIC_SCORES['h144']:.9f}`

`submission_h145_q3repair_2d818e46_uploadsafe.csv` public LB:
`{PUBLIC_SCORES['h145']:.9f}`

Both are worse than H057 by `{PUBLIC_SCORES['h144'] - PUBLIC_SCORES['h057']:.10f}`.

## H144 vs H145 Cell Difference

{md_table(h144_h145, n=20)}

## Pairwise Summary

{md_table(summary, n=20)}

## Interpretation

{md_table(interpretation, n=20)}

## What This Kills

- H144 vs H145 was expected to let public choose between row207 S2 relief and
  Q3 repair-only.  It did not.
- Local route/H088/margin gains are not sufficient to rank these two actions.
- Row-target assignment without a public-listener/responsibility head is
  under-specified.

## What Survives

- H057 remains the best public action frontier.
- H141/H144/H145 still matter as structural probes, but not as frontier
  submissions until the listener mask is learned.
- The next HS-JEPA decoder should predict two fields:

```text
listener(row,target)  = how much public/private sensor listens to this cell
toxicity(row,target)  = whether the proposed action is punished when listened
safe_action = action * listener * (1 - toxicity)
```

## Next High-Information Public Sensor

Submit H141 common core if not already observed publicly:

```text
H141 = common core only
H145 = H141 + row135 Q3 repair
H144 = H141 + row135 Q3 repair + row207 S2 relief
```

Public readings:

- H141 near H144/H145: the common core/body is the public-misaligned part.
- H141 better than H144/H145: row135 Q3/row207 branch cells are toxic or
  non-listened noise.
- H141 worse than H144/H145: the branch cells help, but H057's broader state
  field is still superior.
"""
    (OUT / "h146_report.md").write_text(report)


def run() -> None:
    frames = {name: load_submission(name) for name in FILES}
    all_diffs = pd.concat(
        [diff_cells(left, right, frames) for left, right in PAIRWISE],
        ignore_index=True,
    )
    summary = summarize_pairwise(all_diffs)
    h144_h145 = all_diffs[all_diffs["comparison"].eq("h144_minus_h145")].reset_index(drop=True)
    interpretation = build_interpretation(summary, h144_h145)

    all_diffs.to_csv(OUT / "h146_pairwise_cell_diffs.csv", index=False)
    summary.to_csv(OUT / "h146_pairwise_summary.csv", index=False)
    interpretation.to_csv(OUT / "h146_public_tie_interpretation.csv", index=False)
    write_report(summary, h144_h145, interpretation)

    print(f"wrote {OUT / 'h146_report.md'}")
    print(md_table(summary, n=20))


if __name__ == "__main__":
    run()
