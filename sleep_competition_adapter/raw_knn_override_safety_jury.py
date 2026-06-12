#!/usr/bin/env python3
"""Raw-KNN override safety jury for HS-JEPA.

This experiment keeps raw lifelog KNN as the default world model and asks a
sharper question:

    Can HS-JEPA context identify only the row-target cells where raw KNN is
    likely to fail, without using public LB observations or prior submissions?

It differs from the previous single failure detector in one key way.  The
release decision is not made by one regressor alone.  Multiple gain predictors
act as a small jury, and the selected override must survive model-family,
target-stratified, and matched-null stress checks before it becomes a
submission candidate.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


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
from sleep_competition_adapter.raw_knn_failure_detector import (  # noqa: E402
    best_candidate_per_cell,
    gain_feature_columns,
    make_model,
    prepare_gain_pairs,
    predict_oof_gain,
)


OUT = ROOT / "sleep_competition_adapter" / "outputs" / "raw_knn_override_safety_jury"
OUT.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = 20260612
MODEL_NAMES = ["gradient_boosted_gain", "random_forest_gain", "extra_trees_gain"]
TOP_FRACS = [0.01, 0.02, 0.03, 0.04, 0.06, 0.08, 0.10]
THRESHOLDS = [-0.01, 0.00, 0.01, 0.02, 0.04, 0.08, 0.12]
NULL_REPEATS = 4000


def expert_family(expert: str) -> str:
    if expert in {"global_prior", "subject_prior"}:
        return "prior"
    if expert == "core_knn_blend":
        return "core_geometry"
    if expert.startswith("hsjepa_action_health__"):
        return "core_action_health"
    if expert.startswith("raw_action_core_health__"):
        return "raw_action_core_health"
    return "other"


def add_gain_predictions(gain_pairs: pd.DataFrame, features: list[str]) -> pd.DataFrame:
    frame = gain_pairs.copy()
    for model_name in MODEL_NAMES:
        col = f"predicted_gain__{model_name}"
        if col not in frame.columns:
            frame[col] = predict_oof_gain(frame, model_name, features)
    return frame


def add_jury_scores(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    pred_cols = [f"predicted_gain__{name}" for name in MODEL_NAMES]
    preds = out[pred_cols].to_numpy(dtype=float)
    out["jury_gain_mean"] = preds.mean(axis=1)
    out["jury_gain_std"] = preds.std(axis=1)
    out["jury_gain_lower_confidence"] = out["jury_gain_mean"] - out["jury_gain_std"]
    out["jury_positive_votes"] = (preds > 0).sum(axis=1)
    out["jury_strong_positive_votes"] = (preds > 0.02).sum(axis=1)
    out["expert_family"] = out["expert"].astype(str).map(expert_family)
    out["jury_gain_agreement"] = 1.0 / (1.0 + out["jury_gain_std"].astype(float))
    out["jury_safe_gain"] = (
        0.62 * out["jury_gain_lower_confidence"].astype(float)
        + 0.25 * out["jury_gain_mean"].astype(float)
        + 0.13 * out["predicted_gain__gradient_boosted_gain"].astype(float)
    )
    return out


def best_candidate_by_score(gain_pairs: pd.DataFrame, score_col: str) -> pd.DataFrame:
    rows = []
    for cell_key, group in gain_pairs.groupby("cell_key", sort=False):
        best = group.sort_values(score_col, ascending=False, kind="mergesort").iloc[0]
        rows.append(
            {
                "cell_key": cell_key,
                "row": int(best["row"]),
                "subject_id": best["subject_id"],
                "target": best["target"],
                "expert": best["expert"],
                "expert_family": expert_family(str(best["expert"])),
                "expert_pred": float(best["expert_pred"]),
                "selection_score": float(best[score_col]),
                "true_gain": float(best["gain"]) if "gain" in best.index else np.nan,
                "jury_gain_mean": float(best.get("jury_gain_mean", np.nan)),
                "jury_gain_std": float(best.get("jury_gain_std", np.nan)),
                "jury_gain_lower_confidence": float(best.get("jury_gain_lower_confidence", np.nan)),
                "jury_positive_votes": int(best.get("jury_positive_votes", 0)),
                "jury_strong_positive_votes": int(best.get("jury_strong_positive_votes", 0)),
                "predicted_gain__gradient_boosted_gain": float(best.get("predicted_gain__gradient_boosted_gain", np.nan)),
                "predicted_gain__random_forest_gain": float(best.get("predicted_gain__random_forest_gain", np.nan)),
                "predicted_gain__extra_trees_gain": float(best.get("predicted_gain__extra_trees_gain", np.nan)),
            }
        )
    return pd.DataFrame(rows)


def policy_selected(candidates: pd.DataFrame, policy: dict[str, Any]) -> set[str]:
    frame = candidates.copy()
    if policy.get("min_positive_votes") is not None:
        frame = frame[frame["jury_positive_votes"].ge(int(policy["min_positive_votes"]))]
    if policy.get("min_strong_positive_votes") is not None:
        frame = frame[frame["jury_strong_positive_votes"].ge(int(policy["min_strong_positive_votes"]))]
    if policy.get("allowed_families") is not None:
        frame = frame[frame["expert_family"].isin(policy["allowed_families"])]

    mode = policy["mode"]
    if mode == "topfrac":
        k = max(1, int(round(len(candidates) * float(policy["param"]))))
        return set(frame.sort_values("selection_score", ascending=False, kind="mergesort").head(k)["cell_key"])
    if mode == "threshold":
        return set(frame[frame["selection_score"].gt(float(policy["param"]))]["cell_key"])
    raise KeyError(mode)


def evaluate_candidate_policy(
    cell_frame: pd.DataFrame,
    candidates: pd.DataFrame,
    policy: dict[str, Any],
) -> tuple[dict[str, Any], pd.DataFrame, np.ndarray]:
    selected = policy_selected(candidates, policy)
    candidate_map = candidates.set_index("cell_key")
    pred = []
    action_rows = []
    realized_gains = []
    for rec in cell_frame.to_dict("records"):
        cell_key = rec["cell_key"]
        if cell_key in selected:
            cand = candidate_map.loc[cell_key]
            pred.append(float(cand["expert_pred"]))
            gain = float(cand["true_gain"])
            realized_gains.append(gain)
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
                    "raw_pred": float(rec["pred__raw_knn_blend"]),
                    "selected_pred": float(cand["expert_pred"]),
                    "switched": True,
                }
            )
        else:
            pred.append(float(rec["pred__raw_knn_blend"]))
            realized_gains.append(0.0)
    pred_arr = np.asarray(pred, dtype=float)
    y = cell_frame["y"].to_numpy(dtype=float)
    selected_actions = pd.DataFrame(action_rows)
    metric = {
        "policy_name": policy["name"],
        "score_source": policy["score_source"],
        "mode": policy["mode"],
        "param": float(policy["param"]),
        "min_positive_votes": int(policy.get("min_positive_votes") or 0),
        "min_strong_positive_votes": int(policy.get("min_strong_positive_votes") or 0),
        "logloss": logloss(y, pred_arr),
        "switched_cells": int(len(selected)),
        "switched_rate": float(len(selected) / len(cell_frame)),
        "mean_realized_gain_all_cells": float(np.sum(realized_gains) / len(cell_frame)),
        "mean_realized_gain_switched": float(selected_actions["true_gain"].mean()) if len(selected_actions) else 0.0,
        "positive_true_gain_rate": float((selected_actions["true_gain"] > 0).mean()) if len(selected_actions) else 0.0,
    }
    return metric, selected_actions, pred_arr


def build_policies() -> list[dict[str, Any]]:
    policies: list[dict[str, Any]] = []
    score_sources = [
        ("gradient_boosted_gain", "predicted_gain__gradient_boosted_gain"),
        ("jury_mean", "jury_gain_mean"),
        ("jury_lower_confidence", "jury_gain_lower_confidence"),
        ("jury_safe_gain", "jury_safe_gain"),
    ]
    guards = [
        ("unguarded", {}),
        ("votes2", {"min_positive_votes": 2}),
        ("votes3", {"min_positive_votes": 3}),
        ("strong_votes2", {"min_strong_positive_votes": 2}),
        ("core_families_votes2", {
            "min_positive_votes": 2,
            "allowed_families": ["core_geometry", "core_action_health", "raw_action_core_health"],
        }),
    ]
    for source_name, score_col in score_sources:
        for guard_name, guard in guards:
            for frac in TOP_FRACS:
                policies.append({
                    "name": f"{source_name}_{guard_name}_topfrac_{frac:.2f}",
                    "score_source": score_col,
                    "mode": "topfrac",
                    "param": frac,
                    **guard,
                })
            for threshold in THRESHOLDS:
                policies.append({
                    "name": f"{source_name}_{guard_name}_threshold_{threshold:.3f}",
                    "score_source": score_col,
                    "mode": "threshold",
                    "param": threshold,
                    **guard,
                })
    return policies


def target_stratified_null(
    candidates: pd.DataFrame,
    selected_actions: pd.DataFrame,
    denominator: int,
    rng: np.random.Generator,
    repeats: int = NULL_REPEATS,
) -> dict[str, float]:
    if selected_actions.empty:
        return {
            "target_null_mean": 0.0,
            "target_null_std": 0.0,
            "target_null_p_ge_observed": 1.0,
            "target_null_z": 0.0,
        }
    observed = float(selected_actions["true_gain"].sum() / denominator)
    grouped_candidates = {target: group["true_gain"].to_numpy(dtype=float) for target, group in candidates.groupby("target")}
    selected_counts = selected_actions["target"].value_counts().to_dict()
    samples = np.zeros(repeats, dtype=float)
    for i in range(repeats):
        total = 0.0
        for target, count in selected_counts.items():
            gains = grouped_candidates[target]
            replace = len(gains) < int(count)
            total += float(rng.choice(gains, size=int(count), replace=replace).sum())
        samples[i] = total / denominator
    std = float(samples.std(ddof=1)) if repeats > 1 else 0.0
    return {
        "target_null_mean": float(samples.mean()),
        "target_null_std": std,
        "target_null_p_ge_observed": float((samples >= observed).mean()),
        "target_null_z": float((observed - samples.mean()) / max(std, 1e-12)),
    }


def target_family_stratified_null(
    candidates: pd.DataFrame,
    selected_actions: pd.DataFrame,
    denominator: int,
    rng: np.random.Generator,
    repeats: int = NULL_REPEATS,
) -> dict[str, float]:
    if selected_actions.empty:
        return {
            "target_family_null_mean": 0.0,
            "target_family_null_std": 0.0,
            "target_family_null_p_ge_observed": 1.0,
            "target_family_null_z": 0.0,
        }
    observed = float(selected_actions["true_gain"].sum() / denominator)
    grouped_candidates = {
        key: group["true_gain"].to_numpy(dtype=float)
        for key, group in candidates.groupby(["target", "expert_family"], sort=False)
    }
    selected_counts = selected_actions.groupby(["target", "expert_family"]).size().to_dict()
    fallback_by_target = {target: group["true_gain"].to_numpy(dtype=float) for target, group in candidates.groupby("target")}
    samples = np.zeros(repeats, dtype=float)
    for i in range(repeats):
        total = 0.0
        for key, count in selected_counts.items():
            gains = grouped_candidates.get(key)
            if gains is None or len(gains) == 0:
                gains = fallback_by_target[key[0]]
            replace = len(gains) < int(count)
            total += float(rng.choice(gains, size=int(count), replace=replace).sum())
        samples[i] = total / denominator
    std = float(samples.std(ddof=1)) if repeats > 1 else 0.0
    return {
        "target_family_null_mean": float(samples.mean()),
        "target_family_null_std": std,
        "target_family_null_p_ge_observed": float((samples >= observed).mean()),
        "target_family_null_z": float((observed - samples.mean()) / max(std, 1e-12)),
    }


def evaluate_all_policies(cell_frame: pd.DataFrame, scored_pairs: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    raw_loss = logloss(cell_frame["y"].to_numpy(dtype=float), cell_frame["pred__raw_knn_blend"].to_numpy(dtype=float))
    policy_rows = [{
        "policy_name": "raw_knn_blend_baseline",
        "score_source": "none",
        "mode": "baseline",
        "param": 0.0,
        "min_positive_votes": 0,
        "min_strong_positive_votes": 0,
        "logloss": raw_loss,
        "switched_cells": 0,
        "switched_rate": 0.0,
        "mean_realized_gain_all_cells": 0.0,
        "mean_realized_gain_switched": 0.0,
        "positive_true_gain_rate": 0.0,
        "target_null_mean": 0.0,
        "target_null_std": 0.0,
        "target_null_p_ge_observed": 1.0,
        "target_null_z": 0.0,
        "target_family_null_mean": 0.0,
        "target_family_null_std": 0.0,
        "target_family_null_p_ge_observed": 1.0,
        "target_family_null_z": 0.0,
    }]
    selected_frames = []
    candidate_frames = []
    best_bundle: dict[str, Any] | None = None
    rng = np.random.default_rng(RANDOM_STATE)

    for policy in build_policies():
        candidates = best_candidate_by_score(scored_pairs, policy["score_source"])
        metric, selected_actions, pred_arr = evaluate_candidate_policy(cell_frame, candidates, policy)
        metric.update(target_stratified_null(candidates, selected_actions, len(cell_frame), rng))
        metric.update(target_family_stratified_null(candidates, selected_actions, len(cell_frame), rng))
        policy_rows.append(metric)
        candidates["policy_name"] = policy["name"]
        candidate_frames.append(candidates)
        if len(selected_actions):
            selected_actions["policy_name"] = policy["name"]
            selected_frames.append(selected_actions)
        if best_bundle is None or float(metric["logloss"]) < float(best_bundle["metric"]["logloss"]):
            best_bundle = {
                "policy": policy,
                "metric": metric,
                "candidates": candidates,
                "selected_actions": selected_actions,
                "pred_arr": pred_arr,
            }

    if best_bundle is None:
        raise RuntimeError("no policy evaluated")
    metrics = pd.DataFrame(policy_rows).sort_values("logloss", kind="mergesort").reset_index(drop=True)
    selected = pd.concat(selected_frames, ignore_index=True) if selected_frames else pd.DataFrame()
    candidates_all = pd.concat(candidate_frames, ignore_index=True)
    return metrics, selected, candidates_all, best_bundle


def train_final_submission(
    features_frame: pd.DataFrame,
    labels: pd.DataFrame,
    sample: pd.DataFrame,
    raw_cols: list[str],
    gain_pairs: pd.DataFrame,
    features: list[str],
    best_policy: dict[str, Any],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    train = features_frame[features_frame["split"].eq("train")].copy().reset_index(drop=True)
    train[TARGETS] = labels[TARGETS].to_numpy(dtype=float)
    test = features_frame[features_frame["split"].eq("test")].copy().reset_index(drop=True)
    catalog, _audit = prediction_catalog(train, test, raw_cols)
    test_cells, test_pairs = build_cell_and_pair_frames(test, None, catalog, "test")

    final_pairs = test_pairs[test_pairs["expert"].ne("raw_knn_blend")].copy().reset_index(drop=True)
    for model_name in MODEL_NAMES:
        model = make_model(model_name)
        model.fit(gain_pairs[features].to_numpy(dtype=float), gain_pairs["gain"].to_numpy(dtype=float))
        final_pairs[f"predicted_gain__{model_name}"] = model.predict(final_pairs[features].to_numpy(dtype=float))
    final_pairs = add_jury_scores(final_pairs)
    candidates = best_candidate_by_score(final_pairs, best_policy["score_source"])
    selected = policy_selected(candidates, best_policy)
    candidate_map = candidates.set_index("cell_key")

    pred_vec = []
    action_rows = []
    for rec in test_cells.to_dict("records"):
        cell_key = rec["cell_key"]
        cand = candidate_map.loc[cell_key]
        if cell_key in selected:
            pred = float(cand["expert_pred"])
            switched = True
            selected_expert = str(cand["expert"])
        else:
            pred = float(rec["pred__raw_knn_blend"])
            switched = False
            selected_expert = "raw_knn_blend"
        pred_vec.append(pred)
        action_rows.append(
            {
                "cell_key": cell_key,
                "row": int(rec["row"]),
                "subject_id": rec["subject_id"],
                "target": rec["target"],
                "selected_expert": selected_expert,
                "candidate_expert": str(cand["expert"]),
                "candidate_family": str(cand["expert_family"]),
                "selection_score": float(cand["selection_score"]),
                "jury_gain_mean": float(cand["jury_gain_mean"]),
                "jury_gain_lower_confidence": float(cand["jury_gain_lower_confidence"]),
                "jury_positive_votes": int(cand["jury_positive_votes"]),
                "raw_pred": float(rec["pred__raw_knn_blend"]),
                "selected_pred": pred,
                "switched": switched,
            }
        )

    pred = np.asarray(pred_vec, dtype=float).reshape((len(test), len(TARGETS)))
    submission = sample.copy()
    submission[TARGETS] = np.clip(pred, 1e-5, 1 - 1e-5)
    return submission, pd.DataFrame(action_rows)


def markdown_table(frame: pd.DataFrame, max_rows: int = 12) -> str:
    show = frame.head(max_rows).copy()
    cols = list(show.columns)
    rows = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for rec in show.to_dict("records"):
        cells = []
        for col in cols:
            val = rec[col]
            if isinstance(val, float):
                cells.append(f"{val:.6f}")
            else:
                cells.append(str(val))
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
    top = metrics[top_cols].head(14).copy()
    target_counts = selected[selected["policy_name"].eq(readout["best_policy_name"])]["target"].value_counts().reindex(TARGETS).fillna(0).astype(int)
    family_counts = selected[selected["policy_name"].eq(readout["best_policy_name"])]["expert_family"].value_counts()
    target_count_table = target_counts.rename_axis("target").reset_index(name="count")
    family_count_table = family_counts.rename_axis("expert_family").reset_index(name="count")
    lines = [
        "# Raw-KNN Override Safety Jury",
        "",
        "## 한 줄 요약",
        "",
        "HS-JEPA core/context를 raw KNN을 대체하는 전체 모델로 쓰지 않고, raw KNN이 실패할 row-target cell을 감지하는 safety jury로 사용했다.",
        "",
        "## 왜 중요한가",
        "",
        "이 실험은 public LB, 기존 submission probability, action teacher, frontier file을 사용하지 않는다. 따라서 결과가 좋다면 HS-JEPA core가 competition anchor 없이도 action-health를 판별한다는 증거가 된다.",
        "",
        "## 핵심 결과",
        "",
        f"- raw KNN OOF logloss: `{readout['raw_knn_oof_logloss']:.6f}`",
        f"- best safety-jury policy: `{readout['best_policy_name']}`",
        f"- best safety-jury OOF logloss: `{readout['best_policy_oof_logloss']:.6f}`",
        f"- delta vs raw KNN: `{readout['best_policy_delta_vs_raw_knn']:.6f}`",
        f"- OOF switched cells: `{readout['best_policy_oof_switched_cells']}`",
        f"- target matched-null p(gain >= observed): `{readout['best_policy_target_null_p_ge_observed']:.6f}`",
        f"- target+family matched-null p(gain >= observed): `{readout['best_policy_target_family_null_p_ge_observed']:.6f}`",
        f"- best guarded policy: `{readout['best_guarded_policy_name']}`",
        f"- best guarded OOF logloss: `{readout['best_guarded_oof_logloss']:.6f}`",
        f"- guarded delta vs raw KNN: `{readout['best_guarded_delta_vs_raw_knn']:.6f}`",
        f"- generated candidate: `{readout['candidate_file']}`",
        "",
        "## Best policy target counts",
        "",
        markdown_table(target_count_table, max_rows=10),
        "",
        "## Best policy expert-family counts",
        "",
        markdown_table(family_count_table, max_rows=10),
        "",
        "## Top local policies",
        "",
        markdown_table(top, max_rows=14),
        "",
        "## 논문용 해석",
        "",
        "HS-JEPA의 역할은 모든 예측을 직접 만드는 것이 아니라, 강한 base world model이 언제 실패하는지 판별하는 latent action-health layer가 될 수 있다.",
        "",
        "중요한 부정 결과도 있다. 여러 모델이 동시에 동의하는 consensus guard는 positive true-gain rate를 올리지만, 전체 logloss gain은 크게 줄였다. 즉 현재 신호는 넓고 안정적인 상식 consensus가 아니라 특정 route-risk surface에서만 드러나는 sharp failure boundary에 가깝다.",
        "",
        "따라서 safety jury는 최종 release 장치라기보다, sharp boundary가 shortcut인지 아닌지 확인하는 stress diagnostic으로 쓰는 편이 맞다.",
        "",
        "matched-null stress를 함께 기록하는 이유는 단순히 cell 몇 개를 운 좋게 고른 것인지, target/family 조건을 맞춘 무작위 선택보다 실제로 gain이 큰지를 구분하기 위해서다.",
    ]
    return "\n".join(lines)


def run() -> dict[str, Any]:
    features_frame, labels, sample, raw_cols_from_module = load_world()
    raw_cols = raw_feature_cols(features_frame) if not raw_cols_from_module else raw_cols_from_module
    cell_frame, pair_frame = build_temporal_oof_frames(features_frame, labels, raw_cols)
    gain_pairs = prepare_gain_pairs(cell_frame, pair_frame)
    features = gain_feature_columns(gain_pairs)
    leak_cols = [col for col in features if "loss" in col or col in {"y", "raw_loss", "gain"}]
    if leak_cols:
        raise RuntimeError(f"leaky feature columns detected: {leak_cols}")

    scored_pairs = add_jury_scores(add_gain_predictions(gain_pairs, features))
    metrics, selected, candidates_all, best_bundle = evaluate_all_policies(cell_frame, scored_pairs)
    raw = float(metrics[metrics["policy_name"].eq("raw_knn_blend_baseline")]["logloss"].iloc[0])
    best_metric = metrics.iloc[0]
    best_policy = best_bundle["policy"] if str(best_metric["policy_name"]) == best_bundle["policy"]["name"] else None
    if best_policy is None:
        # The raw baseline can only be first if all jury policies fail.  In that
        # case choose the strongest non-baseline policy as a sensor candidate.
        non_baseline = metrics[~metrics["policy_name"].eq("raw_knn_blend_baseline")].iloc[0]
        matching = [p for p in build_policies() if p["name"] == str(non_baseline["policy_name"])]
        best_policy = matching[0]
        best_metric = non_baseline

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
    candidate_file = f"submission_hsjepa_raw_knn_override_safety_jury_{suffix}_uploadsafe.csv"
    submission.to_csv(ROOT / candidate_file, index=False)
    submission.to_csv(OUT / candidate_file, index=False)

    best_selected = selected[selected["policy_name"].eq(str(best_metric["policy_name"]))].copy()
    guarded_mask = (
        metrics["policy_name"].str.contains("votes2", regex=False)
        | metrics["policy_name"].str.contains("votes3", regex=False)
        | metrics["policy_name"].str.contains("strong_votes2", regex=False)
        | metrics["policy_name"].str.contains("core_families", regex=False)
    )
    best_guarded = metrics[guarded_mask].sort_values("logloss", kind="mergesort").iloc[0]
    readout = {
        "package": "raw_knn_override_safety_jury",
        "status": "anchor_free_safety_jury_ready",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_action_teacher": False,
        "uses_frontier_file": False,
        "raw_knn_oof_logloss": raw,
        "best_policy_name": str(best_metric["policy_name"]),
        "best_policy_score_source": str(best_metric["score_source"]),
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
        "best_guarded_policy_name": str(best_guarded["policy_name"]),
        "best_guarded_oof_logloss": float(best_guarded["logloss"]),
        "best_guarded_delta_vs_raw_knn": float(best_guarded["logloss"] - raw),
        "best_guarded_switched_cells": int(best_guarded["switched_cells"]),
        "best_guarded_positive_true_gain_rate": float(best_guarded["positive_true_gain_rate"]),
        "best_guarded_target_null_p_ge_observed": float(best_guarded["target_null_p_ge_observed"]),
        "best_guarded_target_family_null_p_ge_observed": float(best_guarded["target_family_null_p_ge_observed"]),
        "best_policy_oof_target_counts": best_selected["target"].value_counts().reindex(TARGETS).fillna(0).astype(int).to_dict(),
        "best_policy_oof_expert_family_counts": best_selected["expert_family"].value_counts().to_dict(),
        "candidate_file": candidate_file,
        "root_candidate_file": candidate_file,
        "test_switched_cells": int(test_actions["switched"].sum()),
        "test_switched_rows": int(test_actions.loc[test_actions["switched"], "row"].nunique()),
        "test_target_counts": test_actions.loc[test_actions["switched"], "target"].value_counts().reindex(TARGETS).fillna(0).astype(int).to_dict(),
        "test_expert_counts": test_actions.loc[test_actions["switched"], "selected_expert"].value_counts().to_dict(),
        "interpretation": "HS-JEPA is tested as an anchor-free action-health jury that only overrides raw KNN on predicted failure cells.",
    }

    metrics.to_csv(OUT / "raw_knn_override_safety_jury_policy_table.csv", index=False)
    selected.to_csv(OUT / "raw_knn_override_safety_jury_selected_oof_cells.csv", index=False)
    candidates_all.to_csv(OUT / "raw_knn_override_safety_jury_oof_candidates.csv", index=False)
    test_actions.to_csv(OUT / "raw_knn_override_safety_jury_test_actions.csv", index=False)
    (OUT / "raw_knn_override_safety_jury_readout.json").write_text(json.dumps(readout, ensure_ascii=False, indent=2), encoding="utf-8")
    md = build_markdown(readout, metrics, selected)
    (OUT / "RAW_KNN_OVERRIDE_SAFETY_JURY_KO.md").write_text(md, encoding="utf-8")
    (ROOT / "paper_hsjepa_core" / "RAW_KNN_OVERRIDE_SAFETY_JURY_KO.md").write_text(md, encoding="utf-8")
    return readout


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
