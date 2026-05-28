from __future__ import annotations

from pathlib import Path
import warnings

import numpy as np
import pandas as pd
from pandas.errors import PerformanceWarning


warnings.simplefilter("ignore", PerformanceWarning)


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ITEMS = DATA / "ch2025_data_items"
OUT = ROOT / "analysis_outputs"
KEY = ["subject_id", "lifelog_date"]

DAY_START = 12 * 60
DAY_END = 36 * 60


ABS_WINDOWS = {
    "all24h": (12 * 60, 36 * 60),
    "day12_18": (12 * 60, 18 * 60),
    "evening18_24": (18 * 60, 24 * 60),
    "night18_36": (18 * 60, 36 * 60),
    "cand21_34": (21 * 60, 34 * 60),
    "late24_30": (24 * 60, 30 * 60),
}

REL_WINDOWS = {
    "pre6h": (-6 * 60, 0),
    "pre3h": (-3 * 60, 0),
    "pre1h": (-1 * 60, 0),
    "post2h": (0, 2 * 60),
    "core5h": (1 * 60, 6 * 60),
}


def _read_keys() -> pd.DataFrame:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    sub = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    train["split"] = "train"
    sub["split"] = "submission"
    keys = pd.concat(
        [train[KEY + ["sleep_date", "split"]], sub[KEY + ["sleep_date", "split"]]],
        ignore_index=True,
    )
    proxy = pd.read_parquet(OUT / "sleep_interval_proxy_features.parquet")
    proxy_cols = [c for c in ["proxy_screen_step_start_hour", "proxy_screen_start_hour"] if c in proxy.columns]
    keys = keys.merge(proxy[KEY + proxy_cols], on=KEY, how="left")
    start_hour = keys["proxy_screen_step_start_hour"].fillna(keys["proxy_screen_start_hour"])
    keys["mp_sleep_start_min"] = start_hour * 60.0
    keys["mp_dayofweek"] = keys["lifelog_date"].dt.dayofweek
    keys["mp_is_weekend"] = (keys["mp_dayofweek"] >= 5).astype(float)
    keys = keys.sort_values(KEY).reset_index(drop=True)
    return keys


def _add_lifelog_minute(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["timestamp"] = pd.to_datetime(out["timestamp"])
    hour = out["timestamp"].dt.hour
    minute = out["timestamp"].dt.minute
    base = out["timestamp"].dt.normalize()
    out["lifelog_date"] = np.where(hour < 12, base - pd.Timedelta(days=1), base)
    out["lifelog_date"] = pd.to_datetime(out["lifelog_date"])
    out["mp_minute"] = np.where(hour < 12, (hour + 24) * 60 + minute, hour * 60 + minute).astype(int)
    return out[(out["mp_minute"] >= DAY_START) & (out["mp_minute"] < DAY_END)].copy()


def _list_len(x: object) -> float:
    return float(len(x)) if isinstance(x, list) else 0.0


def _rssi_stats(items: object) -> tuple[float, float, float]:
    rssis = []
    if isinstance(items, list):
        for item in items:
            if not isinstance(item, dict):
                continue
            try:
                rssis.append(float(item.get("rssi")))
            except Exception:
                continue
    if not rssis:
        return (np.nan, np.nan, np.nan)
    arr = np.asarray(rssis, dtype=float)
    return (float(np.nanmean(arr)), float(np.nanmax(arr)), float(np.nanmin(arr)))


def _unique_key_count(items: object, key: str) -> float:
    vals = set()
    if isinstance(items, list):
        for item in items:
            if isinstance(item, dict) and item.get(key) is not None:
                vals.add(str(item.get(key)))
    return float(len(vals))


def _hr_frame() -> pd.DataFrame:
    df = pd.read_parquet(ITEMS / "ch2025_wHr.parquet")

    def stats(x: object) -> tuple[float, float, float, float, float]:
        arr = np.asarray(x if isinstance(x, list) else [], dtype=float)
        arr = arr[np.isfinite(arr)]
        if arr.size == 0:
            return (0.0, np.nan, np.nan, np.nan, np.nan)
        return (float(arr.size), float(arr.mean()), float(arr.min()), float(arr.max()), float(arr.std(ddof=1) if arr.size > 1 else 0.0))

    vals = pd.DataFrame(df["heart_rate"].map(stats).tolist(), columns=["mp_point_count", "mp_value_mean", "mp_value_min", "mp_value_max", "mp_value_std"])
    out = pd.concat([df[["subject_id", "timestamp"]].reset_index(drop=True), vals], axis=1)
    return _add_lifelog_minute(out)


def _numeric_frame(file_name: str, cols: list[str]) -> pd.DataFrame:
    df = pd.read_parquet(ITEMS / file_name)
    value = pd.Series(0.0, index=df.index)
    for col in cols:
        value = value + pd.to_numeric(df[col], errors="coerce").fillna(0.0)
    out = df[["subject_id", "timestamp"]].copy()
    out["mp_point_count"] = 1.0
    out["mp_value_mean"] = value.astype(float)
    out["mp_value_min"] = value.astype(float)
    out["mp_value_max"] = value.astype(float)
    out["mp_value_std"] = 0.0
    return _add_lifelog_minute(out)


def _scan_frame(file_name: str, list_col: str, unique_key: str | None = None, *, gps_speed: bool = False) -> pd.DataFrame:
    df = pd.read_parquet(ITEMS / file_name)
    out = df[["subject_id", "timestamp"]].copy()
    out["mp_point_count"] = df[list_col].map(_list_len)
    if unique_key is None:
        out["mp_unique_count"] = np.nan
    else:
        out["mp_unique_count"] = df[list_col].map(lambda x: _unique_key_count(x, unique_key))

    if gps_speed:
        def gps_stats(items: object) -> tuple[float, float, float]:
            speeds = []
            if isinstance(items, list):
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    try:
                        speeds.append(float(item.get("speed")))
                    except Exception:
                        continue
            if not speeds:
                return (np.nan, np.nan, np.nan)
            arr = np.asarray(speeds, dtype=float)
            return (float(np.nanmean(arr)), float(np.nanmin(arr)), float(np.nanmax(arr)))

        vals = pd.DataFrame(df[list_col].map(gps_stats).tolist(), columns=["mp_value_mean", "mp_value_min", "mp_value_max"])
        vals["mp_value_std"] = np.nan
    elif list_col in {"m_wifi", "m_ble"}:
        vals = pd.DataFrame(df[list_col].map(_rssi_stats).tolist(), columns=["mp_value_mean", "mp_value_max", "mp_value_min"])
        vals["mp_value_std"] = np.nan
    elif list_col == "m_usage_stats":
        def usage_stats(items: object) -> tuple[float, float, float]:
            totals = []
            if isinstance(items, list):
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    try:
                        totals.append(float(item.get("total_time") or 0.0))
                    except Exception:
                        continue
            if not totals:
                return (np.nan, np.nan, np.nan)
            arr = np.asarray(totals, dtype=float)
            return (float(arr.sum()), float(arr.max()), float(len(set(map(str, totals)))))

        vals = pd.DataFrame(df[list_col].map(usage_stats).tolist(), columns=["mp_value_mean", "mp_value_max", "mp_value_min"])
        vals["mp_value_std"] = np.nan
    else:
        vals = pd.DataFrame(
            {
                "mp_value_mean": np.nan,
                "mp_value_min": np.nan,
                "mp_value_max": np.nan,
                "mp_value_std": np.nan,
            },
            index=df.index,
        )
    out = pd.concat([out.reset_index(drop=True), vals.reset_index(drop=True)], axis=1)
    return _add_lifelog_minute(out)


def _window_bounds(row: pd.Series) -> dict[str, tuple[float, float]]:
    out = dict(ABS_WINDOWS)
    start = float(row["mp_sleep_start_min"]) if pd.notna(row["mp_sleep_start_min"]) else np.nan
    for name, (lo, hi) in REL_WINDOWS.items():
        if np.isfinite(start):
            out[name] = (start + lo, start + hi)
        else:
            out[name] = (np.nan, np.nan)
    return out


def _gap_features(minutes: np.ndarray, lo: float, hi: float) -> dict[str, float]:
    lo_i = int(np.floor(max(lo, DAY_START)))
    hi_i = int(np.ceil(min(hi, DAY_END)))
    if not np.isfinite(lo) or not np.isfinite(hi) or hi_i <= lo_i:
        return {
            "minute_count": np.nan,
            "obs_frac": np.nan,
            "first_hour": np.nan,
            "last_hour": np.nan,
            "span_min": np.nan,
            "longest_gap_min": np.nan,
            "median_gap_min": np.nan,
            "p90_gap_min": np.nan,
            "gap30_count": np.nan,
            "gap60_count": np.nan,
        }
    uniq = np.unique(minutes[(minutes >= lo_i) & (minutes < hi_i)].astype(int))
    denom = float(hi_i - lo_i)
    if uniq.size == 0:
        return {
            "minute_count": 0.0,
            "obs_frac": 0.0,
            "first_hour": np.nan,
            "last_hour": np.nan,
            "span_min": 0.0,
            "longest_gap_min": denom,
            "median_gap_min": denom,
            "p90_gap_min": denom,
            "gap30_count": 1.0 if denom >= 30 else 0.0,
            "gap60_count": 1.0 if denom >= 60 else 0.0,
        }
    internal = np.diff(uniq) - 1
    boundary = np.asarray([uniq[0] - lo_i, hi_i - uniq[-1] - 1], dtype=float)
    gaps = np.concatenate([internal.astype(float), boundary])
    return {
        "minute_count": float(uniq.size),
        "obs_frac": float(uniq.size / denom),
        "first_hour": float(uniq[0] / 60.0),
        "last_hour": float(uniq[-1] / 60.0),
        "span_min": float(uniq[-1] - uniq[0] + 1),
        "longest_gap_min": float(np.max(gaps)) if gaps.size else 0.0,
        "median_gap_min": float(np.median(gaps)) if gaps.size else 0.0,
        "p90_gap_min": float(np.quantile(gaps, 0.90)) if gaps.size else 0.0,
        "gap30_count": float((gaps >= 30).sum()),
        "gap60_count": float((gaps >= 60).sum()),
    }


def _aggregate_sensor(keys: pd.DataFrame, events: pd.DataFrame, sensor: str) -> pd.DataFrame:
    grouped = {k: g.reset_index(drop=True) for k, g in events.groupby(KEY, sort=False)}
    rows: list[dict[str, float | str | pd.Timestamp]] = []
    for row in keys.itertuples(index=False):
        key = (row.subject_id, row.lifelog_date)
        g = grouped.get(key)
        out: dict[str, float | str | pd.Timestamp] = {"subject_id": row.subject_id, "lifelog_date": row.lifelog_date}
        bounds = _window_bounds(pd.Series(row._asdict()))
        if g is None:
            minutes = np.asarray([], dtype=float)
            vals = pd.DataFrame(
                {
                    "mp_point_count": [],
                    "mp_unique_count": [],
                    "mp_value_mean": [],
                    "mp_value_min": [],
                    "mp_value_max": [],
                    "mp_value_std": [],
                }
            )
        else:
            minutes = g["mp_minute"].to_numpy(dtype=float)
            vals = g
        for win, (lo, hi) in bounds.items():
            prefix = f"mp_{sensor}_{win}"
            sel = (minutes >= lo) & (minutes < hi) if np.isfinite(lo) and np.isfinite(hi) else np.zeros_like(minutes, dtype=bool)
            part = vals.loc[sel] if len(vals) else vals
            gap = _gap_features(minutes, lo, hi)
            out[f"{prefix}_row_count"] = float(sel.sum())
            for name, value in gap.items():
                out[f"{prefix}_{name}"] = value
            for col, suffix in [
                ("mp_point_count", "point_sum"),
                ("mp_unique_count", "unique_sum"),
                ("mp_value_mean", "value_mean"),
                ("mp_value_min", "value_min"),
                ("mp_value_max", "value_max"),
                ("mp_value_std", "value_std"),
            ]:
                if col not in part.columns or len(part) == 0:
                    out[f"{prefix}_{suffix}"] = np.nan
                    continue
                x = pd.to_numeric(part[col], errors="coerce")
                if suffix in {"point_sum", "unique_sum"}:
                    out[f"{prefix}_{suffix}"] = float(x.sum()) if x.notna().any() else 0.0
                else:
                    out[f"{prefix}_{suffix}"] = float(x.mean()) if x.notna().any() else np.nan
            if "mp_value_mean" in part.columns and len(part):
                x = pd.to_numeric(part["mp_value_mean"], errors="coerce")
                out[f"{prefix}_positive_frac"] = float((x > 0).mean()) if x.notna().any() else np.nan
            else:
                out[f"{prefix}_positive_frac"] = np.nan
        rows.append(out)
    return pd.DataFrame(rows)


def _subject_quantile(values: pd.Series, subjects: pd.Series, q: float) -> pd.Series:
    return values.groupby(subjects, sort=False).transform(lambda x: x.quantile(q))


def _add_subject_context(out: pd.DataFrame, base_cols: list[str]) -> None:
    subjects = out["subject_id"]
    is_weekend = out["mp_is_weekend"].astype(int)
    for col in base_cols:
        raw = pd.to_numeric(out[col], errors="coerce")
        if raw.notna().sum() < 40 or raw.nunique(dropna=True) <= 1:
            continue
        g = raw.groupby(subjects, sort=False)
        mean = g.transform("mean")
        med = g.transform("median")
        std = g.transform("std").replace(0.0, np.nan)
        prev1 = g.shift(1)
        next1 = g.shift(-1)
        same_weekend_med = raw.groupby([subjects, is_weekend], sort=False).transform("median")
        absdev = (raw - med).abs()
        q90 = _subject_quantile(absdev, subjects, 0.90)
        out[f"{col}_dev_subj_med"] = raw - med
        out[f"{col}_zdev_subj_mean"] = (raw - mean) / std
        out[f"{col}_same_weekend_dev"] = raw - same_weekend_med
        out[f"{col}_prev1_delta"] = raw - prev1
        out[f"{col}_next1_delta"] = next1 - raw
        out[f"{col}_very_irregular_flag"] = (absdev > q90).astype(float)
        out[f"{col}_missing"] = raw.isna().astype(float)


def _add_cross_features(out: pd.DataFrame) -> list[str]:
    added: list[str] = []
    windows = list(ABS_WINDOWS) + list(REL_WINDOWS)
    watch = ["hr", "wlight", "pedo"]
    phone = ["screen", "charge", "activity"]
    env = ["wifi", "ble", "gps", "usage", "ambience", "mlight"]
    for win in windows:
        def cols(sensors: list[str], suffix: str) -> list[str]:
            return [f"mp_{sensor}_{win}_{suffix}" for sensor in sensors if f"mp_{sensor}_{win}_{suffix}" in out.columns]

        watch_obs = cols(watch, "obs_frac")
        phone_obs = cols(phone, "obs_frac")
        env_obs = cols(env, "obs_frac")
        if watch_obs:
            out[f"mp_watch_{win}_obs_frac_mean"] = out[watch_obs].mean(axis=1)
            out[f"mp_watch_{win}_obs_frac_min"] = out[watch_obs].min(axis=1)
            out[f"mp_watch_{win}_obs_frac_std"] = out[watch_obs].std(axis=1)
            added.extend([f"mp_watch_{win}_obs_frac_mean", f"mp_watch_{win}_obs_frac_min", f"mp_watch_{win}_obs_frac_std"])
        if phone_obs:
            out[f"mp_phone_{win}_obs_frac_mean"] = out[phone_obs].mean(axis=1)
            out[f"mp_phone_{win}_obs_frac_min"] = out[phone_obs].min(axis=1)
            out[f"mp_phone_{win}_obs_frac_std"] = out[phone_obs].std(axis=1)
            added.extend([f"mp_phone_{win}_obs_frac_mean", f"mp_phone_{win}_obs_frac_min", f"mp_phone_{win}_obs_frac_std"])
        if env_obs:
            out[f"mp_env_{win}_obs_frac_mean"] = out[env_obs].mean(axis=1)
            out[f"mp_env_{win}_obs_frac_max"] = out[env_obs].max(axis=1)
            added.extend([f"mp_env_{win}_obs_frac_mean", f"mp_env_{win}_obs_frac_max"])
        if watch_obs and phone_obs:
            out[f"mp_watch_minus_phone_{win}_obs_frac"] = out[watch_obs].mean(axis=1) - out[phone_obs].mean(axis=1)
            out[f"mp_watch_to_phone_{win}_obs_ratio"] = out[watch_obs].mean(axis=1) / out[phone_obs].mean(axis=1).replace(0.0, np.nan)
            added.extend([f"mp_watch_minus_phone_{win}_obs_frac", f"mp_watch_to_phone_{win}_obs_ratio"])
        all_obs = watch_obs + phone_obs + env_obs
        if all_obs:
            active = (out[all_obs] > 0.01).astype(float)
            out[f"mp_sensor_active_count_{win}"] = active.sum(axis=1)
            out[f"mp_sensor_obs_frac_spread_{win}"] = out[all_obs].max(axis=1) - out[all_obs].min(axis=1)
            added.extend([f"mp_sensor_active_count_{win}", f"mp_sensor_obs_frac_spread_{win}"])
        if f"mp_hr_{win}_obs_frac" in out and f"mp_wlight_{win}_obs_frac" in out:
            out[f"mp_hr_minus_wlight_{win}_obs_frac"] = out[f"mp_hr_{win}_obs_frac"] - out[f"mp_wlight_{win}_obs_frac"]
            added.append(f"mp_hr_minus_wlight_{win}_obs_frac")
        if f"mp_hr_{win}_longest_gap_min" in out and f"mp_pedo_{win}_longest_gap_min" in out:
            out[f"mp_watch_gap_sum_{win}"] = out[f"mp_hr_{win}_longest_gap_min"] + out[f"mp_pedo_{win}_longest_gap_min"]
            added.append(f"mp_watch_gap_sum_{win}")
    for sensor in ["hr", "wlight", "pedo", "screen", "charge", "activity"]:
        pre = f"mp_{sensor}_pre3h_obs_frac"
        core = f"mp_{sensor}_core5h_obs_frac"
        if pre in out and core in out:
            out[f"mp_{sensor}_pre3_to_core_obs_drop"] = out[pre] - out[core]
            added.append(f"mp_{sensor}_pre3_to_core_obs_drop")
    return added


def build_features() -> pd.DataFrame:
    keys = _read_keys()
    sensor_defs = {
        "screen": _numeric_frame("ch2025_mScreenStatus.parquet", ["m_screen_use"]),
        "charge": _numeric_frame("ch2025_mACStatus.parquet", ["m_charging"]),
        "activity": _numeric_frame("ch2025_mActivity.parquet", ["m_activity"]),
        "mlight": _numeric_frame("ch2025_mLight.parquet", ["m_light"]),
        "wlight": _numeric_frame("ch2025_wLight.parquet", ["w_light"]),
        "pedo": _numeric_frame("ch2025_wPedo.parquet", ["step", "step_frequency", "speed", "burned_calories"]),
        "hr": _hr_frame(),
        "wifi": _scan_frame("ch2025_mWifi.parquet", "m_wifi", "bssid"),
        "ble": _scan_frame("ch2025_mBle.parquet", "m_ble", "address"),
        "gps": _scan_frame("ch2025_mGps.parquet", "m_gps", gps_speed=True),
        "usage": _scan_frame("ch2025_mUsageStats.parquet", "m_usage_stats"),
        "ambience": _scan_frame("ch2025_mAmbience.parquet", "m_ambience"),
    }
    out = keys[KEY + ["sleep_date", "split", "mp_sleep_start_min", "mp_dayofweek", "mp_is_weekend"]].copy()
    for sensor, events in sensor_defs.items():
        block = _aggregate_sensor(keys, events, sensor)
        out = out.merge(block, on=KEY, how="left")

    cross_cols = _add_cross_features(out)
    base_cols = [c for c in out.columns if c.startswith("mp_") and c not in {"mp_dayofweek", "mp_is_weekend"}]
    base_cols = [c for c in base_cols if out[c].dtype.kind in "biufc"]
    _add_subject_context(out, base_cols + cross_cols)

    feature_cols = [c for c in out.columns if c.startswith("mp_")]
    out[feature_cols] = out[feature_cols].replace([np.inf, -np.inf], np.nan)
    return out


def main() -> None:
    features = build_features()
    path = OUT / "measurement_process_features.parquet"
    features.to_parquet(path, index=False)
    numeric = [c for c in features.columns if c.startswith("mp_")]
    coverage = pd.DataFrame(
        {
            "feature": numeric,
            "non_null": [int(features[c].notna().sum()) for c in numeric],
            "nunique": [int(features[c].nunique(dropna=True)) for c in numeric],
        }
    ).sort_values(["non_null", "nunique"], ascending=[False, False])
    coverage.to_csv(OUT / "measurement_process_feature_coverage.csv", index=False)
    print(f"saved {path} shape={features.shape} mp_features={len(numeric)}")
    print(coverage.head(30).to_string(index=False))


if __name__ == "__main__":
    main()
