from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import expit, logsumexp
from sklearn.metrics import log_loss


KEY_COLUMNS = ["subject_id", "sleep_date", "lifelog_date"]
TARGET_COLUMNS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
EPS = 1e-5


def normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in KEY_COLUMNS:
        out[col] = out[col].astype(str)
    return out


def parse_float_list(value: str) -> list[float]:
    return [float(part) for part in value.split(",") if part.strip()]


def prediction_matrix(oof: pd.DataFrame) -> np.ndarray:
    return np.column_stack([oof[f"pred_{target}"].to_numpy(dtype=float) for target in TARGET_COLUMNS])


def submission_matrix(submission: pd.DataFrame) -> np.ndarray:
    return submission[TARGET_COLUMNS].to_numpy(dtype=float)


def make_subject_time_folds(frame: pd.DataFrame, n_folds: int) -> list[tuple[np.ndarray, np.ndarray]]:
    ordered = frame.reset_index(names="_idx").sort_values(["subject_id", "lifelog_date", "sleep_date"])
    val_indices: list[list[int]] = [[] for _ in range(n_folds)]
    for _, group in ordered.groupby("subject_id", sort=False):
        chunks = np.array_split(group["_idx"].to_numpy(), n_folds)
        for fold, chunk in enumerate(chunks):
            val_indices[fold].extend(chunk.tolist())
    all_idx = np.arange(len(frame))
    return [
        (np.setdiff1d(all_idx, np.array(sorted(indices), dtype=int)), np.array(sorted(indices), dtype=int))
        for indices in val_indices
    ]


def all_label_patterns() -> np.ndarray:
    values = np.arange(2 ** len(TARGET_COLUMNS), dtype=np.uint16)
    bits = ((values[:, None] >> np.arange(len(TARGET_COLUMNS))) & 1).astype(float)
    return bits


def pattern_indices(labels: np.ndarray) -> np.ndarray:
    powers = (2 ** np.arange(labels.shape[1])).astype(int)
    return labels.astype(int) @ powers


def estimate_pattern_prior(labels: np.ndarray, alpha: float, patterns: np.ndarray) -> np.ndarray:
    counts = np.bincount(pattern_indices(labels), minlength=len(patterns)).astype(float)
    prior = counts + alpha
    return prior / prior.sum()


def safe_logit(values: np.ndarray) -> np.ndarray:
    values = np.clip(values, EPS, 1.0 - EPS)
    return np.log(values / (1.0 - values))


def project_with_prior(pred: np.ndarray, prior: np.ndarray, patterns: np.ndarray, gamma: float) -> np.ndarray:
    logits = safe_logit(pred)
    scores = logits @ patterns.T + gamma * np.log(np.clip(prior, EPS, 1.0))
    posterior = np.exp(scores - logsumexp(scores, axis=1, keepdims=True))
    return np.clip(posterior @ patterns, EPS, 1.0 - EPS)


def oof_project(train: pd.DataFrame, base_oof: np.ndarray, folds: list[tuple[np.ndarray, np.ndarray]], alpha: float, gamma: float, patterns: np.ndarray) -> np.ndarray:
    labels = train[TARGET_COLUMNS].to_numpy(dtype=int)
    projected = np.zeros_like(base_oof, dtype=float)
    for train_idx, val_idx in folds:
        prior = estimate_pattern_prior(labels[train_idx], alpha, patterns)
        projected[val_idx] = project_with_prior(base_oof[val_idx], prior, patterns, gamma)
    return np.clip(projected, EPS, 1.0 - EPS)


def target_loss(y: pd.DataFrame, pred: np.ndarray, target_i: int, indices: np.ndarray | None = None) -> float:
    if indices is None:
        indices = np.arange(len(y))
    target = TARGET_COLUMNS[target_i]
    return float(log_loss(y.iloc[indices][target].to_numpy(), np.clip(pred[indices, target_i], EPS, 1.0 - EPS), labels=[0, 1]))


def average_loss(y: pd.DataFrame, pred: np.ndarray) -> tuple[float, dict[str, float]]:
    per_target = {target: target_loss(y, pred, target_i) for target_i, target in enumerate(TARGET_COLUMNS)}
    return float(np.mean(list(per_target.values()))), per_target


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    base_oof_df = normalize_keys(pd.read_csv(args.base_oof))
    base_submission_df = normalize_keys(pd.read_csv(args.base_submission))
    if not base_oof_df[KEY_COLUMNS].equals(train[KEY_COLUMNS]):
        raise ValueError("Base OOF keys do not match train keys")
    if not base_submission_df[KEY_COLUMNS].equals(sample[KEY_COLUMNS]):
        raise ValueError("Base submission keys do not match sample keys")

    base_oof = np.clip(prediction_matrix(base_oof_df), EPS, 1.0 - EPS)
    base_submission = np.clip(submission_matrix(base_submission_df), EPS, 1.0 - EPS)
    y = train[TARGET_COLUMNS]
    labels = y.to_numpy(dtype=int)
    folds = make_subject_time_folds(train, args.folds)
    patterns = all_label_patterns()

    base_avg, base_targets = average_loss(y, base_oof)
    base_fold_target = {
        target: [target_loss(y, base_oof, target_i, val_idx) for _, val_idx in folds]
        for target_i, target in enumerate(TARGET_COLUMNS)
    }

    cache: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    rows = []
    best_by_target: dict[str, dict] = {}
    for alpha in parse_float_list(args.alphas):
        for gamma in parse_float_list(args.gammas):
            projected_oof = oof_project(train, base_oof, folds, alpha, gamma, patterns)
            full_prior = estimate_pattern_prior(labels, alpha, patterns)
            projected_submission = project_with_prior(base_submission, full_prior, patterns, gamma)
            for weight in parse_float_list(args.weights):
                name = f"prior_a{alpha:g}_g{gamma:g}_w{weight:g}"
                blended_oof = np.clip(weight * projected_oof + (1.0 - weight) * base_oof, EPS, 1.0 - EPS)
                blended_submission = np.clip(weight * projected_submission + (1.0 - weight) * base_submission, EPS, 1.0 - EPS)
                cache[name] = (blended_oof, blended_submission)
                avg, per_target = average_loss(y, blended_oof)
                rows.append({"name": name, "alpha": alpha, "gamma": gamma, "weight": weight, "avg_log_loss": avg, **per_target})
                for target_i, target in enumerate(TARGET_COLUMNS):
                    value = per_target[target]
                    current = best_by_target.get(target)
                    if current is None or value < current["log_loss"]:
                        folds_improved = 0
                        for fold_i, (_, val_idx) in enumerate(folds):
                            cand_fold = target_loss(y, blended_oof, target_i, val_idx)
                            folds_improved += int(cand_fold < base_fold_target[target][fold_i])
                        best_by_target[target] = {
                            "target": target,
                            "log_loss": value,
                            "base_log_loss": base_targets[target],
                            "delta_vs_base": base_targets[target] - value,
                            "candidate": name,
                            "alpha": alpha,
                            "gamma": gamma,
                            "weight": weight,
                            "folds_improved": folds_improved,
                        }

    final_oof = base_oof.copy()
    final_submission = base_submission.copy()
    selection_rows = []
    for target_i, target in enumerate(TARGET_COLUMNS):
        selected = best_by_target[target]
        used = selected["delta_vs_base"] >= args.min_delta and selected["folds_improved"] >= args.min_target_folds_improved
        if used:
            final_oof[:, target_i] = cache[selected["candidate"]][0][:, target_i]
            final_submission[:, target_i] = cache[selected["candidate"]][1][:, target_i]
        selection_rows.append({**selected, "used": bool(used)})

    final_avg, final_targets = average_loss(y, final_oof)
    scores = pd.DataFrame(rows).sort_values("avg_log_loss")
    selection = pd.DataFrame(selection_rows)
    scores.to_csv(output_dir / "candidate_scores.csv", index=False)
    selection.to_csv(output_dir / "targetwise_prior_projection_selection.csv", index=False)

    oof_df = train[KEY_COLUMNS + TARGET_COLUMNS].copy()
    for target_i, target in enumerate(TARGET_COLUMNS):
        oof_df[f"pred_{target}"] = final_oof[:, target_i]
    oof_path = output_dir / "oof_label_prior_projection.csv"
    oof_df.to_csv(oof_path, index=False)

    submission = pd.read_csv(args.sample_path)
    for target_i, target in enumerate(TARGET_COLUMNS):
        submission[target] = final_submission[:, target_i]
    submission_path = output_dir / "submission_label_prior_projection.csv"
    submission.to_csv(submission_path, index=False)

    report = {
        "base_avg_log_loss": base_avg,
        "base_targets": base_targets,
        "final_avg_log_loss": final_avg,
        "final_targets": final_targets,
        "selection": selection_rows,
        "top_candidates": scores.head(20).to_dict(orient="records"),
        "args": vars(args),
    }
    (output_dir / "label_prior_projection_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"base={base_avg:.6f} final={final_avg:.6f}")
    print(selection.to_string(index=False))
    print(f"saved: {oof_path}")
    print(f"saved: {submission_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fold-safe projection of multi-target probabilities onto empirical label-pattern priors.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--base-oof", default="outputs/temporal_prediction_smoothing_stack_wide/oof_temporal_prediction_smoothing.csv")
    parser.add_argument("--base-submission", default="outputs/temporal_prediction_smoothing_stack_wide/submission_temporal_prediction_smoothing.csv")
    parser.add_argument("--output-dir", default="outputs/label_prior_projection")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--alphas", default="0.5,1,2,5")
    parser.add_argument("--gammas", default="0.05,0.1,0.2,0.3,0.5,0.7,1.0")
    parser.add_argument("--weights", default="0.05,0.1,0.15,0.2,0.3,0.5")
    parser.add_argument("--min-target-folds-improved", type=int, default=4)
    parser.add_argument("--min-delta", type=float, default=0.0001)
    return parser.parse_args()


if __name__ == "__main__":
    main()
