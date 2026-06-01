#!/usr/bin/env python3
"""H020: joint target-vector hardworld HS-JEPA.

H018 sampled every row x target cell independently. Real labels are generated
as a seven-target vector for each row. H020 adds that missing constraint:

    context = H018/H019 public equation posterior + train target-vector law
    target  = hidden row-level 7-bit label-vector world
    action  = move H012 toward the posterior marginals of valid label vectors

If target-vector worlds survive public-delta stress, HS-JEPA can claim the
public-equation latent is not only a cell posterior; it is compatible with a
joint Q/S target route. If they fail, independent-cell H018 remains the better
public-equation materializer.
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
DATA = ROOT / "data"
H020 = ROOT / "hitl" / "h020_joint_vector_world_jepa"
H020.mkdir(parents=True, exist_ok=True)

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
H019_PRIMARY = "submission_h019_row_subset_hardworld_gain_all_r240_a1_uploadsafe.csv"

REPORT_OUT = H020 / "h020_report.md"
CONFIG_OUT = H020 / "h020_vector_world_configs.csv"
POSTERIOR_OUT = H020 / "h020_vector_posteriors.csv"
NULL_OUT = H020 / "h020_vector_null_stress.csv"
ROW_OUT = H020 / "h020_row_vector_state.csv"
CELL_OUT = H020 / "h020_cell_joint_vector_posterior.csv"
CANDIDATE_OUT = H020 / "h020_candidates.csv"


@dataclass(frozen=True)
class VectorPriorConfig:
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
    target_subset: str
    k: int
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


def vector_table() -> np.ndarray:
    return np.asarray([[int(b) for b in format(i, "07b")] for i in range(128)], dtype=np.float64)


def code_from_labels(y: np.ndarray) -> np.ndarray:
    weights = np.asarray([64, 32, 16, 8, 4, 2, 1], dtype=np.int64)
    return (y.astype(np.int64) * weights.reshape(1, -1)).sum(axis=1)


def pivot_cell(path: Path, col: str, sample: pd.DataFrame) -> np.ndarray:
    src = pd.read_csv(path)
    mat = np.zeros((len(sample), len(TARGETS)), dtype=np.float64)
    for rec in src.to_dict("records"):
        mat[int(rec["row"]), TARGETS.index(str(rec["target"]))] = float(rec[col])
    return clip_prob(mat)


def load_frames() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, np.ndarray]]:
    known = known_public_table().copy().sort_values("public_lb").reset_index(drop=True)
    if CURRENT not in set(known["file"].astype(str)):
        raise RuntimeError(f"{CURRENT} missing from known public table")
    h012 = load_sub(CURRENT)
    h018 = load_sub(H018_PRIMARY, h012[KEYS])
    h019 = load_sub(H019_PRIMARY, h012[KEYS])
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
    return known, h012[KEYS].copy(), h012, h018, h019, pred_by_file


def build_vector_priors(sample: pd.DataFrame) -> tuple[np.ndarray, dict[str, np.ndarray], pd.DataFrame]:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv")
    y = train[TARGETS].to_numpy(dtype=np.int64)
    codes = code_from_labels(y)
    vecs = vector_table()
    global_counts = np.bincount(codes, minlength=128).astype(np.float64) + 0.5
    global_prior = global_counts / float(global_counts.sum())
    subject_priors: dict[str, np.ndarray] = {}
    for subject in sorted(train["subject_id"].astype(str).unique()):
        mask = train["subject_id"].astype(str).eq(subject).to_numpy()
        counts = np.bincount(codes[mask], minlength=128).astype(np.float64)
        counts = counts + 0.25 * global_prior * 128.0
        subject_priors[subject] = counts / float(counts.sum())
    for subject in sample["subject_id"].astype(str).unique():
        subject_priors.setdefault(str(subject), global_prior)
    code_summary = pd.DataFrame(
        {
            "code": np.arange(128),
            "vector": ["".join(str(int(v)) for v in row) for row in vecs],
            "train_count": np.bincount(codes, minlength=128),
            "global_prior": global_prior,
        }
    ).sort_values("global_prior", ascending=False)
    return global_prior, subject_priors, code_summary


def build_row_distributions(
    q_prior: np.ndarray,
    sample: pd.DataFrame,
    global_prior: np.ndarray,
    subject_priors: dict[str, np.ndarray],
    cfg: VectorPriorConfig,
) -> np.ndarray:
    vecs = vector_table()
    q = clip_prob(q_prior)
    logp = (
        vecs.reshape(1, 128, 7) * np.log(q).reshape(len(q), 1, 7)
        + (1.0 - vecs.reshape(1, 128, 7)) * np.log(1.0 - q).reshape(len(q), 1, 7)
    ).sum(axis=2)
    if cfg.prior_kind == "global":
        logp += cfg.beta * np.log(global_prior + 1.0e-30).reshape(1, -1)
    elif cfg.prior_kind == "subject":
        priors = np.vstack([subject_priors.get(str(s), global_prior) for s in sample["subject_id"].astype(str)])
        logp += cfg.beta * np.log(priors + 1.0e-30)
    elif cfg.prior_kind == "none":
        pass
    else:
        raise ValueError(cfg.prior_kind)
    logp -= logp.max(axis=1, keepdims=True)
    p = np.exp(logp)
    p /= p.sum(axis=1, keepdims=True)
    return p


def row_weight_vector() -> np.ndarray:
    row = pd.read_csv(H020.parent / "h019_row_subset_hardworld_jepa" / "h019_row_public_posterior.csv")
    row = row.sort_values("row").reset_index(drop=True)
    w = row["row_weight"].to_numpy(dtype=np.float64)
    return w / max(float(w.sum()), 1.0e-30)


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


def sample_worlds(
    dist: np.ndarray,
    contrib: np.ndarray,
    actual: np.ndarray,
    cfg: VectorPriorConfig,
    seed: int,
    batch_size: int = 2500,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    n_rows = dist.shape[0]
    n_files = len(actual)
    choices = np.empty((cfg.n_samples, n_rows), dtype=np.uint8)
    preds = np.empty((cfg.n_samples, n_files), dtype=np.float64)
    errors = np.empty(cfg.n_samples, dtype=np.float64)
    cdf = np.cumsum(dist, axis=1)
    cursor = 0
    while cursor < cfg.n_samples:
        size = min(batch_size, cfg.n_samples - cursor)
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


def vector_prior_configs() -> list[VectorPriorConfig]:
    out = [VectorPriorConfig("none", 0.0, 70000)]
    for kind in ["global", "subject"]:
        for beta in [0.15, 0.25, 0.40, 0.60, 0.85, 1.15]:
            out.append(VectorPriorConfig(kind, beta, 70000))
    return out


def evaluate_configs(
    sample: pd.DataFrame,
    q_prior: np.ndarray,
    global_prior: np.ndarray,
    subject_priors: dict[str, np.ndarray],
    contrib: np.ndarray,
    actual: np.ndarray,
) -> tuple[pd.DataFrame, dict[str, tuple[VectorPriorConfig, np.ndarray, np.ndarray, np.ndarray, np.ndarray]]]:
    rows: list[dict[str, Any]] = []
    cache: dict[str, tuple[VectorPriorConfig, np.ndarray, np.ndarray, np.ndarray, np.ndarray]] = {}
    for cfg_i, cfg in enumerate(vector_prior_configs()):
        dist = build_row_distributions(q_prior, sample, global_prior, subject_priors, cfg)
        choices, preds, errors = sample_worlds(dist, contrib, actual, cfg, 20260606 + cfg_i)
        best_idx = int(np.argmin(errors))
        best_pred = preds[best_idx]
        rec = {
            "config_id": f"{cfg.prior_kind}_b{cfg.beta:g}",
            "prior_kind": cfg.prior_kind,
            "beta": cfg.beta,
            "n_samples": cfg.n_samples,
            "best_world_mae": float(errors.min()),
            "top100_world_mae": float(np.mean(np.sort(errors)[:100])),
            "p01_world_mae": float(np.quantile(errors, 0.01)),
            "p05_world_mae": float(np.quantile(errors, 0.05)),
            "median_world_mae": float(np.median(errors)),
            "best_world_p90_abs": float(np.quantile(np.abs(best_pred - actual), 0.90)),
            "best_world_spearman": float(pd.Series(best_pred).corr(pd.Series(actual), method="spearman")),
            "mean_row_vector_entropy": float(np.mean(-(dist * np.log(dist + 1.0e-30)).sum(axis=1))),
            "mean_max_vector_prob": float(np.mean(dist.max(axis=1))),
        }
        rec["config_score"] = (
            rec["top100_world_mae"]
            + 0.25 * rec["best_world_mae"]
            + 0.10 * rec["p01_world_mae"]
            - 0.00003 * rec["best_world_spearman"]
            - 0.00002 * min(cfg.beta, 1.0)
        )
        rows.append(rec)
        cache[str(rec["config_id"])] = (cfg, dist, choices, preds, errors)
    out = pd.DataFrame(rows).sort_values(["config_score", "top100_world_mae"]).reset_index(drop=True)
    out.to_csv(CONFIG_OUT, index=False)
    return out, cache


def posterior_specs() -> list[PosteriorSpec]:
    out: list[PosteriorSpec] = []
    for temp in [0.00008, 0.00012, 0.00018, 0.00025, 0.00035, 0.00055]:
        for power in [1.0, 1.5, 2.0]:
            out.append(PosteriorSpec(f"soft_t{temp:g}_p{power:g}", "soft", temp, 0, power))
    for k in [100, 250, 500, 1000, 2500, 5000]:
        for temp in [0.00012, 0.00025, 0.00050]:
            out.append(PosteriorSpec(f"top{k}_t{temp:g}", "topk", temp, k, 1.0))
        out.append(PosteriorSpec(f"elite{k}", "elite", 0.0, k, 1.0))
    return out


def posterior_weights(errors: np.ndarray, spec: PosteriorSpec) -> tuple[np.ndarray, float]:
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
    return weights, ess


def posterior_distribution(choices: np.ndarray, weights: np.ndarray) -> np.ndarray:
    n_rows = choices.shape[1]
    out = np.zeros((n_rows, 128), dtype=np.float64)
    for row_i in range(n_rows):
        out[row_i] = np.bincount(choices[:, row_i], weights=weights, minlength=128)
    out /= np.maximum(out.sum(axis=1, keepdims=True), 1.0e-30)
    return out


def evaluate_posteriors(
    configs: pd.DataFrame,
    cache: dict[str, tuple[VectorPriorConfig, np.ndarray, np.ndarray, np.ndarray, np.ndarray]],
    contrib: np.ndarray,
    actual: np.ndarray,
    q_prior: np.ndarray,
) -> tuple[pd.DataFrame, dict[str, np.ndarray], dict[str, np.ndarray]]:
    vecs = vector_table()
    rows: list[dict[str, Any]] = []
    dist_by_id: dict[str, np.ndarray] = {}
    q_by_id: dict[str, np.ndarray] = {}
    for rec in configs.head(8).to_dict("records"):
        config_id = str(rec["config_id"])
        cfg, prior_dist, choices, preds, errors = cache[config_id]
        for spec in posterior_specs():
            weights, ess = posterior_weights(errors, spec)
            post_dist = posterior_distribution(choices, weights)
            q_vec = clip_prob(post_dist @ vecs)
            pred = np.einsum("rv,frv->f", post_dist, contrib)
            err = pred - actual
            posterior_id = f"{config_id}_{spec.posterior_id}"
            row_vector_kl = float(np.mean(np.sum(post_dist * (np.log(post_dist + 1.0e-30) - np.log(prior_dist + 1.0e-30)), axis=1)))
            rec_out = {
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
                "q_abs_shift_vs_h018": float(np.mean(np.abs(q_vec - q_prior))),
                "q_max_abs_shift_vs_h018": float(np.max(np.abs(q_vec - q_prior))),
                "q_spearman_vs_h018": float(pd.Series(q_vec.reshape(-1)).corr(pd.Series(q_prior.reshape(-1)), method="spearman")),
                "mean_max_vector_posterior": float(np.mean(post_dist.max(axis=1))),
                "row_vector_kl_from_prior": row_vector_kl,
            }
            rec_out["posterior_score"] = (
                rec_out["posterior_mae"]
                + 0.25 * rec_out["posterior_p90_abs"]
                - 0.00004 * rec_out["posterior_spearman"]
                - 0.00002 * min(rec_out["q_abs_shift_vs_h018"], 0.05) / 0.05
                + 0.00004 * max(200.0 - ess, 0.0) / 200.0
            )
            rows.append(rec_out)
            dist_by_id[posterior_id] = post_dist
            q_by_id[posterior_id] = q_vec
    out = pd.DataFrame(rows).sort_values(["posterior_score", "posterior_mae"]).reset_index(drop=True)
    out.to_csv(POSTERIOR_OUT, index=False)
    return out, dist_by_id, q_by_id


def null_stress(
    configs: pd.DataFrame,
    cache: dict[str, tuple[VectorPriorConfig, np.ndarray, np.ndarray, np.ndarray, np.ndarray]],
    actual: np.ndarray,
    n_perm: int = 300,
) -> pd.DataFrame:
    best_config = str(configs.iloc[0]["config_id"])
    cfg, _, _, preds, errors = cache[best_config]
    real_best = int(np.argmin(errors))
    rows: list[dict[str, Any]] = [
        {
            "kind": "real",
            "iteration": -1,
            "config_id": best_config,
            "prior_kind": cfg.prior_kind,
            "beta": cfg.beta,
            "best_world_mae": float(errors.min()),
            "top100_world_mae": float(np.mean(np.sort(errors)[:100])),
            "p01_world_mae": float(np.quantile(errors, 0.01)),
            "median_world_mae": float(np.median(errors)),
            "best_world_p90_abs": float(np.quantile(np.abs(preds[real_best] - actual), 0.90)),
            "best_world_spearman": float(pd.Series(preds[real_best]).corr(pd.Series(actual), method="spearman")),
        }
    ]
    rng = np.random.default_rng(20260607)
    for i in range(n_perm):
        perm_actual = rng.permutation(actual)
        perm_errors = np.mean(np.abs(preds - perm_actual.reshape(1, -1)), axis=1)
        best = int(np.argmin(perm_errors))
        rows.append(
            {
                "kind": "permute_actual",
                "iteration": i,
                "config_id": best_config,
                "prior_kind": cfg.prior_kind,
                "beta": cfg.beta,
                "best_world_mae": float(perm_errors.min()),
                "top100_world_mae": float(np.mean(np.sort(perm_errors)[:100])),
                "p01_world_mae": float(np.quantile(perm_errors, 0.01)),
                "median_world_mae": float(np.median(perm_errors)),
                "best_world_p90_abs": float(np.quantile(np.abs(preds[best] - perm_actual), 0.90)),
                "best_world_spearman": float(pd.Series(preds[best]).corr(pd.Series(perm_actual), method="spearman")),
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
        ("best_world_mae", "lower"),
        ("top100_world_mae", "lower"),
        ("p01_world_mae", "lower"),
        ("median_world_mae", "lower"),
        ("best_world_p90_abs", "lower"),
        ("best_world_spearman", "higher"),
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


def build_state_tables(
    sample: pd.DataFrame,
    post_dist: np.ndarray,
    q_vec: np.ndarray,
    q_h018: np.ndarray,
    h012_prob: np.ndarray,
    row_weight: np.ndarray,
    posterior: pd.Series,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    vecs = vector_table()
    vector_labels = ["".join(str(int(v)) for v in row) for row in vecs]
    max_idx = post_dist.argmax(axis=1)
    row_entropy = -(post_dist * np.log(post_dist + 1.0e-30)).sum(axis=1)
    row_gain = (loss(h012_prob, q_vec) - loss(q_vec, q_vec)).mean(axis=1)
    row_shift = np.mean(np.abs(q_vec - q_h018), axis=1)
    rows: list[dict[str, Any]] = []
    cell_rows: list[dict[str, Any]] = []
    for row_i in range(len(sample)):
        rec = {
            "row": row_i,
            "subject_id": sample.iloc[row_i]["subject_id"],
            "sleep_date": sample.iloc[row_i]["sleep_date"],
            "lifelog_date": sample.iloc[row_i]["lifelog_date"],
            "row_weight": float(row_weight[row_i]),
            "max_vector_code": int(max_idx[row_i]),
            "max_vector": vector_labels[int(max_idx[row_i])],
            "max_vector_prob": float(post_dist[row_i, max_idx[row_i]]),
            "row_vector_entropy": float(row_entropy[row_i]),
            "row_gain_to_joint_vector": float(row_gain[row_i]),
            "row_abs_shift_vs_h018": float(row_shift[row_i]),
            "row_score": float(
                0.38 * rank01(row_weight)[row_i]
                + 0.30 * rank01(row_gain)[row_i]
                + 0.20 * rank01(row_shift)[row_i]
                + 0.12 * rank01(post_dist.max(axis=1))[row_i]
            ),
            "posterior_id": str(posterior["posterior_id"]),
        }
        rows.append(rec)
        for target_i, target in enumerate(TARGETS):
            cell_rows.append(
                {
                    "row": row_i,
                    "target": target,
                    "h012_prob": float(h012_prob[row_i, target_i]),
                    "h018_prob": float(q_h018[row_i, target_i]),
                    "q_joint_vector": float(q_vec[row_i, target_i]),
                    "joint_minus_h018": float(q_vec[row_i, target_i] - q_h018[row_i, target_i]),
                    "joint_minus_h012": float(q_vec[row_i, target_i] - h012_prob[row_i, target_i]),
                    "row_weight": float(row_weight[row_i]),
                    "row_score": rec["row_score"],
                    "cell_gain": float(loss(h012_prob[row_i, target_i], q_vec[row_i, target_i]) - loss(q_vec[row_i, target_i], q_vec[row_i, target_i])),
                }
            )
    row_df = pd.DataFrame(rows).sort_values("row_score", ascending=False).reset_index(drop=True)
    cell_df = pd.DataFrame(cell_rows)
    cell_df["abs_joint_logit_move"] = np.abs(logit(cell_df["q_joint_vector"].to_numpy()) - logit(cell_df["h012_prob"].to_numpy()))
    cell_df["abs_shift_vs_h018"] = np.abs(cell_df["joint_minus_h018"].to_numpy(dtype=np.float64))
    cell_df["gain_score"] = rank01(cell_df["cell_gain"].to_numpy(dtype=np.float64))
    cell_df["shift_score"] = rank01(cell_df["abs_shift_vs_h018"].to_numpy(dtype=np.float64))
    cell_df["move_score"] = rank01(cell_df["abs_joint_logit_move"].to_numpy(dtype=np.float64))
    cell_df["row_score_rank"] = rank01(cell_df["row_score"].to_numpy(dtype=np.float64))
    cell_df["combined_score"] = 0.40 * cell_df["gain_score"] + 0.24 * cell_df["shift_score"] + 0.20 * cell_df["move_score"] + 0.16 * cell_df["row_score_rank"]
    row_df.to_csv(ROW_OUT, index=False)
    cell_df.sort_values("combined_score", ascending=False).to_csv(CELL_OUT, index=False)
    return row_df, cell_df.sort_values("combined_score", ascending=False).reset_index(drop=True)


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
    for mode in ["combined", "gain", "shift", "move"]:
        for subset in ["all", "Q", "S"]:
            for k in [400, 700, 1000, 1300, 1600, 1750]:
                for alpha in [0.55, 0.75, 1.0, 1.25]:
                    out.append(CandidateSpec(f"{mode}_{subset}_k{k}_a{alpha:g}", mode, subset, k, alpha))
    for target in TARGETS:
        for mode in ["combined", "gain", "shift"]:
            for k in [60, 100, 160, 220, 250]:
                for alpha in [0.75, 1.0, 1.25]:
                    out.append(CandidateSpec(f"{mode}_{target}_k{k}_a{alpha:g}", mode, target, k, alpha))
    return out


def make_candidate_frame(h012: pd.DataFrame, q_vec: np.ndarray, cells: pd.DataFrame, spec: CandidateSpec) -> tuple[pd.DataFrame, np.ndarray]:
    base_prob = h012[TARGETS].to_numpy(dtype=np.float64)
    valid = target_mask(spec.target_subset, base_prob.shape)
    score_col = {
        "combined": "combined_score",
        "gain": "gain_score",
        "shift": "shift_score",
        "move": "move_score",
    }[spec.mode]
    scores = np.full(base_prob.size, -np.inf, dtype=np.float64)
    for rec in cells.to_dict("records"):
        idx = int(rec["row"]) * len(TARGETS) + TARGETS.index(str(rec["target"]))
        scores[idx] = float(rec[score_col])
        if abs(float(rec["q_joint_vector"]) - float(rec["h012_prob"])) <= 1.0e-12:
            valid[idx] = False
    candidates = np.flatnonzero(valid)
    chosen = candidates[np.argsort(scores[candidates])[-min(spec.k, len(candidates)) :]]
    mask = np.zeros(base_prob.size, dtype=bool)
    mask[chosen] = True
    mask = mask.reshape(base_prob.shape)
    z = logit(base_prob)
    moved = z.copy()
    moved[mask] = z[mask] + spec.alpha * (logit(q_vec)[mask] - z[mask])
    out = h012.copy()
    out[TARGETS] = clip_prob(sigmoid(moved))
    return out, mask


def score_candidate(prob: np.ndarray, base_prob: np.ndarray, q_vec: np.ndarray, row_weight: np.ndarray) -> dict[str, float]:
    row_diff = (loss(prob, q_vec) - loss(base_prob, q_vec)).mean(axis=1)
    return {
        "rowweighted_delta_vs_h012": float(row_diff @ row_weight),
        "uniform_delta_vs_h012": float(row_diff.mean()),
        "row_beats_rate": float(np.mean(row_diff < 0.0)),
        "row_p90_delta": float(np.quantile(row_diff, 0.90)),
    }


def generate_candidates(
    h012: pd.DataFrame,
    h018: pd.DataFrame,
    h019: pd.DataFrame,
    q_vec: np.ndarray,
    cells: pd.DataFrame,
    row_weight: np.ndarray,
) -> tuple[pd.DataFrame, Path | None]:
    base_prob = h012[TARGETS].to_numpy(dtype=np.float64)
    h018_prob = h018[TARGETS].to_numpy(dtype=np.float64)
    h019_prob = h019[TARGETS].to_numpy(dtype=np.float64)
    h018_score = score_candidate(h018_prob, base_prob, q_vec, row_weight)
    h019_score = score_candidate(h019_prob, base_prob, q_vec, row_weight)
    rows: list[dict[str, Any]] = []
    frames: list[tuple[pd.DataFrame, CandidateSpec, dict[str, Any]]] = []
    for spec in candidate_specs():
        out, mask = make_candidate_frame(h012, q_vec, cells, spec)
        prob = out[TARGETS].to_numpy(dtype=np.float64)
        rec = score_candidate(prob, base_prob, q_vec, row_weight)
        rec.update(
            {
                "candidate_id": spec.candidate_id,
                "mode": spec.mode,
                "target_subset": spec.target_subset,
                "k": spec.k,
                "alpha": spec.alpha,
                "changed_rows": int((np.abs(prob - base_prob).max(axis=1) > 1.0e-12).sum()),
                "changed_cells": int((np.abs(prob - base_prob) > 1.0e-12).sum()),
                "mean_abs_prob_delta_vs_h012": float(np.mean(np.abs(prob - base_prob))),
                "max_abs_prob_delta_vs_h012": float(np.max(np.abs(prob - base_prob))),
                "mean_abs_prob_delta_vs_h018": float(np.mean(np.abs(prob - h018_prob))),
                "max_abs_prob_delta_vs_h018": float(np.max(np.abs(prob - h018_prob))),
                "h018_rowweighted_delta_vs_h012": h018_score["rowweighted_delta_vs_h012"],
                "h019_rowweighted_delta_vs_h012": h019_score["rowweighted_delta_vs_h012"],
            }
        )
        rows.append(rec)
        frames.append((out, spec, rec))
    candidates = pd.DataFrame(rows)
    candidates["h020_decision"] = np.select(
        [
            (candidates["rowweighted_delta_vs_h012"] < -0.00062)
            & (candidates["max_abs_prob_delta_vs_h012"] <= 0.16)
            & (candidates["changed_cells"] >= 1200),
            (candidates["rowweighted_delta_vs_h012"] < -0.00048)
            & (candidates["max_abs_prob_delta_vs_h012"] <= 0.18),
        ],
        ["joint_vector_big_bet", "joint_vector_sensor"],
        default="diagnostic_only",
    )
    order = {"joint_vector_big_bet": 0, "joint_vector_sensor": 1, "diagnostic_only": 2}
    candidates["decision_rank"] = candidates["h020_decision"].map(order).astype(int)
    candidates = candidates.sort_values(
        ["decision_rank", "rowweighted_delta_vs_h012", "mean_abs_prob_delta_vs_h018"],
        ascending=[True, True, False],
    ).reset_index(drop=True)

    keep = set(candidates.head(60)["candidate_id"].astype(str))
    materialized: dict[str, str] = {}
    primary: Path | None = None
    for out, spec, _ in frames:
        if spec.candidate_id not in keep:
            continue
        path = H020 / f"submission_h020_{safe_id(spec.candidate_id)}_{short_hash(out)}.csv"
        out.to_csv(path, index=False)
        materialized[spec.candidate_id] = rel(path)
    candidates["file"] = candidates["candidate_id"].map(materialized).fillna("not_materialized")
    promoted = candidates[candidates["h020_decision"].isin(["joint_vector_big_bet", "joint_vector_sensor"])].head(1)
    if not promoted.empty:
        source = ROOT / str(promoted.iloc[0]["file"])
        primary = ROOT / f"submission_h020_joint_vector_world_{safe_id(str(promoted.iloc[0]['candidate_id']), 64)}_uploadsafe.csv"
        shutil.copyfile(source, primary)
    candidates.to_csv(CANDIDATE_OUT, index=False)
    return candidates, primary


def write_report(
    code_summary: pd.DataFrame,
    configs: pd.DataFrame,
    posteriors: pd.DataFrame,
    nulls: pd.DataFrame,
    row_state: pd.DataFrame,
    cells: pd.DataFrame,
    candidates: pd.DataFrame,
    primary: Path | None,
) -> None:
    lines: list[str] = []
    lines.append("# H020 Joint Target-Vector Hardworld HS-JEPA\n")
    lines.append("## Question\n")
    lines.append("Does the public-equation latent survive when each row must choose a valid 7-target label vector learned from train target co-occurrence?\n")
    lines.append("## Train Target-Vector Prior\n")
    lines.append(md_table(code_summary.head(20)))
    lines.append("\n## Vector-World Configs\n")
    lines.append(md_table(configs.head(24)))
    lines.append("\n## Vector Posteriors\n")
    lines.append(md_table(posteriors.head(24)))
    lines.append("\n## Null Stress\n")
    lines.append("Known public deltas are permuted while sampled joint-vector world predictions are kept fixed.\n")
    lines.append(md_table(null_summary(nulls)))
    lines.append("\n## Row State Summary\n")
    summary = pd.DataFrame(
        [
            {
                "rows": len(row_state),
                "mean_max_vector_prob": float(row_state["max_vector_prob"].mean()),
                "p90_max_vector_prob": float(row_state["max_vector_prob"].quantile(0.90)),
                "mean_row_entropy": float(row_state["row_vector_entropy"].mean()),
                "mean_row_abs_shift_vs_h018": float(row_state["row_abs_shift_vs_h018"].mean()),
                "top20_row_weight_mass": float(row_state.head(20)["row_weight"].sum()),
            }
        ]
    )
    lines.append(md_table(summary))
    lines.append("\n## Top Rows\n")
    lines.append(
        md_table(
            row_state[
                [
                    "row",
                    "subject_id",
                    "sleep_date",
                    "max_vector",
                    "max_vector_prob",
                    "row_gain_to_joint_vector",
                    "row_abs_shift_vs_h018",
                    "row_score",
                ]
            ].head(30)
        )
    )
    lines.append("\n## Top Cells\n")
    lines.append(md_table(cells.head(30)))
    lines.append("\n## Candidate Selection\n")
    lines.append(md_table(candidates.head(40)))
    lines.append("\n## Decision\n")
    if primary is None:
        lines.append("- No upload-safe candidate promoted; H020 remains diagnostic.\n")
    else:
        lines.append(f"- Primary upload-safe candidate: `{primary.name}`.\n")
        lines.append("- Interpretation: this file bets that H018 should be projected onto a train-informed joint target-vector posterior.\n")
    lines.append("\n## Files\n")
    for p in [CONFIG_OUT, POSTERIOR_OUT, NULL_OUT, ROW_OUT, CELL_OUT, CANDIDATE_OUT]:
        lines.append(f"- `{rel(p)}`\n")
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    known, sample, h012, h018, h019, pred_by_file = load_frames()
    h012_prob = h012[TARGETS].to_numpy(dtype=np.float64)
    h018_prob = h018[TARGETS].to_numpy(dtype=np.float64)
    q_h018 = pivot_cell(H020.parent / "h018_hard_label_world_jepa" / "h018_cell_hard_posterior.csv", "q_hard", sample)
    row_weight = row_weight_vector()
    global_prior, subject_priors, code_summary = build_vector_priors(sample)
    _, contrib, actual = contribution_tensor(known, pred_by_file, h012_prob, row_weight)

    configs, cache = evaluate_configs(sample, q_h018, global_prior, subject_priors, contrib, actual)
    posteriors, dist_by_id, q_by_id = evaluate_posteriors(configs, cache, contrib, actual, q_h018)
    nulls = null_stress(configs, cache, actual)
    selected = posteriors.iloc[0]
    post_dist = dist_by_id[str(selected["posterior_id"])]
    q_vec = q_by_id[str(selected["posterior_id"])]
    row_state, cells = build_state_tables(sample, post_dist, q_vec, q_h018, h012_prob, row_weight, selected)
    candidates, primary = generate_candidates(h012, h018, h019, q_vec, cells, row_weight)
    write_report(code_summary, configs, posteriors, nulls, row_state, cells, candidates, primary)

    print(f"Wrote {REPORT_OUT}")
    if primary is not None:
        print(f"Primary: {primary}")
    else:
        print("Primary: none")
    print(configs.head(10).to_string(index=False))
    print(posteriors.head(10).to_string(index=False))
    print(candidates.head(12).to_string(index=False))


if __name__ == "__main__":
    main()
