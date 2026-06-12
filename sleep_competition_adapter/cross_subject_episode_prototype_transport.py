#!/usr/bin/env python3
"""Cross-subject episode prototype transport for HS-JEPA.

This is a deliberately larger bet than tuning a release policy.  The previous
episode controller improved full OOF but failed subject-invariant stress: the
best actions were concentrated in a small subject tail.  This experiment asks a
different question:

    Can successful episode-action prototypes from other subjects be transported
    to a held-out subject with similar human-state context?

The action score is learned by subject-held-out kNN over HS-JEPA context:
route disagreement, human-state context, and row episode representation.  The
release decoder is therefore not allowed to use the held-out subject's labels
when scoring that subject's row-target actions.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sleep_competition_adapter.contextual_listener_route_selector import build_temporal_oof_frames  # noqa: E402
from sleep_competition_adapter.core_oof_action_health_benchmark import (  # noqa: E402
    TARGETS,
    load_world,
    logloss,
    raw_feature_cols,
    short_hash,
    validate_submission,
)
from sleep_competition_adapter.episode_action_space_restriction_decoder import (  # noqa: E402
    build_test_pairs,
)
from sleep_competition_adapter.episode_selective_assignment_decoder import (  # noqa: E402
    attach_episode_features,
    build_oof_episode_state,
)
from sleep_competition_adapter.failure_boundary_law_distillation import (  # noqa: E402
    add_law_features,
    best_candidate_per_cell,
    feature_views as law_feature_views,
    policy_selected,
)
from sleep_competition_adapter.raw_knn_failure_detector import prepare_gain_pairs  # noqa: E402


OUT = ROOT / "sleep_competition_adapter" / "outputs" / "cross_subject_episode_prototype_transport"
OUT.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = 20260612
NEIGHBORS = [7, 13, 21, 35, 55]
WEIGHTS = ["uniform", "distance"]
GROUP_MODES = ["all", "target", "expert_family", "target_expert_family", "target_episode_family"]
TOP_FRACS = [0.01, 0.02, 0.03, 0.04, 0.06, 0.08, 0.10, 0.15, 0.20]
THRESHOLDS = [-0.02, -0.01, 0.0, 0.005, 0.01, 0.02, 0.04, 0.08]


def numeric_episode_columns(frame: pd.DataFrame) -> list[str]:
    cols = [
        col
        for col in frame.columns
        if (
            col.startswith("row_episode_")
            or col in {"expert_matches_row_episode_route", "family_matches_row_episode"}
        )
        and pd.api.types.is_numeric_dtype(frame[col])
    ]
    return cols


def feature_views(frame: pd.DataFrame) -> dict[str, list[str]]:
    base = law_feature_views(frame)
    episode = numeric_episode_columns(frame)
    views = {
        "route_episode_context": list(dict.fromkeys(base["route_disagreement_law"] + episode)),
        "human_episode_context": list(dict.fromkeys(base["human_state_law"] + episode)),
        "compact_episode_context": list(dict.fromkeys(base["compact_hsjepa_law"] + episode)),
    }
    for name, cols in views.items():
        leak_cols = [col for col in cols if "loss" in col or "gain" in col or col in {"y", "raw_loss"}]
        if leak_cols:
            raise RuntimeError(f"leaky prototype feature columns in {name}: {leak_cols}")
    return views


def group_columns(mode: str) -> list[str]:
    if mode == "all":
        return []
    if mode == "target":
        return ["target"]
    if mode == "expert_family":
        return ["expert_family"]
    if mode == "target_expert_family":
        return ["target", "expert_family"]
    if mode == "target_episode_family":
        return ["target", "row_episode_route_cell_family"]
    raise KeyError(mode)


def fit_knn(train: pd.DataFrame, features: list[str], k: int, weights: str):
    return make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(),
        KNeighborsRegressor(
            n_neighbors=max(1, min(int(k), len(train))),
            weights=weights,
            metric="minkowski",
        ),
    ).fit(train[features], train["gain"].to_numpy(dtype=float))


def predict_grouped_knn(
    train: pd.DataFrame,
    valid: pd.DataFrame,
    features: list[str],
    k: int,
    weights: str,
    mode: str,
) -> np.ndarray:
    pred = np.zeros(len(valid), dtype=float)
    key_cols = group_columns(mode)
    if not key_cols:
        model = fit_knn(train, features, k, weights)
        return np.asarray(model.predict(valid[features]), dtype=float)

    fallback = fit_knn(train, features, k, weights)
    valid_pos = pd.Series(np.arange(len(valid)), index=valid.index)
    for _, valid_group in valid.groupby(key_cols, dropna=False, sort=False):
        mask = np.ones(len(train), dtype=bool)
        for col in key_cols:
            mask &= train[col].astype(str).to_numpy() == str(valid_group[col].iloc[0])
        train_group = train[mask]
        if len(train_group) >= max(4, min(k, 8)):
            model = fit_knn(train_group, features, k, weights)
        else:
            model = fallback
        idx = valid_pos.loc[valid_group.index].to_numpy()
        pred[idx] = np.asarray(model.predict(valid_group[features]), dtype=float)
    return pred


def predict_oof_transport(frame: pd.DataFrame, features: list[str], k: int, weights: str, mode: str) -> np.ndarray:
    pred = np.full(len(frame), np.nan, dtype=float)
    for subject in sorted(frame["subject_id"].unique()):
        train = frame[~frame["subject_id"].eq(subject)].copy()
        valid = frame[frame["subject_id"].eq(subject)].copy()
        pred[valid.index.to_numpy()] = predict_grouped_knn(train, valid, features, k, weights, mode)
    if np.isnan(pred).any():
        raise RuntimeError("cross-subject prototype OOF score contains NaN")
    return pred


def predict_test_transport(train: pd.DataFrame, test: pd.DataFrame, features: list[str], k: int, weights: str, mode: str) -> np.ndarray:
    return predict_grouped_knn(train, test, features, k, weights, mode)


def evaluate_policy(cell_frame: pd.DataFrame, candidates: pd.DataFrame, policy: str, param: float) -> tuple[dict[str, Any], pd.DataFrame]:
    selected = policy_selected(candidates, policy, param)
    candidate_map = candidates.set_index("cell_key")
    pred = []
    gains = []
    actions = []
    for rec in cell_frame.to_dict("records"):
        cell_key = rec["cell_key"]
        if cell_key in selected:
            cand = candidate_map.loc[cell_key]
            gain = float(cand["true_gain"])
            pred.append(float(cand["expert_pred"]))
            gains.append(gain)
            actions.append({
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
            })
        else:
            pred.append(float(rec["pred__raw_knn_blend"]))
            gains.append(0.0)
    y = cell_frame["y"].to_numpy(dtype=float)
    actions_df = pd.DataFrame(actions)
    metric = {
        "policy": policy,
        "param": float(param),
        "logloss": logloss(y, np.asarray(pred, dtype=float)),
        "switched_cells": int(len(selected)),
        "mean_realized_gain_all_cells": float(np.sum(gains) / len(cell_frame)),
        "mean_realized_gain_switched": float(actions_df["true_gain"].mean()) if len(actions_df) else 0.0,
        "positive_true_gain_rate": float((actions_df["true_gain"] > 0).mean()) if len(actions_df) else 0.0,
    }
    return metric, actions_df


def add_action_health(metric: dict[str, Any], actions: pd.DataFrame, cell_frame: pd.DataFrame) -> dict[str, Any]:
    subjects = cell_frame[["subject_id"]].drop_duplicates()["subject_id"].tolist()
    if actions.empty:
        metric.update({
            "active_subjects": 0,
            "positive_active_subjects": 0,
            "negative_active_subjects": 0,
            "active_subject_rate": 0.0,
            "std_subject_gain_per_cell": 0.0,
            "min_active_gain_per_cell": 0.0,
            "robust_transport_score": 0.0,
        })
        return metric
    subject_cells = cell_frame.groupby("subject_id")["cell_key"].nunique()
    subject_gain = actions.groupby("subject_id")["true_gain"].sum()
    active = subject_gain.index.tolist()
    gain_per_cell = pd.Series(0.0, index=subjects)
    for subject, value in subject_gain.items():
        gain_per_cell.loc[subject] = float(value) / float(subject_cells.loc[subject])
    active_gain_per_cell = gain_per_cell.loc[active]
    negative_active_subjects = int((active_gain_per_cell < 0).sum())
    metric.update({
        "active_subjects": int(len(active)),
        "positive_active_subjects": int((active_gain_per_cell > 0).sum()),
        "negative_active_subjects": negative_active_subjects,
        "active_subject_rate": float(len(active) / len(subjects)),
        "std_subject_gain_per_cell": float(gain_per_cell.std(ddof=0)),
        "min_active_gain_per_cell": float(active_gain_per_cell.min()) if len(active_gain_per_cell) else 0.0,
    })
    metric["robust_transport_score"] = (
        float(metric["mean_realized_gain_all_cells"])
        - 0.15 * float(metric["std_subject_gain_per_cell"])
        - 0.0015 * float(metric["negative_active_subjects"])
        + 0.0010 * float(metric["active_subject_rate"])
    )
    return metric


def build_oof_context() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, list[str], pd.DataFrame, dict[str, Any]]:
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
    return features_frame, labels, sample, gain_pairs, raw_cols, row_pair_frame, row_meta


def evaluate_transport(cell_frame: pd.DataFrame, gain_pairs: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    views = feature_views(gain_pairs)
    raw = logloss(cell_frame["y"].to_numpy(dtype=float), cell_frame["pred__raw_knn_blend"].to_numpy(dtype=float))
    metrics = [{
        "law_name": "raw_knn_blend_baseline",
        "feature_view": "none",
        "group_mode": "none",
        "neighbors": 0,
        "weights": "none",
        "policy": "baseline",
        "param": 0.0,
        "logloss": raw,
        "switched_cells": 0,
        "mean_realized_gain_all_cells": 0.0,
        "mean_realized_gain_switched": 0.0,
        "positive_true_gain_rate": 0.0,
        "active_subjects": 0,
        "positive_active_subjects": 0,
        "negative_active_subjects": 0,
        "active_subject_rate": 0.0,
        "std_subject_gain_per_cell": 0.0,
        "min_active_gain_per_cell": 0.0,
        "robust_transport_score": 0.0,
    }]
    all_candidates = []
    all_actions = []
    best_by_logloss: dict[str, Any] | None = None
    best_by_robust: dict[str, Any] | None = None
    for view_name, cols in views.items():
        for mode in GROUP_MODES:
            for k in NEIGHBORS:
                for weights in WEIGHTS:
                    law_name = f"{view_name}__{mode}__knn{k}_{weights}"
                    score_col = f"pred__{law_name}"
                    scored_pairs = gain_pairs.copy()
                    scored_pairs[score_col] = predict_oof_transport(gain_pairs, cols, k, weights, mode)
                    candidates = best_candidate_per_cell(scored_pairs, score_col, law_name, view_name)
                    candidates["law_name"] = law_name
                    candidates["group_mode"] = mode
                    candidates["neighbors"] = k
                    candidates["weights"] = weights
                    all_candidates.append(candidates)
                    for frac in TOP_FRACS:
                        metric, actions = evaluate_policy(cell_frame, candidates, "topfrac", frac)
                        metric.update({
                            "law_name": law_name,
                            "feature_view": view_name,
                            "group_mode": mode,
                            "neighbors": int(k),
                            "weights": weights,
                        })
                        metric = add_action_health(metric, actions, cell_frame)
                        metrics.append(metric)
                        if len(actions):
                            actions["law_name"] = law_name
                            actions["feature_view"] = view_name
                            actions["group_mode"] = mode
                            actions["neighbors"] = int(k)
                            actions["weights"] = weights
                            actions["policy"] = "topfrac"
                            actions["param"] = float(frac)
                            all_actions.append(actions)
                        rec = {"metric": metric, "candidates": candidates, "actions": actions, "features": cols}
                        if best_by_logloss is None or metric["logloss"] < best_by_logloss["metric"]["logloss"]:
                            best_by_logloss = rec
                        if (
                            metric["switched_cells"] >= 10
                            and metric["active_subjects"] >= 3
                            and (best_by_robust is None or metric["robust_transport_score"] > best_by_robust["metric"]["robust_transport_score"])
                        ):
                            best_by_robust = rec
                    for threshold in THRESHOLDS:
                        metric, actions = evaluate_policy(cell_frame, candidates, "threshold", threshold)
                        metric.update({
                            "law_name": law_name,
                            "feature_view": view_name,
                            "group_mode": mode,
                            "neighbors": int(k),
                            "weights": weights,
                        })
                        metric = add_action_health(metric, actions, cell_frame)
                        metrics.append(metric)
                        if len(actions):
                            actions["law_name"] = law_name
                            actions["feature_view"] = view_name
                            actions["group_mode"] = mode
                            actions["neighbors"] = int(k)
                            actions["weights"] = weights
                            actions["policy"] = "threshold"
                            actions["param"] = float(threshold)
                            all_actions.append(actions)
                        rec = {"metric": metric, "candidates": candidates, "actions": actions, "features": cols}
                        if best_by_logloss is None or metric["logloss"] < best_by_logloss["metric"]["logloss"]:
                            best_by_logloss = rec
                        if (
                            metric["switched_cells"] >= 10
                            and metric["active_subjects"] >= 3
                            and (best_by_robust is None or metric["robust_transport_score"] > best_by_robust["metric"]["robust_transport_score"])
                        ):
                            best_by_robust = rec
    if best_by_logloss is None:
        raise RuntimeError("no transport policies evaluated")
    if best_by_robust is None:
        best_by_robust = best_by_logloss
    metrics_df = pd.DataFrame(metrics).sort_values("logloss", kind="mergesort").reset_index(drop=True)
    candidates_df = pd.concat(all_candidates, ignore_index=True) if all_candidates else pd.DataFrame()
    actions_df = pd.concat(all_actions, ignore_index=True) if all_actions else pd.DataFrame()
    return metrics_df, candidates_df, actions_df, {"best_by_logloss": best_by_logloss, "best_by_robust": best_by_robust}


def make_submission(
    features_frame: pd.DataFrame,
    labels: pd.DataFrame,
    sample: pd.DataFrame,
    raw_cols: list[str],
    train_gain_pairs: pd.DataFrame,
    row_pair_frame: pd.DataFrame,
    row_meta: dict[str, Any],
    release: dict[str, Any],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    test_cells, test_pairs, _test_episode = build_test_pairs(features_frame, labels, raw_cols, row_pair_frame, row_meta)
    cols = release["features"]
    score_col = "predicted_cross_subject_transport_gain"
    test_pairs[score_col] = predict_test_transport(
        train_gain_pairs,
        test_pairs,
        cols,
        int(release["metric"]["neighbors"]),
        str(release["metric"]["weights"]),
        str(release["metric"]["group_mode"]),
    )
    candidates = best_candidate_per_cell(test_pairs, score_col, str(release["metric"]["law_name"]), str(release["metric"]["feature_view"]))
    selected = policy_selected(candidates, str(release["metric"]["policy"]), float(release["metric"]["param"]))
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
        actions.append({
            "cell_key": cell_key,
            "row": int(rec["row"]),
            "subject_id": rec["subject_id"],
            "target": rec["target"],
            "selected_expert": expert,
            "candidate_expert": str(cand["expert"]),
            "candidate_family": str(cand["expert_family"]),
            "selection_score": float(cand["selection_score"]),
            "raw_pred": float(rec["pred__raw_knn_blend"]),
            "selected_pred": pred,
            "switched": switched,
        })
    pred = np.asarray(pred_vec, dtype=float).reshape((len(sample), len(TARGETS)))
    submission = sample.copy()
    submission[TARGETS] = np.clip(pred, 1e-5, 1 - 1e-5)
    return submission, pd.DataFrame(actions)


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


def build_markdown(readout: dict[str, Any], metrics: pd.DataFrame, test_actions: pd.DataFrame) -> str:
    top_cols = [
        "law_name",
        "policy",
        "param",
        "logloss",
        "switched_cells",
        "mean_realized_gain_all_cells",
        "active_subjects",
        "negative_active_subjects",
        "robust_transport_score",
    ]
    robust_cols = top_cols
    target_counts = (
        test_actions[test_actions["switched"]]["target"]
        .value_counts()
        .reindex(TARGETS)
        .fillna(0)
        .astype(int)
        .rename_axis("target")
        .reset_index(name="count")
    )
    lines = [
        "# Cross-Subject Episode Prototype Transport",
        "",
        "## 한 줄 요약",
        "",
        "다른 subject에서 성공한 episode-action prototype을 held-out subject의 비슷한 row-target-route로 전이할 수 있는지 검증했다.",
        "",
        "## 재현 명령",
        "",
        "```bash",
        "python3 sleep_competition_adapter/cross_subject_episode_prototype_transport.py",
        "```",
        "",
        "public LB, 기존 submission probability, action teacher, frontier file은 사용하지 않는다.",
        "",
        "## 왜 이것이 HS-JEPA인가",
        "",
        "이 실험의 핵심은 kNN 자체가 아니다. kNN은 JEPA predictor를 non-parametric하게 구현한 한 가지 방식일 뿐이다.",
        "",
        "| JEPA 구성요소 | 이 실험에서의 의미 |",
        "| --- | --- |",
        "| context | 현재 row의 lifelog 상태, target route, expert route, row episode state |",
        "| target representation | 다른 subject에서 실제로 성공했던 hidden episode-action prototype |",
        "| predictor | 현재 context embedding에서 가까운 성공 action representation을 검색/예측하는 cross-subject prototype transport |",
        "| energy / decoder | 예측된 target representation과 가까운 action만 row-target correction으로 release |",
        "| LeJEPA-style health check | active subject coverage, negative active subject count, robust transport score로 shortcut/collapse를 검사 |",
        "",
        "따라서 이 실험은 label을 직접 맞히는 모델이 아니라, 보이는 human context에서 보이지 않는 action representation을 예측하는 HS-JEPA adapter다.",
        "",
        "## Architecture Contract",
        "",
        "```text",
        "visible human-state context",
        "  -> row/target/route joint embedding",
        "  -> predict hidden episode-action representation from peer subjects",
        "  -> score action-health energy",
        "  -> release sparse row-target correction only when transport is healthy",
        "```",
        "",
        "## 핵심 결과",
        "",
        f"- raw OOF logloss: `{readout['raw_oof_logloss']:.6f}`",
        f"- best transport OOF logloss: `{readout['best_oof_logloss']:.6f}`",
        f"- best transport delta vs raw: `{readout['best_delta_vs_raw']:.6f}`",
        f"- robust release law: `{readout['release_law_name']}`",
        f"- robust release OOF logloss: `{readout['release_oof_logloss']:.6f}`",
        f"- robust release active subjects: `{readout['release_active_subjects']}`",
        f"- robust release negative active subjects: `{readout['release_negative_active_subjects']}`",
        f"- candidate: `{readout['candidate_file']}`",
        f"- verdict: `{readout['verdict']}`",
        "",
        "## Best by OOF logloss",
        "",
        markdown_table(metrics[top_cols], max_rows=16),
        "",
        "## Best by robust transport score",
        "",
        markdown_table(metrics.sort_values("robust_transport_score", ascending=False, kind="mergesort")[robust_cols], max_rows=16),
        "",
        "## Release test switched target counts",
        "",
        markdown_table(target_counts, max_rows=10),
        "",
        "## 논문용 해석",
        "",
        "이 실험은 HS-JEPA를 개인의 과거 label memory가 아니라 cross-subject target-representation prediction으로 해석한다.",
        "여기서 target representation은 raw label이 아니라, peer subject에서 성공한 episode-action prototype이다.",
        "성공하면 human-state latent가 subject identity를 넘어 전이 가능한 action geometry를 가진다는 증거가 된다.",
        "실패하면 현재 episode latent는 local diagnostic으로는 유효하지만, peer subject로 전이 가능한 일반 representation은 아직 아니라는 결론이다.",
    ]
    return "\n".join(lines)


def write_compact_action_summaries(candidates: pd.DataFrame, actions: pd.DataFrame) -> None:
    id_cols = ["law_name", "feature_view", "group_mode", "neighbors", "weights"]
    if len(candidates):
        candidate_summary = candidates.groupby(id_cols).agg(
            candidate_cells=("cell_key", "nunique"),
            mean_selection_score=("selection_score", "mean"),
            max_selection_score=("selection_score", "max"),
        ).reset_index()
        candidate_summary.to_csv(OUT / "cross_subject_episode_prototype_transport_candidate_summary.csv", index=False)
    if len(actions):
        action_summary = actions.groupby(id_cols + ["policy", "param"]).agg(
            switched_cells=("cell_key", "nunique"),
            active_subjects=("subject_id", "nunique"),
            mean_true_gain=("true_gain", "mean"),
            gain_sum=("true_gain", "sum"),
            positive_true_gain_rate=("true_gain", lambda s: float((s > 0).mean())),
        ).reset_index()
        action_summary.to_csv(OUT / "cross_subject_episode_prototype_transport_oof_action_summary.csv", index=False)


def run() -> dict[str, Any]:
    features_frame, labels, sample, gain_pairs, raw_cols, row_pair_frame, row_meta = build_oof_context()
    cell_frame = gain_pairs[[
        "cell_key",
        "fold",
        "row",
        "subject_id",
        "target",
        "y",
        "raw_pred",
        "raw_loss",
    ]].drop_duplicates("cell_key").rename(columns={"raw_pred": "pred__raw_knn_blend"}).copy()
    metrics, candidates, actions, best = evaluate_transport(cell_frame, gain_pairs)
    raw_logloss = float(metrics[metrics["law_name"].eq("raw_knn_blend_baseline")]["logloss"].iloc[0])
    release = best["best_by_robust"]
    if release["metric"]["logloss"] > raw_logloss and best["best_by_logloss"]["metric"]["logloss"] < raw_logloss:
        release = best["best_by_logloss"]
    submission, test_actions = make_submission(
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
    candidate_file = f"submission_hsjepa_cross_subject_episode_prototype_transport_{suffix}_uploadsafe.csv"
    submission.to_csv(ROOT / candidate_file, index=False)
    submission.to_csv(OUT / candidate_file, index=False)
    test_actions.to_csv(OUT / "cross_subject_episode_prototype_transport_test_actions.csv", index=False)
    metrics.to_csv(OUT / "cross_subject_episode_prototype_transport_metrics.csv", index=False)
    write_compact_action_summaries(candidates, actions)
    best_metric = metrics.iloc[0].to_dict()
    release_metric = release["metric"]
    if float(best_metric["logloss"]) < raw_logloss - 0.003 and int(best_metric["active_subjects"]) >= 3:
        verdict = "cross_subject_transport_positive"
    elif float(best_metric["logloss"]) < raw_logloss:
        verdict = "cross_subject_transport_local_positive_but_needs_stress"
    else:
        verdict = "cross_subject_transport_failed"
    readout = {
        "package": "cross_subject_episode_prototype_transport",
        "status": "cross_subject_transport_ready",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_action_teacher": False,
        "uses_frontier_file": False,
        "raw_oof_logloss": raw_logloss,
        "best_law_name": str(best_metric["law_name"]),
        "best_oof_logloss": float(best_metric["logloss"]),
        "best_delta_vs_raw": float(best_metric["logloss"] - raw_logloss),
        "best_active_subjects": int(best_metric["active_subjects"]),
        "best_negative_active_subjects": int(best_metric["negative_active_subjects"]),
        "release_law_name": str(release_metric["law_name"]),
        "release_policy": str(release_metric["policy"]),
        "release_param": float(release_metric["param"]),
        "release_oof_logloss": float(release_metric["logloss"]),
        "release_delta_vs_raw": float(release_metric["logloss"] - raw_logloss),
        "release_active_subjects": int(release_metric["active_subjects"]),
        "release_negative_active_subjects": int(release_metric["negative_active_subjects"]),
        "release_robust_transport_score": float(release_metric["robust_transport_score"]),
        "release_test_switched_cells": int(test_actions["switched"].sum()),
        "candidate_file": candidate_file,
        "verdict": verdict,
    }
    (OUT / "cross_subject_episode_prototype_transport_readout.json").write_text(
        json.dumps(readout, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    md = build_markdown(readout, metrics, test_actions)
    (OUT / "CROSS_SUBJECT_EPISODE_PROTOTYPE_TRANSPORT_KO.md").write_text(md + "\n", encoding="utf-8")
    (ROOT / "paper_hsjepa_core" / "CROSS_SUBJECT_EPISODE_PROTOTYPE_TRANSPORT_KO.md").write_text(md + "\n", encoding="utf-8")
    return readout


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
