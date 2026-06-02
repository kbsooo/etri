#!/usr/bin/env python3
"""H115: second-order action-equation HS-JEPA.

H098 uses a signed linear public-action equation.  H112-H114 then add residual
toxicity, row-route bundling, and toxic-subspace projection.  H115 asks whether
the remaining plateau is caused by the public response being nonlinear:

    action direction is not enough;
    target energy, row concentration, and Q/S co-movement create toxicity.

The model here is intentionally low-dimensional.  It fits known public
submissions with target/row/route curvature features, then uses that equation
to select row-target proposals from H112-H114.
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
OUT = HITL / "h115_second_order_action_equation_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H114_PATH = HITL / "h114_toxic_subspace_null_solver_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h114mod", H114_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H114_PATH}")
h114mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h114mod
SPEC.loader.exec_module(h114mod)

h112mod = h114mod.h112mod
h111mod = h114mod.h111mod
h109mod = h114mod.h109mod
h102mod = h114mod.h102mod
h100mod = h114mod.h100mod
h097mod = h114mod.h097mod
h085mod = h114mod.h085mod
h095mod = h097mod.h095mod

TARGETS = h114mod.TARGETS
KEYS = h114mod.KEYS
BASE_FILE = h114mod.BASE_FILE
TOL = h114mod.TOL
H088_FILE = h095mod.H088_FILE


@dataclass(frozen=True)
class CurvatureFit:
    feature_set: str
    alpha: float
    cols: list[str]
    intercept: float
    beta: np.ndarray
    mu: np.ndarray
    sd: np.ndarray
    loo_pred: np.ndarray
    score: float


@dataclass(frozen=True)
class H115Spec:
    name: str
    group: str
    max_cells: int
    max_rows: int
    max_per_subject: int
    max_per_target: int
    q2_cap: int
    amp: float
    cap: float
    proposal_top: int
    max_curv_pred: float
    max_marginal: float
    max_bad_weighted_pos: float
    max_bad_max_pos: float
    max_h088_cos: float
    min_good_margin: float
    route_pred_cap: float
    h098_pred_cap: float
    min_proposal_score: float
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
    for path in OUT.glob("submission_h115_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h115_curvature_*.csv"):
        path.unlink()


def materialize(base_prob: np.ndarray, move_mat: np.ndarray) -> np.ndarray:
    return clip_prob(sigmoid(logit(base_prob) + move_mat))


def route_pred(move_flat: np.ndarray, basis_fit_df: pd.DataFrame, basis_fit_moves: np.ndarray, route_fit: h100mod.RouteBasisFit) -> float:
    return h100mod.predict_candidate_delta(move_flat, basis_fit_df, basis_fit_moves, route_fit)


def h098_pred(move_flat: np.ndarray, cell: pd.DataFrame, h098_fit: h097mod.ResponseFit) -> float:
    return h097mod.predict_candidate_delta(move_flat, cell, h098_fit)


def cosine(a: np.ndarray | None, b: np.ndarray | None) -> float:
    if a is None or b is None:
        return 0.0
    x = np.asarray(a, dtype=np.float64).reshape(-1)
    y = np.asarray(b, dtype=np.float64).reshape(-1)
    return float(np.dot(x, y) / (np.linalg.norm(x) * np.linalg.norm(y) + 1.0e-12))


def overlap_count(a: np.ndarray, b: np.ndarray | None) -> int:
    if b is None:
        return 0
    return int(((np.abs(a.reshape(-1)) > 1.0e-12) & (np.abs(b.reshape(-1)) > 1.0e-12)).sum())


def load_previous_move(sample: pd.DataFrame, base_prob: np.ndarray, pattern: str) -> np.ndarray | None:
    matches = sorted(ROOT.glob(pattern))
    if not matches:
        return None
    prob = h085mod.load_sub(matches[-1], sample)[TARGETS].to_numpy(dtype=np.float64)
    return logit(prob).reshape(-1) - logit(base_prob).reshape(-1)


def frontier_weights(public: pd.DataFrame) -> np.ndarray:
    delta = public["delta_vs_h057"].to_numpy(dtype=np.float64)
    w = 0.10 + 5.0 * np.exp(-np.maximum(delta, 0.0) / 0.0012)
    file_s = public["file"].astype(str)
    w += file_s.eq(BASE_FILE).to_numpy(dtype=float) * 2.0
    w += file_s.eq(H088_FILE).to_numpy(dtype=float) * 3.0
    w += file_s.str.contains("h042|h050|h012", regex=True).to_numpy(dtype=float) * 1.2
    return w / np.mean(w)


def fit_weighted_ridge(x: np.ndarray, y: np.ndarray, w: np.ndarray, alpha: float) -> tuple[float, np.ndarray, np.ndarray, np.ndarray]:
    w = np.asarray(w, dtype=np.float64)
    w = np.maximum(w, 1.0e-9)
    mu = np.average(x, axis=0, weights=w)
    var = np.average((x - mu) ** 2, axis=0, weights=w)
    sd = np.sqrt(np.maximum(var, 1.0e-18))
    sd = np.where(sd < 1.0e-12, 1.0, sd)
    xz = np.nan_to_num((x - mu) / sd)
    xa = np.column_stack([np.ones(len(xz)), xz])
    sw = np.sqrt(w)
    xw = xa * sw[:, None]
    yw = y * sw
    penalty = np.eye(xa.shape[1], dtype=np.float64) * alpha
    penalty[0, 0] = 0.0
    beta_all = np.linalg.pinv(xw.T @ xw + penalty) @ xw.T @ yw
    return float(beta_all[0]), beta_all[1:], mu, sd


def predict_x(x: np.ndarray, fit: CurvatureFit) -> np.ndarray:
    xz = np.nan_to_num((x - fit.mu) / fit.sd)
    return fit.intercept + xz @ fit.beta


def prepare_context() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, np.ndarray, pd.DataFrame, h097mod.ResponseFit, h100mod.RouteBasisFit, pd.DataFrame, np.ndarray, pd.DataFrame, np.ndarray, np.ndarray, pd.DataFrame]:
    pool, public, sample, base_prob, cell, h098_fit, route_fit, basis_fit_df, basis_fit_moves, bad_axes, bad_moves, good_moves, residuals = h114mod.prepare_context()
    return pool, public, sample, base_prob, cell, h098_fit, route_fit, basis_fit_df, basis_fit_moves, bad_axes, bad_moves, good_moves, residuals


def axis_spec(mode: str) -> h114mod.H114Spec:
    return h114mod.H114Spec(
        name=f"axis_{mode}",
        group="broad_nonq2",
        toxic_mode=mode,
        prior_mode="h112_safe",
        max_cells=1,
        max_rows=1,
        max_per_subject=1,
        max_per_target=1,
        q2_cap=0,
        amp=1.0,
        cap=1.0,
        pool_top=1,
        bad_penalty=1.0,
        good_push=0.0,
        ridge=0.1,
        min_abs_move=0.0,
        min_score=0.0,
        max_residual_toxicity=1.0,
        min_residual_safety=0.0,
        max_bad_weighted_pos=1.0,
        max_bad_max_pos=1.0,
        max_h088_cos=1.0,
        min_good_margin=-1.0,
        route_pred_cap=1.0,
        h098_pred_cap=1.0,
        worldview="axis helper",
    )


def build_axis_context(
    pool: pd.DataFrame,
    public: pd.DataFrame,
    residuals: pd.DataFrame,
    bad_axes: pd.DataFrame,
    bad_moves: np.ndarray,
    good_moves: np.ndarray,
) -> dict[str, object]:
    flat = pool["flat_index"].astype(int).to_numpy()
    toxic_all, toxic_meta = h114mod.toxic_axis_matrix(axis_spec("residual_bad_plus_h102"), flat, public, residuals, bad_moves, bad_axes)
    toxic_named, named_meta = h114mod.toxic_axis_matrix(axis_spec("h010_e216_lejepa"), flat, public, residuals, bad_moves, bad_axes)
    good_axes = h114mod.good_axis_matrix(flat, good_moves)
    return {
        "flat": flat,
        "toxic_all": toxic_all,
        "toxic_named": toxic_named,
        "good_axes": good_axes,
        "toxic_meta": toxic_meta,
        "named_meta": named_meta,
    }


def action_features(
    move_flat: np.ndarray,
    shape: tuple[int, int],
    pool: pd.DataFrame,
    bad_axes: pd.DataFrame,
    bad_moves: np.ndarray,
    good_moves: np.ndarray,
    axes: dict[str, object],
) -> dict[str, float]:
    full = np.asarray(move_flat, dtype=np.float64).reshape(-1)
    mat = full.reshape(shape)
    flat = np.asarray(axes["flat"], dtype=int)
    m = full[flat]
    out: dict[str, float] = {}
    out["mean_abs"] = float(np.mean(np.abs(m)))
    out["mean_sq"] = float(np.mean(m * m))
    out["changed_share"] = float(np.mean(np.abs(m) > 1.0e-10))
    out["signed_mean"] = float(np.mean(m))
    out["pos_mean"] = float(np.mean(np.maximum(m, 0.0)))
    out["neg_mean"] = float(np.mean(np.maximum(-m, 0.0)))

    for target in TARGETS:
        idx = TARGETS.index(target)
        vals = mat[:, idx]
        out[f"{target}_signed"] = float(np.mean(vals))
        out[f"{target}_abs"] = float(np.mean(np.abs(vals)))
        out[f"{target}_sq"] = float(np.mean(vals * vals))
        out[f"{target}_pos"] = float(np.mean(np.maximum(vals, 0.0)))
        out[f"{target}_neg"] = float(np.mean(np.maximum(-vals, 0.0)))

    q = mat[:, [0, 1, 2]]
    s = mat[:, [3, 4, 5, 6]]
    out["q_abs"] = float(np.mean(np.abs(q)))
    out["s_abs"] = float(np.mean(np.abs(s)))
    out["q_sq"] = float(np.mean(q * q))
    out["s_sq"] = float(np.mean(s * s))
    out["qs_abs_balance"] = float(abs(out["q_abs"] - out["s_abs"]))
    out["q3_stage_coproduct"] = float(np.mean(mat[:, 2] * np.sum(s, axis=1)))
    out["q1q3_stage_abs_coproduct"] = float(np.mean(np.abs(np.sum(mat[:, [0, 2]], axis=1) * np.sum(s, axis=1))))
    out["stage_early_late_contrast"] = float(np.mean((mat[:, 3] + mat[:, 6]) - (mat[:, 4] + mat[:, 5])))
    out["stage_pair_energy"] = float(np.mean((mat[:, 3] + mat[:, 6]) ** 2 + (mat[:, 4] + mat[:, 5]) ** 2))

    row_l2 = np.sqrt(np.sum(mat * mat, axis=1))
    row_abs = np.sum(np.abs(mat), axis=1)
    out["row_l2_mean"] = float(np.mean(row_l2))
    out["row_l2_top10"] = float(np.mean(np.sort(row_l2)[-10:]))
    out["row_abs_top10"] = float(np.mean(np.sort(row_abs)[-10:]))
    out["active_rows_share"] = float(np.mean(row_abs > 1.0e-10))
    out["active_cells"] = float(np.sum(np.abs(mat) > 1.0e-10))
    out["row_multitarget_share"] = float(np.mean(np.sum(np.abs(mat) > 1.0e-10, axis=1) >= 2))

    h102 = h102mod.cumulative_axis_metrics(full, bad_axes, bad_moves, good_moves)
    out["bad_weighted_pos"] = float(h102["h102_cum_bad_weighted_pos"])
    out["bad_max_pos"] = float(h102["h102_cum_bad_max_pos"])
    out["h088_cos"] = float(h102["h102_cum_h088_axis_cos"])
    out["h088_cos_pos"] = float(max(h102["h102_cum_h088_axis_cos"], 0.0))
    out["good_max"] = float(h102["h102_cum_good_max_cos"])
    out["good_margin"] = float(h102["h102_cum_good_bad_margin"])

    toxic_all = np.asarray(axes["toxic_all"], dtype=np.float64)
    toxic_named = np.asarray(axes["toxic_named"], dtype=np.float64)
    good_ax = np.asarray(axes["good_axes"], dtype=np.float64)
    out["toxic_all_norm"] = float(np.linalg.norm(toxic_all @ m)) if toxic_all.size else 0.0
    out["toxic_named_norm"] = float(np.linalg.norm(toxic_named @ m)) if toxic_named.size else 0.0
    out["good_axis_norm"] = float(np.linalg.norm(good_ax @ m)) if good_ax.size else 0.0

    for col in ["h112_residual_toxicity", "h112_residual_safety", "h112_antidote_score", "h112_assignment_score"]:
        vals = pool[col].to_numpy(dtype=np.float64)
        out[f"{col}_weighted_abs"] = float(np.mean(np.abs(m) * vals))
        out[f"{col}_signed"] = float(np.mean(m * vals))
    return out


def feature_sets(all_cols: list[str]) -> dict[str, list[str]]:
    target_cols = [c for c in all_cols if any(c.startswith(f"{t}_") for t in TARGETS)]
    compact = [
        "mean_abs",
        "mean_sq",
        "changed_share",
        "q_abs",
        "s_abs",
        "q_sq",
        "s_sq",
        "qs_abs_balance",
        "row_l2_mean",
        "row_l2_top10",
        "row_multitarget_share",
        "bad_weighted_pos",
        "bad_max_pos",
        "h088_cos",
        "h088_cos_pos",
        "good_margin",
        "toxic_all_norm",
        "toxic_named_norm",
        "good_axis_norm",
    ]
    route = compact + [
        "q3_stage_coproduct",
        "q1q3_stage_abs_coproduct",
        "stage_early_late_contrast",
        "stage_pair_energy",
        "h112_residual_toxicity_weighted_abs",
        "h112_residual_safety_weighted_abs",
        "h112_antidote_score_weighted_abs",
        "h112_assignment_score_weighted_abs",
    ]
    target_route = route + target_cols
    return {
        "compact_curvature": [c for c in compact if c in all_cols],
        "route_curvature": [c for c in route if c in all_cols],
        "target_route_curvature": [c for c in target_route if c in all_cols],
    }


def fit_curvature_models(
    public: pd.DataFrame,
    pool: pd.DataFrame,
    base_shape: tuple[int, int],
    bad_axes: pd.DataFrame,
    bad_moves: np.ndarray,
    good_moves: np.ndarray,
    axes: dict[str, object],
) -> tuple[pd.DataFrame, pd.DataFrame, CurvatureFit]:
    moves = np.vstack(public["move_logit"].to_list()).astype(np.float64)
    y = public["delta_vs_h057"].to_numpy(dtype=np.float64)
    w = frontier_weights(public)
    feat_rows = [action_features(move, base_shape, pool, bad_axes, bad_moves, good_moves, axes) for move in moves]
    feat = pd.DataFrame(feat_rows).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    fsets = feature_sets(list(feat.columns))
    h088_idx = int(np.where(public["file"].astype(str).eq(H088_FILE).to_numpy())[0][0])
    base_idx = int(np.where(public["file"].astype(str).eq(BASE_FILE).to_numpy())[0][0])
    alphas = [0.03, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0]
    rows = []
    pred_rows = []
    fits: list[CurvatureFit] = []
    for name, cols in fsets.items():
        x = feat[cols].to_numpy(dtype=np.float64)
        for alpha in alphas:
            loo = np.zeros(len(y), dtype=np.float64)
            for held in range(len(y)):
                keep = np.ones(len(y), dtype=bool)
                keep[held] = False
                intercept, beta, mu, sd = fit_weighted_ridge(x[keep], y[keep], w[keep], alpha)
                tmp = CurvatureFit(name, float(alpha), cols, intercept, beta, mu, sd, loo, 0.0)
                loo[held] = predict_x(x[[held]], tmp)[0]
            err = loo - y
            abs_err = np.abs(err)
            weighted_mae = float(np.sum(w * abs_err) / np.sum(w))
            weighted_rmse = float(np.sqrt(np.sum(w * err * err) / np.sum(w)))
            h088_abs = float(abs_err[h088_idx])
            h088_sign_ok = float(np.sign(loo[h088_idx]) == np.sign(y[h088_idx]))
            base_abs = float(abs_err[base_idx])
            intercept, beta, mu, sd = fit_weighted_ridge(x, y, w, alpha)
            score = (
                weighted_mae
                + 0.50 * weighted_rmse
                + 1.45 * h088_abs
                + 0.75 * base_abs
                - 0.00012 * h097mod.pairwise_accuracy(y, loo)
                - 0.00010 * h097mod.spearman(y, loo)
                - 0.00035 * h088_sign_ok
            )
            fit = CurvatureFit(name, float(alpha), cols, intercept, beta, mu, sd, loo.copy(), float(score))
            fits.append(fit)
            rows.append(
                {
                    "feature_set": name,
                    "alpha": float(alpha),
                    "n_features": len(cols),
                    "loo_mae": float(np.mean(abs_err)),
                    "loo_rmse": float(np.sqrt(np.mean(err * err))),
                    "weighted_loo_mae": weighted_mae,
                    "weighted_loo_rmse": weighted_rmse,
                    "loo_spearman": h097mod.spearman(y, loo),
                    "loo_pair_acc": h097mod.pairwise_accuracy(y, loo),
                    "h088_loo_pred": float(loo[h088_idx]),
                    "h088_loo_abs_error": h088_abs,
                    "h088_sign_ok": h088_sign_ok,
                    "base_loo_abs_error": base_abs,
                    "h115_model_score": score,
                }
            )
            for i, rec in public[["file", "public_lb", "delta_vs_h057"]].iterrows():
                pred_rows.append(
                    {
                        "feature_set": name,
                        "alpha": float(alpha),
                        "file": str(rec["file"]),
                        "public_lb": float(rec["public_lb"]),
                        "delta_vs_h057": float(rec["delta_vs_h057"]),
                        "frontier_weight": float(w[i]),
                        "loo_pred_delta": float(loo[i]),
                        "loo_error": float(loo[i] - rec["delta_vs_h057"]),
                    }
                )
    scores = pd.DataFrame(rows).sort_values(["h115_model_score", "h088_loo_abs_error"], ascending=[True, True]).reset_index(drop=True)
    best = scores.iloc[0]
    fit = next(f for f in fits if f.feature_set == str(best["feature_set"]) and abs(f.alpha - float(best["alpha"])) < 1.0e-12)
    return scores, pd.DataFrame(pred_rows), fit


def predict_curvature(move_mat: np.ndarray, fit: CurvatureFit, pool: pd.DataFrame, bad_axes: pd.DataFrame, bad_moves: np.ndarray, good_moves: np.ndarray, axes: dict[str, object]) -> float:
    feats = action_features(move_mat.reshape(-1), move_mat.shape, pool, bad_axes, bad_moves, good_moves, axes)
    x = pd.DataFrame([{col: feats.get(col, 0.0) for col in fit.cols}]).to_numpy(dtype=np.float64)
    return float(predict_x(x, fit)[0])


def candidate_specs() -> list[H115Spec]:
    return [
        H115Spec(
            name="curv_h010_e216_antidote_c60_a070",
            group="h010_e216_antidote",
            max_cells=60,
            max_rows=36,
            max_per_subject=10,
            max_per_target=22,
            q2_cap=0,
            amp=0.70,
            cap=0.25,
            proposal_top=150,
            max_curv_pred=0.000020,
            max_marginal=0.000020,
            max_bad_weighted_pos=0.006,
            max_bad_max_pos=0.038,
            max_h088_cos=-0.004,
            min_good_margin=0.006,
            route_pred_cap=0.000120,
            h098_pred_cap=0.000090,
            min_proposal_score=0.10,
            worldview="H010/E216 antidote actions are only safe when second-order row/target curvature remains low",
        ),
        H115Spec(
            name="curv_h112_pruned_c52_a060",
            group="h112_pruned",
            max_cells=52,
            max_rows=28,
            max_per_subject=10,
            max_per_target=18,
            q2_cap=0,
            amp=0.60,
            cap=0.22,
            proposal_top=140,
            max_curv_pred=0.000010,
            max_marginal=0.000018,
            max_bad_weighted_pos=0.006,
            max_bad_max_pos=0.036,
            max_h088_cos=-0.004,
            min_good_margin=0.008,
            route_pred_cap=0.000120,
            h098_pred_cap=0.000090,
            min_proposal_score=0.12,
            worldview="H112 cell residual toxicity is useful, but second-order target/row curvature must prune the action",
        ),
        H115Spec(
            name="curv_novel_guarded_c36_a050",
            group="novel_guarded",
            max_cells=36,
            max_rows=30,
            max_per_subject=8,
            max_per_target=14,
            q2_cap=0,
            amp=0.50,
            cap=0.18,
            proposal_top=110,
            max_curv_pred=0.000000,
            max_marginal=0.000012,
            max_bad_weighted_pos=0.004,
            max_bad_max_pos=0.032,
            max_h088_cos=-0.004,
            min_good_margin=0.004,
            route_pred_cap=0.000160,
            h098_pred_cap=0.000110,
            min_proposal_score=0.02,
            worldview="H114 novelty can survive only if second-order curvature explicitly says the row/target energy is safe",
        ),
        H115Spec(
            name="curv_q2_companion_c22_a035",
            group="q2_companion",
            max_cells=22,
            max_rows=16,
            max_per_subject=6,
            max_per_target=12,
            q2_cap=8,
            amp=0.35,
            cap=0.14,
            proposal_top=90,
            max_curv_pred=0.000010,
            max_marginal=0.000012,
            max_bad_weighted_pos=0.004,
            max_bad_max_pos=0.030,
            max_h088_cos=-0.002,
            min_good_margin=0.004,
            route_pred_cap=0.000240,
            h098_pred_cap=0.000110,
            min_proposal_score=0.00,
            worldview="Q2 can re-enter only as a low-curvature companion, not as an independent target route",
        ),
        H115Spec(
            name="curv_publicbad_broad_c80_a045",
            group="publicbad_broad",
            max_cells=80,
            max_rows=44,
            max_per_subject=10,
            max_per_target=24,
            q2_cap=0,
            amp=0.45,
            cap=0.18,
            proposal_top=190,
            max_curv_pred=0.000030,
            max_marginal=0.000022,
            max_bad_weighted_pos=0.010,
            max_bad_max_pos=0.050,
            max_h088_cos=-0.002,
            min_good_margin=0.004,
            route_pred_cap=0.000180,
            h098_pred_cap=0.000110,
            min_proposal_score=0.06,
            worldview="a broad public-bad-null action is safe only when second-order concentration penalties are low",
        ),
    ]


def load_selected_proposals(path: Path, move_col: str, source_prefix: str) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    if move_col not in df.columns:
        return pd.DataFrame()
    out = df.copy()
    out["proposal_move"] = out[move_col].to_numpy(dtype=np.float64)
    out["proposal_source"] = source_prefix + "::" + out["candidate_id"].astype(str)
    return out


def build_proposals(pool: pd.DataFrame) -> pd.DataFrame:
    frames = []
    base = pool.copy()
    base["proposal_move"] = base["h112_candidate_raw_move"].to_numpy(dtype=np.float64)
    base["proposal_source"] = "h112_pool"
    frames.append(base)
    frames.append(load_selected_proposals(HITL / "h112_public_residual_toxicity_solver_hsjepa" / "h112_selected_cells.csv", "h112_move", "h112_selected"))
    frames.append(load_selected_proposals(HITL / "h113_row_route_equation_solver_hsjepa" / "h113_selected_cells.csv", "h112_move", "h113_selected"))
    frames.append(load_selected_proposals(HITL / "h114_toxic_subspace_null_solver_hsjepa" / "h114_selected_cells.csv", "h114_null_move", "h114_selected"))
    props = pd.concat([f for f in frames if not f.empty], ignore_index=True, sort=False)
    if "candidate_id" in props.columns:
        props = props.rename(columns={"candidate_id": "source_candidate_id"})
    props = props[np.abs(props["proposal_move"].to_numpy(dtype=np.float64)) > 1.0e-12].copy()
    props["proposal_base_score"] = (
        0.26 * rank01(props["h112_assignment_score"].to_numpy(dtype=np.float64), high=True)
        + 0.22 * rank01(props["h112_residual_safety"].to_numpy(dtype=np.float64), high=True)
        + 0.16 * rank01(props["h112_residual_gap"].to_numpy(dtype=np.float64), high=True)
        + 0.16 * rank01(props["h112_antidote_score"].to_numpy(dtype=np.float64), high=True)
        + 0.08 * props["h112_in_h111_selected"].to_numpy(dtype=np.float64)
        + 0.07 * props["h111_h108_rejected"].to_numpy(dtype=np.float64)
        - 0.20 * rank01(props["h112_residual_toxicity"].to_numpy(dtype=np.float64), high=True)
        - 0.05 * props["target"].astype(str).eq("Q2").astype(float).to_numpy()
    )
    return props


def group_allowed(props: pd.DataFrame, spec: H115Spec) -> np.ndarray:
    target = props["target"].astype(str)
    src = props["proposal_source"].astype(str)
    base = props["proposal_base_score"].to_numpy(dtype=np.float64) >= spec.min_proposal_score
    if spec.group == "h010_e216_antidote":
        return base & target.ne("Q2").to_numpy() & (
            src.str.contains("h010_e216", regex=False).to_numpy()
            | (props["h112_antidote_score"].to_numpy(dtype=np.float64) >= 0.48)
        )
    if spec.group == "h112_pruned":
        return base & target.ne("Q2").to_numpy() & (
            src.str.contains("h112", regex=False).to_numpy()
            | (props["h112_in_h111_selected"].to_numpy(dtype=np.float64) > 0.5)
        )
    if spec.group == "novel_guarded":
        return base & target.ne("Q2").to_numpy() & (
            src.str.contains("novel_lowoverlap", regex=False).to_numpy()
            | (props["h112_in_h111_selected"].to_numpy(dtype=np.float64) < 0.5)
        )
    if spec.group == "q2_companion":
        return base & target.isin(["Q1", "Q2", "Q3", "S1", "S3"]).to_numpy() & (
            src.str.contains("q2_companion", regex=False).to_numpy()
            | target.eq("Q2").to_numpy()
        )
    if spec.group == "publicbad_broad":
        return base & target.ne("Q2").to_numpy()
    raise ValueError(spec.group)


def select_with_curvature(
    props: pd.DataFrame,
    spec: H115Spec,
    fit: CurvatureFit,
    pool: pd.DataFrame,
    shape: tuple[int, int],
    bad_axes: pd.DataFrame,
    bad_moves: np.ndarray,
    good_moves: np.ndarray,
    axes: dict[str, object],
) -> tuple[pd.DataFrame, np.ndarray, dict[str, float], dict[str, float]]:
    work = props[group_allowed(props, spec)].copy()
    if work.empty:
        empty = np.zeros(shape, dtype=np.float64)
        return pd.DataFrame(), empty, h102mod.cumulative_axis_metrics(empty.reshape(-1), bad_axes, bad_moves, good_moves), {}
    single_preds = []
    for rec in work.to_dict("records"):
        tmp = np.zeros(shape, dtype=np.float64)
        tmp[int(rec["row"]), int(rec["target_index"])] = float(np.clip(float(rec["proposal_move"]) * spec.amp, -spec.cap, spec.cap))
        single_preds.append(predict_curvature(tmp, fit, pool, bad_axes, bad_moves, good_moves, axes))
    work["h115_single_curv_pred"] = single_preds
    work["h115_proposal_move"] = np.clip(work["proposal_move"].to_numpy(dtype=np.float64) * spec.amp, -spec.cap, spec.cap)
    work["h115_proposal_score"] = (
        0.45 * work["proposal_base_score"].to_numpy(dtype=np.float64)
        + 0.22 * rank01(-work["h115_single_curv_pred"].to_numpy(dtype=np.float64), high=True)
        + 0.12 * rank01(np.abs(work["h115_proposal_move"].to_numpy(dtype=np.float64)), high=True)
        + 0.10 * rank01(work["h112_antidote_score"].to_numpy(dtype=np.float64), high=True)
        - 0.16 * rank01(work["h112_residual_toxicity"].to_numpy(dtype=np.float64), high=True)
    )
    work = work.sort_values(["h115_proposal_score", "h112_assignment_score"], ascending=[False, False]).head(spec.proposal_top).reset_index(drop=True)

    move_mat = np.zeros(shape, dtype=np.float64)
    selected_idx: list[int] = []
    selected_rows: set[int] = set()
    selected_flat: set[int] = set()
    subject_counts: dict[str, int] = {}
    target_counts: dict[str, int] = {}
    q2_count = 0
    curv_now = predict_curvature(move_mat, fit, pool, bad_axes, bad_moves, good_moves, axes)
    axis = h102mod.cumulative_axis_metrics(move_mat.reshape(-1), bad_axes, bad_moves, good_moves)
    for idx, rec in enumerate(work.to_dict("records")):
        flat = int(rec["flat_index"])
        if flat in selected_flat:
            continue
        if len(selected_idx) >= spec.max_cells:
            break
        row = int(rec["row"])
        subject = str(rec["subject_id"])
        target = str(rec["target"])
        tidx = int(rec["target_index"])
        if row not in selected_rows and len(selected_rows) >= spec.max_rows:
            continue
        if row not in selected_rows and subject_counts.get(subject, 0) + 1 > spec.max_per_subject:
            continue
        if target_counts.get(target, 0) >= spec.max_per_target:
            continue
        if target == "Q2" and q2_count >= spec.q2_cap:
            continue
        tmp = move_mat.copy()
        tmp[row, tidx] = float(rec["h115_proposal_move"])
        cand_axis = h102mod.cumulative_axis_metrics(tmp.reshape(-1), bad_axes, bad_moves, good_moves)
        if cand_axis["h102_cum_bad_weighted_pos"] > spec.max_bad_weighted_pos:
            continue
        if cand_axis["h102_cum_bad_max_pos"] > spec.max_bad_max_pos:
            continue
        if cand_axis["h102_cum_h088_axis_cos"] > spec.max_h088_cos:
            continue
        if cand_axis["h102_cum_good_bad_margin"] < spec.min_good_margin:
            continue
        curv_next = predict_curvature(tmp, fit, pool, bad_axes, bad_moves, good_moves, axes)
        if curv_next > spec.max_curv_pred:
            continue
        if selected_idx and (curv_next - curv_now) > spec.max_marginal:
            continue
        move_mat = tmp
        axis = cand_axis
        curv_now = curv_next
        selected_idx.append(idx)
        selected_flat.add(flat)
        if row not in selected_rows:
            selected_rows.add(row)
            subject_counts[subject] = subject_counts.get(subject, 0) + 1
        target_counts[target] = target_counts.get(target, 0) + 1
        q2_count += int(target == "Q2")

    if not selected_idx:
        return pd.DataFrame(), move_mat, axis, {"h115_curvature_pred_delta_vs_h057": curv_now}
    selected = work.iloc[selected_idx].copy().sort_values(["row", "target_index"]).reset_index(drop=True)
    selected["h112_move"] = [
        move_mat[int(row), int(tidx)]
        for row, tidx in zip(selected["row"].astype(int), selected["target_index"].astype(int))
    ]
    selected["h097_move_col"] = "h112_move"
    diag = {
        "h115_curvature_pred_delta_vs_h057": curv_now,
        "h115_start_curvature_pred_delta_vs_h057": predict_curvature(np.zeros(shape, dtype=np.float64), fit, pool, bad_axes, bad_moves, good_moves, axes),
        "h115_mean_single_curvature_pred": float(selected["h115_single_curv_pred"].mean()),
        "h115_mean_proposal_score": float(selected["h115_proposal_score"].mean()),
        "h115_unique_sources": int(selected["proposal_source"].nunique()),
    }
    return selected, move_mat, axis, diag


def evaluate_candidate(
    candidate_id: str,
    prob: np.ndarray,
    move_mat: np.ndarray,
    selected_cells: pd.DataFrame,
    cell: pd.DataFrame,
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    h098_fit: h097mod.ResponseFit,
    route_fit: h100mod.RouteBasisFit,
    basis_fit_df: pd.DataFrame,
    basis_fit_moves: np.ndarray,
    spec: H115Spec,
    path: Path,
    axis: dict[str, float],
    diag: dict[str, float],
    previous: dict[str, np.ndarray | None],
) -> dict[str, object]:
    proxy = h112mod.H112Spec(
        name=spec.name,
        group=spec.group,
        max_cells=spec.max_cells,
        max_rows=spec.max_rows,
        max_per_subject=spec.max_per_subject,
        max_per_target=spec.max_per_target,
        q2_cap=spec.q2_cap,
        amp=spec.amp,
        cap=spec.cap,
        pool_top=spec.proposal_top,
        beam_width=1,
        min_score=spec.min_proposal_score,
        min_gap=-1.0,
        max_residual_toxicity=1.0,
        min_residual_safety=0.0,
        min_family_count=1,
        max_bad_weighted_pos=spec.max_bad_weighted_pos,
        max_bad_max_pos=spec.max_bad_max_pos,
        max_h088_cos=spec.max_h088_cos,
        min_good_margin=spec.min_good_margin,
        route_pred_cap=spec.route_pred_cap,
        h098_pred_cap=spec.h098_pred_cap,
        worldview=spec.worldview,
    )
    out = h112mod.evaluate_candidate(
        candidate_id,
        prob,
        move_mat,
        selected_cells,
        cell,
        sample,
        base_prob,
        h098_fit,
        route_fit,
        basis_fit_df,
        basis_fit_moves,
        proxy,
        path,
        axis,
    )
    move_flat = move_mat.reshape(-1)
    for label, prev in previous.items():
        out[f"h115_{label}_overlap_cells"] = overlap_count(move_flat, prev)
        out[f"h115_{label}_cosine"] = cosine(move_flat, prev)
    out.update(diag)
    novelty = max(0.0, min(1.0, 1.0 - abs(float(out.get("h115_h112_cosine", 0.0)))))
    curv = float(out["h115_curvature_pred_delta_vs_h057"])
    out["h115_novelty_vs_h112"] = novelty
    out["h115_curvature_quality"] = max(0.0, min(1.0, 1.0 - max(curv, 0.0) / 0.0002))
    out["h115_score"] = (
        130.0 * (-curv)
        + 80.0 * (-float(out["model_pred_delta_vs_h057"]))
        + 80.0 * (-float(out["route_basis_pred_delta_vs_h057"]))
        + 0.16 * float(out["selected_mean_residual_safety"])
        + 0.12 * float(out["selected_mean_residual_gap"])
        + 0.10 * float(out["selected_mean_antidote_score"])
        + 0.08 * novelty
        + 0.06 * max(-float(out["h102_cum_h088_axis_cos"]), 0.0)
        - 0.18 * float(out["selected_mean_residual_toxicity"])
        - 0.55 * max(float(out["h102_cum_bad_weighted_pos"]), 0.0)
        - 0.28 * max(float(out["h102_cum_bad_max_pos"]), 0.0)
        - 0.14 * max(float(out["h102_cum_h088_axis_cos"]), 0.0)
        - 18.0 * max(float(out["hard_diag_delta_vs_h057"]), 0.0)
    )
    return out


def run() -> None:
    cleanup_previous_outputs()
    pool, public, sample, base_prob, cell, h098_fit, route_fit, basis_fit_df, basis_fit_moves, bad_axes, bad_moves, good_moves, residuals = prepare_context()
    axes = build_axis_context(pool, public, residuals, bad_axes, bad_moves, good_moves)
    model_scores, loo_preds, fit = fit_curvature_models(public, pool, base_prob.shape, bad_axes, bad_moves, good_moves, axes)
    props = build_proposals(pool)
    previous = {
        "h114": load_previous_move(sample, base_prob, "submission_h114_nullspace_*_uploadsafe.csv"),
        "h113": load_previous_move(sample, base_prob, "submission_h113_rowroute_*_uploadsafe.csv"),
        "h112": load_previous_move(sample, base_prob, "submission_h112_residualtox_*_uploadsafe.csv"),
        "h111": load_previous_move(sample, base_prob, "submission_h111_boundary_*_uploadsafe.csv"),
    }

    candidate_rows = []
    selected_frames = []
    for spec in candidate_specs():
        selected, move_mat, axis, diag = select_with_curvature(props, spec, fit, pool, base_prob.shape, bad_axes, bad_moves, good_moves, axes)
        if selected.empty:
            continue
        rpred = route_pred(move_mat.reshape(-1), basis_fit_df, basis_fit_moves, route_fit)
        cpred = h098_pred(move_mat.reshape(-1), cell, h098_fit)
        if rpred > spec.route_pred_cap or cpred > spec.h098_pred_cap:
            continue
        prob = materialize(base_prob, move_mat)
        if int((np.abs(prob - base_prob) > TOL).sum()) == 0:
            continue
        hash_id = short_hash(prob)
        candidate_id = safe_id(f"h115_{spec.name}_{hash_id}", 128)
        path = OUT / f"submission_{candidate_id}.csv"
        h085mod.write_submission(sample, prob, path)
        metrics = evaluate_candidate(
            candidate_id,
            prob,
            move_mat,
            selected,
            cell,
            sample,
            base_prob,
            h098_fit,
            route_fit,
            basis_fit_df,
            basis_fit_moves,
            spec,
            path,
            axis,
            diag,
            previous,
        )
        metrics["h115_fit_feature_set"] = fit.feature_set
        metrics["h115_fit_alpha"] = fit.alpha
        metrics["h115_fit_score"] = fit.score
        candidate_rows.append(metrics)
        selected2 = selected.copy()
        if "candidate_id" in selected2.columns:
            selected2 = selected2.drop(columns=["candidate_id"])
        selected2.insert(0, "candidate_id", candidate_id)
        selected_frames.append(selected2)

    candidates = pd.DataFrame(candidate_rows)
    if candidates.empty:
        raise RuntimeError("no H115 candidates")
    candidates = candidates.sort_values(["h115_score", "h115_curvature_pred_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True)
    selected = candidates.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"submission_h115_curvature_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)

    decision = {
        "decision": "promote_h115_second_order_action_equation",
        "selected_candidate_id": selected["candidate_id"],
        "root_uploadsafe_path": str(root_path.resolve()),
        "worldview": selected["worldview"],
        "selected_fit_feature_set": fit.feature_set,
        "selected_fit_alpha": fit.alpha,
        "selected_fit_score": fit.score,
        **selected,
        **{f"root_{key}": value for key, value in validation.items()},
    }

    model_scores.to_csv(OUT / "h115_curvature_model_scores.csv", index=False)
    loo_preds.to_csv(OUT / "h115_curvature_loo_predictions.csv", index=False)
    props.to_csv(OUT / "h115_proposal_pool.csv", index=False)
    candidates.to_csv(OUT / "h115_candidates.csv", index=False)
    pd.concat(selected_frames, ignore_index=True).to_csv(OUT / "h115_selected_cells.csv", index=False)
    pd.DataFrame([decision]).to_csv(OUT / "h115_decision.csv", index=False)

    cols = [
        "candidate_id",
        "spec_name",
        "selected_cells",
        "changed_rows_vs_h057",
        "Q1_changed_vs_h057",
        "Q2_changed_vs_h057",
        "Q3_changed_vs_h057",
        "S1_changed_vs_h057",
        "S2_changed_vs_h057",
        "S3_changed_vs_h057",
        "S4_changed_vs_h057",
        "h115_curvature_pred_delta_vs_h057",
        "model_pred_delta_vs_h057",
        "route_basis_pred_delta_vs_h057",
        "h102_cum_bad_weighted_pos",
        "h102_cum_h088_axis_cos",
        "selected_mean_residual_toxicity",
        "selected_mean_residual_safety",
        "selected_mean_residual_gap",
        "h115_h114_overlap_cells",
        "h115_h114_cosine",
        "h115_h112_overlap_cells",
        "h115_h112_cosine",
        "h115_novelty_vs_h112",
        "h115_score",
        "file",
    ]
    report = f"""# H115 Second-Order Action-Equation HS-JEPA

Question: is the current plateau caused by H098-style linear public response
missing target/row curvature toxicity?

Selected curvature model:

{md_table(model_scores.head(10), 10)}

Candidates:

{md_table(candidates[cols], 20)}

Decision:

{md_table(pd.DataFrame([decision]), 1)}

Interpretation rule:

- If H115 improves over H112-H114, the action decoder needs second-order
  target/row curvature, not only linear public response or toxic subspace.
- If H114 wins and H115 loses, the nonlinear curvature fit over-constrained the
  nullspace discovery.
- If H112/H113 win, local residual toxicity remains the cleaner action field.
"""
    (OUT / "h115_report.md").write_text(report, encoding="utf-8")

    print("H115 selected candidate")
    print(candidates[cols].head(10).to_string(index=False))
    print("\nDecision")
    print(pd.DataFrame([decision])[["decision", "selected_candidate_id", "root_uploadsafe_path", "root_upload_safe"]].to_string(index=False))


if __name__ == "__main__":
    run()
