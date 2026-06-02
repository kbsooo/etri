#!/usr/bin/env python3
"""H100: route-action basis public equation HS-JEPA.

H099 used route templates as a constraint around H098's cell-level signed
equation.  H100 makes route-actions the equation basis itself.

Known public submissions are represented by their signed overlap with candidate
route-action vectors.  The response model is then fitted in this route-action
basis and decoded back into a constrained assignment.
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
OUT = HITL / "h100_route_action_basis_equation_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H099_PATH = HITL / "h099_route_constrained_signed_assignment_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h099mod", H099_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H099_PATH}")
h099mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h099mod
SPEC.loader.exec_module(h099mod)

h098mod = h099mod.h098mod
h097mod = h099mod.h097mod
h095mod = h099mod.h095mod
h085mod = h099mod.h085mod
h087mod = h099mod.h087mod

TARGETS = h099mod.TARGETS
KEYS = h099mod.KEYS
BASE_FILE = h099mod.BASE_FILE
BASE_LB = h099mod.BASE_LB
TOL = h099mod.TOL


@dataclass(frozen=True)
class H100BasisSpec:
    name: str
    mode: str
    route_group: str
    alpha: float
    cap: float
    min_route_score: float
    min_cell_score: float
    top_actions: int


@dataclass(frozen=True)
class H100CandidateSpec:
    name: str
    action_group: str
    max_routes: int
    max_cells: int
    max_rows: int
    max_per_subject: int
    q2_cap: int
    amp: float
    min_action_score: float
    worldview: str


@dataclass(frozen=True)
class RouteBasisFit:
    feature_set: str
    k_basis: int
    alpha: float
    x_cols: list[str]
    intercept: float
    beta: np.ndarray
    mu: np.ndarray
    sd: np.ndarray
    loo_pred: np.ndarray
    loo_mae: float
    loo_rmse: float
    loo_spearman: float
    loo_pair_acc: float


def clip_prob(x: np.ndarray) -> np.ndarray:
    return h085mod.clip_prob(np.asarray(x, dtype=np.float64))


def logit(x: np.ndarray) -> np.ndarray:
    return h085mod.logit(np.asarray(x, dtype=np.float64))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return h085mod.sigmoid(np.asarray(x, dtype=np.float64))


def bce(prob: np.ndarray, q: np.ndarray) -> np.ndarray:
    return h085mod.bce(np.asarray(prob, dtype=np.float64), np.asarray(q, dtype=np.float64))


def rank01(values: np.ndarray, high: bool = True) -> np.ndarray:
    return h085mod.rank01(np.asarray(values, dtype=np.float64), high=high)


def safe_id(text: str, limit: int = 132) -> str:
    return h085mod.safe_id(text, limit=limit)


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return h085mod.md_table(frame, n=n)


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h100_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h100_route_basis_*_uploadsafe.csv"):
        path.unlink()


def basis_specs() -> list[H100BasisSpec]:
    return [
        H100BasisSpec("basis_conflict_a052", "conflict_invert", "conflict", 0.52, 0.68, 0.0, 0.22, 220),
        H100BasisSpec("basis_tail_hybrid_a044", "hybrid_route", "tail", 0.44, 0.58, 0.0, 0.28, 240),
        H100BasisSpec("basis_objective_a042", "frontier_descent", "objective", 0.42, 0.56, 0.0, 0.30, 240),
        H100BasisSpec("basis_q2_counter_a050", "counter_h088", "q2_route", 0.50, 0.62, 0.0, 0.28, 220),
        H100BasisSpec("basis_fullstate_a030", "frontier_descent", "full_state", 0.30, 0.44, 0.0, 0.22, 220),
        H100BasisSpec("basis_nonq2_positive_a038", "positive_bridge", "nonq2_full", 0.38, 0.52, 0.0, 0.20, 220),
    ]


def candidate_specs() -> list[H100CandidateSpec]:
    return [
        H100CandidateSpec(
            name="routebasis_conflict_c80_r30_amp100",
            action_group="conflict",
            max_routes=30,
            max_cells=80,
            max_rows=30,
            max_per_subject=8,
            q2_cap=10,
            amp=1.00,
            min_action_score=0.54,
            worldview="route-action public equation selects H057/H088 conflict assignments directly",
        ),
        H100CandidateSpec(
            name="routebasis_mixed_c150_r52_amp085",
            action_group="mixed",
            max_routes=52,
            max_cells=150,
            max_rows=52,
            max_per_subject=10,
            q2_cap=36,
            amp=0.85,
            min_action_score=0.50,
            worldview="route-action basis reveals a broader signed public-private assignment field",
        ),
        H100CandidateSpec(
            name="routebasis_objective_c140_r55_amp090",
            action_group="objective",
            max_routes=55,
            max_cells=140,
            max_rows=55,
            max_per_subject=10,
            q2_cap=0,
            amp=0.90,
            min_action_score=0.49,
            worldview="route equation says public-safe action is Q3/S objective route movement",
        ),
        H100CandidateSpec(
            name="routebasis_q2tox_c70_r45_amp090",
            action_group="q2tox",
            max_routes=45,
            max_cells=70,
            max_rows=45,
            max_per_subject=8,
            q2_cap=45,
            amp=0.90,
            min_action_score=0.50,
            worldview="route equation isolates Q2 toxicity as direction-specific public punishment",
        ),
        H100CandidateSpec(
            name="routebasis_highassign_c120_r28_amp075",
            action_group="highassign",
            max_routes=28,
            max_cells=120,
            max_rows=28,
            max_per_subject=7,
            q2_cap=28,
            amp=0.75,
            min_action_score=0.48,
            worldview="high H071 assignment routes survive only when route-basis public equation agrees",
        ),
    ]


def action_move_matrix(shape: tuple[int, int], cells: pd.DataFrame, move_col: str = "h100_direct_move") -> np.ndarray:
    move_mat = np.zeros(shape, dtype=np.float64)
    for rec in cells.to_dict("records"):
        move_mat[int(rec["row"]), int(rec["target_index"])] = float(rec[move_col])
    return move_mat


def materialize(base_prob: np.ndarray, move_mat: np.ndarray) -> np.ndarray:
    return clip_prob(sigmoid(logit(base_prob) + move_mat))


def build_route_basis(
    routes: pd.DataFrame,
    pool: pd.DataFrame,
    cell: pd.DataFrame,
    h098_fit: h097mod.ResponseFit,
    base_prob: np.ndarray,
) -> tuple[pd.DataFrame, dict[str, pd.DataFrame], np.ndarray]:
    frames = []
    cells_by_basis: dict[str, pd.DataFrame] = {}
    move_vectors = []

    for spec in basis_specs():
        proxy = h099mod.H099Spec(
            name=spec.name,
            mode=spec.mode,
            route_group=spec.route_group,
            max_routes=9999,
            max_cells=99999,
            max_rows=9999,
            max_per_subject=9999,
            q2_cap=99999,
            alpha=spec.alpha,
            cap=spec.cap,
            min_route_score=spec.min_route_score,
            min_cell_score=spec.min_cell_score,
            worldview=f"H100 basis {spec.name}",
        )
        actions, action_cells = h099mod.route_action_table(routes, pool, cell, h098_fit, base_prob, proxy)
        if actions.empty:
            continue
        actions = actions.head(spec.top_actions).copy()
        actions["basis_spec"] = spec.name
        for rec in actions.to_dict("records"):
            old_id = str(rec["action_id"])
            basis_id = safe_id(f"{spec.name}__{old_id}", 128)
            cells = action_cells[old_id].copy()
            cells["basis_id"] = basis_id
            cells["basis_spec"] = spec.name
            cells["h100_direct_move"] = np.clip(cells["h099_route_move"].to_numpy(dtype=np.float64), -spec.cap, spec.cap) * spec.alpha
            cells["h097_move_col"] = "h100_direct_move"
            cells_by_basis[basis_id] = cells
            move_vectors.append(action_move_matrix(base_prob.shape, cells).reshape(-1))
            rows = dict(rec)
            rows["basis_id"] = basis_id
            rows["basis_spec"] = spec.name
            rows["basis_alpha"] = spec.alpha
            rows["basis_cap"] = spec.cap
            frames.append(rows)

    basis = pd.DataFrame(frames)
    if basis.empty:
        raise RuntimeError("no H100 route basis actions")
    move_matrix = np.vstack(move_vectors).astype(np.float64)
    basis = basis.reset_index(drop=True)
    basis["basis_norm_l2"] = np.linalg.norm(move_matrix, axis=1)
    basis["basis_norm_l1"] = np.abs(move_matrix).sum(axis=1)
    return basis, cells_by_basis, move_matrix


def design_from_moves(moves: np.ndarray, basis_moves: np.ndarray, basis: pd.DataFrame, feature_set: str) -> tuple[np.ndarray, list[str]]:
    n = max(moves.shape[1], 1)
    norm = np.maximum(np.linalg.norm(basis_moves, axis=1), 1.0e-12)
    signed = (moves @ basis_moves.T) / (norm[None, :] * np.sqrt(n))
    absed = (np.abs(moves) @ np.abs(basis_moves).T) / (np.maximum(np.abs(basis_moves).sum(axis=1), 1.0e-12)[None, :])

    if feature_set == "signed":
        x = signed
        cols = [f"signed::{bid}" for bid in basis["basis_id"].astype(str)]
    elif feature_set == "signed_abs":
        x = np.column_stack([signed, absed])
        cols = [f"signed::{bid}" for bid in basis["basis_id"].astype(str)] + [f"abs::{bid}" for bid in basis["basis_id"].astype(str)]
    elif feature_set == "signed_meta":
        meta_rows = []
        for i, move in enumerate(moves):
            meta_rows.append(
                [
                    float(np.mean(np.abs(move))),
                    float(np.mean(move * move)),
                    float(np.mean(np.abs(move) > 1.0e-10)),
                    float(np.max(np.abs(move))),
                    float(np.mean(signed[i])) if moves.ndim == 2 else 0.0,
                ]
            )
        meta = np.asarray(meta_rows, dtype=np.float64)
        x = np.column_stack([signed, meta])
        cols = [f"signed::{bid}" for bid in basis["basis_id"].astype(str)] + [
            "mean_abs_move",
            "mean_sq_move",
            "changed_share",
            "max_abs_move",
            "mean_signed_basis",
        ]
    else:
        raise ValueError(feature_set)
    return np.nan_to_num(x), cols


def fit_weighted_ridge(x: np.ndarray, y: np.ndarray, w: np.ndarray, alpha: float) -> tuple[float, np.ndarray, np.ndarray, np.ndarray]:
    return h098mod.fit_weighted_ridge(x, y, w, alpha)


def predict_x(x: np.ndarray, intercept: float, beta: np.ndarray, mu: np.ndarray, sd: np.ndarray) -> np.ndarray:
    return h097mod.predict_x(x, intercept, beta, mu, sd)


def evaluate_route_basis_models(public: pd.DataFrame, basis: pd.DataFrame, basis_moves: np.ndarray) -> tuple[pd.DataFrame, pd.DataFrame, RouteBasisFit]:
    all_moves = np.vstack(public["move_logit"].to_list()).astype(np.float64)
    y = public["delta_vs_h057"].to_numpy(dtype=np.float64)
    weights = h098mod.frontier_weights(public)
    h088_idx = int(np.where(public["file"].astype(str).eq(h095mod.H088_FILE).to_numpy())[0][0])
    base_idx = int(np.where(public["file"].astype(str).eq(BASE_FILE).to_numpy())[0][0])
    feature_sets = ["signed", "signed_abs", "signed_meta"]
    k_values = [40, 70, 100, 140, 180, min(240, len(basis))]
    alphas = [0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0]
    rows = []
    pred_rows = []
    fits: list[RouteBasisFit] = []

    ranked = basis.sort_values("h099_route_score", ascending=False).reset_index(drop=True)
    for k in sorted(set(k for k in k_values if 8 <= k <= len(ranked))):
        ids = ranked.head(k)["basis_id"].astype(str).tolist()
        mask = basis["basis_id"].astype(str).isin(ids).to_numpy()
        basis_k = basis.loc[mask].reset_index(drop=True)
        moves_k = basis_moves[mask]
        for feature_set in feature_sets:
            x, x_cols = design_from_moves(all_moves, moves_k, basis_k, feature_set)
            if x.shape[1] > 220:
                variances = np.nanvar(x, axis=0)
                keep_cols = np.argsort(variances)[-220:]
                x = x[:, keep_cols]
                x_cols = [x_cols[i] for i in keep_cols]
            for alpha in alphas:
                loo = np.zeros(len(y), dtype=np.float64)
                for held in range(len(y)):
                    keep = np.ones(len(y), dtype=bool)
                    keep[held] = False
                    intercept, beta, mu, sd = fit_weighted_ridge(x[keep], y[keep], weights[keep], alpha)
                    loo[held] = predict_x(x[[held]], intercept, beta, mu, sd)[0]
                err = loo - y
                abs_err = np.abs(err)
                intercept, beta, mu, sd = fit_weighted_ridge(x, y, weights, alpha)
                full_pred = predict_x(x, intercept, beta, mu, sd)
                fit = RouteBasisFit(
                    feature_set=feature_set,
                    k_basis=int(k),
                    alpha=float(alpha),
                    x_cols=x_cols,
                    intercept=intercept,
                    beta=beta,
                    mu=mu,
                    sd=sd,
                    loo_pred=loo,
                    loo_mae=float(np.mean(abs_err)),
                    loo_rmse=float(np.sqrt(np.mean(err * err))),
                    loo_spearman=h097mod.spearman(y, loo),
                    loo_pair_acc=h097mod.pairwise_accuracy(y, loo),
                )
                fits.append(fit)
                weighted_mae = float(np.sum(weights * abs_err) / np.sum(weights))
                weighted_rmse = float(np.sqrt(np.sum(weights * err * err) / np.sum(weights)))
                h088_abs = float(abs_err[h088_idx])
                h088_sign_ok = float(np.sign(loo[h088_idx]) == np.sign(y[h088_idx]))
                base_abs = float(abs_err[base_idx])
                rows.append(
                    {
                        "feature_set": feature_set,
                        "k_basis": int(k),
                        "alpha": float(alpha),
                        "n_x_features": len(x_cols),
                        "loo_mae": fit.loo_mae,
                        "loo_rmse": fit.loo_rmse,
                        "weighted_loo_mae": weighted_mae,
                        "weighted_loo_rmse": weighted_rmse,
                        "loo_spearman": fit.loo_spearman,
                        "loo_pair_acc": fit.loo_pair_acc,
                        "h088_loo_pred": float(loo[h088_idx]),
                        "h088_loo_error": float(err[h088_idx]),
                        "h088_loo_abs_error": h088_abs,
                        "h088_sign_ok": h088_sign_ok,
                        "base_loo_abs_error": base_abs,
                        "full_fit_weighted_mae": float(np.sum(weights * np.abs(full_pred - y)) / np.sum(weights)),
                        "route_basis_rank_score": weighted_mae
                        + 0.45 * weighted_rmse
                        + 1.70 * h088_abs
                        + 0.55 * base_abs
                        - 0.00016 * fit.loo_pair_acc
                        - 0.00008 * fit.loo_spearman
                        - 0.00035 * h088_sign_ok,
                    }
                )
                for i, rec in public[["file", "public_lb", "delta_vs_h057"]].iterrows():
                    pred_rows.append(
                        {
                            "feature_set": feature_set,
                            "k_basis": int(k),
                            "alpha": float(alpha),
                            "file": str(rec["file"]),
                            "public_lb": float(rec["public_lb"]),
                            "delta_vs_h057": float(rec["delta_vs_h057"]),
                            "frontier_weight": float(weights[i]),
                            "loo_pred_delta": float(loo[i]),
                            "loo_error": float(loo[i] - rec["delta_vs_h057"]),
                        }
                    )

    scores = pd.DataFrame(rows).sort_values(["route_basis_rank_score", "h088_loo_abs_error"], ascending=[True, True]).reset_index(drop=True)
    best = scores.iloc[0]
    selected = next(
        fit
        for fit in fits
        if fit.feature_set == str(best["feature_set"])
        and int(fit.k_basis) == int(best["k_basis"])
        and abs(fit.alpha - float(best["alpha"])) < 1.0e-12
    )
    return scores, pd.DataFrame(pred_rows), selected


def selected_basis_for_fit(basis: pd.DataFrame, basis_moves: np.ndarray, fit: RouteBasisFit) -> tuple[pd.DataFrame, np.ndarray]:
    ranked = basis.sort_values("h099_route_score", ascending=False).reset_index(drop=True).head(fit.k_basis)
    ids = set(ranked["basis_id"].astype(str))
    mask = basis["basis_id"].astype(str).isin(ids).to_numpy()
    return basis.loc[mask].reset_index(drop=True), basis_moves[mask]


def predict_candidate_delta(move_flat: np.ndarray, basis_fit_df: pd.DataFrame, basis_fit_moves: np.ndarray, fit: RouteBasisFit) -> float:
    x, x_cols = design_from_moves(move_flat.reshape(1, -1), basis_fit_moves, basis_fit_df, fit.feature_set)
    if x.shape[1] != len(fit.x_cols):
        keep = [i for i, col in enumerate(x_cols) if col in set(fit.x_cols)]
        x = x[:, keep]
    return float(predict_x(x, fit.intercept, fit.beta, fit.mu, fit.sd)[0])


def score_basis_actions(
    basis: pd.DataFrame,
    basis_moves: np.ndarray,
    basis_fit_df: pd.DataFrame,
    basis_fit_moves: np.ndarray,
    fit: RouteBasisFit,
) -> pd.DataFrame:
    out = basis.copy()
    preds = []
    for move in basis_moves:
        preds.append(predict_candidate_delta(move, basis_fit_df, basis_fit_moves, fit))
    out["h100_route_basis_pred_delta"] = np.asarray(preds, dtype=np.float64)
    out["h100_action_score"] = (
        0.28 * rank01(-out["h100_route_basis_pred_delta"].to_numpy(dtype=np.float64), high=True)
        + 0.17 * rank01(out["h099_route_score"].to_numpy(dtype=np.float64), high=True)
        + 0.12 * out["anti_h088_direction_rate"].to_numpy(dtype=np.float64)
        + 0.12 * out["h057_positive_align_rate"].to_numpy(dtype=np.float64)
        + 0.11 * out["selected_conflict_rate"].to_numpy(dtype=np.float64)
        + 0.09 * out["assignment_route_score"].to_numpy(dtype=np.float64)
        + 0.06 * out["selected_safe_cell_mean"].to_numpy(dtype=np.float64)
        - 0.10 * out["mean_bad_same_rank"].to_numpy(dtype=np.float64)
        - 20.0 * np.maximum(out["hard_diag_delta_vs_h057"].to_numpy(dtype=np.float64), 0.0)
        - 14.0 * np.maximum(out["posterior_delta_vs_h057"].to_numpy(dtype=np.float64), 0.0)
    )
    return out.sort_values("h100_action_score", ascending=False).reset_index(drop=True)


def action_group_allowed(rec: dict[str, object], group: str) -> bool:
    basis_spec = str(rec["basis_spec"])
    route_name = str(rec["route_name"])
    if group == "mixed":
        return True
    if group == "conflict":
        return float(rec["selected_conflict_rate"]) >= 0.999
    if group == "objective":
        return basis_spec in {"basis_objective_a042", "basis_nonq2_positive_a038"} or str(rec["route_targets"]).find("S") >= 0
    if group == "q2tox":
        return basis_spec == "basis_q2_counter_a050" or int(rec["Q2_cells"]) > 0
    if group == "highassign":
        return float(rec["assignment_route_score"]) >= 0.58 or route_name in {"full_state", "nonq2_full"}
    raise ValueError(group)


def greedy_select(
    scored: pd.DataFrame,
    cells_by_basis: dict[str, pd.DataFrame],
    spec: H100CandidateSpec,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    selected_actions = []
    selected_cells = []
    used_rows: set[int] = set()
    subject_counts: dict[str, int] = {}
    cell_count = 0
    q2_count = 0

    for rec in scored.to_dict("records"):
        if float(rec["h100_action_score"]) < spec.min_action_score:
            continue
        if not action_group_allowed(rec, spec.action_group):
            continue
        row = int(rec["row"])
        subject = str(rec["subject_id"])
        if row in used_rows:
            continue
        if len(selected_actions) >= spec.max_routes or len(used_rows) >= spec.max_rows:
            break
        cells = cells_by_basis[str(rec["basis_id"])].copy()
        cells["h100_direct_move"] = cells["h100_direct_move"].to_numpy(dtype=np.float64) * spec.amp
        n_cells = int(len(cells))
        n_q2 = int(cells["target"].astype(str).eq("Q2").sum())
        if cell_count + n_cells > spec.max_cells:
            continue
        if q2_count + n_q2 > spec.q2_cap:
            continue
        if subject_counts.get(subject, 0) + 1 > spec.max_per_subject:
            continue
        selected_actions.append(rec)
        selected_cells.append(cells)
        used_rows.add(row)
        subject_counts[subject] = subject_counts.get(subject, 0) + 1
        cell_count += n_cells
        q2_count += n_q2

    if not selected_actions:
        return pd.DataFrame(), pd.DataFrame()
    actions = pd.DataFrame(selected_actions).reset_index(drop=True)
    cells = pd.concat(selected_cells, ignore_index=True).sort_values(["basis_id", "flat_index"])
    cells = cells.drop_duplicates("flat_index", keep="first").reset_index(drop=True)
    cells["h097_move_col"] = "h100_direct_move"
    return actions, cells


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
    route_fit: RouteBasisFit,
    basis_fit_df: pd.DataFrame,
    basis_fit_moves: np.ndarray,
    spec: H100CandidateSpec,
    path: Path,
) -> dict[str, object]:
    proxy = h097mod.H097Spec(
        name=spec.name,
        mode="route_basis",
        target_group=spec.action_group,
        k=spec.max_cells,
        alpha=1.0,
        cap=2.0,
        min_score=spec.min_action_score,
        worldview=spec.worldview,
    )
    metrics = h097mod.evaluate_candidate(candidate_id, prob, move_mat, base_prob, selected_cells, cell, sample, h098_fit, proxy, path)
    route_pred = predict_candidate_delta(move_mat.reshape(-1), basis_fit_df, basis_fit_moves, route_fit)
    metrics["route_basis_pred_delta_vs_h057"] = route_pred
    metrics["route_basis_feature_set"] = route_fit.feature_set
    metrics["route_basis_k"] = route_fit.k_basis
    metrics["route_basis_alpha"] = route_fit.alpha
    metrics["selected_basis_actions"] = int(len(selected_actions))
    metrics["mean_h100_action_score"] = float(selected_actions["h100_action_score"].mean()) if len(selected_actions) else 0.0
    metrics["mean_route_basis_action_delta"] = float(selected_actions["h100_route_basis_pred_delta"].mean()) if len(selected_actions) else 0.0
    metrics["mean_assignment_route_score"] = float(selected_actions["assignment_route_score"].mean()) if len(selected_actions) else 0.0
    metrics["mean_h099_route_score"] = float(selected_actions["h099_route_score"].mean()) if len(selected_actions) else 0.0
    metrics["basis_specs"] = ",".join(sorted(selected_actions["basis_spec"].astype(str).unique().tolist())) if len(selected_actions) else ""
    metrics["h100_score"] = (
        270.0 * (-route_pred)
        + 120.0 * (-float(metrics["model_pred_delta_vs_h057"]))
        + 0.16 * float(metrics["anti_h088_direction_rate"])
        + 0.14 * float(metrics["h057_positive_align_rate"])
        + 0.12 * float(metrics["selected_conflict_rate"])
        + 0.10 * float(metrics["mean_assignment_route_score"])
        + 0.08 * max(float(metrics["cos_h057_vs_h042_direction"]), 0.0)
        - 0.24 * max(float(metrics["cos_h088_direction"]), 0.0)
        - 0.25 * float(metrics["max_positive_bad_cosine"])
        - 24.0 * max(float(metrics["hard_diag_delta_vs_h057"]), 0.0)
        - 10.0 * max(float(metrics["posterior_delta_vs_h057"]), 0.0)
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

    basis, cells_by_basis, basis_moves = build_route_basis(routes, pool, cell, h098_fit, base_prob)
    model_scores, pred_rows, route_fit = evaluate_route_basis_models(public, basis, basis_moves)
    basis_fit_df, basis_fit_moves = selected_basis_for_fit(basis, basis_moves, route_fit)
    scored = score_basis_actions(basis, basis_moves, basis_fit_df, basis_fit_moves, route_fit)

    candidate_rows = []
    selected_action_frames = []
    selected_cell_frames = []
    for spec in candidate_specs():
        selected_actions, selected_cells = greedy_select(scored, cells_by_basis, spec)
        if selected_cells.empty:
            continue
        move_mat = action_move_matrix(base_prob.shape, selected_cells)
        prob = materialize(base_prob, move_mat)
        if int((np.abs(prob - base_prob) > TOL).sum()) == 0:
            continue
        hash_id = short_hash(prob)
        candidate_id = safe_id(f"h100_{spec.name}_{hash_id}", 128)
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
        raise RuntimeError("no H100 candidates")
    candidates = candidates.sort_values(["h100_score", "route_basis_pred_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True)
    selected = candidates.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"submission_h100_route_basis_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)

    public_out = public.drop(columns=["move_logit"]).copy()
    public_out["frontier_weight"] = h098mod.frontier_weights(public)
    selected_model = model_scores.iloc[0].to_dict()
    decision = {
        "decision": "promote_h100_route_action_basis_equation",
        "selected_candidate_id": selected["candidate_id"],
        "root_uploadsafe_path": str(root_path.resolve()),
        "worldview": selected["worldview"],
        "h098_feature_set": h098_fit.feature_set,
        "h098_alpha": h098_fit.alpha,
        **{f"route_basis_{k}": v for k, v in selected_model.items()},
        **selected,
        **{f"root_{key}": value for key, value in validation.items()},
    }

    public_out.to_csv(OUT / "h100_public_moves_weighted.csv", index=False)
    h098_scores.to_csv(OUT / "h100_h098_frontier_model_scores.csv", index=False)
    h098_pred_rows.to_csv(OUT / "h100_h098_frontier_loo_predictions.csv", index=False)
    basis.to_csv(OUT / "h100_route_basis_actions.csv", index=False)
    pd.DataFrame(basis_moves).to_csv(OUT / "h100_route_basis_move_matrix.csv", index=False)
    model_scores.to_csv(OUT / "h100_route_basis_model_scores.csv", index=False)
    pred_rows.to_csv(OUT / "h100_route_basis_loo_predictions.csv", index=False)
    scored.to_csv(OUT / "h100_scored_route_actions.csv", index=False)
    candidates.to_csv(OUT / "h100_candidates.csv", index=False)
    pd.concat(selected_action_frames, ignore_index=True).to_csv(OUT / "h100_selected_route_actions.csv", index=False)
    pd.concat(selected_cell_frames, ignore_index=True).to_csv(OUT / "h100_selected_cells.csv", index=False)
    pd.DataFrame([decision]).to_csv(OUT / "h100_decision.csv", index=False)

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
        "anti_h088_direction_rate",
        "h057_positive_align_rate",
        "selected_conflict_rate",
        "mean_assignment_route_score",
        "cos_h088_direction",
        "max_positive_bad_cosine",
        "h100_score",
        "file",
    ]
    report = f"""# H100 Route-Action Basis Equation HS-JEPA

Question: can known public submissions be explained in route-action basis space
rather than cell-feature space?

Route-basis model scores:

{md_table(model_scores.head(15), 15)}

Selected-model LOO predictions:

{md_table(pred_rows[pred_rows['feature_set'].eq(route_fit.feature_set) & pred_rows['k_basis'].eq(route_fit.k_basis) & pred_rows['alpha'].eq(route_fit.alpha)], 30)}

Candidates:

{md_table(candidates[cols], 20)}

Decision:

{md_table(pd.DataFrame([decision]), 1)}

Interpretation rule:

- If H100 improves over H099/H098, route-action basis is the right public/private
  equation space.
- If H099 improves but H100 loses, route constraints help but public response
  cannot be fitted directly in route basis.
- If H098 wins over both, the hidden law is sparse signed cells rather than
  discrete route assignments.
"""
    (OUT / "h100_report.md").write_text(report, encoding="utf-8")

    print(f"selected={decision['selected_candidate_id']}")
    print(f"root={root_path}")
    print(candidates[cols].head(10).to_string(index=False))
    print("\nroute-basis model")
    print(model_scores.head(10).to_string(index=False))


if __name__ == "__main__":
    run()
