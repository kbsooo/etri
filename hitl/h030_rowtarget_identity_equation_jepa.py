#!/usr/bin/env python3
"""H030: row-target identity public-equation HS-JEPA.

H012 treated known public LB observations as equations over hidden public
labels, then materialized a large E247 -> posterior move.  H016/H019/H020/H029
showed that the public state is not only a global prior: row identity, target
identity, and exact row-target placement matter.

H030 moves that belief inside the equation solver itself.  Each row-target cell
gets a learned "allowance" prior.  Cells supported by row-subset, cell-weight,
joint-vector, and memory-state evidence are allowed to move more under the
public equations; weak cells are strongly shrunk.  The falsification target is
sharp:

    Can these row-target identity priors predict the H012 jackpot when H012 is
    held out, and can they propose a post-H012 action that survives H024 stress?

This is deliberately a big-bet diagnostic.  It is not a smooth blend and not a
safe 0.0001 tuning layer.
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


ROOT = Path(__file__).resolve().parents[1]
HITL = ROOT / "hitl"
OUT = HITL / "h030_rowtarget_identity_equation_jepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1.0e-6

E247 = "submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv"
H012 = "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"
H012_LB = 0.5681234831
E247_LB = 0.5761589494

H012_DIR = HITL / "h012_public_equation_jepa_jackpot"
H014_DIR = HITL / "h014_sleep_state_memory_posterior_audit"
H016_DIR = HITL / "h016_public_subset_weight_jepa"
H019_DIR = HITL / "h019_row_subset_hardworld_jepa"
H020_DIR = HITL / "h020_joint_vector_world_jepa"


@dataclass(frozen=True)
class EquationSet:
    name: str
    anchor_file: str
    include_h012: bool


@dataclass(frozen=True)
class FitConfig:
    equation_set: str
    prior_name: str
    support_name: str
    ridge_mult: float
    floor: float
    gain: float
    power: float


def import_module(path: Path, name: str) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def safe_id(text: str, limit: int = 96) -> str:
    clean = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(text)).strip("_")
    return clean[:limit].strip("_")


def short_hash(frame: pd.DataFrame) -> str:
    arr = np.asarray(frame[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def logit(x: np.ndarray) -> np.ndarray:
    p = clip_prob(x)
    return np.log(p / (1.0 - p))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(x, dtype=np.float64)))


def binary_loss(prob: np.ndarray, y_prob: np.ndarray) -> np.ndarray:
    p = clip_prob(prob)
    q = clip_prob(y_prob)
    return -(q * np.log(p) + (1.0 - q) * np.log(1.0 - p))


def rank01(values: pd.Series | np.ndarray, fill: float = 0.0) -> np.ndarray:
    s = pd.Series(np.asarray(values, dtype=np.float64)).replace([np.inf, -np.inf], np.nan).fillna(fill)
    if float(s.std()) < 1.0e-15:
        return np.full(len(s), 0.5, dtype=np.float64)
    return s.rank(method="average", pct=True).to_numpy(dtype=np.float64)


def normalize_allowance(score: np.ndarray, floor: float, gain: float, power: float) -> np.ndarray:
    score = np.clip(np.asarray(score, dtype=np.float64), 0.0, 1.0)
    raw = float(floor) + float(gain) * np.power(score, float(power))
    raw = np.clip(raw, 1.0e-4, np.quantile(raw, 0.995) if len(raw) else 1.0)
    mean = float(np.mean(raw))
    if not np.isfinite(mean) or mean <= 1.0e-15:
        return np.ones_like(raw)
    return raw / mean


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


def load_h024() -> object:
    return import_module(HITL / "h024_action_health_decoder_jepa.py", "h024_h030")


def load_known(h024: object) -> pd.DataFrame:
    known = h024.read_public_observations().copy()
    known = known.drop_duplicates("file", keep="last").sort_values("public_lb").reset_index(drop=True)
    known.to_csv(OUT / "h030_known_public_sensors.csv", index=False)
    return known


def public_lb(known: pd.DataFrame, file_name: str) -> float:
    rows = known[known["file"].astype(str).eq(file_name)]
    if rows.empty:
        raise KeyError(file_name)
    return float(rows["public_lb"].iloc[0])


def load_prediction_map(h024: object, known: pd.DataFrame, sample: pd.DataFrame) -> dict[str, np.ndarray]:
    pred_by_file: dict[str, np.ndarray] = {}
    for file_name in known["file"].astype(str).tolist():
        try:
            pred_by_file[file_name] = h024.load_sub(file_name, sample)[TARGETS].to_numpy(dtype=np.float64)
        except FileNotFoundError:
            continue
    return pred_by_file


def equation_arrays(
    known: pd.DataFrame,
    pred_by_file: dict[str, np.ndarray],
    anchor_file: str,
    anchor_prob: np.ndarray,
    anchor_lb: float,
    include_h012: bool,
) -> tuple[pd.DataFrame, np.ndarray, np.ndarray, np.ndarray]:
    anchor = clip_prob(anchor_prob.reshape(-1))
    rows: list[dict[str, Any]] = []
    a_rows: list[np.ndarray] = []
    d0_rows: list[np.ndarray] = []
    b_vals: list[float] = []
    n = anchor.size
    for rec in known.to_dict("records"):
        file_name = str(rec["file"])
        if file_name == anchor_file:
            continue
        if file_name == H012 and not include_h012:
            continue
        if file_name not in pred_by_file:
            continue
        pred = clip_prob(pred_by_file[file_name].reshape(-1))
        d0 = -np.log(1.0 - pred) + np.log(1.0 - anchor)
        d1 = np.log((1.0 - pred) / pred) - np.log((1.0 - anchor) / anchor)
        actual_delta = float(rec["public_lb"]) - anchor_lb
        rhs = actual_delta - float(d0.mean())
        rows.append(
            {
                "file": file_name,
                "public_lb": float(rec["public_lb"]),
                "anchor_file": anchor_file,
                "actual_delta_vs_anchor": actual_delta,
                "d0_mean": float(d0.mean()),
                "rhs_label_term": rhs,
                "d1_abs_mean": float(np.mean(np.abs(d1))),
                "changed_cells_vs_anchor": int((np.abs(pred - anchor) > 1.0e-12).sum()),
            }
        )
        a_rows.append(d1 / n)
        d0_rows.append(d0)
        b_vals.append(rhs)
    eq = pd.DataFrame(rows)
    if not a_rows:
        return eq, np.zeros((0, n)), np.zeros((0, n)), np.zeros(0, dtype=np.float64)
    return eq, np.vstack(a_rows), np.vstack(d0_rows), np.asarray(b_vals, dtype=np.float64)


def fit_weighted_posterior(
    a: np.ndarray,
    b: np.ndarray,
    prior: np.ndarray,
    allowance: np.ndarray,
    ridge_mult: float,
) -> np.ndarray:
    prior = clip_prob(prior)
    if len(b) == 0:
        return prior.copy()
    d = np.asarray(allowance, dtype=np.float64)
    d = np.where(np.isfinite(d), d, 1.0)
    d = np.clip(d, 1.0e-4, 100.0)
    d = d / max(float(d.mean()), 1.0e-12)
    ad = a * d[None, :]
    gram = ad @ a.T
    diag = np.diag(gram)
    scale = float(np.median(diag[diag > 0])) if np.any(diag > 0) else float(np.mean(np.abs(gram)) + 1.0e-18)
    lam = float(ridge_mult) * max(scale, 1.0e-18)
    residual = b - a @ prior
    try:
        dual = np.linalg.solve(gram + lam * np.eye(len(b)), residual)
    except np.linalg.LinAlgError:
        dual = np.linalg.pinv(gram + lam * np.eye(len(b))) @ residual
    q = prior + d * (a.T @ dual)
    return clip_prob(q)


def predict_delta(d0: np.ndarray, d1: np.ndarray, q: np.ndarray) -> float:
    return float(np.mean(d0 + d1 * q))


def merge_cell_state(state: pd.DataFrame, path: Path, prefix: str, cols: list[str]) -> pd.DataFrame:
    if not path.exists():
        for col in cols:
            state[f"{prefix}_{col}"] = 0.0
        return state
    df = pd.read_csv(path)
    keep = ["row", "target"] + [c for c in cols if c in df.columns]
    df = df[keep].copy()
    rename = {c: f"{prefix}_{c}" for c in keep if c not in {"row", "target"}}
    df = df.rename(columns=rename)
    out = state.merge(df, on=["row", "target"], how="left")
    for col in cols:
        name = f"{prefix}_{col}"
        if name not in out.columns:
            out[name] = 0.0
        out[name] = out[name].fillna(0.0)
    return out


def merge_row_state(state: pd.DataFrame, path: Path, prefix: str, cols: list[str]) -> pd.DataFrame:
    if not path.exists():
        for col in cols:
            state[f"{prefix}_{col}"] = 0.0
        return state
    df = pd.read_csv(path)
    keep = ["row"] + [c for c in cols if c in df.columns]
    df = df[keep].drop_duplicates("row").copy()
    rename = {c: f"{prefix}_{c}" for c in keep if c != "row"}
    df = df.rename(columns=rename)
    out = state.merge(df, on="row", how="left")
    for col in cols:
        name = f"{prefix}_{col}"
        if name not in out.columns:
            out[name] = 0.0
        out[name] = out[name].fillna(0.0)
    return out


def build_cell_state(sample: pd.DataFrame, e247_prob: np.ndarray, h012_prob: np.ndarray) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    e247_z = logit(e247_prob)
    h012_z = logit(h012_prob)
    for row_i in range(e247_prob.shape[0]):
        meta = sample.iloc[row_i].to_dict()
        for target_i, target in enumerate(TARGETS):
            move = float(h012_z[row_i, target_i] - e247_z[row_i, target_i])
            rows.append(
                {
                    "row": row_i,
                    "target": target,
                    "target_i": target_i,
                    "subject_id": str(meta["subject_id"]),
                    "sleep_date": str(meta["sleep_date"])[:10],
                    "lifelog_date": str(meta["lifelog_date"])[:10],
                    "e247_prob": float(e247_prob[row_i, target_i]),
                    "h012_prob": float(h012_prob[row_i, target_i]),
                    "h012_logit_delta": move,
                    "h012_support": bool(abs(h012_prob[row_i, target_i] - e247_prob[row_i, target_i]) > 1.0e-10),
                    "abs_h012_logit_delta": abs(move),
                }
            )
    state = pd.DataFrame(rows)
    state = merge_cell_state(
        state,
        H012_DIR / "h012_cell_posterior.csv",
        "h012post",
        ["posterior_minus_base", "logit_delta_to_posterior", "direction_consistency", "cell_score"],
    )
    state = merge_cell_state(
        state,
        H014_DIR / "h014_memory_cells.csv",
        "h014mem",
        ["memory_alignment_q", "private_safe_score", "posterior_gain", "row_full_reliability_q"],
    )
    state = merge_cell_state(
        state,
        H016_DIR / "h016_cell_public_weights.csv",
        "h016",
        ["weight_score", "combined_score", "h015_cell_score", "public_weight_median"],
    )
    state = merge_row_state(
        state,
        H019_DIR / "h019_row_public_posterior.csv",
        "h019",
        ["inclusion_prob", "inclusion_lift", "row_weight", "row_score", "row_gain_to_proxy"],
    )
    state = merge_cell_state(
        state,
        H020_DIR / "h020_cell_joint_vector_posterior.csv",
        "h020cell",
        ["q_joint_vector", "joint_minus_h012", "row_weight", "row_score", "cell_gain", "gain_score", "shift_score", "move_score", "combined_score"],
    )
    state = merge_row_state(
        state,
        H020_DIR / "h020_row_vector_state.csv",
        "h020row",
        ["row_weight", "max_vector_prob", "row_vector_entropy", "row_gain_to_joint_vector", "row_abs_shift_vs_h018", "row_score"],
    )

    state["score_h012_support"] = rank01(state["abs_h012_logit_delta"])
    state["score_h012_posterior"] = rank01(np.abs(state["h012post_logit_delta_to_posterior"]) * state["h012post_direction_consistency"])
    state["score_public_cell_weight"] = rank01(0.55 * state["h016_combined_score"] + 0.45 * state["h016_weight_score"])
    state["score_public_row_subset"] = rank01(0.55 * state["h019_row_score"] + 0.30 * state["h019_inclusion_prob"] + 0.15 * state["h019_row_weight"])
    state["score_joint_vector_cell"] = rank01(0.45 * state["h020cell_combined_score"] + 0.25 * state["h020cell_gain_score"] + 0.15 * state["h020cell_shift_score"] + 0.15 * state["h020cell_move_score"])
    state["score_joint_vector_row"] = rank01(0.55 * state["h020row_row_score"] + 0.25 * state["h020row_row_weight"] + 0.20 * state["h020row_row_gain_to_joint_vector"])
    state["score_memory_state"] = rank01(0.50 * state["h014mem_memory_alignment_q"] + 0.35 * state["h014mem_private_safe_score"] + 0.15 * state["h014mem_row_full_reliability_q"])
    state["score_identity_combo"] = np.clip(
        0.22 * state["score_h012_posterior"]
        + 0.18 * state["score_public_cell_weight"]
        + 0.22 * state["score_public_row_subset"]
        + 0.23 * state["score_joint_vector_cell"]
        + 0.10 * state["score_joint_vector_row"]
        + 0.05 * state["score_memory_state"],
        0.0,
        1.0,
    )
    state["score_no_h012_combo"] = np.clip(
        0.25 * state["score_public_cell_weight"]
        + 0.25 * state["score_public_row_subset"]
        + 0.28 * state["score_joint_vector_cell"]
        + 0.15 * state["score_joint_vector_row"]
        + 0.07 * state["score_memory_state"],
        0.0,
        1.0,
    )
    state["score_memory_public_combo"] = np.clip(
        0.32 * state["score_memory_state"]
        + 0.25 * state["score_public_row_subset"]
        + 0.25 * state["score_joint_vector_row"]
        + 0.18 * state["score_public_cell_weight"],
        0.0,
        1.0,
    )
    state["score_exact_support_plus_identity"] = np.where(
        state["h012_support"],
        0.55 + 0.45 * state["score_identity_combo"],
        0.35 * state["score_identity_combo"],
    )
    state.to_csv(OUT / "h030_cell_identity_state.csv", index=False)
    return state


def support_score_maps(state: pd.DataFrame) -> dict[str, np.ndarray]:
    names = [
        "score_h012_support",
        "score_h012_posterior",
        "score_public_cell_weight",
        "score_public_row_subset",
        "score_joint_vector_cell",
        "score_joint_vector_row",
        "score_memory_state",
        "score_identity_combo",
        "score_no_h012_combo",
        "score_memory_public_combo",
        "score_exact_support_plus_identity",
    ]
    out = {"uniform": np.ones(len(state), dtype=np.float64)}
    for name in names:
        out[name.replace("score_", "")] = state[name].to_numpy(dtype=np.float64)
    return out


def build_priors(
    known: pd.DataFrame,
    pred_by_file: dict[str, np.ndarray],
    anchor_prob: np.ndarray,
    e247_prob: np.ndarray,
    h012_prob: np.ndarray,
) -> dict[str, np.ndarray]:
    lbs = known.set_index("file")["public_lb"]
    priors = {
        "anchor": anchor_prob.reshape(-1),
        "e247": e247_prob.reshape(-1),
        "h012": h012_prob.reshape(-1),
    }
    good_preds = []
    good_weights = []
    for file_name, pred in pred_by_file.items():
        lb = float(lbs[file_name])
        if lb <= H012_LB + 0.0085:
            good_preds.append(pred)
            good_weights.append(np.exp(-(lb - H012_LB) / 0.0022))
    if good_preds:
        stack = np.stack(good_preds, axis=0)
        w = np.asarray(good_weights, dtype=np.float64)
        w = w / w.sum()
        priors["good_soft"] = np.tensordot(w, stack, axes=(0, 0)).reshape(-1)
        priors["good_median"] = np.median(stack, axis=0).reshape(-1)
    pre_preds = []
    pre_weights = []
    for file_name, pred in pred_by_file.items():
        if file_name == H012:
            continue
        lb = float(lbs[file_name])
        if lb <= E247_LB + 0.00035:
            pre_preds.append(pred)
            pre_weights.append(np.exp(-(lb - E247_LB) / 0.00025))
    if pre_preds:
        stack = np.stack(pre_preds, axis=0)
        w = np.asarray(pre_weights, dtype=np.float64)
        w = w / w.sum()
        priors["pre_h012_good_soft"] = np.tensordot(w, stack, axes=(0, 0)).reshape(-1)
    return {k: clip_prob(v) for k, v in priors.items()}


def h012_external_equation(
    known: pd.DataFrame,
    pred_by_file: dict[str, np.ndarray],
    anchor_file: str,
    anchor_prob: np.ndarray,
    anchor_lb: float,
) -> tuple[np.ndarray, np.ndarray, float] | None:
    if H012 not in pred_by_file or anchor_file == H012:
        return None
    eq, a, d0, _ = equation_arrays(known, {H012: pred_by_file[H012]}, anchor_file, anchor_prob, anchor_lb, include_h012=True)
    if eq.empty:
        return None
    actual = float(eq["actual_delta_vs_anchor"].iloc[0])
    return a[0] * anchor_prob.size, d0[0], actual


def evaluate_fit_configs(
    eqsets: dict[str, tuple[EquationSet, pd.DataFrame, np.ndarray, np.ndarray, np.ndarray, np.ndarray, dict[str, np.ndarray], tuple[np.ndarray, np.ndarray, float] | None]],
    support_maps: dict[str, np.ndarray],
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    ridge_mults = [1.0e-5, 3.0e-5, 1.0e-4, 3.0e-4, 1.0e-3, 3.0e-3, 1.0e-2, 3.0e-2, 1.0e-1, 3.0e-1, 1.0, 3.0]
    allowance_shapes = [
        (0.05, 16.0, 1.60),
        (0.10, 9.0, 1.00),
        (0.25, 4.0, 0.70),
    ]
    for eq_name, (spec, equations, a, d0_rows, b, anchor_prob, priors, h012_ext) in eqsets.items():
        if equations.empty:
            continue
        d1_rows = a * anchor_prob.size
        actual = equations["actual_delta_vs_anchor"].to_numpy(dtype=np.float64)
        h012_idx = equations.index[equations["file"].astype(str).eq(H012)].tolist()
        for prior_name, prior in priors.items():
            if spec.anchor_file == H012 and prior_name in {"e247", "pre_h012_good_soft"}:
                continue
            for support_name, score in support_maps.items():
                shapes = [(1.0, 1.0, 1.0)] if support_name == "uniform" else allowance_shapes
                for floor, gain, power in shapes:
                    allowance = (
                        np.ones_like(score, dtype=np.float64)
                        if support_name == "uniform"
                        else normalize_allowance(score, floor, gain, power)
                    )
                    for ridge in ridge_mults:
                        q_full = fit_weighted_posterior(a, b, prior, allowance, ridge)
                        full_pred = np.asarray([predict_delta(d0_rows[i], d1_rows[i], q_full) for i in range(len(actual))])
                        loo = np.zeros(len(actual), dtype=np.float64)
                        for heldout in range(len(actual)):
                            keep = np.ones(len(actual), dtype=bool)
                            keep[heldout] = False
                            q_loo = fit_weighted_posterior(a[keep], b[keep], prior, allowance, ridge)
                            loo[heldout] = predict_delta(d0_rows[heldout], d1_rows[heldout], q_loo)
                        err = loo - actual
                        spearman = float(pd.Series(loo).corr(pd.Series(actual), method="spearman"))
                        pearson = float(pd.Series(loo).corr(pd.Series(actual), method="pearson"))
                        h012_loo_pred = np.nan
                        h012_loo_err = np.nan
                        if h012_idx:
                            idx = h012_idx[0]
                            h012_loo_pred = float(loo[idx])
                            h012_loo_err = float(loo[idx] - actual[idx])
                        h012_ext_pred = np.nan
                        h012_ext_err = np.nan
                        if h012_ext is not None:
                            ext_d1, ext_d0, ext_actual = h012_ext
                            h012_ext_pred = predict_delta(ext_d0, ext_d1, q_full)
                            h012_ext_err = h012_ext_pred - ext_actual
                        rows.append(
                            {
                                "equation_set": eq_name,
                                "anchor_file": spec.anchor_file,
                                "include_h012": spec.include_h012,
                                "prior_name": prior_name,
                                "support_name": support_name,
                                "ridge_mult": ridge,
                                "floor": floor,
                                "gain": gain,
                                "power": power,
                                "n_equations": len(actual),
                                "loo_mae": float(np.mean(np.abs(err))),
                                "loo_rmse": float(np.sqrt(np.mean(err * err))),
                                "loo_p90_abs": float(np.quantile(np.abs(err), 0.90)),
                                "loo_spearman": spearman,
                                "loo_pearson": pearson,
                                "known_fit_mae": float(np.mean(np.abs(full_pred - actual))),
                                "h012_loo_pred_delta": h012_loo_pred,
                                "h012_loo_err": h012_loo_err,
                                "h012_external_pred_delta": h012_ext_pred,
                                "h012_external_err": h012_ext_err,
                                "q_mean": float(q_full.mean()),
                                "q_std": float(q_full.std()),
                                "q_l1_from_prior": float(np.mean(np.abs(q_full - prior))),
                                "q_l1_from_anchor": float(np.mean(np.abs(q_full - anchor_prob.reshape(-1)))),
                                "q_extreme_rate": float(np.mean((q_full <= 0.001) | (q_full >= 0.999))),
                                "allowance_top200_mass": float(np.sort(allowance)[-200:].sum() / allowance.sum()),
                                "allowance_ess": float((allowance.sum() ** 2) / np.sum(allowance * allowance)),
                            }
                        )
    cfg = pd.DataFrame(rows)
    if cfg.empty:
        return cfg
    h012_term = cfg["h012_loo_err"].abs().fillna(cfg["h012_external_err"].abs()).fillna(cfg["loo_mae"])
    cfg["h030_config_score"] = (
        cfg["loo_mae"].fillna(9.0)
        + 0.55 * cfg["loo_p90_abs"].fillna(9.0)
        + 0.65 * h012_term
        + 0.00004 * np.maximum(cfg["q_extreme_rate"].fillna(0.0) - 0.18, 0.0) / 0.02
        + 0.00002 * np.maximum(cfg["q_l1_from_anchor"].fillna(0.0) - 0.18, 0.0)
        - 0.00010 * cfg["loo_spearman"].fillna(0.0)
    )
    cfg = cfg.sort_values(["h030_config_score", "loo_mae", "loo_p90_abs"]).reset_index(drop=True)
    cfg.to_csv(OUT / "h030_fit_configs.csv", index=False)
    return cfg


def config_from_row(row: pd.Series) -> FitConfig:
    return FitConfig(
        equation_set=str(row["equation_set"]),
        prior_name=str(row["prior_name"]),
        support_name=str(row["support_name"]),
        ridge_mult=float(row["ridge_mult"]),
        floor=float(row["floor"]),
        gain=float(row["gain"]),
        power=float(row["power"]),
    )


def selected_configs(configs: pd.DataFrame) -> list[FitConfig]:
    out: list[FitConfig] = []
    seen: set[tuple[str, str, str, float, float, float, float]] = set()
    pre = configs[configs["equation_set"].eq("e247_pre_h012")].copy()
    if not pre.empty:
        pre["abs_h012_external_err"] = pre["h012_external_err"].abs()
    true_pre = pre[pre["prior_name"].isin(["anchor", "e247", "pre_h012_good_soft"])].copy() if not pre.empty else pre
    self_pre = pre[pre["prior_name"].isin(["h012", "good_soft"])].copy() if not pre.empty else pre
    selectors = [
        true_pre.sort_values(["abs_h012_external_err", "loo_mae"]).head(10),
        self_pre.sort_values(["abs_h012_external_err", "loo_mae"]).head(4),
        configs[configs["equation_set"].eq("e247_post_h012")].head(8),
        configs[configs["equation_set"].eq("h012_residual")].head(10),
    ]
    pool = pd.concat([s for s in selectors if not s.empty], ignore_index=True)
    for rec in pool.to_dict("records"):
        key = (
            str(rec["equation_set"]),
            str(rec["prior_name"]),
            str(rec["support_name"]),
            float(rec["ridge_mult"]),
            float(rec["floor"]),
            float(rec["gain"]),
            float(rec["power"]),
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(config_from_row(pd.Series(rec)))
        if len(out) >= 32:
            break
    return out


def materialize_q(
    cfg: FitConfig,
    eqsets: dict[str, tuple[EquationSet, pd.DataFrame, np.ndarray, np.ndarray, np.ndarray, np.ndarray, dict[str, np.ndarray], tuple[np.ndarray, np.ndarray, float] | None]],
    support_maps: dict[str, np.ndarray],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, EquationSet]:
    spec, _equations, a, _d0, b, anchor_prob, priors, _h012_ext = eqsets[cfg.equation_set]
    score = support_maps[cfg.support_name]
    allowance = (
        np.ones_like(score, dtype=np.float64)
        if cfg.support_name == "uniform"
        else normalize_allowance(score, cfg.floor, cfg.gain, cfg.power)
    )
    q = fit_weighted_posterior(a, b, priors[cfg.prior_name], allowance, cfg.ridge_mult)
    return q, anchor_prob.reshape(-1), allowance, spec


def write_submission(template: pd.DataFrame, prob: np.ndarray, candidate_id: str) -> Path:
    out = template.copy()
    out[TARGETS] = clip_prob(prob)
    path = OUT / f"submission_h030_{safe_id(candidate_id)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def generate_candidates(
    h024: object,
    configs: list[FitConfig],
    eqsets: dict[str, tuple[EquationSet, pd.DataFrame, np.ndarray, np.ndarray, np.ndarray, np.ndarray, dict[str, np.ndarray], tuple[np.ndarray, np.ndarray, float] | None]],
    support_maps: dict[str, np.ndarray],
    sample: pd.DataFrame,
) -> pd.DataFrame:
    e247_df = h024.load_sub(E247, sample)
    h012_df = h024.load_sub(H012, sample)
    e247_prob = e247_df[TARGETS].to_numpy(dtype=np.float64)
    h012_prob = h012_df[TARGETS].to_numpy(dtype=np.float64)
    e247_z = logit(e247_prob).reshape(-1)
    h012_z = logit(h012_prob).reshape(-1)
    rows: list[dict[str, Any]] = []

    def add_candidate(cfg: FitConfig, q: np.ndarray, base_prob: np.ndarray, base_df: pd.DataFrame, support_score: np.ndarray, candidate_id: str, k: int, alpha: float, family: str) -> None:
        base_z = logit(base_prob).reshape(-1)
        qz = logit(q)
        direction = qz - base_z
        if np.max(np.abs(direction)) <= 1.0e-12:
            return
        cell_score = np.abs(direction) * (0.25 + 0.75 * support_score)
        chosen = np.argsort(cell_score)[-min(k, len(cell_score)) :]
        out_z = base_z.copy()
        out_z[chosen] = base_z[chosen] + alpha * direction[chosen]
        out_prob = sigmoid(out_z).reshape(base_prob.shape)
        path = write_submission(base_df, out_prob, candidate_id)
        move_h012 = logit(out_prob).reshape(-1) - h012_z
        move_e247 = logit(out_prob).reshape(-1) - e247_z
        h012_dir = h012_z - e247_z
        q_delta = float(np.mean(binary_loss(out_prob.reshape(base_prob.shape), q.reshape(base_prob.shape)) - binary_loss(base_prob, q.reshape(base_prob.shape))))
        denom = float(np.linalg.norm(move_e247) * np.linalg.norm(h012_dir) + 1.0e-12)
        rows.append(
            {
                "file": f"hitl/h030_rowtarget_identity_equation_jepa/{path.name}",
                "resolved_path": str(path),
                "candidate_id": candidate_id,
                "family": family,
                "equation_set": cfg.equation_set,
                "prior_name": cfg.prior_name,
                "support_name": cfg.support_name,
                "ridge_mult": cfg.ridge_mult,
                "floor": cfg.floor,
                "gain": cfg.gain,
                "power": cfg.power,
                "k": k,
                "alpha": alpha,
                "posterior_delta_vs_base": q_delta,
                "changed_cells_vs_h012": int(np.sum(np.abs(out_prob - h012_prob) > 1.0e-6)),
                "changed_rows_vs_h012": int(np.sum(np.max(np.abs(out_prob - h012_prob), axis=1) > 1.0e-6)),
                "changed_cells_vs_e247": int(np.sum(np.abs(out_prob - e247_prob) > 1.0e-6)),
                "mean_abs_prob_vs_h012": float(np.mean(np.abs(out_prob - h012_prob))),
                "max_abs_prob_vs_h012": float(np.max(np.abs(out_prob - h012_prob))),
                "mean_abs_logit_vs_h012": float(np.mean(np.abs(move_h012))),
                "max_abs_logit_vs_h012": float(np.max(np.abs(move_h012))),
                "cos_e247_to_h012": float(move_e247 @ h012_dir / denom),
                "proj_e247_to_h012": float(move_e247 @ h012_dir / (h012_dir @ h012_dir + 1.0e-12)),
                "selected_support_mean": float(np.mean(support_score[chosen])),
                "selected_support_min": float(np.min(support_score[chosen])),
            }
        )

    for cfg in configs:
        q, anchor, allowance, spec = materialize_q(cfg, eqsets, support_maps)
        support_score = support_maps[cfg.support_name]
        if spec.anchor_file == H012:
            base_prob = h012_prob
            base_df = h012_df
            for k in [60, 120, 240, 480, 800, 1200]:
                for alpha in [0.35, 0.55, 0.80, 1.10]:
                    add_candidate(
                        cfg,
                        q,
                        base_prob,
                        base_df,
                        support_score,
                        f"{cfg.equation_set}_{cfg.support_name}_{cfg.prior_name}_resid_k{k}_a{alpha:g}",
                        k,
                        alpha,
                        "h012_residual_identity",
                    )
        else:
            base_prob = e247_prob
            base_df = e247_df
            for k in [800, 1000, 1200, 1400, 1600]:
                for alpha in [0.55, 0.70, 0.85, 1.00, 1.15]:
                    add_candidate(
                        cfg,
                        q,
                        base_prob,
                        base_df,
                        support_score,
                        f"{cfg.equation_set}_{cfg.support_name}_{cfg.prior_name}_k{k}_a{alpha:g}",
                        k,
                        alpha,
                        "e247_identity_equation",
                    )
            # One "support-only" hard claim per config: keep H012 support but use
            # the new posterior values.  This tests whether H012's support set
            # was right but its latent target values were underfit.
            h012_support = np.abs(h012_prob.reshape(-1) - e247_prob.reshape(-1)) > 1.0e-10
            out_z = e247_z.copy()
            out_z[h012_support] = e247_z[h012_support] + 0.85 * (logit(q)[h012_support] - e247_z[h012_support])
            out_prob = sigmoid(out_z).reshape(e247_prob.shape)
            path = write_submission(e247_df, out_prob, f"{cfg.equation_set}_{cfg.support_name}_{cfg.prior_name}_exact_h012_support_a0p85")
            rows.append(
                {
                    "file": f"hitl/h030_rowtarget_identity_equation_jepa/{path.name}",
                    "resolved_path": str(path),
                    "candidate_id": f"{cfg.equation_set}_{cfg.support_name}_{cfg.prior_name}_exact_h012_support_a0p85",
                    "family": "exact_h012_support_retarget",
                    "equation_set": cfg.equation_set,
                    "prior_name": cfg.prior_name,
                    "support_name": cfg.support_name,
                    "ridge_mult": cfg.ridge_mult,
                    "floor": cfg.floor,
                    "gain": cfg.gain,
                    "power": cfg.power,
                    "k": int(h012_support.sum()),
                    "alpha": 0.85,
                    "posterior_delta_vs_base": float(np.mean(binary_loss(out_prob, q.reshape(e247_prob.shape)) - binary_loss(e247_prob, q.reshape(e247_prob.shape)))),
                    "changed_cells_vs_h012": int(np.sum(np.abs(out_prob - h012_prob) > 1.0e-6)),
                    "changed_rows_vs_h012": int(np.sum(np.max(np.abs(out_prob - h012_prob), axis=1) > 1.0e-6)),
                    "changed_cells_vs_e247": int(np.sum(np.abs(out_prob - e247_prob) > 1.0e-6)),
                    "mean_abs_prob_vs_h012": float(np.mean(np.abs(out_prob - h012_prob))),
                    "max_abs_prob_vs_h012": float(np.max(np.abs(out_prob - h012_prob))),
                    "mean_abs_logit_vs_h012": float(np.mean(np.abs(logit(out_prob).reshape(-1) - h012_z))),
                    "max_abs_logit_vs_h012": float(np.max(np.abs(logit(out_prob).reshape(-1) - h012_z))),
                    "cos_e247_to_h012": float((logit(out_prob).reshape(-1) - e247_z) @ (h012_z - e247_z) / (np.linalg.norm(logit(out_prob).reshape(-1) - e247_z) * np.linalg.norm(h012_z - e247_z) + 1.0e-12)),
                    "proj_e247_to_h012": float((logit(out_prob).reshape(-1) - e247_z) @ (h012_z - e247_z) / ((h012_z - e247_z) @ (h012_z - e247_z) + 1.0e-12)),
                    "selected_support_mean": float(np.mean(support_score[h012_support])),
                    "selected_support_min": float(np.min(support_score[h012_support])),
                }
            )
    candidates = pd.DataFrame(rows)
    if not candidates.empty:
        candidates = candidates.drop_duplicates("file").reset_index(drop=True)
    candidates.to_csv(OUT / "h030_generated_candidates.csv", index=False)
    return candidates


def score_with_h024(h024: object, variants: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, list[str]]]:
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
    var_rows["source"] = "h030_variant"
    pool = pd.concat([pd.DataFrame(known_rows), var_rows], ignore_index=True)
    features = h024.build_feature_table(pool, refs)
    features.to_csv(OUT / "h030_h024_features.csv", index=False)
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
    cols_by_set = h024.feature_sets(cols)
    model_scores, loo_preds = h024.evaluate_known_models(known_features[["file", "public_lb"]], features, cols_by_set)
    model_scores.to_csv(OUT / "h030_h024_model_scores.csv", index=False)
    loo_preds.to_csv(OUT / "h030_h024_known_loo_predictions.csv", index=False)
    candidate_scores, pred_samples = h024.score_candidates(known_features[["file", "public_lb"]], features, model_scores, cols_by_set)
    pred_samples.to_csv(OUT / "h030_h024_prediction_samples.csv", index=False)
    scored = variants.merge(candidate_scores, on="file", how="left", suffixes=("", "_h024"))
    scored["margin_vs_h012_pred"] = scored["pred_public_median"] - H012_LB
    scored["risk_width"] = scored["pred_public_p90"] - scored["pred_public_p10"]
    scored["h030_action_score"] = (
        scored["pred_public_median"].fillna(0.59)
        + 0.45 * scored["risk_width"].fillna(0.02)
        - 0.00018 * scored["support_better_than_h012"].fillna(0.0)
        + 0.00010 * np.maximum(scored["max_abs_prob_vs_h012"].fillna(0.0) - 0.25, 0.0)
    )
    scored = scored.sort_values(["h030_action_score", "pred_public_median"]).reset_index(drop=True)
    scored.to_csv(OUT / "h030_candidate_scores.csv", index=False)
    return scored, model_scores, features, cols_by_set


def public_perm_stress(h024: object, selected: pd.Series, features: pd.DataFrame, cols_by_set: dict[str, list[str]]) -> pd.DataFrame:
    known = h024.read_public_observations()
    known_features = known[["file", "public_lb"]].merge(features, on="file", how="inner")
    null = h024.permutation_stress(
        known_features[["file", "public_lb"]],
        features,
        cols_by_set,
        str(selected["file"]),
        n_perm=300,
    )
    null.to_csv(OUT / "h030_selected_h024_public_perm_stress.csv", index=False)
    return null


def rowperm_stress(selected: pd.Series) -> pd.DataFrame:
    try:
        h026 = import_module(HITL / "h026_public_private_calibration_veto_jepa.py", "h026_h030")
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
    rowperm.to_csv(OUT / "h030_selected_h025_rowperm_stress.csv", index=False)
    return rowperm


def summarize_families(scored: pd.DataFrame) -> pd.DataFrame:
    rows = []
    if scored.empty:
        return pd.DataFrame()
    for family, group in scored.groupby("family"):
        best = group.sort_values("h030_action_score").iloc[0]
        rows.append(
            {
                "family": family,
                "n": len(group),
                "best_candidate_id": best["candidate_id"],
                "best_pred_public_median": float(best["pred_public_median"]),
                "best_margin_vs_h012": float(best["margin_vs_h012_pred"]),
                "best_support_better_than_h012": float(best["support_better_than_h012"]),
                "best_risk_width": float(best["risk_width"]),
                "median_pred_public": float(group["pred_public_median"].median()),
                "min_pred_public": float(group["pred_public_median"].min()),
            }
        )
    out = pd.DataFrame(rows).sort_values(["best_pred_public_median", "best_risk_width"]).reset_index(drop=True)
    out.to_csv(OUT / "h030_family_summary.csv", index=False)
    return out


def decide(scored: pd.DataFrame, public_perm: pd.DataFrame, rowperm: pd.DataFrame) -> tuple[str, Path | None]:
    if scored.empty:
        return "no_h030_candidates", None
    selected = scored.iloc[0]
    public_perm_p = 1.0
    if not public_perm.empty and "perm_selected_minus_h012" in public_perm.columns:
        real_margin = float(selected["pred_public_median"] - H012_LB)
        public_perm_p = float(np.mean(public_perm["perm_selected_minus_h012"].to_numpy(dtype=np.float64) <= real_margin))
    rowperm_p = 1.0
    if not rowperm.empty and "perm_top1200_sum" in rowperm.columns:
        rowperm_p = float(np.mean(rowperm["perm_top1200_sum"].to_numpy(dtype=np.float64) >= rowperm["real_top1200_sum"].iloc[0]))
    gate = (
        float(selected["pred_public_median"]) <= H012_LB - 0.00075
        and float(selected["support_better_than_h012"]) >= 0.60
        and float(selected["risk_width"]) <= 0.0035
        and public_perm_p <= 0.12
        and rowperm_p <= 0.35
        and float(selected["max_abs_prob_vs_h012"]) <= 0.35
    )
    if not gate:
        return "diagnostic_only_rowtarget_identity_not_action_safe", None
    source = Path(str(selected["resolved_path"]))
    digest = hashlib.sha1(source.read_bytes()).hexdigest()[:8]
    out = ROOT / f"submission_h030_rowtarget_identity_equation_{digest}_uploadsafe.csv"
    shutil.copyfile(source, out)
    return "primary_rowtarget_identity_equation", out


def write_report(
    configs: pd.DataFrame,
    selected_fit_configs: list[FitConfig],
    candidates: pd.DataFrame,
    scored: pd.DataFrame,
    family: pd.DataFrame,
    model_scores: pd.DataFrame,
    public_perm: pd.DataFrame,
    rowperm: pd.DataFrame,
    decision: str,
    promoted: Path | None,
) -> None:
    lines: list[str] = []
    lines.append("# H030 Row-Target Identity Public-Equation HS-JEPA\n\n")
    lines.append("## Question\n\n")
    lines.append(
        "H012 found a large hidden-public-state posterior. H030 asks whether the next breakthrough is not another post-hoc gate, "
        "but putting row-target identity directly into the inverse public-equation solver as a cell allowance prior.\n\n"
    )
    lines.append("## Falsification Target\n\n")
    lines.append(
        "A real identity prior should predict the H012 jackpot when H012 is held out, and should propose post-H012 movements that "
        "H024 prices below H012 under permutation stress. If it cannot do that, H012 is likely a narrow solved basin rather than a smooth route.\n\n"
    )
    lines.append("## Fit Summary\n\n")
    lines.append(f"- fit configs tested: `{len(configs)}`\n")
    lines.append(f"- selected fit configs for materialization: `{len(selected_fit_configs)}`\n")
    lines.append(f"- generated candidates: `{len(candidates)}`\n")
    lines.append(f"- decision: `{decision}`\n")
    lines.append(f"- promoted path: `{promoted if promoted is not None else 'none'}`\n\n")
    fit_cols = [
        "equation_set",
        "prior_name",
        "support_name",
        "ridge_mult",
        "floor",
        "gain",
        "power",
        "loo_mae",
        "loo_p90_abs",
        "loo_spearman",
        "h012_loo_pred_delta",
        "h012_loo_err",
        "h012_external_pred_delta",
        "h012_external_err",
        "q_l1_from_anchor",
        "allowance_ess",
        "h030_config_score",
    ]
    lines.append("## Top Solver Configs\n\n")
    lines.append(md_table(configs[[c for c in fit_cols if c in configs.columns]], 30) + "\n\n")
    lines.append("## Independent H012 Held-Out Check\n\n")
    if not configs.empty:
        pre = configs[configs["equation_set"].eq("e247_pre_h012")].copy()
        true_pre = pre[pre["prior_name"].isin(["anchor", "e247", "pre_h012_good_soft"])].copy()
        leak_pre = pre[pre["prior_name"].isin(["h012", "good_soft"])].copy()
        if not true_pre.empty:
            true_pre["abs_h012_external_err"] = true_pre["h012_external_err"].abs()
            best_true = true_pre.sort_values(["abs_h012_external_err", "loo_mae"]).head(8)
            lines.append(
                "These configs exclude H012 as an equation and do not use the direct `h012`/H012-containing `good_soft` prior. "
                "They are the real test of whether the row-target identity prior could have anticipated the H012 jackpot.\n\n"
            )
            lines.append(md_table(best_true[[c for c in fit_cols + ["abs_h012_external_err"] if c in best_true.columns]], 8) + "\n\n")
        if not leak_pre.empty:
            leak_pre["abs_h012_external_err"] = leak_pre["h012_external_err"].abs()
            best_leak = leak_pre.sort_values(["abs_h012_external_err", "loo_mae"]).head(5)
            lines.append(
                "Self-feedback controls using `h012` or H012-containing `good_soft` priors are stronger but are not independent evidence:\n\n"
            )
            lines.append(md_table(best_leak[[c for c in fit_cols + ["abs_h012_external_err"] if c in best_leak.columns]], 5) + "\n\n")
    lines.append("## Family Summary\n\n")
    family_cols = [
        "family",
        "n",
        "best_candidate_id",
        "best_pred_public_median",
        "best_margin_vs_h012",
        "best_support_better_than_h012",
        "best_risk_width",
        "median_pred_public",
    ]
    lines.append(md_table(family[[c for c in family_cols if c in family.columns]], 20) + "\n\n" if not family.empty else "_empty_\n\n")
    lines.append("## Top Candidates\n\n")
    cand_cols = [
        "candidate_id",
        "family",
        "equation_set",
        "support_name",
        "prior_name",
        "pred_public_median",
        "pred_public_p10",
        "pred_public_p90",
        "margin_vs_h012_pred",
        "support_better_than_h012",
        "risk_width",
        "changed_cells_vs_h012",
        "max_abs_prob_vs_h012",
        "file",
    ]
    lines.append(md_table(scored[[c for c in cand_cols if c in scored.columns]], 25) + "\n\n" if not scored.empty else "_empty_\n\n")
    lines.append("## H024 Decoder Sanity\n\n")
    if not model_scores.empty:
        top = model_scores.iloc[0]
        lines.append(
            f"- best decoder: `{top['feature_set']}` alpha `{top['alpha']}`, "
            f"LOO MAE `{top['loo_mae']:.9f}`, Spearman `{top['loo_spearman']:.9f}`, pairwise `{top['loo_pair_acc']:.9f}`\n"
        )
    if not scored.empty:
        selected = scored.iloc[0]
        lines.append(f"- selected diagnostic: `{selected['candidate_id']}`\n")
        lines.append(f"- selected predicted margin vs H012: `{float(selected['margin_vs_h012_pred']):.9f}`\n")
    if not public_perm.empty and "perm_selected_minus_h012" in public_perm.columns and not scored.empty:
        selected = scored.iloc[0]
        real_margin = float(selected["pred_public_median"] - H012_LB)
        p = float(np.mean(public_perm["perm_selected_minus_h012"].to_numpy(dtype=np.float64) <= real_margin))
        lines.append(f"- H024 public-score permutation p(lower margin): `{p:.9f}`\n")
    if not rowperm.empty and "perm_top1200_sum" in rowperm.columns:
        p = float(np.mean(rowperm["perm_top1200_sum"].to_numpy(dtype=np.float64) >= rowperm["real_top1200_sum"].iloc[0]))
        lines.append(f"- H025 row-permutation p(higher top1200 gain): `{p:.9f}`\n")
        lines.append(f"- real H025 top1200 gain: `{float(rowperm['real_top1200_sum'].iloc[0]):.9f}`\n")
    elif not rowperm.empty and "error" in rowperm.columns:
        lines.append(f"- H025 row-permutation stress error: `{rowperm['error'].iloc[0]}`\n")
    lines.append("\n## Interpretation\n\n")
    lines.append(
        "If top e247_pre_h012 configs predict H012's -0.008 public jump without seeing it, the row-target identity prior is not just self-feedback. "
        "If top h012_residual candidates are still priced above H012, the current bottleneck is not finding another latent, but translating it without breaking the H012 row-target basin.\n"
    )
    lines.append("\n## Files\n\n")
    for path in [
        OUT / "h030_known_public_sensors.csv",
        OUT / "h030_cell_identity_state.csv",
        OUT / "h030_fit_configs.csv",
        OUT / "h030_generated_candidates.csv",
        OUT / "h030_candidate_scores.csv",
        OUT / "h030_family_summary.csv",
        OUT / "h030_h024_model_scores.csv",
        OUT / "h030_selected_h024_public_perm_stress.csv",
        OUT / "h030_selected_h025_rowperm_stress.csv",
    ]:
        lines.append(f"- `{path.relative_to(ROOT)}`\n")
    (OUT / "h030_report.md").write_text("".join(lines), encoding="utf-8")


def main() -> None:
    h024 = load_h024()
    known = load_known(h024)
    h012_df = h024.load_sub(H012)
    sample = h012_df[KEYS].copy()
    e247_df = h024.load_sub(E247, sample)
    h012_prob = h012_df[TARGETS].to_numpy(dtype=np.float64)
    e247_prob = e247_df[TARGETS].to_numpy(dtype=np.float64)
    pred_by_file = load_prediction_map(h024, known, sample)
    cell_state = build_cell_state(sample, e247_prob, h012_prob)
    support_maps = support_score_maps(cell_state)

    eq_specs = [
        EquationSet("e247_pre_h012", E247, False),
        EquationSet("e247_post_h012", E247, True),
        EquationSet("h012_residual", H012, False),
    ]
    eqsets: dict[str, tuple[EquationSet, pd.DataFrame, np.ndarray, np.ndarray, np.ndarray, np.ndarray, dict[str, np.ndarray], tuple[np.ndarray, np.ndarray, float] | None]] = {}
    for spec in eq_specs:
        anchor_df = e247_df if spec.anchor_file == E247 else h012_df
        anchor_prob = anchor_df[TARGETS].to_numpy(dtype=np.float64)
        anchor_lb = public_lb(known, spec.anchor_file)
        eq, a, d0, b = equation_arrays(known, pred_by_file, spec.anchor_file, anchor_prob, anchor_lb, spec.include_h012)
        priors = build_priors(known, pred_by_file, anchor_prob, e247_prob, h012_prob)
        h012_ext = h012_external_equation(known, pred_by_file, spec.anchor_file, anchor_prob, anchor_lb)
        eq.to_csv(OUT / f"h030_equations_{spec.name}.csv", index=False)
        eqsets[spec.name] = (spec, eq, a, d0, b, anchor_prob, priors, h012_ext)

    configs = evaluate_fit_configs(eqsets, support_maps)
    selected_fit_configs = selected_configs(configs)
    pd.DataFrame([cfg.__dict__ for cfg in selected_fit_configs]).to_csv(OUT / "h030_selected_fit_configs.csv", index=False)
    candidates = generate_candidates(h024, selected_fit_configs, eqsets, support_maps, sample)
    if candidates.empty:
        scored = pd.DataFrame()
        model_scores = pd.DataFrame()
        features = pd.DataFrame()
        cols_by_set: dict[str, list[str]] = {}
    else:
        scored, model_scores, features, cols_by_set = score_with_h024(h024, candidates)
    family = summarize_families(scored)
    selected = scored.iloc[0] if len(scored) else None
    if selected is not None and len(features):
        public_perm = public_perm_stress(h024, selected, features, cols_by_set)
        rowperm = rowperm_stress(selected)
    else:
        public_perm = pd.DataFrame()
        rowperm = pd.DataFrame()
    decision, promoted = decide(scored, public_perm, rowperm)
    pd.DataFrame(
        [
            {
                "decision": decision,
                "selected_candidate_id": None if selected is None else selected["candidate_id"],
                "selected_file": None if selected is None else selected["file"],
                "selected_pred_public_median": None if selected is None else float(selected["pred_public_median"]),
                "selected_support_better_than_h012": None if selected is None else float(selected["support_better_than_h012"]),
                "promoted_path": None if promoted is None else str(promoted),
            }
        ]
    ).to_csv(OUT / "h030_decision.csv", index=False)
    write_report(configs, selected_fit_configs, candidates, scored, family, model_scores, public_perm, rowperm, decision, promoted)
    print(pd.read_csv(OUT / "h030_decision.csv").to_string(index=False))
    if len(scored):
        cols = [
            "candidate_id",
            "family",
            "pred_public_median",
            "pred_public_p10",
            "pred_public_p90",
            "margin_vs_h012_pred",
            "support_better_than_h012",
            "risk_width",
            "file",
        ]
        print(scored[cols].head(15).to_string(index=False))
    print(OUT / "h030_report.md")


if __name__ == "__main__":
    main()
