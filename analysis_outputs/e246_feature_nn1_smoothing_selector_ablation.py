#!/usr/bin/env python3
"""E246: feature-NN1 smoothing selector ablation for the E237 Q3 cells.

E245 found that E237's Q3 rollback is compatible with the only E207
`true_jepa_candidate` regime: broad-stage2 feature nearest-neighbor pairs. This
script asks the falsification question:

Can that representation become a selector by itself?

If feature-NN1 smoothing is the hidden law behind E237, selectors built only
from hypothetical Q3 nearest-neighbor smoothing should pass the same E230/E237
stress gates. If they fail, E245 remains a supportive diagnostic, not a
submission generator.

No submission files are created.
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
import e222_e211_support_tail_audit as e222  # noqa: E402
import e230_e224_support_tail_prune_audit as e230  # noqa: E402
import e237_cell_decisive_jepa_target as e237  # noqa: E402
import e239_e237_cell_motif_atlas as e239  # noqa: E402


EPS = 1.0e-12
Q3_IDX = TARGETS.index("Q3")

LOCAL_IN = OUT / "e245_feature_nn1_jepa_compat_local_cells.csv"
SUMMARY_OUT = OUT / "e246_feature_nn1_smoothing_selector_summary.csv"
TARGET_OUT = OUT / "e246_feature_nn1_smoothing_selector_targets.csv"
SELECTOR_OUT = OUT / "e246_feature_nn1_smoothing_selector_rows.csv"
OVERLAP_OUT = OUT / "e246_feature_nn1_smoothing_selector_overlap.csv"
REPORT_OUT = OUT / "e246_feature_nn1_smoothing_selector_report.md"


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


def topk_index(rows: pd.DataFrame, score: pd.Series, k: int) -> np.ndarray:
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


def single_row_smoothing_scores(local: pd.DataFrame) -> pd.DataFrame:
    """Estimate the directed NN-pair Q3 abs-logit change if one row is rolled back."""
    rows = local.sort_values("row_idx").reset_index(drop=True).copy()
    e224 = rows["e224_q3_logit"].to_numpy(dtype=np.float64)
    e154 = rows["e154_q3_logit"].to_numpy(dtype=np.float64)
    nn = rows["nn_row_idx"].to_numpy(dtype=int)

    incoming: list[list[int]] = [[] for _ in range(len(rows))]
    for source, target in enumerate(nn):
        incoming[int(target)].append(int(source))

    source_delta = np.abs(e154 - e224[nn]) - np.abs(e224 - e224[nn])
    incoming_delta_sum = np.zeros(len(rows), dtype=np.float64)
    incoming_count = np.zeros(len(rows), dtype=np.float64)
    for row_idx, sources in enumerate(incoming):
        if not sources:
            continue
        src = np.asarray(sources, dtype=int)
        before = np.abs(e224[src] - e224[row_idx])
        after = np.abs(e224[src] - e154[row_idx])
        incoming_delta_sum[row_idx] = float(np.sum(after - before))
        incoming_count[row_idx] = float(len(src))

    affected_count = 1.0 + incoming_count
    total_delta = source_delta + incoming_delta_sum
    rows["rollback_amp_abs"] = np.abs(e154 - e224)
    rows["nn_source_pair_delta"] = source_delta
    rows["nn_incoming_pair_delta_sum"] = incoming_delta_sum
    rows["nn_incoming_pair_count"] = incoming_count
    rows["single_row_pair_delta_sum"] = total_delta
    rows["single_row_pair_delta_mean"] = total_delta / np.maximum(affected_count, 1.0)
    rows["single_row_smooth_gain_sum"] = -rows["single_row_pair_delta_sum"]
    rows["single_row_smooth_gain_mean"] = -rows["single_row_pair_delta_mean"]
    rows["amp_smooth_gain_sum"] = rows["single_row_smooth_gain_sum"] * rows["rollback_amp_abs"]
    rows["amp_smooth_gain_mean"] = rows["single_row_smooth_gain_mean"] * rows["rollback_amp_abs"]
    rows["source_smooth_gain"] = -rows["nn_source_pair_delta"]
    rows["incoming_smooth_gain_sum"] = -rows["nn_incoming_pair_delta_sum"]
    return rows


def build_selector_rows() -> pd.DataFrame:
    local = pd.read_csv(LOCAL_IN)
    rows = single_row_smoothing_scores(local)
    motif = e239.build_rows()
    keep_cols = [
        "row_idx",
        "e237_drop",
        "e230_swing25",
        "e230_risk21",
        "abs_logit_e224_minus_e154_q3",
        "e208_resid_self_abs_mean",
        "e208_nn_target_dist",
        "e208_resid_self_pc10",
        "full_margin",
        "near_test_edge_2",
        "gap_adjacent_2",
    ]
    rows = rows.merge(motif[[c for c in keep_cols if c in motif.columns]], on="row_idx", how="left")
    for col in ["e237_drop", "e230_swing25", "e230_risk21"]:
        rows[col] = rows[col].fillna(False).astype(bool)
    rows["amp_rank"] = rows["rollback_amp_abs"].rank(method="first", ascending=False)
    rows["smooth_sum_rank"] = rows["single_row_smooth_gain_sum"].rank(method="first", ascending=False)
    rows["smooth_mean_rank"] = rows["single_row_smooth_gain_mean"].rank(method="first", ascending=False)
    rows["amp_smooth_rank"] = rows["amp_smooth_gain_sum"].rank(method="first", ascending=False)
    return rows


def selector_specs(rows: pd.DataFrame) -> list[dict[str, Any]]:
    amp = rows["rollback_amp_abs"]
    smooth_sum = rows["single_row_smooth_gain_sum"]
    smooth_mean = rows["single_row_smooth_gain_mean"]
    amp_smooth_sum = rows["amp_smooth_gain_sum"]
    amp_smooth_mean = rows["amp_smooth_gain_mean"]
    incoming = rows["incoming_smooth_gain_sum"]
    source = rows["source_smooth_gain"]
    nn_dist_penalty = -zscore(rows["nn_dist"])
    smooth_dist = zscore(smooth_sum) + 0.35 * nn_dist_penalty

    specs: list[dict[str, Any]] = [
        {
            "selector_id": "control_e237_learned_cell25",
            "rule_family": "control",
            "row_idx": bool_selector(rows, "e237_drop"),
            "rule_note": "fixed E237 learned Q3 cells",
        },
        {
            "selector_id": "control_e230_swing25",
            "rule_family": "control",
            "row_idx": bool_selector(rows, "e230_swing25"),
            "rule_note": "E230 hand Q3 swing-top25 cells",
        },
        {
            "selector_id": "control_e230_risk21",
            "rule_family": "control",
            "row_idx": bool_selector(rows, "e230_risk21"),
            "rule_note": "E230 hand Q3 risk-top21 cells",
        },
        {
            "selector_id": "simple_amp_top25",
            "rule_family": "control",
            "row_idx": topk_index(rows, amp, 25),
            "rule_note": "top25 by E224-vs-E154 Q3 rollback amplitude",
        },
    ]
    for k in [10, 13, 21, 25, 34]:
        specs.append(
            {
                "selector_id": f"nn_smooth_sum_top{k}",
                "rule_family": "feature_nn1",
                "row_idx": topk_index(rows, smooth_sum, k),
                "rule_note": f"top{k} by single-row directed feature-NN1 Q3 smoothing gain sum",
            }
        )
    for k in [13, 21, 25]:
        specs.append(
            {
                "selector_id": f"nn_smooth_mean_top{k}",
                "rule_family": "feature_nn1",
                "row_idx": topk_index(rows, smooth_mean, k),
                "rule_note": f"top{k} by single-row directed feature-NN1 Q3 smoothing gain mean",
            }
        )
        specs.append(
            {
                "selector_id": f"nn_amp_smooth_top{k}",
                "rule_family": "feature_nn1_amp",
                "row_idx": topk_index(rows, amp_smooth_sum, k),
                "rule_note": f"top{k} by amplitude-weighted feature-NN1 Q3 smoothing gain",
            }
        )
    specs.extend(
        [
            {
                "selector_id": "top50_amp_then_smooth25",
                "rule_family": "feature_nn1_amp",
                "row_idx": topk_within(rows, amp, smooth_sum, 50, 25),
                "rule_note": "within amplitude top50, choose feature-NN1 smooth-sum top25",
            },
            {
                "selector_id": "top50_amp_then_amp_smooth25",
                "rule_family": "feature_nn1_amp",
                "row_idx": topk_within(rows, amp, amp_smooth_sum, 50, 25),
                "rule_note": "within amplitude top50, choose amplitude-weighted smooth top25",
            },
            {
                "selector_id": "incoming_smooth_top25",
                "rule_family": "feature_nn1",
                "row_idx": topk_index(rows, incoming, 25),
                "rule_note": "top25 by incoming directed feature-NN1 smoothing gain",
            },
            {
                "selector_id": "source_smooth_top25",
                "rule_family": "feature_nn1",
                "row_idx": topk_index(rows, source, 25),
                "rule_note": "top25 by outgoing/source directed feature-NN1 smoothing gain",
            },
            {
                "selector_id": "smooth_dist_top25",
                "rule_family": "feature_nn1",
                "row_idx": topk_index(rows, smooth_dist, 25),
                "rule_note": "top25 by smooth-sum z-score with mild nearest-distance penalty",
            },
            {
                "selector_id": "amp_smooth_mean_top25",
                "rule_family": "feature_nn1_amp",
                "row_idx": topk_index(rows, amp_smooth_mean, 25),
                "rule_note": "top25 by amplitude-weighted mean smoothing gain",
            },
        ]
    )

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


def target_metric(targets: pd.DataFrame, candidate_id: str, target: str, col: str, default: float = np.nan) -> float:
    part = targets[
        targets["candidate_id"].eq(candidate_id)
        & targets["pair_kind"].eq("graft_vs_e154")
        & targets["target"].eq(target)
    ]
    if part.empty or col not in part.columns:
        return default
    return float(part[col].iloc[0])


def selector_quality(rows: pd.DataFrame, row_idx: np.ndarray) -> dict[str, Any]:
    part = rows[rows["row_idx"].isin(set(row_idx.astype(int)))]
    if part.empty:
        return {
            "selected_smooth_gain_sum": 0.0,
            "selected_pair_delta_sum": 0.0,
            "selected_amp_mean": np.nan,
            "selected_nn_dist_mean": np.nan,
            "selected_e237_overlap": 0,
        }
    return {
        "selected_smooth_gain_sum": float(part["single_row_smooth_gain_sum"].sum()),
        "selected_pair_delta_sum": float(part["single_row_pair_delta_sum"].sum()),
        "selected_smooth_gain_mean": float(part["single_row_smooth_gain_mean"].mean()),
        "selected_amp_mean": float(part["rollback_amp_abs"].mean()),
        "selected_nn_dist_mean": float(part["nn_dist"].mean()),
        "selected_positive_smooth_share": float((part["single_row_smooth_gain_sum"] > 0).mean()),
        "selected_e237_overlap": int(part["e237_drop"].sum()),
        "selected_e230_swing_overlap": int(part["e230_swing25"].sum()),
        "selected_e230_risk_overlap": int(part["e230_risk21"].sum()),
    }


def audit_specs(rows: pd.DataFrame, specs: list[dict[str, Any]]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    priors = e162.prior_arrays(sample)
    e95 = e230.load_prob(e230.E95_FILE, sample)
    e154 = e230.load_prob(e230.E154_FILE, sample)
    e224 = e230.load_prob(e230.E224_FILE, sample)
    base_rec, base_tgt, base_actual_rec, _ = e237.e224_baseline(sample, priors, e95, e154, e224)
    base_tgt = e222.add_ranking(base_tgt)
    base_q3_top = target_metric(base_tgt, "e224_original", "Q3", "top1_over_abs_expected", 9.0)
    base_q3_adverse = target_metric(base_tgt, "e224_original", "Q3", "adverse_delta", 9.0)
    base_s4_expected = target_metric(base_tgt, "e224_original", "S4", "expected_focus", 0.0)

    summary_rows: list[dict[str, Any]] = []
    target_parts: list[pd.DataFrame] = []
    overlap_rows: list[dict[str, Any]] = []
    ref_sets = {
        "e237": set(rows.loc[rows["e237_drop"].astype(bool), "row_idx"].astype(int)),
        "e230_swing25": set(rows.loc[rows["e230_swing25"].astype(bool), "row_idx"].astype(int)),
        "e230_risk21": set(rows.loc[rows["e230_risk21"].astype(bool), "row_idx"].astype(int)),
        "amp_top25": set(topk_index(rows, rows["rollback_amp_abs"], 25).astype(int)),
    }

    for spec in specs:
        row_idx = np.asarray(spec["row_idx"], dtype=int)
        selector_id = str(spec["selector_id"])
        pred = apply_q3_drop(e224, e154, row_idx)
        candidate = e222.Candidate(
            candidate_id=selector_id,
            file_name=selector_id,
            anchor_file=e230.E154_FILE,
            family="e246_feature_nn1_smoothing_selector",
            status="diagnostic",
            note=str(spec["rule_note"]),
        )
        selected = set(row_idx.astype(int))
        for ref_name, ref in ref_sets.items():
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
        meta = {
            "selector_id": selector_id,
            "rule_family": spec["rule_family"],
            "rule_note": spec["rule_note"],
            "pruned_cells": int(len(row_idx)),
            "pruned_q3": int(len(row_idx)),
            "pruned_s4": 0,
            "row_idx_list": " ".join(map(str, row_idx.tolist())),
            **selector_quality(rows, row_idx),
        }
        for pair_kind, base_name, base in [
            ("graft_vs_e154", e230.E154_FILE, e154),
            ("actual_vs_e95", e230.E95_FILE, e95),
        ]:
            rec, targets, _ = e222.pair_audit(candidate, pair_kind, pred, base, base_name, priors, sample)
            rec.update(meta)
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
    for ref_name in ref_sets:
        part = overlap[overlap["reference"].eq(ref_name)][["selector_id", "intersection", "jaccard"]].rename(
            columns={"intersection": f"overlap_{ref_name}", "jaccard": f"jaccard_{ref_name}"}
        )
        graft = graft.merge(part, on="selector_id", how="left")
    return graft, target_df, overlap


def write_report(summary: pd.DataFrame, target_df: pd.DataFrame, overlap: pd.DataFrame, rows: pd.DataFrame) -> None:
    ranked = summary.sort_values(["e237_like_gate", "e237_like_score"], ascending=[False, False])
    controls = ranked[ranked["rule_family"].eq("control")].copy()
    feature_rules = ranked[~ranked["rule_family"].eq("control")].copy()
    gate_pass = feature_rules[feature_rules["e237_like_gate"].astype(bool)]
    nonclone_pass = gate_pass[gate_pass["overlap_e237"].fillna(0) < 20]

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
        "selected_smooth_gain_sum",
        "selected_positive_smooth_share",
        "overlap_e237",
        "overlap_e230_swing25",
        "overlap_amp_top25",
        "e230_gate",
        "e237_like_gate",
        "e237_like_score",
    ]
    selector_cols = [
        "row_idx",
        "subject_id",
        "lifelog_date",
        "nn_row_idx",
        "nn_dist",
        "rollback_amp_abs",
        "single_row_smooth_gain_sum",
        "single_row_smooth_gain_mean",
        "amp_smooth_gain_sum",
        "e237_drop",
        "e230_swing25",
        "e230_risk21",
        "amp_rank",
        "smooth_sum_rank",
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
    strongest_rows = rows.sort_values("single_row_smooth_gain_sum", ascending=False).head(30)
    lines = [
        "# E246 Feature-NN1 Smoothing Selector Ablation",
        "",
        "## Question",
        "",
        "Can E245's feature-nearest-neighbor JEPA compatibility become a public-free selector, rather than only an explanation for E237?",
        "",
        "A pass requires a feature-NN1 selector to survive the same E237-like graft plus actual-vs-E95 gate. A non-clone pass additionally needs `<20/25` overlap with E237.",
        "",
        "## Controls",
        "",
        md_table(controls, top_cols, n=10),
        "",
        "## Feature-NN1 Selector Ranking",
        "",
        md_table(feature_rules, top_cols, n=40),
        "",
        "## Feature-NN1 Gate Passes",
        "",
        md_table(gate_pass, top_cols, n=20),
        "",
        "## Non-Clone Gate Passes",
        "",
        md_table(nonclone_pass, top_cols, n=20),
        "",
        "## Strongest Single-Row Smooth-Gain Cells",
        "",
        md_table(strongest_rows, selector_cols, n=30),
        "",
        "## Overlap",
        "",
        md_table(overlap.sort_values(["selector_id", "reference"]), overlap_cols, n=80),
        "",
        "## Target Breakdown",
        "",
        md_table(target_df[target_df["pair_kind"].eq("graft_vs_e154")].sort_values(["candidate_id", "target"]), target_cols, n=80),
        "",
        "## Decision",
        "",
    ]
    if nonclone_pass.empty and gate_pass.empty:
        lines.append(
            "- No feature-NN1 smoothing selector passed the E237-like stress gate. E245 remains a supportive LeJEPA diagnostic for E237, not a standalone candidate generator."
        )
    elif nonclone_pass.empty:
        lines.append(
            "- Feature-NN1 selectors passed only as E237-near clones. This supports E237 compatibility but does not justify a new submission before E237 public feedback."
        )
    else:
        best = nonclone_pass.sort_values("e237_like_score", ascending=False).iloc[0]
        lines.append(
            f"- `{best['candidate_id']}` passed as a non-clone feature-NN1 selector. It should become the next materialization target after exact schema audit."
        )
    lines.append("- No submission is created by E246.")
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    rows = build_selector_rows()
    specs = selector_specs(rows)
    summary, target_df, overlap = audit_specs(rows, specs)
    summary = summary.sort_values(["e237_like_gate", "e237_like_score"], ascending=[False, False])
    target_df = target_df.sort_values(["pair_kind", "candidate_id", "target"]) if not target_df.empty else target_df
    overlap = overlap.sort_values(["selector_id", "reference"])
    rows = rows.sort_values("single_row_smooth_gain_sum", ascending=False)

    summary.to_csv(SUMMARY_OUT, index=False)
    target_df.to_csv(TARGET_OUT, index=False)
    rows.to_csv(SELECTOR_OUT, index=False)
    overlap.to_csv(OVERLAP_OUT, index=False)
    write_report(summary, target_df, overlap, rows)

    feature = summary[~summary["rule_family"].eq("control")]
    print(f"[E246 feature selectors] {len(feature)}")
    print(f"[E246 feature e237-like gate passes] {int(feature['e237_like_gate'].sum())}")
    cols = [
        "candidate_id",
        "rule_family",
        "expected_loss_vs_e224",
        "adverse_reduction_vs_e224",
        "support_gain_vs_e224",
        "actual_adverse_reduction_vs_e224",
        "selected_smooth_gain_sum",
        "overlap_e237",
        "e237_like_gate",
        "e237_like_score",
    ]
    print(summary[cols].head(16).round(9).to_string(index=False))
    print(f"\nwrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
