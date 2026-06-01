#!/usr/bin/env python3
"""H021: human-state conditional target-vector prior HS-JEPA.

Question
--------
Can observed human-state context predict the hidden 7-target label vector well
enough to regularize the H012/H020 public-equation posterior?

This is a bigger claim than another blend. The context is human lifelog state
(calendar, app usage, activity, HR, mobility, sensor quality). The target is
the row-level 7-bit Q/S state vector. The action is accepted only where this
human-state vector prior agrees with the public-equation posterior more than a
row-permuted null prior would.
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
OUT = ROOT / "hitl" / "h021_human_state_vector_prior_jepa"
DATA = ROOT / "data"
ANALYSIS = ROOT / "analysis_outputs"
OUT.mkdir(parents=True, exist_ok=True)

if str(ANALYSIS) not in sys.path:
    sys.path.insert(0, str(ANALYSIS))

from public_anchor_bottleneck_decomposition import KEYS, TARGETS, load_sub, logit  # noqa: E402


EPS = 1.0e-6
H012 = "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"
H020 = "submission_h020_joint_vector_world_combined_all_k1750_a1_uploadsafe.csv"
FEATURES_IN = ROOT / "hitl" / "h013_raw_human_state_jepa_gate" / "h013_human_state_features.csv"
H020_CELL_IN = ROOT / "hitl" / "h020_joint_vector_world_jepa" / "h020_cell_joint_vector_posterior.csv"
H020_ROW_IN = ROOT / "hitl" / "h020_joint_vector_world_jepa" / "h020_row_vector_state.csv"

CONFIG_OUT = OUT / "h021_vector_prior_configs.csv"
ROW_OUT = OUT / "h021_test_human_state_vector_prior_rows.csv"
CELL_OUT = OUT / "h021_test_human_state_vector_prior_cells.csv"
CANDIDATE_OUT = OUT / "h021_candidates.csv"
NULL_OUT = OUT / "h021_hs_null_stress.csv"
REPORT_OUT = OUT / "h021_report.md"


@dataclass(frozen=True)
class PriorConfig:
    config_id: str
    group: str
    scope: str
    k: int
    date_decay: float
    alpha: float
    subject_boost: float = 1.0


@dataclass(frozen=True)
class CandidateSpec:
    candidate_id: str
    mode: str
    k: int
    alpha: float
    hs_mix: float


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(x, dtype=np.float64)))


def loss(prob: np.ndarray, y_prob: np.ndarray) -> np.ndarray:
    p = clip_prob(prob)
    q = clip_prob(y_prob)
    return -(q * np.log(p) + (1.0 - q) * np.log(1.0 - p))


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


def rel(path: Path | None) -> str:
    if path is None:
        return "none"
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def safe_id(text: str, limit: int = 96) -> str:
    clean = re.sub(r"[^A-Za-z0-9_.-]+", "_", text).strip("_")
    return clean[:limit].strip("_")


def short_hash(frame: pd.DataFrame) -> str:
    arr = np.asarray(frame[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def rank01(x: np.ndarray) -> np.ndarray:
    s = pd.Series(np.asarray(x, dtype=np.float64))
    return s.rank(method="average", pct=True).to_numpy(dtype=np.float64)


def vector_table() -> np.ndarray:
    return np.asarray([[int(b) for b in format(i, "07b")] for i in range(128)], dtype=np.float64)


def code_from_labels(y: np.ndarray) -> np.ndarray:
    weights = np.asarray([64, 32, 16, 8, 4, 2, 1], dtype=np.int64)
    return (y.astype(np.int64) * weights.reshape(1, -1)).sum(axis=1)


def feature_groups(features: pd.DataFrame) -> dict[str, list[str]]:
    ignore = set(KEYS + ["split", "date"] + TARGETS)
    numeric = [c for c in features.columns if c not in ignore and pd.api.types.is_numeric_dtype(features[c])]
    sleep_tokens = (
        "late",
        "early",
        "prebed",
        "screen",
        "charge",
        "light",
        "w_hr",
        "hr_",
        "usage_late",
        "usage_prebed",
        "usage_early",
        "m_activity_active_late",
        "m_activity_active_early",
    )
    quality_tokens = (
        "count",
        "obs",
        "rows",
        "events",
        "points",
        "list_len",
        "wifi_",
        "ble_",
        "ambience_",
    )
    calendar_tokens = (
        "weekday",
        "weekend",
        "day_of_month",
        "month",
        "payday",
        "subject_day_idx",
        "pre_weekend",
        "post_weekend",
        "month_start",
        "month_end",
    )
    social_tokens = (
        "usage_cat_call",
        "usage_cat_chat",
        "usage_cat_religion",
        "usage_cat_work",
        "usage_cat_finance",
        "usage_cat_game",
        "usage_cat_media",
        "usage_cat_shopping_food",
        "usage_cat_search_news",
        "usage_day_",
        "usage_evening_",
        "usage_late_",
        "usage_prebed_",
    )
    body_tokens = ("pedo_", "m_activity", "w_hr", "gps_")

    sleep_cols = [c for c in numeric if any(tok in c for tok in sleep_tokens)]
    quality_cols = [c for c in numeric if any(tok in c for tok in quality_tokens)]
    calendar_cols = [c for c in numeric if any(tok in c for tok in calendar_tokens)]
    social_cols = [c for c in numeric if any(tok in c for tok in social_tokens)]
    body_cols = [c for c in numeric if any(tok in c for tok in body_tokens)]
    state_cols = sorted(set(sleep_cols + quality_cols + social_cols + body_cols))
    return {
        "all": numeric,
        "state": state_cols,
        "sleep": sleep_cols,
        "quality": quality_cols,
        "social_sleep": sorted(set(social_cols + sleep_cols + calendar_cols)),
        "calendar_body": sorted(set(calendar_cols + body_cols)),
    }


def standardized_matrix(features: pd.DataFrame, cols: list[str], train_mask: np.ndarray) -> np.ndarray:
    if not cols:
        return np.zeros((len(features), 1), dtype=np.float64)
    x = features[cols].to_numpy(dtype=np.float64)
    x = np.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0)
    lo = np.nanpercentile(x[train_mask], 0.5, axis=0)
    hi = np.nanpercentile(x[train_mask], 99.5, axis=0)
    x = np.minimum(np.maximum(x, lo), hi)
    mu = x[train_mask].mean(axis=0)
    sigma = x[train_mask].std(axis=0)
    sigma = np.where(sigma < 1.0e-9, 1.0, sigma)
    z = (x - mu) / sigma
    return np.nan_to_num(z, nan=0.0, posinf=0.0, neginf=0.0)


def make_distribution(
    codes: np.ndarray,
    idx: np.ndarray,
    weights: np.ndarray,
    global_vec_prior: np.ndarray,
    alpha: float,
) -> np.ndarray:
    if len(idx) == 0 or float(np.sum(weights)) <= 1.0e-12:
        return global_vec_prior.copy()
    counts = np.bincount(codes[idx], weights=weights, minlength=128).astype(np.float64)
    counts = counts + alpha * global_vec_prior * max(float(np.sum(weights)), 1.0)
    total = float(counts.sum())
    if total <= 1.0e-12:
        return global_vec_prior.copy()
    return counts / total


def knn_vector_prior(
    z_train: np.ndarray,
    z_query: np.ndarray,
    train_subject: np.ndarray,
    query_subject: np.ndarray,
    train_dates: np.ndarray,
    query_dates: np.ndarray,
    codes: np.ndarray,
    global_vec_prior: np.ndarray,
    cfg: PriorConfig,
    self_exclude: bool,
) -> tuple[np.ndarray, pd.DataFrame]:
    n_query = len(z_query)
    dist_out = np.zeros((n_query, 128), dtype=np.float64)
    rows: list[dict[str, Any]] = []

    for i in range(n_query):
        d = np.mean((z_train - z_query[i]) ** 2, axis=1)
        valid = np.ones(len(z_train), dtype=bool)
        if self_exclude and len(z_train) == n_query:
            valid[i] = False
        same = train_subject == query_subject[i]
        if cfg.scope == "subject":
            valid &= same
        elif cfg.scope == "subject_past":
            valid &= same
            valid &= train_dates < query_dates[i]
            if not np.any(valid):
                valid = same.copy()
                if self_exclude and len(z_train) == n_query:
                    valid[i] = False
        elif cfg.scope == "hybrid":
            pass
        elif cfg.scope == "global":
            pass
        else:
            raise ValueError(cfg.scope)
        idx = np.flatnonzero(valid)
        if len(idx) == 0:
            dist_out[i] = global_vec_prior
            rows.append({"neighbor_count": 0, "same_subject_share": 0.0, "ess": 0.0, "min_dist": np.nan})
            continue
        take = min(cfg.k, len(idx))
        local_order = np.argsort(d[idx])[:take]
        nn = idx[local_order]
        nn_d = d[nn]
        scale = float(np.median(nn_d) + 1.0e-9)
        weights = np.exp(-nn_d / scale)
        if cfg.scope == "hybrid" and cfg.subject_boost > 1.0:
            weights *= np.where(train_subject[nn] == query_subject[i], cfg.subject_boost, 1.0)
        if cfg.date_decay > 0:
            days = np.abs((train_dates[nn] - query_dates[i]).astype("timedelta64[D]").astype(np.float64))
            weights *= np.exp(-days / cfg.date_decay)
        if float(weights.sum()) <= 1.0e-12:
            weights = np.ones_like(weights)
        dist_out[i] = make_distribution(codes, nn, weights, global_vec_prior, cfg.alpha)
        wsum = float(weights.sum())
        ess = float(wsum * wsum / (float(np.sum(weights * weights)) + 1.0e-12))
        rows.append(
            {
                "neighbor_count": int(len(nn)),
                "same_subject_share": float(np.mean(train_subject[nn] == query_subject[i])),
                "ess": ess,
                "min_dist": float(np.min(nn_d)),
            }
        )
    return dist_out, pd.DataFrame(rows)


def evaluate_prior(dist: np.ndarray, codes: np.ndarray, y: np.ndarray) -> dict[str, float]:
    vecs = vector_table()
    q = clip_prob(dist @ vecs)
    vec_nll = -np.log(np.clip(dist[np.arange(len(codes)), codes], EPS, 1.0))
    return {
        "marginal_bce": float(loss(q, y).mean()),
        "vector_nll": float(vec_nll.mean()),
        "vector_top1_acc": float(np.mean(np.argmax(dist, axis=1) == codes)),
        "mean_entropy": float((-dist * np.log(dist + 1.0e-30)).sum(axis=1).mean()),
        "mean_top_prob": float(dist.max(axis=1).mean()),
    }


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    train = train.sort_values(KEYS).reset_index(drop=True)
    sample = sample.sort_values(KEYS).reset_index(drop=True)
    features = pd.read_csv(FEATURES_IN, parse_dates=["sleep_date", "lifelog_date", "date"])
    features = features.sort_values(KEYS).reset_index(drop=True)
    feat_train = features.loc[features["split"].astype(str).eq("train")].reset_index(drop=True)
    feat_test = features.loc[features["split"].astype(str).eq("test")].reset_index(drop=True)
    if not feat_train[KEYS].equals(train[KEYS]):
        raise ValueError("H013 train features do not align with train labels")
    if not feat_test[KEYS].equals(sample[KEYS]):
        raise ValueError("H013 test features do not align with sample")
    h012 = load_sub(H012, sample[KEYS])
    h020 = load_sub(H020, sample[KEYS])
    return train, sample, features, h012, h020, feat_test


def build_h020_cell_matrix(sample: pd.DataFrame) -> tuple[np.ndarray, pd.DataFrame]:
    cells = pd.read_csv(H020_CELL_IN)
    q = np.zeros((len(sample), len(TARGETS)), dtype=np.float64)
    score = np.zeros_like(q)
    gain = np.zeros_like(q)
    for rec in cells.to_dict("records"):
        r = int(rec["row"])
        t = TARGETS.index(str(rec["target"]))
        q[r, t] = float(rec["q_joint_vector"])
        score[r, t] = float(rec["combined_score"])
        gain[r, t] = float(rec["cell_gain"])
    if np.any(q <= 0):
        raise ValueError("H020 cell posterior is incomplete")
    cell_frame = pd.DataFrame(
        {
            "row": np.repeat(np.arange(len(sample)), len(TARGETS)),
            "target": TARGETS * len(sample),
            "h020_score": score.reshape(-1),
            "h020_gain": gain.reshape(-1),
        }
    )
    return clip_prob(q), cell_frame


def validate_submission(path: Path, sample: pd.DataFrame) -> dict[str, Any]:
    df = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"])
    if list(df.columns) != KEYS + TARGETS:
        raise ValueError(f"bad columns in {path}")
    if len(df) != len(sample):
        raise ValueError(f"bad row count in {path}")
    if not df[KEYS].equals(sample[KEYS]):
        raise ValueError(f"key mismatch in {path}")
    arr = df[TARGETS].to_numpy(dtype=np.float64)
    if not np.isfinite(arr).all():
        raise ValueError(f"non-finite probabilities in {path}")
    if arr.min() < EPS or arr.max() > 1.0 - EPS:
        raise ValueError(f"probability bounds failed in {path}")
    if int(df.duplicated(KEYS).sum()) != 0:
        raise ValueError(f"duplicate keys in {path}")
    return {
        "path": str(path),
        "shape": tuple(df.shape),
        "min_prob": float(arr.min()),
        "max_prob": float(arr.max()),
        "duplicate_keys": int(df.duplicated(KEYS).sum()),
    }


def candidate_matrix(
    spec: CandidateSpec,
    h012: np.ndarray,
    h020: np.ndarray,
    q_hs: np.ndarray,
    cell_score: np.ndarray,
    agree: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    z012 = logit(h012)
    z020 = logit(h020)
    zhs = logit(q_hs)
    selected = np.zeros_like(h012, dtype=bool)

    if spec.mode == "agree_h020":
        score = np.where(agree, cell_score, -1.0)
        flat = np.argsort(score.reshape(-1))[::-1][: spec.k]
        rr, cc = np.unravel_index(flat, selected.shape)
        selected[rr, cc] = True
        z = z012.copy()
        z[selected] = z012[selected] + spec.alpha * (z020[selected] - z012[selected])
    elif spec.mode == "agree_joint_hs":
        score = np.where(agree, cell_score, -1.0)
        flat = np.argsort(score.reshape(-1))[::-1][: spec.k]
        rr, cc = np.unravel_index(flat, selected.shape)
        selected[rr, cc] = True
        target = (1.0 - spec.hs_mix) * z020 + spec.hs_mix * zhs
        z = z012.copy()
        z[selected] = z012[selected] + spec.alpha * (target[selected] - z012[selected])
    elif spec.mode == "hs_regularize_all":
        selected[:, :] = True
        target = (1.0 - spec.hs_mix) * z020 + spec.hs_mix * zhs
        z = z012 + spec.alpha * (target - z012)
    elif spec.mode == "conflict_hs_override":
        score = np.where(~agree, cell_score, -1.0)
        flat = np.argsort(score.reshape(-1))[::-1][: spec.k]
        rr, cc = np.unravel_index(flat, selected.shape)
        selected[rr, cc] = True
        z = z020.copy()
        z[selected] = (1.0 - spec.alpha) * z020[selected] + spec.alpha * zhs[selected]
    else:
        raise ValueError(spec.mode)
    return clip_prob(sigmoid(z)), selected


def weighted_mean(arr: np.ndarray, row_weight: np.ndarray) -> float:
    w = row_weight.reshape(-1, 1) / float(len(TARGETS))
    return float(np.sum(arr * w))


def main() -> None:
    rng = np.random.default_rng(20260602)
    for old_candidate in OUT.glob("submission_h021_*.csv"):
        old_candidate.unlink()
    train, sample, features, h012_df, h020_df, _ = load_inputs()
    train_mask = features["split"].astype(str).eq("train").to_numpy()
    test_mask = features["split"].astype(str).eq("test").to_numpy()
    y_train = train[TARGETS].to_numpy(dtype=np.float64)
    codes = code_from_labels(y_train)
    vecs = vector_table()
    global_counts = np.bincount(codes, minlength=128).astype(np.float64) + 0.5
    global_vec_prior = global_counts / float(global_counts.sum())
    global_q = clip_prob(global_vec_prior @ vecs)

    groups = feature_groups(features)
    cfgs = [
        PriorConfig("global_state_k32", "state", "global", 32, 0.0, 0.50),
        PriorConfig("global_all_k32", "all", "global", 32, 0.0, 0.50),
        PriorConfig("global_social_sleep_k32", "social_sleep", "global", 32, 0.0, 0.50),
        PriorConfig("subject_state_k10", "state", "subject", 10, 0.0, 0.75),
        PriorConfig("subject_past_state_k10_d28", "state", "subject_past", 10, 28.0, 0.75),
        PriorConfig("subject_all_k10", "all", "subject", 10, 0.0, 0.75),
        PriorConfig("hybrid_state_k36_boost4", "state", "hybrid", 36, 45.0, 0.50, 4.0),
        PriorConfig("hybrid_social_sleep_k36_boost4", "social_sleep", "hybrid", 36, 45.0, 0.50, 4.0),
        PriorConfig("quality_global_k32", "quality", "global", 32, 0.0, 0.50),
        PriorConfig("calendar_body_global_k32", "calendar_body", "global", 32, 0.0, 0.50),
    ]

    train_subject = train["subject_id"].astype(str).to_numpy()
    test_subject = sample["subject_id"].astype(str).to_numpy()
    train_dates = train["lifelog_date"].to_numpy(dtype="datetime64[D]")
    test_dates = sample["lifelog_date"].to_numpy(dtype="datetime64[D]")
    baseline_global = {
        "marginal_bce": float(loss(np.tile(global_q.reshape(1, -1), (len(train), 1)), y_train).mean()),
        "vector_nll": float((-np.log(np.clip(global_vec_prior[codes], EPS, 1.0))).mean()),
    }

    config_rows: list[dict[str, Any]] = []
    train_dists: dict[str, np.ndarray] = {}
    test_dists: dict[str, np.ndarray] = {}
    test_nn_rows: dict[str, pd.DataFrame] = {}
    for cfg in cfgs:
        cols = groups[cfg.group]
        z = standardized_matrix(features, cols, train_mask)
        z_train = z[train_mask]
        z_test = z[test_mask]
        dist_train, nn_train = knn_vector_prior(
            z_train,
            z_train,
            train_subject,
            train_subject,
            train_dates,
            train_dates,
            codes,
            global_vec_prior,
            cfg,
            self_exclude=True,
        )
        metrics = evaluate_prior(dist_train, codes, y_train)
        dist_test, nn_test = knn_vector_prior(
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
        train_dists[cfg.config_id] = dist_train
        test_dists[cfg.config_id] = dist_test
        test_nn_rows[cfg.config_id] = nn_test
        row = {
            "config_id": cfg.config_id,
            "group": cfg.group,
            "scope": cfg.scope,
            "k": cfg.k,
            "date_decay": cfg.date_decay,
            "alpha": cfg.alpha,
            "subject_boost": cfg.subject_boost,
            "n_cols": len(cols),
            "marginal_bce": metrics["marginal_bce"],
            "delta_marginal_bce_vs_global": metrics["marginal_bce"] - baseline_global["marginal_bce"],
            "vector_nll": metrics["vector_nll"],
            "delta_vector_nll_vs_global": metrics["vector_nll"] - baseline_global["vector_nll"],
            "vector_top1_acc": metrics["vector_top1_acc"],
            "mean_entropy": metrics["mean_entropy"],
            "mean_top_prob": metrics["mean_top_prob"],
            "mean_train_neighbor_ess": float(nn_train["ess"].mean()),
            "mean_test_neighbor_ess": float(nn_test["ess"].mean()),
            "mean_test_same_subject_share": float(nn_test["same_subject_share"].mean()),
        }
        row["config_score"] = (
            row["delta_marginal_bce_vs_global"]
            + 0.06 * row["delta_vector_nll_vs_global"]
            - 0.003 * row["vector_top1_acc"]
        )
        config_rows.append(row)

    config_df = pd.DataFrame(config_rows).sort_values("config_score").reset_index(drop=True)
    config_df.to_csv(CONFIG_OUT, index=False)
    top_cfgs = config_df.head(4)["config_id"].tolist()
    score = config_df.set_index("config_id").loc[top_cfgs, "config_score"].to_numpy(dtype=np.float64)
    weights = np.exp(-(score - score.min()) / max(float(np.std(score)), 1.0e-6))
    weights = weights / weights.sum()
    dist_test_ens = sum(float(w) * test_dists[cid] for w, cid in zip(weights, top_cfgs))
    dist_test_ens = dist_test_ens / dist_test_ens.sum(axis=1, keepdims=True)
    q_hs = clip_prob(dist_test_ens @ vecs)
    entropy = (-dist_test_ens * np.log(dist_test_ens + 1.0e-30)).sum(axis=1)
    entropy_norm = entropy / np.log(128.0)
    top_prob = dist_test_ens.max(axis=1)
    row_conf = 0.55 * (1.0 - entropy_norm) + 0.45 * rank01(top_prob)
    row_conf = np.clip(row_conf, 0.0, 1.0)

    q_h020_cell, h020_cell_frame = build_h020_cell_matrix(sample)
    h012 = clip_prob(h012_df[TARGETS].to_numpy(dtype=np.float64))
    h020_root = clip_prob(h020_df[TARGETS].to_numpy(dtype=np.float64))
    if float(np.max(np.abs(h020_root - q_h020_cell))) > 1.0e-8:
        q_h020 = q_h020_cell
    else:
        q_h020 = h020_root

    h020_rows = pd.read_csv(H020_ROW_IN)
    h020_rows = h020_rows.sort_values("row").reset_index(drop=True)
    row_weight = h020_rows["row_weight"].to_numpy(dtype=np.float64)
    row_weight = row_weight / max(float(row_weight.sum()), 1.0e-30)

    hs_dir = logit(q_hs) - logit(h012)
    h020_dir = logit(q_h020) - logit(h012)
    agree = np.sign(hs_dir) == np.sign(h020_dir)
    agree &= np.abs(hs_dir) > 1.0e-9
    agree &= np.abs(h020_dir) > 1.0e-9
    cell_score = (
        0.45 * h020_cell_frame["h020_score"].to_numpy(dtype=np.float64).reshape(len(sample), len(TARGETS))
        + 0.25 * rank01(np.abs(hs_dir).reshape(-1)).reshape(len(sample), len(TARGETS))
        + 0.20 * row_conf.reshape(-1, 1)
        + 0.10 * rank01(np.abs(h020_dir).reshape(-1)).reshape(len(sample), len(TARGETS))
    )

    row_df = sample[KEYS].copy()
    row_df["hs_top_vector_code"] = np.argmax(dist_test_ens, axis=1)
    row_df["hs_top_vector"] = ["".join(str(int(v)) for v in vecs[i]) for i in np.argmax(dist_test_ens, axis=1)]
    row_df["hs_top_vector_prob"] = top_prob
    row_df["hs_vector_entropy"] = entropy
    row_df["hs_row_conf"] = row_conf
    row_df["hs_h020_agree_rate"] = agree.mean(axis=1)
    row_df["h020_row_score"] = h020_rows["row_score"].to_numpy(dtype=np.float64)
    row_df["h020_row_weight"] = row_weight
    row_df["ensemble_configs"] = ",".join(top_cfgs)
    row_df.to_csv(ROW_OUT, index=False)

    cell_df = h020_cell_frame.copy()
    cell_df["hs_prob"] = q_hs.reshape(-1)
    cell_df["h012_prob"] = h012.reshape(-1)
    cell_df["h020_prob"] = q_h020.reshape(-1)
    cell_df["hs_minus_h012"] = (q_hs - h012).reshape(-1)
    cell_df["h020_minus_h012"] = (q_h020 - h012).reshape(-1)
    cell_df["hs_h020_agree"] = agree.reshape(-1)
    cell_df["hs_cell_score"] = cell_score.reshape(-1)
    cell_df["hs_row_conf"] = np.repeat(row_conf, len(TARGETS))
    cell_df.to_csv(CELL_OUT, index=False)

    specs = [
        CandidateSpec("agree_h020_k900_a1", "agree_h020", 900, 1.0, 0.0),
        CandidateSpec("agree_h020_k1200_a1", "agree_h020", 1200, 1.0, 0.0),
        CandidateSpec("agree_joint_hs_k900_a1_m0.25", "agree_joint_hs", 900, 1.0, 0.25),
        CandidateSpec("agree_joint_hs_k1200_a1_m0.25", "agree_joint_hs", 1200, 1.0, 0.25),
        CandidateSpec("hs_regularize_all_a0.9_m0.18", "hs_regularize_all", 1750, 0.9, 0.18),
        CandidateSpec("hs_regularize_all_a1_m0.25", "hs_regularize_all", 1750, 1.0, 0.25),
        CandidateSpec("conflict_hs_override_k280_a0.35", "conflict_hs_override", 280, 0.35, 1.0),
    ]

    candidate_rows: list[dict[str, Any]] = []
    submissions: dict[str, Path] = {}
    q_targets = {"h020": q_h020, "hs": q_hs}
    base_losses = {name: weighted_mean(loss(h012, q), row_weight) for name, q in q_targets.items()}
    h020_full_delta = weighted_mean(loss(q_h020, q_h020), row_weight) - base_losses["h020"]

    for spec in specs:
        cand, selected = candidate_matrix(spec, h012, q_h020, q_hs, cell_score, agree)
        out_df = sample[KEYS].copy()
        out_df[TARGETS] = cand
        h = short_hash(out_df)
        file_name = f"submission_h021_{safe_id(spec.candidate_id)}_{h}.csv"
        path = OUT / file_name
        out_df.to_csv(path, index=False)
        submissions[spec.candidate_id] = path
        row = {
            "candidate_id": spec.candidate_id,
            "mode": spec.mode,
            "k": spec.k,
            "alpha": spec.alpha,
            "hs_mix": spec.hs_mix,
            "file": rel(path),
            "changed_cells": int(np.sum(np.abs(cand - h012) > 1.0e-12)),
            "changed_rows": int(np.sum(np.any(np.abs(cand - h012) > 1.0e-12, axis=1))),
            "mean_abs_delta_vs_h012": float(np.mean(np.abs(cand - h012))),
            "max_abs_delta_vs_h012": float(np.max(np.abs(cand - h012))),
            "agree_rate_changed": float(np.mean(agree[selected])) if np.any(selected) else float(np.mean(agree)),
            "h020_delta_vs_h012": weighted_mean(loss(cand, q_h020), row_weight) - base_losses["h020"],
            "hs_delta_vs_h012": weighted_mean(loss(cand, q_hs), row_weight) - base_losses["hs"],
            "h020_gain_retained": float(
                (weighted_mean(loss(cand, q_h020), row_weight) - base_losses["h020"]) / (h020_full_delta + 1.0e-12)
            ),
        }
        row["survival_score"] = (
            -row["h020_delta_vs_h012"]
            -0.55 * row["hs_delta_vs_h012"]
            +0.00040 * row["agree_rate_changed"]
            -0.00020 * (row["mean_abs_delta_vs_h012"] > 0.08)
        )
        candidate_rows.append(row)

    candidate_df = pd.DataFrame(candidate_rows)

    null_rows: list[dict[str, Any]] = []
    qhs_flat = q_hs.copy()
    for spec in specs:
        real = candidate_df.loc[candidate_df["candidate_id"].eq(spec.candidate_id)].iloc[0]
        real_hs_delta = float(real["hs_delta_vs_h012"])
        null_deltas: list[float] = []
        null_agree_rates: list[float] = []
        for _ in range(250):
            perm = rng.permutation(len(sample))
            q_perm = qhs_flat[perm]
            hs_dir_perm = logit(q_perm) - logit(h012)
            agree_perm = np.sign(hs_dir_perm) == np.sign(h020_dir)
            agree_perm &= np.abs(hs_dir_perm) > 1.0e-9
            score_perm = (
                0.45 * h020_cell_frame["h020_score"].to_numpy(dtype=np.float64).reshape(len(sample), len(TARGETS))
                + 0.25 * rank01(np.abs(hs_dir_perm).reshape(-1)).reshape(len(sample), len(TARGETS))
                + 0.20 * row_conf[perm].reshape(-1, 1)
                + 0.10 * rank01(np.abs(h020_dir).reshape(-1)).reshape(len(sample), len(TARGETS))
            )
            cand_perm, selected_perm = candidate_matrix(spec, h012, q_h020, q_perm, score_perm, agree_perm)
            null_deltas.append(weighted_mean(loss(cand_perm, q_perm), row_weight) - weighted_mean(loss(h012, q_perm), row_weight))
            null_agree_rates.append(float(np.mean(agree_perm[selected_perm])) if np.any(selected_perm) else float(np.mean(agree_perm)))
        arr = np.asarray(null_deltas, dtype=np.float64)
        null_rows.append(
            {
                "candidate_id": spec.candidate_id,
                "real_hs_delta_vs_h012": real_hs_delta,
                "null_hs_delta_mean": float(arr.mean()),
                "null_hs_delta_p10": float(np.quantile(arr, 0.10)),
                "null_hs_delta_p50": float(np.quantile(arr, 0.50)),
                "null_hs_delta_p90": float(np.quantile(arr, 0.90)),
                "real_percentile_lower_is_better": float(np.mean(arr <= real_hs_delta)),
                "real_agree_rate_changed": float(real["agree_rate_changed"]),
                "null_agree_rate_mean": float(np.mean(null_agree_rates)),
            }
        )
    null_df = pd.DataFrame(null_rows)
    candidate_df = candidate_df.merge(null_df, on="candidate_id", how="left")
    candidate_df["null_hs_advantage"] = candidate_df["null_hs_delta_p50"] - candidate_df["real_hs_delta_vs_h012"]
    candidate_df["public_equation_survives"] = candidate_df["h020_delta_vs_h012"] < 0.0
    candidate_df["human_state_beats_null"] = candidate_df["null_hs_advantage"] > 0.0
    candidate_df["action_decision"] = np.where(
        candidate_df["public_equation_survives"] & candidate_df["human_state_beats_null"],
        "primary_hs_action",
        np.where(candidate_df["public_equation_survives"], "public_only_action", "diagnostic_only"),
    )
    candidate_df["survival_score"] = (
        -candidate_df["h020_delta_vs_h012"]
        +0.60 * np.maximum(candidate_df["null_hs_advantage"], 0.0)
        +0.00025 * candidate_df["agree_rate_changed"]
        -0.00400 * (candidate_df["h020_delta_vs_h012"] > 0.0).astype(float)
        -0.00200 * (candidate_df["changed_cells"] == 1750).astype(float)
    )
    candidate_df = candidate_df.sort_values("survival_score", ascending=False).reset_index(drop=True)
    candidate_df.to_csv(CANDIDATE_OUT, index=False)
    null_df.to_csv(NULL_OUT, index=False)

    primary_pool = candidate_df.loc[candidate_df["action_decision"].eq("primary_hs_action")]
    selected = (primary_pool if not primary_pool.empty else candidate_df).iloc[0]
    selected_path = ROOT / str(selected["file"])
    upload_name = f"{selected_path.stem}_uploadsafe.csv"
    upload_path = ROOT / upload_name
    for old_upload in ROOT.glob("submission_h021_*_uploadsafe.csv"):
        if old_upload != upload_path:
            old_upload.unlink()
    shutil.copyfile(selected_path, upload_path)
    validation = validate_submission(upload_path, sample)

    top_vector_counts = pd.Series(row_df["hs_top_vector"]).value_counts().head(12).reset_index()
    top_vector_counts.columns = ["hs_top_vector", "count"]
    q_hs_mean = pd.DataFrame({"target": TARGETS, "h012_mean": h012.mean(axis=0), "h020_mean": q_h020.mean(axis=0), "hs_mean": q_hs.mean(axis=0)})
    lines = [
        "# H021 Human-State Conditional Vector-Prior HS-JEPA",
        "",
        "## Question",
        "",
        "Can raw human-state context predict the hidden row-level 7-target vector and use that as a non-public regularizer for the H020 public-equation posterior?",
        "",
        "## Train Public-Free Prior Validation",
        "",
        f"Global vector prior baseline marginal BCE: `{baseline_global['marginal_bce']:.9f}`",
        f"Global vector prior baseline vector NLL: `{baseline_global['vector_nll']:.9f}`",
        "",
        md_table(config_df, 16),
        "",
        "## Selected Human-State Prior Ensemble",
        "",
        f"Top configs: `{', '.join(top_cfgs)}`",
        f"Weights: `{', '.join(f'{w:.3f}' for w in weights)}`",
        "",
        "## Test Row Human-State State",
        "",
        md_table(row_df.sort_values('hs_row_conf', ascending=False).head(20), 20),
        "",
        "## Top Human-State Vectors",
        "",
        md_table(top_vector_counts, 12),
        "",
        "## Mean Prior Shift",
        "",
        md_table(q_hs_mean, 7),
        "",
        "## Candidate Ranking",
        "",
        md_table(candidate_df, 12),
        "",
        "## Null Stress",
        "",
        "The human-state prior rows are permuted across test rows. A real candidate should align with the unpermuted human-state vector prior better than this null.",
        "",
        md_table(null_df, 12),
        "",
        "## Decision",
        "",
        f"Selected upload-safe candidate: `{upload_name}`",
        f"Validation: `{validation}`",
        "",
        "A public win would support the HS-JEPA claim that observed lifestyle context predicts a row-level Q/S hidden vector that can safely steer public-equation posterior actions.",
        "A public loss means the human-state vector prior is locally learnable but not yet calibrated enough to translate into leaderboard action.",
        "",
        "## Files",
        "",
        f"- `{rel(CONFIG_OUT)}`",
        f"- `{rel(ROW_OUT)}`",
        f"- `{rel(CELL_OUT)}`",
        f"- `{rel(CANDIDATE_OUT)}`",
        f"- `{rel(NULL_OUT)}`",
        f"- `{rel(REPORT_OUT)}`",
        f"- `{upload_name}`",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n")

    print(f"wrote {REPORT_OUT}")
    print(f"selected {upload_path}")
    print(candidate_df.head(8).to_string(index=False))


if __name__ == "__main__":
    main()
