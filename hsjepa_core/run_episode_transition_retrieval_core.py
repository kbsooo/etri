#!/usr/bin/env python3
"""HS-JEPA next-episode transition retrieval core experiment.

This is a label-free world-model experiment.  It asks a direct JEPA question:

    Can visible current human-life context predict the hidden representation of
    the next episode well enough to retrieve that episode among alternatives?

Labels are used only in a frozen downstream probe after the transition
representation is built.  Public LB, prior submissions, and proprietary
embeddings are not used.
"""

from __future__ import annotations

import json
import math
import sys
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import average_precision_score, log_loss, roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hsjepa_core.human_state_world_model import finite_frame  # noqa: E402
from hsjepa_core.run_human_state_world_model_core import (  # noqa: E402
    make_views,
    subject_relative_frame,
)
from hsjepa_core.run_lifelog_core_state_evidence import (  # noqa: E402
    TARGETS,
    format_float,
    load_frames,
    markdown_table,
    safe_auc,
)


OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "episode_transition_retrieval_core"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "EPISODE_TRANSITION_RETRIEVAL_CORE_KO.md"
RANDOM_SEED = 20260614
LATENT_DIMS = 12
RIDGE_ALPHA = 18.0

warnings.filterwarnings("ignore", message="Skipping features without any observed values")


@dataclass(frozen=True)
class TransitionFold:
    split: str
    fold: int
    train_pair_pos: np.ndarray
    val_pair_pos: np.ndarray


def json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [json_safe(item) for item in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        if not math.isfinite(float(value)):
            return None
        return float(value)
    return value


def build_transition_pairs(frame: pd.DataFrame, row_mask: np.ndarray | None = None) -> pd.DataFrame:
    """Return current->next row pairs within subject chronological order."""

    rows = frame[["subject_id", "lifelog_date", "split"]].copy()
    rows["_row"] = np.arange(len(frame))
    rows["lifelog_date"] = pd.to_datetime(rows["lifelog_date"], errors="coerce")
    if row_mask is not None:
        rows = rows.loc[row_mask].copy()
    rows = rows.sort_values(["subject_id", "lifelog_date", "_row"]).reset_index(drop=True)
    rows["_next_row"] = rows.groupby("subject_id", observed=True)["_row"].shift(-1)
    pairs = rows[np.isfinite(rows["_next_row"])].copy()
    pairs["current_row"] = pairs["_row"].astype(int)
    pairs["next_row"] = pairs["_next_row"].astype(int)
    pairs = pairs[["subject_id", "split", "current_row", "next_row"]].reset_index(drop=True)
    pairs["pair_pos"] = np.arange(len(pairs))
    return pairs


def make_subject_transition_folds(pairs: pd.DataFrame) -> list[TransitionFold]:
    groups = pairs["subject_id"].astype(str).to_numpy()
    splitter = GroupKFold(n_splits=max(2, min(5, len(np.unique(groups)))))
    folds: list[TransitionFold] = []
    for fold, (tr, va) in enumerate(splitter.split(pairs, groups=groups)):
        folds.append(TransitionFold("subject_heldout", fold, tr, va))
    return folds


def make_chronological_transition_folds(frame: pd.DataFrame, pairs: pd.DataFrame) -> list[TransitionFold]:
    val_pos: list[int] = []
    for _, part in pairs.groupby("subject_id", observed=True):
        ordered = part.copy()
        current_dates = pd.to_datetime(frame.iloc[ordered["current_row"]]["lifelog_date"].to_numpy(), errors="coerce")
        ordered = ordered.assign(_date=current_dates).sort_values(["_date", "current_row"])
        if len(ordered) < 4:
            continue
        cut = max(1, int(math.floor(len(ordered) * 0.70)))
        val_pos.extend(ordered.iloc[cut:]["pair_pos"].astype(int).tolist())
    val = np.array(sorted(set(val_pos)), dtype=int)
    train = np.array([pos for pos in pairs["pair_pos"].astype(int).tolist() if pos not in set(val)], dtype=int)
    return [TransitionFold("chronological_holdout", 0, train, val)]


def make_transition_views(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, list[str], list[str]]:
    views = make_views(frame)
    raw_cols = sorted({col for view in views for col in view.columns})
    if len(raw_cols) < 4:
        raise ValueError("not enough raw semantic view columns for transition retrieval")
    relative = subject_relative_frame(frame, raw_cols)
    calendar_cols = [col for col in ["dayofweek", "is_weekend", "dayofmonth", "month_start_proximity", "month_end"] if col in raw_cols]
    rhythm_conditioned = relative.copy()
    for col in calendar_cols:
        rhythm_conditioned[col] = frame[col]
    return frame, relative, rhythm_conditioned, raw_cols, calendar_cols


def encode_target_space(target_frame: pd.DataFrame, raw_cols: list[str], train_rows: np.ndarray) -> tuple[np.ndarray, Any]:
    n_components = max(2, min(LATENT_DIMS, len(raw_cols), len(train_rows) - 1))
    encoder = make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(),
        PCA(n_components=n_components, random_state=RANDOM_SEED),
    )
    encoder.fit(finite_frame(target_frame.iloc[train_rows], raw_cols))
    target_state = np.asarray(encoder.transform(finite_frame(target_frame, raw_cols)), dtype=np.float64)
    return target_state, encoder


def fit_predict_latent(
    context_frame: pd.DataFrame,
    context_cols: list[str],
    target_state: np.ndarray,
    current_rows: np.ndarray,
    next_rows: np.ndarray,
    train_pair_pos: np.ndarray,
    val_pair_pos: np.ndarray,
) -> np.ndarray:
    train_current = current_rows[train_pair_pos]
    train_next = next_rows[train_pair_pos]
    val_current = current_rows[val_pair_pos]
    model = make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(),
        Ridge(alpha=RIDGE_ALPHA),
    )
    model.fit(finite_frame(context_frame.iloc[train_current], context_cols), target_state[train_next])
    return np.asarray(model.predict(finite_frame(context_frame.iloc[val_current], context_cols)), dtype=np.float64)


def fold_subject_center_prediction(
    pairs: pd.DataFrame,
    target_state: np.ndarray,
    next_rows: np.ndarray,
    train_pair_pos: np.ndarray,
    val_pair_pos: np.ndarray,
) -> np.ndarray:
    train_subjects = pairs.iloc[train_pair_pos]["subject_id"].astype(str).to_numpy()
    train_next = next_rows[train_pair_pos]
    centers = {
        subject: target_state[train_next[train_subjects == subject]].mean(axis=0)
        for subject in sorted(set(train_subjects))
    }
    global_center = target_state[train_next].mean(axis=0)
    val_subjects = pairs.iloc[val_pair_pos]["subject_id"].astype(str).to_numpy()
    return np.vstack([centers.get(subject, global_center) for subject in val_subjects])


def retrieval_scores(y_true: np.ndarray, predictions: dict[str, np.ndarray]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    n = len(y_true)
    if n <= 1:
        return pd.DataFrame(rows)
    true_norm = y_true / np.maximum(np.linalg.norm(y_true, axis=1, keepdims=True), 1e-12)
    for method, pred in predictions.items():
        pred_norm = pred / np.maximum(np.linalg.norm(pred, axis=1, keepdims=True), 1e-12)
        distances = 1.0 - pred_norm @ true_norm.T
        ranks = []
        for idx in range(n):
            true_dist = distances[idx, idx]
            ranks.append(1 + int(np.sum(distances[idx] < true_dist - 1e-12)))
        rank_arr = np.asarray(ranks, dtype=np.float64)
        rows.append(
            {
                "method": method,
                "candidate_count": int(n),
                "top1_accuracy": float(np.mean(rank_arr <= 1)),
                "top3_recall": float(np.mean(rank_arr <= min(3, n))),
                "top5_recall": float(np.mean(rank_arr <= min(5, n))),
                "mean_rank": float(rank_arr.mean()),
                "median_rank": float(np.median(rank_arr)),
                "mean_rank_pct": float(np.mean((rank_arr - 1) / max(1, n - 1))),
                "random_top1": float(1.0 / n),
                "random_top5": float(min(5, n) / n),
                "random_mean_rank_pct": 0.5,
                "lift_top1_vs_random": float(np.mean(rank_arr <= 1) - 1.0 / n),
                "lift_top5_vs_random": float(np.mean(rank_arr <= min(5, n)) - min(5, n) / n),
                "lift_rank_pct_vs_random": float(0.5 - np.mean((rank_arr - 1) / max(1, n - 1))),
            }
        )
    return pd.DataFrame(rows)


def evaluate_transition_retrieval(
    frame: pd.DataFrame,
    relative: pd.DataFrame,
    rhythm_conditioned: pd.DataFrame,
    raw_cols: list[str],
    calendar_cols: list[str],
    pairs: pd.DataFrame,
    folds: list[TransitionFold],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    metric_rows: list[pd.DataFrame] = []
    state_rows: list[dict[str, Any]] = []
    current_rows = pairs["current_row"].to_numpy(dtype=int)
    next_rows = pairs["next_row"].to_numpy(dtype=int)

    for fold in folds:
        if len(fold.val_pair_pos) < 2 or len(fold.train_pair_pos) < 4:
            continue
        target_state, _ = encode_target_space(relative, raw_cols, next_rows[fold.train_pair_pos])
        val_next = next_rows[fold.val_pair_pos]
        val_current = current_rows[fold.val_pair_pos]
        y_true = target_state[val_next]

        global_center = np.tile(target_state[next_rows[fold.train_pair_pos]].mean(axis=0), (len(fold.val_pair_pos), 1))
        current_identity = target_state[val_current]
        subject_center = fold_subject_center_prediction(pairs, target_state, next_rows, fold.train_pair_pos, fold.val_pair_pos)
        predictions: dict[str, np.ndarray] = {
            "global_next_center": global_center,
            "current_episode_identity": current_identity,
            "subject_next_center": subject_center,
        }
        if calendar_cols:
            predictions["calendar_to_next_state"] = fit_predict_latent(
                frame,
                calendar_cols,
                target_state,
                current_rows,
                next_rows,
                fold.train_pair_pos,
                fold.val_pair_pos,
            )
        predictions["absolute_context_to_next_state"] = fit_predict_latent(
            frame,
            raw_cols,
            target_state,
            current_rows,
            next_rows,
            fold.train_pair_pos,
            fold.val_pair_pos,
        )
        predictions["subject_relative_context_to_next_state"] = fit_predict_latent(
            relative,
            raw_cols,
            target_state,
            current_rows,
            next_rows,
            fold.train_pair_pos,
            fold.val_pair_pos,
        )
        predictions["rhythm_conditioned_subject_relative_to_next_state"] = fit_predict_latent(
            rhythm_conditioned,
            raw_cols,
            target_state,
            current_rows,
            next_rows,
            fold.train_pair_pos,
            fold.val_pair_pos,
        )

        metrics = retrieval_scores(y_true, predictions)
        metrics.insert(0, "fold", fold.fold)
        metrics.insert(0, "split", fold.split)
        metric_rows.append(metrics)

        for pos, pair_pos in enumerate(fold.val_pair_pos):
            rec = {
                "split": fold.split,
                "fold": int(fold.fold),
                "pair_pos": int(pair_pos),
                "current_row": int(val_current[pos]),
                "next_row": int(val_next[pos]),
                "subject_id": str(pairs.iloc[pair_pos]["subject_id"]),
            }
            for method, pred in predictions.items():
                for comp, value in enumerate(pred[pos]):
                    rec[f"{method}_c{comp + 1}"] = float(value)
            state_rows.append(rec)

    return pd.concat(metric_rows, ignore_index=True, sort=False), pd.DataFrame(state_rows)


def aggregate_retrieval(metrics: pd.DataFrame) -> pd.DataFrame:
    return (
        metrics.groupby(["split", "method"], observed=True)
        .agg(
            folds=("fold", "nunique"),
            mean_candidate_count=("candidate_count", "mean"),
            top1_accuracy=("top1_accuracy", "mean"),
            top3_recall=("top3_recall", "mean"),
            top5_recall=("top5_recall", "mean"),
            mean_rank_pct=("mean_rank_pct", "mean"),
            lift_top1_vs_random=("lift_top1_vs_random", "mean"),
            lift_top5_vs_random=("lift_top5_vs_random", "mean"),
            lift_rank_pct_vs_random=("lift_rank_pct_vs_random", "mean"),
        )
        .reset_index()
    )


def make_probe(feature_count: int) -> Any:
    return make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(),
        LogisticRegression(C=0.30, max_iter=5000, solver="lbfgs"),
    )


def safe_average_precision(y_true: np.ndarray, score: np.ndarray) -> float | None:
    if len(np.unique(y_true)) < 2:
        return None
    return float(average_precision_score(y_true, score))


def evaluate_next_label_probe(
    frame: pd.DataFrame,
    labels: pd.DataFrame,
    relative: pd.DataFrame,
    rhythm_conditioned: pd.DataFrame,
    raw_cols: list[str],
    calendar_cols: list[str],
) -> pd.DataFrame:
    """Frozen linear probe: transition representation -> next-row labels.

    The world-model target remains label-free.  Labels are only used here to
    test whether the predicted next representation linearizes the next
    episode's Q/S state under the same subject-heldout and chronological splits.
    """

    train_mask = frame["split"].eq("train").to_numpy()
    train_pairs = build_transition_pairs(frame, train_mask)
    if train_pairs.empty:
        return pd.DataFrame()
    folds = make_subject_transition_folds(train_pairs) + make_chronological_transition_folds(frame, train_pairs)
    current_rows = train_pairs["current_row"].to_numpy(dtype=int)
    next_rows = train_pairs["next_row"].to_numpy(dtype=int)
    y_labels = labels[TARGETS].astype(int).reset_index(drop=True)
    rows: list[dict[str, Any]] = []

    for fold in folds:
        if len(fold.val_pair_pos) < 2 or len(fold.train_pair_pos) < 4:
            continue
        target_state, _ = encode_target_space(relative, raw_cols, next_rows[fold.train_pair_pos])
        feature_map: dict[str, tuple[np.ndarray, np.ndarray]] = {}
        feature_map["current_episode_identity"] = (
            target_state[current_rows[fold.train_pair_pos]],
            target_state[current_rows[fold.val_pair_pos]],
        )
        feature_map["subject_next_center"] = (
            fold_subject_center_prediction(train_pairs, target_state, next_rows, fold.train_pair_pos, fold.train_pair_pos),
            fold_subject_center_prediction(train_pairs, target_state, next_rows, fold.train_pair_pos, fold.val_pair_pos),
        )
        if calendar_cols:
            feature_map["calendar_to_next_state"] = (
                fit_predict_latent(frame, calendar_cols, target_state, current_rows, next_rows, fold.train_pair_pos, fold.train_pair_pos),
                fit_predict_latent(frame, calendar_cols, target_state, current_rows, next_rows, fold.train_pair_pos, fold.val_pair_pos),
            )
        feature_map["absolute_context_to_next_state"] = (
            fit_predict_latent(frame, raw_cols, target_state, current_rows, next_rows, fold.train_pair_pos, fold.train_pair_pos),
            fit_predict_latent(frame, raw_cols, target_state, current_rows, next_rows, fold.train_pair_pos, fold.val_pair_pos),
        )
        feature_map["subject_relative_context_to_next_state"] = (
            fit_predict_latent(relative, raw_cols, target_state, current_rows, next_rows, fold.train_pair_pos, fold.train_pair_pos),
            fit_predict_latent(relative, raw_cols, target_state, current_rows, next_rows, fold.train_pair_pos, fold.val_pair_pos),
        )
        feature_map["rhythm_conditioned_subject_relative_to_next_state"] = (
            fit_predict_latent(
                rhythm_conditioned,
                raw_cols,
                target_state,
                current_rows,
                next_rows,
                fold.train_pair_pos,
                fold.train_pair_pos,
            ),
            fit_predict_latent(
                rhythm_conditioned,
                raw_cols,
                target_state,
                current_rows,
                next_rows,
                fold.train_pair_pos,
                fold.val_pair_pos,
            ),
        )

        train_next = next_rows[fold.train_pair_pos]
        val_next = next_rows[fold.val_pair_pos]
        for feature_set, (x_train, x_val) in feature_map.items():
            losses = []
            aucs = []
            aps = []
            for target in TARGETS:
                y_train = y_labels.iloc[train_next][target].to_numpy(dtype=int)
                y_val = y_labels.iloc[val_next][target].to_numpy(dtype=int)
                prior = float(np.clip(y_train.mean(), 1e-5, 1 - 1e-5))
                if len(np.unique(y_train)) < 2:
                    pred = np.full(len(y_val), prior, dtype=np.float64)
                else:
                    probe = make_probe(x_train.shape[1])
                    probe.fit(x_train, y_train)
                    pred = np.clip(probe.predict_proba(x_val)[:, 1], 1e-5, 1 - 1e-5)
                    # Fixed low-trust readout to prevent tiny-sample overconfidence.
                    pred = np.clip(prior + 0.10 * (pred - prior), 1e-5, 1 - 1e-5)
                loss = float(log_loss(y_val, pred, labels=[0, 1]))
                auc = safe_auc(y_val, pred)
                ap = safe_average_precision(y_val, pred)
                losses.append(loss)
                if auc is not None:
                    aucs.append(auc)
                if ap is not None:
                    aps.append(ap)
                rows.append(
                    {
                        "split": fold.split,
                        "fold": int(fold.fold),
                        "feature_set": feature_set,
                        "target": target,
                        "logloss": loss,
                        "auc": auc,
                        "average_precision": ap,
                        "positive_rate": float(y_val.mean()),
                        "evaluated_rows": int(len(y_val)),
                    }
                )
            rows.append(
                {
                    "split": fold.split,
                    "fold": int(fold.fold),
                    "feature_set": feature_set,
                    "target": "all",
                    "logloss": float(np.mean(losses)),
                    "auc": float(np.nanmean(aucs)) if aucs else None,
                    "average_precision": float(np.nanmean(aps)) if aps else None,
                    "positive_rate": None,
                    "evaluated_rows": int(len(val_next)),
                }
            )
    return pd.DataFrame(rows)


def aggregate_label_probe(metrics: pd.DataFrame) -> pd.DataFrame:
    if metrics.empty:
        return metrics
    return (
        metrics[metrics["target"].eq("all")]
        .groupby(["split", "feature_set"], observed=True)
        .agg(
            folds=("fold", "nunique"),
            logloss=("logloss", "mean"),
            auc=("auc", "mean"),
            average_precision=("average_precision", "mean"),
            evaluated_rows=("evaluated_rows", "sum"),
        )
        .reset_index()
    )


def summarize(retrieval: pd.DataFrame, label_probe: pd.DataFrame) -> dict[str, Any]:
    subject = retrieval[retrieval["split"].eq("subject_heldout")].copy()
    chrono = retrieval[retrieval["split"].eq("chronological_holdout")].copy()
    best_subject = subject.sort_values(["lift_rank_pct_vs_random", "top5_recall"], ascending=False).head(1)
    best_chrono = chrono.sort_values(["lift_rank_pct_vs_random", "top5_recall"], ascending=False).head(1)
    predicted = subject[subject["method"].eq("subject_relative_context_to_next_state")]
    rhythm_predicted = subject[subject["method"].eq("rhythm_conditioned_subject_relative_to_next_state")]
    persistence = subject[subject["method"].eq("current_episode_identity")]
    label_agg = aggregate_label_probe(label_probe)
    label_subject = label_agg[label_agg["split"].eq("subject_heldout")] if not label_agg.empty else label_agg
    best_label = label_subject.sort_values("logloss").head(1) if not label_subject.empty else label_subject
    pred_label = label_subject[label_subject["feature_set"].eq("subject_relative_context_to_next_state")] if not label_subject.empty else label_subject
    return {
        "package": "episode_transition_retrieval_core",
        "status": "episode_transition_retrieval_core_ready",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "uses_label_as_pretext_target": False,
        "core_adapter_boundary": "labels appear only in frozen next-label probe; retrieval pretext is label-free",
        "latent_dims": LATENT_DIMS,
        "ridge_alpha": RIDGE_ALPHA,
        "subject_best_retrieval": None if best_subject.empty else best_subject.iloc[0].to_dict(),
        "chronological_best_retrieval": None if best_chrono.empty else best_chrono.iloc[0].to_dict(),
        "subject_relative_predicted_retrieval": None if predicted.empty else predicted.iloc[0].to_dict(),
        "subject_rhythm_conditioned_predicted_retrieval": None
        if rhythm_predicted.empty
        else rhythm_predicted.iloc[0].to_dict(),
        "subject_persistence_retrieval": None if persistence.empty else persistence.iloc[0].to_dict(),
        "subject_predicted_rank_lift_minus_persistence": None
        if predicted.empty or persistence.empty
        else float(predicted["lift_rank_pct_vs_random"].iloc[0] - persistence["lift_rank_pct_vs_random"].iloc[0]),
        "subject_best_next_label_probe": None if best_label.empty else best_label.iloc[0].to_dict(),
        "subject_predicted_next_label_probe": None if pred_label.empty else pred_label.iloc[0].to_dict(),
    }


def build_markdown(summary: dict[str, Any], retrieval: pd.DataFrame, label_probe: pd.DataFrame) -> str:
    subject_table = retrieval[retrieval["split"].eq("subject_heldout")].sort_values(
        ["lift_rank_pct_vs_random", "top5_recall"],
        ascending=False,
    )
    chrono_table = retrieval[retrieval["split"].eq("chronological_holdout")].sort_values(
        ["lift_rank_pct_vs_random", "top5_recall"],
        ascending=False,
    )
    label_agg = aggregate_label_probe(label_probe)
    label_subject = (
        label_agg[label_agg["split"].eq("subject_heldout")].sort_values("logloss")
        if not label_agg.empty
        else label_agg
    )
    label_chrono = (
        label_agg[label_agg["split"].eq("chronological_holdout")].sort_values("logloss")
        if not label_agg.empty
        else label_agg
    )
    predicted = summary.get("subject_relative_predicted_retrieval") or {}
    rhythm_predicted = summary.get("subject_rhythm_conditioned_predicted_retrieval") or {}
    persistence = summary.get("subject_persistence_retrieval") or {}
    best_subject = summary.get("subject_best_retrieval") or {}
    if best_subject.get("method") == "rhythm_conditioned_subject_relative_to_next_state" and best_subject.get("lift_rank_pct_vs_random", 0) > 0.10:
        verdict = "transition_retrieval_core_positive"
    elif best_subject.get("method") == "calendar_to_next_state":
        verdict = "transition_retrieval_rhythm_dominant_boundary"
    elif predicted and predicted.get("lift_rank_pct_vs_random", 0) > 0:
        verdict = "transition_retrieval_weak_positive_boundary"
    else:
        verdict = "transition_retrieval_negative_boundary"
    return f"""# Episode Transition Retrieval Core

## 한 줄 요약

이 실험은 HS-JEPA를 label predictor가 아니라 `다음 인간 생활 episode를 예측하는 world model`로 검증한다.

```text
visible current episode context
  -> predict hidden next-episode representation
  -> retrieve the actual next episode among candidate episodes
  -> freeze representation
  -> low-trust next-label probe
```

## 판정

- verdict: `{verdict}`
- public LB ledger 사용: `{summary["uses_public_score_ledger"]}`
- prior submission probability 사용: `{summary["uses_prior_submission_probabilities"]}`
- proprietary embedding API 사용: `{summary["uses_proprietary_embedding_api"]}`
- label을 pretext target으로 사용: `{summary["uses_label_as_pretext_target"]}`

## 왜 이것이 HS-JEPA Core인가

I-JEPA식 질문을 lifelog에 그대로 옮기면 다음과 같다.

```text
현재의 보이는 human-life context만 보고,
보이지 않는 다음 episode representation을 맞힐 수 있는가?
```

이 실험의 target은 Q/S label이나 submission correction이 아니다.
다음 row의 semantic lifelog representation 자체다.

## Subject-Heldout Retrieval

같은 subject가 train/validation에 동시에 들어가지 않는다.
`current_episode_identity`는 "오늘과 내일이 비슷하다"는 persistence baseline이고,
`subject_relative_context_to_next_state`가 HS-JEPA transition predictor다.

{markdown_table(
    subject_table,
    ["method", "folds", "mean_candidate_count", "top1_accuracy", "top5_recall", "mean_rank_pct", "lift_top1_vs_random", "lift_top5_vs_random", "lift_rank_pct_vs_random"],
    max_rows=20,
)}

## Chronological Retrieval

각 subject의 앞 episode로 predictor를 학습하고 뒤 episode를 retrieval한다.

{markdown_table(
    chrono_table,
    ["method", "folds", "mean_candidate_count", "top1_accuracy", "top5_recall", "mean_rank_pct", "lift_top1_vs_random", "lift_top5_vs_random", "lift_rank_pct_vs_random"],
    max_rows=20,
)}

## Persistence와의 비교

- subject-relative predicted transition rank lift: `{format_float(predicted.get("lift_rank_pct_vs_random"), 6)}`
- rhythm-conditioned predicted transition rank lift: `{format_float(rhythm_predicted.get("lift_rank_pct_vs_random"), 6)}`
- persistence rank lift: `{format_float(persistence.get("lift_rank_pct_vs_random"), 6)}`
- predicted minus persistence: `{format_float(summary.get("subject_predicted_rank_lift_minus_persistence"), 6)}`

이 값이 양수이면 HS-JEPA predictor가 단순히 현재 episode를 복사하는 것보다 미래 state를 더 잘 잡는다는 뜻이다.
음수이면 현재 상태 persistence가 더 강한 baseline이라는 뜻이다.

## Frozen Next-Label Probe

다음 episode representation이 Q/S label manifold도 조금 더 선형적으로 만드는지 low-trust probe로만 확인한다.
label은 pretext target이 아니라 freeze된 representation을 읽는 probe target이다.

### Subject-Heldout

{markdown_table(label_subject, ["feature_set", "folds", "logloss", "auc", "average_precision", "evaluated_rows"], max_rows=20)}

### Chronological

{markdown_table(label_chrono, ["feature_set", "folds", "logloss", "auc", "average_precision", "evaluated_rows"], max_rows=20)}

## 현재 해석

strong positive이면 논문 주장은 다음으로 강화된다.

```text
HS-JEPA는 단순 static state encoder가 아니라,
visible human-life context에서 다음 human-state episode를 예측하는 transition world model이다.
```

negative이면 경계도 분명하다.

```text
현재 lifelog에서 미래 episode는 대부분 persistence/calendar/subject prior로 설명되고,
HS-JEPA transition predictor는 아직 persistence를 넘는 일반 transition law를 충분히 복원하지 못했다.
```
"""


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frame, labels = load_frames()
    frame, relative, rhythm_conditioned, raw_cols, calendar_cols = make_transition_views(frame)
    all_pairs = build_transition_pairs(frame)
    folds = make_subject_transition_folds(all_pairs) + make_chronological_transition_folds(frame, all_pairs)
    retrieval_raw, state = evaluate_transition_retrieval(
        frame,
        relative,
        rhythm_conditioned,
        raw_cols,
        calendar_cols,
        all_pairs,
        folds,
    )
    retrieval = aggregate_retrieval(retrieval_raw)
    label_probe = evaluate_next_label_probe(frame, labels, relative, rhythm_conditioned, raw_cols, calendar_cols)
    summary = summarize(retrieval, label_probe)

    retrieval_raw.to_csv(OUT_DIR / "episode_transition_retrieval_fold_metrics.csv", index=False)
    retrieval.to_csv(OUT_DIR / "episode_transition_retrieval_metrics.csv", index=False)
    state.to_csv(OUT_DIR / "episode_transition_predicted_state.csv", index=False)
    label_probe.to_csv(OUT_DIR / "episode_transition_next_label_probe_metrics.csv", index=False)
    (OUT_DIR / "episode_transition_retrieval_summary.json").write_text(
        json.dumps(json_safe(summary), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    markdown = build_markdown(summary, retrieval, label_probe)
    (OUT_DIR / "EPISODE_TRANSITION_RETRIEVAL_CORE_KO.md").write_text(markdown, encoding="utf-8")
    PAPER_DOC.write_text(markdown, encoding="utf-8")
    print(json.dumps(json_safe(summary), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
