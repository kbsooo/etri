#!/usr/bin/env python3
"""Stress audit for Route-Conserving S2 Bridge HS-JEPA.

The team package needs a paper-grade answer to:

    Is the bridge rule a reusable mechanism, or just a selected list of cells?

This audit compares selected driver/bridge actions against feasible candidate
actions using two checks:

1. Random feasible null:
   sample unique-row candidate bundles many times and compare route energy,
   S2 usage, public utility, and toxicity alignment.

2. Within-driver rank:
   for each selected driver, rank the chosen bridge among all feasible bridge
   candidates for the same driver.
"""

from __future__ import annotations

from pathlib import Path
import json

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "route_conserving_s2_bridge"
OUT.mkdir(parents=True, exist_ok=True)

STAGE_SELECTED = ROOT / "paper_hsjepa_core" / "outputs" / "stage_bridge_conservation_solver" / "stage_bridge_stagebridge_jackpot_selected.csv"
STAGE_CANDIDATES = ROOT / "paper_hsjepa_core" / "outputs" / "stage_bridge_conservation_solver" / "stage_bridge_stagebridge_jackpot_candidates.csv"
S2_SELECTED = ROOT / "paper_hsjepa_core" / "outputs" / "s2hub_bridge_solver" / "s2hub_s2hub_jackpot_selected.csv"
S2_CANDIDATES = ROOT / "paper_hsjepa_core" / "outputs" / "s2hub_bridge_solver" / "s2hub_s2hub_jackpot_raw_candidates.csv"


def load_frame(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    if "bridge_target" in df:
        df["bridge_target"] = df["bridge_target"].fillna("").astype(str)
    if "driver_target" in df:
        df["driver_target"] = df["driver_target"].astype(str)
    return df


def add_derived(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["has_bridge"] = out["bridge_target"].astype(str).ne("")
    out["s2_as_driver"] = out["driver_target"].eq("S2")
    out["s2_as_bridge"] = out["bridge_target"].eq("S2")
    out["s2_any"] = out["s2_as_driver"] | out["s2_as_bridge"]
    out["negative_energy"] = out["route_energy_delta"] < 0
    out["positive_public_utility"] = out["public_utility"] > 0
    return out


def summarize(df: pd.DataFrame) -> dict[str, object]:
    df = add_derived(df)
    return {
        "bundles": int(len(df)),
        "rows": int(df["row"].nunique()) if len(df) else 0,
        "cells": int(df["action_count"].sum()) if "action_count" in df else int(len(df)),
        "mean_route_energy_delta": float(df["route_energy_delta"].mean()) if len(df) else 0.0,
        "median_route_energy_delta": float(df["route_energy_delta"].median()) if len(df) else 0.0,
        "negative_energy_rate": float(df["negative_energy"].mean()) if len(df) else 0.0,
        "s2_any_rate": float(df["s2_any"].mean()) if len(df) else 0.0,
        "s2_bridge_rate": float(df["s2_as_bridge"].mean()) if len(df) else 0.0,
        "same_direction_rate": float(df["same_direction"].mean()) if "same_direction" in df and len(df) else 0.0,
        "mean_public_utility": float(df["public_utility"].mean()) if len(df) else 0.0,
        "mean_solver_score": float(df["solver_score"].mean()) if "solver_score" in df and len(df) else 0.0,
        "max_driver_h088_alignment": float(df["driver_h088_alignment"].max()) if len(df) else 0.0,
    }


def random_unique_row_null(
    candidates: pd.DataFrame,
    selected_count: int,
    iterations: int,
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    candidates = add_derived(candidates)
    metric_cols = [
        "action_count",
        "route_energy_delta",
        "s2_any",
        "s2_as_bridge",
        "same_direction",
        "public_utility",
        "solver_score",
        "driver_h088_alignment",
    ]
    groups = {
        int(row): group[metric_cols].to_numpy(dtype=np.float64)
        for row, group in candidates.groupby("row")
    }
    rows = np.array(sorted(groups), dtype=int)
    if selected_count > len(rows):
        raise ValueError("selected_count exceeds available unique candidate rows")

    records = []
    for idx in range(iterations):
        chosen_rows = rng.choice(rows, size=selected_count, replace=False)
        chosen = []
        for row in chosen_rows:
            arr = groups[int(row)]
            chosen.append(arr[int(rng.integers(0, len(arr)))])
        draw = np.vstack(chosen)
        action_count = draw[:, 0]
        route_delta = draw[:, 1]
        s2_any = draw[:, 2]
        s2_bridge = draw[:, 3]
        same_direction = draw[:, 4]
        public_utility = draw[:, 5]
        solver_score = draw[:, 6]
        driver_h088 = draw[:, 7]
        rec = {
            "bundles": int(selected_count),
            "rows": int(selected_count),
            "cells": int(action_count.sum()),
            "mean_route_energy_delta": float(route_delta.mean()),
            "median_route_energy_delta": float(np.median(route_delta)),
            "negative_energy_rate": float((route_delta < 0).mean()),
            "s2_any_rate": float(s2_any.mean()),
            "s2_bridge_rate": float(s2_bridge.mean()),
            "same_direction_rate": float(same_direction.mean()),
            "mean_public_utility": float(public_utility.mean()),
            "mean_solver_score": float(solver_score.mean()),
            "max_driver_h088_alignment": float(driver_h088.max()),
        }
        rec["iteration"] = idx
        records.append(rec)
    return pd.DataFrame(records)


def null_position(actual: dict[str, object], null_df: pd.DataFrame) -> dict[str, float]:
    mean_energy = float(actual["mean_route_energy_delta"])
    solver = float(actual["mean_solver_score"])
    s2_any = float(actual["s2_any_rate"])
    negative_rate = float(actual["negative_energy_rate"])
    utility = float(actual["mean_public_utility"])
    return {
        "p_null_energy_le_actual": float((null_df["mean_route_energy_delta"] <= mean_energy).mean()),
        "p_null_solver_ge_actual": float((null_df["mean_solver_score"] >= solver).mean()),
        "p_null_s2_any_ge_actual": float((null_df["s2_any_rate"] >= s2_any).mean()),
        "p_null_negative_rate_ge_actual": float((null_df["negative_energy_rate"] >= negative_rate).mean()),
        "p_null_utility_ge_actual": float((null_df["mean_public_utility"] >= utility).mean()),
        "null_mean_route_energy_delta_mean": float(null_df["mean_route_energy_delta"].mean()),
        "null_mean_route_energy_delta_std": float(null_df["mean_route_energy_delta"].std(ddof=0)),
        "null_s2_any_rate_mean": float(null_df["s2_any_rate"].mean()),
        "null_negative_energy_rate_mean": float(null_df["negative_energy_rate"].mean()),
    }


def within_driver_rank(selected: pd.DataFrame, candidates: pd.DataFrame) -> pd.DataFrame:
    rows = []
    key_cols = ["row", "driver_target", "driver_flat"]
    grouped = {key: group.reset_index(drop=True) for key, group in candidates.groupby(key_cols)}
    for rec in selected.to_dict("records"):
        key = (rec["row"], rec["driver_target"], rec["driver_flat"])
        group = grouped.get(key)
        if group is None or len(group) == 0:
            continue
        energy_rank = 1.0 + (group["route_energy_delta"] < rec["route_energy_delta"]).sum()
        solver_rank = 1.0 + (group["solver_score"] > rec["solver_score"]).sum()
        s2hub_rank = None
        if "s2hub_score" in group.columns and "s2hub_score" in rec:
            s2hub_rank = 1.0 + (group["s2hub_score"] > rec["s2hub_score"]).sum()
        rows.append(
            {
                "row": int(rec["row"]),
                "driver_target": rec["driver_target"],
                "bridge_target": rec["bridge_target"],
                "candidate_count_for_driver": int(len(group)),
                "route_energy_delta": float(rec["route_energy_delta"]),
                "energy_rank_ascending": float(energy_rank),
                "energy_rank_pct": float(energy_rank / len(group)),
                "solver_score": float(rec["solver_score"]),
                "solver_rank_descending": float(solver_rank),
                "solver_rank_pct": float(solver_rank / len(group)),
                "s2hub_rank_pct": float(s2hub_rank / len(group)) if s2hub_rank is not None else np.nan,
            }
        )
    return pd.DataFrame(rows)


def audit_one(
    name: str,
    selected_path: Path,
    candidate_path: Path,
    iterations: int,
    seed: int,
) -> tuple[dict[str, object], pd.DataFrame, pd.DataFrame]:
    selected = add_derived(load_frame(selected_path))
    candidates = add_derived(load_frame(candidate_path))
    actual = summarize(selected)
    null_df = random_unique_row_null(candidates, len(selected), iterations, seed)
    rank_df = within_driver_rank(selected, candidates)
    rank_summary = {
        "mean_energy_rank_pct": float(rank_df["energy_rank_pct"].mean()),
        "median_energy_rank_pct": float(rank_df["energy_rank_pct"].median()),
        "mean_solver_rank_pct": float(rank_df["solver_rank_pct"].mean()),
        "median_solver_rank_pct": float(rank_df["solver_rank_pct"].median()),
        "mean_s2hub_rank_pct": float(rank_df["s2hub_rank_pct"].mean()) if rank_df["s2hub_rank_pct"].notna().any() else None,
    }
    readout = {
        "name": name,
        "selected_path": str(selected_path.resolve()),
        "candidate_path": str(candidate_path.resolve()),
        "actual": actual,
        "random_unique_row_null": null_position(actual, null_df),
        "within_driver_rank": rank_summary,
        "interpretation": {
            "route_energy": "lower p_null_energy_le_actual means selected bundles are unusually route-conserving",
            "s2_hub": "lower p_null_s2_any_ge_actual means selected bundles use S2 more than random feasible bundles",
            "rank_pct": "lower rank percent means chosen bridge is near the top among feasible choices for the same driver",
        },
    }
    return readout, null_df, rank_df


def run(iterations: int = 5000, seed: int = 20260610) -> dict[str, object]:
    audits = {}
    for offset, (name, selected_path, candidate_path) in enumerate(
        [
            ("route_conserving_objective_bridge_primary", STAGE_SELECTED, STAGE_CANDIDATES),
            ("s2_listener_bridge_interpretable", S2_SELECTED, S2_CANDIDATES),
        ]
    ):
        readout, null_df, rank_df = audit_one(name, selected_path, candidate_path, iterations, seed + offset)
        audits[name] = readout
        null_df.to_csv(OUT / f"{name}_random_null.csv", index=False)
        rank_df.to_csv(OUT / f"{name}_within_driver_rank.csv", index=False)

    summary_rows = []
    for name, audit in audits.items():
        actual = audit["actual"]
        null = audit["random_unique_row_null"]
        rank = audit["within_driver_rank"]
        summary_rows.append(
            {
                "name": name,
                "bundles": actual["bundles"],
                "mean_route_energy_delta": actual["mean_route_energy_delta"],
                "null_mean_route_energy_delta": null["null_mean_route_energy_delta_mean"],
                "p_null_energy_le_actual": null["p_null_energy_le_actual"],
                "s2_any_rate": actual["s2_any_rate"],
                "null_s2_any_rate": null["null_s2_any_rate_mean"],
                "p_null_s2_any_ge_actual": null["p_null_s2_any_ge_actual"],
                "negative_energy_rate": actual["negative_energy_rate"],
                "null_negative_energy_rate": null["null_negative_energy_rate_mean"],
                "mean_energy_rank_pct": rank["mean_energy_rank_pct"],
                "mean_solver_rank_pct": rank["mean_solver_rank_pct"],
                "mean_s2hub_rank_pct": rank["mean_s2hub_rank_pct"],
            }
        )
    summary = pd.DataFrame(summary_rows)
    summary_path = OUT / "route_conserving_s2_bridge_stress_summary.csv"
    summary.to_csv(summary_path, index=False)

    readout = {
        "audit": "Route-Conserving S2 Bridge Stress Audit",
        "iterations": iterations,
        "seed": seed,
        "summary_path": str(summary_path.resolve()),
        "audits": audits,
    }
    readout_path = OUT / "route_conserving_s2_bridge_stress_audit.json"
    readout_path.write_text(json.dumps(readout, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(readout, indent=2, ensure_ascii=False))
    return readout


if __name__ == "__main__":
    run()
