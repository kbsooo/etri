#!/usr/bin/env python3
"""HS-JEPA invariant listener-responsibility pretext experiment.

The learned listener-responsibility pretext showed that responsibility can be
predicted from visible context, but absolute-context variants had high subject
leakage.  This experiment changes the hidden target:

    current transported responsibility
      + within-subject future episode consistency
      + cross-subject cohort consistency
      -> invariant listener-responsibility teacher

The model then predicts that teacher from subject-relative visible context.
Labels are used only after the representation is frozen.
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
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hsjepa_core.run_human_state_world_model_core import subject_leakage_probe  # noqa: E402
from hsjepa_core.run_label_free_transported_listener_responsibility_core import (  # noqa: E402
    SEMANTIC_TARGET_PROFILES,
    build_label_free_listener_features,
    evaluate_target_specific_split,
    global_transport_cols,
    load_transport_state,
    split_folds,
)
from hsjepa_core.run_learned_listener_responsibility_pretext_core import (  # noqa: E402
    aggregate_pretext,
    finite_frame,
    flatten_cols,
    json_safe,
    learned_listener_features,
    make_responsibility_predictor,
    normalize_rows,
    responsibility_features_from_weights,
    softmax_rows,
    subject_relative_context,
    view_teacher_weights,
)
from hsjepa_core.run_lifelog_core_state_evidence import (  # noqa: E402
    TARGETS,
    catalog_features,
    format_float,
    load_frames,
    markdown_table,
    view_columns,
)


OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "invariant_listener_responsibility_pretext_core"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "INVARIANT_LISTENER_RESPONSIBILITY_PRETEXT_CORE_KO.md"
RANDOM_SEED = 20260614


def temporal_consistency_teacher(train_frame: pd.DataFrame, teacher: np.ndarray) -> np.ndarray:
    out = np.zeros_like(teacher, dtype=np.float64)
    mass = np.zeros((len(teacher), 1), dtype=np.float64)
    ordered = train_frame[["subject_id", "lifelog_date"]].copy()
    ordered["lifelog_date"] = pd.to_datetime(ordered["lifelog_date"], errors="coerce")
    ordered["_row"] = np.arange(len(train_frame))
    for _, part in ordered.sort_values(["subject_id", "lifelog_date", "_row"]).groupby("subject_id", observed=True):
        rows = part["_row"].to_numpy(dtype=int)
        for pos, row in enumerate(rows):
            for offset, weight in [(0, 0.55), (1, 0.30), (-1, 0.15)]:
                src_pos = pos + offset
                if 0 <= src_pos < len(rows):
                    out[row] += weight * teacher[rows[src_pos]]
                    mass[row, 0] += weight
    return normalize_rows(out / np.maximum(mass, 1e-12))


def transformed_context(context: pd.DataFrame) -> np.ndarray:
    n_components = min(24, max(2, min(context.shape[0] - 1, context.shape[1])))
    pipe = make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(),
        PCA(n_components=n_components, random_state=RANDOM_SEED),
    )
    return pipe.fit_transform(finite_frame(context, list(context.columns)))


def cohort_consistency_teacher(
    train_frame: pd.DataFrame,
    relative_context: pd.DataFrame,
    teacher: np.ndarray,
    neighbor_count: int = 8,
) -> np.ndarray:
    x = transformed_context(relative_context)
    n_neighbors = min(len(train_frame), max(12, neighbor_count * 5))
    nn = NearestNeighbors(n_neighbors=n_neighbors, metric="euclidean")
    nn.fit(x)
    _, idx = nn.kneighbors(x)
    subject = train_frame["subject_id"].astype(str).to_numpy()
    global_mean = teacher.mean(axis=0)
    out = np.zeros_like(teacher, dtype=np.float64)
    for row in range(len(train_frame)):
        candidates = [
            int(item)
            for item in idx[row]
            if int(item) != row and subject[int(item)] != subject[row]
        ][:neighbor_count]
        if candidates:
            out[row] = teacher[candidates].mean(axis=0)
        else:
            out[row] = global_mean
    return normalize_rows(out)


def consistency_teacher(
    train_frame: pd.DataFrame,
    relative_context: pd.DataFrame,
    state: pd.DataFrame,
    views: dict[str, list[str]],
    profile: dict[str, float],
    mode: str,
) -> np.ndarray:
    current = view_teacher_weights(state, views, profile)
    future = temporal_consistency_teacher(train_frame, current)
    cohort = cohort_consistency_teacher(train_frame, relative_context, current)
    if mode == "future_only":
        return future
    if mode == "cohort_only":
        return cohort
    if mode == "future_cohort":
        return normalize_rows(0.55 * future + 0.45 * cohort)
    if mode == "invariant_mix":
        return normalize_rows(0.45 * current + 0.30 * future + 0.25 * cohort)
    raise ValueError(f"unknown consistency teacher mode: {mode}")


def learned_features_from_teacher(
    train_frame: pd.DataFrame,
    context: pd.DataFrame,
    state: pd.DataFrame,
    views: dict[str, list[str]],
    teacher_by_target: dict[str, np.ndarray],
    folds: list[tuple[np.ndarray, np.ndarray]],
    split_name: str,
    feature_prefix: str,
    responsibility_blend: float,
    teacher_source: str,
) -> tuple[pd.DataFrame, dict[str, list[str]], pd.DataFrame]:
    context = context.reset_index(drop=True)
    all_features = pd.DataFrame(index=state.index)
    target_cols: dict[str, list[str]] = {}
    pretext_rows: list[dict[str, Any]] = []
    view_count = next(iter(teacher_by_target.values())).shape[1]

    for target in TARGETS:
        teacher = teacher_by_target[target]
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
                model.fit(
                    finite_frame(context.iloc[tr_idx], list(context.columns)),
                    np.log(np.clip(train_teacher, 1e-5, 1.0)),
                )
                raw_pred = softmax_rows(model.predict(finite_frame(context.iloc[va_idx], list(context.columns))))
            pred = normalize_rows((1.0 - responsibility_blend) * prior + responsibility_blend * raw_pred)
            predicted[va_idx] = pred

            y = teacher[va_idx]
            ce_pred = -float(np.mean(np.sum(y * np.log(np.clip(pred, 1e-12, 1.0)), axis=1)))
            ce_prior = -float(np.mean(np.sum(y * np.log(np.clip(prior, 1e-12, 1.0)), axis=1)))
            uniform_ce = math.log(max(2, view_count))
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
                    "top1_match_rate": float(np.mean(np.argmax(y, axis=1) == np.argmax(pred, axis=1))),
                    "train_rows": int(len(tr_idx)),
                    "validation_rows": int(len(va_idx)),
                    "uses_public_score": False,
                    "uses_train_labels_for_pretext": False,
                    "teacher_source": teacher_source,
                    "responsibility_blend": responsibility_blend,
                }
            )
        if not evaluated.all():
            missing = ~evaluated
            predicted[missing] = normalize_rows(
                np.tile(teacher[evaluated].mean(axis=0), (int(missing.sum()), 1))
            )
        part = responsibility_features_from_weights(state, views, predicted, f"{feature_prefix}_{target}")
        all_features = pd.concat([all_features, part], axis=1)
        target_cols[target] = list(part.columns)
    return all_features, target_cols, pd.DataFrame(pretext_rows)


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
    current_relative, current_relative_cols, current_relative_pretext = learned_listener_features(
        train_frame,
        relative_context,
        state,
        views,
        SEMANTIC_TARGET_PROFILES,
        folds,
        split_name,
        "current_relative_semantic_balanced",
        0.35,
    )

    configs = [
        ("invariant_mix_relative_balanced", "invariant_mix", 0.35),
        ("invariant_mix_relative_conservative", "invariant_mix", 0.15),
        ("future_cohort_relative_balanced", "future_cohort", 0.35),
        ("future_only_relative_balanced", "future_only", 0.35),
        ("cohort_only_relative_balanced", "cohort_only", 0.35),
    ]
    learned_parts: list[pd.DataFrame] = [current_relative.reset_index(drop=True)]
    learned_maps: dict[str, dict[str, list[str]]] = {
        "current_relative_semantic_balanced_listener_responsibility": current_relative_cols
    }
    pretext_parts: list[pd.DataFrame] = [current_relative_pretext]

    teacher_cache: dict[tuple[str, str], np.ndarray] = {}
    for name, mode, blend in configs:
        teacher_by_target = {}
        for target in TARGETS:
            key = (mode, target)
            teacher_cache[key] = consistency_teacher(
                train_frame,
                relative_context,
                state,
                views,
                SEMANTIC_TARGET_PROFILES[target],
                mode,
            )
            teacher_by_target[target] = teacher_cache[key]
        part, cols, pretext = learned_features_from_teacher(
            train_frame,
            relative_context,
            state,
            views,
            teacher_by_target,
            folds,
            split_name,
            name,
            blend,
            f"{mode}_transported_prototype_reliability",
        )
        learned_parts.append(part.reset_index(drop=True))
        learned_maps[f"{name}_listener_responsibility"] = cols
        pretext_parts.append(pretext)

    features = pd.concat(
        [
            train_frame[raw_cols].reset_index(drop=True),
            state.reset_index(drop=True),
            semantic_direct.reset_index(drop=True),
            *learned_parts,
        ],
        axis=1,
    )
    global_cols = global_transport_cols(views)
    feature_maps = {
        "prior_only": {target: [] for target in TARGETS},
        "raw_lifelog_pca": {target: raw_cols for target in TARGETS},
        "global_transported_prototype": {target: global_cols for target in TARGETS},
        "direct_semantic_listener_responsibility": semantic_direct_cols,
        **learned_maps,
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
        **{name: flatten_cols(cols) for name, cols in learned_maps.items()},
    }
    leakage = subject_leakage_probe(train_frame, features, leakage_sets)
    leakage.insert(0, "split", split_name)
    pretext = aggregate_pretext(pd.concat(pretext_parts, ignore_index=True))
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

    invariant_sets = sorted(
        subject_all[
            subject_all["feature_set"].str.contains("relative")
            & subject_all["feature_set"].str.endswith("_listener_responsibility_calibrated10")
            & ~subject_all["feature_set"].str.startswith("current_")
        ]["feature_set"].tolist()
    )
    subject_losses = {name: loss(subject_all, name) for name in invariant_sets}
    best_name = min(
        [name for name, value in subject_losses.items() if value is not None],
        key=lambda name: subject_losses[name],
    )
    best = subject_losses[best_name]
    prior = loss(subject_all, "prior_only_calibrated10")
    raw = loss(subject_all, "raw_lifelog_pca_calibrated10")
    global_transport = loss(subject_all, "global_transported_prototype_calibrated10")
    direct_semantic = loss(subject_all, "direct_semantic_listener_responsibility_calibrated10")
    current_relative = loss(subject_all, "current_relative_semantic_balanced_listener_responsibility_calibrated10")
    best_row = loss(row_all, best_name)
    best_chrono = loss(chrono_all, best_name)
    global_row = loss(row_all, "global_transported_prototype_calibrated10")
    global_chrono = loss(chrono_all, "global_transported_prototype_calibrated10")

    verdict = "invariant_listener_responsibility_negative"
    if best is not None and prior is not None and best < prior:
        verdict = "invariant_listener_responsibility_prior_positive"
        if current_relative is not None and best < current_relative:
            verdict = "invariant_listener_responsibility_beats_current_positive"
        if global_transport is not None and best < global_transport:
            verdict = "invariant_listener_responsibility_global_positive"

    pretext_rows = {row["feature_set"]: row.to_dict() for _, row in subject_pretext.iterrows()}
    return {
        "package": "invariant_listener_responsibility_pretext_core",
        "status": "invariant_listener_responsibility_pretext_core_ready",
        "verdict": verdict,
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "uses_label_as_pretext_target": False,
        "teacher": "current_plus_future_plus_cross_subject_cohort_transport_reliability",
        "context_encoder": "subject_relative_visible_lifelog_context",
        "subject_prior_logloss": prior,
        "subject_raw_logloss": raw,
        "subject_global_transport_logloss": global_transport,
        "subject_direct_semantic_logloss": direct_semantic,
        "subject_current_relative_logloss": current_relative,
        "subject_best_invariant_feature_set": best_name,
        "subject_best_invariant_logloss": best,
        "subject_best_invariant_delta_vs_prior": None if best is None or prior is None else best - prior,
        "subject_best_invariant_delta_vs_raw": None if best is None or raw is None else best - raw,
        "subject_best_invariant_delta_vs_global": None if best is None or global_transport is None else best - global_transport,
        "subject_best_invariant_delta_vs_direct_semantic": None if best is None or direct_semantic is None else best - direct_semantic,
        "subject_best_invariant_delta_vs_current_relative": None if best is None or current_relative is None else best - current_relative,
        "row_block_best_invariant_delta_vs_global": None if best_row is None or global_row is None else best_row - global_row,
        "chronological_best_invariant_delta_vs_global": None if best_chrono is None or global_chrono is None else best_chrono - global_chrono,
        "subject_pretext_all": pretext_rows,
        "subject_best_invariant_leakage": leak(best_name.replace("_calibrated10", "")),
        "current_relative_subject_leakage": leak("current_relative_semantic_balanced_listener_responsibility"),
        "global_transport_subject_leakage": leak("global_transported_prototype"),
        "raw_subject_leakage": leak("raw_lifelog_pca"),
    }


def build_markdown(summary: dict[str, Any], metrics: pd.DataFrame, leakage: pd.DataFrame, pretext: pd.DataFrame) -> str:
    subject_all = metrics[(metrics["split"].eq("subject_heldout")) & (metrics["target"].eq("all"))].sort_values("logloss")
    row_all = metrics[(metrics["split"].eq("row_block_holdout")) & (metrics["target"].eq("all"))].sort_values("logloss")
    chrono_all = metrics[(metrics["split"].eq("chronological_holdout")) & (metrics["target"].eq("all"))].sort_values("logloss")
    pretext_all = pretext[pretext["target"].eq("all")].sort_values(["split", "feature_set"])
    subject_leak = leakage[leakage["split"].eq("subject_heldout")].sort_values("subject_id_accuracy")
    return f"""# Invariant Listener Responsibility Pretext Core

## 한 줄 요약

이 실험은 현재 row의 listener responsibility만 맞히지 않는다.
같은 subject의 인접 episode와 다른 subject의 유사 episode를 함께 보아
future/cohort-consistent listener responsibility teacher를 만든 뒤,
subject-relative visible context가 그 hidden teacher를 예측하게 한다.

```text
current transported responsibility
  + future episode consistency
  + cross-subject cohort consistency
  -> invariant listener responsibility teacher
  -> subject-relative context prediction
```

## 판정

- verdict: `{summary["verdict"]}`
- public LB ledger 사용: `{summary["uses_public_score_ledger"]}`
- prior submission probability 사용: `{summary["uses_prior_submission_probabilities"]}`
- proprietary embedding API 사용: `{summary["uses_proprietary_embedding_api"]}`
- label을 pretext target으로 사용: `{summary["uses_label_as_pretext_target"]}`
- teacher: `{summary["teacher"]}`
- context encoder: `{summary["context_encoder"]}`

## 핵심 수치

- best invariant feature set: `{summary["subject_best_invariant_feature_set"]}`
- subject best invariant logloss: `{format_float(summary["subject_best_invariant_logloss"], 6)}`
- subject current-relative logloss: `{format_float(summary["subject_current_relative_logloss"], 6)}`
- subject global transport logloss: `{format_float(summary["subject_global_transport_logloss"], 6)}`
- subject direct semantic logloss: `{format_float(summary["subject_direct_semantic_logloss"], 6)}`
- subject prior logloss: `{format_float(summary["subject_prior_logloss"], 6)}`
- delta vs current-relative: `{format_float(summary["subject_best_invariant_delta_vs_current_relative"], 6)}`
- delta vs direct semantic: `{format_float(summary["subject_best_invariant_delta_vs_direct_semantic"], 6)}`
- delta vs prior: `{format_float(summary["subject_best_invariant_delta_vs_prior"], 6)}`
- delta vs raw lifelog PCA: `{format_float(summary["subject_best_invariant_delta_vs_raw"], 6)}`
- delta vs global transport: `{format_float(summary["subject_best_invariant_delta_vs_global"], 6)}`
- row-block delta vs global: `{format_float(summary["row_block_best_invariant_delta_vs_global"], 6)}`
- chronological delta vs global: `{format_float(summary["chronological_best_invariant_delta_vs_global"], 6)}`

## Label-Free Pretext Quality

{markdown_table(pretext_all, ["split", "feature_set", "pretext_cross_entropy", "prior_cross_entropy", "ce_lift_vs_prior", "ce_lift_vs_uniform", "top1_match_rate"], max_rows=30)}

## Subject-Heldout Frozen Probe

{markdown_table(subject_all, ["feature_set", "logloss", "auc"], max_rows=20)}

## Row-Block Frozen Probe

{markdown_table(row_all, ["feature_set", "logloss", "auc"], max_rows=20)}

## Chronological Frozen Probe

{markdown_table(chrono_all, ["feature_set", "logloss", "auc"], max_rows=20)}

## Subject Leakage Diagnostic

{markdown_table(subject_leak, ["feature_set", "subject_id_accuracy", "chance_accuracy", "leakage_lift_vs_chance"], max_rows=12)}

## 해석

positive이면:

```text
HS-JEPA listener responsibility becomes more stable when the hidden teacher
is constrained by future and cohort consistency rather than current-row reliability alone.
```

negative이면:

```text
future/cohort smoothing destroys target-specific listener signal, so invariant responsibility
must be learned as a multi-head objective rather than a smoothed single teacher.
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

    metrics.to_csv(OUT_DIR / "invariant_listener_responsibility_probe_metrics.csv", index=False)
    leakage.to_csv(OUT_DIR / "invariant_listener_responsibility_subject_leakage.csv", index=False)
    pretext.to_csv(OUT_DIR / "invariant_listener_responsibility_pretext_metrics.csv", index=False)
    (OUT_DIR / "invariant_listener_responsibility_pretext_summary.json").write_text(
        json.dumps(json_safe(summary), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    doc = build_markdown(summary, metrics, leakage, pretext)
    (OUT_DIR / "INVARIANT_LISTENER_RESPONSIBILITY_PRETEXT_CORE_KO.md").write_text(doc, encoding="utf-8")
    PAPER_DOC.write_text(doc, encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(json_safe(run()), ensure_ascii=False, indent=2))
