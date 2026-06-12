#!/usr/bin/env python3
"""Episode-conditioned selective assignment decoder for HS-JEPA.

The previous row-reset experiment found a row-level signal: some days look like
hidden episodes where raw lifelog memory should be reset across the whole target
vector.  A full-row reset is too blunt for release, though.  This experiment
turns that signal into a target/listener assignment problem:

    Can a row-level hidden episode state help decide which row-target cells
    should abandon raw KNN, and which expert route should replace it?

The script is intentionally anchor-free:

- no public LB score ledger
- no prior submission probabilities
- no action teacher or frontier file

Supervision is OG train temporal OOF gain only.  The row episode score itself is
OOF-predicted before it is used by the cell-level assignment decoder.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import ElasticNet, HuberRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeRegressor, export_text


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sleep_competition_adapter.contextual_listener_route_selector import (  # noqa: E402
    build_cell_and_pair_frames,
    build_temporal_oof_frames,
)
from sleep_competition_adapter.core_oof_action_health_benchmark import (  # noqa: E402
    TARGETS,
    load_world,
    logloss,
    prediction_catalog,
    raw_feature_cols,
    short_hash,
    validate_submission,
)
from sleep_competition_adapter.failure_boundary_law_distillation import (  # noqa: E402
    add_law_features,
    best_candidate_per_cell,
    feature_views as base_feature_views,
)
from sleep_competition_adapter.raw_knn_failure_detector import prepare_gain_pairs  # noqa: E402
from sleep_competition_adapter.raw_knn_override_safety_jury import (  # noqa: E402
    expert_family,
    target_family_stratified_null,
    target_stratified_null,
)
from sleep_competition_adapter.row_reset_episode_detector import (  # noqa: E402
    aggregate_row_frame,
    best_route_per_row,
    build_row_pairs,
    evaluate_detectors as evaluate_row_episode_detectors,
    feature_columns as row_episode_feature_columns,
    make_model as make_row_episode_model,
)


OUT = ROOT / "sleep_competition_adapter" / "outputs" / "episode_selective_assignment_decoder"
OUT.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = 20260612
TOP_FRACS = [0.005, 0.01, 0.02, 0.03, 0.04, 0.06, 0.08, 0.10, 0.15]
THRESHOLDS = [-0.02, -0.01, 0.0, 0.005, 0.01, 0.02, 0.04, 0.08, 0.12]
NULL_REPEATS = 3000


def episode_route_family_for_cell(route: str) -> str:
    if route in {"global_prior", "subject_prior"}:
        return "prior"
    if route == "core_knn_blend":
        return "core_geometry"
    return "other"


def build_oof_episode_state(cell_frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """Return OOF row episode state and row detector metadata."""
    row_frame = aggregate_row_frame(cell_frame)
    row_pair_frame = build_row_pairs(row_frame, require_losses=True)
    row_metrics, _row_selected, _row_candidates, row_best = evaluate_row_episode_detectors(cell_frame, row_pair_frame)
    row_metric = row_metrics.iloc[0].to_dict()
    candidates = row_best["candidates"].copy()
    episode = candidates[["row", "subject_id", "reset_route", "route_family", "selection_score"]].copy()
    episode = episode.rename(
        columns={
            "reset_route": "row_episode_route",
            "route_family": "row_episode_route_family",
            "selection_score": "row_episode_score",
        }
    )
    episode["row_episode_route_cell_family"] = episode["row_episode_route"].astype(str).map(episode_route_family_for_cell)
    ranked = candidates.sort_values(["row", "subject_id", "selection_score"], ascending=[True, True, False], kind="mergesort")
    second = (
        ranked.groupby(["row", "subject_id"], as_index=False, sort=False)
        .nth(1)[["row", "subject_id", "selection_score"]]
        .rename(columns={"selection_score": "row_episode_second_score"})
    )
    episode = episode.merge(second, on=["row", "subject_id"], how="left")
    episode["row_episode_second_score"] = episode["row_episode_second_score"].fillna(0.0)
    episode["row_episode_margin"] = episode["row_episode_score"].astype(float) - episode["row_episode_second_score"].astype(float)
    episode["row_episode_is_global_prior"] = episode["row_episode_route"].eq("global_prior").astype(float)
    episode["row_episode_is_subject_prior"] = episode["row_episode_route"].eq("subject_prior").astype(float)
    episode["row_episode_is_core"] = episode["row_episode_route"].eq("core_knn_blend").astype(float)
    return episode, row_pair_frame, {
        "row_episode_metric": row_metric,
        "row_episode_best_spec": row_best["spec"],
        "row_episode_best_features": row_best["features"],
    }


def attach_episode_features(frame: pd.DataFrame, episode: pd.DataFrame) -> pd.DataFrame:
    out = frame.merge(episode, on=["row", "subject_id"], how="left")
    out["expert_family"] = out["expert"].astype(str).map(expert_family)
    out["row_episode_score"] = out["row_episode_score"].fillna(0.0)
    out["row_episode_second_score"] = out["row_episode_second_score"].fillna(0.0)
    out["row_episode_margin"] = out["row_episode_margin"].fillna(0.0)
    out["row_episode_is_global_prior"] = out["row_episode_is_global_prior"].fillna(0.0)
    out["row_episode_is_subject_prior"] = out["row_episode_is_subject_prior"].fillna(0.0)
    out["row_episode_is_core"] = out["row_episode_is_core"].fillna(0.0)
    out["expert_matches_row_episode_route"] = out["expert"].astype(str).eq(out["row_episode_route"].astype(str)).astype(float)
    out["family_matches_row_episode"] = out["expert_family"].astype(str).eq(out["row_episode_route_cell_family"].astype(str)).astype(float)
    out["row_episode_score_x_route_match"] = out["row_episode_score"].astype(float) * out["expert_matches_row_episode_route"].astype(float)
    out["row_episode_score_x_family_match"] = out["row_episode_score"].astype(float) * out["family_matches_row_episode"].astype(float)
    out["row_episode_score_x_abs_delta"] = out["row_episode_score"].astype(float) * out.get("abs_delta_vs_raw", 0.0).astype(float)
    out["row_episode_score_x_target_q"] = out["row_episode_score"].astype(float) * out.get("target_is_q", 0.0).astype(float)
    out["row_episode_score_x_target_s"] = out["row_episode_score"].astype(float) * out.get("target_is_s", 0.0).astype(float)
    out["row_episode_score_x_q2"] = out["row_episode_score"].astype(float) * out.get("target_is_q2", 0.0).astype(float)
    out["row_episode_score_x_s2"] = out["row_episode_score"].astype(float) * out.get("target_is_s2", 0.0).astype(float)
    return out


def assignment_feature_views(frame: pd.DataFrame) -> dict[str, list[str]]:
    base = base_feature_views(frame)
    episode_cols = [
        col
        for col in frame.columns
        if col.startswith("row_episode_")
        or col in {"expert_matches_row_episode_route", "family_matches_row_episode"}
    ]
    episode_cols = [col for col in episode_cols if pd.api.types.is_numeric_dtype(frame[col])]
    route = base["route_disagreement_law"]
    compact = base["compact_hsjepa_law"]
    human = base["human_state_law"]
    return {
        "route_law_no_episode": route,
        "episode_route_gate": list(dict.fromkeys(route + episode_cols)),
        "episode_human_listener_assignment": list(dict.fromkeys(human + episode_cols)),
        "episode_full_assignment": list(dict.fromkeys(compact + episode_cols)),
    }


def model_specs() -> list[dict[str, Any]]:
    return [
        {"model_name": "episode_tree_depth2_leaf18", "family": "tree", "depth": 2, "leaf": 18},
        {"model_name": "episode_tree_depth3_leaf14", "family": "tree", "depth": 3, "leaf": 14},
        {"model_name": "episode_gbdt_shallow", "family": "gbdt"},
        {"model_name": "episode_elasticnet_sparse", "family": "elasticnet", "alpha": 0.0006, "l1_ratio": 0.86},
        {"model_name": "episode_huber_linear", "family": "huber"},
    ]


def make_model(spec: dict[str, Any]):
    if spec["family"] == "tree":
        return make_pipeline(
            SimpleImputer(strategy="median"),
            DecisionTreeRegressor(
                max_depth=int(spec["depth"]),
                min_samples_leaf=int(spec["leaf"]),
                random_state=RANDOM_STATE,
            ),
        )
    if spec["family"] == "gbdt":
        return make_pipeline(
            SimpleImputer(strategy="median"),
            GradientBoostingRegressor(
                n_estimators=160,
                max_depth=2,
                min_samples_leaf=18,
                learning_rate=0.035,
                random_state=RANDOM_STATE,
            ),
        )
    if spec["family"] == "elasticnet":
        return make_pipeline(
            SimpleImputer(strategy="median"),
            StandardScaler(),
            ElasticNet(
                alpha=float(spec["alpha"]),
                l1_ratio=float(spec["l1_ratio"]),
                max_iter=30000,
                random_state=RANDOM_STATE,
            ),
        )
    if spec["family"] == "huber":
        return make_pipeline(
            SimpleImputer(strategy="median"),
            StandardScaler(),
            HuberRegressor(epsilon=1.35, alpha=0.0001, max_iter=1200),
        )
    raise KeyError(spec["family"])


def predict_oof_gain(frame: pd.DataFrame, features: list[str], spec: dict[str, Any]) -> np.ndarray:
    pred = np.full(len(frame), np.nan, dtype=float)
    for subject in sorted(frame["subject_id"].unique()):
        train = frame[~frame["subject_id"].eq(subject)]
        valid = frame[frame["subject_id"].eq(subject)]
        model = make_model(spec)
        model.fit(train[features], train["gain"].to_numpy(dtype=float))
        pred[valid.index.to_numpy()] = model.predict(valid[features])
    if np.isnan(pred).any():
        raise RuntimeError("OOF assignment gain prediction contains NaN")
    return pred


def selected_cells(candidates: pd.DataFrame, policy: str, param: float) -> set[str]:
    if policy == "topfrac":
        k = max(1, int(round(len(candidates) * param)))
        return set(candidates.sort_values("selection_score", ascending=False, kind="mergesort").head(k)["cell_key"])
    if policy == "threshold":
        return set(candidates[candidates["selection_score"].gt(param)]["cell_key"])
    raise KeyError(policy)


def evaluate_policy(cell_frame: pd.DataFrame, candidates: pd.DataFrame, policy: str, param: float) -> tuple[dict[str, Any], pd.DataFrame]:
    selected = selected_cells(candidates, policy, param)
    candidate_map = candidates.set_index("cell_key")
    pred = []
    action_rows = []
    gains = []
    for rec in cell_frame.to_dict("records"):
        cell_key = rec["cell_key"]
        if cell_key in selected:
            cand = candidate_map.loc[cell_key]
            pred.append(float(cand["expert_pred"]))
            gain = float(cand["true_gain"])
            gains.append(gain)
            action_rows.append(
                {
                    "cell_key": cell_key,
                    "row": int(rec["row"]),
                    "subject_id": rec["subject_id"],
                    "target": rec["target"],
                    "selected_expert": str(cand["expert"]),
                    "expert_family": str(cand["expert_family"]),
                    "selection_score": float(cand["selection_score"]),
                    "true_gain": gain,
                    "row_episode_score": float(cand.get("row_episode_score", 0.0)),
                    "row_episode_route": str(cand.get("row_episode_route", "")),
                    "expert_matches_row_episode_route": float(cand.get("expert_matches_row_episode_route", 0.0)),
                    "family_matches_row_episode": float(cand.get("family_matches_row_episode", 0.0)),
                    "raw_pred": float(rec["pred__raw_knn_blend"]),
                    "selected_pred": float(cand["expert_pred"]),
                    "switched": True,
                }
            )
        else:
            pred.append(float(rec["pred__raw_knn_blend"]))
            gains.append(0.0)
    y = cell_frame["y"].to_numpy(dtype=float)
    pred_arr = np.asarray(pred, dtype=float)
    actions = pd.DataFrame(action_rows)
    metric = {
        "policy": policy,
        "param": float(param),
        "logloss": logloss(y, pred_arr),
        "switched_cells": int(len(selected)),
        "mean_realized_gain_all_cells": float(np.sum(gains) / len(cell_frame)),
        "mean_realized_gain_switched": float(actions["true_gain"].mean()) if len(actions) else 0.0,
        "positive_true_gain_rate": float((actions["true_gain"] > 0).mean()) if len(actions) else 0.0,
        "episode_route_match_rate": float(actions["expert_matches_row_episode_route"].mean()) if len(actions) else 0.0,
        "episode_family_match_rate": float(actions["family_matches_row_episode"].mean()) if len(actions) else 0.0,
        "mean_row_episode_score_switched": float(actions["row_episode_score"].mean()) if len(actions) else 0.0,
    }
    return metric, actions


def evaluate_assignment_decoders(cell_frame: pd.DataFrame, gain_pairs: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Any], dict[str, Any]]:
    raw = logloss(cell_frame["y"].to_numpy(dtype=float), cell_frame["pred__raw_knn_blend"].to_numpy(dtype=float))
    rng = np.random.default_rng(RANDOM_STATE)
    metrics = [{
        "law_name": "raw_knn_blend_baseline",
        "feature_view": "none",
        "model_name": "raw_knn_blend",
        "model_family": "baseline",
        "policy": "baseline",
        "param": 0.0,
        "logloss": raw,
        "switched_cells": 0,
        "mean_realized_gain_all_cells": 0.0,
        "mean_realized_gain_switched": 0.0,
        "positive_true_gain_rate": 0.0,
        "episode_route_match_rate": 0.0,
        "episode_family_match_rate": 0.0,
        "mean_row_episode_score_switched": 0.0,
        "target_null_p_ge_observed": 1.0,
        "target_family_null_p_ge_observed": 1.0,
        "target_null_z": 0.0,
        "target_family_null_z": 0.0,
    }]
    selected_frames = []
    candidate_frames = []
    best_overall: dict[str, Any] | None = None
    best_episode: dict[str, Any] | None = None
    for view_name, features in assignment_feature_views(gain_pairs).items():
        if not features:
            continue
        for spec in model_specs():
            score_col = f"pred__{view_name}__{spec['model_name']}"
            gain_pairs[score_col] = predict_oof_gain(gain_pairs, features, spec)
            candidates = best_candidate_per_cell(gain_pairs, score_col, str(spec["model_name"]), view_name)
            carry_cols = [
                "cell_key",
                "row_episode_score",
                "row_episode_route",
                "row_episode_route_family",
                "expert_matches_row_episode_route",
                "family_matches_row_episode",
            ]
            candidates = candidates.merge(gain_pairs[carry_cols].drop_duplicates("cell_key"), on="cell_key", how="left")
            candidates["law_name"] = f"{view_name}__{spec['model_name']}"
            candidate_frames.append(candidates)
            for frac in TOP_FRACS:
                metric, actions = evaluate_policy(cell_frame, candidates, "topfrac", frac)
                metric.update({"law_name": candidates["law_name"].iloc[0], "feature_view": view_name, "model_name": spec["model_name"], "model_family": spec["family"]})
                metric.update(target_stratified_null(candidates, actions, len(cell_frame), rng, repeats=NULL_REPEATS))
                metric.update(target_family_stratified_null(candidates, actions, len(cell_frame), rng, repeats=NULL_REPEATS))
                metrics.append(metric)
                if len(actions):
                    actions["law_name"] = metric["law_name"]
                    actions["policy"] = "topfrac"
                    actions["param"] = float(frac)
                    selected_frames.append(actions)
                rec = {"metric": metric, "spec": spec, "features": features, "candidates": candidates, "actions": actions}
                if best_overall is None or metric["logloss"] < best_overall["metric"]["logloss"]:
                    best_overall = rec
                if view_name.startswith("episode") and (best_episode is None or metric["logloss"] < best_episode["metric"]["logloss"]):
                    best_episode = rec
            for threshold in THRESHOLDS:
                metric, actions = evaluate_policy(cell_frame, candidates, "threshold", threshold)
                metric.update({"law_name": candidates["law_name"].iloc[0], "feature_view": view_name, "model_name": spec["model_name"], "model_family": spec["family"]})
                metric.update(target_stratified_null(candidates, actions, len(cell_frame), rng, repeats=NULL_REPEATS))
                metric.update(target_family_stratified_null(candidates, actions, len(cell_frame), rng, repeats=NULL_REPEATS))
                metrics.append(metric)
                if len(actions):
                    actions["law_name"] = metric["law_name"]
                    actions["policy"] = "threshold"
                    actions["param"] = float(threshold)
                    selected_frames.append(actions)
                rec = {"metric": metric, "spec": spec, "features": features, "candidates": candidates, "actions": actions}
                if best_overall is None or metric["logloss"] < best_overall["metric"]["logloss"]:
                    best_overall = rec
                if view_name.startswith("episode") and (best_episode is None or metric["logloss"] < best_episode["metric"]["logloss"]):
                    best_episode = rec
    if best_overall is None or best_episode is None:
        raise RuntimeError("no assignment decoder evaluated")
    metrics_df = pd.DataFrame(metrics).sort_values("logloss", kind="mergesort").reset_index(drop=True)
    selected_df = pd.concat(selected_frames, ignore_index=True) if selected_frames else pd.DataFrame()
    candidates_df = pd.concat(candidate_frames, ignore_index=True)
    return metrics_df, selected_df, candidates_df, best_overall, best_episode


def describe_model(model: Any, features: list[str], spec: dict[str, Any]) -> dict[str, Any]:
    if spec["family"] == "tree":
        tree = model.named_steps["decisiontreeregressor"]
        imp = pd.DataFrame({"feature": features, "importance": tree.feature_importances_}).sort_values("importance", ascending=False, kind="mergesort")
        return {
            "tree_text": export_text(tree, feature_names=features, max_depth=int(spec["depth"])),
            "top_features": imp.head(24).to_dict("records"),
            "nonzero_feature_count": int((imp["importance"] > 0).sum()),
        }
    final = model.steps[-1][1]
    if hasattr(final, "feature_importances_"):
        imp = pd.DataFrame({"feature": features, "importance": final.feature_importances_}).sort_values("importance", ascending=False, kind="mergesort")
        return {"tree_text": "", "top_features": imp.head(24).to_dict("records"), "nonzero_feature_count": int((imp["importance"] > 0).sum())}
    coefs = getattr(final, "coef_", np.zeros(len(features), dtype=float))
    cf = pd.DataFrame({"feature": features, "coef": coefs})
    cf["abs_coef"] = cf["coef"].abs()
    cf = cf.sort_values("abs_coef", ascending=False, kind="mergesort")
    return {"tree_text": "", "top_features": cf.head(24).to_dict("records"), "nonzero_feature_count": int((cf["abs_coef"] > 1e-9).sum())}


def fit_row_episode_for_test(row_pair_frame: pd.DataFrame, row_meta: dict[str, Any], test_cells: pd.DataFrame) -> pd.DataFrame:
    test_row_frame = aggregate_row_frame(test_cells)
    test_row_pairs = build_row_pairs(test_row_frame, require_losses=False)
    test_row_pairs["row_reset_gain"] = 0.0
    test_row_pairs["reset_loss_mean"] = 0.0
    model = make_row_episode_model(row_meta["row_episode_best_spec"])
    model.fit(row_pair_frame[row_meta["row_episode_best_features"]], row_pair_frame["row_reset_gain"].to_numpy(dtype=float))
    test_row_pairs["predicted_row_episode_gain"] = model.predict(test_row_pairs[row_meta["row_episode_best_features"]])
    candidates = best_route_per_row(test_row_pairs, "predicted_row_episode_gain", "test_row_episode")
    episode = candidates[["row", "subject_id", "reset_route", "route_family", "selection_score"]].rename(
        columns={
            "reset_route": "row_episode_route",
            "route_family": "row_episode_route_family",
            "selection_score": "row_episode_score",
        }
    )
    episode["row_episode_route_cell_family"] = episode["row_episode_route"].astype(str).map(episode_route_family_for_cell)
    episode["row_episode_second_score"] = 0.0
    episode["row_episode_margin"] = episode["row_episode_score"]
    episode["row_episode_is_global_prior"] = episode["row_episode_route"].eq("global_prior").astype(float)
    episode["row_episode_is_subject_prior"] = episode["row_episode_route"].eq("subject_prior").astype(float)
    episode["row_episode_is_core"] = episode["row_episode_route"].eq("core_knn_blend").astype(float)
    return episode


def train_final_submission(
    features_frame: pd.DataFrame,
    labels: pd.DataFrame,
    sample: pd.DataFrame,
    raw_cols: list[str],
    gain_pairs: pd.DataFrame,
    row_pair_frame: pd.DataFrame,
    row_meta: dict[str, Any],
    release: dict[str, Any],
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    train = features_frame[features_frame["split"].eq("train")].copy().reset_index(drop=True)
    train[TARGETS] = labels[TARGETS].to_numpy(dtype=float)
    test = features_frame[features_frame["split"].eq("test")].copy().reset_index(drop=True)
    catalog, _audit = prediction_catalog(train, test, raw_cols)
    test_cells, test_pairs = build_cell_and_pair_frames(test, None, catalog, "test")
    test_episode = fit_row_episode_for_test(row_pair_frame, row_meta, test_cells)
    raw_pred = test_cells[["cell_key", "pred__raw_knn_blend"]].rename(columns={"pred__raw_knn_blend": "raw_pred"})
    final_pairs = test_pairs[test_pairs["expert"].ne("raw_knn_blend")].copy().reset_index(drop=True)
    final_pairs = final_pairs.merge(raw_pred, on="cell_key", how="left")
    final_pairs = add_law_features(final_pairs)
    final_pairs = attach_episode_features(final_pairs, test_episode)

    model = make_model(release["spec"])
    model.fit(gain_pairs[release["features"]], gain_pairs["gain"].to_numpy(dtype=float))
    description = describe_model(model, release["features"], release["spec"])
    score_col = "predicted_episode_assignment_gain"
    final_pairs[score_col] = model.predict(final_pairs[release["features"]])
    candidates = best_candidate_per_cell(final_pairs, score_col, str(release["spec"]["model_name"]), str(release["metric"]["feature_view"]))
    carry_cols = [
        "cell_key",
        "row_episode_score",
        "row_episode_route",
        "row_episode_route_family",
        "expert_matches_row_episode_route",
        "family_matches_row_episode",
    ]
    candidates = candidates.merge(final_pairs[carry_cols].drop_duplicates("cell_key"), on="cell_key", how="left")
    selected = selected_cells(candidates, str(release["metric"]["policy"]), float(release["metric"]["param"]))
    candidate_map = candidates.set_index("cell_key")

    pred_vec = []
    actions = []
    for rec in test_cells.to_dict("records"):
        cell_key = rec["cell_key"]
        cand = candidate_map.loc[cell_key]
        if cell_key in selected:
            pred = float(cand["expert_pred"])
            expert = str(cand["expert"])
            switched = True
        else:
            pred = float(rec["pred__raw_knn_blend"])
            expert = "raw_knn_blend"
            switched = False
        pred_vec.append(pred)
        actions.append(
            {
                "cell_key": cell_key,
                "row": int(rec["row"]),
                "subject_id": rec["subject_id"],
                "target": rec["target"],
                "selected_expert": expert,
                "candidate_expert": str(cand["expert"]),
                "candidate_family": str(cand["expert_family"]),
                "selection_score": float(cand["selection_score"]),
                "row_episode_score": float(cand.get("row_episode_score", 0.0)),
                "row_episode_route": str(cand.get("row_episode_route", "")),
                "raw_pred": float(rec["pred__raw_knn_blend"]),
                "selected_pred": pred,
                "switched": switched,
            }
        )
    pred = np.asarray(pred_vec, dtype=float).reshape((len(test), len(TARGETS)))
    submission = sample.copy()
    submission[TARGETS] = np.clip(pred, 1e-5, 1 - 1e-5)
    return submission, pd.DataFrame(actions), description


def markdown_table(frame: pd.DataFrame, max_rows: int = 16) -> str:
    show = frame.head(max_rows).copy()
    cols = list(show.columns)
    rows = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for rec in show.to_dict("records"):
        values = []
        for col in cols:
            value = rec[col]
            values.append(f"{value:.6f}" if isinstance(value, float) else str(value))
        rows.append("| " + " | ".join(values) + " |")
    return "\n".join(rows)


def build_markdown(readout: dict[str, Any], metrics: pd.DataFrame, selected: pd.DataFrame, description: dict[str, Any]) -> str:
    top_cols = [
        "law_name",
        "policy",
        "param",
        "logloss",
        "switched_cells",
        "mean_realized_gain_all_cells",
        "positive_true_gain_rate",
        "episode_route_match_rate",
        "target_family_null_p_ge_observed",
    ]
    feature_table = pd.DataFrame(description["top_features"])
    release_actions = selected[
        selected["law_name"].eq(readout["release_law_name"])
        & selected["policy"].eq(readout["release_policy"])
        & selected["param"].eq(readout["release_policy_param"])
    ] if len(selected) else pd.DataFrame()
    target_counts = release_actions["target"].value_counts().reindex(TARGETS).fillna(0).astype(int).rename_axis("target").reset_index(name="count")
    family_counts = release_actions["expert_family"].value_counts().rename_axis("expert_family").reset_index(name="count") if len(release_actions) else pd.DataFrame(columns=["expert_family", "count"])
    lines = [
        "# Episode-Conditioned Selective Assignment Decoder",
        "",
        "## 한 줄 요약",
        "",
        "row-level hidden episode state를 cell-level target/listener assignment decoder에 주입했다.",
        "",
        "즉 HS-JEPA가 먼저 `오늘 raw memory를 믿어도 되는 episode인가`를 판단하고, 그 다음 `어느 target만 어떤 listener route로 바꿀지`를 고른다.",
        "",
        "## 재현 명령",
        "",
        "```bash",
        "python3 sleep_competition_adapter/episode_selective_assignment_decoder.py",
        "```",
        "",
        "public LB score ledger, 기존 submission probability, action teacher, frontier file은 쓰지 않는다.",
        "",
        "## 핵심 결과",
        "",
        f"- raw KNN OOF logloss: `{readout['raw_knn_oof_logloss']:.6f}`",
        f"- row episode detector OOF logloss: `{readout['row_episode_oof_logloss']:.6f}`",
        f"- best no-episode assignment OOF: `{readout['best_no_episode_oof_logloss']:.6f}`",
        f"- best episode-conditioned assignment OOF: `{readout['best_episode_oof_logloss']:.6f}`",
        f"- episode gain over raw: `{readout['best_episode_delta_vs_raw_knn']:.6f}`",
        f"- episode gain over no-episode: `{readout['best_episode_delta_vs_best_no_episode']:.6f}`",
        f"- release law: `{readout['release_law_name']}`",
        f"- release switched OOF cells: `{readout['release_switched_cells']}`",
        f"- target+family null p-value: `{readout['release_target_family_null_p_ge_observed']:.6f}`",
        f"- generated candidate: `{readout['candidate_file']}`",
        f"- same prediction as failure-boundary law: `{readout['candidate_matches_failure_boundary_law']}`",
        "",
        "## 판정",
        "",
        "episode-conditioned view는 raw KNN보다 좋아졌지만, no-episode route law를 넘지 못했다.",
        "",
        "release model의 nonzero feature에도 `row_episode_*`가 남지 않았다.",
        "즉 row-level hidden episode state는 OOF에서 존재하지만, 현 selective assignment decoder는 그 정보를 실제 action 선택으로 번역하지 못했고 route-disagreement law로 붕괴했다.",
        "",
        "따라서 이 실험의 결론은 positive release가 아니라 negative architecture evidence다.",
        "다음 단계는 episode score를 단순 feature로 넣는 방식이 아니라, episode가 action space 자체를 제한하거나 listener responsibility를 재가중하는 구조여야 한다.",
        "",
        "## Release target counts",
        "",
        markdown_table(target_counts, max_rows=10),
        "",
        "## Release expert-family counts",
        "",
        markdown_table(family_counts, max_rows=10),
        "",
        "## Release model top features",
        "",
        markdown_table(feature_table, max_rows=24),
        "",
        "## Top policies",
        "",
        markdown_table(metrics[top_cols], max_rows=16),
        "",
        "## 논문용 해석",
        "",
        "이 실험은 HS-JEPA를 두 단계로 분해한다.",
        "",
        "1. row episode encoder: 하루 전체의 raw-memory failure state를 예측한다.",
        "2. selective assignment decoder: 그 episode state를 target/listener route 선택에 사용한다.",
        "",
        "episode-conditioned decoder가 no-episode decoder보다 낫다면, HS-JEPA core는 단순 feature가 아니라 action decoder의 독성을 줄이는 latent state로 작동한다는 강한 증거다.",
        "",
        "반대로 no-episode가 더 좋다면, row episode state는 존재하지만 release-grade target assignment에는 아직 충분히 번역되지 않았다는 뜻이다.",
    ]
    return "\n".join(lines)


def run() -> dict[str, Any]:
    features_frame, labels, sample, raw_cols_from_module = load_world()
    raw_cols = raw_feature_cols(features_frame) if not raw_cols_from_module else raw_cols_from_module
    cell_frame, pair_frame = build_temporal_oof_frames(features_frame, labels, raw_cols)
    episode, row_pair_frame, row_meta = build_oof_episode_state(cell_frame)
    raw_pred = cell_frame[["cell_key", "pred__raw_knn_blend"]].rename(columns={"pred__raw_knn_blend": "raw_pred"})
    gain_pairs = prepare_gain_pairs(cell_frame, pair_frame).merge(raw_pred, on="cell_key", how="left", suffixes=("", "_dup"))
    if "raw_pred_dup" in gain_pairs.columns:
        gain_pairs = gain_pairs.drop(columns=["raw_pred_dup"])
    gain_pairs = add_law_features(gain_pairs)
    gain_pairs = attach_episode_features(gain_pairs, episode)
    feature_leaks = [
        col
        for cols in assignment_feature_views(gain_pairs).values()
        for col in cols
        if "loss" in col or "gain" in col or col in {"y", "raw_loss"}
    ]
    if feature_leaks:
        raise RuntimeError(f"leaky assignment feature columns detected: {sorted(set(feature_leaks))}")

    metrics, selected, candidates, best_overall, best_episode = evaluate_assignment_decoders(cell_frame, gain_pairs)
    raw = float(metrics[metrics["law_name"].eq("raw_knn_blend_baseline")]["logloss"].iloc[0])
    no_episode_metrics = metrics[metrics["feature_view"].eq("route_law_no_episode")]
    best_no_episode = no_episode_metrics.iloc[0].to_dict()
    release = best_episode
    submission, test_actions, description = train_final_submission(
        features_frame,
        labels,
        sample,
        raw_cols,
        gain_pairs,
        row_pair_frame,
        row_meta,
        release,
    )
    validate_submission(submission, sample)
    suffix = short_hash(submission)
    candidate_file = f"submission_hsjepa_episode_selective_assignment_decoder_{suffix}_uploadsafe.csv"
    submission.to_csv(ROOT / candidate_file, index=False)
    submission.to_csv(OUT / candidate_file, index=False)
    failure_law_file = ROOT / "submission_hsjepa_failure_boundary_law_distillation_65ce2d48_uploadsafe.csv"
    candidate_matches_failure_law = False
    if failure_law_file.exists():
        failure_submission = pd.read_csv(failure_law_file)
        candidate_matches_failure_law = bool(
            np.allclose(
                submission[TARGETS].to_numpy(dtype=float),
                failure_submission[TARGETS].to_numpy(dtype=float),
                atol=1e-12,
                rtol=0.0,
            )
        )
    release_metric = release["metric"]
    readout = {
        "package": "episode_selective_assignment_decoder",
        "status": "episode_conditioned_assignment_ready",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_action_teacher": False,
        "uses_frontier_file": False,
        "raw_knn_oof_logloss": raw,
        "row_episode_oof_logloss": float(row_meta["row_episode_metric"]["logloss"]),
        "row_episode_law_name": str(row_meta["row_episode_metric"]["law_name"]),
        "best_overall_law_name": str(best_overall["metric"]["law_name"]),
        "best_overall_oof_logloss": float(best_overall["metric"]["logloss"]),
        "best_no_episode_law_name": str(best_no_episode["law_name"]),
        "best_no_episode_oof_logloss": float(best_no_episode["logloss"]),
        "best_episode_law_name": str(best_episode["metric"]["law_name"]),
        "best_episode_oof_logloss": float(best_episode["metric"]["logloss"]),
        "best_episode_delta_vs_raw_knn": float(best_episode["metric"]["logloss"] - raw),
        "best_episode_delta_vs_best_no_episode": float(best_episode["metric"]["logloss"] - float(best_no_episode["logloss"])),
        "release_law_name": str(release_metric["law_name"]),
        "release_feature_view": str(release_metric["feature_view"]),
        "release_model_name": str(release_metric["model_name"]),
        "release_model_family": str(release_metric["model_family"]),
        "release_policy": str(release_metric["policy"]),
        "release_policy_param": float(release_metric["param"]),
        "release_oof_logloss": float(release_metric["logloss"]),
        "release_delta_vs_raw_knn": float(release_metric["logloss"] - raw),
        "release_switched_cells": int(release_metric["switched_cells"]),
        "release_positive_true_gain_rate": float(release_metric["positive_true_gain_rate"]),
        "release_episode_route_match_rate": float(release_metric["episode_route_match_rate"]),
        "release_episode_family_match_rate": float(release_metric["episode_family_match_rate"]),
        "release_target_null_p_ge_observed": float(release_metric["target_null_p_ge_observed"]),
        "release_target_family_null_p_ge_observed": float(release_metric["target_family_null_p_ge_observed"]),
        "release_nonzero_feature_count": int(description["nonzero_feature_count"]),
        "release_top_features": description["top_features"],
        "candidate_file": candidate_file,
        "root_candidate_file": candidate_file,
        "candidate_matches_failure_boundary_law": candidate_matches_failure_law,
        "test_switched_cells": int(test_actions["switched"].sum()),
        "test_switched_rows": int(test_actions.loc[test_actions["switched"], "row"].nunique()),
        "test_selected_expert_counts": test_actions.loc[test_actions["switched"], "selected_expert"].value_counts().to_dict(),
        "test_target_counts": test_actions.loc[test_actions["switched"], "target"].value_counts().reindex(TARGETS).fillna(0).astype(int).to_dict(),
        "submission_priority": "high_information_sensor_episode_conditioned_assignment",
        "interpretation": "Tests whether row-level hidden episode state improves target/listener assignment beyond route-only failure laws.",
    }
    metrics.to_csv(OUT / "episode_selective_assignment_policy_table.csv", index=False)
    selected.to_csv(OUT / "episode_selective_assignment_selected_oof_cells.csv", index=False)
    candidates.to_csv(OUT / "episode_selective_assignment_oof_candidates.csv", index=False)
    gain_pairs.to_csv(OUT / "episode_selective_assignment_oof_gain_pairs.csv", index=False)
    test_actions.to_csv(OUT / "episode_selective_assignment_test_actions.csv", index=False)
    (OUT / "episode_selective_assignment_readout.json").write_text(json.dumps(readout, ensure_ascii=False, indent=2), encoding="utf-8")
    md = build_markdown(readout, metrics, selected, description)
    (OUT / "EPISODE_SELECTIVE_ASSIGNMENT_DECODER_KO.md").write_text(md, encoding="utf-8")
    (ROOT / "paper_hsjepa_core" / "EPISODE_SELECTIVE_ASSIGNMENT_DECODER_KO.md").write_text(md, encoding="utf-8")
    return readout


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
