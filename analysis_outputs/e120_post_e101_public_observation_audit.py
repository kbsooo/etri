#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


OUT = Path(__file__).resolve().parent

E95_PUBLIC = 0.5762913298
MIXMIN_PUBLIC = 0.5763066405
E101_PUBLIC = 0.5763003660
E72_PUBLIC = 0.5764077772
A2C8_PUBLIC = 0.5774393210


def read_csv(name: str) -> pd.DataFrame:
    path = OUT / name
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def fmt(x: float, n: int = 10) -> str:
    if np.isinf(x):
        return "inf" if x > 0 else "-inf"
    return f"{x:.{n}f}"


def classify_decoder(decoder: pd.DataFrame, delta: float) -> pd.Series:
    rows = decoder[
        (delta > decoder["delta_vs_e95_lo_exclusive"])
        & (delta <= decoder["delta_vs_e95_hi_inclusive"])
    ]
    if len(rows) != 1:
        raise RuntimeError(f"Expected exactly one decoder row for {delta}, got {len(rows)}")
    return rows.iloc[0]


def maybe_float(row: pd.Series, key: str) -> float:
    if key not in row or pd.isna(row[key]):
        return float("nan")
    return float(row[key])


def main() -> None:
    delta_vs_e95 = E101_PUBLIC - E95_PUBLIC
    delta_vs_mixmin = E101_PUBLIC - MIXMIN_PUBLIC
    delta_vs_e72 = E101_PUBLIC - E72_PUBLIC
    delta_vs_a2c8 = E101_PUBLIC - A2C8_PUBLIC
    e95_gain_vs_mixmin = E95_PUBLIC - MIXMIN_PUBLIC
    e101_remaining_gain_vs_mixmin = E101_PUBLIC - MIXMIN_PUBLIC
    giveback_share = delta_vs_e95 / (MIXMIN_PUBLIC - E95_PUBLIC)
    remaining_share = (MIXMIN_PUBLIC - E101_PUBLIC) / (MIXMIN_PUBLIC - E95_PUBLIC)

    decoder = read_csv("e116_e101_public_feedback_decoder.csv")
    decoded = classify_decoder(decoder, delta_vs_e95)

    scenarios = read_csv("e107_e101_feedback_decision_map_scenarios.csv")
    small_loss_scenario = scenarios[scenarios["outcome"] == "small_loss_1e_minus5"].iloc[0]

    e109 = read_csv("e109_e101_tie_loss_label_world_summary.csv")
    e110_summary = read_csv("e110_e101_negative_branch_nonactive_tail_summary.csv")
    e110_decision = read_csv("e110_e101_negative_branch_nonactive_tail_decision.csv")
    e119 = read_csv("e119_e101_flank_gate_variant_stress_summary.csv")

    active_all = e119[e119["selector"] == "active_all"].iloc[0]
    local_mean_vs_e95 = float(active_all["scale1_mean_vs_e95"])
    local_p95_vs_e95 = float(active_all["scale1_p95_vs_e95"])
    local_beat = float(active_all["scale1_beat"])
    actual_minus_local_mean = delta_vs_e95 - local_mean_vs_e95
    actual_minus_local_p95 = delta_vs_e95 - local_p95_vs_e95

    exact_beats_e95 = E101_PUBLIC < E95_PUBLIC
    exact_beats_mixmin = E101_PUBLIC < MIXMIN_PUBLIC

    small_loss_rows = e109[e109["outcome"] == "small_loss"].copy()
    subject_small_loss = small_loss_rows[small_loss_rows["prior"] == "subject"]
    subject_small_loss_rate = (
        float(subject_small_loss.iloc[0]["world_rate"]) if len(subject_small_loss) else float("nan")
    )

    strict_noncontrol = int(
        e110_decision.loc[
            e110_decision["strategy"].ne("control"), "e110_strict_candidate"
        ].fillna(False).astype(bool).sum()
    )
    sensor_noncontrol = int(
        e110_decision.loc[
            e110_decision["strategy"].ne("control"), "e110_sensor_candidate"
        ].fillna(False).astype(bool).sum()
    )
    flank_dominators = int(e119["dominates_e101"].sum())
    flank_pass_rows = int(e119["pass_rows"].sum())

    summary = pd.DataFrame(
        [
            {
                "observation": "e101_public",
                "submission": "submission_e101_q2s3tail_177569bc.csv",
                "public_lb": E101_PUBLIC,
                "delta_vs_e95": delta_vs_e95,
                "delta_vs_mixmin": delta_vs_mixmin,
                "delta_vs_e72": delta_vs_e72,
                "delta_vs_a2c8": delta_vs_a2c8,
                "exact_beats_e95": exact_beats_e95,
                "exact_beats_mixmin": exact_beats_mixmin,
                "e116_outcome": decoded["outcome"],
                "e116_model_tension": bool(decoded["e107_model_tension"]),
                "e95_gain_giveback_share": giveback_share,
                "e95_gain_remaining_share": remaining_share,
                "local_e101_mean_vs_e95": local_mean_vs_e95,
                "local_e101_p95_vs_e95": local_p95_vs_e95,
                "local_e101_beat_e95_rate": local_beat,
                "actual_minus_local_mean": actual_minus_local_mean,
                "actual_minus_local_p95": actual_minus_local_p95,
                "e107_small_loss_selection_mode": small_loss_scenario["selection_mode"],
                "e107_small_loss_model_tension": bool(small_loss_scenario["model_tension"]),
                "e107_small_loss_n_scenarios": int(small_loss_scenario["n_scenarios"]),
                "e109_subject_small_loss_rate": subject_small_loss_rate,
                "e110_noncontrol_strict_candidates": strict_noncontrol,
                "e110_noncontrol_sensor_candidates": sensor_noncontrol,
                "e119_total_e101_pass_rows": flank_pass_rows,
                "e119_e101_dominating_rows": flank_dominators,
                "decision": "keep_e95_close_e108_rebuild_public_world",
            }
        ]
    )

    summary_path = OUT / "e120_post_e101_public_observation_summary.csv"
    summary.to_csv(summary_path, index=False)

    report = f"""# E120 Post-E101 Public Observation Audit

## Question

E101 was pre-registered as the smallest Q2/S3 tail rollback sensor after E95. Now that the actual public LB is known, does it open the E108/amplitude branch, revive E89/non-active fallback, or force a public-world rebuild?

## Observation

- E101 public LB: `{fmt(E101_PUBLIC)}`
- E95 public LB: `{fmt(E95_PUBLIC)}`
- Mixmin public LB: `{fmt(MIXMIN_PUBLIC)}`
- Delta E101 vs E95: `{delta_vs_e95:+.10f}`
- Delta E101 vs mixmin: `{delta_vs_mixmin:+.10f}`
- Delta E101 vs E72: `{delta_vs_e72:+.10f}`
- Delta E101 vs a2c8: `{delta_vs_a2c8:+.10f}`

E101 is worse than E95 by `{delta_vs_e95:+.10f}`, but still better than mixmin by `{abs(delta_vs_mixmin):.10f}`. It gives back `{giveback_share:.2%}` of E95's gain over mixmin and preserves `{remaining_share:.2%}` of that gain.

## Decoder Result

E116 classifies the exact observation as `{decoded['outcome']}`.

- E116 world update: {decoded['world_update']}
- E116 next action: {decoded['next_action']}
- E116 forbidden action: {decoded['forbidden_action']}

Important nuance: the coarse E116 `small_loss` band as a whole was marked not mixmin-beating, but the exact E101 score does beat mixmin. The branch decision is still loss-side because the active-cell rollback failed to beat the current E95 frontier.

## Stress Contradiction

The pre-feedback local stress expected full active-all E101 to be favorable:

- local mean vs E95: `{local_mean_vs_e95:+.10f}`
- local p95 vs E95: `{local_p95_vs_e95:+.10f}`
- local beat-E95 rate: `{local_beat:.6f}`

The actual public delta is `{delta_vs_e95:+.10f}`. That is `{actual_minus_local_mean:+.10f}` worse than the local mean and `{actual_minus_local_p95:+.10f}` worse than the local p95. This is the main signal: the E99/E101 broad-plausible world model underestimated the loss-side public tail.

## Loss-Side Gates

- E107 small-loss scenario mode: `{small_loss_scenario['selection_mode']}`, model tension `{bool(small_loss_scenario['model_tension'])}`, nearest scenarios `{int(small_loss_scenario['n_scenarios'])}`.
- E109 subject-prior small-loss mass: `{subject_small_loss_rate:.6f}`.
- E110 non-control strict fallback candidates after tie/loss: `{strict_noncontrol}`.
- E110 non-control diagnostic sensors after tie/loss: `{sensor_noncontrol}`.
- E119 E101-pass flank-gate rows: `{flank_pass_rows}`.
- E119 E101-dominating flank-gate rows: `{flank_dominators}`.

These prior loss-side audits line up with the observed branch: E108/higher-alpha, subject-prior gates, flank-gates, active-restored E89/E85, and non-active grafts are closed as automatic followups.

## Belief Update

The current best one-sentence model changes from:

> E95 may have over-amplified a Q2/S3/S3-heavy active-cell tail, and E101 is the cleanest public kill-test.

to:

> E95's hard-tail target-axis surgery remains the standing law; E101 shows that Q2/S3 rollback support exists enough to stay above mixmin, but not enough to beat the frontier, so the loss-side public tail is outside the E99/E101 local stress model.

## Decision

Keep `submission_e95_hardtail_541e3973.csv` as the public frontier. Mark `submission_e101_q2s3tail_177569bc.csv` as a resolved negative sensor, not as a failed random file.

Do not submit E108, E104 higher-alpha, E106 subject-prior masks, E119 flank-gated variants, full E89, or E110 non-active grafts as automatic next files.

The next useful experiment is not another same-family submission. It is an exact post-E101 public-world rebuild that treats E95 and E101 as a two-point hard-tail boundary: E95 is right enough to win, E101 is right enough to beat mixmin, and the missing structure is the small public subset of Q2/S3/S3-heavy tail labels that flips that boundary.
"""

    report_path = OUT / "e120_post_e101_public_observation_report.md"
    report_path.write_text(report, encoding="utf-8")

    print(f"Wrote {summary_path}")
    print(f"Wrote {report_path}")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
