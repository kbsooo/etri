#!/usr/bin/env python3
"""Public-free real-data evidence for the HS-JEPA core.

This runner does not generate a competition submission and does not read the
public LB ledger. It asks whether an HS-JEPA-style human-state representation,
derived from OG lifelog context, is useful before any leaderboard-facing
adapter is attached.
"""

from __future__ import annotations

import json
import math
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import (
    average_precision_score,
    log_loss,
    r2_score,
    roc_auc_score,
)
from sklearn.model_selection import GroupKFold
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "lifelog_core_state_evidence"
FEATURE_PATH = ROOT / "team_experiments" / "cohort_hsjepa" / "cohort_human_state_features.csv"
FEATURE_BUILDER = ROOT / "team_experiments" / "cohort_hsjepa" / "cohort_hsjepa_experiment.py"
LABEL_PATH = ROOT / "data" / "ch2026_metrics_train.csv"
TEACHER_CELL_PATH = ROOT / "sleep_competition_adapter" / "outputs" / "og_only_assignment_teacher_ranked_cells.csv"

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
NULL_REPEATS = 32
KEY_COLS = {
    "subject_id",
    "sleep_date",
    "lifelog_date",
    "split",
    "metric_row",
    "lifelog_date_str",
}
LABEL_INFORMED_PREFIXES = (
    "peer_margin_",
    "q_group_peer_margin",
    "s_group_peer_margin",
    "target_route_margin",
)
CORE_COHORT_COLS = [
    "peer_group",
    "dist_to_subject_normal",
    "dist_to_peer_normal",
    "subject_minus_peer_dist",
    "subject_outlier_rank",
    "peer_outlier_rank",
    "cohort_outlier_score",
]
CALENDAR_COLS = [
    "dayofweek",
    "is_weekend",
    "dayofmonth",
    "month_start_proximity",
    "month_end",
]


@dataclass(frozen=True)
class FeatureCatalog:
    latent: list[str]
    core_state: list[str]
    raw_numeric: list[str]
    calendar: list[str]
    label_informed: list[str]


def rank01(values: Iterable[float]) -> np.ndarray:
    arr = pd.Series(values, dtype="float64")
    if arr.notna().sum() <= 1:
        return np.zeros(len(arr), dtype=np.float64)
    ranked = arr.rank(method="average", pct=True).to_numpy(dtype=np.float64)
    return np.nan_to_num(ranked, nan=0.5)


def safe_auc(y_true: np.ndarray, score: np.ndarray) -> float | None:
    y_true = np.asarray(y_true, dtype=int)
    score = np.asarray(score, dtype=float)
    if len(np.unique(y_true)) < 2:
        return None
    return float(roc_auc_score(y_true, score))


def safe_average_precision(y_true: np.ndarray, score: np.ndarray) -> float | None:
    y_true = np.asarray(y_true, dtype=int)
    score = np.asarray(score, dtype=float)
    if len(np.unique(y_true)) < 2:
        return None
    return float(average_precision_score(y_true, score))


def ensure_feature_table() -> None:
    if FEATURE_PATH.exists():
        return
    subprocess.run(["python3", str(FEATURE_BUILDER)], cwd=ROOT, check=True)


def load_frames() -> tuple[pd.DataFrame, pd.DataFrame]:
    ensure_feature_table()
    features = pd.read_csv(FEATURE_PATH)
    labels = pd.read_csv(LABEL_PATH)
    train_mask = features["split"].eq("train")
    if int(train_mask.sum()) != len(labels):
        raise ValueError(
            f"train feature rows ({int(train_mask.sum())}) do not match label rows ({len(labels)})"
        )
    features = features.copy()
    features.loc[train_mask, TARGETS] = labels[TARGETS].to_numpy()
    return features, labels


def catalog_features(frame: pd.DataFrame) -> FeatureCatalog:
    numeric_cols = [
        col
        for col in frame.columns
        if pd.api.types.is_numeric_dtype(frame[col])
        and col not in KEY_COLS
        and col not in TARGETS
    ]
    latent = [col for col in numeric_cols if col.startswith("human_state_latent_")]
    label_informed = [
        col for col in numeric_cols if col.startswith(LABEL_INFORMED_PREFIXES)
    ]
    core_state = latent + [col for col in CORE_COHORT_COLS if col in frame.columns]
    raw_numeric = [
        col
        for col in numeric_cols
        if col not in core_state
        and col not in label_informed
        and col not in {"peer_group"}
    ]
    calendar = [col for col in CALENDAR_COLS if col in raw_numeric]
    return FeatureCatalog(
        latent=latent,
        core_state=core_state,
        raw_numeric=raw_numeric,
        calendar=calendar,
        label_informed=label_informed,
    )


def finite_matrix(frame: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    x = frame[cols].replace([np.inf, -np.inf], np.nan)
    return x


def cv_label_probe(frame: pd.DataFrame, catalog: FeatureCatalog) -> tuple[pd.DataFrame, pd.DataFrame]:
    train = frame[frame["split"].eq("train")].reset_index(drop=True)
    groups = train["subject_id"].astype(str).to_numpy()
    n_splits = max(2, min(5, len(np.unique(groups))))
    splitter = GroupKFold(n_splits=n_splits)
    feature_sets = {
        "prior_only": ([], "prior"),
        "calendar_rhythm_linear": (catalog.calendar, "linear"),
        "raw_lifelog_views_linear": (catalog.raw_numeric, "linear"),
        "hsjepa_state_only_linear": (catalog.core_state, "linear"),
        "raw_plus_hsjepa_state_linear": (sorted(set(catalog.raw_numeric + catalog.core_state)), "linear"),
        "hsjepa_state_only_tree": (catalog.core_state, "tree"),
        "raw_plus_hsjepa_state_tree": (sorted(set(catalog.raw_numeric + catalog.core_state)), "tree"),
    }

    prediction_rows: list[dict[str, object]] = []
    metric_rows: list[dict[str, object]] = []
    y_all = train[TARGETS].astype(int)

    for feature_name, (cols, model_kind) in feature_sets.items():
        oof = pd.DataFrame(index=train.index, columns=TARGETS, dtype=float)
        for fold, (tr_idx, va_idx) in enumerate(splitter.split(train, groups=groups)):
            for target in TARGETS:
                y_train = y_all.iloc[tr_idx][target].to_numpy(dtype=int)
                y_val = y_all.iloc[va_idx][target].to_numpy(dtype=int)
                prior = float(np.clip(y_train.mean(), 1e-4, 1 - 1e-4))
                if model_kind == "prior" or len(np.unique(y_train)) < 2 or not cols:
                    pred = np.full(len(va_idx), prior, dtype=float)
                else:
                    if model_kind == "tree":
                        model = make_pipeline(
                            SimpleImputer(strategy="median"),
                            HistGradientBoostingClassifier(
                                learning_rate=0.035,
                                max_leaf_nodes=6,
                                l2_regularization=0.35,
                                random_state=20260612 + fold,
                            ),
                        )
                    else:
                        model = make_pipeline(
                            SimpleImputer(strategy="median"),
                            StandardScaler(),
                            LogisticRegression(
                                C=0.35,
                                max_iter=5000,
                                solver="lbfgs",
                            ),
                        )
                    model.fit(finite_matrix(train.iloc[tr_idx], cols), y_train)
                    pred = model.predict_proba(finite_matrix(train.iloc[va_idx], cols))[:, 1]
                    pred = np.clip(pred, 1e-5, 1 - 1e-5)
                oof.loc[va_idx, target] = pred
                prediction_rows.extend(
                    {
                        "feature_set": feature_name,
                        "fold": fold,
                        "row": int(row),
                        "target": target,
                        "y": int(y_val[pos]),
                        "prediction": float(pred[pos]),
                    }
                    for pos, row in enumerate(va_idx)
                )

        losses = {}
        aucs = {}
        for target in TARGETS:
            y = y_all[target].to_numpy(dtype=int)
            p = oof[target].to_numpy(dtype=float)
            losses[target] = float(log_loss(y, p, labels=[0, 1]))
            aucs[target] = safe_auc(y, p)
            metric_rows.append(
                {
                    "test": "grouped_label_probe",
                    "feature_set": feature_name,
                    "target": target,
                    "metric": "logloss",
                    "value": losses[target],
                    "uses_public_score": False,
                    "uses_label_informed_features": False,
                }
            )
            metric_rows.append(
                {
                    "test": "grouped_label_probe",
                    "feature_set": feature_name,
                    "target": target,
                    "metric": "auc",
                    "value": aucs[target],
                    "uses_public_score": False,
                    "uses_label_informed_features": False,
                }
            )
        metric_rows.append(
            {
                "test": "grouped_label_probe",
                "feature_set": feature_name,
                "target": "all",
                "metric": "mean_logloss",
                "value": float(np.mean(list(losses.values()))),
                "uses_public_score": False,
                "uses_label_informed_features": False,
            }
        )
        metric_rows.append(
            {
                "test": "grouped_label_probe",
                "feature_set": feature_name,
                "target": "all",
                "metric": "mean_auc",
                "value": float(np.nanmean([v for v in aucs.values() if v is not None])),
                "uses_public_score": False,
                "uses_label_informed_features": False,
            }
        )

    return pd.DataFrame(metric_rows), pd.DataFrame(prediction_rows)


def view_columns(catalog: FeatureCatalog) -> dict[str, list[str]]:
    raw = set(catalog.raw_numeric)
    prefixes = {
        "calendar_rhythm": tuple(CALENDAR_COLS),
        "phone_behavior": (
            "phone_charging_",
            "screen_use_",
            "phone_activity_",
            "phone_light_",
            "watch_light_",
        ),
        "body_activity_sleep": (
            "pedo_",
            "step_",
            "walking_",
            "running_",
            "distance_",
            "calories_",
            "speed_",
            "active_",
            "night_step_",
            "hr_",
        ),
        "app_social_context": ("usage_", "night_usage_"),
        "mobility_environment": ("gps_", "wifi_", "ble_", "ambience_"),
    }
    views: dict[str, list[str]] = {}
    for name, pref in prefixes.items():
        if name == "calendar_rhythm":
            cols = [col for col in CALENDAR_COLS if col in raw]
        else:
            cols = [col for col in catalog.raw_numeric if col.startswith(pref)]
        if len(cols) >= 2:
            views[name] = cols
    return views


def component_correlation(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    values = []
    for idx in range(y_true.shape[1]):
        a = y_true[:, idx]
        b = y_pred[:, idx]
        if np.std(a) <= 1e-12 or np.std(b) <= 1e-12:
            continue
        values.append(float(np.corrcoef(a, b)[0, 1]))
    return float(np.nanmean(values)) if values else float("nan")


def masked_view_prediction(frame: pd.DataFrame, catalog: FeatureCatalog) -> pd.DataFrame:
    views = view_columns(catalog)
    all_view_cols = sorted({col for cols in views.values() for col in cols})
    groups = frame["subject_id"].astype(str).to_numpy()
    n_splits = max(2, min(5, len(np.unique(groups))))
    splitter = GroupKFold(n_splits=n_splits)
    rows: list[dict[str, object]] = []
    rng = np.random.default_rng(20260612)

    for target_view, y_cols in views.items():
        x_cols = [col for col in all_view_cols if col not in set(y_cols)]
        if len(x_cols) < 2:
            continue
        r2_values = []
        null_values = []
        corr_values = []
        null_corr_values = []
        for tr_idx, va_idx in splitter.split(frame, groups=groups):
            x_train_raw = finite_matrix(frame.iloc[tr_idx], x_cols)
            x_val_raw = finite_matrix(frame.iloc[va_idx], x_cols)
            y_train_raw = finite_matrix(frame.iloc[tr_idx], y_cols)
            y_val_raw = finite_matrix(frame.iloc[va_idx], y_cols)

            x_imp = SimpleImputer(strategy="median")
            x_scaler = StandardScaler()
            x_train = x_scaler.fit_transform(x_imp.fit_transform(x_train_raw))
            x_val = x_scaler.transform(x_imp.transform(x_val_raw))

            y_imp = SimpleImputer(strategy="median")
            y_scaler = StandardScaler()
            y_train_scaled = y_scaler.fit_transform(y_imp.fit_transform(y_train_raw))
            y_val_scaled = y_scaler.transform(y_imp.transform(y_val_raw))
            dims = max(1, min(4, y_train_scaled.shape[1], y_train_scaled.shape[0] - 1))
            pca = PCA(n_components=dims, random_state=20260612)
            y_train = pca.fit_transform(y_train_scaled)
            y_val = pca.transform(y_val_scaled)

            model = Ridge(alpha=10.0)
            model.fit(x_train, y_train)
            pred = model.predict(x_val)
            r2_values.append(float(r2_score(y_val, pred, multioutput="variance_weighted")))
            corr_values.append(component_correlation(y_val, pred))

            shuffled = y_train.copy()
            rng.shuffle(shuffled, axis=0)
            null_model = Ridge(alpha=10.0)
            null_model.fit(x_train, shuffled)
            null_pred = null_model.predict(x_val)
            null_values.append(float(r2_score(y_val, null_pred, multioutput="variance_weighted")))
            null_corr_values.append(component_correlation(y_val, null_pred))

        rows.append(
            {
                "test": "masked_context_to_target_view",
                "target_view": target_view,
                "context_view_count": len(views) - 1,
                "context_feature_count": len(x_cols),
                "target_feature_count": len(y_cols),
                "mean_r2": float(np.mean(r2_values)),
                "mean_null_r2": float(np.mean(null_values)),
                "r2_lift_vs_null": float(np.mean(r2_values) - np.mean(null_values)),
                "mean_component_corr": float(np.nanmean(corr_values)),
                "mean_null_component_corr": float(np.nanmean(null_corr_values)),
                "component_corr_lift_vs_null": float(np.nanmean(corr_values) - np.nanmean(null_corr_values)),
                "uses_public_score": False,
                "uses_label_informed_features": False,
            }
        )
    return pd.DataFrame(rows)


def representation_matrix(frame: pd.DataFrame, cols: list[str], dims: int | None = None) -> np.ndarray:
    x = finite_matrix(frame, cols)
    x_imp = SimpleImputer(strategy="median").fit_transform(x)
    x_scaled = StandardScaler().fit_transform(x_imp)
    if dims is not None and x_scaled.shape[1] > dims:
        dims = min(dims, x_scaled.shape[0] - 1, x_scaled.shape[1])
        return PCA(n_components=dims, random_state=20260612).fit_transform(x_scaled)
    return x_scaled


def neighbor_consistency(frame: pd.DataFrame, catalog: FeatureCatalog) -> pd.DataFrame:
    train = frame[frame["split"].eq("train")].reset_index(drop=True)
    labels = train[TARGETS].astype(int).to_numpy()
    reps = {
        "calendar_rhythm": catalog.calendar,
        "raw_lifelog_pca8": catalog.raw_numeric,
        "hsjepa_state_only": catalog.core_state,
    }
    rng = np.random.default_rng(20260612)
    rows: list[dict[str, object]] = []
    for rep_name, cols in reps.items():
        if not cols:
            continue
        x = representation_matrix(train, cols, dims=8 if rep_name == "raw_lifelog_pca8" else None)
        k = min(6, len(train))
        nn = NearestNeighbors(n_neighbors=k, metric="euclidean")
        nn.fit(x)
        _, indices = nn.kneighbors(x)
        indices = indices[:, 1:]
        target_matches = []
        random_matches = []
        for i in range(len(train)):
            neighbor_match = (labels[indices[i]] == labels[i]).mean(axis=0)
            random_idx = rng.choice([j for j in range(len(train)) if j != i], size=indices.shape[1], replace=False)
            random_match = (labels[random_idx] == labels[i]).mean(axis=0)
            target_matches.append(neighbor_match)
            random_matches.append(random_match)
        target_arr = np.vstack(target_matches)
        random_arr = np.vstack(random_matches)
        for target_idx, target in enumerate(TARGETS):
            rows.append(
                {
                    "test": "nearest_neighbor_label_consistency",
                    "representation": rep_name,
                    "target": target,
                    "neighbor_match_rate": float(target_arr[:, target_idx].mean()),
                    "random_match_rate": float(random_arr[:, target_idx].mean()),
                    "lift": float(target_arr[:, target_idx].mean() - random_arr[:, target_idx].mean()),
                    "uses_public_score": False,
                    "uses_label_informed_features": False,
                }
            )
        rows.append(
            {
                "test": "nearest_neighbor_label_consistency",
                "representation": rep_name,
                "target": "all",
                "neighbor_match_rate": float(target_arr.mean()),
                "random_match_rate": float(random_arr.mean()),
                "lift": float(target_arr.mean() - random_arr.mean()),
                "uses_public_score": False,
                "uses_label_informed_features": False,
            }
        )
    return pd.DataFrame(rows)


def outlier_target_shift(frame: pd.DataFrame) -> pd.DataFrame:
    train = frame[frame["split"].eq("train")].reset_index(drop=True)
    rows: list[dict[str, object]] = []
    for score_col in ["dist_to_subject_normal", "dist_to_peer_normal", "cohort_outlier_score"]:
        if score_col not in train.columns:
            continue
        score = pd.to_numeric(train[score_col], errors="coerce")
        lo = score <= score.quantile(0.25)
        hi = score >= score.quantile(0.75)
        for target in TARGETS:
            low_rate = float(train.loc[lo, target].mean())
            high_rate = float(train.loc[hi, target].mean())
            rows.append(
                {
                    "test": "human_state_outlier_target_shift",
                    "score": score_col,
                    "target": target,
                    "low_quantile_rate": low_rate,
                    "high_quantile_rate": high_rate,
                    "absolute_shift": abs(high_rate - low_rate),
                    "direction": "higher_in_outliers" if high_rate > low_rate else "lower_in_outliers",
                    "uses_public_score": False,
                    "uses_label_informed_features": False,
                }
            )
        rows.append(
            {
                "test": "human_state_outlier_target_shift",
                "score": score_col,
                "target": "all",
                "low_quantile_rate": float(train.loc[lo, TARGETS].mean().mean()),
                "high_quantile_rate": float(train.loc[hi, TARGETS].mean().mean()),
                "absolute_shift": float(
                    np.abs(train.loc[hi, TARGETS].mean() - train.loc[lo, TARGETS].mean()).mean()
                ),
                "direction": "mixed",
                "uses_public_score": False,
                "uses_label_informed_features": False,
            }
        )
    return pd.DataFrame(rows)


def recall_at_k(y_true: np.ndarray, score: np.ndarray) -> float | None:
    positives = int(np.asarray(y_true).sum())
    if positives <= 0:
        return None
    k = min(positives, len(y_true))
    selected = np.argsort(-np.asarray(score, dtype=float))[:k]
    return float(np.asarray(y_true, dtype=int)[selected].sum() / positives)


def external_action_replay(frame: pd.DataFrame, catalog: FeatureCatalog) -> pd.DataFrame:
    if not TEACHER_CELL_PATH.exists():
        return pd.DataFrame()
    cells = pd.read_csv(TEACHER_CELL_PATH)
    test = frame[frame["split"].eq("test")].copy().reset_index(drop=True)
    if "metric_row" not in test.columns:
        test["metric_row"] = np.arange(len(test))

    row_labels = (
        cells.groupby(["teacher", "row"], observed=True)["teacher_row_has_action"]
        .max()
        .reset_index()
    )
    teachers = sorted(row_labels["teacher"].unique())
    if len(teachers) < 2:
        return pd.DataFrame()

    feature_sets = {
        "core_state_geometry": catalog.core_state,
        "raw_lifelog_context": catalog.raw_numeric,
        "core_plus_raw_context": sorted(set(catalog.core_state + catalog.raw_numeric)),
        "label_informed_adapter_context": sorted(set(catalog.core_state + catalog.label_informed)),
    }
    rows: list[dict[str, object]] = []
    rng = np.random.default_rng(20260612)

    for train_teacher in teachers:
        for test_teacher in teachers:
            if train_teacher == test_teacher:
                continue
            y_train_map = row_labels[row_labels["teacher"].eq(train_teacher)].set_index("row")[
                "teacher_row_has_action"
            ]
            y_test_map = row_labels[row_labels["teacher"].eq(test_teacher)].set_index("row")[
                "teacher_row_has_action"
            ]
            y_train = test["metric_row"].map(y_train_map).fillna(0).astype(int).to_numpy()
            y_test = test["metric_row"].map(y_test_map).fillna(0).astype(int).to_numpy()
            for feature_name, cols in feature_sets.items():
                if not cols or len(np.unique(y_train)) < 2:
                    continue
                model = make_pipeline(
                    SimpleImputer(strategy="median"),
                    StandardScaler(),
                    HistGradientBoostingClassifier(
                        learning_rate=0.04,
                        max_leaf_nodes=8,
                        l2_regularization=0.2,
                        random_state=20260612,
                    ),
                )
                x = finite_matrix(test, cols)
                model.fit(x, y_train)
                score = model.predict_proba(x)[:, 1]
                auc = safe_auc(y_test, score)
                ap = safe_average_precision(y_test, score)
                ratk = recall_at_k(y_test, score)

                null_aucs = []
                for _ in range(NULL_REPEATS):
                    shuffled = y_train.copy()
                    rng.shuffle(shuffled)
                    null_model = make_pipeline(
                        SimpleImputer(strategy="median"),
                        StandardScaler(),
                        HistGradientBoostingClassifier(
                            learning_rate=0.04,
                            max_leaf_nodes=8,
                            l2_regularization=0.2,
                            random_state=int(rng.integers(0, 1_000_000)),
                        ),
                    )
                    null_model.fit(x, shuffled)
                    null_score = null_model.predict_proba(x)[:, 1]
                    null_auc = safe_auc(y_test, null_score)
                    if null_auc is not None and math.isfinite(null_auc):
                        null_aucs.append(null_auc)
                null_mean = float(np.mean(null_aucs)) if null_aucs else None
                null_std = float(np.std(null_aucs)) if null_aucs else None
                rows.append(
                    {
                        "test": "external_adapter_action_replay",
                        "train_teacher": train_teacher,
                        "test_teacher": test_teacher,
                        "feature_set": feature_name,
                        "feature_count": len(cols),
                        "row_auc": auc,
                        "row_average_precision": ap,
                        "row_recall_at_k": ratk,
                        "null_auc_mean": null_mean,
                        "auc_z_vs_permuted_train": (
                            None
                            if auc is None or null_mean is None or not null_std or null_std <= 1e-12
                            else float((auc - null_mean) / null_std)
                        ),
                        "uses_public_score": False,
                        "uses_label_informed_features": feature_name == "label_informed_adapter_context",
                    }
                )
    return pd.DataFrame(rows)


def format_float(value: object, digits: int = 4) -> str:
    if value is None:
        return "NA"
    try:
        if pd.isna(value):
            return "NA"
    except TypeError:
        pass
    return f"{float(value):.{digits}f}"


def markdown_table(df: pd.DataFrame, columns: list[str], max_rows: int = 20) -> str:
    if df.empty:
        return "_No rows._"
    small = df.loc[:, columns].head(max_rows).copy()
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for _, row in small.iterrows():
        vals = []
        for col in columns:
            val = row[col]
            if isinstance(val, float):
                vals.append(format_float(val, 6))
            else:
                vals.append(str(val))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def build_summary(
    label_metrics: pd.DataFrame,
    masked: pd.DataFrame,
    neighbors: pd.DataFrame,
    outliers: pd.DataFrame,
    replay: pd.DataFrame,
    catalog: FeatureCatalog,
) -> dict[str, object]:
    label_mean = label_metrics[
        label_metrics["metric"].eq("mean_logloss") & label_metrics["target"].eq("all")
    ][["feature_set", "value"]].sort_values("value")
    prior_value = float(label_mean[label_mean["feature_set"].eq("prior_only")]["value"].iloc[0])
    state_rows = label_mean[label_mean["feature_set"].str.startswith("hsjepa_state_only")]
    raw_rows = label_mean[label_mean["feature_set"].str.startswith("raw_lifelog_views")]
    state_value = float(state_rows["value"].min()) if len(state_rows) else None
    raw_value = float(raw_rows["value"].min()) if len(raw_rows) else None

    neighbor_all = neighbors[neighbors["target"].eq("all")].copy()
    state_neighbor = neighbor_all[neighbor_all["representation"].eq("hsjepa_state_only")]
    best_masked = masked.sort_values("r2_lift_vs_null", ascending=False).head(1)
    core_replay = replay[
        replay["feature_set"].eq("core_state_geometry")
        & replay["uses_label_informed_features"].eq(False)
    ].copy()

    return {
        "status": "core_real_data_evidence_ready",
        "uses_public_score_ledger": False,
        "uses_proprietary_embedding_api": False,
        "feature_source": str(FEATURE_PATH.relative_to(ROOT)),
        "raw_feature_count": len(catalog.raw_numeric),
        "core_state_feature_count": len(catalog.core_state),
        "label_informed_features_excluded_from_core": catalog.label_informed,
        "external_action_replay_null_repeats": NULL_REPEATS,
        "label_probe": {
            "prior_mean_logloss": prior_value,
            "hsjepa_state_mean_logloss": state_value,
            "raw_lifelog_mean_logloss": raw_value,
            "hsjepa_state_delta_vs_prior": None if state_value is None else state_value - prior_value,
            "raw_lifelog_delta_vs_prior": None if raw_value is None else raw_value - prior_value,
        },
        "neighbor_consistency": (
            {}
            if state_neighbor.empty
            else {
                "hsjepa_state_match_rate": float(state_neighbor["neighbor_match_rate"].iloc[0]),
                "random_match_rate": float(state_neighbor["random_match_rate"].iloc[0]),
                "lift": float(state_neighbor["lift"].iloc[0]),
            }
        ),
        "masked_prediction": (
            {}
            if best_masked.empty
            else {
                "best_target_view": str(best_masked["target_view"].iloc[0]),
                "best_r2_lift_vs_null": float(best_masked["r2_lift_vs_null"].iloc[0]),
                "best_mean_r2": float(best_masked["mean_r2"].iloc[0]),
                "best_component_corr_lift_vs_null": float(best_masked["component_corr_lift_vs_null"].iloc[0]),
            }
        ),
        "external_action_replay": (
            {}
            if core_replay.empty
            else {
                "mean_core_row_auc": float(core_replay["row_auc"].mean()),
                "mean_core_row_recall_at_k": float(core_replay["row_recall_at_k"].mean()),
                "mean_core_auc_z_vs_permuted_train": float(core_replay["auc_z_vs_permuted_train"].mean()),
            }
        ),
    }


def build_markdown(
    summary: dict[str, object],
    label_metrics: pd.DataFrame,
    masked: pd.DataFrame,
    neighbors: pd.DataFrame,
    outliers: pd.DataFrame,
    replay: pd.DataFrame,
) -> str:
    label_table = label_metrics[
        label_metrics["target"].eq("all")
        & label_metrics["metric"].isin(["mean_logloss", "mean_auc"])
    ].pivot(index="feature_set", columns="metric", values="value").reset_index()
    label_table = label_table.sort_values("mean_logloss")

    neighbor_table = neighbors[neighbors["target"].eq("all")].sort_values("lift", ascending=False)
    outlier_table = outliers[outliers["target"].ne("all")].sort_values("absolute_shift", ascending=False)
    replay_table = replay.sort_values("row_auc", ascending=False) if not replay.empty else replay

    label_probe = summary["label_probe"]
    neighbor = summary["neighbor_consistency"]
    masked_best = summary["masked_prediction"]
    replay_summary = summary["external_action_replay"]

    return f"""# HS-JEPA Lifelog Core State Evidence

## 목적

이 실험은 public LB나 제출 점수표를 쓰지 않고, OG lifelog에서 만든 HS-JEPA human-state representation이 실제로 인간 생활 상태를 더 잘 표현하는지 확인한다.

핵심 질문은 두 개다.

1. label을 직접 맞히기 전에, raw lifelog context가 보이지 않는 human-state representation으로 압축되는가?
2. 그 representation이 target manifold, masked view prediction, neighbor consistency, external action replay에서 살아남는가?

## 입력과 분리 원칙

- feature source: `{summary["feature_source"]}`
- public score ledger 사용: `{summary["uses_public_score_ledger"]}`
- proprietary embedding API 사용: `{summary["uses_proprietary_embedding_api"]}`
- raw/core feature 수: raw `{summary["raw_feature_count"]}`, core-state `{summary["core_state_feature_count"]}`
- core-only 검증에서 제외한 label-informed feature: `{", ".join(summary["label_informed_features_excluded_from_core"]) or "none"}`

## 핵심 결과

- grouped label probe에서 prior mean logloss는 `{format_float(label_probe["prior_mean_logloss"], 6)}`이고, HS-JEPA state-only mean logloss는 `{format_float(label_probe["hsjepa_state_mean_logloss"], 6)}`이다.
- HS-JEPA state-only의 prior 대비 변화는 `{format_float(label_probe["hsjepa_state_delta_vs_prior"], 6)}`이다. 이 값이 음수이면 label을 직접 쓰지 않은 state representation만으로도 target manifold 일부를 설명한다.
- latent nearest-neighbor target match lift는 `{format_float(neighbor.get("lift"), 6)}`이다.
- masked context prediction에서 가장 잘 살아난 target view는 `{masked_best.get("best_target_view", "NA")}`이고, null 대비 R2 lift는 `{format_float(masked_best.get("best_r2_lift_vs_null"), 6)}`, component-corr lift는 `{format_float(masked_best.get("best_component_corr_lift_vs_null"), 6)}`이다.
- external action replay에서 core-state geometry 평균 row AUC는 `{format_float(replay_summary.get("mean_core_row_auc"), 6)}`, 평균 recall@k는 `{format_float(replay_summary.get("mean_core_row_recall_at_k"), 6)}`이다. 이 항목은 core 학습이 아니라 adapter replay 진단이다.

## Label Manifold Probe

같은 subject가 fold 양쪽에 동시에 들어가지 않도록 GroupKFold로 검증했다.

{markdown_table(label_table, ["feature_set", "mean_logloss", "mean_auc"])}

## Masked Context → Target View Prediction

I-JEPA식으로 한 view를 가리고, 나머지 lifelog view에서 가려진 view의 PCA representation을 예측했다. raw value 복원이 아니라 view-level representation prediction이다.

{markdown_table(masked.sort_values("r2_lift_vs_null", ascending=False), ["target_view", "context_feature_count", "target_feature_count", "mean_r2", "mean_null_r2", "r2_lift_vs_null", "mean_component_corr", "component_corr_lift_vs_null"])}

## Nearest-Neighbor Label Consistency

좋은 human-state latent라면 가까운 이웃의 target vector도 random 이웃보다 더 비슷해야 한다.

{markdown_table(neighbor_table, ["representation", "neighbor_match_rate", "random_match_rate", "lift"])}

## Human-State Outlier Shift

cohort/personal outlier score 상위 25%와 하위 25% 사이에서 target prevalence가 달라지는지 본다.

{markdown_table(outlier_table, ["score", "target", "low_quantile_rate", "high_quantile_rate", "absolute_shift", "direction"], max_rows=14)}

## External Adapter Action Replay

이 부분은 core-only 성능 증명이 아니라 adapter replay다. public score는 쓰지 않지만, 기존 row-action teacher가 고른 row를 외부 label로 두고 core state가 다른 teacher의 row support를 재발견하는지 본다.

{markdown_table(replay_table, ["train_teacher", "test_teacher", "feature_set", "row_auc", "row_average_precision", "row_recall_at_k", "auc_z_vs_permuted_train"], max_rows=16)}

## 해석

이 실험의 논문적 의미는 HS-JEPA가 특정 제출 파일을 만드는 요령이 아니라, 원천 생활 로그를 hidden human-state space로 보내고 그 공간에서 target/action 구조를 읽는 일반 절차라는 점을 검증하는 것이다.

다만 external action replay는 아직 competition adapter 영역이다. 논문 본문에서는 core evidence와 adapter evidence를 분리해서 제시해야 한다.
"""


def run() -> dict[str, object]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frame, _ = load_frames()
    catalog = catalog_features(frame)
    label_metrics, label_predictions = cv_label_probe(frame, catalog)
    masked = masked_view_prediction(frame, catalog)
    neighbors = neighbor_consistency(frame, catalog)
    outliers = outlier_target_shift(frame)
    replay = external_action_replay(frame, catalog)
    summary = build_summary(label_metrics, masked, neighbors, outliers, replay, catalog)

    label_metrics.to_csv(OUT_DIR / "label_probe_metrics.csv", index=False)
    label_predictions.to_csv(OUT_DIR / "label_probe_oof_predictions.csv", index=False)
    masked.to_csv(OUT_DIR / "masked_view_prediction_metrics.csv", index=False)
    neighbors.to_csv(OUT_DIR / "nearest_neighbor_consistency.csv", index=False)
    outliers.to_csv(OUT_DIR / "human_state_outlier_target_shift.csv", index=False)
    replay.to_csv(OUT_DIR / "external_action_replay_metrics.csv", index=False)
    (OUT_DIR / "lifelog_core_state_evidence_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False)
    )
    (OUT_DIR / "lifelog_core_state_evidence_ko.md").write_text(
        build_markdown(summary, label_metrics, masked, neighbors, outliers, replay)
    )
    return summary


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2, ensure_ascii=False))
