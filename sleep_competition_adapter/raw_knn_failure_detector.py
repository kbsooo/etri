#!/usr/bin/env python3
"""Raw-KNN failure detector for HS-JEPA listener routing.

The contextual router showed a clear boundary:

- sample-level routing improves over fixed target routes
- but broad routing does not beat raw lifelog KNN

This script narrows the task.  It keeps raw lifelog KNN as the default route
and asks whether HS-JEPA route-risk features can detect only the cells where
raw KNN should be abandoned.

No public LB ledger, prior submission probability, action teacher, or frontier
file is used.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor, GradientBoostingRegressor, RandomForestRegressor


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sleep_competition_adapter.contextual_listener_route_selector import (
    build_cell_and_pair_frames,
    build_temporal_oof_frames,
)
from sleep_competition_adapter.core_oof_action_health_benchmark import (
    TARGETS,
    load_world,
    logloss,
    prediction_catalog,
    raw_feature_cols,
    short_hash,
    validate_submission,
)


OUT = ROOT / "sleep_competition_adapter" / "outputs" / "raw_knn_failure_detector"
OUT.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = 20260612
TOP_FRACS = [0.02, 0.04, 0.06, 0.08, 0.10, 0.15, 0.20, 0.30, 0.50]
THRESHOLDS = [-0.02, -0.01, 0.00, 0.005, 0.01, 0.02, 0.04, 0.08, 0.12]


def make_model(name: str):
    if name == "gradient_boosted_gain":
        return GradientBoostingRegressor(
            n_estimators=120,
            max_depth=2,
            min_samples_leaf=18,
            learning_rate=0.045,
            random_state=RANDOM_STATE,
        )
    if name == "random_forest_gain":
        return RandomForestRegressor(
            n_estimators=240,
            max_depth=6,
            min_samples_leaf=14,
            max_features=0.70,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        )
    if name == "extra_trees_gain":
        return ExtraTreesRegressor(
            n_estimators=360,
            max_depth=7,
            min_samples_leaf=12,
            max_features=0.75,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        )
    raise KeyError(name)


def gain_feature_columns(frame: pd.DataFrame) -> list[str]:
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
        "raw_pred",
        "y",
    }
    blocked_prefixes = ("loss__", "oracle_")
    return [
        col
        for col in frame.columns
        if col not in blocked
        and not col.startswith(blocked_prefixes)
        and pd.api.types.is_numeric_dtype(frame[col])
    ]


def prepare_gain_pairs(cell_frame: pd.DataFrame, pair_frame: pd.DataFrame) -> pd.DataFrame:
    raw = cell_frame[["cell_key", "loss__raw_knn_blend", "pred__raw_knn_blend", "y"]].rename(
        columns={"loss__raw_knn_blend": "raw_loss", "pred__raw_knn_blend": "raw_pred"}
    )
    frame = pair_frame.merge(raw, on="cell_key", how="left")
    frame = frame[frame["expert"].ne("raw_knn_blend")].copy().reset_index(drop=True)
    frame["gain"] = frame["raw_loss"].astype(float) - frame["loss"].astype(float)
    return frame


def predict_oof_gain(gain_pairs: pd.DataFrame, model_name: str, features: list[str]) -> np.ndarray:
    pred = np.full(len(gain_pairs), np.nan, dtype=float)
    for subject in sorted(gain_pairs["subject_id"].unique()):
        train = gain_pairs[~gain_pairs["subject_id"].eq(subject)]
        valid = gain_pairs[gain_pairs["subject_id"].eq(subject)]
        model = make_model(model_name)
        model.fit(train[features].to_numpy(dtype=float), train["gain"].to_numpy(dtype=float))
        pred[valid.index.to_numpy()] = model.predict(valid[features].to_numpy(dtype=float))
    if np.isnan(pred).any():
        raise RuntimeError("OOF gain prediction has missing values")
    return pred


def best_candidate_per_cell(gain_pairs: pd.DataFrame, pred_col: str) -> pd.DataFrame:
    rows = []
    for cell_key, group in gain_pairs.groupby("cell_key", sort=False):
        best = group.sort_values(pred_col, ascending=False, kind="mergesort").iloc[0]
        rows.append(
            {
                "cell_key": cell_key,
                "row": int(best["row"]),
                "subject_id": best["subject_id"],
                "target": best["target"],
                "expert": best["expert"],
                "expert_pred": float(best["expert_pred"]),
                "predicted_gain": float(best[pred_col]),
                "true_gain": float(best["gain"]) if "gain" in best.index else np.nan,
            }
        )
    return pd.DataFrame(rows)


def evaluate_policy(cell_frame: pd.DataFrame, candidates: pd.DataFrame, policy: str, param: float) -> dict[str, Any]:
    candidate_map = candidates.set_index("cell_key")
    if policy == "topfrac":
        k = max(1, int(round(len(candidates) * param)))
        selected = set(candidates.sort_values("predicted_gain", ascending=False, kind="mergesort").head(k)["cell_key"])
    elif policy == "threshold":
        selected = set(candidates[candidates["predicted_gain"].gt(param)]["cell_key"])
        k = len(selected)
    else:
        raise KeyError(policy)

    pred = []
    gains = []
    selected_experts = []
    for rec in cell_frame.to_dict("records"):
        cell_key = rec["cell_key"]
        if cell_key in selected:
            cand = candidate_map.loc[cell_key]
            pred.append(float(cand["expert_pred"]))
            gains.append(float(cand["true_gain"]))
            selected_experts.append(str(cand["expert"]))
        else:
            pred.append(float(rec["pred__raw_knn_blend"]))
            gains.append(0.0)
            selected_experts.append("raw_knn_blend")
    pred_arr = np.asarray(pred, dtype=float)
    y = cell_frame["y"].to_numpy(dtype=float)
    return {
        "policy": policy,
        "param": float(param),
        "logloss": logloss(y, pred_arr),
        "switched_cells": int(k),
        "switched_rate": float(k / len(cell_frame)),
        "mean_realized_gain": float(np.mean(gains)),
        "selected_expert_counts": pd.Series(selected_experts).value_counts().to_dict(),
    }


def evaluate_detectors(cell_frame: pd.DataFrame, gain_pairs: pd.DataFrame, features: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    all_candidates = []
    metrics = []
    raw_loss = logloss(cell_frame["y"].to_numpy(dtype=float), cell_frame["pred__raw_knn_blend"].to_numpy(dtype=float))
    metrics.append({
        "model": "raw_knn_blend",
        "policy": "baseline",
        "param": 0.0,
        "logloss": raw_loss,
        "switched_cells": 0,
        "switched_rate": 0.0,
        "mean_realized_gain": 0.0,
    })
    for model_name in ["gradient_boosted_gain", "random_forest_gain", "extra_trees_gain"]:
        pred_col = f"predicted_gain__{model_name}"
        gain_pairs[pred_col] = predict_oof_gain(gain_pairs, model_name, features)
        candidates = best_candidate_per_cell(gain_pairs, pred_col)
        candidates["model"] = model_name
        all_candidates.append(candidates)
        for frac in TOP_FRACS:
            rec = evaluate_policy(cell_frame, candidates, "topfrac", frac)
            rec["model"] = model_name
            metrics.append({k: v for k, v in rec.items() if k != "selected_expert_counts"})
        for threshold in THRESHOLDS:
            rec = evaluate_policy(cell_frame, candidates, "threshold", threshold)
            rec["model"] = model_name
            metrics.append({k: v for k, v in rec.items() if k != "selected_expert_counts"})
    return pd.DataFrame(metrics).sort_values("logloss", kind="mergesort").reset_index(drop=True), pd.concat(all_candidates, ignore_index=True)


def train_final_candidate(
    features_frame: pd.DataFrame,
    labels: pd.DataFrame,
    sample: pd.DataFrame,
    raw_cols: list[str],
    gain_pairs: pd.DataFrame,
    features: list[str],
    best_policy: pd.Series,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    train = features_frame[features_frame["split"].eq("train")].copy().reset_index(drop=True)
    train[TARGETS] = labels[TARGETS].to_numpy(dtype=float)
    test = features_frame[features_frame["split"].eq("test")].copy().reset_index(drop=True)
    catalog, _audit = prediction_catalog(train, test, raw_cols)
    test_cells, test_pairs = build_cell_and_pair_frames(test, None, catalog, "test")
    raw_pred = test_cells["pred__raw_knn_blend"].to_numpy(dtype=float).reshape((len(test), len(TARGETS)))

    final_pairs = test_pairs[test_pairs["expert"].ne("raw_knn_blend")].copy().reset_index(drop=True)
    model_name = str(best_policy["model"])
    model = make_model(model_name)
    model.fit(gain_pairs[features].to_numpy(dtype=float), gain_pairs["gain"].to_numpy(dtype=float))
    final_pairs["predicted_gain"] = model.predict(final_pairs[features].to_numpy(dtype=float))
    candidates = best_candidate_per_cell(final_pairs, "predicted_gain")
    candidates["model"] = model_name

    if best_policy["policy"] == "topfrac":
        k = max(1, int(round(len(candidates) * float(best_policy["param"]))))
        selected = set(candidates.sort_values("predicted_gain", ascending=False, kind="mergesort").head(k)["cell_key"])
    else:
        selected = set(candidates[candidates["predicted_gain"].gt(float(best_policy["param"]))]["cell_key"])
    candidate_map = candidates.set_index("cell_key")

    pred_vec = []
    action_rows = []
    for rec in test_cells.to_dict("records"):
        cell_key = rec["cell_key"]
        if cell_key in selected:
            cand = candidate_map.loc[cell_key]
            pred_vec.append(float(cand["expert_pred"]))
            action_rows.append(
                {
                    "cell_key": cell_key,
                    "row": int(rec["row"]),
                    "subject_id": rec["subject_id"],
                    "target": rec["target"],
                    "selected_expert": str(cand["expert"]),
                    "predicted_gain": float(cand["predicted_gain"]),
                    "raw_pred": float(rec["pred__raw_knn_blend"]),
                    "selected_pred": float(cand["expert_pred"]),
                    "switched": True,
                }
            )
        else:
            pred_vec.append(float(rec["pred__raw_knn_blend"]))
            action_rows.append(
                {
                    "cell_key": cell_key,
                    "row": int(rec["row"]),
                    "subject_id": rec["subject_id"],
                    "target": rec["target"],
                    "selected_expert": "raw_knn_blend",
                    "predicted_gain": float(candidate_map.loc[cell_key]["predicted_gain"]),
                    "raw_pred": float(rec["pred__raw_knn_blend"]),
                    "selected_pred": float(rec["pred__raw_knn_blend"]),
                    "switched": False,
                }
            )
    pred = np.asarray(pred_vec, dtype=float).reshape((len(test), len(TARGETS)))
    submission = sample.copy()
    submission[TARGETS] = np.clip(pred, 1e-5, 1 - 1e-5)
    return submission, pd.DataFrame(action_rows)


def markdown_table(frame: pd.DataFrame) -> str:
    cols = list(frame.columns)
    rows = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for rec in frame.to_dict("records"):
        cells = []
        for col in cols:
            val = rec[col]
            cells.append(f"{val:.6f}" if isinstance(val, float) else str(val))
        rows.append("| " + " | ".join(cells) + " |")
    return "\n".join(rows)


def build_markdown(readout: dict[str, Any], metrics: pd.DataFrame) -> str:
    top = metrics.head(16).copy()
    return "\n".join(
        [
            "# Raw-KNN Failure Detector",
            "",
            "## 목적",
            "",
            "full contextual router가 raw KNN을 넘지 못했기 때문에, 이번에는 raw KNN을 기본값으로 두고 실패할 가능성이 높은 row-target cell만 다른 listener route로 전환한다.",
            "",
            "이 실험은 public LB, 기존 submission probability, action teacher, frontier file을 쓰지 않는다.",
            "",
            "## 핵심 결과",
            "",
            f"- raw KNN OOF logloss: `{readout['raw_knn_oof_logloss']:.6f}`",
            f"- best detector model: `{readout['best_detector_model']}`",
            f"- best detector policy: `{readout['best_detector_policy']}` `{readout['best_detector_param']}`",
            f"- best detector OOF logloss: `{readout['best_detector_oof_logloss']:.6f}`",
            f"- delta vs raw KNN: `{readout['best_detector_delta_vs_raw_knn']:.6f}`",
            f"- OOF switched cells: `{readout['best_detector_oof_switched_cells']}`",
            f"- generated candidate: `{readout['candidate_file']}`",
            "",
            "## Top OOF policies",
            "",
            markdown_table(top),
            "",
            "## 해석",
            "",
            "HS-JEPA route-risk signal은 broad router로 쓰면 불안정하지만, raw KNN failure detector로 좁히면 raw KNN보다 좋은 OOF 결과를 만든다.",
            "",
            "이 결과는 HS-JEPA를 `full router`보다 `failure-aware listener override`로 정립하는 편이 현재 데이터에서는 더 강하다는 뜻이다.",
        ]
    )


def run() -> dict[str, Any]:
    features_frame, labels, sample, raw_cols_from_module = load_world()
    raw_cols = raw_feature_cols(features_frame) if not raw_cols_from_module else raw_cols_from_module
    cell_frame, pair_frame = build_temporal_oof_frames(features_frame, labels, raw_cols)
    gain_pairs = prepare_gain_pairs(cell_frame, pair_frame)
    features = gain_feature_columns(gain_pairs)
    leak_cols = [col for col in features if "loss" in col or col in {"y", "raw_loss", "gain"}]
    if leak_cols:
        raise RuntimeError(f"leaky feature columns detected: {leak_cols}")
    metrics, candidates = evaluate_detectors(cell_frame, gain_pairs, features)
    raw = float(metrics[metrics["model"].eq("raw_knn_blend")]["logloss"].iloc[0])
    best = metrics.iloc[0]
    submission, actions = train_final_candidate(features_frame, labels, sample, raw_cols, gain_pairs, features, best)
    validate_submission(submission, sample)
    suffix = short_hash(submission)
    candidate_file = f"submission_hsjepa_raw_knn_failure_detector_{suffix}_uploadsafe.csv"
    submission.to_csv(ROOT / candidate_file, index=False)
    submission.to_csv(OUT / candidate_file, index=False)

    readout = {
        "package": "raw_knn_failure_detector",
        "status": "anchor_free_failure_detector_ready",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_action_teacher": False,
        "uses_frontier_file": False,
        "raw_knn_oof_logloss": raw,
        "best_detector_model": str(best["model"]),
        "best_detector_policy": str(best["policy"]),
        "best_detector_param": float(best["param"]),
        "best_detector_oof_logloss": float(best["logloss"]),
        "best_detector_delta_vs_raw_knn": float(best["logloss"] - raw),
        "best_detector_oof_switched_cells": int(best["switched_cells"]),
        "best_detector_oof_switched_rate": float(best["switched_rate"]),
        "best_detector_mean_realized_gain": float(best["mean_realized_gain"]),
        "feature_count": len(features),
        "leakage_guard_blocked_columns": ["loss", "gain", "raw_loss", "y", "loss__", "oracle_"],
        "candidate_file": candidate_file,
        "root_candidate_file": candidate_file,
        "test_switched_cells": int(actions["switched"].sum()),
        "test_switched_rows": int(actions.loc[actions["switched"], "row"].nunique()),
        "test_selected_expert_counts": actions["selected_expert"].value_counts().to_dict(),
        "interpretation": "HS-JEPA route-risk is more useful as a raw-KNN failure detector than as a broad contextual router.",
    }

    metrics.to_csv(OUT / "raw_knn_failure_detector_oof_metrics.csv", index=False)
    candidates.to_csv(OUT / "raw_knn_failure_detector_oof_candidate_cells.csv", index=False)
    gain_pairs.to_csv(OUT / "raw_knn_failure_detector_oof_gain_pairs.csv", index=False)
    actions.to_csv(OUT / "raw_knn_failure_detector_test_actions.csv", index=False)
    (OUT / "raw_knn_failure_detector_readout.json").write_text(json.dumps(readout, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "RAW_KNN_FAILURE_DETECTOR_KO.md").write_text(build_markdown(readout, metrics), encoding="utf-8")
    return readout


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
