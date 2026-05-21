from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss

from train_channel_latent_fusion_decoder import load_embedding_view
from train_fold_local_channel_fusion_decoder import DEFAULT_EXPERTS, base_feature_matrix, compress_features, fit_target_model, fold_center, parse_feature_name
from train_hourly_transformer_encoder import dataframe_to_markdown, targetwise_prediction
from train_pruned_state_decoder import average_log_loss, drift_vs_reference, subject_prior, write_prediction
from train_s2_sleep_retrieval_encoder import EPS, TARGET_COLUMNS, make_subject_time_folds, normalize_keys


TARGET_MOE_FEATURES = {
    "Q1": [
        "full__cls_plus_physio__abs_plus_subrel_train",
        "full__cls_plus_all_groups__subrel_train",
        "no_sleep__cls_plus_behavior__subrel_train",
    ],
    "Q2": [
        "only_cross_modal__cls_plus_all_groups__subrel_train",
        "no_sleep__cls_plus_behavior__subrel_train",
        "no_sleep__cls_plus_mobility__subrel_train",
        "full__cls_plus_all_groups__subrel_train",
    ],
    "Q3": [
        "full__cls_plus_all_groups__subrel_train",
        "full__cls_plus_physio__abs_plus_subrel_train",
        "no_sleep__cls_plus_behavior__subrel_train",
    ],
    "S1": [
        "full__cls_plus_physio__abs_plus_subrel_train",
        "full__cls_plus_body__abs_plus_subrel_train",
        "full__cls_plus_all_groups__subrel_train",
    ],
    "S2": [
        "full__cls_plus_body",
        "full__cls_plus_physio__abs_plus_subrel_train",
        "no_sleep__cls_plus_behavior__subrel_train",
    ],
    "S3": [
        "full__cls_plus_all_groups__abs_plus_subrel_train",
        "full__cls_plus_physio__abs_plus_subrel_train",
        "no_sleep__cls_plus_behavior__subrel_train",
    ],
    "S4": [
        "only_event__cls__abs_plus_subrel_train",
        "only_event__cls_plus_event__abs_plus_subrel_train",
        "only_event__cls_plus_behavior__abs_plus_subrel_train",
        "no_sleep__cls_plus_behavior__subrel_train",
    ],
}


def all_feature_names() -> list[str]:
    names = {spec.feature for spec in DEFAULT_EXPERTS}
    for features in TARGET_MOE_FEATURES.values():
        names.update(features)
    return sorted(names)


def prepare_raw_features(view_dirs: dict[str, Path]) -> dict[str, tuple[np.ndarray, np.ndarray, str]]:
    views = {name: load_embedding_view(path) for name, path in view_dirs.items()}
    raw: dict[str, tuple[np.ndarray, np.ndarray, str]] = {}
    for feature in all_feature_names():
        view_name, feature_part, center = parse_feature_name(feature)
        base_train, base_sample = base_feature_matrix(views[view_name], feature_part)
        raw[feature] = (base_train, base_sample, center)
    return raw


def block_stats(x_fit: np.ndarray, x_eval: np.ndarray, x_sample: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    def stats(x: np.ndarray) -> np.ndarray:
        return np.column_stack(
            [
                x.mean(axis=1),
                x.std(axis=1),
                np.sqrt(np.mean(np.square(x), axis=1)),
                np.max(np.abs(x), axis=1),
            ]
        )

    return stats(x_fit), stats(x_eval), stats(x_sample)


def build_fold_feature(
    raw_features: dict[str, tuple[np.ndarray, np.ndarray, str]],
    feature_names: list[str],
    train_subjects: np.ndarray,
    sample_subjects: np.ndarray,
    fit_idx: np.ndarray,
    eval_idx: np.ndarray,
    pca_components: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    fit_parts = []
    eval_parts = []
    sample_parts = []
    for feature_name in feature_names:
        base_train, base_sample, center = raw_features[feature_name]
        x_fit_raw, x_eval_raw, x_sample_raw = fold_center(
            base_train,
            base_sample,
            train_subjects,
            sample_subjects,
            fit_idx,
            eval_idx,
            center,
        )
        x_fit, x_eval, x_sample = compress_features(x_fit_raw, x_eval_raw, x_sample_raw, pca_components)
        s_fit, s_eval, s_sample = block_stats(x_fit, x_eval, x_sample)
        fit_parts.extend([x_fit, s_fit])
        eval_parts.extend([x_eval, s_eval])
        sample_parts.extend([x_sample, s_sample])
    return np.concatenate(fit_parts, axis=1), np.concatenate(eval_parts, axis=1), np.concatenate(sample_parts, axis=1)


def feature_set_for(mode: str, target: str) -> list[str]:
    if mode == "selected_single":
        return [next(spec.feature for spec in DEFAULT_EXPERTS if spec.target == target)]
    if mode == "target_moe":
        return TARGET_MOE_FEATURES[target]
    if mode == "selected_plus_target_moe":
        selected = next(spec.feature for spec in DEFAULT_EXPERTS if spec.target == target)
        return list(dict.fromkeys([selected, *TARGET_MOE_FEATURES[target]]))
    if mode == "wide_moe":
        return all_feature_names()
    raise ValueError(f"Unknown feature mode: {mode}")


def run(args: argparse.Namespace) -> None:
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    train_subjects = train["subject_id"].astype(str).to_numpy(object)
    sample_subjects = sample["subject_id"].astype(str).to_numpy(object)
    view_dirs = {Path(item).name: Path(item) for item in args.view_dirs}
    raw_features = prepare_raw_features(view_dirs)
    folds = make_subject_time_folds(train, args.n_folds)

    candidate_specs = []
    for mode in args.feature_modes:
        for family in args.families:
            if family == "logreg":
                for c in args.logreg_c:
                    for blend in args.blends:
                        candidate_specs.append((mode, family, c, args.ridge_alpha[0], blend, f"{mode}__logreg_c{c:g}_b{blend:g}"))
            elif family == "ridge":
                for alpha in args.ridge_alpha:
                    for blend in args.blends:
                        candidate_specs.append((mode, family, args.logreg_c[0], alpha, blend, f"{mode}__ridge_a{alpha:g}_b{blend:g}"))
            else:
                raise ValueError(f"Unknown family: {family}")

    predictions = {name: np.zeros((len(train), len(TARGET_COLUMNS))) for *_, name in candidate_specs}
    sample_folds = {name: [] for *_, name in candidate_specs}
    fold_rows = []

    for fold_i, fold in enumerate(folds, 1):
        fold_sample = {name: np.zeros((len(sample), len(TARGET_COLUMNS))) for *_, name in candidate_specs}
        prior_fit_all = subject_prior(train.iloc[fold.train_idx], train.iloc[fold.train_idx], args.prior_alpha)
        prior_eval_all = subject_prior(train.iloc[fold.train_idx], train.iloc[fold.val_idx], args.prior_alpha)
        prior_sample_all = subject_prior(train.iloc[fold.train_idx], sample, args.prior_alpha)
        for target_i, target in enumerate(TARGET_COLUMNS):
            y_fit = train.iloc[fold.train_idx][target].to_numpy(int)
            y_eval = train.iloc[fold.val_idx][target].to_numpy(int)
            cache: dict[str, tuple[np.ndarray, np.ndarray, np.ndarray]] = {}
            for mode, family, c, alpha, blend, name in candidate_specs:
                if mode not in cache:
                    cache[mode] = build_fold_feature(
                        raw_features,
                        feature_set_for(mode, target),
                        train_subjects,
                        sample_subjects,
                        fold.train_idx,
                        fold.val_idx,
                        args.pca_components,
                    )
                x_fit, x_eval, x_sample = cache[mode]
                local_args = argparse.Namespace(
                    logreg_c=c,
                    logreg_blend=blend,
                    ridge_alpha=alpha,
                    ridge_blend=blend,
                    hgb_iter=0,
                    hgb_lr=0.0,
                    hgb_leaf_nodes=0,
                    hgb_l2=0.0,
                    hgb_blend=0.0,
                )
                eval_pred, sample_pred = fit_target_model(
                    family,
                    x_fit,
                    y_fit,
                    x_eval,
                    x_sample,
                    prior_fit_all[:, target_i],
                    prior_eval_all[:, target_i],
                    prior_sample_all[:, target_i],
                    local_args,
                )
                eval_pred = np.clip(eval_pred, EPS, 1.0 - EPS)
                sample_pred = np.clip(sample_pred, EPS, 1.0 - EPS)
                predictions[name][fold.val_idx, target_i] = eval_pred
                fold_sample[name][:, target_i] = sample_pred
                fold_rows.append(
                    {
                        "fold": fold_i,
                        "target": target,
                        "source": name,
                        "loss": float(log_loss(y_eval, eval_pred, labels=[0, 1])),
                        "n_features": int(x_fit.shape[1]),
                    }
                )
        for name, pred in fold_sample.items():
            sample_folds[name].append(pred)

    sample_predictions = {name: np.clip(np.mean(parts, axis=0), EPS, 1.0 - EPS) for name, parts in sample_folds.items()}
    score_rows = []
    for name, pred in predictions.items():
        pred = np.clip(pred, EPS, 1.0 - EPS)
        predictions[name] = pred
        avg, per = average_log_loss(train[TARGET_COLUMNS], pred)
        drift = drift_vs_reference(sample, sample_predictions[name], Path(args.reference_submission) if args.reference_submission else None)
        score_rows.append({"source": name, "avg_log_loss": avg, "drift_vs_reference": drift.get("mean_abs_drift"), **per})
    score_df = pd.DataFrame(score_rows).sort_values("avg_log_loss").reset_index(drop=True)

    target_oof, target_sample, target_sources, target_losses = targetwise_prediction(score_df, predictions, sample_predictions, train)
    target_avg, target_per = average_log_loss(train[TARGET_COLUMNS], target_oof)
    target_drift = drift_vs_reference(sample, target_sample, Path(args.reference_submission) if args.reference_submission else None)

    best_global_name = str(score_df.iloc[0]["source"])
    global_oof = predictions[best_global_name]
    global_sample = sample_predictions[best_global_name]
    global_avg, global_per = average_log_loss(train[TARGET_COLUMNS], global_oof)
    global_drift = drift_vs_reference(sample, global_sample, Path(args.reference_submission) if args.reference_submission else None)

    hybrid_avg = None
    hybrid_per = None
    hybrid_drift = None
    hybrid_sources = {}
    hybrid_losses = {}
    hybrid_oof = None
    hybrid_sample = None
    blend_rows = []
    if args.baseline_oof and args.baseline_submission:
        baseline_oof = normalize_keys(pd.read_csv(args.baseline_oof))[[f"pred_{target}" for target in TARGET_COLUMNS]].to_numpy(float)
        baseline_sample = normalize_keys(pd.read_csv(args.baseline_submission))[TARGET_COLUMNS].to_numpy(float)
        baseline_avg, baseline_per = average_log_loss(train[TARGET_COLUMNS], baseline_oof)
        combined_predictions = {"baseline": np.clip(baseline_oof, EPS, 1.0 - EPS), **predictions}
        combined_samples = {"baseline": np.clip(baseline_sample, EPS, 1.0 - EPS), **sample_predictions}
        combined_rows = [{"source": "baseline", "avg_log_loss": baseline_avg, "drift_vs_reference": None, **baseline_per}]
        combined_rows.extend(score_rows)
        combined_df = pd.DataFrame(combined_rows).sort_values("avg_log_loss").reset_index(drop=True)
        hybrid_oof, hybrid_sample, hybrid_sources, hybrid_losses = targetwise_prediction(combined_df, combined_predictions, combined_samples, train)
        hybrid_avg, hybrid_per = average_log_loss(train[TARGET_COLUMNS], hybrid_oof)
        hybrid_drift = drift_vs_reference(sample, hybrid_sample, Path(args.reference_submission) if args.reference_submission else None)
        pd.DataFrame([{"target": target, "source": source, "loss": hybrid_losses[target]} for target, source in hybrid_sources.items()]).to_csv(
            output_dir / "hybrid_targetwise_selection.csv", index=False
        )
        write_prediction(output_dir / "oof_fold_local_latent_moe_hybrid.csv", train, hybrid_oof, oof=True)
        write_prediction(output_dir / "submission_fold_local_latent_moe_hybrid.csv", sample, hybrid_sample, oof=False)
        for weight in args.hybrid_blend_weights:
            blend_oof = np.clip((1.0 - weight) * baseline_oof + weight * hybrid_oof, EPS, 1.0 - EPS)
            blend_sample = np.clip((1.0 - weight) * baseline_sample + weight * hybrid_sample, EPS, 1.0 - EPS)
            blend_avg, blend_per = average_log_loss(train[TARGET_COLUMNS], blend_oof)
            blend_drift = drift_vs_reference(sample, blend_sample, Path(args.reference_submission) if args.reference_submission else None)
            blend_rows.append(
                {
                    "latent_weight": float(weight),
                    "avg_log_loss": float(blend_avg),
                    "drift_vs_reference": blend_drift.get("mean_abs_drift"),
                    **blend_per,
                }
            )
            if weight in args.write_blend_weights:
                suffix = int(round(weight * 100))
                write_prediction(output_dir / f"oof_latent_moe_blend_w{suffix:02d}.csv", train, blend_oof, oof=True)
                write_prediction(output_dir / f"submission_latent_moe_blend_w{suffix:02d}.csv", sample, blend_sample, oof=False)
        pd.DataFrame(blend_rows).to_csv(output_dir / "latent_moe_blend_scores.csv", index=False)

    if hybrid_avg is not None and hybrid_avg <= min(target_avg, global_avg):
        best_name = "baseline_targetwise_hybrid"
        best_oof, best_sample, best_avg, best_per, best_drift = hybrid_oof, hybrid_sample, hybrid_avg, hybrid_per, hybrid_drift
    elif target_avg <= global_avg:
        best_name = "targetwise"
        best_oof, best_sample, best_avg, best_per, best_drift = target_oof, target_sample, target_avg, target_per, target_drift
    else:
        best_name = best_global_name
        best_oof, best_sample, best_avg, best_per, best_drift = global_oof, global_sample, global_avg, global_per, global_drift

    score_df.to_csv(output_dir / "latent_moe_scores.csv", index=False)
    pd.DataFrame(fold_rows).to_csv(output_dir / "latent_moe_fold_losses.csv", index=False)
    pd.DataFrame([{"target": target, "source": source, "loss": target_losses[target]} for target, source in target_sources.items()]).to_csv(
        output_dir / "targetwise_selection.csv", index=False
    )
    write_prediction(output_dir / "oof_fold_local_latent_moe_best.csv", train, best_oof, oof=True)
    write_prediction(output_dir / "submission_fold_local_latent_moe_best.csv", sample, best_sample, oof=False)

    report = {
        "best_source": best_name,
        "best_avg_log_loss": float(best_avg),
        "best_per_target": {target: float(best_per[target]) for target in TARGET_COLUMNS},
        "best_drift_vs_reference": best_drift,
        "best_global_source": best_global_name,
        "best_global_avg_log_loss": float(global_avg),
        "best_global_drift_vs_reference": global_drift,
        "targetwise_avg_log_loss": float(target_avg),
        "targetwise_drift_vs_reference": target_drift,
        "targetwise_sources": target_sources,
        "targetwise_source_losses": target_losses,
        "hybrid_avg_log_loss": None if hybrid_avg is None else float(hybrid_avg),
        "hybrid_drift_vs_reference": hybrid_drift,
        "hybrid_sources": hybrid_sources,
        "hybrid_source_losses": hybrid_losses,
        "hybrid_blend_scores": blend_rows,
        "feature_modes": args.feature_modes,
        "pca_components": args.pca_components,
    }
    (output_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    md = [
        "# Fold-Local Latent MoE Decoder v1",
        "",
        "## Goal",
        "",
        "Move the MoE experiment before probability stacking: target-specific expert latent blocks are subject-centered inside each fold, scaled per block, augmented with block statistics, concatenated, and decoded with small fold-safe residual heads.",
        "",
        "## Result",
        "",
        f"- Best source: `{best_name}`",
        f"- OOF avg logloss: `{best_avg:.6f}`",
        f"- Drift vs v83 reference: `{best_drift.get('mean_abs_drift', float('nan')):.6f}`",
        "",
        "## Top Latent MoE Scores",
        "",
        dataframe_to_markdown(score_df.head(20)),
        "",
        "## Target-Wise Latent Gate",
        "",
        f"- Target-wise avg logloss: `{target_avg:.6f}`",
        f"- Target-wise drift vs v83: `{target_drift.get('mean_abs_drift', float('nan')):.6f}`",
        "",
        dataframe_to_markdown(pd.DataFrame([{"target": target, "source": source, "loss": target_losses[target]} for target, source in target_sources.items()])),
        "",
        "## Baseline Hybrid",
        "",
        f"- Hybrid avg logloss: `{float('nan') if hybrid_avg is None else hybrid_avg:.6f}`",
        f"- Hybrid drift vs v83: `{float('nan') if hybrid_drift is None else hybrid_drift.get('mean_abs_drift', float('nan')):.6f}`",
        "",
        dataframe_to_markdown(pd.DataFrame([{"target": target, "source": source, "loss": hybrid_losses[target]} for target, source in hybrid_sources.items()])),
        "",
        "## Hybrid Shrinkage",
        "",
        "Blend the no-PCA fold-local baseline with the latent-MoE hybrid to expose the OOF/drift tradeoff.",
        "",
        dataframe_to_markdown(pd.DataFrame(blend_rows)),
        "",
        "## Decision",
        "",
        "This is the first decoder that gates raw channel-patch expert latents before final probability formation. A positive target-specific result should feed the next Transformer decoder head; a negative result means expert disagreement is only useful after each expert has already been separately regularized.",
    ]
    (output_dir / "report.md").write_text("\n".join(md), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train fold-local latent-level MoE decoders over channel patch expert blocks.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--view-dirs", nargs="+", default=[
        "outputs/channel_patch_transformer_encoder_v2/no_sleep",
        "outputs/channel_patch_transformer_encoder_v2/full",
        "outputs/channel_patch_transformer_encoder_v2/only_event",
        "outputs/channel_patch_transformer_encoder_v2/only_cross_modal",
    ])
    parser.add_argument("--reference-submission", default="outputs/v83_repaired_v80/submission_v83_gq015_gs010.csv")
    parser.add_argument("--baseline-oof", default="outputs/fold_local_channel_fusion_decoder_no_pca_v1/oof_fold_local_selected.csv")
    parser.add_argument("--baseline-submission", default="outputs/fold_local_channel_fusion_decoder_no_pca_v1/submission_fold_local_selected.csv")
    parser.add_argument("--output-dir", default="outputs/fold_local_latent_moe_decoder_v1")
    parser.add_argument("--feature-modes", nargs="+", default=["selected_single", "target_moe", "selected_plus_target_moe"])
    parser.add_argument("--families", nargs="+", choices=["ridge", "logreg"], default=["ridge", "logreg"])
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--prior-alpha", type=float, default=8.0)
    parser.add_argument("--pca-components", type=int, default=0)
    parser.add_argument("--logreg-c", type=float, nargs="+", default=[0.03, 0.1])
    parser.add_argument("--ridge-alpha", type=float, nargs="+", default=[5.0, 20.0, 80.0])
    parser.add_argument("--blends", type=float, nargs="+", default=[0.05, 0.1, 0.2, 0.35])
    parser.add_argument("--hybrid-blend-weights", type=float, nargs="+", default=[0.0, 0.15, 0.25, 0.35, 0.5, 0.65, 0.8, 1.0])
    parser.add_argument("--write-blend-weights", type=float, nargs="+", default=[0.25, 0.5, 0.65, 1.0])
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
