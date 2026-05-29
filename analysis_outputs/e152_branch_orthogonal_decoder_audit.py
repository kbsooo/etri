#!/usr/bin/env python3
"""E152: can any decoder move outside the E142/E143/E144 branch survive?

E151 says the plateau is a selector-resolution and decoder problem. The live
candidate E144 is useful, but it is almost collinear with E143. This audit asks
the next smallest question before inventing a new model:

    Do the existing E137-E140 decoder families contain a non-collinear
    probability movement whose branch-orthogonal component can pass the same
    strict / E72-budget / post-E101 p95 gates?

No public labels are fitted. A submission is materialized only if a projected
non-collinear movement beats E144 locally while passing the current gates.
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
import e95_hard_tail_gate_scan as e95mod  # noqa: E402
import e130_tail_density_synthesis_probe as e130  # noqa: E402
import e137_blocktarget_state_movement_probe as e137  # noqa: E402
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402
import e139_blocktarget_set_consensus_decoder_probe as e139  # noqa: E402
import e140_tailworld_primitive_decoder_probe as e140  # noqa: E402
import e141_tail_tolerance_transfer_audit as e141  # noqa: E402
import e142_transfer_budget_clipped_decoder_probe as e142  # noqa: E402


E142_FILE = "submission_e142_transferclip_09a92236.csv"
E143_FILE = "submission_e143_activeq2s3repair_68ca656f.csv"
E144_FILE = "submission_e144_activeboundary_d7b4b331.csv"

SOURCE_OUT = OUT / "e152_branch_orthogonal_source_geometry.csv"
SCAN_OUT = OUT / "e152_branch_orthogonal_projection_scan.csv"
SUMMARY_OUT = OUT / "e152_branch_orthogonal_projection_summary.csv"
FRONTIER_OUT = OUT / "e152_branch_orthogonal_projection_frontier.csv"
BLOCKER_OUT = OUT / "e152_branch_orthogonal_blocker_intersections.csv"
REPORT_OUT = OUT / "e152_branch_orthogonal_decoder_report.md"
SUBMISSION_PREFIX = "submission_e152_branchorth"

EPS = 1.0e-6
SOURCE_LIMIT_PER_FAMILY = 24
ORTH_ALPHAS = [0.10, 0.25, 0.50, 0.75, 1.00]
TOP_KS = [0, 50, 100]
MATERIAL_FLOOR = 1.0e-6
NONCOL_RESID_FLOOR = 0.20
SOURCE_RESID_FLOOR = 0.35


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def flatten(x: np.ndarray) -> np.ndarray:
    return np.asarray(x, dtype=np.float64).reshape(-1)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    af = flatten(a)
    bf = flatten(b)
    denom = float(np.linalg.norm(af) * np.linalg.norm(bf))
    if denom <= 1.0e-15:
        return 0.0
    return float(np.dot(af, bf) / denom)


def norm(x: np.ndarray) -> float:
    return float(np.linalg.norm(flatten(x)))


def orthogonal_component(delta: np.ndarray, axis: np.ndarray) -> np.ndarray:
    axis_f = flatten(axis)
    denom = float(np.dot(axis_f, axis_f))
    if denom <= 1.0e-15:
        return np.asarray(delta, dtype=np.float64)
    coef = float(np.dot(flatten(delta), axis_f) / denom)
    return np.asarray(delta, dtype=np.float64) - coef * axis


def resid_ratio(delta: np.ndarray, axis: np.ndarray) -> float:
    n = norm(delta)
    if n <= 1.0e-15:
        return 0.0
    return norm(orthogonal_component(delta, axis)) / n


def bool_col(frame: pd.DataFrame, col: str) -> pd.Series:
    if col not in frame.columns:
        return pd.Series(False, index=frame.index)
    raw = frame[col]
    if raw.dtype == bool:
        return raw.fillna(False)
    return raw.astype(str).str.lower().isin(["true", "1", "yes"])


def rec_bool(rec: pd.Series, col: str) -> bool:
    value = rec.get(col, False)
    if pd.isna(value):
        return False
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    if isinstance(value, (int, float, np.integer, np.floating)):
        return bool(value)
    return str(value).strip().lower() in {"true", "1", "yes"}


def num_col(frame: pd.DataFrame, col: str, default: float = np.nan) -> pd.Series:
    if col not in frame.columns:
        return pd.Series(default, index=frame.index, dtype=float)
    return pd.to_numeric(frame[col], errors="coerce")


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
    rows.append({"pred_index": pred_index, "base_index": 0, "tag": e83.stable_tag(pred, "e152_"), **rec})


def setup_state(sample: pd.DataFrame, refs: dict[str, np.ndarray]) -> tuple[np.ndarray, dict[str, np.ndarray], tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]]:
    cell = pd.read_csv(OUT / "e133_local_safety_colocation_atlas_cell_detail.csv")
    _unit, state, _state_summary = e137.load_blocktarget_state(cell)
    tail_state = e95mod.e72_adverse_setup(refs["mixmin"], refs["failed_e72"])
    _density_masks, density = e130.build_density_masks(sample, refs)
    return state, density, tail_state


def source_builders(
    sample: pd.DataFrame,
    refs: dict[str, np.ndarray],
    state: np.ndarray,
    density: dict[str, np.ndarray],
    tail_state: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray],
) -> list[tuple[str, pd.DataFrame, list[np.ndarray]]]:
    e137_rows, e137_preds, _diag = e137.build_candidates(sample, refs, state, tail_state)
    e138_rows, e138_preds, _diag2, _mask = e138.build_candidates(sample, refs, state, density, tail_state)
    e139_rows, e139_preds, _dec, _mask2 = e139.build_candidates(sample, refs, state, density, tail_state)
    micro = pd.read_csv(e140.MICRO_OUT)
    e140_rows, e140_preds = e140.build_combined_candidates(micro, refs)
    return [
        ("e137", pd.read_csv(e137.SCAN_OUT), e137_preds),
        ("e138", pd.read_csv(e138.SCAN_OUT), e138_preds),
        ("e139", pd.read_csv(e139.SCAN_OUT), e139_preds),
        ("e140", pd.read_csv(e140.SCAN_OUT), e140_preds),
    ]


def source_geometry(
    sample: pd.DataFrame,
    refs: dict[str, np.ndarray],
    state: np.ndarray,
    density: dict[str, np.ndarray],
    tail_state: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray],
    branch_axes: dict[str, np.ndarray],
) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    e95_logit = logit(refs["e95"])
    pred_lookup: dict[str, np.ndarray] = {}
    rows: list[dict[str, Any]] = []
    for family, scan, preds in source_builders(sample, refs, state, density, tail_state):
        scan = scan.reset_index(drop=True).copy()
        if "strategy" in scan.columns:
            variants = scan[~scan["strategy"].astype(str).str.contains("control", na=False)].copy()
        else:
            variants = scan.copy()
        for idx, rec in variants.iterrows():
            pred_index = int(rec["pred_index"])
            if pred_index < 0 or pred_index >= len(preds):
                continue
            pred = clip_prob(preds[pred_index])
            delta = logit(pred) - e95_logit
            delta_norm = norm(delta)
            if delta_norm <= 1.0e-12:
                continue
            source_key = f"{family}:{pred_index}:{idx}"
            pred_lookup[source_key] = pred
            local = float(rec["all_minus_base"]) if "all_minus_base" in rec and pd.notna(rec["all_minus_base"]) else np.nan
            post_p95 = (
                float(rec["post101_p95_vs_e95_e101_sensor"])
                if "post101_p95_vs_e95_e101_sensor" in rec and pd.notna(rec["post101_p95_vs_e95_e101_sensor"])
                else np.nan
            )
            e72_gap = (
                float(rec["e72_plausible_gap_vs_e95"])
                if "e72_plausible_gap_vs_e95" in rec and pd.notna(rec["e72_plausible_gap_vs_e95"])
                else np.nan
            )
            rows.append(
                {
                    "source_key": source_key,
                    "family": family,
                    "source_row": int(idx),
                    "source_pred_index": pred_index,
                    "source_tag": str(rec.get("tag", "")),
                    "source_strategy": str(rec.get("strategy", "")),
                    "source_descriptor": str(
                        rec.get("mask_name", rec.get("pool", rec.get("decoder", rec.get("context", ""))))
                    ),
                    "all_minus_base": local,
                    "post101_p95_vs_e95_e101_sensor": post_p95,
                    "post101_mean_vs_e95_e101_sensor": float(rec.get("post101_mean_vs_e95_e101_sensor", np.nan)),
                    "e72_plausible_gap_vs_e95": e72_gap,
                    "sets_tail_neutral": float(rec.get("sets_tail_neutral", np.nan)),
                    "sets_beating_base": float(rec.get("sets_beating_base", np.nan)),
                    "gate_strict_actionable": rec_bool(rec, "gate_strict_actionable"),
                    "relaxed_structural_tol1e12": rec_bool(rec, "relaxed_structural_tol1e12"),
                    "strict_gate": rec_bool(rec, "strict_gate"),
                    "structural_strict_gate": rec_bool(rec, "structural_strict_gate"),
                    "delta_norm": delta_norm,
                    "changed_cells_vs_e95": int(np.sum(np.abs(delta) > 1.0e-12)),
                    "cos_e144": cosine(delta, branch_axes["e144"]),
                    "cos_e143": cosine(delta, branch_axes["e143"]),
                    "cos_e142": cosine(delta, branch_axes["e142"]),
                    "resid_ratio_e144": resid_ratio(delta, branch_axes["e144"]),
                    "resid_ratio_e143": resid_ratio(delta, branch_axes["e143"]),
                    "resid_ratio_e142": resid_ratio(delta, branch_axes["e142"]),
                }
            )
    geo = pd.DataFrame(rows)
    if geo.empty:
        return geo, pred_lookup
    geo["local_good"] = num_col(geo, "all_minus_base").lt(-MATERIAL_FLOOR)
    geo["local_material_1e5"] = num_col(geo, "all_minus_base").lt(-1.0e-5)
    geo["post101_p95_ok"] = num_col(geo, "post101_p95_vs_e95_e101_sensor").le(0.0)
    geo["post101_mean_ok"] = num_col(geo, "post101_mean_vs_e95_e101_sensor").lt(0.0)
    geo["noncollinear_source"] = geo["resid_ratio_e144"].ge(SOURCE_RESID_FLOOR) & geo["cos_e144"].abs().le(0.90)
    geo["candidate_interest"] = (
        geo["local_good"]
        | geo["post101_p95_ok"]
        | bool_col(geo, "gate_strict_actionable")
        | bool_col(geo, "relaxed_structural_tol1e12")
        | bool_col(geo, "strict_gate")
        | bool_col(geo, "structural_strict_gate")
    )
    geo["source_priority"] = (
        -num_col(geo, "all_minus_base").fillna(0.0).clip(upper=0.0)
        + 0.000010 * geo["post101_p95_ok"].astype(float)
        + 0.000010 * geo["noncollinear_source"].astype(float)
        - 0.000005 * num_col(geo, "e72_plausible_gap_vs_e95").fillna(0.0).clip(lower=0.0)
    )
    return geo.sort_values("source_priority", ascending=False).reset_index(drop=True), pred_lookup


def topk_mask(delta: np.ndarray, top_k: int) -> np.ndarray:
    if top_k <= 0 or top_k >= delta.size:
        return np.ones(delta.shape, dtype=bool)
    flat_abs = np.abs(delta).reshape(-1)
    if not np.any(flat_abs > 0.0):
        return np.zeros(delta.shape, dtype=bool)
    order = np.argsort(-flat_abs)
    mask = np.zeros(delta.size, dtype=bool)
    mask[order[:top_k]] = True
    return mask.reshape(delta.shape)


def build_projected_candidates(
    geo: pd.DataFrame,
    pred_lookup: dict[str, np.ndarray],
    refs: dict[str, np.ndarray],
    branch_axes: dict[str, np.ndarray],
    e144_pred: np.ndarray,
) -> tuple[pd.DataFrame, list[np.ndarray]]:
    e95 = refs["e95"]
    e95_logit = logit(e95)
    e144_delta = branch_axes["e144"]
    preds: list[np.ndarray] = [e95, e144_pred]
    seen: dict[str, int] = {e138.pred_key(e95): 0, e138.pred_key(e144_pred): 1}
    rows: list[dict[str, Any]] = [
        {
            "pred_index": 1,
            "base_index": 0,
            "tag": "e152_control_e144",
            "strategy": "control_e144",
            "projection_mode": "control",
            "source_key": "e144",
            "source_family": "e144",
            "source_tag": E144_FILE,
            "alpha": 1.0,
            "top_k": 0,
        }
    ]

    selected_pool = geo[geo["candidate_interest"]].copy()
    selected_frames: list[pd.DataFrame] = []
    for _family, family_rows in selected_pool.groupby("family", dropna=False):
        selected_frames.append(
            family_rows.sort_values(
                ["source_priority", "noncollinear_source", "local_material_1e5"],
                ascending=[False, False, False],
            )
            .drop_duplicates(["family", "source_pred_index"], keep="first")
            .head(SOURCE_LIMIT_PER_FAMILY)
        )
    selected = pd.concat(selected_frames, ignore_index=True) if selected_frames else selected_pool.head(0)
    for rec in selected.to_dict("records"):
        source_key = str(rec["source_key"])
        pred = pred_lookup[source_key]
        source_delta = logit(pred) - e95_logit
        orth = orthogonal_component(source_delta, e144_delta)
        if norm(orth) <= 1.0e-12:
            continue
        for top_k in TOP_KS:
            mask = topk_mask(orth, top_k)
            masked_orth = np.where(mask, orth, 0.0)
            if norm(masked_orth) <= 1.0e-12:
                continue
            mode_suffix = "full" if top_k == 0 else f"top{top_k}"
            for alpha in ORTH_ALPHAS:
                for anchor_name, anchor_delta in [("e95", np.zeros_like(e144_delta)), ("e144", e144_delta)]:
                    new_delta = anchor_delta + float(alpha) * masked_orth
                    new_pred = clip_prob(sigmoid(e95_logit + new_delta))
                    cand_cos = cosine(new_delta, e144_delta)
                    cand_resid = resid_ratio(new_delta, e144_delta)
                    add_pred(
                        rows,
                        preds,
                        seen,
                        new_pred,
                        {
                            "strategy": "branch_orthogonal_projection",
                            "projection_mode": f"{anchor_name}_plus_orth_{mode_suffix}",
                            "source_key": source_key,
                            "source_family": str(rec["family"]),
                            "source_tag": str(rec["source_tag"]),
                            "source_strategy": str(rec["source_strategy"]),
                            "source_descriptor": str(rec["source_descriptor"]),
                            "source_all_minus_base": float(rec["all_minus_base"]),
                            "source_post101_p95": float(rec["post101_p95_vs_e95_e101_sensor"]),
                            "source_cos_e144": float(rec["cos_e144"]),
                            "source_resid_ratio_e144": float(rec["resid_ratio_e144"]),
                            "source_noncollinear": bool(rec["noncollinear_source"]),
                            "alpha": float(alpha),
                            "top_k": int(top_k),
                            "orth_norm": norm(masked_orth),
                            "candidate_cos_e144": cand_cos,
                            "candidate_resid_ratio_e144": cand_resid,
                            "changed_cells_vs_e95_pre": int(np.sum(np.abs(new_delta) > 1.0e-12)),
                        },
                    )
    return pd.DataFrame(rows), preds


def add_e152_flags(scan: pd.DataFrame, e144_all_minus_e95: float) -> pd.DataFrame:
    threshold = e141.e95_plausible_exposure_threshold()
    out = e142.add_relaxed_flags(scan, threshold)
    out["beats_e144_local"] = out["all_minus_base"].lt(e144_all_minus_e95 - 1.0e-12)
    out["candidate_noncollinear"] = (
        out["candidate_resid_ratio_e144"].fillna(0.0).ge(NONCOL_RESID_FLOOR)
        | out["source_resid_ratio_e144"].fillna(0.0).ge(SOURCE_RESID_FLOOR)
    )
    out["strict_e72_post101"] = (
        out["strategy"].eq("branch_orthogonal_projection")
        & out["relaxed_structural_tol1e12"].fillna(False).astype(bool)
        & out["budget_ok"].fillna(False).astype(bool)
        & out["post101_ok"].fillna(False).astype(bool)
        & out["gate_strict_actionable"].fillna(False).astype(bool)
        & out["local_material"].fillna(False).astype(bool)
    )
    out["e152_submit"] = (
        out["strict_e72_post101"]
        & out["candidate_noncollinear"]
        & out["beats_e144_local"]
        & out["all_minus_base"].lt(-1.0e-5)
    )
    return out


def summarize_sources(geo: pd.DataFrame) -> pd.DataFrame:
    if geo.empty:
        return pd.DataFrame()
    rows: list[dict[str, Any]] = []
    for family, g in geo.groupby("family", dropna=False):
        rows.append(
            {
                "family": family,
                "rows": int(len(g)),
                "candidate_interest": int(g["candidate_interest"].sum()),
                "noncollinear_source": int(g["noncollinear_source"].sum()),
                "local_material_1e5": int(g["local_material_1e5"].sum()),
                "post101_p95_ok": int(g["post101_p95_ok"].sum()),
                "local_and_noncollinear": int((g["local_material_1e5"] & g["noncollinear_source"]).sum()),
                "post101_and_noncollinear": int((g["post101_p95_ok"] & g["noncollinear_source"]).sum()),
                "best_all_minus_base": float(g["all_minus_base"].min()),
                "best_post101_p95": float(g["post101_p95_vs_e95_e101_sensor"].min()),
                "max_resid_ratio_e144": float(g["resid_ratio_e144"].max()),
                "median_abs_cos_e144": float(g["cos_e144"].abs().median()),
            }
        )
    return pd.DataFrame(rows).sort_values("family")


def summarize_scan(scan: pd.DataFrame) -> pd.DataFrame:
    if scan.empty:
        return pd.DataFrame()
    variants = scan[scan["strategy"].eq("branch_orthogonal_projection")].copy()
    groups = ["projection_mode", "source_family"]
    rows: list[dict[str, Any]] = []
    for keys, g in variants.groupby(groups, dropna=False):
        projection_mode, source_family = keys
        rows.append(
            {
                "projection_mode": projection_mode,
                "source_family": source_family,
                "rows": int(len(g)),
                "noncollinear": int(g["candidate_noncollinear"].sum()),
                "relaxed_structural": int(g["relaxed_structural_tol1e12"].sum()),
                "budget_ok": int(g["budget_ok"].sum()),
                "post101_ok": int(g["post101_ok"].sum()),
                "gate_strict_actionable": int(g["gate_strict_actionable"].sum()),
                "strict_e72_post101": int(g["strict_e72_post101"].sum()),
                "e152_submit": int(g["e152_submit"].sum()),
                "best_all_minus_base": float(g["all_minus_base"].min()),
                "best_post101_p95": float(g["post101_p95_vs_e95_e101_sensor"].min()),
                "best_e72_gap": float(g["e72_plausible_gap_vs_e95"].min()),
                "max_candidate_resid_ratio_e144": float(g["candidate_resid_ratio_e144"].max()),
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["e152_submit", "strict_e72_post101", "best_all_minus_base"], ascending=[False, False, True]
    )


def frontier(scan: pd.DataFrame) -> pd.DataFrame:
    if scan.empty:
        return pd.DataFrame()
    variants = scan[scan["strategy"].eq("branch_orthogonal_projection")].copy()
    if variants.empty:
        return variants
    priority_cols = [
        "e152_submit",
        "strict_e72_post101",
        "beats_e144_local",
        "candidate_noncollinear",
        "relaxed_structural_tol1e12",
        "budget_ok",
        "post101_ok",
        "gate_strict_actionable",
    ]
    for col in priority_cols:
        if col not in variants:
            variants[col] = False
    return variants.sort_values(
        [
            "e152_submit",
            "strict_e72_post101",
            "beats_e144_local",
            "candidate_noncollinear",
            "all_minus_base",
            "post101_p95_vs_e95_e101_sensor",
        ],
        ascending=[False, False, False, False, True, True],
    ).head(80)


def blocker_intersections(scan: pd.DataFrame) -> pd.DataFrame:
    if scan.empty:
        return pd.DataFrame()
    variants = scan[scan["strategy"].eq("branch_orthogonal_projection")].copy()
    if variants.empty:
        return pd.DataFrame()
    masks = {
        "relaxed_and_budget": variants["relaxed_structural_tol1e12"].fillna(False).astype(bool)
        & variants["budget_ok"].fillna(False).astype(bool),
        "relaxed_and_post101": variants["relaxed_structural_tol1e12"].fillna(False).astype(bool)
        & variants["post101_ok"].fillna(False).astype(bool),
        "budget_and_post101": variants["budget_ok"].fillna(False).astype(bool)
        & variants["post101_ok"].fillna(False).astype(bool),
        "budget_post101_actionable": variants["budget_ok"].fillna(False).astype(bool)
        & variants["post101_ok"].fillna(False).astype(bool)
        & variants["gate_strict_actionable"].fillna(False).astype(bool),
        "relaxed_budget_post101": variants["relaxed_structural_tol1e12"].fillna(False).astype(bool)
        & variants["budget_ok"].fillna(False).astype(bool)
        & variants["post101_ok"].fillna(False).astype(bool),
        "relaxed_budget_actionable": variants["relaxed_structural_tol1e12"].fillna(False).astype(bool)
        & variants["budget_ok"].fillna(False).astype(bool)
        & variants["gate_strict_actionable"].fillna(False).astype(bool),
        "relaxed_post101_actionable": variants["relaxed_structural_tol1e12"].fillna(False).astype(bool)
        & variants["post101_ok"].fillna(False).astype(bool)
        & variants["gate_strict_actionable"].fillna(False).astype(bool),
        "all_four": variants["relaxed_structural_tol1e12"].fillna(False).astype(bool)
        & variants["budget_ok"].fillna(False).astype(bool)
        & variants["post101_ok"].fillna(False).astype(bool)
        & variants["gate_strict_actionable"].fillna(False).astype(bool),
        "beats_e144_and_all_four": variants["beats_e144_local"].fillna(False).astype(bool)
        & variants["relaxed_structural_tol1e12"].fillna(False).astype(bool)
        & variants["budget_ok"].fillna(False).astype(bool)
        & variants["post101_ok"].fillna(False).astype(bool)
        & variants["gate_strict_actionable"].fillna(False).astype(bool),
    }
    rows: list[dict[str, Any]] = []
    for name, mask in masks.items():
        g = variants[mask].copy()
        rec: dict[str, Any] = {"intersection": name, "count": int(mask.sum())}
        if not g.empty:
            best = g.sort_values(["all_minus_base", "post101_p95_vs_e95_e101_sensor"], ascending=[True, True]).iloc[0]
            rec.update(
                {
                    "best_projection_mode": str(best["projection_mode"]),
                    "best_source_family": str(best["source_family"]),
                    "best_all_minus_base": float(best["all_minus_base"]),
                    "best_post101_p95": float(best["post101_p95_vs_e95_e101_sensor"]),
                    "best_e72_gap": float(best["e72_plausible_gap_vs_e95"]),
                    "best_candidate_resid_ratio_e144": float(best["candidate_resid_ratio_e144"]),
                    "best_gate_strict_actionable": bool(best["gate_strict_actionable"]),
                    "best_relaxed": bool(best["relaxed_structural_tol1e12"]),
                    "best_budget_ok": bool(best["budget_ok"]),
                    "best_post101_ok": bool(best["post101_ok"]),
                    "best_tag": str(best["tag"]),
                }
            )
        rows.append(rec)
    return pd.DataFrame(rows)


def materialize(scan: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> Path | None:
    eligible = scan[scan["e152_submit"].fillna(False).astype(bool)].copy()
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


def write_report(
    source_summary: pd.DataFrame,
    geo: pd.DataFrame,
    summary: pd.DataFrame,
    blockers: pd.DataFrame,
    front: pd.DataFrame,
    submission_path: Path | None,
) -> None:
    variants = pd.read_csv(SCAN_OUT) if SCAN_OUT.exists() else pd.DataFrame()
    if not variants.empty:
        proj = variants[variants["strategy"].eq("branch_orthogonal_projection")]
        strict_count = int(proj["strict_e72_post101"].sum()) if "strict_e72_post101" in proj else 0
        submit_count = int(proj["e152_submit"].sum()) if "e152_submit" in proj else 0
    else:
        proj = pd.DataFrame()
        strict_count = 0
        submit_count = 0
    if submit_count:
        decision = (
            f"Materialized `{submission_path.name}`. This is a real non-collinear E144 successor candidate and should be "
            "interpreted as evidence that decoder geometry, not only branch pruning, can move the frontier."
        )
    elif strict_count:
        decision = (
            "Non-collinear strict/E72/post101 rows exist, but none beat E144 with enough local margin for submission. "
            "Keep them as decoder-target clues, not public files."
        )
    else:
        decision = (
            "No branch-orthogonal projection passes strict/E72/post101 plus active-veto gates. This strengthens the E151 "
            "world model: the visible decoder signal outside E142/E143/E144 is not currently translatable into a safe "
            "probability movement."
        )

    def table(df: pd.DataFrame, cols: list[str], n: int = 20) -> str:
        if df.empty:
            return "None."
        keep = [c for c in cols if c in df.columns]
        return e138.md_table(df[keep].head(n), ".9f")

    lines = [
        "# E152 Branch-Orthogonal Decoder Audit",
        "",
        "## Question",
        "",
        "If E151 is right, the problem is not absence of signal but failure to decode non-collinear signal into public-tail-safe probabilities. This audit projects E137-E140 decoder moves away from the E144 branch and asks whether the remaining component survives the current gates.",
        "",
        "## Source Geometry",
        "",
        table(
            source_summary,
            [
                "family",
                "rows",
                "candidate_interest",
                "noncollinear_source",
                "local_material_1e5",
                "post101_p95_ok",
                "local_and_noncollinear",
                "post101_and_noncollinear",
                "best_all_minus_base",
                "best_post101_p95",
                "max_resid_ratio_e144",
                "median_abs_cos_e144",
            ],
            20,
        ),
        "",
        "## Projection Summary",
        "",
        table(
            summary,
            [
                "projection_mode",
                "source_family",
                "rows",
                "noncollinear",
                "relaxed_structural",
                "budget_ok",
                "post101_ok",
                "gate_strict_actionable",
                "strict_e72_post101",
                "e152_submit",
                "best_all_minus_base",
                "best_post101_p95",
                "best_e72_gap",
                "max_candidate_resid_ratio_e144",
            ],
            40,
        ),
        "",
        "## Gate Intersection Blockers",
        "",
        table(
            blockers,
            [
                "intersection",
                "count",
                "best_projection_mode",
                "best_source_family",
                "best_all_minus_base",
                "best_post101_p95",
                "best_e72_gap",
                "best_candidate_resid_ratio_e144",
                "best_gate_strict_actionable",
                "best_relaxed",
                "best_budget_ok",
                "best_post101_ok",
                "best_tag",
            ],
            20,
        ),
        "",
        "## Frontier Rows",
        "",
        table(
            front,
            [
                "projection_mode",
                "source_family",
                "source_tag",
                "alpha",
                "top_k",
                "all_minus_base",
                "beats_e144_local",
                "relaxed_structural_tol1e12",
                "budget_ok",
                "post101_ok",
                "gate_strict_actionable",
                "strict_e72_post101",
                "candidate_noncollinear",
                "candidate_resid_ratio_e144",
                "source_resid_ratio_e144",
                "post101_p95_vs_e95_e101_sensor",
                "e72_plausible_gap_vs_e95",
                "tag",
            ],
            50,
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
    e142_pred = clip_prob(load_sub(E142_FILE, sample)[TARGETS].to_numpy(dtype=np.float64))
    e143_pred = clip_prob(load_sub(E143_FILE, sample)[TARGETS].to_numpy(dtype=np.float64))
    e144_pred = clip_prob(load_sub(E144_FILE, sample)[TARGETS].to_numpy(dtype=np.float64))
    refs["e142"] = e142_pred
    refs["e143"] = e143_pred
    refs["e144"] = e144_pred

    e95_logit = logit(refs["e95"])
    branch_axes = {
        "e142": logit(e142_pred) - e95_logit,
        "e143": logit(e143_pred) - e95_logit,
        "e144": logit(e144_pred) - e95_logit,
    }
    state, density, tail_state = setup_state(sample, refs)
    geo, pred_lookup = source_geometry(sample, refs, state, density, tail_state, branch_axes)
    source_summary = summarize_sources(geo)
    rows, preds = build_projected_candidates(geo, pred_lookup, refs, branch_axes, e144_pred)

    labels, worlds, views, stress_state = e89mod.build_stress_state(sample, refs["mixmin"])
    if rows.empty:
        scan = rows.copy()
        transfer = pd.DataFrame()
        summary = pd.DataFrame()
        blockers = pd.DataFrame()
        front = pd.DataFrame()
        submission_path = None
    else:
        scan = e83.score_candidate_rows(rows, preds, sample, refs["mixmin"], labels, worlds, views, stress_state)
        scan = e130.add_tail_and_veto_metrics(scan, preds, refs, density, tail_state)
        transfer = e130.post_e101_transfer_summary(sample, scan, preds, refs, tail_state)
        scan = e130.merge_transfer(scan, transfer)
        e144_front = pd.read_csv(OUT / "e144_e143_active_boundary_refine_frontier.csv")
        e144_selected = e144_front[e144_front["tag"].astype(str).str.contains("d7b4b331")].iloc[0]
        scan = add_e152_flags(scan, float(e144_selected["all_minus_base"]))
        summary = summarize_scan(scan)
        front = frontier(scan)
        blockers = blocker_intersections(scan)
        submission_path = materialize(scan, preds, sample)
        scan["materialized_submission"] = False
        if submission_path is not None:
            suffix = submission_path.stem.split("_")[-1]
            scan["materialized_submission"] = scan["tag"].astype(str).str.endswith(suffix)

    geo.to_csv(SOURCE_OUT, index=False)
    scan.to_csv(SCAN_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    blockers.to_csv(BLOCKER_OUT, index=False)
    front.to_csv(FRONTIER_OUT, index=False)
    write_report(source_summary, geo, summary, blockers, front, submission_path)

    variants = scan[scan["strategy"].eq("branch_orthogonal_projection")] if not scan.empty else pd.DataFrame()
    print(
        {
            "source_rows": int(len(geo)),
            "source_interest": int(geo["candidate_interest"].sum()) if len(geo) else 0,
            "source_noncollinear": int(geo["noncollinear_source"].sum()) if len(geo) else 0,
            "projection_rows": int(len(variants)),
            "relaxed": int(variants["relaxed_structural_tol1e12"].sum()) if len(variants) else 0,
            "budget_ok": int(variants["budget_ok"].sum()) if len(variants) else 0,
            "post101_ok": int(variants["post101_ok"].sum()) if len(variants) else 0,
            "gate_strict_actionable": int(variants["gate_strict_actionable"].sum()) if len(variants) else 0,
            "strict_e72_post101": int(variants["strict_e72_post101"].sum()) if len(variants) else 0,
            "e152_submit": int(variants["e152_submit"].sum()) if len(variants) else 0,
            "best_all_minus_e95": float(variants["all_minus_base"].min()) if len(variants) else None,
            "best_post101_p95": float(variants["post101_p95_vs_e95_e101_sensor"].min()) if len(variants) else None,
            "submission": str(submission_path) if submission_path else None,
        }
    )
    print(summary.head(30).to_string(index=False) if not summary.empty else "empty summary")


if __name__ == "__main__":
    main()
