#!/usr/bin/env python3
"""E74 stability stress for the E72/E73 sparse Q2/S3 gate.

E72 found deployable non-`none` gates after E71's sign/agreement gates failed.
E73 materialized the best `top_abs50` row. This probe asks whether that sparse
gate is a broad consensus or a fragile consequence of a few influential cells.

No submission is written by this script.
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

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, load_sub, logit  # noqa: E402
import gradient_consensus_posterior_probe as e63  # noqa: E402
import mixmin_hard_posterior_distillation_probe as e58  # noqa: E402
import mixmin_hard_raw_world_probe as e56  # noqa: E402
import q2_s3_strict_cell_amplitude_probe as e69  # noqa: E402
import q2_s3_strict_cell_consensus_probe as e70  # noqa: E402
import q2_s3_unified_gate_geometry_probe as e72  # noqa: E402
import q2_s3_unified_strict_cell_consensus_probe as e71  # noqa: E402
import raw_block_target_dependency_probe as e55  # noqa: E402


SCAN_OUT = OUT / "q2_s3_sparse_gate_stability_probe_scan.csv"
SUMMARY_OUT = OUT / "q2_s3_sparse_gate_stability_probe_summary.csv"
REPORT_OUT = OUT / "q2_s3_sparse_gate_stability_probe_report.md"

POOL_NAME = "translator_tail_soft_p90_m0.50"
BASE_AGG = "mean"
DELTA_AGG = "signed_p75"
GATE = "top_abs50"
ALPHAS = [8.0, 12.0, 16.0, 20.0, 24.0]
BOOTSTRAP_N = 60
BOOTSTRAP_SIZE = 8
MIN_CELLS = 4
RNG_SEED = 20260529
QS_IDXS = e70.QS_IDXS


def stable_subset_name(idxs: np.ndarray) -> str:
    return "-".join(map(str, sorted(map(int, idxs))))


def add_variant(
    variants: list[dict[str, Any]],
    seen: set[tuple[int, ...]],
    kind: str,
    name: str,
    idxs: np.ndarray,
    reason: str,
) -> None:
    idxs = np.asarray(sorted(set(map(int, idxs))), dtype=int)
    if len(idxs) < MIN_CELLS:
        return
    key = tuple(idxs.tolist())
    if kind != "jackknife" and key in seen:
        return
    seen.add(key)
    variants.append(
        {
            "variant_kind": kind,
            "variant_name": name,
            "reason": reason,
            "idxs": idxs,
            "subset_key": stable_subset_name(idxs),
        }
    )


def make_variants(cells: pd.DataFrame, pool_idxs: np.ndarray) -> list[dict[str, Any]]:
    pool = cells.loc[pool_idxs].copy()
    variants: list[dict[str, Any]] = []
    seen: set[tuple[int, ...]] = set()
    add_variant(variants, seen, "reference", "full_pool", pool_idxs, "E73 selected pool")

    for idx in pool_idxs:
        add_variant(
            variants,
            seen,
            "jackknife",
            f"drop_cell_{int(idx):03d}",
            np.asarray([x for x in pool_idxs if int(x) != int(idx)], dtype=int),
            f"leave out cell {int(idx)}",
        )

    for col in ["support_count", "heldout_set", "band", "base_cell_gate", "gradient_gate", "shape", "scale", "cap"]:
        for value, group in pool.groupby(col, dropna=False):
            safe_value = str(value).replace(",", "_").replace(" ", "_")
            add_variant(
                variants,
                seen,
                "group_keep",
                f"{col}_{safe_value}",
                group.index.to_numpy(dtype=int),
                f"keep {col}={value}",
            )

    for metric, ascending in [
        ("heldout_minus_base", True),
        ("world_support_minus_base", True),
        ("hidden_q2s3_mean_minus_base", True),
        ("block_q2s3_beats_base_rate", False),
    ]:
        ordered = pool.sort_values(metric, ascending=ascending).index.to_numpy(dtype=int)
        for size in [6, 8, 10]:
            add_variant(
                variants,
                seen,
                "rank_keep",
                f"{metric}_top{size}",
                ordered[:size],
                f"keep best {size} by {metric}",
            )

    rng = np.random.default_rng(RNG_SEED)
    boot_seen: set[tuple[int, ...]] = set()
    attempts = 0
    while len(boot_seen) < BOOTSTRAP_N and attempts < BOOTSTRAP_N * 30:
        attempts += 1
        idxs = tuple(sorted(map(int, rng.choice(pool_idxs, size=BOOTSTRAP_SIZE, replace=False))))
        if idxs in boot_seen:
            continue
        boot_seen.add(idxs)
        add_variant(
            variants,
            seen,
            "bootstrap8",
            f"bootstrap8_{len(boot_seen):03d}",
            np.asarray(idxs, dtype=int),
            f"deterministic random {BOOTSTRAP_SIZE}-of-{len(pool_idxs)} subset",
        )
    return variants


def weighted_delta(cells: pd.DataFrame, idxs: np.ndarray, delta_all: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    pool = cells.loc[idxs].copy()
    raw_weight = (
        pool["support_count"].to_numpy(dtype=np.float64)
        * (
            -pool["heldout_minus_base"].to_numpy(dtype=np.float64)
            + 0.20 * -pool["world_support_minus_base"].to_numpy(dtype=np.float64)
            + 0.05 * -pool["hidden_q2s3_mean_minus_base"].to_numpy(dtype=np.float64)
        )
    )
    raw_weight = np.maximum(raw_weight, 0.0) + 1e-12
    weights = raw_weight / raw_weight.sum()
    return e70.aggregate_delta(delta_all[idxs], weights, DELTA_AGG), weights


def build_stability_candidates(
    cells: pd.DataFrame,
    bases: list[np.ndarray],
    deltas: list[np.ndarray],
) -> tuple[pd.DataFrame, list[np.ndarray], list[dict[str, Any]]]:
    base_logits_all = np.stack([logit(x) for x in bases], axis=0)
    delta_all = np.stack(deltas, axis=0)
    pool_idxs = e71.make_unified_pools(cells)[POOL_NAME]
    variants = make_variants(cells, pool_idxs)
    rows: list[dict[str, Any]] = []
    preds: list[np.ndarray] = []
    seen: dict[str, int] = {}

    for variant_id, variant in enumerate(variants):
        idxs = variant["idxs"]
        pool = cells.loc[idxs].copy()
        base_logit = e70.aggregate_base(base_logits_all[idxs], BASE_AGG)
        base_pred = e70.clip_prob(e70.sigmoid(base_logit))
        base_tag = e72.e68_tag(base_pred, f"e74_base_{variant['variant_name']}_")
        if base_tag in seen:
            bidx = seen[base_tag]
        else:
            bidx = len(preds)
            seen[base_tag] = bidx
            preds.append(base_pred)

        delta, weights = weighted_delta(cells, idxs, delta_all)
        gate = e72.adaptive_gate(delta_all[idxs], delta, GATE)
        gated_delta = delta * gate
        gate_active = float((np.abs(gate[:, QS_IDXS]) > 0.0).mean())
        gate_weight = float(gate[:, QS_IDXS].mean())
        unit_move = float(np.abs(gated_delta[:, QS_IDXS]).mean())
        if unit_move <= 1e-12:
            continue
        for alpha in ALPHAS:
            pred = e70.clip_prob(e70.sigmoid(base_logit + float(alpha) * gated_delta))
            tag = e72.e68_tag(pred, f"e74_{variant['variant_name']}_{alpha:.2f}_")
            if tag in seen:
                pred_index = seen[tag]
            else:
                pred_index = len(preds)
                seen[tag] = pred_index
                preds.append(pred)
            rows.append(
                {
                    "pred_index": pred_index,
                    "base_index": bidx,
                    "tag": tag,
                    "base_tag": base_tag,
                    "variant_id": variant_id,
                    "variant_kind": variant["variant_kind"],
                    "variant_name": variant["variant_name"],
                    "reason": variant["reason"],
                    "subset_key": variant["subset_key"],
                    "pool": POOL_NAME,
                    "pool_size": int(len(idxs)),
                    "pool_support_mean": float(pool["support_count"].mean()),
                    "pool_support2_count": int(pool["support_count"].ge(2).sum()),
                    "base_agg": BASE_AGG,
                    "delta_agg": DELTA_AGG,
                    "gate": GATE,
                    "alpha": float(alpha),
                    "gate_active_q2s3": gate_active,
                    "gate_weight_q2s3_mean": gate_weight,
                    "mean_abs_q2s3_delta_unit": unit_move,
                    "weight_max": float(weights.max()),
                    "weight_entropy": float(-(weights * np.log(weights + 1e-12)).sum()),
                    "cell_heldout_mean": float(pool["heldout_minus_base"].mean()),
                    "cell_world_mean": float(pool["world_support_minus_base"].mean()),
                    "cell_hidden_q2s3_mean": float(pool["hidden_q2s3_mean_minus_base"].mean()),
                    "cell_block_win_mean": float(pool["block_q2s3_beats_base_rate"].mean()),
                }
            )
    return pd.DataFrame(rows), preds, variants


def add_reference_distance(scan: pd.DataFrame, preds: list[np.ndarray], mixmin: np.ndarray) -> pd.DataFrame:
    out = scan.copy()
    ref_rows = out[
        out["variant_kind"].eq("reference")
        & out["variant_name"].eq("full_pool")
        & out["alpha"].eq(16.0)
    ]
    if len(ref_rows) != 1:
        raise RuntimeError(f"expected one E74 reference row at alpha 16, found {len(ref_rows)}")
    ref_pred = preds[int(ref_rows.iloc[0]["pred_index"])]
    ref_logit = logit(ref_pred)
    mix_logit = logit(mixmin)
    ref_move = np.abs(ref_logit[:, QS_IDXS] - mix_logit[:, QS_IDXS])
    ref_threshold = np.quantile(ref_move[ref_move > 0], 0.50)
    ref_active = ref_move >= ref_threshold
    rows = []
    for i, pred in enumerate(preds):
        cur_logit = logit(pred)
        cur_move = np.abs(cur_logit[:, QS_IDXS] - mix_logit[:, QS_IDXS])
        cur_threshold = np.quantile(cur_move[cur_move > 0], 0.50) if np.any(cur_move > 0) else np.inf
        cur_active = cur_move >= cur_threshold
        union = ref_active | cur_active
        inter = ref_active & cur_active
        rows.append(
            {
                "pred_index": i,
                "mean_abs_logit_delta_vs_e73": float(np.abs(cur_logit - ref_logit).mean()),
                "mean_abs_q2s3_logit_delta_vs_e73": float(np.abs(cur_logit[:, QS_IDXS] - ref_logit[:, QS_IDXS]).mean()),
                "q2s3_topabs_jaccard_vs_e73": float(inter.sum() / max(1, union.sum())),
            }
        )
    return out.merge(pd.DataFrame(rows), on="pred_index", how="left")


def score_rows(
    rows: pd.DataFrame,
    preds: list[np.ndarray],
    sample: pd.DataFrame,
    mixmin: np.ndarray,
    labels: np.ndarray,
    worlds: pd.DataFrame,
    views: dict[str, np.ndarray],
    state: e55.BaseState,
) -> pd.DataFrame:
    combo = e70.combo_scores(rows, [mixmin] + preds, sample).reset_index(drop=True)
    combo["row_id"] = np.arange(len(combo), dtype=int)
    base_rows = combo[["row_id", "pred_index", "base_index"]].copy()
    nonanchor = e70.nonanchor_scores(base_rows, preds, mixmin, labels, worlds, views, state)
    metric_cols = [c for c in nonanchor.columns if c not in base_rows.columns and c != "row_id"]
    scan_input = combo.merge(nonanchor[["row_id", *metric_cols]], on="row_id", how="left")
    scan_input["nonanchor_evaluated"] = True
    scan = e70.add_gates(scan_input, preds, mixmin)
    scan = scan.rename(columns={"strict_consensus_gate": "strict_gate", "loose_consensus_gate": "loose_gate"})
    scan["deployable_gate"] = scan["strict_gate"] & scan["gate"].ne("none")
    scan = add_reference_distance(scan, preds, mixmin)
    return scan.sort_values(
        ["deployable_gate", "strict_gate", "loose_gate", "all_delta_vs_mixmin"],
        ascending=[False, False, False, True],
    ).reset_index(drop=True)


def summarize(scan: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for kind, group in scan.groupby("variant_kind", sort=False):
        alpha16 = group[group["alpha"].eq(16.0)]
        rows.append(
            {
                "variant_kind": kind,
                "rows": int(len(group)),
                "variants": int(group["variant_name"].nunique()),
                "strict": int(group["strict_gate"].sum()),
                "deployable": int(group["deployable_gate"].sum()),
                "loose": int(group["loose_gate"].sum()),
                "alpha16_deployable": int(alpha16["deployable_gate"].sum()),
                "alpha16_loose": int(alpha16["loose_gate"].sum()),
                "best_all_delta_vs_mixmin": float(group["all_delta_vs_mixmin"].min()),
                "median_alpha16_all_delta": float(alpha16["all_delta_vs_mixmin"].median()) if len(alpha16) else np.nan,
                "worst_alpha16_all_delta": float(alpha16["all_delta_vs_mixmin"].max()) if len(alpha16) else np.nan,
                "best_all_minus_base": float(group["all_minus_base"].min()),
                "best_hidden_q2s3_minus_base": float(group["hidden_q2s3_mean_minus_base"].min()),
                "best_world_support_minus_base": float(group["world_support_minus_base"].min()),
                "best_block_win_rate": float(group["block_q2s3_beats_base_rate"].max()),
                "median_jaccard_vs_e73": float(alpha16["q2s3_topabs_jaccard_vs_e73"].median()) if len(alpha16) else np.nan,
                "max_q2s3_delta_vs_e73": float(alpha16["mean_abs_q2s3_logit_delta_vs_e73"].max()) if len(alpha16) else np.nan,
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["deployable", "strict", "loose", "best_all_delta_vs_mixmin"],
        ascending=[False, False, False, True],
    )


def write_report(scan: pd.DataFrame, summary: pd.DataFrame, cells: pd.DataFrame, variants: list[dict[str, Any]]) -> None:
    ref = scan[
        scan["variant_kind"].eq("reference")
        & scan["variant_name"].eq("full_pool")
        & scan["alpha"].eq(16.0)
    ].iloc[0]
    jack16 = scan[scan["variant_kind"].eq("jackknife") & scan["alpha"].eq(16.0)].sort_values("all_delta_vs_mixmin")
    best = scan.sort_values("all_delta_vs_mixmin").head(30)
    deployable = scan[scan["deployable_gate"]].sort_values("all_delta_vs_mixmin").head(30)
    by_alpha = (
        scan.groupby(["variant_kind", "alpha"])
        .agg(
            rows=("tag", "size"),
            deployable=("deployable_gate", "sum"),
            strict=("strict_gate", "sum"),
            loose=("loose_gate", "sum"),
            best=("all_delta_vs_mixmin", "min"),
            median=("all_delta_vs_mixmin", "median"),
        )
        .reset_index()
    )
    lines = [
        "# E74 Sparse Q2/S3 Gate Stability Probe",
        "",
        "## Observe",
        "",
        "E73 is the first materialized non-`none` Q2/S3 consensus file, but its selected pool has only `13` cells.",
        "",
        "## Wonder",
        "",
        "Is the E73 sparse-magnitude gate a broad latent consensus, or does it depend on a few fragile cells?",
        "",
        "## Method",
        "",
        f"- Source pool: `{POOL_NAME}`.",
        f"- Source cells in pool: `{len(e71.make_unified_pools(cells)[POOL_NAME])}`.",
        f"- Variants: `{len(variants)}` across reference, jackknife, group-keep, rank-keep, and deterministic bootstrap subsets.",
        f"- Alphas: `{ALPHAS}`; gate: `{GATE}`; base/delta: `{BASE_AGG}`/`{DELTA_AGG}`.",
        "- Every variant is combo-scored and hidden/world/block stressed, not just ranked by all-combo delta.",
        "",
        "## Reference E73 Geometry",
        "",
        e56.markdown_table(
            pd.DataFrame(
                [
                    {
                        "all_delta_vs_mixmin": ref["all_delta_vs_mixmin"],
                        "all_minus_base": ref["all_minus_base"],
                        "worst_set_delta_vs_mixmin": ref["worst_set_delta_vs_mixmin"],
                        "hidden_q2s3_mean_minus_base": ref["hidden_q2s3_mean_minus_base"],
                        "world_support_minus_base": ref["world_support_minus_base"],
                        "block_q2s3_beats_base_rate": ref["block_q2s3_beats_base_rate"],
                        "strict_gate": ref["strict_gate"],
                        "deployable_gate": ref["deployable_gate"],
                    }
                ]
            )
        ),
        "",
        "## Stability Summary",
        "",
        e56.markdown_table(summary),
        "",
        "## Alpha Sensitivity",
        "",
        e56.markdown_table(by_alpha),
        "",
        "## Jackknife At Alpha 16",
        "",
        e56.markdown_table(
            jack16[
                [
                    "variant_name",
                    "pool_size",
                    "pool_support2_count",
                    "all_delta_vs_mixmin",
                    "all_minus_base",
                    "worst_set_delta_vs_mixmin",
                    "hidden_q2s3_mean_minus_base",
                    "world_support_minus_base",
                    "block_q2s3_beats_base_rate",
                    "q2s3_topabs_jaccard_vs_e73",
                    "strict_gate",
                    "deployable_gate",
                    "loose_gate",
                ]
            ]
        ),
        "",
        "## Best Rows",
        "",
        e56.markdown_table(
            best[
                [
                    "variant_kind",
                    "variant_name",
                    "pool_size",
                    "alpha",
                    "all_delta_vs_mixmin",
                    "all_minus_base",
                    "worst_set_delta_vs_mixmin",
                    "hidden_q2s3_mean_minus_base",
                    "world_support_minus_base",
                    "block_q2s3_beats_base_rate",
                    "q2s3_topabs_jaccard_vs_e73",
                    "strict_gate",
                    "deployable_gate",
                    "loose_gate",
                ]
            ]
        ),
        "",
        "## Best Deployable Rows",
        "",
        e56.markdown_table(
            deployable[
                [
                    "variant_kind",
                    "variant_name",
                    "pool_size",
                    "alpha",
                    "all_delta_vs_mixmin",
                    "all_minus_base",
                    "worst_set_delta_vs_mixmin",
                    "hidden_q2s3_mean_minus_base",
                    "world_support_minus_base",
                    "block_q2s3_beats_base_rate",
                    "q2s3_topabs_jaccard_vs_e73",
                    "mean_abs_q2s3_logit_delta_vs_e73",
                ]
            ]
        )
        if len(deployable)
        else "_None._",
        "",
        "## Decision",
        "",
    ]
    jack_deploy = int(jack16["deployable_gate"].sum())
    boot16 = scan[scan["variant_kind"].eq("bootstrap8") & scan["alpha"].eq(16.0)]
    boot_deploy = int(boot16["deployable_gate"].sum())
    if jack_deploy >= max(1, len(jack16) // 2) and boot_deploy > 0:
        lines.append("- E73 is not single-cell fragile: many jackknife variants remain deployable and bootstrap support is non-zero.")
    elif jack_deploy > 0 or boot_deploy > 0:
        lines.append("- E73 has partial sparse-gate stability, but support is not broad enough to call it robust.")
    else:
        lines.append("- E73 is fragile under this stress: no jackknife/bootstrap sparse-gate variant remains deployable.")
    lines.extend(
        [
            "- This probe does not write a new submission. It decides whether the existing E73 file should be treated as robust or as a high-risk public sensor.",
            "",
            "## Outputs",
            "",
            f"- `{SCAN_OUT.relative_to(ROOT)}`",
            f"- `{SUMMARY_OUT.relative_to(ROOT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    mixmin = load_sub(e56.MIXMIN_FILE, sample)[TARGETS].to_numpy(dtype=np.float64)
    a2c8 = load_sub(A2C8, sample)[TARGETS].to_numpy(dtype=np.float64)
    raw_prior, _ = e56.raw_prior_from_e54(sample)
    labels = np.load(e56.LABEL_NPZ_OUT, allow_pickle=True)["labels"].astype(np.float64)
    worlds = pd.read_csv(e56.WORLD_OUT)
    state = e55.build_base_state()
    if not state.sample[KEYS].reset_index(drop=True).equals(sample[KEYS].reset_index(drop=True)):
        raise ValueError("sample key mismatch between anchor sample and hidden-rate state")
    views, _ = e63.hidden_row_views(state, sample, mixmin, a2c8)
    components = e58.posterior_components(labels, worlds, raw_prior, mixmin)
    print("loaded shared state", flush=True)

    strict = e69.strict_rows()
    cells = e71.unique_strict_cells(strict)
    bases, _cands, deltas = e71.reconstruct_unified_arrays(cells, sample, mixmin, raw_prior, views, components)
    rows, preds, variants = build_stability_candidates(cells, bases, deltas)
    print(f"built rows={len(rows)} variants={len(variants)} unique_preds={len(preds)}", flush=True)
    scan = score_rows(rows, preds, sample, mixmin, labels, worlds, views, state)
    summary = summarize(scan)
    scan.to_csv(SCAN_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    write_report(scan, summary, cells, variants)
    print(
        f"rows={len(scan)} variants={scan['variant_name'].nunique()} "
        f"strict={int(scan['strict_gate'].sum())} "
        f"deployable={int(scan['deployable_gate'].sum())} "
        f"loose={int(scan['loose_gate'].sum())} "
        f"best_all={scan['all_delta_vs_mixmin'].min():.6g} "
        f"wrote={REPORT_OUT.relative_to(ROOT)}",
        flush=True,
    )
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
