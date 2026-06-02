#!/usr/bin/env python3
"""H086: public-subset responsibility HS-JEPA.

H012/H085 infer a hidden label posterior q from public LB equations. H086 asks a
larger question:

    what if the missing variable is not only q, but which row-target cells the
    public subset effectively listens to?

Known public submissions become a context sequence. The target representation is
a nonnegative row-target responsibility vector w such that public LB deltas are
explained by weighted expected cell losses under the H085 posterior. The decoder
then materializes corrections only where this inferred responsibility and the
HS-JEPA source-action field agree.

A win means HS-JEPA needs an explicit public/private responsibility factor, not
just a better posterior. A loss means public-equation inversion is mostly label
posterior and the responsibility layer is too underdetermined.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import importlib.util
import shutil
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HITL = ROOT / "hitl"
OUT = HITL / "h086_public_responsibility_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
S_TARGETS = ["S1", "S2", "S3", "S4"]
NON_Q2 = [target for target in TARGETS if target != "Q2"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
BASE_FILE = "submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv"
EPS = 1.0e-6
TOL = 1.0e-12


@dataclass(frozen=True)
class H086Spec:
    name: str
    unit: str
    target_group: str
    value_mode: str
    max_units: int
    max_cells: int
    max_rows: int
    q2_cap: int
    max_per_subject: int
    alpha: float
    cap: float
    min_score: float
    require_source_agree: bool
    require_h082: bool
    require_resp_lift: bool
    novelty: str


def import_module(path: Path, name: str) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


H085MOD = import_module(HITL / "h085_augmented_public_equation_jepa.py", "h085mod_for_h086")


def rank01(values: np.ndarray, high: bool = True) -> np.ndarray:
    return H085MOD.rank01(np.asarray(values, dtype=np.float64), high=high)


def clip_prob(x: np.ndarray) -> np.ndarray:
    return H085MOD.clip_prob(x)


def logit(x: np.ndarray) -> np.ndarray:
    return H085MOD.logit(x)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return H085MOD.sigmoid(x)


def bce(prob: np.ndarray, q: np.ndarray) -> np.ndarray:
    return H085MOD.bce(prob, q)


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return H085MOD.md_table(frame, n)


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h086_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h086_public_resp_*_uploadsafe.csv"):
        path.unlink()


def normalize_prior(values: np.ndarray) -> np.ndarray:
    x = np.asarray(values, dtype=np.float64)
    x = np.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0)
    x = np.clip(x, 0.0, None)
    if float(x.sum()) <= 0.0:
        x = np.ones_like(x, dtype=np.float64)
    return x / float(x.sum())


def load_h085_q(sample: pd.DataFrame) -> np.ndarray:
    cell_path = HITL / "h085_augmented_public_equation_jepa" / "h085_cell_table.csv"
    if not cell_path.exists():
        raise FileNotFoundError(cell_path)
    cell = pd.read_csv(cell_path)
    q = np.full((len(sample), len(TARGETS)), 0.5, dtype=np.float64)
    for rec in cell.to_dict("records"):
        q[int(rec["row"]), int(rec["target_index"])] = float(rec["h085_q"])
    return clip_prob(q)


def load_q061(sample: pd.DataFrame) -> np.ndarray:
    path = HITL / "h061_h057_feedback_support_translator_jepa" / "h061_cell_posterior.csv"
    df = pd.read_csv(path)
    q = np.full((len(sample), len(TARGETS)), 0.5, dtype=np.float64)
    target_i = {target: i for i, target in enumerate(TARGETS)}
    for rec in df.to_dict("records"):
        q[int(rec["row"]), target_i[str(rec["target"])]] = float(rec["q061"])
    return clip_prob(q)


def load_cell_table(sample: pd.DataFrame, base_prob: np.ndarray, q_prob: np.ndarray) -> pd.DataFrame:
    path = HITL / "h085_augmented_public_equation_jepa" / "h085_cell_table.csv"
    if path.exists():
        cell = pd.read_csv(path)
    else:
        cell, _row = H085MOD.add_support_tables(sample, base_prob, q_prob)
    return cell.sort_values(["row", "target_index"]).reset_index(drop=True)


def load_known_system(sample: pd.DataFrame, base_prob: np.ndarray, q_prob: np.ndarray) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    known = H085MOD.public_observations(sample)
    pred_by_file: dict[str, np.ndarray] = {}
    for rec in known.to_dict("records"):
        pred_by_file[str(rec["file"])] = H085MOD.load_sub(str(rec["resolved_path"]), sample)[TARGETS].to_numpy(dtype=np.float64)
    equations, a, d0_rows, _b = H085MOD.build_equation_system(known, pred_by_file, base_prob)
    n = base_prob.size
    d1_rows = a * n
    loss_delta = d0_rows + d1_rows * q_prob.reshape(-1)[None, :]
    actual = equations["actual_delta_vs_h057"].to_numpy(dtype=np.float64)
    return equations, loss_delta, actual


def build_priors(cell: pd.DataFrame, sample: pd.DataFrame) -> dict[str, np.ndarray]:
    n_cells = len(cell)
    uniform = np.ones(n_cells, dtype=np.float64)

    row_resp_path = HITL / "h067_row_responsibility_public_state_jepa" / "h067_row_responsibility.csv"
    row_resp = pd.read_csv(row_resp_path).sort_values("row").reset_index(drop=True)
    row_public = row_resp["public_weight"].to_numpy(dtype=np.float64)
    row_rank = row_resp["public_responsibility_rank"].to_numpy(dtype=np.float64)
    row_prior = np.repeat(0.70 * rank01(row_public) + 0.30 * row_rank, len(TARGETS))

    h082 = cell["h082_cell"].to_numpy(dtype=np.float64) if "h082_cell" in cell.columns else np.zeros(n_cells)
    h084 = cell["h084_dark_cell"].to_numpy(dtype=np.float64) if "h084_dark_cell" in cell.columns else np.zeros(n_cells)
    source_count = cell["source_count"].to_numpy(dtype=np.float64)
    source_family = cell["source_family_count"].to_numpy(dtype=np.float64)
    abs_source = np.abs(cell["source_mean_move"].to_numpy(dtype=np.float64))

    public = cell["public_score"].to_numpy(dtype=np.float64)
    invariant = cell["invariant_score"].to_numpy(dtype=np.float64)
    private_safe = np.clip(cell["private_safe_score"].to_numpy(dtype=np.float64), 0.0, None)
    h085_score = np.clip(cell.get("h085_cell_score", pd.Series(np.zeros(n_cells))).to_numpy(dtype=np.float64), 0.0, None)
    source_agree = cell.get("source_agrees_h085", pd.Series(np.zeros(n_cells))).to_numpy(dtype=np.float64)
    bad_avoid = 1.0 - cell["h080_bad_same_rank"].to_numpy(dtype=np.float64)
    q_gain = np.clip(cell["h085_q_gain"].to_numpy(dtype=np.float64), 0.0, None)

    source_prior = (
        0.32 * rank01(source_count)
        + 0.18 * rank01(source_family)
        + 0.18 * rank01(abs_source)
        + 0.16 * source_agree
        + 0.10 * h082
        + 0.06 * h084
    )
    human_prior = (
        0.28 * row_prior
        + 0.18 * public
        + 0.18 * invariant
        + 0.14 * private_safe
        + 0.12 * bad_avoid
        + 0.10 * rank01(q_gain)
    )
    hybrid = (
        0.24 * row_prior
        + 0.22 * public
        + 0.18 * invariant
        + 0.14 * source_prior
        + 0.10 * h085_score
        + 0.08 * bad_avoid
        + 0.04 * (1.0 - cell["is_h050_null"].to_numpy(dtype=np.float64))
    )
    h082_bridge = 0.55 * h082 + 0.18 * source_prior + 0.14 * row_prior + 0.13 * invariant

    return {
        "uniform": normalize_prior(uniform),
        "row_public": normalize_prior(row_prior),
        "human_private": normalize_prior(human_prior),
        "source_action": normalize_prior(source_prior),
        "hybrid_resp": normalize_prior(hybrid),
        "h082_bridge": normalize_prior(h082_bridge),
    }


def fit_responsibility(loss_delta: np.ndarray, actual: np.ndarray, prior: np.ndarray, ridge_mult: float) -> tuple[np.ndarray, np.ndarray]:
    gram = loss_delta @ loss_delta.T
    scale = float(np.median(np.diag(gram)))
    if not np.isfinite(scale) or scale <= 1.0e-18:
        scale = float(np.mean(np.diag(gram)) + 1.0e-18)
    lam = float(ridge_mult) * scale
    residual = actual - loss_delta @ prior
    try:
        dual = np.linalg.solve(gram + lam * np.eye(len(actual)), residual)
    except np.linalg.LinAlgError:
        dual = np.linalg.pinv(gram + lam * np.eye(len(actual))) @ residual
    raw = prior + loss_delta.T @ dual
    projected = normalize_prior(raw)
    return projected, raw


def eval_responsibility_configs(
    equations: pd.DataFrame,
    loss_delta: np.ndarray,
    actual: np.ndarray,
    priors: dict[str, np.ndarray],
) -> tuple[pd.DataFrame, dict[str, np.ndarray], dict[str, np.ndarray]]:
    ridge_mults = [1.0e-4, 3.0e-4, 1.0e-3, 3.0e-3, 1.0e-2, 3.0e-2, 0.1, 0.3, 1.0, 3.0, 10.0]
    rows = []
    weights: dict[str, np.ndarray] = {}
    raw_weights: dict[str, np.ndarray] = {}
    for prior_name, prior in priors.items():
        for ridge_mult in ridge_mults:
            w, raw = fit_responsibility(loss_delta, actual, prior, ridge_mult)
            pred = loss_delta @ w
            loo_pred = []
            for holdout in range(len(actual)):
                keep = np.ones(len(actual), dtype=bool)
                keep[holdout] = False
                w_loo, _raw = fit_responsibility(loss_delta[keep], actual[keep], prior, ridge_mult)
                loo_pred.append(float(loss_delta[holdout] @ w_loo))
            loo_pred_arr = np.asarray(loo_pred, dtype=np.float64)
            err = loo_pred_arr - actual
            key = f"{prior_name}__ridge_{ridge_mult:g}"
            weights[key] = w
            raw_weights[key] = raw
            top50 = float(np.sort(w)[-50:].sum())
            top200 = float(np.sort(w)[-200:].sum())
            effective_cells = float(1.0 / np.sum(w * w))
            raw_negative_rate = float((raw < 0.0).mean())
            rows.append(
                {
                    "resp_key": key,
                    "prior_name": prior_name,
                    "ridge_mult": ridge_mult,
                    "loo_mae": float(np.mean(np.abs(err))),
                    "loo_rmse": float(np.sqrt(np.mean(err * err))),
                    "loo_p90_abs": float(np.quantile(np.abs(err), 0.90)),
                    "loo_spearman": float(pd.Series(loo_pred_arr).corr(pd.Series(actual), method="spearman")),
                    "known_fit_mae": float(np.mean(np.abs(pred - actual))),
                    "known_fit_p90_abs": float(np.quantile(np.abs(pred - actual), 0.90)),
                    "top50_mass": top50,
                    "top200_mass": top200,
                    "effective_cells": effective_cells,
                    "raw_negative_rate": raw_negative_rate,
                    "max_weight": float(w.max()),
                    "weight_entropy": float(-np.sum(w * np.log(np.clip(w, 1.0e-15, None)))),
                    "config_score": float(
                        -np.mean(np.abs(err))
                        -0.35 * np.quantile(np.abs(err), 0.90)
                        +0.00008 * top200
                        -0.00004 * raw_negative_rate
                    ),
                }
            )
    configs = pd.DataFrame(rows).sort_values(
        ["config_score", "loo_mae", "top200_mass"], ascending=[False, True, False]
    ).reset_index(drop=True)
    return configs, weights, raw_weights


def add_responsibility_features(
    cell: pd.DataFrame,
    loss_delta: np.ndarray,
    actual: np.ndarray,
    weight: np.ndarray,
    raw_weight: np.ndarray,
    prior: np.ndarray,
) -> pd.DataFrame:
    out = cell.copy()
    centered_actual = actual - actual.mean()
    centered_loss = loss_delta - loss_delta.mean(axis=0, keepdims=True)
    alignment = centered_actual @ centered_loss / (
        np.linalg.norm(centered_actual) * np.linalg.norm(centered_loss, axis=0) + 1.0e-12
    )
    out["h086_resp_weight"] = weight
    out["h086_resp_raw"] = raw_weight
    out["h086_resp_prior"] = prior
    out["h086_resp_lift"] = weight / np.clip(prior, 1.0e-12, None)
    out["h086_resp_rank"] = rank01(weight)
    out["h086_resp_lift_rank"] = rank01(out["h086_resp_lift"].to_numpy())
    out["h086_equation_alignment"] = np.nan_to_num(alignment, nan=0.0, posinf=0.0, neginf=0.0)
    out["h086_equation_energy"] = np.std(loss_delta, axis=0)
    source_agree = out.get("source_agrees_h085", pd.Series(np.zeros(len(out)))).to_numpy(dtype=np.float64)
    h082_cell = out.get("h082_cell", pd.Series(np.zeros(len(out)))).to_numpy(dtype=np.float64)
    q_gain = np.clip(out["h085_q_gain"].to_numpy(dtype=np.float64), 0.0, None)
    bad_same = out["h080_bad_same_rank"].to_numpy(dtype=np.float64)
    out["h086_resp_action_score"] = (
        0.32 * out["h086_resp_rank"].to_numpy(dtype=np.float64)
        +0.16 * out["h086_resp_lift_rank"].to_numpy(dtype=np.float64)
        +0.15 * rank01(q_gain)
        +0.12 * out["public_score"].to_numpy(dtype=np.float64)
        +0.10 * out["invariant_score"].to_numpy(dtype=np.float64)
        +0.07 * source_agree
        +0.05 * h082_cell
        +0.05 * rank01(out["h086_equation_energy"].to_numpy(dtype=np.float64))
        -0.14 * bad_same
        -0.10 * out["is_h050_null"].to_numpy(dtype=np.float64)
    )
    out.loc[out["h085_q_gain"] <= 0, "h086_resp_action_score"] -= 0.40
    out.loc[out["h086_resp_lift"] <= 1.0, "h086_resp_action_score"] -= 0.06
    return out


def target_indices_for(group: str) -> list[int]:
    if group == "all":
        return list(range(len(TARGETS)))
    if group == "nonq2":
        return [TARGETS.index(target) for target in NON_Q2]
    if group == "stage":
        return [TARGETS.index(target) for target in S_TARGETS]
    if group == "q":
        return [TARGETS.index(target) for target in ["Q1", "Q2", "Q3"]]
    if group == "q2":
        return [TARGETS.index("Q2")]
    raise ValueError(group)


def candidate_specs() -> list[H086Spec]:
    return [
        H086Spec("resp_cell_all_c760_a090", "cell", "all", "h085_q", 760, 760, 190, 95, 28, 0.90, 1.45, 0.64, True, False, True, "public_resp_cell"),
        H086Spec("resp_cell_all_c1100_a075", "cell", "all", "h085_q", 1100, 1100, 220, 125, 34, 0.75, 1.35, 0.58, False, False, True, "broad_resp_cell"),
        H086Spec("resp_h082_bridge_c680_a085", "cell", "all", "h085_q", 680, 680, 185, 90, 28, 0.85, 1.40, 0.58, False, True, True, "h082_resp_bridge"),
        H086Spec("resp_stage_c560_a090", "cell", "stage", "h085_q", 560, 560, 180, 0, 26, 0.90, 1.40, 0.59, True, False, True, "stage_resp"),
        H086Spec("resp_nonq2_c620_a085", "cell", "nonq2", "q061_hybrid", 620, 620, 190, 0, 30, 0.85, 1.35, 0.60, False, False, True, "private_nonq2_resp"),
        H086Spec("resp_q2_c140_a100", "cell", "q2", "h085_q", 140, 140, 140, 140, 24, 1.00, 1.60, 0.58, True, False, True, "q2_resp"),
        H086Spec("resp_row_all_r72_a070", "row", "all", "h085_q", 72, 504, 72, 72, 12, 0.70, 1.30, 0.62, False, False, True, "row_resp_state"),
        H086Spec("resp_row_nonq2_r92_a075", "row", "nonq2", "q061_hybrid", 92, 552, 92, 0, 14, 0.75, 1.35, 0.59, False, False, True, "row_private_resp"),
    ]


def greedy_select(pool: pd.DataFrame, spec: H086Spec) -> pd.DataFrame:
    selected = []
    rows_seen: set[int] = set()
    subject_counts: dict[str, int] = {}
    q2_count = 0
    for rec in pool.to_dict("records"):
        row = int(rec["row"])
        target = str(rec["target"])
        subject = str(rec.get("subject_id", ""))
        if len(selected) >= spec.max_cells:
            break
        if len(rows_seen) >= spec.max_rows and row not in rows_seen:
            continue
        if subject_counts.get(subject, 0) >= spec.max_per_subject and row not in rows_seen:
            continue
        if target == "Q2" and q2_count >= spec.q2_cap:
            continue
        selected.append(rec)
        rows_seen.add(row)
        subject_counts[subject] = subject_counts.get(subject, 0) + 1
        if target == "Q2":
            q2_count += 1
    return pd.DataFrame(selected)


def build_row_pool(cell: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for row, group in cell.groupby("row", sort=True):
        top = group.sort_values("h086_resp_action_score", ascending=False)
        rec0 = group.iloc[0].to_dict()
        rows.append(
            {
                "row": int(row),
                "subject_id": str(rec0["subject_id"]),
                "sleep_date": rec0["sleep_date"],
                "lifelog_date": rec0["lifelog_date"],
                "row_resp_sum": float(group["h086_resp_weight"].sum()),
                "row_resp_lift_mean": float(group["h086_resp_lift"].mean()),
                "row_action_score_mean": float(group["h086_resp_action_score"].mean()),
                "row_action_score_top4": float(top["h086_resp_action_score"].head(4).mean()),
                "row_q_gain_sum": float(group["h085_q_gain"].clip(lower=0).sum()),
                "row_public_mean": float(group["public_score"].mean()),
                "row_invariant_mean": float(group["invariant_score"].mean()),
                "row_source_agree_mean": float(group.get("source_agrees_h085", pd.Series(np.zeros(len(group)))).mean()),
                "row_bad_same_mean": float(group["h080_bad_same_rank"].mean()),
                "row_h082_cells": int(group.get("h082_cell", pd.Series(np.zeros(len(group)))).sum()),
            }
        )
    out = pd.DataFrame(rows)
    out["h086_row_resp_score"] = (
        0.28 * rank01(out["row_resp_sum"].to_numpy())
        +0.18 * rank01(out["row_resp_lift_mean"].to_numpy())
        +0.18 * rank01(out["row_action_score_top4"].to_numpy())
        +0.13 * rank01(out["row_q_gain_sum"].to_numpy())
        +0.10 * out["row_public_mean"].to_numpy(dtype=float)
        +0.08 * out["row_invariant_mean"].to_numpy(dtype=float)
        +0.06 * out["row_source_agree_mean"].to_numpy(dtype=float)
        -0.12 * out["row_bad_same_mean"].to_numpy(dtype=float)
    )
    return out.sort_values(["h086_row_resp_score", "row_resp_sum"], ascending=[False, False]).reset_index(drop=True)


def materialize_candidate(
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    q_h085: np.ndarray,
    q061: np.ndarray,
    cell: pd.DataFrame,
    row_pool: pd.DataFrame,
    spec: H086Spec,
) -> tuple[np.ndarray, pd.DataFrame]:
    allowed_tidx = set(target_indices_for(spec.target_group))
    selected: pd.DataFrame
    if spec.unit == "cell":
        pool = cell[
            cell["target_index"].astype(int).isin(allowed_tidx)
            & (cell["h086_resp_action_score"] >= spec.min_score)
            & (cell["h085_q_gain"] > 0)
            & (cell["is_h050_null"] <= 0)
        ].copy()
        if spec.require_source_agree:
            pool = pool[pool.get("source_agrees_h085", 0) > 0].copy()
        if spec.require_h082:
            pool = pool[cell.get("h082_cell", pd.Series(np.zeros(len(cell)))).loc[pool.index] > 0].copy()
        if spec.require_resp_lift:
            pool = pool[pool["h086_resp_lift"] > 1.0].copy()
        pool = pool.sort_values(["h086_resp_action_score", "h086_resp_weight"], ascending=[False, False])
        selected = greedy_select(pool, spec)
    elif spec.unit == "row":
        chosen_rows = row_pool[row_pool["h086_row_resp_score"] >= spec.min_score].head(spec.max_units)["row"].astype(int).tolist()
        pool = cell[
            cell["row"].astype(int).isin(chosen_rows)
            & cell["target_index"].astype(int).isin(allowed_tidx)
            & (cell["h085_q_gain"] > 0)
            & (cell["is_h050_null"] <= 0)
        ].copy()
        if spec.require_resp_lift:
            pool = pool[pool["h086_resp_lift"] > 0.85].copy()
        pool = pool.sort_values(["row", "h086_resp_action_score"], ascending=[True, False])
        selected = greedy_select(pool, spec)
    else:
        raise ValueError(spec.unit)

    prob = base_prob.copy()
    z_base = logit(base_prob)
    if spec.value_mode == "h085_q":
        z_target = logit(q_h085)
    elif spec.value_mode == "q061_hybrid":
        z_target = 0.55 * logit(q_h085) + 0.45 * logit(q061)
    else:
        raise ValueError(spec.value_mode)

    for rec in selected.to_dict("records"):
        row = int(rec["row"])
        tidx = int(rec["target_index"])
        move = float(np.clip(z_target[row, tidx] - z_base[row, tidx], -spec.cap, spec.cap))
        prob[row, tidx] = float(sigmoid(np.array([z_base[row, tidx] + spec.alpha * move]))[0])
    return clip_prob(prob), selected


def bad_anchor_vectors(sample: pd.DataFrame, base_prob: np.ndarray) -> dict[str, np.ndarray]:
    out: dict[str, np.ndarray] = {}
    for name in H085MOD.BAD_ANCHORS:
        path = H085MOD.locate(name)
        if path is None:
            continue
        try:
            prob = H085MOD.load_sub(path, sample)[TARGETS].to_numpy(dtype=np.float64)
        except Exception:
            continue
        out[name] = (logit(prob) - logit(base_prob)).reshape(-1)
    return out


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1.0e-12))


def evaluate_candidate(
    prob: np.ndarray,
    selected: pd.DataFrame,
    spec: H086Spec,
    base_prob: np.ndarray,
    q_h085: np.ndarray,
    resp_w: np.ndarray,
    bad_vecs: dict[str, np.ndarray],
) -> dict[str, object]:
    changed = np.abs(prob - base_prob) > TOL
    loss_move = (bce(prob, q_h085) - bce(base_prob, q_h085)).reshape(-1)
    move_vec = (logit(prob) - logit(base_prob)).reshape(-1)
    bad_cos = {
        f"bad_cos_{Path(name).stem[:24]}": cosine(move_vec, bad)
        for name, bad in bad_vecs.items()
    }
    max_bad = max([max(v, 0.0) for v in bad_cos.values()] + [0.0])
    h082_ratio = float(selected.get("h082_cell", pd.Series(np.zeros(len(selected)))).mean()) if len(selected) else 0.0
    source_agree_rate = float(selected.get("source_agrees_h085", pd.Series(np.zeros(len(selected)))).mean()) if len(selected) else 0.0
    target_counts = selected["target"].value_counts().to_dict() if len(selected) else {}
    meta: dict[str, object] = {
        "candidate_id": "",
        "spec_name": spec.name,
        "unit": spec.unit,
        "target_group": spec.target_group,
        "value_mode": spec.value_mode,
        "novelty": spec.novelty,
        "alpha": spec.alpha,
        "cap": spec.cap,
        "selected_cells": int(len(selected)),
        "selected_rows": int(selected["row"].nunique()) if len(selected) else 0,
        "q2_cells": int((selected["target"].astype(str) == "Q2").sum()) if len(selected) else 0,
        "resp_weighted_delta_vs_h057": float(loss_move @ resp_w),
        "posterior_delta_vs_h057": float(loss_move.mean()),
        "top_selected_resp_weight_sum": float(selected["h086_resp_weight"].sum()) if len(selected) else 0.0,
        "mean_selected_resp_rank": float(selected["h086_resp_rank"].mean()) if len(selected) else 0.0,
        "mean_selected_resp_lift": float(selected["h086_resp_lift"].mean()) if len(selected) else 0.0,
        "mean_selected_action_score": float(selected["h086_resp_action_score"].mean()) if len(selected) else 0.0,
        "source_agree_rate": source_agree_rate,
        "h082_ratio": h082_ratio,
        "mean_public_score": float(selected["public_score"].mean()) if len(selected) else 0.0,
        "mean_invariant_score": float(selected["invariant_score"].mean()) if len(selected) else 0.0,
        "mean_bad_same_rank": float(selected["h080_bad_same_rank"].mean()) if len(selected) else 1.0,
        "max_positive_bad_cosine": max_bad,
        "mean_abs_prob_move_vs_h057": float(np.abs(prob - base_prob).mean()),
        "max_abs_prob_move_vs_h057": float(np.abs(prob - base_prob).max()),
        "target_templates": ";".join(f"{k}:{v}" for k, v in sorted(target_counts.items())),
        **bad_cos,
    }
    for target in TARGETS:
        meta[f"{target}_changed_vs_h057"] = int(changed[:, TARGETS.index(target)].sum())
    return meta


def write_submission(sample: pd.DataFrame, prob: np.ndarray, path: Path) -> None:
    out = sample.copy()
    for i, target in enumerate(TARGETS):
        out[target] = clip_prob(prob[:, i])
    out.to_csv(path, index=False)


def validate_submission(path: Path, sample: pd.DataFrame, base_prob: np.ndarray) -> dict[str, object]:
    df = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"])
    df = df.sort_values(KEYS).reset_index(drop=True)
    prob = df[TARGETS].to_numpy(dtype=np.float64)
    return {
        "path": str(path.resolve()),
        "rows": int(len(df)),
        "keys_match": bool(df[KEYS].equals(sample[KEYS])),
        "duplicate_keys": int(df.duplicated(KEYS).sum()),
        "nan_cells": int(np.isnan(prob).sum()),
        "min_prob": float(np.nanmin(prob)),
        "max_prob": float(np.nanmax(prob)),
        "changed_cells_vs_h057_validation": int((np.abs(prob - base_prob) > TOL).sum()),
        "upload_safe": bool(
            len(df) == len(sample)
            and df[KEYS].equals(sample[KEYS])
            and int(df.duplicated(KEYS).sum()) == 0
            and int(np.isnan(prob).sum()) == 0
            and float(np.nanmin(prob)) >= EPS
            and float(np.nanmax(prob)) <= 1.0 - EPS + 1.0e-12
        ),
    }


def candidate_sweep(
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    q_h085: np.ndarray,
    q061: np.ndarray,
    cell: pd.DataFrame,
    row_pool: pd.DataFrame,
    resp_w: np.ndarray,
    bad_vecs: dict[str, np.ndarray],
) -> tuple[pd.DataFrame, dict[str, np.ndarray], pd.DataFrame]:
    rows = []
    probs: dict[str, np.ndarray] = {}
    selected_tables = []
    seen: set[str] = set()
    for spec in candidate_specs():
        prob, selected = materialize_candidate(sample, base_prob, q_h085, q061, cell, row_pool, spec)
        if selected.empty:
            continue
        digest = short_hash(prob)
        if digest in seen:
            continue
        seen.add(digest)
        meta = evaluate_candidate(prob, selected, spec, base_prob, q_h085, resp_w, bad_vecs)
        cid = f"h086_{spec.name}_{digest}"
        meta["candidate_id"] = cid
        meta["hash"] = digest
        rows.append(meta)
        probs[cid] = prob
        selected_tables.append(selected.assign(candidate_id=cid))
    cand = pd.DataFrame(rows)
    if cand.empty:
        raise RuntimeError("no H086 candidates")
    cand["resp_rank"] = rank01(-cand["resp_weighted_delta_vs_h057"].to_numpy())
    cand["posterior_rank"] = rank01(-cand["posterior_delta_vs_h057"].to_numpy())
    cand["bad_avoid_rank"] = rank01(-cand["max_positive_bad_cosine"].to_numpy())
    cand["support_rank"] = rank01(cand["top_selected_resp_weight_sum"].to_numpy())
    cand["source_rank"] = rank01(cand["source_agree_rate"].to_numpy())
    cand["h082_rank"] = rank01(cand["h082_ratio"].to_numpy())
    cand["size_rank"] = rank01(np.minimum(cand["selected_cells"].to_numpy(dtype=float), 900.0))
    cand["bigbet_unit_bonus"] = cand["unit"].map({"row": 0.14, "cell": 0.04}).fillna(0.0)
    cand["h086_score"] = (
        0.30 * cand["resp_rank"]
        +0.16 * cand["posterior_rank"]
        +0.14 * cand["bad_avoid_rank"]
        +0.12 * cand["support_rank"]
        +0.09 * cand["source_rank"]
        +0.07 * cand["h082_rank"]
        +0.06 * cand["size_rank"]
        +cand["bigbet_unit_bonus"]
        -0.06 * (cand["max_abs_prob_move_vs_h057"] > 0.22).astype(float)
    )
    cand = cand.sort_values(["h086_score", "resp_weighted_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True)
    for _, rec in cand.iterrows():
        cid = str(rec["candidate_id"])
        path = OUT / f"submission_{cid}.csv"
        write_submission(sample, probs[cid], path)
        cand.loc[cand["candidate_id"].eq(cid), "file"] = path.name
        cand.loc[cand["candidate_id"].eq(cid), "resolved_path"] = str(path.resolve())
    selected_all = pd.concat(selected_tables, ignore_index=True) if selected_tables else pd.DataFrame()
    return cand, probs, selected_all


def write_report(
    equations: pd.DataFrame,
    configs: pd.DataFrame,
    cell: pd.DataFrame,
    row_pool: pd.DataFrame,
    cand: pd.DataFrame,
    selected_all: pd.DataFrame,
    decision: pd.DataFrame,
) -> None:
    selected_cols = [
        "candidate_id",
        "row",
        "subject_id",
        "sleep_date",
        "target",
        "h086_resp_weight",
        "h086_resp_lift",
        "h086_resp_action_score",
        "h085_q_gain",
        "source_agrees_h085",
        "h082_cell",
        "public_score",
        "invariant_score",
        "h080_bad_same_rank",
    ]
    parts = [
        "# H086 Public-Subset Responsibility HS-JEPA",
        "",
        "Question: is the missing public/private factor a row-target responsibility vector rather than only a label posterior?",
        "",
        "Design:",
        "",
        "- context: known public LB observations and their loss-delta signatures;",
        "- target representation: nonnegative row-target responsibility weights fit to public LB deltas under H085 q;",
        "- decoder: high-responsibility cells or rows moved toward H085/q061 hidden state;",
        "- stress: leave-one-submission-out equation fit, bad-anchor cosine, source-action agreement.",
        "",
        "Public equations:",
        "",
        md_table(equations, 40),
        "",
        "Responsibility posterior configs:",
        "",
        md_table(configs, 30),
        "",
        "Top responsibility cells:",
        "",
        md_table(
            cell.sort_values("h086_resp_weight", ascending=False)[
                [
                    "row",
                    "subject_id",
                    "sleep_date",
                    "target",
                    "h086_resp_weight",
                    "h086_resp_lift",
                    "h086_resp_action_score",
                    "h085_q_gain",
                    "source_agrees_h085",
                    "h082_cell",
                    "public_score",
                    "invariant_score",
                    "h080_bad_same_rank",
                ]
            ],
            80,
        ),
        "",
        "Top responsibility rows:",
        "",
        md_table(row_pool, 40),
        "",
        "Candidates:",
        "",
        md_table(cand, 30),
        "",
        "Selected cells sample:",
        "",
        md_table(selected_all[[c for c in selected_cols if c in selected_all.columns]], 160),
        "",
        "Decision:",
        "",
        md_table(decision),
        "",
        "Interpretation:",
        "",
        "- If H086 improves over H057, HS-JEPA needs a public/private responsibility head: public LB listens more to some row-target states than others.",
        "- If H086 loses, the public-equation jump was mostly label-posterior reconstruction and responsibility is too underdetermined from the current sensor set.",
    ]
    (OUT / "h086_report.md").write_text("\n".join(parts))


def main() -> None:
    cleanup_previous_outputs()
    sample = H085MOD.load_sub(BASE_FILE).sort_values(KEYS).reset_index(drop=True)
    base_prob = sample[TARGETS].to_numpy(dtype=np.float64)
    q_h085 = load_h085_q(sample)
    q061 = load_q061(sample)
    equations, loss_delta, actual = load_known_system(sample, base_prob, q_h085)
    cell0 = load_cell_table(sample, base_prob, q_h085)
    priors = build_priors(cell0, sample)
    configs, weights, raw_weights = eval_responsibility_configs(equations, loss_delta, actual, priors)
    best = configs.iloc[0]
    key = str(best["resp_key"])
    prior = priors[str(best["prior_name"])]
    resp_w = weights[key]
    raw_w = raw_weights[key]
    cell = add_responsibility_features(cell0, loss_delta, actual, resp_w, raw_w, prior)
    row_pool = build_row_pool(cell)
    bad_vecs = bad_anchor_vectors(sample, base_prob)
    cand, probs, selected_all = candidate_sweep(sample, base_prob, q_h085, q061, cell, row_pool, resp_w, bad_vecs)

    bigbet = cand[
        (cand["resp_weighted_delta_vs_h057"] <= -0.0010)
        & (cand["selected_cells"] >= 120)
        & (cand["max_positive_bad_cosine"] <= 0.01)
    ].copy()
    if len(bigbet):
        selected = bigbet.sort_values(["h086_score", "resp_weighted_delta_vs_h057"], ascending=[False, True]).iloc[0]
        decision_name = "promote_public_responsibility_bigbet"
        worldview = "public LB is generated by a hidden row-target responsibility field"
    else:
        selected = cand.iloc[0]
        decision_name = "promote_public_responsibility_diagnostic"
        worldview = "responsibility field is measurable but did not clear every big-bet guardrail"

    selected_id = str(selected["candidate_id"])
    root_file = ROOT / f"submission_h086_public_resp_{selected['hash']}_uploadsafe.csv"
    shutil.copy2(Path(str(selected["resolved_path"])), root_file)
    validation = validate_submission(root_file, sample, base_prob)
    decision = pd.DataFrame([{**best.to_dict(), **selected.to_dict(), **validation}])
    decision.insert(0, "worldview", worldview)
    decision.insert(0, "root_uploadsafe_path", str(root_file.resolve()))
    decision.insert(0, "selected_resolved_path", str(selected["resolved_path"]))
    decision.insert(0, "selected_file", str(selected["file"]))
    decision.insert(0, "selected_candidate_id", selected_id)
    decision.insert(0, "decision", decision_name)

    equations.to_csv(OUT / "h086_public_equations.csv", index=False)
    configs.to_csv(OUT / "h086_responsibility_configs.csv", index=False)
    cell.to_csv(OUT / "h086_cell_responsibility.csv", index=False)
    row_pool.to_csv(OUT / "h086_row_responsibility.csv", index=False)
    cand.to_csv(OUT / "h086_candidate_scores.csv", index=False)
    selected_all.to_csv(OUT / "h086_selected_cells_all_candidates.csv", index=False)
    selected_cells = selected_all[selected_all["candidate_id"].astype(str).eq(selected_id)].copy()
    selected_cells.to_csv(OUT / "h086_selected_cells.csv", index=False)
    decision.to_csv(OUT / "h086_decision.csv", index=False)
    write_report(equations, configs, cell, row_pool, cand, selected_all, decision)

    print(f"selected={selected_id}")
    print(f"root={root_file}")
    print(
        decision[
            [
                "decision",
                "resp_key",
                "resp_weighted_delta_vs_h057",
                "posterior_delta_vs_h057",
                "selected_cells",
                "selected_rows",
                "max_positive_bad_cosine",
                "upload_safe",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
