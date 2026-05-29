#!/usr/bin/env python3
"""E126 cell-level anatomy of E101-compatible tail-budget worlds.

SAUNA question:
E125 showed that E101-compatible scenarios are not q2s3-mask scenarios. This
script reconstructs the actual E72-adverse cells selected by each E124 scenario
and asks what the E101-compatible tail budget is made of.

No submission is generated. E101 public feedback is used only as a diagnostic
filter over already-defined E96/E124 scenarios.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

import e96_public_miss_budget_tail_scenarios as e96  # noqa: E402
from e102_e101_active_cell_structure_audit import build_hidden_row_meta  # noqa: E402
import hidden_block_rate_reconstruction_audit as hbr  # noqa: E402
from public_anchor_bottleneck_decomposition import KEYS, TARGETS, load_sub, logit  # noqa: E402


SCENARIOS_IN = OUT / "e124_e101_conditioned_tail_transfer_scenarios.csv"
SELECTED_OUT = OUT / "e126_e101_survivor_cell_budget_selected_detail.csv"
GROUP_OUT = OUT / "e126_e101_survivor_cell_budget_group_summary.csv"
CATEGORY_OUT = OUT / "e126_e101_survivor_cell_budget_category_summary.csv"
REPORT_OUT = OUT / "e126_e101_survivor_cell_budget_report.md"

FILES = {
    **e96.FILES,
    "e101": "submission_e101_q2s3tail_177569bc.csv",
}

EPS = 1.0e-9


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


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def load_pred(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    return clip_prob(load_sub(file_name, sample)[TARGETS].to_numpy(dtype=np.float64))


def build_flat_cell_meta(sample: pd.DataFrame, row_meta: pd.DataFrame, preds: dict[str, np.ndarray], masks: dict[str, np.ndarray], e72_pos: np.ndarray, e72_delta: np.ndarray) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    le101 = logit(preds["e101"])
    le95 = logit(preds["e95"])
    lmix = logit(preds["mixmin"])
    le86 = logit(preds["e86"])
    for row_i in range(len(sample)):
        row = row_meta.iloc[row_i]
        for j, target in enumerate(TARGETS):
            flat = row_i * len(TARGETS) + j
            rows.append(
                {
                    "cell_idx": flat,
                    "sub_idx": row_i,
                    "target": target,
                    "target_group": "Q" if target.startswith("Q") else "S",
                    "target_is_q2s3": target in {"Q2", "S3"},
                    "e101_active": abs(float(le101[row_i, j] - le95[row_i, j])) > EPS,
                    "e95_moved_vs_mixmin": abs(float(le95[row_i, j] - lmix[row_i, j])) > EPS,
                    "e95_fallback_cell": bool(masks["e95_fallback_cells"][flat]),
                    "e86_moved_vs_mixmin": abs(float(le86[row_i, j] - lmix[row_i, j])) > EPS,
                    "e72_active": abs(float(e72_delta[row_i, j])) > EPS,
                    "e72_pos": float(e72_pos[row_i, j]),
                    "e72_abs_logit_delta": abs(float(e72_delta[row_i, j])),
                    "hidden_block_id": row["hidden_block_id"],
                    "subject_id": row["subject_id"],
                    "context_type": row["context_type"],
                    "block_len_bin": row["block_len_bin"],
                    "pos_bin": row["pos_bin"],
                    "edge_like": row["pos_bin"] in {"left_edge", "right_edge", "near_edge", "single"},
                    "is_weekend": int(row["is_weekend"]),
                    "block_n_rows": int(row["block_n_rows"]),
                    "edge_distance": int(row["edge_distance"]),
                }
            )
    return pd.DataFrame(rows)


def scenario_group_names(row: pd.Series) -> list[str]:
    names: list[str] = []
    if bool(row["is_broad_plausible"]):
        names.append("broad")
        if bool(row["e101_sensor_plausible"]):
            names.append("e101_plausible")
        if str(row["mask_name"]) == "q2s3":
            names.append("broad_q2s3")
        if str(row["mask_name"]) in {"all", "e72_top50_hard"}:
            names.append("broad_all_or_top50")
        if float(row["alpha"]) <= 1.0:
            names.append("broad_low_alpha")
        if abs(float(row["tail_e101"]) - float(row["tail_e95"])) <= 1.0e-8:
            names.append("broad_tail_equal")
    return names


def iter_scenario_weights(e72_pos_flat: np.ndarray, masks: dict[str, np.ndarray], wanted_ids: set[str]):
    scenario_count = 0
    deterministic_masks = [
        "all",
        "q2",
        "s1",
        "s2",
        "s3",
        "q2s3",
        "s1s2s3",
        "live_q2s1s2s3",
        "e72_top20_abs",
        "e72_top50_hard",
        "e95_fallback_cells",
        "e95_nonfallback_cells",
        "e95_fallback_q2s3",
        "e95_fallback_s1s2s3",
        "e95_moved_vs_mixmin",
        "e86_moved_vs_mixmin",
        "e90_moved_vs_mixmin",
        "e89_moved_vs_mixmin",
    ]
    budget_sum = float(e96.E72_PUBLIC_MISS * len(e72_pos_flat))
    for mask_name in deterministic_masks:
        mask = masks[mask_name]
        indices = np.flatnonzero(mask & (e72_pos_flat > 1.0e-12))
        if len(indices) == 0:
            continue
        for mode in ["top", "bottom", "median"]:
            scenario_count += 1
            scenario_id = f"d{scenario_count:04d}"
            if scenario_id not in wanted_ids:
                continue
            order = e96.deterministic_order(indices, e72_pos_flat, mode)
            weights, achieved, fractional_cells, full_cells = e96.take_budget(order, e72_pos_flat, budget_sum)
            yield scenario_id, weights, achieved, fractional_cells, full_cells

    rng = np.random.default_rng(e96.RANDOM_SEED)
    random_masks = [
        "all",
        "q2s3",
        "s1s2s3",
        "live_q2s1s2s3",
        "e72_top50_hard",
        "e95_fallback_cells",
        "e95_moved_vs_mixmin",
        "e86_moved_vs_mixmin",
    ]
    for mask_name in random_masks:
        mask = masks[mask_name]
        indices = np.flatnonzero(mask & (e72_pos_flat > 1.0e-12))
        if len(indices) == 0:
            continue
        for gamma in [0.0, 0.5, 1.0, 2.0]:
            for rep in range(e96.RANDOM_SCENARIOS_PER_MASK_GAMMA):
                order = e96.weighted_random_order(indices, e72_pos_flat, gamma, rng)
                scenario_count += 1
                scenario_id = f"r{scenario_count:04d}"
                if scenario_id not in wanted_ids:
                    continue
                weights, achieved, fractional_cells, full_cells = e96.take_budget(order, e72_pos_flat, budget_sum)
                yield scenario_id, weights, achieved, fractional_cells, full_cells


def reconstruct_selected_records(scenarios: pd.DataFrame, cell_meta: pd.DataFrame, e72_pos_flat: np.ndarray, masks: dict[str, np.ndarray]) -> pd.DataFrame:
    broad = scenarios[scenarios["is_broad_plausible"]].copy()
    wanted_ids = set(broad["scenario_id"].astype(str))
    group_map = {str(row["scenario_id"]): scenario_group_names(row) for _, row in broad.iterrows()}
    scenario_meta = broad.set_index("scenario_id")
    records: list[dict[str, Any]] = []

    for scenario_id, weights, achieved, fractional_cells, full_cells in iter_scenario_weights(e72_pos_flat, masks, wanted_ids):
        nz = np.flatnonzero(weights > 0.0)
        scen = scenario_meta.loc[scenario_id]
        groups = group_map[scenario_id]
        for cell_idx in nz:
            meta = cell_meta.iloc[int(cell_idx)]
            budget_mass = float(weights[cell_idx] * e72_pos_flat[cell_idx])
            for group_name in groups:
                records.append(
                    {
                        "group_name": group_name,
                        "scenario_id": scenario_id,
                        "cell_idx": int(cell_idx),
                        "select_weight": float(weights[cell_idx]),
                        "budget_mass": budget_mass,
                        "budget_mass_per_all": budget_mass / len(e72_pos_flat),
                        "scenario_alpha": float(scen["alpha"]),
                        "scenario_lambda": float(scen["lambda"]),
                        "mask_name": str(scen["mask_name"]),
                        "order_name": str(scen["order_name"]),
                        "gamma": float(scen["gamma"]) if pd.notna(scen["gamma"]) else np.nan,
                        **meta.to_dict(),
                    }
                )
    return pd.DataFrame(records)


def summarize_groups(selected: pd.DataFrame, scenarios: pd.DataFrame) -> pd.DataFrame:
    scenario_counts = defaultdict(int)
    for _, row in scenarios.iterrows():
        for group in scenario_group_names(row):
            scenario_counts[group] += 1
    rows: list[dict[str, Any]] = []
    for group_name, group in selected.groupby("group_name", sort=False):
        total_mass = float(group["budget_mass"].sum())
        total_weight = float(group["select_weight"].sum())
        def mass_share(mask: pd.Series) -> float:
            return float(group.loc[mask.to_numpy(bool), "budget_mass"].sum() / total_mass) if total_mass > 0 else np.nan
        rows.append(
            {
                "group_name": group_name,
                "n_scenarios": int(scenario_counts[group_name]),
                "selected_records": int(len(group)),
                "budget_mass": total_mass,
                "select_weight_sum": total_weight,
                "avg_selected_weight_per_scenario": total_weight / max(int(scenario_counts[group_name]), 1),
                "q_target_mass_share": mass_share(group["target_group"].eq("Q")),
                "s_target_mass_share": mass_share(group["target_group"].eq("S")),
                "q2s3_mass_share": mass_share(group["target_is_q2s3"]),
                "e101_active_mass_share": mass_share(group["e101_active"]),
                "e95_fallback_mass_share": mass_share(group["e95_fallback_cell"]),
                "e95_moved_mass_share": mass_share(group["e95_moved_vs_mixmin"]),
                "edge_like_mass_share": mass_share(group["edge_like"]),
                "between_train_runs_mass_share": mass_share(group["context_type"].eq("between_train_runs")),
                "weekend_mass_share": mass_share(group["is_weekend"].eq(1)),
                "median_alpha": float(group.drop_duplicates("scenario_id")["scenario_alpha"].median()),
                "median_lambda": float(group.drop_duplicates("scenario_id")["scenario_lambda"].median()),
            }
        )
    return pd.DataFrame(rows).sort_values("group_name")


def summarize_categories(selected: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    fields = ["target", "target_group", "target_is_q2s3", "e101_active", "e95_fallback_cell", "context_type", "pos_bin", "block_len_bin", "edge_like", "subject_id"]
    for group_name, group in selected.groupby("group_name", sort=False):
        total_mass = float(group["budget_mass"].sum())
        for field in fields:
            for value, sub in group.groupby(field, dropna=False, sort=False):
                mass = float(sub["budget_mass"].sum())
                rows.append(
                    {
                        "group_name": group_name,
                        "field": field,
                        "value": str(value),
                        "selected_records": int(len(sub)),
                        "budget_mass": mass,
                        "budget_share": mass / total_mass if total_mass > 0 else np.nan,
                        "weight_share": float(sub["select_weight"].sum() / group["select_weight"].sum()) if group["select_weight"].sum() > 0 else np.nan,
                        "n_scenarios": int(sub["scenario_id"].nunique()),
                    }
                )
    return pd.DataFrame(rows).sort_values(["group_name", "field", "budget_share"], ascending=[True, True, False])


def write_report(group_summary: pd.DataFrame, category: pd.DataFrame) -> None:
    view_groups = group_summary[group_summary["group_name"].isin(["broad", "e101_plausible", "broad_q2s3", "broad_all_or_top50", "broad_low_alpha", "broad_tail_equal"])]
    key_cats = category[
        category["group_name"].isin(["e101_plausible", "broad_q2s3", "broad_all_or_top50"])
        & category["field"].isin(["target", "target_group", "target_is_q2s3", "e101_active", "e95_fallback_cell", "context_type", "pos_bin"])
    ].copy()
    key_cats = key_cats.groupby(["group_name", "field"], group_keys=False).head(5)

    e101 = group_summary[group_summary["group_name"].eq("e101_plausible")].iloc[0]
    q2s3 = group_summary[group_summary["group_name"].eq("broad_q2s3")].iloc[0]
    all_top = group_summary[group_summary["group_name"].eq("broad_all_or_top50")].iloc[0]

    report = f"""# E126 E101 survivor cell-budget anatomy

## Question

E125 showed that E101-compatible scenarios are not q2s3-mask scenarios. E126
reconstructs the actual E72-adverse cells selected by the scenarios and asks:
what kind of public-miss budget makes E101's local rollback fail to transfer?

## Group Summary

{md_table(view_groups[[
    'group_name',
    'n_scenarios',
    'avg_selected_weight_per_scenario',
    'q_target_mass_share',
    's_target_mass_share',
    'q2s3_mass_share',
    'e101_active_mass_share',
    'e95_fallback_mass_share',
    'e95_moved_mass_share',
    'edge_like_mass_share',
    'between_train_runs_mass_share',
    'median_alpha',
]], '.6f')}

## Category Detail

{md_table(key_cats[[
    'group_name',
    'field',
    'value',
    'budget_share',
    'weight_share',
    'n_scenarios',
]], '.6f')}

## Interpretation

- E101-plausible selected budget has q2s3 mass share `{float(e101['q2s3_mass_share']):.6f}` and E101-active mass share `{float(e101['e101_active_mass_share']):.6f}`.
- Broad q2s3 worlds have q2s3 mass share `{float(q2s3['q2s3_mass_share']):.6f}` and E101-active mass share `{float(q2s3['e101_active_mass_share']):.6f}`.
- Broad all/top50 worlds have q2s3 mass share `{float(all_top['q2s3_mass_share']):.6f}` and E101-active mass share `{float(all_top['e101_active_mass_share']):.6f}`.

The E101-compatible budget is not concentrated on the cells E101 actually
changes. It is broader, more S-heavy, and closer to E95's generic hard-tail
field than to the active Q2/S3 rollback. That explains why local alpha collapses:
the public-compatible tail budget charges many cells outside the E101 move, so
E101's apparent local edge is mostly not on the realized public-loss surface.

## Decision

No submission. Same-line E95-to-E101 variants remain closed. The next useful
experiment should ask whether a different hidden structure can predict this
public-transfer shrinkage field before probability movement is attempted.
"""
    REPORT_OUT.write_text(report)


def main() -> None:
    scenarios = pd.read_csv(SCENARIOS_IN)
    sample = load_sub(FILES["mixmin"]).sort_values(KEYS).reset_index(drop=True)
    train, sample_from_data = hbr.read_data()
    sample_from_data = sample_from_data.sort_values(KEYS).reset_index(drop=True)
    train = train.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True)
    if not sample[KEYS].equals(sample_from_data[KEYS]):
        raise RuntimeError("submission sample keys do not match data sample keys")

    preds = {name: load_pred(file_name, sample) for name, file_name in FILES.items()}
    base = preds["mixmin"]
    e72 = preds["failed_e72"]
    e72_delta = logit(e72) - logit(base)
    wrong_is_zero = e72_delta > EPS
    wrong_is_one = e72_delta < -EPS
    adverse = {
        name: e96.adverse_delta_for_e72_direction(pred, base, wrong_is_zero, wrong_is_one)
        for name, pred in preds.items()
    }
    e72_pos = np.maximum(adverse["failed_e72"], 0.0)
    masks = e96.build_masks(preds, e72_pos, e72_delta)
    row_meta = build_hidden_row_meta(train, sample)
    cell_meta = build_flat_cell_meta(sample, row_meta, preds, masks, e72_pos, e72_delta)
    selected = reconstruct_selected_records(scenarios, cell_meta, e72_pos.reshape(-1), masks)
    group_summary = summarize_groups(selected, scenarios)
    category = summarize_categories(selected)

    selected.to_csv(SELECTED_OUT, index=False)
    group_summary.to_csv(GROUP_OUT, index=False)
    category.to_csv(CATEGORY_OUT, index=False)
    write_report(group_summary, category)

    print("Wrote:")
    for path in [SELECTED_OUT, GROUP_OUT, CATEGORY_OUT, REPORT_OUT]:
        print(f"- {path.relative_to(ROOT)}")
    print(group_summary.to_string(index=False))


if __name__ == "__main__":
    main()
