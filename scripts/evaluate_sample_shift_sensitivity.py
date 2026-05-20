from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


KEY_COLUMNS = ["subject_id", "sleep_date", "lifelog_date"]
TARGET_COLUMNS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
EPS = 1e-5


def normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in KEY_COLUMNS:
        out[col] = out[col].astype(str)
    return out


def prediction_matrix(oof: pd.DataFrame) -> np.ndarray:
    pred_cols = [f"pred_{target}" for target in TARGET_COLUMNS]
    missing = sorted(set(pred_cols) - set(oof.columns))
    if missing:
        raise ValueError(f"OOF file is missing prediction columns: {missing}")
    return np.clip(oof[pred_cols].to_numpy(dtype=float), EPS, 1.0 - EPS)


def row_losses(y: pd.DataFrame, pred: np.ndarray) -> np.ndarray:
    y_arr = y[TARGET_COLUMNS].to_numpy(dtype=float)
    return -(y_arr * np.log(pred) + (1.0 - y_arr) * np.log(1.0 - pred)).mean(axis=1)


def add_panel_position(train: pd.DataFrame, sample: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    all_rows = pd.concat(
        [
            train[KEY_COLUMNS].assign(_split="train", _row=np.arange(len(train))),
            sample[KEY_COLUMNS].assign(_split="test", _row=np.arange(len(sample))),
        ],
        ignore_index=True,
    )
    ordered = all_rows.sort_values(["subject_id", "lifelog_date", "sleep_date"]).copy()
    ordered["panel_index"] = ordered.groupby("subject_id").cumcount().astype(float)
    subject_max = ordered.groupby("subject_id")["panel_index"].transform("max").replace(0, 1)
    ordered["panel_position"] = ordered["panel_index"] / subject_max
    train_position = (
        ordered[ordered["_split"].eq("train")]
        .sort_values("_row")["panel_position"]
        .reset_index(drop=True)
    )
    sample_position = (
        ordered[ordered["_split"].eq("test")]
        .sort_values("_row")["panel_position"]
        .reset_index(drop=True)
    )
    train_out = train.reset_index(drop=True).copy()
    sample_out = sample.reset_index(drop=True).copy()
    train_out["panel_position"] = train_position
    sample_out["panel_position"] = sample_position
    return train_out, sample_out


def sample_position_weights(train: pd.DataFrame, sample: pd.DataFrame, bins: np.ndarray) -> np.ndarray:
    train_bin = np.digitize(train["panel_position"].to_numpy(dtype=float), bins) - 1
    sample_bin = np.digitize(sample["panel_position"].to_numpy(dtype=float), bins) - 1
    n_bins = len(bins) - 1
    train_frac = np.bincount(train_bin, minlength=n_bins).astype(float) / max(len(train_bin), 1)
    sample_frac = np.bincount(sample_bin, minlength=n_bins).astype(float) / max(len(sample_bin), 1)
    ratio = np.divide(sample_frac, train_frac, out=np.zeros(n_bins, dtype=float), where=train_frac > 0)
    weights = ratio[train_bin]
    if weights.mean() > 0:
        weights = weights / weights.mean()
    return weights.astype(float)


def bootstrap_mean(
    values: np.ndarray,
    seed: int,
    n_bootstrap: int,
    weights: np.ndarray | None = None,
) -> tuple[float, float]:
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    if weights is None:
        probabilities = None
    else:
        weights = np.clip(np.asarray(weights, dtype=float), 0.0, None)
        probabilities = weights / weights.sum() if weights.sum() > 0 else None
    boot = np.empty(n_bootstrap, dtype=float)
    for i in range(n_bootstrap):
        idx = rng.choice(len(values), size=len(values), replace=True, p=probabilities)
        boot[i] = float(values[idx].mean())
    return float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.500))


def parse_seeds(raw: str) -> list[int]:
    return [int(item.strip()) for item in raw.split(",") if item.strip()]


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    train, sample = add_panel_position(train, sample)
    bins = np.asarray([float(value) for value in args.position_bins.split(",")], dtype=float)
    bins[-1] += 1e-6
    weights = sample_position_weights(train, sample, bins)

    base_oof = normalize_keys(pd.read_csv(args.base_oof))
    cand_oof = normalize_keys(pd.read_csv(args.candidate_oof))
    for name, oof in [("baseline", base_oof), ("candidate", cand_oof)]:
        if not oof[KEY_COLUMNS].equals(train[KEY_COLUMNS]):
            raise ValueError(f"{name} OOF keys do not match train keys")

    y = train[TARGET_COLUMNS]
    base_loss = row_losses(y, prediction_matrix(base_oof))
    cand_loss = row_losses(y, prediction_matrix(cand_oof))
    diff = base_loss - cand_loss
    tail_mask = train["panel_position"].to_numpy(dtype=float) >= args.tail_position

    leave_rows = []
    for subject in sorted(train["subject_id"].unique()):
        keep = train["subject_id"].ne(subject).to_numpy()
        keep_tail = keep & tail_mask
        leave_rows.append(
            {
                "left_out": subject,
                "n_removed": int((~keep).sum()),
                "uniform_delta": float(diff[keep].mean()),
                "sample_weighted_delta": float(np.average(diff[keep], weights=weights[keep])),
                "tail_delta": float(diff[keep_tail].mean()) if keep_tail.any() else np.nan,
            }
        )
    leave_df = pd.DataFrame(leave_rows).sort_values("sample_weighted_delta").reset_index(drop=True)
    leave_df.to_csv(output_dir / "leave_one_subject_sensitivity.csv", index=False)

    seed_rows = []
    tail_diff = diff[tail_mask]
    for seed in parse_seeds(args.seeds):
        weighted_p025, weighted_p500 = bootstrap_mean(diff, seed, args.bootstrap, weights)
        tail_p025, tail_p500 = bootstrap_mean(tail_diff, seed, args.bootstrap)
        seed_rows.append(
            {
                "seed": seed,
                "weighted_p025": weighted_p025,
                "weighted_p500": weighted_p500,
                "tail_p025": tail_p025,
                "tail_p500": tail_p500,
            }
        )
    seed_df = pd.DataFrame(seed_rows)
    seed_df.to_csv(output_dir / "bootstrap_seed_sensitivity.csv", index=False)

    print("leave-one-subject")
    print(leave_df.to_string(index=False))
    print("\nbootstrap seed sensitivity")
    print(seed_df.to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sample-shift sensitivity checks for OOF candidate deltas.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--base-oof", required=True)
    parser.add_argument("--candidate-oof", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--position-bins", default="0,0.3333333333,0.6666666667,0.8,1.0")
    parser.add_argument("--tail-position", type=float, default=0.8)
    parser.add_argument("--bootstrap", type=int, default=5000)
    parser.add_argument("--seeds", default="1,7,42,123,2026,9999,260519")
    return parser.parse_args()


if __name__ == "__main__":
    main()
