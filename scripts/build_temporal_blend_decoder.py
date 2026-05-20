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


def make_subject_time_folds(train_df: pd.DataFrame, n_folds: int) -> list[tuple[np.ndarray, np.ndarray]]:
    ordered = train_df.reset_index(names="_idx").sort_values(["subject_id", "lifelog_date", "sleep_date"])
    val_indices: list[list[int]] = [[] for _ in range(n_folds)]
    for _, group in ordered.groupby("subject_id", sort=False):
        for fold, chunk in enumerate(np.array_split(group["_idx"].to_numpy(), n_folds)):
            val_indices[fold].extend(chunk.tolist())
    all_indices = np.arange(len(train_df))
    return [
        (np.setdiff1d(all_indices, np.array(sorted(fold_indices), dtype=int)), np.array(sorted(fold_indices), dtype=int))
        for fold_indices in val_indices
    ]


def temporal_prior(
    train_part: pd.DataFrame,
    eval_part: pd.DataFrame,
    bandwidth: float,
    alpha: float,
) -> np.ndarray:
    global_rate = train_part[TARGET_COLUMNS].mean().to_numpy(dtype=float)
    pred = np.zeros((len(eval_part), len(TARGET_COLUMNS)), dtype=float)
    for row_i, (_, row) in enumerate(eval_part.iterrows()):
        pool = train_part[train_part["subject_id"].eq(row["subject_id"])]
        if pool.empty:
            pred[row_i] = global_rate
            continue
        distance = np.abs(pool["day_index_subject"].to_numpy(dtype=float) - float(row["day_index_subject"]))
        weights = np.exp(-distance / bandwidth)
        numerator = (weights[:, None] * pool[TARGET_COLUMNS].to_numpy(dtype=float)).sum(axis=0) + alpha * global_rate
        denominator = weights.sum() + alpha
        pred[row_i] = numerator / denominator
    return np.clip(pred, EPS, 1.0 - EPS)


def average_log_loss(y_true: pd.DataFrame, pred: np.ndarray) -> tuple[float, dict[str, float]]:
    pred = np.clip(pred, EPS, 1.0 - EPS)
    per_target = {
        target: float(log_loss(y_true[target].to_numpy(), pred[:, i], labels=[0, 1]))
        for i, target in enumerate(TARGET_COLUMNS)
    }
    return float(np.mean(list(per_target.values()))), per_target


def row_average_losses(y_true: pd.DataFrame, pred: np.ndarray) -> np.ndarray:
    pred = np.clip(pred, EPS, 1.0 - EPS)
    rows = []
    y = y_true[TARGET_COLUMNS].to_numpy(dtype=float)
    for i in range(len(y_true)):
        losses = -(y[i] * np.log(pred[i]) + (1.0 - y[i]) * np.log(1.0 - pred[i]))
        rows.append(float(np.mean(losses)))
    return np.array(rows)


def parse_float_list(value: str) -> list[float]:
    return [float(part) for part in value.split(",") if part.strip()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Blend target-wise latent decoder predictions with same-subject temporal priors.")
    parser.add_argument("--latent-path", default="outputs/diffusion_encoder/day_latents.parquet")
    parser.add_argument("--base-oof", default="outputs/latent_decoder/oof_targetwise.csv")
    parser.add_argument("--base-submission", default="outputs/latent_decoder/submission_latent_decoder_targetwise.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--output-dir", default="outputs/latent_decoder")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--bandwidths", default="7,10,14,21,28,42")
    parser.add_argument("--alphas", default="2,5,10,20")
    parser.add_argument("--weights", default="0,0.05,0.1,0.15,0.2,0.25,0.3,0.35,0.4,0.45,0.5,0.55,0.6,0.65,0.7,0.75,0.8,0.85,0.9,0.95,1")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    latent = pd.read_parquet(args.latent_path)
    latent[KEY_COLUMNS] = latent[KEY_COLUMNS].astype(str)
    train_df = latent[latent["is_labeled"].eq(1)].copy().reset_index(drop=True)
    test_df = latent[latent["is_labeled"].eq(0)].copy().reset_index(drop=True)
    sample = pd.read_csv(args.sample_path)
    sample[KEY_COLUMNS] = sample[KEY_COLUMNS].astype(str)
    test_df = sample[KEY_COLUMNS].merge(
        test_df[KEY_COLUMNS + ["day_index_subject"]],
        on=KEY_COLUMNS,
        how="left",
        validate="one_to_one",
    )
    if test_df["day_index_subject"].isna().any():
        raise ValueError("Some sample rows failed to join with latent day index")

    base_oof_df = pd.read_csv(args.base_oof)
    base_oof = np.column_stack([base_oof_df[f"pred_{target}"].to_numpy(dtype=float) for target in TARGET_COLUMNS])
    base_submission = pd.read_csv(args.base_submission)
    base_submission[KEY_COLUMNS] = base_submission[KEY_COLUMNS].astype(str)
    if not base_submission[KEY_COLUMNS].equals(sample[KEY_COLUMNS]):
        raise ValueError("Base submission keys do not match sample keys")
    base_test = base_submission[TARGET_COLUMNS].to_numpy(dtype=float)

    folds = make_subject_time_folds(train_df, args.folds)
    bandwidths = parse_float_list(args.bandwidths)
    alphas = parse_float_list(args.alphas)
    weights = parse_float_list(args.weights)

    temporal_oofs: dict[tuple[float, float], np.ndarray] = {}
    for bandwidth in bandwidths:
        for alpha in alphas:
            pred = np.zeros((len(train_df), len(TARGET_COLUMNS)), dtype=float)
            for train_idx, val_idx in folds:
                pred[val_idx] = temporal_prior(train_df.iloc[train_idx], train_df.iloc[val_idx], bandwidth, alpha)
            temporal_oofs[(bandwidth, alpha)] = pred

    final_oof = np.zeros_like(base_oof)
    final_test = np.zeros_like(base_test)
    selection_rows = []
    for target_i, target in enumerate(TARGET_COLUMNS):
        best = {"loss": np.inf}
        y = train_df[target].to_numpy(dtype=int)
        for (bandwidth, alpha), temporal_oof in temporal_oofs.items():
            for weight in weights:
                candidate = np.clip(weight * base_oof[:, target_i] + (1.0 - weight) * temporal_oof[:, target_i], EPS, 1.0 - EPS)
                loss = float(log_loss(y, candidate, labels=[0, 1]))
                if loss < best["loss"]:
                    best = {
                        "loss": loss,
                        "bandwidth": bandwidth,
                        "alpha": alpha,
                        "decoder_weight": weight,
                        "oof": candidate,
                    }
        final_oof[:, target_i] = best["oof"]
        temporal_test = temporal_prior(train_df, test_df, best["bandwidth"], best["alpha"])[:, target_i]
        final_test[:, target_i] = np.clip(
            best["decoder_weight"] * base_test[:, target_i] + (1.0 - best["decoder_weight"]) * temporal_test,
            EPS,
            1.0 - EPS,
        )
        selection_rows.append(
            {
                "target": target,
                "log_loss": best["loss"],
                "bandwidth": best["bandwidth"],
                "alpha": best["alpha"],
                "decoder_weight": best["decoder_weight"],
                "temporal_weight": 1.0 - best["decoder_weight"],
            }
        )

    score, per_target = average_log_loss(train_df[TARGET_COLUMNS], final_oof)
    base_score, base_per_target = average_log_loss(train_df[TARGET_COLUMNS], base_oof)
    diff = row_average_losses(train_df[TARGET_COLUMNS], base_oof) - row_average_losses(train_df[TARGET_COLUMNS], final_oof)
    rng = np.random.default_rng(42)
    boot = []
    for _ in range(5000):
        idx = rng.integers(0, len(diff), len(diff))
        boot.append(float(diff[idx].mean()))
    boot = np.array(boot)

    selection = pd.DataFrame(selection_rows)
    selection.to_csv(output_dir / "temporal_blend_selection.csv", index=False)
    pd.DataFrame(
        [
            {
                "name": "targetwise_temporal_blend",
                "avg_log_loss": score,
                "base_targetwise_log_loss": base_score,
                "improvement": base_score - score,
                "bootstrap_improvement_p025": float(np.quantile(boot, 0.025)),
                "bootstrap_improvement_p500": float(np.quantile(boot, 0.5)),
                "bootstrap_improvement_p975": float(np.quantile(boot, 0.975)),
                **per_target,
            }
        ]
    ).to_csv(output_dir / "temporal_blend_score.csv", index=False)

    oof_df = train_df[KEY_COLUMNS + TARGET_COLUMNS].copy()
    for target_i, target in enumerate(TARGET_COLUMNS):
        oof_df[f"pred_{target}"] = final_oof[:, target_i]
    oof_df.to_csv(output_dir / "oof_targetwise_temporal_blend.csv", index=False)

    submission = sample.copy()
    for target_i, target in enumerate(TARGET_COLUMNS):
        submission[target] = final_test[:, target_i]
    submission.to_csv(output_dir / "submission_latent_decoder_targetwise_temporal.csv", index=False)

    report = {
        "metric": "Average Log-Loss",
        "base_targetwise_log_loss": base_score,
        "base_per_target": base_per_target,
        "temporal_blend_log_loss": score,
        "temporal_blend_per_target": per_target,
        "improvement": base_score - score,
        "bootstrap_improvement_ci": [float(x) for x in np.quantile(boot, [0.025, 0.5, 0.975])],
        "selection": selection_rows,
        "prediction_summary": {
            target: {
                "min": float(final_test[:, i].min()),
                "mean": float(final_test[:, i].mean()),
                "max": float(final_test[:, i].max()),
            }
            for i, target in enumerate(TARGET_COLUMNS)
        },
        "args": vars(args),
    }
    (output_dir / "temporal_blend_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"base_targetwise_log_loss={base_score:.6f}")
    print(f"temporal_blend_log_loss={score:.6f}")
    print(f"saved submission: {output_dir / 'submission_latent_decoder_targetwise_temporal.csv'}")
    print(f"saved report: {output_dir / 'temporal_blend_report.json'}")


if __name__ == "__main__":
    main()
