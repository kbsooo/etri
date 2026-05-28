#!/usr/bin/env python3
"""E72 gate-geometry stress for unified Q2/S3 consensus.

E71 showed that unified strict-cell consensus is not a pure heldout artifact,
but every strict row still depends on `gate=none`. This probe asks whether the
failure is caused by overly hard agreement thresholds or by a deeper absence of
deployable gate geometry.

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
import q2_s3_unified_strict_cell_consensus_probe as e71  # noqa: E402
import raw_block_target_dependency_probe as e55  # noqa: E402


SCAN_OUT = OUT / "q2_s3_unified_gate_geometry_probe_scan.csv"
SUMMARY_OUT = OUT / "q2_s3_unified_gate_geometry_probe_summary.csv"
REPORT_OUT = OUT / "q2_s3_unified_gate_geometry_probe_report.md"

ALPHAS = [2.0, 4.0, 8.0, 12.0, 16.0, 24.0]
GATES = [
    "none",
    "top_abs50",
    "top_abs30",
    "agree55",
    "soft_signed",
    "soft_signed_sq",
    "soft_agree_top50",
    "q2_only",
    "s3_only",
    "q2_agree55",
    "s3_agree55",
]
FOCUS_POOLS = {
    "all_unique",
    "support2",
    "support2_top50",
    "top50_heldout_mean",
    "top75_heldout_mean",
    "high_block",
    "support2_high_block",
    "translator_tail_soft_p90_m0.50",
    "translator_tail_soft_p90_m1.00",
}
QS_IDXS = e70.QS_IDXS
Q2_IDX = TARGETS.index("Q2")
S3_IDX = TARGETS.index("S3")


def _top_abs_mask(abs_delta: np.ndarray, keep_frac: float) -> np.ndarray:
    nonzero = abs_delta[abs_delta > 0.0]
    if len(nonzero) == 0:
        return np.zeros_like(abs_delta, dtype=np.float64)
    threshold = float(np.quantile(nonzero, 1.0 - keep_frac))
    return (abs_delta >= threshold).astype(np.float64)


def adaptive_gate(delta_stack: np.ndarray, delta: np.ndarray, mode: str) -> np.ndarray:
    if mode == "none":
        return np.ones_like(delta, dtype=np.float64)

    signs = np.sign(delta_stack)
    pos = (signs > 0).mean(axis=0)
    neg = (signs < 0).mean(axis=0)
    agreement = np.maximum(pos, neg)
    signed_support = np.where(delta > 0, pos, np.where(delta < 0, neg, 0.0))
    abs_delta = np.abs(delta)
    top50 = _top_abs_mask(abs_delta, 0.50)
    top30 = _top_abs_mask(abs_delta, 0.30)

    if mode == "top_abs50":
        return top50
    if mode == "top_abs30":
        return top30
    if mode == "agree50":
        return (agreement >= 0.50).astype(np.float64)
    if mode == "agree55":
        return (agreement >= 0.55).astype(np.float64)
    if mode == "agree60":
        return (agreement >= 0.60).astype(np.float64)
    if mode == "agree75":
        return (agreement >= 0.75).astype(np.float64)
    if mode == "agree60_top50":
        return ((agreement >= 0.60) & (top50 > 0.0)).astype(np.float64)
    if mode == "soft_signed":
        return np.clip((signed_support - 0.50) / 0.25, 0.0, 1.0)
    if mode == "soft_signed_sq":
        soft = np.clip((signed_support - 0.50) / 0.25, 0.0, 1.0)
        return soft * soft
    if mode == "soft_agree":
        return np.clip((agreement - 0.50) / 0.25, 0.0, 1.0)
    if mode == "soft_agree_top50":
        soft = np.clip((agreement - 0.50) / 0.25, 0.0, 1.0)
        return soft * top50

    target_mask = np.zeros_like(delta, dtype=np.float64)
    if mode == "q2_only":
        target_mask[:, Q2_IDX] = 1.0
        return target_mask
    if mode == "s3_only":
        target_mask[:, S3_IDX] = 1.0
        return target_mask
    if mode == "q2_agree55":
        target_mask[:, Q2_IDX] = (agreement[:, Q2_IDX] >= 0.55).astype(np.float64)
        return target_mask
    if mode == "s3_agree55":
        target_mask[:, S3_IDX] = (agreement[:, S3_IDX] >= 0.55).astype(np.float64)
        return target_mask
    raise KeyError(mode)


def build_adaptive_candidates(
    cells: pd.DataFrame,
    bases: list[np.ndarray],
    deltas: list[np.ndarray],
) -> tuple[pd.DataFrame, list[np.ndarray]]:
    base_logits_all = np.stack([logit(x) for x in bases], axis=0)
    delta_all = np.stack(deltas, axis=0)
    pools = {k: v for k, v in e71.make_unified_pools(cells).items() if k in FOCUS_POOLS}
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
        for base_agg in e70.BASE_AGGS:
            base_logit = e70.aggregate_base(base_logits_all[idxs], base_agg)
            base_pred = e70.clip_prob(e70.sigmoid(base_logit))
            base_tag = e68_tag(base_pred, f"e72_base_{pool_name}_{base_agg}_")
            if base_tag in seen:
                bidx = seen[base_tag]
            else:
                bidx = len(preds)
                seen[base_tag] = bidx
                preds.append(base_pred)
            for delta_agg in e70.DELTA_AGGS:
                delta = e70.aggregate_delta(delta_all[idxs], weights, delta_agg)
                for gate_name in GATES:
                    gate = adaptive_gate(delta_all[idxs], delta, gate_name)
                    gated_delta = delta * gate
                    if np.abs(gated_delta[:, QS_IDXS]).mean() <= 1e-12:
                        continue
                    gate_active = float((np.abs(gate[:, QS_IDXS]) > 0.0).mean())
                    gate_weight = float(gate[:, QS_IDXS].mean())
                    for alpha in ALPHAS:
                        pred = e70.clip_prob(e70.sigmoid(base_logit + float(alpha) * gated_delta))
                        tag = e68_tag(pred, f"e72_{pool_name}_{gate_name}_{alpha:.2f}_")
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
                                "gate_weight_q2s3_mean": gate_weight,
                                "mean_abs_q2s3_delta_unit": float(np.abs(gated_delta[:, QS_IDXS]).mean()),
                            }
                        )
    return pd.DataFrame(rows), preds


def e68_tag(pred: np.ndarray, prefix: str) -> str:
    return e71.e68.e67.stable_tag(pred, prefix=prefix)


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
                "gate_active_q2s3": float(best["gate_active_q2s3"]),
                "gate_weight_q2s3_mean": float(best["gate_weight_q2s3_mean"]),
                "strict_gate": int(group["strict_gate"].sum()),
                "deployable_gate": int(group["deployable_gate"].sum()),
                "loose_gate": int(group["loose_gate"].sum()),
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
        ["deployable_gate", "strict_gate", "loose_gate", "best_all_delta_vs_mixmin"],
        ascending=[False, False, False, True],
    )


def write_report(scan: pd.DataFrame, summary: pd.DataFrame, cells: pd.DataFrame) -> None:
    best = scan.sort_values("all_delta_vs_mixmin").head(30)
    deployable = scan[scan["deployable_gate"]].sort_values("all_delta_vs_mixmin").head(20)
    loose_non_none = scan[scan["loose_gate"] & scan["gate"].ne("none")].sort_values("all_delta_vs_mixmin").head(20)
    by_gate = (
        scan.groupby("gate")
        .agg(
            n=("gate", "size"),
            margin=("all_margin_vs_mixmin", "sum"),
            strict=("strict_gate", "sum"),
            deployable=("deployable_gate", "sum"),
            loose=("loose_gate", "sum"),
            best=("all_delta_vs_mixmin", "min"),
            active=("gate_active_q2s3", "mean"),
            weight=("gate_weight_q2s3_mean", "mean"),
        )
        .reset_index()
        .sort_values(["deployable", "strict", "loose", "best"], ascending=[False, False, False, True])
    )
    strict_n = int(scan["strict_gate"].sum())
    deployable_n = int(scan["deployable_gate"].sum())
    loose_n = int(scan["loose_gate"].sum())
    lines = [
        "# E72 Unified Q2/S3 Gate Geometry Probe",
        "",
        "## Observe",
        "",
        "E71 preserved one strict unified row, but every strict row still used `gate=none`.",
        "",
        "## Wonder",
        "",
        "Is the non-`none` failure caused by hard agreement thresholds, or is deployable agreement geometry absent?",
        "",
        "## Method",
        "",
        f"- Source strict rows: `{int(cells['support_count'].sum())}`.",
        f"- Unique cells: `{len(cells)}`; support-2 cells: `{int(cells['support_count'].ge(2).sum())}`.",
        f"- Candidate rows: `{len(scan)}`.",
        f"- Unique predictions: `{scan['pred_index'].nunique()}` plus mixmin reference.",
        f"- Gates: `{GATES}`.",
        f"- Alphas: `{ALPHAS}`.",
        "- Strict gate is the E70/E71 all-combo, tail, hidden, world, block, and raw-energy gate.",
        "- Deployable gate requires strict gate and `gate != none`.",
        "",
        "## Gate Summary",
        "",
        e56.markdown_table(by_gate),
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
                    "strict_gate",
                    "deployable_gate",
                    "loose_gate",
                ]
            ]
        ),
        "",
        "## Best Deployable Rows",
        "",
        e56.markdown_table(deployable.head(20)) if len(deployable) else "_None._",
        "",
        "## Best Loose Non-None Rows",
        "",
        e56.markdown_table(
            loose_non_none[
                [
                    "pool",
                    "base_agg",
                    "delta_agg",
                    "gate",
                    "alpha",
                    "all_delta_vs_mixmin",
                    "all_minus_base",
                    "sets_beating_base",
                    "sets_tail_neutral",
                    "hidden_q2s3_mean_minus_base",
                    "world_support_minus_base",
                    "block_q2s3_beats_base_rate",
                    "loose_gate",
                ]
            ].head(20)
        )
        if len(loose_non_none)
        else "_None._",
        "",
        "## Decision",
        "",
    ]
    if deployable_n:
        lines.append(f"- Deployable non-`none` gates exist: `{deployable_n}`. Build a candidate-file stress next, not a blind submission.")
    elif strict_n:
        lines.append(f"- Strict rows exist: `{strict_n}`, but deployable non-`none` gates are `0`.")
        lines.append("- The gate failure is not just the E71 hard-threshold implementation; soft and target-specific gates still fail strict deployability.")
    elif loose_n:
        lines.append(f"- Loose rows exist: `{loose_n}`, but no strict row survives.")
    else:
        lines.append("- No useful gate survives even loose requirements.")
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
    cells = e71.unique_strict_cells(strict)
    print(f"strict rows={len(strict)} unique_cells={len(cells)} support2={int(cells['support_count'].ge(2).sum())}", flush=True)
    bases, _cands, deltas = e71.reconstruct_unified_arrays(cells, sample, mixmin, raw_prior, views, components)
    print("reconstructed unified cells", flush=True)
    rows, preds = build_adaptive_candidates(cells, bases, deltas)
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
    scan = scan.rename(columns={"strict_consensus_gate": "strict_gate", "loose_consensus_gate": "loose_gate"})
    scan["deployable_gate"] = scan["strict_gate"] & scan["gate"].ne("none")
    scan = scan.sort_values(
        ["deployable_gate", "strict_gate", "loose_gate", "all_delta_vs_mixmin"],
        ascending=[False, False, False, True],
    )
    summary = summarize(scan)
    scan.to_csv(SCAN_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    write_report(scan, summary, cells)
    print(
        f"rows={len(scan)} unique_preds={scan['pred_index'].nunique()} "
        f"strict={int(scan['strict_gate'].sum())} "
        f"deployable={int(scan['deployable_gate'].sum())} "
        f"loose={int(scan['loose_gate'].sum())} "
        f"best_all={scan['all_delta_vs_mixmin'].min():.6g} wrote={REPORT_OUT.relative_to(ROOT)}",
        flush=True,
    )
    print(summary.head(20).to_string(index=False))


if __name__ == "__main__":
    main()
