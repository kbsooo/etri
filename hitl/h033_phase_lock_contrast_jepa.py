#!/usr/bin/env python3
"""H033: phase-lock contrastive HS-JEPA.

H032 recovered H012 itself from a dense phase diagram, but no sibling beat it.
H033 turns that negative result into a new learning problem:

    Which exact row-target operations make a near-H012 sibling die?

Instead of sweeping another alpha/k/top-k grid, this script treats the H032
siblings as interventions that break H012 in different cells. It learns a
cell-level phase-lock law from those interventions, then asks whether the law
contains any public-free negative-cost operation that can move H012 itself.
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
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
HITL = ROOT / "hitl"
OUT = HITL / "h033_phase_lock_contrast_jepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1.0e-6

E247 = "submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv"
H012 = "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"
H012_LB = 0.5681234831

H032_DIR = HITL / "h032_h012_phase_translator_jepa"
H012_DIR = HITL / "h012_public_equation_jepa_jackpot"


@dataclass(frozen=True)
class OpSpec:
    op: str
    k: int
    alpha: float
    family: str


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


def short_hash(frame: pd.DataFrame) -> str:
    arr = np.asarray(frame[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def logit(x: np.ndarray) -> np.ndarray:
    p = clip_prob(x)
    return np.log(p / (1.0 - p))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(x, dtype=np.float64)))


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
    return import_module(HITL / "h024_action_health_decoder_jepa.py", "h024_h033")


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
    scores = scores.sort_values("pre_state_margin_vs_h012_pred").reset_index(drop=True)
    return scores


def build_break_matrix(
    h024: object,
    scores: pd.DataFrame,
    sample: pd.DataFrame,
    e247_prob: np.ndarray,
    h012_prob: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, pd.DataFrame, dict[str, np.ndarray]]:
    z_e247 = logit(e247_prob).reshape(-1)
    z_h012 = logit(h012_prob).reshape(-1)
    h012_dir = z_h012 - z_e247
    support = np.abs(h012_dir) > 1.0e-8
    direction = np.sign(h012_dir)
    direction[~support] = 0.0
    n_cell = len(h012_dir)

    rows: list[dict[str, Any]] = []
    x = np.zeros((len(scores), n_cell * 3), dtype=np.float32)
    y = scores["pre_state_margin_vs_h012_pred"].to_numpy(dtype=np.float64)

    for i, rec in enumerate(scores.to_dict("records")):
        prob = h024.load_sub(str(rec["resolved_path"]), sample)[TARGETS].to_numpy(dtype=np.float64)
        dz = logit(prob).reshape(-1) - z_h012
        rollback = np.zeros(n_cell, dtype=np.float32)
        over = np.zeros(n_cell, dtype=np.float32)
        add = np.zeros(n_cell, dtype=np.float32)
        rollback[support] = np.maximum(0.0, -direction[support] * dz[support]).astype(np.float32)
        over[support] = np.maximum(0.0, direction[support] * dz[support]).astype(np.float32)
        add[~support] = np.abs(dz[~support]).astype(np.float32)
        x[i, :n_cell] = rollback
        x[i, n_cell : 2 * n_cell] = over
        x[i, 2 * n_cell :] = add
        rows.append(
            {
                "file": rec["file"],
                "candidate_id": rec["candidate_id"],
                "score_name": rec["score_name"],
                "target_group": rec["target_group"],
                "curve": rec["curve"],
                "k": int(rec["k"]),
                "alpha": float(rec["alpha"]),
                "y_margin": float(y[i]),
                "rollback_sum": float(rollback.sum()),
                "over_sum": float(over.sum()),
                "add_sum": float(add.sum()),
                "n_rollback_cells": int(np.sum(rollback > 1.0e-8)),
                "n_over_cells": int(np.sum(over > 1.0e-8)),
                "n_add_cells": int(np.sum(add > 1.0e-8)),
            }
        )
    meta = pd.DataFrame(rows)
    meta.to_csv(OUT / "h033_break_dataset_meta.csv", index=False)
    parts = {"support": support, "direction": direction, "h012_dir": h012_dir, "z_h012": z_h012, "z_e247": z_e247}
    return x, y, meta, parts


def fit_ridge_predict(x_train: np.ndarray, y_train: np.ndarray, x_pred: np.ndarray, alpha: float) -> tuple[np.ndarray, Ridge, StandardScaler]:
    scaler = StandardScaler(with_mean=True, with_std=True)
    xs = scaler.fit_transform(x_train)
    xp = scaler.transform(x_pred)
    model = Ridge(alpha=alpha, fit_intercept=True, solver="lsqr", max_iter=5000, random_state=20260602)
    model.fit(xs, y_train)
    pred = model.predict(xp)
    return pred, model, scaler


def cv_phase_lock(x: np.ndarray, y: np.ndarray, meta: pd.DataFrame) -> pd.DataFrame:
    alphas = [0.1, 1.0, 10.0, 100.0, 1000.0]
    fold_defs: list[tuple[str, np.ndarray]] = []
    for col in ["score_name", "target_group", "curve"]:
        for val in sorted(meta[col].dropna().unique()):
            mask = meta[col].astype(str).eq(str(val)).to_numpy()
            if 25 <= int(mask.sum()) <= len(meta) - 25:
                fold_defs.append((f"{col}={val}", mask))
    # Deterministic random folds catch pure interpolation even when family folds
    # are too structured.
    rng = np.random.default_rng(20260602)
    assignment = rng.integers(0, 5, size=len(meta))
    for fold in range(5):
        fold_defs.append((f"random5={fold}", assignment == fold))

    rows = []
    for alpha in alphas:
        fold_pred = np.full(len(y), np.nan, dtype=np.float64)
        for name, test_mask in fold_defs:
            train_mask = ~test_mask
            pred, _, _ = fit_ridge_predict(x[train_mask], y[train_mask], x[test_mask], alpha)
            fold_pred[test_mask] = pred
            yt = y[test_mask]
            rows.append(
                {
                    "alpha": alpha,
                    "fold": name,
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
                "alpha": alpha,
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
    cv = pd.DataFrame(rows)
    cv.to_csv(OUT / "h033_phase_lock_cv.csv", index=False)
    return cv


def fit_full_lock_model(x: np.ndarray, y: np.ndarray, alpha: float) -> tuple[np.ndarray, Ridge, StandardScaler]:
    pred, model, scaler = fit_ridge_predict(x, y, x, alpha)
    return pred, model, scaler


def cell_index_frame(cells: pd.DataFrame, parts: dict[str, np.ndarray]) -> pd.DataFrame:
    n_cell = len(parts["support"])
    rows = []
    cells_keyed = cells.copy()
    cells_keyed["cell_id"] = cells_keyed["row"].astype(int) * len(TARGETS) + cells_keyed["target_i"].astype(int)
    keep_cols = [
        "cell_id",
        "row",
        "target",
        "target_i",
        "cell_score",
        "identity_phase_score",
        "memory_conflict_phase_score",
        "route_translator_score",
        "memory_disagrees_h012",
        "memory_agrees_h012",
        "memory_alignment_q",
        "posterior_gain",
        "score_identity_combo",
        "score_joint_vector_cell",
        "score_public_row_subset",
        "h012_abs_logit_delta",
        "q_abs_logit_delta",
        "h012_changed",
    ]
    base = cells_keyed[[c for c in keep_cols if c in cells_keyed.columns]].copy()
    if len(base) != n_cell:
        # H032 cell state is one row per row-target; make the assumption explicit.
        raise ValueError(f"expected {n_cell} cells, got {len(base)}")
    for i in range(n_cell):
        rows.append({"cell_id": i})
    idx = pd.DataFrame(rows).merge(base, on="cell_id", how="left")
    return idx


def coefficient_frame(model: Ridge, scaler: StandardScaler, cells: pd.DataFrame, parts: dict[str, np.ndarray]) -> pd.DataFrame:
    n_cell = len(parts["support"])
    scale = np.where(scaler.scale_ < 1.0e-12, 1.0, scaler.scale_)
    raw_beta = model.coef_.astype(np.float64) / scale
    frame = cell_index_frame(cells, parts)
    frame["rollback_beta"] = raw_beta[:n_cell]
    frame["over_beta"] = raw_beta[n_cell : 2 * n_cell]
    frame["add_beta"] = raw_beta[2 * n_cell :]
    frame["support"] = parts["support"]
    frame["h012_direction"] = parts["direction"]
    frame["lock_cost"] = np.where(frame["support"], frame["rollback_beta"], frame["add_beta"])
    frame["negative_op_cost"] = np.minimum.reduce([frame["rollback_beta"], frame["over_beta"], frame["add_beta"]])
    frame["lock_rank"] = pd.Series(frame["lock_cost"]).rank(method="average", pct=True).to_numpy()
    frame["relief_rank"] = pd.Series(-frame["negative_op_cost"]).rank(method="average", pct=True).to_numpy()
    frame.to_csv(OUT / "h033_cell_phase_lock_coefficients.csv", index=False)
    return frame


def summarize_coefficients(coefs: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    summary = []
    for target, part in coefs.groupby("target"):
        summary.append(
            {
                "target": target,
                "n": len(part),
                "support_rate": float(part["support"].mean()),
                "rollback_beta_mean_support": float(part.loc[part["support"], "rollback_beta"].mean()),
                "rollback_beta_p90_support": float(part.loc[part["support"], "rollback_beta"].quantile(0.90)),
                "add_beta_mean_outside": float(part.loc[~part["support"], "add_beta"].mean()),
                "add_beta_p90_outside": float(part.loc[~part["support"], "add_beta"].quantile(0.90)),
                "negative_rollback_cells": int(((part["support"]) & (part["rollback_beta"] < 0)).sum()),
                "negative_add_cells": int(((~part["support"]) & (part["add_beta"] < 0)).sum()),
                "memory_disagree_rate_support": float(part.loc[part["support"], "memory_disagrees_h012"].fillna(False).mean()),
            }
        )
    by_target = pd.DataFrame(summary).sort_values("target").reset_index(drop=True)
    by_target.to_csv(OUT / "h033_target_phase_lock_summary.csv", index=False)

    top_cols = [
        "row",
        "target",
        "support",
        "lock_cost",
        "rollback_beta",
        "over_beta",
        "add_beta",
        "negative_op_cost",
        "cell_score",
        "identity_phase_score",
        "memory_conflict_phase_score",
        "memory_disagrees_h012",
        "posterior_gain",
        "h012_abs_logit_delta",
    ]
    top = pd.concat(
        [
            coefs.sort_values("rollback_beta", ascending=False).head(50).assign(slice="top_rollback_lock"),
            coefs[coefs["support"]].sort_values("rollback_beta").head(50).assign(slice="negative_rollback_relief"),
            coefs[~coefs["support"]].sort_values("add_beta").head(50).assign(slice="negative_add_relief"),
            coefs.sort_values("lock_cost", ascending=False).head(50).assign(slice="top_lock_cost"),
        ],
        ignore_index=True,
    )
    top[[c for c in ["slice"] + top_cols if c in top.columns]].to_csv(OUT / "h033_top_phase_lock_cells.csv", index=False)
    return by_target, top


def write_submission(template: pd.DataFrame, prob: np.ndarray, candidate_id: str) -> Path:
    out = template.copy()
    out[TARGETS] = clip_prob(prob)
    path = OUT / f"submission_h033_{safe_id(candidate_id)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def materialize_candidates(
    template: pd.DataFrame,
    h012_prob: np.ndarray,
    q: np.ndarray,
    e247_prob: np.ndarray,
    coefs: pd.DataFrame,
    parts: dict[str, np.ndarray],
) -> pd.DataFrame:
    z_h012 = parts["z_h012"].copy()
    z_e247 = parts["z_e247"]
    z_q = logit(q).reshape(-1)
    h012_dir = parts["h012_dir"]
    q_dir = z_q - z_e247

    rollback_pool = coefs[(coefs["support"]) & (coefs["rollback_beta"] < 0)].sort_values("rollback_beta")
    add_pool = coefs[(~coefs["support"]) & (coefs["add_beta"] < 0)].sort_values("add_beta")
    over_pool = coefs[(coefs["support"]) & (coefs["over_beta"] < 0)].sort_values("over_beta")

    specs: list[OpSpec] = []
    for k in [10, 25, 50, 80, 120, 180]:
        for alpha in [0.10, 0.25, 0.40, 0.60]:
            specs.append(OpSpec("rollback", k, alpha, "negative_rollback"))
    for k in [10, 25, 50, 80, 120, 200]:
        for alpha in [0.10, 0.25, 0.40, 0.70]:
            specs.append(OpSpec("add", k, alpha, "negative_add"))
    for k in [10, 25, 50, 80, 120]:
        for alpha in [0.05, 0.10, 0.18, 0.28]:
            specs.append(OpSpec("over", k, alpha, "negative_over"))
    for k in [10, 25, 50, 80, 120]:
        for alpha in [0.10, 0.25, 0.40]:
            specs.append(OpSpec("rollback_add", k, alpha, "negative_combo"))

    rows: list[dict[str, Any]] = []
    seen = {hashlib.sha1(np.round(h012_prob, 12).tobytes()).hexdigest()[:12]}
    n_cell = len(z_h012)
    for spec in specs:
        z = z_h012.copy()
        touched: list[int] = []
        if spec.op in {"rollback", "rollback_add"} and not rollback_pool.empty:
            ids = rollback_pool.head(min(spec.k, len(rollback_pool)))["cell_id"].to_numpy(dtype=int)
            z[ids] = z_h012[ids] - spec.alpha * h012_dir[ids]
            touched.extend(ids.tolist())
        if spec.op in {"add", "rollback_add"} and not add_pool.empty:
            ids = add_pool.head(min(spec.k, len(add_pool)))["cell_id"].to_numpy(dtype=int)
            z[ids] = z_h012[ids] + spec.alpha * q_dir[ids]
            touched.extend(ids.tolist())
        if spec.op == "over" and not over_pool.empty:
            ids = over_pool.head(min(spec.k, len(over_pool)))["cell_id"].to_numpy(dtype=int)
            z[ids] = z_h012[ids] + spec.alpha * h012_dir[ids]
            touched.extend(ids.tolist())
        if not touched:
            continue
        prob = sigmoid(z).reshape(h012_prob.shape)
        digest = hashlib.sha1(np.round(prob, 12).tobytes()).hexdigest()[:12]
        if digest in seen:
            continue
        seen.add(digest)
        candidate_id = f"{spec.family}_{spec.op}_k{spec.k}_a{spec.alpha:g}"
        path = write_submission(template, prob, candidate_id)
        diff = np.abs(prob - h012_prob)
        rows.append(
            {
                "file": f"hitl/h033_phase_lock_contrast_jepa/{path.name}",
                "resolved_path": str(path),
                "candidate_id": candidate_id,
                "family": spec.family,
                "op": spec.op,
                "k": spec.k,
                "alpha": spec.alpha,
                "changed_cells_vs_h012": int(np.sum(diff > 1.0e-6)),
                "changed_rows_vs_h012": int(np.sum(np.any(diff > 1.0e-6, axis=1))),
                "max_abs_prob_vs_h012": float(np.max(diff)),
                "mean_abs_prob_vs_h012": float(np.mean(diff)),
                "rollback_cells": int(sum(i < n_cell for i in touched)),
                "predicted_coeff_gain": float(coefs.set_index("cell_id").loc[list(set(touched)), "negative_op_cost"].sum()),
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "h033_generated_phase_lock_candidates.csv", index=False)
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
    var_rows["source"] = "h033_phase_lock"
    pool = pd.concat([pd.DataFrame(known_rows), var_rows], ignore_index=True).drop_duplicates("file", keep="last")
    features = h024.build_feature_table(pool, refs)
    features.to_csv(OUT / "h033_h024_features.csv", index=False)
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
    cols_by_set = h024.feature_sets(cols)
    return known, features, cols_by_set


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
    model_no_h012.to_csv(OUT / "h033_pre_h012_h024_model_scores.csv", index=False)
    loo_no_h012.to_csv(OUT / "h033_pre_h012_h024_loo_predictions.csv", index=False)
    model_full.to_csv(OUT / "h033_full_h024_model_scores.csv", index=False)
    loo_full.to_csv(OUT / "h033_full_h024_loo_predictions.csv", index=False)

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
    pred_frame.to_csv(OUT / "h033_direct_decoder_predictions.csv", index=False)

    scored = variants.merge(pred_frame, on="file", how="left")
    h012_pred = pred_frame[pred_frame["file"].eq(H012)]
    if h012_pred.empty:
        h012_pre_state = H012_LB
    else:
        h012_pre_state = float(h012_pred[[c for c in h012_pred.columns if c.startswith("pre_state")]].mean(axis=1).iloc[0])
    scored["pre_state_mean"] = scored[[c for c in scored.columns if c.startswith("pre_state")]].mean(axis=1)
    scored["pre_geometry_mean"] = scored[[c for c in scored.columns if c.startswith("pre_geometry")]].mean(axis=1)
    scored["full_state_mean"] = scored[[c for c in scored.columns if c.startswith("full_state")]].mean(axis=1)
    scored["full_geometry_mean"] = scored[[c for c in scored.columns if c.startswith("full_geometry")]].mean(axis=1)
    scored["pre_state_margin_vs_h012_pred"] = scored["pre_state_mean"] - h012_pre_state
    scored["h033_action_score"] = (
        scored["pre_state_mean"].fillna(0.60)
        + 0.25 * np.maximum(scored["pre_geometry_mean"].fillna(0.60) - H012_LB, -0.03)
        + 0.00002 * scored["changed_cells_vs_h012"].fillna(0) / 50.0
        + 0.008 * np.maximum(scored["max_abs_prob_vs_h012"].fillna(0) - 0.10, 0)
    )
    scored = scored.sort_values(["h033_action_score", "pre_state_mean", "changed_cells_vs_h012"]).reset_index(drop=True)
    scored.to_csv(OUT / "h033_candidate_scores.csv", index=False)
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
    null.to_csv(OUT / "h033_selected_pre_h012_public_perm_stress.csv", index=False)
    return null


def rowperm_stress(selected: pd.Series) -> pd.DataFrame:
    try:
        h026 = import_module(HITL / "h026_public_private_calibration_veto_jepa.py", "h026_h033")
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
    rowperm.to_csv(OUT / "h033_selected_h025_rowperm_stress.csv", index=False)
    return rowperm


def decide(scored: pd.DataFrame, public_perm: pd.DataFrame, rowperm: pd.DataFrame) -> tuple[str, Path | None]:
    if scored.empty:
        return "no_h033_candidates", None
    selected = scored.iloc[0]
    public_perm_p = 1.0
    if not public_perm.empty and "perm_selected_minus_h012" in public_perm.columns:
        public_perm_p = float(np.mean(public_perm["perm_selected_minus_h012"].to_numpy(dtype=np.float64) <= float(selected["pre_state_margin_vs_h012_pred"])))
    rowperm_p = 1.0
    if not rowperm.empty and "perm_top1200_sum" in rowperm.columns:
        rowperm_p = float(np.mean(rowperm["perm_top1200_sum"].to_numpy(dtype=np.float64) >= rowperm["real_top1200_sum"].iloc[0]))
    gate = (
        float(selected["pre_state_margin_vs_h012_pred"]) <= -0.00030
        and float(selected["changed_cells_vs_h012"]) <= 180
        and float(selected["max_abs_prob_vs_h012"]) <= 0.10
        and public_perm_p <= 0.25
        and rowperm_p <= 0.35
    )
    if not gate:
        return "diagnostic_only_no_phase_lock_action_clears_stress", None
    src = Path(str(selected["resolved_path"]))
    dst = ROOT / f"submission_h033_phase_lock_{safe_id(str(selected['candidate_id']), 72)}_uploadsafe.csv"
    shutil.copyfile(src, dst)
    return "promote_h033_phase_lock_big_bet", dst


def write_report(
    cv: pd.DataFrame,
    train_pred: np.ndarray,
    y: np.ndarray,
    coefs: pd.DataFrame,
    target_summary: pd.DataFrame,
    candidate_scores: pd.DataFrame,
    public_perm: pd.DataFrame,
    rowperm: pd.DataFrame,
    decision: str,
    promoted: Path | None,
) -> None:
    all_oof = cv[cv["fold"].eq("__all_oof__")].sort_values("mae").head(5)
    best_cv = all_oof.iloc[0] if not all_oof.empty else None
    train_mae = float(np.mean(np.abs(train_pred - y)))
    train_rho = spearman(y, train_pred)
    selected = candidate_scores.iloc[0] if not candidate_scores.empty else None
    support = coefs[coefs["support"]]
    outside = coefs[~coefs["support"]]
    lines = [
        "# H033 Phase-Lock Contrastive HS-JEPA\n\n",
        "## Question\n\n",
        "H032 recovered H012 but found no stronger sibling. H033 asks which row-target operations make those siblings fail, and whether the learned phase-lock law contains any negative-cost move away from H012.\n\n",
        "## Phase-Lock Model Health\n\n",
    ]
    if best_cv is not None:
        lines.append(
            f"- best all-OOF alpha: `{best_cv['alpha']}` MAE `{best_cv['mae']:.9f}`, "
            f"Spearman `{best_cv['spearman']:.9f}`, pairwise `{best_cv['pair_acc']:.9f}`\n"
        )
    lines.append(f"- full-fit train MAE: `{train_mae:.9f}`\n")
    lines.append(f"- full-fit train Spearman: `{train_rho:.9f}`\n")
    lines.append(f"- H012-support cells with negative rollback cost: `{int((support['rollback_beta'] < 0).sum())}` / `{len(support)}`\n")
    lines.append(f"- outside-support cells with negative add cost: `{int((outside['add_beta'] < 0).sum())}` / `{len(outside)}`\n\n")
    lines.append("## Best CV Rows\n\n")
    lines.append(md_table(all_oof, 5) + "\n\n")
    lines.append("## Target Phase-Lock Summary\n\n")
    lines.append(md_table(target_summary, 12) + "\n\n")
    lines.append("## Top Candidate Actions\n\n")
    keep = [
        "candidate_id",
        "family",
        "op",
        "k",
        "alpha",
        "changed_cells_vs_h012",
        "max_abs_prob_vs_h012",
        "pre_state_mean",
        "pre_state_margin_vs_h012_pred",
        "pre_geometry_mean",
        "h033_action_score",
        "file",
    ]
    lines.append(md_table(candidate_scores[[c for c in keep if c in candidate_scores.columns]], 20) + "\n\n")
    lines.append("## Stress\n\n")
    lines.append(f"- decision: `{decision}`\n")
    lines.append(f"- promoted path: `{promoted if promoted is not None else 'none'}`\n")
    if selected is not None:
        lines.append(f"- selected candidate: `{selected['candidate_id']}`\n")
        lines.append(f"- selected pre-state margin vs H012 prediction: `{float(selected['pre_state_margin_vs_h012_pred']):.9f}`\n")
    if not public_perm.empty and "perm_selected_minus_h012" in public_perm.columns and selected is not None:
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
        lines.append("No candidate actions were generated. The phase-lock law is diagnostic only.\n")
    elif promoted is None:
        lines.append(
            "The H032 sibling failures are learnable as a phase-lock contrast, but the negative-cost operations do not yet clear public-free action stress. "
            "This supports the discrete-translation-law direction while rejecting a direct H012 edit from the first linear contrast model.\n"
        )
    else:
        lines.append(
            "A phase-lock-derived move cleared the stress gate. This is a high-information public test of whether H012 can be improved by learned row-target contrast rather than smooth phase continuation.\n"
        )
    lines.append("\n## Files\n\n")
    for path in [
        OUT / "h033_break_dataset_meta.csv",
        OUT / "h033_phase_lock_cv.csv",
        OUT / "h033_cell_phase_lock_coefficients.csv",
        OUT / "h033_target_phase_lock_summary.csv",
        OUT / "h033_top_phase_lock_cells.csv",
        OUT / "h033_generated_phase_lock_candidates.csv",
        OUT / "h033_candidate_scores.csv",
        OUT / "h033_selected_pre_h012_public_perm_stress.csv",
        OUT / "h033_selected_h025_rowperm_stress.csv",
    ]:
        lines.append(f"- `{path.relative_to(ROOT)}`\n")
    (OUT / "h033_report.md").write_text("".join(lines), encoding="utf-8")


def main() -> None:
    h024 = load_h024()
    sample, h012_df, e247_prob, h012_prob, q = load_base(h024)
    h032_scores = load_phase_scores()
    h032_cells = pd.read_csv(H032_DIR / "h032_cell_phase_state.csv")
    x, y, meta, parts = build_break_matrix(h024, h032_scores, sample, e247_prob, h012_prob)
    cv = cv_phase_lock(x, y, meta)
    best_alpha = float(cv[cv["fold"].eq("__all_oof__")].sort_values("mae").iloc[0]["alpha"])
    train_pred, model, scaler = fit_full_lock_model(x, y, best_alpha)
    meta["phase_lock_pred_margin"] = train_pred
    meta["phase_lock_train_residual"] = train_pred - y
    meta.to_csv(OUT / "h033_break_dataset_meta.csv", index=False)
    coefs = coefficient_frame(model, scaler, h032_cells, parts)
    target_summary, _ = summarize_coefficients(coefs)
    variants = materialize_candidates(h012_df, h012_prob, q, e247_prob, coefs, parts)
    if variants.empty:
        candidate_scores = pd.DataFrame()
        public_perm = pd.DataFrame()
        rowperm = pd.DataFrame()
        decision, promoted = "diagnostic_only_no_negative_phase_lock_actions", None
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
                "best_alpha": best_alpha,
                "n_phase_siblings": int(len(h032_scores)),
                "n_generated_candidates": int(len(variants)),
                "selected_candidate_id": None if candidate_scores.empty else candidate_scores.iloc[0]["candidate_id"],
                "selected_file": None if candidate_scores.empty else candidate_scores.iloc[0]["file"],
                "selected_pre_state_margin_vs_h012_pred": None if candidate_scores.empty else candidate_scores.iloc[0]["pre_state_margin_vs_h012_pred"],
                "promoted_path": None if promoted is None else str(promoted),
            }
        ]
    ).to_csv(OUT / "h033_decision.csv", index=False)
    write_report(cv, train_pred, y, coefs, target_summary, candidate_scores, public_perm, rowperm, decision, promoted)
    print(pd.read_csv(OUT / "h033_decision.csv").to_string(index=False))
    if not candidate_scores.empty:
        print(candidate_scores.head(20).to_string(index=False))
    print(OUT / "h033_report.md")


if __name__ == "__main__":
    main()
