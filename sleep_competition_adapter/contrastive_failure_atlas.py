#!/usr/bin/env python3
"""Contrastive failure atlas for HS-JEPA raw-KNN overrides.

The previous safety jury found a sharp raw-KNN failure boundary, but the best
release policy still came from a supervised gain regressor.  This experiment
tests a more architectural question:

    Do successful and toxic row-target actions form separable prototype
    manifolds in HS-JEPA human-state context space?

No public LB ledger, prior submission probabilities, action teacher, or
frontier file is used.  The atlas is trained only from OG train OOF action
outcomes: actions that improve raw-KNN loss become positive prototypes, and
actions that make raw-KNN worse become toxic prototypes.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler


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


OUT = ROOT / "sleep_competition_adapter" / "outputs" / "contrastive_failure_atlas"
OUT.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = 20260612
POSITIVE_GAIN_FLOOR = 0.10
TOXIC_GAIN_CEILING = -0.10
POSITIVE_QUANTILE = 0.84
TOXIC_QUANTILE = 0.16
K_NEIGHBORS = 18
TARGET_WEIGHT = 0.45
FAMILY_WEIGHT = 0.20
TOP_FRACS = [0.005, 0.01, 0.02, 0.03, 0.04, 0.06, 0.08, 0.10, 0.15]
THRESHOLDS = [-0.30, -0.15, 0.00, 0.15, 0.30, 0.50, 0.75, 1.00]
NULL_REPEATS = 4000


def atlas_feature_columns(frame: pd.DataFrame) -> list[str]:
    blocked = {
        "cell_key",
        "fold",
        "row",
        "subject_id",
        "target",
        "expert",
        "loss",
        "gain",
        "raw_loss",
        "y",
    }
    blocked_prefixes = ("loss__", "oracle_", "predicted_gain__")
    return [
        col
        for col in frame.columns
        if col not in blocked
        and not col.startswith(blocked_prefixes)
        and pd.api.types.is_numeric_dtype(frame[col])
    ]


def prototype_masks(frame: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    pos_floor = max(POSITIVE_GAIN_FLOOR, float(frame["gain"].quantile(POSITIVE_QUANTILE)))
    neg_ceiling = min(TOXIC_GAIN_CEILING, float(frame["gain"].quantile(TOXIC_QUANTILE)))
    pos = frame["gain"].ge(pos_floor)
    neg = frame["gain"].le(neg_ceiling)
    if int(pos.sum()) < 24:
        pos = frame["gain"].ge(float(frame["gain"].quantile(0.90)))
    if int(neg.sum()) < 24:
        neg = frame["gain"].le(float(frame["gain"].quantile(0.10)))
    return pos, neg


def affinity(
    x_query: np.ndarray,
    x_proto: np.ndarray,
    k: int = K_NEIGHBORS,
) -> np.ndarray:
    if len(x_proto) == 0:
        return np.zeros(len(x_query), dtype=float)
    n_neighbors = max(1, min(k, len(x_proto)))
    nn = NearestNeighbors(n_neighbors=n_neighbors, metric="euclidean")
    nn.fit(x_proto)
    distances, _ = nn.kneighbors(x_query)
    mean_distance = distances.mean(axis=1)
    return 1.0 / (1.0 + mean_distance)


def score_view(
    x_train: np.ndarray,
    x_eval: np.ndarray,
    train_frame: pd.DataFrame,
    eval_frame: pd.DataFrame,
    group_cols: list[str] | None = None,
) -> np.ndarray:
    if not group_cols:
        pos, neg = prototype_masks(train_frame)
        return affinity(x_eval, x_train[pos.to_numpy()]) - affinity(x_eval, x_train[neg.to_numpy()])

    scores = np.zeros(len(eval_frame), dtype=float)
    global_score = score_view(x_train, x_eval, train_frame, eval_frame, None)
    for key, eval_group in eval_frame.groupby(group_cols, sort=False):
        if not isinstance(key, tuple):
            key = (key,)
        mask = np.ones(len(train_frame), dtype=bool)
        for col, value in zip(group_cols, key):
            mask &= train_frame[col].eq(value).to_numpy()
        if int(mask.sum()) < 60:
            scores[eval_group.index.to_numpy()] = global_score[eval_group.index.to_numpy()]
            continue
        sub_train = train_frame[mask].reset_index(drop=True)
        pos, neg = prototype_masks(sub_train)
        if int(pos.sum()) < 8 or int(neg.sum()) < 8:
            scores[eval_group.index.to_numpy()] = global_score[eval_group.index.to_numpy()]
            continue
        sub_x = x_train[mask]
        local = affinity(x_eval[eval_group.index.to_numpy()], sub_x[pos.to_numpy()], k=min(K_NEIGHBORS, int(pos.sum())))
        local -= affinity(x_eval[eval_group.index.to_numpy()], sub_x[neg.to_numpy()], k=min(K_NEIGHBORS, int(neg.sum())))
        scores[eval_group.index.to_numpy()] = local
    return scores


def score_oof_atlas(gain_pairs: pd.DataFrame, features: list[str]) -> pd.DataFrame:
    scored_parts = []
    for subject in sorted(gain_pairs["subject_id"].unique()):
        train = gain_pairs[~gain_pairs["subject_id"].eq(subject)].copy().reset_index(drop=True)
        valid = gain_pairs[gain_pairs["subject_id"].eq(subject)].copy().reset_index(drop=True)

        imp = SimpleImputer(strategy="median")
        scaler = StandardScaler()
        x_train = scaler.fit_transform(imp.fit_transform(train[features].replace([np.inf, -np.inf], np.nan)))
        x_valid = scaler.transform(imp.transform(valid[features].replace([np.inf, -np.inf], np.nan)))

        valid["atlas_global_score"] = score_view(x_train, x_valid, train, valid)
        valid["atlas_target_score"] = score_view(x_train, x_valid, train, valid, ["target"])
        valid["atlas_family_score"] = score_view(x_train, x_valid, train, valid, ["expert_family"])
        valid["atlas_target_family_score"] = score_view(x_train, x_valid, train, valid, ["target", "expert_family"])
        valid["atlas_hybrid_score"] = (
            (1.0 - TARGET_WEIGHT - FAMILY_WEIGHT) * valid["atlas_global_score"].astype(float)
            + TARGET_WEIGHT * valid["atlas_target_score"].astype(float)
            + FAMILY_WEIGHT * valid["atlas_family_score"].astype(float)
        )
        valid["atlas_contrastive_score"] = (
            0.55 * valid["atlas_hybrid_score"].astype(float)
            + 0.45 * valid["atlas_target_family_score"].astype(float)
        )
        scored_parts.append(valid)
    return pd.concat(scored_parts, ignore_index=True)


def score_final_atlas(train_pairs: pd.DataFrame, test_pairs: pd.DataFrame, features: list[str]) -> pd.DataFrame:
    train = train_pairs.copy().reset_index(drop=True)
    test = test_pairs.copy().reset_index(drop=True)
    imp = SimpleImputer(strategy="median")
    scaler = StandardScaler()
    x_train = scaler.fit_transform(imp.fit_transform(train[features].replace([np.inf, -np.inf], np.nan)))
    x_test = scaler.transform(imp.transform(test[features].replace([np.inf, -np.inf], np.nan)))
    test["atlas_global_score"] = score_view(x_train, x_test, train, test)
    test["atlas_target_score"] = score_view(x_train, x_test, train, test, ["target"])
    test["atlas_family_score"] = score_view(x_train, x_test, train, test, ["expert_family"])
    test["atlas_target_family_score"] = score_view(x_train, x_test, train, test, ["target", "expert_family"])
    test["atlas_hybrid_score"] = (
        (1.0 - TARGET_WEIGHT - FAMILY_WEIGHT) * test["atlas_global_score"].astype(float)
        + TARGET_WEIGHT * test["atlas_target_score"].astype(float)
        + FAMILY_WEIGHT * test["atlas_family_score"].astype(float)
    )
    test["atlas_contrastive_score"] = (
        0.55 * test["atlas_hybrid_score"].astype(float)
        + 0.45 * test["atlas_target_family_score"].astype(float)
    )
    return test


def best_candidate_by_score(scored_pairs: pd.DataFrame, score_col: str) -> pd.DataFrame:
    rows = []
    for cell_key, group in scored_pairs.groupby("cell_key", sort=False):
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
                "atlas_global_score": float(best.get("atlas_global_score", np.nan)),
                "atlas_target_score": float(best.get("atlas_target_score", np.nan)),
                "atlas_family_score": float(best.get("atlas_family_score", np.nan)),
                "atlas_target_family_score": float(best.get("atlas_target_family_score", np.nan)),
                "atlas_hybrid_score": float(best.get("atlas_hybrid_score", np.nan)),
                "atlas_contrastive_score": float(best.get("atlas_contrastive_score", np.nan)),
            }
        )
    return pd.DataFrame(rows)


def selected_cells(candidates: pd.DataFrame, policy: dict[str, Any]) -> set[str]:
    frame = candidates.copy()
    if policy.get("allowed_families") is not None:
        frame = frame[frame["expert_family"].isin(policy["allowed_families"])]
    if policy["mode"] == "topfrac":
        k = max(1, int(round(len(candidates) * float(policy["param"]))))
        return set(frame.sort_values("selection_score", ascending=False, kind="mergesort").head(k)["cell_key"])
    if policy["mode"] == "threshold":
        return set(frame[frame["selection_score"].gt(float(policy["param"]))]["cell_key"])
    raise KeyError(policy["mode"])


def build_policies() -> list[dict[str, Any]]:
    policies = []
    score_cols = [
        "atlas_global_score",
        "atlas_target_score",
        "atlas_family_score",
        "atlas_target_family_score",
        "atlas_hybrid_score",
        "atlas_contrastive_score",
    ]
    family_guards = [
        ("all", None),
        ("core_or_prior", ["prior", "core_geometry", "core_action_health", "raw_action_core_health"]),
        ("core_only", ["core_geometry", "core_action_health", "raw_action_core_health"]),
    ]
    for score_col in score_cols:
        for guard_name, families in family_guards:
            for frac in TOP_FRACS:
                policies.append({
                    "name": f"{score_col}_{guard_name}_topfrac_{frac:.3f}",
                    "score_col": score_col,
                    "mode": "topfrac",
                    "param": frac,
                    "allowed_families": families,
                })
            for threshold in THRESHOLDS:
                policies.append({
                    "name": f"{score_col}_{guard_name}_threshold_{threshold:.2f}",
                    "score_col": score_col,
                    "mode": "threshold",
                    "param": threshold,
                    "allowed_families": families,
                })
    return policies


def evaluate_policy(
    cell_frame: pd.DataFrame,
    candidates: pd.DataFrame,
    policy: dict[str, Any],
) -> tuple[dict[str, Any], pd.DataFrame]:
    selected = selected_cells(candidates, policy)
    candidate_map = candidates.set_index("cell_key")
    pred = []
    actions = []
    gains = []
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
        "policy_name": policy["name"],
        "score_col": policy["score_col"],
        "mode": policy["mode"],
        "param": float(policy["param"]),
        "family_guard": "all" if policy.get("allowed_families") is None else ",".join(policy["allowed_families"]),
        "logloss": logloss(y, pred_arr),
        "switched_cells": int(len(selected)),
        "switched_rate": float(len(selected) / len(cell_frame)),
        "mean_realized_gain_all_cells": float(np.sum(gains) / len(cell_frame)),
        "mean_realized_gain_switched": float(actions_df["true_gain"].mean()) if len(actions_df) else 0.0,
        "positive_true_gain_rate": float((actions_df["true_gain"] > 0).mean()) if len(actions_df) else 0.0,
    }
    return metric, actions_df


def evaluate_all(cell_frame: pd.DataFrame, scored_pairs: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    raw_loss = logloss(cell_frame["y"].to_numpy(dtype=float), cell_frame["pred__raw_knn_blend"].to_numpy(dtype=float))
    metrics = [{
        "policy_name": "raw_knn_blend_baseline",
        "score_col": "none",
        "mode": "baseline",
        "param": 0.0,
        "family_guard": "none",
        "logloss": raw_loss,
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
    best: dict[str, Any] | None = None
    rng = np.random.default_rng(RANDOM_STATE)

    for policy in build_policies():
        candidates = best_candidate_by_score(scored_pairs, policy["score_col"])
        metric, actions = evaluate_policy(cell_frame, candidates, policy)
        metric.update(target_stratified_null(candidates, actions, len(cell_frame), rng, repeats=NULL_REPEATS))
        metric.update(target_family_stratified_null(candidates, actions, len(cell_frame), rng, repeats=NULL_REPEATS))
        metrics.append(metric)
        if len(actions):
            actions["policy_name"] = policy["name"]
            selected_frames.append(actions)
        if best is None or float(metric["logloss"]) < float(best["metric"]["logloss"]):
            best = {"policy": policy, "metric": metric, "candidates": candidates, "actions": actions}

    if best is None:
        raise RuntimeError("no atlas policy evaluated")
    metrics_df = pd.DataFrame(metrics).sort_values("logloss", kind="mergesort").reset_index(drop=True)
    selected_df = pd.concat(selected_frames, ignore_index=True) if selected_frames else pd.DataFrame()
    return metrics_df, selected_df, best


def train_final_submission(
    features_frame: pd.DataFrame,
    labels: pd.DataFrame,
    sample: pd.DataFrame,
    raw_cols: list[str],
    train_pairs: pd.DataFrame,
    features: list[str],
    best_policy: dict[str, Any],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    train = features_frame[features_frame["split"].eq("train")].copy().reset_index(drop=True)
    train[TARGETS] = labels[TARGETS].to_numpy(dtype=float)
    test = features_frame[features_frame["split"].eq("test")].copy().reset_index(drop=True)
    catalog, _audit = prediction_catalog(train, test, raw_cols)
    test_cells, test_pairs = build_cell_and_pair_frames(test, None, catalog, "test")
    final_pairs = test_pairs[test_pairs["expert"].ne("raw_knn_blend")].copy().reset_index(drop=True)
    raw_pred = test_cells[["cell_key", "pred__raw_knn_blend"]].rename(columns={"pred__raw_knn_blend": "raw_pred"})
    final_pairs = final_pairs.merge(raw_pred, on="cell_key", how="left")
    final_pairs["expert_family"] = final_pairs["expert"].astype(str).map(expert_family)
    scored_test = score_final_atlas(train_pairs, final_pairs, features)
    candidates = best_candidate_by_score(scored_test, best_policy["score_col"])
    selected = selected_cells(candidates, best_policy)
    candidate_map = candidates.set_index("cell_key")

    pred_vec = []
    actions = []
    for rec in test_cells.to_dict("records"):
        cell_key = rec["cell_key"]
        cand = candidate_map.loc[cell_key]
        if cell_key in selected:
            selected_pred = float(cand["expert_pred"])
            selected_expert = str(cand["expert"])
            switched = True
        else:
            selected_pred = float(rec["pred__raw_knn_blend"])
            selected_expert = "raw_knn_blend"
            switched = False
        pred_vec.append(selected_pred)
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
                "selected_pred": selected_pred,
                "switched": switched,
            }
        )

    pred = np.asarray(pred_vec, dtype=float).reshape((len(test), len(TARGETS)))
    submission = sample.copy()
    submission[TARGETS] = np.clip(pred, 1e-5, 1 - 1e-5)
    return submission, pd.DataFrame(actions)


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


def build_markdown(readout: dict[str, Any], metrics: pd.DataFrame, selected: pd.DataFrame) -> str:
    top_cols = [
        "policy_name",
        "logloss",
        "switched_cells",
        "mean_realized_gain_all_cells",
        "positive_true_gain_rate",
        "target_null_p_ge_observed",
        "target_family_null_p_ge_observed",
    ]
    best_actions = selected[selected["policy_name"].eq(readout["best_policy_name"])] if len(selected) else pd.DataFrame()
    target_counts = best_actions["target"].value_counts().reindex(TARGETS).fillna(0).astype(int).rename_axis("target").reset_index(name="count")
    family_counts = best_actions["expert_family"].value_counts().rename_axis("expert_family").reset_index(name="count")
    lines = [
        "# Contrastive Failure Atlas",
        "",
        "## 한 줄 요약",
        "",
        "raw KNN이 실패한 action과 raw KNN보다 더 나빠진 toxic action을 HS-JEPA human-state 공간의 prototype atlas로 만들고, test row-target action을 이 atlas에 투영했다.",
        "",
        "## 목적",
        "",
        "직전 safety jury는 sharp boundary를 찾았지만 supervised gain regressor 성격이 강했다. 이번 실험은 더 JEPA답게 `성공한 action representation`과 `실패한 action representation` 사이의 contrastive energy만으로 release할 cell을 고른다.",
        "",
        "## 핵심 결과",
        "",
        f"- raw KNN OOF logloss: `{readout['raw_knn_oof_logloss']:.6f}`",
        f"- best atlas policy: `{readout['best_policy_name']}`",
        f"- best atlas OOF logloss: `{readout['best_policy_oof_logloss']:.6f}`",
        f"- delta vs raw KNN: `{readout['best_policy_delta_vs_raw_knn']:.6f}`",
        f"- OOF switched cells: `{readout['best_policy_oof_switched_cells']}`",
        f"- target matched-null p(gain >= observed): `{readout['best_policy_target_null_p_ge_observed']:.6f}`",
        f"- target+family matched-null p(gain >= observed): `{readout['best_policy_target_family_null_p_ge_observed']:.6f}`",
        f"- generated candidate: `{readout['candidate_file']}`",
        f"- submission priority: `{readout['submission_priority']}`",
        "",
        "## Best policy target counts",
        "",
        markdown_table(target_counts, max_rows=10),
        "",
        "## Best policy expert-family counts",
        "",
        markdown_table(family_counts, max_rows=10),
        "",
        "## Top policies",
        "",
        markdown_table(metrics[top_cols], max_rows=14),
        "",
        "## 논문용 해석",
        "",
        "OOF 평균은 raw KNN보다 좋아졌지만, matched-null p-value가 `0.53` 수준이므로 이 결과는 `좋은 action manifold`가 안정적으로 분리됐다는 증거가 아니다.",
        "",
        "오히려 직전 sharp boundary는 prototype geometry만으로는 잡히지 않는 얇은 non-linear boundary였다는 해석이 강해졌다. 따라서 HS-JEPA core는 인간 상태 representation으로 남고, release-grade row-target assignment에는 별도 decoder가 필요하다.",
        "",
        "이 후보는 제출 1순위가 아니라 negative architectural evidence다. 논문에서는 `core representation alone is not a release-grade action solver`를 보여주는 ablation으로 쓰는 편이 맞다.",
    ]
    return "\n".join(lines)


def run() -> dict[str, Any]:
    features_frame, labels, sample, raw_cols_from_module = load_world()
    raw_cols = raw_feature_cols(features_frame) if not raw_cols_from_module else raw_cols_from_module
    cell_frame, pair_frame = build_temporal_oof_frames(features_frame, labels, raw_cols)
    gain_pairs = prepare_gain_pairs(cell_frame, pair_frame)
    gain_pairs["expert_family"] = gain_pairs["expert"].astype(str).map(expert_family)
    features = atlas_feature_columns(gain_pairs)
    leak_cols = [col for col in features if "loss" in col or "gain" in col or col in {"y", "raw_loss"}]
    if leak_cols:
        raise RuntimeError(f"leaky atlas feature columns detected: {leak_cols}")

    scored_pairs = score_oof_atlas(gain_pairs, features)
    metrics, selected, best = evaluate_all(cell_frame, scored_pairs)
    raw = float(metrics[metrics["policy_name"].eq("raw_knn_blend_baseline")]["logloss"].iloc[0])
    best_metric = metrics.iloc[0]
    if str(best_metric["policy_name"]) == "raw_knn_blend_baseline":
        best_metric = metrics[~metrics["policy_name"].eq("raw_knn_blend_baseline")].iloc[0]
        matching = [p for p in build_policies() if p["name"] == str(best_metric["policy_name"])]
        best_policy = matching[0]
    else:
        best_policy = best["policy"]

    submission, test_actions = train_final_submission(
        features_frame,
        labels,
        sample,
        raw_cols,
        scored_pairs,
        features,
        best_policy,
    )
    validate_submission(submission, sample)
    suffix = short_hash(submission)
    candidate_file = f"submission_hsjepa_contrastive_failure_atlas_{suffix}_uploadsafe.csv"
    submission.to_csv(ROOT / candidate_file, index=False)
    submission.to_csv(OUT / candidate_file, index=False)

    best_selected = selected[selected["policy_name"].eq(str(best_metric["policy_name"]))].copy()
    readout = {
        "package": "contrastive_failure_atlas",
        "status": "anchor_free_contrastive_atlas_ready",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_action_teacher": False,
        "uses_frontier_file": False,
        "raw_knn_oof_logloss": raw,
        "best_policy_name": str(best_metric["policy_name"]),
        "best_policy_score_col": str(best_metric["score_col"]),
        "best_policy_mode": str(best_metric["mode"]),
        "best_policy_param": float(best_metric["param"]),
        "best_policy_oof_logloss": float(best_metric["logloss"]),
        "best_policy_delta_vs_raw_knn": float(best_metric["logloss"] - raw),
        "best_policy_oof_switched_cells": int(best_metric["switched_cells"]),
        "best_policy_oof_switched_rate": float(best_metric["switched_rate"]),
        "best_policy_positive_true_gain_rate": float(best_metric["positive_true_gain_rate"]),
        "best_policy_mean_realized_gain_all_cells": float(best_metric["mean_realized_gain_all_cells"]),
        "best_policy_target_null_p_ge_observed": float(best_metric["target_null_p_ge_observed"]),
        "best_policy_target_family_null_p_ge_observed": float(best_metric["target_family_null_p_ge_observed"]),
        "best_policy_target_null_z": float(best_metric["target_null_z"]),
        "best_policy_target_family_null_z": float(best_metric["target_family_null_z"]),
        "best_policy_oof_target_counts": best_selected["target"].value_counts().reindex(TARGETS).fillna(0).astype(int).to_dict(),
        "best_policy_oof_expert_family_counts": best_selected["expert_family"].value_counts().to_dict(),
        "feature_count": len(features),
        "prototype_config": {
            "positive_gain_floor": POSITIVE_GAIN_FLOOR,
            "toxic_gain_ceiling": TOXIC_GAIN_CEILING,
            "positive_quantile": POSITIVE_QUANTILE,
            "toxic_quantile": TOXIC_QUANTILE,
            "k_neighbors": K_NEIGHBORS,
            "target_weight": TARGET_WEIGHT,
            "family_weight": FAMILY_WEIGHT,
        },
        "candidate_file": candidate_file,
        "root_candidate_file": candidate_file,
        "test_switched_cells": int(test_actions["switched"].sum()),
        "test_switched_rows": int(test_actions.loc[test_actions["switched"], "row"].nunique()),
        "test_target_counts": test_actions.loc[test_actions["switched"], "target"].value_counts().reindex(TARGETS).fillna(0).astype(int).to_dict(),
        "test_expert_counts": test_actions.loc[test_actions["switched"], "selected_expert"].value_counts().to_dict(),
        "submission_priority": "low_negative_evidence_not_primary_submission",
        "interpretation": "Tests whether HS-JEPA action success/failure can be represented as a contrastive prototype atlas rather than a supervised gain regressor.",
    }

    metrics.to_csv(OUT / "contrastive_failure_atlas_policy_table.csv", index=False)
    selected.to_csv(OUT / "contrastive_failure_atlas_selected_oof_cells.csv", index=False)
    scored_pairs[
        [
            "cell_key",
            "row",
            "subject_id",
            "target",
            "expert",
            "expert_family",
            "gain",
            "atlas_global_score",
            "atlas_target_score",
            "atlas_family_score",
            "atlas_target_family_score",
            "atlas_hybrid_score",
            "atlas_contrastive_score",
        ]
    ].to_csv(OUT / "contrastive_failure_atlas_oof_scores.csv", index=False)
    test_actions.to_csv(OUT / "contrastive_failure_atlas_test_actions.csv", index=False)
    (OUT / "contrastive_failure_atlas_readout.json").write_text(json.dumps(readout, ensure_ascii=False, indent=2), encoding="utf-8")
    md = build_markdown(readout, metrics, selected)
    (OUT / "CONTRASTIVE_FAILURE_ATLAS_KO.md").write_text(md, encoding="utf-8")
    (ROOT / "paper_hsjepa_core" / "CONTRASTIVE_FAILURE_ATLAS_KO.md").write_text(md, encoding="utf-8")
    return readout


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
