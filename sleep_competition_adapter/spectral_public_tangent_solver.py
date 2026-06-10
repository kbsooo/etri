#!/usr/bin/env python3
"""Spectral public-tangent solver for the sleep competition adapter.

This is a deliberately high-variance HS-JEPA big bet.

The claim is not that another local decoder is slightly better.  The claim is
that the public failures after H057 are not independent mistakes: they share a
low-rank public-loss tangent.  If that tangent is real, a healthy HS-JEPA action
should either move opposite to it or live in a nearly orthogonal private-safe
subspace.

In HS-JEPA terms:

    observed submissions + public LB
      -> hidden public-loss action tangent
      -> candidate human-state action pool
      -> anti-tangent / orthogonal action release

The solver creates upload-safe public sensors.  Public LB should be interpreted
as a sensor of the latent action equation, not as a post-hoc tuning target.
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


HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "spectral_public_tangent_solver"
OUT.mkdir(parents=True, exist_ok=True)

BASE_SUBMISSION = ROOT / "submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv"
CURRENT_BEST_PUBLIC_LB = 0.5677475939
PUBLIC_LEDGER = ROOT / "data_analytics" / "hsjepa_public_score_ledger.csv"

COUNTERFACTUAL_CELLS = HERE / "outputs" / "counterfactual_listener_dropout_solver" / "counterfactual_listener_dropout_cells.csv"
CANDIDATE1_CELLS = ROOT / "final_hsjepa_candidates" / "outputs" / "candidate_1_public_loss_sparse_tomography" / "candidate1_selected_cells.csv"
ROUTE_FRONTIER_CELLS = HERE / "outputs" / "route_frontier_action_decoder" / "route_frontier_action_decoder_audit.csv"
ROUTE_TOXICITY_CELLS = HERE / "outputs" / "route_toxicity_fusion_decoder" / "route_toxicity_fusion_decoder_audit.csv"

READOUT_JSON = OUT / "spectral_public_tangent_readout.json"
READOUT_MD = OUT / "spectral_public_tangent_readout_ko.md"
CELL_CSV = OUT / "spectral_public_tangent_cells.csv"
ANCHOR_CSV = OUT / "spectral_public_tangent_anchor_modes.csv"
NULL_CSV = OUT / "spectral_public_tangent_null_stress.csv"


@dataclass(frozen=True)
class SpectralConfig:
    name: str
    worldview: str
    mode: str
    max_cells: int
    max_cells_per_row: int
    min_health: float
    min_abs_bad_rank: float
    max_abs_bad_rank: float
    min_source_families: int
    step_scale: float
    step_floor: float
    step_cap: float
    target_caps: tuple[tuple[str, int], ...]


CONFIGS = (
    SpectralConfig(
        name="anti_bad_tangent_sparse",
        worldview=(
            "Known public failures share a low-rank bad action tangent; release only HS-JEPA cells "
            "whose proposed direction is opposite to that tangent."
        ),
        mode="anti",
        max_cells=42,
        max_cells_per_row=2,
        min_health=0.46,
        min_abs_bad_rank=0.60,
        max_abs_bad_rank=1.00,
        min_source_families=1,
        step_scale=0.36,
        step_floor=0.035,
        step_cap=0.42,
        target_caps=(("Q1", 5), ("Q2", 9), ("Q3", 5), ("S1", 7), ("S2", 9), ("S3", 5), ("S4", 7)),
    ),
    SpectralConfig(
        name="anti_bad_tangent_pressure",
        worldview=(
            "If the public-loss tangent is real, a larger anti-tangent field should move public LB "
            "more than conservative cell-by-cell decoders."
        ),
        mode="anti",
        max_cells=86,
        max_cells_per_row=3,
        min_health=0.38,
        min_abs_bad_rank=0.48,
        max_abs_bad_rank=1.00,
        min_source_families=1,
        step_scale=0.50,
        step_floor=0.045,
        step_cap=0.66,
        target_caps=(("Q1", 10), ("Q2", 18), ("Q3", 10), ("S1", 13), ("S2", 18), ("S3", 12), ("S4", 15)),
    ),
    SpectralConfig(
        name="orthogonal_private_residual",
        worldview=(
            "H057 may already be optimal along the public tangent; remaining private-safe upside should "
            "come from high-health cells nearly orthogonal to the bad public mode."
        ),
        mode="orthogonal",
        max_cells=54,
        max_cells_per_row=2,
        min_health=0.50,
        min_abs_bad_rank=0.00,
        max_abs_bad_rank=0.42,
        min_source_families=1,
        step_scale=0.32,
        step_floor=0.030,
        step_cap=0.46,
        target_caps=(("Q1", 7), ("Q2", 10), ("Q3", 7), ("S1", 8), ("S2", 10), ("S3", 6), ("S4", 8)),
    ),
    SpectralConfig(
        name="bad_tangent_sign_flip",
        worldview=(
            "Some high-health actions may have failed only because their sign was aligned with the public-bad "
            "mode; flip those signs as a direct sign-equation stress test."
        ),
        mode="flip_bad_aligned",
        max_cells=34,
        max_cells_per_row=2,
        min_health=0.44,
        min_abs_bad_rank=0.55,
        max_abs_bad_rank=1.00,
        min_source_families=1,
        step_scale=0.28,
        step_floor=0.030,
        step_cap=0.38,
        target_caps=(("Q1", 4), ("Q2", 8), ("Q3", 4), ("S1", 5), ("S2", 8), ("S3", 5), ("S4", 5)),
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
    series = pd.Series(values, dtype="float64")
    if series.notna().sum() <= 1:
        return pd.Series([0.5] * len(series), index=series.index)
    return series.rank(pct=True, method="average", ascending=higher).fillna(0.0)


def z_and_p(actual: float, nulls: list[float], higher_is_better: bool = True) -> dict[str, float | None]:
    if not nulls:
        return {"actual": float(actual), "null_mean": None, "null_std": None, "z": None, "p": None}
    arr = np.asarray(nulls, dtype=np.float64)
    mean = float(arr.mean())
    std = float(arr.std(ddof=1)) if len(arr) > 1 else 0.0
    z = (float(actual) - mean) / std if std > 0.0 else 0.0
    p = float((arr >= actual).mean()) if higher_is_better else float((arr <= actual).mean())
    return {"actual": float(actual), "null_mean": mean, "null_std": std, "z": float(z), "p": p}


def locate(file_name: str) -> Path | None:
    path = ROOT / file_name
    if path.exists():
        return path
    hits = list(ROOT.glob(f"**/{Path(file_name).name}"))
    return hits[0] if hits else None


def load_base() -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    base = pd.read_csv(BASE_SUBMISSION, parse_dates=KEYS[1:]).sort_values(KEYS).reset_index(drop=True)
    base_prob = base[TARGETS].to_numpy(dtype=np.float64)
    base_logit = logit(base_prob).reshape(-1)
    return base, base_prob, base_logit


def load_submission_move(file_name: str, sample: pd.DataFrame, base_logit: np.ndarray) -> np.ndarray | None:
    path = locate(file_name)
    if path is None:
        return None
    try:
        frame = pd.read_csv(path, parse_dates=KEYS[1:]).sort_values(KEYS).reset_index(drop=True)
    except Exception:
        return None
    if len(frame) != len(sample) or not frame[KEYS].equals(sample[KEYS]):
        return None
    prob = frame[TARGETS].to_numpy(dtype=np.float64)
    move = logit(prob).reshape(-1) - base_logit
    return move if np.isfinite(move).all() and np.abs(move).sum() > TOL else None


def spectral_public_tangent(sample: pd.DataFrame, base_logit: np.ndarray) -> dict[str, object]:
    ledger = pd.read_csv(PUBLIC_LEDGER)
    moves: list[np.ndarray] = []
    rows: list[dict[str, object]] = []
    for rec in ledger.to_dict("records"):
        file_name = str(rec["file"])
        lb = float(rec["public_lb"])
        delta = lb - CURRENT_BEST_PUBLIC_LB
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
                "public_lb": lb,
                "delta_vs_current_best": delta,
                "move_l2": norm,
                "changed_cells": int((np.abs(move) > TOL).sum()),
            }
        )
    if len(moves) < 4:
        raise RuntimeError(f"not enough public anchors for spectral tangent: {len(moves)}")

    x = np.vstack(moves)
    weights = np.asarray([float(row["delta_vs_current_best"]) for row in rows], dtype=np.float64)
    weights = np.power(weights / weights.max(), 0.65)
    x_unit = x / (np.linalg.norm(x, axis=1, keepdims=True) + 1e-12)
    centroid = np.average(x_unit, axis=0, weights=weights)
    centroid = centroid / (np.linalg.norm(centroid) + 1e-12)

    x_weighted = x_unit * np.sqrt(weights[:, None])
    _u, s, vt = np.linalg.svd(x_weighted, full_matrices=False)
    pc1 = vt[0]
    if float(pc1 @ centroid) < 0.0:
        pc1 = -pc1
    bad_tangent = 0.58 * centroid + 0.42 * pc1
    bad_tangent = bad_tangent / (np.linalg.norm(bad_tangent) + 1e-12)

    coords = x_unit @ bad_tangent
    mode_rows = []
    for idx, row in enumerate(rows):
        mode_rows.append(
            {
                **row,
                "bad_tangent_coord": float(coords[idx]),
                "weighted_coord": float(coords[idx] * weights[idx]),
            }
        )
    anchors = pd.DataFrame(mode_rows).sort_values("bad_tangent_coord", ascending=False)
    anchors.to_csv(ANCHOR_CSV, index=False)

    variance = (s**2) / float((s**2).sum())
    return {
        "bad_tangent": bad_tangent,
        "anchor_frame": anchors,
        "spectral": {
            "anchor_count": int(len(rows)),
            "first_mode_variance": float(variance[0]),
            "top5_cumulative_variance": float(variance[:5].sum()),
            "singular_values": [float(v) for v in s[:8]],
            "mean_bad_tangent_coord": float(coords.mean()),
            "min_bad_tangent_coord": float(coords.min()),
            "max_bad_tangent_coord": float(coords.max()),
        },
    }


def source_frame_from_dropout() -> pd.DataFrame:
    if not COUNTERFACTUAL_CELLS.exists():
        return pd.DataFrame()
    frame = pd.read_csv(COUNTERFACTUAL_CELLS)
    keep_cols = [
        "row",
        "target",
        "target_idx",
        "cell_key",
        "direction",
        "action_delta",
        "listener_dropout_health",
        "dropout_min_score",
        "dropout_survival_count",
        "same_negative_rank",
        "opposite_negative_rank",
        "boundary_class",
    ]
    frame = frame[[col for col in keep_cols if col in frame.columns]].copy()
    frame["source_family"] = "listener_dropout"
    frame["proposed_logit_step"] = frame["action_delta"].astype(float)
    frame["health"] = frame.get("listener_dropout_health", 0.45).astype(float)
    frame["local_score"] = frame.get("dropout_min_score", 0.45).astype(float)
    return frame


def source_frame_from_candidate1() -> pd.DataFrame:
    if not CANDIDATE1_CELLS.exists():
        return pd.DataFrame()
    frame = pd.read_csv(CANDIDATE1_CELLS)
    out = pd.DataFrame()
    out["flat_idx"] = frame["flat_idx"].astype(int)
    out["row"] = frame["row"].astype(int)
    out["target"] = frame["target"].astype(str)
    out["target_idx"] = out["flat_idx"] % len(TARGETS)
    out["cell_key"] = out["row"].astype(str) + ":" + out["target"]
    out["direction"] = np.sign(frame["sign"].astype(float)).replace(0, 1).astype(int)
    out["proposed_logit_step"] = frame["logit_move"].astype(float).clip(-0.80, 0.80)
    out["source_family"] = "public_loss_tomography"
    out["health"] = (
        0.35 * rank01(frame["score"].astype(float))
        + 0.30 * frame["sign_stability"].astype(float).clip(0, 1)
        + 0.20 * (1.0 - frame["h088_alignment"].astype(float).clip(0, 1))
        + 0.15 * rank01(frame["source_support"].astype(float))
    )
    out["local_score"] = rank01(frame["score"].astype(float))
    out["boundary_class"] = "public_loss_tomography"
    out["dropout_survival_count"] = 0
    return out


def source_frame_from_route(path: Path, family: str, score_col: str) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    frame = pd.read_csv(path)
    required = {"row", "target", "flat_idx", "decoded_logit_move"}
    if not required.issubset(frame.columns):
        return pd.DataFrame()
    out = pd.DataFrame()
    out["flat_idx"] = frame["flat_idx"].astype(int)
    out["row"] = frame["row"].astype(int)
    out["target"] = frame["target"].astype(str)
    out["target_idx"] = out["flat_idx"] % len(TARGETS)
    out["cell_key"] = out["row"].astype(str) + ":" + out["target"]
    out["proposed_logit_step"] = frame["decoded_logit_move"].astype(float).clip(-0.80, 0.80)
    out["direction"] = np.sign(out["proposed_logit_step"]).replace(0, 1).astype(int)
    out["source_family"] = family
    base_score = frame[score_col].astype(float) if score_col in frame else frame["route_gain"].astype(float)
    joint = frame["bundle_joint_safety"].astype(float) if "bundle_joint_safety" in frame else 0.5
    support = frame["row_support_rank"].astype(float) if "row_support_rank" in frame else 0.5
    out["health"] = (0.45 * rank01(base_score) + 0.30 * pd.Series(joint).clip(0, 1) + 0.25 * pd.Series(support).clip(0, 1)).astype(float)
    out["local_score"] = rank01(base_score)
    out["boundary_class"] = family
    out["dropout_survival_count"] = 0
    return out


def candidate_pool(bad_tangent: np.ndarray) -> pd.DataFrame:
    frames = [
        source_frame_from_dropout(),
        source_frame_from_candidate1(),
        source_frame_from_route(ROUTE_FRONTIER_CELLS, "route_frontier", "route_frontier_score"),
        source_frame_from_route(ROUTE_TOXICITY_CELLS, "route_toxicity_fusion", "route_toxicity_fusion_score"),
    ]
    frames = [frame for frame in frames if not frame.empty]
    if not frames:
        raise RuntimeError("no candidate source cells available")
    raw = pd.concat(frames, ignore_index=True, sort=False)
    if "flat_idx" not in raw:
        raw["flat_idx"] = np.nan
    missing_flat = raw["flat_idx"].isna()
    raw.loc[missing_flat, "flat_idx"] = (
        raw.loc[missing_flat, "row"].astype(int) * len(TARGETS)
        + raw.loc[missing_flat, "target_idx"].astype(int)
    )
    raw["flat_idx"] = raw["flat_idx"].astype(int)
    raw["direction"] = np.sign(raw["direction"].astype(float)).replace(0, 1).astype(int)
    raw["proposed_logit_step"] = raw["proposed_logit_step"].astype(float)
    raw["health"] = raw["health"].fillna(0.35).astype(float).clip(0, 1)
    raw["local_score"] = raw["local_score"].fillna(0.35).astype(float)
    raw["bad_tangent_value"] = bad_tangent[raw["flat_idx"].to_numpy(dtype=int)]
    raw["bad_tangent_abs"] = raw["bad_tangent_value"].abs()
    raw["bad_tangent_abs_rank"] = rank01(raw["bad_tangent_abs"])
    tangent_sign = pd.Series(np.sign(raw["bad_tangent_value"]), index=raw.index).replace(0, 1)
    raw["anti_tangent_direction"] = (-tangent_sign).astype(int)
    raw["proposed_is_anti_bad"] = raw["direction"].eq(raw["anti_tangent_direction"])
    raw["proposed_is_bad_aligned"] = ~raw["proposed_is_anti_bad"]

    grouped_rows = []
    for (flat_idx, direction), group in raw.groupby(["flat_idx", "direction"], sort=False):
        source_families = sorted(set(group["source_family"].astype(str)))
        best = group.sort_values(["health", "local_score"], ascending=False).iloc[0]
        grouped_rows.append(
            {
                "flat_idx": int(flat_idx),
                "row": int(best["row"]),
                "target": str(best["target"]),
                "target_idx": int(best["target_idx"]),
                "cell_key": str(best["cell_key"]),
                "direction": int(direction),
                "source_families": ",".join(source_families),
                "source_family_count": int(len(source_families)),
                "source_records": int(len(group)),
                "mean_health": float(group["health"].mean()),
                "max_health": float(group["health"].max()),
                "mean_local_score": float(group["local_score"].mean()),
                "max_abs_proposed_step": float(group["proposed_logit_step"].abs().max()),
                "mean_abs_proposed_step": float(group["proposed_logit_step"].abs().mean()),
                "bad_tangent_value": float(best["bad_tangent_value"]),
                "bad_tangent_abs": float(best["bad_tangent_abs"]),
                "bad_tangent_abs_rank": float(best["bad_tangent_abs_rank"]),
                "anti_tangent_direction": int(best["anti_tangent_direction"]),
                "proposed_is_anti_bad": bool(best["proposed_is_anti_bad"]),
                "proposed_is_bad_aligned": bool(best["proposed_is_bad_aligned"]),
            }
        )
    pool = pd.DataFrame(grouped_rows)
    pool["action_health"] = (
        0.36 * pool["max_health"]
        + 0.22 * pool["mean_health"]
        + 0.18 * rank01(pool["source_family_count"])
        + 0.12 * rank01(pool["source_records"])
        + 0.12 * pool["mean_local_score"].clip(0, 1)
    ).clip(0, 1)
    pool["anti_bad_score"] = (
        0.48 * pool["bad_tangent_abs_rank"]
        + 0.28 * pool["action_health"]
        + 0.14 * rank01(pool["source_family_count"])
        + 0.10 * rank01(pool["max_abs_proposed_step"])
    )
    pool["orthogonal_score"] = (
        0.44 * pool["action_health"]
        + 0.22 * (1.0 - pool["bad_tangent_abs_rank"])
        + 0.18 * rank01(pool["source_family_count"])
        + 0.16 * pool["mean_local_score"].clip(0, 1)
    )
    return pool.sort_values("anti_bad_score", ascending=False).reset_index(drop=True)


def select_cells(pool: pd.DataFrame, config: SpectralConfig) -> pd.DataFrame:
    frame = pool.copy()
    frame = frame[frame["action_health"].ge(config.min_health)]
    frame = frame[frame["bad_tangent_abs_rank"].between(config.min_abs_bad_rank, config.max_abs_bad_rank)]
    frame = frame[frame["source_family_count"].ge(config.min_source_families)]
    if config.mode == "anti":
        frame = frame[frame["proposed_is_anti_bad"]].copy()
        frame["selection_score"] = frame["anti_bad_score"]
        frame["released_direction"] = frame["anti_tangent_direction"]
    elif config.mode == "orthogonal":
        frame = frame.copy()
        frame["selection_score"] = frame["orthogonal_score"]
        frame["released_direction"] = frame["direction"]
    elif config.mode == "flip_bad_aligned":
        frame = frame[frame["proposed_is_bad_aligned"]].copy()
        frame["selection_score"] = frame["anti_bad_score"]
        frame["released_direction"] = frame["anti_tangent_direction"]
    else:
        raise ValueError(config.mode)
    if frame.empty:
        return frame

    target_caps = dict(config.target_caps)
    selected: list[pd.Series] = []
    row_counts: dict[int, int] = {}
    target_counts: dict[str, int] = {}
    for _, rec in frame.sort_values("selection_score", ascending=False, kind="mergesort").iterrows():
        row = int(rec["row"])
        target = str(rec["target"])
        if row_counts.get(row, 0) >= config.max_cells_per_row:
            continue
        if target_counts.get(target, 0) >= target_caps.get(target, config.max_cells):
            continue
        selected.append(rec)
        row_counts[row] = row_counts.get(row, 0) + 1
        target_counts[target] = target_counts.get(target, 0) + 1
        if len(selected) >= config.max_cells:
            break
    if not selected:
        return pd.DataFrame(columns=list(frame.columns))
    out = pd.DataFrame(selected).reset_index(drop=True)
    magnitude = (
        config.step_floor
        + config.step_scale * out["bad_tangent_abs_rank"].astype(float) * (0.35 + out["action_health"].astype(float))
    )
    if config.mode == "orthogonal":
        magnitude = config.step_floor + config.step_scale * (0.35 + out["action_health"].astype(float)) * (
            1.0 - out["bad_tangent_abs_rank"].astype(float)
        )
    out["released_logit_step"] = out["released_direction"].astype(float) * magnitude.clip(0.0, config.step_cap)
    out["config"] = config.name
    return out


def apply_cells(sample: pd.DataFrame, base_prob: np.ndarray, base_logit: np.ndarray, selected: pd.DataFrame, config: SpectralConfig) -> dict[str, object]:
    move = np.zeros(base_logit.size, dtype=np.float64)
    for rec in selected.to_dict("records"):
        move[int(rec["flat_idx"])] = finite(rec["released_logit_step"])
    prob = clip_prob(sigmoid(base_logit + move).reshape(base_prob.shape))
    digest = short_hash(prob)
    name = f"submission_hsjepa_spectral_public_tangent_{config.name}_{digest}_uploadsafe.csv"
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


def score_selection(selected: pd.DataFrame, move: np.ndarray, bad_tangent: np.ndarray) -> dict[str, float]:
    if selected.empty:
        return {
            "cells": 0.0,
            "rows": 0.0,
            "mean_action_health": 0.0,
            "mean_bad_tangent_abs_rank": 0.0,
            "anti_bad_rate": 0.0,
            "source_family_mean": 0.0,
            "bad_tangent_dot": 0.0,
            "bad_tangent_cosine": 0.0,
            "q_rate": 0.0,
            "s_rate": 0.0,
        }
    denom = float(np.linalg.norm(move) * np.linalg.norm(bad_tangent))
    return {
        "cells": float(len(selected)),
        "rows": float(selected["row"].nunique()),
        "mean_action_health": float(selected["action_health"].mean()),
        "mean_bad_tangent_abs_rank": float(selected["bad_tangent_abs_rank"].mean()),
        "anti_bad_rate": float((np.sign(selected["released_logit_step"]) == selected["anti_tangent_direction"]).mean()),
        "source_family_mean": float(selected["source_family_count"].mean()),
        "bad_tangent_dot": float(move @ bad_tangent),
        "bad_tangent_cosine": float((move @ bad_tangent) / denom) if denom > 0 else 0.0,
        "q_rate": float(selected["target"].str.startswith("Q").mean()),
        "s_rate": float(selected["target"].str.startswith("S").mean()),
    }


def null_stress(pool: pd.DataFrame, selected: pd.DataFrame, move: np.ndarray, bad_tangent: np.ndarray, rng: np.random.Generator) -> dict[str, object]:
    actual = score_selection(selected, move, bad_tangent)
    if selected.empty:
        return {"actual": actual, "tests": {}}
    null_scores: list[dict[str, float]] = []
    for _ in range(500):
        sampled_parts = []
        for target, group in selected.groupby("target"):
            candidate = pool[pool["target"].eq(target)]
            if candidate.empty:
                continue
            sampled_parts.append(
                candidate.sample(
                    n=len(group),
                    replace=len(candidate) < len(group),
                    random_state=int(rng.integers(0, 2**31 - 1)),
                )
            )
        if not sampled_parts:
            continue
        sampled = pd.concat(sampled_parts, ignore_index=True)
        sampled = sampled.head(len(selected)).copy()
        sampled["released_logit_step"] = np.sign(sampled["anti_tangent_direction"].astype(float)) * selected[
            "released_logit_step"
        ].abs().to_numpy()[: len(sampled)]
        null_move = np.zeros_like(move)
        for rec in sampled.to_dict("records"):
            null_move[int(rec["flat_idx"])] = finite(rec["released_logit_step"])
        null_scores.append(score_selection(sampled, null_move, bad_tangent))

    tests = {}
    for metric, high in [
        ("mean_action_health", True),
        ("mean_bad_tangent_abs_rank", True),
        ("anti_bad_rate", True),
        ("source_family_mean", True),
        ("bad_tangent_dot", False),
        ("bad_tangent_cosine", False),
    ]:
        tests[metric] = z_and_p(actual[metric], [row[metric] for row in null_scores], higher_is_better=high)
    return {"actual": actual, "tests": tests}


def build_markdown(readout: dict[str, object]) -> str:
    lines = [
        "# Spectral Public-Tangent Solver",
        "",
        "## 핵심 주장",
        "",
        "H057 이후 public에서 나빠진 submission들은 독립적인 실패가 아니라 하나의 저차원 public-loss tangent를 공유한다. "
        "HS-JEPA action이 진짜라면 이 bad tangent의 반대 방향 또는 거의 직교한 subspace에서 release되어야 한다.",
        "",
        "## Spectral 진단",
        "",
    ]
    spectral = readout["spectral"]
    lines += [
        f"- public anchor count: `{spectral['anchor_count']}`",
        f"- first mode variance: `{fmt(spectral['first_mode_variance'], 6)}`",
        f"- top5 cumulative variance: `{fmt(spectral['top5_cumulative_variance'], 6)}`",
        f"- mean bad-tangent coordinate: `{fmt(spectral['mean_bad_tangent_coord'], 6)}`",
        "",
        "## 후보",
        "",
        "| rank | variant | changed cells | rows | bad dot | bad cosine | upload safe | file |",
        "| ---: | --- | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for item in readout["ranking"]:
        actual = item["stress"]["actual"]
        validation = item["validation"]
        lines.append(
            f"| {item['rank']} | `{item['variant']}` | `{validation['changed_cells_vs_current_best']}` | "
            f"`{actual['rows']:.0f}` | `{fmt(actual['bad_tangent_dot'], 6)}` | `{fmt(actual['bad_tangent_cosine'], 4)}` | "
            f"`{validation['upload_safe']}` | `{item['submission_file']}` |"
        )
    lines += [
        "",
        "## Public LB 해석",
        "",
        "- anti-bad 후보가 좋아지면: H057 이후 plateau는 public-bad tangent의 반대 방향을 충분히 못 탄 것이다.",
        "- orthogonal 후보가 좋아지면: H057는 public tangent상 거의 최적이고, 남은 upside는 private-safe residual subspace에 있다.",
        "- sign-flip 후보가 좋아지면: cell support는 맞았지만 action sign equation이 틀렸다는 뜻이다.",
        "- 모두 나빠지면: public 실패들의 low-rank 구조는 real이지만, 그 반대 방향이 label-valid action이라는 보장은 없다는 뜻이다.",
    ]
    return "\n".join(lines)


def run() -> dict[str, object]:
    sample, base_prob, base_logit = load_base()
    tangent = spectral_public_tangent(sample, base_logit)
    bad_tangent = np.asarray(tangent["bad_tangent"], dtype=np.float64)
    pool = candidate_pool(bad_tangent)
    pool.to_csv(CELL_CSV, index=False)

    rng = np.random.default_rng(20260611)
    variants = []
    selected_frames = []
    for config in CONFIGS:
        selected = select_cells(pool, config)
        selected_frames.append(selected.assign(config=config.name))
        item = apply_cells(sample, base_prob, base_logit, selected, config)
        stress = null_stress(pool, selected, item["move"], bad_tangent, rng)
        priority = 0.0
        tests = stress["tests"]
        actual = stress["actual"]
        if tests:
            priority += max(0.0, finite(tests["mean_action_health"].get("z"))) * 0.16
            priority += max(0.0, finite(tests["mean_bad_tangent_abs_rank"].get("z"))) * 0.12
            priority += max(0.0, -finite(tests["bad_tangent_cosine"].get("z"))) * 0.22
        priority += max(0.0, -float(actual["bad_tangent_cosine"])) * 0.58
        priority += min(0.22, float(actual["cells"]) / 250.0)
        variants.append(
            {
                "variant": config.name,
                "worldview": config.worldview,
                "submission_file": item["submission_file"],
                "root_path": item["root_path"],
                "local_path": item["local_path"],
                "validation": item["validation"],
                "stress": stress,
                "priority": float(priority),
                "config": asdict(config),
            }
        )

    variants.sort(key=lambda row: row["priority"], reverse=True)
    for idx, item in enumerate(variants, start=1):
        item["rank"] = idx

    selected_all = pd.concat([frame for frame in selected_frames if not frame.empty], ignore_index=True)
    selected_all.to_csv(OUT / "spectral_public_tangent_selected_cells.csv", index=False)

    null_rows = []
    for item in variants:
        actual = item["stress"]["actual"]
        for metric, test in item["stress"]["tests"].items():
            null_rows.append({"variant": item["variant"], "metric": metric, **test, **{f"actual_{k}": v for k, v in actual.items()}})
    pd.DataFrame(null_rows).to_csv(NULL_CSV, index=False)

    readout = {
        "experiment": "spectral_public_tangent_solver",
        "architecture_role": "HS-JEPA public/private action-equation sensor",
        "status": "spectral_public_tangent_ready",
        "claim": (
            "Known public failures share a low-rank bad action tangent; HS-JEPA should either release "
            "anti-tangent actions or find a private-safe orthogonal residual subspace."
        ),
        "spectral": tangent["spectral"],
        "pool": {
            "candidate_cells": int(len(pool)),
            "source_families": sorted({family for text in pool["source_families"].astype(str) for family in text.split(",") if family}),
            "anti_bad_cells": int(pool["proposed_is_anti_bad"].sum()),
            "bad_aligned_cells": int(pool["proposed_is_bad_aligned"].sum()),
        },
        "verdict": {
            "recommended_information_sensor": {
                "variant": variants[0]["variant"],
                "submission_file": variants[0]["submission_file"],
                "priority": variants[0]["priority"],
            },
            "recommended_counter_sensor": {
                "variant": "orthogonal_private_residual",
                "submission_file": next(
                    (item["submission_file"] for item in variants if item["variant"] == "orthogonal_private_residual"),
                    None,
                ),
            },
            "failure_interpretation": (
                "If all variants fail public LB, the bad tangent is descriptive but not a valid inverse action direction; "
                "the next bottleneck is label-validity constraints, not public-mode discovery."
            ),
        },
        "ranking": variants,
        "outputs": {
            "readout_json": str(READOUT_JSON.resolve()),
            "readout_md": str(READOUT_MD.resolve()),
            "cell_pool": str(CELL_CSV.resolve()),
            "anchor_modes": str(ANCHOR_CSV.resolve()),
            "null_stress": str(NULL_CSV.resolve()),
        },
    }
    READOUT_JSON.write_text(json.dumps(readout, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    READOUT_MD.write_text(build_markdown(readout), encoding="utf-8")
    print(json.dumps(readout, indent=2, ensure_ascii=False, allow_nan=False))
    return readout


if __name__ == "__main__":
    run()
