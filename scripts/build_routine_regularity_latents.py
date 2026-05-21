from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


KEY_COLUMNS = ["subject_id", "lifelog_date"]
TARGET_KEYS = ["subject_id", "sleep_date", "lifelog_date"]
SIGNALS = {
    "phone": ["phone_activity", "screen_mean", "usage_total", "ev_phone_active"],
    "mobility": ["mobility_activity", "gps_speed_mean", "step_sum", "ev_moving"],
    "body": ["body_activity", "hr_mean", "pedo_n", "act_walk_ratio"],
    "coverage": ["sensor_coverage_n", "ev_present_phone", "ev_present_gps", "ev_present_hr", "ev_no_wear"],
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
    return frame[TARGET_KEYS]


def load_rows(train_path: str, sample_path: str) -> pd.DataFrame:
    return pd.concat([normalize_rows(train_path), normalize_rows(sample_path)], ignore_index=True).drop_duplicates()


def scaled_signal(group: pd.DataFrame, cols: list[str], scales: dict[str, float]) -> np.ndarray:
    values = []
    for col in cols:
        if col not in group:
            continue
        x = np.nan_to_num(group[col].to_numpy(float), nan=0.0, posinf=0.0, neginf=0.0)
        scale = scales.get(col, 1.0)
        if scale <= 1e-8:
            values.append(np.zeros_like(x))
        else:
            values.append(np.clip(x / scale, 0.0, 5.0))
    if not values:
        return np.zeros(len(group), dtype=float)
    return np.nanmean(np.vstack(values), axis=0)


def corr(a: np.ndarray, b: np.ndarray) -> float:
    a = np.nan_to_num(a.astype(float), nan=0.0, posinf=0.0, neginf=0.0)
    b = np.nan_to_num(b.astype(float), nan=0.0, posinf=0.0, neginf=0.0)
    if np.std(a) <= 1e-8 or np.std(b) <= 1e-8:
        return 0.0
    return safe_float(float(np.corrcoef(a, b)[0, 1]))


def cosine_dist(a: np.ndarray, b: np.ndarray) -> float:
    a = np.nan_to_num(a.astype(float), nan=0.0, posinf=0.0, neginf=0.0)
    b = np.nan_to_num(b.astype(float), nan=0.0, posinf=0.0, neginf=0.0)
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom <= 1e-8:
        return 0.0
    return safe_float(1.0 - float(np.dot(a, b) / denom))


def entropy(values: np.ndarray) -> float:
    values = np.clip(np.nan_to_num(values.astype(float), nan=0.0), 0.0, None)
    total = values.sum()
    if total <= 1e-8:
        return 0.0
    prob = values / total
    return safe_float(float(-(prob * np.log(np.maximum(prob, 1e-12))).sum()))


def circular_hour(signal: np.ndarray) -> tuple[float, float]:
    weights = np.clip(np.nan_to_num(signal.astype(float), nan=0.0), 0.0, None)
    total = weights.sum()
    if total <= 1e-8:
        return 0.0, 0.0
    angles = 2.0 * np.pi * np.arange(len(weights)) / len(weights)
    sin_v = float((np.sin(angles) * weights).sum() / total)
    cos_v = float((np.cos(angles) * weights).sum() / total)
    strength = float(np.sqrt(sin_v**2 + cos_v**2))
    hour = float((np.arctan2(sin_v, cos_v) % (2.0 * np.pi)) * 24.0 / (2.0 * np.pi))
    return safe_float(hour), safe_float(strength)


def hour_shift(value: float, center: float) -> float:
    return safe_float(((value - center + 12.0) % 24.0) - 12.0)


def active_bounds(signal: np.ndarray) -> tuple[float, float, float]:
    threshold = max(float(np.nanmedian(signal) + 0.5 * np.nanstd(signal)), 1e-8)
    idx = np.flatnonzero(signal > threshold)
    if len(idx) == 0:
        return 0.0, 0.0, 0.0
    return float(idx[0] / 2.0), float((idx[-1] + 1) / 2.0), float(len(idx) / len(signal))


def transition_count(states: np.ndarray) -> int:
    if len(states) <= 1:
        return 0
    return int((states[1:] != states[:-1]).sum())


def best_shift_correlation(today: dict[str, np.ndarray], baseline: dict[str, np.ndarray], max_lag: int = 4) -> tuple[float, float]:
    best_lag = 0
    best_corr = -2.0
    for lag in range(-max_lag, max_lag + 1):
        vals = []
        for name in SIGNALS:
            vals.append(corr(np.roll(today[name], lag), baseline[name]))
        score = float(np.mean(vals))
        if score > best_corr:
            best_corr = score
            best_lag = lag
    return safe_float(best_corr), float(best_lag)


def flatten_profile(signals: dict[str, np.ndarray]) -> np.ndarray:
    return np.concatenate([signals[name] for name in SIGNALS])


def daily_signal_tables(grid: pd.DataFrame) -> tuple[pd.DataFrame, dict[tuple[str, str], dict[str, np.ndarray]]]:
    grid = grid.copy()
    grid["subject_id"] = grid["subject_id"].astype(str)
    grid["date"] = pd.to_datetime(grid["date"]).dt.strftime("%Y-%m-%d")
    scales = {}
    for cols in SIGNALS.values():
        for col in cols:
            if col in grid:
                vals = np.abs(grid[col].to_numpy(float))
                scale = np.nanpercentile(vals, 90)
                if not np.isfinite(scale) or scale <= 1e-8:
                    scale = np.nanmax(vals)
                scales[col] = float(scale if np.isfinite(scale) and scale > 1e-8 else 1.0)
    records = []
    profiles: dict[tuple[str, str], dict[str, np.ndarray]] = {}
    for (subject, date), group in grid.groupby(["subject_id", "date"], sort=True):
        group = group.sort_values("tok")
        day = {name: scaled_signal(group, cols, scales) for name, cols in SIGNALS.items()}
        if len(next(iter(day.values()))) != 48:
            continue
        profiles[(subject, date)] = day
        row = {"subject_id": subject, "lifelog_date": date, "weekday": int(pd.Timestamp(date).weekday())}
        stacked = np.vstack([day[name] for name in SIGNALS])
        state = np.argmax(np.vstack([stacked, np.ones(48) * 0.05]), axis=0)
        for name, signal in day.items():
            start, end, active_ratio = active_bounds(signal)
            phase_hour, phase_strength = circular_hour(signal)
            row[f"{name}_sum"] = safe_float(signal.sum())
            row[f"{name}_std"] = safe_float(signal.std())
            row[f"{name}_entropy"] = entropy(signal)
            row[f"{name}_phase_hour"] = phase_hour
            row[f"{name}_phase_strength"] = phase_strength
            row[f"{name}_active_start_hour"] = start
            row[f"{name}_active_end_hour"] = end
            row[f"{name}_active_ratio"] = active_ratio
            row[f"{name}_night_ratio"] = safe_float(signal[:12].sum() / max(signal.sum(), 1e-8))
            row[f"{name}_evening_ratio"] = safe_float(signal[36:].sum() / max(signal.sum(), 1e-8))
        row["routine_state_entropy"] = entropy(np.bincount(state, minlength=len(SIGNALS) + 1).astype(float))
        row["routine_transition_count"] = float(transition_count(state))
        records.append(row)
    return pd.DataFrame(records).sort_values(KEY_COLUMNS).reset_index(drop=True), profiles


def sleep_features(rows: pd.DataFrame, sleep_summary: pd.DataFrame) -> pd.DataFrame:
    sleep = sleep_summary.copy()
    sleep["subject_id"] = sleep["subject_id"].astype(str)
    sleep["sleep_date"] = pd.to_datetime(sleep["sleep_date"]).dt.strftime("%Y-%m-%d")
    sleep["sleep_onset"] = pd.to_datetime(sleep["sleep_onset"])
    sleep["wake_time"] = pd.to_datetime(sleep["wake_time"])
    merged = rows.merge(sleep, on=["subject_id", "sleep_date"], how="left", validate="many_to_one")
    out = merged[KEY_COLUMNS].copy()
    onset_hour = merged["sleep_onset"].dt.hour + merged["sleep_onset"].dt.minute / 60.0
    wake_hour = merged["wake_time"].dt.hour + merged["wake_time"].dt.minute / 60.0
    midpoint = merged["sleep_onset"] + (merged["wake_time"] - merged["sleep_onset"]) / 2
    mid_hour = midpoint.dt.hour + midpoint.dt.minute / 60.0
    out["sleep_onset_hour"] = onset_hour.fillna(0.0).astype(float)
    out["wake_hour"] = wake_hour.fillna(0.0).astype(float)
    out["sleep_midpoint_hour"] = mid_hour.fillna(0.0).astype(float)
    for col in ["tst_min", "sleep_eff", "n_awakenings", "longest_block_min", "sol_proxy_min"]:
        out[col] = merged[col].fillna(0.0).astype(float)
    return out


def add_subject_deviation(features: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    for col in cols:
        if col not in features:
            continue
        center = features.groupby("subject_id")[col].transform("median")
        if col.endswith("_hour"):
            diff = ((features[col] - center + 12.0) % 24.0) - 12.0
            features[f"z_rr_{col}_subject_shift"] = diff
            features[f"z_rr_{col}_subject_abs_shift"] = diff.abs()
        else:
            features[f"z_rr_{col}_subject_dev"] = features[col] - center
            mad = features.groupby("subject_id")[col].transform(lambda s: np.nanmedian(np.abs(s - np.nanmedian(s))) + 1e-6)
            features[f"z_rr_{col}_subject_z"] = (features[col] - center) / mad
    return features


def build_features(rows: pd.DataFrame, grid: pd.DataFrame, sleep: pd.DataFrame) -> pd.DataFrame:
    daily, profiles = daily_signal_tables(grid)
    sleep_day = sleep_features(rows, sleep)
    features = rows[KEY_COLUMNS].merge(daily, on=KEY_COLUMNS, how="left").merge(sleep_day, on=KEY_COLUMNS, how="left")
    features["lifelog_dt"] = pd.to_datetime(features["lifelog_date"])
    features["weekday"] = features["lifelog_dt"].dt.weekday
    features["is_weekend"] = features["weekday"].isin([5, 6]).astype(float)

    profile_baseline: dict[str, dict[str, np.ndarray]] = {}
    weekday_baseline: dict[tuple[str, int], dict[str, np.ndarray]] = {}
    for subject in features["subject_id"].unique():
        subject_days = [p for (s, _), p in profiles.items() if s == subject]
        if subject_days:
            profile_baseline[subject] = {name: np.nanmedian(np.vstack([d[name] for d in subject_days]), axis=0) for name in SIGNALS}
        for weekday in range(7):
            days = [p for (s, d), p in profiles.items() if s == subject and pd.Timestamp(d).weekday() == weekday]
            if days:
                weekday_baseline[(subject, weekday)] = {name: np.nanmedian(np.vstack([d[name] for d in days]), axis=0) for name in SIGNALS}

    records = []
    for _, row in features.iterrows():
        subject = str(row["subject_id"])
        date = row["lifelog_date"]
        out = row.to_dict()
        today = profiles.get((subject, date))
        baseline = profile_baseline.get(subject)
        if today is not None and baseline is not None:
            flat_today = flatten_profile(today)
            flat_base = flatten_profile(baseline)
            out["z_rr_profile_corr_to_subject"] = corr(flat_today, flat_base)
            out["z_rr_profile_cosine_dist_to_subject"] = cosine_dist(flat_today, flat_base)
            out["z_rr_profile_abs_gap_to_subject"] = safe_float(np.mean(np.abs(flat_today - flat_base)))
            shift_corr, shift_lag = best_shift_correlation(today, baseline)
            out["z_rr_best_shift_corr_to_subject"] = shift_corr
            out["z_rr_best_shift_lag_to_subject"] = shift_lag
            wb = weekday_baseline.get((subject, int(row["weekday"])))
            if wb is not None:
                flat_wb = flatten_profile(wb)
                out["z_rr_profile_corr_to_subject_weekday"] = corr(flat_today, flat_wb)
                out["z_rr_profile_abs_gap_to_subject_weekday"] = safe_float(np.mean(np.abs(flat_today - flat_wb)))
                out["z_rr_weekday_gap_minus_global_gap"] = out["z_rr_profile_abs_gap_to_subject_weekday"] - out["z_rr_profile_abs_gap_to_subject"]
            for name in SIGNALS:
                out[f"z_rr_{name}_phase_shift_from_subject"] = hour_shift(out.get(f"{name}_phase_hour", 0.0), circular_hour(baseline[name])[0])
                out[f"z_rr_{name}_phase_abs_shift_from_subject"] = abs(out[f"z_rr_{name}_phase_shift_from_subject"])
        records.append(out)
    features = pd.DataFrame(records).sort_values(KEY_COLUMNS).reset_index(drop=True)

    raw_cols = [
        c
        for c in features.columns
        if c not in KEY_COLUMNS + ["lifelog_dt"]
        and not c.startswith("z_rr_")
        and pd.api.types.is_numeric_dtype(features[c])
    ]
    features = add_subject_deviation(features, raw_cols)
    features = features.sort_values(["subject_id", "lifelog_dt"]).reset_index(drop=True)

    rolling_cols = [
        "phone_sum",
        "mobility_sum",
        "body_sum",
        "coverage_sum",
        "routine_transition_count",
        "routine_state_entropy",
        "sleep_midpoint_hour",
        "sleep_onset_hour",
        "wake_hour",
        "tst_min",
        "sleep_eff",
    ]
    for window in ROLL_WINDOWS:
        for col in rolling_cols:
            if col not in features:
                continue
            shifted = features.groupby("subject_id")[col].shift(1)
            roll_mean = shifted.groupby(features["subject_id"]).rolling(window, min_periods=2).mean().reset_index(level=0, drop=True)
            roll_std = shifted.groupby(features["subject_id"]).rolling(window, min_periods=2).std().reset_index(level=0, drop=True).fillna(0.0)
            if col.endswith("_hour"):
                delta = ((features[col] - roll_mean + 12.0) % 24.0) - 12.0
            else:
                delta = features[col] - roll_mean
            features[f"z_rr_{col}_past{window}_delta"] = delta.fillna(0.0)
            features[f"z_rr_{col}_past{window}_abs_delta"] = delta.abs().fillna(0.0)
            features[f"z_rr_{col}_past{window}_volatility"] = roll_std.fillna(0.0)

    profile_cols = [c for c in features.columns if c.startswith("z_rr_")]
    keep = KEY_COLUMNS + profile_cols
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
    rows = load_rows(args.train_path, args.sample_path)
    grid = pd.read_parquet(args.grid_path)
    sleep = pd.read_parquet(args.sleep_summary)
    features = build_features(rows, grid, sleep)
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
        "signals": SIGNALS,
        "roll_windows": ROLL_WINDOWS,
    }
    output.with_suffix(".report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    md = [
        "# Routine Regularity Latents",
        "",
        "## Purpose",
        "",
        "Encode personal routine residuals, weekday-specific routine distance, circadian phase shift, sleep regularity break, and multi-scale volatility.",
        "",
        f"- Output: `{output}`",
        f"- Rows: `{len(features)}`",
        f"- Feature count: `{len(feature_cols)}`",
        "",
        "## Feature Coverage",
        "",
        dataframe_to_markdown(coverage.head(32)),
    ]
    output.with_suffix(".report.md").write_text("\n".join(md), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build routine regularity and personal routine residual latent features.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--grid-path", default="artifacts/multires_30min_event_hybrid_grid.parquet")
    parser.add_argument("--sleep-summary", default="artifacts/07_sleep_summary.parquet")
    parser.add_argument("--output", default="artifacts/domain_routine_regularity_v1.parquet")
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
