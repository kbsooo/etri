from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss

sys.path.append(str(Path(__file__).resolve().parent))
import calibration_experiments as cal  # noqa: E402
import deep_dive_analysis as d  # noqa: E402
import sensor_residual_experiments as sr  # noqa: E402


OUT = Path(__file__).resolve().parent
TARGETS = d.TARGETS


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1 - 1e-5)


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([log_loss(y[:, j], clip(pred[:, j]), labels=[0, 1]) for j in range(y.shape[1])]))


def per_target_loss(y: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    return {target: log_loss(y[:, j], clip(pred[:, j]), labels=[0, 1]) for j, target in enumerate(TARGETS)}


def optimize_blend_per_target(y: np.ndarray, base: np.ndarray, sensor: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    grid = np.array([0.0, 0.02, 0.05, 0.08, 0.1, 0.15, 0.2, 0.3, 0.45, 0.6])
    weights = np.zeros(len(TARGETS))
    losses = np.zeros(len(TARGETS))
    pred = np.zeros_like(base)
    for j in range(len(TARGETS)):
        loss_grid = []
        for w in grid:
            p = (1 - w) * base[:, j] + w * sensor[:, j]
            loss_grid.append(log_loss(y[:, j], clip(p), labels=[0, 1]))
        best = int(np.argmin(loss_grid))
        weights[j] = grid[best]
        losses[j] = loss_grid[best]
        pred[:, j] = (1 - weights[j]) * base[:, j] + weights[j] * sensor[:, j]
    return weights, losses, clip(pred)


def nested_group_selection(train: pd.DataFrame, groups: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    y = train[TARGETS].to_numpy()
    pred_base = np.zeros_like(y, dtype=float)
    pred_selected = np.zeros_like(y, dtype=float)
    selected_rows = []

    for fold_id, (tr_idx, val_idx) in enumerate(d.make_folds(train, "subject_blocks")):
        outer_train = train.iloc[tr_idx].copy().reset_index(drop=True)
        outer_val = train.iloc[val_idx].copy().reset_index(drop=True)
        inner_folds = d.make_folds(outer_train, "subject_blocks")
        inner_y = outer_train[TARGETS].to_numpy()
        inner_base = cal.base_oof(outer_train, inner_folds)
        outer_base = cal.temporal_base(outer_train, outer_val)
        pred_base[val_idx] = outer_base

        group_info = {}
        for group in groups:
            inner_sensor = sr.sensor_oof(outer_train, inner_folds, group)
            weights, losses, _ = optimize_blend_per_target(inner_y, inner_base, inner_sensor)
            outer_sensor = sr.fit_sensor_predict(outer_train, outer_val, group)
            group_info[group] = {"weights": weights, "losses": losses, "outer_sensor": outer_sensor}

        outer_block = outer_base.copy()
        for j, target in enumerate(TARGETS):
            best_group = min(groups, key=lambda g: group_info[g]["losses"][j])
            w = group_info[best_group]["weights"][j]
            outer_block[:, j] = (1 - w) * outer_base[:, j] + w * group_info[best_group]["outer_sensor"][:, j]
            selected_rows.append(
                {
                    "fold_id": fold_id,
                    "target": target,
                    "selected_group": best_group,
                    "weight": w,
                    "inner_loss": group_info[best_group]["losses"][j],
                }
            )
        pred_selected[val_idx] = clip(outer_block)
        print(f"[outer fold {fold_id}] selected groups {selected_rows[-len(TARGETS):]}", flush=True)

    rows = []
    for name, pred in [("temporal_base", pred_base), ("target_group_sensor", pred_selected)]:
        row = {"model": name, "mean": mean_loss(y, pred)}
        row.update(per_target_loss(y, pred))
        rows.append(row)
    return pd.DataFrame(rows), pd.DataFrame(selected_rows)


def full_train_group_choices(train: pd.DataFrame, groups: list[str]) -> pd.DataFrame:
    folds = d.make_folds(train, "subject_blocks")
    y = train[TARGETS].to_numpy()
    base = cal.base_oof(train, folds)
    rows = []
    for group in groups:
        sensor = sr.sensor_oof(train, folds, group)
        weights, losses, _ = optimize_blend_per_target(y, base, sensor)
        for j, target in enumerate(TARGETS):
            rows.append({"target": target, "group": group, "weight": weights[j], "loss": losses[j]})
    choices = pd.DataFrame(rows)
    return choices.sort_values(["target", "loss"]).groupby("target", as_index=False).head(1)


def make_submission(train: pd.DataFrame, sub: pd.DataFrame, choices: pd.DataFrame) -> pd.DataFrame:
    base = cal.temporal_base(train, sub)
    pred = base.copy()
    group_cache: dict[str, np.ndarray] = {}
    for _, row in choices.iterrows():
        target = row["target"]
        group = row["group"]
        weight = float(row["weight"])
        if group not in group_cache:
            group_cache[group] = sr.fit_sensor_predict(train, sub, group)
        j = TARGETS.index(target)
        pred[:, j] = (1 - weight) * base[:, j] + weight * group_cache[group][:, j]
    out = sub[["subject_id", "sleep_date", "lifelog_date"]].copy()
    for j, target in enumerate(TARGETS):
        out[target] = clip(pred[:, j])
    return out


def main() -> None:
    groups = ["all", "phone", "watch", "mobility", "usage_ambience"]
    train = sr.add_extra_features(pd.read_parquet(OUT / "train_deep_features.parquet"))
    sub = sr.add_extra_features(pd.read_parquet(OUT / "submission_deep_features.parquet"))
    results, selected = nested_group_selection(train, groups)
    choices = full_train_group_choices(train, groups)
    submission = make_submission(train, sub, choices)
    results.to_csv(OUT / "target_specific_sensor_selection_results.csv", index=False)
    selected.to_csv(OUT / "target_specific_sensor_selection_by_fold.csv", index=False)
    choices.to_csv(OUT / "target_specific_sensor_full_choices.csv", index=False)
    submission.to_csv(OUT / "submission_target_specific_sensor.csv", index=False)
    print("\nNested target-specific sensor selection")
    print(results.round(5).to_string(index=False))
    print("\nFull-train sensor choices")
    print(choices.round(5).to_string(index=False))
    print("\nSubmission summary")
    print(submission[TARGETS].describe().round(4).to_string())


if __name__ == "__main__":
    main()
