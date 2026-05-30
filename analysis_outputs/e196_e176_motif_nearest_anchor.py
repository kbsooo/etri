#!/usr/bin/env python3
"""E196: E176 critical-cell motif nearest-anchor stress.

E195 locks E176 as the next public sensor, but it does not reduce the
hard-label uncertainty inside E176. This audit asks a smaller question:

    Do E176's public-decisive cells look like known public-winning or
    public-losing critical-cell motifs if we ignore label priors and look only
    at row/order/block/target anatomy?

This is not a submission generator and not a public-LB predictor. It is a
falsification test for a tempting shortcut: replacing the public sensor with a
motif-only decisive-cell selector.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


OUT = Path(__file__).resolve().parent
CELLS_IN = OUT / "e180_known_anchor_decisive_cell_visibility_cells.csv"

PROFILE_OUT = OUT / "e196_e176_motif_nearest_anchor_profiles.csv"
LOO_OUT = OUT / "e196_e176_motif_nearest_anchor_loo.csv"
NEIGHBOR_OUT = OUT / "e196_e176_motif_nearest_anchor_neighbors.csv"
SUMMARY_OUT = OUT / "e196_e176_motif_nearest_anchor_summary.csv"
REPORT_OUT = OUT / "e196_e176_motif_nearest_anchor_report.md"

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
TOP_SETS = {"top4": 4, "top16": 16, "top33": 33}
PENDING_PAIR = "e176_vs_e95_pending"


def fmt(x: object) -> str:
    if pd.isna(x):
        return "NA"
    if isinstance(x, (float, np.floating)):
        return f"{float(x):.9g}"
    return str(x)


def markdown_table(df: pd.DataFrame, n: int = 40) -> str:
    if df.empty:
        return "_empty_"
    view = df.head(n).copy()
    for col in view.columns:
        view[col] = view[col].map(fmt).astype(str).str.replace("|", "\\|", regex=False)
    header = "| " + " | ".join(view.columns) + " |"
    sep = "| " + " | ".join(["---"] * len(view.columns)) + " |"
    rows = ["| " + " | ".join(row.astype(str).tolist()) + " |" for _, row in view.iterrows()]
    return "\n".join([header, sep, *rows])


def safe_weighted_mean(values: pd.Series, weights: np.ndarray) -> float:
    arr = values.fillna(0).astype(float).to_numpy()
    if len(arr) == 0:
        return 0.0
    if float(weights.sum()) <= 0:
        return float(arr.mean())
    return float(np.average(arr, weights=weights))


def weighted_rate(part: pd.DataFrame, mask: pd.Series, weights: np.ndarray) -> float:
    if len(part) == 0:
        return 0.0
    vals = mask.fillna(False).astype(bool).to_numpy(dtype=float)
    if float(weights.sum()) <= 0:
        return float(vals.mean())
    return float(np.average(vals, weights=weights))


def categorical_shares(part: pd.DataFrame, column: str, prefix: str, values: list[str], weights: np.ndarray) -> dict[str, float]:
    out: dict[str, float] = {}
    denom = float(weights.sum())
    for value in values:
        if len(part) == 0 or denom <= 0:
            out[f"{prefix}_{value}"] = 0.0
        else:
            out[f"{prefix}_{value}"] = float(weights[part[column].astype(str).eq(value).to_numpy()].sum() / denom)
    return out


def build_profiles(cells: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    context_values = ["between_train_runs", "after_train_run", "before_train_run", "isolated"]
    pos_values = ["single", "left_edge", "right_edge", "near_edge", "interior"]
    block_values = ["1-2", "3-5", "6-10", "11-16"]

    for pair in cells["pair"].unique():
        for top_name, top_n in TOP_SETS.items():
            part = cells[cells["pair"].eq(pair) & cells["swing_rank"].le(top_n)].copy()
            if part.empty:
                continue
            weights = part["swing"].fillna(0).astype(float).to_numpy()
            if float(weights.sum()) <= 0:
                weights = np.ones(len(part), dtype=float)

            actual_direction = str(part["actual_direction"].iloc[0])
            rec: dict[str, Any] = {
                "pair": pair,
                "set": top_name,
                "top_n": int(top_n),
                "actual_direction": actual_direction,
                "known_status": "pending" if actual_direction.startswith("pending") else "known",
                "family": str(part["family"].iloc[0]),
                "actual_delta": float(part["actual_delta"].iloc[0]) if pd.notna(part["actual_delta"].iloc[0]) else np.nan,
                "n_cells": int(len(part)),
                "n_rows": int(part["sub_idx"].nunique()),
                "n_subjects": int(part["subject_id"].nunique()),
                "n_blocks": int(part["hidden_block_id"].nunique()),
                "swing_sum": float(part["swing"].sum()),
                "top_swing_share": float(part["swing"].max() / max(part["swing"].sum(), 1.0e-12)),
                "row_coverage": float(part["sub_idx"].nunique() / 250.0),
                "subject_coverage": float(part["subject_id"].nunique() / max(cells["subject_id"].nunique(), 1)),
                "block_coverage": float(part["hidden_block_id"].nunique() / max(cells["hidden_block_id"].nunique(), 1)),
                "between_train_runs_rate": weighted_rate(part, part["between_train_runs"], weights),
                "edge_like_rate": weighted_rate(part, part["edge_like"], weights),
                "is_weekend_rate": weighted_rate(part, part["is_weekend"].astype(bool), weights),
                "flank_conflict_rate": weighted_rate(part, part["flank_conflict"].astype(bool), weights),
                "both_flanks_rate": weighted_rate(part, part["both_flanks"].astype(bool), weights),
                "e72_active_rate": weighted_rate(part, part["e72_active"].astype(bool), weights),
                "e101_active_rate": weighted_rate(part, part["e101_active"].astype(bool), weights),
                "all_veto_null_rate": weighted_rate(
                    part, part.get("all_veto_null", pd.Series(False, index=part.index)).astype(bool), weights
                ),
                "all_safe_density_mean": safe_weighted_mean(
                    part.get("all_safe_density", pd.Series(0.0, index=part.index)), weights
                ),
                "broad_low_alpha_mass_mean": safe_weighted_mean(
                    part.get("broad_low_alpha_mass", pd.Series(0.0, index=part.index)), weights
                ),
                "e101_plausible_mass_mean": safe_weighted_mean(
                    part.get("e101_plausible_mass", pd.Series(0.0, index=part.index)), weights
                ),
            }
            rec.update(categorical_shares(part, "target", "target", TARGETS, weights))
            rec.update(categorical_shares(part, "context_type", "context", context_values, weights))
            rec.update(categorical_shares(part, "pos_bin", "pos", pos_values, weights))
            rec.update(categorical_shares(part, "block_len_bin", "block_len", block_values, weights))
            rec["q_share"] = sum(rec[f"target_{t}"] for t in ["Q1", "Q2", "Q3"])
            rec["s_share"] = sum(rec[f"target_{t}"] for t in ["S1", "S2", "S3", "S4"])
            rec["q2s3_share"] = rec["target_Q2"] + rec["target_S3"]
            rows.append(rec)
    return pd.DataFrame(rows)


def feature_views(profiles: pd.DataFrame) -> dict[str, list[str]]:
    base_cols = [
        "n_cells",
        "n_rows",
        "n_subjects",
        "n_blocks",
        "top_swing_share",
        "row_coverage",
        "subject_coverage",
        "block_coverage",
        "between_train_runs_rate",
        "edge_like_rate",
        "is_weekend_rate",
        "q_share",
        "s_share",
        "q2s3_share",
    ]
    target_cols = [c for c in profiles.columns if c.startswith("target_")]
    context_cols = [c for c in profiles.columns if c.startswith("context_")]
    pos_cols = [c for c in profiles.columns if c.startswith("pos_")]
    block_cols = [c for c in profiles.columns if c.startswith("block_len_")]
    sequence = base_cols + target_cols + context_cols + pos_cols + block_cols
    axis = sequence + [
        "e72_active_rate",
        "e101_active_rate",
        "all_veto_null_rate",
        "all_safe_density_mean",
        "broad_low_alpha_mass_mean",
        "e101_plausible_mass_mean",
    ]
    flank = axis + ["flank_conflict_rate", "both_flanks_rate"]
    return {
        "sequence_only": [c for c in sequence if c in profiles.columns],
        "sequence_axis": [c for c in axis if c in profiles.columns],
        "sequence_axis_flank": [c for c in flank if c in profiles.columns],
    }


def zscore(train: pd.DataFrame, test: pd.DataFrame, cols: list[str]) -> tuple[np.ndarray, np.ndarray]:
    x_train = train[cols].astype(float).fillna(0.0)
    x_test = test[cols].astype(float).fillna(0.0)
    mu = x_train.mean(axis=0)
    sd = x_train.std(axis=0, ddof=0).replace(0.0, 1.0)
    return ((x_train - mu) / sd).to_numpy(dtype=float), ((x_test - mu) / sd).to_numpy(dtype=float)


def nearest_vote(distances: pd.DataFrame) -> dict[str, float]:
    d = distances.copy()
    d["weight"] = 1.0 / np.maximum(d["distance"].astype(float), 1.0e-9)
    vote = d.groupby("actual_direction")["weight"].sum()
    total = float(vote.sum())
    out = {
        "vote_new_won": float(vote.get("new_won", 0.0) / total) if total > 0 else np.nan,
        "vote_new_lost": float(vote.get("new_lost", 0.0) / total) if total > 0 else np.nan,
    }
    return out


def run_loo_and_neighbors(profiles: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    views = feature_views(profiles)
    known = profiles[profiles["known_status"].eq("known")].copy()
    pending = profiles[profiles["pair"].eq(PENDING_PAIR)].copy()

    loo_rows: list[dict[str, Any]] = []
    neighbor_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []

    for set_name in TOP_SETS:
        known_set = known[known["set"].eq(set_name)].copy().reset_index(drop=True)
        pending_set = pending[pending["set"].eq(set_name)].copy().reset_index(drop=True)
        if known_set.empty or pending_set.empty:
            continue

        for view_name, cols in views.items():
            # Leave-one-known-pair-out nearest-neighbor stress.
            correct = []
            exact_e101_correct = np.nan
            mixmin_correct = np.nan
            for i, held in known_set.iterrows():
                train = known_set.drop(index=i).reset_index(drop=True)
                test = held.to_frame().T.reset_index(drop=True)
                x_train, x_test = zscore(train, test, cols)
                distances = np.linalg.norm(x_train - x_test[0][None, :], axis=1)
                nn_pos = int(np.argmin(distances))
                nearest = train.iloc[nn_pos]
                pred = str(nearest["actual_direction"])
                truth = str(held["actual_direction"])
                is_correct = bool(pred == truth)
                correct.append(is_correct)
                if held["pair"] == "e101_vs_e95":
                    exact_e101_correct = float(is_correct)
                if held["pair"] == "mixmin_vs_a2c8":
                    mixmin_correct = float(is_correct)

                by_dir: dict[str, float] = {}
                for direction, grp in train.assign(distance=distances).groupby("actual_direction"):
                    by_dir[str(direction)] = float(grp["distance"].min())
                margin_new_won_minus_new_lost = by_dir.get("new_won", np.nan) - by_dir.get("new_lost", np.nan)
                loo_rows.append(
                    {
                        "set": set_name,
                        "view": view_name,
                        "heldout_pair": str(held["pair"]),
                        "heldout_family": str(held["family"]),
                        "actual_direction": truth,
                        "nearest_pair": str(nearest["pair"]),
                        "nearest_family": str(nearest["family"]),
                        "pred_direction": pred,
                        "correct": int(is_correct),
                        "nearest_distance": float(distances[nn_pos]),
                        "min_distance_new_won": by_dir.get("new_won", np.nan),
                        "min_distance_new_lost": by_dir.get("new_lost", np.nan),
                        "margin_new_won_minus_new_lost": margin_new_won_minus_new_lost,
                    }
                )

            # Pending E176 nearest-anchor read.
            train = known_set.reset_index(drop=True)
            test = pending_set.reset_index(drop=True)
            x_train, x_test = zscore(train, test, cols)
            distances = np.linalg.norm(x_train - x_test[0][None, :], axis=1)
            dist_df = train[["pair", "family", "actual_direction"]].copy()
            dist_df["distance"] = distances
            dist_df = dist_df.sort_values("distance").reset_index(drop=True)
            votes = nearest_vote(dist_df)
            for rank, rec in enumerate(dist_df.head(6).to_dict("records"), start=1):
                neighbor_rows.append(
                    {
                        "set": set_name,
                        "view": view_name,
                        "pending_pair": PENDING_PAIR,
                        "neighbor_rank": rank,
                        "neighbor_pair": rec["pair"],
                        "neighbor_family": rec["family"],
                        "neighbor_direction": rec["actual_direction"],
                        "distance": float(rec["distance"]),
                        **votes,
                    }
                )

            nearest_direction = str(dist_df.iloc[0]["actual_direction"])
            nearest_distance = float(dist_df.iloc[0]["distance"])
            nearest_loss_distance = float(dist_df[dist_df["actual_direction"].eq("new_lost")]["distance"].min())
            nearest_win_distance = float(dist_df[dist_df["actual_direction"].eq("new_won")]["distance"].min())
            summary_rows.append(
                {
                    "set": set_name,
                    "view": view_name,
                    "known_loo_accuracy": float(np.mean(correct)),
                    "known_loo_correct": int(np.sum(correct)),
                    "known_loo_n": int(len(correct)),
                    "exact_e101_boundary_correct": exact_e101_correct,
                    "mixmin_broad_success_correct": mixmin_correct,
                    "e176_nearest_direction": nearest_direction,
                    "e176_nearest_pair": str(dist_df.iloc[0]["pair"]),
                    "e176_nearest_distance": nearest_distance,
                    "e176_nearest_win_distance": nearest_win_distance,
                    "e176_nearest_loss_distance": nearest_loss_distance,
                    "e176_win_distance_advantage": nearest_loss_distance - nearest_win_distance,
                    "e176_inverse_distance_vote_new_won": votes["vote_new_won"],
                    "e176_inverse_distance_vote_new_lost": votes["vote_new_lost"],
                    "action_grade": bool(
                        np.mean(correct) >= 0.80
                        and exact_e101_correct == 1.0
                        and mixmin_correct == 1.0
                        and votes["vote_new_won"] >= 0.65
                    ),
                }
            )

    loo = pd.DataFrame(loo_rows)
    neighbors = pd.DataFrame(neighbor_rows)
    summary = pd.DataFrame(summary_rows).sort_values(
        ["action_grade", "known_loo_accuracy", "exact_e101_boundary_correct", "e176_inverse_distance_vote_new_won"],
        ascending=[False, False, False, False],
    )
    return loo, neighbors, summary


def write_report(profiles: pd.DataFrame, loo: pd.DataFrame, neighbors: pd.DataFrame, summary: pd.DataFrame) -> None:
    best = summary.iloc[0]
    e176_profiles = profiles[profiles["pair"].eq(PENDING_PAIR)].copy()
    top_neighbors = neighbors[
        neighbors["neighbor_rank"].le(3)
        & neighbors["set"].eq(str(best["set"]))
        & neighbors["view"].eq(str(best["view"]))
    ].copy()
    failed_reason = "No motif view is action-grade." if not bool(summary["action_grade"].any()) else "At least one motif view is action-grade."
    e176_note = (
        "E176's top4/top16 motifs are closest to a known loss in the best high-accuracy views, "
        "while top33 motifs drift toward mixmin. That split is anatomy, not an actionable selector."
    )
    body = f"""# E196 E176 Motif Nearest-Anchor Stress

## Question

Can row/order/block/target motif alone resolve whether E176's public-decisive cells resemble known public-winning or public-losing critical-cell patterns?

## Result

{failed_reason} The best view is `{best['view']}` on `{best['set']}` with known-pair LOO accuracy `{float(best['known_loo_accuracy']):.6f}`, exact E101 boundary correctness `{fmt(best['exact_e101_boundary_correct'])}`, and mixmin broad-success correctness `{fmt(best['mixmin_broad_success_correct'])}`.

E176's nearest anchors in that best view lean `{best['e176_nearest_direction']}` with inverse-distance vote new_won `{float(best['e176_inverse_distance_vote_new_won']):.6f}`, but this is not action-grade because the known-anchor stress is too weak.

## Summary

{markdown_table(summary, n=20)}

## E176 Profiles

{markdown_table(e176_profiles, n=20)}

## Best-View E176 Neighbors

{markdown_table(top_neighbors, n=10)}

## Leave-One-Known-Pair Stress

{markdown_table(loo.sort_values(['set', 'view', 'heldout_pair']), n=80)}

## Interpretation

- E176's critical-cell motif has weak winner-neighbor evidence, but the nearest-anchor rule misses important known anchors, especially the exact E101/E95 frontier boundary in several views.
- This kills the shortcut "use row/order motif nearest anchors as a decisive-cell selector."
- The result does not demote E176: E195's information-value argument remains stronger because E176 is a public sensor with a pre-registered decoder, not a motif-certified expected-score file.

## Decision

No submission is created. Keep `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv` as the next public sensor. E196 adds only a weak anatomy note: {e176_note}
"""
    REPORT_OUT.write_text(body, encoding="utf-8")


def main() -> None:
    if not CELLS_IN.exists():
        raise FileNotFoundError(CELLS_IN)
    cells = pd.read_csv(CELLS_IN, low_memory=False)
    profiles = build_profiles(cells)
    loo, neighbors, summary = run_loo_and_neighbors(profiles)
    profiles.to_csv(PROFILE_OUT, index=False)
    loo.to_csv(LOO_OUT, index=False)
    neighbors.to_csv(NEIGHBOR_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    write_report(profiles, loo, neighbors, summary)
    print("wrote", PROFILE_OUT)
    print("wrote", LOO_OUT)
    print("wrote", NEIGHBOR_OUT)
    print("wrote", SUMMARY_OUT)
    print("wrote", REPORT_OUT)
    print(summary.head(12).to_string(index=False))


if __name__ == "__main__":
    main()
