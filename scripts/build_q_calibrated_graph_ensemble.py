from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss


KEY_COLUMNS = ["subject_id", "sleep_date", "lifelog_date"]
TARGET_COLUMNS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
Q_TARGETS = ["Q1", "Q2", "Q3"]
EPS = 1e-5


def normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in KEY_COLUMNS:
        out[col] = out[col].astype(str)
    return out


def parse_float_list(value: str) -> list[float]:
    return [float(part) for part in value.split(",") if part.strip()]


def parse_str_list(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


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


def prediction_matrix(oof: pd.DataFrame) -> np.ndarray:
    return np.column_stack([oof[f"pred_{target}"].to_numpy(dtype=float) for target in TARGET_COLUMNS])


def submission_matrix(submission: pd.DataFrame) -> np.ndarray:
    return submission[TARGET_COLUMNS].to_numpy(dtype=float)


def logit(values: np.ndarray) -> np.ndarray:
    clipped = np.clip(values, EPS, 1.0 - EPS)
    return np.log(clipped / (1.0 - clipped))


def sigmoid(values: np.ndarray) -> np.ndarray:
    values = np.clip(values, -40.0, 40.0)
    return 1.0 / (1.0 + np.exp(-values))


def solve_intercept(scores: np.ndarray, target_mean: float) -> float:
    target_mean = float(np.clip(target_mean, EPS, 1.0 - EPS))
    lo, hi = -20.0, 20.0
    for _ in range(60):
        mid = (lo + hi) / 2.0
        if sigmoid(scores + mid).mean() < target_mean:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def smoothed_subject_rates(train_part: pd.DataFrame, alpha: float) -> tuple[pd.DataFrame, pd.Series]:
    global_rate = train_part[Q_TARGETS].mean()
    subject_sum = train_part.groupby("subject_id")[Q_TARGETS].sum()
    subject_count = train_part.groupby("subject_id")[Q_TARGETS].count()
    rates = (subject_sum + alpha * global_rate) / (subject_count + alpha)
    return rates, global_rate


def target_group_mean(mode: str, subject: str, target: str, rates: pd.DataFrame, global_rate: pd.Series) -> float:
    subject_rate = float(rates.loc[subject, target]) if subject in rates.index else float(global_rate[target])
    if mode == "half":
        return 0.5
    if mode == "global":
        return float(global_rate[target])
    if mode == "subject":
        return subject_rate
    if mode == "half_subject_50":
        return 0.5 * 0.5 + 0.5 * subject_rate
    raise ValueError(f"Unknown calibration mode: {mode}")


def calibrate_part(
    eval_frame: pd.DataFrame,
    pred: np.ndarray,
    rates: pd.DataFrame,
    global_rate: pd.Series,
    mode: str,
    beta: float,
) -> np.ndarray:
    calibrated = pred.copy()
    frame = eval_frame.reset_index(drop=True)
    for target_i, target in enumerate(Q_TARGETS):
        col_i = TARGET_COLUMNS.index(target)
        raw = logit(pred[:, col_i])
        for subject, group in frame.groupby("subject_id", sort=False):
            idx = group.index.to_numpy()
            scores = raw[idx]
            std = float(scores.std())
            if std > 1e-8:
                scores = (scores - float(scores.mean())) / std
            else:
                scores = scores - float(scores.mean())
            scores = beta * scores
            target_mean = target_group_mean(mode, str(subject), target, rates, global_rate)
            calibrated[idx, col_i] = sigmoid(scores + solve_intercept(scores, target_mean))
    return np.clip(calibrated, EPS, 1.0 - EPS)


def oof_calibration(train: pd.DataFrame, base_pred: np.ndarray, folds: list[tuple[np.ndarray, np.ndarray]], mode: str, beta: float, alpha: float) -> np.ndarray:
    calibrated = base_pred.copy()
    for train_idx, val_idx in folds:
        rates, global_rate = smoothed_subject_rates(train.iloc[train_idx], alpha)
        calibrated[val_idx] = calibrate_part(train.iloc[val_idx], base_pred[val_idx], rates, global_rate, mode, beta)
    return calibrated


def test_calibration(train: pd.DataFrame, sample: pd.DataFrame, base_pred: np.ndarray, mode: str, beta: float, alpha: float) -> np.ndarray:
    rates, global_rate = smoothed_subject_rates(train, alpha)
    return calibrate_part(sample, base_pred, rates, global_rate, mode, beta)


def target_loss(y: pd.DataFrame, pred: np.ndarray, target_i: int, indices: np.ndarray | None = None) -> float:
    if indices is None:
        indices = np.arange(len(y))
    target = TARGET_COLUMNS[target_i]
    return float(log_loss(y.iloc[indices][target].to_numpy(), np.clip(pred[indices, target_i], EPS, 1.0 - EPS), labels=[0, 1]))


def average_loss(y: pd.DataFrame, pred: np.ndarray) -> tuple[float, dict[str, float]]:
    per_target = {target: target_loss(y, pred, i) for i, target in enumerate(TARGET_COLUMNS)}
    return float(np.mean(list(per_target.values()))), per_target


def row_losses(y: pd.DataFrame, pred: np.ndarray) -> np.ndarray:
    y_arr = y[TARGET_COLUMNS].to_numpy(dtype=float)
    pred = np.clip(pred, EPS, 1.0 - EPS)
    return -(y_arr * np.log(pred) + (1.0 - y_arr) * np.log(1.0 - pred)).mean(axis=1)


def bootstrap_improvement(base_loss: np.ndarray, candidate_loss: np.ndarray, seed: int, n_bootstrap: int) -> dict[str, float]:
    diff = base_loss - candidate_loss
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

    y = train[TARGET_COLUMNS]
    folds = make_subject_time_folds(train, args.folds)
    base_oof = np.clip(prediction_matrix(base_oof_df), EPS, 1.0 - EPS)
    base_submission = np.clip(submission_matrix(base_submission_df), EPS, 1.0 - EPS)
    base_avg, base_targets = average_loss(y, base_oof)
    base_fold_scores = [average_loss(y.iloc[val_idx], base_oof[val_idx])[0] for _, val_idx in folds]
    base_row_loss = row_losses(y, base_oof)

    rows = []
    cache: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for mode in parse_str_list(args.modes):
        for beta in parse_float_list(args.betas):
            for alpha in parse_float_list(args.alphas):
                calibrated_oof = oof_calibration(train, base_oof, folds, mode, beta, alpha)
                calibrated_submission = test_calibration(train, sample, base_submission, mode, beta, alpha)
                for weight in parse_float_list(args.blend_weights):
                    candidate_oof = base_oof.copy()
                    candidate_submission = base_submission.copy()
                    for target in Q_TARGETS:
                        target_i = TARGET_COLUMNS.index(target)
                        candidate_oof[:, target_i] = np.clip(
                            weight * calibrated_oof[:, target_i] + (1.0 - weight) * base_oof[:, target_i],
                            EPS,
                            1.0 - EPS,
                        )
                        candidate_submission[:, target_i] = np.clip(
                            weight * calibrated_submission[:, target_i] + (1.0 - weight) * base_submission[:, target_i],
                            EPS,
                            1.0 - EPS,
                        )
                    avg, per_target = average_loss(y, candidate_oof)
                    fold_scores = [average_loss(y.iloc[val_idx], candidate_oof[val_idx])[0] for _, val_idx in folds]
                    fold_improvements = [base_score - score for base_score, score in zip(base_fold_scores, fold_scores)]
                    target_delta = {target: base_targets[target] - per_target[target] for target in TARGET_COLUMNS}
                    boot = bootstrap_improvement(base_row_loss, row_losses(y, candidate_oof), args.seed, args.bootstrap)
                    promoted = (
                        boot["improvement_p025"] > 0.0
                        and sum(delta > 0 for delta in fold_improvements) >= max(args.folds - 1, 1)
                        and min(target_delta.values()) >= -args.max_target_regression
                    )
                    name = f"qcal_w{weight:g}_beta{beta:g}_alpha{alpha:g}_{mode}"
                    rows.append(
                        {
                            "name": name,
                            "avg_log_loss": avg,
                            "delta_vs_base": base_avg - avg,
                            "folds_improved_vs_base": int(sum(delta > 0 for delta in fold_improvements)),
                            "worst_target_delta_vs_base": float(min(target_delta.values())),
                            "promote": bool(promoted),
                            "weight": weight,
                            "beta": beta,
                            "alpha": alpha,
                            "mode": mode,
                            **per_target,
                            **boot,
                        }
                    )
                    cache[name] = (candidate_oof, candidate_submission)

    scores = pd.DataFrame(rows).sort_values(
        ["promote", "avg_log_loss", "improvement_p025"],
        ascending=[False, True, False],
    )
    if scores.empty:
        raise RuntimeError("No Q calibration candidates were generated")
    selected = scores.iloc[0].to_dict()
    selected_oof, selected_submission = cache[str(selected["name"])]

    scores.to_csv(output_dir / "q_calibration_scores.csv", index=False)
    pd.DataFrame([selected]).to_csv(output_dir / "selected_q_calibration.csv", index=False)

    oof_df = train[KEY_COLUMNS + TARGET_COLUMNS].copy()
    for target_i, target in enumerate(TARGET_COLUMNS):
        oof_df[f"pred_{target}"] = selected_oof[:, target_i]
    oof_path = output_dir / "oof_q_calibrated_graph_ensemble.csv"
    oof_df.to_csv(oof_path, index=False)

    submission = pd.read_csv(args.sample_path)
    for target_i, target in enumerate(TARGET_COLUMNS):
        submission[target] = selected_submission[:, target_i]
    submission_path = output_dir / "submission_q_calibrated_graph_ensemble.csv"
    submission.to_csv(submission_path, index=False)

    report = {
        "base_avg_log_loss": base_avg,
        "base_targets": base_targets,
        "selected": selected,
        "top_candidates": scores.head(20).to_dict(orient="records"),
        "args": vars(args),
    }
    (output_dir / "q_calibrated_graph_ensemble_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"base={base_avg:.6f} selected={selected['avg_log_loss']:.6f} promote={selected['promote']}")
    print(scores.head(15).to_string(index=False))
    print(f"saved: {oof_path}")
    print(f"saved: {submission_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Robust Q-count calibration on top of graph diffusion predictions.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--base-oof", default="outputs/graph_diffusion_variant_ensemble/oof_graph_diffusion_variant_ensemble.csv")
    parser.add_argument("--base-submission", default="outputs/graph_diffusion_variant_ensemble/submission_graph_diffusion_variant_ensemble.csv")
    parser.add_argument("--output-dir", default="outputs/q_calibrated_graph_ensemble")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--blend-weights", default="0.05,0.1,0.15,0.2")
    parser.add_argument("--betas", default="0.5,0.75,1,1.5,2")
    parser.add_argument("--alphas", default="1,2,5,10,20,50,100")
    parser.add_argument("--modes", default="half,global,subject,half_subject_50")
    parser.add_argument("--bootstrap", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--max-target-regression", type=float, default=0.003)
    return parser.parse_args()


if __name__ == "__main__":
    main()
