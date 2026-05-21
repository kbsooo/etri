from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from train_pruned_state_decoder import (
    KEY_COLUMNS,
    TARGET_COLUMNS,
    average_log_loss,
    cap_columns_by_variance,
    drift_vs_reference,
    family_masks,
    run_preset,
    targetwise_select,
    write_prediction,
)
from train_s2_sleep_retrieval_encoder import dataframe_to_markdown, merge_feature_tables, normalize_keys


@dataclass(frozen=True)
class FamilyRecipe:
    name: str
    include_any: tuple[str, ...] = ()
    drop_any: tuple[str, ...] = ()


RECIPES = [
    FamilyRecipe("only_rhythm_deviation", include_any=("rhythm", "deviation")),
    FamilyRecipe("only_rhythm_missingness", include_any=("rhythm", "missingness")),
    FamilyRecipe("only_rhythm_cross_modal", include_any=("rhythm", "cross_modal")),
    FamilyRecipe("only_deviation_cross_modal", include_any=("deviation", "cross_modal")),
    FamilyRecipe("only_missingness_cross_modal", include_any=("missingness", "cross_modal")),
    FamilyRecipe("only_rhythm_deviation_cross_modal", include_any=("rhythm", "deviation", "cross_modal")),
    FamilyRecipe("only_rhythm_deviation_missingness", include_any=("rhythm", "deviation", "missingness")),
    FamilyRecipe("only_state_core", include_any=("rhythm", "deviation", "cross_modal", "missingness", "rank")),
    FamilyRecipe("drop_raw_ratio", drop_any=("raw", "ratio")),
    FamilyRecipe("drop_raw_rank", drop_any=("raw", "rank")),
    FamilyRecipe("drop_ratio_rank", drop_any=("ratio", "rank")),
    FamilyRecipe("drop_ratio_temporal_delta", drop_any=("ratio", "temporal_delta")),
    FamilyRecipe("drop_late_rank", drop_any=("late_pool", "rank")),
    FamilyRecipe("drop_gps_phone", drop_any=("gps", "phone")),
    FamilyRecipe("drop_sleep_late", drop_any=("sleep", "late_pool")),
    FamilyRecipe("drop_missingness_ratio", drop_any=("missingness", "ratio")),
]


class NamedPreset:
    def __init__(self, name: str) -> None:
        self.name = name


def columns_for_recipe(columns: list[str], recipe: FamilyRecipe) -> list[str]:
    masks = family_masks(columns)
    if recipe.include_any:
        keep = np.zeros(len(columns), dtype=bool)
        for family in recipe.include_any:
            keep |= masks[family]
    else:
        keep = np.ones(len(columns), dtype=bool)
    for family in recipe.drop_any:
        keep &= ~masks[family]
    selected = [col for col, flag in zip(columns, keep) if flag]
    if not selected:
        raise ValueError(f"{recipe.name} selected no columns")
    return selected


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    train_x, sample_x = merge_feature_tables(train, sample)
    all_cols = train_x.columns.tolist()
    y_df = train[TARGET_COLUMNS].astype(int)

    reports = []
    all_oof: dict[str, np.ndarray] = {}
    all_sample: dict[str, np.ndarray] = {}
    feature_rows = []
    for recipe in RECIPES:
        columns = columns_for_recipe(all_cols, recipe)
        columns = cap_columns_by_variance(train_x, sample_x, columns, args.max_features)
        feature_rows.append({"recipe": recipe.name, "feature_count": len(columns)})
        if len(columns) < args.min_features:
            continue
        report, oof, sample_pred = run_preset(NamedPreset(recipe.name), train, sample, train_x, sample_x, columns, args)
        reports.append(report)
        for candidate, pred in oof.items():
            key = f"{recipe.name}__{candidate}"
            all_oof[key] = pred
            all_sample[key] = sample_pred[candidate]

    if not reports:
        raise RuntimeError("No family recipe produced a report")

    score_df = pd.DataFrame([row for report in reports for row in report["scores"]]).sort_values("avg_log_loss")
    recipe_df = pd.DataFrame(
        [
            {
                "recipe": report["preset"],
                "feature_count": report["feature_count"],
                "best_candidate": report["best_candidate"],
                "best_avg_log_loss": report["best_avg_log_loss"],
            }
            for report in reports
        ]
    ).sort_values("best_avg_log_loss")
    selected, tw_oof, tw_sample = targetwise_select(y_df, all_oof, all_sample)
    best_key = f"{score_df.iloc[0]['preset']}__{score_df.iloc[0]['candidate']}"
    best_oof = all_oof[best_key]
    best_sample = all_sample[best_key]
    best_avg, best_targets = average_log_loss(y_df, best_oof)
    tw_avg, tw_targets = average_log_loss(y_df, tw_oof)

    pd.DataFrame(feature_rows).to_csv(output_dir / "recipe_feature_counts.csv", index=False)
    score_df.to_csv(output_dir / "candidate_scores.csv", index=False)
    recipe_df.to_csv(output_dir / "recipe_scores.csv", index=False)
    selected.to_csv(output_dir / "targetwise_selection.csv", index=False)
    write_prediction(output_dir / "oof_extended_family_best_global.csv", train, best_oof, oof=True)
    write_prediction(output_dir / "submission_extended_family_best_global.csv", sample, best_sample, oof=False)
    write_prediction(output_dir / "oof_extended_family_targetwise.csv", train, tw_oof, oof=True)
    write_prediction(output_dir / "submission_extended_family_targetwise.csv", sample, tw_sample, oof=False)

    diagnostics = {
        "best_global_key": best_key,
        "best_global": {"avg_log_loss": best_avg, **best_targets},
        "targetwise": {"avg_log_loss": tw_avg, **tw_targets},
        "targetwise_selection": selected.to_dict(orient="records"),
        "drift_vs_reference_best_global": drift_vs_reference(sample, best_sample, Path(args.reference_submission) if args.reference_submission else None),
        "drift_vs_reference_targetwise": drift_vs_reference(sample, tw_sample, Path(args.reference_submission) if args.reference_submission else None),
        "args": vars(args),
    }
    (output_dir / "report.json").write_text(json.dumps({"reports": reports, "diagnostics": diagnostics}, indent=2), encoding="utf-8")
    lines = [
        "# Extended Family Pruning Decoder",
        "",
        "This experiment tests feature-family combinations beyond one-family-only/drop ablations.",
        "",
        "## Best Recipes",
        "",
        dataframe_to_markdown(recipe_df),
        "",
        "## Best Candidates",
        "",
        dataframe_to_markdown(score_df.head(30)),
        "",
        "## Target-wise Selection",
        "",
        dataframe_to_markdown(selected),
        "",
        "## Summary",
        "",
        f"- Best global: `{best_key}` avg `{best_avg:.6f}`",
        f"- Target-wise avg: `{tw_avg:.6f}`",
        f"- Best global drift vs reference: `{diagnostics['drift_vs_reference_best_global'].get('mean_abs_drift', float('nan')):.6f}`",
        f"- Target-wise drift vs reference: `{diagnostics['drift_vs_reference_targetwise'].get('mean_abs_drift', float('nan')):.6f}`",
    ]
    (output_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"best_global={best_key} avg={best_avg:.6f}")
    print(f"targetwise avg={tw_avg:.6f}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extended feature-family combination pruning experiment.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--output-dir", default="outputs/extended_family_pruning_decoder_v1")
    parser.add_argument("--reference-submission", default="outputs/v83_repaired_v80/submission_v83_gq015_gs010.csv")
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--max-features", type=int, default=520)
    parser.add_argument("--min-features", type=int, default=20)
    parser.add_argument("--pca-dim", type=int, default=28)
    parser.add_argument("--n-proto", type=int, default=10)
    parser.add_argument("--n-label-proto", type=int, default=12)
    parser.add_argument("--logreg-c", type=float, default=0.03)
    parser.add_argument("--subject-alpha", type=float, default=10.0)
    parser.add_argument("--max-pairs", type=int, default=10000)
    return parser.parse_args()


if __name__ == "__main__":
    main()
