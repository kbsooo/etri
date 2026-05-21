from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

from build_hourly_transformer_view_ensemble import collect_prediction_pairs, prediction_matrix
from train_hourly_transformer_encoder import dataframe_to_markdown
from train_pruned_state_decoder import average_log_loss, drift_vs_reference, safe_logit, subject_prior, write_prediction
from train_s2_sleep_retrieval_encoder import EPS, TARGET_COLUMNS, make_subject_time_folds, normalize_keys
from train_transformer_moe_head import add_panel_position


def collect_view_artifacts(input_dirs: list[Path]) -> tuple[list[str], list[np.ndarray], list[np.ndarray], np.ndarray, np.ndarray]:
    names: list[str] = []
    train_embeddings: list[np.ndarray] = []
    sample_embeddings: list[np.ndarray] = []
    oof_preds: list[np.ndarray] = []
    sub_preds: list[np.ndarray] = []
    for output_dir in input_dirs:
        for view_dir in sorted(path for path in output_dir.iterdir() if path.is_dir()):
            emb_path = view_dir / "embeddings.npz"
            oof_path = view_dir / "oof_targetwise.csv"
            sub_path = view_dir / "submission_targetwise.csv"
            if not (emb_path.exists() and oof_path.exists() and sub_path.exists()):
                continue
            emb = np.load(emb_path, allow_pickle=True)
            names.append(f"{output_dir.name}__{view_dir.name}")
            train_embeddings.append(np.asarray(emb["train"], dtype=float))
            sample_embeddings.append(np.asarray(emb["sample"], dtype=float))
            oof_preds.append(prediction_matrix(oof_path, target_prefix=True))
            sub_preds.append(prediction_matrix(sub_path, target_prefix=False))
    if not names:
        raise FileNotFoundError(f"No view embeddings found under: {input_dirs}")
    return names, train_embeddings, sample_embeddings, np.stack(oof_preds, axis=0), np.stack(sub_preds, axis=0)


def pca_embedding_block(
    train_z: np.ndarray,
    sample_z: np.ndarray,
    fit_idx: np.ndarray,
    eval_idx: np.ndarray,
    pca_dim: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    scaler = StandardScaler()
    z_fit = scaler.fit_transform(train_z[fit_idx])
    z_eval = scaler.transform(train_z[eval_idx])
    z_sample = scaler.transform(sample_z)
    dim = min(pca_dim, z_fit.shape[1], max(1, z_fit.shape[0] - 1))
    pca = PCA(n_components=dim, random_state=2026)
    fit_block = pca.fit_transform(z_fit)
    eval_block = pca.transform(z_eval)
    sample_block = pca.transform(z_sample)
    return fit_block, eval_block, sample_block


def build_fold_features(
    train_embeddings: list[np.ndarray],
    sample_embeddings: list[np.ndarray],
    source_oof: np.ndarray,
    source_sub: np.ndarray,
    target_i: int,
    fit_idx: np.ndarray,
    eval_idx: np.ndarray,
    train_panel: np.ndarray,
    sample_panel: np.ndarray,
    prior_fit: np.ndarray,
    prior_eval: np.ndarray,
    prior_sample: np.ndarray,
    pca_dim: int,
    use_embeddings: bool,
    use_logits: bool,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    fit_parts = []
    eval_parts = []
    sample_parts = []

    if use_logits:
        fit_logits = safe_logit(source_oof[:, fit_idx, target_i].T)
        eval_logits = safe_logit(source_oof[:, eval_idx, target_i].T)
        sample_logits = safe_logit(source_sub[:, :, target_i].T)
        fit_parts.extend([fit_logits, fit_logits.mean(axis=1, keepdims=True), fit_logits.std(axis=1, keepdims=True)])
        eval_parts.extend([eval_logits, eval_logits.mean(axis=1, keepdims=True), eval_logits.std(axis=1, keepdims=True)])
        sample_parts.extend([sample_logits, sample_logits.mean(axis=1, keepdims=True), sample_logits.std(axis=1, keepdims=True)])

    if use_embeddings:
        for train_z, sample_z in zip(train_embeddings, sample_embeddings):
            fit_block, eval_block, sample_block = pca_embedding_block(train_z, sample_z, fit_idx, eval_idx, pca_dim)
            fit_parts.append(fit_block)
            eval_parts.append(eval_block)
            sample_parts.append(sample_block)

    fit_parts.extend([train_panel[fit_idx].reshape(-1, 1), prior_fit.reshape(-1, 1)])
    eval_parts.extend([train_panel[eval_idx].reshape(-1, 1), prior_eval.reshape(-1, 1)])
    sample_parts.extend([sample_panel.reshape(-1, 1), prior_sample.reshape(-1, 1)])

    return np.concatenate(fit_parts, axis=1), np.concatenate(eval_parts, axis=1), np.concatenate(sample_parts, axis=1)


def train_nested_head(
    train: pd.DataFrame,
    sample: pd.DataFrame,
    train_embeddings: list[np.ndarray],
    sample_embeddings: list[np.ndarray],
    source_oof: np.ndarray,
    source_sub: np.ndarray,
    c_value: float,
    pca_dim: int,
    prior_alpha: float,
    use_embeddings: bool,
    use_logits: bool,
) -> tuple[np.ndarray, np.ndarray]:
    folds = make_subject_time_folds(train, 5)
    oof = np.zeros((len(train), len(TARGET_COLUMNS)))
    sample_folds = []
    train_panel = train["panel_position"].to_numpy(float)
    sample_panel = sample["panel_position"].to_numpy(float)
    for fold in folds:
        fold_sample = np.zeros((len(sample), len(TARGET_COLUMNS)))
        prior_fit_all = subject_prior(train.iloc[fold.train_idx], train.iloc[fold.train_idx], prior_alpha)
        prior_eval_all = subject_prior(train.iloc[fold.train_idx], train.iloc[fold.val_idx], prior_alpha)
        prior_sub_all = subject_prior(train.iloc[fold.train_idx], sample, prior_alpha)
        for target_i, target in enumerate(TARGET_COLUMNS):
            x_fit, x_eval, x_sub = build_fold_features(
                train_embeddings,
                sample_embeddings,
                source_oof,
                source_sub,
                target_i,
                fold.train_idx,
                fold.val_idx,
                train_panel,
                sample_panel,
                prior_fit_all[:, target_i],
                prior_eval_all[:, target_i],
                prior_sub_all[:, target_i],
                pca_dim,
                use_embeddings=use_embeddings,
                use_logits=use_logits,
            )
            scaler = StandardScaler()
            x_fit = scaler.fit_transform(x_fit)
            x_eval = scaler.transform(x_eval)
            x_sub = scaler.transform(x_sub)
            y_fit = train.iloc[fold.train_idx][target].to_numpy(int)
            if len(np.unique(y_fit)) < 2:
                pred_eval = np.full(len(fold.val_idx), float(y_fit[0]))
                pred_sub = np.full(len(sample), float(y_fit[0]))
            else:
                model = LogisticRegression(C=c_value, solver="lbfgs", max_iter=5000, random_state=2026)
                model.fit(x_fit, y_fit)
                pred_eval = model.predict_proba(x_eval)[:, 1]
                pred_sub = model.predict_proba(x_sub)[:, 1]
            oof[fold.val_idx, target_i] = pred_eval
            fold_sample[:, target_i] = pred_sub
        sample_folds.append(fold_sample)
    return np.clip(oof, EPS, 1.0 - EPS), np.clip(np.mean(sample_folds, axis=0), EPS, 1.0 - EPS)


def run(args: argparse.Namespace) -> None:
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    train, sample = add_panel_position(train, sample)
    names, train_embeddings, sample_embeddings, source_oof, source_sub = collect_view_artifacts([Path(item) for item in args.input_dirs])

    rows = []
    predictions = {}
    specs = [
        ("embedding_only", True, False),
        ("logit_plus_embedding", True, True),
    ]
    for spec_name, use_embeddings, use_logits in specs:
        for pca_dim in args.pca_dims:
            for c_value in args.c_values:
                oof, sub = train_nested_head(
                    train,
                    sample,
                    train_embeddings,
                    sample_embeddings,
                    source_oof,
                    source_sub,
                    c_value=c_value,
                    pca_dim=pca_dim,
                    prior_alpha=args.prior_alpha,
                    use_embeddings=use_embeddings,
                    use_logits=use_logits,
                )
                avg, per = average_log_loss(train[TARGET_COLUMNS], oof)
                name = f"{spec_name}_pca{pca_dim}_c{c_value:g}".replace(".", "p")
                rows.append({"source": name, "avg_log_loss": avg, **per})
                predictions[name] = (oof, sub)

    result_df = pd.DataFrame(rows).sort_values("avg_log_loss").reset_index(drop=True)
    best_name = str(result_df.iloc[0]["source"])
    best_oof, best_sub = predictions[best_name]
    drift = drift_vs_reference(sample, best_sub, Path(args.reference_submission) if args.reference_submission else None)
    write_prediction(output_dir / "oof_transformer_embedding_moe_best.csv", train, best_oof, oof=True)
    write_prediction(output_dir / "submission_transformer_embedding_moe_best.csv", sample, best_sub, oof=False)
    result_df.to_csv(output_dir / "embedding_moe_scores.csv", index=False)

    report = {
        "best_source": best_name,
        "best_avg_log_loss": float(result_df.iloc[0]["avg_log_loss"]),
        "drift_vs_reference": drift,
        "n_views": len(names),
        "views": names,
        "scores": result_df.to_dict(orient="records"),
    }
    (output_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    md = [
        "# Transformer Embedding MoE Head v1",
        "",
        "## Result",
        "",
        f"- Best source: `{best_name}`",
        f"- OOF avg logloss: `{float(result_df.iloc[0]['avg_log_loss']):.6f}`",
        f"- Drift vs v83 reference: `{drift.get('mean_abs_drift', float('nan')):.6f}`",
        f"- Views: `{len(names)}`",
        "",
        "## Scores",
        "",
        dataframe_to_markdown(result_df),
        "",
        "## Interpretation",
        "",
        "This head reads Transformer day embeddings directly. Each view embedding is reduced fold-safely with PCA inside the outer fold, then a small target-specific logistic head sees the reduced embeddings, optional expert logits, panel position, and fold-safe subject prior.",
    ]
    (output_dir / "report.md").write_text("\n".join(md), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train an embedding-level MoE head over Transformer view latents.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument(
        "--input-dirs",
        nargs="+",
        default=[
            "outputs/hourly_transformer_encoder_v1",
            "outputs/hourly_transformer_encoder_v1_extra",
            "outputs/multires10_transformer_encoder_v1",
            "outputs/multires30_transformer_encoder_v1",
        ],
    )
    parser.add_argument("--reference-submission", default="outputs/v83_repaired_v80/submission_v83_gq015_gs010.csv")
    parser.add_argument("--output-dir", default="outputs/transformer_embedding_moe_head_v1")
    parser.add_argument("--pca-dims", type=int, nargs="+", default=[2, 4, 8])
    parser.add_argument("--c-values", type=float, nargs="+", default=[0.01, 0.03, 0.10, 0.30])
    parser.add_argument("--prior-alpha", type=float, default=8.0)
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
