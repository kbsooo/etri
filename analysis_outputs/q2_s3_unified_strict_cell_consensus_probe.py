#!/usr/bin/env python3
"""E71 unified consensus stress for E68 strict Q2/S3 cells.

E70 showed that E68 strict Q2/S3 cells can accumulate into a small
selector-margin consensus, but every strict row used `gate=none` and the cells
were rebuilt with heldout-specific anchor gradients.

This probe removes that heldout-specific prediction rule. E68 strict rows are
used only as evidence for selecting unique cells; each selected cell is rebuilt
once with the full combo family. We then ask whether the consensus survives as a
unified test-time rule.

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
from public_lb_actual_anchor_ranker import COMBO_TABLES  # noqa: E402
import gradient_consensus_posterior_probe as e63  # noqa: E402
import mixmin_hard_posterior_distillation_probe as e58  # noqa: E402
import mixmin_hard_raw_world_probe as e56  # noqa: E402
import q2_s3_strict_cell_amplitude_probe as e69  # noqa: E402
import q2_s3_strict_cell_consensus_probe as e70  # noqa: E402
import q2_s3_tail_gate_independence_probe as e68  # noqa: E402
import raw_block_target_dependency_probe as e55  # noqa: E402


SCAN_OUT = OUT / "q2_s3_unified_strict_cell_consensus_probe_scan.csv"
SUMMARY_OUT = OUT / "q2_s3_unified_strict_cell_consensus_probe_summary.csv"
REPORT_OUT = OUT / "q2_s3_unified_strict_cell_consensus_probe_report.md"

ALPHAS = e70.ALPHAS
BASE_AGGS = e70.BASE_AGGS
DELTA_AGGS = e70.DELTA_AGGS
GATES = e70.GATES
ANCHOR_MARGIN = e70.ANCHOR_MARGIN
QS_IDXS = e70.QS_IDXS


def unique_strict_cells(strict: pd.DataFrame) -> pd.DataFrame:
    key_cols = e68.candidate_key_cols() + ["translator"]
    agg = {
        "heldout_set": lambda x: ",".join(sorted(map(str, x))),
        "heldout_minus_base": "mean",
        "heldout_worst_minus_base": "mean",
        "train_minus_base": "mean",
        "train_worst_minus_base": "mean",
        "world_support_minus_base": "mean",
        "raw_energy_q_p90_minus_base": "mean",
        "hidden_core_minus_base": "mean",
        "hidden_q2_minus_base": "mean",
        "hidden_s3_minus_base": "mean",
        "hidden_q2s3_mean_minus_base": "mean",
        "block_q2s3_mean_minus_base": "mean",
        "block_q2s3_max_minus_base": "mean",
        "block_q2s3_beats_base_rate": "mean",
        "block_q2s3_tail_safe_rate": "mean",
    }
    cells = strict.groupby(key_cols, dropna=False).agg(agg).reset_index()
    counts = strict.groupby(key_cols, dropna=False).size().reset_index(name="support_count")
    cells = cells.merge(counts, on=key_cols, how="inner")
    cells = cells.sort_values(["support_count", "heldout_minus_base"], ascending=[False, True]).reset_index(drop=True)
    return cells


def reconstruct_unified_arrays(
    cells: pd.DataFrame,
    sample: pd.DataFrame,
    mixmin: np.ndarray,
    raw_prior: np.ndarray,
    views: dict[str, np.ndarray],
    components: dict[str, dict[str, np.ndarray]],
) -> tuple[list[np.ndarray], list[np.ndarray], list[np.ndarray]]:
    gradients, gradient_weights = e68.anchor_gradient_for_sets(sample, mixmin, list(COMBO_TABLES))
    bases: list[np.ndarray] = []
    cands: list[np.ndarray] = []
    deltas: list[np.ndarray] = []
    for rec in cells.to_dict("records"):
        spec = pd.Series(rec)
        base = e68.pred_from_config(spec, "no_q2_s3", components, raw_prior, mixmin, views, gradients, gradient_weights)
        cand = e68.pred_from_config(spec, str(rec["translator"]), components, raw_prior, mixmin, views, gradients, gradient_weights)
        q_delta = np.zeros_like(base)
        q_delta[:, QS_IDXS] = logit(cand)[:, QS_IDXS] - logit(base)[:, QS_IDXS]
        bases.append(base)
        cands.append(cand)
        deltas.append(q_delta)
    return bases, cands, deltas


def make_unified_pools(cells: pd.DataFrame) -> dict[str, np.ndarray]:
    pools: dict[str, np.ndarray] = {"all_unique": cells.index.to_numpy(dtype=int)}
    pools["support2"] = cells[cells["support_count"].ge(2)].index.to_numpy(dtype=int)
    pools["top50_heldout_mean"] = cells.sort_values("heldout_minus_base").head(50).index.to_numpy(dtype=int)
    pools["top75_heldout_mean"] = cells.sort_values("heldout_minus_base").head(75).index.to_numpy(dtype=int)
    pools["support2_top50"] = (
        cells[cells["support_count"].ge(2)].sort_values("heldout_minus_base").head(50).index.to_numpy(dtype=int)
    )
    block_cut = float(cells["block_q2s3_beats_base_rate"].quantile(0.65))
    world_cut = float(cells["world_support_minus_base"].quantile(0.35))
    hidden_cut = float(cells["hidden_q2s3_mean_minus_base"].quantile(0.35))
    pools["high_block"] = cells[cells["block_q2s3_beats_base_rate"].ge(block_cut)].index.to_numpy(dtype=int)
    pools["high_world"] = cells[cells["world_support_minus_base"].le(world_cut)].index.to_numpy(dtype=int)
    pools["high_hidden"] = cells[cells["hidden_q2s3_mean_minus_base"].le(hidden_cut)].index.to_numpy(dtype=int)
    pools["support2_high_block"] = cells[
        cells["support_count"].ge(2) & cells["block_q2s3_beats_base_rate"].ge(block_cut)
    ].index.to_numpy(dtype=int)
    for translator, group in cells.groupby("translator", sort=False):
        pools[f"translator_{translator}"] = group.index.to_numpy(dtype=int)
    return {k: v for k, v in pools.items() if len(v) >= 8}


def build_unified_candidates(
    cells: pd.DataFrame,
    bases: list[np.ndarray],
    deltas: list[np.ndarray],
) -> tuple[pd.DataFrame, list[np.ndarray]]:
    base_logits_all = np.stack([logit(x) for x in bases], axis=0)
    delta_all = np.stack(deltas, axis=0)
    pools = make_unified_pools(cells)
    rows: list[dict[str, Any]] = []
    preds: list[np.ndarray] = []
    seen: dict[str, int] = {}
    for pool_name, idxs in pools.items():
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
        for base_agg in BASE_AGGS:
            base_logit = e70.aggregate_base(base_logits_all[idxs], base_agg)
            base_pred = e70.clip_prob(e70.sigmoid(base_logit))
            base_tag = e68.e67.stable_tag(base_pred, prefix=f"e71_base_{pool_name}_{base_agg}_")
            if base_tag in seen:
                bidx = seen[base_tag]
            else:
                bidx = len(preds)
                seen[base_tag] = bidx
                preds.append(base_pred)
            for delta_agg in DELTA_AGGS:
                delta = e70.aggregate_delta(delta_all[idxs], weights, delta_agg)
                for gate_name in GATES:
                    gate = e70.consensus_gate(delta_all[idxs], delta, gate_name)
                    gated_delta = delta * gate
                    if np.abs(gated_delta[:, QS_IDXS]).mean() <= 1e-12:
                        continue
                    gate_active = float((np.abs(gated_delta[:, QS_IDXS]) > 0.0).mean())
                    for alpha in ALPHAS:
                        pred = e70.clip_prob(e70.sigmoid(base_logit + float(alpha) * gated_delta))
                        tag = e68.e67.stable_tag(pred, prefix=f"e71_{pool_name}_{alpha:.2f}_")
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
                                "pool": pool_name,
                                "pool_size": int(len(idxs)),
                                "pool_support_mean": float(pool["support_count"].mean()),
                                "base_agg": base_agg,
                                "delta_agg": delta_agg,
                                "gate": gate_name,
                                "alpha": float(alpha),
                                "gate_active_q2s3": gate_active,
                                "mean_abs_q2s3_delta_unit": float(np.abs(gated_delta[:, QS_IDXS]).mean()),
                            }
                        )
    return pd.DataFrame(rows), preds


def summarize(scan: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (pool, base_agg, delta_agg, gate), group in scan.groupby(["pool", "base_agg", "delta_agg", "gate"]):
        best = group.sort_values("all_delta_vs_mixmin").iloc[0]
        rows.append(
            {
                "pool": pool,
                "base_agg": base_agg,
                "delta_agg": delta_agg,
                "gate": gate,
                "n": int(len(group)),
                "pool_size": int(best["pool_size"]),
                "pool_support_mean": float(best["pool_support_mean"]),
                "strict_unified_gate": int(group["strict_unified_gate"].sum()),
                "deployable_unified_gate": int(group["deployable_unified_gate"].sum()),
                "loose_unified_gate": int(group["loose_unified_gate"].sum()),
                "all_margin_vs_mixmin": int(group["all_margin_vs_mixmin"].sum()),
                "best_all_delta_vs_mixmin": float(best["all_delta_vs_mixmin"]),
                "best_all_minus_base": float(group["all_minus_base"].min()),
                "best_worst_set_delta": float(group["worst_set_delta_vs_mixmin"].min()),
                "best_sets_beating_base": int(group["sets_beating_base"].max()),
                "best_sets_tail_neutral": int(group["sets_tail_neutral"].max()),
                "best_hidden_q2s3_minus_base": float(group["hidden_q2s3_mean_minus_base"].min()),
                "best_world_support_minus_base": float(group["world_support_minus_base"].min()),
                "best_block_win_rate": float(group["block_q2s3_beats_base_rate"].max()),
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["deployable_unified_gate", "strict_unified_gate", "loose_unified_gate", "best_all_delta_vs_mixmin"],
        ascending=[False, False, False, True],
    )


def write_report(scan: pd.DataFrame, summary: pd.DataFrame, cells: pd.DataFrame) -> None:
    best = scan.sort_values("all_delta_vs_mixmin").head(25)
    strict_n = int(scan["strict_unified_gate"].sum())
    deployable_n = int(scan["deployable_unified_gate"].sum())
    loose_n = int(scan["loose_unified_gate"].sum())
    strict_gate_counts = (
        scan[scan["strict_unified_gate"]]["gate"].value_counts().to_dict() if strict_n else {}
    )
    lines = [
        "# E71 Unified Q2/S3 Strict-Cell Consensus Probe",
        "",
        "## Observe",
        "",
        "E70 found strict consensus rows, but all used `gate=none` and heldout-specific cell reconstruction.",
        "",
        "## Wonder",
        "",
        "Does the E70 consensus survive when each E68 strict cell is rebuilt once with the full combo family?",
        "",
        "## Method",
        "",
        f"- E68 strict rows: `{int(cells['support_count'].sum())}`.",
        f"- Unique strict cells: `{len(cells)}`.",
        f"- Cells with support from two heldout families: `{int(cells['support_count'].ge(2).sum())}`.",
        f"- Candidate rows: `{len(scan)}`.",
        f"- Unique predictions: `{scan['pred_index'].nunique()}` plus mixmin reference.",
        f"- Pools: `{scan['pool'].nunique()}`; base aggregators: `{BASE_AGGS}`; delta aggregators: `{DELTA_AGGS}`; gates: `{GATES}`; alphas: `{ALPHAS}`.",
        "- Strict unified gate uses the same tail/hidden/world/block requirements as E70.",
        "- Deployable unified gate additionally requires `gate != none`, so it cannot rely on disagreement-permissive consensus.",
        "",
        "## Summary",
        "",
        e56.markdown_table(summary.head(30)),
        "",
        "## Best Full-Combo Rows",
        "",
        e56.markdown_table(
            best[
                [
                    "pool",
                    "pool_size",
                    "pool_support_mean",
                    "base_agg",
                    "delta_agg",
                    "gate",
                    "alpha",
                    "all_delta_vs_mixmin",
                    "all_minus_base",
                    "sets_beating_base",
                    "sets_tail_neutral",
                    "world_support_minus_base",
                    "hidden_q2s3_mean_minus_base",
                    "block_q2s3_beats_base_rate",
                    "strict_unified_gate",
                    "deployable_unified_gate",
                    "loose_unified_gate",
                ]
            ]
        ),
        "",
        "## Decision",
        "",
    ]
    if deployable_n:
        lines.append(f"- Deployable unified gates exist: `{deployable_n}`. This branch deserves candidate-file construction plus a final pre-submit stress.")
    elif strict_n:
        lines.append(f"- Strict unified gates exist: `{strict_n}`, but deployable gates are `0`; strict gate counts by consensus gate: `{strict_gate_counts}`.")
        lines.append("- Unified consensus survives only as a diagnostic energy unless a conservative gate can reproduce the margin.")
    elif loose_n:
        lines.append(f"- Loose unified gates exist: `{loose_n}`, but strict margin/tail requirements fail.")
    else:
        lines.append("- Unified consensus gates are `0`; E70's heldout-specific consensus does not transfer to a unified rule.")
    lines.extend(
        [
            "- No submission file is produced.",
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
    cells = unique_strict_cells(strict)
    print(f"strict rows={len(strict)} unique_cells={len(cells)} support2={int(cells['support_count'].ge(2).sum())}", flush=True)
    bases, _cands, deltas = reconstruct_unified_arrays(cells, sample, mixmin, raw_prior, views, components)
    print("reconstructed unified cells", flush=True)
    rows, preds = build_unified_candidates(cells, bases, deltas)
    print(f"built candidate rows={len(rows)} unique_preds={len(preds)}", flush=True)
    combo = e70.combo_scores(rows, [mixmin] + preds, sample)
    print("combo scores computed", flush=True)
    selected = e70.select_nonanchor_rows(combo)
    print(f"selected nonanchor rows={len(selected)}", flush=True)
    nonanchor = e70.nonanchor_scores(selected, preds, mixmin, labels, worlds, views, state)
    combo = combo.reset_index(drop=True).copy()
    combo["row_id"] = np.arange(len(combo), dtype=int)
    metric_cols = [c for c in nonanchor.columns if c not in combo.columns and c != "row_id"]
    scan_input = combo.merge(nonanchor[["row_id", *metric_cols]], on="row_id", how="left")
    scan_input["nonanchor_evaluated"] = scan_input["row_id"].isin(set(nonanchor["row_id"].astype(int)))
    scan = e70.add_gates(scan_input, preds, mixmin)
    scan = scan.rename(
        columns={
            "strict_consensus_gate": "strict_unified_gate",
            "loose_consensus_gate": "loose_unified_gate",
        }
    )
    scan["deployable_unified_gate"] = scan["strict_unified_gate"] & scan["gate"].ne("none")
    scan = scan.sort_values(
        ["deployable_unified_gate", "strict_unified_gate", "loose_unified_gate", "all_delta_vs_mixmin"],
        ascending=[False, False, False, True],
    )
    summary = summarize(scan)
    scan.to_csv(SCAN_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    write_report(scan, summary, cells)
    print(
        f"rows={len(scan)} unique_preds={scan['pred_index'].nunique()} "
        f"strict={int(scan['strict_unified_gate'].sum())} "
        f"deployable={int(scan['deployable_unified_gate'].sum())} "
        f"loose={int(scan['loose_unified_gate'].sum())} "
        f"best_all={scan['all_delta_vs_mixmin'].min():.6g} wrote={REPORT_OUT.relative_to(ROOT)}",
        flush=True,
    )
    print(summary.head(20).to_string(index=False))


if __name__ == "__main__":
    main()
