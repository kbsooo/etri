from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler


KEY_COLUMNS = ["subject_id", "lifelog_date"]
ROLL_WINDOWS = [7, 14, 28]
PROFILE_SIGNALS = [
    "sensor_coverage_n",
    "ev_no_wear",
    "ev_low_coverage",
    "ev_present_hr",
    "ev_present_pedo",
    "ev_present_phone",
    "ev_present_gps",
    "ev_charging_on",
]


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


def entropy(values: np.ndarray) -> float:
    x = np.clip(np.nan_to_num(values.astype(float), nan=0.0), 0.0, None)
    total = x.sum()
    if total <= 1e-8:
        return 0.0
    prob = x / total
    return safe_float(float(-(prob * np.log(np.maximum(prob, 1e-12))).sum()))


def corr(a: np.ndarray, b: np.ndarray) -> float:
    a = np.nan_to_num(a.astype(float), nan=0.0, posinf=0.0, neginf=0.0)
    b = np.nan_to_num(b.astype(float), nan=0.0, posinf=0.0, neginf=0.0)
    if np.std(a) <= 1e-8 or np.std(b) <= 1e-8:
        return 0.0
    return safe_float(float(np.corrcoef(a, b)[0, 1]))


def cosine_dist(a: np.ndarray, b: np.ndarray) -> float:
    a = np.nan_to_num(a.astype(float), nan=0.0, posinf=0.0, neginf=0.0)
    b = np.nan_to_num(b.astype(float), nan=0.0, posinf=0.0, neginf=0.0)
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom <= 1e-8:
        return 0.0
    return safe_float(1.0 - float(np.dot(a, b) / denom))


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


def transition_count(mask: np.ndarray) -> int:
    if len(mask) <= 1:
        return 0
    return int(np.abs(np.diff(mask.astype(int))).sum())


def circular_phase(signal: np.ndarray) -> tuple[float, float]:
    weights = np.clip(np.nan_to_num(signal.astype(float), nan=0.0), 0.0, None)
    total = weights.sum()
    if total <= 1e-8:
        return 0.0, 0.0
    angles = 2.0 * np.pi * np.arange(len(weights)) / len(weights)
    sin_v = float((np.sin(angles) * weights).sum() / total)
    cos_v = float((np.cos(angles) * weights).sum() / total)
    strength = float(np.sqrt(sin_v**2 + cos_v**2))
    hour = float((np.arctan2(sin_v, cos_v) % (2.0 * np.pi)) * 24.0 / (2.0 * np.pi))
    return safe_float(hour), safe_float(strength)


def hour_shift(value: float, center: float) -> float:
    return safe_float(((value - center + 12.0) % 24.0) - 12.0)


def scaled_profile(group: pd.DataFrame, scales: dict[str, float]) -> dict[str, np.ndarray]:
    out = {}
    group = group.sort_values("tok")
    for col in PROFILE_SIGNALS:
        if col not in group:
            out[col] = np.zeros(48, dtype=float)
            continue
        arr = np.nan_to_num(group[col].to_numpy(float), nan=0.0, posinf=0.0, neginf=0.0)
        if len(arr) != 48:
            fixed = np.zeros(48, dtype=float)
            fixed[: min(len(arr), 48)] = arr[:48]
            arr = fixed
        scale = scales.get(col, 1.0)
        if scale <= 1e-8:
            out[col] = np.zeros(48, dtype=float)
        else:
            out[col] = np.clip(arr / scale, 0.0, 5.0)
    return out


def flatten_profile(profile: dict[str, np.ndarray]) -> np.ndarray:
    return np.concatenate([profile[col] for col in PROFILE_SIGNALS])


def profile_rows(grid: pd.DataFrame) -> tuple[pd.DataFrame, dict[tuple[str, str], dict[str, np.ndarray]], np.ndarray]:
    grid = grid.copy()
    grid["subject_id"] = grid["subject_id"].astype(str)
    grid["date"] = pd.to_datetime(grid["date"]).dt.strftime("%Y-%m-%d")
    scales = {}
    for col in PROFILE_SIGNALS:
        vals = np.abs(grid[col].to_numpy(float)) if col in grid else np.array([1.0])
        scale = np.nanpercentile(vals, 95)
        if not np.isfinite(scale) or scale <= 1e-8:
            scale = np.nanmax(vals)
        scales[col] = float(scale if np.isfinite(scale) and scale > 1e-8 else 1.0)

    rows = []
    profiles: dict[tuple[str, str], dict[str, np.ndarray]] = {}
    flat_parts = []
    for (subject, date), group in grid.groupby(["subject_id", "date"], sort=True):
        profile = scaled_profile(group, scales)
        profiles[(subject, date)] = profile
        flat = flatten_profile(profile)
        flat_parts.append(flat)
        no_wear = profile["ev_no_wear"] > 0.5
        low_cov = profile["ev_low_coverage"] > 0.5
        device_off = no_wear | low_cov | ((profile["ev_present_hr"] + profile["ev_present_pedo"]) <= 0.0)
        coverage = profile["sensor_coverage_n"]
        off_hour, off_strength = circular_phase(device_off.astype(float))
        cov_hour, cov_strength = circular_phase(coverage)
        rows.append(
            {
                "subject_id": subject,
                "lifelog_date": date,
                "weekday": int(pd.Timestamp(date).weekday()),
                "z_crp_no_wear_ratio": safe_float(float(no_wear.mean())),
                "z_crp_low_coverage_ratio": safe_float(float(low_cov.mean())),
                "z_crp_device_off_ratio": safe_float(float(device_off.mean())),
                "z_crp_device_off_longest_run": float(longest_run(device_off)),
                "z_crp_device_off_transitions": float(transition_count(device_off)),
                "z_crp_device_off_entropy": entropy(device_off.astype(float)),
                "z_crp_device_off_phase_hour": off_hour,
                "z_crp_device_off_phase_strength": off_strength,
                "z_crp_coverage_mean": safe_float(float(coverage.mean())),
                "z_crp_coverage_std": safe_float(float(coverage.std())),
                "z_crp_coverage_entropy": entropy(coverage),
                "z_crp_coverage_phase_hour": cov_hour,
                "z_crp_coverage_phase_strength": cov_strength,
                "z_crp_night_device_off_ratio": safe_float(float(device_off[:12].mean())),
                "z_crp_evening_device_off_ratio": safe_float(float(device_off[36:].mean())),
                "z_crp_night_coverage_mean": safe_float(float(coverage[:12].mean())),
                "z_crp_evening_coverage_mean": safe_float(float(coverage[36:].mean())),
            }
        )
    return pd.DataFrame(rows), profiles, np.vstack(flat_parts)


def add_baseline_distances(features: pd.DataFrame, profiles: dict[tuple[str, str], dict[str, np.ndarray]]) -> pd.DataFrame:
    subject_base: dict[str, np.ndarray] = {}
    weekday_base: dict[tuple[str, int], np.ndarray] = {}
    global_base = np.nanmedian(np.vstack([flatten_profile(p) for p in profiles.values()]), axis=0)
    for subject in features["subject_id"].astype(str).unique():
        parts = [flatten_profile(p) for (s, _), p in profiles.items() if s == subject]
        subject_base[subject] = np.nanmedian(np.vstack(parts), axis=0) if parts else global_base
        for weekday in range(7):
            wparts = [flatten_profile(p) for (s, d), p in profiles.items() if s == subject and pd.Timestamp(d).weekday() == weekday]
            if wparts:
                weekday_base[(subject, weekday)] = np.nanmedian(np.vstack(wparts), axis=0)

    additions = []
    for _, row in features.iterrows():
        key = (str(row["subject_id"]), row["lifelog_date"])
        flat = flatten_profile(profiles[key])
        subj = subject_base.get(str(row["subject_id"]), global_base)
        wb = weekday_base.get((str(row["subject_id"]), int(row["weekday"])), subj)
        additions.append(
            {
                "z_crp_profile_corr_to_subject": corr(flat, subj),
                "z_crp_profile_cosine_dist_to_subject": cosine_dist(flat, subj),
                "z_crp_profile_abs_gap_to_subject": safe_float(float(np.mean(np.abs(flat - subj)))),
                "z_crp_profile_corr_to_subject_weekday": corr(flat, wb),
                "z_crp_profile_abs_gap_to_subject_weekday": safe_float(float(np.mean(np.abs(flat - wb)))),
                "z_crp_weekday_gap_minus_global_gap": safe_float(float(np.mean(np.abs(flat - wb)) - np.mean(np.abs(flat - subj)))),
                "z_crp_profile_cosine_dist_to_global": cosine_dist(flat, global_base),
            }
        )
    return pd.concat([features.reset_index(drop=True), pd.DataFrame(additions)], axis=1)


def add_prototype_distances(features: pd.DataFrame, flat_profiles: np.ndarray, n_clusters: int, seed: int) -> pd.DataFrame:
    matrix = SimpleImputer(strategy="median", keep_empty_features=True).fit_transform(flat_profiles)
    matrix = StandardScaler().fit_transform(matrix)
    n_clusters = min(n_clusters, max(2, len(features) // 20))
    model = KMeans(n_clusters=n_clusters, random_state=seed, n_init=20)
    labels = model.fit_predict(matrix)
    dists = model.transform(matrix)
    additions = {
        "z_crp_proto_label": labels.astype(float),
        "z_crp_proto_min_dist": dists.min(axis=1),
        "z_crp_proto_margin_1_2": np.sort(dists, axis=1)[:, 1] - np.sort(dists, axis=1)[:, 0],
        "z_crp_proto_entropy": np.array([entropy(1.0 / (row + 1e-6)) for row in dists]),
    }
    for idx in range(n_clusters):
        additions[f"z_crp_proto_dist_{idx:02d}"] = dists[:, idx]
        additions[f"z_crp_proto_weight_{idx:02d}"] = np.exp(-dists[:, idx]) / np.exp(-dists).sum(axis=1)
    return pd.concat([features.reset_index(drop=True), pd.DataFrame(additions)], axis=1)


def add_subject_and_rolling(features: pd.DataFrame) -> pd.DataFrame:
    features["lifelog_dt"] = pd.to_datetime(features["lifelog_date"])
    features = features.sort_values(["subject_id", "lifelog_dt"]).reset_index(drop=True)
    additions = {}
    base_cols = [c for c in features.columns if c.startswith("z_crp_")]
    for col in base_cols:
        if not pd.api.types.is_numeric_dtype(features[col]):
            continue
        center = features.groupby("subject_id")[col].transform("median")
        if col.endswith("_phase_hour"):
            diff = ((features[col] - center + 12.0) % 24.0) - 12.0
            additions[f"{col}_subshift"] = diff
            additions[f"{col}_subabs_shift"] = diff.abs()
        else:
            mad = features.groupby("subject_id")[col].transform(lambda s: np.nanmedian(np.abs(s - np.nanmedian(s))))
            std = features.groupby("subject_id")[col].transform("std").fillna(0.0)
            scale = pd.concat([mad, std / 1.4826, pd.Series(1.0, index=features.index)], axis=1).max(axis=1)
            additions[f"{col}_subdev"] = features[col] - center
            additions[f"{col}_subrz"] = ((features[col] - center) / scale).clip(-20.0, 20.0)

    roll_cols = [
        c
        for c in base_cols
        if any(token in c for token in ["device_off", "coverage", "profile_", "proto_min", "proto_margin"])
    ]
    for window in ROLL_WINDOWS:
        for col in roll_cols:
            shifted = features.groupby("subject_id")[col].shift(1)
            roll = shifted.groupby(features["subject_id"]).rolling(window, min_periods=2).mean().reset_index(level=0, drop=True)
            delta = features[col] - roll
            additions[f"{col}_past{window}_delta"] = delta.fillna(0.0)
            additions[f"{col}_past{window}_abs_delta"] = delta.abs().fillna(0.0)
    return pd.concat([features, pd.DataFrame(additions, index=features.index)], axis=1)


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
    rows = load_rows(args.train_path, args.sample_path)
    grid = pd.read_parquet(args.grid_path)
    daily, profiles, flat_profiles = profile_rows(grid)
    features = rows.merge(daily, on=KEY_COLUMNS, how="left", validate="one_to_one")
    features = add_baseline_distances(features, profiles)
    features = add_prototype_distances(features, flat_profiles, args.n_clusters, args.seed)
    features = add_subject_and_rolling(features)
    keep_cols = KEY_COLUMNS + sorted(
        [c for c in features.columns if c.startswith("z_crp_") and pd.api.types.is_numeric_dtype(features[c])]
    )
    features = features[keep_cols].replace([np.inf, -np.inf], 0.0).fillna(0.0)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    features.to_parquet(output, index=False)

    best = pd.read_parquet(args.best).copy()
    best["subject_id"] = best["subject_id"].astype(str)
    best["lifelog_date"] = pd.to_datetime(best["lifelog_date"]).dt.strftime("%Y-%m-%d")
    best_cols = [c for c in best.columns if c.startswith("z_")]
    additive = best[KEY_COLUMNS + best_cols].merge(features, on=KEY_COLUMNS, how="inner", validate="one_to_one")
    additive_output = Path(args.additive_output)
    additive_output.parent.mkdir(parents=True, exist_ok=True)
    additive.to_parquet(additive_output, index=False)

    feature_cols = [c for c in features.columns if c not in KEY_COLUMNS]
    stats = pd.DataFrame(
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
        "n_clusters": int(args.n_clusters),
        "profile_signals": PROFILE_SIGNALS,
        "hypothesis": "S4 coverage/no-wear signal may be a coarse daily rhythm/prototype deviation rather than a sleep-boundary episode.",
    }
    output.with_suffix(".report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    output.with_suffix(".report.md").write_text(
        "\n".join(
            [
                "# Coverage Rhythm Prototype Latents",
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
                dataframe_to_markdown(stats.head(60)),
            ]
        ),
        encoding="utf-8",
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build daily coverage/no-wear rhythm prototype latents.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--grid-path", default="artifacts/multires_30min_event_hybrid_grid.parquet")
    parser.add_argument("--best", default="artifacts/domain_best_late_fusion_v1.parquet")
    parser.add_argument("--output", default="artifacts/domain_coverage_rhythm_prototype_v1.parquet")
    parser.add_argument("--additive-output", default="artifacts/domain_best_plus_coverage_rhythm_prototype_v1.parquet")
    parser.add_argument("--n-clusters", type=int, default=8)
    parser.add_argument("--seed", type=int, default=2026)
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
