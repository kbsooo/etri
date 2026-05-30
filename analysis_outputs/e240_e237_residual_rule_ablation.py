#!/usr/bin/env python3
"""E240: residual-energy rule ablation for the E237 Q3 cells.

E239 found that E237's learned Q3 cells are amplitude-filtered but not pure
top-k, and that E208 residual/nearest-neighbor energy is enriched. This audit
asks the falsification question:

Can simple public-free residual-energy rules replace the learned E237 cell
selector under the same E230/E237 stress metrics?

No submission files are created. Passing here would weaken the "learned
cell-level JEPA target" story; failing here strengthens that E237 is not just a
post-hoc residual-energy sort.
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
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402
import e162_branch_readability_flip_thresholds as e162  # noqa: E402
import e222_e211_support_tail_audit as e222  # noqa: E402
import e230_e224_support_tail_prune_audit as e230  # noqa: E402
import e237_cell_decisive_jepa_target as e237  # noqa: E402
import e238_e237_public_feedback_decoder as e238  # noqa: E402
import e239_e237_cell_motif_atlas as e239  # noqa: E402


Q3_IDX = TARGETS.index("Q3")
EPS = 1.0e-12

SUMMARY_OUT = OUT / "e240_e237_residual_rule_ablation_summary.csv"
TARGET_OUT = OUT / "e240_e237_residual_rule_ablation_targets.csv"
OVERLAP_OUT = OUT / "e240_e237_residual_rule_ablation_overlap.csv"
REPORT_OUT = OUT / "e240_e237_residual_rule_ablation_report.md"


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 40, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return e138.md_table(view.head(n), floatfmt)


def zscore(values: pd.Series) -> pd.Series:
    vals = pd.to_numeric(values, errors="coerce").astype(float)
    mu = float(vals.mean())
    sigma = float(vals.std(ddof=0))
    if sigma <= EPS:
        return pd.Series(np.zeros(len(vals)), index=vals.index)
    return (vals - mu) / sigma


def topk_index(rows: pd.DataFrame, score: pd.Series, k: int = 25) -> np.ndarray:
    ordered = rows.assign(_score=pd.to_numeric(score, errors="coerce")).sort_values(
        ["_score", "row_idx"], ascending=[False, True]
    )
    return ordered.head(k)["row_idx"].to_numpy(dtype=int)


def topk_within(rows: pd.DataFrame, base_score: pd.Series, inner_score: pd.Series, base_k: int, final_k: int) -> np.ndarray:
    base_idx = topk_index(rows, base_score, base_k)
    part = rows[rows["row_idx"].isin(base_idx)].copy()
    return topk_index(part, inner_score.loc[part.index], final_k)


def bool_selector(rows: pd.DataFrame, name: str) -> np.ndarray:
    return rows.loc[rows[name].astype(bool), "row_idx"].to_numpy(dtype=int)


def selector_specs(rows: pd.DataFrame) -> list[dict[str, Any]]:
    amp = rows["abs_logit_e224_minus_e154_q3"]
    resid_abs = rows["e208_resid_self_abs_mean"]
    nn_dist = rows["e208_nn_target_dist"]
    resid_pc10 = rows["e208_resid_self_pc10"]
    resid_norm = rows["e208_resid_self_norm"]
    e215_resid = rows["e215_resid_abs_mean"]
    low_margin = -rows["full_margin"]
    no_edge = -rows["near_test_edge_2"].fillna(0.0)
    no_gap_adj = -rows["gap_adjacent_2"].fillna(0.0)

    z_amp = zscore(amp)
    z_resid_abs = zscore(resid_abs)
    z_nn = zscore(nn_dist)
    z_pc10 = zscore(resid_pc10)
    z_resid_norm = zscore(resid_norm)
    z_e215 = zscore(e215_resid)
    z_low_margin = zscore(low_margin)
    z_no_edge = zscore(no_edge)
    z_no_gap = zscore(no_gap_adj)

    residual_combo = z_resid_abs + z_nn + z_pc10 + 0.5 * z_resid_norm
    e239_combo = z_amp + residual_combo + 0.5 * z_low_margin
    e239_combo_noedge = e239_combo + 0.35 * z_no_edge + 0.20 * z_no_gap
    e215_e208_combo = z_amp + 0.8 * residual_combo + 0.5 * z_e215 + 0.4 * z_low_margin

    specs = [
        {
            "selector_id": "control_e237_learned_cell25",
            "rule_family": "control",
            "row_idx": bool_selector(rows, "e237_drop"),
            "rule_note": "fixed E237 learned selected cells",
        },
        {
            "selector_id": "control_e230_swing25",
            "rule_family": "control",
            "row_idx": bool_selector(rows, "e230_swing25"),
            "rule_note": "E230 hand swing top25 cells",
        },
        {
            "selector_id": "control_e230_risk21",
            "rule_family": "control",
            "row_idx": bool_selector(rows, "e230_risk21"),
            "rule_note": "E230 hand risk top21 cells",
        },
        {
            "selector_id": "simple_amp_top25",
            "rule_family": "simple",
            "row_idx": topk_index(rows, amp, 25),
            "rule_note": "top25 by E224-vs-E154 Q3 absolute logit movement",
        },
        {
            "selector_id": "simple_resid_abs_top25",
            "rule_family": "simple",
            "row_idx": topk_index(rows, resid_abs, 25),
            "rule_note": "top25 by E208 residual self absolute mean",
        },
        {
            "selector_id": "simple_nn_dist_top25",
            "rule_family": "simple",
            "row_idx": topk_index(rows, nn_dist, 25),
            "rule_note": "top25 by E208 nearest-neighbor target distance",
        },
        {
            "selector_id": "simple_pc10_top25",
            "rule_family": "simple",
            "row_idx": topk_index(rows, resid_pc10, 25),
            "rule_note": "top25 by E208 residual self PC10",
        },
        {
            "selector_id": "top50_amp_then_resid_abs25",
            "rule_family": "top50_residual",
            "row_idx": topk_within(rows, amp, resid_abs, 50, 25),
            "rule_note": "within amplitude top50, choose residual-abs top25",
        },
        {
            "selector_id": "top50_amp_then_nn25",
            "rule_family": "top50_residual",
            "row_idx": topk_within(rows, amp, nn_dist, 50, 25),
            "rule_note": "within amplitude top50, choose NN-distance top25",
        },
        {
            "selector_id": "top50_amp_then_pc10_25",
            "rule_family": "top50_residual",
            "row_idx": topk_within(rows, amp, resid_pc10, 50, 25),
            "rule_note": "within amplitude top50, choose residual-PC10 top25",
        },
        {
            "selector_id": "top50_amp_then_resid_combo25",
            "rule_family": "top50_residual",
            "row_idx": topk_within(rows, amp, residual_combo, 50, 25),
            "rule_note": "within amplitude top50, choose E208 residual combo top25",
        },
        {
            "selector_id": "global_amp_resid_combo25",
            "rule_family": "combined",
            "row_idx": topk_index(rows, z_amp + residual_combo, 25),
            "rule_note": "global top25 by amplitude plus E208 residual combo",
        },
        {
            "selector_id": "global_e239_combo25",
            "rule_family": "combined",
            "row_idx": topk_index(rows, e239_combo, 25),
            "rule_note": "global top25 by E239 motif combo: amp + E208 residual + low full-margin",
        },
        {
            "selector_id": "global_e239_combo_noedge25",
            "rule_family": "combined",
            "row_idx": topk_index(rows, e239_combo_noedge, 25),
            "rule_note": "global E239 motif combo with edge/adjacency penalty",
        },
        {
            "selector_id": "global_e215_e208_combo25",
            "rule_family": "combined",
            "row_idx": topk_index(rows, e215_e208_combo, 25),
            "rule_note": "global top25 by amplitude plus E208 residual and E215 residual",
        },
    ]
    dedup: dict[tuple[int, ...], dict[str, Any]] = {}
    for spec in specs:
        row_idx = np.array(sorted(set(np.asarray(spec["row_idx"], dtype=int))), dtype=int)
        spec = dict(spec)
        spec["row_idx"] = row_idx
        key = tuple(row_idx.tolist())
        if key not in dedup:
            dedup[key] = spec
    return list(dedup.values())


def apply_q3_drop(e224: np.ndarray, e154: np.ndarray, row_idx: np.ndarray) -> np.ndarray:
    spec = {
        "variant_id": "tmp",
        "row_idx": np.asarray(row_idx, dtype=int),
        "target_idx": np.full(len(row_idx), Q3_IDX, dtype=int),
        "keep_fraction": 0.0,
    }
    return e230.apply_variant(e224, e154, spec)


def audit_specs(rows: pd.DataFrame, specs: list[dict[str, Any]]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    priors = e162.prior_arrays(sample)
    e95 = e230.load_prob(e230.E95_FILE, sample)
    e154 = e230.load_prob(e230.E154_FILE, sample)
    e224 = e230.load_prob(e230.E224_FILE, sample)

    base_spec = e222.Candidate(
        candidate_id="e224_original",
        file_name=e230.E224_FILE,
        anchor_file=e230.E154_FILE,
        family="e224_q3_scale_pareto",
        status="baseline",
        note="Current E224 clean capped-Q3/S4 JEPA candidate.",
    )
    base_rec, base_tgt, _ = e222.pair_audit(base_spec, "graft_vs_e154", e224, e154, e230.E154_FILE, priors, sample)
    base_actual_rec, _, _ = e222.pair_audit(base_spec, "actual_vs_e95", e224, e95, e230.E95_FILE, priors, sample)
    base_tgt = e222.add_ranking(base_tgt)
    base_q3 = base_tgt[base_tgt["target"].eq("Q3")].iloc[0]
    base_s4 = base_tgt[base_tgt["target"].eq("S4")].iloc[0]

    summary_rows: list[dict[str, Any]] = []
    target_parts: list[pd.DataFrame] = []
    overlap_rows: list[dict[str, Any]] = []
    e237_set = set(rows.loc[rows["e237_drop"].astype(bool), "row_idx"].astype(int))
    swing_set = set(rows.loc[rows["e230_swing25"].astype(bool), "row_idx"].astype(int))
    risk_set = set(rows.loc[rows["e230_risk21"].astype(bool), "row_idx"].astype(int))

    for spec in specs:
        row_idx = np.asarray(spec["row_idx"], dtype=int)
        selector_id = str(spec["selector_id"])
        pred = apply_q3_drop(e224, e154, row_idx)
        candidate = e222.Candidate(
            candidate_id=selector_id,
            file_name=selector_id,
            anchor_file=e230.E154_FILE,
            family="e240_residual_rule_ablation",
            status="diagnostic",
            note=str(spec["rule_note"]),
        )
        selected = set(row_idx.astype(int))
        for ref_name, ref in [("e237", e237_set), ("e230_swing25", swing_set), ("e230_risk21", risk_set)]:
            inter = len(selected & ref)
            union = len(selected | ref)
            overlap_rows.append(
                {
                    "selector_id": selector_id,
                    "rule_family": spec["rule_family"],
                    "reference": ref_name,
                    "selected_n": len(selected),
                    "reference_n": len(ref),
                    "intersection": inter,
                    "jaccard": float(inter / union) if union else 1.0,
                    "selector_recall": float(inter / max(len(selected), 1)),
                    "reference_recall": float(inter / max(len(ref), 1)),
                }
            )
        for pair_kind, base_name, base in [
            ("graft_vs_e154", e230.E154_FILE, e154),
            ("actual_vs_e95", e230.E95_FILE, e95),
        ]:
            rec, targets, _ = e222.pair_audit(candidate, pair_kind, pred, base, base_name, priors, sample)
            rec.update(
                {
                    "selector_id": selector_id,
                    "rule_family": spec["rule_family"],
                    "rule_note": spec["rule_note"],
                    "pruned_cells": int(len(row_idx)),
                    "pruned_q3": int(len(row_idx)),
                    "pruned_s4": 0,
                    "row_idx_list": " ".join(map(str, row_idx.tolist())),
                }
            )
            summary_rows.append(rec)
            if not targets.empty:
                targets = targets.copy()
                targets["selector_id"] = selector_id
                targets["rule_family"] = spec["rule_family"]
                target_parts.append(targets)

    summary = pd.DataFrame(summary_rows)
    target_df = pd.concat(target_parts, ignore_index=True) if target_parts else pd.DataFrame()
    target_df = e222.add_ranking(target_df) if not target_df.empty else target_df
    summary = e230.add_comparison_metrics(summary, target_df, pd.Series(base_rec)) if not summary.empty else summary

    actual = summary[summary["pair_kind"].eq("actual_vs_e95")][
        [
            "candidate_id",
            "expected_focus",
            "adverse_delta",
            "support_prob_focus_swing_weighted",
        ]
    ].rename(
        columns={
            "expected_focus": "actual_expected_focus",
            "adverse_delta": "actual_adverse_delta",
            "support_prob_focus_swing_weighted": "actual_support_prob_focus_swing_weighted",
        }
    )
    actual["actual_expected_delta_vs_e224"] = actual["actual_expected_focus"] - float(base_actual_rec["expected_focus"])
    actual["actual_adverse_reduction_vs_e224"] = float(base_actual_rec["adverse_delta"]) - actual["actual_adverse_delta"]
    actual["actual_support_gain_vs_e224"] = (
        actual["actual_support_prob_focus_swing_weighted"] - float(base_actual_rec["support_prob_focus_swing_weighted"])
    )
    graft = summary[summary["pair_kind"].eq("graft_vs_e154")].copy()
    graft = graft.merge(actual, on="candidate_id", how="left")
    base_q3_top = float(base_q3["top1_over_abs_expected"])
    base_q3_adverse = float(base_q3["adverse_delta"])
    base_s4_expected = float(base_s4["expected_focus"])
    graft["e237_like_gate"] = (
        (graft["expected_loss_vs_e224"] <= 0.000080)
        & (graft["adverse_reduction_vs_e224"] >= 0.000150)
        & (graft["support_gain_vs_e224"] > 0.0)
        & (graft["q3_top1_over_abs_expected"] <= min(base_q3_top, 0.875120489))
        & (graft["q3_adverse_delta"] <= base_q3_adverse)
        & (graft["s4_expected_focus"] <= base_s4_expected + 0.000080)
        & (graft["actual_expected_delta_vs_e224"] <= 0.000020)
        & (graft["actual_adverse_reduction_vs_e224"] >= 0.000150)
        & (graft["actual_support_gain_vs_e224"] > 0.0)
    )
    graft["e237_like_score"] = (
        -graft["expected_loss_vs_e224"].fillna(9.0) * 140.0
        + graft["adverse_reduction_vs_e224"].fillna(0.0) * 100.0
        + graft["support_gain_vs_e224"].fillna(0.0) * 0.08
        - np.maximum(graft["q3_top1_over_abs_expected"].fillna(9.0) - base_q3_top, 0.0) * 0.04
    )
    overlap = pd.DataFrame(overlap_rows)
    e237_overlap = overlap[overlap["reference"].eq("e237")][["selector_id", "intersection", "jaccard"]].rename(
        columns={"intersection": "overlap_e237", "jaccard": "jaccard_e237"}
    )
    swing_overlap = overlap[overlap["reference"].eq("e230_swing25")][["selector_id", "intersection", "jaccard"]].rename(
        columns={"intersection": "overlap_e230_swing25", "jaccard": "jaccard_e230_swing25"}
    )
    risk_overlap = overlap[overlap["reference"].eq("e230_risk21")][["selector_id", "intersection", "jaccard"]].rename(
        columns={"intersection": "overlap_e230_risk21", "jaccard": "jaccard_e230_risk21"}
    )
    graft = graft.merge(e237_overlap, left_on="candidate_id", right_on="selector_id", how="left").drop(
        columns=["selector_id_y"], errors="ignore"
    ).rename(columns={"selector_id_x": "selector_id"})
    graft = graft.merge(swing_overlap, on="selector_id", how="left")
    graft = graft.merge(risk_overlap, on="selector_id", how="left")
    return graft, target_df, overlap


def write_report(summary: pd.DataFrame, target_df: pd.DataFrame, overlap: pd.DataFrame) -> None:
    ranked = summary.sort_values(["e237_like_gate", "e237_like_score"], ascending=[False, False])
    simple = ranked[~ranked["rule_family"].eq("control")].copy()
    control = ranked[ranked["rule_family"].eq("control")].copy()
    gate_pass = simple[simple["e237_like_gate"].astype(bool)]
    top_cols = [
        "candidate_id",
        "rule_family",
        "pruned_cells",
        "expected_loss_vs_e224",
        "adverse_reduction_vs_e224",
        "support_gain_vs_e224",
        "actual_expected_delta_vs_e224",
        "actual_adverse_reduction_vs_e224",
        "actual_support_gain_vs_e224",
        "q3_top1_over_abs_expected",
        "q3_adverse_delta",
        "overlap_e237",
        "overlap_e230_swing25",
        "overlap_e230_risk21",
        "e230_gate",
        "e237_like_gate",
        "e237_like_score",
    ]
    target_cols = [
        "candidate_id",
        "target",
        "moved_cells",
        "expected_focus",
        "adverse_delta",
        "support_prob_focus_swing_weighted",
        "top1_over_abs_expected",
    ]
    overlap_cols = [
        "selector_id",
        "rule_family",
        "reference",
        "selected_n",
        "reference_n",
        "intersection",
        "jaccard",
    ]
    lines = [
        "# E240 E237 Residual-Rule Ablation",
        "",
        "## Question",
        "",
        "Can the E239 residual-energy motif replace the learned E237 Q3 cell selector with a simple public-free rule?",
        "",
        "## Control Selectors",
        "",
        md_table(control, top_cols, n=10),
        "",
        "## Simple-Rule Ranking",
        "",
        md_table(simple, top_cols, n=30),
        "",
        "## Simple E237-Like Gate Passes",
        "",
        md_table(gate_pass, top_cols, n=20),
        "",
        "## Overlap",
        "",
        md_table(overlap.sort_values(["selector_id", "reference"]), overlap_cols, n=60),
        "",
        "## Target Breakdown",
        "",
        md_table(target_df[target_df["pair_kind"].eq("graft_vs_e154")].sort_values(["candidate_id", "target"]), target_cols, n=70),
        "",
        "## Decision",
        "",
    ]
    if gate_pass.empty:
        lines.append(
            "- No simple residual-energy or amplitude rule passed the E237-like graft plus actual-vs-E95 stress. This supports the learned-cell target over a post-hoc top50 residual sort."
        )
    else:
        best = gate_pass.sort_values("e237_like_score", ascending=False).iloc[0]
        lines.append(
            f"- Simple rule `{best['candidate_id']}` passed the E237-like gate. This weakens the learned-cell claim and should be used only as a diagnostic until E237 public feedback is known."
        )
    lines.append("- No submission is created from E240.")
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    rows = e239.build_rows()
    specs = selector_specs(rows)
    summary, target_df, overlap = audit_specs(rows, specs)
    summary = summary.sort_values(["e237_like_gate", "e237_like_score"], ascending=[False, False])
    target_df = target_df.sort_values(["pair_kind", "candidate_id", "target"]) if not target_df.empty else target_df
    overlap = overlap.sort_values(["selector_id", "reference"])
    summary.to_csv(SUMMARY_OUT, index=False)
    target_df.to_csv(TARGET_OUT, index=False)
    overlap.to_csv(OVERLAP_OUT, index=False)
    write_report(summary, target_df, overlap)
    simple = summary[~summary["rule_family"].eq("control")]
    print(f"[E240 simple selectors] {len(simple)}")
    print(f"[E240 simple e237-like gate passes] {int(simple['e237_like_gate'].sum())}")
    cols = [
        "candidate_id",
        "rule_family",
        "expected_loss_vs_e224",
        "adverse_reduction_vs_e224",
        "support_gain_vs_e224",
        "actual_adverse_reduction_vs_e224",
        "overlap_e237",
        "e237_like_gate",
        "e237_like_score",
    ]
    print(summary[cols].head(12).round(9).to_string(index=False))
    print(f"\nwrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
