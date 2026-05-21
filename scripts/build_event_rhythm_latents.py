from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


KEY_COLUMNS = ["subject_id", "lifelog_date"]
SIGNALS = {
    "phone": ["phone_activity", "screen_mean", "usage_total", "ev_phone_active"],
    "mobility": ["mobility_activity", "gps_speed_mean", "step_sum", "ev_moving"],
    "body": ["body_activity", "hr_mean", "pedo_n", "act_walk_ratio"],
    "coverage": ["sensor_coverage_n", "ev_present_phone", "ev_present_gps", "ev_present_hr", "ev_no_wear"],
}
PHASES = {
    "night": range(0, 12),
    "morning": range(12, 24),
    "afternoon": range(24, 36),
    "evening": range(36, 48),
}


def safe_float(value: float) -> float:
    if value != value or np.isinf(value):
        return 0.0
    return float(value)


def normalized_signal(group: pd.DataFrame, cols: list[str]) -> np.ndarray:
    values = []
    for col in cols:
        if col not in group:
            continue
        x = group[col].to_numpy(float)
        x = np.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0)
        scale = np.nanpercentile(np.abs(x), 90)
        if scale <= 1e-8:
            scale = np.nanmax(np.abs(x))
        if scale <= 1e-8:
            values.append(np.zeros_like(x))
        else:
            values.append(np.clip(x / scale, 0.0, 5.0))
    if not values:
        return np.zeros(len(group), dtype=float)
    return np.nanmean(np.vstack(values), axis=0)


def active_runs(active: np.ndarray) -> list[int]:
    runs = []
    current = 0
    for flag in active.astype(bool):
        if flag:
            current += 1
        elif current:
            runs.append(current)
            current = 0
    if current:
        runs.append(current)
    return runs


def burstiness_from_times(times: np.ndarray) -> float:
    if len(times) < 3:
        return 0.0
    intervals = np.diff(times.astype(float))
    mean = intervals.mean()
    std = intervals.std()
    denom = std + mean
    return float((std - mean) / denom) if denom > 1e-8 else 0.0


def circular_stats(signal: np.ndarray) -> dict[str, float]:
    weights = np.clip(signal.astype(float), 0.0, None)
    total = weights.sum()
    if total <= 1e-8:
        return {"phase_sin": 0.0, "phase_cos": 0.0, "phase_strength": 0.0, "phase_hour": 0.0}
    angles = 2.0 * np.pi * np.arange(len(weights)) / len(weights)
    sin_v = float((np.sin(angles) * weights).sum() / total)
    cos_v = float((np.cos(angles) * weights).sum() / total)
    strength = float(np.sqrt(sin_v**2 + cos_v**2))
    hour = float((np.arctan2(sin_v, cos_v) % (2.0 * np.pi)) * 24.0 / (2.0 * np.pi))
    return {"phase_sin": sin_v, "phase_cos": cos_v, "phase_strength": strength, "phase_hour": hour}


def entropy(values: np.ndarray) -> float:
    total = values.sum()
    if total <= 1e-8:
        return 0.0
    prob = values / total
    return float(-(prob * np.log(np.maximum(prob, 1e-12))).sum())


def day_signal_features(signal: np.ndarray, prefix: str) -> dict[str, float]:
    signal = np.nan_to_num(signal, nan=0.0, posinf=0.0, neginf=0.0)
    threshold = max(float(np.nanmedian(signal) + 0.5 * np.nanstd(signal)), 1e-8)
    active = signal > threshold
    active_idx = np.flatnonzero(active)
    runs = active_runs(active)
    phase_sums = np.array([signal[list(slots)].sum() for slots in PHASES.values()], dtype=float)
    phase_ratio = phase_sums / max(phase_sums.sum(), 1e-8)
    circ = circular_stats(signal)
    out = {
        f"z_er_{prefix}_sum": safe_float(signal.sum()),
        f"z_er_{prefix}_mean": safe_float(signal.mean()),
        f"z_er_{prefix}_std": safe_float(signal.std()),
        f"z_er_{prefix}_max": safe_float(signal.max()),
        f"z_er_{prefix}_active_ratio": safe_float(active.mean()),
        f"z_er_{prefix}_run_count": float(len(runs)),
        f"z_er_{prefix}_longest_run": float(max(runs) if runs else 0),
        f"z_er_{prefix}_mean_run": safe_float(float(np.mean(runs)) if runs else 0.0),
        f"z_er_{prefix}_burstiness": burstiness_from_times(active_idx),
        f"z_er_{prefix}_phase_entropy": entropy(phase_sums),
        f"z_er_{prefix}_phase_peak": float(np.argmax(phase_sums)) if phase_sums.sum() > 0 else 0.0,
        f"z_er_{prefix}_phase_strength": circ["phase_strength"],
        f"z_er_{prefix}_phase_sin": circ["phase_sin"],
        f"z_er_{prefix}_phase_cos": circ["phase_cos"],
        f"z_er_{prefix}_phase_hour": circ["phase_hour"],
    }
    for phase_name, ratio in zip(PHASES.keys(), phase_ratio):
        out[f"z_er_{prefix}_{phase_name}_ratio"] = safe_float(ratio)
    return out


def build_features(grid: pd.DataFrame) -> pd.DataFrame:
    rows = []
    grid = grid.copy()
    grid["subject_id"] = grid["subject_id"].astype(str)
    grid["date"] = pd.to_datetime(grid["date"]).dt.strftime("%Y-%m-%d")
    for (subject, date), group in grid.groupby(["subject_id", "date"], sort=True):
        group = group.sort_values("tok")
        row = {"subject_id": subject, "lifelog_date": date}
        signals = {name: normalized_signal(group, cols) for name, cols in SIGNALS.items()}
        for name, signal in signals.items():
            row.update(day_signal_features(signal, name))
        for left, right in [("phone", "mobility"), ("phone", "body"), ("mobility", "body"), ("coverage", "phone")]:
            a = signals[left]
            b = signals[right]
            if np.std(a) > 1e-8 and np.std(b) > 1e-8:
                corr = float(np.corrcoef(a, b)[0, 1])
            else:
                corr = 0.0
            row[f"z_er_{left}_{right}_corr"] = safe_float(corr)
            row[f"z_er_{left}_{right}_abs_gap_mean"] = safe_float(np.mean(np.abs(a - b)))
            row[f"z_er_{left}_{right}_coactive_ratio"] = safe_float(((a > np.median(a)) & (b > np.median(b))).mean())
        rows.append(row)
    features = pd.DataFrame(rows).sort_values(KEY_COLUMNS).reset_index(drop=True)
    phase_cols = [c for c in features.columns if c.endswith("_phase_hour")]
    for col in phase_cols:
        center = features.groupby("subject_id")[col].transform("median")
        diff = ((features[col] - center + 12.0) % 24.0) - 12.0
        features[f"{col}_subject_shift_abs"] = diff.abs()
        features[f"{col}_subject_shift_signed"] = diff
    return features


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
    grid = pd.read_parquet(args.input)
    features = build_features(grid)
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
        "input": args.input,
        "output": str(output),
        "rows": int(len(features)),
        "feature_count": int(len(feature_cols)),
        "signals": SIGNALS,
    }
    output.with_suffix(".report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    md = [
        "# Event Rhythm Latents",
        "",
        "## Purpose",
        "",
        "Encode burstiness, active-run structure, circadian phase, and cross-modal rhythm gaps from the 30-minute token grid.",
        "",
        f"- Input: `{args.input}`",
        f"- Output: `{output}`",
        f"- Rows: `{len(features)}`",
        f"- Feature count: `{len(feature_cols)}`",
        "",
        "## Feature Coverage",
        "",
        dataframe_to_markdown(coverage.head(24)),
    ]
    output.with_suffix(".report.md").write_text("\n".join(md), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build event burstiness/circadian rhythm latent features from a token grid.")
    parser.add_argument("--input", default="artifacts/multires_30min_event_hybrid_grid.parquet")
    parser.add_argument("--output", default="artifacts/domain_event_rhythm_v1.parquet")
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
