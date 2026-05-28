from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss

sys.path.append(str(Path(__file__).resolve().parent))
import calibration_experiments as cal  # noqa: E402
import deep_dive_analysis as d  # noqa: E402
import meta_feature_experiments as mf  # noqa: E402
import sensor_feature_variant_experiments as sfv  # noqa: E402


OUT = Path(__file__).resolve().parent
TARGETS = d.TARGETS


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1 - 1e-5)


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([log_loss(y[:, j], clip(pred[:, j]), labels=[0, 1]) for j in range(y.shape[1])]))


def per_target_loss(y: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    return {target: log_loss(y[:, j], clip(pred[:, j]), labels=[0, 1]) for j, target in enumerate(TARGETS)}


def current_fixed(base: np.ndarray, phone: np.ndarray, mobility: np.ndarray) -> np.ndarray:
    pred = base.copy()
    for target, source, weight in [("Q2", "phone", 0.10), ("Q3", "mobility", 0.20), ("S4", "mobility", 0.10)]:
        j = TARGETS.index(target)
        sensor = phone if source == "phone" else mobility
        pred[:, j] = (1 - weight) * base[:, j] + weight * sensor[:, j]
    return clip(pred)


def main() -> None:
    train, sub = mf.prepare(force_meta=False)
    y = train[TARGETS].to_numpy()
    current, watch = oof_current_watch(train)

    rows = []
    grid = [0.0, 0.005, 0.01, 0.02, 0.03, 0.05, 0.08, 0.10, 0.15]
    for target in ["S1", "S2", "S3", "S4"]:
        j = TARGETS.index(target)
        for weight in grid:
            pred = current.copy()
            pred[:, j] = (1 - weight) * current[:, j] + weight * watch[:, j]
            row = {"target": target, "weight": weight, "mean": mean_loss(y, pred)}
            row.update(per_target_loss(y, pred))
            rows.append(row)
    result = pd.DataFrame(rows).sort_values("mean")
    result.to_csv(OUT / "tiny_watch_cap_results.csv", index=False)
    nested, selected = nested_watch_caps(train, grid)
    nested.to_csv(OUT / "tiny_watch_cap_nested_results.csv", index=False)
    selected.to_csv(OUT / "tiny_watch_cap_nested_selected.csv", index=False)
    full_weights = result.sort_values(["target", "mean"]).groupby("target", as_index=False).head(1)
    full_weights.to_csv(OUT / "tiny_watch_cap_full_weights.csv", index=False)
    submission = make_submission(train, sub, full_weights)
    submission.to_csv(OUT / "submission_tiny_watch_cap.csv", index=False)
    if float(nested.iloc[0]["mean"]) < 0.6228411063084949 and str(nested.iloc[0]["model"]) == "nested_tiny_watch":
        submission.to_csv(OUT / "submission_best.csv", index=False)
    print("\nDirect tiny watch")
    print(result.head(20).round(6).to_string(index=False))
    print("\nNested tiny watch")
    print(nested.round(6).to_string(index=False))
    print("\nSelected")
    print(selected.to_string(index=False))


def oof_current_watch(train: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    y = train[TARGETS].to_numpy()
    current = np.zeros_like(y, dtype=float)
    watch = np.zeros_like(y, dtype=float)
    for fold_id, (tr_idx, val_idx) in enumerate(d.make_folds(train, "subject_blocks")):
        tr = train.iloc[tr_idx].copy().reset_index(drop=True)
        val = train.iloc[val_idx].copy().reset_index(drop=True)
        base_val = cal.temporal_base(tr, val)
        phone = sfv.fit_sensor_predict_variant(tr, val, "phone", "missing")
        mobility = sfv.fit_sensor_predict_variant(tr, val, "mobility", "missing")
        watch_val = mf.fit_predict(tr, val, "meta_watch")
        current[val_idx] = current_fixed(base_val, phone, mobility)
        watch[val_idx] = watch_val
        print(f"[watch tiny] fold {fold_id}", flush=True)
    return current, watch


def choose_weights(y: np.ndarray, current: np.ndarray, watch: np.ndarray, grid: list[float]) -> dict[str, float]:
    out = {}
    for target in ["S1", "S2", "S3", "S4"]:
        j = TARGETS.index(target)
        losses = []
        for weight in grid:
            pred = (1 - weight) * current[:, j] + weight * watch[:, j]
            losses.append(log_loss(y[:, j], clip(pred), labels=[0, 1]))
        out[target] = float(grid[int(np.argmin(losses))])
    return out


def apply_weights(current: np.ndarray, watch: np.ndarray, weights: dict[str, float]) -> np.ndarray:
    pred = current.copy()
    for target, weight in weights.items():
        j = TARGETS.index(target)
        pred[:, j] = (1 - weight) * current[:, j] + weight * watch[:, j]
    return clip(pred)


def nested_watch_caps(train: pd.DataFrame, grid: list[float]) -> tuple[pd.DataFrame, pd.DataFrame]:
    y = train[TARGETS].to_numpy()
    pred_current = np.zeros_like(y, dtype=float)
    pred_nested = np.zeros_like(y, dtype=float)
    selected_rows = []
    for outer_id, (tr_idx, val_idx) in enumerate(d.make_folds(train, "subject_blocks")):
        outer_train = train.iloc[tr_idx].copy().reset_index(drop=True)
        outer_val = train.iloc[val_idx].copy().reset_index(drop=True)
        inner_current, inner_watch = oof_current_watch(outer_train)
        weights = choose_weights(outer_train[TARGETS].to_numpy(), inner_current, inner_watch, grid)
        base_val = cal.temporal_base(outer_train, outer_val)
        phone = sfv.fit_sensor_predict_variant(outer_train, outer_val, "phone", "missing")
        mobility = sfv.fit_sensor_predict_variant(outer_train, outer_val, "mobility", "missing")
        current_val = current_fixed(base_val, phone, mobility)
        watch_val = mf.fit_predict(outer_train, outer_val, "meta_watch")
        pred_current[val_idx] = current_val
        pred_nested[val_idx] = apply_weights(current_val, watch_val, weights)
        for target, weight in weights.items():
            selected_rows.append({"outer_fold": outer_id, "target": target, "weight": weight})
        print(f"[watch nested] outer {outer_id} weights={weights}", flush=True)
    rows = []
    for name, pred in [("current_missing", pred_current), ("nested_tiny_watch", pred_nested)]:
        row = {"model": name, "mean": mean_loss(y, pred)}
        row.update(per_target_loss(y, pred))
        rows.append(row)
    return pd.DataFrame(rows).sort_values("mean"), pd.DataFrame(selected_rows)


def make_submission(train: pd.DataFrame, sub: pd.DataFrame, full_weights: pd.DataFrame) -> pd.DataFrame:
    base = cal.temporal_base(train, sub)
    phone = sfv.fit_sensor_predict_variant(train, sub, "phone", "missing")
    mobility = sfv.fit_sensor_predict_variant(train, sub, "mobility", "missing")
    current = current_fixed(base, phone, mobility)
    watch = mf.fit_predict(train, sub, "meta_watch")
    weights = {row["target"]: float(row["weight"]) for _, row in full_weights.iterrows()}
    pred = apply_weights(current, watch, weights)
    out = sub[["subject_id", "sleep_date", "lifelog_date"]].copy()
    for j, target in enumerate(TARGETS):
        out[target] = pred[:, j]
    return out


if __name__ == "__main__":
    main()
