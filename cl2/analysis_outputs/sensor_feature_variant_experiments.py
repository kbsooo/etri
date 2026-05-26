from __future__ import annotations

import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from pandas.errors import PerformanceWarning
from sklearn.metrics import log_loss

sys.path.append(str(Path(__file__).resolve().parent))
import calibration_experiments as cal  # noqa: E402
import deep_dive_analysis as d  # noqa: E402
import sensor_residual_experiments as sr  # noqa: E402


OUT = Path(__file__).resolve().parent
TARGETS = d.TARGETS
KEY = d.KEY
FIXED_CHOICES = {
    "Q1": ("base", 0.0),
    "Q2": ("phone", 0.10),
    "Q3": ("mobility", 0.20),
    "S1": ("base", 0.0),
    "S2": ("base", 0.0),
    "S3": ("base", 0.0),
    "S4": ("mobility", 0.10),
}


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1 - 1e-5)


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([log_loss(y[:, j], clip(pred[:, j]), labels=[0, 1]) for j in range(y.shape[1])]))


def per_target_loss(y: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    return {target: log_loss(y[:, j], clip(pred[:, j]), labels=[0, 1]) for j, target in enumerate(TARGETS)}


def group_prefixes(group: str) -> tuple[str, ...]:
    if group == "phone":
        return ("phone_",)
    if group == "mobility":
        return ("gps_", "loc_", "wifi_", "ble_")
    raise ValueError(group)


def variant_columns(rows: pd.DataFrame, group: str) -> list[str]:
    prefixes = group_prefixes(group)
    excluded = set(TARGETS + KEY + ["sleep_date", "split", "dow", "month"])
    cols = []
    for col in rows.columns:
        if col in excluded:
            continue
        if col.startswith(prefixes) and pd.api.types.is_numeric_dtype(rows[col]):
            cols.append(col)
    return cols


def add_variant_features(
    fit_rows: pd.DataFrame,
    apply_rows: pd.DataFrame,
    group: str,
    variant: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    fit_aug = fit_rows.copy()
    apply_aug = apply_rows.copy()
    if variant == "base":
        return fit_aug, apply_aug

    cols = variant_columns(fit_rows, group)
    fit_new = {}
    apply_new = {}
    if "missing" in variant:
        for col in cols:
            if fit_rows[col].isna().mean() > 0.02 or apply_rows[col].isna().mean() > 0.02:
                new_col = f"{col}__missing"
                fit_new[new_col] = fit_rows[col].isna().astype(float)
                apply_new[new_col] = apply_rows[col].isna().astype(float)

    if "subject_z" in variant:
        global_mean = fit_rows[cols].mean(numeric_only=True)
        global_std = fit_rows[cols].std(numeric_only=True).replace(0, np.nan)
        grouped_mean = fit_rows.groupby("subject_id")[cols].mean(numeric_only=True)
        grouped_std = fit_rows.groupby("subject_id")[cols].std(numeric_only=True).replace(0, np.nan)
        for col in cols:
            new_col = f"{col}__subj_z"
            fit_mean = fit_rows["subject_id"].map(grouped_mean[col]).fillna(global_mean[col])
            fit_std = fit_rows["subject_id"].map(grouped_std[col]).fillna(global_std[col]).fillna(1.0)
            apply_mean = apply_rows["subject_id"].map(grouped_mean[col]).fillna(global_mean[col])
            apply_std = apply_rows["subject_id"].map(grouped_std[col]).fillna(global_std[col]).fillna(1.0)
            fit_new[new_col] = (fit_rows[col] - fit_mean) / fit_std
            apply_new[new_col] = (apply_rows[col] - apply_mean) / apply_std

    if fit_new:
        fit_aug = pd.concat([fit_aug, pd.DataFrame(fit_new, index=fit_rows.index)], axis=1).copy()
        apply_aug = pd.concat([apply_aug, pd.DataFrame(apply_new, index=apply_rows.index)], axis=1).copy()
    return fit_aug, apply_aug


def fit_sensor_predict_variant(train_rows: pd.DataFrame, val_rows: pd.DataFrame, group: str, variant: str) -> np.ndarray:
    tr_aug, val_aug = add_variant_features(train_rows, val_rows, group, variant)
    cols = sr.feature_columns(tr_aug, group)
    pipe, cols = sr.make_sensor_pipeline(cols)
    pipe.fit(tr_aug[cols], tr_aug[TARGETS])
    return sr.proba_matrix(pipe, val_aug, cols)


def apply_fixed_caps(base: np.ndarray, phone: np.ndarray, mobility: np.ndarray) -> np.ndarray:
    pred = base.copy()
    sources = {"phone": phone, "mobility": mobility}
    for target, (source, weight) in FIXED_CHOICES.items():
        if source == "base" or weight == 0:
            continue
        j = TARGETS.index(target)
        pred[:, j] = (1.0 - weight) * base[:, j] + weight * sources[source][:, j]
    return clip(pred)


def fixed_cap_variant_oof(train: pd.DataFrame, variant: str) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    folds = d.make_folds(train, "subject_blocks")
    base = np.zeros((len(train), len(TARGETS)), dtype=float)
    phone = np.zeros_like(base)
    mobility = np.zeros_like(base)
    for fold_id, (tr_idx, val_idx) in enumerate(folds):
        tr = train.iloc[tr_idx].copy().reset_index(drop=True)
        val = train.iloc[val_idx].copy().reset_index(drop=True)
        base[val_idx] = cal.temporal_base(tr, val)
        phone[val_idx] = fit_sensor_predict_variant(tr, val, "phone", variant)
        mobility[val_idx] = fit_sensor_predict_variant(tr, val, "mobility", variant)
        print(f"[variant {variant}] fold {fold_id}", flush=True)
    pred = apply_fixed_caps(base, phone, mobility)
    return base, phone, mobility, pred


def make_submission(train: pd.DataFrame, sub: pd.DataFrame, variant: str) -> pd.DataFrame:
    base = cal.temporal_base(train, sub)
    phone = fit_sensor_predict_variant(train, sub, "phone", variant)
    mobility = fit_sensor_predict_variant(train, sub, "mobility", variant)
    pred = apply_fixed_caps(base, phone, mobility)
    out = sub[["subject_id", "sleep_date", "lifelog_date"]].copy()
    for j, target in enumerate(TARGETS):
        out[target] = pred[:, j]
    return out


def main() -> None:
    warnings.simplefilter("ignore", PerformanceWarning)
    train = sr.add_extra_features(pd.read_parquet(OUT / "train_deep_features.parquet"))
    sub = sr.add_extra_features(pd.read_parquet(OUT / "submission_deep_features.parquet"))
    y = train[TARGETS].to_numpy()
    rows = []
    variant_preds = {}
    for variant in ["base", "missing", "subject_z", "missing_subject_z"]:
        _, phone, mobility, pred = fixed_cap_variant_oof(train, variant)
        variant_preds[variant] = pred
        row = {"variant": variant, "model": "fixed_small_cap", "mean": mean_loss(y, pred)}
        row.update(per_target_loss(y, pred))
        row["phone_sensor_mean"] = mean_loss(y, phone)
        row["mobility_sensor_mean"] = mean_loss(y, mobility)
        rows.append(row)

    result = pd.DataFrame(rows).sort_values("mean")
    result.to_csv(OUT / "sensor_feature_variant_results.csv", index=False)
    best_variant = str(result.iloc[0]["variant"])
    make_submission(train, sub, best_variant).to_csv(
        OUT / f"submission_conservative_sensor_blend_{best_variant}.csv",
        index=False,
    )

    print("\nSensor feature variants")
    print(result.round(5).to_string(index=False))
    print(f"\nBest variant: {best_variant}")


if __name__ == "__main__":
    main()
