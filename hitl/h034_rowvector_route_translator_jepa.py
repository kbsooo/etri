#!/usr/bin/env python3
"""H034: row-vector route translator HS-JEPA.

H033 showed that H012-vs-sibling failures are learnable, but direct cellwise
negative-cost edits are not action-safe. H034 moves the translator one level up:
the atomic object is a row's 7-target route pattern, not an independent cell.

The experiment has two falsifiable parts:

1. Can row-vector route features predict H032 sibling margins?
2. If yes, do row-level rollback/add/whole-vector actions clear H012-relative
   public-free stress better than H033 cell edits?
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import importlib.util
import re
import shutil
import sys
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
HITL = ROOT / "hitl"
OUT = HITL / "h034_rowvector_route_translator_jepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1.0e-6

E247 = "submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv"
H012 = "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"
H012_LB = 0.5681234831

H012_DIR = HITL / "h012_public_equation_jepa_jackpot"
H032_DIR = HITL / "h032_h012_phase_translator_jepa"
H033_DIR = HITL / "h033_phase_lock_contrast_jepa"


@dataclass(frozen=True)
class RowActionSpec:
    family: str
    op: str
    k: int
    alpha: float
    row_score: str
    target_mask: str


def import_module(path: Path, name: str) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def safe_id(text: str, limit: int = 120) -> str:
    clean = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(text)).strip("_")
    return clean[:limit].strip("_")


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def logit(x: np.ndarray) -> np.ndarray:
    p = clip_prob(x)
    return np.log(p / (1.0 - p))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(x, dtype=np.float64)))


def short_hash(frame: pd.DataFrame) -> str:
    return hashlib.sha1(np.round(frame[TARGETS].to_numpy(dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def rankdata(x: np.ndarray) -> np.ndarray:
    return pd.Series(np.asarray(x, dtype=np.float64)).rank(method="average").to_numpy(dtype=np.float64)


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 3:
        return float("nan")
    ra = rankdata(a)
    rb = rankdata(b)
    if np.std(ra) < 1.0e-12 or np.std(rb) < 1.0e-12:
        return float("nan")
    return float(np.corrcoef(ra, rb)[0, 1])


def pairwise_accuracy(y: np.ndarray, pred: np.ndarray) -> float:
    ok = 0
    total = 0
    for i in range(len(y)):
        for j in range(i + 1, len(y)):
            dy = y[i] - y[j]
            dp = pred[i] - pred[j]
            if abs(dy) < 1.0e-12:
                continue
            total += 1
            ok += int(np.sign(dy) == np.sign(dp))
    return float(ok / total) if total else float("nan")


def md_table(frame: pd.DataFrame, n: int = 30) -> str:
    if frame.empty:
        return "_empty_"
    view = frame.head(n).copy()
    for col in view.columns:
        if pd.api.types.is_float_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else f"{float(x):.9f}")
    view = view.fillna("")
    headers = [str(c) for c in view.columns]
    rows = [[str(v).replace("\n", " ") for v in row] for row in view.to_numpy()]
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    out.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(out)


def load_h024() -> object:
    return import_module(HITL / "h024_action_health_decoder_jepa.py", "h024_h034")


def load_base(h024: object) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray, np.ndarray, np.ndarray]:
    h012_df = h024.load_sub(H012)
    sample = h012_df[KEYS].copy()
    e247_df = h024.load_sub(E247, sample)
    q = np.zeros_like(h012_df[TARGETS].to_numpy(dtype=np.float64))
    posterior = pd.read_csv(H012_DIR / "h012_cell_posterior.csv")
    target_to_i = {t: i for i, t in enumerate(TARGETS)}
    for rec in posterior.to_dict("records"):
        q[int(rec["row"]), target_to_i[str(rec["target"])]] = float(rec["posterior_prob"])
    if np.any(q <= 0):
        raise ValueError("incomplete H012 posterior")
    return (
        sample,
        h012_df,
        e247_df[TARGETS].to_numpy(dtype=np.float64),
        h012_df[TARGETS].to_numpy(dtype=np.float64),
        clip_prob(q),
    )


def load_phase_scores() -> pd.DataFrame:
    scores = pd.read_csv(H032_DIR / "h032_phase_candidate_scores.csv")
    scores = scores[scores["candidate_id"] != "anchor_h012_actual"].copy()
    scores = scores.dropna(subset=["pre_state_margin_vs_h012_pred"])
    return scores.sort_values("pre_state_margin_vs_h012_pred").reset_index(drop=True)


def target_mask(mask_name: str, row: pd.Series | None = None) -> np.ndarray:
    if mask_name == "all":
        names = TARGETS
    elif mask_name == "Q":
        names = ["Q1", "Q2", "Q3"]
    elif mask_name == "S":
        names = ["S1", "S2", "S3", "S4"]
    elif mask_name == "S124":
        names = ["S1", "S2", "S4"]
    elif mask_name == "S2S4":
        names = ["S2", "S4"]
    elif mask_name == "Q3S":
        names = ["Q3", "S1", "S2", "S3", "S4"]
    elif mask_name == "changed":
        if row is None:
            raise ValueError("row is required for changed mask")
        names = [t for t in TARGETS if bool(row[f"support_{t}"])]
    elif mask_name == "outside":
        if row is None:
            raise ValueError("row is required for outside mask")
        names = [t for t in TARGETS if not bool(row[f"support_{t}"])]
    else:
        raise KeyError(mask_name)
    out = np.zeros(len(TARGETS), dtype=bool)
    for t in names:
        out[TARGETS.index(t)] = True
    return out


def build_row_state(coefs: pd.DataFrame, cells: pd.DataFrame) -> pd.DataFrame:
    coefs = coefs.copy()
    cells = cells.copy()
    rows: list[dict[str, Any]] = []
    for row_id, part in coefs.groupby("row"):
        part = part.sort_values("target_i")
        rec: dict[str, Any] = {"row": int(row_id)}
        for _, c in part.iterrows():
            t = str(c["target"])
            rec[f"support_{t}"] = bool(c["support"])
            rec[f"rollback_beta_{t}"] = float(c["rollback_beta"])
            rec[f"over_beta_{t}"] = float(c["over_beta"])
            rec[f"add_beta_{t}"] = float(c["add_beta"])
            rec[f"neg_cost_{t}"] = float(c["negative_op_cost"])
            rec[f"gain_{t}"] = float(c.get("posterior_gain", 0.0))
            rec[f"mem_dis_{t}"] = bool(c.get("memory_disagrees_h012", False))
        support = part["support"].to_numpy(dtype=bool)
        rec["support_count"] = int(support.sum())
        rec["outside_count"] = int((~support).sum())
        rec["rollback_sum_support"] = float(part.loc[part["support"], "rollback_beta"].sum())
        rec["rollback_neg_sum_support"] = float(part.loc[part["support"], "rollback_beta"].clip(upper=0).sum())
        rec["add_sum_outside"] = float(part.loc[~part["support"], "add_beta"].sum())
        rec["add_neg_sum_outside"] = float(part.loc[~part["support"], "add_beta"].clip(upper=0).sum())
        rec["over_neg_sum_support"] = float(part.loc[part["support"], "over_beta"].clip(upper=0).sum())
        rec["neg_cost_sum"] = float(part["negative_op_cost"].sum())
        rec["lock_cost_sum"] = float(part["lock_cost"].sum())
        rec["posterior_gain_sum"] = float(part.get("posterior_gain", pd.Series(0.0, index=part.index)).sum())
        rec["memory_disagree_count"] = int(part.get("memory_disagrees_h012", pd.Series(False, index=part.index)).fillna(False).sum())
        rec["identity_mean"] = float(part.get("identity_phase_score", pd.Series(0.0, index=part.index)).mean())
        rec["route_mean"] = float(part.get("route_translator_score", pd.Series(0.0, index=part.index)).mean())
        rec["joint_vector_mean"] = float(part.get("score_joint_vector_cell", pd.Series(0.0, index=part.index)).mean())
        rec["public_row_subset_mean"] = float(part.get("score_public_row_subset", pd.Series(0.0, index=part.index)).mean())
        rec["support_code"] = "".join("1" if x else "0" for x in support)
        rows.append(rec)
    out = pd.DataFrame(rows).sort_values("row").reset_index(drop=True)
    # Add H032 row reliability if present.
    rel = (
        cells.groupby("row")
        .agg(
            h032_row_full_reliability_q=("row_full_reliability_q", "mean"),
            h032_private_safe=("private_safe_score", "mean"),
            h032_cell_score=("cell_score", "mean"),
        )
        .reset_index()
    )
    out = out.merge(rel, on="row", how="left")
    out.to_csv(OUT / "h034_row_route_state.csv", index=False)
    return out


def route_features_from_prob(
    prob: np.ndarray,
    h012_prob: np.ndarray,
    e247_prob: np.ndarray,
    q: np.ndarray,
    coefs: pd.DataFrame,
    row_state: pd.DataFrame,
    meta: dict[str, Any] | None = None,
) -> dict[str, float | str]:
    z = logit(prob)
    z_h012 = logit(h012_prob)
    z_e247 = logit(e247_prob)
    z_q = logit(q)
    dz = z - z_h012
    h012_dir = z_h012 - z_e247
    support = np.abs(h012_dir) > 1.0e-8
    direction = np.sign(h012_dir)
    rollback = np.zeros_like(dz)
    over = np.zeros_like(dz)
    add = np.zeros_like(dz)
    rollback[support] = np.maximum(0.0, -direction[support] * dz[support])
    over[support] = np.maximum(0.0, direction[support] * dz[support])
    add[~support] = np.abs(dz[~support])
    changed = np.abs(dz) > 1.0e-8
    row_changed = changed.any(axis=1)
    row_rollback = rollback.sum(axis=1)
    row_over = over.sum(axis=1)
    row_add = add.sum(axis=1)
    row_n_changed = changed.sum(axis=1)
    row_n_rollback = (rollback > 1.0e-8).sum(axis=1)
    row_n_add = (add > 1.0e-8).sum(axis=1)
    row_mixed = ((row_n_rollback > 0) & (row_n_add > 0)).astype(float)
    co = coefs.sort_values(["row", "target_i"]).copy()
    rb = co["rollback_beta"].to_numpy(dtype=np.float64).reshape(prob.shape)
    ob = co["over_beta"].to_numpy(dtype=np.float64).reshape(prob.shape)
    ab = co["add_beta"].to_numpy(dtype=np.float64).reshape(prob.shape)
    neg = co["negative_op_cost"].to_numpy(dtype=np.float64).reshape(prob.shape)

    feat: dict[str, float | str] = {}
    if meta:
        for k, v in meta.items():
            if isinstance(v, (int, float, np.integer, np.floating)):
                feat[f"meta_{k}"] = float(v)
    feat["changed_cells"] = float(changed.sum())
    feat["changed_rows"] = float(row_changed.sum())
    feat["max_abs_prob_vs_h012"] = float(np.max(np.abs(prob - h012_prob)))
    feat["mean_abs_prob_vs_h012"] = float(np.mean(np.abs(prob - h012_prob)))
    feat["mean_abs_logit_vs_h012"] = float(np.mean(np.abs(dz)))
    feat["rollback_sum"] = float(rollback.sum())
    feat["over_sum"] = float(over.sum())
    feat["add_sum"] = float(add.sum())
    feat["rollback_beta_weighted"] = float((rollback * rb).sum())
    feat["over_beta_weighted"] = float((over * ob).sum())
    feat["add_beta_weighted"] = float((add * ab).sum())
    feat["negative_cost_weighted"] = float((np.abs(dz) * neg).sum())
    feat["q_bce_delta_vs_h012"] = float(np.mean(-(q * np.log(clip_prob(prob)) + (1 - q) * np.log(clip_prob(1 - prob))) + (q * np.log(clip_prob(h012_prob)) + (1 - q) * np.log(clip_prob(1 - h012_prob)))))
    for name, arr in [("row_changed", row_changed.astype(float)), ("row_rollback", row_rollback), ("row_over", row_over), ("row_add", row_add), ("row_mixed", row_mixed)]:
        feat[f"{name}_mean"] = float(arr.mean())
        feat[f"{name}_sum"] = float(arr.sum())
        feat[f"{name}_p90"] = float(np.quantile(arr, 0.90))
        feat[f"{name}_p99"] = float(np.quantile(arr, 0.99))
    for n in range(1, 8):
        feat[f"rows_changed_eq{n}"] = float(np.sum(row_n_changed == n))
        feat[f"rows_rollback_eq{n}"] = float(np.sum(row_n_rollback == n))
        feat[f"rows_add_eq{n}"] = float(np.sum(row_n_add == n))
    for group_name, names in {
        "Q": ["Q1", "Q2", "Q3"],
        "S": ["S1", "S2", "S3", "S4"],
        "S124": ["S1", "S2", "S4"],
        "S2S4": ["S2", "S4"],
        "Q3S": ["Q3", "S1", "S2", "S3", "S4"],
    }.items():
        idx = [TARGETS.index(t) for t in names]
        feat[f"{group_name}_rollback_sum"] = float(rollback[:, idx].sum())
        feat[f"{group_name}_add_sum"] = float(add[:, idx].sum())
        feat[f"{group_name}_changed_cells"] = float(changed[:, idx].sum())
        feat[f"{group_name}_rows_changed"] = float(changed[:, idx].any(axis=1).sum())
    # Route-state weighted aggregates distinguish row identity from pure target totals.
    row_weight_cols = [
        "rollback_neg_sum_support",
        "add_neg_sum_outside",
        "neg_cost_sum",
        "lock_cost_sum",
        "posterior_gain_sum",
        "memory_disagree_count",
        "identity_mean",
        "route_mean",
        "joint_vector_mean",
        "public_row_subset_mean",
    ]
    rs = row_state.sort_values("row")
    for col in row_weight_cols:
        vals = rs[col].to_numpy(dtype=np.float64)
        feat[f"row_changed_x_{col}"] = float((row_changed.astype(float) * vals).sum())
        feat[f"row_add_x_{col}"] = float((row_add * vals).sum())
        feat[f"row_rollback_x_{col}"] = float((row_rollback * vals).sum())
    return feat


def build_route_dataset(
    h024: object,
    scores: pd.DataFrame,
    sample: pd.DataFrame,
    h012_prob: np.ndarray,
    e247_prob: np.ndarray,
    q: np.ndarray,
    coefs: pd.DataFrame,
    row_state: pd.DataFrame,
) -> tuple[pd.DataFrame, np.ndarray, pd.DataFrame]:
    rows: list[dict[str, Any]] = []
    y = scores["pre_state_margin_vs_h012_pred"].to_numpy(dtype=np.float64)
    for rec in scores.to_dict("records"):
        prob = h024.load_sub(str(rec["resolved_path"]), sample)[TARGETS].to_numpy(dtype=np.float64)
        meta = {
            "k": float(rec.get("k", 0)),
            "alpha": float(rec.get("alpha", 0)),
            "changed_cells_vs_h012": float(rec.get("changed_cells_vs_h012", 0)),
            "phase_loss_margin_vs_h012": float(rec.get("phase_loss_margin_vs_h012", 0)),
            "proj_e247_to_h012": float(rec.get("proj_e247_to_h012", 0)),
            "cos_e247_to_h012": float(rec.get("cos_e247_to_h012", 0)),
        }
        feat = route_features_from_prob(prob, h012_prob, e247_prob, q, coefs, row_state, meta)
        feat.update(
            {
                "file": rec["file"],
                "resolved_path": rec["resolved_path"],
                "candidate_id": rec["candidate_id"],
                "score_name": rec["score_name"],
                "target_group": rec["target_group"],
                "curve": rec["curve"],
            }
        )
        rows.append(feat)
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "h034_route_training_features.csv", index=False)
    return df, y, scores


def numeric_cols(frame: pd.DataFrame) -> list[str]:
    blocked = {"file", "resolved_path", "candidate_id", "score_name", "target_group", "curve"}
    return [c for c in frame.columns if c not in blocked and pd.api.types.is_numeric_dtype(frame[c])]


def fit_ridge(x_train: np.ndarray, y_train: np.ndarray, x_pred: np.ndarray, alpha: float) -> tuple[np.ndarray, Ridge, StandardScaler]:
    scaler = StandardScaler(with_mean=True, with_std=True)
    xs = scaler.fit_transform(x_train)
    xp = scaler.transform(x_pred)
    model = Ridge(alpha=alpha, fit_intercept=True, solver="lsqr", max_iter=5000, random_state=20260602)
    model.fit(xs, y_train)
    return model.predict(xp), model, scaler


def cv_route_models(features: pd.DataFrame, y: np.ndarray, meta: pd.DataFrame, cols: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    x = features[cols].fillna(0.0).to_numpy(dtype=np.float64)
    fold_defs: list[tuple[str, np.ndarray]] = []
    for col in ["score_name", "target_group", "curve"]:
        for val in sorted(meta[col].dropna().unique()):
            mask = meta[col].astype(str).eq(str(val)).to_numpy()
            if 25 <= int(mask.sum()) <= len(meta) - 25:
                fold_defs.append((f"{col}={val}", mask))
    rng = np.random.default_rng(20260602)
    assignment = rng.integers(0, 5, size=len(meta))
    for fold in range(5):
        fold_defs.append((f"random5={fold}", assignment == fold))

    model_specs: list[tuple[str, float | None]] = [("ridge_1", 1.0), ("ridge_10", 10.0), ("ridge_100", 100.0), ("et_route", None)]
    rows: list[dict[str, Any]] = []
    pred_rows: list[dict[str, Any]] = []
    for model_name, alpha in model_specs:
        fold_pred = np.full(len(y), np.nan, dtype=np.float64)
        for fold_name, test_mask in fold_defs:
            train_mask = ~test_mask
            if alpha is None:
                model = ExtraTreesRegressor(
                    n_estimators=350,
                    max_depth=8,
                    min_samples_leaf=8,
                    max_features=0.75,
                    random_state=20260602,
                    n_jobs=-1,
                )
                model.fit(x[train_mask], y[train_mask])
                pred = model.predict(x[test_mask])
            else:
                pred, _, _ = fit_ridge(x[train_mask], y[train_mask], x[test_mask], float(alpha))
            fold_pred[test_mask] = pred
            yt = y[test_mask]
            rows.append(
                {
                    "model": model_name,
                    "fold": fold_name,
                    "n_test": int(test_mask.sum()),
                    "mae": float(np.mean(np.abs(pred - yt))),
                    "rmse": float(np.sqrt(np.mean((pred - yt) ** 2))),
                    "spearman": spearman(yt, pred),
                    "pair_acc": pairwise_accuracy(yt, pred),
                    "pred_min": float(np.min(pred)),
                    "pred_max": float(np.max(pred)),
                }
            )
        valid = np.isfinite(fold_pred)
        rows.append(
            {
                "model": model_name,
                "fold": "__all_oof__",
                "n_test": int(valid.sum()),
                "mae": float(np.mean(np.abs(fold_pred[valid] - y[valid]))),
                "rmse": float(np.sqrt(np.mean((fold_pred[valid] - y[valid]) ** 2))),
                "spearman": spearman(y[valid], fold_pred[valid]),
                "pair_acc": pairwise_accuracy(y[valid], fold_pred[valid]),
                "pred_min": float(np.min(fold_pred[valid])),
                "pred_max": float(np.max(fold_pred[valid])),
            }
        )
        for rec, pred in zip(meta.to_dict("records"), fold_pred):
            pred_rows.append({"model": model_name, "candidate_id": rec["candidate_id"], "oof_route_margin_pred": pred})
    cv = pd.DataFrame(rows)
    preds = pd.DataFrame(pred_rows)
    cv.to_csv(OUT / "h034_route_cv.csv", index=False)
    preds.to_csv(OUT / "h034_route_oof_predictions.csv", index=False)
    return cv, preds


def fit_route_predictors(features: pd.DataFrame, y: np.ndarray, cols: list[str]) -> dict[str, Any]:
    x = features[cols].fillna(0.0).to_numpy(dtype=np.float64)
    _, ridge, scaler = fit_ridge(x, y, x, 100.0)
    et = ExtraTreesRegressor(
        n_estimators=500,
        max_depth=9,
        min_samples_leaf=6,
        max_features=0.75,
        random_state=20260603,
        n_jobs=-1,
    )
    et.fit(x, y)
    imp = pd.DataFrame({"feature": cols, "et_importance": et.feature_importances_}).sort_values("et_importance", ascending=False)
    scale = np.where(scaler.scale_ < 1.0e-12, 1.0, scaler.scale_)
    beta = pd.DataFrame({"feature": cols, "ridge_beta": ridge.coef_.astype(np.float64) / scale}).sort_values("ridge_beta")
    imp.merge(beta, on="feature", how="outer").to_csv(OUT / "h034_route_feature_importance.csv", index=False)
    return {"ridge": ridge, "scaler": scaler, "et": et}


def write_submission(template: pd.DataFrame, prob: np.ndarray, candidate_id: str) -> Path:
    out = template.copy()
    out[TARGETS] = clip_prob(prob)
    path = OUT / f"submission_h034_{safe_id(candidate_id)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def row_order(row_state: pd.DataFrame, row_score: str) -> pd.DataFrame:
    ascending = True
    if row_score == "rollback_relief":
        key = "rollback_neg_sum_support"
    elif row_score == "add_relief":
        key = "add_neg_sum_outside"
    elif row_score == "neg_total":
        key = "neg_cost_sum"
    elif row_score == "memory_conflict":
        key = "memory_disagree_count"
        ascending = False
    elif row_score == "identity":
        key = "identity_mean"
        ascending = False
    elif row_score == "public_row_subset":
        key = "public_row_subset_mean"
        ascending = False
    elif row_score == "joint_vector":
        key = "joint_vector_mean"
        ascending = False
    elif row_score == "lock_cost_high":
        key = "lock_cost_sum"
        ascending = False
    else:
        raise KeyError(row_score)
    return row_state.sort_values(key, ascending=ascending).reset_index(drop=True)


def action_specs() -> list[RowActionSpec]:
    specs: list[RowActionSpec] = []
    for row_score in ["add_relief", "neg_total", "memory_conflict", "joint_vector", "public_row_subset"]:
        for k in [1, 2, 3, 5, 8, 13, 21, 34]:
            for alpha in [0.08, 0.16, 0.28, 0.45]:
                specs.append(RowActionSpec("row_add_complement", "add", k, alpha, row_score, "outside"))
    for row_score in ["rollback_relief", "neg_total", "lock_cost_high", "memory_conflict"]:
        for k in [1, 2, 3, 5, 8, 13, 21, 34]:
            for alpha in [0.08, 0.16, 0.28, 0.45]:
                specs.append(RowActionSpec("row_rollback_support", "rollback", k, alpha, row_score, "changed"))
    for row_score in ["neg_total", "memory_conflict", "joint_vector"]:
        for k in [1, 2, 3, 5, 8, 13, 21]:
            for alpha in [0.08, 0.16, 0.28]:
                specs.append(RowActionSpec("row_combo_route", "rollback_add", k, alpha, row_score, "all"))
    for row_score in ["add_relief", "memory_conflict", "joint_vector"]:
        for k in [1, 2, 3, 5, 8, 13]:
            for alpha in [0.05, 0.10, 0.18]:
                specs.append(RowActionSpec("row_whole_q", "whole_q", k, alpha, row_score, "all"))
    return specs


def materialize_row_candidates(
    template: pd.DataFrame,
    h012_prob: np.ndarray,
    e247_prob: np.ndarray,
    q: np.ndarray,
    row_state: pd.DataFrame,
    predictors: dict[str, Any],
    train_cols: list[str],
    coefs: pd.DataFrame,
) -> pd.DataFrame:
    z_h012 = logit(h012_prob)
    z_e247 = logit(e247_prob)
    z_q = logit(q)
    h012_dir = z_h012 - z_e247
    q_dir = z_q - z_e247
    rows: list[dict[str, Any]] = []
    seen = {hashlib.sha1(np.round(h012_prob, 12).tobytes()).hexdigest()[:12]}

    for spec in action_specs():
        ordered = row_order(row_state, spec.row_score).head(spec.k)
        if ordered.empty:
            continue
        z = z_h012.copy()
        touched: list[tuple[int, int]] = []
        for _, rr in ordered.iterrows():
            r = int(rr["row"])
            if spec.op == "rollback":
                mask = target_mask(spec.target_mask, rr)
                idx = np.flatnonzero(mask)
                z[r, idx] = z_h012[r, idx] - spec.alpha * h012_dir[r, idx]
                touched.extend((r, int(i)) for i in idx)
            elif spec.op == "add":
                mask = target_mask(spec.target_mask, rr)
                idx = np.flatnonzero(mask)
                z[r, idx] = z_h012[r, idx] + spec.alpha * q_dir[r, idx]
                touched.extend((r, int(i)) for i in idx)
            elif spec.op == "rollback_add":
                s_mask = target_mask("changed", rr)
                o_mask = target_mask("outside", rr)
                s_idx = np.flatnonzero(s_mask)
                o_idx = np.flatnonzero(o_mask)
                z[r, s_idx] = z_h012[r, s_idx] - spec.alpha * h012_dir[r, s_idx]
                z[r, o_idx] = z_h012[r, o_idx] + spec.alpha * q_dir[r, o_idx]
                touched.extend((r, int(i)) for i in np.concatenate([s_idx, o_idx]))
            elif spec.op == "whole_q":
                idx = np.arange(len(TARGETS))
                z[r, idx] = z_h012[r, idx] + spec.alpha * (z_q[r, idx] - z_h012[r, idx])
                touched.extend((r, int(i)) for i in idx)
            else:
                raise KeyError(spec.op)
        if not touched:
            continue
        prob = sigmoid(z)
        digest = hashlib.sha1(np.round(prob, 12).tobytes()).hexdigest()[:12]
        if digest in seen:
            continue
        seen.add(digest)
        candidate_id = f"{spec.family}_{spec.op}_{spec.row_score}_{spec.target_mask}_r{spec.k}_a{spec.alpha:g}"
        path = write_submission(template, prob, candidate_id)
        feat = route_features_from_prob(prob, h012_prob, e247_prob, q, coefs, row_state)
        x = pd.DataFrame([feat]).reindex(columns=train_cols).fillna(0.0).to_numpy(dtype=np.float64)
        ridge_pred = float(predictors["ridge"].predict(predictors["scaler"].transform(x))[0])
        et_pred = float(predictors["et"].predict(x)[0])
        diff = np.abs(prob - h012_prob)
        rows.append(
            {
                "file": f"hitl/h034_rowvector_route_translator_jepa/{path.name}",
                "resolved_path": str(path),
                "candidate_id": candidate_id,
                "family": spec.family,
                "op": spec.op,
                "row_score": spec.row_score,
                "target_mask": spec.target_mask,
                "k_rows": spec.k,
                "alpha": spec.alpha,
                "changed_cells_vs_h012": int(np.sum(diff > 1.0e-6)),
                "changed_rows_vs_h012": int(np.sum(np.any(diff > 1.0e-6, axis=1))),
                "max_abs_prob_vs_h012": float(np.max(diff)),
                "mean_abs_prob_vs_h012": float(np.mean(diff)),
                "route_ridge_margin_pred": ridge_pred,
                "route_et_margin_pred": et_pred,
                "route_mean_margin_pred": float((ridge_pred + et_pred) / 2.0),
                "touched_rows": ",".join(str(int(x)) for x in ordered["row"].tolist()),
            }
        )
    out = pd.DataFrame(rows)
    if not out.empty:
        out = out.sort_values(["route_mean_margin_pred", "changed_cells_vs_h012"]).reset_index(drop=True)
    out.to_csv(OUT / "h034_generated_rowroute_candidates.csv", index=False)
    return out


def h024_feature_table(h024: object, variants: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, list[str]]]:
    known = h024.read_public_observations()
    refs = h024.build_reference_pack()
    known_rows = [
        {
            "file": rec["file"],
            "resolved_path": str(h024.locate(rec["file"]) or rec["file"]),
            "source": "known_public",
        }
        for rec in known.to_dict("records")
    ]
    var_rows = variants[["file", "resolved_path", "candidate_id", "family"]].copy()
    var_rows["source"] = "h034_rowroute"
    pool = pd.concat([pd.DataFrame(known_rows), var_rows], ignore_index=True).drop_duplicates("file", keep="last")
    features = h024.build_feature_table(pool, refs)
    features.to_csv(OUT / "h034_h024_features.csv", index=False)
    known_features = known[["file", "public_lb"]].merge(features, on="file", how="inner")
    blocked = {
        "file",
        "resolved_path",
        "source",
        "pool_file",
        "pool_resolved_path",
        "pool_candidate_id",
        "pool_family",
        "pool_source",
        "pool_known_public_lb",
        "known_public_lb",
        "public_lb",
    }
    cols = h024.numeric_feature_cols(known_features, blocked)
    return known, features, h024.feature_sets(cols)


def ridge_predict_one(h024: object, known: pd.DataFrame, features: pd.DataFrame, cols: list[str], alpha: float) -> np.ndarray:
    known_features = known[["file", "public_lb"]].merge(features, on="file", how="inner")
    return h024.ridge_fit_predict(
        known_features[cols].to_numpy(dtype=np.float64),
        known_features["public_lb"].to_numpy(dtype=np.float64),
        features[cols].to_numpy(dtype=np.float64),
        alpha,
    )


def score_candidates(h024: object, variants: pd.DataFrame, known: pd.DataFrame, features: pd.DataFrame, cols_by_set: dict[str, list[str]]) -> pd.DataFrame:
    known_no_h012 = known[known["file"] != H012].copy().reset_index(drop=True)
    model_no_h012, loo_no_h012 = h024.evaluate_known_models(known_no_h012[["file", "public_lb"]], features, cols_by_set)
    model_full, loo_full = h024.evaluate_known_models(known[["file", "public_lb"]], features, cols_by_set)
    model_no_h012.to_csv(OUT / "h034_pre_h012_h024_model_scores.csv", index=False)
    loo_no_h012.to_csv(OUT / "h034_pre_h012_h024_loo_predictions.csv", index=False)
    model_full.to_csv(OUT / "h034_full_h024_model_scores.csv", index=False)
    loo_full.to_csv(OUT / "h034_full_h024_loo_predictions.csv", index=False)

    pred_cols: dict[str, np.ndarray] = {}
    for set_name, alpha in [("state", 100.0), ("state", 10.0), ("geometry", 100.0), ("geometry", 10.0)]:
        if set_name in cols_by_set:
            pred_cols[f"pre_{set_name}_a{alpha:g}"] = ridge_predict_one(h024, known_no_h012, features, cols_by_set[set_name], alpha)
    for set_name, alpha in [("state", 100.0), ("geometry", 100.0)]:
        if set_name in cols_by_set:
            pred_cols[f"full_{set_name}_a{alpha:g}"] = ridge_predict_one(h024, known, features, cols_by_set[set_name], alpha)

    pred_frame = features[["file"]].copy()
    for key, pred in pred_cols.items():
        pred_frame[key] = pred
    pred_frame.to_csv(OUT / "h034_direct_decoder_predictions.csv", index=False)
    scored = variants.merge(pred_frame, on="file", how="left")
    h012_pred = pred_frame[pred_frame["file"].eq(H012)]
    h012_pre_state = H012_LB
    if not h012_pred.empty:
        h012_cols = [c for c in h012_pred.columns if c.startswith("pre_state")]
        if h012_cols:
            h012_pre_state = float(h012_pred[h012_cols].mean(axis=1).iloc[0])
    scored["pre_state_mean"] = scored[[c for c in scored.columns if c.startswith("pre_state")]].mean(axis=1)
    scored["pre_geometry_mean"] = scored[[c for c in scored.columns if c.startswith("pre_geometry")]].mean(axis=1)
    scored["full_state_mean"] = scored[[c for c in scored.columns if c.startswith("full_state")]].mean(axis=1)
    scored["full_geometry_mean"] = scored[[c for c in scored.columns if c.startswith("full_geometry")]].mean(axis=1)
    scored["pre_state_margin_vs_h012_pred"] = scored["pre_state_mean"] - h012_pre_state
    scored["h034_action_score"] = (
        scored["pre_state_mean"].fillna(0.60)
        + 0.20 * np.maximum(scored["pre_geometry_mean"].fillna(0.60) - H012_LB, -0.03)
        + 0.16 * np.maximum(scored["route_mean_margin_pred"].fillna(0.04), -0.003)
        + 0.000025 * scored["changed_cells_vs_h012"].fillna(0) / 50.0
        + 0.006 * np.maximum(scored["max_abs_prob_vs_h012"].fillna(0) - 0.10, 0)
    )
    scored = scored.sort_values(["h034_action_score", "pre_state_mean", "route_mean_margin_pred"]).reset_index(drop=True)
    scored.to_csv(OUT / "h034_candidate_scores.csv", index=False)
    return scored


def public_perm_stress(h024: object, selected: pd.Series, known: pd.DataFrame, features: pd.DataFrame, cols_by_set: dict[str, list[str]]) -> pd.DataFrame:
    known_no_h012 = known[known["file"] != H012].copy().reset_index(drop=True)
    null = h024.permutation_stress(
        known_no_h012[["file", "public_lb"]],
        features,
        cols_by_set,
        str(selected["file"]),
        n_perm=300,
    )
    null.to_csv(OUT / "h034_selected_pre_h012_public_perm_stress.csv", index=False)
    return null


def rowperm_stress(selected: pd.Series) -> pd.DataFrame:
    try:
        h026 = import_module(HITL / "h026_public_private_calibration_veto_jepa.py", "h026_h034")
        rt26 = h026.prepare_runtime()
        rowperm = rt26.h025.row_permutation_candidate_stress(
            rt26.action_model,
            rt26.action_cols,
            str(selected["resolved_path"]),
            rt26.h012_prob,
            rt26.test_pcs,
            rt26.sample,
            n_perm=300,
        )
    except Exception as exc:
        rowperm = pd.DataFrame([{"error": repr(exc)}])
    rowperm.to_csv(OUT / "h034_selected_h025_rowperm_stress.csv", index=False)
    return rowperm


def decide(scored: pd.DataFrame, public_perm: pd.DataFrame, rowperm: pd.DataFrame) -> tuple[str, Path | None]:
    if scored.empty:
        return "no_h034_candidates", None
    selected = scored.iloc[0]
    public_perm_p = 1.0
    if not public_perm.empty and "perm_selected_minus_h012" in public_perm.columns:
        public_perm_p = float(np.mean(public_perm["perm_selected_minus_h012"].to_numpy(dtype=np.float64) <= float(selected["pre_state_margin_vs_h012_pred"])))
    rowperm_p = 1.0
    if not rowperm.empty and "perm_top1200_sum" in rowperm.columns:
        rowperm_p = float(np.mean(rowperm["perm_top1200_sum"].to_numpy(dtype=np.float64) >= rowperm["real_top1200_sum"].iloc[0]))
    gate = (
        float(selected["pre_state_margin_vs_h012_pred"]) <= -0.00030
        and float(selected["route_mean_margin_pred"]) <= -0.00050
        and float(selected["changed_cells_vs_h012"]) <= 240
        and float(selected["max_abs_prob_vs_h012"]) <= 0.14
        and public_perm_p <= 0.25
        and rowperm_p <= 0.35
    )
    if not gate:
        return "diagnostic_only_no_rowroute_action_clears_stress", None
    src = Path(str(selected["resolved_path"]))
    dst = ROOT / f"submission_h034_rowroute_{safe_id(str(selected['candidate_id']), 72)}_uploadsafe.csv"
    shutil.copyfile(src, dst)
    return "promote_h034_rowroute_big_bet", dst


def write_report(
    cv: pd.DataFrame,
    candidates: pd.DataFrame,
    public_perm: pd.DataFrame,
    rowperm: pd.DataFrame,
    decision: str,
    promoted: Path | None,
) -> None:
    all_oof = cv[cv["fold"].eq("__all_oof__")].sort_values("mae")
    selected = candidates.iloc[0] if not candidates.empty else None
    lines = [
        "# H034 Row-Vector Route Translator HS-JEPA\n\n",
        "## Question\n\n",
        "H033 killed independent-cell phase-lock editing. H034 asks whether H012 is instead locked at the row-vector route level: a row's 7-target action pattern is the atomic state.\n\n",
        "## Route Model Health\n\n",
        md_table(all_oof, 8) + "\n\n",
        "## Top Candidate Actions\n\n",
    ]
    keep = [
        "candidate_id",
        "family",
        "op",
        "row_score",
        "target_mask",
        "k_rows",
        "alpha",
        "changed_cells_vs_h012",
        "max_abs_prob_vs_h012",
        "route_mean_margin_pred",
        "pre_state_mean",
        "pre_state_margin_vs_h012_pred",
        "pre_geometry_mean",
        "h034_action_score",
        "file",
    ]
    lines.append(md_table(candidates[[c for c in keep if c in candidates.columns]], 24) + "\n\n")
    lines.append("## Stress\n\n")
    lines.append(f"- decision: `{decision}`\n")
    lines.append(f"- promoted path: `{promoted if promoted is not None else 'none'}`\n")
    if selected is not None:
        lines.append(f"- selected candidate: `{selected['candidate_id']}`\n")
        lines.append(f"- selected route mean margin prediction: `{float(selected['route_mean_margin_pred']):.9f}`\n")
        lines.append(f"- selected pre-state margin vs H012 prediction: `{float(selected['pre_state_margin_vs_h012_pred']):.9f}`\n")
    if selected is not None and not public_perm.empty and "perm_selected_minus_h012" in public_perm.columns:
        p = float(np.mean(public_perm["perm_selected_minus_h012"].to_numpy(dtype=np.float64) <= float(selected["pre_state_margin_vs_h012_pred"])))
        lines.append(f"- pre-H012 public-score permutation p(lower margin): `{p:.9f}`\n")
    if not rowperm.empty and "perm_top1200_sum" in rowperm.columns:
        p = float(np.mean(rowperm["perm_top1200_sum"].to_numpy(dtype=np.float64) >= rowperm["real_top1200_sum"].iloc[0]))
        lines.append(f"- H025 row-permutation p(higher top1200 gain): `{p:.9f}`\n")
        lines.append(f"- real H025 top1200 gain: `{float(rowperm['real_top1200_sum'].iloc[0]):.9f}`\n")
    elif not rowperm.empty:
        lines.append(f"- H025 row-permutation stress: `{rowperm.iloc[0].to_dict()}`\n")
    lines.append("\n## Interpretation\n\n")
    if selected is None:
        lines.append("No row-route candidates were generated.\n")
    elif promoted is None:
        lines.append(
            "The row-vector route representation is tested as a higher-level translator after H033. "
            "If its route CV is healthy but generated actions still fail H024/H025, then H012 is not editable by first-order row-route actions either. "
            "The next step should be a direct H012-vs-sibling classifier or a combinatorial route solver, not larger row top-k edits.\n"
        )
    else:
        lines.append(
            "A row-route action cleared public-free stress. This is a high-information public test of whether H012 can be extended by row-vector route translation.\n"
        )
    lines.append("\n## Files\n\n")
    for path in [
        OUT / "h034_row_route_state.csv",
        OUT / "h034_route_training_features.csv",
        OUT / "h034_route_cv.csv",
        OUT / "h034_route_oof_predictions.csv",
        OUT / "h034_route_feature_importance.csv",
        OUT / "h034_generated_rowroute_candidates.csv",
        OUT / "h034_candidate_scores.csv",
        OUT / "h034_selected_pre_h012_public_perm_stress.csv",
        OUT / "h034_selected_h025_rowperm_stress.csv",
    ]:
        lines.append(f"- `{path.relative_to(ROOT)}`\n")
    (OUT / "h034_report.md").write_text("".join(lines), encoding="utf-8")


def main() -> None:
    h024 = load_h024()
    sample, h012_df, e247_prob, h012_prob, q = load_base(h024)
    h032_scores = load_phase_scores()
    h032_cells = pd.read_csv(H032_DIR / "h032_cell_phase_state.csv")
    h033_coefs = pd.read_csv(H033_DIR / "h033_cell_phase_lock_coefficients.csv")
    row_state = build_row_state(h033_coefs, h032_cells)
    route_features, y, meta = build_route_dataset(h024, h032_scores, sample, h012_prob, e247_prob, q, h033_coefs, row_state)
    cols = numeric_cols(route_features)
    cv, _ = cv_route_models(route_features, y, meta, cols)
    predictors = fit_route_predictors(route_features, y, cols)
    variants = materialize_row_candidates(h012_df, h012_prob, e247_prob, q, row_state, predictors, cols, h033_coefs)
    if variants.empty:
        candidate_scores = pd.DataFrame()
        public_perm = pd.DataFrame()
        rowperm = pd.DataFrame()
        decision, promoted = "diagnostic_only_no_rowroute_candidates", None
    else:
        known, features, cols_by_set = h024_feature_table(h024, variants)
        candidate_scores = score_candidates(h024, variants, known, features, cols_by_set)
        selected = candidate_scores.iloc[0]
        public_perm = public_perm_stress(h024, selected, known, features, cols_by_set)
        rowperm = rowperm_stress(selected)
        decision, promoted = decide(candidate_scores, public_perm, rowperm)
    pd.DataFrame(
        [
            {
                "decision": decision,
                "n_route_training_rows": int(len(route_features)),
                "n_generated_candidates": int(len(variants)),
                "best_route_model": None if cv.empty else cv[cv["fold"].eq("__all_oof__")].sort_values("mae").iloc[0]["model"],
                "selected_candidate_id": None if candidate_scores.empty else candidate_scores.iloc[0]["candidate_id"],
                "selected_file": None if candidate_scores.empty else candidate_scores.iloc[0]["file"],
                "selected_route_mean_margin_pred": None if candidate_scores.empty else candidate_scores.iloc[0]["route_mean_margin_pred"],
                "selected_pre_state_margin_vs_h012_pred": None if candidate_scores.empty else candidate_scores.iloc[0]["pre_state_margin_vs_h012_pred"],
                "promoted_path": None if promoted is None else str(promoted),
            }
        ]
    ).to_csv(OUT / "h034_decision.csv", index=False)
    write_report(cv, candidate_scores, public_perm, rowperm, decision, promoted)
    print(pd.read_csv(OUT / "h034_decision.csv").to_string(index=False))
    if not candidate_scores.empty:
        print(candidate_scores.head(20).to_string(index=False))
    print(OUT / "h034_report.md")


if __name__ == "__main__":
    main()
