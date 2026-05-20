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


def target_loss(y: pd.DataFrame, pred: np.ndarray, target_i: int) -> float:
    target = TARGET_COLUMNS[target_i]
    return float(log_loss(y[target].to_numpy(), np.clip(pred[:, target_i], EPS, 1.0 - EPS), labels=[0, 1]))


def average_loss(y: pd.DataFrame, pred: np.ndarray) -> tuple[float, dict[str, float]]:
    per_target = {target: target_loss(y, pred, i) for i, target in enumerate(TARGET_COLUMNS)}
    return float(np.mean(list(per_target.values()))), per_target


def default_candidates() -> list[str]:
    return [
        "graph_variant:outputs/graph_diffusion_variant_ensemble/oof_graph_diffusion_variant_ensemble.csv:outputs/graph_diffusion_variant_ensemble/submission_graph_diffusion_variant_ensemble.csv",
        "stack:outputs/prediction_stack_decoder/oof_prediction_stack_decoder.csv:outputs/prediction_stack_decoder/submission_prediction_stack_decoder.csv",
        "stack_qcal:outputs/prediction_stack_decoder_with_qcal/oof_prediction_stack_decoder.csv:outputs/prediction_stack_decoder_with_qcal/submission_prediction_stack_decoder.csv",
        "stack_full_bank:outputs/prediction_stack_decoder_full_bank/oof_prediction_stack_decoder.csv:outputs/prediction_stack_decoder_full_bank/submission_prediction_stack_decoder.csv",
    ]


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
    candidates = [load_candidate(item, train, sample) for item in (args.candidates or default_candidates())]

    score_rows = []
    for candidate in candidates:
        avg, per_target = average_loss(y, candidate["oof"])
        score_rows.append({"name": candidate["name"], "avg_log_loss": avg, **per_target})

    final_oof = np.zeros((len(train), len(TARGET_COLUMNS)), dtype=float)
    final_submission = np.zeros((len(sample), len(TARGET_COLUMNS)), dtype=float)
    selection_rows = []
    for target_i, target in enumerate(TARGET_COLUMNS):
        losses = [(target_loss(y, candidate["oof"], target_i), candidate) for candidate in candidates]
        loss_value, selected = min(losses, key=lambda item: item[0])
        final_oof[:, target_i] = selected["oof"][:, target_i]
        final_submission[:, target_i] = selected["submission"][:, target_i]
        selection_rows.append(
            {
                "target": target,
                "source": selected["name"],
                "selected_loss": loss_value,
                **{f"loss_{candidate['name']}": target_loss(y, candidate["oof"], target_i) for candidate in candidates},
            }
        )

    final_avg, final_targets = average_loss(y, final_oof)
    scores = pd.DataFrame(score_rows).sort_values("avg_log_loss")
    selection = pd.DataFrame(selection_rows)
    scores.to_csv(output_dir / "source_scores.csv", index=False)
    selection.to_csv(output_dir / "selection.csv", index=False)

    oof_df = train[KEY_COLUMNS + TARGET_COLUMNS].copy()
    for target_i, target in enumerate(TARGET_COLUMNS):
        oof_df[f"pred_{target}"] = final_oof[:, target_i]
    oof_path = output_dir / "oof_targetwise_prediction_ensemble.csv"
    oof_df.to_csv(oof_path, index=False)

    submission = pd.read_csv(args.sample_path)
    for target_i, target in enumerate(TARGET_COLUMNS):
        submission[target] = final_submission[:, target_i]
    submission_path = output_dir / "submission_targetwise_prediction_ensemble.csv"
    submission.to_csv(submission_path, index=False)

    report = {
        "final_avg_log_loss": final_avg,
        "final_targets": final_targets,
        "source_scores": scores.to_dict(orient="records"),
        "selection": selection_rows,
        "args": vars(args),
    }
    (output_dir / "targetwise_prediction_ensemble_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"final={final_avg:.6f}")
    print(selection.to_string(index=False))
    print(f"saved: {oof_path}")
    print(f"saved: {submission_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Target-wise ensemble over prediction-space decoder candidates.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--output-dir", default="outputs/targetwise_prediction_ensemble")
    parser.add_argument("--candidates", nargs="*", default=None)
    return parser.parse_args()


if __name__ == "__main__":
    main()
