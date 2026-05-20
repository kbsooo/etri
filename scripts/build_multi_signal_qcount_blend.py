from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss


KEY_COLUMNS = ["subject_id", "sleep_date", "lifelog_date"]
TARGET_COLUMNS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
EPS = 1e-5


def normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in KEY_COLUMNS:
        out[col] = out[col].astype(str)
    return out


def prediction_matrix(oof: pd.DataFrame) -> np.ndarray:
    pred = np.column_stack([oof[f"pred_{target}"].to_numpy(dtype=float) for target in TARGET_COLUMNS])
    return np.clip(pred, EPS, 1.0 - EPS)


def submission_matrix(submission: pd.DataFrame) -> np.ndarray:
    return np.clip(submission[TARGET_COLUMNS].to_numpy(dtype=float), EPS, 1.0 - EPS)


def load_oof(path: str, train: pd.DataFrame) -> np.ndarray:
    df = normalize_keys(pd.read_csv(path))
    if not df[KEY_COLUMNS].equals(train[KEY_COLUMNS]):
        raise ValueError(f"OOF keys do not match train keys: {path}")
    return prediction_matrix(df)


def load_submission(path: str, sample: pd.DataFrame) -> np.ndarray:
    df = normalize_keys(pd.read_csv(path))
    if not df[KEY_COLUMNS].equals(sample[KEY_COLUMNS]):
        raise ValueError(f"Submission keys do not match sample keys: {path}")
    return submission_matrix(df)


def average_loss(y: pd.DataFrame, pred: np.ndarray) -> tuple[float, dict[str, float]]:
    per_target = {
        target: float(log_loss(y[target].to_numpy(), pred[:, target_i], labels=[0, 1]))
        for target_i, target in enumerate(TARGET_COLUMNS)
    }
    return float(np.mean(list(per_target.values()))), per_target


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    display = df.copy()
    for col in display.columns:
        if pd.api.types.is_float_dtype(display[col]):
            display[col] = display[col].map(lambda value: "" if pd.isna(value) else f"{value:.6f}")
        else:
            display[col] = display[col].map(lambda value: "" if pd.isna(value) else str(value))
    header = "| " + " | ".join(display.columns) + " |"
    separator = "| " + " | ".join(["---"] * len(display.columns)) + " |"
    rows = ["| " + " | ".join(row) + " |" for row in display.astype(str).to_numpy()]
    return "\n".join([header, separator, *rows])


def blend(
    base: np.ndarray,
    markov: np.ndarray,
    prior: np.ndarray,
    sleep: np.ndarray,
    broad: np.ndarray,
    args: argparse.Namespace,
) -> np.ndarray:
    pred = (
        base
        + args.markov_weight * (markov - base)
        + args.prior_weight * (prior - base)
        + args.sleep_weight * (sleep - base)
    )
    if args.broad_s4_weight:
        s4_i = TARGET_COLUMNS.index("S4")
        pred[:, s4_i] += args.broad_s4_weight * (broad[:, s4_i] - base[:, s4_i])
    return np.clip(pred, EPS, 1.0 - EPS)


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))

    base_oof = load_oof(args.base_oof, train)
    markov_oof = load_oof(args.markov_oof, train)
    prior_oof = load_oof(args.prior_oof, train)
    sleep_oof = load_oof(args.sleep_oof, train)
    broad_oof = load_oof(args.broad_oof, train)

    base_sub = load_submission(args.base_submission, sample)
    markov_sub = load_submission(args.markov_submission, sample)
    prior_sub = load_submission(args.prior_submission, sample)
    sleep_sub = load_submission(args.sleep_submission, sample)
    broad_sub = load_submission(args.broad_submission, sample)

    final_oof = blend(base_oof, markov_oof, prior_oof, sleep_oof, broad_oof, args)
    final_sub = blend(base_sub, markov_sub, prior_sub, sleep_sub, broad_sub, args)

    y = train[TARGET_COLUMNS]
    base_avg, base_targets = average_loss(y, base_oof)
    final_avg, final_targets = average_loss(y, final_oof)
    target_deltas = {target: base_targets[target] - final_targets[target] for target in TARGET_COLUMNS}

    oof_df = train[KEY_COLUMNS + TARGET_COLUMNS].copy()
    for target_i, target in enumerate(TARGET_COLUMNS):
        oof_df[f"pred_{target}"] = final_oof[:, target_i]
    oof_path = output_dir / "oof_multi_signal_qcount_blend.csv"
    oof_df.to_csv(oof_path, index=False)

    submission = pd.read_csv(args.sample_path)
    for target_i, target in enumerate(TARGET_COLUMNS):
        submission[target] = final_sub[:, target_i]
    submission_path = output_dir / "submission_multi_signal_qcount_blend.csv"
    submission.to_csv(submission_path, index=False)

    report = {
        "base_avg_log_loss": base_avg,
        "final_avg_log_loss": final_avg,
        "improvement": base_avg - final_avg,
        "base_targets": base_targets,
        "final_targets": final_targets,
        "target_deltas": target_deltas,
        "weights": {
            "markov": args.markov_weight,
            "prior": args.prior_weight,
            "sleep": args.sleep_weight,
            "broad_s4_only": args.broad_s4_weight,
        },
        "inputs": vars(args),
    }
    (output_dir / "multi_signal_qcount_blend_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# Multi-signal Q-count Blend",
        "",
        f"- Base avg logloss: `{base_avg:.6f}`",
        f"- Final avg logloss: `{final_avg:.6f}`",
        f"- Improvement: `{base_avg - final_avg:.6f}`",
        f"- Weights: markov `{args.markov_weight:g}`, prior `{args.prior_weight:g}`, sleep `{args.sleep_weight:g}`, broad S4-only `{args.broad_s4_weight:g}`",
        "",
        "## Target Deltas",
        "",
        dataframe_to_markdown(pd.DataFrame([target_deltas])),
        "",
    ]
    (output_dir / "multi_signal_qcount_blend_report.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"base={base_avg:.6f} final={final_avg:.6f} improvement={base_avg - final_avg:.6f}")
    print(f"saved: {submission_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Blend weak post-Q-count signals with conservative fixed weights.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--base-oof", default="outputs/block_aware_targetwise_transductive_q_count_vs_w03/oof_block_aware_targetwise_blend.csv")
    parser.add_argument("--base-submission", default="outputs/block_aware_targetwise_transductive_q_count_vs_w03/submission_block_aware_targetwise_blend.csv")
    parser.add_argument("--markov-oof", default="outputs/markov_label_prior_on_qcount_probe/oof_markov_label_prior.csv")
    parser.add_argument("--markov-submission", default="outputs/markov_label_prior_on_qcount_probe/submission_markov_label_prior.csv")
    parser.add_argument("--prior-oof", default="outputs/label_prior_projection_on_qcount/oof_label_prior_projection.csv")
    parser.add_argument("--prior-submission", default="outputs/label_prior_projection_on_qcount/submission_label_prior_projection.csv")
    parser.add_argument("--sleep-oof", default="outputs/sleep_metric_decoder_on_qcount_min3/oof_sleep_metric_decoder.csv")
    parser.add_argument("--sleep-submission", default="outputs/sleep_metric_decoder_on_qcount_min3/submission_sleep_metric_decoder.csv")
    parser.add_argument("--broad-oof", default="outputs/master_residual_broad_on_w03_min3/oof_master_residual_decoder.csv")
    parser.add_argument("--broad-submission", default="outputs/master_residual_broad_on_w03_min3/submission_master_residual_decoder.csv")
    parser.add_argument("--output-dir", default="outputs/multi_signal_qcount_blend")
    parser.add_argument("--markov-weight", type=float, default=0.15)
    parser.add_argument("--prior-weight", type=float, default=0.20)
    parser.add_argument("--sleep-weight", type=float, default=0.15)
    parser.add_argument("--broad-s4-weight", type=float, default=0.15)
    return parser.parse_args()


if __name__ == "__main__":
    main()
