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


def make_subject_time_folds(df: pd.DataFrame, n_folds: int) -> list[np.ndarray]:
    ordered = df.reset_index(names="_idx").sort_values(["subject_id", "lifelog_date", "sleep_date"])
    buckets: list[list[int]] = [[] for _ in range(n_folds)]
    for _, group in ordered.groupby("subject_id", sort=False):
        for fold, chunk in enumerate(np.array_split(group["_idx"].to_numpy(), n_folds)):
            buckets[fold].extend(chunk.tolist())
    return [np.array(sorted(bucket), dtype=int) for bucket in buckets]


def oof_matrix(df: pd.DataFrame) -> np.ndarray:
    pred = np.column_stack([df[f"pred_{target}"].to_numpy(dtype=float) for target in TARGET_COLUMNS])
    return np.clip(pred, EPS, 1.0 - EPS)


def submission_matrix(df: pd.DataFrame) -> np.ndarray:
    return np.clip(df[TARGET_COLUMNS].to_numpy(dtype=float), EPS, 1.0 - EPS)


def score(y: pd.DataFrame, pred: np.ndarray, idx: np.ndarray | None = None) -> tuple[float, dict[str, float]]:
    if idx is None:
        idx = np.arange(len(y))
    per_target = {
        target: float(log_loss(y.iloc[idx][target].to_numpy(), pred[idx, i], labels=[0, 1]))
        for i, target in enumerate(TARGET_COLUMNS)
    }
    return float(np.mean(list(per_target.values()))), per_target


def row_loss(y: pd.DataFrame, pred: np.ndarray) -> np.ndarray:
    y_arr = y[TARGET_COLUMNS].to_numpy(dtype=float)
    pred = np.clip(pred, EPS, 1.0 - EPS)
    return -(y_arr * np.log(pred) + (1.0 - y_arr) * np.log(1.0 - pred)).mean(axis=1)


def bootstrap_ci(base: np.ndarray, candidate: np.ndarray, seed: int, n_bootstrap: int) -> list[float]:
    diff = base - candidate
    rng = np.random.default_rng(seed)
    values = np.empty(n_bootstrap, dtype=float)
    for i in range(n_bootstrap):
        idx = rng.integers(0, len(diff), len(diff))
        values[i] = float(diff[idx].mean())
    return [float(v) for v in np.quantile(values, [0.025, 0.5, 0.975])]


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    base_oof = normalize_keys(pd.read_csv(args.base_oof))
    master_oof = normalize_keys(pd.read_csv(args.master_oof))
    q_oof = normalize_keys(pd.read_csv(args.q_oof))
    base_sub = normalize_keys(pd.read_csv(args.base_submission))
    master_sub = normalize_keys(pd.read_csv(args.master_submission))
    q_sub = normalize_keys(pd.read_csv(args.q_submission))

    for name, frame in [("base_oof", base_oof), ("master_oof", master_oof), ("q_oof", q_oof)]:
        if not frame[KEY_COLUMNS].equals(train[KEY_COLUMNS]):
            raise ValueError(f"{name} keys do not match train keys")
    for name, frame in [("base_submission", base_sub), ("master_submission", master_sub), ("q_submission", q_sub)]:
        if not frame[KEY_COLUMNS].equals(sample[KEY_COLUMNS]):
            raise ValueError(f"{name} keys do not match sample keys")

    base_pred = oof_matrix(base_oof)
    master_pred = oof_matrix(master_oof)
    q_pred = oof_matrix(q_oof)
    base_test = submission_matrix(base_sub)
    master_test = submission_matrix(master_sub)
    q_test = submission_matrix(q_sub)

    # Use only target-wise improvements that were stable in the robust diagnostics.
    hybrid_pred = base_pred.copy()
    hybrid_test = base_test.copy()
    source = {}
    for target in ["Q1", "Q2"]:
        i = TARGET_COLUMNS.index(target)
        hybrid_pred[:, i] = q_pred[:, i]
        hybrid_test[:, i] = q_test[:, i]
        source[target] = "q_ranker_tuned"
    for target in ["Q3", "S1", "S4"]:
        i = TARGET_COLUMNS.index(target)
        hybrid_pred[:, i] = master_pred[:, i]
        hybrid_test[:, i] = master_test[:, i]
        source[target] = "master_temporal"
    for target in ["S2", "S3"]:
        source[target] = "latent_temporal"

    rows = []
    folds = make_subject_time_folds(train, args.folds)
    y = train[TARGET_COLUMNS]
    base_avg, base_targets = score(y, base_pred)
    base_loss = row_loss(y, base_pred)

    best = None
    for weight in [float(v) for v in args.weights.split(",") if v]:
        pred = np.clip(weight * hybrid_pred + (1.0 - weight) * base_pred, EPS, 1.0 - EPS)
        test = np.clip(weight * hybrid_test + (1.0 - weight) * base_test, EPS, 1.0 - EPS)
        avg, targets = score(y, pred)
        fold_scores = [score(y, pred, fold)[0] for fold in folds]
        base_fold_scores = [score(y, base_pred, fold)[0] for fold in folds]
        fold_improvements = [b - s for b, s in zip(base_fold_scores, fold_scores)]
        ci = bootstrap_ci(base_loss, row_loss(y, pred), args.seed, args.bootstrap)
        target_deltas = {target: base_targets[target] - targets[target] for target in TARGET_COLUMNS}
        row = {
            "name": f"robust_safe_w{weight:g}",
            "hybrid_weight": weight,
            "avg_log_loss": avg,
            "improvement_vs_base": base_avg - avg,
            "bootstrap_p025": ci[0],
            "bootstrap_p500": ci[1],
            "bootstrap_p975": ci[2],
            "fold_std": float(np.std(fold_scores)),
            "improved_folds": int(sum(delta > 0 for delta in fold_improvements)),
            "worst_target_delta": float(min(target_deltas.values())),
            **targets,
        }
        rows.append(row)
        passes = ci[0] > 0 and row["improved_folds"] == args.folds and row["worst_target_delta"] >= -args.max_target_regression
        if passes and (best is None or row["avg_log_loss"] < best["row"]["avg_log_loss"]):
            best = {"row": row, "pred": pred, "test": test}

    score_df = pd.DataFrame(rows).sort_values("avg_log_loss").reset_index(drop=True)
    score_df.to_csv(output_dir / "robust_safe_ensemble_scores.csv", index=False)
    if best is None:
        best_weight = float(score_df.iloc[0]["hybrid_weight"])
        pred = np.clip(best_weight * hybrid_pred + (1.0 - best_weight) * base_pred, EPS, 1.0 - EPS)
        test = np.clip(best_weight * hybrid_test + (1.0 - best_weight) * base_test, EPS, 1.0 - EPS)
        best = {"row": score_df.iloc[0].to_dict(), "pred": pred, "test": test}

    oof_out = train[KEY_COLUMNS + TARGET_COLUMNS].copy()
    for i, target in enumerate(TARGET_COLUMNS):
        oof_out[f"pred_{target}"] = best["pred"][:, i]
    oof_out.to_csv(output_dir / "oof_robust_safe_ensemble.csv", index=False)

    submission = sample.copy()
    for i, target in enumerate(TARGET_COLUMNS):
        submission[target] = best["test"][:, i]
    submission.to_csv(output_dir / "submission_robust_safe_ensemble.csv", index=False)

    report = {
        "base_score": {"avg_log_loss": base_avg, **base_targets},
        "best": best["row"],
        "target_sources": source,
        "args": vars(args),
    }
    (output_dir / "robust_safe_ensemble_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(pd.DataFrame([best["row"]]).to_string(index=False))
    print(f"saved submission: {output_dir / 'submission_robust_safe_ensemble.csv'}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a conservative robust-safe ensemble.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--base-oof", default="outputs/latent_decoder/oof_targetwise_temporal_blend.csv")
    parser.add_argument("--base-submission", default="outputs/latent_decoder/submission_latent_decoder_targetwise_temporal.csv")
    parser.add_argument("--master-oof", default="outputs/master_aggressive_decoder_fast/oof_temporal_master_oof_blend.csv")
    parser.add_argument("--master-submission", default="outputs/master_aggressive_decoder_fast/submission_temporal_master_oof_blend.csv")
    parser.add_argument("--q-oof", default="outputs/q_ranker_decoder_tuned/oof_q_ranker_with_baseline_s.csv")
    parser.add_argument("--q-submission", default="outputs/q_ranker_decoder_tuned/submission_q_ranker_with_baseline_s.csv")
    parser.add_argument("--output-dir", default="outputs/robust_safe_ensemble")
    parser.add_argument("--weights", default="0.25,0.35,0.5,0.65,0.8,1.0")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--bootstrap", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--max-target-regression", type=float, default=0.003)
    return parser.parse_args()


if __name__ == "__main__":
    main()
