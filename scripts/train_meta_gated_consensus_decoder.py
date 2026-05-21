from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import log_loss
from sklearn.preprocessing import StandardScaler

from train_consensus_pruned_state_decoder import FIXED_MAPS
from train_nested_pruned_state_decoder import predict_candidate, preset_lookup
from train_pruned_state_decoder import (
    EPS,
    KEY_COLUMNS,
    TARGET_COLUMNS,
    average_log_loss,
    cap_columns_by_variance,
    columns_for_preset,
    drift_vs_reference,
    safe_logit,
    sigmoid,
    subject_prior,
    write_prediction,
)
from train_s2_sleep_retrieval_encoder import dataframe_to_markdown, make_subject_time_folds, merge_feature_tables, normalize_keys


SHRINK_WEIGHTS = (0.25, 0.50, 0.75, 1.00)


def panel_position(keys: pd.DataFrame) -> np.ndarray:
    ordered = keys.reset_index(drop=True).copy()
    ordered["_row"] = np.arange(len(ordered))
    return ordered.groupby("subject_id")["_row"].rank(method="first", pct=True).to_numpy(float)


def meta_features(base: np.ndarray, source: np.ndarray, pos: np.ndarray) -> np.ndarray:
    base_logit = safe_logit(base)
    source_logit = safe_logit(source)
    delta = source_logit - base_logit
    return np.column_stack(
        [
            base,
            source,
            base_logit,
            source_logit,
            delta,
            np.abs(delta),
            np.sign(delta),
            pos,
            pos * pos,
            np.clip(pos - 0.5, -0.5, 0.5),
        ]
    )


def shrink_prediction(base: np.ndarray, source: np.ndarray, weight: float) -> np.ndarray:
    return np.clip(sigmoid(safe_logit(base) + weight * (safe_logit(source) - safe_logit(base))), EPS, 1.0 - EPS)


def fit_meta_logreg(x_fit: np.ndarray, y_fit: np.ndarray, x_eval: np.ndarray, x_sample: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    if len(np.unique(y_fit)) < 2:
        value = float(y_fit[0])
        return np.full(len(x_eval), value), np.full(len(x_sample), value)
    scaler = StandardScaler()
    x_fit_s = scaler.fit_transform(x_fit)
    x_eval_s = scaler.transform(x_eval)
    x_sample_s = scaler.transform(x_sample)
    model = LogisticRegression(C=0.08, solver="lbfgs", max_iter=4000, random_state=2026)
    model.fit(x_fit_s, y_fit)
    return model.predict_proba(x_eval_s)[:, 1], model.predict_proba(x_sample_s)[:, 1]


def fit_meta_residual_ridge(
    x_fit: np.ndarray,
    y_fit: np.ndarray,
    base_fit: np.ndarray,
    base_eval: np.ndarray,
    base_sample: np.ndarray,
    x_eval: np.ndarray,
    x_sample: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    scaler = StandardScaler()
    x_fit_s = scaler.fit_transform(x_fit)
    x_eval_s = scaler.transform(x_eval)
    x_sample_s = scaler.transform(x_sample)
    residual = safe_logit((y_fit * 0.98) + 0.01) - safe_logit(base_fit)
    model = Ridge(alpha=80.0)
    model.fit(x_fit_s, residual)
    eval_pred = sigmoid(safe_logit(base_eval) + model.predict(x_eval_s))
    sample_pred = sigmoid(safe_logit(base_sample) + model.predict(x_sample_s))
    return np.clip(eval_pred, EPS, 1.0 - EPS), np.clip(sample_pred, EPS, 1.0 - EPS)


def inner_source_oof(
    spec,
    target: str,
    train: pd.DataFrame,
    sample: pd.DataFrame,
    train_x: pd.DataFrame,
    sample_x: pd.DataFrame,
    preset_columns: dict[str, list[str]],
    outer_train_idx: np.ndarray,
    args: argparse.Namespace,
) -> tuple[np.ndarray, np.ndarray]:
    outer_train = train.iloc[outer_train_idx].reset_index(drop=True)
    inner_folds = make_subject_time_folds(outer_train, args.inner_folds)
    oof_source = np.zeros(len(outer_train_idx), dtype=float)
    oof_base = np.zeros(len(outer_train_idx), dtype=float)
    target_i = TARGET_COLUMNS.index(target)
    for fold in inner_folds:
        fit_global = outer_train_idx[fold.train_idx]
        val_global = outer_train_idx[fold.val_idx]
        val_pred, _ = predict_candidate(
            spec,
            target,
            train,
            sample,
            train_x,
            sample_x,
            preset_columns,
            fit_global,
            val_global,
            args,
        )
        base_val = subject_prior(train.iloc[fit_global], train.iloc[val_global], args.subject_alpha)[:, target_i]
        oof_source[fold.val_idx] = val_pred
        oof_base[fold.val_idx] = base_val
    return np.clip(oof_base, EPS, 1.0 - EPS), np.clip(oof_source, EPS, 1.0 - EPS)


def run_variant(
    fixed_map_name: str,
    train: pd.DataFrame,
    sample: pd.DataFrame,
    train_x: pd.DataFrame,
    sample_x: pd.DataFrame,
    preset_columns: dict[str, list[str]],
    args: argparse.Namespace,
) -> tuple[dict[str, np.ndarray], dict[str, list[dict]]]:
    folds = make_subject_time_folds(train, args.folds)
    variants = [f"shrink_w{int(weight * 100):02d}" for weight in SHRINK_WEIGHTS] + ["meta_logreg", "meta_residual_ridge"]
    oof = {name: np.zeros((len(train), len(TARGET_COLUMNS)), dtype=float) for name in variants}
    sample_folds = {name: [] for name in variants}
    train_pos = panel_position(train[KEY_COLUMNS])
    sample_pos = panel_position(sample[KEY_COLUMNS])
    diagnostic_rows: list[dict] = []
    fixed_map = FIXED_MAPS[fixed_map_name]

    for fold_i, fold in enumerate(folds):
        fold_sample = {name: np.zeros((len(sample), len(TARGET_COLUMNS)), dtype=float) for name in variants}
        for target_i, target in enumerate(TARGET_COLUMNS):
            spec = fixed_map[target]
            val_source, sample_source = predict_candidate(
                spec,
                target,
                train,
                sample,
                train_x,
                sample_x,
                preset_columns,
                fold.train_idx,
                fold.val_idx,
                args,
            )
            base_val = subject_prior(train.iloc[fold.train_idx], train.iloc[fold.val_idx], args.subject_alpha)[:, target_i]
            base_sample = subject_prior(train.iloc[fold.train_idx], sample, args.subject_alpha)[:, target_i]
            for weight in SHRINK_WEIGHTS:
                name = f"shrink_w{int(weight * 100):02d}"
                oof[name][fold.val_idx, target_i] = shrink_prediction(base_val, val_source, weight)
                fold_sample[name][:, target_i] = shrink_prediction(base_sample, sample_source, weight)

            inner_base, inner_source = inner_source_oof(
                spec,
                target,
                train,
                sample,
                train_x,
                sample_x,
                preset_columns,
                fold.train_idx,
                args,
            )
            inner_y = train.iloc[fold.train_idx][target].to_numpy(int)
            x_inner = meta_features(inner_base, inner_source, train_pos[fold.train_idx])
            x_val = meta_features(base_val, val_source, train_pos[fold.val_idx])
            x_sample = meta_features(base_sample, sample_source, sample_pos)
            logreg_val, logreg_sample = fit_meta_logreg(x_inner, inner_y, x_val, x_sample)
            ridge_val, ridge_sample = fit_meta_residual_ridge(
                x_inner,
                inner_y,
                inner_base,
                base_val,
                base_sample,
                x_val,
                x_sample,
            )
            oof["meta_logreg"][fold.val_idx, target_i] = np.clip(logreg_val, EPS, 1.0 - EPS)
            oof["meta_residual_ridge"][fold.val_idx, target_i] = np.clip(ridge_val, EPS, 1.0 - EPS)
            fold_sample["meta_logreg"][:, target_i] = np.clip(logreg_sample, EPS, 1.0 - EPS)
            fold_sample["meta_residual_ridge"][:, target_i] = np.clip(ridge_sample, EPS, 1.0 - EPS)
            diagnostic_rows.append(
                {
                    "fold": fold_i,
                    "target": target,
                    "source": spec.name,
                    "val_source_minus_base_abs_mean": float(np.mean(np.abs(safe_logit(val_source) - safe_logit(base_val)))),
                    "sample_source_minus_base_abs_mean": float(np.mean(np.abs(safe_logit(sample_source) - safe_logit(base_sample)))),
                }
            )
        for name in variants:
            sample_folds[name].append(fold_sample[name])

    sample_pred = {name: np.mean(np.stack(parts, axis=0), axis=0) for name, parts in sample_folds.items()}
    output = {f"oof_{name}": pred for name, pred in oof.items()}
    output.update({f"sample_{name}": pred for name, pred in sample_pred.items()})
    return output, {"fold_diagnostics": diagnostic_rows}


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    train_x, sample_x = merge_feature_tables(train, sample)
    all_cols = train_x.columns.tolist()
    presets = preset_lookup()
    fixed_map = FIXED_MAPS[args.fixed_map]
    used_presets = sorted({spec.preset for spec in fixed_map.values() if spec.preset != "subject_prior"})
    preset_columns = {
        name: cap_columns_by_variance(train_x, sample_x, columns_for_preset(all_cols, presets[name]), args.max_features)
        for name in used_presets
    }

    predictions, diagnostics = run_variant(args.fixed_map, train, sample, train_x, sample_x, preset_columns, args)
    y_df = train[TARGET_COLUMNS].astype(int)
    score_rows = []
    for key, pred in predictions.items():
        if not key.startswith("oof_"):
            continue
        variant = key.removeprefix("oof_")
        sample_pred = predictions[f"sample_{variant}"]
        avg, per_target = average_log_loss(y_df, pred)
        drift = drift_vs_reference(sample, sample_pred, Path(args.reference_submission) if args.reference_submission else None)
        base_sample = np.zeros_like(sample_pred)
        for fold in make_subject_time_folds(train, args.folds):
            base_sample += subject_prior(train.iloc[fold.train_idx], sample, args.subject_alpha)
        base_sample /= args.folds
        source_delta = sample_pred - base_sample
        score_rows.append(
            {
                "variant": variant,
                "avg_log_loss": avg,
                **per_target,
                "drift_vs_reference": drift.get("mean_abs_drift"),
                "corr_vs_reference": drift.get("corr"),
                "sample_abs_delta_vs_subject_prior": float(np.mean(np.abs(source_delta))),
                "sample_mean_delta_vs_subject_prior": float(np.mean(source_delta)),
            }
        )
        write_prediction(output_dir / f"oof_{variant}.csv", train, pred, oof=True)
        write_prediction(output_dir / f"submission_{variant}.csv", sample, sample_pred, oof=False)

    score_df = pd.DataFrame(score_rows).sort_values("avg_log_loss")
    score_df.to_csv(output_dir / "meta_gated_scores.csv", index=False)
    pd.DataFrame(diagnostics["fold_diagnostics"]).to_csv(output_dir / "fold_diagnostics.csv", index=False)
    report = {
        "scores": score_df.to_dict(orient="records"),
        "fixed_map": args.fixed_map,
        "fixed_sources": {target: spec.name for target, spec in fixed_map.items()},
        "preset_feature_counts": {name: len(cols) for name, cols in preset_columns.items()},
        "args": vars(args),
    }
    (output_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = [
        "# Meta-Gated Consensus Decoder",
        "",
        "This experiment keeps the fixed consensus state sources but learns a small fold-safe meta gate between subject prior and state source.",
        "",
        dataframe_to_markdown(score_df),
    ]
    (output_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(score_df.to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fold-safe meta gates over fixed pruned-state consensus decoder sources.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--output-dir", default="outputs/meta_gated_consensus_decoder_v1")
    parser.add_argument("--reference-submission", default="outputs/v83_repaired_v80/submission_v83_gq015_gs010.csv")
    parser.add_argument("--fixed-map", default="consensus_signal", choices=sorted(FIXED_MAPS))
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--inner-folds", type=int, default=4)
    parser.add_argument("--max-features", type=int, default=520)
    parser.add_argument("--pca-dim", type=int, default=28)
    parser.add_argument("--n-proto", type=int, default=10)
    parser.add_argument("--n-label-proto", type=int, default=12)
    parser.add_argument("--logreg-c", type=float, default=0.03)
    parser.add_argument("--subject-alpha", type=float, default=10.0)
    parser.add_argument("--max-pairs", type=int, default=10000)
    return parser.parse_args()


if __name__ == "__main__":
    main()
