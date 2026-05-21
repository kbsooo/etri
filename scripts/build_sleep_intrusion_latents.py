from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


TARGET_KEYS = ["subject_id", "sleep_date", "lifelog_date"]
OUTPUT_KEYS = ["subject_id", "lifelog_date"]
SIGNALS = [
    "ev_phone_active",
    "ev_moving",
    "ev_no_wear",
    "ev_low_coverage",
    "ev_charging_on",
    "screen_mean",
    "usage_total",
    "step_sum",
    "mlight_mean",
    "wlight_mean",
    "sensor_coverage_n",
]
WINDOWS = {
    "prebed2h": (-120, 0),
    "prebed6h": (-360, 0),
    "sleep": (0, None),
    "postwake2h": (None, 120),
}


def normalize_metrics(path: str) -> pd.DataFrame:
    frame = pd.read_csv(path).copy()
    frame["subject_id"] = frame["subject_id"].astype(str)
    frame["sleep_date"] = pd.to_datetime(frame["sleep_date"]).dt.strftime("%Y-%m-%d")
    frame["lifelog_date"] = pd.to_datetime(frame["lifelog_date"]).dt.strftime("%Y-%m-%d")
    return frame[TARGET_KEYS]


def load_rows(train_path: str, sample_path: str) -> pd.DataFrame:
    return pd.concat([normalize_metrics(train_path), normalize_metrics(sample_path)], ignore_index=True).drop_duplicates()


def grid_with_timestamp(path: str) -> pd.DataFrame:
    grid = pd.read_parquet(path).copy()
    grid["subject_id"] = grid["subject_id"].astype(str)
    grid["date"] = pd.to_datetime(grid["date"])
    grid["timestamp"] = grid["date"] + pd.to_timedelta(grid["tok"].astype(int) * 30, unit="m")
    return grid


def safe_sum(values: pd.Series) -> float:
    return float(np.nan_to_num(values.to_numpy(float), nan=0.0).sum())


def safe_mean(values: pd.Series) -> float:
    arr = values.to_numpy(float)
    if np.isfinite(arr).sum() == 0:
        return 0.0
    return float(np.nanmean(arr))


def safe_max(values: pd.Series) -> float:
    arr = values.to_numpy(float)
    if np.isfinite(arr).sum() == 0:
        return 0.0
    return float(np.nanmax(arr))


def longest_run(mask: np.ndarray) -> int:
    best = 0
    cur = 0
    for flag in mask.astype(bool):
        if flag:
            cur += 1
            best = max(best, cur)
        else:
            cur = 0
    return int(best)


def transition_count(mask: np.ndarray) -> int:
    if len(mask) <= 1:
        return 0
    return int(np.abs(np.diff(mask.astype(int))).sum())


def window_slice(day_grid: pd.DataFrame, onset: pd.Timestamp, wake: pd.Timestamp, name: str) -> pd.DataFrame:
    left, right = WINDOWS[name]
    if name == "sleep":
        start = onset
        end = wake
    elif name.startswith("prebed"):
        start = onset + pd.Timedelta(minutes=int(left))
        end = onset + pd.Timedelta(minutes=int(right))
    else:
        start = wake + pd.Timedelta(minutes=int(left or 0))
        end = wake + pd.Timedelta(minutes=int(right or 0))
    return day_grid[(day_grid["timestamp"] >= start) & (day_grid["timestamp"] < end)]


def summarize_window(part: pd.DataFrame, prefix: str) -> dict[str, float]:
    out: dict[str, float] = {f"z_si_{prefix}_tok_n": float(len(part))}
    for col in SIGNALS:
        if col not in part:
            continue
        out[f"z_si_{prefix}_{col}_sum"] = safe_sum(part[col])
        out[f"z_si_{prefix}_{col}_mean"] = safe_mean(part[col])
        out[f"z_si_{prefix}_{col}_max"] = safe_max(part[col])
    for event_col in ["ev_phone_active", "ev_moving", "ev_no_wear", "ev_low_coverage", "ev_charging_on"]:
        if event_col not in part:
            continue
        mask = np.nan_to_num(part[event_col].to_numpy(float), nan=0.0) > 0.5
        out[f"z_si_{prefix}_{event_col}_ratio"] = float(mask.mean()) if len(mask) else 0.0
        out[f"z_si_{prefix}_{event_col}_start_count"] = float(((part.get(event_col + "_start", 0).to_numpy(float) if event_col + "_start" in part else np.zeros(len(part))) > 0.5).sum())
        out[f"z_si_{prefix}_{event_col}_longest_run"] = float(longest_run(mask))
        out[f"z_si_{prefix}_{event_col}_transitions"] = float(transition_count(mask))
    if {"ev_phone_active", "ev_moving"}.issubset(part.columns):
        phone = np.nan_to_num(part["ev_phone_active"].to_numpy(float), nan=0.0) > 0.5
        moving = np.nan_to_num(part["ev_moving"].to_numpy(float), nan=0.0) > 0.5
        out[f"z_si_{prefix}_phone_or_move_ratio"] = float((phone | moving).mean()) if len(part) else 0.0
        out[f"z_si_{prefix}_phone_and_still_ratio"] = float((phone & ~moving).mean()) if len(part) else 0.0
    return out


def build_features(rows: pd.DataFrame, grid: pd.DataFrame, sleep: pd.DataFrame) -> pd.DataFrame:
    sleep = sleep.copy()
    sleep["subject_id"] = sleep["subject_id"].astype(str)
    sleep["sleep_date"] = pd.to_datetime(sleep["sleep_date"]).dt.strftime("%Y-%m-%d")
    sleep["sleep_onset"] = pd.to_datetime(sleep["sleep_onset"])
    sleep["wake_time"] = pd.to_datetime(sleep["wake_time"])
    merged = rows.merge(sleep, on=["subject_id", "sleep_date"], how="left", validate="many_to_one")
    grid_by_subject = {s: g.sort_values("timestamp") for s, g in grid.groupby("subject_id")}
    out_rows = []
    for _, row in merged.iterrows():
        subject = str(row["subject_id"])
        out = {"subject_id": subject, "lifelog_date": row["lifelog_date"]}
        onset = row.get("sleep_onset")
        wake = row.get("wake_time")
        out["z_si_tst_min"] = float(row.get("tst_min", 0.0) if pd.notna(row.get("tst_min")) else 0.0)
        out["z_si_sleep_eff"] = float(row.get("sleep_eff", 0.0) if pd.notna(row.get("sleep_eff")) else 0.0)
        out["z_si_sol_proxy_min"] = float(row.get("sol_proxy_min", 0.0) if pd.notna(row.get("sol_proxy_min")) else 0.0)
        out["z_si_n_awakenings"] = float(row.get("n_awakenings", 0.0) if pd.notna(row.get("n_awakenings")) else 0.0)
        if pd.isna(onset) or pd.isna(wake) or subject not in grid_by_subject:
            out_rows.append(out)
            continue
        subject_grid = grid_by_subject[subject]
        start = onset - pd.Timedelta(hours=8)
        end = wake + pd.Timedelta(hours=4)
        day_grid = subject_grid[(subject_grid["timestamp"] >= start) & (subject_grid["timestamp"] < end)]
        out["z_si_onset_hour"] = float(onset.hour + onset.minute / 60.0)
        out["z_si_wake_hour"] = float(wake.hour + wake.minute / 60.0)
        out["z_si_sleep_window_min"] = float((wake - onset).total_seconds() / 60.0)
        out["z_si_sleep_midpoint_hour"] = float(((onset + (wake - onset) / 2).hour + (onset + (wake - onset) / 2).minute / 60.0))
        for window in WINDOWS:
            out.update(summarize_window(window_slice(day_grid, onset, wake, window), window))
        out_rows.append(out)
    features = pd.DataFrame(out_rows).sort_values(OUTPUT_KEYS).reset_index(drop=True)
    for col in ["z_si_tst_min", "z_si_sleep_eff", "z_si_sol_proxy_min", "z_si_n_awakenings", "z_si_onset_hour", "z_si_wake_hour", "z_si_sleep_midpoint_hour"]:
        if col in features:
            center = features.groupby("subject_id")[col].transform("median")
            features[f"{col}_subject_dev"] = features[col] - center
            if col.endswith("_hour"):
                features[f"{col}_subject_abs_shift"] = (((features[col] - center + 12.0) % 24.0) - 12.0).abs()
    for window in [3, 7, 14]:
        for col in ["z_si_tst_min", "z_si_sleep_eff", "z_si_sol_proxy_min"]:
            shifted = features.groupby("subject_id")[col].shift(1)
            roll = shifted.groupby(features["subject_id"]).rolling(window, min_periods=2).mean().reset_index(level=0, drop=True)
            features[f"{col}_past{window}_delta"] = features[col] - roll
    return features


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
    grid = grid_with_timestamp(args.grid_path)
    sleep = pd.read_parquet(args.sleep_summary)
    features = build_features(rows, grid, sleep)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    features.to_parquet(output, index=False)
    feature_cols = [c for c in features.columns if c not in OUTPUT_KEYS]
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
        "windows": WINDOWS,
    }
    output.with_suffix(".report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    md = [
        "# Sleep Intrusion Latents",
        "",
        "## Purpose",
        "",
        "Build sleep-window, prebed, postwake, phone-intrusion, no-wear, low-coverage, and sleep-debt features.",
        "",
        f"- Output: `{output}`",
        f"- Rows: `{len(features)}`",
        f"- Feature count: `{len(feature_cols)}`",
        "",
        "## Feature Coverage",
        "",
        dataframe_to_markdown(coverage.head(30)),
    ]
    output.with_suffix(".report.md").write_text("\n".join(md), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build sleep intrusion and sleep-window sensor features.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--grid-path", default="artifacts/multires_30min_event_hybrid_grid.parquet")
    parser.add_argument("--sleep-summary", default="artifacts/07_sleep_summary.parquet")
    parser.add_argument("--output", default="artifacts/domain_sleep_intrusion_v1.parquet")
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
