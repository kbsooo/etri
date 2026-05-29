#!/usr/bin/env python3
"""E159: pre-public attribution decoder for E154 public feedback.

E158 fixes score bands for the repaired branch, but a scalar E154 public score
does not say which part of the move should be credited or blamed. E154 contains
the whole E144 residual branch plus an additional repaired body. This script
decomposes the E154-vs-E95 LogLoss movement into additive per-label segments:

1. E95 -> E144 inherited body.
2. E144 -> E154 adjustment on those inherited cells.
3. E144 -> E154 extra cells outside E144.

The same hidden label is shared by multiple segments on the same row/target
cell during simulation, so component attribution remains additive without
pretending duplicated segments are independent labels.
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
from public_anchor_bottleneck_decomposition import TARGETS, KEYS, load_sub  # noqa: E402


E95_FILE = "submission_e95_hardtail_541e3973.csv"
E144_FILE = "submission_e144_activeboundary_d7b4b331.csv"
E154_FILE = "submission_e154_s3repair_9f2e2e73.csv"

E95_PUBLIC = 0.5762913298
TOTAL_TEST_CELLS = 250 * 7
N_SIMS = 200_000
RNG_SEED = 20260530 + 159
EPS = 1.0e-12

CELLS_OUT = OUT / "e159_e154_public_outcome_attribution_cells.csv"
OUTCOME_OUT = OUT / "e159_e154_public_outcome_attribution_rates.csv"
GROUP_OUT = OUT / "e159_e154_public_outcome_group_attribution.csv"
TOP_OUT = OUT / "e159_e154_public_outcome_top_responsibility.csv"
REPORT_OUT = OUT / "e159_e154_public_outcome_attribution_report.md"
BANDS_IN = OUT / "e158_repaired_branch_public_decoder_bands.csv"

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

WIN_OUTCOMES = {"breakthrough_win", "clean_win", "micro_win"}


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


def hard_loss_deltas(p_new: np.ndarray, p_base: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    p_new = np.clip(np.asarray(p_new, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)
    p_base = np.clip(np.asarray(p_base, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)
    delta_y1 = -np.log(p_new) + np.log(p_base)
    delta_y0 = -np.log(1.0 - p_new) + np.log(1.0 - p_base)
    return delta_y1, delta_y0


def add_segment(
    records: list[dict[str, Any]],
    *,
    sub_idx: int,
    target_idx: int,
    target: str,
    component: str,
    p_from: float,
    p_to: float,
    p_e95: float,
    p_e144: float,
    p_e154: float,
) -> None:
    d1, d0 = hard_loss_deltas(np.asarray([p_to]), np.asarray([p_from]))
    delta_y1 = float(d1[0])
    delta_y0 = float(d0[0])
    support_y = int(delta_y1 < delta_y0)
    support_delta = min(delta_y1, delta_y0)
    adverse_delta = max(delta_y1, delta_y0)
    cell_id = f"{sub_idx}:{target}"
    records.append(
        {
            "cell_id": cell_id,
            "sub_idx": sub_idx,
            "target": target,
            "target_idx": target_idx,
            "component": component,
            "p_from": float(p_from),
            "p_to": float(p_to),
            "p_e95": float(p_e95),
            "p_e144": float(p_e144),
            "p_e154": float(p_e154),
            "delta_prob_segment": float(p_to - p_from),
            "delta_prob_e154_minus_e95": float(p_e154 - p_e95),
            "delta_prob_e144_minus_e95": float(p_e144 - p_e95),
            "delta_prob_e154_minus_e144": float(p_e154 - p_e144),
            "delta_y1": delta_y1,
            "delta_y0": delta_y0,
            "support_label": support_y,
            "support_y_for_e154": support_y,
            "support_y_for_e144": support_y,
            "support_delta": float(support_delta),
            "adverse_delta": float(adverse_delta),
            "flip_benefit": float(adverse_delta - support_delta),
            "segment_better_if_y1": bool(delta_y1 < 0.0),
            "segment_better_if_y0": bool(delta_y0 < 0.0),
            "moves_prob_up": bool(p_to > p_from),
            "moves_prob_down": bool(p_to < p_from),
            "is_inherited_e144_cell": bool(abs(p_e144 - p_e95) > EPS),
            "is_e154_extra_cell": bool(abs(p_e144 - p_e95) <= EPS),
        }
    )


def build_segments(sample: pd.DataFrame, meta: pd.DataFrame) -> pd.DataFrame:
    p95 = load_sub(E95_FILE, sample)[TARGETS].to_numpy(dtype=np.float64)
    p144 = load_sub(E144_FILE, sample)[TARGETS].to_numpy(dtype=np.float64)
    p154 = load_sub(E154_FILE, sample)[TARGETS].to_numpy(dtype=np.float64)

    records: list[dict[str, Any]] = []
    for row_i in range(len(sample)):
        for target_i, target in enumerate(TARGETS):
            v95 = float(p95[row_i, target_i])
            v144 = float(p144[row_i, target_i])
            v154 = float(p154[row_i, target_i])
            if abs(v154 - v95) <= EPS and abs(v144 - v95) <= EPS:
                continue
            if abs(v144 - v95) > EPS:
                add_segment(
                    records,
                    sub_idx=row_i,
                    target_idx=target_i,
                    target=target,
                    component="inherited_e144_body",
                    p_from=v95,
                    p_to=v144,
                    p_e95=v95,
                    p_e144=v144,
                    p_e154=v154,
                )
            if abs(v154 - v144) > EPS:
                component = (
                    "e154_adjustment_on_e144_body"
                    if abs(v144 - v95) > EPS
                    else "e154_extra_body"
                )
                add_segment(
                    records,
                    sub_idx=row_i,
                    target_idx=target_i,
                    target=target,
                    component=component,
                    p_from=v144,
                    p_to=v154,
                    p_e95=v95,
                    p_e144=v144,
                    p_e154=v154,
                )

    segments = pd.DataFrame(records)
    if segments.empty:
        raise RuntimeError("E154 and E95 have no differing cells")
    segments = segments.merge(meta, on="sub_idx", how="left", validate="many_to_one")
    segments["edge_like"] = segments["pos_bin"].isin(["left_edge", "right_edge", "near_edge", "single"])
    segments["flip_rank"] = segments["flip_benefit"].rank(method="first", ascending=False).astype(int)
    segments["segment_id"] = np.arange(len(segments), dtype=int)
    cell_codes, uniques = pd.factorize(segments["cell_id"], sort=True)
    segments["unique_cell_idx"] = cell_codes.astype(int)
    segments["unique_cell_count"] = len(uniques)
    return segments


def assign_outcomes(delta: np.ndarray, bands: pd.DataFrame) -> np.ndarray:
    outcome = np.full(delta.shape, "__unassigned__", dtype=object)
    for row in bands.itertuples(index=False):
        lo = float(row.delta_lo_exclusive)
        hi = float(row.delta_hi_inclusive)
        mask = (delta > lo) & (delta <= hi)
        outcome[mask] = row.outcome
    if np.any(outcome == "__unassigned__"):
        raise RuntimeError("Some simulated deltas did not map to an E158 outcome band")
    return outcome


def build_group_masks(segments: pd.DataFrame) -> list[tuple[str, str, np.ndarray]]:
    groups: list[tuple[str, str, np.ndarray]] = []
    for target in sorted(segments["target"].unique()):
        groups.append(("target", str(target), segments["target"].eq(target).to_numpy()))
    for component in sorted(segments["component"].unique()):
        groups.append(("component", str(component), segments["component"].eq(component).to_numpy()))
    for (target, component), _ in segments.groupby(["target", "component"], sort=True):
        mask = segments["target"].eq(target).to_numpy() & segments["component"].eq(component).to_numpy()
        groups.append(("target_component", f"{target}:{component}", mask))
    return groups


def make_segment_labels(segments: pd.DataFrame, prior: str, rng: np.random.Generator) -> np.ndarray:
    unique = (
        segments.sort_values("unique_cell_idx")
        .drop_duplicates("unique_cell_idx", keep="first")
        .sort_values("unique_cell_idx")
    )
    p_y1 = unique[f"p_y1_{prior}"].to_numpy(dtype=np.float64)
    labels_unique = rng.random((N_SIMS, len(unique))) < p_y1[None, :]
    seg_idx = segments["unique_cell_idx"].to_numpy(dtype=int)
    return labels_unique[:, seg_idx]


def simulate_one_prior(
    segments: pd.DataFrame,
    bands: pd.DataFrame,
    prior: str,
    group_masks: list[tuple[str, str, np.ndarray]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    seed_offset = sum((i + 1) * ord(ch) for i, ch in enumerate(prior))
    rng = np.random.default_rng(RNG_SEED + seed_offset)

    labels = make_segment_labels(segments, prior, rng)
    d1 = segments["delta_y1"].to_numpy(dtype=np.float64)
    d0 = segments["delta_y0"].to_numpy(dtype=np.float64)
    contrib = np.where(labels, d1[None, :], d0[None, :])
    delta = contrib.sum(axis=1) / TOTAL_TEST_CELLS
    outcomes = assign_outcomes(delta, bands)

    support_y = segments["support_y_for_e154"].to_numpy(dtype=bool)
    support = labels == support_y[None, :]
    flip = segments["flip_benefit"].to_numpy(dtype=np.float64)

    outcome_rows: list[dict[str, Any]] = []
    group_rows: list[dict[str, Any]] = []
    top_rows: list[dict[str, Any]] = []

    unconditional_support = support.mean(axis=0)
    unconditional_delta_by_segment = contrib.mean(axis=0) / TOTAL_TEST_CELLS
    unconditional_flip_share = (support * flip[None, :]).sum(axis=1) / max(float(flip.sum()), EPS)

    for band in bands.itertuples(index=False):
        outcome = str(band.outcome)
        idx = outcomes == outcome
        n_worlds = int(idx.sum())
        is_win = outcome in WIN_OUTCOMES
        direction = "credit" if is_win else "blame_or_neutral"

        if n_worlds:
            d = delta[idx]
            s = support[idx]
            c = contrib[idx]
            support_segments = s.sum(axis=1)
            support_flip_share = (s * flip[None, :]).sum(axis=1) / max(float(flip.sum()), EPS)
            top20_mask = segments["flip_rank"].to_numpy(dtype=int) <= 20
            inherited_mask = segments["component"].eq("inherited_e144_body").to_numpy()
            adjust_mask = segments["component"].eq("e154_adjustment_on_e144_body").to_numpy()
            extra_mask = segments["component"].eq("e154_extra_body").to_numpy()
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
                    "support_segments_mean": float(support_segments.mean()),
                    "support_flip_share_mean": float(support_flip_share.mean()),
                    "support_flip_share_lift": float(support_flip_share.mean() - unconditional_flip_share.mean()),
                    "top20_support_rate": float(s[:, top20_mask].mean()),
                    "inherited_body_support_rate": float(s[:, inherited_mask].mean()),
                    "e154_adjustment_support_rate": float(s[:, adjust_mask].mean()),
                    "e154_extra_support_rate": float(s[:, extra_mask].mean()),
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
                    "support_segments_mean": np.nan,
                    "support_flip_share_mean": np.nan,
                    "support_flip_share_lift": np.nan,
                    "top20_support_rate": np.nan,
                    "inherited_body_support_rate": np.nan,
                    "e154_adjustment_support_rate": np.nan,
                    "e154_extra_support_rate": np.nan,
                }
            )
            continue

        local_rows: list[dict[str, Any]] = []
        for group_kind, group_name, mask in group_masks:
            if not bool(mask.any()):
                continue
            conditional_support_rate = float(s[:, mask].mean())
            unconditional_support_rate = float(unconditional_support[mask].mean())
            conditional_delta = float(c[:, mask].sum(axis=1).mean() / TOTAL_TEST_CELLS)
            unconditional_delta = float(unconditional_delta_by_segment[mask].sum())
            conditional_flip_share_group = float(
                (s[:, mask] * flip[mask][None, :]).sum(axis=1).mean() / max(float(flip[mask].sum()), EPS)
            )
            row = {
                "prior": prior,
                "outcome": outcome,
                "world_rate": float(n_worlds / N_SIMS),
                "group_kind": group_kind,
                "group": group_name,
                "segments": int(mask.sum()),
                "unique_cells": int(segments.loc[mask, "cell_id"].nunique()),
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

        ranked = sorted(
            local_rows,
            key=lambda r: r["conditional_delta_per_all"],
            reverse=not is_win,
        )
        for rank, row in enumerate(ranked[:10], start=1):
            top_rows.append(
                {
                    "prior": prior,
                    "outcome": outcome,
                    "rank": rank,
                    "direction": direction,
                    "group_kind": row["group_kind"],
                    "group": row["group"],
                    "segments": row["segments"],
                    "unique_cells": row["unique_cells"],
                    "world_rate": row["world_rate"],
                    "support_rate_lift": row["support_rate_lift"],
                    "delta_shift_per_all": row["delta_shift_per_all"],
                    "conditional_delta_per_all": row["conditional_delta_per_all"],
                    "unconditional_delta_per_all": row["unconditional_delta_per_all"],
                }
            )

    return outcome_rows, group_rows, top_rows


def add_expected_prior_columns(segments: pd.DataFrame) -> pd.DataFrame:
    out = segments.copy()
    for prior in PRIORS:
        out[f"hard_support_{prior}"] = out[f"support_probability_{prior}"].to_numpy(dtype=np.float64) >= 0.5
    return out


def write_report(
    segments: pd.DataFrame,
    bands: pd.DataFrame,
    outcome_df: pd.DataFrame,
    group_df: pd.DataFrame,
    top_df: pd.DataFrame,
) -> None:
    target_counts = (
        segments.groupby("target")
        .agg(
            segments=("segment_id", "size"),
            unique_cells=("cell_id", "nunique"),
            flip_benefit=("flip_benefit", "sum"),
            abs_delta_prob=("delta_prob_segment", lambda x: float(np.abs(x).sum())),
        )
        .reset_index()
        .sort_values("flip_benefit", ascending=False)
    )
    component_counts = (
        segments.groupby("component")
        .agg(
            segments=("segment_id", "size"),
            unique_cells=("cell_id", "nunique"),
            flip_benefit=("flip_benefit", "sum"),
            abs_delta_prob=("delta_prob_segment", lambda x: float(np.abs(x).sum())),
        )
        .reset_index()
        .sort_values("flip_benefit", ascending=False)
    )

    focus_priors = ["global", "subject", "nearest_hard085"]
    focus_outcomes = ["breakthrough_win", "clean_win", "micro_win", "tie", "small_loss", "branch_loss", "hard_fail"]
    focus_rates = outcome_df[outcome_df["prior"].isin(focus_priors)].copy()
    focus_rates["outcome"] = pd.Categorical(focus_rates["outcome"], categories=focus_outcomes, ordered=True)
    focus_rates = focus_rates.sort_values(["prior", "outcome"])

    top_focus = top_df[
        top_df["prior"].isin(focus_priors)
        & top_df["outcome"].isin(["clean_win", "micro_win", "tie", "small_loss", "branch_loss", "hard_fail"])
        & top_df["rank"].le(5)
        & top_df["group_kind"].isin(["target", "component"])
    ].copy()
    top_focus = top_focus.sort_values(["prior", "outcome", "rank"])
    top_focus["rank"] = top_focus.groupby(["prior", "outcome"]).cumcount() + 1

    small_loss_groups = group_df[
        group_df["outcome"].eq("small_loss")
        & group_df["prior"].isin(focus_priors)
        & group_df["group_kind"].isin(["target", "component"])
    ].copy()
    small_loss_groups = small_loss_groups.sort_values(["prior", "delta_shift_per_all"], ascending=[True, False])

    hard_groups = group_df[
        group_df["outcome"].isin(["branch_loss", "hard_fail"])
        & group_df["prior"].isin(focus_priors)
        & group_df["group_kind"].isin(["target", "component"])
    ].copy()
    hard_groups = hard_groups.sort_values(["prior", "outcome", "delta_shift_per_all"], ascending=[True, True, False])

    lines = [
        "# E159 E154 Public Outcome Attribution",
        "",
        "## Question",
        "",
        "E158 says how to bucket the public score for `submission_e154_s3repair_9f2e2e73.csv`. This audit asks which target/component support pattern would make each bucket happen.",
        "",
        "The decomposition is additive in LogLoss: E95 -> E144 inherited body, then E144 -> E154 adjustment/extra body. Duplicate segments on the same row-target share one simulated hidden label.",
        "",
        "## Movement Anatomy",
        "",
        f"- unique E154-vs-E95 moved cells: `{int(segments['cell_id'].nunique())}`",
        f"- additive LogLoss segments: `{len(segments)}`",
        f"- moved rows: `{int(segments['sub_idx'].nunique())}`",
        f"- moved subjects: `{int(segments['subject_id'].nunique())}`",
        "",
        "### By Component",
        "",
        md_table(component_counts, ".9f"),
        "",
        "### By Target",
        "",
        md_table(target_counts, ".9f"),
        "",
        "## Outcome Rates",
        "",
        md_table(
            focus_rates[
                [
                    "prior",
                    "outcome",
                    "world_rate",
                    "mean_delta_vs_e95",
                    "p05_delta",
                    "p50_delta",
                    "p95_delta",
                    "support_flip_share_mean",
                    "top20_support_rate",
                    "inherited_body_support_rate",
                    "e154_adjustment_support_rate",
                    "e154_extra_support_rate",
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
                    "segments",
                    "unique_cells",
                    "world_rate",
                    "delta_shift_per_all",
                    "conditional_delta_per_all",
                ]
            ],
            ".9f",
        ),
        "",
        "## Small-Loss Anatomy",
        "",
        md_table(
            small_loss_groups[
                [
                    "prior",
                    "group_kind",
                    "group",
                    "segments",
                    "unique_cells",
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
            hard_groups[
                [
                    "prior",
                    "outcome",
                    "group_kind",
                    "group",
                    "segments",
                    "unique_cells",
                    "world_rate",
                    "conditional_support_rate",
                    "unconditional_support_rate",
                    "support_rate_lift",
                    "conditional_delta_per_all",
                    "delta_shift_per_all",
                ]
            ].head(42),
            ".9f",
        ),
        "",
        "## Interpretation",
        "",
    ]

    for prior in focus_priors:
        rates = outcome_df[outcome_df["prior"].eq(prior)].set_index("outcome")
        win_rate = float(rates.loc[list(WIN_OUTCOMES), "world_rate"].sum())
        tie_rate = float(rates.loc["tie", "world_rate"])
        small_loss_rate = float(rates.loc["small_loss", "world_rate"])
        branch_or_worse = float(rates.loc[["branch_loss", "hard_fail"], "world_rate"].sum())
        lines.append(
            f"- `{prior}`: win mass `{win_rate:.6f}`, tie `{tie_rate:.6f}`, "
            f"small-loss `{small_loss_rate:.6f}`, branch-or-worse `{branch_or_worse:.6f}`."
        )

    lines.extend(
        [
            "- If E154 wins, credit only the groups with negative conditional contribution in this table; do not infer that every repaired sibling is validated.",
            "- If E154 ties or small-loses and blame concentrates in `e154_adjustment_on_e144_body` or `e154_extra_body`, E155 is the clean amplitude-control follow-up.",
            "- If E154 branch-loss/hard-fails with blame dominated by `inherited_e144_body`, E155 is not a rescue; use E144 as the unrepaired contrast or leave this branch.",
            "- If target blame is broad Q3/S3/S2 rather than component-local, the bottleneck is hidden public target-prior allocation, not S3 repair exactness.",
            "",
            "## Decision",
            "",
            "After E154 public feedback, combine E158 score band with this E159 target/component attribution. E155 is justified only when the score says the branch is not dead and the attribution blames E154's added body rather than the inherited E144 branch.",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n")


def main() -> None:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    train = train.sort_values(hbr.SORT_KEY).reset_index(drop=True)
    sample = sample.sort_values(KEYS).reset_index(drop=True)
    meta = e102.build_hidden_row_meta(train, sample)

    segments = build_segments(sample, meta)
    segments = e118.add_flank_context(segments, train)
    segments = e118.add_support_priors(segments)
    segments = add_expected_prior_columns(segments)
    segments.to_csv(CELLS_OUT, index=False)

    bands = pd.read_csv(BANDS_IN)
    group_masks = build_group_masks(segments)
    outcome_rows: list[dict[str, Any]] = []
    group_rows: list[dict[str, Any]] = []
    top_rows: list[dict[str, Any]] = []
    for prior in PRIORS:
        one_outcome, one_group, one_top = simulate_one_prior(segments, bands, prior, group_masks)
        outcome_rows.extend(one_outcome)
        group_rows.extend(one_group)
        top_rows.extend(one_top)

    outcome_df = pd.DataFrame(outcome_rows)
    group_df = pd.DataFrame(group_rows)
    top_df = pd.DataFrame(top_rows)
    outcome_df.to_csv(OUTCOME_OUT, index=False)
    group_df.to_csv(GROUP_OUT, index=False)
    top_df.to_csv(TOP_OUT, index=False)
    write_report(segments, bands, outcome_df, group_df, top_df)

    print(
        {
            "segments": len(segments),
            "unique_cells": int(segments["cell_id"].nunique()),
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
