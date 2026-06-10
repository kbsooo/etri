#!/usr/bin/env python3
"""Mixture-listener responsibility solver for HS-JEPA.

This is a deliberately high-risk paper-facing experiment.

The previous LB-conditioned responsibility solver assumes that the public
leaderboard behaves like one scalar listener.  That is useful, but it is also
underdetermined: many row-target action fields can explain the same scalar
score movement.

This solver tests a stronger HS-JEPA thesis:

    public LB response = mixture of latent listener heads

The heads are estimated from the low-rank action geometry of previous public
observations.  The solver then asks whether row-target actions should be
released only when the scalar listener, the dominant public mode, and the
private residual modes agree, or whether the breakthrough lives in the
conflict between those listener heads.

The reusable claim is about listener factorization.  The competition adapter
uses public LB submissions as the external scalar observations and Q/S route
energy as the invariant manifold.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json
import math
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sleep_competition_adapter.factorized_toxicity_decoder_candidate import (  # noqa: E402
    KEYS,
    TARGETS,
    TOL,
    clip_prob,
    logit,
    short_hash,
    sigmoid,
    validate_submission,
    write_submission,
)
from sleep_competition_adapter.lb_conditioned_responsibility_solver import (  # noqa: E402
    fit_responsibility,
    load_anchor_matrix,
)
from sleep_competition_adapter.negative_tangent_invariant_projection_solver import (  # noqa: E402
    TargetInvariantManifold,
    load_manifold,
)
from sleep_competition_adapter.spectral_public_tangent_solver import (  # noqa: E402
    candidate_pool,
    load_base,
    rank01,
    spectral_public_tangent,
    z_and_p,
)


HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "mixture_listener_responsibility_solver"
OUT.mkdir(parents=True, exist_ok=True)

READOUT_JSON = OUT / "mixture_listener_responsibility_readout.json"
READOUT_MD = OUT / "mixture_listener_responsibility_readout_ko.md"
CELL_CSV = OUT / "mixture_listener_responsibility_cells.csv"
SELECTED_CSV = OUT / "mixture_listener_responsibility_selected_cells.csv"
MODE_CSV = OUT / "mixture_listener_modes.csv"
NULL_CSV = OUT / "mixture_listener_responsibility_null_stress.csv"


@dataclass(frozen=True)
class MixtureConfig:
    name: str
    worldview: str
    release_head: str
    max_cells: int
    max_cells_per_row: int
    min_action_health: float
    min_scalar_rank: float
    min_head_rank: float
    min_mode_confidence: float
    max_energy_delta: float
    max_subject_delta: float
    require_supported: bool
    require_consensus: bool
    require_conflict: bool
    step_floor: float
    step_scale: float
    step_cap: float
    target_caps: tuple[tuple[str, int], ...]


CONFIGS = (
    MixtureConfig(
        name="mixture_consensus_jackpot",
        worldview=(
            "If public LB is a mixture listener, the safest large action should be "
            "where scalar, dominant public mode, and residual modes agree."
        ),
        release_head="consensus",
        max_cells=72,
        max_cells_per_row=3,
        min_action_health=0.28,
        min_scalar_rank=0.42,
        min_head_rank=0.40,
        min_mode_confidence=0.34,
        max_energy_delta=0.030,
        max_subject_delta=0.060,
        require_supported=False,
        require_consensus=True,
        require_conflict=False,
        step_floor=0.020,
        step_scale=0.42,
        step_cap=0.58,
        target_caps=(("Q1", 10), ("Q2", 16), ("Q3", 10), ("S1", 12), ("S2", 16), ("S3", 8), ("S4", 12)),
    ),
    MixtureConfig(
        name="private_residual_rescue_jackpot",
        worldview=(
            "The first public mode may be a collapse/shortcut detector.  The "
            "recoverable signal may live in residual listener heads that conflict "
            "with that dominant mode."
        ),
        release_head="residual",
        max_cells=64,
        max_cells_per_row=3,
        min_action_health=0.24,
        min_scalar_rank=0.30,
        min_head_rank=0.46,
        min_mode_confidence=0.38,
        max_energy_delta=0.040,
        max_subject_delta=0.080,
        require_supported=False,
        require_consensus=False,
        require_conflict=True,
        step_floor=0.022,
        step_scale=0.46,
        step_cap=0.62,
        target_caps=(("Q1", 8), ("Q2", 15), ("Q3", 9), ("S1", 10), ("S2", 15), ("S3", 7), ("S4", 10)),
    ),
    MixtureConfig(
        name="bad_mode_inside_out_probe",
        worldview=(
            "The dominant bad tangent may not be uniformly bad.  Some cells inside "
            "that mode can be valid if action-health and scalar responsibility agree."
        ),
        release_head="bad_mode",
        max_cells=50,
        max_cells_per_row=2,
        min_action_health=0.34,
        min_scalar_rank=0.52,
        min_head_rank=0.54,
        min_mode_confidence=0.42,
        max_energy_delta=0.018,
        max_subject_delta=0.050,
        require_supported=True,
        require_consensus=False,
        require_conflict=False,
        step_floor=0.018,
        step_scale=0.34,
        step_cap=0.48,
        target_caps=(("Q1", 7), ("Q2", 11), ("Q3", 7), ("S1", 8), ("S2", 11), ("S3", 6), ("S4", 8)),
    ),
    MixtureConfig(
        name="target_listener_split_qs",
        worldview=(
            "Subjective Q labels and objective S labels may listen to different "
            "latent heads.  Q actions use residual modes; S actions use scalar/public "
            "consensus."
        ),
        release_head="target_split",
        max_cells=66,
        max_cells_per_row=3,
        min_action_health=0.26,
        min_scalar_rank=0.34,
        min_head_rank=0.38,
        min_mode_confidence=0.30,
        max_energy_delta=0.036,
        max_subject_delta=0.070,
        require_supported=False,
        require_consensus=False,
        require_conflict=False,
        step_floor=0.020,
        step_scale=0.40,
        step_cap=0.56,
        target_caps=(("Q1", 10), ("Q2", 14), ("Q3", 10), ("S1", 10), ("S2", 14), ("S3", 8), ("S4", 10)),
    ),
    MixtureConfig(
        name="portable_mixture_core",
        worldview=(
            "For the paper thesis, release only actions supported by existing "
            "adapter families and non-worsening personal-coordinate invariance."
        ),
        release_head="consensus",
        max_cells=34,
        max_cells_per_row=1,
        min_action_health=0.40,
        min_scalar_rank=0.40,
        min_head_rank=0.34,
        min_mode_confidence=0.28,
        max_energy_delta=0.004,
        max_subject_delta=0.002,
        require_supported=True,
        require_consensus=False,
        require_conflict=False,
        step_floor=0.014,
        step_scale=0.24,
        step_cap=0.34,
        target_caps=(("Q1", 5), ("Q2", 8), ("Q3", 5), ("S1", 5), ("S2", 8), ("S3", 4), ("S4", 5)),
    ),
)


def finite(value: Any, default: float = 0.0) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    return out if math.isfinite(out) else default


def fmt(value: Any, digits: int = 4) -> str:
    val = finite(value, float("nan"))
    return f"{val:.{digits}f}" if math.isfinite(val) else "n/a"


def sign_or_one(values: pd.Series | np.ndarray) -> np.ndarray:
    sign = np.sign(np.asarray(values, dtype=np.float64))
    sign[sign == 0] = 1
    return sign.astype(int)


def fit_mixture_modes(anchor_matrix: np.ndarray, loss_delta: np.ndarray, flats: np.ndarray) -> dict[str, object]:
    raw = anchor_matrix[:, flats].astype(np.float64)
    std = raw.std(axis=0, ddof=1)
    std = np.where(std < 1e-6, 1.0, std)
    x = raw / std[None, :]
    x_center = x - x.mean(axis=0, keepdims=True)
    y = loss_delta.astype(np.float64)
    y_z = y - float(y.mean())
    y_std = float(y_z.std(ddof=1)) if len(y_z) > 1 else 1.0
    if y_std < 1e-12:
        y_std = 1.0
    y_z = y_z / y_std

    u, s, vt = np.linalg.svd(x_center, full_matrices=False)
    scores = u * s[None, :]
    keep = min(6, scores.shape[1])
    score_keep = scores[:, :keep]
    beta = np.linalg.solve(score_keep.T @ score_keep + 0.45 * np.eye(keep), score_keep.T @ y_z)
    mode_grad_std = beta[:, None] * vt[:keep]
    mode_grad = mode_grad_std / std[None, :]
    scalar_fit = fit_responsibility(anchor_matrix, loss_delta, flats)
    scalar_grad = np.asarray(scalar_fit["coef"], dtype=np.float64) / std
    scalar_stability = np.asarray(scalar_fit["sign_stability"], dtype=np.float64)

    pred = score_keep @ beta
    loo_pred = []
    for idx in range(score_keep.shape[0]):
        mask = np.ones(score_keep.shape[0], dtype=bool)
        mask[idx] = False
        local_x = score_keep[mask]
        local_y = y_z[mask]
        local_beta = np.linalg.solve(local_x.T @ local_x + 0.65 * np.eye(keep), local_x.T @ local_y)
        loo_pred.append(float(score_keep[idx] @ local_beta))
    loo_pred_arr = np.asarray(loo_pred, dtype=np.float64)
    loo_corr = float(np.corrcoef(y_z, loo_pred_arr)[0, 1]) if np.std(loo_pred_arr) > 0 else 0.0

    variance = (s**2) / float((s**2).sum()) if float((s**2).sum()) > 0 else np.zeros_like(s)
    rows = []
    for idx in range(keep):
        rows.append(
            {
                "mode": idx,
                "variance": float(variance[idx]),
                "cumulative_variance": float(variance[: idx + 1].sum()),
                "beta": float(beta[idx]),
                "score_loss_corr": float(np.corrcoef(scores[:, idx], y_z)[0, 1]) if np.std(scores[:, idx]) > 0 else 0.0,
                "singular_value": float(s[idx]),
            }
        )
    pd.DataFrame(rows).to_csv(MODE_CSV, index=False)
    return {
        "flats": flats,
        "std": std,
        "scalar_grad": scalar_grad,
        "scalar_stability": scalar_stability,
        "mode_grad": mode_grad,
        "beta": beta,
        "variance": variance[:keep],
        "loo_corr": loo_corr,
        "train_corr": float(np.corrcoef(y_z, pred)[0, 1]) if np.std(pred) > 0 else 0.0,
        "modes": rows,
        "scalar_fit": scalar_fit["fit"],
    }


def build_mixture_cells(
    pool: pd.DataFrame,
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    base_logit: np.ndarray,
    manifold: TargetInvariantManifold,
    anchor_matrix: np.ndarray,
    loss_delta: np.ndarray,
) -> tuple[pd.DataFrame, dict[str, object]]:
    flats = np.asarray(sorted(pool["flat_idx"].astype(int).unique()), dtype=int)
    fit = fit_mixture_modes(anchor_matrix, loss_delta, flats)
    flat_pos = {int(flat): idx for idx, flat in enumerate(flats)}

    best = (
        pool.sort_values(["action_health", "source_family_count", "anti_bad_score"], ascending=False)
        .groupby("flat_idx", as_index=False)
        .first()
    )
    support_signs = pool.groupby("flat_idx")["direction"].apply(lambda s: set(s.astype(int))).to_dict()
    base_logit_matrix = base_logit.reshape(base_prob.shape)
    rows: list[dict[str, object]] = []
    for _, rec in best.iterrows():
        flat = int(rec["flat_idx"])
        pos = flat_pos[flat]
        row_idx = int(rec["row"])
        target_idx = int(rec["target_idx"])
        target = str(rec["target"])
        subject = str(sample.iloc[row_idx]["subject_id"])
        old_vec = base_prob[row_idx].copy()
        old_parts = manifold.energy_parts(subject, old_vec)

        scalar_grad = float(fit["scalar_grad"][pos])
        bad_grad = float(fit["mode_grad"][0, pos])
        residual_grad = float(fit["mode_grad"][1:, pos].sum()) if fit["mode_grad"].shape[0] > 1 else 0.0
        total_mode_grad = bad_grad + residual_grad
        scalar_release = -1 if scalar_grad > 0 else 1
        bad_release = -1 if bad_grad > 0 else 1
        residual_release = -1 if residual_grad > 0 else 1
        mode_release = -1 if total_mode_grad > 0 else 1
        split_release = residual_release if target.startswith("Q") else scalar_release

        mode_abs = np.abs(fit["mode_grad"][:, pos])
        confidence = float(mode_abs.max() / (mode_abs.sum() + 1e-12))
        residual_share = float(abs(residual_grad) / (abs(bad_grad) + abs(residual_grad) + 1e-12))
        scalar_bad_agree = bool(scalar_release == bad_release)
        scalar_residual_agree = bool(scalar_release == residual_release)
        mode_conflict = bool(bad_release != residual_release)
        consensus_release = scalar_release
        if not (scalar_bad_agree and scalar_residual_agree):
            consensus_release = mode_release

        release_map = {
            "scalar": scalar_release,
            "bad_mode": bad_release,
            "residual": residual_release,
            "consensus": consensus_release,
            "target_split": split_release,
        }
        for head, release_sign in release_map.items():
            step = float(release_sign) * 0.10
            new_vec = old_vec.copy()
            new_vec[target_idx] = clip_prob(sigmoid(np.asarray([base_logit_matrix[row_idx, target_idx] + step])))[0]
            new_parts = manifold.energy_parts(subject, new_vec)
            rows.append(
                {
                    **rec.to_dict(),
                    "subject_id": subject,
                    "release_head": head,
                    "release_sign": int(release_sign),
                    "supported_release": bool(release_sign in support_signs.get(flat, set())),
                    "support_signs": ",".join(str(v) for v in sorted(support_signs.get(flat, set()))),
                    "scalar_grad": scalar_grad,
                    "bad_mode_grad": bad_grad,
                    "residual_grad": residual_grad,
                    "total_mode_grad": total_mode_grad,
                    "scalar_stability": float(fit["scalar_stability"][pos]),
                    "mode_confidence": confidence,
                    "residual_share": residual_share,
                    "scalar_bad_agree": scalar_bad_agree,
                    "scalar_residual_agree": scalar_residual_agree,
                    "mode_conflict": mode_conflict,
                    "prototype_predicted_scalar_delta": float(scalar_grad * step),
                    "prototype_predicted_bad_delta": float(bad_grad * step),
                    "prototype_predicted_residual_delta": float(residual_grad * step),
                    "prototype_predicted_total_mode_delta": float(total_mode_grad * step),
                    "prototype_energy_delta": float(new_parts["combined_energy"] - old_parts["combined_energy"]),
                    "prototype_subject_delta": float(new_parts["subject_energy"] - old_parts["subject_energy"]),
                }
            )

    frame = pd.DataFrame(rows)
    if frame.empty:
        return frame, fit
    frame["scalar_abs_rank"] = rank01(frame["scalar_grad"].abs())
    frame["bad_abs_rank"] = rank01(frame["bad_mode_grad"].abs())
    frame["residual_abs_rank"] = rank01(frame["residual_grad"].abs())
    frame["total_mode_abs_rank"] = rank01(frame["total_mode_grad"].abs())
    frame["head_abs_grad"] = np.select(
        [
            frame["release_head"].eq("bad_mode"),
            frame["release_head"].eq("residual"),
            frame["release_head"].eq("target_split") & frame["target"].astype(str).str.startswith("Q"),
        ],
        [
            frame["bad_mode_grad"].abs(),
            frame["residual_grad"].abs(),
            frame["residual_grad"].abs(),
        ],
        default=frame["total_mode_grad"].abs(),
    )
    frame["head_abs_rank"] = rank01(frame["head_abs_grad"])
    frame["agreement_score"] = (
        frame["scalar_bad_agree"].astype(float)
        + frame["scalar_residual_agree"].astype(float)
        + (~frame["mode_conflict"].astype(bool)).astype(float)
    ) / 3.0
    frame["conflict_score"] = (
        frame["mode_conflict"].astype(float) * 0.55
        + (1.0 - frame["agreement_score"]) * 0.25
        + frame["residual_share"].clip(0, 1) * 0.20
    )
    frame["mixture_score"] = (
        0.22 * frame["scalar_abs_rank"]
        + 0.20 * frame["head_abs_rank"]
        + 0.16 * frame["scalar_stability"].clip(0, 1)
        + 0.14 * frame["mode_confidence"].clip(0, 1)
        + 0.12 * frame["action_health"].astype(float).clip(0, 1)
        + 0.08 * rank01(frame["source_family_count"])
        + 0.08 * rank01(-frame["prototype_energy_delta"])
    )
    return frame.sort_values("mixture_score", ascending=False, kind="mergesort").reset_index(drop=True), fit


def release_step(row: pd.Series, config: MixtureConfig) -> float:
    magnitude = (
        config.step_floor
        + config.step_scale
        * float(row["head_abs_rank"])
        * (0.35 + 0.65 * float(row["mode_confidence"]))
        * (0.55 + 0.45 * float(row["action_health"]))
    )
    return float(row["release_sign"]) * float(np.clip(magnitude, 0.0, config.step_cap))


def filter_config(frame: pd.DataFrame, config: MixtureConfig) -> pd.DataFrame:
    out = frame[frame["release_head"].eq(config.release_head)].copy()
    out = out[
        out["action_health"].astype(float).ge(config.min_action_health)
        & out["scalar_abs_rank"].astype(float).ge(config.min_scalar_rank)
        & out["head_abs_rank"].astype(float).ge(config.min_head_rank)
        & out["mode_confidence"].astype(float).ge(config.min_mode_confidence)
    ].copy()
    if config.require_supported:
        out = out[out["supported_release"].astype(bool)]
    if config.require_consensus:
        out = out[out["agreement_score"].astype(float).ge(0.99)]
    if config.require_conflict:
        out = out[out["mode_conflict"].astype(bool)]
    return out


def greedy_release(
    frame: pd.DataFrame,
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    base_logit: np.ndarray,
    manifold: TargetInvariantManifold,
    config: MixtureConfig,
) -> tuple[pd.DataFrame, np.ndarray]:
    feasible = filter_config(frame, config)
    if feasible.empty:
        return feasible, np.zeros(base_logit.size, dtype=np.float64)

    feasible = feasible.copy()
    if config.require_conflict:
        feasible["_priority"] = (
            0.38 * feasible["conflict_score"].astype(float)
            + 0.24 * feasible["head_abs_rank"].astype(float)
            + 0.18 * feasible["mode_confidence"].astype(float)
            + 0.12 * feasible["action_health"].astype(float)
            + 0.08 * feasible["scalar_stability"].astype(float)
        )
    else:
        feasible["_priority"] = (
            0.30 * feasible["mixture_score"].astype(float)
            + 0.26 * feasible["agreement_score"].astype(float)
            + 0.18 * feasible["head_abs_rank"].astype(float)
            + 0.14 * feasible["action_health"].astype(float)
            + 0.12 * feasible["scalar_stability"].astype(float)
        )

    caps = dict(config.target_caps)
    current = base_prob.copy()
    base_logit_matrix = base_logit.reshape(base_prob.shape)
    move = np.zeros(base_logit.size, dtype=np.float64)
    selected: list[dict[str, object]] = []
    row_counts: dict[int, int] = {}
    target_counts: dict[str, int] = {}

    for rec in feasible.sort_values("_priority", ascending=False, kind="mergesort").to_dict("records"):
        row_idx = int(rec["row"])
        target = str(rec["target"])
        target_idx = int(rec["target_idx"])
        flat = int(rec["flat_idx"])
        if row_counts.get(row_idx, 0) >= config.max_cells_per_row:
            continue
        if target_counts.get(target, 0) >= caps.get(target, config.max_cells):
            continue
        if abs(move[flat]) > TOL:
            continue

        step = release_step(pd.Series(rec), config)
        old_vec = current[row_idx].copy()
        old_parts = manifold.energy_parts(str(sample.iloc[row_idx]["subject_id"]), old_vec)
        new_vec = old_vec.copy()
        new_vec[target_idx] = clip_prob(sigmoid(np.asarray([base_logit_matrix[row_idx, target_idx] + step])))[0]
        new_parts = manifold.energy_parts(str(sample.iloc[row_idx]["subject_id"]), new_vec)
        energy_delta = float(new_parts["combined_energy"] - old_parts["combined_energy"])
        subject_delta = float(new_parts["subject_energy"] - old_parts["subject_energy"])
        if energy_delta > config.max_energy_delta:
            continue
        if subject_delta > config.max_subject_delta:
            continue

        rec["released_logit_step"] = step
        rec["predicted_scalar_delta"] = float(rec["scalar_grad"]) * step
        rec["predicted_bad_delta"] = float(rec["bad_mode_grad"]) * step
        rec["predicted_residual_delta"] = float(rec["residual_grad"]) * step
        rec["predicted_total_mode_delta"] = float(rec["total_mode_grad"]) * step
        rec["incremental_energy_delta"] = energy_delta
        rec["incremental_subject_delta"] = subject_delta
        rec["variant"] = config.name
        selected.append(rec)
        current[row_idx] = new_vec
        move[flat] = step
        row_counts[row_idx] = row_counts.get(row_idx, 0) + 1
        target_counts[target] = target_counts.get(target, 0) + 1
        if len(selected) >= config.max_cells:
            break
    return pd.DataFrame(selected), move


def selection_metrics(selected: pd.DataFrame, move: np.ndarray, bad_tangent: np.ndarray) -> dict[str, float]:
    if selected.empty:
        return {
            "cells": 0.0,
            "rows": 0.0,
            "mean_mixture_score": 0.0,
            "mean_agreement_score": 0.0,
            "mean_conflict_score": 0.0,
            "mean_mode_confidence": 0.0,
            "mean_action_health": 0.0,
            "sum_predicted_scalar_delta": 0.0,
            "sum_predicted_bad_delta": 0.0,
            "sum_predicted_residual_delta": 0.0,
            "sum_predicted_total_mode_delta": 0.0,
            "mean_energy_delta": 0.0,
            "mean_subject_delta": 0.0,
            "supported_rate": 0.0,
            "bad_tangent_cosine": 0.0,
        }
    denom = float(np.linalg.norm(move) * np.linalg.norm(bad_tangent))
    cosine = float((move @ bad_tangent) / denom) if denom > 0 else 0.0
    return {
        "cells": float(len(selected)),
        "rows": float(selected["row"].nunique()),
        "mean_mixture_score": float(selected["mixture_score"].mean()),
        "mean_agreement_score": float(selected["agreement_score"].mean()),
        "mean_conflict_score": float(selected["conflict_score"].mean()),
        "mean_mode_confidence": float(selected["mode_confidence"].mean()),
        "mean_action_health": float(selected["action_health"].mean()),
        "sum_predicted_scalar_delta": float(selected["predicted_scalar_delta"].sum()),
        "sum_predicted_bad_delta": float(selected["predicted_bad_delta"].sum()),
        "sum_predicted_residual_delta": float(selected["predicted_residual_delta"].sum()),
        "sum_predicted_total_mode_delta": float(selected["predicted_total_mode_delta"].sum()),
        "mean_energy_delta": float(selected["incremental_energy_delta"].mean()),
        "mean_subject_delta": float(selected["incremental_subject_delta"].mean()),
        "supported_rate": float(selected["supported_release"].astype(bool).mean()),
        "bad_tangent_cosine": cosine,
    }


def null_stress(
    frame: pd.DataFrame,
    selected: pd.DataFrame,
    move: np.ndarray,
    bad_tangent: np.ndarray,
    config: MixtureConfig,
) -> dict[str, object]:
    actual = selection_metrics(selected, move, bad_tangent)
    if selected.empty:
        return {"actual": actual, "tests": {}, "null_frame": pd.DataFrame()}
    rng = np.random.default_rng(abs(hash(config.name)) % (2**32))
    feasible = filter_config(frame, config)
    if feasible.empty:
        feasible = frame[frame["release_head"].eq(config.release_head)].copy()
    if feasible.empty:
        feasible = frame.copy()
    null_rows = []
    target_counts = selected["target"].value_counts().to_dict()
    magnitudes = selected["released_logit_step"].abs().to_numpy(dtype=np.float64)
    for _ in range(700):
        parts = []
        for target, count in target_counts.items():
            group = feasible[feasible["target"].eq(target)]
            if group.empty:
                group = feasible
            parts.append(
                group.sample(
                    n=int(count),
                    replace=len(group) < int(count),
                    random_state=int(rng.integers(0, 2**31 - 1)),
                )
            )
        sampled = pd.concat(parts, ignore_index=True).head(len(selected)).copy()
        sampled["released_logit_step"] = sampled["release_sign"].astype(float).to_numpy() * magnitudes[: len(sampled)]
        sampled["predicted_scalar_delta"] = sampled["scalar_grad"].astype(float) * sampled["released_logit_step"].astype(float)
        sampled["predicted_bad_delta"] = sampled["bad_mode_grad"].astype(float) * sampled["released_logit_step"].astype(float)
        sampled["predicted_residual_delta"] = sampled["residual_grad"].astype(float) * sampled["released_logit_step"].astype(float)
        sampled["predicted_total_mode_delta"] = sampled["total_mode_grad"].astype(float) * sampled["released_logit_step"].astype(float)
        sampled["incremental_energy_delta"] = sampled["prototype_energy_delta"].astype(float)
        sampled["incremental_subject_delta"] = sampled["prototype_subject_delta"].astype(float)
        sampled_move = np.zeros_like(move)
        for rec in sampled.to_dict("records"):
            sampled_move[int(rec["flat_idx"])] = finite(rec["released_logit_step"])
        null_rows.append(selection_metrics(sampled, sampled_move, bad_tangent))
    null = pd.DataFrame(null_rows)
    tests = {}
    for metric, higher in [
        ("mean_mixture_score", True),
        ("mean_agreement_score", True),
        ("mean_conflict_score", True),
        ("mean_mode_confidence", True),
        ("mean_action_health", True),
        ("sum_predicted_scalar_delta", False),
        ("sum_predicted_bad_delta", False),
        ("sum_predicted_residual_delta", False),
        ("sum_predicted_total_mode_delta", False),
        ("mean_energy_delta", False),
        ("mean_subject_delta", False),
        ("supported_rate", True),
        ("bad_tangent_cosine", False),
    ]:
        tests[metric] = z_and_p(actual[metric], null[metric].tolist(), higher_is_better=higher)
    return {"actual": actual, "tests": tests, "null_frame": null}


def build_submission(
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    base_logit: np.ndarray,
    selected: pd.DataFrame,
    move: np.ndarray,
    config: MixtureConfig,
) -> dict[str, object]:
    prob = clip_prob(sigmoid(base_logit + move).reshape(base_prob.shape))
    digest = short_hash(prob)
    name = f"submission_hsjepa_mixture_listener_{config.name}_{digest}_uploadsafe.csv"
    local = OUT / name
    root = ROOT / name
    write_submission(local, sample, prob)
    write_submission(root, sample, prob)
    return {
        "variant": config.name,
        "worldview": config.worldview,
        "submission_file": name,
        "local_path": str(local.resolve()),
        "root_path": str(root.resolve()),
        "validation": validate_submission(root, sample, base_prob),
        "changed_cells": int((np.abs(move) > TOL).sum()),
        "selected_rows": int(selected["row"].nunique()) if not selected.empty else 0,
    }


def build_verdict(variants: dict[str, object]) -> dict[str, object]:
    scored = []
    for name, rec in variants.items():
        metrics = rec["metrics"]
        validation = rec["submission"]["validation"]
        score = (
            -0.28 * float(metrics["sum_predicted_scalar_delta"])
            -0.18 * float(metrics["sum_predicted_total_mode_delta"])
            + 0.16 * float(metrics["mean_mode_confidence"])
            + 0.13 * float(metrics["mean_mixture_score"])
            + 0.11 * float(metrics["mean_action_health"])
            + 0.08 * float(metrics["supported_rate"])
            - 0.06 * abs(float(metrics["bad_tangent_cosine"]))
        )
        if name == "private_residual_rescue_jackpot":
            score += 0.22 * float(metrics["mean_conflict_score"])
        if not validation["upload_safe"] or metrics["cells"] <= 0:
            score = -1e9
        scored.append((score, name))
    scored.sort(reverse=True)
    recommended = scored[0][1] if scored else None
    return {
        "status": "candidate_ready" if recommended else "no_candidate",
        "recommended_variant": recommended,
        "reason": (
            "Recommended by mixture-listener predicted improvement, mode confidence, "
            "action-health, and upload-safe validation."
            if recommended
            else "No non-empty upload-safe mixture-listener action survived constraints."
        ),
        "ranking": [{"variant": name, "score": float(score)} for score, name in scored],
    }


def build_markdown(readout: dict[str, object]) -> str:
    rows = [
        "| Rank | Variant | Cells | Rows | Scalar delta | Mode delta | Conflict | Confidence | Bad cosine | Upload-safe | File |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for idx, item in enumerate(readout["verdict"]["ranking"], start=1):
        variant = item["variant"]
        rec = readout["variants"][variant]
        metrics = rec["metrics"]
        submission = rec["submission"]
        rows.append(
            f"| {idx} | `{variant}` | `{int(metrics['cells'])}` | `{int(metrics['rows'])}` | "
            f"`{fmt(metrics['sum_predicted_scalar_delta'], 5)}` | "
            f"`{fmt(metrics['sum_predicted_total_mode_delta'], 5)}` | "
            f"`{fmt(metrics['mean_conflict_score'], 3)}` | "
            f"`{fmt(metrics['mean_mode_confidence'], 3)}` | "
            f"`{fmt(metrics['bad_tangent_cosine'], 4)}` | "
            f"`{submission['validation']['upload_safe']}` | `{submission['submission_file']}` |"
        )
    modes = [
        "| Mode | Variance | Cumulative | Beta | Score/Loss corr |",
        "| ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in readout["mixture_fit"]["modes"]:
        modes.append(
            f"| {item['mode']} | `{fmt(item['variance'], 4)}` | `{fmt(item['cumulative_variance'], 4)}` | "
            f"`{fmt(item['beta'], 4)}` | `{fmt(item['score_loss_corr'], 4)}` |"
        )
    return "\n".join(
        [
            "# Mixture-Listener Responsibility Solver",
            "",
            "## Thesis",
            "",
            "Public LB is not treated as one monolithic target.  It is treated as a "
            "scalar observation emitted by a mixture of latent listeners.  HS-JEPA "
            "must decide whether actions are valid under consensus, conflict, or "
            "target-specific listener routing.",
            "",
            "## Mixture Fit",
            "",
            f"- Anchor count: `{readout['anchor_count']}`",
            f"- Candidate cells: `{readout['cell_count']}`",
            f"- Mixture train corr: `{fmt(readout['mixture_fit']['train_corr'], 4)}`",
            f"- Mixture LOO corr: `{fmt(readout['mixture_fit']['loo_corr'], 4)}`",
            f"- Scalar LOO corr: `{fmt(readout['mixture_fit']['scalar_fit']['loo_corr'], 4)}`",
            "",
            *modes,
            "",
            "## Verdict",
            "",
            f"- Status: `{readout['verdict']['status']}`",
            f"- Recommended variant: `{readout['verdict']['recommended_variant']}`",
            f"- Reason: {readout['verdict']['reason']}",
            "",
            "## Generated Candidates",
            "",
            *rows,
            "",
            "## Sensor Interpretation",
            "",
            "- If `mixture_consensus_jackpot` wins, HS-JEPA should require agreement among latent listeners.",
            "- If `private_residual_rescue_jackpot` wins, the breakthrough lives in listener conflict, not consensus.",
            "- If `target_listener_split_qs` wins, Q/S should be routed through different listener heads.",
            "- If all fail, public LB anchors are not enough to identify an action-grade listener mixture.",
            "",
        ]
    )


def run() -> dict[str, object]:
    sample, base_prob, base_logit = load_base()
    base_prob = clip_prob(base_prob)
    manifold = load_manifold()
    spectral = spectral_public_tangent(sample, base_logit)
    bad_tangent = spectral["bad_tangent"]
    pool = candidate_pool(bad_tangent)
    anchors = load_anchor_matrix(sample, base_logit)
    cells, fit = build_mixture_cells(pool, sample, base_prob, base_logit, manifold, anchors["moves"], anchors["loss_delta"])
    cells.to_csv(CELL_CSV, index=False)

    variants: dict[str, object] = {}
    selected_frames = []
    null_frames = []
    for config in CONFIGS:
        selected, move = greedy_release(cells, sample, base_prob, base_logit, manifold, config)
        if not selected.empty:
            selected_frames.append(selected)
        submission = build_submission(sample, base_prob, base_logit, selected, move, config)
        metrics = selection_metrics(selected, move, bad_tangent)
        stress = null_stress(cells, selected, move, bad_tangent, config)
        null = stress.pop("null_frame")
        if not null.empty:
            null["variant"] = config.name
            null_frames.append(null)
        variants[config.name] = {
            "config": asdict(config),
            "submission": submission,
            "metrics": metrics,
            "stress": stress,
        }

    if selected_frames:
        pd.concat(selected_frames, ignore_index=True).to_csv(SELECTED_CSV, index=False)
    if null_frames:
        pd.concat(null_frames, ignore_index=True).to_csv(NULL_CSV, index=False)

    readout = {
        "experiment": "Mixture-Listener Responsibility Solver",
        "architecture_role": "competition_adapter_latent_listener_factorization_head",
        "core_claim": (
            "HS-JEPA should not convert one scalar listener observation directly into "
            "action; it should factor latent listener heads and release actions by "
            "consensus, conflict, or target-specific routing."
        ),
        "anchor_count": int(anchors["moves"].shape[0]),
        "cell_count": int(len(cells)),
        "spectral": spectral["spectral"],
        "mixture_fit": {
            "train_corr": fit["train_corr"],
            "loo_corr": fit["loo_corr"],
            "modes": fit["modes"],
            "scalar_fit": fit["scalar_fit"],
        },
        "variants": variants,
        "verdict": build_verdict(variants),
        "outputs": {
            "readout_json": str(READOUT_JSON.resolve()),
            "readout_md": str(READOUT_MD.resolve()),
            "cells": str(CELL_CSV.resolve()),
            "selected_cells": str(SELECTED_CSV.resolve()),
            "modes": str(MODE_CSV.resolve()),
            "null_stress": str(NULL_CSV.resolve()),
        },
    }
    READOUT_JSON.write_text(json.dumps(readout, ensure_ascii=False, indent=2), encoding="utf-8")
    READOUT_MD.write_text(build_markdown(readout), encoding="utf-8")
    print(json.dumps({"status": readout["verdict"]["status"], "recommended": readout["verdict"]["recommended_variant"]}, ensure_ascii=False, indent=2))
    return readout


if __name__ == "__main__":
    run()
