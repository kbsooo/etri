from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.preprocessing import StandardScaler

from train_hourly_transformer_encoder import dataframe_to_markdown, targetwise_prediction
from train_pruned_state_decoder import average_log_loss, drift_vs_reference, subject_prior, write_prediction
from train_s2_sleep_retrieval_encoder import EPS, TARGET_COLUMNS, make_subject_time_folds, normalize_keys


PRED_COLUMNS = [f"pred_{target}" for target in TARGET_COLUMNS]


def logit(p: np.ndarray) -> np.ndarray:
    p = np.clip(p, EPS, 1.0 - EPS)
    return np.log(p / (1.0 - p))


def load_sources(source_dirs: list[Path]) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray]]:
    oof_sources: dict[str, np.ndarray] = {}
    sample_sources: dict[str, np.ndarray] = {}
    for source_dir in source_dirs:
        prefix = source_dir.name.replace("fold_local_channel_fusion_decoder_", "")
        for oof_path in sorted(source_dir.glob("oof_fold_local_*.csv")):
            stem = oof_path.stem.removeprefix("oof_")
            if stem.endswith("channel_fusion_best"):
                continue
            submission_path = source_dir / f"submission_{stem}.csv"
            if not submission_path.exists():
                continue
            name = f"{prefix}__{stem}"
            oof = normalize_keys(pd.read_csv(oof_path))[PRED_COLUMNS].to_numpy(float)
            sample = normalize_keys(pd.read_csv(submission_path))[TARGET_COLUMNS].to_numpy(float)
            oof_sources[name] = np.clip(oof, EPS, 1.0 - EPS)
            sample_sources[name] = np.clip(sample, EPS, 1.0 - EPS)
    if not oof_sources:
        raise ValueError("No fold-local source prediction files found.")
    return oof_sources, sample_sources


def source_matrix(sources: dict[str, np.ndarray], target_idx: int) -> np.ndarray:
    probs = np.column_stack([pred[:, target_idx] for pred in sources.values()])
    logits = logit(probs)
    return np.concatenate([probs, logits, probs.mean(axis=1, keepdims=True), logits.mean(axis=1, keepdims=True)], axis=1)


def fit_predict_family(
    family: str,
    x_fit: np.ndarray,
    y_fit: np.ndarray,
    x_eval: np.ndarray,
    x_sample: np.ndarray,
    prior_fit: np.ndarray,
    prior_eval: np.ndarray,
    prior_sample: np.ndarray,
    c: float,
    alpha: float,
    blend: float,
) -> tuple[np.ndarray, np.ndarray]:
    scaler = StandardScaler()
    x_fit = np.clip(scaler.fit_transform(x_fit), -20.0, 20.0)
    x_eval = np.clip(scaler.transform(x_eval), -20.0, 20.0)
    x_sample = np.clip(scaler.transform(x_sample), -20.0, 20.0)
    if family == "logreg":
        if len(np.unique(y_fit)) < 2:
            pred_eval = np.full(len(x_eval), float(y_fit[0]))
            pred_sample = np.full(len(x_sample), float(y_fit[0]))
        else:
            model = LogisticRegression(C=c, solver="lbfgs", max_iter=5000, random_state=2026)
            model.fit(x_fit, y_fit)
            pred_eval = model.predict_proba(x_eval)[:, 1]
            pred_sample = model.predict_proba(x_sample)[:, 1]
        return (1.0 - blend) * prior_eval + blend * pred_eval, (1.0 - blend) * prior_sample + blend * pred_sample
    if family == "ridge":
        model = Ridge(alpha=alpha, solver="lsqr", random_state=2026)
        model.fit(x_fit, y_fit.astype(float) - prior_fit)
        return prior_eval + blend * model.predict(x_eval), prior_sample + blend * model.predict(x_sample)
    raise ValueError(f"Unknown family: {family}")


def run(args: argparse.Namespace) -> None:
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    oof_sources, sample_sources = load_sources([Path(item) for item in args.source_dirs])
    folds = make_subject_time_folds(train, args.n_folds)

    candidate_specs = []
    for c in args.c_values:
        for blend in args.blends:
            candidate_specs.append(("logreg", c, 0.0, blend, f"moe_logreg_c{c:g}_b{blend:g}"))
    for alpha in args.ridge_alphas:
        for blend in args.blends:
            candidate_specs.append(("ridge", 0.0, alpha, blend, f"moe_ridge_a{alpha:g}_b{blend:g}"))

    predictions = {name: np.zeros((len(train), len(TARGET_COLUMNS))) for *_, name in candidate_specs}
    sample_parts = {name: [] for *_, name in candidate_specs}
    fold_rows = []

    for fold_i, fold in enumerate(folds, 1):
        fold_sample = {name: np.zeros((len(sample), len(TARGET_COLUMNS))) for *_, name in candidate_specs}
        prior_fit_all = subject_prior(train.iloc[fold.train_idx], train.iloc[fold.train_idx], args.prior_alpha)
        prior_eval_all = subject_prior(train.iloc[fold.train_idx], train.iloc[fold.val_idx], args.prior_alpha)
        prior_sample_all = subject_prior(train.iloc[fold.train_idx], sample, args.prior_alpha)
        for target_i, target in enumerate(TARGET_COLUMNS):
            x_all = source_matrix(oof_sources, target_i)
            x_sample = source_matrix(sample_sources, target_i)
            y_fit = train.iloc[fold.train_idx][target].to_numpy(int)
            y_eval = train.iloc[fold.val_idx][target].to_numpy(int)
            for family, c, alpha, blend, name in candidate_specs:
                pred_eval, pred_sample = fit_predict_family(
                    family,
                    x_all[fold.train_idx],
                    y_fit,
                    x_all[fold.val_idx],
                    x_sample,
                    prior_fit_all[:, target_i],
                    prior_eval_all[:, target_i],
                    prior_sample_all[:, target_i],
                    c,
                    alpha,
                    blend,
                )
                pred_eval = np.clip(pred_eval, EPS, 1.0 - EPS)
                pred_sample = np.clip(pred_sample, EPS, 1.0 - EPS)
                predictions[name][fold.val_idx, target_i] = pred_eval
                fold_sample[name][:, target_i] = pred_sample
                fold_rows.append(
                    {
                        "fold": fold_i,
                        "target": target,
                        "source": name,
                        "loss": float(pd.NA) if len(np.unique(y_eval)) < 2 else float(-np.mean(y_eval * np.log(pred_eval) + (1 - y_eval) * np.log(1 - pred_eval))),
                    }
                )
        for name, pred in fold_sample.items():
            sample_parts[name].append(pred)

    sample_predictions = {name: np.clip(np.mean(parts, axis=0), EPS, 1.0 - EPS) for name, parts in sample_parts.items()}
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
    if args.baseline_oof and args.baseline_submission:
        baseline_oof = normalize_keys(pd.read_csv(args.baseline_oof))[PRED_COLUMNS].to_numpy(float)
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
        write_prediction(output_dir / "oof_fold_local_channel_moe_hybrid.csv", train, hybrid_oof, oof=True)
        write_prediction(output_dir / "submission_fold_local_channel_moe_hybrid.csv", sample, hybrid_sample, oof=False)

    if hybrid_avg is not None and hybrid_avg <= min(target_avg, global_avg):
        best_name = "baseline_targetwise_hybrid"
        best_oof, best_sample, best_avg, best_per, best_drift = hybrid_oof, hybrid_sample, hybrid_avg, hybrid_per, hybrid_drift
    elif target_avg <= global_avg:
        best_name = "targetwise"
        best_oof, best_sample, best_avg, best_per, best_drift = target_oof, target_sample, target_avg, target_per, target_drift
    else:
        best_name = best_global_name
        best_oof, best_sample, best_avg, best_per, best_drift = global_oof, global_sample, global_avg, global_per, global_drift

    score_df.to_csv(output_dir / "moe_scores.csv", index=False)
    pd.DataFrame(fold_rows).to_csv(output_dir / "moe_fold_losses.csv", index=False)
    pd.DataFrame([{"target": target, "source": source, "loss": target_losses[target]} for target, source in target_sources.items()]).to_csv(
        output_dir / "targetwise_selection.csv", index=False
    )
    write_prediction(output_dir / "oof_fold_local_channel_moe_best.csv", train, best_oof, oof=True)
    write_prediction(output_dir / "submission_fold_local_channel_moe_best.csv", sample, best_sample, oof=False)

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
        "input_sources": list(oof_sources.keys()),
        "n_input_sources": len(oof_sources),
    }
    (output_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    md = [
        "# Fold-Local Channel MoE Decoder v1",
        "",
        "## Goal",
        "",
        "Treat the fold-local channel-fusion decoders as expert predictions and train a small fold-safe stacking gate over their probabilities/logits. This tests whether the channel-patch experts contain complementary signal beyond the best single expert.",
        "",
        "## Result",
        "",
        f"- Best source: `{best_name}`",
        f"- OOF avg logloss: `{best_avg:.6f}`",
        f"- Drift vs v83 reference: `{best_drift.get('mean_abs_drift', float('nan')):.6f}`",
        f"- Input sources: `{len(oof_sources)}`",
        "",
        "## Top MoE Scores",
        "",
        dataframe_to_markdown(score_df.head(20)),
        "",
        "## Target-Wise Gate",
        "",
        f"- Target-wise avg logloss: `{target_avg:.6f}`",
        f"- Target-wise drift vs v83: `{target_drift.get('mean_abs_drift', float('nan')):.6f}`",
        "",
        dataframe_to_markdown(pd.DataFrame([{"target": target, "source": source, "loss": target_losses[target]} for target, source in target_sources.items()])),
        "",
        "## Baseline Hybrid Gate",
        "",
        "This keeps the fold-local no-PCA selected decoder unless a MoE source beats it for a target.",
        "",
        f"- Hybrid avg logloss: `{float('nan') if hybrid_avg is None else hybrid_avg:.6f}`",
        f"- Hybrid drift vs v83: `{float('nan') if hybrid_drift is None else hybrid_drift.get('mean_abs_drift', float('nan')):.6f}`",
        "",
        dataframe_to_markdown(pd.DataFrame([{"target": target, "source": source, "loss": hybrid_losses[target]} for target, source in hybrid_sources.items()])),
        "",
        "## Decision",
        "",
        "A positive result means the expert predictions disagree in label-useful ways and the next decoder should become a real latent-level MoE. A flat or negative result means the bottleneck is still the expert latent quality, not the final gate.",
    ]
    (output_dir / "report.md").write_text("\n".join(md), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train a small MoE/stacking decoder over fold-local channel fusion source predictions.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--source-dirs", nargs="+", default=[
        "outputs/fold_local_channel_fusion_decoder_no_pca_v1",
        "outputs/fold_local_channel_fusion_decoder_v1",
    ])
    parser.add_argument("--reference-submission", default="outputs/v83_repaired_v80/submission_v83_gq015_gs010.csv")
    parser.add_argument("--output-dir", default="outputs/fold_local_channel_moe_decoder_v1")
    parser.add_argument("--baseline-oof", default="outputs/fold_local_channel_fusion_decoder_no_pca_v1/oof_fold_local_selected.csv")
    parser.add_argument("--baseline-submission", default="outputs/fold_local_channel_fusion_decoder_no_pca_v1/submission_fold_local_selected.csv")
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--prior-alpha", type=float, default=8.0)
    parser.add_argument("--c-values", type=float, nargs="+", default=[0.03, 0.1, 0.3])
    parser.add_argument("--ridge-alphas", type=float, nargs="+", default=[5.0, 20.0, 80.0])
    parser.add_argument("--blends", type=float, nargs="+", default=[0.05, 0.1, 0.2, 0.35])
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
