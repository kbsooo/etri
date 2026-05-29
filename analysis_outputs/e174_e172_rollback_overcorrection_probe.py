#!/usr/bin/env python3
"""E174: rollback overcorrection probe for E172.

E173 says E172 repairs E169's visible/flank tail, but the rollback itself costs
focus-prior edge mostly in Q2/S2. This script asks whether E172's keep=0.25
rollback is too conservative, or whether that cost is necessary to keep the
visible-tail gate closed.

No model is trained. A submission is materialized only if a partial reopening
keeps the visible-tail guard while recovering a public-readable amount of
focus-prior edge versus E172.
"""

from __future__ import annotations

import hashlib
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
import e164_universe_broad_edge_screen as e164  # noqa: E402
import e165_broad_edge_bad_axis_geometry as e165  # noqa: E402
import e166_broad_survivor_scale_probe as e166  # noqa: E402
import e171_e169_critical_cell_prior_audit as e171  # noqa: E402
import e172_e169_critical_tail_rollback_probe as e172  # noqa: E402


E95_FILE = "submission_e95_hardtail_541e3973.csv"
E169_FILE = "submission_e169_ctx_veto_c5e806e3.csv"
E172_FILE = "submission_e172_vis_pos_all_keep0p25_d90f4407.csv"
E154_FILE = "submission_e154_s3repair_9f2e2e73.csv"
E101_FILE = "submission_e101_q2s3tail_177569bc.csv"
MIXMIN_FILE = "submission_mixmin_0c916bb4.csv"

SCAN_OUT = OUT / "e174_e172_rollback_overcorrection_probe_scan.csv"
SHORTLIST_OUT = OUT / "e174_e172_rollback_overcorrection_probe_shortlist.csv"
ROLLBACK_CELLS_OUT = OUT / "e174_e172_rollback_overcorrection_probe_cells.csv"
REPORT_OUT = OUT / "e174_e172_rollback_overcorrection_probe_report.md"

EPS = 1.0e-12


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 40, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return e138.md_table(view.head(n), floatfmt)


def load_prob(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    return e166.load_prob_path(OUT / file_name, sample)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    aa = np.asarray(a, dtype=np.float64).reshape(-1)
    bb = np.asarray(b, dtype=np.float64).reshape(-1)
    den = float(np.linalg.norm(aa) * np.linalg.norm(bb))
    if den <= EPS:
        return 0.0
    return float(np.dot(aa, bb) / den)


def rollback_cell_table(cells: pd.DataFrame, e172_prob: np.ndarray, e169_prob: np.ndarray) -> pd.DataFrame:
    out = cells.copy()
    selected = out["expected_delta_visible_mean"].gt(0).to_numpy()
    r = out["sub_idx"].to_numpy(dtype=int)
    c = out["target_idx"].to_numpy(dtype=int)
    d1, d0 = e162.hard_loss_deltas(e172_prob[r, c], e169_prob[r, c])
    d1 = d1 / e172.N_PUBLIC_CELLS
    d0 = d0 / e172.N_PUBLIC_CELLS
    for prior in ["focus_mean", "visible_mean", "subject", "flank_mean", "nearest_hard085"]:
        p = out[f"p_y1_{prior}"].to_numpy(dtype=np.float64)
        out[f"rollback_delta_{prior}"] = p * d1 + (1.0 - p) * d0
    out["rollback_selected_e172"] = selected
    out["rollback_abs_swing"] = np.abs(d1 - d0)
    out["rollback_support_label"] = np.where(d1 < d0, 1, 0)
    out["rollback_support_prob_focus"] = np.where(
        out["rollback_support_label"].eq(1),
        out["p_y1_focus_mean"],
        1.0 - out["p_y1_focus_mean"],
    )
    out["rollback_focus_cost_rank"] = (
        out["rollback_delta_focus_mean"].where(selected, -np.inf).rank(method="first", ascending=False).astype(int)
    )
    return out


def base_keep_values(cells: pd.DataFrame, keep: float = 0.25) -> np.ndarray:
    keep_values = np.ones(len(cells), dtype=np.float64)
    keep_values[cells["expected_delta_visible_mean"].gt(0).to_numpy()] = float(keep)
    return keep_values


def keep_matrix_from_values(cells: pd.DataFrame, keep_values: np.ndarray) -> np.ndarray:
    mat = np.ones((250, len(TARGETS)), dtype=np.float64)
    r = cells["sub_idx"].to_numpy(dtype=int)
    c = cells["target_idx"].to_numpy(dtype=int)
    mat[r, c] = np.asarray(keep_values, dtype=np.float64)
    return mat


def build_specs(cells: pd.DataFrame, rollback_cells: pd.DataFrame) -> list[dict[str, Any]]:
    selected = rollback_cells["rollback_selected_e172"].to_numpy()
    specs: list[dict[str, Any]] = [
        {"policy": "baseline_e169_keep1", "keep_values": np.ones(len(cells), dtype=np.float64)},
        {"policy": "baseline_e172_keep0p25", "keep_values": base_keep_values(cells, 0.25)},
    ]

    for keep in [0.35, 0.40, 0.50, 0.60, 0.65, 0.75]:
        specs.append({"policy": f"uniform_visiblepos_keep{str(keep).replace('.', 'p')}", "keep_values": base_keep_values(cells, keep)})

    groups: list[tuple[str, np.ndarray]] = []
    target = rollback_cells["target"].astype(str)
    for name, targets in [
        ("q2", ["Q2"]),
        ("s2", ["S2"]),
        ("q2s2", ["Q2", "S2"]),
        ("q2s2s1", ["Q2", "S2", "S1"]),
        ("q2s2s3", ["Q2", "S2", "S3"]),
        ("positive_cost_targets", ["Q2", "S2", "S1", "S3", "S4"]),
        ("negative_cost_targets", ["Q1", "Q3"]),
    ]:
        groups.append((name, selected & target.isin(targets).to_numpy()))

    cost = rollback_cells["rollback_delta_focus_mean"].to_numpy(dtype=np.float64)
    positive_cost = selected & (cost > 0)
    groups.append(("focus_cost_positive", positive_cost))
    for n in [25, 50, 75, 100, 150, 200]:
        top = selected & rollback_cells["rollback_focus_cost_rank"].le(n).to_numpy()
        groups.append((f"focus_cost_top{n}", top))
    groups.extend(
        [
            ("non_e72_focus_cost_positive", positive_cost & ~rollback_cells["e72_active"].fillna(False).astype(bool).to_numpy()),
            ("between_focus_cost_positive", positive_cost & rollback_cells["between_train_runs"].fillna(False).astype(bool).to_numpy()),
            ("q2s2_focus_cost_positive", positive_cost & target.isin(["Q2", "S2"]).to_numpy()),
            ("q2s2_non_e72", selected & target.isin(["Q2", "S2"]).to_numpy() & ~rollback_cells["e72_active"].fillna(False).astype(bool).to_numpy()),
        ]
    )

    seen: set[tuple[str, float]] = set()
    for name, mask in groups:
        count = int(mask.sum())
        if count == 0:
            continue
        for keep in [0.50, 0.65, 0.75, 1.00]:
            key = (name, keep)
            if key in seen:
                continue
            seen.add(key)
            kv = base_keep_values(cells, 0.25)
            kv[mask] = keep
            specs.append({"policy": f"reopen_{name}_to{str(keep).replace('.', 'p')}", "keep_values": kv})
    return specs


def materialize(sample: pd.DataFrame, pred: np.ndarray, policy: str) -> str:
    digest = hashlib.sha1(np.round(pred, 10).tobytes()).hexdigest()[:8]
    safe = (
        policy.replace("uniform_visiblepos_", "uvp_")
        .replace("reopen_", "ro_")
        .replace("focus_cost_", "fc_")
        .replace("positive", "pos")
        .replace("targets", "tgts")
    )
    safe = "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in safe)[:80]
    file_name = f"submission_e174_{safe}_{digest}.csv"
    sub = sample[KEYS].copy()
    sub[TARGETS] = pred
    sub.to_csv(OUT / file_name, index=False)
    return file_name


def score_specs(
    specs: list[dict[str, Any]],
    sample: pd.DataFrame,
    cells: pd.DataFrame,
    z95: np.ndarray,
    z169: np.ndarray,
    e95: np.ndarray,
    e154_axis: np.ndarray,
    e101_axis: np.ndarray,
    mixmin_axis: np.ndarray,
    bad_names: list[str],
    bad_basis: np.ndarray,
) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    rows: list[dict[str, Any]] = []
    preds: dict[str, np.ndarray] = {}
    for spec in specs:
        policy = str(spec["policy"])
        keep_values = np.asarray(spec["keep_values"], dtype=np.float64)
        keep_matrix = keep_matrix_from_values(cells, keep_values)
        rec, pred = e172.score_variant(
            policy,
            keep_matrix,
            sample,
            cells,
            z95,
            z169,
            e95,
            e154_axis,
            e101_axis,
            mixmin_axis,
            bad_names,
            bad_basis,
            int(np.sum(np.abs(keep_values - 1.0) > EPS)),
        )
        move = logit(pred) - z95
        rec["mean_keep_selected"] = float(np.mean(keep_values[cells["expected_delta_visible_mean"].gt(0).to_numpy()]))
        rec["n_keep_changed_from_e172"] = int(np.sum(np.abs(keep_values - base_keep_values(cells, 0.25)) > EPS))
        rec["cos_e172_axis"] = cosine(move, (logit(load_prob(E172_FILE, sample)) - z95).reshape(-1))
        rows.append(rec)
        preds[policy] = pred
    return pd.DataFrame(rows), preds


def run() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    e95 = load_prob(E95_FILE, sample)
    e169 = load_prob(E169_FILE, sample)
    e172_prob = load_prob(E172_FILE, sample)
    e154 = load_prob(E154_FILE, sample)
    e101 = load_prob(E101_FILE, sample)
    mixmin = load_prob(MIXMIN_FILE, sample)
    z95 = logit(e95)
    z169 = logit(e169)
    e154_axis = (logit(e154) - z95).reshape(-1)
    e101_axis = (logit(e101) - z95).reshape(-1)
    mixmin_axis = (logit(mixmin) - z95).reshape(-1)
    bad_names, bad_basis = e165.bad_axes(sample, z95)
    cells = e171.build_cells()
    rollback_cells = rollback_cell_table(cells, e172_prob, e169)
    specs = build_specs(cells, rollback_cells)
    scan, preds = score_specs(
        specs,
        sample,
        cells,
        z95,
        z169,
        e95,
        e154_axis,
        e101_axis,
        mixmin_axis,
        bad_names,
        bad_basis,
    )
    e172_row = scan[scan["policy"].eq("baseline_e172_keep0p25")].iloc[0]
    scan["delta_focus_vs_e172"] = scan["expected_delta_focus_mean"] - float(e172_row["expected_delta_focus_mean"])
    scan["delta_visible_p95_vs_e172"] = scan["p95_delta_norm_visible_mean"] - float(e172_row["p95_delta_norm_visible_mean"])
    scan["delta_visible_worse_e101_vs_e172"] = scan["worse_than_e101_norm_visible_mean"] - float(
        e172_row["worse_than_e101_norm_visible_mean"]
    )
    scan["broad_retained"] = (
        scan["moved_cells"].ge(900)
        & scan["moved_rows"].ge(190)
        & scan["cells_to_flip_expected"].ge(30)
        & scan["top1_over_abs_expected"].le(0.055)
    )
    scan["visible_tail_guard"] = (
        scan["p95_delta_norm_visible_mean"].le(-1.0e-5)
        & scan["worse_than_e101_norm_visible_mean"].le(0.002)
        & scan["mean_delta_visible_mean"].le(-4.0e-5)
    )
    scan["geometry_guard"] = (
        scan["bad_span_energy"].le(0.285)
        & scan["max_bad_cos"].le(0.20)
        & scan["q2s3_share_vs_e95"].le(0.34)
        & scan["mean_abs_logit_move_vs_e95"].le(0.0010)
    )
    scan["body_recovered"] = scan["delta_focus_vs_e172"].le(-2.0e-6)
    scan["e174_gate"] = scan["broad_retained"] & scan["visible_tail_guard"] & scan["geometry_guard"] & scan["body_recovered"]
    scan["pareto_score"] = (
        scan["expected_delta_focus_mean"]
        + np.maximum(scan["p95_delta_norm_visible_mean"] + 1.0e-5, 0.0) * 5.0
        + np.maximum(scan["worse_than_e101_norm_visible_mean"] - 0.002, 0.0) * 1.0e-4
        + np.maximum(scan["bad_span_energy"] - 0.285, 0.0) * 1.0e-4
    )
    scan = scan.sort_values(
        ["e174_gate", "pareto_score", "expected_delta_focus_mean", "p95_delta_norm_visible_mean"],
        ascending=[False, True, True, True],
    ).reset_index(drop=True)
    shortlist = scan[scan["e174_gate"].fillna(False)].copy()
    direct_effect = pd.DataFrame()
    if not shortlist.empty:
        best_policy = str(shortlist.iloc[0]["policy"])
        shortlist.loc[shortlist["policy"].eq(best_policy), "materialized_file"] = materialize(
            sample, preds[best_policy], best_policy
        )
        direct_effect = direct_reopen_effect_by_target(sample, preds[best_policy], e172_prob)

    scan.to_csv(SCAN_OUT, index=False)
    shortlist.to_csv(SHORTLIST_OUT, index=False)
    rollback_cells.to_csv(ROLLBACK_CELLS_OUT, index=False)
    write_report(scan, shortlist, rollback_cells, direct_effect)
    print(SCAN_OUT)
    print(SHORTLIST_OUT)
    print(ROLLBACK_CELLS_OUT)
    print(REPORT_OUT)
    if not shortlist.empty and "materialized_file" in shortlist:
        for file_name in shortlist["materialized_file"].dropna().astype(str).tolist():
            print(OUT / file_name)


def direct_reopen_effect_by_target(
    sample: pd.DataFrame,
    p_new: np.ndarray,
    p_base: np.ndarray,
) -> pd.DataFrame:
    priors = e172.e162_priors(sample)
    moved = np.abs(p_new - p_base) > EPS
    row_idx, target_idx = np.where(moved)
    if len(row_idx) == 0:
        return pd.DataFrame()
    dy1, dy0 = e162.hard_loss_deltas(p_new[row_idx, target_idx], p_base[row_idx, target_idx])
    py = priors["focus_mean"][row_idx, target_idx]
    expected = (py * dy1 + (1.0 - py) * dy0) / e172.N_PUBLIC_CELLS
    out = pd.DataFrame(
        {
            "target": [TARGETS[j] for j in target_idx],
            "delta_focus_vs_e172": expected,
            "abs_swing_vs_e172": np.abs(dy1 - dy0) / e172.N_PUBLIC_CELLS,
            "support_label": np.where(dy1 < dy0, 1, 0),
            "support_prob_focus": np.where(dy1 < dy0, py, 1.0 - py),
        }
    )
    return (
        out.groupby("target")
        .agg(
            moved_cells=("target", "size"),
            delta_focus_vs_e172=("delta_focus_vs_e172", "sum"),
            total_abs_swing=("abs_swing_vs_e172", "sum"),
            mean_support_prob_focus=("support_prob_focus", "mean"),
        )
        .reset_index()
        .sort_values("delta_focus_vs_e172")
    )


def write_report(
    scan: pd.DataFrame,
    shortlist: pd.DataFrame,
    rollback_cells: pd.DataFrame,
    direct_effect: pd.DataFrame,
) -> None:
    cols = [
        "policy",
        "e174_gate",
        "expected_delta_focus_mean",
        "delta_focus_vs_e172",
        "mean_delta_visible_mean",
        "p95_delta_norm_visible_mean",
        "worse_than_e101_norm_visible_mean",
        "delta_visible_p95_vs_e172",
        "moved_cells",
        "cells_to_flip_expected",
        "top1_over_abs_expected",
        "bad_span_energy",
        "max_bad_axis",
        "max_bad_cos",
        "q2s3_share_vs_e95",
        "mean_keep_selected",
        "n_keep_changed_from_e172",
        "materialized_file",
    ]
    rb_summary = (
        rollback_cells[rollback_cells["rollback_selected_e172"]]
        .groupby("target")
        .agg(
            n_cells=("target", "size"),
            rollback_focus_cost=("rollback_delta_focus_mean", "sum"),
            rollback_visible_delta=("rollback_delta_visible_mean", "sum"),
            mean_safe_density=("all_safe_density", "mean"),
            e72_active_rate=("e72_active", "mean"),
        )
        .reset_index()
        .sort_values("rollback_focus_cost", ascending=False)
    )
    report = f"""# E174 E172 Rollback Overcorrection Probe

## Question

E173 shows E172 repairs visible/flank tail risk, but E172-vs-E169 rollback costs
focus-prior edge, especially in Q2/S2. Is keep=0.25 overconservative, or is the
cost necessary to keep the visible-tail guard closed?

## Cell-Prior Reopen View By Target

This table uses E171 cell priors on all E172 visible-positive rollback cells.
Positive values mean E172 lost focus-prior edge versus E169 on that subset;
negative values mean the rollback protected that target under the cell-prior
view. The gate below uses the stricter E162 focus-prior score.

{md_table(rb_summary, [
    "target",
    "n_cells",
    "rollback_focus_cost",
    "rollback_visible_delta",
    "mean_safe_density",
    "e72_active_rate",
])}

## Scan Summary

- variants scored: `{len(scan)}`.
- E174 gate variants: `{int(scan['e174_gate'].sum())}`.
- materialized files: `{int(shortlist['materialized_file'].notna().sum()) if not shortlist.empty and 'materialized_file' in shortlist else 0}`.

## Materialized Candidate Direct Effect Vs E172

{md_table(direct_effect, [
    "target",
    "moved_cells",
    "delta_focus_vs_e172",
    "total_abs_swing",
    "mean_support_prob_focus",
])}

## Top Rows

{md_table(scan.head(30), cols, n=30)}

## E174-Gate Shortlist

{md_table(shortlist, cols, n=20)}

## Interpretation

- If the shortlist is empty, E172's conservative tail rollback is necessary
  under current public-free priors; do not reopen Q2/S2 before public feedback.
- If a shortlist exists, E172 was tail-safe but slightly overconservative. The
  materialized file is a Pareto contrast: it should only replace E172 if the
  recovered focus edge is worth spending some visible-tail margin.
- This is still a pre-public proxy. Public feedback must be decoded by E173 or a
  follow-up decoder before any same-family keep-factor tuning.
"""
    REPORT_OUT.write_text(report)


if __name__ == "__main__":
    run()
