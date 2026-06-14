#!/usr/bin/env python3
"""Rhythm-conditioned action-health core experiment for HS-JEPA.

The residual listener-router helped subject/block readout but was toxic on a
chronological split.  The rhythm-conditioned residual listener experiment then
showed that rhythm context is the better temporal decoder.

This experiment asks the next core-boundary question:

    Can rhythm context + listener residual interfaces predict which row-target
    actions are healthy, before a competition adapter releases them?

It is public-free.  The hidden action-health target is built from OG train
labels only: raw lifelog-memory action vs train-fold prior, measured by
realized logloss gain.  Labels are used only to construct/evaluate this
train-only action-health target, not as a pretext representation.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, mean_absolute_error, roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hsjepa_core.run_action_support_world_model_core import target_context_columns  # noqa: E402
from hsjepa_core.run_global_transport_residual_listener_router_core import (  # noqa: E402
    BEST_LEARNED_DESIGN_MODE,
    BEST_LEARNED_PREDICTION_BLEND,
    BEST_LEARNED_ROUTER_NAME,
    BEST_LEARNED_SEMANTIC_BLEND,
    BEST_LEARNED_TEACHER_MODE,
    build_router_delta_features,
    existing_target_cols,
)
from hsjepa_core.run_label_free_transported_listener_responsibility_core import (  # noqa: E402
    SEMANTIC_TARGET_PROFILES,
    build_label_free_listener_features,
    global_transport_cols,
    load_transport_state,
    split_folds,
)
from hsjepa_core.run_invariant_listener_responsibility_pretext_core import learned_features_from_teacher  # noqa: E402
from hsjepa_core.run_learned_listener_head_router_core import (  # noqa: E402
    build_learned_routed_features,
    hidden_head_suitability_teacher,
    learned_router_weights,
)
from hsjepa_core.run_learned_listener_responsibility_pretext_core import (  # noqa: E402
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
from hsjepa_core.run_listener_head_router_pretext_core import build_routed_features  # noqa: E402
from hsjepa_core.run_multi_head_listener_responsibility_pretext_core import (  # noqa: E402
    HEADS,
    compact_cols,
    combine_target_cols,
    sanitize_features,
    target_teacher_heads,
)
from hsjepa_core.run_rhythm_conditioned_residual_listener_core import (  # noqa: E402
    build_rhythm_gated_target_features,
    clean_name,
    rhythm_context_frame,
)
from hsjepa_core.run_tail_safe_expected_utility_core import (  # noqa: E402
    apply_policies,
    build_mode_tables,
    choose_target_policies,
    classifier_factory,
    policy_grid,
    regressor_factory,
)
from sleep_competition_adapter.target_route_conservation_decoder import build_listener_cells  # noqa: E402


OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "rhythm_conditioned_action_health_core"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "RHYTHM_CONDITIONED_ACTION_HEALTH_CORE_KO.md"
RANDOM_SEED = 20260614
NULL_REPEATS = 10


def safe_auc(y: np.ndarray, score: np.ndarray) -> float | None:
    y = np.asarray(y, dtype=int)
    score = np.asarray(score, dtype=np.float64)
    mask = np.isfinite(score)
    if mask.sum() == 0 or len(np.unique(y[mask])) < 2:
        return None
    return float(roc_auc_score(y[mask], score[mask]))


def safe_ap(y: np.ndarray, score: np.ndarray) -> float | None:
    y = np.asarray(y, dtype=int)
    score = np.asarray(score, dtype=np.float64)
    mask = np.isfinite(score)
    if mask.sum() == 0 or len(np.unique(y[mask])) < 2:
        return None
    return float(average_precision_score(y[mask], score[mask]))


def target_feature_values(
    cells: pd.DataFrame,
    row_features: pd.DataFrame,
    target_to_cols: dict[str, list[str]],
    prefix: str,
) -> tuple[pd.DataFrame, list[str]]:
    """Expand row-level target-specific features into a cell-level table."""

    data: dict[str, np.ndarray] = {}
    row_idx = cells["row"].to_numpy(dtype=np.int64)
    target_values = cells["target"].astype(str).to_numpy()
    output_cols: list[str] = []
    for target in TARGETS:
        mask = target_values == target
        for col in target_to_cols.get(target, []):
            if col not in row_features.columns:
                continue
            out_col = f"{prefix}_{clean_name(col)}"
            if out_col not in data:
                data[out_col] = np.full(len(cells), np.nan, dtype=np.float64)
                output_cols.append(out_col)
            data[out_col][mask] = row_features.iloc[row_idx[mask]][col].to_numpy(dtype=np.float64)
    return pd.DataFrame(data, index=cells.index), output_cols


def shared_row_values(cells: pd.DataFrame, row_features: pd.DataFrame, cols: list[str], prefix: str) -> tuple[pd.DataFrame, list[str]]:
    row_idx = cells["row"].to_numpy(dtype=np.int64)
    data: dict[str, np.ndarray] = {}
    output_cols: list[str] = []
    for col in cols:
        if col not in row_features.columns:
            continue
        out_col = f"{prefix}_{clean_name(col)}"
        data[out_col] = row_features.iloc[row_idx][col].to_numpy(dtype=np.float64)
        output_cols.append(out_col)
    return pd.DataFrame(data, index=cells.index), output_cols


def split_interface_features(
    split_name: str,
    train_frame: pd.DataFrame,
    relative_context: pd.DataFrame,
    views: dict[str, list[str]],
) -> tuple[pd.DataFrame, dict[str, list[str]], dict[str, list[str]], list[str], list[str]]:
    """Build the same rhythm/residual interface used by the frozen label probe."""

    state = load_transport_state(split_name).reset_index(drop=True)
    folds = split_folds(split_name, train_frame)
    direct_semantic, _direct_cols = build_label_free_listener_features(
        state,
        views,
        SEMANTIC_TARGET_PROFILES,
        "direct_semantic",
    )
    teachers = target_teacher_heads(train_frame, relative_context, state, views)
    head_parts: dict[str, pd.DataFrame] = {}
    head_cols: dict[str, dict[str, list[str]]] = {}
    for head in HEADS:
        prefix = f"head_{head}"
        part, cols, _pretext = learned_features_from_teacher(
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

    fixed_semantic, fixed_cols, _fixed_weights = build_routed_features(
        head_parts,
        head_cols,
        "semantic_prior_router",
    )
    teacher_weights = {
        target: hidden_head_suitability_teacher(state, views, teachers, target, BEST_LEARNED_TEACHER_MODE)
        for target in TARGETS
    }
    learned_weights, _learned_pretext, _learned_weight_summary = learned_router_weights(
        train_frame,
        relative_context,
        head_parts,
        head_cols,
        teacher_weights,
        folds,
        split_name,
        BEST_LEARNED_ROUTER_NAME,
        BEST_LEARNED_DESIGN_MODE,
        BEST_LEARNED_PREDICTION_BLEND,
        BEST_LEARNED_SEMANTIC_BLEND,
        f"{BEST_LEARNED_TEACHER_MODE}_hidden_head_suitability",
    )
    learned_router, learned_cols = build_learned_routed_features(
        head_parts,
        head_cols,
        learned_weights,
        BEST_LEARNED_ROUTER_NAME,
    )
    router_delta, router_delta_cols = build_router_delta_features(
        learned_router,
        learned_cols,
        fixed_semantic,
        fixed_cols,
        BEST_LEARNED_ROUTER_NAME,
        "semantic_prior_router",
        "learned_router_residual_delta",
    )
    rhythm, rhythm_cols = rhythm_context_frame(train_frame, state)
    residual_source = pd.concat(
        [
            fixed_semantic.reset_index(drop=True),
            learned_router.reset_index(drop=True),
            router_delta.reset_index(drop=True),
        ],
        axis=1,
    )
    residual_cols = combine_target_cols([fixed_cols, learned_cols, router_delta_cols])
    gated, gated_cols = build_rhythm_gated_target_features(
        residual_source,
        residual_cols,
        rhythm,
        "rhythm_gated_residual",
    )
    row_features = pd.concat(
        [
            state.reset_index(drop=True),
            direct_semantic.reset_index(drop=True),
            *(head_parts[head].reset_index(drop=True) for head in HEADS),
            fixed_semantic.reset_index(drop=True),
            learned_router.reset_index(drop=True),
            router_delta.reset_index(drop=True),
            rhythm.reset_index(drop=True),
            gated.reset_index(drop=True),
        ],
        axis=1,
    )
    row_features = sanitize_features(row_features)
    fixed_cols = existing_target_cols(row_features, fixed_cols)
    learned_cols = existing_target_cols(row_features, learned_cols)
    router_delta_cols = existing_target_cols(row_features, router_delta_cols)
    gated_cols = existing_target_cols(row_features, gated_cols)
    residual_cols = combine_target_cols([fixed_cols, learned_cols, router_delta_cols])
    global_cols = sorted(set(col for col in global_transport_cols(views) if col in row_features.columns))
    rhythm_cols = [col for col in rhythm_cols if col in row_features.columns]
    return row_features, residual_cols, gated_cols, global_cols, rhythm_cols


def add_split_features_to_cells(
    cells: pd.DataFrame,
    row_features: pd.DataFrame,
    residual_cols: dict[str, list[str]],
    gated_cols: dict[str, list[str]],
    global_cols: list[str],
    rhythm_cols: list[str],
) -> tuple[pd.DataFrame, dict[str, list[str]]]:
    parts = [cells.reset_index(drop=True)]
    shared_global, shared_global_cols = shared_row_values(cells, row_features, global_cols, "global_transport")
    shared_rhythm, shared_rhythm_cols = shared_row_values(cells, row_features, rhythm_cols, "rhythm")
    target_residual, target_residual_cols = target_feature_values(cells, row_features, residual_cols, "listener_residual")
    target_gated, target_gated_cols = target_feature_values(cells, row_features, gated_cols, "rhythm_gated_residual")
    parts.extend([shared_global, shared_rhythm, target_residual, target_gated])
    out = pd.concat(parts, axis=1)
    out = sanitize_features(out)
    support_col = "support_score_target_interaction_world_residual_energy"
    if support_col in out.columns:
        if "rhythm_rhythm_stability_gate" in out.columns:
            out["support_x_rhythm_stability"] = out[support_col] * out["rhythm_rhythm_stability_gate"]
            out["move_x_rhythm_stability"] = out["action_move"].astype(float) * out["rhythm_rhythm_stability_gate"]
        if "rhythm_rhythm_instability_gate" in out.columns:
            out["support_x_rhythm_instability"] = out[support_col] * out["rhythm_rhythm_instability_gate"]
            out["move_x_rhythm_instability"] = out["action_move"].astype(float) * out["rhythm_rhythm_instability_gate"]
    feature_groups = {
        "global": shared_global_cols,
        "rhythm": shared_rhythm_cols
        + [
            col
            for col in [
                "support_x_rhythm_stability",
                "support_x_rhythm_instability",
                "move_x_rhythm_stability",
                "move_x_rhythm_instability",
            ]
            if col in out.columns
        ],
        "residual": target_residual_cols,
        "gated": target_gated_cols,
    }
    return out, feature_groups


def add_mode_interactions(modes: pd.DataFrame) -> pd.DataFrame:
    out = modes.copy()
    if "rhythm_rhythm_stability_gate" in out.columns:
        out["mode_rhythm_stability_alignment"] = np.where(
            out["decoder_action"].eq("raw_memory_release"),
            out["rhythm_rhythm_stability_gate"].astype(float),
            out["rhythm_rhythm_instability_gate"].astype(float),
        )
    if "support_score_target_interaction_world_residual_energy" in out.columns and "mode_rhythm_stability_alignment" in out.columns:
        out["listener_support_x_mode_rhythm_alignment"] = (
            out["support_score_target_interaction_world_residual_energy"].astype(float)
            * out["mode_rhythm_stability_alignment"].astype(float)
        )
    return out


def feature_maps(modes: pd.DataFrame, groups: dict[str, list[str]]) -> dict[str, list[str]]:
    action_base = [
        "prior_prob",
        "candidate_prob",
        "inverse_prob",
        "action_prob",
        "action_move",
        "abs_action_move",
        "action_move_rank",
        "decisive_action",
        "action_delta",
        "action_abs_delta",
        "decoder_raw",
        "decoder_inverse",
    ]
    support_cols = [
        col
        for col in [
            "support_score_target_interaction_world_residual_energy",
            "listener_mode_alignment",
            "listener_support_x_mode_rhythm_alignment",
        ]
        if col in modes.columns
    ]
    route_cols = [col for col in modes.columns if col.startswith("route_family__")]
    base = [col for col in target_context_columns() + action_base + route_cols if col in modes.columns]
    out = {
        "action_only": base,
        "listener_support_baseline": base + support_cols,
        "rhythm_temporal_decoder": base + groups["rhythm"],
        "residual_listener_interface": base + support_cols + groups["global"] + groups["residual"],
        "rhythm_conditioned_action_health": (
            base
            + support_cols
            + groups["global"]
            + groups["rhythm"]
            + groups["residual"]
            + groups["gated"]
        ),
    }
    return {name: sorted(set(cols)) for name, cols in out.items()}


def row_folds_to_mode_folds(modes: pd.DataFrame, row_folds: list[tuple[np.ndarray, np.ndarray]]) -> list[tuple[np.ndarray, np.ndarray]]:
    row_values = modes["row"].to_numpy(dtype=np.int64)
    folds: list[tuple[np.ndarray, np.ndarray]] = []
    for tr_rows, va_rows in row_folds:
        tr_set = set(np.asarray(tr_rows, dtype=np.int64).tolist())
        va_set = set(np.asarray(va_rows, dtype=np.int64).tolist())
        tr = np.flatnonzero(np.fromiter((row in tr_set for row in row_values), dtype=bool, count=len(row_values)))
        va = np.flatnonzero(np.fromiter((row in va_set for row in row_values), dtype=bool, count=len(row_values)))
        folds.append((tr, va))
    return folds


def fit_split_utility(
    modes: pd.DataFrame,
    features: list[str],
    folds: list[tuple[np.ndarray, np.ndarray]],
    seed_label: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    y_gain = modes["effective_gain"].astype(float).to_numpy()
    y_tail = modes["tail_loss"].astype(float).to_numpy()
    y_health = modes["healthy_action"].astype(int).to_numpy()
    y_toxic = modes["toxic_tail"].astype(int).to_numpy()
    weights = modes["gain_abs_weight"].astype(float).to_numpy()
    oof_gain = np.zeros(len(modes), dtype=np.float64)
    oof_tail = np.zeros(len(modes), dtype=np.float64)
    oof_health = np.zeros(len(modes), dtype=np.float64)
    oof_toxic = np.zeros(len(modes), dtype=np.float64)
    features = [col for col in features if col in modes.columns]
    for fold, (tr, va) in enumerate(folds):
        gain_model = regressor_factory(RANDOM_SEED + 11 * fold + len(seed_label))
        tail_model = regressor_factory(RANDOM_SEED + 17 * fold + len(features))
        gain_model.fit(modes.iloc[tr][features], y_gain[tr], histgradientboostingregressor__sample_weight=weights[tr])
        tail_model.fit(modes.iloc[tr][features], y_tail[tr], histgradientboostingregressor__sample_weight=weights[tr])
        oof_gain[va] = gain_model.predict(modes.iloc[va][features])
        oof_tail[va] = np.maximum(tail_model.predict(modes.iloc[va][features]), 0.0)
        if len(np.unique(y_health[tr])) < 2:
            oof_health[va] = float(y_health[tr].mean())
        else:
            health_model = classifier_factory(RANDOM_SEED + 23 * fold + len(seed_label))
            health_model.fit(modes.iloc[tr][features], y_health[tr])
            oof_health[va] = health_model.predict_proba(modes.iloc[va][features])[:, 1]
        if len(np.unique(y_toxic[tr])) < 2:
            oof_toxic[va] = float(y_toxic[tr].mean())
        else:
            toxic_model = classifier_factory(RANDOM_SEED + 31 * fold + len(features))
            toxic_model.fit(modes.iloc[tr][features], y_toxic[tr], histgradientboostingclassifier__sample_weight=weights[tr])
            oof_toxic[va] = toxic_model.predict_proba(modes.iloc[va][features])[:, 1]
    scored = modes.copy()
    scored["predicted_gain"] = oof_gain
    scored["predicted_tail_loss"] = oof_tail
    scored["predicted_health_prob"] = oof_health
    scored["predicted_toxic_tail_prob"] = oof_toxic
    scored["tail_safe_utility"] = scored["predicted_gain"] - 1.20 * scored["predicted_tail_loss"] - 0.08 * scored["predicted_toxic_tail_prob"]
    scored["health_weighted_utility"] = scored["predicted_health_prob"] * scored["predicted_gain"] - 1.50 * scored["predicted_toxic_tail_prob"]
    scored["pessimistic_utility"] = scored["predicted_gain"] - 2.00 * scored["predicted_tail_loss"] - 0.20 * scored["predicted_toxic_tail_prob"]
    scored["health_score_only"] = scored["predicted_health_prob"]
    metrics = pd.DataFrame(
        [
            {"metric": "feature_count", "value": len(features)},
            {"metric": "gain_mae", "value": float(mean_absolute_error(y_gain, oof_gain))},
            {"metric": "tail_loss_mae", "value": float(mean_absolute_error(y_tail, oof_tail))},
            {"metric": "health_auc", "value": safe_auc(y_health, oof_health)},
            {"metric": "health_ap", "value": safe_ap(y_health, oof_health)},
            {"metric": "toxic_tail_auc", "value": safe_auc(y_toxic, oof_toxic)},
            {"metric": "toxic_tail_ap", "value": safe_ap(y_toxic, oof_toxic)},
        ]
    )
    return scored, metrics


def evaluate_feature_set(
    split_name: str,
    feature_name: str,
    modes: pd.DataFrame,
    features: list[str],
    folds: list[tuple[np.ndarray, np.ndarray]],
) -> tuple[dict[str, Any], pd.DataFrame, pd.DataFrame]:
    scored, model_metrics = fit_split_utility(modes, features, folds, f"{split_name}:{feature_name}")
    grid = policy_grid(scored, null_repeats=NULL_REPEATS)
    chosen = choose_target_policies(grid)
    audit = apply_policies(scored, chosen)
    selected = audit[audit["released"]].copy()
    gain_sum = float(selected["effective_gain"].sum()) if len(selected) else 0.0
    positive_rate = float((selected["effective_gain"] > 0).mean()) if len(selected) else np.nan
    accepted_targets = chosen.loc[chosen["accepted"].eq(True), "target"].astype(str).tolist()
    row = {
        "split": split_name,
        "feature_set": feature_name,
        "feature_count": int(model_metrics.loc[model_metrics["metric"].eq("feature_count"), "value"].iloc[0]),
        "health_auc": float(model_metrics.loc[model_metrics["metric"].eq("health_auc"), "value"].iloc[0]),
        "health_ap": float(model_metrics.loc[model_metrics["metric"].eq("health_ap"), "value"].iloc[0]),
        "toxic_tail_auc": float(model_metrics.loc[model_metrics["metric"].eq("toxic_tail_auc"), "value"].iloc[0]),
        "toxic_tail_ap": float(model_metrics.loc[model_metrics["metric"].eq("toxic_tail_ap"), "value"].iloc[0]),
        "selected_gain_sum": gain_sum,
        "selected_cells": int(len(selected)),
        "selected_positive_gain_rate": positive_rate,
        "accepted_targets": ",".join(accepted_targets),
        "accepted_target_count": int(len(accepted_targets)),
    }
    chosen = chosen.copy()
    chosen.insert(0, "feature_set", feature_name)
    chosen.insert(0, "split", split_name)
    return row, chosen, audit


def summarize(results: pd.DataFrame) -> dict[str, Any]:
    pivot_gain = results.pivot(index="split", columns="feature_set", values="selected_gain_sum")
    pivot_health = results.pivot(index="split", columns="feature_set", values="health_auc")
    pivot_toxic = results.pivot(index="split", columns="feature_set", values="toxic_tail_auc")

    def table_delta(table: pd.DataFrame, split: str, left: str, right: str) -> float | None:
        if split not in table.index or left not in table.columns or right not in table.columns:
            return None
        return float(table.loc[split, left] - table.loc[split, right])

    subject_delta = table_delta(pivot_gain, "subject_heldout", "rhythm_conditioned_action_health", "listener_support_baseline")
    chrono_delta = table_delta(pivot_gain, "chronological_holdout", "rhythm_conditioned_action_health", "listener_support_baseline")
    row_delta = table_delta(pivot_gain, "row_block_holdout", "rhythm_conditioned_action_health", "listener_support_baseline")
    rhythm_vs_action = table_delta(pivot_gain, "chronological_holdout", "rhythm_temporal_decoder", "action_only")
    subject_health_delta = table_delta(
        pivot_health,
        "subject_heldout",
        "rhythm_conditioned_action_health",
        "listener_support_baseline",
    )
    chrono_health_delta = table_delta(
        pivot_health,
        "chronological_holdout",
        "rhythm_conditioned_action_health",
        "listener_support_baseline",
    )
    subject_toxic_delta = table_delta(
        pivot_toxic,
        "subject_heldout",
        "rhythm_conditioned_action_health",
        "listener_support_baseline",
    )
    chrono_toxic_delta = table_delta(
        pivot_toxic,
        "chronological_holdout",
        "rhythm_conditioned_action_health",
        "listener_support_baseline",
    )
    accepted_total = int(results["accepted_target_count"].sum())
    verdict = "rhythm_conditioned_action_health_negative"
    if accepted_total == 0:
        verdict = "rhythm_conditioned_action_health_no_safe_assignment_boundary"
    elif (chrono_delta or 0.0) > 0.0 and (subject_delta or 0.0) > 0.0:
        verdict = "rhythm_conditioned_action_health_subject_chrono_positive"
    elif (chrono_delta or 0.0) > 0.0:
        verdict = "rhythm_conditioned_action_health_temporal_positive_subject_boundary"
    elif (subject_delta or 0.0) > 0.0:
        verdict = "rhythm_conditioned_action_health_subject_positive_temporal_boundary"
    best_rows = (
        results.sort_values(["split", "selected_gain_sum"], ascending=[True, False])
        .groupby("split", observed=True)
        .head(1)
    )
    return {
        "package": "rhythm_conditioned_action_health_core",
        "status": "rhythm_conditioned_action_health_core_ready",
        "verdict": verdict,
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "uses_label_as_pretext_target": False,
        "architecture_question": "can_rhythm_temporal_decoder_and_listener_residual_interface_predict_action_health",
        "subject_delta_vs_listener_support": subject_delta,
        "row_block_delta_vs_listener_support": row_delta,
        "chronological_delta_vs_listener_support": chrono_delta,
        "chronological_rhythm_temporal_delta_vs_action_only": rhythm_vs_action,
        "subject_health_auc_delta_vs_listener_support": subject_health_delta,
        "chronological_health_auc_delta_vs_listener_support": chrono_health_delta,
        "subject_toxic_tail_auc_delta_vs_listener_support": subject_toxic_delta,
        "chronological_toxic_tail_auc_delta_vs_listener_support": chrono_toxic_delta,
        "accepted_target_count_total": accepted_total,
        "best_by_split": best_rows.to_dict(orient="records"),
        "gain_pivot": pivot_gain.reset_index().to_dict(orient="records"),
        "health_auc_pivot": pivot_health.reset_index().to_dict(orient="records"),
        "toxic_tail_auc_pivot": pivot_toxic.reset_index().to_dict(orient="records"),
    }


def build_markdown(summary: dict[str, Any], results: pd.DataFrame, chosen: pd.DataFrame) -> str:
    return f"""# Rhythm-Conditioned Action-Health Core

## 한 줄 요약

이 실험은 HS-JEPA의 rhythm temporal decoder와 listener residual interface가
실제 row-target action toxicity / safe assignment field로 이어지는지 검증한다.

```text
transported human-state grammar
  + listener residual interface
  + rhythm-conditioned temporal decoder
  -> hidden action-health / toxicity representation
```

## 사용하지 않은 정보

- public LB ledger: `{summary["uses_public_score_ledger"]}`
- prior submission probabilities: `{summary["uses_prior_submission_probabilities"]}`
- proprietary embedding API: `{summary["uses_proprietary_embedding_api"]}`
- label as pretext target: `{summary["uses_label_as_pretext_target"]}`

## 판정

- verdict: `{summary["verdict"]}`
- subject delta vs listener-support baseline: `{format_float(summary["subject_delta_vs_listener_support"], 6)}`
- row-block delta vs listener-support baseline: `{format_float(summary["row_block_delta_vs_listener_support"], 6)}`
- chronological delta vs listener-support baseline: `{format_float(summary["chronological_delta_vs_listener_support"], 6)}`
- chronological rhythm-temporal delta vs action-only: `{format_float(summary["chronological_rhythm_temporal_delta_vs_action_only"], 6)}`
- subject health-AUC delta vs listener-support baseline: `{format_float(summary["subject_health_auc_delta_vs_listener_support"], 6)}`
- chronological health-AUC delta vs listener-support baseline: `{format_float(summary["chronological_health_auc_delta_vs_listener_support"], 6)}`
- subject toxic-tail-AUC delta vs listener-support baseline: `{format_float(summary["subject_toxic_tail_auc_delta_vs_listener_support"], 6)}`
- chronological toxic-tail-AUC delta vs listener-support baseline: `{format_float(summary["chronological_toxic_tail_auc_delta_vs_listener_support"], 6)}`
- accepted target count total: `{summary["accepted_target_count_total"]}`

## Split Results

{markdown_table(results, ["split", "feature_set", "feature_count", "health_auc", "health_ap", "toxic_tail_auc", "toxic_tail_ap", "selected_gain_sum", "selected_cells", "selected_positive_gain_rate", "accepted_targets"], max_rows=80)}

## Chosen Target Policies

{markdown_table(chosen, ["split", "feature_set", "target", "accepted", "score_col", "policy", "fraction", "selected_cells", "selected_gain_sum", "selected_positive_gain_rate", "positive_subjects", "negative_subjects", "gain_lift_vs_null", "tail_safe_policy_score", "accept_reason"], max_rows=80)}

## 해석

positive이면:

```text
HS-JEPA core representation은 단순히 label geometry를 만들 뿐 아니라,
visible rhythm context와 listener residual을 통해 action-health field까지 읽을 수 있다.
```

negative이면:

```text
rhythm/residual representation은 label readout에는 도움이 되지만,
safe action assignment로 번역하려면 별도의 action-tail teacher나 adapter가 필요하다.
```

특히 `accepted target count total`이 0이면 다음 믿음은 죽는다.

```text
rhythm-conditioned residual interface alone is already an action-grade decoder.
```

현재 이 실험은 submission 후보가 아니다.
목적은 HS-JEPA core가 action-health로 확장되는지 반증하는 것이다.
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

    base_train_cells, base_test_cells, _priors, _view_metrics = build_listener_cells()
    _test_modes_placeholder = base_test_cells.copy()

    result_rows: list[dict[str, Any]] = []
    chosen_parts: list[pd.DataFrame] = []
    audit_parts: list[pd.DataFrame] = []
    for split_name in ["subject_heldout", "chronological_holdout", "row_block_holdout"]:
        row_features, residual_cols, gated_cols, global_cols, rhythm_cols = split_interface_features(
            split_name,
            train_frame,
            relative_context,
            views,
        )
        train_cells, groups = add_split_features_to_cells(
            base_train_cells,
            row_features,
            residual_cols,
            gated_cols,
            global_cols,
            rhythm_cols,
        )
        train_modes, _test_modes = build_mode_tables(train_cells, _test_modes_placeholder)
        train_modes = add_mode_interactions(train_modes)
        fmap = feature_maps(train_modes, groups)
        mode_folds = row_folds_to_mode_folds(train_modes, split_folds(split_name, train_frame))
        for feature_name, cols in fmap.items():
            row, chosen, audit = evaluate_feature_set(split_name, feature_name, train_modes, cols, mode_folds)
            result_rows.append(row)
            chosen_parts.append(chosen)
            audit = audit[audit["released"]].copy()
            audit["split"] = split_name
            audit["feature_set"] = feature_name
            keep_cols = [
                "split",
                "feature_set",
                "row",
                "metric_row",
                "subject_id",
                "target",
                "decoder_action",
                "effective_gain",
                "predicted_gain",
                "predicted_tail_loss",
                "predicted_health_prob",
                "predicted_toxic_tail_prob",
            ]
            audit_parts.append(audit[[col for col in keep_cols if col in audit.columns]])

    results = pd.DataFrame(result_rows).sort_values(["split", "selected_gain_sum"], ascending=[True, False])
    chosen_all = pd.concat(chosen_parts, ignore_index=True, sort=False)
    audit_all = pd.concat(audit_parts, ignore_index=True, sort=False) if audit_parts else pd.DataFrame()
    summary = summarize(results)

    results.to_csv(OUT_DIR / "rhythm_conditioned_action_health_split_results.csv", index=False)
    chosen_all.to_csv(OUT_DIR / "rhythm_conditioned_action_health_chosen_policies.csv", index=False)
    audit_all.to_csv(OUT_DIR / "rhythm_conditioned_action_health_action_audit.csv", index=False)
    (OUT_DIR / "rhythm_conditioned_action_health_summary.json").write_text(
        json.dumps(json_safe(summary), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    doc = build_markdown(summary, results, chosen_all)
    (OUT_DIR / "RHYTHM_CONDITIONED_ACTION_HEALTH_CORE_KO.md").write_text(doc, encoding="utf-8")
    PAPER_DOC.write_text(doc, encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(json_safe(run()), ensure_ascii=False, indent=2))
