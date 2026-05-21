from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


KEY_COLUMNS = ["subject_id", "lifelog_date"]


def z_columns(frame: pd.DataFrame) -> list[str]:
    cols = [col for col in frame.columns if col.startswith("z_")]
    if not cols:
        raise ValueError("No z_* columns found")
    return cols


def softmax_negative_distance(distances: np.ndarray, temperature: float) -> np.ndarray:
    scaled = -distances / max(temperature, 1e-6)
    scaled = scaled - scaled.max(axis=1, keepdims=True)
    exp = np.exp(scaled)
    return exp / np.maximum(exp.sum(axis=1, keepdims=True), 1e-12)


def entropy(prob: np.ndarray) -> np.ndarray:
    return -(prob * np.log(np.maximum(prob, 1e-12))).sum(axis=1)


def fit_kmeans_features(values: np.ndarray, prefix: str, ks: list[int], random_state: int) -> pd.DataFrame:
    rows: dict[str, np.ndarray] = {}
    pipeline = make_pipeline(
        SimpleImputer(strategy="median", keep_empty_features=True),
        StandardScaler(),
    )
    x = pipeline.fit_transform(values)
    for k in ks:
        model = KMeans(n_clusters=k, random_state=random_state, n_init=30)
        labels = model.fit_predict(x)
        distances = model.transform(x)
        sorted_dist = np.sort(distances, axis=1)
        temp = float(np.nanmedian(sorted_dist[:, 0])) if len(sorted_dist) else 1.0
        probs = softmax_negative_distance(distances, temp)
        rows[f"z_{prefix}_k{k}_label"] = labels.astype(float)
        rows[f"z_{prefix}_k{k}_min_dist"] = sorted_dist[:, 0]
        rows[f"z_{prefix}_k{k}_second_dist"] = sorted_dist[:, 1] if k > 1 else sorted_dist[:, 0]
        rows[f"z_{prefix}_k{k}_dist_margin"] = rows[f"z_{prefix}_k{k}_second_dist"] - rows[f"z_{prefix}_k{k}_min_dist"]
        rows[f"z_{prefix}_k{k}_soft_entropy"] = entropy(probs)
        for cluster in range(k):
            rows[f"z_{prefix}_k{k}_dist_c{cluster}"] = distances[:, cluster]
            rows[f"z_{prefix}_k{k}_prob_c{cluster}"] = probs[:, cluster]
    return pd.DataFrame(rows)


def build_subject_centered(frame: pd.DataFrame, cols: list[str]) -> np.ndarray:
    global_center = frame[cols].median(axis=0, skipna=True).fillna(0.0)
    centers = frame.groupby("subject_id")[cols].median()
    center_rows = []
    for subject in frame["subject_id"].astype(str):
        center_rows.append(centers.loc[subject].to_numpy(float) if subject in centers.index else global_center.to_numpy(float))
    return frame[cols].to_numpy(float) - np.vstack(center_rows)


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
    source = pd.read_parquet(args.input).copy()
    source["subject_id"] = source["subject_id"].astype(str)
    source["lifelog_date"] = pd.to_datetime(source["lifelog_date"]).dt.strftime("%Y-%m-%d")
    source = source.sort_values(KEY_COLUMNS).reset_index(drop=True)
    cols = z_columns(source)
    ks = [int(k) for k in args.k]

    abs_features = fit_kmeans_features(source[cols].to_numpy(float), "proto_abs", ks, args.random_state)
    centered_values = build_subject_centered(source, cols)
    dev_features = fit_kmeans_features(centered_values, "proto_dev", ks, args.random_state + 17)
    out = pd.concat([source[KEY_COLUMNS].reset_index(drop=True), abs_features, dev_features], axis=1)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(output, index=False)
    feature_cols = [c for c in out.columns if c not in KEY_COLUMNS]
    coverage = pd.DataFrame(
        [
            {
                "feature": col,
                "non_null_rate": float(out[col].notna().mean()),
                "mean": float(out[col].mean(skipna=True)),
                "std": float(out[col].std(skipna=True)),
            }
            for col in feature_cols
        ]
    )
    report = {
        "input": args.input,
        "output": str(output),
        "rows": int(len(out)),
        "feature_count": int(len(feature_cols)),
        "k": ks,
        "source_column_count": int(len(cols)),
    }
    output.with_suffix(".report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = [
        "# Prototype State Latents",
        "",
        "## Purpose",
        "",
        "Build unsupervised global and subject-centered prototype distances over a latent state space.",
        "",
        f"- Input: `{args.input}`",
        f"- Output: `{output}`",
        f"- Rows: `{len(out)}`",
        f"- Feature count: `{len(feature_cols)}`",
        f"- K values: `{', '.join(str(k) for k in ks)}`",
        "",
        "## Feature Coverage",
        "",
        dataframe_to_markdown(coverage.head(20)),
    ]
    output.with_suffix(".report.md").write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build unsupervised prototype-state features from a latent parquet.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--k", type=int, nargs="+", default=[3, 5, 8])
    parser.add_argument("--random-state", type=int, default=42)
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
