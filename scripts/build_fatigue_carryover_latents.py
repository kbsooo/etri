from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


KEY_COLUMNS = ["subject_id", "lifelog_date"]
ROW_KEYS = ["subject_id", "sleep_date", "lifelog_date"]
WINDOWS = {
    "recovery4h": ("wake", 0, 240),
    "postwake10h": ("wake", 0, 600),
    "fatigue_late": ("wake", 720, None),
    "prebed4h": ("onset", -240, 0),
}
SIGNALS = {
    "phone": ["phone_activity", "screen_mean", "usage_total", "ev_phone_active"],
    "activity": ["mobility_activity", "step_sum", "distance_sum", "ev_moving"],
    "body": ["body_activity", "hr_mean", "hr_rmssd", "pedo_n"],
    "light": ["mlight_mean", "wlight_mean", "mlight_max", "wlight_max"],
    "coverage": ["sensor_coverage_n", "ev_no_wear", "ev_low_coverage"],
}
ROLL_WINDOWS = [3, 7, 14, 28]


def safe_float(value: float) -> float:
    if value != value or np.isinf(value):
        return 0.0
    return float(value)


def normalize_rows(path: str) -> pd.DataFrame:
    frame = pd.read_csv(path).copy()
    frame["subject_id"] = frame["subject_id"].astype(str)
    frame["sleep_date"] = pd.to_datetime(frame["sleep_date"]).dt.strftime("%Y-%m-%d")
    frame["lifelog_date"] = pd.to_datetime(frame["lifelog_date"]).dt.strftime("%Y-%m-%d")
    return frame[ROW_KEYS]


def load_rows(train_path: str, sample_path: str) -> pd.DataFrame:
    return pd.concat([normalize_rows(train_path), normalize_rows(sample_path)], ignore_index=True).drop_duplicates()


def grid_with_time(path: str) -> pd.DataFrame:
    grid = pd.read_parquet(path).copy()
    grid["subject_id"] = grid["subject_id"].astype(str)
    grid["date"] = pd.to_datetime(grid["date"])
    grid["timestamp"] = grid["date"] + pd.to_timedelta(grid["tok"].astype(int) * 30, unit="m")
    return grid


def scaled_signal(part: pd.DataFrame, cols: list[str], scales: dict[str, float]) -> np.ndarray:
    values = []
    for col in cols:
        if col not in part:
            continue
        x = np.nan_to_num(part[col].to_numpy(float), nan=0.0, posinf=0.0, neginf=0.0)
        scale = scales.get(col, 1.0)
        values.append(np.zeros_like(x) if scale <= 1e-8 else np.clip(x / scale, 0.0, 5.0))
    if not values:
        return np.zeros(len(part), dtype=float)
    return np.nanmean(np.vstack(values), axis=0)


def summarize(values: np.ndarray, prefix: str) -> dict[str, float]:
    values = np.nan_to_num(values.astype(float), nan=0.0, posinf=0.0, neginf=0.0)
    if len(values) == 0:
        return {
            f"{prefix}_sum": 0.0,
            f"{prefix}_mean": 0.0,
            f"{prefix}_std": 0.0,
            f"{prefix}_max": 0.0,
            f"{prefix}_slope": 0.0,
        }
    x = np.arange(len(values), dtype=float)
    slope = 0.0
    if len(values) >= 3 and np.std(values) > 1e-8:
        slope = float(np.polyfit(x, values, deg=1)[0])
    return {
        f"{prefix}_sum": safe_float(values.sum()),
        f"{prefix}_mean": safe_float(values.mean()),
        f"{prefix}_std": safe_float(values.std()),
        f"{prefix}_max": safe_float(values.max()),
        f"{prefix}_slope": safe_float(slope),
    }


def window_part(subject_grid: pd.DataFrame, onset: pd.Timestamp, wake: pd.Timestamp, spec: tuple[str, int, int | None]) -> pd.DataFrame:
    anchor, start_min, end_min = spec
    anchor_time = wake if anchor == "wake" else onset
    start = anchor_time + pd.Timedelta(minutes=int(start_min))
    end = onset if end_min is None else anchor_time + pd.Timedelta(minutes=int(end_min))
    if end <= start:
        return subject_grid.iloc[:0]
    return subject_grid[(subject_grid["timestamp"] >= start) & (subject_grid["timestamp"] < end)]


def add_subject_deviation(frame: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    additions = {}
    for col in cols:
        center = frame.groupby("subject_id")[col].transform("median")
        mad = frame.groupby("subject_id")[col].transform(lambda s: np.nanmedian(np.abs(s - np.nanmedian(s))) + 1e-6)
        additions[f"z_fc_{col}_subdev"] = frame[col] - center
        additions[f"z_fc_{col}_subrz"] = (frame[col] - center) / mad
    return pd.concat([frame, pd.DataFrame(additions, index=frame.index)], axis=1)


def add_roll_features(frame: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    frame = frame.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True)
    additions = {}
    for window in ROLL_WINDOWS:
        for col in cols:
            shifted = frame.groupby("subject_id")[col].shift(1)
            roll = shifted.groupby(frame["subject_id"]).rolling(window, min_periods=2).mean().reset_index(level=0, drop=True)
            roll_std = shifted.groupby(frame["subject_id"]).rolling(window, min_periods=2).std().reset_index(level=0, drop=True)
            delta = frame[col] - roll
            additions[f"z_fc_{col}_past{window}_delta"] = delta.fillna(0.0)
            additions[f"z_fc_{col}_past{window}_abs_delta"] = delta.abs().fillna(0.0)
            additions[f"z_fc_{col}_past{window}_volatility"] = roll_std.fillna(0.0)
    return pd.concat([frame, pd.DataFrame(additions, index=frame.index)], axis=1)


def build_features(args: argparse.Namespace) -> pd.DataFrame:
    rows = load_rows(args.train_path, args.sample_path)
    grid = grid_with_time(args.grid_path)
    sleep = pd.read_parquet(args.sleep_summary).copy()
    sleep["subject_id"] = sleep["subject_id"].astype(str)
    sleep["sleep_date"] = pd.to_datetime(sleep["sleep_date"]).dt.strftime("%Y-%m-%d")
    sleep["sleep_onset"] = pd.to_datetime(sleep["sleep_onset"])
    sleep["wake_time"] = pd.to_datetime(sleep["wake_time"])
    merged = rows.merge(sleep, on=["subject_id", "sleep_date"], how="left", validate="many_to_one")

    scales = {}
    for cols in SIGNALS.values():
        for col in cols:
            if col in grid:
                vals = np.abs(grid[col].to_numpy(float))
                scale = np.nanpercentile(vals, 90)
                if not np.isfinite(scale) or scale <= 1e-8:
                    scale = np.nanmax(vals)
                scales[col] = float(scale if np.isfinite(scale) and scale > 1e-8 else 1.0)

    grid_by_subject = {s: g.sort_values("timestamp") for s, g in grid.groupby("subject_id")}
    out_rows = []
    for _, row in merged.iterrows():
        subject = str(row["subject_id"])
        out = {"subject_id": subject, "lifelog_date": row["lifelog_date"]}
        onset = row.get("sleep_onset")
        wake = row.get("wake_time")
        out["z_fc_tst_min"] = safe_float(row.get("tst_min", 0.0))
        out["z_fc_sleep_eff"] = safe_float(row.get("sleep_eff", 0.0))
        out["z_fc_sol_proxy_min"] = safe_float(row.get("sol_proxy_min", 0.0))
        out["z_fc_n_awakenings"] = safe_float(row.get("n_awakenings", 0.0))
        out["z_fc_longest_block_min"] = safe_float(row.get("longest_block_min", 0.0))
        if pd.isna(onset) or pd.isna(wake) or subject not in grid_by_subject:
            out_rows.append(out)
            continue
        subject_grid = grid_by_subject[subject]
        out["z_fc_wake_hour"] = safe_float(wake.hour + wake.minute / 60.0)
        out["z_fc_onset_hour"] = safe_float(onset.hour + onset.minute / 60.0)
        out["z_fc_awake_interval_min"] = safe_float((onset - wake).total_seconds() / 60.0)
        for win_name, spec in WINDOWS.items():
            part = window_part(subject_grid, onset, wake, spec)
            out[f"z_fc_{win_name}_tok_n"] = float(len(part))
            for sig_name, cols in SIGNALS.items():
                sig = scaled_signal(part, cols, scales)
                out.update(summarize(sig, f"z_fc_{win_name}_{sig_name}"))
            if len(part):
                phone = scaled_signal(part, SIGNALS["phone"], scales)
                activity = scaled_signal(part, SIGNALS["activity"], scales)
                out[f"z_fc_{win_name}_phone_activity_gap"] = safe_float(phone.mean() - activity.mean())
                out[f"z_fc_{win_name}_arousal_load"] = safe_float(phone.mean() + activity.mean() + scaled_signal(part, SIGNALS["light"], scales).mean())
        out["z_fc_late_minus_recovery_phone"] = out.get("z_fc_fatigue_late_phone_mean", 0.0) - out.get("z_fc_recovery4h_phone_mean", 0.0)
        out["z_fc_late_minus_recovery_activity"] = out.get("z_fc_fatigue_late_activity_mean", 0.0) - out.get("z_fc_recovery4h_activity_mean", 0.0)
        out["z_fc_prebed_minus_recovery_arousal"] = out.get("z_fc_prebed4h_arousal_load", 0.0) - out.get("z_fc_recovery4h_arousal_load", 0.0)
        out_rows.append(out)

    features = pd.DataFrame(out_rows).sort_values(KEY_COLUMNS).reset_index(drop=True)
    features["lifelog_dt"] = pd.to_datetime(features["lifelog_date"])
    features["weekday"] = features["lifelog_dt"].dt.weekday.astype(float)
    features["is_monday"] = (features["weekday"] == 0).astype(float)
    features["is_after_weekend"] = features["weekday"].isin([0, 1]).astype(float)

    base_cols = [c for c in features.columns if c.startswith("z_fc_") and pd.api.types.is_numeric_dtype(features[c])]
    features = add_subject_deviation(features, base_cols[:80])
    debt_cols = [
        "z_fc_tst_min",
        "z_fc_sleep_eff",
        "z_fc_awake_interval_min",
        "z_fc_fatigue_late_phone_mean",
        "z_fc_fatigue_late_activity_mean",
        "z_fc_prebed4h_phone_mean",
        "z_fc_recovery4h_activity_slope",
        "z_fc_postwake10h_activity_sum",
    ]
    features = add_roll_features(features, [c for c in debt_cols if c in features])
    if "z_fc_tst_min_past7_delta" in features:
        features["z_fc_sleep_debt7"] = (-features["z_fc_tst_min_past7_delta"]).clip(lower=0.0)
    if "z_fc_tst_min_past14_delta" in features:
        features["z_fc_sleep_debt14"] = (-features["z_fc_tst_min_past14_delta"]).clip(lower=0.0)
    if "z_fc_fatigue_late_phone_mean_past14_delta" in features:
        features["z_fc_screen_fatigue14"] = features["z_fc_fatigue_late_phone_mean_past14_delta"].clip(lower=0.0)
    if {"is_after_weekend", "z_fc_sleep_debt7"}.issubset(features.columns):
        features["z_fc_weekend_transition_debt"] = features["is_after_weekend"] * features["z_fc_sleep_debt7"]

    keep = KEY_COLUMNS + sorted([c for c in features.columns if c.startswith("z_fc_") or c in ["weekday", "is_monday", "is_after_weekend"]])
    return features[keep].fillna(0.0).replace([np.inf, -np.inf], 0.0)


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
    features = build_features(args)
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
        "windows": WINDOWS,
        "roll_windows": ROLL_WINDOWS,
    }
    output.with_suffix(".report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    md = [
        "# Fatigue Carryover Latents",
        "",
        "## Purpose",
        "",
        "Encode wake-anchored recovery, late-day fatigue accumulation, sleep debt, screen fatigue, and weekend transition carry-over.",
        "",
        f"- Output: `{output}`",
        f"- Rows: `{len(features)}`",
        f"- Feature count: `{len(feature_cols)}`",
        "",
        "## Feature Coverage",
        "",
        dataframe_to_markdown(coverage.head(36)),
    ]
    output.with_suffix(".report.md").write_text("\n".join(md), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build fatigue/recovery carry-over feature latents.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--grid-path", default="artifacts/multires_30min_event_hybrid_grid.parquet")
    parser.add_argument("--sleep-summary", default="artifacts/07_sleep_summary.parquet")
    parser.add_argument("--output", default="artifacts/domain_fatigue_carryover_v1.parquet")
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
