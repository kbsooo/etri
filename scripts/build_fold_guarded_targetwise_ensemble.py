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


def target_loss(y: pd.DataFrame, pred: np.ndarray, target_i: int, indices: np.ndarray | None = None) -> float:
    if indices is None:
        indices = np.arange(len(y))
    target = TARGET_COLUMNS[target_i]
    return float(log_loss(y.iloc[indices][target].to_numpy(), np.clip(pred[indices, target_i], EPS, 1.0 - EPS), labels=[0, 1]))


def average_loss(y: pd.DataFrame, pred: np.ndarray) -> tuple[float, dict[str, float]]:
    per_target = {target: target_loss(y, pred, target_i) for target_i, target in enumerate(TARGET_COLUMNS)}
    return float(np.mean(list(per_target.values()))), per_target


def load_candidate(item: str, train: pd.DataFrame, sample: pd.DataFrame) -> dict:
    parts = item.split(":")
    if len(parts) != 3:
        raise ValueError("Candidate entries must be name:oof_path:submission_path")
    name, oof_path, submission_path = parts
    oof = normalize_keys(pd.read_csv(oof_path))
    submission = normalize_keys(pd.read_csv(submission_path))
    if not oof[KEY_COLUMNS].equals(train[KEY_COLUMNS]):
        raise ValueError(f"{name} OOF keys do not match train keys: {oof_path}")
    if not submission[KEY_COLUMNS].equals(sample[KEY_COLUMNS]):
        raise ValueError(f"{name} submission keys do not match sample keys: {submission_path}")
    return {
        "name": name,
        "oof_path": oof_path,
        "submission_path": submission_path,
        "oof": np.clip(prediction_matrix(oof), EPS, 1.0 - EPS),
        "submission": np.clip(submission_matrix(submission), EPS, 1.0 - EPS),
    }


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    y = train[TARGET_COLUMNS]
    folds = make_subject_time_folds(train, args.folds)

    baseline = load_candidate(args.baseline, train, sample)
    candidates = [baseline] + [load_candidate(item, train, sample) for item in args.candidates]

    score_rows = []
    for candidate in candidates:
        avg, per_target = average_loss(y, candidate["oof"])
        score_rows.append({"name": candidate["name"], "avg_log_loss": avg, **per_target})

    final_oof = baseline["oof"].copy()
    final_submission = baseline["submission"].copy()
    selection_rows = []
    for target_i, target in enumerate(TARGET_COLUMNS):
        baseline_loss = target_loss(y, baseline["oof"], target_i)
        rows = []
        for candidate in candidates:
            value = target_loss(y, candidate["oof"], target_i)
            folds_improved = 0
            for fold in folds:
                base_fold = target_loss(y, baseline["oof"], target_i, fold)
                cand_fold = target_loss(y, candidate["oof"], target_i, fold)
                folds_improved += int(cand_fold < base_fold)
            rows.append((value, folds_improved, candidate))

        eligible = [
            item
            for item in rows
            if item[2]["name"] == baseline["name"]
            or (baseline_loss - item[0] >= args.min_delta and item[1] >= args.min_folds_improved)
        ]
        selected_loss, selected_folds, selected = min(eligible, key=lambda item: item[0])
        final_oof[:, target_i] = selected["oof"][:, target_i]
        final_submission[:, target_i] = selected["submission"][:, target_i]
        selection_rows.append(
            {
                "target": target,
                "source": selected["name"],
                "selected_loss": selected_loss,
                "baseline_loss": baseline_loss,
                "delta_vs_baseline": baseline_loss - selected_loss,
                "folds_improved": selected_folds,
                "used": selected["name"] != baseline["name"],
                **{f"loss_{candidate['name']}": target_loss(y, candidate["oof"], target_i) for candidate in candidates},
                **{
                    f"folds_{candidate['name']}": sum(
                        target_loss(y, candidate["oof"], target_i, fold)
                        < target_loss(y, baseline["oof"], target_i, fold)
                        for fold in folds
                    )
                    for candidate in candidates
                },
            }
        )

    final_avg, final_targets = average_loss(y, final_oof)
    baseline_avg, baseline_targets = average_loss(y, baseline["oof"])
    scores = pd.DataFrame(score_rows).sort_values("avg_log_loss")
    selection = pd.DataFrame(selection_rows)
    scores.to_csv(output_dir / "source_scores.csv", index=False)
    selection.to_csv(output_dir / "selection.csv", index=False)

    oof_df = train[KEY_COLUMNS + TARGET_COLUMNS].copy()
    for target_i, target in enumerate(TARGET_COLUMNS):
        oof_df[f"pred_{target}"] = final_oof[:, target_i]
    oof_path = output_dir / "oof_fold_guarded_targetwise_ensemble.csv"
    oof_df.to_csv(oof_path, index=False)

    submission = pd.read_csv(args.sample_path)
    for target_i, target in enumerate(TARGET_COLUMNS):
        submission[target] = final_submission[:, target_i]
    submission_path = output_dir / "submission_fold_guarded_targetwise_ensemble.csv"
    submission.to_csv(submission_path, index=False)

    report = {
        "baseline": baseline["name"],
        "baseline_avg_log_loss": baseline_avg,
        "baseline_targets": baseline_targets,
        "final_avg_log_loss": final_avg,
        "final_targets": final_targets,
        "selection": selection_rows,
        "source_scores": scores.to_dict(orient="records"),
        "args": vars(args),
    }
    (output_dir / "fold_guarded_targetwise_ensemble_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"baseline={baseline_avg:.6f} final={final_avg:.6f}")
    print(selection[["target", "source", "selected_loss", "baseline_loss", "delta_vs_baseline", "folds_improved", "used"]].to_string(index=False))
    print(f"saved: {oof_path}")
    print(f"saved: {submission_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Target-wise ensemble with fold-improvement guard against local overfit.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--output-dir", default="outputs/fold_guarded_targetwise_ensemble")
    parser.add_argument("--baseline", required=True, help="Baseline entry formatted name:oof_path:submission_path")
    parser.add_argument("--candidates", nargs="+", required=True, help="Candidate entries formatted name:oof_path:submission_path")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--min-folds-improved", type=int, default=4)
    parser.add_argument("--min-delta", type=float, default=0.0001)
    return parser.parse_args()


if __name__ == "__main__":
    main()
