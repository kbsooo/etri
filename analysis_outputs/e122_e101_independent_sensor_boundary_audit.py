#!/usr/bin/env python3
"""E122 independent sensor audit for the E101 small-loss boundary.

SAUNA question:
E121 says E101 lost at a one-high-impact-S3-cell scale. Did any non-public
sensor already available before E101 feedback identify that boundary, or would
using E121 posterior cells as a gate amount to leaderboard-label fitting?
"""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
from typing import Any

import numpy as np
import pandas as pd


OUT = Path(__file__).resolve().parent

E95_PUBLIC = 0.5762913298
MIXMIN_PUBLIC = 0.5763066405
E101_PUBLIC = 0.5763003660
OBS_DELTA = E101_PUBLIC - E95_PUBLIC
TOTAL_TEST_CELLS = 250 * 7

CELLS_FLANK = OUT / "e118_e101_flank_label_support_cells.csv"
CELLS_RAW = OUT / "e114_e101_raw_context_support_cells.csv"
CELLS_POST = OUT / "e121_e101_small_loss_inverse_posterior_cells.csv"
E119_SUMMARY = OUT / "e119_e101_flank_gate_variant_stress_summary.csv"
DECODER = OUT / "e116_e101_public_feedback_decoder.csv"
GENERATED_INPUTS = {
    CELLS_FLANK: OUT / "e118_e101_flank_label_support_audit.py",
    CELLS_POST: OUT / "e121_e101_small_loss_inverse_posterior.py",
}

SUMMARY_OUT = OUT / "e122_e101_independent_sensor_boundary_summary.csv"
CRITICAL_OUT = OUT / "e122_e101_independent_sensor_boundary_critical_summary.csv"
REPORT_OUT = OUT / "e122_e101_independent_sensor_boundary_report.md"

FLANK_PRIORS = [
    "global",
    "subject",
    "prev_beta",
    "next_beta",
    "nearest_beta",
    "both_equal_beta",
    "both_distance_beta",
    "edge_endpoint_beta",
    "nearest_hard085",
    "conflict_flat",
]

RAW_SOURCES = [
    "global_prior_y1",
    "subject_prior_y1",
    "full_subject_prior_y1",
    "raw_plus_prior_y1",
    "validation_gated_raw_y1",
]


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
                vals.append(format(float(value), floatfmt))
            else:
                vals.append(str(value))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def ensure_generated_inputs() -> None:
    """Regenerate ignored intermediate cell tables when running from a fresh checkout."""
    for output, generator in GENERATED_INPUTS.items():
        if output.exists():
            continue
        if not generator.exists():
            raise FileNotFoundError(f"missing generator for {output}: {generator}")
        subprocess.run([sys.executable, str(generator)], check=True)


def classify_delta(decoder: pd.DataFrame, delta: float) -> str:
    rows = decoder[
        (delta > decoder["delta_vs_e95_lo_exclusive"])
        & (delta <= decoder["delta_vs_e95_hi_inclusive"])
    ]
    if len(rows) != 1:
        return "unclassified"
    return str(rows.iloc[0]["outcome"])


def hard_delta_from_support_probability(cells: pd.DataFrame, support_col: str) -> dict[str, Any]:
    support = cells[support_col].to_numpy(dtype=np.float64) >= 0.5
    delta = np.where(
        support,
        cells["support_delta"].to_numpy(dtype=np.float64),
        cells["adverse_delta"].to_numpy(dtype=np.float64),
    )
    flip_share = float(
        cells.loc[support, "flip_benefit"].sum() / max(cells["flip_benefit"].sum(), 1.0e-12)
    )
    return {
        "expected_delta_vs_e95": float(delta.sum() / TOTAL_TEST_CELLS),
        "hard_support_cells": int(support.sum()),
        "hard_support_flip_share": flip_share,
        "top10_support_rate": float(support[cells["flip_rank"].to_numpy(dtype=int) <= 10].mean()),
        "top23_support_rate": float(support[cells["flip_rank"].to_numpy(dtype=int) <= 23].mean()),
        "s3_support_rate": float(support[cells["target"].eq("S3").to_numpy()].mean()),
    }


def add_row(
    rows: list[dict[str, Any]],
    decoder: pd.DataFrame,
    sensor: str,
    family: str,
    mode: str,
    expected_delta: float,
    p_beats_e95: float | None = None,
    hard_support_cells: int | None = None,
    hard_support_flip_share: float | None = None,
    top10_support_rate: float | None = None,
    top23_support_rate: float | None = None,
    s3_support_rate: float | None = None,
    notes: str = "",
) -> None:
    rows.append(
        {
            "sensor": sensor,
            "family": family,
            "mode": mode,
            "expected_delta_vs_e95": expected_delta,
            "error_vs_actual_delta": expected_delta - OBS_DELTA,
            "abs_error_vs_actual_delta": abs(expected_delta - OBS_DELTA),
            "predicted_e116_branch": classify_delta(decoder, expected_delta),
            "actual_branch": classify_delta(decoder, OBS_DELTA),
            "branch_matches_actual": classify_delta(decoder, expected_delta)
            == classify_delta(decoder, OBS_DELTA),
            "p_beats_e95": np.nan if p_beats_e95 is None else p_beats_e95,
            "hard_support_cells": np.nan if hard_support_cells is None else hard_support_cells,
            "hard_support_flip_share": np.nan
            if hard_support_flip_share is None
            else hard_support_flip_share,
            "top10_support_rate": np.nan if top10_support_rate is None else top10_support_rate,
            "top23_support_rate": np.nan if top23_support_rate is None else top23_support_rate,
            "s3_support_rate": np.nan if s3_support_rate is None else s3_support_rate,
            "notes": notes,
        }
    )


def build_sensor_summary(cells: pd.DataFrame, raw: pd.DataFrame, decoder: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    add_row(
        rows,
        decoder,
        sensor="actual_e101_public",
        family="public_observation",
        mode="observed",
        expected_delta=OBS_DELTA,
        notes="external aggregate public LB sensor",
    )

    e119 = read_csv(E119_SUMMARY)
    active_all = e119[e119["selector"].eq("active_all")].iloc[0]
    add_row(
        rows,
        decoder,
        sensor="e119_local_transfer_active_all",
        family="local_tail_transfer",
        mode="scenario_mean",
        expected_delta=float(active_all["scale1_mean_vs_e95"]),
        p_beats_e95=float(active_all["scale1_beat"]),
        notes="pre-public local stress for full E101 active set",
    )
    add_row(
        rows,
        decoder,
        sensor="e119_local_transfer_active_all_p95",
        family="local_tail_transfer",
        mode="scenario_p95",
        expected_delta=float(active_all["scale1_p95_vs_e95"]),
        notes="loss-side p95 still predicted near tie/win, not observed small-loss",
    )

    for prior in FLANK_PRIORS:
        expected = float(cells[f"expected_delta_{prior}"].sum() / TOTAL_TEST_CELLS)
        hard = hard_delta_from_support_probability(cells, f"support_probability_{prior}")
        add_row(
            rows,
            decoder,
            sensor=f"flank_{prior}",
            family="train_flank_prior",
            mode="probability_expectation",
            expected_delta=expected,
            p_beats_e95=np.nan,
            notes="expected hard-label delta from E118 support probabilities",
        )
        add_row(
            rows,
            decoder,
            sensor=f"flank_{prior}",
            family="train_flank_prior",
            mode="hard_p_ge_0p5",
            expected_delta=float(hard.pop("expected_delta_vs_e95")),
            p_beats_e95=np.nan,
            notes="deterministic support if support probability >= 0.5",
            **hard,
        )

    raw = raw.set_index(["sub_idx", "target"])
    for source in RAW_SOURCES:
        source_cells = cells.set_index(["sub_idx", "target"]).copy()
        source_cells[f"{source}_support_probability"] = raw[f"{source}_support_probability"]
        source_cells[f"{source}_expected_delta"] = raw[f"{source}_expected_delta"]
        source_cells = source_cells.reset_index()
        expected = float(source_cells[f"{source}_expected_delta"].sum() / TOTAL_TEST_CELLS)
        hard = hard_delta_from_support_probability(source_cells, f"{source}_support_probability")
        add_row(
            rows,
            decoder,
            sensor=f"raw_{source}",
            family="raw_context_prior",
            mode="probability_expectation",
            expected_delta=expected,
            notes="expected hard-label delta from E114 raw-context support probabilities",
        )
        add_row(
            rows,
            decoder,
            sensor=f"raw_{source}",
            family="raw_context_prior",
            mode="hard_p_ge_0p5",
            expected_delta=float(hard.pop("expected_delta_vs_e95")),
            notes="deterministic support if raw support probability >= 0.5",
            **hard,
        )

    out = pd.DataFrame(rows)
    return out.sort_values(["abs_error_vs_actual_delta", "family", "sensor", "mode"]).reset_index(drop=True)


def build_critical_table(cells: pd.DataFrame, raw: pd.DataFrame, post: pd.DataFrame) -> pd.DataFrame:
    merged = cells.merge(
        raw[
            [
                "sub_idx",
                "target",
                "raw_plus_prior_y1_support_probability",
                "validation_gated_raw_y1_support_probability",
            ]
        ],
        on=["sub_idx", "target"],
        how="left",
    ).merge(
        post[
            [
                "sub_idx",
                "target",
                "posterior_support_mean",
                "posterior_support_std",
                "posterior_support_minus_prior_mean",
            ]
        ],
        on=["sub_idx", "target"],
        how="left",
    )
    merged = merged.sort_values("flip_benefit", ascending=False).reset_index(drop=True)
    merged["flip_rank"] = np.arange(1, len(merged) + 1)
    all_adverse = float(merged["adverse_delta"].sum())
    merged["cum_flip_benefit"] = merged["flip_benefit"].cumsum()
    merged["delta_if_topk_support_per_all"] = (
        all_adverse - merged["cum_flip_benefit"]
    ) / TOTAL_TEST_CELLS
    keep_cols = [
        "flip_rank",
        "sub_idx",
        "target",
        "subject_id",
        "hidden_block_id",
        "lifelog_date",
        "pos_bin",
        "flank_conflict",
        "support_label",
        "flip_benefit",
        "delta_if_topk_support_per_all",
        "support_probability_subject",
        "support_probability_edge_endpoint_beta",
        "support_probability_nearest_beta",
        "support_probability_conflict_flat",
        "raw_plus_prior_y1_support_probability",
        "validation_gated_raw_y1_support_probability",
        "posterior_support_mean",
        "posterior_support_std",
        "posterior_support_minus_prior_mean",
    ]
    return merged.loc[merged["flip_rank"].between(18, 26), keep_cols].reset_index(drop=True)


def main() -> None:
    ensure_generated_inputs()

    cells = read_csv(CELLS_FLANK)
    raw = read_csv(CELLS_RAW)
    post = read_csv(CELLS_POST)
    decoder = read_csv(DECODER)

    cells = cells[cells["active"].astype(bool)].copy()
    cells["flip_rank"] = cells["flip_benefit"].rank(method="first", ascending=False).astype(int)

    summary = build_sensor_summary(cells, raw, decoder)
    summary.to_csv(SUMMARY_OUT, index=False)

    critical = build_critical_table(cells, raw, post)
    critical.to_csv(CRITICAL_OUT, index=False)

    best_predictors = summary[
        summary["mode"].isin(["probability_expectation", "scenario_mean", "scenario_p95"])
    ].head(12)
    hard_rows = summary[summary["mode"].eq("hard_p_ge_0p5")].head(12)

    rank23 = critical[critical["flip_rank"].eq(23)].iloc[0]
    rank22 = critical[critical["flip_rank"].eq(22)].iloc[0]
    local_transfer = summary[summary["sensor"].eq("e119_local_transfer_active_all")].iloc[0]
    subject = summary[
        summary["sensor"].eq("flank_subject")
        & summary["mode"].eq("probability_expectation")
    ].iloc[0]
    raw_plus = summary[
        summary["sensor"].eq("raw_raw_plus_prior_y1")
        & summary["mode"].eq("probability_expectation")
    ].iloc[0]

    report = f"""# E122 E101 Independent Sensor Boundary Audit

## Question

E121 says the observed E101 small-loss boundary is roughly a greedy top-flip support count of `22` instead of `23`. Did any non-public sensor already identify that boundary, or would a same-line post-E101 gate be public-score fitting?

## Sensor Forecasts

Actual E101-vs-E95 public delta: `{OBS_DELTA:+.10f}`.

Best expectation-style sensors by absolute error to the observed delta:

{md_table(best_predictors[['sensor','family','mode','expected_delta_vs_e95','error_vs_actual_delta','predicted_e116_branch','branch_matches_actual','p_beats_e95','notes']], '.9f')}

Best deterministic `p >= 0.5` support gates:

{md_table(hard_rows[['sensor','family','expected_delta_vs_e95','error_vs_actual_delta','predicted_e116_branch','hard_support_cells','hard_support_flip_share','top23_support_rate','s3_support_rate']], '.9f')}

## Critical Boundary Cells

The greedy budget says rank `22` is closest to the observed small loss and rank `23` is the first top-flip support count that would beat E95.

{md_table(critical, '.6f')}

Rank `22` support probability under subject / edge / raw / posterior:

- subject: `{float(rank22['support_probability_subject']):.6f}`
- edge endpoint: `{float(rank22['support_probability_edge_endpoint_beta']):.6f}`
- raw+prior: `{float(rank22['raw_plus_prior_y1_support_probability']):.6f}`
- posterior mean: `{float(rank22['posterior_support_mean']):.6f}`

Rank `23` support probability under subject / edge / raw / posterior:

- subject: `{float(rank23['support_probability_subject']):.6f}`
- edge endpoint: `{float(rank23['support_probability_edge_endpoint_beta']):.6f}`
- raw+prior: `{float(rank23['raw_plus_prior_y1_support_probability']):.6f}`
- posterior mean: `{float(rank23['posterior_support_mean']):.6f}`

## Belief Update

The failed sensor is the local transfer model: it expected E101 mean `{float(local_transfer['expected_delta_vs_e95']):+.9f}` and p95 near the win/tie edge, while public returned `{OBS_DELTA:+.9f}`. The simple train-derived priors are closer to the observed small loss. Subject prior expected `{float(subject['expected_delta_vs_e95']):+.9f}` and raw+prior expected `{float(raw_plus['expected_delta_vs_e95']):+.9f}`.

But this does not create a submission gate. The critical rank `23` cell still has high support under subject/edge/posterior views, and raw is not an independent pro-E101 validator. The visible sensors explain why E101 was not catastrophic, but they do not identify a clean cell to stop before E95 is beaten.

## Decision

Same-line E101 posterior gating remains closed. The strongest current world model is:

> E95 sits on a narrow S3-heavy hard-label boundary. Visible subject/flank priors forecast a small loss better than local tail-transfer, but no non-public sensor identifies the exact high-impact S3 support/adverse cells with enough resolution to justify a new E95-to-E101 submission.

Next highest-information action: either search for a genuinely different non-public sensor of high-impact S3 cell support, or leave the same Q2/S3 rollback line and test a different hidden-structure hypothesis.
"""

    REPORT_OUT.write_text(report, encoding="utf-8")

    print(f"Wrote {SUMMARY_OUT}")
    print(f"Wrote {CRITICAL_OUT}")
    print(f"Wrote {REPORT_OUT}")
    print(best_predictors[["sensor", "expected_delta_vs_e95", "error_vs_actual_delta", "predicted_e116_branch"]].to_string(index=False))


if __name__ == "__main__":
    main()
