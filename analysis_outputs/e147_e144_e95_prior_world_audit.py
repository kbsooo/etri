#!/usr/bin/env python3
"""E147: public-free prior-world audit for E144 versus E95.

E146 showed that E144's tiny retained-tail edge is prior-supported versus E143.
That is not the same as saying E144 as a whole is prior-supported versus the
current public frontier E95. This audit isolates every E144-vs-E95 moved cell
and asks:

Which hidden label world must E144 be betting on, target by target and component
by component? Do train-derived global/subject/flank priors support that world,
or is E144 mainly an anchor/stress candidate whose local gates disagree with
visible label priors?

This is not a submission generator. It is a pre-public interpretation audit for
`submission_e144_activeboundary_d7b4b331.csv`.
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
TOTAL_TEST_CELLS = 250 * 7

CELL_OUT = OUT / "e147_e144_e95_prior_world_cells.csv"
SUMMARY_OUT = OUT / "e147_e144_e95_prior_world_summary.csv"
TARGET_OUT = OUT / "e147_e144_e95_prior_world_by_target.csv"
COMPONENT_OUT = OUT / "e147_e144_e95_prior_world_by_component.csv"
SIM_OUT = OUT / "e147_e144_e95_prior_world_simulation.csv"
REPORT_OUT = OUT / "e147_e144_e95_prior_world_report.md"

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


def build_cells(sample: pd.DataFrame, meta: pd.DataFrame) -> pd.DataFrame:
    p95 = load_sub(E95_FILE, sample)[TARGETS].to_numpy(dtype=np.float64)
    p143 = load_sub(E143_FILE, sample)[TARGETS].to_numpy(dtype=np.float64)
    p144 = load_sub(E144_FILE, sample)[TARGETS].to_numpy(dtype=np.float64)
    dy1, dy0 = hard_loss_deltas(p144, p95)
    moved = np.abs(p144 - p95) > 1.0e-12
    differs_from_e143 = np.abs(p144 - p143) > 1.0e-12

    records: list[dict[str, Any]] = []
    for row_i in range(len(sample)):
        for target_i, target in enumerate(TARGETS):
            if not bool(moved[row_i, target_i]):
                continue
            new_if_y1 = float(dy1[row_i, target_i])
            new_if_y0 = float(dy0[row_i, target_i])
            support_y = int(new_if_y1 < new_if_y0)
            support_delta = min(new_if_y1, new_if_y0)
            adverse_delta = max(new_if_y1, new_if_y0)
            if bool(differs_from_e143[row_i, target_i]):
                component = "e144_fine_tail_delta"
            else:
                component = "inherited_e143_body"
            records.append(
                {
                    "sub_idx": row_i,
                    "target": target,
                    "target_idx": target_i,
                    "component": component,
                    "p_e95": float(p95[row_i, target_i]),
                    "p_e143": float(p143[row_i, target_i]),
                    "p_e144": float(p144[row_i, target_i]),
                    "delta_prob_e144_minus_e95": float(p144[row_i, target_i] - p95[row_i, target_i]),
                    "delta_prob_e144_minus_e143": float(p144[row_i, target_i] - p143[row_i, target_i]),
                    "delta_y1": new_if_y1,
                    "delta_y0": new_if_y0,
                    "support_label": support_y,
                    "support_y_for_e144": support_y,
                    "support_delta": float(support_delta),
                    "adverse_delta": float(adverse_delta),
                    "flip_benefit": float(adverse_delta - support_delta),
                    "e144_better_if_y1": bool(new_if_y1 < 0.0),
                    "e144_better_if_y0": bool(new_if_y0 < 0.0),
                    "differs_from_e143": bool(differs_from_e143[row_i, target_i]),
                    "moves_prob_up": bool(p144[row_i, target_i] > p95[row_i, target_i]),
                    "moves_prob_down": bool(p144[row_i, target_i] < p95[row_i, target_i]),
                }
            )
    cells = pd.DataFrame(records)
    cells = cells.merge(meta, on="sub_idx", how="left", validate="many_to_one")
    if cells.empty:
        raise RuntimeError("E144 and E95 have no differing cells")
    cells["edge_like"] = cells["pos_bin"].isin(["left_edge", "right_edge", "near_edge", "single"])
    cells["flip_rank"] = cells["flip_benefit"].rank(method="first", ascending=False).astype(int)
    return cells


def add_prior_rollups(cells: pd.DataFrame) -> pd.DataFrame:
    out = cells.copy()
    # e118.add_support_priors already adds p_y1, support_probability, and expected_delta.
    for prior in PRIORS:
        out[f"hard_support_{prior}"] = out[f"support_probability_{prior}"].to_numpy(dtype=np.float64) >= 0.5
    return out


def simulate_prior(cells: pd.DataFrame, prior: str) -> dict[str, Any]:
    seed_offset = sum((i + 1) * ord(ch) for i, ch in enumerate(prior))
    rng = np.random.default_rng(RNG_SEED + seed_offset)
    p_y1 = cells[f"p_y1_{prior}"].to_numpy(dtype=np.float64)
    labels = rng.random((N_SIMS, len(cells))) < p_y1[None, :]
    d1 = cells["delta_y1"].to_numpy(dtype=np.float64)
    d0 = cells["delta_y0"].to_numpy(dtype=np.float64)
    totals = np.where(labels, d1[None, :], d0[None, :]).sum(axis=1) / TOTAL_TEST_CELLS
    support_y = cells["support_y_for_e144"].to_numpy(dtype=bool)
    support = labels == support_y[None, :]
    flip = cells["flip_benefit"].to_numpy(dtype=np.float64)
    flip_share = (support * flip[None, :]).sum(axis=1) / max(float(flip.sum()), EPS)
    return {
        "prior": prior,
        "sim_mean_delta_e144_minus_e95": float(totals.mean()),
        "sim_p05": float(np.quantile(totals, 0.05)),
        "sim_p50": float(np.quantile(totals, 0.50)),
        "sim_p95": float(np.quantile(totals, 0.95)),
        "p_e144_beats_e95": float((totals < 0.0).mean()),
        "sim_expected_lb_if_full_test_prior": float(E95_PUBLIC + totals.mean()),
        "support_cells_mean": float(support.sum(axis=1).mean()),
        "support_flip_share_mean": float(flip_share.mean()),
        "top20_support_rate": float(support[:, cells["flip_rank"].to_numpy(dtype=int) <= 20].mean()),
        "fine_tail_support_rate": float(support[:, cells["component"].eq("e144_fine_tail_delta").to_numpy()].mean()),
        "body_support_rate": float(support[:, cells["component"].eq("inherited_e143_body").to_numpy()].mean()),
    }


def summarize(cells: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    summary_rows: list[dict[str, Any]] = []
    target_rows: list[dict[str, Any]] = []
    component_rows: list[dict[str, Any]] = []
    for prior in PRIORS:
        exp = cells[f"expected_delta_{prior}"].to_numpy(dtype=np.float64)
        hard = cells[f"hard_support_{prior}"].to_numpy(dtype=bool)
        summary_rows.append(
            {
                "prior": prior,
                "expected_delta_e144_minus_e95": float(exp.sum() / TOTAL_TEST_CELLS),
                "expected_delta_total": float(exp.sum()),
                "expected_lb_if_full_test_prior": float(E95_PUBLIC + exp.sum() / TOTAL_TEST_CELLS),
                "prefers_e144": bool(exp.sum() < 0.0),
                "hard_support_cells": int(hard.sum()),
                "hard_support_flip_share": float(
                    cells.loc[hard, "flip_benefit"].sum() / max(cells["flip_benefit"].sum(), EPS)
                ),
                "mean_support_probability": float(cells[f"support_probability_{prior}"].mean()),
                "top20_support_rate": float(hard[cells["flip_rank"].to_numpy(dtype=int) <= 20].mean()),
                "fine_tail_hard_support_rate": float(hard[cells["component"].eq("e144_fine_tail_delta").to_numpy()].mean()),
                "body_hard_support_rate": float(hard[cells["component"].eq("inherited_e143_body").to_numpy()].mean()),
            }
        )
        for target, group in cells.groupby("target", sort=False):
            gexp = group[f"expected_delta_{prior}"].sum()
            ghard = group[f"hard_support_{prior}"].to_numpy(dtype=bool)
            target_rows.append(
                {
                    "prior": prior,
                    "target": target,
                    "cells": int(len(group)),
                    "expected_delta_per_all": float(gexp / TOTAL_TEST_CELLS),
                    "expected_delta_total": float(gexp),
                    "prefers_e144": bool(gexp < 0.0),
                    "hard_support_cells": int(ghard.sum()),
                    "mean_support_probability": float(group[f"support_probability_{prior}"].mean()),
                    "flip_benefit_total": float(group["flip_benefit"].sum()),
                }
            )
        for component, group in cells.groupby("component", sort=False):
            gexp = group[f"expected_delta_{prior}"].sum()
            ghard = group[f"hard_support_{prior}"].to_numpy(dtype=bool)
            component_rows.append(
                {
                    "prior": prior,
                    "component": component,
                    "cells": int(len(group)),
                    "expected_delta_per_all": float(gexp / TOTAL_TEST_CELLS),
                    "expected_delta_total": float(gexp),
                    "prefers_e144": bool(gexp < 0.0),
                    "hard_support_cells": int(ghard.sum()),
                    "mean_support_probability": float(group[f"support_probability_{prior}"].mean()),
                    "flip_benefit_total": float(group["flip_benefit"].sum()),
                }
            )
    summary = pd.DataFrame(summary_rows).sort_values("expected_delta_e144_minus_e95")
    target = pd.DataFrame(target_rows).sort_values(["prior", "expected_delta_per_all"])
    component = pd.DataFrame(component_rows).sort_values(["prior", "expected_delta_per_all"])
    sim = pd.DataFrame([simulate_prior(cells, prior) for prior in PRIORS]).sort_values(
        "sim_mean_delta_e144_minus_e95"
    )
    return summary, target, component, sim


def write_report(cells: pd.DataFrame, summary: pd.DataFrame, target: pd.DataFrame, component: pd.DataFrame, sim: pd.DataFrame) -> None:
    target_counts = (
        cells.groupby("target")
        .agg(cells=("target", "size"), rows=("sub_idx", "nunique"), flip_benefit=("flip_benefit", "sum"))
        .reset_index()
        .sort_values("cells", ascending=False)
    )
    component_counts = (
        cells.groupby("component")
        .agg(cells=("component", "size"), rows=("sub_idx", "nunique"), flip_benefit=("flip_benefit", "sum"))
        .reset_index()
    )
    nearest_target = target[target["prior"].eq("nearest_hard085")].copy()
    subject_target = target[target["prior"].eq("subject")].copy()
    nearest_component = component[component["prior"].eq("nearest_hard085")].copy()
    best_prior = summary.iloc[0]
    worst_prior = summary.iloc[-1]
    e144_prior_count = int(summary["prefers_e144"].sum())
    top_cells = cells.sort_values("flip_benefit", ascending=False).head(15)[
        [
            "sub_idx",
            "subject_id",
            "lifelog_date",
            "target",
            "component",
            "p_e95",
            "p_e144",
            "support_y_for_e144",
            "flip_benefit",
            "pos_bin",
            "flank_conflict",
            "support_probability_subject",
            "support_probability_nearest_hard085",
        ]
    ]

    if e144_prior_count == len(summary):
        read = "visible priors broadly support E144 over E95"
    elif e144_prior_count == 0:
        read = "visible priors broadly oppose E144 over E95"
    else:
        read = "visible priors are split, so E144 depends on anchor/stress structure beyond simple priors"

    lines = [
        "# E147 E144/E95 Prior-World Audit",
        "",
        "## Question",
        "",
        "E146 showed E144's fine S3 tail is prior-supported versus E143. E147 asks the larger question: do public-free global/subject/flank priors support E144 as a whole versus the current E95 frontier?",
        "",
        "## Cell Anatomy",
        "",
        f"- E144-vs-E95 moved cells: `{len(cells)}`",
        f"- rows touched: `{cells['sub_idx'].nunique()}`",
        f"- subjects touched: `{cells['subject_id'].nunique()}`",
        f"- edge-like cells: `{int(cells['edge_like'].sum())}`",
        f"- flank-conflict cells: `{int(cells['flank_conflict'].sum())}`",
        f"- total flip benefit: `{cells['flip_benefit'].sum():.12f}`",
        "",
        "Target counts:",
        "",
        md_table(target_counts, ".6f"),
        "",
        "Component counts:",
        "",
        md_table(component_counts, ".6f"),
        "",
        "## Prior Summary",
        "",
        md_table(summary, ".12f"),
        "",
        "## Simulation Summary",
        "",
        md_table(sim, ".12f"),
        "",
        "## Nearest-Hard Target Contributions",
        "",
        md_table(nearest_target, ".12f"),
        "",
        "## Subject-Prior Target Contributions",
        "",
        md_table(subject_target, ".12f"),
        "",
        "## Nearest-Hard Component Contributions",
        "",
        md_table(nearest_component, ".12f"),
        "",
        "## Highest Impact Cells",
        "",
        md_table(top_cells, ".6f"),
        "",
        "## Interpretation",
        "",
        f"- Priors preferring E144 over E95: `{e144_prior_count}/{len(summary)}`.",
        f"- Best expected prior: `{best_prior['prior']}` with delta `{best_prior['expected_delta_e144_minus_e95']:.12f}`.",
        f"- Worst expected prior: `{worst_prior['prior']}` with delta `{worst_prior['expected_delta_e144_minus_e95']:.12f}`.",
        f"- Read: {read}.",
        "",
        "## Decision",
        "",
        "No submission is created. E144 remains the next public sensor. This audit defines what that sensor is betting on: not just the E146 fine-tail delta, but the full inherited residual body versus E95. If public feedback disagrees with the visible-prior direction, the next analysis should identify the target/component whose prior contribution failed rather than tune the whole E142/E143/E144 family.",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n")


def main() -> None:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    train = train.sort_values(hbr.SORT_KEY).reset_index(drop=True)
    sample = sample.sort_values(hbr.KEY).reset_index(drop=True)

    meta = e102.build_hidden_row_meta(train, sample)
    cells = build_cells(sample, meta)
    cells = e118.add_flank_context(cells, train)
    cells = e118.add_support_priors(cells)
    cells = add_prior_rollups(cells)
    summary, target, component, sim = summarize(cells)

    cells.to_csv(CELL_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    target.to_csv(TARGET_OUT, index=False)
    component.to_csv(COMPONENT_OUT, index=False)
    sim.to_csv(SIM_OUT, index=False)
    write_report(cells, summary, target, component, sim)

    print(
        {
            "cells": str(CELL_OUT),
            "summary": str(SUMMARY_OUT),
            "target": str(TARGET_OUT),
            "component": str(COMPONENT_OUT),
            "simulation": str(SIM_OUT),
            "report": str(REPORT_OUT),
            "moved_cells": int(len(cells)),
            "priors_preferring_e144": int(summary["prefers_e144"].sum()),
        }
    )
    print(summary.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
