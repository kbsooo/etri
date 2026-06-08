#!/usr/bin/env python3
"""Cohort-relative HS-JEPA experiment.

This is a team-facing experiment that combines the cohort-relative human-state
idea with the current HS-JEPA reproduction path without relying on private
version names.

Question:
    If a subject-day is unusual both against the subject's own normal state and
    against a peer cohort's normal state, can that become a useful HS-JEPA
    context view and a safer row-target action-health gate?

Outputs:
    - local CV metrics for sensor-only baseline vs cohort-augmented features
    - test row cohort/action-health scores
    - a diagnostic upload-safe submission derived from the current best
    - a human-readable report
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import json
import math
import re
from typing import Iterable

import numpy as np
import pandas as pd

from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "team_experiments" / "cohort_hsjepa"

KEYS = ["subject_id", "sleep_date", "lifelog_date"]
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
EPS = 1.0e-6

CURRENT_PUBLIC_BEST_FILE = "submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv"
BASELINE_BEFORE_ROW_STATE_FILE = "submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv"
PUBLIC_LISTENER_POSTERIOR_FILE = "hitl/h055_postfeedback_public_listener_jepa/h055_cell_posterior.csv"


@dataclass(frozen=True)
class ExperimentConfig:
    peer_group_count: int = 4
    latent_dims: int = 8
    random_state: int = 42
    candidate_amplify_top_quantile: float = 0.72
    candidate_damp_bottom_quantile: float = 0.35
    candidate_amplify: float = 1.035
    candidate_damp: float = 0.965
    candidate_max_abs_logit_step: float = 1.85


def clip_prob(values: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(values, dtype=np.float64), EPS, 1.0 - EPS)


def logit(values: np.ndarray) -> np.ndarray:
    p = clip_prob(values)
    return np.log(p / (1.0 - p))


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(values, dtype=np.float64)))


def soft_bce(prob: np.ndarray, target_prob: np.ndarray) -> np.ndarray:
    p = clip_prob(prob)
    q = clip_prob(target_prob)
    return -(q * np.log(p) + (1.0 - q) * np.log(1.0 - p))


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def rank01(values: Iterable[float]) -> np.ndarray:
    s = pd.Series(np.asarray(list(values), dtype=np.float64)).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    if s.nunique(dropna=True) <= 1:
        return np.full(len(s), 0.5, dtype=np.float64)
    return s.rank(method="average", pct=True).to_numpy(dtype=np.float64)


def as_list(value: object) -> list:
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return []
    return []


def load_submission(filename: str) -> pd.DataFrame:
    df = pd.read_csv(ROOT / filename, parse_dates=["sleep_date", "lifelog_date"])
    return df.sort_values(KEYS).reset_index(drop=True)


def make_metric_rows() -> pd.DataFrame:
    train = pd.read_csv(ROOT / "data" / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    test = pd.read_csv(ROOT / "data" / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    train["split"] = "train"
    test["split"] = "test"
    train["metric_row"] = np.arange(len(train), dtype=int)
    test["metric_row"] = np.arange(len(test), dtype=int)
    rows = pd.concat([train, test], ignore_index=True, sort=False)
    rows["lifelog_date_str"] = rows["lifelog_date"].dt.strftime("%Y-%m-%d")
    rows["sleep_date_str"] = rows["sleep_date"].dt.strftime("%Y-%m-%d")
    rows["dayofweek"] = rows["lifelog_date"].dt.dayofweek.astype(int)
    rows["is_weekend"] = rows["dayofweek"].isin([5, 6]).astype(int)
    rows["dayofmonth"] = rows["lifelog_date"].dt.day.astype(int)
    rows["month_start_proximity"] = np.minimum(rows["dayofmonth"] - 1, 31 - rows["dayofmonth"]).clip(lower=0)
    rows["month_end"] = rows["lifelog_date"].dt.is_month_end.astype(int)
    return rows


def add_time_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["lifelog_date_str"] = out["timestamp"].dt.strftime("%Y-%m-%d")
    out["hour"] = out["timestamp"].dt.hour
    out["is_night"] = out["hour"].isin([0, 1, 2, 3, 4, 5]).astype(int)
    out["is_evening"] = out["hour"].isin([20, 21, 22, 23]).astype(int)
    out["is_morning"] = out["hour"].isin([6, 7, 8, 9]).astype(int)
    return out


def merge_features(left: pd.DataFrame, right: pd.DataFrame) -> pd.DataFrame:
    if right.empty:
        return left
    return left.merge(right, on=["subject_id", "lifelog_date_str"], how="left")


def aggregate_numeric_file(path: Path, value_col: str, prefix: str) -> pd.DataFrame:
    df = add_time_columns(pd.read_parquet(path)[["subject_id", "timestamp", value_col]])
    df[value_col] = pd.to_numeric(df[value_col], errors="coerce")
    df[f"{prefix}_night_value"] = df[value_col].where(df["is_night"].eq(1))
    df[f"{prefix}_evening_value"] = df[value_col].where(df["is_evening"].eq(1))
    df[f"{prefix}_morning_value"] = df[value_col].where(df["is_morning"].eq(1))
    group = df.groupby(["subject_id", "lifelog_date_str"], observed=True)
    out = group[value_col].agg(
        **{
            f"{prefix}_count": "count",
            f"{prefix}_mean": "mean",
            f"{prefix}_std": "std",
            f"{prefix}_min": "min",
            f"{prefix}_max": "max",
        }
    ).reset_index()
    extra = group[[f"{prefix}_night_value", f"{prefix}_evening_value", f"{prefix}_morning_value"]].mean().reset_index()
    return out.merge(extra, on=["subject_id", "lifelog_date_str"], how="left")


def aggregate_pedo(path: Path) -> pd.DataFrame:
    df = add_time_columns(pd.read_parquet(path))
    for col in ["step", "walking_step", "running_step", "distance", "speed", "burned_calories"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["active_minute"] = (df["step"] > 0).astype(int)
    df["night_step"] = df["step"].where(df["is_night"].eq(1), 0)
    group = df.groupby(["subject_id", "lifelog_date_str"], observed=True)
    return group.agg(
        pedo_rows=("step", "count"),
        step_sum=("step", "sum"),
        walking_step_sum=("walking_step", "sum"),
        running_step_sum=("running_step", "sum"),
        distance_sum=("distance", "sum"),
        calories_sum=("burned_calories", "sum"),
        speed_mean=("speed", "mean"),
        speed_max=("speed", "max"),
        active_minutes=("active_minute", "sum"),
        night_step_sum=("night_step", "sum"),
    ).reset_index()


def aggregate_hr(path: Path) -> pd.DataFrame:
    df = add_time_columns(pd.read_parquet(path))

    def arr_stats(value: object) -> tuple[float, float, float, float, int]:
        arr = pd.to_numeric(pd.Series(as_list(value)), errors="coerce").dropna().to_numpy(dtype=np.float64)
        if len(arr) == 0:
            return np.nan, np.nan, np.nan, np.nan, 0
        return float(arr.mean()), float(arr.std()), float(arr.min()), float(arr.max()), int(len(arr))

    stats = df["heart_rate"].map(arr_stats)
    df["hr_row_mean"] = [x[0] for x in stats]
    df["hr_row_std"] = [x[1] for x in stats]
    df["hr_row_min"] = [x[2] for x in stats]
    df["hr_row_max"] = [x[3] for x in stats]
    df["hr_points"] = [x[4] for x in stats]
    df["hr_night_mean"] = df["hr_row_mean"].where(df["is_night"].eq(1))
    group = df.groupby(["subject_id", "lifelog_date_str"], observed=True)
    return group.agg(
        hr_rows=("hr_row_mean", "count"),
        hr_points=("hr_points", "sum"),
        hr_mean=("hr_row_mean", "mean"),
        hr_std=("hr_row_mean", "std"),
        hr_min=("hr_row_min", "min"),
        hr_max=("hr_row_max", "max"),
        hr_row_variability=("hr_row_std", "mean"),
        hr_night_mean=("hr_night_mean", "mean"),
    ).reset_index()


def aggregate_usage(path: Path) -> pd.DataFrame:
    df = add_time_columns(pd.read_parquet(path))
    patterns = {
        "social": r"카카오|톡|메시지|message|instagram|facebook|라인|line",
        "call": r"통화|전화|call",
        "finance": r"토스|은행|카드|pay|증권|finance|bank|캐시|cash",
        "religion_ritual": r"성경|교회|성당|bible|기도|찬송|묵상",
        "media": r"youtube|유튜브|netflix|티빙|wavve|music|멜론|영상|플레이어",
        "search_browser": r"naver|google|chrome|browser|검색|safari",
        "home_launcher": r"홈|launcher|one ui",
    }

    def row_stats(items: object) -> dict[str, float]:
        rec = {f"usage_{name}_time": 0.0 for name in patterns}
        total = 0.0
        app_count = 0
        times: list[float] = []
        for item in as_list(items):
            if not isinstance(item, dict):
                continue
            name = str(item.get("app_name", "")).lower()
            value = float(item.get("total_time", 0.0) or 0.0)
            total += value
            times.append(value)
            app_count += 1
            for key, pat in patterns.items():
                if re.search(pat, name, flags=re.IGNORECASE):
                    rec[f"usage_{key}_time"] += value
        if total > 0 and times:
            probs = np.asarray(times, dtype=np.float64) / total
            entropy = float(-(probs * np.log(probs + 1e-12)).sum())
        else:
            entropy = 0.0
        rec["usage_total_time"] = total
        rec["usage_app_count"] = float(app_count)
        rec["usage_entropy"] = entropy
        return rec

    stats = pd.DataFrame(df["m_usage_stats"].map(row_stats).tolist())
    stats["subject_id"] = df["subject_id"].to_numpy()
    stats["lifelog_date_str"] = df["lifelog_date_str"].to_numpy()
    stats["is_night"] = df["is_night"].to_numpy()
    for col in [c for c in stats.columns if c.startswith("usage_") and c.endswith("_time")]:
        stats[f"night_{col}"] = stats[col].where(stats["is_night"].eq(1), 0.0)
    group = stats.groupby(["subject_id", "lifelog_date_str"], observed=True)
    agg_map = {col: "sum" for col in stats.columns if col.startswith("usage_")}
    agg_map.update({col: "sum" for col in stats.columns if col.startswith("night_usage_")})
    return group.agg(agg_map).reset_index()


def aggregate_gps(path: Path) -> pd.DataFrame:
    df = add_time_columns(pd.read_parquet(path))

    def row_stats(items: object) -> dict[str, float]:
        speeds, lats, lons = [], [], []
        for item in as_list(items):
            if not isinstance(item, dict):
                continue
            if item.get("speed") is not None:
                speeds.append(float(item.get("speed") or 0.0))
            if item.get("latitude") is not None:
                lats.append(float(item.get("latitude") or 0.0))
            if item.get("longitude") is not None:
                lons.append(float(item.get("longitude") or 0.0))
        speed_arr = np.asarray(speeds, dtype=np.float64)
        return {
            "gps_points": float(len(speeds)),
            "gps_speed_mean": float(speed_arr.mean()) if len(speed_arr) else np.nan,
            "gps_speed_max": float(speed_arr.max()) if len(speed_arr) else np.nan,
            "gps_moving_points": float((speed_arr > 0.5).sum()) if len(speed_arr) else 0.0,
            "gps_lat_std": float(np.std(lats)) if len(lats) > 1 else 0.0,
            "gps_lon_std": float(np.std(lons)) if len(lons) > 1 else 0.0,
        }

    stats = pd.DataFrame(df["m_gps"].map(row_stats).tolist())
    stats["subject_id"] = df["subject_id"].to_numpy()
    stats["lifelog_date_str"] = df["lifelog_date_str"].to_numpy()
    group = stats.groupby(["subject_id", "lifelog_date_str"], observed=True)
    return group.agg(
        gps_rows=("gps_points", "count"),
        gps_points=("gps_points", "sum"),
        gps_speed_mean=("gps_speed_mean", "mean"),
        gps_speed_max=("gps_speed_max", "max"),
        gps_moving_points=("gps_moving_points", "sum"),
        gps_lat_std=("gps_lat_std", "mean"),
        gps_lon_std=("gps_lon_std", "mean"),
    ).reset_index()


def aggregate_proximity_list(path: Path, column: str, prefix: str) -> pd.DataFrame:
    df = add_time_columns(pd.read_parquet(path))

    def row_stats(items: object) -> dict[str, float]:
        rssis = []
        for item in as_list(items):
            if isinstance(item, dict) and item.get("rssi") is not None:
                rssis.append(float(item.get("rssi") or -100.0))
        arr = np.asarray(rssis, dtype=np.float64)
        return {
            f"{prefix}_count": float(len(arr)),
            f"{prefix}_rssi_mean": float(arr.mean()) if len(arr) else np.nan,
            f"{prefix}_strong_count": float((arr > -65).sum()) if len(arr) else 0.0,
        }

    stats = pd.DataFrame(df[column].map(row_stats).tolist())
    stats["subject_id"] = df["subject_id"].to_numpy()
    stats["lifelog_date_str"] = df["lifelog_date_str"].to_numpy()
    group = stats.groupby(["subject_id", "lifelog_date_str"], observed=True)
    return group.agg({c: "mean" if c.endswith("_mean") else "sum" for c in stats.columns if c.startswith(prefix)}).reset_index()


def aggregate_ambience(path: Path) -> pd.DataFrame:
    df = add_time_columns(pd.read_parquet(path))
    labels = {
        "music": "music",
        "speech": "speech",
        "vehicle": "vehicle",
        "outside": "outside",
        "inside": "inside",
    }

    def row_stats(items: object) -> dict[str, float]:
        rec = {f"ambience_{key}": 0.0 for key in labels}
        for item in as_list(items):
            if not isinstance(item, (list, tuple)) or len(item) < 2:
                continue
            label = str(item[0]).lower()
            score = float(item[1] or 0.0)
            for key, needle in labels.items():
                if needle in label:
                    rec[f"ambience_{key}"] = max(rec[f"ambience_{key}"], score)
        return rec

    stats = pd.DataFrame(df["m_ambience"].map(row_stats).tolist())
    stats["subject_id"] = df["subject_id"].to_numpy()
    stats["lifelog_date_str"] = df["lifelog_date_str"].to_numpy()
    group = stats.groupby(["subject_id", "lifelog_date_str"], observed=True)
    return group.mean(numeric_only=True).reset_index()


def build_daily_features(rows: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    data_dir = ROOT / "data" / "ch2025_data_items"
    features = rows[KEYS + ["split", "metric_row", "lifelog_date_str", "dayofweek", "is_weekend", "dayofmonth", "month_start_proximity", "month_end"]].copy()

    aggregations = [
        aggregate_numeric_file(data_dir / "ch2025_mACStatus.parquet", "m_charging", "phone_charging"),
        aggregate_numeric_file(data_dir / "ch2025_mScreenStatus.parquet", "m_screen_use", "screen_use"),
        aggregate_numeric_file(data_dir / "ch2025_mActivity.parquet", "m_activity", "phone_activity"),
        aggregate_numeric_file(data_dir / "ch2025_mLight.parquet", "m_light", "phone_light"),
        aggregate_numeric_file(data_dir / "ch2025_wLight.parquet", "w_light", "watch_light"),
        aggregate_pedo(data_dir / "ch2025_wPedo.parquet"),
        aggregate_hr(data_dir / "ch2025_wHr.parquet"),
        aggregate_usage(data_dir / "ch2025_mUsageStats.parquet"),
        aggregate_gps(data_dir / "ch2025_mGps.parquet"),
        aggregate_proximity_list(data_dir / "ch2025_mWifi.parquet", "m_wifi", "wifi"),
        aggregate_proximity_list(data_dir / "ch2025_mBle.parquet", "m_ble", "ble"),
        aggregate_ambience(data_dir / "ch2025_mAmbience.parquet"),
    ]
    for part in aggregations:
        features = merge_features(features, part)

    numeric_cols = [
        col for col in features.columns
        if col not in KEYS + ["split", "metric_row", "lifelog_date_str"] and pd.api.types.is_numeric_dtype(features[col])
    ]
    for col in numeric_cols:
        features[col] = pd.to_numeric(features[col], errors="coerce")
    return features, numeric_cols


def build_latent_and_cohort(features: pd.DataFrame, numeric_cols: list[str], config: ExperimentConfig) -> tuple[pd.DataFrame, list[str], dict[str, object]]:
    x = features[numeric_cols].copy()
    imputer = SimpleImputer(strategy="median")
    scaler = StandardScaler()
    x_imp = imputer.fit_transform(x)
    x_scaled = scaler.fit_transform(x_imp)
    dims = max(2, min(config.latent_dims, x_scaled.shape[0] - 1, x_scaled.shape[1]))
    pca = PCA(n_components=dims, random_state=config.random_state)
    latent = pca.fit_transform(x_scaled)
    latent_cols = [f"human_state_latent_{i}" for i in range(dims)]
    out = features.copy()
    for i, col in enumerate(latent_cols):
        out[col] = latent[:, i]

    fp_mean = out.groupby("subject_id", observed=True)[latent_cols].mean()
    fp_std = out.groupby("subject_id", observed=True)[latent_cols].std().fillna(0.0)
    fingerprints = pd.concat([fp_mean.add_suffix("_mean"), fp_std.add_suffix("_std")], axis=1)
    k = min(config.peer_group_count, len(fingerprints))
    kmeans = KMeans(n_clusters=k, random_state=config.random_state, n_init=20)
    fingerprints["peer_group"] = kmeans.fit_predict(StandardScaler().fit_transform(fingerprints))
    out = out.merge(fingerprints[["peer_group"]].reset_index(), on="subject_id", how="left")

    subject_centers = out.groupby("subject_id", observed=True)[latent_cols].mean()
    group_centers = out.groupby("peer_group", observed=True)[latent_cols].mean()
    subject_center_arr = np.vstack([subject_centers.loc[s].to_numpy(dtype=np.float64) for s in out["subject_id"]])
    group_center_arr = np.vstack([group_centers.loc[g].to_numpy(dtype=np.float64) for g in out["peer_group"]])
    latent_arr = out[latent_cols].to_numpy(dtype=np.float64)

    out["dist_to_subject_normal"] = np.linalg.norm(latent_arr - subject_center_arr, axis=1)
    out["dist_to_peer_normal"] = np.linalg.norm(latent_arr - group_center_arr, axis=1)
    out["subject_minus_peer_dist"] = out["dist_to_subject_normal"] - out["dist_to_peer_normal"]
    out["subject_outlier_rank"] = rank01(out["dist_to_subject_normal"])
    out["peer_outlier_rank"] = rank01(out["dist_to_peer_normal"])
    out["cohort_outlier_score"] = (
        0.42 * out["subject_outlier_rank"]
        + 0.42 * out["peer_outlier_rank"]
        + 0.16 * rank01(np.abs(out["subject_minus_peer_dist"]))
    )
    cohort_cols = [
        "peer_group",
        "dist_to_subject_normal",
        "dist_to_peer_normal",
        "subject_minus_peer_dist",
        "subject_outlier_rank",
        "peer_outlier_rank",
        "cohort_outlier_score",
    ]
    meta = {
        "latent_dims": dims,
        "pca_explained_variance_ratio": [float(x) for x in pca.explained_variance_ratio_],
        "peer_group_count": k,
        "subjects": int(out["subject_id"].nunique()),
        "feature_count": len(numeric_cols),
    }
    return out, latent_cols + cohort_cols, meta


def peer_margins(
    frame: pd.DataFrame,
    score_indices: np.ndarray,
    train_indices: np.ndarray,
    labels: pd.DataFrame,
    latent_cols: list[str],
    exclude_self_for_training: bool,
) -> pd.DataFrame:
    out = pd.DataFrame(index=score_indices)
    train_set = set(int(i) for i in train_indices)
    latent_train = frame.loc[train_indices, latent_cols].to_numpy(dtype=np.float64)
    global_mean = latent_train.mean(axis=0)
    for target in TARGETS:
        y_train = labels.loc[train_indices, target].to_numpy(dtype=int)
        for idx in score_indices:
            group = frame.loc[idx, "peer_group"]
            mask_group = frame.loc[train_indices, "peer_group"].to_numpy() == group
            usable = train_indices[mask_group]
            if len(usable) < 4:
                usable = train_indices
            if exclude_self_for_training and int(idx) in train_set and len(usable) > 1:
                usable = np.asarray([u for u in usable if int(u) != int(idx)], dtype=int)
            y_usable = labels.loc[usable, target].to_numpy(dtype=int)
            z_usable = frame.loc[usable, latent_cols].to_numpy(dtype=np.float64)
            pos = z_usable[y_usable == 1]
            neg = z_usable[y_usable == 0]
            pos_c = pos.mean(axis=0) if len(pos) else global_mean
            neg_c = neg.mean(axis=0) if len(neg) else global_mean
            z = frame.loc[idx, latent_cols].to_numpy(dtype=np.float64)
            out.loc[idx, f"peer_margin_{target}"] = float(np.linalg.norm(z - neg_c) - np.linalg.norm(z - pos_c))
    out = out.reset_index().rename(columns={"index": "_feature_index"})
    return out


def add_full_peer_margins(frame: pd.DataFrame, labels: pd.DataFrame, latent_cols: list[str]) -> pd.DataFrame:
    train_idx = frame.index[frame["split"].eq("train")].to_numpy(dtype=int)
    all_idx = frame.index.to_numpy(dtype=int)
    margins = peer_margins(frame, all_idx, train_idx, labels, latent_cols, exclude_self_for_training=False)
    out = frame.reset_index().rename(columns={"index": "_feature_index"}).merge(margins, on="_feature_index", how="left")
    return out.drop(columns=["_feature_index"])


def date_block_splits(train_frame: pd.DataFrame, n_splits: int = 5) -> list[tuple[np.ndarray, np.ndarray]]:
    dates = np.array(sorted(train_frame["lifelog_date_str"].unique()))
    chunks = np.array_split(dates, n_splits)
    splits = []
    for chunk in chunks:
        val_mask = train_frame["lifelog_date_str"].isin(chunk).to_numpy()
        val = train_frame.index[val_mask].to_numpy(dtype=int)
        tr = train_frame.index[~val_mask].to_numpy(dtype=int)
        splits.append((tr, val))
    return splits


def subject_group_splits(train_frame: pd.DataFrame, n_splits: int = 5) -> list[tuple[np.ndarray, np.ndarray]]:
    groups = train_frame["subject_id"].astype(str).to_numpy()
    return [(tr, val) for tr, val in GroupKFold(n_splits=n_splits).split(train_frame, groups=groups)]


def fit_predict_target(x_train: pd.DataFrame, y_train: np.ndarray, x_val: pd.DataFrame) -> np.ndarray:
    model = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=2000, C=0.45, solver="lbfgs")),
        ]
    )
    model.fit(x_train, y_train)
    return clip_prob(model.predict_proba(x_val)[:, 1])


def evaluate_cv(frame_with_cohort: pd.DataFrame, numeric_cols: list[str], cohort_cols: list[str]) -> pd.DataFrame:
    train_rows = frame_with_cohort[frame_with_cohort["split"].eq("train")].copy().reset_index(drop=True)
    labels = pd.read_csv(ROOT / "data" / "ch2026_metrics_train.csv")[TARGETS]
    train_rows[TARGETS] = labels

    base_cols = [c for c in numeric_cols if c in train_rows.columns]
    unsup_cols = base_cols + [c for c in cohort_cols if c in train_rows.columns and c != "peer_group"]
    latent_cols = [c for c in cohort_cols if c.startswith("human_state_latent_")]

    rows = []
    split_sets = {
        "date_block": date_block_splits(train_rows, 5),
        "subject_group": subject_group_splits(train_rows, 5),
    }
    for split_name, splits in split_sets.items():
        for feature_set, static_cols, use_peer_margin in [
            ("sensor_calendar_only", base_cols, False),
            ("sensor_plus_cohort_context", unsup_cols, False),
            ("sensor_plus_cohort_and_peer_margin", unsup_cols, True),
        ]:
            fold_losses = []
            target_losses: dict[str, list[float]] = {target: [] for target in TARGETS}
            for fold, (tr, val) in enumerate(splits):
                fold_frame = train_rows.copy()
                cols = list(static_cols)
                if use_peer_margin:
                    stale_margin_cols = [c for c in fold_frame.columns if c.startswith("peer_margin_")]
                    fold_frame = fold_frame.drop(columns=stale_margin_cols, errors="ignore")
                    margin_train = peer_margins(fold_frame, tr, tr, labels, latent_cols, exclude_self_for_training=True)
                    margin_val = peer_margins(fold_frame, val, tr, labels, latent_cols, exclude_self_for_training=False)
                    margins = pd.concat([margin_train, margin_val], ignore_index=True)
                    fold_frame = fold_frame.reset_index().rename(columns={"index": "_feature_index"}).merge(
                        margins, on="_feature_index", how="left"
                    ).set_index("_feature_index").sort_index()
                    margin_cols = [f"peer_margin_{target}" for target in TARGETS]
                    cols = cols + margin_cols
                pred = np.zeros((len(val), len(TARGETS)), dtype=np.float64)
                for j, target in enumerate(TARGETS):
                    pred[:, j] = fit_predict_target(
                        fold_frame.loc[tr, cols],
                        labels.loc[tr, target].to_numpy(dtype=int),
                        fold_frame.loc[val, cols],
                    )
                    loss = log_loss(labels.loc[val, target].to_numpy(dtype=int), pred[:, j], labels=[0, 1])
                    target_losses[target].append(float(loss))
                fold_loss = float(np.mean([
                    log_loss(labels.loc[val, target].to_numpy(dtype=int), pred[:, j], labels=[0, 1])
                    for j, target in enumerate(TARGETS)
                ]))
                fold_losses.append(fold_loss)
                rows.append(
                    {
                        "split": split_name,
                        "feature_set": feature_set,
                        "fold": fold,
                        "mean_logloss": fold_loss,
                        **{
                            f"{target}_logloss": float(log_loss(labels.loc[val, target].to_numpy(dtype=int), pred[:, j], labels=[0, 1]))
                            for j, target in enumerate(TARGETS)
                        },
                    }
                )
            rows.append(
                {
                    "split": split_name,
                    "feature_set": feature_set,
                    "fold": "mean",
                    "mean_logloss": float(np.mean(fold_losses)),
                    "std_logloss": float(np.std(fold_losses)),
                    **{f"{target}_logloss": float(np.mean(vals)) for target, vals in target_losses.items()},
                }
            )
    return pd.DataFrame(rows)


def load_listener_target(sample: pd.DataFrame) -> np.ndarray:
    cells = pd.read_csv(ROOT / PUBLIC_LISTENER_POSTERIOR_FILE)
    q = np.full((len(sample), len(TARGETS)), np.nan, dtype=np.float64)
    t_index = {target: i for i, target in enumerate(TARGETS)}
    for rec in cells.to_dict("records"):
        row = int(rec["row"])
        target = str(rec["target"])
        if 0 <= row < len(sample) and target in t_index:
            q[row, t_index[target]] = float(rec["posterior_prob"])
    if np.isnan(q).any():
        raise ValueError("Listener posterior is incomplete.")
    return clip_prob(q)


def build_candidate_and_action_audit(full_frame: pd.DataFrame, config: ExperimentConfig) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    best = load_submission(CURRENT_PUBLIC_BEST_FILE)
    base = load_submission(BASELINE_BEFORE_ROW_STATE_FILE)
    listener = load_listener_target(best)
    best_prob = best[TARGETS].to_numpy(dtype=np.float64)
    base_prob = base[TARGETS].to_numpy(dtype=np.float64)
    delta_z = logit(best_prob) - logit(base_prob)
    action_mask = np.abs(delta_z) > 1.0e-12

    test_features = full_frame[full_frame["split"].eq("test")].copy().reset_index(drop=True)
    for target in TARGETS:
        if f"peer_margin_{target}" not in test_features:
            test_features[f"peer_margin_{target}"] = 0.0
    test_features["target_route_margin_q2q3s2"] = (
        0.34 * rank01(np.abs(test_features["peer_margin_Q2"]))
        + 0.33 * rank01(np.abs(test_features["peer_margin_Q3"]))
        + 0.33 * rank01(np.abs(test_features["peer_margin_S2"]))
    )
    test_features["cohort_action_health"] = (
        0.55 * rank01(test_features["cohort_outlier_score"])
        + 0.30 * rank01(test_features["target_route_margin_q2q3s2"])
        + 0.15 * rank01(np.abs(test_features["subject_minus_peer_dist"]))
    )

    low = float(test_features["cohort_action_health"].quantile(config.candidate_damp_bottom_quantile))
    high = float(test_features["cohort_action_health"].quantile(config.candidate_amplify_top_quantile))
    multipliers = np.ones(len(test_features), dtype=np.float64)
    multipliers[test_features["cohort_action_health"].to_numpy() >= high] = config.candidate_amplify
    multipliers[test_features["cohort_action_health"].to_numpy() <= low] = config.candidate_damp

    candidate_z = logit(base_prob).copy()
    safe_delta_z = np.clip(delta_z, -config.candidate_max_abs_logit_step, config.candidate_max_abs_logit_step)
    for row in range(len(best)):
        candidate_z[row, :] = logit(base_prob[row, :]) + multipliers[row] * safe_delta_z[row, :]
    candidate_z[~action_mask] = logit(best_prob)[~action_mask]
    candidate_prob = clip_prob(sigmoid(candidate_z))

    out = best[KEYS].copy()
    for j, target in enumerate(TARGETS):
        out[target] = candidate_prob[:, j]
    digest = short_hash(candidate_prob)
    submission_path = OUT / f"submission_team_cohort_hsjepa_gate_{digest}_uploadsafe.csv"
    out.to_csv(submission_path, index=False)
    (ROOT / submission_path.name).write_text(submission_path.read_text())

    base_soft = float(np.mean(soft_bce(base_prob, listener)))
    best_soft = float(np.mean(soft_bce(best_prob, listener)))
    candidate_soft = float(np.mean(soft_bce(candidate_prob, listener)))
    metrics = pd.DataFrame(
        [
            {
                "model": "baseline_before_row_state_correction",
                "soft_listener_logloss": base_soft,
                "delta_vs_current_best": base_soft - best_soft,
                "submission_file": BASELINE_BEFORE_ROW_STATE_FILE,
            },
            {
                "model": "current_public_best",
                "soft_listener_logloss": best_soft,
                "delta_vs_current_best": 0.0,
                "submission_file": CURRENT_PUBLIC_BEST_FILE,
            },
            {
                "model": "cohort_relative_hsjepa_gate",
                "soft_listener_logloss": candidate_soft,
                "delta_vs_current_best": candidate_soft - best_soft,
                "submission_file": submission_path.name,
            },
        ]
    )

    audit_rows = []
    gain_vs_best = soft_bce(best_prob, listener) - soft_bce(candidate_prob, listener)
    for row in range(len(best)):
        for j, target in enumerate(TARGETS):
            if not action_mask[row, j] and abs(candidate_prob[row, j] - best_prob[row, j]) <= 1.0e-12:
                continue
            audit_rows.append(
                {
                    "row": row,
                    **{key: best.loc[row, key] for key in KEYS},
                    "target": target,
                    "cohort_action_health": float(test_features.loc[row, "cohort_action_health"]),
                    "multiplier": float(multipliers[row]),
                    "current_best_prob": float(best_prob[row, j]),
                    "candidate_prob": float(candidate_prob[row, j]),
                    "delta_vs_current_best": float(candidate_prob[row, j] - best_prob[row, j]),
                    "soft_listener_gain_vs_current_best": float(gain_vs_best[row, j]),
                }
            )
    audit = pd.DataFrame(audit_rows)
    return out, audit, metrics


def evaluate_action_alignment(full_frame: pd.DataFrame) -> pd.DataFrame:
    hidden = pd.read_csv(ROOT / "hs_jepa_end_to_end" / "h057_hidden_row_states.csv")
    test = full_frame[full_frame["split"].eq("test")].copy().reset_index(drop=True)
    y = test["metric_row"].isin(hidden["row"]).astype(int).to_numpy()
    rows = []
    for col in ["cohort_outlier_score", "dist_to_subject_normal", "dist_to_peer_normal", "target_route_margin_q2q3s2"]:
        if col not in test.columns:
            continue
        score = test[col].fillna(0.0).to_numpy(dtype=np.float64)
        if len(np.unique(y)) == 2 and len(np.unique(score)) > 1:
            auc = roc_auc_score(y, score)
        else:
            auc = np.nan
        rows.append(
            {
                "signal": col,
                "auc_for_current_best_hidden_rows": float(auc) if np.isfinite(auc) else np.nan,
                "mean_selected": float(score[y == 1].mean()) if y.sum() else np.nan,
                "mean_not_selected": float(score[y == 0].mean()) if (1 - y).sum() else np.nan,
                "selected_rows": int(y.sum()),
                "total_rows": int(len(y)),
            }
        )
    return pd.DataFrame(rows)


def markdown_table(df: pd.DataFrame, max_rows: int = 20) -> str:
    if df.empty:
        return "_empty_"
    view = df.head(max_rows).copy()
    lines = [
        "| " + " | ".join(map(str, view.columns)) + " |",
        "| " + " | ".join(["---"] * len(view.columns)) + " |",
    ]
    for _, row in view.iterrows():
        lines.append("| " + " | ".join(str(row[c]).replace("|", "/") for c in view.columns) + " |")
    return "\n".join(lines)


def write_report(
    meta: dict[str, object],
    cv: pd.DataFrame,
    alignment: pd.DataFrame,
    candidate_metrics: pd.DataFrame,
    action_audit: pd.DataFrame,
) -> None:
    mean_cv = cv[cv["fold"].astype(str).eq("mean")].copy()
    target_counts = action_audit.groupby("target").size().reset_index(name="changed_cells")
    report = f"""# Cohort-Relative HS-JEPA Experiment

## One-line Summary

This experiment combines the cohort-relative human-state outlier idea with
HS-JEPA by treating peer-cohort anomaly as a **context view** and
**action-health gate**, not as a direct label rule.

## Why This Exists

The teammate idea asks:

- Is this day unusual for this subject?
- Is this day unusual inside a peer cohort of similar subjects?
- If yes, does that anomaly help Q2/Q3/S2 or row-target correction?

HS-JEPA adds one constraint:

> Cohort anomaly should not directly overwrite labels. It should first become a
> hidden state representation and only then decide whether a row-target action is
> safe.

## Data and Representation

- Raw sensor/date rows reviewed through local daily aggregation.
- Numeric daily features: `{meta['feature_count']}`
- Latent dimensions: `{meta['latent_dims']}`
- Peer groups: `{meta['peer_group_count']}`
- Subjects: `{meta['subjects']}`
- PCA explained variance ratio: `{json.dumps(meta['pca_explained_variance_ratio'])}`

## Local CV Performance

Lower logloss is better. These are not public LB estimates; they test whether
cohort context carries train-side target signal.

{markdown_table(mean_cv.sort_values(['split', 'mean_logloss']), 20)}

## Current-Best Action Alignment

This checks whether cohort anomaly independently identifies the rows used by
the current HS-JEPA best action field.

{markdown_table(alignment, 20)}

## Diagnostic Candidate

The generated candidate starts from the current best and changes only the
strength of already-known current-best row-target actions:

- high cohort action-health rows get a small amplification;
- low cohort action-health rows get a small dampening;
- no new broad target route is introduced.

{markdown_table(candidate_metrics, 10)}

Changed cells by target:

{markdown_table(target_counts, 10)}

## Interpretation

This is a useful architecture experiment if cohort features improve local CV or
if cohort action-health aligns with the current-best hidden rows. It is not a
proof that the candidate should be submitted. The candidate is diagnostic
because it asks whether peer-relative state can safely tune an already validated
HS-JEPA action field.

## Decision

- If `sensor_plus_cohort_context` or `sensor_plus_cohort_and_peer_margin`
  improves date-block CV without damaging subject-group CV, the cohort module is
  worth adding to the formal HS-JEPA architecture.
- If current-best hidden-row AUC is weak, cohort anomaly is probably a paper
  context view, not a submission-grade action gate yet.
- If the diagnostic candidate worsens soft listener loss versus current best,
  do not submit it before a stronger solver is built.
"""
    (OUT / "cohort_hsjepa_report.md").write_text(report)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    config = ExperimentConfig()

    rows = make_metric_rows()
    daily, numeric_cols = build_daily_features(rows)
    latent, cohort_cols, meta = build_latent_and_cohort(daily, numeric_cols, config)
    train_labels = pd.read_csv(ROOT / "data" / "ch2026_metrics_train.csv")[TARGETS]
    latent = add_full_peer_margins(latent, train_labels, [c for c in cohort_cols if c.startswith("human_state_latent_")])

    latent["target_route_margin_q2q3s2"] = (
        0.34 * rank01(np.abs(latent["peer_margin_Q2"]))
        + 0.33 * rank01(np.abs(latent["peer_margin_Q3"]))
        + 0.33 * rank01(np.abs(latent["peer_margin_S2"]))
    )

    cv = evaluate_cv(latent, numeric_cols, cohort_cols)
    _, action_audit, candidate_metrics = build_candidate_and_action_audit(latent, config)
    alignment = evaluate_action_alignment(latent)

    daily.to_csv(OUT / "daily_sensor_features.csv", index=False)
    latent.to_csv(OUT / "cohort_human_state_features.csv", index=False)
    cv.to_csv(OUT / "cohort_hsjepa_cv_results.csv", index=False)
    alignment.to_csv(OUT / "cohort_hsjepa_action_alignment.csv", index=False)
    action_audit.to_csv(OUT / "cohort_hsjepa_action_audit.csv", index=False)
    candidate_metrics.to_csv(OUT / "cohort_hsjepa_candidate_metrics.csv", index=False)
    (OUT / "cohort_hsjepa_metadata.json").write_text(json.dumps(meta, indent=2))
    write_report(meta, cv, alignment, candidate_metrics, action_audit)

    print(json.dumps({
        "output_dir": str(OUT),
        "feature_count": meta["feature_count"],
        "latent_dims": meta["latent_dims"],
        "peer_group_count": meta["peer_group_count"],
        "cv_mean_rows": int(cv["fold"].astype(str).eq("mean").sum()),
        "candidate_file": str((OUT / str(candidate_metrics.loc[candidate_metrics["model"].eq("cohort_relative_hsjepa_gate"), "submission_file"].iloc[0])).resolve()),
        "report": str((OUT / "cohort_hsjepa_report.md").resolve()),
    }, indent=2))


if __name__ == "__main__":
    main()
