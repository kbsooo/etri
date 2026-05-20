from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import expit, logit
from sklearn.metrics import log_loss


KEY_COLUMNS = ["subject_id", "sleep_date", "lifelog_date"]
TARGET_COLUMNS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
EPS = 1e-5


@dataclass(frozen=True)
class CandidateSpec:
    name: str
    bandwidth: float | None
    weight: float
    smoothing_space: str


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


def smooth_predictions(frame: pd.DataFrame, pred: np.ndarray, bandwidth: float, weight: float, smoothing_space: str) -> np.ndarray:
    out = pred.copy()
    dates = pd.to_datetime(frame["lifelog_date"]).map(pd.Timestamp.toordinal).to_numpy(dtype=float)
    if smoothing_space == "prob":
        smooth_input = pred
        inverse = lambda values: values
    elif smoothing_space == "logit":
        smooth_input = logit(np.clip(pred, EPS, 1.0 - EPS))
        inverse = expit
    else:
        raise ValueError(f"Unsupported smoothing space: {smoothing_space}")

    for _, group in frame.reset_index().groupby("subject_id", sort=False):
        idx = group["index"].to_numpy(dtype=int)
        if len(idx) <= 1:
            continue
        dist = np.abs(dates[idx, None] - dates[idx][None, :])
        kernel = np.exp(-dist / bandwidth)
        kernel = kernel / kernel.sum(axis=1, keepdims=True)
        local = inverse(kernel @ smooth_input[idx])
        out[idx] = (1.0 - weight) * pred[idx] + weight * local
    return np.clip(out, EPS, 1.0 - EPS)


def target_loss(y: pd.DataFrame, pred: np.ndarray, target_i: int, indices: np.ndarray) -> float:
    if len(indices) == 0:
        return float("inf")
    target = TARGET_COLUMNS[target_i]
    return float(log_loss(y.iloc[indices][target].to_numpy(), np.clip(pred[indices, target_i], EPS, 1.0 - EPS), labels=[0, 1]))


def average_loss(y: pd.DataFrame, pred: np.ndarray) -> tuple[float, dict[str, float]]:
    per_target = {
        target: target_loss(y, pred, target_i, np.arange(len(y)))
        for target_i, target in enumerate(TARGET_COLUMNS)
    }
    return float(np.mean(list(per_target.values()))), per_target


def build_candidate_specs(args: argparse.Namespace) -> list[CandidateSpec]:
    specs = [CandidateSpec("base", None, 0.0, "base")]
    for smoothing_space in args.smoothing_spaces.split(","):
        smoothing_space = smoothing_space.strip()
        if not smoothing_space:
            continue
        for bandwidth in parse_float_list(args.bandwidths):
            for weight in parse_float_list(args.weights):
                specs.append(
                    CandidateSpec(
                        f"{smoothing_space}_bw{bandwidth:g}_w{weight:g}",
                        bandwidth,
                        weight,
                        smoothing_space,
                    )
                )
    return specs


def select_candidate(
    y: pd.DataFrame,
    candidate_pred: dict[str, np.ndarray],
    target_i: int,
    indices: np.ndarray,
    min_delta: float,
) -> tuple[str, float, float]:
    base_loss = target_loss(y, candidate_pred["base"], target_i, indices)
    best_name = "base"
    best_loss = base_loss
    for name, pred in candidate_pred.items():
        loss = target_loss(y, pred, target_i, indices)
        if loss < best_loss:
            best_name = name
            best_loss = loss
    if best_name != "base" and base_loss - best_loss >= min_delta:
        return best_name, best_loss, base_loss
    return "base", base_loss, base_loss


def selection_pool_for_fold(folds: list[np.ndarray], fold_i: int, mode: str, n_rows: int) -> np.ndarray:
    if mode == "complement":
        mask = np.ones(n_rows, dtype=bool)
        mask[folds[fold_i]] = False
        return np.flatnonzero(mask)
    if mode == "prefix":
        if fold_i == 0:
            return np.array([], dtype=int)
        return np.concatenate(folds[:fold_i])
    raise ValueError(f"Unsupported selection mode: {mode}")


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
    subjects = train["subject_id"].to_numpy()
    specs = build_candidate_specs(args)

    candidate_oof: dict[str, np.ndarray] = {}
    for spec in specs:
        if spec.name == "base":
            candidate_oof[spec.name] = base_oof
        else:
            candidate_oof[spec.name] = smooth_predictions(train, base_oof, float(spec.bandwidth), spec.weight, spec.smoothing_space)

    final_oof = base_oof.copy()
    selection_rows = []
    all_idx = np.arange(len(train))
    for fold_i, val_idx in enumerate(folds):
        pool_idx = selection_pool_for_fold(folds, fold_i, args.selection_mode, len(train))
        if len(pool_idx) < args.min_global_rows:
            pool_idx = all_idx[~np.isin(all_idx, val_idx)] if args.selection_mode == "prefix" else pool_idx
        for target_i, target in enumerate(TARGET_COLUMNS):
            global_name, global_loss, global_base_loss = select_candidate(y, candidate_oof, target_i, pool_idx, args.min_delta)
            for subject in np.unique(subjects[val_idx]):
                val_subject_idx = val_idx[subjects[val_idx] == subject]
                subject_pool = pool_idx[subjects[pool_idx] == subject]
                selected_name = global_name
                selected_scope = "global"
                selected_loss = global_loss
                selected_base_loss = global_base_loss
                if len(subject_pool) >= args.min_subject_rows:
                    subject_name, subject_loss, subject_base_loss = select_candidate(
                        y,
                        candidate_oof,
                        target_i,
                        subject_pool,
                        args.min_delta,
                    )
                    if subject_name != "base":
                        selected_name = subject_name
                        selected_scope = "subject"
                        selected_loss = subject_loss
                        selected_base_loss = subject_base_loss
                final_oof[val_subject_idx, target_i] = candidate_oof[selected_name][val_subject_idx, target_i]
                selection_rows.append(
                    {
                        "fold": fold_i,
                        "target": target,
                        "subject_id": subject,
                        "scope": selected_scope,
                        "selected": selected_name,
                        "selection_loss": selected_loss,
                        "selection_base_loss": selected_base_loss,
                        "selection_delta": selected_base_loss - selected_loss,
                        "n_pool": int(len(subject_pool) if selected_scope == "subject" else len(pool_idx)),
                        "n_val": int(len(val_subject_idx)),
                    }
                )

    combo_frame = pd.concat([train[KEY_COLUMNS], sample[KEY_COLUMNS]], ignore_index=True)
    combo_pred = np.vstack([base_oof, base_submission])
    candidate_combo: dict[str, np.ndarray] = {"base": combo_pred}
    for spec in specs:
        if spec.name == "base":
            continue
        candidate_combo[spec.name] = smooth_predictions(
            combo_frame,
            combo_pred,
            float(spec.bandwidth),
            spec.weight,
            spec.smoothing_space,
        )

    final_submission = base_submission.copy()
    final_selection_rows = []
    for target_i, target in enumerate(TARGET_COLUMNS):
        global_name, global_loss, global_base_loss = select_candidate(y, candidate_oof, target_i, all_idx, args.min_delta)
        for subject in sample["subject_id"].unique():
            test_subject_idx = np.flatnonzero(sample["subject_id"].to_numpy() == subject)
            train_subject_idx = np.flatnonzero(subjects == subject)
            selected_name = global_name
            selected_scope = "global"
            selected_loss = global_loss
            selected_base_loss = global_base_loss
            if len(train_subject_idx) >= args.min_subject_rows:
                subject_name, subject_loss, subject_base_loss = select_candidate(
                    y,
                    candidate_oof,
                    target_i,
                    train_subject_idx,
                    args.min_delta,
                )
                if subject_name != "base":
                    selected_name = subject_name
                    selected_scope = "subject"
                    selected_loss = subject_loss
                    selected_base_loss = subject_base_loss
            final_submission[test_subject_idx, target_i] = candidate_combo[selected_name][len(train) + test_subject_idx, target_i]
            final_selection_rows.append(
                {
                    "target": target,
                    "subject_id": subject,
                    "scope": selected_scope,
                    "selected": selected_name,
                    "selection_loss": selected_loss,
                    "selection_base_loss": selected_base_loss,
                    "selection_delta": selected_base_loss - selected_loss,
                    "n_pool": int(len(train_subject_idx) if selected_scope == "subject" else len(train)),
                    "n_test": int(len(test_subject_idx)),
                }
            )

    base_avg, base_targets = average_loss(y, base_oof)
    final_avg, final_targets = average_loss(y, final_oof)

    selection = pd.DataFrame(selection_rows)
    final_selection = pd.DataFrame(final_selection_rows)
    selection_summary = (
        selection.groupby(["target", "selected", "scope"], as_index=False)
        .agg(n=("selected", "size"), mean_selection_delta=("selection_delta", "mean"))
        .sort_values(["target", "n"], ascending=[True, False])
    )
    selection.to_csv(output_dir / "nested_selection.csv", index=False)
    final_selection.to_csv(output_dir / "submission_selection.csv", index=False)
    selection_summary.to_csv(output_dir / "selection_summary.csv", index=False)

    oof_df = train[KEY_COLUMNS + TARGET_COLUMNS].copy()
    for target_i, target in enumerate(TARGET_COLUMNS):
        oof_df[f"pred_{target}"] = final_oof[:, target_i]
    oof_path = output_dir / "oof_subject_adaptive_smoothing.csv"
    oof_df.to_csv(oof_path, index=False)

    submission = pd.read_csv(args.sample_path)
    for target_i, target in enumerate(TARGET_COLUMNS):
        submission[target] = np.clip(final_submission[:, target_i], EPS, 1.0 - EPS)
    submission_path = output_dir / "submission_subject_adaptive_smoothing.csv"
    submission.to_csv(submission_path, index=False)

    candidate_scores = []
    for name, pred in candidate_oof.items():
        avg, per_target = average_loss(y, pred)
        candidate_scores.append({"name": name, "avg_log_loss": avg, **per_target})
    pd.DataFrame(candidate_scores).sort_values("avg_log_loss").to_csv(output_dir / "candidate_scores.csv", index=False)

    report = {
        "base_avg_log_loss": base_avg,
        "base_targets": base_targets,
        "final_avg_log_loss": final_avg,
        "final_targets": final_targets,
        "args": vars(args),
        "selected_counts": selection_summary.to_dict(orient="records"),
    }
    (output_dir / "subject_adaptive_smoothing_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"base={base_avg:.6f} final={final_avg:.6f}")
    print(pd.DataFrame({"target": TARGET_COLUMNS, "base": [base_targets[t] for t in TARGET_COLUMNS], "final": [final_targets[t] for t in TARGET_COLUMNS]}).to_string(index=False))
    print(f"saved: {oof_path}")
    print(f"saved: {submission_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Nested subject-adaptive temporal smoothing selector.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--base-oof", default="outputs/prediction_stack_decoder_qcal_wide/oof_prediction_stack_decoder.csv")
    parser.add_argument("--base-submission", default="outputs/prediction_stack_decoder_qcal_wide/submission_prediction_stack_decoder.csv")
    parser.add_argument("--output-dir", default="outputs/subject_adaptive_smoothing")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--bandwidths", default="2,5,10,14,21,30,45,60")
    parser.add_argument("--weights", default="0.1,0.2,0.3,0.4,0.5,0.7,0.85,1.0")
    parser.add_argument("--smoothing-spaces", default="prob,logit")
    parser.add_argument("--selection-mode", choices=["complement", "prefix"], default="complement")
    parser.add_argument("--min-subject-rows", type=int, default=12)
    parser.add_argument("--min-global-rows", type=int, default=40)
    parser.add_argument("--min-delta", type=float, default=0.001)
    return parser.parse_args()


if __name__ == "__main__":
    main()
