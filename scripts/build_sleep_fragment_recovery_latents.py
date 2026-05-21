from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


KEY_COLUMNS = ["subject_id", "lifelog_date"]
ROW_KEYS = ["subject_id", "sleep_date", "lifelog_date"]
ROLL_WINDOWS = [3, 7, 14, 28]


def normalize_rows(path: str) -> pd.DataFrame:
    frame = pd.read_csv(path).copy()
    frame["subject_id"] = frame["subject_id"].astype(str)
    frame["sleep_date"] = pd.to_datetime(frame["sleep_date"]).dt.strftime("%Y-%m-%d")
    frame["lifelog_date"] = pd.to_datetime(frame["lifelog_date"]).dt.strftime("%Y-%m-%d")
    return frame[ROW_KEYS]


def load_rows(train_path: str, sample_path: str) -> pd.DataFrame:
    return pd.concat([normalize_rows(train_path), normalize_rows(sample_path)], ignore_index=True).drop_duplicates()


def grid_with_timestamp(path: str) -> pd.DataFrame:
    grid = pd.read_parquet(path).copy()
    grid["subject_id"] = grid["subject_id"].astype(str)
    grid["date"] = pd.to_datetime(grid["date"])
    grid["timestamp"] = grid["date"] + pd.to_timedelta(grid["tok"].astype(int) * 30, unit="m")
    return grid.sort_values(["subject_id", "timestamp"]).reset_index(drop=True)


def safe_float(value: float) -> float:
    if value != value or np.isinf(value):
        return 0.0
    return float(value)


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


def slope(values: np.ndarray) -> float:
    values = np.nan_to_num(values.astype(float), nan=0.0, posinf=0.0, neginf=0.0)
    if len(values) < 3 or np.std(values) < 1e-8:
        return 0.0
    return safe_float(np.polyfit(np.arange(len(values), dtype=float), values, deg=1)[0])


def summarize_numeric(part: pd.DataFrame, col: str, prefix: str) -> dict[str, float]:
    if col not in part or len(part) == 0:
        return {
            f"{prefix}_mean": 0.0,
            f"{prefix}_std": 0.0,
            f"{prefix}_max": 0.0,
            f"{prefix}_sum": 0.0,
            f"{prefix}_slope": 0.0,
        }
    values = np.nan_to_num(part[col].to_numpy(float), nan=0.0, posinf=0.0, neginf=0.0)
    return {
        f"{prefix}_mean": safe_float(values.mean()),
        f"{prefix}_std": safe_float(values.std()),
        f"{prefix}_max": safe_float(values.max()),
        f"{prefix}_sum": safe_float(values.sum()),
        f"{prefix}_slope": slope(values),
    }


def summarize_event(part: pd.DataFrame, col: str, prefix: str) -> dict[str, float]:
    if col not in part or len(part) == 0:
        return {
            f"{prefix}_ratio": 0.0,
            f"{prefix}_starts": 0.0,
            f"{prefix}_transitions": 0.0,
            f"{prefix}_longest_run": 0.0,
        }
    mask = np.nan_to_num(part[col].to_numpy(float), nan=0.0) > 0.5
    starts = part.get(f"{col}_start")
    if starts is None:
        start_count = max(0, transition_count(mask) // 2)
    else:
        start_count = int((np.nan_to_num(starts.to_numpy(float), nan=0.0) > 0.5).sum())
    return {
        f"{prefix}_ratio": safe_float(mask.mean()),
        f"{prefix}_starts": float(start_count),
        f"{prefix}_transitions": float(transition_count(mask)),
        f"{prefix}_longest_run": float(longest_run(mask)),
    }


def event_fragment_features(events: pd.DataFrame, onset: pd.Timestamp, wake: pd.Timestamp) -> dict[str, float]:
    out: dict[str, float] = {}
    sleep_len = max((wake - onset).total_seconds() / 60.0, 1.0)
    aw = events[events["kind"].astype(str).str.contains("awak", case=False, na=False)].copy()
    durations = aw["duration_min"].to_numpy(float) if not aw.empty else np.array([], dtype=float)
    out["z_sfr_awaken_n"] = float(len(aw))
    out["z_sfr_awaken_total_min"] = safe_float(durations.sum()) if len(durations) else 0.0
    out["z_sfr_awaken_mean_min"] = safe_float(durations.mean()) if len(durations) else 0.0
    out["z_sfr_awaken_max_min"] = safe_float(durations.max()) if len(durations) else 0.0
    out["z_sfr_awaken_density"] = out["z_sfr_awaken_total_min"] / sleep_len
    out["z_sfr_awaken_count_per_hour"] = out["z_sfr_awaken_n"] / (sleep_len / 60.0)
    out["z_sfr_awaken_long_share"] = float((durations >= 10.0).mean()) if len(durations) else 0.0
    if aw.empty:
        out.update(
            {
                "z_sfr_awaken_first_frac": 0.0,
                "z_sfr_awaken_last_frac": 0.0,
                "z_sfr_awaken_midpoint_std": 0.0,
                "z_sfr_awaken_early_load": 0.0,
                "z_sfr_awaken_late_load": 0.0,
                "z_sfr_awaken_cluster_score": 0.0,
            }
        )
        return out
    mid = pd.to_datetime(aw["start"]) + (pd.to_datetime(aw["end"]) - pd.to_datetime(aw["start"])) / 2
    frac = ((mid - onset).dt.total_seconds() / 60.0 / sleep_len).clip(0.0, 1.0).to_numpy(float)
    dur_weight = durations / (durations.sum() + 1e-6)
    out["z_sfr_awaken_first_frac"] = safe_float(frac.min())
    out["z_sfr_awaken_last_frac"] = safe_float(frac.max())
    out["z_sfr_awaken_midpoint_std"] = safe_float(frac.std())
    out["z_sfr_awaken_early_load"] = safe_float(dur_weight[frac <= 0.33].sum())
    out["z_sfr_awaken_late_load"] = safe_float(dur_weight[frac >= 0.66].sum())
    if len(frac) >= 2:
        out["z_sfr_awaken_cluster_score"] = safe_float(1.0 / (np.diff(np.sort(frac)).mean() + 1e-3))
    else:
        out["z_sfr_awaken_cluster_score"] = 0.0
    return out


def window_part(grid: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    return grid[(grid["timestamp"] >= start) & (grid["timestamp"] < end)].copy()


def sensor_fragment_features(grid: pd.DataFrame, onset: pd.Timestamp, wake: pd.Timestamp) -> dict[str, float]:
    out: dict[str, float] = {}
    windows = {
        "sleep": (onset, wake),
        "sleep_first": (onset, onset + (wake - onset) / 3),
        "sleep_mid": (onset + (wake - onset) / 3, onset + (wake - onset) * 2 / 3),
        "sleep_last": (onset + (wake - onset) * 2 / 3, wake),
        "postwake1h": (wake, wake + pd.Timedelta(hours=1)),
        "postwake3h": (wake, wake + pd.Timedelta(hours=3)),
        "day_recovery": (wake, wake + pd.Timedelta(hours=8)),
    }
    numeric_cols = ["hr_mean", "hr_std", "hr_rmssd", "screen_mean", "usage_total", "step_sum", "mlight_mean", "wlight_mean", "sensor_coverage_n"]
    event_cols = ["ev_phone_active", "ev_moving", "ev_no_wear", "ev_low_coverage", "ev_charging_on"]
    for name, (start, end) in windows.items():
        part = window_part(grid, start, end)
        out[f"z_sfr_{name}_tok_n"] = float(len(part))
        for col in numeric_cols:
            out.update(summarize_numeric(part, col, f"z_sfr_{name}_{col}"))
        for col in event_cols:
            out.update(summarize_event(part, col, f"z_sfr_{name}_{col}"))
        if len(part):
            phone = np.nan_to_num(part.get("ev_phone_active", pd.Series(dtype=float)).to_numpy(float), nan=0.0) > 0.5
            moving = np.nan_to_num(part.get("ev_moving", pd.Series(dtype=float)).to_numpy(float), nan=0.0) > 0.5
            low = np.nan_to_num(part.get("ev_low_coverage", pd.Series(dtype=float)).to_numpy(float), nan=0.0) > 0.5
            light = np.nan_to_num(part.get("mlight_mean", pd.Series(dtype=float)).to_numpy(float), nan=0.0)
            out[f"z_sfr_{name}_phone_still_ratio"] = safe_float((phone & ~moving).mean())
            out[f"z_sfr_{name}_arousal_transition_load"] = safe_float(transition_count(phone) + transition_count(moving) + transition_count(low))
            out[f"z_sfr_{name}_light_burst_n"] = float((light > np.nanpercentile(light, 75) if len(light) else np.array([])).sum())
        else:
            out[f"z_sfr_{name}_phone_still_ratio"] = 0.0
            out[f"z_sfr_{name}_arousal_transition_load"] = 0.0
            out[f"z_sfr_{name}_light_burst_n"] = 0.0
    out["z_sfr_sleep_late_minus_early_phone"] = out.get("z_sfr_sleep_last_ev_phone_active_ratio", 0.0) - out.get("z_sfr_sleep_first_ev_phone_active_ratio", 0.0)
    out["z_sfr_sleep_late_minus_early_moving"] = out.get("z_sfr_sleep_last_ev_moving_ratio", 0.0) - out.get("z_sfr_sleep_first_ev_moving_ratio", 0.0)
    out["z_sfr_wake_activity_ramp"] = out.get("z_sfr_day_recovery_step_sum_slope", 0.0) + out.get("z_sfr_day_recovery_ev_moving_ratio", 0.0)
    out["z_sfr_wake_phone_still_load"] = out.get("z_sfr_postwake3h_phone_still_ratio", 0.0) + out.get("z_sfr_postwake3h_usage_total_mean", 0.0)
    out["z_sfr_sleep_sensor_fragment_score"] = (
        out.get("z_sfr_sleep_arousal_transition_load", 0.0)
        + out.get("z_sfr_sleep_ev_low_coverage_transitions", 0.0)
        + out.get("z_sfr_sleep_ev_no_wear_transitions", 0.0)
    )
    return out


def add_subject_stats(frame: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    additions = {}
    for col in cols:
        center = frame.groupby("subject_id")[col].transform("median")
        mad = frame.groupby("subject_id")[col].transform(lambda s: np.nanmedian(np.abs(s - np.nanmedian(s))) + 1e-6)
        additions[f"{col}_subdev"] = frame[col] - center
        additions[f"{col}_subrz"] = (frame[col] - center) / mad
        additions[f"{col}_subpct"] = frame.groupby("subject_id")[col].rank(pct=True).fillna(0.5)
    return pd.concat([frame, pd.DataFrame(additions, index=frame.index)], axis=1)


def add_roll_stats(frame: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    frame = frame.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True)
    additions = {}
    for window in ROLL_WINDOWS:
        for col in cols:
            shifted = frame.groupby("subject_id")[col].shift(1)
            roll = shifted.groupby(frame["subject_id"]).rolling(window, min_periods=2).mean().reset_index(level=0, drop=True)
            roll_std = shifted.groupby(frame["subject_id"]).rolling(window, min_periods=2).std().reset_index(level=0, drop=True)
            delta = frame[col] - roll
            additions[f"{col}_past{window}_delta"] = delta.fillna(0.0)
            additions[f"{col}_past{window}_abs_delta"] = delta.abs().fillna(0.0)
            additions[f"{col}_past{window}_volatility"] = roll_std.fillna(0.0)
    return pd.concat([frame, pd.DataFrame(additions, index=frame.index)], axis=1)


def build_features(args: argparse.Namespace) -> pd.DataFrame:
    rows = load_rows(args.train_path, args.sample_path)
    sleep = pd.read_parquet(args.sleep_summary).copy()
    sleep["subject_id"] = sleep["subject_id"].astype(str)
    sleep["sleep_date"] = pd.to_datetime(sleep["sleep_date"]).dt.strftime("%Y-%m-%d")
    sleep["sleep_onset"] = pd.to_datetime(sleep["sleep_onset"])
    sleep["wake_time"] = pd.to_datetime(sleep["wake_time"])
    events = pd.read_parquet(args.sleep_events).copy()
    events["subject_id"] = events["subject_id"].astype(str)
    events["sleep_date"] = pd.to_datetime(events["sleep_date"]).dt.strftime("%Y-%m-%d")
    events["start"] = pd.to_datetime(events["start"])
    events["end"] = pd.to_datetime(events["end"])
    grid = grid_with_timestamp(args.grid_path)
    grid_by_subject = {subject: part for subject, part in grid.groupby("subject_id")}
    events_by_key = {(s, d): part for (s, d), part in events.groupby(["subject_id", "sleep_date"])}
    merged = rows.merge(sleep, on=["subject_id", "sleep_date"], how="left", validate="many_to_one")
    out_rows = []
    for _, row in merged.iterrows():
        subject = str(row["subject_id"])
        sleep_date = str(row["sleep_date"])
        out = {"subject_id": subject, "lifelog_date": row["lifelog_date"]}
        onset = row.get("sleep_onset")
        wake = row.get("wake_time")
        out["z_sfr_tst_min"] = safe_float(row.get("tst_min", 0.0))
        out["z_sfr_sleep_eff"] = safe_float(row.get("sleep_eff", 0.0))
        out["z_sfr_sol_proxy_min"] = safe_float(row.get("sol_proxy_min", 0.0))
        out["z_sfr_n_awakenings"] = safe_float(row.get("n_awakenings", 0.0))
        out["z_sfr_n_awakenings_long"] = safe_float(row.get("n_awakenings_long", 0.0))
        out["z_sfr_longest_block_min"] = safe_float(row.get("longest_block_min", 0.0))
        if pd.notna(onset) and pd.notna(wake):
            sleep_len = max((wake - onset).total_seconds() / 60.0, 1.0)
            out["z_sfr_sleep_window_min"] = sleep_len
            out["z_sfr_longest_block_share"] = out["z_sfr_longest_block_min"] / sleep_len
            out["z_sfr_sol_share"] = out["z_sfr_sol_proxy_min"] / sleep_len
            out["z_sfr_onset_hour"] = safe_float(onset.hour + onset.minute / 60.0)
            out["z_sfr_wake_hour"] = safe_float(wake.hour + wake.minute / 60.0)
            out.update(event_fragment_features(events_by_key.get((subject, sleep_date), events.iloc[:0]), onset, wake))
            if subject in grid_by_subject:
                subject_grid = grid_by_subject[subject]
                start = onset - pd.Timedelta(hours=1)
                end = wake + pd.Timedelta(hours=10)
                day_grid = subject_grid[(subject_grid["timestamp"] >= start) & (subject_grid["timestamp"] < end)]
                out.update(sensor_fragment_features(day_grid, onset, wake))
        out_rows.append(out)
    features = pd.DataFrame(out_rows).sort_values(KEY_COLUMNS).reset_index(drop=True)
    base_cols = [c for c in features.columns if c.startswith("z_sfr_") and pd.api.types.is_numeric_dtype(features[c])]
    stat_cols = [
        c
        for c in base_cols
        if any(key in c for key in ["awaken", "fragment", "postwake", "recovery", "wake_", "sleep_eff", "longest_block", "phone_still"])
    ][:120]
    features = add_subject_stats(features, stat_cols)
    roll_cols = [
        c
        for c in [
            "z_sfr_awaken_density",
            "z_sfr_awaken_late_load",
            "z_sfr_sleep_sensor_fragment_score",
            "z_sfr_sleep_eff",
            "z_sfr_longest_block_share",
            "z_sfr_wake_activity_ramp",
            "z_sfr_wake_phone_still_load",
            "z_sfr_postwake3h_ev_moving_ratio",
            "z_sfr_postwake3h_usage_total_mean",
        ]
        if c in features
    ]
    features = add_roll_stats(features, roll_cols)
    keep_cols = KEY_COLUMNS + sorted([c for c in features.columns if c.startswith("z_sfr_")])
    return features[keep_cols].fillna(0.0).replace([np.inf, -np.inf], 0.0)


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
        "hypothesis": "S-family labels may respond to sleep fragmentation and post-wake recovery rather than total sleep amount",
    }
    output.with_suffix(".report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    md = [
        "# Sleep Fragment Recovery Latents",
        "",
        "## Purpose",
        "",
        "Encode awakening fragmentation, sleep-window sensor arousal, late-sleep disturbance, and post-wake recovery shape for S1/S3 discovery.",
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
    parser = argparse.ArgumentParser(description="Build sleep fragmentation and recovery latent features.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--sleep-summary", default="artifacts/07_sleep_summary.parquet")
    parser.add_argument("--sleep-events", default="artifacts/07_sleep_events.parquet")
    parser.add_argument("--grid-path", default="artifacts/multires_30min_event_hybrid_grid.parquet")
    parser.add_argument("--output", default="artifacts/domain_sleep_fragment_recovery_v1.parquet")
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
