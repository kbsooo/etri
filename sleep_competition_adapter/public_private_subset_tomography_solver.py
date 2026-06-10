#!/usr/bin/env python3
"""Public/private subset tomography solver for HS-JEPA.

This is a high-risk HS-JEPA big-bet module.

The previous LB-conditioned solvers estimate row-target action responsibility
from scalar public LB observations.  This solver asks a sharper question:

    public LB response = public subset inclusion * hidden label direction

The two terms are intentionally separated.  A cell can look public-visible but
still be private-toxic, or it can look label-directional but not public-included.
HS-JEPA should release actions only after deciding which hidden listener world a
row-target belongs to.

The reusable architecture claim is external-listener tomography.  The
competition adapter instantiates the external listener as public LB, the hidden
label direction as a row-target latent, and private-safety as action-health plus
route/subject invariant energy.
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
    logit,
    short_hash,
    sigmoid,
    validate_submission,
    write_submission,
)
from sleep_competition_adapter.lb_conditioned_responsibility_solver import (  # noqa: E402
    build_responsibility_cells,
    load_anchor_matrix,
)
from sleep_competition_adapter.negative_tangent_invariant_projection_solver import (  # noqa: E402
    TargetInvariantManifold,
    load_manifold,
)
from sleep_competition_adapter.spectral_public_tangent_solver import (  # noqa: E402
    candidate_pool,
    load_base,
    spectral_public_tangent,
    z_and_p,
)


HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "public_private_subset_tomography_solver"
OUT.mkdir(parents=True, exist_ok=True)

READOUT_JSON = OUT / "public_private_subset_tomography_readout.json"
READOUT_MD = OUT / "public_private_subset_tomography_readout_ko.md"
CELL_CSV = OUT / "public_private_subset_tomography_cells.csv"
SELECTED_CSV = OUT / "public_private_subset_tomography_selected_cells.csv"
NULL_CSV = OUT / "public_private_subset_tomography_null_stress.csv"


@dataclass(frozen=True)
class TomographyConfig:
    name: str
    worldview: str
    mode: str
    max_cells: int
    max_cells_per_row: int
    min_public_inclusion: float
    min_label_confidence: float
    min_private_safety: float
    max_toxicity: float
    min_gap: float
    max_energy_delta: float
    max_subject_delta: float
    max_predicted_delta: float
    step_floor: float
    step_scale: float
    step_cap: float
    target_caps: tuple[tuple[str, int], ...]


CONFIGS = (
    TomographyConfig(
        name="subset_label_direction_jackpot",
        worldview=(
            "The public listener is sparse: trust high public-inclusion cells and "
            "their inferred label direction, even when private safety is only moderate."
        ),
        mode="public_first",
        max_cells=88,
        max_cells_per_row=3,
        min_public_inclusion=0.66,
        min_label_confidence=0.60,
        min_private_safety=0.24,
        max_toxicity=0.80,
        min_gap=-0.10,
        max_energy_delta=0.040,
        max_subject_delta=0.080,
        max_predicted_delta=-0.0006,
        step_floor=0.022,
        step_scale=0.48,
        step_cap=0.66,
        target_caps=(("Q1", 10), ("Q2", 18), ("Q3", 10), ("S1", 13), ("S2", 18), ("S3", 10), ("S4", 13)),
    ),
    TomographyConfig(
        name="private_safe_subset_equation",
        worldview=(
            "Public inclusion is useful only when the same cell is private-safe "
            "under action-health, route energy, and subject-prior invariants."
        ),
        mode="safety_first",
        max_cells=42,
        max_cells_per_row=2,
        min_public_inclusion=0.48,
        min_label_confidence=0.56,
        min_private_safety=0.58,
        max_toxicity=0.46,
        min_gap=-0.30,
        max_energy_delta=0.010,
        max_subject_delta=0.020,
        max_predicted_delta=-0.0002,
        step_floor=0.016,
        step_scale=0.30,
        step_cap=0.42,
        target_caps=(("Q1", 6), ("Q2", 10), ("Q3", 6), ("S1", 7), ("S2", 10), ("S3", 5), ("S4", 7)),
    ),
    TomographyConfig(
        name="public_private_boundary_probe",
        worldview=(
            "The largest hidden world is the conflict region: public-visible cells "
            "that look private-toxic.  Move them softly to test whether toxicity is "
            "a false veto or a real private boundary."
        ),
        mode="gap_probe",
        max_cells=34,
        max_cells_per_row=2,
        min_public_inclusion=0.62,
        min_label_confidence=0.55,
        min_private_safety=0.10,
        max_toxicity=1.00,
        min_gap=0.18,
        max_energy_delta=0.060,
        max_subject_delta=0.120,
        max_predicted_delta=-0.0001,
        step_floor=0.014,
        step_scale=0.22,
        step_cap=0.34,
        target_caps=(("Q1", 5), ("Q2", 9), ("Q3", 5), ("S1", 5), ("S2", 9), ("S3", 5), ("S4", 5)),
    ),
    TomographyConfig(
        name="qs_dual_subset_route",
        worldview=(
            "Subjective Q targets should follow public-inclusion/label-direction, "
            "while objective S targets require private-safe route conservation."
        ),
        mode="qs_split",
        max_cells=64,
        max_cells_per_row=3,
        min_public_inclusion=0.52,
        min_label_confidence=0.55,
        min_private_safety=0.34,
        max_toxicity=0.68,
        min_gap=-0.18,
        max_energy_delta=0.026,
        max_subject_delta=0.052,
        max_predicted_delta=-0.0003,
        step_floor=0.018,
        step_scale=0.38,
        step_cap=0.54,
        target_caps=(("Q1", 9), ("Q2", 14), ("Q3", 9), ("S1", 9), ("S2", 14), ("S3", 7), ("S4", 9)),
    ),
    TomographyConfig(
        name="orthogonal_private_rescue",
        worldview=(
            "If public subset tomography is overfit, the useful private action "
            "should live in cells with lower public inclusion but strong private "
            "safety and near-orthogonality to known bad public axes."
        ),
        mode="private_rescue",
        max_cells=38,
        max_cells_per_row=2,
        min_public_inclusion=0.20,
        min_label_confidence=0.50,
        min_private_safety=0.64,
        max_toxicity=0.35,
        min_gap=-1.00,
        max_energy_delta=0.004,
        max_subject_delta=0.010,
        max_predicted_delta=0.0003,
        step_floor=0.012,
        step_scale=0.24,
        step_cap=0.34,
        target_caps=(("Q1", 5), ("Q2", 8), ("Q3", 5), ("S1", 6), ("S2", 8), ("S3", 4), ("S4", 6)),
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
    series = pd.Series(values, dtype="float64").replace([np.inf, -np.inf], np.nan).fillna(0.0)
    if series.nunique(dropna=True) <= 1:
        return pd.Series(np.full(len(series), 0.5), index=series.index)
    ranked = series.rank(method="average", pct=True)
    return ranked if higher else 1.0 - ranked


def target_caps(config: TomographyConfig) -> dict[str, int]:
    return {target: cap for target, cap in config.target_caps}


def target_family(target: str) -> str:
    return "Q" if str(target).startswith("Q") else "S"


def build_tomography_cells(
    responsibility: pd.DataFrame,
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    anchor_matrix: np.ndarray,
    bad_tangent: np.ndarray,
) -> pd.DataFrame:
    frame = responsibility.copy()
    base_flat = base_prob.reshape(-1)
    coverage = (np.abs(anchor_matrix) > TOL).mean(axis=0)
    coverage_map = {idx: float(val) for idx, val in enumerate(coverage)}
    bad_abs = np.abs(bad_tangent)
    bad_scale = float(np.percentile(bad_abs, 95)) if len(bad_abs) else 1.0
    if bad_scale < 1e-12:
        bad_scale = 1.0

    rows = []
    for rec in frame.to_dict("records"):
        flat = int(rec["flat_idx"])
        row_idx = int(rec["row"])
        target = str(rec["target"])
        release_sign = int(rec["release_sign"])
        base_p = float(base_flat[flat])
        label_room = (1.0 - base_p) if release_sign > 0 else base_p
        bad_alignment = float(release_sign * bad_tangent[flat] / bad_scale)
        public_gradient = float(rec["public_loss_gradient"])
        feature_std = max(float(rec.get("feature_std", 1.0)), 1e-8)
        rows.append(
            {
                **rec,
                "subject_id": str(sample.iloc[row_idx]["subject_id"]),
                "target_family": target_family(target),
                "anchor_coverage": coverage_map.get(flat, 0.0),
                "base_probability": base_p,
                "inferred_label_value": 1 if release_sign > 0 else 0,
                "label_direction_room": label_room,
                "bad_axis_alignment": bad_alignment,
                "bad_axis_abs": abs(bad_alignment),
                "public_gradient_per_logit": public_gradient / feature_std,
            }
        )
    out = pd.DataFrame(rows)
    if out.empty:
        return out

    out["coverage_rank"] = rank01(out["anchor_coverage"])
    out["label_room_rank"] = rank01(out["label_direction_room"])
    out["gradient_rank"] = rank01(out["public_gradient_abs"])
    out["stability_rank"] = rank01(out["sign_stability"])
    out["private_energy_rank"] = rank01(-out["combined_energy_delta"].astype(float))
    out["subject_energy_rank"] = rank01(-out["subject_energy_delta"].astype(float))
    out["anti_bad_rank"] = rank01(-out["bad_axis_alignment"].astype(float))
    out["toxicity_rank"] = rank01(out["bad_axis_alignment"].astype(float))

    out["public_inclusion_score"] = (
        0.30 * out["gradient_rank"].astype(float)
        + 0.22 * out["stability_rank"].astype(float)
        + 0.17 * out["coverage_rank"].astype(float)
        + 0.13 * out["label_room_rank"].astype(float)
        + 0.10 * out["abs_grad_rank"].astype(float)
        + 0.08 * rank01(out["source_family_count"].astype(float)).astype(float)
    )
    out["label_direction_confidence"] = (
        0.48 * out["sign_stability"].astype(float)
        + 0.22 * out["label_room_rank"].astype(float)
        + 0.18 * out["gradient_rank"].astype(float)
        + 0.12 * out["coverage_rank"].astype(float)
    )
    out["private_safety_score"] = (
        0.26 * out["action_health"].astype(float)
        + 0.18 * out["support_rank"].astype(float)
        + 0.17 * out["private_energy_rank"].astype(float)
        + 0.13 * out["subject_energy_rank"].astype(float)
        + 0.12 * out["anti_bad_rank"].astype(float)
        + 0.08 * out["supported_release"].astype(float)
        + 0.06 * rank01(out["source_family_count"].astype(float)).astype(float)
    )
    out["toxicity_score"] = (
        0.40 * out["toxicity_rank"].astype(float)
        + 0.20 * rank01(out["subject_energy_delta"].astype(float)).astype(float)
        + 0.18 * rank01(out["combined_energy_delta"].astype(float)).astype(float)
        + 0.12 * (1.0 - out["action_health"].astype(float).clip(0, 1))
        + 0.10 * (1.0 - out["supported_release"].astype(float))
    )
    out["public_private_gap"] = out["public_inclusion_score"] - out["private_safety_score"]
    out["tomography_score"] = (
        0.26 * out["public_inclusion_score"]
        + 0.22 * out["label_direction_confidence"]
        + 0.20 * out["private_safety_score"]
        - 0.16 * out["toxicity_score"]
        + 0.10 * out["private_energy_rank"].astype(float)
        + 0.08 * out["coverage_rank"].astype(float)
    )
    return out.sort_values("tomography_score", ascending=False, kind="mergesort").reset_index(drop=True)


def release_priority(frame: pd.DataFrame, config: TomographyConfig) -> pd.Series:
    if config.mode == "public_first":
        return (
            0.42 * frame["public_inclusion_score"]
            + 0.28 * frame["label_direction_confidence"]
            + 0.12 * frame["private_safety_score"]
            - 0.10 * frame["toxicity_score"]
            + 0.08 * frame["coverage_rank"]
        )
    if config.mode == "safety_first":
        return (
            0.38 * frame["private_safety_score"]
            + 0.26 * frame["public_inclusion_score"]
            + 0.18 * frame["label_direction_confidence"]
            - 0.12 * frame["toxicity_score"]
            + 0.06 * frame["private_energy_rank"]
        )
    if config.mode == "gap_probe":
        return (
            0.42 * frame["public_private_gap"]
            + 0.26 * frame["public_inclusion_score"]
            + 0.18 * frame["label_direction_confidence"]
            + 0.14 * frame["toxicity_score"]
        )
    if config.mode == "qs_split":
        q_mask = frame["target_family"].eq("Q").astype(float)
        return (
            q_mask * (0.42 * frame["public_inclusion_score"] + 0.28 * frame["label_direction_confidence"])
            + (1.0 - q_mask) * (0.38 * frame["private_safety_score"] + 0.22 * frame["private_energy_rank"])
            + 0.14 * frame["public_inclusion_score"]
            - 0.10 * frame["toxicity_score"]
        )
    if config.mode == "private_rescue":
        return (
            0.48 * frame["private_safety_score"]
            + 0.20 * (1.0 - frame["bad_axis_abs"].clip(0, 1))
            + 0.16 * frame["private_energy_rank"]
            + 0.10 * frame["label_direction_confidence"]
            - 0.06 * frame["public_inclusion_score"]
        )
    raise ValueError(config.mode)


def filter_config(frame: pd.DataFrame, config: TomographyConfig) -> pd.DataFrame:
    out = frame[
        frame["public_inclusion_score"].astype(float).ge(config.min_public_inclusion)
        & frame["label_direction_confidence"].astype(float).ge(config.min_label_confidence)
        & frame["private_safety_score"].astype(float).ge(config.min_private_safety)
        & frame["toxicity_score"].astype(float).le(config.max_toxicity)
        & frame["public_private_gap"].astype(float).ge(config.min_gap)
    ].copy()
    if config.mode == "private_rescue":
        out = out[out["public_inclusion_score"].astype(float).le(0.58)].copy()
    return out


def release_step(row: pd.Series, config: TomographyConfig) -> float:
    if config.mode == "gap_probe":
        strength = float(row["public_private_gap"])
    elif config.mode == "private_rescue":
        strength = float(row["private_safety_score"]) * (1.0 - min(float(row["bad_axis_abs"]), 1.0))
    elif config.mode == "safety_first":
        strength = 0.55 * float(row["private_safety_score"]) + 0.45 * float(row["public_inclusion_score"])
    elif config.mode == "qs_split":
        strength = (
            float(row["public_inclusion_score"])
            if str(row["target_family"]) == "Q"
            else float(row["private_safety_score"])
        )
    else:
        strength = float(row["public_inclusion_score"])
    magnitude = config.step_floor + config.step_scale * strength * float(row["label_direction_confidence"])
    return float(row["release_sign"]) * float(np.clip(magnitude, 0.0, config.step_cap))


def greedy_release(
    frame: pd.DataFrame,
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    base_logit: np.ndarray,
    manifold: TargetInvariantManifold,
    config: TomographyConfig,
) -> tuple[pd.DataFrame, np.ndarray]:
    feasible = filter_config(frame, config)
    if feasible.empty:
        return feasible, np.zeros(base_logit.size, dtype=np.float64)
    feasible = feasible.copy()
    feasible["_priority"] = release_priority(feasible, config)

    caps = target_caps(config)
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
        predicted_delta = float(rec["public_loss_gradient"]) * (step / max(float(rec["feature_std"]), 1e-8))
        if predicted_delta > config.max_predicted_delta:
            continue

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
        rec["predicted_public_delta"] = predicted_delta
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
            "mean_public_inclusion": 0.0,
            "mean_label_confidence": 0.0,
            "mean_private_safety": 0.0,
            "mean_toxicity": 0.0,
            "mean_gap": 0.0,
            "sum_predicted_public_delta": 0.0,
            "mean_energy_delta": 0.0,
            "mean_subject_delta": 0.0,
            "bad_tangent_cosine": 0.0,
            "q_rate": 0.0,
        }
    denom = float(np.linalg.norm(move) * np.linalg.norm(bad_tangent))
    cosine = float((move @ bad_tangent) / denom) if denom > 0 else 0.0
    return {
        "cells": float(len(selected)),
        "rows": float(selected["row"].nunique()),
        "mean_public_inclusion": float(selected["public_inclusion_score"].mean()),
        "mean_label_confidence": float(selected["label_direction_confidence"].mean()),
        "mean_private_safety": float(selected["private_safety_score"].mean()),
        "mean_toxicity": float(selected["toxicity_score"].mean()),
        "mean_gap": float(selected["public_private_gap"].mean()),
        "sum_predicted_public_delta": float(selected["predicted_public_delta"].sum()),
        "mean_energy_delta": float(selected["incremental_energy_delta"].mean()),
        "mean_subject_delta": float(selected["incremental_subject_delta"].mean()),
        "bad_tangent_cosine": cosine,
        "q_rate": float(selected["target_family"].eq("Q").mean()),
    }


def null_stress(
    frame: pd.DataFrame,
    selected: pd.DataFrame,
    move: np.ndarray,
    bad_tangent: np.ndarray,
    config: TomographyConfig,
) -> dict[str, object]:
    actual = selection_metrics(selected, move, bad_tangent)
    if selected.empty:
        return {"actual": actual, "tests": {}, "null_frame": pd.DataFrame()}
    rng = np.random.default_rng(abs(hash(config.name)) % (2**32))
    feasible = filter_config(frame, config)
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
        sampled["predicted_public_delta"] = sampled["public_loss_gradient"].astype(float) * (
            sampled["released_logit_step"].astype(float) / sampled["feature_std"].astype(float).clip(lower=1e-8)
        )
        sampled["incremental_energy_delta"] = sampled["combined_energy_delta"].astype(float)
        sampled["incremental_subject_delta"] = sampled["subject_energy_delta"].astype(float)
        sampled_move = np.zeros_like(move)
        for rec in sampled.to_dict("records"):
            sampled_move[int(rec["flat_idx"])] = finite(rec["released_logit_step"])
        null_rows.append(selection_metrics(sampled, sampled_move, bad_tangent))
    null = pd.DataFrame(null_rows)
    tests = {}
    for metric, higher in [
        ("mean_public_inclusion", True),
        ("mean_label_confidence", True),
        ("mean_private_safety", True),
        ("mean_toxicity", False),
        ("mean_gap", True),
        ("sum_predicted_public_delta", False),
        ("mean_energy_delta", False),
        ("mean_subject_delta", False),
        ("bad_tangent_cosine", False),
        ("q_rate", True),
    ]:
        tests[metric] = z_and_p(actual[metric], null[metric].tolist(), higher_is_better=higher)
    return {"actual": actual, "tests": tests, "null_frame": null}


def build_submission(
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    base_logit: np.ndarray,
    selected: pd.DataFrame,
    move: np.ndarray,
    config: TomographyConfig,
) -> dict[str, object]:
    prob = clip_prob(sigmoid(base_logit + move).reshape(base_prob.shape))
    digest = short_hash(prob)
    name = f"submission_hsjepa_subset_tomography_{config.name}_{digest}_uploadsafe.csv"
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
            -0.30 * float(metrics["sum_predicted_public_delta"])
            + 0.20 * float(metrics["mean_public_inclusion"])
            + 0.18 * float(metrics["mean_label_confidence"])
            + 0.16 * float(metrics["mean_private_safety"])
            - 0.12 * float(metrics["mean_toxicity"])
            - 0.06 * abs(float(metrics["bad_tangent_cosine"]))
        )
        if name == "public_private_boundary_probe":
            score += 0.16 * float(metrics["mean_gap"])
        if not validation["upload_safe"] or metrics["cells"] <= 0:
            score = -1e9
        scored.append((score, name))
    scored.sort(reverse=True)
    recommended = scored[0][1] if scored else None
    return {
        "status": "candidate_ready" if recommended else "no_candidate",
        "recommended_variant": recommended,
        "reason": (
            "Recommended by public-inclusion, label-direction confidence, private-safety, "
            "predicted public delta, and upload-safe validation."
            if recommended
            else "No upload-safe subset tomography action survived constraints."
        ),
        "ranking": [{"variant": name, "score": float(score)} for score, name in scored],
    }


def build_markdown(readout: dict[str, object]) -> str:
    rows = [
        "| Rank | Variant | Cells | Rows | Public incl. | Label conf. | Private safe | Toxicity | Pred delta | Bad cosine | Upload-safe | File |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for idx, item in enumerate(readout["verdict"]["ranking"], start=1):
        variant = item["variant"]
        rec = readout["variants"][variant]
        metrics = rec["metrics"]
        submission = rec["submission"]
        rows.append(
            f"| {idx} | `{variant}` | `{int(metrics['cells'])}` | `{int(metrics['rows'])}` | "
            f"`{fmt(metrics['mean_public_inclusion'], 3)}` | "
            f"`{fmt(metrics['mean_label_confidence'], 3)}` | "
            f"`{fmt(metrics['mean_private_safety'], 3)}` | "
            f"`{fmt(metrics['mean_toxicity'], 3)}` | "
            f"`{fmt(metrics['sum_predicted_public_delta'], 5)}` | "
            f"`{fmt(metrics['bad_tangent_cosine'], 4)}` | "
            f"`{submission['validation']['upload_safe']}` | `{submission['submission_file']}` |"
        )
    return "\n".join(
        [
            "# Public/Private Subset Tomography Solver",
            "",
            "## Thesis",
            "",
            "HS-JEPA should not treat scalar public feedback as direct action truth.  "
            "It should decompose the feedback into public subset inclusion, hidden "
            "label direction, private-safety, and toxicity fields.",
            "",
            "## Evidence",
            "",
            f"- Anchor count: `{readout['anchor_count']}`",
            f"- Tomography cells: `{readout['cell_count']}`",
            f"- Source responsibility LOO corr: `{fmt(readout['source_fit']['loo_corr'], 4)}`",
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
            "- If `subset_label_direction_jackpot` wins, the missing state is mainly public subset inclusion plus label direction.",
            "- If `private_safe_subset_equation` wins, private/action-health constraints are the true bottleneck.",
            "- If `public_private_boundary_probe` wins, previous toxicity vetoes were over-conservative.",
            "- If `qs_dual_subset_route` wins, Q and S require different public/private listener routes.",
            "- If all fail, public subset tomography is descriptive but not yet action-grade.",
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
    responsibility, source_fit = build_responsibility_cells(
        pool=pool,
        sample=sample,
        base_prob=base_prob,
        base_logit=base_logit,
        bad_tangent=bad_tangent,
        manifold=manifold,
        anchor_matrix=anchors["moves"],
        loss_delta=anchors["loss_delta"],
    )
    cells = build_tomography_cells(responsibility, sample, base_prob, anchors["moves"], bad_tangent)
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
        "experiment": "Public/Private Subset Tomography Solver",
        "architecture_role": "competition_adapter_external_listener_tomography_head",
        "core_claim": (
            "HS-JEPA can decompose scalar external feedback into public subset "
            "inclusion, hidden label direction, private-safety, and toxicity before "
            "releasing a row-target action."
        ),
        "anchor_count": int(anchors["moves"].shape[0]),
        "cell_count": int(len(cells)),
        "spectral": spectral["spectral"],
        "source_fit": source_fit["fit"],
        "variants": variants,
        "verdict": build_verdict(variants),
        "outputs": {
            "readout_json": str(READOUT_JSON.resolve()),
            "readout_md": str(READOUT_MD.resolve()),
            "cells": str(CELL_CSV.resolve()),
            "selected_cells": str(SELECTED_CSV.resolve()),
            "null_stress": str(NULL_CSV.resolve()),
        },
    }
    READOUT_JSON.write_text(json.dumps(readout, ensure_ascii=False, indent=2), encoding="utf-8")
    READOUT_MD.write_text(build_markdown(readout), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": readout["verdict"]["status"],
                "recommended": readout["verdict"]["recommended_variant"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return readout


if __name__ == "__main__":
    run()
