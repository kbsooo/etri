from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


KEY_COLUMNS = ["subject_id", "lifelog_date"]
ROLL_WINDOWS = [3, 7, 14, 28]


def normalize_rows(path: str) -> pd.DataFrame:
    frame = pd.read_csv(path).copy()
    frame["subject_id"] = frame["subject_id"].astype(str)
    frame["lifelog_date"] = pd.to_datetime(frame["lifelog_date"]).dt.strftime("%Y-%m-%d")
    return frame[KEY_COLUMNS]


def load_rows(train_path: str, sample_path: str) -> pd.DataFrame:
    return pd.concat([normalize_rows(train_path), normalize_rows(sample_path)], ignore_index=True).drop_duplicates()


def safe_div(numer: pd.Series | np.ndarray | float, denom: pd.Series | np.ndarray | float) -> np.ndarray:
    return (pd.Series(numer, copy=False).astype(float) / (pd.Series(denom, copy=False).astype(float) + 1e-6)).to_numpy()


def robust_mean(frame: pd.DataFrame, cols: list[str]) -> pd.Series:
    present = [c for c in cols if c in frame]
    if not present:
        return pd.Series(0.0, index=frame.index)
    x = frame[present].apply(pd.to_numeric, errors="coerce").fillna(0.0)
    scaled = {}
    for col in present:
        values = x[col]
        med = float(values.median())
        iqr = float(values.quantile(0.75) - values.quantile(0.25))
        scale = max(iqr / 1.349, float(values.std()) / 1.4826, 1.0)
        scaled[col] = ((values - med) / scale).clip(-10.0, 10.0)
    return pd.DataFrame(scaled, index=frame.index).mean(axis=1)


def circadian_shift(hour: pd.Series, center: pd.Series) -> pd.Series:
    return ((hour.astype(float) - center.astype(float) + 12.0) % 24.0) - 12.0


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
    state = pd.read_parquet(args.state_features).copy()
    state["subject_id"] = state["subject_id"].astype(str)
    state["lifelog_date"] = pd.to_datetime(state["lifelog_date"]).dt.strftime("%Y-%m-%d")
    features = rows.merge(state, on=KEY_COLUMNS, how="left", validate="one_to_one")

    if args.digital_isolation:
        di = pd.read_parquet(args.digital_isolation).copy()
        di["subject_id"] = di["subject_id"].astype(str)
        di["lifelog_date"] = pd.to_datetime(di["lifelog_date"]).dt.strftime("%Y-%m-%d")
        features = features.merge(di, on=KEY_COLUMNS, how="left", validate="one_to_one")

    numeric_cols = [c for c in features.columns if c not in KEY_COLUMNS and pd.api.types.is_numeric_dtype(features[c])]
    features[numeric_cols] = features[numeric_cols].fillna(0.0).replace([np.inf, -np.inf], 0.0)

    out = features[KEY_COLUMNS].copy()
    out["z_cc_physical_load"] = robust_mean(
        features,
        [
            "day_step_sum",
            "day_gps_speed_mean",
            "day_gps_speed_max",
            "day_hr_mean",
            "day_hr_std",
            "ep_step_sum_sum",
            "ep_gps_speed_mean_mean",
            "ep_ev_moving_sum",
            "dev_day_step_sum",
            "rz_day_step_sum",
            "dev_day_gps_speed_mean",
            "rz_day_gps_speed_mean",
        ],
    )
    out["z_cc_mobility_context_switch"] = robust_mean(
        features,
        [
            "gps_elsewhere_ratio",
            "ep_gps_lat_std_mean",
            "ep_gps_lon_std_mean",
            "ep_gps_speed_max_std",
            "ep_ev_moving_start_sum",
            "ep_ev_moving_end_sum",
            "ep_move_phone_silent_ratio",
            "ds_mobility_phone_gap",
        ],
    )
    out["z_cc_evening_arousal"] = robust_mean(
        features,
        [
            "z_evening_screen_on_ratio",
            "z_lateNight_screen_on_ratio",
            "z_evening_step_sum",
            "z_lateNight_step_sum",
            "z_evening_hr_mean",
            "z_lateNight_hr_mean",
            "ds_evening_screen_share",
            "ds_night_screen_share",
            "ds_prebed_phone_total",
            "ep_night_ev_phone_active_ratio",
            "z_di_evening_phone_ratio",
            "z_di_night_phone_ratio",
            "z_di_evening_usage_share",
            "z_di_night_usage_share",
            "z_di_prebed_passive_over_social",
        ],
    )
    out["z_cc_sleep_opportunity"] = robust_mean(
        features,
        [
            "tst_min",
            "sleep_eff",
            "longest_block_min",
            "gps_home_ratio",
            "ep_ev_no_wear_longest_run",
            "ep_ev_low_coverage_longest_run",
        ],
    )
    out["z_cc_sleep_friction"] = robust_mean(
        features,
        [
            "sol_proxy_min",
            "n_awakenings",
            "n_awakenings_long",
            "z_night_screen_on_ratio",
            "z_night_step_sum",
            "ep_night_ev_phone_active_ratio",
            "ep_ev_phone_active_longest_run",
            "z_di_short_check_ratio",
            "z_di_phone_burstiness",
        ],
    )
    out["z_cc_continuity_loss"] = robust_mean(
        features,
        [
            "n_awakenings",
            "n_awakenings_long",
            "sol_proxy_min",
            "ep_ev_phone_active_start_sum",
            "ep_ev_social_audio_start_sum",
            "ep_ev_low_coverage_start_sum",
            "ep_ev_no_wear_start_sum",
            "z_di_phone_start_count",
            "z_di_screen_without_usage_ratio",
        ],
    )
    out["z_cc_morning_recovery"] = robust_mean(
        features,
        [
            "z_earlyAM_step_sum",
            "z_AM_step_sum",
            "z_earlyAM_hr_mean",
            "z_AM_hr_mean",
            "z_earlyAM_screen_on_ratio",
            "z_AM_screen_on_ratio",
            "ep_ev_phone_active_first_tok",
            "ep_ev_moving_first_tok",
        ],
    )
    out["z_cc_recovery_deficit"] = out["z_cc_physical_load"] + out["z_cc_sleep_friction"] - out["z_cc_morning_recovery"]
    out["z_cc_arousal_without_load"] = out["z_cc_evening_arousal"] - out["z_cc_physical_load"].clip(lower=0.0)
    out["z_cc_load_after_bad_sleep"] = out["z_cc_physical_load"] * out["z_cc_sleep_friction"].clip(lower=0.0)
    out["z_cc_high_load_low_opportunity"] = out["z_cc_physical_load"] - out["z_cc_sleep_opportunity"]
    out["z_cc_arousal_to_opportunity_gap"] = out["z_cc_evening_arousal"] - out["z_cc_sleep_opportunity"]
    out["z_cc_fragmented_recovery_gap"] = out["z_cc_continuity_loss"] - out["z_cc_morning_recovery"]
    out["z_cc_stress_chain_score"] = (
        out["z_cc_mobility_context_switch"]
        + out["z_cc_evening_arousal"]
        + out["z_cc_sleep_friction"]
        - out["z_cc_morning_recovery"]
    )
    out["z_cc_sleep_quality_chain_score"] = (
        out["z_cc_sleep_opportunity"]
        - out["z_cc_sleep_friction"]
        - out["z_cc_continuity_loss"]
        - 0.5 * out["z_cc_evening_arousal"].clip(lower=0.0)
    )
    out["z_cc_fatigue_chain_score"] = (
        out["z_cc_physical_load"]
        + out["z_cc_mobility_context_switch"]
        + out["z_cc_continuity_loss"]
        - out["z_cc_morning_recovery"]
    )

    if {"sleep_onset", "wake_time"}.issubset(features.columns):
        onset = pd.to_datetime(features["sleep_onset"], errors="coerce")
        wake = pd.to_datetime(features["wake_time"], errors="coerce")
        onset_hour = (onset.dt.hour + onset.dt.minute / 60.0).fillna(0.0)
        wake_hour = (wake.dt.hour + wake.dt.minute / 60.0).fillna(0.0)
        onset_center = onset_hour.groupby(features["subject_id"]).transform("median")
        wake_center = wake_hour.groupby(features["subject_id"]).transform("median")
        out["z_cc_onset_late_shift"] = circadian_shift(onset_hour, onset_center).clip(-12.0, 12.0)
        out["z_cc_wake_late_shift"] = circadian_shift(wake_hour, wake_center).clip(-12.0, 12.0)
        out["z_cc_phase_compression"] = out["z_cc_onset_late_shift"] - out["z_cc_wake_late_shift"]
        out["z_cc_late_arousal_chain"] = out["z_cc_onset_late_shift"].clip(lower=0.0) + out["z_cc_evening_arousal"]

    base_cols = [c for c in out.columns if c.startswith("z_cc_")]
    out = add_subject_stats(out, base_cols)
    roll_cols = [
        c
        for c in [
            "z_cc_physical_load",
            "z_cc_mobility_context_switch",
            "z_cc_evening_arousal",
            "z_cc_sleep_opportunity",
            "z_cc_sleep_friction",
            "z_cc_continuity_loss",
            "z_cc_morning_recovery",
            "z_cc_recovery_deficit",
            "z_cc_stress_chain_score",
            "z_cc_sleep_quality_chain_score",
            "z_cc_fatigue_chain_score",
        ]
        if c in out
    ]
    out = add_rolling(out, roll_cols)
    keep_cols = KEY_COLUMNS + sorted([c for c in out.columns if c.startswith("z_cc_")])
    return out[keep_cols].sort_values(KEY_COLUMNS).fillna(0.0).replace([np.inf, -np.inf], 0.0)


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
        "hypotheses": [
            "A day should be represented as load -> arousal -> sleep opportunity -> continuity -> recovery.",
            "S1/S3 may depend on chain bottlenecks rather than any single sensor family.",
            "Subject-relative chain gaps can expose fatigue/stress states without label-derived targets.",
        ],
    }
    output.with_suffix(".report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    md = [
        "# Causal Chain Latents",
        "",
        "## Purpose",
        "",
        "Encode a subject-day as a causal sketch: physical/mobility load, evening arousal, sleep opportunity, continuity loss, and morning recovery.",
        "",
        f"- Output: `{output}`",
        f"- Rows: `{len(features)}`",
        f"- Feature count: `{len(feature_cols)}`",
        "",
        "## Feature Summary",
        "",
        dataframe_to_markdown(stats.head(60)),
    ]
    output.with_suffix(".report.md").write_text("\n".join(md), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build load-arousal-sleep-recovery causal chain features.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--state-features", default="artifacts/domain_state_features_v1.parquet")
    parser.add_argument("--digital-isolation", default="artifacts/domain_digital_isolation_v1.parquet")
    parser.add_argument("--output", default="artifacts/domain_causal_chain_v1.parquet")
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
