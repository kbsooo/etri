#!/usr/bin/env python3
"""Invariant-projected negative tangent solver for the sleep adapter.

This is a HS-JEPA paper-facing big bet.

The previous spectral solver found that post-H057 public failures are almost
one-dimensional.  A naive move opposite to that direction is still only a
competition trick unless the released action also remains plausible under the
hidden target route.

This module tests the stronger thesis:

    public-bad negative representation
      + target/subject invariant manifold
      -> feasible row-target correction field

The core architectural claim is independent of this competition.  The adapter
specific part is how we estimate the invariants: here, the target route is
approximated by the train-label covariance and subject-level label priors.
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
from sleep_competition_adapter.spectral_public_tangent_solver import (  # noqa: E402
    candidate_pool,
    finite,
    load_base,
    rank01,
    spectral_public_tangent,
    z_and_p,
)


HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "negative_tangent_invariant_projection_solver"
OUT.mkdir(parents=True, exist_ok=True)

TRAIN_CSV = ROOT / "data" / "ch2026_metrics_train.csv"
READOUT_JSON = OUT / "negative_tangent_invariant_projection_readout.json"
READOUT_MD = OUT / "negative_tangent_invariant_projection_readout.md"
PROJECTED_CELLS_CSV = OUT / "negative_tangent_invariant_projection_cells.csv"
SELECTED_CELLS_CSV = OUT / "negative_tangent_invariant_projection_selected_cells.csv"
NULL_CSV = OUT / "negative_tangent_invariant_projection_null_stress.csv"


@dataclass(frozen=True)
class ProjectionConfig:
    name: str
    worldview: str
    sign_policy: str
    max_cells: int
    max_cells_per_row: int
    min_action_health: float
    min_bad_abs_rank: float
    max_bad_dot: float
    max_incremental_energy_delta: float
    require_energy_descent: bool
    require_subject_nonworse: bool
    step_floor: float
    step_scale: float
    step_cap: float
    target_caps: tuple[tuple[str, int], ...]


CONFIGS = (
    ProjectionConfig(
        name="anti_tangent_invariant_projection",
        worldview=(
            "The public-bad tangent is real, but release must be projected back "
            "onto the train target route and each subject prior."
        ),
        sign_policy="anti_only",
        max_cells=58,
        max_cells_per_row=2,
        min_action_health=0.40,
        min_bad_abs_rank=0.52,
        max_bad_dot=-1e-5,
        max_incremental_energy_delta=0.010,
        require_energy_descent=False,
        require_subject_nonworse=False,
        step_floor=0.028,
        step_scale=0.36,
        step_cap=0.46,
        target_caps=(("Q1", 7), ("Q2", 14), ("Q3", 7), ("S1", 9), ("S2", 13), ("S3", 5), ("S4", 9)),
    ),
    ProjectionConfig(
        name="energy_descent_negative_space",
        worldview=(
            "Only anti-public-bad actions that also reduce target-route energy "
            "should be released."
        ),
        sign_policy="anti_only",
        max_cells=42,
        max_cells_per_row=2,
        min_action_health=0.36,
        min_bad_abs_rank=0.42,
        max_bad_dot=-1e-5,
        max_incremental_energy_delta=-0.001,
        require_energy_descent=True,
        require_subject_nonworse=False,
        step_floor=0.020,
        step_scale=0.30,
        step_cap=0.40,
        target_caps=(("Q1", 6), ("Q2", 10), ("Q3", 6), ("S1", 6), ("S2", 10), ("S3", 4), ("S4", 6)),
    ),
    ProjectionConfig(
        name="subject_prior_safe_projection",
        worldview=(
            "The correct anti-tangent field is the one that is safe in the "
            "personal coordinate system of each subject."
        ),
        sign_policy="anti_only",
        max_cells=46,
        max_cells_per_row=2,
        min_action_health=0.36,
        min_bad_abs_rank=0.40,
        max_bad_dot=-1e-5,
        max_incremental_energy_delta=0.014,
        require_energy_descent=False,
        require_subject_nonworse=True,
        step_floor=0.020,
        step_scale=0.32,
        step_cap=0.42,
        target_caps=(("Q1", 6), ("Q2", 12), ("Q3", 6), ("S1", 7), ("S2", 10), ("S3", 4), ("S4", 7)),
    ),
    ProjectionConfig(
        name="sign_equation_projection",
        worldview=(
            "Some supported cells have the wrong action sign; choose the sign "
            "that satisfies public-bad opposition and route validity jointly."
        ),
        sign_policy="choose_sign",
        max_cells=36,
        max_cells_per_row=1,
        min_action_health=0.44,
        min_bad_abs_rank=0.50,
        max_bad_dot=0.0005,
        max_incremental_energy_delta=0.006,
        require_energy_descent=False,
        require_subject_nonworse=False,
        step_floor=0.018,
        step_scale=0.26,
        step_cap=0.34,
        target_caps=(("Q1", 5), ("Q2", 8), ("Q3", 5), ("S1", 5), ("S2", 8), ("S3", 3), ("S4", 5)),
    ),
)


def fmt(value: Any, digits: int = 4) -> str:
    val = finite(value, float("nan"))
    return f"{val:.{digits}f}" if math.isfinite(val) else "n/a"


def target_caps(config: ProjectionConfig) -> dict[str, int]:
    return {target: count for target, count in config.target_caps}


class TargetInvariantManifold:
    """Train-label route manifold plus subject-personal prior coordinates."""

    def __init__(self, train: pd.DataFrame):
        labels = train[TARGETS].to_numpy(dtype=np.float64)
        self.global_mean = labels.mean(axis=0)
        centered = labels - self.global_mean
        cov = np.cov(centered, rowvar=False)
        diag = np.diag(np.diag(cov))
        shrink = 0.35
        cov = (1.0 - shrink) * cov + shrink * diag + 0.025 * np.eye(len(TARGETS))
        self.inv_cov = np.linalg.pinv(cov)
        self.target_std = np.sqrt(np.clip(self.global_mean * (1.0 - self.global_mean), 0.015, None))
        subject_mean = train.groupby("subject_id")[TARGETS].mean()
        self.subject_mean = {
            str(subject): row.to_numpy(dtype=np.float64)
            for subject, row in subject_mean.iterrows()
        }

    def global_energy(self, vec: np.ndarray) -> float:
        diff = np.asarray(vec, dtype=np.float64) - self.global_mean
        return float(diff @ self.inv_cov @ diff)

    def subject_energy(self, subject: str, vec: np.ndarray) -> float:
        prior = self.subject_mean.get(str(subject), self.global_mean)
        diff = (np.asarray(vec, dtype=np.float64) - prior) / self.target_std
        return float(np.mean(diff * diff))

    def energy_parts(self, subject: str, vec: np.ndarray) -> dict[str, float]:
        global_energy = self.global_energy(vec)
        subject_energy = self.subject_energy(subject, vec)
        return {
            "global_energy": global_energy,
            "subject_energy": subject_energy,
            "combined_energy": global_energy + 0.38 * subject_energy,
        }


def load_manifold() -> TargetInvariantManifold:
    train = pd.read_csv(TRAIN_CSV, parse_dates=KEYS[1:])
    return TargetInvariantManifold(train)


def move_magnitude(row: pd.Series, config: ProjectionConfig) -> float:
    return float(
        np.clip(
            config.step_floor
            + config.step_scale
            * float(row["bad_tangent_abs_rank"])
            * (0.32 + 0.68 * float(row["action_health"])),
            0.0,
            config.step_cap,
        )
    )


def candidate_signs(row: pd.Series, config: ProjectionConfig) -> list[int]:
    if config.sign_policy == "anti_only":
        return [int(row["anti_tangent_direction"])]
    if config.sign_policy == "choose_sign":
        return [-1, 1]
    raise ValueError(config.sign_policy)


def projected_candidate_cells(
    pool: pd.DataFrame,
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    bad_tangent: np.ndarray,
    manifold: TargetInvariantManifold,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    base_logit_matrix = logit(base_prob)
    for _, base_row in pool.iterrows():
        if float(base_row["action_health"]) < 0.30:
            continue
        row_idx = int(base_row["row"])
        target_idx = int(base_row["target_idx"])
        subject = str(sample.iloc[row_idx]["subject_id"])
        old_vec = base_prob[row_idx].copy()
        old_parts = manifold.energy_parts(subject, old_vec)
        flat = int(base_row["flat_idx"])
        for sign in [-1, 1]:
            magnitude = 0.12 + 0.36 * float(base_row["bad_tangent_abs_rank"]) * (
                0.28 + float(base_row["action_health"])
            )
            step = float(sign) * float(np.clip(magnitude, 0.0, 0.54))
            new_vec = old_vec.copy()
            new_vec[target_idx] = clip_prob(
                sigmoid(np.asarray([base_logit_matrix[row_idx, target_idx] + step]))
            )[0]
            new_parts = manifold.energy_parts(subject, new_vec)
            bad_dot = float(step * bad_tangent[flat])
            rows.append(
                {
                    **base_row.to_dict(),
                    "release_sign": int(sign),
                    "raw_projection_step": step,
                    "bad_tangent_dot": bad_dot,
                    "anti_bad_benefit": -bad_dot,
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
    frame = pd.DataFrame(rows)
    if frame.empty:
        return frame
    frame["invariant_good_rank"] = rank01(-frame["combined_energy_delta"].astype(float))
    frame["subject_good_rank"] = rank01(-frame["subject_energy_delta"].astype(float))
    frame["anti_benefit_rank"] = rank01(frame["anti_bad_benefit"].astype(float))
    frame["projection_score"] = (
        0.34 * frame["anti_benefit_rank"]
        + 0.24 * frame["invariant_good_rank"]
        + 0.18 * frame["subject_good_rank"]
        + 0.16 * frame["action_health"].astype(float)
        + 0.08 * rank01(frame["source_family_count"].astype(float))
    )
    return frame.sort_values("projection_score", ascending=False, kind="mergesort").reset_index(drop=True)


def filter_for_config(frame: pd.DataFrame, config: ProjectionConfig) -> pd.DataFrame:
    out = frame[
        frame["action_health"].astype(float).ge(config.min_action_health)
        & frame["bad_tangent_abs_rank"].astype(float).ge(config.min_bad_abs_rank)
        & frame["bad_tangent_dot"].astype(float).le(config.max_bad_dot)
    ].copy()
    if config.sign_policy == "anti_only":
        out = out[out["release_sign"].astype(int).eq(out["anti_tangent_direction"].astype(int))]
    if config.require_energy_descent:
        out = out[out["combined_energy_delta"].astype(float).le(config.max_incremental_energy_delta)]
    if config.require_subject_nonworse:
        out = out[out["subject_energy_delta"].astype(float).le(0.0005)]
    return out


def greedy_project(
    frame: pd.DataFrame,
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    base_logit: np.ndarray,
    manifold: TargetInvariantManifold,
    config: ProjectionConfig,
) -> tuple[pd.DataFrame, np.ndarray]:
    pool = filter_for_config(frame, config)
    if pool.empty:
        return pool, np.zeros(base_prob.size, dtype=np.float64)

    caps = target_caps(config)
    row_counts: dict[int, int] = {}
    target_counts: dict[str, int] = {}
    selected: list[dict[str, object]] = []
    current_prob = base_prob.copy()
    move = np.zeros(base_prob.size, dtype=np.float64)

    for rec in pool.sort_values("projection_score", ascending=False, kind="mergesort").to_dict("records"):
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

        proposed_step = float(rec["release_sign"]) * move_magnitude(pd.Series(rec), config)
        old_vec = current_prob[row_idx].copy()
        old_parts = manifold.energy_parts(str(sample.iloc[row_idx]["subject_id"]), old_vec)
        new_vec = old_vec.copy()
        new_vec[target_idx] = clip_prob(
            sigmoid(np.asarray([base_logit.reshape(base_prob.shape)[row_idx, target_idx] + proposed_step]))
        )[0]
        new_parts = manifold.energy_parts(str(sample.iloc[row_idx]["subject_id"]), new_vec)
        incremental = new_parts["combined_energy"] - old_parts["combined_energy"]
        subject_delta = new_parts["subject_energy"] - old_parts["subject_energy"]
        bad_dot = float(proposed_step * float(rec["bad_tangent_value"]))

        if bad_dot > config.max_bad_dot:
            continue
        if incremental > config.max_incremental_energy_delta:
            continue
        if config.require_energy_descent and incremental > -0.001:
            continue
        if config.require_subject_nonworse and subject_delta > 0.0005:
            continue

        rec["released_logit_step"] = proposed_step
        rec["incremental_combined_energy_delta"] = incremental
        rec["incremental_subject_energy_delta"] = subject_delta
        rec["incremental_global_energy_delta"] = new_parts["global_energy"] - old_parts["global_energy"]
        rec["released_bad_tangent_dot"] = bad_dot
        selected.append(rec)
        current_prob[row_idx] = new_vec
        move[flat] = proposed_step
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
            "mean_action_health": 0.0,
            "mean_projection_score": 0.0,
            "mean_incremental_energy_delta": 0.0,
            "mean_subject_energy_delta": 0.0,
            "bad_tangent_dot": 0.0,
            "bad_tangent_cosine": 0.0,
            "anti_bad_rate": 0.0,
        }
    denom = float(np.linalg.norm(move) * np.linalg.norm(bad_tangent))
    anti_rate = float((np.sign(selected["released_logit_step"]) == selected["anti_tangent_direction"]).mean())
    return {
        "cells": float(len(selected)),
        "rows": float(selected["row"].nunique()),
        "mean_action_health": float(selected["action_health"].mean()),
        "mean_projection_score": float(selected["projection_score"].mean()),
        "mean_incremental_energy_delta": float(selected["incremental_combined_energy_delta"].mean()),
        "mean_subject_energy_delta": float(selected["incremental_subject_energy_delta"].mean()),
        "bad_tangent_dot": float(move @ bad_tangent),
        "bad_tangent_cosine": float((move @ bad_tangent) / denom) if denom > 0.0 else 0.0,
        "anti_bad_rate": anti_rate,
    }


def null_stress(
    candidates: pd.DataFrame,
    selected: pd.DataFrame,
    move: np.ndarray,
    bad_tangent: np.ndarray,
    config: ProjectionConfig,
) -> dict[str, object]:
    actual = selection_metrics(selected, move, bad_tangent)
    if selected.empty:
        return {"actual": actual, "tests": {}, "null_frame": pd.DataFrame()}
    rng = np.random.default_rng(abs(hash(config.name)) % (2**32))
    feasible = filter_for_config(candidates, config)
    if feasible.empty:
        feasible = candidates.copy()
    null_rows: list[dict[str, float]] = []
    target_counts = selected["target"].value_counts().to_dict()
    for _ in range(600):
        draws = []
        for target, count in target_counts.items():
            group = feasible[feasible["target"].eq(target)]
            if group.empty:
                group = feasible
            draws.append(
                group.sample(
                    n=int(count),
                    replace=len(group) < int(count),
                    random_state=int(rng.integers(0, 2**31 - 1)),
                )
            )
        sampled = pd.concat(draws, ignore_index=True).head(len(selected)).copy()
        sampled["released_logit_step"] = selected["released_logit_step"].abs().to_numpy()[: len(sampled)] * np.sign(
            sampled["release_sign"].astype(float).to_numpy()
        )
        sampled["incremental_combined_energy_delta"] = sampled["combined_energy_delta"]
        sampled["incremental_subject_energy_delta"] = sampled["subject_energy_delta"]
        sampled_move = np.zeros_like(move)
        for rec in sampled.to_dict("records"):
            sampled_move[int(rec["flat_idx"])] = finite(rec["released_logit_step"])
        null_rows.append(selection_metrics(sampled, sampled_move, bad_tangent))
    null = pd.DataFrame(null_rows)
    tests = {}
    for metric, higher in [
        ("mean_action_health", True),
        ("mean_projection_score", True),
        ("mean_incremental_energy_delta", False),
        ("mean_subject_energy_delta", False),
        ("bad_tangent_dot", False),
        ("bad_tangent_cosine", False),
        ("anti_bad_rate", True),
    ]:
        tests[metric] = z_and_p(actual[metric], null[metric].tolist(), higher_is_better=higher)
    return {"actual": actual, "tests": tests, "null_frame": null}


def build_submission(
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    base_logit: np.ndarray,
    selected: pd.DataFrame,
    move: np.ndarray,
    config: ProjectionConfig,
) -> dict[str, object]:
    prob = clip_prob(sigmoid(base_logit + move).reshape(base_prob.shape))
    digest = short_hash(prob)
    name = f"submission_hsjepa_negative_tangent_invariant_{config.name}_{digest}_uploadsafe.csv"
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
    scored = []
    for name, item in variants.items():
        metrics = item["metrics"]
        validation = item["submission"]["validation"]
        score = (
            -0.30 * float(metrics["bad_tangent_cosine"])
            -0.24 * float(metrics["mean_incremental_energy_delta"])
            -0.16 * float(metrics["mean_subject_energy_delta"])
            + 0.18 * float(metrics["mean_projection_score"])
            + 0.12 * float(metrics["mean_action_health"])
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
            "Recommended by joint anti-public-bad direction, invariant energy, "
            "subject-prior safety, and upload-safe validation."
            if recommended
            else "No non-empty upload-safe projection survived the constraints."
        ),
        "ranking": [{"variant": name, "score": float(score)} for score, name in scored],
    }


def build_markdown(readout: dict[str, object]) -> str:
    rows = [
        "| Rank | Variant | Cells | Rows | Bad cosine | Energy delta | Subject delta | Upload-safe | File |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    ranked = readout["verdict"]["ranking"]
    for idx, item in enumerate(ranked, start=1):
        variant = item["variant"]
        rec = readout["variants"][variant]
        metrics = rec["metrics"]
        submission = rec["submission"]
        rows.append(
            f"| {idx} | `{variant}` | `{int(metrics['cells'])}` | `{int(metrics['rows'])}` | "
            f"`{fmt(metrics['bad_tangent_cosine'], 4)}` | "
            f"`{fmt(metrics['mean_incremental_energy_delta'], 5)}` | "
            f"`{fmt(metrics['mean_subject_energy_delta'], 5)}` | "
            f"`{submission['validation']['upload_safe']}` | `{submission['submission_file']}` |"
        )

    return "\n".join(
        [
            "# Negative Tangent Invariant Projection Solver",
            "",
            "## Thesis",
            "",
            "A low-rank negative public representation is not enough.  HS-JEPA needs an "
            "action projector that releases only corrections that remain plausible under "
            "the target-route and subject-prior invariant manifold.",
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
            "- If the recommended candidate improves materially, HS-JEPA needs a "
            "negative-representation plus invariant-action projection head.",
            "- If it fails near the previous negative sensors, the public-bad mode is "
            "diagnostic but its inverse is not label-valid.",
            "- If the subject-prior variant wins, personal-coordinate safety is more "
            "important than global target-route safety.",
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
    projected = projected_candidate_cells(pool, sample, base_prob, bad_tangent, manifold)
    projected.to_csv(PROJECTED_CELLS_CSV, index=False)

    variants: dict[str, object] = {}
    selected_frames = []
    null_frames = []
    for config in CONFIGS:
        selected, move = greedy_project(projected, sample, base_prob, base_logit, manifold, config)
        selected["variant"] = config.name
        selected_frames.append(selected)
        submission = build_submission(sample, base_prob, base_logit, selected, move, config)
        metrics = selection_metrics(selected, move, bad_tangent)
        stress = null_stress(projected, selected, move, bad_tangent, config)
        null_frame = stress.pop("null_frame")
        if not null_frame.empty:
            null_frame["variant"] = config.name
            null_frames.append(null_frame)
        variants[config.name] = {
            "config": asdict(config),
            "submission": submission,
            "metrics": metrics,
            "stress": stress,
        }

    if selected_frames:
        pd.concat(selected_frames, ignore_index=True).to_csv(SELECTED_CELLS_CSV, index=False)
    if null_frames:
        pd.concat(null_frames, ignore_index=True).to_csv(NULL_CSV, index=False)

    readout = {
        "experiment": "Negative Tangent Invariant Projection Solver",
        "architecture_role": "competition_adapter_projection_head",
        "core_claim": (
            "HS-JEPA representations become action-grade only after projection "
            "onto invariant human-state routes."
        ),
        "spectral": spectral["spectral"],
        "projected_cells": int(len(projected)),
        "variants": variants,
    }
    readout["verdict"] = build_verdict(variants)
    READOUT_JSON.write_text(json.dumps(readout, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    READOUT_MD.write_text(build_markdown(readout), encoding="utf-8")
    print(json.dumps(readout, indent=2, ensure_ascii=False, allow_nan=False))
    return readout


if __name__ == "__main__":
    run()
