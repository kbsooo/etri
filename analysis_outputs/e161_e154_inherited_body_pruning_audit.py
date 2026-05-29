#!/usr/bin/env python3
"""E161: can E154 be improved by pruning attribution-risk cells?

E159 says E154 loss-side blame is often inherited E144 body, not just E154's
added body. The tempting follow-up is to cut high-risk inherited cells. This
probe tries that directly without public labels:

1. rank E154-vs-E95 cells by public-free expected LogLoss risk;
2. revert top-risk cells either to E144 or all the way to E95;
3. rescore with the same E154/E155 health gates;
4. only materialize if pruning beats E154 locally while reducing public-free
   expected risk.

The kill question is whether "the body has removable risky cells" is a real
next-submission mechanism or another branch-collinear micro-control.
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
import e83_q2s3_energy_structural_gate_scan as e83  # noqa: E402
import e89_e86_e72_decontamination_scan as e89mod  # noqa: E402
import e130_tail_density_synthesis_probe as e130  # noqa: E402
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402
import e153_gate_intersection_failure_atlas as e153  # noqa: E402
import e155_e154_branch_body_ablation as e155  # noqa: E402


SEGMENTS_IN = OUT / "e159_e154_public_outcome_attribution_cells.csv"
SCAN_OUT = OUT / "e161_e154_inherited_body_pruning_scan.csv"
SUMMARY_OUT = OUT / "e161_e154_inherited_body_pruning_summary.csv"
FRONTIER_OUT = OUT / "e161_e154_inherited_body_pruning_frontier.csv"
REPORT_OUT = OUT / "e161_e154_inherited_body_pruning_report.md"
SUBMISSION_PREFIX = "submission_e161_pruned_e154"

EPS = 1.0e-6
PRIOR_VIEWS = ["global", "subject", "nearest_hard085", "focus_mean"]
COMPONENT_SCOPES = ["all", "inherited", "added", "adjustment", "extra"]
TARGET_SCOPES = ["all", "Q1", "Q3", "S2", "S3", "S4"]
TOP_COUNTS = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
MODES = ["to_e144", "to_e95"]
PUBLIC_READABLE_GUARD = 2.0e-6


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    aa = np.asarray(a, dtype=np.float64).reshape(-1)
    bb = np.asarray(b, dtype=np.float64).reshape(-1)
    denom = float(np.linalg.norm(aa) * np.linalg.norm(bb))
    if denom <= 1.0e-15:
        return 0.0
    return float(np.dot(aa, bb) / denom)


def load_aligned(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    return clip_prob(load_sub(file_name, sample)[TARGETS].to_numpy(dtype=np.float64))


def hard_expected_delta(p_new: np.ndarray, p_base: np.ndarray, p_y1: np.ndarray) -> np.ndarray:
    p_new = clip_prob(p_new)
    p_base = clip_prob(p_base)
    p_y1 = np.asarray(p_y1, dtype=np.float64)
    delta_y1 = -np.log(p_new) + np.log(p_base)
    delta_y0 = -np.log(1.0 - p_new) + np.log(1.0 - p_base)
    return p_y1 * delta_y1 + (1.0 - p_y1) * delta_y0


def add_pred(
    rows: list[dict[str, Any]],
    preds: list[np.ndarray],
    seen: dict[str, int],
    pred: np.ndarray,
    rec: dict[str, Any],
) -> None:
    key = e138.pred_key(pred)
    if key in seen:
        pred_index = seen[key]
    else:
        pred_index = len(preds)
        seen[key] = pred_index
        preds.append(pred)
    rows.append({"pred_index": pred_index, "base_index": 0, "tag": e83.stable_tag(pred, "e161_"), **rec})


def build_cell_table(segments: pd.DataFrame, n_rows: int) -> pd.DataFrame:
    prior_cols = {
        "global": "p_y1_global",
        "subject": "p_y1_subject",
        "nearest_hard085": "p_y1_nearest_hard085",
    }
    for name, col in prior_cols.items():
        if col not in segments:
            raise RuntimeError(f"Missing prior column {col} in {SEGMENTS_IN}")

    rows: list[dict[str, Any]] = []
    grouped = segments.groupby(["sub_idx", "target_idx", "target"], sort=False)
    for (sub_idx, target_idx, target), group in grouped:
        p95 = float(group["p_e95"].iloc[0])
        p144 = float(group["p_e144"].iloc[0])
        p154 = float(group["p_e154"].iloc[0])
        components = set(str(v) for v in group["component"].unique())
        rec: dict[str, Any] = {
            "sub_idx": int(sub_idx),
            "target_idx": int(target_idx),
            "flat_idx": int(sub_idx) * len(TARGETS) + int(target_idx),
            "target": str(target),
            "p_e95": p95,
            "p_e144": p144,
            "p_e154": p154,
            "has_inherited": "inherited_e144_body" in components,
            "has_adjustment": "e154_adjustment_on_e144_body" in components,
            "has_extra": "e154_extra_body" in components,
            "component_label": "+".join(sorted(components)),
            "abs_logit_e154_e95": abs(float(logit(np.asarray([p154]))[0] - logit(np.asarray([p95]))[0])),
        }
        for view, col in prior_cols.items():
            p_y1 = float(group[col].iloc[0])
            rec[f"p_y1_{view}"] = p_y1
            rec[f"expected_delta_{view}"] = float(
                hard_expected_delta(np.asarray([p154]), np.asarray([p95]), np.asarray([p_y1]))[0]
            )
        rec["expected_delta_focus_mean"] = float(
            np.mean([rec["expected_delta_global"], rec["expected_delta_subject"], rec["expected_delta_nearest_hard085"]])
        )
        rec["support_prob_focus_mean"] = float(
            np.mean(
                [
                    group["support_probability_global"].iloc[0],
                    group["support_probability_subject"].iloc[0],
                    group["support_probability_nearest_hard085"].iloc[0],
                ]
            )
        )
        rows.append(rec)
    cells = pd.DataFrame(rows)
    expected = int(segments["unique_cell_count"].iloc[0])
    if len(cells) != expected:
        raise RuntimeError(f"cell table mismatch: {len(cells)} vs expected {expected}")
    if cells["sub_idx"].max() >= n_rows:
        raise RuntimeError("cell table row index exceeds sample size")
    return cells


def component_mask(cells: pd.DataFrame, scope: str) -> pd.Series:
    if scope == "all":
        return pd.Series(True, index=cells.index)
    if scope == "inherited":
        return cells["has_inherited"].astype(bool)
    if scope == "added":
        return cells["has_adjustment"].astype(bool) | cells["has_extra"].astype(bool)
    if scope == "adjustment":
        return cells["has_adjustment"].astype(bool)
    if scope == "extra":
        return cells["has_extra"].astype(bool)
    raise ValueError(scope)


def target_mask(cells: pd.DataFrame, scope: str) -> pd.Series:
    if scope == "all":
        return pd.Series(True, index=cells.index)
    return cells["target"].eq(scope)


def movement_metrics(pred: np.ndarray, refs: dict[str, np.ndarray]) -> dict[str, Any]:
    move95 = logit(pred) - logit(refs["e95"])
    move154 = logit(pred) - logit(refs["e154"])
    move144 = logit(pred) - logit(refs["e144"])
    e154_axis = logit(refs["e154"]) - logit(refs["e95"])
    e144_axis = logit(refs["e144"]) - logit(refs["e95"])
    active = np.abs(move95) > 1.0e-10
    target_l1 = np.abs(move95).sum(axis=0)
    total = float(target_l1.sum())
    return {
        "changed_cells_vs_e95": int(active.sum()),
        "changed_rows_vs_e95": int(active.any(axis=1).sum()),
        "changed_cells_vs_e154": int((np.abs(move154) > 1.0e-10).sum()),
        "changed_cells_vs_e144": int((np.abs(move144) > 1.0e-10).sum()),
        "l1_vs_e95": total,
        "l1_vs_e154": float(np.abs(move154).sum()),
        "cos_vs_e154_axis": cosine(move95, e154_axis),
        "cos_vs_e144_axis": cosine(move95, e144_axis),
        **{
            f"target_share_{target}": float(target_l1[idx] / total) if total > 0 else 0.0
            for idx, target in enumerate(TARGETS)
        },
    }


def expected_metrics(pred: np.ndarray, refs: dict[str, np.ndarray], cells: pd.DataFrame) -> dict[str, Any]:
    out: dict[str, Any] = {}
    row_idx = cells["sub_idx"].to_numpy(dtype=int)
    target_idx = cells["target_idx"].to_numpy(dtype=int)
    p_new = pred[row_idx, target_idx]
    p_base = refs["e95"][row_idx, target_idx]
    focus_vals: list[float] = []
    for view in ["global", "subject", "nearest_hard085"]:
        p_y = cells[f"p_y1_{view}"].to_numpy(dtype=np.float64)
        val = float(hard_expected_delta(p_new, p_base, p_y).sum() / (250.0 * len(TARGETS)))
        out[f"expected_delta_{view}"] = val
        focus_vals.append(val)
    out["expected_delta_focus_mean"] = float(np.mean(focus_vals))
    return out


def build_candidates(
    sample: pd.DataFrame,
    refs: dict[str, np.ndarray],
    cells: pd.DataFrame,
) -> tuple[pd.DataFrame, list[np.ndarray]]:
    rows: list[dict[str, Any]] = []
    preds: list[np.ndarray] = []
    seen: dict[str, int] = {}

    controls = {
        "control_e95": refs["e95"],
        "control_e144": refs["e144"],
        "control_e154": refs["e154"],
        "control_e155": refs["e155"],
        "control_e157": refs["e157"],
        "control_e156": refs["e156"],
    }
    for name, pred in controls.items():
        add_pred(
            rows,
            preds,
            seen,
            pred,
            {
                "strategy": name,
                "prune_mode": "control",
                "prior_view": "",
                "component_scope": "",
                "target_scope": "",
                "top_n": 0,
                "risk_positive_pool": 0,
                "reverted_cells": 0,
                "mean_reverted_risk": np.nan,
                "max_reverted_risk": np.nan,
                **movement_metrics(pred, refs),
                **expected_metrics(pred, refs, cells),
            },
        )

    e154 = refs["e154"]
    e154_logit = logit(e154)
    e144_logit = logit(refs["e144"])
    e95_logit = logit(refs["e95"])

    seen_masks: set[tuple[str, str, str, str, int, tuple[int, ...]]] = set()
    for prior_view in PRIOR_VIEWS:
        risk_col = f"expected_delta_{prior_view}"
        for component_scope in COMPONENT_SCOPES:
            c_mask = component_mask(cells, component_scope)
            for target_scope in TARGET_SCOPES:
                t_mask = target_mask(cells, target_scope)
                pool = cells[c_mask & t_mask & cells[risk_col].gt(0.0)].copy()
                if pool.empty:
                    continue
                pool = pool.sort_values([risk_col, "abs_logit_e154_e95"], ascending=[False, False])
                for top_n in TOP_COUNTS:
                    if top_n > len(pool):
                        continue
                    chosen = pool.head(top_n).copy()
                    flat = tuple(sorted(chosen["flat_idx"].astype(int).tolist()))
                    for mode in MODES:
                        key = (prior_view, component_scope, target_scope, mode, top_n, flat)
                        if key in seen_masks:
                            continue
                        seen_masks.add(key)
                        new_logit = e154_logit.copy()
                        sub_idx = chosen["sub_idx"].to_numpy(dtype=int)
                        target_idx = chosen["target_idx"].to_numpy(dtype=int)
                        if mode == "to_e144":
                            new_logit[sub_idx, target_idx] = e144_logit[sub_idx, target_idx]
                        elif mode == "to_e95":
                            new_logit[sub_idx, target_idx] = e95_logit[sub_idx, target_idx]
                        else:
                            raise ValueError(mode)
                        pred = clip_prob(sigmoid(new_logit))
                        add_pred(
                            rows,
                            preds,
                            seen,
                            pred,
                            {
                                "strategy": "risk_prune",
                                "prune_mode": mode,
                                "prior_view": prior_view,
                                "component_scope": component_scope,
                                "target_scope": target_scope,
                                "top_n": int(top_n),
                                "risk_positive_pool": int(len(pool)),
                                "reverted_cells": int(len(chosen)),
                                "mean_reverted_risk": float(chosen[risk_col].mean()),
                                "max_reverted_risk": float(chosen[risk_col].max()),
                                **movement_metrics(pred, refs),
                                **expected_metrics(pred, refs, cells),
                            },
                        )
    return pd.DataFrame(rows), preds


def add_e161_flags(scan: pd.DataFrame) -> pd.DataFrame:
    out = scan.copy()
    controls = out[out["strategy"].astype(str).str.startswith("control_")].copy()
    def control_value(name: str, col: str) -> float:
        vals = controls.loc[controls["strategy"].eq(name), col]
        if vals.empty:
            raise RuntimeError(f"Missing control {name}")
        return float(vals.iloc[0])

    e144_all = control_value("control_e144", "all_minus_base")
    e154_all = control_value("control_e154", "all_minus_base")
    e155_all = control_value("control_e155", "all_minus_base")
    e154_expected = control_value("control_e154", "expected_delta_focus_mean")
    out = e155.add_health_flags(out, e144_all)
    out["focus_expected_delta_vs_e154"] = out["expected_delta_focus_mean"] - e154_expected
    out["local_delta_vs_e154"] = out["all_minus_base"] - e154_all
    out["local_delta_vs_e155"] = out["all_minus_base"] - e155_all
    out["public_free_safer_than_e154"] = out["focus_expected_delta_vs_e154"].lt(-1.0e-12)
    out["local_not_worse_than_e155"] = out["local_delta_vs_e155"].le(1.0e-12)
    out["beats_e154_local"] = out["local_delta_vs_e154"].lt(-1.0e-12)
    out["beats_e154_readable"] = out["local_delta_vs_e154"].lt(-PUBLIC_READABLE_GUARD)
    out["e161_control_grade"] = (
        out["strategy"].eq("risk_prune")
        & out["all_four_health"].fillna(False).astype(bool)
        & out["beats_e144_local"].fillna(False).astype(bool)
        & out["local_not_worse_than_e155"].fillna(False).astype(bool)
        & out["public_free_safer_than_e154"].fillna(False).astype(bool)
    )
    out["e161_submit"] = out["e161_control_grade"] & out["beats_e154_readable"].fillna(False).astype(bool)
    return out


def summarize(scan: pd.DataFrame) -> pd.DataFrame:
    variants = scan[scan["strategy"].eq("risk_prune")].copy()
    if variants.empty:
        return pd.DataFrame()
    rows: list[dict[str, Any]] = []
    for keys, group in variants.groupby(["prior_view", "component_scope", "target_scope", "prune_mode"], dropna=False):
        prior_view, component_scope, target_scope, prune_mode = keys
        all_four = group[group["all_four_health"].fillna(False).astype(bool)]
        control_grade = group[group["e161_control_grade"].fillna(False).astype(bool)]
        submit = group[group["e161_submit"].fillna(False).astype(bool)]
        best_local = group.sort_values("all_minus_base").head(1)
        best_safe = group.sort_values(["expected_delta_focus_mean", "all_minus_base"], ascending=[True, True]).head(1)
        rows.append(
            {
                "prior_view": str(prior_view),
                "component_scope": str(component_scope),
                "target_scope": str(target_scope),
                "prune_mode": str(prune_mode),
                "rows": int(len(group)),
                "all_four_health": int(len(all_four)),
                "control_grade": int(len(control_grade)),
                "e161_submit": int(len(submit)),
                "best_all_minus_base": float(best_local["all_minus_base"].iloc[0]) if len(best_local) else np.nan,
                "best_local_delta_vs_e154": float(best_local["local_delta_vs_e154"].iloc[0]) if len(best_local) else np.nan,
                "best_focus_expected_delta": float(best_safe["expected_delta_focus_mean"].iloc[0]) if len(best_safe) else np.nan,
                "best_focus_delta_vs_e154": float(best_safe["focus_expected_delta_vs_e154"].iloc[0]) if len(best_safe) else np.nan,
                "best_safe_all_minus_base": float(best_safe["all_minus_base"].iloc[0]) if len(best_safe) else np.nan,
                "best_safe_top_n": int(best_safe["top_n"].iloc[0]) if len(best_safe) else -1,
                "best_safe_tag": str(best_safe["tag"].iloc[0]) if len(best_safe) else "",
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["e161_submit", "control_grade", "all_four_health", "best_focus_delta_vs_e154", "best_all_minus_base"],
        ascending=[False, False, False, True, True],
    )


def frontier(scan: pd.DataFrame) -> pd.DataFrame:
    keep = [
        "strategy",
        "prune_mode",
        "prior_view",
        "component_scope",
        "target_scope",
        "top_n",
        "reverted_cells",
        "all_minus_base",
        "local_delta_vs_e154",
        "local_delta_vs_e155",
        "expected_delta_focus_mean",
        "focus_expected_delta_vs_e154",
        "all_four_health",
        "e161_control_grade",
        "e161_submit",
        "beats_e144_local",
        "beats_e154_readable",
        "public_free_safer_than_e154",
        "relaxed_structural_tol1e12",
        "budget_ok",
        "post101_ok",
        "gate_strict_actionable",
        "post101_p95_vs_e95_e101_sensor",
        "e72_plausible_gap_vs_e95",
        "changed_cells_vs_e154",
        "cos_vs_e154_axis",
        "cos_vs_e144_axis",
        "tag",
    ]
    return scan.sort_values(
        [
            "e161_submit",
            "e161_control_grade",
            "all_four_health",
            "focus_expected_delta_vs_e154",
            "all_minus_base",
        ],
        ascending=[False, False, False, True, True],
    )[[c for c in keep if c in scan.columns]].head(120)


def materialize(scan: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> Path | None:
    eligible = scan[scan["e161_submit"].fillna(False).astype(bool)].copy()
    if eligible.empty:
        return None
    chosen = eligible.sort_values(
        ["local_delta_vs_e154", "focus_expected_delta_vs_e154", "post101_p95_vs_e95_e101_sensor"],
        ascending=[True, True, True],
    ).iloc[0]
    pred = preds[int(chosen["pred_index"])]
    tag = str(chosen["tag"]).split("_")[-1]
    path = OUT / f"{SUBMISSION_PREFIX}_{tag}.csv"
    sub = sample[KEYS].copy()
    sub[TARGETS] = clip_prob(pred)
    sub.to_csv(path, index=False)
    return path


def md_table(frame: pd.DataFrame, cols: list[str], n: int = 40) -> str:
    if frame.empty:
        return "_empty_"
    keep = [c for c in cols if c in frame.columns]
    return e138.md_table(frame[keep].head(n), ".9f")


def write_report(scan: pd.DataFrame, summary: pd.DataFrame, front: pd.DataFrame, submission_path: Path | None) -> None:
    variants = scan[scan["strategy"].eq("risk_prune")]
    controls = scan[scan["strategy"].astype(str).str.startswith("control_")]
    submit_count = int(variants["e161_submit"].fillna(False).astype(bool).sum()) if len(variants) else 0
    control_grade = int(variants["e161_control_grade"].fillna(False).astype(bool).sum()) if len(variants) else 0
    all_four = int(variants["all_four_health"].fillna(False).astype(bool).sum()) if len(variants) else 0
    if submission_path is not None:
        decision = f"Materialized `{submission_path.name}` because pruning beat E154 by a readable local margin while reducing public-free expected risk."
    elif control_grade:
        decision = "No submission. Some pruned rows are safer than E154 and not worse than E155, but none beat E154 by a public-readable local margin."
    elif all_four:
        decision = "No submission. Pruning can keep all-four health, but it either gives up too much local edge or does not reduce public-free risk enough."
    else:
        decision = "No submission. Attribution-risk pruning does not preserve the all-four E154 health state."

    lines = [
        "# E161 E154 Inherited-Body Pruning Audit",
        "",
        "## Question",
        "",
        "E159 says E154 failures can be inherited-body dominated. E161 asks whether those risky cells are actually removable before public feedback, or whether pruning only creates another sub-resolution branch control.",
        "",
        "## Counts",
        "",
        f"- pruning rows: `{len(variants)}`.",
        f"- all-four rows: `{all_four}`.",
        f"- control-grade rows: `{control_grade}`.",
        f"- submission-grade rows: `{submit_count}`.",
        f"- materialized submission: `{submission_path.name if submission_path else ''}`.",
        "",
        "## Controls",
        "",
        md_table(
            controls.sort_values("all_minus_base"),
            [
                "strategy",
                "all_minus_base",
                "local_delta_vs_e154",
                "expected_delta_focus_mean",
                "focus_expected_delta_vs_e154",
                "all_four_health",
                "post101_p95_vs_e95_e101_sensor",
                "e72_plausible_gap_vs_e95",
                "changed_cells_vs_e154",
                "tag",
            ],
            20,
        ),
        "",
        "## Summary",
        "",
        md_table(summary, list(summary.columns), 60),
        "",
        "## Frontier Rows",
        "",
        md_table(front, list(front.columns), 80),
        "",
        "## Decision",
        "",
        decision,
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    refs = e130.load_refs(sample)
    refs.update(
        {
            "e144": load_aligned("submission_e144_activeboundary_d7b4b331.csv", sample),
            "e154": load_aligned("submission_e154_s3repair_9f2e2e73.csv", sample),
            "e155": load_aligned("submission_e155_bodytemp_d27e7965.csv", sample),
            "e157": load_aligned("submission_e157_lowbodypareto_bd67930d.csv", sample),
            "e156": load_aligned("submission_e156_targetaxis_757546d2.csv", sample),
        }
    )
    segments = pd.read_csv(SEGMENTS_IN, low_memory=False)
    cells = build_cell_table(segments, len(sample))
    _state, density, tail_state = e153.e152.setup_state(sample, refs)
    rows, preds = build_candidates(sample, refs, cells)

    labels, worlds, views, stress_state = e89mod.build_stress_state(sample, refs["mixmin"])
    scan = e83.score_candidate_rows(rows, preds, sample, refs["mixmin"], labels, worlds, views, stress_state)
    scan = e130.add_tail_and_veto_metrics(scan, preds, refs, density, tail_state)
    transfer_scan = scan.copy()
    transfer_scan.loc[transfer_scan["strategy"].astype(str).str.startswith("control_"), "strategy"] = "control"
    transfer = e130.post_e101_transfer_summary(sample, transfer_scan, preds, refs, tail_state)
    scan = e130.merge_transfer(scan, transfer)
    scan = add_e161_flags(scan)
    summary = summarize(scan)
    front = frontier(scan)
    submission_path = materialize(scan, preds, sample)
    scan["materialized_submission"] = False
    if submission_path is not None:
        suffix = submission_path.stem.split("_")[-1]
        scan["materialized_submission"] = scan["tag"].astype(str).str.endswith(suffix)

    scan.to_csv(SCAN_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    front.to_csv(FRONTIER_OUT, index=False)
    write_report(scan, summary, front, submission_path)

    variants = scan[scan["strategy"].eq("risk_prune")]
    print(
        {
            "rows": int(len(scan)),
            "prune_rows": int(len(variants)),
            "all_four": int(variants["all_four_health"].fillna(False).astype(bool).sum()),
            "control_grade": int(variants["e161_control_grade"].fillna(False).astype(bool).sum()),
            "e161_submit": int(variants["e161_submit"].fillna(False).astype(bool).sum()),
            "best_local_delta_vs_e154": float(variants["local_delta_vs_e154"].min()) if len(variants) else None,
            "best_focus_delta_vs_e154": float(variants["focus_expected_delta_vs_e154"].min()) if len(variants) else None,
            "submission": str(submission_path) if submission_path is not None else None,
        }
    )
    print(summary.head(20).to_string(index=False))


if __name__ == "__main__":
    main()
