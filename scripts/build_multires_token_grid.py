from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def time_bin(frame: pd.DataFrame, minutes: int) -> pd.DataFrame:
    out = frame.copy()
    out["date"] = out["timestamp"].dt.strftime("%Y-%m-%d")
    minutes_from_midnight = out["timestamp"].dt.hour * 60 + out["timestamp"].dt.minute
    out["tok"] = (minutes_from_midnight // minutes).astype(int)
    return out


def scalar_agg(path: Path, value_col: str, prefix: str, minutes: int, how: str = "mean") -> pd.DataFrame:
    df = time_bin(pd.read_parquet(path)[["subject_id", "timestamp", value_col]], minutes)
    grouped = df.groupby(["subject_id", "date", "tok"], sort=False)[value_col]
    parts = [grouped.count().rename(f"{prefix}_n")]
    if how == "sum":
        parts.append(grouped.sum().rename(f"{prefix}_sum"))
    else:
        parts.append(grouped.mean().rename(f"{prefix}_mean"))
        parts.append(grouped.max().rename(f"{prefix}_max"))
    return pd.concat(parts, axis=1).reset_index()


def activity_agg(path: Path, minutes: int) -> pd.DataFrame:
    df = time_bin(pd.read_parquet(path), minutes)
    grouped = df.groupby(["subject_id", "date", "tok"], sort=False)
    out = grouped["m_activity"].count().rename("act_n").to_frame()
    out["act_still_ratio"] = grouped["m_activity"].apply(lambda s: float((s == 0).mean()))
    out["act_walk_ratio"] = grouped["m_activity"].apply(lambda s: float((s == 1).mean()))
    out["act_run_ratio"] = grouped["m_activity"].apply(lambda s: float((s == 2).mean()))
    out["act_vehicle_ratio"] = grouped["m_activity"].apply(lambda s: float((s == 4).mean()))
    out["act_other_ratio"] = grouped["m_activity"].apply(lambda s: float((~s.isin([0, 1, 2, 4])).mean()))
    return out.reset_index()


def pedo_agg(path: Path, minutes: int) -> pd.DataFrame:
    cols = ["subject_id", "timestamp", "step", "running_step", "walking_step", "distance", "speed", "burned_calories"]
    df = time_bin(pd.read_parquet(path)[cols], minutes)
    grouped = df.groupby(["subject_id", "date", "tok"], sort=False)
    return grouped.agg(
        pedo_n=("step", "count"),
        step_sum=("step", "sum"),
        running_step_sum=("running_step", "sum"),
        walking_step_sum=("walking_step", "sum"),
        distance_sum=("distance", "sum"),
        speed_mean=("speed", "mean"),
        speed_max=("speed", "max"),
        cal_sum=("burned_calories", "sum"),
    ).reset_index()


def list_numbers(values: Any) -> list[float]:
    if isinstance(values, np.ndarray):
        values = values.tolist()
    if not isinstance(values, list):
        return []
    out = []
    for item in values:
        try:
            out.append(float(item))
        except (TypeError, ValueError):
            continue
    return out


def as_items(values: Any) -> list[Any]:
    if isinstance(values, np.ndarray):
        values = values.tolist()
    return values if isinstance(values, list) else []


def hr_agg(path: Path, minutes: int) -> pd.DataFrame:
    df = pd.read_parquet(path)
    rows = []
    for sid, ts, values in df[["subject_id", "timestamp", "heart_rate"]].itertuples(index=False):
        nums = list_numbers(values)
        if nums:
            arr = np.asarray(nums, dtype=float)
            diff = np.diff(arr)
            rows.append(
                {
                    "subject_id": sid,
                    "timestamp": ts,
                    "hr_n": len(arr),
                    "hr_mean": float(np.mean(arr)),
                    "hr_std": float(np.std(arr)),
                    "hr_min": float(np.min(arr)),
                    "hr_max": float(np.max(arr)),
                    "hr_rmssd": float(np.sqrt(np.mean(diff * diff))) if len(diff) else 0.0,
                }
            )
    flat = time_bin(pd.DataFrame(rows), minutes)
    grouped = flat.groupby(["subject_id", "date", "tok"], sort=False)
    return grouped.agg(
        hr_rows=("hr_n", "count"),
        hr_n=("hr_n", "sum"),
        hr_mean=("hr_mean", "mean"),
        hr_std=("hr_std", "mean"),
        hr_min=("hr_min", "min"),
        hr_max=("hr_max", "max"),
        hr_rmssd=("hr_rmssd", "mean"),
    ).reset_index()


def gps_agg(path: Path, minutes: int) -> pd.DataFrame:
    df = pd.read_parquet(path)
    rows = []
    for sid, ts, values in df[["subject_id", "timestamp", "m_gps"]].itertuples(index=False):
        values = as_items(values)
        if not values:
            continue
        speeds, lats, lons, alts = [], [], [], []
        for item in values:
            if not isinstance(item, dict):
                continue
            for bucket, key in ((speeds, "speed"), (lats, "latitude"), (lons, "longitude"), (alts, "altitude")):
                if key in item and item[key] is not None:
                    bucket.append(float(item[key]))
        if speeds or lats:
            rows.append(
                {
                    "subject_id": sid,
                    "timestamp": ts,
                    "gps_n": len(values),
                    "gps_speed_mean": float(np.mean(speeds)) if speeds else np.nan,
                    "gps_speed_max": float(np.max(speeds)) if speeds else np.nan,
                    "gps_lat_std": float(np.std(lats)) if lats else np.nan,
                    "gps_lon_std": float(np.std(lons)) if lons else np.nan,
                    "gps_alt_mean": float(np.mean(alts)) if alts else np.nan,
                }
            )
    flat = time_bin(pd.DataFrame(rows), minutes)
    grouped = flat.groupby(["subject_id", "date", "tok"], sort=False)
    return grouped.agg(
        gps_rows=("gps_n", "count"),
        gps_n=("gps_n", "sum"),
        gps_speed_mean=("gps_speed_mean", "mean"),
        gps_speed_max=("gps_speed_max", "max"),
        gps_lat_std=("gps_lat_std", "mean"),
        gps_lon_std=("gps_lon_std", "mean"),
        gps_alt_mean=("gps_alt_mean", "mean"),
    ).reset_index()


AMBIENCE_BUCKETS = {
    "speech": ("speech", "conversation", "talk"),
    "music": ("music", "song", "instrument"),
    "vehicle": ("vehicle", "car", "truck", "motor", "traffic"),
    "outdoor": ("outside", "outdoor", "rural", "urban"),
    "indoor": ("inside", "room", "domestic", "office"),
    "alarm": ("alarm", "bell", "chime", "ring"),
    "silence": ("silence", "quiet"),
}


def ambience_agg(path: Path, minutes: int) -> pd.DataFrame:
    df = pd.read_parquet(path)
    rows = []
    for sid, ts, values in df[["subject_id", "timestamp", "m_ambience"]].itertuples(index=False):
        row = {"subject_id": sid, "timestamp": ts, "amb_n": 0}
        for bucket in AMBIENCE_BUCKETS:
            row[f"amb_{bucket}"] = 0.0
        values = as_items(values)
        if values:
            row["amb_n"] = len(values)
            for item in values:
                if not isinstance(item, (list, tuple)) or len(item) < 2:
                    continue
                label = str(item[0]).lower()
                try:
                    score = float(item[1])
                except (TypeError, ValueError):
                    continue
                for bucket, tokens in AMBIENCE_BUCKETS.items():
                    if any(token in label for token in tokens):
                        row[f"amb_{bucket}"] += score
        rows.append(row)
    flat = time_bin(pd.DataFrame(rows), minutes)
    return flat.groupby(["subject_id", "date", "tok"], sort=False).mean(numeric_only=True).reset_index()


def radio_agg(path: Path, object_col: str, prefix: str, id_key: str, minutes: int) -> pd.DataFrame:
    df = pd.read_parquet(path)
    rows = []
    for sid, ts, values in df[["subject_id", "timestamp", object_col]].itertuples(index=False):
        count = 0
        rssis = []
        ids = set()
        values = as_items(values)
        if values:
            count = len(values)
            for item in values:
                if not isinstance(item, dict):
                    continue
                if id_key in item:
                    ids.add(str(item[id_key]))
                if "rssi" in item and item["rssi"] is not None:
                    rssis.append(float(item["rssi"]))
        rows.append(
            {
                "subject_id": sid,
                "timestamp": ts,
                f"{prefix}_scan_n": count,
                f"{prefix}_unique_n": len(ids),
                f"{prefix}_rssi_mean": float(np.mean(rssis)) if rssis else np.nan,
                f"{prefix}_rssi_max": float(np.max(rssis)) if rssis else np.nan,
            }
        )
    flat = time_bin(pd.DataFrame(rows), minutes)
    return flat.groupby(["subject_id", "date", "tok"], sort=False).mean(numeric_only=True).reset_index()


def usage_agg(path: Path, minutes: int) -> pd.DataFrame:
    df = pd.read_parquet(path)
    rows = []
    for sid, ts, values in df[["subject_id", "timestamp", "m_usage_stats"]].itertuples(index=False):
        total, max_time, count = 0.0, 0.0, 0
        values = as_items(values)
        if values:
            count = len(values)
            for item in values:
                if isinstance(item, dict) and "total_time" in item and item["total_time"] is not None:
                    val = float(item["total_time"])
                    total += val
                    max_time = max(max_time, val)
        rows.append({"subject_id": sid, "timestamp": ts, "usage_app_n": count, "usage_total": total, "usage_max": max_time})
    flat = time_bin(pd.DataFrame(rows), minutes)
    return flat.groupby(["subject_id", "date", "tok"], sort=False).mean(numeric_only=True).reset_index()


def merge_parts(parts: list[pd.DataFrame]) -> pd.DataFrame:
    merged = parts[0]
    for part in parts[1:]:
        merged = merged.merge(part, on=["subject_id", "date", "tok"], how="outer", validate="one_to_one")
    return merged.sort_values(["subject_id", "date", "tok"]).reset_index(drop=True)


def add_cross_modal_features(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["body_activity"] = out.get("act_walk_ratio", 0).fillna(0) + out.get("act_run_ratio", 0).fillna(0) + np.log1p(out.get("step_sum", 0).fillna(0))
    out["phone_activity"] = out.get("screen_mean", 0).fillna(0) + out.get("usage_total", 0).fillna(0).pipe(np.log1p)
    out["mobility_activity"] = out.get("gps_speed_mean", 0).fillna(0) + out.get("speed_mean", 0).fillna(0)
    out["body_phone_gap"] = out["body_activity"] - out["phone_activity"]
    out["mobility_phone_gap"] = out["mobility_activity"] - out["phone_activity"]
    out["sensor_coverage_n"] = out[[col for col in out.columns if col.endswith("_n") or col.endswith("_rows")]].notna().sum(axis=1)
    return out


def build_grid(data_dir: Path, minutes: int) -> pd.DataFrame:
    parts = [
        activity_agg(data_dir / "ch2025_mActivity.parquet", minutes),
        scalar_agg(data_dir / "ch2025_mScreenStatus.parquet", "m_screen_use", "screen", minutes),
        scalar_agg(data_dir / "ch2025_mACStatus.parquet", "m_charging", "charging", minutes),
        scalar_agg(data_dir / "ch2025_mLight.parquet", "m_light", "mlight", minutes),
        scalar_agg(data_dir / "ch2025_wLight.parquet", "w_light", "wlight", minutes),
        pedo_agg(data_dir / "ch2025_wPedo.parquet", minutes),
        hr_agg(data_dir / "ch2025_wHr.parquet", minutes),
        gps_agg(data_dir / "ch2025_mGps.parquet", minutes),
        ambience_agg(data_dir / "ch2025_mAmbience.parquet", minutes),
        radio_agg(data_dir / "ch2025_mWifi.parquet", "m_wifi", "wifi", "bssid", minutes),
        radio_agg(data_dir / "ch2025_mBle.parquet", "m_ble", "ble", "address", minutes),
        usage_agg(data_dir / "ch2025_mUsageStats.parquet", minutes),
    ]
    return add_cross_modal_features(merge_parts(parts))


def run(args: argparse.Namespace) -> None:
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    grid = build_grid(Path(args.data_dir), args.minutes)
    output_path = output_dir / f"multires_{args.minutes}min_grid.parquet"
    grid.to_parquet(output_path, index=False)
    report = {
        "minutes": args.minutes,
        "path": str(output_path),
        "shape": list(grid.shape),
        "subjects": sorted(grid["subject_id"].unique().tolist()),
        "date_min": str(grid["date"].min()),
        "date_max": str(grid["date"].max()),
        "columns": grid.columns.tolist(),
        "non_null_rate": {col: float(grid[col].notna().mean()) for col in grid.columns if col not in ["subject_id", "date", "tok"]},
    }
    (output_dir / f"multires_{args.minutes}min_grid_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    md = [
        f"# Multires {args.minutes}min Token Grid",
        "",
        f"- Output: `{output_path}`",
        f"- Shape: `{grid.shape[0]} x {grid.shape[1]}`",
        f"- Dates: `{grid['date'].min()}` to `{grid['date'].max()}`",
        f"- Subjects: `{grid['subject_id'].nunique()}`",
        "",
        "This grid keeps raw stream coverage as signal instead of hiding missingness. Object-list streams are first summarized row-wise, then aggregated into fixed within-day tokens.",
    ]
    (output_dir / f"multires_{args.minutes}min_grid_report.md").write_text("\n".join(md), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build raw-sensor multi-resolution token grids.")
    parser.add_argument("--data-dir", default="data/ch2025_data_items")
    parser.add_argument("--output-dir", default="artifacts")
    parser.add_argument("--minutes", type=int, default=10)
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
