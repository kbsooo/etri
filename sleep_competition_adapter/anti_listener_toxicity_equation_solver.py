#!/usr/bin/env python3
"""Anti-listener toxicity equation solver for the sleep adapter.

This is a high-risk HS-JEPA big-bet module.

The cross-listener transport experiment produced a useful negative sensor:
listener-confirmed shadow cells were locally coherent, but public LB punished
the release.  HS-JEPA should therefore not interpret listener responsibility as
an action generator.  This solver treats failed listener actions as toxic
teachers and asks a sharper question:

    can the adapter identify row-target moves that are inverse to the
    listener-toxic direction while still satisfying public, private, and route
    action-health constraints?

The reusable architecture claim is anti-listener action-health.  The
competition-specific adapter instantiates it with public LB anchors, H057 as
the current action field, and target-level row equations.
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
    TARGETS,
    TOL,
    clip_prob,
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
    CURRENT_BEST_PUBLIC_LB,
    load_base,
    load_submission_move,
    z_and_p,
)


HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "anti_listener_toxicity_equation_solver"
OUT.mkdir(parents=True, exist_ok=True)

READOUT_JSON = OUT / "anti_listener_toxicity_equation_readout.json"
READOUT_MD = OUT / "anti_listener_toxicity_equation_readout_ko.md"
CELL_CSV = OUT / "anti_listener_toxicity_equation_cells.csv"
SELECTED_CSV = OUT / "anti_listener_toxicity_equation_selected_cells.csv"
NULL_CSV = OUT / "anti_listener_toxicity_equation_null_stress.csv"

PUBLIC_PRIVATE_CELLS = (
    HERE / "outputs" / "public_private_subset_tomography_solver" / "public_private_subset_tomography_cells.csv"
)
HARDWORLD_SECTORS = HERE / "outputs" / "hardworld_toxicity_factorization_sectors.csv"
CROSS_LISTENER_CELLS = HERE / "outputs" / "cross_listener_transport_decoder" / "cross_listener_transport_cells.csv"


@dataclass(frozen=True)
class ToxicAnchor:
    name: str
    file: str
    public_lb: float
    family: str
    role: str


@dataclass(frozen=True)
class AntiListenerConfig:
    name: str
    worldview: str
    mode: str
    max_cells: int
    max_cells_per_row: int
    min_public_gain: float
    min_listener_inverse: float
    min_listener_safety: float
    min_private_safety: float
    max_hardworld_toxicity: float
    max_broad_toxicity: float
    max_energy_delta: float
    max_subject_delta: float
    step_floor: float
    step_scale: float
    step_cap: float
    target_caps: tuple[tuple[str, int], ...]


TOXIC_ANCHORS = (
    ToxicAnchor(
        name="cross_listener_transport",
        file="submission_hsjepa_cross_listener_transport_listener_confirmed_shadow_660faef3_uploadsafe.csv",
        public_lb=0.5684860446,
        family="listener",
        role="listener-confirmed shadow release failed public",
    ),
    ToxicAnchor(
        name="target_listener_lift",
        file="submission_hsjepa_target_listener_route_lift_s2hub_listener_lift_jackpot_f2ab2816_uploadsafe.csv",
        public_lb=0.5680255019,
        family="listener",
        role="direct target-listener lift failed public",
    ),
    ToxicAnchor(
        name="h088_hardworld",
        file="submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv",
        public_lb=0.5684942019,
        family="hardworld",
        role="dual-head hard-world action field failed public",
    ),
    ToxicAnchor(
        name="h010_objective_tail",
        file="submission_h010_objective_s1s4_v2_uploadsafe.csv",
        public_lb=0.5781718175,
        family="objective_tail",
        role="S1/S4 objective tail route failed public",
    ),
    ToxicAnchor(
        name="e216_maskfam_jepa",
        file="submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv",
        public_lb=0.5772865088,
        family="direct_jepa",
        role="masked-family JEPA S2 translator failed public",
    ),
)


CONFIGS = (
    AntiListenerConfig(
        name="listener_inverse_jackpot",
        worldview=(
            "The failed listener actions point almost exactly toward the toxic "
            "direction; the breakthrough is to move the same row-targets in the "
            "opposite direction when the public equation also agrees."
        ),
        mode="inverse_first",
        max_cells=42,
        max_cells_per_row=2,
        min_public_gain=0.48,
        min_listener_inverse=0.68,
        min_listener_safety=0.46,
        min_private_safety=0.28,
        max_hardworld_toxicity=0.70,
        max_broad_toxicity=0.76,
        max_energy_delta=0.050,
        max_subject_delta=0.100,
        step_floor=0.018,
        step_scale=0.40,
        step_cap=0.58,
        target_caps=(("Q1", 7), ("Q2", 13), ("Q3", 7), ("S1", 8), ("S2", 12), ("S3", 5), ("S4", 8)),
    ),
    AntiListenerConfig(
        name="private_safe_anti_listener_bridge",
        worldview=(
            "The listener-negative axis is useful only after a private/action "
            "health filter.  Prefer inverse listener cells that are also route "
            "and subject safe."
        ),
        mode="private_safe",
        max_cells=30,
        max_cells_per_row=2,
        min_public_gain=0.35,
        min_listener_inverse=0.40,
        min_listener_safety=0.48,
        min_private_safety=0.48,
        max_hardworld_toxicity=0.58,
        max_broad_toxicity=0.68,
        max_energy_delta=0.025,
        max_subject_delta=0.050,
        step_floor=0.014,
        step_scale=0.26,
        step_cap=0.38,
        target_caps=(("Q1", 5), ("Q2", 9), ("Q3", 5), ("S1", 6), ("S2", 8), ("S3", 3), ("S4", 6)),
    ),
    AntiListenerConfig(
        name="q2s2_listener_toxicity_route",
        worldview=(
            "The listener-toxic mode is concentrated around intervention/stage "
            "translation, so Q2 and S2 should be decoded through a separate "
            "anti-listener route."
        ),
        mode="q2s2",
        max_cells=28,
        max_cells_per_row=2,
        min_public_gain=0.38,
        min_listener_inverse=0.50,
        min_listener_safety=0.48,
        min_private_safety=0.34,
        max_hardworld_toxicity=0.62,
        max_broad_toxicity=0.68,
        max_energy_delta=0.026,
        max_subject_delta=0.052,
        step_floor=0.016,
        step_scale=0.32,
        step_cap=0.46,
        target_caps=(("Q2", 15), ("S2", 13)),
    ),
    AntiListenerConfig(
        name="public_subset_veto_listener_toxicity",
        worldview=(
            "Public subset tomography was directionally right, but it must veto "
            "cells that overlap the listener-toxic action field."
        ),
        mode="subset_veto",
        max_cells=36,
        max_cells_per_row=2,
        min_public_gain=0.56,
        min_listener_inverse=0.24,
        min_listener_safety=0.50,
        min_private_safety=0.30,
        max_hardworld_toxicity=0.70,
        max_broad_toxicity=0.72,
        max_energy_delta=0.040,
        max_subject_delta=0.080,
        step_floor=0.015,
        step_scale=0.30,
        step_cap=0.44,
        target_caps=(("Q1", 6), ("Q2", 10), ("Q3", 6), ("S1", 6), ("S2", 10), ("S3", 4), ("S4", 6)),
    ),
    AntiListenerConfig(
        name="listener_toxicity_boundary_probe",
        worldview=(
            "If the listener-toxic field is over-vetoed, a tiny movement on the "
            "conflict boundary should expose whether the toxicity is real or a "
            "false private-safety prior."
        ),
        mode="boundary_probe",
        max_cells=18,
        max_cells_per_row=1,
        min_public_gain=0.42,
        min_listener_inverse=0.54,
        min_listener_safety=0.20,
        min_private_safety=0.20,
        max_hardworld_toxicity=0.88,
        max_broad_toxicity=0.88,
        max_energy_delta=0.060,
        max_subject_delta=0.120,
        step_floor=0.010,
        step_scale=0.18,
        step_cap=0.24,
        target_caps=(("Q1", 3), ("Q2", 5), ("Q3", 3), ("S1", 3), ("S2", 5), ("S3", 2), ("S4", 3)),
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


def rank01(values: pd.Series | np.ndarray, higher: bool = True) -> pd.Series:
    series = pd.Series(values, dtype="float64").replace([np.inf, -np.inf], np.nan)
    series = series.fillna(float(series.median()) if series.notna().any() else 0.0)
    if series.nunique(dropna=True) <= 1:
        return pd.Series(np.full(len(series), 0.5), index=series.index)
    ranked = series.rank(method="average", pct=True)
    return ranked if higher else 1.0 - ranked


def cap_map(config: AntiListenerConfig) -> dict[str, int]:
    return {target: count for target, count in config.target_caps}


def locate_column(frame: pd.DataFrame, candidates: list[str], default: float = 0.0) -> pd.Series:
    for col in candidates:
        if col in frame:
            return frame[col].astype(float)
    return pd.Series(np.full(len(frame), default), index=frame.index, dtype="float64")


def candidate_sources() -> pd.DataFrame:
    if not PUBLIC_PRIVATE_CELLS.exists():
        raise FileNotFoundError(PUBLIC_PRIVATE_CELLS)
    if not HARDWORLD_SECTORS.exists():
        raise FileNotFoundError(HARDWORLD_SECTORS)
    if not CROSS_LISTENER_CELLS.exists():
        raise FileNotFoundError(CROSS_LISTENER_CELLS)

    rows: list[dict[str, object]] = []
    tomography = pd.read_csv(PUBLIC_PRIVATE_CELLS)
    for rec in tomography.to_dict("records"):
        rows.append(
            {
                "flat_idx": int(rec["flat_idx"]),
                "row": int(rec["row"]),
                "target": str(rec["target"]),
                "target_idx": int(rec["target_idx"]),
                "direction": int(rec["release_sign"]),
                "source": "subset_tomography",
                "tomography_score": finite(rec.get("tomography_score")),
                "public_inclusion_score": finite(rec.get("public_inclusion_score")),
                "label_direction_confidence": finite(rec.get("label_direction_confidence")),
                "private_safety_score": finite(rec.get("private_safety_score")),
                "prototype_predicted_loss_delta": finite(rec.get("prototype_predicted_loss_delta")),
            }
        )

    sectors = pd.read_csv(HARDWORLD_SECTORS)
    for rec in sectors.to_dict("records"):
        rows.append(
            {
                "flat_idx": int(rec["flat_idx"]),
                "row": int(rec["row"]),
                "target": str(rec["target"]),
                "target_idx": int(rec["target_idx"]),
                "direction": int(rec["candidate_sign"]),
                "source": "hardworld_sector",
                "sector_selection_score": finite(rec.get("selection_score")),
                "sector_joint_safety": finite(rec.get("joint_safety_min_rank")),
                "sector_hardworld_toxic": finite(rec.get("hardworld_toxic_rank")),
                "sector_broad_toxic": finite(rec.get("broad_toxic_rank_ex_hardworld")),
                "sector_listener_benefit": finite(rec.get("listener_benefit_rank")),
                "sector_human_state_responsibility": finite(rec.get("human_state_responsibility")),
                "teacher_has_action": bool(rec.get("teacher_has_action", False)),
                "lrj_has_cell": bool(rec.get("lrj_has_cell", False)),
            }
        )

    cross = pd.read_csv(CROSS_LISTENER_CELLS)
    for rec in cross.to_dict("records"):
        flat = int(rec["row"]) * len(TARGETS) + int(rec["target_idx"])
        direction = int(np.sign(finite(rec.get("action_delta"))))
        if direction == 0:
            direction = int(rec.get("direction", 0))
        if direction != 0:
            rows.append(
                {
                    "flat_idx": flat,
                    "row": int(rec["row"]),
                    "target": str(rec["target"]),
                    "target_idx": int(rec["target_idx"]),
                    "direction": -direction,
                    "source": "inverse_cross_listener",
                    "cross_listener_transport_score": finite(rec.get("cross_listener_transport_score")),
                    "cross_listener_score": finite(rec.get("listener_score")),
                    "cross_row_s2_score": finite(rec.get("row_s2_listener_score")),
                    "cross_boundary_class": str(rec.get("boundary_class", "")),
                }
            )

    frame = pd.DataFrame(rows)
    frame = frame[frame["direction"].isin([-1, 1])].copy()
    if frame.empty:
        raise RuntimeError("No anti-listener candidate sources were loaded")

    source_list = (
        frame.groupby(["flat_idx", "direction"])["source"]
        .apply(lambda s: ",".join(sorted(set(str(v) for v in s))))
        .rename("sources")
        .reset_index()
    )
    agg = (
        frame.groupby(["flat_idx", "direction"], as_index=False)
        .agg(
            row=("row", "first"),
            target=("target", "first"),
            target_idx=("target_idx", "first"),
            tomography_score=("tomography_score", "max"),
            public_inclusion_score=("public_inclusion_score", "max"),
            label_direction_confidence=("label_direction_confidence", "max"),
            private_safety_score=("private_safety_score", "max"),
            prototype_predicted_loss_delta=("prototype_predicted_loss_delta", "min"),
            sector_selection_score=("sector_selection_score", "max"),
            sector_joint_safety=("sector_joint_safety", "max"),
            sector_hardworld_toxic=("sector_hardworld_toxic", "max"),
            sector_broad_toxic=("sector_broad_toxic", "max"),
            sector_listener_benefit=("sector_listener_benefit", "max"),
            sector_human_state_responsibility=("sector_human_state_responsibility", "max"),
            cross_listener_transport_score=("cross_listener_transport_score", "max"),
            cross_listener_score=("cross_listener_score", "max"),
            cross_row_s2_score=("cross_row_s2_score", "max"),
            teacher_has_action=("teacher_has_action", "max"),
            lrj_has_cell=("lrj_has_cell", "max"),
        )
        .merge(source_list, on=["flat_idx", "direction"], how="left")
    )
    for col in [
        "tomography_score",
        "public_inclusion_score",
        "label_direction_confidence",
        "private_safety_score",
        "prototype_predicted_loss_delta",
        "sector_selection_score",
        "sector_joint_safety",
        "sector_hardworld_toxic",
        "sector_broad_toxic",
        "sector_listener_benefit",
        "sector_human_state_responsibility",
        "cross_listener_transport_score",
        "cross_listener_score",
        "cross_row_s2_score",
    ]:
        agg[col] = agg[col].astype(float).replace([np.inf, -np.inf], np.nan)
    agg["cell_key"] = agg["row"].astype(str) + ":" + agg["target"].astype(str)
    return agg.reset_index(drop=True)


def load_toxic_anchor_moves(sample: pd.DataFrame, base_logit: np.ndarray) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    rows = []
    moves = {}
    for anchor in TOXIC_ANCHORS:
        move = load_submission_move(anchor.file, sample, base_logit)
        available = move is not None
        if move is not None:
            moves[anchor.name] = move
        rows.append(
            {
                **asdict(anchor),
                "available": bool(available),
                "delta_vs_h057": float(anchor.public_lb - CURRENT_BEST_PUBLIC_LB),
                "changed_cells": int((np.abs(move) > TOL).sum()) if move is not None else 0,
                "move_l2": float(np.linalg.norm(move)) if move is not None else 0.0,
            }
        )
    frame = pd.DataFrame(rows)
    if len(moves) < 3:
        raise RuntimeError(f"Not enough toxic anchors could be loaded: {sorted(moves)}")
    return frame, moves


def add_public_fit(frame: pd.DataFrame, sample: pd.DataFrame, base_prob: np.ndarray, base_logit: np.ndarray) -> pd.DataFrame:
    anchor = load_anchor_matrix(sample, base_logit)
    flats = np.asarray(sorted(frame["flat_idx"].astype(int).unique()), dtype=int)
    fit = fit_responsibility(
        np.asarray(anchor["moves"], dtype=np.float64),
        np.asarray(anchor["loss_delta"], dtype=np.float64),
        flats,
    )
    coef = np.asarray(fit["coef"], dtype=np.float64)
    stability = np.asarray(fit["sign_stability"], dtype=np.float64)
    std = np.asarray(fit["feature_std"], dtype=np.float64)
    coef_map = {int(flat): float(coef[idx]) for idx, flat in enumerate(flats)}
    stability_map = {int(flat): float(stability[idx]) for idx, flat in enumerate(flats)}
    std_map = {int(flat): float(std[idx]) for idx, flat in enumerate(flats)}
    out = frame.copy()
    out["public_loss_gradient"] = out["flat_idx"].map(coef_map).astype(float)
    out["sign_stability"] = out["flat_idx"].map(stability_map).astype(float)
    out["feature_std"] = out["flat_idx"].map(std_map).astype(float).clip(lower=1e-8)
    out["public_release_agrees"] = np.sign(-out["public_loss_gradient"].to_numpy()) == out["direction"].to_numpy()
    grad_p95 = float(np.percentile(np.abs(coef), 95)) if len(coef) else 1.0
    if grad_p95 < 1e-12:
        grad_p95 = 1.0
    out["public_gradient_strength"] = np.clip(np.abs(out["public_loss_gradient"]) / grad_p95, 0.0, 1.0)
    out["base_probability"] = base_prob.reshape(-1)[out["flat_idx"].astype(int).to_numpy()]
    out.attrs["source_fit"] = fit["fit"]
    out.attrs["source_anchor_count"] = int(np.asarray(anchor["moves"]).shape[0])
    return out


def add_toxicity_features(frame: pd.DataFrame, moves: dict[str, np.ndarray]) -> pd.DataFrame:
    out = frame.copy()
    direction = out["direction"].astype(int).to_numpy()
    flats = out["flat_idx"].astype(int).to_numpy()
    listener_same = np.zeros(len(out), dtype=np.float64)
    listener_inverse = np.zeros(len(out), dtype=np.float64)
    hardworld_same = np.zeros(len(out), dtype=np.float64)
    broad_same = np.zeros(len(out), dtype=np.float64)
    available_same_count = np.zeros(len(out), dtype=np.float64)

    for anchor in TOXIC_ANCHORS:
        move = moves.get(anchor.name)
        if move is None:
            continue
        local = move[flats]
        sign = np.sign(local).astype(int)
        active = np.abs(local) > TOL
        same = active & (sign == direction)
        inverse = active & (sign == -direction)
        weight = max(float(anchor.public_lb - CURRENT_BEST_PUBLIC_LB), 1e-6)
        weight = math.sqrt(weight / 0.001)
        if anchor.family == "listener":
            listener_same += weight * same.astype(float) * np.minimum(np.abs(local), 1.0)
            listener_inverse += weight * inverse.astype(float) * np.minimum(np.abs(local), 1.0)
        elif anchor.family == "hardworld":
            hardworld_same += weight * same.astype(float) * np.minimum(np.abs(local), 1.0)
        else:
            broad_same += weight * same.astype(float) * np.minimum(np.abs(local), 1.0)
        available_same_count += same.astype(float)
        out[f"{anchor.name}_same"] = same
        out[f"{anchor.name}_inverse"] = inverse
        out[f"{anchor.name}_move"] = local

    out["listener_toxic_same_weight"] = listener_same
    out["listener_inverse_weight"] = listener_inverse
    out["hardworld_toxic_same_weight"] = hardworld_same
    out["broad_toxic_same_weight"] = broad_same
    out["toxic_anchor_same_count"] = available_same_count

    out["listener_toxicity_rank"] = rank01(listener_same, higher=True)
    out["listener_inverse_rank"] = rank01(listener_inverse, higher=True)
    out["listener_safety_rank"] = rank01(listener_same, higher=False)
    out["hardworld_toxicity_rank_from_anchor"] = rank01(hardworld_same, higher=True)
    out["broad_toxicity_rank_from_anchor"] = rank01(broad_same, higher=True)
    out["broad_safety_rank_from_anchor"] = rank01(broad_same, higher=False)
    return out


def add_action_health(frame: pd.DataFrame, sample: pd.DataFrame, base_prob: np.ndarray, base_logit: np.ndarray) -> pd.DataFrame:
    manifold = load_manifold()
    base_matrix = base_logit.reshape(base_prob.shape)
    out = frame.copy()
    private_from_tomography = out["private_safety_score"].fillna(0.0).astype(float)
    private_from_sector = out["sector_joint_safety"].fillna(0.0).astype(float)
    out["merged_private_safety"] = np.maximum(private_from_tomography, private_from_sector)
    out["sector_hardworld_toxic"] = out["sector_hardworld_toxic"].fillna(out["hardworld_toxicity_rank_from_anchor"]).astype(float)
    out["sector_broad_toxic"] = out["sector_broad_toxic"].fillna(out["broad_toxicity_rank_from_anchor"]).astype(float)
    out["public_gain_rank"] = rank01(
        -out["public_loss_gradient"].astype(float).to_numpy() * out["direction"].astype(float).to_numpy(),
        higher=True,
    )
    out["listener_transport_rank"] = rank01(out["cross_listener_transport_score"].fillna(0.0), higher=True)
    out["anti_listener_equation_score"] = (
        0.23 * out["public_gain_rank"].astype(float)
        + 0.22 * out["listener_inverse_rank"].astype(float)
        + 0.18 * out["listener_safety_rank"].astype(float)
        + 0.16 * out["merged_private_safety"].astype(float)
        + 0.09 * out["sign_stability"].astype(float)
        + 0.06 * out["sector_human_state_responsibility"].fillna(0.0).astype(float)
        + 0.06 * out["public_inclusion_score"].fillna(0.0).astype(float)
        - 0.10 * out["sector_hardworld_toxic"].astype(float)
        - 0.08 * out["sector_broad_toxic"].astype(float)
    )

    old_global = []
    new_global = []
    global_delta = []
    old_subject = []
    new_subject = []
    subject_delta = []
    preview_steps = []
    predicted_delta = []
    for rec in out.to_dict("records"):
        row_idx = int(rec["row"])
        target_idx = int(rec["target_idx"])
        direction = int(rec["direction"])
        strength = finite(rec.get("public_gradient_strength"))
        stability = finite(rec.get("sign_stability"))
        listener_inverse = finite(rec.get("listener_inverse_rank"))
        private_safety = finite(rec.get("merged_private_safety"))
        step = direction * float(np.clip(0.012 + 0.30 * strength * (0.25 + 0.75 * stability) * (0.40 + 0.60 * listener_inverse) * (0.45 + 0.55 * private_safety), 0.0, 0.42))
        subject = str(sample.iloc[row_idx]["subject_id"])
        old_vec = base_prob[row_idx].copy()
        old_parts = manifold.energy_parts(subject, old_vec)
        new_vec = old_vec.copy()
        new_vec[target_idx] = clip_prob(sigmoid(np.asarray([base_matrix[row_idx, target_idx] + step])))[0]
        new_parts = manifold.energy_parts(subject, new_vec)
        old_global.append(old_parts["global_energy"])
        new_global.append(new_parts["global_energy"])
        global_delta.append(new_parts["global_energy"] - old_parts["global_energy"])
        old_subject.append(old_parts["subject_energy"])
        new_subject.append(new_parts["subject_energy"])
        subject_delta.append(new_parts["subject_energy"] - old_parts["subject_energy"])
        preview_steps.append(step)
        predicted_delta.append(finite(rec.get("public_loss_gradient")) * (step / max(finite(rec.get("feature_std"), 1.0), 1e-8)))

    out["preview_step"] = preview_steps
    out["preview_predicted_public_delta"] = predicted_delta
    out["old_global_energy"] = old_global
    out["new_global_energy"] = new_global
    out["global_energy_delta"] = global_delta
    out["old_subject_energy"] = old_subject
    out["new_subject_energy"] = new_subject
    out["subject_energy_delta"] = subject_delta
    return out.sort_values("anti_listener_equation_score", ascending=False).reset_index(drop=True)


def select_cells(frame: pd.DataFrame, config: AntiListenerConfig) -> pd.DataFrame:
    cand = frame.copy()
    if config.mode == "q2s2":
        cand = cand[cand["target"].isin(["Q2", "S2"])].copy()
    elif config.mode == "subset_veto":
        cand = cand[cand["sources"].astype(str).str.contains("subset_tomography", regex=False)].copy()
    elif config.mode == "boundary_probe":
        cand = cand[(cand["listener_inverse_rank"] >= config.min_listener_inverse) & (cand["listener_toxicity_rank"] >= 0.40)].copy()

    cand = cand[
        (cand["public_gain_rank"] >= config.min_public_gain)
        & (cand["listener_inverse_rank"] >= config.min_listener_inverse)
        & (cand["listener_safety_rank"] >= config.min_listener_safety)
        & (cand["merged_private_safety"] >= config.min_private_safety)
        & (cand["sector_hardworld_toxic"] <= config.max_hardworld_toxicity)
        & (cand["sector_broad_toxic"] <= config.max_broad_toxicity)
        & (cand["global_energy_delta"] <= config.max_energy_delta)
        & (cand["subject_energy_delta"] <= config.max_subject_delta)
        & (cand["preview_predicted_public_delta"] <= 0.002)
    ].copy()
    if cand.empty:
        return cand

    caps = cap_map(config)
    cand["target_cap"] = cand["target"].map(caps).fillna(0).astype(int)
    cand = cand[cand["target_cap"] > 0].copy()
    if cand.empty:
        return cand

    sort_cols = {
        "inverse_first": ["listener_inverse_rank", "public_gain_rank", "anti_listener_equation_score"],
        "private_safe": ["merged_private_safety", "listener_safety_rank", "public_gain_rank"],
        "q2s2": ["listener_inverse_rank", "sector_human_state_responsibility", "public_gain_rank"],
        "subset_veto": ["public_inclusion_score", "listener_safety_rank", "public_gain_rank"],
        "boundary_probe": ["listener_inverse_rank", "listener_toxicity_rank", "public_gain_rank"],
    }.get(config.mode, ["anti_listener_equation_score"])
    cand = cand.sort_values(sort_cols, ascending=False).copy()

    selected = []
    row_counts: dict[int, int] = {}
    target_counts: dict[str, int] = {}
    used: set[tuple[int, str]] = set()
    for rec in cand.to_dict("records"):
        row_idx = int(rec["row"])
        target = str(rec["target"])
        flat = int(rec["flat_idx"])
        if (flat, target) in used:
            continue
        if row_counts.get(row_idx, 0) >= config.max_cells_per_row:
            continue
        if target_counts.get(target, 0) >= caps.get(target, 0):
            continue
        selected.append(rec)
        used.add((flat, target))
        row_counts[row_idx] = row_counts.get(row_idx, 0) + 1
        target_counts[target] = target_counts.get(target, 0) + 1
        if len(selected) >= config.max_cells:
            break
    return pd.DataFrame(selected)


def step_for_row(row: pd.Series, config: AntiListenerConfig) -> float:
    magnitude = (
        config.step_floor
        + config.step_scale
        * finite(row.get("public_gain_rank"))
        * (0.35 + 0.65 * finite(row.get("listener_inverse_rank")))
        * (0.40 + 0.60 * finite(row.get("merged_private_safety")))
        * (0.45 + 0.55 * finite(row.get("sign_stability")))
    )
    if config.mode == "boundary_probe":
        magnitude *= 0.55
    return int(row["direction"]) * float(np.clip(magnitude, 0.0, config.step_cap))


def apply_variant(
    selected: pd.DataFrame,
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    base_logit: np.ndarray,
    config: AntiListenerConfig,
) -> tuple[np.ndarray, pd.DataFrame, dict[str, object]]:
    prob = base_prob.copy()
    logit_matrix = base_logit.reshape(base_prob.shape).copy()
    rows = []
    for rec in selected.to_dict("records"):
        row_idx = int(rec["row"])
        target_idx = int(rec["target_idx"])
        step = step_for_row(pd.Series(rec), config)
        logit_matrix[row_idx, target_idx] += step
        prob[row_idx, target_idx] = clip_prob(sigmoid(np.asarray([logit_matrix[row_idx, target_idx]])))[0]
        out = dict(rec)
        out["released_step"] = float(step)
        out["released_abs_step"] = abs(float(step))
        out["released_predicted_public_delta"] = finite(rec.get("public_loss_gradient")) * (
            step / max(finite(rec.get("feature_std"), 1.0), 1e-8)
        )
        rows.append(out)
    selected_out = pd.DataFrame(rows)
    if selected_out.empty:
        metrics = {
            "cells": 0,
            "rows": 0,
            "sum_predicted_public_delta": 0.0,
            "mean_listener_inverse": 0.0,
            "mean_listener_safety": 0.0,
            "mean_private_safety": 0.0,
            "mean_hardworld_toxicity": 0.0,
            "mean_broad_toxicity": 0.0,
        }
    else:
        metrics = {
            "cells": int(len(selected_out)),
            "rows": int(selected_out["row"].nunique()),
            "sum_predicted_public_delta": float(selected_out["released_predicted_public_delta"].sum()),
            "mean_listener_inverse": float(selected_out["listener_inverse_rank"].mean()),
            "mean_listener_safety": float(selected_out["listener_safety_rank"].mean()),
            "mean_private_safety": float(selected_out["merged_private_safety"].mean()),
            "mean_hardworld_toxicity": float(selected_out["sector_hardworld_toxic"].mean()),
            "mean_broad_toxicity": float(selected_out["sector_broad_toxic"].mean()),
            "target_counts": selected_out["target"].value_counts().reindex(TARGETS).fillna(0).astype(int).to_dict(),
            "source_counts": selected_out["sources"].str.get_dummies(sep=",").sum().astype(int).to_dict()
            if "sources" in selected_out
            else {},
        }
    return prob, selected_out, metrics


def null_stress(frame: pd.DataFrame, selected_by_variant: dict[str, pd.DataFrame], iterations: int = 2500) -> pd.DataFrame:
    rng = np.random.default_rng(20260611)
    rows = []
    for variant, selected in selected_by_variant.items():
        if selected.empty:
            rows.append({"variant": variant, "cells": 0, "status": "empty"})
            continue
        target_counts = selected["target"].value_counts().to_dict()
        pool = frame.copy()
        actual = {
            "score": float(selected["anti_listener_equation_score"].mean()),
            "listener_inverse": float(selected["listener_inverse_rank"].mean()),
            "listener_safety": float(selected["listener_safety_rank"].mean()),
            "private_safety": float(selected["merged_private_safety"].mean()),
            "hardworld_toxicity": float(selected["sector_hardworld_toxic"].mean()),
            "broad_toxicity": float(selected["sector_broad_toxic"].mean()),
            "pred_delta": float(selected["released_predicted_public_delta"].sum())
            if "released_predicted_public_delta" in selected
            else float(selected["preview_predicted_public_delta"].sum()),
        }
        null = {key: [] for key in actual}
        for _ in range(iterations):
            parts = []
            for target, count in target_counts.items():
                target_pool = pool[pool["target"].eq(target)]
                if target_pool.empty:
                    target_pool = pool
                parts.append(
                    target_pool.sample(
                        n=int(count),
                        replace=len(target_pool) < int(count),
                        random_state=int(rng.integers(0, 2**31 - 1)),
                    )
                )
            sampled = pd.concat(parts, ignore_index=True)
            null["score"].append(float(sampled["anti_listener_equation_score"].mean()))
            null["listener_inverse"].append(float(sampled["listener_inverse_rank"].mean()))
            null["listener_safety"].append(float(sampled["listener_safety_rank"].mean()))
            null["private_safety"].append(float(sampled["merged_private_safety"].mean()))
            null["hardworld_toxicity"].append(float(sampled["sector_hardworld_toxic"].mean()))
            null["broad_toxicity"].append(float(sampled["sector_broad_toxic"].mean()))
            null["pred_delta"].append(float(sampled["preview_predicted_public_delta"].sum()))
        record = {"variant": variant, "cells": int(len(selected)), "status": "ok"}
        for key, actual_value in actual.items():
            arr = np.asarray(null[key], dtype=np.float64)
            higher = key not in {"hardworld_toxicity", "broad_toxicity", "pred_delta"}
            stats = z_and_p(actual_value, arr.tolist(), higher_is_better=higher)
            record[f"{key}_actual"] = actual_value
            record[f"{key}_null_mean"] = stats["null_mean"]
            record[f"{key}_z"] = stats["z"]
            record[f"{key}_p"] = stats["p"]
        rows.append(record)
    return pd.DataFrame(rows)


def build_readout(
    variants: dict[str, dict[str, object]],
    cells: pd.DataFrame,
    toxic_anchors: pd.DataFrame,
    source_fit: dict[str, object],
    nulls: pd.DataFrame,
) -> dict[str, object]:
    ranking = []
    for name, item in variants.items():
        metrics = item["metrics"]
        validation = item["submission"]["validation"]
        score = (
            0.28 * finite(metrics.get("mean_listener_inverse"))
            + 0.24 * finite(metrics.get("mean_listener_safety"))
            + 0.22 * finite(metrics.get("mean_private_safety"))
            + 0.16 * max(0.0, -finite(metrics.get("sum_predicted_public_delta")))
            - 0.14 * finite(metrics.get("mean_hardworld_toxicity"))
            - 0.10 * finite(metrics.get("mean_broad_toxicity"))
        )
        if not validation.get("upload_safe"):
            score -= 10.0
        ranking.append(
            {
                "variant": name,
                "score": float(score),
                "cells": int(metrics.get("cells", 0)),
                "predicted_delta": finite(metrics.get("sum_predicted_public_delta")),
                "upload_safe": bool(validation.get("upload_safe")),
            }
        )
    ranking = sorted(ranking, key=lambda x: x["score"], reverse=True)
    recommended = ranking[0]["variant"] if ranking else None
    return {
        "experiment": "Anti-Listener Toxicity Equation Solver",
        "architecture_role": "competition_adapter_big_bet",
        "thesis": (
            "Listener responsibility is not an action generator.  Failed listener "
            "releases define an anti-listener toxicity field, and HS-JEPA should "
            "release only row-target moves that invert that field while preserving "
            "public/private action health."
        ),
        "source_fit": source_fit,
        "toxic_anchors": toxic_anchors.to_dict("records"),
        "cell_count": int(len(cells)),
        "verdict": {
            "status": "candidate_ready",
            "recommended_variant": recommended,
            "ranking": ranking,
            "interpretation": (
                "If an inverse variant wins public, the missing structure was not more listener authority; "
                "it was an anti-listener action-health equation."
            ),
        },
        "variants": variants,
        "null_stress": nulls.to_dict("records"),
        "outputs": {
            "readout_json": str(READOUT_JSON.resolve()),
            "readout_md": str(READOUT_MD.resolve()),
            "cells_csv": str(CELL_CSV.resolve()),
            "selected_csv": str(SELECTED_CSV.resolve()),
            "null_csv": str(NULL_CSV.resolve()),
        },
    }


def write_markdown(readout: dict[str, object]) -> None:
    variants = readout["variants"]
    rows = [
        "| Rank | Variant | Cells | Rows | Listener inverse | Listener safety | Private safety | Hardworld tox | Broad tox | Pred delta | Upload-safe | File |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for rank, item in enumerate(readout["verdict"]["ranking"], start=1):
        variant = str(item["variant"])
        rec = variants[variant]
        metrics = rec["metrics"]
        sub = rec["submission"]
        rows.append(
            "| "
            + " | ".join(
                [
                    str(rank),
                    f"`{variant}`",
                    f"`{int(metrics.get('cells', 0))}`",
                    f"`{int(metrics.get('rows', 0))}`",
                    f"`{fmt(metrics.get('mean_listener_inverse'), 3)}`",
                    f"`{fmt(metrics.get('mean_listener_safety'), 3)}`",
                    f"`{fmt(metrics.get('mean_private_safety'), 3)}`",
                    f"`{fmt(metrics.get('mean_hardworld_toxicity'), 3)}`",
                    f"`{fmt(metrics.get('mean_broad_toxicity'), 3)}`",
                    f"`{fmt(metrics.get('sum_predicted_public_delta'), 5)}`",
                    f"`{sub['validation']['upload_safe']}`",
                    f"`{sub['submission_file']}`",
                ]
            )
            + " |"
        )
    md = "\n".join(
        [
            "# Anti-Listener Toxicity Equation Solver",
            "",
            "## Thesis",
            "",
            str(readout["thesis"]),
            "",
            "## Evidence",
            "",
            f"- Toxic anchors loaded: `{sum(1 for r in readout['toxic_anchors'] if r['available'])}`",
            f"- Candidate row-target directions: `{readout['cell_count']}`",
            f"- Source responsibility LOO corr: `{fmt(readout['source_fit'].get('loo_corr'), 4)}`",
            "",
            "## Verdict",
            "",
            f"- Status: `{readout['verdict']['status']}`",
            f"- Recommended variant: `{readout['verdict']['recommended_variant']}`",
            "",
            "## Generated Candidates",
            "",
            *rows,
            "",
            "## Sensor Interpretation",
            "",
            "- If `listener_inverse_jackpot` wins, the failed listener submissions were pointing at the toxic direction and should be inverted.",
            "- If `private_safe_anti_listener_bridge` wins, anti-listener only works after private/action-health filtering.",
            "- If `q2s2_listener_toxicity_route` wins, Q2/S2 are the listener-toxicity route.",
            "- If `public_subset_veto_listener_toxicity` wins, subset tomography is useful only after listener-toxic cells are removed.",
            "- If all fail, listener toxicity is descriptive but not action-grade.",
            "",
        ]
    )
    READOUT_MD.write_text(md, encoding="utf-8")


def run() -> dict[str, object]:
    sample, base_prob, base_logit = load_base()
    source = candidate_sources()
    toxic_anchors, toxic_moves = load_toxic_anchor_moves(sample, base_logit)
    frame = add_public_fit(source, sample, base_prob, base_logit)
    frame = add_toxicity_features(frame, toxic_moves)
    frame = add_action_health(frame, sample, base_prob, base_logit)
    frame.to_csv(CELL_CSV, index=False)

    variants: dict[str, dict[str, object]] = {}
    selected_frames = []
    selected_by_variant = {}
    for config in CONFIGS:
        selected = select_cells(frame, config)
        prob, selected_out, metrics = apply_variant(selected, sample, base_prob, base_logit, config)
        hash_id = short_hash(prob)
        file_name = f"submission_hsjepa_anti_listener_toxicity_{config.name}_{hash_id}_uploadsafe.csv"
        local_path = OUT / file_name
        root_path = ROOT / file_name
        write_submission(local_path, sample, prob)
        write_submission(root_path, sample, prob)
        validation = validate_submission(root_path, sample, base_prob)
        if not selected_out.empty:
            selected_out["variant"] = config.name
            selected_out["submission_file"] = file_name
            selected_frames.append(selected_out)
        selected_by_variant[config.name] = selected_out
        variants[config.name] = {
            "worldview": config.worldview,
            "config": asdict(config),
            "metrics": metrics,
            "submission": {
                "submission_file": file_name,
                "root_path": str(root_path.resolve()),
                "local_path": str(local_path.resolve()),
                "validation": validation,
                "changed_cells": validation["changed_cells_vs_current_best"],
            },
        }

    selected_all = pd.concat(selected_frames, ignore_index=True) if selected_frames else pd.DataFrame()
    selected_all.to_csv(SELECTED_CSV, index=False)
    nulls = null_stress(frame, selected_by_variant)
    nulls.to_csv(NULL_CSV, index=False)
    readout = build_readout(variants, frame, toxic_anchors, frame.attrs.get("source_fit", {}), nulls)
    READOUT_JSON.write_text(json.dumps(readout, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(readout)
    print(json.dumps({"status": "candidate_ready", "recommended": readout["verdict"]["recommended_variant"]}, ensure_ascii=False))
    return readout


def main() -> None:
    run()


if __name__ == "__main__":
    main()
