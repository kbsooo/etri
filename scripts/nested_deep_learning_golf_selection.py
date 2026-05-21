from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from train_hourly_transformer_encoder import dataframe_to_markdown
from train_s2_sleep_retrieval_encoder import KEY_COLUMNS, TARGET_COLUMNS, make_subject_time_folds, normalize_keys


def weighted_mean(values: pd.Series, weights: pd.Series) -> float:
    return float(np.average(values.to_numpy(float), weights=weights.to_numpy(float)))


def add_fold_weights(train: pd.DataFrame, fold_losses: pd.DataFrame, n_folds: int) -> pd.DataFrame:
    folds = make_subject_time_folds(train, n_folds)
    fold_sizes = {i + 1: len(fold.val_idx) for i, fold in enumerate(folds)}
    out = fold_losses.copy()
    out["fold_size"] = out["fold"].map(fold_sizes).astype(float)
    if out["fold_size"].isna().any():
        raise ValueError("Some fold ids in fold losses do not match generated folds.")
    return out


def full_targetwise_from_fold_losses(fold_losses: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, float], float]:
    rows = []
    per_target = {}
    for target in TARGET_COLUMNS:
        part = fold_losses[fold_losses["target"] == target]
        source_scores = (
            part.groupby("source", sort=False)
            .apply(lambda g: weighted_mean(g["loss"], g["fold_size"]), include_groups=False)
            .reset_index(name="loss")
            .sort_values("loss")
        )
        best = source_scores.iloc[0]
        rows.append({"target": target, "source": best["source"], "loss": float(best["loss"])})
        per_target[target] = float(best["loss"])
    return pd.DataFrame(rows), per_target, float(np.mean(list(per_target.values())))


def nested_targetwise_from_fold_losses(fold_losses: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, float], float]:
    nested_rows = []
    per_fold_target = []
    for outer_fold in sorted(fold_losses["fold"].unique()):
        for target in TARGET_COLUMNS:
            inner = fold_losses[(fold_losses["fold"] != outer_fold) & (fold_losses["target"] == target)]
            outer = fold_losses[(fold_losses["fold"] == outer_fold) & (fold_losses["target"] == target)]
            inner_scores = (
                inner.groupby("source", sort=False)
                .apply(lambda g: weighted_mean(g["loss"], g["fold_size"]), include_groups=False)
                .reset_index(name="inner_loss")
                .sort_values("inner_loss")
            )
            best_source = str(inner_scores.iloc[0]["source"])
            outer_match = outer[outer["source"] == best_source]
            if len(outer_match) != 1:
                raise ValueError(f"Missing outer loss for fold={outer_fold} target={target} source={best_source}")
            row = outer_match.iloc[0]
            nested_rows.append(
                {
                    "fold": int(outer_fold),
                    "target": target,
                    "source": best_source,
                    "inner_loss": float(inner_scores.iloc[0]["inner_loss"]),
                    "outer_loss": float(row["loss"]),
                    "fold_size": float(row["fold_size"]),
                }
            )
    nested = pd.DataFrame(nested_rows)
    per_target = {}
    for target in TARGET_COLUMNS:
        part = nested[nested["target"] == target]
        per_target[target] = weighted_mean(part["outer_loss"], part["fold_size"])
        per_fold_target.append({"target": target, "nested_loss": per_target[target]})
    return nested, pd.DataFrame(per_fold_target), per_target, float(np.mean(list(per_target.values())))


def source_score_table(fold_losses: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for source, group in fold_losses.groupby("source", sort=False):
        target_losses = {}
        for target in TARGET_COLUMNS:
            part = group[group["target"] == target]
            target_losses[target] = weighted_mean(part["loss"], part["fold_size"])
        rows.append({"source": source, "avg_log_loss": float(np.mean(list(target_losses.values()))), **target_losses})
    return pd.DataFrame(rows).sort_values("avg_log_loss").reset_index(drop=True)


def run(args: argparse.Namespace) -> None:
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    train = normalize_keys(pd.read_csv(args.train_path))
    fold_losses = pd.read_csv(input_dir / "golf_fold_losses.csv")
    fold_losses = add_fold_weights(train, fold_losses, args.n_folds)
    scores = source_score_table(fold_losses)
    full_selection, full_per, full_avg = full_targetwise_from_fold_losses(fold_losses)
    nested_selection, nested_per_df, nested_per, nested_avg = nested_targetwise_from_fold_losses(fold_losses)
    counts = nested_selection.groupby(["target", "source"]).size().reset_index(name="count").sort_values(["target", "count"], ascending=[True, False])

    prior_row = pd.read_csv(input_dir / "golf_scores.csv")
    prior = prior_row.loc[prior_row["source"] == "subject_prior", "avg_log_loss"]
    subject_prior_avg = float(prior.iloc[0]) if len(prior) else float("nan")
    global_best_avg = float(scores.iloc[0]["avg_log_loss"])
    global_best_source = str(scores.iloc[0]["source"])

    full_selection.to_csv(output_dir / "full_targetwise_selection_from_fold_losses.csv", index=False)
    nested_selection.to_csv(output_dir / "nested_targetwise_selection_from_fold_losses.csv", index=False)
    counts.to_csv(output_dir / "nested_selection_counts.csv", index=False)
    scores.to_csv(output_dir / "source_scores_from_fold_losses.csv", index=False)

    report = {
        "input_dir": str(input_dir),
        "subject_prior_avg_log_loss": subject_prior_avg,
        "global_best_source": global_best_source,
        "global_best_avg_log_loss": global_best_avg,
        "full_targetwise_avg_log_loss": full_avg,
        "full_targetwise_per_target": full_per,
        "nested_targetwise_avg_log_loss": nested_avg,
        "nested_targetwise_per_target": nested_per,
        "selection_optimism": nested_avg - full_avg,
        "nested_gain_vs_subject_prior": subject_prior_avg - nested_avg,
        "full_gain_vs_subject_prior": subject_prior_avg - full_avg,
        "global_gain_vs_subject_prior": subject_prior_avg - global_best_avg,
        "selection_counts": counts.to_dict(orient="records"),
    }
    (output_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    md = [
        "# Nested Deep Learning Golf Selection",
        "",
        "## Result",
        "",
        f"- Subject-prior baseline: `{subject_prior_avg:.6f}`",
        f"- Best global tiny decoder: `{global_best_avg:.6f}` (`{global_best_source}`)",
        f"- Full-OOF targetwise selection: `{full_avg:.6f}`",
        f"- Nested targetwise selection: `{nested_avg:.6f}`",
        f"- Estimated selection optimism: `{nested_avg - full_avg:.6f}`",
        f"- Nested gain vs subject prior: `{subject_prior_avg - nested_avg:.6f}`",
        "",
        "## Nested Per Target",
        "",
        dataframe_to_markdown(nested_per_df),
        "",
        "## Nested Selection Counts",
        "",
        dataframe_to_markdown(counts),
        "",
        "## Full Targetwise Selection",
        "",
        dataframe_to_markdown(full_selection),
        "",
        "## Top Global Sources",
        "",
        dataframe_to_markdown(scores.head(15)),
        "",
        "This diagnostic uses the saved fold-level losses from the golf run. It does not retrain models or reconstruct OOF predictions; it estimates the selection bias of choosing target-specific tiny decoders on the same OOF labels.",
    ]
    (output_dir / "report.md").write_text("\n".join(md), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Nested selection diagnostic for Deep Learning Golf fold losses.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--input-dir", default="outputs/deep_learning_golf_v1")
    parser.add_argument("--output-dir", default="outputs/nested_deep_learning_golf_selection_v1")
    parser.add_argument("--n-folds", type=int, default=5)
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
