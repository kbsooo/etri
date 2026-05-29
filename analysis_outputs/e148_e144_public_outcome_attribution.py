#!/usr/bin/env python3
"""E148: pre-public attribution decoder for possible E144 outcomes.

E145 fixes public-score bands for the pending E144 submission. E147 says the
whole E144-vs-E95 movement is visible-prior supported, while S3/Q3 remain the
target-local stress axes.

This script joins those two facts. Before E144 public feedback is known, it asks:

If the hidden public labels land E144 in each E145 band, which target/component
support pattern would have produced that observation under train-derived priors?

The output is an interpretation guardrail. It creates no submission and does not
fit public LB. It pre-registers which parts of E144 should be blamed or credited
for each possible feedback band.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

CELLS_IN = OUT / "e147_e144_e95_prior_world_cells.csv"
BANDS_IN = OUT / "e145_e144_public_feedback_decoder.csv"

OUTCOME_OUT = OUT / "e148_e144_public_outcome_attribution_rates.csv"
GROUP_OUT = OUT / "e148_e144_public_outcome_group_attribution.csv"
TOP_OUT = OUT / "e148_e144_public_outcome_top_responsibility.csv"
REPORT_OUT = OUT / "e148_e144_public_outcome_attribution_report.md"

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

TOTAL_TEST_CELLS = 250 * 7
N_SIMS = 250_000
RNG_SEED = 20260530 + 148
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


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, np.integer)):
        return bool(value)
    return str(value).strip().lower() == "true"


def assign_outcomes(delta: np.ndarray, bands: pd.DataFrame) -> np.ndarray:
    outcome = np.full(delta.shape, "__unassigned__", dtype=object)
    for row in bands.itertuples(index=False):
        lo = float(row.delta_vs_e95_lo_exclusive)
        hi = float(row.delta_vs_e95_hi_inclusive)
        mask = (delta > lo) & (delta <= hi)
        outcome[mask] = row.outcome
    if np.any(outcome == "__unassigned__"):
        raise RuntimeError("Some simulated deltas did not map to an E145 outcome band")
    return outcome


def build_group_masks(cells: pd.DataFrame) -> list[tuple[str, str, np.ndarray]]:
    groups: list[tuple[str, str, np.ndarray]] = []
    for target in sorted(cells["target"].unique()):
        groups.append(("target", str(target), cells["target"].eq(target).to_numpy()))
    for component in sorted(cells["component"].unique()):
        groups.append(("component", str(component), cells["component"].eq(component).to_numpy()))
    for (target, component), _ in cells.groupby(["target", "component"], sort=True):
        mask = cells["target"].eq(target).to_numpy() & cells["component"].eq(component).to_numpy()
        groups.append(("target_component", f"{target}:{component}", mask))
    return groups


def simulate_one_prior(
    cells: pd.DataFrame,
    bands: pd.DataFrame,
    prior: str,
    group_masks: list[tuple[str, str, np.ndarray]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    seed_offset = sum((i + 1) * ord(ch) for i, ch in enumerate(prior))
    rng = np.random.default_rng(RNG_SEED + seed_offset)

    p_y1 = cells[f"p_y1_{prior}"].to_numpy(dtype=np.float64)
    labels = rng.random((N_SIMS, len(cells))) < p_y1[None, :]
    d1 = cells["delta_y1"].to_numpy(dtype=np.float64)
    d0 = cells["delta_y0"].to_numpy(dtype=np.float64)
    contrib = np.where(labels, d1[None, :], d0[None, :])
    delta = contrib.sum(axis=1) / TOTAL_TEST_CELLS
    outcomes = assign_outcomes(delta, bands)

    support_y = cells["support_y_for_e144"].to_numpy(dtype=bool)
    support = labels == support_y[None, :]
    flip = cells["flip_benefit"].to_numpy(dtype=np.float64)

    outcome_rows: list[dict[str, Any]] = []
    group_rows: list[dict[str, Any]] = []
    top_rows: list[dict[str, Any]] = []

    unconditional_support = support.mean(axis=0)
    unconditional_delta_by_cell = contrib.mean(axis=0) / TOTAL_TEST_CELLS
    unconditional_flip_share = (support * flip[None, :]).sum(axis=1) / max(float(flip.sum()), EPS)

    for band in bands.itertuples(index=False):
        outcome = band.outcome
        idx = outcomes == outcome
        n_worlds = int(idx.sum())
        if n_worlds:
            d = delta[idx]
            s = support[idx]
            c = contrib[idx]
            support_cells = s.sum(axis=1)
            support_flip_share = (s * flip[None, :]).sum(axis=1) / max(float(flip.sum()), EPS)
            top20_mask = cells["flip_rank"].to_numpy(dtype=int) <= 20
            fine_mask = cells["component"].eq("e144_fine_tail_delta").to_numpy()
            body_mask = cells["component"].eq("inherited_e143_body").to_numpy()
            outcome_rows.append(
                {
                    "prior": prior,
                    "outcome": outcome,
                    "worlds": n_worlds,
                    "world_rate": float(n_worlds / N_SIMS),
                    "mean_delta_vs_e95": float(d.mean()),
                    "p05_delta": float(np.quantile(d, 0.05)),
                    "p50_delta": float(np.quantile(d, 0.50)),
                    "p95_delta": float(np.quantile(d, 0.95)),
                    "support_cells_mean": float(support_cells.mean()),
                    "support_flip_share_mean": float(support_flip_share.mean()),
                    "support_flip_share_lift": float(support_flip_share.mean() - unconditional_flip_share.mean()),
                    "top20_support_rate": float(s[:, top20_mask].mean()),
                    "fine_tail_support_rate": float(s[:, fine_mask].mean()),
                    "body_support_rate": float(s[:, body_mask].mean()),
                }
            )
        else:
            outcome_rows.append(
                {
                    "prior": prior,
                    "outcome": outcome,
                    "worlds": 0,
                    "world_rate": 0.0,
                    "mean_delta_vs_e95": np.nan,
                    "p05_delta": np.nan,
                    "p50_delta": np.nan,
                    "p95_delta": np.nan,
                    "support_cells_mean": np.nan,
                    "support_flip_share_mean": np.nan,
                    "support_flip_share_lift": np.nan,
                    "top20_support_rate": np.nan,
                    "fine_tail_support_rate": np.nan,
                    "body_support_rate": np.nan,
                }
            )
            continue

        beats_e95 = parse_bool(band.beats_e95)
        direction = "credit" if beats_e95 else "blame"
        local_rows: list[dict[str, Any]] = []
        for group_kind, group_name, mask in group_masks:
            if not bool(mask.any()):
                continue
            conditional_support_rate = float(s[:, mask].mean())
            unconditional_support_rate = float(unconditional_support[mask].mean())
            conditional_delta = float(c[:, mask].sum(axis=1).mean() / TOTAL_TEST_CELLS)
            unconditional_delta = float(unconditional_delta_by_cell[mask].sum())
            conditional_flip_share_group = float((s[:, mask] * flip[mask][None, :]).sum(axis=1).mean() / max(float(flip[mask].sum()), EPS))
            row = {
                "prior": prior,
                "outcome": outcome,
                "world_rate": float(n_worlds / N_SIMS),
                "group_kind": group_kind,
                "group": group_name,
                "cells": int(mask.sum()),
                "direction": direction,
                "conditional_support_rate": conditional_support_rate,
                "unconditional_support_rate": unconditional_support_rate,
                "support_rate_lift": conditional_support_rate - unconditional_support_rate,
                "conditional_delta_per_all": conditional_delta,
                "unconditional_delta_per_all": unconditional_delta,
                "delta_shift_per_all": conditional_delta - unconditional_delta,
                "conditional_flip_share_group": conditional_flip_share_group,
            }
            group_rows.append(row)
            local_rows.append(row)

        # Credit wins by the groups that actually contribute the most negative
        # conditional LogLoss delta in that band. Blame non-wins by the groups
        # that contribute the most positive conditional delta. This is different
        # from support-rate lift versus the prior baseline: a micro-win can be
        # worse than prior expectation while still having specific groups that
        # carry the score below E95.
        ranked = sorted(
            local_rows,
            key=lambda r: r["conditional_delta_per_all"],
            reverse=not beats_e95,
        )
        for rank, row in enumerate(ranked[:8], start=1):
            top_rows.append(
                {
                    "prior": prior,
                    "outcome": outcome,
                    "rank": rank,
                    "direction": direction,
                    "group_kind": row["group_kind"],
                    "group": row["group"],
                    "cells": row["cells"],
                    "world_rate": row["world_rate"],
                    "support_rate_lift": row["support_rate_lift"],
                    "delta_shift_per_all": row["delta_shift_per_all"],
                    "conditional_delta_per_all": row["conditional_delta_per_all"],
                    "unconditional_delta_per_all": row["unconditional_delta_per_all"],
                }
            )

    return outcome_rows, group_rows, top_rows


def write_report(
    bands: pd.DataFrame,
    outcome_df: pd.DataFrame,
    group_df: pd.DataFrame,
    top_df: pd.DataFrame,
) -> None:
    ordered = outcome_df.merge(bands[["outcome", "beats_e95"]], on="outcome", how="left")
    nearest_rates = ordered[ordered["prior"].eq("nearest_hard085")].copy()
    subject_rates = ordered[ordered["prior"].eq("subject")].copy()
    global_rates = ordered[ordered["prior"].eq("global")].copy()

    # For the likely decision-critical bands, show the highest responsibility
    # groups under priors with distinct geometry.
    critical_outcomes = ["clean_win", "micro_win", "tie", "fine_loss_branch_alive", "branch_loss", "hard_fail"]
    top_focus = top_df[
        top_df["prior"].isin(["nearest_hard085", "subject", "global"])
        & top_df["outcome"].isin(critical_outcomes)
        & top_df["rank"].le(4)
        & top_df["group_kind"].isin(["target", "component"])
    ].copy()
    top_focus = top_focus.sort_values(["prior", "outcome", "rank"])
    top_focus["rank"] = top_focus.groupby(["prior", "outcome"]).cumcount() + 1

    fine_loss_groups = group_df[
        group_df["outcome"].eq("fine_loss_branch_alive")
        & group_df["prior"].isin(["nearest_hard085", "subject", "global"])
        & group_df["group_kind"].isin(["target", "component"])
    ].copy()
    fine_loss_groups = fine_loss_groups.sort_values(["prior", "delta_shift_per_all"], ascending=[True, False])

    branch_loss_groups = group_df[
        group_df["outcome"].isin(["branch_loss", "hard_fail"])
        & group_df["prior"].isin(["nearest_hard085", "subject", "global"])
        & group_df["group_kind"].isin(["target", "component"])
    ].copy()
    branch_loss_groups = branch_loss_groups.sort_values(["prior", "outcome", "delta_shift_per_all"], ascending=[True, True, False])

    lines = [
        "# E148 E144 Public Outcome Attribution",
        "",
        "## Question",
        "",
        "Before E144 public feedback is known, map each E145 score band to the target/component support pattern that would make that band plausible under public-free priors.",
        "",
        "This is not a submission generator. It is a pre-registered interpretation guardrail for `submission_e144_activeboundary_d7b4b331.csv`.",
        "",
        "## Outcome Rates",
        "",
        "### Global Prior",
        "",
        md_table(
            global_rates[
                [
                    "outcome",
                    "world_rate",
                    "mean_delta_vs_e95",
                    "p05_delta",
                    "p50_delta",
                    "p95_delta",
                    "support_flip_share_mean",
                    "top20_support_rate",
                    "fine_tail_support_rate",
                    "body_support_rate",
                ]
            ],
            ".9f",
        ),
        "",
        "### Subject Prior",
        "",
        md_table(
            subject_rates[
                [
                    "outcome",
                    "world_rate",
                    "mean_delta_vs_e95",
                    "p05_delta",
                    "p50_delta",
                    "p95_delta",
                    "support_flip_share_mean",
                    "top20_support_rate",
                    "fine_tail_support_rate",
                    "body_support_rate",
                ]
            ],
            ".9f",
        ),
        "",
        "### Nearest-Hard Prior",
        "",
        md_table(
            nearest_rates[
                [
                    "outcome",
                    "world_rate",
                    "mean_delta_vs_e95",
                    "p05_delta",
                    "p50_delta",
                    "p95_delta",
                    "support_flip_share_mean",
                    "top20_support_rate",
                    "fine_tail_support_rate",
                    "body_support_rate",
                ]
            ],
            ".9f",
        ),
        "",
        "## Top Responsibility Groups",
        "",
        md_table(
            top_focus[
                [
                    "prior",
                    "outcome",
                    "rank",
                    "direction",
                    "group_kind",
                    "group",
                    "cells",
                    "world_rate",
                    "support_rate_lift",
                    "delta_shift_per_all",
                    "conditional_delta_per_all",
                ]
            ],
            ".9f",
        ),
        "",
        "## Fine-Loss Anatomy",
        "",
        md_table(
            fine_loss_groups[
                [
                    "prior",
                    "group_kind",
                    "group",
                    "cells",
                    "world_rate",
                    "conditional_support_rate",
                    "unconditional_support_rate",
                    "support_rate_lift",
                    "conditional_delta_per_all",
                    "delta_shift_per_all",
                ]
            ].head(30),
            ".9f",
        ),
        "",
        "## Branch/Hard-Fail Anatomy",
        "",
        md_table(
            branch_loss_groups[
                [
                    "prior",
                    "outcome",
                    "group_kind",
                    "group",
                    "cells",
                    "world_rate",
                    "conditional_support_rate",
                    "unconditional_support_rate",
                    "support_rate_lift",
                    "conditional_delta_per_all",
                    "delta_shift_per_all",
                ]
            ].head(36),
            ".9f",
        ),
        "",
        "## Interpretation",
        "",
    ]

    # Compact synthesized read from the produced tables.
    for prior in ["global", "subject", "nearest_hard085"]:
        rates = outcome_df[outcome_df["prior"].eq(prior)].set_index("outcome")
        win_rate = float(rates.loc[["breakthrough_win", "clean_win", "micro_win"], "world_rate"].sum())
        nonwin_rate = float(1.0 - win_rate)
        fine_alive = float(rates.loc["fine_loss_branch_alive", "world_rate"])
        branch_or_worse = float(rates.loc[["branch_loss", "hard_fail"], "world_rate"].sum())
        lines.append(
            f"- `{prior}`: win-rate mass `{win_rate:.6f}`, non-win mass `{nonwin_rate:.6f}`, "
            f"fine-loss-alive `{fine_alive:.6f}`, branch-or-worse `{branch_or_worse:.6f}`."
        )

    lines.extend(
        [
            "- A future E144 win should be credited to the groups with the most negative conditional LogLoss delta in this table, not to the whole branch by default.",
            "- A fine loss should be read as a narrow support shortfall; E143 remains a contrast only if the shortfall concentrates in `e144_fine_tail_delta` or S3.",
            "- A branch loss or hard fail should be read as a broad target/component failure only if the adverse shift is not isolated to the fine-tail component.",
            "",
            "## Decision",
            "",
            "No submission is created. E144 remains the next public sensor. After E144 public feedback, read the score through E145 bands and this E148 attribution table before creating any E143/E142 follow-up or closing the branch.",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n")


def main() -> None:
    cells = pd.read_csv(CELLS_IN)
    bands = pd.read_csv(BANDS_IN)
    group_masks = build_group_masks(cells)

    outcome_rows: list[dict[str, Any]] = []
    group_rows: list[dict[str, Any]] = []
    top_rows: list[dict[str, Any]] = []
    for prior in PRIORS:
        one_outcome, one_group, one_top = simulate_one_prior(cells, bands, prior, group_masks)
        outcome_rows.extend(one_outcome)
        group_rows.extend(one_group)
        top_rows.extend(one_top)

    outcome_df = pd.DataFrame(outcome_rows)
    group_df = pd.DataFrame(group_rows)
    top_df = pd.DataFrame(top_rows)

    outcome_df.to_csv(OUTCOME_OUT, index=False)
    group_df.to_csv(GROUP_OUT, index=False)
    top_df.to_csv(TOP_OUT, index=False)
    write_report(bands, outcome_df, group_df, top_df)

    print(
        {
            "outcome_rates": str(OUTCOME_OUT),
            "group_attribution": str(GROUP_OUT),
            "top_responsibility": str(TOP_OUT),
            "report": str(REPORT_OUT),
            "priors": len(PRIORS),
            "sims_per_prior": N_SIMS,
        }
    )
    focus = outcome_df[
        outcome_df["prior"].isin(["global", "subject", "nearest_hard085"])
    ][["prior", "outcome", "world_rate", "mean_delta_vs_e95", "support_flip_share_mean"]]
    print(focus.to_string(index=False))


if __name__ == "__main__":
    main()
