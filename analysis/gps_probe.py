from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


DATA_DIR = Path("data")
OUT_DIR = Path("outputs/data_probe")


def as_list(value: Any) -> list[Any]:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, list):
        return value
    return []


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


def explode_points(gps: pd.DataFrame) -> pd.DataFrame:
    records = []
    for sid, ts, items in gps[["subject_id", "timestamp", "m_gps"]].itertuples(index=False):
        for point in as_list(items):
            if isinstance(point, dict):
                records.append(
                    (
                        sid,
                        ts,
                        point.get("latitude"),
                        point.get("longitude"),
                        point.get("altitude"),
                        point.get("speed"),
                    )
                )
    points = pd.DataFrame(records, columns=["subject_id", "timestamp", "lat", "lon", "alt", "speed"])
    for col in ["lat", "lon", "alt", "speed"]:
        points[col] = pd.to_numeric(points[col], errors="coerce")
    return points


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    gps = pd.read_parquet(DATA_DIR / "ch2025_data_items/ch2025_mGps.parquet")
    train = pd.read_csv(DATA_DIR / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    test = pd.read_csv(DATA_DIR / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    target_rows = pd.concat([train.assign(split="train"), test.assign(split="test")], ignore_index=True)
    target_rows["lifelog_date"] = target_rows["lifelog_date"].dt.date

    gps = gps.copy()
    gps["lifelog_date"] = gps["timestamp"].dt.date
    gps["point_count"] = gps["m_gps"].map(lambda x: len(as_list(x)))

    day_rows = (
        gps.groupby(["subject_id", "lifelog_date"])
        .agg(
            minute_rows=("timestamp", "size"),
            active_hours=("timestamp", lambda s: s.dt.hour.nunique()),
            points=("point_count", "sum"),
            first_ts=("timestamp", "min"),
            last_ts=("timestamp", "max"),
        )
        .reset_index()
    )
    coverage = target_rows[["subject_id", "lifelog_date", "split"]].merge(
        day_rows, on=["subject_id", "lifelog_date"], how="left"
    )
    coverage_summary = (
        coverage.groupby("split")
        .agg(
            days=("lifelog_date", "size"),
            available=("minute_rows", lambda s: int(s.notna().sum())),
            availability=("minute_rows", lambda s: float(s.notna().mean())),
            median_minute_rows=("minute_rows", "median"),
            median_points=("points", "median"),
            median_active_hours=("active_hours", "median"),
        )
        .reset_index()
    )
    subject_coverage = (
        coverage.groupby(["subject_id", "split"])
        .agg(
            days=("lifelog_date", "size"),
            available=("minute_rows", lambda s: int(s.notna().sum())),
            median_minute_rows=("minute_rows", "median"),
            median_active_hours=("active_hours", "median"),
        )
        .reset_index()
    )

    points = explode_points(gps)
    points["lifelog_date"] = points["timestamp"].dt.date
    points["hour"] = points["timestamp"].dt.hour

    numeric_stats = points[["lat", "lon", "alt", "speed"]].describe(
        percentiles=[0.001, 0.01, 0.05, 0.5, 0.95, 0.99, 0.999]
    )
    speed_outliers = pd.DataFrame(
        [{"threshold": threshold, "rate": float((points["speed"] > threshold).mean())} for threshold in [0, 0.5, 1, 2, 5, 10, 20, 50, 100]]
    )
    subject_stats = (
        points.groupby("subject_id")
        .agg(
            points=("lat", "size"),
            lat_min=("lat", "min"),
            lat_max=("lat", "max"),
            lon_min=("lon", "min"),
            lon_max=("lon", "max"),
            lat_std=("lat", "std"),
            lon_std=("lon", "std"),
            speed_median=("speed", "median"),
            speed_p95=("speed", lambda s: s.quantile(0.95)),
            speed_p99=("speed", lambda s: s.quantile(0.99)),
        )
        .reset_index()
    )
    day_features = (
        points.groupby(["subject_id", "lifelog_date"])
        .agg(
            raw_points=("speed", "size"),
            speed_mean=("speed", "mean"),
            speed_p95=("speed", lambda s: s.quantile(0.95)),
            speed_max=("speed", "max"),
            stationary_rate=("speed", lambda s: float((s <= 0.5).mean())),
            moving_rate=("speed", lambda s: float((s > 1.5).mean())),
            lat_std=("lat", "std"),
            lon_std=("lon", "std"),
            alt_std=("alt", "std"),
            active_hours=("hour", "nunique"),
        )
        .reset_index()
    )

    gap_rows = []
    for sid, group in gps.sort_values("timestamp").groupby("subject_id"):
        gaps = group["timestamp"].diff().dt.total_seconds().dropna() / 60
        gap_rows.append(
            {
                "subject_id": sid,
                "minute_rows": len(group),
                "median_gap_min": float(gaps.median()),
                "p95_gap_min": float(gaps.quantile(0.95)),
                "gaps_over_10m_rate": float((gaps > 10).mean()),
            }
        )
    gap_stats = pd.DataFrame(gap_rows)

    day_features.to_parquet(OUT_DIR / "gps_day_features.parquet", index=False)
    coverage_summary.to_csv(OUT_DIR / "gps_coverage_summary.csv", index=False)
    subject_coverage.to_csv(OUT_DIR / "gps_subject_coverage.csv", index=False)
    subject_stats.to_csv(OUT_DIR / "gps_subject_stats.csv", index=False)
    speed_outliers.to_csv(OUT_DIR / "gps_speed_outliers.csv", index=False)
    gap_stats.to_csv(OUT_DIR / "gps_timestamp_gaps.csv", index=False)

    lines = [
        "# GPS Probe",
        "",
        "## Verdict",
        "GPS is usable, but should be treated as anonymized relative mobility data, not real map coordinates.",
        "",
        "## Table Structure",
        f"- rows: {len(gps)} minute-level rows",
        f"- raw points inside list column: {int(gps['point_count'].sum())}",
        f"- subjects: {gps['subject_id'].nunique()}",
        f"- time range: {gps['timestamp'].min()} to {gps['timestamp'].max()}",
        f"- point count per minute row median: {gps['point_count'].median():.0f}",
        "",
        "## Coverage On Target Days",
        markdown_table(coverage_summary),
        "",
        "## Coverage By Subject",
        markdown_table(subject_coverage),
        "",
        "## Point Numeric Stats",
        markdown_table(numeric_stats.reset_index().rename(columns={'index': 'stat'})),
        "",
        "## Speed Outlier Rates",
        markdown_table(speed_outliers),
        "",
        "## Subject Coordinate And Speed Ranges",
        markdown_table(subject_stats),
        "",
        "## Day Feature Stats",
        markdown_table(day_features.drop(columns=['subject_id', 'lifelog_date']).describe(percentiles=[0.05, 0.5, 0.95]).reset_index().rename(columns={'index': 'stat'})),
        "",
        "## Timestamp Continuity",
        markdown_table(gap_stats),
        "",
        "## Recommended Use",
        "- Use daily mobility features: active hours, point count, stationary/moving rate, speed quantiles, coordinate spread, altitude variation.",
        "- Use within-subject deviations: today's mobility compared to that subject's usual mobility.",
        "- Use robust clipping for speed/altitude outliers before feeding neural models.",
        "- Do not use absolute geographic meaning; coordinates look transformed/anonymized and should not be mapped to real places.",
    ]
    (OUT_DIR / "gps_probe_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_DIR / 'gps_probe_report.md'}")


if __name__ == "__main__":
    main()
