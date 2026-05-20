from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cross_decomposition import PLSRegression
from sklearn.decomposition import PCA
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, RidgeClassifier
from sklearn.metrics import log_loss
from sklearn.preprocessing import StandardScaler

from train_s2_sleep_retrieval_encoder import (
    EPS,
    KEY_COLUMNS,
    SEED,
    TARGET_COLUMNS,
    add_fold_safe_subject_deviation,
    dataframe_to_markdown,
    load_base_predictions,
    make_subject_time_folds,
    merge_feature_tables,
    normalize_keys,
    safe_logit,
    select_group_columns,
    sigmoid,
)


@dataclass(frozen=True)
class SourcePack:
    name: str
    oof: np.ndarray
    sample: np.ndarray
    avg_log_loss: float
    target_log_loss: dict[str, float]


def average_log_loss(y: pd.DataFrame, pred: np.ndarray) -> tuple[float, dict[str, float]]:
    clipped = np.clip(pred, EPS, 1.0 - EPS)
    per_target = {
        target: float(log_loss(y[target].to_numpy(int), clipped[:, i], labels=[0, 1]))
        for i, target in enumerate(TARGET_COLUMNS)
    }
    return float(np.mean(list(per_target.values()))), per_target


def select_joint_columns(frame: pd.DataFrame, groups: list[str]) -> list[str]:
    columns = frame.columns.tolist()
    selected: list[str] = []
    for group in groups:
        selected.extend(select_group_columns(columns, group))
    deduped = sorted(set(selected))
    if not deduped:
        raise ValueError(f"No columns selected for groups={groups}")
    return deduped


def top_label_aligned_columns(x_fit: pd.DataFrame, y_fit: pd.DataFrame, max_features: int) -> list[str]:
    missing = x_fit.isna().mean(axis=0)
    unique = x_fit.nunique(dropna=True)
    candidates = x_fit.columns[(missing <= 0.75) & (unique > 1)].tolist()
    if len(candidates) <= max_features:
        return candidates

    imputer = SimpleImputer(strategy="median", keep_empty_features=True)
    values = imputer.fit_transform(x_fit[candidates])
    values = np.nan_to_num(values, nan=0.0, posinf=0.0, neginf=0.0)
    scores = np.zeros(len(candidates), dtype=float)
    for target in TARGET_COLUMNS:
        y = y_fit[target].to_numpy(int)
        if len(np.unique(y)) < 2:
            continue
        pos = values[y == 1]
        neg = values[y == 0]
        mean_gap = np.abs(np.nanmean(pos, axis=0) - np.nanmean(neg, axis=0))
        pooled = np.nanstd(values, axis=0) + 1e-6
        scores = np.maximum(scores, mean_gap / pooled)
    order = np.argsort(scores)[::-1]
    keep = [candidates[i] for i in order[:max_features]]
    return sorted(keep)


def top_residual_aligned_columns(x_fit: pd.DataFrame, residual_fit: np.ndarray, max_features: int) -> list[str]:
    missing = x_fit.isna().mean(axis=0)
    unique = x_fit.nunique(dropna=True)
    candidates = x_fit.columns[(missing <= 0.75) & (unique > 1)].tolist()
    if len(candidates) <= max_features:
        return candidates

    imputer = SimpleImputer(strategy="median", keep_empty_features=True)
    values = imputer.fit_transform(x_fit[candidates])
    values = np.nan_to_num(values, nan=0.0, posinf=0.0, neginf=0.0)
    values = (values - np.mean(values, axis=0, keepdims=True)) / (np.std(values, axis=0, keepdims=True) + 1e-6)
    residual = np.nan_to_num(residual_fit, nan=0.0, posinf=0.0, neginf=0.0)
    residual = residual - np.mean(residual, axis=0, keepdims=True)
    residual = residual / (np.std(residual, axis=0, keepdims=True) + 1e-6)
    scores = np.max(np.abs(values.T @ residual) / max(1, values.shape[0]), axis=1)
    order = np.argsort(scores)[::-1]
    keep = [candidates[i] for i in order[:max_features]]
    return sorted(keep)


def fit_joint_latent(
    x_fit: pd.DataFrame,
    y_fit: pd.DataFrame,
    x_apply: pd.DataFrame,
    x_sample: pd.DataFrame,
    max_features: int,
    pca_dim: int,
    pls_dim: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict[str, int]]:
    keep = top_label_aligned_columns(x_fit, y_fit, max_features)
    imputer = SimpleImputer(strategy="median", keep_empty_features=True)
    scaler = StandardScaler()
    fit_x = scaler.fit_transform(imputer.fit_transform(x_fit[keep]))
    apply_x = scaler.transform(imputer.transform(x_apply[keep]))
    sample_x = scaler.transform(imputer.transform(x_sample[keep]))
    fit_x = np.clip(np.nan_to_num(fit_x, nan=0.0, posinf=8.0, neginf=-8.0), -8.0, 8.0)
    apply_x = np.clip(np.nan_to_num(apply_x, nan=0.0, posinf=8.0, neginf=-8.0), -8.0, 8.0)
    sample_x = np.clip(np.nan_to_num(sample_x, nan=0.0, posinf=8.0, neginf=-8.0), -8.0, 8.0)

    latent_fit_parts: list[np.ndarray] = []
    latent_apply_parts: list[np.ndarray] = []
    latent_sample_parts: list[np.ndarray] = []
    used_pca_dim = min(pca_dim, fit_x.shape[0] - 1, fit_x.shape[1])
    if used_pca_dim >= 2:
        pca = PCA(n_components=used_pca_dim, random_state=SEED)
        latent_fit_parts.append(pca.fit_transform(fit_x))
        latent_apply_parts.append(pca.transform(apply_x))
        latent_sample_parts.append(pca.transform(sample_x))

    y_center = y_fit[TARGET_COLUMNS].to_numpy(float)
    used_pls_dim = min(pls_dim, fit_x.shape[0] - 2, fit_x.shape[1], len(TARGET_COLUMNS))
    if used_pls_dim >= 2:
        pls = PLSRegression(n_components=used_pls_dim, scale=False)
        pls.fit(fit_x, y_center)
        latent_fit_parts.append(pls.transform(fit_x))
        latent_apply_parts.append(pls.transform(apply_x))
        latent_sample_parts.append(pls.transform(sample_x))

    if not latent_fit_parts:
        latent_fit_parts = [fit_x]
        latent_apply_parts = [apply_x]
        latent_sample_parts = [sample_x]

    z_fit = np.hstack(latent_fit_parts)
    z_apply = np.hstack(latent_apply_parts)
    z_sample = np.hstack(latent_sample_parts)
    for arr in (z_fit, z_apply, z_sample):
        arr[:] = np.clip(np.nan_to_num(arr, nan=0.0, posinf=8.0, neginf=-8.0), -8.0, 8.0)

    z_scaler = StandardScaler()
    z_fit = z_scaler.fit_transform(z_fit)
    z_apply = z_scaler.transform(z_apply)
    z_sample = z_scaler.transform(z_sample)

    for arr in (z_fit, z_apply, z_sample):
        arr[:] = np.clip(np.nan_to_num(arr, nan=0.0, posinf=8.0, neginf=-8.0), -8.0, 8.0)
    meta = {"selected_features": len(keep), "pca_dim": max(0, used_pca_dim), "pls_dim": max(0, used_pls_dim), "latent_dim": z_fit.shape[1]}
    return z_fit.astype(np.float32), z_apply.astype(np.float32), z_sample.astype(np.float32), meta


def fit_residual_pls_latent(
    x_fit: pd.DataFrame,
    residual_fit: np.ndarray,
    x_apply: pd.DataFrame,
    x_sample: pd.DataFrame,
    max_features: int,
    pls_dim: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict[str, int]]:
    keep = top_residual_aligned_columns(x_fit, residual_fit, max_features)
    imputer = SimpleImputer(strategy="median", keep_empty_features=True)
    scaler = StandardScaler()
    fit_x = scaler.fit_transform(imputer.fit_transform(x_fit[keep]))
    apply_x = scaler.transform(imputer.transform(x_apply[keep]))
    sample_x = scaler.transform(imputer.transform(x_sample[keep]))
    fit_x = np.clip(np.nan_to_num(fit_x, nan=0.0, posinf=8.0, neginf=-8.0), -8.0, 8.0)
    apply_x = np.clip(np.nan_to_num(apply_x, nan=0.0, posinf=8.0, neginf=-8.0), -8.0, 8.0)
    sample_x = np.clip(np.nan_to_num(sample_x, nan=0.0, posinf=8.0, neginf=-8.0), -8.0, 8.0)

    residual = np.nan_to_num(residual_fit, nan=0.0, posinf=0.0, neginf=0.0)
    residual = residual - np.mean(residual, axis=0, keepdims=True)
    used_pls_dim = min(pls_dim, fit_x.shape[0] - 2, fit_x.shape[1], residual.shape[1])
    if used_pls_dim >= 2 and np.std(residual) > 1e-8:
        pls = PLSRegression(n_components=used_pls_dim, scale=False)
        pls.fit(fit_x, residual)
        z_fit = pls.transform(fit_x)
        z_apply = pls.transform(apply_x)
        z_sample = pls.transform(sample_x)
    else:
        used_pls_dim = min(max(2, pls_dim), fit_x.shape[0] - 1, fit_x.shape[1])
        pca = PCA(n_components=used_pls_dim, random_state=SEED)
        z_fit = pca.fit_transform(fit_x)
        z_apply = pca.transform(apply_x)
        z_sample = pca.transform(sample_x)

    z_scaler = StandardScaler()
    z_fit = z_scaler.fit_transform(z_fit)
    z_apply = z_scaler.transform(z_apply)
    z_sample = z_scaler.transform(z_sample)
    for arr in (z_fit, z_apply, z_sample):
        arr[:] = np.clip(np.nan_to_num(arr, nan=0.0, posinf=8.0, neginf=-8.0), -8.0, 8.0)
    meta = {"residual_selected_features": len(keep), "residual_pls_dim": max(0, used_pls_dim), "residual_latent_dim": z_fit.shape[1]}
    return z_fit.astype(np.float32), z_apply.astype(np.float32), z_sample.astype(np.float32), meta


def fit_head_probability(
    method: str,
    z_fit: np.ndarray,
    y_fit: np.ndarray,
    z_apply: np.ndarray,
    z_sample: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    z_fit = np.clip(np.nan_to_num(z_fit, nan=0.0, posinf=8.0, neginf=-8.0), -8.0, 8.0)
    z_apply = np.clip(np.nan_to_num(z_apply, nan=0.0, posinf=8.0, neginf=-8.0), -8.0, 8.0)
    z_sample = np.clip(np.nan_to_num(z_sample, nan=0.0, posinf=8.0, neginf=-8.0), -8.0, 8.0)
    if method == "logreg":
        model = LogisticRegression(C=0.10, class_weight="balanced", max_iter=2000, solver="liblinear", random_state=SEED)
    elif method == "ridge":
        model = RidgeClassifier(alpha=10.0, class_weight="balanced", solver="lsqr")
    elif method == "hgb":
        model = HistGradientBoostingClassifier(
            learning_rate=0.03,
            max_iter=70,
            max_leaf_nodes=7,
            l2_regularization=0.6,
            min_samples_leaf=16,
            random_state=SEED,
        )
    else:
        raise ValueError(method)
    model.fit(z_fit, y_fit)
    if hasattr(model, "predict_proba"):
        return model.predict_proba(z_apply)[:, 1], model.predict_proba(z_sample)[:, 1]
    return sigmoid(model.decision_function(z_apply)), sigmoid(model.decision_function(z_sample))


def weighted_knn_residual(
    z_fit: np.ndarray,
    z_apply: np.ndarray,
    y_fit: np.ndarray,
    base_fit: np.ndarray,
    base_apply: np.ndarray,
    k: int,
    temp: float,
    logit_mode: bool,
) -> np.ndarray:
    z_fit = np.clip(np.nan_to_num(z_fit, nan=0.0, posinf=8.0, neginf=-8.0), -8.0, 8.0)
    z_apply = np.clip(np.nan_to_num(z_apply, nan=0.0, posinf=8.0, neginf=-8.0), -8.0, 8.0)
    d2 = ((z_apply[:, None, :] - z_fit[None, :, :]) ** 2).mean(axis=2)
    kk = min(k, z_fit.shape[0])
    idx = np.argpartition(d2, kk - 1, axis=1)[:, :kk]
    chosen = np.take_along_axis(d2, idx, axis=1)
    scale = np.maximum(np.median(chosen, axis=1, keepdims=True), 1e-6) * temp
    weights = np.exp(-chosen / scale)
    weights = weights / np.maximum(weights.sum(axis=1, keepdims=True), 1e-12)
    if logit_mode:
        y_smooth = y_fit * 0.98 + 0.01
        residual = safe_logit(y_smooth) - safe_logit(base_fit)
        pred = sigmoid(safe_logit(base_apply) + (weights * residual[idx]).sum(axis=1))
    else:
        residual = y_fit - base_fit
        pred = base_apply + (weights * residual[idx]).sum(axis=1)
    return np.clip(pred, EPS, 1.0 - EPS)


def label_metric_weights(z_fit: np.ndarray, y_fit: np.ndarray) -> np.ndarray:
    z_fit = np.clip(np.nan_to_num(z_fit, nan=0.0, posinf=8.0, neginf=-8.0), -8.0, 8.0)
    if len(np.unique(y_fit)) < 2:
        return np.ones(z_fit.shape[1], dtype=np.float32)
    pos = z_fit[y_fit == 1]
    neg = z_fit[y_fit == 0]
    gap = np.abs(pos.mean(axis=0) - neg.mean(axis=0))
    spread = z_fit.std(axis=0) + 1e-6
    score = gap / spread
    score = np.nan_to_num(score, nan=0.0, posinf=0.0, neginf=0.0)
    if np.max(score) <= 1e-6:
        return np.ones(z_fit.shape[1], dtype=np.float32)
    weights = 0.35 + 3.65 * (score / np.max(score))
    return weights.astype(np.float32)


def residual_metric_weights(z_fit: np.ndarray, residual_fit: np.ndarray) -> np.ndarray:
    z_fit = np.clip(np.nan_to_num(z_fit, nan=0.0, posinf=8.0, neginf=-8.0), -8.0, 8.0)
    residual_fit = np.nan_to_num(residual_fit, nan=0.0, posinf=0.0, neginf=0.0)
    if len(residual_fit) < 20 or np.nanstd(residual_fit) <= 1e-6:
        return np.ones(z_fit.shape[1], dtype=np.float32)
    lo, hi = np.quantile(residual_fit, [0.35, 0.65])
    low_mask = residual_fit <= lo
    high_mask = residual_fit >= hi
    if low_mask.sum() < 8 or high_mask.sum() < 8:
        return np.ones(z_fit.shape[1], dtype=np.float32)
    gap = np.abs(z_fit[high_mask].mean(axis=0) - z_fit[low_mask].mean(axis=0))
    spread = z_fit.std(axis=0) + 1e-6
    score = np.nan_to_num(gap / spread, nan=0.0, posinf=0.0, neginf=0.0)
    if np.max(score) <= 1e-6:
        return np.ones(z_fit.shape[1], dtype=np.float32)
    weights = 0.30 + 4.20 * (score / np.max(score))
    return weights.astype(np.float32)


def residual_contrast_features(
    ref_z: np.ndarray,
    query_z: np.ndarray,
    ref_y: np.ndarray,
    ref_base: np.ndarray,
    query_base: np.ndarray,
    metric_weights: np.ndarray,
) -> np.ndarray:
    weights = np.sqrt(np.maximum(metric_weights, 1e-6)).reshape(1, -1)
    ref_z = np.clip(np.nan_to_num(ref_z * weights, nan=0.0, posinf=8.0, neginf=-8.0), -8.0, 8.0)
    query_z = np.clip(np.nan_to_num(query_z * weights, nan=0.0, posinf=8.0, neginf=-8.0), -8.0, 8.0)
    residual = np.nan_to_num(ref_y - ref_base, nan=0.0, posinf=0.0, neginf=0.0)
    lo, hi = np.quantile(residual, [0.35, 0.65]) if len(residual) else (0.0, 0.0)
    low_mask = residual <= lo
    high_mask = residual >= hi
    if low_mask.sum() < 8 or high_mask.sum() < 8:
        center_high = ref_z.mean(axis=0)
        center_low = ref_z.mean(axis=0)
    else:
        center_high = ref_z[high_mask].mean(axis=0)
        center_low = ref_z[low_mask].mean(axis=0)
    direction = center_high - center_low
    norm = float(np.linalg.norm(direction))
    if norm <= 1e-6:
        direction = np.zeros_like(direction)
        norm = 1.0
    unit = direction / norm
    d_high = ((query_z - center_high) ** 2).mean(axis=1)
    d_low = ((query_z - center_low) ** 2).mean(axis=1)
    contrast_raw = (query_z - (center_high + center_low) / 2.0) @ unit
    raw_scale = np.std(contrast_raw) if np.std(contrast_raw) > 1e-6 else 1.0
    contrast_prob = sigmoid(safe_logit(query_base) + contrast_raw / raw_scale)
    features = np.column_stack(
        [
            query_base,
            safe_logit(query_base),
            d_high,
            d_low,
            d_low - d_high,
            contrast_raw,
            contrast_raw / raw_scale,
            contrast_prob,
            contrast_prob - query_base,
            np.full(len(query_z), float(np.mean(residual))),
            np.full(len(query_z), float(np.std(residual))),
            np.full(len(query_z), float(hi - lo)),
        ]
    )
    return np.clip(np.nan_to_num(features, nan=0.0, posinf=8.0, neginf=-8.0), -8.0, 8.0).astype(np.float32)


def metric_weighted_knn_residual(
    z_fit: np.ndarray,
    z_apply: np.ndarray,
    y_fit: np.ndarray,
    base_fit: np.ndarray,
    base_apply: np.ndarray,
    metric_weights: np.ndarray,
    k: int,
    temp: float,
    logit_mode: bool,
) -> np.ndarray:
    weights = np.sqrt(np.maximum(metric_weights, 1e-6)).reshape(1, -1)
    return weighted_knn_residual(
        z_fit * weights,
        z_apply * weights,
        y_fit,
        base_fit,
        base_apply,
        k,
        temp,
        logit_mode,
    )


def attention_knn_residual(
    z_fit: np.ndarray,
    z_apply: np.ndarray,
    y_fit: np.ndarray,
    base_fit: np.ndarray,
    base_apply: np.ndarray,
    fit_keys: pd.DataFrame,
    apply_keys: pd.DataFrame,
    metric_weights: np.ndarray | None,
    k: int,
    temp: float,
    logit_mode: bool,
) -> np.ndarray:
    z_fit = np.clip(np.nan_to_num(z_fit, nan=0.0, posinf=8.0, neginf=-8.0), -8.0, 8.0)
    z_apply = np.clip(np.nan_to_num(z_apply, nan=0.0, posinf=8.0, neginf=-8.0), -8.0, 8.0)
    if metric_weights is not None:
        weights = np.sqrt(np.maximum(metric_weights, 1e-6)).reshape(1, -1)
        z_fit = z_fit * weights
        z_apply = z_apply * weights
    d2 = ((z_apply[:, None, :] - z_fit[None, :, :]) ** 2).mean(axis=2)
    kk = min(k, z_fit.shape[0])
    idx = np.argpartition(d2, kk - 1, axis=1)[:, :kk]
    chosen = np.take_along_axis(d2, idx, axis=1)

    fit_subjects = fit_keys["subject_id"].astype(str).to_numpy()
    apply_subjects = apply_keys["subject_id"].astype(str).to_numpy()
    same_subject = (apply_subjects[:, None] == fit_subjects[idx]).astype(float)

    fit_dates = pd.to_datetime(fit_keys["lifelog_date"]).to_numpy(dtype="datetime64[D]")
    apply_dates = pd.to_datetime(apply_keys["lifelog_date"]).to_numpy(dtype="datetime64[D]")
    day_delta = np.abs((apply_dates[:, None] - fit_dates[idx]).astype("timedelta64[D]").astype(float))
    recency = np.exp(-np.clip(day_delta, 0.0, 365.0) / 21.0)

    scale = np.maximum(np.nanmedian(chosen, axis=1, keepdims=True), 1e-6) * temp
    score = -chosen / scale + 0.65 * same_subject + 0.35 * recency
    score = score - np.max(score, axis=1, keepdims=True)
    attn = np.exp(np.clip(score, -50.0, 50.0))
    attn = attn / np.maximum(attn.sum(axis=1, keepdims=True), 1e-12)

    if logit_mode:
        y_smooth = y_fit * 0.98 + 0.01
        residual = safe_logit(y_smooth) - safe_logit(base_fit)
        pred = sigmoid(safe_logit(base_apply) + (attn * residual[idx]).sum(axis=1))
    else:
        residual = y_fit - base_fit
        pred = base_apply + (attn * residual[idx]).sum(axis=1)
    return np.clip(pred, EPS, 1.0 - EPS)


def neighbor_context_features(
    ref_z: np.ndarray,
    query_z: np.ndarray,
    ref_y: np.ndarray,
    ref_base: np.ndarray,
    query_base: np.ndarray,
    ref_keys: pd.DataFrame,
    query_keys: pd.DataFrame,
    metric_weights: np.ndarray | None,
    k: int,
    temp: float,
    exclude_self: bool = False,
) -> np.ndarray:
    ref_z = np.clip(np.nan_to_num(ref_z, nan=0.0, posinf=8.0, neginf=-8.0), -8.0, 8.0)
    query_z = np.clip(np.nan_to_num(query_z, nan=0.0, posinf=8.0, neginf=-8.0), -8.0, 8.0)
    if metric_weights is not None:
        weights = np.sqrt(np.maximum(metric_weights, 1e-6)).reshape(1, -1)
        ref_z = ref_z * weights
        query_z = query_z * weights

    d2 = ((query_z[:, None, :] - ref_z[None, :, :]) ** 2).mean(axis=2)
    if exclude_self and len(query_z) == len(ref_z):
        np.fill_diagonal(d2, np.inf)
    kk = min(k, max(1, ref_z.shape[0] - (1 if exclude_self else 0)))
    idx = np.argpartition(d2, kk - 1, axis=1)[:, :kk]
    chosen = np.take_along_axis(d2, idx, axis=1)

    ref_subjects = ref_keys["subject_id"].astype(str).to_numpy()
    query_subjects = query_keys["subject_id"].astype(str).to_numpy()
    same_subject = (query_subjects[:, None] == ref_subjects[idx]).astype(float)

    ref_dates = pd.to_datetime(ref_keys["lifelog_date"]).to_numpy(dtype="datetime64[D]")
    query_dates = pd.to_datetime(query_keys["lifelog_date"]).to_numpy(dtype="datetime64[D]")
    day_delta = np.abs((query_dates[:, None] - ref_dates[idx]).astype("timedelta64[D]").astype(float))
    recency = np.exp(-np.clip(day_delta, 0.0, 365.0) / 21.0)

    scale = np.maximum(np.nanmedian(chosen, axis=1, keepdims=True), 1e-6) * temp
    distance_weight = np.exp(-chosen / scale)
    distance_weight = distance_weight / np.maximum(distance_weight.sum(axis=1, keepdims=True), 1e-12)

    context_score = -chosen / scale + 0.65 * same_subject + 0.35 * recency
    context_score = context_score - np.max(context_score, axis=1, keepdims=True)
    context_weight = np.exp(np.clip(context_score, -50.0, 50.0))
    context_weight = context_weight / np.maximum(context_weight.sum(axis=1, keepdims=True), 1e-12)

    residual = ref_y - ref_base
    y_smooth = ref_y * 0.98 + 0.01
    logit_residual = safe_logit(y_smooth) - safe_logit(ref_base)

    def weighted(values: np.ndarray, weights: np.ndarray) -> np.ndarray:
        return (weights * values[idx]).sum(axis=1)

    same_mass = (context_weight * same_subject).sum(axis=1)
    recent_mass = (context_weight * recency).sum(axis=1)
    close_same_mass = (context_weight * same_subject * (day_delta <= 14.0)).sum(axis=1)
    far_cross_mass = (context_weight * (1.0 - same_subject) * (day_delta > 28.0)).sum(axis=1)

    dist_min = np.nanmin(chosen, axis=1)
    dist_mean = np.nanmean(chosen, axis=1)
    dist_std = np.nanstd(chosen, axis=1)
    day_mean = (context_weight * np.clip(day_delta, 0.0, 365.0)).sum(axis=1)
    label_dist = weighted(ref_y, distance_weight)
    label_ctx = weighted(ref_y, context_weight)
    resid_dist = weighted(residual, distance_weight)
    resid_ctx = weighted(residual, context_weight)
    logit_dist = weighted(logit_residual, distance_weight)
    logit_ctx = weighted(logit_residual, context_weight)
    base_ctx = weighted(ref_base, context_weight)

    features = np.column_stack(
        [
            query_base,
            safe_logit(query_base),
            label_dist,
            label_ctx,
            np.clip(query_base + resid_dist, EPS, 1.0 - EPS),
            np.clip(query_base + resid_ctx, EPS, 1.0 - EPS),
            sigmoid(safe_logit(query_base) + logit_dist),
            sigmoid(safe_logit(query_base) + logit_ctx),
            resid_dist,
            resid_ctx,
            logit_dist,
            logit_ctx,
            base_ctx,
            label_ctx - label_dist,
            same_mass,
            recent_mass,
            close_same_mass,
            far_cross_mass,
            dist_min,
            dist_mean,
            dist_std,
            1.0 / np.sqrt(np.maximum(dist_mean, 1e-6)),
            day_mean / 30.0,
        ]
    )
    return np.clip(np.nan_to_num(features, nan=0.0, posinf=8.0, neginf=-8.0), -8.0, 8.0).astype(np.float32)


def local_decoder_features(
    ref_z: np.ndarray,
    query_z: np.ndarray,
    ref_y: np.ndarray,
    ref_base: np.ndarray,
    query_base: np.ndarray,
    k: int,
    temp: float,
    exclude_self: bool = False,
) -> np.ndarray:
    ref_z = np.clip(np.nan_to_num(ref_z, nan=0.0, posinf=8.0, neginf=-8.0), -8.0, 8.0)
    query_z = np.clip(np.nan_to_num(query_z, nan=0.0, posinf=8.0, neginf=-8.0), -8.0, 8.0)
    d2 = ((query_z[:, None, :] - ref_z[None, :, :]) ** 2).mean(axis=2)
    if exclude_self and len(query_z) == len(ref_z):
        np.fill_diagonal(d2, np.inf)
    kk = min(k, max(1, ref_z.shape[0] - (1 if exclude_self else 0)))
    idx = np.argpartition(d2, kk - 1, axis=1)[:, :kk]
    chosen = np.take_along_axis(d2, idx, axis=1)
    scale = np.maximum(np.nanmedian(chosen, axis=1, keepdims=True), 1e-6) * temp
    weights = np.exp(-chosen / scale)
    weights = weights / np.maximum(weights.sum(axis=1, keepdims=True), 1e-12)

    knn_label = (weights * ref_y[idx]).sum(axis=1)
    residual = ref_y - ref_base
    knn_resid = np.clip(query_base + (weights * residual[idx]).sum(axis=1), EPS, 1.0 - EPS)
    y_smooth = ref_y * 0.98 + 0.01
    logit_residual = safe_logit(y_smooth) - safe_logit(ref_base)
    knn_logit = sigmoid(safe_logit(query_base) + (weights * logit_residual[idx]).sum(axis=1))

    prior = np.clip(ref_y.mean(), EPS, 1.0 - EPS)
    if len(np.unique(ref_y)) >= 2:
        pos = ref_z[ref_y == 1].mean(axis=0)
        neg = ref_z[ref_y == 0].mean(axis=0)
        d_pos = ((query_z - pos) ** 2).mean(axis=1)
        d_neg = ((query_z - neg) ** 2).mean(axis=1)
        proto_raw = d_neg - d_pos
        proto_scale = np.std(proto_raw) if np.std(proto_raw) > 1e-6 else 1.0
        proto = sigmoid(safe_logit(np.full(len(query_z), prior)) + proto_raw / proto_scale)
    else:
        d_pos = np.full(len(query_z), np.nan)
        d_neg = np.full(len(query_z), np.nan)
        proto_raw = np.zeros(len(query_z))
        proto = np.full(len(query_z), prior)

    d_min = np.nanmin(chosen, axis=1)
    d_mean = np.nanmean(chosen, axis=1)
    d_std = np.nanstd(chosen, axis=1)
    features = np.column_stack(
        [
            safe_logit(query_base),
            knn_label,
            knn_resid,
            knn_logit,
            safe_logit(knn_logit) - safe_logit(query_base),
            knn_resid - query_base,
            proto,
            proto - prior,
            proto_raw,
            d_pos,
            d_neg,
            d_min,
            d_mean,
            d_std,
            1.0 / np.sqrt(np.maximum(d_mean, 1e-6)),
        ]
    )
    return np.clip(np.nan_to_num(features, nan=0.0, posinf=8.0, neginf=-8.0), -8.0, 8.0).astype(np.float32)


def fit_local_decoder(
    method: str,
    fit_features: np.ndarray,
    y_fit: np.ndarray,
    apply_features: np.ndarray,
    sample_features: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    if method == "local_logreg":
        model = LogisticRegression(C=0.08, class_weight="balanced", max_iter=2000, solver="liblinear", random_state=SEED)
    elif method == "local_hgb":
        model = HistGradientBoostingClassifier(
            learning_rate=0.025,
            max_iter=60,
            max_leaf_nodes=5,
            l2_regularization=0.8,
            min_samples_leaf=18,
            random_state=SEED,
        )
    else:
        raise ValueError(method)
    model.fit(fit_features, y_fit)
    return model.predict_proba(apply_features)[:, 1], model.predict_proba(sample_features)[:, 1]


def write_source(output_dir: Path, train: pd.DataFrame, sample: pd.DataFrame, source: SourcePack) -> tuple[Path, Path]:
    oof = train[KEY_COLUMNS + TARGET_COLUMNS].copy()
    submission = sample[KEY_COLUMNS].copy()
    for i, target in enumerate(TARGET_COLUMNS):
        oof[f"pred_{target}"] = np.clip(source.oof[:, i], EPS, 1.0 - EPS)
        submission[target] = np.clip(source.sample[:, i], EPS, 1.0 - EPS)
    oof_path = output_dir / f"oof_{source.name}.csv"
    sub_path = output_dir / f"submission_{source.name}.csv"
    oof.to_csv(oof_path, index=False)
    submission.to_csv(sub_path, index=False)
    return oof_path, sub_path


def train_joint_encoder(args: argparse.Namespace) -> None:
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    base_train, base_sample = load_base_predictions(train, sample, Path(args.base_oof), Path(args.base_submission))
    raw_train_x, raw_sample_x = merge_feature_tables(train, sample)
    groups = [group.strip() for group in args.groups.split(",") if group.strip()]
    columns = select_joint_columns(raw_train_x, groups)
    group_train_x = raw_train_x[columns]
    group_sample_x = raw_sample_x[columns]
    folds = make_subject_time_folds(train, args.n_folds)
    y_df = train[TARGET_COLUMNS].astype(int)

    source_names = [
        "joint_pls_logreg",
        "joint_pls_hgb",
        "joint_pls_ridge",
        "joint_pls_knn_resid",
        "joint_pls_knn_logitresid",
        "joint_metric_knn_resid",
        "joint_metric_knn_logitresid",
        "joint_residual_metric_knn_resid",
        "joint_residual_metric_knn_logitresid",
        "joint_residual_contrast_logreg",
        "joint_residual_contrast_hgb",
        "joint_residual_metric_neighbor_logreg",
        "joint_residual_metric_neighbor_hgb",
        "joint_residual_pls_knn_resid",
        "joint_residual_pls_knn_logitresid",
        "joint_residual_pls_local_logreg",
        "joint_residual_pls_local_hgb",
        "joint_residual_pls_neighbor_logreg",
        "joint_residual_pls_neighbor_hgb",
        "joint_attention_knn_resid",
        "joint_attention_knn_logitresid",
        "joint_metric_attention_knn_resid",
        "joint_metric_attention_knn_logitresid",
        "joint_neighbor_logreg",
        "joint_neighbor_hgb",
        "joint_metric_neighbor_logreg",
        "joint_metric_neighbor_hgb",
        "joint_local_logreg",
        "joint_local_hgb",
        "joint_proto_mix",
    ]
    oof_by_source = {name: np.full_like(base_train, np.nan, dtype=float) for name in source_names}
    sample_folds_by_source = {name: [] for name in source_names}
    latent_oof = np.full((len(train), args.pca_dim + min(args.pls_dim, len(TARGET_COLUMNS))), np.nan, dtype=float)
    latent_sample_folds: list[np.ndarray] = []
    fold_meta: list[dict[str, int | float]] = []

    for fold_id, fold in enumerate(folds):
        fit_x, val_x, sample_x = add_fold_safe_subject_deviation(
            group_train_x,
            group_sample_x,
            train[KEY_COLUMNS],
            sample[KEY_COLUMNS],
            fold.train_idx,
            fold.val_idx,
        )
        assert val_x is not None
        z_fit, z_val, z_sample, meta = fit_joint_latent(
            fit_x,
            y_df.iloc[fold.train_idx],
            val_x,
            sample_x,
            args.max_features,
            args.pca_dim,
            args.pls_dim,
        )
        residual_fit_targets = y_df.iloc[fold.train_idx][TARGET_COLUMNS].to_numpy(float) - base_train[fold.train_idx, :]
        rz_fit, rz_val, rz_sample, residual_meta = fit_residual_pls_latent(
            fit_x,
            residual_fit_targets,
            val_x,
            sample_x,
            args.max_features,
            args.residual_pls_dim,
        )
        if latent_oof.shape[1] != z_val.shape[1]:
            latent_oof = np.full((len(train), z_val.shape[1]), np.nan, dtype=float)
        latent_oof[fold.val_idx] = z_val
        latent_sample_folds.append(z_sample)
        meta = {"fold": fold_id, "train_rows": int(len(fold.train_idx)), "valid_rows": int(len(fold.val_idx)), **meta, **residual_meta}
        fold_meta.append(meta)

        for target_i, target in enumerate(TARGET_COLUMNS):
            y_fit = y_df.iloc[fold.train_idx][target].to_numpy(int)
            base_fit = base_train[fold.train_idx, target_i]
            base_val = base_train[fold.val_idx, target_i]
            base_test = base_sample[:, target_i]
            for method in ("logreg", "hgb", "ridge"):
                val_pred, sample_pred = fit_head_probability(method, z_fit, y_fit, z_val, z_sample)
                oof_by_source[f"joint_pls_{method}"][fold.val_idx, target_i] = val_pred
                sample_folds_by_source[f"joint_pls_{method}"].append((target_i, sample_pred))
            oof_by_source["joint_pls_knn_resid"][fold.val_idx, target_i] = weighted_knn_residual(
                z_fit, z_val, y_fit, base_fit, base_val, args.knn_k, args.knn_temp, False
            )
            sample_folds_by_source["joint_pls_knn_resid"].append(
                (target_i, weighted_knn_residual(z_fit, z_sample, y_fit, base_fit, base_test, args.knn_k, args.knn_temp, False))
            )
            oof_by_source["joint_pls_knn_logitresid"][fold.val_idx, target_i] = weighted_knn_residual(
                z_fit, z_val, y_fit, base_fit, base_val, args.knn_k, args.knn_temp, True
            )
            sample_folds_by_source["joint_pls_knn_logitresid"].append(
                (target_i, weighted_knn_residual(z_fit, z_sample, y_fit, base_fit, base_test, args.knn_k, args.knn_temp, True))
            )
            metric_weights = label_metric_weights(z_fit, y_fit)
            residual_weights = residual_metric_weights(z_fit, y_fit - base_fit)
            oof_by_source["joint_metric_knn_resid"][fold.val_idx, target_i] = metric_weighted_knn_residual(
                z_fit, z_val, y_fit, base_fit, base_val, metric_weights, args.knn_k, args.knn_temp, False
            )
            sample_folds_by_source["joint_metric_knn_resid"].append(
                (
                    target_i,
                    metric_weighted_knn_residual(z_fit, z_sample, y_fit, base_fit, base_test, metric_weights, args.knn_k, args.knn_temp, False),
                )
            )
            oof_by_source["joint_metric_knn_logitresid"][fold.val_idx, target_i] = metric_weighted_knn_residual(
                z_fit, z_val, y_fit, base_fit, base_val, metric_weights, args.knn_k, args.knn_temp, True
            )
            sample_folds_by_source["joint_metric_knn_logitresid"].append(
                (
                    target_i,
                    metric_weighted_knn_residual(z_fit, z_sample, y_fit, base_fit, base_test, metric_weights, args.knn_k, args.knn_temp, True),
                )
            )
            oof_by_source["joint_residual_metric_knn_resid"][fold.val_idx, target_i] = metric_weighted_knn_residual(
                z_fit, z_val, y_fit, base_fit, base_val, residual_weights, args.knn_k, args.knn_temp, False
            )
            sample_folds_by_source["joint_residual_metric_knn_resid"].append(
                (
                    target_i,
                    metric_weighted_knn_residual(z_fit, z_sample, y_fit, base_fit, base_test, residual_weights, args.knn_k, args.knn_temp, False),
                )
            )
            oof_by_source["joint_residual_metric_knn_logitresid"][fold.val_idx, target_i] = metric_weighted_knn_residual(
                z_fit, z_val, y_fit, base_fit, base_val, residual_weights, args.knn_k, args.knn_temp, True
            )
            sample_folds_by_source["joint_residual_metric_knn_logitresid"].append(
                (
                    target_i,
                    metric_weighted_knn_residual(z_fit, z_sample, y_fit, base_fit, base_test, residual_weights, args.knn_k, args.knn_temp, True),
                )
            )
            oof_by_source["joint_residual_pls_knn_resid"][fold.val_idx, target_i] = weighted_knn_residual(
                rz_fit, rz_val, y_fit, base_fit, base_val, args.knn_k, args.knn_temp, False
            )
            sample_folds_by_source["joint_residual_pls_knn_resid"].append(
                (target_i, weighted_knn_residual(rz_fit, rz_sample, y_fit, base_fit, base_test, args.knn_k, args.knn_temp, False))
            )
            oof_by_source["joint_residual_pls_knn_logitresid"][fold.val_idx, target_i] = weighted_knn_residual(
                rz_fit, rz_val, y_fit, base_fit, base_val, args.knn_k, args.knn_temp, True
            )
            sample_folds_by_source["joint_residual_pls_knn_logitresid"].append(
                (target_i, weighted_knn_residual(rz_fit, rz_sample, y_fit, base_fit, base_test, args.knn_k, args.knn_temp, True))
            )
            fit_keys = train.iloc[fold.train_idx][KEY_COLUMNS]
            val_keys = train.iloc[fold.val_idx][KEY_COLUMNS]
            sample_keys = sample[KEY_COLUMNS]
            oof_by_source["joint_attention_knn_resid"][fold.val_idx, target_i] = attention_knn_residual(
                z_fit, z_val, y_fit, base_fit, base_val, fit_keys, val_keys, None, args.knn_k, args.knn_temp, False
            )
            sample_folds_by_source["joint_attention_knn_resid"].append(
                (
                    target_i,
                    attention_knn_residual(z_fit, z_sample, y_fit, base_fit, base_test, fit_keys, sample_keys, None, args.knn_k, args.knn_temp, False),
                )
            )
            oof_by_source["joint_attention_knn_logitresid"][fold.val_idx, target_i] = attention_knn_residual(
                z_fit, z_val, y_fit, base_fit, base_val, fit_keys, val_keys, None, args.knn_k, args.knn_temp, True
            )
            sample_folds_by_source["joint_attention_knn_logitresid"].append(
                (
                    target_i,
                    attention_knn_residual(z_fit, z_sample, y_fit, base_fit, base_test, fit_keys, sample_keys, None, args.knn_k, args.knn_temp, True),
                )
            )
            oof_by_source["joint_metric_attention_knn_resid"][fold.val_idx, target_i] = attention_knn_residual(
                z_fit, z_val, y_fit, base_fit, base_val, fit_keys, val_keys, metric_weights, args.knn_k, args.knn_temp, False
            )
            sample_folds_by_source["joint_metric_attention_knn_resid"].append(
                (
                    target_i,
                    attention_knn_residual(
                        z_fit, z_sample, y_fit, base_fit, base_test, fit_keys, sample_keys, metric_weights, args.knn_k, args.knn_temp, False
                    ),
                )
            )
            oof_by_source["joint_metric_attention_knn_logitresid"][fold.val_idx, target_i] = attention_knn_residual(
                z_fit, z_val, y_fit, base_fit, base_val, fit_keys, val_keys, metric_weights, args.knn_k, args.knn_temp, True
            )
            sample_folds_by_source["joint_metric_attention_knn_logitresid"].append(
                (
                    target_i,
                    attention_knn_residual(
                        z_fit, z_sample, y_fit, base_fit, base_test, fit_keys, sample_keys, metric_weights, args.knn_k, args.knn_temp, True
                    ),
                )
            )
            fit_neighbor = neighbor_context_features(
                z_fit, z_fit, y_fit, base_fit, base_fit, fit_keys, fit_keys, None, args.knn_k, args.knn_temp, exclude_self=True
            )
            val_neighbor = neighbor_context_features(
                z_fit, z_val, y_fit, base_fit, base_val, fit_keys, val_keys, None, args.knn_k, args.knn_temp
            )
            sample_neighbor = neighbor_context_features(
                z_fit, z_sample, y_fit, base_fit, base_test, fit_keys, sample_keys, None, args.knn_k, args.knn_temp
            )
            fit_metric_neighbor = neighbor_context_features(
                z_fit, z_fit, y_fit, base_fit, base_fit, fit_keys, fit_keys, metric_weights, args.knn_k, args.knn_temp, exclude_self=True
            )
            val_metric_neighbor = neighbor_context_features(
                z_fit, z_val, y_fit, base_fit, base_val, fit_keys, val_keys, metric_weights, args.knn_k, args.knn_temp
            )
            sample_metric_neighbor = neighbor_context_features(
                z_fit, z_sample, y_fit, base_fit, base_test, fit_keys, sample_keys, metric_weights, args.knn_k, args.knn_temp
            )
            fit_residual_metric_neighbor = neighbor_context_features(
                z_fit,
                z_fit,
                y_fit,
                base_fit,
                base_fit,
                fit_keys,
                fit_keys,
                residual_weights,
                args.knn_k,
                args.knn_temp,
                exclude_self=True,
            )
            val_residual_metric_neighbor = neighbor_context_features(
                z_fit, z_val, y_fit, base_fit, base_val, fit_keys, val_keys, residual_weights, args.knn_k, args.knn_temp
            )
            sample_residual_metric_neighbor = neighbor_context_features(
                z_fit, z_sample, y_fit, base_fit, base_test, fit_keys, sample_keys, residual_weights, args.knn_k, args.knn_temp
            )
            fit_residual_contrast = residual_contrast_features(z_fit, z_fit, y_fit, base_fit, base_fit, residual_weights)
            val_residual_contrast = residual_contrast_features(z_fit, z_val, y_fit, base_fit, base_val, residual_weights)
            sample_residual_contrast = residual_contrast_features(z_fit, z_sample, y_fit, base_fit, base_test, residual_weights)
            fit_residual_pls_local = local_decoder_features(
                rz_fit, rz_fit, y_fit, base_fit, base_fit, args.knn_k, args.knn_temp, exclude_self=True
            )
            val_residual_pls_local = local_decoder_features(rz_fit, rz_val, y_fit, base_fit, base_val, args.knn_k, args.knn_temp)
            sample_residual_pls_local = local_decoder_features(rz_fit, rz_sample, y_fit, base_fit, base_test, args.knn_k, args.knn_temp)
            fit_residual_pls_neighbor = neighbor_context_features(
                rz_fit, rz_fit, y_fit, base_fit, base_fit, fit_keys, fit_keys, None, args.knn_k, args.knn_temp, exclude_self=True
            )
            val_residual_pls_neighbor = neighbor_context_features(
                rz_fit, rz_val, y_fit, base_fit, base_val, fit_keys, val_keys, None, args.knn_k, args.knn_temp
            )
            sample_residual_pls_neighbor = neighbor_context_features(
                rz_fit, rz_sample, y_fit, base_fit, base_test, fit_keys, sample_keys, None, args.knn_k, args.knn_temp
            )
            for method in ("local_logreg", "local_hgb"):
                suffix = "logreg" if method == "local_logreg" else "hgb"
                val_pred, sample_pred = fit_local_decoder(method, fit_neighbor, y_fit, val_neighbor, sample_neighbor)
                source_name = f"joint_neighbor_{suffix}"
                oof_by_source[source_name][fold.val_idx, target_i] = val_pred
                sample_folds_by_source[source_name].append((target_i, sample_pred))

                val_pred, sample_pred = fit_local_decoder(
                    method,
                    fit_metric_neighbor,
                    y_fit,
                    val_metric_neighbor,
                    sample_metric_neighbor,
                )
                source_name = f"joint_metric_neighbor_{suffix}"
                oof_by_source[source_name][fold.val_idx, target_i] = val_pred
                sample_folds_by_source[source_name].append((target_i, sample_pred))

                val_pred, sample_pred = fit_local_decoder(
                    method,
                    fit_residual_metric_neighbor,
                    y_fit,
                    val_residual_metric_neighbor,
                    sample_residual_metric_neighbor,
                )
                source_name = f"joint_residual_metric_neighbor_{suffix}"
                oof_by_source[source_name][fold.val_idx, target_i] = val_pred
                sample_folds_by_source[source_name].append((target_i, sample_pred))

                val_pred, sample_pred = fit_local_decoder(
                    method,
                    fit_residual_contrast,
                    y_fit,
                    val_residual_contrast,
                    sample_residual_contrast,
                )
                source_name = f"joint_residual_contrast_{suffix}"
                oof_by_source[source_name][fold.val_idx, target_i] = val_pred
                sample_folds_by_source[source_name].append((target_i, sample_pred))

                val_pred, sample_pred = fit_local_decoder(
                    method,
                    fit_residual_pls_local,
                    y_fit,
                    val_residual_pls_local,
                    sample_residual_pls_local,
                )
                source_name = f"joint_residual_pls_local_{suffix}"
                oof_by_source[source_name][fold.val_idx, target_i] = val_pred
                sample_folds_by_source[source_name].append((target_i, sample_pred))

                val_pred, sample_pred = fit_local_decoder(
                    method,
                    fit_residual_pls_neighbor,
                    y_fit,
                    val_residual_pls_neighbor,
                    sample_residual_pls_neighbor,
                )
                source_name = f"joint_residual_pls_neighbor_{suffix}"
                oof_by_source[source_name][fold.val_idx, target_i] = val_pred
                sample_folds_by_source[source_name].append((target_i, sample_pred))

            fit_local = local_decoder_features(z_fit, z_fit, y_fit, base_fit, base_fit, args.knn_k, args.knn_temp, exclude_self=True)
            val_local = local_decoder_features(z_fit, z_val, y_fit, base_fit, base_val, args.knn_k, args.knn_temp)
            sample_local = local_decoder_features(z_fit, z_sample, y_fit, base_fit, base_test, args.knn_k, args.knn_temp)
            for method in ("local_logreg", "local_hgb"):
                val_pred, sample_pred = fit_local_decoder(method, fit_local, y_fit, val_local, sample_local)
                source_name = f"joint_{method}"
                oof_by_source[source_name][fold.val_idx, target_i] = val_pred
                sample_folds_by_source[source_name].append((target_i, sample_pred))
            proto_mix_val = np.clip(
                0.80 * base_val + 0.10 * val_local[:, 2] + 0.05 * val_local[:, 3] + 0.05 * val_local[:, 6],
                EPS,
                1.0 - EPS,
            )
            proto_mix_sample = np.clip(
                0.80 * base_test + 0.10 * sample_local[:, 2] + 0.05 * sample_local[:, 3] + 0.05 * sample_local[:, 6],
                EPS,
                1.0 - EPS,
            )
            oof_by_source["joint_proto_mix"][fold.val_idx, target_i] = proto_mix_val
            sample_folds_by_source["joint_proto_mix"].append((target_i, proto_mix_sample))

    base_avg, base_targets = average_log_loss(y_df, base_train)
    source_rows: list[dict[str, object]] = []
    source_paths: list[dict[str, object]] = []
    latent_sample = np.mean(latent_sample_folds, axis=0)
    latent_train_df = train[KEY_COLUMNS].copy()
    latent_sample_df = sample[KEY_COLUMNS].copy()
    for i in range(latent_oof.shape[1]):
        latent_train_df[f"z_{i:02d}"] = latent_oof[:, i]
        latent_sample_df[f"z_{i:02d}"] = latent_sample[:, i]
    latent_train_df.to_parquet(output_dir / "joint_state_space_latents_train.parquet", index=False)
    latent_sample_df.to_parquet(output_dir / "joint_state_space_latents_sample.parquet", index=False)

    for name in source_names:
        if np.isnan(oof_by_source[name]).any():
            raise RuntimeError(f"{name} has missing OOF predictions")
        sample_pred = np.zeros_like(base_sample)
        counts = np.zeros_like(base_sample)
        for target_i, pred in sample_folds_by_source[name]:
            sample_pred[:, target_i] += pred
            counts[:, target_i] += 1.0
        sample_pred = np.divide(sample_pred, np.maximum(counts, 1.0))
        avg, per_target = average_log_loss(y_df, oof_by_source[name])
        pack = SourcePack(name=name, oof=oof_by_source[name], sample=sample_pred, avg_log_loss=avg, target_log_loss=per_target)
        oof_path, sub_path = write_source(output_dir, train, sample, pack)
        row = {"name": name, "avg_log_loss": avg, **per_target}
        source_rows.append(row)
        source_paths.append({"name": name, "oof": str(oof_path), "submission": str(sub_path), **row})

    scores = pd.DataFrame([{"name": "base", "avg_log_loss": base_avg, **base_targets}, *source_rows]).sort_values("avg_log_loss")
    scores.to_csv(output_dir / "score.csv", index=False)
    report = {
        "base_avg_log_loss": base_avg,
        "best_avg_log_loss": float(scores.iloc[0]["avg_log_loss"]),
        "best_source": str(scores.iloc[0]["name"]),
        "sources": source_paths,
        "fold_meta": fold_meta,
        "feature_groups": groups,
        "selected_columns": len(columns),
        "args": vars(args),
    }
    (output_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = [
        "# Joint state-space encoder",
        "",
        f"- Base OOF: `{base_avg:.6f}`",
        f"- Best source: `{report['best_source']}`",
        f"- Best source OOF: `{report['best_avg_log_loss']:.6f}`",
        f"- Selected raw columns: `{len(columns)}`",
        "",
        "## Scores",
        "",
        dataframe_to_markdown(scores),
        "",
        "## Fold Latent Meta",
        "",
        dataframe_to_markdown(pd.DataFrame(fold_meta)),
    ]
    (output_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"base={base_avg:.6f} best={report['best_avg_log_loss']:.6f} source={report['best_source']}")
    print(f"saved: {output_dir / 'report.md'}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a common label-aligned personal state-space latent with seven heads.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--base-oof", default="outputs/conditional_latent_routing_v53_integrated_state_space_on_v52/oof_conditional_latent_routing.csv")
    parser.add_argument("--base-submission", default="outputs/conditional_latent_routing_v53_integrated_state_space_on_v52/submission_conditional_latent_routing.csv")
    parser.add_argument("--output-dir", default="outputs/joint_state_space_encoder_v1_on_v53")
    parser.add_argument("--groups", default="temporal_state_transition,temporal_state_recurrence,temporal_state_novelty,temporal_state_novelty_recovery")
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--max-features", type=int, default=420)
    parser.add_argument("--pca-dim", type=int, default=32)
    parser.add_argument("--pls-dim", type=int, default=7)
    parser.add_argument("--residual-pls-dim", type=int, default=7)
    parser.add_argument("--knn-k", type=int, default=19)
    parser.add_argument("--knn-temp", type=float, default=1.2)
    return parser.parse_args()


def main() -> None:
    train_joint_encoder(parse_args())


if __name__ == "__main__":
    main()
