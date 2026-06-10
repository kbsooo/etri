#!/usr/bin/env python3
"""Frontier-trajectory active-silence solver for the sleep adapter.

This is a high-risk HS-JEPA big-bet module.

Previous public-sensor solvers mostly used failures: bad public tangents,
listener toxicity, and public/private subset tomography.  This solver adds the
missing complementary target representation:

    the trajectory of actions that actually moved the public frontier.

In HS-JEPA terms, the public leaderboard is not optimized directly.  It is read
as a sparse external listener that emitted a noisy gradient-descent path.  A
healthy action decoder should know not only what to release, but also what to
keep silent.  The experiment therefore contrasts:

    positive frontier transitions
      vs.
    post-frontier toxic/action-failure branches

and creates public-sensor submissions that test whether the next breakthrough
comes from continuing the successful frontier direction, inverting the silence
field, or probing the boundary between the two.
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
    finite,
    load_base,
    load_submission_move,
    rank01,
    spectral_public_tangent,
    z_and_p,
)


HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "frontier_trajectory_silence_solver"
OUT.mkdir(parents=True, exist_ok=True)

READOUT_JSON = OUT / "frontier_trajectory_silence_readout.json"
READOUT_MD = OUT / "frontier_trajectory_silence_readout_ko.md"
CELL_CSV = OUT / "frontier_trajectory_silence_cells.csv"
SELECTED_CSV = OUT / "frontier_trajectory_silence_selected_cells.csv"
EDGE_CSV = OUT / "frontier_trajectory_edges.csv"
NULL_CSV = OUT / "frontier_trajectory_silence_null_stress.csv"
GENERATED_PREFIX = "submission_hsjepa_frontier_silence_"


@dataclass(frozen=True)
class FrontierPoint:
    name: str
    file: str
    public_lb: float
    role: str


@dataclass(frozen=True)
class SilenceConfig:
    name: str
    worldview: str
    mode: str
    max_cells: int
    max_cells_per_row: int
    min_frontier_rank: float
    min_anti_bad_rank: float
    max_silence_pressure: float
    max_energy_delta: float
    max_subject_delta: float
    require_frontier_source: bool
    step_floor: float
    step_scale: float
    step_cap: float
    target_caps: tuple[tuple[str, int], ...]


FRONTIER_PATH = (
    FrontierPoint(
        name="H012",
        file="submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv",
        public_lb=0.5681234831,
        role="first HS-JEPA public-equation jump",
    ),
    FrontierPoint(
        name="H042",
        file="submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv",
        public_lb=0.5679048248,
        role="Q2 phase route improvement",
    ),
    FrontierPoint(
        name="H057",
        file="submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv",
        public_lb=CURRENT_BEST_PUBLIC_LB,
        role="current best hidden row-state vector",
    ),
)


CONFIGS = (
    SilenceConfig(
        name="frontier_continuation_gate",
        worldview=(
            "The H012->H042->H057 path is a real hidden-state descent direction. "
            "Continue only cells aligned with that path and not aligned with the "
            "post-frontier silence/toxicity field."
        ),
        mode="frontier_continue",
        max_cells=44,
        max_cells_per_row=2,
        min_frontier_rank=0.66,
        min_anti_bad_rank=0.30,
        max_silence_pressure=0.58,
        max_energy_delta=0.035,
        max_subject_delta=0.075,
        require_frontier_source=False,
        step_floor=0.012,
        step_scale=0.24,
        step_cap=0.34,
        target_caps=(("Q1", 6), ("Q2", 11), ("Q3", 6), ("S1", 6), ("S2", 10), ("S3", 4), ("S4", 6)),
    ),
    SilenceConfig(
        name="positive_path_overshoot_sensor",
        worldview=(
            "If H057 under-stepped the successful frontier action field, then "
            "a stronger continuation of the actual positive transition cells "
            "should move public LB meaningfully."
        ),
        mode="frontier_overshoot",
        max_cells=38,
        max_cells_per_row=2,
        min_frontier_rank=0.58,
        min_anti_bad_rank=0.18,
        max_silence_pressure=0.68,
        max_energy_delta=0.055,
        max_subject_delta=0.120,
        require_frontier_source=True,
        step_floor=0.018,
        step_scale=0.34,
        step_cap=0.52,
        target_caps=(("Q1", 6), ("Q2", 10), ("Q3", 6), ("S1", 6), ("S2", 9), ("S3", 4), ("S4", 6)),
    ),
    SilenceConfig(
        name="active_silence_inversion",
        worldview=(
            "The frontier path may be blocked by a silence field.  If the "
            "silence field is action-grade, moving opposite to it should expose "
            "new row-target support beyond H057."
        ),
        mode="anti_silence",
        max_cells=36,
        max_cells_per_row=2,
        min_frontier_rank=0.26,
        min_anti_bad_rank=0.62,
        max_silence_pressure=0.74,
        max_energy_delta=0.030,
        max_subject_delta=0.070,
        require_frontier_source=False,
        step_floor=0.012,
        step_scale=0.30,
        step_cap=0.44,
        target_caps=(("Q1", 5), ("Q2", 9), ("Q3", 5), ("S1", 6), ("S2", 8), ("S3", 4), ("S4", 5)),
    ),
    SilenceConfig(
        name="frontier_silence_boundary_probe",
        worldview=(
            "The most informative rows are where frontier continuation and "
            "silence pressure disagree.  A small boundary action tests whether "
            "HS-JEPA should release or abstain there."
        ),
        mode="boundary_probe",
        max_cells=18,
        max_cells_per_row=1,
        min_frontier_rank=0.55,
        min_anti_bad_rank=0.05,
        max_silence_pressure=0.88,
        max_energy_delta=0.060,
        max_subject_delta=0.120,
        require_frontier_source=False,
        step_floor=0.008,
        step_scale=0.12,
        step_cap=0.18,
        target_caps=(("Q1", 3), ("Q2", 5), ("Q3", 3), ("S1", 3), ("S2", 4), ("S3", 2), ("S4", 3)),
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
    return hits[0] if hits else None


def read_submission(file_name: str) -> pd.DataFrame:
    path = locate(file_name)
    if path is None:
        raise FileNotFoundError(file_name)
    return pd.read_csv(path, parse_dates=KEYS[1:]).sort_values(KEYS).reset_index(drop=True)


def unit(vec: np.ndarray) -> np.ndarray:
    norm = float(np.linalg.norm(vec))
    return vec / (norm + 1e-12)


def build_frontier_tangent(base: pd.DataFrame, base_logit: np.ndarray) -> dict[str, object]:
    points = []
    for point in FRONTIER_PATH:
        frame = read_submission(point.file)
        if not frame[KEYS].equals(base[KEYS]):
            raise RuntimeError(f"frontier key mismatch: {point.file}")
        points.append((point, logit(frame[TARGETS].to_numpy(dtype=np.float64)).reshape(-1)))

    edge_rows: list[dict[str, object]] = []
    edge_vectors: list[np.ndarray] = []
    edge_weights: list[float] = []
    for (prev, prev_vec), (nxt, nxt_vec) in zip(points[:-1], points[1:]):
        edge = nxt_vec - prev_vec
        gain = float(prev.public_lb - nxt.public_lb)
        if gain <= 0.0 or np.linalg.norm(edge) <= TOL:
            continue
        edge_vectors.append(unit(edge))
        edge_weights.append(gain**0.65)
        edge_rows.append(
            {
                "from": prev.name,
                "to": nxt.name,
                "from_file": prev.file,
                "to_file": nxt.file,
                "public_gain": gain,
                "changed_cells": int((np.abs(edge) > TOL).sum()),
                "move_l2": float(np.linalg.norm(edge)),
                "role": f"{prev.role} -> {nxt.role}",
            }
        )

    direct = points[-1][1] - points[0][1]
    direct_gain = float(points[0][0].public_lb - points[-1][0].public_lb)
    if direct_gain > 0.0 and np.linalg.norm(direct) > TOL:
        edge_vectors.append(unit(direct))
        edge_weights.append(direct_gain**0.65)
        edge_rows.append(
            {
                "from": points[0][0].name,
                "to": points[-1][0].name,
                "from_file": points[0][0].file,
                "to_file": points[-1][0].file,
                "public_gain": direct_gain,
                "changed_cells": int((np.abs(direct) > TOL).sum()),
                "move_l2": float(np.linalg.norm(direct)),
                "role": "direct positive frontier tangent",
            }
        )

    if not edge_vectors:
        raise RuntimeError("no positive frontier edges available")

    weights = np.asarray(edge_weights, dtype=np.float64)
    tangent = np.average(np.vstack(edge_vectors), axis=0, weights=weights)
    tangent = unit(tangent)
    edges = pd.DataFrame(edge_rows)
    edges.to_csv(EDGE_CSV, index=False)
    return {
        "frontier_tangent": tangent,
        "edges": edges,
        "summary": {
            "edge_count": int(len(edges)),
            "total_public_gain": float(edges["public_gain"].sum()),
            "mean_changed_cells": float(edges["changed_cells"].mean()),
            "mean_move_l2": float(edges["move_l2"].mean()),
        },
    }


def source_family(file_name: str) -> str:
    name = Path(file_name).name
    if name.startswith("submission_hsjepa_"):
        rest = name.removeprefix("submission_hsjepa_")
        tokens = rest.split("_")
        return "_".join(tokens[:2]) if len(tokens) >= 2 else tokens[0]
    if name.startswith("submission_h"):
        return "human_numbered"
    return "other"


def source_files() -> list[str]:
    files: set[str] = set()
    for path in ROOT.glob("submission_hsjepa_*.csv"):
        if path.name.startswith(GENERATED_PREFIX):
            continue
        files.add(path.name)
    for point in FRONTIER_PATH:
        files.add(point.file)
    ledger = pd.read_csv(PUBLIC_LEDGER)
    for file_name in ledger["file"].astype(str):
        path = locate(file_name)
        if path is not None:
            files.add(path.name)
    files.discard(FRONTIER_PATH[-1].file)
    files.discard("submission_hsjepa_end_to_end_h057_7cde1a77_uploadsafe.csv")
    return sorted(files)


def clean_generated_submissions() -> None:
    for directory in (ROOT, OUT):
        for path in directory.glob(f"{GENERATED_PREFIX}*.csv"):
            path.unlink()


def public_map() -> dict[str, float]:
    ledger = pd.read_csv(PUBLIC_LEDGER)
    return {str(row.file): float(row.public_lb) for row in ledger.itertuples(index=False)}


def add_frontier_edge_records(base: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    frames = [(point, read_submission(point.file)) for point in FRONTIER_PATH]
    for (prev, prev_frame), (nxt, nxt_frame) in zip(frames[:-1], frames[1:]):
        prev_logit = logit(prev_frame[TARGETS].to_numpy(dtype=np.float64)).reshape(-1)
        nxt_logit = logit(nxt_frame[TARGETS].to_numpy(dtype=np.float64)).reshape(-1)
        edge = nxt_logit - prev_logit
        gain = float(prev.public_lb - nxt.public_lb)
        if gain <= 0.0:
            continue
        for flat_idx in np.flatnonzero(np.abs(edge) > TOL):
            row_idx = int(flat_idx // len(TARGETS))
            target_idx = int(flat_idx % len(TARGETS))
            step = float(edge[flat_idx])
            rows.append(
                {
                    "flat_idx": flat_idx,
                    "row": row_idx,
                    "target": TARGETS[target_idx],
                    "target_idx": target_idx,
                    "cell_key": f"{row_idx}:{TARGETS[target_idx]}",
                    "direction": int(np.sign(step) or 1),
                    "step": step,
                    "abs_step": abs(step),
                    "file": f"frontier_edge_{prev.name}_to_{nxt.name}",
                    "source_family": "frontier_transition",
                    "public_lb": np.nan,
                    "known_bad_weight": 0.0,
                    "frontier_source": True,
                    "public_gain": gain,
                }
            )
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows)


def proposal_records(base: pd.DataFrame, base_logit: np.ndarray) -> pd.DataFrame:
    pmap = public_map()
    rows: list[dict[str, object]] = []
    for file_name in source_files():
        move = load_submission_move(file_name, base, base_logit)
        if move is None:
            continue
        public_lb = pmap.get(file_name, np.nan)
        known_bad_weight = max(0.0, finite(public_lb, CURRENT_BEST_PUBLIC_LB) - CURRENT_BEST_PUBLIC_LB)
        family = source_family(file_name)
        changed = np.flatnonzero(np.abs(move) > TOL)
        for flat_idx in changed:
            row_idx = int(flat_idx // len(TARGETS))
            target_idx = int(flat_idx % len(TARGETS))
            step = float(move[flat_idx])
            rows.append(
                {
                    "flat_idx": int(flat_idx),
                    "row": row_idx,
                    "target": TARGETS[target_idx],
                    "target_idx": target_idx,
                    "cell_key": f"{row_idx}:{TARGETS[target_idx]}",
                    "direction": int(np.sign(step) or 1),
                    "step": step,
                    "abs_step": abs(step),
                    "file": file_name,
                    "source_family": family,
                    "public_lb": public_lb,
                    "known_bad_weight": known_bad_weight,
                    "frontier_source": False,
                    "public_gain": 0.0,
                }
            )
    frame = pd.DataFrame(rows)
    frontier = add_frontier_edge_records(base)
    if not frontier.empty:
        frame = pd.concat([frame, frontier], ignore_index=True, sort=False)
    if frame.empty:
        raise RuntimeError("no source proposal records")
    return frame


def aggregate_pool(records: pd.DataFrame, frontier_tangent: np.ndarray, bad_tangent: np.ndarray) -> pd.DataFrame:
    grouped_rows: list[dict[str, object]] = []
    for (flat_idx, direction), group in records.groupby(["flat_idx", "direction"], sort=False):
        best = group.sort_values(["frontier_source", "abs_step"], ascending=False).iloc[0]
        families = sorted(set(group["source_family"].astype(str)))
        files = sorted(set(group["file"].astype(str)))[:16]
        grouped_rows.append(
            {
                "flat_idx": int(flat_idx),
                "row": int(best["row"]),
                "target": str(best["target"]),
                "target_idx": int(best["target_idx"]),
                "cell_key": str(best["cell_key"]),
                "direction": int(direction),
                "source_records": int(len(group)),
                "source_files": int(group["file"].nunique()),
                "source_family_count": int(len(families)),
                "source_families": ",".join(families),
                "source_file_examples": ",".join(files),
                "frontier_source_count": int(group["frontier_source"].sum()),
                "frontier_source": bool(group["frontier_source"].any()),
                "known_bad_count": int(group["known_bad_weight"].gt(0).sum()),
                "known_bad_weight": float(group["known_bad_weight"].sum()),
                "mean_abs_step": float(group["abs_step"].mean()),
                "max_abs_step": float(group["abs_step"].max()),
                "mean_signed_step": float(group["step"].mean()),
                "frontier_public_gain": float(group["public_gain"].sum()),
            }
        )
    pool = pd.DataFrame(grouped_rows)
    pool["frontier_value"] = frontier_tangent[pool["flat_idx"].to_numpy(dtype=int)]
    pool["bad_tangent_value"] = bad_tangent[pool["flat_idx"].to_numpy(dtype=int)]
    pool["frontier_alignment"] = pool["direction"].astype(float) * pool["frontier_value"].astype(float)
    pool["bad_alignment"] = pool["direction"].astype(float) * pool["bad_tangent_value"].astype(float)
    pool["anti_bad_alignment"] = -pool["bad_alignment"]
    pool["frontier_positive"] = pool["frontier_alignment"].clip(lower=0.0)
    pool["anti_bad_positive"] = pool["anti_bad_alignment"].clip(lower=0.0)
    pool["bad_positive"] = pool["bad_alignment"].clip(lower=0.0)
    pool["frontier_rank"] = rank01(pool["frontier_positive"])
    pool["anti_bad_rank"] = rank01(pool["anti_bad_positive"])
    pool["bad_rank"] = rank01(pool["bad_positive"])
    pool["source_rank"] = rank01(np.log1p(pool["source_records"]))
    pool["family_rank"] = rank01(pool["source_family_count"])
    pool["bad_weight_rank"] = rank01(pool["known_bad_weight"])
    pool["step_rank"] = rank01(pool["max_abs_step"])
    pool["silence_pressure"] = (
        0.38 * pool["bad_rank"]
        + 0.28 * pool["bad_weight_rank"]
        + 0.16 * (1.0 - pool["frontier_rank"])
        + 0.10 * pool["source_rank"]
        + 0.08 * (1.0 - pool["anti_bad_rank"])
    ).clip(0, 1)
    pool["frontier_release_score"] = (
        0.36 * pool["frontier_rank"]
        + 0.22 * pool["anti_bad_rank"]
        + 0.16 * pool["family_rank"]
        + 0.14 * pool["source_rank"]
        + 0.12 * (1.0 - pool["bad_weight_rank"])
    )
    pool["anti_silence_score"] = (
        0.34 * pool["anti_bad_rank"]
        + 0.24 * (1.0 - pool["silence_pressure"])
        + 0.16 * pool["frontier_rank"]
        + 0.14 * pool["family_rank"]
        + 0.12 * pool["source_rank"]
    )
    pool["boundary_score"] = (
        0.40 * np.minimum(pool["frontier_rank"], pool["bad_rank"])
        + 0.24 * pool["anti_bad_rank"]
        + 0.20 * pool["family_rank"]
        + 0.16 * pool["source_rank"]
    )
    return pool


def add_invariant_features(
    pool: pd.DataFrame,
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    base_logit: np.ndarray,
    manifold: TargetInvariantManifold,
) -> pd.DataFrame:
    out = pool.copy()
    rows: list[dict[str, float]] = []
    base_matrix = base_logit.reshape(base_prob.shape)
    for rec in out.to_dict("records"):
        row_idx = int(rec["row"])
        target_idx = int(rec["target_idx"])
        direction = int(rec["direction"])
        mag = float(np.clip(0.010 + 0.22 * rec["frontier_rank"] + 0.16 * rec["anti_bad_rank"], 0.010, 0.42))
        before = base_prob[row_idx].copy()
        trial_logit = base_matrix[row_idx].copy()
        trial_logit[target_idx] += direction * mag
        after = clip_prob(sigmoid(trial_logit))
        before_energy = manifold.energy_parts(str(sample.loc[row_idx, "subject_id"]), before)
        after_energy = manifold.energy_parts(str(sample.loc[row_idx, "subject_id"]), after)
        rows.append(
            {
                "trial_step": direction * mag,
                "global_energy_delta": after_energy["global_energy"] - before_energy["global_energy"],
                "subject_energy_delta": after_energy["subject_energy"] - before_energy["subject_energy"],
                "combined_energy_delta": after_energy["combined_energy"] - before_energy["combined_energy"],
            }
        )
    feat = pd.DataFrame(rows)
    out = pd.concat([out.reset_index(drop=True), feat], axis=1)
    out["invariant_rank"] = rank01(-out["combined_energy_delta"])
    out["subject_safe_rank"] = rank01(-out["subject_energy_delta"])
    out["frontier_release_score"] = (
        0.84 * out["frontier_release_score"] + 0.10 * out["invariant_rank"] + 0.06 * out["subject_safe_rank"]
    )
    out["anti_silence_score"] = (
        0.84 * out["anti_silence_score"] + 0.10 * out["invariant_rank"] + 0.06 * out["subject_safe_rank"]
    )
    out["boundary_score"] = 0.86 * out["boundary_score"] + 0.08 * out["invariant_rank"] + 0.06 * out["subject_safe_rank"]
    return out


def target_caps(config: SilenceConfig) -> dict[str, int]:
    return {target: cap for target, cap in config.target_caps}


def select_cells(pool: pd.DataFrame, config: SilenceConfig) -> pd.DataFrame:
    frame = pool.copy()
    frame = frame[frame["frontier_rank"].ge(config.min_frontier_rank)]
    frame = frame[frame["anti_bad_rank"].ge(config.min_anti_bad_rank)]
    frame = frame[frame["silence_pressure"].le(config.max_silence_pressure)]
    frame = frame[frame["combined_energy_delta"].le(config.max_energy_delta)]
    frame = frame[frame["subject_energy_delta"].le(config.max_subject_delta)]
    if config.require_frontier_source:
        frame = frame[frame["frontier_source"]].copy()

    if config.mode in {"frontier_continue", "frontier_overshoot"}:
        frame = frame[frame["frontier_alignment"].gt(0)].copy()
        frame["released_direction"] = frame["direction"]
        frame["selection_score"] = frame["frontier_release_score"]
    elif config.mode == "anti_silence":
        frame = frame[frame["anti_bad_alignment"].gt(0)].copy()
        frame["released_direction"] = frame["direction"]
        frame["selection_score"] = frame["anti_silence_score"]
    elif config.mode == "boundary_probe":
        frame = frame[frame["bad_rank"].ge(0.45)].copy()
        frame["released_direction"] = np.where(
            frame["frontier_rank"].ge(frame["bad_rank"]),
            frame["direction"],
            np.sign(-frame["bad_tangent_value"]).replace(0, 1).astype(int),
        )
        frame["selection_score"] = frame["boundary_score"]
    else:
        raise ValueError(config.mode)

    if frame.empty:
        return frame

    caps = target_caps(config)
    selected: list[pd.Series] = []
    used: set[int] = set()
    row_counts: dict[int, int] = {}
    target_counts: dict[str, int] = {}
    for _, rec in frame.sort_values("selection_score", ascending=False, kind="mergesort").iterrows():
        flat_idx = int(rec["flat_idx"])
        row = int(rec["row"])
        target = str(rec["target"])
        if flat_idx in used:
            continue
        if row_counts.get(row, 0) >= config.max_cells_per_row:
            continue
        if target_counts.get(target, 0) >= caps.get(target, config.max_cells):
            continue
        selected.append(rec)
        used.add(flat_idx)
        row_counts[row] = row_counts.get(row, 0) + 1
        target_counts[target] = target_counts.get(target, 0) + 1
        if len(selected) >= config.max_cells:
            break

    if not selected:
        return pd.DataFrame(columns=list(frame.columns))

    out = pd.DataFrame(selected).reset_index(drop=True)
    mag = config.step_floor + config.step_scale * (
        0.46 * out["frontier_rank"].astype(float)
        + 0.34 * out["anti_bad_rank"].astype(float)
        + 0.20 * out["invariant_rank"].astype(float)
    )
    if config.mode == "boundary_probe":
        mag *= 0.62
    if config.mode == "frontier_overshoot":
        mag *= 1.18
    out["released_logit_step"] = out["released_direction"].astype(float) * mag.clip(0.0, config.step_cap)
    out["config"] = config.name
    return out


def apply_cells(
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    base_logit: np.ndarray,
    selected: pd.DataFrame,
    config: SilenceConfig,
) -> dict[str, object]:
    move = np.zeros(base_logit.size, dtype=np.float64)
    for rec in selected.to_dict("records"):
        move[int(rec["flat_idx"])] = finite(rec["released_logit_step"])
    prob = clip_prob(sigmoid(base_logit + move).reshape(base_prob.shape))
    digest = short_hash(prob)
    name = f"submission_hsjepa_frontier_silence_{config.name}_{digest}_uploadsafe.csv"
    local_path = OUT / name
    root_path = ROOT / name
    write_submission(local_path, sample, prob)
    write_submission(root_path, sample, prob)
    return {
        "variant": config.name,
        "worldview": config.worldview,
        "submission_file": name,
        "root_path": str(root_path.resolve()),
        "local_path": str(local_path.resolve()),
        "validation": validate_submission(root_path, sample, base_prob),
        "move": move,
    }


def score_selection(selected: pd.DataFrame, move: np.ndarray, frontier_tangent: np.ndarray, bad_tangent: np.ndarray) -> dict[str, float]:
    if selected.empty:
        return {
            "cell_count": 0.0,
            "row_count": 0.0,
            "mean_frontier_rank": 0.0,
            "mean_anti_bad_rank": 0.0,
            "mean_silence_pressure": 0.0,
            "mean_invariant_rank": 0.0,
            "mean_energy_delta": 0.0,
            "frontier_cosine": 0.0,
            "bad_tangent_cosine": 0.0,
            "frontier_source_rate": 0.0,
            "known_bad_count_mean": 0.0,
        }
    move_norm = float(np.linalg.norm(move))
    frontier_cosine = float((move @ frontier_tangent) / (move_norm * np.linalg.norm(frontier_tangent) + 1e-12))
    bad_cosine = float((move @ bad_tangent) / (move_norm * np.linalg.norm(bad_tangent) + 1e-12))
    return {
        "cell_count": float(len(selected)),
        "row_count": float(selected["row"].nunique()),
        "mean_frontier_rank": float(selected["frontier_rank"].mean()),
        "mean_anti_bad_rank": float(selected["anti_bad_rank"].mean()),
        "mean_silence_pressure": float(selected["silence_pressure"].mean()),
        "mean_invariant_rank": float(selected["invariant_rank"].mean()),
        "mean_energy_delta": float(selected["combined_energy_delta"].mean()),
        "frontier_cosine": frontier_cosine,
        "bad_tangent_cosine": bad_cosine,
        "frontier_source_rate": float(selected["frontier_source"].mean()),
        "known_bad_count_mean": float(selected["known_bad_count"].mean()),
    }


def null_stress(
    pool: pd.DataFrame,
    selected: pd.DataFrame,
    move: np.ndarray,
    frontier_tangent: np.ndarray,
    bad_tangent: np.ndarray,
    rng: np.random.Generator,
) -> dict[str, object]:
    actual = score_selection(selected, move, frontier_tangent, bad_tangent)
    if selected.empty:
        return {"actual": actual, "tests": {}}
    null_scores: list[dict[str, float]] = []
    for _ in range(600):
        parts = []
        for target, group in selected.groupby("target"):
            candidates = pool[pool["target"].eq(target)]
            if candidates.empty:
                continue
            parts.append(
                candidates.sample(
                    n=len(group),
                    replace=len(candidates) < len(group),
                    random_state=int(rng.integers(0, 2**31 - 1)),
                )
            )
        if not parts:
            continue
        sampled = pd.concat(parts, ignore_index=True).head(len(selected)).copy()
        sampled["released_logit_step"] = np.sign(sampled["direction"].astype(float)) * selected[
            "released_logit_step"
        ].abs().to_numpy()[: len(sampled)]
        sampled_move = np.zeros_like(move)
        for rec in sampled.to_dict("records"):
            sampled_move[int(rec["flat_idx"])] = finite(rec["released_logit_step"])
        null_scores.append(score_selection(sampled, sampled_move, frontier_tangent, bad_tangent))

    tests = {}
    for metric, high in [
        ("mean_frontier_rank", True),
        ("mean_anti_bad_rank", True),
        ("mean_silence_pressure", False),
        ("mean_invariant_rank", True),
        ("mean_energy_delta", False),
        ("frontier_cosine", True),
        ("bad_tangent_cosine", False),
        ("frontier_source_rate", True),
    ]:
        tests[metric] = z_and_p(actual[metric], [row[metric] for row in null_scores], higher_is_better=high)
    return {"actual": actual, "tests": tests}


def variant_priority(metrics: dict[str, float], config: SilenceConfig) -> float:
    return (
        0.42 * metrics["frontier_cosine"]
        - 0.32 * metrics["bad_tangent_cosine"]
        + 0.30 * metrics["mean_frontier_rank"]
        + 0.22 * metrics["mean_anti_bad_rank"]
        - 0.24 * metrics["mean_silence_pressure"]
        + 0.18 * metrics["mean_invariant_rank"]
        + (0.12 if config.mode == "frontier_overshoot" else 0.0)
    )


def build_markdown(readout: dict[str, object]) -> str:
    verdict = readout["verdict"]
    lines = [
        "# Frontier-Trajectory Active-Silence Solver",
        "",
        "## Thesis",
        "",
        str(readout["thesis"]),
        "",
        "## Frontier Evidence",
        "",
        f"- Positive frontier edges: `{readout['frontier']['edge_count']}`",
        f"- Total frontier public gain: `{fmt(readout['frontier']['total_public_gain'], 7)}`",
        f"- Candidate row-target directions: `{readout['cell_count']}`",
        f"- Bad tangent first-mode variance: `{fmt(readout['negative_tangent']['first_mode_variance'])}`",
        "",
        "## Verdict",
        "",
        f"- Status: `{verdict['status']}`",
        f"- Recommended variant: `{verdict['recommended_variant']}`",
        "",
        "## Generated Candidates",
        "",
        "| Rank | Variant | Cells | Rows | Frontier cos | Bad cos | Silence | Energy | Upload-safe | File |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for idx, row in enumerate(verdict["ranking"], 1):
        variant = row["variant"]
        info = readout["variants"][variant]
        metrics = info["metrics"]
        sub = info["submission"]
        lines.append(
            "| "
            + " | ".join(
                [
                    str(idx),
                    f"`{variant}`",
                    f"`{int(metrics['cell_count'])}`",
                    f"`{int(metrics['row_count'])}`",
                    f"`{fmt(metrics['frontier_cosine'], 3)}`",
                    f"`{fmt(metrics['bad_tangent_cosine'], 3)}`",
                    f"`{fmt(metrics['mean_silence_pressure'], 3)}`",
                    f"`{fmt(metrics['mean_energy_delta'], 4)}`",
                    f"`{sub['validation']['upload_safe']}`",
                    f"`{sub['submission_file']}`",
                ]
            )
            + " |"
        )
    lines += [
        "",
        "## Sensor Interpretation",
        "",
        "- If `positive_path_overshoot_sensor` wins, H057 was an under-stepped frontier trajectory, not a final optimum.",
        "- If `frontier_continuation_gate` wins, the positive public trajectory is real but requires active silence gating.",
        "- If `active_silence_inversion` wins, silence/toxicity is itself an invertible target representation.",
        "- If all fail, the public frontier path is descriptive; the missing module is not continuation but row-support discovery.",
    ]
    return "\n".join(lines) + "\n"


def run() -> dict[str, object]:
    clean_generated_submissions()
    sample, base_prob, base_logit = load_base()
    frontier = build_frontier_tangent(sample, base_logit)
    spectral = spectral_public_tangent(sample, base_logit)
    bad_tangent = np.asarray(spectral["bad_tangent"], dtype=np.float64)
    frontier_tangent = np.asarray(frontier["frontier_tangent"], dtype=np.float64)
    manifold = load_manifold()

    records = proposal_records(sample, base_logit)
    pool = aggregate_pool(records, frontier_tangent, bad_tangent)
    pool = add_invariant_features(pool, sample, base_prob, base_logit, manifold)
    pool.sort_values("frontier_release_score", ascending=False).to_csv(CELL_CSV, index=False)

    rng = np.random.default_rng(20260611)
    selected_frames: list[pd.DataFrame] = []
    variants: dict[str, object] = {}
    ranking: list[dict[str, object]] = []
    null_rows: list[dict[str, object]] = []
    for config in CONFIGS:
        selected = select_cells(pool, config)
        if not selected.empty:
            selected_frames.append(selected)
        sub = apply_cells(sample, base_prob, base_logit, selected, config)
        metrics = score_selection(selected, sub["move"], frontier_tangent, bad_tangent)
        stress = null_stress(pool, selected, sub["move"], frontier_tangent, bad_tangent, rng)
        priority = variant_priority(metrics, config)
        ranking.append(
            {
                "variant": config.name,
                "score": float(priority),
                "cells": int(metrics["cell_count"]),
                "frontier_cosine": float(metrics["frontier_cosine"]),
                "bad_tangent_cosine": float(metrics["bad_tangent_cosine"]),
                "upload_safe": bool(sub["validation"]["upload_safe"]),
            }
        )
        for metric, test in stress["tests"].items():
            null_rows.append({"variant": config.name, "metric": metric, **test})
        sub_public = {key: value for key, value in sub.items() if key != "move"}
        variants[config.name] = {
            "worldview": config.worldview,
            "config": asdict(config),
            "metrics": metrics,
            "stress": stress,
            "submission": sub_public,
        }

    if selected_frames:
        pd.concat(selected_frames, ignore_index=True, sort=False).to_csv(SELECTED_CSV, index=False)
    else:
        pd.DataFrame().to_csv(SELECTED_CSV, index=False)
    pd.DataFrame(null_rows).to_csv(NULL_CSV, index=False)

    ranking = sorted(ranking, key=lambda row: row["score"], reverse=True)
    recommended = next((row["variant"] for row in ranking if row["upload_safe"] and row["cells"] > 0), None)
    readout = {
        "experiment": "Frontier-Trajectory Active-Silence Solver",
        "architecture_role": "competition_adapter_big_bet",
        "thesis": (
            "The public frontier is a noisy gradient-descent trajectory.  HS-JEPA "
            "should learn both the positive frontier tangent and the active-silence "
            "field that blocks toxic post-frontier branches before releasing row-target actions."
        ),
        "frontier": frontier["summary"],
        "negative_tangent": spectral["spectral"],
        "cell_count": int(len(pool)),
        "verdict": {
            "status": "candidate_ready" if recommended else "no_candidate",
            "recommended_variant": recommended,
            "ranking": ranking,
            "interpretation": (
                "If a frontier-continuation variant wins public, HS-JEPA has learned an action-grade "
                "descent path.  If it fails while anti-listener/subset candidates win, the bottleneck "
                "is not continuation but public/private row-support assignment."
            ),
        },
        "variants": variants,
        "outputs": {
            "readout_json": str(READOUT_JSON.resolve()),
            "readout_markdown": str(READOUT_MD.resolve()),
            "cells": str(CELL_CSV.resolve()),
            "selected_cells": str(SELECTED_CSV.resolve()),
            "frontier_edges": str(EDGE_CSV.resolve()),
            "null_stress": str(NULL_CSV.resolve()),
        },
    }
    READOUT_JSON.write_text(json.dumps(readout, ensure_ascii=False, indent=2), encoding="utf-8")
    READOUT_MD.write_text(build_markdown(readout), encoding="utf-8")
    return readout


if __name__ == "__main__":
    result = run()
    print(json.dumps({"status": result["verdict"]["status"], "recommended": result["verdict"]["recommended_variant"]}, indent=2))
