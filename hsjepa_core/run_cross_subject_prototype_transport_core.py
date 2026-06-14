#!/usr/bin/env python3
"""HS-JEPA cross-subject prototype transport core experiment.

This is a stricter version of the prototype-grammar evidence:

    train subjects/blocks define a subject-relative episode grammar
      -> held-out subjects/blocks are transported into that grammar
      -> masked context predicts held-out hidden prototype responsibilities
      -> frozen low-trust probes read only transported state

The core never uses public LB, prior submission probabilities, or labels as a
pretext target.  Labels are used only after the transported representation is
fixed.
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
from hsjepa_core.run_human_state_prototype_grammar_core import (  # noqa: E402
    PROTOTYPES_PER_VIEW,
    json_safe,
)
from hsjepa_core.run_human_state_world_model_core import (  # noqa: E402
    calibrated_probe_metrics,
    chronological_folds,
    evaluate_split,
    neighbor_consistency,
    subject_folds,
    subject_leakage_probe,
)
from hsjepa_core.run_lifelog_core_state_evidence import (  # noqa: E402
    catalog_features,
    format_float,
    load_frames,
    markdown_table,
    view_columns,
)


OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "cross_subject_prototype_transport_core"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "CROSS_SUBJECT_PROTOTYPE_TRANSPORT_CORE_KO.md"
RANDOM_SEED = 20260614
LATENT_DIMS_PER_VIEW = 4
LOGISTIC_C = 0.55


def row_block_folds(train_frame: pd.DataFrame, n_blocks: int = 5) -> list[tuple[np.ndarray, np.ndarray]]:
    ordered = train_frame[["subject_id", "lifelog_date"]].copy()
    ordered["lifelog_date"] = pd.to_datetime(ordered["lifelog_date"], errors="coerce")
    ordered["_row"] = np.arange(len(train_frame))
    ordered = ordered.sort_values(["lifelog_date", "subject_id", "_row"])
    blocks = np.array_split(ordered["_row"].to_numpy(dtype=int), n_blocks)
    all_rows = np.arange(len(train_frame), dtype=int)
    folds: list[tuple[np.ndarray, np.ndarray]] = []
    for block in blocks:
        val = np.array(sorted(set(block.tolist())), dtype=int)
        train = np.array([idx for idx in all_rows if idx not in set(val.tolist())], dtype=int)
        if len(train) and len(val):
            folds.append((train, val))
    return folds


def subject_relative_values(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    out = frame.copy()
    grouped = out.groupby("subject_id", observed=True)
    for col in columns:
        values = pd.to_numeric(out[col], errors="coerce")
        mean = grouped[col].transform("mean")
        std = grouped[col].transform("std").replace(0.0, np.nan)
        out[col] = ((values - mean) / std).clip(-5, 5)
    return out


def entropy_rows(proba: np.ndarray) -> np.ndarray:
    k = proba.shape[1]
    return -np.sum(proba * np.log(np.clip(proba, 1e-12, 1.0)), axis=1) / math.log(max(2, k))


def soft_assign(distances: np.ndarray) -> np.ndarray:
    tau = float(np.median(np.min(distances, axis=1)))
    tau = tau if tau > 1e-9 else 1.0
    score = -distances / tau
    score = score - np.max(score, axis=1, keepdims=True)
    exp_score = np.exp(score)
    return exp_score / np.maximum(exp_score.sum(axis=1, keepdims=True), 1e-12)


def fit_latent_models(
    relative_frame: pd.DataFrame,
    views: dict[str, list[str]],
    train_idx: np.ndarray,
    transform_idx: np.ndarray,
) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray]]:
    train_latent: dict[str, np.ndarray] = {}
    transform_latent: dict[str, np.ndarray] = {}
    for view, cols in views.items():
        n_components = max(1, min(LATENT_DIMS_PER_VIEW, len(cols), len(train_idx) - 1))
        model = make_pipeline(
            SimpleImputer(strategy="median"),
            StandardScaler(),
            PCA(n_components=n_components, random_state=RANDOM_SEED),
        )
        model.fit(finite_frame(relative_frame.iloc[train_idx], cols))
        train_latent[view] = np.asarray(
            model.transform(finite_frame(relative_frame.iloc[train_idx], cols)),
            dtype=np.float64,
        )
        transform_latent[view] = np.asarray(
            model.transform(finite_frame(relative_frame.iloc[transform_idx], cols)),
            dtype=np.float64,
        )
    return train_latent, transform_latent


def concat_context(latents: dict[str, np.ndarray], target_view: str) -> np.ndarray:
    parts = [values for view, values in latents.items() if view != target_view]
    return np.hstack(parts)


def make_empty_state(index: pd.Index, views: dict[str, list[str]]) -> pd.DataFrame:
    out = pd.DataFrame(index=index)
    for view in views:
        for proto in range(PROTOTYPES_PER_VIEW):
            out[f"cspg_pred_{view}_p{proto}"] = np.nan
            out[f"cspg_true_{view}_p{proto}"] = np.nan
        out[f"cspg_pred_{view}_confidence"] = np.nan
        out[f"cspg_pred_{view}_entropy"] = np.nan
        out[f"cspg_true_{view}_confidence"] = np.nan
        out[f"cspg_true_{view}_entropy"] = np.nan
        out[f"cspg_energy_{view}"] = np.nan
        out[f"cspg_energy_lift_{view}"] = np.nan
        out[f"cspg_match_{view}"] = np.nan
    return out


def transport_state_for_folds(
    frame: pd.DataFrame,
    relative_frame: pd.DataFrame,
    views: dict[str, list[str]],
    folds: list[tuple[np.ndarray, np.ndarray]],
    split_name: str,
    fill_train_rows: bool = False,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    state = make_empty_state(frame.index, views)
    metric_rows: list[dict[str, Any]] = []
    fold_rows: list[dict[str, Any]] = []

    for fold, (train_idx, val_idx) in enumerate(folds):
        transform_idx = np.array(sorted(set(np.concatenate([train_idx, val_idx]).tolist())), dtype=int) if fill_train_rows else val_idx
        train_latent, transform_latent = fit_latent_models(relative_frame, views, train_idx, transform_idx)
        local_position = {int(row): pos for pos, row in enumerate(transform_idx)}

        for target_view in views:
            k = PROTOTYPES_PER_VIEW
            x_train_target = train_latent[target_view]
            km = KMeans(n_clusters=k, n_init=32, random_state=RANDOM_SEED + fold)
            y_train = km.fit_predict(x_train_target)
            train_dist = km.transform(x_train_target)
            train_resp = soft_assign(train_dist)

            x_transform_target = transform_latent[target_view]
            transform_dist = km.transform(x_transform_target)
            y_transform = km.predict(x_transform_target)
            transform_resp = soft_assign(transform_dist)

            prior = np.bincount(y_train, minlength=k).astype(np.float64)
            prior = (prior + 1.0) / (prior.sum() + k)

            x_context_train = concat_context(train_latent, target_view)
            x_context_transform = concat_context(transform_latent, target_view)
            if len(np.unique(y_train)) < 2:
                pred = np.tile(prior, (len(transform_idx), 1))
            else:
                model = make_pipeline(
                    SimpleImputer(strategy="median"),
                    StandardScaler(),
                    LogisticRegression(C=LOGISTIC_C, max_iter=5000, solver="lbfgs"),
                )
                model.fit(x_context_train, y_train)
                raw = model.predict_proba(x_context_transform)
                pred = np.zeros((len(transform_idx), k), dtype=np.float64)
                for class_pos, class_label in enumerate(model.classes_):
                    pred[:, int(class_label)] = raw[:, class_pos]
                missing = pred.sum(axis=1) <= 1e-12
                if np.any(missing):
                    pred[missing] = prior
            pred = np.clip(pred, 1e-6, 1.0)
            pred = pred / pred.sum(axis=1, keepdims=True)

            val_pos = np.array([local_position[int(row)] for row in val_idx], dtype=int)
            y_val = y_transform[val_pos]
            pred_val = pred[val_pos]
            prior_val = np.tile(prior, (len(val_idx), 1))
            ce = float(log_loss(y_val, pred_val, labels=list(range(k))))
            prior_ce = float(log_loss(y_val, prior_val, labels=list(range(k))))
            fold_rows.append(
                {
                    "split": split_name,
                    "fold": fold,
                    "target_view": target_view,
                    "rows": int(len(val_idx)),
                    "cross_entropy": ce,
                    "prior_cross_entropy": prior_ce,
                    "cross_entropy_lift_vs_prior": prior_ce - ce,
                    "accuracy": float(accuracy_score(y_val, np.argmax(pred_val, axis=1))),
                    "prior_accuracy": float(accuracy_score(y_val, np.argmax(prior_val, axis=1))),
                    "prototype_count": int(k),
                    "transport_rows": int(len(transform_idx)),
                    "train_rows": int(len(train_idx)),
                }
            )

            rows_to_write = transform_idx if fill_train_rows else val_idx
            write_pos = np.arange(len(transform_idx)) if fill_train_rows else val_pos
            y_write = y_transform[write_pos]
            pred_write = pred[write_pos]
            true_write = transform_resp[write_pos]
            prior_write = np.tile(prior, (len(rows_to_write), 1))
            energy = -np.log(np.clip(pred_write[np.arange(len(rows_to_write)), y_write], 1e-12, 1.0))
            prior_energy = -np.log(np.clip(prior_write[np.arange(len(rows_to_write)), y_write], 1e-12, 1.0))

            for proto in range(k):
                state.loc[rows_to_write, f"cspg_pred_{target_view}_p{proto}"] = pred_write[:, proto]
                state.loc[rows_to_write, f"cspg_true_{target_view}_p{proto}"] = true_write[:, proto]
            state.loc[rows_to_write, f"cspg_pred_{target_view}_confidence"] = pred_write.max(axis=1)
            state.loc[rows_to_write, f"cspg_pred_{target_view}_entropy"] = entropy_rows(pred_write)
            state.loc[rows_to_write, f"cspg_true_{target_view}_confidence"] = true_write.max(axis=1)
            state.loc[rows_to_write, f"cspg_true_{target_view}_entropy"] = entropy_rows(true_write)
            state.loc[rows_to_write, f"cspg_energy_{target_view}"] = energy
            state.loc[rows_to_write, f"cspg_energy_lift_{target_view}"] = prior_energy - energy
            state.loc[rows_to_write, f"cspg_match_{target_view}"] = (np.argmax(pred_write, axis=1) == y_write).astype(float)

    energy_cols = [c for c in state.columns if c.startswith("cspg_energy_") and "_lift_" not in c]
    lift_cols = [c for c in state.columns if c.startswith("cspg_energy_lift_")]
    confidence_cols = [c for c in state.columns if c.startswith("cspg_pred_") and c.endswith("_confidence")]
    entropy_cols = [c for c in state.columns if c.startswith("cspg_pred_") and c.endswith("_entropy")]
    match_cols = [c for c in state.columns if c.startswith("cspg_match_")]
    state["cspg_energy_mean"] = state[energy_cols].mean(axis=1)
    state["cspg_energy_max"] = state[energy_cols].max(axis=1)
    state["cspg_energy_rank_mean"] = rank01(state["cspg_energy_mean"].to_numpy(dtype=np.float64))
    state["cspg_energy_lift_mean"] = state[lift_cols].mean(axis=1)
    state["cspg_confidence_mean"] = state[confidence_cols].mean(axis=1)
    state["cspg_entropy_mean"] = state[entropy_cols].mean(axis=1)
    state["cspg_match_mean"] = state[match_cols].mean(axis=1)

    fold_metrics = pd.DataFrame(fold_rows)
    for target_view, part in fold_metrics.groupby("target_view", observed=True):
        metric_rows.append(
            {
                "split": split_name,
                "target_view": target_view,
                "folds": int(part["fold"].nunique()),
                "rows": int(part["rows"].sum()),
                "cross_entropy": float(np.average(part["cross_entropy"], weights=part["rows"])),
                "prior_cross_entropy": float(np.average(part["prior_cross_entropy"], weights=part["rows"])),
                "cross_entropy_lift_vs_prior": float(np.average(part["cross_entropy_lift_vs_prior"], weights=part["rows"])),
                "accuracy": float(np.average(part["accuracy"], weights=part["rows"])),
                "prior_accuracy": float(np.average(part["prior_accuracy"], weights=part["rows"])),
                "uses_public_score": False,
                "uses_label_as_pretext": False,
            }
        )
    return state, pd.DataFrame(metric_rows), fold_metrics


def feature_columns(state: pd.DataFrame) -> dict[str, list[str]]:
    pred_prob = [c for c in state.columns if c.startswith("cspg_pred_") and "_p" in c]
    true_prob = [c for c in state.columns if c.startswith("cspg_true_") and "_p" in c]
    stats = [
        c
        for c in state.columns
        if c.startswith("cspg_")
        and (
            c.endswith("_confidence")
            or c.endswith("_entropy")
            or c.startswith("cspg_energy_")
            or c.startswith("cspg_match_")
            or c in {
                "cspg_energy_mean",
                "cspg_energy_max",
                "cspg_energy_rank_mean",
                "cspg_energy_lift_mean",
                "cspg_confidence_mean",
                "cspg_entropy_mean",
                "cspg_match_mean",
            }
        )
    ]
    invariant = [c for c in stats if not c.startswith("cspg_match_")]
    return {
        "transported_prototype_stats": sorted(set(invariant)),
        "transported_prototype_probabilities": sorted(set(pred_prob)),
        "transported_prototype_stats_probabilities": sorted(set(invariant + pred_prob)),
        "transported_observed_upper_bound": sorted(set(true_prob + [c for c in stats if c.startswith("cspg_true_")])),
    }


def evaluate_transport_split(
    split_name: str,
    train_frame: pd.DataFrame,
    state: pd.DataFrame,
    folds: list[tuple[np.ndarray, np.ndarray]],
    raw_cols: list[str],
    calendar_cols: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    feature_sets = {
        "prior_only": [],
        "calendar_rhythm": calendar_cols,
        "raw_lifelog_pca": raw_cols,
        **feature_columns(state),
    }
    features = pd.concat([train_frame[raw_cols].reset_index(drop=True), state.reset_index(drop=True)], axis=1)
    metrics, predictions = evaluate_split(train_frame, features, feature_sets, split_name, folds)
    probe_metrics = pd.concat(
        [
            metrics,
            calibrated_probe_metrics(predictions, shrink=0.05),
            calibrated_probe_metrics(predictions, shrink=0.10),
        ],
        ignore_index=True,
        sort=False,
    )
    neighbor = neighbor_consistency(train_frame, features, feature_sets)
    leakage = subject_leakage_probe(train_frame, features, {k: v for k, v in feature_sets.items() if v})
    return probe_metrics, predictions, neighbor, leakage


def summarize(
    pretext: pd.DataFrame,
    probes: pd.DataFrame,
    leakage: pd.DataFrame,
    neighbor: pd.DataFrame,
) -> dict[str, Any]:
    subject_all = probes[(probes["split"].eq("subject_heldout")) & (probes["target"].eq("all"))]
    row_all = probes[(probes["split"].eq("row_block_holdout")) & (probes["target"].eq("all"))]
    prior = subject_all[subject_all["feature_set"].eq("prior_only")]
    stats = subject_all[subject_all["feature_set"].eq("transported_prototype_stats_calibrated10")]
    stats_probs = subject_all[subject_all["feature_set"].eq("transported_prototype_stats_probabilities_calibrated10")]
    raw = subject_all[subject_all["feature_set"].eq("raw_lifelog_pca_calibrated10")]
    best_subject = subject_all.sort_values("logloss").head(1)
    best_row = row_all.sort_values("logloss").head(1)
    subject_pretext = pretext[pretext["split"].eq("subject_heldout")]
    leak_stats = leakage[leakage["feature_set"].eq("transported_prototype_stats")]
    raw_leak = leakage[leakage["feature_set"].eq("raw_lifelog_pca")]
    nn_all = neighbor[neighbor["target"].eq("all")].sort_values("lift", ascending=False)

    def single(frame: pd.DataFrame) -> dict[str, Any] | None:
        return None if frame.empty else frame.iloc[0].to_dict()

    prior_loss = float(prior["logloss"].iloc[0]) if not prior.empty else float("nan")
    stats_loss = float(stats["logloss"].iloc[0]) if not stats.empty else float("nan")
    stats_probs_loss = float(stats_probs["logloss"].iloc[0]) if not stats_probs.empty else float("nan")
    raw_loss = float(raw["logloss"].iloc[0]) if not raw.empty else float("nan")
    pretext_lift = float(subject_pretext["cross_entropy_lift_vs_prior"].mean()) if not subject_pretext.empty else float("nan")
    leakage_acc = float(leak_stats["subject_id_accuracy"].iloc[0]) if not leak_stats.empty else float("nan")

    verdict = "cross_subject_transport_negative_boundary"
    if np.isfinite(pretext_lift) and np.isfinite(stats_loss) and np.isfinite(prior_loss):
        if pretext_lift > 0 and stats_loss < prior_loss and leakage_acc < 0.35:
            verdict = "cross_subject_prototype_transport_core_positive"
        elif pretext_lift > 0:
            verdict = "cross_subject_transport_pretext_only_boundary"

    return {
        "package": "cross_subject_prototype_transport_core",
        "status": "cross_subject_prototype_transport_core_ready",
        "verdict": verdict,
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "uses_label_as_pretext_target": False,
        "prototype_count": PROTOTYPES_PER_VIEW,
        "subject_pretext_mean_cross_entropy_lift_vs_prior": pretext_lift,
        "subject_stats_logloss": stats_loss,
        "subject_stats_delta_vs_prior": stats_loss - prior_loss,
        "subject_stats_probabilities_logloss": stats_probs_loss,
        "subject_stats_probabilities_delta_vs_prior": stats_probs_loss - prior_loss,
        "subject_prior_logloss": prior_loss,
        "subject_raw_logloss": raw_loss,
        "subject_stats_delta_vs_raw": stats_loss - raw_loss,
        "subject_best_probe": single(best_subject),
        "row_block_best_probe": single(best_row),
        "transported_stats_subject_leakage": single(leak_stats),
        "raw_subject_leakage": single(raw_leak),
        "best_neighbor_consistency": single(nn_all.head(1)),
    }


def build_markdown(summary: dict[str, Any], pretext: pd.DataFrame, probes: pd.DataFrame, leakage: pd.DataFrame, neighbor: pd.DataFrame) -> str:
    subject_pretext = pretext[pretext["split"].eq("subject_heldout")].sort_values("cross_entropy_lift_vs_prior", ascending=False)
    subject_all = probes[(probes["split"].eq("subject_heldout")) & (probes["target"].eq("all"))].sort_values("logloss")
    chrono_all = probes[(probes["split"].eq("chronological_holdout")) & (probes["target"].eq("all"))].sort_values("logloss")
    row_all = probes[(probes["split"].eq("row_block_holdout")) & (probes["target"].eq("all"))].sort_values("logloss")
    subject_leakage = leakage[leakage["split"].eq("subject_heldout")].sort_values("subject_id_accuracy")
    nn_all = neighbor[(neighbor["split"].eq("subject_heldout")) & (neighbor["target"].eq("all"))].sort_values("lift", ascending=False)

    return f"""# Cross-Subject Prototype Transport Core

## 한 줄 요약

이 실험은 HS-JEPA prototype grammar를 더 엄격하게 검증한다.
prototype을 전체 데이터에서 한 번 만든 것이 아니라, fold마다 train subjects/blocks에서만 만든 뒤 held-out row/subject로 운반했다.

```text
train subjects define subject-relative episode grammar
  -> held-out subject is transported into that grammar
  -> visible views predict hidden transported prototype responsibilities
  -> frozen probes read transported state
```

## 판정

- verdict: `{summary["verdict"]}`
- public LB ledger 사용: `{summary["uses_public_score_ledger"]}`
- prior submission probability 사용: `{summary["uses_prior_submission_probabilities"]}`
- proprietary embedding API 사용: `{summary["uses_proprietary_embedding_api"]}`
- label을 pretext target으로 사용: `{summary["uses_label_as_pretext_target"]}`

## 왜 이것이 이전 Prototype Grammar보다 엄격한가

이전 실험은 subject-relative grammar 자체가 유효한지 먼저 확인했다.
이번 실험은 더 강한 질문을 던진다.

```text
다른 subject들이 만든 human-state grammar를
처음 보는 subject에게 운반해도 같은 구조가 들리는가?
```

즉 subject identity shortcut을 줄이는 것에서 한 단계 더 나아가,
grammar가 cross-subject transport 가능한지 본다.

## Subject-Heldout Transport Pretext

- mean cross-entropy lift vs prior: `{format_float(summary["subject_pretext_mean_cross_entropy_lift_vs_prior"], 6)}`

{markdown_table(subject_pretext, ["target_view", "cross_entropy", "prior_cross_entropy", "cross_entropy_lift_vs_prior", "accuracy", "prior_accuracy"], max_rows=12)}

## Subject-Heldout Frozen Probe

{markdown_table(subject_all, ["feature_set", "logloss", "auc"], max_rows=18)}

## Chronological Frozen Probe

{markdown_table(chrono_all, ["feature_set", "logloss", "auc"], max_rows=18)}

## Row-Block Frozen Probe

{markdown_table(row_all, ["feature_set", "logloss", "auc"], max_rows=18)}

## Subject Leakage Probe

{markdown_table(subject_leakage, ["feature_set", "subject_id_accuracy", "chance_accuracy", "leakage_lift_vs_chance"], max_rows=12)}

## Neighbor Consistency

{markdown_table(nn_all, ["feature_set", "neighbor_match_rate", "random_match_rate", "lift"], max_rows=12)}

## 현재 해석

strong positive이면 논문 주장은 다음으로 강화된다.

```text
HS-JEPA learns a subject-relative human-state grammar that can be transported
from observed subjects to unseen subjects before any label-specific decoder.
```

negative이면 경계도 명확하다.

```text
Prototype grammar is useful when fitted on the full cohort,
but its cross-subject transported form is not yet strong enough.
The next step should be route/listener-conditioned transport rather than a single global grammar.
```
"""


def run() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    PAPER_DOC.parent.mkdir(parents=True, exist_ok=True)

    frame_all, _labels = load_frames()
    catalog = catalog_features(frame_all)
    views = view_columns(catalog)
    train_mask = frame_all["split"].eq("train")
    frame = frame_all.loc[train_mask].reset_index(drop=True)
    relative = subject_relative_values(frame, catalog.raw_numeric)

    split_folds = {
        "subject_heldout": (subject_folds(frame), False),
        "chronological_holdout": (chronological_folds(frame), True),
        "row_block_holdout": (row_block_folds(frame), False),
    }

    state_parts: dict[str, pd.DataFrame] = {}
    pretext_parts: list[pd.DataFrame] = []
    fold_parts: list[pd.DataFrame] = []
    probe_parts: list[pd.DataFrame] = []
    neighbor_parts: list[pd.DataFrame] = []
    leakage_parts: list[pd.DataFrame] = []

    for split_name, (folds, fill_train_rows) in split_folds.items():
        state, metrics, fold_metrics = transport_state_for_folds(
            frame,
            relative,
            views,
            folds,
            split_name,
            fill_train_rows=fill_train_rows,
        )
        state_parts[split_name] = state
        pretext_parts.append(metrics)
        fold_parts.append(fold_metrics)
        probe, _predictions, neighbor, leakage = evaluate_transport_split(
            split_name,
            frame,
            state,
            folds,
            catalog.raw_numeric,
            catalog.calendar,
        )
        probe_parts.append(probe)
        neighbor.insert(0, "split", split_name)
        leakage.insert(0, "split", split_name)
        neighbor_parts.append(neighbor)
        leakage_parts.append(leakage)

    pretext = pd.concat(pretext_parts, ignore_index=True, sort=False)
    folds = pd.concat(fold_parts, ignore_index=True, sort=False)
    probes = pd.concat(probe_parts, ignore_index=True, sort=False)
    neighbor = pd.concat(neighbor_parts, ignore_index=True, sort=False)
    leakage = pd.concat(leakage_parts, ignore_index=True, sort=False)
    summary = summarize(pretext, probes, leakage[leakage["split"].eq("subject_heldout")], neighbor[neighbor["split"].eq("subject_heldout")])

    for split_name, state in state_parts.items():
        state.to_csv(OUT_DIR / f"cross_subject_transport_state_{split_name}.csv", index=False)
    pretext.to_csv(OUT_DIR / "cross_subject_transport_pretext_metrics.csv", index=False)
    folds.to_csv(OUT_DIR / "cross_subject_transport_pretext_fold_metrics.csv", index=False)
    probes.to_csv(OUT_DIR / "cross_subject_transport_probe_metrics.csv", index=False)
    neighbor.to_csv(OUT_DIR / "cross_subject_transport_neighbor_consistency.csv", index=False)
    leakage.to_csv(OUT_DIR / "cross_subject_transport_subject_leakage.csv", index=False)
    (OUT_DIR / "cross_subject_prototype_transport_summary.json").write_text(
        json.dumps(json_safe(summary), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    doc = build_markdown(summary, pretext, probes, leakage, neighbor)
    (OUT_DIR / "CROSS_SUBJECT_PROTOTYPE_TRANSPORT_CORE_KO.md").write_text(doc, encoding="utf-8")
    PAPER_DOC.write_text(doc, encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(json_safe(run()), ensure_ascii=False, indent=2))
