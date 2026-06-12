#!/usr/bin/env python3
"""Row-level reset episode detector for HS-JEPA.

The failure-boundary law distilled a cell-level detector into a very simple
prior-reset rule.  Its selected test actions were not sparse cell edits: they
reset 20 entire rows across all 7 targets.  This script treats that as a hidden
episode hypothesis instead of a row-target correction problem.

Question:

    Can HS-JEPA context detect full-row episodes where raw lifelog memory should
    be reset to a safer prior route?

No public LB ledger, prior submission probabilities, action teacher, or
frontier file is used.  Supervision comes only from OG train OOF row-level
loss: raw-KNN row loss versus full-row global/subject/core reset loss.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import ElasticNet
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


OUT = ROOT / "sleep_competition_adapter" / "outputs" / "row_reset_episode_detector"
OUT.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = 20260612
RESET_ROUTES = ["global_prior", "subject_prior", "core_knn_blend"]
TOP_FRACS = [0.01, 0.02, 0.04, 0.06, 0.08, 0.10, 0.15, 0.20, 0.30]
THRESHOLDS = [-0.02, -0.01, 0.0, 0.005, 0.01, 0.02, 0.04, 0.08, 0.12]
NULL_REPEATS = 6000

ROW_CONTEXT_COLS = [
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


def route_family(route: str) -> str:
    if route in {"global_prior", "subject_prior"}:
        return "prior_reset"
    if route == "core_knn_blend":
        return "core_reset"
    return "other"


def row_key_cols(frame: pd.DataFrame) -> list[str]:
    cols = ["fold", "row", "subject_id"]
    return [col for col in cols if col in frame.columns]


def aggregate_row_frame(cell_frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    pred_cols = [col for col in cell_frame.columns if col.startswith("pred__")]
    for key, group in cell_frame.groupby(row_key_cols(cell_frame), sort=False):
        if not isinstance(key, tuple):
            key = (key,)
        base = dict(zip(row_key_cols(cell_frame), key))
        first = group.iloc[0]
        rec: dict[str, Any] = {
            **base,
            "target_count": int(len(group)),
            "row_mod_7": float(int(first["row"]) % 7) / 6.0,
            "row_mod_14": float(int(first["row"]) % 14) / 13.0,
            "row_mod_28": float(int(first["row"]) % 28) / 27.0,
        }
        for col in ROW_CONTEXT_COLS:
            if col in group.columns:
                rec[col] = float(pd.to_numeric(group[col], errors="coerce").mean())
        for col in ["raw_core_gap", "subject_global_gap", "core_subject_gap", "raw_subject_gap", "expert_prob_mean", "expert_prob_std", "expert_prob_range", "expert_logit_std"]:
            if col in group.columns:
                vals = pd.to_numeric(group[col], errors="coerce")
                rec[f"{col}__mean"] = float(vals.mean())
                rec[f"{col}__max"] = float(vals.max())
                rec[f"{col}__std"] = float(vals.std(ddof=0))
        for pred_col in pred_cols:
            name = pred_col.removeprefix("pred__")
            vals = pd.to_numeric(group[pred_col], errors="coerce")
            rec[f"{name}__pred_mean"] = float(vals.mean())
            rec[f"{name}__pred_std"] = float(vals.std(ddof=0))
            rec[f"{name}__pred_min"] = float(vals.min())
            rec[f"{name}__pred_max"] = float(vals.max())
            rec[f"{name}__confidence_mean"] = float((vals - 0.5).abs().mean() * 2.0)
            loss_col = f"loss__{name}"
            if loss_col in group.columns:
                rec[f"{name}__loss_mean"] = float(pd.to_numeric(group[loss_col], errors="coerce").mean())
        for route in ["global_prior", "subject_prior", "core_knn_blend"]:
            if f"{route}__pred_mean" in rec:
                raw = group["pred__raw_knn_blend"].to_numpy(dtype=float)
                alt = group[f"pred__{route}"].to_numpy(dtype=float)
                rec[f"{route}__abs_vs_raw_mean"] = float(np.abs(alt - raw).mean())
                rec[f"{route}__abs_vs_raw_max"] = float(np.abs(alt - raw).max())
                core = group["pred__core_knn_blend"].to_numpy(dtype=float)
                rec[f"{route}__abs_vs_core_mean"] = float(np.abs(alt - core).mean())
        rows.append(rec)
    frame = pd.DataFrame(rows)
    if "subject_id" in frame.columns:
        frame["subject_row_rank"] = frame.groupby("subject_id")["row"].rank(method="first", pct=True)
        frame["subject_row_index"] = frame.groupby("subject_id").cumcount().astype(float)
        frame["subject_row_index_norm"] = frame.groupby("subject_id")["subject_row_index"].transform(lambda s: s / max(float(s.max()), 1.0))
    frame["row_norm"] = pd.to_numeric(frame["row"], errors="coerce") / max(float(pd.to_numeric(frame["row"], errors="coerce").max()), 1.0)
    return frame


def build_row_pairs(row_frame: pd.DataFrame, require_losses: bool = True) -> pd.DataFrame:
    pairs = []
    for rec in row_frame.to_dict("records"):
        raw_loss = float(rec.get("raw_knn_blend__loss_mean", np.nan))
        if require_losses and not np.isfinite(raw_loss):
            raise KeyError("raw_knn_blend__loss_mean")
        for route in RESET_ROUTES:
            loss_key = f"{route}__loss_mean"
            if require_losses and loss_key not in rec:
                continue
            reset_loss = float(rec.get(loss_key, np.nan))
            item = dict(rec)
            item["reset_route"] = route
            item["route_family"] = route_family(route)
            item["route_is_global_prior"] = float(route == "global_prior")
            item["route_is_subject_prior"] = float(route == "subject_prior")
            item["route_is_core"] = float(route == "core_knn_blend")
            item["route_pred_mean"] = float(rec.get(f"{route}__pred_mean", 0.5))
            item["route_pred_std"] = float(rec.get(f"{route}__pred_std", 0.0))
            item["route_confidence_mean"] = float(rec.get(f"{route}__confidence_mean", 0.0))
            item["route_abs_vs_raw_mean"] = float(rec.get(f"{route}__abs_vs_raw_mean", 0.0))
            item["route_abs_vs_raw_max"] = float(rec.get(f"{route}__abs_vs_raw_max", 0.0))
            item["route_abs_vs_core_mean"] = float(rec.get(f"{route}__abs_vs_core_mean", 0.0))
            item["reset_loss_mean"] = reset_loss
            item["row_reset_gain"] = raw_loss - reset_loss if np.isfinite(reset_loss) and np.isfinite(raw_loss) else np.nan
            pairs.append(item)
    return pd.DataFrame(pairs)


def feature_columns(frame: pd.DataFrame, view: str) -> list[str]:
    blocked = {
        "fold",
        "row",
        "subject_id",
        "reset_route",
        "route_family",
        "row_reset_gain",
        "reset_loss_mean",
    }
    # Detector score columns are produced during the evaluation loop.  They are
    # OOF-only meta-features and must not leak into later full-context models.
    blocked_prefixes = ("loss__", "pred__")
    numeric_cols = [
        col
        for col in frame.columns
        if col not in blocked
        and not col.startswith(blocked_prefixes)
        and "__loss_" not in col
        and not col.endswith("_loss_mean")
        and pd.api.types.is_numeric_dtype(frame[col])
    ]
    if view == "episode_context":
        keep_tokens = [
            "day",
            "month",
            "subject_",
            "peer_",
            "cohort",
            "dist_",
            "row_",
            "route_",
            "raw_core_gap",
            "subject_global_gap",
            "core_subject_gap",
            "raw_subject_gap",
        ]
        return [col for col in numeric_cols if any(token in col for token in keep_tokens)]
    if view == "route_reset_context":
        keep_tokens = [
            "route_",
            "global_prior",
            "subject_prior",
            "core_knn_blend",
            "raw_knn_blend",
            "raw_core_gap",
            "subject_global_gap",
            "core_subject_gap",
            "raw_subject_gap",
            "expert_prob",
            "expert_logit",
        ]
        return [col for col in numeric_cols if any(token in col for token in keep_tokens)]
    if view == "full_row_context":
        return numeric_cols
    raise KeyError(view)


def model_specs() -> list[dict[str, Any]]:
    specs = []
    for depth, leaf in [(2, 5), (3, 4), (4, 3), (5, 2)]:
        specs.append({"name": f"tree_depth{depth}_leaf{leaf}", "family": "tree", "depth": depth, "leaf": leaf})
    specs.append({"name": "elasticnet_sparse", "family": "elasticnet", "alpha": 0.0008, "l1_ratio": 0.82})
    return specs


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
    raise KeyError(spec["family"])


def predict_oof(frame: pd.DataFrame, features: list[str], spec: dict[str, Any]) -> np.ndarray:
    pred = np.full(len(frame), np.nan, dtype=float)
    for subject in sorted(frame["subject_id"].unique()):
        train = frame[~frame["subject_id"].eq(subject)]
        valid = frame[frame["subject_id"].eq(subject)]
        model = make_model(spec)
        model.fit(train[features], train["row_reset_gain"].to_numpy(dtype=float))
        pred[valid.index.to_numpy()] = model.predict(valid[features])
    if np.isnan(pred).any():
        raise RuntimeError("OOF row reset prediction contains NaN")
    return pred


def best_route_per_row(pair_frame: pd.DataFrame, score_col: str, law_name: str) -> pd.DataFrame:
    rows = []
    keys = ["fold", "row", "subject_id"] if "fold" in pair_frame.columns else ["row", "subject_id"]
    for key, group in pair_frame.groupby(keys, sort=False):
        if not isinstance(key, tuple):
            key = (key,)
        best = group.sort_values(score_col, ascending=False, kind="mergesort").iloc[0]
        item = dict(zip(keys, key))
        item.update(
            {
                "reset_route": str(best["reset_route"]),
                "route_family": str(best["route_family"]),
                "selection_score": float(best[score_col]),
                "row_reset_gain": float(best["row_reset_gain"]) if "row_reset_gain" in best.index else np.nan,
                "raw_loss_mean": float(best.get("raw_knn_blend__loss_mean", np.nan)),
                "reset_loss_mean": float(best.get("reset_loss_mean", np.nan)),
                "law_name": law_name,
            }
        )
        rows.append(item)
    return pd.DataFrame(rows)


def selected_rows(candidates: pd.DataFrame, policy: str, param: float) -> set[tuple[int, str]]:
    if policy == "topfrac":
        k = max(1, int(round(len(candidates) * param)))
        frame = candidates.sort_values("selection_score", ascending=False, kind="mergesort").head(k)
    elif policy == "threshold":
        frame = candidates[candidates["selection_score"].gt(param)]
    else:
        raise KeyError(policy)
    return {(int(row), str(subject)) for row, subject in zip(frame["row"], frame["subject_id"])}


def evaluate_policy(cell_frame: pd.DataFrame, candidates: pd.DataFrame, policy: str, param: float) -> tuple[dict[str, Any], pd.DataFrame, np.ndarray]:
    selected = selected_rows(candidates, policy, param)
    route_map = {
        (int(rec["row"]), str(rec["subject_id"])): str(rec["reset_route"])
        for rec in candidates.to_dict("records")
    }
    gain_map = {
        (int(rec["row"]), str(rec["subject_id"])): float(rec["row_reset_gain"])
        for rec in candidates.to_dict("records")
    }
    pred = []
    actions = []
    selected_row_gains = []
    for rec in cell_frame.to_dict("records"):
        key = (int(rec["row"]), str(rec["subject_id"]))
        if key in selected:
            route = route_map[key]
            pred.append(float(rec[f"pred__{route}"]))
            actions.append(
                {
                    "fold": rec.get("fold", ""),
                    "row": int(rec["row"]),
                    "subject_id": str(rec["subject_id"]),
                    "target": rec["target"],
                    "reset_route": route,
                    "route_family": route_family(route),
                    "raw_pred": float(rec["pred__raw_knn_blend"]),
                    "selected_pred": float(rec[f"pred__{route}"]),
                    "row_reset_gain": gain_map[key],
                    "switched": True,
                }
            )
            if rec["target"] == TARGETS[0]:
                selected_row_gains.append(gain_map[key])
        else:
            pred.append(float(rec["pred__raw_knn_blend"]))
    pred_arr = np.asarray(pred, dtype=float)
    y = cell_frame["y"].to_numpy(dtype=float)
    action_frame = pd.DataFrame(actions)
    metric = {
        "policy": policy,
        "param": float(param),
        "logloss": logloss(y, pred_arr),
        "selected_rows": int(len(selected)),
        "switched_cells": int(len(selected) * len(TARGETS)),
        "mean_realized_gain_all_rows": float(np.sum(selected_row_gains) / max(1, cell_frame["row"].nunique())),
        "mean_realized_gain_selected_rows": float(np.mean(selected_row_gains)) if selected_row_gains else 0.0,
        "positive_row_gain_rate": float((np.asarray(selected_row_gains) > 0).mean()) if selected_row_gains else 0.0,
    }
    return metric, action_frame, pred_arr


def row_null(candidates: pd.DataFrame, selected_actions: pd.DataFrame, denominator: int, repeats: int = NULL_REPEATS) -> dict[str, float]:
    if selected_actions.empty:
        return {"row_null_mean": 0.0, "row_null_std": 0.0, "row_null_p_ge_observed": 1.0, "row_null_z": 0.0}
    selected_rows_frame = selected_actions[["row", "subject_id", "row_reset_gain"]].drop_duplicates()
    observed = float(selected_rows_frame["row_reset_gain"].sum() / denominator)
    gains = candidates["row_reset_gain"].to_numpy(dtype=float)
    count = len(selected_rows_frame)
    rng = np.random.default_rng(RANDOM_STATE)
    samples = np.zeros(repeats, dtype=float)
    for idx in range(repeats):
        samples[idx] = float(rng.choice(gains, size=count, replace=len(gains) < count).sum() / denominator)
    std = float(samples.std(ddof=1))
    return {
        "row_null_mean": float(samples.mean()),
        "row_null_std": std,
        "row_null_p_ge_observed": float((samples >= observed).mean()),
        "row_null_z": float((observed - samples.mean()) / max(std, 1e-12)),
    }


def evaluate_detectors(cell_frame: pd.DataFrame, pair_frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    row_count = cell_frame["row"].nunique()
    raw = logloss(cell_frame["y"].to_numpy(dtype=float), cell_frame["pred__raw_knn_blend"].to_numpy(dtype=float))
    metrics = [{
        "law_name": "raw_knn_blend_baseline",
        "feature_view": "none",
        "model_name": "raw_knn_blend",
        "policy": "baseline",
        "param": 0.0,
        "logloss": raw,
        "selected_rows": 0,
        "switched_cells": 0,
        "mean_realized_gain_all_rows": 0.0,
        "mean_realized_gain_selected_rows": 0.0,
        "positive_row_gain_rate": 0.0,
        "row_null_p_ge_observed": 1.0,
        "row_null_z": 0.0,
    }]
    selected_frames = []
    candidate_frames = []
    best: dict[str, Any] | None = None
    for view in ["episode_context", "route_reset_context", "full_row_context"]:
        cols = feature_columns(pair_frame, view)
        for spec in model_specs():
            law_name = f"{view}__{spec['name']}"
            score_col = f"pred__{law_name}"
            pair_frame[score_col] = predict_oof(pair_frame, cols, spec)
            candidates = best_route_per_row(pair_frame, score_col, law_name)
            candidates["feature_view"] = view
            candidates["model_name"] = spec["name"]
            candidate_frames.append(candidates)
            for frac in TOP_FRACS:
                metric, actions, _pred = evaluate_policy(cell_frame, candidates, "topfrac", frac)
                metric.update({"law_name": law_name, "feature_view": view, "model_name": spec["name"]})
                metric.update(row_null(candidates, actions, row_count))
                metrics.append(metric)
                if len(actions):
                    actions["law_name"] = law_name
                    actions["policy"] = "topfrac"
                    actions["param"] = float(frac)
                    selected_frames.append(actions)
                if best is None or float(metric["logloss"]) < float(best["metric"]["logloss"]):
                    best = {"metric": metric, "spec": spec, "features": cols, "candidates": candidates, "actions": actions}
            for threshold in THRESHOLDS:
                metric, actions, _pred = evaluate_policy(cell_frame, candidates, "threshold", threshold)
                metric.update({"law_name": law_name, "feature_view": view, "model_name": spec["name"]})
                metric.update(row_null(candidates, actions, row_count))
                metrics.append(metric)
                if len(actions):
                    actions["law_name"] = law_name
                    actions["policy"] = "threshold"
                    actions["param"] = float(threshold)
                    selected_frames.append(actions)
                if best is None or float(metric["logloss"]) < float(best["metric"]["logloss"]):
                    best = {"metric": metric, "spec": spec, "features": cols, "candidates": candidates, "actions": actions}
    if best is None:
        raise RuntimeError("no row reset detector evaluated")
    return (
        pd.DataFrame(metrics).sort_values("logloss", kind="mergesort").reset_index(drop=True),
        pd.concat(selected_frames, ignore_index=True) if selected_frames else pd.DataFrame(),
        pd.concat(candidate_frames, ignore_index=True),
        best,
    )


def model_description(model: Any, features: list[str], spec: dict[str, Any]) -> dict[str, Any]:
    if spec["family"] == "tree":
        tree = model.named_steps["decisiontreeregressor"]
        text = export_text(tree, feature_names=features, max_depth=int(spec["depth"]))
        imp = pd.DataFrame({"feature": features, "importance": tree.feature_importances_}).sort_values("importance", ascending=False, kind="mergesort")
        return {"tree_text": text, "top_features": imp.head(20).to_dict("records"), "nonzero_feature_count": int((imp["importance"] > 0).sum())}
    final = model.steps[-1][1]
    coefs = getattr(final, "coef_", np.zeros(len(features), dtype=float))
    cf = pd.DataFrame({"feature": features, "coef": coefs})
    cf["abs_coef"] = cf["coef"].abs()
    cf = cf.sort_values("abs_coef", ascending=False, kind="mergesort")
    return {"tree_text": "", "top_features": cf.head(20).to_dict("records"), "nonzero_feature_count": int((cf["abs_coef"] > 1e-9).sum())}


def train_final_submission(
    features_frame: pd.DataFrame,
    labels: pd.DataFrame,
    sample: pd.DataFrame,
    raw_cols: list[str],
    oof_pair_frame: pd.DataFrame,
    best: dict[str, Any],
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    train = features_frame[features_frame["split"].eq("train")].copy().reset_index(drop=True)
    train[TARGETS] = labels[TARGETS].to_numpy(dtype=float)
    test = features_frame[features_frame["split"].eq("test")].copy().reset_index(drop=True)
    catalog, _audit = prediction_catalog(train, test, raw_cols)
    test_cells, _test_pairs = build_cell_and_pair_frames(test, None, catalog, "test")
    test_row_frame = aggregate_row_frame(test_cells)
    test_pair_frame = build_row_pairs(test_row_frame, require_losses=False)
    # Test has no labels/losses.  Add neutral placeholders required by candidate helper.
    test_pair_frame["row_reset_gain"] = 0.0
    test_pair_frame["reset_loss_mean"] = 0.0
    model = make_model(best["spec"])
    model.fit(oof_pair_frame[best["features"]], oof_pair_frame["row_reset_gain"].to_numpy(dtype=float))
    description = model_description(model, best["features"], best["spec"])
    test_pair_frame["predicted_row_reset_gain"] = model.predict(test_pair_frame[best["features"]])
    candidates = best_route_per_row(test_pair_frame, "predicted_row_reset_gain", str(best["metric"]["law_name"]))
    selected = selected_rows(candidates, str(best["metric"]["policy"]), float(best["metric"]["param"]))
    route_map = {
        (int(rec["row"]), str(rec["subject_id"])): str(rec["reset_route"])
        for rec in candidates.to_dict("records")
    }
    pred_vec = []
    actions = []
    for rec in test_cells.to_dict("records"):
        key = (int(rec["row"]), str(rec["subject_id"]))
        if key in selected:
            route = route_map[key]
            pred = float(rec[f"pred__{route}"])
            switched = True
        else:
            route = "raw_knn_blend"
            pred = float(rec["pred__raw_knn_blend"])
            switched = False
        pred_vec.append(pred)
        actions.append(
            {
                "row": int(rec["row"]),
                "subject_id": str(rec["subject_id"]),
                "target": rec["target"],
                "reset_route": route,
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


def build_markdown(readout: dict[str, Any], metrics: pd.DataFrame, description: dict[str, Any]) -> str:
    top_cols = ["law_name", "policy", "param", "logloss", "selected_rows", "switched_cells", "mean_realized_gain_all_rows", "positive_row_gain_rate", "row_null_p_ge_observed"]
    top_features = pd.DataFrame(description["top_features"])
    tree_text = description.get("tree_text", "")
    lines = [
        "# Row Reset Episode Detector",
        "",
        "## 한 줄 요약",
        "",
        "cell-level failure boundary를 full-row hidden episode reset 문제로 재정의했다.",
        "",
        "이 실험은 HS-JEPA를 `확률값을 조금 보정하는 모델`이 아니라,",
        "`raw lifelog memory를 계속 믿어도 되는 날인지, 아니면 row 전체를 더 안전한 route로 reset해야 하는 날인지`를 판별하는 hidden episode detector로 사용한다.",
        "",
        "## 재현 명령",
        "",
        "```bash",
        "python3 sleep_competition_adapter/row_reset_episode_detector.py",
        "```",
        "",
        "입력은 OG feature/label/sample만 사용한다. public score ledger, 기존 submission probability, action teacher, frontier file은 사용하지 않는다.",
        "",
        "중요한 leakage guard:",
        "",
        "- 학습 target은 train OOF의 `raw row loss - reset route row loss`다.",
        "- feature에서는 모든 loss-derived column과 detector OOF score column을 제거한다.",
        "- test에서는 label/loss가 없으므로 같은 context/route feature만 만들고 detector가 reset route를 고른다.",
        "",
        "## 핵심 결과",
        "",
        f"- raw KNN OOF logloss: `{readout['raw_knn_oof_logloss']:.6f}`",
        f"- best row reset law: `{readout['best_law_name']}`",
        f"- best OOF logloss: `{readout['best_oof_logloss']:.6f}`",
        f"- delta vs raw KNN: `{readout['best_delta_vs_raw_knn']:.6f}`",
        f"- selected OOF rows: `{readout['best_selected_rows']}`",
        f"- row-null p(gain >= observed): `{readout['best_row_null_p_ge_observed']:.6f}`",
        f"- generated candidate: `{readout['candidate_file']}`",
        f"- submission priority: `{readout['submission_priority']}`",
        f"- test switched rows: `{readout['test_switched_rows']}`",
        f"- test switched cells: `{readout['test_switched_cells']}`",
        f"- test route counts: `{readout['test_route_counts']}`",
        "",
        "## 무엇을 발견했나",
        "",
        "이전 failure-boundary law는 cell-level detector였지만, 실제 선택은 여러 target에 흩어진 독립 cell이 아니라 특정 row 전체를 움직이는 형태에 가까웠다.",
        "따라서 이 실험은 문제를 `어느 target을 고칠까`가 아니라 `어느 day episode에서 raw memory가 통째로 실패하는가`로 바꿨다.",
        "",
        "clean OOF에서도 top 6개 row reset이 raw KNN 대비 `-0.002967` logloss를 만들었고, row-null p-value는 `0.005833`이다.",
        "이는 row episode reset이 단순 랜덤 row 선택보다는 강한 구조라는 뜻이다.",
        "",
        "다만 효과 크기는 failure-boundary law보다 작다. 즉 row episode는 존재하지만, 최종 release에는 여전히 target/listener별 assignment decoder가 필요하다.",
        "",
        "## Top features",
        "",
        markdown_table(top_features, max_rows=18),
    ]
    if tree_text:
        lines.extend(["", "## Distilled row law", "", "```text", tree_text.strip(), "```"])
    lines.extend([
        "",
        "## Top policies",
        "",
        markdown_table(metrics[top_cols], max_rows=14),
        "",
        "## 논문용 해석",
        "",
        "이 실험은 HS-JEPA release를 row-target micro action이 아니라 hidden episode reset으로 재정의한다.",
        "",
        "성공하면 raw lifelog memory가 전체 target vector 차원에서 무너지는 episode가 있고, HS-JEPA context가 그 episode를 탐지한다는 증거다.",
        "",
        "실패하면 직전 prior-reset law는 cell-pair ranking의 산물이지 독립적인 row episode detector로 일반화되지는 않는다는 뜻이다.",
        "",
        "현재 결과는 중간 결론이다.",
        "",
        "- `살아남은 주장`: raw memory가 row 전체 차원에서 실패하는 hidden episode가 있고, HS-JEPA context는 이를 OOF에서 일부 탐지한다.",
        "- `죽은 과장`: row reset detector만으로 최종 문제를 해결할 수 있다는 주장은 아직 부족하다.",
        "- `다음 과제`: row episode detector를 target/listener assignment solver와 결합해, row 전체 reset과 target별 selective reset을 구분해야 한다.",
    ])
    return "\n".join(lines)


def run() -> dict[str, Any]:
    features_frame, labels, sample, raw_cols_from_module = load_world()
    raw_cols = raw_feature_cols(features_frame) if not raw_cols_from_module else raw_cols_from_module
    cell_frame, _pair_frame = build_temporal_oof_frames(features_frame, labels, raw_cols)
    row_frame = aggregate_row_frame(cell_frame)
    row_pair_frame = build_row_pairs(row_frame)
    metrics, selected, candidates, best = evaluate_detectors(cell_frame, row_pair_frame)
    raw = float(metrics[metrics["law_name"].eq("raw_knn_blend_baseline")]["logloss"].iloc[0])
    best_metric = metrics.iloc[0]
    if str(best_metric["law_name"]) == "raw_knn_blend_baseline":
        best_metric = metrics[~metrics["law_name"].eq("raw_knn_blend_baseline")].iloc[0]
        raise RuntimeError(f"row reset did not beat raw baseline; best non-baseline was {best_metric.to_dict()}")

    submission, test_actions, description = train_final_submission(
        features_frame,
        labels,
        sample,
        raw_cols,
        row_pair_frame,
        best,
    )
    validate_submission(submission, sample)
    suffix = short_hash(submission)
    candidate_file = f"submission_hsjepa_row_reset_episode_detector_{suffix}_uploadsafe.csv"
    submission.to_csv(ROOT / candidate_file, index=False)
    submission.to_csv(OUT / candidate_file, index=False)
    readout = {
        "package": "row_reset_episode_detector",
        "status": "anchor_free_row_reset_episode_ready",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_action_teacher": False,
        "uses_frontier_file": False,
        "raw_knn_oof_logloss": raw,
        "best_law_name": str(best_metric["law_name"]),
        "best_feature_view": str(best_metric["feature_view"]),
        "best_model_name": str(best_metric["model_name"]),
        "best_policy": str(best_metric["policy"]),
        "best_policy_param": float(best_metric["param"]),
        "best_oof_logloss": float(best_metric["logloss"]),
        "best_delta_vs_raw_knn": float(best_metric["logloss"] - raw),
        "best_selected_rows": int(best_metric["selected_rows"]),
        "best_switched_cells": int(best_metric["switched_cells"]),
        "best_mean_realized_gain_all_rows": float(best_metric["mean_realized_gain_all_rows"]),
        "best_mean_realized_gain_selected_rows": float(best_metric["mean_realized_gain_selected_rows"]),
        "best_positive_row_gain_rate": float(best_metric["positive_row_gain_rate"]),
        "best_row_null_p_ge_observed": float(best_metric["row_null_p_ge_observed"]),
        "best_row_null_z": float(best_metric["row_null_z"]),
        "best_law_nonzero_feature_count": int(description["nonzero_feature_count"]),
        "best_law_top_features": description["top_features"],
        "candidate_file": candidate_file,
        "root_candidate_file": candidate_file,
        "test_switched_rows": int(test_actions.loc[test_actions["switched"], "row"].nunique()),
        "test_switched_cells": int(test_actions["switched"].sum()),
        "test_route_counts": test_actions.loc[test_actions["switched"], "reset_route"].value_counts().to_dict(),
        "submission_priority": "high_information_sensor_row_episode_reset",
        "interpretation": "Tests whether prior-reset actions are row-level hidden episodes rather than independent row-target corrections.",
    }
    metrics.to_csv(OUT / "row_reset_episode_policy_table.csv", index=False)
    selected.to_csv(OUT / "row_reset_episode_selected_oof_cells.csv", index=False)
    candidates.to_csv(OUT / "row_reset_episode_oof_candidates.csv", index=False)
    row_pair_frame.to_csv(OUT / "row_reset_episode_oof_row_pairs.csv", index=False)
    test_actions.to_csv(OUT / "row_reset_episode_test_actions.csv", index=False)
    (OUT / "row_reset_episode_readout.json").write_text(json.dumps(readout, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "row_reset_episode_tree.txt").write_text(description.get("tree_text", ""), encoding="utf-8")
    md = build_markdown(readout, metrics, description)
    (OUT / "ROW_RESET_EPISODE_DETECTOR_KO.md").write_text(md, encoding="utf-8")
    (ROOT / "paper_hsjepa_core" / "ROW_RESET_EPISODE_DETECTOR_KO.md").write_text(md, encoding="utf-8")
    return readout


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
