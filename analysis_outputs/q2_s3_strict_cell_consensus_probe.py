#!/usr/bin/env python3
"""E70 consensus stress for independently validated Q2/S3 strict cells.

E69 rejected a single-pair/global-alpha explanation: one E68 strict Q2/S3 cell
can be scaled close to the margin, but tail stability erodes before the move is
submission-scale. This probe asks a different JEPA-style question:

Do multiple independently validated Q2/S3 cells share a common row/target
representation that accumulates into a safer consensus movement?

We build consensus bases from matched `no_q2_s3` predictions, aggregate Q2/S3
logit deltas across E68 strict pairs, apply agreement/magnitude gates, and score
the result against combo, hidden, world, and block stresses. No submission is
written.
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
import q2_s3_tail_gate_independence_probe as e68  # noqa: E402
import raw_block_target_dependency_probe as e55  # noqa: E402


SCAN_OUT = OUT / "q2_s3_strict_cell_consensus_probe_scan.csv"
SUMMARY_OUT = OUT / "q2_s3_strict_cell_consensus_probe_summary.csv"
REPORT_OUT = OUT / "q2_s3_strict_cell_consensus_probe_report.md"

EPS = 1e-6
ANCHOR_MARGIN = 1.0e-5
ALPHAS = [0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0]
BASE_AGGS = ["mean", "median"]
DELTA_AGGS = ["mean", "median", "weighted_mean", "signed_p75"]
GATES = ["none", "agree60", "agree75", "agree60_top50"]
MAX_NONANCHOR_ROWS = 700

Q2_IDX = TARGETS.index("Q2")
S3_IDX = TARGETS.index("S3")
QS_IDXS = [Q2_IDX, S3_IDX]


def clip_prob(x: np.ndarray | float) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def sigmoid(x: np.ndarray | float) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def reconstruct_strict_arrays(
    strict: pd.DataFrame,
    sample: pd.DataFrame,
    mixmin: np.ndarray,
    raw_prior: np.ndarray,
    views: dict[str, np.ndarray],
    components: dict[str, dict[str, np.ndarray]],
) -> tuple[list[np.ndarray], list[np.ndarray], list[np.ndarray]]:
    bases: list[np.ndarray] = []
    cands: list[np.ndarray] = []
    deltas: list[np.ndarray] = []
    for rec in strict.to_dict("records"):
        heldout_set = str(rec["heldout_set"])
        train_sets = [name for name in COMBO_TABLES if name != heldout_set]
        gradients, gradient_weights = e68.anchor_gradient_for_sets(sample, mixmin, train_sets)
        spec = pd.Series(rec)
        base = e68.pred_from_config(spec, "no_q2_s3", components, raw_prior, mixmin, views, gradients, gradient_weights)
        cand = e68.pred_from_config(spec, str(rec["translator"]), components, raw_prior, mixmin, views, gradients, gradient_weights)
        q_delta = np.zeros_like(base)
        q_delta[:, QS_IDXS] = logit(cand)[:, QS_IDXS] - logit(base)[:, QS_IDXS]
        bases.append(base)
        cands.append(cand)
        deltas.append(q_delta)
    return bases, cands, deltas


def make_pools(strict: pd.DataFrame) -> dict[str, np.ndarray]:
    pools: dict[str, np.ndarray] = {"all": strict.index.to_numpy(dtype=int)}
    for heldout, group in strict.groupby("heldout_set", sort=False):
        pools[f"heldout_{heldout}"] = group.index.to_numpy(dtype=int)
    for translator, group in strict.groupby("translator", sort=False):
        pools[f"translator_{translator}"] = group.index.to_numpy(dtype=int)
    pools["top50_heldout"] = strict.sort_values("heldout_minus_base").head(50).index.to_numpy(dtype=int)
    pools["top100_heldout"] = strict.sort_values("heldout_minus_base").head(100).index.to_numpy(dtype=int)
    pools["high_block"] = strict[strict["block_q2s3_beats_base_rate"].ge(0.70)].index.to_numpy(dtype=int)
    world_cut = float(strict["world_support_minus_base"].quantile(0.35))
    pools["high_world"] = strict[strict["world_support_minus_base"].le(world_cut)].index.to_numpy(dtype=int)
    return {k: v for k, v in pools.items() if len(v) >= 8}


def aggregate_base(base_logits: np.ndarray, mode: str) -> np.ndarray:
    if mode == "mean":
        return base_logits.mean(axis=0)
    if mode == "median":
        return np.median(base_logits, axis=0)
    raise KeyError(mode)


def aggregate_delta(delta_stack: np.ndarray, weights: np.ndarray, mode: str) -> np.ndarray:
    if mode == "mean":
        return delta_stack.mean(axis=0)
    if mode == "median":
        return np.median(delta_stack, axis=0)
    if mode == "weighted_mean":
        return np.einsum("i,irt->rt", weights, delta_stack)
    if mode == "signed_p75":
        mean = delta_stack.mean(axis=0)
        mag = np.quantile(np.abs(delta_stack), 0.75, axis=0)
        return np.sign(mean) * mag
    raise KeyError(mode)


def consensus_gate(delta_stack: np.ndarray, delta: np.ndarray, mode: str) -> np.ndarray:
    if mode == "none":
        return np.ones_like(delta, dtype=np.float64)
    signs = np.sign(delta_stack)
    pos = (signs > 0).mean(axis=0)
    neg = (signs < 0).mean(axis=0)
    agreement = np.maximum(pos, neg)
    if mode == "agree60":
        return (agreement >= 0.60).astype(np.float64)
    if mode == "agree75":
        return (agreement >= 0.75).astype(np.float64)
    abs_delta = np.abs(delta)
    nonzero = abs_delta[abs_delta > 0.0]
    if len(nonzero) == 0:
        return np.zeros_like(delta, dtype=np.float64)
    if mode == "top_abs50":
        threshold = float(np.quantile(nonzero, 0.50))
        return (abs_delta >= threshold).astype(np.float64)
    if mode == "top_abs30":
        threshold = float(np.quantile(nonzero, 0.70))
        return (abs_delta >= threshold).astype(np.float64)
    if mode == "agree60_top50":
        threshold = float(np.quantile(nonzero, 0.50))
        return ((agreement >= 0.60) & (abs_delta >= threshold)).astype(np.float64)
    raise KeyError(mode)


def build_candidates(
    strict: pd.DataFrame,
    bases: list[np.ndarray],
    deltas: list[np.ndarray],
) -> tuple[pd.DataFrame, list[np.ndarray], dict[str, int]]:
    base_logits_all = np.stack([logit(x) for x in bases], axis=0)
    delta_all = np.stack(deltas, axis=0)
    pools = make_pools(strict)
    rows: list[dict[str, Any]] = []
    preds: list[np.ndarray] = []
    base_index: dict[str, int] = {}
    seen: dict[str, int] = {}
    for pool_name, idxs in pools.items():
        pool = strict.loc[idxs].copy()
        raw_weight = (
            -pool["heldout_minus_base"].to_numpy(dtype=np.float64)
            + 0.20 * -pool["world_support_minus_base"].to_numpy(dtype=np.float64)
            + 0.05 * -pool["hidden_q2s3_mean_minus_base"].to_numpy(dtype=np.float64)
        )
        raw_weight = np.maximum(raw_weight, 0.0) + 1e-12
        weights = raw_weight / raw_weight.sum()
        for base_agg in BASE_AGGS:
            base_logit = aggregate_base(base_logits_all[idxs], base_agg)
            base_pred = clip_prob(sigmoid(base_logit))
            base_tag = e68.e67.stable_tag(base_pred, prefix=f"e70_base_{pool_name}_{base_agg}_")
            if base_tag in seen:
                bidx = seen[base_tag]
            else:
                bidx = len(preds)
                seen[base_tag] = bidx
                preds.append(base_pred)
            base_index[f"{pool_name}|{base_agg}"] = bidx
            for delta_agg in DELTA_AGGS:
                delta = aggregate_delta(delta_all[idxs], weights, delta_agg)
                for gate_name in GATES:
                    gate = consensus_gate(delta_all[idxs], delta, gate_name)
                    gated_delta = delta * gate
                    if np.abs(gated_delta[:, QS_IDXS]).mean() <= 1e-12:
                        continue
                    gate_active = float((np.abs(gated_delta[:, QS_IDXS]) > 0.0).mean())
                    for alpha in ALPHAS:
                        pred = clip_prob(sigmoid(base_logit + float(alpha) * gated_delta))
                        tag = e68.e67.stable_tag(pred, prefix=f"e70_{pool_name}_{alpha:.2f}_")
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
                                "base_agg": base_agg,
                                "delta_agg": delta_agg,
                                "gate": gate_name,
                                "alpha": float(alpha),
                                "gate_active_q2s3": gate_active,
                                "mean_abs_q2s3_delta_unit": float(np.abs(gated_delta[:, QS_IDXS]).mean()),
                            }
                        )
    return pd.DataFrame(rows), preds, base_index


def combo_scores(rows: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> pd.DataFrame:
    score_frames = {
        "all": e68.combo_set_score(preds, sample, list(COMBO_TABLES)).set_index("candidate_index"),
        **{
            f"set_{name}": e68.combo_set_score(preds, sample, [name]).set_index("candidate_index")
            for name in COMBO_TABLES
        },
    }
    mix_idx = 0
    metric_rows: list[dict[str, Any]] = []
    for rec in rows.to_dict("records"):
        idx = int(rec["pred_index"]) + 1
        bidx = int(rec["base_index"]) + 1
        metrics: dict[str, Any] = {}
        set_minus_base = []
        set_delta = []
        set_worst_minus_base = []
        for name, frame in score_frames.items():
            cand_score = float(frame.loc[idx, "score"] - frame.loc[mix_idx, "score"])
            base_score = float(frame.loc[bidx, "score"] - frame.loc[mix_idx, "score"])
            cand_worst = float(frame.loc[idx, "worst"] - frame.loc[mix_idx, "worst"])
            base_worst = float(frame.loc[bidx, "worst"] - frame.loc[mix_idx, "worst"])
            metrics[f"{name}_delta_vs_mixmin"] = cand_score
            metrics[f"{name}_minus_base"] = cand_score - base_score
            metrics[f"{name}_worst_minus_base"] = cand_worst - base_worst
            if name.startswith("set_"):
                set_delta.append(cand_score)
                set_minus_base.append(cand_score - base_score)
                set_worst_minus_base.append(cand_worst - base_worst)
        metrics["best_set_delta_vs_mixmin"] = float(np.min(set_delta))
        metrics["worst_set_delta_vs_mixmin"] = float(np.max(set_delta))
        metrics["sets_beating_base"] = int((np.asarray(set_minus_base) < 0.0).sum())
        metrics["sets_tail_neutral"] = int((np.asarray(set_worst_minus_base) <= 0.0).sum())
        metric_rows.append(metrics)
    return pd.concat([rows.reset_index(drop=True), pd.DataFrame(metric_rows)], axis=1)


def select_nonanchor_rows(combo: pd.DataFrame) -> pd.DataFrame:
    combo = combo.reset_index(drop=True).copy()
    combo["row_id"] = np.arange(len(combo), dtype=int)
    candidates = [
        combo[combo["all_minus_base"] < 0.0],
        combo[combo["sets_beating_base"] >= max(1, len(COMBO_TABLES) - 1)],
        combo.nsmallest(MAX_NONANCHOR_ROWS // 2, "all_delta_vs_mixmin"),
        combo.nsmallest(MAX_NONANCHOR_ROWS // 2, "all_minus_base"),
    ]
    selected = pd.concat(candidates, ignore_index=False).drop_duplicates("row_id")
    if len(selected) > MAX_NONANCHOR_ROWS:
        selected = selected.sort_values(["sets_beating_base", "all_delta_vs_mixmin"], ascending=[False, True]).head(
            MAX_NONANCHOR_ROWS
        )
    return selected.sort_values("row_id").reset_index(drop=True)


def nonanchor_scores(
    rows: pd.DataFrame,
    preds: list[np.ndarray],
    mixmin: np.ndarray,
    labels: np.ndarray,
    worlds: pd.DataFrame,
    views: dict[str, np.ndarray],
    state: e55.BaseState,
) -> pd.DataFrame:
    unique_indexes = sorted(set(rows["pred_index"].astype(int)) | set(rows["base_index"].astype(int)))
    stats = {
        i: e68.score_prediction(str(i), preds[i], mixmin, labels, worlds, views, state)
        for i in unique_indexes
    }
    metric_rows: list[dict[str, Any]] = []
    for rec in rows.to_dict("records"):
        idx = int(rec["pred_index"])
        bidx = int(rec["base_index"])
        cur = stats[idx]
        base = stats[bidx]
        block = cur["_block_vector"] - base["_block_vector"]
        metric_rows.append(
            {
                "world_support_minus_base": float(cur["world_support_score"] - base["world_support_score"]),
                "raw_energy_q_p90_minus_base": float(
                    cur["raw_energy_quarter_p90_delta"] - base["raw_energy_quarter_p90_delta"]
                ),
                "hidden_core_minus_base": float(cur["hidden_core_mean_delta"] - base["hidden_core_mean_delta"]),
                "hidden_q2_minus_base": float(cur["hidden_core_delta_Q2"] - base["hidden_core_delta_Q2"]),
                "hidden_s3_minus_base": float(cur["hidden_core_delta_S3"] - base["hidden_core_delta_S3"]),
                "hidden_q2s3_mean_minus_base": float(
                    0.5
                    * (
                        cur["hidden_core_delta_Q2"]
                        - base["hidden_core_delta_Q2"]
                        + cur["hidden_core_delta_S3"]
                        - base["hidden_core_delta_S3"]
                    )
                ),
                "block_q2s3_mean_minus_base": float(block.mean()),
                "block_q2s3_max_minus_base": float(block.max()),
                "block_q2s3_beats_base_rate": float((block < 0.0).mean()),
                "block_q2s3_tail_safe_rate": float((block <= 1.0e-8).mean()),
            }
        )
    return pd.concat([rows.reset_index(drop=True), pd.DataFrame(metric_rows)], axis=1)


def add_gates(rows: pd.DataFrame, preds: list[np.ndarray], mixmin: np.ndarray) -> pd.DataFrame:
    out = rows.copy()
    mix_logit = logit(mixmin)
    move_rows = []
    for i, pred in enumerate(preds):
        delta = logit(pred) - mix_logit
        move_rows.append(
            {
                "pred_index": i,
                "mean_abs_logit_move_vs_mixmin": float(np.abs(delta).mean()),
                "mean_abs_q2s3_logit_move_vs_mixmin": float(np.abs(delta[:, QS_IDXS]).mean()),
            }
        )
    out = out.merge(pd.DataFrame(move_rows), on="pred_index", how="left")
    out["all_beats_base"] = out["all_minus_base"] < 0.0
    out["all_margin_vs_mixmin"] = out["all_delta_vs_mixmin"] < -ANCHOR_MARGIN
    out["all_sets_beat_base"] = out["sets_beating_base"] == len(COMBO_TABLES)
    out["all_sets_tail_neutral"] = out["sets_tail_neutral"] == len(COMBO_TABLES)
    out["hidden_q2s3_beats_base"] = out["hidden_q2s3_mean_minus_base"] < 0.0
    out["world_nonworse"] = out["world_support_minus_base"] <= 0.0
    out["block_majority_beats"] = out["block_q2s3_beats_base_rate"] >= 0.55
    out["block_tail_safe"] = out["block_q2s3_tail_safe_rate"] >= 0.75
    evaluated = out.get("nonanchor_evaluated", pd.Series(True, index=out.index)).fillna(False).astype(bool)
    out["strict_consensus_gate"] = (
        evaluated
        &
        out["all_margin_vs_mixmin"]
        & out["all_beats_base"]
        & out["all_sets_beat_base"]
        & out["all_sets_tail_neutral"]
        & out["hidden_q2s3_beats_base"]
        & out["world_nonworse"]
        & out["block_majority_beats"]
        & out["block_tail_safe"]
        & out["raw_energy_q_p90_minus_base"].le(0.0)
    )
    out["loose_consensus_gate"] = (
        evaluated
        &
        out["all_beats_base"]
        & out["hidden_q2s3_beats_base"]
        & out["world_nonworse"]
        & out["block_majority_beats"]
    )
    return out


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
                "strict_consensus_gate": int(group["strict_consensus_gate"].sum()),
                "loose_consensus_gate": int(group["loose_consensus_gate"].sum()),
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
        ["strict_consensus_gate", "loose_consensus_gate", "best_all_delta_vs_mixmin"],
        ascending=[False, False, True],
    )


def write_report(scan: pd.DataFrame, summary: pd.DataFrame) -> None:
    best = scan.sort_values("all_delta_vs_mixmin").head(25)
    strict_n = int(scan["strict_consensus_gate"].sum())
    loose_n = int(scan["loose_consensus_gate"].sum())
    lines = [
        "# E70 Q2/S3 Strict-Cell Consensus Probe",
        "",
        "## Observe",
        "",
        "E69 says one strict pair plus global alpha cannot clear margin without tail instability.",
        "",
        "## Wonder",
        "",
        "Do multiple E68 strict cells share a consensus row/target representation that accumulates into safer Q2/S3 movement?",
        "",
        "## Method",
        "",
        f"- Strict E68 cells used: `{scan['pool_size'].max()}` in the full pool.",
        f"- Candidate rows: `{len(scan)}`.",
        f"- Unique predictions: `{scan['pred_index'].nunique()}` plus mixmin reference.",
        f"- Pools: `{scan['pool'].nunique()}`; base aggregators: `{BASE_AGGS}`; delta aggregators: `{DELTA_AGGS}`; gates: `{GATES}`; alphas: `{ALPHAS}`.",
        "- Strict gate requires all-combo margin, all combo sets beat base, all set worst tails non-worse, hidden/world/block support, and raw-energy non-worsening.",
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
                    "strict_consensus_gate",
                    "loose_consensus_gate",
                ]
            ]
        ),
        "",
        "## Decision",
        "",
    ]
    if strict_n:
        lines.append(f"- Strict consensus gates exist: `{strict_n}`. This branch deserves a unified-rule stress before any submission.")
    elif loose_n:
        lines.append(f"- Loose consensus gates exist: `{loose_n}`, but strict margin/tail requirements fail. Consensus is useful as energy, not a submission.")
    else:
        lines.append("- Consensus gates are `0`; E68 strict cells do not accumulate into a safe margin-scale Q2/S3 move under these aggregators.")
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
    bases, _cands, deltas = reconstruct_strict_arrays(strict, sample, mixmin, raw_prior, views, components)
    print(f"reconstructed strict cells={len(strict)}", flush=True)
    rows, preds, _base_index = build_candidates(strict, bases, deltas)
    print(f"built candidate rows={len(rows)} unique_preds={len(preds)}", flush=True)
    combo = combo_scores(rows, [mixmin] + preds, sample)
    print("combo scores computed", flush=True)
    # combo scoring uses [mixmin] + preds, while non-anchor stats use preds only.
    selected = select_nonanchor_rows(combo)
    print(f"selected nonanchor rows={len(selected)}", flush=True)
    nonanchor = nonanchor_scores(selected, preds, mixmin, labels, worlds, views, state)
    combo = combo.reset_index(drop=True).copy()
    combo["row_id"] = np.arange(len(combo), dtype=int)
    metric_cols = [c for c in nonanchor.columns if c not in combo.columns and c != "row_id"]
    scan_input = combo.merge(nonanchor[["row_id", *metric_cols]], on="row_id", how="left")
    scan_input["nonanchor_evaluated"] = scan_input["row_id"].isin(set(nonanchor["row_id"].astype(int)))
    scan = add_gates(scan_input, preds, mixmin).sort_values(
        ["strict_consensus_gate", "loose_consensus_gate", "all_delta_vs_mixmin"],
        ascending=[False, False, True],
    )
    summary = summarize(scan)
    scan.to_csv(SCAN_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    write_report(scan, summary)
    print(
        f"rows={len(scan)} unique_preds={scan['pred_index'].nunique()} "
        f"strict={int(scan['strict_consensus_gate'].sum())} loose={int(scan['loose_consensus_gate'].sum())} "
        f"best_all={scan['all_delta_vs_mixmin'].min():.6g} wrote={REPORT_OUT.relative_to(ROOT)}"
    )
    print(summary.head(20).to_string(index=False))


if __name__ == "__main__":
    main()
