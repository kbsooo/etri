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


def make_subject_time_folds(frame: pd.DataFrame, n_folds: int) -> list[tuple[np.ndarray, np.ndarray]]:
    ordered = frame.reset_index(names="_idx").sort_values(["subject_id", "lifelog_date", "sleep_date"])
    val_indices: list[list[int]] = [[] for _ in range(n_folds)]
    for _, group in ordered.groupby("subject_id", sort=False):
        chunks = np.array_split(group["_idx"].to_numpy(), n_folds)
        for fold, chunk in enumerate(chunks):
            val_indices[fold].extend(chunk.tolist())
    all_idx = np.arange(len(frame), dtype=int)
    return [
        (np.setdiff1d(all_idx, np.array(sorted(indices), dtype=int)), np.array(sorted(indices), dtype=int))
        for indices in val_indices
    ]


def prediction_matrix(oof: pd.DataFrame) -> np.ndarray:
    pred = np.column_stack([oof[f"pred_{target}"].to_numpy(dtype=float) for target in TARGET_COLUMNS])
    return np.clip(pred, EPS, 1.0 - EPS)


def submission_matrix(submission: pd.DataFrame) -> np.ndarray:
    return np.clip(submission[TARGET_COLUMNS].to_numpy(dtype=float), EPS, 1.0 - EPS)


def safe_logit(values: np.ndarray) -> np.ndarray:
    values = np.clip(values, EPS, 1.0 - EPS)
    return np.log(values / (1.0 - values))


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(values, -40.0, 40.0)))


def solve_intercept(scores: np.ndarray, target_mean: float) -> float:
    target_mean = float(np.clip(target_mean, EPS, 1.0 - EPS))
    lo, hi = -25.0, 25.0
    for _ in range(80):
        mid = (lo + hi) / 2.0
        if float(sigmoid(scores + mid).mean()) < target_mean:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def expected_eval_rate(
    observed_train: pd.DataFrame,
    subject: str,
    target: str,
    eval_count: int,
    total_positive_rate: float,
) -> float:
    subject_train = observed_train[observed_train["subject_id"].eq(subject)]
    if eval_count <= 0:
        return float(subject_train[target].mean()) if len(subject_train) else total_positive_rate
    train_count = int(len(subject_train))
    train_pos = float(subject_train[target].sum()) if train_count else 0.0
    desired_total_pos = total_positive_rate * float(train_count + eval_count)
    desired_eval_pos = desired_total_pos - train_pos
    return float(np.clip(desired_eval_pos / float(eval_count), EPS, 1.0 - EPS))


def calibrate_eval_block(
    eval_frame: pd.DataFrame,
    pred: np.ndarray,
    observed_train: pd.DataFrame,
    total_positive_rate: float,
    count_strength: float,
    beta: float,
) -> np.ndarray:
    out = pred.copy()
    eval_reset = eval_frame.reset_index(drop=True)
    for target in Q_TARGETS:
        target_i = TARGET_COLUMNS.index(target)
        raw = safe_logit(pred[:, target_i])
        for subject, group in eval_reset.reset_index().groupby("subject_id", sort=False):
            idx = group["index"].to_numpy(dtype=int)
            scores = raw[idx]
            std = float(np.nanstd(scores))
            if np.isfinite(std) and std > 1e-8:
                scores = (scores - float(np.nanmean(scores))) / std
            else:
                scores = scores - float(np.nanmean(scores))
            scores = beta * scores
            base_mean = float(pred[idx, target_i].mean())
            count_mean = expected_eval_rate(observed_train, str(subject), target, len(idx), total_positive_rate)
            target_mean = (1.0 - count_strength) * base_mean + count_strength * count_mean
            out[idx, target_i] = sigmoid(scores + solve_intercept(scores, target_mean))
    return np.clip(out, EPS, 1.0 - EPS)


def calibrate_oof(
    train: pd.DataFrame,
    base_oof: np.ndarray,
    folds: list[tuple[np.ndarray, np.ndarray]],
    total_positive_rate: float,
    count_strength: float,
    beta: float,
) -> np.ndarray:
    out = base_oof.copy()
    for train_idx, val_idx in folds:
        out[val_idx] = calibrate_eval_block(
            train.iloc[val_idx],
            base_oof[val_idx],
            train.iloc[train_idx],
            total_positive_rate,
            count_strength,
            beta,
        )
    return out


def calibrate_submission(
    train: pd.DataFrame,
    sample: pd.DataFrame,
    base_submission: np.ndarray,
    total_positive_rate: float,
    count_strength: float,
    beta: float,
) -> np.ndarray:
    return calibrate_eval_block(sample, base_submission, train, total_positive_rate, count_strength, beta)


def target_loss(y: pd.DataFrame, pred: np.ndarray, target_i: int, indices: np.ndarray | None = None) -> float:
    if indices is None:
        indices = np.arange(len(y), dtype=int)
    target = TARGET_COLUMNS[target_i]
    return float(log_loss(y.iloc[indices][target].to_numpy(), np.clip(pred[indices, target_i], EPS, 1.0 - EPS), labels=[0, 1]))


def average_loss(y: pd.DataFrame, pred: np.ndarray) -> tuple[float, dict[str, float]]:
    per_target = {target: target_loss(y, pred, target_i) for target_i, target in enumerate(TARGET_COLUMNS)}
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


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    base_oof_df = normalize_keys(pd.read_csv(args.base_oof))
    base_sub_df = normalize_keys(pd.read_csv(args.base_submission))
    if not base_oof_df[KEY_COLUMNS].equals(train[KEY_COLUMNS]):
        raise ValueError("Base OOF keys do not match train keys")
    if not base_sub_df[KEY_COLUMNS].equals(sample[KEY_COLUMNS]):
        raise ValueError("Base submission keys do not match sample keys")

    folds = make_subject_time_folds(train, args.folds)
    y = train[TARGET_COLUMNS]
    base_oof = prediction_matrix(base_oof_df)
    base_sub = submission_matrix(base_sub_df)
    base_avg, base_targets = average_loss(y, base_oof)
    base_fold_target = {
        target: [target_loss(y, base_oof, target_i, val_idx) for _, val_idx in folds]
        for target_i, target in enumerate(TARGET_COLUMNS)
    }

    rows = []
    cache: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for total_positive_rate in parse_float_list(args.total_positive_rates):
        for count_strength in parse_float_list(args.count_strengths):
            for beta in parse_float_list(args.betas):
                cal_oof = calibrate_oof(train, base_oof, folds, total_positive_rate, count_strength, beta)
                cal_sub = calibrate_submission(train, sample, base_sub, total_positive_rate, count_strength, beta)
                for blend_weight in parse_float_list(args.blend_weights):
                    name = f"qcount_r{total_positive_rate:g}_s{count_strength:g}_b{beta:g}_w{blend_weight:g}"
                    pred = base_oof.copy()
                    sub = base_sub.copy()
                    for target in Q_TARGETS:
                        target_i = TARGET_COLUMNS.index(target)
                        pred[:, target_i] = np.clip(
                            (1.0 - blend_weight) * base_oof[:, target_i] + blend_weight * cal_oof[:, target_i],
                            EPS,
                            1.0 - EPS,
                        )
                        sub[:, target_i] = np.clip(
                            (1.0 - blend_weight) * base_sub[:, target_i] + blend_weight * cal_sub[:, target_i],
                            EPS,
                            1.0 - EPS,
                        )
                    cache[name] = (pred, sub)
                    avg, per_target = average_loss(y, pred)
                    row = {
                        "name": name,
                        "avg_log_loss": avg,
                        "total_positive_rate": total_positive_rate,
                        "count_strength": count_strength,
                        "beta": beta,
                        "blend_weight": blend_weight,
                        **per_target,
                    }
                    rows.append(row)

    scores = pd.DataFrame(rows).sort_values("avg_log_loss").reset_index(drop=True)
    best_by_target: dict[str, dict] = {}
    for row in scores.to_dict(orient="records"):
        pred, _ = cache[str(row["name"])]
        for target_i, target in enumerate(TARGET_COLUMNS):
            value = target_loss(y, pred, target_i)
            current = best_by_target.get(target)
            if current is not None and value >= current["log_loss"]:
                continue
            fold_scores = [target_loss(y, pred, target_i, val_idx) for _, val_idx in folds]
            folds_improved = int(sum(base_fold > cand_fold for base_fold, cand_fold in zip(base_fold_target[target], fold_scores)))
            best_by_target[target] = {
                "target": target,
                "log_loss": value,
                "base_log_loss": base_targets[target],
                "delta_vs_base": base_targets[target] - value,
                "candidate": row["name"],
                "total_positive_rate": row["total_positive_rate"],
                "count_strength": row["count_strength"],
                "beta": row["beta"],
                "blend_weight": row["blend_weight"],
                "folds_improved": folds_improved,
            }

    final_oof = base_oof.copy()
    final_sub = base_sub.copy()
    selection_rows = []
    for target_i, target in enumerate(TARGET_COLUMNS):
        selected = best_by_target[target]
        used = (
            target in Q_TARGETS
            and selected["delta_vs_base"] >= args.min_delta
            and selected["folds_improved"] >= args.min_target_folds_improved
        )
        if used:
            final_oof[:, target_i] = cache[selected["candidate"]][0][:, target_i]
            final_sub[:, target_i] = cache[selected["candidate"]][1][:, target_i]
        selection_rows.append({**selected, "used": bool(used)})

    final_avg, final_targets = average_loss(y, final_oof)
    scores.to_csv(output_dir / "q_count_scores.csv", index=False)
    selection = pd.DataFrame(selection_rows)
    selection.to_csv(output_dir / "targetwise_q_count_selection.csv", index=False)

    oof_df = train[KEY_COLUMNS + TARGET_COLUMNS].copy()
    for target_i, target in enumerate(TARGET_COLUMNS):
        oof_df[f"pred_{target}"] = final_oof[:, target_i]
    oof_path = output_dir / "oof_transductive_q_count.csv"
    oof_df.to_csv(oof_path, index=False)

    submission = pd.read_csv(args.sample_path)
    for target_i, target in enumerate(TARGET_COLUMNS):
        submission[target] = final_sub[:, target_i]
    submission_path = output_dir / "submission_transductive_q_count.csv"
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
    (output_dir / "transductive_q_count_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# Transductive Q Count Report",
        "",
        f"- Base avg logloss: `{base_avg:.6f}`",
        f"- Final avg logloss: `{final_avg:.6f}`",
        "- OOF uses only fold-train labels to infer the held-out subject block mean.",
        "",
        "## Selection",
        "",
        dataframe_to_markdown(selection),
        "",
        "## Top Candidates",
        "",
        dataframe_to_markdown(scores.head(12)),
        "",
    ]
    (output_dir / "transductive_q_count_report.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"base={base_avg:.6f} final={final_avg:.6f}")
    print(selection.to_string(index=False))
    print(f"saved: {submission_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fold-safe Q-count calibration using the questionnaire whole-period mean constraint.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--base-oof", required=True)
    parser.add_argument("--base-submission", required=True)
    parser.add_argument("--output-dir", default="outputs/transductive_q_count")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--total-positive-rates", default="0.45,0.5,0.55")
    parser.add_argument("--count-strengths", default="0.1,0.2,0.35,0.5,0.75,1.0")
    parser.add_argument("--betas", default="0.5,0.75,1.0,1.25,1.5")
    parser.add_argument("--blend-weights", default="0.05,0.1,0.15,0.2,0.3,0.5")
    parser.add_argument("--min-target-folds-improved", type=int, default=4)
    parser.add_argument("--min-delta", type=float, default=0.00005)
    return parser.parse_args()


if __name__ == "__main__":
    main()
