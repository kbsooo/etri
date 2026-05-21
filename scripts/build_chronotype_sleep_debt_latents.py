from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


KEY_COLUMNS = ["subject_id", "lifelog_date"]
ROW_KEYS = ["subject_id", "sleep_date", "lifelog_date"]
ROLL_WINDOWS = [3, 7, 14, 28]
GRID_SIGNALS = [
    "step_sum",
    "cal_sum",
    "body_activity",
    "phone_activity",
    "mobility_activity",
    "screen_mean",
    "usage_total",
    "ev_phone_active",
    "ev_moving",
    "ev_no_wear",
    "sensor_coverage_n",
]


def safe_float(value: float) -> float:
    if value != value or np.isinf(value):
        return 0.0
    return float(value)


def circ_diff_hours(value: pd.Series | np.ndarray | float, center: pd.Series | np.ndarray | float) -> pd.Series | np.ndarray | float:
    return ((value - center + 12.0) % 24.0) - 12.0


def circular_std_hours(values: pd.Series) -> float:
    arr = values.dropna().to_numpy(float)
    if len(arr) < 2:
        return 0.0
    angles = 2.0 * np.pi * arr / 24.0
    r = np.sqrt(np.mean(np.sin(angles)) ** 2 + np.mean(np.cos(angles)) ** 2)
    r = np.clip(r, 1e-8, 1.0)
    return safe_float(np.sqrt(-2.0 * np.log(r)) * 24.0 / (2.0 * np.pi))


def normalize_rows(path: str) -> pd.DataFrame:
    frame = pd.read_csv(path).copy()
    frame["subject_id"] = frame["subject_id"].astype(str)
    frame["sleep_date"] = pd.to_datetime(frame["sleep_date"]).dt.strftime("%Y-%m-%d")
    frame["lifelog_date"] = pd.to_datetime(frame["lifelog_date"]).dt.strftime("%Y-%m-%d")
    return frame[ROW_KEYS]


def load_rows(train_path: str, sample_path: str) -> pd.DataFrame:
    return pd.concat([normalize_rows(train_path), normalize_rows(sample_path)], ignore_index=True).drop_duplicates()


def load_sleep(path: str) -> pd.DataFrame:
    sleep = pd.read_parquet(path).copy()
    sleep["subject_id"] = sleep["subject_id"].astype(str)
    sleep["sleep_date"] = pd.to_datetime(sleep["sleep_date"]).dt.strftime("%Y-%m-%d")
    sleep["sleep_onset"] = pd.to_datetime(sleep["sleep_onset"])
    sleep["wake_time"] = pd.to_datetime(sleep["wake_time"])
    return sleep


def load_grid(path: str) -> pd.DataFrame:
    grid = pd.read_parquet(path).copy()
    grid["subject_id"] = grid["subject_id"].astype(str)
    grid["date"] = pd.to_datetime(grid["date"])
    grid["timestamp"] = grid["date"] + pd.to_timedelta(grid["tok"].astype(int) * 30, unit="m")
    return grid


def summarize_grid_window(subject_grid: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp, prefix: str) -> dict[str, float]:
    part = subject_grid[(subject_grid["timestamp"] >= start) & (subject_grid["timestamp"] < end)]
    out: dict[str, float] = {f"z_cs_{prefix}_tok_n": float(len(part))}
    for col in GRID_SIGNALS:
        if col not in part:
            continue
        arr = np.nan_to_num(part[col].to_numpy(float), nan=0.0, posinf=0.0, neginf=0.0)
        out[f"z_cs_{prefix}_{col}_sum"] = safe_float(arr.sum())
        out[f"z_cs_{prefix}_{col}_mean"] = safe_float(arr.mean() if len(arr) else 0.0)
        out[f"z_cs_{prefix}_{col}_max"] = safe_float(arr.max() if len(arr) else 0.0)
    if {"ev_phone_active", "ev_moving"}.issubset(part.columns):
        phone = np.nan_to_num(part["ev_phone_active"].to_numpy(float), nan=0.0) > 0.5
        moving = np.nan_to_num(part["ev_moving"].to_numpy(float), nan=0.0) > 0.5
        out[f"z_cs_{prefix}_phone_still_ratio"] = safe_float(float((phone & ~moving).mean()) if len(part) else 0.0)
    return out


def add_subject_baselines(features: pd.DataFrame) -> pd.DataFrame:
    features = features.copy()
    subject_group = features.groupby("subject_id", group_keys=False)
    for col in ["onset_hour", "wake_hour", "midpoint_hour", "tst_min", "sleep_eff", "sol_proxy_min", "n_awakenings"]:
        center = subject_group[col].transform("median")
        if col.endswith("_hour"):
            diff = circ_diff_hours(features[col], center)
            features[f"z_cs_{col}_subject_shift"] = diff
            features[f"z_cs_{col}_subject_abs_shift"] = diff.abs()
        else:
            mad = subject_group[col].transform(lambda s: np.nanmedian(np.abs(s - np.nanmedian(s))) + 1e-6)
            features[f"z_cs_{col}_subject_dev"] = features[col] - center
            features[f"z_cs_{col}_subject_z"] = (features[col] - center) / mad

    weekday_median = features.groupby(["subject_id", "weekday"])["midpoint_hour"].transform("median")
    weekend_median = features.groupby(["subject_id", "is_weekend"])["midpoint_hour"].transform("median")
    global_mid = subject_group["midpoint_hour"].transform("median")
    features["z_cs_midpoint_weekday_shift"] = circ_diff_hours(features["midpoint_hour"], weekday_median)
    features["z_cs_midpoint_weekend_class_shift"] = circ_diff_hours(features["midpoint_hour"], weekend_median)
    features["z_cs_midpoint_social_jetlag_abs"] = circ_diff_hours(weekend_median, global_mid).abs()
    features["z_cs_is_weekend"] = features["is_weekend"].astype(float)
    return features


def add_rolling_features(features: pd.DataFrame) -> pd.DataFrame:
    features = features.sort_values(["subject_id", "lifelog_dt"]).copy()
    med_tst = features.groupby("subject_id")["tst_min"].transform("median")
    med_eff = features.groupby("subject_id")["sleep_eff"].transform("median")
    med_sol = features.groupby("subject_id")["sol_proxy_min"].transform("median")
    med_awaken = features.groupby("subject_id")["n_awakenings"].transform("median")
    features["z_cs_sleep_deficit_today"] = np.maximum(0.0, med_tst - features["tst_min"])
    features["z_cs_sleep_surplus_today"] = np.maximum(0.0, features["tst_min"] - med_tst)
    features["z_cs_eff_deficit_today"] = np.maximum(0.0, med_eff - features["sleep_eff"])
    features["z_cs_sol_excess_today"] = np.maximum(0.0, features["sol_proxy_min"] - med_sol)
    features["z_cs_awakening_excess_today"] = np.maximum(0.0, features["n_awakenings"] - med_awaken)

    for window in ROLL_WINDOWS:
        for col in [
            "z_cs_sleep_deficit_today",
            "z_cs_eff_deficit_today",
            "z_cs_sol_excess_today",
            "z_cs_awakening_excess_today",
        ]:
            shifted = features.groupby("subject_id")[col].shift(1)
            roll_sum = shifted.groupby(features["subject_id"]).rolling(window, min_periods=2).sum().reset_index(level=0, drop=True)
            roll_mean = shifted.groupby(features["subject_id"]).rolling(window, min_periods=2).mean().reset_index(level=0, drop=True)
            features[f"{col}_past{window}_sum"] = roll_sum.fillna(0.0)
            features[f"{col}_past{window}_mean"] = roll_mean.fillna(0.0)

        for hour_col in ["onset_hour", "wake_hour", "midpoint_hour"]:
            shifted = features.groupby("subject_id")[hour_col].shift(1)
            circ_std = (
                shifted.groupby(features["subject_id"])
                .rolling(window, min_periods=3)
                .apply(circular_std_hours, raw=False)
                .reset_index(level=0, drop=True)
            )
            features[f"z_cs_{hour_col}_past{window}_circ_std"] = circ_std.fillna(0.0)

        onset_shift = features.groupby("subject_id")["z_cs_onset_hour_subject_shift"].shift(1)
        late_flag = (onset_shift > 1.0).astype(float)
        early_wake = (features.groupby("subject_id")["z_cs_wake_hour_subject_shift"].shift(1) < -1.0).astype(float)
        features[f"z_cs_late_bed_streak_past{window}"] = (
            late_flag.groupby(features["subject_id"]).rolling(window, min_periods=1).sum().reset_index(level=0, drop=True).fillna(0.0)
        )
        features[f"z_cs_early_wake_streak_past{window}"] = (
            early_wake.groupby(features["subject_id"]).rolling(window, min_periods=1).sum().reset_index(level=0, drop=True).fillna(0.0)
        )
    return features


def build_features(rows: pd.DataFrame, sleep: pd.DataFrame, grid: pd.DataFrame) -> pd.DataFrame:
    merged = rows.merge(sleep, on=["subject_id", "sleep_date"], how="left", validate="many_to_one")
    merged["lifelog_dt"] = pd.to_datetime(merged["lifelog_date"])
    merged["weekday"] = merged["lifelog_dt"].dt.weekday
    merged["is_weekend"] = merged["weekday"].isin([5, 6]).astype(int)
    merged["onset_hour"] = merged["sleep_onset"].dt.hour + merged["sleep_onset"].dt.minute / 60.0
    merged["wake_hour"] = merged["wake_time"].dt.hour + merged["wake_time"].dt.minute / 60.0
    midpoint = merged["sleep_onset"] + (merged["wake_time"] - merged["sleep_onset"]) / 2
    merged["midpoint_hour"] = midpoint.dt.hour + midpoint.dt.minute / 60.0
    merged["sleep_window_min"] = (merged["wake_time"] - merged["sleep_onset"]).dt.total_seconds() / 60.0
    merged["sleep_to_sleep_wake_interval_min"] = (
        merged.sort_values(["subject_id", "wake_time"]).groupby("subject_id")["wake_time"].diff().dt.total_seconds() / 60.0
    )
    merged["sleep_to_sleep_onset_interval_min"] = (
        merged.sort_values(["subject_id", "sleep_onset"]).groupby("subject_id")["sleep_onset"].diff().dt.total_seconds() / 60.0
    )
    for col in ["tst_min", "sleep_eff", "sol_proxy_min", "n_awakenings", "longest_block_min"]:
        merged[col] = merged[col].fillna(0.0).astype(float)
    for col in ["onset_hour", "wake_hour", "midpoint_hour", "sleep_window_min", "sleep_to_sleep_wake_interval_min", "sleep_to_sleep_onset_interval_min"]:
        merged[col] = merged[col].fillna(0.0).astype(float)

    grid_by_subject = {subject: group.sort_values("timestamp") for subject, group in grid.groupby("subject_id")}
    records = []
    for _, row in merged.iterrows():
        out = {
            "subject_id": str(row["subject_id"]),
            "lifelog_date": row["lifelog_date"],
            "lifelog_dt": row["lifelog_dt"],
            "weekday": int(row["weekday"]),
            "is_weekend": int(row["is_weekend"]),
            "onset_hour": float(row["onset_hour"]),
            "wake_hour": float(row["wake_hour"]),
            "midpoint_hour": float(row["midpoint_hour"]),
            "tst_min": float(row["tst_min"]),
            "sleep_eff": float(row["sleep_eff"]),
            "sol_proxy_min": float(row["sol_proxy_min"]),
            "n_awakenings": float(row["n_awakenings"]),
            "longest_block_min": float(row["longest_block_min"]),
            "z_cs_sleep_window_min": float(row["sleep_window_min"]),
            "z_cs_sleep_to_sleep_wake_interval_min": float(row["sleep_to_sleep_wake_interval_min"]),
            "z_cs_sleep_to_sleep_onset_interval_min": float(row["sleep_to_sleep_onset_interval_min"]),
        }
        subject_grid = grid_by_subject.get(str(row["subject_id"]))
        if subject_grid is not None and pd.notna(row["wake_time"]):
            wake = row["wake_time"]
            onset = row["sleep_onset"]
            out.update(summarize_grid_window(subject_grid, wake, wake + pd.Timedelta(hours=3), "postwake3h"))
            out.update(summarize_grid_window(subject_grid, wake, wake + pd.Timedelta(hours=6), "postwake6h"))
            out.update(summarize_grid_window(subject_grid, onset - pd.Timedelta(hours=6), onset, "prebed6h"))
        records.append(out)

    features = pd.DataFrame(records).sort_values(KEY_COLUMNS).reset_index(drop=True)
    features = add_subject_baselines(features)
    features = add_rolling_features(features)

    numeric_cols = [c for c in features.columns if c not in KEY_COLUMNS + ["lifelog_dt"] and pd.api.types.is_numeric_dtype(features[c])]
    keep = KEY_COLUMNS + [c for c in numeric_cols if c.startswith("z_cs_")]
    result = features[keep].copy()
    result = result.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    return result.sort_values(KEY_COLUMNS).reset_index(drop=True)


def dataframe_to_markdown(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "_No rows._"
    cols = frame.columns.tolist()
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in frame.iterrows():
        vals = []
        for col in cols:
            value = row[col]
            vals.append(f"{value:.6f}" if isinstance(value, float) else str(value))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def run(args: argparse.Namespace) -> None:
    rows = load_rows(args.train_path, args.sample_path)
    sleep = load_sleep(args.sleep_summary)
    grid = load_grid(args.grid_path)
    features = build_features(rows, sleep, grid)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    features.to_parquet(output, index=False)
    feature_cols = [c for c in features.columns if c not in KEY_COLUMNS]
    coverage = pd.DataFrame(
        {
            "feature": feature_cols,
            "non_null_rate": [float(features[c].notna().mean()) for c in feature_cols],
            "mean": [float(features[c].mean(skipna=True)) for c in feature_cols],
            "std": [float(features[c].std(skipna=True)) for c in feature_cols],
        }
    )
    report = {
        "output": str(output),
        "rows": int(len(features)),
        "feature_count": int(len(feature_cols)),
        "hypotheses": [
            "S1/S3 may depend on sleep-to-sleep alignment rather than calendar-day aggregates.",
            "Social jetlag and chronotype drift may explain sleep latency/quality failures.",
            "Rolling sleep debt and irregularity debt may carry more label signal than single-day sleep metrics.",
            "Post-wake energy recovery may reveal whether a sleep episode restored daytime activity.",
        ],
    }
    output.with_suffix(".report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    md = [
        "# Chronotype Sleep Debt Latents",
        "",
        "## Purpose",
        "",
        "Build sleep-to-sleep, social-jetlag, chronotype drift, sleep debt ledger, and post-wake recovery features for S1/S3 discovery.",
        "",
        f"- Output: `{output}`",
        f"- Rows: `{len(features)}`",
        f"- Feature count: `{len(feature_cols)}`",
        "",
        "## Feature Coverage",
        "",
        dataframe_to_markdown(coverage.head(40)),
    ]
    output.with_suffix(".report.md").write_text("\n".join(md), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build chronotype, social-jetlag, sleep-debt, and post-wake recovery features.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--sleep-summary", default="artifacts/07_sleep_summary.parquet")
    parser.add_argument("--grid-path", default="artifacts/multires_30min_event_hybrid_grid.parquet")
    parser.add_argument("--output", default="artifacts/domain_chronotype_sleep_debt_v1.parquet")
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
