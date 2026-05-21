from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import log_loss
from sklearn.preprocessing import StandardScaler

from train_channel_latent_fusion_decoder import channel_group, compact_group_latent, load_embedding_view
from train_hourly_transformer_encoder import dataframe_to_markdown
from train_pruned_state_decoder import average_log_loss, drift_vs_reference, subject_prior, write_prediction
from train_s2_sleep_retrieval_encoder import EPS, TARGET_COLUMNS, make_subject_time_folds, normalize_keys


@dataclass(frozen=True)
class ExpertSpec:
    target: str
    feature: str
    model_family: str


DEFAULT_EXPERTS = [
    ExpertSpec("Q1", "full__cls_plus_physio__abs_plus_subrel_train", "ridge"),
    ExpertSpec("Q2", "only_cross_modal__cls_plus_all_groups__subrel_train", "logreg"),
    ExpertSpec("Q3", "full__cls_plus_all_groups__subrel_train", "ridge"),
    ExpertSpec("S1", "full__cls_plus_physio__abs_plus_subrel_train", "ridge"),
    ExpertSpec("S2", "full__cls_plus_body", "logreg"),
    ExpertSpec("S3", "full__cls_plus_all_groups__abs_plus_subrel_train", "logreg"),
    ExpertSpec("S4", "only_event__cls__abs_plus_subrel_train", "ridge"),
]


def parse_feature_name(feature: str) -> tuple[str, str, str]:
    view, rest = feature.split("__", 1)
    center = "absolute"
    for suffix in ("__abs_plus_subrel_train", "__subrel_train"):
        if rest.endswith(suffix):
            rest = rest[: -len(suffix)]
            center = suffix[2:]
            break
    return view, rest, center


def base_feature_matrix(view: dict[str, object], feature_part: str) -> tuple[np.ndarray, np.ndarray]:
    z_train = np.asarray(view["train"], dtype=np.float32)
    z_sample = np.asarray(view["sample"], dtype=np.float32)
    c_train = np.asarray(view["channel_train"], dtype=np.float32)
    c_sample = np.asarray(view["channel_sample"], dtype=np.float32)
    channels = list(view["channels"])
    group_sets = {
        "event": ("event",),
        "body": ("body",),
        "phone": ("phone",),
        "mobility": ("mobility",),
        "behavior": ("event", "phone", "mobility", "cross"),
        "physio": ("body", "light"),
        "all_groups": ("event", "body", "phone", "mobility", "ambience", "radio", "light", "cross", "other"),
    }
    if feature_part == "cls":
        return z_train, z_sample
    if feature_part.startswith("cls_plus_"):
        group_name = feature_part.removeprefix("cls_plus_")
        group_train = compact_group_latent(c_train, channels, group_sets[group_name])
        group_sample = compact_group_latent(c_sample, channels, group_sets[group_name])
        return np.concatenate([z_train, group_train], axis=1), np.concatenate([z_sample, group_sample], axis=1)
    return compact_group_latent(c_train, channels, group_sets[feature_part]), compact_group_latent(c_sample, channels, group_sets[feature_part])


def fold_center(
    x_all: np.ndarray,
    x_sample: np.ndarray,
    train_subjects: np.ndarray,
    sample_subjects: np.ndarray,
    fit_idx: np.ndarray,
    eval_idx: np.ndarray,
    center: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if center == "absolute":
        return x_all[fit_idx], x_all[eval_idx], x_sample

    fit_subjects = train_subjects[fit_idx]
    eval_subjects = train_subjects[eval_idx]
    x_fit = x_all[fit_idx]
    x_eval = x_all[eval_idx]
    rel_fit = np.zeros_like(x_fit)
    rel_eval = np.zeros_like(x_eval)
    rel_sample = np.zeros_like(x_sample)
    all_subjects = sorted(set(train_subjects.tolist()) | set(sample_subjects.tolist()))
    for subject in all_subjects:
        fit_mask = fit_subjects == subject
        if not fit_mask.any():
            mean = x_all[train_subjects == subject].mean(axis=0, keepdims=True)
        else:
            mean = x_fit[fit_mask].mean(axis=0, keepdims=True)
        rel_fit[fit_mask] = x_fit[fit_mask] - mean
        eval_mask = eval_subjects == subject
        if eval_mask.any():
            rel_eval[eval_mask] = x_eval[eval_mask] - mean
        sample_mask = sample_subjects == subject
        if sample_mask.any():
            rel_sample[sample_mask] = x_sample[sample_mask] - mean

    if center == "subrel_train":
        return rel_fit, rel_eval, rel_sample
    if center == "abs_plus_subrel_train":
        return (
            np.concatenate([x_fit, rel_fit], axis=1),
            np.concatenate([x_eval, rel_eval], axis=1),
            np.concatenate([x_sample, rel_sample], axis=1),
        )
    raise ValueError(f"Unknown center: {center}")


def compress_features(x_fit: np.ndarray, x_eval: np.ndarray, x_sample: np.ndarray, n_components: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    x_fit = np.nan_to_num(np.asarray(x_fit, dtype=np.float64), nan=0.0, posinf=0.0, neginf=0.0)
    x_eval = np.nan_to_num(np.asarray(x_eval, dtype=np.float64), nan=0.0, posinf=0.0, neginf=0.0)
    x_sample = np.nan_to_num(np.asarray(x_sample, dtype=np.float64), nan=0.0, posinf=0.0, neginf=0.0)
    std = x_fit.std(axis=0)
    keep = std > 1e-6
    if keep.any():
        x_fit = x_fit[:, keep]
        x_eval = x_eval[:, keep]
        x_sample = x_sample[:, keep]
    scaler = StandardScaler()
    fit_scaled = np.clip(scaler.fit_transform(x_fit), -20.0, 20.0)
    eval_scaled = np.clip(scaler.transform(x_eval), -20.0, 20.0)
    sample_scaled = np.clip(scaler.transform(x_sample), -20.0, 20.0)
    if n_components <= 0 or fit_scaled.shape[1] <= n_components:
        return fit_scaled, eval_scaled, sample_scaled
    pca = PCA(n_components=min(n_components, len(x_fit) - 1, fit_scaled.shape[1]), random_state=2026)
    return pca.fit_transform(fit_scaled), pca.transform(eval_scaled), pca.transform(sample_scaled)


def fit_target_model(
    family: str,
    x_fit: np.ndarray,
    y_fit: np.ndarray,
    x_eval: np.ndarray,
    x_sample: np.ndarray,
    prior_fit: np.ndarray,
    prior_eval: np.ndarray,
    prior_sample: np.ndarray,
    args: argparse.Namespace,
) -> tuple[np.ndarray, np.ndarray]:
    if family == "logreg":
        if len(np.unique(y_fit)) < 2:
            pred_eval = np.full(len(x_eval), float(y_fit[0]))
            pred_sample = np.full(len(x_sample), float(y_fit[0]))
        else:
            model = LogisticRegression(C=args.logreg_c, solver="lbfgs", max_iter=5000, random_state=2026)
            model.fit(x_fit, y_fit)
            pred_eval = model.predict_proba(x_eval)[:, 1]
            pred_sample = model.predict_proba(x_sample)[:, 1]
        return (1.0 - args.logreg_blend) * prior_eval + args.logreg_blend * pred_eval, (1.0 - args.logreg_blend) * prior_sample + args.logreg_blend * pred_sample
    if family == "ridge":
        model = Ridge(alpha=args.ridge_alpha, solver="lsqr", random_state=2026)
        model.fit(x_fit, y_fit.astype(float) - prior_fit)
        return prior_eval + args.ridge_blend * model.predict(x_eval), prior_sample + args.ridge_blend * model.predict(x_sample)
    if family == "hgb":
        model = HistGradientBoostingRegressor(
            max_iter=args.hgb_iter,
            learning_rate=args.hgb_lr,
            max_leaf_nodes=args.hgb_leaf_nodes,
            l2_regularization=args.hgb_l2,
            random_state=2026,
        )
        model.fit(x_fit, y_fit.astype(float) - prior_fit)
        return prior_eval + args.hgb_blend * model.predict(x_eval), prior_sample + args.hgb_blend * model.predict(x_sample)
    raise ValueError(f"Unknown model family: {family}")


def run(args: argparse.Namespace) -> None:
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    train_subjects = train["subject_id"].astype(str).to_numpy(object)
    sample_subjects = sample["subject_id"].astype(str).to_numpy(object)
    view_dirs = {Path(item).name: Path(item) for item in args.view_dirs}
    views = {name: load_embedding_view(path) for name, path in view_dirs.items()}

    specs = DEFAULT_EXPERTS
    raw_features: dict[str, tuple[np.ndarray, np.ndarray, str]] = {}
    for spec in specs:
        view_name, feature_part, center = parse_feature_name(spec.feature)
        if spec.feature not in raw_features:
            base_train, base_sample = base_feature_matrix(views[view_name], feature_part)
            raw_features[spec.feature] = (base_train, base_sample, center)

    folds = make_subject_time_folds(train, args.n_folds)
    predictions: dict[str, np.ndarray] = {"fold_local_selected": np.zeros((len(train), len(TARGET_COLUMNS)))}
    sample_folds = {"fold_local_selected": []}
    for family in ("ridge", "logreg", "hgb"):
        predictions[f"fold_local_all_{family}"] = np.zeros((len(train), len(TARGET_COLUMNS)))
        sample_folds[f"fold_local_all_{family}"] = []

    fold_rows = []
    for fold_i, fold in enumerate(folds, 1):
        selected_sample = np.zeros((len(sample), len(TARGET_COLUMNS)))
        family_sample = {family: np.zeros((len(sample), len(TARGET_COLUMNS))) for family in ("ridge", "logreg", "hgb")}
        prior_fit_all = subject_prior(train.iloc[fold.train_idx], train.iloc[fold.train_idx], args.prior_alpha)
        prior_eval_all = subject_prior(train.iloc[fold.train_idx], train.iloc[fold.val_idx], args.prior_alpha)
        prior_sample_all = subject_prior(train.iloc[fold.train_idx], sample, args.prior_alpha)
        for target_i, target in enumerate(TARGET_COLUMNS):
            spec = next(item for item in specs if item.target == target)
            base_train, base_sample, center = raw_features[spec.feature]
            x_fit_raw, x_eval_raw, x_sample_raw = fold_center(
                base_train,
                base_sample,
                train_subjects,
                sample_subjects,
                fold.train_idx,
                fold.val_idx,
                center,
            )
            x_fit, x_eval, x_sample = compress_features(x_fit_raw, x_eval_raw, x_sample_raw, args.pca_components)
            y_fit = train.iloc[fold.train_idx][target].to_numpy(int)
            y_eval = train.iloc[fold.val_idx][target].to_numpy(int)
            for family in ("ridge", "logreg", "hgb"):
                eval_pred, sample_pred = fit_target_model(
                    family,
                    x_fit,
                    y_fit,
                    x_eval,
                    x_sample,
                    prior_fit_all[:, target_i],
                    prior_eval_all[:, target_i],
                    prior_sample_all[:, target_i],
                    args,
                )
                eval_pred = np.clip(eval_pred, EPS, 1.0 - EPS)
                sample_pred = np.clip(sample_pred, EPS, 1.0 - EPS)
                predictions[f"fold_local_all_{family}"][fold.val_idx, target_i] = eval_pred
                family_sample[family][:, target_i] = sample_pred
                if family == spec.model_family:
                    predictions["fold_local_selected"][fold.val_idx, target_i] = eval_pred
                    selected_sample[:, target_i] = sample_pred
                    fold_rows.append(
                        {
                            "fold": fold_i,
                            "target": target,
                            "feature": spec.feature,
                            "family": family,
                            "loss": float(log_loss(y_eval, eval_pred, labels=[0, 1])),
                        }
                    )
        sample_folds["fold_local_selected"].append(selected_sample)
        for family, pred in family_sample.items():
            sample_folds[f"fold_local_all_{family}"].append(pred)

    sample_predictions = {name: np.clip(np.mean(parts, axis=0), EPS, 1.0 - EPS) for name, parts in sample_folds.items()}
    score_rows = []
    for name, pred in predictions.items():
        pred = np.clip(pred, EPS, 1.0 - EPS)
        predictions[name] = pred
        avg, per = average_log_loss(train[TARGET_COLUMNS], pred)
        drift = drift_vs_reference(sample, sample_predictions[name], Path(args.reference_submission) if args.reference_submission else None)
        score_rows.append({"source": name, "avg_log_loss": avg, "drift_vs_reference": drift.get("mean_abs_drift"), **per})
    score_df = pd.DataFrame(score_rows).sort_values("avg_log_loss").reset_index(drop=True)
    best_name = str(score_df.iloc[0]["source"])
    best_oof = predictions[best_name]
    best_sample = sample_predictions[best_name]
    best_avg, best_per = average_log_loss(train[TARGET_COLUMNS], best_oof)
    best_drift = drift_vs_reference(sample, best_sample, Path(args.reference_submission) if args.reference_submission else None)

    score_df.to_csv(output_dir / "fold_local_scores.csv", index=False)
    pd.DataFrame(fold_rows).to_csv(output_dir / "fold_target_losses.csv", index=False)
    pd.DataFrame([spec.__dict__ for spec in specs]).to_csv(output_dir / "expert_specs.csv", index=False)
    write_prediction(output_dir / "oof_fold_local_channel_fusion_best.csv", train, best_oof, oof=True)
    write_prediction(output_dir / "submission_fold_local_channel_fusion_best.csv", sample, best_sample, oof=False)

    report = {
        "best_source": best_name,
        "best_avg_log_loss": float(best_avg),
        "best_per_target": {target: float(best_per[target]) for target in TARGET_COLUMNS},
        "drift_vs_reference_best": best_drift,
        "scores": score_df.to_dict(orient="records"),
        "expert_specs": [spec.__dict__ for spec in specs],
        "fold_target_losses": fold_rows,
        "pca_components": args.pca_components,
    }
    (output_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    md = [
        "# Fold-Local Channel Fusion Decoder v1",
        "",
        "## Goal",
        "",
        "Re-evaluate the selected channel-latent experts with subject-relative centering computed inside each outer fold. This removes the optimistic train-wide subject mean used in the first fusion decoder.",
        "",
        "## Result",
        "",
        f"- Best source: `{best_name}`",
        f"- OOF avg logloss: `{best_avg:.6f}`",
        f"- Drift vs v83 reference: `{best_drift.get('mean_abs_drift', float('nan')):.6f}`",
        "",
        "## Candidate Scores",
        "",
        dataframe_to_markdown(score_df),
        "",
        "## Expert Specs",
        "",
        dataframe_to_markdown(pd.DataFrame([spec.__dict__ for spec in specs])),
        "",
        "## Fold Target Losses",
        "",
        dataframe_to_markdown(pd.DataFrame(fold_rows)),
        "",
        "## Decision",
        "",
        "If this remains close to the train-centered fusion result, the subject-relative decoder signal is not only an artifact of train-wide centering. A large drop means the previous fusion score was optimistic and the next decoder should use fold-local/transductive centering explicitly.",
    ]
    (output_dir / "report.md").write_text("\n".join(md), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fold-local subject-relative channel latent fusion decoder.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--view-dirs", nargs="+", default=[
        "outputs/channel_patch_transformer_encoder_v2/no_sleep",
        "outputs/channel_patch_transformer_encoder_v2/full",
        "outputs/channel_patch_transformer_encoder_v2/only_event",
        "outputs/channel_patch_transformer_encoder_v2/only_cross_modal",
    ])
    parser.add_argument("--reference-submission", default="outputs/v83_repaired_v80/submission_v83_gq015_gs010.csv")
    parser.add_argument("--output-dir", default="outputs/fold_local_channel_fusion_decoder_v1")
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--prior-alpha", type=float, default=8.0)
    parser.add_argument("--pca-components", type=int, default=16)
    parser.add_argument("--logreg-c", type=float, default=0.10)
    parser.add_argument("--logreg-blend", type=float, default=0.10)
    parser.add_argument("--ridge-alpha", type=float, default=5.0)
    parser.add_argument("--ridge-blend", type=float, default=0.10)
    parser.add_argument("--hgb-iter", type=int, default=40)
    parser.add_argument("--hgb-lr", type=float, default=0.03)
    parser.add_argument("--hgb-leaf-nodes", type=int, default=7)
    parser.add_argument("--hgb-l2", type=float, default=1.0)
    parser.add_argument("--hgb-blend", type=float, default=0.05)
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
