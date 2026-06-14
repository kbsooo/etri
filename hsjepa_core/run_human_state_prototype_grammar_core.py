#!/usr/bin/env python3
"""HS-JEPA Human-State Prototype Grammar core experiment.

This runner tests a core paper claim without using public LB or submission
probabilities:

    visible human-life context
      -> predicted hidden episode-prototype responsibilities
      -> frozen low-trust probes and subject/row-block stress tests

The target representation is a label-free prototype grammar over semantic
lifelog views.  Labels are used only after the representation is frozen.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hsjepa_core.human_state_world_model import finite_frame, rank01  # noqa: E402
from hsjepa_core.run_human_state_world_model_core import (  # noqa: E402
    calibrated_probe_metrics,
    chronological_folds,
    evaluate_split,
    neighbor_consistency,
    subject_folds,
    subject_relative_frame,
    subject_leakage_probe,
)
from hsjepa_core.run_lifelog_core_state_evidence import (  # noqa: E402
    TARGETS,
    catalog_features,
    format_float,
    load_frames,
    markdown_table,
    view_columns,
)


OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "human_state_prototype_grammar_core"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "HUMAN_STATE_PROTOTYPE_GRAMMAR_CORE_KO.md"
RANDOM_SEED = 20260614
LATENT_DIMS_PER_VIEW = 4
PROTOTYPES_PER_VIEW = 3
LOGISTIC_C = 0.55
GRAMMAR_FRAME = "subject_relative_lifelog"


def json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [json_safe(v) for v in value]
    if isinstance(value, tuple):
        return [json_safe(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        if not np.isfinite(value):
            return None
        return float(value)
    if isinstance(value, np.ndarray):
        return json_safe(value.tolist())
    return value


def row_block_folds(train_frame: pd.DataFrame, n_blocks: int = 5) -> list[tuple[np.ndarray, np.ndarray]]:
    ordered = train_frame[["subject_id", "lifelog_date"]].copy()
    ordered["lifelog_date"] = pd.to_datetime(ordered["lifelog_date"], errors="coerce")
    ordered["_row"] = np.arange(len(train_frame))
    ordered = ordered.sort_values(["lifelog_date", "subject_id", "_row"])
    blocks = np.array_split(ordered["_row"].to_numpy(dtype=int), n_blocks)
    folds: list[tuple[np.ndarray, np.ndarray]] = []
    all_rows = np.arange(len(train_frame), dtype=int)
    for block in blocks:
        val = np.array(sorted(set(block.tolist())), dtype=int)
        train = np.array([idx for idx in all_rows if idx not in set(val.tolist())], dtype=int)
        if len(val) and len(train):
            folds.append((train, val))
    return folds


def fit_view_latents(frame: pd.DataFrame, views: dict[str, list[str]]) -> tuple[pd.DataFrame, dict[str, list[str]]]:
    latent = pd.DataFrame(index=frame.index)
    colsets: dict[str, list[str]] = {}
    for view, cols in views.items():
        if len(cols) < 2:
            continue
        n_components = max(1, min(LATENT_DIMS_PER_VIEW, len(cols), len(frame) - 1))
        model = make_pipeline(
            SimpleImputer(strategy="median"),
            StandardScaler(),
            PCA(n_components=n_components, random_state=RANDOM_SEED),
        )
        values = model.fit_transform(finite_frame(frame, cols))
        names = [f"pg_latent_{view}_c{idx + 1}" for idx in range(values.shape[1])]
        latent[names] = values
        colsets[view] = names
    return latent, colsets


def softmax_rows(scores: np.ndarray) -> np.ndarray:
    shifted = scores - np.max(scores, axis=1, keepdims=True)
    exp_scores = np.exp(shifted)
    denom = np.maximum(exp_scores.sum(axis=1, keepdims=True), 1e-12)
    return exp_scores / denom


def fit_prototypes(
    latent: pd.DataFrame,
    view_latent_cols: dict[str, list[str]],
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, int]]:
    state = pd.DataFrame(index=latent.index)
    rows: list[dict[str, Any]] = []
    prototype_counts: dict[str, int] = {}

    for view, cols in view_latent_cols.items():
        x = SimpleImputer(strategy="median").fit_transform(finite_frame(latent, cols))
        x = StandardScaler().fit_transform(x)
        k = max(2, min(PROTOTYPES_PER_VIEW, len(x) - 1))
        km = KMeans(n_clusters=k, n_init=32, random_state=RANDOM_SEED)
        labels = km.fit_predict(x)
        distances = km.transform(x)
        tau = float(np.median(np.min(distances, axis=1)))
        tau = tau if tau > 1e-9 else 1.0
        responsibilities = softmax_rows(-distances / tau)

        state[f"pg_true_{view}_prototype"] = labels
        state[f"pg_true_{view}_confidence"] = responsibilities.max(axis=1)
        entropy = -np.sum(responsibilities * np.log(np.clip(responsibilities, 1e-12, 1.0)), axis=1) / math.log(k)
        state[f"pg_true_{view}_entropy"] = entropy
        for proto in range(k):
            state[f"pg_true_{view}_p{proto}"] = responsibilities[:, proto]
        prototype_counts[view] = k

        counts = pd.Series(labels).value_counts(normalize=True).sort_index()
        for proto in range(k):
            rows.append(
                {
                    "view": view,
                    "prototype": proto,
                    "share": float(counts.get(proto, 0.0)),
                    "mean_confidence": float(responsibilities[labels == proto, proto].mean()),
                    "rows": int((labels == proto).sum()),
                }
            )

    return state, pd.DataFrame(rows), prototype_counts


def predict_masked_prototypes(
    latent: pd.DataFrame,
    prototype_state: pd.DataFrame,
    view_latent_cols: dict[str, list[str]],
    prototype_counts: dict[str, int],
    groups: np.ndarray,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    pred_state = pd.DataFrame(index=latent.index)
    metric_rows: list[dict[str, Any]] = []
    fold_rows: list[dict[str, Any]] = []
    n_splits = max(2, min(5, len(np.unique(groups))))
    splitter = GroupKFold(n_splits=n_splits)

    for target_view, target_cols in view_latent_cols.items():
        context_cols = [
            col
            for view, cols in view_latent_cols.items()
            if view != target_view
            for col in cols
        ]
        y = prototype_state[f"pg_true_{target_view}_prototype"].to_numpy(dtype=int)
        k = prototype_counts[target_view]
        proba = np.zeros((len(latent), k), dtype=np.float64)
        prior_proba = np.zeros((len(latent), k), dtype=np.float64)

        for fold, (tr, va) in enumerate(splitter.split(latent, groups=groups)):
            y_train = y[tr]
            prior = np.bincount(y_train, minlength=k).astype(np.float64)
            prior = (prior + 1.0) / (prior.sum() + k)
            prior_proba[va] = prior
            if len(np.unique(y_train)) < 2:
                fold_proba = np.tile(prior, (len(va), 1))
            else:
                model = make_pipeline(
                    SimpleImputer(strategy="median"),
                    StandardScaler(),
                    LogisticRegression(
                        C=LOGISTIC_C,
                        max_iter=5000,
                        solver="lbfgs",
                    ),
                )
                model.fit(finite_frame(latent.iloc[tr], context_cols), y_train)
                raw = model.predict_proba(finite_frame(latent.iloc[va], context_cols))
                fold_proba = np.zeros((len(va), k), dtype=np.float64)
                for class_pos, class_label in enumerate(model.classes_):
                    fold_proba[:, int(class_label)] = raw[:, class_pos]
                missing = fold_proba.sum(axis=1) <= 1e-12
                if np.any(missing):
                    fold_proba[missing] = prior
            fold_proba = np.clip(fold_proba, 1e-6, 1.0)
            fold_proba = fold_proba / fold_proba.sum(axis=1, keepdims=True)
            proba[va] = fold_proba

            fold_loss = float(log_loss(y[va], fold_proba, labels=list(range(k))))
            fold_prior_loss = float(log_loss(y[va], prior_proba[va], labels=list(range(k))))
            fold_rows.append(
                {
                    "target_view": target_view,
                    "fold": fold,
                    "rows": int(len(va)),
                    "prototype_count": int(k),
                    "cross_entropy": fold_loss,
                    "prior_cross_entropy": fold_prior_loss,
                    "cross_entropy_lift_vs_prior": fold_prior_loss - fold_loss,
                    "accuracy": float(accuracy_score(y[va], np.argmax(fold_proba, axis=1))),
                    "prior_accuracy": float(accuracy_score(y[va], np.argmax(prior_proba[va], axis=1))),
                }
            )

        energy = -np.log(np.clip(proba[np.arange(len(y)), y], 1e-12, 1.0))
        prior_energy = -np.log(np.clip(prior_proba[np.arange(len(y)), y], 1e-12, 1.0))
        pred_entropy = -np.sum(proba * np.log(np.clip(proba, 1e-12, 1.0)), axis=1) / math.log(k)
        for proto in range(k):
            pred_state[f"pg_pred_{target_view}_p{proto}"] = proba[:, proto]
        pred_state[f"pg_pred_{target_view}_prototype"] = np.argmax(proba, axis=1)
        pred_state[f"pg_energy_{target_view}"] = energy
        pred_state[f"pg_energy_lift_{target_view}"] = prior_energy - energy
        pred_state[f"pg_pred_{target_view}_confidence"] = proba.max(axis=1)
        pred_state[f"pg_pred_{target_view}_entropy"] = pred_entropy

        loss = float(log_loss(y, proba, labels=list(range(k))))
        prior_loss = float(log_loss(y, prior_proba, labels=list(range(k))))
        metric_rows.append(
            {
                "target_view": target_view,
                "rows": int(len(y)),
                "prototype_count": int(k),
                "context_feature_count": int(len(context_cols)),
                "cross_entropy": loss,
                "prior_cross_entropy": prior_loss,
                "cross_entropy_lift_vs_prior": prior_loss - loss,
                "accuracy": float(accuracy_score(y, np.argmax(proba, axis=1))),
                "prior_accuracy": float(accuracy_score(y, np.argmax(prior_proba, axis=1))),
                "accuracy_lift_vs_prior": float(
                    accuracy_score(y, np.argmax(proba, axis=1))
                    - accuracy_score(y, np.argmax(prior_proba, axis=1))
                ),
                "mean_energy": float(energy.mean()),
                "mean_prior_energy": float(prior_energy.mean()),
                "uses_public_score": False,
                "uses_label_as_pretext": False,
            }
        )

    energy_cols = [col for col in pred_state.columns if col.startswith("pg_energy_") and "_lift_" not in col]
    confidence_cols = [col for col in pred_state.columns if col.endswith("_confidence")]
    entropy_cols = [col for col in pred_state.columns if col.endswith("_entropy")]
    pred_state["pg_energy_mean"] = pred_state[energy_cols].mean(axis=1)
    pred_state["pg_energy_max"] = pred_state[energy_cols].max(axis=1)
    pred_state["pg_energy_rank_mean"] = rank01(pred_state["pg_energy_mean"].to_numpy(dtype=np.float64))
    pred_state["pg_confidence_mean"] = pred_state[confidence_cols].mean(axis=1)
    pred_state["pg_entropy_mean"] = pred_state[entropy_cols].mean(axis=1)
    return pred_state, pd.DataFrame(metric_rows), pd.DataFrame(fold_rows)


def prototype_interpretation(
    frame: pd.DataFrame,
    views: dict[str, list[str]],
    prototype_state: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for view, cols in views.items():
        label_col = f"pg_true_{view}_prototype"
        if label_col not in prototype_state:
            continue
        x = finite_frame(frame, cols)
        values = SimpleImputer(strategy="median").fit_transform(x)
        z = StandardScaler().fit_transform(values)
        labels = prototype_state[label_col].to_numpy(dtype=int)
        for proto in sorted(np.unique(labels)):
            mask = labels == proto
            mean_z = z[mask].mean(axis=0)
            order_pos = np.argsort(-mean_z)[:5]
            order_neg = np.argsort(mean_z)[:5]
            subject_counts = frame.loc[mask, "subject_id"].astype(str).value_counts(normalize=True)
            entropy = -float((subject_counts * np.log(np.clip(subject_counts, 1e-12, 1.0))).sum())
            entropy = entropy / math.log(max(2, frame["subject_id"].nunique()))
            rows.append(
                {
                    "view": view,
                    "prototype": int(proto),
                    "rows": int(mask.sum()),
                    "train_rows": int((frame.loc[mask, "split"].eq("train")).sum()),
                    "test_rows": int((frame.loc[mask, "split"].eq("test")).sum()),
                    "subject_entropy_0to1": entropy,
                    "top_positive_features": ", ".join(str(cols[idx]) for idx in order_pos),
                    "top_positive_z": ", ".join(format_float(mean_z[idx], 3) for idx in order_pos),
                    "top_negative_features": ", ".join(str(cols[idx]) for idx in order_neg),
                    "top_negative_z": ", ".join(format_float(mean_z[idx], 3) for idx in order_neg),
                }
            )
    return pd.DataFrame(rows)


def feature_columns(predicted: pd.DataFrame, observed: pd.DataFrame) -> dict[str, list[str]]:
    pred_prob_cols = [c for c in predicted.columns if c.startswith("pg_pred_") and "_p" in c]
    pred_energy_cols = [c for c in predicted.columns if c.startswith("pg_energy_") or c in {"pg_energy_mean", "pg_energy_max", "pg_energy_rank_mean"}]
    pred_stat_cols = [c for c in predicted.columns if c.startswith("pg_pred_") and (c.endswith("_confidence") or c.endswith("_entropy"))]
    true_prob_cols = [c for c in observed.columns if c.startswith("pg_true_") and "_p" in c]
    true_stat_cols = [c for c in observed.columns if c.startswith("pg_true_") and (c.endswith("_confidence") or c.endswith("_entropy"))]
    return {
        "predicted_prototype_grammar": sorted(set(pred_prob_cols + pred_stat_cols)),
        "predicted_prototype_grammar_energy": sorted(set(pred_prob_cols + pred_stat_cols + pred_energy_cols)),
        "observed_prototype_upper_bound": sorted(set(true_prob_cols + true_stat_cols)),
        "prototype_full_observed_predicted": sorted(set(pred_prob_cols + pred_stat_cols + pred_energy_cols + true_prob_cols + true_stat_cols)),
    }


def summarize(
    pretext_metrics: pd.DataFrame,
    probe_metrics: pd.DataFrame,
    neighbor_metrics: pd.DataFrame,
    leakage_metrics: pd.DataFrame,
    interpretation: pd.DataFrame,
) -> dict[str, Any]:
    subject_all = probe_metrics[(probe_metrics["split"].eq("subject_heldout")) & (probe_metrics["target"].eq("all"))]
    row_all = probe_metrics[(probe_metrics["split"].eq("row_block_holdout")) & (probe_metrics["target"].eq("all"))]
    prior = subject_all[subject_all["feature_set"].eq("prior_only")]
    predicted = subject_all[subject_all["feature_set"].eq("predicted_prototype_grammar_calibrated10")]
    predicted_energy = subject_all[subject_all["feature_set"].eq("predicted_prototype_grammar_energy_calibrated10")]
    observed = subject_all[subject_all["feature_set"].eq("observed_prototype_upper_bound_calibrated10")]
    best_subject = subject_all.sort_values("logloss").head(1)
    best_row = row_all.sort_values("logloss").head(1)
    best_pretext = pretext_metrics.sort_values("cross_entropy_lift_vs_prior", ascending=False).head(1)
    nn_all = neighbor_metrics[neighbor_metrics["target"].eq("all")].sort_values("lift", ascending=False)

    def row_or_none(frame: pd.DataFrame) -> dict[str, Any] | None:
        return None if frame.empty else frame.iloc[0].to_dict()

    prior_loss = float(prior["logloss"].iloc[0]) if not prior.empty else float("nan")
    predicted_loss = float(predicted["logloss"].iloc[0]) if not predicted.empty else float("nan")
    predicted_energy_loss = float(predicted_energy["logloss"].iloc[0]) if not predicted_energy.empty else float("nan")
    observed_loss = float(observed["logloss"].iloc[0]) if not observed.empty else float("nan")
    leakage_pred = leakage_metrics[
        leakage_metrics["feature_set"].eq("predicted_prototype_grammar_energy")
    ]
    subject_entropy = (
        float(interpretation["subject_entropy_0to1"].mean())
        if "subject_entropy_0to1" in interpretation and not interpretation.empty
        else float("nan")
    )

    pretext_lift = float(pretext_metrics["cross_entropy_lift_vs_prior"].mean())
    leakage_acc = (
        float(leakage_pred["subject_id_accuracy"].iloc[0])
        if not leakage_pred.empty
        else float("nan")
    )
    verdict = "prototype_grammar_negative_boundary"
    if np.isfinite(predicted_energy_loss) and np.isfinite(prior_loss):
        delta = predicted_energy_loss - prior_loss
        if pretext_lift > 0 and delta < 0 and np.isfinite(leakage_acc) and leakage_acc < 0.35:
            verdict = "subject_invariant_prototype_grammar_core_positive_boundary"
        elif delta < 0:
            verdict = "prototype_grammar_probe_only_boundary"

    return {
        "package": "human_state_prototype_grammar_core",
        "status": "human_state_prototype_grammar_core_ready",
        "verdict": verdict,
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "uses_label_as_pretext_target": False,
        "grammar_frame": GRAMMAR_FRAME,
        "latent_dims_per_view": LATENT_DIMS_PER_VIEW,
        "prototypes_per_view": PROTOTYPES_PER_VIEW,
        "pretext_mean_cross_entropy_lift_vs_prior": pretext_lift,
        "best_pretext": row_or_none(best_pretext),
        "subject_prior_logloss": prior_loss,
        "subject_predicted_prototype_logloss": predicted_loss,
        "subject_predicted_prototype_delta_vs_prior": predicted_loss - prior_loss,
        "subject_predicted_energy_logloss": predicted_energy_loss,
        "subject_predicted_energy_delta_vs_prior": predicted_energy_loss - prior_loss,
        "subject_observed_upper_bound_logloss": observed_loss,
        "subject_observed_upper_bound_delta_vs_prior": observed_loss - prior_loss,
        "subject_best_probe": row_or_none(best_subject),
        "row_block_best_probe": row_or_none(best_row),
        "best_neighbor_consistency": row_or_none(nn_all.head(1)),
        "predicted_energy_subject_leakage": row_or_none(leakage_pred),
        "mean_prototype_subject_entropy": subject_entropy,
    }


def build_markdown(
    summary: dict[str, Any],
    pretext_metrics: pd.DataFrame,
    fold_metrics: pd.DataFrame,
    probe_metrics: pd.DataFrame,
    neighbor_metrics: pd.DataFrame,
    leakage_metrics: pd.DataFrame,
    interpretation: pd.DataFrame,
) -> str:
    subject_all = probe_metrics[(probe_metrics["split"].eq("subject_heldout")) & (probe_metrics["target"].eq("all"))].sort_values("logloss")
    chrono_all = probe_metrics[(probe_metrics["split"].eq("chronological_holdout")) & (probe_metrics["target"].eq("all"))].sort_values("logloss")
    row_all = probe_metrics[(probe_metrics["split"].eq("row_block_holdout")) & (probe_metrics["target"].eq("all"))].sort_values("logloss")
    nn_all = neighbor_metrics[neighbor_metrics["target"].eq("all")].sort_values("lift", ascending=False)

    return f"""# Human-State Prototype Grammar Core

## 한 줄 요약

이 실험은 HS-JEPA를 연속 latent 후처리가 아니라 `인간 생활 episode prototype grammar`를 예측하는 core architecture로 검증한다.

```text
visible semantic lifelog views
  -> predict masked hidden prototype responsibilities
  -> freeze predicted grammar
  -> subject-heldout / chronological / row-block probes
```

## 판정

- verdict: `{summary["verdict"]}`
- grammar frame: `{summary["grammar_frame"]}`
- public LB ledger 사용: `{summary["uses_public_score_ledger"]}`
- prior submission probability 사용: `{summary["uses_prior_submission_probabilities"]}`
- proprietary embedding API 사용: `{summary["uses_proprietary_embedding_api"]}`
- label을 pretext target으로 사용: `{summary["uses_label_as_pretext_target"]}`

## 왜 이것이 HS-JEPA Core인가

JEPA의 질문을 인간 생활 로그로 옮기면 다음과 같다.

```text
일부 생활 context만 보고,
보이지 않는 semantic view가 어떤 human-state prototype에 속하는지 예측할 수 있는가?
```

여기서 prototype은 Q/S label이 아니다. phone behavior, body/sleep, social/app, mobility/environment 같은 semantic view가 만드는 label-free episode 원형이다.
또한 prototype은 absolute feature가 아니라 subject-relative lifelog 좌표에서 만든다.
따라서 한 사람의 고유 센서/사용량 크기를 외우는 것이 아니라, 그 사람 기준으로 오늘이 어떤 생활 episode 원형에 가까운지를 묻는다.

## Masked Context -> Prototype Responsibility Pretext

- 평균 cross-entropy lift vs prior: `{format_float(summary["pretext_mean_cross_entropy_lift_vs_prior"], 6)}`
- best pretext view: `{summary["best_pretext"]["target_view"] if summary.get("best_pretext") else "NA"}`
- best cross-entropy lift: `{format_float(summary["best_pretext"]["cross_entropy_lift_vs_prior"] if summary.get("best_pretext") else None, 6)}`

{markdown_table(pretext_metrics.sort_values("cross_entropy_lift_vs_prior", ascending=False), ["target_view", "prototype_count", "context_feature_count", "cross_entropy", "prior_cross_entropy", "cross_entropy_lift_vs_prior", "accuracy", "prior_accuracy"])}

## Subject-Heldout Frozen Probe

같은 subject가 train/validation 양쪽에 동시에 들어가지 않는다. label은 frozen representation을 읽는 probe에서만 사용한다.

{markdown_table(subject_all, ["feature_set", "logloss", "auc"], max_rows=18)}

## Chronological Frozen Probe

각 subject의 앞쪽 episode로 읽고 뒤쪽 episode를 평가한다.

{markdown_table(chrono_all, ["feature_set", "logloss", "auc"], max_rows=18)}

## Row-Block Frozen Probe

전체 row order를 시간 block으로 나누어 특정 시기 block을 통째로 holdout한다.

{markdown_table(row_all, ["feature_set", "logloss", "auc"], max_rows=18)}

## Neighbor Consistency

좋은 prototype grammar라면 가까운 이웃의 target vector가 random 이웃보다 더 비슷해야 한다.

{markdown_table(nn_all, ["feature_set", "neighbor_match_rate", "random_match_rate", "lift"], max_rows=12)}

## Subject Leakage Probe

prototype grammar가 subject identity shortcut인지 확인한다. accuracy가 높을수록 subject identity를 더 잘 외운다.

{markdown_table(leakage_metrics.sort_values("subject_id_accuracy"), ["feature_set", "subject_id_accuracy", "chance_accuracy", "leakage_lift_vs_chance"], max_rows=12)}

## Prototype Interpretation

각 prototype의 상위 feature는 사람이 해석 가능한 생활 episode 원형을 제공한다.

{markdown_table(interpretation.sort_values(["view", "prototype"]), ["view", "prototype", "rows", "subject_entropy_0to1", "top_positive_features", "top_negative_features"], max_rows=18)}

## 현재 해석

이 실험이 strong positive이면 논문 주장은 다음으로 강화된다.

```text
HS-JEPA는 label prediction 이전에 subject-invariant human-life episode grammar를 복원한다.
이 grammar는 subject-heldout 조건에서도 target manifold를 더 선형적으로 만든다.
```

negative이면 다음 경계가 생긴다.

```text
prototype grammar 자체는 masked view를 예측할 수 있지만,
Q/S label로 번역되는 축은 listener-specific drift/route decoder가 따로 필요하다.
```
"""


def run() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    PAPER_DOC.parent.mkdir(parents=True, exist_ok=True)

    frame, _labels = load_frames()
    catalog = catalog_features(frame)
    views = view_columns(catalog)

    grammar_frame = subject_relative_frame(frame, catalog.raw_numeric)
    latent, view_latent_cols = fit_view_latents(grammar_frame, views)
    observed, prototype_summary, prototype_counts = fit_prototypes(latent, view_latent_cols)
    groups = frame["subject_id"].astype(str).to_numpy()
    predicted, pretext_metrics, fold_metrics = predict_masked_prototypes(
        latent,
        observed,
        view_latent_cols,
        prototype_counts,
        groups,
    )
    interpretation = prototype_interpretation(grammar_frame, views, observed)

    state = pd.concat([latent, observed, predicted], axis=1)
    colsets = feature_columns(predicted, observed)
    catalog_cols = {
        "prior_only": [],
        "calendar_rhythm": catalog.calendar,
        "raw_lifelog_pca": catalog.raw_numeric,
    }

    train_mask = frame["split"].eq("train")
    train_frame = frame.loc[train_mask].reset_index(drop=True)
    train_state = state.loc[train_mask].reset_index(drop=True)
    train_catalog_frame = frame.loc[train_mask].reset_index(drop=True)
    train_features = pd.concat([train_catalog_frame[catalog.raw_numeric], train_state], axis=1)
    feature_sets = {
        **catalog_cols,
        **colsets,
    }

    probe_parts: list[pd.DataFrame] = []
    prediction_parts: list[pd.DataFrame] = []
    for split_name, folds in {
        "subject_heldout": subject_folds(train_frame),
        "chronological_holdout": chronological_folds(train_frame),
        "row_block_holdout": row_block_folds(train_frame),
    }.items():
        metrics, predictions = evaluate_split(train_frame, train_features, feature_sets, split_name, folds)
        probe_parts.append(metrics)
        prediction_parts.append(predictions)
        probe_parts.append(calibrated_probe_metrics(predictions, shrink=0.05))
        probe_parts.append(calibrated_probe_metrics(predictions, shrink=0.10))

    probe_metrics = pd.concat(probe_parts, ignore_index=True, sort=False)
    probe_predictions = pd.concat(prediction_parts, ignore_index=True, sort=False)
    neighbor_metrics = neighbor_consistency(train_frame, train_features, feature_sets)
    leakage_metrics = subject_leakage_probe(
        train_frame,
        train_features,
        {key: value for key, value in feature_sets.items() if value},
    )
    summary = summarize(pretext_metrics, probe_metrics, neighbor_metrics, leakage_metrics, interpretation)

    latent.to_csv(OUT_DIR / "prototype_grammar_view_latents.csv", index=False)
    observed.to_csv(OUT_DIR / "prototype_grammar_observed_state.csv", index=False)
    predicted.to_csv(OUT_DIR / "prototype_grammar_predicted_state.csv", index=False)
    prototype_summary.to_csv(OUT_DIR / "prototype_grammar_cluster_summary.csv", index=False)
    pretext_metrics.to_csv(OUT_DIR / "prototype_grammar_pretext_metrics.csv", index=False)
    fold_metrics.to_csv(OUT_DIR / "prototype_grammar_pretext_fold_metrics.csv", index=False)
    probe_metrics.to_csv(OUT_DIR / "prototype_grammar_probe_metrics.csv", index=False)
    probe_predictions.to_csv(OUT_DIR / "prototype_grammar_probe_predictions.csv", index=False)
    neighbor_metrics.to_csv(OUT_DIR / "prototype_grammar_neighbor_consistency.csv", index=False)
    leakage_metrics.to_csv(OUT_DIR / "prototype_grammar_subject_leakage.csv", index=False)
    interpretation.to_csv(OUT_DIR / "prototype_grammar_interpretation.csv", index=False)
    (OUT_DIR / "human_state_prototype_grammar_summary.json").write_text(
        json.dumps(json_safe(summary), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    doc = build_markdown(summary, pretext_metrics, fold_metrics, probe_metrics, neighbor_metrics, leakage_metrics, interpretation)
    (OUT_DIR / "HUMAN_STATE_PROTOTYPE_GRAMMAR_CORE_KO.md").write_text(doc, encoding="utf-8")
    PAPER_DOC.write_text(doc, encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(json_safe(run()), ensure_ascii=False, indent=2))
