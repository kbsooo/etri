#!/usr/bin/env python3
"""HS-JEPA routine-break world-model core experiment.

This is a core-side experiment, not a leaderboard adapter.  It asks whether a
more human-centered hidden target helps:

    visible context -> hidden routine-break / episode-reset representation

The target is label-free.  It is built from subject-relative deviations,
within-subject transitions, and rolling personal-baseline residuals.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
import warnings
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.metrics import log_loss
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hsjepa_core.human_state_world_model import (  # noqa: E402
    SemanticView,
    WorldModelConfig,
    component_correlation,
    encode_latent,
    finite_frame,
    rank01,
    ridge_predict_oof,
    weighted_r2,
)
from hsjepa_core.run_human_state_world_model_core import (  # noqa: E402
    build_downstream_probe_submission,
    calibrated_probe_metrics,
    chronological_folds,
    evaluate_split,
    make_views,
    subject_folds,
    subject_leakage_probe,
    subject_relative_frame,
)
from hsjepa_core.run_lifelog_core_state_evidence import (  # noqa: E402
    TARGETS,
    catalog_features,
    format_float,
    load_frames,
    markdown_table,
)


OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "routine_break_world_model_core"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "ROUTINE_BREAK_WORLD_MODEL_CORE_KO.md"
RANDOM_SEED = 20260613
CONFIG = WorldModelConfig(
    latent_dims_per_view=4,
    future_state_dims=8,
    ridge_alpha=16.0,
    group_folds=5,
    cohort_count=4,
    random_state=RANDOM_SEED,
)

warnings.filterwarnings("ignore", message="Skipping features without any observed values")


def short_hash(frame: pd.DataFrame) -> str:
    arr = frame[TARGETS].to_numpy(dtype=np.float64)
    return hashlib.sha256(np.round(arr, 10).tobytes()).hexdigest()[:8]


def ordered_subject_indices(frame: pd.DataFrame) -> list[np.ndarray]:
    order_frame = frame[["subject_id", "lifelog_date"]].copy()
    order_frame["_row"] = np.arange(len(frame))
    order_frame["lifelog_date"] = pd.to_datetime(order_frame["lifelog_date"], errors="coerce")
    groups = []
    for _, part in order_frame.sort_values(["subject_id", "lifelog_date", "_row"]).groupby("subject_id", observed=True):
        groups.append(part["_row"].to_numpy(dtype=int))
    return groups


def rolling_baseline(values: np.ndarray, window: int = 3) -> tuple[np.ndarray, np.ndarray]:
    previous = np.zeros_like(values, dtype=np.float64)
    baseline = np.zeros_like(values, dtype=np.float64)
    for idx in range(len(values)):
        if idx > 0:
            previous[idx] = values[idx - 1]
            start = max(0, idx - window)
            baseline[idx] = np.nanmean(values[start:idx], axis=0)
        else:
            previous[idx] = 0.0
            baseline[idx] = 0.0
    previous = np.nan_to_num(previous, nan=0.0, posinf=0.0, neginf=0.0)
    baseline = np.nan_to_num(baseline, nan=0.0, posinf=0.0, neginf=0.0)
    return previous, baseline


def build_routine_descriptors(
    frame: pd.DataFrame,
    views: list[SemanticView],
    raw_cols: list[str],
) -> tuple[pd.DataFrame, dict[str, list[str]]]:
    relative = subject_relative_frame(frame, raw_cols)
    rel_values = finite_frame(relative, raw_cols).fillna(0.0).to_numpy(dtype=np.float64)
    rel_values = np.nan_to_num(rel_values, nan=0.0, posinf=0.0, neginf=0.0)
    previous = np.zeros_like(rel_values, dtype=np.float64)
    baseline = np.zeros_like(rel_values, dtype=np.float64)

    for indices in ordered_subject_indices(frame):
        prev_sub, base_sub = rolling_baseline(rel_values[indices], window=3)
        previous[indices] = prev_sub
        baseline[indices] = base_sub

    delta = rel_values - previous
    residual = rel_values - baseline
    abs_residual = np.abs(residual)
    abs_delta = np.abs(delta)

    col_pos = {col: idx for idx, col in enumerate(raw_cols)}
    descriptor_data: dict[str, np.ndarray] = {}
    view_descriptor_cols: dict[str, list[str]] = {}
    for view in views:
        positions = [col_pos[col] for col in view.columns if col in col_pos]
        if len(positions) < 2:
            continue
        cols: list[str] = []
        arrays = {
            "relative": rel_values[:, positions],
            "delta": delta[:, positions],
            "residual": residual[:, positions],
            "abs_delta": abs_delta[:, positions],
            "abs_residual": abs_residual[:, positions],
        }
        for family, arr in arrays.items():
            for offset, source_col in enumerate([raw_cols[pos] for pos in positions]):
                col = f"rb_{view.name}_{family}_{source_col}"
                descriptor_data[col] = arr[:, offset]
                cols.append(col)
        descriptor_data[f"rb_intensity_{view.name}"] = np.sqrt(np.nanmean(np.square(residual[:, positions]), axis=1))
        descriptor_data[f"rb_jump_{view.name}"] = np.sqrt(np.nanmean(np.square(delta[:, positions]), axis=1))
        descriptor_data[f"rb_abs_state_{view.name}"] = np.sqrt(np.nanmean(np.square(rel_values[:, positions]), axis=1))
        cols.extend([f"rb_intensity_{view.name}", f"rb_jump_{view.name}", f"rb_abs_state_{view.name}"])
        view_descriptor_cols[view.name] = cols

    descriptor = pd.DataFrame(descriptor_data, index=frame.index)
    descriptor["rb_intensity_mean"] = descriptor[[c for c in descriptor.columns if c.startswith("rb_intensity_")]].mean(axis=1)
    descriptor["rb_jump_mean"] = descriptor[[c for c in descriptor.columns if c.startswith("rb_jump_")]].mean(axis=1)
    descriptor["rb_abs_state_mean"] = descriptor[[c for c in descriptor.columns if c.startswith("rb_abs_state_")]].mean(axis=1)
    return descriptor, view_descriptor_cols


def json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [json_safe(item) for item in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        if not math.isfinite(float(value)):
            return None
        return float(value)
    return value


def masked_routine_break_state(
    frame: pd.DataFrame,
    relative_frame: pd.DataFrame,
    views: list[SemanticView],
    raw_cols: list[str],
    descriptors: pd.DataFrame,
    view_descriptor_cols: dict[str, list[str]],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    state = pd.DataFrame(index=frame.index)
    metrics: list[dict[str, Any]] = []
    groups = frame["subject_id"].astype(str).to_numpy()
    all_context_cols = raw_cols

    for view in views:
        target_cols = view_descriptor_cols.get(view.name, [])
        context_cols = [col for col in all_context_cols if col not in set(view.columns)]
        if len(target_cols) < 4 or len(context_cols) < 2:
            continue
        target_state, _ = encode_latent(
            descriptors,
            target_cols,
            CONFIG.latent_dims_per_view,
            RANDOM_SEED,
        )
        pred, null_pred = ridge_predict_oof(
            relative_frame,
            context_cols,
            target_state,
            groups,
            CONFIG,
        )
        residual = target_state - pred
        energy = np.sqrt(np.mean(np.square(residual), axis=1))
        for comp in range(target_state.shape[1]):
            state[f"rbwm_pred_{view.name}_c{comp + 1}"] = pred[:, comp]
            state[f"rbwm_resid_{view.name}_c{comp + 1}"] = residual[:, comp]
        state[f"rbwm_energy_{view.name}"] = energy
        state[f"rbwm_energy_rank_{view.name}"] = rank01(energy)
        state[f"rbwm_observed_intensity_{view.name}"] = descriptors[f"rb_intensity_{view.name}"].to_numpy(dtype=np.float64)
        state[f"rbwm_observed_jump_{view.name}"] = descriptors[f"rb_jump_{view.name}"].to_numpy(dtype=np.float64)

        metrics.append(
            {
                "task": "masked_context_to_routine_break_view",
                "target": view.name,
                "components": int(target_state.shape[1]),
                "context_feature_count": len(context_cols),
                "target_feature_count": len(target_cols),
                "component_corr": component_correlation(target_state, pred),
                "null_component_corr": component_correlation(target_state, null_pred),
                "component_corr_lift_vs_null": component_correlation(target_state, pred)
                - component_correlation(target_state, null_pred),
                "r2": weighted_r2(target_state, pred),
                "null_r2": weighted_r2(target_state, null_pred),
                "r2_lift_vs_null": weighted_r2(target_state, pred) - weighted_r2(target_state, null_pred),
            }
        )
    return state, pd.DataFrame(metrics)


def future_routine_break_state(
    frame: pd.DataFrame,
    relative_frame: pd.DataFrame,
    raw_cols: list[str],
    descriptors: pd.DataFrame,
    view_descriptor_cols: dict[str, list[str]],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    all_descriptor_cols = sorted({col for cols in view_descriptor_cols.values() for col in cols})
    global_state, _ = encode_latent(descriptors, all_descriptor_cols, CONFIG.future_state_dims, RANDOM_SEED)
    ordered = frame[["subject_id", "lifelog_date"]].copy()
    ordered["_row"] = np.arange(len(frame))
    ordered["lifelog_date"] = pd.to_datetime(ordered["lifelog_date"], errors="coerce")
    ordered = ordered.sort_values(["subject_id", "lifelog_date", "_row"])
    ordered["_next_row"] = ordered.groupby("subject_id", observed=True)["_row"].shift(-1)
    next_row = ordered.set_index("_row")["_next_row"].reindex(np.arange(len(frame))).to_numpy()
    valid = np.isfinite(next_row)
    valid_indices = np.where(valid)[0]

    state = pd.DataFrame(index=frame.index)
    if valid.sum() < 8 or len(np.unique(frame.loc[valid, "subject_id"])) < 2:
        return state, pd.DataFrame()

    target_state = global_state[next_row[valid].astype(int)]
    pred_valid, null_valid = ridge_predict_oof(
        relative_frame.iloc[valid_indices].reset_index(drop=True),
        raw_cols,
        target_state,
        frame.loc[valid, "subject_id"].astype(str).to_numpy(),
        CONFIG,
    )
    pred = np.full((len(frame), target_state.shape[1]), np.nan, dtype=np.float64)
    residual = np.full_like(pred, np.nan)
    pred[valid_indices] = pred_valid
    residual[valid_indices] = target_state - pred_valid
    energy = np.full(len(frame), np.nan, dtype=np.float64)
    energy[valid_indices] = np.sqrt(np.mean(np.square(residual[valid_indices]), axis=1))
    for comp in range(target_state.shape[1]):
        state[f"rbwm_future_pred_c{comp + 1}"] = pred[:, comp]
        state[f"rbwm_future_resid_c{comp + 1}"] = residual[:, comp]
    state["rbwm_future_energy"] = energy
    state["rbwm_future_energy_rank"] = rank01(energy)
    metrics = pd.DataFrame(
        [
            {
                "task": "current_context_to_next_routine_break",
                "target": "next_episode_routine_break",
                "components": int(target_state.shape[1]),
                "context_feature_count": len(raw_cols),
                "target_feature_count": len(all_descriptor_cols),
                "component_corr": component_correlation(target_state, pred_valid),
                "null_component_corr": component_correlation(target_state, null_valid),
                "component_corr_lift_vs_null": component_correlation(target_state, pred_valid)
                - component_correlation(target_state, null_valid),
                "r2": weighted_r2(target_state, pred_valid),
                "null_r2": weighted_r2(target_state, null_valid),
                "r2_lift_vs_null": weighted_r2(target_state, pred_valid) - weighted_r2(target_state, null_valid),
                "valid_rows": int(valid.sum()),
            }
        ]
    )
    return state, metrics


def build_routine_break_world_state(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, list[str]]]:
    views = make_views(frame)
    raw_cols = sorted({col for view in views for col in view.columns})
    relative_frame = subject_relative_frame(frame, raw_cols)
    descriptors, view_descriptor_cols = build_routine_descriptors(frame, views, raw_cols)
    masked_state, masked_metrics = masked_routine_break_state(
        frame,
        relative_frame,
        views,
        raw_cols,
        descriptors,
        view_descriptor_cols,
    )
    future_state, future_metrics = future_routine_break_state(
        frame,
        relative_frame,
        raw_cols,
        descriptors,
        view_descriptor_cols,
    )
    state = pd.concat([masked_state, future_state], axis=1)
    energy_cols = [c for c in state.columns if "energy" in c and "_rank" not in c]
    rank_cols = [c for c in state.columns if "energy_rank" in c]
    pred_cols = [c for c in state.columns if c.startswith("rbwm_pred_") or c.startswith("rbwm_future_pred_")]
    resid_cols = [c for c in state.columns if c.startswith("rbwm_resid_") or c.startswith("rbwm_future_resid_")]
    observed_cols = [c for c in state.columns if c.startswith("rbwm_observed_")]
    state["rbwm_energy_mean"] = state[energy_cols].mean(axis=1)
    state["rbwm_energy_max"] = state[energy_cols].max(axis=1)
    state["rbwm_energy_rank_mean"] = state[rank_cols].mean(axis=1)
    state["rbwm_energy_rank_max"] = state[rank_cols].max(axis=1)
    state["rbwm_observed_intensity_mean"] = state[[c for c in observed_cols if "intensity" in c]].mean(axis=1)
    state["rbwm_observed_jump_mean"] = state[[c for c in observed_cols if "jump" in c]].mean(axis=1)
    metrics = pd.concat([masked_metrics, future_metrics], ignore_index=True, sort=False)
    colsets = {
        "routine_break_predicted": pred_cols,
        "routine_break_energy": energy_cols + rank_cols + [
            "rbwm_energy_mean",
            "rbwm_energy_max",
            "rbwm_energy_rank_mean",
            "rbwm_energy_rank_max",
        ],
        "routine_break_observed": observed_cols + ["rbwm_observed_intensity_mean", "rbwm_observed_jump_mean"],
        "routine_break_full": sorted(set(pred_cols + resid_cols + observed_cols + list(state.columns))),
    }
    return state, metrics, colsets


def neighbor_consistency(
    train_frame: pd.DataFrame,
    features: pd.DataFrame,
    feature_sets: dict[str, list[str]],
) -> pd.DataFrame:
    labels = train_frame[TARGETS].astype(int).to_numpy()
    rng = np.random.default_rng(RANDOM_SEED)
    rows: list[dict[str, Any]] = []
    for feature_set, cols in feature_sets.items():
        if not cols:
            continue
        x = SimpleImputer(strategy="median").fit_transform(finite_frame(features, cols))
        x = StandardScaler().fit_transform(x)
        if x.shape[1] > 24:
            x = PCA(n_components=min(24, x.shape[0] - 1, x.shape[1]), random_state=RANDOM_SEED).fit_transform(x)
        nn = NearestNeighbors(n_neighbors=min(6, len(features)), metric="euclidean")
        nn.fit(x)
        _, idx = nn.kneighbors(x)
        idx = idx[:, 1:]
        near = []
        rnd = []
        for row in range(len(features)):
            near.append((labels[idx[row]] == labels[row]).mean(axis=0))
            pool = [item for item in range(len(features)) if item != row]
            random_idx = rng.choice(pool, size=idx.shape[1], replace=False)
            rnd.append((labels[random_idx] == labels[row]).mean(axis=0))
        near_arr = np.vstack(near)
        rnd_arr = np.vstack(rnd)
        for target_idx, target in enumerate(TARGETS):
            rows.append(
                {
                    "feature_set": feature_set,
                    "target": target,
                    "neighbor_match_rate": float(near_arr[:, target_idx].mean()),
                    "random_match_rate": float(rnd_arr[:, target_idx].mean()),
                    "lift": float(near_arr[:, target_idx].mean() - rnd_arr[:, target_idx].mean()),
                }
            )
        rows.append(
            {
                "feature_set": feature_set,
                "target": "all",
                "neighbor_match_rate": float(near_arr.mean()),
                "random_match_rate": float(rnd_arr.mean()),
                "lift": float(near_arr.mean() - rnd_arr.mean()),
            }
        )
    return pd.DataFrame(rows)


def summarize(
    pretext_metrics: pd.DataFrame,
    probe_metrics: pd.DataFrame,
    nn_metrics: pd.DataFrame,
    leakage: pd.DataFrame,
    candidate_file: str,
) -> dict[str, Any]:
    pretext = pretext_metrics.sort_values("component_corr_lift_vs_null", ascending=False)
    subject_all = probe_metrics[(probe_metrics["split"].eq("subject_heldout")) & (probe_metrics["target"].eq("all"))]
    chrono_all = probe_metrics[(probe_metrics["split"].eq("chronological_holdout")) & (probe_metrics["target"].eq("all"))]
    prior = subject_all[subject_all["feature_set"].eq("prior_only")]
    routine = subject_all[subject_all["feature_set"].eq("routine_break_predicted_calibrated10")]
    routine_full = subject_all[subject_all["feature_set"].eq("routine_break_full_calibrated10")]
    best_subject = subject_all.sort_values("logloss").head(1)
    nn_all = nn_metrics[nn_metrics["target"].eq("all")].sort_values("lift", ascending=False)
    return {
        "package": "routine_break_world_model_core",
        "status": "routine_break_world_model_core_ready",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "uses_label_as_pretext_target": False,
        "hidden_target": "subject_relative_routine_break_and_next_episode_reset",
        "best_pretext": None if pretext.empty else pretext.iloc[0].to_dict(),
        "subject_prior_logloss": None if prior.empty else float(prior["logloss"].iloc[0]),
        "routine_predicted_calibrated_logloss": None if routine.empty else float(routine["logloss"].iloc[0]),
        "routine_full_calibrated_logloss": None if routine_full.empty else float(routine_full["logloss"].iloc[0]),
        "routine_predicted_delta_vs_prior": None
        if prior.empty or routine.empty
        else float(routine["logloss"].iloc[0] - prior["logloss"].iloc[0]),
        "routine_full_delta_vs_prior": None
        if prior.empty or routine_full.empty
        else float(routine_full["logloss"].iloc[0] - prior["logloss"].iloc[0]),
        "subject_best_probe": None if best_subject.empty else best_subject.iloc[0].to_dict(),
        "chronological_best_probe": None if chrono_all.empty else chrono_all.sort_values("logloss").iloc[0].to_dict(),
        "best_neighbor_consistency": None if nn_all.empty else nn_all.iloc[0].to_dict(),
        "subject_leakage": leakage.to_dict(orient="records"),
        "candidate_file": candidate_file,
    }


def build_markdown(
    summary: dict[str, Any],
    pretext_metrics: pd.DataFrame,
    probe_metrics: pd.DataFrame,
    nn_metrics: pd.DataFrame,
    leakage: pd.DataFrame,
    candidate_file: str,
) -> str:
    best_pretext = summary.get("best_pretext") or {}
    verdict = "core_positive" if (summary.get("routine_predicted_delta_vs_prior") or 1.0) < 0 else "core_mixed_or_negative"
    subject_all = (
        probe_metrics[(probe_metrics["split"].eq("subject_heldout")) & (probe_metrics["target"].eq("all"))]
        .sort_values("logloss")
        .loc[:, ["feature_set", "logloss", "auc"]]
    )
    chrono_all = (
        probe_metrics[(probe_metrics["split"].eq("chronological_holdout")) & (probe_metrics["target"].eq("all"))]
        .sort_values("logloss")
        .loc[:, ["feature_set", "logloss", "auc"]]
    )
    return f"""# Routine-Break World Model Core

## 한 줄 요약

HS-JEPA의 hidden target을 단순 masked-view state에서 한 단계 바꾸어,
사람의 루틴 붕괴와 episode reset을 label 없이 예측하는 world model로 만든 실험이다.

```text
visible human-life context
  -> subject-relative deviation / transition / personal-baseline residual
  -> hidden routine-break representation
  -> frozen low-trust Q/S probe
```

## 판정

- verdict: `{verdict}`
- public LB ledger 사용: `{summary["uses_public_score_ledger"]}`
- prior submission probability 사용: `{summary["uses_prior_submission_probabilities"]}`
- proprietary embedding API 사용: `{summary["uses_proprietary_embedding_api"]}`
- label을 pretext target으로 사용: `{summary["uses_label_as_pretext_target"]}`

## 왜 이것이 HS-JEPA Core인가

이 실험은 Q/S label이나 public LB를 target으로 삼지 않는다.
target은 다음 세 가지로 만든 hidden human-state representation이다.

1. subject-relative current state
2. previous episode에서 현재 episode로 넘어온 jump
3. 개인 rolling baseline에서 벗어난 routine-break residual

따라서 이 실험의 질문은 다음이다.

```text
보이는 생활 context만으로
보이지 않는 루틴 붕괴/episode reset 표현을 예측할 수 있는가?
```

## Pretext 결과

- best pretext task: `{best_pretext.get("task", "NA")}`
- best target: `{best_pretext.get("target", "NA")}`
- best component-corr lift vs null: `{format_float(best_pretext.get("component_corr_lift_vs_null"), 6)}`
- best R2 lift vs null: `{format_float(best_pretext.get("r2_lift_vs_null"), 6)}`

{markdown_table(
    pretext_metrics.sort_values("component_corr_lift_vs_null", ascending=False).head(12),
    ["task", "target", "component_corr", "null_component_corr", "component_corr_lift_vs_null", "r2_lift_vs_null"],
)}

## Frozen Subject-Heldout Probe

`_calibrated10`은 fold prior에서 10%만 움직이는 fixed low-trust probe다.

{markdown_table(subject_all, ["feature_set", "logloss", "auc"])}

## Chronological Row-Heldout Probe

{markdown_table(chrono_all, ["feature_set", "logloss", "auc"])}

## Nearest-Neighbor State Consistency

{markdown_table(
    nn_metrics[nn_metrics["target"].eq("all")].sort_values("lift", ascending=False),
    ["feature_set", "neighbor_match_rate", "random_match_rate", "lift"],
)}

## Subject Leakage Diagnostic

{markdown_table(
    leakage.sort_values("subject_id_accuracy", ascending=False),
    ["feature_set", "subject_id_accuracy", "chance_accuracy", "leakage_lift_vs_chance"],
)}

## Downstream Probe Candidate

- file: `{candidate_file}`

이 파일은 HS-JEPA core 증거가 아니라 downstream probe candidate다.

## 해석

positive이면:

```text
루틴 붕괴/episode reset은 HS-JEPA core target으로 적합하며,
subject-relative world model보다 더 강한 label-free human-state representation이다.
```

negative이면:

```text
루틴 붕괴 target은 예측 가능하더라도 Q/S label manifold로 잘 번역되지 않는다.
다음 core target은 sleep-stage-like hidden factor 쪽으로 옮겨야 한다.
```
"""


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frame, labels = load_frames()
    views = make_views(frame)
    raw_cols = sorted({col for view in views for col in view.columns})
    state, pretext_metrics, colsets = build_routine_break_world_state(frame)
    state = pd.concat(
        [frame[["subject_id", "sleep_date", "lifelog_date", "split", "metric_row"]].reset_index(drop=True), state.reset_index(drop=True)],
        axis=1,
    )
    catalog = catalog_features(frame)
    combined = pd.concat(
        [frame.reset_index(drop=True), state.drop(columns=["subject_id", "sleep_date", "lifelog_date", "split", "metric_row"])],
        axis=1,
    )
    feature_sets = {
        "prior_only": [],
        "raw_lifelog_pca": raw_cols,
        "existing_cohort_human_state": catalog.core_state,
        "routine_break_predicted": colsets["routine_break_predicted"],
        "routine_break_energy": colsets["routine_break_energy"],
        "routine_break_observed": colsets["routine_break_observed"],
        "routine_break_full": colsets["routine_break_full"],
        "raw_plus_routine_break_full": sorted(set(raw_cols + colsets["routine_break_full"])),
    }

    train_mask = frame["split"].eq("train").to_numpy()
    train_frame = frame.loc[train_mask].reset_index(drop=True)
    train_features = combined.loc[train_mask].reset_index(drop=True)
    subject_metrics, subject_predictions = evaluate_split(
        train_frame,
        train_features,
        feature_sets,
        "subject_heldout",
        subject_folds(train_frame),
    )
    chrono_metrics, chrono_predictions = evaluate_split(
        train_frame,
        train_features,
        feature_sets,
        "chronological_holdout",
        chronological_folds(train_frame),
    )
    probe_metrics = pd.concat([subject_metrics, chrono_metrics], ignore_index=True)
    probe_predictions = pd.concat([subject_predictions, chrono_predictions], ignore_index=True)
    probe_metrics = pd.concat([probe_metrics, calibrated_probe_metrics(probe_predictions)], ignore_index=True, sort=False)
    nn_metrics = neighbor_consistency(train_frame, train_features, feature_sets)
    leakage = subject_leakage_probe(
        train_frame,
        train_features,
        {key: value for key, value in feature_sets.items() if key not in {"prior_only", "raw_plus_routine_break_full"}},
    )

    test_mask = frame["split"].eq("test").to_numpy()
    test_frame = frame.loc[test_mask].reset_index(drop=True)
    test_features = combined.loc[test_mask].reset_index(drop=True)
    submission = build_downstream_probe_submission(
        train_frame,
        test_frame,
        train_features,
        test_features,
        colsets["routine_break_predicted"],
    )
    candidate_name = f"submission_hsjepa_routine_break_world_model_probe_{short_hash(submission)}_uploadsafe.csv"
    candidate_path = ROOT / candidate_name
    submission.to_csv(candidate_path, index=False)
    submission.to_csv(OUT_DIR / candidate_name, index=False)

    summary = json_safe(summarize(pretext_metrics, probe_metrics, nn_metrics, leakage, candidate_name))
    state.to_csv(OUT_DIR / "routine_break_world_model_state.csv", index=False)
    pretext_metrics.to_csv(OUT_DIR / "routine_break_world_model_pretext_metrics.csv", index=False)
    probe_metrics.to_csv(OUT_DIR / "routine_break_world_model_probe_metrics.csv", index=False)
    probe_predictions.to_csv(OUT_DIR / "routine_break_world_model_probe_predictions.csv", index=False)
    nn_metrics.to_csv(OUT_DIR / "routine_break_world_model_neighbor_consistency.csv", index=False)
    leakage.to_csv(OUT_DIR / "routine_break_world_model_subject_leakage.csv", index=False)
    (OUT_DIR / "routine_break_world_model_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, allow_nan=False),
        encoding="utf-8",
    )
    markdown = build_markdown(summary, pretext_metrics, probe_metrics, nn_metrics, leakage, candidate_name)
    (OUT_DIR / "ROUTINE_BREAK_WORLD_MODEL_CORE_KO.md").write_text(markdown, encoding="utf-8")
    PAPER_DOC.write_text(markdown, encoding="utf-8")
    print(
        json.dumps(
            {
                "status": summary["status"],
                "candidate_file": candidate_name,
                "routine_predicted_delta_vs_prior": summary["routine_predicted_delta_vs_prior"],
                "routine_full_delta_vs_prior": summary["routine_full_delta_vs_prior"],
                "best_pretext_lift": None
                if summary["best_pretext"] is None
                else summary["best_pretext"]["component_corr_lift_vs_null"],
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
