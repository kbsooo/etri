#!/usr/bin/env python3
"""H023: human-state proposal/Pareto vector-world HS-JEPA.

H022 rejected q_hs as the final posterior prior: beta-positive human-state
posteriors did not beat the beta-zero public-equation posterior.

H023 tests a narrower and more honest architecture role:

    context = public-equation vector worlds sampled from H018/H020/H022 views
    target  = public-compatible hidden row-level Q/S vector worlds
    q_hs    = proposal/Pareto constraint after public compatibility, not a
              generative probability prior
    action  = materialize only if a q_hs-Pareto posterior stays public-fit and
              beats row-permuted q_hs controls
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
HITL = ROOT / "hitl"
ANALYSIS = ROOT / "analysis_outputs"
OUT = HITL / "h023_hs_pareto_proposal_vector_jepa"
OUT.mkdir(parents=True, exist_ok=True)

for path in [HITL, ANALYSIS]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import h022_hs_conditioned_vector_world_jepa as h022  # noqa: E402


KEYS = h022.KEYS
TARGETS = h022.TARGETS
EPS = 1.0e-6

POOL_OUT = OUT / "h023_pool_sources.csv"
POSTERIOR_OUT = OUT / "h023_pareto_posteriors.csv"
ALIGN_OUT = OUT / "h023_public_hs_alignment.csv"
ROWPERM_OUT = OUT / "h023_rowperm_null.csv"
ROW_OUT = OUT / "h023_row_state.csv"
CELL_OUT = OUT / "h023_cell_state.csv"
CANDIDATE_OUT = OUT / "h023_candidates.csv"
REPORT_OUT = OUT / "h023_report.md"


@dataclass(frozen=True)
class PoolSource:
    source_id: str
    prior_kind: str
    beta: float
    n_samples: int
    seed: int


@dataclass(frozen=True)
class ParetoSpec:
    posterior_id: str
    top_k: int
    temperature: float
    hs_lambda: float
    mode: str


@dataclass(frozen=True)
class CandidateSpec:
    candidate_id: str
    mode: str
    k: int
    alpha: float
    target_subset: str = "all"


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(x, dtype=np.float64)))


def safe_id(text: str, limit: int = 96) -> str:
    clean = re.sub(r"[^A-Za-z0-9_.-]+", "_", text).strip("_")
    return clean[:limit].strip("_")


def short_hash(frame: pd.DataFrame) -> str:
    return hashlib.sha1(np.round(frame[TARGETS].to_numpy(dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def rel(path: Path | None) -> str:
    if path is None:
        return "none"
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def rank01(x: np.ndarray) -> np.ndarray:
    return pd.Series(np.asarray(x, dtype=np.float64)).rank(method="average", pct=True).to_numpy(dtype=np.float64)


def md_table(frame: pd.DataFrame, n: int = 24) -> str:
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


def pool_sources() -> list[PoolSource]:
    return [
        PoolSource("none_b0", "none", 0.0, 70000, 20260630),
        PoolSource("hs_b0.1", "hs", 0.10, 70000, 20260631),
        PoolSource("hs_b0.18", "hs", 0.18, 55000, 20260632),
        PoolSource("hsconf_b0.2", "hs_conf", 0.20, 55000, 20260633),
    ]


def pareto_specs() -> list[ParetoSpec]:
    specs: list[ParetoSpec] = []
    for top_k in [250, 500, 1000, 2500, 5000, 10000]:
        for temp in [0.00012, 0.00025, 0.00050]:
            specs.append(ParetoSpec(f"public_top{top_k}_lam0_t{temp:g}", top_k, temp, 0.0, "public_only"))
            for lam in [0.20, 0.45, 0.75, 1.10, 1.60, 2.40]:
                specs.append(ParetoSpec(f"pareto_top{top_k}_lam{lam:g}_t{temp:g}", top_k, temp, lam, "pareto"))
        for lam in [0.75, 1.10, 1.60, 2.40]:
            specs.append(ParetoSpec(f"rank_top{top_k}_lam{lam:g}", top_k, 0.0, lam, "rank"))
    return specs


def candidate_specs() -> list[CandidateSpec]:
    specs: list[CandidateSpec] = []
    for mode in ["gain", "combined", "shift"]:
        for k in [700, 1000, 1200, 1500, 1750]:
            for alpha in [0.60, 0.75, 1.00, 1.20]:
                specs.append(CandidateSpec(f"{mode}_all_k{k}_a{alpha:g}", mode, k, alpha, "all"))
    for target_subset in ["Q", "S", "Q2S1", "Q2S3", "Q1Q3S1S3"]:
        for mode in ["gain", "combined"]:
            for k in [250, 450, 700, 950]:
                for alpha in [0.75, 1.00, 1.25]:
                    specs.append(CandidateSpec(f"{mode}_{target_subset}_k{k}_a{alpha:g}", mode, k, alpha, target_subset))
    return specs


def target_mask(target_subset: str, shape: tuple[int, int]) -> np.ndarray:
    mask = np.zeros(shape, dtype=bool)
    if target_subset == "all":
        mask[:] = True
    elif target_subset == "Q":
        mask[:, :3] = True
    elif target_subset == "S":
        mask[:, 3:] = True
    else:
        targets = {
            "Q2S1": ["Q2", "S1"],
            "Q2S3": ["Q2", "S3"],
            "Q1Q3S1S3": ["Q1", "Q3", "S1", "S3"],
        }[target_subset]
        for target in targets:
            mask[:, TARGETS.index(target)] = True
    return mask


def vector_energy(choices: np.ndarray, dist: np.ndarray, row_weight: np.ndarray) -> np.ndarray:
    neglog = -np.log(dist + 1.0e-30)
    out = np.zeros(choices.shape[0], dtype=np.float64)
    for row_i in range(choices.shape[1]):
        out += row_weight[row_i] * neglog[row_i, choices[:, row_i]]
    return out


def sample_pool(
    q_base: np.ndarray,
    hs_dist: np.ndarray,
    hs_conf: np.ndarray,
    contrib: np.ndarray,
    actual: np.ndarray,
    row_weight: np.ndarray,
) -> tuple[pd.DataFrame, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    choices_parts: list[np.ndarray] = []
    preds_parts: list[np.ndarray] = []
    errors_parts: list[np.ndarray] = []
    source_ids: list[str] = []
    rows: list[dict[str, Any]] = []

    for src in pool_sources():
        cfg = h022.VectorConfig(src.source_id, src.prior_kind, src.beta, src.n_samples)
        dist = h022.build_row_distribution(q_base, hs_dist, hs_conf, cfg)
        choices, preds, errors = h022.sample_worlds(dist, contrib, actual, src.n_samples, src.seed)
        hs_e = vector_energy(choices, hs_dist, row_weight)
        best = int(np.argmin(errors))
        rows.append(
            {
                "source_id": src.source_id,
                "prior_kind": src.prior_kind,
                "beta": src.beta,
                "n_samples": src.n_samples,
                "best_world_mae": float(errors.min()),
                "top100_world_mae": float(np.mean(np.sort(errors)[:100])),
                "p01_world_mae": float(np.quantile(errors, 0.01)),
                "median_world_mae": float(np.median(errors)),
                "best_world_hs_energy": float(hs_e[best]),
                "top100_hs_energy": float(np.mean(hs_e[np.argsort(errors)[:100]])),
                "best_world_spearman": float(pd.Series(preds[best]).corr(pd.Series(actual), method="spearman")),
            }
        )
        choices_parts.append(choices)
        preds_parts.append(preds)
        errors_parts.append(errors)
        source_ids.extend([src.source_id] * src.n_samples)

    pool = pd.DataFrame(rows).sort_values(["top100_world_mae", "best_world_mae"]).reset_index(drop=True)
    pool.to_csv(POOL_OUT, index=False)
    choices_all = np.vstack(choices_parts)
    preds_all = np.vstack(preds_parts)
    errors_all = np.concatenate(errors_parts)
    source_arr = np.asarray(source_ids, dtype=object)
    hs_energy = vector_energy(choices_all, hs_dist, row_weight)
    return pool, choices_all, preds_all, errors_all, source_arr, hs_energy


def public_hs_alignment(
    choices: np.ndarray,
    errors: np.ndarray,
    hs_energy: np.ndarray,
    hs_dist: np.ndarray,
    row_weight: np.ndarray,
    n_perm: int = 80,
) -> pd.DataFrame:
    rng = np.random.default_rng(20260634)
    rows: list[dict[str, Any]] = []
    order = np.argsort(errors)
    for top_k in [100, 250, 500, 1000, 2500, 5000, 10000]:
        idx = order[:top_k]
        real = float(np.mean(hs_energy[idx]))
        null_vals: list[float] = []
        for i in range(n_perm):
            perm = rng.permutation(len(hs_dist))
            null_vals.append(float(np.mean(vector_energy(choices[idx], hs_dist[perm], row_weight))))
        arr = np.asarray(null_vals, dtype=np.float64)
        rows.append(
            {
                "top_k_public_worlds": top_k,
                "real_hs_energy": real,
                "null_mean": float(arr.mean()),
                "null_p10": float(np.quantile(arr, 0.10)),
                "null_p50": float(np.quantile(arr, 0.50)),
                "null_p90": float(np.quantile(arr, 0.90)),
                "real_minus_null_p50": float(real - np.quantile(arr, 0.50)),
                "one_sided_p": float((1 + (arr <= real).sum()) / (len(arr) + 1)),
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(ALIGN_OUT, index=False)
    return out


def posterior_distribution(choices: np.ndarray, weights: np.ndarray) -> np.ndarray:
    out = np.zeros((choices.shape[1], 128), dtype=np.float64)
    for row_i in range(choices.shape[1]):
        out[row_i] = np.bincount(choices[:, row_i], weights=weights, minlength=128)
    out /= np.maximum(out.sum(axis=1, keepdims=True), 1.0e-30)
    return out


def weights_for_spec(errors: np.ndarray, hs_energy: np.ndarray, spec: ParetoSpec) -> tuple[np.ndarray, float, np.ndarray]:
    order = np.argsort(errors)[: min(spec.top_k, len(errors))]
    local_e = errors[order]
    local_h = hs_energy[order]
    w = np.zeros(len(errors), dtype=np.float64)
    if spec.mode == "public_only":
        score = -(local_e - float(local_e.min())) / max(spec.temperature, 1.0e-12)
    elif spec.mode == "pareto":
        z_h = (local_h - float(local_h.mean())) / max(float(local_h.std()), 1.0e-12)
        score = -(local_e - float(local_e.min())) / max(spec.temperature, 1.0e-12) - spec.hs_lambda * z_h
    elif spec.mode == "rank":
        e_rank = rank01(local_e)
        h_rank = rank01(local_h)
        score = -(e_rank + spec.hs_lambda * h_rank)
    else:
        raise ValueError(spec.mode)
    score -= float(score.max())
    raw = np.exp(score)
    raw /= max(float(raw.sum()), 1.0e-30)
    w[order] = raw
    ess = float(1.0 / np.sum(w * w))
    return w, ess, order


def evaluate_pareto_posteriors(
    choices: np.ndarray,
    preds: np.ndarray,
    errors: np.ndarray,
    source_arr: np.ndarray,
    hs_energy: np.ndarray,
    contrib: np.ndarray,
    actual: np.ndarray,
    q_base: np.ndarray,
    hs_dist: np.ndarray,
) -> tuple[pd.DataFrame, dict[str, np.ndarray], dict[str, np.ndarray], dict[str, np.ndarray]]:
    vecs = h022.vector_table()
    rows: list[dict[str, Any]] = []
    dist_by_id: dict[str, np.ndarray] = {}
    q_by_id: dict[str, np.ndarray] = {}
    weights_by_id: dict[str, np.ndarray] = {}
    best_public_mae = None

    for spec in pareto_specs():
        weights, ess, order = weights_for_spec(errors, hs_energy, spec)
        post_dist = posterior_distribution(choices, weights)
        q_vec = clip_prob(post_dist @ vecs)
        pred = np.einsum("rv,frv->f", post_dist, contrib)
        err = pred - actual
        active = np.flatnonzero(weights > 0)
        source_counts = pd.Series(source_arr[active]).value_counts(normalize=True)
        hs_share = float(source_counts[[idx for idx in source_counts.index if str(idx).startswith("hs")]].sum()) if len(source_counts) else 0.0
        row_kl_hs = float(np.mean(np.sum(post_dist * (np.log(post_dist + 1.0e-30) - np.log(hs_dist + 1.0e-30)), axis=1)))
        rec = {
            "posterior_id": spec.posterior_id,
            "mode": spec.mode,
            "top_k": spec.top_k,
            "temperature": spec.temperature,
            "hs_lambda": spec.hs_lambda,
            "posterior_mae": float(np.mean(np.abs(err))),
            "posterior_p90_abs": float(np.quantile(np.abs(err), 0.90)),
            "posterior_spearman": float(pd.Series(pred).corr(pd.Series(actual), method="spearman")),
            "ess": ess,
            "ess_rate_in_topk": float(ess / max(len(order), 1)),
            "weighted_world_error": float(np.sum(weights * errors)),
            "weighted_hs_energy": float(np.sum(weights * hs_energy)),
            "topk_mean_hs_energy": float(np.mean(hs_energy[order])),
            "row_vector_kl_from_hs": row_kl_hs,
            "mean_max_vector_posterior": float(np.mean(post_dist.max(axis=1))),
            "q_abs_shift_vs_base": float(np.mean(np.abs(q_vec - q_base))),
            "q_max_abs_shift_vs_base": float(np.max(np.abs(q_vec - q_base))),
            "q_spearman_vs_base": float(pd.Series(q_vec.reshape(-1)).corr(pd.Series(q_base.reshape(-1)), method="spearman")),
            "hs_source_weight_share": hs_share,
        }
        if spec.hs_lambda == 0.0 and spec.mode == "public_only":
            if best_public_mae is None or rec["posterior_mae"] < best_public_mae:
                best_public_mae = rec["posterior_mae"]
        rows.append(rec)
        dist_by_id[spec.posterior_id] = post_dist
        q_by_id[spec.posterior_id] = q_vec
        weights_by_id[spec.posterior_id] = weights

    out = pd.DataFrame(rows)
    public_best_mae = float(out.loc[out["hs_lambda"].eq(0.0), "posterior_mae"].min())
    public_best_p90 = float(out.loc[out["hs_lambda"].eq(0.0), "posterior_p90_abs"].min())
    hs_ref = float(out.loc[out["hs_lambda"].eq(0.0), "weighted_hs_energy"].min())
    out["mae_over_public_best"] = out["posterior_mae"] - public_best_mae
    out["p90_over_public_best"] = out["posterior_p90_abs"] - public_best_p90
    out["hs_energy_gain_vs_public"] = hs_ref - out["weighted_hs_energy"]
    out["pareto_score"] = (
        out["posterior_mae"]
        + 0.25 * out["posterior_p90_abs"]
        - 0.00004 * out["posterior_spearman"]
        + 0.30 * np.maximum(out["mae_over_public_best"], 0.0)
        - 0.000015 * np.tanh(np.maximum(out["hs_energy_gain_vs_public"], 0.0) / 0.02)
    )
    out["prelim_decision"] = np.where(
        (out["hs_lambda"] > 0)
        & (out["mae_over_public_best"] <= 0.000006)
        & (out["p90_over_public_best"] <= 0.000020)
        & (out["hs_energy_gain_vs_public"] > 0),
        "pareto_candidate",
        np.where(out["hs_lambda"].eq(0.0), "public_baseline", "diagnostic_only"),
    )
    out = out.sort_values(["prelim_decision", "pareto_score", "posterior_mae"], ascending=[True, True, True]).reset_index(drop=True)
    out.to_csv(POSTERIOR_OUT, index=False)
    return out, dist_by_id, q_by_id, weights_by_id


def rowperm_null(
    posteriors: pd.DataFrame,
    choices: np.ndarray,
    errors: np.ndarray,
    hs_dist: np.ndarray,
    row_weight: np.ndarray,
    contrib: np.ndarray,
    actual: np.ndarray,
    n_perm: int = 60,
) -> pd.DataFrame:
    rng = np.random.default_rng(20260635)
    vecs = h022.vector_table()
    selected = posteriors.loc[posteriors["prelim_decision"].eq("pareto_candidate")].head(8)
    if selected.empty:
        selected = posteriors.loc[posteriors["hs_lambda"].gt(0)].head(8)
    rows: list[dict[str, Any]] = []

    for rec in selected.to_dict("records"):
        spec = next(s for s in pareto_specs() if s.posterior_id == str(rec["posterior_id"]))
        real_hs = vector_energy(choices, hs_dist, row_weight)
        weights, ess, _ = weights_for_spec(errors, real_hs, spec)
        post_dist = posterior_distribution(choices, weights)
        pred = np.einsum("rv,frv->f", post_dist, contrib)
        err = pred - actual
        real = {
            "posterior_id": spec.posterior_id,
            "kind": "real",
            "iteration": -1,
            "posterior_mae": float(np.mean(np.abs(err))),
            "posterior_p90_abs": float(np.quantile(np.abs(err), 0.90)),
            "posterior_spearman": float(pd.Series(pred).corr(pd.Series(actual), method="spearman")),
            "weighted_hs_energy": float(np.sum(weights * real_hs)),
            "row_vector_kl_from_hs": float(np.mean(np.sum(post_dist * (np.log(post_dist + 1.0e-30) - np.log(hs_dist + 1.0e-30)), axis=1))),
            "ess": ess,
        }
        rows.append(real)
        for i in range(n_perm):
            perm = rng.permutation(len(hs_dist))
            perm_hs = vector_energy(choices, hs_dist[perm], row_weight)
            w, ess_p, _ = weights_for_spec(errors, perm_hs, spec)
            pdist = posterior_distribution(choices, w)
            pred_p = np.einsum("rv,frv->f", pdist, contrib)
            err_p = pred_p - actual
            rows.append(
                {
                    "posterior_id": spec.posterior_id,
                    "kind": "permute_hs_rows",
                    "iteration": i,
                    "posterior_mae": float(np.mean(np.abs(err_p))),
                    "posterior_p90_abs": float(np.quantile(np.abs(err_p), 0.90)),
                    "posterior_spearman": float(pd.Series(pred_p).corr(pd.Series(actual), method="spearman")),
                    "weighted_hs_energy": float(np.sum(w * perm_hs)),
                    "row_vector_kl_from_hs": float(np.mean(np.sum(pdist * (np.log(pdist + 1.0e-30) - np.log(hs_dist + 1.0e-30)), axis=1))),
                    "ess": ess_p,
                }
            )
    out = pd.DataFrame(rows)
    out.to_csv(ROWPERM_OUT, index=False)
    return out


def add_rowperm_summary(posteriors: pd.DataFrame, nulls: pd.DataFrame) -> pd.DataFrame:
    if nulls.empty:
        posteriors["rowperm_public_p"] = 1.0
        posteriors["rowperm_hs_kl_p"] = 1.0
        return posteriors
    rows = []
    for pid, part in nulls.groupby("posterior_id"):
        real = part.loc[part["kind"].eq("real")].iloc[0]
        perm = part.loc[part["kind"].ne("real")]
        rows.append(
            {
                "posterior_id": pid,
                "rowperm_public_p": float((1 + (perm["posterior_mae"] <= float(real["posterior_mae"])).sum()) / (len(perm) + 1)),
                "rowperm_hs_kl_p": float((1 + (perm["row_vector_kl_from_hs"] <= float(real["row_vector_kl_from_hs"])).sum()) / (len(perm) + 1)),
                "rowperm_public_median": float(perm["posterior_mae"].median()),
                "rowperm_hs_kl_median": float(perm["row_vector_kl_from_hs"].median()),
            }
        )
    merged = posteriors.merge(pd.DataFrame(rows), on="posterior_id", how="left")
    for col in ["rowperm_public_p", "rowperm_hs_kl_p"]:
        merged[col] = merged[col].fillna(1.0)
    merged["final_decision"] = np.where(
        (merged["prelim_decision"].eq("pareto_candidate"))
        & (merged["rowperm_public_p"] <= 0.40)
        & (merged["rowperm_hs_kl_p"] <= 0.20),
        "pareto_action_candidate",
        merged["prelim_decision"],
    )
    order = {"pareto_action_candidate": 0, "pareto_candidate": 1, "public_baseline": 2, "diagnostic_only": 3}
    merged["decision_rank"] = merged["final_decision"].map(order).fillna(9).astype(int)
    merged = merged.sort_values(["decision_rank", "pareto_score", "posterior_mae"]).reset_index(drop=True)
    merged.to_csv(POSTERIOR_OUT, index=False)
    return merged


def build_state_tables(
    sample: pd.DataFrame,
    post_dist: np.ndarray,
    q_vec: np.ndarray,
    q_base: np.ndarray,
    hs_dist: np.ndarray,
    h012_prob: np.ndarray,
    row_weight: np.ndarray,
    selected: pd.Series,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    row_state, cells = h022.build_state_tables(
        sample,
        post_dist,
        q_vec,
        q_base,
        hs_dist,
        h012_prob,
        row_weight,
        selected,
        write_outputs=False,
    )
    row_state.to_csv(ROW_OUT, index=False)
    cells.to_csv(CELL_OUT, index=False)
    return row_state, cells


def make_candidate(h012: pd.DataFrame, q_vec: np.ndarray, cells: pd.DataFrame, spec: CandidateSpec) -> tuple[pd.DataFrame, np.ndarray]:
    base = h012[TARGETS].to_numpy(dtype=np.float64)
    out = base.copy()
    mask_allowed = target_mask(spec.target_subset, base.shape)
    score_map = cells.sort_values(["row", "target"]).reset_index(drop=True)["combined_score"].to_numpy(dtype=np.float64).reshape(base.shape)
    gain_map = cells.sort_values(["row", "target"]).reset_index(drop=True)["cell_gain"].to_numpy(dtype=np.float64).reshape(base.shape)
    shift = q_vec - base
    agree = cells.sort_values(["row", "target"]).reset_index(drop=True)["hs_h023_agree"].to_numpy(dtype=bool).reshape(base.shape)
    if spec.mode == "gain":
        scores = gain_map
        valid = mask_allowed & (gain_map > 0)
    elif spec.mode == "combined":
        scores = score_map
        valid = mask_allowed & (gain_map > 0) & agree
    elif spec.mode == "shift":
        scores = np.abs(shift) * score_map
        valid = mask_allowed & (gain_map > 0)
    else:
        raise ValueError(spec.mode)
    flat = np.flatnonzero(valid.reshape(-1))
    selected = np.zeros(base.shape, dtype=bool)
    if len(flat):
        chosen = flat[np.argsort(scores.reshape(-1)[flat])[-min(spec.k, len(flat)) :]]
        selected.reshape(-1)[chosen] = True
        out[selected] = clip_prob(sigmoid(h022.logit(base[selected]) + spec.alpha * (h022.logit(q_vec[selected]) - h022.logit(base[selected]))))
    frame = h012[KEYS].copy()
    for idx, target in enumerate(TARGETS):
        frame[target] = out[:, idx]
    return frame, selected


def score_candidate(prob: np.ndarray, base: np.ndarray, q_vec: np.ndarray, row_weight: np.ndarray) -> dict[str, float]:
    delta = (h022.loss(prob, q_vec) - h022.loss(base, q_vec)).mean(axis=1)
    weighted = float(np.sum(row_weight * delta))
    return {
        "rowweighted_delta_vs_h012": weighted,
        "uniform_delta_vs_h012": float(delta.mean()),
        "row_beats_rate": float(np.mean(delta < 0)),
        "row_p90_delta": float(np.quantile(delta, 0.90)),
    }


def validate_submission(path: Path, sample: pd.DataFrame) -> dict[str, Any]:
    df = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"])
    if len(df) != len(sample) or not df[KEYS].equals(sample[KEYS]):
        raise ValueError(f"submission alignment failed: {path}")
    vals = df[TARGETS].to_numpy(dtype=np.float64)
    if not np.isfinite(vals).all():
        raise ValueError(f"non-finite probabilities: {path}")
    if vals.min() < 0 or vals.max() > 1:
        raise ValueError(f"probability range failed: {path}")
    return {"min_prob": float(vals.min()), "max_prob": float(vals.max()), "rows": int(len(df))}


def generate_candidates(
    sample: pd.DataFrame,
    h012: pd.DataFrame,
    h020: pd.DataFrame,
    h021_sub: pd.DataFrame,
    q_vec: np.ndarray,
    cells: pd.DataFrame,
    row_weight: np.ndarray,
    selected: pd.Series,
) -> tuple[pd.DataFrame, Path | None]:
    base = h012[TARGETS].to_numpy(dtype=np.float64)
    refs = {
        "h020": h020[TARGETS].to_numpy(dtype=np.float64),
        "h021": h021_sub[TARGETS].to_numpy(dtype=np.float64),
    }
    ref_scores = {name: score_candidate(prob, base, q_vec, row_weight)["rowweighted_delta_vs_h012"] for name, prob in refs.items()}
    rows: list[dict[str, Any]] = []
    frames: dict[str, pd.DataFrame] = {}
    masks: dict[str, np.ndarray] = {}
    for spec in candidate_specs():
        frame, mask = make_candidate(h012, q_vec, cells, spec)
        prob = frame[TARGETS].to_numpy(dtype=np.float64)
        rec = score_candidate(prob, base, q_vec, row_weight)
        rec.update(
            {
                "candidate_id": spec.candidate_id,
                "mode": spec.mode,
                "target_subset": spec.target_subset,
                "k": spec.k,
                "alpha": spec.alpha,
                "changed_rows": int(mask.any(axis=1).sum()),
                "changed_cells": int(mask.sum()),
                "mean_abs_prob_delta_vs_h012": float(np.mean(np.abs(prob - base))),
                "max_abs_prob_delta_vs_h012": float(np.max(np.abs(prob - base))),
                "mean_abs_prob_delta_vs_h020": float(np.mean(np.abs(prob - refs["h020"]))),
                "h020_rowweighted_delta_vs_h012": ref_scores["h020"],
                "h021_rowweighted_delta_vs_h012": ref_scores["h021"],
                "posterior_id": str(selected["posterior_id"]),
                "posterior_final_decision": str(selected.get("final_decision", "unknown")),
                "rowperm_public_p": float(selected.get("rowperm_public_p", 1.0)),
                "rowperm_hs_kl_p": float(selected.get("rowperm_hs_kl_p", 1.0)),
            }
        )
        rows.append(rec)
        frames[spec.candidate_id] = frame
        masks[spec.candidate_id] = mask
    cand = pd.DataFrame(rows)
    cand["beats_h020_under_h023"] = cand["rowweighted_delta_vs_h012"] < cand["h020_rowweighted_delta_vs_h012"]
    cand["h023_decision"] = np.select(
        [
            (cand["posterior_final_decision"].eq("pareto_action_candidate"))
            & (cand["rowweighted_delta_vs_h012"] < -0.0010)
            & (cand["row_beats_rate"] >= 0.98)
            & (cand["max_abs_prob_delta_vs_h012"] <= 0.16)
            & (cand["changed_cells"] >= 1000),
            (cand["posterior_final_decision"].isin(["pareto_action_candidate", "pareto_candidate"]))
            & (cand["rowweighted_delta_vs_h012"] < -0.00065)
            & (cand["max_abs_prob_delta_vs_h012"] <= 0.18),
        ],
        ["primary_pareto_action", "diagnostic_sensor"],
        default="diagnostic_only",
    )
    order = {"primary_pareto_action": 0, "diagnostic_sensor": 1, "diagnostic_only": 2}
    cand["decision_rank"] = cand["h023_decision"].map(order).astype(int)
    cand = cand.sort_values(["decision_rank", "rowweighted_delta_vs_h012", "changed_cells"]).reset_index(drop=True)

    materialized: dict[str, str] = {}
    keep = set(cand.head(45)["candidate_id"].astype(str))
    for cid, frame in frames.items():
        if cid not in keep:
            continue
        path = OUT / f"submission_h023_{safe_id(cid)}_{short_hash(frame)}.csv"
        frame.to_csv(path, index=False)
        validate_submission(path, sample)
        materialized[cid] = rel(path)
    cand["file"] = cand["candidate_id"].map(materialized).fillna("not_materialized")

    primary: Path | None = None
    promoted = cand.loc[cand["h023_decision"].eq("primary_pareto_action")]
    if not promoted.empty:
        best = promoted.iloc[0]
        primary = ROOT / f"submission_h023_hs_pareto_{safe_id(str(best['candidate_id']), 64)}_uploadsafe.csv"
        shutil.copyfile(OUT / Path(str(best["file"])).name, primary)
        validate_submission(primary, sample)
        cand.loc[cand["candidate_id"].eq(str(best["candidate_id"])), "file"] = rel(primary)
    cand.to_csv(CANDIDATE_OUT, index=False)
    return cand, primary


def write_report(
    pool: pd.DataFrame,
    align: pd.DataFrame,
    posteriors: pd.DataFrame,
    nulls: pd.DataFrame,
    row_state: pd.DataFrame,
    cells: pd.DataFrame,
    candidates: pd.DataFrame,
    primary: Path | None,
) -> None:
    lines: list[str] = [
        "# H023 Human-State Proposal/Pareto Vector-World HS-JEPA",
        "",
        "## Question",
        "",
        "Can q_hs choose among public-compatible vector worlds as a proposal/Pareto constraint, after H022 rejected q_hs as a final posterior prior?",
        "",
        "## Pool Sources",
        "",
        md_table(pool, 12),
        "",
        "## Public-Compatible Worlds vs Human-State Energy",
        "",
        "Public-error top-k worlds are compared against q_hs row-permutation controls.",
        "",
        md_table(align, 12),
        "",
        "## Pareto Posteriors",
        "",
        md_table(posteriors.head(24), 24),
        "",
        "## Row-Permutation Null",
        "",
        md_table(nulls.head(40), 40),
        "",
        "## Top Rows",
        "",
        md_table(row_state.head(24), 24),
        "",
        "## Top Cells",
        "",
        md_table(cells.head(30), 30),
        "",
        "## Candidate Selection",
        "",
        md_table(candidates.head(35), 35),
        "",
        "## Decision",
        "",
    ]
    if primary is None:
        lines.append("- No upload-safe H023 candidate promoted. q_hs proposal/Pareto evidence is diagnostic under this run.")
    else:
        lines.append(f"- Primary upload-safe candidate: `{primary.name}`")
        lines.append("- This file bets that q_hs can select a public-compatible hidden row-vector world without being the final generative prior.")
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- `{rel(POOL_OUT)}`",
            f"- `{rel(ALIGN_OUT)}`",
            f"- `{rel(POSTERIOR_OUT)}`",
            f"- `{rel(ROWPERM_OUT)}`",
            f"- `{rel(ROW_OUT)}`",
            f"- `{rel(CELL_OUT)}`",
            f"- `{rel(CANDIDATE_OUT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n")


def main() -> None:
    for old in OUT.glob("submission_h023_*.csv"):
        old.unlink()
    known, sample, h012, _, h020, h021_sub, pred_by_file = h022.load_frames()
    h012_prob = h012[TARGETS].to_numpy(dtype=np.float64)
    q_base = h022.pivot_cell(h022.H018_CELL, "q_hard", sample)
    row_weight = h022.row_weight_vector()
    hs_dist, hs_conf, _ = h022.build_hs_vector_prior(sample)
    _, contrib, actual = h022.contribution_tensor(known, pred_by_file, h012_prob, row_weight)

    pool, choices, preds, errors, source_arr, hs_energy = sample_pool(q_base, hs_dist, hs_conf, contrib, actual, row_weight)
    align = public_hs_alignment(choices, errors, hs_energy, hs_dist, row_weight)
    posteriors, dist_by_id, q_by_id, _ = evaluate_pareto_posteriors(
        choices, preds, errors, source_arr, hs_energy, contrib, actual, q_base, hs_dist
    )
    nulls = rowperm_null(posteriors, choices, errors, hs_dist, row_weight, contrib, actual)
    posteriors = add_rowperm_summary(posteriors, nulls)
    selected = posteriors.iloc[0]
    post_dist = dist_by_id[str(selected["posterior_id"])]
    q_vec = q_by_id[str(selected["posterior_id"])]
    row_state, cells = build_state_tables(sample, post_dist, q_vec, q_base, hs_dist, h012_prob, row_weight, selected)
    cells = cells.rename(columns={"q_h022": "q_h023", "h022_minus_h012": "h023_minus_h012", "h022_minus_base": "h023_minus_base", "hs_h022_agree": "hs_h023_agree"})
    cells.to_csv(CELL_OUT, index=False)
    candidates, primary = generate_candidates(sample, h012, h020, h021_sub, q_vec, cells, row_weight, selected)
    write_report(pool, align, posteriors, nulls, row_state, cells, candidates, primary)

    print("H023 selected posterior")
    print(posteriors.head(10).to_string(index=False))
    print("H023 candidates")
    print(candidates.head(12).to_string(index=False))
    print("primary", rel(primary) if primary else "None")


if __name__ == "__main__":
    main()
