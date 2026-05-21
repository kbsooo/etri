from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
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
    fit_state_features,
    safe_logit,
    sigmoid,
    subject_prior,
    write_prediction,
)
from train_s2_sleep_retrieval_encoder import SEED, dataframe_to_markdown, make_subject_time_folds, merge_feature_tables, normalize_keys


Q_TARGETS = ["Q1", "Q2", "Q3"]
S_TARGETS = ["S1", "S2", "S3", "S4"]
Q_INDEX = [TARGET_COLUMNS.index(t) for t in Q_TARGETS]
S_INDEX = [TARGET_COLUMNS.index(t) for t in S_TARGETS]

PRESETS = [
    "only_rhythm",
    "no_ratio",
    "no_sleep",
    "no_temporal_delta",
    "drop_ratio_temporal_delta",
    "only_missingness",
    "no_missingness",
]
DECODER_PAIRS = [
    ("q_cluster4", "s_cluster6"),
    ("q_cluster4", "s_cluster8"),
    ("q_pattern", "s_pattern"),
    ("q_knn25", "s_knn25"),
    ("q_state_mean", "s_state_mean"),
    ("q_pattern", "s_cluster8"),
    ("q_cluster4", "s_pattern"),
]
WEIGHTS = [0.05, 0.10, 0.20, 0.35]


@dataclass(frozen=True)
class SourceSpec:
    preset: str
    q_decoder: str
    s_decoder: str
    weight: float

    @property
    def name(self) -> str:
        return f"{self.preset}__family_{self.q_decoder}_{self.s_decoder}_w{int(self.weight * 100):02d}"


def blend_with_prior(base: np.ndarray, pred: np.ndarray, weight: float) -> np.ndarray:
    return np.clip(sigmoid((1.0 - weight) * safe_logit(base) + weight * safe_logit(pred)), EPS, 1.0 - EPS)


def smooth_label_means(y_fit: np.ndarray, labels: np.ndarray, n_classes: int, alpha: float) -> np.ndarray:
    global_rate = y_fit.mean(axis=0)
    means = np.zeros((n_classes, y_fit.shape[1]), dtype=float)
    for class_i in range(n_classes):
        idx = labels == class_i
        means[class_i] = (y_fit[idx].sum(axis=0) + alpha * global_rate) / (idx.sum() + alpha)
    return np.clip(means, EPS, 1.0 - EPS)


def class_proba(model: LogisticRegression, x: np.ndarray, n_classes: int) -> np.ndarray:
    proba = np.zeros((len(x), n_classes), dtype=float)
    raw = model.predict_proba(x)
    for col_i, class_i in enumerate(model.classes_.astype(int)):
        proba[:, class_i] = raw[:, col_i]
    return proba


def fit_cluster_state(
    x_fit: np.ndarray,
    y_fit: np.ndarray,
    x_eval: np.ndarray,
    x_sample: np.ndarray,
    k: int,
    c_value: float,
    alpha: float,
) -> tuple[np.ndarray, np.ndarray]:
    k = min(k, max(2, len(x_fit) // 20))
    if k < 2:
        mean = y_fit.mean(axis=0)
        return np.tile(mean, (len(x_eval), 1)), np.tile(mean, (len(x_sample), 1))
    km = KMeans(n_clusters=k, n_init=20, random_state=SEED)
    labels = km.fit_predict(y_fit)
    means = smooth_label_means(y_fit, labels, k, alpha)
    if len(np.unique(labels)) < 2:
        pred = means[labels[0]]
        return np.tile(pred, (len(x_eval), 1)), np.tile(pred, (len(x_sample), 1))
    model = LogisticRegression(C=c_value, solver="lbfgs", max_iter=5000, random_state=SEED)
    model.fit(x_fit, labels)
    return class_proba(model, x_eval, k) @ means, class_proba(model, x_sample, k) @ means


def fit_pattern_state(
    x_fit: np.ndarray,
    y_fit: np.ndarray,
    x_eval: np.ndarray,
    x_sample: np.ndarray,
    c_value: float,
    alpha: float,
) -> tuple[np.ndarray, np.ndarray]:
    patterns, labels = np.unique(y_fit.astype(int), axis=0, return_inverse=True)
    n_classes = len(patterns)
    if n_classes < 2:
        pred = patterns[0].astype(float)
        return np.tile(pred, (len(x_eval), 1)), np.tile(pred, (len(x_sample), 1))
    means = smooth_label_means(y_fit, labels, n_classes, alpha)
    model = LogisticRegression(C=c_value, solver="lbfgs", max_iter=5000, random_state=SEED)
    model.fit(x_fit, labels)
    return class_proba(model, x_eval, n_classes) @ means, class_proba(model, x_sample, n_classes) @ means


def fit_label_knn(
    x_fit: np.ndarray,
    y_fit: np.ndarray,
    x_eval: np.ndarray,
    x_sample: np.ndarray,
    k: int,
) -> tuple[np.ndarray, np.ndarray]:
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
        return np.einsum("ij,ijk->ik", weights, y_fit[idx])

    return np.clip(pred(x_eval), EPS, 1.0 - EPS), np.clip(pred(x_sample), EPS, 1.0 - EPS)


def fit_family_decoder(
    decoder: str,
    x_fit: np.ndarray,
    y_fit: np.ndarray,
    x_eval: np.ndarray,
    x_sample: np.ndarray,
    args: argparse.Namespace,
) -> tuple[np.ndarray, np.ndarray]:
    if decoder in {"q_cluster4", "s_cluster6", "s_cluster8"}:
        k = {"q_cluster4": 4, "s_cluster6": 6, "s_cluster8": 8}[decoder]
        return fit_cluster_state(x_fit, y_fit, x_eval, x_sample, k, args.label_c, args.label_alpha)
    if decoder in {"q_pattern", "s_pattern"}:
        return fit_pattern_state(x_fit, y_fit, x_eval, x_sample, args.label_c, args.label_alpha)
    if decoder in {"q_knn25", "s_knn25"}:
        return fit_label_knn(x_fit, y_fit, x_eval, x_sample, 25)
    if decoder in {"q_state_mean", "s_state_mean"}:
        if decoder.startswith("q_"):
            cluster = fit_cluster_state(x_fit, y_fit, x_eval, x_sample, 4, args.label_c, args.label_alpha)
            pattern = fit_pattern_state(x_fit, y_fit, x_eval, x_sample, args.label_c, args.label_alpha)
        else:
            cluster6 = fit_cluster_state(x_fit, y_fit, x_eval, x_sample, 6, args.label_c, args.label_alpha)
            cluster8 = fit_cluster_state(x_fit, y_fit, x_eval, x_sample, 8, args.label_c, args.label_alpha)
            pattern = fit_pattern_state(x_fit, y_fit, x_eval, x_sample, args.label_c, args.label_alpha)
            knn = fit_label_knn(x_fit, y_fit, x_eval, x_sample, 25)
            return (
                np.mean([cluster6[0], cluster8[0], pattern[0], knn[0]], axis=0),
                np.mean([cluster6[1], cluster8[1], pattern[1], knn[1]], axis=0),
            )
        knn = fit_label_knn(x_fit, y_fit, x_eval, x_sample, 25)
        return (
            np.mean([cluster[0], pattern[0], knn[0]], axis=0),
            np.mean([cluster[1], pattern[1], knn[1]], axis=0),
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


def combine_family_preds(
    q_pred: np.ndarray,
    s_pred: np.ndarray,
    n_rows: int,
) -> np.ndarray:
    pred = np.zeros((n_rows, len(TARGET_COLUMNS)), dtype=float)
    pred[:, Q_INDEX] = q_pred
    pred[:, S_INDEX] = s_pred
    return np.clip(pred, EPS, 1.0 - EPS)


def run_preset_sources(
    preset: str,
    train: pd.DataFrame,
    sample: pd.DataFrame,
    train_x: pd.DataFrame,
    sample_x: pd.DataFrame,
    columns: list[str],
    args: argparse.Namespace,
) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray], list[dict]]:
    folds = make_subject_time_folds(train, args.folds)
    specs = [SourceSpec(preset, q_dec, s_dec, weight) for q_dec, s_dec in DECODER_PAIRS for weight in WEIGHTS]
    oof_by_name = {spec.name: np.zeros((len(train), len(TARGET_COLUMNS)), dtype=float) for spec in specs}
    sample_parts = {spec.name: [] for spec in specs}
    fold_rows = []

    q_decoders = sorted({q_dec for q_dec, _ in DECODER_PAIRS})
    s_decoders = sorted({s_dec for _, s_dec in DECODER_PAIRS})
    for fold_i, fold in enumerate(folds):
        fit_idx, val_idx = fold.train_idx, fold.val_idx
        fit_state, val_state, sample_state = fit_state_features(
            train_x,
            sample_x,
            train[KEY_COLUMNS],
            sample[KEY_COLUMNS],
            fit_idx,
            val_idx,
            columns,
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
        y_fit_full = train.iloc[fit_idx][TARGET_COLUMNS].to_numpy(int)
        y_fit_q = y_fit_full[:, Q_INDEX]
        y_fit_s = y_fit_full[:, S_INDEX]
        base_val = subject_prior(train.iloc[fit_idx], train.iloc[val_idx], args.subject_alpha)
        base_sample = subject_prior(train.iloc[fit_idx], sample, args.subject_alpha)
        q_raw = {
            decoder: fit_family_decoder(decoder, fit_s, y_fit_q, val_s, sample_s, args)
            for decoder in q_decoders
        }
        s_raw = {
            decoder: fit_family_decoder(decoder, fit_s, y_fit_s, val_s, sample_s, args)
            for decoder in s_decoders
        }
        fold_pred = {spec.name: np.zeros((len(sample), len(TARGET_COLUMNS)), dtype=float) for spec in specs}
        for q_dec, s_dec in DECODER_PAIRS:
            val_pred = combine_family_preds(q_raw[q_dec][0], s_raw[s_dec][0], len(val_idx))
            sample_pred = combine_family_preds(q_raw[q_dec][1], s_raw[s_dec][1], len(sample))
            for weight in WEIGHTS:
                spec = SourceSpec(preset, q_dec, s_dec, weight)
                oof_by_name[spec.name][val_idx] = blend_with_prior(base_val, val_pred, weight)
                fold_pred[spec.name] = blend_with_prior(base_sample, sample_pred, weight)
        for spec in specs:
            sample_parts[spec.name].append(fold_pred[spec.name])
        fold_rows.append(
            {
                "preset": preset,
                "fold": fold_i,
                "state_dim": int(fit_s.shape[1]),
                "fit_q_patterns": int(pd.DataFrame(y_fit_q).drop_duplicates().shape[0]),
                "fit_s_patterns": int(pd.DataFrame(y_fit_s).drop_duplicates().shape[0]),
                "fit_full_patterns": int(pd.DataFrame(y_fit_full).drop_duplicates().shape[0]),
            }
        )
    sample_by_name = {name: np.mean(np.stack(parts, axis=0), axis=0) for name, parts in sample_parts.items()}
    return oof_by_name, sample_by_name, fold_rows


def targetwise_select(
    y_df: pd.DataFrame,
    oof_by_source: dict[str, np.ndarray],
    sample_by_source: dict[str, np.ndarray],
) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    rows = []
    out_oof = np.zeros((len(y_df), len(TARGET_COLUMNS)), dtype=float)
    out_sample = np.zeros((next(iter(sample_by_source.values())).shape[0], len(TARGET_COLUMNS)), dtype=float)
    for target_i, target in enumerate(TARGET_COLUMNS):
        best = None
        for name, pred in oof_by_source.items():
            loss = float(log_loss(y_df[target].to_numpy(int), np.clip(pred[:, target_i], EPS, 1.0 - EPS), labels=[0, 1]))
            if best is None or loss < best["log_loss"]:
                family = "Q" if target in Q_TARGETS else "S"
                best = {"target": target, "family": family, "source": name, "log_loss": loss}
        if best is None:
            raise RuntimeError(target)
        rows.append(best)
        out_oof[:, target_i] = oof_by_source[best["source"]][:, target_i]
        out_sample[:, target_i] = sample_by_source[best["source"]][:, target_i]
    avg, _ = average_log_loss(y_df, out_oof)
    selected = pd.DataFrame(rows)
    selected["targetwise_avg_log_loss"] = avg
    return selected, np.clip(out_oof, EPS, 1.0 - EPS), np.clip(out_sample, EPS, 1.0 - EPS)


def parse_source_name(name: str) -> dict[str, object]:
    preset, rest = name.split("__family_", 1)
    body, weight_text = rest.rsplit("_w", 1)
    q_decoder = next(q for q, _ in DECODER_PAIRS if body.startswith(q + "_"))
    s_decoder = body[len(q_decoder) + 1 :]
    return {
        "preset": preset,
        "q_decoder": q_decoder,
        "s_decoder": s_decoder,
        "weight": int(weight_text) / 100.0,
    }


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    train_x, sample_x = merge_feature_tables(train, sample)
    preset_columns = build_preset_columns(train_x, sample_x, args)
    y_df = train[TARGET_COLUMNS].astype(int)
    score_rows = []
    fold_rows = []
    oof_by_source = {}
    sample_by_source = {}
    for preset in PRESETS:
        preset_oof, preset_sample, rows = run_preset_sources(preset, train, sample, train_x, sample_x, preset_columns[preset], args)
        fold_rows.extend(rows)
        for source_name, oof in preset_oof.items():
            sample_pred = preset_sample[source_name]
            avg, per_target = average_log_loss(y_df, oof)
            score_rows.append(
                {
                    "source": source_name,
                    **parse_source_name(source_name),
                    "avg_log_loss": avg,
                    **per_target,
                }
            )
            oof_by_source[source_name] = oof
            sample_by_source[source_name] = sample_pred
    score_df = pd.DataFrame(score_rows).sort_values("avg_log_loss")
    selected, tw_oof, tw_sample = targetwise_select(y_df, oof_by_source, sample_by_source)
    best_name = str(score_df.iloc[0]["source"])
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
        "decoder_pairs": DECODER_PAIRS,
        "args": vars(args),
    }
    score_df.to_csv(output_dir / "family_label_state_scores.csv", index=False)
    selected.to_csv(output_dir / "targetwise_selection.csv", index=False)
    pd.DataFrame(fold_rows).to_csv(output_dir / "fold_state_dims.csv", index=False)
    write_prediction(output_dir / "oof_family_label_state_best_global.csv", train, best_oof, oof=True)
    write_prediction(output_dir / "submission_family_label_state_best_global.csv", sample, best_sample, oof=False)
    write_prediction(output_dir / "oof_family_label_state_targetwise.csv", train, tw_oof, oof=True)
    write_prediction(output_dir / "submission_family_label_state_targetwise.csv", sample, tw_sample, oof=False)
    (output_dir / "report.json").write_text(json.dumps({"diagnostics": diagnostics, "scores": score_df.head(100).to_dict(orient="records")}, indent=2), encoding="utf-8")
    lines = [
        "# Family Label-State Decoder",
        "",
        "This experiment splits the sparse 7-label state bottleneck into Q-family and S-family intermediate states. Each family is decoded separately from the same feature-pruned state latent, recombined into seven probabilities, then blended with a fold-safe subject prior.",
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
        f"- Q/S pattern counts by fold: `{pd.DataFrame(fold_rows)[['fit_q_patterns', 'fit_s_patterns', 'fit_full_patterns']].drop_duplicates().to_dict(orient='records')}`",
    ]
    (output_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"best_global={best_name} avg={best_avg:.6f}")
    print(f"targetwise avg={tw_avg:.6f}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Q/S-family label-state decoder over pruned state latents.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--output-dir", default="outputs/family_label_state_decoder_v1")
    parser.add_argument("--reference-submission", default="outputs/v83_repaired_v80/submission_v83_gq015_gs010.csv")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--max-features", type=int, default=520)
    parser.add_argument("--pca-dim", type=int, default=28)
    parser.add_argument("--n-proto", type=int, default=10)
    parser.add_argument("--label-c", type=float, default=0.05)
    parser.add_argument("--label-alpha", type=float, default=8.0)
    parser.add_argument("--subject-alpha", type=float, default=10.0)
    return parser.parse_args()


if __name__ == "__main__":
    main()
