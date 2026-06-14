#!/usr/bin/env python3
"""HS-JEPA global-transport residual listener-router core experiment.

The learned listener-head router improved over fixed semantic routing, but did
not replace the global transported prototype grammar under subject-heldout
stress.  This experiment tests the next architecture question:

    Is listener-head routing a replacement for the transported grammar,
    or a residual interface on top of it?

The core contract stays public-free:

    subject-relative visible human-life context
      -> cross-subject transported prototype grammar
      -> label-free hidden listener-head suitability prediction
      -> residual listener-router interface
      -> frozen downstream probe

Labels are used only after the representations are frozen.
"""

from __future__ import annotations

import json
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
from hsjepa_core.run_listener_head_router_pretext_core import build_routed_features  # noqa: E402
from hsjepa_core.run_multi_head_listener_responsibility_pretext_core import (  # noqa: E402
    HEADS,
    HEAD_PREFIX,
    combine_target_cols,
    compact_cols,
    sanitize_features,
    target_teacher_heads,
)


OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "global_transport_residual_listener_router_core"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "GLOBAL_TRANSPORT_RESIDUAL_LISTENER_ROUTER_CORE_KO.md"

BEST_LEARNED_ROUTER_NAME = "learned_semantic_router_context_headsignal"
BEST_LEARNED_TEACHER_MODE = "state_suitability_semantic"
BEST_LEARNED_DESIGN_MODE = "context_headsignal"
BEST_LEARNED_PREDICTION_BLEND = 0.45
BEST_LEARNED_SEMANTIC_BLEND = 0.0


def suffix_after_prefix(col: str, prefix: str, target: str) -> str:
    marker = f"{prefix}_{target}_"
    if marker not in col:
        return col
    return col.split(marker, 1)[1]


def existing_target_cols(features: pd.DataFrame, cols: dict[str, list[str]]) -> dict[str, list[str]]:
    available = set(features.columns)
    return {
        target: sorted(set(col for col in cols[target] if col in available))
        for target in TARGETS
    }


def add_global(
    global_cols: list[str],
    target_cols: dict[str, list[str]],
) -> dict[str, list[str]]:
    return {
        target: sorted(set(global_cols + target_cols[target]))
        for target in TARGETS
    }


def router_weight_cols(cols: dict[str, list[str]]) -> dict[str, list[str]]:
    return {
        target: [
            col
            for col in cols[target]
            if "_router_w_" in col or col.endswith("_router_entropy") or col.endswith("_router_margin")
        ]
        for target in TARGETS
    }


def build_router_delta_features(
    learned: pd.DataFrame,
    learned_cols: dict[str, list[str]],
    fixed: pd.DataFrame,
    fixed_cols: dict[str, list[str]],
    learned_prefix: str,
    fixed_prefix: str,
    out_prefix: str,
) -> tuple[pd.DataFrame, dict[str, list[str]]]:
    data: dict[str, np.ndarray] = {}
    target_cols: dict[str, list[str]] = {}
    for target in TARGETS:
        learned_map = {
            suffix_after_prefix(col, learned_prefix, target): col
            for col in learned_cols[target]
        }
        fixed_map = {
            suffix_after_prefix(col, fixed_prefix, target): col
            for col in fixed_cols[target]
        }
        shared = sorted(set(learned_map).intersection(fixed_map))
        cols_for_target: list[str] = []
        for suffix in shared:
            lval = np.nan_to_num(
                learned[learned_map[suffix]].to_numpy(dtype=np.float64),
                nan=0.0,
                posinf=0.0,
                neginf=0.0,
            )
            fval = np.nan_to_num(
                fixed[fixed_map[suffix]].to_numpy(dtype=np.float64),
                nan=0.0,
                posinf=0.0,
                neginf=0.0,
            )
            delta = lval - fval
            col = f"{out_prefix}_{target}_{suffix}_learned_minus_semantic"
            abs_col = f"{out_prefix}_{target}_{suffix}_abs_learned_minus_semantic"
            data[col] = delta
            data[abs_col] = np.abs(delta)
            cols_for_target.extend([col, abs_col])
        target_cols[target] = cols_for_target
    return pd.DataFrame(data, index=learned.index), target_cols


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

    features = pd.concat(
        [
            train_frame[raw_cols].reset_index(drop=True),
            state.reset_index(drop=True),
            direct_semantic.reset_index(drop=True),
            *(head_parts[head].reset_index(drop=True) for head in HEADS),
            fixed_semantic.reset_index(drop=True),
            learned_router.reset_index(drop=True),
            router_delta.reset_index(drop=True),
        ],
        axis=1,
    )
    features = sanitize_features(features)
    global_cols = sorted(set(col for col in global_transport_cols(views) if col in features.columns))
    learned_router_cols = existing_target_cols(features, learned_router_cols)
    fixed_semantic_cols = existing_target_cols(features, fixed_semantic_cols)
    direct_semantic_cols = existing_target_cols(features, direct_semantic_cols)
    router_delta_cols = existing_target_cols(features, router_delta_cols)
    compact_head_cols = {
        head: existing_target_cols(features, compact_head_cols[head])
        for head in HEADS
    }
    learned_weight_cols = router_weight_cols(learned_router_cols)

    feature_maps = {
        "prior_only": {target: [] for target in TARGETS},
        "raw_lifelog_pca": {target: raw_cols for target in TARGETS},
        "global_transported_prototype": {target: global_cols for target in TARGETS},
        "future_listener_head": compact_head_cols["future"],
        "semantic_prior_router": fixed_semantic_cols,
        "learned_listener_head_router": learned_router_cols,
        "learned_router_weight_signal": learned_weight_cols,
        "learned_router_delta_signal": router_delta_cols,
        "global_plus_future_listener_head": add_global(global_cols, compact_head_cols["future"]),
        "global_plus_semantic_prior_router": add_global(global_cols, fixed_semantic_cols),
        "global_plus_learned_listener_head_router": add_global(global_cols, learned_router_cols),
        "global_plus_learned_router_weight_signal": add_global(global_cols, learned_weight_cols),
        "global_plus_learned_router_delta_signal": add_global(global_cols, router_delta_cols),
        "global_plus_learned_router_full_residual": add_global(
            global_cols,
            combine_target_cols([learned_router_cols, router_delta_cols]),
        ),
        "global_plus_semantic_and_learned_router": add_global(
            global_cols,
            combine_target_cols([fixed_semantic_cols, learned_router_cols, router_delta_cols]),
        ),
        "direct_semantic_listener": direct_semantic_cols,
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
        "future_listener_head": flatten_cols(compact_head_cols["future"]),
        "semantic_prior_router": flatten_cols(fixed_semantic_cols),
        "learned_listener_head_router": flatten_cols(learned_router_cols),
        "learned_router_weight_signal": flatten_cols(learned_weight_cols),
        "learned_router_delta_signal": flatten_cols(router_delta_cols),
        "global_plus_learned_listener_head_router": sorted(
            set(global_cols + flatten_cols(learned_router_cols))
        ),
        "global_plus_learned_router_delta_signal": sorted(
            set(global_cols + flatten_cols(router_delta_cols))
        ),
        "global_plus_learned_router_full_residual": sorted(
            set(global_cols + flatten_cols(learned_router_cols) + flatten_cols(router_delta_cols))
        ),
        "global_plus_semantic_and_learned_router": sorted(
            set(
                global_cols
                + flatten_cols(fixed_semantic_cols)
                + flatten_cols(learned_router_cols)
                + flatten_cols(router_delta_cols)
            )
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


def summarize(
    metrics: pd.DataFrame,
    leakage: pd.DataFrame,
    pretext: pd.DataFrame,
    router_weights_frame: pd.DataFrame,
) -> dict[str, Any]:
    subject_all = metrics[(metrics["split"].eq("subject_heldout")) & (metrics["target"].eq("all"))]
    row_all = metrics[(metrics["split"].eq("row_block_holdout")) & (metrics["target"].eq("all"))]
    chrono_all = metrics[(metrics["split"].eq("chronological_holdout")) & (metrics["target"].eq("all"))]

    def loss(frame: pd.DataFrame, feature_set: str) -> float | None:
        part = frame[frame["feature_set"].eq(feature_set)]
        return None if part.empty else float(part["logloss"].iloc[0])

    def leak(feature_set: str) -> dict[str, Any] | None:
        part = leakage[leakage["split"].eq("subject_heldout") & leakage["feature_set"].eq(feature_set)]
        return None if part.empty else part.iloc[0].to_dict()

    calibrated_suffix = "_calibrated10"
    prior = loss(subject_all, f"prior_only{calibrated_suffix}")
    raw = loss(subject_all, f"raw_lifelog_pca{calibrated_suffix}")
    global_transport = loss(subject_all, f"global_transported_prototype{calibrated_suffix}")
    semantic_prior = loss(subject_all, f"semantic_prior_router{calibrated_suffix}")
    learned_router = loss(subject_all, f"learned_listener_head_router{calibrated_suffix}")
    future_head = loss(subject_all, f"future_listener_head{calibrated_suffix}")

    residual_sets = sorted(
        name
        for name in subject_all["feature_set"].tolist()
        if name.startswith("global_plus_") and name.endswith(calibrated_suffix)
    )
    learned_residual_sets = [name for name in residual_sets if "learned" in name]
    best_residual_name = min(
        residual_sets,
        key=lambda name: loss(subject_all, name) if loss(subject_all, name) is not None else np.inf,
    )
    best_learned_residual_name = min(
        learned_residual_sets,
        key=lambda name: loss(subject_all, name) if loss(subject_all, name) is not None else np.inf,
    )
    best_residual = loss(subject_all, best_residual_name)
    best_learned_residual = loss(subject_all, best_learned_residual_name)
    best_row = loss(row_all, best_learned_residual_name)
    best_chrono = loss(chrono_all, best_learned_residual_name)
    global_row = loss(row_all, f"global_transported_prototype{calibrated_suffix}")
    global_chrono = loss(chrono_all, f"global_transported_prototype{calibrated_suffix}")

    verdict = "global_transport_residual_listener_router_negative"
    if best_learned_residual is not None and global_transport is not None and best_learned_residual < global_transport:
        verdict = "global_transport_residual_listener_router_positive"
    elif best_residual is not None and global_transport is not None and best_residual < global_transport:
        verdict = "residual_interface_positive_but_not_learned_router"
    elif learned_router is not None and semantic_prior is not None and learned_router < semantic_prior:
        verdict = "learned_router_positive_but_not_residual"

    subject_pretext = pretext[(pretext["split"].eq("subject_heldout")) & (pretext["target"].eq("all"))]
    return {
        "package": "global_transport_residual_listener_router_core",
        "status": "global_transport_residual_listener_router_core_ready",
        "verdict": verdict,
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "uses_label_as_pretext_target": False,
        "architecture_question": "listener_router_replacement_vs_global_transport_residual_interface",
        "context_encoder": "subject_relative_visible_lifelog_context_plus_transported_prototype_grammar",
        "residual_interface": "learned_label_free_listener_head_router_on_global_transport_backbone",
        "subject_prior_logloss": prior,
        "subject_raw_logloss": raw,
        "subject_global_transport_logloss": global_transport,
        "subject_future_head_logloss": future_head,
        "subject_semantic_prior_router_logloss": semantic_prior,
        "subject_learned_router_logloss": learned_router,
        "subject_best_residual_feature_set": best_residual_name,
        "subject_best_residual_logloss": best_residual,
        "subject_best_learned_residual_feature_set": best_learned_residual_name,
        "subject_best_learned_residual_logloss": best_learned_residual,
        "subject_best_residual_delta_vs_global": None
        if best_residual is None or global_transport is None
        else best_residual - global_transport,
        "subject_best_learned_residual_delta_vs_global": None
        if best_learned_residual is None or global_transport is None
        else best_learned_residual - global_transport,
        "subject_best_learned_residual_delta_vs_learned_alone": None
        if best_learned_residual is None or learned_router is None
        else best_learned_residual - learned_router,
        "subject_best_learned_residual_delta_vs_semantic_prior": None
        if best_learned_residual is None or semantic_prior is None
        else best_learned_residual - semantic_prior,
        "row_block_best_learned_residual_delta_vs_global": None
        if best_row is None or global_row is None
        else best_row - global_row,
        "chronological_best_learned_residual_delta_vs_global": None
        if best_chrono is None or global_chrono is None
        else best_chrono - global_chrono,
        "subject_pretext_all": {row["feature_set"]: row.to_dict() for _, row in subject_pretext.iterrows()},
        "subject_router_weights": {
            f"{row['router']}::{row['target']}": row.to_dict()
            for _, row in router_weights_frame[router_weights_frame["split"].eq("subject_heldout")].iterrows()
        },
        "subject_best_learned_residual_leakage": leak(
            best_learned_residual_name.replace(calibrated_suffix, "")
        ),
        "global_transport_subject_leakage": leak("global_transported_prototype"),
        "learned_router_subject_leakage": leak("learned_listener_head_router"),
        "learned_delta_subject_leakage": leak("learned_router_delta_signal"),
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
        metrics["split"].eq("subject_heldout")
        & metrics["target"].isin(TARGETS)
        & metrics["feature_set"].eq(summary["subject_best_learned_residual_feature_set"])
    ].sort_values("target")
    pretext_all = pretext[pretext["target"].eq("all")].sort_values(["split", "feature_set"])
    subject_leak = leakage[leakage["split"].eq("subject_heldout")].sort_values("subject_id_accuracy")
    subject_weights = router_weights_frame[router_weights_frame["split"].eq("subject_heldout")].sort_values(
        ["router", "target"]
    )
    return f"""# Global Transport Residual Listener-Router Core

## 한 줄 요약

이 실험은 learned listener-head router가 global transported prototype grammar를
대체해야 하는지, 아니면 그 위에 붙는 residual listener interface여야 하는지 검증한다.

```text
subject-relative visible human-life context
  -> cross-subject transported prototype grammar
  -> label-free hidden listener-head suitability prediction
  -> learned residual listener-router interface
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

- global transport logloss: `{format_float(summary["subject_global_transport_logloss"], 6)}`
- learned router alone logloss: `{format_float(summary["subject_learned_router_logloss"], 6)}`
- semantic-prior router alone logloss: `{format_float(summary["subject_semantic_prior_router_logloss"], 6)}`
- best residual feature set: `{summary["subject_best_residual_feature_set"]}`
- best residual logloss: `{format_float(summary["subject_best_residual_logloss"], 6)}`
- best residual delta vs global: `{format_float(summary["subject_best_residual_delta_vs_global"], 6)}`
- best learned residual feature set: `{summary["subject_best_learned_residual_feature_set"]}`
- best learned residual logloss: `{format_float(summary["subject_best_learned_residual_logloss"], 6)}`
- best learned residual delta vs global: `{format_float(summary["subject_best_learned_residual_delta_vs_global"], 6)}`
- best learned residual delta vs learned alone: `{format_float(summary["subject_best_learned_residual_delta_vs_learned_alone"], 6)}`
- row-block best learned residual delta vs global: `{format_float(summary["row_block_best_learned_residual_delta_vs_global"], 6)}`
- chronological best learned residual delta vs global: `{format_float(summary["chronological_best_learned_residual_delta_vs_global"], 6)}`

## Subject-Heldout Frozen Probe

{markdown_table(subject_all, ["feature_set", "logloss", "auc"], max_rows=32)}

## Best Learned Residual Target Breakdown

{markdown_table(target_rows, ["target", "logloss", "auc"], max_rows=12)}

## Row-Block Frozen Probe

{markdown_table(row_all, ["feature_set", "logloss", "auc"], max_rows=32)}

## Chronological Frozen Probe

{markdown_table(chrono_all, ["feature_set", "logloss", "auc"], max_rows=32)}

## Label-Free Pretext Quality

{markdown_table(pretext_all, ["split", "feature_set", "pretext_cross_entropy", "prior_cross_entropy", "semantic_cross_entropy", "ce_lift_vs_prior", "ce_lift_vs_semantic", "top1_match_rate"], max_rows=36)}

## Router Weight Summary

{markdown_table(subject_weights, ["router", "target", "mean_w_current", "mean_w_future", "mean_w_cohort", "mean_entropy", "mean_margin"], max_rows=56)}

## Subject Leakage Diagnostic

{markdown_table(subject_leak, ["feature_set", "subject_id_accuracy", "chance_accuracy", "leakage_lift_vs_chance"], max_rows=16)}

## 해석

positive이면 논문 문장은 다음처럼 정리한다.

```text
HS-JEPA should not expose one monolithic human-state vector.
It first transports a subject-invariant episode grammar and then learns a
listener-specific residual interface that decides how each target should read it.
```

negative이면 죽는 믿음은 이것이다.

```text
Current learned listener-head routing contains additional subject-heldout
information beyond global transported prototype grammar.
```

그 경우 learned router는 아직 replacement도 residual interface도 아니며,
다음 core는 residual을 붙이는 방식보다 hidden action-health/release gate를
별도 target representation으로 만들어야 한다.
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

    metrics.to_csv(OUT_DIR / "global_transport_residual_listener_router_probe_metrics.csv", index=False)
    leakage.to_csv(OUT_DIR / "global_transport_residual_listener_router_subject_leakage.csv", index=False)
    pretext.to_csv(OUT_DIR / "global_transport_residual_listener_router_pretext_metrics.csv", index=False)
    router_weights_frame.to_csv(OUT_DIR / "global_transport_residual_listener_router_weights.csv", index=False)
    (OUT_DIR / "global_transport_residual_listener_router_summary.json").write_text(
        json.dumps(json_safe(summary), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    doc = build_markdown(summary, metrics, leakage, pretext, router_weights_frame)
    (OUT_DIR / "GLOBAL_TRANSPORT_RESIDUAL_LISTENER_ROUTER_CORE_KO.md").write_text(doc, encoding="utf-8")
    PAPER_DOC.write_text(doc, encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(json_safe(run()), ensure_ascii=False, indent=2))
