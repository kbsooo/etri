from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.metrics import log_loss
from sklearn.preprocessing import StandardScaler

from train_pruned_state_decoder import (
    EPS,
    KEY_COLUMNS,
    TARGET_COLUMNS,
    Preset,
    average_log_loss,
    build_presets,
    cap_columns_by_variance,
    columns_for_preset,
    drift_vs_reference,
    fit_hgb,
    fit_logreg,
    fit_prototype_label,
    fit_rank_pairwise,
    fit_residual_ridge,
    fit_state_features,
    safe_logit,
    sigmoid,
    subject_prior,
    write_prediction,
)
from train_s2_sleep_retrieval_encoder import dataframe_to_markdown, make_subject_time_folds, merge_feature_tables, normalize_keys


@dataclass(frozen=True)
class CandidateSpec:
    preset: str
    decoder: str
    weight: float | None = None

    @property
    def name(self) -> str:
        if self.weight is None:
            return f"{self.preset}__{self.decoder}"
        return f"{self.preset}__prior_logit_blend_{self.decoder}_w{int(self.weight * 100):02d}"


TARGET_CANDIDATES: dict[str, list[CandidateSpec]] = {
    "Q1": [
        CandidateSpec("only_missingness", "logreg", 0.10),
        CandidateSpec("no_raw", "hgb", 0.10),
        CandidateSpec("only_rhythm", "hgb", 0.20),
        CandidateSpec("no_temporal_delta", "hgb", 0.10),
        CandidateSpec("subject_prior", "subject_prior"),
    ],
    "Q2": [
        CandidateSpec("no_ratio", "state_mean", 0.35),
        CandidateSpec("only_rhythm", "hgb", 0.20),
        CandidateSpec("no_derivative", "hgb", 0.10),
        CandidateSpec("no_ratio", "residual_ridge", 0.03),
        CandidateSpec("subject_prior", "subject_prior"),
    ],
    "Q3": [
        CandidateSpec("no_sleep", "hgb", 0.35),
        CandidateSpec("only_rhythm", "state_mean", 0.10),
        CandidateSpec("no_rank", "hgb", 0.10),
        CandidateSpec("no_derivative", "hgb", 0.10),
        CandidateSpec("subject_prior", "subject_prior"),
    ],
    "S1": [
        CandidateSpec("only_rhythm", "rank_pairwise", 0.05),
        CandidateSpec("only_rhythm", "hgb", 0.20),
        CandidateSpec("only_cross_modal", "residual_ridge", 0.05),
        CandidateSpec("no_derivative", "hgb", 0.10),
        CandidateSpec("subject_prior", "subject_prior"),
    ],
    "S2": [
        CandidateSpec("no_missingness", "residual_ridge", 0.05),
        CandidateSpec("no_derivative", "hgb", 0.10),
        CandidateSpec("only_rhythm", "hgb", 0.20),
        CandidateSpec("only_deviation", "hgb", 0.10),
        CandidateSpec("subject_prior", "subject_prior"),
    ],
    "S3": [
        CandidateSpec("only_missingness", "rank_pairwise", 0.05),
        CandidateSpec("only_cross_modal", "hgb", 0.10),
        CandidateSpec("only_rhythm", "hgb", 0.10),
        CandidateSpec("no_ratio", "residual_ridge", 0.03),
        CandidateSpec("subject_prior", "subject_prior"),
    ],
    "S4": [
        CandidateSpec("no_rank", "hgb", 0.35),
        CandidateSpec("only_cross_modal", "hgb", 0.10),
        CandidateSpec("no_temporal_delta", "hgb", 0.20),
        CandidateSpec("no_derivative", "hgb", 0.20),
        CandidateSpec("subject_prior", "subject_prior"),
    ],
}


def preset_lookup() -> dict[str, Preset]:
    presets = {preset.name: preset for preset in build_presets()}
    presets["subject_prior"] = Preset("subject_prior", "full")
    return presets


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
    if decoder == "logreg":
        return fit_logreg(x_fit, y_fit, x_eval, x_sample, args.logreg_c)
    if decoder == "hgb":
        return fit_hgb(x_fit, y_fit, x_eval, x_sample)
    if decoder == "rank_pairwise":
        return fit_rank_pairwise(x_fit, y_fit, x_eval, x_sample, args.max_pairs)
    if decoder == "prototype":
        return fit_prototype_label(x_fit, y_fit, x_eval, x_sample, args.n_label_proto)
    if decoder == "residual_ridge":
        return fit_residual_ridge(x_fit, y_fit, base_fit, base_eval, base_sample, x_eval, x_sample)
    if decoder == "state_mean":
        preds = [
            fit_logreg(x_fit, y_fit, x_eval, x_sample, args.logreg_c),
            fit_hgb(x_fit, y_fit, x_eval, x_sample),
            fit_rank_pairwise(x_fit, y_fit, x_eval, x_sample, args.max_pairs),
            fit_prototype_label(x_fit, y_fit, x_eval, x_sample, args.n_label_proto),
            fit_residual_ridge(x_fit, y_fit, base_fit, base_eval, base_sample, x_eval, x_sample),
        ]
        return np.mean([p[0] for p in preds], axis=0), np.mean([p[1] for p in preds], axis=0)
    raise ValueError(decoder)


def predict_candidate(
    spec: CandidateSpec,
    target: str,
    train: pd.DataFrame,
    sample: pd.DataFrame,
    train_x: pd.DataFrame,
    sample_x: pd.DataFrame,
    preset_columns: dict[str, list[str]],
    fit_idx: np.ndarray,
    eval_idx: np.ndarray,
    args: argparse.Namespace,
) -> tuple[np.ndarray, np.ndarray]:
    target_i = TARGET_COLUMNS.index(target)
    base_fit_all = subject_prior(train.iloc[fit_idx], train.iloc[fit_idx], args.subject_alpha)
    base_eval_all = subject_prior(train.iloc[fit_idx], train.iloc[eval_idx], args.subject_alpha)
    base_sample_all = subject_prior(train.iloc[fit_idx], sample, args.subject_alpha)
    if spec.decoder == "subject_prior":
        return base_eval_all[:, target_i], base_sample_all[:, target_i]

    fit_state, eval_state, sample_state = fit_state_features(
        train_x,
        sample_x,
        train[KEY_COLUMNS],
        sample[KEY_COLUMNS],
        fit_idx,
        eval_idx,
        preset_columns[spec.preset],
        args.pca_dim,
        args.n_proto,
    )
    if eval_state is None:
        raise RuntimeError("eval_state missing")
    imputer = SimpleImputer(strategy="median", keep_empty_features=True)
    scaler = StandardScaler()
    fit_s = scaler.fit_transform(imputer.fit_transform(fit_state))
    eval_s = scaler.transform(imputer.transform(eval_state))
    sample_s = scaler.transform(imputer.transform(sample_state))
    y_fit = train.iloc[fit_idx][target].to_numpy(int)
    eval_pred, sample_pred = source_prediction(
        spec.decoder,
        fit_s,
        y_fit,
        eval_s,
        sample_s,
        base_fit_all[:, target_i],
        base_eval_all[:, target_i],
        base_sample_all[:, target_i],
        args,
    )
    if spec.weight is not None:
        weight = spec.weight
        eval_pred = sigmoid((1.0 - weight) * safe_logit(base_eval_all[:, target_i]) + weight * safe_logit(eval_pred))
        sample_pred = sigmoid((1.0 - weight) * safe_logit(base_sample_all[:, target_i]) + weight * safe_logit(sample_pred))
    return np.clip(eval_pred, EPS, 1.0 - EPS), np.clip(sample_pred, EPS, 1.0 - EPS)


def nested_select_for_outer(
    target: str,
    outer_train_idx: np.ndarray,
    train: pd.DataFrame,
    sample: pd.DataFrame,
    train_x: pd.DataFrame,
    sample_x: pd.DataFrame,
    preset_columns: dict[str, list[str]],
    args: argparse.Namespace,
) -> tuple[CandidateSpec, list[dict]]:
    outer_train = train.iloc[outer_train_idx].reset_index(drop=True)
    inner_folds = make_subject_time_folds(outer_train, args.inner_folds)
    rows = []
    for spec in TARGET_CANDIDATES[target]:
        inner_oof = np.zeros(len(outer_train_idx), dtype=float)
        for fold in inner_folds:
            fit_global = outer_train_idx[fold.train_idx]
            val_global = outer_train_idx[fold.val_idx]
            pred, _ = predict_candidate(spec, target, train, sample, train_x, sample_x, preset_columns, fit_global, val_global, args)
            inner_oof[fold.val_idx] = pred
        loss = float(log_loss(outer_train[target].to_numpy(int), np.clip(inner_oof, EPS, 1.0 - EPS), labels=[0, 1]))
        rows.append({"target": target, "candidate": spec.name, "inner_log_loss": loss})
    best_row = min(rows, key=lambda row: row["inner_log_loss"])
    best_spec = next(spec for spec in TARGET_CANDIDATES[target] if spec.name == best_row["candidate"])
    return best_spec, rows


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    train_x, sample_x = merge_feature_tables(train, sample)
    all_cols = train_x.columns.tolist()
    presets = preset_lookup()
    used_presets = sorted({spec.preset for specs in TARGET_CANDIDATES.values() for spec in specs if spec.preset != "subject_prior"})
    preset_columns = {
        name: cap_columns_by_variance(train_x, sample_x, columns_for_preset(all_cols, presets[name]), args.max_features)
        for name in used_presets
    }

    outer_folds = make_subject_time_folds(train, args.outer_folds)
    oof = np.zeros((len(train), len(TARGET_COLUMNS)), dtype=float)
    sample_folds = []
    selection_rows = []
    inner_rows = []
    for outer_i, outer in enumerate(outer_folds):
        fold_sample = np.zeros((len(sample), len(TARGET_COLUMNS)), dtype=float)
        for target_i, target in enumerate(TARGET_COLUMNS):
            best_spec, rows = nested_select_for_outer(
                target,
                outer.train_idx,
                train,
                sample,
                train_x,
                sample_x,
                preset_columns,
                args,
            )
            inner_rows.extend({"outer_fold": outer_i, **row} for row in rows)
            val_pred, sample_pred = predict_candidate(
                best_spec,
                target,
                train,
                sample,
                train_x,
                sample_x,
                preset_columns,
                outer.train_idx,
                outer.val_idx,
                args,
            )
            oof[outer.val_idx, target_i] = val_pred
            fold_sample[:, target_i] = sample_pred
            selection_rows.append({"outer_fold": outer_i, "target": target, "selected": best_spec.name})
        sample_folds.append(fold_sample)

    sample_pred = np.mean(np.stack(sample_folds, axis=0), axis=0)
    avg, per_target = average_log_loss(train[TARGET_COLUMNS].astype(int), oof)
    selection = pd.DataFrame(selection_rows)
    inner = pd.DataFrame(inner_rows)
    target_counts = selection.groupby(["target", "selected"]).size().reset_index(name="outer_count").sort_values(["target", "outer_count"], ascending=[True, False])
    write_prediction(output_dir / "oof_nested_pruned_state_targetwise.csv", train, oof, oof=True)
    write_prediction(output_dir / "submission_nested_pruned_state_targetwise.csv", sample, sample_pred, oof=False)
    selection.to_csv(output_dir / "outer_target_selection.csv", index=False)
    target_counts.to_csv(output_dir / "selection_counts.csv", index=False)
    inner.to_csv(output_dir / "inner_candidate_scores.csv", index=False)
    diagnostics = {
        "avg_log_loss": avg,
        "per_target": per_target,
        "drift_vs_reference": drift_vs_reference(sample, sample_pred, Path(args.reference_submission) if args.reference_submission else None),
        "args": vars(args),
        "preset_feature_counts": {name: len(cols) for name, cols in preset_columns.items()},
    }
    (output_dir / "report.json").write_text(json.dumps(diagnostics, indent=2), encoding="utf-8")
    lines = [
        "# Nested Pruned State Decoder",
        "",
        "Target-specific feature-family candidates are selected inside each outer fold, then scored on held-out rows.",
        "",
        f"- Nested target-wise OOF avg: `{avg:.6f}`",
        f"- Drift vs v83 diagnostic reference: `{diagnostics['drift_vs_reference'].get('mean_abs_drift', float('nan')):.6f}`",
        "",
        "## Per-target OOF",
        "",
        dataframe_to_markdown(pd.DataFrame([{"avg_log_loss": avg, **per_target}])),
        "",
        "## Selection Counts",
        "",
        dataframe_to_markdown(target_counts),
        "",
        "## Inner Candidate Scores",
        "",
        dataframe_to_markdown(inner.sort_values(["target", "outer_fold", "inner_log_loss"]).head(80)),
    ]
    (output_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"nested_targetwise avg={avg:.6f}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Nested target-aware pruned state decoder.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--output-dir", default="outputs/nested_pruned_state_decoder_v1")
    parser.add_argument("--reference-submission", default="outputs/v83_repaired_v80/submission_v83_gq015_gs010.csv")
    parser.add_argument("--outer-folds", type=int, default=5)
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
