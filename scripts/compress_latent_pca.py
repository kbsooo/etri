from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


KEY_COLUMNS = ["subject_id", "lifelog_date"]


def normalize_keys(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["subject_id"] = out["subject_id"].astype(str)
    out["lifelog_date"] = pd.to_datetime(out["lifelog_date"]).dt.strftime("%Y-%m-%d")
    return out


def run(args: argparse.Namespace) -> None:
    source_path = Path(args.source)
    source = normalize_keys(pd.read_parquet(source_path))
    z_cols = [col for col in source.columns if col.startswith("z_")]
    if not z_cols:
        raise ValueError(f"No z_* columns in {source_path}")
    if source[KEY_COLUMNS].duplicated().any():
        raise ValueError(f"Duplicate day keys in {source_path}")

    n_components = min(args.n_components, len(z_cols), len(source))
    model = make_pipeline(
        SimpleImputer(strategy="median", keep_empty_features=True),
        StandardScaler(),
        PCA(n_components=n_components, random_state=args.seed),
    )
    z = model.fit_transform(source[z_cols]).astype(np.float32)
    pca = model.named_steps["pca"]

    out = source[KEY_COLUMNS].copy()
    for i in range(z.shape[1]):
        out[f"z_pca_{i:02d}"] = z[:, i]

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(output_path, index=False)

    report = {
        "source": str(source_path),
        "output": str(output_path),
        "rows": int(len(source)),
        "source_z_cols": int(len(z_cols)),
        "n_components": int(n_components),
        "explained_variance_ratio_sum": float(np.sum(pca.explained_variance_ratio_)),
        "explained_variance_ratio": [float(v) for v in pca.explained_variance_ratio_],
        "seed": int(args.seed),
    }
    report_path = output_path.with_suffix(".report.json")
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    md = [
        "# Latent PCA Compression",
        "",
        "## Purpose",
        "",
        "Compress a high-dimensional unlabeled latent table into a small orthogonal coordinate system before probing. No labels are used.",
        "",
        "## Source",
        "",
        f"- Source: `{source_path}`",
        f"- Source z columns: `{len(z_cols)}`",
        f"- Rows: `{len(source)}`",
        "",
        "## Output",
        "",
        f"- Output: `{output_path}`",
        f"- Components: `{n_components}`",
        f"- Explained variance ratio sum: `{report['explained_variance_ratio_sum']:.6f}`",
    ]
    output_path.with_suffix(".report.md").write_text("\n".join(md), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compress z_* latent columns with unsupervised PCA.")
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--n-components", type=int, default=32)
    parser.add_argument("--seed", type=int, default=42)
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
