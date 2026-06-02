#!/usr/bin/env python3
"""H104: toxic-axis residual transport HS-JEPA.

H103 selects route-actions whose combined move stays inside the known bad-axis
nullspace.  H104 tests the stronger hypothesis:

    the route-action law is useful, but submitted action must be the
    bad-axis-residual part of that law

Instead of only choosing safe route-actions, H104 builds a desired route-action
field, projects out the positive component along bad public axes, and decodes
the remaining residual field back into row-target assignments.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import importlib.util
import shutil
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HITL = ROOT / "hitl"
OUT = HITL / "h104_toxic_axis_residual_transport_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H103_PATH = HITL / "h103_toxic_shadow_cancellation_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h103mod", H103_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H103_PATH}")
h103mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h103mod
SPEC.loader.exec_module(h103mod)

h102mod = h103mod.h102mod
h100mod = h103mod.h100mod
h099mod = h103mod.h099mod
h098mod = h103mod.h098mod
h097mod = h103mod.h097mod
h095mod = h103mod.h095mod
h085mod = h103mod.h085mod

TARGETS = h103mod.TARGETS
KEYS = h103mod.KEYS
BASE_FILE = h103mod.BASE_FILE
TOL = h103mod.TOL


@dataclass(frozen=True)
class H104Spec:
    name: str
    source_group: str
    top_actions: int
    max_cells: int
    max_rows: int
    max_per_subject: int
    q2_cap: int
    max_per_target: int
    amp: float
    move_cap: float
    min_abs_move: float
    projection_strength: float
    projection_ridge: float
    good_boost: float
    h088_extra: float
    second_projection_strength: float
    max_bad_weighted_pos: float
    max_bad_max_pos: float
    max_h088_cos: float
    min_good_margin: float
    route_pred_cap: float
    h098_pred_cap: float
    worldview: str


def clip_prob(x: np.ndarray) -> np.ndarray:
    return h085mod.clip_prob(np.asarray(x, dtype=np.float64))


def logit(x: np.ndarray) -> np.ndarray:
    return h085mod.logit(np.asarray(x, dtype=np.float64))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return h085mod.sigmoid(np.asarray(x, dtype=np.float64))


def rank01(values: np.ndarray, high: bool = True) -> np.ndarray:
    return h085mod.rank01(np.asarray(values, dtype=np.float64), high=high)


def safe_id(text: str, limit: int = 132) -> str:
    return h085mod.safe_id(text, limit=limit)


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return h085mod.md_table(frame, n=n)


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h104_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h104_toxicresid_*_uploadsafe.csv"):
        path.unlink()


def candidate_specs() -> list[H104Spec]:
    return [
        H104Spec(
            name="resid_conflict_transport_c96_a110",
            source_group="conflict_transport",
            top_actions=76,
            max_cells=96,
            max_rows=60,
            max_per_subject=11,
            q2_cap=8,
            max_per_target=24,
            amp=1.10,
            move_cap=0.34,
            min_abs_move=0.012,
            projection_strength=1.10,
            projection_ridge=0.030,
            good_boost=0.10,
            h088_extra=1.20,
            second_projection_strength=0.35,
            max_bad_weighted_pos=0.018,
            max_bad_max_pos=0.075,
            max_h088_cos=-0.002,
            min_good_margin=0.004,
            route_pred_cap=-0.000260,
            h098_pred_cap=0.000070,
            worldview="route-action signal is real, but only its bad-axis residual should be submitted",
        ),
        H104Spec(
            name="broad_route_resid_c160_a085",
            source_group="broad_route",
            top_actions=120,
            max_cells=160,
            max_rows=96,
            max_per_subject=16,
            q2_cap=24,
            max_per_target=38,
            amp=0.85,
            move_cap=0.24,
            min_abs_move=0.010,
            projection_strength=1.00,
            projection_ridge=0.050,
            good_boost=0.16,
            h088_extra=0.70,
            second_projection_strength=0.25,
            max_bad_weighted_pos=0.026,
            max_bad_max_pos=0.105,
            max_h088_cos=0.002,
            min_good_margin=-0.002,
            route_pred_cap=-0.000420,
            h098_pred_cap=0.000090,
            worldview="public-safe field is a broad residualized route law, not a sparse nullspace",
        ),
        H104Spec(
            name="good_anchor_oblique_resid_c140_a100",
            source_group="anchor_oblique",
            top_actions=98,
            max_cells=140,
            max_rows=82,
            max_per_subject=14,
            q2_cap=14,
            max_per_target=34,
            amp=1.00,
            move_cap=0.30,
            min_abs_move=0.011,
            projection_strength=0.90,
            projection_ridge=0.060,
            good_boost=0.34,
            h088_extra=0.90,
            second_projection_strength=0.45,
            max_bad_weighted_pos=0.022,
            max_bad_max_pos=0.090,
            max_h088_cos=0.000,
            min_good_margin=0.012,
            route_pred_cap=-0.000310,
            h098_pred_cap=0.000080,
            worldview="H057-positive anchors define an oblique safe subspace after bad-axis residualization",
        ),
        H104Spec(
            name="objective_resid_q2zero_c120_a095",
            source_group="objective_residual",
            top_actions=92,
            max_cells=120,
            max_rows=78,
            max_per_subject=14,
            q2_cap=0,
            max_per_target=36,
            amp=0.95,
            move_cap=0.28,
            min_abs_move=0.010,
            projection_strength=1.05,
            projection_ridge=0.040,
            good_boost=0.18,
            h088_extra=0.80,
            second_projection_strength=0.30,
            max_bad_weighted_pos=0.024,
            max_bad_max_pos=0.095,
            max_h088_cos=0.001,
            min_good_margin=0.006,
            route_pred_cap=-0.000260,
            h098_pred_cap=0.000090,
            worldview="Q3/S objective route law survives if Q2 is treated as toxic spillover and removed",
        ),
        H104Spec(
            name="q2_counter_resid_c72_a075",
            source_group="q2_counter",
            top_actions=64,
            max_cells=72,
            max_rows=54,
            max_per_subject=9,
            q2_cap=32,
            max_per_target=32,
            amp=0.75,
            move_cap=0.20,
            min_abs_move=0.009,
            projection_strength=1.25,
            projection_ridge=0.035,
            good_boost=0.08,
            h088_extra=1.70,
            second_projection_strength=0.50,
            max_bad_weighted_pos=0.012,
            max_bad_max_pos=0.060,
            max_h088_cos=-0.006,
            min_good_margin=0.000,
            route_pred_cap=-0.000110,
            h098_pred_cap=0.000060,
            worldview="Q2 can move only as an explicit anti-H088 residual counter-field",
        ),
    ]


def normalize_rows(mat: np.ndarray) -> np.ndarray:
    mat = np.asarray(mat, dtype=np.float64)
    norm = np.maximum(np.linalg.norm(mat, axis=1), 1.0e-12)
    return mat / norm[:, None]


def positive_bad_residualize(
    vec: np.ndarray,
    bad_axes: pd.DataFrame,
    bad_moves: np.ndarray,
    strength: float,
    ridge: float,
    h088_extra: float,
) -> tuple[np.ndarray, dict[str, float]]:
    if np.linalg.norm(vec) <= 1.0e-12:
        return vec.copy(), {"removed_norm": 0.0, "positive_coeff_count": 0.0, "h088_removed": 0.0}
    unit_bad = normalize_rows(bad_moves)
    weights = np.sqrt(bad_axes["weight"].to_numpy(dtype=np.float64))
    design = unit_bad * weights[:, None]
    gram = design @ design.T
    rhs = design @ vec
    coef = np.linalg.pinv(gram + ridge * np.eye(len(design))) @ rhs
    pos = np.maximum(coef, 0.0)
    correction = design.T @ pos
    h088_removed = 0.0
    h088_mask = bad_axes["axis_name"].astype(str).eq(h095mod.H088_FILE).to_numpy()
    if h088_mask.any():
        h088_unit = unit_bad[h088_mask][0]
        h088_coeff = max(float(np.dot(vec, h088_unit)), 0.0)
        correction = correction + h088_extra * h088_coeff * h088_unit
        h088_removed = h088_coeff
    out = vec - strength * correction
    return out, {
        "removed_norm": float(np.linalg.norm(strength * correction)),
        "positive_coeff_count": float((pos > 1.0e-10).sum()),
        "h088_removed": float(h088_removed),
    }


def good_anchor_boost(vec: np.ndarray, good_moves: np.ndarray, boost: float) -> tuple[np.ndarray, float]:
    if boost <= 0.0 or np.linalg.norm(vec) <= 1.0e-12:
        return vec.copy(), 0.0
    unit_good = normalize_rows(good_moves)
    coef = np.maximum(unit_good @ vec, 0.0)
    if not np.any(coef > 0.0):
        return vec.copy(), 0.0
    add = unit_good.T @ coef / max(len(unit_good), 1)
    return vec + boost * add, float(np.linalg.norm(boost * add))


def action_priority(scored: pd.DataFrame) -> pd.DataFrame:
    out = scored.copy()
    out["h104_priority"] = (
        0.34 * rank01(-out["h100_route_basis_pred_delta"].to_numpy(dtype=np.float64), high=True)
        + 0.20 * rank01(out["h100_action_score"].to_numpy(dtype=np.float64), high=True)
        + 0.16 * rank01(out["h102_axis_score"].to_numpy(dtype=np.float64), high=True)
        + 0.10 * out["selected_conflict_rate"].to_numpy(dtype=np.float64)
        + 0.08 * out["anti_h088_direction_rate"].to_numpy(dtype=np.float64)
        + 0.08 * out["h057_positive_align_rate"].to_numpy(dtype=np.float64)
        + 0.06 * rank01(out["h102_good_bad_margin"].to_numpy(dtype=np.float64), high=True)
        - 0.12 * rank01(out["h102_bad_weighted_pos"].to_numpy(dtype=np.float64), high=True)
        - 0.08 * np.maximum(out["h102_h088_axis_cos"].to_numpy(dtype=np.float64), 0.0)
        - 0.06 * out["mean_bad_same_rank"].to_numpy(dtype=np.float64)
    )
    return out.sort_values("h104_priority", ascending=False).reset_index(drop=True)


def source_allowed(rec: dict[str, object], group: str) -> bool:
    basis_spec = str(rec["basis_spec"])
    route_name = str(rec["route_name"])
    route_targets = str(rec["route_targets"])
    if group == "conflict_transport":
        return float(rec["selected_conflict_rate"]) >= 0.75 and float(rec["h102_axis_score"]) >= 0.42
    if group == "broad_route":
        return float(rec["h100_route_basis_pred_delta"]) < 0.000025 and float(rec["h100_action_score"]) >= 0.48
    if group == "anchor_oblique":
        return float(rec["h102_good_bad_margin"]) > 0.004 or float(rec["h102_good_max_cos"]) > 0.020
    if group == "objective_residual":
        return (
            (basis_spec in {"basis_objective_a042", "basis_nonq2_positive_a038", "basis_tail_hybrid_a044"} or "S" in route_targets)
            and int(rec["Q2_cells"]) == 0
        )
    if group == "q2_counter":
        return (
            basis_spec == "basis_q2_counter_a050"
            or int(rec["Q2_cells"]) > 0
            or "q2" in route_name.lower()
        ) and float(rec["h102_h088_axis_cos"]) <= 0.006
    raise ValueError(group)


def build_desired_field(
    scored: pd.DataFrame,
    cells_by_basis: dict[str, pd.DataFrame],
    spec: H104Spec,
    shape: tuple[int, int],
) -> tuple[pd.DataFrame, np.ndarray]:
    selected = []
    used_rows: set[int] = set()
    used_basis: set[str] = set()
    subject_counts: dict[str, int] = {}
    q2_count = 0
    move = np.zeros(shape[0] * shape[1], dtype=np.float64)

    for rec in action_priority(scored).to_dict("records"):
        if len(selected) >= spec.top_actions:
            break
        if not source_allowed(rec, spec.source_group):
            continue
        basis_id = str(rec["basis_id"])
        row = int(rec["row"])
        subject = str(rec["subject_id"])
        if basis_id in used_basis or row in used_rows:
            continue
        if subject_counts.get(subject, 0) + 1 > spec.max_per_subject:
            continue
        cells = cells_by_basis[basis_id]
        n_q2 = int(cells["target"].astype(str).eq("Q2").sum())
        if q2_count + n_q2 > spec.q2_cap:
            continue
        tmp = move.copy()
        weight = (
            0.70
            + 0.28 * float(rec["h102_axis_score"])
            + 0.10 * max(float(rec["h102_good_bad_margin"]), 0.0)
            + 0.08 * max(-float(rec["h100_route_basis_pred_delta"]) / 0.00025, 0.0)
        )
        for cell_rec in cells.to_dict("records"):
            flat = int(cell_rec["flat_index"])
            tmp[flat] += float(cell_rec["h100_direct_move"]) * spec.amp * weight
        tmp = np.clip(tmp, -spec.move_cap, spec.move_cap)
        move = tmp
        selected.append(rec)
        used_basis.add(basis_id)
        used_rows.add(row)
        subject_counts[subject] = subject_counts.get(subject, 0) + 1
        q2_count += n_q2
    return pd.DataFrame(selected), move


def target_allowed(target: str, group: str) -> bool:
    if group in {"conflict_transport", "broad_route", "anchor_oblique"}:
        return True
    if group == "objective_residual":
        return target in {"Q3", "S1", "S2", "S3", "S4"}
    if group == "q2_counter":
        return target == "Q2"
    raise ValueError(group)


def decode_residual_cells(
    residual: np.ndarray,
    cell: pd.DataFrame,
    spec: H104Spec,
) -> tuple[pd.DataFrame, np.ndarray]:
    ordered = cell.sort_values("flat_index").reset_index(drop=True).copy()
    move = np.clip(residual.copy(), -spec.move_cap, spec.move_cap)
    sign = np.sign(move)
    h088_sign = np.sign(ordered["h088_logit_move"].to_numpy(dtype=np.float64))
    h057_sign = np.sign(ordered["h057_positive_logit_move"].to_numpy(dtype=np.float64))
    anti_h088 = (sign * h088_sign < 0).astype(float)
    align_h057 = (
        (sign * h057_sign > 0)
        & (ordered["h057_positive_weight"].to_numpy(dtype=np.float64) > 0)
    ).astype(float)
    quality = (
        0.34
        + 0.22 * anti_h088
        + 0.20 * align_h057
        + 0.18 * ordered["h057_h088_anti_conflict"].to_numpy(dtype=np.float64)
        + 0.12 * ordered["h095_safe_cell_score"].to_numpy(dtype=np.float64)
        + 0.10 * ordered["h098_frontier_cell_score"].to_numpy(dtype=np.float64)
        - 0.16 * ordered["h080_bad_same_rank"].to_numpy(dtype=np.float64)
        - 0.08 * ordered["is_h050_null"].to_numpy(dtype=np.float64)
    )
    ordered["h104_move"] = move
    ordered["h104_abs_move"] = np.abs(move)
    ordered["h104_decode_score"] = ordered["h104_abs_move"] * quality
    ordered = ordered[np.abs(ordered["h104_move"].to_numpy(dtype=np.float64)) >= spec.min_abs_move].copy()
    ordered = ordered[ordered["target"].astype(str).map(lambda target: target_allowed(target, spec.source_group))]
    ordered = ordered.sort_values("h104_decode_score", ascending=False)

    selected_rows = []
    used_rows: set[int] = set()
    subject_counts: dict[str, int] = {}
    target_counts: dict[str, int] = {}
    q2_count = 0
    for rec in ordered.to_dict("records"):
        if len(selected_rows) >= spec.max_cells:
            break
        row = int(rec["row"])
        subject = str(rec["subject_id"])
        target = str(rec["target"])
        if row not in used_rows and len(used_rows) >= spec.max_rows:
            continue
        if subject_counts.get(subject, 0) + (0 if row in used_rows else 1) > spec.max_per_subject:
            continue
        if target_counts.get(target, 0) >= spec.max_per_target:
            continue
        if target == "Q2" and q2_count >= spec.q2_cap:
            continue
        selected_rows.append(rec)
        if row not in used_rows:
            used_rows.add(row)
            subject_counts[subject] = subject_counts.get(subject, 0) + 1
        target_counts[target] = target_counts.get(target, 0) + 1
        if target == "Q2":
            q2_count += 1

    selected = pd.DataFrame(selected_rows)
    if selected.empty:
        return selected, np.zeros((250, len(TARGETS)), dtype=np.float64)
    selected = selected.sort_values(["row", "target_index"]).reset_index(drop=True)
    selected["h097_move_col"] = "h104_move"
    move_mat = np.zeros((250, len(TARGETS)), dtype=np.float64)
    for rec in selected.to_dict("records"):
        move_mat[int(rec["row"]), int(rec["target_index"])] = float(rec["h104_move"])
    return selected, move_mat


def materialize(base_prob: np.ndarray, move_mat: np.ndarray) -> np.ndarray:
    return clip_prob(sigmoid(logit(base_prob) + move_mat))


def route_prediction(
    move_flat: np.ndarray,
    basis_fit_df: pd.DataFrame,
    basis_fit_moves: np.ndarray,
    route_fit: h100mod.RouteBasisFit,
) -> float:
    return h100mod.predict_candidate_delta(move_flat, basis_fit_df, basis_fit_moves, route_fit)


def evaluate_candidate(
    candidate_id: str,
    prob: np.ndarray,
    move_mat: np.ndarray,
    desired: np.ndarray,
    residual: np.ndarray,
    source_actions: pd.DataFrame,
    selected_cells: pd.DataFrame,
    cell: pd.DataFrame,
    sample: pd.DataFrame,
    h098_fit: h097mod.ResponseFit,
    route_fit: h100mod.RouteBasisFit,
    basis_fit_df: pd.DataFrame,
    basis_fit_moves: np.ndarray,
    bad_axes: pd.DataFrame,
    bad_moves: np.ndarray,
    good_moves: np.ndarray,
    spec: H104Spec,
    path: Path,
    projection_stats: dict[str, float],
) -> dict[str, object]:
    proxy = h097mod.H097Spec(
        name=spec.name,
        mode="toxic_axis_residual_transport",
        target_group=spec.source_group,
        k=spec.max_cells,
        alpha=spec.amp,
        cap=spec.move_cap,
        min_score=spec.min_abs_move,
        worldview=spec.worldview,
    )
    out = h097mod.evaluate_candidate(candidate_id, prob, move_mat, base_prob, selected_cells, cell, sample, h098_fit, proxy, path)
    axis = h102mod.cumulative_axis_metrics(move_mat.reshape(-1), bad_axes, bad_moves, good_moves)
    desired_axis = h102mod.cumulative_axis_metrics(desired, bad_axes, bad_moves, good_moves)
    residual_axis = h102mod.cumulative_axis_metrics(residual, bad_axes, bad_moves, good_moves)
    route_pred = route_prediction(move_mat.reshape(-1), basis_fit_df, basis_fit_moves, route_fit)
    desired_route_pred = route_prediction(desired, basis_fit_df, basis_fit_moves, route_fit)
    residual_route_pred = route_prediction(residual, basis_fit_df, basis_fit_moves, route_fit)
    out.update(axis)
    out.update({f"desired_{k}": v for k, v in desired_axis.items()})
    out.update({f"residual_{k}": v for k, v in residual_axis.items()})
    out.update(projection_stats)
    out["route_basis_pred_delta_vs_h057"] = route_pred
    out["desired_route_basis_pred_delta_vs_h057"] = desired_route_pred
    out["residual_route_basis_pred_delta_vs_h057"] = residual_route_pred
    out["route_basis_feature_set"] = route_fit.feature_set
    out["route_basis_k"] = route_fit.k_basis
    out["route_basis_alpha"] = route_fit.alpha
    out["source_actions"] = int(len(source_actions))
    out["source_action_rows"] = int(source_actions["row"].nunique()) if len(source_actions) else 0
    out["source_mean_h100_action_score"] = float(source_actions["h100_action_score"].mean()) if len(source_actions) else 0.0
    out["source_mean_h102_axis_score"] = float(source_actions["h102_axis_score"].mean()) if len(source_actions) else 0.0
    out["source_mean_route_delta"] = float(source_actions["h100_route_basis_pred_delta"].mean()) if len(source_actions) else 0.0
    out["desired_l2"] = float(np.linalg.norm(desired))
    out["residual_l2"] = float(np.linalg.norm(residual))
    out["submitted_l2"] = float(np.linalg.norm(move_mat.reshape(-1)))
    out["residual_keep_ratio"] = float(np.linalg.norm(residual) / (np.linalg.norm(desired) + 1.0e-12))
    out["submitted_keep_ratio"] = float(np.linalg.norm(move_mat.reshape(-1)) / (np.linalg.norm(desired) + 1.0e-12))
    out["h104_score"] = (
        330.0 * (-float(out["route_basis_pred_delta_vs_h057"]))
        + 90.0 * (-float(out["model_pred_delta_vs_h057"]))
        + 0.0040 * float(out["selected_cells"])
        + 0.0020 * float(out["source_actions"])
        + 0.18 * float(out["anti_h088_direction_rate"])
        + 0.16 * float(out["h057_positive_align_rate"])
        + 0.13 * float(out["selected_conflict_rate"])
        + 0.16 * max(float(out["h102_cum_good_bad_margin"]), 0.0)
        + 0.10 * max(-float(out["h102_cum_h088_axis_cos"]), 0.0)
        - 0.55 * max(float(out["h102_cum_bad_weighted_pos"]), 0.0)
        - 0.35 * max(float(out["h102_cum_bad_max_pos"]), 0.0)
        - 0.35 * max(float(out["h102_cum_h088_axis_cos"]), 0.0)
        - 0.22 * max(float(out["max_positive_bad_cosine"]), 0.0)
        - 22.0 * max(float(out["hard_diag_delta_vs_h057"]), 0.0)
        - 12.0 * max(float(out["posterior_delta_vs_h057"]), 0.0)
    )
    return out


def run() -> None:
    cleanup_previous_outputs()
    base = h085mod.load_sub(BASE_FILE)
    sample = base[KEYS].copy()
    global base_prob
    base_prob = base[TARGETS].to_numpy(dtype=np.float64)
    cell_raw = h097mod.ensure_h095_cell_table(sample, base_prob)
    cell, feature_sets = h097mod.add_context_features(cell_raw, sample)
    public = h097mod.load_public_moves(sample, base_prob)
    h098_scores, h098_pred_rows, h098_fit = h098mod.evaluate_weighted_models(public, cell, feature_sets)
    gradient = h097mod.response_gradient(cell, h098_fit)
    pool = h098mod.build_frontier_pool(cell, gradient)
    cell = cell.drop(columns=["h098_frontier_cell_score"], errors="ignore").merge(
        pool[["flat_index", "h098_frontier_cell_score"]],
        on="flat_index",
        how="left",
    )
    cell["h098_frontier_cell_score"] = cell["h098_frontier_cell_score"].fillna(0.0)
    routes = h099mod.load_routes()

    basis, cells_by_basis, basis_moves = h100mod.build_route_basis(routes, pool, cell, h098_fit, base_prob)
    model_scores, pred_rows, route_fit = h100mod.evaluate_route_basis_models(public, basis, basis_moves)
    basis_fit_df, basis_fit_moves = h100mod.selected_basis_for_fit(basis, basis_moves, route_fit)
    scored0 = h100mod.score_basis_actions(basis, basis_moves, basis_fit_df, basis_fit_moves, route_fit)
    bad_axes, bad_moves, good_axes, good_moves = h102mod.build_axes(public, sample, base_prob)
    scored_base = h102mod.add_axis_scores(scored0, basis_moves, bad_axes, bad_moves, good_axes, good_moves)

    candidate_rows = []
    selected_action_frames = []
    selected_cell_frames = []
    for spec in candidate_specs():
        source_actions, desired = build_desired_field(scored_base, cells_by_basis, spec, base_prob.shape)
        if source_actions.empty or np.linalg.norm(desired) <= 1.0e-12:
            continue
        residual1, stats1 = positive_bad_residualize(
            desired,
            bad_axes,
            bad_moves,
            spec.projection_strength,
            spec.projection_ridge,
            spec.h088_extra,
        )
        residual2, good_norm = good_anchor_boost(residual1, good_moves, spec.good_boost)
        residual, stats2 = positive_bad_residualize(
            residual2,
            bad_axes,
            bad_moves,
            spec.second_projection_strength,
            spec.projection_ridge * 1.4,
            spec.h088_extra * 0.35,
        )
        residual = np.clip(residual, -spec.move_cap, spec.move_cap)
        projection_stats = {
            "first_removed_norm": stats1["removed_norm"],
            "first_positive_coeff_count": stats1["positive_coeff_count"],
            "first_h088_removed": stats1["h088_removed"],
            "good_boost_norm": good_norm,
            "second_removed_norm": stats2["removed_norm"],
            "second_positive_coeff_count": stats2["positive_coeff_count"],
            "second_h088_removed": stats2["h088_removed"],
        }
        selected_cells, move_mat = decode_residual_cells(residual, cell, spec)
        if selected_cells.empty:
            continue
        axis = h102mod.cumulative_axis_metrics(move_mat.reshape(-1), bad_axes, bad_moves, good_moves)
        route_pred = route_prediction(move_mat.reshape(-1), basis_fit_df, basis_fit_moves, route_fit)
        h098_pred = h097mod.predict_candidate_delta(move_mat.reshape(-1), cell, h098_fit)
        if axis["h102_cum_bad_weighted_pos"] > spec.max_bad_weighted_pos:
            continue
        if axis["h102_cum_bad_max_pos"] > spec.max_bad_max_pos:
            continue
        if axis["h102_cum_h088_axis_cos"] > spec.max_h088_cos:
            continue
        if axis["h102_cum_good_bad_margin"] < spec.min_good_margin:
            continue
        if route_pred > spec.route_pred_cap:
            continue
        if h098_pred > spec.h098_pred_cap:
            continue
        prob = materialize(base_prob, move_mat)
        if int((np.abs(prob - base_prob) > TOL).sum()) == 0:
            continue
        hash_id = short_hash(prob)
        candidate_id = safe_id(f"h104_{spec.name}_{hash_id}", 128)
        path = OUT / f"submission_{candidate_id}.csv"
        h085mod.write_submission(sample, prob, path)
        row = evaluate_candidate(
            candidate_id,
            prob,
            move_mat,
            desired,
            residual,
            source_actions,
            selected_cells,
            cell,
            sample,
            h098_fit,
            route_fit,
            basis_fit_df,
            basis_fit_moves,
            bad_axes,
            bad_moves,
            good_moves,
            spec,
            path,
            projection_stats,
        )
        candidate_rows.append(row)
        source_actions = source_actions.copy()
        source_actions.insert(0, "candidate_id", candidate_id)
        selected_action_frames.append(source_actions)
        selected_cells = selected_cells.copy()
        selected_cells.insert(0, "candidate_id", candidate_id)
        selected_cell_frames.append(selected_cells)

    candidates = pd.DataFrame(candidate_rows)
    if candidates.empty:
        raise RuntimeError("no H104 candidates")
    candidates = candidates.sort_values(
        ["h104_score", "route_basis_pred_delta_vs_h057"],
        ascending=[False, True],
    ).reset_index(drop=True)
    selected = candidates.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"submission_h104_toxicresid_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)

    selected_model = model_scores.iloc[0].to_dict()
    decision = {
        "decision": "promote_h104_toxic_axis_residual_transport",
        "selected_candidate_id": selected["candidate_id"],
        "root_uploadsafe_path": str(root_path.resolve()),
        "worldview": selected["worldview"],
        "h098_feature_set": h098_fit.feature_set,
        "h098_alpha": h098_fit.alpha,
        **{f"route_basis_{k}": v for k, v in selected_model.items()},
        **selected,
        **{f"root_{key}": value for key, value in validation.items()},
    }

    public_out = public.drop(columns=["move_logit"]).copy()
    public_out["frontier_weight"] = h098mod.frontier_weights(public)
    public_out.to_csv(OUT / "h104_public_moves_weighted.csv", index=False)
    bad_axes.to_csv(OUT / "h104_bad_axes.csv", index=False)
    good_axes.to_csv(OUT / "h104_good_axes.csv", index=False)
    model_scores.to_csv(OUT / "h104_route_basis_model_scores.csv", index=False)
    pred_rows.to_csv(OUT / "h104_route_basis_loo_predictions.csv", index=False)
    h098_scores.to_csv(OUT / "h104_h098_frontier_model_scores.csv", index=False)
    h098_pred_rows.to_csv(OUT / "h104_h098_frontier_loo_predictions.csv", index=False)
    scored_base.to_csv(OUT / "h104_scored_route_actions_base.csv", index=False)
    candidates.to_csv(OUT / "h104_candidates.csv", index=False)
    pd.concat(selected_action_frames, ignore_index=True).to_csv(OUT / "h104_source_route_actions.csv", index=False)
    pd.concat(selected_cell_frames, ignore_index=True).to_csv(OUT / "h104_selected_cells.csv", index=False)
    pd.DataFrame([decision]).to_csv(OUT / "h104_decision.csv", index=False)

    cols = [
        "candidate_id",
        "spec_name",
        "source_actions",
        "selected_cells",
        "changed_rows_vs_h057",
        "route_basis_pred_delta_vs_h057",
        "desired_route_basis_pred_delta_vs_h057",
        "residual_route_basis_pred_delta_vs_h057",
        "model_pred_delta_vs_h057",
        "posterior_delta_vs_h057",
        "hard_diag_delta_vs_h057",
        "h102_cum_bad_weighted_pos",
        "h102_cum_bad_max_pos",
        "h102_cum_h088_axis_cos",
        "h102_cum_good_bad_margin",
        "residual_keep_ratio",
        "submitted_keep_ratio",
        "anti_h088_direction_rate",
        "h057_positive_align_rate",
        "selected_conflict_rate",
        "h104_score",
        "file",
    ]
    report = f"""# H104 Toxic-Axis Residual Transport HS-JEPA

Question: is the H100/H103 route-action signal useful only after removing the
positive component along known bad public axes?

Route-basis model scores:

{md_table(model_scores.head(12), 12)}

Candidates:

{md_table(candidates[cols], 20)}

Decision:

{md_table(pd.DataFrame([decision]), 1)}

Interpretation rule:

- If H104 beats H103/H100, action toxicity is a linear public-axis component and
  HS-JEPA should decode residualized route fields.
- If H103 beats H104, route-actions must be selected as discrete assignments;
  projecting the vector destroys row-target semantics.
- If H100 beats both, known bad axes are overlapping the real positive route
  law and should become soft diagnostics only.
"""
    (OUT / "h104_report.md").write_text(report, encoding="utf-8")

    print(f"selected={decision['selected_candidate_id']}")
    print(f"root={root_path}")
    print(candidates[cols].head(10).to_string(index=False))
    print("\nroute-basis model")
    print(model_scores.head(10).to_string(index=False))


if __name__ == "__main__":
    run()
