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
    cols = sip.feature_columns(train_rows)
    pipe = make_pipe(cols, cfg)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        pipe.fit(train_rows[cols], train_rows[TARGETS])
    return proba_matrix(pipe, rows, cols)


def oof_for_config(train: pd.DataFrame, cfg: ETConfig) -> np.ndarray:
    pred = np.zeros((len(train), len(TARGETS)), dtype=float)
    for fold_id, (tr_idx, val_idx) in enumerate(d.make_folds(train, "subject_blocks")):
        pred[val_idx] = fit_predict(train.iloc[tr_idx].copy(), train.iloc[val_idx].copy(), cfg)
        print(f"[sleep proxy search] {cfg.name} fold={fold_id}", flush=True)
    return clip(pred)


def summarize(train: pd.DataFrame, name: str, pred: np.ndarray) -> pd.DataFrame:
    current = np.load(OUT / "final_hybrid_0p598_repro_oof.npy")
    y = train[TARGETS].to_numpy(dtype=int)
    grid = np.array([0.0, 0.02, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30, 0.45, 0.60, 0.80, 1.00])
    rows = []
    first_subjects = set(sorted(train["subject_id"].unique())[:5])
    select_mask = train["subject_id"].isin(first_subjects).to_numpy()
    hold_mask = ~select_mask
    for j, target in enumerate(TARGETS):
        base_loss = loss_col(y[:, j], current[:, j])
        proxy_loss = loss_col(y[:, j], pred[:, j])
        blend_losses = []
        for w in grid:
            blend_losses.append(loss_col(y[:, j], (1.0 - w) * current[:, j] + w * pred[:, j]))
        best_i = int(np.argmin(blend_losses))
        selected = None
        for w in grid:
            p = (1.0 - w) * current[:, j] + w * pred[:, j]
            sel = loss_col(y[select_mask, j], p[select_mask])
            if selected is None or sel < selected[0]:
                selected = (sel, float(w), p)
        assert selected is not None
        rows.append(
            {
                "config": name,
                "target": target,
                "current_loss": base_loss,
                "proxy_loss": proxy_loss,
                "best_weight": float(grid[best_i]),
                "best_blend_loss": float(blend_losses[best_i]),
                "delta_vs_current": float(blend_losses[best_i] - base_loss),
                "half_selected_weight": selected[1],
                "half_select_loss": selected[0],
                "half_holdout_current": loss_col(y[hold_mask, j], current[hold_mask, j]),
                "half_holdout_blend": loss_col(y[hold_mask, j], selected[2][hold_mask]),
            }
        )
    return pd.DataFrame(rows)


def configs() -> list[ETConfig]:
    out = []
    for leaf in [3, 5, 6, 8, 10, 14]:
        for mf in [0.25, 0.35, 0.45, 0.60, 0.80]:
            name = f"et_leaf{leaf}_mf{mf:g}"
            out.append(ETConfig(name, 420, leaf, mf, None, 260526 + leaf * 10 + int(mf * 100)))
    out.extend(
        [
            ETConfig("et_leaf4_mf0.45_depth8", 520, 4, 0.45, 8, 260601),
            ETConfig("et_leaf4_mf0.60_depth10", 520, 4, 0.60, 10, 260602),
            ETConfig("et_leaf2_mf0.25_depth6", 520, 2, 0.25, 6, 260603),
        ]
    )
    return out


def main() -> None:
    train, _ = sip.prepare_frames()
    all_rows = []
    for cfg in configs():
        pred = oof_for_config(train, cfg)
        np.save(OUT / f"sleep_interval_proxy_oof_{cfg.name}.npy", pred)
        all_rows.append(summarize(train, cfg.name, pred))
    result = pd.concat(all_rows, ignore_index=True)
    result.to_csv(OUT / "sleep_interval_proxy_model_search_results.csv", index=False)
    top = result.sort_values(["target", "best_blend_loss"]).groupby("target").head(8)
    top.to_csv(OUT / "sleep_interval_proxy_model_search_top.csv", index=False)
    print(top.round(6).to_string(index=False))
    print("wrote", OUT / "sleep_interval_proxy_model_search_results.csv")


if __name__ == "__main__":
    main()
