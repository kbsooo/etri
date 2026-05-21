from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from probe_domain_ssl_latents import (
    EPS,
    KEY_COLUMNS,
    TARGET_COLUMNS,
    average_log_loss,
    feature_views,
    fit_probe,
    load_latent_table,
    make_subject_time_folds,
    normalize_keys,
    subject_prior,
    write_prediction,
)


DEFAULT_LATENTS = {
    "best": "artifacts/domain_best_late_fusion_v1.parquet",
    "td_trajectory": "outputs/domain_temporal_deviation_probe_v1/subsets/trajectory.parquet",
}


def parse_latent_specs(items: list[str]) -> dict[str, Path]:
    specs = {name: Path(path) for name, path in DEFAULT_LATENTS.items()}
    for item in items:
        if "=" not in item:
            raise ValueError(f"Latent spec must be name=path, got {item}")
        name, path = item.split("=", 1)
        specs[name] = Path(path)
    return specs


def parse_source(source: str) -> tuple[str, str, float, float]:
    parts = source.split("__")
    if len(parts) != 3:
        raise ValueError(f"Unsupported source format: {source}")
    latent, view, params = parts
    c_part, b_part = params.split("_")
    return latent, view, float(c_part.removeprefix("c")), float(b_part.removeprefix("b"))


def source_family(source: str) -> str:
    if source.startswith("best_plus_mobility_constriction") or source.startswith("mobility_constriction"):
        return "mobility_constriction"
    if source.startswith("best_plus_fatigue_carryover") or source.startswith("fatigue_carryover"):
        return "fatigue_carryover"
    if source.startswith("best_plus_routine_digital"):
        return "routine_digital"
    if source.startswith("best_plus_digital_sleep") or source.startswith("digital_sleep"):
        return "digital_sleep"
    if source.startswith("best_plus_routine_regularity") or source.startswith("routine_regularity"):
        return "routine_regularity"
    if source.startswith("best_plus_sleep_intrusion") or source.startswith("sleep_intrusion"):
        return "sleep_intrusion"
    if source.startswith("best_plus_trajectory_proto") or source.startswith("trajectory_proto"):
        return "trajectory_proto"
    if source.startswith("best_plus_event_rhythm") or source.startswith("event_rhythm"):
        return "event_rhythm"
    if source.startswith("td_trajectory"):
        return "trajectory"
    if source.startswith("best"):
        return "best_late_fusion"
    return "other"


def select_test_sources(fold_losses: pd.DataFrame, base_source: str, min_train_delta: float) -> pd.DataFrame:
    rows = []
    for target in TARGET_COLUMNS:
        target_losses = fold_losses[fold_losses["target"] == target]
        scores = (
            target_losses.groupby("source", as_index=False)["loss"]
            .mean()
            .rename(columns={"loss": "selector_loss"})
            .sort_values(["selector_loss", "source"], ascending=[True, True])
        )
        raw_best = scores.iloc[0]
        base_loss = float(scores.loc[scores["source"] == base_source, "selector_loss"].iloc[0])
        if float(raw_best["selector_loss"]) < base_loss - min_train_delta:
            selected_source = str(raw_best["source"])
            selected_loss = float(raw_best["selector_loss"])
            action = "switch"
        else:
            selected_source = base_source
            selected_loss = base_loss
            action = "base"
        rows.append(
            {
                "target": target,
                "selected_source": selected_source,
                "source_family": source_family(selected_source),
                "raw_best_source": str(raw_best["source"]),
                "raw_best_selector_loss": float(raw_best["selector_loss"]),
                "base_selector_loss": base_loss,
                "selector_loss": selected_loss,
                "selection_action": action,
            }
        )
    return pd.DataFrame(rows)


def dataframe_to_markdown(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "_No rows._"
    cols = frame.columns.tolist()
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in frame.iterrows():
        vals = []
        for col in cols:
            value = row[col]
            vals.append(f"{value:.6f}" if isinstance(value, float) else str(value))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def run(args: argparse.Namespace) -> None:
    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    folds = make_subject_time_folds(train, args.n_folds)
    latent_specs = parse_latent_specs(args.latent)
    latent_tables = {name: load_latent_table(path, train, sample) for name, path in latent_specs.items()}
    nested_selection = pd.read_csv(args.nested_selected)
    if args.test_selected:
        test_selection = pd.read_csv(args.test_selected)
    else:
        fold_losses = pd.read_csv(args.fold_losses)
        source_prefixes = tuple(args.source_prefix)
        fold_losses = fold_losses[fold_losses["source"].astype(str).str.startswith(source_prefixes)].copy()
        test_selection = select_test_sources(fold_losses, args.base_source, args.min_train_delta)

    needed_sources = set(nested_selection["selected_source"].astype(str)) | set(test_selection["selected_source"].astype(str))
    source_specs = {source: parse_source(source) for source in needed_sources}

    oof = np.zeros((len(train), len(TARGET_COLUMNS)), dtype=float)
    sample_fold_predictions: dict[str, list[np.ndarray]] = {source: [] for source in needed_sources}
    fit_rows = []

    for fold_i, (fit_idx, eval_idx) in enumerate(folds, 1):
        fit_frame = train.iloc[fit_idx]
        eval_frame = train.iloc[eval_idx]
        prior_eval_all = subject_prior(fit_frame, eval_frame, args.prior_alpha)
        prior_sample_all = subject_prior(fit_frame, sample, args.prior_alpha)
        fold_source_sample = {
            source: np.zeros((len(sample), len(TARGET_COLUMNS)), dtype=float)
            for source in needed_sources
        }
        view_cache: dict[tuple[str, str], tuple[np.ndarray, np.ndarray, np.ndarray]] = {}
        for source, (latent_name, view_name, c_value, blend) in source_specs.items():
            train_x, sample_x, z_cols = latent_tables[latent_name]
            cache_key = (latent_name, view_name)
            if cache_key not in view_cache:
                view_cache[cache_key] = feature_views(train_x, sample_x, z_cols, fit_idx, eval_idx)[view_name]
            x_fit, x_eval, x_sample = view_cache[cache_key]
            for target_i, target in enumerate(TARGET_COLUMNS):
                pred_eval, pred_sample = fit_probe(
                    x_fit,
                    fit_frame[target].to_numpy(int),
                    x_eval,
                    x_sample,
                    prior_eval_all[:, target_i],
                    prior_sample_all[:, target_i],
                    c_value,
                    blend,
                )
                selected = nested_selection[
                    (nested_selection["held_fold"] == fold_i)
                    & (nested_selection["target"] == target)
                    & (nested_selection["selected_source"] == source)
                ]
                if not selected.empty:
                    oof[eval_idx, target_i] = pred_eval
                fold_source_sample[source][:, target_i] = pred_sample
                fit_rows.append(
                    {
                        "fold": fold_i,
                        "source": source,
                        "target": target,
                        "loss": float(selected["held_loss"].iloc[0]) if not selected.empty else np.nan,
                    }
                )
        for source, pred in fold_source_sample.items():
            sample_fold_predictions[source].append(pred)

    sample_by_source = {source: np.mean(parts, axis=0) for source, parts in sample_fold_predictions.items()}
    sample_pred = np.zeros((len(sample), len(TARGET_COLUMNS)), dtype=float)
    for target_i, target in enumerate(TARGET_COLUMNS):
        selected_source = str(test_selection.loc[test_selection["target"] == target, "selected_source"].iloc[0])
        sample_pred[:, target_i] = sample_by_source[selected_source][:, target_i]

    avg, per_target = average_log_loss(train[TARGET_COLUMNS], oof)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    write_prediction(output_dir / "oof_nested_temporal_decoder.csv", train, oof, oof=True)
    write_prediction(output_dir / "submission_nested_temporal_decoder.csv", sample, np.clip(sample_pred, EPS, 1.0 - EPS), oof=False)
    nested_selection.to_csv(output_dir / "oof_source_selection.csv", index=False)
    test_selection.to_csv(output_dir / "test_source_selection.csv", index=False)
    pd.DataFrame(fit_rows).to_csv(output_dir / "fit_rows.csv", index=False)
    report = {
        "avg_log_loss": avg,
        "per_target_log_loss": per_target,
        "base_source": args.base_source,
        "min_train_delta": args.min_train_delta,
        "needed_sources": sorted(needed_sources),
        "test_source_selection": test_selection.to_dict(orient="records"),
    }
    (output_dir / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    md = [
        "# Nested Temporal Decoder",
        "",
        "## Purpose",
        "",
        "Materialize nested source-selection diagnostics as OOF and test prediction files.",
        "",
        "## OOF Score",
        "",
        f"- Avg logloss: `{avg:.6f}`",
        "",
        "## Per Target",
        "",
        dataframe_to_markdown(pd.DataFrame([per_target])),
        "",
        "## Test-Time Source Selection",
        "",
        dataframe_to_markdown(test_selection),
        "",
        "## Read",
        "",
        "Only targets listed in the source-selection table move away from the current best late-fusion source.",
    ]
    (output_dir / "report.md").write_text("\n".join(md), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build OOF/test predictions from nested temporal source selection.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--latent", action="append", default=[], help="Extra or overriding latent spec as name=path.")
    parser.add_argument("--nested-selected", default="outputs/domain_temporal_deviation_nested_selection_trajectory_only_margin_0p003/nested_selected_fold_losses.csv")
    parser.add_argument("--test-selected", default="")
    parser.add_argument("--fold-losses", default="outputs/domain_temporal_deviation_subset_probe_v1/fold_target_losses.csv")
    parser.add_argument("--output-dir", default="outputs/domain_nested_temporal_decoder_v1")
    parser.add_argument("--base-source", default="best__absolute_plus_deviation__c0.3_b0.2")
    parser.add_argument("--source-prefix", nargs="*", default=["best", "td_trajectory"])
    parser.add_argument("--min-train-delta", type=float, default=0.003)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--prior-alpha", type=float, default=8.0)
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
