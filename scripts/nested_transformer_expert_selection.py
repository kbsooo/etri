from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss

from train_hourly_transformer_encoder import dataframe_to_markdown
from train_pruned_state_decoder import average_log_loss, drift_vs_reference, write_prediction
from train_s2_sleep_retrieval_encoder import EPS, TARGET_COLUMNS, make_subject_time_folds, normalize_keys
from train_transformer_moe_head import add_panel_position, load_sources, source_score_table, targetwise_best


def nested_target_selection(
    train: pd.DataFrame,
    names: list[str],
    source_oof: np.ndarray,
) -> tuple[np.ndarray, pd.DataFrame]:
    folds = make_subject_time_folds(train, 5)
    nested = np.zeros((len(train), len(TARGET_COLUMNS)))
    rows = []
    for fold_i, fold in enumerate(folds):
        for target_i, target in enumerate(TARGET_COLUMNS):
            losses = [
                float(log_loss(train.iloc[fold.train_idx][target].to_numpy(int), source_oof[source_i, fold.train_idx, target_i], labels=[0, 1]))
                for source_i in range(len(names))
            ]
            best_i = int(np.argmin(losses))
            nested[fold.val_idx, target_i] = source_oof[best_i, fold.val_idx, target_i]
            rows.append(
                {
                    "fold": fold_i,
                    "target": target,
                    "source": names[best_i],
                    "inner_loss": losses[best_i],
                    "outer_loss": float(log_loss(train.iloc[fold.val_idx][target].to_numpy(int), source_oof[best_i, fold.val_idx, target_i], labels=[0, 1])),
                }
            )
    return np.clip(nested, EPS, 1.0 - EPS), pd.DataFrame(rows)


def full_train_selection_submission(
    train: pd.DataFrame,
    sample: pd.DataFrame,
    names: list[str],
    source_oof: np.ndarray,
    source_sub: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, pd.DataFrame]:
    return targetwise_best(train, sample, names, source_oof, source_sub)


def run(args: argparse.Namespace) -> None:
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    train, sample = add_panel_position(train, sample)
    names, source_oof, source_sub = load_sources([Path(item) for item in args.input_dirs])

    source_scores = source_score_table(train, names, source_oof)
    full_oof, full_sub, full_selection = full_train_selection_submission(train, sample, names, source_oof, source_sub)
    nested_oof, nested_selection = nested_target_selection(train, names, source_oof)

    full_avg, full_per = average_log_loss(train[TARGET_COLUMNS], full_oof)
    nested_avg, nested_per = average_log_loss(train[TARGET_COLUMNS], nested_oof)
    drift = drift_vs_reference(sample, full_sub, Path(args.reference_submission) if args.reference_submission else None)

    source_scores.to_csv(output_dir / "source_scores.csv", index=False)
    full_selection.to_csv(output_dir / "full_train_target_selection.csv", index=False)
    nested_selection.to_csv(output_dir / "nested_target_selection.csv", index=False)
    write_prediction(output_dir / "oof_nested_transformer_expert_selection.csv", train, nested_oof, oof=True)
    write_prediction(output_dir / "submission_full_train_transformer_expert_selection.csv", sample, full_sub, oof=False)

    selection_counts = nested_selection.groupby(["target", "source"]).size().reset_index(name="count").sort_values(["target", "count"], ascending=[True, False])
    report = {
        "full_oof_avg_log_loss": full_avg,
        "full_oof_per_target": full_per,
        "nested_oof_avg_log_loss": nested_avg,
        "nested_oof_per_target": nested_per,
        "selection_optimism": nested_avg - full_avg,
        "drift_vs_reference_full_submission": drift,
        "n_sources": len(names),
        "selection_counts": selection_counts.to_dict(orient="records"),
    }
    (output_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    md = [
        "# Nested Transformer Expert Selection",
        "",
        "## Result",
        "",
        f"- Full-OOF targetwise expert selection: `{full_avg:.6f}`",
        f"- Nested targetwise expert selection: `{nested_avg:.6f}`",
        f"- Estimated selection optimism: `{nested_avg - full_avg:.6f}`",
        f"- Full-selection submission drift vs v83: `{drift.get('mean_abs_drift', float('nan')):.6f}`",
        "",
        "## Nested Selection Counts",
        "",
        dataframe_to_markdown(selection_counts),
        "",
        "## Full-Train Target Selection",
        "",
        dataframe_to_markdown(full_selection),
        "",
        "## Top Sources",
        "",
        dataframe_to_markdown(source_scores.head(12)),
        "",
        "This diagnostic isolates source-selection optimism. It does not retrain Transformer encoders inside folds; it only asks whether selecting the best expert per target on full OOF labels was overly optimistic.",
    ]
    (output_dir / "report.md").write_text("\n".join(md), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Estimate nested selection optimism across Transformer experts.")
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
    parser.add_argument("--output-dir", default="outputs/nested_transformer_expert_selection_v1")
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
