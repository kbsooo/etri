from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


KEY_COLUMNS = ["subject_id", "lifelog_date"]
TARGET_KEYS = ["subject_id", "sleep_date", "lifelog_date"]
ROLL_WINDOWS = [3, 7, 14, 28]
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


def safe_div(numer: pd.Series | np.ndarray | float, denom: pd.Series | np.ndarray | float) -> pd.Series:
    return pd.Series(numer).astype(float) / (pd.Series(denom).astype(float) + 1e-6)


def entropy_from_cols(frame: pd.DataFrame, cols: list[str]) -> pd.Series:
    if not cols:
        return pd.Series(0.0, index=frame.index)
    x = frame[cols].fillna(0.0).clip(lower=0.0)
    total = x.sum(axis=1) + 1e-12
    p = x.div(total, axis=0)
    return -(p * np.log(p + 1e-12)).sum(axis=1)


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


def first_true_minutes(part: pd.DataFrame, mask: np.ndarray, anchor: pd.Timestamp) -> float:
    if len(part) == 0 or not mask.any():
        return 999.0
    return float((part.loc[mask, "timestamp"].iloc[0] - anchor).total_seconds() / 60.0)


def last_true_minutes(part: pd.DataFrame, mask: np.ndarray, anchor: pd.Timestamp) -> float:
    if len(part) == 0 or not mask.any():
        return 999.0
    return float((anchor - part.loc[mask, "timestamp"].iloc[-1]).total_seconds() / 60.0)


def count_starts(values: np.ndarray) -> int:
    flags = values.astype(bool)
    if len(flags) == 0:
        return 0
    shifted = np.r_[False, flags[:-1]]
    return int((flags & ~shifted).sum())


def summarize_boundary_windows(day_grid: pd.DataFrame, onset: pd.Timestamp, wake: pd.Timestamp) -> dict[str, float]:
    out: dict[str, float] = {}
    windows = {
        "prebed1h": (onset - pd.Timedelta(hours=1), onset),
        "prebed2h": (onset - pd.Timedelta(hours=2), onset),
        "prebed4h": (onset - pd.Timedelta(hours=4), onset),
        "sleep": (onset, wake),
        "postwake1h": (wake, wake + pd.Timedelta(hours=1)),
        "postwake2h": (wake, wake + pd.Timedelta(hours=2)),
    }
    for name, (start, end) in windows.items():
        part = day_grid[(day_grid["timestamp"] >= start) & (day_grid["timestamp"] < end)].copy()
        phone = np.nan_to_num(part.get("ev_phone_active", pd.Series(dtype=float)).to_numpy(float), nan=0.0) > 0.5
        moving = np.nan_to_num(part.get("ev_moving", pd.Series(dtype=float)).to_numpy(float), nan=0.0) > 0.5
        charging = np.nan_to_num(part.get("ev_charging_on", pd.Series(dtype=float)).to_numpy(float), nan=0.0) > 0.5
        low_cov = np.nan_to_num(part.get("ev_low_coverage", pd.Series(dtype=float)).to_numpy(float), nan=0.0) > 0.5
        no_wear = np.nan_to_num(part.get("ev_no_wear", pd.Series(dtype=float)).to_numpy(float), nan=0.0) > 0.5
        usage = np.nan_to_num(part.get("usage_total", pd.Series(dtype=float)).to_numpy(float), nan=0.0)
        screen = np.nan_to_num(part.get("screen_mean", pd.Series(dtype=float)).to_numpy(float), nan=0.0)
        steps = np.nan_to_num(part.get("step_sum", pd.Series(dtype=float)).to_numpy(float), nan=0.0)
        out[f"z_db_{name}_tok_n"] = float(len(part))
        out[f"z_db_{name}_phone_ratio"] = float(phone.mean()) if len(phone) else 0.0
        out[f"z_db_{name}_phone_starts"] = float(count_starts(phone))
        out[f"z_db_{name}_phone_longest_run"] = float(longest_run(phone))
        out[f"z_db_{name}_usage_total"] = float(usage.sum())
        out[f"z_db_{name}_screen_mean"] = float(screen.mean()) if len(screen) else 0.0
        out[f"z_db_{name}_phone_still_ratio"] = float((phone & ~moving).mean()) if len(phone) else 0.0
        out[f"z_db_{name}_phone_move_ratio"] = float((phone & moving).mean()) if len(phone) else 0.0
        out[f"z_db_{name}_charging_ratio"] = float(charging.mean()) if len(charging) else 0.0
        out[f"z_db_{name}_lowcov_or_nowear_ratio"] = float((low_cov | no_wear).mean()) if len(low_cov) else 0.0
        out[f"z_db_{name}_step_sum"] = float(steps.sum())
    pre = day_grid[(day_grid["timestamp"] >= onset - pd.Timedelta(hours=6)) & (day_grid["timestamp"] < onset)].copy()
    post = day_grid[(day_grid["timestamp"] >= wake) & (day_grid["timestamp"] < wake + pd.Timedelta(hours=4))].copy()
    sleep = day_grid[(day_grid["timestamp"] >= onset) & (day_grid["timestamp"] < wake)].copy()
    pre_phone = np.nan_to_num(pre.get("ev_phone_active", pd.Series(dtype=float)).to_numpy(float), nan=0.0) > 0.5
    post_phone = np.nan_to_num(post.get("ev_phone_active", pd.Series(dtype=float)).to_numpy(float), nan=0.0) > 0.5
    post_move = np.nan_to_num(post.get("ev_moving", pd.Series(dtype=float)).to_numpy(float), nan=0.0) > 0.5
    sleep_phone = np.nan_to_num(sleep.get("ev_phone_active", pd.Series(dtype=float)).to_numpy(float), nan=0.0) > 0.5
    sleep_charging = np.nan_to_num(sleep.get("ev_charging_on", pd.Series(dtype=float)).to_numpy(float), nan=0.0) > 0.5
    out["z_db_last_phone_before_onset_min"] = last_true_minutes(pre, pre_phone, onset)
    out["z_db_first_phone_after_wake_min"] = first_true_minutes(post, post_phone, wake)
    out["z_db_first_move_after_wake_min"] = first_true_minutes(post, post_move, wake)
    out["z_db_phone_before_sleep_recency"] = 1.0 / (1.0 + out["z_db_last_phone_before_onset_min"])
    out["z_db_wake_phone_latency"] = out["z_db_first_phone_after_wake_min"]
    out["z_db_wake_move_latency"] = out["z_db_first_move_after_wake_min"]
    out["z_db_wake_phone_before_move_min"] = out["z_db_first_move_after_wake_min"] - out["z_db_first_phone_after_wake_min"]
    out["z_db_sleep_phone_bout_count"] = float(count_starts(sleep_phone))
    out["z_db_sleep_phone_longest_run"] = float(longest_run(sleep_phone))
    out["z_db_sleep_phone_while_charging_ratio"] = float((sleep_phone & sleep_charging).mean()) if len(sleep_phone) else 0.0
    out["z_db_sleep_phone_without_charging_ratio"] = float((sleep_phone & ~sleep_charging).mean()) if len(sleep_phone) else 0.0
    out["z_db_boundary_disruption_score"] = (
        out["z_db_prebed2h_phone_still_ratio"]
        + out["z_db_sleep_phone_without_charging_ratio"]
        + out["z_db_phone_before_sleep_recency"]
    )
    out["z_db_morning_sluggish_score"] = (
        np.log1p(max(out["z_db_first_move_after_wake_min"], 0.0))
        + out["z_db_postwake2h_phone_still_ratio"]
        - out["z_db_postwake2h_step_sum"] / 500.0
    )
    return out


def add_app_features(rows: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    out = rows.copy()
    daily = pd.read_parquet(args.app_daily).copy()
    daily["subject_id"] = daily["subject_id"].astype(str)
    daily["lifelog_date"] = pd.to_datetime(daily["date"]).dt.strftime("%Y-%m-%d")
    daily_cols = [f"app_{cat}_sec" for cat in APP_CATEGORIES if f"app_{cat}_sec" in daily]
    out = out.merge(daily[KEY_COLUMNS + daily_cols], on=KEY_COLUMNS, how="left")
    prebed = pd.read_parquet(args.app_prebed).copy()
    prebed["subject_id"] = prebed["subject_id"].astype(str)
    prebed["sleep_date"] = pd.to_datetime(prebed["sleep_date"]).dt.strftime("%Y-%m-%d")
    pre_cols = [f"prebed_{cat}_sec" for cat in APP_CATEGORIES if f"prebed_{cat}_sec" in prebed]
    out = out.merge(prebed[["subject_id", "sleep_date"] + pre_cols], on=["subject_id", "sleep_date"], how="left")
    out[daily_cols + pre_cols] = out[daily_cols + pre_cols].fillna(0.0)
    app_social = [f"app_{cat}_sec" for cat in SOCIAL_APPS if f"app_{cat}_sec" in out]
    app_stim = [f"app_{cat}_sec" for cat in STIM_APPS if f"app_{cat}_sec" in out]
    pre_social = [f"prebed_{cat}_sec" for cat in SOCIAL_APPS if f"prebed_{cat}_sec" in out]
    pre_stim = [f"prebed_{cat}_sec" for cat in STIM_APPS if f"prebed_{cat}_sec" in out]
    out["z_db_app_total_sec"] = out[daily_cols].sum(axis=1) if daily_cols else 0.0
    out["z_db_app_stim_sec"] = out[app_stim].sum(axis=1) if app_stim else 0.0
    out["z_db_app_social_sec"] = out[app_social].sum(axis=1) if app_social else 0.0
    out["z_db_prebed_total_sec"] = out[pre_cols].sum(axis=1) if pre_cols else 0.0
    out["z_db_prebed_stim_sec"] = out[pre_stim].sum(axis=1) if pre_stim else 0.0
    out["z_db_prebed_social_sec"] = out[pre_social].sum(axis=1) if pre_social else 0.0
    out["z_db_app_entropy"] = entropy_from_cols(out, daily_cols)
    out["z_db_prebed_entropy"] = entropy_from_cols(out, pre_cols)
    out["z_db_prebed_share"] = safe_div(out["z_db_prebed_total_sec"], out["z_db_app_total_sec"]).to_numpy()
    out["z_db_prebed_stim_share"] = safe_div(out["z_db_prebed_stim_sec"], out["z_db_prebed_total_sec"]).to_numpy()
    out["z_db_prebed_social_share"] = safe_div(out["z_db_prebed_social_sec"], out["z_db_prebed_total_sec"]).to_numpy()
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


def add_rolling(frame: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    frame = frame.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True)
    additions = {}
    for window in ROLL_WINDOWS:
        for col in cols:
            shifted = frame.groupby("subject_id")[col].shift(1)
            roll = shifted.groupby(frame["subject_id"]).rolling(window, min_periods=2).mean().reset_index(level=0, drop=True)
            additions[f"{col}_past{window}_delta"] = (frame[col] - roll).fillna(0.0)
            additions[f"{col}_past{window}_ratio"] = safe_div(frame[col], roll.fillna(0.0)).replace([np.inf, -np.inf], 0.0).to_numpy()
    return pd.concat([frame, pd.DataFrame(additions, index=frame.index)], axis=1)


def build_features(args: argparse.Namespace) -> pd.DataFrame:
    rows = load_rows(args.train_path, args.sample_path)
    grid = grid_with_timestamp(args.grid_path)
    sleep = pd.read_parquet(args.sleep_summary).copy()
    sleep["subject_id"] = sleep["subject_id"].astype(str)
    sleep["sleep_date"] = pd.to_datetime(sleep["sleep_date"]).dt.strftime("%Y-%m-%d")
    sleep["sleep_onset"] = pd.to_datetime(sleep["sleep_onset"])
    sleep["wake_time"] = pd.to_datetime(sleep["wake_time"])
    merged = rows.merge(sleep, on=["subject_id", "sleep_date"], how="left", validate="many_to_one")
    grid_by_subject = {subject: group for subject, group in grid.groupby("subject_id")}
    out_rows = []
    for _, row in merged.iterrows():
        subject = str(row["subject_id"])
        out = {"subject_id": subject, "sleep_date": row["sleep_date"], "lifelog_date": row["lifelog_date"]}
        onset = row.get("sleep_onset")
        wake = row.get("wake_time")
        if pd.notna(onset) and pd.notna(wake) and subject in grid_by_subject:
            subject_grid = grid_by_subject[subject]
            start = onset - pd.Timedelta(hours=8)
            end = wake + pd.Timedelta(hours=4)
            day_grid = subject_grid[(subject_grid["timestamp"] >= start) & (subject_grid["timestamp"] < end)]
            out.update(summarize_boundary_windows(day_grid, onset, wake))
            out["z_db_onset_hour"] = float(onset.hour + onset.minute / 60.0)
            out["z_db_wake_hour"] = float(wake.hour + wake.minute / 60.0)
            out["z_db_sleep_window_min"] = float((wake - onset).total_seconds() / 60.0)
        out_rows.append(out)
    features = pd.DataFrame(out_rows)
    features = add_app_features(features, args).fillna(0.0)
    base_cols = [
        c
        for c in features.columns
        if c.startswith("z_db_") and pd.api.types.is_numeric_dtype(features[c])
    ]
    core_cols = [
        c
        for c in base_cols
        if any(
            key in c
            for key in [
                "prebed",
                "sleep_phone",
                "wake",
                "boundary",
                "morning",
                "last_phone",
                "first_phone",
                "first_move",
                "app_",
            ]
        )
    ]
    features = add_subject_stats(features, core_cols)
    roll_cols = [
        c
        for c in [
            "z_db_boundary_disruption_score",
            "z_db_morning_sluggish_score",
            "z_db_last_phone_before_onset_min",
            "z_db_first_phone_after_wake_min",
            "z_db_wake_phone_before_move_min",
            "z_db_prebed_total_sec",
            "z_db_prebed_stim_sec",
            "z_db_sleep_phone_bout_count",
        ]
        if c in features
    ]
    features = add_rolling(features, roll_cols)
    keep_cols = KEY_COLUMNS + sorted(
        [c for c in features.columns if c.startswith("z_db_") and pd.api.types.is_numeric_dtype(features[c])]
    )
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
        "hypothesis": "sleep labels respond to smartphone timing around sleep and wake boundaries, not only total phone usage",
    }
    output.with_suffix(".report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    md = [
        "# Digital Boundary Latents",
        "",
        "## Purpose",
        "",
        "Encode phone/app behavior at sleep boundaries: last phone before sleep, phone intrusions during sleep, first phone/move after wake, prebed stimulation, and phone-stillness pressure.",
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
    parser = argparse.ArgumentParser(description="Build smartphone sleep-boundary timing latent features.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--grid-path", default="artifacts/multires_30min_event_hybrid_grid.parquet")
    parser.add_argument("--sleep-summary", default="artifacts/07_sleep_summary.parquet")
    parser.add_argument("--app-daily", default="artifacts/09_app_categories_daily.parquet")
    parser.add_argument("--app-prebed", default="artifacts/09_app_prebed_categories.parquet")
    parser.add_argument("--output", default="artifacts/domain_digital_boundary_v1.parquet")
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
