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


def parse_float_list(value: str) -> list[float]:
    return [float(part) for part in value.split(",") if part.strip()]


def make_subject_time_folds(frame: pd.DataFrame, n_folds: int) -> list[np.ndarray]:
    ordered = frame.reset_index(names="_idx").sort_values(["subject_id", "lifelog_date", "sleep_date"])
    val_indices: list[list[int]] = [[] for _ in range(n_folds)]
    for _, group in ordered.groupby("subject_id", sort=False):
        chunks = np.array_split(group["_idx"].to_numpy(), n_folds)
        for fold, chunk in enumerate(chunks):
            val_indices[fold].extend(chunk.tolist())
    return [np.array(sorted(indices), dtype=int) for indices in val_indices]


def prediction_matrix(oof: pd.DataFrame) -> np.ndarray:
    pred = np.column_stack([oof[f"pred_{target}"].to_numpy(dtype=float) for target in TARGET_COLUMNS])
    return np.clip(pred, EPS, 1.0 - EPS)


def submission_matrix(submission: pd.DataFrame) -> np.ndarray:
    return np.clip(submission[TARGET_COLUMNS].to_numpy(dtype=float), EPS, 1.0 - EPS)


def score(y: pd.DataFrame, pred: np.ndarray, indices: np.ndarray | None = None) -> tuple[float, dict[str, float]]:
    if indices is None:
        indices = np.arange(len(y))
    per_target = {
        target: float(log_loss(y.iloc[indices][target].to_numpy(), pred[indices, target_i], labels=[0, 1]))
        for target_i, target in enumerate(TARGET_COLUMNS)
    }
    return float(np.mean(list(per_target.values()))), per_target


def row_loss(y: pd.DataFrame, pred: np.ndarray) -> np.ndarray:
    y_arr = y[TARGET_COLUMNS].to_numpy(dtype=float)
    pred = np.clip(pred, EPS, 1.0 - EPS)
    return -(y_arr * np.log(pred) + (1.0 - y_arr) * np.log1p(-pred)).mean(axis=1)


def bootstrap_improvement(base_loss: np.ndarray, cand_loss: np.ndarray, seed: int, n_bootstrap: int) -> dict[str, float]:
    diff = base_loss - cand_loss
    rng = np.random.default_rng(seed)
    boot = np.empty(n_bootstrap, dtype=float)
    for i in range(n_bootstrap):
        idx = rng.integers(0, len(diff), len(diff))
        boot[i] = float(diff[idx].mean())
    return {
        "improvement": float(diff.mean()),
        "improvement_p025": float(np.quantile(boot, 0.025)),
        "improvement_p500": float(np.quantile(boot, 0.500)),
        "improvement_p975": float(np.quantile(boot, 0.975)),
    }


def load_pair(args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    base_oof = normalize_keys(pd.read_csv(args.base_oof))
    cand_oof = normalize_keys(pd.read_csv(args.candidate_oof))
    base_sub = normalize_keys(pd.read_csv(args.base_submission))
    cand_sub = normalize_keys(pd.read_csv(args.candidate_submission))
    for name, frame in [("base_oof", base_oof), ("candidate_oof", cand_oof)]:
        if not frame[KEY_COLUMNS].equals(train[KEY_COLUMNS]):
            raise ValueError(f"{name} keys do not match train keys")
    for name, frame in [("base_submission", base_sub), ("candidate_submission", cand_sub)]:
        if not frame[KEY_COLUMNS].equals(sample[KEY_COLUMNS]):
            raise ValueError(f"{name} keys do not match sample keys")
    return train, sample, prediction_matrix(base_oof), prediction_matrix(cand_oof), submission_matrix(base_sub), submission_matrix(cand_sub)


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    train, sample, base_pred, cand_pred, base_test, cand_test = load_pair(args)
    y = train[TARGET_COLUMNS]
    folds = make_subject_time_folds(train, args.folds)
    base_avg, base_targets = score(y, base_pred)
    base_fold_scores = [score(y, base_pred, fold)[0] for fold in folds]
    base_loss = row_loss(y, base_pred)

    rows = []
    cache: dict[float, tuple[np.ndarray, np.ndarray]] = {}
    for weight in parse_float_list(args.weights):
        pred = np.clip((1.0 - weight) * base_pred + weight * cand_pred, EPS, 1.0 - EPS)
        test = np.clip((1.0 - weight) * base_test + weight * cand_test, EPS, 1.0 - EPS)
        avg, targets = score(y, pred)
        fold_scores = [score(y, pred, fold)[0] for fold in folds]
        fold_deltas = [base_score - cand_score for base_score, cand_score in zip(base_fold_scores, fold_scores)]
        target_deltas = {target: base_targets[target] - targets[target] for target in TARGET_COLUMNS}
        boot = bootstrap_improvement(base_loss, row_loss(y, pred), args.seed, args.bootstrap)
        row = {
            "name": f"{args.name}_w{weight:g}",
            "weight": weight,
            "avg_log_loss": avg,
            "delta_vs_base": base_avg - avg,
            "fold_std": float(np.std(fold_scores)),
            "worst_fold": float(np.max(fold_scores)),
            "improved_folds": int(sum(delta > 0 for delta in fold_deltas)),
            "worst_target_delta": float(min(target_deltas.values())),
            "promote": bool(
                boot["improvement_p025"] > 0.0
                and sum(delta > 0 for delta in fold_deltas) >= max(args.folds - 1, 1)
                and min(target_deltas.values()) >= -args.max_target_regression
            ),
            **targets,
            **boot,
        }
        rows.append(row)
        cache[weight] = (pred, test)

    scores = pd.DataFrame(rows).sort_values(["promote", "avg_log_loss"], ascending=[False, True]).reset_index(drop=True)
    promoted = scores[scores["promote"]]
    if promoted.empty:
        best_row = scores.sort_values("avg_log_loss").iloc[0].to_dict()
    else:
        best_row = promoted.sort_values("avg_log_loss").iloc[0].to_dict()
    best_weight = float(best_row["weight"])
    best_pred, best_test = cache[best_weight]

    scores.to_csv(output_dir / "blend_scores.csv", index=False)

    oof = train[KEY_COLUMNS + TARGET_COLUMNS].copy()
    for target_i, target in enumerate(TARGET_COLUMNS):
        oof[f"pred_{target}"] = best_pred[:, target_i]
    oof_path = output_dir / "oof_candidate_probability_blend.csv"
    oof.to_csv(oof_path, index=False)

    submission = sample.copy()
    for target_i, target in enumerate(TARGET_COLUMNS):
        submission[target] = best_test[:, target_i]
    submission_path = output_dir / "submission_candidate_probability_blend.csv"
    submission.to_csv(submission_path, index=False)

    report = {
        "base_avg_log_loss": base_avg,
        "base_targets": base_targets,
        "best": best_row,
        "args": vars(args),
    }
    (output_dir / "candidate_probability_blend_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(scores.head(12).to_string(index=False))
    print(f"selected weight={best_weight:g} avg={best_row['avg_log_loss']:.6f} promote={best_row['promote']}")
    print(f"saved: {submission_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Blend two OOF/submission probability candidates with robust diagnostics.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--base-oof", required=True)
    parser.add_argument("--base-submission", required=True)
    parser.add_argument("--candidate-oof", required=True)
    parser.add_argument("--candidate-submission", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--name", default="blend")
    parser.add_argument("--weights", default="0.05,0.1,0.15,0.2,0.25,0.3,0.4,0.5,0.65,0.8,1.0")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--bootstrap", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--max-target-regression", type=float, default=0.001)
    return parser.parse_args()


if __name__ == "__main__":
    main()
