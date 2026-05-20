from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss


KEY_COLUMNS = ["subject_id", "sleep_date", "lifelog_date"]
TARGET_COLUMNS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
EPS = 1e-5


@dataclass(frozen=True)
class Move:
    target: str
    lo: float
    hi: float
    weight: float
    source_name: str


def normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in KEY_COLUMNS:
        out[col] = out[col].astype(str)
    return out


def logit(p: np.ndarray) -> np.ndarray:
    p = np.clip(p, EPS, 1.0 - EPS)
    return np.log(p / (1.0 - p))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -50.0, 50.0)))


def prediction_matrix(oof: pd.DataFrame) -> np.ndarray:
    return np.clip(np.column_stack([oof[f"pred_{target}"].to_numpy(float) for target in TARGET_COLUMNS]), EPS, 1.0 - EPS)


def submission_matrix(submission: pd.DataFrame) -> np.ndarray:
    return np.clip(submission[TARGET_COLUMNS].to_numpy(float), EPS, 1.0 - EPS)


def add_panel_position(train: pd.DataFrame, sample: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    all_rows = pd.concat(
        [
            train[KEY_COLUMNS].assign(_split="train", _row=np.arange(len(train))),
            sample[KEY_COLUMNS].assign(_split="sample", _row=np.arange(len(sample))),
        ],
        ignore_index=True,
    )
    all_rows = all_rows.sort_values(["subject_id", "lifelog_date", "sleep_date"]).copy()
    all_rows["panel_index"] = all_rows.groupby("subject_id").cumcount().astype(float)
    denom = all_rows.groupby("subject_id")["panel_index"].transform("max").replace(0, 1)
    all_rows["panel_position"] = all_rows["panel_index"] / denom
    train_pos = all_rows[all_rows["_split"].eq("train")].sort_values("_row")["panel_position"].to_numpy(float)
    sample_pos = all_rows[all_rows["_split"].eq("sample")].sort_values("_row")["panel_position"].to_numpy(float)
    train_out = train.reset_index(drop=True).copy()
    sample_out = sample.reset_index(drop=True).copy()
    train_out["panel_position"] = train_pos
    sample_out["panel_position"] = sample_pos
    return train_out, sample_out


def blend(base: np.ndarray, source: np.ndarray, weight: float) -> np.ndarray:
    return np.clip(sigmoid(logit(base) + weight * (logit(source) - logit(base))), EPS, 1.0 - EPS)


def avg_logloss(y: pd.DataFrame, pred: np.ndarray) -> float:
    return float(
        np.mean(
            [
                log_loss(y[target], np.clip(pred[:, i], EPS, 1.0 - EPS), labels=[0, 1])
                for i, target in enumerate(TARGET_COLUMNS)
            ]
        )
    )


def sample_position_weights(train: pd.DataFrame, sample: pd.DataFrame) -> np.ndarray:
    bins = np.asarray([0.0, 1 / 3, 2 / 3, 0.8, 1.000001], dtype=float)
    train_bin = np.digitize(train["panel_position"].to_numpy(float), bins) - 1
    sample_bin = np.digitize(sample["panel_position"].to_numpy(float), bins) - 1
    train_frac = np.bincount(train_bin, minlength=len(bins) - 1).astype(float) / len(train_bin)
    sample_frac = np.bincount(sample_bin, minlength=len(bins) - 1).astype(float) / len(sample_bin)
    ratio = np.divide(sample_frac, train_frac, out=np.zeros_like(train_frac), where=train_frac > 0)
    weights = ratio[train_bin]
    return weights / weights.mean()


def weighted_avg_logloss(y: pd.DataFrame, pred: np.ndarray, weights: np.ndarray) -> float:
    return float(
        np.mean(
            [
                log_loss(y[target], np.clip(pred[:, i], EPS, 1.0 - EPS), labels=[0, 1], sample_weight=weights)
                for i, target in enumerate(TARGET_COLUMNS)
            ]
        )
    )


def stats(pred: np.ndarray) -> dict[str, float]:
    return {
        "min": float(pred.min()),
        "p01": float(np.quantile(pred, 0.01)),
        "p05": float(np.quantile(pred, 0.05)),
        "mean": float(pred.mean()),
        "p95": float(np.quantile(pred, 0.95)),
        "p99": float(np.quantile(pred, 0.99)),
        "max": float(pred.max()),
        "abs_logit_mean": float(np.abs(logit(pred)).mean()),
        "extreme_005_995": float(((pred < 0.005) | (pred > 0.995)).mean()),
    }


def build_variant(
    name: str,
    moves: list[Move],
    train: pd.DataFrame,
    sample: pd.DataFrame,
    base_oof: np.ndarray,
    base_sub: np.ndarray,
    source_oof: np.ndarray,
    source_sub: np.ndarray,
    output_dir: Path,
) -> dict[str, object]:
    oof = base_oof.copy()
    sub = base_sub.copy()
    train_apply_rows = 0
    sample_apply_rows = 0
    for move in moves:
        target_i = TARGET_COLUMNS.index(move.target)
        train_mask = (train["panel_position"].to_numpy(float) >= move.lo) & (train["panel_position"].to_numpy(float) < move.hi)
        sample_mask = (sample["panel_position"].to_numpy(float) >= move.lo) & (sample["panel_position"].to_numpy(float) < move.hi)
        oof[train_mask, target_i] = blend(base_oof[:, target_i], source_oof[:, target_i], move.weight)[train_mask]
        sub[sample_mask, target_i] = blend(base_sub[:, target_i], source_sub[:, target_i], move.weight)[sample_mask]
        train_apply_rows += int(train_mask.sum())
        sample_apply_rows += int(sample_mask.sum())

    oof_frame = train[KEY_COLUMNS + TARGET_COLUMNS].copy()
    sub_frame = sample[KEY_COLUMNS].copy()
    for target_i, target in enumerate(TARGET_COLUMNS):
        oof_frame[f"pred_{target}"] = oof[:, target_i]
        sub_frame[target] = sub[:, target_i]

    oof_path = output_dir / f"oof_{name}.csv"
    sub_path = output_dir / f"submission_{name}.csv"
    oof_frame.to_csv(oof_path, index=False)
    sub_frame.to_csv(sub_path, index=False)
    weights = sample_position_weights(train, sample)
    return {
        "name": name,
        "uniform_oof_cv": avg_logloss(train[TARGET_COLUMNS], oof),
        "sample_weighted_oof_cv": weighted_avg_logloss(train[TARGET_COLUMNS], oof, weights),
        "train_apply_rows": train_apply_rows,
        "sample_apply_rows": sample_apply_rows,
        "oof_path": str(oof_path),
        "submission_path": str(sub_path),
        "moves": [move.__dict__ for move in moves],
        **stats(sub),
    }


def main() -> None:
    output_dir = Path("outputs/sequence_encoder_residual_portfolio")
    output_dir.mkdir(parents=True, exist_ok=True)
    train_raw = normalize_keys(pd.read_csv("data/ch2026_metrics_train.csv"))
    sample_raw = normalize_keys(pd.read_csv("data/ch2026_submission_sample.csv"))
    train, sample = add_panel_position(train_raw, sample_raw)

    base_oof_frame = normalize_keys(pd.read_csv("outputs/temporal_retrieval_prototype_portfolio/oof_trp_s2tail_w080_q3midtail_w035.csv"))
    base_sub_frame = normalize_keys(pd.read_csv("outputs/temporal_retrieval_prototype_portfolio/submission_trp_s2tail_w080_q3midtail_w035.csv"))
    source_oof_frame = normalize_keys(pd.read_csv("outputs/sequence_encoder_residual/oof_gru28.csv"))
    source_sub_frame = normalize_keys(pd.read_csv("outputs/sequence_encoder_residual/submission_gru28.csv"))
    for label, frame, ref in [
        ("base_oof", base_oof_frame, train),
        ("base_sub", base_sub_frame, sample),
        ("source_oof", source_oof_frame, train),
        ("source_sub", source_sub_frame, sample),
    ]:
        if not frame[KEY_COLUMNS].equals(ref[KEY_COLUMNS]):
            raise ValueError(f"key mismatch: {label}")

    base_oof = prediction_matrix(base_oof_frame)
    base_sub = submission_matrix(base_sub_frame)
    source_oof = prediction_matrix(source_oof_frame)
    source_sub = submission_matrix(source_sub_frame)

    variants = [
        ("trp_plus_gru28_s3tail_w100", [Move("S3", 0.8, 1.000001, 1.00, "gru28_sequence_residual")]),
        ("trp_plus_gru28_s3tail_w080", [Move("S3", 0.8, 1.000001, 0.80, "gru28_sequence_residual")]),
        ("trp_plus_gru28_s3tail_w050", [Move("S3", 0.8, 1.000001, 0.50, "gru28_sequence_residual")]),
    ]
    rows = [
        build_variant(name, moves, train, sample, base_oof, base_sub, source_oof, source_sub, output_dir)
        for name, moves in variants
    ]
    report = pd.DataFrame(rows).sort_values(["sample_weighted_oof_cv", "uniform_oof_cv"]).reset_index(drop=True)
    report.to_csv(output_dir / "portfolio_report.csv", index=False)
    (output_dir / "portfolio_report.json").write_text(
        json.dumps(report.to_dict(orient="records"), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(report.to_string(index=False))


if __name__ == "__main__":
    main()
