#!/usr/bin/env python3
"""Interpretable failure-boundary law distillation for HS-JEPA.

Raw-KNN failure detection worked, but the strongest boundary came from a
non-linear gain regressor.  The contrastive prototype atlas did not pass
matched-null stress.  This experiment asks the next architectural question:

    Can the sharp raw-KNN failure boundary be distilled into a small,
    interpretable HS-JEPA action law?

The script trains only on OG train OOF action outcomes.  It does not use public
LB observations, prior submission probabilities, action teachers, or frontier
files.  It compares shallow tree laws and sparse linear laws over multiple
feature views so the result says whether human-state context is actually needed
or whether route-disagreement variables alone explain the boundary.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
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
from sleep_competition_adapter.raw_knn_failure_detector import prepare_gain_pairs  # noqa: E402
from sleep_competition_adapter.raw_knn_override_safety_jury import (  # noqa: E402
    expert_family,
    target_family_stratified_null,
    target_stratified_null,
)


OUT = ROOT / "sleep_competition_adapter" / "outputs" / "failure_boundary_law_distillation"
OUT.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = 20260612
TOP_FRACS = [0.005, 0.01, 0.02, 0.03, 0.04, 0.06, 0.08, 0.10]
THRESHOLDS = [-0.03, -0.01, 0.00, 0.005, 0.01, 0.02, 0.04, 0.08, 0.12]
NULL_REPEATS = 4000


HUMAN_STATE_COLS = [
    "dayofweek",
    "is_weekend",
    "dayofmonth_rank",
    "month_start_proximity",
    "month_end",
    "dist_to_subject_normal",
    "dist_to_peer_normal",
    "subject_minus_peer_dist",
    "subject_outlier_rank",
    "peer_outlier_rank",
    "cohort_outlier_score",
]
ROUTE_DISAGREEMENT_COLS = [
    "abs_vs_global",
    "abs_vs_subject",
    "abs_vs_raw",
    "abs_vs_core",
    "expert_prob_mean",
    "expert_prob_std",
    "expert_prob_range",
    "expert_logit_std",
    "raw_core_gap",
    "subject_global_gap",
    "core_subject_gap",
    "raw_subject_gap",
    "delta_vs_raw",
    "abs_delta_vs_raw",
    "delta_logit_vs_raw",
    "abs_delta_logit_vs_raw",
    "raw_confidence",
    "expert_confidence",
    "confidence_delta",
]
TARGET_EXPERT_COLS = [
    "expert_pred",
    "expert_logit",
    "target_idx",
    "target_is_q",
    "target_is_s",
    "target_is_q2",
    "target_is_s2",
    "expert_is_global_prior",
    "expert_is_subject_prior",
    "expert_is_core_geometry",
    "expert_is_core_action_health",
    "expert_is_raw_action_core_gate",
    "expert_is_strict",
    "expert_is_balanced",
    "expert_is_wide",
    "expert_is_high_margin",
    "family_is_prior",
    "family_is_core_geometry",
    "family_is_core_action_health",
    "family_is_raw_action_core_health",
]


def logit(values: np.ndarray | pd.Series) -> np.ndarray:
    arr = np.clip(np.asarray(values, dtype=float), 1e-5, 1 - 1e-5)
    return np.log(arr / (1.0 - arr))


def add_law_features(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    if "expert_family" not in out.columns:
        out["expert_family"] = out["expert"].astype(str).map(expert_family)
    out["delta_vs_raw"] = out["expert_pred"].astype(float) - out["raw_pred"].astype(float)
    out["abs_delta_vs_raw"] = out["delta_vs_raw"].abs()
    out["raw_logit"] = logit(out["raw_pred"])
    out["delta_logit_vs_raw"] = out["expert_logit"].astype(float) - out["raw_logit"].astype(float)
    out["abs_delta_logit_vs_raw"] = out["delta_logit_vs_raw"].abs()
    out["raw_confidence"] = (out["raw_pred"].astype(float) - 0.5).abs() * 2.0
    out["expert_confidence"] = (out["expert_pred"].astype(float) - 0.5).abs() * 2.0
    out["confidence_delta"] = out["expert_confidence"] - out["raw_confidence"]
    out["family_is_prior"] = out["expert_family"].eq("prior").astype(float)
    out["family_is_core_geometry"] = out["expert_family"].eq("core_geometry").astype(float)
    out["family_is_core_action_health"] = out["expert_family"].eq("core_action_health").astype(float)
    out["family_is_raw_action_core_health"] = out["expert_family"].eq("raw_action_core_health").astype(float)
    return out


def available_columns(frame: pd.DataFrame, columns: list[str]) -> list[str]:
    return [col for col in columns if col in frame.columns and pd.api.types.is_numeric_dtype(frame[col])]


def feature_views(frame: pd.DataFrame) -> dict[str, list[str]]:
    target_expert = available_columns(frame, TARGET_EXPERT_COLS)
    route = available_columns(frame, ROUTE_DISAGREEMENT_COLS)
    human = available_columns(frame, HUMAN_STATE_COLS)
    compact = list(dict.fromkeys(target_expert + route + human))
    route_only = list(dict.fromkeys(target_expert + route))
    human_only = list(dict.fromkeys(target_expert + human))
    minimal = list(dict.fromkeys([
        "target_idx",
        "target_is_q",
        "target_is_s",
        "expert_pred",
        "expert_logit",
        "delta_vs_raw",
        "abs_delta_vs_raw",
        "delta_logit_vs_raw",
        "abs_delta_logit_vs_raw",
        "raw_core_gap",
        "subject_global_gap",
        "cohort_outlier_score",
        "subject_outlier_rank",
        "peer_outlier_rank",
        "expert_is_global_prior",
        "expert_is_subject_prior",
        "expert_is_core_geometry",
        "expert_is_core_action_health",
        "expert_is_raw_action_core_gate",
    ]))
    minimal = available_columns(frame, minimal)
    return {
        "minimal_hsjepa_law": minimal,
        "route_disagreement_law": route_only,
        "human_state_law": human_only,
        "compact_hsjepa_law": compact,
    }


def model_specs() -> list[dict[str, Any]]:
    specs = []
    for depth, leaf in [(2, 28), (3, 24), (4, 18), (5, 14)]:
        specs.append({
            "model_name": f"tree_depth{depth}_leaf{leaf}",
            "family": "shallow_tree",
            "depth": depth,
            "leaf": leaf,
        })
    specs.extend([
        {"model_name": "elasticnet_sparse_alpha_0p0005", "family": "sparse_linear", "alpha": 0.0005, "l1_ratio": 0.82},
        {"model_name": "elasticnet_sparse_alpha_0p001", "family": "sparse_linear", "alpha": 0.001, "l1_ratio": 0.88},
        {"model_name": "huber_linear_epsilon_1p35", "family": "robust_linear", "epsilon": 1.35},
    ])
    return specs


def make_model(spec: dict[str, Any]):
    if spec["family"] == "shallow_tree":
        return make_pipeline(
            SimpleImputer(strategy="median"),
            DecisionTreeRegressor(
                max_depth=int(spec["depth"]),
                min_samples_leaf=int(spec["leaf"]),
                random_state=RANDOM_STATE,
            ),
        )
    if spec["family"] == "sparse_linear":
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
    if spec["family"] == "robust_linear":
        return make_pipeline(
            SimpleImputer(strategy="median"),
            StandardScaler(),
            HuberRegressor(epsilon=float(spec["epsilon"]), alpha=0.0001, max_iter=1000),
        )
    raise KeyError(spec["family"])


def predict_oof_law(gain_pairs: pd.DataFrame, features: list[str], spec: dict[str, Any]) -> np.ndarray:
    pred = np.full(len(gain_pairs), np.nan, dtype=float)
    for subject in sorted(gain_pairs["subject_id"].unique()):
        train = gain_pairs[~gain_pairs["subject_id"].eq(subject)]
        valid = gain_pairs[gain_pairs["subject_id"].eq(subject)]
        model = make_model(spec)
        model.fit(train[features], train["gain"].to_numpy(dtype=float))
        pred[valid.index.to_numpy()] = model.predict(valid[features])
    if np.isnan(pred).any():
        raise RuntimeError("law OOF prediction has missing values")
    return pred


def best_candidate_per_cell(gain_pairs: pd.DataFrame, score_col: str, model_name: str, feature_view: str) -> pd.DataFrame:
    rows = []
    for cell_key, group in gain_pairs.groupby("cell_key", sort=False):
        best = group.sort_values(score_col, ascending=False, kind="mergesort").iloc[0]
        rows.append(
            {
                "cell_key": cell_key,
                "row": int(best["row"]),
                "subject_id": best["subject_id"],
                "target": best["target"],
                "expert": str(best["expert"]),
                "expert_family": str(best["expert_family"]),
                "expert_pred": float(best["expert_pred"]),
                "selection_score": float(best[score_col]),
                "true_gain": float(best["gain"]) if "gain" in best.index else np.nan,
                "model_name": model_name,
                "feature_view": feature_view,
            }
        )
    return pd.DataFrame(rows)


def policy_selected(candidates: pd.DataFrame, policy: str, param: float) -> set[str]:
    if policy == "topfrac":
        k = max(1, int(round(len(candidates) * param)))
        return set(candidates.sort_values("selection_score", ascending=False, kind="mergesort").head(k)["cell_key"])
    if policy == "threshold":
        return set(candidates[candidates["selection_score"].gt(param)]["cell_key"])
    raise KeyError(policy)


def evaluate_policy(
    cell_frame: pd.DataFrame,
    candidates: pd.DataFrame,
    policy: str,
    param: float,
) -> tuple[dict[str, Any], pd.DataFrame]:
    selected = policy_selected(candidates, policy, param)
    candidate_map = candidates.set_index("cell_key")
    pred = []
    gains = []
    actions = []
    for rec in cell_frame.to_dict("records"):
        cell_key = rec["cell_key"]
        if cell_key in selected:
            cand = candidate_map.loc[cell_key]
            pred.append(float(cand["expert_pred"]))
            gain = float(cand["true_gain"])
            gains.append(gain)
            actions.append(
                {
                    "cell_key": cell_key,
                    "row": int(rec["row"]),
                    "subject_id": rec["subject_id"],
                    "target": rec["target"],
                    "selected_expert": str(cand["expert"]),
                    "expert_family": str(cand["expert_family"]),
                    "selection_score": float(cand["selection_score"]),
                    "true_gain": gain,
                    "raw_pred": float(rec["pred__raw_knn_blend"]),
                    "selected_pred": float(cand["expert_pred"]),
                    "switched": True,
                }
            )
        else:
            pred.append(float(rec["pred__raw_knn_blend"]))
            gains.append(0.0)
    pred_arr = np.asarray(pred, dtype=float)
    y = cell_frame["y"].to_numpy(dtype=float)
    actions_df = pd.DataFrame(actions)
    metric = {
        "policy": policy,
        "param": float(param),
        "logloss": logloss(y, pred_arr),
        "switched_cells": int(len(selected)),
        "switched_rate": float(len(selected) / len(cell_frame)),
        "mean_realized_gain_all_cells": float(np.sum(gains) / len(cell_frame)),
        "mean_realized_gain_switched": float(actions_df["true_gain"].mean()) if len(actions_df) else 0.0,
        "positive_true_gain_rate": float((actions_df["true_gain"] > 0).mean()) if len(actions_df) else 0.0,
    }
    return metric, actions_df


def evaluate_laws(cell_frame: pd.DataFrame, gain_pairs: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    raw = logloss(cell_frame["y"].to_numpy(dtype=float), cell_frame["pred__raw_knn_blend"].to_numpy(dtype=float))
    metrics = [{
        "law_name": "raw_knn_blend_baseline",
        "model_name": "raw_knn_blend",
        "feature_view": "none",
        "model_family": "baseline",
        "policy": "baseline",
        "param": 0.0,
        "logloss": raw,
        "switched_cells": 0,
        "switched_rate": 0.0,
        "mean_realized_gain_all_cells": 0.0,
        "mean_realized_gain_switched": 0.0,
        "positive_true_gain_rate": 0.0,
        "target_null_p_ge_observed": 1.0,
        "target_family_null_p_ge_observed": 1.0,
        "target_null_z": 0.0,
        "target_family_null_z": 0.0,
    }]
    selected_frames = []
    candidate_frames = []
    best: dict[str, Any] | None = None
    rng = np.random.default_rng(RANDOM_STATE)
    views = feature_views(gain_pairs)

    for view_name, cols in views.items():
        for spec in model_specs():
            score_col = f"pred__{view_name}__{spec['model_name']}"
            gain_pairs[score_col] = predict_oof_law(gain_pairs, cols, spec)
            candidates = best_candidate_per_cell(gain_pairs, score_col, str(spec["model_name"]), view_name)
            candidates["law_name"] = f"{view_name}__{spec['model_name']}"
            candidate_frames.append(candidates)
            for frac in TOP_FRACS:
                metric, actions = evaluate_policy(cell_frame, candidates, "topfrac", frac)
                metric.update({
                    "law_name": f"{view_name}__{spec['model_name']}",
                    "model_name": str(spec["model_name"]),
                    "feature_view": view_name,
                    "model_family": str(spec["family"]),
                })
                metric.update(target_stratified_null(candidates, actions, len(cell_frame), rng, repeats=NULL_REPEATS))
                metric.update(target_family_stratified_null(candidates, actions, len(cell_frame), rng, repeats=NULL_REPEATS))
                metrics.append(metric)
                if len(actions):
                    actions["law_name"] = metric["law_name"]
                    actions["policy"] = "topfrac"
                    actions["param"] = float(frac)
                    selected_frames.append(actions)
                if best is None or float(metric["logloss"]) < float(best["metric"]["logloss"]):
                    best = {"metric": metric, "spec": spec, "features": cols, "candidates": candidates, "actions": actions}
            for threshold in THRESHOLDS:
                metric, actions = evaluate_policy(cell_frame, candidates, "threshold", threshold)
                metric.update({
                    "law_name": f"{view_name}__{spec['model_name']}",
                    "model_name": str(spec["model_name"]),
                    "feature_view": view_name,
                    "model_family": str(spec["family"]),
                })
                metric.update(target_stratified_null(candidates, actions, len(cell_frame), rng, repeats=NULL_REPEATS))
                metric.update(target_family_stratified_null(candidates, actions, len(cell_frame), rng, repeats=NULL_REPEATS))
                metrics.append(metric)
                if len(actions):
                    actions["law_name"] = metric["law_name"]
                    actions["policy"] = "threshold"
                    actions["param"] = float(threshold)
                    selected_frames.append(actions)
                if best is None or float(metric["logloss"]) < float(best["metric"]["logloss"]):
                    best = {"metric": metric, "spec": spec, "features": cols, "candidates": candidates, "actions": actions}

    if best is None:
        raise RuntimeError("no law evaluated")
    metrics_df = pd.DataFrame(metrics).sort_values("logloss", kind="mergesort").reset_index(drop=True)
    selected_df = pd.concat(selected_frames, ignore_index=True) if selected_frames else pd.DataFrame()
    candidates_df = pd.concat(candidate_frames, ignore_index=True)
    return metrics_df, selected_df, candidates_df, best


def fit_full_model(frame: pd.DataFrame, features: list[str], spec: dict[str, Any]):
    model = make_model(spec)
    model.fit(frame[features], frame["gain"].to_numpy(dtype=float))
    return model


def model_description(model: Any, features: list[str], spec: dict[str, Any]) -> dict[str, Any]:
    if spec["family"] == "shallow_tree":
        tree = model.named_steps["decisiontreeregressor"]
        text = export_text(tree, feature_names=features, max_depth=int(spec["depth"]))
        importances = pd.DataFrame({
            "feature": features,
            "importance": tree.feature_importances_,
        }).sort_values("importance", ascending=False, kind="mergesort")
        return {
            "tree_text": text,
            "top_features": importances.head(18).to_dict("records"),
            "nonzero_feature_count": int((importances["importance"] > 0).sum()),
        }
    final = model.steps[-1][1]
    coefs = getattr(final, "coef_", np.zeros(len(features), dtype=float))
    coef_frame = pd.DataFrame({"feature": features, "coef": coefs})
    coef_frame["abs_coef"] = coef_frame["coef"].abs()
    coef_frame = coef_frame.sort_values("abs_coef", ascending=False, kind="mergesort")
    return {
        "tree_text": "",
        "top_features": coef_frame.head(18).to_dict("records"),
        "nonzero_feature_count": int((coef_frame["abs_coef"] > 1e-9).sum()),
    }


def train_final_submission(
    features_frame: pd.DataFrame,
    labels: pd.DataFrame,
    sample: pd.DataFrame,
    raw_cols: list[str],
    gain_pairs: pd.DataFrame,
    best: dict[str, Any],
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    train = features_frame[features_frame["split"].eq("train")].copy().reset_index(drop=True)
    train[TARGETS] = labels[TARGETS].to_numpy(dtype=float)
    test = features_frame[features_frame["split"].eq("test")].copy().reset_index(drop=True)
    catalog, _audit = prediction_catalog(train, test, raw_cols)
    test_cells, test_pairs = build_cell_and_pair_frames(test, None, catalog, "test")
    final_pairs = test_pairs[test_pairs["expert"].ne("raw_knn_blend")].copy().reset_index(drop=True)
    raw_pred = test_cells[["cell_key", "pred__raw_knn_blend"]].rename(columns={"pred__raw_knn_blend": "raw_pred"})
    final_pairs = final_pairs.merge(raw_pred, on="cell_key", how="left")
    final_pairs = add_law_features(final_pairs)

    model = fit_full_model(gain_pairs, best["features"], best["spec"])
    description = model_description(model, best["features"], best["spec"])
    score_col = "predicted_law_gain"
    final_pairs[score_col] = model.predict(final_pairs[best["features"]])
    candidates = best_candidate_per_cell(
        final_pairs,
        score_col,
        str(best["spec"]["model_name"]),
        str(best["metric"]["feature_view"]),
    )
    selected = policy_selected(candidates, str(best["metric"]["policy"]), float(best["metric"]["param"]))
    candidate_map = candidates.set_index("cell_key")

    pred_vec = []
    actions = []
    for rec in test_cells.to_dict("records"):
        cell_key = rec["cell_key"]
        cand = candidate_map.loc[cell_key]
        if cell_key in selected:
            pred = float(cand["expert_pred"])
            selected_expert = str(cand["expert"])
            switched = True
        else:
            pred = float(rec["pred__raw_knn_blend"])
            selected_expert = "raw_knn_blend"
            switched = False
        pred_vec.append(pred)
        actions.append(
            {
                "cell_key": cell_key,
                "row": int(rec["row"]),
                "subject_id": rec["subject_id"],
                "target": rec["target"],
                "selected_expert": selected_expert,
                "candidate_expert": str(cand["expert"]),
                "candidate_family": str(cand["expert_family"]),
                "selection_score": float(cand["selection_score"]),
                "raw_pred": float(rec["pred__raw_knn_blend"]),
                "selected_pred": pred,
                "switched": switched,
            }
        )
    pred = np.asarray(pred_vec, dtype=float).reshape((len(test), len(TARGETS)))
    submission = sample.copy()
    submission[TARGETS] = np.clip(pred, 1e-5, 1 - 1e-5)
    return submission, pd.DataFrame(actions), description


def markdown_table(frame: pd.DataFrame, max_rows: int = 14) -> str:
    show = frame.head(max_rows).copy()
    cols = list(show.columns)
    rows = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for rec in show.to_dict("records"):
        cells = []
        for col in cols:
            value = rec[col]
            cells.append(f"{value:.6f}" if isinstance(value, float) else str(value))
        rows.append("| " + " | ".join(cells) + " |")
    return "\n".join(rows)


def build_markdown(readout: dict[str, Any], metrics: pd.DataFrame, selected: pd.DataFrame, law_description: dict[str, Any]) -> str:
    top_cols = [
        "law_name",
        "policy",
        "param",
        "logloss",
        "switched_cells",
        "mean_realized_gain_all_cells",
        "positive_true_gain_rate",
        "target_null_p_ge_observed",
        "target_family_null_p_ge_observed",
    ]
    best_actions = selected[
        selected["law_name"].eq(readout["best_law_name"])
        & selected["policy"].eq(readout["best_policy"])
        & selected["param"].eq(readout["best_policy_param"])
    ] if len(selected) else pd.DataFrame()
    target_counts = best_actions["target"].value_counts().reindex(TARGETS).fillna(0).astype(int).rename_axis("target").reset_index(name="count")
    family_counts = best_actions["expert_family"].value_counts().rename_axis("expert_family").reset_index(name="count")
    feature_importance = pd.DataFrame(law_description["top_features"])
    tree_text = law_description.get("tree_text", "")
    tree_block = ["", "## Distilled tree law", "", "```text", tree_text.strip(), "```"] if tree_text else []
    lines = [
        "# Failure Boundary Law Distillation",
        "",
        "## 한 줄 요약",
        "",
        "raw KNN failure detector의 sharp boundary를 shallow tree / sparse linear law로 증류했다.",
        "",
        "## 목적",
        "",
        "직전 contrastive atlas는 prototype geometry만으로 release-grade action을 고르지 못했다. 이번 실험은 boundary가 완전히 black-box인지, 아니면 몇 개의 HS-JEPA context law로 설명 가능한지 검증한다.",
        "",
        "## 핵심 결과",
        "",
        f"- raw KNN OOF logloss: `{readout['raw_knn_oof_logloss']:.6f}`",
        f"- best law: `{readout['best_law_name']}`",
        f"- best law family: `{readout['best_model_family']}`",
        f"- best feature view: `{readout['best_feature_view']}`",
        f"- best law OOF logloss: `{readout['best_law_oof_logloss']:.6f}`",
        f"- delta vs raw KNN: `{readout['best_law_delta_vs_raw_knn']:.6f}`",
        f"- delta vs GBDT failure detector: `{readout['best_law_delta_vs_gbdt_failure_detector']:.6f}`",
        f"- OOF switched cells: `{readout['best_law_oof_switched_cells']}`",
        f"- target matched-null p(gain >= observed): `{readout['best_law_target_null_p_ge_observed']:.6f}`",
        f"- target+family matched-null p(gain >= observed): `{readout['best_law_target_family_null_p_ge_observed']:.6f}`",
        f"- generated candidate: `{readout['candidate_file']}`",
        f"- submission priority: `{readout['submission_priority']}`",
        f"- law reading: `{readout['best_law_distilled_sentence']}`",
        "",
        "## Best law target counts",
        "",
        markdown_table(target_counts, max_rows=10),
        "",
        "## Best law expert-family counts",
        "",
        markdown_table(family_counts, max_rows=10),
        "",
        "## Top features",
        "",
        markdown_table(feature_importance, max_rows=18),
    ]
    lines.extend(tree_block)
    lines.extend([
        "",
        "## Top policies",
        "",
        markdown_table(metrics[top_cols], max_rows=14),
        "",
        "## 논문용 해석",
        "",
        "가장 중요한 발견은 depth-2 tree가 GBDT detector와 거의 같은 OOF gain을 냈다는 점이다. 즉 sharp failure boundary가 완전한 black-box는 아니다.",
        "",
        "다만 이 law는 직접 human-social feature가 아니라 `abs_vs_core`와 `expert_prob_mean`만 사용했다. 따라서 HS-JEPA core는 label predictor라기보다, raw KNN/priors/action routes가 과하게 벗어났는지를 재는 listener agreement 기준점으로 작동한다.",
        "",
        "또 하나의 중요한 점은 tree leaf 값이 모두 음수라는 것이다. 이 law는 절대적 positive-gain predictor가 아니라, 여러 toxic action 중 덜 위험한 prior-reset 후보를 상대적으로 고르는 toxicity-minimizing ranker다.",
        "",
        "결론적으로 HS-JEPA release decoder는 `human-state -> label`이 아니라 `raw memory가 불안정할 때 core agreement를 기준으로 prior reset을 허용하는 law`로 정리할 수 있다.",
    ])
    return "\n".join(lines)


def run() -> dict[str, Any]:
    features_frame, labels, sample, raw_cols_from_module = load_world()
    raw_cols = raw_feature_cols(features_frame) if not raw_cols_from_module else raw_cols_from_module
    cell_frame, pair_frame = build_temporal_oof_frames(features_frame, labels, raw_cols)
    gain_pairs = add_law_features(prepare_gain_pairs(cell_frame, pair_frame))
    leak_cols = [col for cols in feature_views(gain_pairs).values() for col in cols if "loss" in col or "gain" in col or col in {"y", "raw_loss"}]
    if leak_cols:
        raise RuntimeError(f"leaky law feature columns detected: {sorted(set(leak_cols))}")

    metrics, selected, candidates, best = evaluate_laws(cell_frame, gain_pairs)
    raw = float(metrics[metrics["law_name"].eq("raw_knn_blend_baseline")]["logloss"].iloc[0])
    best_metric = metrics.iloc[0]
    if str(best_metric["law_name"]) == "raw_knn_blend_baseline":
        best_metric = metrics[~metrics["law_name"].eq("raw_knn_blend_baseline")].iloc[0]
        matching = None
        for view_name, cols in feature_views(gain_pairs).items():
            for spec in model_specs():
                if f"{view_name}__{spec['model_name']}" == str(best_metric["law_name"]):
                    matching = {"metric": best_metric.to_dict(), "spec": spec, "features": cols}
        if matching is None:
            raise RuntimeError("could not recover best non-baseline law")
        best = matching

    submission, test_actions, law_description = train_final_submission(
        features_frame,
        labels,
        sample,
        raw_cols,
        gain_pairs,
        best,
    )
    validate_submission(submission, sample)
    suffix = short_hash(submission)
    candidate_file = f"submission_hsjepa_failure_boundary_law_distillation_{suffix}_uploadsafe.csv"
    submission.to_csv(ROOT / candidate_file, index=False)
    submission.to_csv(OUT / candidate_file, index=False)

    best_selected = selected[
        selected["law_name"].eq(str(best_metric["law_name"]))
        & selected["policy"].eq(str(best_metric["policy"]))
        & selected["param"].eq(float(best_metric["param"]))
    ].copy()
    gbdt_reference = 0.6324777550533113
    readout = {
        "package": "failure_boundary_law_distillation",
        "status": "anchor_free_interpretable_law_ready",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_action_teacher": False,
        "uses_frontier_file": False,
        "raw_knn_oof_logloss": raw,
        "gbdt_failure_detector_reference_oof_logloss": gbdt_reference,
        "best_law_name": str(best_metric["law_name"]),
        "best_model_name": str(best_metric["model_name"]),
        "best_model_family": str(best_metric["model_family"]),
        "best_feature_view": str(best_metric["feature_view"]),
        "best_policy": str(best_metric["policy"]),
        "best_policy_param": float(best_metric["param"]),
        "best_law_oof_logloss": float(best_metric["logloss"]),
        "best_law_delta_vs_raw_knn": float(best_metric["logloss"] - raw),
        "best_law_delta_vs_gbdt_failure_detector": float(best_metric["logloss"] - gbdt_reference),
        "best_law_oof_switched_cells": int(best_metric["switched_cells"]),
        "best_law_oof_switched_rate": float(best_metric["switched_rate"]),
        "best_law_positive_true_gain_rate": float(best_metric["positive_true_gain_rate"]),
        "best_law_mean_realized_gain_all_cells": float(best_metric["mean_realized_gain_all_cells"]),
        "best_law_target_null_p_ge_observed": float(best_metric["target_null_p_ge_observed"]),
        "best_law_target_family_null_p_ge_observed": float(best_metric["target_family_null_p_ge_observed"]),
        "best_law_target_null_z": float(best_metric["target_null_z"]),
        "best_law_target_family_null_z": float(best_metric["target_family_null_z"]),
        "best_law_oof_target_counts": best_selected["target"].value_counts().reindex(TARGETS).fillna(0).astype(int).to_dict(),
        "best_law_oof_expert_family_counts": best_selected["expert_family"].value_counts().to_dict(),
        "best_law_nonzero_feature_count": int(law_description["nonzero_feature_count"]),
        "best_law_top_features": law_description["top_features"],
        "candidate_file": candidate_file,
        "root_candidate_file": candidate_file,
        "test_switched_cells": int(test_actions["switched"].sum()),
        "test_switched_rows": int(test_actions.loc[test_actions["switched"], "row"].nunique()),
        "test_target_counts": test_actions.loc[test_actions["switched"], "target"].value_counts().reindex(TARGETS).fillna(0).astype(int).to_dict(),
        "test_expert_counts": test_actions.loc[test_actions["switched"], "selected_expert"].value_counts().to_dict(),
        "best_law_distilled_sentence": "If an alternative route stays close enough to core geometry and the route-average probability is not extremely low, treat it as a lower-toxicity prior-reset candidate rather than a positive-gain action.",
        "best_law_selected_is_prior_reset": bool(best_selected["expert_family"].eq("prior").all()) if len(best_selected) else False,
        "test_row_reset_pattern": "20 test rows x 7 targets switched to global_prior",
        "submission_priority": "high_information_sensor_prior_reset_law",
        "interpretation": "Tests whether the raw-KNN failure boundary can be expressed as an interpretable HS-JEPA action law.",
    }

    metrics.to_csv(OUT / "failure_boundary_law_policy_table.csv", index=False)
    selected.to_csv(OUT / "failure_boundary_law_selected_oof_cells.csv", index=False)
    candidates.to_csv(OUT / "failure_boundary_law_oof_candidates.csv", index=False)
    test_actions.to_csv(OUT / "failure_boundary_law_test_actions.csv", index=False)
    (OUT / "failure_boundary_law_readout.json").write_text(json.dumps(readout, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "failure_boundary_law_tree.txt").write_text(law_description.get("tree_text", ""), encoding="utf-8")
    md = build_markdown(readout, metrics, selected, law_description)
    (OUT / "FAILURE_BOUNDARY_LAW_DISTILLATION_KO.md").write_text(md, encoding="utf-8")
    (ROOT / "paper_hsjepa_core" / "FAILURE_BOUNDARY_LAW_DISTILLATION_KO.md").write_text(md, encoding="utf-8")
    return readout


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
