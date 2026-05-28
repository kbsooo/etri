from __future__ import annotations

import itertools
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss

sys.path.append(str(Path(__file__).resolve().parent))
import calibration_experiments as cal  # noqa: E402
import deep_dive_analysis as d  # noqa: E402


OUT = Path(__file__).resolve().parent
TARGETS = d.TARGETS


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1 - 1e-5)


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([log_loss(y[:, j], clip(pred[:, j]), labels=[0, 1]) for j in range(y.shape[1])]))


def per_target_loss(y: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    return {target: log_loss(y[:, j], clip(pred[:, j]), labels=[0, 1]) for j, target in enumerate(TARGETS)}


def target_temporal_from_hist(
    ref: pd.DataFrame,
    rows: pd.DataFrame,
    hist: pd.DataFrame,
    target: str,
    shrink: float,
    alpha: float,
    tau: float,
    k: int,
) -> np.ndarray:
    j = TARGETS.index(target)
    subj = cal.subject_prior(ref, rows, shrink)[:, j]
    cols = [f"hist_{target}_nearest"]
    if k >= 3:
        cols.append(f"hist_{target}_near3_mean")
    if k >= 5:
        cols.append(f"hist_{target}_near5_mean")
    local = hist[cols].mean(axis=1, skipna=True).to_numpy(dtype=float)
    dist = (
        hist[[f"hist_{target}_nearest_dist", f"hist_{target}_prev_dist", f"hist_{target}_next_dist"]]
        .min(axis=1, skipna=True)
        .fillna(60)
        .to_numpy(dtype=float)
    )
    w = np.minimum(0.95, alpha * np.exp(-dist / tau))
    local = np.where(np.isnan(local), subj, local)
    return clip((1 - w) * subj + w * local)


def target_temporal(ref: pd.DataFrame, rows: pd.DataFrame, target: str, config: dict[str, float]) -> np.ndarray:
    hist = d.temporal_label_features_for_fold(ref, ref, rows)
    return target_temporal_from_hist(ref, rows, hist, target, **config)


def matrix_with_configs(ref: pd.DataFrame, rows: pd.DataFrame, configs_by_target: dict[str, dict[str, float]]) -> np.ndarray:
    pred = np.zeros((len(rows), len(TARGETS)))
    hist = d.temporal_label_features_for_fold(ref, ref, rows)
    for j, target in enumerate(TARGETS):
        pred[:, j] = target_temporal_from_hist(ref, rows, hist, target, **configs_by_target[target])
    return clip(pred)


def select_configs(inner_train: pd.DataFrame, configs: list[dict[str, float]]) -> tuple[dict[str, dict[str, float]], pd.DataFrame]:
    folds = d.make_folds(inner_train, "subject_blocks")
    cache = []
    for tr_idx, val_idx in folds:
        ref = inner_train.iloc[tr_idx].copy()
        rows = inner_train.iloc[val_idx].copy()
        hist = d.temporal_label_features_for_fold(ref, ref, rows)
        cache.append((val_idx, ref, rows, hist))

    y = inner_train[TARGETS].to_numpy()
    records = []
    for cfg in configs:
        pred = np.zeros_like(y, dtype=float)
        for val_idx, ref, rows, hist in cache:
            for j, target in enumerate(TARGETS):
                pred[val_idx, j] = target_temporal_from_hist(ref, rows, hist, target, **cfg)
        losses = per_target_loss(y, pred)
        record = dict(cfg)
        record["mean"] = mean_loss(y, pred)
        record.update(losses)
        records.append(record)
    table = pd.DataFrame(records)
    selected = {}
    for target in TARGETS:
        row = table.sort_values(target).iloc[0]
        selected[target] = {
            "shrink": float(row["shrink"]),
            "alpha": float(row["alpha"]),
            "tau": float(row["tau"]),
            "k": int(row["k"]),
        }
    return selected, table


def nested_target_specific(train: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, dict[str, float]]]:
    configs = [
        {"shrink": s, "alpha": a, "tau": tau, "k": k}
        for s, a, tau, k in itertools.product([4, 8, 16, 32], [0.1, 0.2, 0.35, 0.5], [3, 7, 14, 30], [1, 3, 5])
    ]
    fixed_config = {target: {"shrink": 16.0, "alpha": 0.2, "tau": 14.0, "k": 5} for target in TARGETS}
    y = train[TARGETS].to_numpy()
    pred_fixed = np.zeros_like(y, dtype=float)
    pred_target = np.zeros_like(y, dtype=float)
    selected_rows = []

    for fold_id, (tr_idx, val_idx) in enumerate(d.make_folds(train, "subject_blocks")):
        outer_train = train.iloc[tr_idx].copy().reset_index(drop=True)
        outer_val = train.iloc[val_idx].copy().reset_index(drop=True)
        selected, _ = select_configs(outer_train, configs)
        pred_fixed[val_idx] = matrix_with_configs(outer_train, outer_val, fixed_config)
        pred_target[val_idx] = matrix_with_configs(outer_train, outer_val, selected)
        for target, cfg in selected.items():
            selected_rows.append({"fold_id": fold_id, "target": target, **cfg})
        print(f"[outer fold {fold_id}] selected {selected}", flush=True)

    result_rows = []
    for name, pred in [("fixed_temporal", pred_fixed), ("target_specific_temporal", pred_target)]:
        row = {"model": name, "mean": mean_loss(y, pred)}
        row.update(per_target_loss(y, pred))
        result_rows.append(row)

    # Full-data config selection for candidate submission.
    full_selected, full_table = select_configs(train, configs)
    full_table.to_csv(OUT / "target_temporal_full_grid.csv", index=False)
    return pd.DataFrame(result_rows), pd.DataFrame(selected_rows), full_selected


def make_submission(train: pd.DataFrame, sub: pd.DataFrame, full_selected: dict[str, dict[str, float]]) -> pd.DataFrame:
    pred = matrix_with_configs(train, sub, full_selected)
    out = sub[["subject_id", "sleep_date", "lifelog_date"]].copy()
    for j, target in enumerate(TARGETS):
        out[target] = pred[:, j]
    return out


def main() -> None:
    train = pd.read_parquet(OUT / "train_deep_features.parquet")
    sub = pd.read_parquet(OUT / "submission_deep_features.parquet")
    results, selected, full_selected = nested_target_specific(train)
    results.to_csv(OUT / "target_specific_temporal_results.csv", index=False)
    selected.to_csv(OUT / "target_specific_temporal_selected_by_fold.csv", index=False)
    pd.DataFrame([{"target": target, **cfg} for target, cfg in full_selected.items()]).to_csv(
        OUT / "target_specific_temporal_full_selected.csv", index=False
    )
    submission = make_submission(train, sub, full_selected)
    submission.to_csv(OUT / "submission_target_specific_temporal.csv", index=False)
    print("\nNested target-specific temporal")
    print(results.round(5).to_string(index=False))
    print("\nFull-data selected configs")
    print(pd.DataFrame([{"target": target, **cfg} for target, cfg in full_selected.items()]).to_string(index=False))
    print("\nSubmission summary")
    print(submission[TARGETS].describe().round(4).to_string())


if __name__ == "__main__":
    main()
