#!/usr/bin/env python3
"""HS-JEPA cohort-relative world-model core experiment.

This is a public-free core experiment.  It turns the cohort idea into an
HS-JEPA hidden target rather than a competition adapter:

    visible daily context -> hidden personal-vs-peer human-state representation

The target is label-free.  It is derived from routine-break and sleep-pressure
states, subject fingerprints, and cohort-relative outlier geometry.
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
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hsjepa_core.human_state_world_model import (  # noqa: E402
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
from hsjepa_core.run_routine_break_world_model_core import (  # noqa: E402
    build_routine_descriptors,
)
from hsjepa_core.run_sleep_pressure_world_model_core import (  # noqa: E402
    build_sleep_pressure_descriptors,
    json_safe,
    sleep_pressure_families,
)


OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "cohort_relative_world_model_core"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "COHORT_RELATIVE_WORLD_MODEL_CORE_KO.md"
RANDOM_SEED = 20260613
CONFIG = WorldModelConfig(
    latent_dims_per_view=6,
    future_state_dims=8,
    ridge_alpha=14.0,
    group_folds=5,
    cohort_count=4,
    random_state=RANDOM_SEED,
)

warnings.filterwarnings("ignore", message="Skipping features without any observed values")


def short_hash(frame: pd.DataFrame) -> str:
    arr = frame[TARGETS].to_numpy(dtype=np.float64)
    return hashlib.sha256(np.round(arr, 10).tobytes()).hexdigest()[:8]


def build_base_human_state(
    frame: pd.DataFrame,
    raw_cols: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, list[str]]]:
    views = make_views(frame)
    sleep_families = sleep_pressure_families(raw_cols)
    sleep_families = {key: value for key, value in sleep_families.items() if len(value) >= 2}
    sleep_desc, sleep_cols = build_sleep_pressure_descriptors(frame, raw_cols, sleep_families)
    routine_desc, routine_cols = build_routine_descriptors(frame, views, raw_cols)

    combined = pd.concat(
        [
            sleep_desc.add_prefix("sleep__"),
            routine_desc.add_prefix("routine__"),
        ],
        axis=1,
    )
    descriptor_cols = list(combined.columns)
    latent, _ = encode_latent(combined, descriptor_cols, 14, RANDOM_SEED)
    basis = pd.DataFrame(
        latent,
        index=frame.index,
        columns=[f"base_human_state_c{idx + 1}" for idx in range(latent.shape[1])],
    )
    scalar_cols = [
        col
        for col in combined.columns
        if col.endswith("_mean")
        or "_intensity_" in col
        or "_jump_" in col
        or "_recovery_debt_" in col
    ]
    if scalar_cols:
        scalar_latent, _ = encode_latent(combined, scalar_cols, min(8, len(scalar_cols)), RANDOM_SEED)
        for idx in range(scalar_latent.shape[1]):
            basis[f"base_scalar_state_c{idx + 1}"] = scalar_latent[:, idx]
    source_cols = {
        "base_human_state": list(basis.columns),
        "sleep_pressure_descriptor": [f"sleep__{col}" for col in sleep_desc.columns],
        "routine_break_descriptor": [f"routine__{col}" for col in routine_desc.columns],
    }
    return basis, combined, source_cols


def assign_subject_cohorts(frame: pd.DataFrame, basis: pd.DataFrame) -> tuple[pd.Series, pd.DataFrame]:
    subject_ids = frame["subject_id"].astype(str)
    grouped = basis.groupby(subject_ids, observed=True)
    fingerprint = pd.concat(
        [
            grouped.mean().add_suffix("_mean"),
            grouped.std().fillna(0.0).add_suffix("_std"),
            grouped.size().rename("row_count"),
        ],
        axis=1,
    )
    x = make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(),
    ).fit_transform(fingerprint)
    best_labels: np.ndarray | None = None
    for n_clusters in range(max(2, min(CONFIG.cohort_count, len(fingerprint))), 1, -1):
        labels = KMeans(n_clusters=n_clusters, n_init=50, random_state=RANDOM_SEED).fit_predict(x)
        counts = pd.Series(labels).value_counts()
        if int(counts.min()) >= 2:
            best_labels = labels
            break
    if best_labels is None:
        best_labels = KMeans(n_clusters=2, n_init=50, random_state=RANDOM_SEED).fit_predict(x)
    cohorts = best_labels
    fingerprint = fingerprint.copy()
    fingerprint["cohort_id"] = cohorts
    cohort_map = fingerprint["cohort_id"].astype(int).to_dict()
    return subject_ids.map(cohort_map).astype(int), fingerprint


def cohort_excluding_subject_centers(
    subject_centers: dict[str, np.ndarray],
    subject_cohorts: dict[str, int],
) -> dict[str, np.ndarray]:
    subjects = sorted(subject_centers)
    global_center = np.mean(np.vstack([subject_centers[sub] for sub in subjects]), axis=0)
    centers: dict[str, np.ndarray] = {}
    for subject in subjects:
        cohort = subject_cohorts[subject]
        peers = [sub for sub in subjects if sub != subject and subject_cohorts[sub] == cohort]
        if not peers:
            peers = [sub for sub in subjects if sub != subject]
        centers[subject] = np.mean(np.vstack([subject_centers[sub] for sub in peers]), axis=0) if peers else global_center
    return centers


def build_cohort_relative_state(frame: pd.DataFrame, basis: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    cohort_ids, fingerprint = assign_subject_cohorts(frame, basis)
    subjects = frame["subject_id"].astype(str)
    values = basis.to_numpy(dtype=np.float64)
    basis_cols = list(basis.columns)

    subject_centers = {
        subject: basis.loc[subjects.eq(subject)].mean(axis=0).to_numpy(dtype=np.float64)
        for subject in sorted(subjects.unique())
    }
    subject_cohorts = {
        subject: int(cohort_ids.loc[subjects.eq(subject)].iloc[0])
        for subject in sorted(subjects.unique())
    }
    cohort_centers = cohort_excluding_subject_centers(subject_centers, subject_cohorts)
    global_center = np.mean(np.vstack(list(subject_centers.values())), axis=0)

    subject_center = np.vstack([subject_centers[sub] for sub in subjects])
    cohort_center = np.vstack([cohort_centers[sub] for sub in subjects])
    global_center_rows = np.tile(global_center, (len(frame), 1))
    subject_resid = values - subject_center
    cohort_resid = values - cohort_center
    subject_to_cohort = subject_center - cohort_center
    global_resid = values - global_center_rows

    state_data: dict[str, np.ndarray] = {}
    for idx, col in enumerate(basis_cols):
        state_data[f"crwm_subject_resid_{col}"] = subject_resid[:, idx]
        state_data[f"crwm_cohort_resid_{col}"] = cohort_resid[:, idx]
        state_data[f"crwm_subject_to_cohort_{col}"] = subject_to_cohort[:, idx]
        state_data[f"crwm_global_resid_{col}"] = global_resid[:, idx]

    state = pd.DataFrame(state_data, index=frame.index)
    state["crwm_cohort_id"] = cohort_ids.to_numpy(dtype=np.float64)
    state["crwm_subject_distance"] = np.sqrt(np.mean(np.square(subject_resid), axis=1))
    state["crwm_cohort_distance"] = np.sqrt(np.mean(np.square(cohort_resid), axis=1))
    state["crwm_global_distance"] = np.sqrt(np.mean(np.square(global_resid), axis=1))
    state["crwm_subject_to_cohort_distance"] = np.sqrt(np.mean(np.square(subject_to_cohort), axis=1))
    state["crwm_cohort_minus_subject_distance"] = state["crwm_cohort_distance"] - state["crwm_subject_distance"]
    state["crwm_subject_distance_rank"] = (
        state["crwm_subject_distance"].groupby(subjects, observed=True).rank(method="average", pct=True).fillna(0.5)
    )
    state["crwm_cohort_distance_rank"] = (
        state["crwm_cohort_distance"].groupby(cohort_ids, observed=True).rank(method="average", pct=True).fillna(0.5)
    )
    state["crwm_global_distance_rank"] = rank01(state["crwm_global_distance"].to_numpy(dtype=np.float64))
    state["crwm_peer_outlier_score"] = (
        0.45 * state["crwm_cohort_distance_rank"]
        + 0.35 * rank01(state["crwm_cohort_minus_subject_distance"].to_numpy(dtype=np.float64))
        + 0.20 * rank01(state["crwm_subject_to_cohort_distance"].to_numpy(dtype=np.float64))
    )

    fingerprint_out = fingerprint.reset_index(names="subject_id")
    return state, fingerprint_out


def predict_cohort_state(
    frame: pd.DataFrame,
    relative_frame: pd.DataFrame,
    raw_cols: list[str],
    cohort_state: pd.DataFrame,
    family_cols: dict[str, list[str]],
) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    state_data: dict[str, np.ndarray] = {}
    groups = frame["subject_id"].astype(str).to_numpy()
    target_cols = [col for col in cohort_state.columns if col.startswith("crwm_")]
    target_latent, _ = encode_latent(cohort_state, target_cols, CONFIG.future_state_dims, RANDOM_SEED)
    metric_rows: list[dict[str, Any]] = []

    contexts = {"all_visible_context": raw_cols}
    for family, cols in family_cols.items():
        contexts[f"masked_without_{family}"] = [col for col in raw_cols if col not in set(cols)]

    predicted_cols: list[str] = []
    for context_name, context_cols in contexts.items():
        if len(context_cols) < 2:
            continue
        pred, null_pred = ridge_predict_oof(relative_frame, context_cols, target_latent, groups, CONFIG)
        residual = target_latent - pred
        energy = np.sqrt(np.mean(np.square(residual), axis=1))
        safe_name = context_name.replace("masked_without_", "mask_")
        for comp in range(target_latent.shape[1]):
            pred_col = f"crwm_pred_{safe_name}_c{comp + 1}"
            state_data[pred_col] = pred[:, comp]
            state_data[f"crwm_resid_{safe_name}_c{comp + 1}"] = residual[:, comp]
            predicted_cols.append(pred_col)
        state_data[f"crwm_energy_{safe_name}"] = energy
        state_data[f"crwm_energy_rank_{safe_name}"] = rank01(energy)
        metric_rows.append(
            {
                "task": "visible_context_to_cohort_relative_state",
                "target": "personal_vs_peer_state",
                "context": context_name,
                "components": int(target_latent.shape[1]),
                "context_feature_count": len(context_cols),
                "target_feature_count": len(target_cols),
                "component_corr": component_correlation(target_latent, pred),
                "null_component_corr": component_correlation(target_latent, null_pred),
                "component_corr_lift_vs_null": component_correlation(target_latent, pred)
                - component_correlation(target_latent, null_pred),
                "r2": weighted_r2(target_latent, pred),
                "null_r2": weighted_r2(target_latent, null_pred),
                "r2_lift_vs_null": weighted_r2(target_latent, pred) - weighted_r2(target_latent, null_pred),
            }
        )

    state = pd.DataFrame(state_data, index=frame.index)
    return state, pd.DataFrame(metric_rows), predicted_cols


def future_cohort_state(
    frame: pd.DataFrame,
    relative_frame: pd.DataFrame,
    raw_cols: list[str],
    cohort_state: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    target_cols = [col for col in cohort_state.columns if col.startswith("crwm_")]
    target_latent, _ = encode_latent(cohort_state, target_cols, CONFIG.future_state_dims, RANDOM_SEED)
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

    next_target = target_latent[next_row[valid].astype(int)]
    pred_valid, null_valid = ridge_predict_oof(
        relative_frame.iloc[valid_indices].reset_index(drop=True),
        raw_cols,
        next_target,
        frame.loc[valid, "subject_id"].astype(str).to_numpy(),
        CONFIG,
    )
    pred = np.full((len(frame), next_target.shape[1]), np.nan, dtype=np.float64)
    residual = np.full_like(pred, np.nan)
    pred[valid_indices] = pred_valid
    residual[valid_indices] = next_target - pred_valid
    energy = np.full(len(frame), np.nan, dtype=np.float64)
    energy[valid_indices] = np.sqrt(np.mean(np.square(residual[valid_indices]), axis=1))
    for comp in range(next_target.shape[1]):
        state[f"crwm_future_pred_c{comp + 1}"] = pred[:, comp]
        state[f"crwm_future_resid_c{comp + 1}"] = residual[:, comp]
    state["crwm_future_energy"] = energy
    state["crwm_future_energy_rank"] = rank01(energy)
    metrics = pd.DataFrame(
        [
            {
                "task": "current_context_to_next_cohort_relative_state",
                "target": "next_personal_vs_peer_state",
                "context": "all_visible_context",
                "components": int(next_target.shape[1]),
                "context_feature_count": len(raw_cols),
                "target_feature_count": len(target_cols),
                "component_corr": component_correlation(next_target, pred_valid),
                "null_component_corr": component_correlation(next_target, null_valid),
                "component_corr_lift_vs_null": component_correlation(next_target, pred_valid)
                - component_correlation(next_target, null_valid),
                "r2": weighted_r2(next_target, pred_valid),
                "null_r2": weighted_r2(next_target, null_valid),
                "r2_lift_vs_null": weighted_r2(next_target, pred_valid) - weighted_r2(next_target, null_valid),
                "valid_rows": int(valid.sum()),
            }
        ]
    )
    return state, metrics


def build_cohort_relative_world_state(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, list[str]]]:
    views = make_views(frame)
    raw_cols = sorted({col for view in views for col in view.columns})
    family_cols = {view.name: list(view.columns) for view in views}
    basis, descriptor_frame, source_cols = build_base_human_state(frame, raw_cols)
    cohort_observed, subject_fingerprint = build_cohort_relative_state(frame, basis)
    relative_frame = subject_relative_frame(frame, raw_cols)
    predicted, prediction_metrics, predicted_cols = predict_cohort_state(
        frame,
        relative_frame,
        raw_cols,
        cohort_observed,
        family_cols,
    )
    future, future_metrics = future_cohort_state(frame, relative_frame, raw_cols, cohort_observed)
    state = pd.concat([cohort_observed, predicted, future], axis=1)
    energy_cols = [c for c in state.columns if "energy" in c and "_rank" not in c]
    rank_cols = [c for c in state.columns if "energy_rank" in c]
    observed_cols = [c for c in cohort_observed.columns if c.startswith("crwm_")]
    resid_cols = [c for c in state.columns if c.startswith("crwm_resid_") or c.startswith("crwm_future_resid_")]
    future_pred_cols = [c for c in state.columns if c.startswith("crwm_future_pred_")]
    state["crwm_energy_mean"] = state[energy_cols].mean(axis=1)
    state["crwm_energy_max"] = state[energy_cols].max(axis=1)
    state["crwm_energy_rank_mean"] = state[rank_cols].mean(axis=1)
    state["crwm_energy_rank_max"] = state[rank_cols].max(axis=1)
    metrics = pd.concat([prediction_metrics, future_metrics], ignore_index=True, sort=False)
    colsets = {
        "cohort_relative_predicted": sorted(set(predicted_cols + future_pred_cols)),
        "cohort_relative_energy": energy_cols
        + rank_cols
        + ["crwm_energy_mean", "crwm_energy_max", "crwm_energy_rank_mean", "crwm_energy_rank_max"],
        "cohort_relative_observed": observed_cols,
        "cohort_relative_full": sorted(set(list(state.columns))),
        "base_descriptor": list(descriptor_frame.columns),
        "base_source": sorted(set(source_cols["base_human_state"])),
    }
    return state, metrics, subject_fingerprint, colsets


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
    subject_fingerprint: pd.DataFrame,
    candidate_file: str,
) -> dict[str, Any]:
    pretext = pretext_metrics.sort_values("component_corr_lift_vs_null", ascending=False)
    subject_all = probe_metrics[(probe_metrics["split"].eq("subject_heldout")) & (probe_metrics["target"].eq("all"))]
    chrono_all = probe_metrics[(probe_metrics["split"].eq("chronological_holdout")) & (probe_metrics["target"].eq("all"))]
    prior = subject_all[subject_all["feature_set"].eq("prior_only")]
    predicted = subject_all[subject_all["feature_set"].eq("cohort_relative_predicted_calibrated10")]
    full = subject_all[subject_all["feature_set"].eq("cohort_relative_full_calibrated10")]
    best_subject = subject_all.sort_values("logloss").head(1)
    nn_all = nn_metrics[nn_metrics["target"].eq("all")].sort_values("lift", ascending=False)
    cohort_sizes = subject_fingerprint["cohort_id"].value_counts().sort_index().to_dict()
    return {
        "package": "cohort_relative_world_model_core",
        "status": "cohort_relative_world_model_core_ready",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "uses_label_as_pretext_target": False,
        "hidden_target": "personal_vs_peer_cohort_relative_state",
        "cohort_count": int(subject_fingerprint["cohort_id"].nunique()),
        "cohort_sizes": {str(key): int(value) for key, value in cohort_sizes.items()},
        "best_pretext": None if pretext.empty else pretext.iloc[0].to_dict(),
        "subject_prior_logloss": None if prior.empty else float(prior["logloss"].iloc[0]),
        "cohort_relative_predicted_calibrated_logloss": None
        if predicted.empty
        else float(predicted["logloss"].iloc[0]),
        "cohort_relative_full_calibrated_logloss": None if full.empty else float(full["logloss"].iloc[0]),
        "cohort_relative_predicted_delta_vs_prior": None
        if prior.empty or predicted.empty
        else float(predicted["logloss"].iloc[0] - prior["logloss"].iloc[0]),
        "cohort_relative_full_delta_vs_prior": None
        if prior.empty or full.empty
        else float(full["logloss"].iloc[0] - prior["logloss"].iloc[0]),
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
    pred_delta = summary.get("cohort_relative_predicted_delta_vs_prior")
    full_delta = summary.get("cohort_relative_full_delta_vs_prior")
    verdict = "core_positive" if (pred_delta is not None and pred_delta < 0) or (full_delta is not None and full_delta < 0) else "core_mixed_or_negative"
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
    return f"""# Cohort-Relative World Model Core

## 한 줄 요약

HS-JEPA의 hidden target을 `개인의 평소`와 `비슷한 peer cohort의 평소` 사이의 좌표계로 만든 실험이다.

```text
visible daily human-life context
  -> hidden personal-vs-peer cohort-relative representation
  -> frozen low-trust Q/S probe
```

## 판정

- verdict: `{verdict}`
- public LB ledger 사용: `{summary["uses_public_score_ledger"]}`
- prior submission probability 사용: `{summary["uses_prior_submission_probabilities"]}`
- proprietary embedding API 사용: `{summary["uses_proprietary_embedding_api"]}`
- label을 pretext target으로 사용: `{summary["uses_label_as_pretext_target"]}`
- cohort count: `{summary["cohort_count"]}`
- cohort sizes: `{summary["cohort_sizes"]}`
- cohort selection: singleton cohort를 허용하지 않는 가장 큰 K를 선택한다.

## 왜 이것이 HS-JEPA Core인가

이 실험은 Q/S label이나 public LB를 target으로 삼지 않는다.
target은 다음 label-free geometry다.

1. 오늘이 이 사람의 평소에서 얼마나 벗어났는가
2. 오늘이 비슷한 peer cohort의 평소에서 얼마나 벗어났는가
3. 이 사람 자체가 자기 cohort 안에서 얼마나 특이한가
4. 이 row가 개인 기준 outlier인지, peer 기준 outlier인지

즉 질문은 다음이다.

```text
보이는 생활 context만으로
개인-대-peer human-state 좌표계에서 오늘의 위치를 예측할 수 있는가?
```

## Pretext 결과

- best pretext task: `{best_pretext.get("task", "NA")}`
- best context: `{best_pretext.get("context", "NA")}`
- best component-corr lift vs null: `{format_float(best_pretext.get("component_corr_lift_vs_null"), 6)}`
- best R2 lift vs null: `{format_float(best_pretext.get("r2_lift_vs_null"), 6)}`

{markdown_table(
    pretext_metrics.sort_values("component_corr_lift_vs_null", ascending=False).head(12),
    ["task", "context", "component_corr", "null_component_corr", "component_corr_lift_vs_null", "r2_lift_vs_null"],
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

이 파일은 HS-JEPA core 증거를 public에서 관측하기 위한 downstream probe candidate다.

## 해석

positive이면:

```text
cohort-relative human-state는 HS-JEPA core target으로 적합하다.
개인 내부 비교와 peer cohort 비교를 동시에 쓰면 label-free representation이 더 유용해진다.
```

주의:

```text
observed/full cohort geometry는 subject identity를 강하게 담는다.
따라서 core evidence는 observed state가 아니라 subject-heldout OOF predicted state에 둔다.
```

negative이면:

```text
cohort-relative geometry는 subject identity 또는 cohort shortcut을 담을 수 있지만,
Q/S label manifold로 안전하게 번역되지 않는다.
cohort는 core target보다 diagnostic/adapter로 남겨야 한다.
```
"""


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frame, labels = load_frames()
    views = make_views(frame)
    raw_cols = sorted({col for view in views for col in view.columns})
    state, pretext_metrics, subject_fingerprint, colsets = build_cohort_relative_world_state(frame)
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
        "cohort_relative_predicted": colsets["cohort_relative_predicted"],
        "cohort_relative_energy": colsets["cohort_relative_energy"],
        "cohort_relative_observed": colsets["cohort_relative_observed"],
        "cohort_relative_full": colsets["cohort_relative_full"],
        "raw_plus_cohort_relative_full": sorted(set(raw_cols + colsets["cohort_relative_full"])),
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
        {key: value for key, value in feature_sets.items() if key not in {"prior_only", "raw_plus_cohort_relative_full"}},
    )

    test_mask = frame["split"].eq("test").to_numpy()
    test_frame = frame.loc[test_mask].reset_index(drop=True)
    test_features = combined.loc[test_mask].reset_index(drop=True)
    submission = build_downstream_probe_submission(
        train_frame,
        test_frame,
        train_features,
        test_features,
        colsets["cohort_relative_predicted"],
    )
    candidate_name = f"submission_hsjepa_cohort_relative_world_model_probe_{short_hash(submission)}_uploadsafe.csv"
    candidate_path = ROOT / candidate_name
    submission.to_csv(candidate_path, index=False)
    submission.to_csv(OUT_DIR / candidate_name, index=False)

    summary = json_safe(summarize(pretext_metrics, probe_metrics, nn_metrics, leakage, subject_fingerprint, candidate_name))
    state.to_csv(OUT_DIR / "cohort_relative_world_model_state.csv", index=False)
    subject_fingerprint.to_csv(OUT_DIR / "cohort_relative_subject_fingerprint.csv", index=False)
    pretext_metrics.to_csv(OUT_DIR / "cohort_relative_world_model_pretext_metrics.csv", index=False)
    probe_metrics.to_csv(OUT_DIR / "cohort_relative_world_model_probe_metrics.csv", index=False)
    probe_predictions.to_csv(OUT_DIR / "cohort_relative_world_model_probe_predictions.csv", index=False)
    nn_metrics.to_csv(OUT_DIR / "cohort_relative_world_model_neighbor_consistency.csv", index=False)
    leakage.to_csv(OUT_DIR / "cohort_relative_world_model_subject_leakage.csv", index=False)
    (OUT_DIR / "cohort_relative_world_model_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, allow_nan=False),
        encoding="utf-8",
    )
    markdown = build_markdown(summary, pretext_metrics, probe_metrics, nn_metrics, leakage, candidate_name)
    (OUT_DIR / "COHORT_RELATIVE_WORLD_MODEL_CORE_KO.md").write_text(markdown, encoding="utf-8")
    PAPER_DOC.write_text(markdown, encoding="utf-8")
    print(
        json.dumps(
            {
                "status": summary["status"],
                "candidate_file": candidate_name,
                "cohort_relative_predicted_delta_vs_prior": summary["cohort_relative_predicted_delta_vs_prior"],
                "cohort_relative_full_delta_vs_prior": summary["cohort_relative_full_delta_vs_prior"],
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
