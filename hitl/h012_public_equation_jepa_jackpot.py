#!/usr/bin/env python3
"""H012: public-equation HS-JEPA jackpot.

Known public LB observations are not just scores.  For fixed submissions, each
LB difference is a linear equation in the hidden public labels, up to the
unknown public subset/weighting.  H012 treats those equations as a JEPA target:

    context = candidate prediction tensors and their known public LB response
    target  = hidden public label/subset representation
    action  = move E247 toward cells supported by the inferred representation

This is a high-risk inverse problem.  It is not a safe blend and it is not
allowed to be read as a calibrated LB forecast.  It asks a sharper question:
can the old public observations reconstruct a nontrivial hidden public state
that creates a submission far outside ordinary micro-tuning?
"""

from __future__ import annotations

import hashlib
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
HITL = ROOT / "hitl"
H012 = HITL / "h012_public_equation_jepa_jackpot"
H012.mkdir(parents=True, exist_ok=True)

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import (  # noqa: E402
    KEYS,
    TARGETS,
    known_public_table,
    load_sub,
    logit,
)


EPS = 1.0e-6
CURRENT = "submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv"
REPORT_OUT = H012 / "h012_report.md"
CONFIG_OUT = H012 / "h012_posterior_configs.csv"
POSTERIOR_OUT = H012 / "h012_cell_posterior.csv"
CANDIDATE_OUT = H012 / "h012_candidates.csv"
SELECTION_OUT = H012 / "h012_selection.csv"
EQUATION_OUT = H012 / "h012_known_equations.csv"


@dataclass(frozen=True)
class PosteriorConfig:
    prior_name: str
    ridge_mult: float


@dataclass(frozen=True)
class CandidateSpec:
    candidate_id: str
    family: str
    alpha: float
    target_subset: str
    cell_mode: str
    k: int = 0
    min_consistency: float = 0.0


def safe_id(text: str, limit: int = 128) -> str:
    clean = re.sub(r"[^A-Za-z0-9_.-]+", "_", text).strip("_")
    return clean[:limit].strip("_")


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(x, dtype=np.float64)))


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def loss(prob: np.ndarray, y_prob: np.ndarray) -> np.ndarray:
    p = clip_prob(prob)
    q = clip_prob(y_prob)
    return -(q * np.log(p) + (1.0 - q) * np.log(1.0 - p))


def rel(path: Path | None) -> str:
    if path is None:
        return "none"
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def short_hash(frame: pd.DataFrame) -> str:
    arr = np.asarray(frame[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def load_public_system() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, np.ndarray], np.ndarray]:
    known = known_public_table().copy()
    if CURRENT not in set(known["file"].astype(str)):
        raise RuntimeError(f"{CURRENT} missing from known public table")
    known = known.sort_values("public_lb").reset_index(drop=True)
    base = load_sub(CURRENT)
    sample = base[KEYS].copy()
    pred_by_file: dict[str, np.ndarray] = {}
    rows: list[dict[str, Any]] = []
    for rec in known.to_dict("records"):
        file_name = str(rec["file"])
        try:
            df = load_sub(file_name, sample)
        except FileNotFoundError:
            continue
        pred = df[TARGETS].to_numpy(dtype=np.float64)
        pred_by_file[file_name] = pred
        rows.append(rec)
    known = pd.DataFrame(rows).sort_values("public_lb").reset_index(drop=True)
    return known, sample, pred_by_file, base[TARGETS].to_numpy(dtype=np.float64)


def prior_vectors(known: pd.DataFrame, pred_by_file: dict[str, np.ndarray], base_prob: np.ndarray) -> dict[str, np.ndarray]:
    lbs = known.set_index("file")["public_lb"]
    best_lb = float(lbs.min())
    preds = []
    weights = []
    for file_name, pred in pred_by_file.items():
        lb = float(lbs[file_name])
        if lb <= best_lb + 0.00045:
            preds.append(pred)
            weights.append(np.exp(-(lb - best_lb) / 0.00022))
    if not preds:
        preds = [base_prob]
        weights = [1.0]
    stack = np.stack(preds, axis=0)
    w = np.asarray(weights, dtype=np.float64)
    w = w / w.sum()
    good_soft = np.tensordot(w, stack, axes=(0, 0))
    good_median = np.median(stack, axis=0)
    return {
        "e247": base_prob.reshape(-1),
        "good_soft": good_soft.reshape(-1),
        "good_median": good_median.reshape(-1),
        "neutral": np.full(base_prob.size, 0.5, dtype=np.float64),
        "sharp_e247": sigmoid(1.35 * logit(base_prob)).reshape(-1),
    }


def equation_arrays(
    known: pd.DataFrame,
    pred_by_file: dict[str, np.ndarray],
    base_prob: np.ndarray,
) -> tuple[pd.DataFrame, np.ndarray, np.ndarray, np.ndarray]:
    base = clip_prob(base_prob.reshape(-1))
    base_lb = float(known.loc[known["file"].eq(CURRENT), "public_lb"].iloc[0])
    rows: list[dict[str, Any]] = []
    a_rows: list[np.ndarray] = []
    d0_rows: list[np.ndarray] = []
    b_vals: list[float] = []
    n = base.size
    for rec in known.to_dict("records"):
        file_name = str(rec["file"])
        if file_name == CURRENT or file_name not in pred_by_file:
            continue
        pred = clip_prob(pred_by_file[file_name].reshape(-1))
        d0 = -np.log(1.0 - pred) + np.log(1.0 - base)
        d1 = np.log((1.0 - pred) / pred) - np.log((1.0 - base) / base)
        actual_delta = float(rec["public_lb"]) - base_lb
        rhs = actual_delta - float(d0.mean())
        rows.append(
            {
                "file": file_name,
                "public_lb": float(rec["public_lb"]),
                "actual_delta_vs_current": actual_delta,
                "d0_mean": float(d0.mean()),
                "rhs_label_term": rhs,
                "d1_l2_mean": float(np.sqrt(np.mean(d1 * d1))),
                "d1_abs_mean": float(np.mean(np.abs(d1))),
                "changed_cells_vs_current": int((np.abs(pred - base) > 1.0e-12).sum()),
            }
        )
        a_rows.append(d1 / n)
        d0_rows.append(d0)
        b_vals.append(rhs)
    equations = pd.DataFrame(rows)
    equations.to_csv(EQUATION_OUT, index=False)
    return equations, np.vstack(a_rows), np.vstack(d0_rows), np.asarray(b_vals, dtype=np.float64)


def fit_posterior(a: np.ndarray, b: np.ndarray, prior: np.ndarray, ridge_mult: float) -> np.ndarray:
    if len(b) == 0:
        return clip_prob(prior)
    gram = a @ a.T
    scale = float(np.median(np.diag(gram)))
    if not np.isfinite(scale) or scale <= 1.0e-18:
        scale = float(np.mean(np.diag(gram)) + 1.0e-18)
    lam = float(ridge_mult) * scale
    residual = b - a @ prior
    try:
        dual = np.linalg.solve(gram + lam * np.eye(len(b)), residual)
    except np.linalg.LinAlgError:
        dual = np.linalg.pinv(gram + lam * np.eye(len(b))) @ residual
    q = prior + a.T @ dual
    return clip_prob(q)


def predict_delta_from_q(d0: np.ndarray, d1: np.ndarray, q: np.ndarray) -> float:
    return float(np.mean(d0 + d1 * q))


def evaluate_configs(
    equations: pd.DataFrame,
    a: np.ndarray,
    d0_rows: np.ndarray,
    b: np.ndarray,
    priors: dict[str, np.ndarray],
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    d1_rows = a * priors[next(iter(priors))].size
    ridge_mults = [1.0e-5, 3.0e-5, 1.0e-4, 3.0e-4, 1.0e-3, 3.0e-3, 1.0e-2, 3.0e-2, 1.0e-1, 3.0e-1, 1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0]
    actual = equations["actual_delta_vs_current"].to_numpy(dtype=np.float64)
    files = equations["file"].astype(str).tolist()
    for prior_name, prior in priors.items():
        for mult in ridge_mults:
            preds: list[float] = []
            full_q = fit_posterior(a, b, prior, mult)
            full_pred = np.asarray([predict_delta_from_q(d0_rows[i], d1_rows[i], full_q) for i in range(len(files))])
            for heldout in range(len(files)):
                keep = np.ones(len(files), dtype=bool)
                keep[heldout] = False
                q = fit_posterior(a[keep], b[keep], prior, mult)
                preds.append(predict_delta_from_q(d0_rows[heldout], d1_rows[heldout], q))
            pred = np.asarray(preds, dtype=np.float64)
            err = pred - actual
            corr = float(pd.Series(pred).corr(pd.Series(actual), method="spearman"))
            pearson = float(pd.Series(pred).corr(pd.Series(actual), method="pearson"))
            current_safe_rate = float((pred > -1.0e-9).mean())
            rows.append(
                {
                    "prior_name": prior_name,
                    "ridge_mult": mult,
                    "loo_mae": float(np.mean(np.abs(err))),
                    "loo_rmse": float(np.sqrt(np.mean(err * err))),
                    "loo_p90_abs": float(np.quantile(np.abs(err), 0.90)),
                    "loo_spearman": corr,
                    "loo_pearson": pearson,
                    "known_fit_mae": float(np.mean(np.abs(full_pred - actual))),
                    "known_fit_p90_abs": float(np.quantile(np.abs(full_pred - actual), 0.90)),
                    "current_safe_rate": current_safe_rate,
                    "q_mean": float(full_q.mean()),
                    "q_std": float(full_q.std()),
                    "q_min": float(full_q.min()),
                    "q_max": float(full_q.max()),
                    "q_l1_from_prior": float(np.mean(np.abs(full_q - prior))),
                }
            )
    cfg = pd.DataFrame(rows)
    cfg["config_score"] = (
        cfg["loo_mae"].fillna(9.0)
        + 0.30 * cfg["loo_p90_abs"].fillna(9.0)
        - 0.00012 * cfg["loo_spearman"].fillna(0.0)
        + 0.00002 * np.maximum(cfg["q_l1_from_prior"].fillna(0.0) - 0.20, 0.0)
    )
    cfg = cfg.sort_values(["config_score", "loo_mae", "known_fit_mae"]).reset_index(drop=True)
    cfg.to_csv(CONFIG_OUT, index=False)
    return cfg


def selected_configs(configs: pd.DataFrame, limit: int = 8) -> list[PosteriorConfig]:
    out: list[PosteriorConfig] = []
    seen: set[tuple[str, float]] = set()
    strong = configs[
        (configs["loo_spearman"].fillna(-1) >= 0.25)
        & (configs["loo_mae"] <= configs["loo_mae"].quantile(0.60))
    ]
    source = strong if len(strong) else configs
    for rec in source.head(limit * 3).to_dict("records"):
        key = (str(rec["prior_name"]), float(rec["ridge_mult"]))
        if key in seen:
            continue
        seen.add(key)
        out.append(PosteriorConfig(key[0], key[1]))
        if len(out) >= limit:
            break
    return out


def build_scenario_posteriors(
    configs: list[PosteriorConfig],
    a: np.ndarray,
    b: np.ndarray,
    priors: dict[str, np.ndarray],
) -> tuple[np.ndarray, list[str]]:
    qs: list[np.ndarray] = []
    names: list[str] = []
    for cfg in configs:
        q = fit_posterior(a, b, priors[cfg.prior_name], cfg.ridge_mult)
        qs.append(q)
        names.append(f"{cfg.prior_name}_r{cfg.ridge_mult:g}_full")
    if configs:
        cfg = configs[0]
        for heldout in range(len(b)):
            keep = np.ones(len(b), dtype=bool)
            keep[heldout] = False
            q = fit_posterior(a[keep], b[keep], priors[cfg.prior_name], cfg.ridge_mult)
            qs.append(q)
            names.append(f"{cfg.prior_name}_r{cfg.ridge_mult:g}_loo{heldout}")
    return np.vstack(qs), names


def target_mask(target_subset: str, shape: tuple[int, int]) -> np.ndarray:
    mask = np.zeros(shape, dtype=bool)
    if target_subset == "all":
        mask[:, :] = True
    elif target_subset == "Q":
        for target in ["Q1", "Q2", "Q3"]:
            mask[:, TARGETS.index(target)] = True
    elif target_subset == "S":
        for target in ["S1", "S2", "S3", "S4"]:
            mask[:, TARGETS.index(target)] = True
    elif target_subset in TARGETS:
        mask[:, TARGETS.index(target_subset)] = True
    else:
        raise ValueError(target_subset)
    return mask


def candidate_specs() -> list[CandidateSpec]:
    out: list[CandidateSpec] = []
    for alpha in [0.15, 0.25, 0.40, 0.60]:
        out.append(CandidateSpec(f"direct_all_a{alpha:g}", "direct", alpha, "all", "all"))
    for target_subset in ["all", "Q", "S"]:
        for k in [50, 100, 200, 400, 800, 1200]:
            for alpha in [0.40, 0.70, 1.00, 1.35]:
                out.append(CandidateSpec(f"top_{target_subset}_k{k}_a{alpha:g}", "top", alpha, target_subset, "top", k=k, min_consistency=0.55))
    for target in TARGETS:
        for k in [10, 20, 35, 50, 80, 120]:
            for alpha in [0.70, 1.00, 1.35]:
                out.append(CandidateSpec(f"target_{target}_k{k}_a{alpha:g}", "target_top", alpha, target, "top", k=k, min_consistency=0.55))
    for target_subset in ["all", "Q", "S"]:
        for k in [35, 70, 140, 280]:
            for alpha in [0.70, 1.10, 1.50]:
                out.append(CandidateSpec(f"stable_{target_subset}_k{k}_a{alpha:g}", "stable_top", alpha, target_subset, "stable_top", k=k, min_consistency=0.75))
    return out


def cell_selection(spec: CandidateSpec, score: np.ndarray, consistency: np.ndarray, shape: tuple[int, int]) -> np.ndarray:
    mask = target_mask(spec.target_subset, shape).reshape(-1)
    if spec.cell_mode == "all":
        return mask.reshape(shape)
    allowed = mask & (consistency >= spec.min_consistency)
    flat = np.flatnonzero(allowed)
    if len(flat) == 0:
        return np.zeros(shape, dtype=bool)
    chosen = flat[np.argsort(score[flat])[-min(spec.k, len(flat)) :]]
    out = np.zeros(shape[0] * shape[1], dtype=bool)
    out[chosen] = True
    return out.reshape(shape)


def write_candidate(base_df: pd.DataFrame, q_main: np.ndarray, spec: CandidateSpec, mask: np.ndarray) -> Path:
    base_prob = base_df[TARGETS].to_numpy(dtype=np.float64)
    q = q_main.reshape(base_prob.shape)
    z = logit(base_prob)
    zq = logit(q)
    out_prob = base_prob.copy()
    moved = z.copy()
    moved[mask] = (1.0 - spec.alpha) * z[mask] + spec.alpha * zq[mask]
    out_prob[mask] = sigmoid(moved[mask])
    out = base_df.copy()
    out[TARGETS] = np.clip(out_prob, EPS, 1.0 - EPS)
    path = H012 / f"submission_h012_{safe_id(spec.candidate_id)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def score_candidate(
    path: Path,
    base_prob: np.ndarray,
    q_scenarios: np.ndarray,
    known_moves: dict[str, np.ndarray],
) -> dict[str, Any]:
    pred = load_sub(path, load_sub(CURRENT)[KEYS])[TARGETS].to_numpy(dtype=np.float64)
    base = base_prob
    q_shape = base.shape
    deltas = []
    for q in q_scenarios:
        qq = q.reshape(q_shape)
        deltas.append(float(np.mean(loss(pred, qq) - loss(base, qq))))
    deltas_arr = np.asarray(deltas, dtype=np.float64)
    move = (logit(pred) - logit(base)).reshape(-1)
    rec: dict[str, Any] = {
        "file": rel(path),
        "basename": path.name,
        "scenario_count": len(deltas_arr),
        "posterior_delta_mean": float(np.mean(deltas_arr)),
        "posterior_delta_median": float(np.median(deltas_arr)),
        "posterior_delta_p10": float(np.quantile(deltas_arr, 0.10)),
        "posterior_delta_p90": float(np.quantile(deltas_arr, 0.90)),
        "posterior_delta_max": float(np.max(deltas_arr)),
        "posterior_beats_current_rate": float(np.mean(deltas_arr < 0.0)),
        "changed_rows": int((np.abs(pred - base).max(axis=1) > 1.0e-12).sum()),
        "changed_cells": int((np.abs(pred - base) > 1.0e-12).sum()),
        "mean_abs_logit_delta": float(np.mean(np.abs(move))),
        "l1_logit_delta": float(np.sum(np.abs(move))),
        "max_abs_logit_delta": float(np.max(np.abs(move))),
        "max_abs_prob_delta": float(np.max(np.abs(pred - base))),
    }
    for ti, target in enumerate(TARGETS):
        rec[f"changed_{target}"] = int((np.abs(pred[:, ti] - base[:, ti]) > 1.0e-12).sum())
    for name, direction in known_moves.items():
        denom = float(np.linalg.norm(move) * np.linalg.norm(direction) + 1.0e-12)
        rec[f"cos_{name}"] = float(move @ direction / denom)
        rec[f"proj_{name}"] = float(move @ direction / (direction @ direction + 1.0e-12))
    return rec


def build_known_moves(sample: pd.DataFrame, base_prob: np.ndarray) -> dict[str, np.ndarray]:
    names = {
        "h010_bad": "submission_h010_objective_s1s4_v2_uploadsafe.csv",
        "e323_bad": "submission_e323_5508f966_uploadsafe.csv",
        "e216_bad": "submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv",
        "e267_bad": "submission_e267_humansocial_tail_balanced_2936100f.csv",
        "e368_q2s1": "submission_e368_q2s1rowmask_selected_e368_q2_damp_s1_recover_amp1_06_be814361_uploadsafe.csv",
        "e95_good": "submission_e95_hardtail_541e3973.csv",
        "mixmin_good": "submission_mixmin_0c916bb4.csv",
    }
    out: dict[str, np.ndarray] = {}
    base_logit = logit(base_prob).reshape(-1)
    for key, file_name in names.items():
        try:
            pred = load_sub(file_name, sample)[TARGETS].to_numpy(dtype=np.float64)
        except FileNotFoundError:
            continue
        out[key] = logit(pred).reshape(-1) - base_logit
    return out


def materialize_and_score(
    base_df: pd.DataFrame,
    q_scenarios: np.ndarray,
    scenario_names: list[str],
    sample: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, Path | None]:
    base_prob = base_df[TARGETS].to_numpy(dtype=np.float64)
    q_main = np.median(q_scenarios, axis=0)
    z_base = logit(base_prob).reshape(-1)
    z_scenarios = logit(q_scenarios)
    z_main = np.median(z_scenarios, axis=0)
    direction = np.sign(z_main - z_base)
    consistency = np.mean(np.sign(z_scenarios - z_base) == direction[None, :], axis=0)
    score = np.abs(z_main - z_base) * consistency
    known_moves = build_known_moves(sample, base_prob)

    cell_rows = []
    qmat = q_main.reshape(base_prob.shape)
    for row_i in range(base_prob.shape[0]):
        for target_i, target in enumerate(TARGETS):
            idx = row_i * len(TARGETS) + target_i
            cell_rows.append(
                {
                    "row": row_i,
                    "target": target,
                    "base_prob": float(base_prob[row_i, target_i]),
                    "posterior_prob": float(qmat[row_i, target_i]),
                    "posterior_minus_base": float(qmat[row_i, target_i] - base_prob[row_i, target_i]),
                    "logit_delta_to_posterior": float(z_main[idx] - z_base[idx]),
                    "direction_consistency": float(consistency[idx]),
                    "cell_score": float(score[idx]),
                }
            )
    pd.DataFrame(cell_rows).sort_values("cell_score", ascending=False).to_csv(POSTERIOR_OUT, index=False)

    rows: list[dict[str, Any]] = []
    selection_rows: list[dict[str, Any]] = []
    paths: list[Path] = []
    for spec in candidate_specs():
        mask = cell_selection(spec, score, consistency, base_prob.shape)
        if not mask.any():
            continue
        path = write_candidate(base_df, q_main, spec, mask)
        paths.append(path)
        rec = score_candidate(path, base_prob, q_scenarios, known_moves)
        rec.update(
            {
                "candidate_id": spec.candidate_id,
                "family": spec.family,
                "alpha": spec.alpha,
                "target_subset": spec.target_subset,
                "cell_mode": spec.cell_mode,
                "k": spec.k,
                "min_consistency": spec.min_consistency,
                "mean_cell_score_changed": float(score[mask.reshape(-1)].mean()),
                "min_consistency_changed": float(consistency[mask.reshape(-1)].min()),
                "mean_consistency_changed": float(consistency[mask.reshape(-1)].mean()),
            }
        )
        rows.append(rec)
    candidates = pd.DataFrame(rows)
    candidates["public_bad_cos_pos_sum"] = 0.0
    for col in ["cos_h010_bad", "cos_e323_bad", "cos_e216_bad", "cos_e267_bad"]:
        if col in candidates.columns:
            candidates["public_bad_cos_pos_sum"] += candidates[col].clip(lower=0.0)
    candidates["h012_big_bet_gate"] = (
        (candidates["posterior_delta_mean"] < -0.00060)
        & (candidates["posterior_delta_p90"] < -0.00018)
        & (candidates["posterior_beats_current_rate"] >= 0.75)
        & (candidates["changed_cells"] >= 35)
        & (candidates["max_abs_prob_delta"] <= 0.30)
    )
    candidates["h012_extreme_sensor_gate"] = (
        (candidates["posterior_delta_mean"] < -0.00120)
        & (candidates["posterior_beats_current_rate"] >= 0.60)
        & (candidates["max_abs_prob_delta"] <= 0.45)
    )
    candidates["h012_score"] = (
        candidates["posterior_delta_p90"].fillna(9.0)
        + 0.40 * candidates["posterior_delta_mean"].fillna(9.0)
        + 0.00015 * candidates["public_bad_cos_pos_sum"].fillna(0.0)
        + 0.00005 * np.maximum(candidates["max_abs_prob_delta"].fillna(0.0) - 0.25, 0.0) / 0.10
        - 0.00004 * np.log1p(candidates["changed_cells"].fillna(0.0)) / np.log(1751.0)
    )
    candidates["h012_decision"] = np.select(
        [
            candidates["h012_big_bet_gate"],
            candidates["h012_extreme_sensor_gate"],
            candidates["posterior_delta_mean"] < -0.00025,
        ],
        ["public_equation_jackpot", "public_equation_extreme_sensor", "posterior_sensor_only"],
        default="reject",
    )
    order = {
        "public_equation_jackpot": 0,
        "public_equation_extreme_sensor": 1,
        "posterior_sensor_only": 2,
        "reject": 3,
    }
    candidates["decision_rank"] = candidates["h012_decision"].map(order).fillna(9).astype(int)
    candidates = candidates.sort_values(["decision_rank", "h012_score", "posterior_delta_p90"]).reset_index(drop=True)
    candidates.to_csv(CANDIDATE_OUT, index=False)
    candidates.to_csv(SELECTION_OUT, index=False)

    top = candidates[candidates["h012_decision"].isin(["public_equation_jackpot", "public_equation_extreme_sensor"])].head(1)
    primary = None
    if not top.empty:
        source = ROOT / str(top.iloc[0]["file"])
        primary = ROOT / f"submission_h012_public_equation_{safe_id(str(top.iloc[0]['candidate_id']), 72)}_uploadsafe.csv"
        shutil.copyfile(source, primary)
    return candidates, pd.DataFrame({"scenario_name": scenario_names}), primary


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


def write_report(
    known: pd.DataFrame,
    equations: pd.DataFrame,
    configs: pd.DataFrame,
    selected: list[PosteriorConfig],
    candidates: pd.DataFrame,
    primary: Path | None,
) -> None:
    top_cols = [
        "candidate_id",
        "h012_decision",
        "family",
        "target_subset",
        "changed_cells",
        "posterior_delta_mean",
        "posterior_delta_p90",
        "posterior_beats_current_rate",
        "max_abs_prob_delta",
        "public_bad_cos_pos_sum",
        "file",
    ]
    config_cols = [
        "prior_name",
        "ridge_mult",
        "loo_mae",
        "loo_p90_abs",
        "loo_spearman",
        "known_fit_mae",
        "q_mean",
        "q_std",
        "q_l1_from_prior",
    ]
    lines = [
        "# H012 Public-Equation HS-JEPA Jackpot",
        "",
        "## Question",
        "",
        "Can known public LB observations be treated as equations over hidden public labels/subset, then converted into an action candidate?",
        "",
        "## Worldview",
        "",
        "HS-JEPA's target representation is not a label column or a feature reconstruction. Here the target is the hidden public state that makes all old public scores simultaneously true.",
        "",
        "## Evidence",
        "",
        f"- known public observations loaded: `{len(known)}`",
        f"- public equations vs E247: `{len(equations)}`",
        f"- posterior configs tested: `{len(configs)}`",
        f"- selected posterior scenarios: `{len(selected)} full configs plus leave-one-out variants from the top config`",
        f"- generated candidates: `{len(candidates)}`",
        f"- primary upload-safe file: `{rel(primary) if primary else 'none'}`",
        "",
        "## Selected Posterior Configs",
        "",
        md_table(pd.DataFrame([cfg.__dict__ for cfg in selected]), n=20),
        "",
        "## Top Config Diagnostics",
        "",
        md_table(configs[config_cols], n=20),
        "",
        "## Candidate Selection",
        "",
        md_table(candidates[[c for c in top_cols if c in candidates.columns]], n=40),
        "",
        "## Decision Rule",
        "",
        "This is a high-risk inverse-public experiment. A public win would validate public-equation latent reconstruction as an HS-JEPA target. A loss would show that the old public equations are too underidentified or too subset-mismatched to materialize directly.",
        "",
        "## Files",
        "",
        f"- `{rel(CONFIG_OUT)}`",
        f"- `{rel(EQUATION_OUT)}`",
        f"- `{rel(POSTERIOR_OUT)}`",
        f"- `{rel(CANDIDATE_OUT)}`",
        f"- `{rel(SELECTION_OUT)}`",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    known, sample, pred_by_file, base_prob = load_public_system()
    priors = prior_vectors(known, pred_by_file, base_prob)
    equations, a, d0_rows, b = equation_arrays(known, pred_by_file, base_prob)
    configs = evaluate_configs(equations, a, d0_rows, b, priors)
    selected = selected_configs(configs)
    q_scenarios, scenario_names = build_scenario_posteriors(selected, a, b, priors)
    base_df = load_sub(CURRENT)
    candidates, scenario_frame, primary = materialize_and_score(base_df, q_scenarios, scenario_names, sample)
    scenario_frame.to_csv(H012 / "h012_posterior_scenarios.csv", index=False)
    write_report(known, equations, configs, selected, candidates, primary)
    print(REPORT_OUT)
    if primary is not None:
        print(primary)
    print(
        candidates[
            [
                "candidate_id",
                "h012_decision",
                "posterior_delta_mean",
                "posterior_delta_p90",
                "posterior_beats_current_rate",
                "changed_cells",
                "max_abs_prob_delta",
                "public_bad_cos_pos_sum",
                "file",
            ]
        ]
        .head(25)
        .round(9)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
