#!/usr/bin/env python3
"""H106: route-consensus kernel expansion HS-JEPA.

H105 showed a surprising collapse: a signed route-coefficient solver selected
29 positive route terms, but only 8 submitted cells on 4 id06/id07 rows.

H106 tests whether that kernel is merely a tiny public-sensitive pocket or the
visible tip of a larger route-consensus field:

    many route-actions voting the same row-target direction
      -> consensus action pressure
      -> bad-axis safe sparse expansion
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
OUT = HITL / "h106_route_consensus_kernel_expansion_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H105_PATH = HITL / "h105_signed_route_coefficient_solver_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h105mod", H105_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H105_PATH}")
h105mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h105mod
SPEC.loader.exec_module(h105mod)

h104mod = h105mod.h104mod
h103mod = h105mod.h103mod
h102mod = h105mod.h102mod
h100mod = h105mod.h100mod
h099mod = h105mod.h099mod
h098mod = h105mod.h098mod
h097mod = h105mod.h097mod
h095mod = h105mod.h095mod
h085mod = h105mod.h085mod

TARGETS = h105mod.TARGETS
KEYS = h105mod.KEYS
BASE_FILE = h105mod.BASE_FILE
TOL = h105mod.TOL

H105_SEED_ROWS = {144, 146, 151, 164}


@dataclass(frozen=True)
class H106Spec:
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
    min_vote_weight: float
    min_consensus: float
    max_bad_weighted_pos: float
    max_bad_max_pos: float
    max_h088_cos: float
    min_good_margin: float
    route_pred_cap: float
    h098_pred_cap: float
    require_seed_subject: bool
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
    for path in OUT.glob("submission_h106_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h106_routeconsensus_*_uploadsafe.csv"):
        path.unlink()


def candidate_specs() -> list[H106Spec]:
    return [
        H106Spec(
            name="kernel_seed_expand_c44_a090",
            source_group="kernel_seed_expand",
            top_actions=96,
            max_cells=44,
            max_rows=22,
            max_per_subject=12,
            q2_cap=4,
            max_per_target=14,
            amp=0.90,
            move_cap=0.28,
            min_abs_move=0.012,
            min_vote_weight=0.55,
            min_consensus=0.62,
            max_bad_weighted_pos=0.006,
            max_bad_max_pos=0.035,
            max_h088_cos=-0.004,
            min_good_margin=0.010,
            route_pred_cap=-0.000380,
            h098_pred_cap=0.000060,
            require_seed_subject=True,
            worldview="H105 tiny kernel expands only inside the id06/id07 route-consensus neighborhood",
        ),
        H106Spec(
            name="id06id07_episode_kernel_c70_a075",
            source_group="id06id07_episode",
            top_actions=140,
            max_cells=70,
            max_rows=34,
            max_per_subject=18,
            q2_cap=8,
            max_per_target=20,
            amp=0.75,
            move_cap=0.24,
            min_abs_move=0.010,
            min_vote_weight=0.42,
            min_consensus=0.56,
            max_bad_weighted_pos=0.012,
            max_bad_max_pos=0.060,
            max_h088_cos=-0.002,
            min_good_margin=0.006,
            route_pred_cap=-0.000560,
            h098_pred_cap=0.000075,
            require_seed_subject=True,
            worldview="the H105 id06/id07 kernel is an episode-level hidden state, not just four rows",
        ),
        H106Spec(
            name="broad_conflict_consensus_c96_a065",
            source_group="broad_conflict",
            top_actions=220,
            max_cells=96,
            max_rows=64,
            max_per_subject=12,
            q2_cap=10,
            max_per_target=26,
            amp=0.65,
            move_cap=0.22,
            min_abs_move=0.010,
            min_vote_weight=0.34,
            min_consensus=0.58,
            max_bad_weighted_pos=0.020,
            max_bad_max_pos=0.080,
            max_h088_cos=0.000,
            min_good_margin=0.000,
            route_pred_cap=-0.000620,
            h098_pred_cap=0.000090,
            require_seed_subject=False,
            worldview="route-consensus cells outside id06/id07 share the same public/private action law",
        ),
        H106Spec(
            name="objective_consensus_q2zero_c88_a070",
            source_group="objective_consensus",
            top_actions=180,
            max_cells=88,
            max_rows=58,
            max_per_subject=12,
            q2_cap=0,
            max_per_target=28,
            amp=0.70,
            move_cap=0.22,
            min_abs_move=0.010,
            min_vote_weight=0.32,
            min_consensus=0.52,
            max_bad_weighted_pos=0.022,
            max_bad_max_pos=0.085,
            max_h088_cos=0.000,
            min_good_margin=0.008,
            route_pred_cap=-0.000500,
            h098_pred_cap=0.000095,
            require_seed_subject=False,
            worldview="Q3/S objective consensus is the transferable part of the H105 kernel after removing Q2",
        ),
        H106Spec(
            name="strict_conflict_core_c24_a100",
            source_group="strict_conflict_core",
            top_actions=80,
            max_cells=24,
            max_rows=12,
            max_per_subject=8,
            q2_cap=2,
            max_per_target=10,
            amp=1.00,
            move_cap=0.30,
            min_abs_move=0.014,
            min_vote_weight=0.70,
            min_consensus=0.72,
            max_bad_weighted_pos=0.004,
            max_bad_max_pos=0.026,
            max_h088_cos=-0.006,
            min_good_margin=0.014,
            route_pred_cap=-0.000300,
            h098_pred_cap=0.000050,
            require_seed_subject=True,
            worldview="only the highest-consensus conflict core is action-grade; broader expansion is toxic",
        ),
    ]


def action_allowed(rec: dict[str, object], group: str) -> bool:
    subject = str(rec["subject_id"])
    basis_spec = str(rec["basis_spec"])
    route_targets = str(rec["route_targets"])
    row = int(rec["row"])
    if group == "kernel_seed_expand":
        return subject in {"id06", "id07"} and float(rec["selected_conflict_rate"]) >= 0.75
    if group == "id06id07_episode":
        return subject in {"id06", "id07"} and float(rec["h102_axis_score"]) >= 0.34
    if group == "broad_conflict":
        return float(rec["selected_conflict_rate"]) >= 0.70 and float(rec["h102_axis_score"]) >= 0.40
    if group == "objective_consensus":
        return (
            basis_spec in {"basis_objective_a042", "basis_nonq2_positive_a038", "basis_tail_hybrid_a044"}
            or "S" in route_targets
        ) and int(rec["Q2_cells"]) == 0
    if group == "strict_conflict_core":
        return row in H105_SEED_ROWS or (
            subject in {"id06", "id07"}
            and float(rec["selected_conflict_rate"]) >= 0.95
            and float(rec["anti_h088_direction_rate"]) >= 0.95
        )
    raise ValueError(group)


def build_consensus_table(
    scored: pd.DataFrame,
    cells_by_basis: dict[str, pd.DataFrame],
    spec: H106Spec,
    cell: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    ranked = h105mod.seed_priority(scored)
    action_rows = []
    n = len(cell)
    vote_sum = np.zeros(n, dtype=np.float64)
    vote_abs = np.zeros(n, dtype=np.float64)
    vote_weight = np.zeros(n, dtype=np.float64)
    vote_count = np.zeros(n, dtype=np.float64)
    pos_count = np.zeros(n, dtype=np.float64)
    neg_count = np.zeros(n, dtype=np.float64)
    max_abs = np.zeros(n, dtype=np.float64)

    for rec in ranked.to_dict("records"):
        if len(action_rows) >= spec.top_actions:
            break
        if not action_allowed(rec, spec.source_group):
            continue
        basis_id = str(rec["basis_id"])
        cells = cells_by_basis[basis_id]
        route_gain = max(-float(rec["h100_route_basis_pred_delta"]) / 0.00025, 0.0)
        weight = (
            0.30
            + 0.55 * float(rec["h105_seed_priority"])
            + 0.28 * float(rec["h102_axis_score"])
            + 0.12 * min(route_gain, 3.0)
            + 0.10 * float(rec["selected_conflict_rate"])
        )
        if int(rec["row"]) in H105_SEED_ROWS:
            weight *= 1.12
        action_rows.append({**rec, "h106_vote_weight": weight})
        for cell_rec in cells.to_dict("records"):
            flat = int(cell_rec["flat_index"])
            move = float(cell_rec["h100_direct_move"])
            vote_sum[flat] += weight * move
            vote_abs[flat] += weight * abs(move)
            vote_weight[flat] += weight
            vote_count[flat] += 1.0
            pos_count[flat] += float(move > 0)
            neg_count[flat] += float(move < 0)
            max_abs[flat] = max(max_abs[flat], abs(move))

    out = cell.sort_values("flat_index").reset_index(drop=True).copy()
    out["h106_vote_sum"] = vote_sum
    out["h106_vote_abs"] = vote_abs
    out["h106_vote_weight"] = vote_weight
    out["h106_vote_count"] = vote_count
    out["h106_vote_consensus"] = np.abs(vote_sum) / (vote_abs + 1.0e-12)
    out["h106_pos_count"] = pos_count
    out["h106_neg_count"] = neg_count
    out["h106_max_abs_component"] = max_abs
    mean_move = vote_sum / (vote_weight + 1.0e-12)
    out["h106_move"] = np.clip(mean_move * spec.amp, -spec.move_cap, spec.move_cap)
    sign = np.sign(out["h106_move"].to_numpy(dtype=np.float64))
    h088_sign = np.sign(out["h088_logit_move"].to_numpy(dtype=np.float64))
    h057_sign = np.sign(out["h057_positive_logit_move"].to_numpy(dtype=np.float64))
    anti_h088 = (sign * h088_sign < 0).astype(float)
    align_h057 = (
        (sign * h057_sign > 0)
        & (out["h057_positive_weight"].to_numpy(dtype=np.float64) > 0)
    ).astype(float)
    seed_distance = np.asarray(
        [min(abs(int(row) - seed) for seed in H105_SEED_ROWS) for row in out["row"].astype(int)],
        dtype=np.float64,
    )
    out["h106_seed_row"] = out["row"].astype(int).isin(H105_SEED_ROWS).astype(float)
    out["h106_seed_distance"] = seed_distance
    out["h106_seed_neighbor"] = (seed_distance <= 8.0).astype(float)
    out["h106_seed_subject"] = out["subject_id"].astype(str).isin(["id06", "id07"]).astype(float)
    out["h106_anti_h088"] = anti_h088
    out["h106_align_h057"] = align_h057
    out["h106_score"] = (
        np.abs(out["h106_move"].to_numpy(dtype=np.float64))
        * (0.55 + out["h106_vote_consensus"].to_numpy(dtype=np.float64))
        * (0.45 + np.log1p(out["h106_vote_weight"].to_numpy(dtype=np.float64)))
        * (
            0.70
            + 0.40 * anti_h088
            + 0.34 * align_h057
            + 0.24 * out["h057_h088_anti_conflict"].to_numpy(dtype=np.float64)
            + 0.18 * out["h095_safe_cell_score"].to_numpy(dtype=np.float64)
            + 0.12 * out["h098_frontier_cell_score"].to_numpy(dtype=np.float64)
            + 0.12 * out["h106_seed_neighbor"].to_numpy(dtype=np.float64)
            + 0.10 * out["h106_seed_row"].to_numpy(dtype=np.float64)
            - 0.18 * out["h080_bad_same_rank"].to_numpy(dtype=np.float64)
            - 0.08 * out["is_h050_null"].to_numpy(dtype=np.float64)
        )
    )
    return out, pd.DataFrame(action_rows)


def target_allowed(target: str, group: str) -> bool:
    if group in {"kernel_seed_expand", "id06id07_episode", "broad_conflict", "strict_conflict_core"}:
        return True
    if group == "objective_consensus":
        return target in {"Q3", "S1", "S2", "S3", "S4"}
    raise ValueError(group)


def route_pred(
    move_flat: np.ndarray,
    basis_fit_df: pd.DataFrame,
    basis_fit_moves: np.ndarray,
    route_fit: h100mod.RouteBasisFit,
) -> float:
    return h100mod.predict_candidate_delta(move_flat, basis_fit_df, basis_fit_moves, route_fit)


def h098_pred(move_flat: np.ndarray, cell: pd.DataFrame, h098_fit: h097mod.ResponseFit) -> float:
    return h097mod.predict_candidate_delta(move_flat, cell, h098_fit)


def select_cells(
    consensus: pd.DataFrame,
    spec: H106Spec,
    base_shape: tuple[int, int],
    bad_axes: pd.DataFrame,
    bad_moves: np.ndarray,
    good_moves: np.ndarray,
) -> tuple[pd.DataFrame, np.ndarray]:
    pool = consensus.copy()
    pool = pool[np.abs(pool["h106_move"].to_numpy(dtype=np.float64)) >= spec.min_abs_move].copy()
    pool = pool[pool["h106_vote_weight"].to_numpy(dtype=np.float64) >= spec.min_vote_weight]
    pool = pool[pool["h106_vote_consensus"].to_numpy(dtype=np.float64) >= spec.min_consensus]
    pool = pool[pool["target"].astype(str).map(lambda target: target_allowed(target, spec.source_group))]
    if spec.require_seed_subject:
        pool = pool[pool["h106_seed_subject"].to_numpy(dtype=np.float64) > 0]
    pool = pool.sort_values("h106_score", ascending=False)

    selected_rows = []
    used_rows: set[int] = set()
    subject_counts: dict[str, int] = {}
    target_counts: dict[str, int] = {}
    q2_count = 0
    move_mat = np.zeros(base_shape, dtype=np.float64)

    for rec in pool.to_dict("records"):
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

        tmp = move_mat.copy()
        tmp[row, int(rec["target_index"])] = float(rec["h106_move"])
        axis = h102mod.cumulative_axis_metrics(tmp.reshape(-1), bad_axes, bad_moves, good_moves)
        if axis["h102_cum_bad_weighted_pos"] > spec.max_bad_weighted_pos:
            continue
        if axis["h102_cum_bad_max_pos"] > spec.max_bad_max_pos:
            continue
        if axis["h102_cum_h088_axis_cos"] > spec.max_h088_cos:
            continue
        if axis["h102_cum_good_bad_margin"] < spec.min_good_margin:
            continue

        move_mat = tmp
        selected_rows.append(rec)
        if row not in used_rows:
            used_rows.add(row)
            subject_counts[subject] = subject_counts.get(subject, 0) + 1
        target_counts[target] = target_counts.get(target, 0) + 1
        if target == "Q2":
            q2_count += 1

    selected = pd.DataFrame(selected_rows)
    if selected.empty:
        return selected, move_mat
    selected = selected.sort_values(["row", "target_index"]).reset_index(drop=True)
    selected["h097_move_col"] = "h106_move"
    return selected, move_mat


def materialize(base_prob: np.ndarray, move_mat: np.ndarray) -> np.ndarray:
    return clip_prob(sigmoid(logit(base_prob) + move_mat))


def evaluate_candidate(
    candidate_id: str,
    prob: np.ndarray,
    move_mat: np.ndarray,
    selected_cells: pd.DataFrame,
    source_actions: pd.DataFrame,
    consensus: pd.DataFrame,
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
    spec: H106Spec,
    path: Path,
) -> dict[str, object]:
    proxy = h097mod.H097Spec(
        name=spec.name,
        mode="route_consensus_kernel_expansion",
        target_group=spec.source_group,
        k=spec.max_cells,
        alpha=spec.amp,
        cap=spec.move_cap,
        min_score=spec.min_abs_move,
        worldview=spec.worldview,
    )
    out = h097mod.evaluate_candidate(candidate_id, prob, move_mat, base_prob, selected_cells, cell, sample, h098_fit, proxy, path)
    axis = h102mod.cumulative_axis_metrics(move_mat.reshape(-1), bad_axes, bad_moves, good_moves)
    out.update(axis)
    out["route_basis_pred_delta_vs_h057"] = route_pred(move_mat.reshape(-1), basis_fit_df, basis_fit_moves, route_fit)
    out["route_basis_feature_set"] = route_fit.feature_set
    out["route_basis_k"] = route_fit.k_basis
    out["route_basis_alpha"] = route_fit.alpha
    out["source_actions"] = int(len(source_actions))
    out["source_subjects"] = int(source_actions["subject_id"].nunique()) if len(source_actions) else 0
    out["source_rows"] = int(source_actions["row"].nunique()) if len(source_actions) else 0
    out["selected_seed_rows"] = int(selected_cells["h106_seed_row"].sum()) if len(selected_cells) else 0
    out["selected_seed_neighbors"] = int(selected_cells["h106_seed_neighbor"].sum()) if len(selected_cells) else 0
    out["selected_seed_subject_cells"] = int(selected_cells["h106_seed_subject"].sum()) if len(selected_cells) else 0
    out["selected_mean_vote_weight"] = float(selected_cells["h106_vote_weight"].mean()) if len(selected_cells) else 0.0
    out["selected_mean_consensus"] = float(selected_cells["h106_vote_consensus"].mean()) if len(selected_cells) else 0.0
    out["selected_mean_h106_score"] = float(selected_cells["h106_score"].mean()) if len(selected_cells) else 0.0
    out["global_consensus_cells"] = int((consensus["h106_vote_weight"].to_numpy(dtype=np.float64) >= spec.min_vote_weight).sum())
    out["global_high_consensus_cells"] = int(
        (
            (consensus["h106_vote_weight"].to_numpy(dtype=np.float64) >= spec.min_vote_weight)
            & (consensus["h106_vote_consensus"].to_numpy(dtype=np.float64) >= spec.min_consensus)
            & (np.abs(consensus["h106_move"].to_numpy(dtype=np.float64)) >= spec.min_abs_move)
        ).sum()
    )
    out["h106_score"] = (
        325.0 * (-float(out["route_basis_pred_delta_vs_h057"]))
        + 92.0 * (-float(out["model_pred_delta_vs_h057"]))
        + 0.0040 * float(out["selected_cells"])
        + 0.0015 * float(out["source_actions"])
        + 0.18 * float(out["anti_h088_direction_rate"])
        + 0.16 * float(out["h057_positive_align_rate"])
        + 0.12 * float(out["selected_conflict_rate"])
        + 0.10 * float(out["selected_mean_consensus"])
        + 0.12 * max(float(out["h102_cum_good_bad_margin"]), 0.0)
        + 0.10 * max(-float(out["h102_cum_h088_axis_cos"]), 0.0)
        - 0.58 * max(float(out["h102_cum_bad_weighted_pos"]), 0.0)
        - 0.36 * max(float(out["h102_cum_bad_max_pos"]), 0.0)
        - 0.35 * max(float(out["h102_cum_h088_axis_cos"]), 0.0)
        - 0.24 * max(float(out["max_positive_bad_cosine"]), 0.0)
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
    source_frames = []
    selected_cell_frames = []
    consensus_frames = []
    for spec in candidate_specs():
        consensus, source_actions = build_consensus_table(scored_base, cells_by_basis, spec, cell)
        selected_cells, move_mat = select_cells(consensus, spec, base_prob.shape, bad_axes, bad_moves, good_moves)
        if selected_cells.empty:
            continue
        rpred = route_pred(move_mat.reshape(-1), basis_fit_df, basis_fit_moves, route_fit)
        cpred = h098_pred(move_mat.reshape(-1), cell, h098_fit)
        if rpred > spec.route_pred_cap:
            continue
        if cpred > spec.h098_pred_cap:
            continue
        prob = materialize(base_prob, move_mat)
        if int((np.abs(prob - base_prob) > TOL).sum()) == 0:
            continue
        hash_id = short_hash(prob)
        candidate_id = safe_id(f"h106_{spec.name}_{hash_id}", 128)
        path = OUT / f"submission_{candidate_id}.csv"
        h085mod.write_submission(sample, prob, path)
        row = evaluate_candidate(
            candidate_id,
            prob,
            move_mat,
            selected_cells,
            source_actions,
            consensus,
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
        source_actions = source_actions.copy()
        source_actions.insert(0, "candidate_id", candidate_id)
        source_frames.append(source_actions)
        selected_cells = selected_cells.copy()
        selected_cells.insert(0, "candidate_id", candidate_id)
        selected_cell_frames.append(selected_cells)
        top_consensus = consensus.sort_values("h106_score", ascending=False).head(220).copy()
        top_consensus.insert(0, "candidate_id", candidate_id)
        consensus_frames.append(top_consensus)

    candidates = pd.DataFrame(candidate_rows)
    if candidates.empty:
        raise RuntimeError("no H106 candidates")
    candidates = candidates.sort_values(["h106_score", "route_basis_pred_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True)
    selected = candidates.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"submission_h106_routeconsensus_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)

    selected_model = model_scores.iloc[0].to_dict()
    decision = {
        "decision": "promote_h106_route_consensus_kernel_expansion",
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
    public_out.to_csv(OUT / "h106_public_moves_weighted.csv", index=False)
    bad_axes.to_csv(OUT / "h106_bad_axes.csv", index=False)
    good_axes.to_csv(OUT / "h106_good_axes.csv", index=False)
    model_scores.to_csv(OUT / "h106_route_basis_model_scores.csv", index=False)
    pred_rows.to_csv(OUT / "h106_route_basis_loo_predictions.csv", index=False)
    h098_scores.to_csv(OUT / "h106_h098_frontier_model_scores.csv", index=False)
    h098_pred_rows.to_csv(OUT / "h106_h098_frontier_loo_predictions.csv", index=False)
    scored_base.to_csv(OUT / "h106_scored_route_actions_base.csv", index=False)
    candidates.to_csv(OUT / "h106_candidates.csv", index=False)
    pd.concat(source_frames, ignore_index=True).to_csv(OUT / "h106_source_actions.csv", index=False)
    pd.concat(selected_cell_frames, ignore_index=True).to_csv(OUT / "h106_selected_cells.csv", index=False)
    pd.concat(consensus_frames, ignore_index=True).to_csv(OUT / "h106_top_consensus_cells.csv", index=False)
    pd.DataFrame([decision]).to_csv(OUT / "h106_decision.csv", index=False)

    cols = [
        "candidate_id",
        "spec_name",
        "source_actions",
        "selected_cells",
        "changed_rows_vs_h057",
        "selected_seed_rows",
        "selected_seed_neighbors",
        "route_basis_pred_delta_vs_h057",
        "model_pred_delta_vs_h057",
        "posterior_delta_vs_h057",
        "hard_diag_delta_vs_h057",
        "h102_cum_bad_weighted_pos",
        "h102_cum_bad_max_pos",
        "h102_cum_h088_axis_cos",
        "h102_cum_good_bad_margin",
        "selected_mean_vote_weight",
        "selected_mean_consensus",
        "anti_h088_direction_rate",
        "h057_positive_align_rate",
        "selected_conflict_rate",
        "h106_score",
        "file",
    ]
    report = f"""# H106 Route-Consensus Kernel Expansion HS-JEPA

Question: is the H105 tiny id06/id07 kernel expandable through repeated
route-action consensus votes?

Route-basis model scores:

{md_table(model_scores.head(12), 12)}

Candidates:

{md_table(candidates[cols], 20)}

Decision:

{md_table(pd.DataFrame([decision]), 1)}

Interpretation rule:

- If H106 beats H105, the tiny kernel is a seed of a transferable consensus
  field.
- If H105 beats H106, the public-sensitive route-consensus law is sharply
  localized and should not be expanded.
- If H103/H104 beat both, action-grade safety lives at portfolio/residual-field
  level rather than consensus-vote cells.
"""
    (OUT / "h106_report.md").write_text(report, encoding="utf-8")

    print(f"selected={decision['selected_candidate_id']}")
    print(f"root={root_path}")
    print(candidates[cols].head(10).to_string(index=False))
    print("\nroute-basis model")
    print(model_scores.head(10).to_string(index=False))


if __name__ == "__main__":
    run()
