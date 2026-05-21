from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from train_hourly_transformer_encoder import dataframe_to_markdown, evaluate_embedding_probe, targetwise_prediction
from train_pruned_state_decoder import average_log_loss, drift_vs_reference, write_prediction
from train_s2_sleep_retrieval_encoder import TARGET_COLUMNS, normalize_keys


def channel_group(name: str) -> str:
    lower = name.lower()
    if lower.startswith("ev_"):
        return "event"
    if any(token in lower for token in ("hr", "pedo", "step", "cal", "still", "walk", "run", "vehicle")):
        return "body"
    if any(token in lower for token in ("screen", "charging", "usage", "phone")):
        return "phone"
    if any(token in lower for token in ("gps", "lat", "lon", "speed", "distance", "mobility")):
        return "mobility"
    if lower.startswith("amb_"):
        return "ambience"
    if any(token in lower for token in ("wifi", "ble", "rssi")):
        return "radio"
    if "light" in lower:
        return "light"
    if any(token in lower for token in ("gap", "activity", "coverage")):
        return "cross"
    return "other"


def compact_group_latent(channel_latent: np.ndarray, channels: list[str], groups: tuple[str, ...]) -> np.ndarray:
    parts = []
    channel_groups = np.array([channel_group(ch) for ch in channels], dtype=object)
    for group in groups:
        idx = np.flatnonzero(channel_groups == group)
        if len(idx) == 0:
            continue
        selected = channel_latent[:, idx, :]
        parts.append(selected.mean(axis=1))
        parts.append(selected.std(axis=1))
    if not parts:
        raise ValueError(f"No channels found for groups={groups}")
    return np.concatenate(parts, axis=1)


def subject_center(
    train_x: np.ndarray,
    sample_x: np.ndarray,
    train_subjects: np.ndarray,
    sample_subjects: np.ndarray,
    mode: str,
) -> tuple[np.ndarray, np.ndarray]:
    train_x = np.asarray(train_x, dtype=np.float32)
    sample_x = np.asarray(sample_x, dtype=np.float32)
    train_subjects = np.asarray(train_subjects, dtype=object)
    sample_subjects = np.asarray(sample_subjects, dtype=object)
    centered_train = np.zeros_like(train_x)
    centered_sample = np.zeros_like(sample_x)
    all_subjects = sorted(set(train_subjects.tolist()) | set(sample_subjects.tolist()))
    for subject in all_subjects:
        train_idx = np.flatnonzero(train_subjects == subject)
        sample_idx = np.flatnonzero(sample_subjects == subject)
        if mode == "train":
            basis = train_x[train_idx] if len(train_idx) else sample_x[sample_idx]
            mean = basis.mean(axis=0, keepdims=True)
            if len(train_idx):
                centered_train[train_idx] = train_x[train_idx] - mean
            if len(sample_idx):
                centered_sample[sample_idx] = sample_x[sample_idx] - mean
        elif mode == "all":
            basis_parts = []
            if len(train_idx):
                basis_parts.append(train_x[train_idx])
            if len(sample_idx):
                basis_parts.append(sample_x[sample_idx])
            mean = np.vstack(basis_parts).mean(axis=0, keepdims=True)
            if len(train_idx):
                centered_train[train_idx] = train_x[train_idx] - mean
            if len(sample_idx):
                centered_sample[sample_idx] = sample_x[sample_idx] - mean
        elif mode == "loo_train":
            if len(train_idx):
                if len(train_idx) > 1:
                    total = train_x[train_idx].sum(axis=0, keepdims=True)
                    centered_train[train_idx] = train_x[train_idx] - (total - train_x[train_idx]) / float(len(train_idx) - 1)
                else:
                    centered_train[train_idx] = 0.0
            if len(sample_idx):
                basis = train_x[train_idx] if len(train_idx) else sample_x[sample_idx]
                centered_sample[sample_idx] = sample_x[sample_idx] - basis.mean(axis=0, keepdims=True)
        else:
            raise ValueError(f"Unknown subject centering mode: {mode}")
    return centered_train, centered_sample


def load_embedding_view(view_dir: Path) -> dict[str, object]:
    path = view_dir / "embeddings.npz"
    if not path.exists():
        raise FileNotFoundError(path)
    data = np.load(path, allow_pickle=True)
    required = {"train", "sample", "channel_train", "channel_sample", "channels"}
    missing = sorted(required - set(data.files))
    if missing:
        raise ValueError(f"{path} is missing {missing}; rerun channel patch encoder after channel-latent support")
    channels = [str(item) for item in data["channels"].tolist()]
    return {
        "name": view_dir.name,
        "train": data["train"].astype(np.float32),
        "sample": data["sample"].astype(np.float32),
        "channel_train": data["channel_train"].astype(np.float32),
        "channel_sample": data["channel_sample"].astype(np.float32),
        "channels": channels,
    }


def add_centered_variants(
    out: dict[str, tuple[np.ndarray, np.ndarray]],
    name: str,
    train_mat: np.ndarray,
    sample_mat: np.ndarray,
    train_subjects: np.ndarray,
    sample_subjects: np.ndarray,
    modes: tuple[str, ...],
) -> None:
    if "absolute" in modes:
        out[name] = (train_mat, sample_mat)
    for mode in ("train", "all", "loo_train"):
        if f"subrel_{mode}" not in modes and f"abs_plus_subrel_{mode}" not in modes:
            continue
        centered_train, centered_sample = subject_center(train_mat, sample_mat, train_subjects, sample_subjects, mode)
        if f"subrel_{mode}" in modes:
            out[f"{name}__subrel_{mode}"] = (centered_train, centered_sample)
        if f"abs_plus_subrel_{mode}" in modes:
            out[f"{name}__abs_plus_subrel_{mode}"] = (
                np.concatenate([train_mat, centered_train], axis=1),
                np.concatenate([sample_mat, centered_sample], axis=1),
            )


def candidate_feature_matrices(
    view: dict[str, object],
    train_subjects: np.ndarray,
    sample_subjects: np.ndarray,
    candidate_mode: str,
) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    z_train = np.asarray(view["train"], dtype=np.float32)
    z_sample = np.asarray(view["sample"], dtype=np.float32)
    c_train = np.asarray(view["channel_train"], dtype=np.float32)
    c_sample = np.asarray(view["channel_sample"], dtype=np.float32)
    channels = list(view["channels"])
    if candidate_mode == "curated":
        modes = ("absolute", "subrel_train", "abs_plus_subrel_train")
        group_sets = {
            "event": ("event",),
            "body": ("body",),
            "phone": ("phone",),
            "mobility": ("mobility",),
            "behavior": ("event", "phone", "mobility", "cross"),
            "physio": ("body", "light"),
            "all_groups": ("event", "body", "phone", "mobility", "ambience", "radio", "light", "cross", "other"),
        }
    elif candidate_mode == "relative_only":
        modes = ("subrel_train",)
        group_sets = {
            "event": ("event",),
            "body": ("body",),
            "phone": ("phone",),
            "mobility": ("mobility",),
            "behavior": ("event", "phone", "mobility", "cross"),
            "physio": ("body", "light"),
            "all_groups": ("event", "body", "phone", "mobility", "ambience", "radio", "light", "cross", "other"),
        }
    elif candidate_mode == "all":
        modes = ("absolute", "subrel_train", "abs_plus_subrel_train", "subrel_all", "abs_plus_subrel_all", "subrel_loo_train", "abs_plus_subrel_loo_train")
        group_sets = {
            "event": ("event",),
            "body": ("body",),
            "phone": ("phone",),
            "mobility": ("mobility",),
            "ambience": ("ambience",),
            "radio": ("radio",),
            "light": ("light",),
            "cross": ("cross",),
            "behavior": ("event", "phone", "mobility", "cross"),
            "physio": ("body", "light"),
            "context": ("ambience", "radio", "light"),
            "all_groups": ("event", "body", "phone", "mobility", "ambience", "radio", "light", "cross", "other"),
        }
    else:
        raise ValueError(f"Unknown candidate mode: {candidate_mode}")

    candidates: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    add_centered_variants(candidates, f"{view['name']}__cls", z_train, z_sample, train_subjects, sample_subjects, modes)
    if candidate_mode == "curated" and str(view["name"]) == "only_event":
        group_sets = {key: value for key, value in group_sets.items() if key in {"event", "behavior", "all_groups"}}
    elif candidate_mode == "curated" and str(view["name"]) == "only_cross_modal":
        group_sets = {key: value for key, value in group_sets.items() if key in {"mobility", "behavior", "all_groups"}}
    elif candidate_mode == "curated" and str(view["name"]) == "no_sleep":
        group_sets = {key: value for key, value in group_sets.items() if key in {"event", "phone", "mobility", "behavior", "all_groups"}}
    elif candidate_mode == "curated" and str(view["name"]) == "full":
        group_sets = {key: value for key, value in group_sets.items() if key in {"body", "physio", "behavior", "all_groups"}}
    for group_name, groups in group_sets.items():
        try:
            train_mat = compact_group_latent(c_train, channels, groups)
            sample_mat = compact_group_latent(c_sample, channels, groups)
        except ValueError:
            continue
        add_centered_variants(candidates, f"{view['name']}__{group_name}", train_mat, sample_mat, train_subjects, sample_subjects, modes)
        cls_plus_train = np.concatenate([z_train, train_mat], axis=1)
        cls_plus_sample = np.concatenate([z_sample, sample_mat], axis=1)
        add_centered_variants(candidates, f"{view['name']}__cls_plus_{group_name}", cls_plus_train, cls_plus_sample, train_subjects, sample_subjects, modes)
    return candidates


def evaluate_candidates(
    train: pd.DataFrame,
    sample: pd.DataFrame,
    feature_candidates: dict[str, tuple[np.ndarray, np.ndarray]],
    args: argparse.Namespace,
) -> tuple[pd.DataFrame, dict[str, np.ndarray], dict[str, np.ndarray]]:
    rows = []
    all_oof: dict[str, np.ndarray] = {}
    all_sample: dict[str, np.ndarray] = {}
    for name, (z_train, z_sample) in feature_candidates.items():
        print(f"[fusion] evaluating {name} shape={z_train.shape}", flush=True)
        score_df, candidates_oof, candidates_sample = evaluate_embedding_probe(train, sample, z_train, z_sample, args)
        local_name = str(score_df.iloc[0]["source"])
        pred_name = f"{name}__{local_name}"
        pred_oof = candidates_oof[local_name]
        pred_sample = candidates_sample[local_name]
        avg, per = average_log_loss(train[TARGET_COLUMNS], pred_oof)
        rows.append({"source": pred_name, "feature": name, "probe": local_name, "avg_log_loss": avg, **per})
        all_oof[pred_name] = pred_oof
        all_sample[pred_name] = pred_sample
    return pd.DataFrame(rows).sort_values("avg_log_loss").reset_index(drop=True), all_oof, all_sample


def run(args: argparse.Namespace) -> None:
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    train_subjects = train["subject_id"].astype(str).to_numpy(object)
    sample_subjects = sample["subject_id"].astype(str).to_numpy(object)
    view_dirs = [Path(item) for item in args.view_dirs]
    features: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    view_group_rows = []
    for view_dir in view_dirs:
        view = load_embedding_view(view_dir)
        channels = list(view["channels"])
        counts = pd.Series([channel_group(ch) for ch in channels]).value_counts().sort_index()
        for group, count in counts.items():
            view_group_rows.append({"view": view["name"], "group": group, "channels": int(count)})
        features.update(candidate_feature_matrices(view, train_subjects, sample_subjects, args.candidate_mode))
    print(f"[fusion] feature candidates={len(features)} mode={args.candidate_mode}", flush=True)

    score_df, candidates_oof, candidates_sample = evaluate_candidates(train, sample, features, args)
    target_oof, target_sample, target_sources, target_losses = targetwise_prediction(score_df, candidates_oof, candidates_sample, train)
    target_avg, target_per = average_log_loss(train[TARGET_COLUMNS], target_oof)
    global_name = str(score_df.iloc[0]["source"])
    global_oof = candidates_oof[global_name]
    global_sample = candidates_sample[global_name]
    global_avg, global_per = average_log_loss(train[TARGET_COLUMNS], global_oof)

    predictions = {
        "best_global": (global_oof, global_sample, global_avg, global_per),
        "targetwise": (target_oof, target_sample, target_avg, target_per),
    }
    best_name = min(predictions, key=lambda key: predictions[key][2])
    best_oof, best_sample, best_avg, best_per = predictions[best_name]
    drift_best = drift_vs_reference(sample, best_sample, Path(args.reference_submission) if args.reference_submission else None)
    drift_global = drift_vs_reference(sample, global_sample, Path(args.reference_submission) if args.reference_submission else None)
    drift_target = drift_vs_reference(sample, target_sample, Path(args.reference_submission) if args.reference_submission else None)

    score_df.to_csv(output_dir / "fusion_candidate_scores.csv", index=False)
    pd.DataFrame(view_group_rows).to_csv(output_dir / "channel_group_counts.csv", index=False)
    pd.DataFrame([{"target": k, "source": v, "loss": target_losses[k]} for k, v in target_sources.items()]).to_csv(
        output_dir / "targetwise_selection.csv", index=False
    )
    write_prediction(output_dir / "oof_channel_latent_fusion_best.csv", train, best_oof, oof=True)
    write_prediction(output_dir / "submission_channel_latent_fusion_best.csv", sample, best_sample, oof=False)

    report = {
        "best_source": best_name,
        "best_avg_log_loss": float(best_avg),
        "best_per_target": {target: float(best_per[target]) for target in TARGET_COLUMNS},
        "best_global_source": global_name,
        "best_global_avg_log_loss": float(global_avg),
        "best_global_per_target": {target: float(global_per[target]) for target in TARGET_COLUMNS},
        "targetwise_avg_log_loss": float(target_avg),
        "targetwise_per_target": {target: float(target_per[target]) for target in TARGET_COLUMNS},
        "targetwise_sources": target_sources,
        "targetwise_source_losses": target_losses,
        "drift_vs_reference_best": drift_best,
        "drift_vs_reference_global": drift_global,
        "drift_vs_reference_targetwise": drift_target,
        "n_feature_candidates": len(features),
        "candidate_mode": args.candidate_mode,
        "view_group_counts": view_group_rows,
    }
    (output_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    md = [
        "# Channel Latent Fusion Decoder v1",
        "",
        "## Goal",
        "",
        "Decode the channel-independent patch encoder without collapsing everything into one day CLS vector. Each modality/channel group becomes an expert feature source, then fold-safe probes and target-wise fusion choose which latent family helps each label.",
        "",
        "## Result",
        "",
        f"- Best source: `{best_name}`",
        f"- OOF avg logloss: `{best_avg:.6f}`",
        f"- Drift vs v83 reference: `{drift_best.get('mean_abs_drift', float('nan')):.6f}`",
        f"- Feature candidates: `{len(features)}`",
        "",
        "## Top Candidate Scores",
        "",
        dataframe_to_markdown(score_df.head(20)),
        "",
        "## Target-Wise Fusion",
        "",
        f"- Target-wise avg logloss: `{target_avg:.6f}`",
        f"- Target-wise drift vs v83: `{drift_target.get('mean_abs_drift', float('nan')):.6f}`",
        "",
        dataframe_to_markdown(pd.DataFrame([{"target": k, "source": v, "loss": target_losses[k]} for k, v in target_sources.items()])),
        "",
        "## Channel Groups",
        "",
        dataframe_to_markdown(pd.DataFrame(view_group_rows)),
        "",
        "## Decision",
        "",
        "This is the first decoder that reads modality/channel latents rather than only the collapsed CLS day embedding. A positive result would mean the encoder should expose expert latents directly; a negative result means the SSL objective still does not make channel latents label-readable enough.",
    ]
    (output_dir / "report.md").write_text("\n".join(md), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train a modality/channel latent fusion decoder over channel patch encoder outputs.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--view-dirs", nargs="+", default=[
        "outputs/channel_patch_transformer_encoder_v2/no_sleep",
        "outputs/channel_patch_transformer_encoder_v2/full",
        "outputs/channel_patch_transformer_encoder_v2/only_event",
    ])
    parser.add_argument("--reference-submission", default="outputs/v83_repaired_v80/submission_v83_gq015_gs010.csv")
    parser.add_argument("--output-dir", default="outputs/channel_latent_fusion_decoder_v1")
    parser.add_argument("--candidate-mode", choices=["curated", "relative_only", "all"], default="curated")
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--probe-prior-alpha", type=float, default=8.0)
    parser.add_argument("--prior-alphas", type=float, nargs="+", default=[4.0, 8.0, 16.0])
    parser.add_argument("--c-values", type=float, nargs="+", default=[0.03, 0.10, 0.30])
    parser.add_argument("--logreg-blends", type=float, nargs="+", default=[0.05, 0.10, 0.20, 0.35])
    parser.add_argument("--ridge-alphas", type=float, nargs="+", default=[1.0, 5.0, 20.0])
    parser.add_argument("--ridge-blends", type=float, nargs="+", default=[0.05, 0.10, 0.20, 0.35])
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
