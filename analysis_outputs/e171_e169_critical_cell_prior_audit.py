#!/usr/bin/env python3
"""E171: critical-cell prior audit for E169.

E170 says `submission_e169_ctx_veto_c5e806e3.csv` is broad in expectation, but
its public readability can still hinge on a few high-swing hidden labels. This
script asks whether those critical cells are independently supported by visible
global/subject/flank priors, and what E170 score bands those priors imply.

No submission is created.
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

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, load_sub  # noqa: E402
import hidden_block_rate_reconstruction_audit as hbr  # noqa: E402
import e102_e101_active_cell_structure_audit as e102  # noqa: E402
import e118_e101_flank_label_support_audit as e118  # noqa: E402
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402
import e162_branch_readability_flip_thresholds as e162  # noqa: E402
import e170_e169_public_feedback_decoder as e170  # noqa: E402


E95_FILE = "submission_e95_hardtail_541e3973.csv"
E169_FILE = "submission_e169_ctx_veto_c5e806e3.csv"
E167_CELLS = OUT / "e167_broad_survivor_context_alignment_cells.csv"

CELLS_OUT = OUT / "e171_e169_critical_cell_prior_audit_cells.csv"
SET_SUMMARY_OUT = OUT / "e171_e169_critical_cell_prior_audit_set_summary.csv"
OUTCOME_OUT = OUT / "e171_e169_critical_cell_prior_audit_outcomes.csv"
NULL_OUT = OUT / "e171_e169_critical_cell_prior_audit_null.csv"
REPORT_OUT = OUT / "e171_e169_critical_cell_prior_audit_report.md"

N_PUBLIC_CELLS = 250 * len(TARGETS)
N_SIMS = 50_000
N_NULL = 3_000
SEED = 171_2026
EPS = 1.0e-12

PRIORS = [
    "global",
    "subject",
    "nearest_beta",
    "both_distance_beta",
    "edge_endpoint_beta",
    "nearest_hard085",
    "conflict_flat",
    "focus_mean",
    "flank_mean",
    "visible_mean",
]


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 40, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return e138.md_table(view.head(n), floatfmt)


def load_prob(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    return load_sub(file_name, sample)[TARGETS].to_numpy(dtype=np.float64)


def build_cells() -> pd.DataFrame:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    train = train.sort_values(hbr.SORT_KEY).reset_index(drop=True)
    sample = sample.sort_values(KEYS).reset_index(drop=True)
    aligned = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)

    meta = e102.build_hidden_row_meta(train, sample)
    p_new = load_prob(E169_FILE, aligned)
    p_base = load_prob(E95_FILE, aligned)
    moved = np.abs(p_new - p_base) > EPS
    row_idx, target_idx = np.where(moved)
    dy1, dy0 = e162.hard_loss_deltas(p_new[row_idx, target_idx], p_base[row_idx, target_idx])
    dy1_s = dy1 / N_PUBLIC_CELLS
    dy0_s = dy0 / N_PUBLIC_CELLS
    swing = np.abs(dy1_s - dy0_s)
    support_label = np.where(dy1_s < dy0_s, 1, 0).astype(int)

    cells = pd.DataFrame(
        {
            "sub_idx": row_idx.astype(int),
            "target_idx": target_idx.astype(int),
            "target": [TARGETS[j] for j in target_idx],
            "target_group": ["Q" if TARGETS[j].startswith("Q") else "S" for j in target_idx],
            "delta_y1": dy1_s,
            "delta_y0": dy0_s,
            "swing": swing,
            "support_label": support_label,
            "support_delta": np.minimum(dy1_s, dy0_s),
            "adverse_delta": np.maximum(dy1_s, dy0_s),
        }
    )
    cells = cells.merge(meta, on="sub_idx", how="left", validate="many_to_one")
    if cells["global_pos"].isna().any():
        raise RuntimeError("missing global_pos after meta merge")

    context = pd.read_csv(E167_CELLS, low_memory=False)
    context = context[context["pair"].eq("e166_vs_e95")].copy()
    keep_cols = [
        "sub_idx",
        "target_idx",
        "edge_like",
        "e72_active",
        "e101_active",
        "all_veto_null",
        "all_safe_density",
        "broad_low_alpha_mass",
        "e101_plausible_mass",
        "benefit_rank",
        "swing_rank",
    ]
    cells = cells.merge(context[keep_cols], on=["sub_idx", "target_idx"], how="left", validate="one_to_one")
    cells["edge_like"] = cells["edge_like"].fillna(cells["pos_bin"].isin(["left_edge", "right_edge", "near_edge", "single"]))
    cells["e72_active"] = cells["e72_active"].fillna(False).astype(bool)
    cells["between_train_runs"] = cells["context_type"].eq("between_train_runs")
    cells["context_high"] = cells["edge_like"].astype(bool) | cells["between_train_runs"]

    cells = e118.add_flank_context(cells, train)
    cells = e118.add_support_priors(cells)

    focus_cols = ["p_y1_global", "p_y1_subject", "p_y1_nearest_hard085"]
    flank_cols = ["p_y1_nearest_beta", "p_y1_both_distance_beta", "p_y1_edge_endpoint_beta", "p_y1_conflict_flat"]
    visible_cols = ["p_y1_global", "p_y1_subject", *flank_cols, "p_y1_nearest_hard085"]
    cells["p_y1_focus_mean"] = cells[focus_cols].mean(axis=1)
    cells["p_y1_flank_mean"] = cells[flank_cols].mean(axis=1)
    cells["p_y1_visible_mean"] = cells[visible_cols].mean(axis=1)

    for prior in ["focus_mean", "flank_mean", "visible_mean"]:
        p = cells[f"p_y1_{prior}"].to_numpy(dtype=np.float64)
        cells[f"support_probability_{prior}"] = np.where(
            cells["support_label"].to_numpy(dtype=int) == 1, p, 1.0 - p
        )
        cells[f"expected_delta_{prior}"] = p * cells["delta_y1"].to_numpy(dtype=np.float64) + (1.0 - p) * cells[
            "delta_y0"
        ].to_numpy(dtype=np.float64)

    prior_support_cols = [f"support_probability_{p}" for p in PRIORS]
    cells["support_prob_min"] = cells[prior_support_cols].min(axis=1)
    cells["support_prob_max"] = cells[prior_support_cols].max(axis=1)
    cells["support_prob_range"] = cells["support_prob_max"] - cells["support_prob_min"]
    cells["n_priors_support_ge_05"] = (cells[prior_support_cols] >= 0.5).sum(axis=1)
    cells["all_prior_support"] = cells["n_priors_support_ge_05"].eq(len(PRIORS))
    cells["all_prior_adverse"] = cells["n_priors_support_ge_05"].eq(0)
    cells["prior_split"] = cells["n_priors_support_ge_05"].between(1, len(PRIORS) - 1)
    cells["ambiguous_visible_mean"] = cells["support_probability_visible_mean"].between(0.45, 0.55)
    cells["swing_rank"] = cells["swing"].rank(method="first", ascending=False).astype(int)
    cells["expected_rank_focus"] = cells["expected_delta_focus_mean"].rank(method="first", ascending=True).astype(int)
    return cells.sort_values("swing_rank").reset_index(drop=True)


def set_masks(cells: pd.DataFrame) -> list[tuple[str, np.ndarray]]:
    masks: list[tuple[str, np.ndarray]] = [
        ("all_moved", np.ones(len(cells), dtype=bool)),
        ("top1_swing", cells["swing_rank"].le(1).to_numpy()),
        ("top4_e95_edge", cells["swing_rank"].le(4).to_numpy()),
        ("top8_swing", cells["swing_rank"].le(8).to_numpy()),
        ("top16_swing", cells["swing_rank"].le(16).to_numpy()),
        ("top32_expected_flip", cells["swing_rank"].le(32).to_numpy()),
        ("top32_expected_benefit", cells["expected_rank_focus"].le(32).to_numpy()),
        ("between_train_runs", cells["between_train_runs"].to_numpy(dtype=bool)),
        ("not_e72_active", ~cells["e72_active"].to_numpy(dtype=bool)),
        (
            "between_and_not_e72",
            cells["between_train_runs"].to_numpy(dtype=bool) & ~cells["e72_active"].to_numpy(dtype=bool),
        ),
    ]
    for target in TARGETS:
        masks.append((f"target_{target}", cells["target"].eq(target).to_numpy()))
    return masks


def summarize_sets(cells: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for set_name, mask in set_masks(cells):
        part = cells.loc[mask].copy()
        if part.empty:
            continue
        rec: dict[str, Any] = {
            "set": set_name,
            "n_cells": int(len(part)),
            "n_rows": int(part["sub_idx"].nunique()),
            "targets": ",".join(sorted(part["target"].unique())),
            "swing_sum": float(part["swing"].sum()),
            "top1_swing": float(part["swing"].max()),
            "support_prob_min_mean": float(part["support_prob_min"].mean()),
            "support_prob_range_mean": float(part["support_prob_range"].mean()),
            "all_prior_support_rate": float(part["all_prior_support"].mean()),
            "all_prior_adverse_rate": float(part["all_prior_adverse"].mean()),
            "prior_split_rate": float(part["prior_split"].mean()),
            "ambiguous_visible_rate": float(part["ambiguous_visible_mean"].mean()),
            "flank_conflict_rate": float(part["flank_conflict"].astype(bool).mean()),
            "both_flanks_rate": float(part["both_flanks"].astype(bool).mean()),
            "between_train_runs_rate": float(part["between_train_runs"].mean()),
            "e72_active_rate": float(part["e72_active"].mean()),
        }
        for prior in PRIORS:
            weights = part["swing"].to_numpy(dtype=np.float64)
            support = part[f"support_probability_{prior}"].to_numpy(dtype=np.float64)
            expected = part[f"expected_delta_{prior}"].to_numpy(dtype=np.float64)
            rec[f"expected_delta_{prior}"] = float(expected.sum())
            rec[f"support_mean_{prior}"] = float(support.mean())
            rec[f"support_swing_weighted_{prior}"] = float(np.average(support, weights=weights))
            rec[f"hard_support_rate_{prior}"] = float((support >= 0.5).mean())
        rows.append(rec)
    return pd.DataFrame(rows)


def assign_outcomes(delta: np.ndarray, bands: pd.DataFrame) -> np.ndarray:
    outcome = np.full(delta.shape, "__unassigned__", dtype=object)
    for row in bands.itertuples(index=False):
        lo = float(row.delta_vs_e95_lo_exclusive)
        hi = float(row.delta_vs_e95_hi_inclusive)
        mask = (delta > lo) & (delta <= hi)
        outcome[mask] = row.outcome
    if np.any(outcome == "__unassigned__"):
        raise RuntimeError("some deltas did not map to E170 bands")
    return outcome


def simulate_outcomes(cells: pd.DataFrame) -> pd.DataFrame:
    bands = e170.build_bands()
    rows: list[dict[str, Any]] = []
    d1 = cells["delta_y1"].to_numpy(dtype=np.float64)
    d0 = cells["delta_y0"].to_numpy(dtype=np.float64)
    for prior in PRIORS:
        seed_offset = sum((i + 1) * ord(ch) for i, ch in enumerate(prior))
        rng = np.random.default_rng(SEED + seed_offset)
        p = cells[f"p_y1_{prior}"].to_numpy(dtype=np.float64)
        labels = rng.random((N_SIMS, len(cells))) < p[None, :]
        delta = (labels * d1[None, :] + (~labels) * d0[None, :]).sum(axis=1)
        outcomes = assign_outcomes(delta, bands)
        for outcome, count in pd.Series(outcomes).value_counts(normalize=False).items():
            subset = delta[outcomes == outcome]
            rows.append(
                {
                    "prior": prior,
                    "outcome": str(outcome),
                    "world_count": int(count),
                    "world_rate": float(count / N_SIMS),
                    "mean_delta_vs_e95": float(subset.mean()),
                    "p05_delta_vs_e95": float(np.quantile(subset, 0.05)),
                    "p50_delta_vs_e95": float(np.quantile(subset, 0.50)),
                    "p95_delta_vs_e95": float(np.quantile(subset, 0.95)),
                    "mean_public_lb": float(e170.E95_PUBLIC + subset.mean()),
                }
            )
        rows.append(
            {
                "prior": prior,
                "outcome": "__summary__",
                "world_count": int(N_SIMS),
                "world_rate": 1.0,
                "mean_delta_vs_e95": float(delta.mean()),
                "p05_delta_vs_e95": float(np.quantile(delta, 0.05)),
                "p50_delta_vs_e95": float(np.quantile(delta, 0.50)),
                "p95_delta_vs_e95": float(np.quantile(delta, 0.95)),
                "mean_public_lb": float(e170.E95_PUBLIC + delta.mean()),
                "win_rate": float((delta < 0).mean()),
                "e95_edge_or_better_rate": float((delta <= e170.E95_EDGE_VS_MIXMIN).mean()),
                "worse_than_e101_rate": float((delta > e170.E101_DELTA_VS_E95).mean()),
                "worse_than_mixmin_rate": float((delta > e170.MIXMIN_DELTA_VS_E95).mean()),
            }
        )
    return pd.DataFrame(rows)


def null_support(cells: pd.DataFrame) -> pd.DataFrame:
    rng = np.random.default_rng(SEED + 991)
    rows: list[dict[str, Any]] = []
    support = cells["support_probability_visible_mean"].to_numpy(dtype=np.float64)
    swing = cells["swing"].to_numpy(dtype=np.float64)
    target_indices = {
        target: cells.index[cells["target"].eq(target)].to_numpy(dtype=int)
        for target in sorted(cells["target"].unique())
    }
    top_sets = [
        ("top4_e95_edge", cells["swing_rank"].le(4).to_numpy()),
        ("top16_swing", cells["swing_rank"].le(16).to_numpy()),
        ("top32_expected_flip", cells["swing_rank"].le(32).to_numpy()),
    ]
    for set_name, mask in top_sets:
        top = cells.loc[mask].copy()
        target_counts = top["target"].value_counts().to_dict()
        observed = float(np.average(top["support_probability_visible_mean"], weights=top["swing"]))
        sims: list[float] = []
        for _ in range(N_NULL):
            take_parts: list[np.ndarray] = []
            for target, n in target_counts.items():
                pool = target_indices[target]
                replace = len(pool) < int(n)
                take_parts.append(rng.choice(pool, size=int(n), replace=replace))
            take = np.concatenate(take_parts)
            sims.append(float(np.average(support[take], weights=swing[take])))
        arr = np.asarray(sims, dtype=np.float64)
        rows.append(
            {
                "set": set_name,
                "n_cells": int(len(top)),
                "observed_support_swing_weighted_visible_mean": observed,
                "null_mean": float(arr.mean()),
                "null_p05": float(np.quantile(arr, 0.05)),
                "null_p50": float(np.quantile(arr, 0.50)),
                "null_p95": float(np.quantile(arr, 0.95)),
                "z": float((observed - arr.mean()) / max(arr.std(ddof=1), EPS)),
                "p_low": float((arr <= observed).mean()),
                "p_high": float((arr >= observed).mean()),
            }
        )
    return pd.DataFrame(rows)


def write_report(cells: pd.DataFrame, sets: pd.DataFrame, outcomes: pd.DataFrame, nulls: pd.DataFrame) -> None:
    summary = outcomes[outcomes["outcome"].eq("__summary__")].copy()
    band = outcomes[~outcomes["outcome"].eq("__summary__")].copy()
    critical_cols = [
        "sub_idx",
        "target",
        "swing_rank",
        "swing",
        "support_label",
        "support_probability_visible_mean",
        "support_prob_min",
        "support_prob_range",
        "n_priors_support_ge_05",
        "context_type",
        "pos_bin",
        "e72_active",
        "flank_conflict",
        "p_y1_subject",
        "p_y1_edge_endpoint_beta",
        "p_y1_nearest_hard085",
    ]
    set_cols = [
        "set",
        "n_cells",
        "n_rows",
        "targets",
        "expected_delta_visible_mean",
        "support_swing_weighted_visible_mean",
        "hard_support_rate_visible_mean",
        "support_prob_min_mean",
        "all_prior_support_rate",
        "prior_split_rate",
        "ambiguous_visible_rate",
        "flank_conflict_rate",
        "between_train_runs_rate",
        "e72_active_rate",
    ]
    summary_cols = [
        "prior",
        "mean_delta_vs_e95",
        "p05_delta_vs_e95",
        "p50_delta_vs_e95",
        "p95_delta_vs_e95",
        "win_rate",
        "e95_edge_or_better_rate",
        "worse_than_e101_rate",
        "worse_than_mixmin_rate",
    ]
    band_cols = ["prior", "outcome", "world_rate", "mean_delta_vs_e95", "p50_delta_vs_e95"]
    report = f"""# E171 E169 Critical-Cell Prior Audit

## Question

E170 showed that E169 is broad in expectation, but public-readable movement can
still be decided by a few high-swing hidden labels. Are those critical cells
supported by independent global/subject/flank priors, or is E169 still mostly a
hidden-label bet?

## Critical Cells

{md_table(cells.sort_values("swing_rank"), critical_cols, n=32)}

## Set Summary

{md_table(sets, set_cols, n=40)}

## Prior-Implied E170 Outcome Summary

{md_table(summary, summary_cols, n=20)}

## Prior-Implied Band Mass

{md_table(band.sort_values(["prior", "world_rate"], ascending=[True, False]), band_cols, n=80)}

## Target-Matched Null For Top Critical Sets

{md_table(nulls, None, n=20)}

## Interpretation

- E171 creates no submission. It tests whether E170's high-swing cells are
  public-free-prior supported.
- If top critical sets have low visible support or strong prior split, E169
  remains an information-rich sensor rather than an expected-score claim.
- If several priors put most mass below E95 and the top critical sets are
  better than target-matched nulls, E169 becomes a stronger one-slot candidate.
- Near-duplicate E169 variants remain blocked unless this audit shows the
  decisive cells are both supported and localized to the differing Q2/S3 cells.
"""
    REPORT_OUT.write_text(report)


def run() -> None:
    cells = build_cells()
    sets = summarize_sets(cells)
    outcomes = simulate_outcomes(cells)
    nulls = null_support(cells)
    cells.to_csv(CELLS_OUT, index=False)
    sets.to_csv(SET_SUMMARY_OUT, index=False)
    outcomes.to_csv(OUTCOME_OUT, index=False)
    nulls.to_csv(NULL_OUT, index=False)
    write_report(cells, sets, outcomes, nulls)
    print(CELLS_OUT)
    print(SET_SUMMARY_OUT)
    print(OUTCOME_OUT)
    print(NULL_OUT)
    print(REPORT_OUT)


if __name__ == "__main__":
    run()
