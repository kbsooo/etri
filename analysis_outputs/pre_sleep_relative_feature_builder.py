from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ITEMS = DATA / "ch2025_data_items"
OUT = ROOT / "analysis_outputs"
KEY = ["subject_id", "lifelog_date"]
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]


WINDOWS = {
    "pre1h": (-1.0, 0.0),
    "pre3h": (-3.0, 0.0),
    "pre6h": (-6.0, 0.0),
    "post2h": (0.0, 2.0),
    "core5h": (1.0, 6.0),
}


def all_keys() -> pd.DataFrame:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    sub = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    train["split"] = "train"
    sub["split"] = "submission"
    keys = pd.concat([train[KEY + ["sleep_date", "split"]], sub[KEY + ["sleep_date", "split"]]], ignore_index=True)
    proxy = pd.read_parquet(OUT / "sleep_interval_proxy_features.parquet")
    keys = keys.merge(proxy[KEY + ["proxy_screen_step_start_hour", "proxy_screen_start_hour"]], on=KEY, how="left")
    start = keys["proxy_screen_step_start_hour"].fillna(keys["proxy_screen_start_hour"])
    keys["pre_sleep_start_ts"] = keys["lifelog_date"] + pd.to_timedelta(start, unit="h")
    return keys.sort_values(KEY).reset_index(drop=True)


def add_time(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df.sort_values(["subject_id", "timestamp"]).reset_index(drop=True)


def by_subject(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    return {str(sid): g.reset_index(drop=True) for sid, g in df.groupby("subject_id", sort=False)}


def stats_for_values(vals: pd.Series) -> dict[str, float]:
    arr = pd.to_numeric(vals, errors="coerce").to_numpy(dtype=float)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return {"count": 0.0, "mean": np.nan, "std": np.nan, "min": np.nan, "max": np.nan, "sum": 0.0, "last": np.nan}
    return {
        "count": float(arr.size),
        "mean": float(np.mean(arr)),
        "std": float(np.std(arr, ddof=1)) if arr.size > 1 else 0.0,
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
        "sum": float(np.sum(arr)),
        "last": float(arr[-1]),
    }


def aggregate_numeric(keys: pd.DataFrame, events: pd.DataFrame, value_cols: list[str], prefix: str) -> pd.DataFrame:
    subjects = by_subject(add_time(events))
    rows = []
    for row in keys.itertuples(index=False):
        sid = str(row.subject_id)
        start_ts = row.pre_sleep_start_ts
        out = {"subject_id": sid, "lifelog_date": row.lifelog_date}
        g = subjects.get(sid)
        for win, (lo, hi) in WINDOWS.items():
            if g is None or pd.isna(start_ts):
                part = None
            else:
                begin = start_ts + pd.Timedelta(hours=lo)
                end = start_ts + pd.Timedelta(hours=hi)
                part = g[(g["timestamp"] >= begin) & (g["timestamp"] < end)]
            for col in value_cols:
                stats = stats_for_values(pd.Series(dtype=float) if part is None else part[col])
                for name, val in stats.items():
                    out[f"presleep_{prefix}_{win}_{col}_{name}"] = val
        rows.append(out)
    return pd.DataFrame(rows)


def heart_rate_rows() -> pd.DataFrame:
    df = add_time(pd.read_parquet(ITEMS / "ch2025_wHr.parquet"))

    def arr_stats(x):
        arr = np.asarray(x if isinstance(x, list) else [], dtype=float)
        arr = arr[np.isfinite(arr)]
        if arr.size == 0:
            return (np.nan, np.nan, np.nan, np.nan, 0.0)
        return (float(arr.mean()), float(arr.min()), float(arr.max()), float(arr.std()), float(arr.size))

    vals = pd.DataFrame(df["heart_rate"].map(arr_stats).tolist(), columns=["hr_mean", "hr_min", "hr_max", "hr_std", "hr_points"])
    return pd.concat([df[["subject_id", "timestamp"]], vals], axis=1)


def usage_rows() -> pd.DataFrame:
    df = add_time(pd.read_parquet(ITEMS / "ch2025_mUsageStats.parquet"))
    keywords = {
        "chat": ["카카오톡", "메시지", "Messenger", "LINE", "WhatsApp", "Telegram"],
        "call": ["전화", "통화"],
        "search": ["NAVER", "Chrome", "Google", "삼성 인터넷", "Safari"],
        "video": ["YouTube", "Netflix", "TikTok", "동영상"],
        "music": ["Music", "멜론", "Spotify", "YouTube Music"],
        "finance": ["토스", "KB", "카카오뱅크", "뱅크", "증권"],
        "home": ["One UI 홈", "Launcher"],
        "health": ["헬스", "건강", "캐시워크", "Samsung Health"],
    }

    def row_stats(items):
        out = {f"kw_{k}_time": 0.0 for k in keywords}
        apps = set()
        total = []
        for item in items if isinstance(items, list) else []:
            if not isinstance(item, dict):
                continue
            app = str(item.get("app_name", ""))
            t = float(item.get("total_time") or 0.0)
            apps.add(app)
            total.append(t)
            lower = app.lower()
            for name, keys in keywords.items():
                if any(k.lower() in lower for k in keys):
                    out[f"kw_{name}_time"] += t
        out.update({"apps": float(len(apps)), "items": float(len(total)), "time_sum": float(sum(total)), "time_max": float(max(total) if total else 0.0)})
        return out

    vals = pd.DataFrame(df["m_usage_stats"].map(row_stats).tolist())
    return pd.concat([df[["subject_id", "timestamp"]], vals], axis=1)


def ambience_rows() -> pd.DataFrame:
    df = add_time(pd.read_parquet(ITEMS / "ch2025_mAmbience.parquet"))
    buckets = ["speech", "music", "vehicle", "inside", "outside", "silence", "animal", "water", "rain"]

    def row_stats(items):
        best_label = ""
        best_prob = np.nan
        if isinstance(items, list):
            for pair in items:
                try:
                    label = str(pair[0])
                    prob = float(pair[1])
                except Exception:
                    continue
                if pd.isna(best_prob) or prob > best_prob:
                    best_label = label
                    best_prob = prob
        lower = best_label.lower()
        out = {"top_prob": best_prob}
        for bucket in buckets:
            out[f"top_is_{bucket}"] = float(bucket in lower)
        return out

    vals = pd.DataFrame(df["m_ambience"].map(row_stats).tolist())
    return pd.concat([df[["subject_id", "timestamp"]], vals], axis=1)


def main() -> None:
    keys = all_keys()
    blocks = [
        aggregate_numeric(keys, pd.read_parquet(ITEMS / "ch2025_mScreenStatus.parquet"), ["m_screen_use"], "screen"),
        aggregate_numeric(keys, pd.read_parquet(ITEMS / "ch2025_mActivity.parquet"), ["m_activity"], "activity"),
        aggregate_numeric(keys, pd.read_parquet(ITEMS / "ch2025_mACStatus.parquet"), ["m_charging"], "charge"),
        aggregate_numeric(keys, pd.read_parquet(ITEMS / "ch2025_mLight.parquet"), ["m_light"], "mlight"),
        aggregate_numeric(keys, pd.read_parquet(ITEMS / "ch2025_wLight.parquet"), ["w_light"], "wlight"),
        aggregate_numeric(keys, pd.read_parquet(ITEMS / "ch2025_wPedo.parquet"), ["step", "step_frequency", "speed", "burned_calories"], "pedo"),
        aggregate_numeric(keys, heart_rate_rows(), ["hr_mean", "hr_min", "hr_max", "hr_std", "hr_points"], "hr"),
        aggregate_numeric(keys, usage_rows(), ["apps", "items", "time_sum", "time_max", "kw_chat_time", "kw_call_time", "kw_search_time", "kw_video_time", "kw_music_time", "kw_finance_time", "kw_home_time", "kw_health_time"], "usage"),
        aggregate_numeric(keys, ambience_rows(), ["top_prob", "top_is_speech", "top_is_music", "top_is_vehicle", "top_is_inside", "top_is_outside", "top_is_silence", "top_is_animal", "top_is_water", "top_is_rain"], "ambience"),
    ]
    out = keys[KEY + ["sleep_date", "split", "pre_sleep_start_ts"]].copy()
    for block in blocks:
        out = out.merge(block, on=KEY, how="left")
    out.to_parquet(OUT / "pre_sleep_relative_features.parquet", index=False)
    print(out.shape)
    print(out.filter(regex="^presleep_").shape[1], "presleep feature columns")


if __name__ == "__main__":
    main()
