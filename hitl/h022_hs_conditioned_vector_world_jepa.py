#!/usr/bin/env python3
"""H022: human-state conditioned vector-world HS-JEPA.

H020 proved that public equations are compatible with row-level 7-target
vector worlds, but its selected prior had beta=0. H021 proved that raw
human-state context predicts row-level target vectors, but direct q_hs
replacement is not action-safe.

H022 puts the two claims into one posterior:

    context = H018 public-equation marginals + H021 human-state vector prior
    target  = hidden row-level 7-bit Q/S vector world
    action  = move H012 toward the posterior only if conditional human-state
              vector worlds survive both public-delta and q_hs-row permutation
              stress.
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
ANALYSIS = ROOT / "analysis_outputs"
DATA = ROOT / "data"
HITL = ROOT / "hitl"
OUT = HITL / "h022_hs_conditioned_vector_world_jepa"
OUT.mkdir(parents=True, exist_ok=True)

for path in [ANALYSIS, HITL]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from public_anchor_bottleneck_decomposition import KEYS, TARGETS, known_public_table, load_sub, logit  # noqa: E402
import h021_human_state_vector_prior_jepa as h021  # noqa: E402


EPS = 1.0e-6
CURRENT = "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"
H018_PRIMARY = "submission_h018_hard_label_world_combined_all_k1750_a1_uploadsafe.csv"
H020_PRIMARY = "submission_h020_joint_vector_world_combined_all_k1750_a1_uploadsafe.csv"
H021_PRIMARY = "submission_h021_agree_h020_k1200_a1_e1546ba9_uploadsafe.csv"

H018_CELL = HITL / "h018_hard_label_world_jepa" / "h018_cell_hard_posterior.csv"
H019_ROW = HITL / "h019_row_subset_hardworld_jepa" / "h019_row_public_posterior.csv"
H021_ROWS = HITL / "h021_human_state_vector_prior_jepa" / "h021_test_human_state_vector_prior_rows.csv"

CONFIG_OUT = OUT / "h022_vector_world_configs.csv"
POSTERIOR_OUT = OUT / "h022_vector_posteriors.csv"
PUBLIC_NULL_OUT = OUT / "h022_public_delta_null.csv"
HS_NULL_OUT = OUT / "h022_hs_rowperm_null.csv"
ROW_OUT = OUT / "h022_row_state.csv"
CELL_OUT = OUT / "h022_cell_state.csv"
CANDIDATE_OUT = OUT / "h022_candidates.csv"
REPORT_OUT = OUT / "h022_report.md"


@dataclass(frozen=True)
class VectorConfig:
    config_id: str
    prior_kind: str
    beta: float
    n_samples: int


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
    k: int
    alpha: float
    target_subset: str = "all"


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(x, dtype=np.float64)))


def loss(prob: np.ndarray, y_prob: np.ndarray) -> np.ndarray:
    p = clip_prob(prob)
    q = clip_prob(y_prob)
    return -(q * np.log(p) + (1.0 - q) * np.log(1.0 - p))


def vector_table() -> np.ndarray:
    return np.asarray([[int(b) for b in format(i, "07b")] for i in range(128)], dtype=np.float64)


def code_from_labels(y: np.ndarray) -> np.ndarray:
    weights = np.asarray([64, 32, 16, 8, 4, 2, 1], dtype=np.int64)
    return (y.astype(np.int64) * weights.reshape(1, -1)).sum(axis=1)


def rank01(x: np.ndarray) -> np.ndarray:
    return pd.Series(np.asarray(x, dtype=np.float64)).rank(method="average", pct=True).to_numpy(dtype=np.float64)


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


def load_frames() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, np.ndarray]]:
    known = known_public_table().copy().sort_values("public_lb").reset_index(drop=True)
    h012 = load_sub(CURRENT)
    sample = h012[KEYS].copy()
    h018 = load_sub(H018_PRIMARY, sample)
    h020 = load_sub(H020_PRIMARY, sample)
    h021_sub = load_sub(H021_PRIMARY, sample)
    pred_by_file: dict[str, np.ndarray] = {}
    rows: list[dict[str, Any]] = []
    for rec in known.to_dict("records"):
        name = str(rec["file"])
        try:
            df = load_sub(name, sample)
        except FileNotFoundError:
            continue
        pred_by_file[name] = df[TARGETS].to_numpy(dtype=np.float64)
        rows.append(rec)
    known = pd.DataFrame(rows).sort_values("public_lb").reset_index(drop=True)
    if CURRENT not in set(known["file"].astype(str)):
        raise RuntimeError(f"{CURRENT} missing from known public table")
    return known, sample, h012, h018, h020, h021_sub, pred_by_file


def pivot_cell(path: Path, col: str, sample: pd.DataFrame) -> np.ndarray:
    src = pd.read_csv(path)
    mat = np.zeros((len(sample), len(TARGETS)), dtype=np.float64)
    for rec in src.to_dict("records"):
        mat[int(rec["row"]), TARGETS.index(str(rec["target"]))] = float(rec[col])
    if np.any(mat <= 0):
        raise ValueError(f"incomplete cell posterior: {path}")
    return clip_prob(mat)


def row_weight_vector() -> np.ndarray:
    row = pd.read_csv(H019_ROW).sort_values("row").reset_index(drop=True)
    w = row["row_weight"].to_numpy(dtype=np.float64)
    return w / max(float(w.sum()), 1.0e-30)


def h021_prior_configs() -> list[h021.PriorConfig]:
    return [
        h021.PriorConfig("global_state_k32", "state", "global", 32, 0.0, 0.50),
        h021.PriorConfig("global_all_k32", "all", "global", 32, 0.0, 0.50),
        h021.PriorConfig("global_social_sleep_k32", "social_sleep", "global", 32, 0.0, 0.50),
        h021.PriorConfig("subject_state_k10", "state", "subject", 10, 0.0, 0.75),
        h021.PriorConfig("subject_past_state_k10_d28", "state", "subject_past", 10, 28.0, 0.75),
        h021.PriorConfig("subject_all_k10", "all", "subject", 10, 0.0, 0.75),
        h021.PriorConfig("hybrid_state_k36_boost4", "state", "hybrid", 36, 45.0, 0.50, 4.0),
        h021.PriorConfig("hybrid_social_sleep_k36_boost4", "social_sleep", "hybrid", 36, 45.0, 0.50, 4.0),
        h021.PriorConfig("quality_global_k32", "quality", "global", 32, 0.0, 0.50),
        h021.PriorConfig("calendar_body_global_k32", "calendar_body", "global", 32, 0.0, 0.50),
    ]


def build_hs_vector_prior(sample: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, pd.DataFrame]:
    train, sample2, features, _, _, _ = h021.load_inputs()
    if not sample2[KEYS].equals(sample[KEYS]):
        raise ValueError("H021 sample alignment mismatch")
    train_mask = features["split"].astype(str).eq("train").to_numpy()
    test_mask = features["split"].astype(str).eq("test").to_numpy()
    y_train = train[TARGETS].to_numpy(dtype=np.float64)
    codes = code_from_labels(y_train)
    global_counts = np.bincount(codes, minlength=128).astype(np.float64) + 0.5
    global_vec_prior = global_counts / float(global_counts.sum())

    config_df = pd.read_csv(HITL / "h021_human_state_vector_prior_jepa" / "h021_vector_prior_configs.csv")
    top_cfgs = config_df.sort_values("config_score").head(4)["config_id"].astype(str).tolist()
    cfg_rows = config_df.set_index("config_id").loc[top_cfgs, "config_score"].to_numpy(dtype=np.float64)
    weights = np.exp(-(cfg_rows - float(cfg_rows.min())) / max(float(np.std(cfg_rows)), 1.0e-6))
    weights = weights / weights.sum()
    cfg_by_id = {cfg.config_id: cfg for cfg in h021_prior_configs()}
    groups = h021.feature_groups(features)
    train_subject = train["subject_id"].astype(str).to_numpy()
    test_subject = sample["subject_id"].astype(str).to_numpy()
    train_dates = train["lifelog_date"].to_numpy(dtype="datetime64[D]")
    test_dates = sample["lifelog_date"].to_numpy(dtype="datetime64[D]")

    dist = np.zeros((len(sample), 128), dtype=np.float64)
    for weight, cfg_id in zip(weights, top_cfgs):
        cfg = cfg_by_id[cfg_id]
        z = h021.standardized_matrix(features, groups[cfg.group], train_mask)
        z_train = z[train_mask]
        z_test = z[test_mask]
        part, _ = h021.knn_vector_prior(
            z_train,
            z_test,
            train_subject,
            test_subject,
            train_dates,
            test_dates,
            codes,
            global_vec_prior,
            cfg,
            self_exclude=False,
        )
        dist += float(weight) * part
    dist = dist / np.maximum(dist.sum(axis=1, keepdims=True), 1.0e-30)
    row = pd.read_csv(H021_ROWS, parse_dates=["sleep_date", "lifelog_date"])
    row = row.sort_values(KEYS).reset_index(drop=True)
    if not row[KEYS].equals(sample[KEYS]):
        raise ValueError("H021 row diagnostics alignment mismatch")
    return dist, row["hs_row_conf"].to_numpy(dtype=np.float64), config_df


def contribution_tensor(
    known: pd.DataFrame,
    pred_by_file: dict[str, np.ndarray],
    h012_prob: np.ndarray,
    row_weight: np.ndarray,
) -> tuple[list[str], np.ndarray, np.ndarray]:
    vecs = vector_table()
    base_lb = float(known.loc[known["file"].eq(CURRENT), "public_lb"].iloc[0])
    files: list[str] = []
    actual: list[float] = []
    for rec in known.to_dict("records"):
        name = str(rec["file"])
        if name == CURRENT or name not in pred_by_file:
            continue
        files.append(name)
        actual.append(float(rec["public_lb"]) - base_lb)
    contrib = np.zeros((len(files), h012_prob.shape[0], 128), dtype=np.float64)
    base_loss = np.zeros((h012_prob.shape[0], 128), dtype=np.float64)
    for row_i in range(h012_prob.shape[0]):
        base_loss[row_i] = loss(h012_prob[row_i].reshape(1, -1), vecs).mean(axis=1) * row_weight[row_i]
    for file_i, file_name in enumerate(files):
        pred = pred_by_file[file_name]
        for row_i in range(h012_prob.shape[0]):
            contrib[file_i, row_i] = loss(pred[row_i].reshape(1, -1), vecs).mean(axis=1) * row_weight[row_i] - base_loss[row_i]
    return files, contrib, np.asarray(actual, dtype=np.float64)


def build_row_distribution(q_base: np.ndarray, hs_dist: np.ndarray, hs_conf: np.ndarray, cfg: VectorConfig) -> np.ndarray:
    vecs = vector_table()
    q = clip_prob(q_base)
    logp = (
        vecs.reshape(1, 128, 7) * np.log(q).reshape(len(q), 1, 7)
        + (1.0 - vecs.reshape(1, 128, 7)) * np.log(1.0 - q).reshape(len(q), 1, 7)
    ).sum(axis=2)
    if cfg.prior_kind == "none":
        pass
    elif cfg.prior_kind == "hs":
        logp += cfg.beta * np.log(hs_dist + 1.0e-30)
    elif cfg.prior_kind == "hs_conf":
        scale = 0.25 + 1.25 * np.clip(hs_conf, 0.0, 1.0)
        logp += (cfg.beta * scale).reshape(-1, 1) * np.log(hs_dist + 1.0e-30)
    elif cfg.prior_kind == "hs_invconf":
        scale = 1.50 - np.clip(hs_conf, 0.0, 1.0)
        logp += (cfg.beta * scale).reshape(-1, 1) * np.log(hs_dist + 1.0e-30)
    elif cfg.prior_kind == "hs_marginal":
        q_hs = clip_prob(hs_dist @ vecs)
        q_mix = clip_prob(sigmoid((1.0 - cfg.beta) * logit(q) + cfg.beta * logit(q_hs)))
        logp = (
            vecs.reshape(1, 128, 7) * np.log(q_mix).reshape(len(q_mix), 1, 7)
            + (1.0 - vecs.reshape(1, 128, 7)) * np.log(1.0 - q_mix).reshape(len(q_mix), 1, 7)
        ).sum(axis=2)
    else:
        raise ValueError(cfg.prior_kind)
    logp -= logp.max(axis=1, keepdims=True)
    p = np.exp(logp)
    p /= np.maximum(p.sum(axis=1, keepdims=True), 1.0e-30)
    return p


def vector_configs() -> list[VectorConfig]:
    cfgs = [VectorConfig("none_b0", "none", 0.0, 60000)]
    for beta in [0.10, 0.18, 0.25, 0.35, 0.50, 0.75, 1.00, 1.35]:
        cfgs.append(VectorConfig(f"hs_b{beta:g}", "hs", beta, 60000))
    for beta in [0.20, 0.35, 0.55, 0.85]:
        cfgs.append(VectorConfig(f"hsconf_b{beta:g}", "hs_conf", beta, 60000))
    for beta in [0.25, 0.45, 0.65]:
        cfgs.append(VectorConfig(f"hsmarg_b{beta:g}", "hs_marginal", beta, 60000))
    return cfgs


def sample_worlds(
    dist: np.ndarray,
    contrib: np.ndarray,
    actual: np.ndarray,
    n_samples: int,
    seed: int,
    batch_size: int = 2500,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    n_rows = dist.shape[0]
    n_files = len(actual)
    choices = np.empty((n_samples, n_rows), dtype=np.uint8)
    preds = np.empty((n_samples, n_files), dtype=np.float64)
    errors = np.empty(n_samples, dtype=np.float64)
    cdf = np.cumsum(dist, axis=1)
    cursor = 0
    while cursor < n_samples:
        size = min(batch_size, n_samples - cursor)
        u = rng.random((size, n_rows), dtype=np.float64)
        batch_choices = np.empty((size, n_rows), dtype=np.uint8)
        for row_i in range(n_rows):
            batch_choices[:, row_i] = np.searchsorted(cdf[row_i], u[:, row_i]).astype(np.uint8)
        pred = np.zeros((size, n_files), dtype=np.float64)
        for row_i in range(n_rows):
            pred += contrib[:, row_i, batch_choices[:, row_i]].T
        err = np.mean(np.abs(pred - actual.reshape(1, -1)), axis=1)
        choices[cursor : cursor + size] = batch_choices
        preds[cursor : cursor + size] = pred
        errors[cursor : cursor + size] = err
        cursor += size
    return choices, preds, errors


def evaluate_configs(
    q_base: np.ndarray,
    hs_dist: np.ndarray,
    hs_conf: np.ndarray,
    contrib: np.ndarray,
    actual: np.ndarray,
) -> tuple[pd.DataFrame, dict[str, tuple[VectorConfig, np.ndarray, np.ndarray, np.ndarray, np.ndarray]]]:
    rows: list[dict[str, Any]] = []
    cache: dict[str, tuple[VectorConfig, np.ndarray, np.ndarray, np.ndarray, np.ndarray]] = {}
    for cfg_i, cfg in enumerate(vector_configs()):
        dist = build_row_distribution(q_base, hs_dist, hs_conf, cfg)
        choices, preds, errors = sample_worlds(dist, contrib, actual, cfg.n_samples, 20260622 + cfg_i)
        best = int(np.argmin(errors))
        rec = {
            "config_id": cfg.config_id,
            "prior_kind": cfg.prior_kind,
            "beta": cfg.beta,
            "n_samples": cfg.n_samples,
            "best_world_mae": float(errors.min()),
            "top100_world_mae": float(np.mean(np.sort(errors)[:100])),
            "p01_world_mae": float(np.quantile(errors, 0.01)),
            "p05_world_mae": float(np.quantile(errors, 0.05)),
            "median_world_mae": float(np.median(errors)),
            "best_world_p90_abs": float(np.quantile(np.abs(preds[best] - actual), 0.90)),
            "best_world_spearman": float(pd.Series(preds[best]).corr(pd.Series(actual), method="spearman")),
            "mean_row_vector_entropy": float(np.mean(-(dist * np.log(dist + 1.0e-30)).sum(axis=1))),
            "mean_max_vector_prob": float(np.mean(dist.max(axis=1))),
            "mean_hs_prior_kl": float(np.mean(np.sum(dist * (np.log(dist + 1.0e-30) - np.log(hs_dist + 1.0e-30)), axis=1))),
        }
        rec["config_score"] = (
            rec["top100_world_mae"]
            + 0.25 * rec["best_world_mae"]
            + 0.10 * rec["p01_world_mae"]
            - 0.00003 * rec["best_world_spearman"]
            - 0.000025 * (cfg.prior_kind != "none")
        )
        rows.append(rec)
        cache[cfg.config_id] = (cfg, dist, choices, preds, errors)
    out = pd.DataFrame(rows).sort_values(["config_score", "top100_world_mae"]).reset_index(drop=True)
    out.to_csv(CONFIG_OUT, index=False)
    return out, cache


def posterior_specs() -> list[PosteriorSpec]:
    specs: list[PosteriorSpec] = []
    for temp in [0.00008, 0.00012, 0.00018, 0.00025, 0.00035, 0.00055]:
        for power in [1.0, 1.5, 2.0]:
            specs.append(PosteriorSpec(f"soft_t{temp:g}_p{power:g}", "soft", temp, 0, power))
    for k in [100, 250, 500, 1000, 2500, 5000]:
        for temp in [0.00012, 0.00025, 0.00050]:
            specs.append(PosteriorSpec(f"top{k}_t{temp:g}", "topk", temp, k, 1.0))
        specs.append(PosteriorSpec(f"elite{k}", "elite", 0.0, k, 1.0))
    return specs


def posterior_weights(errors: np.ndarray, spec: PosteriorSpec) -> tuple[np.ndarray, float]:
    if spec.method == "soft":
        raw = np.exp(-(errors - float(errors.min())) / max(spec.temperature, 1.0e-12))
        raw = raw**spec.weight_power
    elif spec.method == "topk":
        order = np.argsort(errors)[: spec.top_k]
        raw = np.zeros(len(errors), dtype=np.float64)
        raw[order] = np.exp(-(errors[order] - float(errors[order].min())) / max(spec.temperature, 1.0e-12))
    elif spec.method == "elite":
        order = np.argsort(errors)[: spec.top_k]
        raw = np.zeros(len(errors), dtype=np.float64)
        raw[order] = 1.0
    else:
        raise ValueError(spec.method)
    if float(raw.sum()) <= 1.0e-30:
        raw[:] = 1.0
    weights = raw / float(raw.sum())
    return weights, float(1.0 / np.sum(weights * weights))


def posterior_distribution(choices: np.ndarray, weights: np.ndarray) -> np.ndarray:
    out = np.zeros((choices.shape[1], 128), dtype=np.float64)
    for row_i in range(choices.shape[1]):
        out[row_i] = np.bincount(choices[:, row_i], weights=weights, minlength=128)
    out /= np.maximum(out.sum(axis=1, keepdims=True), 1.0e-30)
    return out


def evaluate_posteriors(
    configs: pd.DataFrame,
    cache: dict[str, tuple[VectorConfig, np.ndarray, np.ndarray, np.ndarray, np.ndarray]],
    contrib: np.ndarray,
    actual: np.ndarray,
    q_base: np.ndarray,
    hs_dist: np.ndarray,
) -> tuple[pd.DataFrame, dict[str, np.ndarray], dict[str, np.ndarray]]:
    vecs = vector_table()
    rows: list[dict[str, Any]] = []
    dist_by_id: dict[str, np.ndarray] = {}
    q_by_id: dict[str, np.ndarray] = {}
    for cfg_rec in configs.head(8).to_dict("records"):
        config_id = str(cfg_rec["config_id"])
        cfg, prior_dist, choices, preds, errors = cache[config_id]
        for spec in posterior_specs():
            weights, ess = posterior_weights(errors, spec)
            post_dist = posterior_distribution(choices, weights)
            q_vec = clip_prob(post_dist @ vecs)
            pred = np.einsum("rv,frv->f", post_dist, contrib)
            err = pred - actual
            posterior_id = f"{config_id}_{spec.posterior_id}"
            row_kl_prior = float(np.mean(np.sum(post_dist * (np.log(post_dist + 1.0e-30) - np.log(prior_dist + 1.0e-30)), axis=1)))
            row_kl_hs = float(np.mean(np.sum(post_dist * (np.log(post_dist + 1.0e-30) - np.log(hs_dist + 1.0e-30)), axis=1)))
            rec = {
                "posterior_id": posterior_id,
                "config_id": config_id,
                "prior_kind": cfg.prior_kind,
                "beta": cfg.beta,
                "method": spec.method,
                "temperature": spec.temperature,
                "top_k": spec.top_k,
                "weight_power": spec.weight_power,
                "posterior_mae": float(np.mean(np.abs(err))),
                "posterior_p90_abs": float(np.quantile(np.abs(err), 0.90)),
                "posterior_spearman": float(pd.Series(pred).corr(pd.Series(actual), method="spearman")),
                "best_world_mae": float(errors.min()),
                "top100_world_mae": float(np.mean(np.sort(errors)[:100])),
                "median_world_mae": float(np.median(errors)),
                "ess": ess,
                "ess_rate": float(ess / len(errors)),
                "q_abs_shift_vs_base": float(np.mean(np.abs(q_vec - q_base))),
                "q_max_abs_shift_vs_base": float(np.max(np.abs(q_vec - q_base))),
                "q_spearman_vs_base": float(pd.Series(q_vec.reshape(-1)).corr(pd.Series(q_base.reshape(-1)), method="spearman")),
                "mean_max_vector_posterior": float(np.mean(post_dist.max(axis=1))),
                "row_vector_kl_from_prior": row_kl_prior,
                "row_vector_kl_from_hs": row_kl_hs,
            }
            rec["posterior_score"] = (
                rec["posterior_mae"]
                + 0.25 * rec["posterior_p90_abs"]
                - 0.00004 * rec["posterior_spearman"]
                - 0.000015 * (cfg.prior_kind != "none")
                + 0.00004 * max(160.0 - ess, 0.0) / 160.0
            )
            rows.append(rec)
            dist_by_id[posterior_id] = post_dist
            q_by_id[posterior_id] = q_vec
    out = pd.DataFrame(rows).sort_values(["posterior_score", "posterior_mae"]).reset_index(drop=True)
    out.to_csv(POSTERIOR_OUT, index=False)
    return out, dist_by_id, q_by_id


def public_delta_null(
    configs: pd.DataFrame,
    cache: dict[str, tuple[VectorConfig, np.ndarray, np.ndarray, np.ndarray, np.ndarray]],
    actual: np.ndarray,
    n_perm: int = 300,
) -> pd.DataFrame:
    best_id = str(configs.iloc[0]["config_id"])
    cfg, _, _, preds, errors = cache[best_id]
    best = int(np.argmin(errors))
    rows = [
        {
            "kind": "real",
            "iteration": -1,
            "config_id": best_id,
            "prior_kind": cfg.prior_kind,
            "beta": cfg.beta,
            "best_world_mae": float(errors.min()),
            "top100_world_mae": float(np.mean(np.sort(errors)[:100])),
            "p01_world_mae": float(np.quantile(errors, 0.01)),
            "median_world_mae": float(np.median(errors)),
            "best_world_p90_abs": float(np.quantile(np.abs(preds[best] - actual), 0.90)),
            "best_world_spearman": float(pd.Series(preds[best]).corr(pd.Series(actual), method="spearman")),
        }
    ]
    rng = np.random.default_rng(20260623)
    for i in range(n_perm):
        perm_actual = rng.permutation(actual)
        perm_errors = np.mean(np.abs(preds - perm_actual.reshape(1, -1)), axis=1)
        pbest = int(np.argmin(perm_errors))
        rows.append(
            {
                "kind": "permute_actual",
                "iteration": i,
                "config_id": best_id,
                "prior_kind": cfg.prior_kind,
                "beta": cfg.beta,
                "best_world_mae": float(perm_errors.min()),
                "top100_world_mae": float(np.mean(np.sort(perm_errors)[:100])),
                "p01_world_mae": float(np.quantile(perm_errors, 0.01)),
                "median_world_mae": float(np.median(perm_errors)),
                "best_world_p90_abs": float(np.quantile(np.abs(preds[pbest] - perm_actual), 0.90)),
                "best_world_spearman": float(pd.Series(preds[pbest]).corr(pd.Series(perm_actual), method="spearman")),
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(PUBLIC_NULL_OUT, index=False)
    return out


def hs_rowperm_null(
    configs: pd.DataFrame,
    q_base: np.ndarray,
    hs_dist: np.ndarray,
    hs_conf: np.ndarray,
    contrib: np.ndarray,
    actual: np.ndarray,
    n_perm: int = 80,
) -> pd.DataFrame:
    positive = configs.loc[configs["prior_kind"].astype(str).ne("none")].copy()
    if positive.empty:
        positive = configs.copy()
    best_cfg_id = str(positive.iloc[0]["config_id"])
    cfg = next(c for c in vector_configs() if c.config_id == best_cfg_id)
    real_dist = build_row_distribution(q_base, hs_dist, hs_conf, cfg)
    _, real_preds, real_errors = sample_worlds(real_dist, contrib, actual, 15000, 20260624)
    rows = [
        {
            "kind": "real",
            "iteration": -1,
            "config_id": cfg.config_id,
            "prior_kind": cfg.prior_kind,
            "beta": cfg.beta,
            "best_world_mae": float(real_errors.min()),
            "top100_world_mae": float(np.mean(np.sort(real_errors)[:100])),
            "p01_world_mae": float(np.quantile(real_errors, 0.01)),
            "median_world_mae": float(np.median(real_errors)),
        }
    ]
    rng = np.random.default_rng(20260625)
    for i in range(n_perm):
        perm = rng.permutation(len(hs_dist))
        dist = build_row_distribution(q_base, hs_dist[perm], hs_conf[perm], cfg)
        _, _, errors = sample_worlds(dist, contrib, actual, 8000, 20260625 + i)
        rows.append(
            {
                "kind": "permute_hs_rows",
                "iteration": i,
                "config_id": cfg.config_id,
                "prior_kind": cfg.prior_kind,
                "beta": cfg.beta,
                "best_world_mae": float(errors.min()),
                "top100_world_mae": float(np.mean(np.sort(errors)[:100])),
                "p01_world_mae": float(np.quantile(errors, 0.01)),
                "median_world_mae": float(np.median(errors)),
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(HS_NULL_OUT, index=False)
    return out


def null_summary(nulls: pd.DataFrame) -> pd.DataFrame:
    real = nulls[nulls["kind"].eq("real")].iloc[0]
    perm = nulls[nulls["kind"].ne("real")]
    rows: list[dict[str, Any]] = []
    for metric, direction in [
        ("best_world_mae", "lower"),
        ("top100_world_mae", "lower"),
        ("p01_world_mae", "lower"),
        ("median_world_mae", "lower"),
    ]:
        rv = float(real[metric])
        pv = perm[metric].astype(float)
        p = float((1 + (pv <= rv).sum()) / (len(pv) + 1))
        rows.append(
            {
                "metric": metric,
                "direction": direction,
                "real": rv,
                "null_mean": float(pv.mean()),
                "null_p10": float(pv.quantile(0.10)),
                "null_p50": float(pv.quantile(0.50)),
                "null_p90": float(pv.quantile(0.90)),
                "real_percentile_vs_null": float((pv < rv).mean()),
                "one_sided_p": p,
            }
        )
    return pd.DataFrame(rows)


def build_state_tables(
    sample: pd.DataFrame,
    post_dist: np.ndarray,
    q_vec: np.ndarray,
    q_base: np.ndarray,
    q_hs: np.ndarray,
    h012_prob: np.ndarray,
    row_weight: np.ndarray,
    selected: pd.Series,
    write_outputs: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    vecs = vector_table()
    max_idx = post_dist.argmax(axis=1)
    row_entropy = -(post_dist * np.log(post_dist + 1.0e-30)).sum(axis=1)
    row_gain = (loss(h012_prob, q_vec) - loss(q_vec, q_vec)).mean(axis=1)
    row_shift = np.mean(np.abs(q_vec - q_base), axis=1)
    hs_kl = np.sum(post_dist * (np.log(post_dist + 1.0e-30) - np.log(q_hs + 1.0e-30)), axis=1)
    row_score = 0.34 * rank01(row_weight) + 0.30 * rank01(row_gain) + 0.18 * rank01(row_shift) + 0.18 * rank01(-hs_kl)
    vector_labels = ["".join(str(int(v)) for v in row) for row in vecs]
    rows: list[dict[str, Any]] = []
    cells: list[dict[str, Any]] = []
    q_hs_marg = clip_prob(q_hs @ vecs)
    for row_i in range(len(sample)):
        rows.append(
            {
                "row": row_i,
                "subject_id": sample.iloc[row_i]["subject_id"],
                "sleep_date": sample.iloc[row_i]["sleep_date"],
                "lifelog_date": sample.iloc[row_i]["lifelog_date"],
                "row_weight": float(row_weight[row_i]),
                "max_vector_code": int(max_idx[row_i]),
                "max_vector": vector_labels[int(max_idx[row_i])],
                "max_vector_prob": float(post_dist[row_i, max_idx[row_i]]),
                "row_vector_entropy": float(row_entropy[row_i]),
                "row_gain_to_h022_vector": float(row_gain[row_i]),
                "row_abs_shift_vs_base": float(row_shift[row_i]),
                "row_kl_from_hs": float(hs_kl[row_i]),
                "row_score": float(row_score[row_i]),
                "posterior_id": str(selected["posterior_id"]),
            }
        )
        for target_i, target in enumerate(TARGETS):
            h022_dir = float(logit(q_vec[row_i, target_i]) - logit(h012_prob[row_i, target_i]))
            hs_dir = float(logit(q_hs_marg[row_i, target_i]) - logit(h012_prob[row_i, target_i]))
            cells.append(
                {
                    "row": row_i,
                    "target": target,
                    "h012_prob": float(h012_prob[row_i, target_i]),
                    "q_base_prob": float(q_base[row_i, target_i]),
                    "hs_prob": float(q_hs_marg[row_i, target_i]),
                    "q_h022": float(q_vec[row_i, target_i]),
                    "h022_minus_h012": float(q_vec[row_i, target_i] - h012_prob[row_i, target_i]),
                    "h022_minus_base": float(q_vec[row_i, target_i] - q_base[row_i, target_i]),
                    "hs_h022_agree": bool(np.sign(hs_dir) == np.sign(h022_dir) and abs(hs_dir) > 1.0e-9 and abs(h022_dir) > 1.0e-9),
                    "row_weight": float(row_weight[row_i]),
                    "row_score": float(row_score[row_i]),
                    "cell_gain": float(loss(h012_prob[row_i, target_i], q_vec[row_i, target_i]) - loss(q_vec[row_i, target_i], q_vec[row_i, target_i])),
                }
            )
    row_df = pd.DataFrame(rows).sort_values("row_score", ascending=False).reset_index(drop=True)
    cell_df = pd.DataFrame(cells)
    cell_df["abs_h022_logit_move"] = np.abs(logit(cell_df["q_h022"].to_numpy()) - logit(cell_df["h012_prob"].to_numpy()))
    cell_df["abs_shift_vs_base"] = np.abs(cell_df["h022_minus_base"].to_numpy(dtype=np.float64))
    cell_df["gain_score"] = rank01(cell_df["cell_gain"].to_numpy(dtype=np.float64))
    cell_df["move_score"] = rank01(cell_df["abs_h022_logit_move"].to_numpy(dtype=np.float64))
    cell_df["shift_score"] = rank01(cell_df["abs_shift_vs_base"].to_numpy(dtype=np.float64))
    cell_df["row_score_rank"] = rank01(cell_df["row_score"].to_numpy(dtype=np.float64))
    cell_df["hs_agree_score"] = np.where(cell_df["hs_h022_agree"].to_numpy(dtype=bool), 1.0, 0.0)
    cell_df["combined_score"] = (
        0.34 * cell_df["gain_score"]
        + 0.22 * cell_df["move_score"]
        + 0.16 * cell_df["shift_score"]
        + 0.16 * cell_df["row_score_rank"]
        + 0.12 * cell_df["hs_agree_score"]
    )
    sorted_cells = cell_df.sort_values("combined_score", ascending=False).reset_index(drop=True)
    if write_outputs:
        row_df.to_csv(ROW_OUT, index=False)
        sorted_cells.to_csv(CELL_OUT, index=False)
    return row_df, sorted_cells


def candidate_specs() -> list[CandidateSpec]:
    specs: list[CandidateSpec] = []
    for mode in ["combined", "gain", "hsagree", "shift"]:
        for k in [700, 1000, 1200, 1500, 1750]:
            for alpha in [0.75, 1.0, 1.25]:
                specs.append(CandidateSpec(f"{mode}_all_k{k}_a{alpha:g}", mode, k, alpha, "all"))
    for subset in ["Q", "S"]:
        for mode in ["combined", "hsagree"]:
            for k in [250, 450, 700, 900]:
                for alpha in [0.75, 1.0]:
                    specs.append(CandidateSpec(f"{mode}_{subset}_k{k}_a{alpha:g}", mode, k, alpha, subset))
    return specs


def target_mask(target_subset: str, shape: tuple[int, int]) -> np.ndarray:
    mask = np.zeros(shape, dtype=bool)
    if target_subset == "all":
        mask[:, :] = True
    elif target_subset == "Q":
        mask[:, :3] = True
    elif target_subset == "S":
        mask[:, 3:] = True
    else:
        raise ValueError(target_subset)
    return mask.reshape(-1)


def make_candidate(h012: pd.DataFrame, q_vec: np.ndarray, cells: pd.DataFrame, spec: CandidateSpec) -> tuple[pd.DataFrame, np.ndarray]:
    base_prob = h012[TARGETS].to_numpy(dtype=np.float64)
    valid = target_mask(spec.target_subset, base_prob.shape)
    score_col = {
        "combined": "combined_score",
        "gain": "gain_score",
        "hsagree": "hs_agree_score",
        "shift": "shift_score",
    }[spec.mode]
    scores = np.full(base_prob.size, -np.inf, dtype=np.float64)
    for rec in cells.to_dict("records"):
        idx = int(rec["row"]) * len(TARGETS) + TARGETS.index(str(rec["target"]))
        scores[idx] = float(rec[score_col])
        if spec.mode == "hsagree" and not bool(rec["hs_h022_agree"]):
            valid[idx] = False
    candidates = np.flatnonzero(valid)
    chosen = candidates[np.argsort(scores[candidates])[-min(spec.k, len(candidates)) :]]
    mask = np.zeros(base_prob.size, dtype=bool)
    mask[chosen] = True
    mask = mask.reshape(base_prob.shape)
    moved = logit(base_prob)
    moved[mask] = moved[mask] + spec.alpha * (logit(q_vec)[mask] - logit(base_prob)[mask])
    out = h012.copy()
    out[TARGETS] = clip_prob(sigmoid(moved))
    return out, mask


def score_candidate(prob: np.ndarray, base: np.ndarray, q_vec: np.ndarray, row_weight: np.ndarray) -> dict[str, float]:
    row_diff = (loss(prob, q_vec) - loss(base, q_vec)).mean(axis=1)
    return {
        "rowweighted_delta_vs_h012": float(row_diff @ row_weight),
        "uniform_delta_vs_h012": float(row_diff.mean()),
        "row_beats_rate": float(np.mean(row_diff < 0.0)),
        "row_p90_delta": float(np.quantile(row_diff, 0.90)),
    }


def validate_submission(path: Path, sample: pd.DataFrame) -> dict[str, Any]:
    df = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"])
    if list(df.columns) != KEYS + TARGETS:
        raise ValueError(f"bad columns: {path}")
    if len(df) != len(sample) or not df[KEYS].equals(sample[KEYS]):
        raise ValueError(f"bad keys: {path}")
    arr = df[TARGETS].to_numpy(dtype=np.float64)
    if not np.isfinite(arr).all():
        raise ValueError(f"nonfinite probabilities: {path}")
    if arr.min() < EPS or arr.max() > 1.0 - EPS:
        raise ValueError(f"probability bounds failed: {path}")
    return {"shape": tuple(df.shape), "min_prob": float(arr.min()), "max_prob": float(arr.max()), "duplicate_keys": int(df.duplicated(KEYS).sum())}


def generate_candidates(
    sample: pd.DataFrame,
    h012: pd.DataFrame,
    h018: pd.DataFrame,
    h020: pd.DataFrame,
    h021_sub: pd.DataFrame,
    q_vec: np.ndarray,
    cells: pd.DataFrame,
    row_weight: np.ndarray,
    selected: pd.Series,
    hs_nulls: pd.DataFrame,
) -> tuple[pd.DataFrame, Path | None]:
    for old in OUT.glob("submission_h022_*.csv"):
        old.unlink()
    base = h012[TARGETS].to_numpy(dtype=np.float64)
    refs = {
        "h018": h018[TARGETS].to_numpy(dtype=np.float64),
        "h020": h020[TARGETS].to_numpy(dtype=np.float64),
        "h021": h021_sub[TARGETS].to_numpy(dtype=np.float64),
    }
    ref_scores = {name: score_candidate(prob, base, q_vec, row_weight)["rowweighted_delta_vs_h012"] for name, prob in refs.items()}
    rows: list[dict[str, Any]] = []
    frames: list[tuple[pd.DataFrame, CandidateSpec]] = []
    for spec in candidate_specs():
        out, mask = make_candidate(h012, q_vec, cells, spec)
        prob = out[TARGETS].to_numpy(dtype=np.float64)
        rec = score_candidate(prob, base, q_vec, row_weight)
        rec.update(
            {
                "candidate_id": spec.candidate_id,
                "mode": spec.mode,
                "target_subset": spec.target_subset,
                "k": spec.k,
                "alpha": spec.alpha,
                "changed_rows": int(np.any(np.abs(prob - base) > 1.0e-12, axis=1).sum()),
                "changed_cells": int((np.abs(prob - base) > 1.0e-12).sum()),
                "mean_abs_prob_delta_vs_h012": float(np.mean(np.abs(prob - base))),
                "max_abs_prob_delta_vs_h012": float(np.max(np.abs(prob - base))),
                "mean_abs_prob_delta_vs_h020": float(np.mean(np.abs(prob - refs["h020"]))),
                "h018_rowweighted_delta_vs_h012": ref_scores["h018"],
                "h020_rowweighted_delta_vs_h012": ref_scores["h020"],
                "h021_rowweighted_delta_vs_h012": ref_scores["h021"],
                "selected_prior_kind": str(selected["prior_kind"]),
                "selected_beta": float(selected["beta"]),
            }
        )
        rows.append(rec)
        frames.append((out, spec))
    cand = pd.DataFrame(rows)
    hs_sum = null_summary(hs_nulls)
    hs_real_top = float(hs_sum.loc[hs_sum["metric"].eq("top100_world_mae"), "real"].iloc[0])
    hs_null_p50 = float(hs_sum.loc[hs_sum["metric"].eq("top100_world_mae"), "null_p50"].iloc[0])
    hs_prior_survives = bool(str(selected["prior_kind"]) != "none" and hs_real_top < hs_null_p50)
    cand["beats_h020_under_h022"] = cand["rowweighted_delta_vs_h012"] < cand["h020_rowweighted_delta_vs_h012"]
    cand["h022_decision"] = np.select(
        [
            hs_prior_survives
            & cand["beats_h020_under_h022"]
            & (cand["rowweighted_delta_vs_h012"] < -0.00070)
            & (cand["changed_cells"] >= 1000)
            & (cand["max_abs_prob_delta_vs_h012"] <= 0.17),
            hs_prior_survives
            & (cand["rowweighted_delta_vs_h012"] < -0.00055)
            & (cand["changed_cells"] >= 700),
        ],
        ["hs_conditioned_vector_big_bet", "hs_conditioned_vector_sensor"],
        default="diagnostic_only",
    )
    order = {"hs_conditioned_vector_big_bet": 0, "hs_conditioned_vector_sensor": 1, "diagnostic_only": 2}
    cand["decision_rank"] = cand["h022_decision"].map(order).astype(int)
    cand = cand.sort_values(["decision_rank", "rowweighted_delta_vs_h012", "mean_abs_prob_delta_vs_h020"], ascending=[True, True, False]).reset_index(drop=True)
    keep = set(cand.head(40)["candidate_id"].astype(str))
    materialized: dict[str, str] = {}
    for out, spec in frames:
        if spec.candidate_id not in keep:
            continue
        path = OUT / f"submission_h022_{safe_id(spec.candidate_id)}_{short_hash(out)}.csv"
        out.to_csv(path, index=False)
        materialized[spec.candidate_id] = rel(path)
    cand["file"] = cand["candidate_id"].map(materialized).fillna("not_materialized")
    primary: Path | None = None
    promoted = cand[cand["h022_decision"].ne("diagnostic_only")].head(1)
    if not promoted.empty:
        source = ROOT / str(promoted.iloc[0]["file"])
        primary = ROOT / f"submission_h022_hs_conditioned_vector_{safe_id(str(promoted.iloc[0]['candidate_id']), 64)}_uploadsafe.csv"
        for old in ROOT.glob("submission_h022_*_uploadsafe.csv"):
            if old != primary:
                old.unlink()
        shutil.copyfile(source, primary)
        validate_submission(primary, sample)
    cand.to_csv(CANDIDATE_OUT, index=False)
    return cand, primary


def write_report(
    h021_configs: pd.DataFrame,
    configs: pd.DataFrame,
    posteriors: pd.DataFrame,
    public_nulls: pd.DataFrame,
    hs_nulls: pd.DataFrame,
    row_state: pd.DataFrame,
    cells: pd.DataFrame,
    candidates: pd.DataFrame,
    primary: Path | None,
) -> None:
    lines = [
        "# H022 Human-State Conditioned Vector-World HS-JEPA",
        "",
        "## Question",
        "",
        "Can H021's human-state target-vector prior become the actual row-vector prior inside the H020 public-equation vector-world posterior?",
        "",
        "## H021 Prior Evidence Used",
        "",
        md_table(h021_configs.sort_values("config_score").head(10), 10),
        "",
        "## Vector-World Configs",
        "",
        md_table(configs.head(18), 18),
        "",
        "## Vector Posteriors",
        "",
        md_table(posteriors.head(18), 18),
        "",
        "## Public-Delta Null",
        "",
        "Known public deltas are permuted while sampled vector-world predictions are kept fixed.",
        "",
        md_table(null_summary(public_nulls), 8),
        "",
        "## Human-State Row-Permutation Null",
        "",
        "The q_hs rows are permuted before vector-world sampling. This tests whether row-conditioned human-state prior matters, not only aggregate vector frequency.",
        "",
        md_table(null_summary(hs_nulls), 8),
        "",
        "## Row State Summary",
        "",
        md_table(
            pd.DataFrame(
                [
                    {
                        "rows": len(row_state),
                        "mean_max_vector_prob": float(row_state["max_vector_prob"].mean()),
                        "mean_entropy": float(row_state["row_vector_entropy"].mean()),
                        "mean_kl_from_hs": float(row_state["row_kl_from_hs"].mean()),
                        "top20_row_weight_mass": float(row_state.head(20)["row_weight"].sum()),
                    }
                ]
            )
        ),
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
        md_table(candidates.head(30), 30),
        "",
        "## Decision",
        "",
    ]
    if primary is None:
        lines.append("- No upload-safe H022 candidate promoted. The conditional human-state vector prior is diagnostic under this run.")
    else:
        lines.append(f"- Primary upload-safe candidate: `{primary.name}`")
        lines.append("- This file bets that human-state-conditioned vector worlds beat both H020's beta-zero posterior and row-permuted q_hs controls.")
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- `{rel(CONFIG_OUT)}`",
            f"- `{rel(POSTERIOR_OUT)}`",
            f"- `{rel(PUBLIC_NULL_OUT)}`",
            f"- `{rel(HS_NULL_OUT)}`",
            f"- `{rel(ROW_OUT)}`",
            f"- `{rel(CELL_OUT)}`",
            f"- `{rel(CANDIDATE_OUT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    known, sample, h012, h018, h020, h021_sub, pred_by_file = load_frames()
    h012_prob = h012[TARGETS].to_numpy(dtype=np.float64)
    q_base = pivot_cell(H018_CELL, "q_hard", sample)
    row_weight = row_weight_vector()
    hs_dist, hs_conf, h021_configs = build_hs_vector_prior(sample)
    _, contrib, actual = contribution_tensor(known, pred_by_file, h012_prob, row_weight)
    configs, cache = evaluate_configs(q_base, hs_dist, hs_conf, contrib, actual)
    posteriors, dist_by_id, q_by_id = evaluate_posteriors(configs, cache, contrib, actual, q_base, hs_dist)
    public_nulls = public_delta_null(configs, cache, actual)
    hs_nulls = hs_rowperm_null(configs, q_base, hs_dist, hs_conf, contrib, actual)
    selected = posteriors.iloc[0]
    post_dist = dist_by_id[str(selected["posterior_id"])]
    q_vec = q_by_id[str(selected["posterior_id"])]
    row_state, cells = build_state_tables(sample, post_dist, q_vec, q_base, hs_dist, h012_prob, row_weight, selected)
    candidates, primary = generate_candidates(sample, h012, h018, h020, h021_sub, q_vec, cells, row_weight, selected, hs_nulls)
    write_report(h021_configs, configs, posteriors, public_nulls, hs_nulls, row_state, cells, candidates, primary)

    print(f"wrote {REPORT_OUT}")
    print(f"primary {primary}")
    print(configs.head(10).to_string(index=False))
    print(posteriors.head(10).to_string(index=False))
    print(candidates.head(12).to_string(index=False))


if __name__ == "__main__":
    main()
