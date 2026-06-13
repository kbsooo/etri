#!/usr/bin/env python3
"""Reusable HS-JEPA human-state world-model core.

This module is intentionally independent of the sleep competition schema.  It
implements the core JEPA contract:

    visible context views -> predicted hidden target-view representation

The target is not a label and not a submission correction.  It is a latent
state of another semantic view or future human-state episode.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


@dataclass(frozen=True)
class SemanticView:
    """Named feature family used as context or hidden target."""

    name: str
    columns: tuple[str, ...]


@dataclass(frozen=True)
class WorldModelConfig:
    """HS-JEPA world-model hyperparameters."""

    latent_dims_per_view: int = 4
    future_state_dims: int = 8
    ridge_alpha: float = 18.0
    group_folds: int = 5
    cohort_count: int = 4
    random_state: int = 20260613


@dataclass(frozen=True)
class PretextMetric:
    """One masked/future prediction metric row."""

    task: str
    target: str
    components: int
    context_feature_count: int
    target_feature_count: int
    component_corr: float
    null_component_corr: float
    component_corr_lift_vs_null: float
    r2: float
    null_r2: float
    r2_lift_vs_null: float


def finite_frame(frame: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    return frame[list(columns)].replace([np.inf, -np.inf], np.nan)


def rank01(values: np.ndarray) -> np.ndarray:
    series = pd.Series(values, dtype="float64")
    if series.notna().sum() <= 1:
        return np.zeros(len(series), dtype=np.float64)
    return series.rank(method="average", pct=True).fillna(0.5).to_numpy(dtype=np.float64)


def component_correlation(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    values: list[float] = []
    for idx in range(y_true.shape[1]):
        a = y_true[:, idx]
        b = y_pred[:, idx]
        if np.std(a) <= 1e-12 or np.std(b) <= 1e-12:
            continue
        values.append(float(np.corrcoef(a, b)[0, 1]))
    return float(np.nanmean(values)) if values else float("nan")


def weighted_r2(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    residual = np.sum(np.square(y_true - y_pred), axis=0)
    centered = np.sum(np.square(y_true - np.mean(y_true, axis=0, keepdims=True)), axis=0)
    valid = centered > 1e-12
    if not np.any(valid):
        return float("nan")
    weights = centered[valid] / centered[valid].sum()
    return float(np.sum(weights * (1.0 - residual[valid] / centered[valid])))


def encode_latent(
    frame: pd.DataFrame,
    columns: list[str],
    dims: int,
    random_state: int,
) -> tuple[np.ndarray, make_pipeline]:
    n_components = max(1, min(dims, len(columns), len(frame) - 1))
    encoder = make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(),
        PCA(n_components=n_components, random_state=random_state),
    )
    latent = encoder.fit_transform(finite_frame(frame, columns))
    return np.asarray(latent, dtype=np.float64), encoder


def transform_latent(frame: pd.DataFrame, columns: list[str], encoder: make_pipeline) -> np.ndarray:
    return np.asarray(encoder.transform(finite_frame(frame, columns)), dtype=np.float64)


def ridge_predict_oof(
    frame: pd.DataFrame,
    context_columns: list[str],
    target_state: np.ndarray,
    groups: np.ndarray,
    config: WorldModelConfig,
) -> tuple[np.ndarray, np.ndarray]:
    """Predict latent target state with subject/group-heldout OOF splits."""

    n_splits = max(2, min(config.group_folds, len(np.unique(groups))))
    splitter = GroupKFold(n_splits=n_splits)
    pred = np.zeros_like(target_state, dtype=np.float64)
    null_pred = np.zeros_like(target_state, dtype=np.float64)
    rng = np.random.default_rng(config.random_state)

    for fold, (train_idx, val_idx) in enumerate(splitter.split(frame, groups=groups)):
        model = make_pipeline(
            SimpleImputer(strategy="median"),
            StandardScaler(),
            Ridge(alpha=config.ridge_alpha),
        )
        model.fit(finite_frame(frame.iloc[train_idx], context_columns), target_state[train_idx])
        pred[val_idx] = model.predict(finite_frame(frame.iloc[val_idx], context_columns))

        shuffled = target_state[train_idx].copy()
        rng.shuffle(shuffled, axis=0)
        null_model = make_pipeline(
            SimpleImputer(strategy="median"),
            StandardScaler(),
            Ridge(alpha=config.ridge_alpha),
        )
        null_model.fit(finite_frame(frame.iloc[train_idx], context_columns), shuffled)
        null_pred[val_idx] = null_model.predict(finite_frame(frame.iloc[val_idx], context_columns))

    return pred, null_pred


class HumanStateWorldModel:
    """Label-free HS-JEPA core for tabular human lifelog views."""

    def __init__(self, views: list[SemanticView], config: WorldModelConfig | None = None) -> None:
        if len(views) < 2:
            raise ValueError("at least two semantic views are required")
        self.views = views
        self.config = config or WorldModelConfig()

    @property
    def all_view_columns(self) -> list[str]:
        return sorted({column for view in self.views for column in view.columns})

    def masked_view_state(self, frame: pd.DataFrame, groups: np.ndarray) -> tuple[pd.DataFrame, pd.DataFrame]:
        state = pd.DataFrame(index=frame.index)
        metric_rows: list[PretextMetric] = []
        all_columns = self.all_view_columns

        for view in self.views:
            target_columns = list(view.columns)
            context_columns = [column for column in all_columns if column not in set(target_columns)]
            if len(context_columns) < 2 or len(target_columns) < 2:
                continue

            target_state, _ = encode_latent(
                frame,
                target_columns,
                self.config.latent_dims_per_view,
                self.config.random_state,
            )
            pred, null_pred = ridge_predict_oof(
                frame,
                context_columns,
                target_state,
                groups,
                self.config,
            )
            residual = target_state - pred
            energy = np.sqrt(np.mean(np.square(residual), axis=1))
            for comp in range(target_state.shape[1]):
                state[f"hswm_pred_{view.name}_c{comp + 1}"] = pred[:, comp]
                state[f"hswm_resid_{view.name}_c{comp + 1}"] = residual[:, comp]
            state[f"hswm_energy_{view.name}"] = energy
            state[f"hswm_energy_rank_{view.name}"] = rank01(energy)

            metric_rows.append(
                PretextMetric(
                    task="masked_context_to_view_state",
                    target=view.name,
                    components=int(target_state.shape[1]),
                    context_feature_count=len(context_columns),
                    target_feature_count=len(target_columns),
                    component_corr=component_correlation(target_state, pred),
                    null_component_corr=component_correlation(target_state, null_pred),
                    component_corr_lift_vs_null=component_correlation(target_state, pred)
                    - component_correlation(target_state, null_pred),
                    r2=weighted_r2(target_state, pred),
                    null_r2=weighted_r2(target_state, null_pred),
                    r2_lift_vs_null=weighted_r2(target_state, pred) - weighted_r2(target_state, null_pred),
                )
            )

        energy_cols = [column for column in state.columns if column.startswith("hswm_energy_") and "_rank_" not in column]
        rank_cols = [column for column in state.columns if column.startswith("hswm_energy_rank_")]
        state["hswm_masked_energy_mean"] = state[energy_cols].mean(axis=1)
        state["hswm_masked_energy_max"] = state[energy_cols].max(axis=1)
        state["hswm_masked_energy_rank_mean"] = state[rank_cols].mean(axis=1)
        state["hswm_masked_energy_rank_max"] = state[rank_cols].max(axis=1)
        return state, pd.DataFrame([item.__dict__ for item in metric_rows])

    def future_state(
        self,
        frame: pd.DataFrame,
        subject_column: str,
        date_column: str,
        groups: np.ndarray,
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        raw_state, _ = encode_latent(
            frame,
            self.all_view_columns,
            self.config.future_state_dims,
            self.config.random_state,
        )
        ordered = frame[[subject_column, date_column]].copy()
        ordered["_row"] = np.arange(len(frame))
        ordered[date_column] = pd.to_datetime(ordered[date_column], errors="coerce")
        ordered = ordered.sort_values([subject_column, date_column, "_row"])
        ordered["_next_row"] = ordered.groupby(subject_column, observed=True)["_row"].shift(-1)
        next_row = ordered.set_index("_row")["_next_row"].reindex(np.arange(len(frame))).to_numpy()
        valid = np.isfinite(next_row)

        state = pd.DataFrame(index=frame.index)
        if valid.sum() < 8 or len(np.unique(groups[valid])) < 2:
            for comp in range(raw_state.shape[1]):
                state[f"hswm_future_pred_c{comp + 1}"] = np.nan
                state[f"hswm_future_resid_c{comp + 1}"] = np.nan
            state["hswm_future_energy"] = np.nan
            state["hswm_future_energy_rank"] = np.nan
            return state, pd.DataFrame()

        valid_indices = np.where(valid)[0]
        target_state = raw_state[next_row[valid].astype(int)]
        pred_valid, null_pred_valid = ridge_predict_oof(
            frame.iloc[valid_indices].reset_index(drop=True),
            self.all_view_columns,
            target_state,
            groups[valid],
            self.config,
        )
        pred = np.full_like(raw_state, np.nan, dtype=np.float64)
        residual = np.full_like(raw_state, np.nan, dtype=np.float64)
        pred[valid_indices] = pred_valid
        residual[valid_indices] = target_state - pred_valid
        energy = np.full(len(frame), np.nan, dtype=np.float64)
        energy[valid_indices] = np.sqrt(np.mean(np.square(residual[valid_indices]), axis=1))

        for comp in range(raw_state.shape[1]):
            state[f"hswm_future_pred_c{comp + 1}"] = pred[:, comp]
            state[f"hswm_future_resid_c{comp + 1}"] = residual[:, comp]
        state["hswm_future_energy"] = energy
        state["hswm_future_energy_rank"] = rank01(energy)

        metrics = pd.DataFrame(
            [
                {
                    "task": "current_context_to_future_state",
                    "target": "next_subject_episode",
                    "components": int(raw_state.shape[1]),
                    "context_feature_count": len(self.all_view_columns),
                    "target_feature_count": len(self.all_view_columns),
                    "component_corr": component_correlation(target_state, pred_valid),
                    "null_component_corr": component_correlation(target_state, null_pred_valid),
                    "component_corr_lift_vs_null": component_correlation(target_state, pred_valid)
                    - component_correlation(target_state, null_pred_valid),
                    "r2": weighted_r2(target_state, pred_valid),
                    "null_r2": weighted_r2(target_state, null_pred_valid),
                    "r2_lift_vs_null": weighted_r2(target_state, pred_valid) - weighted_r2(target_state, null_pred_valid),
                    "valid_rows": int(valid.sum()),
                }
            ]
        )
        return state, metrics

    def cohort_state(
        self,
        frame: pd.DataFrame,
        subject_column: str,
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        raw_state, _ = encode_latent(
            frame,
            self.all_view_columns,
            self.config.future_state_dims,
            self.config.random_state,
        )
        row_state = pd.DataFrame(raw_state, index=frame.index)
        subjects = frame[subject_column].astype(str)
        fingerprints = row_state.groupby(subjects, observed=True).agg(["mean", "std"]).fillna(0.0)
        n_clusters = max(2, min(self.config.cohort_count, len(fingerprints)))
        kmeans = KMeans(n_clusters=n_clusters, n_init=32, random_state=self.config.random_state)
        subject_cluster = pd.Series(kmeans.fit_predict(fingerprints), index=fingerprints.index)

        subject_mean = row_state.groupby(subjects, observed=True).transform("mean")
        cohort_mean_by_subject = {}
        for subject, cluster in subject_cluster.items():
            members = subject_cluster[subject_cluster.eq(cluster)].index
            cohort_mean_by_subject[subject] = row_state[subjects.isin(members)].mean(axis=0).to_numpy(dtype=np.float64)

        subject_normal = subject_mean.to_numpy(dtype=np.float64)
        cohort_normal = np.vstack([cohort_mean_by_subject[item] for item in subjects])
        dist_subject = np.sqrt(np.mean(np.square(raw_state - subject_normal), axis=1))
        dist_cohort = np.sqrt(np.mean(np.square(raw_state - cohort_normal), axis=1))
        subject_to_cohort = np.sqrt(np.mean(np.square(subject_normal - cohort_normal), axis=1))

        state = pd.DataFrame(index=frame.index)
        state["hswm_cohort_id"] = subjects.map(subject_cluster).astype(float).to_numpy()
        state["hswm_subject_normal_dist"] = dist_subject
        state["hswm_cohort_normal_dist"] = dist_cohort
        state["hswm_subject_minus_cohort_dist"] = dist_subject - dist_cohort
        state["hswm_subject_to_cohort_dist"] = subject_to_cohort
        state["hswm_cohort_outlier_rank"] = rank01(dist_cohort)

        metrics = pd.DataFrame(
            [
                {
                    "task": "cohort_state_geometry",
                    "target": "subject_fingerprint_cluster",
                    "cohort_count": int(n_clusters),
                    "subject_count": int(len(fingerprints)),
                    "mean_subject_normal_dist": float(np.nanmean(dist_subject)),
                    "mean_cohort_normal_dist": float(np.nanmean(dist_cohort)),
                    "mean_subject_to_cohort_dist": float(np.nanmean(subject_to_cohort)),
                }
            ]
        )
        return state, metrics

    def fit_transform(
        self,
        frame: pd.DataFrame,
        subject_column: str,
        date_column: str,
        group_values: Iterable[object],
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        groups = np.asarray(list(group_values))
        masked_state, masked_metrics = self.masked_view_state(frame, groups)
        future_state, future_metrics = self.future_state(frame, subject_column, date_column, groups)
        cohort_state, cohort_metrics = self.cohort_state(frame, subject_column)
        state = pd.concat([masked_state, future_state, cohort_state], axis=1)
        metrics = pd.concat([masked_metrics, future_metrics, cohort_metrics], ignore_index=True, sort=False)
        return state, metrics
