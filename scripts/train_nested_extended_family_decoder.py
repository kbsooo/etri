from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss

from train_extended_family_pruning_decoder import RECIPES, columns_for_recipe
from train_nested_pruned_state_decoder import CandidateSpec, predict_candidate, preset_lookup
from train_pruned_state_decoder import (
    EPS,
    KEY_COLUMNS,
    TARGET_COLUMNS,
    Preset,
    average_log_loss,
    cap_columns_by_variance,
    columns_for_preset,
    drift_vs_reference,
    write_prediction,
)
from train_s2_sleep_retrieval_encoder import dataframe_to_markdown, make_subject_time_folds, merge_feature_tables, normalize_keys


TARGET_CANDIDATES: dict[str, list[CandidateSpec]] = {
    "Q1": [
        CandidateSpec("drop_ratio_temporal_delta", "hgb", 0.35),
        CandidateSpec("drop_ratio_temporal_delta", "hgb", 0.20),
        CandidateSpec("only_rhythm", "hgb", 0.20),
        CandidateSpec("subject_prior", "subject_prior"),
    ],
    "Q2": [
        CandidateSpec("drop_raw_ratio", "hgb", 0.35),
        CandidateSpec("no_ratio", "state_mean", 0.35),
        CandidateSpec("only_rhythm", "hgb", 0.20),
        CandidateSpec("subject_prior", "subject_prior"),
    ],
    "Q3": [
        CandidateSpec("drop_sleep_late", "hgb", 0.35),
        CandidateSpec("no_sleep", "hgb", 0.35),
        CandidateSpec("only_rhythm", "state_mean", 0.10),
        CandidateSpec("subject_prior", "subject_prior"),
    ],
    "S1": [
        CandidateSpec("drop_raw_rank", "residual_ridge", 0.10),
        CandidateSpec("only_rhythm", "hgb", 0.20),
        CandidateSpec("only_deviation_cross_modal", "residual_ridge", 0.03),
        CandidateSpec("subject_prior", "subject_prior"),
    ],
    "S2": [
        CandidateSpec("only_rhythm_deviation_cross_modal", "residual_ridge", 0.05),
        CandidateSpec("no_missingness", "residual_ridge", 0.05),
        CandidateSpec("only_rhythm", "hgb", 0.20),
        CandidateSpec("subject_prior", "subject_prior"),
    ],
    "S3": [
        CandidateSpec("drop_ratio_temporal_delta", "hgb", 0.20),
        CandidateSpec("only_missingness", "rank_pairwise", 0.05),
        CandidateSpec("only_cross_modal", "hgb", 0.10),
        CandidateSpec("subject_prior", "subject_prior"),
    ],
    "S4": [
        CandidateSpec("only_missingness_cross_modal", "rank_pairwise", 0.10),
        CandidateSpec("only_cross_modal", "hgb", 0.10),
        CandidateSpec("no_temporal_delta", "hgb", 0.20),
        CandidateSpec("subject_prior", "subject_prior"),
    ],
}


def build_preset_columns(
    train_x: pd.DataFrame,
    sample_x: pd.DataFrame,
    args: argparse.Namespace,
) -> dict[str, list[str]]:
    all_cols = train_x.columns.tolist()
    base_presets: dict[str, Preset] = preset_lookup()
    recipe_lookup = {recipe.name: recipe for recipe in RECIPES}
    used = sorted({spec.preset for specs in TARGET_CANDIDATES.values() for spec in specs if spec.preset != "subject_prior"})
    out: dict[str, list[str]] = {}
    for name in used:
        if name in recipe_lookup:
            columns = columns_for_recipe(all_cols, recipe_lookup[name])
        else:
            columns = columns_for_preset(all_cols, base_presets[name])
        out[name] = cap_columns_by_variance(train_x, sample_x, columns, args.max_features)
    return out


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
    preset_columns = build_preset_columns(train_x, sample_x, args)
    folds = make_subject_time_folds(train, args.folds)
    oof = np.zeros((len(train), len(TARGET_COLUMNS)), dtype=float)
    sample_folds = []
    selection_rows = []
    inner_rows = []
    for fold_i, fold in enumerate(folds):
        fold_sample = np.zeros((len(sample), len(TARGET_COLUMNS)), dtype=float)
        for target_i, target in enumerate(TARGET_COLUMNS):
            best_spec, rows = nested_select_for_outer(target, fold.train_idx, train, sample, train_x, sample_x, preset_columns, args)
            for row in rows:
                row["outer_fold"] = fold_i
                inner_rows.append(row)
            val_pred, sample_pred = predict_candidate(
                best_spec,
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
            oof[fold.val_idx, target_i] = val_pred
            fold_sample[:, target_i] = sample_pred
            selection_rows.append({"outer_fold": fold_i, "target": target, "selected": best_spec.name})
        sample_folds.append(fold_sample)

    sample_pred = np.mean(np.stack(sample_folds, axis=0), axis=0)
    avg, per_target = average_log_loss(train[TARGET_COLUMNS].astype(int), oof)
    drift = drift_vs_reference(sample, sample_pred, Path(args.reference_submission) if args.reference_submission else None)
    selection_df = pd.DataFrame(selection_rows)
    counts = selection_df.groupby(["target", "selected"]).size().reset_index(name="count").sort_values(["target", "count"], ascending=[True, False])
    pd.DataFrame(inner_rows).to_csv(output_dir / "inner_candidate_scores.csv", index=False)
    selection_df.to_csv(output_dir / "outer_selections.csv", index=False)
    counts.to_csv(output_dir / "selection_counts.csv", index=False)
    write_prediction(output_dir / "oof_nested_extended_family_decoder.csv", train, oof, oof=True)
    write_prediction(output_dir / "submission_nested_extended_family_decoder.csv", sample, sample_pred, oof=False)
    report = {
        "avg_log_loss": avg,
        "per_target": per_target,
        "drift_vs_reference": drift,
        "selection_counts": counts.to_dict(orient="records"),
        "preset_feature_counts": {name: len(cols) for name, cols in preset_columns.items()},
        "args": vars(args),
    }
    (output_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    summary_df = pd.DataFrame([{"avg_log_loss": avg, **per_target, "drift_vs_reference": drift.get("mean_abs_drift"), "corr_vs_reference": drift.get("corr")}])
    lines = [
        "# Nested Extended Family Decoder",
        "",
        "Nested validation of extended family-pruning target candidates. Inner folds select source; outer folds score it.",
        "",
        "## Score",
        "",
        dataframe_to_markdown(summary_df),
        "",
        "## Selection Counts",
        "",
        dataframe_to_markdown(counts),
    ]
    (output_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(summary_df.to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Nested selection for extended feature-family pruning candidates.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--output-dir", default="outputs/nested_extended_family_decoder_v1")
    parser.add_argument("--reference-submission", default="outputs/v83_repaired_v80/submission_v83_gq015_gs010.csv")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--inner-folds", type=int, default=3)
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
