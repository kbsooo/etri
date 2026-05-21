from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


KEY_COLUMNS = ["subject_id", "lifelog_date"]
ROLL_WINDOWS = [3, 7, 14, 28]


def safe_float(value: float) -> float:
    if value != value or np.isinf(value):
        return 0.0
    return float(value)


def normalize_rows(path: str) -> pd.DataFrame:
    frame = pd.read_csv(path).copy()
    frame["subject_id"] = frame["subject_id"].astype(str)
    frame["lifelog_date"] = pd.to_datetime(frame["lifelog_date"]).dt.strftime("%Y-%m-%d")
    return frame[KEY_COLUMNS]


def load_rows(train_path: str, sample_path: str) -> pd.DataFrame:
    return pd.concat([normalize_rows(train_path), normalize_rows(sample_path)], ignore_index=True).drop_duplicates()


def load_grid(path: str) -> pd.DataFrame:
    grid = pd.read_parquet(path).copy()
    grid["subject_id"] = grid["subject_id"].astype(str)
    grid["date"] = pd.to_datetime(grid["date"]).dt.strftime("%Y-%m-%d")
    return grid


def scale_array(values: np.ndarray, scale: float) -> np.ndarray:
    values = np.nan_to_num(values.astype(float), nan=0.0, posinf=0.0, neginf=0.0)
    if scale <= 1e-8:
        return np.zeros_like(values)
    return np.clip(values / scale, 0.0, 8.0)


def entropy(values: np.ndarray) -> float:
    x = np.clip(np.nan_to_num(values.astype(float), nan=0.0), 0.0, None)
    total = x.sum()
    if total <= 1e-8:
        return 0.0
    p = x / total
    return safe_float(float(-(p * np.log(np.maximum(p, 1e-12))).sum()))


def weighted_phase(values: np.ndarray) -> tuple[float, float]:
    weights = np.clip(np.nan_to_num(values.astype(float), nan=0.0), 0.0, None)
    total = weights.sum()
    if total <= 1e-8:
        return 0.0, 0.0
    angles = 2.0 * np.pi * np.arange(len(weights)) / len(weights)
    sin_v = float((np.sin(angles) * weights).sum() / total)
    cos_v = float((np.cos(angles) * weights).sum() / total)
    strength = float(np.sqrt(sin_v**2 + cos_v**2))
    hour = float((np.arctan2(sin_v, cos_v) % (2.0 * np.pi)) * 24.0 / (2.0 * np.pi))
    return safe_float(hour), safe_float(strength)


def count_runs(mask: np.ndarray) -> tuple[int, int, int]:
    runs = []
    cur = 0
    for flag in mask.astype(bool):
        if flag:
            cur += 1
        elif cur:
            runs.append(cur)
            cur = 0
    if cur:
        runs.append(cur)
    if not runs:
        return 0, 0, 0
    return int(len(runs)), int(max(runs)), int(sum(1 for r in runs if r <= 2))


def transition_count(mask: np.ndarray) -> int:
    if len(mask) <= 1:
        return 0
    return int(np.abs(np.diff(mask.astype(int))).sum())


def segment_stats(values: np.ndarray, prefix: str, segments: dict[str, slice]) -> dict[str, float]:
    out = {}
    total = float(np.clip(values, 0.0, None).sum()) + 1e-8
    for name, slc in segments.items():
        part = values[slc]
        out[f"z_ef_{prefix}_{name}_sum"] = safe_float(part.sum())
        out[f"z_ef_{prefix}_{name}_mean"] = safe_float(part.mean() if len(part) else 0.0)
        out[f"z_ef_{prefix}_{name}_ratio"] = safe_float(part.sum() / total)
    return out


def build_daily_profiles(grid: pd.DataFrame) -> pd.DataFrame:
    scales = {}
    for col in [
        "step_sum",
        "cal_sum",
        "body_activity",
        "mobility_activity",
        "phone_activity",
        "screen_mean",
        "usage_total",
        "gps_speed_mean",
        "gps_speed_max",
    ]:
        if col in grid:
            vals = np.abs(grid[col].to_numpy(float))
            scale = np.nanpercentile(vals, 90)
            if not np.isfinite(scale) or scale <= 1e-8:
                scale = np.nanmax(vals)
            scales[col] = float(scale if np.isfinite(scale) and scale > 1e-8 else 1.0)

    segments = {
        "night": slice(0, 12),
        "morning": slice(12, 20),
        "workday": slice(20, 36),
        "evening": slice(36, 44),
        "late": slice(44, 48),
    }
    rows = []
    for (subject, date), group in grid.groupby(["subject_id", "date"], sort=True):
        group = group.sort_values("tok")
        if len(group) != 48:
            continue
        step = scale_array(group.get("step_sum", pd.Series(np.zeros(48))).to_numpy(float), scales.get("step_sum", 1.0))
        cal = scale_array(group.get("cal_sum", pd.Series(np.zeros(48))).to_numpy(float), scales.get("cal_sum", 1.0))
        body = scale_array(group.get("body_activity", pd.Series(np.zeros(48))).to_numpy(float), scales.get("body_activity", 1.0))
        mobility = scale_array(group.get("mobility_activity", pd.Series(np.zeros(48))).to_numpy(float), scales.get("mobility_activity", 1.0))
        phone = scale_array(group.get("phone_activity", pd.Series(np.zeros(48))).to_numpy(float), scales.get("phone_activity", 1.0))
        screen = scale_array(group.get("screen_mean", pd.Series(np.zeros(48))).to_numpy(float), scales.get("screen_mean", 1.0))
        usage = scale_array(group.get("usage_total", pd.Series(np.zeros(48))).to_numpy(float), scales.get("usage_total", 1.0))
        speed = scale_array(group.get("gps_speed_mean", pd.Series(np.zeros(48))).to_numpy(float), scales.get("gps_speed_mean", 1.0))
        speed_max = scale_array(group.get("gps_speed_max", pd.Series(np.zeros(48))).to_numpy(float), scales.get("gps_speed_max", 1.0))
        vehicle = np.nan_to_num(group.get("act_vehicle_ratio", pd.Series(np.zeros(48))).to_numpy(float), nan=0.0)
        moving = np.nan_to_num(group.get("ev_moving", pd.Series(np.zeros(48))).to_numpy(float), nan=0.0) > 0.5
        phone_active = np.nan_to_num(group.get("ev_phone_active", pd.Series(np.zeros(48))).to_numpy(float), nan=0.0) > 0.5

        energy = np.nanmean(np.vstack([step, cal, body, mobility]), axis=0)
        digital = np.nanmean(np.vstack([phone, screen, usage]), axis=0)
        commute = np.nanmean(np.vstack([speed, speed_max, vehicle]), axis=0)
        active = energy > max(float(np.nanmedian(energy) + 0.5 * np.nanstd(energy)), 0.15)
        commute_active = (commute > 0.35) | (vehicle > 0.25)
        active_runs, longest_active, micro_active = count_runs(active)
        commute_runs, longest_commute, micro_commute = count_runs(commute_active)
        energy_phase, energy_strength = weighted_phase(energy)
        digital_phase, digital_strength = weighted_phase(digital)

        out = {
            "subject_id": subject,
            "lifelog_date": date,
            "weekday": float(pd.Timestamp(date).weekday()),
            "z_ef_energy_sum": safe_float(energy.sum()),
            "z_ef_energy_mean": safe_float(energy.mean()),
            "z_ef_energy_std": safe_float(energy.std()),
            "z_ef_energy_entropy": entropy(energy),
            "z_ef_energy_peak_tok": float(np.argmax(energy)),
            "z_ef_energy_peak_hour": float(np.argmax(energy) / 2.0),
            "z_ef_energy_phase_hour": energy_phase,
            "z_ef_energy_phase_strength": energy_strength,
            "z_ef_digital_sum": safe_float(digital.sum()),
            "z_ef_digital_entropy": entropy(digital),
            "z_ef_digital_phase_hour": digital_phase,
            "z_ef_digital_phase_strength": digital_strength,
            "z_ef_energy_digital_phase_gap": safe_float(((digital_phase - energy_phase + 12.0) % 24.0) - 12.0),
            "z_ef_energy_active_run_count": float(active_runs),
            "z_ef_energy_longest_active_run": float(longest_active),
            "z_ef_energy_micro_active_runs": float(micro_active),
            "z_ef_energy_transition_count": float(transition_count(active)),
            "z_ef_phone_still_ratio": safe_float(float((phone_active & ~moving).mean())),
            "z_ef_move_phone_silent_ratio": safe_float(float((moving & ~phone_active).mean())),
            "z_ef_commute_sum": safe_float(commute.sum()),
            "z_ef_commute_am_sum": safe_float(commute[12:22].sum()),
            "z_ef_commute_pm_sum": safe_float(commute[32:44].sum()),
            "z_ef_commute_run_count": float(commute_runs),
            "z_ef_commute_longest_run": float(longest_commute),
            "z_ef_commute_micro_runs": float(micro_commute),
            "z_ef_commute_transition_count": float(transition_count(commute_active)),
            "z_ef_stop_go_commute": safe_float(transition_count(commute_active) / max(commute.sum(), 1e-6)),
        }
        out.update(segment_stats(energy, "energy", segments))
        out.update(segment_stats(digital, "digital", segments))
        out.update(segment_stats(commute, "commute", segments))
        rows.append(out)
    return pd.DataFrame(rows).sort_values(KEY_COLUMNS).reset_index(drop=True)


def add_subject_and_rolling(features: pd.DataFrame) -> pd.DataFrame:
    features = features.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True)
    additions = {}
    subject = features["subject_id"]
    base_cols = [c for c in features.columns if c.startswith("z_ef_")]
    for col in base_cols:
        center = features.groupby("subject_id")[col].transform("median")
        mad = features.groupby("subject_id")[col].transform(lambda s: np.nanmedian(np.abs(s - np.nanmedian(s))) + 1e-6)
        if col.endswith("_hour"):
            diff = ((features[col] - center + 12.0) % 24.0) - 12.0
            additions[f"{col}_subshift"] = diff
            additions[f"{col}_subabs_shift"] = diff.abs()
        else:
            additions[f"{col}_subdev"] = features[col] - center
            additions[f"{col}_subrz"] = (features[col] - center) / mad

    rolling_base = [
        "z_ef_energy_sum",
        "z_ef_energy_mean",
        "z_ef_energy_morning_sum",
        "z_ef_energy_workday_sum",
        "z_ef_energy_evening_sum",
        "z_ef_energy_active_run_count",
        "z_ef_energy_transition_count",
        "z_ef_commute_sum",
        "z_ef_stop_go_commute",
        "z_ef_digital_sum",
        "z_ef_phone_still_ratio",
    ]
    for window in ROLL_WINDOWS:
        for col in [c for c in rolling_base if c in features]:
            shifted = features.groupby("subject_id")[col].shift(1)
            roll = shifted.groupby(subject).rolling(window, min_periods=2).mean().reset_index(level=0, drop=True)
            roll_std = shifted.groupby(subject).rolling(window, min_periods=2).std().reset_index(level=0, drop=True)
            additions[f"{col}_past{window}_delta"] = (features[col] - roll).fillna(0.0)
            additions[f"{col}_past{window}_abs_delta"] = (features[col] - roll).abs().fillna(0.0)
            additions[f"{col}_past{window}_volatility"] = roll_std.fillna(0.0)

    add = pd.DataFrame(additions, index=features.index)
    out = pd.concat([features, add], axis=1)
    prev_energy = out.groupby("subject_id")["z_ef_energy_sum"].shift(1).fillna(0.0)
    out["z_ef_prev_load_morning_recovery"] = prev_energy * out.get("z_ef_energy_morning_sum", 0.0)
    out["z_ef_prev_load_low_morning"] = prev_energy * (-out.get("z_ef_energy_morning_sum_past7_delta", 0.0)).clip(lower=0.0)
    out["z_ef_prev_commute_low_recovery"] = out.groupby("subject_id")["z_ef_commute_sum"].shift(1).fillna(0.0) * (-out.get("z_ef_energy_morning_sum_past7_delta", 0.0)).clip(lower=0.0)
    return out


def build_features(args: argparse.Namespace) -> pd.DataFrame:
    rows = load_rows(args.train_path, args.sample_path)
    daily = build_daily_profiles(load_grid(args.grid_path))
    features = rows.merge(daily, on=KEY_COLUMNS, how="left")
    features = features.fillna(0.0)
    features = add_subject_and_rolling(features)
    keep = KEY_COLUMNS + sorted([c for c in features.columns if c.startswith("z_ef_") or c == "weekday"])
    return features[keep].replace([np.inf, -np.inf], 0.0).fillna(0.0)


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
        "hypotheses": [
            "S1/S3 may reflect daytime energy restoration and fragmentation rather than sleep timing.",
            "Physical fatigue recovery slope may appear as previous-day load followed by low morning energy.",
            "Commute stop-go and passive movement may proxy stress/fatigue load.",
            "Energy phase shift and micro-bouts may reveal disrupted daily rhythm.",
        ],
    }
    output.with_suffix(".report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    md = [
        "# Energy Fragmentation Latents",
        "",
        "## Purpose",
        "",
        "Build physical energy, recovery slope, commute stress, daytime fragmentation, and digital-energy phase features.",
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
    parser = argparse.ArgumentParser(description="Build daytime energy, fragmentation, recovery, and commute-stress features.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--grid-path", default="artifacts/multires_30min_event_hybrid_grid.parquet")
    parser.add_argument("--output", default="artifacts/domain_energy_fragmentation_v1.parquet")
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
