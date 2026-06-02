#!/usr/bin/env python3
"""H102: bad-axis nullspace assignment HS-JEPA.

H100 showed a strong route-action public equation, but H101 showed that simple
model-agreement pruning collapses the action field to only a few cells.

H102 changes the safety question:

    toxic action is not a local cell score
    toxic action is projection onto bad public action axes

The decoder therefore selects route-actions that H100 likes, while keeping the
combined move vector outside the positive span of known bad public submissions.
It allows overlap when the H057-positive anchor margin is stronger than the bad
axis shadow, because the H057 direction itself partially overlaps old bad axes.
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
OUT = HITL / "h102_bad_axis_nullspace_assignment_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H100_PATH = HITL / "h100_route_action_basis_equation_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h100mod", H100_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H100_PATH}")
h100mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h100mod
SPEC.loader.exec_module(h100mod)

h099mod = h100mod.h099mod
h098mod = h100mod.h098mod
h097mod = h100mod.h097mod
h095mod = h100mod.h095mod
h085mod = h100mod.h085mod

TARGETS = h100mod.TARGETS
KEYS = h100mod.KEYS
BASE_FILE = h100mod.BASE_FILE
BASE_LB = h100mod.BASE_LB
TOL = h100mod.TOL

GOOD_ANCHORS = [
    "submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv",
    "submission_h050_target_route_phase_b140216b_uploadsafe.csv",
    "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv",
]


@dataclass(frozen=True)
class H102Spec:
    name: str
    group: str
    max_actions: int
    max_cells: int
    max_rows: int
    max_per_subject: int
    q2_cap: int
    amp: float
    min_action_score: float
    max_bad_weighted_pos: float
    max_bad_max_pos: float
    max_h088_cos: float
    min_good_margin: float
    max_cell_pred_delta: float
    route_pred_cap: float
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


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    aa = np.asarray(a, dtype=np.float64).reshape(-1)
    bb = np.asarray(b, dtype=np.float64).reshape(-1)
    return float(np.dot(aa, bb) / (np.linalg.norm(aa) * np.linalg.norm(bb) + 1.0e-12))


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h102_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h102_badnull_*_uploadsafe.csv"):
        path.unlink()


def candidate_specs() -> list[H102Spec]:
    return [
        H102Spec(
            name="shadow_margin_conflict_c96_r34_amp105",
            group="shadow_margin_conflict",
            max_actions=34,
            max_cells=96,
            max_rows=34,
            max_per_subject=8,
            q2_cap=12,
            amp=1.05,
            min_action_score=0.55,
            max_bad_weighted_pos=0.032,
            max_bad_max_pos=0.115,
            max_h088_cos=0.000,
            min_good_margin=-0.010,
            max_cell_pred_delta=0.000070,
            route_pred_cap=0.000000,
            worldview="safe action is H100 conflict route movement with positive-anchor margin over bad-axis shadow",
        ),
        H102Spec(
            name="strict_null_conflict_c72_r28_amp100",
            group="strict_null_conflict",
            max_actions=28,
            max_cells=72,
            max_rows=28,
            max_per_subject=7,
            q2_cap=8,
            amp=1.00,
            min_action_score=0.50,
            max_bad_weighted_pos=0.008,
            max_bad_max_pos=0.045,
            max_h088_cos=0.004,
            min_good_margin=-0.002,
            max_cell_pred_delta=0.000040,
            route_pred_cap=0.000000,
            worldview="safe action is the near-nullspace part of the H057/H088 conflict field",
        ),
        H102Spec(
            name="anchor_shadow_bridge_c128_r42_amp090",
            group="anchor_shadow_bridge",
            max_actions=42,
            max_cells=128,
            max_rows=42,
            max_per_subject=9,
            q2_cap=18,
            amp=0.90,
            min_action_score=0.48,
            max_bad_weighted_pos=0.040,
            max_bad_max_pos=0.140,
            max_h088_cos=0.008,
            min_good_margin=0.006,
            max_cell_pred_delta=0.000090,
            route_pred_cap=-0.000020,
            worldview="some bad-axis overlap is allowed only when H057-positive anchor margin dominates",
        ),
        H102Spec(
            name="routegain_badnull_c150_r52_amp085",
            group="routegain_badnull",
            max_actions=52,
            max_cells=150,
            max_rows=52,
            max_per_subject=10,
            q2_cap=34,
            amp=0.85,
            min_action_score=0.46,
            max_bad_weighted_pos=0.028,
            max_bad_max_pos=0.100,
            max_h088_cos=0.010,
            min_good_margin=-0.006,
            max_cell_pred_delta=0.000060,
            route_pred_cap=-0.000080,
            worldview="route-basis gain can be expanded if the cumulative action remains bad-axis safe",
        ),
        H102Spec(
            name="lowtox_objective_null_c110_r40_amp095",
            group="lowtox_objective_null",
            max_actions=40,
            max_cells=110,
            max_rows=40,
            max_per_subject=9,
            q2_cap=0,
            amp=0.95,
            min_action_score=0.44,
            max_bad_weighted_pos=0.025,
            max_bad_max_pos=0.095,
            max_h088_cos=0.010,
            min_good_margin=-0.006,
            max_cell_pred_delta=0.000060,
            route_pred_cap=-0.000030,
            worldview="objective Q3/S route-actions are safe only in the bad-axis nullspace",
        ),
    ]


def action_move_matrix(shape: tuple[int, int], cells: pd.DataFrame, move_col: str = "h102_direct_move") -> np.ndarray:
    move_mat = np.zeros(shape, dtype=np.float64)
    for rec in cells.to_dict("records"):
        move_mat[int(rec["row"]), int(rec["target_index"])] = float(rec[move_col])
    return move_mat


def materialize(base_prob: np.ndarray, move_mat: np.ndarray) -> np.ndarray:
    return clip_prob(sigmoid(logit(base_prob) + move_mat))


def build_axes(public: pd.DataFrame, sample: pd.DataFrame, base_prob: np.ndarray) -> tuple[pd.DataFrame, np.ndarray, pd.DataFrame, np.ndarray]:
    base_logit = logit(base_prob).reshape(-1)
    public_moves = np.vstack(public["move_logit"].to_list()).astype(np.float64)
    bad_rows = []
    good_rows = []

    for i, rec in public.reset_index(drop=True).iterrows():
        file_name = str(rec["file"])
        if file_name == BASE_FILE:
            continue
        if any(anchor in file_name for anchor in ["h042", "h050", "h012"]):
            continue
        delta = max(float(rec["delta_vs_h057"]), 0.0)
        if delta <= 0.0:
            continue
        weight = 0.15 + np.log1p(delta / 0.0005)
        if file_name == h095mod.H088_FILE:
            weight += 3.0
        if any(tag in file_name for tag in ["jepa", "lejepa", "h010", "e216", "e323"]):
            weight += 0.45
        bad_rows.append({"axis_name": file_name, "axis_type": "bad_public", "weight": weight, "delta_vs_h057": delta, "move": public_moves[i]})

    for anchor in GOOD_ANCHORS:
        path = h085mod.locate(anchor)
        if path is None:
            continue
        anchor_prob = h085mod.load_sub(path, sample)[TARGETS].to_numpy(dtype=np.float64)
        good_rows.append(
            {
                "axis_name": anchor,
                "axis_type": "h057_positive_anchor",
                "weight": 1.0,
                "delta_vs_h057": 0.0,
                "move": base_logit - logit(anchor_prob).reshape(-1),
            }
        )

    if not bad_rows or not good_rows:
        raise RuntimeError("failed to build H102 axes")

    bad = pd.DataFrame(bad_rows)
    good = pd.DataFrame(good_rows)
    bad_moves = np.vstack(bad["move"].to_list()).astype(np.float64)
    good_moves = np.vstack(good["move"].to_list()).astype(np.float64)
    bad["weight"] = bad["weight"].to_numpy(dtype=np.float64) / np.mean(bad["weight"].to_numpy(dtype=np.float64))
    return bad.drop(columns=["move"]), bad_moves, good.drop(columns=["move"]), good_moves


def cos_matrix(moves: np.ndarray, axes: np.ndarray) -> np.ndarray:
    move_norm = np.maximum(np.linalg.norm(moves, axis=1), 1.0e-12)
    axis_norm = np.maximum(np.linalg.norm(axes, axis=1), 1.0e-12)
    return (moves @ axes.T) / (move_norm[:, None] * axis_norm[None, :])


def add_axis_scores(scored: pd.DataFrame, basis_moves: np.ndarray, bad_axes: pd.DataFrame, bad_moves: np.ndarray, good_axes: pd.DataFrame, good_moves: np.ndarray) -> pd.DataFrame:
    out = scored.copy()
    bad_cos = cos_matrix(basis_moves, bad_moves)
    good_cos = cos_matrix(basis_moves, good_moves)
    bad_w = bad_axes["weight"].to_numpy(dtype=np.float64)
    bad_pos = np.maximum(bad_cos, 0.0)
    h088_cols = bad_axes["axis_name"].astype(str).eq(h095mod.H088_FILE).to_numpy()
    h088_cos = bad_cos[:, h088_cols][:, 0] if h088_cols.any() else np.zeros(len(out), dtype=np.float64)

    out["h102_bad_max_pos"] = bad_pos.max(axis=1)
    out["h102_bad_mean_pos"] = bad_pos.mean(axis=1)
    out["h102_bad_weighted_pos"] = (bad_pos * bad_w[None, :]).mean(axis=1)
    out["h102_h088_axis_cos"] = h088_cos
    out["h102_good_max_cos"] = good_cos.max(axis=1)
    out["h102_good_mean_cos"] = good_cos.mean(axis=1)
    out["h102_good_bad_margin"] = out["h102_good_max_cos"] - out["h102_bad_weighted_pos"]
    out["h102_shadow_ratio"] = out["h102_good_max_cos"] / (out["h102_bad_weighted_pos"] + 1.0e-9)
    out["h102_axis_score"] = (
        0.24 * rank01(out["h100_action_score"].to_numpy(dtype=np.float64), high=True)
        + 0.18 * rank01(-out["h100_route_basis_pred_delta"].to_numpy(dtype=np.float64), high=True)
        + 0.14 * rank01(out["h102_good_bad_margin"].to_numpy(dtype=np.float64), high=True)
        + 0.10 * rank01(out["h102_shadow_ratio"].to_numpy(dtype=np.float64), high=True)
        + 0.10 * rank01(-out["h102_h088_axis_cos"].to_numpy(dtype=np.float64), high=True)
        + 0.10 * out["selected_conflict_rate"].to_numpy(dtype=np.float64)
        + 0.08 * out["h057_positive_align_rate"].to_numpy(dtype=np.float64)
        + 0.08 * out["anti_h088_direction_rate"].to_numpy(dtype=np.float64)
        + 0.06 * out["assignment_route_score"].to_numpy(dtype=np.float64)
        - 0.16 * rank01(out["h102_bad_weighted_pos"].to_numpy(dtype=np.float64), high=True)
        - 0.08 * out["selected_toxic_mean"].to_numpy(dtype=np.float64)
        - 0.06 * out["mean_bad_same_rank"].to_numpy(dtype=np.float64)
    )
    return out.sort_values("h102_axis_score", ascending=False).reset_index(drop=True)


def group_allowed(rec: dict[str, object], group: str) -> bool:
    if group == "shadow_margin_conflict":
        return h100mod.action_group_allowed(rec, "conflict") and float(rec["h102_good_bad_margin"]) >= -0.02
    if group == "strict_null_conflict":
        return h100mod.action_group_allowed(rec, "conflict") and float(rec["h102_bad_max_pos"]) <= 0.06
    if group == "anchor_shadow_bridge":
        return float(rec["h102_good_max_cos"]) >= 0.01 and float(rec["h102_good_bad_margin"]) >= 0.0
    if group == "routegain_badnull":
        return float(rec["h100_route_basis_pred_delta"]) < 0.0 and float(rec["h102_bad_weighted_pos"]) <= 0.04
    if group == "lowtox_objective_null":
        return h100mod.action_group_allowed(rec, "objective") and float(rec["selected_toxic_mean"]) <= 0.72
    raise ValueError(group)


def cumulative_axis_metrics(move_flat: np.ndarray, bad_axes: pd.DataFrame, bad_moves: np.ndarray, good_moves: np.ndarray) -> dict[str, float]:
    if np.linalg.norm(move_flat) <= 1.0e-12:
        return {
            "h102_cum_bad_max_pos": 0.0,
            "h102_cum_bad_weighted_pos": 0.0,
            "h102_cum_h088_axis_cos": 0.0,
            "h102_cum_good_max_cos": 0.0,
            "h102_cum_good_mean_cos": 0.0,
            "h102_cum_good_bad_margin": 0.0,
        }
    bad_cos = np.asarray([cosine(move_flat, axis) for axis in bad_moves], dtype=np.float64)
    good_cos = np.asarray([cosine(move_flat, axis) for axis in good_moves], dtype=np.float64)
    bad_pos = np.maximum(bad_cos, 0.0)
    bad_w = bad_axes["weight"].to_numpy(dtype=np.float64)
    h088_mask = bad_axes["axis_name"].astype(str).eq(h095mod.H088_FILE).to_numpy()
    h088_cos = float(bad_cos[h088_mask][0]) if h088_mask.any() else 0.0
    bad_weighted = float(np.mean(bad_pos * bad_w))
    good_max = float(np.max(good_cos))
    return {
        "h102_cum_bad_max_pos": float(np.max(bad_pos)),
        "h102_cum_bad_weighted_pos": bad_weighted,
        "h102_cum_h088_axis_cos": h088_cos,
        "h102_cum_good_max_cos": good_max,
        "h102_cum_good_mean_cos": float(np.mean(good_cos)),
        "h102_cum_good_bad_margin": good_max - bad_weighted,
    }


def greedy_select(
    scored: pd.DataFrame,
    cells_by_basis: dict[str, pd.DataFrame],
    spec: H102Spec,
    base_shape: tuple[int, int],
    bad_axes: pd.DataFrame,
    bad_moves: np.ndarray,
    good_moves: np.ndarray,
    h098_fit: h097mod.ResponseFit,
    route_fit: h100mod.RouteBasisFit,
    basis_fit_df: pd.DataFrame,
    basis_fit_moves: np.ndarray,
    cell: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, float]]:
    selected_actions = []
    selected_cells = []
    used_rows: set[int] = set()
    subject_counts: dict[str, int] = {}
    cell_count = 0
    q2_count = 0
    move_mat = np.zeros(base_shape, dtype=np.float64)
    last_metrics = cumulative_axis_metrics(move_mat.reshape(-1), bad_axes, bad_moves, good_moves)
    last_metrics["h102_cum_route_pred_delta"] = 0.0
    last_metrics["h102_cum_cell_pred_delta"] = 0.0

    for rec in scored.to_dict("records"):
        if float(rec["h102_axis_score"]) < spec.min_action_score:
            continue
        if not group_allowed(rec, spec.group):
            continue
        row = int(rec["row"])
        subject = str(rec["subject_id"])
        if row in used_rows:
            continue
        if len(selected_actions) >= spec.max_actions or len(used_rows) >= spec.max_rows:
            break
        if subject_counts.get(subject, 0) + 1 > spec.max_per_subject:
            continue

        cells = cells_by_basis[str(rec["basis_id"])].copy()
        cells["h102_direct_move"] = cells["h100_direct_move"].to_numpy(dtype=np.float64) * spec.amp
        n_cells = int(len(cells))
        n_q2 = int(cells["target"].astype(str).eq("Q2").sum())
        if cell_count + n_cells > spec.max_cells:
            continue
        if q2_count + n_q2 > spec.q2_cap:
            continue

        tmp = move_mat.copy()
        for cell_rec in cells.to_dict("records"):
            tmp[int(cell_rec["row"]), int(cell_rec["target_index"])] = float(cell_rec["h102_direct_move"])
        tmp_flat = tmp.reshape(-1)
        axis_metrics = cumulative_axis_metrics(tmp_flat, bad_axes, bad_moves, good_moves)
        if axis_metrics["h102_cum_bad_weighted_pos"] > spec.max_bad_weighted_pos:
            continue
        if axis_metrics["h102_cum_bad_max_pos"] > spec.max_bad_max_pos:
            continue
        if axis_metrics["h102_cum_h088_axis_cos"] > spec.max_h088_cos:
            continue
        if axis_metrics["h102_cum_good_bad_margin"] < spec.min_good_margin:
            continue

        route_pred = h100mod.predict_candidate_delta(tmp_flat, basis_fit_df, basis_fit_moves, route_fit)
        if route_pred > spec.route_pred_cap:
            continue
        cell_pred = h097mod.predict_candidate_delta(tmp_flat, cell, h098_fit)
        if cell_pred > spec.max_cell_pred_delta:
            continue

        move_mat = tmp
        axis_metrics["h102_cum_route_pred_delta"] = float(route_pred)
        axis_metrics["h102_cum_cell_pred_delta"] = float(cell_pred)
        last_metrics = axis_metrics
        selected_actions.append(rec)
        selected_cells.append(cells)
        used_rows.add(row)
        subject_counts[subject] = subject_counts.get(subject, 0) + 1
        cell_count += n_cells
        q2_count += n_q2

    if not selected_actions:
        return pd.DataFrame(), pd.DataFrame(), last_metrics
    actions = pd.DataFrame(selected_actions).reset_index(drop=True)
    cells = pd.concat(selected_cells, ignore_index=True).sort_values(["basis_id", "flat_index"])
    cells = cells.drop_duplicates("flat_index", keep="first").reset_index(drop=True)
    cells["h097_move_col"] = "h102_direct_move"
    return actions, cells, last_metrics


def evaluate_candidate(
    candidate_id: str,
    prob: np.ndarray,
    move_mat: np.ndarray,
    base_prob: np.ndarray,
    selected_cells: pd.DataFrame,
    selected_actions: pd.DataFrame,
    cell: pd.DataFrame,
    sample: pd.DataFrame,
    h098_fit: h097mod.ResponseFit,
    route_fit: h100mod.RouteBasisFit,
    basis_fit_df: pd.DataFrame,
    basis_fit_moves: np.ndarray,
    spec: H102Spec,
    path: Path,
    axis_metrics: dict[str, float],
) -> dict[str, object]:
    proxy = h100mod.H100CandidateSpec(
        name=spec.name,
        action_group=spec.group,
        max_routes=spec.max_actions,
        max_cells=spec.max_cells,
        max_rows=spec.max_rows,
        max_per_subject=spec.max_per_subject,
        q2_cap=spec.q2_cap,
        amp=spec.amp,
        min_action_score=spec.min_action_score,
        worldview=spec.worldview,
    )
    metrics = h100mod.evaluate_candidate(
        candidate_id,
        prob,
        move_mat,
        base_prob,
        selected_cells,
        selected_actions,
        cell,
        sample,
        h098_fit,
        route_fit,
        basis_fit_df,
        basis_fit_moves,
        proxy,
        path,
    )
    metrics.update(axis_metrics)
    metrics["mean_h102_axis_score"] = float(selected_actions["h102_axis_score"].mean()) if len(selected_actions) else 0.0
    metrics["mean_h102_good_bad_margin"] = float(selected_actions["h102_good_bad_margin"].mean()) if len(selected_actions) else 0.0
    metrics["mean_h102_bad_weighted_pos"] = float(selected_actions["h102_bad_weighted_pos"].mean()) if len(selected_actions) else 0.0
    metrics["mean_h102_good_max_cos"] = float(selected_actions["h102_good_max_cos"].mean()) if len(selected_actions) else 0.0
    metrics["h102_score"] = (
        300.0 * (-float(metrics["route_basis_pred_delta_vs_h057"]))
        + 110.0 * (-float(metrics["model_pred_delta_vs_h057"]))
        + 0.22 * float(metrics["anti_h088_direction_rate"])
        + 0.20 * float(metrics["h057_positive_align_rate"])
        + 0.16 * float(metrics["selected_conflict_rate"])
        + 0.12 * max(float(metrics["h102_cum_good_bad_margin"]), 0.0)
        + 0.10 * max(float(metrics["h102_cum_good_max_cos"]), 0.0)
        + 0.08 * float(metrics["mean_h102_axis_score"])
        - 0.36 * max(float(metrics["h102_cum_bad_weighted_pos"]), 0.0)
        - 0.18 * max(float(metrics["h102_cum_bad_max_pos"]), 0.0)
        - 0.22 * max(float(metrics["h102_cum_h088_axis_cos"]), 0.0)
        - 0.24 * float(metrics["max_positive_bad_cosine"])
        - 22.0 * max(float(metrics["hard_diag_delta_vs_h057"]), 0.0)
        - 12.0 * max(float(metrics["posterior_delta_vs_h057"]), 0.0)
    )
    return metrics


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
    routes = h099mod.load_routes()

    basis, cells_by_basis, basis_moves = h100mod.build_route_basis(routes, pool, cell, h098_fit, base_prob)
    model_scores, pred_rows, route_fit = h100mod.evaluate_route_basis_models(public, basis, basis_moves)
    basis_fit_df, basis_fit_moves = h100mod.selected_basis_for_fit(basis, basis_moves, route_fit)
    scored0 = h100mod.score_basis_actions(basis, basis_moves, basis_fit_df, basis_fit_moves, route_fit)
    bad_axes, bad_moves, good_axes, good_moves = build_axes(public, sample, base_prob)
    scored = add_axis_scores(scored0, basis_moves, bad_axes, bad_moves, good_axes, good_moves)

    candidate_rows = []
    selected_action_frames = []
    selected_cell_frames = []
    for spec in candidate_specs():
        selected_actions, selected_cells, axis_metrics = greedy_select(
            scored,
            cells_by_basis,
            spec,
            base_prob.shape,
            bad_axes,
            bad_moves,
            good_moves,
            h098_fit,
            route_fit,
            basis_fit_df,
            basis_fit_moves,
            cell,
        )
        if selected_cells.empty:
            continue
        move_mat = action_move_matrix(base_prob.shape, selected_cells)
        prob = materialize(base_prob, move_mat)
        if int((np.abs(prob - base_prob) > TOL).sum()) == 0:
            continue
        hash_id = short_hash(prob)
        candidate_id = safe_id(f"h102_{spec.name}_{hash_id}", 128)
        path = OUT / f"submission_{candidate_id}.csv"
        h085mod.write_submission(sample, prob, path)
        metrics = evaluate_candidate(
            candidate_id,
            prob,
            move_mat,
            base_prob,
            selected_cells,
            selected_actions,
            cell,
            sample,
            h098_fit,
            route_fit,
            basis_fit_df,
            basis_fit_moves,
            spec,
            path,
            axis_metrics,
        )
        candidate_rows.append(metrics)
        selected_actions = selected_actions.copy()
        selected_actions.insert(0, "candidate_id", candidate_id)
        selected_action_frames.append(selected_actions)
        selected_cells = selected_cells.copy()
        selected_cells.insert(0, "candidate_id", candidate_id)
        selected_cell_frames.append(selected_cells)

    candidates = pd.DataFrame(candidate_rows)
    if candidates.empty:
        raise RuntimeError("no H102 candidates")
    candidates = candidates.sort_values(["h102_score", "route_basis_pred_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True)
    selected = candidates.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"submission_h102_badnull_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)

    public_out = public.drop(columns=["move_logit"]).copy()
    public_out["frontier_weight"] = h098mod.frontier_weights(public)
    selected_model = model_scores.iloc[0].to_dict()
    decision = {
        "decision": "promote_h102_bad_axis_nullspace_assignment",
        "selected_candidate_id": selected["candidate_id"],
        "root_uploadsafe_path": str(root_path.resolve()),
        "worldview": selected["worldview"],
        "h098_feature_set": h098_fit.feature_set,
        "h098_alpha": h098_fit.alpha,
        **{f"route_basis_{k}": v for k, v in selected_model.items()},
        **selected,
        **{f"root_{key}": value for key, value in validation.items()},
    }

    public_out.to_csv(OUT / "h102_public_moves_weighted.csv", index=False)
    bad_axes.to_csv(OUT / "h102_bad_axes.csv", index=False)
    good_axes.to_csv(OUT / "h102_good_axes.csv", index=False)
    h098_scores.to_csv(OUT / "h102_h098_frontier_model_scores.csv", index=False)
    h098_pred_rows.to_csv(OUT / "h102_h098_frontier_loo_predictions.csv", index=False)
    model_scores.to_csv(OUT / "h102_route_basis_model_scores.csv", index=False)
    pred_rows.to_csv(OUT / "h102_route_basis_loo_predictions.csv", index=False)
    scored.to_csv(OUT / "h102_scored_route_actions.csv", index=False)
    candidates.to_csv(OUT / "h102_candidates.csv", index=False)
    pd.concat(selected_action_frames, ignore_index=True).to_csv(OUT / "h102_selected_route_actions.csv", index=False)
    pd.concat(selected_cell_frames, ignore_index=True).to_csv(OUT / "h102_selected_cells.csv", index=False)
    pd.DataFrame([decision]).to_csv(OUT / "h102_decision.csv", index=False)

    cols = [
        "candidate_id",
        "spec_name",
        "selected_basis_actions",
        "selected_cells",
        "changed_rows_vs_h057",
        "route_basis_pred_delta_vs_h057",
        "model_pred_delta_vs_h057",
        "posterior_delta_vs_h057",
        "hard_diag_delta_vs_h057",
        "h102_cum_bad_weighted_pos",
        "h102_cum_bad_max_pos",
        "h102_cum_h088_axis_cos",
        "h102_cum_good_bad_margin",
        "anti_h088_direction_rate",
        "h057_positive_align_rate",
        "selected_conflict_rate",
        "h102_score",
        "file",
    ]
    report = f"""# H102 Bad-Axis Nullspace Assignment HS-JEPA

Question: can H100 route-actions become safer when the decoder avoids the
positive span of known bad public submission axes?

Bad axes:

{md_table(bad_axes, 30)}

Good anchor axes:

{md_table(good_axes, 10)}

Route-basis model scores:

{md_table(model_scores.head(15), 15)}

Candidates:

{md_table(candidates[cols], 20)}

Decision:

{md_table(pd.DataFrame([decision]), 1)}

Interpretation rule:

- If H102 improves over H100, public/private safety is a global bad-axis
  nullspace or shadow-margin problem.
- If H100 improves but H102 loses, the bad axes overlap the true positive
  H057 route too much and should not be used as hard action constraints.
- If both lose, route-action basis is still only a sensor; the safe assignment
  field needs a different route family.
"""
    (OUT / "h102_report.md").write_text(report, encoding="utf-8")

    print(f"selected={decision['selected_candidate_id']}")
    print(f"root={root_path}")
    print(candidates[cols].head(10).to_string(index=False))


if __name__ == "__main__":
    run()
