#!/usr/bin/env python3
"""H098: frontier-weighted signed action equation HS-JEPA.

H097 learned the broad public leaderboard response but failed the important
frontier stress: H088 was predicted in the wrong direction under LOO.

H098 keeps the same signed action-equation representation, but changes the
sensor weighting.  Frontier observations near H057/H042/H050/H012/H088 dominate
the fit; older 0.576-0.581 submissions become weak background constraints.
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
OUT = HITL / "h098_frontier_weighted_action_equation_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H097_PATH = HITL / "h097_signed_public_action_equation_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h097mod", H097_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H097_PATH}")
h097mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h097mod
SPEC.loader.exec_module(h097mod)

h095mod = h097mod.h095mod
h085mod = h097mod.h085mod
h087mod = h097mod.h087mod

TARGETS = h097mod.TARGETS
KEYS = h097mod.KEYS
BASE_FILE = h097mod.BASE_FILE
BASE_LB = h097mod.BASE_LB
TOL = h097mod.TOL
H088_FILE = h095mod.H088_FILE


@dataclass(frozen=True)
class H098Spec:
    name: str
    mode: str
    target_group: str
    k: int
    alpha: float
    cap: float
    min_score: float
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
    for path in OUT.glob("submission_h098_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h098_frontier_equation_*_uploadsafe.csv"):
        path.unlink()


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


def evaluate_weighted_models(public: pd.DataFrame, cell: pd.DataFrame, feature_sets: dict[str, list[str]]) -> tuple[pd.DataFrame, pd.DataFrame, h097mod.ResponseFit]:
    moves = np.vstack(public["move_logit"].to_list()).astype(np.float64)
    y = public["delta_vs_h057"].to_numpy(dtype=np.float64)
    w = frontier_weights(public)
    h088_idx = int(np.where(public["file"].astype(str).eq(H088_FILE).to_numpy())[0][0])
    base_idx = int(np.where(public["file"].astype(str).eq(BASE_FILE).to_numpy())[0][0])
    alphas = [0.003, 0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0, 100.0]
    rows = []
    pred_rows = []
    fits: list[h097mod.ResponseFit] = []

    for feature_set, cols in feature_sets.items():
        x, x_cols, _f = h097mod.build_design_for_moves(moves, cell, cols)
        if x.shape[1] > 120:
            variances = np.nanvar(x, axis=0)
            keep = np.argsort(variances)[-120:]
            x = x[:, keep]
            x_cols = [x_cols[i] for i in keep]
        for alpha in alphas:
            loo = np.zeros(len(y), dtype=np.float64)
            for held in range(len(y)):
                keep_mask = np.ones(len(y), dtype=bool)
                keep_mask[held] = False
                intercept, beta, mu, sd = fit_weighted_ridge(x[keep_mask], y[keep_mask], w[keep_mask], alpha)
                loo[held] = h097mod.predict_x(x[[held]], intercept, beta, mu, sd)[0]
            err = loo - y
            abs_err = np.abs(err)
            weighted_mae = float(np.sum(w * abs_err) / np.sum(w))
            weighted_rmse = float(np.sqrt(np.sum(w * err * err) / np.sum(w)))
            h088_error = float(err[h088_idx])
            h088_abs = float(abs_err[h088_idx])
            h088_sign_ok = float(np.sign(loo[h088_idx]) == np.sign(y[h088_idx]))
            base_abs = float(abs_err[base_idx])
            intercept, beta, mu, sd = fit_weighted_ridge(x, y, w, alpha)
            full_pred = h097mod.predict_x(x, intercept, beta, mu, sd)
            fit = h097mod.ResponseFit(
                feature_set=feature_set,
                alpha=float(alpha),
                cell_cols=cols,
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
            rows.append(
                {
                    "feature_set": feature_set,
                    "alpha": float(alpha),
                    "n_x_features": len(x_cols),
                    "loo_mae": fit.loo_mae,
                    "loo_rmse": fit.loo_rmse,
                    "weighted_loo_mae": weighted_mae,
                    "weighted_loo_rmse": weighted_rmse,
                    "loo_spearman": fit.loo_spearman,
                    "loo_pair_acc": fit.loo_pair_acc,
                    "h088_loo_pred": float(loo[h088_idx]),
                    "h088_loo_error": h088_error,
                    "h088_loo_abs_error": h088_abs,
                    "h088_sign_ok": h088_sign_ok,
                    "base_loo_abs_error": base_abs,
                    "full_fit_weighted_mae": float(np.sum(w * np.abs(full_pred - y)) / np.sum(w)),
                    "frontier_rank_score": weighted_mae
                    + 0.45 * weighted_rmse
                    + 1.60 * h088_abs
                    + 0.65 * base_abs
                    - 0.00018 * fit.loo_pair_acc
                    - 0.00010 * fit.loo_spearman
                    - 0.00035 * h088_sign_ok,
                }
            )
            for i, rec in public[["file", "public_lb", "delta_vs_h057"]].iterrows():
                pred_rows.append(
                    {
                        "feature_set": feature_set,
                        "alpha": float(alpha),
                        "file": str(rec["file"]),
                        "public_lb": float(rec["public_lb"]),
                        "delta_vs_h057": float(rec["delta_vs_h057"]),
                        "frontier_weight": float(w[i]),
                        "loo_pred_delta": float(loo[i]),
                        "loo_error": float(loo[i] - rec["delta_vs_h057"]),
                    }
                )

    scores = pd.DataFrame(rows).sort_values(["frontier_rank_score", "h088_loo_abs_error"], ascending=[True, True]).reset_index(drop=True)
    selected_row = scores.iloc[0]
    selected = next(
        fit
        for fit in fits
        if fit.feature_set == str(selected_row["feature_set"]) and abs(fit.alpha - float(selected_row["alpha"])) < 1.0e-12
    )
    return scores, pd.DataFrame(pred_rows), selected


def build_frontier_pool(cell: pd.DataFrame, gradient: np.ndarray) -> pd.DataFrame:
    pool = h097mod.build_action_pool(cell, gradient)
    descent_move = pool["h097_descent_logit_move"].to_numpy(dtype=np.float64)
    h088_move = pool["h088_logit_move"].to_numpy(dtype=np.float64)
    h057_move = pool["h057_positive_logit_move"].to_numpy(dtype=np.float64)
    anti_h088 = (np.sign(descent_move) * np.sign(h088_move) < 0).astype(float)
    align_h057 = (
        (np.sign(descent_move) * np.sign(h057_move) > 0)
        & (pool["h057_positive_weight"].to_numpy(dtype=np.float64) > 0)
    ).astype(float)
    pool["h098_frontier_cell_score"] = (
        0.28 * rank01(np.abs(pool["h097_gradient"].to_numpy(dtype=np.float64)), high=True)
        + 0.18 * anti_h088 * pool["h088_toxicity"].to_numpy(dtype=np.float64)
        + 0.17 * align_h057 * pool["h057_positive_weight"].to_numpy(dtype=np.float64)
        + 0.15 * pool["h057_h088_anti_conflict"].to_numpy(dtype=np.float64)
        + 0.10 * pool["h095_safe_cell_score"].to_numpy(dtype=np.float64)
        + 0.06 * pool["source_agrees_h085"].to_numpy(dtype=np.float64)
        + 0.05 * pool["h082_cell"].to_numpy(dtype=np.float64)
        - 0.15 * pool["h080_bad_same_rank"].to_numpy(dtype=np.float64)
        - 0.10 * pool["is_h050_null"].to_numpy(dtype=np.float64)
    )
    return pool.sort_values("h098_frontier_cell_score", ascending=False).reset_index(drop=True)


def candidate_specs() -> list[H098Spec]:
    return [
        H098Spec(
            name="frontier_descent_all_c220_a040",
            mode="signed_descent",
            target_group="all",
            k=220,
            alpha=0.40,
            cap=0.52,
            min_score=0.35,
            worldview="frontier-weighted action gradient yields a broad signed descent field",
        ),
        H098Spec(
            name="frontier_counter_h088_c180_a045",
            mode="counter_h088",
            target_group="all",
            k=180,
            alpha=0.45,
            cap=0.55,
            min_score=0.36,
            worldview="H088 failed action should be inverted where frontier model agrees",
        ),
        H098Spec(
            name="frontier_conflict_c83_a052",
            mode="conflict_invert",
            target_group="conflict",
            k=83,
            alpha=0.52,
            cap=0.68,
            min_score=0.32,
            worldview="frontier equation keeps the H096 conflict field but uses lower amplitude",
        ),
        H098Spec(
            name="frontier_objective_c160_a045",
            mode="signed_descent",
            target_group="objective_plus_q3",
            k=160,
            alpha=0.45,
            cap=0.54,
            min_score=0.34,
            worldview="frontier sensor localizes the signed field to Q3/S objective routes",
        ),
        H098Spec(
            name="frontier_q2_c85_a060",
            mode="signed_descent",
            target_group="q2",
            k=85,
            alpha=0.60,
            cap=0.78,
            min_score=0.34,
            worldview="frontier model reopens only Q2 hardtail-safe cells",
        ),
    ]


def select_cells(pool: pd.DataFrame, spec: H098Spec) -> pd.DataFrame:
    pool2 = pool.copy()
    pool2["h097_cell_score"] = pool2["h098_frontier_cell_score"]
    selected = h097mod.select_cells(pool2, spec)
    if selected.empty:
        return selected
    selected["h098_frontier_cell_score"] = selected["h097_cell_score"]
    return selected


def run() -> None:
    cleanup_previous_outputs()
    base = h085mod.load_sub(BASE_FILE)
    sample = base[KEYS].copy()
    base_prob = base[TARGETS].to_numpy(dtype=np.float64)
    cell_raw = h097mod.ensure_h095_cell_table(sample, base_prob)
    cell, feature_sets = h097mod.add_context_features(cell_raw, sample)
    public = h097mod.load_public_moves(sample, base_prob)
    model_scores, pred_rows, fit = evaluate_weighted_models(public, cell, feature_sets)
    gradient = h097mod.response_gradient(cell, fit)
    pool = build_frontier_pool(cell, gradient)

    candidate_rows = []
    selected_frames = []
    for spec in candidate_specs():
        selected = select_cells(pool, spec)
        if selected.empty:
            continue
        prob, move_mat = h097mod.materialize_candidate(base_prob, selected, spec)
        if int((np.abs(prob - base_prob) > TOL).sum()) == 0:
            continue
        hash_id = short_hash(prob)
        candidate_id = safe_id(f"h098_{spec.name}_{hash_id}", 128)
        path = OUT / f"submission_{candidate_id}.csv"
        h085mod.write_submission(sample, prob, path)
        metrics = h097mod.evaluate_candidate(candidate_id, prob, move_mat, base_prob, selected, cell, sample, fit, spec, path)
        metrics["h098_frontier_score"] = (
            250.0 * (-float(metrics["model_pred_delta_vs_h057"]))
            + 0.18 * float(metrics["anti_h088_direction_rate"])
            + 0.15 * float(metrics["h057_positive_align_rate"])
            + 0.12 * float(metrics["selected_conflict_rate"])
            + 0.10 * max(float(metrics["cos_h057_vs_h042_direction"]), 0.0)
            - 0.20 * max(float(metrics["cos_h088_direction"]), 0.0)
            - 0.24 * float(metrics["max_positive_bad_cosine"])
            - 20.0 * max(float(metrics["hard_diag_delta_vs_h057"]), 0.0)
        )
        candidate_rows.append(metrics)
        selected = selected.copy()
        selected.insert(0, "candidate_id", candidate_id)
        selected_frames.append(selected)

    candidates = pd.DataFrame(candidate_rows)
    if candidates.empty:
        raise RuntimeError("no H098 candidates")
    candidates = candidates.sort_values(["h098_frontier_score", "model_pred_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True)
    selected = candidates.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"submission_h098_frontier_equation_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)

    selected_model_row = model_scores.iloc[0].to_dict()
    decision = {
        "decision": "promote_h098_frontier_weighted_action_equation",
        "selected_candidate_id": selected["candidate_id"],
        "root_uploadsafe_path": str(root_path.resolve()),
        "worldview": selected["worldview"],
        "response_feature_set": fit.feature_set,
        "response_alpha": fit.alpha,
        **{f"response_{k}": v for k, v in selected_model_row.items() if k not in {"feature_set", "alpha"}},
        **selected,
        **{f"root_{key}": value for key, value in validation.items()},
    }

    public_out = public.drop(columns=["move_logit"]).copy()
    public_out["frontier_weight"] = frontier_weights(public)
    public_out.to_csv(OUT / "h098_public_moves_weighted.csv", index=False)
    model_scores.to_csv(OUT / "h098_frontier_model_scores.csv", index=False)
    pred_rows.to_csv(OUT / "h098_frontier_loo_predictions.csv", index=False)
    pool.to_csv(OUT / "h098_action_pool.csv", index=False)
    candidates.to_csv(OUT / "h098_candidates.csv", index=False)
    pd.concat(selected_frames, ignore_index=True).to_csv(OUT / "h098_selected_cells.csv", index=False)
    pd.DataFrame([decision]).to_csv(OUT / "h098_decision.csv", index=False)

    cols = [
        "candidate_id",
        "spec_name",
        "selected_cells",
        "changed_rows_vs_h057",
        "model_pred_delta_vs_h057",
        "posterior_delta_vs_h057",
        "hard_diag_delta_vs_h057",
        "anti_h088_direction_rate",
        "h057_positive_align_rate",
        "selected_conflict_rate",
        "cos_h088_direction",
        "cos_h057_vs_h042_direction",
        "max_positive_bad_cosine",
        "h098_frontier_score",
        "file",
    ]
    report = f"""# H098 Frontier-Weighted Signed Action Equation HS-JEPA

Question: can the signed public-action equation explain H088 when frontier
observations are weighted above old bad submissions?

Frontier model scores:

{md_table(model_scores.head(15), 15)}

Selected-model LOO predictions:

{md_table(pred_rows[pred_rows['feature_set'].eq(fit.feature_set) & pred_rows['alpha'].eq(fit.alpha)], 30)}

Candidates:

{md_table(candidates[cols], 20)}

Decision:

{md_table(pd.DataFrame([decision]), 1)}

Interpretation rule:

- If H098 improves, the action-equation solver should be frontier-weighted and
  H088 must be a first-class training sensor.
- If H098 loses but H096 wins, the H088 sensor is useful only as local conflict
  inversion, not as a global response model.
- If both lose, the signed equation needs row/route constraints rather than
  cell-level gradients.
"""
    (OUT / "h098_report.md").write_text(report, encoding="utf-8")

    print(f"selected={decision['selected_candidate_id']}")
    print(f"root={root_path}")
    print(candidates[cols].head(10).to_string(index=False))
    print("\\nfrontier model")
    print(model_scores.head(8).to_string(index=False))


if __name__ == "__main__":
    run()
