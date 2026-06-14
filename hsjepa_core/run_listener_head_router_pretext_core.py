#!/usr/bin/env python3
"""HS-JEPA label-free listener-head router experiment.

The previous multi-head experiment showed that naive current/future/cohort
concatenation does not beat the compact future-consistent head.  This experiment
tests the next architecture step:

    visible subject-relative context
      -> current / future / cohort listener-responsibility heads
      -> label-free listener router chooses a head mixture
      -> frozen downstream probe reads the routed representation

The router uses only head confidence/entropy/energy and semantic target priors.
Labels are used only after the routed representation is frozen.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hsjepa_core.run_human_state_world_model_core import subject_leakage_probe  # noqa: E402
from hsjepa_core.run_invariant_listener_responsibility_pretext_core import learned_features_from_teacher  # noqa: E402
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
    flatten_cols,
    json_safe,
    subject_relative_context,
)
from hsjepa_core.run_lifelog_core_state_evidence import (  # noqa: E402
    TARGETS,
    catalog_features,
    format_float,
    load_frames,
    markdown_table,
    view_columns,
)
from hsjepa_core.run_multi_head_listener_responsibility_pretext_core import (  # noqa: E402
    COMPACT_SUFFIXES,
    HEADS,
    HEAD_PREFIX,
    combine_target_cols,
    compact_cols,
    sanitize_features,
    suffix_after_target,
    target_teacher_heads,
)


OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "listener_head_router_pretext_core"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "LISTENER_HEAD_ROUTER_PRETEXT_CORE_KO.md"


HEAD_PRIORS: dict[str, dict[str, float]] = {
    "Q1": {"current": 0.25, "future": 0.55, "cohort": 0.20},
    "Q2": {"current": 0.20, "future": 0.60, "cohort": 0.20},
    "Q3": {"current": 0.25, "future": 0.50, "cohort": 0.25},
    "S1": {"current": 0.35, "future": 0.45, "cohort": 0.20},
    "S2": {"current": 0.30, "future": 0.45, "cohort": 0.25},
    "S3": {"current": 0.40, "future": 0.25, "cohort": 0.35},
    "S4": {"current": 0.40, "future": 0.25, "cohort": 0.35},
}
FUTURE_ANCHOR_PRIOR = {"current": 0.18, "future": 0.66, "cohort": 0.16}


def standardize(values: np.ndarray) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64)
    med = np.nanmedian(arr)
    scale = np.nanpercentile(arr, 75) - np.nanpercentile(arr, 25)
    if not np.isfinite(scale) or scale <= 1e-9:
        scale = np.nanstd(arr)
    if not np.isfinite(scale) or scale <= 1e-9:
        return np.zeros_like(arr, dtype=np.float64)
    return np.nan_to_num((arr - med) / scale, nan=0.0, posinf=0.0, neginf=0.0)


def softmax(values: np.ndarray) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64)
    arr = arr - np.nanmax(arr, axis=1, keepdims=True)
    exp = np.exp(np.clip(arr, -30.0, 30.0))
    return exp / np.maximum(exp.sum(axis=1, keepdims=True), 1e-12)


def target_suffix_map(
    head_cols: dict[str, dict[str, list[str]]],
    target: str,
) -> dict[str, dict[str, str]]:
    return {
        head: {
            suffix_after_target(col, HEAD_PREFIX[head], target): col
            for col in head_cols[head][target]
        }
        for head in HEADS
    }


def head_reliability_scores(
    head_parts: dict[str, pd.DataFrame],
    head_cols: dict[str, dict[str, list[str]]],
    target: str,
) -> np.ndarray:
    suffix_maps = target_suffix_map(head_cols, target)
    scores = []
    for head in HEADS:
        mapping = suffix_maps[head]

        def value(suffix: str) -> np.ndarray:
            col = mapping.get(suffix)
            if col is None:
                return np.zeros(len(head_parts[head]), dtype=np.float64)
            return np.nan_to_num(
                head_parts[head][col].to_numpy(dtype=np.float64),
                nan=0.0,
                posinf=0.0,
                neginf=0.0,
            )

        raw_score = (
            0.90 * standardize(value("confidence_weighted"))
            + 0.45 * standardize(value("energy_lift_weighted"))
            + 0.35 * standardize(value("responsibility_max"))
            - 0.65 * standardize(value("responsibility_entropy"))
            - 0.25 * standardize(value("entropy_weighted"))
        )
        scores.append(raw_score)
    return np.column_stack(scores)


def router_weights(
    scores: np.ndarray,
    target: str,
    mode: str,
) -> np.ndarray:
    n = scores.shape[0]
    if mode == "confidence_router":
        return softmax(0.70 * scores)
    if mode == "semantic_prior_router":
        prior = np.array([HEAD_PRIORS[target][head] for head in HEADS], dtype=np.float64)
        return np.tile(prior / prior.sum(), (n, 1))
    if mode == "semantic_confidence_router":
        prior = np.log(np.array([HEAD_PRIORS[target][head] for head in HEADS], dtype=np.float64))
        return softmax(prior.reshape(1, -1) + 0.55 * scores)
    if mode == "future_anchor_router":
        prior = np.log(np.array([FUTURE_ANCHOR_PRIOR[head] for head in HEADS], dtype=np.float64))
        return softmax(prior.reshape(1, -1) + 0.45 * scores)
    if mode == "anti_shortcut_router":
        prior = np.log(np.array([0.28, 0.54, 0.18], dtype=np.float64))
        penalty = np.array([0.00, 0.00, -0.20], dtype=np.float64)
        return softmax(prior.reshape(1, -1) + 0.50 * scores + penalty.reshape(1, -1))
    raise ValueError(f"unknown router mode: {mode}")


def build_routed_features(
    head_parts: dict[str, pd.DataFrame],
    head_cols: dict[str, dict[str, list[str]]],
    mode: str,
) -> tuple[pd.DataFrame, dict[str, list[str]], pd.DataFrame]:
    index = next(iter(head_parts.values())).index
    data: dict[str, np.ndarray] = {}
    target_cols: dict[str, list[str]] = {}
    weight_rows: list[dict[str, Any]] = []
    for target in TARGETS:
        suffix_maps = target_suffix_map(head_cols, target)
        scores = head_reliability_scores(head_parts, head_cols, target)
        weights = router_weights(scores, target, mode)
        cols_for_target: list[str] = []
        for pos, head in enumerate(HEADS):
            col = f"{mode}_{target}_router_w_{head}"
            data[col] = weights[:, pos]
            cols_for_target.append(col)
        entropy_col = f"{mode}_{target}_router_entropy"
        margin_col = f"{mode}_{target}_router_margin"
        sorted_w = np.sort(weights, axis=1)
        data[entropy_col] = -np.sum(weights * np.log(np.clip(weights, 1e-12, 1.0)), axis=1) / math.log(len(HEADS))
        data[margin_col] = sorted_w[:, -1] - sorted_w[:, -2]
        cols_for_target.extend([entropy_col, margin_col])

        shared = [
            suffix
            for suffix in sorted(set.intersection(*(set(suffix_maps[head]) for head in HEADS)))
            if suffix in COMPACT_SUFFIXES
        ]
        for suffix in shared:
            values = np.column_stack(
                [
                    np.nan_to_num(
                        head_parts[head][suffix_maps[head][suffix]].to_numpy(dtype=np.float64),
                        nan=0.0,
                        posinf=0.0,
                        neginf=0.0,
                    )
                    for head in HEADS
                ]
            )
            col = f"{mode}_{target}_{suffix}_routed"
            data[col] = np.sum(weights * values, axis=1)
            cols_for_target.append(col)
        target_cols[target] = cols_for_target
        mean_weights = weights.mean(axis=0)
        weight_rows.append(
            {
                "router": mode,
                "target": target,
                "mean_w_current": float(mean_weights[0]),
                "mean_w_future": float(mean_weights[1]),
                "mean_w_cohort": float(mean_weights[2]),
                "mean_entropy": float(np.mean(data[entropy_col])),
                "mean_margin": float(np.mean(data[margin_col])),
            }
        )
    return pd.DataFrame(data, index=index), target_cols, pd.DataFrame(weight_rows)


def evaluate_split_package(
    split_name: str,
    train_frame: pd.DataFrame,
    relative_context: pd.DataFrame,
    raw_cols: list[str],
    views: dict[str, list[str]],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    state = load_transport_state(split_name)
    folds = split_folds(split_name, train_frame)
    direct_semantic, direct_semantic_cols = build_label_free_listener_features(
        state,
        views,
        SEMANTIC_TARGET_PROFILES,
        "direct_semantic",
    )
    teachers = target_teacher_heads(train_frame, relative_context, state, views)

    head_parts: dict[str, pd.DataFrame] = {}
    head_cols: dict[str, dict[str, list[str]]] = {}
    pretext_parts: list[pd.DataFrame] = []
    for head in HEADS:
        prefix = HEAD_PREFIX[head]
        part, cols, pretext = learned_features_from_teacher(
            train_frame,
            relative_context,
            state,
            views,
            teachers[head],
            folds,
            split_name,
            prefix,
            0.35,
            f"{head}_transported_prototype_reliability",
        )
        head_parts[head] = part.reset_index(drop=True)
        head_cols[head] = cols
        pretext_parts.append(pretext)

    compact_head_cols = {
        head: compact_cols(head_cols[head], HEAD_PREFIX[head])
        for head in HEADS
    }
    router_modes = [
        "confidence_router",
        "semantic_prior_router",
        "semantic_confidence_router",
        "future_anchor_router",
        "anti_shortcut_router",
    ]
    router_parts: list[pd.DataFrame] = []
    router_maps: dict[str, dict[str, list[str]]] = {}
    router_weight_parts: list[pd.DataFrame] = []
    for mode in router_modes:
        part, cols, weight_summary = build_routed_features(head_parts, head_cols, mode)
        router_parts.append(part.reset_index(drop=True))
        router_maps[f"{mode}_listener_responsibility"] = cols
        weight_summary.insert(0, "split", split_name)
        router_weight_parts.append(weight_summary)

    features = pd.concat(
        [
            train_frame[raw_cols].reset_index(drop=True),
            state.reset_index(drop=True),
            direct_semantic.reset_index(drop=True),
            *(head_parts[head].reset_index(drop=True) for head in HEADS),
            *router_parts,
        ],
        axis=1,
    )
    features = sanitize_features(features)
    global_cols = global_transport_cols(views)
    head_maps = {
        f"{HEAD_PREFIX[head]}_listener_responsibility": compact_head_cols[head]
        for head in HEADS
    }
    feature_maps = {
        "prior_only": {target: [] for target in TARGETS},
        "raw_lifelog_pca": {target: raw_cols for target in TARGETS},
        "global_transported_prototype": {target: global_cols for target in TARGETS},
        "direct_semantic_listener_responsibility": direct_semantic_cols,
        **head_maps,
        "multihead_current_future_cohort_listener_responsibility": combine_target_cols(
            [compact_head_cols["current"], compact_head_cols["future"], compact_head_cols["cohort"]]
        ),
        **router_maps,
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
        "direct_semantic_listener_responsibility": flatten_cols(direct_semantic_cols),
        **{name: flatten_cols(cols) for name, cols in head_maps.items()},
        "multihead_current_future_cohort_listener_responsibility": flatten_cols(
            combine_target_cols([compact_head_cols["current"], compact_head_cols["future"], compact_head_cols["cohort"]])
        ),
        **{name: flatten_cols(cols) for name, cols in router_maps.items()},
    }
    leakage = subject_leakage_probe(train_frame, features, leakage_sets)
    leakage.insert(0, "split", split_name)
    pretext = aggregate_pretext(pd.concat(pretext_parts, ignore_index=True))
    return metrics, leakage, pretext, pd.concat(router_weight_parts, ignore_index=True)


def summarize(
    metrics: pd.DataFrame,
    leakage: pd.DataFrame,
    pretext: pd.DataFrame,
    router_weights_frame: pd.DataFrame,
) -> dict[str, Any]:
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

    single_sets = [
        f"{HEAD_PREFIX[head]}_listener_responsibility_calibrated10"
        for head in HEADS
    ]
    router_sets = sorted(
        subject_all[
            subject_all["feature_set"].str.endswith("_router_listener_responsibility_calibrated10")
        ]["feature_set"].tolist()
    )
    single_losses = {name: loss(subject_all, name) for name in single_sets}
    router_losses = {name: loss(subject_all, name) for name in router_sets}
    best_single_name = min(
        [name for name, value in single_losses.items() if value is not None],
        key=lambda name: single_losses[name],
    )
    best_router_name = min(
        [name for name, value in router_losses.items() if value is not None],
        key=lambda name: router_losses[name],
    )
    best_single = single_losses[best_single_name]
    best_router = router_losses[best_router_name]
    prior = loss(subject_all, "prior_only_calibrated10")
    raw = loss(subject_all, "raw_lifelog_pca_calibrated10")
    global_transport = loss(subject_all, "global_transported_prototype_calibrated10")
    direct_semantic = loss(subject_all, "direct_semantic_listener_responsibility_calibrated10")
    naive_multi = loss(subject_all, "multihead_current_future_cohort_listener_responsibility_calibrated10")
    best_row = loss(row_all, best_router_name)
    best_chrono = loss(chrono_all, best_router_name)
    global_row = loss(row_all, "global_transported_prototype_calibrated10")
    global_chrono = loss(chrono_all, "global_transported_prototype_calibrated10")

    verdict = "listener_head_router_negative"
    if best_router is not None and prior is not None and best_router < prior:
        verdict = "listener_head_router_prior_positive"
        if best_single is not None and best_router < best_single:
            verdict = "listener_head_router_beats_single_positive"
        if global_transport is not None and best_router < global_transport:
            verdict = "listener_head_router_global_positive"

    weight_rows = {
        f"{row['router']}::{row['target']}": row.to_dict()
        for _, row in router_weights_frame[router_weights_frame["split"].eq("subject_heldout")].iterrows()
    }
    pretext_rows = {row["feature_set"]: row.to_dict() for _, row in subject_pretext.iterrows()}
    return {
        "package": "listener_head_router_pretext_core",
        "status": "listener_head_router_pretext_core_ready",
        "verdict": verdict,
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "uses_label_as_pretext_target": False,
        "router": "label_free_head_confidence_entropy_energy_and_target_semantic_prior",
        "context_encoder": "subject_relative_visible_lifelog_context",
        "subject_prior_logloss": prior,
        "subject_raw_logloss": raw,
        "subject_global_transport_logloss": global_transport,
        "subject_direct_semantic_logloss": direct_semantic,
        "subject_naive_multi_head_logloss": naive_multi,
        "subject_best_single_head_feature_set": best_single_name,
        "subject_best_single_head_logloss": best_single,
        "subject_best_router_feature_set": best_router_name,
        "subject_best_router_logloss": best_router,
        "subject_best_router_delta_vs_single": None if best_router is None or best_single is None else best_router - best_single,
        "subject_best_router_delta_vs_prior": None if best_router is None or prior is None else best_router - prior,
        "subject_best_router_delta_vs_raw": None if best_router is None or raw is None else best_router - raw,
        "subject_best_router_delta_vs_direct_semantic": None if best_router is None or direct_semantic is None else best_router - direct_semantic,
        "subject_best_router_delta_vs_naive_multi": None if best_router is None or naive_multi is None else best_router - naive_multi,
        "subject_best_router_delta_vs_global": None if best_router is None or global_transport is None else best_router - global_transport,
        "row_block_best_router_delta_vs_global": None if best_row is None or global_row is None else best_row - global_row,
        "chronological_best_router_delta_vs_global": None if best_chrono is None or global_chrono is None else best_chrono - global_chrono,
        "subject_pretext_all": pretext_rows,
        "subject_router_weights": weight_rows,
        "subject_best_router_leakage": leak(best_router_name.replace("_calibrated10", "")),
        "subject_best_single_leakage": leak(best_single_name.replace("_calibrated10", "")),
        "global_transport_subject_leakage": leak("global_transported_prototype"),
        "raw_subject_leakage": leak("raw_lifelog_pca"),
    }


def build_markdown(
    summary: dict[str, Any],
    metrics: pd.DataFrame,
    leakage: pd.DataFrame,
    pretext: pd.DataFrame,
    router_weights_frame: pd.DataFrame,
) -> str:
    subject_all = metrics[(metrics["split"].eq("subject_heldout")) & (metrics["target"].eq("all"))].sort_values("logloss")
    row_all = metrics[(metrics["split"].eq("row_block_holdout")) & (metrics["target"].eq("all"))].sort_values("logloss")
    chrono_all = metrics[(metrics["split"].eq("chronological_holdout")) & (metrics["target"].eq("all"))].sort_values("logloss")
    pretext_all = pretext[pretext["target"].eq("all")].sort_values(["split", "feature_set"])
    subject_leak = leakage[leakage["split"].eq("subject_heldout")].sort_values("subject_id_accuracy")
    subject_weights = router_weights_frame[router_weights_frame["split"].eq("subject_heldout")].sort_values(["router", "target"])
    return f"""# Listener Head Router Pretext Core

## 한 줄 요약

이 실험은 current/future/cohort head를 concat하지 않는다.
label-free router가 head confidence, entropy, energy, target semantic prior를 보고
각 target-row에서 어느 head를 읽을지 soft routing한다.

```text
subject-relative visible human-life context
  -> current / future / cohort listener-responsibility heads
  -> label-free listener-head router
  -> routed human-state interface
  -> frozen downstream probe
```

## 판정

- verdict: `{summary["verdict"]}`
- public LB ledger 사용: `{summary["uses_public_score_ledger"]}`
- prior submission probability 사용: `{summary["uses_prior_submission_probabilities"]}`
- proprietary embedding API 사용: `{summary["uses_proprietary_embedding_api"]}`
- label을 pretext target으로 사용: `{summary["uses_label_as_pretext_target"]}`
- router: `{summary["router"]}`
- context encoder: `{summary["context_encoder"]}`

## 핵심 수치

- best single head: `{summary["subject_best_single_head_feature_set"]}`
- best single-head logloss: `{format_float(summary["subject_best_single_head_logloss"], 6)}`
- best router: `{summary["subject_best_router_feature_set"]}`
- best router logloss: `{format_float(summary["subject_best_router_logloss"], 6)}`
- naive multi-head logloss: `{format_float(summary["subject_naive_multi_head_logloss"], 6)}`
- global transport logloss: `{format_float(summary["subject_global_transport_logloss"], 6)}`
- direct semantic logloss: `{format_float(summary["subject_direct_semantic_logloss"], 6)}`
- prior logloss: `{format_float(summary["subject_prior_logloss"], 6)}`
- router delta vs single: `{format_float(summary["subject_best_router_delta_vs_single"], 6)}`
- router delta vs prior: `{format_float(summary["subject_best_router_delta_vs_prior"], 6)}`
- router delta vs raw lifelog PCA: `{format_float(summary["subject_best_router_delta_vs_raw"], 6)}`
- router delta vs direct semantic: `{format_float(summary["subject_best_router_delta_vs_direct_semantic"], 6)}`
- router delta vs naive multi-head: `{format_float(summary["subject_best_router_delta_vs_naive_multi"], 6)}`
- router delta vs global transport: `{format_float(summary["subject_best_router_delta_vs_global"], 6)}`
- row-block router delta vs global: `{format_float(summary["row_block_best_router_delta_vs_global"], 6)}`
- chronological router delta vs global: `{format_float(summary["chronological_best_router_delta_vs_global"], 6)}`

## Subject-Heldout Frozen Probe

{markdown_table(subject_all, ["feature_set", "logloss", "auc"], max_rows=24)}

## Row-Block Frozen Probe

{markdown_table(row_all, ["feature_set", "logloss", "auc"], max_rows=24)}

## Chronological Frozen Probe

{markdown_table(chrono_all, ["feature_set", "logloss", "auc"], max_rows=24)}

## Label-Free Pretext Quality

{markdown_table(pretext_all, ["split", "feature_set", "pretext_cross_entropy", "prior_cross_entropy", "ce_lift_vs_prior", "top1_match_rate"], max_rows=24)}

## Router Weight Summary

{markdown_table(subject_weights, ["router", "target", "mean_w_current", "mean_w_future", "mean_w_cohort", "mean_entropy", "mean_margin"], max_rows=40)}

## Subject Leakage Diagnostic

{markdown_table(subject_leak, ["feature_set", "subject_id_accuracy", "chance_accuracy", "leakage_lift_vs_chance"], max_rows=16)}

## 해석

positive이면:

```text
HS-JEPA should expose current/future/cohort heads and use a label-free listener router
instead of naive head concatenation.
```

negative이면:

```text
The missing component is not a hand-built head router.  The future head itself is useful,
but router learning must be a stronger JEPA objective rather than confidence heuristics.
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
    weight_parts: list[pd.DataFrame] = []
    for split_name in ["subject_heldout", "chronological_holdout", "row_block_holdout"]:
        metrics, leakage, pretext, weights = evaluate_split_package(
            split_name,
            train_frame,
            relative_context,
            catalog.raw_numeric,
            views,
        )
        metric_parts.append(metrics)
        leakage_parts.append(leakage)
        pretext_parts.append(pretext)
        weight_parts.append(weights)

    metrics = pd.concat(metric_parts, ignore_index=True, sort=False)
    leakage = pd.concat(leakage_parts, ignore_index=True, sort=False)
    pretext = pd.concat(pretext_parts, ignore_index=True, sort=False)
    router_weights_frame = pd.concat(weight_parts, ignore_index=True, sort=False)
    summary = summarize(metrics, leakage, pretext, router_weights_frame)

    metrics.to_csv(OUT_DIR / "listener_head_router_probe_metrics.csv", index=False)
    leakage.to_csv(OUT_DIR / "listener_head_router_subject_leakage.csv", index=False)
    pretext.to_csv(OUT_DIR / "listener_head_router_pretext_metrics.csv", index=False)
    router_weights_frame.to_csv(OUT_DIR / "listener_head_router_weights.csv", index=False)
    (OUT_DIR / "listener_head_router_pretext_summary.json").write_text(
        json.dumps(json_safe(summary), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    doc = build_markdown(summary, metrics, leakage, pretext, router_weights_frame)
    (OUT_DIR / "LISTENER_HEAD_ROUTER_PRETEXT_CORE_KO.md").write_text(doc, encoding="utf-8")
    PAPER_DOC.write_text(doc, encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(json_safe(run()), ensure_ascii=False, indent=2))
