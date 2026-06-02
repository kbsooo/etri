#!/usr/bin/env python3
"""H103: toxic-shadow cancellation assignment HS-JEPA.

H102 found a clean bad-axis nullspace action, but the selected root candidate
collapsed to seven cells.  H103 tests the next equation-solver idea:

    safe action need not be individually bad-axis silent
    safe action can be a portfolio whose toxic shadows cancel

The decoder first reserves counter-shadow route-actions, then admits higher
route-basis-gain actions as long as the cumulative move vector stays safe under
bad public axes, H088 cosine, H057-positive anchor margin, and H098 cell
equation stress.
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
OUT = HITL / "h103_toxic_shadow_cancellation_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H102_PATH = HITL / "h102_bad_axis_nullspace_assignment_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h102mod", H102_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H102_PATH}")
h102mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h102mod
SPEC.loader.exec_module(h102mod)

h100mod = h102mod.h100mod
h099mod = h102mod.h099mod
h098mod = h102mod.h098mod
h097mod = h102mod.h097mod
h095mod = h102mod.h095mod
h085mod = h102mod.h085mod

TARGETS = h102mod.TARGETS
KEYS = h102mod.KEYS
BASE_FILE = h102mod.BASE_FILE
TOL = h102mod.TOL


@dataclass(frozen=True)
class H103Spec:
    name: str
    group: str
    max_actions: int
    max_cells: int
    max_rows: int
    max_per_subject: int
    q2_cap: int
    amp: float
    reserve_count: int
    pool_top: int
    min_axis_score: float
    max_bad_weighted_pos: float
    max_bad_max_pos: float
    max_h088_cos: float
    min_good_margin: float
    route_pred_cap: float
    max_cell_pred_delta: float
    worldview: str


def clip_prob(x: np.ndarray) -> np.ndarray:
    return h085mod.clip_prob(np.asarray(x, dtype=np.float64))


def logit(x: np.ndarray) -> np.ndarray:
    return h085mod.logit(np.asarray(x, dtype=np.float64))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return h085mod.sigmoid(np.asarray(x, dtype=np.float64))


def safe_id(text: str, limit: int = 132) -> str:
    return h085mod.safe_id(text, limit=limit)


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return h085mod.md_table(frame, n=n)


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h103_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h103_shadowcancel_*_uploadsafe.csv"):
        path.unlink()


def candidate_specs() -> list[H103Spec]:
    return [
        H103Spec(
            name="balanced_shadow_portfolio_c180_r62_amp090",
            group="balanced_shadow",
            max_actions=62,
            max_cells=180,
            max_rows=62,
            max_per_subject=12,
            q2_cap=38,
            amp=0.90,
            reserve_count=10,
            pool_top=260,
            min_axis_score=0.38,
            max_bad_weighted_pos=0.026,
            max_bad_max_pos=0.085,
            max_h088_cos=0.004,
            min_good_margin=0.000,
            route_pred_cap=-0.000120,
            max_cell_pred_delta=0.000090,
            worldview="counter-shadow reserves allow a denser H100 route-action portfolio",
        ),
        H103Spec(
            name="dense_nullplus_conflict_c132_r45_amp100",
            group="dense_conflict",
            max_actions=45,
            max_cells=132,
            max_rows=45,
            max_per_subject=10,
            q2_cap=18,
            amp=1.00,
            reserve_count=8,
            pool_top=220,
            min_axis_score=0.44,
            max_bad_weighted_pos=0.014,
            max_bad_max_pos=0.055,
            max_h088_cos=0.000,
            min_good_margin=0.008,
            route_pred_cap=-0.000180,
            max_cell_pred_delta=0.000070,
            worldview="H102 strict-null can be expanded by pairing conflict routes with counter-shadow reserves",
        ),
        H103Spec(
            name="id06_block_shadow_cancel_c96_r20_amp110",
            group="id06_block",
            max_actions=20,
            max_cells=96,
            max_rows=20,
            max_per_subject=20,
            q2_cap=12,
            amp=1.10,
            reserve_count=6,
            pool_top=160,
            min_axis_score=0.42,
            max_bad_weighted_pos=0.032,
            max_bad_max_pos=0.105,
            max_h088_cos=0.006,
            min_good_margin=0.002,
            route_pred_cap=-0.000320,
            max_cell_pred_delta=0.000090,
            worldview="the H057/H088 law is concentrated in the id06 public-sensitive block and can be shadow-cancelled",
        ),
        H103Spec(
            name="qsubjective_gain_cancel_c90_r30_amp085",
            group="qsubjective_gain",
            max_actions=30,
            max_cells=90,
            max_rows=30,
            max_per_subject=8,
            q2_cap=20,
            amp=0.85,
            reserve_count=8,
            pool_top=220,
            min_axis_score=0.34,
            max_bad_weighted_pos=0.030,
            max_bad_max_pos=0.100,
            max_h088_cos=0.006,
            min_good_margin=0.010,
            route_pred_cap=-0.000450,
            max_cell_pred_delta=0.000080,
            worldview="Q-subjective high-gain route-actions are safe only when their bad-axis shadows are cancelled",
        ),
        H103Spec(
            name="objective_shadow_bridge_c150_r55_amp080",
            group="objective_bridge",
            max_actions=55,
            max_cells=150,
            max_rows=55,
            max_per_subject=10,
            q2_cap=0,
            amp=0.80,
            reserve_count=12,
            pool_top=260,
            min_axis_score=0.30,
            max_bad_weighted_pos=0.030,
            max_bad_max_pos=0.095,
            max_h088_cos=0.006,
            min_good_margin=0.020,
            route_pred_cap=-0.000180,
            max_cell_pred_delta=0.000100,
            worldview="objective Q3/S actions become safe when balanced by negative toxic-shadow routes",
        ),
    ]


def action_move_matrix(shape: tuple[int, int], cells: pd.DataFrame, move_col: str = "h103_direct_move") -> np.ndarray:
    move_mat = np.zeros(shape, dtype=np.float64)
    for rec in cells.to_dict("records"):
        move_mat[int(rec["row"]), int(rec["target_index"])] = float(rec[move_col])
    return move_mat


def materialize(base_prob: np.ndarray, move_mat: np.ndarray) -> np.ndarray:
    return clip_prob(sigmoid(logit(base_prob) + move_mat))


def action_vectors(
    scored: pd.DataFrame,
    cells_by_basis: dict[str, pd.DataFrame],
    shape: tuple[int, int],
    amp: float,
) -> tuple[np.ndarray, dict[str, pd.DataFrame]]:
    vectors = []
    cells_scaled: dict[str, pd.DataFrame] = {}
    for basis_id in scored["basis_id"].astype(str).tolist():
        cells = cells_by_basis[basis_id].copy()
        cells["h103_direct_move"] = cells["h100_direct_move"].to_numpy(dtype=np.float64) * amp
        cells["h097_move_col"] = "h103_direct_move"
        cells_scaled[basis_id] = cells
        vectors.append(action_move_matrix(shape, cells).reshape(-1))
    return np.vstack(vectors).astype(np.float64), cells_scaled


def add_shadow_features(
    scored: pd.DataFrame,
    action_moves: np.ndarray,
    bad_axes: pd.DataFrame,
    bad_moves: np.ndarray,
    good_moves: np.ndarray,
) -> pd.DataFrame:
    out = scored.copy().reset_index(drop=True)
    bad_cos = h102mod.cos_matrix(action_moves, bad_moves)
    good_cos = h102mod.cos_matrix(action_moves, good_moves)
    bad_w = bad_axes["weight"].to_numpy(dtype=np.float64)
    bad_pos = np.maximum(bad_cos, 0.0)
    bad_neg = np.maximum(-bad_cos, 0.0)
    h088_mask = bad_axes["axis_name"].astype(str).eq(h095mod.H088_FILE).to_numpy()
    h088_cos = bad_cos[:, h088_mask][:, 0] if h088_mask.any() else np.zeros(len(out), dtype=np.float64)

    out["h103_bad_weighted_neg"] = (bad_neg * bad_w[None, :]).mean(axis=1)
    out["h103_bad_weighted_pos"] = (bad_pos * bad_w[None, :]).mean(axis=1)
    out["h103_good_max_cos"] = good_cos.max(axis=1)
    out["h103_h088_axis_cos"] = h088_cos
    out["h103_shadow_credit"] = (
        out["h103_bad_weighted_neg"].to_numpy(dtype=np.float64)
        + np.maximum(out["h103_good_max_cos"].to_numpy(dtype=np.float64), 0.0)
        - out["h103_bad_weighted_pos"].to_numpy(dtype=np.float64)
    )
    out["h103_gain_credit"] = (
        -out["h100_route_basis_pred_delta"].to_numpy(dtype=np.float64)
        + 0.00016 * out["h102_axis_score"].to_numpy(dtype=np.float64)
        + 0.00008 * out["h103_shadow_credit"].to_numpy(dtype=np.float64)
    )
    return out


def group_allowed(rec: dict[str, object], group: str, reserve: bool) -> bool:
    route_name = str(rec["route_name"])
    basis_spec = str(rec["basis_spec"])
    subject = str(rec["subject_id"])
    if reserve:
        return float(rec["h103_shadow_credit"]) > 0.010 or float(rec["h103_h088_axis_cos"]) < -0.020
    if group == "balanced_shadow":
        return float(rec["h100_route_basis_pred_delta"]) < 0.000020 or float(rec["h102_axis_score"]) > 0.55
    if group == "dense_conflict":
        return float(rec["selected_conflict_rate"]) >= 0.75 and float(rec["h102_axis_score"]) > 0.45
    if group == "id06_block":
        return subject == "id06" and float(rec["h102_axis_score"]) > 0.35
    if group == "qsubjective_gain":
        return (
            ("q_subjective" in route_name or "q1q3" in route_name or "nonq2" in route_name)
            and float(rec["h100_route_basis_pred_delta"]) < 0.000020
        )
    if group == "objective_bridge":
        return (
            basis_spec in {"basis_objective_a042", "basis_nonq2_positive_a038", "basis_tail_hybrid_a044"}
            and ("S" in str(rec["route_targets"]) or "q3" in route_name)
        )
    raise ValueError(group)


def portfolio_metrics(
    move_flat: np.ndarray,
    bad_axes: pd.DataFrame,
    bad_moves: np.ndarray,
    good_moves: np.ndarray,
    h098_fit: h097mod.ResponseFit,
    route_fit: h100mod.RouteBasisFit,
    basis_fit_df: pd.DataFrame,
    basis_fit_moves: np.ndarray,
    cell: pd.DataFrame,
) -> dict[str, float]:
    axis = h102mod.cumulative_axis_metrics(move_flat, bad_axes, bad_moves, good_moves)
    axis["h103_route_pred_delta"] = h100mod.predict_candidate_delta(move_flat, basis_fit_df, basis_fit_moves, route_fit)
    axis["h103_cell_pred_delta"] = h097mod.predict_candidate_delta(move_flat, cell, h098_fit)
    return axis


def greedy_portfolio(
    scored: pd.DataFrame,
    action_moves: np.ndarray,
    cells_scaled: dict[str, pd.DataFrame],
    spec: H103Spec,
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
    work = scored.copy().reset_index(drop=True)
    work["_idx"] = np.arange(len(work), dtype=int)
    reserve = work.sort_values(
        ["h103_shadow_credit", "h103_h088_axis_cos", "h102_axis_score"],
        ascending=[False, True, False],
    ).head(spec.pool_top)
    gain = work.sort_values(
        ["h103_gain_credit", "h100_route_basis_pred_delta", "h102_axis_score"],
        ascending=[False, True, False],
    ).head(spec.pool_top)
    ordered_rows = []
    reserve_added = 0
    for rec in reserve.to_dict("records"):
        if reserve_added >= spec.reserve_count:
            break
        if group_allowed(rec, spec.group, reserve=True):
            rec = dict(rec)
            rec["_stage"] = "reserve"
            ordered_rows.append(rec)
            reserve_added += 1
    for rec in gain.to_dict("records"):
        if float(rec["h102_axis_score"]) < spec.min_axis_score:
            continue
        if group_allowed(rec, spec.group, reserve=False):
            rec = dict(rec)
            rec["_stage"] = "gain"
            ordered_rows.append(rec)

    selected_actions = []
    selected_cells = []
    used_rows: set[int] = set()
    used_basis: set[str] = set()
    subject_counts: dict[str, int] = {}
    cell_count = 0
    q2_count = 0
    move_mat = np.zeros(base_shape, dtype=np.float64)
    best_metrics = portfolio_metrics(move_mat.reshape(-1), bad_axes, bad_moves, good_moves, h098_fit, route_fit, basis_fit_df, basis_fit_moves, cell)

    for rec in ordered_rows:
        basis_id = str(rec["basis_id"])
        if basis_id in used_basis:
            continue
        row = int(rec["row"])
        subject = str(rec["subject_id"])
        if row in used_rows:
            continue
        if len(selected_actions) >= spec.max_actions or len(used_rows) >= spec.max_rows:
            break
        if subject_counts.get(subject, 0) + 1 > spec.max_per_subject:
            continue
        cells = cells_scaled[basis_id].copy()
        n_cells = int(len(cells))
        n_q2 = int(cells["target"].astype(str).eq("Q2").sum())
        if cell_count + n_cells > spec.max_cells:
            continue
        if q2_count + n_q2 > spec.q2_cap:
            continue

        tmp = move_mat.copy()
        for cell_rec in cells.to_dict("records"):
            tmp[int(cell_rec["row"]), int(cell_rec["target_index"])] = float(cell_rec["h103_direct_move"])
        metrics = portfolio_metrics(tmp.reshape(-1), bad_axes, bad_moves, good_moves, h098_fit, route_fit, basis_fit_df, basis_fit_moves, cell)
        if metrics["h102_cum_bad_weighted_pos"] > spec.max_bad_weighted_pos:
            continue
        if metrics["h102_cum_bad_max_pos"] > spec.max_bad_max_pos:
            continue
        if metrics["h102_cum_h088_axis_cos"] > spec.max_h088_cos:
            continue
        if metrics["h102_cum_good_bad_margin"] < spec.min_good_margin:
            continue
        if metrics["h103_route_pred_delta"] > spec.route_pred_cap:
            continue
        if metrics["h103_cell_pred_delta"] > spec.max_cell_pred_delta:
            continue

        move_mat = tmp
        best_metrics = metrics
        selected_actions.append(rec)
        selected_cells.append(cells)
        used_rows.add(row)
        used_basis.add(basis_id)
        subject_counts[subject] = subject_counts.get(subject, 0) + 1
        cell_count += n_cells
        q2_count += n_q2

    if not selected_actions:
        return pd.DataFrame(), pd.DataFrame(), best_metrics
    actions = pd.DataFrame(selected_actions).drop(columns=["_idx"], errors="ignore").reset_index(drop=True)
    cells = pd.concat(selected_cells, ignore_index=True).sort_values(["basis_id", "flat_index"])
    cells = cells.drop_duplicates("flat_index", keep="first").reset_index(drop=True)
    cells["h097_move_col"] = "h103_direct_move"
    return actions, cells, best_metrics


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
    spec: H103Spec,
    path: Path,
    metrics: dict[str, float],
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
        min_action_score=spec.min_axis_score,
        worldview=spec.worldview,
    )
    out = h100mod.evaluate_candidate(
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
    out.update(metrics)
    out["mean_h103_shadow_credit"] = float(selected_actions["h103_shadow_credit"].mean()) if len(selected_actions) else 0.0
    out["mean_h103_bad_weighted_pos"] = float(selected_actions["h103_bad_weighted_pos"].mean()) if len(selected_actions) else 0.0
    out["mean_h103_bad_weighted_neg"] = float(selected_actions["h103_bad_weighted_neg"].mean()) if len(selected_actions) else 0.0
    out["mean_h103_good_max_cos"] = float(selected_actions["h103_good_max_cos"].mean()) if len(selected_actions) else 0.0
    out["reserve_actions"] = int(selected_actions.get("_stage", pd.Series(dtype=str)).astype(str).eq("reserve").sum()) if len(selected_actions) else 0
    out["gain_actions"] = int(selected_actions.get("_stage", pd.Series(dtype=str)).astype(str).eq("gain").sum()) if len(selected_actions) else 0
    out["h103_score"] = (
        270.0 * (-float(out["route_basis_pred_delta_vs_h057"]))
        + 120.0 * (-float(out["model_pred_delta_vs_h057"]))
        + 0.0050 * float(out["selected_cells"])
        + 0.0040 * float(out["selected_basis_actions"])
        + 0.20 * float(out["anti_h088_direction_rate"])
        + 0.18 * float(out["h057_positive_align_rate"])
        + 0.14 * float(out["selected_conflict_rate"])
        + 0.12 * max(float(out["h102_cum_good_bad_margin"]), 0.0)
        + 0.08 * max(float(out["h102_cum_good_max_cos"]), 0.0)
        + 0.08 * float(out["mean_h103_shadow_credit"])
        - 0.40 * max(float(out["h102_cum_bad_weighted_pos"]), 0.0)
        - 0.22 * max(float(out["h102_cum_bad_max_pos"]), 0.0)
        - 0.22 * max(float(out["h102_cum_h088_axis_cos"]), 0.0)
        - 0.25 * float(out["max_positive_bad_cosine"])
        - 20.0 * max(float(out["hard_diag_delta_vs_h057"]), 0.0)
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
        move_vectors, cells_scaled = action_vectors(scored_base, cells_by_basis, base_prob.shape, spec.amp)
        scored = add_shadow_features(scored_base, move_vectors, bad_axes, bad_moves, good_moves)
        selected_actions, selected_cells, metrics = greedy_portfolio(
            scored,
            move_vectors,
            cells_scaled,
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
        candidate_id = safe_id(f"h103_{spec.name}_{hash_id}", 128)
        path = OUT / f"submission_{candidate_id}.csv"
        h085mod.write_submission(sample, prob, path)
        row = evaluate_candidate(
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
            metrics,
        )
        candidate_rows.append(row)
        selected_actions = selected_actions.copy()
        selected_actions.insert(0, "candidate_id", candidate_id)
        selected_action_frames.append(selected_actions)
        selected_cells = selected_cells.copy()
        selected_cells.insert(0, "candidate_id", candidate_id)
        selected_cell_frames.append(selected_cells)

    candidates = pd.DataFrame(candidate_rows)
    if candidates.empty:
        raise RuntimeError("no H103 candidates")
    candidates = candidates.sort_values(["h103_score", "route_basis_pred_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True)
    selected = candidates.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"submission_h103_shadowcancel_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)

    public_out = public.drop(columns=["move_logit"]).copy()
    public_out["frontier_weight"] = h098mod.frontier_weights(public)
    selected_model = model_scores.iloc[0].to_dict()
    decision = {
        "decision": "promote_h103_toxic_shadow_cancellation",
        "selected_candidate_id": selected["candidate_id"],
        "root_uploadsafe_path": str(root_path.resolve()),
        "worldview": selected["worldview"],
        "h098_feature_set": h098_fit.feature_set,
        "h098_alpha": h098_fit.alpha,
        **{f"route_basis_{k}": v for k, v in selected_model.items()},
        **selected,
        **{f"root_{key}": value for key, value in validation.items()},
    }

    public_out.to_csv(OUT / "h103_public_moves_weighted.csv", index=False)
    bad_axes.to_csv(OUT / "h103_bad_axes.csv", index=False)
    good_axes.to_csv(OUT / "h103_good_axes.csv", index=False)
    model_scores.to_csv(OUT / "h103_route_basis_model_scores.csv", index=False)
    pred_rows.to_csv(OUT / "h103_route_basis_loo_predictions.csv", index=False)
    h098_scores.to_csv(OUT / "h103_h098_frontier_model_scores.csv", index=False)
    h098_pred_rows.to_csv(OUT / "h103_h098_frontier_loo_predictions.csv", index=False)
    scored_base.to_csv(OUT / "h103_scored_route_actions_base.csv", index=False)
    candidates.to_csv(OUT / "h103_candidates.csv", index=False)
    pd.concat(selected_action_frames, ignore_index=True).to_csv(OUT / "h103_selected_route_actions.csv", index=False)
    pd.concat(selected_cell_frames, ignore_index=True).to_csv(OUT / "h103_selected_cells.csv", index=False)
    pd.DataFrame([decision]).to_csv(OUT / "h103_decision.csv", index=False)

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
        "reserve_actions",
        "gain_actions",
        "anti_h088_direction_rate",
        "h057_positive_align_rate",
        "selected_conflict_rate",
        "h103_score",
        "file",
    ]
    report = f"""# H103 Toxic-Shadow Cancellation HS-JEPA

Question: can we expand H102's tiny nullspace action by first reserving
counter-shadow route-actions and then admitting high-gain route-basis actions?

Candidates:

{md_table(candidates[cols], 20)}

Decision:

{md_table(pd.DataFrame([decision]), 1)}

Interpretation rule:

- If H103 improves over H102/H100, public-safe action is a balanced portfolio
  problem, not a per-action gate.
- If H102 improves but H103 loses, toxic-shadow cancellation is too optimistic;
  safe action must remain near the strict nullspace.
- If H100 improves but H102/H103 lose, old bad public axes overlap the true
  positive route-basis law too much to constrain the decoder.
"""
    (OUT / "h103_report.md").write_text(report, encoding="utf-8")

    print(f"selected={decision['selected_candidate_id']}")
    print(f"root={root_path}")
    print(candidates[cols].head(10).to_string(index=False))


if __name__ == "__main__":
    run()
