from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

import sys

sys.path.append(str(Path(__file__).resolve().parent))
import deep_dive_analysis as d  # noqa: E402


OUT = Path(__file__).resolve().parent
DATA = OUT.parents[0] / "data"
TARGETS = d.TARGETS
KEY = d.KEY


@dataclass(frozen=True)
class MetaConfig:
    mode: str
    c_value: float
    strength: float

    @property
    def name(self) -> str:
        return f"{self.mode}_C{self.c_value:g}_g{self.strength:g}"


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1 - 1e-5)


def logit(p: np.ndarray) -> np.ndarray:
    p = clip(p)
    return np.log(p / (1.0 - p))


def sigmoid(z: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-z))


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    return float(log_loss(y.astype(int), clip(p), labels=[0, 1]))


def per_target_losses(y: np.ndarray, p: np.ndarray) -> dict[str, float]:
    return {t: loss_col(y[:, j], p[:, j]) for j, t in enumerate(TARGETS)}


def current_oof() -> np.ndarray:
    path = OUT / "final_hybrid_0p594_q23foldsafe_oof.npy"
    if path.exists():
        return np.load(path)
    base = np.load(OUT / "final_hybrid_0p598_repro_oof.npy")
    q1_aug = np.load(OUT / "sleep_interval_proxy_augmented_oof_aug_leaf10_mf0.6.npy")
    s1_proxy = np.load(OUT / "sleep_interval_proxy_oof_et_leaf6_mf0.8.npy")
    q23_proxy = np.load(OUT / "sleep_interval_proxy_foldsafe_oof_foldsafe_leaf3_mf0.35.npy")
    pred = base.copy()
    pred[:, TARGETS.index("Q1")] = 0.40 * base[:, TARGETS.index("Q1")] + 0.60 * q1_aug[:, TARGETS.index("Q1")]
    pred[:, TARGETS.index("Q2")] = 0.80 * base[:, TARGETS.index("Q2")] + 0.20 * q23_proxy[:, TARGETS.index("Q2")]
    pred[:, TARGETS.index("Q3")] = 0.90 * base[:, TARGETS.index("Q3")] + 0.10 * q23_proxy[:, TARGETS.index("Q3")]
    pred[:, TARGETS.index("S1")] = 0.70 * base[:, TARGETS.index("S1")] + 0.30 * s1_proxy[:, TARGETS.index("S1")]
    pred = clip(pred)
    np.save(path, pred)
    return pred


def config_grid() -> list[MetaConfig]:
    modes = ["own", "pairs", "all"]
    c_values = [0.01, 0.03, 0.05, 0.10, 0.20, 0.50]
    strengths = [0.15, 0.25, 0.35, 0.50, 0.75, 1.00]
    return [MetaConfig(m, c, g) for m in modes for c in c_values for g in strengths]


def mode_columns(target: str, mode: str) -> list[str]:
    if mode == "own":
        return [target]
    pairs = {
        "Q1": ["Q1", "S1", "Q2", "Q3"],
        "Q2": ["Q2", "Q3", "Q1"],
        "Q3": ["Q3", "Q2", "Q1"],
        "S1": ["S1", "Q1", "S2", "S4"],
        "S2": ["S2", "S4", "S3", "S1"],
        "S3": ["S3", "S2", "S1"],
        "S4": ["S4", "S2", "S1", "S3"],
    }
    if mode == "pairs":
        return pairs[target]
    if mode == "all":
        return TARGETS
    raise ValueError(mode)


def feature_frame(rows: pd.DataFrame, pred: np.ndarray, target: str, mode: str) -> pd.DataFrame:
    cols = mode_columns(target, mode)
    out = pd.DataFrame({f"logit_{t}": logit(pred[:, TARGETS.index(t)]) for t in cols})
    out["subject_id"] = rows["subject_id"].astype(str).to_numpy()
    out["dow"] = rows["lifelog_date"].dt.dayofweek.astype(str).to_numpy()
    out["subject_day_index"] = rows["subject_day_index"].to_numpy(dtype=float) if "subject_day_index" in rows else np.arange(len(rows), dtype=float)
    return out


def make_pipe(x: pd.DataFrame, c_value: float) -> Pipeline:
    cat = [c for c in ["subject_id", "dow"] if c in x.columns]
    num = [c for c in x.columns if c not in cat]
    pre = ColumnTransformer(
        [
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat),
            ("num", Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), num),
        ],
        sparse_threshold=0.2,
    )
    clf = LogisticRegression(C=c_value, solver="liblinear", max_iter=1000)
    return Pipeline([("pre", pre), ("clf", clf)])


def fit_predict_config(
    train_rows: pd.DataFrame,
    train_pred: np.ndarray,
    y_train: np.ndarray,
    val_rows: pd.DataFrame,
    val_pred: np.ndarray,
    target: str,
    cfg: MetaConfig,
) -> np.ndarray:
    j = TARGETS.index(target)
    x_train = feature_frame(train_rows, train_pred, target, cfg.mode)
    x_val = feature_frame(val_rows, val_pred, target, cfg.mode)
    pipe = make_pipe(x_train, cfg.c_value)
    pipe.fit(x_train, y_train[:, j])
    meta = pipe.predict_proba(x_val)[:, 1]
    return clip((1.0 - cfg.strength) * val_pred[:, j] + cfg.strength * meta)


def select_config_inner(rows: pd.DataFrame, pred: np.ndarray, target: str) -> tuple[MetaConfig | None, float, float]:
    y = rows[TARGETS].to_numpy(dtype=int)
    j = TARGETS.index(target)
    base_loss = loss_col(y[:, j], pred[:, j])
    folds = d.make_folds(rows.reset_index(drop=True), "subject_blocks")
    best_cfg: MetaConfig | None = None
    best_loss = base_loss
    for cfg in config_grid():
        p = pred[:, j].copy()
        for tr_idx, val_idx in folds:
            tr = rows.iloc[tr_idx].copy().reset_index(drop=True)
            val = rows.iloc[val_idx].copy().reset_index(drop=True)
            p[val_idx] = fit_predict_config(
                tr,
                pred[tr_idx],
                y[tr_idx],
                val,
                pred[val_idx],
                target,
                cfg,
            )
        loss = loss_col(y[:, j], p)
        if loss < best_loss:
            best_loss = loss
            best_cfg = cfg
    return best_cfg, base_loss, best_loss


def nested_eval(train: pd.DataFrame, pred: np.ndarray) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray]:
    y = train[TARGETS].to_numpy(dtype=int)
    out = pred.copy()
    selected_rows = []
    for fold_id, (tr_idx, val_idx) in enumerate(d.make_folds(train, "subject_blocks")):
        tr = train.iloc[tr_idx].copy().reset_index(drop=True)
        val = train.iloc[val_idx].copy().reset_index(drop=True)
        y_tr = tr[TARGETS].to_numpy(dtype=int)
        for target in TARGETS:
            cfg, inner_base, inner_best = select_config_inner(tr, pred[tr_idx], target)
            if cfg is not None and inner_best + 0.0005 < inner_base:
                out[val_idx, TARGETS.index(target)] = fit_predict_config(
                    tr,
                    pred[tr_idx],
                    y_tr,
                    val,
                    pred[val_idx],
                    target,
                    cfg,
                )
                cfg_name = cfg.name
            else:
                cfg_name = "identity"
            selected_rows.append(
                {
                    "outer_fold": fold_id,
                    "target": target,
                    "selected": cfg_name,
                    "inner_base_loss": inner_base,
                    "inner_best_loss": inner_best,
                }
            )
        print(f"[cross-target nested] outer={fold_id}", flush=True)
    rows = []
    for name, p in [("current_0p594_oof", pred), ("nested_cross_target", out)]:
        row = {"model": name, "mean": float(np.mean(list(per_target_losses(y, p).values())))}
        row.update(per_target_losses(y, p))
        rows.append(row)
    return pd.DataFrame(rows), pd.DataFrame(selected_rows), clip(out)


def half_subject_guardrail(train: pd.DataFrame, pred: np.ndarray) -> pd.DataFrame:
    y = train[TARGETS].to_numpy(dtype=int)
    first_subjects = set(sorted(train["subject_id"].unique())[:5])
    select_mask = train["subject_id"].isin(first_subjects).to_numpy()
    hold_mask = ~select_mask
    rows = []
    for target in TARGETS:
        cfg, sel_base, sel_best = select_config_inner(train[select_mask].reset_index(drop=True), pred[select_mask], target)
        j = TARGETS.index(target)
        hold_base = loss_col(y[hold_mask, j], pred[hold_mask, j])
        if cfg is None:
            hold_meta = hold_base
            cfg_name = "identity"
        else:
            meta = fit_predict_config(
                train[select_mask].copy().reset_index(drop=True),
                pred[select_mask],
                y[select_mask],
                train[hold_mask].copy().reset_index(drop=True),
                pred[hold_mask],
                target,
                cfg,
            )
            hold_meta = loss_col(y[hold_mask, j], meta)
            cfg_name = cfg.name
        rows.append(
            {
                "target": target,
                "selected": cfg_name,
                "select_base_loss": sel_base,
                "select_best_loss": sel_best,
                "holdout_base_loss": hold_base,
                "holdout_meta_loss": hold_meta,
            }
        )
    return pd.DataFrame(rows)


def full_train_choice(train: pd.DataFrame, pred: np.ndarray, guardrail: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for target in TARGETS:
        cfg, base_loss, best_loss = select_config_inner(train.reset_index(drop=True), pred, target)
        hold = guardrail[guardrail["target"].eq(target)].iloc[0]
        if (
            cfg is not None
            and best_loss + 0.0008 < base_loss
            and float(hold["holdout_meta_loss"]) + 0.0002 < float(hold["holdout_base_loss"])
        ):
            rows.append({"target": target, "config": cfg.name, "base_loss": base_loss, "best_loss": best_loss})
        else:
            rows.append({"target": target, "config": "identity", "base_loss": base_loss, "best_loss": base_loss})
    return pd.DataFrame(rows)


def apply_submission(train: pd.DataFrame, pred: np.ndarray, selected: pd.DataFrame) -> pd.DataFrame:
    sub = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    sub = sub.sort_values(KEY).reset_index(drop=True)
    out = pd.read_csv(OUT / "submission_hybrid_0p594_sleep_proxy_q23foldsafe.csv", parse_dates=["sleep_date", "lifelog_date"])
    out = out.sort_values(KEY).reset_index(drop=True)
    sub_pred = out[TARGETS].to_numpy(dtype=float)
    y = train[TARGETS].to_numpy(dtype=int)
    for row in selected.itertuples(index=False):
        target = str(row.target)
        if str(row.config) == "identity":
            continue
        mode, rest = str(row.config).split("_C", 1)
        c_str, g_str = rest.split("_g", 1)
        cfg = MetaConfig(mode, float(c_str), float(g_str))
        out[target] = fit_predict_config(
            train.copy().reset_index(drop=True),
            pred,
            y,
            sub.copy().reset_index(drop=True),
            sub_pred,
            target,
            cfg,
        )
    out[TARGETS] = out[TARGETS].clip(1e-5, 1 - 1e-5)
    out.to_csv(OUT / "submission_hybrid_0p594_cross_target.csv", index=False)
    return out


def main() -> None:
    train = pd.read_parquet(OUT / "train_deep_features.parquet")
    train = train.sort_values(KEY).reset_index(drop=True)
    pred = current_oof()
    nested, selected_folds, nested_pred = nested_eval(train, pred)
    guardrail = half_subject_guardrail(train, pred)
    selected = full_train_choice(train, pred, guardrail)
    nested.to_csv(OUT / "current_0p594_cross_target_nested_results.csv", index=False)
    selected_folds.to_csv(OUT / "current_0p594_cross_target_nested_selected.csv", index=False)
    np.save(OUT / "current_0p594_cross_target_nested_oof.npy", nested_pred)
    guardrail.to_csv(OUT / "current_0p594_cross_target_half_subject.csv", index=False)
    selected.to_csv(OUT / "current_0p594_cross_target_full_selected.csv", index=False)
    out = apply_submission(train, pred, selected)

    estimate = pd.read_csv(OUT / "hybrid_0p594_sleep_proxy_q23foldsafe_cv_estimate.csv")
    nested_losses = nested[nested["model"].eq("nested_cross_target")].iloc[0]
    for row in selected.itertuples(index=False):
        if str(row.config) == "identity":
            continue
        target = str(row.target)
        estimate.loc[estimate["target"].eq(target), "source"] = f"cross_target_{row.config}"
        estimate.loc[estimate["target"].eq(target), "cv_loss"] = float(nested_losses[target])
    estimate.loc[estimate["target"].eq("mean"), "source"] = "hybrid_0p594_cross_target"
    estimate.loc[estimate["target"].eq("mean"), "cv_loss"] = float(
        estimate[estimate["target"].isin(TARGETS)]["cv_loss"].mean()
    )
    estimate.to_csv(OUT / "hybrid_0p594_cross_target_cv_estimate.csv", index=False)

    print(nested.round(6).to_string(index=False))
    print("\nHalf-subject")
    print(guardrail.round(6).to_string(index=False))
    print("\nFull selected")
    print(selected.round(6).to_string(index=False))
    print("\nEstimate")
    print(estimate.to_string(index=False))
    print("wrote", OUT / "submission_hybrid_0p594_cross_target.csv", out.shape)


if __name__ == "__main__":
    main()
