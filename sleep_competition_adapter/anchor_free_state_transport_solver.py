#!/usr/bin/env python3
"""Anchor-free state-transport solver for the sleep competition adapter.

This is intentionally not a current-best micro-refiner.

Previous HS-JEPA submissions found a strong row-state frontier, then moved in
small neighborhoods around it.  That is useful for score, but weak as a paper
claim because it turns the architecture into anchor-following.

This solver treats the known submissions as noisy listeners of a hidden
row-target field:

    pre-HS feature frontier
    public-equation jump
    Q2 phase route
    row-state vector frontier
    frontier active-silence
    negative/toxic listener branches

It then synthesizes a fresh probability tensor from those listeners.  The
current best is only one listener, not the base action.  Public LB for these
outputs should be read as a sensor for the thesis:

    Can HS-JEPA transport hidden state across listeners without anchoring
    every action to the previous best?
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
    candidate_pool,
    finite,
    load_submission_move,
    rank01,
    spectral_public_tangent,
    z_and_p,
)


HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "anchor_free_state_transport_solver"
OUT.mkdir(parents=True, exist_ok=True)

CURRENT_BEST_FILE = "submission_hsjepa_frontier_silence_positive_path_overshoot_sensor_1e013277_uploadsafe.csv"
ROW_STATE_FILE = "submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv"
PRE_HS_FILE = "submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv"

READOUT_JSON = OUT / "anchor_free_state_transport_readout.json"
READOUT_MD = OUT / "anchor_free_state_transport_readout_ko.md"
CELL_CSV = OUT / "anchor_free_state_transport_cells.csv"
SELECTED_CSV = OUT / "anchor_free_state_transport_selected_cells.csv"
NULL_CSV = OUT / "anchor_free_state_transport_null_stress.csv"
GENERATED_PREFIX = "submission_hsjepa_anchorfree_state_transport_"


@dataclass(frozen=True)
class ListenerWorld:
    name: str
    file: str
    weight: float
    polarity: str
    note: str


@dataclass(frozen=True)
class TransportConfig:
    name: str
    worldview: str
    mode: str
    current_mix: float
    positive_gain: float
    toxic_repel: float
    shock: float
    min_cell_score: float
    max_cells: int
    max_cells_per_row: int
    max_route_energy_delta: float
    max_subject_energy_delta: float
    target_caps: tuple[tuple[str, int], ...]


POSITIVE_WORLDS = (
    ListenerWorld(
        name="pre_hs_feature_frontier",
        file=PRE_HS_FILE,
        weight=0.20,
        polarity="context",
        note="pre-HS feature/model plateau before the large public-equation jump",
    ),
    ListenerWorld(
        name="public_equation_jump",
        file="submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv",
        weight=0.70,
        polarity="positive",
        note="first large hidden public-state materialization",
    ),
    ListenerWorld(
        name="q2_phase_route",
        file="submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv",
        weight=0.90,
        polarity="positive",
        note="Q2 support row phase marker",
    ),
    ListenerWorld(
        name="row_state_vector_frontier",
        file=ROW_STATE_FILE,
        weight=1.00,
        polarity="positive",
        note="complete hidden row-state vector frontier",
    ),
    ListenerWorld(
        name="frontier_active_silence",
        file=CURRENT_BEST_FILE,
        weight=1.10,
        polarity="positive",
        note="new best; release/abstain trajectory listener",
    ),
)

NEGATIVE_WORLDS = (
    ListenerWorld(
        name="dual_head_toxicity_stress",
        file="submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv",
        weight=0.75,
        polarity="negative",
        note="broad dual-head action field punished by public",
    ),
    ListenerWorld(
        name="cross_listener_transport_stress",
        file="submission_hsjepa_cross_listener_transport_listener_confirmed_shadow_660faef3_uploadsafe.csv",
        weight=0.70,
        polarity="negative",
        note="listener-confirmed shadow release punished by public",
    ),
    ListenerWorld(
        name="objective_s1s4_toxic_route",
        file="submission_h010_objective_s1s4_v2_uploadsafe.csv",
        weight=0.55,
        polarity="negative",
        note="objective S1/S4 route action public-bad anchor",
    ),
    ListenerWorld(
        name="maskfam_jepa_s2_toxic_route",
        file="submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv",
        weight=0.45,
        polarity="negative",
        note="direct masked-family JEPA S2 translator public miss",
    ),
    ListenerWorld(
        name="null_common_residual_toxic_route",
        file="submission_e323_5508f966_uploadsafe.csv",
        weight=0.50,
        polarity="negative",
        note="null-common residual branch public miss",
    ),
)

CONFIGS = (
    TransportConfig(
        name="full_field_public_private_reset",
        worldview=(
            "The hidden row-target field is not a local perturbation of the best file. "
            "Reconstruct a fresh field from positive listener worlds, repel it from "
            "negative listener worlds, and release the whole tensor."
        ),
        mode="dense",
        current_mix=0.06,
        positive_gain=1.04,
        toxic_repel=0.24,
        shock=1.00,
        min_cell_score=0.00,
        max_cells=1750,
        max_cells_per_row=7,
        max_route_energy_delta=99.0,
        max_subject_energy_delta=99.0,
        target_caps=(("Q1", 250), ("Q2", 250), ("Q3", 250), ("S1", 250), ("S2", 250), ("S3", 250), ("S4", 250)),
    ),
    TransportConfig(
        name="nonlocal_transport_release",
        worldview=(
            "Do not release the whole reconstructed field.  Release the cells where "
            "positive listener consensus, negative-listener repulsion, route validity, "
            "and source support all agree."
        ),
        mode="selected",
        current_mix=0.16,
        positive_gain=1.18,
        toxic_repel=0.32,
        shock=1.05,
        min_cell_score=0.58,
        max_cells=620,
        max_cells_per_row=4,
        max_route_energy_delta=0.16,
        max_subject_energy_delta=0.34,
        target_caps=(("Q1", 90), ("Q2", 120), ("Q3", 90), ("S1", 80), ("S2", 120), ("S3", 60), ("S4", 80)),
    ),
    TransportConfig(
        name="listener_shock_reset",
        worldview=(
            "If the current frontier is over-anchored, a stronger listener-transport "
            "shock should expose whether positive/negative public worlds define a "
            "usable state equation beyond local correction."
        ),
        mode="selected",
        current_mix=0.00,
        positive_gain=1.38,
        toxic_repel=0.44,
        shock=1.22,
        min_cell_score=0.50,
        max_cells=980,
        max_cells_per_row=6,
        max_route_energy_delta=0.30,
        max_subject_energy_delta=0.55,
        target_caps=(("Q1", 140), ("Q2", 180), ("Q3", 140), ("S1", 120), ("S2", 180), ("S3", 100), ("S4", 120)),
    ),
    TransportConfig(
        name="cohort_ready_private_safe_reset",
        worldview=(
            "A private-safe reset should avoid dense objective-tail shock, favor "
            "Q2/Q3/S2 and route-valid cells, and leave room for cohort-relative "
            "human-state views as future context."
        ),
        mode="selected",
        current_mix=0.24,
        positive_gain=1.08,
        toxic_repel=0.38,
        shock=0.82,
        min_cell_score=0.64,
        max_cells=360,
        max_cells_per_row=3,
        max_route_energy_delta=0.08,
        max_subject_energy_delta=0.22,
        target_caps=(("Q1", 38), ("Q2", 88), ("Q3", 56), ("S1", 30), ("S2", 88), ("S3", 24), ("S4", 36)),
    ),
)


def fmt(value: Any, digits: int = 4) -> str:
    val = finite(value, float("nan"))
    return f"{val:.{digits}f}" if math.isfinite(val) else "n/a"


def locate(file_name: str) -> Path | None:
    path = ROOT / file_name
    if path.exists():
        return path
    hits = list(ROOT.glob(f"**/{Path(file_name).name}"))
    hits = [hit for hit in hits if "outputs/anchor_free_state_transport_solver" not in hit.as_posix()]
    return hits[0] if hits else None


def load_submission(file_name: str, sample: pd.DataFrame | None = None) -> pd.DataFrame:
    path = locate(file_name)
    if path is None:
        raise FileNotFoundError(file_name)
    frame = pd.read_csv(path, parse_dates=KEYS[1:]).sort_values(KEYS).reset_index(drop=True)
    if sample is not None and (len(frame) != len(sample) or not frame[KEYS].equals(sample[KEYS])):
        raise ValueError(f"key mismatch for {file_name}")
    return frame


def load_world_logits(sample: pd.DataFrame, worlds: tuple[ListenerWorld, ...]) -> tuple[list[ListenerWorld], np.ndarray]:
    used: list[ListenerWorld] = []
    logits: list[np.ndarray] = []
    for world in worlds:
        try:
            frame = load_submission(world.file, sample)
        except Exception:
            continue
        prob = frame[TARGETS].to_numpy(dtype=np.float64)
        if np.isfinite(prob).all():
            used.append(world)
            logits.append(logit(prob).reshape(-1))
    if not logits:
        raise RuntimeError("no listener worlds loaded")
    return used, np.vstack(logits)


def weighted_mean(logits: np.ndarray, worlds: list[ListenerWorld]) -> np.ndarray:
    weights = np.asarray([world.weight for world in worlds], dtype=np.float64)
    weights = weights / weights.sum()
    return np.average(logits, axis=0, weights=weights)


def summarize_worlds(worlds: list[ListenerWorld]) -> list[dict[str, object]]:
    return [asdict(world) for world in worlds]


def build_cell_frame(
    sample: pd.DataFrame,
    current_prob: np.ndarray,
    current_logit: np.ndarray,
    row_state_logit: np.ndarray,
    pre_logit: np.ndarray,
    positive_logits: np.ndarray,
    negative_logits: np.ndarray,
    desired_logit: np.ndarray,
    bad_tangent: np.ndarray,
    pool: pd.DataFrame,
    manifold: TargetInvariantManifold,
) -> pd.DataFrame:
    pos_std = positive_logits.std(axis=0)
    pos_center = positive_logits.mean(axis=0)
    neg_center = negative_logits.mean(axis=0)

    rows = []
    support = pool.sort_values("action_health", ascending=False).drop_duplicates("flat_idx").set_index("flat_idx")
    for row_idx, rec in sample.iterrows():
        subject = str(rec["subject_id"])
        current_vec = current_prob[row_idx].copy()
        base_energy = manifold.energy_parts(subject, current_vec)
        for target_idx, target in enumerate(TARGETS):
            flat_idx = row_idx * len(TARGETS) + target_idx
            proposal_vec = current_vec.copy()
            proposal_vec[target_idx] = float(sigmoid(desired_logit[flat_idx]))
            proposal_energy = manifold.energy_parts(subject, proposal_vec)
            transport_delta = float(desired_logit[flat_idx] - current_logit[flat_idx])
            pre_delta = float(desired_logit[flat_idx] - pre_logit[flat_idx])
            neg_distance = float(abs(desired_logit[flat_idx] - neg_center[flat_idx]))
            pos_disagreement = float(pos_std[flat_idx])
            frontier_delta = float(current_logit[flat_idx] - row_state_logit[flat_idx])
            if flat_idx in support.index:
                src = support.loc[flat_idx]
                source_health = float(src.get("action_health", 0.5))
                source_families = str(src.get("source_families", ""))
                source_count = int(src.get("source_family_count", 0))
                source_direction = int(src.get("direction", np.sign(transport_delta) or 1))
            else:
                source_health = 0.36
                source_families = ""
                source_count = 0
                source_direction = int(np.sign(transport_delta) or 1)
            rows.append(
                {
                    "flat_idx": int(flat_idx),
                    "row": int(row_idx),
                    "subject_id": subject,
                    "target": target,
                    "target_idx": int(target_idx),
                    "cell_key": f"{row_idx}:{target}",
                    "desired_logit": float(desired_logit[flat_idx]),
                    "current_logit": float(current_logit[flat_idx]),
                    "row_state_logit": float(row_state_logit[flat_idx]),
                    "pre_logit": float(pre_logit[flat_idx]),
                    "transport_delta": transport_delta,
                    "pre_delta": pre_delta,
                    "abs_transport_delta": abs(transport_delta),
                    "positive_mean_logit": float(pos_center[flat_idx]),
                    "negative_mean_logit": float(neg_center[flat_idx]),
                    "negative_distance": neg_distance,
                    "positive_disagreement": pos_disagreement,
                    "frontier_delta": frontier_delta,
                    "frontier_sign_agrees": bool(np.sign(frontier_delta) == np.sign(transport_delta) and abs(frontier_delta) > TOL),
                    "bad_tangent_value": float(bad_tangent[flat_idx]),
                    "bad_tangent_alignment": float(bad_tangent[flat_idx] * np.sign(transport_delta or 1.0)),
                    "source_health": source_health,
                    "source_family_count": source_count,
                    "source_families": source_families,
                    "source_direction": source_direction,
                    "route_energy_delta": float(proposal_energy["combined_energy"] - base_energy["combined_energy"]),
                    "subject_energy_delta": float(proposal_energy["subject_energy"] - base_energy["subject_energy"]),
                }
            )
    frame = pd.DataFrame(rows)
    frame["transport_rank"] = rank01(frame["abs_transport_delta"])
    frame["negative_distance_rank"] = rank01(frame["negative_distance"])
    frame["positive_consensus_rank"] = 1.0 - rank01(frame["positive_disagreement"])
    frame["source_health_rank"] = rank01(frame["source_health"])
    frame["route_safe_rank"] = 1.0 - rank01(frame["route_energy_delta"], higher=True)
    frame["subject_safe_rank"] = 1.0 - rank01(frame["subject_energy_delta"], higher=True)
    frame["anti_bad_rank"] = 1.0 - rank01(frame["bad_tangent_alignment"], higher=True)
    frame["cell_score"] = (
        0.20 * frame["transport_rank"]
        + 0.18 * frame["negative_distance_rank"]
        + 0.16 * frame["positive_consensus_rank"]
        + 0.15 * frame["source_health_rank"]
        + 0.12 * frame["route_safe_rank"]
        + 0.10 * frame["subject_safe_rank"]
        + 0.09 * frame["anti_bad_rank"]
    )
    frame.loc[frame["frontier_sign_agrees"], "cell_score"] += 0.035
    frame.loc[frame["target"].isin(["Q2", "Q3", "S2"]), "cell_score"] += 0.018
    frame.loc[frame["target"].isin(["S1", "S3", "S4"]), "cell_score"] -= 0.012
    return frame.sort_values("cell_score", ascending=False).reset_index(drop=True)


def synthesize_desired_field(
    current_logit: np.ndarray,
    pre_logit: np.ndarray,
    pos_mean: np.ndarray,
    neg_mean: np.ndarray,
    config: TransportConfig,
) -> np.ndarray:
    positive_transport = pre_logit + config.positive_gain * (pos_mean - pre_logit)
    negative_repel = config.toxic_repel * (pos_mean - neg_mean)
    synth = positive_transport + negative_repel
    moved = current_logit + config.shock * (synth - current_logit)
    desired = config.current_mix * current_logit + (1.0 - config.current_mix) * moved
    return np.clip(desired, -8.5, 8.5)


def target_caps(config: TransportConfig) -> dict[str, int]:
    return {target: cap for target, cap in config.target_caps}


def select_cells(cells: pd.DataFrame, config: TransportConfig) -> pd.DataFrame:
    frame = cells.copy()
    frame = frame[frame["cell_score"].ge(config.min_cell_score)]
    frame = frame[frame["route_energy_delta"].le(config.max_route_energy_delta)]
    frame = frame[frame["subject_energy_delta"].le(config.max_subject_energy_delta)]
    frame = frame[frame["abs_transport_delta"].gt(0.003)]
    target_limit = target_caps(config)
    selected: list[pd.Series] = []
    row_counts: dict[int, int] = {}
    target_counts: dict[str, int] = {}
    for _, rec in frame.sort_values("cell_score", ascending=False, kind="mergesort").iterrows():
        row = int(rec["row"])
        target = str(rec["target"])
        if row_counts.get(row, 0) >= config.max_cells_per_row:
            continue
        if target_counts.get(target, 0) >= target_limit.get(target, config.max_cells):
            continue
        selected.append(rec)
        row_counts[row] = row_counts.get(row, 0) + 1
        target_counts[target] = target_counts.get(target, 0) + 1
        if len(selected) >= config.max_cells:
            break
    if not selected:
        return pd.DataFrame(columns=list(frame.columns))
    return pd.DataFrame(selected).reset_index(drop=True)


def decode_variant(
    sample: pd.DataFrame,
    current_prob: np.ndarray,
    current_logit: np.ndarray,
    desired_logit: np.ndarray,
    cells: pd.DataFrame,
    config: TransportConfig,
) -> dict[str, object]:
    if config.mode == "dense":
        new_logit = desired_logit.copy()
        selected = cells.copy()
        selected["selected"] = True
    elif config.mode == "selected":
        new_logit = current_logit.copy()
        selected = select_cells(cells, config)
        for rec in selected.to_dict("records"):
            flat_idx = int(rec["flat_idx"])
            new_logit[flat_idx] = finite(rec["desired_logit"])
        selected["selected"] = True
    else:
        raise ValueError(config.mode)

    prob = clip_prob(sigmoid(new_logit).reshape(current_prob.shape))
    digest = short_hash(prob)
    name = f"{GENERATED_PREFIX}{config.name}_{digest}_uploadsafe.csv"
    local_path = OUT / name
    root_path = ROOT / name
    write_submission(local_path, sample, prob)
    write_submission(root_path, sample, prob)
    validation = validate_submission(root_path, sample, current_prob)
    moved = logit(prob).reshape(-1) - current_logit
    selected.to_csv(OUT / f"{config.name}_selected_cells.csv", index=False)
    return {
        "name": config.name,
        "worldview": config.worldview,
        "file": name,
        "local_path": str(local_path.relative_to(ROOT)),
        "root_path": str(root_path.relative_to(ROOT)),
        "hash": digest,
        "validation": validation,
        "changed_cells_vs_current_best": int((np.abs(prob - current_prob) > TOL).sum()),
        "changed_rows_vs_current_best": int((np.abs(prob - current_prob).max(axis=1) > TOL).sum()),
        "mean_abs_logit_move_vs_current": float(np.mean(np.abs(moved))),
        "max_abs_logit_move_vs_current": float(np.max(np.abs(moved))),
        "selected_cells": int(len(selected)),
        "selected_rows": int(selected["row"].nunique()) if not selected.empty else 0,
        "target_counts": selected["target"].value_counts().to_dict() if not selected.empty else {},
        "mean_cell_score": float(selected["cell_score"].mean()) if not selected.empty else None,
        "mean_route_energy_delta": float(selected["route_energy_delta"].mean()) if not selected.empty else None,
        "mean_subject_energy_delta": float(selected["subject_energy_delta"].mean()) if not selected.empty else None,
        "mean_negative_distance_rank": float(selected["negative_distance_rank"].mean()) if not selected.empty else None,
    }


def null_stress(cells: pd.DataFrame, selected: pd.DataFrame, config: TransportConfig, seed: int = 20260612) -> dict[str, object]:
    if selected.empty:
        return {}
    rng = np.random.default_rng(seed)
    pools = cells[cells["target"].isin(selected["target"].unique())].copy()
    actual = {
        "cell_score": float(selected["cell_score"].mean()),
        "route_energy_delta": float(selected["route_energy_delta"].mean()),
        "negative_distance_rank": float(selected["negative_distance_rank"].mean()),
        "anti_bad_rank": float(selected["anti_bad_rank"].mean()),
    }
    null_rows = []
    n = len(selected)
    for idx in range(300):
        sample_idx = rng.choice(pools.index.to_numpy(), size=n, replace=False)
        fake = pools.loc[sample_idx]
        null_rows.append(
            {
                "trial": idx,
                "cell_score": float(fake["cell_score"].mean()),
                "route_energy_delta": float(fake["route_energy_delta"].mean()),
                "negative_distance_rank": float(fake["negative_distance_rank"].mean()),
                "anti_bad_rank": float(fake["anti_bad_rank"].mean()),
            }
        )
    null = pd.DataFrame(null_rows)
    return {
        "cell_score": z_and_p(actual["cell_score"], null["cell_score"].tolist(), higher_is_better=True),
        "route_energy_delta": z_and_p(actual["route_energy_delta"], null["route_energy_delta"].tolist(), higher_is_better=False),
        "negative_distance_rank": z_and_p(actual["negative_distance_rank"], null["negative_distance_rank"].tolist(), higher_is_better=True),
        "anti_bad_rank": z_and_p(actual["anti_bad_rank"], null["anti_bad_rank"].tolist(), higher_is_better=True),
    }


def write_readout(readout: dict[str, object], variants: list[dict[str, object]]) -> None:
    READOUT_JSON.write_text(json.dumps(readout, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# Anchor-Free State Transport Solver",
        "",
        "## 핵심 주장",
        "",
        "현재 best 주변을 조금 더 미는 실험이 아니라, 여러 listener world를 합성해 fresh row-target field를 만든다.",
        "",
        "```text",
        "positive listeners + negative/toxic listeners -> anchor-free state transport field",
        "```",
        "",
        "## Loaded Worlds",
        "",
        "### Positive",
    ]
    for world in readout["positive_worlds"]:
        lines.append(f"- `{world['name']}`: `{world['file']}`")
    lines += ["", "### Negative"]
    for world in readout["negative_worlds"]:
        lines.append(f"- `{world['name']}`: `{world['file']}`")
    lines += ["", "## Candidates", ""]
    for variant in variants:
        lines += [
            f"### {variant['name']}",
            "",
            variant["worldview"],
            "",
            f"- file: `{variant['file']}`",
            f"- changed cells vs current best: `{variant['changed_cells_vs_current_best']}`",
            f"- changed rows vs current best: `{variant['changed_rows_vs_current_best']}`",
            f"- selected cells: `{variant['selected_cells']}`",
            f"- mean abs logit move vs current: `{fmt(variant['mean_abs_logit_move_vs_current'], 6)}`",
            f"- upload safe: `{variant['validation']['upload_safe']}`",
            f"- target counts: `{variant['target_counts']}`",
            "",
        ]
    lines += [
        "## 해석",
        "",
        "이 후보들은 의도적으로 보수적 anchor continuation이 아니다. public LB가 악화되어도 정보가 있다.",
        "",
        "- 좋아지면: HS-JEPA는 current best를 anchor로 삼지 않고도 listener world를 transport해 action field를 만들 수 있다.",
        "- 나빠지면: public-equation/row-state/silence world는 개별적으로는 유효하지만, fresh tensor 합성에는 아직 private/toxicity/invariant가 부족하다.",
    ]
    READOUT_MD.write_text("\n".join(lines), encoding="utf-8")


def run() -> dict[str, object]:
    # Remove stale generated outputs so this solver never trains on itself through glob lookups.
    for path in list(ROOT.glob(f"{GENERATED_PREFIX}*_uploadsafe.csv")) + list(OUT.glob(f"{GENERATED_PREFIX}*_uploadsafe.csv")):
        path.unlink(missing_ok=True)

    current = load_submission(CURRENT_BEST_FILE)
    sample = current[KEYS].copy()
    current_prob = current[TARGETS].to_numpy(dtype=np.float64)
    current_logit = logit(current_prob).reshape(-1)

    row_state = load_submission(ROW_STATE_FILE, sample)
    row_state_logit = logit(row_state[TARGETS].to_numpy(dtype=np.float64)).reshape(-1)

    pre = load_submission(PRE_HS_FILE, sample)
    pre_logit = logit(pre[TARGETS].to_numpy(dtype=np.float64)).reshape(-1)

    positive_worlds, positive_logits = load_world_logits(sample, POSITIVE_WORLDS)
    negative_worlds, negative_logits = load_world_logits(sample, NEGATIVE_WORLDS)
    positive_mean = weighted_mean(positive_logits, positive_worlds)
    negative_mean = weighted_mean(negative_logits, negative_worlds)

    # Existing tangent/cell pool is used as diagnostic support, not as the base output.
    tangent = spectral_public_tangent(sample, row_state_logit)
    bad_tangent = tangent["bad_tangent"]
    pool = candidate_pool(bad_tangent)
    manifold = load_manifold()

    base_cells = None
    variants = []
    nulls = []
    for config in CONFIGS:
        desired = synthesize_desired_field(current_logit, pre_logit, positive_mean, negative_mean, config)
        cells = build_cell_frame(
            sample,
            current_prob,
            current_logit,
            row_state_logit,
            pre_logit,
            positive_logits,
            negative_logits,
            desired,
            bad_tangent,
            pool,
            manifold,
        )
        cells["config"] = config.name
        if base_cells is None:
            base_cells = cells
        result = decode_variant(sample, current_prob, current_logit, desired, cells, config)
        selected_path = OUT / f"{config.name}_selected_cells.csv"
        selected = pd.read_csv(selected_path) if selected_path.exists() else pd.DataFrame()
        result["null_stress"] = null_stress(cells, selected, config)
        variants.append(result)
        for metric, payload in result["null_stress"].items():
            nulls.append({"config": config.name, "metric": metric, **payload})

    if base_cells is not None:
        base_cells.to_csv(CELL_CSV, index=False)
    pd.concat(
        [pd.read_csv(OUT / f"{config.name}_selected_cells.csv").assign(config=config.name) for config in CONFIGS],
        ignore_index=True,
    ).to_csv(SELECTED_CSV, index=False)
    pd.DataFrame(nulls).to_csv(NULL_CSV, index=False)

    readout = {
        "thesis": "Anchor-free HS-JEPA state transport treats current best as one listener, not as the base anchor.",
        "current_best_file": CURRENT_BEST_FILE,
        "current_best_public_lb": 0.5677269444,
        "positive_worlds": summarize_worlds(positive_worlds),
        "negative_worlds": summarize_worlds(negative_worlds),
        "spectral": tangent["spectral"],
        "variants": variants,
    }
    write_readout(readout, variants)
    return readout


if __name__ == "__main__":
    result = run()
    print(json.dumps({"variants": result["variants"]}, ensure_ascii=False, indent=2))
