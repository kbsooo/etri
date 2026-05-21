from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


KEY_COLUMNS = ["subject_id", "lifelog_date"]
TARGET_KEYS = ["subject_id", "sleep_date", "lifelog_date"]
ROLL_WINDOWS = [3, 7, 14, 28]


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
    return grid.sort_values(["subject_id", "timestamp"]).reset_index(drop=True)


def safe_div(numer: pd.Series | np.ndarray | float, denom: pd.Series | np.ndarray | float) -> np.ndarray:
    return (pd.Series(numer, copy=False).astype(float) / (pd.Series(denom, copy=False).astype(float) + 1e-6)).to_numpy()


def values(part: pd.DataFrame, col: str) -> np.ndarray:
    if col not in part:
        return np.zeros(len(part), dtype=float)
    return np.nan_to_num(part[col].to_numpy(float), nan=0.0, posinf=0.0, neginf=0.0)


def flag(part: pd.DataFrame, col: str, threshold: float = 0.5) -> np.ndarray:
    return values(part, col) > threshold


def longest_run(mask: np.ndarray) -> int:
    best = 0
    cur = 0
    for item in mask.astype(bool):
        if item:
            cur += 1
            best = max(best, cur)
        else:
            cur = 0
    return int(best)


def count_starts(mask: np.ndarray) -> int:
    flags = mask.astype(bool)
    if len(flags) == 0:
        return 0
    shifted = np.r_[False, flags[:-1]]
    return int((flags & ~shifted).sum())


def count_toggles(mask: np.ndarray) -> int:
    flags = mask.astype(bool)
    if len(flags) <= 1:
        return 0
    return int(np.not_equal(flags[1:], flags[:-1]).sum())


def last_true_minutes(part: pd.DataFrame, mask: np.ndarray, anchor: pd.Timestamp) -> float:
    if len(part) == 0 or not mask.any():
        return 999.0
    return float((anchor - part.loc[mask, "timestamp"].iloc[-1]).total_seconds() / 60.0)


def first_stable_run_start_minutes(part: pd.DataFrame, mask: np.ndarray, anchor: pd.Timestamp, run_len: int = 2) -> float:
    flags = mask.astype(bool)
    if len(flags) < run_len:
        return 999.0
    for idx in range(0, len(flags) - run_len + 1):
        if flags[idx : idx + run_len].all():
            return float((anchor - part["timestamp"].iloc[idx]).total_seconds() / 60.0)
    return 999.0


def aggregate_window(part: pd.DataFrame, prefix: str, bright_thr: float, dark_thr: float) -> dict[str, float]:
    out: dict[str, float] = {}
    n = len(part)
    phone = flag(part, "ev_phone_active")
    moving = flag(part, "ev_moving")
    charging = flag(part, "ev_charging_on")
    social = flag(part, "ev_social_audio")
    low_cov = flag(part, "ev_low_coverage")
    no_wear = flag(part, "ev_no_wear")
    light = values(part, "mlight_mean") + values(part, "wlight_mean")
    bright = light > bright_thr
    dark = light <= dark_thr
    screen = values(part, "screen_mean")
    steps = values(part, "step_sum")
    silence = values(part, "amb_silence")
    speech = values(part, "amb_speech")
    music = values(part, "amb_music")
    vehicle = values(part, "amb_vehicle")
    phone_usage = values(part, "usage_total")
    still = ~moving

    out[f"{prefix}_tok_n"] = float(n)
    out[f"{prefix}_phone_ratio"] = float(phone.mean()) if n else 0.0
    out[f"{prefix}_phone_starts"] = float(count_starts(phone))
    out[f"{prefix}_phone_toggles"] = float(count_toggles(phone))
    out[f"{prefix}_phone_longest_run"] = float(longest_run(phone))
    out[f"{prefix}_usage_total"] = float(phone_usage.sum())
    out[f"{prefix}_usage_max"] = float(phone_usage.max()) if n else 0.0
    out[f"{prefix}_screen_mean"] = float(screen.mean()) if n else 0.0
    out[f"{prefix}_screen_max"] = float(screen.max()) if n else 0.0
    out[f"{prefix}_moving_ratio"] = float(moving.mean()) if n else 0.0
    out[f"{prefix}_moving_starts"] = float(count_starts(moving))
    out[f"{prefix}_step_sum"] = float(steps.sum())
    out[f"{prefix}_charging_ratio"] = float(charging.mean()) if n else 0.0
    out[f"{prefix}_charging_starts"] = float(count_starts(charging))
    out[f"{prefix}_social_audio_ratio"] = float(social.mean()) if n else 0.0
    out[f"{prefix}_social_audio_starts"] = float(count_starts(social))
    out[f"{prefix}_bright_ratio"] = float(bright.mean()) if n else 0.0
    out[f"{prefix}_dark_ratio"] = float(dark.mean()) if n else 0.0
    out[f"{prefix}_light_mean"] = float(light.mean()) if n else 0.0
    out[f"{prefix}_silence_mean"] = float(silence.mean()) if n else 0.0
    out[f"{prefix}_speech_mean"] = float(speech.mean()) if n else 0.0
    out[f"{prefix}_music_mean"] = float(music.mean()) if n else 0.0
    out[f"{prefix}_vehicle_mean"] = float(vehicle.mean()) if n else 0.0
    out[f"{prefix}_lowcov_or_nowear_ratio"] = float((low_cov | no_wear).mean()) if n else 0.0
    out[f"{prefix}_settled_ratio"] = float((still & ~phone & dark).mean()) if n else 0.0
    out[f"{prefix}_settled_charging_ratio"] = float((still & ~phone & dark & charging).mean()) if n else 0.0
    out[f"{prefix}_conflict_phone_dark_still_ratio"] = float((phone & dark & still).mean()) if n else 0.0
    out[f"{prefix}_conflict_phone_charging_ratio"] = float((phone & charging).mean()) if n else 0.0
    return out


def summarize_onset_transition(day_grid: pd.DataFrame, onset: pd.Timestamp, bright_thr: float, dark_thr: float) -> dict[str, float]:
    out: dict[str, float] = {}
    window_defs = {
        "pre6h": (onset - pd.Timedelta(hours=6), onset),
        "pre4h": (onset - pd.Timedelta(hours=4), onset),
        "pre2h": (onset - pd.Timedelta(hours=2), onset),
        "pre1h": (onset - pd.Timedelta(hours=1), onset),
        "pre30m": (onset - pd.Timedelta(minutes=30), onset),
        "post1h": (onset, onset + pd.Timedelta(hours=1)),
    }
    parts = {name: day_grid[(day_grid["timestamp"] >= start) & (day_grid["timestamp"] < end)] for name, (start, end) in window_defs.items()}
    for name, part in parts.items():
        out.update(aggregate_window(part, f"z_sot_{name}", bright_thr, dark_thr))

    pre6h = parts["pre6h"]
    pre4h = parts["pre4h"]
    light6 = values(pre6h, "mlight_mean") + values(pre6h, "wlight_mean")
    phone6 = flag(pre6h, "ev_phone_active")
    moving6 = flag(pre6h, "ev_moving")
    charging6 = flag(pre6h, "ev_charging_on")
    social6 = flag(pre6h, "ev_social_audio")
    bright6 = light6 > bright_thr
    screen6 = values(pre6h, "screen_mean") > 0.0
    dark6 = light6 <= dark_thr
    still6 = ~moving6
    quiet6 = values(pre6h, "amb_silence") >= np.maximum(values(pre6h, "amb_speech"), values(pre6h, "amb_music"))
    settled6 = still6 & ~phone6 & dark6
    quiet_settled6 = settled6 & quiet6

    out["z_sot_last_phone_latency_min"] = last_true_minutes(pre6h, phone6, onset)
    out["z_sot_last_moving_latency_min"] = last_true_minutes(pre6h, moving6, onset)
    out["z_sot_last_bright_latency_min"] = last_true_minutes(pre6h, bright6, onset)
    out["z_sot_last_screen_latency_min"] = last_true_minutes(pre6h, screen6, onset)
    out["z_sot_last_social_audio_latency_min"] = last_true_minutes(pre6h, social6, onset)
    out["z_sot_last_charging_latency_min"] = last_true_minutes(pre6h, charging6, onset)
    for col in [
        "phone",
        "moving",
        "bright",
        "screen",
        "social_audio",
        "charging",
    ]:
        out[f"z_sot_{col}_recency"] = 1.0 / (1.0 + out[f"z_sot_last_{col}_latency_min"])

    out["z_sot_settled_run_start_latency_min"] = first_stable_run_start_minutes(pre4h, settled6[-len(pre4h) :] if len(pre4h) else np.array([], dtype=bool), onset)
    out["z_sot_quiet_settled_run_start_latency_min"] = first_stable_run_start_minutes(
        pre4h, quiet_settled6[-len(pre4h) :] if len(pre4h) else np.array([], dtype=bool), onset
    )
    out["z_sot_settled_recency"] = 1.0 / (1.0 + out["z_sot_settled_run_start_latency_min"])
    out["z_sot_quiet_settled_recency"] = 1.0 / (1.0 + out["z_sot_quiet_settled_run_start_latency_min"])

    def g(name: str) -> float:
        return float(out.get(name, 0.0))

    out["z_sot_phone_shutdown_slope_4h_to_1h"] = g("z_sot_pre4h_phone_ratio") - g("z_sot_pre1h_phone_ratio")
    out["z_sot_phone_shutdown_slope_2h_to_30m"] = g("z_sot_pre2h_phone_ratio") - g("z_sot_pre30m_phone_ratio")
    out["z_sot_moving_shutdown_slope_4h_to_1h"] = g("z_sot_pre4h_moving_ratio") - g("z_sot_pre1h_moving_ratio")
    out["z_sot_light_shutdown_slope_4h_to_1h"] = g("z_sot_pre4h_bright_ratio") - g("z_sot_pre1h_bright_ratio")
    out["z_sot_dark_rise_2h_to_30m"] = g("z_sot_pre30m_dark_ratio") - g("z_sot_pre2h_dark_ratio")
    out["z_sot_charging_rise_2h_to_30m"] = g("z_sot_pre30m_charging_ratio") - g("z_sot_pre2h_charging_ratio")
    out["z_sot_silence_rise_2h_to_30m"] = g("z_sot_pre30m_silence_mean") - g("z_sot_pre2h_silence_mean")
    out["z_sot_usage_decay_2h_to_30m"] = np.log1p(g("z_sot_pre2h_usage_total")) - np.log1p(g("z_sot_pre30m_usage_total"))
    out["z_sot_fragmentation_pressure"] = (
        g("z_sot_pre2h_phone_starts")
        + g("z_sot_pre2h_moving_starts")
        + g("z_sot_pre2h_social_audio_starts")
        + 0.5 * g("z_sot_pre2h_phone_toggles")
    )
    out["z_sot_last_hour_conflict_pressure"] = (
        g("z_sot_pre1h_conflict_phone_dark_still_ratio")
        + g("z_sot_pre1h_conflict_phone_charging_ratio")
        + g("z_sot_pre1h_bright_ratio")
        + g("z_sot_pre1h_moving_ratio")
    )
    out["z_sot_onset_readiness_score"] = (
        g("z_sot_pre30m_dark_ratio")
        + g("z_sot_pre30m_settled_ratio")
        + g("z_sot_pre30m_silence_mean")
        + g("z_sot_pre30m_charging_ratio")
        - g("z_sot_pre30m_phone_ratio")
        - g("z_sot_pre30m_moving_ratio")
        - g("z_sot_pre30m_bright_ratio")
    )
    out["z_sot_transition_cleanliness_score"] = (
        out["z_sot_phone_shutdown_slope_2h_to_30m"]
        + out["z_sot_moving_shutdown_slope_4h_to_1h"]
        + out["z_sot_dark_rise_2h_to_30m"]
        + out["z_sot_charging_rise_2h_to_30m"]
        - out["z_sot_fragmentation_pressure"] / 4.0
    )
    out["z_sot_onset_disruption_score"] = (
        out["z_sot_last_hour_conflict_pressure"]
        + out["z_sot_phone_recency"]
        + out["z_sot_bright_recency"]
        + out["z_sot_social_audio_recency"]
        - out["z_sot_settled_recency"]
    )
    return out


def add_subject_stats(frame: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    additions = {}
    for col in cols:
        center = frame.groupby("subject_id")[col].transform("median")
        mad = frame.groupby("subject_id")[col].transform(lambda s: np.nanmedian(np.abs(s - np.nanmedian(s))))
        iqr = frame.groupby("subject_id")[col].transform(lambda s: np.nanpercentile(s, 75) - np.nanpercentile(s, 25))
        std = frame.groupby("subject_id")[col].transform("std").fillna(0.0)
        scale = pd.concat([mad, iqr / 1.349, std / 1.4826, pd.Series(1.0, index=frame.index)], axis=1).max(axis=1)
        additions[f"{col}_subdev"] = frame[col] - center
        additions[f"{col}_subrz"] = ((frame[col] - center) / scale).clip(-20.0, 20.0)
        additions[f"{col}_subpct"] = frame.groupby("subject_id")[col].rank(pct=True).fillna(0.5)
    return pd.concat([frame, pd.DataFrame(additions, index=frame.index)], axis=1)


def add_rolling(frame: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    frame = frame.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True)
    additions = {}
    for window in ROLL_WINDOWS:
        for col in cols:
            shifted = frame.groupby("subject_id")[col].shift(1)
            roll_mean = shifted.groupby(frame["subject_id"]).rolling(window, min_periods=2).mean().reset_index(level=0, drop=True)
            roll_std = shifted.groupby(frame["subject_id"]).rolling(window, min_periods=3).std().reset_index(level=0, drop=True)
            additions[f"{col}_past{window}_delta"] = (frame[col] - roll_mean).fillna(0.0)
            additions[f"{col}_past{window}_volatility_gap"] = (frame[col] - roll_mean).abs().div(roll_std.fillna(0.0) + 1.0).fillna(0.0)
    return pd.concat([frame, pd.DataFrame(additions, index=frame.index)], axis=1)


def build_features(args: argparse.Namespace) -> pd.DataFrame:
    rows = load_rows(args.train_path, args.sample_path)
    sleep = pd.read_parquet(args.sleep_summary).copy()
    sleep["subject_id"] = sleep["subject_id"].astype(str)
    sleep["sleep_date"] = pd.to_datetime(sleep["sleep_date"]).dt.strftime("%Y-%m-%d")
    sleep["sleep_onset"] = pd.to_datetime(sleep["sleep_onset"], errors="coerce")
    grid = grid_with_timestamp(args.grid_path)
    light = (grid.get("mlight_mean", 0.0).fillna(0.0) + grid.get("wlight_mean", 0.0).fillna(0.0)).astype(float)
    positive_light = light[light > 0]
    bright_thr = float(positive_light.quantile(0.75)) if len(positive_light) else 1.0
    dark_thr = float(positive_light.quantile(0.25)) if len(positive_light) else 0.0

    merged = rows.merge(sleep[["subject_id", "sleep_date", "sleep_onset"]], on=["subject_id", "sleep_date"], how="left", validate="many_to_one")
    grid_by_subject = {subject: group for subject, group in grid.groupby("subject_id")}
    out_rows = []
    for _, row in merged.iterrows():
        subject = str(row["subject_id"])
        out = {"subject_id": subject, "sleep_date": row["sleep_date"], "lifelog_date": row["lifelog_date"]}
        onset = row.get("sleep_onset")
        if pd.notna(onset) and subject in grid_by_subject:
            subject_grid = grid_by_subject[subject]
            day_grid = subject_grid[
                (subject_grid["timestamp"] >= onset - pd.Timedelta(hours=7))
                & (subject_grid["timestamp"] < onset + pd.Timedelta(hours=2))
            ]
            out.update(summarize_onset_transition(day_grid, onset, bright_thr, dark_thr))
            out["z_sot_onset_hour"] = float(onset.hour + onset.minute / 60.0)
        out_rows.append(out)

    features = pd.DataFrame(out_rows).fillna(0.0).replace([np.inf, -np.inf], 0.0)
    base_cols = [c for c in features.columns if c.startswith("z_sot_") and pd.api.types.is_numeric_dtype(features[c])]
    core_patterns = [
        "latency",
        "recency",
        "shutdown",
        "rise",
        "decay",
        "fragmentation",
        "conflict",
        "readiness",
        "cleanliness",
        "disruption",
        "settled",
    ]
    core_cols = [c for c in base_cols if any(p in c for p in core_patterns)]
    features = add_subject_stats(features, core_cols)
    roll_cols = [
        c
        for c in [
            "z_sot_onset_readiness_score",
            "z_sot_transition_cleanliness_score",
            "z_sot_onset_disruption_score",
            "z_sot_last_phone_latency_min",
            "z_sot_last_moving_latency_min",
            "z_sot_last_bright_latency_min",
            "z_sot_fragmentation_pressure",
            "z_sot_last_hour_conflict_pressure",
        ]
        if c in features
    ]
    features = add_rolling(features, roll_cols)
    keep_cols = KEY_COLUMNS + sorted([c for c in features.columns if c.startswith("z_sot_") and pd.api.types.is_numeric_dtype(features[c])])
    return features[keep_cols].sort_values(KEY_COLUMNS).fillna(0.0).replace([np.inf, -np.inf], 0.0)


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
    stats = pd.DataFrame(
        {
            "feature": feature_cols,
            "mean": [float(features[c].mean()) for c in feature_cols],
            "std": [float(features[c].std()) for c in feature_cols],
        }
    )
    report = {
        "output": str(output),
        "rows": int(len(features)),
        "feature_count": int(len(feature_cols)),
        "hypothesis": "S3 may depend on the sleep-onset transition curve: last digital/movement/light events, shutdown slope, settling consensus, and pre-onset fragmentation.",
    }
    output.with_suffix(".report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    md = [
        "# Sleep Onset Transition Latents",
        "",
        "## Purpose",
        "",
        "Encode the six hours before sleep onset as a behavioral transition: last phone/movement/bright-light events, shutdown slope, fragmentation, and readiness to settle.",
        "",
        f"- Output: `{output}`",
        f"- Rows: `{len(features)}`",
        f"- Feature count: `{len(feature_cols)}`",
        "",
        "## Feature Summary",
        "",
        dataframe_to_markdown(stats.head(80)),
    ]
    output.with_suffix(".report.md").write_text("\n".join(md), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build sleep-onset transition latent features.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--grid-path", default="artifacts/multires_30min_event_hybrid_grid.parquet")
    parser.add_argument("--sleep-summary", default="artifacts/07_sleep_summary.parquet")
    parser.add_argument("--output", default="artifacts/domain_sleep_onset_transition_v1.parquet")
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
