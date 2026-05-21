from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.preprocessing import StandardScaler

from train_extended_family_pruning_decoder import RECIPES, columns_for_recipe
from train_nested_pruned_state_decoder import preset_lookup, source_prediction
from train_pruned_state_decoder import (
    EPS,
    KEY_COLUMNS,
    TARGET_COLUMNS,
    Preset,
    average_log_loss,
    cap_columns_by_variance,
    columns_for_preset,
    drift_vs_reference,
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
    "drop_ratio_temporal_delta",
]
DECODERS = ["hgb", "residual_ridge", "state_mean"]
WEIGHTS = [0.05, 0.10, 0.20]


@dataclass(frozen=True)
class SourceSpec:
    preset: str
    decoder: str
    weight: float

    @property
    def name(self) -> str:
        return f"{self.preset}__multiscale_{self.decoder}_w{int(self.weight * 100):02d}"


def key_dates(keys: pd.DataFrame) -> np.ndarray:
    dates = pd.to_datetime(keys["sleep_date"], errors="coerce")
    if dates.isna().any():
        dates = pd.to_datetime(keys["lifelog_date"], errors="coerce")
    return dates.astype("int64").to_numpy()


def summarize_pool(z: np.ndarray, pool_idx: np.ndarray, row: np.ndarray, global_mean: np.ndarray, global_std: np.ndarray) -> np.ndarray:
    if len(pool_idx) < 2:
        mean = global_mean
        std = global_std
        rank = np.full_like(row, 0.5)
        dist_stats = np.array([0.0, 0.0, 0.0, 0.0], dtype=float)
    else:
        pool = z[pool_idx]
        mean = pool.mean(axis=0)
        std = pool.std(axis=0) + 1e-6
        rank = (pool <= row).mean(axis=0)
        dist = np.sqrt(((pool - row) ** 2).mean(axis=1))
        dist_stats = np.array(
            [
                float(np.min(dist)),
                float(np.mean(dist)),
                float(np.quantile(dist, 0.25)),
                float(np.quantile(dist, 0.75)),
            ],
            dtype=float,
        )
    dev = (row - mean) / std
    return np.concatenate([dev, np.abs(dev), rank - 0.5, np.abs(rank - 0.5), dist_stats])


def multiscale_state_from_z(
    fit_z: np.ndarray,
    query_z: np.ndarray,
    fit_keys: pd.DataFrame,
    query_keys: pd.DataFrame,
    fit_self_positions: np.ndarray | None,
) -> np.ndarray:
    fit_subjects = fit_keys["subject_id"].to_numpy(str)
    query_subjects = query_keys["subject_id"].to_numpy(str)
    fit_dates = key_dates(fit_keys)
    query_dates = key_dates(query_keys)
    global_mean = fit_z.mean(axis=0)
    global_std = fit_z.std(axis=0) + 1e-6
    out = []
    for row_i, (sid, date_value) in enumerate(zip(query_subjects, query_dates)):
        row = query_z[row_i]
        same = np.flatnonzero(fit_subjects == sid)
        if fit_self_positions is not None:
            self_pos = fit_self_positions[row_i]
            same = same[same != self_pos]
        past = same[fit_dates[same] < date_value]
        recent7 = past[np.argsort(fit_dates[past])[-7:]] if len(past) else past
        recent14 = past[np.argsort(fit_dates[past])[-14:]] if len(past) else past
        fallback = same if len(same) >= 2 else np.arange(len(fit_z))
        blocks = [
            row,
            (row - global_mean) / global_std,
            np.abs((row - global_mean) / global_std),
            summarize_pool(fit_z, fallback, row, global_mean, global_std),
            summarize_pool(fit_z, past, row, global_mean, global_std),
            summarize_pool(fit_z, recent7, row, global_mean, global_std),
            summarize_pool(fit_z, recent14, row, global_mean, global_std),
        ]
        subject_span = fit_dates[same]
        if len(subject_span):
            denom = max(1.0, float(subject_span.max() - subject_span.min()))
            rel_pos = (float(date_value - subject_span.min()) / denom) if denom else 0.5
            past_frac = len(past) / max(1, len(same))
        else:
            rel_pos, past_frac = 0.5, 0.0
        blocks.append(np.array([rel_pos, past_frac, len(same), len(past), len(recent7), len(recent14)], dtype=float))
        out.append(np.concatenate(blocks))
    return np.vstack(out)


def fit_multiscale_state_features(
    train_x: pd.DataFrame,
    sample_x: pd.DataFrame,
    train_keys: pd.DataFrame,
    sample_keys: pd.DataFrame,
    fit_idx: np.ndarray,
    eval_idx: np.ndarray,
    columns: list[str],
    pca_dim: int,
    n_proto: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    fit_raw = train_x.iloc[fit_idx][columns].replace([np.inf, -np.inf], np.nan)
    eval_raw = train_x.iloc[eval_idx][columns].replace([np.inf, -np.inf], np.nan)
    sample_raw = sample_x[columns].replace([np.inf, -np.inf], np.nan)
    imputer = SimpleImputer(strategy="median", keep_empty_features=True)
    scaler = StandardScaler()
    fit_scaled = scaler.fit_transform(imputer.fit_transform(fit_raw))
    eval_scaled = scaler.transform(imputer.transform(eval_raw))
    sample_scaled = scaler.transform(imputer.transform(sample_raw))
    dim = min(pca_dim, fit_scaled.shape[1], max(1, fit_scaled.shape[0] - 1))
    pca = PCA(n_components=dim, random_state=SEED)
    fit_z = pca.fit_transform(fit_scaled)
    eval_z = pca.transform(eval_scaled)
    sample_z = pca.transform(sample_scaled)
    fit_keys = train_keys.iloc[fit_idx].reset_index(drop=True)
    eval_keys = train_keys.iloc[eval_idx].reset_index(drop=True)
    sample_keys = sample_keys.reset_index(drop=True)
    fit_state = multiscale_state_from_z(fit_z, fit_z, fit_keys, fit_keys, np.arange(len(fit_idx)))
    eval_state = multiscale_state_from_z(fit_z, eval_z, fit_keys, eval_keys, None)
    sample_state = multiscale_state_from_z(fit_z, sample_z, fit_keys, sample_keys, None)
    k = min(n_proto, max(2, len(fit_state) // 25))
    if k >= 2:
        km = KMeans(n_clusters=k, n_init=10, random_state=SEED)
        fit_dist = km.fit_transform(fit_state)
        eval_dist = km.transform(eval_state)
        sample_dist = km.transform(sample_state)

        def soft(dist: np.ndarray) -> np.ndarray:
            scale = np.nanmedian(dist) + 1e-6
            logits = -dist / scale
            logits -= logits.max(axis=1, keepdims=True)
            weights = np.exp(logits)
            return weights / weights.sum(axis=1, keepdims=True)

        fit_state = np.concatenate([fit_state, soft(fit_dist)], axis=1)
        eval_state = np.concatenate([eval_state, soft(eval_dist)], axis=1)
        sample_state = np.concatenate([sample_state, soft(sample_dist)], axis=1)
    return fit_state, eval_state, sample_state


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
        fit_state, val_state, sample_state = fit_multiscale_state_features(
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
            if spec.decoder == "state_mean":
                preds = [
                    source_prediction(decoder, fit_s, y_fit, val_s, sample_s, base_fit[:, target_i], base_val[:, target_i], base_sample[:, target_i], args)
                    for decoder in ("logreg", "hgb", "rank_pairwise", "residual_ridge")
                ]
                val_pred = np.mean([p[0] for p in preds], axis=0)
                sample_pred = np.mean([p[1] for p in preds], axis=0)
            else:
                val_pred, sample_pred = source_prediction(
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
            oof[val_idx, target_i] = sigmoid((1.0 - spec.weight) * safe_logit(base_val[:, target_i]) + spec.weight * safe_logit(val_pred))
            fold_sample[:, target_i] = sigmoid((1.0 - spec.weight) * safe_logit(base_sample[:, target_i]) + spec.weight * safe_logit(sample_pred))
        sample_folds.append(np.clip(fold_sample, EPS, 1.0 - EPS))
        fold_rows.append({"source": spec.name, "fold": fold_i, "state_dim": int(fit_s.shape[1])})
    return np.clip(oof, EPS, 1.0 - EPS), np.mean(np.stack(sample_folds, axis=0), axis=0), fold_rows


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
    names = [SourceSpec(preset, decoder, weight).name for decoder in DECODERS for weight in WEIGHTS]
    oof_by_name = {name: np.zeros((len(train), len(TARGET_COLUMNS)), dtype=float) for name in names}
    sample_parts = {name: [] for name in names}
    fold_rows = []
    for fold_i, fold in enumerate(folds):
        fit_idx, val_idx = fold.train_idx, fold.val_idx
        fit_state, val_state, sample_state = fit_multiscale_state_features(
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
        imputer = SimpleImputer(strategy="median", keep_empty_features=True)
        scaler = StandardScaler()
        fit_s = scaler.fit_transform(imputer.fit_transform(fit_state))
        val_s = scaler.transform(imputer.transform(val_state))
        sample_s = scaler.transform(imputer.transform(sample_state))
        base_fit = subject_prior(train.iloc[fit_idx], train.iloc[fit_idx], args.subject_alpha)
        base_val = subject_prior(train.iloc[fit_idx], train.iloc[val_idx], args.subject_alpha)
        base_sample = subject_prior(train.iloc[fit_idx], sample, args.subject_alpha)
        fold_pred = {name: np.zeros((len(sample), len(TARGET_COLUMNS)), dtype=float) for name in names}
        for target_i, target in enumerate(TARGET_COLUMNS):
            y_fit = train.iloc[fit_idx][target].to_numpy(int)
            raw_preds = {}
            for decoder in ("hgb", "residual_ridge"):
                raw_preds[decoder] = source_prediction(
                    decoder,
                    fit_s,
                    y_fit,
                    val_s,
                    sample_s,
                    base_fit[:, target_i],
                    base_val[:, target_i],
                    base_sample[:, target_i],
                    args,
                )
            raw_preds["state_mean"] = (
                np.mean([raw_preds["hgb"][0], raw_preds["residual_ridge"][0]], axis=0),
                np.mean([raw_preds["hgb"][1], raw_preds["residual_ridge"][1]], axis=0),
            )
            for decoder in DECODERS:
                val_pred, sample_pred = raw_preds[decoder]
                for weight in WEIGHTS:
                    name = SourceSpec(preset, decoder, weight).name
                    oof_by_name[name][val_idx, target_i] = sigmoid(
                        (1.0 - weight) * safe_logit(base_val[:, target_i]) + weight * safe_logit(val_pred)
                    )
                    fold_pred[name][:, target_i] = sigmoid(
                        (1.0 - weight) * safe_logit(base_sample[:, target_i]) + weight * safe_logit(sample_pred)
                    )
        for name in names:
            sample_parts[name].append(np.clip(fold_pred[name], EPS, 1.0 - EPS))
        fold_rows.append({"preset": preset, "fold": fold_i, "state_dim": int(fit_s.shape[1])})
    sample_by_name = {name: np.mean(np.stack(parts, axis=0), axis=0) for name, parts in sample_parts.items()}
    return {k: np.clip(v, EPS, 1.0 - EPS) for k, v in oof_by_name.items()}, sample_by_name, fold_rows


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
    y_df = train[TARGET_COLUMNS].astype(int)
    score_rows = []
    fold_rows = []
    oof_by_source = {}
    sample_by_source = {}
    for preset in PRESETS:
        preset_oof, preset_sample, rows = run_preset_sources(
            preset,
            train,
            sample,
            train_x,
            sample_x,
            preset_columns[preset],
            args,
        )
        fold_rows.extend(rows)
        for source_name, oof in preset_oof.items():
            sample_pred = preset_sample[source_name]
            avg, per_target = average_log_loss(y_df, oof)
            source_tail, weight_text = source_name.split("__multiscale_", 1)[1].rsplit("_w", 1)
            score_rows.append(
                {
                    "source": source_name,
                    "preset": preset,
                    "decoder": source_tail,
                    "weight": int(weight_text) / 100.0,
                    "avg_log_loss": avg,
                    **per_target,
                }
            )
            oof_by_source[source_name] = oof
            sample_by_source[source_name] = sample_pred
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
    score_df.to_csv(output_dir / "multiscale_state_scores.csv", index=False)
    selected.to_csv(output_dir / "targetwise_selection.csv", index=False)
    pd.DataFrame(fold_rows).to_csv(output_dir / "fold_state_dims.csv", index=False)
    write_prediction(output_dir / "oof_multiscale_state_best_global.csv", train, best_oof, oof=True)
    write_prediction(output_dir / "submission_multiscale_state_best_global.csv", sample, best_sample, oof=False)
    write_prediction(output_dir / "oof_multiscale_state_targetwise.csv", train, tw_oof, oof=True)
    write_prediction(output_dir / "submission_multiscale_state_targetwise.csv", sample, tw_sample, oof=False)
    (output_dir / "report.json").write_text(json.dumps({"diagnostics": diagnostics, "scores": score_df.head(80).to_dict(orient="records")}, indent=2), encoding="utf-8")
    lines = [
        "# Multiscale Subject State Decoder",
        "",
        "This experiment strengthens the encoder state with subject-history baselines, past-only ranks, recent 7/14-day deviations, and distance/novelty summaries before applying state decoders.",
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
    parser = argparse.ArgumentParser(description="Multiscale subject-state decoder experiment.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--output-dir", default="outputs/multiscale_subject_state_decoder_v1")
    parser.add_argument("--reference-submission", default="outputs/v83_repaired_v80/submission_v83_gq015_gs010.csv")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--max-features", type=int, default=520)
    parser.add_argument("--pca-dim", type=int, default=24)
    parser.add_argument("--n-proto", type=int, default=10)
    parser.add_argument("--n-label-proto", type=int, default=12)
    parser.add_argument("--logreg-c", type=float, default=0.03)
    parser.add_argument("--subject-alpha", type=float, default=10.0)
    parser.add_argument("--max-pairs", type=int, default=10000)
    return parser.parse_args()


if __name__ == "__main__":
    main()
