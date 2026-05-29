#!/usr/bin/env python3
"""E154: can S3-only repair open E152's missing-actionable near misses?

E153 showed that almost every E152 three-of-four near miss passes relaxed,
E72-budget, and post-E101 gates, then dies on actionability. The target anatomy
said this is not Q2; it is S3 active-boundary exposure. This probe tests the
smallest repair: roll back selected S3 cells toward E95 and rescore with the
same gates.

No public labels are fitted. A submission is materialized only if a repaired
row passes relaxed/E72/post-E101/actionability, keeps material local reward,
and beats the current E144 sensor locally.
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
import e141_tail_tolerance_transfer_audit as e141  # noqa: E402
import e142_transfer_budget_clipped_decoder_probe as e142  # noqa: E402
import e153_gate_intersection_failure_atlas as e153  # noqa: E402


SCAN_OUT = OUT / "e154_s3_active_boundary_repair_scan.csv"
SUMMARY_OUT = OUT / "e154_s3_active_boundary_repair_summary.csv"
BLOCKER_OUT = OUT / "e154_s3_active_boundary_repair_blockers.csv"
FRONTIER_OUT = OUT / "e154_s3_active_boundary_repair_frontier.csv"
REPORT_OUT = OUT / "e154_s3_active_boundary_repair_report.md"
SUBMISSION_PREFIX = "submission_e154_s3repair"

EPS = 1.0e-6
MATERIAL_FLOOR = 1.0e-6
S3 = TARGETS.index("S3")
Q2 = TARGETS.index("Q2")
Q2S3 = [Q2, S3]
S_ALL = [TARGETS.index(t) for t in ["S1", "S2", "S3", "S4"]]

# Keep this scan deliberately narrow. E154 asks whether the E153 failure mode
# opens under S3 rollback at all; exhaustive amplitude search would blur that
# kill-question and is much slower than needed.
TOP_COUNTS = [1, 2, 3, 5, 8, 13, 21, 34]
KEEP_FACTORS = [0.0, 0.10, 0.25, 0.50]
FULL_KEEP_FACTORS = [0.0, 0.25, 0.50]


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


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
    rows.append({"pred_index": pred_index, "base_index": 0, "tag": e83.stable_tag(pred, "e154_"), **rec})


def bool_col(frame: pd.DataFrame, col: str) -> pd.Series:
    if col not in frame.columns:
        return pd.Series(False, index=frame.index)
    raw = frame[col]
    if raw.dtype == bool:
        return raw.fillna(False)
    return raw.astype(str).str.lower().isin({"true", "1", "yes"})


def normalize_weight(values: np.ndarray) -> np.ndarray:
    return e130.normalize_weight(np.asarray(values, dtype=np.float64).reshape(-1)).reshape(values.shape)


def ranked_masks(delta: np.ndarray, density: dict[str, np.ndarray]) -> list[dict[str, Any]]:
    active = np.abs(delta) > 1.0e-12
    s3_target = np.zeros_like(active, dtype=bool)
    s3_target[:, S3] = True
    active_s3 = active & s3_target
    if not active_s3.any():
        return []

    e101_active = np.asarray(density["e101_active"], dtype=np.float64) > 0.5
    tail_equal = np.asarray(density["tail_equal"], dtype=np.float64)
    plausible = np.asarray(density["plausible"], dtype=np.float64)
    q2s3 = np.asarray(density["q2s3"], dtype=np.float64)
    abs_delta = np.abs(delta)

    w_e101 = normalize_weight(e101_active.astype(float))
    w_tail = normalize_weight(tail_equal)
    w_plausible = normalize_weight(plausible)
    w_q2s3 = normalize_weight(q2s3)
    composite = abs_delta * (w_q2s3 + w_e101 + 0.50 * w_tail + 0.25 * w_plausible)

    masks: list[dict[str, Any]] = []
    seen: set[bytes] = set()
    base_masks = [
        ("s3_all", active_s3, "full"),
        ("s3_e101_active", active_s3 & e101_active, "full"),
        ("s3_non_e101", active_s3 & (~e101_active), "full"),
    ]
    for name, mask, ranker in base_masks:
        if not mask.any():
            continue
        key = mask.tobytes()
        if key in seen:
            continue
        seen.add(key)
        masks.append({"mask_name": name, "mask": mask, "ranker": ranker, "top_n": int(mask.sum())})

    flat_active = np.flatnonzero(active_s3.reshape(-1))
    rankers = {
        "s3_abs": abs_delta.reshape(-1),
        "s3_e101": (abs_delta * w_e101).reshape(-1),
        "s3_tail_equal": (abs_delta * w_tail).reshape(-1),
        "s3_composite": composite.reshape(-1),
    }
    for ranker, score in rankers.items():
        valid = flat_active[score[flat_active] > 0.0]
        if len(valid) == 0:
            continue
        order = valid[np.argsort(-score[valid])]
        for top_n in TOP_COUNTS:
            if top_n > len(order):
                continue
            mask = np.zeros(delta.size, dtype=bool)
            mask[order[:top_n]] = True
            mask = mask.reshape(delta.shape)
            key = mask.tobytes()
            if key in seen:
                continue
            seen.add(key)
            masks.append({"mask_name": f"top_{ranker}_{top_n}", "mask": mask, "ranker": ranker, "top_n": int(top_n)})
    return masks


def build_candidates(
    e152_scan: pd.DataFrame,
    e152_preds: list[np.ndarray],
    refs: dict[str, np.ndarray],
    density: dict[str, np.ndarray],
    sample: pd.DataFrame,
) -> tuple[pd.DataFrame, list[np.ndarray]]:
    e95 = refs["e95"]
    e95_logit = logit(e95)
    e144 = clip_prob(load_sub("submission_e144_activeboundary_d7b4b331.csv", sample)[TARGETS].to_numpy(dtype=np.float64))

    rows: list[dict[str, Any]] = []
    preds: list[np.ndarray] = []
    seen: dict[str, int] = {}
    add_pred(
        rows,
        preds,
        seen,
        e95,
        {
            "strategy": "control_e95",
            "repair_mode": "control",
            "source_tag": "e95",
            "source_variant_pos": -1,
            "source_pred_index": 0,
            "source_gate_class": "control",
            "mask_name": "none",
            "ranker": "",
            "top_n": 0,
            "keep_factor": 1.0,
            "rollback_cells": 0,
            "rollback_s3_cells": 0,
            "rollback_q2s3_cells": 0,
            "rollback_s_cells": 0,
        },
    )
    add_pred(
        rows,
        preds,
        seen,
        e144,
        {
            "strategy": "control_e144",
            "repair_mode": "control",
            "source_tag": "e144",
            "source_variant_pos": -1,
            "source_pred_index": 1,
            "source_gate_class": "control",
            "mask_name": "none",
            "ranker": "",
            "top_n": 0,
            "keep_factor": 1.0,
            "rollback_cells": 0,
            "rollback_s3_cells": 0,
            "rollback_q2s3_cells": 0,
            "rollback_s_cells": 0,
        },
    )

    near = e152_scan[e152_scan["gate_class"].eq("missing_actionable")].copy()
    near = near.sort_values(["all_minus_base", "post101_p95_vs_e95_e101_sensor"], ascending=[True, True])
    for rec in near.to_dict("records"):
        pred_index = int(rec["pred_index"])
        if pred_index < 0 or pred_index >= len(e152_preds):
            continue
        pred = clip_prob(e152_preds[pred_index])
        delta = logit(pred) - e95_logit
        add_pred(
            rows,
            preds,
            seen,
            pred,
            {
                "strategy": "control_nearmiss",
                "repair_mode": "none",
                "source_tag": str(rec.get("tag", "")),
                "source_variant_pos": int(rec.get("variant_pos", -1)),
                "source_pred_index": pred_index,
                "source_gate_class": str(rec.get("gate_class", "")),
                "source_projection_mode": str(rec.get("projection_mode", "")),
                "source_family": str(rec.get("source_family", "")),
                "source_all_minus_base": float(rec.get("all_minus_base", np.nan)),
                "source_post101_p95": float(rec.get("post101_p95_vs_e95_e101_sensor", np.nan)),
                "source_e72_gap": float(rec.get("e72_plausible_gap_vs_e95", np.nan)),
                "source_fail_action_cos": bool(rec.get("fail_action_cos", False)),
                "source_fail_active_q2s3": bool(rec.get("fail_action_active_q2s3", False)),
                "mask_name": "none",
                "ranker": "",
                "top_n": 0,
                "keep_factor": 1.0,
                "rollback_cells": 0,
                "rollback_s3_cells": 0,
                "rollback_q2s3_cells": 0,
                "rollback_s_cells": 0,
            },
        )
        for mask_rec in ranked_masks(delta, density):
            mask = np.asarray(mask_rec["mask"], dtype=bool)
            keep_factors = FULL_KEEP_FACTORS if mask_rec["ranker"] == "full" else KEEP_FACTORS
            for keep_factor in keep_factors:
                new_delta = delta.copy()
                new_delta[mask] *= float(keep_factor)
                repaired = clip_prob(sigmoid(e95_logit + new_delta))
                add_pred(
                    rows,
                    preds,
                    seen,
                    repaired,
                    {
                        "strategy": "s3_active_boundary_repair",
                        "repair_mode": "s3_to_e95",
                        "source_tag": str(rec.get("tag", "")),
                        "source_variant_pos": int(rec.get("variant_pos", -1)),
                        "source_pred_index": pred_index,
                        "source_gate_class": str(rec.get("gate_class", "")),
                        "source_projection_mode": str(rec.get("projection_mode", "")),
                        "source_family": str(rec.get("source_family", "")),
                        "source_all_minus_base": float(rec.get("all_minus_base", np.nan)),
                        "source_post101_p95": float(rec.get("post101_p95_vs_e95_e101_sensor", np.nan)),
                        "source_e72_gap": float(rec.get("e72_plausible_gap_vs_e95", np.nan)),
                        "source_fail_action_cos": bool(rec.get("fail_action_cos", False)),
                        "source_fail_active_q2s3": bool(rec.get("fail_action_active_q2s3", False)),
                        "mask_name": str(mask_rec["mask_name"]),
                        "ranker": str(mask_rec["ranker"]),
                        "top_n": int(mask_rec["top_n"]),
                        "keep_factor": float(keep_factor),
                        "rollback_cells": int(mask.sum()),
                        "rollback_s3_cells": int(mask[:, S3].sum()),
                        "rollback_q2s3_cells": int(mask[:, Q2S3].sum()),
                        "rollback_s_cells": int(mask[:, S_ALL].sum()),
                    },
                )
    return pd.DataFrame(rows), preds


def add_e154_flags(scan: pd.DataFrame, e144_all_minus_e95: float) -> pd.DataFrame:
    threshold = e141.e95_plausible_exposure_threshold()
    out = e142.add_relaxed_flags(scan, threshold)
    out["all_four"] = (
        out["strategy"].eq("s3_active_boundary_repair")
        & out["relaxed_structural_tol1e12"].fillna(False).astype(bool)
        & out["budget_ok"].fillna(False).astype(bool)
        & out["post101_ok"].fillna(False).astype(bool)
        & out["gate_strict_actionable"].fillna(False).astype(bool)
        & out["local_material"].fillna(False).astype(bool)
    )
    out["beats_e144_local"] = out["all_minus_base"].lt(float(e144_all_minus_e95) - 1.0e-12)
    out["e154_submit"] = out["all_four"] & out["beats_e144_local"] & out["all_minus_base"].lt(-1.0e-5)
    out["passed_gate_count"] = (
        out[["relaxed_structural_tol1e12", "budget_ok", "post101_ok", "gate_strict_actionable"]]
        .fillna(False)
        .astype(bool)
        .astype(int)
        .sum(axis=1)
    )
    out["gate_class"] = "other"
    relaxed = out["relaxed_structural_tol1e12"].fillna(False).astype(bool)
    budget = out["budget_ok"].fillna(False).astype(bool)
    post101 = out["post101_ok"].fillna(False).astype(bool)
    action = out["gate_strict_actionable"].fillna(False).astype(bool)
    out.loc[relaxed & budget & post101 & action, "gate_class"] = "all_four"
    out.loc[relaxed & budget & post101 & ~action, "gate_class"] = "missing_actionable"
    out.loc[budget & post101 & action & ~relaxed, "gate_class"] = "missing_relaxed"
    out.loc[relaxed & post101 & action & ~budget, "gate_class"] = "missing_budget"
    out.loc[relaxed & budget & action & ~post101, "gate_class"] = "missing_post101"
    return out


def summarize(scan: pd.DataFrame) -> pd.DataFrame:
    variants = scan[scan["strategy"].eq("s3_active_boundary_repair")].copy()
    if variants.empty:
        return pd.DataFrame()
    rows: list[dict[str, Any]] = []
    for keys, group in variants.groupby(["mask_name", "ranker"], dropna=False):
        mask_name, ranker = keys
        all_four = group[group["all_four"].fillna(False).astype(bool)]
        submit = group[group["e154_submit"].fillna(False).astype(bool)]
        rows.append(
            {
                "mask_name": str(mask_name),
                "ranker": str(ranker),
                "rows": int(len(group)),
                "all_four": int(len(all_four)),
                "e154_submit": int(len(submit)),
                "actionable": int(group["gate_strict_actionable"].fillna(False).astype(bool).sum()),
                "relaxed": int(group["relaxed_structural_tol1e12"].fillna(False).astype(bool).sum()),
                "budget_ok": int(group["budget_ok"].fillna(False).astype(bool).sum()),
                "post101_ok": int(group["post101_ok"].fillna(False).astype(bool).sum()),
                "best_all_minus_base": float(group["all_minus_base"].min()),
                "best_all_four_all_minus_base": float(all_four["all_minus_base"].min()) if len(all_four) else np.nan,
                "best_post101_p95": float(group["post101_p95_vs_e95_e101_sensor"].min()),
                "best_e72_gap": float(group["e72_plausible_gap_vs_e95"].min()),
                "min_q2s3_l1": float(group["q2s3_delta95_l1"].min()),
                "min_e101_active_l1": float(group["e101_active_delta95_l1"].min()),
                "min_tail_equal_resid": float(group["tail_equal_law_resid_ratio"].min()),
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["e154_submit", "all_four", "best_all_four_all_minus_base", "best_all_minus_base"],
        ascending=[False, False, True, True],
    )


def blocker_summary(scan: pd.DataFrame) -> pd.DataFrame:
    variants = scan[scan["strategy"].eq("s3_active_boundary_repair")].copy()
    if variants.empty:
        return pd.DataFrame()
    cols = {
        "fail_action_cos": ~bool_col(variants, "gate_cos95_resid025"),
        "fail_action_active_q2s3": ~bool_col(variants, "gate_active_q2s3_not_more_than_e101"),
        "fail_action_e72": ~bool_col(variants, "gate_e72_not_more_than_e95"),
        "fail_action_material": ~bool_col(variants, "gate_material_vs_e95"),
        "fail_relaxed": ~bool_col(variants, "relaxed_structural_tol1e12"),
        "fail_budget": ~bool_col(variants, "budget_ok"),
        "fail_post101": ~bool_col(variants, "post101_ok"),
    }
    rows: list[dict[str, Any]] = []
    for name, group in variants.groupby("gate_class", dropna=False):
        idx = group.index
        for col, values in cols.items():
            vals = values.loc[idx]
            rows.append(
                {
                    "gate_class": name,
                    "component": col,
                    "fail_count": int(vals.sum()),
                    "rows": int(len(group)),
                    "fail_rate": float(vals.mean()) if len(group) else np.nan,
                }
            )
    return pd.DataFrame(rows).sort_values(["gate_class", "fail_rate", "fail_count"], ascending=[True, False, False])


def frontier(scan: pd.DataFrame) -> pd.DataFrame:
    variants = scan[scan["strategy"].isin(["s3_active_boundary_repair", "control_nearmiss", "control_e144"])].copy()
    if variants.empty:
        return pd.DataFrame()
    keep = [
        "strategy",
        "gate_class",
        "mask_name",
        "ranker",
        "top_n",
        "keep_factor",
        "rollback_s3_cells",
        "source_tag",
        "source_family",
        "source_projection_mode",
        "all_minus_base",
        "all_four",
        "e154_submit",
        "beats_e144_local",
        "relaxed_structural_tol1e12",
        "budget_ok",
        "post101_ok",
        "gate_strict_actionable",
        "gate_cos95_resid025",
        "gate_active_q2s3_not_more_than_e101",
        "q2s3_delta95_l1",
        "e101_active_delta95_l1",
        "tail_equal_law_cosine",
        "tail_equal_law_resid_ratio",
        "post101_p95_vs_e95_e101_sensor",
        "e72_plausible_gap_vs_e95",
        "tag",
    ]
    for col in ["all_four", "e154_submit", "beats_e144_local"]:
        if col not in variants:
            variants[col] = False
    return variants.sort_values(
        [
            "e154_submit",
            "all_four",
            "beats_e144_local",
            "passed_gate_count",
            "all_minus_base",
            "post101_p95_vs_e95_e101_sensor",
        ],
        ascending=[False, False, False, False, True, True],
    )[[c for c in keep if c in variants.columns]].head(100)


def materialize(scan: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> Path | None:
    eligible = scan[scan["e154_submit"].fillna(False).astype(bool)].copy()
    if eligible.empty:
        return None
    eligible = eligible.sort_values(["all_minus_base", "post101_p95_vs_e95_e101_sensor"], ascending=[True, True])
    rec = eligible.iloc[0]
    pred = preds[int(rec["pred_index"])]
    tag = str(rec["tag"]).split("_")[-1]
    path = OUT / f"{SUBMISSION_PREFIX}_{tag}.csv"
    sub = sample[KEYS].copy()
    sub[TARGETS] = clip_prob(pred)
    sub.to_csv(path, index=False)
    return path


def write_report(summary: pd.DataFrame, blockers: pd.DataFrame, front: pd.DataFrame, scan: pd.DataFrame, submission_path: Path | None) -> None:
    variants = scan[scan["strategy"].eq("s3_active_boundary_repair")].copy()
    near = scan[scan["strategy"].eq("control_nearmiss")].copy()
    all_four_count = int(variants["all_four"].sum()) if len(variants) else 0
    submit_count = int(variants["e154_submit"].sum()) if len(variants) else 0
    if submit_count:
        decision = f"Materialized `{submission_path.name}`. This is a repaired E152 near-miss that passes all-four gates and beats E144 locally."
    elif all_four_count:
        decision = "All-four repairs exist, but none beat E144 with enough local margin for materialization. Keep as repair geometry, not a public file."
    else:
        decision = "No submission. S3 rollback repairs actionability in some rows, but the all-four gate still does not open; S3 active-boundary and relaxed/post101 reward remain coupled."

    def table(df: pd.DataFrame, cols: list[str], n: int = 30) -> str:
        if df.empty:
            return "_empty_"
        keep = [c for c in cols if c in df.columns]
        return e138.md_table(df[keep].head(n), ".9f")

    lines = [
        "# E154 S3 Active-Boundary Repair Probe",
        "",
        "## Question",
        "",
        "E153 showed that E152's near misses mostly fail actionability through S3 active-boundary exposure. E154 asks whether S3-only rollback can make those rows pass all-four gates without destroying relaxed/E72/post-E101 health.",
        "",
        "## Counts",
        "",
        f"- source missing-actionable controls: `{len(near)}`.",
        f"- generated S3 repair rows: `{len(variants)}`.",
        f"- all-four repairs: `{all_four_count}`.",
        f"- materialized submission rows: `{submit_count}`.",
        "",
        "## Repair Summary",
        "",
        table(
            summary,
            [
                "mask_name",
                "ranker",
                "rows",
                "all_four",
                "e154_submit",
                "actionable",
                "relaxed",
                "budget_ok",
                "post101_ok",
                "best_all_minus_base",
                "best_all_four_all_minus_base",
                "best_post101_p95",
                "best_e72_gap",
                "min_q2s3_l1",
                "min_tail_equal_resid",
            ],
            40,
        ),
        "",
        "## Blockers",
        "",
        table(blockers, ["gate_class", "component", "fail_count", "rows", "fail_rate"], 50),
        "",
        "## Frontier Rows",
        "",
        table(
            front,
            [
                "strategy",
                "gate_class",
                "mask_name",
                "ranker",
                "top_n",
                "keep_factor",
                "rollback_s3_cells",
                "source_tag",
                "all_minus_base",
                "all_four",
                "e154_submit",
                "beats_e144_local",
                "relaxed_structural_tol1e12",
                "budget_ok",
                "post101_ok",
                "gate_strict_actionable",
                "gate_cos95_resid025",
                "gate_active_q2s3_not_more_than_e101",
                "q2s3_delta95_l1",
                "tail_equal_law_resid_ratio",
                "post101_p95_vs_e95_e101_sensor",
                "e72_plausible_gap_vs_e95",
                "tag",
            ],
            60,
        ),
        "",
        "## Decision",
        "",
        decision,
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    refs = e130.load_refs(sample)
    state, density, tail_state = e153.e152.setup_state(sample, refs)
    e152_scan = pd.read_csv(e153.SCAN_IN).reset_index(drop=True)
    e152_scan = e153.add_gate_classes(e152_scan)
    e152_scan["variant_pos"] = np.arange(len(e152_scan), dtype=int)
    _sample2, refs2, _branch_axes, e152_preds = e153.rebuild_e152_predictions()
    refs.update(refs2)

    rows, preds = build_candidates(e152_scan, e152_preds, refs, density, sample)
    labels, worlds, views, stress_state = e89mod.build_stress_state(sample, refs["mixmin"])
    scan = e83.score_candidate_rows(rows, preds, sample, refs["mixmin"], labels, worlds, views, stress_state)
    scan = e130.add_tail_and_veto_metrics(scan, preds, refs, density, tail_state)
    transfer = e130.post_e101_transfer_summary(sample, scan, preds, refs, tail_state)
    scan = e130.merge_transfer(scan, transfer)
    e144_control = scan[scan["strategy"].eq("control_e144")].head(1)
    e144_all = float(e144_control["all_minus_base"].iloc[0]) if len(e144_control) else -9.725930e-6
    scan = add_e154_flags(scan, e144_all)
    summary = summarize(scan)
    blockers = blocker_summary(scan)
    front = frontier(scan)
    submission_path = materialize(scan, preds, sample)
    scan["materialized_submission"] = False
    if submission_path is not None:
        suffix = submission_path.stem.split("_")[-1]
        scan["materialized_submission"] = scan["tag"].astype(str).str.endswith(suffix)

    scan.to_csv(SCAN_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    blockers.to_csv(BLOCKER_OUT, index=False)
    front.to_csv(FRONTIER_OUT, index=False)
    write_report(summary, blockers, front, scan, submission_path)

    variants = scan[scan["strategy"].eq("s3_active_boundary_repair")]
    print(
        {
            "source_missing_actionable": int((scan["strategy"] == "control_nearmiss").sum()),
            "repair_rows": int(len(variants)),
            "all_four": int(variants["all_four"].sum()) if len(variants) else 0,
            "e154_submit": int(variants["e154_submit"].sum()) if len(variants) else 0,
            "best_all_minus_base": float(variants["all_minus_base"].min()) if len(variants) else None,
            "best_all_four_all_minus_base": float(variants.loc[variants["all_four"], "all_minus_base"].min())
            if len(variants) and variants["all_four"].any()
            else None,
            "submission": str(submission_path) if submission_path is not None else None,
        }
    )
    if len(summary):
        print(summary.head(12)[["mask_name", "ranker", "rows", "all_four", "e154_submit", "best_all_minus_base", "best_all_four_all_minus_base"]].to_string(index=False))


if __name__ == "__main__":
    main()
