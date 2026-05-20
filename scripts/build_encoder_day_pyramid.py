from __future__ import annotations

import argparse
import hashlib
import json
import math
import warnings
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY_COLUMNS = ["subject_id", "sleep_date", "lifelog_date"]


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


def safe_name(value: str) -> str:
    return "".join(ch if ch.isalnum() else "_" for ch in value)[:40]


def entropy_from_counts(counts: np.ndarray) -> float:
    total = counts.sum()
    if total <= 0:
        return np.nan
    p = counts[counts > 0] / total
    return float(-(p * np.log2(p + 1e-12)).sum())


def target_frame(data_dir: Path) -> pd.DataFrame:
    train = pd.read_csv(data_dir / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = pd.read_csv(data_dir / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample[TARGETS] = np.nan
    rows = pd.concat(
        [
            train.assign(split="train", is_labeled=1),
            sample.assign(split="test", is_labeled=0),
        ],
        ignore_index=True,
    )
    rows["lifelog_date"] = rows["lifelog_date"].dt.date
    rows["sleep_date"] = rows["sleep_date"].dt.date
    rows = rows.sort_values(["subject_id", "lifelog_date", "sleep_date"]).reset_index(drop=True)
    lifelog = pd.to_datetime(rows["lifelog_date"])
    rows["weekday"] = lifelog.dt.dayofweek.astype(int)
    rows["is_weekend"] = rows["weekday"].isin([5, 6]).astype(int)
    rows["month"] = lifelog.dt.month.astype(int)
    first = rows.groupby("subject_id")["lifelog_date"].transform("min")
    rows["day_index_subject"] = (pd.to_datetime(rows["lifelog_date"]) - pd.to_datetime(first)).dt.days.astype(int)
    rows["panel_index"] = rows.groupby("subject_id").cumcount().astype(float)
    denom = rows.groupby("subject_id")["panel_index"].transform("max").replace(0, 1)
    rows["panel_position"] = rows["panel_index"] / denom
    return rows


class FiveMinuteGridBuilder:
    def __init__(self, day_rows: pd.DataFrame, bin_minutes: int) -> None:
        if 1440 % bin_minutes != 0:
            raise ValueError("bin_minutes must divide 1440")
        self.day_rows = day_rows
        self.bin_minutes = bin_minutes
        self.slots = 1440 // bin_minutes
        self.day_lookup = {(r.subject_id, r.lifelog_date): i for i, r in day_rows.iterrows()}
        self.features: list[np.ndarray] = []
        self.masks: list[np.ndarray] = []
        self.channel_names: list[str] = []
        self.channel_modalities: list[str] = []

    @property
    def n_days(self) -> int:
        return len(self.day_rows)

    def add_binned_frame(self, modality: str, frame: pd.DataFrame, feature_cols: list[str]) -> None:
        if frame.empty:
            return
        needed = ["subject_id", "lifelog_date", "slot", *feature_cols]
        frame = frame[[c for c in needed if c in frame.columns]].copy()
        for col in feature_cols:
            if col not in frame.columns:
                continue
            values = np.zeros((self.n_days, self.slots), dtype=np.float32)
            mask = np.zeros((self.n_days, self.slots), dtype=np.float32)
            for row in frame[["subject_id", "lifelog_date", "slot", col]].itertuples(index=False):
                idx = self.day_lookup.get((row.subject_id, row.lifelog_date))
                if idx is None:
                    continue
                slot = int(row.slot)
                value = getattr(row, col)
                if 0 <= slot < self.slots and pd.notna(value):
                    values[idx, slot] = float(value)
                    mask[idx, slot] = 1.0
            self.features.append(values)
            self.masks.append(mask)
            self.channel_names.append(f"{modality}__{col}")
            self.channel_modalities.append(modality)

    def arrays(self) -> tuple[np.ndarray, np.ndarray]:
        if not self.features:
            raise ValueError("No grid features were added")
        x = np.stack(self.features, axis=-1).astype(np.float32)
        mask = np.stack(self.masks, axis=-1).astype(np.float32)
        return x, mask


def add_time_keys(df: pd.DataFrame, bin_minutes: int) -> pd.DataFrame:
    out = df.copy()
    ts = pd.to_datetime(out["timestamp"])
    out["lifelog_date"] = ts.dt.date
    minutes = ts.dt.hour * 60 + ts.dt.minute
    out["slot"] = (minutes // bin_minutes).astype(int)
    return out


def merge_feature_frames(frames: list[pd.DataFrame], keys: list[str]) -> pd.DataFrame:
    out = frames[0]
    for frame in frames[1:]:
        out = out.merge(frame, on=keys, how="outer")
    return out


def add_scalar_modality(
    builder: FiveMinuteGridBuilder,
    item_dir: Path,
    file_name: str,
    modality: str,
    value_cols: list[str],
    stats: tuple[str, ...] = ("mean", "max", "min", "std", "sum"),
) -> None:
    df = add_time_keys(pd.read_parquet(item_dir / file_name), builder.bin_minutes)
    group_keys = ["subject_id", "lifelog_date", "slot"]
    group = df.groupby(group_keys, sort=False)
    frames = [group.size().rename("row_count").reset_index()]
    feature_cols = ["row_count"]
    for col in value_cols:
        if col not in df.columns or df[col].nunique(dropna=True) <= 1:
            continue
        agg = group[col].agg(list(stats)).reset_index()
        rename = {stat: f"{col}_{stat}" for stat in stats}
        agg = agg.rename(columns=rename)
        frames.append(agg)
        feature_cols.extend(rename.values())
        if pd.api.types.is_numeric_dtype(df[col]):
            zero = group[col].agg(lambda s: float((s == 0).mean())).rename(f"{col}_zero_rate").reset_index()
            frames.append(zero)
            feature_cols.append(f"{col}_zero_rate")
    builder.add_binned_frame(modality, merge_feature_frames(frames, group_keys), feature_cols)


def add_activity(builder: FiveMinuteGridBuilder, item_dir: Path) -> None:
    df = add_time_keys(pd.read_parquet(item_dir / "ch2025_mActivity.parquet"), builder.bin_minutes)
    group_keys = ["subject_id", "lifelog_date", "slot"]
    counts = df.groupby(group_keys).size().rename("row_count").reset_index()
    wide = pd.crosstab([df["subject_id"], df["lifelog_date"], df["slot"]], df["m_activity"]).reset_index()
    classes = [c for c in wide.columns if c not in group_keys]
    rename = {c: f"class_{int(c)}_count" for c in classes}
    wide = wide.rename(columns=rename)
    out = counts.merge(wide, on=group_keys, how="left")
    class_count_cols = list(rename.values())
    for col in class_count_cols:
        out[col.replace("_count", "_rate")] = out[col] / out["row_count"].replace(0, np.nan)
    out["entropy"] = out[class_count_cols].apply(lambda row: entropy_from_counts(row.to_numpy(dtype=float)), axis=1)
    feature_cols = ["row_count", "entropy"] + [c.replace("_count", "_rate") for c in class_count_cols]
    builder.add_binned_frame("mActivity", out, feature_cols)


def add_ambience(builder: FiveMinuteGridBuilder, item_dir: Path, top_k: int) -> None:
    df = pd.read_parquet(item_dir / "ch2025_mAmbience.parquet")
    top_counter: Counter[str] = Counter()
    parsed: list[tuple[str, Any, int, str | None, float, float]] = []
    for sid, ts, items in df[["subject_id", "timestamp", "m_ambience"]].itertuples(index=False):
        labels: list[str] = []
        probs: list[float] = []
        for item in as_list(items):
            pair = as_pair(item)
            if pair is None:
                continue
            labels.append(str(pair[0]))
            probs.append(float(pair[1]))
        top_label = labels[0] if labels else None
        if top_label is not None:
            top_counter[top_label] += 1
        slot = (ts.hour * 60 + ts.minute) // builder.bin_minutes
        parsed.append((sid, ts.date(), int(slot), top_label, probs[0] if probs else np.nan, float(np.sum(probs)) if probs else np.nan))
    top_labels = [label for label, _ in top_counter.most_common(top_k)]
    long = pd.DataFrame(parsed, columns=["subject_id", "lifelog_date", "slot", "top_label", "top_prob", "prob_sum"])
    group_keys = ["subject_id", "lifelog_date", "slot"]
    out = long.groupby(group_keys).agg(
        row_count=("top_label", "size"),
        top_prob_mean=("top_prob", "mean"),
        prob_sum_mean=("prob_sum", "mean"),
    ).reset_index()
    counts = pd.crosstab([long["subject_id"], long["lifelog_date"], long["slot"]], long["top_label"]).reset_index()
    counts = counts.rename(columns={label: f"top_{i:02d}_{safe_name(label)}_rate" for i, label in enumerate(top_labels)})
    out = out.merge(counts, on=group_keys, how="left")
    rate_cols: list[str] = []
    for i, label in enumerate(top_labels):
        col = f"top_{i:02d}_{safe_name(label)}_rate"
        if col not in out:
            out[col] = 0.0
        else:
            out[col] = out[col] / out["row_count"].replace(0, np.nan)
        rate_cols.append(col)
    builder.add_binned_frame("mAmbience", out, ["row_count", "top_prob_mean", "prob_sum_mean", *rate_cols])


def add_device_list(
    builder: FiveMinuteGridBuilder,
    item_dir: Path,
    file_name: str,
    modality: str,
    list_col: str,
    id_key: str,
    buckets: int,
) -> None:
    df = pd.read_parquet(item_dir / file_name)
    group_acc: dict[tuple[str, Any, int], dict[str, Any]] = defaultdict(
        lambda: {"rows": 0, "scan": 0, "ids": set(), "classes": set(), "rssis": [], "buckets": np.zeros(buckets, dtype=np.float32)}
    )
    for sid, ts, items in df[["subject_id", "timestamp", list_col]].itertuples(index=False):
        key = (sid, ts.date(), int((ts.hour * 60 + ts.minute) // builder.bin_minutes))
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
    for (sid, date, slot), acc in group_acc.items():
        rssis = np.asarray(acc["rssis"], dtype=float)
        rec = {
            "subject_id": sid,
            "lifelog_date": date,
            "slot": slot,
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
    feature_cols = [
        "row_count",
        "scan_count",
        "unique_count",
        "class_unique_count",
        "rssi_mean",
        "rssi_max",
        "rssi_min",
        *[f"id_hash_{b:02d}" for b in range(buckets)],
    ]
    builder.add_binned_frame(modality, out, feature_cols)


def add_gps(builder: FiveMinuteGridBuilder, item_dir: Path) -> None:
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
                "slot": int((ts.hour * 60 + ts.minute) // builder.bin_minutes),
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
    group_keys = ["subject_id", "lifelog_date", "slot"]
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
    builder.add_binned_frame(
        "mGps",
        out,
        ["row_count", "point_count", "speed_mean", "speed_max", "stationary_rate", "moving_rate", "lat_std", "lon_std", "alt_std"],
    )


def add_usage(builder: FiveMinuteGridBuilder, item_dir: Path, buckets: int) -> None:
    df = pd.read_parquet(item_dir / "ch2025_mUsageStats.parquet")
    group_acc: dict[tuple[str, Any, int], dict[str, Any]] = defaultdict(
        lambda: {"rows": 0, "events": 0, "apps": set(), "times": [], "buckets": np.zeros(buckets, dtype=np.float32)}
    )
    for sid, ts, items in df[["subject_id", "timestamp", "m_usage_stats"]].itertuples(index=False):
        key = (sid, ts.date(), int((ts.hour * 60 + ts.minute) // builder.bin_minutes))
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
                acc["buckets"][stable_bucket(app, buckets)] += np.log1p(max(total_time, 0.0))
            acc["times"].append(total_time)
    rows = []
    for (sid, date, slot), acc in group_acc.items():
        times = np.asarray(acc["times"], dtype=float)
        rec = {
            "subject_id": sid,
            "lifelog_date": date,
            "slot": slot,
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
    feature_cols = ["row_count", "app_events", "unique_apps", "total_time_sum", "total_time_max", *[f"app_hash_{b:02d}" for b in range(buckets)]]
    builder.add_binned_frame("mUsageStats", out, feature_cols)


def add_hr(builder: FiveMinuteGridBuilder, item_dir: Path) -> None:
    df = pd.read_parquet(item_dir / "ch2025_wHr.parquet")
    rows = []
    for sid, ts, values in df[["subject_id", "timestamp", "heart_rate"]].itertuples(index=False):
        vals = np.asarray([float(v) for v in as_list(values) if v is not None], dtype=float)
        rows.append(
            {
                "subject_id": sid,
                "lifelog_date": ts.date(),
                "slot": int((ts.hour * 60 + ts.minute) // builder.bin_minutes),
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
    group_keys = ["subject_id", "lifelog_date", "slot"]
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
    builder.add_binned_frame("wHr", out, ["row_count", "hr_points", "hr_mean", "hr_std", "hr_min", "hr_max", "hr_p10", "hr_p90"])


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
    return np.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0).astype(np.float32), stats


def subject_global_baselines(x: np.ndarray, mask: np.ndarray, day_rows: pd.DataFrame) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray], np.ndarray]:
    subjects = day_rows["subject_id"].astype(str).to_numpy()
    global_denom = mask.sum(axis=0)
    global_base = np.divide((x * mask).sum(axis=0), np.maximum(global_denom, 1.0), out=np.zeros_like(x[0]), where=global_denom > 0)
    subject_base: dict[str, np.ndarray] = {}
    subject_avail: dict[str, np.ndarray] = {}
    for sid in sorted(np.unique(subjects)):
        idx = subjects == sid
        denom = mask[idx].sum(axis=0)
        base = np.divide((x[idx] * mask[idx]).sum(axis=0), np.maximum(denom, 1.0), out=np.zeros_like(global_base), where=denom > 0)
        base = np.where(denom > 0, base, global_base)
        subject_base[sid] = base.astype(np.float32)
        subject_avail[sid] = (denom > 0).astype(np.float32)
    return subject_base, subject_avail, global_base.astype(np.float32)


def master_signature(master_path: Path, day_rows: pd.DataFrame, n_components: int) -> np.ndarray:
    master = pd.read_parquet(master_path).copy()
    for col in KEY_COLUMNS:
        if col in master.columns:
            master[col] = master[col].astype(str)
    keys = day_rows[KEY_COLUMNS].astype(str)
    numeric_cols = [
        col
        for col in master.select_dtypes(include=[np.number]).columns
        if col not in TARGETS and not col.startswith("pred_")
    ]
    merged = keys.merge(master[KEY_COLUMNS + numeric_cols], on=KEY_COLUMNS, how="left", validate="one_to_one")
    arr = merged[numeric_cols].replace([np.inf, -np.inf], np.nan).to_numpy(dtype=float)
    med = np.nanmedian(arr, axis=0)
    med = np.where(np.isfinite(med), med, 0.0)
    missing = ~np.isfinite(arr)
    if missing.any():
        arr[missing] = np.take(med, np.where(missing)[1])
    low = np.percentile(arr, 1, axis=0)
    high = np.percentile(arr, 99, axis=0)
    arr = np.clip(arr, low, high)
    mean = arr.mean(axis=0)
    std = arr.std(axis=0)
    std = np.where(std > 1e-8, std, 1.0)
    z = (arr - mean) / std
    n_comp = min(n_components, z.shape[1], max(1, z.shape[0] - 1))
    _, _, vt = np.linalg.svd(z, full_matrices=False)
    return (z @ vt[:n_comp].T).astype(np.float32)


def build_normal_twin(
    x: np.ndarray,
    mask: np.ndarray,
    day_rows: pd.DataFrame,
    signature: np.ndarray,
    k: int,
) -> tuple[np.ndarray, np.ndarray, pd.DataFrame]:
    n_days = x.shape[0]
    subjects = day_rows["subject_id"].astype(str).to_numpy()
    weekdays = day_rows["weekday"].to_numpy(dtype=int)
    panel_pos = day_rows["panel_index"].to_numpy(dtype=float)
    by_subject: dict[str, np.ndarray] = {
        sid: np.where(subjects == sid)[0] for sid in sorted(np.unique(subjects))
    }
    subject_base, subject_avail, global_base = subject_global_baselines(x, mask, day_rows)
    twin = np.zeros_like(x, dtype=np.float32)
    twin_mask = np.zeros_like(mask, dtype=np.float32)
    rows: list[dict[str, Any]] = []
    sig_dim = max(1, signature.shape[1])
    for i in range(n_days):
        sid = subjects[i]
        candidates = by_subject[sid][by_subject[sid] != i]
        if len(candidates) == 0:
            candidates = np.arange(n_days, dtype=int)
            candidates = candidates[candidates != i]
        sig_dist = np.sqrt(((signature[candidates] - signature[i]) ** 2).sum(axis=1) / sig_dim)
        weekday_bonus = np.where(weekdays[candidates] == weekdays[i], 0.0, 0.35)
        time_dist = np.abs(panel_pos[candidates] - panel_pos[i]) / 14.0
        score = sig_dist + weekday_bonus + 0.15 * time_dist
        order = np.argsort(score)[: min(k, len(candidates))]
        chosen = candidates[order]
        chosen_score = score[order]
        scale = float(np.median(chosen_score[chosen_score > 1e-6])) if np.any(chosen_score > 1e-6) else 1.0
        weights = np.exp(-chosen_score / max(scale, 1e-3)).astype(np.float32)
        if float(weights.sum()) <= 0:
            weights = np.ones(len(chosen), dtype=np.float32)
        weights = weights / weights.sum()
        obs = mask[chosen]
        denom = (obs * weights[:, None, None]).sum(axis=0)
        num = (x[chosen] * obs * weights[:, None, None]).sum(axis=0)
        base = np.divide(num, np.maximum(denom, 1e-6), out=np.zeros_like(x[0]), where=denom > 0)
        fallback = subject_base[sid]
        base = np.where(denom > 0, base, fallback)
        base = np.where(np.isfinite(base), base, global_base)
        twin[i] = base.astype(np.float32)
        twin_mask[i] = np.where(denom > 0, 1.0, subject_avail[sid]).astype(np.float32)
        rows.append(
            {
                "row_index": i,
                "subject_id": sid,
                "lifelog_date": str(day_rows.loc[i, "lifelog_date"]),
                "n_neighbors": int(len(chosen)),
                "mean_neighbor_score": float(chosen_score.mean()) if len(chosen_score) else np.nan,
                "same_weekday_neighbors": int((weekdays[chosen] == weekdays[i]).sum()) if len(chosen) else 0,
                "neighbor_rows": ",".join(map(str, chosen.tolist())),
            }
        )
    return twin, twin_mask, pd.DataFrame(rows)


def time_since_last_seen(mask: np.ndarray) -> np.ndarray:
    n_days, n_slots, n_channels = mask.shape
    gap = np.zeros_like(mask, dtype=np.float32)
    for day in range(n_days):
        last = np.full(n_channels, -1, dtype=np.int32)
        for slot in range(n_slots):
            seen = mask[day, slot] > 0
            last[seen] = slot
            gap[day, slot] = np.where(last >= 0, slot - last, n_slots)
    return (gap / float(n_slots)).astype(np.float32)


def contiguous_segments(condition: np.ndarray, min_len: int = 1) -> list[tuple[int, int]]:
    segments: list[tuple[int, int]] = []
    start: int | None = None
    for idx, value in enumerate(condition.astype(bool).tolist() + [False]):
        if value and start is None:
            start = idx
        elif not value and start is not None:
            if idx - start >= min_len:
                segments.append((start, idx))
            start = None
    return segments


EVENT_TYPES = [
    "missing_gap",
    "screen_burst",
    "night_phone",
    "charging_no_hr",
    "activity_burst",
    "mobility_trip",
    "high_hr_rest",
    "late_light",
    "novel_place",
    "off_wrist",
    "sleep_interrupt",
    "usage_burst",
]

DAYPARTS = [
    ("late_night", 0, 6),
    ("morning", 6, 12),
    ("afternoon", 12, 18),
    ("evening", 18, 22),
    ("night", 22, 24),
]


def channel_index(channel_names: list[str], contains: str) -> int | None:
    for idx, name in enumerate(channel_names):
        if contains in name:
            return idx
    return None


def segment_feature(
    event_type: str,
    start: int,
    end: int,
    intensity: float,
    delta_abs: float,
    coverage: float,
    slots: int,
) -> np.ndarray:
    type_vec = np.zeros(len(EVENT_TYPES), dtype=np.float32)
    type_vec[EVENT_TYPES.index(event_type)] = 1.0
    center = (start + end - 1) / 2.0
    center_frac = center / max(slots - 1, 1)
    hour = center_frac * 24.0
    part_vec = np.zeros(len(DAYPARTS), dtype=np.float32)
    for i, (_, lo, hi) in enumerate(DAYPARTS):
        if lo <= hour < hi:
            part_vec[i] = 1.0
            break
    intensity_scaled = math.tanh(float(intensity) / 8.0)
    delta_scaled = math.tanh(float(delta_abs) / 4.0)
    scalar = np.asarray(
        [
            start / slots,
            end / slots,
            (end - start) / slots,
            math.sin(2.0 * math.pi * center_frac),
            math.cos(2.0 * math.pi * center_frac),
            intensity_scaled,
            delta_scaled,
            float(np.clip(coverage, 0.0, 1.0)),
        ],
        dtype=np.float32,
    )
    return np.concatenate([type_vec, scalar, part_vec])


def build_event_tokens(
    x: np.ndarray,
    x_raw: np.ndarray,
    mask: np.ndarray,
    delta: np.ndarray,
    channel_names: list[str],
    max_events: int,
    max_events_per_type: int,
) -> tuple[np.ndarray, np.ndarray, list[str]]:
    n_days, slots, _ = x.shape
    event_dim = len(EVENT_TYPES) + 8 + len(DAYPARTS)
    events = np.zeros((n_days, max_events, event_dim), dtype=np.float32)
    event_mask = np.zeros((n_days, max_events), dtype=np.float32)
    idx_screen = channel_index(channel_names, "mScreenStatus__m_screen_use_mean")
    idx_charge = channel_index(channel_names, "mACStatus__m_charging_mean")
    idx_hr = channel_index(channel_names, "wHr__hr_mean")
    idx_step = channel_index(channel_names, "wPedo__step_sum")
    idx_pedo_speed = channel_index(channel_names, "wPedo__speed_mean")
    idx_gps_speed = channel_index(channel_names, "mGps__speed_mean")
    idx_gps_moving = channel_index(channel_names, "mGps__moving_rate")
    idx_mlight = channel_index(channel_names, "mLight__m_light_mean")
    idx_wlight = channel_index(channel_names, "wLight__w_light_mean")
    idx_wifi = channel_index(channel_names, "mWifi__unique_count")
    idx_ble = channel_index(channel_names, "mBle__unique_count")
    idx_usage = channel_index(channel_names, "mUsageStats__total_time_sum")
    idx_wlight_seen = channel_index(channel_names, "wLight__row_count")
    idx_pedo_seen = channel_index(channel_names, "wPedo__row_count")
    for day in range(n_days):
        candidates: list[tuple[float, np.ndarray]] = []

        coverage = mask[day].mean(axis=1)
        for start, end in contiguous_segments(coverage < 0.05, min_len=6):
            intensity = (1.0 - float(coverage[start:end].mean())) * (end - start) / 12.0
            candidates.append((intensity, segment_feature("missing_gap", start, end, intensity, 0.0, float(coverage[start:end].mean()), slots)))

        if idx_screen is not None:
            screen = (x_raw[day, :, idx_screen] > 0.5) & (mask[day, :, idx_screen] > 0)
            for start, end in contiguous_segments(screen, min_len=2):
                dabs = float(np.abs(delta[day, start:end, idx_screen]).mean())
                intensity = float(screen[start:end].mean()) * (end - start) / 6.0 + dabs
                event_name = "night_phone" if start < slots // 4 or start >= int(slots * 22 / 24) else "screen_burst"
                candidates.append((intensity, segment_feature(event_name, start, end, intensity, dabs, 1.0, slots)))

        if idx_charge is not None and idx_hr is not None:
            charge_no_hr = (x_raw[day, :, idx_charge] > 0.5) & (mask[day, :, idx_charge] > 0) & (mask[day, :, idx_hr] < 0.5)
            for start, end in contiguous_segments(charge_no_hr, min_len=3):
                intensity = (end - start) / 12.0
                candidates.append((intensity, segment_feature("charging_no_hr", start, end, intensity, 0.0, 0.0, slots)))

        if idx_step is not None:
            step_burst = (x[day, :, idx_step] > 1.0) & (mask[day, :, idx_step] > 0)
            for start, end in contiguous_segments(step_burst, min_len=1):
                dabs = float(np.abs(delta[day, start:end, idx_step]).mean())
                intensity = float(np.maximum(x[day, start:end, idx_step], 0).sum()) / 3.0 + dabs
                candidates.append((intensity, segment_feature("activity_burst", start, end, intensity, dabs, 1.0, slots)))

        mobility = np.zeros(slots, dtype=bool)
        for idx in [idx_gps_speed, idx_gps_moving, idx_pedo_speed]:
            if idx is not None:
                mobility |= (x[day, :, idx] > 0.8) & (mask[day, :, idx] > 0)
        for start, end in contiguous_segments(mobility, min_len=2):
            valid_idx = [idx for idx in [idx_gps_speed, idx_gps_moving, idx_pedo_speed] if idx is not None]
            dabs = float(np.abs(delta[day, start:end, valid_idx]).mean()) if valid_idx else 0.0
            intensity = (end - start) / 8.0 + dabs
            candidates.append((intensity, segment_feature("mobility_trip", start, end, intensity, dabs, 1.0, slots)))

        if idx_hr is not None:
            rest = np.ones(slots, dtype=bool)
            for idx in [idx_step, idx_gps_speed, idx_pedo_speed]:
                if idx is not None:
                    rest &= (x[day, :, idx] < 0.2) | (mask[day, :, idx] < 0.5)
            high_hr = (x[day, :, idx_hr] > 1.0) & (mask[day, :, idx_hr] > 0) & rest
            for start, end in contiguous_segments(high_hr, min_len=2):
                dabs = float(np.abs(delta[day, start:end, idx_hr]).mean())
                intensity = float(np.maximum(x[day, start:end, idx_hr], 0).mean()) + dabs
                candidates.append((intensity, segment_feature("high_hr_rest", start, end, intensity, dabs, 1.0, slots)))

        light_idxs = [idx for idx in [idx_mlight, idx_wlight] if idx is not None]
        if light_idxs:
            late = np.zeros(slots, dtype=bool)
            late[: slots // 4] = True
            late[int(slots * 22 / 24) :] = True
            light_high = late.copy()
            seen_any = np.zeros(slots, dtype=bool)
            for idx in light_idxs:
                light_high &= (x[day, :, idx] > 0.8) | (mask[day, :, idx] < 0.5)
                seen_any |= mask[day, :, idx] > 0
            light_high &= seen_any
            for start, end in contiguous_segments(light_high, min_len=1):
                dabs = float(np.abs(delta[day, start:end, light_idxs]).mean())
                intensity = float(np.maximum(x[day, start:end, light_idxs], 0).mean()) + dabs
                candidates.append((intensity, segment_feature("late_light", start, end, intensity, dabs, 1.0, slots)))

        place_idxs = [idx for idx in [idx_wifi, idx_ble] if idx is not None]
        if place_idxs:
            novel = np.zeros(slots, dtype=bool)
            for idx in place_idxs:
                novel |= (x[day, :, idx] > 1.0) & (mask[day, :, idx] > 0)
            for start, end in contiguous_segments(novel, min_len=1):
                dabs = float(np.abs(delta[day, start:end, place_idxs]).mean())
                intensity = float(np.maximum(x[day, start:end, place_idxs], 0).mean()) + dabs
                candidates.append((intensity, segment_feature("novel_place", start, end, intensity, dabs, 1.0, slots)))

        watch_idxs = [idx for idx in [idx_hr, idx_wlight_seen, idx_pedo_seen] if idx is not None]
        if watch_idxs:
            off = (mask[day, :, watch_idxs].mean(axis=1) < 0.1)
            for start, end in contiguous_segments(off, min_len=6):
                intensity = (end - start) / 12.0
                candidates.append((intensity, segment_feature("off_wrist", start, end, intensity, 0.0, 0.0, slots)))

        if idx_usage is not None:
            usage = (x[day, :, idx_usage] > 1.0) & (mask[day, :, idx_usage] > 0)
            for start, end in contiguous_segments(usage, min_len=1):
                dabs = float(np.abs(delta[day, start:end, idx_usage]).mean())
                intensity = float(np.maximum(x[day, start:end, idx_usage], 0).sum()) / 2.0 + dabs
                candidates.append((intensity, segment_feature("usage_burst", start, end, intensity, dabs, 1.0, slots)))

        if idx_screen is not None or idx_step is not None:
            night = np.zeros(slots, dtype=bool)
            night[: slots // 4] = True
            night[int(slots * 22 / 24) :] = True
            interrupt = night.copy()
            source_idxs = []
            if idx_screen is not None:
                interrupt &= ((x_raw[day, :, idx_screen] > 0.5) & (mask[day, :, idx_screen] > 0)) | ~night
                source_idxs.append(idx_screen)
            if idx_step is not None:
                interrupt |= night & (x[day, :, idx_step] > 0.8) & (mask[day, :, idx_step] > 0)
                source_idxs.append(idx_step)
            interrupt &= night
            for start, end in contiguous_segments(interrupt, min_len=1):
                dabs = float(np.abs(delta[day, start:end, source_idxs]).mean()) if source_idxs else 0.0
                intensity = (end - start) / 4.0 + dabs
                candidates.append((intensity, segment_feature("sleep_interrupt", start, end, intensity, dabs, 1.0, slots)))

        limited_candidates: list[tuple[float, np.ndarray]] = []
        for event_type_idx in range(len(EVENT_TYPES)):
            typed = [(score, vec) for score, vec in candidates if int(np.argmax(vec[: len(EVENT_TYPES)])) == event_type_idx]
            typed.sort(key=lambda item: item[0], reverse=True)
            limited_candidates.extend(typed[:max_events_per_type])
        limited_candidates.sort(key=lambda item: item[0], reverse=True)
        for pos, (_, vec) in enumerate(limited_candidates[:max_events]):
            events[day, pos] = vec
            event_mask[day, pos] = 1.0
    names = [f"type__{name}" for name in EVENT_TYPES] + [
        "start_frac",
        "end_frac",
        "duration_frac",
        "center_sin",
        "center_cos",
        "intensity",
        "abs_delta",
        "coverage",
    ] + [f"daypart__{name}" for name, _, _ in DAYPARTS]
    return events, event_mask, names


PROTOTYPE_GROUPS: dict[str, tuple[str, ...]] = {
    "phone": ("mScreenStatus", "mUsageStats", "mACStatus"),
    "physiology": ("wHr", "wPedo"),
    "mobility": ("mGps", "wPedo", "mActivity"),
    "light_ambience": ("mLight", "wLight", "mAmbience"),
    "social_place": ("mWifi", "mBle", "mGps"),
    "missingness": ("__mask__",),
    "sleep_proxy": ("wHr", "wPedo", "mScreenStatus", "mLight", "wLight"),
}


def longest_false_run(mask_1d: np.ndarray) -> float:
    longest = 0
    current = 0
    for val in mask_1d.astype(bool):
        if val:
            current = 0
        else:
            current += 1
            longest = max(longest, current)
    return float(longest)


def safe_nanstd(values: np.ndarray, axis: tuple[int, ...]) -> np.ndarray:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        return np.nan_to_num(np.nanstd(values, axis=axis), nan=0.0, posinf=0.0, neginf=0.0)


def safe_nanmax(values: np.ndarray, axis: tuple[int, ...]) -> np.ndarray:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        return np.nan_to_num(np.nanmax(values, axis=axis), nan=0.0, posinf=0.0, neginf=0.0)


def safe_nanpercentile(values: np.ndarray, q: float, axis: tuple[int, ...]) -> np.ndarray:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        return np.nan_to_num(np.nanpercentile(values, q, axis=axis), nan=0.0, posinf=0.0, neginf=0.0)


def group_summary_features(
    x: np.ndarray,
    mask: np.ndarray,
    delta: np.ndarray,
    gap: np.ndarray,
    channel_names: list[str],
) -> tuple[np.ndarray, list[str], list[str]]:
    summaries: list[np.ndarray] = []
    row_names: list[str] = []
    feature_names = [
        "mean",
        "std",
        "p90",
        "max",
        "delta_abs_mean",
        "delta_abs_p90",
        "coverage",
        "night_mean",
        "night_coverage",
        "longest_gap",
        "gap_mean",
    ]
    slots = x.shape[1]
    night_slots = np.r_[0 : slots // 4, int(slots * 22 / 24) : slots]
    for group_name, prefixes in PROTOTYPE_GROUPS.items():
        if "__mask__" in prefixes:
            group_mask = mask.mean(axis=2)
            group_gap = gap.mean(axis=2)
            arr = np.column_stack(
                [
                    group_mask.mean(axis=1),
                    group_mask.std(axis=1),
                    np.percentile(group_mask, 90, axis=1),
                    group_mask.max(axis=1),
                    (1.0 - group_mask).mean(axis=1),
                    np.percentile(1.0 - group_mask, 90, axis=1),
                    group_mask.mean(axis=1),
                    group_mask[:, night_slots].mean(axis=1),
                    group_mask[:, night_slots].mean(axis=1),
                    np.asarray([longest_false_run(row) / slots for row in group_mask > 0.05], dtype=np.float32),
                    group_gap.mean(axis=1),
                ]
            )
        else:
            idx = [i for i, name in enumerate(channel_names) if any(name.startswith(prefix + "__") for prefix in prefixes)]
            if not idx:
                arr = np.zeros((x.shape[0], len(feature_names)), dtype=np.float32)
            else:
                vals = x[:, :, idx]
                obs = mask[:, :, idx]
                deltas = np.abs(delta[:, :, idx])
                denom = np.maximum(obs.sum(axis=(1, 2)), 1.0)
                observed_vals = np.where(obs > 0, vals, np.nan)
                arr = np.column_stack(
                    [
                        np.nan_to_num(np.nansum(vals * obs, axis=(1, 2)) / denom),
                        safe_nanstd(observed_vals, axis=(1, 2)),
                        safe_nanpercentile(observed_vals, 90, axis=(1, 2)),
                        safe_nanmax(observed_vals, axis=(1, 2)),
                        np.nan_to_num((deltas * obs).sum(axis=(1, 2)) / denom),
                        safe_nanpercentile(np.where(obs > 0, deltas, np.nan), 90, axis=(1, 2)),
                        obs.mean(axis=(1, 2)),
                        np.nan_to_num(np.nansum(vals[:, night_slots] * obs[:, night_slots], axis=(1, 2)) / np.maximum(obs[:, night_slots].sum(axis=(1, 2)), 1.0)),
                        obs[:, night_slots].mean(axis=(1, 2)),
                        np.asarray([longest_false_run((obs_day.mean(axis=1) > 0.05)) / slots for obs_day in obs], dtype=np.float32),
                        gap[:, :, idx].mean(axis=(1, 2)),
                    ]
                )
        summaries.append(arr.astype(np.float32))
        row_names.append(group_name)
    return np.stack(summaries, axis=1).astype(np.float32), row_names, feature_names


def prototype_mixtures(group_features: np.ndarray, group_names: list[str], k: int, seed: int) -> tuple[np.ndarray, pd.DataFrame]:
    try:
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler
    except Exception as exc:  # pragma: no cover - sklearn is available in the project env.
        raise RuntimeError("scikit-learn is required to build prototype mixtures") from exc

    n_days, n_groups, _ = group_features.shape
    mixtures = np.zeros((n_days, n_groups, k), dtype=np.float32)
    rows: list[dict[str, Any]] = []
    for group_idx, group_name in enumerate(group_names):
        arr = group_features[:, group_idx, :]
        arr = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0)
        scaled = StandardScaler().fit_transform(arr)
        n_clusters = min(k, max(1, len(np.unique(np.round(scaled, 5), axis=0))))
        if n_clusters == 1:
            mixtures[:, group_idx, 0] = 1.0
            rows.append({"group": group_name, "prototype": 0, "count": int(n_days), "inertia": 0.0})
            continue
        model = KMeans(n_clusters=n_clusters, n_init=20, random_state=seed + group_idx)
        labels = model.fit_predict(scaled)
        dist = np.linalg.norm(scaled[:, None, :] - model.cluster_centers_[None, :, :], axis=2)
        temperature = float(np.median(dist[dist > 1e-6])) if np.any(dist > 1e-6) else 1.0
        logits = -dist / max(temperature, 1e-3)
        logits = logits - logits.max(axis=1, keepdims=True)
        soft = np.exp(logits)
        soft = soft / soft.sum(axis=1, keepdims=True)
        mixtures[:, group_idx, :n_clusters] = soft.astype(np.float32)
        for proto in range(n_clusters):
            rows.append(
                {
                    "group": group_name,
                    "prototype": int(proto),
                    "count": int((labels == proto).sum()),
                    "inertia": float(model.inertia_),
                }
            )
    return mixtures, pd.DataFrame(rows)


def day_context(day_rows: pd.DataFrame) -> tuple[np.ndarray, list[str]]:
    weekday = day_rows["weekday"].to_numpy(dtype=float)
    month = day_rows["month"].to_numpy(dtype=float)
    panel = day_rows["panel_position"].to_numpy(dtype=float)
    idx = day_rows["day_index_subject"].to_numpy(dtype=float)
    idx_scaled = idx / max(float(idx.max()), 1.0)
    context = np.column_stack(
        [
            np.sin(2.0 * np.pi * weekday / 7.0),
            np.cos(2.0 * np.pi * weekday / 7.0),
            day_rows["is_weekend"].to_numpy(dtype=float),
            np.sin(2.0 * np.pi * (month - 1.0) / 12.0),
            np.cos(2.0 * np.pi * (month - 1.0) / 12.0),
            panel,
            idx_scaled,
        ]
    ).astype(np.float32)
    return context, ["weekday_sin", "weekday_cos", "is_weekend", "month_sin", "month_cos", "panel_position", "subject_day_index_scaled"]


def time_features(slots: int) -> tuple[np.ndarray, list[str]]:
    slot = np.arange(slots, dtype=float)
    frac = slot / slots
    hour = frac * 24.0
    feats = [
        np.sin(2.0 * np.pi * frac),
        np.cos(2.0 * np.pi * frac),
        np.sin(4.0 * np.pi * frac),
        np.cos(4.0 * np.pi * frac),
    ]
    names = ["slot_sin_1", "slot_cos_1", "slot_sin_2", "slot_cos_2"]
    for name, lo, hi in DAYPARTS:
        feats.append(((hour >= lo) & (hour < hi)).astype(float))
        names.append(f"daypart__{name}")
    return np.column_stack(feats).astype(np.float32), names


def write_report(
    output_dir: Path,
    x_input: np.ndarray,
    base_channels: list[str],
    event_mask: np.ndarray,
    prototype_groups: list[str],
    metadata: dict[str, Any],
) -> None:
    lines = [
        "# Encoder Day Pyramid Report",
        "",
        f"- integrated input tensor: `{tuple(x_input.shape)}`",
        f"- base 5-min channels: `{len(base_channels)}`",
        f"- slots per day: `{metadata['shape']['slots']}`",
        f"- event tokens per day: max `{metadata['shape']['max_events']}`, mean observed `{event_mask.sum(axis=1).mean():.2f}`",
        f"- prototype groups: `{', '.join(prototype_groups)}`",
        "",
        "## Input Blocks",
        "",
        "- `actual__*`: normalized 5-minute sensor values.",
        "- `normal_twin__*`: label-free same-subject normal-day counterfactual baseline.",
        "- `delta__*` and `abs_delta__*`: today minus normal twin.",
        "- `observed__*`: sensor availability as data, not just a mask.",
        "- `gap_since__*`: time since each sensor/channel was last observed.",
        "- `event_tokens`: sparse headline events such as off-wrist gaps, night phone use, HR-at-rest, movement trips, and late light.",
        "- `prototype_mixture`: modality-wise soft assignment to sleep/phone/mobility/physiology/social-place style prototypes.",
    ]
    (output_dir / "encoder_day_pyramid_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_dataset(args: argparse.Namespace) -> None:
    data_dir = Path(args.data_dir)
    item_dir = data_dir / "ch2025_data_items"
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = target_frame(data_dir)
    builder = FiveMinuteGridBuilder(rows, args.bin_minutes)
    add_scalar_modality(builder, item_dir, "ch2025_mACStatus.parquet", "mACStatus", ["m_charging"], stats=("mean", "sum"))
    add_activity(builder, item_dir)
    add_ambience(builder, item_dir, args.ambience_top_k)
    add_device_list(builder, item_dir, "ch2025_mBle.parquet", "mBle", "m_ble", "address", args.device_hash_buckets)
    add_gps(builder, item_dir)
    add_scalar_modality(builder, item_dir, "ch2025_mLight.parquet", "mLight", ["m_light"], stats=("mean", "max", "sum"))
    add_scalar_modality(builder, item_dir, "ch2025_mScreenStatus.parquet", "mScreenStatus", ["m_screen_use"], stats=("mean", "sum"))
    add_usage(builder, item_dir, args.app_hash_buckets)
    add_device_list(builder, item_dir, "ch2025_mWifi.parquet", "mWifi", "m_wifi", "bssid", args.device_hash_buckets)
    add_hr(builder, item_dir)
    add_scalar_modality(builder, item_dir, "ch2025_wLight.parquet", "wLight", ["w_light"], stats=("mean", "max", "sum"))
    add_scalar_modality(
        builder,
        item_dir,
        "ch2025_wPedo.parquet",
        "wPedo",
        ["step", "step_frequency", "distance", "speed", "burned_calories"],
        stats=("mean", "max", "sum"),
    )

    x_raw, observed = builder.arrays()
    x_actual, norm_stats = auto_transform(x_raw, observed, builder.channel_names)
    signature = master_signature(Path(args.master_path), rows, args.signature_components)
    normal_twin, normal_twin_mask, twin_neighbors = build_normal_twin(x_actual, observed, rows, signature, args.normal_k)
    delta = np.where(observed > 0, x_actual - normal_twin, 0.0).astype(np.float32)
    abs_delta = np.abs(delta).astype(np.float32)
    gap = time_since_last_seen(observed)

    event_tokens, event_mask, event_feature_names = build_event_tokens(
        x_actual,
        x_raw,
        observed,
        delta,
        builder.channel_names,
        args.max_events,
        args.max_events_per_type,
    )
    group_features, prototype_group_names, prototype_feature_names = group_summary_features(
        x_actual,
        observed,
        delta,
        gap,
        builder.channel_names,
    )
    proto_mix, proto_summary = prototype_mixtures(group_features, prototype_group_names, args.prototype_k, args.seed)
    day_ctx, day_context_names = day_context(rows)
    slot_features, slot_feature_names = time_features(builder.slots)

    input_blocks = [
        ("actual", x_actual, observed),
        ("normal_twin", normal_twin, np.ones_like(observed, dtype=np.float32)),
        ("delta", delta, observed),
        ("abs_delta", abs_delta, observed),
        ("observed", observed, np.ones_like(observed, dtype=np.float32)),
        ("gap_since", gap, np.ones_like(observed, dtype=np.float32)),
    ]
    x_input = np.concatenate([block for _, block, _ in input_blocks], axis=2).astype(np.float32)
    input_mask = np.concatenate([block_mask for _, _, block_mask in input_blocks], axis=2).astype(np.float32)
    input_channel_names = [f"{prefix}__{name}" for prefix, _, _ in input_blocks for name in builder.channel_names]
    input_modalities = [f"{prefix}:{modality}" for prefix, _, _ in input_blocks for modality in builder.channel_modalities]

    np.savez_compressed(
        output_dir / "encoder_day_pyramid.npz",
        x=x_input.astype(np.float16 if args.float16 else np.float32),
        mask=input_mask.astype(np.float16 if args.float16 else np.float32),
        actual=x_actual.astype(np.float16 if args.float16 else np.float32),
        actual_mask=observed.astype(np.float16 if args.float16 else np.float32),
        raw=x_raw.astype(np.float32),
        normal_twin=normal_twin.astype(np.float16 if args.float16 else np.float32),
        normal_twin_mask=normal_twin_mask.astype(np.float16 if args.float16 else np.float32),
        delta=delta.astype(np.float16 if args.float16 else np.float32),
        abs_delta=abs_delta.astype(np.float16 if args.float16 else np.float32),
        gap_since=gap.astype(np.float16 if args.float16 else np.float32),
        event_tokens=event_tokens.astype(np.float16 if args.float16 else np.float32),
        event_mask=event_mask.astype(np.float16 if args.float16 else np.float32),
        prototype_mixture=proto_mix.astype(np.float16 if args.float16 else np.float32),
        prototype_features=group_features.astype(np.float16 if args.float16 else np.float32),
        day_context=day_ctx.astype(np.float16 if args.float16 else np.float32),
        slot_features=slot_features.astype(np.float16 if args.float16 else np.float32),
    )
    rows.to_csv(output_dir / "day_index.csv", index=False)
    twin_neighbors.to_csv(output_dir / "normal_twin_neighbors.csv", index=False)
    proto_summary.to_csv(output_dir / "prototype_summary.csv", index=False)
    pd.DataFrame({"event_feature": event_feature_names}).to_csv(output_dir / "event_feature_names.csv", index=False)
    event_type_counts = []
    for idx, event_type in enumerate(EVENT_TYPES):
        event_type_counts.append(
            {
                "event_type": event_type,
                "count": int(((event_tokens[:, :, idx] > 0.5) & (event_mask > 0)).sum()),
                "days_with_event": int(((event_tokens[:, :, idx] > 0.5) & (event_mask > 0)).any(axis=1).sum()),
            }
        )
    pd.DataFrame(event_type_counts).to_csv(output_dir / "event_type_counts.csv", index=False)
    coverage = pd.DataFrame(
        {
            "channel": builder.channel_names,
            "modality": builder.channel_modalities,
            "observed_rate": observed.mean(axis=(0, 1)),
            "nonzero_raw_rate": (x_raw != 0).mean(axis=(0, 1)),
        }
    )
    coverage.to_csv(output_dir / "channel_coverage.csv", index=False)

    metadata: dict[str, Any] = {
        "shape": {
            "days": int(x_input.shape[0]),
            "slots": int(x_input.shape[1]),
            "base_channels": int(x_actual.shape[2]),
            "input_channels": int(x_input.shape[2]),
            "max_events": int(args.max_events),
            "event_dim": int(event_tokens.shape[2]),
            "prototype_groups": int(proto_mix.shape[1]),
            "prototype_k": int(proto_mix.shape[2]),
        },
        "bin_minutes": int(args.bin_minutes),
        "base_channel_names": builder.channel_names,
        "base_channel_modalities": builder.channel_modalities,
        "input_channel_names": input_channel_names,
        "input_channel_modalities": input_modalities,
        "event_types": EVENT_TYPES,
        "event_feature_names": event_feature_names,
        "prototype_group_names": prototype_group_names,
        "prototype_feature_names": prototype_feature_names,
        "day_context_names": day_context_names,
        "slot_feature_names": slot_feature_names,
        "normalization": norm_stats,
        "args": vars(args),
        "notes": [
            "All 700 train plus submission subject-days are included without using labels.",
            "Normal-day twins are label-free counterfactual baselines built from same-subject neighbor days.",
            "Delta channels expose actual-minus-normal deviation directly to an Encoder.",
            "Observed masks and time-since-last-seen channels preserve missingness as behavior.",
            "Event tokens summarize sparse high-signal episodes that can be missed by dense pooling.",
            "Prototype mixtures decompose each day into modality-level behavioral styles.",
        ],
    }
    (output_dir / "tensor_metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(output_dir, x_input, builder.channel_names, event_mask, prototype_group_names, metadata)
    print(f"wrote {output_dir / 'encoder_day_pyramid.npz'}")
    print(f"x={x_input.shape} base={x_actual.shape} events={event_tokens.shape} prototypes={proto_mix.shape}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a 5-minute Normal-Day Twin Event Pyramid tensor for encoder-decoder experiments.")
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--master-path", default="artifacts/10_master_daily.parquet")
    parser.add_argument("--output-dir", default="outputs/encoder_day_pyramid")
    parser.add_argument("--bin-minutes", type=int, default=5)
    parser.add_argument("--device-hash-buckets", type=int, default=8)
    parser.add_argument("--app-hash-buckets", type=int, default=8)
    parser.add_argument("--ambience-top-k", type=int, default=10)
    parser.add_argument("--signature-components", type=int, default=32)
    parser.add_argument("--normal-k", type=int, default=10)
    parser.add_argument("--max-events", type=int, default=48)
    parser.add_argument("--max-events-per-type", type=int, default=3)
    parser.add_argument("--prototype-k", type=int, default=4)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--float16", action=argparse.BooleanOptionalAction, default=True)
    return parser.parse_args()


if __name__ == "__main__":
    build_dataset(parse_args())
