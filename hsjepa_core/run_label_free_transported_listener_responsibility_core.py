#!/usr/bin/env python3
"""HS-JEPA label-free transported listener responsibility experiment.

Previous transported-prototype listener readout selected a target-specific view
with frozen labels.  This run removes that selection step:

    target description + transported prototype confidence/energy
      -> label-free listener responsibility
      -> frozen subject-heldout / row-block probes

The listener profiles are fixed from human-readable target semantics.  Labels
are used only after the representation is fixed.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hsjepa_core.human_state_world_model import finite_frame  # noqa: E402
from hsjepa_core.run_cross_subject_prototype_transport_core import (  # noqa: E402
    OUT_DIR as TRANSPORT_OUT_DIR,
    row_block_folds,
    run as run_transport_core,
)
from hsjepa_core.run_human_state_prototype_grammar_core import PROTOTYPES_PER_VIEW  # noqa: E402
from hsjepa_core.run_human_state_world_model_core import (  # noqa: E402
    PROBE_CALIBRATION_SHRINK,
    chronological_folds,
    make_linear_probe,
    subject_folds,
    subject_leakage_probe,
)
from hsjepa_core.run_lifelog_core_state_evidence import (  # noqa: E402
    TARGETS,
    catalog_features,
    format_float,
    load_frames,
    markdown_table,
    safe_auc,
    view_columns,
)


OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "label_free_transported_listener_responsibility_core"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "LABEL_FREE_TRANSPORTED_LISTENER_RESPONSIBILITY_CORE_KO.md"


SEMANTIC_TARGET_PROFILES: dict[str, dict[str, float]] = {
    # Q1: subjective sleep satisfaction is read as body recovery plus daily routine/mobility context.
    "Q1": {
        "body_activity_sleep": 1.4,
        "mobility_environment": 1.1,
        "calendar_rhythm": 1.0,
    },
    # Q2: sleep intervention/load is treated as routine disruption and phone/social arousal.
    "Q2": {
        "calendar_rhythm": 1.3,
        "phone_behavior": 1.1,
        "app_social_context": 1.0,
    },
    # Q3: sleep quality is an interaction between sleep/body state and late social/cognitive context.
    "Q3": {
        "body_activity_sleep": 1.3,
        "app_social_context": 1.1,
        "phone_behavior": 1.0,
    },
    # S1-S4 are objective sleep-stage related, so body/sleep and rhythm dominate.
    "S1": {
        "body_activity_sleep": 1.5,
        "calendar_rhythm": 1.0,
    },
    "S2": {
        "body_activity_sleep": 1.4,
        "calendar_rhythm": 1.1,
        "mobility_environment": 0.7,
    },
    "S3": {
        "calendar_rhythm": 1.3,
        "phone_behavior": 1.0,
        "app_social_context": 0.8,
    },
    "S4": {
        "body_activity_sleep": 1.3,
        "phone_behavior": 1.0,
        "app_social_context": 0.8,
    },
}

FAMILY_TARGET_PROFILES: dict[str, dict[str, float]] = {
    target: (
        {
            "app_social_context": 1.3,
            "phone_behavior": 1.2,
            "calendar_rhythm": 1.0,
            "mobility_environment": 0.8,
            "body_activity_sleep": 0.8,
        }
        if target.startswith("Q")
        else {
            "body_activity_sleep": 1.4,
            "calendar_rhythm": 1.2,
            "mobility_environment": 0.8,
            "phone_behavior": 0.5,
            "app_social_context": 0.5,
        }
    )
    for target in TARGETS
}


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


def ensure_transport_outputs() -> None:
    required = [
        TRANSPORT_OUT_DIR / "cross_subject_transport_state_subject_heldout.csv",
        TRANSPORT_OUT_DIR / "cross_subject_transport_state_chronological_holdout.csv",
        TRANSPORT_OUT_DIR / "cross_subject_transport_state_row_block_holdout.csv",
    ]
    if not all(path.exists() for path in required):
        run_transport_core()


def load_transport_state(split_name: str) -> pd.DataFrame:
    ensure_transport_outputs()
    return pd.read_csv(TRANSPORT_OUT_DIR / f"cross_subject_transport_state_{split_name}.csv")


def view_probability_cols(view: str) -> list[str]:
    return [f"cspg_pred_{view}_p{proto}" for proto in range(PROTOTYPES_PER_VIEW)]


def view_stat_cols(view: str) -> list[str]:
    return [
        f"cspg_pred_{view}_confidence",
        f"cspg_pred_{view}_entropy",
        f"cspg_energy_{view}",
        f"cspg_energy_lift_{view}",
    ]


def global_transport_cols(views: dict[str, list[str]]) -> list[str]:
    cols: list[str] = []
    for view in views:
        cols.extend(view_probability_cols(view))
        cols.extend(view_stat_cols(view))
    cols.extend(
        [
            "cspg_energy_mean",
            "cspg_energy_max",
            "cspg_energy_rank_mean",
            "cspg_energy_lift_mean",
            "cspg_confidence_mean",
            "cspg_entropy_mean",
        ]
    )
    return sorted(set(cols))


def split_folds(split_name: str, frame: pd.DataFrame) -> list[tuple[np.ndarray, np.ndarray]]:
    if split_name == "subject_heldout":
        return subject_folds(frame)
    if split_name == "chronological_holdout":
        return chronological_folds(frame)
    if split_name == "row_block_holdout":
        return row_block_folds(frame)
    raise ValueError(f"unknown split: {split_name}")


def profile_responsibility(
    state: pd.DataFrame,
    views: dict[str, list[str]],
    profile: dict[str, float],
) -> pd.DataFrame:
    available = [view for view in views if view in profile]
    if not available:
        raise ValueError("profile has no matching views")
    base = np.array([profile[view] for view in available], dtype=np.float64)
    confidence = np.column_stack(
        [state[f"cspg_pred_{view}_confidence"].to_numpy(dtype=np.float64) for view in available]
    )
    entropy = np.column_stack(
        [state[f"cspg_pred_{view}_entropy"].to_numpy(dtype=np.float64) for view in available]
    )
    lift = np.column_stack(
        [state[f"cspg_energy_lift_{view}"].to_numpy(dtype=np.float64) for view in available]
    )
    reliability = np.clip(confidence, 0.0, 1.0) * np.clip(1.0 - entropy, 0.0, 1.0) * np.exp(
        0.25 * np.clip(lift, -3.0, 3.0)
    )
    weights = reliability * base.reshape(1, -1)
    weights = weights / np.maximum(weights.sum(axis=1, keepdims=True), 1e-12)

    out = pd.DataFrame(index=state.index)
    for proto in range(PROTOTYPES_PER_VIEW):
        values = np.column_stack(
            [state[f"cspg_pred_{view}_p{proto}"].to_numpy(dtype=np.float64) for view in available]
        )
        out[f"p{proto}"] = np.sum(weights * values, axis=1)
    for stat in ["confidence", "entropy"]:
        values = np.column_stack(
            [state[f"cspg_pred_{view}_{stat}"].to_numpy(dtype=np.float64) for view in available]
        )
        out[f"{stat}_weighted"] = np.sum(weights * values, axis=1)
    for stat in ["energy", "energy_lift"]:
        values = np.column_stack(
            [state[f"cspg_{stat}_{view}"].to_numpy(dtype=np.float64) for view in available]
        )
        out[f"{stat}_weighted"] = np.sum(weights * values, axis=1)
    out["responsibility_max"] = weights.max(axis=1)
    out["responsibility_entropy"] = -np.sum(weights * np.log(np.clip(weights, 1e-12, 1.0)), axis=1) / math.log(
        max(2, len(available))
    )
    for pos, view in enumerate(available):
        out[f"w_{view}"] = weights[:, pos]
    return out


def build_label_free_listener_features(
    state: pd.DataFrame,
    views: dict[str, list[str]],
    profiles: dict[str, dict[str, float]],
    prefix: str,
) -> tuple[pd.DataFrame, dict[str, list[str]]]:
    features = pd.DataFrame(index=state.index)
    target_cols: dict[str, list[str]] = {}
    for target in TARGETS:
        part = profile_responsibility(state, views, profiles[target])
        rename = {col: f"{prefix}_{target}_{col}" for col in part.columns}
        part = part.rename(columns=rename)
        features = pd.concat([features, part], axis=1)
        target_cols[target] = list(part.columns)
    return features, target_cols


def evaluate_target_specific_split(
    train_frame: pd.DataFrame,
    features: pd.DataFrame,
    feature_maps: dict[str, dict[str, list[str]]],
    split_name: str,
    folds: list[tuple[np.ndarray, np.ndarray]],
    shrink: float = PROBE_CALIBRATION_SHRINK,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    y_all = train_frame[TARGETS].astype(int).reset_index(drop=True)
    features = features.reset_index(drop=True)
    metric_rows: list[dict[str, Any]] = []
    prediction_rows: list[dict[str, Any]] = []
    for feature_name, target_to_cols in feature_maps.items():
        calibrated_losses: list[float] = []
        calibrated_aucs: list[float] = []
        raw_losses: list[float] = []
        raw_aucs: list[float] = []
        for target in TARGETS:
            oof = np.full(len(train_frame), np.nan, dtype=np.float64)
            prior_oof = np.full(len(train_frame), np.nan, dtype=np.float64)
            evaluated = np.zeros(len(train_frame), dtype=bool)
            cols = target_to_cols[target]
            for fold, (tr_idx, va_idx) in enumerate(folds):
                evaluated[va_idx] = True
                y_train = y_all.iloc[tr_idx][target].to_numpy(dtype=int)
                y_val = y_all.iloc[va_idx][target].to_numpy(dtype=int)
                prior = float(np.clip(y_train.mean(), 1e-5, 1 - 1e-5))
                if not cols or len(np.unique(y_train)) < 2:
                    pred = np.full(len(va_idx), prior, dtype=np.float64)
                else:
                    model = make_linear_probe(feature_name, len(cols))
                    model.fit(finite_frame(features.iloc[tr_idx], cols), y_train)
                    pred = np.clip(
                        model.predict_proba(finite_frame(features.iloc[va_idx], cols))[:, 1],
                        1e-5,
                        1 - 1e-5,
                    )
                oof[va_idx] = pred
                prior_oof[va_idx] = prior
                for pos, row in enumerate(va_idx):
                    prediction_rows.append(
                        {
                            "split": split_name,
                            "feature_set": feature_name,
                            "fold": fold,
                            "row": int(row),
                            "target": target,
                            "y": int(y_val[pos]),
                            "prediction": float(pred[pos]),
                            "fold_prior": prior,
                        }
                    )
            y = y_all.loc[evaluated, target].to_numpy(dtype=int)
            raw = oof[evaluated]
            prior = prior_oof[evaluated]
            calibrated = np.clip(prior + shrink * (raw - prior), 1e-5, 1 - 1e-5)
            raw_loss = float(log_loss(y, raw, labels=[0, 1]))
            raw_auc = safe_auc(y, raw)
            calibrated_loss = float(log_loss(y, calibrated, labels=[0, 1]))
            calibrated_auc = safe_auc(y, calibrated)
            raw_losses.append(raw_loss)
            calibrated_losses.append(calibrated_loss)
            if raw_auc is not None:
                raw_aucs.append(raw_auc)
            if calibrated_auc is not None:
                calibrated_aucs.append(calibrated_auc)
            for suffix, loss, auc in [
                ("", raw_loss, raw_auc),
                (f"_calibrated{int(shrink * 100):02d}", calibrated_loss, calibrated_auc),
            ]:
                metric_rows.append(
                    {
                        "split": split_name,
                        "feature_set": f"{feature_name}{suffix}",
                        "target": target,
                        "logloss": loss,
                        "auc": auc,
                        "uses_public_score": False,
                        "uses_train_labels": True,
                        "core_representation_frozen": True,
                        "listener_profile_source": "target_description_not_labels",
                        "probe_calibration_shrink": None if not suffix else shrink,
                        "evaluated_rows": int(evaluated.sum()),
                    }
                )
        for suffix, losses, aucs in [
            ("", raw_losses, raw_aucs),
            (f"_calibrated{int(shrink * 100):02d}", calibrated_losses, calibrated_aucs),
        ]:
            metric_rows.append(
                {
                    "split": split_name,
                    "feature_set": f"{feature_name}{suffix}",
                    "target": "all",
                    "logloss": float(np.mean(losses)),
                    "auc": float(np.nanmean(aucs)) if aucs else None,
                    "uses_public_score": False,
                    "uses_train_labels": True,
                    "core_representation_frozen": True,
                    "listener_profile_source": "target_description_not_labels",
                    "probe_calibration_shrink": None if not suffix else shrink,
                    "evaluated_rows": int(len(train_frame)),
                }
            )
    return pd.DataFrame(metric_rows), pd.DataFrame(prediction_rows)


def summarize(metrics: pd.DataFrame, leakage: pd.DataFrame) -> dict[str, Any]:
    subject_all = metrics[(metrics["split"].eq("subject_heldout")) & (metrics["target"].eq("all"))]
    row_all = metrics[(metrics["split"].eq("row_block_holdout")) & (metrics["target"].eq("all"))]
    chrono_all = metrics[(metrics["split"].eq("chronological_holdout")) & (metrics["target"].eq("all"))]

    def loss(frame: pd.DataFrame, feature_set: str) -> float | None:
        part = frame[frame["feature_set"].eq(feature_set)]
        return None if part.empty else float(part["logloss"].iloc[0])

    semantic = loss(subject_all, "label_free_semantic_listener_responsibility_calibrated10")
    family = loss(subject_all, "label_free_family_listener_responsibility_calibrated10")
    global_transport = loss(subject_all, "global_transported_prototype_calibrated10")
    prior = loss(subject_all, "prior_only_calibrated10")
    raw = loss(subject_all, "raw_lifelog_pca_calibrated10")
    semantic_row = loss(row_all, "label_free_semantic_listener_responsibility_calibrated10")
    global_row = loss(row_all, "global_transported_prototype_calibrated10")
    semantic_chrono = loss(chrono_all, "label_free_semantic_listener_responsibility_calibrated10")
    global_chrono = loss(chrono_all, "global_transported_prototype_calibrated10")
    best_subject = subject_all.sort_values("logloss").head(1)
    leak_subject = leakage[leakage["split"].eq("subject_heldout")]
    semantic_leak = leak_subject[leak_subject["feature_set"].eq("label_free_semantic_listener_responsibility")]
    family_leak = leak_subject[leak_subject["feature_set"].eq("label_free_family_listener_responsibility")]
    global_leak = leak_subject[leak_subject["feature_set"].eq("global_transported_prototype")]
    raw_leak = leak_subject[leak_subject["feature_set"].eq("raw_lifelog_pca")]

    verdict = "label_free_listener_responsibility_negative"
    if semantic is not None and prior is not None and semantic < prior:
        verdict = "label_free_listener_responsibility_prior_positive"
        if global_transport is not None and semantic < global_transport:
            verdict = "label_free_listener_responsibility_global_positive"

    return {
        "package": "label_free_transported_listener_responsibility_core",
        "status": "label_free_transported_listener_responsibility_core_ready",
        "verdict": verdict,
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "uses_label_as_pretext_target": False,
        "listener_profile_source": "target_descriptions_and_human_state_semantics",
        "subject_prior_logloss": prior,
        "subject_raw_logloss": raw,
        "subject_global_transport_logloss": global_transport,
        "subject_semantic_listener_logloss": semantic,
        "subject_family_listener_logloss": family,
        "subject_semantic_delta_vs_prior": None if semantic is None or prior is None else semantic - prior,
        "subject_semantic_delta_vs_global": None if semantic is None or global_transport is None else semantic - global_transport,
        "subject_semantic_delta_vs_raw": None if semantic is None or raw is None else semantic - raw,
        "subject_family_delta_vs_global": None if family is None or global_transport is None else family - global_transport,
        "row_block_semantic_delta_vs_global": None if semantic_row is None or global_row is None else semantic_row - global_row,
        "chronological_semantic_delta_vs_global": None if semantic_chrono is None or global_chrono is None else semantic_chrono - global_chrono,
        "subject_best_probe": None if best_subject.empty else best_subject.iloc[0].to_dict(),
        "semantic_listener_subject_leakage": None if semantic_leak.empty else semantic_leak.iloc[0].to_dict(),
        "family_listener_subject_leakage": None if family_leak.empty else family_leak.iloc[0].to_dict(),
        "global_transport_subject_leakage": None if global_leak.empty else global_leak.iloc[0].to_dict(),
        "raw_subject_leakage": None if raw_leak.empty else raw_leak.iloc[0].to_dict(),
        "semantic_target_profiles": SEMANTIC_TARGET_PROFILES,
        "family_target_profiles": FAMILY_TARGET_PROFILES,
    }


def build_markdown(summary: dict[str, Any], metrics: pd.DataFrame, leakage: pd.DataFrame) -> str:
    subject_all = metrics[(metrics["split"].eq("subject_heldout")) & (metrics["target"].eq("all"))].sort_values("logloss")
    row_all = metrics[(metrics["split"].eq("row_block_holdout")) & (metrics["target"].eq("all"))].sort_values("logloss")
    chrono_all = metrics[(metrics["split"].eq("chronological_holdout")) & (metrics["target"].eq("all"))].sort_values("logloss")
    target_subject = metrics[
        metrics["split"].eq("subject_heldout")
        & metrics["target"].isin(TARGETS)
        & metrics["feature_set"].eq("label_free_semantic_listener_responsibility_calibrated10")
    ].sort_values("target")
    subject_leak = leakage[leakage["split"].eq("subject_heldout")].sort_values("subject_id_accuracy")
    return f"""# Label-Free Transported Listener Responsibility Core

## 한 줄 요약

이 실험은 target/listener view를 label probe로 고르지 않는다.
target 설명에서 고정한 human-state listener profile과 transported prototype의 confidence/entropy/energy만으로
label-free listener responsibility를 만든 뒤, frozen probe로만 검증한다.

```text
target description + transported prototype reliability
  -> label-free listener responsibility
  -> frozen subject-heldout / row-block probes
```

## 판정

- verdict: `{summary["verdict"]}`
- public LB ledger 사용: `{summary["uses_public_score_ledger"]}`
- prior submission probability 사용: `{summary["uses_prior_submission_probabilities"]}`
- proprietary embedding API 사용: `{summary["uses_proprietary_embedding_api"]}`
- label을 pretext target으로 사용: `{summary["uses_label_as_pretext_target"]}`
- listener profile source: `{summary["listener_profile_source"]}`

## 핵심 수치

- subject semantic listener logloss: `{format_float(summary["subject_semantic_listener_logloss"], 6)}`
- subject global transport logloss: `{format_float(summary["subject_global_transport_logloss"], 6)}`
- subject prior logloss: `{format_float(summary["subject_prior_logloss"], 6)}`
- delta vs global transport: `{format_float(summary["subject_semantic_delta_vs_global"], 6)}`
- delta vs prior: `{format_float(summary["subject_semantic_delta_vs_prior"], 6)}`
- delta vs raw lifelog PCA: `{format_float(summary["subject_semantic_delta_vs_raw"], 6)}`
- row-block delta vs global: `{format_float(summary["row_block_semantic_delta_vs_global"], 6)}`
- chronological delta vs global: `{format_float(summary["chronological_semantic_delta_vs_global"], 6)}`

## Subject-Heldout Frozen Probe

{markdown_table(subject_all, ["feature_set", "logloss", "auc"], max_rows=20)}

## Target별 Semantic Listener Probe

{markdown_table(target_subject, ["target", "logloss", "auc"], max_rows=10)}

## Row-Block Frozen Probe

{markdown_table(row_all, ["feature_set", "logloss", "auc"], max_rows=20)}

## Chronological Frozen Probe

{markdown_table(chrono_all, ["feature_set", "logloss", "auc"], max_rows=20)}

## Subject Leakage Diagnostic

{markdown_table(subject_leak, ["feature_set", "subject_id_accuracy", "chance_accuracy", "leakage_lift_vs_chance"], max_rows=12)}

## Semantic Target Profiles

```json
{json.dumps(SEMANTIC_TARGET_PROFILES, ensure_ascii=False, indent=2)}
```

## 해석

positive이면:

```text
HS-JEPA can expose a listener-readable transported grammar without selecting routes from labels.
```

negative이면:

```text
Human-semantic listener profiles are not enough.
The previous listener-readout gain mostly came from frozen label selection, so the next core must learn
listener responsibility as a pretext target rather than hand-code it.
```
"""


def run() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    PAPER_DOC.parent.mkdir(parents=True, exist_ok=True)
    ensure_transport_outputs()

    frame_all, _labels = load_frames()
    train_frame = frame_all[frame_all["split"].eq("train")].reset_index(drop=True)
    catalog = catalog_features(frame_all)
    views = view_columns(catalog)

    metric_parts: list[pd.DataFrame] = []
    leakage_parts: list[pd.DataFrame] = []

    for split_name in ["subject_heldout", "chronological_holdout", "row_block_holdout"]:
        state = load_transport_state(split_name)
        semantic_features, semantic_cols = build_label_free_listener_features(
            state,
            views,
            SEMANTIC_TARGET_PROFILES,
            "lftlr_semantic",
        )
        family_features, family_cols = build_label_free_listener_features(
            state,
            views,
            FAMILY_TARGET_PROFILES,
            "lftlr_family",
        )
        features = pd.concat(
            [
                train_frame[catalog.raw_numeric].reset_index(drop=True),
                state.reset_index(drop=True),
                semantic_features.reset_index(drop=True),
                family_features.reset_index(drop=True),
            ],
            axis=1,
        )
        global_cols = global_transport_cols(views)
        feature_maps = {
            "prior_only": {target: [] for target in TARGETS},
            "raw_lifelog_pca": {target: catalog.raw_numeric for target in TARGETS},
            "global_transported_prototype": {target: global_cols for target in TARGETS},
            "label_free_semantic_listener_responsibility": semantic_cols,
            "label_free_family_listener_responsibility": family_cols,
        }
        metrics, _predictions = evaluate_target_specific_split(
            train_frame,
            features,
            feature_maps,
            split_name,
            split_folds(split_name, train_frame),
        )
        leakage_sets = {
            "raw_lifelog_pca": catalog.raw_numeric,
            "global_transported_prototype": global_cols,
            "label_free_semantic_listener_responsibility": sorted(
                set(col for cols in semantic_cols.values() for col in cols)
            ),
            "label_free_family_listener_responsibility": sorted(
                set(col for cols in family_cols.values() for col in cols)
            ),
        }
        leakage = subject_leakage_probe(train_frame, features, leakage_sets)
        leakage.insert(0, "split", split_name)
        metric_parts.append(metrics)
        leakage_parts.append(leakage)

    metrics = pd.concat(metric_parts, ignore_index=True, sort=False)
    leakage = pd.concat(leakage_parts, ignore_index=True, sort=False)
    summary = summarize(metrics, leakage)

    metrics.to_csv(OUT_DIR / "label_free_transported_listener_probe_metrics.csv", index=False)
    leakage.to_csv(OUT_DIR / "label_free_transported_listener_subject_leakage.csv", index=False)
    (OUT_DIR / "label_free_transported_listener_responsibility_summary.json").write_text(
        json.dumps(json_safe(summary), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    doc = build_markdown(summary, metrics, leakage)
    (OUT_DIR / "LABEL_FREE_TRANSPORTED_LISTENER_RESPONSIBILITY_CORE_KO.md").write_text(doc, encoding="utf-8")
    PAPER_DOC.write_text(doc, encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(json_safe(run()), ensure_ascii=False, indent=2))
