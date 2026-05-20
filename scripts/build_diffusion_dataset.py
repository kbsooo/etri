from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
ZERO_VALUE_COLUMNS = {"running_step", "walking_step"}


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, float) and np.isnan(value):
        return []
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, list):
        return value
    return []


def as_pair(value: Any) -> tuple[Any, Any] | None:
    if isinstance(value, np.ndarray):
        value = value.tolist()
    if isinstance(value, (list, tuple)) and len(value) >= 2:
        return value[0], value[1]
    return None


def stable_bucket(value: str, buckets: int) -> int:
    digest = hashlib.md5(value.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % buckets


def entropy_from_counts(counts: np.ndarray) -> float:
    total = counts.sum()
    if total <= 0:
        return np.nan
    p = counts[counts > 0] / total
    return float(-(p * np.log2(p + 1e-12)).sum())


def target_frame(data_dir: Path) -> pd.DataFrame:
    train = pd.read_csv(data_dir / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    test = pd.read_csv(data_dir / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    test[TARGETS] = np.nan
    rows = pd.concat([train.assign(split="train", is_labeled=1), test.assign(split="test", is_labeled=0)], ignore_index=True)
    rows["lifelog_date"] = rows["lifelog_date"].dt.date
    rows["sleep_date"] = rows["sleep_date"].dt.date
    rows = rows.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True)
    rows["weekday"] = pd.to_datetime(rows["lifelog_date"]).dt.dayofweek
    rows["is_weekend"] = rows["weekday"].isin([5, 6]).astype(int)
    first = rows.groupby("subject_id")["lifelog_date"].transform("min")
    rows["day_index_subject"] = (pd.to_datetime(rows["lifelog_date"]) - pd.to_datetime(first)).dt.days.astype(int)
    return rows


class TensorBuilder:
    def __init__(self, day_rows: pd.DataFrame) -> None:
        self.day_rows = day_rows
        self.day_lookup = {(r.subject_id, r.lifelog_date): i for i, r in day_rows.iterrows()}
        self.features: list[np.ndarray] = []
        self.masks: list[np.ndarray] = []
        self.channel_names: list[str] = []
        self.channel_modalities: list[str] = []

    @property
    def n_days(self) -> int:
        return len(self.day_rows)

    def add_hourly_frame(self, modality: str, frame: pd.DataFrame, feature_cols: list[str]) -> None:
        if frame.empty:
            return
        for col in feature_cols:
            values = np.zeros((self.n_days, 24), dtype=np.float32)
            mask = np.zeros((self.n_days, 24), dtype=np.float32)
            for row in frame[["subject_id", "lifelog_date", "hour", col]].itertuples(index=False):
                idx = self.day_lookup.get((row.subject_id, row.lifelog_date))
                if idx is None:
                    continue
                hour = int(row.hour)
                value = getattr(row, col)
                if 0 <= hour < 24 and pd.notna(value):
                    values[idx, hour] = float(value)
                    mask[idx, hour] = 1.0
            self.features.append(values)
            self.masks.append(mask)
            self.channel_names.append(f"{modality}__{col}")
            self.channel_modalities.append(modality)

    def arrays(self) -> tuple[np.ndarray, np.ndarray]:
        x = np.stack(self.features, axis=-1).astype(np.float32)
        mask = np.stack(self.masks, axis=-1).astype(np.float32)
        return x, mask


def add_scalar_modality(
    builder: TensorBuilder,
    item_dir: Path,
    file_name: str,
    modality: str,
    value_cols: list[str],
) -> None:
    df = pd.read_parquet(item_dir / file_name)
    df["lifelog_date"] = df["timestamp"].dt.date
    df["hour"] = df["timestamp"].dt.hour
    usable_cols = [c for c in value_cols if c not in ZERO_VALUE_COLUMNS and df[c].nunique(dropna=True) > 1]
    group = df.groupby(["subject_id", "lifelog_date", "hour"], sort=False)
    frames = [group.size().rename("row_count").reset_index()]
    feature_cols = ["row_count"]
    for col in usable_cols:
        stats = group[col].agg(["mean", "max", "min", "std", "sum"]).reset_index()
        stats = stats.rename(columns={stat: f"{col}_{stat}" for stat in ["mean", "max", "min", "std", "sum"]})
        frames.append(stats)
        feature_cols.extend([f"{col}_{stat}" for stat in ["mean", "max", "min", "std", "sum"]])
        if pd.api.types.is_numeric_dtype(df[col]):
            zero_rate = group[col].agg(lambda s: float((s == 0).mean())).rename(f"{col}_zero_rate").reset_index()
            frames.append(zero_rate)
            feature_cols.append(f"{col}_zero_rate")
    out = frames[0]
    for frame in frames[1:]:
        out = out.merge(frame, on=["subject_id", "lifelog_date", "hour"], how="left")
    builder.add_hourly_frame(modality, out, feature_cols)


def add_activity(builder: TensorBuilder, item_dir: Path) -> None:
    df = pd.read_parquet(item_dir / "ch2025_mActivity.parquet")
    df["lifelog_date"] = df["timestamp"].dt.date
    df["hour"] = df["timestamp"].dt.hour
    classes = sorted(df["m_activity"].dropna().unique().tolist())
    group_keys = ["subject_id", "lifelog_date", "hour"]
    counts = df.groupby(group_keys).size().rename("row_count").reset_index()
    wide = pd.crosstab([df["subject_id"], df["lifelog_date"], df["hour"]], df["m_activity"]).reset_index()
    wide.columns = group_keys + [f"class_{int(c)}_count" for c in classes]
    out = counts.merge(wide, on=group_keys, how="left")
    class_count_cols = [f"class_{int(c)}_count" for c in classes]
    for col in class_count_cols:
        out[col.replace("_count", "_rate")] = out[col] / out["row_count"].replace(0, np.nan)
    out["entropy"] = out[class_count_cols].apply(lambda row: entropy_from_counts(row.to_numpy(dtype=float)), axis=1)
    feature_cols = ["row_count", "entropy"] + [c.replace("_count", "_rate") for c in class_count_cols]
    builder.add_hourly_frame("mActivity", out, feature_cols)


def add_ambience(builder: TensorBuilder, item_dir: Path, top_k: int) -> None:
    df = pd.read_parquet(item_dir / "ch2025_mAmbience.parquet")
    top_counter: Counter[str] = Counter()
    parsed: list[tuple[str, Any, int, str | None, float, float]] = []
    for sid, ts, items in df[["subject_id", "timestamp", "m_ambience"]].itertuples(index=False):
        labels = []
        probs = []
        for item in as_list(items):
            pair = as_pair(item)
            if pair is None:
                continue
            labels.append(str(pair[0]))
            probs.append(float(pair[1]))
        top_label = labels[0] if labels else None
        if top_label is not None:
            top_counter[top_label] += 1
        parsed.append((sid, ts.date(), ts.hour, top_label, probs[0] if probs else np.nan, float(np.sum(probs)) if probs else np.nan))
    top_labels = [label for label, _ in top_counter.most_common(top_k)]
    long = pd.DataFrame(parsed, columns=["subject_id", "lifelog_date", "hour", "top_label", "top_prob", "prob_sum"])
    group_keys = ["subject_id", "lifelog_date", "hour"]
    out = long.groupby(group_keys).agg(row_count=("top_label", "size"), top_prob_mean=("top_prob", "mean"), prob_sum_mean=("prob_sum", "mean")).reset_index()
    counts = pd.crosstab([long["subject_id"], long["lifelog_date"], long["hour"]], long["top_label"]).reset_index()
    counts = counts.rename(columns={label: f"top_{i:02d}_{safe_name(label)}_rate" for i, label in enumerate(top_labels)})
    out = out.merge(counts, on=group_keys, how="left")
    rate_cols = []
    for i, label in enumerate(top_labels):
        col = f"top_{i:02d}_{safe_name(label)}_rate"
        if col not in out:
            out[col] = 0.0
        else:
            out[col] = out[col] / out["row_count"].replace(0, np.nan)
        rate_cols.append(col)
    builder.add_hourly_frame("mAmbience", out, ["row_count", "top_prob_mean", "prob_sum_mean"] + rate_cols)


def safe_name(value: str) -> str:
    return "".join(ch if ch.isalnum() else "_" for ch in value)[:40]


def add_device_list(
    builder: TensorBuilder,
    item_dir: Path,
    file_name: str,
    modality: str,
    list_col: str,
    id_key: str,
    buckets: int,
) -> None:
    df = pd.read_parquet(item_dir / file_name)
    group_acc: dict[tuple[str, Any, int], dict[str, Any]] = defaultdict(lambda: {"rows": 0, "scan": 0, "ids": set(), "classes": set(), "rssis": [], "buckets": np.zeros(buckets, dtype=np.float32)})
    for sid, ts, items in df[["subject_id", "timestamp", list_col]].itertuples(index=False):
        key = (sid, ts.date(), int(ts.hour))
        acc = group_acc[key]
        acc["rows"] += 1
        for item in as_list(items):
            if not isinstance(item, dict):
                continue
            ident = str(item.get(id_key, ""))
            if ident:
                acc["ids"].add(ident)
                acc["scan"] += 1
                acc["buckets"][stable_bucket(ident, buckets)] += 1.0
            if item.get("device_class") is not None:
                acc["classes"].add(str(item["device_class"]))
            if item.get("rssi") is not None:
                acc["rssis"].append(float(item["rssi"]))
    rows = []
    for (sid, date, hour), acc in group_acc.items():
        rssis = np.asarray(acc["rssis"], dtype=float)
        rec = {
            "subject_id": sid,
            "lifelog_date": date,
            "hour": hour,
            "row_count": acc["rows"],
            "scan_count": acc["scan"],
            "unique_count": len(acc["ids"]),
            "class_unique_count": len(acc["classes"]),
            "rssi_mean": float(np.mean(rssis)) if len(rssis) else np.nan,
            "rssi_max": float(np.max(rssis)) if len(rssis) else np.nan,
            "rssi_min": float(np.min(rssis)) if len(rssis) else np.nan,
        }
        for bucket in range(buckets):
            rec[f"id_hash_{bucket:02d}"] = float(acc["buckets"][bucket])
        rows.append(rec)
    out = pd.DataFrame(rows)
    feature_cols = ["row_count", "scan_count", "unique_count", "class_unique_count", "rssi_mean", "rssi_max", "rssi_min"] + [f"id_hash_{b:02d}" for b in range(buckets)]
    builder.add_hourly_frame(modality, out, feature_cols)


def add_gps(builder: TensorBuilder, item_dir: Path) -> None:
    df = pd.read_parquet(item_dir / "ch2025_mGps.parquet")
    rows = []
    for sid, ts, items in df[["subject_id", "timestamp", "m_gps"]].itertuples(index=False):
        pts = [item for item in as_list(items) if isinstance(item, dict)]
        speeds = np.asarray([float(p["speed"]) for p in pts if p.get("speed") is not None], dtype=float)
        lats = np.asarray([float(p["latitude"]) for p in pts if p.get("latitude") is not None], dtype=float)
        lons = np.asarray([float(p["longitude"]) for p in pts if p.get("longitude") is not None], dtype=float)
        alts = np.asarray([float(p["altitude"]) for p in pts if p.get("altitude") is not None], dtype=float)
        rows.append(
            {
                "subject_id": sid,
                "lifelog_date": ts.date(),
                "hour": int(ts.hour),
                "minute_rows": 1,
                "point_count": len(pts),
                "speed_mean": float(np.mean(speeds)) if len(speeds) else np.nan,
                "speed_max": float(np.max(speeds)) if len(speeds) else np.nan,
                "stationary_rate": float((speeds <= 0.5).mean()) if len(speeds) else np.nan,
                "moving_rate": float((speeds > 1.5).mean()) if len(speeds) else np.nan,
                "lat_std": float(np.std(lats)) if len(lats) else np.nan,
                "lon_std": float(np.std(lons)) if len(lons) else np.nan,
                "alt_std": float(np.std(alts)) if len(alts) else np.nan,
            }
        )
    minute = pd.DataFrame(rows)
    group_keys = ["subject_id", "lifelog_date", "hour"]
    out = minute.groupby(group_keys).agg(
        row_count=("minute_rows", "sum"),
        point_count=("point_count", "sum"),
        speed_mean=("speed_mean", "mean"),
        speed_max=("speed_max", "max"),
        stationary_rate=("stationary_rate", "mean"),
        moving_rate=("moving_rate", "mean"),
        lat_std=("lat_std", "mean"),
        lon_std=("lon_std", "mean"),
        alt_std=("alt_std", "mean"),
    ).reset_index()
    builder.add_hourly_frame("mGps", out, ["row_count", "point_count", "speed_mean", "speed_max", "stationary_rate", "moving_rate", "lat_std", "lon_std", "alt_std"])


def add_usage(builder: TensorBuilder, item_dir: Path, buckets: int) -> None:
    df = pd.read_parquet(item_dir / "ch2025_mUsageStats.parquet")
    group_acc: dict[tuple[str, Any, int], dict[str, Any]] = defaultdict(lambda: {"rows": 0, "events": 0, "apps": set(), "times": [], "buckets": np.zeros(buckets, dtype=np.float32)})
    for sid, ts, items in df[["subject_id", "timestamp", "m_usage_stats"]].itertuples(index=False):
        key = (sid, ts.date(), int(ts.hour))
        acc = group_acc[key]
        acc["rows"] += 1
        for item in as_list(items):
            if not isinstance(item, dict):
                continue
            app = str(item.get("app_name", "")).strip()
            total_time = float(item.get("total_time", 0.0) or 0.0)
            if app:
                acc["apps"].add(app)
                acc["events"] += 1
                acc["buckets"][stable_bucket(app, buckets)] += np.log1p(total_time)
            acc["times"].append(total_time)
    rows = []
    for (sid, date, hour), acc in group_acc.items():
        times = np.asarray(acc["times"], dtype=float)
        rec = {
            "subject_id": sid,
            "lifelog_date": date,
            "hour": hour,
            "row_count": acc["rows"],
            "app_events": acc["events"],
            "unique_apps": len(acc["apps"]),
            "total_time_sum": float(np.sum(times)) if len(times) else 0.0,
            "total_time_max": float(np.max(times)) if len(times) else 0.0,
        }
        for bucket in range(buckets):
            rec[f"app_hash_{bucket:02d}"] = float(acc["buckets"][bucket])
        rows.append(rec)
    out = pd.DataFrame(rows)
    feature_cols = ["row_count", "app_events", "unique_apps", "total_time_sum", "total_time_max"] + [f"app_hash_{b:02d}" for b in range(buckets)]
    builder.add_hourly_frame("mUsageStats", out, feature_cols)


def add_hr(builder: TensorBuilder, item_dir: Path) -> None:
    df = pd.read_parquet(item_dir / "ch2025_wHr.parquet")
    rows = []
    for sid, ts, values in df[["subject_id", "timestamp", "heart_rate"]].itertuples(index=False):
        vals = np.asarray([float(v) for v in as_list(values) if v is not None], dtype=float)
        rows.append(
            {
                "subject_id": sid,
                "lifelog_date": ts.date(),
                "hour": int(ts.hour),
                "row_count": 1,
                "hr_points": len(vals),
                "hr_mean": float(np.mean(vals)) if len(vals) else np.nan,
                "hr_std": float(np.std(vals)) if len(vals) else np.nan,
                "hr_min": float(np.min(vals)) if len(vals) else np.nan,
                "hr_max": float(np.max(vals)) if len(vals) else np.nan,
                "hr_p10": float(np.percentile(vals, 10)) if len(vals) else np.nan,
                "hr_p90": float(np.percentile(vals, 90)) if len(vals) else np.nan,
            }
        )
    minute = pd.DataFrame(rows)
    group_keys = ["subject_id", "lifelog_date", "hour"]
    out = minute.groupby(group_keys).agg(
        row_count=("row_count", "sum"),
        hr_points=("hr_points", "sum"),
        hr_mean=("hr_mean", "mean"),
        hr_std=("hr_std", "mean"),
        hr_min=("hr_min", "min"),
        hr_max=("hr_max", "max"),
        hr_p10=("hr_p10", "mean"),
        hr_p90=("hr_p90", "mean"),
    ).reset_index()
    builder.add_hourly_frame("wHr", out, ["row_count", "hr_points", "hr_mean", "hr_std", "hr_min", "hr_max", "hr_p10", "hr_p90"])


def auto_transform(x_raw: np.ndarray, mask: np.ndarray, channel_names: list[str]) -> tuple[np.ndarray, dict[str, Any]]:
    x = x_raw.copy()
    stats: dict[str, Any] = {"channels": []}
    for idx, name in enumerate(channel_names):
        observed = mask[:, :, idx] > 0
        vals = x[:, :, idx][observed]
        if len(vals) == 0:
            stats["channels"].append({"name": name, "transform": "empty", "mean": 0.0, "std": 1.0, "clip_low": 0.0, "clip_high": 0.0})
            continue
        finite = vals[np.isfinite(vals)]
        if len(finite) == 0:
            finite = np.array([0.0], dtype=np.float32)
        clip_low = float(np.percentile(finite, 1))
        clip_high = float(np.percentile(finite, 99))
        min_v = float(np.min(finite))
        transform = "identity"
        if min_v >= 0.0 and (
            clip_high > 20.0
            or any(token in name for token in ["count", "sum", "points", "rows", "time", "step", "distance", "calories", "hash"])
        ):
            transform = "log1p"
            x[:, :, idx] = np.where(observed, np.log1p(np.clip(x[:, :, idx], 0.0, None)), x[:, :, idx])
            vals2 = x[:, :, idx][observed]
            clip_low = float(np.percentile(vals2, 1))
            clip_high = float(np.percentile(vals2, 99))
        clipped = np.clip(x[:, :, idx][observed], clip_low, clip_high)
        mean = float(np.mean(clipped))
        std = float(np.std(clipped))
        if std < 1e-6:
            std = 1.0
        x[:, :, idx] = np.where(observed, (np.clip(x[:, :, idx], clip_low, clip_high) - mean) / std, 0.0)
        stats["channels"].append({"name": name, "transform": transform, "mean": mean, "std": std, "clip_low": clip_low, "clip_high": clip_high})
    x = np.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0).astype(np.float32)
    return x, stats


def add_subject_deviations(x: np.ndarray, mask: np.ndarray, day_rows: pd.DataFrame, channel_names: list[str], modalities: list[str]) -> tuple[np.ndarray, np.ndarray, list[str], list[str]]:
    dev_features = []
    dev_masks = []
    dev_names = []
    dev_modalities = []
    subjects = day_rows["subject_id"].to_numpy()
    for ch_idx, name in enumerate(channel_names):
        dev = np.zeros_like(x[:, :, ch_idx], dtype=np.float32)
        dev_mask = mask[:, :, ch_idx].copy()
        for sid in np.unique(subjects):
            idx = subjects == sid
            observed = mask[idx, :, ch_idx] > 0
            values = x[idx, :, ch_idx]
            if observed.sum() == 0:
                continue
            baseline = float(np.mean(values[observed]))
            dev[idx, :] = np.where(observed, values - baseline, 0.0)
        dev_features.append(dev)
        dev_masks.append(dev_mask)
        dev_names.append(name + "__subject_dev")
        dev_modalities.append(modalities[ch_idx] + "_dev")
    return (
        np.concatenate([x, np.stack(dev_features, axis=-1)], axis=-1),
        np.concatenate([mask, np.stack(dev_masks, axis=-1)], axis=-1),
        channel_names + dev_names,
        modalities + dev_modalities,
    )


def build_dataset(args: argparse.Namespace) -> None:
    data_dir = Path(args.data_dir)
    item_dir = data_dir / "ch2025_data_items"
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = target_frame(data_dir)
    builder = TensorBuilder(rows)

    add_scalar_modality(builder, item_dir, "ch2025_mACStatus.parquet", "mACStatus", ["m_charging"])
    add_activity(builder, item_dir)
    add_ambience(builder, item_dir, args.ambience_top_k)
    add_device_list(builder, item_dir, "ch2025_mBle.parquet", "mBle", "m_ble", "address", args.device_hash_buckets)
    add_gps(builder, item_dir)
    add_scalar_modality(builder, item_dir, "ch2025_mLight.parquet", "mLight", ["m_light"])
    add_scalar_modality(builder, item_dir, "ch2025_mScreenStatus.parquet", "mScreenStatus", ["m_screen_use"])
    add_usage(builder, item_dir, args.app_hash_buckets)
    add_device_list(builder, item_dir, "ch2025_mWifi.parquet", "mWifi", "m_wifi", "bssid", args.device_hash_buckets)
    add_hr(builder, item_dir)
    add_scalar_modality(builder, item_dir, "ch2025_wLight.parquet", "wLight", ["w_light"])
    add_scalar_modality(
        builder,
        item_dir,
        "ch2025_wPedo.parquet",
        "wPedo",
        ["step", "step_frequency", "running_step", "walking_step", "distance", "speed", "burned_calories"],
    )

    x_raw, mask = builder.arrays()
    x, norm_stats = auto_transform(x_raw, mask, builder.channel_names)
    channel_names = builder.channel_names
    channel_modalities = builder.channel_modalities
    if args.add_subject_deviation:
        x, mask, channel_names, channel_modalities = add_subject_deviations(x, mask, rows, channel_names, channel_modalities)

    np.savez_compressed(output_dir / "hourly_tensor.npz", x=x, mask=mask.astype(np.float32), x_raw=x_raw.astype(np.float32))
    rows.to_csv(output_dir / "day_index.csv", index=False)
    metadata = {
        "shape": {"days": int(x.shape[0]), "hours": int(x.shape[1]), "channels": int(x.shape[2])},
        "channel_names": channel_names,
        "channel_modalities": channel_modalities,
        "normalization": norm_stats,
        "args": vars(args),
        "notes": [
            "All 700 subject-days in train plus submission_sample are represented.",
            "All 12 raw sensor modalities contribute channels.",
            "running_step and walking_step are omitted because they are constant zero.",
            "High-cardinality app/device identifiers are represented by stable hash buckets, not raw one-hot columns.",
        ],
    }
    (output_dir / "tensor_metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    coverage = pd.DataFrame(
        {
            "channel": channel_names,
            "modality": channel_modalities,
            "observed_rate": mask.mean(axis=(0, 1)),
            "nonzero_rate": (x != 0).mean(axis=(0, 1)),
        }
    )
    coverage.to_csv(output_dir / "channel_coverage.csv", index=False)
    print(f"wrote {output_dir / 'hourly_tensor.npz'} shape={x.shape}")
    print(f"channels={len(channel_names)} observed_rate_mean={mask.mean():.4f}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a 700-day hourly multimodal tensor for diffusion-style pretraining.")
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--output-dir", default="outputs/diffusion_encoder")
    parser.add_argument("--device-hash-buckets", type=int, default=16)
    parser.add_argument("--app-hash-buckets", type=int, default=16)
    parser.add_argument("--ambience-top-k", type=int, default=16)
    parser.add_argument("--add-subject-deviation", action=argparse.BooleanOptionalAction, default=True)
    return parser.parse_args()


if __name__ == "__main__":
    build_dataset(parse_args())
