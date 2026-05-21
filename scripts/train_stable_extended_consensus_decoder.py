from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from train_extended_family_pruning_decoder import RECIPES, columns_for_recipe
from train_nested_pruned_state_decoder import CandidateSpec, predict_candidate, preset_lookup
from train_pruned_state_decoder import (
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


FIXED_MAPS: dict[str, dict[str, CandidateSpec]] = {
    "stable_nested_vote": {
        "Q1": CandidateSpec("only_rhythm", "hgb", 0.20),
        "Q2": CandidateSpec("only_rhythm", "hgb", 0.20),
        "Q3": CandidateSpec("drop_sleep_late", "hgb", 0.35),
        "S1": CandidateSpec("subject_prior", "subject_prior"),
        "S2": CandidateSpec("no_missingness", "residual_ridge", 0.05),
        "S3": CandidateSpec("subject_prior", "subject_prior"),
        "S4": CandidateSpec("no_temporal_delta", "hgb", 0.20),
    },
    "stable_prior_guarded": {
        "Q1": CandidateSpec("only_rhythm", "hgb", 0.20),
        "Q2": CandidateSpec("no_ratio", "state_mean", 0.35),
        "Q3": CandidateSpec("drop_sleep_late", "hgb", 0.35),
        "S1": CandidateSpec("subject_prior", "subject_prior"),
        "S2": CandidateSpec("subject_prior", "subject_prior"),
        "S3": CandidateSpec("subject_prior", "subject_prior"),
        "S4": CandidateSpec("no_temporal_delta", "hgb", 0.20),
    },
    "stable_signal_s4_temporal": {
        "Q1": CandidateSpec("only_rhythm", "hgb", 0.20),
        "Q2": CandidateSpec("no_ratio", "state_mean", 0.35),
        "Q3": CandidateSpec("no_sleep", "hgb", 0.35),
        "S1": CandidateSpec("only_rhythm", "hgb", 0.20),
        "S2": CandidateSpec("no_missingness", "residual_ridge", 0.05),
        "S3": CandidateSpec("only_missingness", "rank_pairwise", 0.05),
        "S4": CandidateSpec("no_temporal_delta", "hgb", 0.20),
    },
    "extended_full_oof_winners": {
        "Q1": CandidateSpec("drop_ratio_temporal_delta", "hgb", 0.35),
        "Q2": CandidateSpec("drop_raw_ratio", "hgb", 0.35),
        "Q3": CandidateSpec("drop_sleep_late", "hgb", 0.35),
        "S1": CandidateSpec("drop_raw_rank", "residual_ridge", 0.10),
        "S2": CandidateSpec("only_rhythm_deviation_cross_modal", "residual_ridge", 0.05),
        "S3": CandidateSpec("drop_ratio_temporal_delta", "hgb", 0.20),
        "S4": CandidateSpec("only_missingness_cross_modal", "rank_pairwise", 0.10),
    },
    "q1_s4_only": {
        "Q1": CandidateSpec("only_rhythm", "hgb", 0.20),
        "Q2": CandidateSpec("subject_prior", "subject_prior"),
        "Q3": CandidateSpec("subject_prior", "subject_prior"),
        "S1": CandidateSpec("subject_prior", "subject_prior"),
        "S2": CandidateSpec("subject_prior", "subject_prior"),
        "S3": CandidateSpec("subject_prior", "subject_prior"),
        "S4": CandidateSpec("no_temporal_delta", "hgb", 0.20),
    },
}


def build_preset_columns(
    train_x: pd.DataFrame,
    sample_x: pd.DataFrame,
    args: argparse.Namespace,
) -> dict[str, list[str]]:
    all_cols = train_x.columns.tolist()
    base_presets: dict[str, Preset] = preset_lookup()
    recipe_lookup = {recipe.name: recipe for recipe in RECIPES}
    used = sorted({spec.preset for fixed_map in FIXED_MAPS.values() for spec in fixed_map.values() if spec.preset != "subject_prior"})
    columns_by_name: dict[str, list[str]] = {}
    for name in used:
        if name in recipe_lookup:
            columns = columns_for_recipe(all_cols, recipe_lookup[name])
        else:
            columns = columns_for_preset(all_cols, base_presets[name])
        columns_by_name[name] = cap_columns_by_variance(train_x, sample_x, columns, args.max_features)
    return columns_by_name


def run_fixed_map(
    name: str,
    fixed_map: dict[str, CandidateSpec],
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
    source_rows = []
    for fold_i, fold in enumerate(folds):
        fold_sample = np.zeros((len(sample), len(TARGET_COLUMNS)), dtype=float)
        for target_i, target in enumerate(TARGET_COLUMNS):
            spec = fixed_map[target]
            val_pred, sample_pred = predict_candidate(
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
            oof[fold.val_idx, target_i] = val_pred
            fold_sample[:, target_i] = sample_pred
            source_rows.append({"variant": name, "fold": fold_i, "target": target, "source": spec.name})
        sample_folds.append(fold_sample)
    return oof, np.mean(np.stack(sample_folds, axis=0), axis=0), source_rows


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    train_x, sample_x = merge_feature_tables(train, sample)
    preset_columns = build_preset_columns(train_x, sample_x, args)

    reports = []
    source_rows = []
    y_df = train[TARGET_COLUMNS].astype(int)
    for name, fixed_map in FIXED_MAPS.items():
        oof, submission, rows = run_fixed_map(name, fixed_map, train, sample, train_x, sample_x, preset_columns, args)
        avg, per_target = average_log_loss(y_df, oof)
        drift = drift_vs_reference(sample, submission, Path(args.reference_submission) if args.reference_submission else None)
        reports.append(
            {
                "variant": name,
                "avg_log_loss": avg,
                **per_target,
                "drift_vs_reference": drift.get("mean_abs_drift"),
                "corr_vs_reference": drift.get("corr"),
            }
        )
        source_rows.extend(rows)
        write_prediction(output_dir / f"oof_{name}.csv", train, oof, oof=True)
        write_prediction(output_dir / f"submission_{name}.csv", sample, submission, oof=False)

    report_df = pd.DataFrame(reports).sort_values("avg_log_loss")
    report_df.to_csv(output_dir / "stable_consensus_scores.csv", index=False)
    pd.DataFrame(source_rows).to_csv(output_dir / "fixed_sources.csv", index=False)
    report = {
        "scores": report_df.to_dict(orient="records"),
        "fixed_maps": {name: {target: spec.name for target, spec in fixed_map.items()} for name, fixed_map in FIXED_MAPS.items()},
        "preset_feature_counts": {name: len(cols) for name, cols in preset_columns.items()},
        "args": vars(args),
    }
    (output_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = [
        "# Stable Extended Consensus Decoder",
        "",
        "Fixed maps that combine stable nested selection counts with extended feature-family candidates. No target selection is performed inside this run.",
        "",
        dataframe_to_markdown(report_df),
    ]
    (output_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(report_df.to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Stable fixed maps from nested extended-family decoder findings.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--output-dir", default="outputs/stable_extended_consensus_decoder_v1")
    parser.add_argument("--reference-submission", default="outputs/v83_repaired_v80/submission_v83_gq015_gs010.csv")
    parser.add_argument("--folds", type=int, default=5)
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
