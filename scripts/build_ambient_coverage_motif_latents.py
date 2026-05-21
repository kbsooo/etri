from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


KEY_COLUMNS = ["subject_id", "lifelog_date"]
ROLL_WINDOWS = [3, 7, 14, 28]
STATE_SELECT_PATTERNS = [
    "light",
    "mlight",
    "wlight",
    "amb_",
    "coverage",
    "no_wear",
    "low_coverage",
    "present_hr",
    "present_pedo",
    "present_gps",
    "present_phone",
    "present_light",
    "present_ambience",
    "missing_run",
    "missing_until_next",
    "phone_nowear",
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
    p = x / total
    return safe_float(float(-(p * np.log(np.maximum(p, 1e-12))).sum()))


def transition_count(states: np.ndarray) -> int:
    if len(states) <= 1:
        return 0
    return int((states[1:] != states[:-1]).sum())


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


def cosine_dist(a: np.ndarray, b: np.ndarray) -> float:
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom <= 1e-8:
        return 0.0
    return safe_float(1.0 - float(np.dot(a, b) / denom))


def state_columns(state: pd.DataFrame) -> list[str]:
    cols = []
    for col in state.columns:
        low = col.lower()
        if col in KEY_COLUMNS:
            continue
        if not pd.api.types.is_numeric_dtype(state[col]):
            continue
        if any(pattern in low for pattern in STATE_SELECT_PATTERNS):
            cols.append(col)
    return sorted(cols)


def add_state_feature_block(features: pd.DataFrame, state: pd.DataFrame) -> pd.DataFrame:
    state = state.copy()
    state["subject_id"] = state["subject_id"].astype(str)
    state["lifelog_date"] = pd.to_datetime(state["lifelog_date"]).dt.strftime("%Y-%m-%d")
    cols = state_columns(state)
    slim = state[KEY_COLUMNS + cols].copy()
    renamed = {col: f"z_acm_state_{col}" for col in cols}
    slim = slim.rename(columns=renamed)
    return features.merge(slim, on=KEY_COLUMNS, how="left")


def token_state_vector(group: pd.DataFrame) -> tuple[dict[str, float], np.ndarray]:
    group = group.sort_values("tok")
    n = len(group)
    if n == 0:
        return {}, np.zeros(64, dtype=float)
    mlight = np.nan_to_num(group.get("mlight_mean", pd.Series(np.zeros(n))).to_numpy(float), nan=0.0)
    wlight = np.nan_to_num(group.get("wlight_mean", pd.Series(np.zeros(n))).to_numpy(float), nan=0.0)
    amb_silence = np.nan_to_num(group.get("amb_silence", pd.Series(np.zeros(n))).to_numpy(float), nan=0.0)
    amb_speech = np.nan_to_num(group.get("amb_speech", pd.Series(np.zeros(n))).to_numpy(float), nan=0.0)
    amb_music = np.nan_to_num(group.get("amb_music", pd.Series(np.zeros(n))).to_numpy(float), nan=0.0)
    no_wear = np.nan_to_num(group.get("ev_no_wear", pd.Series(np.zeros(n))).to_numpy(float), nan=0.0) > 0.5
    low_cov = np.nan_to_num(group.get("ev_low_coverage", pd.Series(np.zeros(n))).to_numpy(float), nan=0.0) > 0.5
    phone = np.nan_to_num(group.get("ev_phone_active", pd.Series(np.zeros(n))).to_numpy(float), nan=0.0) > 0.5
    moving = np.nan_to_num(group.get("ev_moving", pd.Series(np.zeros(n))).to_numpy(float), nan=0.0) > 0.5
    coverage = np.nan_to_num(group.get("sensor_coverage_n", pd.Series(np.zeros(n))).to_numpy(float), nan=0.0)

    light_q = np.quantile(mlight + wlight, [0.35, 0.75]) if n >= 4 else [0.0, 1.0]
    light_state = np.digitize(mlight + wlight, light_q)
    ambient_state = np.argmax(np.vstack([amb_silence, amb_speech, amb_music, np.ones(n) * 0.05]), axis=0)
    coverage_state = np.where(no_wear, 2, np.where(low_cov, 1, 0))
    behavior_state = np.where(phone & ~moving, 1, np.where(moving & ~phone, 2, np.where(phone & moving, 3, 0)))
    state = light_state + 3 * ambient_state + 12 * coverage_state + 36 * (behavior_state > 0).astype(int)
    counts = np.bincount(np.clip(state, 0, 63), minlength=64).astype(float)
    motif = counts / max(float(counts.sum()), 1.0)

    out = {
        "z_acm_light_entropy": entropy(mlight + wlight),
        "z_acm_light_transition_count": float(transition_count(light_state)),
        "z_acm_bright_ratio": safe_float(float(((mlight + wlight) > light_q[1]).mean())),
        "z_acm_dark_ratio": safe_float(float(((mlight + wlight) <= light_q[0]).mean())),
        "z_acm_ambient_entropy": entropy(np.bincount(ambient_state, minlength=4).astype(float)),
        "z_acm_ambient_transition_count": float(transition_count(ambient_state)),
        "z_acm_silence_ratio": safe_float(float((ambient_state == 0).mean())),
        "z_acm_speech_music_ratio": safe_float(float(((ambient_state == 1) | (ambient_state == 2)).mean())),
        "z_acm_no_wear_ratio": safe_float(float(no_wear.mean())),
        "z_acm_low_coverage_ratio": safe_float(float(low_cov.mean())),
        "z_acm_no_wear_longest_run": float(longest_run(no_wear)),
        "z_acm_low_coverage_longest_run": float(longest_run(low_cov)),
        "z_acm_coverage_mean": safe_float(float(coverage.mean())),
        "z_acm_coverage_std": safe_float(float(coverage.std())),
        "z_acm_coverage_transition_count": float(transition_count(coverage_state)),
        "z_acm_phone_nowear_ratio": safe_float(float((phone & no_wear).mean())),
        "z_acm_phone_lowcov_ratio": safe_float(float((phone & low_cov).mean())),
        "z_acm_motif_entropy": entropy(motif),
        "z_acm_motif_transition_count": float(transition_count(state)),
        "z_acm_night_no_wear_ratio": safe_float(float(no_wear[:12].mean())),
        "z_acm_night_low_coverage_ratio": safe_float(float(low_cov[:12].mean())),
        "z_acm_night_bright_ratio": safe_float(float(((mlight[:12] + wlight[:12]) > light_q[1]).mean())),
        "z_acm_evening_bright_ratio": safe_float(float(((mlight[36:] + wlight[36:]) > light_q[1]).mean())),
        "z_acm_night_silence_ratio": safe_float(float((ambient_state[:12] == 0).mean())),
    }
    for idx, value in enumerate(motif):
        if value > 0:
            out[f"z_acm_motif_{idx:02d}"] = safe_float(value)
    return out, motif


def add_grid_motifs(features: pd.DataFrame, grid: pd.DataFrame) -> pd.DataFrame:
    grid = grid.copy()
    grid["subject_id"] = grid["subject_id"].astype(str)
    grid["date"] = pd.to_datetime(grid["date"]).dt.strftime("%Y-%m-%d")
    rows = []
    motifs = {}
    for (subject, date), group in grid.groupby(["subject_id", "date"], sort=True):
        out, motif = token_state_vector(group)
        out.update({"subject_id": subject, "lifelog_date": date})
        rows.append(out)
        motifs[(subject, date)] = motif
    motif_frame = pd.DataFrame(rows).fillna(0.0)
    merged = features.merge(motif_frame, on=KEY_COLUMNS, how="left")

    global_motif = np.nanmean(np.vstack(list(motifs.values())), axis=0) if motifs else np.zeros(64, dtype=float)
    subject_baselines: dict[str, np.ndarray] = {}
    for subject in merged["subject_id"].astype(str).unique():
        parts = [m for (s, _), m in motifs.items() if s == subject]
        subject_baselines[subject] = np.nanmean(np.vstack(parts), axis=0) if parts else global_motif

    dists = []
    global_dists = []
    for _, row in merged.iterrows():
        key = (str(row["subject_id"]), row["lifelog_date"])
        motif = motifs.get(key, np.zeros(64, dtype=float))
        dists.append(cosine_dist(motif, subject_baselines.get(str(row["subject_id"]), global_motif)))
        global_dists.append(cosine_dist(motif, global_motif))
    merged["z_acm_motif_subject_cosine_dist"] = dists
    merged["z_acm_motif_global_cosine_dist"] = global_dists
    return merged


def add_deviation_and_rolling(features: pd.DataFrame) -> pd.DataFrame:
    features = features.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True)
    additions = {}
    base_cols = [c for c in features.columns if c.startswith("z_acm_")]
    for col in base_cols:
        if not pd.api.types.is_numeric_dtype(features[col]):
            continue
        center = features.groupby("subject_id")[col].transform("median")
        mad = features.groupby("subject_id")[col].transform(lambda s: np.nanmedian(np.abs(s - np.nanmedian(s))) + 1e-6)
        additions[f"{col}_subdev"] = features[col] - center
        additions[f"{col}_subrz"] = (features[col] - center) / mad

    roll_cols = [
        c
        for c in [
            "z_acm_no_wear_ratio",
            "z_acm_low_coverage_ratio",
            "z_acm_coverage_mean",
            "z_acm_light_entropy",
            "z_acm_bright_ratio",
            "z_acm_dark_ratio",
            "z_acm_ambient_entropy",
            "z_acm_silence_ratio",
            "z_acm_motif_subject_cosine_dist",
            "z_acm_motif_global_cosine_dist",
            "z_acm_night_no_wear_ratio",
            "z_acm_night_bright_ratio",
        ]
        if c in features
    ]
    for window in ROLL_WINDOWS:
        for col in roll_cols:
            shifted = features.groupby("subject_id")[col].shift(1)
            roll = shifted.groupby(features["subject_id"]).rolling(window, min_periods=2).mean().reset_index(level=0, drop=True)
            roll_std = shifted.groupby(features["subject_id"]).rolling(window, min_periods=2).std().reset_index(level=0, drop=True)
            additions[f"{col}_past{window}_delta"] = (features[col] - roll).fillna(0.0)
            additions[f"{col}_past{window}_abs_delta"] = (features[col] - roll).abs().fillna(0.0)
            additions[f"{col}_past{window}_volatility"] = roll_std.fillna(0.0)
    return pd.concat([features, pd.DataFrame(additions, index=features.index)], axis=1)


def build_features(args: argparse.Namespace) -> pd.DataFrame:
    rows = load_rows(args.train_path, args.sample_path)
    state = pd.read_parquet(args.state_features)
    grid = pd.read_parquet(args.grid_path)
    features = rows.copy()
    features = add_state_feature_block(features, state)
    features = add_grid_motifs(features, grid)
    features = features.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    features = add_deviation_and_rolling(features)
    keep = KEY_COLUMNS + sorted([c for c in features.columns if c.startswith("z_acm_")])
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
            "S1/S3 may depend on non-random no-wear and low-coverage episodes.",
            "Ambient/light stability may capture sleep environment and daytime regularity missed by timing features.",
            "Day-state motif distance may reveal unusual multimodal days without using labels.",
        ],
    }
    output.with_suffix(".report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    md = [
        "# Ambient Coverage Motif Latents",
        "",
        "## Purpose",
        "",
        "Build ambient/light stability, sensor coverage/no-wear semantics, and day-state motif features.",
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
    parser = argparse.ArgumentParser(description="Build ambient/light, coverage/no-wear, and motif features.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--state-features", default="artifacts/domain_state_features_v1.parquet")
    parser.add_argument("--grid-path", default="artifacts/multires_30min_event_hybrid_grid.parquet")
    parser.add_argument("--output", default="artifacts/domain_ambient_coverage_motif_v1.parquet")
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
