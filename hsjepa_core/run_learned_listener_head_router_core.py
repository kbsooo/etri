#!/usr/bin/env python3
"""HS-JEPA learned listener-head router core experiment.

The fixed listener-head router showed a useful boundary: target semantic priors
can route current/future/cohort listener heads slightly better than the best
single head, while confidence-only routing is weak.  This experiment turns that
boundary into a JEPA-style pretext task:

    visible subject-relative human-life context
      + predicted current/future/cohort listener heads
      -> hidden listener-head suitability field
      -> learned head router
      -> routed human-state interface
      -> frozen downstream probe

The head-suitability teacher is label-free.  It is built from transported
prototype confidence, entropy, energy, and current/future/cohort consistency.
Labels are used only after the router representation is frozen.
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
    finite_frame,
    flatten_cols,
    json_safe,
    make_responsibility_predictor,
    normalize_rows,
    softmax_rows,
    subject_relative_context,
    view_order,
)
from hsjepa_core.run_lifelog_core_state_evidence import (  # noqa: E402
    TARGETS,
    catalog_features,
    format_float,
    load_frames,
    markdown_table,
    view_columns,
)
from hsjepa_core.run_listener_head_router_pretext_core import (  # noqa: E402
    HEAD_PRIORS,
    build_routed_features,
    head_reliability_scores,
    softmax,
    standardize,
    target_suffix_map,
)
from hsjepa_core.run_multi_head_listener_responsibility_pretext_core import (  # noqa: E402
    COMPACT_SUFFIXES,
    HEADS,
    HEAD_PREFIX,
    combine_target_cols,
    compact_cols,
    sanitize_features,
    target_teacher_heads,
)


OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "learned_listener_head_router_core"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "LEARNED_LISTENER_HEAD_ROUTER_CORE_KO.md"


def weighted_state_stat(
    state: pd.DataFrame,
    views: dict[str, list[str]],
    weights: np.ndarray,
    stat: str,
) -> np.ndarray:
    names = view_order(views)
    if stat in {"confidence", "entropy"}:
        cols = [f"cspg_pred_{view}_{stat}" for view in names]
    else:
        cols = [f"cspg_{stat}_{view}" for view in names]
    values = np.column_stack([state[col].to_numpy(dtype=np.float64) for col in cols])
    return np.sum(weights * values, axis=1)


def responsibility_entropy(weights: np.ndarray) -> np.ndarray:
    return -np.sum(weights * np.log(np.clip(weights, 1e-12, 1.0)), axis=1) / math.log(weights.shape[1])


def distribution_agreement(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    numer = np.sum(left * right, axis=1)
    denom = np.linalg.norm(left, axis=1) * np.linalg.norm(right, axis=1)
    return np.divide(numer, np.maximum(denom, 1e-12))


def hidden_head_suitability_teacher(
    state: pd.DataFrame,
    views: dict[str, list[str]],
    teachers: dict[str, dict[str, np.ndarray]],
    target: str,
    mode: str,
) -> np.ndarray:
    """Build a label-free hidden suitability distribution over heads."""

    raw_scores: list[np.ndarray] = []
    current = teachers["current"][target]
    future = teachers["future"][target]
    cohort = teachers["cohort"][target]
    agreements = {
        "current": 0.50 * distribution_agreement(current, future)
        + 0.50 * distribution_agreement(current, cohort),
        "future": distribution_agreement(current, future),
        "cohort": distribution_agreement(current, cohort),
    }
    semantic_prior = np.log(np.array([HEAD_PRIORS[target][head] for head in HEADS], dtype=np.float64))

    for head in HEADS:
        weights = teachers[head][target]
        score = (
            0.80 * standardize(weighted_state_stat(state, views, weights, "confidence"))
            + 0.35 * standardize(weighted_state_stat(state, views, weights, "energy_lift"))
            + 0.25 * standardize(np.max(weights, axis=1))
            + 0.30 * standardize(agreements[head])
            - 0.55 * standardize(responsibility_entropy(weights))
            - 0.25 * standardize(weighted_state_stat(state, views, weights, "entropy"))
        )
        raw_scores.append(score)

    scores = np.column_stack(raw_scores)
    if mode == "state_suitability":
        return softmax(0.85 * scores)
    if mode == "state_suitability_semantic":
        return softmax(0.70 * scores + 0.85 * semantic_prior.reshape(1, -1))
    if mode == "semantic_distilled":
        return softmax(0.35 * scores + 1.20 * semantic_prior.reshape(1, -1))
    raise ValueError(f"unknown teacher mode: {mode}")


def router_design(
    context: pd.DataFrame,
    head_parts: dict[str, pd.DataFrame],
    head_cols: dict[str, dict[str, list[str]]],
    target: str,
    mode: str,
) -> pd.DataFrame:
    pieces: list[pd.DataFrame] = []
    if mode in {"context", "context_headsignal", "context_headsignal_semantic"}:
        pieces.append(context.reset_index(drop=True))
    if mode in {"headsignal", "context_headsignal", "context_headsignal_semantic"}:
        scores = head_reliability_scores(head_parts, head_cols, target)
        part = pd.DataFrame(
            {
                f"{target}_headscore_{head}": scores[:, idx]
                for idx, head in enumerate(HEADS)
            }
        )
        weights = softmax(0.70 * scores)
        part[f"{target}_headscore_entropy"] = responsibility_entropy(weights)
        part[f"{target}_headscore_margin"] = np.sort(weights, axis=1)[:, -1] - np.sort(weights, axis=1)[:, -2]
        suffix_maps = target_suffix_map(head_cols, target)
        for head in HEADS:
            for suffix in sorted(COMPACT_SUFFIXES):
                col = suffix_maps[head].get(suffix)
                if col is not None:
                    part[f"{target}_{head}_{suffix}"] = head_parts[head][col].to_numpy(dtype=np.float64)
        pieces.append(part.reset_index(drop=True))
    if not pieces:
        raise ValueError(f"unknown router design mode: {mode}")
    return sanitize_features(pd.concat(pieces, axis=1))


def learned_router_weights(
    train_frame: pd.DataFrame,
    context: pd.DataFrame,
    head_parts: dict[str, pd.DataFrame],
    head_cols: dict[str, dict[str, list[str]]],
    teacher_weights: dict[str, np.ndarray],
    folds: list[tuple[np.ndarray, np.ndarray]],
    split_name: str,
    feature_prefix: str,
    design_mode: str,
    prediction_blend: float,
    semantic_blend: float,
    teacher_source: str,
) -> tuple[dict[str, np.ndarray], pd.DataFrame, pd.DataFrame]:
    weights_by_target: dict[str, np.ndarray] = {}
    pretext_rows: list[dict[str, Any]] = []
    weight_rows: list[dict[str, Any]] = []

    for target in TARGETS:
        teacher = teacher_weights[target]
        x = router_design(context, head_parts, head_cols, target, design_mode)
        predicted = np.zeros_like(teacher, dtype=np.float64)
        semantic = np.tile(
            normalize_rows(np.array([[HEAD_PRIORS[target][head] for head in HEADS]], dtype=np.float64)),
            (len(teacher), 1),
        )
        evaluated = np.zeros(len(teacher), dtype=bool)
        for fold, (tr_idx, va_idx) in enumerate(folds):
            evaluated[va_idx] = True
            train_teacher = teacher[tr_idx]
            prior = normalize_rows(np.tile(train_teacher.mean(axis=0), (len(va_idx), 1)))
            if len(tr_idx) < 8:
                raw_pred = prior
            else:
                model = make_responsibility_predictor(x.shape[1], len(tr_idx))
                model.fit(
                    finite_frame(x.iloc[tr_idx], list(x.columns)),
                    np.log(np.clip(train_teacher, 1e-5, 1.0)),
                )
                raw_pred = softmax_rows(model.predict(finite_frame(x.iloc[va_idx], list(x.columns))))
            pred = normalize_rows((1.0 - prediction_blend) * prior + prediction_blend * raw_pred)
            if semantic_blend > 0.0:
                pred = normalize_rows((1.0 - semantic_blend) * pred + semantic_blend * semantic[va_idx])
            predicted[va_idx] = pred

            y = teacher[va_idx]
            ce_pred = -float(np.mean(np.sum(y * np.log(np.clip(pred, 1e-12, 1.0)), axis=1)))
            ce_prior = -float(np.mean(np.sum(y * np.log(np.clip(prior, 1e-12, 1.0)), axis=1)))
            ce_semantic = -float(np.mean(np.sum(y * np.log(np.clip(semantic[va_idx], 1e-12, 1.0)), axis=1)))
            pretext_rows.append(
                {
                    "split": split_name,
                    "feature_set": feature_prefix,
                    "target": target,
                    "fold": fold,
                    "pretext_cross_entropy": ce_pred,
                    "prior_cross_entropy": ce_prior,
                    "semantic_cross_entropy": ce_semantic,
                    "uniform_cross_entropy": math.log(len(HEADS)),
                    "ce_lift_vs_prior": ce_prior - ce_pred,
                    "ce_lift_vs_semantic": ce_semantic - ce_pred,
                    "ce_lift_vs_uniform": math.log(len(HEADS)) - ce_pred,
                    "top1_match_rate": float(np.mean(np.argmax(y, axis=1) == np.argmax(pred, axis=1))),
                    "train_rows": int(len(tr_idx)),
                    "validation_rows": int(len(va_idx)),
                    "uses_public_score": False,
                    "uses_train_labels_for_pretext": False,
                    "teacher_source": teacher_source,
                    "design_mode": design_mode,
                    "prediction_blend": prediction_blend,
                    "responsibility_blend": prediction_blend,
                    "semantic_blend": semantic_blend,
                }
            )
        if not evaluated.all():
            missing = ~evaluated
            fallback = normalize_rows(np.tile(teacher[evaluated].mean(axis=0), (int(missing.sum()), 1)))
            predicted[missing] = fallback
        weights_by_target[target] = predicted
        mean_weights = predicted.mean(axis=0)
        weight_rows.append(
            {
                "split": split_name,
                "router": feature_prefix,
                "target": target,
                "mean_w_current": float(mean_weights[0]),
                "mean_w_future": float(mean_weights[1]),
                "mean_w_cohort": float(mean_weights[2]),
                "mean_entropy": float(np.mean(responsibility_entropy(predicted))),
                "mean_margin": float(np.mean(np.sort(predicted, axis=1)[:, -1] - np.sort(predicted, axis=1)[:, -2])),
            }
        )
    return weights_by_target, pd.DataFrame(pretext_rows), pd.DataFrame(weight_rows)


def build_learned_routed_features(
    head_parts: dict[str, pd.DataFrame],
    head_cols: dict[str, dict[str, list[str]]],
    weights_by_target: dict[str, np.ndarray],
    prefix: str,
) -> tuple[pd.DataFrame, dict[str, list[str]]]:
    index = next(iter(head_parts.values())).index
    data: dict[str, np.ndarray] = {}
    target_cols: dict[str, list[str]] = {}
    for target in TARGETS:
        suffix_maps = target_suffix_map(head_cols, target)
        weights = weights_by_target[target]
        cols_for_target: list[str] = []
        for pos, head in enumerate(HEADS):
            col = f"{prefix}_{target}_router_w_{head}"
            data[col] = weights[:, pos]
            cols_for_target.append(col)
        entropy_col = f"{prefix}_{target}_router_entropy"
        margin_col = f"{prefix}_{target}_router_margin"
        sorted_w = np.sort(weights, axis=1)
        data[entropy_col] = responsibility_entropy(weights)
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
            col = f"{prefix}_{target}_{suffix}_routed"
            data[col] = np.sum(weights * values, axis=1)
            cols_for_target.append(col)
        target_cols[target] = cols_for_target
    return pd.DataFrame(data, index=index), target_cols


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
    head_pretext_parts: list[pd.DataFrame] = []
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
        head_pretext_parts.append(pretext)

    compact_head_cols = {
        head: compact_cols(head_cols[head], HEAD_PREFIX[head])
        for head in HEADS
    }
    fixed_semantic, fixed_semantic_cols, fixed_semantic_weights = build_routed_features(
        head_parts,
        head_cols,
        "semantic_prior_router",
    )

    router_configs = [
        ("learned_state_router_context", "state_suitability", "context", 0.45, 0.00),
        ("learned_state_router_headsignal", "state_suitability", "headsignal", 0.45, 0.00),
        ("learned_state_router_context_headsignal", "state_suitability", "context_headsignal", 0.45, 0.00),
        ("learned_semantic_router_context_headsignal", "state_suitability_semantic", "context_headsignal", 0.45, 0.00),
        ("learned_semantic_blend_router_context_headsignal", "state_suitability", "context_headsignal", 0.45, 0.35),
        ("learned_semantic_distilled_router_headsignal", "semantic_distilled", "headsignal", 0.45, 0.00),
    ]
    learned_parts: list[pd.DataFrame] = []
    learned_maps: dict[str, dict[str, list[str]]] = {}
    router_pretext_parts: list[pd.DataFrame] = []
    router_weight_parts: list[pd.DataFrame] = [fixed_semantic_weights.assign(split=split_name)]
    for name, teacher_mode, design_mode, pred_blend, semantic_blend in router_configs:
        teacher_weights = {
            target: hidden_head_suitability_teacher(state, views, teachers, target, teacher_mode)
            for target in TARGETS
        }
        weights, pretext, weight_summary = learned_router_weights(
            train_frame,
            relative_context,
            head_parts,
            head_cols,
            teacher_weights,
            folds,
            split_name,
            name,
            design_mode,
            pred_blend,
            semantic_blend,
            f"{teacher_mode}_hidden_head_suitability",
        )
        part, cols = build_learned_routed_features(head_parts, head_cols, weights, name)
        learned_parts.append(part.reset_index(drop=True))
        learned_maps[f"{name}_listener_responsibility"] = cols
        router_pretext_parts.append(pretext)
        router_weight_parts.append(weight_summary)

    features = pd.concat(
        [
            train_frame[raw_cols].reset_index(drop=True),
            state.reset_index(drop=True),
            direct_semantic.reset_index(drop=True),
            *(head_parts[head].reset_index(drop=True) for head in HEADS),
            fixed_semantic.reset_index(drop=True),
            *learned_parts,
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
        "semantic_prior_router_listener_responsibility": fixed_semantic_cols,
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
        "direct_semantic_listener_responsibility": flatten_cols(direct_semantic_cols),
        **{name: flatten_cols(cols) for name, cols in head_maps.items()},
        "multihead_current_future_cohort_listener_responsibility": flatten_cols(
            combine_target_cols([compact_head_cols["current"], compact_head_cols["future"], compact_head_cols["cohort"]])
        ),
        "semantic_prior_router_listener_responsibility": flatten_cols(fixed_semantic_cols),
        **{name: flatten_cols(cols) for name, cols in learned_maps.items()},
    }
    leakage = subject_leakage_probe(train_frame, features, leakage_sets)
    leakage.insert(0, "split", split_name)
    pretext = pd.concat(
        [
            aggregate_pretext(pd.concat(head_pretext_parts, ignore_index=True)),
            aggregate_pretext(pd.concat(router_pretext_parts, ignore_index=True)),
        ],
        ignore_index=True,
        sort=False,
    )
    return metrics, leakage, pretext, pd.concat(router_weight_parts, ignore_index=True, sort=False)


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
    learned_sets = sorted(
        subject_all[
            subject_all["feature_set"].str.startswith("learned_")
            & subject_all["feature_set"].str.endswith("_listener_responsibility_calibrated10")
        ]["feature_set"].tolist()
    )
    single_losses = {name: loss(subject_all, name) for name in single_sets}
    learned_losses = {name: loss(subject_all, name) for name in learned_sets}
    best_single_name = min(
        [name for name, value in single_losses.items() if value is not None],
        key=lambda name: single_losses[name],
    )
    best_learned_name = min(
        [name for name, value in learned_losses.items() if value is not None],
        key=lambda name: learned_losses[name],
    )
    best_single = single_losses[best_single_name]
    best_learned = learned_losses[best_learned_name]
    prior = loss(subject_all, "prior_only_calibrated10")
    raw = loss(subject_all, "raw_lifelog_pca_calibrated10")
    global_transport = loss(subject_all, "global_transported_prototype_calibrated10")
    direct_semantic = loss(subject_all, "direct_semantic_listener_responsibility_calibrated10")
    semantic_prior = loss(subject_all, "semantic_prior_router_listener_responsibility_calibrated10")
    naive_multi = loss(subject_all, "multihead_current_future_cohort_listener_responsibility_calibrated10")
    best_row = loss(row_all, best_learned_name)
    best_chrono = loss(chrono_all, best_learned_name)
    global_row = loss(row_all, "global_transported_prototype_calibrated10")
    global_chrono = loss(chrono_all, "global_transported_prototype_calibrated10")

    verdict = "learned_listener_head_router_negative"
    if best_learned is not None and prior is not None and best_learned < prior:
        verdict = "learned_listener_head_router_prior_positive"
        if best_single is not None and best_learned < best_single:
            verdict = "learned_listener_head_router_beats_single_positive"
        if semantic_prior is not None and best_learned < semantic_prior:
            verdict = "learned_listener_head_router_beats_semantic_positive"
        if global_transport is not None and best_learned < global_transport:
            verdict = "learned_listener_head_router_global_positive"

    return {
        "package": "learned_listener_head_router_core",
        "status": "learned_listener_head_router_core_ready",
        "verdict": verdict,
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "uses_label_as_pretext_target": False,
        "router": "learned_label_free_hidden_head_suitability",
        "context_encoder": "subject_relative_visible_lifelog_context_plus_predicted_listener_heads",
        "subject_prior_logloss": prior,
        "subject_raw_logloss": raw,
        "subject_global_transport_logloss": global_transport,
        "subject_direct_semantic_logloss": direct_semantic,
        "subject_naive_multi_head_logloss": naive_multi,
        "subject_semantic_prior_router_logloss": semantic_prior,
        "subject_best_single_head_feature_set": best_single_name,
        "subject_best_single_head_logloss": best_single,
        "subject_best_learned_router_feature_set": best_learned_name,
        "subject_best_learned_router_logloss": best_learned,
        "subject_best_learned_delta_vs_single": None if best_learned is None or best_single is None else best_learned - best_single,
        "subject_best_learned_delta_vs_semantic_prior": None if best_learned is None or semantic_prior is None else best_learned - semantic_prior,
        "subject_best_learned_delta_vs_prior": None if best_learned is None or prior is None else best_learned - prior,
        "subject_best_learned_delta_vs_raw": None if best_learned is None or raw is None else best_learned - raw,
        "subject_best_learned_delta_vs_direct_semantic": None if best_learned is None or direct_semantic is None else best_learned - direct_semantic,
        "subject_best_learned_delta_vs_naive_multi": None if best_learned is None or naive_multi is None else best_learned - naive_multi,
        "subject_best_learned_delta_vs_global": None if best_learned is None or global_transport is None else best_learned - global_transport,
        "row_block_best_learned_delta_vs_global": None if best_row is None or global_row is None else best_row - global_row,
        "chronological_best_learned_delta_vs_global": None if best_chrono is None or global_chrono is None else best_chrono - global_chrono,
        "subject_pretext_all": {row["feature_set"]: row.to_dict() for _, row in subject_pretext.iterrows()},
        "subject_router_weights": {
            f"{row['router']}::{row['target']}": row.to_dict()
            for _, row in router_weights_frame[router_weights_frame["split"].eq("subject_heldout")].iterrows()
        },
        "subject_best_learned_leakage": leak(best_learned_name.replace("_calibrated10", "")),
        "subject_semantic_prior_leakage": leak("semantic_prior_router_listener_responsibility"),
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
    return f"""# Learned Listener-Head Router Core

## 한 줄 요약

이 실험은 사람이 고정한 semantic-prior router를 넘기 위해,
current/future/cohort head 중 어느 head를 들어야 하는지를 label-free hidden
head-suitability pretext로 학습한다.

```text
visible subject-relative human-life context
  + predicted current/future/cohort listener heads
  -> hidden head-suitability field prediction
  -> learned listener-head router
  -> routed HS-JEPA interface
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

- best learned router: `{summary["subject_best_learned_router_feature_set"]}`
- best learned router logloss: `{format_float(summary["subject_best_learned_router_logloss"], 6)}`
- fixed semantic-prior router logloss: `{format_float(summary["subject_semantic_prior_router_logloss"], 6)}`
- best single head: `{summary["subject_best_single_head_feature_set"]}`
- best single-head logloss: `{format_float(summary["subject_best_single_head_logloss"], 6)}`
- naive multi-head logloss: `{format_float(summary["subject_naive_multi_head_logloss"], 6)}`
- global transport logloss: `{format_float(summary["subject_global_transport_logloss"], 6)}`
- direct semantic logloss: `{format_float(summary["subject_direct_semantic_logloss"], 6)}`
- prior logloss: `{format_float(summary["subject_prior_logloss"], 6)}`
- learned delta vs fixed semantic router: `{format_float(summary["subject_best_learned_delta_vs_semantic_prior"], 6)}`
- learned delta vs single: `{format_float(summary["subject_best_learned_delta_vs_single"], 6)}`
- learned delta vs prior: `{format_float(summary["subject_best_learned_delta_vs_prior"], 6)}`
- learned delta vs raw lifelog PCA: `{format_float(summary["subject_best_learned_delta_vs_raw"], 6)}`
- learned delta vs direct semantic: `{format_float(summary["subject_best_learned_delta_vs_direct_semantic"], 6)}`
- learned delta vs naive multi-head: `{format_float(summary["subject_best_learned_delta_vs_naive_multi"], 6)}`
- learned delta vs global transport: `{format_float(summary["subject_best_learned_delta_vs_global"], 6)}`
- row-block learned delta vs global: `{format_float(summary["row_block_best_learned_delta_vs_global"], 6)}`
- chronological learned delta vs global: `{format_float(summary["chronological_best_learned_delta_vs_global"], 6)}`

## Subject-Heldout Frozen Probe

{markdown_table(subject_all, ["feature_set", "logloss", "auc"], max_rows=28)}

## Row-Block Frozen Probe

{markdown_table(row_all, ["feature_set", "logloss", "auc"], max_rows=28)}

## Chronological Frozen Probe

{markdown_table(chrono_all, ["feature_set", "logloss", "auc"], max_rows=28)}

## Label-Free Router Pretext Quality

{markdown_table(pretext_all, ["split", "feature_set", "pretext_cross_entropy", "prior_cross_entropy", "semantic_cross_entropy", "ce_lift_vs_prior", "ce_lift_vs_semantic", "top1_match_rate"], max_rows=36)}

## Router Weight Summary

{markdown_table(subject_weights, ["router", "target", "mean_w_current", "mean_w_future", "mean_w_cohort", "mean_entropy", "mean_margin"], max_rows=56)}

## Subject Leakage Diagnostic

{markdown_table(subject_leak, ["feature_set", "subject_id_accuracy", "chance_accuracy", "leakage_lift_vs_chance"], max_rows=20)}

## 해석

이 실험은 HS-JEPA의 논문 포인트를 더 엄격하게 찌른다.
기존 fixed semantic router는 사람이 target 의미를 보고 current/future/cohort head prior를 넣었다.
여기서는 그 prior를 hidden head-suitability prediction으로 대체할 수 있는지 본다.

positive이면:

```text
HS-JEPA can learn listener-head routing as a core pretext objective.
```

negative이면:

```text
The current learned router does not yet replace semantic listener priors.
HS-JEPA still needs a stronger route-suitability target or a better router objective.
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

    metrics.to_csv(OUT_DIR / "learned_listener_head_router_probe_metrics.csv", index=False)
    leakage.to_csv(OUT_DIR / "learned_listener_head_router_subject_leakage.csv", index=False)
    pretext.to_csv(OUT_DIR / "learned_listener_head_router_pretext_metrics.csv", index=False)
    router_weights_frame.to_csv(OUT_DIR / "learned_listener_head_router_weights.csv", index=False)
    (OUT_DIR / "learned_listener_head_router_summary.json").write_text(
        json.dumps(json_safe(summary), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    doc = build_markdown(summary, metrics, leakage, pretext, router_weights_frame)
    (OUT_DIR / "LEARNED_LISTENER_HEAD_ROUTER_CORE_KO.md").write_text(doc, encoding="utf-8")
    PAPER_DOC.write_text(doc, encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(json_safe(run()), ensure_ascii=False, indent=2))
