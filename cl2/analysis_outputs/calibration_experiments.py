from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

sys.path.append(str(Path(__file__).resolve().parent))
import deep_dive_analysis as d  # noqa: E402


OUT = Path(__file__).resolve().parent
TARGETS = d.TARGETS
KEY = d.KEY


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1 - 1e-5)


def logit(p: np.ndarray) -> np.ndarray:
    p = clip(p)
    return np.log(p / (1 - p))


def mean_logloss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([log_loss(y[:, j], clip(pred[:, j]), labels=[0, 1]) for j in range(y.shape[1])]))


def per_target_logloss(y: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    return {t: log_loss(y[:, j], clip(pred[:, j]), labels=[0, 1]) for j, t in enumerate(TARGETS)}


def subject_prior(ref: pd.DataFrame, rows: pd.DataFrame, shrink: float) -> np.ndarray:
    global_mean = ref[TARGETS].mean()
    subj_sum = ref.groupby("subject_id")[TARGETS].sum()
    subj_n = ref.groupby("subject_id").size()
    pred = np.zeros((len(rows), len(TARGETS)))
    for i, (_, row) in enumerate(rows.iterrows()):
        sid = row["subject_id"]
        if sid in subj_sum.index:
            p = (subj_sum.loc[sid] + shrink * global_mean) / (subj_n.loc[sid] + shrink)
        else:
            p = global_mean
        pred[i] = p.to_numpy(dtype=float)
    return clip(pred)


def temporal_base(ref: pd.DataFrame, rows: pd.DataFrame, shrink: float = 16, alpha: float = 0.2, tau: float = 14, k: int = 5) -> np.ndarray:
    subj = subject_prior(ref, rows, shrink)
    hist = d.temporal_label_features_for_fold(ref, ref, rows)
    pred = np.zeros((len(rows), len(TARGETS)))
    for j, target in enumerate(TARGETS):
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
        local = np.where(np.isnan(local), subj[:, j], local)
        pred[:, j] = (1 - w) * subj[:, j] + w * local
    return clip(pred)


def base_oof(train: pd.DataFrame, folds: list[tuple[np.ndarray, np.ndarray]], **kwargs) -> np.ndarray:
    pred = np.zeros((len(train), len(TARGETS)))
    for tr_idx, val_idx in folds:
        pred[val_idx] = temporal_base(train.iloc[tr_idx].copy(), train.iloc[val_idx].copy(), **kwargs)
    return clip(pred)


def prediction_frame(rows: pd.DataFrame, pred: np.ndarray, prefix: str = "base") -> pd.DataFrame:
    out = rows[["subject_id", "lifelog_date"]].reset_index(drop=True).copy()
    for j, target in enumerate(TARGETS):
        out[f"{prefix}_{target}"] = pred[:, j]
        out[f"{prefix}_{target}_logit"] = logit(pred[:, j])
    out["dow"] = rows["lifelog_date"].dt.dayofweek.astype(str).to_numpy()
    out["month"] = rows["lifelog_date"].dt.month.astype(str).to_numpy()
    min_day = rows.groupby("subject_id")["lifelog_date"].transform("min")
    out["subject_day_index"] = (rows["lifelog_date"] - min_day).dt.days.to_numpy()
    return out


def calibrate_fold(
    train_rows: pd.DataFrame,
    y_train: pd.DataFrame,
    train_base: np.ndarray,
    val_rows: pd.DataFrame,
    val_base: np.ndarray,
    mode: str,
) -> np.ndarray:
    if mode == "identity":
        return val_base

    train_feat = prediction_frame(train_rows, train_base)
    val_feat = prediction_frame(val_rows, val_base)
    out = np.zeros_like(val_base)

    if mode == "own_platt":
        for j, target in enumerate(TARGETS):
            xcols = [f"base_{target}_logit"]
            pipe = Pipeline(
                [
                    ("impute", SimpleImputer(strategy="median")),
                    ("clf", LogisticRegression(C=1.0, solver="liblinear", max_iter=1000)),
                ]
            )
            pipe.fit(train_feat[xcols], y_train[target])
            out[:, j] = pipe.predict_proba(val_feat[xcols])[:, 1]
        return clip(out)

    if mode == "joint_logits":
        xcols = [f"base_{t}_logit" for t in TARGETS]
        for j, target in enumerate(TARGETS):
            pipe = Pipeline(
                [
                    ("impute", SimpleImputer(strategy="median")),
                    ("scale", StandardScaler()),
                    ("clf", LogisticRegression(C=0.35, solver="liblinear", max_iter=1000)),
                ]
            )
            pipe.fit(train_feat[xcols], y_train[target])
            out[:, j] = pipe.predict_proba(val_feat[xcols])[:, 1]
        return clip(out)

    if mode == "joint_logits_subject":
        xcols = [f"base_{t}_logit" for t in TARGETS] + ["subject_id", "dow", "month", "subject_day_index"]
        cat_cols = ["subject_id", "dow", "month"]
        num_cols = [c for c in xcols if c not in cat_cols]
        pre = ColumnTransformer(
            [
                ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
                ("num", Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), num_cols),
            ]
        )
        for j, target in enumerate(TARGETS):
            pipe = Pipeline([("pre", pre), ("clf", LogisticRegression(C=0.25, solver="liblinear", max_iter=1000))])
            pipe.fit(train_feat[xcols], y_train[target])
            out[:, j] = pipe.predict_proba(val_feat[xcols])[:, 1]
        return clip(out)

    raise ValueError(mode)


def nested_calibration_oof(train: pd.DataFrame, outer_kind: str, inner_kind: str = "subject_blocks") -> pd.DataFrame:
    outer_folds = d.make_folds(train, outer_kind)
    y = train[TARGETS].to_numpy()
    modes = ["identity", "own_platt", "joint_logits", "joint_logits_subject"]
    preds = {m: np.zeros_like(y, dtype=float) for m in modes}

    for tr_idx, val_idx in outer_folds:
        outer_train = train.iloc[tr_idx].copy().reset_index(drop=True)
        outer_val = train.iloc[val_idx].copy().reset_index(drop=True)
        inner_folds = d.make_folds(outer_train, inner_kind)
        train_base = base_oof(outer_train, inner_folds)
        val_base = temporal_base(outer_train, outer_val)
        for mode in modes:
            preds[mode][val_idx] = calibrate_fold(outer_train, outer_train[TARGETS], train_base, outer_val, val_base, mode)

    rows = []
    for mode, pred in preds.items():
        row = {"outer_fold": outer_kind, "calibration": mode, "mean": mean_logloss(y, pred)}
        row.update(per_target_logloss(y, pred))
        rows.append(row)
    return pd.DataFrame(rows).sort_values("mean")


def rule_blend(pred: np.ndarray, strength: float) -> np.ndarray:
    """Deterministic co-occurrence smoothing with hand-picked stable label edges."""
    p = pred.copy()
    idx = {t: i for i, t in enumerate(TARGETS)}
    pairs = [
        ("S2", "S4", 0.50),
        ("S4", "S2", 0.46),
        ("S3", "S2", 0.39),
        ("S2", "S3", 0.39),
        ("S1", "S2", 0.39),
        ("S1", "Q1", 0.38),
        ("Q2", "Q3", 0.34),
        ("Q3", "Q2", 0.34),
        ("Q1", "S1", 0.34),
    ]
    logits = logit(p)
    for src, dst, weight in pairs:
        logits[:, idx[dst]] += strength * weight * (p[:, idx[src]] - 0.5)
    return clip(1 / (1 + np.exp(-logits)))


def rule_blend_oof(train: pd.DataFrame, fold_kind: str) -> pd.DataFrame:
    folds = d.make_folds(train, fold_kind)
    y = train[TARGETS].to_numpy()
    base = base_oof(train, folds)
    rows = []
    for strength in [0.05, 0.1, 0.2, 0.35, 0.5, 0.8, 1.2]:
        pred = rule_blend(base, strength)
        row = {"outer_fold": fold_kind, "calibration": f"rule_blend_{strength}", "mean": mean_logloss(y, pred)}
        row.update(per_target_logloss(y, pred))
        rows.append(row)
    return pd.DataFrame(rows).sort_values("mean")


def main() -> None:
    train = pd.read_parquet(OUT / "train_deep_features.parquet")
    all_rows = []
    for outer_kind in ["subject_blocks", "random"]:
        all_rows.append(nested_calibration_oof(train, outer_kind))
        all_rows.append(rule_blend_oof(train, outer_kind))
    result = pd.concat(all_rows, ignore_index=True).sort_values(["outer_fold", "mean"])
    result.to_csv(OUT / "calibration_experiment_results.csv", index=False)
    print(result.round(5).to_string(index=False))


if __name__ == "__main__":
    main()
