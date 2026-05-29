#!/usr/bin/env python3
"""E176: E174 component ablation probe.

E174 is the sharpest current broad expected-score candidate, but it spends more
Q2/S3 and bad-axis margin than E172. This experiment asks whether any obvious
component of E174 can be damped back toward E172 while preserving nearly all of
E174's focus-prior edge.

No model is trained. A submission is materialized only if a component ablation is
near-E174 in focus edge and strictly improves a risk axis.
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
import e165_broad_edge_bad_axis_geometry as e165  # noqa: E402
import e166_broad_survivor_scale_probe as e166  # noqa: E402
import e171_e169_critical_cell_prior_audit as e171  # noqa: E402
import e172_e169_critical_tail_rollback_probe as e172  # noqa: E402
import e174_e172_rollback_overcorrection_probe as e174  # noqa: E402


E95_FILE = "submission_e95_hardtail_541e3973.csv"
E169_FILE = "submission_e169_ctx_veto_c5e806e3.csv"
E172_FILE = "submission_e172_vis_pos_all_keep0p25_d90f4407.csv"
E174_FILE = "submission_e174_ro_fc_top75_to1p0_95638e73.csv"
E154_FILE = "submission_e154_s3repair_9f2e2e73.csv"
E101_FILE = "submission_e101_q2s3tail_177569bc.csv"
MIXMIN_FILE = "submission_mixmin_0c916bb4.csv"

SCAN_OUT = OUT / "e176_e174_component_ablation_probe_scan.csv"
SHORTLIST_OUT = OUT / "e176_e174_component_ablation_probe_shortlist.csv"
COMPONENTS_OUT = OUT / "e176_e174_component_ablation_probe_components.csv"
DIRECT_OUT = OUT / "e176_e174_component_ablation_probe_direct_effect.csv"
REPORT_OUT = OUT / "e176_e174_component_ablation_probe_report.md"

EPS = 1.0e-12


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 40, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in frame.columns if cols is None or c in cols]]
    return e138.md_table(view.head(n), floatfmt)


def load_prob(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    return e166.load_prob_path(OUT / file_name, sample)


def base_e174_keep_values(cells: pd.DataFrame, rollback_cells: pd.DataFrame) -> np.ndarray:
    keep_values = e174.base_keep_values(cells, 0.25)
    reopened = rollback_cells["rollback_selected_e172"].to_numpy() & rollback_cells["rollback_focus_cost_rank"].le(75).to_numpy()
    keep_values[reopened] = 1.0
    return keep_values


def reopened_mask(rollback_cells: pd.DataFrame) -> np.ndarray:
    return rollback_cells["rollback_selected_e172"].to_numpy() & rollback_cells["rollback_focus_cost_rank"].le(75).to_numpy()


def spec_from_keep(policy: str, keep_values: np.ndarray) -> dict[str, Any]:
    return {"policy": policy, "keep_values": keep_values.copy()}


def build_specs(cells: pd.DataFrame, rollback_cells: pd.DataFrame) -> list[dict[str, Any]]:
    e172_keep = e174.base_keep_values(cells, 0.25)
    e174_keep = base_e174_keep_values(cells, rollback_cells)
    reopened = reopened_mask(rollback_cells)
    target = rollback_cells["target"].astype(str)
    safe = rollback_cells["all_safe_density"].fillna(0.0).to_numpy(dtype=np.float64)
    e72_active = rollback_cells["e72_active"].fillna(False).astype(bool).to_numpy()
    context = rollback_cells["context_type"].astype(str)
    support = rollback_cells["rollback_support_prob_focus"].to_numpy(dtype=np.float64)
    swing_rank = rollback_cells.loc[reopened, "rollback_abs_swing"].rank(method="first", ascending=False)
    swing_rank_full = pd.Series(np.inf, index=rollback_cells.index, dtype=float)
    swing_rank_full.loc[rollback_cells.index[reopened]] = swing_rank
    swing_rank_full = swing_rank_full.to_numpy(dtype=float)

    specs: list[dict[str, Any]] = [
        spec_from_keep("baseline_e172", e172_keep),
        spec_from_keep("baseline_e174", e174_keep),
        spec_from_keep("baseline_e169", np.ones(len(cells), dtype=np.float64)),
    ]

    for keep in [0.50, 0.65, 0.75, 0.85]:
        kv = e174_keep.copy()
        kv[reopened] = keep
        specs.append(spec_from_keep(f"dampen_all_reopened_to{str(keep).replace('.', 'p')}", kv))

    masks: list[tuple[str, np.ndarray]] = []
    for name, targets in [
        ("q2", ["Q2"]),
        ("s3", ["S3"]),
        ("s2", ["S2"]),
        ("s1", ["S1"]),
        ("q2s3", ["Q2", "S3"]),
        ("q2s2", ["Q2", "S2"]),
        ("s3s2", ["S3", "S2"]),
        ("q2s3s2", ["Q2", "S3", "S2"]),
        ("q2s3s2s1", ["Q2", "S3", "S2", "S1"]),
        ("q_targets", ["Q1", "Q2", "Q3"]),
        ("s_targets", ["S1", "S2", "S3", "S4"]),
    ]:
        masks.append((name, reopened & target.isin(targets).to_numpy()))

    masks.extend(
        [
            ("between", reopened & context.eq("between_train_runs").to_numpy()),
            ("after", reopened & context.eq("after_train_run").to_numpy()),
            ("e72_active", reopened & e72_active),
            ("not_e72", reopened & ~e72_active),
            ("safe_low_le0p20", reopened & (safe <= 0.20)),
            ("safe_high_gt0p40", reopened & (safe > 0.40)),
            ("support_low_lt0p50", reopened & (support < 0.50)),
            ("support_high_ge0p70", reopened & (support >= 0.70)),
        ]
    )
    for n in [5, 10, 20, 40]:
        masks.append((f"top_swing{n}", reopened & (swing_rank_full <= n)))
        masks.append((f"not_top_swing{n}", reopened & (swing_rank_full > n)))
    for n in [25, 50]:
        masks.append((f"top_focus{n}", reopened & rollback_cells["rollback_focus_cost_rank"].le(n).to_numpy()))
        masks.append((f"not_top_focus{n}", reopened & rollback_cells["rollback_focus_cost_rank"].gt(n).to_numpy()))

    seen: set[tuple[str, float, str]] = set()
    for name, mask in masks:
        if int(mask.sum()) == 0:
            continue
        for keep in [0.25, 0.50, 0.65, 0.75]:
            key = (name, keep, "dampen")
            if key not in seen:
                seen.add(key)
                kv = e174_keep.copy()
                kv[mask] = keep
                specs.append(spec_from_keep(f"ablate_{name}_to{str(keep).replace('.', 'p')}", kv))
        key = (name, 1.0, "only")
        if key not in seen:
            seen.add(key)
            kv = e172_keep.copy()
            kv[mask] = 1.0
            specs.append(spec_from_keep(f"only_{name}_reopened", kv))
    return specs


def component_table(rollback_cells: pd.DataFrame) -> pd.DataFrame:
    reopened = rollback_cells[reopened_mask(rollback_cells)].copy()
    reopened["swing_rank_reopened"] = reopened["rollback_abs_swing"].rank(method="first", ascending=False).astype(int)
    groups: list[pd.DataFrame] = []
    for kind, cols in [
        ("target", ["target"]),
        ("target_group", ["target_group"]),
        ("context_type", ["context_type"]),
        ("e72_active", ["e72_active"]),
        ("safe_low", ["safe_low"]),
        ("support_low", ["support_low"]),
        ("target_context", ["target", "context_type"]),
    ]:
        work = reopened.copy()
        if "safe_low" in cols:
            work["safe_low"] = work["all_safe_density"].le(0.20)
        if "support_low" in cols:
            work["support_low"] = work["rollback_support_prob_focus"].lt(0.50)
        one = (
            work.groupby(cols, dropna=False)
            .agg(
                n_cells=("target", "size"),
                n_rows=("sub_idx", "nunique"),
                focus_cost_e172_to_e169=("rollback_delta_focus_mean", "sum"),
                visible_delta_e172_to_e169=("rollback_delta_visible_mean", "sum"),
                abs_swing=("rollback_abs_swing", "sum"),
                top_swing=("rollback_abs_swing", "max"),
                mean_support_focus=("rollback_support_prob_focus", "mean"),
                mean_safe_density=("all_safe_density", "mean"),
                e72_active_rate=("e72_active", "mean"),
            )
            .reset_index()
        )
        one.insert(0, "group_kind", kind)
        one["group"] = one[cols].astype(str).agg(":".join, axis=1)
        groups.append(one)
    return pd.concat(groups, ignore_index=True, sort=False).sort_values(
        ["focus_cost_e172_to_e169", "n_cells"], ascending=[False, False]
    )


def materialize(sample: pd.DataFrame, pred: np.ndarray, policy: str) -> str:
    digest = hashlib.sha1(np.round(pred, 10).tobytes()).hexdigest()[:8]
    safe = policy.replace("ablate_", "abl_").replace("reopened", "rop").replace("dampen_", "dmp_")
    safe = "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in safe)[:80]
    file_name = f"submission_e176_{safe}_{digest}.csv"
    sub = sample[KEYS].copy()
    sub[TARGETS] = pred
    sub.to_csv(OUT / file_name, index=False)
    return file_name


def direct_effect(
    name: str,
    p_new: np.ndarray,
    p_base: np.ndarray,
    sample: pd.DataFrame,
) -> pd.DataFrame:
    priors = e172.e162_priors(sample)
    moved = np.abs(p_new - p_base) > EPS
    row_idx, target_idx = np.where(moved)
    if len(row_idx) == 0:
        return pd.DataFrame()
    dy1, dy0 = e162.hard_loss_deltas(p_new[row_idx, target_idx], p_base[row_idx, target_idx])
    dy1_s = dy1 / e172.N_PUBLIC_CELLS
    dy0_s = dy0 / e172.N_PUBLIC_CELLS
    py = priors["focus_mean"][row_idx, target_idx]
    expected = py * dy1_s + (1.0 - py) * dy0_s
    out = pd.DataFrame(
        {
            "pair": name,
            "target": [TARGETS[j] for j in target_idx],
            "expected_delta_focus_mean": expected,
            "swing": np.abs(dy1_s - dy0_s),
            "support_label": np.where(dy1_s < dy0_s, 1, 0),
            "support_prob_focus": np.where(dy1_s < dy0_s, py, 1.0 - py),
            "sub_idx": row_idx,
        }
    )
    return (
        out.groupby(["pair", "target"])
        .agg(
            n_cells=("target", "size"),
            n_rows=("sub_idx", "nunique"),
            expected_delta_focus_mean=("expected_delta_focus_mean", "sum"),
            swing_sum=("swing", "sum"),
            mean_support_prob_focus=("support_prob_focus", "mean"),
        )
        .reset_index()
        .sort_values(["pair", "expected_delta_focus_mean"])
    )


def score_all(sample: pd.DataFrame, cells: pd.DataFrame, specs: list[dict[str, Any]]) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    e95 = load_prob(E95_FILE, sample)
    e169 = load_prob(E169_FILE, sample)
    e154 = load_prob(E154_FILE, sample)
    e101 = load_prob(E101_FILE, sample)
    mixmin = load_prob(MIXMIN_FILE, sample)
    z95 = logit(e95)
    z169 = logit(e169)
    e154_axis = (logit(e154) - z95).reshape(-1)
    e101_axis = (logit(e101) - z95).reshape(-1)
    mixmin_axis = (logit(mixmin) - z95).reshape(-1)
    bad_names, bad_basis = e165.bad_axes(sample, z95)
    return e174.score_specs(
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


def annotate_scan(scan: pd.DataFrame) -> pd.DataFrame:
    e172_row = scan[scan["policy"].eq("baseline_e172")].iloc[0]
    e174_row = scan[scan["policy"].eq("baseline_e174")].iloc[0]
    scan = scan.copy()
    scan["delta_focus_vs_e172"] = scan["expected_delta_focus_mean"] - float(e172_row["expected_delta_focus_mean"])
    scan["delta_focus_vs_e174"] = scan["expected_delta_focus_mean"] - float(e174_row["expected_delta_focus_mean"])
    for col in [
        "p95_delta_norm_visible_mean",
        "worse_than_e101_norm_visible_mean",
        "bad_span_energy",
        "max_bad_cos",
        "q2s3_share_vs_e95",
        "mean_abs_logit_move_vs_e95",
    ]:
        scan[f"delta_{col}_vs_e174"] = scan[col] - float(e174_row[col])
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
    scan["material_vs_e172"] = scan["delta_focus_vs_e172"].le(-8.0e-6)
    scan["near_e174_edge"] = scan["delta_focus_vs_e174"].le(2.0e-6)
    scan["risk_reduced_vs_e174"] = (
        scan["delta_p95_delta_norm_visible_mean_vs_e174"].le(-1.0e-6)
        | scan["delta_worse_than_e101_norm_visible_mean_vs_e174"].le(-5.0e-5)
        | scan["delta_bad_span_energy_vs_e174"].le(-0.005)
        | scan["delta_max_bad_cos_vs_e174"].le(-0.005)
        | scan["delta_q2s3_share_vs_e95_vs_e174"].le(-0.005)
    )
    scan["e176_gate"] = (
        ~scan["policy"].eq("baseline_e174")
        & scan["broad_retained"]
        & scan["visible_tail_guard"]
        & scan["geometry_guard"]
        & scan["material_vs_e172"]
        & scan["near_e174_edge"]
        & scan["risk_reduced_vs_e174"]
    )
    scan["dominance_score"] = (
        scan["expected_delta_focus_mean"]
        + np.maximum(scan["p95_delta_norm_visible_mean"] + 1.0e-5, 0.0) * 5.0
        + np.maximum(scan["q2s3_share_vs_e95"] - 0.335, 0.0) * 1.0e-4
        + np.maximum(scan["max_bad_cos"] - 0.16, 0.0) * 1.0e-4
        + np.maximum(scan["bad_span_energy"] - 0.260, 0.0) * 1.0e-4
    )
    return scan.sort_values(
        ["e176_gate", "dominance_score", "expected_delta_focus_mean", "p95_delta_norm_visible_mean"],
        ascending=[False, True, True, True],
    ).reset_index(drop=True)


def write_report(scan: pd.DataFrame, shortlist: pd.DataFrame, components: pd.DataFrame, direct: pd.DataFrame) -> None:
    cols = [
        "policy",
        "e176_gate",
        "expected_delta_focus_mean",
        "delta_focus_vs_e174",
        "delta_focus_vs_e172",
        "mean_delta_visible_mean",
        "p95_delta_norm_visible_mean",
        "delta_p95_delta_norm_visible_mean_vs_e174",
        "worse_than_e101_norm_visible_mean",
        "bad_span_energy",
        "max_bad_cos",
        "q2s3_share_vs_e95",
        "delta_q2s3_share_vs_e95_vs_e174",
        "moved_cells",
        "cells_to_flip_expected",
        "top1_over_abs_expected",
        "n_keep_changed_from_e172",
        "materialized_file",
    ]
    component_cols = [
        "group_kind",
        "group",
        "n_cells",
        "focus_cost_e172_to_e169",
        "visible_delta_e172_to_e169",
        "abs_swing",
        "mean_support_focus",
        "mean_safe_density",
        "e72_active_rate",
    ]
    report = f"""# E176 E174 Component Ablation Probe

## Question

E174 is the highest-upside broad expected-score candidate, but it spends more
Q2/S3 and bad-axis margin than E172. Can any obvious E174 component be damped
back toward E172 while keeping near-E174 focus edge?

## Reopened Component Anatomy

This table summarizes the `75` cells that E174 reopens relative to E172. Positive
`focus_cost_e172_to_e169` means E172 gave up focus-prior edge on that component,
so reopening it is locally beneficial under the E162 focus prior.

{md_table(components, component_cols, n=30)}

## Scan Summary

- variants scored: `{len(scan)}`.
- E176 gate variants: `{int(scan['e176_gate'].sum())}`.
- materialized files: `{int(shortlist['materialized_file'].notna().sum()) if not shortlist.empty and 'materialized_file' in shortlist else 0}`.

## Top Rows

{md_table(scan.head(35), cols, n=35)}

## E176-Gate Shortlist

{md_table(shortlist, cols, n=25)}

## Materialized Direct Effect

{md_table(direct, [
    "pair",
    "target",
    "n_cells",
    "n_rows",
    "expected_delta_focus_mean",
    "swing_sum",
    "mean_support_prob_focus",
], n=40)}

## Interpretation

- If E176 gate is empty, the obvious Q2/S3/S2/S1/context/risk ablations do not
  dominate E174. E174 remains the sharpest expected-score file and E172 remains
  the safer contrast.
- If E176 gate materializes a file, that file is a safer E174 sibling only if it
  stays within `2e-6` of E174 focus edge while reducing a risk axis. It should
  still be decoded through the E175 band logic because it is same-family.
- This does not use public feedback. It is an anti-autopilot check against
  submitting E174 when a simple component-damped version already dominates it.
"""
    REPORT_OUT.write_text(report)


def run() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    cells = e171.build_cells()
    e172_prob = load_prob(E172_FILE, sample)
    e169_prob = load_prob(E169_FILE, sample)
    e174_prob = load_prob(E174_FILE, sample)
    rollback_cells = e174.rollback_cell_table(cells, e172_prob, e169_prob)
    specs = build_specs(cells, rollback_cells)
    scan, preds = score_all(sample, cells, specs)
    scan = annotate_scan(scan)
    components = component_table(rollback_cells)
    shortlist = scan[scan["e176_gate"].fillna(False)].copy()
    direct = pd.DataFrame()
    if not shortlist.empty:
        best_policy = str(shortlist.iloc[0]["policy"])
        shortlist.loc[shortlist["policy"].eq(best_policy), "materialized_file"] = materialize(
            sample, preds[best_policy], best_policy
        )
        direct = pd.concat(
            [
                direct_effect(f"{best_policy}_vs_e174", preds[best_policy], e174_prob, sample),
                direct_effect(f"{best_policy}_vs_e172", preds[best_policy], e172_prob, sample),
            ],
            ignore_index=True,
        )

    scan.to_csv(SCAN_OUT, index=False)
    shortlist.to_csv(SHORTLIST_OUT, index=False)
    components.to_csv(COMPONENTS_OUT, index=False)
    direct.to_csv(DIRECT_OUT, index=False)
    write_report(scan, shortlist, components, direct)
    print(SCAN_OUT)
    print(SHORTLIST_OUT)
    print(COMPONENTS_OUT)
    print(DIRECT_OUT)
    print(REPORT_OUT)
    if not shortlist.empty and "materialized_file" in shortlist:
        for file_name in shortlist["materialized_file"].dropna().astype(str).tolist():
            print(OUT / file_name)


if __name__ == "__main__":
    run()
