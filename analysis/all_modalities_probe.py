from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


DATA_DIR = Path("data")
ITEM_DIR = DATA_DIR / "ch2025_data_items"
OUT_DIR = Path("outputs/data_probe")


MODALITIES: dict[str, dict[str, Any]] = {
    "mACStatus": {"file": "ch2025_mACStatus.parquet", "kind": "scalar", "value_cols": ["m_charging"]},
    "mActivity": {"file": "ch2025_mActivity.parquet", "kind": "categorical", "value_cols": ["m_activity"]},
    "mAmbience": {"file": "ch2025_mAmbience.parquet", "kind": "ambience", "value_cols": ["m_ambience"]},
    "mBle": {"file": "ch2025_mBle.parquet", "kind": "device_list", "value_cols": ["m_ble"], "id_key": "address"},
    "mGps": {"file": "ch2025_mGps.parquet", "kind": "gps", "value_cols": ["m_gps"]},
    "mLight": {"file": "ch2025_mLight.parquet", "kind": "scalar", "value_cols": ["m_light"]},
    "mScreenStatus": {"file": "ch2025_mScreenStatus.parquet", "kind": "scalar", "value_cols": ["m_screen_use"]},
    "mUsageStats": {"file": "ch2025_mUsageStats.parquet", "kind": "usage", "value_cols": ["m_usage_stats"]},
    "mWifi": {"file": "ch2025_mWifi.parquet", "kind": "device_list", "value_cols": ["m_wifi"], "id_key": "bssid"},
    "wHr": {"file": "ch2025_wHr.parquet", "kind": "hr_list", "value_cols": ["heart_rate"]},
    "wLight": {"file": "ch2025_wLight.parquet", "kind": "scalar", "value_cols": ["w_light"]},
    "wPedo": {
        "file": "ch2025_wPedo.parquet",
        "kind": "multiscalar",
        "value_cols": ["step", "step_frequency", "running_step", "walking_step", "distance", "speed", "burned_calories"],
    },
}

RECOMMENDATIONS: dict[str, list[str]] = {
    "mACStatus": [
        "Use as a phone routine and charging-at-night signal.",
        "Aggregate charging rate by hour/daypart and longest charging run.",
        "Do not over-interpret as sleep by itself; combine with screen inactivity and watch signals.",
    ],
    "mActivity": [
        "Use class proportions, entropy, daypart proportions, and transition counts.",
        "Keep the raw integer classes as categorical embeddings for sequence encoders.",
        "Treat high unknown/still rates as behavior signals, not only noise.",
    ],
    "mAmbience": [
        "Use top-label rates, label entropy, top probability, and broad groups such as Speech/Music/Vehicle/Outside.",
        "This is useful for context but labels are noisy; prefer daily/hourly rates over single observations.",
    ],
    "mBle": [
        "Use unique device count, scan count, RSSI stats, class diversity, and within-subject stable-device hashes.",
        "Good for social/proximity/place context; sparse compared with minute sensors.",
        "Avoid raw address one-hot explosion; use top-K per subject or feature hashing.",
    ],
    "mGps": [
        "Use as anonymized relative mobility, not real map coordinates.",
        "Aggregate speed, stationary/moving rate, coordinate spread, active hours, and within-subject mobility deviation.",
        "Clip speed/altitude outliers before neural inputs.",
    ],
    "mLight": [
        "Use phone ambient light exposure by daypart, especially evening/night and morning.",
        "Combine with screen and charging to infer phone context; phone light alone may reflect device placement.",
    ],
    "mScreenStatus": [
        "Highly useful bedtime behavior signal.",
        "Use screen-use rate by hour, late-night use, last active time, total active minutes, and long inactivity runs.",
    ],
    "mUsageStats": [
        "Use total app time, unique apps, app entropy, late-night app use, and coarse app categories/top-K apps.",
        "App names are high-cardinality and personal; use top-K/hash/category rather than raw one-hot everywhere.",
    ],
    "mWifi": [
        "Strong place/routine proxy; often more useful than anonymized GPS for location stability.",
        "Use unique AP count, scan density, RSSI stats, repeated AP overlap, place entropy, and within-subject location clusters.",
        "Avoid raw BSSID leakage/overfit; use subject-local clustering or hashing.",
    ],
    "wHr": [
        "Use heart-rate level/variability, nighttime resting HR, high-HR bursts, and coverage as watch-wearing signal.",
        "List values per minute should be summarized per hour before feeding sequence models.",
    ],
    "wLight": [
        "Use wrist light exposure, night darkness, morning exposure, and coverage/wearing proxies.",
        "Interpret together with watch HR and pedometer.",
    ],
    "wPedo": [
        "Use steps/distance/speed/calories by hour/daypart, active bouts, sedentary duration, and personal deviations.",
        "Zeros are meaningful; preserve zero rates rather than imputing them away.",
    ],
}


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


def markdown_table(frame: pd.DataFrame, max_rows: int | None = None) -> str:
    if frame.empty:
        return "_empty_"
    view = frame.head(max_rows).copy() if max_rows is not None else frame.copy()
    for col in view.columns:
        if pd.api.types.is_float_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else f"{x:.4g}")
        else:
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else str(x))
    cols = [str(c) for c in view.columns]
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for row in view.itertuples(index=False):
        lines.append("| " + " | ".join(str(x).replace("\n", " ") for x in row) + " |")
    return "\n".join(lines)


def target_rows() -> pd.DataFrame:
    train = pd.read_csv(DATA_DIR / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    test = pd.read_csv(DATA_DIR / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    rows = pd.concat([train.assign(split="train"), test.assign(split="test")], ignore_index=True)
    rows["lifelog_date"] = rows["lifelog_date"].dt.date
    return rows[["subject_id", "lifelog_date", "split"]]


def day_coverage(df: pd.DataFrame, rows: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    daily = (
        df.assign(lifelog_date=df["timestamp"].dt.date)
        .groupby(["subject_id", "lifelog_date"])
        .agg(row_count=("timestamp", "size"), active_hours=("timestamp", lambda s: s.dt.hour.nunique()))
        .reset_index()
    )
    merged = rows.merge(daily, on=["subject_id", "lifelog_date"], how="left")
    by_split = (
        merged.groupby("split")
        .agg(
            target_days=("lifelog_date", "size"),
            available_days=("row_count", lambda s: int(s.notna().sum())),
            availability=("row_count", lambda s: float(s.notna().mean())),
            median_rows=("row_count", "median"),
            median_active_hours=("active_hours", "median"),
        )
        .reset_index()
    )
    by_subject = (
        merged.groupby(["subject_id", "split"])
        .agg(
            days=("lifelog_date", "size"),
            available=("row_count", lambda s: int(s.notna().sum())),
            availability=("row_count", lambda s: float(s.notna().mean())),
            median_rows=("row_count", "median"),
            median_active_hours=("active_hours", "median"),
        )
        .reset_index()
    )
    return by_split, by_subject


def inventory_row(name: str, cfg: dict[str, Any], df: pd.DataFrame) -> dict[str, Any]:
    gaps = []
    for _, group in df.sort_values("timestamp").groupby("subject_id"):
        gap = group["timestamp"].diff().dt.total_seconds().dropna() / 60
        if len(gap):
            gaps.append(gap)
    all_gaps = pd.concat(gaps, ignore_index=True) if gaps else pd.Series(dtype=float)
    return {
        "modality": name,
        "file": cfg["file"],
        "kind": cfg["kind"],
        "rows": len(df),
        "subjects": int(df["subject_id"].nunique()),
        "time_min": str(df["timestamp"].min()),
        "time_max": str(df["timestamp"].max()),
        "columns": ", ".join(df.columns),
        "median_gap_min": float(all_gaps.median()) if len(all_gaps) else np.nan,
        "p95_gap_min": float(all_gaps.quantile(0.95)) if len(all_gaps) else np.nan,
        "gaps_over_10m_rate": float((all_gaps > 10).mean()) if len(all_gaps) else np.nan,
    }


def numeric_summary(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    rows = []
    for col in cols:
        s = pd.to_numeric(df[col], errors="coerce")
        rows.append(
            {
                "feature": col,
                "count": int(s.notna().sum()),
                "missing_rate": float(s.isna().mean()),
                "mean": float(s.mean()),
                "std": float(s.std()),
                "min": float(s.min()),
                "p01": float(s.quantile(0.01)),
                "p05": float(s.quantile(0.05)),
                "p50": float(s.quantile(0.50)),
                "p95": float(s.quantile(0.95)),
                "p99": float(s.quantile(0.99)),
                "max": float(s.max()),
                "zero_rate": float((s == 0).mean()),
            }
        )
    return pd.DataFrame(rows)


def scalar_details(name: str, df: pd.DataFrame, cols: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    stats = numeric_summary(df, cols)
    rows = []
    for col in cols:
        if df[col].nunique(dropna=True) <= 20:
            vc = df[col].value_counts(dropna=False).head(30)
            for value, count in vc.items():
                rows.append({"modality": name, "feature": col, "value": str(value), "count": int(count), "rate": float(count / len(df))})
    return stats, pd.DataFrame(rows)


def ambience_details(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    top_labels: Counter[str] = Counter()
    any_labels: Counter[str] = Counter()
    list_lengths = []
    top_probs = []
    prob_sums = []
    for items in df["m_ambience"]:
        labels = []
        probs = []
        for item in as_list(items):
            pair = as_pair(item)
            if pair is not None:
                label = str(pair[0])
                prob = float(pair[1])
                labels.append(label)
                probs.append(prob)
                any_labels[label] += 1
        list_lengths.append(len(labels))
        if labels:
            top_labels[labels[0]] += 1
            top_probs.append(probs[0])
            prob_sums.append(sum(probs))
    stats = pd.DataFrame(
        [
            {"feature": "labels_per_row", **pd.Series(list_lengths).describe(percentiles=[0.01, 0.05, 0.5, 0.95, 0.99]).to_dict()},
            {"feature": "top_probability", **pd.Series(top_probs).describe(percentiles=[0.01, 0.05, 0.5, 0.95, 0.99]).to_dict()},
            {"feature": "probability_sum", **pd.Series(prob_sums).describe(percentiles=[0.01, 0.05, 0.5, 0.95, 0.99]).to_dict()},
        ]
    )
    top = pd.DataFrame(
        [{"label": label, "top_count": count, "top_rate": count / len(df), "any_count": any_labels[label]} for label, count in top_labels.most_common(30)]
    )
    return stats, top


def device_details(df: pd.DataFrame, list_col: str, id_key: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    row_stats = []
    rssi_values = []
    device_counter: Counter[str] = Counter()
    class_counter: Counter[str] = Counter()
    for items in df[list_col]:
        ids = []
        classes = []
        rssis = []
        for item in as_list(items):
            if isinstance(item, dict):
                if id_key in item:
                    ids.append(str(item[id_key]))
                if "device_class" in item:
                    classes.append(str(item["device_class"]))
                if "rssi" in item and item["rssi"] is not None:
                    rssis.append(float(item["rssi"]))
        device_counter.update(ids)
        class_counter.update(classes)
        rssi_values.extend(rssis)
        row_stats.append(
            {
                "scan_count": len(ids),
                "unique_count": len(set(ids)),
                "class_unique_count": len(set(classes)),
                "rssi_mean": float(np.mean(rssis)) if rssis else np.nan,
                "rssi_max": float(np.max(rssis)) if rssis else np.nan,
                "rssi_min": float(np.min(rssis)) if rssis else np.nan,
            }
        )
    stats = pd.DataFrame(row_stats).describe(percentiles=[0.01, 0.05, 0.5, 0.95, 0.99]).reset_index().rename(columns={"index": "stat"})
    top_devices = pd.DataFrame([{"id": key, "count": value} for key, value in device_counter.most_common(20)])
    top_classes = pd.DataFrame([{"class": key, "count": value} for key, value in class_counter.most_common(20)])
    rssi = pd.Series(rssi_values, dtype=float).describe(percentiles=[0.01, 0.05, 0.5, 0.95, 0.99]).to_frame("rssi").reset_index().rename(columns={"index": "stat"})
    stats = pd.concat([stats, pd.DataFrame([{"stat": "total_unique_ids", "scan_count": len(device_counter)}])], ignore_index=True)
    return stats, top_devices, pd.concat([top_classes.assign(type="class"), rssi.assign(type="rssi")], ignore_index=True)


def usage_details(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    row_stats = []
    app_counter: Counter[str] = Counter()
    total_times = []
    for items in df["m_usage_stats"]:
        apps = []
        times = []
        for item in as_list(items):
            if isinstance(item, dict):
                app = str(item.get("app_name", "")).strip()
                if app:
                    apps.append(app)
                if item.get("total_time") is not None:
                    times.append(float(item["total_time"]))
        app_counter.update(apps)
        total_times.extend(times)
        row_stats.append(
            {
                "apps_per_row": len(apps),
                "unique_apps_per_row": len(set(apps)),
                "total_time_sum": float(np.sum(times)) if times else 0.0,
                "total_time_max": float(np.max(times)) if times else np.nan,
            }
        )
    stats = pd.DataFrame(row_stats).describe(percentiles=[0.01, 0.05, 0.5, 0.95, 0.99]).reset_index().rename(columns={"index": "stat"})
    app_time_stats = pd.Series(total_times, dtype=float).describe(percentiles=[0.01, 0.05, 0.5, 0.95, 0.99]).to_dict()
    stats = pd.concat([stats, pd.DataFrame([{"stat": f"app_total_time_{k}", "total_time_sum": v} for k, v in app_time_stats.items()])], ignore_index=True)
    top_apps = pd.DataFrame([{"app": key, "count": value} for key, value in app_counter.most_common(40)])
    return stats, top_apps


def gps_details(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    values = defaultdict(list)
    point_counts = []
    for items in df["m_gps"]:
        pts = as_list(items)
        point_counts.append(len(pts))
        for item in pts:
            if isinstance(item, dict):
                for key in ["latitude", "longitude", "altitude", "speed"]:
                    if item.get(key) is not None:
                        values[key].append(float(item[key]))
    rows = [{"feature": "points_per_row", **pd.Series(point_counts).describe(percentiles=[0.01, 0.05, 0.5, 0.95, 0.99]).to_dict()}]
    for key, vals in values.items():
        rows.append({"feature": key, **pd.Series(vals, dtype=float).describe(percentiles=[0.01, 0.05, 0.5, 0.95, 0.99]).to_dict()})
    speed = pd.Series(values["speed"], dtype=float)
    outliers = pd.DataFrame([{"threshold": th, "rate": float((speed > th).mean())} for th in [0.5, 1, 2, 5, 10, 20, 50, 100]])
    return pd.DataFrame(rows), outliers


def hr_details(df: pd.DataFrame) -> pd.DataFrame:
    row_stats = []
    values = []
    for items in df["heart_rate"]:
        vals = [float(x) for x in as_list(items) if x is not None]
        values.extend(vals)
        row_stats.append(
            {
                "hr_points_per_row": len(vals),
                "hr_mean": float(np.mean(vals)) if vals else np.nan,
                "hr_std": float(np.std(vals)) if vals else np.nan,
                "hr_min": float(np.min(vals)) if vals else np.nan,
                "hr_max": float(np.max(vals)) if vals else np.nan,
            }
        )
    stats = pd.DataFrame(row_stats).describe(percentiles=[0.01, 0.05, 0.5, 0.95, 0.99]).reset_index().rename(columns={"index": "stat"})
    point_stats = pd.Series(values, dtype=float).describe(percentiles=[0.01, 0.05, 0.5, 0.95, 0.99]).to_dict()
    stats = pd.concat([stats, pd.DataFrame([{"stat": f"raw_hr_{k}", "hr_mean": v} for k, v in point_stats.items()])], ignore_index=True)
    return stats


def detail_tables(name: str, cfg: dict[str, Any], df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    kind = cfg["kind"]
    if kind in {"scalar", "multiscalar"}:
        stats, counts = scalar_details(name, df, cfg["value_cols"])
        return {"numeric_stats": stats, "value_counts": counts}
    if kind == "categorical":
        counts = df[cfg["value_cols"][0]].value_counts(dropna=False).reset_index()
        counts.columns = ["value", "count"]
        counts["rate"] = counts["count"] / len(df)
        return {"category_counts": counts}
    if kind == "ambience":
        stats, top = ambience_details(df)
        return {"ambience_stats": stats, "top_ambience_labels": top}
    if kind == "device_list":
        stats, top_devices, aux = device_details(df, cfg["value_cols"][0], cfg["id_key"])
        return {"device_stats": stats, "top_device_ids": top_devices, "device_aux": aux}
    if kind == "usage":
        stats, top_apps = usage_details(df)
        return {"usage_stats": stats, "top_apps": top_apps}
    if kind == "gps":
        stats, outliers = gps_details(df)
        return {"gps_stats": stats, "gps_speed_outliers": outliers}
    if kind == "hr_list":
        return {"hr_stats": hr_details(df)}
    raise ValueError(f"unknown kind: {kind}")


def compact_detail_for_report(tables: dict[str, pd.DataFrame]) -> str:
    chunks = []
    for name, table in tables.items():
        chunks.append(f"**{name}**")
        chunks.append(markdown_table(table, max_rows=12))
    return "\n\n".join(chunks)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = target_rows()
    inventory = []
    coverage_split_tables = []
    coverage_subject_tables = []
    details_for_json: dict[str, dict[str, list[dict[str, Any]]]] = {}
    report_lines = [
        "# All Modalities Probe",
        "",
        "This report checks every raw sensor table for structure, coverage, value distribution, usability, and encoder input strategy.",
        "",
    ]

    for name, cfg in MODALITIES.items():
        df = pd.read_parquet(ITEM_DIR / cfg["file"])
        inv = inventory_row(name, cfg, df)
        inventory.append(inv)
        by_split, by_subject = day_coverage(df, rows)
        by_split.insert(0, "modality", name)
        by_subject.insert(0, "modality", name)
        coverage_split_tables.append(by_split)
        coverage_subject_tables.append(by_subject)
        details = detail_tables(name, cfg, df)
        details_for_json[name] = {key: value.to_dict(orient="records") for key, value in details.items()}

        report_lines.extend(
            [
                f"## {name}",
                "",
                f"- file: `{cfg['file']}`",
                f"- kind: `{cfg['kind']}`",
                f"- rows: {len(df):,}",
                f"- columns: {', '.join(df.columns)}",
                f"- time: {df['timestamp'].min()} to {df['timestamp'].max()}",
                "",
                "**Target-day coverage**",
                markdown_table(by_split),
                "",
                compact_detail_for_report(details),
                "",
                "**Recommended use**",
            ]
        )
        for line in RECOMMENDATIONS[name]:
            report_lines.append(f"- {line}")
        report_lines.append("")

    inventory_df = pd.DataFrame(inventory)
    coverage_split = pd.concat(coverage_split_tables, ignore_index=True)
    coverage_subject = pd.concat(coverage_subject_tables, ignore_index=True)

    inventory_df.to_csv(OUT_DIR / "all_modalities_inventory.csv", index=False)
    coverage_split.to_csv(OUT_DIR / "all_modalities_coverage_by_split.csv", index=False)
    coverage_subject.to_csv(OUT_DIR / "all_modalities_coverage_by_subject.csv", index=False)
    (OUT_DIR / "all_modalities_details.json").write_text(json.dumps(details_for_json, ensure_ascii=False, indent=2), encoding="utf-8")

    overview = [
        "# All Modalities Overview",
        "",
        "## Inventory",
        markdown_table(inventory_df),
        "",
        "## Coverage By Split",
        markdown_table(coverage_split),
        "",
        "## Practical Encoder Input Plan",
        "- Align every modality to `subject_id + lifelog_date + hour`.",
        "- For dense minute sensors, aggregate hourly mean/sum/std/rate and keep availability masks.",
        "- For list sensors, use count/unique/RSSI/probability summaries plus top-K or hashed tokens.",
        "- For sequence encoders, feed 24 hourly bins with modality masks; for tabular heads, flatten daypart/day summaries.",
        "- Compute within-subject deviations for every stable numeric channel.",
        "",
    ]
    overview.extend(report_lines[3:])
    (OUT_DIR / "all_modalities_probe_report.md").write_text("\n".join(overview) + "\n", encoding="utf-8")
    print(f"wrote {OUT_DIR / 'all_modalities_probe_report.md'}")


if __name__ == "__main__":
    main()
