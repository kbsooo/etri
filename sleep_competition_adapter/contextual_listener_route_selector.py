#!/usr/bin/env python3
"""Context-dependent listener route selector.

This experiment continues the anchor-free HS-JEPA line:

- no public LB ledger
- no prior submission probabilities
- no action teacher
- no row-state frontier file

The previous OOF benchmark showed that a target-level listener route selector
beats single-route baselines on temporal future splits.  This script asks the
next architecture question:

    Can HS-JEPA context choose the listener route per row-target cell?

It trains a route-risk regressor on OOF cells only.  For each candidate route it
predicts the cell log-loss and selects or softly mixes routes with lower
predicted loss.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sleep_competition_adapter.core_oof_action_health_benchmark import (  # noqa: E402
    ID_COLS,
    TARGETS,
    load_world,
    logloss,
    prediction_catalog,
    raw_feature_cols,
    short_hash,
    temporal_subject_tail_splits,
    validate_submission,
)


OUT = ROOT / "sleep_competition_adapter" / "outputs" / "contextual_listener_route_selector"
OUT.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = 20260612
SOFT_TEMPERATURE = 0.035
RAW_FALLBACK_MARGINS = [0.000, 0.004, 0.008, 0.014, 0.022]


EXPERT_FAMILIES = {
    "global_prior": "safe_prior",
    "subject_prior": "safe_prior",
    "raw_knn_blend": "raw_lifelog",
    "core_knn_blend": "human_state_core",
    "hsjepa_action_health__strict_listener_health": "core_action_health",
    "hsjepa_action_health__balanced_listener_health": "core_action_health",
    "hsjepa_action_health__wide_listener_health": "core_action_health",
    "hsjepa_action_health__high_margin_listener_health": "core_action_health",
    "raw_action_core_health__strict_listener_health": "raw_action_core_gate",
    "raw_action_core_health__balanced_listener_health": "raw_action_core_gate",
    "raw_action_core_health__wide_listener_health": "raw_action_core_gate",
    "raw_action_core_health__high_margin_listener_health": "raw_action_core_gate",
}


def cell_loss(y: np.ndarray, pred: np.ndarray) -> np.ndarray:
    pred = np.clip(pred.astype(float), 1e-5, 1 - 1e-5)
    return -(y.astype(float) * np.log(pred) + (1 - y.astype(float)) * np.log(1 - pred))


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-values))


def logit(values: np.ndarray) -> np.ndarray:
    values = np.clip(values.astype(float), 1e-5, 1 - 1e-5)
    return np.log(values / (1.0 - values))


def target_index(target: str) -> int:
    return TARGETS.index(target)


def numeric(value: Any, default: float = 0.0) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    return out if math.isfinite(out) else default


def route_family_features(expert: str) -> dict[str, float]:
    family = EXPERT_FAMILIES.get(expert, "other")
    return {
        "expert_is_global_prior": float(expert == "global_prior"),
        "expert_is_subject_prior": float(expert == "subject_prior"),
        "expert_is_raw_lifelog": float(family == "raw_lifelog"),
        "expert_is_core_geometry": float(family == "human_state_core"),
        "expert_is_core_action_health": float(family == "core_action_health"),
        "expert_is_raw_action_core_gate": float(family == "raw_action_core_gate"),
        "expert_is_strict": float("strict" in expert),
        "expert_is_balanced": float("balanced" in expert),
        "expert_is_wide": float("wide" in expert),
        "expert_is_high_margin": float("high_margin" in expert),
    }


def row_context_features(row: pd.Series, target: str, expert_values: dict[str, float]) -> dict[str, float]:
    values = np.asarray(list(expert_values.values()), dtype=float)
    logits = logit(values)
    target_idx = target_index(target)
    return {
        "target_idx": float(target_idx),
        "target_is_q": float(target.startswith("Q")),
        "target_is_s": float(target.startswith("S")),
        "target_is_q2": float(target == "Q2"),
        "target_is_s2": float(target == "S2"),
        "dayofweek": numeric(row.get("dayofweek")) / 6.0,
        "is_weekend": numeric(row.get("is_weekend")),
        "dayofmonth_rank": numeric(row.get("dayofmonth")) / 31.0,
        "month_start_proximity": numeric(row.get("month_start_proximity")) / 7.0,
        "month_end": numeric(row.get("month_end")),
        "dist_to_subject_normal": numeric(row.get("dist_to_subject_normal")),
        "dist_to_peer_normal": numeric(row.get("dist_to_peer_normal")),
        "subject_minus_peer_dist": abs(numeric(row.get("subject_minus_peer_dist"))),
        "subject_outlier_rank": numeric(row.get("subject_outlier_rank"), 0.5),
        "peer_outlier_rank": numeric(row.get("peer_outlier_rank"), 0.5),
        "cohort_outlier_score": numeric(row.get("cohort_outlier_score"), 0.5),
        "expert_prob_mean": float(values.mean()),
        "expert_prob_std": float(values.std(ddof=0)),
        "expert_prob_range": float(values.max() - values.min()),
        "expert_logit_std": float(logits.std(ddof=0)),
        "raw_core_gap": float(abs(expert_values.get("raw_knn_blend", 0.5) - expert_values.get("core_knn_blend", 0.5))),
        "subject_global_gap": float(abs(expert_values.get("subject_prior", 0.5) - expert_values.get("global_prior", 0.5))),
        "core_subject_gap": float(abs(expert_values.get("core_knn_blend", 0.5) - expert_values.get("subject_prior", 0.5))),
        "raw_subject_gap": float(abs(expert_values.get("raw_knn_blend", 0.5) - expert_values.get("subject_prior", 0.5))),
    }


def build_cell_and_pair_frames(
    eval_frame: pd.DataFrame,
    y_eval: pd.DataFrame | None,
    catalog: dict[str, np.ndarray],
    fold: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    cell_rows = []
    pair_rows = []
    expert_names = list(catalog.keys())
    for row_pos, (_, row) in enumerate(eval_frame.iterrows()):
        for target in TARGETS:
            t_idx = target_index(target)
            expert_values = {name: float(catalog[name][row_pos, t_idx]) for name in expert_names}
            context = row_context_features(row, target, expert_values)
            y_value = None if y_eval is None else float(y_eval.iloc[row_pos][target])
            losses = {
                name: (float(cell_loss(np.asarray([y_value]), np.asarray([pred]))[0]) if y_value is not None else np.nan)
                for name, pred in expert_values.items()
            }
            oracle_expert = min(losses, key=losses.get) if y_value is not None else ""
            cell_key = f"{int(row.get('metric_row', row_pos))}:{target}"
            cell_base = {
                "cell_key": cell_key,
                "fold": fold,
                "row": int(row.get("metric_row", row_pos)),
                "subject_id": row["subject_id"],
                "target": target,
                "target_idx": t_idx,
                "y": y_value if y_value is not None else np.nan,
                "oracle_expert": oracle_expert,
                "oracle_loss": losses.get(oracle_expert, np.nan) if y_value is not None else np.nan,
            }
            cell_base.update(context)
            for name, pred in expert_values.items():
                cell_base[f"pred__{name}"] = pred
                cell_base[f"loss__{name}"] = losses[name]
            cell_rows.append(cell_base)
            for name, pred in expert_values.items():
                pair = {
                    "cell_key": cell_key,
                    "fold": fold,
                    "row": int(row.get("metric_row", row_pos)),
                    "subject_id": row["subject_id"],
                    "target": target,
                    "expert": name,
                    "expert_pred": pred,
                    "expert_logit": float(logit(np.asarray([pred]))[0]),
                    "loss": losses[name],
                    "abs_vs_global": abs(pred - expert_values.get("global_prior", pred)),
                    "abs_vs_subject": abs(pred - expert_values.get("subject_prior", pred)),
                    "abs_vs_raw": abs(pred - expert_values.get("raw_knn_blend", pred)),
                    "abs_vs_core": abs(pred - expert_values.get("core_knn_blend", pred)),
                }
                pair.update(context)
                pair.update(route_family_features(name))
                pair_rows.append(pair)
    return pd.DataFrame(cell_rows), pd.DataFrame(pair_rows)


def build_temporal_oof_frames(features: pd.DataFrame, labels: pd.DataFrame, raw_cols: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    train = features[features["split"].eq("train")].copy().reset_index(drop=True)
    train[TARGETS] = labels[TARGETS].to_numpy(dtype=float)
    cell_frames = []
    pair_frames = []
    for fold_name, tr_idx, val_idx in temporal_subject_tail_splits(train):
        tr = train.loc[tr_idx].copy()
        val = train.loc[val_idx].copy()
        catalog, _audit = prediction_catalog(tr, val, raw_cols)
        y_val = val[TARGETS].copy().reset_index(drop=True)
        cells, pairs = build_cell_and_pair_frames(val.reset_index(drop=True), y_val, catalog, fold_name)
        cell_frames.append(cells)
        pair_frames.append(pairs)
    return pd.concat(cell_frames, ignore_index=True), pd.concat(pair_frames, ignore_index=True)


def feature_columns(pair_frame: pd.DataFrame) -> list[str]:
    blocked = {"cell_key", "fold", "row", "subject_id", "target", "expert", "loss"}
    return [
        col
        for col in pair_frame.columns
        if col not in blocked and pd.api.types.is_numeric_dtype(pair_frame[col])
    ]


def make_router() -> RandomForestRegressor:
    return RandomForestRegressor(
        n_estimators=360,
        max_depth=7,
        min_samples_leaf=10,
        max_features=0.72,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )


def route_predictions(cell_frame: pd.DataFrame, pair_frame: pd.DataFrame, pred_loss_col: str) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    merged = pair_frame[["cell_key", "expert", "expert_pred", pred_loss_col]].copy()
    selected_rows = []
    hard_pred = []
    soft_pred = []
    for cell_key, group in merged.groupby("cell_key", sort=False):
        group = group.sort_values(pred_loss_col, ascending=True, kind="mergesort")
        best = group.iloc[0]
        hard_pred.append(float(best["expert_pred"]))
        raw_scores = -group[pred_loss_col].to_numpy(dtype=float)
        peak = raw_scores.max()
        weights = np.exp((raw_scores - peak) / SOFT_TEMPERATURE)
        weights = weights / max(weights.sum(), 1e-12)
        soft_pred.append(float(np.sum(weights * group["expert_pred"].to_numpy(dtype=float))))
        selected_rows.append(
            {
                "cell_key": cell_key,
                "selected_expert": str(best["expert"]),
                "predicted_loss": float(best[pred_loss_col]),
                "soft_entropy": float(-(weights * np.log(np.clip(weights, 1e-12, 1))).sum()),
            }
        )
    route = pd.DataFrame(selected_rows)
    ordered = cell_frame[["cell_key"]].merge(route, on="cell_key", how="left")
    return ordered, np.asarray(hard_pred, dtype=float), np.asarray(soft_pred, dtype=float)


def raw_fallback_predictions(pair_frame: pd.DataFrame, pred_loss_col: str, margin: float) -> tuple[np.ndarray, list[str]]:
    preds = []
    experts = []
    for _cell_key, group in pair_frame.groupby("cell_key", sort=False):
        group = group.sort_values(pred_loss_col, ascending=True, kind="mergesort")
        raw = group[group["expert"].eq("raw_knn_blend")]
        best = group.iloc[0]
        if raw.empty:
            preds.append(float(best["expert_pred"]))
            experts.append(str(best["expert"]))
            continue
        raw_row = raw.iloc[0]
        if float(best[pred_loss_col]) + margin < float(raw_row[pred_loss_col]):
            preds.append(float(best["expert_pred"]))
            experts.append(str(best["expert"]))
        else:
            preds.append(float(raw_row["expert_pred"]))
            experts.append("raw_knn_blend")
    return np.asarray(preds, dtype=float), experts


def evaluate_oof_router(cell_frame: pd.DataFrame, pair_frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    features = feature_columns(pair_frame)
    routed_cells = []
    metric_rows = []
    y_all = cell_frame["y"].to_numpy(dtype=float)

    expert_names = [col.removeprefix("pred__") for col in cell_frame.columns if col.startswith("pred__")]
    for expert in expert_names:
        metric_rows.append({
            "model": expert,
            "mean_logloss": logloss(y_all, cell_frame[f"pred__{expert}"].to_numpy(dtype=float)),
        })

    fixed_preds = np.zeros(len(cell_frame), dtype=float)
    hard_preds = np.zeros(len(cell_frame), dtype=float)
    soft_preds = np.zeros(len(cell_frame), dtype=float)
    fallback_preds = {margin: np.zeros(len(cell_frame), dtype=float) for margin in RAW_FALLBACK_MARGINS}

    for subject in sorted(cell_frame["subject_id"].unique()):
        train_cells = cell_frame[~cell_frame["subject_id"].eq(subject)].copy()
        eval_cells = cell_frame[cell_frame["subject_id"].eq(subject)].copy()
        train_pairs = pair_frame[~pair_frame["subject_id"].eq(subject)].copy()
        eval_pairs = pair_frame[pair_frame["subject_id"].eq(subject)].copy()

        # Fixed target route chosen without the held-out subject.
        target_route = {}
        for target in TARGETS:
            losses = {
                expert: float(train_cells[train_cells["target"].eq(target)][f"loss__{expert}"].mean())
                for expert in expert_names
            }
            target_route[target] = min(losses, key=losses.get)
        for idx, row in eval_cells.iterrows():
            expert = target_route[str(row["target"])]
            fixed_preds[idx] = float(row[f"pred__{expert}"])

        router = make_router()
        router.fit(train_pairs[features].to_numpy(dtype=float), train_pairs["loss"].to_numpy(dtype=float))
        eval_pairs = eval_pairs.copy()
        eval_pairs["predicted_route_loss"] = router.predict(eval_pairs[features].to_numpy(dtype=float))
        route, hard, soft = route_predictions(eval_cells, eval_pairs, "predicted_route_loss")
        fallback = {
            margin: raw_fallback_predictions(eval_pairs, "predicted_route_loss", margin)
            for margin in RAW_FALLBACK_MARGINS
        }
        eval_indices = eval_cells.index.to_numpy()
        hard_preds[eval_indices] = hard
        soft_preds[eval_indices] = soft
        for margin, pred in fallback.items():
            fallback_preds[margin][eval_indices] = pred[0]
        route["subject_id"] = subject
        routed_cells.append(route)

    metric_rows.append({"model": "fixed_target_listener_route_oof", "mean_logloss": logloss(y_all, fixed_preds)})
    metric_rows.append({"model": "contextual_listener_router_hard_oof", "mean_logloss": logloss(y_all, hard_preds)})
    metric_rows.append({"model": "contextual_listener_router_soft_oof", "mean_logloss": logloss(y_all, soft_preds)})
    for margin, pred in fallback_preds.items():
        metric_rows.append({
            "model": f"contextual_raw_fallback_margin_{margin:.3f}",
            "mean_logloss": logloss(y_all, pred),
        })
    metrics = pd.DataFrame(metric_rows).sort_values("mean_logloss", kind="mergesort").reset_index(drop=True)
    routed = pd.concat(routed_cells, ignore_index=True)
    return metrics, routed


def train_final_context_router(
    features: pd.DataFrame,
    labels: pd.DataFrame,
    sample: pd.DataFrame,
    raw_cols: list[str],
    oof_pairs: pd.DataFrame,
    selected_mode: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    train = features[features["split"].eq("train")].copy().reset_index(drop=True)
    train[TARGETS] = labels[TARGETS].to_numpy(dtype=float)
    test = features[features["split"].eq("test")].copy().reset_index(drop=True)
    catalog, _audit = prediction_catalog(train, test, raw_cols)
    test_cells, test_pairs = build_cell_and_pair_frames(test, None, catalog, "test")

    features_cols = feature_columns(oof_pairs)
    router = make_router()
    router.fit(oof_pairs[features_cols].to_numpy(dtype=float), oof_pairs["loss"].to_numpy(dtype=float))
    test_pairs = test_pairs.copy()
    test_pairs["predicted_route_loss"] = router.predict(test_pairs[features_cols].to_numpy(dtype=float))
    route, hard, soft = route_predictions(test_cells, test_pairs, "predicted_route_loss")

    if selected_mode == "soft":
        pred_vec = soft
        final_experts = ["soft_mixture"] * len(route)
    elif selected_mode.startswith("raw_fallback_margin_"):
        margin = float(selected_mode.rsplit("_", 1)[1])
        pred_vec, final_experts = raw_fallback_predictions(test_pairs, "predicted_route_loss", margin)
    else:
        pred_vec = hard
        final_experts = route["selected_expert"].astype(str).tolist()
    pred = pred_vec.reshape((len(test), len(TARGETS)))
    sub = sample.copy()
    sub[TARGETS] = np.clip(pred, 1e-5, 1 - 1e-5)
    route = pd.concat([test_cells[["cell_key", "row", "subject_id", "target", "target_idx"]].reset_index(drop=True), route.drop(columns=["cell_key"])], axis=1)
    route["final_selected_expert"] = final_experts
    return sub, route


def build_markdown(readout: dict[str, Any], metrics: pd.DataFrame) -> str:
    def table_md(frame: pd.DataFrame) -> str:
        cols = list(frame.columns)
        rows = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
        for rec in frame.to_dict("records"):
            cells = []
            for col in cols:
                value = rec[col]
                cells.append(f"{value:.6f}" if isinstance(value, float) else str(value))
            rows.append("| " + " | ".join(cells) + " |")
        return "\n".join(rows)

    lines = [
        "# Contextual Listener Route Selector",
        "",
        "## 목적",
        "",
        "target별 고정 route selector 다음 질문을 검증한다.",
        "",
        "```text",
        "HS-JEPA core context가 row-target마다 어떤 listener route를 들어야 하는지 고를 수 있는가?",
        "```",
        "",
        "이 실험은 public LB, 기존 submission probability, action teacher, frontier file을 쓰지 않는다.",
        "",
        "## 핵심 결과",
        "",
        f"- best OOF model: `{readout['best_oof_model']}`",
        f"- best OOF logloss: `{readout['best_oof_logloss']:.6f}`",
        f"- fixed target route OOF logloss: `{readout['fixed_target_route_oof_logloss']:.6f}`",
        f"- contextual hard router OOF logloss: `{readout['contextual_hard_oof_logloss']:.6f}`",
        f"- contextual soft router OOF logloss: `{readout['contextual_soft_oof_logloss']:.6f}`",
        f"- best contextual/fallback model: `{readout['best_contextual_or_fallback_model']}`",
        f"- best contextual/fallback OOF logloss: `{readout['best_contextual_or_fallback_oof_logloss']:.6f}`",
        f"- delta vs raw KNN: `{readout['best_contextual_or_fallback_delta_vs_raw_knn']:.6f}`",
        f"- selected submission mode: `{readout['selected_submission_mode']}`",
        f"- generated candidate: `{readout['candidate_file']}`",
        "",
        "## OOF score table",
        "",
        table_md(metrics),
        "",
        "## 해석",
        "",
        "contextual router가 fixed target route를 이기면 HS-JEPA가 sample-level listener responsibility로 확장됐다는 뜻이다.",
        "",
        "raw-fallback이 raw KNN을 이기면 HS-JEPA가 좋은 기본 예측기에서 벗어날 순간을 고른다는 뜻이다.",
        "",
        "이기지 못하면 현재 증거는 target-level route selection까지가 안정적이고, sample-level route는 아직 데이터 수가 부족하거나 action-risk supervision이 약하다는 뜻이다.",
    ]
    return "\n".join(lines)


def run() -> dict[str, Any]:
    features, labels, sample, raw_cols_from_module = load_world()
    raw_cols = raw_feature_cols(features) if not raw_cols_from_module else raw_cols_from_module
    cell_frame, pair_frame = build_temporal_oof_frames(features, labels, raw_cols)
    metrics, routed_oof = evaluate_oof_router(cell_frame, pair_frame)

    fixed = float(metrics[metrics["model"].eq("fixed_target_listener_route_oof")]["mean_logloss"].iloc[0])
    hard = float(metrics[metrics["model"].eq("contextual_listener_router_hard_oof")]["mean_logloss"].iloc[0])
    soft = float(metrics[metrics["model"].eq("contextual_listener_router_soft_oof")]["mean_logloss"].iloc[0])
    best = metrics.iloc[0]
    route_candidates = metrics[
        metrics["model"].str.startswith("contextual_listener_router_")
        | metrics["model"].str.startswith("contextual_raw_fallback_")
    ].copy()
    best_route_candidate = route_candidates.sort_values("mean_logloss", kind="mergesort").iloc[0]
    best_route_name = str(best_route_candidate["model"])
    if best_route_name == "contextual_listener_router_soft_oof":
        selected_mode = "soft"
    elif best_route_name == "contextual_listener_router_hard_oof":
        selected_mode = "hard"
    elif best_route_name.startswith("contextual_raw_fallback_margin_"):
        selected_mode = best_route_name.replace("contextual_", "")
    else:
        selected_mode = "soft" if soft <= hard else "hard"
    submission, test_route = train_final_context_router(features, labels, sample, raw_cols, pair_frame, selected_mode)
    validate_submission(submission, sample)
    suffix = short_hash(submission)
    candidate_file = f"submission_hsjepa_contextual_listener_router_{suffix}_uploadsafe.csv"
    submission.to_csv(ROOT / candidate_file, index=False)
    submission.to_csv(OUT / candidate_file, index=False)

    readout = {
        "package": "contextual_listener_route_selector",
        "status": "anchor_free_contextual_router_ready",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_action_teacher": False,
        "uses_frontier_file": False,
        "best_oof_model": str(best["model"]),
        "best_oof_logloss": float(best["mean_logloss"]),
        "fixed_target_route_oof_logloss": fixed,
        "contextual_hard_oof_logloss": hard,
        "contextual_soft_oof_logloss": soft,
        "best_contextual_or_fallback_model": best_route_name,
        "best_contextual_or_fallback_oof_logloss": float(best_route_candidate["mean_logloss"]),
        "contextual_hard_delta_vs_fixed": hard - fixed,
        "contextual_soft_delta_vs_fixed": soft - fixed,
        "best_contextual_or_fallback_delta_vs_raw_knn": float(best_route_candidate["mean_logloss"] - metrics[metrics["model"].eq("raw_knn_blend")]["mean_logloss"].iloc[0]),
        "selected_submission_mode": selected_mode,
        "candidate_file": candidate_file,
        "root_candidate_file": candidate_file,
        "test_selected_expert_counts": test_route["final_selected_expert"].value_counts().to_dict(),
        "test_selected_target_expert_counts": test_route.groupby(["target", "final_selected_expert"]).size().astype(int).reset_index(name="count").to_dict("records"),
        "interpretation": "Tests whether HS-JEPA can move from fixed target listener routes to sample-level contextual route responsibility.",
    }

    cell_frame.to_csv(OUT / "contextual_listener_route_oof_cells.csv", index=False)
    pair_frame.to_csv(OUT / "contextual_listener_route_oof_pairs.csv", index=False)
    metrics.to_csv(OUT / "contextual_listener_route_oof_metrics.csv", index=False)
    routed_oof.to_csv(OUT / "contextual_listener_route_oof_selected_cells.csv", index=False)
    test_route.to_csv(OUT / "contextual_listener_route_test_selected_cells.csv", index=False)
    (OUT / "contextual_listener_route_readout.json").write_text(json.dumps(readout, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "CONTEXTUAL_LISTENER_ROUTE_SELECTOR_KO.md").write_text(build_markdown(readout, metrics), encoding="utf-8")
    return readout


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
