from __future__ import annotations

import sys
import warnings
from dataclasses import dataclass
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
import deep_dive_analysis as d  # noqa: E402
import sleep_interval_proxy_experiments as sip  # noqa: E402


OUT = Path(__file__).resolve().parent
TARGETS = d.TARGETS
KEY = d.KEY


@dataclass(frozen=True)
class ETConfig:
    name: str
    n_estimators: int
    min_samples_leaf: int
    max_features: float
    max_depth: int | None
    seed: int


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1 - 1e-5)


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    return float(log_loss(y.astype(int), clip(p), labels=[0, 1]))


def augmentation_columns(df: pd.DataFrame) -> list[str]:
    keys = [
        "duration_min",
        "start_hour",
        "end_hour",
        "mid_hour",
        "duration_x_charge",
        "late_start_excess",
        "last_screen",
        "first_screen",
        "candidate_minutes",
        "candidate_sum",
        "candidate_mean",
        "step_core_sum",
        "screen_on_core_min",
        "hr_mean",
        "hr_min",
        "charge_frac",
    ]
    cols = []
    for col in df.columns:
        if not col.startswith("proxy_"):
            continue
        if df[col].dtype.kind not in "if":
            continue
        if any(key in col for key in keys):
            cols.append(col)
    return cols


def build_augmented_proxy() -> pd.DataFrame:
    path = OUT / "sleep_interval_proxy_augmented_features.parquet"
    if path.exists():
        return pd.read_parquet(path)
    base = sip.build_proxy_features().sort_values(KEY).reset_index(drop=True)
    aug = base.copy()
    cols = augmentation_columns(base)
    for col in cols:
        grp = aug.groupby("subject_id", sort=False)[col]
        mean = grp.transform("mean")
        std = grp.transform("std").replace(0, np.nan)
        aug[f"{col}_subj_z"] = (aug[col] - mean) / std
        aug[f"{col}_subj_center"] = aug[col] - mean
        aug[f"{col}_subj_rank"] = grp.rank(pct=True)
        sorted_aug = aug.sort_values(KEY)
        prev = sorted_aug.groupby("subject_id", sort=False)[col].shift(1)
        nxt = sorted_aug.groupby("subject_id", sort=False)[col].shift(-1)
        roll = (
            sorted_aug.groupby("subject_id", sort=False)[col]
            .rolling(3, min_periods=1, center=True)
            .mean()
            .reset_index(level=0, drop=True)
        )
        aug.loc[sorted_aug.index, f"{col}_prev_delta"] = sorted_aug[col] - prev
        aug.loc[sorted_aug.index, f"{col}_next_delta"] = nxt - sorted_aug[col]
        aug.loc[sorted_aug.index, f"{col}_neighbor_mean"] = (prev + nxt) / 2.0
        aug.loc[sorted_aug.index, f"{col}_neighbor_delta"] = sorted_aug[col] - (prev + nxt) / 2.0
        aug.loc[sorted_aug.index, f"{col}_roll3_center_delta"] = sorted_aug[col] - roll
    aug.to_parquet(path, index=False)
    return aug


def prepare_frames() -> tuple[pd.DataFrame, pd.DataFrame]:
    train = pd.read_parquet(OUT / "train_deep_features.parquet")
    sub = pd.read_parquet(OUT / "submission_deep_features.parquet")
    proxy = build_augmented_proxy()
    keep = KEY + ["sleep_date", "split", "dow", "month", "day", "weekofyear", "subject_day_index", "is_weekend"]
    train = train[keep + TARGETS].merge(proxy, on=KEY, how="left").sort_values(KEY).reset_index(drop=True)
    sub = sub[keep].merge(proxy, on=KEY, how="left").sort_values(KEY).reset_index(drop=True)
    return train, sub


def feature_columns(rows: pd.DataFrame) -> list[str]:
    excluded = set(TARGETS + KEY + ["sleep_date", "split"])
    return [c for c in rows.columns if c not in excluded]


def make_pipe(cols: list[str], cfg: ETConfig) -> Pipeline:
    cat = [c for c in cols if c in {"subject_id", "dow", "month"}]
    num = [c for c in cols if c not in cat]
    pre = ColumnTransformer(
        [
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat),
            ("num", SimpleImputer(strategy="median"), num),
        ],
        sparse_threshold=0.2,
    )
    clf = ExtraTreesClassifier(
        n_estimators=cfg.n_estimators,
        min_samples_leaf=cfg.min_samples_leaf,
        max_features=cfg.max_features,
        max_depth=cfg.max_depth,
        random_state=cfg.seed,
        n_jobs=-1,
    )
    return Pipeline([("pre", pre), ("clf", clf)])


def proba_matrix(pipe: Pipeline, rows: pd.DataFrame, cols: list[str]) -> np.ndarray:
    probas = pipe.predict_proba(rows[cols])
    classes = pipe.named_steps["clf"].classes_
    out = np.zeros((len(rows), len(TARGETS)), dtype=float)
    for j, proba in enumerate(probas):
        if proba.shape[1] == 1:
            out[:, j] = float(classes[j][0] == 1)
        else:
            out[:, j] = proba[:, list(classes[j]).index(1)]
    return clip(out)


def fit_predict(train_rows: pd.DataFrame, rows: pd.DataFrame, cfg: ETConfig) -> np.ndarray:
    cols = feature_columns(train_rows)
    pipe = make_pipe(cols, cfg)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        pipe.fit(train_rows[cols], train_rows[TARGETS])
    return proba_matrix(pipe, rows, cols)


def oof_for_config(train: pd.DataFrame, cfg: ETConfig) -> np.ndarray:
    pred = np.zeros((len(train), len(TARGETS)), dtype=float)
    for fold_id, (tr_idx, val_idx) in enumerate(d.make_folds(train, "subject_blocks")):
        pred[val_idx] = fit_predict(train.iloc[tr_idx].copy(), train.iloc[val_idx].copy(), cfg)
        print(f"[sleep proxy augmented] {cfg.name} fold={fold_id}", flush=True)
    return clip(pred)


def summarize(train: pd.DataFrame, cfg_name: str, pred: np.ndarray) -> pd.DataFrame:
    current = np.load(OUT / "final_hybrid_0p598_repro_oof.npy")
    y = train[TARGETS].to_numpy(dtype=int)
    grid = np.array([0.0, 0.02, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30, 0.45, 0.60, 0.80, 1.00])
    first_subjects = set(sorted(train["subject_id"].unique())[:5])
    select_mask = train["subject_id"].isin(first_subjects).to_numpy()
    hold_mask = ~select_mask
    rows = []
    for j, target in enumerate(TARGETS):
        base_loss = loss_col(y[:, j], current[:, j])
        proxy_loss = loss_col(y[:, j], pred[:, j])
        losses = [loss_col(y[:, j], (1.0 - w) * current[:, j] + w * pred[:, j]) for w in grid]
        best_i = int(np.argmin(losses))
        selected = None
        for w in grid:
            p = (1.0 - w) * current[:, j] + w * pred[:, j]
            sel_loss = loss_col(y[select_mask, j], p[select_mask])
            if selected is None or sel_loss < selected[0]:
                selected = (sel_loss, float(w), p)
        assert selected is not None
        rows.append(
            {
                "config": cfg_name,
                "target": target,
                "current_loss": base_loss,
                "proxy_loss": proxy_loss,
                "best_weight": float(grid[best_i]),
                "best_blend_loss": float(losses[best_i]),
                "delta_vs_current": float(losses[best_i] - base_loss),
                "half_selected_weight": selected[1],
                "half_select_loss": selected[0],
                "half_holdout_current": loss_col(y[hold_mask, j], current[hold_mask, j]),
                "half_holdout_blend": loss_col(y[hold_mask, j], selected[2][hold_mask]),
            }
        )
    return pd.DataFrame(rows)


def configs() -> list[ETConfig]:
    return [
        ETConfig("aug_leaf6_mf0.8", 520, 6, 0.80, None, 260701),
        ETConfig("aug_leaf8_mf0.8", 520, 8, 0.80, None, 260702),
        ETConfig("aug_leaf4_mf0.6_depth10", 520, 4, 0.60, 10, 260703),
        ETConfig("aug_leaf3_mf0.35", 520, 3, 0.35, None, 260704),
        ETConfig("aug_leaf10_mf0.6", 520, 10, 0.60, None, 260705),
    ]


def make_submission(train: pd.DataFrame, sub: pd.DataFrame, result: pd.DataFrame) -> None:
    base = pd.read_csv(OUT / "submission_hybrid_0p597_sleep_proxy.csv", parse_dates=["sleep_date", "lifelog_date"])
    base = base.sort_values(KEY).reset_index(drop=True)
    estimate = pd.read_csv(OUT / "hybrid_0p597_sleep_proxy_cv_estimate.csv")
    selected = result.sort_values(["target", "best_blend_loss"]).groupby("target").head(1)
    for row in selected.itertuples(index=False):
        if str(row.target) not in {"Q1", "S1"}:
            continue
        if float(row.delta_vs_current) >= -0.002:
            continue
        if float(row.half_holdout_blend) >= float(row.half_holdout_current):
            continue
        cfg = next(c for c in configs() if c.name == str(row.config))
        proxy_sub = fit_predict(train.copy(), sub.copy(), cfg)
        j = TARGETS.index(str(row.target))
        w = float(row.best_weight)
        old_base = pd.read_csv(OUT / "submission_hybrid_0p598_repro.csv", parse_dates=["sleep_date", "lifelog_date"])
        old_base = old_base.sort_values(KEY).reset_index(drop=True)
        base[str(row.target)] = clip((1.0 - w) * old_base[str(row.target)].to_numpy(dtype=float) + w * proxy_sub[:, j])
        estimate.loc[estimate["target"].eq(str(row.target)), "source"] = f"{row.config}_w{w:g}_aug_sleep_proxy"
        estimate.loc[estimate["target"].eq(str(row.target)), "cv_loss"] = float(row.best_blend_loss)
    base[TARGETS] = base[TARGETS].clip(1e-5, 1 - 1e-5)
    base.to_csv(OUT / "submission_hybrid_0p597_sleep_proxy_augmented.csv", index=False)
    mean_loss = float(estimate[estimate["target"].isin(TARGETS)]["cv_loss"].mean())
    estimate.loc[estimate["target"].eq("mean"), "source"] = "hybrid_0p595_sleep_proxy_augmented"
    estimate.loc[estimate["target"].eq("mean"), "cv_loss"] = mean_loss
    estimate.to_csv(OUT / "hybrid_0p595_sleep_proxy_augmented_cv_estimate.csv", index=False)


def main() -> None:
    train, sub = prepare_frames()
    rows = []
    for cfg in configs():
        pred = oof_for_config(train, cfg)
        np.save(OUT / f"sleep_interval_proxy_augmented_oof_{cfg.name}.npy", pred)
        rows.append(summarize(train, cfg.name, pred))
    result = pd.concat(rows, ignore_index=True)
    result.to_csv(OUT / "sleep_interval_proxy_augmented_results.csv", index=False)
    top = result.sort_values(["target", "best_blend_loss"]).groupby("target").head(5)
    top.to_csv(OUT / "sleep_interval_proxy_augmented_top.csv", index=False)
    make_submission(train, sub, result)
    print(top.round(6).to_string(index=False))
    print("wrote", OUT / "sleep_interval_proxy_augmented_results.csv")


if __name__ == "__main__":
    main()
