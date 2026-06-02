#!/usr/bin/env python3
"""H105: signed route-coefficient equation solver HS-JEPA.

H103 selects safe route-actions.  H104 residualizes a desired route field.
H105 tests the next bigger claim:

    route-actions are basis functions of a hidden public/private equation
    and the safe action is a signed coefficient solution, not a subset

The solver greedily searches positive and counter-route coefficients under
bad-axis, H088, good-anchor, H098, and route-basis constraints, then decodes
the resulting coefficient field back into row-target cells.
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
OUT = HITL / "h105_signed_route_coefficient_solver_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H104_PATH = HITL / "h104_toxic_axis_residual_transport_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h104mod", H104_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H104_PATH}")
h104mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h104mod
SPEC.loader.exec_module(h104mod)

h103mod = h104mod.h103mod
h102mod = h104mod.h102mod
h100mod = h104mod.h100mod
h099mod = h104mod.h099mod
h098mod = h104mod.h098mod
h097mod = h104mod.h097mod
h095mod = h104mod.h095mod
h085mod = h104mod.h085mod

TARGETS = h104mod.TARGETS
KEYS = h104mod.KEYS
BASE_FILE = h104mod.BASE_FILE
TOL = h104mod.TOL


@dataclass(frozen=True)
class H105Spec:
    name: str
    route_group: str
    pool_top: int
    max_steps: int
    max_cells: int
    max_rows: int
    max_per_subject: int
    q2_cap: int
    max_per_target: int
    plus_amp: float
    counter_amp: float
    move_cap: float
    min_abs_move: float
    max_bad_weighted_pos: float
    max_bad_max_pos: float
    max_h088_cos: float
    min_good_margin: float
    route_pred_cap: float
    h098_pred_cap: float
    min_objective_gain: float
    allow_counter: bool
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
    for path in OUT.glob("submission_h105_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h105_signedcoef_*_uploadsafe.csv"):
        path.unlink()


def candidate_specs() -> list[H105Spec]:
    return [
        H105Spec(
            name="signed_null_lagrange_c120_s42",
            route_group="signed_null",
            pool_top=120,
            max_steps=42,
            max_cells=120,
            max_rows=72,
            max_per_subject=12,
            q2_cap=12,
            max_per_target=30,
            plus_amp=0.84,
            counter_amp=0.36,
            move_cap=0.30,
            min_abs_move=0.011,
            max_bad_weighted_pos=0.012,
            max_bad_max_pos=0.055,
            max_h088_cos=-0.004,
            min_good_margin=0.010,
            route_pred_cap=-0.000260,
            h098_pred_cap=0.000070,
            min_objective_gain=0.0010,
            allow_counter=True,
            worldview="safe assignment is a signed coefficient solution in the bad-axis nullspace",
        ),
        H105Spec(
            name="broad_coeff_transport_c180_s58",
            route_group="broad_coeff",
            pool_top=180,
            max_steps=58,
            max_cells=180,
            max_rows=105,
            max_per_subject=17,
            q2_cap=28,
            max_per_target=42,
            plus_amp=0.68,
            counter_amp=0.26,
            move_cap=0.24,
            min_abs_move=0.010,
            max_bad_weighted_pos=0.024,
            max_bad_max_pos=0.090,
            max_h088_cos=0.000,
            min_good_margin=0.000,
            route_pred_cap=-0.000420,
            h098_pred_cap=0.000090,
            min_objective_gain=0.0007,
            allow_counter=True,
            worldview="public-safe field is a broad signed route-coefficient transport solution",
        ),
        H105Spec(
            name="anchor_tangent_coeff_c150_s50",
            route_group="anchor_tangent",
            pool_top=150,
            max_steps=50,
            max_cells=150,
            max_rows=92,
            max_per_subject=15,
            q2_cap=18,
            max_per_target=36,
            plus_amp=0.74,
            counter_amp=0.22,
            move_cap=0.26,
            min_abs_move=0.010,
            max_bad_weighted_pos=0.020,
            max_bad_max_pos=0.080,
            max_h088_cos=-0.001,
            min_good_margin=0.030,
            route_pred_cap=-0.000320,
            h098_pred_cap=0.000080,
            min_objective_gain=0.0008,
            allow_counter=True,
            worldview="safe signed coefficients must stay tangent to H057-positive anchor directions",
        ),
        H105Spec(
            name="objective_coeff_q2zero_c150_s52",
            route_group="objective_coeff",
            pool_top=150,
            max_steps=52,
            max_cells=150,
            max_rows=98,
            max_per_subject=16,
            q2_cap=0,
            max_per_target=42,
            plus_amp=0.78,
            counter_amp=0.18,
            move_cap=0.26,
            min_abs_move=0.010,
            max_bad_weighted_pos=0.022,
            max_bad_max_pos=0.085,
            max_h088_cos=0.000,
            min_good_margin=0.014,
            route_pred_cap=-0.000300,
            h098_pred_cap=0.000095,
            min_objective_gain=0.0007,
            allow_counter=True,
            worldview="objective Q3/S stage law is a signed coefficient field after Q2 spillover removal",
        ),
        H105Spec(
            name="discrete_plus_only_c90_s30",
            route_group="plus_only",
            pool_top=90,
            max_steps=30,
            max_cells=90,
            max_rows=60,
            max_per_subject=10,
            q2_cap=8,
            max_per_target=28,
            plus_amp=0.86,
            counter_amp=0.0,
            move_cap=0.30,
            min_abs_move=0.011,
            max_bad_weighted_pos=0.010,
            max_bad_max_pos=0.052,
            max_h088_cos=-0.004,
            min_good_margin=0.012,
            route_pred_cap=-0.000240,
            h098_pred_cap=0.000065,
            min_objective_gain=0.0008,
            allow_counter=False,
            worldview="if signed coefficients fail, a stricter plus-only coefficient solver may preserve route semantics",
        ),
    ]


def route_allowed(rec: dict[str, object], group: str) -> bool:
    basis_spec = str(rec["basis_spec"])
    route_targets = str(rec["route_targets"])
    route_name = str(rec["route_name"]).lower()
    if group == "signed_null":
        return float(rec["h102_axis_score"]) >= 0.45 and float(rec["selected_conflict_rate"]) >= 0.70
    if group == "broad_coeff":
        return float(rec["h100_action_score"]) >= 0.47 and float(rec["h100_route_basis_pred_delta"]) < 0.000035
    if group == "anchor_tangent":
        return float(rec["h102_good_bad_margin"]) > 0.004 or float(rec["h102_good_max_cos"]) > 0.020
    if group == "objective_coeff":
        return (
            basis_spec in {"basis_objective_a042", "basis_nonq2_positive_a038", "basis_tail_hybrid_a044"}
            or "S" in route_targets
            or "q3" in route_name
        ) and int(rec["Q2_cells"]) == 0
    if group == "plus_only":
        return float(rec["selected_conflict_rate"]) >= 0.92 and float(rec["h102_axis_score"]) >= 0.50
    raise ValueError(group)


def seed_priority(scored: pd.DataFrame) -> pd.DataFrame:
    out = scored.copy()
    out["h105_seed_priority"] = (
        0.32 * rank01(-out["h100_route_basis_pred_delta"].to_numpy(dtype=np.float64), high=True)
        + 0.22 * rank01(out["h100_action_score"].to_numpy(dtype=np.float64), high=True)
        + 0.18 * rank01(out["h102_axis_score"].to_numpy(dtype=np.float64), high=True)
        + 0.10 * out["selected_conflict_rate"].to_numpy(dtype=np.float64)
        + 0.08 * out["anti_h088_direction_rate"].to_numpy(dtype=np.float64)
        + 0.08 * out["h057_positive_align_rate"].to_numpy(dtype=np.float64)
        + 0.06 * rank01(out["h102_good_bad_margin"].to_numpy(dtype=np.float64), high=True)
        - 0.12 * rank01(out["h102_bad_weighted_pos"].to_numpy(dtype=np.float64), high=True)
        - 0.08 * out["mean_bad_same_rank"].to_numpy(dtype=np.float64)
    )
    return out.sort_values("h105_seed_priority", ascending=False).reset_index(drop=True)


def action_matrix(shape: tuple[int, int], cells: pd.DataFrame, move_col: str) -> np.ndarray:
    move = np.zeros(shape[0] * shape[1], dtype=np.float64)
    for rec in cells.to_dict("records"):
        move[int(rec["flat_index"])] += float(rec[move_col])
    return move


def route_pred(
    move_flat: np.ndarray,
    basis_fit_df: pd.DataFrame,
    basis_fit_moves: np.ndarray,
    route_fit: h100mod.RouteBasisFit,
) -> float:
    return h100mod.predict_candidate_delta(move_flat, basis_fit_df, basis_fit_moves, route_fit)


def h098_pred(move_flat: np.ndarray, cell: pd.DataFrame, h098_fit: h097mod.ResponseFit) -> float:
    return h097mod.predict_candidate_delta(move_flat, cell, h098_fit)


def lagrangian_score(
    move_flat: np.ndarray,
    bad_axes: pd.DataFrame,
    bad_moves: np.ndarray,
    good_moves: np.ndarray,
    cell: pd.DataFrame,
    h098_fit: h097mod.ResponseFit,
    basis_fit_df: pd.DataFrame,
    basis_fit_moves: np.ndarray,
    route_fit: h100mod.RouteBasisFit,
) -> dict[str, float]:
    axis = h102mod.cumulative_axis_metrics(move_flat, bad_axes, bad_moves, good_moves)
    rpred = route_pred(move_flat, basis_fit_df, basis_fit_moves, route_fit)
    cpred = h098_pred(move_flat, cell, h098_fit)
    score = (
        360.0 * (-rpred)
        + 95.0 * (-cpred)
        + 0.18 * max(axis["h102_cum_good_bad_margin"], 0.0)
        + 0.12 * max(-axis["h102_cum_h088_axis_cos"], 0.0)
        - 0.62 * max(axis["h102_cum_bad_weighted_pos"], 0.0)
        - 0.42 * max(axis["h102_cum_bad_max_pos"], 0.0)
        - 0.38 * max(axis["h102_cum_h088_axis_cos"], 0.0)
        - 0.012 * float(np.mean(np.abs(move_flat) > 1.0e-10))
        - 0.0015 * float(np.linalg.norm(move_flat))
    )
    return {
        **axis,
        "route_basis_pred_delta_vs_h057": rpred,
        "model_pred_delta_vs_h057": cpred,
        "h105_lagrangian": float(score),
    }


def make_terms(
    scored: pd.DataFrame,
    cells_by_basis: dict[str, pd.DataFrame],
    spec: H105Spec,
    shape: tuple[int, int],
) -> tuple[pd.DataFrame, np.ndarray]:
    rows = []
    moves = []
    base = seed_priority(scored)
    kept = []
    for rec in base.to_dict("records"):
        if not route_allowed(rec, spec.route_group):
            continue
        kept.append(rec)
        if len(kept) >= spec.pool_top:
            break
    for rec in kept:
        basis_id = str(rec["basis_id"])
        cells = cells_by_basis[basis_id].copy()
        cells["h105_term_move"] = cells["h100_direct_move"].to_numpy(dtype=np.float64) * spec.plus_amp
        plus = dict(rec)
        plus["term_id"] = safe_id(f"plus__{basis_id}", 128)
        plus["term_sign"] = 1
        plus["term_amp"] = spec.plus_amp
        plus["term_role"] = "plus"
        rows.append(plus)
        moves.append(action_matrix(shape, cells, "h105_term_move"))
        if spec.allow_counter:
            cells["h105_term_move"] = -cells["h100_direct_move"].to_numpy(dtype=np.float64) * spec.counter_amp
            minus = dict(rec)
            minus["term_id"] = safe_id(f"counter__{basis_id}", 128)
            minus["term_sign"] = -1
            minus["term_amp"] = spec.counter_amp
            minus["term_role"] = "counter"
            rows.append(minus)
            moves.append(action_matrix(shape, cells, "h105_term_move"))
    if not rows:
        return pd.DataFrame(), np.empty((0, shape[0] * shape[1]), dtype=np.float64)
    terms = pd.DataFrame(rows).reset_index(drop=True)
    move_matrix = np.vstack(moves).astype(np.float64)
    return terms, move_matrix


def term_constraints_ok(
    rec: dict[str, object],
    used_basis: set[str],
    used_rows: set[int],
    subject_counts: dict[str, int],
    spec: H105Spec,
) -> bool:
    basis_id = str(rec["basis_id"])
    row = int(rec["row"])
    subject = str(rec["subject_id"])
    if basis_id in used_basis:
        return False
    if row not in used_rows and len(used_rows) >= spec.max_rows:
        return False
    if row not in used_rows and subject_counts.get(subject, 0) + 1 > spec.max_per_subject:
        return False
    return True


def greedy_coefficients(
    terms: pd.DataFrame,
    term_moves: np.ndarray,
    spec: H105Spec,
    bad_axes: pd.DataFrame,
    bad_moves: np.ndarray,
    good_moves: np.ndarray,
    cell: pd.DataFrame,
    h098_fit: h097mod.ResponseFit,
    basis_fit_df: pd.DataFrame,
    basis_fit_moves: np.ndarray,
    route_fit: h100mod.RouteBasisFit,
) -> tuple[pd.DataFrame, np.ndarray, pd.DataFrame]:
    move = np.zeros(term_moves.shape[1], dtype=np.float64)
    current = lagrangian_score(move, bad_axes, bad_moves, good_moves, cell, h098_fit, basis_fit_df, basis_fit_moves, route_fit)
    selected = []
    trace_rows = []
    used_terms: set[int] = set()
    used_basis: set[str] = set()
    used_rows: set[int] = set()
    subject_counts: dict[str, int] = {}

    for step in range(spec.max_steps):
        best_i = None
        best_move = None
        best_metrics = None
        best_gain = -np.inf
        for i, rec in enumerate(terms.to_dict("records")):
            if i in used_terms:
                continue
            if not term_constraints_ok(rec, used_basis, used_rows, subject_counts, spec):
                continue
            tmp = np.clip(move + term_moves[i], -spec.move_cap, spec.move_cap)
            metrics = lagrangian_score(tmp, bad_axes, bad_moves, good_moves, cell, h098_fit, basis_fit_df, basis_fit_moves, route_fit)
            if metrics["h102_cum_bad_weighted_pos"] > spec.max_bad_weighted_pos:
                continue
            if metrics["h102_cum_bad_max_pos"] > spec.max_bad_max_pos:
                continue
            if metrics["h102_cum_h088_axis_cos"] > spec.max_h088_cos:
                continue
            if metrics["h102_cum_good_bad_margin"] < spec.min_good_margin:
                continue
            if metrics["route_basis_pred_delta_vs_h057"] > spec.route_pred_cap:
                continue
            if metrics["model_pred_delta_vs_h057"] > spec.h098_pred_cap:
                continue
            gain = float(metrics["h105_lagrangian"] - current["h105_lagrangian"])
            if gain > best_gain:
                best_i = i
                best_move = tmp
                best_metrics = metrics
                best_gain = gain
        if best_i is None or best_gain < spec.min_objective_gain:
            break
        rec = terms.iloc[best_i].to_dict()
        used_terms.add(best_i)
        used_basis.add(str(rec["basis_id"]))
        row = int(rec["row"])
        subject = str(rec["subject_id"])
        if row not in used_rows:
            used_rows.add(row)
            subject_counts[subject] = subject_counts.get(subject, 0) + 1
        selected.append({**rec, "greedy_step": step, "objective_gain": best_gain, **best_metrics})
        trace_rows.append({"step": step, "selected_term": rec["term_id"], "gain": best_gain, **best_metrics})
        move = best_move
        current = best_metrics
    return pd.DataFrame(selected), move, pd.DataFrame(trace_rows)


def decode_cells(move_flat: np.ndarray, cell: pd.DataFrame, spec: H105Spec) -> tuple[pd.DataFrame, np.ndarray]:
    ordered = cell.sort_values("flat_index").reset_index(drop=True).copy()
    move = np.clip(move_flat.copy(), -spec.move_cap, spec.move_cap)
    sign = np.sign(move)
    h088_sign = np.sign(ordered["h088_logit_move"].to_numpy(dtype=np.float64))
    h057_sign = np.sign(ordered["h057_positive_logit_move"].to_numpy(dtype=np.float64))
    anti_h088 = (sign * h088_sign < 0).astype(float)
    align_h057 = (
        (sign * h057_sign > 0)
        & (ordered["h057_positive_weight"].to_numpy(dtype=np.float64) > 0)
    ).astype(float)
    quality = (
        0.32
        + 0.24 * anti_h088
        + 0.20 * align_h057
        + 0.18 * ordered["h057_h088_anti_conflict"].to_numpy(dtype=np.float64)
        + 0.12 * ordered["h095_safe_cell_score"].to_numpy(dtype=np.float64)
        + 0.10 * ordered["h098_frontier_cell_score"].to_numpy(dtype=np.float64)
        - 0.16 * ordered["h080_bad_same_rank"].to_numpy(dtype=np.float64)
        - 0.08 * ordered["is_h050_null"].to_numpy(dtype=np.float64)
    )
    ordered["h105_move"] = move
    ordered["h105_abs_move"] = np.abs(move)
    ordered["h105_decode_score"] = ordered["h105_abs_move"] * quality
    ordered = ordered[ordered["h105_abs_move"].to_numpy(dtype=np.float64) >= spec.min_abs_move].copy()
    ordered = ordered.sort_values("h105_decode_score", ascending=False)
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
        if row not in used_rows and subject_counts.get(subject, 0) + 1 > spec.max_per_subject:
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
    selected["h097_move_col"] = "h105_move"
    move_mat = np.zeros((250, len(TARGETS)), dtype=np.float64)
    for rec in selected.to_dict("records"):
        move_mat[int(rec["row"]), int(rec["target_index"])] = float(rec["h105_move"])
    return selected, move_mat


def materialize(base_prob: np.ndarray, move_mat: np.ndarray) -> np.ndarray:
    return clip_prob(sigmoid(logit(base_prob) + move_mat))


def evaluate_candidate(
    candidate_id: str,
    prob: np.ndarray,
    move_mat: np.ndarray,
    coeff_move: np.ndarray,
    selected_terms: pd.DataFrame,
    selected_cells: pd.DataFrame,
    cell: pd.DataFrame,
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    h098_fit: h097mod.ResponseFit,
    route_fit: h100mod.RouteBasisFit,
    basis_fit_df: pd.DataFrame,
    basis_fit_moves: np.ndarray,
    bad_axes: pd.DataFrame,
    bad_moves: np.ndarray,
    good_moves: np.ndarray,
    spec: H105Spec,
    path: Path,
) -> dict[str, object]:
    proxy = h097mod.H097Spec(
        name=spec.name,
        mode="signed_route_coefficient_solver",
        target_group=spec.route_group,
        k=spec.max_cells,
        alpha=spec.plus_amp,
        cap=spec.move_cap,
        min_score=spec.min_abs_move,
        worldview=spec.worldview,
    )
    out = h097mod.evaluate_candidate(candidate_id, prob, move_mat, base_prob, selected_cells, cell, sample, h098_fit, proxy, path)
    axis = h102mod.cumulative_axis_metrics(move_mat.reshape(-1), bad_axes, bad_moves, good_moves)
    coeff_axis = h102mod.cumulative_axis_metrics(coeff_move, bad_axes, bad_moves, good_moves)
    out.update(axis)
    out.update({f"coeff_{k}": v for k, v in coeff_axis.items()})
    coeff_route = route_pred(coeff_move, basis_fit_df, basis_fit_moves, route_fit)
    submitted_route = route_pred(move_mat.reshape(-1), basis_fit_df, basis_fit_moves, route_fit)
    out["route_basis_pred_delta_vs_h057"] = submitted_route
    out["coeff_route_basis_pred_delta_vs_h057"] = coeff_route
    out["coeff_model_pred_delta_vs_h057"] = h098_pred(coeff_move, cell, h098_fit)
    out["route_basis_feature_set"] = route_fit.feature_set
    out["route_basis_k"] = route_fit.k_basis
    out["route_basis_alpha"] = route_fit.alpha
    out["selected_terms"] = int(len(selected_terms))
    out["plus_terms"] = int(selected_terms["term_role"].astype(str).eq("plus").sum()) if len(selected_terms) else 0
    out["counter_terms"] = int(selected_terms["term_role"].astype(str).eq("counter").sum()) if len(selected_terms) else 0
    out["term_rows"] = int(selected_terms["row"].nunique()) if len(selected_terms) else 0
    out["term_mean_h100_action_score"] = float(selected_terms["h100_action_score"].mean()) if len(selected_terms) else 0.0
    out["term_mean_h102_axis_score"] = float(selected_terms["h102_axis_score"].mean()) if len(selected_terms) else 0.0
    out["term_mean_route_delta"] = float(selected_terms["h100_route_basis_pred_delta"].mean()) if len(selected_terms) else 0.0
    out["coeff_l2"] = float(np.linalg.norm(coeff_move))
    out["submitted_l2"] = float(np.linalg.norm(move_mat.reshape(-1)))
    out["submitted_keep_ratio"] = float(np.linalg.norm(move_mat.reshape(-1)) / (np.linalg.norm(coeff_move) + 1.0e-12))
    out["h105_score"] = (
        335.0 * (-float(out["route_basis_pred_delta_vs_h057"]))
        + 88.0 * (-float(out["model_pred_delta_vs_h057"]))
        + 0.0032 * float(out["selected_cells"])
        + 0.0025 * float(out["selected_terms"])
        + 0.18 * float(out["anti_h088_direction_rate"])
        + 0.16 * float(out["h057_positive_align_rate"])
        + 0.11 * float(out["selected_conflict_rate"])
        + 0.16 * max(float(out["h102_cum_good_bad_margin"]), 0.0)
        + 0.10 * max(-float(out["h102_cum_h088_axis_cos"]), 0.0)
        - 0.58 * max(float(out["h102_cum_bad_weighted_pos"]), 0.0)
        - 0.36 * max(float(out["h102_cum_bad_max_pos"]), 0.0)
        - 0.35 * max(float(out["h102_cum_h088_axis_cos"]), 0.0)
        - 0.25 * max(float(out["max_positive_bad_cosine"]), 0.0)
        - 22.0 * max(float(out["hard_diag_delta_vs_h057"]), 0.0)
        - 12.0 * max(float(out["posterior_delta_vs_h057"]), 0.0)
    )
    return out


def run() -> None:
    cleanup_previous_outputs()
    base = h085mod.load_sub(BASE_FILE)
    sample = base[KEYS].copy()
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
    selected_term_frames = []
    selected_cell_frames = []
    trace_frames = []
    for spec in candidate_specs():
        terms, term_moves = make_terms(scored_base, cells_by_basis, spec, base_prob.shape)
        if terms.empty:
            continue
        selected_terms, coeff_move, trace = greedy_coefficients(
            terms,
            term_moves,
            spec,
            bad_axes,
            bad_moves,
            good_moves,
            cell,
            h098_fit,
            basis_fit_df,
            basis_fit_moves,
            route_fit,
        )
        if selected_terms.empty:
            continue
        selected_cells, move_mat = decode_cells(coeff_move, cell, spec)
        if selected_cells.empty:
            continue
        axis = h102mod.cumulative_axis_metrics(move_mat.reshape(-1), bad_axes, bad_moves, good_moves)
        rpred = route_pred(move_mat.reshape(-1), basis_fit_df, basis_fit_moves, route_fit)
        cpred = h098_pred(move_mat.reshape(-1), cell, h098_fit)
        if axis["h102_cum_bad_weighted_pos"] > spec.max_bad_weighted_pos:
            continue
        if axis["h102_cum_bad_max_pos"] > spec.max_bad_max_pos:
            continue
        if axis["h102_cum_h088_axis_cos"] > spec.max_h088_cos:
            continue
        if axis["h102_cum_good_bad_margin"] < spec.min_good_margin:
            continue
        if rpred > spec.route_pred_cap:
            continue
        if cpred > spec.h098_pred_cap:
            continue
        prob = materialize(base_prob, move_mat)
        if int((np.abs(prob - base_prob) > TOL).sum()) == 0:
            continue
        hash_id = short_hash(prob)
        candidate_id = safe_id(f"h105_{spec.name}_{hash_id}", 128)
        path = OUT / f"submission_{candidate_id}.csv"
        h085mod.write_submission(sample, prob, path)
        row = evaluate_candidate(
            candidate_id,
            prob,
            move_mat,
            coeff_move,
            selected_terms,
            selected_cells,
            cell,
            sample,
            base_prob,
            h098_fit,
            route_fit,
            basis_fit_df,
            basis_fit_moves,
            bad_axes,
            bad_moves,
            good_moves,
            spec,
            path,
        )
        candidate_rows.append(row)
        selected_terms = selected_terms.copy()
        selected_terms.insert(0, "candidate_id", candidate_id)
        selected_term_frames.append(selected_terms)
        selected_cells = selected_cells.copy()
        selected_cells.insert(0, "candidate_id", candidate_id)
        selected_cell_frames.append(selected_cells)
        trace = trace.copy()
        trace.insert(0, "candidate_id", candidate_id)
        trace_frames.append(trace)

    candidates = pd.DataFrame(candidate_rows)
    if candidates.empty:
        raise RuntimeError("no H105 candidates")
    candidates = candidates.sort_values(["h105_score", "route_basis_pred_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True)
    selected = candidates.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"submission_h105_signedcoef_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)

    selected_model = model_scores.iloc[0].to_dict()
    decision = {
        "decision": "promote_h105_signed_route_coefficient_solver",
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
    public_out.to_csv(OUT / "h105_public_moves_weighted.csv", index=False)
    bad_axes.to_csv(OUT / "h105_bad_axes.csv", index=False)
    good_axes.to_csv(OUT / "h105_good_axes.csv", index=False)
    model_scores.to_csv(OUT / "h105_route_basis_model_scores.csv", index=False)
    pred_rows.to_csv(OUT / "h105_route_basis_loo_predictions.csv", index=False)
    h098_scores.to_csv(OUT / "h105_h098_frontier_model_scores.csv", index=False)
    h098_pred_rows.to_csv(OUT / "h105_h098_frontier_loo_predictions.csv", index=False)
    scored_base.to_csv(OUT / "h105_scored_route_actions_base.csv", index=False)
    candidates.to_csv(OUT / "h105_candidates.csv", index=False)
    pd.concat(selected_term_frames, ignore_index=True).to_csv(OUT / "h105_selected_terms.csv", index=False)
    pd.concat(selected_cell_frames, ignore_index=True).to_csv(OUT / "h105_selected_cells.csv", index=False)
    pd.concat(trace_frames, ignore_index=True).to_csv(OUT / "h105_greedy_trace.csv", index=False)
    pd.DataFrame([decision]).to_csv(OUT / "h105_decision.csv", index=False)

    cols = [
        "candidate_id",
        "spec_name",
        "selected_terms",
        "plus_terms",
        "counter_terms",
        "selected_cells",
        "changed_rows_vs_h057",
        "route_basis_pred_delta_vs_h057",
        "coeff_route_basis_pred_delta_vs_h057",
        "model_pred_delta_vs_h057",
        "posterior_delta_vs_h057",
        "hard_diag_delta_vs_h057",
        "h102_cum_bad_weighted_pos",
        "h102_cum_bad_max_pos",
        "h102_cum_h088_axis_cos",
        "h102_cum_good_bad_margin",
        "submitted_keep_ratio",
        "anti_h088_direction_rate",
        "h057_positive_align_rate",
        "selected_conflict_rate",
        "h105_score",
        "file",
    ]
    report = f"""# H105 Signed Route-Coefficient Solver HS-JEPA

Question: should route-actions be treated as signed basis functions of a
public/private equation instead of discrete actions?

Route-basis model scores:

{md_table(model_scores.head(12), 12)}

Candidates:

{md_table(candidates[cols], 20)}

Decision:

{md_table(pd.DataFrame([decision]), 1)}

Interpretation rule:

- If H105 beats H103/H104, HS-JEPA's action decoder should solve signed
  coefficients over route-action bases.
- If H103 beats H105, route-action signs and magnitudes are semantic and should
  stay discrete.
- If H104 beats H105, projection/transport is useful but signed coefficients
  overfit the public equation.
"""
    (OUT / "h105_report.md").write_text(report, encoding="utf-8")

    print(f"selected={decision['selected_candidate_id']}")
    print(f"root={root_path}")
    print(candidates[cols].head(10).to_string(index=False))
    print("\nroute-basis model")
    print(model_scores.head(10).to_string(index=False))


if __name__ == "__main__":
    run()
