from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss

from train_pruned_state_decoder import EPS, KEY_COLUMNS, TARGET_COLUMNS, average_log_loss, drift_vs_reference, safe_logit, sigmoid, subject_prior, write_prediction
from train_residual_cap_gate_decoder import (
    CAPS,
    GATE_MODES,
    SCALES,
    align_oof,
    align_submission,
    read_oof,
    read_submission,
    residual_gate,
)
from train_s2_sleep_retrieval_encoder import dataframe_to_markdown, make_subject_time_folds, normalize_keys


def fold_safe_prior(train: pd.DataFrame, sample: pd.DataFrame, folds: int, alpha: float) -> tuple[np.ndarray, np.ndarray, list]:
    train_prior = np.zeros((len(train), len(TARGET_COLUMNS)), dtype=float)
    sample_parts = []
    fold_defs = []
    for fold in make_subject_time_folds(train, folds):
        train_prior[fold.val_idx] = subject_prior(train.iloc[fold.train_idx], train.iloc[fold.val_idx], alpha)
        sample_parts.append(subject_prior(train.iloc[fold.train_idx], sample, alpha))
        fold_defs.append(fold)
    return np.clip(train_prior, EPS, 1.0 - EPS), np.clip(np.mean(np.stack(sample_parts, axis=0), axis=0), EPS, 1.0 - EPS), fold_defs


def source_name(mode: str, scale: float, cap: float) -> str:
    return f"capgate_{mode}_s{int(scale * 100):03d}_c{int(cap * 100):03d}"


def source_params(name: str) -> tuple[str, float, float]:
    if name == "stable_signal_s4_temporal":
        return "stable", 0.0, 0.0
    if name == "extended_full_oof_winners":
        return "extended", 0.0, 0.0
    parts = name.replace("capgate_", "").split("_")
    mode = "_".join(parts[:-2])
    scale = int(parts[-2][1:]) / 100.0
    cap = int(parts[-1][1:]) / 100.0
    return mode, scale, cap


def build_source_matrix(
    stable: np.ndarray,
    extended: np.ndarray,
    prior: np.ndarray,
    threshold_residual: np.ndarray,
) -> dict[str, np.ndarray]:
    out = {
        "stable_signal_s4_temporal": stable,
        "extended_full_oof_winners": extended,
    }
    for mode in GATE_MODES:
        for scale in SCALES:
            for cap in CAPS:
                thresholds = None
                if mode in {"top_abs_50", "top_abs_35"}:
                    pct = 50 if mode == "top_abs_50" else 65
                    thresholds = np.percentile(np.abs(threshold_residual), pct, axis=0)
                out[source_name(mode, scale, cap)] = residual_gate(stable, extended, prior, scale, cap, mode, thresholds)
    return out


def select_global_source(
    y_df: pd.DataFrame,
    pred_by_source: dict[str, np.ndarray],
    fit_idx: np.ndarray,
) -> tuple[str, list[dict]]:
    rows = []
    y_fit = y_df.iloc[fit_idx]
    for name, pred in pred_by_source.items():
        avg, per_target = average_log_loss(y_fit, pred[fit_idx])
        rows.append({"selection": "global", "source": name, "avg_log_loss": avg, **per_target})
    best = min(rows, key=lambda row: row["avg_log_loss"])
    return str(best["source"]), rows


def select_target_sources(
    y_df: pd.DataFrame,
    pred_by_source: dict[str, np.ndarray],
    fit_idx: np.ndarray,
) -> tuple[dict[str, str], list[dict]]:
    rows = []
    choices = {}
    for target_i, target in enumerate(TARGET_COLUMNS):
        best = None
        y_target = y_df.iloc[fit_idx][target].to_numpy(int)
        for name, pred in pred_by_source.items():
            loss = float(log_loss(y_target, np.clip(pred[fit_idx, target_i], EPS, 1.0 - EPS), labels=[0, 1]))
            row = {"selection": "targetwise", "target": target, "source": name, "log_loss": loss}
            rows.append(row)
            if best is None or loss < best["log_loss"]:
                best = row
        if best is None:
            raise RuntimeError(target)
        choices[target] = str(best["source"])
    return choices, rows


def apply_target_sources(pred_by_source: dict[str, np.ndarray], choices: dict[str, str], rows: int) -> np.ndarray:
    out = np.zeros((rows, len(TARGET_COLUMNS)), dtype=float)
    for target_i, target in enumerate(TARGET_COLUMNS):
        out[:, target_i] = pred_by_source[choices[target]][:, target_i]
    return np.clip(out, EPS, 1.0 - EPS)


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    y_df = train[TARGET_COLUMNS].astype(int)

    stable_oof = align_oof(train, read_oof(Path(args.stable_oof)))
    stable_sample = align_submission(sample, read_submission(Path(args.stable_submission)))
    extended_oof = align_oof(train, read_oof(Path(args.extended_oof)))
    extended_sample = align_submission(sample, read_submission(Path(args.extended_submission)))
    prior_oof, prior_sample, folds = fold_safe_prior(train, sample, args.folds, args.subject_alpha)

    nested_global_oof = np.zeros_like(stable_oof)
    nested_target_oof = np.zeros_like(stable_oof)
    global_sample_parts = []
    target_sample_parts = []
    selection_rows = []
    candidate_rows = []
    for outer_i, fold in enumerate(folds):
        threshold_residual = safe_logit(extended_oof[fold.train_idx]) - safe_logit(stable_oof[fold.train_idx])
        pred_by_source = build_source_matrix(stable_oof, extended_oof, prior_oof, threshold_residual)
        sample_by_source = build_source_matrix(stable_sample, extended_sample, prior_sample, threshold_residual)

        global_choice, global_rows = select_global_source(y_df, pred_by_source, fold.train_idx)
        candidate_rows.extend({"outer_fold": outer_i, **row} for row in global_rows)
        nested_global_oof[fold.val_idx] = pred_by_source[global_choice][fold.val_idx]
        global_sample_parts.append(sample_by_source[global_choice])
        selection_rows.append({"outer_fold": outer_i, "selection": "global", "target": "ALL", "selected": global_choice})

        target_choices, target_rows = select_target_sources(y_df, pred_by_source, fold.train_idx)
        candidate_rows.extend({"outer_fold": outer_i, **row} for row in target_rows)
        nested_target_oof[fold.val_idx] = apply_target_sources(pred_by_source, target_choices, len(train))[fold.val_idx]
        target_sample_parts.append(apply_target_sources(sample_by_source, target_choices, len(sample)))
        for target, selected in target_choices.items():
            selection_rows.append({"outer_fold": outer_i, "selection": "targetwise", "target": target, "selected": selected})

    nested_global_sample = np.mean(np.stack(global_sample_parts, axis=0), axis=0)
    nested_target_sample = np.mean(np.stack(target_sample_parts, axis=0), axis=0)

    reference_sources = {
        "stable_signal_s4_temporal": (stable_oof, stable_sample),
        "extended_full_oof_winners": (extended_oof, extended_sample),
        "nested_global_capgate": (nested_global_oof, nested_global_sample),
        "nested_target_capgate": (nested_target_oof, nested_target_sample),
    }
    score_rows = []
    for name, (oof, submission) in reference_sources.items():
        avg, per_target = average_log_loss(y_df, oof)
        drift = drift_vs_reference(sample, submission, Path(args.reference_submission) if args.reference_submission else None)
        score_rows.append(
            {
                "source": name,
                "avg_log_loss": avg,
                **per_target,
                "drift_vs_reference": drift.get("mean_abs_drift"),
                "corr_vs_reference": drift.get("corr"),
            }
        )
    score_df = pd.DataFrame(score_rows).sort_values("avg_log_loss")
    selection_df = pd.DataFrame(selection_rows)
    candidate_df = pd.DataFrame(candidate_rows)
    selection_counts = selection_df.groupby(["selection", "target", "selected"]).size().reset_index(name="outer_count").sort_values(
        ["selection", "target", "outer_count"], ascending=[True, True, False]
    )

    score_df.to_csv(output_dir / "nested_cap_gate_scores.csv", index=False)
    selection_df.to_csv(output_dir / "outer_selection.csv", index=False)
    selection_counts.to_csv(output_dir / "selection_counts.csv", index=False)
    candidate_df.to_csv(output_dir / "outer_candidate_scores.csv", index=False)
    write_prediction(output_dir / "oof_nested_global_capgate.csv", train, nested_global_oof, oof=True)
    write_prediction(output_dir / "submission_nested_global_capgate.csv", sample, nested_global_sample, oof=False)
    write_prediction(output_dir / "oof_nested_target_capgate.csv", train, nested_target_oof, oof=True)
    write_prediction(output_dir / "submission_nested_target_capgate.csv", sample, nested_target_sample, oof=False)

    diagnostics = {
        "scores": score_df.to_dict(orient="records"),
        "selection_counts": selection_counts.to_dict(orient="records"),
        "args": vars(args),
    }
    (output_dir / "report.json").write_text(json.dumps(diagnostics, indent=2), encoding="utf-8")
    lines = [
        "# Nested Residual Cap-Gate Decoder",
        "",
        "This stress test selects residual cap-gate parameters only on each outer fold's train rows, then scores the selected source on held-out outer rows. It tests whether the full-OOF cap-gate improvement survives selection bias.",
        "",
        "## Scores",
        "",
        dataframe_to_markdown(score_df),
        "",
        "## Selection Counts",
        "",
        dataframe_to_markdown(selection_counts),
        "",
        "## Best Outer Candidate Rows",
        "",
        dataframe_to_markdown(candidate_df.sort_values([col for col in ["outer_fold", "selection", "target", "avg_log_loss", "log_loss"] if col in candidate_df.columns]).head(100)),
    ]
    (output_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(score_df.to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Nested/stress validation for residual cap-gate decoder selection.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--output-dir", default="outputs/nested_residual_cap_gate_decoder_v1")
    parser.add_argument("--stable-oof", default="outputs/stable_extended_consensus_decoder_v1/oof_stable_signal_s4_temporal.csv")
    parser.add_argument("--stable-submission", default="outputs/stable_extended_consensus_decoder_v1/submission_stable_signal_s4_temporal.csv")
    parser.add_argument("--extended-oof", default="outputs/stable_extended_consensus_decoder_v1/oof_extended_full_oof_winners.csv")
    parser.add_argument("--extended-submission", default="outputs/stable_extended_consensus_decoder_v1/submission_extended_full_oof_winners.csv")
    parser.add_argument("--reference-submission", default="outputs/v83_repaired_v80/submission_v83_gq015_gs010.csv")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--subject-alpha", type=float, default=10.0)
    return parser.parse_args()


if __name__ == "__main__":
    main()
