#!/usr/bin/env python3
"""E146: public-free prior audit for the E144-vs-E143 fine tail.

E144 is the current next public sensor, but its local edge over E143 is tiny.
This audit isolates only the cells where E144 differs from E143 and asks a
smaller question:

Do global, subject, and visible train-flank priors prefer the E144 retained
active-tail movement, or do they prefer E143's stricter rollback?

No submission is created here. The output is a pre-public interpretation aid:
if E144 later loses narrowly, this audit decides whether E143 is an evidence
based contrast or only a same-family rescue.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

import hidden_block_rate_reconstruction_audit as hbr  # noqa: E402
import e102_e101_active_cell_structure_audit as e102  # noqa: E402
import e118_e101_flank_label_support_audit as e118  # noqa: E402
from public_anchor_bottleneck_decomposition import TARGETS, load_sub  # noqa: E402


E95_FILE = "submission_e95_hardtail_541e3973.csv"
E143_FILE = "submission_e143_activeq2s3repair_68ca656f.csv"
E144_FILE = "submission_e144_activeboundary_d7b4b331.csv"

E95_PUBLIC = 0.5762913298
E101_PUBLIC = 0.5763003660
MIXMIN_PUBLIC = 0.5763066405
TOTAL_TEST_CELLS = 250 * 7

CELL_OUT = OUT / "e146_e144_e143_tail_prior_cells.csv"
SUMMARY_OUT = OUT / "e146_e144_e143_tail_prior_summary.csv"
SIM_OUT = OUT / "e146_e144_e143_tail_prior_simulation.csv"
REPORT_OUT = OUT / "e146_e144_e143_tail_prior_report.md"

PRIORS = [
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
RNG_SEED = 20260530
N_SIMS = 200_000
EPS = 1.0e-12


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


def hard_loss_deltas(p_new: np.ndarray, p_base: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    p_new = np.clip(np.asarray(p_new, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)
    p_base = np.clip(np.asarray(p_base, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)
    delta_y1 = -np.log(p_new) + np.log(p_base)
    delta_y0 = -np.log(1.0 - p_new) + np.log(1.0 - p_base)
    return delta_y1, delta_y0


def build_tail_cells(sample: pd.DataFrame, meta: pd.DataFrame) -> pd.DataFrame:
    p95 = load_sub(E95_FILE, sample)[TARGETS].to_numpy(dtype=np.float64)
    p143 = load_sub(E143_FILE, sample)[TARGETS].to_numpy(dtype=np.float64)
    p144 = load_sub(E144_FILE, sample)[TARGETS].to_numpy(dtype=np.float64)
    dy1, dy0 = hard_loss_deltas(p144, p143)
    diff = np.abs(p144 - p143) > 1.0e-12

    records: list[dict[str, Any]] = []
    for row_i in range(len(sample)):
        for target_i, target in enumerate(TARGETS):
            if not bool(diff[row_i, target_i]):
                continue
            new_if_y1 = float(dy1[row_i, target_i])
            new_if_y0 = float(dy0[row_i, target_i])
            support_y = int(new_if_y1 < new_if_y0)
            support_delta = min(new_if_y1, new_if_y0)
            adverse_delta = max(new_if_y1, new_if_y0)
            base = {
                "sub_idx": row_i,
                "target": target,
                "target_idx": target_i,
                "p_e95": float(p95[row_i, target_i]),
                "p_e143": float(p143[row_i, target_i]),
                "p_e144": float(p144[row_i, target_i]),
                "delta_prob_e144_minus_e143": float(p144[row_i, target_i] - p143[row_i, target_i]),
                "delta_y1_e144_minus_e143": new_if_y1,
                "delta_y0_e144_minus_e143": new_if_y0,
                "delta_y1": new_if_y1,
                "delta_y0": new_if_y0,
                "support_label": support_y,
                "support_y_for_e144": support_y,
                "support_delta": float(support_delta),
                "adverse_delta": float(adverse_delta),
                "flip_benefit": float(adverse_delta - support_delta),
                "e144_better_if_y1": bool(new_if_y1 < 0.0),
                "e144_better_if_y0": bool(new_if_y0 < 0.0),
                "moved_toward_e95": bool(
                    abs(p144[row_i, target_i] - p95[row_i, target_i])
                    < abs(p143[row_i, target_i] - p95[row_i, target_i])
                ),
                "moved_away_from_e95": bool(
                    abs(p144[row_i, target_i] - p95[row_i, target_i])
                    > abs(p143[row_i, target_i] - p95[row_i, target_i])
                ),
            }
            records.append(base)

    cells = pd.DataFrame(records)
    cells = cells.merge(meta, on="sub_idx", how="left", validate="many_to_one")
    if cells.empty:
        raise RuntimeError("E144 and E143 have no differing cells")
    cells["edge_like"] = cells["pos_bin"].isin(["left_edge", "right_edge", "near_edge", "single"])
    cells["flip_rank"] = cells["flip_benefit"].rank(method="first", ascending=False).astype(int)
    return cells


def add_expected_prior_deltas(cells: pd.DataFrame) -> pd.DataFrame:
    out = cells.copy()
    for prior in PRIORS:
        p_y1 = out[f"p_y1_{prior}"].to_numpy(dtype=np.float64)
        exp_delta = p_y1 * out["delta_y1_e144_minus_e143"].to_numpy(dtype=np.float64)
        exp_delta += (1.0 - p_y1) * out["delta_y0_e144_minus_e143"].to_numpy(dtype=np.float64)
        support_p = np.where(out["support_y_for_e144"].to_numpy(dtype=int) == 1, p_y1, 1.0 - p_y1)
        out[f"expected_delta_{prior}"] = exp_delta
        out[f"support_probability_{prior}"] = support_p
        out[f"hard_support_{prior}"] = support_p >= 0.5
    return out


def simulate_prior(cells: pd.DataFrame, prior: str) -> dict[str, Any]:
    seed_offset = sum((i + 1) * ord(ch) for i, ch in enumerate(prior))
    rng = np.random.default_rng(RNG_SEED + seed_offset)
    p_y1 = cells[f"p_y1_{prior}"].to_numpy(dtype=np.float64)
    labels = rng.random((N_SIMS, len(cells))) < p_y1[None, :]
    d1 = cells["delta_y1_e144_minus_e143"].to_numpy(dtype=np.float64)
    d0 = cells["delta_y0_e144_minus_e143"].to_numpy(dtype=np.float64)
    totals = np.where(labels, d1[None, :], d0[None, :]).sum(axis=1) / TOTAL_TEST_CELLS
    support_y = cells["support_y_for_e144"].to_numpy(dtype=bool)
    support = labels == support_y[None, :]
    flip = cells["flip_benefit"].to_numpy(dtype=np.float64)
    flip_share = (support * flip[None, :]).sum(axis=1) / max(float(flip.sum()), EPS)
    return {
        "prior": prior,
        "sim_mean_delta_e144_minus_e143": float(totals.mean()),
        "sim_p05": float(np.quantile(totals, 0.05)),
        "sim_p50": float(np.quantile(totals, 0.50)),
        "sim_p95": float(np.quantile(totals, 0.95)),
        "p_e144_beats_e143": float((totals < 0.0).mean()),
        "support_cells_mean": float(support.sum(axis=1).mean()),
        "support_flip_share_mean": float(flip_share.mean()),
        "top10_support_rate": float(support[:, cells["flip_rank"].to_numpy(dtype=int) <= 10].mean()),
        "edge_support_rate": float(support[:, cells["edge_like"].to_numpy(dtype=bool)].mean()),
    }


def summarize_priors(cells: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[dict[str, Any]] = []
    for prior in PRIORS:
        exp = cells[f"expected_delta_{prior}"].to_numpy(dtype=np.float64)
        hard = cells[f"hard_support_{prior}"].to_numpy(dtype=bool)
        flip_share = float(cells.loc[hard, "flip_benefit"].sum() / max(cells["flip_benefit"].sum(), EPS))
        rows.append(
            {
                "prior": prior,
                "expected_delta_e144_minus_e143": float(exp.sum() / TOTAL_TEST_CELLS),
                "expected_delta_total": float(exp.sum()),
                "hard_support_cells": int(hard.sum()),
                "hard_support_flip_share": flip_share,
                "mean_support_probability": float(cells[f"support_probability_{prior}"].mean()),
                "top10_support_rate": float(hard[cells["flip_rank"].to_numpy(dtype=int) <= 10].mean()),
                "edge_support_rate": float(hard[cells["edge_like"].to_numpy(dtype=bool)].mean()),
                "prefers_e144": bool(exp.sum() < 0.0),
            }
        )
    summary = pd.DataFrame(rows).sort_values("expected_delta_e144_minus_e143")
    sim = pd.DataFrame([simulate_prior(cells, prior) for prior in PRIORS]).sort_values(
        "sim_mean_delta_e144_minus_e143"
    )
    return summary, sim


def write_report(cells: pd.DataFrame, summary: pd.DataFrame, sim: pd.DataFrame) -> None:
    target_counts = cells.groupby("target").size().reset_index(name="cells")
    direction_counts = cells.groupby(["target", "moved_toward_e95", "moved_away_from_e95"]).size().reset_index(name="cells")
    top_cells = cells.sort_values("flip_benefit", ascending=False).head(12)[
        [
            "sub_idx",
            "subject_id",
            "lifelog_date",
            "target",
            "p_e143",
            "p_e144",
            "support_y_for_e144",
            "flip_benefit",
            "pos_bin",
            "flank_conflict",
            "support_probability_subject",
            "support_probability_edge_endpoint_beta",
        ]
    ]

    best_prior = summary.iloc[0]
    worst_prior = summary.iloc[-1]
    best_sim = sim.iloc[0]
    e144_prior_count = int(summary["prefers_e144"].sum())
    branch_note = (
        "independent priors mostly support the retained E144 tail"
        if e144_prior_count >= 6
        else "independent priors do not broadly support E144 over E143"
    )
    decision_note = (
        "Because the priors support E144, a narrow E144 loss should not automatically promote E143 as a safer expected-score file; it would mainly say that public S3 tail labels are more adverse than visible priors. E143 remains a clean contrast only if the public slot is meant to test fine-tail retention itself."
        if e144_prior_count >= 6
        else "Because the priors do not support E144 broadly, a narrow E144 loss would make E143 a stronger conservative contrast before any looser E142/E144-style followup."
    )

    lines = [
        "# E146 E144/E143 Tail Prior Audit",
        "",
        "## Question",
        "",
        "E144 beats E143 locally by only `~1.75e-7`. This audit isolates the cells where E144 differs from E143 and asks whether public-free global/subject/flank priors prefer E144's retained active-tail movement.",
        "",
        "## Cell Anatomy",
        "",
        f"- differing cells: `{len(cells)}`",
        f"- rows touched: `{cells['sub_idx'].nunique()}`",
        f"- subjects touched: `{cells['subject_id'].nunique()}`",
        f"- edge-like cells: `{int(cells['edge_like'].sum())}`",
        f"- flank-conflict cells: `{int(cells['flank_conflict'].sum())}`",
        f"- total flip benefit over differing cells: `{cells['flip_benefit'].sum():.12f}`",
        "",
        "Target counts:",
        "",
        md_table(target_counts, ".6f"),
        "",
        "Direction counts:",
        "",
        md_table(direction_counts, ".6f"),
        "",
        "## Prior Summary",
        "",
        md_table(summary, ".12f"),
        "",
        "## Prior Simulation",
        "",
        md_table(sim, ".12f"),
        "",
        "## Highest Impact Cells",
        "",
        md_table(top_cells, ".6f"),
        "",
        "## Interpretation",
        "",
        f"- Priors preferring E144 over E143: `{e144_prior_count}/{len(summary)}`.",
        f"- Best expected prior: `{best_prior['prior']}` with delta `{best_prior['expected_delta_e144_minus_e143']:.12f}`.",
        f"- Worst expected prior: `{worst_prior['prior']}` with delta `{worst_prior['expected_delta_e144_minus_e143']:.12f}`.",
        f"- Best simulated prior: `{best_sim['prior']}` with `p_e144_beats_e143={best_sim['p_e144_beats_e143']:.6f}`.",
        f"- Read: {branch_note}.",
        "",
        "## Decision",
        "",
        f"No submission is created. E144 remains the next public sensor because it passes the pre-registered strict gates. {decision_note}",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n")


def main() -> None:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    train = train.sort_values(hbr.SORT_KEY).reset_index(drop=True)
    sample = sample.sort_values(hbr.KEY).reset_index(drop=True)

    meta = e102.build_hidden_row_meta(train, sample)
    cells = build_tail_cells(sample, meta)
    cells = e118.add_flank_context(cells, train)
    cells = e118.add_support_priors(cells)
    cells = add_expected_prior_deltas(cells)
    summary, sim = summarize_priors(cells)

    cells.to_csv(CELL_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    sim.to_csv(SIM_OUT, index=False)
    write_report(cells, summary, sim)

    print(
        {
            "cells": str(CELL_OUT),
            "summary": str(SUMMARY_OUT),
            "simulation": str(SIM_OUT),
            "report": str(REPORT_OUT),
            "differing_cells": int(len(cells)),
            "priors_preferring_e144": int(summary["prefers_e144"].sum()),
        }
    )
    print(summary.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
