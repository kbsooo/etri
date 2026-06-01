#!/usr/bin/env python3
"""H016: public-subset weight HS-JEPA.

H012/H015 treat known public scores mostly as constraints on hidden label
posteriors. H016 tests the complementary hidden world:

    context = fixed submission loss-delta tensors under several label proxies
    target  = hidden public cell/row weighting that makes known LB deltas true
    action  = apply H015 movement where the inferred public-weight posterior is high

If this works, the next breakthrough is not "sharpen every H012 cell"; it is
"identify which row x target cells the public sensor is listening to." If it
fails, H015 remains the cleaner self-feedback sensor.
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
H016 = ROOT / "hitl" / "h016_public_subset_weight_jepa"
H016.mkdir(parents=True, exist_ok=True)

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
H012_PUBLIC = 0.5681234831

REPORT_OUT = H016 / "h016_report.md"
CONFIG_OUT = H016 / "h016_weight_configs.csv"
CELL_OUT = H016 / "h016_cell_public_weights.csv"
CANDIDATE_OUT = H016 / "h016_candidates.csv"
NULL_OUT = H016 / "h016_null_stress.csv"


@dataclass(frozen=True)
class WeightConfig:
    proxy_name: str
    ridge_mult: float
    cap_mult: float


@dataclass(frozen=True)
class CandidateSpec:
    candidate_id: str
    mode: str
    target_subset: str
    k: int
    alpha: float
    min_weight_q: float = 0.0


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
    sample = h012[KEYS].copy()
    return known, sample, h012, h015, h012, pred_by_file


def build_label_proxies(
    known: pd.DataFrame,
    pred_by_file: dict[str, np.ndarray],
    h012_prob: np.ndarray,
    h015_prob: np.ndarray,
    sample: pd.DataFrame,
) -> dict[str, np.ndarray]:
    lbs = known.set_index("file")["public_lb"].astype(float)
    best = float(lbs.min())
    top_files = [str(f) for f in known["file"].tolist() if str(f) in pred_by_file][:8]

    def weighted(scale: float) -> np.ndarray:
        preds = []
        weights = []
        for name in top_files:
            preds.append(pred_by_file[name])
            weights.append(np.exp(-(float(lbs[name]) - best) / scale))
        w = np.asarray(weights, dtype=np.float64)
        w = w / max(w.sum(), 1.0e-12)
        return np.tensordot(w, np.stack(preds, axis=0), axes=(0, 0))

    h015_post = pivot_posterior(H016.parent / "h015_public_equation_self_feedback" / "h015_cell_posterior.csv", "posterior_prob", sample)
    h012_post = pivot_posterior(H016.parent / "h012_public_equation_jepa_jackpot" / "h012_cell_posterior.csv", "posterior_prob", sample)
    proxies = {
        "h012_current": h012_prob,
        "h015_candidate": h015_prob,
        "h015_median_posterior": h015_post,
        "h012_median_posterior": h012_post,
        "top8_soft_wide": weighted(0.0060),
        "top8_soft_verywide": weighted(0.0120),
    }
    return {k: clip_prob(v) for k, v in proxies.items()}


def expected_delta_matrix(
    known: pd.DataFrame,
    pred_by_file: dict[str, np.ndarray],
    anchor_prob: np.ndarray,
    q_proxy: np.ndarray,
) -> tuple[list[str], np.ndarray, np.ndarray]:
    files: list[str] = []
    rows: list[np.ndarray] = []
    actual: list[float] = []
    base_lb = float(known.loc[known["file"].eq(CURRENT), "public_lb"].iloc[0])
    anchor_loss = loss(anchor_prob, q_proxy).reshape(-1)
    for rec in known.to_dict("records"):
        name = str(rec["file"])
        if name == CURRENT or name not in pred_by_file:
            continue
        pred_loss = loss(pred_by_file[name], q_proxy).reshape(-1)
        files.append(name)
        rows.append(pred_loss - anchor_loss)
        actual.append(float(rec["public_lb"]) - base_lb)
    return files, np.vstack(rows), np.asarray(actual, dtype=np.float64)


def cap_and_normalize(w: np.ndarray, cap_mult: float) -> np.ndarray:
    n = len(w)
    out = np.maximum(np.asarray(w, dtype=np.float64), 0.0)
    if cap_mult > 0:
        cap = cap_mult / n
        for _ in range(6):
            over = out > cap
            if not over.any():
                break
            excess = float((out[over] - cap).sum())
            out[over] = cap
            under = ~over
            if under.any():
                out[under] += excess * out[under] / max(float(out[under].sum()), 1.0e-12)
    s = float(out.sum())
    if not np.isfinite(s) or s <= 1.0e-18:
        return np.full(n, 1.0 / n, dtype=np.float64)
    return out / s


def fit_weights(deltas: np.ndarray, actual: np.ndarray, ridge_mult: float, cap_mult: float) -> np.ndarray:
    m, n = deltas.shape
    uniform = np.full(n, 1.0 / n, dtype=np.float64)
    residual = actual - deltas @ uniform
    centered = deltas - deltas.mean(axis=1, keepdims=True)
    gram = centered @ centered.T
    scale = float(np.median(np.diag(gram)))
    if not np.isfinite(scale) or scale <= 1.0e-18:
        scale = float(np.mean(np.diag(gram)) + 1.0e-18)
    lam = ridge_mult * scale
    try:
        dual = np.linalg.solve(gram + lam * np.eye(m), residual)
    except np.linalg.LinAlgError:
        dual = np.linalg.pinv(gram + lam * np.eye(m)) @ residual
    raw = uniform + centered.T @ dual
    return cap_and_normalize(raw, cap_mult)


def weight_metrics(deltas: np.ndarray, actual: np.ndarray, ridge_mult: float, cap_mult: float) -> tuple[dict[str, float], np.ndarray, np.ndarray]:
    w_full = fit_weights(deltas, actual, ridge_mult, cap_mult)
    pred_full = deltas @ w_full
    loo_pred: list[float] = []
    for heldout in range(len(actual)):
        keep = np.ones(len(actual), dtype=bool)
        keep[heldout] = False
        w = fit_weights(deltas[keep], actual[keep], ridge_mult, cap_mult)
        loo_pred.append(float(deltas[heldout] @ w))
    pred = np.asarray(loo_pred, dtype=np.float64)
    err = pred - actual
    entropy = -float(np.sum(w_full * np.log(w_full + 1.0e-30)))
    eff_n = float(np.exp(entropy))
    uniform_delta = deltas.mean(axis=1)
    rec = {
        "loo_mae": float(np.mean(np.abs(err))),
        "loo_p90_abs": float(np.quantile(np.abs(err), 0.90)),
        "loo_spearman": float(pd.Series(pred).corr(pd.Series(actual), method="spearman")),
        "loo_pearson": float(pd.Series(pred).corr(pd.Series(actual), method="pearson")),
        "known_fit_mae": float(np.mean(np.abs(pred_full - actual))),
        "uniform_mae": float(np.mean(np.abs(uniform_delta - actual))),
        "weight_eff_n": eff_n,
        "weight_max_over_uniform": float(w_full.max() * len(w_full)),
        "weight_top50_mass": float(np.sort(w_full)[-50:].sum()),
        "weight_top200_mass": float(np.sort(w_full)[-200:].sum()),
    }
    return rec, w_full, pred


def null_stress(
    known: pd.DataFrame,
    pred_by_file: dict[str, np.ndarray],
    h012_prob: np.ndarray,
    proxies: dict[str, np.ndarray],
    best: WeightConfig,
    n_perm: int = 300,
) -> pd.DataFrame:
    _, deltas, actual = expected_delta_matrix(known, pred_by_file, h012_prob, proxies[best.proxy_name])
    real, _, _ = weight_metrics(deltas, actual, best.ridge_mult, best.cap_mult)
    rng = np.random.default_rng(20260602)
    rows: list[dict[str, Any]] = []
    rows.append(
        {
            "kind": "real",
            "iteration": -1,
            "proxy_name": best.proxy_name,
            "ridge_mult": best.ridge_mult,
            "cap_mult": best.cap_mult,
            **real,
        }
    )
    for i in range(n_perm):
        perm_actual = rng.permutation(actual)
        rec, _, _ = weight_metrics(deltas, perm_actual, best.ridge_mult, best.cap_mult)
        rows.append(
            {
                "kind": "permute_actual",
                "iteration": i,
                "proxy_name": best.proxy_name,
                "ridge_mult": best.ridge_mult,
                "cap_mult": best.cap_mult,
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


def evaluate_weight_configs(
    known: pd.DataFrame,
    pred_by_file: dict[str, np.ndarray],
    h012_prob: np.ndarray,
    proxies: dict[str, np.ndarray],
) -> tuple[pd.DataFrame, dict[tuple[str, float, float], np.ndarray], dict[str, np.ndarray]]:
    rows: list[dict[str, Any]] = []
    weights: dict[tuple[str, float, float], np.ndarray] = {}
    delta_by_proxy: dict[str, np.ndarray] = {}
    actual_by_proxy: dict[str, np.ndarray] = {}
    ridge_mults = [1.0e-5, 3.0e-5, 1.0e-4, 3.0e-4, 1.0e-3, 3.0e-3, 1.0e-2, 3.0e-2, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0, 100.0]
    cap_mults = [12.0, 25.0, 50.0, 100.0, 0.0]
    for proxy_name, q_proxy in proxies.items():
        _, deltas, actual = expected_delta_matrix(known, pred_by_file, h012_prob, q_proxy)
        delta_by_proxy[proxy_name] = deltas
        actual_by_proxy[proxy_name] = actual
        for ridge in ridge_mults:
            for cap in cap_mults:
                rec, w, _ = weight_metrics(deltas, actual, ridge, cap)
                rec.update({"proxy_name": proxy_name, "ridge_mult": ridge, "cap_mult": cap})
                rows.append(rec)
                weights[(proxy_name, ridge, cap)] = w
    cfg = pd.DataFrame(rows)
    cfg["config_score"] = (
        cfg["loo_mae"].fillna(9.0)
        + 0.25 * cfg["loo_p90_abs"].fillna(9.0)
        - 0.00008 * cfg["loo_spearman"].fillna(0.0)
        + 0.00010 * np.maximum(80.0 - cfg["weight_eff_n"].fillna(0.0), 0.0) / 80.0
        + 0.00005 * np.maximum(cfg["weight_top50_mass"].fillna(0.0) - 0.35, 0.0)
    )
    cfg = cfg.sort_values(["config_score", "loo_mae", "known_fit_mae"]).reset_index(drop=True)
    cfg.to_csv(CONFIG_OUT, index=False)
    return cfg, weights, delta_by_proxy


def select_configs(configs: pd.DataFrame, limit: int = 12) -> list[WeightConfig]:
    strong = configs[
        (configs["loo_spearman"].fillna(-1) >= 0.35)
        & (configs["loo_mae"] <= configs["loo_mae"].quantile(0.50))
        & (configs["weight_eff_n"] >= 40.0)
    ]
    source = strong if len(strong) else configs
    out: list[WeightConfig] = []
    seen: set[tuple[str, float, float]] = set()
    for rec in source.head(limit * 4).to_dict("records"):
        key = (str(rec["proxy_name"]), float(rec["ridge_mult"]), float(rec["cap_mult"]))
        if key in seen:
            continue
        seen.add(key)
        out.append(WeightConfig(*key))
        if len(out) >= limit:
            break
    return out


def h015_cell_score(sample: pd.DataFrame) -> np.ndarray:
    src = pd.read_csv(H016.parent / "h015_public_equation_self_feedback" / "h015_cell_posterior.csv")
    score = np.zeros((len(sample), len(TARGETS)), dtype=np.float64)
    consistency = np.zeros_like(score)
    for rec in src.to_dict("records"):
        row = int(rec["row"])
        target_i = TARGETS.index(str(rec["target"]))
        score[row, target_i] = float(rec["cell_score"])
        consistency[row, target_i] = float(rec["direction_consistency"])
    return score.reshape(-1), consistency.reshape(-1)


def build_cell_weights(
    selected: list[WeightConfig],
    weights: dict[tuple[str, float, float], np.ndarray],
    proxies: dict[str, np.ndarray],
    h012_prob: np.ndarray,
    h015_prob: np.ndarray,
    sample: pd.DataFrame,
) -> pd.DataFrame:
    n = h012_prob.size
    uniform = 1.0 / n
    w_stack = []
    ratio_stack = []
    gain_stack = []
    for cfg in selected:
        key = (cfg.proxy_name, cfg.ridge_mult, cfg.cap_mult)
        w = weights[key]
        q = proxies[cfg.proxy_name].reshape(h012_prob.shape)
        cell_delta = (loss(h015_prob, q) - loss(h012_prob, q)).reshape(-1)
        w_stack.append(w)
        ratio_stack.append(np.log((w + 1.0e-30) / uniform))
        gain_stack.append(-w * cell_delta)
    w_arr = np.vstack(w_stack)
    ratio_arr = np.vstack(ratio_stack)
    gain_arr = np.vstack(gain_stack)
    h015_score, h015_consistency = h015_cell_score(sample)
    h012_flat = h012_prob.reshape(-1)
    h015_flat = h015_prob.reshape(-1)
    move_abs = np.abs(logit(h015_flat) - logit(h012_flat))
    weight_score = rank01(np.median(ratio_arr, axis=0))
    gain_score = rank01(np.mean(gain_arr, axis=0))
    h015_score_rank = rank01(h015_score)
    combined = 0.42 * weight_score + 0.38 * gain_score + 0.20 * h015_score_rank
    rows = []
    for row_i in range(len(sample)):
        for target_i, target in enumerate(TARGETS):
            idx = row_i * len(TARGETS) + target_i
            rows.append(
                {
                    "row": row_i,
                    "target": target,
                    "h012_prob": float(h012_flat[idx]),
                    "h015_prob": float(h015_flat[idx]),
                    "h015_minus_h012": float(h015_flat[idx] - h012_flat[idx]),
                    "abs_h015_logit_move": float(move_abs[idx]),
                    "public_weight_mean": float(w_arr[:, idx].mean()),
                    "public_weight_median": float(np.median(w_arr[:, idx])),
                    "log_weight_ratio_median": float(np.median(ratio_arr[:, idx])),
                    "weight_score": float(weight_score[idx]),
                    "h015_public_gain_score": float(gain_score[idx]),
                    "h015_cell_score": float(h015_score[idx]),
                    "h015_cell_score_rank": float(h015_score_rank[idx]),
                    "h015_direction_consistency": float(h015_consistency[idx]),
                    "combined_score": float(combined[idx]),
                    "mean_weighted_h015_cell_gain": float(np.mean(gain_arr[:, idx])),
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
    modes = ["combined", "weight", "gain", "h015"]
    for mode in modes:
        for subset in ["all", "Q", "S"]:
            for k in [120, 240, 400, 700, 1000, 1400, 1600]:
                for alpha in [0.75, 1.00, 1.25, 1.50]:
                    out.append(CandidateSpec(f"{mode}_{subset}_k{k}_a{alpha:g}", mode, subset, k, alpha))
    for target in TARGETS:
        for mode in ["combined", "gain"]:
            for k in [30, 60, 100, 160, 220]:
                for alpha in [1.0, 1.35]:
                    out.append(CandidateSpec(f"{mode}_{target}_k{k}_a{alpha:g}", mode, target, k, alpha))
    for q in [0.55, 0.65, 0.75, 0.85]:
        for alpha in [1.0, 1.25]:
            out.append(CandidateSpec(f"public_weight_floor_q{int(q*100)}_a{alpha:g}", "floor", "all", 1750, alpha, q))
    return out


def select_mask(spec: CandidateSpec, cells: pd.DataFrame, h012_prob: np.ndarray, h015_prob: np.ndarray) -> np.ndarray:
    shape = h012_prob.shape
    valid = target_mask(spec.target_subset, shape)
    move = np.abs(logit(h015_prob).reshape(-1) - logit(h012_prob).reshape(-1)) > 1.0e-12
    valid &= move
    if spec.min_weight_q > 0:
        score = np.zeros(shape[0] * shape[1], dtype=np.float64)
        for rec in cells.to_dict("records"):
            idx = int(rec["row"]) * len(TARGETS) + TARGETS.index(str(rec["target"]))
            score[idx] = float(rec["weight_score"])
        valid &= score >= spec.min_weight_q
    col = {
        "combined": "combined_score",
        "weight": "weight_score",
        "gain": "h015_public_gain_score",
        "h015": "h015_cell_score_rank",
        "floor": "combined_score",
    }[spec.mode]
    score_arr = np.full(shape[0] * shape[1], -np.inf, dtype=np.float64)
    for rec in cells.to_dict("records"):
        idx = int(rec["row"]) * len(TARGETS) + TARGETS.index(str(rec["target"]))
        score_arr[idx] = float(rec[col])
    candidates = np.flatnonzero(valid)
    chosen = candidates[np.argsort(score_arr[candidates])[-min(spec.k, len(candidates)) :]]
    mask = np.zeros(shape[0] * shape[1], dtype=bool)
    mask[chosen] = True
    return mask.reshape(shape)


def make_candidate_frame(base: pd.DataFrame, h015: pd.DataFrame, spec: CandidateSpec, mask: np.ndarray) -> pd.DataFrame:
    base_prob = base[TARGETS].to_numpy(dtype=np.float64)
    h015_prob = h015[TARGETS].to_numpy(dtype=np.float64)
    z = logit(base_prob)
    dz = logit(h015_prob) - z
    out_prob = base_prob.copy()
    moved = z.copy()
    moved[mask] = z[mask] + spec.alpha * dz[mask]
    out_prob[mask] = sigmoid(moved[mask])
    out = base.copy()
    out[TARGETS] = np.clip(out_prob, EPS, 1.0 - EPS)
    return out


def score_prob(
    prob: np.ndarray,
    h012_prob: np.ndarray,
    selected: list[WeightConfig],
    weights: dict[tuple[str, float, float], np.ndarray],
    proxies: dict[str, np.ndarray],
) -> dict[str, float]:
    weighted = []
    uniform = []
    for cfg in selected:
        key = (cfg.proxy_name, cfg.ridge_mult, cfg.cap_mult)
        q = proxies[cfg.proxy_name]
        diff = (loss(prob, q) - loss(h012_prob, q)).reshape(-1)
        weighted.append(float(diff @ weights[key]))
        uniform.append(float(diff.mean()))
    warr = np.asarray(weighted, dtype=np.float64)
    uarr = np.asarray(uniform, dtype=np.float64)
    return {
        "subset_delta_mean_vs_h012": float(warr.mean()),
        "subset_delta_p10_vs_h012": float(np.quantile(warr, 0.10)),
        "subset_delta_p90_vs_h012": float(np.quantile(warr, 0.90)),
        "subset_delta_max_vs_h012": float(warr.max()),
        "subset_beats_h012_rate": float(np.mean(warr < 0.0)),
        "uniform_delta_mean_vs_h012": float(uarr.mean()),
        "uniform_delta_p90_vs_h012": float(np.quantile(uarr, 0.90)),
    }


def generate_candidates(
    h012: pd.DataFrame,
    h015: pd.DataFrame,
    cells: pd.DataFrame,
    selected: list[WeightConfig],
    weights: dict[tuple[str, float, float], np.ndarray],
    proxies: dict[str, np.ndarray],
) -> tuple[pd.DataFrame, Path | None]:
    h012_prob = h012[TARGETS].to_numpy(dtype=np.float64)
    h015_prob = h015[TARGETS].to_numpy(dtype=np.float64)
    h015_score = score_prob(h015_prob, h012_prob, selected, weights, proxies)
    rows: list[dict[str, Any]] = []
    frames: list[tuple[pd.DataFrame, CandidateSpec, dict[str, Any]]] = []
    for spec in candidate_specs():
        mask = select_mask(spec, cells, h012_prob, h015_prob)
        if not mask.any():
            continue
        out = make_candidate_frame(h012, h015, spec, mask)
        prob = out[TARGETS].to_numpy(dtype=np.float64)
        rec = score_prob(prob, h012_prob, selected, weights, proxies)
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
                "h015_subset_delta_mean": h015_score["subset_delta_mean_vs_h012"],
                "delta_gain_vs_h015_subset": float(rec["subset_delta_mean_vs_h012"] - h015_score["subset_delta_mean_vs_h012"]),
            }
        )
        rows.append(rec)
        frames.append((out, spec, rec))
    candidates = pd.DataFrame(rows)
    candidates["h016_decision"] = np.select(
        [
            (candidates["delta_gain_vs_h015_subset"] < -0.00035)
            & (candidates["subset_delta_p90_vs_h012"] < candidates["h015_subset_delta_mean"] + 0.00035)
            & (candidates["max_abs_prob_delta_vs_h012"] <= 0.11),
            (candidates["delta_gain_vs_h015_subset"] < -0.00015)
            & (candidates["subset_beats_h012_rate"] >= 0.80)
            & (candidates["max_abs_prob_delta_vs_h012"] <= 0.14),
        ],
        ["public_subset_big_bet", "public_subset_sensor"],
        default="diagnostic_only",
    )
    order = {"public_subset_big_bet": 0, "public_subset_sensor": 1, "diagnostic_only": 2}
    candidates["decision_rank"] = candidates["h016_decision"].map(order).astype(int)
    candidates = candidates.sort_values(["decision_rank", "delta_gain_vs_h015_subset", "subset_delta_p90_vs_h012"]).reset_index(drop=True)

    materialized: dict[str, str] = {}
    keep_ids = set(candidates.head(40)["candidate_id"].astype(str))
    primary = None
    for out, spec, _ in frames:
        if spec.candidate_id not in keep_ids:
            continue
        path = H016 / f"submission_h016_{safe_id(spec.candidate_id)}_{short_hash(out)}.csv"
        out.to_csv(path, index=False)
        materialized[spec.candidate_id] = rel(path)
    candidates["file"] = candidates["candidate_id"].map(materialized).fillna("not_materialized")
    promoted = candidates[candidates["h016_decision"].isin(["public_subset_big_bet", "public_subset_sensor"])].head(1)
    if not promoted.empty:
        source = ROOT / str(promoted.iloc[0]["file"])
        primary = ROOT / f"submission_h016_public_subset_{safe_id(str(promoted.iloc[0]['candidate_id']), 72)}_uploadsafe.csv"
        shutil.copyfile(source, primary)
    candidates.to_csv(CANDIDATE_OUT, index=False)
    return candidates, primary


def write_report(
    configs: pd.DataFrame,
    selected: list[WeightConfig],
    cells: pd.DataFrame,
    candidates: pd.DataFrame,
    nulls: pd.DataFrame,
    primary: Path | None,
) -> None:
    config_cols = [
        "proxy_name",
        "ridge_mult",
        "cap_mult",
        "loo_mae",
        "loo_p90_abs",
        "loo_spearman",
        "uniform_mae",
        "weight_eff_n",
        "weight_top50_mass",
        "weight_top200_mass",
    ]
    cand_cols = [
        "candidate_id",
        "h016_decision",
        "mode",
        "target_subset",
        "changed_cells",
        "subset_delta_mean_vs_h012",
        "subset_delta_p90_vs_h012",
        "h015_subset_delta_mean",
        "delta_gain_vs_h015_subset",
        "uniform_delta_mean_vs_h012",
        "max_abs_prob_delta_vs_h012",
        "file",
    ]
    target_summary = (
        cells.groupby("target", as_index=False)
        .agg(
            mean_weight_score=("weight_score", "mean"),
            top_weight_cells=("weight_score", lambda s: int((s >= s.quantile(0.90)).sum())),
            mean_gain_score=("h015_public_gain_score", "mean"),
            mean_combined=("combined_score", "mean"),
        )
        .sort_values("mean_combined", ascending=False)
    )
    lines = [
        "# H016 Public-Subset Weight HS-JEPA",
        "",
        "## Question",
        "",
        "Are known public LB equations telling us hidden labels, or also which row x target cells the public subset listens to?",
        "",
        "## Selected Weight Configs",
        "",
        md_table(pd.DataFrame([cfg.__dict__ for cfg in selected]), n=20),
        "",
        "## Top Weight Diagnostics",
        "",
        md_table(configs[config_cols], n=25),
        "",
        "## Null Stress",
        "",
        "This permutes the known public LB deltas while keeping the same submission-delta tensor. If H016 is just an underdetermined equation fit, permutation should look similarly good.",
        "",
        md_table(null_summary(nulls), n=20),
        "",
        "## Target Weight Summary",
        "",
        md_table(target_summary, n=10),
        "",
        "## Candidate Selection",
        "",
        md_table(candidates[[c for c in cand_cols if c in candidates.columns]], n=40),
        "",
        "## Decision",
        "",
    ]
    if primary is None:
        lines.extend(
            [
                "- No public-subset weighted candidate beats H015 strongly enough to promote.",
                "- Interpretation: H015 remains the cleaner next sensor; subset weights are diagnostic, not an action layer yet.",
            ]
        )
    else:
        lines.extend(
            [
                f"- Primary upload-safe candidate: `{rel(primary)}`.",
                "- Interpretation: hidden public-subset weighting produces a different action than H015 and is worth a public sensor.",
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
    known, sample, h012, h015, _, pred_by_file = load_frames()
    h012_prob = h012[TARGETS].to_numpy(dtype=np.float64)
    h015_prob = h015[TARGETS].to_numpy(dtype=np.float64)
    proxies = build_label_proxies(known, pred_by_file, h012_prob, h015_prob, sample)
    configs, weights, _ = evaluate_weight_configs(known, pred_by_file, h012_prob, proxies)
    selected = select_configs(configs)
    nulls = null_stress(known, pred_by_file, h012_prob, proxies, selected[0])
    cells = build_cell_weights(selected, weights, proxies, h012_prob, h015_prob, sample)
    candidates, primary = generate_candidates(h012, h015, cells, selected, weights, proxies)
    write_report(configs, selected, cells, candidates, nulls, primary)
    print(f"wrote {REPORT_OUT}")
    if primary is not None:
        print(f"primary {primary}")
    print(
        candidates[
            [
                "candidate_id",
                "h016_decision",
                "subset_delta_mean_vs_h012",
                "subset_delta_p90_vs_h012",
                "h015_subset_delta_mean",
                "delta_gain_vs_h015_subset",
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
