from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss

from train_deep_learning_golf import (
    EPS,
    TARGET_COLUMNS,
    Spec,
    fit_predict_net,
    grouped_abs_drift,
    macro_f1_at_half,
    param_count,
    prepare_matrix,
)
from train_hourly_transformer_encoder import dataframe_to_markdown, targetwise_prediction
from train_pruned_state_decoder import average_log_loss, drift_vs_reference, subject_prior, write_prediction
from train_s2_sleep_retrieval_encoder import KEY_COLUMNS, make_subject_time_folds, normalize_keys
from train_tiny_deviation_encoder import subject_relative
from train_deep_learning_golf import choose_device


def load_embedding(path: Path) -> tuple[np.ndarray, np.ndarray]:
    data = np.load(path / "embeddings.npz", allow_pickle=True)
    return data["train"].astype(float), data["sample"].astype(float)


def build_specs(args: argparse.Namespace) -> list[Spec]:
    specs: list[Spec] = []
    for mode in args.feature_modes:
        for top_k in args.top_k:
            for blend in args.blends:
                specs.append(Spec(f"{mode}__linear_k{top_k}_b{blend:g}", mode, "linear", top_k, 0, args.weight_decay[0], blend))
                for bottleneck in args.bottlenecks:
                    for wd in args.weight_decay:
                        specs.append(Spec(f"{mode}__lowrank_r{bottleneck}_k{top_k}_wd{wd:g}_b{blend:g}", mode, "lowrank", top_k, bottleneck, wd, blend))
                        specs.append(Spec(f"{mode}__mlp_h{bottleneck}_k{top_k}_wd{wd:g}_b{blend:g}", mode, "tiny_mlp", top_k, bottleneck, wd, blend))
    return specs


def run(args: argparse.Namespace) -> None:
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    train_subjects = train["subject_id"].astype(str).to_numpy(object)
    sample_subjects = sample["subject_id"].astype(str).to_numpy(object)
    y_all = train[TARGET_COLUMNS].to_numpy(float)
    folds = make_subject_time_folds(train, args.n_folds)
    device = choose_device(args.device)

    view_data = {}
    for item in args.view_dirs:
        path = Path(item)
        view_data[path.name] = load_embedding(path)

    specs = []
    for view_name in view_data:
        for spec in build_specs(args):
            specs.append(
                Spec(
                    f"{view_name}__{spec.name}",
                    f"{view_name}::{spec.mode}",
                    spec.model,
                    spec.top_k,
                    spec.bottleneck,
                    spec.weight_decay,
                    spec.blend,
                )
            )

    predictions = {spec.name: np.zeros((len(train), len(TARGET_COLUMNS)), dtype=float) for spec in specs}
    sample_folds = {spec.name: [] for spec in specs}
    fold_rows = []
    selected_rows = []
    prior_oof = np.zeros((len(train), len(TARGET_COLUMNS)), dtype=float)
    prior_sample_parts = []
    global_oof = np.zeros((len(train), len(TARGET_COLUMNS)), dtype=float)
    global_sample_parts = []

    for fold_i, fold in enumerate(folds, 1):
        prior_eval_all = subject_prior(train.iloc[fold.train_idx], train.iloc[fold.val_idx], args.prior_alpha)
        prior_sample_all = subject_prior(train.iloc[fold.train_idx], sample, args.prior_alpha)
        prior_oof[fold.val_idx] = prior_eval_all
        prior_sample_parts.append(prior_sample_all)
        means = train.iloc[fold.train_idx][TARGET_COLUMNS].mean().to_numpy(float)
        global_oof[fold.val_idx] = means[None, :]
        global_sample_parts.append(np.repeat(means[None, :], len(sample), axis=0))

        fold_sample = {spec.name: np.zeros((len(sample), len(TARGET_COLUMNS)), dtype=float) for spec in specs}
        y_fit = y_all[fold.train_idx]
        y_eval = y_all[fold.val_idx]
        mode_cache: dict[str, tuple[np.ndarray, np.ndarray, np.ndarray]] = {}
        for view_name, (z_train, z_sample) in view_data.items():
            rel_fit, rel_eval, rel_sample = subject_relative(z_train, z_sample, train_subjects, sample_subjects, fold.train_idx, fold.val_idx)
            raw_fit, raw_eval, raw_sample = z_train[fold.train_idx], z_train[fold.val_idx], z_sample
            mode_cache[f"{view_name}::absolute"] = (raw_fit, raw_eval, raw_sample)
            mode_cache[f"{view_name}::deviation"] = (rel_fit, rel_eval, rel_sample)
            mode_cache[f"{view_name}::absolute_plus_deviation"] = (
                np.concatenate([raw_fit, rel_fit], axis=1),
                np.concatenate([raw_eval, rel_eval], axis=1),
                np.concatenate([raw_sample, rel_sample], axis=1),
            )

        for spec in specs:
            x_fit_raw, x_eval_raw, x_sample_raw = mode_cache[spec.mode]
            x_fit, x_eval, x_sample, keep = prepare_matrix(x_fit_raw, x_eval_raw, x_sample_raw, y_fit, spec.top_k)
            pred_eval_raw, pred_sample_raw = fit_predict_net(
                x_fit,
                y_fit,
                x_eval,
                x_sample,
                spec,
                device,
                args.epochs,
                args.patience,
            )
            pred_eval = np.clip((1.0 - spec.blend) * prior_eval_all + spec.blend * pred_eval_raw, EPS, 1.0 - EPS)
            pred_sample = np.clip((1.0 - spec.blend) * prior_sample_all + spec.blend * pred_sample_raw, EPS, 1.0 - EPS)
            predictions[spec.name][fold.val_idx] = pred_eval
            fold_sample[spec.name] = pred_sample
            selected_rows.append(
                {
                    "fold": fold_i,
                    "source": spec.name,
                    "mode": spec.mode,
                    "model": spec.model,
                    "top_k": spec.top_k,
                    "bottleneck": spec.bottleneck,
                    "weight_decay": spec.weight_decay,
                    "blend": spec.blend,
                    "params": param_count(x_fit.shape[1], len(TARGET_COLUMNS), spec.model, spec.bottleneck),
                    "selected_feature_indices": " ".join(map(str, keep.tolist())),
                }
            )
            for target_i, target in enumerate(TARGET_COLUMNS):
                fold_rows.append(
                    {
                        "fold": fold_i,
                        "target": target,
                        "source": spec.name,
                        "loss": float(log_loss(y_eval[:, target_i], pred_eval[:, target_i], labels=[0, 1])),
                    }
                )
        for name, pred in fold_sample.items():
            sample_folds[name].append(pred)
        print(f"[latent-golf] fold {fold_i}/{len(folds)} done", flush=True)

    sample_predictions = {name: np.clip(np.mean(parts, axis=0), EPS, 1.0 - EPS) for name, parts in sample_folds.items()}
    baselines = {
        "bias_global": (np.clip(global_oof, EPS, 1 - EPS), np.clip(np.mean(global_sample_parts, axis=0), EPS, 1 - EPS), 7),
        "subject_prior": (np.clip(prior_oof, EPS, 1 - EPS), np.clip(np.mean(prior_sample_parts, axis=0), EPS, 1 - EPS), 7 * train["subject_id"].nunique()),
    }

    score_rows = []
    for name, (pred, sample_pred, params) in baselines.items():
        avg, per = average_log_loss(train[TARGET_COLUMNS], pred)
        drift = drift_vs_reference(sample, sample_pred, Path(args.reference_submission) if args.reference_submission else None)
        score_rows.append(
            {
                "source": name,
                "avg_log_loss": avg,
                "macro_f1_at_0p5": macro_f1_at_half(train[TARGET_COLUMNS], pred),
                "mean_params": params,
                "drift_vs_reference": drift.get("mean_abs_drift"),
                **per,
            }
        )
    for spec in specs:
        pred = np.clip(predictions[spec.name], EPS, 1.0 - EPS)
        avg, per = average_log_loss(train[TARGET_COLUMNS], pred)
        drift = drift_vs_reference(sample, sample_predictions[spec.name], Path(args.reference_submission) if args.reference_submission else None)
        score_rows.append(
            {
                "source": spec.name,
                "avg_log_loss": avg,
                "macro_f1_at_0p5": macro_f1_at_half(train[TARGET_COLUMNS], pred),
                "mean_params": param_count(spec.top_k, len(TARGET_COLUMNS), spec.model, spec.bottleneck),
                "drift_vs_reference": drift.get("mean_abs_drift"),
                "mode": spec.mode,
                "model": spec.model,
                "top_k": spec.top_k,
                "bottleneck": spec.bottleneck,
                "weight_decay": spec.weight_decay,
                "blend": spec.blend,
                **per,
            }
        )

    score_df = pd.DataFrame(score_rows).sort_values("avg_log_loss").reset_index(drop=True)
    model_predictions = {**{k: v[0] for k, v in baselines.items()}, **predictions}
    model_sample_predictions = {**{k: v[1] for k, v in baselines.items()}, **sample_predictions}
    target_oof, target_sample, target_sources, target_losses = targetwise_prediction(score_df, model_predictions, model_sample_predictions, train)
    target_avg, target_per = average_log_loss(train[TARGET_COLUMNS], target_oof)
    target_drift = drift_vs_reference(sample, target_sample, Path(args.reference_submission) if args.reference_submission else None)
    best_global = str(score_df.iloc[0]["source"])
    global_avg, global_per = average_log_loss(train[TARGET_COLUMNS], model_predictions[best_global])
    global_drift = drift_vs_reference(sample, model_sample_predictions[best_global], Path(args.reference_submission) if args.reference_submission else None)

    prior_avg, prior_per = average_log_loss(train[TARGET_COLUMNS], prior_oof)
    best_name = "targetwise" if target_avg <= global_avg else best_global
    best_oof = target_oof if best_name == "targetwise" else model_predictions[best_global]
    best_sample = target_sample if best_name == "targetwise" else model_sample_predictions[best_global]
    best_avg = target_avg if best_name == "targetwise" else global_avg
    best_per = target_per if best_name == "targetwise" else global_per
    best_drift = target_drift if best_name == "targetwise" else global_drift
    best_target_gain_vs_prior = {target: float(prior_per[target] - best_per[target]) for target in TARGET_COLUMNS}

    score_df.to_csv(output_dir / "latent_golf_scores.csv", index=False)
    pd.DataFrame(fold_rows).to_csv(output_dir / "latent_golf_fold_losses.csv", index=False)
    pd.DataFrame(selected_rows).to_csv(output_dir / "latent_golf_selected_features.csv", index=False)
    pd.DataFrame([{"target": target, "source": source, "loss": target_losses[target]} for target, source in target_sources.items()]).to_csv(output_dir / "targetwise_selection.csv", index=False)
    if args.save_candidates:
        np.savez_compressed(
            output_dir / "latent_golf_candidate_predictions.npz",
            sources=np.array(list(model_predictions.keys()), dtype=object),
            oof=np.stack([model_predictions[name] for name in model_predictions], axis=0).astype(np.float32),
            sample=np.stack([model_sample_predictions[name] for name in model_predictions], axis=0).astype(np.float32),
        )
    write_prediction(output_dir / "oof_latent_deep_learning_golf_best.csv", train, best_oof, oof=True)
    write_prediction(output_dir / "submission_latent_deep_learning_golf_best.csv", sample, best_sample, oof=False)

    report = {
        "best_source": best_name,
        "best_avg_log_loss": float(best_avg),
        "best_per_target": {target: float(best_per[target]) for target in TARGET_COLUMNS},
        "best_drift_vs_reference": best_drift,
        "best_subject_drift_vs_reference": grouped_abs_drift(sample, best_sample, args.reference_submission, "subject_id"),
        "best_target_gain_vs_subject_prior": best_target_gain_vs_prior,
        "best_global_source": best_global,
        "best_global_avg_log_loss": float(global_avg),
        "best_global_drift_vs_reference": global_drift,
        "targetwise_avg_log_loss": float(target_avg),
        "targetwise_drift_vs_reference": target_drift,
        "targetwise_sources": target_sources,
        "targetwise_source_losses": target_losses,
        "subject_prior_avg_log_loss": float(prior_avg),
        "n_candidates": len(specs) + len(baselines),
        "views": sorted(view_data),
        "device": str(device),
        "saved_candidates": bool(args.save_candidates),
    }
    (output_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    md = [
        "# Latent Deep Learning Golf v1",
        "",
        "## Goal",
        "",
        "Apply the minimum-parameter golf decoder discipline to existing channel-patch Transformer CLS latents.",
        "",
        "## Result",
        "",
        f"- Best source: `{best_name}`",
        f"- OOF avg logloss: `{best_avg:.6f}`",
        f"- Subject-prior OOF avg logloss: `{prior_avg:.6f}`",
        f"- Gain vs subject prior: `{prior_avg - best_avg:.6f}`",
        f"- Macro F1 @ 0.5: `{macro_f1_at_half(train[TARGET_COLUMNS], best_oof):.6f}`",
        f"- Drift vs v83 reference: `{best_drift.get('mean_abs_drift', float('nan')):.6f}`",
        "",
        "## Target Gain vs Subject Prior",
        "",
        dataframe_to_markdown(pd.DataFrame([{"target": target, "gain": best_target_gain_vs_prior[target]} for target in TARGET_COLUMNS])),
        "",
        "## Subject Drift vs v83",
        "",
        dataframe_to_markdown(pd.DataFrame([{"subject_id": subject, "mean_abs_drift": drift} for subject, drift in report["best_subject_drift_vs_reference"].items()])),
        "",
        "## Top Scores",
        "",
        dataframe_to_markdown(score_df.head(25)),
        "",
        "## Target-Wise Selection",
        "",
        f"- Target-wise avg logloss: `{target_avg:.6f}`",
        f"- Target-wise drift vs v83: `{target_drift.get('mean_abs_drift', float('nan')):.6f}`",
        "",
        dataframe_to_markdown(pd.DataFrame([{"target": target, "source": source, "loss": target_losses[target]} for target, source in target_sources.items()])),
        "",
        "## Decision",
        "",
        "This tests whether the existing Transformer SSL latent is label-readable under a tiny fixed decoder. Targetwise gains are diagnostic only until nested selection is run.",
    ]
    (output_dir / "report.md").write_text("\n".join(md), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Tiny golf decoders over Transformer CLS latents.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument(
        "--view-dirs",
        nargs="+",
        default=[
            "outputs/channel_patch_transformer_encoder_v1/full",
            "outputs/channel_patch_transformer_encoder_v1/no_sleep",
            "outputs/channel_patch_transformer_encoder_v1/only_cross_modal",
            "outputs/channel_patch_transformer_encoder_v1/only_event",
            "outputs/channel_patch_transformer_encoder_v1/only_rhythm",
        ],
    )
    parser.add_argument("--reference-submission", default="outputs/v83_repaired_v80/submission_v83_gq015_gs010.csv")
    parser.add_argument("--output-dir", default="outputs/latent_deep_learning_golf_v1")
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--prior-alpha", type=float, default=8.0)
    parser.add_argument("--feature-modes", nargs="+", default=["absolute", "deviation", "absolute_plus_deviation"])
    parser.add_argument("--top-k", type=int, nargs="+", default=[1, 2, 4, 8])
    parser.add_argument("--bottlenecks", type=int, nargs="+", default=[1, 2, 3, 4])
    parser.add_argument("--blends", type=float, nargs="+", default=[0.05, 0.1, 0.2, 0.35])
    parser.add_argument("--weight-decay", type=float, nargs="+", default=[0.03, 0.1])
    parser.add_argument("--epochs", type=int, default=220)
    parser.add_argument("--patience", type=int, default=30)
    parser.add_argument("--device", choices=["cpu", "mps", "cuda"], default="mps")
    parser.add_argument("--save-candidates", action="store_true")
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
