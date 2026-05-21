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


def values(part: pd.DataFrame, col: str) -> np.ndarray:
    if col not in part:
        return np.zeros(len(part), dtype=float)
    return np.nan_to_num(part[col].to_numpy(float), nan=0.0, posinf=0.0, neginf=0.0)


def flag(part: pd.DataFrame, col: str, threshold: float = 0.5) -> np.ndarray:
    return values(part, col) > threshold


def count_starts(mask: np.ndarray) -> int:
    flags = mask.astype(bool)
    if len(flags) == 0:
        return 0
    shifted = np.r_[False, flags[:-1]]
    return int((flags & ~shifted).sum())


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


def first_true_minutes(part: pd.DataFrame, mask: np.ndarray, anchor: pd.Timestamp) -> float:
    if len(part) == 0 or not mask.any():
        return 999.0
    return float((part.loc[mask, "timestamp"].iloc[0] - anchor).total_seconds() / 60.0)


def aggregate_window(part: pd.DataFrame, prefix: str, bright_thr: float) -> dict[str, float]:
    out: dict[str, float] = {}
    n = len(part)
    phone = flag(part, "ev_phone_active")
    moving = flag(part, "ev_moving")
    charging = flag(part, "ev_charging_on")
    low_cov = flag(part, "ev_low_coverage")
    no_wear = flag(part, "ev_no_wear")
    light = values(part, "mlight_mean") + values(part, "wlight_mean")
    bright = light > bright_thr
    screen = values(part, "screen_mean")
    steps = values(part, "step_sum")
    hr = values(part, "hr_mean")
    hr_present = values(part, "ev_present_hr") > 0.5
    silence = values(part, "amb_silence")
    speech = values(part, "amb_speech")
    music = values(part, "amb_music")
    still = ~moving

    out[f"{prefix}_tok_n"] = float(n)
    out[f"{prefix}_phone_ratio"] = float(phone.mean()) if n else 0.0
    out[f"{prefix}_phone_starts"] = float(count_starts(phone))
    out[f"{prefix}_moving_ratio"] = float(moving.mean()) if n else 0.0
    out[f"{prefix}_moving_starts"] = float(count_starts(moving))
    out[f"{prefix}_moving_longest_run"] = float(longest_run(moving))
    out[f"{prefix}_step_sum"] = float(steps.sum())
    out[f"{prefix}_step_mean"] = float(steps.mean()) if n else 0.0
    out[f"{prefix}_screen_mean"] = float(screen.mean()) if n else 0.0
    out[f"{prefix}_screen_max"] = float(screen.max()) if n else 0.0
    out[f"{prefix}_charging_ratio"] = float(charging.mean()) if n else 0.0
    out[f"{prefix}_bright_ratio"] = float(bright.mean()) if n else 0.0
    out[f"{prefix}_light_mean"] = float(light.mean()) if n else 0.0
    out[f"{prefix}_hr_mean"] = float(hr[hr_present].mean()) if hr_present.any() else 0.0
    out[f"{prefix}_hr_present_ratio"] = float(hr_present.mean()) if n else 0.0
    out[f"{prefix}_silence_mean"] = float(silence.mean()) if n else 0.0
    out[f"{prefix}_speech_music_mean"] = float((speech + music).mean()) if n else 0.0
    out[f"{prefix}_lowcov_or_nowear_ratio"] = float((low_cov | no_wear).mean()) if n else 0.0
    out[f"{prefix}_phone_still_ratio"] = float((phone & still).mean()) if n else 0.0
    out[f"{prefix}_phone_before_move_pressure"] = float((phone & ~moving).sum() - moving.sum()) if n else 0.0
    out[f"{prefix}_activation_score"] = (
        out[f"{prefix}_moving_ratio"]
        + np.log1p(out[f"{prefix}_step_sum"]) / 6.0
        + out[f"{prefix}_bright_ratio"]
        + out[f"{prefix}_speech_music_mean"]
        - out[f"{prefix}_phone_still_ratio"]
        - out[f"{prefix}_lowcov_or_nowear_ratio"]
    )
    return out


def summarize_wake_activation(day_grid: pd.DataFrame, wake: pd.Timestamp, sleep_row: pd.Series, bright_thr: float) -> dict[str, float]:
    out: dict[str, float] = {}
    windows = {
        "prewake1h": (wake - pd.Timedelta(hours=1), wake),
        "post30m": (wake, wake + pd.Timedelta(minutes=30)),
        "post1h": (wake, wake + pd.Timedelta(hours=1)),
        "post2h": (wake, wake + pd.Timedelta(hours=2)),
        "post4h": (wake, wake + pd.Timedelta(hours=4)),
        "daytime8h": (wake, wake + pd.Timedelta(hours=8)),
    }
    parts = {name: day_grid[(day_grid["timestamp"] >= start) & (day_grid["timestamp"] < end)] for name, (start, end) in windows.items()}
    for name, part in parts.items():
        out.update(aggregate_window(part, f"z_wai_{name}", bright_thr))

    post4h = parts["post4h"]
    light = values(post4h, "mlight_mean") + values(post4h, "wlight_mean")
    first_phone = first_true_minutes(post4h, flag(post4h, "ev_phone_active"), wake)
    first_move = first_true_minutes(post4h, flag(post4h, "ev_moving"), wake)
    first_steps = first_true_minutes(post4h, values(post4h, "step_sum") > 0.0, wake)
    first_screen = first_true_minutes(post4h, values(post4h, "screen_mean") > 0.0, wake)
    first_bright = first_true_minutes(post4h, light > bright_thr, wake)
    first_hr = first_true_minutes(post4h, values(post4h, "ev_present_hr") > 0.5, wake)
    out["z_wai_first_phone_latency_min"] = first_phone
    out["z_wai_first_move_latency_min"] = first_move
    out["z_wai_first_step_latency_min"] = first_steps
    out["z_wai_first_screen_latency_min"] = first_screen
    out["z_wai_first_bright_latency_min"] = first_bright
    out["z_wai_first_hr_latency_min"] = first_hr
    for name in ["phone", "move", "step", "screen", "bright", "hr"]:
        out[f"z_wai_{name}_recency"] = 1.0 / (1.0 + out[f"z_wai_first_{name}_latency_min"])

    def g(name: str) -> float:
        return float(out.get(name, 0.0))

    out["z_wai_phone_before_body_min"] = first_move - first_phone
    out["z_wai_screen_before_body_min"] = first_move - first_screen
    out["z_wai_body_before_phone_min"] = first_phone - first_move
    out["z_wai_activation_slope_30m_to_2h"] = g("z_wai_post2h_activation_score") - g("z_wai_post30m_activation_score")
    out["z_wai_activation_slope_1h_to_4h"] = g("z_wai_post4h_activation_score") - g("z_wai_post1h_activation_score")
    out["z_wai_step_slope_30m_to_2h"] = np.log1p(g("z_wai_post2h_step_sum")) - np.log1p(g("z_wai_post30m_step_sum"))
    out["z_wai_light_slope_30m_to_2h"] = g("z_wai_post2h_bright_ratio") - g("z_wai_post30m_bright_ratio")
    out["z_wai_inertia_score"] = (
        np.log1p(max(first_move, 0.0))
        + np.log1p(max(first_steps, 0.0))
        + g("z_wai_post1h_phone_still_ratio")
        + g("z_wai_post1h_lowcov_or_nowear_ratio")
        - g("z_wai_post1h_activation_score")
    )
    out["z_wai_clean_start_score"] = (
        g("z_wai_post1h_moving_ratio")
        + np.log1p(g("z_wai_post1h_step_sum")) / 6.0
        + g("z_wai_post1h_bright_ratio")
        - g("z_wai_post1h_phone_still_ratio")
        - np.log1p(max(first_move, 0.0)) / 6.0
    )

    tst = float(sleep_row.get("tst_min", 0.0) or 0.0)
    sleep_eff = float(sleep_row.get("sleep_eff", 0.0) or 0.0)
    sol = float(sleep_row.get("sol_proxy_min", 0.0) or 0.0)
    awakenings = float(sleep_row.get("n_awakenings", 0.0) or 0.0)
    out["z_wai_sleep_amount_x_activation"] = np.log1p(max(tst, 0.0)) * g("z_wai_post2h_activation_score")
    out["z_wai_sleep_eff_x_clean_start"] = sleep_eff * out["z_wai_clean_start_score"]
    out["z_wai_fragmented_sleep_x_inertia"] = (np.log1p(max(sol, 0.0)) + awakenings) * out["z_wai_inertia_score"]
    out["z_wai_short_sleep_slow_start"] = np.maximum(0.0, 420.0 - tst) / 60.0 + out["z_wai_inertia_score"]
    out["z_wai_long_sleep_slow_start"] = np.maximum(0.0, tst - 480.0) / 60.0 + out["z_wai_inertia_score"]
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
    sleep["wake_time"] = pd.to_datetime(sleep["wake_time"], errors="coerce")
    grid = grid_with_timestamp(args.grid_path)
    light = (grid.get("mlight_mean", 0.0).fillna(0.0) + grid.get("wlight_mean", 0.0).fillna(0.0)).astype(float)
    positive_light = light[light > 0]
    bright_thr = float(positive_light.quantile(0.75)) if len(positive_light) else 1.0

    merged = rows.merge(sleep, on=["subject_id", "sleep_date"], how="left", validate="many_to_one")
    grid_by_subject = {subject: group for subject, group in grid.groupby("subject_id")}
    out_rows = []
    for _, row in merged.iterrows():
        subject = str(row["subject_id"])
        out = {"subject_id": subject, "sleep_date": row["sleep_date"], "lifelog_date": row["lifelog_date"]}
        wake = row.get("wake_time")
        if pd.notna(wake) and subject in grid_by_subject:
            subject_grid = grid_by_subject[subject]
            day_grid = subject_grid[
                (subject_grid["timestamp"] >= wake - pd.Timedelta(hours=2))
                & (subject_grid["timestamp"] < wake + pd.Timedelta(hours=10))
            ]
            out.update(summarize_wake_activation(day_grid, wake, row, bright_thr))
            out["z_wai_wake_hour"] = float(wake.hour + wake.minute / 60.0)
        out_rows.append(out)

    features = pd.DataFrame(out_rows).fillna(0.0).replace([np.inf, -np.inf], 0.0)
    base_cols = [c for c in features.columns if c.startswith("z_wai_") and pd.api.types.is_numeric_dtype(features[c])]
    core_patterns = [
        "latency",
        "recency",
        "inertia",
        "clean_start",
        "activation",
        "slope",
        "phone_before",
        "body_before",
        "short_sleep",
        "long_sleep",
        "fragmented_sleep",
    ]
    core_cols = [c for c in base_cols if any(p in c for p in core_patterns)]
    features = add_subject_stats(features, core_cols)
    roll_cols = [
        c
        for c in [
            "z_wai_inertia_score",
            "z_wai_clean_start_score",
            "z_wai_activation_slope_30m_to_2h",
            "z_wai_step_slope_30m_to_2h",
            "z_wai_first_move_latency_min",
            "z_wai_first_step_latency_min",
            "z_wai_phone_before_body_min",
            "z_wai_sleep_eff_x_clean_start",
            "z_wai_fragmented_sleep_x_inertia",
        ]
        if c in features
    ]
    features = add_rolling(features, roll_cols)
    keep_cols = KEY_COLUMNS + sorted([c for c in features.columns if c.startswith("z_wai_") and pd.api.types.is_numeric_dtype(features[c])])
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
        "hypothesis": "S1 may depend on wake-start inertia: how quickly body, light, HR, and phone behavior activate after wake relative to the subject baseline.",
    }
    output.with_suffix(".report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    md = [
        "# Wake Activation Inertia Latents",
        "",
        "## Purpose",
        "",
        "Encode post-wake start-up dynamics: first movement/step/phone/light/HR, activation slope, phone-only sluggishness, and sleep-quality interaction.",
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
    parser = argparse.ArgumentParser(description="Build post-wake activation and sleep inertia latent features.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--grid-path", default="artifacts/multires_30min_event_hybrid_grid.parquet")
    parser.add_argument("--sleep-summary", default="artifacts/07_sleep_summary.parquet")
    parser.add_argument("--output", default="artifacts/domain_wake_activation_inertia_v1.parquet")
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
