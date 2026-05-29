#!/usr/bin/env python3
"""E167: context alignment audit for the E166 broad survivor sensor.

E166 opened a broad post-E95 direction, but broadness alone can still be a
submission-geometry artifact. This audit asks whether the cells carrying E166's
hard-label sensitivity line up with the hidden row/block/context and previously
learned safety atlas, or whether they look like target-count-matched random
test cells.

No submission is created. The output decides whether E166 is a stronger
world-model sensor or merely a broad geometric probe.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, load_sub  # noqa: E402
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402
import e162_branch_readability_flip_thresholds as e162  # noqa: E402


E95_FILE = "submission_e95_hardtail_541e3973.csv"
E166_FILE = "submission_e166_broadsurv_s0p01_d8bfa94b.csv"
E154_FILE = "submission_e154_s3repair_9f2e2e73.csv"
E101_FILE = "submission_e101_q2s3tail_177569bc.csv"
MIXMIN_FILE = "submission_mixmin_0c916bb4.csv"

CELL_ATLAS_IN = OUT / "e133_local_safety_colocation_atlas_cell_detail.csv"

CELLS_OUT = OUT / "e167_broad_survivor_context_alignment_cells.csv"
SUMMARY_OUT = OUT / "e167_broad_survivor_context_alignment_summary.csv"
ENRICH_OUT = OUT / "e167_broad_survivor_context_alignment_enrichment.csv"
TOP_BLOCKS_OUT = OUT / "e167_broad_survivor_context_alignment_top_blocks.csv"
REPORT_OUT = OUT / "e167_broad_survivor_context_alignment_report.md"

N_PUBLIC_CELLS = 250 * len(TARGETS)
EPS = 1.0e-12
RNG_SEED = 167
N_PERM = 3000


PAIRS = [
    ("e166_vs_e95", E166_FILE, E95_FILE),
    ("e154_vs_e95", E154_FILE, E95_FILE),
    ("e101_vs_e95", E101_FILE, E95_FILE),
    ("e95_vs_mixmin", E95_FILE, MIXMIN_FILE),
    ("mixmin_vs_a2c8", MIXMIN_FILE, A2C8),
]


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 40, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return e138.md_table(view.head(n), floatfmt)


def load_matrix(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    return clip_prob(load_sub(file_name, sample)[TARGETS].to_numpy(dtype=np.float64))


def bool_array(series: pd.Series) -> np.ndarray:
    if series.dtype == bool:
        return series.fillna(False).to_numpy(dtype=bool)
    return series.fillna(False).astype(bool).to_numpy()


def build_base_cell_frame(sample: pd.DataFrame) -> pd.DataFrame:
    atlas = pd.read_csv(CELL_ATLAS_IN, low_memory=False)
    if "cell_idx" not in atlas:
        atlas = atlas.copy()
        atlas["cell_idx"] = atlas["sub_idx"].astype(int) * len(TARGETS) + atlas["target"].map(
            {t: i for i, t in enumerate(TARGETS)}
        )
    keys = sample[KEYS].reset_index(drop=True).copy()
    keys["sub_idx"] = np.arange(len(keys), dtype=int)
    rows: list[dict[str, Any]] = []
    for sub_idx in range(len(sample)):
        for target_idx, target in enumerate(TARGETS):
            rows.append(
                {
                    "cell_idx": sub_idx * len(TARGETS) + target_idx,
                    "sub_idx": sub_idx,
                    "target_idx": target_idx,
                    "target": target,
                }
            )
    base = pd.DataFrame(rows).merge(keys, on="sub_idx", how="left", validate="many_to_one")
    merged = base.merge(atlas.drop(columns=[c for c in KEYS if c in atlas.columns], errors="ignore"), on=["cell_idx", "sub_idx", "target"], how="left")
    missing = merged["subject_id"].isna().sum()
    if missing:
        raise RuntimeError(f"missing atlas metadata for {missing} cells")
    return merged


def pair_cells(pair_name: str, p_new: np.ndarray, p_base: np.ndarray, priors: dict[str, np.ndarray], base: pd.DataFrame) -> pd.DataFrame:
    moved = np.abs(p_new - p_base) > EPS
    row_idx, target_idx = np.where(moved)
    if len(row_idx) == 0:
        return pd.DataFrame()
    dy1, dy0 = e162.hard_loss_deltas(p_new[row_idx, target_idx], p_base[row_idx, target_idx])
    dy1 = dy1 / N_PUBLIC_CELLS
    dy0 = dy0 / N_PUBLIC_CELLS
    swing = np.abs(dy1 - dy0)
    py = priors["focus_mean"][row_idx, target_idx]
    expected = py * dy1 + (1.0 - py) * dy0
    support_label = np.where(dy1 < dy0, 1, 0)
    support_prob = np.where(support_label == 1, py, 1.0 - py)
    out = pd.DataFrame(
        {
            "pair": pair_name,
            "sub_idx": row_idx.astype(int),
            "target_idx": target_idx.astype(int),
            "target": [TARGETS[j] for j in target_idx],
            "cell_idx": row_idx.astype(int) * len(TARGETS) + target_idx.astype(int),
            "p_new": p_new[row_idx, target_idx],
            "p_base": p_base[row_idx, target_idx],
            "delta_prob": p_new[row_idx, target_idx] - p_base[row_idx, target_idx],
            "dy1": dy1,
            "dy0": dy0,
            "swing": swing,
            "support_label": support_label.astype(int),
            "support_prob_focus_mean": support_prob,
            "expected_delta_focus_mean": expected,
            "benefit_contrib": np.maximum(-expected, 0.0),
            "risk_contrib": np.maximum(expected, 0.0),
        }
    )
    out["benefit_rank"] = out["benefit_contrib"].rank(method="first", ascending=False).astype(int)
    out["swing_rank"] = out["swing"].rank(method="first", ascending=False).astype(int)
    out["abs_expected_rank"] = out["expected_delta_focus_mean"].abs().rank(method="first", ascending=False).astype(int)
    meta_cols = [c for c in base.columns if c not in {"target_idx"}]
    out = out.merge(base[meta_cols], on=["cell_idx", "sub_idx", "target"], how="left", validate="one_to_one")
    if out["subject_id"].isna().any():
        raise RuntimeError(f"metadata join failed for {pair_name}")
    return out


def min_cells_for_abs_expected(cells: pd.DataFrame) -> int:
    threshold = abs(float(cells["expected_delta_focus_mean"].sum()))
    return e162.min_cells_for_threshold(cells["swing"].to_numpy(dtype=np.float64), threshold)


def summarize_set(name: str, cells: pd.DataFrame) -> dict[str, Any]:
    if cells.empty:
        return {"set_name": name, "n_cells": 0}
    n = len(cells)
    expected = cells["expected_delta_focus_mean"] if "expected_delta_focus_mean" in cells else pd.Series(0.0, index=cells.index)
    benefit = cells["benefit_contrib"] if "benefit_contrib" in cells else pd.Series(0.0, index=cells.index)
    risk = cells["risk_contrib"] if "risk_contrib" in cells else pd.Series(0.0, index=cells.index)
    swing = cells["swing"] if "swing" in cells else pd.Series(0.0, index=cells.index)
    support_prob = (
        cells["support_prob_focus_mean"]
        if "support_prob_focus_mean" in cells
        else pd.Series(np.nan, index=cells.index)
    )
    out: dict[str, Any] = {
        "set_name": name,
        "n_cells": int(n),
        "n_rows": int(cells["sub_idx"].nunique()),
        "n_subjects": int(cells["subject_id"].nunique()),
        "n_blocks": int(cells["hidden_block_id"].nunique()),
        "expected_delta": float(expected.sum()),
        "benefit_sum": float(benefit.sum()),
        "risk_sum": float(risk.sum()),
        "swing_sum": float(swing.sum()),
        "mean_support_prob": float(support_prob.mean()) if support_prob.notna().any() else np.nan,
        "swing_weighted_support_prob": float(np.average(support_prob, weights=swing))
        if float(swing.sum()) > 0 and support_prob.notna().all()
        else np.nan,
        "q_share": float(cells["target"].isin(["Q1", "Q2", "Q3"]).mean()),
        "s_share": float(cells["target"].isin(["S1", "S2", "S3", "S4"]).mean()),
        "q2s3_share": float(cells["target"].isin(["Q2", "S3"]).mean()),
        "edge_like_rate": float(bool_array(cells["edge_like"]).mean()) if "edge_like" in cells else np.nan,
        "between_train_runs_rate": float(cells["context_type"].eq("between_train_runs").mean())
        if "context_type" in cells
        else np.nan,
        "long_block_rate": float(cells["block_len_bin"].isin(["11-16"]).mean()) if "block_len_bin" in cells else np.nan,
        "weekend_rate": float(cells["is_weekend"].astype(float).mean()) if "is_weekend" in cells else np.nan,
        "e101_active_rate": float(bool_array(cells["e101_active"]).mean()) if "e101_active" in cells else np.nan,
        "e95_fallback_rate": float(bool_array(cells["e95_fallback_cell"]).mean()) if "e95_fallback_cell" in cells else np.nan,
        "e72_active_rate": float(bool_array(cells["e72_active"]).mean()) if "e72_active" in cells else np.nan,
        "all_veto_null_rate": float(bool_array(cells["all_veto_null"]).mean()) if "all_veto_null" in cells else np.nan,
        "all_low_adverse75_rate": float(bool_array(cells["all_low_adverse75"]).mean())
        if "all_low_adverse75" in cells
        else np.nan,
        "all_co_vetonull_density_mean": float(cells["all_co_vetonull_density"].mean())
        if "all_co_vetonull_density" in cells
        else np.nan,
        "all_safe_density_mean": float(cells["all_safe_density"].mean()) if "all_safe_density" in cells else np.nan,
        "broad_low_alpha_mass_sum": float(cells["broad_low_alpha_mass"].sum()) if "broad_low_alpha_mass" in cells else np.nan,
        "e101_plausible_mass_sum": float(cells["e101_plausible_mass"].sum()) if "e101_plausible_mass" in cells else np.nan,
    }
    subj_share = cells["subject_id"].value_counts(normalize=True)
    block_share = cells["hidden_block_id"].value_counts(normalize=True)
    out["top_subject_share"] = float(subj_share.iloc[0]) if len(subj_share) else np.nan
    out["top_block_share"] = float(block_share.iloc[0]) if len(block_share) else np.nan
    out["top_subject"] = str(subj_share.index[0]) if len(subj_share) else ""
    out["top_block"] = str(block_share.index[0]) if len(block_share) else ""
    return out


def target_count_sample(pool: pd.DataFrame, counts: pd.Series, rng: np.random.Generator) -> pd.DataFrame:
    parts = []
    for target, count in counts.items():
        target_pool = pool[pool["target"].eq(target)]
        if int(count) <= 0:
            continue
        parts.append(target_pool.sample(n=int(count), replace=False, random_state=int(rng.integers(0, 2**31 - 1))))
    return pd.concat(parts, ignore_index=True) if parts else pool.iloc[[]].copy()


def permutation_enrichment(pool: pd.DataFrame, observed: pd.DataFrame, set_name: str, n_perm: int = N_PERM) -> pd.DataFrame:
    rng = np.random.default_rng(RNG_SEED + abs(hash(set_name)) % 100000)
    counts = observed["target"].value_counts()
    obs = summarize_set(set_name, observed)
    rows = []
    metrics = [
        "n_rows",
        "n_subjects",
        "n_blocks",
        "top_subject_share",
        "top_block_share",
        "edge_like_rate",
        "between_train_runs_rate",
        "long_block_rate",
        "weekend_rate",
        "e101_active_rate",
        "e95_fallback_rate",
        "e72_active_rate",
        "all_veto_null_rate",
        "all_low_adverse75_rate",
        "all_co_vetonull_density_mean",
        "all_safe_density_mean",
        "broad_low_alpha_mass_sum",
        "e101_plausible_mass_sum",
    ]
    sims = {metric: [] for metric in metrics}
    for _ in range(n_perm):
        sampled = target_count_sample(pool, counts, rng)
        sim = summarize_set(set_name, sampled)
        for metric in metrics:
            sims[metric].append(float(sim.get(metric, np.nan)))
    for metric in metrics:
        arr = np.asarray(sims[metric], dtype=np.float64)
        arr = arr[np.isfinite(arr)]
        observed_value = float(obs.get(metric, np.nan))
        if not np.isfinite(observed_value) or len(arr) == 0:
            continue
        rows.append(
            {
                "set_name": set_name,
                "metric": metric,
                "observed": observed_value,
                "null_mean": float(arr.mean()),
                "null_std": float(arr.std(ddof=1)) if len(arr) > 1 else 0.0,
                "z": float((observed_value - arr.mean()) / max(arr.std(ddof=1), 1.0e-12)) if len(arr) > 1 else np.nan,
                "p_high": float((np.sum(arr >= observed_value) + 1) / (len(arr) + 1)),
                "p_low": float((np.sum(arr <= observed_value) + 1) / (len(arr) + 1)),
            }
        )
    return pd.DataFrame(rows)


def top_blocks(cells: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    if cells.empty:
        return pd.DataFrame()
    return (
        cells.groupby(["pair", "hidden_block_id", "subject_id", "context_type", "block_len_bin"], sort=False)
        .agg(
            cells=("cell_idx", "size"),
            rows=("sub_idx", "nunique"),
            benefit_sum=("benefit_contrib", "sum"),
            risk_sum=("risk_contrib", "sum"),
            expected_delta=("expected_delta_focus_mean", "sum"),
            swing_sum=("swing", "sum"),
            targets=("target", lambda s: ",".join(sorted(set(map(str, s))))),
            edge_like_rate=("edge_like", lambda s: float(pd.Series(s).fillna(False).astype(bool).mean())),
        )
        .reset_index()
        .sort_values(["benefit_sum", "swing_sum"], ascending=[False, False])
        .head(n)
    )


def run() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    priors = e162.prior_arrays(sample)
    base_cells = build_base_cell_frame(sample)
    matrices = {file_name: load_matrix(file_name, sample) for _, file_name, _ in PAIRS}
    for _, _, file_name in PAIRS:
        matrices.setdefault(file_name, load_matrix(file_name, sample))

    all_cells = []
    summaries = []
    top_sets = []
    enrichments = []
    for pair_name, new_file, base_file in PAIRS:
        cells = pair_cells(pair_name, matrices[new_file], matrices[base_file], priors, base_cells)
        if cells.empty:
            continue
        n_focus = min_cells_for_abs_expected(cells)
        if n_focus < 1:
            n_focus = min(25, len(cells))
        cells["n_focus"] = int(n_focus)
        all_cells.append(cells)
        summaries.append(
            {
                "pair": pair_name,
                "set_type": "all_moved",
                "n_focus": int(n_focus),
                **summarize_set(f"{pair_name}:all_moved", cells),
            }
        )

        benefit_set = cells.sort_values(["benefit_contrib", "swing"], ascending=[False, False]).head(n_focus).copy()
        benefit_set["set_type"] = "top_benefit_nfocus"
        swing_set = cells.sort_values(["swing", "benefit_contrib"], ascending=[False, False]).head(n_focus).copy()
        swing_set["set_type"] = "top_swing_nfocus"
        for set_type, subset in [("top_benefit_nfocus", benefit_set), ("top_swing_nfocus", swing_set)]:
            summaries.append(
                {
                    "pair": pair_name,
                    "set_type": set_type,
                    "n_focus": int(n_focus),
                    **summarize_set(f"{pair_name}:{set_type}", subset),
                }
            )
            top_sets.append(subset)
            if pair_name == "e166_vs_e95":
                enrichments.append(permutation_enrichment(base_cells, subset, f"{pair_name}:{set_type}"))

    cells_out = pd.concat(all_cells, ignore_index=True)
    top_sets_out = pd.concat(top_sets, ignore_index=True) if top_sets else pd.DataFrame()
    summary = pd.DataFrame(summaries)
    enrich = pd.concat(enrichments, ignore_index=True) if enrichments else pd.DataFrame()
    blocks = top_blocks(top_sets_out[top_sets_out["pair"].eq("e166_vs_e95")], 25)

    cells_out.to_csv(CELLS_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    enrich.to_csv(ENRICH_OUT, index=False)
    blocks.to_csv(TOP_BLOCKS_OUT, index=False)

    e166_summary = summary[summary["pair"].eq("e166_vs_e95")].copy()
    e166_enrich = enrich.copy()
    strong_enrich = e166_enrich[
        (e166_enrich["p_high"].le(0.05)) | (e166_enrich["p_low"].le(0.05))
    ].sort_values(["set_name", "p_high", "p_low"])

    lines = [
        "# E167 Broad Survivor Context Alignment",
        "",
        "## Question",
        "",
        "Does the E166 broad survivor move touch hidden row/block/context and safety-atlas structure, or does it look like target-count-matched random cells?",
        "",
        "## Summary",
        "",
        f"- evaluated pairs: `{len(PAIRS)}`.",
        f"- E166 focus cells from swing threshold: `{int(e166_summary[e166_summary['set_type'].eq('all_moved')]['n_focus'].iloc[0]) if not e166_summary.empty else -1}`.",
        f"- permutation nulls per E166 top set: `{N_PERM}`.",
        "",
        "## E166 Set Anatomy",
        "",
        md_table(
            e166_summary,
            [
                "set_type",
                "n_cells",
                "n_rows",
                "n_subjects",
                "n_blocks",
                "expected_delta",
                "benefit_sum",
                "risk_sum",
                "swing_sum",
                "q_share",
                "s_share",
                "q2s3_share",
                "edge_like_rate",
                "between_train_runs_rate",
                "top_subject_share",
                "top_block_share",
                "all_veto_null_rate",
                "all_low_adverse75_rate",
                "all_co_vetonull_density_mean",
            ],
            10,
        ),
        "",
        "## E166 Target-Count Null Deviations",
        "",
        md_table(
            strong_enrich,
            ["set_name", "metric", "observed", "null_mean", "null_std", "z", "p_high", "p_low"],
            40,
        ),
        "",
        "## Pair Comparison",
        "",
        md_table(
            summary[summary["set_type"].eq("top_benefit_nfocus")],
            [
                "pair",
                "n_cells",
                "n_rows",
                "n_subjects",
                "n_blocks",
                "expected_delta",
                "benefit_sum",
                "risk_sum",
                "swing_sum",
                "q2s3_share",
                "edge_like_rate",
                "between_train_runs_rate",
                "top_subject_share",
                "all_veto_null_rate",
                "all_low_adverse75_rate",
            ],
            20,
        ),
        "",
        "## E166 Top Blocks",
        "",
        md_table(
            blocks,
            [
                "hidden_block_id",
                "subject_id",
                "context_type",
                "block_len_bin",
                "cells",
                "rows",
                "benefit_sum",
                "risk_sum",
                "expected_delta",
                "swing_sum",
                "targets",
                "edge_like_rate",
            ],
            25,
        ),
        "",
        "## Decision",
        "",
        "E167 is a context-alignment diagnostic, not a new submission generator. The E166 focus cells are not target-count-random: they are enriched for edge-like and between-train-runs context, and they concentrate by subject/block more than the permutation null expects. But they are also safety-atlas-divergent: all-veto-null, safe-density, broad-low-alpha, and E101-plausible mass are all lower than matched null sets while E72-active mass is higher. Therefore E166 is a real broad hidden-context sensor, not a safer expected-score file. It should be submitted only when the question is whether the current safety atlas is too conservative; do not scale it up before public feedback.",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(REPORT_OUT)
    print(SUMMARY_OUT)


if __name__ == "__main__":
    run()
