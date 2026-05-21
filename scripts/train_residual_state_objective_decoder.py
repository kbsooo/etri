from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from sklearn.metrics import log_loss
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

from train_extended_family_pruning_decoder import RECIPES, columns_for_recipe
from train_nested_pruned_state_decoder import preset_lookup
from train_pruned_state_decoder import (
    EPS,
    KEY_COLUMNS,
    TARGET_COLUMNS,
    Preset,
    average_log_loss,
    cap_columns_by_variance,
    columns_for_preset,
    drift_vs_reference,
    fit_residual_ridge,
    fit_state_features,
    safe_logit,
    sigmoid,
    subject_prior,
    write_prediction,
)
from train_s2_sleep_retrieval_encoder import SEED, dataframe_to_markdown, make_subject_time_folds, merge_feature_tables, normalize_keys


PRESETS = [
    "only_rhythm",
    "no_ratio",
    "no_sleep",
    "no_missingness",
    "only_missingness",
    "no_temporal_delta",
    "only_deviation_cross_modal",
    "only_rhythm_deviation_cross_modal",
    "only_missingness_cross_modal",
    "drop_ratio_temporal_delta",
    "drop_sleep_late",
]
DECODERS = ["residual_ridge", "residual_proto", "residual_knn", "residual_mean"]
WEIGHTS = [0.03, 0.05, 0.10, 0.20, 0.35]


@dataclass(frozen=True)
class SourceSpec:
    preset: str
    decoder: str
    weight: float

    @property
    def name(self) -> str:
        return f"{self.preset}__{self.decoder}_w{int(self.weight * 100):02d}"


def smooth_logit_residual(y: np.ndarray, base: np.ndarray) -> np.ndarray:
    y_smooth = (y * 0.98) + 0.01
    return safe_logit(y_smooth) - safe_logit(base)


def apply_residual(base: np.ndarray, residual: np.ndarray, weight: float) -> np.ndarray:
    return np.clip(sigmoid(safe_logit(base) + weight * residual), EPS, 1.0 - EPS)


def fit_residual_proto(
    x_fit: np.ndarray,
    y_fit: np.ndarray,
    base_fit: np.ndarray,
    base_eval: np.ndarray,
    base_sample: np.ndarray,
    x_eval: np.ndarray,
    x_sample: np.ndarray,
    k: int,
    alpha: float,
) -> tuple[np.ndarray, np.ndarray]:
    residual = smooth_logit_residual(y_fit, base_fit)
    k = min(k, max(2, len(x_fit) // 20))
    if k < 2:
        value = float(np.mean(residual))
        return np.full(len(x_eval), value), np.full(len(x_sample), value)
    km = KMeans(n_clusters=k, n_init=10, random_state=SEED)
    dist_fit = km.fit_transform(x_fit)
    labels = km.labels_
    global_resid = float(np.mean(residual))
    means = np.zeros(k, dtype=float)
    for cluster in range(k):
        idx = labels == cluster
        means[cluster] = (residual[idx].sum() + alpha * global_resid) / (idx.sum() + alpha)

    def pred(dist: np.ndarray) -> np.ndarray:
        scale = np.nanmedian(dist_fit) + 1e-6
        logits = -dist / scale
        logits -= logits.max(axis=1, keepdims=True)
        weights = np.exp(logits)
        weights /= weights.sum(axis=1, keepdims=True)
        return weights @ means

    return pred(km.transform(x_eval)), pred(km.transform(x_sample))


def fit_residual_knn(
    x_fit: np.ndarray,
    y_fit: np.ndarray,
    base_fit: np.ndarray,
    x_eval: np.ndarray,
    x_sample: np.ndarray,
    k: int,
) -> tuple[np.ndarray, np.ndarray]:
    residual = smooth_logit_residual(y_fit, base_fit)
    k = min(k, len(x_fit))
    nn = NearestNeighbors(n_neighbors=k, metric="euclidean")
    nn.fit(x_fit)

    def pred(x: np.ndarray) -> np.ndarray:
        dist, idx = nn.kneighbors(x)
        scale = np.nanmedian(dist) + 1e-6
        logits = -dist / scale
        logits -= logits.max(axis=1, keepdims=True)
        weights = np.exp(logits)
        weights /= weights.sum(axis=1, keepdims=True)
        return (weights * residual[idx]).sum(axis=1)

    return pred(x_eval), pred(x_sample)


def source_prediction(
    decoder: str,
    x_fit: np.ndarray,
    y_fit: np.ndarray,
    x_eval: np.ndarray,
    x_sample: np.ndarray,
    base_fit: np.ndarray,
    base_eval: np.ndarray,
    base_sample: np.ndarray,
    args: argparse.Namespace,
) -> tuple[np.ndarray, np.ndarray]:
    if decoder == "residual_ridge":
        pred_eval, pred_sample = fit_residual_ridge(x_fit, y_fit, base_fit, base_eval, base_sample, x_eval, x_sample)
        return safe_logit(pred_eval) - safe_logit(base_eval), safe_logit(pred_sample) - safe_logit(base_sample)
    if decoder == "residual_proto":
        return fit_residual_proto(x_fit, y_fit, base_fit, base_eval, base_sample, x_eval, x_sample, args.n_resid_proto, args.resid_proto_alpha)
    if decoder == "residual_knn":
        return fit_residual_knn(x_fit, y_fit, base_fit, x_eval, x_sample, args.knn_k)
    if decoder == "residual_mean":
        proto_eval, proto_sample = fit_residual_proto(
            x_fit,
            y_fit,
            base_fit,
            base_eval,
            base_sample,
            x_eval,
            x_sample,
            args.n_resid_proto,
            args.resid_proto_alpha,
        )
        knn_eval, knn_sample = fit_residual_knn(x_fit, y_fit, base_fit, x_eval, x_sample, args.knn_k)
        ridge_eval, ridge_sample = source_prediction(
            "residual_ridge",
            x_fit,
            y_fit,
            x_eval,
            x_sample,
            base_fit,
            base_eval,
            base_sample,
            args,
        )
        return (
            np.mean(np.vstack([proto_eval, knn_eval, ridge_eval]), axis=0),
            np.mean(np.vstack([proto_sample, knn_sample, ridge_sample]), axis=0),
        )
    raise ValueError(decoder)


def build_preset_columns(train_x: pd.DataFrame, sample_x: pd.DataFrame, args: argparse.Namespace) -> dict[str, list[str]]:
    all_cols = train_x.columns.tolist()
    base_presets: dict[str, Preset] = preset_lookup()
    recipe_lookup = {recipe.name: recipe for recipe in RECIPES}
    out = {}
    for name in PRESETS:
        if name in recipe_lookup:
            columns = columns_for_recipe(all_cols, recipe_lookup[name])
        else:
            columns = columns_for_preset(all_cols, base_presets[name])
        out[name] = cap_columns_by_variance(train_x, sample_x, columns, args.max_features)
    return out


def run_source(
    spec: SourceSpec,
    train: pd.DataFrame,
    sample: pd.DataFrame,
    train_x: pd.DataFrame,
    sample_x: pd.DataFrame,
    preset_columns: dict[str, list[str]],
    args: argparse.Namespace,
) -> tuple[np.ndarray, np.ndarray, list[dict]]:
    folds = make_subject_time_folds(train, args.folds)
    oof = np.zeros((len(train), len(TARGET_COLUMNS)), dtype=float)
    sample_folds = []
    fold_rows = []
    for fold_i, fold in enumerate(folds):
        fit_idx, val_idx = fold.train_idx, fold.val_idx
        fit_state, val_state, sample_state = fit_state_features(
            train_x,
            sample_x,
            train[KEY_COLUMNS],
            sample[KEY_COLUMNS],
            fit_idx,
            val_idx,
            preset_columns[spec.preset],
            args.pca_dim,
            args.n_proto,
        )
        if val_state is None:
            raise RuntimeError("validation state missing")
        imputer = SimpleImputer(strategy="median", keep_empty_features=True)
        scaler = StandardScaler()
        fit_s = scaler.fit_transform(imputer.fit_transform(fit_state))
        val_s = scaler.transform(imputer.transform(val_state))
        sample_s = scaler.transform(imputer.transform(sample_state))
        base_fit = subject_prior(train.iloc[fit_idx], train.iloc[fit_idx], args.subject_alpha)
        base_val = subject_prior(train.iloc[fit_idx], train.iloc[val_idx], args.subject_alpha)
        base_sample = subject_prior(train.iloc[fit_idx], sample, args.subject_alpha)
        fold_sample = np.zeros((len(sample), len(TARGET_COLUMNS)), dtype=float)
        for target_i, target in enumerate(TARGET_COLUMNS):
            y_fit = train.iloc[fit_idx][target].to_numpy(int)
            resid_val, resid_sample = source_prediction(
                spec.decoder,
                fit_s,
                y_fit,
                val_s,
                sample_s,
                base_fit[:, target_i],
                base_val[:, target_i],
                base_sample[:, target_i],
                args,
            )
            oof[val_idx, target_i] = apply_residual(base_val[:, target_i], resid_val, spec.weight)
            fold_sample[:, target_i] = apply_residual(base_sample[:, target_i], resid_sample, spec.weight)
        sample_folds.append(fold_sample)
        fold_rows.append({"source": spec.name, "fold": fold_i, "state_dim": int(fit_s.shape[1])})
    return oof, np.mean(np.stack(sample_folds, axis=0), axis=0), fold_rows


def targetwise_select(y_df: pd.DataFrame, oof_by_source: dict[str, np.ndarray], sample_by_source: dict[str, np.ndarray]) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    rows = []
    out_oof = np.zeros((len(y_df), len(TARGET_COLUMNS)), dtype=float)
    out_sample = np.zeros((next(iter(sample_by_source.values())).shape[0], len(TARGET_COLUMNS)), dtype=float)
    for target_i, target in enumerate(TARGET_COLUMNS):
        best = None
        for name, pred in oof_by_source.items():
            loss = float(log_loss(y_df[target].to_numpy(int), np.clip(pred[:, target_i], EPS, 1.0 - EPS), labels=[0, 1]))
            if best is None or loss < best["log_loss"]:
                best = {"target": target, "source": name, "log_loss": loss}
        if best is None:
            raise RuntimeError(target)
        rows.append(best)
        out_oof[:, target_i] = oof_by_source[best["source"]][:, target_i]
        out_sample[:, target_i] = sample_by_source[best["source"]][:, target_i]
    avg, _ = average_log_loss(y_df, out_oof)
    selected = pd.DataFrame(rows)
    selected["targetwise_avg_log_loss"] = avg
    return selected, np.clip(out_oof, EPS, 1.0 - EPS), np.clip(out_sample, EPS, 1.0 - EPS)


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    train_x, sample_x = merge_feature_tables(train, sample)
    preset_columns = build_preset_columns(train_x, sample_x, args)
    specs = [SourceSpec(preset, decoder, weight) for preset in PRESETS for decoder in DECODERS for weight in WEIGHTS]
    score_rows = []
    fold_rows = []
    oof_by_source = {}
    sample_by_source = {}
    y_df = train[TARGET_COLUMNS].astype(int)
    for spec in specs:
        oof, sample_pred, rows = run_source(spec, train, sample, train_x, sample_x, preset_columns, args)
        avg, per_target = average_log_loss(y_df, oof)
        score_rows.append({"source": spec.name, "preset": spec.preset, "decoder": spec.decoder, "weight": spec.weight, "avg_log_loss": avg, **per_target})
        fold_rows.extend(rows)
        oof_by_source[spec.name] = oof
        sample_by_source[spec.name] = sample_pred

    score_df = pd.DataFrame(score_rows).sort_values("avg_log_loss")
    selected, tw_oof, tw_sample = targetwise_select(y_df, oof_by_source, sample_by_source)
    best_name = score_df.iloc[0]["source"]
    best_oof = oof_by_source[best_name]
    best_sample = sample_by_source[best_name]
    best_avg, best_targets = average_log_loss(y_df, best_oof)
    tw_avg, tw_targets = average_log_loss(y_df, tw_oof)
    diagnostics = {
        "best_global_key": best_name,
        "best_global": {"avg_log_loss": best_avg, **best_targets},
        "targetwise": {"avg_log_loss": tw_avg, **tw_targets},
        "targetwise_selection": selected.to_dict(orient="records"),
        "drift_vs_reference_best_global": drift_vs_reference(sample, best_sample, Path(args.reference_submission) if args.reference_submission else None),
        "drift_vs_reference_targetwise": drift_vs_reference(sample, tw_sample, Path(args.reference_submission) if args.reference_submission else None),
        "preset_feature_counts": {name: len(cols) for name, cols in preset_columns.items()},
        "args": vars(args),
    }
    score_df.to_csv(output_dir / "residual_state_scores.csv", index=False)
    pd.DataFrame(fold_rows).to_csv(output_dir / "fold_state_dims.csv", index=False)
    selected.to_csv(output_dir / "targetwise_selection.csv", index=False)
    write_prediction(output_dir / "oof_residual_state_best_global.csv", train, best_oof, oof=True)
    write_prediction(output_dir / "submission_residual_state_best_global.csv", sample, best_sample, oof=False)
    write_prediction(output_dir / "oof_residual_state_targetwise.csv", train, tw_oof, oof=True)
    write_prediction(output_dir / "submission_residual_state_targetwise.csv", sample, tw_sample, oof=False)
    (output_dir / "report.json").write_text(json.dumps({"diagnostics": diagnostics, "scores": score_df.head(80).to_dict(orient="records")}, indent=2), encoding="utf-8")
    lines = [
        "# Residual State Objective Decoder",
        "",
        "This experiment predicts logit residuals over subject-prior from state latents using residual prototypes, residual nearest-neighbor, and residual ridge objectives.",
        "",
        "## Best Sources",
        "",
        dataframe_to_markdown(score_df.head(30)),
        "",
        "## Target-wise Selection",
        "",
        dataframe_to_markdown(selected),
        "",
        "## Summary",
        "",
        f"- Best global: `{best_name}` avg `{best_avg:.6f}`",
        f"- Target-wise avg: `{tw_avg:.6f}`",
        f"- Best global drift vs reference: `{diagnostics['drift_vs_reference_best_global'].get('mean_abs_drift', float('nan')):.6f}`",
        f"- Target-wise drift vs reference: `{diagnostics['drift_vs_reference_targetwise'].get('mean_abs_drift', float('nan')):.6f}`",
    ]
    (output_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"best_global={best_name} avg={best_avg:.6f}")
    print(f"targetwise avg={tw_avg:.6f}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Residual objective decoders over subject-normalized state latents.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--output-dir", default="outputs/residual_state_objective_decoder_v1")
    parser.add_argument("--reference-submission", default="outputs/v83_repaired_v80/submission_v83_gq015_gs010.csv")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--max-features", type=int, default=520)
    parser.add_argument("--pca-dim", type=int, default=28)
    parser.add_argument("--n-proto", type=int, default=10)
    parser.add_argument("--n-resid-proto", type=int, default=12)
    parser.add_argument("--resid-proto-alpha", type=float, default=8.0)
    parser.add_argument("--knn-k", type=int, default=35)
    parser.add_argument("--n-label-proto", type=int, default=12)
    parser.add_argument("--logreg-c", type=float, default=0.03)
    parser.add_argument("--subject-alpha", type=float, default=10.0)
    parser.add_argument("--max-pairs", type=int, default=10000)
    return parser.parse_args()


if __name__ == "__main__":
    main()
