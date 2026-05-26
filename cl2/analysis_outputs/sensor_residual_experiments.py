from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import log_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

sys.path.append(str(Path(__file__).resolve().parent))
import calibration_experiments as cal  # noqa: E402
import deep_dive_analysis as d  # noqa: E402


OUT = Path(__file__).resolve().parent
TARGETS = d.TARGETS
KEY = d.KEY


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1 - 1e-5)


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([log_loss(y[:, j], clip(pred[:, j]), labels=[0, 1]) for j in range(y.shape[1])]))


def per_target_loss(y: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    return {target: log_loss(y[:, j], clip(pred[:, j]), labels=[0, 1]) for j, target in enumerate(TARGETS)}


def add_extra_features(train: pd.DataFrame) -> pd.DataFrame:
    out = train.copy()
    for name in ["location_daily_features.csv", "wifi_identity_daily_features.csv", "ble_identity_daily_features.csv"]:
        path = OUT / name
        if path.exists():
            extra = pd.read_csv(path, parse_dates=["lifelog_date"])
            out = out.merge(extra, on=KEY, how="left")
    return out


def feature_columns(train: pd.DataFrame, group: str) -> list[str]:
    excluded = set(TARGETS + KEY + ["sleep_date", "split"])
    base = [c for c in train.columns if c not in excluded]
    if group == "all":
        return base
    if group == "no_history_meta":
        return [c for c in base if not c.startswith("hist_")]
    prefixes = {
        "phone": ("phone_",),
        "watch": ("watch_", "hr_"),
        "mobility": ("gps_", "loc_", "wifi_", "ble_"),
        "usage_ambience": ("usage_", "ambience_"),
        "light": ("phone_light_", "watch_light_"),
        "coverage": ("hr_", "watch_pedo_", "wifi_", "ble_", "gps_", "ambience_len_"),
    }
    if group in prefixes:
        keep = tuple(prefixes[group])
        return [c for c in base if c.startswith(keep) or c in {"subject_id", "dow", "month", "day", "weekofyear", "subject_day_index", "is_weekend"}]
    raise ValueError(group)


def make_sensor_pipeline(cols: list[str]) -> tuple[Pipeline, list[str]]:
    cat_cols = [c for c in cols if c in {"subject_id", "dow", "month"}]
    num_cols = [c for c in cols if c not in cat_cols]
    pre = ColumnTransformer(
        [
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
            ("num", SimpleImputer(strategy="median"), num_cols),
        ],
        sparse_threshold=0.2,
    )
    clf = ExtraTreesClassifier(
        n_estimators=180,
        min_samples_leaf=8,
        max_features=0.35,
        random_state=731,
        n_jobs=-1,
    )
    return Pipeline([("pre", pre), ("clf", clf)]), cols


def proba_matrix(pipe: Pipeline, rows: pd.DataFrame, cols: list[str]) -> np.ndarray:
    probas = pipe.predict_proba(rows[cols])
    out = np.zeros((len(rows), len(TARGETS)))
    for j, proba in enumerate(probas):
        if proba.shape[1] == 1:
            cls = pipe.named_steps["clf"].classes_[j][0]
            out[:, j] = 1.0 if cls == 1 else 0.0
        else:
            out[:, j] = proba[:, list(pipe.named_steps["clf"].classes_[j]).index(1)]
    return clip(out)


def sensor_oof(train: pd.DataFrame, folds: list[tuple[np.ndarray, np.ndarray]], group: str) -> np.ndarray:
    cols = feature_columns(train, group)
    pred = np.zeros((len(train), len(TARGETS)))
    for tr_idx, val_idx in folds:
        pipe, cols = make_sensor_pipeline(cols)
        pipe.fit(train.iloc[tr_idx][cols], train.iloc[tr_idx][TARGETS])
        pred[val_idx] = proba_matrix(pipe, train.iloc[val_idx], cols)
    return clip(pred)


def fit_sensor_predict(train_rows: pd.DataFrame, val_rows: pd.DataFrame, group: str) -> np.ndarray:
    cols = feature_columns(train_rows, group)
    pipe, cols = make_sensor_pipeline(cols)
    pipe.fit(train_rows[cols], train_rows[TARGETS])
    return proba_matrix(pipe, val_rows, cols)


def optimize_blend(y: np.ndarray, base: np.ndarray, sensor: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    grid = np.array([0.0, 0.02, 0.05, 0.08, 0.1, 0.15, 0.2, 0.3, 0.45, 0.6])
    weights = np.zeros(len(TARGETS))
    blended = np.zeros_like(base)
    for j in range(len(TARGETS)):
        losses = []
        for w in grid:
            p = (1 - w) * base[:, j] + w * sensor[:, j]
            losses.append(log_loss(y[:, j], clip(p), labels=[0, 1]))
        best = int(np.argmin(losses))
        weights[j] = grid[best]
        blended[:, j] = (1 - weights[j]) * base[:, j] + weights[j] * sensor[:, j]
    return weights, clip(blended)


def nested_sensor_blend(train: pd.DataFrame, outer_kind: str, group: str) -> pd.DataFrame:
    y = train[TARGETS].to_numpy()
    pred_base = np.zeros_like(y, dtype=float)
    pred_sensor = np.zeros_like(y, dtype=float)
    pred_blend = np.zeros_like(y, dtype=float)
    weight_rows = []
    for fold_id, (tr_idx, val_idx) in enumerate(d.make_folds(train, outer_kind)):
        outer_train = train.iloc[tr_idx].copy().reset_index(drop=True)
        outer_val = train.iloc[val_idx].copy().reset_index(drop=True)
        inner_folds = d.make_folds(outer_train, "subject_blocks")
        inner_base = cal.base_oof(outer_train, inner_folds)
        inner_sensor = sensor_oof(outer_train, inner_folds, group)
        weights, _ = optimize_blend(outer_train[TARGETS].to_numpy(), inner_base, inner_sensor)
        base_val = cal.temporal_base(outer_train, outer_val)
        sensor_val = fit_sensor_predict(outer_train, outer_val, group)
        blend_val = clip((1 - weights) * base_val + weights * sensor_val)
        pred_base[val_idx] = base_val
        pred_sensor[val_idx] = sensor_val
        pred_blend[val_idx] = blend_val
        row = {"outer_fold": outer_kind, "feature_group": group, "fold_id": fold_id}
        row.update({f"w_{t}": weights[j] for j, t in enumerate(TARGETS)})
        weight_rows.append(row)

    rows = []
    for name, pred in [("temporal_base", pred_base), ("sensor_only", pred_sensor), ("nested_blend", pred_blend)]:
        row = {"outer_fold": outer_kind, "feature_group": group, "model": name, "mean": mean_loss(y, pred)}
        row.update(per_target_loss(y, pred))
        rows.append(row)
    weight_df = pd.DataFrame(weight_rows)
    return pd.DataFrame(rows), weight_df


def group_ablation(train: pd.DataFrame, fold_kind: str) -> pd.DataFrame:
    y = train[TARGETS].to_numpy()
    rows = []
    for group in ["phone", "watch", "mobility", "usage_ambience", "light", "coverage", "all"]:
        pred = sensor_oof(train, d.make_folds(train, fold_kind), group)
        row = {"outer_fold": fold_kind, "feature_group": group, "model": "sensor_only", "mean": mean_loss(y, pred)}
        row.update(per_target_loss(y, pred))
        rows.append(row)
    return pd.DataFrame(rows).sort_values("mean")


def main() -> None:
    train = add_extra_features(pd.read_parquet(OUT / "train_deep_features.parquet"))
    all_results = []
    all_weights = []
    for group in ["all", "phone", "watch", "mobility", "usage_ambience"]:
        print(f"[nested] group={group}", flush=True)
        result, weights = nested_sensor_blend(train, "subject_blocks", group)
        all_results.append(result)
        all_weights.append(weights)
    ablation = group_ablation(train, "subject_blocks")
    nested = pd.concat(all_results, ignore_index=True).sort_values(["feature_group", "mean"])
    weights = pd.concat(all_weights, ignore_index=True)
    nested.to_csv(OUT / "sensor_nested_blend_results.csv", index=False)
    weights.to_csv(OUT / "sensor_nested_blend_weights.csv", index=False)
    ablation.to_csv(OUT / "sensor_group_ablation.csv", index=False)
    print("\nNested blend")
    print(nested.round(5).to_string(index=False))
    print("\nBlend weights")
    print(weights.round(3).to_string(index=False))
    print("\nSensor group ablation")
    print(ablation.round(5).to_string(index=False))


if __name__ == "__main__":
    main()
