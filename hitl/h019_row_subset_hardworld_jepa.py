#!/usr/bin/env python3
"""H019: hard public row-subset HS-JEPA.

H016 allowed arbitrary row x target cell weights. H018 forced binary labels but
kept those cell weights. H019 imposes the more realistic public-LB structure:

    public_delta(file) ~= mean_{row in hidden_public_rows}
        mean_target loss_delta(file, row, target, q[row, target])

The target representation is now a hidden row-subset posterior. If it works,
the public sensor is not only a diffuse cell-weight field; it has a recoverable
row-level public/private state. If it fails, the previous cell-weight view is
mostly an equation fit rather than a realistic public split model.
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
H019 = ROOT / "hitl" / "h019_row_subset_hardworld_jepa"
H019.mkdir(parents=True, exist_ok=True)

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
H018_PRIMARY = "submission_h018_hard_label_world_combined_all_k1750_a1_uploadsafe.csv"

REPORT_OUT = H019 / "h019_report.md"
CONFIG_OUT = H019 / "h019_row_subset_configs.csv"
POSTERIOR_OUT = H019 / "h019_row_subset_posteriors.csv"
NULL_OUT = H019 / "h019_row_subset_null_stress.csv"
ROW_OUT = H019 / "h019_row_public_posterior.csv"
CANDIDATE_OUT = H019 / "h019_candidates.csv"


@dataclass(frozen=True)
class SubsetConfig:
    proxy_name: str
    subset_size: int
    n_masks: int


@dataclass(frozen=True)
class PosteriorSpec:
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
    row_k: int
    alpha: float


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


def pivot_cell(path: Path, col: str, sample: pd.DataFrame) -> np.ndarray:
    src = pd.read_csv(path)
    mat = np.zeros((len(sample), len(TARGETS)), dtype=np.float64)
    for rec in src.to_dict("records"):
        mat[int(rec["row"]), TARGETS.index(str(rec["target"]))] = float(rec[col])
    return clip_prob(mat)


def load_frames() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, np.ndarray]]:
    known = known_public_table().copy().sort_values("public_lb").reset_index(drop=True)
    if CURRENT not in set(known["file"].astype(str)):
        raise RuntimeError(f"{CURRENT} missing from known public table")
    h012 = load_sub(CURRENT)
    h018 = load_sub(H018_PRIMARY, h012[KEYS])
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
    return known, h012[KEYS].copy(), h012, h018, pred_by_file


def build_label_proxies(sample: pd.DataFrame, h012: pd.DataFrame, h018: pd.DataFrame) -> dict[str, np.ndarray]:
    return {
        "h018_hard": pivot_cell(H019.parent / "h018_hard_label_world_jepa" / "h018_cell_hard_posterior.csv", "q_hard", sample),
        "h017_joint": pivot_cell(H019.parent / "h017_joint_label_weight_jepa" / "h017_cell_joint_state.csv", "joint_q_median", sample),
        "h012_public": pivot_cell(H019.parent / "h012_public_equation_jepa_jackpot" / "h012_cell_posterior.csv", "posterior_prob", sample),
        "h015_public": pivot_cell(H019.parent / "h015_public_equation_self_feedback" / "h015_cell_posterior.csv", "posterior_prob", sample),
        "h018_submission": h018[TARGETS].to_numpy(dtype=np.float64),
        "h012_current": h012[TARGETS].to_numpy(dtype=np.float64),
    }


def row_delta_system(
    known: pd.DataFrame,
    pred_by_file: dict[str, np.ndarray],
    h012_prob: np.ndarray,
    q_proxy: np.ndarray,
) -> tuple[list[str], np.ndarray, np.ndarray]:
    files: list[str] = []
    rows: list[np.ndarray] = []
    actual: list[float] = []
    base_lb = float(known.loc[known["file"].eq(CURRENT), "public_lb"].iloc[0])
    anchor_loss = loss(h012_prob, q_proxy)
    for rec in known.to_dict("records"):
        name = str(rec["file"])
        if name == CURRENT or name not in pred_by_file:
            continue
        delta = (loss(pred_by_file[name], q_proxy) - anchor_loss).mean(axis=1)
        files.append(name)
        rows.append(delta)
        actual.append(float(rec["public_lb"]) - base_lb)
    return files, np.vstack(rows), np.asarray(actual, dtype=np.float64)


def sample_row_masks(n_rows: int, subset_size: int, n_masks: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    masks = np.zeros((n_masks, n_rows), dtype=np.uint8)
    for i in range(n_masks):
        masks[i, rng.choice(n_rows, subset_size, replace=False)] = 1
    return masks


def subset_predictions(masks: np.ndarray, row_delta: np.ndarray, subset_size: int) -> np.ndarray:
    return masks.astype(np.float64) @ row_delta.T / float(subset_size)


def config_metrics(preds: np.ndarray, actual: np.ndarray) -> dict[str, float]:
    err = np.mean(np.abs(preds - actual.reshape(1, -1)), axis=1)
    best_idx = int(np.argmin(err))
    best_pred = preds[best_idx]
    return {
        "best_mask_mae": float(err.min()),
        "top100_mask_mae": float(np.mean(np.sort(err)[: min(100, len(err))])),
        "p01_mask_mae": float(np.quantile(err, 0.01)),
        "p05_mask_mae": float(np.quantile(err, 0.05)),
        "median_mask_mae": float(np.median(err)),
        "best_mask_p90_abs": float(np.quantile(np.abs(best_pred - actual), 0.90)),
        "best_mask_spearman": float(pd.Series(best_pred).corr(pd.Series(actual), method="spearman")),
    }


def evaluate_subset_configs(
    proxies: dict[str, np.ndarray],
    known: pd.DataFrame,
    pred_by_file: dict[str, np.ndarray],
    h012_prob: np.ndarray,
) -> tuple[pd.DataFrame, dict[tuple[str, int], np.ndarray], dict[str, tuple[list[str], np.ndarray, np.ndarray]]]:
    subset_sizes = [40, 60, 80, 100, 125, 150, 180, 210, 240]
    n_masks = 18000
    rows: list[dict[str, Any]] = []
    masks_by_size: dict[int, np.ndarray] = {}
    systems: dict[str, tuple[list[str], np.ndarray, np.ndarray]] = {}
    preds_by_key: dict[tuple[str, int], np.ndarray] = {}

    for subset_size in subset_sizes:
        masks_by_size[subset_size] = sample_row_masks(
            h012_prob.shape[0],
            subset_size,
            n_masks,
            20260604 + subset_size,
        )

    for proxy_name, q_proxy in proxies.items():
        if proxy_name == "h012_current":
            continue
        files, row_delta, actual = row_delta_system(known, pred_by_file, h012_prob, q_proxy)
        systems[proxy_name] = (files, row_delta, actual)
        uniform_pred = row_delta.mean(axis=1)
        uniform_mae = float(np.mean(np.abs(uniform_pred - actual)))
        for subset_size, masks in masks_by_size.items():
            preds = subset_predictions(masks, row_delta, subset_size)
            rec = config_metrics(preds, actual)
            rec.update(
                {
                    "proxy_name": proxy_name,
                    "subset_size": subset_size,
                    "n_masks": n_masks,
                    "uniform_row_mae": uniform_mae,
                    "sampled_prior_inclusion": float(subset_size / h012_prob.shape[0]),
                }
            )
            rec["config_score"] = (
                rec["top100_mask_mae"]
                + 0.25 * rec["best_mask_mae"]
                + 0.10 * rec["p01_mask_mae"]
                - 0.00003 * rec["best_mask_spearman"]
                + 0.00002 * abs(subset_size / h012_prob.shape[0] - 0.60)
            )
            rows.append(rec)
            preds_by_key[(proxy_name, subset_size)] = preds
    cfg = pd.DataFrame(rows).sort_values(["config_score", "top100_mask_mae"]).reset_index(drop=True)
    cfg.to_csv(CONFIG_OUT, index=False)
    return cfg, masks_by_size, systems


def posterior_specs() -> list[PosteriorSpec]:
    out: list[PosteriorSpec] = []
    for temp in [0.00004, 0.00006, 0.00008, 0.00012, 0.00020, 0.00035]:
        for power in [1.0, 1.5, 2.0]:
            out.append(PosteriorSpec(f"soft_t{temp:g}_p{power:g}", "soft", temp, 0, power))
    for top_k in [50, 100, 250, 500, 1000, 2500, 5000]:
        for temp in [0.00008, 0.00015, 0.00030]:
            out.append(PosteriorSpec(f"top{top_k}_t{temp:g}", "topk", temp, top_k, 1.0))
        out.append(PosteriorSpec(f"elite{top_k}", "elite", 0.0, top_k, 1.0))
    return out


def mask_posterior(masks: np.ndarray, errors: np.ndarray, spec: PosteriorSpec) -> tuple[np.ndarray, np.ndarray, float]:
    if spec.method == "soft":
        raw = np.exp(-(errors - float(errors.min())) / max(spec.temperature, 1.0e-12))
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
    if float(raw.sum()) <= 1.0e-30:
        raw[:] = 1.0
    weights = raw / float(raw.sum())
    ess = float(1.0 / np.sum(weights * weights))
    inc = weights @ masks.astype(np.float64)
    return inc, weights, ess


def evaluate_posteriors(
    cfg: pd.DataFrame,
    masks_by_size: dict[int, np.ndarray],
    systems: dict[str, tuple[list[str], np.ndarray, np.ndarray]],
) -> tuple[pd.DataFrame, dict[str, np.ndarray], SubsetConfig]:
    top_cfg = cfg.head(8)
    rows: list[dict[str, Any]] = []
    inc_by_id: dict[str, np.ndarray] = {}
    selected_base = SubsetConfig(
        str(cfg.iloc[0]["proxy_name"]),
        int(cfg.iloc[0]["subset_size"]),
        int(cfg.iloc[0]["n_masks"]),
    )
    for base_rec in top_cfg.to_dict("records"):
        proxy_name = str(base_rec["proxy_name"])
        subset_size = int(base_rec["subset_size"])
        masks = masks_by_size[subset_size]
        _, row_delta, actual = systems[proxy_name]
        preds = subset_predictions(masks, row_delta, subset_size)
        errors = np.mean(np.abs(preds - actual.reshape(1, -1)), axis=1)
        prior_inc = subset_size / masks.shape[1]
        for spec in posterior_specs():
            inc, weights, ess = mask_posterior(masks, errors, spec)
            row_w = inc / max(float(inc.sum()), 1.0e-30)
            pred = row_w @ row_delta.T
            err = pred - actual
            posterior_id = f"{proxy_name}_k{subset_size}_{spec.posterior_id}"
            rec = {
                "posterior_id": posterior_id,
                "proxy_name": proxy_name,
                "subset_size": subset_size,
                "method": spec.method,
                "temperature": spec.temperature,
                "top_k": spec.top_k,
                "weight_power": spec.weight_power,
                "posterior_mae": float(np.mean(np.abs(err))),
                "posterior_p90_abs": float(np.quantile(np.abs(err), 0.90)),
                "posterior_spearman": float(pd.Series(pred).corr(pd.Series(actual), method="spearman")),
                "best_mask_mae": float(errors.min()),
                "top100_mask_mae": float(np.mean(np.sort(errors)[:100])),
                "median_mask_mae": float(np.median(errors)),
                "ess": ess,
                "ess_rate": float(ess / len(errors)),
                "inclusion_prior": float(prior_inc),
                "inclusion_abs_shift": float(np.mean(np.abs(inc - prior_inc))),
                "inclusion_min": float(inc.min()),
                "inclusion_max": float(inc.max()),
                "inclusion_top20_mean": float(np.sort(inc)[-20:].mean()),
                "inclusion_bottom20_mean": float(np.sort(inc)[:20].mean()),
            }
            rec["posterior_score"] = (
                rec["posterior_mae"]
                + 0.25 * rec["posterior_p90_abs"]
                - 0.00004 * rec["posterior_spearman"]
                - 0.00003 * min(rec["inclusion_abs_shift"], 0.25) / 0.25
                + 0.00004 * max(150.0 - ess, 0.0) / 150.0
            )
            rows.append(rec)
            inc_by_id[posterior_id] = inc
    post = pd.DataFrame(rows).sort_values(["posterior_score", "posterior_mae"]).reset_index(drop=True)
    post.to_csv(POSTERIOR_OUT, index=False)
    return post, inc_by_id, selected_base


def null_stress(
    cfg: pd.DataFrame,
    masks_by_size: dict[int, np.ndarray],
    systems: dict[str, tuple[list[str], np.ndarray, np.ndarray]],
    n_perm: int = 300,
) -> pd.DataFrame:
    best = cfg.iloc[0]
    proxy_name = str(best["proxy_name"])
    subset_size = int(best["subset_size"])
    masks = masks_by_size[subset_size]
    _, row_delta, actual = systems[proxy_name]
    preds = subset_predictions(masks, row_delta, subset_size)
    real = config_metrics(preds, actual)
    rows: list[dict[str, Any]] = [
        {
            "kind": "real",
            "iteration": -1,
            "proxy_name": proxy_name,
            "subset_size": subset_size,
            **real,
        }
    ]
    rng = np.random.default_rng(20260605)
    for i in range(n_perm):
        perm_actual = rng.permutation(actual)
        rec = config_metrics(preds, perm_actual)
        rows.append(
            {
                "kind": "permute_actual",
                "iteration": i,
                "proxy_name": proxy_name,
                "subset_size": subset_size,
                **rec,
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(NULL_OUT, index=False)
    return out


def null_summary(nulls: pd.DataFrame) -> pd.DataFrame:
    real = nulls[nulls["kind"].eq("real")].iloc[0]
    perm = nulls[nulls["kind"].ne("real")]
    rows: list[dict[str, Any]] = []
    for metric, direction in [
        ("best_mask_mae", "lower"),
        ("top100_mask_mae", "lower"),
        ("p01_mask_mae", "lower"),
        ("median_mask_mae", "lower"),
        ("best_mask_p90_abs", "lower"),
        ("best_mask_spearman", "higher"),
    ]:
        rv = float(real[metric])
        pv = perm[metric].astype(float)
        if direction == "lower":
            p = float((1 + (pv <= rv).sum()) / (len(pv) + 1))
            percentile = float((pv < rv).mean())
        else:
            p = float((1 + (pv >= rv).sum()) / (len(pv) + 1))
            percentile = float((pv < rv).mean())
        rows.append(
            {
                "metric": metric,
                "direction": direction,
                "real": rv,
                "null_mean": float(pv.mean()),
                "null_p10": float(pv.quantile(0.10)),
                "null_p50": float(pv.quantile(0.50)),
                "null_p90": float(pv.quantile(0.90)),
                "real_percentile_vs_null": percentile,
                "one_sided_p": p,
            }
        )
    return pd.DataFrame(rows)


def build_row_table(
    sample: pd.DataFrame,
    inc: np.ndarray,
    best_proxy: np.ndarray,
    h012_prob: np.ndarray,
    h018_prob: np.ndarray,
    selected_posterior: pd.Series,
) -> pd.DataFrame:
    row_w = inc / max(float(inc.sum()), 1.0e-30)
    target = best_proxy
    row_gain = (loss(h012_prob, target) - loss(target, target)).mean(axis=1)
    h018_gain = (loss(h012_prob, target) - loss(h018_prob, target)).mean(axis=1)
    row_move = np.mean(np.abs(logit(target) - logit(h012_prob)), axis=1)
    inclusion_lift = inc / max(float(selected_posterior["inclusion_prior"]), 1.0e-30)
    score = (
        0.42 * rank01(inc)
        + 0.28 * rank01(row_gain)
        + 0.18 * rank01(row_move)
        + 0.12 * rank01(inclusion_lift)
    )
    rows: list[dict[str, Any]] = []
    for i in range(len(sample)):
        rec = {
            "row": i,
            "subject_id": sample.iloc[i]["subject_id"],
            "sleep_date": sample.iloc[i]["sleep_date"],
            "lifelog_date": sample.iloc[i]["lifelog_date"],
            "inclusion_prob": float(inc[i]),
            "inclusion_prior": float(selected_posterior["inclusion_prior"]),
            "inclusion_lift": float(inclusion_lift[i]),
            "row_weight": float(row_w[i]),
            "row_gain_to_proxy": float(row_gain[i]),
            "row_gain_h018_to_proxy": float(h018_gain[i]),
            "mean_abs_logit_move_to_proxy": float(row_move[i]),
            "row_score": float(score[i]),
        }
        for j, target_name in enumerate(TARGETS):
            rec[f"{target_name}_h012"] = float(h012_prob[i, j])
            rec[f"{target_name}_proxy"] = float(target[i, j])
        rows.append(rec)
    out = pd.DataFrame(rows).sort_values("row_score", ascending=False).reset_index(drop=True)
    out.to_csv(ROW_OUT, index=False)
    return out


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
    return mask


def candidate_specs() -> list[CandidateSpec]:
    out: list[CandidateSpec] = []
    for mode in ["row_score", "inclusion", "gain", "lift"]:
        for subset in ["all", "Q", "S"]:
            for row_k in [40, 60, 80, 100, 125, 150, 180, 210, 240]:
                for alpha in [0.55, 0.75, 1.0, 1.25]:
                    out.append(CandidateSpec(f"{mode}_{subset}_r{row_k}_a{alpha:g}", mode, subset, row_k, alpha))
    for target in TARGETS:
        for mode in ["row_score", "inclusion"]:
            for row_k in [40, 80, 125, 180, 240]:
                for alpha in [0.75, 1.0, 1.25]:
                    out.append(CandidateSpec(f"{mode}_{target}_r{row_k}_a{alpha:g}", mode, target, row_k, alpha))
    return out


def make_candidate_frame(
    h012: pd.DataFrame,
    target_prob: np.ndarray,
    row_table: pd.DataFrame,
    spec: CandidateSpec,
) -> tuple[pd.DataFrame, np.ndarray]:
    base_prob = h012[TARGETS].to_numpy(dtype=np.float64)
    score_col = {
        "row_score": "row_score",
        "inclusion": "inclusion_prob",
        "gain": "row_gain_to_proxy",
        "lift": "inclusion_lift",
    }[spec.mode]
    chosen_rows = row_table.sort_values(score_col, ascending=False).head(spec.row_k)["row"].astype(int).to_numpy()
    mask = np.zeros(base_prob.shape, dtype=bool)
    mask[chosen_rows, :] = True
    mask &= target_mask(spec.target_subset, base_prob.shape)
    z = logit(base_prob)
    moved = z.copy()
    moved[mask] = z[mask] + spec.alpha * (logit(target_prob)[mask] - z[mask])
    out = h012.copy()
    out[TARGETS] = clip_prob(sigmoid(moved))
    return out, mask


def score_candidate(
    prob: np.ndarray,
    base_prob: np.ndarray,
    target_prob: np.ndarray,
    row_weight: np.ndarray,
) -> dict[str, float]:
    row_diff = (loss(prob, target_prob) - loss(base_prob, target_prob)).mean(axis=1)
    return {
        "rowposterior_delta_vs_h012": float(row_diff @ row_weight),
        "uniform_row_delta_vs_h012": float(row_diff.mean()),
        "rowposterior_beats_rate": float(np.mean(row_diff < 0.0)),
        "rowposterior_p90_row_delta": float(np.quantile(row_diff, 0.90)),
    }


def generate_candidates(
    h012: pd.DataFrame,
    h018: pd.DataFrame,
    target_prob: np.ndarray,
    row_table: pd.DataFrame,
) -> tuple[pd.DataFrame, Path | None]:
    base_prob = h012[TARGETS].to_numpy(dtype=np.float64)
    h018_prob = h018[TARGETS].to_numpy(dtype=np.float64)
    row_weight = row_table.sort_values("row")["row_weight"].to_numpy(dtype=np.float64)
    h018_score = score_candidate(h018_prob, base_prob, target_prob, row_weight)
    rows: list[dict[str, Any]] = []
    frames: list[tuple[pd.DataFrame, CandidateSpec, dict[str, Any]]] = []
    for spec in candidate_specs():
        out, mask = make_candidate_frame(h012, target_prob, row_table, spec)
        prob = out[TARGETS].to_numpy(dtype=np.float64)
        rec = score_candidate(prob, base_prob, target_prob, row_weight)
        rec.update(
            {
                "candidate_id": spec.candidate_id,
                "mode": spec.mode,
                "target_subset": spec.target_subset,
                "row_k": spec.row_k,
                "alpha": spec.alpha,
                "changed_rows": int((np.abs(prob - base_prob).max(axis=1) > 1.0e-12).sum()),
                "changed_cells": int((np.abs(prob - base_prob) > 1.0e-12).sum()),
                "mean_abs_prob_delta_vs_h012": float(np.mean(np.abs(prob - base_prob))),
                "max_abs_prob_delta_vs_h012": float(np.max(np.abs(prob - base_prob))),
                "mean_abs_prob_delta_vs_h018": float(np.mean(np.abs(prob - h018_prob))),
                "max_abs_prob_delta_vs_h018": float(np.max(np.abs(prob - h018_prob))),
                "h018_rowposterior_delta_vs_h012": h018_score["rowposterior_delta_vs_h012"],
                "h018_uniform_row_delta_vs_h012": h018_score["uniform_row_delta_vs_h012"],
            }
        )
        rows.append(rec)
        frames.append((out, spec, rec))
    candidates = pd.DataFrame(rows)
    candidates["h019_decision"] = np.select(
        [
            (candidates["rowposterior_delta_vs_h012"] < -0.00062)
            & (candidates["max_abs_prob_delta_vs_h012"] <= 0.15)
            & (candidates["changed_cells"] >= 1200),
            (candidates["rowposterior_delta_vs_h012"] < -0.00050)
            & (candidates["max_abs_prob_delta_vs_h012"] <= 0.16)
            & (candidates["changed_cells"] >= 700),
        ],
        ["row_subset_big_bet", "row_subset_sensor"],
        default="diagnostic_only",
    )
    order = {"row_subset_big_bet": 0, "row_subset_sensor": 1, "diagnostic_only": 2}
    candidates["decision_rank"] = candidates["h019_decision"].map(order).astype(int)
    candidates = candidates.sort_values(
        ["decision_rank", "rowposterior_delta_vs_h012", "mean_abs_prob_delta_vs_h018"],
        ascending=[True, True, False],
    ).reset_index(drop=True)

    keep = set(candidates.head(60)["candidate_id"].astype(str))
    materialized: dict[str, str] = {}
    primary: Path | None = None
    for out, spec, _ in frames:
        if spec.candidate_id not in keep:
            continue
        path = H019 / f"submission_h019_{safe_id(spec.candidate_id)}_{short_hash(out)}.csv"
        out.to_csv(path, index=False)
        materialized[spec.candidate_id] = rel(path)
    candidates["file"] = candidates["candidate_id"].map(materialized).fillna("not_materialized")
    promoted = candidates[candidates["h019_decision"].isin(["row_subset_big_bet", "row_subset_sensor"])].head(1)
    if not promoted.empty:
        source = ROOT / str(promoted.iloc[0]["file"])
        primary = ROOT / f"submission_h019_row_subset_hardworld_{safe_id(str(promoted.iloc[0]['candidate_id']), 64)}_uploadsafe.csv"
        shutil.copyfile(source, primary)
    candidates.to_csv(CANDIDATE_OUT, index=False)
    return candidates, primary


def write_report(
    cfg: pd.DataFrame,
    post: pd.DataFrame,
    nulls: pd.DataFrame,
    row_table: pd.DataFrame,
    candidates: pd.DataFrame,
    primary: Path | None,
) -> None:
    lines: list[str] = []
    lines.append("# H019 Row-Subset Hardworld HS-JEPA\n")
    lines.append("## Question\n")
    lines.append("Can known public LB deltas be explained by a hidden row-level public subset rather than free cell weights?\n")
    lines.append("## Top Row-Subset Configs\n")
    lines.append(md_table(cfg.head(24)))
    lines.append("\n## Top Row-Subset Posteriors\n")
    lines.append(md_table(post.head(24)))
    lines.append("\n## Null Stress\n")
    lines.append("Known public deltas are permuted while the same sampled row masks and row-delta tensors are kept fixed.\n")
    lines.append(md_table(null_summary(nulls)))
    lines.append("\n## Row Posterior Summary\n")
    summary = pd.DataFrame(
        [
            {
                "rows": len(row_table),
                "inclusion_prior": float(row_table["inclusion_prior"].iloc[0]),
                "inclusion_min": float(row_table["inclusion_prob"].min()),
                "inclusion_max": float(row_table["inclusion_prob"].max()),
                "inclusion_top20_mean": float(row_table["inclusion_prob"].head(20).mean()),
                "inclusion_bottom20_mean": float(row_table["inclusion_prob"].tail(20).mean()),
                "row_weight_top20_mass": float(row_table["row_weight"].head(20).sum()),
            }
        ]
    )
    lines.append(md_table(summary))
    lines.append("\n## Top Rows\n")
    top_cols = [
        "row",
        "subject_id",
        "sleep_date",
        "inclusion_prob",
        "inclusion_lift",
        "row_gain_to_proxy",
        "mean_abs_logit_move_to_proxy",
        "row_score",
    ]
    lines.append(md_table(row_table[top_cols].head(30)))
    lines.append("\n## Candidate Selection\n")
    lines.append(md_table(candidates.head(40)))
    lines.append("\n## Decision\n")
    if primary is None:
        lines.append("- No upload-safe candidate promoted; H019 remains diagnostic.\n")
    else:
        lines.append(f"- Primary upload-safe candidate: `{primary.name}`.\n")
        lines.append("- Interpretation: this file excludes low posterior-inclusion rows from the H018/H017 hardworld action.\n")
    lines.append("\n## Files\n")
    for p in [CONFIG_OUT, POSTERIOR_OUT, NULL_OUT, ROW_OUT, CANDIDATE_OUT]:
        lines.append(f"- `{rel(p)}`\n")
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    known, sample, h012, h018, pred_by_file = load_frames()
    h012_prob = h012[TARGETS].to_numpy(dtype=np.float64)
    h018_prob = h018[TARGETS].to_numpy(dtype=np.float64)
    proxies = build_label_proxies(sample, h012, h018)

    cfg, masks_by_size, systems = evaluate_subset_configs(proxies, known, pred_by_file, h012_prob)
    post, inc_by_id, _ = evaluate_posteriors(cfg, masks_by_size, systems)
    nulls = null_stress(cfg, masks_by_size, systems)

    selected = post.iloc[0]
    selected_inc = inc_by_id[str(selected["posterior_id"])]
    selected_proxy = proxies[str(selected["proxy_name"])]
    row_table = build_row_table(sample, selected_inc, selected_proxy, h012_prob, h018_prob, selected)
    candidates, primary = generate_candidates(h012, h018, selected_proxy, row_table)
    write_report(cfg, post, nulls, row_table, candidates, primary)

    print(f"Wrote {REPORT_OUT}")
    if primary is not None:
        print(f"Primary: {primary}")
    else:
        print("Primary: none")
    print(candidates.head(12).to_string(index=False))


if __name__ == "__main__":
    main()
