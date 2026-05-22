from __future__ import annotations

import argparse
import json
import re
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler


KEY_COLUMNS = ["subject_id", "lifelog_date"]

DEFAULT_BLOCKS = {
    "q1_boundary": "artifacts/domain_boundary_objective_target_map_v1.parquet",
    "q2_sleep_rolling": "artifacts/domain_sleep_consensus_compact_rolling_v1.parquet",
    "q3_mobility": "artifacts/domain_mobility_constriction_v1.parquet",
    "q3_recovery": "artifacts/domain_causal_chain_recovery_v1.parquet",
    "s1_wake_recovery": "artifacts/domain_wake_activation_inertia_sleep_recovery_interaction_v1.parquet",
    "s2_sleep_consensus": "artifacts/domain_sleep_consensus_purity_subject_relative_only_v1.parquet",
    "s3_onset_settle": "artifacts/domain_sleep_onset_transition_micro_subject_relative_only_v1.parquet",
    "s4_coverage_rhythm": "artifacts/domain_routine_regularity_coverage_rhythm_v1.parquet",
    "opportunity": "artifacts/domain_causal_chain_opportunity_v1.parquet",
    "energy_recovery": "artifacts/domain_energy_fragmentation_recovery_slope_v1.parquet",
}


def normalize(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["subject_id"] = out["subject_id"].astype(str)
    out["lifelog_date"] = pd.to_datetime(out["lifelog_date"]).dt.strftime("%Y-%m-%d")
    return out


def clean_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_")[-52:]


def selected_z_columns(frame: pd.DataFrame, cap: int) -> list[str]:
    cols = [col for col in frame.columns if col.startswith("z_") and not col.startswith("z_best")]
    if not cols:
        cols = [col for col in frame.columns if col.startswith("z_")]
    variances = frame[cols].replace([np.inf, -np.inf], np.nan).var(axis=0, skipna=True).fillna(0.0)
    return variances.sort_values(ascending=False).head(cap).index.tolist()


def read_block(name: str, path: Path, cap: int) -> tuple[pd.DataFrame, list[str]]:
    frame = normalize(pd.read_parquet(path))
    cols = selected_z_columns(frame, cap)
    renamed = {col: f"{name}__{col}" for col in cols}
    return frame[KEY_COLUMNS + cols].rename(columns=renamed), [renamed[col] for col in cols]


def scale_frame(frame: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    values = SimpleImputer(strategy="median", keep_empty_features=True).fit_transform(frame[cols])
    scaled = StandardScaler().fit_transform(values)
    return pd.DataFrame(scaled, columns=cols, index=frame.index)


def add_block_state(out: dict[str, np.ndarray], name: str, block: pd.DataFrame, pca_dim: int, keep_top: int) -> list[str]:
    arr = block.to_numpy(float)
    out[f"z_psg_{name}_mean"] = np.nanmean(arr, axis=1)
    out[f"z_psg_{name}_std"] = np.nanstd(arr, axis=1)
    out[f"z_psg_{name}_abs_mean"] = np.nanmean(np.abs(arr), axis=1)
    out[f"z_psg_{name}_pos_mean"] = np.nanmean(np.maximum(arr, 0.0), axis=1)
    out[f"z_psg_{name}_neg_mean"] = np.nanmean(np.minimum(arr, 0.0), axis=1)
    out[f"z_psg_{name}_max"] = np.nanmax(arr, axis=1)
    out[f"z_psg_{name}_min"] = np.nanmin(arr, axis=1)
    out[f"z_psg_{name}_range"] = np.nanmax(arr, axis=1) - np.nanmin(arr, axis=1)

    n_components = min(pca_dim, block.shape[1], max(1, block.shape[0] - 1))
    pca_values = PCA(n_components=n_components, random_state=0).fit_transform(np.nan_to_num(arr, nan=0.0))
    for i in range(n_components):
        out[f"z_psg_{name}_pca{i:02d}"] = pca_values[:, i]

    top_cols = block.var(axis=0).sort_values(ascending=False).head(keep_top).index.tolist()
    for i, col in enumerate(top_cols):
        out[f"z_psg_{name}_top{i:02d}_{clean_name(col)}"] = block[col].to_numpy(float)
    return [f"z_psg_{name}_mean", f"z_psg_{name}_abs_mean", f"z_psg_{name}_pca00"]


def add_subject_relative_summaries(out_df: pd.DataFrame) -> pd.DataFrame:
    z_cols = [col for col in out_df.columns if col.startswith("z_psg_")]
    additions: dict[str, np.ndarray] = {}
    for col in z_cols:
        center = out_df.groupby("subject_id")[col].transform("median")
        mad = (out_df[col] - center).abs().groupby(out_df["subject_id"]).transform("median").replace(0, np.nan)
        additions[f"{col}_subdev"] = (out_df[col] - center).fillna(0.0).to_numpy(float)
        additions[f"{col}_subrz"] = ((out_df[col] - center) / mad.fillna(mad.median())).replace([np.inf, -np.inf], 0.0).fillna(0.0).to_numpy(float)
    return pd.concat([out_df, pd.DataFrame(additions)], axis=1)


def add_pairwise_gates(out: dict[str, np.ndarray], block_handles: dict[str, list[str]], base_values: dict[str, np.ndarray]) -> None:
    for left, right in combinations(block_handles, 2):
        l_mean = base_values[f"z_psg_{left}_mean"]
        r_mean = base_values[f"z_psg_{right}_mean"]
        l_abs = base_values[f"z_psg_{left}_abs_mean"]
        r_abs = base_values[f"z_psg_{right}_abs_mean"]
        out[f"z_psg_pair_{left}__{right}_signed_product"] = l_mean * r_mean
        out[f"z_psg_pair_{left}__{right}_load_product"] = l_abs * r_abs
        out[f"z_psg_pair_{left}__{right}_load_gap"] = l_abs - r_abs
        out[f"z_psg_pair_{left}__{right}_same_direction"] = np.sign(l_mean) * np.sign(r_mean)


def add_prototypes(out: dict[str, np.ndarray], summary: pd.DataFrame, ks: list[int]) -> None:
    matrix = SimpleImputer(strategy="median", keep_empty_features=True).fit_transform(summary)
    matrix = StandardScaler().fit_transform(matrix)
    for k in ks:
        if k >= len(summary):
            continue
        km = KMeans(n_clusters=k, n_init=20, random_state=100 + k)
        labels = km.fit_predict(matrix)
        distances = km.transform(matrix)
        min_dist = distances.min(axis=1)
        out[f"z_psg_proto{k}_min_dist"] = min_dist
        out[f"z_psg_proto{k}_margin"] = np.partition(distances, 1, axis=1)[:, 1] - min_dist
        out[f"z_psg_proto{k}_label_norm"] = labels.astype(float) / max(k - 1, 1)
        for i in range(k):
            out[f"z_psg_proto{k}_dist_{i:02d}"] = distances[:, i]


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
    specs = DEFAULT_BLOCKS.copy()
    for item in args.block:
        if "=" not in item:
            raise ValueError(f"Block override must be name=path, got {item}")
        name, path = item.split("=", 1)
        specs[name] = path

    merged: pd.DataFrame | None = None
    block_cols: dict[str, list[str]] = {}
    for name, raw_path in specs.items():
        path = Path(raw_path)
        if not path.exists():
            raise FileNotFoundError(path)
        block, cols = read_block(name, path, args.cap_per_block)
        merged = block if merged is None else merged.merge(block, on=KEY_COLUMNS, how="inner", validate="one_to_one")
        block_cols[name] = cols
    if merged is None:
        raise ValueError("No source blocks loaded")

    scaled_blocks = {name: scale_frame(merged, cols) for name, cols in block_cols.items()}
    out_cols: dict[str, np.ndarray] = {}
    handles: dict[str, list[str]] = {}
    for name, block in scaled_blocks.items():
        handles[name] = add_block_state(out_cols, name, block, args.pca_dim, args.keep_top)
    base_values = dict(out_cols)
    add_pairwise_gates(out_cols, handles, base_values)
    summary_cols = [col for col in out_cols if col.endswith("_mean") or col.endswith("_abs_mean") or col.endswith("_pca00")]
    add_prototypes(out_cols, pd.DataFrame({col: out_cols[col] for col in summary_cols}), args.prototype_k)

    out = pd.concat([merged[KEY_COLUMNS].reset_index(drop=True), pd.DataFrame(out_cols)], axis=1)
    out = add_subject_relative_summaries(out)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(output, index=False)

    best = normalize(pd.read_parquet(args.best))
    best_cols = [col for col in best.columns if col.startswith("z_")]
    additive = best[KEY_COLUMNS + best_cols].merge(out, on=KEY_COLUMNS, how="inner", validate="one_to_one")
    additive_output = Path(args.additive_output)
    additive_output.parent.mkdir(parents=True, exist_ok=True)
    additive.to_parquet(additive_output, index=False)

    block_summary = pd.DataFrame(
        [
            {
                "block": name,
                "source": specs[name],
                "selected_features": len(block_cols[name]),
            }
            for name in specs
        ]
    )
    feature_cols = [col for col in out.columns if col.startswith("z_")]
    report = {
        "output": str(output),
        "additive_output": str(additive_output),
        "rows": int(len(out)),
        "feature_count": int(len(feature_cols)),
        "blocks": block_summary.to_dict(orient="records"),
        "hypothesis": "Protected target experts should be encoded as low-dimensional state loads, conflicts, and prototypes so a decoder can gate them without ingesting every raw family column.",
    }
    output.with_suffix(".report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    stats = pd.DataFrame(
        {
            "feature": feature_cols,
            "mean": [float(out[col].mean(skipna=True)) for col in feature_cols],
            "std": [float(out[col].std(skipna=True)) for col in feature_cols],
        }
    )
    output.with_suffix(".report.md").write_text(
        "\n".join(
            [
                "# Protected State Gate Latents",
                "",
                "## Hypothesis",
                "",
                report["hypothesis"],
                "",
                f"- Output: `{output}`",
                f"- Additive output: `{additive_output}`",
                f"- Rows: `{len(out)}`",
                f"- Feature count: `{len(feature_cols)}`",
                "",
                "## Blocks",
                "",
                dataframe_to_markdown(block_summary),
                "",
                "## Feature Summary",
                "",
                dataframe_to_markdown(stats.head(80)),
            ]
        ),
        encoding="utf-8",
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build low-dimensional protected expert state/gate latents.")
    parser.add_argument("--best", default="artifacts/domain_best_late_fusion_v1.parquet")
    parser.add_argument("--output", default="artifacts/domain_protected_state_gate_v1.parquet")
    parser.add_argument("--additive-output", default="artifacts/domain_best_plus_protected_state_gate_v1.parquet")
    parser.add_argument("--cap-per-block", type=int, default=72)
    parser.add_argument("--pca-dim", type=int, default=3)
    parser.add_argument("--keep-top", type=int, default=6)
    parser.add_argument("--prototype-k", type=int, nargs="+", default=[4, 8, 12])
    parser.add_argument("--block", action="append", default=[])
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
