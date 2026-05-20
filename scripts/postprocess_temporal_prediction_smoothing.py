from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss
from scipy.special import expit, logit


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


def make_subject_time_folds(frame: pd.DataFrame, n_folds: int) -> list[np.ndarray]:
    ordered = frame.reset_index(names="_idx").sort_values(["subject_id", "lifelog_date", "sleep_date"])
    val_indices: list[list[int]] = [[] for _ in range(n_folds)]
    for _, group in ordered.groupby("subject_id", sort=False):
        chunks = np.array_split(group["_idx"].to_numpy(), n_folds)
        for fold, chunk in enumerate(chunks):
            val_indices[fold].extend(chunk.tolist())
    return [np.array(sorted(indices), dtype=int) for indices in val_indices]


def smooth_predictions(
    frame: pd.DataFrame,
    pred: np.ndarray,
    bandwidth: float,
    weight: float,
    smoothing_space: str = "prob",
    exclude_self: bool = False,
) -> np.ndarray:
    out = pred.copy()
    dates = pd.to_datetime(frame["lifelog_date"]).map(pd.Timestamp.toordinal).to_numpy(dtype=float)
    if smoothing_space == "prob":
        smooth_input = pred
        inverse = lambda values: values
    elif smoothing_space == "logit":
        smooth_input = logit(np.clip(pred, EPS, 1.0 - EPS))
        inverse = expit
    else:
        raise ValueError(f"Unsupported smoothing_space: {smoothing_space}")

    for _, group in frame.reset_index().groupby("subject_id", sort=False):
        idx = group["index"].to_numpy(dtype=int)
        if len(idx) <= 1:
            continue
        dist = np.abs(dates[idx, None] - dates[idx][None, :])
        kernel = np.exp(-dist / bandwidth)
        if exclude_self:
            np.fill_diagonal(kernel, 0.0)
            zero_rows = kernel.sum(axis=1) <= 0
            if zero_rows.any():
                kernel[zero_rows, zero_rows] = 1.0
        kernel = kernel / kernel.sum(axis=1, keepdims=True)
        local = inverse(kernel @ smooth_input[idx])
        out[idx] = (1.0 - weight) * pred[idx] + weight * local
    return np.clip(out, EPS, 1.0 - EPS)


def target_loss(y: pd.DataFrame, pred: np.ndarray, target_i: int, indices: np.ndarray | None = None) -> float:
    if indices is None:
        indices = np.arange(len(y))
    target = TARGET_COLUMNS[target_i]
    return float(log_loss(y.iloc[indices][target].to_numpy(), np.clip(pred[indices, target_i], EPS, 1.0 - EPS), labels=[0, 1]))


def average_loss(y: pd.DataFrame, pred: np.ndarray) -> tuple[float, dict[str, float]]:
    per_target = {target: target_loss(y, pred, i) for i, target in enumerate(TARGET_COLUMNS)}
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
    folds = make_subject_time_folds(train, args.folds)
    base_avg, base_targets = average_loss(y, base_oof)
    base_fold_target = {
        target: [target_loss(y, base_oof, target_i, fold) for fold in folds]
        for target_i, target in enumerate(TARGET_COLUMNS)
    }

    smoothed_cache: dict[str, np.ndarray] = {}
    rows = []
    best_by_target: dict[str, dict] = {}
    for bandwidth in parse_float_list(args.bandwidths):
        for weight in parse_float_list(args.weights):
            name = f"smooth_{args.smoothing_space}_bw{bandwidth:g}_w{weight:g}"
            if args.exclude_self:
                name += "_noself"
            smoothed = smooth_predictions(train, base_oof, bandwidth, weight, args.smoothing_space, args.exclude_self)
            smoothed_cache[name] = smoothed
            avg, per_target = average_loss(y, smoothed)
            rows.append({"name": name, "bandwidth": bandwidth, "weight": weight, "avg_log_loss": avg, **per_target})
            for target_i, target in enumerate(TARGET_COLUMNS):
                value = per_target[target]
                current = best_by_target.get(target)
                if current is None or value < current["log_loss"]:
                    folds_improved = 0
                    for fold_i, fold in enumerate(folds):
                        cand_fold = target_loss(y, smoothed, target_i, fold)
                        folds_improved += int(base_fold_target[target][fold_i] > cand_fold)
                    best_by_target[target] = {
                        "target": target,
                        "log_loss": value,
                        "base_log_loss": base_targets[target],
                        "delta_vs_base": base_targets[target] - value,
                        "smooth_name": name,
                        "bandwidth": bandwidth,
                        "weight": weight,
                        "folds_improved": folds_improved,
                    }

    final_oof = base_oof.copy()
    selection_rows = []
    for target_i, target in enumerate(TARGET_COLUMNS):
        selected = best_by_target[target]
        used = selected["delta_vs_base"] > 0 and selected["folds_improved"] >= args.min_target_folds_improved
        if used:
            final_oof[:, target_i] = smoothed_cache[selected["smooth_name"]][:, target_i]
        selection_rows.append({**selected, "used": bool(used)})

    combo_frame = pd.concat([train[KEY_COLUMNS], sample[KEY_COLUMNS]], ignore_index=True)
    combo_pred = np.vstack([base_oof, base_submission])
    final_submission = base_submission.copy()
    for target_i, target in enumerate(TARGET_COLUMNS):
        selected = selection_rows[target_i]
        if selected["used"]:
            combo_smoothed = smooth_predictions(
                combo_frame,
                combo_pred,
                float(selected["bandwidth"]),
                float(selected["weight"]),
                args.smoothing_space,
                args.exclude_self,
            )
            final_submission[:, target_i] = combo_smoothed[len(train) :, target_i]

    final_avg, final_targets = average_loss(y, final_oof)
    scores = pd.DataFrame(rows).sort_values("avg_log_loss")
    selection = pd.DataFrame(selection_rows)
    scores.to_csv(output_dir / "smoothing_scores.csv", index=False)
    selection.to_csv(output_dir / "targetwise_smoothing_selection.csv", index=False)

    oof_df = train[KEY_COLUMNS + TARGET_COLUMNS].copy()
    for target_i, target in enumerate(TARGET_COLUMNS):
        oof_df[f"pred_{target}"] = final_oof[:, target_i]
    oof_path = output_dir / "oof_temporal_prediction_smoothing.csv"
    oof_df.to_csv(oof_path, index=False)

    submission = pd.read_csv(args.sample_path)
    for target_i, target in enumerate(TARGET_COLUMNS):
        submission[target] = final_submission[:, target_i]
    submission_path = output_dir / "submission_temporal_prediction_smoothing.csv"
    submission.to_csv(submission_path, index=False)

    report = {
        "base_avg_log_loss": base_avg,
        "base_targets": base_targets,
        "final_avg_log_loss": final_avg,
        "final_targets": final_targets,
        "selection": selection_rows,
        "top_smoothing_candidates": scores.head(20).to_dict(orient="records"),
        "args": vars(args),
    }
    (output_dir / "temporal_prediction_smoothing_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"base={base_avg:.6f} final={final_avg:.6f}")
    print(selection.to_string(index=False))
    print(f"saved: {oof_path}")
    print(f"saved: {submission_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Unsupervised temporal smoothing of prediction probabilities.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--base-oof", default="outputs/prediction_stack_decoder_qcal_wide/oof_prediction_stack_decoder.csv")
    parser.add_argument("--base-submission", default="outputs/prediction_stack_decoder_qcal_wide/submission_prediction_stack_decoder.csv")
    parser.add_argument("--output-dir", default="outputs/temporal_prediction_smoothing")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--bandwidths", default="1,2,3,5,7,10,14,21")
    parser.add_argument("--weights", default="0.05,0.1,0.15,0.2,0.3,0.5,0.7,1.0")
    parser.add_argument("--min-target-folds-improved", type=int, default=4)
    parser.add_argument("--smoothing-space", choices=["prob", "logit"], default="prob")
    parser.add_argument("--exclude-self", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    main()
