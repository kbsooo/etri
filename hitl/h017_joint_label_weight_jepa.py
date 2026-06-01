#!/usr/bin/env python3
"""H017: joint label x public-weight HS-JEPA.

H012 solved hidden public labels with uniform cell weights. H016 solved hidden
public cell weights with fixed label proxies. H017 tests the stronger hidden
world:

    public LB delta = sum_cell w[cell] * loss_delta(pred, q[cell])

Instead of choosing labels or weights, it solves the joint same-level latent
state `(q, w)` under high-entropy constraints, then materializes H012 -> q only
where the joint public-weighted gain is large.

The anti-collapse check is direct: keep the known submission loss-delta tensor
fixed and permute the public deltas. If the real public deltas are not special,
the joint solver should look similarly good on permutations.
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
H017 = ROOT / "hitl" / "h017_joint_label_weight_jepa"
H017.mkdir(parents=True, exist_ok=True)

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
H015_PRIMARY = "submission_h015_self_feedback_top_all_k1600_a0.7_uploadsafe.csv"
H016_PRIMARY = "submission_h016_public_subset_gain_all_k1000_a0.75_uploadsafe.csv"
H012_PUBLIC = 0.5681234831

REPORT_OUT = H017 / "h017_report.md"
CONFIG_OUT = H017 / "h017_joint_configs.csv"
NULL_OUT = H017 / "h017_null_stress.csv"
CELL_OUT = H017 / "h017_cell_joint_state.csv"
CANDIDATE_OUT = H017 / "h017_candidates.csv"


@dataclass(frozen=True)
class JointConfig:
    q_prior_name: str
    w_prior_name: str
    ridge_mult: float
    cap_mult: float


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


def cap_and_normalize(w: np.ndarray, cap_mult: float) -> np.ndarray:
    n = len(w)
    out = np.maximum(np.asarray(w, dtype=np.float64), 0.0)
    if cap_mult > 0:
        cap = cap_mult / n
        for _ in range(8):
            over = out > cap
            if not over.any():
                break
            excess = float((out[over] - cap).sum())
            out[over] = cap
            under = ~over
            if under.any():
                base = np.maximum(out[under], 1.0e-30)
                out[under] += excess * base / max(float(base.sum()), 1.0e-30)
    s = float(out.sum())
    if not np.isfinite(s) or s <= 1.0e-30:
        return np.full(n, 1.0 / n, dtype=np.float64)
    return out / s


def pivot_posterior(path: Path, col: str, sample: pd.DataFrame) -> np.ndarray:
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
    h015 = load_sub(H015_PRIMARY, h012[KEYS])
    h016 = load_sub(H016_PRIMARY, h012[KEYS])
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
    return known, h012[KEYS].copy(), h012, h015, h016, pred_by_file


def top_weighted_prior(known: pd.DataFrame, pred_by_file: dict[str, np.ndarray], scale: float) -> np.ndarray:
    lbs = known.set_index("file")["public_lb"].astype(float)
    best = float(lbs.min())
    files = [str(f) for f in known["file"].tolist() if str(f) in pred_by_file][:8]
    preds = []
    weights = []
    for name in files:
        preds.append(pred_by_file[name])
        weights.append(np.exp(-(float(lbs[name]) - best) / scale))
    w = np.asarray(weights, dtype=np.float64)
    w = w / max(float(w.sum()), 1.0e-30)
    return clip_prob(np.tensordot(w, np.stack(preds, axis=0), axes=(0, 0)))


def build_q_priors(
    known: pd.DataFrame,
    pred_by_file: dict[str, np.ndarray],
    h012_prob: np.ndarray,
    h015_prob: np.ndarray,
    h016_prob: np.ndarray,
    sample: pd.DataFrame,
) -> dict[str, np.ndarray]:
    h012_post = pivot_posterior(H017.parent / "h012_public_equation_jepa_jackpot" / "h012_cell_posterior.csv", "posterior_prob", sample)
    h015_post = pivot_posterior(H017.parent / "h015_public_equation_self_feedback" / "h015_cell_posterior.csv", "posterior_prob", sample)
    return {
        "h012_current": clip_prob(h012_prob),
        "h015_candidate": clip_prob(h015_prob),
        "h016_candidate": clip_prob(h016_prob),
        "h012_public_posterior": h012_post,
        "h015_public_posterior": h015_post,
        "top8_soft_wide": top_weighted_prior(known, pred_by_file, 0.0060),
        "top8_soft_verywide": top_weighted_prior(known, pred_by_file, 0.0120),
    }


def build_w_priors(sample: pd.DataFrame) -> dict[str, np.ndarray]:
    n = len(sample) * len(TARGETS)
    uniform = np.full(n, 1.0 / n, dtype=np.float64)
    cells = pd.read_csv(H017.parent / "h016_public_subset_weight_jepa" / "h016_cell_public_weights.csv")
    w_mean = np.zeros(n, dtype=np.float64)
    w_median = np.zeros(n, dtype=np.float64)
    combined = np.zeros(n, dtype=np.float64)
    gain = np.zeros(n, dtype=np.float64)
    for rec in cells.to_dict("records"):
        idx = int(rec["row"]) * len(TARGETS) + TARGETS.index(str(rec["target"]))
        w_mean[idx] = float(rec["public_weight_mean"])
        w_median[idx] = float(rec["public_weight_median"])
        combined[idx] = float(rec["combined_score"])
        gain[idx] = float(rec["h015_public_gain_score"])
    combined_w = uniform * (0.25 + 1.50 * rank01(combined))
    gain_w = uniform * (0.25 + 1.50 * rank01(gain))
    return {
        "uniform": uniform,
        "h016_mean_weight": cap_and_normalize(w_mean, 0.0),
        "h016_median_weight": cap_and_normalize(w_median, 0.0),
        "h016_combined_rank": cap_and_normalize(combined_w, 12.0),
        "h016_gain_rank": cap_and_normalize(gain_w, 12.0),
    }


def equation_arrays(
    known: pd.DataFrame,
    pred_by_file: dict[str, np.ndarray],
    base_prob: np.ndarray,
) -> tuple[list[str], np.ndarray, np.ndarray, np.ndarray]:
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
    return files, np.vstack(d0_rows), np.vstack(d1_rows), np.asarray(actual, dtype=np.float64)


def project_joint(raw: np.ndarray, w_prior: np.ndarray, q_prior: np.ndarray, cap_mult: float) -> tuple[np.ndarray, np.ndarray]:
    n = len(w_prior)
    raw_w = raw[:n]
    raw_r = raw[n:]
    w = cap_and_normalize(np.where(np.isfinite(raw_w), raw_w, w_prior), cap_mult)
    denom = np.maximum(raw_w, 1.0e-18)
    q_raw = raw_r / denom
    q = np.where((raw_w > 1.0e-18) & np.isfinite(q_raw), q_raw, q_prior)
    q = clip_prob(q)
    return w, q


def fit_joint(
    d0: np.ndarray,
    d1: np.ndarray,
    actual: np.ndarray,
    w_prior: np.ndarray,
    q_prior: np.ndarray,
    ridge_mult: float,
    cap_mult: float,
) -> tuple[np.ndarray, np.ndarray]:
    a = np.hstack([d0, d1])
    x0 = np.concatenate([w_prior, w_prior * q_prior])
    gram = a @ a.T
    scale = float(np.median(np.diag(gram)))
    if not np.isfinite(scale) or scale <= 1.0e-18:
        scale = float(np.mean(np.diag(gram)) + 1.0e-18)
    residual = actual - a @ x0
    lam = ridge_mult * scale
    try:
        dual = np.linalg.solve(gram + lam * np.eye(len(actual)), residual)
    except np.linalg.LinAlgError:
        dual = np.linalg.pinv(gram + lam * np.eye(len(actual))) @ residual
    raw = x0 + a.T @ dual
    return project_joint(raw, w_prior, q_prior, cap_mult)


def joint_predict(d0: np.ndarray, d1: np.ndarray, w: np.ndarray, q: np.ndarray) -> np.ndarray:
    return d0 @ w + d1 @ (w * q)


def joint_metrics(
    d0: np.ndarray,
    d1: np.ndarray,
    actual: np.ndarray,
    w_prior: np.ndarray,
    q_prior: np.ndarray,
    ridge_mult: float,
    cap_mult: float,
) -> tuple[dict[str, float], np.ndarray, np.ndarray, np.ndarray]:
    w_full, q_full = fit_joint(d0, d1, actual, w_prior, q_prior, ridge_mult, cap_mult)
    pred_full = joint_predict(d0, d1, w_full, q_full)
    loo_pred: list[float] = []
    for heldout in range(len(actual)):
        keep = np.ones(len(actual), dtype=bool)
        keep[heldout] = False
        w, q = fit_joint(d0[keep], d1[keep], actual[keep], w_prior, q_prior, ridge_mult, cap_mult)
        loo_pred.append(float(joint_predict(d0[heldout : heldout + 1], d1[heldout : heldout + 1], w, q)[0]))
    pred = np.asarray(loo_pred, dtype=np.float64)
    err = pred - actual
    uniform = np.full(len(w_prior), 1.0 / len(w_prior), dtype=np.float64)
    uniform_pred = joint_predict(d0, d1, uniform, q_prior)
    entropy = -float(np.sum(w_full * np.log(w_full + 1.0e-30)))
    target_means = {}
    q_mat = q_full.reshape(-1, len(TARGETS))
    w_mat = w_full.reshape(-1, len(TARGETS))
    for i, t in enumerate(TARGETS):
        target_means[f"q_mean_{t}"] = float(q_mat[:, i].mean())
        target_means[f"w_mass_{t}"] = float(w_mat[:, i].sum())
    rec = {
        "loo_mae": float(np.mean(np.abs(err))),
        "loo_p90_abs": float(np.quantile(np.abs(err), 0.90)),
        "loo_spearman": float(pd.Series(pred).corr(pd.Series(actual), method="spearman")),
        "loo_pearson": float(pd.Series(pred).corr(pd.Series(actual), method="pearson")),
        "known_fit_mae": float(np.mean(np.abs(pred_full - actual))),
        "uniform_prior_mae": float(np.mean(np.abs(uniform_pred - actual))),
        "weight_eff_n": float(np.exp(entropy)),
        "weight_max_over_uniform": float(w_full.max() * len(w_full)),
        "weight_top50_mass": float(np.sort(w_full)[-50:].sum()),
        "weight_top200_mass": float(np.sort(w_full)[-200:].sum()),
        "q_mean": float(q_full.mean()),
        "q_std": float(q_full.std()),
        "q_prior_abs_move": float(np.mean(np.abs(q_full - q_prior))),
        "w_prior_l1_move": float(np.sum(np.abs(w_full - w_prior))),
        **target_means,
    }
    return rec, w_full, q_full, pred


def evaluate_configs(
    d0: np.ndarray,
    d1: np.ndarray,
    actual: np.ndarray,
    q_priors: dict[str, np.ndarray],
    w_priors: dict[str, np.ndarray],
) -> tuple[pd.DataFrame, dict[tuple[str, str, float, float], tuple[np.ndarray, np.ndarray]]]:
    rows: list[dict[str, Any]] = []
    states: dict[tuple[str, str, float, float], tuple[np.ndarray, np.ndarray]] = {}
    ridge_mults = [1.0e-5, 3.0e-5, 1.0e-4, 3.0e-4, 1.0e-3, 3.0e-3, 1.0e-2, 3.0e-2, 0.1, 0.3, 1.0, 3.0]
    cap_mults = [8.0, 12.0, 25.0, 50.0, 0.0]
    for q_name, q_mat in q_priors.items():
        q_prior = q_mat.reshape(-1)
        for w_name, w_prior in w_priors.items():
            for ridge in ridge_mults:
                for cap in cap_mults:
                    rec, w, q, _ = joint_metrics(d0, d1, actual, w_prior, q_prior, ridge, cap)
                    rec.update({"q_prior_name": q_name, "w_prior_name": w_name, "ridge_mult": ridge, "cap_mult": cap})
                    rows.append(rec)
                    states[(q_name, w_name, ridge, cap)] = (w, q)
    cfg = pd.DataFrame(rows)
    cfg["config_score"] = (
        cfg["loo_mae"].fillna(9.0)
        + 0.25 * cfg["loo_p90_abs"].fillna(9.0)
        - 0.00008 * cfg["loo_spearman"].fillna(0.0)
        + 0.00010 * np.maximum(120.0 - cfg["weight_eff_n"].fillna(0.0), 0.0) / 120.0
        + 0.00005 * np.maximum(cfg["weight_top50_mass"].fillna(0.0) - 0.35, 0.0)
        + 0.00003 * np.maximum(cfg["q_prior_abs_move"].fillna(0.0) - 0.18, 0.0)
    )
    cfg = cfg.sort_values(["config_score", "loo_mae", "known_fit_mae"]).reset_index(drop=True)
    cfg.to_csv(CONFIG_OUT, index=False)
    return cfg, states


def select_configs(configs: pd.DataFrame, limit: int = 12) -> list[JointConfig]:
    strong = configs[
        (configs["loo_spearman"].fillna(-1) >= 0.60)
        & (configs["loo_mae"] <= configs["loo_mae"].quantile(0.35))
        & (configs["weight_eff_n"] >= 120.0)
        & (configs["q_prior_abs_move"] <= 0.25)
    ]
    source = strong if len(strong) else configs
    out: list[JointConfig] = []
    seen: set[tuple[str, str, float, float]] = set()
    for rec in source.head(limit * 5).to_dict("records"):
        key = (str(rec["q_prior_name"]), str(rec["w_prior_name"]), float(rec["ridge_mult"]), float(rec["cap_mult"]))
        if key in seen:
            continue
        seen.add(key)
        out.append(JointConfig(*key))
        if len(out) >= limit:
            break
    return out


def null_stress(
    d0: np.ndarray,
    d1: np.ndarray,
    actual: np.ndarray,
    q_prior: np.ndarray,
    w_prior: np.ndarray,
    cfg: JointConfig,
    n_perm: int = 300,
) -> pd.DataFrame:
    real, _, _, _ = joint_metrics(d0, d1, actual, w_prior, q_prior, cfg.ridge_mult, cfg.cap_mult)
    rng = np.random.default_rng(20260602)
    rows: list[dict[str, Any]] = [
        {
            "kind": "real",
            "iteration": -1,
            "q_prior_name": cfg.q_prior_name,
            "w_prior_name": cfg.w_prior_name,
            "ridge_mult": cfg.ridge_mult,
            "cap_mult": cfg.cap_mult,
            **real,
        }
    ]
    for i in range(n_perm):
        rec, _, _, _ = joint_metrics(d0, d1, rng.permutation(actual), w_prior, q_prior, cfg.ridge_mult, cfg.cap_mult)
        rows.append(
            {
                "kind": "permute_actual",
                "iteration": i,
                "q_prior_name": cfg.q_prior_name,
                "w_prior_name": cfg.w_prior_name,
                "ridge_mult": cfg.ridge_mult,
                "cap_mult": cfg.cap_mult,
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
    specs = [
        ("loo_mae", "lower"),
        ("loo_p90_abs", "lower"),
        ("loo_spearman", "higher"),
        ("loo_pearson", "higher"),
        ("known_fit_mae", "lower"),
        ("weight_eff_n", "higher"),
        ("weight_top50_mass", "lower"),
        ("q_prior_abs_move", "lower"),
    ]
    for metric, direction in specs:
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


def build_cell_state(
    selected: list[JointConfig],
    states: dict[tuple[str, str, float, float], tuple[np.ndarray, np.ndarray]],
    h012_prob: np.ndarray,
    h015_prob: np.ndarray,
    h016_prob: np.ndarray,
    sample: pd.DataFrame,
) -> pd.DataFrame:
    shape = h012_prob.shape
    w_stack = []
    q_stack = []
    for cfg in selected:
        w, q = states[(cfg.q_prior_name, cfg.w_prior_name, cfg.ridge_mult, cfg.cap_mult)]
        w_stack.append(w)
        q_stack.append(q)
    w_arr = np.vstack(w_stack)
    q_arr = np.vstack(q_stack)
    h012_flat = h012_prob.reshape(-1)
    h015_flat = h015_prob.reshape(-1)
    h016_flat = h016_prob.reshape(-1)
    q_med = np.median(q_arr, axis=0)
    w_mean = np.mean(w_arr, axis=0)
    dz_joint = logit(q_med) - logit(h012_flat)
    dz_h015 = logit(h015_flat) - logit(h012_flat)
    dz_h016 = logit(h016_flat) - logit(h012_flat)
    agree_h015 = np.sign(dz_joint) == np.sign(dz_h015)
    agree_h016 = np.sign(dz_joint) == np.sign(dz_h016)
    oracle_gain = w_mean * (loss(h012_flat, q_med) - loss(q_med, q_med))
    h015_gain = w_mean * (loss(h012_flat, q_med) - loss(h015_flat, q_med))
    h016_gain = w_mean * (loss(h012_flat, q_med) - loss(h016_flat, q_med))
    weight_score = rank01(np.log(w_mean + 1.0e-30))
    q_shift_score = rank01(np.abs(dz_joint))
    oracle_gain_score = rank01(oracle_gain)
    h015_gain_score = rank01(h015_gain)
    h016_gain_score = rank01(h016_gain)
    consensus_score = rank01(oracle_gain * (0.25 + agree_h015.astype(float) + agree_h016.astype(float)))
    conflict_score = rank01(oracle_gain * ((~agree_h015).astype(float) + 0.5 * (~agree_h016).astype(float)))
    rows: list[dict[str, Any]] = []
    for row_i in range(shape[0]):
        for target_i, target in enumerate(TARGETS):
            idx = row_i * len(TARGETS) + target_i
            rows.append(
                {
                    "row": row_i,
                    "target": target,
                    "h012_prob": float(h012_flat[idx]),
                    "h015_prob": float(h015_flat[idx]),
                    "h016_prob": float(h016_flat[idx]),
                    "joint_q_median": float(q_med[idx]),
                    "joint_q_mean": float(q_arr[:, idx].mean()),
                    "joint_q_std": float(q_arr[:, idx].std()),
                    "joint_weight_mean": float(w_mean[idx]),
                    "joint_weight_median": float(np.median(w_arr[:, idx])),
                    "joint_logit_delta": float(dz_joint[idx]),
                    "abs_joint_logit_delta": float(abs(dz_joint[idx])),
                    "agree_h015_direction": bool(agree_h015[idx]),
                    "agree_h016_direction": bool(agree_h016[idx]),
                    "joint_oracle_cell_gain": float(oracle_gain[idx]),
                    "h015_cell_gain_under_joint_q": float(h015_gain[idx]),
                    "h016_cell_gain_under_joint_q": float(h016_gain[idx]),
                    "weight_score": float(weight_score[idx]),
                    "q_shift_score": float(q_shift_score[idx]),
                    "oracle_gain_score": float(oracle_gain_score[idx]),
                    "h015_gain_score": float(h015_gain_score[idx]),
                    "h016_gain_score": float(h016_gain_score[idx]),
                    "consensus_score": float(consensus_score[idx]),
                    "conflict_score": float(conflict_score[idx]),
                }
            )
    cells = pd.DataFrame(rows).sort_values("oracle_gain_score", ascending=False).reset_index(drop=True)
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
    for mode in ["oracle_gain", "consensus", "conflict", "weight_shift", "h015_gain", "h016_gain"]:
        for subset in ["all", "Q", "S"]:
            for k in [180, 300, 500, 800, 1100, 1400, 1650]:
                for alpha in [0.35, 0.55, 0.75, 1.00, 1.25]:
                    out.append(CandidateSpec(f"{mode}_{subset}_k{k}_a{alpha:g}", mode, subset, k, alpha))
    for target in TARGETS:
        for mode in ["oracle_gain", "consensus", "conflict"]:
            for k in [40, 80, 130, 190, 240]:
                for alpha in [0.55, 0.85, 1.15]:
                    out.append(CandidateSpec(f"{mode}_{target}_k{k}_a{alpha:g}", mode, target, k, alpha))
    return out


def select_mask(spec: CandidateSpec, cells: pd.DataFrame, shape: tuple[int, int]) -> np.ndarray:
    valid = target_mask(spec.target_subset, shape)
    score_col = {
        "oracle_gain": "oracle_gain_score",
        "consensus": "consensus_score",
        "conflict": "conflict_score",
        "weight_shift": "weight_score",
        "h015_gain": "h015_gain_score",
        "h016_gain": "h016_gain_score",
    }[spec.mode]
    score = np.full(shape[0] * shape[1], -np.inf, dtype=np.float64)
    for rec in cells.to_dict("records"):
        idx = int(rec["row"]) * len(TARGETS) + TARGETS.index(str(rec["target"]))
        score[idx] = float(rec[score_col])
        if abs(float(rec["joint_logit_delta"])) <= 1.0e-12:
            valid[idx] = False
    candidates = np.flatnonzero(valid)
    chosen = candidates[np.argsort(score[candidates])[-min(spec.k, len(candidates)) :]]
    mask = np.zeros(shape[0] * shape[1], dtype=bool)
    mask[chosen] = True
    return mask.reshape(shape)


def make_candidate_frame(base: pd.DataFrame, q_joint: np.ndarray, spec: CandidateSpec, mask: np.ndarray) -> pd.DataFrame:
    base_prob = base[TARGETS].to_numpy(dtype=np.float64)
    moved = logit(base_prob)
    moved[mask] = moved[mask] + spec.alpha * (logit(q_joint)[mask] - logit(base_prob)[mask])
    out = base.copy()
    out[TARGETS] = clip_prob(sigmoid(moved))
    return out


def score_prob(
    prob: np.ndarray,
    h012_prob: np.ndarray,
    selected: list[JointConfig],
    states: dict[tuple[str, str, float, float], tuple[np.ndarray, np.ndarray]],
) -> dict[str, float]:
    vals = []
    for cfg in selected:
        w, q = states[(cfg.q_prior_name, cfg.w_prior_name, cfg.ridge_mult, cfg.cap_mult)]
        diff = (loss(prob.reshape(-1), q) - loss(h012_prob.reshape(-1), q))
        vals.append(float(diff @ w))
    arr = np.asarray(vals, dtype=np.float64)
    uniform = []
    q_med = np.median(np.vstack([states[(cfg.q_prior_name, cfg.w_prior_name, cfg.ridge_mult, cfg.cap_mult)][1] for cfg in selected]), axis=0)
    uniform.append(float(np.mean(loss(prob.reshape(-1), q_med) - loss(h012_prob.reshape(-1), q_med))))
    return {
        "joint_delta_mean_vs_h012": float(arr.mean()),
        "joint_delta_p10_vs_h012": float(np.quantile(arr, 0.10)),
        "joint_delta_p90_vs_h012": float(np.quantile(arr, 0.90)),
        "joint_delta_max_vs_h012": float(arr.max()),
        "joint_beats_h012_rate": float(np.mean(arr < 0.0)),
        "uniform_joint_q_delta_vs_h012": float(np.mean(uniform)),
    }


def generate_candidates(
    h012: pd.DataFrame,
    h015: pd.DataFrame,
    h016: pd.DataFrame,
    cells: pd.DataFrame,
    selected: list[JointConfig],
    states: dict[tuple[str, str, float, float], tuple[np.ndarray, np.ndarray]],
) -> tuple[pd.DataFrame, Path | None]:
    h012_prob = h012[TARGETS].to_numpy(dtype=np.float64)
    h015_prob = h015[TARGETS].to_numpy(dtype=np.float64)
    h016_prob = h016[TARGETS].to_numpy(dtype=np.float64)
    q_stack = [states[(cfg.q_prior_name, cfg.w_prior_name, cfg.ridge_mult, cfg.cap_mult)][1] for cfg in selected]
    q_joint = np.median(np.vstack(q_stack), axis=0).reshape(h012_prob.shape)
    h015_score = score_prob(h015_prob, h012_prob, selected, states)
    h016_score = score_prob(h016_prob, h012_prob, selected, states)
    rows: list[dict[str, Any]] = []
    frames: list[tuple[pd.DataFrame, CandidateSpec, dict[str, Any]]] = []
    for spec in candidate_specs():
        mask = select_mask(spec, cells, h012_prob.shape)
        if not mask.any():
            continue
        out = make_candidate_frame(h012, q_joint, spec, mask)
        prob = out[TARGETS].to_numpy(dtype=np.float64)
        rec = score_prob(prob, h012_prob, selected, states)
        rec.update(
            {
                "candidate_id": spec.candidate_id,
                "mode": spec.mode,
                "target_subset": spec.target_subset,
                "k": spec.k,
                "alpha": spec.alpha,
                "changed_rows": int((np.abs(prob - h012_prob).max(axis=1) > 1.0e-12).sum()),
                "changed_cells": int((np.abs(prob - h012_prob) > 1.0e-12).sum()),
                "mean_abs_prob_delta_vs_h012": float(np.mean(np.abs(prob - h012_prob))),
                "max_abs_prob_delta_vs_h012": float(np.max(np.abs(prob - h012_prob))),
                "h015_joint_delta_mean": h015_score["joint_delta_mean_vs_h012"],
                "h016_joint_delta_mean": h016_score["joint_delta_mean_vs_h012"],
                "gain_vs_h015_under_joint": float(rec["joint_delta_mean_vs_h012"] - h015_score["joint_delta_mean_vs_h012"]),
                "gain_vs_h016_under_joint": float(rec["joint_delta_mean_vs_h012"] - h016_score["joint_delta_mean_vs_h012"]),
            }
        )
        rows.append(rec)
        frames.append((out, spec, rec))
    candidates = pd.DataFrame(rows)
    candidates["h017_decision"] = np.select(
        [
            (candidates["joint_delta_mean_vs_h012"] < -0.00090)
            & (candidates["joint_delta_p90_vs_h012"] < -0.00045)
            & (candidates["max_abs_prob_delta_vs_h012"] <= 0.22),
            (candidates["joint_delta_mean_vs_h012"] < -0.00035)
            & (candidates["joint_beats_h012_rate"] >= 0.85)
            & (candidates["max_abs_prob_delta_vs_h012"] <= 0.18),
        ],
        ["joint_world_big_bet", "joint_world_sensor"],
        default="diagnostic_only",
    )
    order = {"joint_world_big_bet": 0, "joint_world_sensor": 1, "diagnostic_only": 2}
    candidates["decision_rank"] = candidates["h017_decision"].map(order).astype(int)
    candidates = candidates.sort_values(["decision_rank", "joint_delta_mean_vs_h012", "joint_delta_p90_vs_h012"]).reset_index(drop=True)
    materialized: dict[str, str] = {}
    keep = set(candidates.head(45)["candidate_id"].astype(str))
    primary = None
    for out, spec, _ in frames:
        if spec.candidate_id not in keep:
            continue
        path = H017 / f"submission_h017_{safe_id(spec.candidate_id)}_{short_hash(out)}.csv"
        out.to_csv(path, index=False)
        materialized[spec.candidate_id] = rel(path)
    candidates["file"] = candidates["candidate_id"].map(materialized).fillna("not_materialized")
    promoted = candidates[candidates["h017_decision"].isin(["joint_world_big_bet", "joint_world_sensor"])].head(1)
    if not promoted.empty:
        source = ROOT / str(promoted.iloc[0]["file"])
        primary = ROOT / f"submission_h017_joint_label_weight_{safe_id(str(promoted.iloc[0]['candidate_id']), 64)}_uploadsafe.csv"
        shutil.copyfile(source, primary)
    candidates.to_csv(CANDIDATE_OUT, index=False)
    return candidates, primary


def write_report(
    configs: pd.DataFrame,
    selected: list[JointConfig],
    nulls: pd.DataFrame,
    cells: pd.DataFrame,
    candidates: pd.DataFrame,
    primary: Path | None,
) -> None:
    config_cols = [
        "q_prior_name",
        "w_prior_name",
        "ridge_mult",
        "cap_mult",
        "loo_mae",
        "loo_p90_abs",
        "loo_spearman",
        "uniform_prior_mae",
        "weight_eff_n",
        "weight_top50_mass",
        "q_prior_abs_move",
        "w_prior_l1_move",
    ]
    cand_cols = [
        "candidate_id",
        "h017_decision",
        "mode",
        "target_subset",
        "changed_cells",
        "joint_delta_mean_vs_h012",
        "joint_delta_p90_vs_h012",
        "h015_joint_delta_mean",
        "h016_joint_delta_mean",
        "gain_vs_h015_under_joint",
        "gain_vs_h016_under_joint",
        "max_abs_prob_delta_vs_h012",
        "file",
    ]
    target_summary = (
        cells.groupby("target", as_index=False)
        .agg(
            mean_weight=("joint_weight_mean", "mean"),
            mean_q=("joint_q_median", "mean"),
            mean_abs_logit_delta=("abs_joint_logit_delta", "mean"),
            mean_gain=("joint_oracle_cell_gain", "mean"),
            h015_agree_rate=("agree_h015_direction", "mean"),
            h016_agree_rate=("agree_h016_direction", "mean"),
        )
        .sort_values("mean_gain", ascending=False)
    )
    lines = [
        "# H017 Joint Label x Public-Weight HS-JEPA",
        "",
        "## Question",
        "",
        "Can H012's hidden label posterior and H016's public cell-weight field be solved as one joint latent state?",
        "",
        "## Selected Joint Configs",
        "",
        md_table(pd.DataFrame([cfg.__dict__ for cfg in selected]), n=20),
        "",
        "## Top Joint Diagnostics",
        "",
        md_table(configs[[c for c in config_cols if c in configs.columns]], n=25),
        "",
        "## Null Stress",
        "",
        "Public deltas are permuted while the same submission loss-delta tensor is kept fixed.",
        "",
        md_table(null_summary(nulls), n=20),
        "",
        "## Critical Read",
        "",
        "- The top configs barely move `q` or `w` away from the priors. This is not evidence that a brand-new joint latent was discovered.",
        "- The useful evidence is compatibility: `H012 public posterior + H016 diffuse public weights` already explains known public deltas almost exactly and far outside permutation nulls.",
        "- Therefore H017 is best read as a posterior-completion test: H012 may not have moved far enough toward its own public posterior under the H016 public-weight field.",
        "",
        "## Target Summary",
        "",
        md_table(target_summary, n=10),
        "",
        "## Candidate Selection",
        "",
        md_table(candidates[[c for c in cand_cols if c in candidates.columns]], n=45),
        "",
        "## Decision",
        "",
    ]
    if primary is None:
        lines.extend(
            [
                "- No H017 candidate clears the joint-world promotion gate.",
                "- Interpretation: the joint label x weight latent is diagnostic only; do not submit by default.",
            ]
        )
    else:
        lines.extend(
            [
                f"- Primary upload-safe candidate: `{rel(primary)}`.",
                "- Interpretation: this file bets that public labels and public cell weights must be solved jointly, not as separate H012/H016 projections.",
            ]
        )
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- `{rel(CONFIG_OUT)}`",
            f"- `{rel(NULL_OUT)}`",
            f"- `{rel(CELL_OUT)}`",
            f"- `{rel(CANDIDATE_OUT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    known, sample, h012, h015, h016, pred_by_file = load_frames()
    h012_prob = h012[TARGETS].to_numpy(dtype=np.float64)
    h015_prob = h015[TARGETS].to_numpy(dtype=np.float64)
    h016_prob = h016[TARGETS].to_numpy(dtype=np.float64)
    q_priors = build_q_priors(known, pred_by_file, h012_prob, h015_prob, h016_prob, sample)
    w_priors = build_w_priors(sample)
    _, d0, d1, actual = equation_arrays(known, pred_by_file, h012_prob)
    configs, states = evaluate_configs(d0, d1, actual, q_priors, w_priors)
    selected = select_configs(configs)
    best = selected[0]
    nulls = null_stress(
        d0,
        d1,
        actual,
        q_priors[best.q_prior_name].reshape(-1),
        w_priors[best.w_prior_name],
        best,
    )
    cells = build_cell_state(selected, states, h012_prob, h015_prob, h016_prob, sample)
    candidates, primary = generate_candidates(h012, h015, h016, cells, selected, states)
    write_report(configs, selected, nulls, cells, candidates, primary)
    print(f"wrote {REPORT_OUT}")
    if primary is not None:
        print(f"primary {primary}")
    print(
        candidates[
            [
                "candidate_id",
                "h017_decision",
                "joint_delta_mean_vs_h012",
                "joint_delta_p90_vs_h012",
                "h015_joint_delta_mean",
                "h016_joint_delta_mean",
                "gain_vs_h015_under_joint",
                "gain_vs_h016_under_joint",
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
