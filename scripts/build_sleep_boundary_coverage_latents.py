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
    "prebed2h": (-120, 0),
    "onset1h": (0, 60),
    "sleep_full": ("sleep", "sleep"),
    "sleep_first": (0.0, 1 / 3),
    "sleep_mid": (1 / 3, 2 / 3),
    "sleep_final": (2 / 3, 1.0),
    "wake1h": (-60, 0),
    "postwake2h": (0, 120),
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


def count_ends(mask: np.ndarray) -> int:
    flags = mask.astype(bool)
    if len(flags) == 0:
        return 0
    return int((flags & ~np.r_[flags[1:], False]).sum())


def transition_count(mask: np.ndarray) -> int:
    if len(mask) <= 1:
        return 0
    return int(np.abs(np.diff(mask.astype(int))).sum())


def entropy(values_: np.ndarray) -> float:
    x = np.clip(np.nan_to_num(values_.astype(float), nan=0.0), 0.0, None)
    total = x.sum()
    if total <= 1e-8:
        return 0.0
    prob = x / total
    return safe_float(float(-(prob * np.log(np.maximum(prob, 1e-12))).sum()))


def window_slice(day_grid: pd.DataFrame, onset: pd.Timestamp, wake: pd.Timestamp, name: str) -> pd.DataFrame:
    spec = WINDOWS[name]
    if name == "prebed2h":
        start = onset + pd.Timedelta(minutes=int(spec[0]))
        end = onset + pd.Timedelta(minutes=int(spec[1]))
    elif name == "onset1h":
        start = onset + pd.Timedelta(minutes=int(spec[0]))
        end = onset + pd.Timedelta(minutes=int(spec[1]))
    elif name == "sleep_full":
        start = onset
        end = wake
    elif name in {"sleep_first", "sleep_mid", "sleep_final"}:
        total = wake - onset
        start = onset + total * float(spec[0])
        end = onset + total * float(spec[1])
    elif name == "wake1h":
        start = wake + pd.Timedelta(minutes=int(spec[0]))
        end = wake + pd.Timedelta(minutes=int(spec[1]))
    elif name == "postwake2h":
        start = wake + pd.Timedelta(minutes=int(spec[0]))
        end = wake + pd.Timedelta(minutes=int(spec[1]))
    else:
        raise ValueError(f"Unknown window: {name}")
    return day_grid[(day_grid["timestamp"] >= start) & (day_grid["timestamp"] < end)]


def summarize_window(part: pd.DataFrame, prefix: str) -> dict[str, float]:
    n = len(part)
    no_wear = flag(part, "ev_no_wear")
    low_cov = flag(part, "ev_low_coverage")
    hr_present = flag(part, "ev_present_hr")
    pedo_present = flag(part, "ev_present_pedo")
    gps_present = flag(part, "ev_present_gps")
    phone_present = flag(part, "ev_present_phone")
    light_present = flag(part, "ev_present_light")
    ambience_present = flag(part, "ev_present_ambience")
    phone_active = flag(part, "ev_phone_active")
    charging = flag(part, "ev_charging_on")
    coverage = values(part, "sensor_coverage_n")
    missing_run_cols = [
        "ev_present_hr_missing_run",
        "ev_present_pedo_missing_run",
        "ev_present_gps_missing_run",
        "ev_present_phone_missing_run",
        "ev_no_wear_present_run",
        "ev_low_coverage_present_run",
    ]
    present_count = (
        hr_present.astype(int)
        + pedo_present.astype(int)
        + gps_present.astype(int)
        + phone_present.astype(int)
        + light_present.astype(int)
        + ambience_present.astype(int)
    )
    body_missing = ~(hr_present | pedo_present)
    phone_only_present = phone_present & ~(hr_present | pedo_present)
    body_only_present = (hr_present | pedo_present) & ~phone_present
    device_off = no_wear | low_cov | body_missing
    intentional_off_like = device_off & ~phone_active
    conflict_off = device_off & (phone_active | phone_present)
    coverage_state = np.where(no_wear, 3, np.where(low_cov, 2, np.where(body_missing, 1, 0)))

    out = {f"{prefix}_tok_n": float(n)}
    for name, mask in [
        ("no_wear", no_wear),
        ("low_coverage", low_cov),
        ("body_missing", body_missing),
        ("phone_missing", ~phone_present),
        ("device_off", device_off),
        ("intentional_off_like", intentional_off_like),
        ("conflict_off", conflict_off),
        ("phone_only_present", phone_only_present),
        ("body_only_present", body_only_present),
        ("charging_device_off", charging & device_off),
    ]:
        out[f"{prefix}_{name}_ratio"] = safe_float(float(mask.mean())) if n else 0.0
        out[f"{prefix}_{name}_starts"] = float(count_starts(mask))
        out[f"{prefix}_{name}_ends"] = float(count_ends(mask))
        out[f"{prefix}_{name}_transitions"] = float(transition_count(mask))
        out[f"{prefix}_{name}_longest_run"] = float(longest_run(mask))

    out[f"{prefix}_coverage_mean"] = safe_float(float(coverage.mean())) if n else 0.0
    out[f"{prefix}_coverage_std"] = safe_float(float(coverage.std())) if n else 0.0
    out[f"{prefix}_coverage_min"] = safe_float(float(coverage.min())) if n else 0.0
    out[f"{prefix}_present_count_mean"] = safe_float(float(present_count.mean())) if n else 0.0
    out[f"{prefix}_present_count_std"] = safe_float(float(present_count.std())) if n else 0.0
    out[f"{prefix}_coverage_state_entropy"] = entropy(np.bincount(coverage_state, minlength=4).astype(float))
    out[f"{prefix}_coverage_state_transitions"] = float(transition_count(coverage_state))
    for col in missing_run_cols:
        arr = values(part, col)
        out[f"{prefix}_{col}_mean"] = safe_float(float(arr.mean())) if n else 0.0
        out[f"{prefix}_{col}_max"] = safe_float(float(arr.max())) if n else 0.0

    out[f"{prefix}_off_stability_score"] = (
        out[f"{prefix}_intentional_off_like_ratio"]
        + out[f"{prefix}_intentional_off_like_longest_run"] / max(float(n), 1.0)
        - out[f"{prefix}_conflict_off_ratio"]
        - out[f"{prefix}_coverage_state_transitions"] / max(float(n), 1.0)
    )
    out[f"{prefix}_off_fragment_score"] = (
        out[f"{prefix}_device_off_starts"]
        + out[f"{prefix}_device_off_transitions"]
        + out[f"{prefix}_conflict_off_starts"]
    ) / max(float(n), 1.0)
    return out


def add_subject_and_rolling(features: pd.DataFrame) -> pd.DataFrame:
    features = features.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True)
    additions = {}
    base_cols = [c for c in features.columns if c.startswith("z_sbc_")]
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
                "device_off_ratio",
                "intentional_off_like_ratio",
                "conflict_off_ratio",
                "off_stability_score",
                "off_fragment_score",
                "coverage_mean",
                "coverage_state_entropy",
                "coverage_state_transitions",
            ]
        )
    ]
    for window in ROLL_WINDOWS:
        for col in roll_cols:
            shifted = features.groupby("subject_id")[col].shift(1)
            roll = shifted.groupby(features["subject_id"]).rolling(window, min_periods=2).mean().reset_index(level=0, drop=True)
            roll_std = shifted.groupby(features["subject_id"]).rolling(window, min_periods=3).std().reset_index(level=0, drop=True)
            delta = features[col] - roll
            additions[f"{col}_past{window}_delta"] = delta.fillna(0.0)
            additions[f"{col}_past{window}_abs_delta"] = delta.abs().fillna(0.0)
            additions[f"{col}_past{window}_volatility_gap"] = delta.abs().div(roll_std.fillna(0.0) + 1.0).fillna(0.0)
    return pd.concat([features, pd.DataFrame(additions, index=features.index)], axis=1)


def build_features(args: argparse.Namespace) -> pd.DataFrame:
    rows = load_rows(args.train_path, args.sample_path)
    sleep = pd.read_parquet(args.sleep_summary).copy()
    sleep["subject_id"] = sleep["subject_id"].astype(str)
    sleep["sleep_date"] = pd.to_datetime(sleep["sleep_date"]).dt.strftime("%Y-%m-%d")
    sleep["sleep_onset"] = pd.to_datetime(sleep["sleep_onset"], errors="coerce")
    sleep["wake_time"] = pd.to_datetime(sleep["wake_time"], errors="coerce")
    grid = grid_with_timestamp(args.grid_path)
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
            day_grid = subject_grid[
                (subject_grid["timestamp"] >= onset - pd.Timedelta(hours=3))
                & (subject_grid["timestamp"] < wake + pd.Timedelta(hours=3))
            ]
            for window in WINDOWS:
                out.update(summarize_window(window_slice(day_grid, onset, wake, window), f"z_sbc_{window}"))
            out["z_sbc_sleep_final_minus_first_off_stability"] = out.get("z_sbc_sleep_final_off_stability_score", 0.0) - out.get("z_sbc_sleep_first_off_stability_score", 0.0)
            out["z_sbc_sleep_final_minus_first_fragment"] = out.get("z_sbc_sleep_final_off_fragment_score", 0.0) - out.get("z_sbc_sleep_first_off_fragment_score", 0.0)
            out["z_sbc_wake_minus_onset_conflict"] = out.get("z_sbc_wake1h_conflict_off_ratio", 0.0) - out.get("z_sbc_onset1h_conflict_off_ratio", 0.0)
            out["z_sbc_prebed_to_sleep_off_shift"] = out.get("z_sbc_sleep_full_device_off_ratio", 0.0) - out.get("z_sbc_prebed2h_device_off_ratio", 0.0)
            out["z_sbc_postwake_recoverage_gap"] = out.get("z_sbc_sleep_full_coverage_mean", 0.0) - out.get("z_sbc_postwake2h_coverage_mean", 0.0)
        out_rows.append(out)
    features = pd.DataFrame(out_rows).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    features = add_subject_and_rolling(features)
    keep_cols = KEY_COLUMNS + sorted([c for c in features.columns if c.startswith("z_sbc_") and pd.api.types.is_numeric_dtype(features[c])])
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

    best = pd.read_parquet(args.best).copy()
    best["subject_id"] = best["subject_id"].astype(str)
    best["lifelog_date"] = pd.to_datetime(best["lifelog_date"]).dt.strftime("%Y-%m-%d")
    best_cols = [col for col in best.columns if col.startswith("z_")]
    additive = best[KEY_COLUMNS + best_cols].merge(features, on=KEY_COLUMNS, how="inner", validate="one_to_one")
    additive_output = Path(args.additive_output)
    additive_output.parent.mkdir(parents=True, exist_ok=True)
    additive.to_parquet(additive_output, index=False)

    feature_cols = [c for c in features.columns if c not in KEY_COLUMNS]
    coverage = pd.DataFrame(
        {
            "feature": feature_cols,
            "mean": [float(features[c].mean(skipna=True)) for c in feature_cols],
            "std": [float(features[c].std(skipna=True)) for c in feature_cols],
        }
    )
    report = {
        "output": str(output),
        "additive_output": str(additive_output),
        "rows": int(len(features)),
        "feature_count": int(len(feature_cols)),
        "additive_feature_count": int(len(additive.columns) - len(KEY_COLUMNS)),
        "windows": WINDOWS,
        "hypothesis": "S4 should be read through subject-relative coverage/no-wear rhythm around sleep boundaries, not broad routine interactions.",
    }
    output.with_suffix(".report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    md = [
        "# Sleep Boundary Coverage Latents",
        "",
        "## Purpose",
        "",
        report["hypothesis"],
        "",
        f"- Output: `{output}`",
        f"- Additive output: `{additive_output}`",
        f"- Rows: `{len(features)}`",
        f"- Feature count: `{len(feature_cols)}`",
        "",
        "## Feature Summary",
        "",
        dataframe_to_markdown(coverage.head(60)),
    ]
    output.with_suffix(".report.md").write_text("\n".join(md), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build sleep-boundary coverage/no-wear objective latents.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--grid-path", default="artifacts/multires_30min_event_hybrid_grid.parquet")
    parser.add_argument("--sleep-summary", default="artifacts/07_sleep_summary.parquet")
    parser.add_argument("--best", default="artifacts/domain_best_late_fusion_v1.parquet")
    parser.add_argument("--output", default="artifacts/domain_sleep_boundary_coverage_v1.parquet")
    parser.add_argument("--additive-output", default="artifacts/domain_best_plus_sleep_boundary_coverage_v1.parquet")
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
