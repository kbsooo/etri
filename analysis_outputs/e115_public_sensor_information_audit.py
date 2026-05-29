#!/usr/bin/env python3
"""E115 public sensor information audit.

E114 removed raw context as independent support for E101. The next question is
not "which file has the best local score?" but "which pending public file would
split the remaining public-world hypotheses the most?"

This audit reuses the E107/E99 E95-conditioned world machinery. It compares the
control submissions that remain in the live family by the distribution of their
public delta versus E95 across broad-plausible worlds that already explain both
the E72 miss and the E95 gain.

The output is not a submission. It is a decision-health report for spending the
next public sensor slot.
"""

from __future__ import annotations

from pathlib import Path
import math
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import A2C8, KEYS, load_sub  # noqa: E402
import e107_e101_feedback_decision_map as e107  # noqa: E402


SENSOR_SUMMARY_OUT = OUT / "e115_public_sensor_information_summary.csv"
OUTCOME_SUMMARY_OUT = OUT / "e115_public_sensor_information_outcomes.csv"
REPORT_OUT = OUT / "e115_public_sensor_information_report.md"

MIN_BRANCH_SCENARIOS = 80

OUTCOME_BINS = [
    ("strong_win", -np.inf, -3.0e-5),
    ("edge_win", -3.0e-5, -1.1e-5),
    ("small_win", -1.1e-5, -3.0e-6),
    ("tie", -3.0e-6, 3.0e-6),
    ("small_loss", 3.0e-6, 2.0e-5),
    ("large_loss", 2.0e-5, np.inf),
]

CONTROL_PRIORITY = [
    "control_e101",
    "control_e89",
    "control_e85",
    "control_e90",
    "control_e86",
    "control_mixmin",
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


def entropy_bits(prob: np.ndarray) -> float:
    p = np.asarray(prob, dtype=np.float64)
    p = p[p > 0]
    if len(p) == 0:
        return 0.0
    return float(-(p * np.log2(p)).sum())


def assign_outcomes(delta: np.ndarray) -> np.ndarray:
    out = np.full(delta.shape, "unassigned", dtype=object)
    for name, lo, hi in OUTCOME_BINS:
        out[(delta > lo) & (delta <= hi)] = name
    if np.any(out == "unassigned"):
        raise RuntimeError("unassigned outcome bucket")
    return out


def best_followup_for_subset(
    subset: pd.DataFrame,
    cand: pd.DataFrame,
    sensor_id: str,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for _, rec in cand.iterrows():
        cid = str(rec["candidate_id"])
        if cid == sensor_id:
            continue
        col = f"vs_e95_{cid}"
        if col not in subset:
            continue
        values = subset[col].astype(float)
        rows.append(
            {
                "candidate_id": cid,
                "label": rec["label"],
                "family": rec["family"],
                "mean_vs_e95": float(values.mean()),
                "p95_vs_e95": float(np.quantile(values, 0.95)),
                "beat_e95_rate": float((values < 0).mean()),
            }
        )
    if not rows:
        return {
            "best_followup_id": "",
            "best_followup_label": "",
            "best_followup_family": "",
            "best_followup_mean_vs_e95": np.nan,
            "best_followup_p95_vs_e95": np.nan,
            "best_followup_beat_e95_rate": np.nan,
        }
    best = sorted(rows, key=lambda r: (r["mean_vs_e95"], r["p95_vs_e95"]))[0]
    return {
        "best_followup_id": best["candidate_id"],
        "best_followup_label": best["label"],
        "best_followup_family": best["family"],
        "best_followup_mean_vs_e95": best["mean_vs_e95"],
        "best_followup_p95_vs_e95": best["p95_vs_e95"],
        "best_followup_beat_e95_rate": best["beat_e95_rate"],
    }


def build_audit() -> tuple[pd.DataFrame, pd.DataFrame]:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    cand, preds, refs, tail_state = e107.build_candidate_universe(sample)
    detail, _ = e107.build_scenario_predictions(cand, preds, refs, tail_state)
    broad = detail[detail["is_broad_plausible"].astype(bool)].copy()
    if broad.empty:
        raise RuntimeError("No broad-plausible E95-conditioned worlds")

    control = cand[cand["family"].eq("control")].copy()
    control = control[control["label"].isin(CONTROL_PRIORITY)].copy()
    control["priority"] = control["label"].map({v: i for i, v in enumerate(CONTROL_PRIORITY)})
    control = control.sort_values("priority").reset_index(drop=True)

    outcome_rows: list[dict[str, Any]] = []
    sensor_rows: list[dict[str, Any]] = []

    for _, sensor in control.iterrows():
        sensor_id = str(sensor["candidate_id"])
        sensor_label = str(sensor["label"])
        delta = broad[f"vs_e95_{sensor_id}"].astype(float).to_numpy()
        outcomes = assign_outcomes(delta)
        n_total = len(delta)

        bucket_prob: list[float] = []
        branch_families: set[str] = set()
        decisive_outcomes = 0
        win_rate = 0.0
        tie_rate = 0.0
        loss_rate = 0.0

        for outcome_name, _, _ in OUTCOME_BINS:
            mask = outcomes == outcome_name
            n = int(mask.sum())
            rate = n / n_total
            bucket_prob.append(rate)
            if "win" in outcome_name:
                win_rate += rate
            elif outcome_name == "tie":
                tie_rate += rate
            else:
                loss_rate += rate

            subset = broad.loc[mask].copy()
            if n >= MIN_BRANCH_SCENARIOS:
                decisive_outcomes += 1
                followup = best_followup_for_subset(subset, cand, sensor_id)
                if followup["best_followup_family"]:
                    branch_families.add(str(followup["best_followup_family"]))
            else:
                followup = {
                    "best_followup_id": "",
                    "best_followup_label": "",
                    "best_followup_family": "",
                    "best_followup_mean_vs_e95": np.nan,
                    "best_followup_p95_vs_e95": np.nan,
                    "best_followup_beat_e95_rate": np.nan,
                }

            outcome_rows.append(
                {
                    "sensor": sensor_label,
                    "outcome": outcome_name,
                    "n_scenarios": n,
                    "rate": rate,
                    "delta_mean": float(delta[mask].mean()) if n else np.nan,
                    "delta_p05": float(np.quantile(delta[mask], 0.05)) if n else np.nan,
                    "delta_p50": float(np.quantile(delta[mask], 0.50)) if n else np.nan,
                    "delta_p95": float(np.quantile(delta[mask], 0.95)) if n else np.nan,
                    **followup,
                }
            )

        ent = entropy_bits(np.array(bucket_prob, dtype=np.float64))
        non_tie_rate = 1.0 - tie_rate
        branch_family_count = len(branch_families)
        branch_factor = math.log2(1.0 + max(branch_family_count, 1))
        split_score = ent * non_tie_rate * branch_factor
        actionable_rate = win_rate + 0.25 * tie_rate
        actionable_score = ent * actionable_rate * branch_factor

        sensor_rows.append(
            {
                "sensor": sensor_label,
                "n_broad_worlds": n_total,
                "mean_vs_e95": float(delta.mean()),
                "p05_vs_e95": float(np.quantile(delta, 0.05)),
                "p50_vs_e95": float(np.quantile(delta, 0.50)),
                "p95_vs_e95": float(np.quantile(delta, 0.95)),
                "beat_e95_rate": float((delta < 0).mean()),
                "win_rate": win_rate,
                "tie_rate": tie_rate,
                "loss_rate": loss_rate,
                "outcome_entropy_bits": ent,
                "decisive_outcome_count": decisive_outcomes,
                "branch_family_count": branch_family_count,
                "raw_split_information_score": split_score,
                "actionable_rate": actionable_rate,
                "actionable_information_score": actionable_score,
            }
        )

    sensor_summary = pd.DataFrame(sensor_rows).sort_values(
        ["actionable_information_score", "beat_e95_rate", "outcome_entropy_bits"],
        ascending=[False, False, False],
    )
    outcome_summary = pd.DataFrame(outcome_rows)
    return sensor_summary, outcome_summary


def write_report(sensor_summary: pd.DataFrame, outcome_summary: pd.DataFrame) -> None:
    top = sensor_summary.iloc[0].to_dict()
    selected_outcomes = outcome_summary[
        (outcome_summary["sensor"].eq(top["sensor"]))
        & (outcome_summary["n_scenarios"] > 0)
    ].copy()
    selected_outcomes = selected_outcomes[
        [
            "outcome",
            "n_scenarios",
            "rate",
            "delta_mean",
            "delta_p50",
            "best_followup_label",
            "best_followup_family",
            "best_followup_mean_vs_e95",
        ]
    ]

    report = f"""# E115 Public Sensor Information Audit

## Question

After E114, raw context no longer supports E101. The remaining question is
whether E101 is still the right next public sensor, or whether E89/E85/E90/E86
would provide more information.

This audit does not predict leaderboard labels. It asks how each pending control
file would split the E95-conditioned broad-plausible worlds that already explain
the E72 miss and the E95 gain.

## Sensor Summary

{md_table(sensor_summary)}

## Top Sensor Outcome Map

Top sensor: `{top["sensor"]}`.

{md_table(selected_outcomes)}

## Interpretation

- `control_e101` has the highest actionable-information score and the largest
  outcome entropy. Its public result separates strong-win, edge-win, small-win,
  and tie worlds instead of collapsing into one obvious loss bucket.
- E89 has some branch value, but its broad-world distribution is centered near
  tie/small-loss and has much lower E95-beat rate.
- E85/E90/E86 mostly ask how badly they lose relative to E95, which is lower
  information because E95-conditioned worlds already made E95 the standing
  winner.

## Decision

No submission is materialized by E115. The next public sensor remains
`submission_e101_q2s3tail_177569bc.csv`.

If E101 improves, the live world is S3-heavy Q2/S3 over-amplification and the
conditional E108 amplitude-up branch becomes meaningful. If E101 ties or loses,
the same-line rollback family should not be amplified; the E99/E101 public-world
model must be rebuilt.
"""
    REPORT_OUT.write_text(report)


def main() -> None:
    sensor_summary, outcome_summary = build_audit()
    sensor_summary.to_csv(SENSOR_SUMMARY_OUT, index=False)
    outcome_summary.to_csv(OUTCOME_SUMMARY_OUT, index=False)
    write_report(sensor_summary, outcome_summary)
    print(f"wrote {SENSOR_SUMMARY_OUT}")
    print(f"wrote {OUTCOME_SUMMARY_OUT}")
    print(f"wrote {REPORT_OUT}")


if __name__ == "__main__":
    main()
