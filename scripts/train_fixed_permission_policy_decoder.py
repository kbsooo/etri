from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from train_pruned_state_decoder import KEY_COLUMNS, TARGET_COLUMNS, average_log_loss, drift_vs_reference, subject_prior, write_prediction
from train_residual_cap_gate_decoder import align_oof, align_submission, read_oof, read_submission, residual_gate
from train_s2_sleep_retrieval_encoder import dataframe_to_markdown, make_subject_time_folds, normalize_keys


POLICIES = {
    "global_signed_s100_c050": {
        "default": ("capgate", "signed_margin", 1.00, 0.50),
    },
    "q1s3_signed_rest_stable": {
        "default": ("stable",),
        "Q1": ("capgate", "signed_margin", 1.25, 0.30),
        "S3": ("capgate", "signed_margin", 1.00, 0.30),
    },
    "q1s3_signed_s2_extended_rest_stable": {
        "default": ("stable",),
        "Q1": ("capgate", "signed_margin", 1.25, 0.30),
        "S2": ("extended",),
        "S3": ("capgate", "signed_margin", 1.00, 0.30),
    },
    "q1s3_signed_s1s2_extended_rest_stable": {
        "default": ("stable",),
        "Q1": ("capgate", "signed_margin", 1.25, 0.30),
        "S1": ("extended",),
        "S2": ("extended",),
        "S3": ("capgate", "signed_margin", 1.00, 0.30),
    },
    "q1s3_signed_s1s2s4_extended_q3_stable": {
        "default": ("stable",),
        "Q1": ("capgate", "signed_margin", 1.25, 0.30),
        "S1": ("extended",),
        "S2": ("extended",),
        "S3": ("capgate", "signed_margin", 1.00, 0.30),
        "S4": ("extended",),
    },
    "nested_majority_policy": {
        "default": ("stable",),
        "Q1": ("capgate", "signed_margin", 1.25, 0.30),
        "Q3": ("stable",),
        "S1": ("extended",),
        "S2": ("extended",),
        "S3": ("capgate", "signed_margin", 1.25, 0.30),
        "S4": ("extended",),
    },
}


def fold_safe_prior(train: pd.DataFrame, sample: pd.DataFrame, folds: int, alpha: float) -> tuple[np.ndarray, np.ndarray]:
    train_prior = np.zeros((len(train), len(TARGET_COLUMNS)), dtype=float)
    sample_parts = []
    for fold in make_subject_time_folds(train, folds):
        train_prior[fold.val_idx] = subject_prior(train.iloc[fold.train_idx], train.iloc[fold.val_idx], alpha)
        sample_parts.append(subject_prior(train.iloc[fold.train_idx], sample, alpha))
    return train_prior, np.mean(np.stack(sample_parts, axis=0), axis=0)


def apply_policy(
    policy: dict[str, tuple],
    stable: np.ndarray,
    extended: np.ndarray,
    prior: np.ndarray,
) -> np.ndarray:
    out = np.zeros_like(stable)
    cache: dict[tuple, np.ndarray] = {}
    for target_i, target in enumerate(TARGET_COLUMNS):
        action = policy.get(target, policy["default"])
        if action[0] == "stable":
            out[:, target_i] = stable[:, target_i]
        elif action[0] == "extended":
            out[:, target_i] = extended[:, target_i]
        elif action[0] == "capgate":
            _, mode, scale, cap = action
            key = (mode, scale, cap)
            if key not in cache:
                cache[key] = residual_gate(stable, extended, prior, float(scale), float(cap), str(mode))
            out[:, target_i] = cache[key][:, target_i]
        else:
            raise ValueError(action)
    return out


def describe_policy(policy: dict[str, tuple]) -> dict[str, str]:
    out = {}
    for target in TARGET_COLUMNS:
        action = policy.get(target, policy["default"])
        if action[0] == "capgate":
            out[target] = f"{action[1]}_s{int(float(action[2]) * 100):03d}_c{int(float(action[3]) * 100):03d}"
        else:
            out[target] = str(action[0])
    return out


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

    preds: dict[str, tuple[np.ndarray, np.ndarray]] = {
        "stable_signal_s4_temporal": (stable_oof, stable_sample),
        "extended_full_oof_winners": (extended_oof, extended_sample),
    }
    for name, policy in POLICIES.items():
        preds[name] = (
            apply_policy(policy, stable_oof, extended_oof, prior_oof),
            apply_policy(policy, stable_sample, extended_sample, prior_sample),
        )

    rows = []
    for name, (oof, submission) in preds.items():
        avg, per_target = average_log_loss(y_df, oof)
        drift = drift_vs_reference(sample, submission, Path(args.reference_submission) if args.reference_submission else None)
        rows.append(
            {
                "source": name,
                "avg_log_loss": avg,
                **per_target,
                "drift_vs_reference": drift.get("mean_abs_drift"),
                "corr_vs_reference": drift.get("corr"),
            }
        )
        write_prediction(output_dir / f"oof_{name}.csv", train, oof, oof=True)
        write_prediction(output_dir / f"submission_{name}.csv", sample, submission, oof=False)
    score_df = pd.DataFrame(rows).sort_values("avg_log_loss")
    policy_df = pd.DataFrame([{"policy": name, **describe_policy(policy)} for name, policy in POLICIES.items()])
    score_df.to_csv(output_dir / "fixed_permission_policy_scores.csv", index=False)
    policy_df.to_csv(output_dir / "policy_definitions.csv", index=False)
    report = {
        "scores": score_df.to_dict(orient="records"),
        "policies": policy_df.to_dict(orient="records"),
        "args": vars(args),
    }
    (output_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = [
        "# Fixed Permission Policy Decoder",
        "",
        "This experiment removes full target-wise grid selection and tests fixed decoder policies derived from nested cap-gate evidence: Q1/S3 get signed-margin residual permission, Q3 stays stable, and S1/S2/S4 are compared as stable vs aggressive extended residuals.",
        "",
        "## Scores",
        "",
        dataframe_to_markdown(score_df),
        "",
        "## Policy Definitions",
        "",
        dataframe_to_markdown(policy_df),
    ]
    (output_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(score_df.to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fixed target policy decoder using signed-margin residual permission.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--output-dir", default="outputs/fixed_permission_policy_decoder_v1")
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
