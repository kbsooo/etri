from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


KEY_COLUMNS = ["subject_id", "lifelog_date"]
TARGET_KEYS = ["subject_id", "sleep_date", "lifelog_date"]
ROLL_WINDOWS = [3, 7, 14, 28]
WINDOWS = {
    "prebed90m": (-90, 0),
    "sleep_full": (0.0, 1.0),
    "sleep_first": (0.0, 1 / 3),
    "sleep_mid": (1 / 3, 2 / 3),
    "sleep_final": (2 / 3, 1.0),
    "postwake90m": (1.0, None),
}


def safe_float(value: float) -> float:
    if value != value or np.isinf(value):
        return 0.0
    return float(value)


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
    return int((flags & ~np.r_[False, flags[:-1]]).sum())


def transition_count(mask: np.ndarray) -> int:
    if len(mask) <= 1:
        return 0
    return int(np.abs(np.diff(mask.astype(int))).sum())


def window_slice(day_grid: pd.DataFrame, onset: pd.Timestamp, wake: pd.Timestamp, name: str) -> pd.DataFrame:
    left, right = WINDOWS[name]
    if name == "prebed90m":
        start = onset + pd.Timedelta(minutes=int(left))
        end = onset
    elif name == "postwake90m":
        start = wake
        end = wake + pd.Timedelta(minutes=90)
    else:
        total = wake - onset
        start = onset + total * float(left)
        end = onset + total * float(right)
    return day_grid[(day_grid["timestamp"] >= start) & (day_grid["timestamp"] < end)]


def summarize_window(part: pd.DataFrame, prefix: str, dark_thr: float, bright_thr: float) -> dict[str, float]:
    n = len(part)
    phone = flag(part, "ev_phone_active")
    moving = flag(part, "ev_moving")
    no_wear = flag(part, "ev_no_wear")
    low_cov = flag(part, "ev_low_coverage")
    charging = flag(part, "ev_charging_on")
    screen = values(part, "screen_mean")
    usage = values(part, "usage_total")
    steps = values(part, "step_sum")
    hr_present = flag(part, "ev_present_hr")
    pedo_present = flag(part, "ev_present_pedo")
    phone_present = flag(part, "ev_present_phone")
    gps_present = flag(part, "ev_present_gps")
    light = values(part, "mlight_mean") + values(part, "wlight_mean")
    silence = values(part, "amb_silence")
    speech = values(part, "amb_speech")
    music = values(part, "amb_music")

    dark = light <= dark_thr
    bright = light >= bright_thr
    still = ~moving
    phone_silent = ~phone & (screen <= 0.0) & (usage <= 0.0)
    sensor_quiet = (no_wear | low_cov | (~hr_present & ~pedo_present & ~phone_present))
    observed_quiet = still & phone_silent & dark
    ambient_quiet = silence >= np.maximum(speech, music)
    sleep_consensus = observed_quiet & (ambient_quiet | sensor_quiet)
    missing_sleep_like = sensor_quiet & dark & phone_silent & still
    device_off_conflict = sensor_quiet & (phone | (screen > 0.0) | (usage > 0.0) | moving | bright)
    intrusion = phone | moving | (screen > 0.0) | (usage > 0.0) | (steps > 0.0) | bright
    quiet_break = ~sleep_consensus & intrusion

    out = {f"{prefix}_tok_n": float(n)}
    for name, mask in [
        ("sleep_consensus", sleep_consensus),
        ("observed_quiet", observed_quiet),
        ("ambient_quiet", ambient_quiet),
        ("missing_sleep_like", missing_sleep_like),
        ("device_off_conflict", device_off_conflict),
        ("intrusion", intrusion),
        ("quiet_break", quiet_break),
        ("phone_dark_still_conflict", phone & dark & still),
        ("motion_dark_conflict", moving & dark),
        ("bright_still_conflict", bright & still),
        ("charging_quiet", charging & sleep_consensus),
    ]:
        out[f"{prefix}_{name}_ratio"] = safe_float(float(mask.mean())) if n else 0.0
        out[f"{prefix}_{name}_starts"] = float(count_starts(mask))
        out[f"{prefix}_{name}_transitions"] = float(transition_count(mask))
        out[f"{prefix}_{name}_longest_run"] = float(longest_run(mask))

    out[f"{prefix}_light_mean"] = safe_float(float(light.mean())) if n else 0.0
    out[f"{prefix}_light_std"] = safe_float(float(light.std())) if n else 0.0
    out[f"{prefix}_coverage_present_ratio"] = safe_float(float((hr_present | pedo_present | phone_present | gps_present).mean())) if n else 0.0
    out[f"{prefix}_sensor_disagreement_ratio"] = safe_float(float(((gps_present | phone_present) & ~(hr_present | pedo_present)).mean())) if n else 0.0
    out[f"{prefix}_purity_score"] = (
        out[f"{prefix}_sleep_consensus_ratio"]
        + out[f"{prefix}_sleep_consensus_longest_run"] / max(float(n), 1.0)
        + out[f"{prefix}_missing_sleep_like_ratio"]
        - out[f"{prefix}_quiet_break_ratio"]
        - out[f"{prefix}_device_off_conflict_ratio"]
    )
    out[f"{prefix}_micro_awake_score"] = (
        out[f"{prefix}_intrusion_starts"]
        + out[f"{prefix}_quiet_break_starts"]
        + out[f"{prefix}_phone_dark_still_conflict_starts"]
        + out[f"{prefix}_motion_dark_conflict_starts"]
    ) / max(float(n), 1.0)
    return out


def add_subject_and_rolling(features: pd.DataFrame) -> pd.DataFrame:
    features = features.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True)
    additions = {}
    base_cols = [c for c in features.columns if c.startswith("z_scp_")]
    for col in base_cols:
        if not pd.api.types.is_numeric_dtype(features[col]):
            continue
        center = features.groupby("subject_id")[col].transform("median")
        mad = features.groupby("subject_id")[col].transform(lambda s: np.nanmedian(np.abs(s - np.nanmedian(s))))
        std = features.groupby("subject_id")[col].transform("std").fillna(0.0)
        scale = pd.concat([mad, std / 1.4826, pd.Series(1.0, index=features.index)], axis=1).max(axis=1)
        additions[f"{col}_subdev"] = features[col] - center
        additions[f"{col}_subrz"] = ((features[col] - center) / scale).clip(-20.0, 20.0)
        additions[f"{col}_subpct"] = features.groupby("subject_id")[col].rank(pct=True).fillna(0.5)

    roll_cols = [
        c
        for c in base_cols
        if any(
            token in c
            for token in [
                "purity_score",
                "micro_awake_score",
                "sleep_consensus_ratio",
                "missing_sleep_like_ratio",
                "device_off_conflict_ratio",
                "quiet_break_ratio",
                "coverage_present_ratio",
            ]
        )
    ]
    for window in ROLL_WINDOWS:
        for col in roll_cols:
            shifted = features.groupby("subject_id")[col].shift(1)
            roll = shifted.groupby(features["subject_id"]).rolling(window, min_periods=2).mean().reset_index(level=0, drop=True)
            roll_std = shifted.groupby(features["subject_id"]).rolling(window, min_periods=3).std().reset_index(level=0, drop=True)
            additions[f"{col}_past{window}_delta"] = (features[col] - roll).fillna(0.0)
            additions[f"{col}_past{window}_volatility_gap"] = (features[col] - roll).abs().div(roll_std.fillna(0.0) + 1.0).fillna(0.0)
    return pd.concat([features, pd.DataFrame(additions, index=features.index)], axis=1)


def build_features(args: argparse.Namespace) -> pd.DataFrame:
    rows = load_rows(args.train_path, args.sample_path)
    sleep = pd.read_parquet(args.sleep_summary).copy()
    sleep["subject_id"] = sleep["subject_id"].astype(str)
    sleep["sleep_date"] = pd.to_datetime(sleep["sleep_date"]).dt.strftime("%Y-%m-%d")
    sleep["sleep_onset"] = pd.to_datetime(sleep["sleep_onset"], errors="coerce")
    sleep["wake_time"] = pd.to_datetime(sleep["wake_time"], errors="coerce")
    grid = grid_with_timestamp(args.grid_path)
    light = (grid.get("mlight_mean", 0.0).fillna(0.0) + grid.get("wlight_mean", 0.0).fillna(0.0)).astype(float)
    positive_light = light[light > 0]
    dark_thr = float(positive_light.quantile(0.20)) if len(positive_light) else 0.0
    bright_thr = float(positive_light.quantile(0.80)) if len(positive_light) else 1.0

    merged = rows.merge(sleep, on=["subject_id", "sleep_date"], how="left", validate="many_to_one")
    grid_by_subject = {subject: group for subject, group in grid.groupby("subject_id")}
    out_rows = []
    for _, row in merged.iterrows():
        subject = str(row["subject_id"])
        out = {"subject_id": subject, "lifelog_date": row["lifelog_date"]}
        onset = row.get("sleep_onset")
        wake = row.get("wake_time")
        if pd.notna(onset) and pd.notna(wake) and wake > onset and subject in grid_by_subject:
            subject_grid = grid_by_subject[subject]
            start = onset - pd.Timedelta(hours=2)
            end = wake + pd.Timedelta(hours=2)
            day_grid = subject_grid[(subject_grid["timestamp"] >= start) & (subject_grid["timestamp"] < end)]
            for name in WINDOWS:
                part = window_slice(day_grid, onset, wake, name)
                out.update(summarize_window(part, f"z_scp_{name}", dark_thr, bright_thr))
            first = out.get("z_scp_sleep_first_purity_score", 0.0)
            mid = out.get("z_scp_sleep_mid_purity_score", 0.0)
            final = out.get("z_scp_sleep_final_purity_score", 0.0)
            out["z_scp_purity_final_minus_first"] = final - first
            out["z_scp_purity_midpoint_u_shape"] = (first + final) / 2.0 - mid
            out["z_scp_micro_awake_final_minus_first"] = out.get("z_scp_sleep_final_micro_awake_score", 0.0) - out.get("z_scp_sleep_first_micro_awake_score", 0.0)
            out["z_scp_consensus_duration_share"] = out.get("z_scp_sleep_full_sleep_consensus_longest_run", 0.0) / max(out.get("z_scp_sleep_full_tok_n", 0.0), 1.0)
            out["z_scp_sleep_eff_x_purity"] = safe_float(float(row.get("sleep_eff", 0.0) or 0.0)) * out.get("z_scp_sleep_full_purity_score", 0.0)
            out["z_scp_awakenings_x_micro_awake"] = safe_float(float(row.get("n_awakenings", 0.0) or 0.0)) * out.get("z_scp_sleep_full_micro_awake_score", 0.0)
            out["z_scp_sol_x_prebed_conflict"] = safe_float(float(row.get("sol_proxy_min", 0.0) or 0.0)) * out.get("z_scp_prebed90m_intrusion_ratio", 0.0)
        out_rows.append(out)
    features = pd.DataFrame(out_rows).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    features = add_subject_and_rolling(features)
    keep_cols = KEY_COLUMNS + sorted([c for c in features.columns if c.startswith("z_scp_") and pd.api.types.is_numeric_dtype(features[c])])
    return features[keep_cols].sort_values(KEY_COLUMNS).replace([np.inf, -np.inf], 0.0).fillna(0.0)


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
        "hypothesis": "S2/S4 may depend on sleep-window consensus purity and micro-awakening conflicts, not broad ambient or postwake totals.",
    }
    output.with_suffix(".report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    md = [
        "# Sleep Consensus Purity Latents",
        "",
        "## Purpose",
        "",
        "Encode cross-modal sleep-window purity, micro-awakening conflicts, and whether missingness looks like sleep or device-off conflict.",
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
    parser = argparse.ArgumentParser(description="Build sleep consensus purity and micro-awakening latent features.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--grid-path", default="artifacts/multires_30min_event_hybrid_grid.parquet")
    parser.add_argument("--sleep-summary", default="artifacts/07_sleep_summary.parquet")
    parser.add_argument("--output", default="artifacts/domain_sleep_consensus_purity_v1.parquet")
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
