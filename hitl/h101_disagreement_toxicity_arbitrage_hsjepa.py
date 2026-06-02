#!/usr/bin/env python3
"""H101: disagreement-toxicity arbitrage HS-JEPA.

H100 made a strong route-basis claim, but H098's cell equation only weakly
agreed with the promoted action.  H101 turns that disagreement into the object
of study:

    route-basis equation says useful + cell equation does not call it toxic
    -> candidate safe assignment field

This is not a softer blend.  It asks whether public/private action toxicity is
the disagreement boundary between route-action equations and cell equations.
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
OUT = HITL / "h101_disagreement_toxicity_arbitrage_hsjepa"
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


@dataclass(frozen=True)
class H101Spec:
    name: str
    group: str
    max_routes: int
    max_cells: int
    max_rows: int
    max_per_subject: int
    q2_cap: int
    amp: float
    min_score: float
    min_neg_rate: float
    max_cell_pred_delta: float
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
    for path in OUT.glob("submission_h101_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h101_disagreement_toxicity_*_uploadsafe.csv"):
        path.unlink()


def candidate_specs() -> list[H101Spec]:
    return [
        H101Spec(
            name="stable_concord_c80_r36_amp100",
            group="stable_concord",
            max_routes=36,
            max_cells=80,
            max_rows=36,
            max_per_subject=9,
            q2_cap=12,
            amp=1.00,
            min_score=0.53,
            min_neg_rate=0.60,
            max_cell_pred_delta=0.000010,
            worldview="route-basis benefit survives when H098 cell equation is non-toxic",
        ),
        H101Spec(
            name="route_advantage_c70_r30_amp095",
            group="route_advantage",
            max_routes=30,
            max_cells=70,
            max_rows=30,
            max_per_subject=8,
            q2_cap=10,
            amp=0.95,
            min_score=0.52,
            min_neg_rate=0.55,
            max_cell_pred_delta=0.000025,
            worldview="route equation reveals hidden safe assignment where cell equation is nearly silent",
        ),
        H101Spec(
            name="conflict_stable_c72_r30_amp100",
            group="conflict_stable",
            max_routes=30,
            max_cells=72,
            max_rows=30,
            max_per_subject=8,
            q2_cap=10,
            amp=1.00,
            min_score=0.51,
            min_neg_rate=0.50,
            max_cell_pred_delta=0.000020,
            worldview="H057/H088 conflict cells are safe only when route-basis models agree",
        ),
        H101Spec(
            name="highassign_stable_c110_r34_amp080",
            group="highassign_stable",
            max_routes=34,
            max_cells=110,
            max_rows=34,
            max_per_subject=8,
            q2_cap=28,
            amp=0.80,
            min_score=0.48,
            min_neg_rate=0.50,
            max_cell_pred_delta=0.000020,
            worldview="high H071 assignment routes survive the disagreement toxicity boundary",
        ),
        H101Spec(
            name="h100_pruned_c56_r24_amp090",
            group="h100_pruned",
            max_routes=24,
            max_cells=56,
            max_rows=24,
            max_per_subject=7,
            q2_cap=8,
            amp=0.90,
            min_score=0.50,
            min_neg_rate=0.50,
            max_cell_pred_delta=0.000020,
            worldview="prune H100 to the route actions that remain stable under equation disagreement",
        ),
    ]


def action_move_matrix(shape: tuple[int, int], cells: pd.DataFrame, move_col: str = "h101_direct_move") -> np.ndarray:
    move_mat = np.zeros(shape, dtype=np.float64)
    for rec in cells.to_dict("records"):
        move_mat[int(rec["row"]), int(rec["target_index"])] = float(rec[move_col])
    return move_mat


def materialize(base_prob: np.ndarray, move_mat: np.ndarray) -> np.ndarray:
    return clip_prob(sigmoid(logit(base_prob) + move_mat))


def select_model_rows(model_scores: pd.DataFrame) -> pd.DataFrame:
    rows = model_scores[
        (model_scores["h088_sign_ok"].astype(float) > 0.0)
        & (model_scores["weighted_loo_mae"].astype(float) <= 0.00065)
        & (model_scores["base_loo_abs_error"].astype(float) <= 0.0016)
    ].copy()
    if rows.empty:
        rows = model_scores.copy()
    rows = rows.sort_values(["route_basis_rank_score", "weighted_loo_mae"], ascending=[True, True]).head(12)
    return rows.reset_index(drop=True)


def fit_route_model(
    public: pd.DataFrame,
    basis: pd.DataFrame,
    basis_moves: np.ndarray,
    feature_set: str,
    k_basis: int,
    alpha: float,
) -> tuple[h100mod.RouteBasisFit, pd.DataFrame, np.ndarray]:
    ranked = basis.sort_values("h099_route_score", ascending=False).reset_index(drop=True).head(int(k_basis))
    ids = set(ranked["basis_id"].astype(str))
    mask = basis["basis_id"].astype(str).isin(ids).to_numpy()
    basis_k = basis.loc[mask].reset_index(drop=True)
    moves_k = basis_moves[mask]
    public_moves = np.vstack(public["move_logit"].to_list()).astype(np.float64)
    y = public["delta_vs_h057"].to_numpy(dtype=np.float64)
    weights = h098mod.frontier_weights(public)
    x, x_cols = h100mod.design_from_moves(public_moves, moves_k, basis_k, feature_set)
    if x.shape[1] > 220:
        variances = np.nanvar(x, axis=0)
        keep = np.argsort(variances)[-220:]
        x = x[:, keep]
        x_cols = [x_cols[i] for i in keep]
    intercept, beta, mu, sd = h100mod.fit_weighted_ridge(x, y, weights, float(alpha))
    pred = h100mod.predict_x(x, intercept, beta, mu, sd)
    fit = h100mod.RouteBasisFit(
        feature_set=str(feature_set),
        k_basis=int(k_basis),
        alpha=float(alpha),
        x_cols=x_cols,
        intercept=intercept,
        beta=beta,
        mu=mu,
        sd=sd,
        loo_pred=pred,
        loo_mae=float(np.mean(np.abs(pred - y))),
        loo_rmse=float(np.sqrt(np.mean((pred - y) ** 2))),
        loo_spearman=h097mod.spearman(y, pred),
        loo_pair_acc=h097mod.pairwise_accuracy(y, pred),
    )
    return fit, basis_k, moves_k


def score_stability(
    basis: pd.DataFrame,
    basis_moves: np.ndarray,
    public: pd.DataFrame,
    model_scores: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    model_rows = select_model_rows(model_scores)
    pred_cols = []
    fit_rows = []
    for i, rec in enumerate(model_rows.to_dict("records")):
        fit, basis_k, moves_k = fit_route_model(
            public,
            basis,
            basis_moves,
            str(rec["feature_set"]),
            int(rec["k_basis"]),
            float(rec["alpha"]),
        )
        preds = [
            h100mod.predict_candidate_delta(move, basis_k, moves_k, fit)
            for move in basis_moves
        ]
        col = f"h101_route_pred_m{i:02d}"
        pred_cols.append(col)
        basis[col] = np.asarray(preds, dtype=np.float64)
        fit_rows.append(
            {
                "model_index": i,
                "feature_set": fit.feature_set,
                "k_basis": fit.k_basis,
                "alpha": fit.alpha,
                "source_route_basis_rank_score": float(rec["route_basis_rank_score"]),
                "source_weighted_loo_mae": float(rec["weighted_loo_mae"]),
                "source_h088_loo_pred": float(rec["h088_loo_pred"]),
                "source_h088_loo_error": float(rec["h088_loo_error"]),
                "full_fit_mae": fit.loo_mae,
                "full_fit_spearman": fit.loo_spearman,
            }
        )
    preds = basis[pred_cols].to_numpy(dtype=np.float64)
    basis["h101_route_pred_mean"] = preds.mean(axis=1)
    basis["h101_route_pred_median"] = np.median(preds, axis=1)
    basis["h101_route_pred_min"] = preds.min(axis=1)
    basis["h101_route_pred_max"] = preds.max(axis=1)
    basis["h101_route_pred_std"] = preds.std(axis=1)
    basis["h101_route_neg_rate"] = (preds < 0.0).mean(axis=1)
    basis["h101_route_gain"] = -basis["h101_route_pred_mean"].to_numpy(dtype=np.float64)
    basis["h101_cell_gain"] = -basis["model_pred_delta_vs_h057"].to_numpy(dtype=np.float64)
    basis["h101_route_cell_gap"] = basis["h101_route_gain"] - np.maximum(basis["h101_cell_gain"], 0.0)
    basis["h101_cell_nontoxic"] = (basis["model_pred_delta_vs_h057"].to_numpy(dtype=np.float64) <= 0.00002).astype(float)
    basis["h101_stability_score"] = (
        0.22 * rank01(basis["h101_route_gain"].to_numpy(dtype=np.float64), high=True)
        + 0.15 * basis["h101_route_neg_rate"].to_numpy(dtype=np.float64)
        + 0.14 * rank01(basis["h101_route_cell_gap"].to_numpy(dtype=np.float64), high=True)
        + 0.12 * rank01(-basis["model_pred_delta_vs_h057"].to_numpy(dtype=np.float64), high=True)
        + 0.10 * basis["anti_h088_direction_rate"].to_numpy(dtype=np.float64)
        + 0.10 * basis["h057_positive_align_rate"].to_numpy(dtype=np.float64)
        + 0.08 * basis["selected_conflict_rate"].to_numpy(dtype=np.float64)
        + 0.06 * basis["h099_route_score"].to_numpy(dtype=np.float64)
        + 0.05 * basis["assignment_route_score"].to_numpy(dtype=np.float64)
        - 0.12 * rank01(basis["h101_route_pred_std"].to_numpy(dtype=np.float64), high=True)
        - 0.10 * basis["mean_bad_same_rank"].to_numpy(dtype=np.float64)
        - 18.0 * np.maximum(basis["hard_diag_delta_vs_h057"].to_numpy(dtype=np.float64), 0.0)
        - 10.0 * np.maximum(basis["posterior_delta_vs_h057"].to_numpy(dtype=np.float64), 0.0)
    )
    basis["h100_route_basis_pred_delta"] = basis["h101_route_pred_mean"]
    basis["h100_action_score"] = basis["h101_stability_score"]
    return basis.sort_values("h101_stability_score", ascending=False).reset_index(drop=True), pd.DataFrame(fit_rows)


def action_allowed(rec: dict[str, object], spec: H101Spec) -> bool:
    if float(rec["h101_route_neg_rate"]) < spec.min_neg_rate:
        return False
    if float(rec["model_pred_delta_vs_h057"]) > spec.max_cell_pred_delta:
        return False
    group = spec.group
    basis_spec = str(rec["basis_spec"])
    if group == "stable_concord":
        return float(rec["h101_route_pred_mean"]) < 0 and float(rec["model_pred_delta_vs_h057"]) <= 0
    if group == "route_advantage":
        return float(rec["h101_route_cell_gap"]) > 0 and float(rec["h101_route_pred_mean"]) < 0
    if group == "conflict_stable":
        return float(rec["selected_conflict_rate"]) >= 0.999 and float(rec["h101_route_pred_mean"]) < 0
    if group == "highassign_stable":
        return (float(rec["assignment_route_score"]) >= 0.50 or str(rec["route_name"]) in {"full_state", "nonq2_full"}) and float(rec["h101_route_pred_mean"]) < 0
    if group == "h100_pruned":
        return (
            basis_spec in {"basis_conflict_a052", "basis_q2_counter_a050", "basis_objective_a042"}
            and float(rec["selected_conflict_rate"]) >= 0.75
            and float(rec["h101_route_pred_mean"]) < 0
        )
    raise ValueError(group)


def greedy_select(
    scored: pd.DataFrame,
    cells_by_basis: dict[str, pd.DataFrame],
    spec: H101Spec,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    selected_actions = []
    selected_cells = []
    used_rows: set[int] = set()
    subject_counts: dict[str, int] = {}
    cell_count = 0
    q2_count = 0
    for rec in scored.to_dict("records"):
        if float(rec["h101_stability_score"]) < spec.min_score:
            continue
        if not action_allowed(rec, spec):
            continue
        row = int(rec["row"])
        subject = str(rec["subject_id"])
        if row in used_rows:
            continue
        if len(selected_actions) >= spec.max_routes or len(used_rows) >= spec.max_rows:
            break
        cells = cells_by_basis[str(rec["basis_id"])].copy()
        cells["h101_direct_move"] = cells["h100_direct_move"].to_numpy(dtype=np.float64) * spec.amp
        cells["h097_move_col"] = "h101_direct_move"
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
    route_fit: h100mod.RouteBasisFit,
    basis_fit_df: pd.DataFrame,
    basis_fit_moves: np.ndarray,
    spec: H101Spec,
    path: Path,
) -> dict[str, object]:
    proxy = h100mod.H100CandidateSpec(
        name=spec.name,
        action_group=spec.group,
        max_routes=spec.max_routes,
        max_cells=spec.max_cells,
        max_rows=spec.max_rows,
        max_per_subject=spec.max_per_subject,
        q2_cap=spec.q2_cap,
        amp=spec.amp,
        min_action_score=spec.min_score,
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
    if len(selected_actions):
        metrics["mean_h101_stability_score"] = float(selected_actions["h101_stability_score"].mean())
        metrics["mean_h101_route_pred_mean"] = float(selected_actions["h101_route_pred_mean"].mean())
        metrics["mean_h101_route_neg_rate"] = float(selected_actions["h101_route_neg_rate"].mean())
        metrics["mean_h101_route_cell_gap"] = float(selected_actions["h101_route_cell_gap"].mean())
        metrics["mean_h101_route_pred_std"] = float(selected_actions["h101_route_pred_std"].mean())
    else:
        metrics["mean_h101_stability_score"] = 0.0
        metrics["mean_h101_route_pred_mean"] = 0.0
        metrics["mean_h101_route_neg_rate"] = 0.0
        metrics["mean_h101_route_cell_gap"] = 0.0
        metrics["mean_h101_route_pred_std"] = 0.0
    metrics["h101_score"] = (
        230.0 * (-float(metrics["route_basis_pred_delta_vs_h057"]))
        + 160.0 * (-float(metrics["model_pred_delta_vs_h057"]))
        + 0.16 * float(metrics["mean_h101_route_neg_rate"])
        + 0.14 * float(metrics["anti_h088_direction_rate"])
        + 0.13 * float(metrics["h057_positive_align_rate"])
        + 0.11 * float(metrics["selected_conflict_rate"])
        + 0.10 * max(float(metrics["cos_h057_vs_h042_direction"]), 0.0)
        - 0.22 * max(float(metrics["cos_h088_direction"]), 0.0)
        - 0.24 * float(metrics["max_positive_bad_cosine"])
        - 24.0 * max(float(metrics["hard_diag_delta_vs_h057"]), 0.0)
        - 10.0 * max(float(metrics["posterior_delta_vs_h057"]), 0.0)
        - 0.05 * float(metrics["mean_h101_route_pred_std"])
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
    route_model_scores, route_pred_rows, route_fit = h100mod.evaluate_route_basis_models(public, basis, basis_moves)
    basis_fit_df, basis_fit_moves = h100mod.selected_basis_for_fit(basis, basis_moves, route_fit)
    scored, stability_models = score_stability(basis.copy(), basis_moves, public, route_model_scores)

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
        candidate_id = safe_id(f"h101_{spec.name}_{hash_id}", 128)
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
        raise RuntimeError("no H101 candidates")
    candidates = candidates.sort_values(["h101_score", "route_basis_pred_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True)
    selected = candidates.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"submission_h101_disagreement_toxicity_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)

    public_out = public.drop(columns=["move_logit"]).copy()
    public_out["frontier_weight"] = h098mod.frontier_weights(public)
    decision = {
        "decision": "promote_h101_disagreement_toxicity_arbitrage",
        "selected_candidate_id": selected["candidate_id"],
        "root_uploadsafe_path": str(root_path.resolve()),
        "worldview": selected["worldview"],
        "h098_feature_set": h098_fit.feature_set,
        "h098_alpha": h098_fit.alpha,
        "route_basis_feature_set": route_fit.feature_set,
        "route_basis_k": route_fit.k_basis,
        "route_basis_alpha": route_fit.alpha,
        **selected,
        **{f"root_{key}": value for key, value in validation.items()},
    }

    public_out.to_csv(OUT / "h101_public_moves_weighted.csv", index=False)
    h098_scores.to_csv(OUT / "h101_h098_frontier_model_scores.csv", index=False)
    h098_pred_rows.to_csv(OUT / "h101_h098_frontier_loo_predictions.csv", index=False)
    route_model_scores.to_csv(OUT / "h101_route_basis_model_scores.csv", index=False)
    route_pred_rows.to_csv(OUT / "h101_route_basis_loo_predictions.csv", index=False)
    stability_models.to_csv(OUT / "h101_stability_models.csv", index=False)
    scored.to_csv(OUT / "h101_scored_route_actions.csv", index=False)
    candidates.to_csv(OUT / "h101_candidates.csv", index=False)
    pd.concat(selected_action_frames, ignore_index=True).to_csv(OUT / "h101_selected_route_actions.csv", index=False)
    pd.concat(selected_cell_frames, ignore_index=True).to_csv(OUT / "h101_selected_cells.csv", index=False)
    pd.DataFrame([decision]).to_csv(OUT / "h101_decision.csv", index=False)

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
        "mean_h101_route_neg_rate",
        "mean_h101_route_cell_gap",
        "cos_h088_direction",
        "max_positive_bad_cosine",
        "h101_score",
        "file",
    ]
    report = f"""# H101 Disagreement-Toxicity Arbitrage HS-JEPA

Question: is the safe assignment field the region where route-basis equations
predict benefit while H098's cell equation does not mark the action as toxic?

Stability models:

{md_table(stability_models, 15)}

Candidates:

{md_table(candidates[cols], 20)}

Decision:

{md_table(pd.DataFrame([decision]), 1)}

Interpretation rule:

- If H101 improves over H100, the action toxicity boundary is the disagreement
  filter between route-basis and cell-equation decoders.
- If H100 improves but H101 loses, the stronger route-basis signal should not
  be diluted by cell-equation caution.
- If both lose, route-basis action decoding is likely explanatory but not
  action-grade.
"""
    (OUT / "h101_report.md").write_text(report, encoding="utf-8")

    print(f"selected={decision['selected_candidate_id']}")
    print(f"root={root_path}")
    print(candidates[cols].head(10).to_string(index=False))
    print("\nstability models")
    print(stability_models.head(12).to_string(index=False))


if __name__ == "__main__":
    run()
