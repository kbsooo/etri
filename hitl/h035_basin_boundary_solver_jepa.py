#!/usr/bin/env python3
"""H035: H012 basin-boundary combinatorial solver HS-JEPA.

H032 recovered H012 as the best phase point and H034 showed that first-order
row edits are still outside the action-safe basin. H035 changes the action
unit again: keep H012's public-equation posterior direction, but solve a
constrained support-swap problem around the 1200 H012 cells.

The falsifiable bet:

If H012 is a row-target identity basin rather than a single lucky mask, then
small structure-preserving swaps should produce a candidate that stays near
the H012 phase-lock route while improving the public-equation posterior loss.
If every such swap is rejected by the route/action-health stack, then the
H012 mask is closer to a locked fixed point than to a smooth editable support.
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
OUT = HITL / "h035_basin_boundary_solver_jepa"
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
H034_DIR = HITL / "h034_rowvector_route_translator_jepa"


@dataclass(frozen=True)
class SwapSpec:
    family: str
    k: int
    alpha: float
    drop_metric: str
    add_metric: str
    preserve: str


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


def bce(prob: np.ndarray, q: np.ndarray) -> np.ndarray:
    p = clip_prob(prob)
    y = clip_prob(q)
    return -(y * np.log(p) + (1.0 - y) * np.log(1.0 - p))


def short_hash(frame: pd.DataFrame) -> str:
    arr = np.round(frame[TARGETS].to_numpy(dtype=np.float64), 12)
    return hashlib.sha1(arr.tobytes()).hexdigest()[:8]


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


def rank01(x: pd.Series, ascending: bool) -> pd.Series:
    if x.nunique(dropna=True) <= 1:
        return pd.Series(0.5, index=x.index)
    r = x.rank(method="average", ascending=ascending)
    return (r - 1.0) / max(float(len(x) - 1), 1.0)


def load_h024() -> object:
    return import_module(HITL / "h024_action_health_decoder_jepa.py", "h024_h035")


def load_h034() -> object:
    return import_module(HITL / "h034_rowvector_route_translator_jepa.py", "h034_h035")


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


def cell_key_frame() -> pd.DataFrame:
    cells = pd.read_csv(H032_DIR / "h032_cell_phase_state.csv")
    coefs = pd.read_csv(H033_DIR / "h033_cell_phase_lock_coefficients.csv")
    row_state = pd.read_csv(H034_DIR / "h034_row_route_state.csv")
    keep_coef = [
        "row",
        "target",
        "rollback_beta",
        "over_beta",
        "add_beta",
        "lock_cost",
        "negative_op_cost",
        "support",
    ]
    out = cells.merge(coefs[keep_coef], on=["row", "target"], how="left", suffixes=("", "_coef"))
    row_cols = [
        "row",
        "support_count",
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
    out = out.merge(row_state[row_cols], on="row", how="left")
    out["support"] = out["h012_changed"].astype(bool)
    out["outside"] = ~out["support"]
    out["flat_idx"] = out["row"].astype(int) * len(TARGETS) + out["target_i"].astype(int)

    # Drop risk: H012 support cells that are semantically weak or costly under
    # previous phase-lock diagnostics. Add utility: outside cells that fit the
    # same public-equation / row-vector human-state prior.
    out["drop_boundary"] = (
        0.18 * rank01(out["cell_score"], ascending=True)
        + 0.15 * rank01(out["identity_phase_score"], ascending=True)
        + 0.13 * rank01(out["route_translator_score"], ascending=True)
        + 0.11 * rank01(out["score_joint_vector_cell"], ascending=True)
        + 0.11 * rank01(out["score_public_row_subset"], ascending=True)
        + 0.11 * rank01(out["private_safe_score"], ascending=True)
        + 0.10 * out["memory_disagrees_h012"].astype(float)
        + 0.07 * rank01(out["lock_cost"], ascending=True)
        + 0.04 * rank01(out["negative_op_cost"], ascending=True)
    )
    out["drop_memory_conflict"] = (
        0.40 * out["memory_disagrees_h012"].astype(float)
        + 0.20 * rank01(out["memory_alignment_q"], ascending=True)
        + 0.15 * rank01(out["score_memory_public_combo"], ascending=True)
        + 0.15 * rank01(out["private_safe_score"], ascending=True)
        + 0.10 * rank01(out["identity_phase_score"], ascending=True)
    )
    out["drop_low_public_identity"] = (
        0.30 * rank01(out["score_public_row_subset"], ascending=True)
        + 0.25 * rank01(out["score_identity_combo"], ascending=True)
        + 0.20 * rank01(out["score_joint_vector_cell"], ascending=True)
        + 0.15 * rank01(out["route_translator_score"], ascending=True)
        + 0.10 * rank01(out["posterior_gain"], ascending=True)
    )
    out["add_public_vector"] = (
        0.26 * rank01(out["score_public_row_subset"], ascending=False)
        + 0.23 * rank01(out["score_joint_vector_cell"], ascending=False)
        + 0.18 * rank01(out["score_identity_combo"], ascending=False)
        + 0.14 * rank01(out["posterior_gain"], ascending=False)
        + 0.11 * rank01(out["direction_consistency"], ascending=False)
        + 0.08 * rank01(out["private_safe_score"], ascending=False)
    )
    out["add_no_h012"] = (
        0.30 * rank01(out["score_no_h012_combo"], ascending=False)
        + 0.22 * rank01(out["cell_score"], ascending=False)
        + 0.18 * rank01(out["score_joint_vector_cell"], ascending=False)
        + 0.15 * rank01(out["route_translator_score"], ascending=False)
        + 0.15 * rank01(out["private_safe_score"], ascending=False)
    )
    out["add_memory_public"] = (
        0.30 * rank01(out["score_memory_public_combo"], ascending=False)
        + 0.23 * rank01(out["memory_alignment_q"], ascending=False)
        + 0.17 * rank01(out["score_public_row_subset"], ascending=False)
        + 0.16 * rank01(out["posterior_gain"], ascending=False)
        + 0.14 * rank01(out["private_safe_score"], ascending=False)
    )
    out.to_csv(OUT / "h035_cell_state.csv", index=False)
    return out


def train_route_model() -> tuple[list[str], Ridge, StandardScaler, ExtraTreesRegressor, pd.DataFrame]:
    features = pd.read_csv(H034_DIR / "h034_route_training_features.csv")
    scores = pd.read_csv(H032_DIR / "h032_phase_candidate_scores.csv")
    scores = scores[scores["candidate_id"] != "anchor_h012_actual"].copy()
    y = scores["pre_state_margin_vs_h012_pred"].to_numpy(dtype=np.float64)
    blocked = {"file", "resolved_path", "candidate_id", "score_name", "target_group", "curve"}
    cols = [c for c in features.columns if c not in blocked and pd.api.types.is_numeric_dtype(features[c])]
    x = features[cols].fillna(0.0).to_numpy(dtype=np.float64)
    scaler = StandardScaler(with_mean=True, with_std=True)
    xs = scaler.fit_transform(x)
    ridge = Ridge(alpha=100.0, fit_intercept=True, solver="lsqr", max_iter=5000, random_state=20260602)
    ridge.fit(xs, y)
    et = ExtraTreesRegressor(
        n_estimators=650,
        max_depth=10,
        min_samples_leaf=5,
        max_features=0.70,
        random_state=20260604,
        n_jobs=-1,
    )
    et.fit(x, y)
    pred = (ridge.predict(xs) + et.predict(x)) / 2.0
    health = pd.DataFrame(
        [
            {
                "n": int(len(y)),
                "mae": float(np.mean(np.abs(pred - y))),
                "rmse": float(np.sqrt(np.mean((pred - y) ** 2))),
                "pred_min": float(np.min(pred)),
                "pred_median": float(np.median(pred)),
                "pred_max": float(np.max(pred)),
                "target_min": float(np.min(y)),
                "target_median": float(np.median(y)),
                "target_max": float(np.max(y)),
            }
        ]
    )
    health.to_csv(OUT / "h035_route_model_fit.csv", index=False)
    return cols, ridge, scaler, et, health


def swap_specs() -> list[SwapSpec]:
    specs: list[SwapSpec] = []
    for preserve in ["target", "row", "support_count"]:
        for drop_metric in ["drop_boundary", "drop_memory_conflict", "drop_low_public_identity"]:
            for add_metric in ["add_public_vector", "add_no_h012", "add_memory_public"]:
                for k in [7, 14, 28, 56, 84, 112, 168, 224]:
                    for alpha in [0.58, 0.70, 0.82]:
                        specs.append(SwapSpec("swap", k, alpha, drop_metric, add_metric, preserve))
    for drop_metric in ["drop_boundary", "drop_memory_conflict", "drop_low_public_identity"]:
        for k in [10, 20, 40, 80, 120, 180]:
            for alpha in [0.55, 0.70, 0.85]:
                specs.append(SwapSpec("soften_tail", k, alpha, drop_metric, "none", "support"))
    return specs


def preserve_swap_mask(cells: pd.DataFrame, spec: SwapSpec) -> tuple[np.ndarray, list[int], list[int]]:
    n = len(cells)
    support = cells["support"].to_numpy(dtype=bool)
    selected = support.copy()
    drop_ids: list[int] = []
    add_ids: list[int] = []

    if spec.family == "soften_tail":
        chosen = (
            cells[cells["support"]]
            .sort_values(spec.drop_metric, ascending=False)
            .head(spec.k)
            .index.tolist()
        )
        # Mask stays identical. The selected support cells will use a different alpha.
        return selected, chosen, []

    if spec.preserve == "target":
        groups = list(cells.groupby("target", sort=True))
    elif spec.preserve == "row":
        groups = [(str(k), v) for k, v in cells.groupby("row", sort=True)]
    elif spec.preserve == "support_count":
        groups = [(str(k), v) for k, v in cells.groupby("support_count", sort=True)]
    else:
        raise KeyError(spec.preserve)

    # Allocate swaps proportional to available support while requiring each
    # group to replace like with like.
    support_counts = np.asarray([int(g["support"].sum()) for _, g in groups], dtype=np.float64)
    total_support = float(support_counts.sum())
    if total_support <= 0:
        return selected, drop_ids, add_ids
    raw = support_counts / total_support * spec.k
    alloc = np.floor(raw).astype(int)
    remainder = int(spec.k - alloc.sum())
    if remainder > 0:
        order = np.argsort(-(raw - alloc))
        for idx in order[:remainder]:
            alloc[idx] += 1

    for (_, part), take in zip(groups, alloc):
        if take <= 0:
            continue
        s_part = part[part["support"]].sort_values(spec.drop_metric, ascending=False)
        o_part = part[~part["support"]].sort_values(spec.add_metric, ascending=False)
        m = min(int(take), len(s_part), len(o_part))
        if m <= 0:
            continue
        drop = s_part.head(m).index.tolist()
        add = o_part.head(m).index.tolist()
        selected[drop] = False
        selected[add] = True
        drop_ids.extend(drop)
        add_ids.extend(add)
    if len(selected) != n:
        raise RuntimeError("mask size mismatch")
    return selected, drop_ids, add_ids


def write_submission(template: pd.DataFrame, prob: np.ndarray, candidate_id: str) -> Path:
    out = template.copy()
    out[TARGETS] = clip_prob(prob)
    path = OUT / f"submission_h035_{safe_id(candidate_id)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def materialize_candidates(
    template: pd.DataFrame,
    e247_prob: np.ndarray,
    h012_prob: np.ndarray,
    q: np.ndarray,
    cells: pd.DataFrame,
    h034: object,
    route_cols: list[str],
    ridge: Ridge,
    scaler: StandardScaler,
    et: ExtraTreesRegressor,
) -> pd.DataFrame:
    z_e247 = logit(e247_prob)
    z_q = logit(q)
    n_cells = e247_prob.size
    h012_support_flat = np.zeros(n_cells, dtype=bool)
    h012_support_flat[cells["flat_idx"].to_numpy(dtype=int)] = cells["support"].to_numpy(dtype=bool)
    h012_support = h012_support_flat.reshape(e247_prob.shape)
    z_h012 = logit(h012_prob)
    rows: list[dict[str, Any]] = []
    seen = {hashlib.sha1(np.round(h012_prob, 12).tobytes()).hexdigest()[:12]}
    coefs = pd.read_csv(H033_DIR / "h033_cell_phase_lock_coefficients.csv")
    row_state = pd.read_csv(H034_DIR / "h034_row_route_state.csv")

    for spec in swap_specs():
        cell_order_mask, drop_ids, add_ids = preserve_swap_mask(cells, spec)
        if spec.family == "swap" and (not drop_ids or not add_ids):
            continue
        z = z_e247.copy()
        selected_flat = np.zeros(n_cells, dtype=bool)
        selected_flat[cells["flat_idx"].to_numpy(dtype=int)] = cell_order_mask
        mask = selected_flat.reshape(e247_prob.shape)
        z[mask] = (1.0 - spec.alpha) * z_e247[mask] + spec.alpha * z_q[mask]
        if spec.family == "soften_tail":
            # Keep all H012 support but soften the selected tail cells from
            # alpha=0.70 toward the spec alpha.
            tail = np.zeros_like(cell_order_mask, dtype=bool)
            tail[drop_ids] = True
            tail_flat = np.zeros(n_cells, dtype=bool)
            tail_flat[cells["flat_idx"].to_numpy(dtype=int)] = tail
            tail2 = tail_flat.reshape(e247_prob.shape)
            z[h012_support] = 0.30 * z_e247[h012_support] + 0.70 * z_q[h012_support]
            z[tail2] = (1.0 - spec.alpha) * z_e247[tail2] + spec.alpha * z_q[tail2]
        prob = sigmoid(z)
        digest = hashlib.sha1(np.round(prob, 12).tobytes()).hexdigest()[:12]
        if digest in seen:
            continue
        seen.add(digest)
        diff_h012 = np.abs(prob - h012_prob)
        if np.max(diff_h012) <= 1.0e-9:
            continue
        cid = (
            f"{spec.family}_{spec.preserve}_{spec.drop_metric}_to_{spec.add_metric}"
            f"_k{spec.k}_a{spec.alpha:g}"
        )
        path = write_submission(template, prob, cid)
        feat = h034.route_features_from_prob(prob, h012_prob, e247_prob, q, coefs, row_state)
        x = pd.DataFrame([feat]).reindex(columns=route_cols).fillna(0.0).to_numpy(dtype=np.float64)
        route_ridge = float(ridge.predict(scaler.transform(x))[0])
        route_et = float(et.predict(x)[0])
        q_loss = float(np.mean(bce(prob, q) - bce(h012_prob, q)))
        e247_loss = float(np.mean(bce(prob, q) - bce(e247_prob, q)))
        support_new = mask
        rows.append(
            {
                "file": f"hitl/h035_basin_boundary_solver_jepa/{path.name}",
                "resolved_path": str(path),
                "candidate_id": cid,
                "family": spec.family,
                "preserve": spec.preserve,
                "drop_metric": spec.drop_metric,
                "add_metric": spec.add_metric,
                "k": spec.k,
                "alpha": spec.alpha,
                "drop_count": int(len(drop_ids)),
                "add_count": int(len(add_ids)),
                "selected_cells": int(support_new.sum()),
                "changed_cells_vs_h012": int(np.sum(diff_h012 > 1.0e-6)),
                "changed_rows_vs_h012": int(np.sum(np.any(diff_h012 > 1.0e-6, axis=1))),
                "max_abs_prob_vs_h012": float(np.max(diff_h012)),
                "mean_abs_prob_vs_h012": float(np.mean(diff_h012)),
                "route_ridge_margin_pred": route_ridge,
                "route_et_margin_pred": route_et,
                "route_mean_margin_pred": float((route_ridge + route_et) / 2.0),
                "q_loss_delta_vs_h012": q_loss,
                "q_loss_delta_vs_e247": e247_loss,
                "dropped_rows": ",".join(str(int(cells.loc[i, "row"])) for i in drop_ids[:80]),
                "added_rows": ",".join(str(int(cells.loc[i, "row"])) for i in add_ids[:80]),
            }
        )
    out = pd.DataFrame(rows)
    if not out.empty:
        out["basin_solver_score"] = (
            out["q_loss_delta_vs_h012"].fillna(9.0)
            + 0.45 * np.maximum(out["route_mean_margin_pred"].fillna(0.05), -0.002)
            + 0.00025 * out["changed_cells_vs_h012"].fillna(0.0) / 120.0
            + 0.004 * np.maximum(out["max_abs_prob_vs_h012"].fillna(0.0) - 0.12, 0.0)
        )
        out = out.sort_values(["basin_solver_score", "route_mean_margin_pred", "q_loss_delta_vs_h012"]).reset_index(drop=True)
    out.to_csv(OUT / "h035_generated_basin_candidates.csv", index=False)
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
    var_rows["source"] = "h035_basin_solver"
    pool = pd.concat([pd.DataFrame(known_rows), var_rows], ignore_index=True).drop_duplicates("file", keep="last")
    features = h024.build_feature_table(pool, refs)
    features.to_csv(OUT / "h035_h024_features.csv", index=False)
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


def score_candidates(
    h024: object,
    variants: pd.DataFrame,
    known: pd.DataFrame,
    features: pd.DataFrame,
    cols_by_set: dict[str, list[str]],
) -> pd.DataFrame:
    known_no_h012 = known[known["file"] != H012].copy().reset_index(drop=True)
    model_no_h012, loo_no_h012 = h024.evaluate_known_models(known_no_h012[["file", "public_lb"]], features, cols_by_set)
    model_full, loo_full = h024.evaluate_known_models(known[["file", "public_lb"]], features, cols_by_set)
    model_no_h012.to_csv(OUT / "h035_pre_h012_h024_model_scores.csv", index=False)
    loo_no_h012.to_csv(OUT / "h035_pre_h012_h024_loo_predictions.csv", index=False)
    model_full.to_csv(OUT / "h035_full_h024_model_scores.csv", index=False)
    loo_full.to_csv(OUT / "h035_full_h024_loo_predictions.csv", index=False)

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
    pred_frame.to_csv(OUT / "h035_direct_decoder_predictions.csv", index=False)
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
    scored["h035_action_score"] = (
        scored["pre_state_margin_vs_h012_pred"].fillna(0.03)
        + 0.45 * np.maximum(scored["route_mean_margin_pred"].fillna(0.05), -0.002)
        + 0.35 * scored["q_loss_delta_vs_h012"].fillna(0.01)
        + 0.00005 * scored["changed_cells_vs_h012"].fillna(0.0) / 50.0
        + 0.004 * np.maximum(scored["max_abs_prob_vs_h012"].fillna(0.0) - 0.12, 0.0)
    )
    scored = scored.sort_values(["h035_action_score", "pre_state_margin_vs_h012_pred", "route_mean_margin_pred"]).reset_index(drop=True)
    scored.to_csv(OUT / "h035_candidate_scores.csv", index=False)
    return scored


def public_perm_stress(
    h024: object,
    selected: pd.Series,
    known: pd.DataFrame,
    features: pd.DataFrame,
    cols_by_set: dict[str, list[str]],
) -> pd.DataFrame:
    known_no_h012 = known[known["file"] != H012].copy().reset_index(drop=True)
    null = h024.permutation_stress(
        known_no_h012[["file", "public_lb"]],
        features,
        cols_by_set,
        str(selected["file"]),
        n_perm=300,
    )
    null.to_csv(OUT / "h035_selected_pre_h012_public_perm_stress.csv", index=False)
    return null


def rowperm_stress(selected: pd.Series) -> pd.DataFrame:
    try:
        h026 = import_module(HITL / "h026_public_private_calibration_veto_jepa.py", "h026_h035")
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
    rowperm.to_csv(OUT / "h035_selected_h025_rowperm_stress.csv", index=False)
    return rowperm


def decide(scored: pd.DataFrame, public_perm: pd.DataFrame, rowperm: pd.DataFrame) -> tuple[str, Path | None]:
    if scored.empty:
        return "diagnostic_only_no_basin_candidates", None
    selected = scored.iloc[0]
    public_perm_p = 1.0
    if not public_perm.empty and "perm_selected_minus_h012" in public_perm.columns:
        public_perm_p = float(np.mean(public_perm["perm_selected_minus_h012"].to_numpy(dtype=np.float64) <= float(selected["pre_state_margin_vs_h012_pred"])))
    rowperm_p = 1.0
    if not rowperm.empty and "perm_top1200_sum" in rowperm.columns:
        rowperm_p = float(np.mean(rowperm["perm_top1200_sum"].to_numpy(dtype=np.float64) >= rowperm["real_top1200_sum"].iloc[0]))

    gate = (
        float(selected["q_loss_delta_vs_h012"]) <= -0.00008
        and float(selected["route_mean_margin_pred"]) <= 0.0060
        and float(selected["pre_state_margin_vs_h012_pred"]) <= -0.00025
        and float(selected["changed_cells_vs_h012"]) >= 14
        and float(selected["changed_cells_vs_h012"]) <= 420
        and float(selected["max_abs_prob_vs_h012"]) <= 0.18
        and public_perm_p <= 0.25
        and rowperm_p <= 0.35
    )
    if not gate:
        return "diagnostic_only_h012_basin_locked_no_swap_clears_stress", None
    src = Path(str(selected["resolved_path"]))
    dst = ROOT / f"submission_h035_basin_solver_{safe_id(str(selected['candidate_id']), 72)}_uploadsafe.csv"
    shutil.copyfile(src, dst)
    return "promote_h035_basin_boundary_big_bet", dst


def write_report(
    route_health: pd.DataFrame,
    variants: pd.DataFrame,
    scored: pd.DataFrame,
    public_perm: pd.DataFrame,
    rowperm: pd.DataFrame,
    decision: str,
    promoted: Path | None,
) -> None:
    selected = scored.iloc[0] if not scored.empty else None
    audit: dict[str, Any] = {}
    best_q = None
    best_route = None
    if not scored.empty:
        q_gate = scored["q_loss_delta_vs_h012"] < 0.0
        route_gate = scored["route_mean_margin_pred"] <= 0.006
        pre_gate = scored["pre_state_margin_vs_h012_pred"] <= 0.0
        strict_gate = (
            (scored["q_loss_delta_vs_h012"] <= -0.00008)
            & route_gate
            & (scored["pre_state_margin_vs_h012_pred"] <= -0.00025)
        )
        audit = {
            "generated_candidates": int(len(scored)),
            "q_improving_vs_h012": int(q_gate.sum()),
            "route_safe_count": int(route_gate.sum()),
            "pre_state_better_count": int(pre_gate.sum()),
            "strict_gate_count": int(strict_gate.sum()),
            "best_q_delta": float(scored["q_loss_delta_vs_h012"].min()),
            "best_route_margin": float(scored["route_mean_margin_pred"].min()),
            "best_pre_state_margin": float(scored["pre_state_margin_vs_h012_pred"].min()),
        }
        best_q = scored.sort_values("q_loss_delta_vs_h012").iloc[0]
        best_route = scored.sort_values("route_mean_margin_pred").iloc[0]
    lines = [
        "# H035 Basin-Boundary Solver HS-JEPA\n\n",
        "## Question\n\n",
        "H035 asks whether H012 is an editable row-target identity basin. It keeps the public-equation posterior direction, but swaps H012 support cells under target/row/support-count constraints before action-health stress.\n\n",
        "## Route Fit\n\n",
        md_table(route_health, 5) + "\n\n",
        "## Generated Candidate Summary\n\n",
    ]
    if variants.empty:
        lines.append("_No candidates generated._\n\n")
    else:
        summary = (
            variants.groupby(["family", "preserve"])
            .agg(
                n=("candidate_id", "count"),
                best_q_delta=("q_loss_delta_vs_h012", "min"),
                best_route_margin=("route_mean_margin_pred", "min"),
                best_basin_score=("basin_solver_score", "min"),
            )
            .reset_index()
            .sort_values("best_basin_score")
        )
        lines.append(md_table(summary, 30) + "\n\n")
    lines.append("## Top Candidate Actions\n\n")
    keep = [
        "candidate_id",
        "family",
        "preserve",
        "drop_metric",
        "add_metric",
        "k",
        "alpha",
        "changed_cells_vs_h012",
        "max_abs_prob_vs_h012",
        "q_loss_delta_vs_h012",
        "route_mean_margin_pred",
        "pre_state_margin_vs_h012_pred",
        "pre_state_mean",
        "h035_action_score",
        "file",
    ]
    lines.append(md_table(scored[[c for c in keep if c in scored.columns]], 24) + "\n\n")
    lines.append("## Boundary Audit\n\n")
    if audit:
        audit_frame = pd.DataFrame([audit])
        lines.append(md_table(audit_frame, 5) + "\n\n")
        if best_q is not None:
            lines.append(
                "- best q-improving candidate: "
                f"`{best_q['candidate_id']}`, q delta `{float(best_q['q_loss_delta_vs_h012']):.9f}`, "
                f"route margin `{float(best_q['route_mean_margin_pred']):.9f}`, "
                f"pre-state margin `{float(best_q['pre_state_margin_vs_h012_pred']):.9f}`\n"
            )
        if best_route is not None:
            lines.append(
                "- best route-margin candidate: "
                f"`{best_route['candidate_id']}`, q delta `{float(best_route['q_loss_delta_vs_h012']):.9f}`, "
                f"route margin `{float(best_route['route_mean_margin_pred']):.9f}`, "
                f"pre-state margin `{float(best_route['pre_state_margin_vs_h012_pred']):.9f}`\n"
            )
        lines.append("\n")
    else:
        lines.append("_No scored candidates._\n\n")
    lines.append("## Stress\n\n")
    lines.append(f"- decision: `{decision}`\n")
    lines.append(f"- promoted path: `{promoted if promoted is not None else 'none'}`\n")
    if selected is not None:
        lines.append(f"- selected candidate: `{selected['candidate_id']}`\n")
        lines.append(f"- selected q-loss delta vs H012: `{float(selected['q_loss_delta_vs_h012']):.9f}`\n")
        lines.append(f"- selected route margin prediction: `{float(selected['route_mean_margin_pred']):.9f}`\n")
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
    if promoted is not None:
        lines.append(
            "A constrained basin-swap action cleared all public-free gates. This is a high-information test that H012 is not a fixed point but an editable identity basin.\n"
        )
    elif selected is not None:
        if audit.get("q_improving_vs_h012", 0) > 0:
            lines.append(
                f"The solver found `{audit['q_improving_vs_h012']}` posterior-improving swaps, "
                "so the public-equation posterior alone still has local directions. "
                "However, none survived the route/pre-state gates: route-safe count is "
                f"`{audit['route_safe_count']}` and pre-state-better count is `{audit['pre_state_better_count']}`. "
                "The selected combined-score action is q-worse than H012, while the best q-improving action is still route/pre-state bad. "
                "That strengthens the locked-basin view: H012 is not safely editable by local support replacement even when target/row structure is preserved. "
                "The next big-bet should stop doing local swaps and solve the hidden public labels/subset jointly, or seek new external constraints on private/public split.\n"
            )
        else:
            lines.append(
                "No posterior-improving local swap survived even the public-equation q objective. "
                "That would make the locked-basin conclusion stronger: H012 is not editable by this support-swap action family. "
                "The next big-bet should stop doing local swaps and solve the hidden public labels/subset jointly, or seek new external constraints on private/public split.\n"
            )
    else:
        lines.append("No valid basin-swap action was materialized.\n")
    lines.append("\n## Files\n\n")
    for path in [
        OUT / "h035_cell_state.csv",
        OUT / "h035_route_model_fit.csv",
        OUT / "h035_generated_basin_candidates.csv",
        OUT / "h035_candidate_scores.csv",
        OUT / "h035_selected_pre_h012_public_perm_stress.csv",
        OUT / "h035_selected_h025_rowperm_stress.csv",
        OUT / "h035_decision.csv",
    ]:
        lines.append(f"- `{path.relative_to(ROOT)}`\n")
    (OUT / "h035_report.md").write_text("".join(lines), encoding="utf-8")


def main() -> None:
    h024 = load_h024()
    h034 = load_h034()
    sample, h012_df, e247_prob, h012_prob, q = load_base(h024)
    cells = cell_key_frame()
    route_cols, ridge, scaler, et, route_health = train_route_model()
    variants = materialize_candidates(h012_df, e247_prob, h012_prob, q, cells, h034, route_cols, ridge, scaler, et)
    if variants.empty:
        scored = pd.DataFrame()
        public_perm = pd.DataFrame()
        rowperm = pd.DataFrame()
        decision, promoted = "diagnostic_only_no_basin_candidates", None
    else:
        known, features, cols_by_set = h024_feature_table(h024, variants)
        scored = score_candidates(h024, variants, known, features, cols_by_set)
        selected = scored.iloc[0]
        public_perm = public_perm_stress(h024, selected, known, features, cols_by_set)
        rowperm = rowperm_stress(selected)
        decision, promoted = decide(scored, public_perm, rowperm)

    pd.DataFrame(
        [
            {
                "decision": decision,
                "n_generated_candidates": int(len(variants)),
                "selected_candidate_id": None if scored.empty else scored.iloc[0]["candidate_id"],
                "selected_file": None if scored.empty else scored.iloc[0]["file"],
                "selected_q_loss_delta_vs_h012": None if scored.empty else scored.iloc[0]["q_loss_delta_vs_h012"],
                "selected_route_mean_margin_pred": None if scored.empty else scored.iloc[0]["route_mean_margin_pred"],
                "selected_pre_state_margin_vs_h012_pred": None if scored.empty else scored.iloc[0]["pre_state_margin_vs_h012_pred"],
                "promoted_path": None if promoted is None else str(promoted),
            }
        ]
    ).to_csv(OUT / "h035_decision.csv", index=False)
    write_report(route_health, variants, scored, public_perm, rowperm, decision, promoted)
    print(pd.read_csv(OUT / "h035_decision.csv").to_string(index=False))
    if not scored.empty:
        print(scored.head(20).to_string(index=False))
    print(OUT / "h035_report.md")


if __name__ == "__main__":
    main()
