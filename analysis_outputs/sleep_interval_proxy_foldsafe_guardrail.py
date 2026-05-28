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
import geometry_mask_cv_experiments as geom  # noqa: E402
import sleep_interval_proxy_augmented_experiments as aug  # noqa: E402
import sleep_interval_proxy_experiments as sip  # noqa: E402


OUT = Path(__file__).resolve().parent
DATA = OUT.parents[0] / "data"
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


def configs() -> list[ETConfig]:
    return [
        ETConfig("foldsafe_leaf10_mf0.6", 520, 10, 0.60, None, 260805),
        ETConfig("foldsafe_leaf6_mf0.8", 520, 6, 0.80, None, 260806),
        ETConfig("foldsafe_leaf3_mf0.35", 520, 3, 0.35, None, 260807),
        ETConfig("foldsafe_leaf4_mf0.6_depth10", 520, 4, 0.60, 10, 260808),
    ]


def relative_source_cols(rows: pd.DataFrame) -> list[str]:
    cols = aug.augmentation_columns(rows)
    # Keep only self-contained row covariates; fold-safe mode intentionally
    # excludes prev/next/rolling terms because those use hidden-block covariates.
    return [c for c in cols if not any(x in c for x in ["neighbor", "prev_", "next_", "roll3"])]


def add_ref_relative_features(rows: pd.DataFrame, ref: pd.DataFrame, rel_cols: list[str]) -> pd.DataFrame:
    out = rows.copy()
    additions: dict[str, np.ndarray] = {}
    ref_groups = {str(sid): g for sid, g in ref.groupby("subject_id", sort=False)}
    row_sids = rows["subject_id"].astype(str).to_numpy()
    for col in rel_cols:
        values = rows[col].to_numpy(dtype=float)
        centers = np.full(len(rows), np.nan, dtype=float)
        zscores = np.full(len(rows), np.nan, dtype=float)
        ranks = np.full(len(rows), np.nan, dtype=float)
        for sid in np.unique(row_sids):
            idx = np.where(row_sids == sid)[0]
            ref_g = ref_groups.get(str(sid))
            if ref_g is None or col not in ref_g:
                continue
            ref_vals = ref_g[col].to_numpy(dtype=float)
            ref_vals = ref_vals[np.isfinite(ref_vals)]
            if ref_vals.size == 0:
                continue
            mean = float(np.mean(ref_vals))
            std = float(np.std(ref_vals, ddof=1)) if ref_vals.size > 1 else np.nan
            vals = values[idx]
            centers[idx] = vals - mean
            if np.isfinite(std) and std > 0:
                zscores[idx] = (vals - mean) / std
            sorted_vals = np.sort(ref_vals)
            ranks[idx] = np.searchsorted(sorted_vals, vals, side="right") / float(len(sorted_vals))
        additions[f"{col}_ref_center"] = centers
        additions[f"{col}_ref_z"] = zscores
        additions[f"{col}_ref_rank"] = ranks
    rel = pd.DataFrame(additions, index=rows.index)
    return pd.concat([out, rel], axis=1)


def base_frames() -> tuple[pd.DataFrame, pd.DataFrame]:
    train, sub = sip.prepare_frames()
    train = train.sort_values(KEY).reset_index(drop=True)
    sub = sub.sort_values(KEY).reset_index(drop=True)
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


def fold_oof(train: pd.DataFrame, cfg: ETConfig, folds: list[tuple[np.ndarray, np.ndarray]]) -> np.ndarray:
    rel_cols = relative_source_cols(train)
    pred = np.zeros((len(train), len(TARGETS)), dtype=float)
    for fold_id, (tr_idx, val_idx) in enumerate(folds):
        ref_raw = train.iloc[tr_idx].copy().reset_index(drop=True)
        val_raw = train.iloc[val_idx].copy().reset_index(drop=True)
        ref = add_ref_relative_features(ref_raw, ref_raw, rel_cols)
        val = add_ref_relative_features(val_raw, ref_raw, rel_cols)
        pred[val_idx] = fit_predict(ref, val, cfg)
        print(f"[foldsafe proxy] {cfg.name} fold={fold_id}", flush=True)
    return clip(pred)


def summarize_subject_blocks(train: pd.DataFrame, pred: np.ndarray, cfg_name: str) -> pd.DataFrame:
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
            sel = loss_col(y[select_mask, j], p[select_mask])
            if selected is None or sel < selected[0]:
                selected = (sel, float(w), p)
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


def geometry_guardrail(train: pd.DataFrame, sub: pd.DataFrame, cfg: ETConfig) -> pd.DataFrame:
    raw_train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    raw_sub = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    raw_train = raw_train.sort_values(KEY).reset_index(drop=True)
    raw_sub = raw_sub.sort_values(KEY).reset_index(drop=True)
    rel_cols = relative_source_cols(train)
    current = np.load(OUT / "final_hybrid_0p598_repro_oof.npy")
    folds = geom.geometry_folds(raw_train, raw_sub, n_repeats=10)
    ys, bases, proxies = [], [], []
    for fold_id, (tr_idx, val_idx, fold_name) in enumerate(folds):
        ref_raw = train.iloc[tr_idx].copy().reset_index(drop=True)
        val_raw = train.iloc[val_idx].copy().reset_index(drop=True)
        ref = add_ref_relative_features(ref_raw, ref_raw, rel_cols)
        val = add_ref_relative_features(val_raw, ref_raw, rel_cols)
        proxy = fit_predict(ref, val, cfg)
        ys.append(train.iloc[val_idx][TARGETS].to_numpy(dtype=int))
        bases.append(current[val_idx])
        proxies.append(proxy)
        print(f"[foldsafe geometry] {cfg.name} {fold_name} val={len(val_idx)}", flush=True)
    y = np.vstack(ys)
    base = np.vstack(bases)
    proxy = np.vstack(proxies)
    grid = np.array([0.0, 0.02, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30, 0.45, 0.60, 0.80, 1.00])
    rows = []
    for j, target in enumerate(TARGETS):
        base_loss = loss_col(y[:, j], base[:, j])
        losses = [loss_col(y[:, j], (1.0 - w) * base[:, j] + w * proxy[:, j]) for w in grid]
        best_i = int(np.argmin(losses))
        rows.append(
            {
                "config": cfg.name,
                "target": target,
                "base_loss": base_loss,
                "proxy_loss": loss_col(y[:, j], proxy[:, j]),
                "best_weight": float(grid[best_i]),
                "best_blend_loss": float(losses[best_i]),
                "delta_vs_base": float(losses[best_i] - base_loss),
                "scored_occurrences": int(len(y)),
            }
        )
    return pd.DataFrame(rows)


def make_submission(train: pd.DataFrame, sub: pd.DataFrame, selected: pd.DataFrame) -> None:
    base = pd.read_csv(OUT / "submission_hybrid_0p597_sleep_proxy.csv", parse_dates=["sleep_date", "lifelog_date"])
    old_base = pd.read_csv(OUT / "submission_hybrid_0p598_repro.csv", parse_dates=["sleep_date", "lifelog_date"])
    base = base.sort_values(KEY).reset_index(drop=True)
    old_base = old_base.sort_values(KEY).reset_index(drop=True)
    estimate = pd.read_csv(OUT / "hybrid_0p597_sleep_proxy_cv_estimate.csv")
    rel_cols = relative_source_cols(train)
    train_aug = add_ref_relative_features(train.copy().reset_index(drop=True), train.copy().reset_index(drop=True), rel_cols)
    sub_aug = add_ref_relative_features(sub.copy().reset_index(drop=True), train.copy().reset_index(drop=True), rel_cols)
    for row in selected.itertuples(index=False):
        target = str(row.target)
        if target != "Q1":
            continue
        if float(row.delta_vs_current) >= -0.002:
            continue
        if float(row.half_holdout_blend) >= float(row.half_holdout_current):
            continue
        cfg = next(c for c in configs() if c.name == str(row.config))
        proxy_sub = fit_predict(train_aug, sub_aug, cfg)
        w = float(row.best_weight)
        j = TARGETS.index(target)
        base[target] = clip((1.0 - w) * old_base[target].to_numpy(dtype=float) + w * proxy_sub[:, j])
        estimate.loc[estimate["target"].eq(target), "source"] = f"{cfg.name}_w{w:g}_refstats_sleep_proxy"
        estimate.loc[estimate["target"].eq(target), "cv_loss"] = float(row.best_blend_loss)
    base[TARGETS] = base[TARGETS].clip(1e-5, 1 - 1e-5)
    base.to_csv(OUT / "submission_hybrid_0p597_sleep_proxy_foldsafe.csv", index=False)
    mean_loss = float(estimate[estimate["target"].isin(TARGETS)]["cv_loss"].mean())
    estimate.loc[estimate["target"].eq("mean"), "source"] = "hybrid_0p595_sleep_proxy_foldsafe"
    estimate.loc[estimate["target"].eq("mean"), "cv_loss"] = mean_loss
    estimate.to_csv(OUT / "hybrid_0p595_sleep_proxy_foldsafe_cv_estimate.csv", index=False)


def main() -> None:
    train, sub = base_frames()
    folds = d.make_folds(train, "subject_blocks")
    all_rows = []
    preds = {}
    for cfg in configs():
        pred = fold_oof(train, cfg, folds)
        preds[cfg.name] = pred
        np.save(OUT / f"sleep_interval_proxy_foldsafe_oof_{cfg.name}.npy", pred)
        all_rows.append(summarize_subject_blocks(train, pred, cfg.name))
    result = pd.concat(all_rows, ignore_index=True)
    result.to_csv(OUT / "sleep_interval_proxy_foldsafe_results.csv", index=False)
    top = result.sort_values(["target", "best_blend_loss"]).groupby("target").head(5)
    top.to_csv(OUT / "sleep_interval_proxy_foldsafe_top.csv", index=False)
    q1_best = result[result["target"].eq("Q1")].sort_values("best_blend_loss").iloc[0]
    geom_result = geometry_guardrail(train, sub, next(c for c in configs() if c.name == str(q1_best["config"])))
    geom_result.to_csv(OUT / "sleep_interval_proxy_foldsafe_geometry_cv_results.csv", index=False)
    make_submission(train, sub, result.sort_values(["target", "best_blend_loss"]).groupby("target").head(1))
    print(top.round(6).to_string(index=False))
    print("\nGeometry guardrail")
    print(geom_result.round(6).to_string(index=False))
    print("wrote", OUT / "sleep_interval_proxy_foldsafe_results.csv")


if __name__ == "__main__":
    main()
