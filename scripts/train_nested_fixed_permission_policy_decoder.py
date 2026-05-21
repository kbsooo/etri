from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss

from train_fixed_permission_policy_decoder import POLICIES, apply_policy, fold_safe_prior
from train_pruned_state_decoder import EPS, TARGET_COLUMNS, average_log_loss, drift_vs_reference, write_prediction
from train_residual_cap_gate_decoder import align_oof, align_submission, read_oof, read_submission
from train_s2_sleep_retrieval_encoder import dataframe_to_markdown, make_subject_time_folds, normalize_keys


def select_global_policy(y_df: pd.DataFrame, pred_by_policy: dict[str, np.ndarray], fit_idx: np.ndarray) -> tuple[str, list[dict]]:
    rows = []
    y_fit = y_df.iloc[fit_idx]
    for name, pred in pred_by_policy.items():
        avg, per_target = average_log_loss(y_fit, pred[fit_idx])
        rows.append({"selection": "global", "policy": name, "avg_log_loss": avg, **per_target})
    best = min(rows, key=lambda row: row["avg_log_loss"])
    return str(best["policy"]), rows


def select_target_policies(y_df: pd.DataFrame, pred_by_policy: dict[str, np.ndarray], fit_idx: np.ndarray) -> tuple[dict[str, str], list[dict]]:
    choices = {}
    rows = []
    for target_i, target in enumerate(TARGET_COLUMNS):
        y_target = y_df.iloc[fit_idx][target].to_numpy(int)
        best = None
        for name, pred in pred_by_policy.items():
            loss = float(log_loss(y_target, np.clip(pred[fit_idx, target_i], EPS, 1.0 - EPS), labels=[0, 1]))
            row = {"selection": "targetwise", "target": target, "policy": name, "log_loss": loss}
            rows.append(row)
            if best is None or loss < best["log_loss"]:
                best = row
        if best is None:
            raise RuntimeError(target)
        choices[target] = str(best["policy"])
    return choices, rows


def apply_target_policy_choices(pred_by_policy: dict[str, np.ndarray], choices: dict[str, str], rows: int) -> np.ndarray:
    out = np.zeros((rows, len(TARGET_COLUMNS)), dtype=float)
    for target_i, target in enumerate(TARGET_COLUMNS):
        out[:, target_i] = pred_by_policy[choices[target]][:, target_i]
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
    prior_oof, prior_sample = fold_safe_prior(train, sample, args.folds, args.subject_alpha)

    pred_by_policy = {
        "stable_signal_s4_temporal": stable_oof,
        "extended_full_oof_winners": extended_oof,
        **{name: apply_policy(policy, stable_oof, extended_oof, prior_oof) for name, policy in POLICIES.items()},
    }
    sample_by_policy = {
        "stable_signal_s4_temporal": stable_sample,
        "extended_full_oof_winners": extended_sample,
        **{name: apply_policy(policy, stable_sample, extended_sample, prior_sample) for name, policy in POLICIES.items()},
    }

    folds = make_subject_time_folds(train, args.folds)
    nested_global_oof = np.zeros_like(stable_oof)
    nested_target_oof = np.zeros_like(stable_oof)
    global_sample_parts = []
    target_sample_parts = []
    selection_rows = []
    candidate_rows = []
    for outer_i, fold in enumerate(folds):
        global_choice, global_rows = select_global_policy(y_df, pred_by_policy, fold.train_idx)
        candidate_rows.extend({"outer_fold": outer_i, **row} for row in global_rows)
        nested_global_oof[fold.val_idx] = pred_by_policy[global_choice][fold.val_idx]
        global_sample_parts.append(sample_by_policy[global_choice])
        selection_rows.append({"outer_fold": outer_i, "selection": "global", "target": "ALL", "selected": global_choice})

        target_choices, target_rows = select_target_policies(y_df, pred_by_policy, fold.train_idx)
        candidate_rows.extend({"outer_fold": outer_i, **row} for row in target_rows)
        nested_target_oof[fold.val_idx] = apply_target_policy_choices(pred_by_policy, target_choices, len(train))[fold.val_idx]
        target_sample_parts.append(apply_target_policy_choices(sample_by_policy, target_choices, len(sample)))
        for target, selected in target_choices.items():
            selection_rows.append({"outer_fold": outer_i, "selection": "targetwise", "target": target, "selected": selected})

    nested_global_sample = np.mean(np.stack(global_sample_parts, axis=0), axis=0)
    nested_target_sample = np.mean(np.stack(target_sample_parts, axis=0), axis=0)

    score_inputs = {
        "stable_signal_s4_temporal": (stable_oof, stable_sample),
        "extended_full_oof_winners": (extended_oof, extended_sample),
        "fixed_policy_best": (pred_by_policy["q1s3_signed_s1s2s4_extended_q3_stable"], sample_by_policy["q1s3_signed_s1s2s4_extended_q3_stable"]),
        "nested_global_policy": (nested_global_oof, nested_global_sample),
        "nested_target_policy": (nested_target_oof, nested_target_sample),
    }
    score_rows = []
    for name, (oof, submission) in score_inputs.items():
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
    counts = selection_df.groupby(["selection", "target", "selected"]).size().reset_index(name="outer_count").sort_values(
        ["selection", "target", "outer_count"], ascending=[True, True, False]
    )

    score_df.to_csv(output_dir / "nested_fixed_policy_scores.csv", index=False)
    selection_df.to_csv(output_dir / "outer_policy_selection.csv", index=False)
    counts.to_csv(output_dir / "selection_counts.csv", index=False)
    candidate_df.to_csv(output_dir / "outer_candidate_policy_scores.csv", index=False)
    write_prediction(output_dir / "oof_nested_global_policy.csv", train, nested_global_oof, oof=True)
    write_prediction(output_dir / "submission_nested_global_policy.csv", sample, nested_global_sample, oof=False)
    write_prediction(output_dir / "oof_nested_target_policy.csv", train, nested_target_oof, oof=True)
    write_prediction(output_dir / "submission_nested_target_policy.csv", sample, nested_target_sample, oof=False)
    (output_dir / "report.json").write_text(
        json.dumps({"scores": score_df.to_dict(orient="records"), "selection_counts": counts.to_dict(orient="records"), "args": vars(args)}, indent=2),
        encoding="utf-8",
    )
    lines = [
        "# Nested Fixed Permission Policy Decoder",
        "",
        "This stress test selects among fixed permission policies on each outer fold's train rows and scores on held-out rows. It estimates how much of the fixed-policy improvement is policy-search optimism.",
        "",
        "## Scores",
        "",
        dataframe_to_markdown(score_df),
        "",
        "## Selection Counts",
        "",
        dataframe_to_markdown(counts),
    ]
    (output_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(score_df.to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Nested validation for fixed permission policy decoder candidates.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--output-dir", default="outputs/nested_fixed_permission_policy_decoder_v1")
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
