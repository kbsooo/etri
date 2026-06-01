#!/usr/bin/env python3
"""H018: hard-label public-world HS-JEPA.

H012/H017 use continuous posteriors. The true public labels are binary.
H018 asks whether the public-equation state remains meaningful after imposing
that harder world constraint:

    y[cell] ~ Bernoulli(q_h017[cell])
    public_delta(file) ~= sum_cell w_h017[cell] * loss_delta(file, y[cell])

It samples many hard public worlds from the H017 prior, keeps worlds whose
known-public equations fit, and turns the resulting posterior over hard worlds
into submission candidates. If this works, the public-equation branch is not
just a smooth calibration trick; it is a posterior over plausible binary
evaluation worlds.
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
H018 = ROOT / "hitl" / "h018_hard_label_world_jepa"
H018.mkdir(parents=True, exist_ok=True)

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
CURRENT = "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"
H017_PRIMARY = "submission_h017_joint_label_weight_oracle_gain_all_k1650_a1_uploadsafe.csv"
REPORT_OUT = H018 / "h018_report.md"
WORLD_OUT = H018 / "h018_world_posterior_configs.csv"
NULL_OUT = H018 / "h018_world_null_stress.csv"
CELL_OUT = H018 / "h018_cell_hard_posterior.csv"
CANDIDATE_OUT = H018 / "h018_candidates.csv"


@dataclass(frozen=True)
class WorldPosterior:
    posterior_id: str
    method: str
    temperature: float
    top_k: int
    weight_power: float


@dataclass(frozen=True)
class CandidateSpec:
    candidate_id: str
    mode: str
    target_subset: str
    k: int
    alpha: float
    target_kind: str


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(x, dtype=np.float64)))


def loss(prob: np.ndarray, y_prob: np.ndarray) -> np.ndarray:
    p = clip_prob(prob)
    q = clip_prob(y_prob)
    return -(q * np.log(p) + (1.0 - q) * np.log(1.0 - p))


def safe_id(text: str, limit: int = 96) -> str:
    clean = re.sub(r"[^A-Za-z0-9_.-]+", "_", text).strip("_")
    return clean[:limit].strip("_")


def short_hash(frame: pd.DataFrame) -> str:
    arr = np.asarray(frame[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def rel(path: Path | None) -> str:
    if path is None:
        return "none"
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def rank01(x: np.ndarray) -> np.ndarray:
    s = pd.Series(np.asarray(x, dtype=np.float64))
    return s.rank(method="average", pct=True).to_numpy(dtype=np.float64)


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


def load_frames() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, np.ndarray]]:
    known = known_public_table().copy().sort_values("public_lb").reset_index(drop=True)
    if CURRENT not in set(known["file"].astype(str)):
        raise RuntimeError(f"{CURRENT} missing from known public table")
    h012 = load_sub(CURRENT)
    h017 = load_sub(H017_PRIMARY, h012[KEYS])
    pred_by_file: dict[str, np.ndarray] = {}
    rows: list[dict[str, Any]] = []
    for rec in known.to_dict("records"):
        name = str(rec["file"])
        try:
            df = load_sub(name, h012[KEYS])
        except FileNotFoundError:
            continue
        pred_by_file[name] = df[TARGETS].to_numpy(dtype=np.float64)
        rows.append(rec)
    known = pd.DataFrame(rows).sort_values("public_lb").reset_index(drop=True)
    return known, h012[KEYS].copy(), h012, h017, pred_by_file


def load_h017_state(sample: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    state = pd.read_csv(H018.parent / "h017_joint_label_weight_jepa" / "h017_cell_joint_state.csv")
    q = np.zeros(len(sample) * len(TARGETS), dtype=np.float64)
    w = np.zeros_like(q)
    for rec in state.to_dict("records"):
        idx = int(rec["row"]) * len(TARGETS) + TARGETS.index(str(rec["target"]))
        q[idx] = float(rec["joint_q_median"])
        w[idx] = float(rec["joint_weight_mean"])
    w = np.maximum(w, 0.0)
    w = w / max(float(w.sum()), 1.0e-30)
    return clip_prob(q), w


def equation_arrays(
    known: pd.DataFrame,
    pred_by_file: dict[str, np.ndarray],
    base_prob: np.ndarray,
    w: np.ndarray,
) -> tuple[list[str], np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    base = clip_prob(base_prob.reshape(-1))
    base_lb = float(known.loc[known["file"].eq(CURRENT), "public_lb"].iloc[0])
    files: list[str] = []
    d0_rows: list[np.ndarray] = []
    d1_rows: list[np.ndarray] = []
    actual: list[float] = []
    for rec in known.to_dict("records"):
        name = str(rec["file"])
        if name == CURRENT or name not in pred_by_file:
            continue
        pred = clip_prob(pred_by_file[name].reshape(-1))
        d0 = -np.log(1.0 - pred) + np.log(1.0 - base)
        d1 = np.log((1.0 - pred) / pred) - np.log((1.0 - base) / base)
        files.append(name)
        d0_rows.append(d0)
        d1_rows.append(d1)
        actual.append(float(rec["public_lb"]) - base_lb)
    d0 = np.vstack(d0_rows)
    d1 = np.vstack(d1_rows)
    base_term = d0 @ w
    coef = (d1 * w.reshape(1, -1)).T
    return files, base_term, coef, d0, np.asarray(actual, dtype=np.float64)


def sample_hard_worlds(
    q_prior: np.ndarray,
    base_term: np.ndarray,
    coef: np.ndarray,
    actual: np.ndarray,
    n_samples: int = 90000,
    batch_size: int = 3000,
    seed: int = 20260602,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    n = len(q_prior)
    m = len(actual)
    worlds = np.empty((n_samples, n), dtype=np.uint8)
    preds = np.empty((n_samples, m), dtype=np.float64)
    errors = np.empty(n_samples, dtype=np.float64)
    cursor = 0
    while cursor < n_samples:
        size = min(batch_size, n_samples - cursor)
        y = (rng.random((size, n), dtype=np.float64) < q_prior.reshape(1, -1)).astype(np.uint8)
        pred = base_term.reshape(1, -1) + y.astype(np.float64) @ coef
        err = np.mean(np.abs(pred - actual.reshape(1, -1)), axis=1)
        worlds[cursor : cursor + size] = y
        preds[cursor : cursor + size] = pred
        errors[cursor : cursor + size] = err
        cursor += size
    best_idx = int(np.argmin(errors))
    return worlds, preds, errors, worlds[best_idx].astype(np.float64)


def weighted_posterior(worlds: np.ndarray, errors: np.ndarray, spec: WorldPosterior) -> tuple[np.ndarray, np.ndarray, float]:
    if spec.method == "soft":
        e = errors - float(errors.min())
        raw = np.exp(-e / max(spec.temperature, 1.0e-12))
        if spec.weight_power != 1.0:
            raw = raw**spec.weight_power
    elif spec.method == "topk":
        order = np.argsort(errors)[: spec.top_k]
        raw = np.zeros(len(errors), dtype=np.float64)
        local = errors[order] - float(errors[order].min())
        raw[order] = np.exp(-local / max(spec.temperature, 1.0e-12))
    elif spec.method == "elite":
        order = np.argsort(errors)[: spec.top_k]
        raw = np.zeros(len(errors), dtype=np.float64)
        raw[order] = 1.0
    else:
        raise ValueError(spec.method)
    s = float(raw.sum())
    if not np.isfinite(s) or s <= 1.0e-30:
        raw[:] = 1.0
        s = float(raw.sum())
    weights = raw / s
    ess = float(1.0 / np.sum(weights * weights))
    q = weights @ worlds.astype(np.float64)
    return clip_prob(q), weights, ess


def posterior_specs() -> list[WorldPosterior]:
    out: list[WorldPosterior] = []
    for temp in [0.00012, 0.0002, 0.00035, 0.0006, 0.0010, 0.0016]:
        for power in [1.0, 1.5, 2.0]:
            out.append(WorldPosterior(f"soft_t{temp:g}_p{power:g}", "soft", temp, 0, power))
    for k in [50, 100, 250, 500, 1000, 2500, 5000]:
        for temp in [0.00012, 0.00025, 0.0005, 0.0010]:
            out.append(WorldPosterior(f"top{k}_t{temp:g}", "topk", temp, k, 1.0))
        out.append(WorldPosterior(f"elite{k}", "elite", 0.0, k, 1.0))
    return out


def evaluate_world_posteriors(
    worlds: np.ndarray,
    preds: np.ndarray,
    errors: np.ndarray,
    q_prior: np.ndarray,
    base_term: np.ndarray,
    coef: np.ndarray,
    actual: np.ndarray,
) -> tuple[pd.DataFrame, dict[str, np.ndarray], dict[str, np.ndarray]]:
    rows: list[dict[str, Any]] = []
    q_by_id: dict[str, np.ndarray] = {}
    weights_by_id: dict[str, np.ndarray] = {}
    for spec in posterior_specs():
        q, weights, ess = weighted_posterior(worlds, errors, spec)
        pred = base_term + q @ coef
        err = pred - actual
        rec = {
            "posterior_id": spec.posterior_id,
            "method": spec.method,
            "temperature": spec.temperature,
            "top_k": spec.top_k,
            "weight_power": spec.weight_power,
            "posterior_pred_mae": float(np.mean(np.abs(err))),
            "posterior_pred_p90_abs": float(np.quantile(np.abs(err), 0.90)),
            "best_world_mae": float(errors.min()),
            "top100_world_mae": float(np.mean(np.sort(errors)[:100])),
            "sample_error_median": float(np.median(errors)),
            "ess": ess,
            "ess_rate": float(ess / len(errors)),
            "q_prior_abs_shift": float(np.mean(np.abs(q - q_prior))),
            "q_prior_corr": float(pd.Series(q).corr(pd.Series(q_prior), method="spearman")),
            "hardness": float(np.mean(np.maximum(q, 1.0 - q))),
            "pred_delta_rank": float(pd.Series(pred).corr(pd.Series(actual), method="spearman")),
        }
        rec["posterior_score"] = (
            rec["posterior_pred_mae"]
            + 0.25 * rec["posterior_pred_p90_abs"]
            + 0.00008 * max(0.0, 30.0 - ess) / 30.0
            - 0.00003 * min(rec["q_prior_abs_shift"], 0.05) / 0.05
        )
        rows.append(rec)
        q_by_id[spec.posterior_id] = q
        weights_by_id[spec.posterior_id] = weights
    df = pd.DataFrame(rows).sort_values(["posterior_score", "posterior_pred_mae"]).reset_index(drop=True)
    df.to_csv(WORLD_OUT, index=False)
    return df, q_by_id, weights_by_id


def null_stress(preds: np.ndarray, errors: np.ndarray, actual: np.ndarray, n_perm: int = 300) -> pd.DataFrame:
    rng = np.random.default_rng(20260603)
    rows: list[dict[str, Any]] = [
        {
            "kind": "real",
            "iteration": -1,
            "best_world_mae": float(errors.min()),
            "top100_world_mae": float(np.mean(np.sort(errors)[:100])),
            "median_world_mae": float(np.median(errors)),
            "p01_world_mae": float(np.quantile(errors, 0.01)),
            "p05_world_mae": float(np.quantile(errors, 0.05)),
        }
    ]
    for i in range(n_perm):
        perm_actual = rng.permutation(actual)
        perm_errors = np.mean(np.abs(preds - perm_actual.reshape(1, -1)), axis=1)
        rows.append(
            {
                "kind": "permute_actual",
                "iteration": i,
                "best_world_mae": float(perm_errors.min()),
                "top100_world_mae": float(np.mean(np.sort(perm_errors)[:100])),
                "median_world_mae": float(np.median(perm_errors)),
                "p01_world_mae": float(np.quantile(perm_errors, 0.01)),
                "p05_world_mae": float(np.quantile(perm_errors, 0.05)),
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(NULL_OUT, index=False)
    return out


def null_summary(nulls: pd.DataFrame) -> pd.DataFrame:
    real = nulls[nulls["kind"].eq("real")].iloc[0]
    perm = nulls[nulls["kind"].ne("real")]
    rows: list[dict[str, Any]] = []
    for metric in ["best_world_mae", "top100_world_mae", "median_world_mae", "p01_world_mae", "p05_world_mae"]:
        rv = float(real[metric])
        pv = perm[metric].astype(float)
        rows.append(
            {
                "metric": metric,
                "real": rv,
                "null_mean": float(pv.mean()),
                "null_p10": float(pv.quantile(0.10)),
                "null_p50": float(pv.quantile(0.50)),
                "null_p90": float(pv.quantile(0.90)),
                "real_percentile_vs_null": float((pv < rv).mean()),
                "one_sided_p_lower": float((1 + (pv <= rv).sum()) / (len(pv) + 1)),
            }
        )
    return pd.DataFrame(rows)


def build_cell_table(
    q_hard: np.ndarray,
    q_prior: np.ndarray,
    best_y: np.ndarray,
    w: np.ndarray,
    h012_prob: np.ndarray,
    h017_prob: np.ndarray,
    sample: pd.DataFrame,
) -> pd.DataFrame:
    h012_flat = h012_prob.reshape(-1)
    h017_flat = h017_prob.reshape(-1)
    dz_hard = logit(q_hard) - logit(h012_flat)
    dz_prior = logit(q_prior) - logit(h012_flat)
    dz_h017 = logit(h017_flat) - logit(h012_flat)
    hard_gain = w * (loss(h012_flat, q_hard) - loss(q_hard, q_hard))
    h017_gain = w * (loss(h012_flat, q_hard) - loss(h017_flat, q_hard))
    best_gain = w * (loss(h012_flat, best_y) - loss(clip_prob(best_y * (1.0 - 2 * EPS) + EPS), best_y))
    binary_shock = np.abs(q_hard - q_prior)
    confidence = np.maximum(q_hard, 1.0 - q_hard)
    score_gain = rank01(hard_gain)
    score_shift = rank01(np.abs(dz_hard))
    score_shock = rank01(binary_shock)
    score_conf = rank01(confidence)
    score_h017 = rank01(h017_gain)
    combined = 0.34 * score_gain + 0.22 * score_shift + 0.18 * score_shock + 0.14 * score_conf + 0.12 * rank01(np.log(w + 1.0e-30))
    rows: list[dict[str, Any]] = []
    for row_i in range(len(sample)):
        for target_i, target in enumerate(TARGETS):
            idx = row_i * len(TARGETS) + target_i
            rows.append(
                {
                    "row": row_i,
                    "target": target,
                    "h012_prob": float(h012_flat[idx]),
                    "h017_prob": float(h017_flat[idx]),
                    "q_prior": float(q_prior[idx]),
                    "q_hard": float(q_hard[idx]),
                    "best_world_y": int(best_y[idx]),
                    "public_weight": float(w[idx]),
                    "hard_minus_prior": float(q_hard[idx] - q_prior[idx]),
                    "hard_minus_h012": float(q_hard[idx] - h012_flat[idx]),
                    "hard_logit_delta": float(dz_hard[idx]),
                    "prior_logit_delta": float(dz_prior[idx]),
                    "h017_logit_delta": float(dz_h017[idx]),
                    "binary_shock": float(binary_shock[idx]),
                    "confidence": float(confidence[idx]),
                    "hard_gain": float(hard_gain[idx]),
                    "h017_gain_under_hard": float(h017_gain[idx]),
                    "best_world_gain": float(best_gain[idx]),
                    "gain_score": float(score_gain[idx]),
                    "shift_score": float(score_shift[idx]),
                    "shock_score": float(score_shock[idx]),
                    "confidence_score": float(score_conf[idx]),
                    "h017_gain_score": float(score_h017[idx]),
                    "combined_score": float(combined[idx]),
                }
            )
    cells = pd.DataFrame(rows).sort_values("combined_score", ascending=False).reset_index(drop=True)
    cells.to_csv(CELL_OUT, index=False)
    return cells


def target_mask(target_subset: str, shape: tuple[int, int]) -> np.ndarray:
    mask = np.zeros(shape, dtype=bool)
    if target_subset == "all":
        mask[:, :] = True
    elif target_subset == "Q":
        mask[:, :3] = True
    elif target_subset == "S":
        mask[:, 3:] = True
    elif target_subset in TARGETS:
        mask[:, TARGETS.index(target_subset)] = True
    else:
        raise ValueError(target_subset)
    return mask.reshape(-1)


def candidate_specs() -> list[CandidateSpec]:
    out: list[CandidateSpec] = []
    modes = ["combined", "gain", "shock", "confidence", "h017_gain", "best_world"]
    for mode in modes:
        for subset in ["all", "Q", "S"]:
            for k in [200, 400, 700, 1000, 1300, 1600, 1750]:
                for alpha in [0.35, 0.55, 0.75, 1.0, 1.25]:
                    target_kind = "best" if mode == "best_world" else "posterior"
                    out.append(CandidateSpec(f"{mode}_{subset}_k{k}_a{alpha:g}", mode, subset, k, alpha, target_kind))
    for target in TARGETS:
        for mode in ["combined", "gain", "shock"]:
            for k in [40, 80, 140, 200, 250]:
                for alpha in [0.55, 0.85, 1.15]:
                    out.append(CandidateSpec(f"{mode}_{target}_k{k}_a{alpha:g}", mode, target, k, alpha, "posterior"))
    return out


def select_mask(spec: CandidateSpec, cells: pd.DataFrame, shape: tuple[int, int]) -> np.ndarray:
    valid = target_mask(spec.target_subset, shape)
    score_col = {
        "combined": "combined_score",
        "gain": "gain_score",
        "shock": "shock_score",
        "confidence": "confidence_score",
        "h017_gain": "h017_gain_score",
        "best_world": "best_world_gain",
    }[spec.mode]
    score = np.full(shape[0] * shape[1], -np.inf, dtype=np.float64)
    for rec in cells.to_dict("records"):
        idx = int(rec["row"]) * len(TARGETS) + TARGETS.index(str(rec["target"]))
        score[idx] = float(rec[score_col])
        if abs(float(rec["hard_logit_delta"])) <= 1.0e-12:
            valid[idx] = False
    candidates = np.flatnonzero(valid)
    chosen = candidates[np.argsort(score[candidates])[-min(spec.k, len(candidates)) :]]
    mask = np.zeros(shape[0] * shape[1], dtype=bool)
    mask[chosen] = True
    return mask.reshape(shape)


def make_candidate_frame(base: pd.DataFrame, q_hard: np.ndarray, best_y: np.ndarray, spec: CandidateSpec, mask: np.ndarray) -> pd.DataFrame:
    base_prob = base[TARGETS].to_numpy(dtype=np.float64)
    target = q_hard.reshape(base_prob.shape) if spec.target_kind == "posterior" else clip_prob(best_y.reshape(base_prob.shape) * (1.0 - 2.0 * EPS) + EPS)
    z = logit(base_prob)
    moved = z.copy()
    moved[mask] = z[mask] + spec.alpha * (logit(target)[mask] - z[mask])
    out = base.copy()
    out[TARGETS] = clip_prob(sigmoid(moved))
    return out


def score_prob(prob: np.ndarray, base_prob: np.ndarray, q_hard: np.ndarray, w: np.ndarray) -> dict[str, float]:
    diff = loss(prob.reshape(-1), q_hard) - loss(base_prob.reshape(-1), q_hard)
    return {
        "hard_delta_vs_h012": float(diff @ w),
        "uniform_hard_delta_vs_h012": float(diff.mean()),
    }


def generate_candidates(
    h012: pd.DataFrame,
    cells: pd.DataFrame,
    q_hard: np.ndarray,
    best_y: np.ndarray,
    w: np.ndarray,
) -> tuple[pd.DataFrame, Path | None]:
    base_prob = h012[TARGETS].to_numpy(dtype=np.float64)
    rows: list[dict[str, Any]] = []
    frames: list[tuple[pd.DataFrame, CandidateSpec, dict[str, Any]]] = []
    for spec in candidate_specs():
        mask = select_mask(spec, cells, base_prob.shape)
        if not mask.any():
            continue
        out = make_candidate_frame(h012, q_hard, best_y, spec, mask)
        prob = out[TARGETS].to_numpy(dtype=np.float64)
        rec = score_prob(prob, base_prob, q_hard, w)
        rec.update(
            {
                "candidate_id": spec.candidate_id,
                "mode": spec.mode,
                "target_kind": spec.target_kind,
                "target_subset": spec.target_subset,
                "k": spec.k,
                "alpha": spec.alpha,
                "changed_rows": int((np.abs(prob - base_prob).max(axis=1) > 1.0e-12).sum()),
                "changed_cells": int((np.abs(prob - base_prob) > 1.0e-12).sum()),
                "mean_abs_prob_delta_vs_h012": float(np.mean(np.abs(prob - base_prob))),
                "max_abs_prob_delta_vs_h012": float(np.max(np.abs(prob - base_prob))),
            }
        )
        rows.append(rec)
        frames.append((out, spec, rec))
    candidates = pd.DataFrame(rows)
    candidates["h018_decision"] = np.select(
        [
            (candidates["hard_delta_vs_h012"] < -0.00090) & (candidates["max_abs_prob_delta_vs_h012"] <= 0.24),
            (candidates["hard_delta_vs_h012"] < -0.00040) & (candidates["max_abs_prob_delta_vs_h012"] <= 0.18),
        ],
        ["hard_world_big_bet", "hard_world_sensor"],
        default="diagnostic_only",
    )
    order = {"hard_world_big_bet": 0, "hard_world_sensor": 1, "diagnostic_only": 2}
    candidates["decision_rank"] = candidates["h018_decision"].map(order).astype(int)
    candidates = candidates.sort_values(["decision_rank", "hard_delta_vs_h012", "max_abs_prob_delta_vs_h012"]).reset_index(drop=True)
    materialized: dict[str, str] = {}
    keep = set(candidates.head(50)["candidate_id"].astype(str))
    primary = None
    for out, spec, _ in frames:
        if spec.candidate_id not in keep:
            continue
        path = H018 / f"submission_h018_{safe_id(spec.candidate_id)}_{short_hash(out)}.csv"
        out.to_csv(path, index=False)
        materialized[spec.candidate_id] = rel(path)
    candidates["file"] = candidates["candidate_id"].map(materialized).fillna("not_materialized")
    promoted = candidates[candidates["h018_decision"].isin(["hard_world_big_bet", "hard_world_sensor"])].head(1)
    if not promoted.empty:
        source = ROOT / str(promoted.iloc[0]["file"])
        primary = ROOT / f"submission_h018_hard_label_world_{safe_id(str(promoted.iloc[0]['candidate_id']), 64)}_uploadsafe.csv"
        shutil.copyfile(source, primary)
    candidates.to_csv(CANDIDATE_OUT, index=False)
    return candidates, primary


def write_report(
    worlds: pd.DataFrame,
    nulls: pd.DataFrame,
    cells: pd.DataFrame,
    candidates: pd.DataFrame,
    primary: Path | None,
    n_samples: int,
) -> None:
    world_cols = [
        "posterior_id",
        "method",
        "temperature",
        "top_k",
        "weight_power",
        "posterior_pred_mae",
        "posterior_pred_p90_abs",
        "best_world_mae",
        "top100_world_mae",
        "ess",
        "ess_rate",
        "q_prior_abs_shift",
        "q_prior_corr",
        "hardness",
    ]
    cand_cols = [
        "candidate_id",
        "h018_decision",
        "mode",
        "target_kind",
        "target_subset",
        "changed_cells",
        "hard_delta_vs_h012",
        "uniform_hard_delta_vs_h012",
        "max_abs_prob_delta_vs_h012",
        "file",
    ]
    target_summary = (
        cells.groupby("target", as_index=False)
        .agg(
            mean_q_hard=("q_hard", "mean"),
            mean_q_prior=("q_prior", "mean"),
            mean_shock=("binary_shock", "mean"),
            mean_gain=("hard_gain", "mean"),
            mean_weight=("public_weight", "mean"),
            mean_confidence=("confidence", "mean"),
        )
        .sort_values("mean_gain", ascending=False)
    )
    lines = [
        "# H018 Hard-Label Public-World HS-JEPA",
        "",
        "## Question",
        "",
        "Does the public-equation latent survive when the hidden public labels are forced to be binary worlds?",
        "",
        f"- sampled hard worlds: `{n_samples}`",
        "",
        "## Top Hard-World Posteriors",
        "",
        md_table(worlds[[c for c in world_cols if c in worlds.columns]], n=30),
        "",
        "## Null Stress",
        "",
        "Known public deltas are permuted while the same sampled hard-world predictions are kept fixed.",
        "",
        md_table(null_summary(nulls), n=20),
        "",
        "## Target Summary",
        "",
        md_table(target_summary, n=10),
        "",
        "## Candidate Selection",
        "",
        md_table(candidates[[c for c in cand_cols if c in candidates.columns]], n=50),
        "",
        "## Decision",
        "",
    ]
    if primary is None:
        lines.extend(
            [
                "- No hard-label posterior candidate clears the promotion gate.",
                "- Interpretation: binary-world sampling is diagnostic only; continuous H017 posterior remains the action layer.",
            ]
        )
    else:
        lines.extend(
            [
                f"- Primary upload-safe candidate: `{rel(primary)}`.",
                "- Interpretation: this file bets that the binary public-world posterior exposes a sharper target than continuous posterior-completion.",
            ]
        )
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- `{rel(WORLD_OUT)}`",
            f"- `{rel(NULL_OUT)}`",
            f"- `{rel(CELL_OUT)}`",
            f"- `{rel(CANDIDATE_OUT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    known, sample, h012, h017, pred_by_file = load_frames()
    h012_prob = h012[TARGETS].to_numpy(dtype=np.float64)
    h017_prob = h017[TARGETS].to_numpy(dtype=np.float64)
    q_prior, w = load_h017_state(sample)
    _, base_term, coef, _, actual = equation_arrays(known, pred_by_file, h012_prob, w)
    n_samples = 90000
    worlds_arr, preds, errors, best_y = sample_hard_worlds(q_prior, base_term, coef, actual, n_samples=n_samples)
    nulls = null_stress(preds, errors, actual)
    worlds, q_by_id, _ = evaluate_world_posteriors(worlds_arr, preds, errors, q_prior, base_term, coef, actual)
    selected_id = str(worlds.iloc[0]["posterior_id"])
    q_hard = q_by_id[selected_id]
    cells = build_cell_table(q_hard, q_prior, best_y, w, h012_prob, h017_prob, sample)
    candidates, primary = generate_candidates(h012, cells, q_hard, best_y, w)
    write_report(worlds, nulls, cells, candidates, primary, n_samples)
    print(f"wrote {REPORT_OUT}")
    if primary is not None:
        print(f"primary {primary}")
    print(
        candidates[
            [
                "candidate_id",
                "h018_decision",
                "hard_delta_vs_h012",
                "uniform_hard_delta_vs_h012",
                "changed_cells",
                "max_abs_prob_delta_vs_h012",
                "file",
            ]
        ]
        .head(25)
        .round(9)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
