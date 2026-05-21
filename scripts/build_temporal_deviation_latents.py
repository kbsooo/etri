from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


KEY_COLUMNS = ["subject_id", "lifelog_date"]


def normalize_latent(path: Path) -> pd.DataFrame:
    frame = pd.read_parquet(path).copy()
    frame["subject_id"] = frame["subject_id"].astype(str)
    frame["lifelog_date"] = pd.to_datetime(frame["lifelog_date"]).dt.strftime("%Y-%m-%d")
    return frame.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True)


def z_columns(frame: pd.DataFrame) -> list[str]:
    cols = [col for col in frame.columns if col.startswith("z_")]
    if not cols:
        raise ValueError("No z_* latent columns found")
    return cols


def safe_norm(x: np.ndarray) -> np.ndarray:
    return np.linalg.norm(x, axis=1)


def cosine_to_center(values: np.ndarray, center: np.ndarray) -> np.ndarray:
    dot = (values * center).sum(axis=1)
    denom = np.maximum(np.linalg.norm(values, axis=1) * np.linalg.norm(center, axis=1), 1e-8)
    return dot / denom


def centered_stats(
    values: np.ndarray,
    dates: np.ndarray,
    idx: int,
    window: int,
    direction: str,
) -> tuple[np.ndarray, int]:
    current_date = dates[idx]
    if direction == "past":
        mask = (dates < current_date) & (dates >= current_date - np.timedelta64(window, "D"))
    elif direction == "future":
        mask = (dates > current_date) & (dates <= current_date + np.timedelta64(window, "D"))
    else:
        raise ValueError(f"Unknown direction: {direction}")
    if not mask.any():
        return np.full(values.shape[1], np.nan, dtype=float), 0
    return np.nanmedian(values[mask], axis=0), int(mask.sum())


def build_features(frame: pd.DataFrame, windows: list[int]) -> pd.DataFrame:
    z_cols = z_columns(frame)
    rows = []
    for _, group in frame.groupby("subject_id", sort=False):
        group = group.sort_values("lifelog_date").reset_index(drop=True)
        values = group[z_cols].to_numpy(float)
        dates = pd.to_datetime(group["lifelog_date"]).to_numpy(dtype="datetime64[D]")
        subject_center = np.nanmedian(values, axis=0)
        subject_center = np.nan_to_num(subject_center, nan=0.0)
        subject_center_rows = np.tile(subject_center, (len(group), 1))
        base_dev = values - subject_center_rows
        for i, row in group.iterrows():
            out = {col: row[col] for col in KEY_COLUMNS}
            current = values[i : i + 1]
            current_dev = base_dev[i : i + 1]
            out["subject_center_l2"] = float(safe_norm(current_dev)[0])
            out["subject_center_cosine"] = float(cosine_to_center(current, subject_center_rows[i : i + 1])[0])
            for window in windows:
                past, past_n = centered_stats(values, dates, i, window, "past")
                future, future_n = centered_stats(values, dates, i, window, "future")
                for prefix, center, count in [
                    (f"past{window}", past, past_n),
                    (f"future{window}", future, future_n),
                ]:
                    center_row = center[None, :]
                    diff = current - center_row
                    out[f"{prefix}_n"] = float(count)
                    out[f"{prefix}_l2"] = float(safe_norm(diff)[0]) if count else np.nan
                    out[f"{prefix}_cosine"] = float(cosine_to_center(current, center_row)[0]) if count else np.nan
                    out[f"{prefix}_signed_mean"] = float(np.nanmean(diff)) if count else np.nan
                    out[f"{prefix}_abs_mean"] = float(np.nanmean(np.abs(diff))) if count else np.nan
                if past_n and future_n:
                    past_diff = current - past[None, :]
                    future_diff = current - future[None, :]
                    out[f"recovery{window}_l2_delta"] = float(safe_norm(future_diff)[0] - safe_norm(past_diff)[0])
                    out[f"recovery{window}_abs_delta"] = float(np.nanmean(np.abs(future_diff)) - np.nanmean(np.abs(past_diff)))
                    out[f"trajectory{window}_center_l2"] = float(np.linalg.norm(future - past))
                    out[f"trajectory{window}_alignment"] = float(cosine_to_center(current - past[None, :], future[None, :] - past[None, :])[0])
                else:
                    out[f"recovery{window}_l2_delta"] = np.nan
                    out[f"recovery{window}_abs_delta"] = np.nan
                    out[f"trajectory{window}_center_l2"] = np.nan
                    out[f"trajectory{window}_alignment"] = np.nan
            rows.append(out)
    return pd.DataFrame(rows)


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
    source = normalize_latent(Path(args.input))
    windows = [int(w) for w in args.windows]
    features = build_features(source, windows)
    rename = {
        col: f"z_td_{col}"
        for col in features.columns
        if col not in KEY_COLUMNS
    }
    features = features.rename(columns=rename)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    features.to_parquet(output, index=False)
    feature_cols = [c for c in features.columns if c not in KEY_COLUMNS]
    coverage = pd.DataFrame(
        [
            {
                "feature": col,
                "non_null_rate": float(features[col].notna().mean()),
                "mean": float(features[col].mean(skipna=True)),
                "std": float(features[col].std(skipna=True)),
            }
            for col in feature_cols
        ]
    ).sort_values(["non_null_rate", "feature"], ascending=[True, True])
    report = {
        "input": args.input,
        "output": str(output),
        "rows": int(len(features)),
        "feature_count": int(len(feature_cols)),
        "windows": windows,
        "lowest_coverage": coverage.head(20).to_dict(orient="records"),
    }
    report_path = output.with_suffix(".report.json")
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    md = [
        "# Temporal Deviation Latents",
        "",
        "## Purpose",
        "",
        "Build target-free multi-day novelty, recovery, and trajectory features from the current best day latent.",
        "",
        f"- Input: `{args.input}`",
        f"- Output: `{output}`",
        f"- Rows: `{len(features)}`",
        f"- Feature count: `{len(feature_cols)}`",
        f"- Windows: `{', '.join(str(w) for w in windows)}`",
        "",
        "## Lowest Coverage Features",
        "",
        dataframe_to_markdown(coverage.head(20)),
    ]
    output.with_suffix(".report.md").write_text("\n".join(md), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build multi-day temporal deviation features from a latent parquet.")
    parser.add_argument("--input", default="artifacts/domain_best_late_fusion_v1.parquet")
    parser.add_argument("--output", default="artifacts/domain_temporal_deviation_v1.parquet")
    parser.add_argument("--windows", type=int, nargs="+", default=[3, 7, 14, 28])
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
