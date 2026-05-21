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


def with_lifelog_date(frame: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
    out = frame.copy()
    out["subject_id"] = out["subject_id"].astype(str)
    out["lifelog_date"] = pd.to_datetime(out[date_col]).dt.strftime("%Y-%m-%d")
    return out.drop(columns=[date_col])


def entropy_cols(frame: pd.DataFrame, cols: list[str]) -> pd.Series:
    x = frame[cols].fillna(0.0).clip(lower=0.0)
    total = x.sum(axis=1) + 1e-12
    p = x.div(total, axis=0)
    return -(p * np.log(p + 1e-12)).sum(axis=1)


def add_subject_deviation(frame: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    additions = {}
    for col in cols:
        center = frame.groupby("subject_id")[col].transform("median")
        mad = frame.groupby("subject_id")[col].transform(lambda s: np.nanmedian(np.abs(s - np.nanmedian(s))) + 1e-6)
        additions[f"z_mc_{col}_subdev"] = frame[col] - center
        additions[f"z_mc_{col}_subrz"] = (frame[col] - center) / mad
        rank = frame.groupby("subject_id")[col].rank(pct=True)
        additions[f"z_mc_{col}_subpct"] = rank.fillna(0.5)
    return pd.concat([frame, pd.DataFrame(additions, index=frame.index)], axis=1)


def add_rolling(frame: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    frame = frame.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True)
    additions = {}
    for window in ROLL_WINDOWS:
        for col in cols:
            shifted = frame.groupby("subject_id")[col].shift(1)
            roll = shifted.groupby(frame["subject_id"]).rolling(window, min_periods=2).mean().reset_index(level=0, drop=True)
            roll_std = shifted.groupby(frame["subject_id"]).rolling(window, min_periods=2).std().reset_index(level=0, drop=True)
            additions[f"z_mc_{col}_past{window}_delta"] = (frame[col] - roll).fillna(0.0)
            additions[f"z_mc_{col}_past{window}_abs_delta"] = (frame[col] - roll).abs().fillna(0.0)
            additions[f"z_mc_{col}_past{window}_volatility"] = roll_std.fillna(0.0)
    return pd.concat([frame, pd.DataFrame(additions, index=frame.index)], axis=1)


def build_features(args: argparse.Namespace) -> pd.DataFrame:
    rows = pd.concat([normalize_rows(args.train_path), normalize_rows(args.sample_path)], ignore_index=True).drop_duplicates()
    places = with_lifelog_date(pd.read_parquet(args.place_durations))
    novelty = with_lifelog_date(pd.read_parquet(args.daily_novelty))
    mobility = with_lifelog_date(pd.read_parquet(args.mobility_daily))
    state = pd.read_parquet(args.state_features).copy()
    state["subject_id"] = state["subject_id"].astype(str)
    state["lifelog_date"] = pd.to_datetime(state["lifelog_date"]).dt.strftime("%Y-%m-%d")
    state_cols = [
        c
        for c in [
            "day_step_sum",
            "day_gps_speed_mean",
            "day_gps_speed_max",
            "day_gps_lat_std",
            "day_gps_lon_std",
            "z_night_gps_speed_mean",
            "z_evening_gps_speed_mean",
            "z_lateNight_gps_speed_mean",
            "ds_place_entropy",
            "ds_mobility_phone_gap",
            "ep_ev_moving_ratio",
            "ep_ev_moving_first_tok",
            "ep_ev_moving_last_tok",
            "ep_ev_moving_longest_run",
            "ep_move_phone_silent_ratio",
            "ep_phone_move_agreement",
        ]
        if c in state
    ]
    features = rows.merge(places, on=KEY_COLUMNS, how="left")
    features = features.merge(novelty, on=KEY_COLUMNS, how="left", suffixes=("", "_novelty"))
    features = features.merge(mobility, on=KEY_COLUMNS, how="left")
    features = features.merge(state[KEY_COLUMNS + state_cols], on=KEY_COLUMNS, how="left")
    features = features.fillna(0.0)

    place_cols = [c for c in ["home", "work_or_school", "other", "elsewhere"] if c in features]
    features["z_mc_place_entropy"] = entropy_cols(features, place_cols) if place_cols else 0.0
    total_place = features[place_cols].sum(axis=1) + 1e-6 if place_cols else 1.0
    features["z_mc_home_share"] = features.get("home", 0.0) / total_place
    features["z_mc_elsewhere_share"] = features.get("elsewhere", 0.0) / total_place
    features["z_mc_work_share"] = features.get("work_or_school", 0.0) / total_place
    features["z_mc_out_of_home_min"] = features.get("elsewhere", 0.0) + features.get("work_or_school", 0.0) + features.get("other", 0.0)
    features["z_mc_constriction_raw"] = features["z_mc_home_share"] - features["z_mc_elsewhere_share"]
    features["z_mc_passive_mobility"] = features.get("mob_vehicle_min", 0.0) + features.get("mob_transit_hispeed_min", 0.0)
    features["z_mc_active_mobility"] = features.get("mob_walk_min", 0.0) + features.get("mob_bike_or_jog_min", 0.0)
    features["z_mc_passive_active_ratio"] = features["z_mc_passive_mobility"] / (features["z_mc_active_mobility"] + 1e-6)
    features["z_mc_stationary_home_load"] = features.get("mob_stationary_min", 0.0) * features["z_mc_home_share"]
    features["z_mc_novel_location_load"] = features.get("wifi_novelty_ratio", 0.0) + features.get("ble_novelty_ratio", 0.0) + features.get("gps_elsewhere_ratio", 0.0)
    features["z_mc_location_var_proxy"] = features.get("day_gps_lat_std", 0.0).abs() + features.get("day_gps_lon_std", 0.0).abs()
    features["z_mc_evening_mobility_pressure"] = features.get("z_evening_gps_speed_mean", 0.0) + features.get("z_lateNight_gps_speed_mean", 0.0)

    numeric_cols = [c for c in features.columns if c not in KEY_COLUMNS and pd.api.types.is_numeric_dtype(features[c])]
    core = [
        c
        for c in numeric_cols
        if c.startswith("z_mc_")
        or c in [
            "minutes_moving",
            "gps_stationary_min",
            "gps_elsewhere_ratio",
            "gps_home_ratio",
            "wifi_novelty_ratio",
            "ble_novelty_ratio",
            "outings",
            "mob_stationary_min",
            "mob_walk_min",
            "mob_vehicle_min",
            "day_step_sum",
            "day_gps_speed_mean",
            "day_gps_speed_max",
        ]
    ]
    features = add_subject_deviation(features, core)
    roll_cols = [
        c
        for c in [
            "z_mc_home_share",
            "z_mc_out_of_home_min",
            "z_mc_constriction_raw",
            "z_mc_place_entropy",
            "z_mc_novel_location_load",
            "z_mc_passive_active_ratio",
            "z_mc_stationary_home_load",
            "minutes_moving",
            "outings",
            "day_step_sum",
        ]
        if c in features
    ]
    features = add_rolling(features, roll_cols)
    features["lifelog_dt"] = pd.to_datetime(features["lifelog_date"])
    features["weekday"] = features["lifelog_dt"].dt.weekday.astype(float)
    features["z_mc_weekend_home_interaction"] = features["weekday"].isin([5, 6]).astype(float) * features["z_mc_home_share"]

    keep_cols = KEY_COLUMNS + sorted([c for c in features.columns if c.startswith("z_mc_") or c in ["weekday"]])
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
    report = {"output": str(output), "rows": int(len(features)), "feature_count": int(len(feature_cols))}
    output.with_suffix(".report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    md = [
        "# Mobility Constriction Latents",
        "",
        "## Purpose",
        "",
        "Encode home-stay deviation, location entropy, novelty, passive/active mobility balance, and constrained-day markers.",
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
    parser = argparse.ArgumentParser(description="Build mobility constriction and location novelty latent features.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--place-durations", default="artifacts/06_daily_place_durations.parquet")
    parser.add_argument("--daily-novelty", default="artifacts/06_daily_novelty.parquet")
    parser.add_argument("--mobility-daily", default="artifacts/09_mobility_daily.parquet")
    parser.add_argument("--state-features", default="artifacts/domain_state_features_v1.parquet")
    parser.add_argument("--output", default="artifacts/domain_mobility_constriction_v1.parquet")
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
