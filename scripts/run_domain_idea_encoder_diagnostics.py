from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import StratifiedKFold
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler


DEFAULT_VIEWS = [
    "full",
    "no_body",
    "no_phone",
    "no_gps_radio",
    "no_missingness",
    "no_event",
    "no_cross_modal",
    "only_body",
    "only_phone",
    "only_gps_radio",
    "only_missingness",
    "only_event",
    "only_cross_modal",
]


def load_tokens(path: Path) -> dict[str, np.ndarray]:
    arr = np.load(path, allow_pickle=True)
    return {key: arr[key] for key in arr.files}


def key_frame(tokens: dict[str, np.ndarray]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "subject_id": tokens["subject_id"].astype(str),
            "lifelog_date": tokens["lifelog_date"].astype(str),
        }
    )


def load_split(train_path: Path, sample_path: Path) -> pd.DataFrame:
    train = pd.read_csv(train_path)[["subject_id", "lifelog_date"]].copy()
    sample = pd.read_csv(sample_path)[["subject_id", "lifelog_date"]].copy()
    train["split"] = "train"
    sample["split"] = "sample"
    split = pd.concat([train, sample], ignore_index=True)
    split["subject_id"] = split["subject_id"].astype(str)
    split["lifelog_date"] = pd.to_datetime(split["lifelog_date"]).dt.strftime("%Y-%m-%d")
    return split


def selected_channel_indices(groups: np.ndarray, view: str) -> np.ndarray:
    groups_str = groups.astype(str)
    if view == "full":
        mask = np.ones(len(groups_str), dtype=bool)
    elif view.startswith("no_"):
        target = view.removeprefix("no_")
        mask = groups_str != target
    elif view.startswith("only_"):
        target = view.removeprefix("only_")
        mask = groups_str == target
    else:
        raise ValueError(f"Unknown view syntax: {view}")
    idx = np.flatnonzero(mask)
    if len(idx) == 0:
        raise ValueError(f"View {view} selected zero channels")
    return idx


def flatten_view(values: np.ndarray, mask: np.ndarray, idx: np.ndarray, include_mask: bool) -> np.ndarray:
    x_val = values[:, idx, :] * mask[:, idx, :]
    flat = x_val.reshape(values.shape[0], -1)
    if include_mask:
        flat = np.concatenate([flat, mask[:, idx, :].reshape(values.shape[0], -1)], axis=1)
    return np.nan_to_num(flat.astype(np.float32), nan=0.0, posinf=0.0, neginf=0.0)


def cosine_temporal_locality(z: np.ndarray, keys: pd.DataFrame) -> dict[str, float]:
    z_norm = z / np.maximum(np.linalg.norm(z, axis=1, keepdims=True), 1e-8)
    adjacent = []
    random_pairs = []
    rng = np.random.default_rng(2026)
    ordered = keys.reset_index(names="_idx").sort_values(["subject_id", "lifelog_date"])
    for _, group in ordered.groupby("subject_id", sort=False):
        idx = group["_idx"].to_numpy()
        if len(idx) > 1:
            adjacent.extend(float((z_norm[a] * z_norm[b]).sum()) for a, b in zip(idx[:-1], idx[1:]))
    for _ in range(max(100, len(adjacent))):
        a, b = rng.choice(len(keys), size=2, replace=False)
        random_pairs.append(float((z_norm[a] * z_norm[b]).sum()))
    return {
        "adjacent_cosine_mean": float(np.mean(adjacent)) if adjacent else float("nan"),
        "random_cosine_mean": float(np.mean(random_pairs)) if random_pairs else float("nan"),
        "temporal_locality_gap": float(np.mean(adjacent) - np.mean(random_pairs)) if adjacent and random_pairs else float("nan"),
    }


def nearest_neighbor_stats(z: np.ndarray, keys: pd.DataFrame) -> dict[str, float]:
    if len(z) < 3:
        return {"same_subject_nn_rate": float("nan"), "mean_neighbor_day_gap": float("nan")}
    nbrs = NearestNeighbors(n_neighbors=2, metric="cosine").fit(z)
    _, indices = nbrs.kneighbors(z)
    nn = indices[:, 1]
    dates = pd.to_datetime(keys["lifelog_date"])
    day_gap = np.abs((dates.iloc[nn].reset_index(drop=True) - dates.reset_index(drop=True)).dt.days.to_numpy())
    same_subject = keys["subject_id"].to_numpy() == keys["subject_id"].to_numpy()[nn]
    return {
        "same_subject_nn_rate": float(np.mean(same_subject)),
        "mean_neighbor_day_gap": float(np.mean(day_gap)),
    }


def subject_leakage_score(z: np.ndarray, subject_id: np.ndarray) -> float:
    z = StandardScaler().fit_transform(z)
    y = pd.Series(subject_id).astype("category").cat.codes.to_numpy()
    counts = pd.Series(y).value_counts()
    n_splits = int(min(5, counts.min()))
    if n_splits < 2:
        return float("nan")
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=2026)
    pred = np.zeros_like(y)
    for tr, va in skf.split(z, y):
        clf = LogisticRegression(max_iter=2000, C=0.3)
        clf.fit(z[tr], y[tr])
        pred[va] = clf.predict(z[va])
    return float(accuracy_score(y, pred))


def train_sample_shift(z: np.ndarray, keys: pd.DataFrame) -> dict[str, float]:
    train_mask = keys["split"].to_numpy() == "train"
    sample_mask = keys["split"].to_numpy() == "sample"
    if not train_mask.any() or not sample_mask.any():
        return {"train_sample_mean_l2": float("nan"), "train_sample_std_l2": float("nan")}
    train = z[train_mask]
    sample = z[sample_mask]
    return {
        "train_sample_mean_l2": float(np.linalg.norm(train.mean(axis=0) - sample.mean(axis=0))),
        "train_sample_std_l2": float(np.linalg.norm(train.std(axis=0) - sample.std(axis=0))),
    }


def pca_encoder_diagnostics(x: np.ndarray, keys: pd.DataFrame, latent_dim: int) -> tuple[np.ndarray, dict[str, float]]:
    x_scaled = StandardScaler().fit_transform(x)
    n_components = int(min(latent_dim, x_scaled.shape[0] - 1, x_scaled.shape[1]))
    pca = PCA(n_components=n_components, random_state=2026)
    z = pca.fit_transform(x_scaled)
    recon = pca.inverse_transform(z)
    mse = float(np.mean((x_scaled - recon) ** 2))
    explained = float(np.sum(pca.explained_variance_ratio_))
    metrics = {
        "latent_dim": n_components,
        "input_dim": int(x_scaled.shape[1]),
        "pca_reconstruction_mse": mse,
        "pca_explained_variance": explained,
        "subject_leakage_acc": subject_leakage_score(z, keys["subject_id"].to_numpy()),
        **train_sample_shift(z, keys),
        **cosine_temporal_locality(z, keys),
        **nearest_neighbor_stats(z, keys),
    }
    return z.astype(np.float32), metrics


def coverage_for_view(manifest: pd.DataFrame, view: str) -> pd.DataFrame:
    out = manifest.copy()
    if view == "full":
        covered = out["implementation_batch"].isin(["domain_state_v1", "encoder_pretrain_later"])
    elif view.startswith("only_"):
        token = view.removeprefix("only_")
        covered = out["families"].fillna("").str.contains(token, case=False, regex=False)
    elif view.startswith("no_"):
        token = view.removeprefix("no_")
        covered = ~out["families"].fillna("").str.contains(token, case=False, regex=False)
    else:
        covered = pd.Series(False, index=out.index)
    return out.loc[covered, ["idea_id", "source", "source_idea_no", "experiment_family", "implementation_batch", "risk"]].assign(view=view)


def dataframe_to_markdown(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "_No rows._"
    columns = list(frame.columns)
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for _, row in frame.iterrows():
        values = []
        for col in columns:
            value = row[col]
            if isinstance(value, float):
                values.append(f"{value:.6f}")
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def run(args: argparse.Namespace) -> None:
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    tokens = load_tokens(Path(args.token_path))
    keys = key_frame(tokens)
    split = load_split(Path(args.train_path), Path(args.sample_path))
    keys = keys.merge(split, on=["subject_id", "lifelog_date"], how="left", validate="one_to_one")
    keys["split"] = keys["split"].fillna("unknown")
    values = tokens["values"].astype(np.float32)
    mask = tokens["mask"].astype(np.float32)
    groups = tokens["channel_groups"].astype(str)
    manifest = pd.read_csv(args.manifest_path)
    views = [v.strip() for v in args.views.split(",") if v.strip()]

    summary_rows = []
    coverage_rows = []
    for view in views:
        idx = selected_channel_indices(groups, view)
        x = flatten_view(values, mask, idx, include_mask=args.include_mask)
        z, metrics = pca_encoder_diagnostics(x, keys, args.latent_dim)
        view_dir = output_dir / view
        view_dir.mkdir(parents=True, exist_ok=True)
        np.save(view_dir / "pca_latents.npy", z)
        pd.concat([keys.reset_index(drop=True), pd.DataFrame(z, columns=[f"z_{i:02d}" for i in range(z.shape[1])])], axis=1).to_parquet(
            view_dir / "pca_latents.parquet",
            index=False,
        )
        report = {
            "view": view,
            "channels_selected": int(len(idx)),
            "channel_groups_selected": sorted(pd.Series(groups[idx]).unique().tolist()),
            "include_mask": bool(args.include_mask),
            **metrics,
        }
        (view_dir / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        summary_rows.append(report)
        coverage_rows.append(coverage_for_view(manifest, view))

    summary = pd.DataFrame(summary_rows).sort_values(["train_sample_mean_l2", "pca_reconstruction_mse"])
    summary.to_csv(output_dir / "encoder_diagnostics_summary.csv", index=False)
    coverage = pd.concat(coverage_rows, ignore_index=True).drop_duplicates(["view", "idea_id"])
    coverage.to_csv(output_dir / "idea_view_coverage.csv", index=False)
    covered_ideas = coverage["idea_id"].nunique()
    total_ideas = manifest["idea_id"].nunique()
    final_report = {
        "token_path": args.token_path,
        "manifest_path": args.manifest_path,
        "views": views,
        "total_ideas": int(total_ideas),
        "covered_ideas_by_views": int(covered_ideas),
        "coverage_rate": float(covered_ideas / max(total_ideas, 1)),
        "best_low_shift_view": str(summary.iloc[0]["view"]) if len(summary) else "",
        "summary": summary.to_dict(orient="records"),
    }
    (output_dir / "report.json").write_text(json.dumps(final_report, indent=2, ensure_ascii=False), encoding="utf-8")
    md = [
        "# Domain Idea Encoder Diagnostics v1",
        "",
        "## Purpose",
        "",
        "Run label-free encoder-first diagnostics over the token views implied by the 300+ data-engineering ideas. This is deliberately not a decoder experiment.",
        "",
        "## Coverage",
        "",
        f"- Ideas in manifest: `{total_ideas}`",
        f"- Ideas touched by at least one view diagnostic: `{covered_ideas}`",
        f"- Coverage rate: `{covered_ideas / max(total_ideas, 1):.3f}`",
        "",
        "## View Summary",
        "",
        dataframe_to_markdown(summary),
        "",
        "## How To Read",
        "",
        "- Lower `pca_reconstruction_mse` means the view has a compact reconstructable structure.",
        "- Lower `train_sample_mean_l2` means less train/sample coordinate drift.",
        "- `subject_leakage_acc` is a warning signal: very high values mean the latent may memorize identity instead of day state.",
        "- `temporal_locality_gap` checks whether adjacent days are closer than random days without using labels.",
    ]
    (output_dir / "report.md").write_text("\n".join(md), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run label-free encoder diagnostics for domain idea token views.")
    parser.add_argument("--token-path", default="artifacts/domain_encoder_tokens_v1.npz")
    parser.add_argument("--manifest-path", default="experiments/domain_idea_bank/domain_idea_manifest.csv")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--output-dir", default="outputs/domain_idea_encoder_diagnostics_v1")
    parser.add_argument("--views", default=",".join(DEFAULT_VIEWS))
    parser.add_argument("--latent-dim", type=int, default=24)
    parser.add_argument("--include-mask", dest="include_mask", action="store_true", default=True)
    parser.add_argument("--no-include-mask", dest="include_mask", action="store_false")
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
