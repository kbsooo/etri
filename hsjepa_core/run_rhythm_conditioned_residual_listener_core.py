#!/usr/bin/env python3
"""HS-JEPA rhythm-conditioned residual listener core experiment.

The previous residual listener-router experiment showed a useful split:

    subject-heldout / row-block: residual listener routing helps
    chronological holdout: residual listener routing is toxic

This experiment does not tune leaderboard actions.  It asks a core world-model
question:

    Can visible rhythm context tell when a listener residual should be read as
    stable grammar and when it should be treated as temporal drift?

The representation is public-free and label-free until the frozen probe stage.
"""

from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hsjepa_core.run_global_transport_residual_listener_router_core import (  # noqa: E402
    BEST_LEARNED_DESIGN_MODE,
    BEST_LEARNED_PREDICTION_BLEND,
    BEST_LEARNED_ROUTER_NAME,
    BEST_LEARNED_SEMANTIC_BLEND,
    BEST_LEARNED_TEACHER_MODE,
    add_global,
    build_router_delta_features,
    existing_target_cols,
)
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
from hsjepa_core.run_learned_listener_head_router_core import (  # noqa: E402
    build_learned_routed_features,
    hidden_head_suitability_teacher,
    learned_router_weights,
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
from hsjepa_core.run_listener_head_router_pretext_core import build_routed_features, standardize  # noqa: E402
from hsjepa_core.run_multi_head_listener_responsibility_pretext_core import (  # noqa: E402
    HEADS,
    HEAD_PREFIX,
    combine_target_cols,
    compact_cols,
    sanitize_features,
    target_teacher_heads,
)


OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "rhythm_conditioned_residual_listener_core"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "RHYTHM_CONDITIONED_RESIDUAL_LISTENER_CORE_KO.md"


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(values, -30.0, 30.0)))


def clean_name(col: str) -> str:
    cleaned = re.sub(r"[^0-9a-zA-Z]+", "_", col)
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned[-96:]


def rhythm_context_frame(train_frame: pd.DataFrame, state: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Build label-free rhythm context and stability features."""

    out = pd.DataFrame(index=train_frame.index)
    confidence = state["cspg_pred_calendar_rhythm_confidence"].to_numpy(dtype=np.float64)
    entropy = state["cspg_pred_calendar_rhythm_entropy"].to_numpy(dtype=np.float64)
    energy_lift = state["cspg_energy_lift_calendar_rhythm"].to_numpy(dtype=np.float64)
    energy = state["cspg_energy_calendar_rhythm"].to_numpy(dtype=np.float64)
    stability = sigmoid(
        0.85 * standardize(confidence)
        + 0.35 * standardize(energy_lift)
        - 0.70 * standardize(entropy)
        - 0.25 * standardize(energy)
    )
    out["rhythm_confidence"] = confidence
    out["rhythm_entropy"] = entropy
    out["rhythm_energy_lift"] = energy_lift
    out["rhythm_energy"] = energy
    out["rhythm_stability_gate"] = stability
    out["rhythm_instability_gate"] = 1.0 - stability
    for col in ["is_weekend", "dayofweek", "dayofmonth", "month_start_proximity", "month_end"]:
        if col in train_frame.columns:
            out[f"rhythm_{col}"] = pd.to_numeric(train_frame[col], errors="coerce").to_numpy(dtype=np.float64)
    if "dayofweek" in train_frame.columns:
        dow = pd.to_numeric(train_frame["dayofweek"], errors="coerce").fillna(0).to_numpy(dtype=np.float64)
        out["rhythm_dayofweek_sin"] = np.sin(2.0 * math.pi * dow / 7.0)
        out["rhythm_dayofweek_cos"] = np.cos(2.0 * math.pi * dow / 7.0)
    if "dayofmonth" in train_frame.columns:
        dom = pd.to_numeric(train_frame["dayofmonth"], errors="coerce").fillna(15).to_numpy(dtype=np.float64)
        out["rhythm_dayofmonth_sin"] = np.sin(2.0 * math.pi * dom / 31.0)
        out["rhythm_dayofmonth_cos"] = np.cos(2.0 * math.pi * dom / 31.0)
    out = sanitize_features(out)
    return out, list(out.columns)


def build_rhythm_gated_target_features(
    source: pd.DataFrame,
    source_cols: dict[str, list[str]],
    rhythm: pd.DataFrame,
    prefix: str,
) -> tuple[pd.DataFrame, dict[str, list[str]]]:
    """Expose residual features through stable/unstable rhythm gates."""

    gate_cols = [
        "rhythm_stability_gate",
        "rhythm_instability_gate",
        "rhythm_is_weekend",
        "rhythm_month_end",
        "rhythm_month_start_proximity",
    ]
    gate_cols = [col for col in gate_cols if col in rhythm.columns]
    base_keep_markers = (
        "_routed",
        "_router_margin",
        "_router_entropy",
        "learned_minus_semantic",
    )
    data: dict[str, np.ndarray] = {}
    target_cols: dict[str, list[str]] = {}
    for target in TARGETS:
        cols_for_target: list[str] = []
        selected = [
            col
            for col in source_cols[target]
            if any(marker in col for marker in base_keep_markers)
        ]
        for col in selected:
            values = np.nan_to_num(
                source[col].to_numpy(dtype=np.float64),
                nan=0.0,
                posinf=0.0,
                neginf=0.0,
            )
            name = clean_name(col)
            for gate_col in gate_cols:
                gated_col = f"{prefix}_{target}_{name}_x_{gate_col}"
                data[gated_col] = values * rhythm[gate_col].to_numpy(dtype=np.float64)
                cols_for_target.append(gated_col)
        target_cols[target] = cols_for_target
    return pd.DataFrame(data, index=source.index), target_cols


def evaluate_split_package(
    split_name: str,
    train_frame: pd.DataFrame,
    relative_context: pd.DataFrame,
    raw_cols: list[str],
    views: dict[str, list[str]],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    state = load_transport_state(split_name)
    folds = split_folds(split_name, train_frame)

    direct_semantic, _direct_semantic_cols = build_label_free_listener_features(
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
    teacher_weights = {
        target: hidden_head_suitability_teacher(
            state,
            views,
            teachers,
            target,
            BEST_LEARNED_TEACHER_MODE,
        )
        for target in TARGETS
    }
    learned_weights, learned_pretext, learned_weight_summary = learned_router_weights(
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
    learned_router, learned_router_cols = build_learned_routed_features(
        head_parts,
        head_cols,
        learned_weights,
        BEST_LEARNED_ROUTER_NAME,
    )
    router_delta, router_delta_cols = build_router_delta_features(
        learned_router,
        learned_router_cols,
        fixed_semantic,
        fixed_semantic_cols,
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
    residual_cols = combine_target_cols([fixed_semantic_cols, learned_router_cols, router_delta_cols])
    rhythm_gated_residual, rhythm_gated_residual_cols = build_rhythm_gated_target_features(
        residual_source,
        residual_cols,
        rhythm,
        "rhythm_gated_residual",
    )

    features = pd.concat(
        [
            train_frame[raw_cols].reset_index(drop=True),
            state.reset_index(drop=True),
            direct_semantic.reset_index(drop=True),
            *(head_parts[head].reset_index(drop=True) for head in HEADS),
            fixed_semantic.reset_index(drop=True),
            learned_router.reset_index(drop=True),
            router_delta.reset_index(drop=True),
            rhythm.reset_index(drop=True),
            rhythm_gated_residual.reset_index(drop=True),
        ],
        axis=1,
    )
    features = sanitize_features(features)
    global_cols = sorted(set(col for col in global_transport_cols(views) if col in features.columns))
    fixed_semantic_cols = existing_target_cols(features, fixed_semantic_cols)
    learned_router_cols = existing_target_cols(features, learned_router_cols)
    router_delta_cols = existing_target_cols(features, router_delta_cols)
    rhythm_gated_residual_cols = existing_target_cols(features, rhythm_gated_residual_cols)
    rhythm_cols = [col for col in rhythm_cols if col in features.columns]
    residual_cols = combine_target_cols([fixed_semantic_cols, learned_router_cols, router_delta_cols])

    feature_maps = {
        "prior_only": {target: [] for target in TARGETS},
        "raw_lifelog_pca": {target: raw_cols for target in TARGETS},
        "global_transported_prototype": {target: global_cols for target in TARGETS},
        "rhythm_context": {target: rhythm_cols for target in TARGETS},
        "global_plus_rhythm_context": {target: sorted(set(global_cols + rhythm_cols)) for target in TARGETS},
        "future_listener_head": compact_head_cols["future"],
        "semantic_prior_router": fixed_semantic_cols,
        "learned_listener_head_router": learned_router_cols,
        "global_plus_semantic_and_learned_router": add_global(global_cols, residual_cols),
        "rhythm_gated_residual_listener": rhythm_gated_residual_cols,
        "global_plus_rhythm_gated_residual_listener": add_global(global_cols, rhythm_gated_residual_cols),
        "global_plus_rhythm_context_and_gated_residual": add_global(
            global_cols + rhythm_cols,
            rhythm_gated_residual_cols,
        ),
        "global_plus_residual_and_rhythm_gated_residual": add_global(
            global_cols,
            combine_target_cols([residual_cols, rhythm_gated_residual_cols]),
        ),
        "global_plus_residual_rhythm_context_and_gated_residual": add_global(
            global_cols + rhythm_cols,
            combine_target_cols([residual_cols, rhythm_gated_residual_cols]),
        ),
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
        "rhythm_context": rhythm_cols,
        "global_plus_rhythm_context": sorted(set(global_cols + rhythm_cols)),
        "global_plus_semantic_and_learned_router": sorted(set(global_cols + flatten_cols(residual_cols))),
        "rhythm_gated_residual_listener": flatten_cols(rhythm_gated_residual_cols),
        "global_plus_rhythm_gated_residual_listener": sorted(
            set(global_cols + flatten_cols(rhythm_gated_residual_cols))
        ),
        "global_plus_rhythm_context_and_gated_residual": sorted(
            set(global_cols + rhythm_cols + flatten_cols(rhythm_gated_residual_cols))
        ),
        "global_plus_residual_and_rhythm_gated_residual": sorted(
            set(global_cols + flatten_cols(residual_cols) + flatten_cols(rhythm_gated_residual_cols))
        ),
        "global_plus_residual_rhythm_context_and_gated_residual": sorted(
            set(global_cols + rhythm_cols + flatten_cols(residual_cols) + flatten_cols(rhythm_gated_residual_cols))
        ),
    }
    leakage = subject_leakage_probe(train_frame, features, leakage_sets)
    leakage.insert(0, "split", split_name)
    pretext = pd.concat(
        [
            aggregate_pretext(pd.concat(head_pretext_parts, ignore_index=True)),
            aggregate_pretext(learned_pretext),
        ],
        ignore_index=True,
        sort=False,
    )
    weights = pd.concat(
        [
            fixed_semantic_weights.assign(split=split_name),
            learned_weight_summary,
        ],
        ignore_index=True,
        sort=False,
    )
    return metrics, leakage, pretext, weights


def split_loss(metrics: pd.DataFrame, split: str, feature_set: str) -> float | None:
    part = metrics[
        metrics["split"].eq(split)
        & metrics["target"].eq("all")
        & metrics["feature_set"].eq(feature_set)
    ]
    return None if part.empty else float(part["logloss"].iloc[0])


def summarize(
    metrics: pd.DataFrame,
    leakage: pd.DataFrame,
    pretext: pd.DataFrame,
    router_weights_frame: pd.DataFrame,
) -> dict[str, Any]:
    suffix = "_calibrated10"
    global_name = f"global_transported_prototype{suffix}"
    plain_residual_name = f"global_plus_semantic_and_learned_router{suffix}"
    rhythm_candidates = sorted(
        name
        for name in metrics[
            metrics["split"].eq("chronological_holdout") & metrics["target"].eq("all")
        ]["feature_set"].tolist()
        if "rhythm" in name and name.endswith(suffix)
    )
    chrono_best_rhythm = min(
        rhythm_candidates,
        key=lambda name: split_loss(metrics, "chronological_holdout", name)
        if split_loss(metrics, "chronological_holdout", name) is not None
        else np.inf,
    )
    subject_best_rhythm = min(
        rhythm_candidates,
        key=lambda name: split_loss(metrics, "subject_heldout", name)
        if split_loss(metrics, "subject_heldout", name) is not None
        else np.inf,
    )
    row_best_rhythm = min(
        rhythm_candidates,
        key=lambda name: split_loss(metrics, "row_block_holdout", name)
        if split_loss(metrics, "row_block_holdout", name) is not None
        else np.inf,
    )
    gated_candidates = [name for name in rhythm_candidates if "gated_residual" in name]
    chrono_best_gated = min(
        gated_candidates,
        key=lambda name: split_loss(metrics, "chronological_holdout", name)
        if split_loss(metrics, "chronological_holdout", name) is not None
        else np.inf,
    )
    subject_best_gated = min(
        gated_candidates,
        key=lambda name: split_loss(metrics, "subject_heldout", name)
        if split_loss(metrics, "subject_heldout", name) is not None
        else np.inf,
    )
    row_best_gated = min(
        gated_candidates,
        key=lambda name: split_loss(metrics, "row_block_holdout", name)
        if split_loss(metrics, "row_block_holdout", name) is not None
        else np.inf,
    )

    def leak(feature_set: str) -> dict[str, Any] | None:
        part = leakage[leakage["split"].eq("subject_heldout") & leakage["feature_set"].eq(feature_set)]
        return None if part.empty else part.iloc[0].to_dict()

    global_subject = split_loss(metrics, "subject_heldout", global_name)
    global_row = split_loss(metrics, "row_block_holdout", global_name)
    global_chrono = split_loss(metrics, "chronological_holdout", global_name)
    plain_subject = split_loss(metrics, "subject_heldout", plain_residual_name)
    plain_row = split_loss(metrics, "row_block_holdout", plain_residual_name)
    plain_chrono = split_loss(metrics, "chronological_holdout", plain_residual_name)
    chrono_best_loss = split_loss(metrics, "chronological_holdout", chrono_best_rhythm)
    subject_best_loss = split_loss(metrics, "subject_heldout", subject_best_rhythm)
    row_best_loss = split_loss(metrics, "row_block_holdout", row_best_rhythm)
    chrono_best_gated_loss = split_loss(metrics, "chronological_holdout", chrono_best_gated)
    subject_best_gated_loss = split_loss(metrics, "subject_heldout", subject_best_gated)
    row_best_gated_loss = split_loss(metrics, "row_block_holdout", row_best_gated)

    verdict = "rhythm_conditioned_residual_listener_negative"
    if chrono_best_loss is not None and global_chrono is not None and chrono_best_loss < global_chrono:
        verdict = "rhythm_context_temporal_decoder_positive"
        if (
            subject_best_gated_loss is not None
            and plain_subject is not None
            and subject_best_gated_loss < plain_subject
        ):
            verdict = "rhythm_context_temporal_decoder_with_gated_residual_subject_positive"
        if (
            chrono_best_gated_loss is not None
            and plain_chrono is not None
            and chrono_best_gated_loss < plain_chrono
            and chrono_best_gated_loss <= global_chrono
        ):
            verdict = "rhythm_gated_residual_temporal_positive"
    elif subject_best_loss is not None and global_subject is not None and subject_best_loss < global_subject:
        verdict = "rhythm_conditioned_residual_listener_subject_positive_only"

    subject_pretext = pretext[(pretext["split"].eq("subject_heldout")) & (pretext["target"].eq("all"))]
    return {
        "package": "rhythm_conditioned_residual_listener_core",
        "status": "rhythm_conditioned_residual_listener_core_ready",
        "verdict": verdict,
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "uses_label_as_pretext_target": False,
        "architecture_question": "can_visible_rhythm_context_separate_stable_listener_residual_from_temporal_drift",
        "context_encoder": "calendar_rhythm_transport_confidence_energy_plus_subject_relative_visible_lifelog_context",
        "residual_interface": "global_transport_backbone_plus_rhythm_gated_listener_residual",
        "global_feature_set": global_name,
        "plain_residual_feature_set": plain_residual_name,
        "chronological_best_rhythm_feature_set": chrono_best_rhythm,
        "subject_best_rhythm_feature_set": subject_best_rhythm,
        "row_block_best_rhythm_feature_set": row_best_rhythm,
        "chronological_best_gated_residual_feature_set": chrono_best_gated,
        "subject_best_gated_residual_feature_set": subject_best_gated,
        "row_block_best_gated_residual_feature_set": row_best_gated,
        "subject_global_logloss": global_subject,
        "subject_plain_residual_logloss": plain_subject,
        "subject_best_rhythm_logloss": subject_best_loss,
        "subject_plain_residual_delta_vs_global": None
        if plain_subject is None or global_subject is None
        else plain_subject - global_subject,
        "subject_best_rhythm_delta_vs_global": None
        if subject_best_loss is None or global_subject is None
        else subject_best_loss - global_subject,
        "subject_best_rhythm_delta_vs_plain_residual": None
        if subject_best_loss is None or plain_subject is None
        else subject_best_loss - plain_subject,
        "subject_best_gated_residual_logloss": subject_best_gated_loss,
        "subject_best_gated_residual_delta_vs_plain_residual": None
        if subject_best_gated_loss is None or plain_subject is None
        else subject_best_gated_loss - plain_subject,
        "row_block_global_logloss": global_row,
        "row_block_plain_residual_logloss": plain_row,
        "row_block_best_rhythm_logloss": row_best_loss,
        "row_block_best_rhythm_delta_vs_global": None
        if row_best_loss is None or global_row is None
        else row_best_loss - global_row,
        "row_block_best_rhythm_delta_vs_plain_residual": None
        if row_best_loss is None or plain_row is None
        else row_best_loss - plain_row,
        "row_block_best_gated_residual_logloss": row_best_gated_loss,
        "row_block_best_gated_residual_delta_vs_plain_residual": None
        if row_best_gated_loss is None or plain_row is None
        else row_best_gated_loss - plain_row,
        "chronological_global_logloss": global_chrono,
        "chronological_plain_residual_logloss": plain_chrono,
        "chronological_best_rhythm_logloss": chrono_best_loss,
        "chronological_plain_residual_delta_vs_global": None
        if plain_chrono is None or global_chrono is None
        else plain_chrono - global_chrono,
        "chronological_best_rhythm_delta_vs_global": None
        if chrono_best_loss is None or global_chrono is None
        else chrono_best_loss - global_chrono,
        "chronological_best_rhythm_delta_vs_plain_residual": None
        if chrono_best_loss is None or plain_chrono is None
        else chrono_best_loss - plain_chrono,
        "chronological_best_gated_residual_logloss": chrono_best_gated_loss,
        "chronological_best_gated_residual_delta_vs_global": None
        if chrono_best_gated_loss is None or global_chrono is None
        else chrono_best_gated_loss - global_chrono,
        "chronological_best_gated_residual_delta_vs_plain_residual": None
        if chrono_best_gated_loss is None or plain_chrono is None
        else chrono_best_gated_loss - plain_chrono,
        "subject_pretext_all": {row["feature_set"]: row.to_dict() for _, row in subject_pretext.iterrows()},
        "subject_router_weights": {
            f"{row['router']}::{row['target']}": row.to_dict()
            for _, row in router_weights_frame[router_weights_frame["split"].eq("subject_heldout")].iterrows()
        },
        "subject_best_rhythm_leakage": leak(subject_best_rhythm.replace(suffix, "")),
        "subject_best_gated_residual_leakage": leak(subject_best_gated.replace(suffix, "")),
        "global_transport_subject_leakage": leak("global_transported_prototype"),
        "plain_residual_subject_leakage": leak("global_plus_semantic_and_learned_router"),
        "rhythm_context_subject_leakage": leak("rhythm_context"),
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
    target_rows = metrics[
        metrics["split"].eq("chronological_holdout")
        & metrics["target"].isin(TARGETS)
        & metrics["feature_set"].eq(summary["chronological_best_rhythm_feature_set"])
    ].sort_values("target")
    pretext_all = pretext[pretext["target"].eq("all")].sort_values(["split", "feature_set"])
    subject_leak = leakage[leakage["split"].eq("subject_heldout")].sort_values("subject_id_accuracy")
    subject_weights = router_weights_frame[router_weights_frame["split"].eq("subject_heldout")].sort_values(
        ["router", "target"]
    )
    return f"""# Rhythm-Conditioned Residual Listener Core

## 한 줄 요약

이 실험은 residual listener router가 시간 순서 split에서 독성을 보인 이유를
`리듬이 안정적인 날의 residual`과 `리듬이 흔들리는 날의 residual`을 구분하지 못했기 때문이라고 가정한다.

```text
calendar rhythm confidence / entropy / energy
  -> rhythm stability gate
  -> stable residual listener channel
  -> unstable residual listener channel
  -> frozen downstream probe
```

## 판정

- verdict: `{summary["verdict"]}`
- public LB ledger 사용: `{summary["uses_public_score_ledger"]}`
- prior submission probability 사용: `{summary["uses_prior_submission_probabilities"]}`
- proprietary embedding API 사용: `{summary["uses_proprietary_embedding_api"]}`
- label을 pretext target으로 사용: `{summary["uses_label_as_pretext_target"]}`
- architecture question: `{summary["architecture_question"]}`
- residual interface: `{summary["residual_interface"]}`

## 핵심 수치

### Subject-Heldout

- global transport: `{format_float(summary["subject_global_logloss"], 6)}`
- plain residual: `{format_float(summary["subject_plain_residual_logloss"], 6)}`
- best rhythm feature: `{summary["subject_best_rhythm_feature_set"]}`
- best rhythm logloss: `{format_float(summary["subject_best_rhythm_logloss"], 6)}`
- best rhythm delta vs global: `{format_float(summary["subject_best_rhythm_delta_vs_global"], 6)}`
- best rhythm delta vs plain residual: `{format_float(summary["subject_best_rhythm_delta_vs_plain_residual"], 6)}`
- best gated residual feature: `{summary["subject_best_gated_residual_feature_set"]}`
- best gated residual logloss: `{format_float(summary["subject_best_gated_residual_logloss"], 6)}`
- best gated residual delta vs plain residual: `{format_float(summary["subject_best_gated_residual_delta_vs_plain_residual"], 6)}`

### Row-Block

- global transport: `{format_float(summary["row_block_global_logloss"], 6)}`
- plain residual: `{format_float(summary["row_block_plain_residual_logloss"], 6)}`
- best rhythm feature: `{summary["row_block_best_rhythm_feature_set"]}`
- best rhythm logloss: `{format_float(summary["row_block_best_rhythm_logloss"], 6)}`
- best rhythm delta vs global: `{format_float(summary["row_block_best_rhythm_delta_vs_global"], 6)}`
- best rhythm delta vs plain residual: `{format_float(summary["row_block_best_rhythm_delta_vs_plain_residual"], 6)}`
- best gated residual feature: `{summary["row_block_best_gated_residual_feature_set"]}`
- best gated residual logloss: `{format_float(summary["row_block_best_gated_residual_logloss"], 6)}`
- best gated residual delta vs plain residual: `{format_float(summary["row_block_best_gated_residual_delta_vs_plain_residual"], 6)}`

### Chronological

- global transport: `{format_float(summary["chronological_global_logloss"], 6)}`
- plain residual: `{format_float(summary["chronological_plain_residual_logloss"], 6)}`
- plain residual delta vs global: `{format_float(summary["chronological_plain_residual_delta_vs_global"], 6)}`
- best rhythm feature: `{summary["chronological_best_rhythm_feature_set"]}`
- best rhythm logloss: `{format_float(summary["chronological_best_rhythm_logloss"], 6)}`
- best rhythm delta vs global: `{format_float(summary["chronological_best_rhythm_delta_vs_global"], 6)}`
- best rhythm delta vs plain residual: `{format_float(summary["chronological_best_rhythm_delta_vs_plain_residual"], 6)}`
- best gated residual feature: `{summary["chronological_best_gated_residual_feature_set"]}`
- best gated residual logloss: `{format_float(summary["chronological_best_gated_residual_logloss"], 6)}`
- best gated residual delta vs global: `{format_float(summary["chronological_best_gated_residual_delta_vs_global"], 6)}`
- best gated residual delta vs plain residual: `{format_float(summary["chronological_best_gated_residual_delta_vs_plain_residual"], 6)}`

## Subject-Heldout Frozen Probe

{markdown_table(subject_all, ["feature_set", "logloss", "auc"], max_rows=32)}

## Row-Block Frozen Probe

{markdown_table(row_all, ["feature_set", "logloss", "auc"], max_rows=32)}

## Chronological Frozen Probe

{markdown_table(chrono_all, ["feature_set", "logloss", "auc"], max_rows=32)}

## Chronological Target Breakdown For Best Rhythm Feature

{markdown_table(target_rows, ["target", "logloss", "auc"], max_rows=12)}

## Label-Free Pretext Quality

{markdown_table(pretext_all, ["split", "feature_set", "pretext_cross_entropy", "prior_cross_entropy", "semantic_cross_entropy", "ce_lift_vs_prior", "ce_lift_vs_semantic", "top1_match_rate"], max_rows=36)}

## Router Weight Summary

{markdown_table(subject_weights, ["router", "target", "mean_w_current", "mean_w_future", "mean_w_cohort", "mean_entropy", "mean_margin"], max_rows=56)}

## Subject Leakage Diagnostic

{markdown_table(subject_leak, ["feature_set", "subject_id_accuracy", "chance_accuracy", "leakage_lift_vs_chance"], max_rows=16)}

## 해석

positive이면:

```text
HS-JEPA should separate two readouts:
1. rhythm context as the temporal drift decoder,
2. rhythm-gated residual listener channels as subject/block readability adapters.
```

negative이면:

```text
Simple rhythm gating is not enough to solve chronological drift toxicity.
The next core target should predict future drift/action-health directly rather than
only gate residual readout by rhythm confidence.
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

    metrics.to_csv(OUT_DIR / "rhythm_conditioned_residual_listener_probe_metrics.csv", index=False)
    leakage.to_csv(OUT_DIR / "rhythm_conditioned_residual_listener_subject_leakage.csv", index=False)
    pretext.to_csv(OUT_DIR / "rhythm_conditioned_residual_listener_pretext_metrics.csv", index=False)
    router_weights_frame.to_csv(OUT_DIR / "rhythm_conditioned_residual_listener_weights.csv", index=False)
    (OUT_DIR / "rhythm_conditioned_residual_listener_summary.json").write_text(
        json.dumps(json_safe(summary), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    doc = build_markdown(summary, metrics, leakage, pretext, router_weights_frame)
    (OUT_DIR / "RHYTHM_CONDITIONED_RESIDUAL_LISTENER_CORE_KO.md").write_text(doc, encoding="utf-8")
    PAPER_DOC.write_text(doc, encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(json_safe(run()), ensure_ascii=False, indent=2))
