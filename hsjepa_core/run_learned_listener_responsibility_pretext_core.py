#!/usr/bin/env python3
"""HS-JEPA learned listener-responsibility pretext experiment.

The previous label-free listener experiment used hand-coded target profiles:

    target description + transported prototype reliability
      -> listener responsibility

This experiment makes the missing HS-JEPA contract explicit:

    visible human-life context
      -> hidden transported listener-responsibility field
      -> frozen downstream probes

The hidden teacher is still label-free.  It is built from transported prototype
confidence, entropy, and energy.  Labels are used only after the representation
is frozen, as subject-heldout / row-block / chronological probes.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hsjepa_core.run_human_state_prototype_grammar_core import PROTOTYPES_PER_VIEW  # noqa: E402
from hsjepa_core.run_human_state_world_model_core import subject_leakage_probe  # noqa: E402
from hsjepa_core.run_label_free_transported_listener_responsibility_core import (  # noqa: E402
    FAMILY_TARGET_PROFILES,
    SEMANTIC_TARGET_PROFILES,
    build_label_free_listener_features,
    evaluate_target_specific_split,
    global_transport_cols,
    load_transport_state,
    split_folds,
)
from hsjepa_core.run_lifelog_core_state_evidence import (  # noqa: E402
    TARGETS,
    catalog_features,
    format_float,
    load_frames,
    markdown_table,
    view_columns,
)


OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "learned_listener_responsibility_pretext_core"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "LEARNED_LISTENER_RESPONSIBILITY_PRETEXT_CORE_KO.md"
RANDOM_SEED = 20260614
RIDGE_ALPHA = 12.0


def json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [json_safe(v) for v in value]
    if isinstance(value, tuple):
        return [json_safe(v) for v in value]
    if isinstance(value, np.ndarray):
        return json_safe(value.tolist())
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        if not np.isfinite(value):
            return None
        return float(value)
    return value


def finite_frame(frame: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    return frame[cols].replace([np.inf, -np.inf], np.nan)


def subject_relative_context(train_frame: pd.DataFrame, context: pd.DataFrame) -> pd.DataFrame:
    out = context.copy()
    subject = train_frame["subject_id"].astype(str).reset_index(drop=True)
    for col in out.columns:
        values = pd.to_numeric(out[col], errors="coerce")
        grouped = values.groupby(subject)
        mean = grouped.transform("mean")
        std = grouped.transform("std").replace(0.0, np.nan)
        out[col] = ((values - mean) / std).clip(-5.0, 5.0)
    return out


def softmax_rows(logits: np.ndarray) -> np.ndarray:
    arr = np.asarray(logits, dtype=np.float64)
    arr = arr - np.nanmax(arr, axis=1, keepdims=True)
    exp = np.exp(np.clip(arr, -40.0, 40.0))
    return exp / np.maximum(exp.sum(axis=1, keepdims=True), 1e-12)


def normalize_rows(values: np.ndarray) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64)
    arr = np.clip(arr, 1e-9, None)
    return arr / np.maximum(arr.sum(axis=1, keepdims=True), 1e-12)


def view_order(views: dict[str, list[str]]) -> list[str]:
    return list(views.keys())


def view_teacher_weights(
    state: pd.DataFrame,
    views: dict[str, list[str]],
    profile: dict[str, float] | None,
) -> np.ndarray:
    names = view_order(views)
    confidence = np.column_stack(
        [state[f"cspg_pred_{view}_confidence"].to_numpy(dtype=np.float64) for view in names]
    )
    entropy = np.column_stack(
        [state[f"cspg_pred_{view}_entropy"].to_numpy(dtype=np.float64) for view in names]
    )
    lift = np.column_stack(
        [state[f"cspg_energy_lift_{view}"].to_numpy(dtype=np.float64) for view in names]
    )
    reliability = np.clip(confidence, 0.0, 1.0) * np.clip(1.0 - entropy, 0.0, 1.0)
    reliability *= np.exp(0.25 * np.clip(lift, -3.0, 3.0))
    if profile is None:
        base = np.ones(len(names), dtype=np.float64)
    else:
        base = np.array([profile.get(view, 0.0) for view in names], dtype=np.float64)
        if float(base.sum()) <= 0.0:
            base = np.ones(len(names), dtype=np.float64)
    return normalize_rows(reliability * base.reshape(1, -1))


def make_responsibility_predictor(feature_count: int, train_count: int) -> Any:
    steps: list[Any] = [SimpleImputer(strategy="median"), StandardScaler()]
    if feature_count > 36 and train_count > 12:
        steps.append(PCA(n_components=min(32, feature_count, train_count - 1), random_state=RANDOM_SEED))
    steps.append(Ridge(alpha=RIDGE_ALPHA))
    return make_pipeline(*steps)


def responsibility_features_from_weights(
    state: pd.DataFrame,
    views: dict[str, list[str]],
    weights: np.ndarray,
    prefix: str,
) -> pd.DataFrame:
    names = view_order(views)
    out = pd.DataFrame(index=state.index)
    for proto in range(PROTOTYPES_PER_VIEW):
        values = np.column_stack(
            [state[f"cspg_pred_{view}_p{proto}"].to_numpy(dtype=np.float64) for view in names]
        )
        out[f"{prefix}_p{proto}"] = np.sum(weights * values, axis=1)
    for stat in ["confidence", "entropy"]:
        values = np.column_stack(
            [state[f"cspg_pred_{view}_{stat}"].to_numpy(dtype=np.float64) for view in names]
        )
        out[f"{prefix}_{stat}_weighted"] = np.sum(weights * values, axis=1)
    for stat in ["energy", "energy_lift"]:
        values = np.column_stack(
            [state[f"cspg_{stat}_{view}"].to_numpy(dtype=np.float64) for view in names]
        )
        out[f"{prefix}_{stat}_weighted"] = np.sum(weights * values, axis=1)
    out[f"{prefix}_responsibility_max"] = weights.max(axis=1)
    out[f"{prefix}_responsibility_entropy"] = -np.sum(
        weights * np.log(np.clip(weights, 1e-12, 1.0)),
        axis=1,
    ) / math.log(max(2, len(names)))
    for idx, view in enumerate(names):
        out[f"{prefix}_w_{view}"] = weights[:, idx]
    return out


def learned_listener_features(
    train_frame: pd.DataFrame,
    context: pd.DataFrame,
    state: pd.DataFrame,
    views: dict[str, list[str]],
    profiles: dict[str, dict[str, float] | None],
    folds: list[tuple[np.ndarray, np.ndarray]],
    split_name: str,
    feature_prefix: str,
    responsibility_blend: float,
) -> tuple[pd.DataFrame, dict[str, list[str]], pd.DataFrame]:
    context = context.reset_index(drop=True)
    state = state.reset_index(drop=True)
    all_features = pd.DataFrame(index=state.index)
    target_cols: dict[str, list[str]] = {}
    pretext_rows: list[dict[str, Any]] = []
    views_count = len(view_order(views))

    for target in TARGETS:
        teacher = view_teacher_weights(state, views, profiles[target])
        predicted = np.zeros_like(teacher, dtype=np.float64)
        evaluated = np.zeros(len(state), dtype=bool)
        for fold, (tr_idx, va_idx) in enumerate(folds):
            evaluated[va_idx] = True
            train_teacher = teacher[tr_idx]
            prior = normalize_rows(np.tile(train_teacher.mean(axis=0), (len(va_idx), 1)))
            if len(tr_idx) < 8:
                raw_pred = prior
            else:
                model = make_responsibility_predictor(context.shape[1], len(tr_idx))
                model.fit(finite_frame(context.iloc[tr_idx], list(context.columns)), np.log(np.clip(train_teacher, 1e-5, 1.0)))
                raw_pred = softmax_rows(model.predict(finite_frame(context.iloc[va_idx], list(context.columns))))
            pred = normalize_rows((1.0 - responsibility_blend) * prior + responsibility_blend * raw_pred)
            predicted[va_idx] = pred

            y = teacher[va_idx]
            ce_pred = -float(np.mean(np.sum(y * np.log(np.clip(pred, 1e-12, 1.0)), axis=1)))
            ce_prior = -float(np.mean(np.sum(y * np.log(np.clip(prior, 1e-12, 1.0)), axis=1)))
            top1_match = float(np.mean(np.argmax(y, axis=1) == np.argmax(pred, axis=1)))
            uniform_ce = math.log(max(2, views_count))
            pretext_rows.append(
                {
                    "split": split_name,
                    "feature_set": feature_prefix,
                    "target": target,
                    "fold": fold,
                    "pretext_cross_entropy": ce_pred,
                    "prior_cross_entropy": ce_prior,
                    "uniform_cross_entropy": uniform_ce,
                    "ce_lift_vs_prior": ce_prior - ce_pred,
                    "ce_lift_vs_uniform": uniform_ce - ce_pred,
                    "top1_match_rate": top1_match,
                    "train_rows": int(len(tr_idx)),
                    "validation_rows": int(len(va_idx)),
                    "uses_public_score": False,
                    "uses_train_labels_for_pretext": False,
                    "teacher_source": "transported_prototype_reliability",
                    "responsibility_blend": responsibility_blend,
                }
            )

        if not evaluated.all():
            missing = ~evaluated
            fallback = normalize_rows(np.tile(teacher[evaluated].mean(axis=0), (int(missing.sum()), 1)))
            predicted[missing] = fallback
        part = responsibility_features_from_weights(
            state,
            views,
            predicted,
            f"{feature_prefix}_{target}",
        )
        all_features = pd.concat([all_features, part], axis=1)
        target_cols[target] = list(part.columns)

    return all_features, target_cols, pd.DataFrame(pretext_rows)


def aggregate_pretext(pretext: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for (split, feature_set), part in pretext.groupby(["split", "feature_set"], observed=True):
        rows.append(
            {
                "split": split,
                "feature_set": feature_set,
                "target": "all",
                "pretext_cross_entropy": float(part["pretext_cross_entropy"].mean()),
                "prior_cross_entropy": float(part["prior_cross_entropy"].mean()),
                "uniform_cross_entropy": float(part["uniform_cross_entropy"].mean()),
                "ce_lift_vs_prior": float(part["ce_lift_vs_prior"].mean()),
                "ce_lift_vs_uniform": float(part["ce_lift_vs_uniform"].mean()),
                "top1_match_rate": float(part["top1_match_rate"].mean()),
                "uses_public_score": False,
                "uses_train_labels_for_pretext": False,
                "teacher_source": "transported_prototype_reliability",
                "responsibility_blend": float(part["responsibility_blend"].mean()),
            }
        )
    return pd.concat([pretext, pd.DataFrame(rows)], ignore_index=True, sort=False)


def flatten_cols(target_cols: dict[str, list[str]]) -> list[str]:
    return sorted(set(col for cols in target_cols.values() for col in cols))


def evaluate_split_package(
    split_name: str,
    train_frame: pd.DataFrame,
    context: pd.DataFrame,
    relative_context: pd.DataFrame,
    raw_cols: list[str],
    views: dict[str, list[str]],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    state = load_transport_state(split_name)
    folds = split_folds(split_name, train_frame)

    semantic_direct, semantic_direct_cols = build_label_free_listener_features(
        state,
        views,
        SEMANTIC_TARGET_PROFILES,
        "direct_semantic",
    )
    family_direct, family_direct_cols = build_label_free_listener_features(
        state,
        views,
        FAMILY_TARGET_PROFILES,
        "direct_family",
    )
    generic_profiles = {target: None for target in TARGETS}
    learned_configs = [
        ("learned_semantic_open_loop", context, SEMANTIC_TARGET_PROFILES, 1.00),
        ("learned_semantic_balanced", context, SEMANTIC_TARGET_PROFILES, 0.35),
        ("learned_semantic_conservative", context, SEMANTIC_TARGET_PROFILES, 0.15),
        ("learned_semantic_relative_balanced", relative_context, SEMANTIC_TARGET_PROFILES, 0.35),
        ("learned_semantic_relative_conservative", relative_context, SEMANTIC_TARGET_PROFILES, 0.15),
        ("learned_family_balanced", context, FAMILY_TARGET_PROFILES, 0.35),
        ("learned_generic_balanced", context, generic_profiles, 0.35),
    ]
    learned_feature_parts: list[pd.DataFrame] = []
    learned_feature_maps: dict[str, dict[str, list[str]]] = {}
    learned_pretext_parts: list[pd.DataFrame] = []
    for name, context_frame, profiles, blend in learned_configs:
        part, cols, pretext_part = learned_listener_features(
            train_frame,
            context_frame,
            state,
            views,
            profiles,
            folds,
            split_name,
            name,
            blend,
        )
        learned_feature_parts.append(part.reset_index(drop=True))
        learned_feature_maps[f"{name}_listener_responsibility"] = cols
        learned_pretext_parts.append(pretext_part)

    features = pd.concat(
        [
            train_frame[raw_cols].reset_index(drop=True),
            state.reset_index(drop=True),
            semantic_direct.reset_index(drop=True),
            family_direct.reset_index(drop=True),
            *learned_feature_parts,
        ],
        axis=1,
    )
    global_cols = global_transport_cols(views)
    feature_maps = {
        "prior_only": {target: [] for target in TARGETS},
        "raw_lifelog_pca": {target: raw_cols for target in TARGETS},
        "global_transported_prototype": {target: global_cols for target in TARGETS},
        "direct_semantic_listener_responsibility": semantic_direct_cols,
        "direct_family_listener_responsibility": family_direct_cols,
        **learned_feature_maps,
    }
    metrics, _predictions = evaluate_target_specific_split(
        train_frame,
        features,
        feature_maps,
        split_name,
        folds,
    )
    leakage_sets = {
        "raw_lifelog_pca": raw_cols,
        "global_transported_prototype": global_cols,
        "direct_semantic_listener_responsibility": flatten_cols(semantic_direct_cols),
        **{name: flatten_cols(cols) for name, cols in learned_feature_maps.items()},
    }
    leakage = subject_leakage_probe(train_frame, features, leakage_sets)
    leakage.insert(0, "split", split_name)
    pretext = aggregate_pretext(pd.concat(learned_pretext_parts, ignore_index=True))
    return metrics, leakage, pretext


def summarize(metrics: pd.DataFrame, leakage: pd.DataFrame, pretext: pd.DataFrame) -> dict[str, Any]:
    subject_all = metrics[(metrics["split"].eq("subject_heldout")) & (metrics["target"].eq("all"))]
    row_all = metrics[(metrics["split"].eq("row_block_holdout")) & (metrics["target"].eq("all"))]
    chrono_all = metrics[(metrics["split"].eq("chronological_holdout")) & (metrics["target"].eq("all"))]
    subject_pretext = pretext[(pretext["split"].eq("subject_heldout")) & (pretext["target"].eq("all"))]

    def loss(frame: pd.DataFrame, feature_set: str) -> float | None:
        part = frame[frame["feature_set"].eq(feature_set)]
        return None if part.empty else float(part["logloss"].iloc[0])

    def leak(feature_set: str) -> dict[str, Any] | None:
        part = leakage[leakage["split"].eq("subject_heldout") & leakage["feature_set"].eq(feature_set)]
        return None if part.empty else part.iloc[0].to_dict()

    learned_sets = sorted(
        subject_all[
            subject_all["feature_set"].str.startswith("learned_")
            & subject_all["feature_set"].str.endswith("_listener_responsibility_calibrated10")
        ]["feature_set"].tolist()
    )
    subject_losses = {name: loss(subject_all, name) for name in learned_sets}
    best_name = min(
        [name for name, value in subject_losses.items() if value is not None],
        key=lambda name: subject_losses[name],
    )
    learned_open = loss(subject_all, "learned_semantic_open_loop_listener_responsibility_calibrated10")
    learned_balanced = loss(subject_all, "learned_semantic_balanced_listener_responsibility_calibrated10")
    learned_conservative = loss(subject_all, "learned_semantic_conservative_listener_responsibility_calibrated10")
    learned_family = loss(subject_all, "learned_family_balanced_listener_responsibility_calibrated10")
    learned_generic = loss(subject_all, "learned_generic_balanced_listener_responsibility_calibrated10")
    direct_semantic = loss(subject_all, "direct_semantic_listener_responsibility_calibrated10")
    global_transport = loss(subject_all, "global_transported_prototype_calibrated10")
    prior = loss(subject_all, "prior_only_calibrated10")
    raw = loss(subject_all, "raw_lifelog_pca_calibrated10")
    best = subject_losses[best_name]
    best_row = loss(row_all, best_name)
    best_chrono = loss(chrono_all, best_name)
    global_row = loss(row_all, "global_transported_prototype_calibrated10")
    global_chrono = loss(chrono_all, "global_transported_prototype_calibrated10")

    verdict = "learned_listener_responsibility_negative"
    if best is not None and prior is not None and best < prior:
        verdict = "learned_listener_responsibility_prior_positive"
        if direct_semantic is not None and best < direct_semantic:
            verdict = "learned_listener_responsibility_beats_handcoded_positive"
        if global_transport is not None and best < global_transport:
            verdict = "learned_listener_responsibility_global_positive"

    pretext_rows = {
        row["feature_set"]: row.to_dict()
        for _, row in subject_pretext.iterrows()
    }

    return {
        "package": "learned_listener_responsibility_pretext_core",
        "status": "learned_listener_responsibility_pretext_core_ready",
        "verdict": verdict,
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "uses_label_as_pretext_target": False,
        "pretext_teacher": "transported_prototype_confidence_entropy_energy",
        "context_encoder": f"ridge_alpha_{RIDGE_ALPHA}_over_visible_lifelog_context",
        "subject_prior_logloss": prior,
        "subject_raw_logloss": raw,
        "subject_global_transport_logloss": global_transport,
        "subject_direct_semantic_logloss": direct_semantic,
        "subject_learned_semantic_open_loop_logloss": learned_open,
        "subject_learned_semantic_balanced_logloss": learned_balanced,
        "subject_learned_semantic_conservative_logloss": learned_conservative,
        "subject_learned_family_balanced_logloss": learned_family,
        "subject_learned_generic_balanced_logloss": learned_generic,
        "subject_best_learned_feature_set": best_name,
        "subject_best_learned_logloss": best,
        "subject_best_learned_delta_vs_prior": None if best is None or prior is None else best - prior,
        "subject_best_learned_delta_vs_raw": None if best is None or raw is None else best - raw,
        "subject_best_learned_delta_vs_global": None if best is None or global_transport is None else best - global_transport,
        "subject_best_learned_delta_vs_direct_semantic": None if best is None or direct_semantic is None else best - direct_semantic,
        "row_block_best_learned_delta_vs_global": None if best_row is None or global_row is None else best_row - global_row,
        "chronological_best_learned_delta_vs_global": None if best_chrono is None or global_chrono is None else best_chrono - global_chrono,
        "subject_pretext_all": pretext_rows,
        "subject_best_learned_leakage": leak(best_name.replace("_calibrated10", "")),
        "learned_semantic_open_loop_subject_leakage": leak("learned_semantic_open_loop_listener_responsibility"),
        "learned_semantic_balanced_subject_leakage": leak("learned_semantic_balanced_listener_responsibility"),
        "learned_semantic_conservative_subject_leakage": leak("learned_semantic_conservative_listener_responsibility"),
        "learned_semantic_relative_balanced_subject_leakage": leak("learned_semantic_relative_balanced_listener_responsibility"),
        "learned_semantic_relative_conservative_subject_leakage": leak("learned_semantic_relative_conservative_listener_responsibility"),
        "learned_family_balanced_subject_leakage": leak("learned_family_balanced_listener_responsibility"),
        "learned_generic_balanced_subject_leakage": leak("learned_generic_balanced_listener_responsibility"),
        "direct_semantic_subject_leakage": leak("direct_semantic_listener_responsibility"),
        "global_transport_subject_leakage": leak("global_transported_prototype"),
        "raw_subject_leakage": leak("raw_lifelog_pca"),
    }


def build_markdown(summary: dict[str, Any], metrics: pd.DataFrame, leakage: pd.DataFrame, pretext: pd.DataFrame) -> str:
    subject_all = metrics[(metrics["split"].eq("subject_heldout")) & (metrics["target"].eq("all"))].sort_values("logloss")
    row_all = metrics[(metrics["split"].eq("row_block_holdout")) & (metrics["target"].eq("all"))].sort_values("logloss")
    chrono_all = metrics[(metrics["split"].eq("chronological_holdout")) & (metrics["target"].eq("all"))].sort_values("logloss")
    pretext_all = pretext[pretext["target"].eq("all")].sort_values(["split", "feature_set"])
    target_subject = metrics[
        metrics["split"].eq("subject_heldout")
        & metrics["target"].isin(TARGETS)
        & metrics["feature_set"].eq(f"{summary['subject_best_learned_feature_set']}")
    ].sort_values("target")
    subject_leak = leakage[leakage["split"].eq("subject_heldout")].sort_values("subject_id_accuracy")
    return f"""# Learned Listener Responsibility Pretext Core

## 한 줄 요약

이 실험은 hand-coded listener profile을 그대로 쓰지 않는다.
OG visible human-life context만 보고 transported prototype reliability에서 만든
hidden listener responsibility field를 예측한다.

```text
visible human-life context
  -> hidden transported listener-responsibility field
  -> frozen subject-heldout / row-block probes
```

## 판정

- verdict: `{summary["verdict"]}`
- public LB ledger 사용: `{summary["uses_public_score_ledger"]}`
- prior submission probability 사용: `{summary["uses_prior_submission_probabilities"]}`
- proprietary embedding API 사용: `{summary["uses_proprietary_embedding_api"]}`
- label을 pretext target으로 사용: `{summary["uses_label_as_pretext_target"]}`
- pretext teacher: `{summary["pretext_teacher"]}`
- context encoder: `{summary["context_encoder"]}`

## 핵심 수치

- best learned feature set: `{summary["subject_best_learned_feature_set"]}`
- subject best learned logloss: `{format_float(summary["subject_best_learned_logloss"], 6)}`
- subject global transport logloss: `{format_float(summary["subject_global_transport_logloss"], 6)}`
- subject direct semantic logloss: `{format_float(summary["subject_direct_semantic_logloss"], 6)}`
- subject prior logloss: `{format_float(summary["subject_prior_logloss"], 6)}`
- delta vs prior: `{format_float(summary["subject_best_learned_delta_vs_prior"], 6)}`
- delta vs raw lifelog PCA: `{format_float(summary["subject_best_learned_delta_vs_raw"], 6)}`
- delta vs global transport: `{format_float(summary["subject_best_learned_delta_vs_global"], 6)}`
- delta vs direct semantic: `{format_float(summary["subject_best_learned_delta_vs_direct_semantic"], 6)}`
- row-block delta vs global: `{format_float(summary["row_block_best_learned_delta_vs_global"], 6)}`
- chronological delta vs global: `{format_float(summary["chronological_best_learned_delta_vs_global"], 6)}`

## Label-Free Pretext Quality

{markdown_table(pretext_all, ["split", "feature_set", "pretext_cross_entropy", "prior_cross_entropy", "ce_lift_vs_prior", "ce_lift_vs_uniform", "top1_match_rate"], max_rows=30)}

## Subject-Heldout Frozen Probe

{markdown_table(subject_all, ["feature_set", "logloss", "auc"], max_rows=20)}

## Best Learned Target Probe

{markdown_table(target_subject, ["target", "logloss", "auc"], max_rows=10)}

## Row-Block Frozen Probe

{markdown_table(row_all, ["feature_set", "logloss", "auc"], max_rows=20)}

## Chronological Frozen Probe

{markdown_table(chrono_all, ["feature_set", "logloss", "auc"], max_rows=20)}

## Subject Leakage Diagnostic

{markdown_table(subject_leak, ["feature_set", "subject_id_accuracy", "chance_accuracy", "leakage_lift_vs_chance"], max_rows=12)}

## 해석

이 실험은 HS-JEPA를 다음 주장으로 좁힌다.

```text
listener responsibility는 사람이 target 설명으로 고정하는 profile이 아니라,
visible human context에서 hidden transported grammar를 예측하는 pretext여야 한다.
```

성공이면:

```text
HS-JEPA core can learn a listener-responsibility interface without labels.
```

실패이면:

```text
transported grammar는 존재하지만 listener responsibility를 raw context encoder만으로
학습하기에는 teacher나 objective가 아직 약하다. 다음 core는 future/cohort consistency를
teacher에 포함해야 한다.
```
"""


def run() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    PAPER_DOC.parent.mkdir(parents=True, exist_ok=True)
    frame_all, _labels = load_frames()
    train_frame = frame_all[frame_all["split"].eq("train")].reset_index(drop=True)
    catalog = catalog_features(frame_all)
    views = view_columns(catalog)
    context_cols = sorted(set(catalog.raw_numeric + catalog.calendar + catalog.core_state))
    context = train_frame[context_cols].reset_index(drop=True)
    relative_context = subject_relative_context(train_frame, context).reset_index(drop=True)

    metric_parts: list[pd.DataFrame] = []
    leakage_parts: list[pd.DataFrame] = []
    pretext_parts: list[pd.DataFrame] = []
    for split_name in ["subject_heldout", "chronological_holdout", "row_block_holdout"]:
        metrics, leakage, pretext = evaluate_split_package(
            split_name,
            train_frame,
            context,
            relative_context,
            catalog.raw_numeric,
            views,
        )
        metric_parts.append(metrics)
        leakage_parts.append(leakage)
        pretext_parts.append(pretext)

    metrics = pd.concat(metric_parts, ignore_index=True, sort=False)
    leakage = pd.concat(leakage_parts, ignore_index=True, sort=False)
    pretext = pd.concat(pretext_parts, ignore_index=True, sort=False)
    summary = summarize(metrics, leakage, pretext)

    metrics.to_csv(OUT_DIR / "learned_listener_responsibility_probe_metrics.csv", index=False)
    leakage.to_csv(OUT_DIR / "learned_listener_responsibility_subject_leakage.csv", index=False)
    pretext.to_csv(OUT_DIR / "learned_listener_responsibility_pretext_metrics.csv", index=False)
    (OUT_DIR / "learned_listener_responsibility_pretext_summary.json").write_text(
        json.dumps(json_safe(summary), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    doc = build_markdown(summary, metrics, leakage, pretext)
    (OUT_DIR / "LEARNED_LISTENER_RESPONSIBILITY_PRETEXT_CORE_KO.md").write_text(doc, encoding="utf-8")
    PAPER_DOC.write_text(doc, encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(json_safe(run()), ensure_ascii=False, indent=2))
