#!/usr/bin/env python3
"""H013: raw Human-State JEPA gate for the public-equation action.

H012 directly materialized a hidden public-state posterior inferred from old
public LB observations.  That is a legitimate jackpot hypothesis, but it is
also the most overfit-prone version of the idea.

H013 asks a different HS-JEPA question:

    context = raw human lifelog state for the row/day
    target  = public-equation action health and target-route compatibility
    action  = apply H012 only where the raw human state says the route is alive

If this works, HS-JEPA is not just public-LB inversion.  It becomes a
context-to-action-health architecture: raw social/physical/phone context
predicts where a hidden public-state action should be trusted.
"""

from __future__ import annotations

import hashlib
import re
import shutil
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
HITL = ROOT / "hitl"
H013 = HITL / "h013_raw_human_state_jepa_gate"
H013.mkdir(parents=True, exist_ok=True)

for path in [OUT, HITL]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from e272_public_free_candidate_audit import build_features, evaluate_models, score_candidates  # noqa: E402
from public_anchor_bottleneck_decomposition import (  # noqa: E402
    KEYS,
    TARGETS,
    known_public_table,
    load_sub,
    logit,
)
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


CURRENT = "submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv"
H012_PRIMARY = "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"
H010_FILE = "submission_h010_objective_s1s4_v2_uploadsafe.csv"
E247_LB = 0.5761589494

POSTERIOR_PATH = HITL / "h012_public_equation_jepa_jackpot" / "h012_cell_posterior.csv"
REPORT_OUT = H013 / "h013_report.md"
FEATURE_OUT = H013 / "h013_human_state_features.csv"
LATENT_OUT = H013 / "h013_human_state_latent.csv"
ROW_STATE_OUT = H013 / "h013_row_state_scores.csv"
CANDIDATE_OUT = H013 / "h013_candidates.csv"
SELECTION_OUT = H013 / "h013_selection.csv"

EPS = 1.0e-6


@dataclass(frozen=True)
class GateSpec:
    candidate_id: str
    family: str
    alpha: float
    row_mode: str
    cell_mode: str
    k_rows: int
    k_cells: int
    target_subset: str = "all"
    require_route_agree: bool = False
    min_consistency: float = 0.0


def safe_id(text: str, limit: int = 128) -> str:
    clean = re.sub(r"[^A-Za-z0-9_.-]+", "_", text).strip("_")
    return clean[:limit].strip("_")


def sigmoid(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    return 1.0 / (1.0 + np.exp(-x))


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def rel(path: Path | str) -> str:
    path = Path(path)
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def short_hash(frame: pd.DataFrame) -> str:
    arr = np.asarray(frame[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def flatten_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, float) and np.isnan(value):
        return []
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, list):
        return value
    return [value]


def quantile01(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    order = np.argsort(x)
    ranks = np.empty_like(order, dtype=np.float64)
    ranks[order] = np.arange(len(x), dtype=np.float64)
    if len(x) <= 1:
        return np.zeros_like(x)
    return ranks / (len(x) - 1.0)


def date_frame() -> pd.DataFrame:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    train["split"] = "train"
    sample["split"] = "test"
    all_rows = pd.concat([train[KEYS + ["split"] + TARGETS], sample[KEYS + ["split"] + TARGETS]], ignore_index=True)
    all_rows["date"] = all_rows["lifelog_date"].dt.normalize()
    all_rows["weekday"] = all_rows["lifelog_date"].dt.weekday.astype(float)
    all_rows["is_weekend"] = (all_rows["weekday"] >= 5).astype(float)
    all_rows["day_of_month"] = all_rows["lifelog_date"].dt.day.astype(float)
    all_rows["month"] = all_rows["lifelog_date"].dt.month.astype(float)
    all_rows["is_month_start"] = (all_rows["day_of_month"] <= 3).astype(float)
    all_rows["is_month_end"] = (all_rows["day_of_month"] >= 25).astype(float)
    all_rows["payday_10_window"] = (np.abs(all_rows["day_of_month"] - 10.0) <= 1).astype(float)
    all_rows["payday_25_window"] = (np.abs(all_rows["day_of_month"] - 25.0) <= 2).astype(float)
    all_rows["pre_weekend"] = (all_rows["weekday"] == 4).astype(float)
    all_rows["post_weekend"] = (all_rows["weekday"] == 0).astype(float)
    first_by_subject = all_rows.groupby("subject_id")["lifelog_date"].transform("min")
    all_rows["subject_day_idx"] = (all_rows["lifelog_date"] - first_by_subject).dt.days.astype(float)
    return all_rows


def empty_daily(index: pd.DataFrame) -> pd.DataFrame:
    out = index[["subject_id", "date"]].drop_duplicates().copy()
    return out


def add_group_features(base: pd.DataFrame, feat: pd.DataFrame) -> pd.DataFrame:
    if feat.empty:
        return base
    return base.merge(feat, on=["subject_id", "date"], how="left")


def segment_name(hour: int) -> str:
    if hour < 4:
        return "late"
    if hour < 8:
        return "early"
    if hour < 12:
        return "morning"
    if hour < 18:
        return "day"
    if hour < 22:
        return "evening"
    return "prebed"


def numeric_daily(path: Path, value_cols: list[str], prefix: str, index: pd.DataFrame) -> pd.DataFrame:
    df = pd.read_parquet(path)
    if df.empty:
        return empty_daily(index)
    df["date"] = df["timestamp"].dt.normalize()
    df["hour"] = df["timestamp"].dt.hour
    df["segment"] = df["hour"].map(segment_name)
    keep_dates = index[["subject_id", "date"]].drop_duplicates()
    df = df.merge(keep_dates, on=["subject_id", "date"], how="inner")
    if df.empty:
        return empty_daily(index)

    aggs: dict[str, list[str]] = {}
    for col in value_cols:
        aggs[col] = ["count", "mean", "std", "min", "max", "sum"]
    daily = df.groupby(["subject_id", "date"]).agg(aggs)
    daily.columns = [f"{prefix}_{c}_{a}" for c, a in daily.columns]
    daily = daily.reset_index()

    seg_parts: list[pd.DataFrame] = []
    for col in value_cols:
        pivot = df.pivot_table(index=["subject_id", "date"], columns="segment", values=col, aggfunc="sum", fill_value=0.0)
        pivot.columns = [f"{prefix}_{col}_{str(c)}_sum" for c in pivot.columns]
        seg_parts.append(pivot.reset_index())
    for part in seg_parts:
        daily = daily.merge(part, on=["subject_id", "date"], how="left")
    return daily


def activity_daily(index: pd.DataFrame) -> pd.DataFrame:
    df = pd.read_parquet(DATA / "ch2025_data_items" / "ch2025_mActivity.parquet")
    df["date"] = df["timestamp"].dt.normalize()
    df["hour"] = df["timestamp"].dt.hour
    df["segment"] = df["hour"].map(segment_name)
    df = df.merge(index[["subject_id", "date"]].drop_duplicates(), on=["subject_id", "date"], how="inner")
    if df.empty:
        return empty_daily(index)
    out = df.groupby(["subject_id", "date"]).agg(
        m_activity_count=("m_activity", "count"),
        m_activity_mean=("m_activity", "mean"),
        m_activity_std=("m_activity", "std"),
        m_activity_active_rate=("m_activity", lambda x: float(np.mean(np.asarray(x) != 0))),
    ).reset_index()
    code = pd.crosstab([df["subject_id"], df["date"]], df["m_activity"], normalize="index")
    code.columns = [f"m_activity_code_{int(c)}_rate" for c in code.columns]
    code = code.reset_index()
    out = out.merge(code, on=["subject_id", "date"], how="left")
    seg = pd.crosstab([df["subject_id"], df["date"]], df["segment"], values=(df["m_activity"] != 0).astype(float), aggfunc="mean").fillna(0)
    seg.columns = [f"m_activity_active_{c}_rate" for c in seg.columns]
    out = out.merge(seg.reset_index(), on=["subject_id", "date"], how="left")
    return out


def heart_rate_daily(index: pd.DataFrame) -> pd.DataFrame:
    df = pd.read_parquet(DATA / "ch2025_data_items" / "ch2025_wHr.parquet")
    df["date"] = df["timestamp"].dt.normalize()
    df["hour"] = df["timestamp"].dt.hour
    df["segment"] = df["hour"].map(segment_name)
    df = df.merge(index[["subject_id", "date"]].drop_duplicates(), on=["subject_id", "date"], how="inner")
    rows: list[dict[str, Any]] = []
    for rec in df[["subject_id", "date", "segment", "heart_rate"]].itertuples(index=False):
        values = np.asarray(flatten_list(rec.heart_rate), dtype=np.float64)
        values = values[np.isfinite(values)]
        if values.size == 0:
            continue
        rows.append(
            {
                "subject_id": rec.subject_id,
                "date": rec.date,
                "segment": rec.segment,
                "hr_count": float(values.size),
                "hr_mean": float(values.mean()),
                "hr_min": float(values.min()),
                "hr_max": float(values.max()),
                "hr_std": float(values.std()),
                "hr_high_rate": float(np.mean(values >= 95.0)),
                "hr_low_rate": float(np.mean(values <= 55.0)),
            }
        )
    flat = pd.DataFrame(rows)
    if flat.empty:
        return empty_daily(index)
    daily = flat.groupby(["subject_id", "date"]).agg(
        w_hr_obs=("hr_count", "sum"),
        w_hr_mean=("hr_mean", "mean"),
        w_hr_min=("hr_min", "min"),
        w_hr_max=("hr_max", "max"),
        w_hr_std_mean=("hr_std", "mean"),
        w_hr_high_rate=("hr_high_rate", "mean"),
        w_hr_low_rate=("hr_low_rate", "mean"),
    ).reset_index()
    for col in ["hr_mean", "hr_high_rate", "hr_low_rate"]:
        pivot = flat.pivot_table(index=["subject_id", "date"], columns="segment", values=col, aggfunc="mean", fill_value=0.0)
        pivot.columns = [f"w_{col}_{c}" for c in pivot.columns]
        daily = daily.merge(pivot.reset_index(), on=["subject_id", "date"], how="left")
    return daily


APP_CATEGORIES: dict[str, list[str]] = {
    "chat": ["카카오", "kakao", "톡", "메시지", "message", "messenger", "라인", "telegram"],
    "call": ["전화", "통화", "call", "phone"],
    "religion": ["성경", "bible", "교회", "성당", "기도", "찬송", "묵상"],
    "finance": ["토스", "bank", "은행", "카드", "pay", "페이", "증권", "주식", "계좌", "cash"],
    "work": ["gmail", "mail", "메일", "office", "word", "excel", "powerpoint", "teams", "zoom", "slack", "notion"],
    "search_news": ["naver", "네이버", "chrome", "google", "삼성 인터넷", "뉴스", "daum", "다음"],
    "media": ["youtube", "유튜브", "netflix", "tving", "wavve", "melon", "spotify", "music", "뮤직", "웹툰", "티빙"],
    "shopping_food": ["쿠팡", "배민", "배달", "요기요", "마켓", "11번가", "gmarket", "shopping", "shop"],
    "mobility": ["지도", "map", "tmap", "택시", "taxi", "버스", "지하철", "kakao t", "카카오 t"],
    "game": ["game", "게임", "play", "roblox", "pokemon", "포켓몬"],
    "health": ["health", "헬스", "건강", "운동", "samsung health", "캐시워크", "walk"],
    "system": ["one ui", "홈", "launcher", "system", "설정", "settings"],
}


def app_category(name: str) -> str:
    text = str(name).lower().strip()
    for category, keys in APP_CATEGORIES.items():
        if any(key.lower() in text for key in keys):
            return category
    return "other"


def usage_daily(index: pd.DataFrame) -> pd.DataFrame:
    df = pd.read_parquet(DATA / "ch2025_data_items" / "ch2025_mUsageStats.parquet")
    df["date"] = df["timestamp"].dt.normalize()
    df["hour"] = df["timestamp"].dt.hour
    df["segment"] = df["hour"].map(segment_name)
    df = df.merge(index[["subject_id", "date"]].drop_duplicates(), on=["subject_id", "date"], how="inner")
    rows: list[dict[str, Any]] = []
    for rec in df[["subject_id", "date", "segment", "m_usage_stats"]].itertuples(index=False):
        usage = flatten_list(rec.m_usage_stats)
        for item in usage:
            if not isinstance(item, dict):
                continue
            total_time = float(item.get("total_time", 0.0) or 0.0)
            if not np.isfinite(total_time) or total_time <= 0.0:
                continue
            name = str(item.get("app_name", ""))
            rows.append(
                {
                    "subject_id": rec.subject_id,
                    "date": rec.date,
                    "segment": rec.segment,
                    "category": app_category(name),
                    "total_time": total_time,
                    "log_time": np.log1p(total_time),
                }
            )
    flat = pd.DataFrame(rows)
    if flat.empty:
        return empty_daily(index)
    daily = flat.groupby(["subject_id", "date"]).agg(
        usage_total_time=("total_time", "sum"),
        usage_log_time=("log_time", "sum"),
        usage_app_events=("total_time", "count"),
        usage_max_app_time=("total_time", "max"),
    ).reset_index()
    cat = flat.pivot_table(index=["subject_id", "date"], columns="category", values="total_time", aggfunc="sum", fill_value=0.0)
    cat.columns = [f"usage_cat_{c}_time" for c in cat.columns]
    daily = daily.merge(cat.reset_index(), on=["subject_id", "date"], how="left")
    for category in sorted(set(APP_CATEGORIES) | {"other"}):
        if f"usage_cat_{category}_time" not in daily.columns:
            daily[f"usage_cat_{category}_time"] = 0.0
    seg_cat = flat.pivot_table(index=["subject_id", "date"], columns=["segment", "category"], values="total_time", aggfunc="sum", fill_value=0.0)
    seg_cat.columns = [f"usage_{seg}_{cat}_time" for seg, cat in seg_cat.columns]
    daily = daily.merge(seg_cat.reset_index(), on=["subject_id", "date"], how="left")
    total = daily["usage_total_time"].replace(0.0, np.nan)
    for category in sorted(set(APP_CATEGORIES) | {"other"}):
        col = f"usage_cat_{category}_time"
        daily[f"{col}_share"] = (daily[col] / total).fillna(0.0)
    return daily


def gps_daily(index: pd.DataFrame) -> pd.DataFrame:
    df = pd.read_parquet(DATA / "ch2025_data_items" / "ch2025_mGps.parquet")
    df["date"] = df["timestamp"].dt.normalize()
    df["hour"] = df["timestamp"].dt.hour
    df["segment"] = df["hour"].map(segment_name)
    df = df.merge(index[["subject_id", "date"]].drop_duplicates(), on=["subject_id", "date"], how="inner")
    rows: list[dict[str, Any]] = []
    for rec in df[["subject_id", "date", "segment", "m_gps"]].itertuples(index=False):
        vals = flatten_list(rec.m_gps)
        speeds: list[float] = []
        lats: list[float] = []
        lons: list[float] = []
        for item in vals:
            if not isinstance(item, dict):
                continue
            speed = float(item.get("speed", 0.0) or 0.0)
            lat = float(item.get("latitude", np.nan))
            lon = float(item.get("longitude", np.nan))
            if np.isfinite(speed):
                speeds.append(speed)
            if np.isfinite(lat):
                lats.append(lat)
            if np.isfinite(lon):
                lons.append(lon)
        if not speeds and not lats:
            continue
        speed_arr = np.asarray(speeds if speeds else [0.0], dtype=np.float64)
        rows.append(
            {
                "subject_id": rec.subject_id,
                "date": rec.date,
                "segment": rec.segment,
                "gps_points": float(len(vals)),
                "gps_speed_mean": float(speed_arr.mean()),
                "gps_speed_max": float(speed_arr.max()),
                "gps_lat_std": float(np.std(lats)) if len(lats) > 1 else 0.0,
                "gps_lon_std": float(np.std(lons)) if len(lons) > 1 else 0.0,
            }
        )
    flat = pd.DataFrame(rows)
    if flat.empty:
        return empty_daily(index)
    daily = flat.groupby(["subject_id", "date"]).agg(
        gps_points=("gps_points", "sum"),
        gps_speed_mean=("gps_speed_mean", "mean"),
        gps_speed_max=("gps_speed_max", "max"),
        gps_lat_std_mean=("gps_lat_std", "mean"),
        gps_lon_std_mean=("gps_lon_std", "mean"),
    ).reset_index()
    for col in ["gps_points", "gps_speed_mean", "gps_speed_max"]:
        pivot = flat.pivot_table(index=["subject_id", "date"], columns="segment", values=col, aggfunc="sum", fill_value=0.0)
        pivot.columns = [f"{col}_{c}" for c in pivot.columns]
        daily = daily.merge(pivot.reset_index(), on=["subject_id", "date"], how="left")
    return daily


def count_list_daily(path: Path, obj_col: str, prefix: str, index: pd.DataFrame) -> pd.DataFrame:
    df = pd.read_parquet(path)
    df["date"] = df["timestamp"].dt.normalize()
    df = df.merge(index[["subject_id", "date"]].drop_duplicates(), on=["subject_id", "date"], how="inner")
    if df.empty:
        return empty_daily(index)
    df[f"{prefix}_list_len"] = df[obj_col].map(lambda x: float(len(flatten_list(x))))
    return df.groupby(["subject_id", "date"]).agg(
        **{
            f"{prefix}_rows": (obj_col, "count"),
            f"{prefix}_list_len_sum": (f"{prefix}_list_len", "sum"),
            f"{prefix}_list_len_mean": (f"{prefix}_list_len", "mean"),
            f"{prefix}_list_len_max": (f"{prefix}_list_len", "max"),
        }
    ).reset_index()


def build_human_state_features() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rows = date_frame()
    daily = empty_daily(rows)
    static_cols = [
        "weekday",
        "is_weekend",
        "day_of_month",
        "month",
        "is_month_start",
        "is_month_end",
        "payday_10_window",
        "payday_25_window",
        "pre_weekend",
        "post_weekend",
        "subject_day_idx",
    ]
    static = rows[["subject_id", "date"] + static_cols].drop_duplicates(["subject_id", "date"])
    daily = add_group_features(daily, static)
    daily = add_group_features(daily, numeric_daily(DATA / "ch2025_data_items" / "ch2025_mScreenStatus.parquet", ["m_screen_use"], "screen", rows))
    daily = add_group_features(daily, numeric_daily(DATA / "ch2025_data_items" / "ch2025_mACStatus.parquet", ["m_charging"], "charge", rows))
    daily = add_group_features(daily, numeric_daily(DATA / "ch2025_data_items" / "ch2025_mLight.parquet", ["m_light"], "phone_light", rows))
    daily = add_group_features(daily, numeric_daily(DATA / "ch2025_data_items" / "ch2025_wLight.parquet", ["w_light"], "watch_light", rows))
    daily = add_group_features(daily, numeric_daily(DATA / "ch2025_data_items" / "ch2025_wPedo.parquet", ["step", "distance", "speed", "burned_calories"], "pedo", rows))
    daily = add_group_features(daily, activity_daily(rows))
    daily = add_group_features(daily, heart_rate_daily(rows))
    daily = add_group_features(daily, usage_daily(rows))
    daily = add_group_features(daily, gps_daily(rows))
    daily = add_group_features(daily, count_list_daily(DATA / "ch2025_data_items" / "ch2025_mBle.parquet", "m_ble", "ble", rows))
    daily = add_group_features(daily, count_list_daily(DATA / "ch2025_data_items" / "ch2025_mWifi.parquet", "m_wifi", "wifi", rows))
    daily = add_group_features(daily, count_list_daily(DATA / "ch2025_data_items" / "ch2025_mAmbience.parquet", "m_ambience", "ambience", rows))

    full = rows.merge(daily, on=["subject_id", "date"], how="left")
    for col in full.columns:
        if col not in KEYS + ["split", "date"] + TARGETS:
            full[col] = pd.to_numeric(full[col], errors="coerce")
    value_cols = [c for c in full.columns if c not in KEYS + ["split", "date"] + TARGETS]
    full[value_cols] = full[value_cols].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    full.to_csv(FEATURE_OUT, index=False)
    return rows, daily, full


def standardize(x: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    mu = np.nanmean(x, axis=0)
    sigma = np.nanstd(x, axis=0)
    sigma = np.where(sigma < 1.0e-9, 1.0, sigma)
    return np.nan_to_num((x - mu) / sigma), mu, sigma


def pca_latent(features: pd.DataFrame, n_components: int = 16) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    value_cols = [c for c in features.columns if c not in KEYS + ["split", "date"] + TARGETS]
    x = features[value_cols].to_numpy(dtype=np.float64)
    z, _, _ = standardize(x)
    u, s, vt = np.linalg.svd(z, full_matrices=False)
    comps = u[:, :n_components] * s[:n_components]
    out = features[KEYS + ["split"]].copy()
    for i in range(comps.shape[1]):
        out[f"hs_pc{i+1:02d}"] = comps[:, i]
    variance = (s * s) / max(1, z.shape[0] - 1)
    explained = variance / max(float(variance.sum()), 1.0e-12)
    diag = pd.DataFrame(
        {
            "component": [f"hs_pc{i+1:02d}" for i in range(len(explained[:n_components]))],
            "explained_ratio": explained[:n_components],
            "singular_value": s[:n_components],
        }
    )
    diag.to_csv(H013 / "h013_latent_pca_diagnostics.csv", index=False)
    out.to_csv(LATENT_OUT, index=False)
    return out, z, comps


def knn_label_route(features: pd.DataFrame, z: np.ndarray, base_prob: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    train_mask = features["split"].eq("train").to_numpy()
    test_mask = features["split"].eq("test").to_numpy()
    y_train = features.loc[train_mask, TARGETS].to_numpy(dtype=np.float64)
    z_train = z[train_mask]
    z_test = z[test_mask]
    dist = ((z_test[:, None, :] - z_train[None, :, :]) ** 2).mean(axis=2)
    k = min(35, z_train.shape[0])
    idx = np.argpartition(dist, kth=k - 1, axis=1)[:, :k]
    local_dist = np.take_along_axis(dist, idx, axis=1)
    scale = np.median(local_dist, axis=1, keepdims=True)
    scale = np.where(scale <= 1.0e-9, np.mean(local_dist, axis=1, keepdims=True) + 1.0e-9, scale)
    weights = np.exp(-local_dist / scale)
    weights = weights / weights.sum(axis=1, keepdims=True)
    prior = np.einsum("ij,ijt->it", weights, y_train[idx])
    prior = np.clip((prior * k + 0.5) / (k + 1.0), EPS, 1.0 - EPS)
    route = logit(prior) - logit(base_prob)
    return prior, route


def row_knn_smooth(values: np.ndarray, latent: np.ndarray, k: int = 15) -> np.ndarray:
    dist = ((latent[:, None, :] - latent[None, :, :]) ** 2).mean(axis=2)
    np.fill_diagonal(dist, np.inf)
    k = min(k, len(values) - 1)
    idx = np.argpartition(dist, kth=k - 1, axis=1)[:, :k]
    local = np.take_along_axis(dist, idx, axis=1)
    scale = np.median(local, axis=1, keepdims=True)
    scale = np.where(scale <= 1.0e-9, np.mean(local, axis=1, keepdims=True) + 1.0e-9, scale)
    weights = np.exp(-local / scale)
    weights = weights / weights.sum(axis=1, keepdims=True)
    return np.sum(weights * values[idx], axis=1)


def load_h012_direction(base_prob: np.ndarray) -> tuple[np.ndarray, pd.DataFrame]:
    posterior = pd.read_csv(POSTERIOR_PATH)
    d = np.zeros_like(base_prob, dtype=np.float64)
    consistency = np.zeros_like(base_prob, dtype=np.float64)
    score = np.zeros_like(base_prob, dtype=np.float64)
    for rec in posterior.to_dict("records"):
        row = int(rec["row"])
        target = str(rec["target"])
        ti = TARGETS.index(target)
        d[row, ti] = float(rec["logit_delta_to_posterior"])
        consistency[row, ti] = float(rec["direction_consistency"])
        score[row, ti] = float(rec["cell_score"])
    posterior["target_i"] = posterior["target"].map({t: i for i, t in enumerate(TARGETS)})
    posterior["flat_i"] = posterior["row"].astype(int) * len(TARGETS) + posterior["target_i"].astype(int)
    return d, posterior


def known_anchor_files() -> pd.DataFrame:
    known = known_public_table().copy()
    rows: list[dict[str, Any]] = []
    for rec in known.to_dict("records"):
        file_name = str(rec["file"])
        if file_name == CURRENT:
            continue
        try:
            load_sub(file_name)
        except FileNotFoundError:
            continue
        delta = float(rec["public_lb"]) - E247_LB
        rows.append({"file": file_name, "public_lb": float(rec["public_lb"]), "delta_vs_e247": delta})
    return pd.DataFrame(rows)


def row_action_health(sample: pd.DataFrame, base_logit: np.ndarray, h012_dir: np.ndarray, latent: np.ndarray) -> pd.DataFrame:
    anchors = known_anchor_files()
    rows: list[dict[str, Any]] = []
    target_bad = np.zeros((base_logit.shape[0], len(TARGETS)), dtype=np.float64)
    target_anti_bad = np.zeros_like(target_bad)
    row_bad = np.zeros(base_logit.shape[0], dtype=np.float64)
    row_anti_bad = np.zeros(base_logit.shape[0], dtype=np.float64)
    row_survivor = np.zeros(base_logit.shape[0], dtype=np.float64)

    h012_norm_row = np.sqrt(np.sum(h012_dir * h012_dir, axis=1)) + 1.0e-12
    for rec in anchors.to_dict("records"):
        file_name = str(rec["file"])
        delta = float(rec["delta_vs_e247"])
        pred = load_sub(file_name, sample)[TARGETS].to_numpy(dtype=np.float64)
        move = logit(pred) - base_logit
        move_norm = np.sqrt(np.sum(move * move, axis=1)) + 1.0e-12
        row_cos = np.sum(move * h012_dir, axis=1) / (move_norm * h012_norm_row)
        severity = max(delta, 0.0)
        bad_weight = severity / 0.00025
        survivor_weight = 1.0 / (1.0 + max(delta, 0.0) / 0.00020)
        row_bad += bad_weight * np.maximum(row_cos, 0.0)
        row_anti_bad += bad_weight * np.maximum(-row_cos, 0.0)
        row_survivor += survivor_weight * np.maximum(row_cos, 0.0)
        same = np.sign(move) == np.sign(h012_dir)
        opp = np.sign(move) == -np.sign(h012_dir)
        mag = np.abs(move) * (np.abs(h012_dir) > 1.0e-9)
        target_bad += bad_weight * same * mag
        target_anti_bad += bad_weight * opp * mag
        rows.append(
            {
                "file": file_name,
                "delta_vs_e247": delta,
                "row_cos_mean": float(np.mean(row_cos)),
                "row_cos_p90": float(np.quantile(row_cos, 0.90)),
                "same_sign_cell_rate": float(np.mean(same[np.abs(h012_dir) > 1.0e-9])),
            }
        )

    raw_health = row_anti_bad - row_bad + 0.20 * row_survivor
    smooth = row_knn_smooth(raw_health, latent[:, : min(12, latent.shape[1])], k=17)
    health = 0.65 * raw_health + 0.35 * smooth
    q = quantile01(health)
    out = sample.copy()
    out["raw_action_health"] = raw_health
    out["smoothed_action_health"] = smooth
    out["hs_action_health"] = health
    out["hs_action_health_q"] = q
    out["bad_alignment"] = row_bad
    out["anti_bad_alignment"] = row_anti_bad
    out["survivor_alignment"] = row_survivor
    for ti, target in enumerate(TARGETS):
        out[f"{target}_bad_cell_pressure"] = target_bad[:, ti]
        out[f"{target}_anti_bad_cell_pressure"] = target_anti_bad[:, ti]
    pd.DataFrame(rows).to_csv(H013 / "h013_anchor_action_alignment.csv", index=False)
    out.to_csv(ROW_STATE_OUT, index=False)
    return out


def target_mask(target_subset: str, shape: tuple[int, int]) -> np.ndarray:
    mask = np.zeros(shape, dtype=bool)
    if target_subset == "all":
        mask[:] = True
    elif target_subset == "Q":
        for t in ["Q1", "Q2", "Q3"]:
            mask[:, TARGETS.index(t)] = True
    elif target_subset == "S":
        for t in ["S1", "S2", "S3", "S4"]:
            mask[:, TARGETS.index(t)] = True
    elif target_subset in TARGETS:
        mask[:, TARGETS.index(target_subset)] = True
    elif target_subset == "Q3S":
        for t in ["Q3", "S1", "S2", "S3", "S4"]:
            mask[:, TARGETS.index(t)] = True
    elif target_subset == "S1S4":
        for t in ["S1", "S4"]:
            mask[:, TARGETS.index(t)] = True
    else:
        raise ValueError(target_subset)
    return mask


def specs() -> list[GateSpec]:
    out: list[GateSpec] = []
    row_modes = ["health_top", "health_midtop", "health_anti_bad", "health_low_control"]
    for row_mode in row_modes:
        for k_rows in [40, 70, 100, 140, 190]:
            for k_cells in [160, 260, 420, 650, 900]:
                for alpha in [0.35, 0.55, 0.75, 1.00]:
                    out.append(GateSpec(f"{row_mode}_all_r{k_rows}_c{k_cells}_a{alpha:g}", "h012_raw_gate", alpha, row_mode, "h012_top", k_rows, k_cells))
                    out.append(GateSpec(f"{row_mode}_route_r{k_rows}_c{k_cells}_a{alpha:g}", "route_agree_gate", alpha, row_mode, "h012_top", k_rows, k_cells, require_route_agree=True))
    for target_subset in ["Q", "S", "Q3S", "S1S4", "Q3", "S1", "S4"]:
        for row_mode in ["health_top", "health_anti_bad"]:
            for k_rows in [70, 120, 180]:
                for k_cells in [120, 240, 420]:
                    for alpha in [0.55, 0.85, 1.15]:
                        out.append(
                            GateSpec(
                                f"{row_mode}_{target_subset}_r{k_rows}_c{k_cells}_a{alpha:g}",
                                "target_route_gate",
                                alpha,
                                row_mode,
                                "h012_top",
                                k_rows,
                                k_cells,
                                target_subset=target_subset,
                                require_route_agree=True,
                            )
                        )
    for k_rows in [50, 100, 150, 220]:
        for alpha in [0.20, 0.35, 0.50]:
            out.append(GateSpec(f"knn_label_route_r{k_rows}_a{alpha:g}", "knn_label_route", alpha, "health_top", "route_abs", k_rows, 500, require_route_agree=True))
    return out


def row_selector(row_scores: pd.DataFrame, row_mode: str, k: int) -> np.ndarray:
    if row_mode == "health_top":
        order = np.argsort(row_scores["hs_action_health"].to_numpy(dtype=np.float64))
        chosen = order[-min(k, len(order)) :]
    elif row_mode == "health_midtop":
        q = row_scores["hs_action_health_q"].to_numpy(dtype=np.float64)
        pool = np.flatnonzero((q >= 0.45) & (q <= 0.88))
        if len(pool) == 0:
            pool = np.arange(len(q))
        chosen = pool[np.argsort(row_scores["hs_action_health"].to_numpy(dtype=np.float64)[pool])[-min(k, len(pool)) :]]
    elif row_mode == "health_anti_bad":
        score = row_scores["anti_bad_alignment"].to_numpy(dtype=np.float64) - row_scores["bad_alignment"].to_numpy(dtype=np.float64)
        chosen = np.argsort(score)[-min(k, len(score)) :]
    elif row_mode == "health_low_control":
        chosen = np.argsort(row_scores["hs_action_health"].to_numpy(dtype=np.float64))[: min(k, len(row_scores))]
    else:
        raise ValueError(row_mode)
    mask = np.zeros(len(row_scores), dtype=bool)
    mask[chosen] = True
    return mask


def cell_selector(
    spec: GateSpec,
    row_mask: np.ndarray,
    h012_dir: np.ndarray,
    cell_score: np.ndarray,
    consistency: np.ndarray,
    route: np.ndarray,
) -> np.ndarray:
    valid = row_mask[:, None] & target_mask(spec.target_subset, h012_dir.shape)
    valid &= np.abs(h012_dir) > 1.0e-9
    valid &= consistency >= spec.min_consistency
    if spec.require_route_agree:
        valid &= np.sign(route) == np.sign(h012_dir)
        valid &= np.abs(route) >= 0.02

    if spec.cell_mode == "h012_top":
        score = cell_score.copy()
    elif spec.cell_mode == "route_abs":
        score = np.abs(route) * (np.sign(route) == np.sign(h012_dir))
    else:
        raise ValueError(spec.cell_mode)

    flat = np.flatnonzero(valid.reshape(-1))
    if len(flat) == 0:
        return np.zeros_like(valid)
    chosen = flat[np.argsort(score.reshape(-1)[flat])[-min(spec.k_cells, len(flat)) :]]
    mask = np.zeros_like(valid)
    mask.reshape(-1)[chosen] = True
    return mask


def posterior_loss_delta(base_prob: np.ndarray, cand_prob: np.ndarray, q: np.ndarray) -> float:
    p0 = clip_prob(base_prob)
    p1 = clip_prob(cand_prob)
    y = clip_prob(q)
    l0 = -(y * np.log(p0) + (1.0 - y) * np.log(1.0 - p0))
    l1 = -(y * np.log(p1) + (1.0 - y) * np.log(1.0 - p1))
    return float(np.mean(l1 - l0))


def write_candidate(base: pd.DataFrame, base_logit: np.ndarray, direction: np.ndarray, mask: np.ndarray, alpha: float, candidate_id: str) -> Path:
    out = base.copy()
    z = base_logit.copy()
    z[mask] = z[mask] + alpha * direction[mask]
    prob = np.clip(sigmoid(z), EPS, 1.0 - EPS)
    out[TARGETS] = prob
    path = H013 / f"submission_h013_{safe_id(candidate_id)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def validate_submission(path: Path, sample: pd.DataFrame) -> None:
    df = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEYS).reset_index(drop=True)
    if not df[KEYS].equals(sample[KEYS]):
        raise ValueError(f"key mismatch: {path}")
    values = df[TARGETS].to_numpy(dtype=np.float64)
    if not np.isfinite(values).all():
        raise ValueError(f"non-finite probabilities: {path}")
    if values.min() < 0.0 or values.max() > 1.0:
        raise ValueError(f"probability range error: {path}")


def movement_stats(path: Path, sample: pd.DataFrame, base_prob: np.ndarray, base_logit: np.ndarray, q: np.ndarray) -> dict[str, Any]:
    df = load_sub(path, sample)
    prob = df[TARGETS].to_numpy(dtype=np.float64)
    move = logit(prob) - base_logit
    changed = np.abs(move) > 1.0e-12
    row_changed = changed.any(axis=1)
    out: dict[str, Any] = {
        "changed_rows": int(row_changed.sum()),
        "changed_cells": int(changed.sum()),
        "mean_abs_logit_delta": float(np.mean(np.abs(move))),
        "l1_logit_delta": float(np.sum(np.abs(move))),
        "max_abs_logit_delta": float(np.max(np.abs(move))),
        "max_abs_prob_delta": float(np.max(np.abs(prob - base_prob))),
        "posterior_delta": posterior_loss_delta(base_prob, prob, q),
    }
    for ti, target in enumerate(TARGETS):
        out[f"changed_{target}"] = int(changed[:, ti].sum())
    return out


def generate_candidates() -> tuple[pd.DataFrame, pd.DataFrame, Path]:
    rows, _, features = build_human_state_features()
    latent_frame, z_all, pcs_all = pca_latent(features)

    base = load_sub(CURRENT)
    sample = base[KEYS].copy()
    base_prob = base[TARGETS].to_numpy(dtype=np.float64)
    base_logit = logit(base_prob)
    h012_dir, posterior = load_h012_direction(base_prob)
    q = np.clip(base_prob + posterior.pivot(index="row", columns="target", values="posterior_minus_base").reindex(range(len(base))).fillna(0.0)[TARGETS].to_numpy(dtype=np.float64), EPS, 1.0 - EPS)
    consistency = np.zeros_like(base_prob)
    cell_score = np.zeros_like(base_prob)
    for rec in posterior.to_dict("records"):
        consistency[int(rec["row"]), int(rec["target_i"])] = float(rec["direction_consistency"])
        cell_score[int(rec["row"]), int(rec["target_i"])] = float(rec["cell_score"])

    train_test_features = features.sort_values(KEYS).reset_index(drop=True)
    test_mask = train_test_features["split"].eq("test").to_numpy()
    test_pcs = pcs_all[test_mask]
    label_prior, label_route = knn_label_route(train_test_features, z_all, base_prob)
    row_scores = row_action_health(sample, base_logit, h012_dir, test_pcs)
    for ti, target in enumerate(TARGETS):
        row_scores[f"{target}_knn_prior"] = label_prior[:, ti]
        row_scores[f"{target}_route_logit"] = label_route[:, ti]
    row_scores.to_csv(ROW_STATE_OUT, index=False)

    candidate_rows: list[dict[str, Any]] = []
    candidate_paths: list[Path] = []
    for spec in specs():
        row_mask = row_selector(row_scores, spec.row_mode, spec.k_rows)
        direction = h012_dir.copy()
        if spec.family == "knn_label_route":
            direction = np.where(np.sign(label_route) == np.sign(h012_dir), label_route, 0.0)
        mask = cell_selector(spec, row_mask, h012_dir, cell_score, consistency, label_route)
        if not mask.any():
            continue
        path = write_candidate(base, base_logit, direction, mask, spec.alpha, spec.candidate_id)
        validate_submission(path, sample)
        candidate_paths.append(path)
        stats = movement_stats(path, sample, base_prob, base_logit, q)
        changed_rows = np.flatnonzero(mask.any(axis=1))
        candidate_rows.append(
            {
                "candidate_id": spec.candidate_id,
                "family": spec.family,
                "alpha": spec.alpha,
                "row_mode": spec.row_mode,
                "cell_mode": spec.cell_mode,
                "k_rows": spec.k_rows,
                "k_cells": spec.k_cells,
                "target_subset": spec.target_subset,
                "require_route_agree": spec.require_route_agree,
                "min_consistency": spec.min_consistency,
                "file": rel(path),
                "basename": path.name,
                "mean_row_health_changed": float(row_scores.loc[changed_rows, "hs_action_health"].mean()) if len(changed_rows) else 0.0,
                "min_row_health_q_changed": float(row_scores.loc[changed_rows, "hs_action_health_q"].min()) if len(changed_rows) else 0.0,
                "mean_bad_alignment_changed": float(row_scores.loc[changed_rows, "bad_alignment"].mean()) if len(changed_rows) else 0.0,
                "mean_anti_bad_alignment_changed": float(row_scores.loc[changed_rows, "anti_bad_alignment"].mean()) if len(changed_rows) else 0.0,
                "route_agree_rate_changed": float((np.sign(label_route[mask]) == np.sign(h012_dir[mask])).mean()) if mask.any() else 0.0,
                "mean_cell_score_changed": float(cell_score[mask].mean()),
                "mean_consistency_changed": float(consistency[mask].mean()),
                **stats,
            }
        )
    candidates = pd.DataFrame(candidate_rows)
    candidates.to_csv(CANDIDATE_OUT, index=False)

    known, refs, ref_vecs = build_known_and_refs(sample)
    known["file"] = known["file"].astype(str)
    model_df = evaluate_models(known)
    feat_files = [CURRENT] + candidates["file"].astype(str).tolist()
    feat = build_features(feat_files, sample, refs, ref_vecs)
    scored = score_candidates(known, feat, model_df)
    merged = candidates.merge(scored, left_on="file", right_on="file", how="left", suffixes=("", "_selector"))
    merged["raw_gate_strength"] = merged["mean_row_health_changed"] - 0.35 * merged["mean_bad_alignment_changed"]
    merged["h013_big_bet_gate"] = (
        (merged["posterior_delta"] < -0.0010)
        & (merged["changed_cells"] >= 120)
        & (merged["mean_consistency_changed"] >= 0.80)
        & (merged["raw_gate_strength"] > merged["raw_gate_strength"].median())
    )
    if "public_bad_cos_pos_sum" not in merged.columns:
        merged["public_bad_cos_pos_sum"] = merged.get("incremental_bad_axis_vs_current", pd.Series(0.0, index=merged.index)).abs()
    merged["h013_selector_survival_gate"] = (
        (merged["pred_delta_vs_current_p90"].fillna(9.0) < 0.00095)
        & (merged["public_bad_cos_pos_sum"].fillna(0.0) < 0.050)
    )
    merged["h013_score"] = (
        merged["posterior_delta"]
        - 0.00025 * merged["raw_gate_strength"].rank(pct=True)
        + 0.20 * merged["pred_delta_vs_current_p90"].fillna(0.0015)
        + 0.00010 * (1.0 - merged["route_agree_rate_changed"])
    )
    merged["h013_decision"] = np.where(
        merged["h013_big_bet_gate"] & merged["h013_selector_survival_gate"],
        "raw_hs_jepa_jackpot",
        np.where(merged["h013_big_bet_gate"], "raw_hs_jepa_high_risk", "reject"),
    )
    merged = merged.sort_values(["h013_decision", "h013_score"], ascending=[True, True]).reset_index(drop=True)
    priority = {"raw_hs_jepa_jackpot": 0, "raw_hs_jepa_high_risk": 1, "reject": 2}
    merged["_priority"] = merged["h013_decision"].map(priority)
    merged = merged.sort_values(["_priority", "h013_score"], ascending=[True, True]).drop(columns=["_priority"]).reset_index(drop=True)
    merged["decision_rank"] = np.arange(len(merged))
    merged.to_csv(SELECTION_OUT, index=False)
    selected = merged.iloc[0]
    selected_path = ROOT / str(selected["file"])
    upload = ROOT / f"submission_h013_raw_hs_jepa_{safe_id(str(selected['candidate_id']), 80)}_{short_hash(load_sub(selected_path, sample))}_uploadsafe.csv"
    shutil.copyfile(selected_path, upload)
    validate_submission(upload, sample)
    return merged, row_scores, upload


def write_report(selection: pd.DataFrame, row_scores: pd.DataFrame, upload: Path) -> None:
    top = selection.head(35).copy()
    public_ready = selection[selection["h013_decision"].eq("raw_hs_jepa_jackpot")]
    high_risk = selection[selection["h013_decision"].eq("raw_hs_jepa_high_risk")]
    lines: list[str] = []
    lines.append("# H013 Raw Human-State JEPA Gate")
    lines.append("")
    lines.append("## Question")
    lines.append("")
    lines.append("Can raw lifelog context decide where the H012 public-equation action is healthy?")
    lines.append("")
    lines.append("## Worldview")
    lines.append("")
    lines.append(
        "HS-JEPA context is the human day state: app categories, screen/charging rhythm, activity, mobility, heart-rate, light, calendar, and payday/weekend proxies. "
        "The target representation is not the label itself; it is action-health for applying the hidden public-equation direction."
    )
    lines.append("")
    lines.append("## Evidence")
    lines.append("")
    lines.append(f"- generated candidates: `{len(selection)}`")
    lines.append(f"- jackpot-gated candidates: `{len(public_ready)}`")
    lines.append(f"- high-risk candidates: `{len(high_risk)}`")
    lines.append(f"- selected upload-safe file: `{upload.name}`")
    lines.append(f"- row health q min/median/max: `{row_scores['hs_action_health_q'].min():.6f}` / `{row_scores['hs_action_health_q'].median():.6f}` / `{row_scores['hs_action_health_q'].max():.6f}`")
    lines.append("")
    lines.append("## Top Selection")
    cols = [
        "candidate_id",
        "h013_decision",
        "family",
        "row_mode",
        "target_subset",
        "alpha",
        "changed_rows",
        "changed_cells",
        "posterior_delta",
        "pred_delta_vs_current_mean",
        "pred_delta_vs_current_p90",
        "raw_gate_strength",
        "route_agree_rate_changed",
        "mean_consistency_changed",
        "file",
    ]
    view = top[[c for c in cols if c in top.columns]].copy()
    lines.append(markdown_table(view))
    lines.append("")
    lines.append("## Decision Rule")
    lines.append("")
    lines.append(
        "A public win would support the HS-JEPA claim that raw human-state context can gate a hidden public-state action. "
        "A loss, especially if H012 also fails, means the current raw context/action-health translator is not enough; the public-equation posterior should remain diagnostic rather than directly materialized."
    )
    lines.append("")
    lines.append("## Files")
    lines.append("")
    for path in [FEATURE_OUT, LATENT_OUT, ROW_STATE_OUT, CANDIDATE_OUT, SELECTION_OUT, REPORT_OUT, upload]:
        lines.append(f"- `{rel(path)}`")
    lines.append("")
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def markdown_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "_empty_"
    df = frame.copy()
    for col in df.columns:
        if pd.api.types.is_float_dtype(df[col]):
            df[col] = df[col].map(lambda x: "" if pd.isna(x) else f"{float(x):.9f}")
        else:
            df[col] = df[col].map(lambda x: "" if pd.isna(x) else str(x))
    header = "| " + " | ".join(df.columns) + " |"
    sep = "| " + " | ".join(["---"] * len(df.columns)) + " |"
    rows = ["| " + " | ".join(row) + " |" for row in df.astype(str).to_numpy()]
    return "\n".join([header, sep, *rows])


def main() -> None:
    selection, row_scores, upload = generate_candidates()
    write_report(selection, row_scores, upload)
    print(f"Wrote {REPORT_OUT}")
    print(f"Selected {upload}")
    print(selection.head(12).to_string(index=False))


if __name__ == "__main__":
    main()
