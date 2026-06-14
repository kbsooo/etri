#!/usr/bin/env python3
"""HS-JEPA multi-head listener-responsibility pretext experiment.

The invariant listener experiment showed a boundary: averaging current,
future, and cohort consistency can blur target-specific utility.  This
experiment keeps those consistency routes as separate heads:

    visible subject-relative context
      -> current listener responsibility head
      -> future-consistent listener responsibility head
      -> cohort-consistent listener responsibility head
      -> frozen listener reads the useful head geometry

Labels are used only after the multi-head representation is frozen.
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
from hsjepa_core.run_invariant_listener_responsibility_pretext_core import (  # noqa: E402
    cohort_consistency_teacher,
    learned_features_from_teacher,
    temporal_consistency_teacher,
)
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


OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "multi_head_listener_responsibility_pretext_core"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "MULTI_HEAD_LISTENER_RESPONSIBILITY_PRETEXT_CORE_KO.md"


HEADS = ["current", "future", "cohort"]
HEAD_PREFIX = {
    "current": "head_current_relative",
    "future": "head_future_relative",
    "cohort": "head_cohort_relative",
}
COMPACT_SUFFIXES = {
    "p0",
    "p1",
    "confidence_weighted",
    "entropy_weighted",
    "energy_weighted",
    "energy_lift_weighted",
    "responsibility_max",
    "responsibility_entropy",
}
DELTA_SUFFIXES = {
    "confidence_weighted",
    "energy_lift_weighted",
    "responsibility_max",
    "responsibility_entropy",
}


def target_teacher_heads(
    train_frame: pd.DataFrame,
    relative_context: pd.DataFrame,
    state: pd.DataFrame,
    views: dict[str, list[str]],
) -> dict[str, dict[str, np.ndarray]]:
    heads: dict[str, dict[str, np.ndarray]] = {head: {} for head in HEADS}
    for target in TARGETS:
        current = view_teacher_weights(state, views, SEMANTIC_TARGET_PROFILES[target])
        heads["current"][target] = current
        heads["future"][target] = temporal_consistency_teacher(train_frame, current)
        heads["cohort"][target] = cohort_consistency_teacher(train_frame, relative_context, current)
    return heads


def suffix_after_target(col: str, prefix: str, target: str) -> str:
    marker = f"{prefix}_{target}_"
    if marker not in col:
        return col
    return col.split(marker, 1)[1]


def build_delta_features(
    head_parts: dict[str, pd.DataFrame],
    head_cols: dict[str, dict[str, list[str]]],
) -> tuple[pd.DataFrame, dict[str, list[str]]]:
    index = next(iter(head_parts.values())).index
    data: dict[str, np.ndarray] = {}
    target_cols: dict[str, list[str]] = {}
    pairs = [
        ("future", "current"),
        ("cohort", "current"),
        ("future", "cohort"),
    ]
    for target in TARGETS:
        cols_for_target: list[str] = []
        suffix_maps: dict[str, dict[str, str]] = {}
        for head in HEADS:
            prefix = HEAD_PREFIX[head]
            suffix_maps[head] = {
                suffix_after_target(col, prefix, target): col
                for col in head_cols[head][target]
            }

        shared = [
            suffix
            for suffix in sorted(set.intersection(*(set(suffix_maps[head]) for head in HEADS)))
            if suffix in DELTA_SUFFIXES
        ]
        for suffix in shared:
            values = {
                head: np.nan_to_num(
                    head_parts[head][suffix_maps[head][suffix]].to_numpy(dtype=np.float64),
                    nan=0.0,
                    posinf=0.0,
                    neginf=0.0,
                )
                for head in HEADS
            }
            stacked = np.vstack([values[head] for head in HEADS])
            range_col = f"multihead_delta_{target}_{suffix}_head_range"
            data[range_col] = stacked.max(axis=0) - stacked.min(axis=0)
            cols_for_target.append(range_col)
            for left, right in pairs:
                diff_col = f"multihead_delta_{target}_{suffix}_{left}_minus_{right}"
                abs_col = f"multihead_delta_{target}_{suffix}_abs_{left}_minus_{right}"
                diff = values[left] - values[right]
                data[diff_col] = diff
                data[abs_col] = np.abs(diff)
                cols_for_target.extend([diff_col, abs_col])
        target_cols[target] = cols_for_target
    return pd.DataFrame(data, index=index), target_cols


def sanitize_features(features: pd.DataFrame) -> pd.DataFrame:
    numeric = features.apply(pd.to_numeric, errors="coerce")
    numeric = numeric.replace([np.inf, -np.inf], np.nan)
    return numeric.clip(lower=-1e6, upper=1e6).copy()


def combine_target_cols(
    pieces: list[dict[str, list[str]]],
) -> dict[str, list[str]]:
    return {
        target: sorted(set(col for piece in pieces for col in piece[target]))
        for target in TARGETS
    }


def compact_cols(cols: dict[str, list[str]], prefix: str) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for target in TARGETS:
        keep = []
        for col in cols[target]:
            suffix = suffix_after_target(col, prefix, target)
            if suffix in COMPACT_SUFFIXES:
                keep.append(col)
        out[target] = keep
    return out


def evaluate_split_package(
    split_name: str,
    train_frame: pd.DataFrame,
    relative_context: pd.DataFrame,
    raw_cols: list[str],
    views: dict[str, list[str]],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
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

    delta_features, delta_cols = build_delta_features(head_parts, head_cols)
    compact_head_cols = {
        head: compact_cols(head_cols[head], HEAD_PREFIX[head])
        for head in HEADS
    }
    features = pd.concat(
        [
            train_frame[raw_cols].reset_index(drop=True),
            state.reset_index(drop=True),
            direct_semantic.reset_index(drop=True),
            *(head_parts[head].reset_index(drop=True) for head in HEADS),
            delta_features.reset_index(drop=True),
        ],
        axis=1,
    )
    features = sanitize_features(features)

    global_cols = global_transport_cols(views)
    head_maps = {
        f"{HEAD_PREFIX[head]}_listener_responsibility": compact_head_cols[head]
        for head in HEADS
    }
    combo_maps = {
        "multihead_current_future_listener_responsibility": combine_target_cols(
            [compact_head_cols["current"], compact_head_cols["future"]]
        ),
        "multihead_current_cohort_listener_responsibility": combine_target_cols(
            [compact_head_cols["current"], compact_head_cols["cohort"]]
        ),
        "multihead_future_cohort_listener_responsibility": combine_target_cols(
            [compact_head_cols["future"], compact_head_cols["cohort"]]
        ),
        "multihead_current_future_cohort_listener_responsibility": combine_target_cols(
            [compact_head_cols["current"], compact_head_cols["future"], compact_head_cols["cohort"]]
        ),
        "multihead_delta_listener_responsibility": delta_cols,
    }
    feature_maps = {
        "prior_only": {target: [] for target in TARGETS},
        "raw_lifelog_pca": {target: raw_cols for target in TARGETS},
        "global_transported_prototype": {target: global_cols for target in TARGETS},
        "direct_semantic_listener_responsibility": direct_semantic_cols,
        **head_maps,
        **combo_maps,
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
        **{name: flatten_cols(cols) for name, cols in combo_maps.items()},
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

    single_sets = [
        f"{HEAD_PREFIX[head]}_listener_responsibility_calibrated10"
        for head in HEADS
    ]
    multi_sets = sorted(
        subject_all[
            subject_all["feature_set"].str.startswith("multihead_")
            & subject_all["feature_set"].str.endswith("_listener_responsibility_calibrated10")
        ]["feature_set"].tolist()
    )
    single_losses = {name: loss(subject_all, name) for name in single_sets}
    multi_losses = {name: loss(subject_all, name) for name in multi_sets}
    best_single_name = min(
        [name for name, value in single_losses.items() if value is not None],
        key=lambda name: single_losses[name],
    )
    best_multi_name = min(
        [name for name, value in multi_losses.items() if value is not None],
        key=lambda name: multi_losses[name],
    )
    best_single = single_losses[best_single_name]
    best_multi = multi_losses[best_multi_name]

    prior = loss(subject_all, "prior_only_calibrated10")
    raw = loss(subject_all, "raw_lifelog_pca_calibrated10")
    global_transport = loss(subject_all, "global_transported_prototype_calibrated10")
    direct_semantic = loss(subject_all, "direct_semantic_listener_responsibility_calibrated10")
    best_row = loss(row_all, best_multi_name)
    best_chrono = loss(chrono_all, best_multi_name)
    global_row = loss(row_all, "global_transported_prototype_calibrated10")
    global_chrono = loss(chrono_all, "global_transported_prototype_calibrated10")

    verdict = "multi_head_listener_responsibility_negative"
    if best_multi is not None and prior is not None and best_multi < prior:
        verdict = "multi_head_listener_responsibility_prior_positive"
        if best_single is not None and best_multi < best_single:
            verdict = "multi_head_listener_responsibility_beats_single_positive"
        if global_transport is not None and best_multi < global_transport:
            verdict = "multi_head_listener_responsibility_global_positive"

    pretext_rows = {row["feature_set"]: row.to_dict() for _, row in subject_pretext.iterrows()}
    return {
        "package": "multi_head_listener_responsibility_pretext_core",
        "status": "multi_head_listener_responsibility_pretext_core_ready",
        "verdict": verdict,
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "uses_label_as_pretext_target": False,
        "teacher": "separate_current_future_cohort_listener_responsibility_heads",
        "context_encoder": "subject_relative_visible_lifelog_context",
        "subject_prior_logloss": prior,
        "subject_raw_logloss": raw,
        "subject_global_transport_logloss": global_transport,
        "subject_direct_semantic_logloss": direct_semantic,
        "subject_best_single_head_feature_set": best_single_name,
        "subject_best_single_head_logloss": best_single,
        "subject_best_multi_head_feature_set": best_multi_name,
        "subject_best_multi_head_logloss": best_multi,
        "subject_best_multi_delta_vs_single": None if best_multi is None or best_single is None else best_multi - best_single,
        "subject_best_multi_delta_vs_prior": None if best_multi is None or prior is None else best_multi - prior,
        "subject_best_multi_delta_vs_raw": None if best_multi is None or raw is None else best_multi - raw,
        "subject_best_multi_delta_vs_global": None if best_multi is None or global_transport is None else best_multi - global_transport,
        "subject_best_multi_delta_vs_direct_semantic": None if best_multi is None or direct_semantic is None else best_multi - direct_semantic,
        "row_block_best_multi_delta_vs_global": None if best_row is None or global_row is None else best_row - global_row,
        "chronological_best_multi_delta_vs_global": None if best_chrono is None or global_chrono is None else best_chrono - global_chrono,
        "subject_pretext_all": pretext_rows,
        "subject_best_multi_leakage": leak(best_multi_name.replace("_calibrated10", "")),
        "subject_best_single_leakage": leak(best_single_name.replace("_calibrated10", "")),
        "global_transport_subject_leakage": leak("global_transported_prototype"),
        "raw_subject_leakage": leak("raw_lifelog_pca"),
    }


def build_markdown(summary: dict[str, Any], metrics: pd.DataFrame, leakage: pd.DataFrame, pretext: pd.DataFrame) -> str:
    subject_all = metrics[(metrics["split"].eq("subject_heldout")) & (metrics["target"].eq("all"))].sort_values("logloss")
    row_all = metrics[(metrics["split"].eq("row_block_holdout")) & (metrics["target"].eq("all"))].sort_values("logloss")
    chrono_all = metrics[(metrics["split"].eq("chronological_holdout")) & (metrics["target"].eq("all"))].sort_values("logloss")
    pretext_all = pretext[pretext["target"].eq("all")].sort_values(["split", "feature_set"])
    subject_leak = leakage[leakage["split"].eq("subject_heldout")].sort_values("subject_id_accuracy")
    return f"""# Multi-Head Listener Responsibility Pretext Core

## 한 줄 요약

이 실험은 current/future/cohort consistency를 하나의 teacher로 평균내지 않는다.
세 개의 hidden listener-responsibility head를 따로 예측하고,
frozen listener probe가 어떤 head geometry를 읽어야 하는지 검사한다.

```text
subject-relative visible human-life context
  -> current responsibility head
  -> future-consistent responsibility head
  -> cohort-consistent responsibility head
  -> frozen listener reads single/concat/delta head geometry
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

- best single-head feature set: `{summary["subject_best_single_head_feature_set"]}`
- best single-head logloss: `{format_float(summary["subject_best_single_head_logloss"], 6)}`
- best multi-head feature set: `{summary["subject_best_multi_head_feature_set"]}`
- best multi-head logloss: `{format_float(summary["subject_best_multi_head_logloss"], 6)}`
- subject global transport logloss: `{format_float(summary["subject_global_transport_logloss"], 6)}`
- subject direct semantic logloss: `{format_float(summary["subject_direct_semantic_logloss"], 6)}`
- subject prior logloss: `{format_float(summary["subject_prior_logloss"], 6)}`
- delta vs best single head: `{format_float(summary["subject_best_multi_delta_vs_single"], 6)}`
- delta vs prior: `{format_float(summary["subject_best_multi_delta_vs_prior"], 6)}`
- delta vs raw lifelog PCA: `{format_float(summary["subject_best_multi_delta_vs_raw"], 6)}`
- delta vs global transport: `{format_float(summary["subject_best_multi_delta_vs_global"], 6)}`
- delta vs direct semantic: `{format_float(summary["subject_best_multi_delta_vs_direct_semantic"], 6)}`
- row-block delta vs global: `{format_float(summary["row_block_best_multi_delta_vs_global"], 6)}`
- chronological delta vs global: `{format_float(summary["chronological_best_multi_delta_vs_global"], 6)}`

## Label-Free Pretext Quality

{markdown_table(pretext_all, ["split", "feature_set", "pretext_cross_entropy", "prior_cross_entropy", "ce_lift_vs_prior", "ce_lift_vs_uniform", "top1_match_rate"], max_rows=30)}

## Subject-Heldout Frozen Probe

{markdown_table(subject_all, ["feature_set", "logloss", "auc"], max_rows=24)}

## Row-Block Frozen Probe

{markdown_table(row_all, ["feature_set", "logloss", "auc"], max_rows=24)}

## Chronological Frozen Probe

{markdown_table(chrono_all, ["feature_set", "logloss", "auc"], max_rows=24)}

## Subject Leakage Diagnostic

{markdown_table(subject_leak, ["feature_set", "subject_id_accuracy", "chance_accuracy", "leakage_lift_vs_chance"], max_rows=16)}

## 해석

positive이면:

```text
HS-JEPA should preserve current/future/cohort responsibility as separate heads.
The useful human-state interface is not a smoothed invariant teacher but a
route-preserving multi-head representation.
```

negative이면:

```text
current/future/cohort separation is not enough; the missing component is not
head preservation but a stronger listener decoder or a better hidden teacher.
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

    metrics.to_csv(OUT_DIR / "multi_head_listener_responsibility_probe_metrics.csv", index=False)
    leakage.to_csv(OUT_DIR / "multi_head_listener_responsibility_subject_leakage.csv", index=False)
    pretext.to_csv(OUT_DIR / "multi_head_listener_responsibility_pretext_metrics.csv", index=False)
    (OUT_DIR / "multi_head_listener_responsibility_pretext_summary.json").write_text(
        json.dumps(json_safe(summary), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    doc = build_markdown(summary, metrics, leakage, pretext)
    (OUT_DIR / "MULTI_HEAD_LISTENER_RESPONSIBILITY_PRETEXT_CORE_KO.md").write_text(doc, encoding="utf-8")
    PAPER_DOC.write_text(doc, encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(json_safe(run()), ensure_ascii=False, indent=2))
