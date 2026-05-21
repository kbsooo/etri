from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


KEY_COLUMNS = ["subject_id", "lifelog_date"]
DIGITAL_KEYWORDS = [
    "phone",
    "screen",
    "usage",
    "app_",
    "charging",
    "prebed",
    "messenger",
    "sns",
    "video",
    "game",
    "music",
    "browser",
    "call",
]
APP_CATEGORIES = [
    "browser",
    "call",
    "camera",
    "finance",
    "game",
    "health",
    "messenger",
    "music",
    "navigation",
    "news",
    "os_launcher",
    "other",
    "productivity",
    "reading",
    "religion",
    "shopping",
    "sns",
    "video",
]
SOCIAL_APPS = ["messenger", "sns", "call"]
STIM_APPS = ["video", "game", "sns", "music", "news"]
UTIL_APPS = ["finance", "navigation", "productivity", "reading", "health"]


def safe_div(numer: pd.Series, denom: pd.Series | float) -> pd.Series:
    return numer.astype(float) / (pd.Series(denom, index=numer.index).astype(float) + 1e-6)


def entropy_from_cols(frame: pd.DataFrame, cols: list[str]) -> pd.Series:
    x = frame[cols].fillna(0.0).clip(lower=0.0)
    total = x.sum(axis=1) + 1e-12
    p = x.div(total, axis=0)
    return -(p * np.log(p + 1e-12)).sum(axis=1)


def normalize_rows(path: str) -> pd.DataFrame:
    frame = pd.read_csv(path).copy()
    frame["subject_id"] = frame["subject_id"].astype(str)
    frame["sleep_date"] = pd.to_datetime(frame["sleep_date"]).dt.strftime("%Y-%m-%d")
    frame["lifelog_date"] = pd.to_datetime(frame["lifelog_date"]).dt.strftime("%Y-%m-%d")
    return frame[["subject_id", "sleep_date", "lifelog_date"]]


def add_subject_stats(frame: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    additions = {}
    for col in cols:
        center = frame.groupby("subject_id")[col].transform("median")
        mad = frame.groupby("subject_id")[col].transform(lambda s: np.nanmedian(np.abs(s - np.nanmedian(s))) + 1e-6)
        additions[f"z_ds_{col}_subdev"] = frame[col] - center
        additions[f"z_ds_{col}_subrz"] = (frame[col] - center) / mad
    return pd.concat([frame, pd.DataFrame(additions, index=frame.index)], axis=1)


def add_roll_stats(frame: pd.DataFrame, cols: list[str], windows: list[int]) -> pd.DataFrame:
    frame = frame.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True)
    additions = {}
    for window in windows:
        for col in cols:
            shifted = frame.groupby("subject_id")[col].shift(1)
            roll = shifted.groupby(frame["subject_id"]).rolling(window, min_periods=2).mean().reset_index(level=0, drop=True)
            additions[f"z_ds_{col}_past{window}_delta"] = (frame[col] - roll).fillna(0.0)
            additions[f"z_ds_{col}_past{window}_ratio"] = safe_div(frame[col], roll.fillna(0.0)).replace([np.inf, -np.inf], 0.0)
    return pd.concat([frame, pd.DataFrame(additions, index=frame.index)], axis=1)


def build_features(args: argparse.Namespace) -> pd.DataFrame:
    rows = pd.concat([normalize_rows(args.train_path), normalize_rows(args.sample_path)], ignore_index=True).drop_duplicates()
    state = pd.read_parquet(args.state_features).copy()
    state["subject_id"] = state["subject_id"].astype(str)
    state["lifelog_date"] = pd.to_datetime(state["lifelog_date"]).dt.strftime("%Y-%m-%d")
    digital_cols = [
        c
        for c in state.columns
        if c not in KEY_COLUMNS
        and any(key in c.lower() for key in DIGITAL_KEYWORDS)
        and pd.api.types.is_numeric_dtype(state[c])
    ]
    features = rows[KEY_COLUMNS].merge(state[KEY_COLUMNS + digital_cols], on=KEY_COLUMNS, how="left")

    app_daily = pd.read_parquet(args.app_daily).copy()
    app_daily["subject_id"] = app_daily["subject_id"].astype(str)
    app_daily["lifelog_date"] = pd.to_datetime(app_daily["date"]).dt.strftime("%Y-%m-%d")
    app_daily_cols = [f"app_{cat}_sec" for cat in APP_CATEGORIES if f"app_{cat}_sec" in app_daily]
    features = features.merge(app_daily[KEY_COLUMNS + app_daily_cols], on=KEY_COLUMNS, how="left", suffixes=("", "_dailyraw"))

    app_prebed = pd.read_parquet(args.app_prebed).copy()
    app_prebed["subject_id"] = app_prebed["subject_id"].astype(str)
    app_prebed["sleep_date"] = pd.to_datetime(app_prebed["sleep_date"]).dt.strftime("%Y-%m-%d")
    prebed_cols = [f"prebed_{cat}_sec" for cat in APP_CATEGORIES if f"prebed_{cat}_sec" in app_prebed]
    features = features.merge(rows[["subject_id", "sleep_date", "lifelog_date"]], on=KEY_COLUMNS, how="left")
    features = features.merge(app_prebed[["subject_id", "sleep_date"] + prebed_cols], on=["subject_id", "sleep_date"], how="left")
    features = features.drop(columns=["sleep_date"])
    features = features.fillna(0.0)

    additions = {}
    app_cols = [c for c in features.columns if c.startswith("app_") and c.endswith("_sec")]
    pre_cols = [c for c in features.columns if c.startswith("prebed_") and c.endswith("_sec")]
    additions["z_ds_app_total_sec_raw"] = features[app_cols].sum(axis=1) if app_cols else 0.0
    additions["z_ds_prebed_total_sec_raw"] = features[pre_cols].sum(axis=1) if pre_cols else 0.0
    additions["z_ds_app_entropy_raw"] = entropy_from_cols(features, app_cols) if app_cols else 0.0
    additions["z_ds_prebed_entropy_raw"] = entropy_from_cols(features, pre_cols) if pre_cols else 0.0
    for label, cats in [("social", SOCIAL_APPS), ("stim", STIM_APPS), ("util", UTIL_APPS)]:
        daily = [f"app_{cat}_sec" for cat in cats if f"app_{cat}_sec" in features]
        pre = [f"prebed_{cat}_sec" for cat in cats if f"prebed_{cat}_sec" in features]
        additions[f"z_ds_app_{label}_sec"] = features[daily].sum(axis=1) if daily else 0.0
        additions[f"z_ds_prebed_{label}_sec"] = features[pre].sum(axis=1) if pre else 0.0
    additions_frame = pd.DataFrame(additions, index=features.index)
    features = pd.concat([features, additions_frame], axis=1)
    features["z_ds_prebed_share_raw"] = safe_div(features["z_ds_prebed_total_sec_raw"], features["z_ds_app_total_sec_raw"])
    features["z_ds_prebed_stim_share"] = safe_div(features["z_ds_prebed_stim_sec"], features["z_ds_prebed_total_sec_raw"])
    features["z_ds_prebed_social_share"] = safe_div(features["z_ds_prebed_social_sec"], features["z_ds_prebed_total_sec_raw"])
    features["z_ds_day_stim_share"] = safe_div(features["z_ds_app_stim_sec"], features["z_ds_app_total_sec_raw"])
    features["z_ds_day_social_share"] = safe_div(features["z_ds_app_social_sec"], features["z_ds_app_total_sec_raw"])

    pressure_cols = [
        c
        for c in [
            "day_screen_on_ratio",
            "z_evening_screen_on_ratio",
            "z_lateNight_screen_on_ratio",
            "ds_night_screen_share",
            "ds_evening_screen_share",
            "ds_prebed_phone_total",
            "ep_ev_phone_active_ratio",
            "ep_night_ev_phone_active_ratio",
            "z_ds_prebed_total_sec_raw",
            "z_ds_prebed_stim_share",
            "z_ds_prebed_social_share",
        ]
        if c in features
    ]
    features["z_ds_digital_sleep_pressure"] = features[pressure_cols].rank(pct=True).mean(axis=1) if pressure_cols else 0.0
    features["z_ds_late_phone_minus_day_phone"] = features.get("z_lateNight_screen_on_ratio", 0.0) - features.get("day_screen_on_ratio", 0.0)
    features["z_ds_evening_phone_minus_day_phone"] = features.get("z_evening_screen_on_ratio", 0.0) - features.get("day_screen_on_ratio", 0.0)

    core_cols = [
        c
        for c in features.columns
        if c not in KEY_COLUMNS
        and pd.api.types.is_numeric_dtype(features[c])
        and (
            c.startswith("z_ds_")
            or c.startswith("dev_")
            or c.startswith("rz_")
            or any(key in c.lower() for key in DIGITAL_KEYWORDS)
        )
    ]
    features = add_subject_stats(features, [c for c in core_cols if c.startswith("z_ds_")][:24])
    features = add_roll_stats(features, [c for c in core_cols if c.startswith("z_ds_")][:16], [3, 7, 14])
    keep_cols = KEY_COLUMNS + sorted([c for c in features.columns if c not in KEY_COLUMNS and pd.api.types.is_numeric_dtype(features[c])])
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
        "hypothesis": "digital phone/screen/app usage is a primary sleep-label predictor",
    }
    output.with_suffix(".report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    md = [
        "# Digital Sleep Latents",
        "",
        "## Purpose",
        "",
        "Isolate smartphone/screen/app/prebed usage as a first-class sleep decoder feature family instead of mixing it into generic behavior features.",
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
    parser = argparse.ArgumentParser(description="Build phone/screen/app-centric sleep feature latents.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--state-features", default="artifacts/domain_state_features_v1.parquet")
    parser.add_argument("--app-daily", default="artifacts/09_app_categories_daily.parquet")
    parser.add_argument("--app-prebed", default="artifacts/09_app_prebed_categories.parquet")
    parser.add_argument("--output", default="artifacts/domain_digital_sleep_v1.parquet")
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
