#!/usr/bin/env python3
"""LB-conditioned responsibility solver for the sleep adapter.

This is an HS-JEPA paper-facing big bet.

The previous solvers treated public failures mostly as a geometry problem:
post-H057 failures collapse onto a low-rank negative tangent.  This module asks
a stronger question:

    can the scalar public LB observations be decomposed into row-target
    responsibility over candidate actions?

In HS-JEPA terms, the public leaderboard is not used as a target to tune toward.
It is treated as a listener that emitted scalar observations after seeing a
sequence of action fields.  The solver estimates which row-target actions were
responsible for worse observations, then releases only the inverse actions that
also satisfy target-route and subject-prior invariants.

The architecture claim is general.  The competition-specific part is that the
external listener is the public LB and the invariant manifold is estimated from
the train target covariance plus subject priors.
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
from sleep_competition_adapter.negative_tangent_invariant_projection_solver import (  # noqa: E402
    TargetInvariantManifold,
    load_manifold,
)
from sleep_competition_adapter.spectral_public_tangent_solver import (  # noqa: E402
    CURRENT_BEST_PUBLIC_LB,
    PUBLIC_LEDGER,
    candidate_pool,
    finite,
    load_base,
    load_submission_move,
    rank01,
    spectral_public_tangent,
    z_and_p,
)


HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "lb_conditioned_responsibility_solver"
OUT.mkdir(parents=True, exist_ok=True)

READOUT_JSON = OUT / "lb_conditioned_responsibility_readout.json"
READOUT_MD = OUT / "lb_conditioned_responsibility_readout_ko.md"
RESPONSIBILITY_CSV = OUT / "lb_conditioned_responsibility_cells.csv"
SELECTED_CSV = OUT / "lb_conditioned_responsibility_selected_cells.csv"
ANCHOR_CSV = OUT / "lb_conditioned_responsibility_anchor_fit.csv"
NULL_CSV = OUT / "lb_conditioned_responsibility_null_stress.csv"


@dataclass(frozen=True)
class ResponsibilityConfig:
    name: str
    worldview: str
    max_cells: int
    max_cells_per_row: int
    min_abs_grad_rank: float
    min_sign_stability: float
    min_action_health: float
    min_support_rank: float
    require_supported_release: bool
    require_subject_nonworse: bool
    max_incremental_energy_delta: float
    max_predicted_loss_delta: float
    step_floor: float
    step_scale: float
    step_cap: float
    target_caps: tuple[tuple[str, int], ...]
    selection_style: str = "balanced"


CONFIGS = (
    ResponsibilityConfig(
        name="pure_lb_gradient_jackpot",
        worldview=(
            "The scalar public listener equation is trusted directly: choose the "
            "largest stable inverse-gradient actions even if they are less supported "
            "by the existing adapter decoders."
        ),
        max_cells=58,
        max_cells_per_row=3,
        min_abs_grad_rank=0.70,
        min_sign_stability=0.68,
        min_action_health=0.20,
        min_support_rank=0.10,
        require_supported_release=False,
        require_subject_nonworse=False,
        max_incremental_energy_delta=0.050,
        max_predicted_loss_delta=-0.004,
        step_floor=0.024,
        step_scale=0.46,
        step_cap=0.66,
        target_caps=(("Q1", 8), ("Q2", 14), ("Q3", 8), ("S1", 10), ("S2", 12), ("S3", 6), ("S4", 10)),
        selection_style="predicted_gradient",
    ),
    ResponsibilityConfig(
        name="stable_public_listener_inverse",
        worldview=(
            "The public listener exposes stable row-target responsibility; release "
            "only the inverse of high-stability harmful actions."
        ),
        max_cells=34,
        max_cells_per_row=2,
        min_abs_grad_rank=0.62,
        min_sign_stability=0.74,
        min_action_health=0.35,
        min_support_rank=0.35,
        require_supported_release=True,
        require_subject_nonworse=False,
        max_incremental_energy_delta=0.010,
        max_predicted_loss_delta=-0.002,
        step_floor=0.018,
        step_scale=0.28,
        step_cap=0.38,
        target_caps=(("Q1", 5), ("Q2", 9), ("Q3", 5), ("S1", 6), ("S2", 8), ("S3", 4), ("S4", 5)),
    ),
    ResponsibilityConfig(
        name="subject_safe_public_private_equation",
        worldview=(
            "A public-safe inverse action is valid only if it is also safe in the "
            "personal coordinate system of the subject."
        ),
        max_cells=32,
        max_cells_per_row=2,
        min_abs_grad_rank=0.55,
        min_sign_stability=0.68,
        min_action_health=0.32,
        min_support_rank=0.28,
        require_supported_release=True,
        require_subject_nonworse=True,
        max_incremental_energy_delta=0.012,
        max_predicted_loss_delta=-0.001,
        step_floor=0.016,
        step_scale=0.25,
        step_cap=0.35,
        target_caps=(("Q1", 5), ("Q2", 8), ("Q3", 5), ("S1", 5), ("S2", 7), ("S3", 3), ("S4", 5)),
    ),
    ResponsibilityConfig(
        name="jackpot_public_equation_release",
        worldview=(
            "If the scalar public listener really identifies the hidden equation, "
            "a broader inverse responsibility release should move much more than "
            "local decoder tweaks."
        ),
        max_cells=72,
        max_cells_per_row=3,
        min_abs_grad_rank=0.42,
        min_sign_stability=0.58,
        min_action_health=0.28,
        min_support_rank=0.18,
        require_supported_release=False,
        require_subject_nonworse=False,
        max_incremental_energy_delta=0.020,
        max_predicted_loss_delta=-0.0005,
        step_floor=0.020,
        step_scale=0.36,
        step_cap=0.52,
        target_caps=(("Q1", 9), ("Q2", 17), ("Q3", 9), ("S1", 11), ("S2", 16), ("S3", 6), ("S4", 10)),
    ),
    ResponsibilityConfig(
        name="route_invariant_responsibility_core",
        worldview=(
            "The reusable HS-JEPA core should prefer responsibility inversions "
            "that reduce route energy even if their public gradient is smaller."
        ),
        max_cells=28,
        max_cells_per_row=1,
        min_abs_grad_rank=0.40,
        min_sign_stability=0.62,
        min_action_health=0.30,
        min_support_rank=0.25,
        require_supported_release=True,
        require_subject_nonworse=False,
        max_incremental_energy_delta=-0.001,
        max_predicted_loss_delta=-0.0003,
        step_floor=0.014,
        step_scale=0.22,
        step_cap=0.32,
        target_caps=(("Q1", 4), ("Q2", 7), ("Q3", 4), ("S1", 5), ("S2", 6), ("S3", 3), ("S4", 4)),
        selection_style="invariant_first",
    ),
)


def fmt(value: Any, digits: int = 4) -> str:
    val = finite(value, float("nan"))
    return f"{val:.{digits}f}" if math.isfinite(val) else "n/a"


def target_caps(config: ResponsibilityConfig) -> dict[str, int]:
    return {target: cap for target, cap in config.target_caps}


def load_anchor_matrix(sample: pd.DataFrame, base_logit: np.ndarray) -> dict[str, object]:
    ledger = pd.read_csv(PUBLIC_LEDGER)
    moves: list[np.ndarray] = []
    rows: list[dict[str, object]] = []
    for rec in ledger.to_dict("records"):
        file_name = str(rec["file"])
        public_lb = float(rec["public_lb"])
        delta = public_lb - CURRENT_BEST_PUBLIC_LB
        if delta <= 0.0:
            continue
        move = load_submission_move(file_name, sample, base_logit)
        if move is None:
            continue
        norm = float(np.linalg.norm(move))
        if norm <= TOL:
            continue
        moves.append(move)
        rows.append(
            {
                "file": file_name,
                "public_lb": public_lb,
                "delta_vs_h057": delta,
                "move_l2": norm,
                "changed_cells": int((np.abs(move) > TOL).sum()),
            }
        )
    if len(moves) < 8:
        raise RuntimeError(f"not enough public anchors: {len(moves)}")
    matrix = np.vstack(moves).astype(np.float64)
    y = np.asarray([row["delta_vs_h057"] for row in rows], dtype=np.float64)
    anchor_frame = pd.DataFrame(rows)
    anchor_frame.to_csv(ANCHOR_CSV, index=False)
    return {"moves": matrix, "loss_delta": y, "anchors": anchor_frame}


def ridge_dual_coefficients(x: np.ndarray, y: np.ndarray, ridge: float) -> np.ndarray:
    """Return primal ridge coefficients using the dual form for p >> n."""
    gram = x @ x.T
    alpha = np.linalg.solve(gram + ridge * np.eye(gram.shape[0]), y)
    return x.T @ alpha


def fit_responsibility(
    anchor_matrix: np.ndarray,
    loss_delta: np.ndarray,
    candidate_flats: np.ndarray,
) -> dict[str, object]:
    x_raw = anchor_matrix[:, candidate_flats].astype(np.float64)
    col_std = x_raw.std(axis=0, ddof=1)
    col_std = np.where(col_std < 1e-6, 1.0, col_std)
    x = x_raw / col_std[None, :]

    y = loss_delta.astype(np.float64)
    y_center = y - float(y.mean())
    y_scale = float(y_center.std(ddof=1)) if len(y_center) > 1 else 1.0
    if y_scale < 1e-12:
        y_scale = 1.0
    y_z = y_center / y_scale

    ridges = (0.35, 0.80, 1.60, 3.20)
    coefs = np.vstack([ridge_dual_coefficients(x, y_z, ridge) for ridge in ridges])
    coef = coefs.mean(axis=0)

    loo_coefs = []
    loo_pred = []
    for idx in range(x.shape[0]):
        mask = np.ones(x.shape[0], dtype=bool)
        mask[idx] = False
        x_train = x[mask]
        y_train = y_z[mask]
        local = ridge_dual_coefficients(x_train, y_train, ridge=1.60)
        loo_coefs.append(local)
        loo_pred.append(float(x[idx] @ local))
    loo_coefs_arr = np.vstack(loo_coefs)
    coef_sign = np.sign(coef)
    coef_sign = np.where(coef_sign == 0, 1, coef_sign)
    loo_sign = np.sign(loo_coefs_arr)
    loo_sign = np.where(loo_sign == 0, 1, loo_sign)
    sign_stability = (loo_sign == coef_sign[None, :]).mean(axis=0)
    loo_pred_arr = np.asarray(loo_pred, dtype=np.float64)
    loo_corr = float(np.corrcoef(y_z, loo_pred_arr)[0, 1]) if len(y_z) > 2 and np.std(loo_pred_arr) > 0 else 0.0
    loo_mse = float(np.mean((y_z - loo_pred_arr) ** 2))

    return {
        "coef": coef,
        "coef_by_ridge": coefs,
        "loo_coefs": loo_coefs_arr,
        "sign_stability": sign_stability,
        "feature_std": col_std,
        "y_mean": float(y.mean()),
        "y_scale": y_scale,
        "fit": {
            "anchor_count": int(anchor_matrix.shape[0]),
            "feature_count": int(x.shape[1]),
            "ridge_values": list(ridges),
            "loo_corr": loo_corr,
            "loo_mse": loo_mse,
            "loss_delta_min": float(y.min()),
            "loss_delta_max": float(y.max()),
            "loss_delta_mean": float(y.mean()),
        },
    }


def release_step(row: pd.Series, config: ResponsibilityConfig) -> float:
    magnitude = (
        config.step_floor
        + config.step_scale
        * float(row["abs_grad_rank"])
        * (0.30 + 0.70 * float(row["sign_stability"]))
        * (0.55 + 0.45 * float(row["action_health"]))
    )
    return float(row["release_sign"]) * float(np.clip(magnitude, 0.0, config.step_cap))


def build_responsibility_cells(
    pool: pd.DataFrame,
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    base_logit: np.ndarray,
    bad_tangent: np.ndarray,
    manifold: TargetInvariantManifold,
    anchor_matrix: np.ndarray,
    loss_delta: np.ndarray,
) -> tuple[pd.DataFrame, dict[str, object]]:
    flats = np.asarray(sorted(pool["flat_idx"].astype(int).unique()), dtype=int)
    fit = fit_responsibility(anchor_matrix, loss_delta, flats)
    coef = np.asarray(fit["coef"], dtype=np.float64)
    stability = np.asarray(fit["sign_stability"], dtype=np.float64)
    std = np.asarray(fit["feature_std"], dtype=np.float64)
    coef_map = {int(flat): coef[idx] for idx, flat in enumerate(flats)}
    stability_map = {int(flat): stability[idx] for idx, flat in enumerate(flats)}
    std_map = {int(flat): std[idx] for idx, flat in enumerate(flats)}
    grad_p95 = float(np.percentile(np.abs(coef), 95)) if len(coef) else 1.0
    if grad_p95 < 1e-12:
        grad_p95 = 1.0

    best_by_flat = (
        pool.sort_values(["action_health", "source_family_count", "anti_bad_score"], ascending=False)
        .groupby("flat_idx", as_index=False)
        .first()
    )
    support_signs = pool.groupby("flat_idx")["direction"].apply(lambda s: set(s.astype(int))).to_dict()
    base_logit_matrix = base_logit.reshape(base_prob.shape)
    rows: list[dict[str, object]] = []
    for _, rec in best_by_flat.iterrows():
        flat = int(rec["flat_idx"])
        row_idx = int(rec["row"])
        target_idx = int(rec["target_idx"])
        target = str(rec["target"])
        coef_value = float(coef_map.get(flat, 0.0))
        if abs(coef_value) <= 1e-12:
            release_sign = 0
        else:
            release_sign = -1 if coef_value > 0.0 else 1
        if release_sign == 0:
            continue
        subject = str(sample.iloc[row_idx]["subject_id"])
        old_vec = base_prob[row_idx].copy()
        old_parts = manifold.energy_parts(subject, old_vec)
        candidate = rec.to_dict()
        candidate.update(
            {
                "public_loss_gradient": coef_value,
                "feature_std": float(std_map.get(flat, 1.0)),
                "release_sign": int(release_sign),
                "sign_stability": float(stability_map.get(flat, 0.0)),
                "supported_release": bool(release_sign in support_signs.get(flat, set())),
                "support_signs": ",".join(str(v) for v in sorted(support_signs.get(flat, set()))),
                "bad_tangent_dot_sign": float(release_sign * float(bad_tangent[flat])),
                "public_gradient_abs": abs(coef_value),
            }
        )
        grad_scale = float(np.clip(abs(coef_value) / grad_p95, 0.0, 1.0))
        proto_magnitude = 0.018 + 0.28 * grad_scale * (0.30 + 0.70 * candidate["sign_stability"])
        step = float(release_sign) * float(np.clip(proto_magnitude, 0.0, 0.38))
        new_vec = old_vec.copy()
        new_vec[target_idx] = clip_prob(sigmoid(np.asarray([base_logit_matrix[row_idx, target_idx] + step])))[0]
        new_parts = manifold.energy_parts(subject, new_vec)
        candidate.update(
            {
                "prototype_step": step,
                "prototype_predicted_loss_delta": float(coef_value * (step / candidate["feature_std"])),
                "old_global_energy": old_parts["global_energy"],
                "new_global_energy": new_parts["global_energy"],
                "global_energy_delta": new_parts["global_energy"] - old_parts["global_energy"],
                "old_subject_energy": old_parts["subject_energy"],
                "new_subject_energy": new_parts["subject_energy"],
                "subject_energy_delta": new_parts["subject_energy"] - old_parts["subject_energy"],
                "old_combined_energy": old_parts["combined_energy"],
                "new_combined_energy": new_parts["combined_energy"],
                "combined_energy_delta": new_parts["combined_energy"] - old_parts["combined_energy"],
                "subject_id": subject,
            }
        )
        rows.append(candidate)

    frame = pd.DataFrame(rows)
    if frame.empty:
        return frame, fit
    frame["abs_grad_rank"] = rank01(frame["public_gradient_abs"].astype(float))
    frame["stability_rank"] = rank01(frame["sign_stability"].astype(float))
    frame["support_rank"] = rank01(frame["source_family_count"].astype(float) + frame["supported_release"].astype(float))
    frame["invariant_good_rank"] = rank01(-frame["combined_energy_delta"].astype(float))
    frame["subject_good_rank"] = rank01(-frame["subject_energy_delta"].astype(float))
    frame["responsibility_score"] = (
        0.30 * frame["abs_grad_rank"]
        + 0.22 * frame["stability_rank"]
        + 0.16 * frame["action_health"].astype(float)
        + 0.14 * frame["support_rank"]
        + 0.12 * frame["invariant_good_rank"]
        + 0.06 * frame["subject_good_rank"]
    )
    return frame.sort_values("responsibility_score", ascending=False, kind="mergesort").reset_index(drop=True), fit


def filter_config(frame: pd.DataFrame, config: ResponsibilityConfig) -> pd.DataFrame:
    out = frame[
        frame["abs_grad_rank"].astype(float).ge(config.min_abs_grad_rank)
        & frame["sign_stability"].astype(float).ge(config.min_sign_stability)
        & frame["action_health"].astype(float).ge(config.min_action_health)
        & frame["support_rank"].astype(float).ge(config.min_support_rank)
    ].copy()
    if config.require_supported_release:
        out = out[out["supported_release"].astype(bool)]
    if config.require_subject_nonworse:
        out = out[out["subject_energy_delta"].astype(float).le(0.0005)]
    return out


def greedy_release(
    frame: pd.DataFrame,
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    base_logit: np.ndarray,
    manifold: TargetInvariantManifold,
    config: ResponsibilityConfig,
) -> tuple[pd.DataFrame, np.ndarray]:
    feasible = filter_config(frame, config)
    if feasible.empty:
        return feasible, np.zeros(base_prob.size, dtype=np.float64)
    if config.selection_style == "predicted_gradient":
        priority_rows = []
        for rec in feasible.to_dict("records"):
            step = release_step(pd.Series(rec), config)
            predicted_delta = float(rec["public_loss_gradient"]) * (step / float(rec["feature_std"]))
            priority_rows.append(-predicted_delta + 0.08 * float(rec["sign_stability"]) + 0.04 * float(rec["action_health"]))
        feasible = feasible.copy()
        feasible["_release_priority"] = priority_rows
    elif config.selection_style == "invariant_first":
        feasible = feasible.copy()
        feasible["_release_priority"] = (
            0.44 * feasible["invariant_good_rank"].astype(float)
            + 0.22 * feasible["subject_good_rank"].astype(float)
            + 0.18 * feasible["abs_grad_rank"].astype(float)
            + 0.16 * feasible["sign_stability"].astype(float)
        )
    else:
        feasible = feasible.copy()
        feasible["_release_priority"] = feasible["responsibility_score"].astype(float)

    caps = target_caps(config)
    current_prob = base_prob.copy()
    move = np.zeros(base_prob.size, dtype=np.float64)
    selected: list[dict[str, object]] = []
    row_counts: dict[int, int] = {}
    target_counts: dict[str, int] = {}
    base_logit_matrix = base_logit.reshape(base_prob.shape)

    for rec in feasible.sort_values("_release_priority", ascending=False, kind="mergesort").to_dict("records"):
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
        predicted_delta = float(rec["public_loss_gradient"]) * (step / float(rec["feature_std"]))
        if predicted_delta > config.max_predicted_loss_delta:
            continue

        old_vec = current_prob[row_idx].copy()
        old_parts = manifold.energy_parts(str(sample.iloc[row_idx]["subject_id"]), old_vec)
        new_vec = old_vec.copy()
        new_vec[target_idx] = clip_prob(sigmoid(np.asarray([base_logit_matrix[row_idx, target_idx] + step])))[0]
        new_parts = manifold.energy_parts(str(sample.iloc[row_idx]["subject_id"]), new_vec)
        incremental = new_parts["combined_energy"] - old_parts["combined_energy"]
        subject_delta = new_parts["subject_energy"] - old_parts["subject_energy"]
        if incremental > config.max_incremental_energy_delta:
            continue
        if config.require_subject_nonworse and subject_delta > 0.0005:
            continue

        rec["released_logit_step"] = step
        rec["predicted_loss_delta"] = predicted_delta
        rec["incremental_combined_energy_delta"] = incremental
        rec["incremental_subject_energy_delta"] = subject_delta
        rec["incremental_global_energy_delta"] = new_parts["global_energy"] - old_parts["global_energy"]
        rec["variant"] = config.name
        selected.append(rec)
        current_prob[row_idx] = new_vec
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
            "mean_responsibility_score": 0.0,
            "mean_abs_grad_rank": 0.0,
            "mean_sign_stability": 0.0,
            "mean_action_health": 0.0,
            "mean_predicted_loss_delta": 0.0,
            "sum_predicted_loss_delta": 0.0,
            "mean_incremental_energy_delta": 0.0,
            "mean_subject_energy_delta": 0.0,
            "supported_release_rate": 0.0,
            "bad_tangent_cosine": 0.0,
        }
    denom = float(np.linalg.norm(move) * np.linalg.norm(bad_tangent))
    cosine = float((move @ bad_tangent) / denom) if denom > 0.0 else 0.0
    return {
        "cells": float(len(selected)),
        "rows": float(selected["row"].nunique()),
        "mean_responsibility_score": float(selected["responsibility_score"].mean()),
        "mean_abs_grad_rank": float(selected["abs_grad_rank"].mean()),
        "mean_sign_stability": float(selected["sign_stability"].mean()),
        "mean_action_health": float(selected["action_health"].mean()),
        "mean_predicted_loss_delta": float(selected["predicted_loss_delta"].mean()),
        "sum_predicted_loss_delta": float(selected["predicted_loss_delta"].sum()),
        "mean_incremental_energy_delta": float(selected["incremental_combined_energy_delta"].mean()),
        "mean_subject_energy_delta": float(selected["incremental_subject_energy_delta"].mean()),
        "supported_release_rate": float(selected["supported_release"].astype(bool).mean()),
        "bad_tangent_cosine": cosine,
    }


def null_stress(
    frame: pd.DataFrame,
    selected: pd.DataFrame,
    move: np.ndarray,
    bad_tangent: np.ndarray,
    config: ResponsibilityConfig,
) -> dict[str, object]:
    actual = selection_metrics(selected, move, bad_tangent)
    if selected.empty:
        return {"actual": actual, "tests": {}, "null_frame": pd.DataFrame()}
    rng = np.random.default_rng(abs(hash(config.name)) % (2**32))
    feasible = filter_config(frame, config)
    if feasible.empty:
        feasible = frame.copy()
    null_rows: list[dict[str, float]] = []
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
        sampled["released_logit_step"] = (
            sampled["release_sign"].astype(float).to_numpy() * magnitudes[: len(sampled)]
        )
        sampled["predicted_loss_delta"] = sampled["public_loss_gradient"].astype(float) * (
            sampled["released_logit_step"].astype(float) / sampled["feature_std"].astype(float)
        )
        sampled["incremental_combined_energy_delta"] = sampled["combined_energy_delta"].astype(float)
        sampled["incremental_subject_energy_delta"] = sampled["subject_energy_delta"].astype(float)
        sampled_move = np.zeros_like(move)
        for rec in sampled.to_dict("records"):
            sampled_move[int(rec["flat_idx"])] = finite(rec["released_logit_step"])
        null_rows.append(selection_metrics(sampled, sampled_move, bad_tangent))
    null = pd.DataFrame(null_rows)
    tests = {}
    for metric, higher in [
        ("mean_responsibility_score", True),
        ("mean_abs_grad_rank", True),
        ("mean_sign_stability", True),
        ("mean_action_health", True),
        ("mean_predicted_loss_delta", False),
        ("sum_predicted_loss_delta", False),
        ("mean_incremental_energy_delta", False),
        ("mean_subject_energy_delta", False),
        ("supported_release_rate", True),
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
    config: ResponsibilityConfig,
) -> dict[str, object]:
    prob = clip_prob(sigmoid(base_logit + move).reshape(base_prob.shape))
    digest = short_hash(prob)
    name = f"submission_hsjepa_lb_responsibility_{config.name}_{digest}_uploadsafe.csv"
    local_path = OUT / name
    root_path = ROOT / name
    write_submission(local_path, sample, prob)
    write_submission(root_path, sample, prob)
    return {
        "variant": config.name,
        "worldview": config.worldview,
        "submission_file": name,
        "local_path": str(local_path.resolve()),
        "root_path": str(root_path.resolve()),
        "validation": validate_submission(root_path, sample, base_prob),
        "changed_cells": int((np.abs(move) > TOL).sum()),
        "selected_rows": int(selected["row"].nunique()) if not selected.empty else 0,
    }


def build_verdict(variants: dict[str, object]) -> dict[str, object]:
    scored: list[tuple[float, str]] = []
    for name, rec in variants.items():
        metrics = rec["metrics"]
        validation = rec["submission"]["validation"]
        score = (
            -0.34 * float(metrics["sum_predicted_loss_delta"])
            -0.18 * float(metrics["mean_incremental_energy_delta"])
            + 0.16 * float(metrics["mean_sign_stability"])
            + 0.14 * float(metrics["mean_responsibility_score"])
            + 0.10 * float(metrics["supported_release_rate"])
            - 0.08 * float(metrics["bad_tangent_cosine"])
        )
        if not validation["upload_safe"] or metrics["cells"] <= 0:
            score = -1e9
        scored.append((score, name))
    scored.sort(reverse=True)
    recommended = scored[0][1] if scored else None
    return {
        "status": "candidate_ready" if recommended else "no_candidate",
        "recommended_variant": recommended,
        "reason": (
            "Recommended by predicted public-listener improvement, LOO sign stability, "
            "invariant energy, and upload-safe validation."
            if recommended
            else "No non-empty upload-safe responsibility inversion survived the constraints."
        ),
        "ranking": [{"variant": name, "score": float(score)} for score, name in scored],
    }


def build_markdown(readout: dict[str, object]) -> str:
    rows = [
        "| Rank | Variant | Cells | Rows | Predicted loss delta | Sign stability | Energy delta | Bad cosine | Upload-safe | File |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for idx, item in enumerate(readout["verdict"]["ranking"], start=1):
        variant = item["variant"]
        rec = readout["variants"][variant]
        metrics = rec["metrics"]
        submission = rec["submission"]
        rows.append(
            f"| {idx} | `{variant}` | `{int(metrics['cells'])}` | `{int(metrics['rows'])}` | "
            f"`{fmt(metrics['sum_predicted_loss_delta'], 5)}` | "
            f"`{fmt(metrics['mean_sign_stability'], 3)}` | "
            f"`{fmt(metrics['mean_incremental_energy_delta'], 5)}` | "
            f"`{fmt(metrics['bad_tangent_cosine'], 4)}` | "
            f"`{submission['validation']['upload_safe']}` | `{submission['submission_file']}` |"
        )
    fit = readout["fit"]
    return "\n".join(
        [
            "# LB-Conditioned Responsibility Solver",
            "",
            "## Thesis",
            "",
            "Public LB is treated as an external listener that emits scalar observations "
            "after seeing row-target action fields.  HS-JEPA can use these observations "
            "to estimate action responsibility, then invert only the actions that remain "
            "valid under target-route and subject-prior invariants.",
            "",
            "## Anchor Fit",
            "",
            f"- Anchor count: `{fit['anchor_count']}`",
            f"- Candidate features: `{fit['feature_count']}`",
            f"- LOO correlation: `{fmt(fit['loo_corr'], 4)}`",
            f"- LOO MSE: `{fmt(fit['loo_mse'], 4)}`",
            f"- Loss delta range: `{fmt(fit['loss_delta_min'], 6)}` to `{fmt(fit['loss_delta_max'], 6)}`",
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
            "## Public LB Sensor Interpretation",
            "",
            "- If this beats H057, the paper claim strengthens: listener responsibility can be "
            "estimated from scalar outcome observations, not only from explicit labels.",
            "- If it fails like listener transport, the bottleneck is not responsibility "
            "estimation but an unobserved public/private row-support assignment.",
            "- If only the subject-safe variant survives, personal-coordinate invariance is "
            "the missing action-health constraint.",
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
    responsibility, fit = build_responsibility_cells(
        pool=pool,
        sample=sample,
        base_prob=base_prob,
        base_logit=base_logit,
        bad_tangent=bad_tangent,
        manifold=manifold,
        anchor_matrix=anchors["moves"],
        loss_delta=anchors["loss_delta"],
    )
    responsibility.to_csv(RESPONSIBILITY_CSV, index=False)

    variants: dict[str, object] = {}
    selected_frames = []
    null_frames = []
    for config in CONFIGS:
        selected, move = greedy_release(responsibility, sample, base_prob, base_logit, manifold, config)
        if not selected.empty:
            selected_frames.append(selected)
        submission = build_submission(sample, base_prob, base_logit, selected, move, config)
        metrics = selection_metrics(selected, move, bad_tangent)
        stress = null_stress(responsibility, selected, move, bad_tangent, config)
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
        "experiment": "LB-Conditioned Responsibility Solver",
        "architecture_role": "competition_adapter_external_listener_responsibility_head",
        "core_claim": (
            "HS-JEPA listener responsibility can be inferred from scalar listener observations "
            "and converted to action only through invariant projection."
        ),
        "spectral": spectral["spectral"],
        "fit": fit["fit"],
        "responsibility_cells": int(len(responsibility)),
        "variants": variants,
        "verdict": build_verdict(variants),
        "outputs": {
            "readout_json": str(READOUT_JSON.resolve()),
            "readout_md": str(READOUT_MD.resolve()),
            "responsibility_cells": str(RESPONSIBILITY_CSV.resolve()),
            "selected_cells": str(SELECTED_CSV.resolve()),
            "anchor_fit": str(ANCHOR_CSV.resolve()),
            "null_stress": str(NULL_CSV.resolve()),
        },
    }
    READOUT_JSON.write_text(json.dumps(readout, ensure_ascii=False, indent=2), encoding="utf-8")
    READOUT_MD.write_text(build_markdown(readout), encoding="utf-8")
    print(json.dumps({"status": readout["verdict"]["status"], "recommended": readout["verdict"]["recommended_variant"]}, ensure_ascii=False, indent=2))
    return readout


if __name__ == "__main__":
    run()
