#!/usr/bin/env python3
"""H111: global boundary assignment solver HS-JEPA.

H110 made the first explicit benefit/toxicity split, but its own boundary audit
found a contradiction: H108 cells rejected by H110 had higher local
benefit-toxicity gap than many H110-kept cells.  That means the next problem is
not local cell scoring.  It is global assignment under public-bad-axis
interactions.

H111 treats H110's pool as a set of signed row-target items and uses a small
beam/knapsack solver to choose a globally safe boundary.  It explicitly labels
H108-kept, H108-rejected, and H110-added cells so the solver can test whether
the missing signal is "rescue high-gap H108 cells" rather than adding another
local filter.
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
OUT = HITL / "h111_global_boundary_assignment_solver_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H110_PATH = HITL / "h110_toxicity_gap_assignment_solver_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h110mod", H110_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H110_PATH}")
h110mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h110mod
SPEC.loader.exec_module(h110mod)

h109mod = h110mod.h109mod
h102mod = h110mod.h102mod
h100mod = h110mod.h100mod
h097mod = h110mod.h097mod
h085mod = h110mod.h085mod

TARGETS = h110mod.TARGETS
KEYS = h110mod.KEYS
BASE_FILE = h110mod.BASE_FILE
TOL = h110mod.TOL

H108_ID = "h108_strict_intersection_c48_a085_610a26a0"
H109_ID = "h109_kernel_coeff_focus_c48_t7_54147083"
H110_ID = "h110_toxgap_kernel_release_c64_a085_7b02f196"


@dataclass(frozen=True)
class H111Spec:
    name: str
    group: str
    max_cells: int
    max_rows: int
    max_per_subject: int
    max_per_target: int
    q2_cap: int
    amp: float
    cap: float
    pool_top: int
    beam_width: int
    min_boundary_score: float
    min_gap: float
    min_family_count: int
    max_toxicity: float
    max_bad_weighted_pos: float
    max_bad_max_pos: float
    max_h088_cos: float
    min_good_margin: float
    route_pred_cap: float
    h098_pred_cap: float
    worldview: str


@dataclass
class BeamState:
    selected: tuple[int, ...]
    move_mat: np.ndarray
    rows: frozenset[int]
    subjects: tuple[tuple[str, int], ...]
    targets: tuple[tuple[str, int], ...]
    q2_count: int
    score: float
    axis: dict[str, float]


def clip_prob(x: np.ndarray) -> np.ndarray:
    return h085mod.clip_prob(np.asarray(x, dtype=np.float64))


def logit(x: np.ndarray) -> np.ndarray:
    return h085mod.logit(np.asarray(x, dtype=np.float64))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return h085mod.sigmoid(np.asarray(x, dtype=np.float64))


def rank01(values: np.ndarray, high: bool = True) -> np.ndarray:
    return h085mod.rank01(np.asarray(values, dtype=np.float64), high=high)


def safe_id(text: str, limit: int = 132) -> str:
    return h085mod.safe_id(text, limit=limit)


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return h085mod.md_table(frame, n=n)


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h111_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h111_boundary_*.csv"):
        path.unlink()


def candidate_specs() -> list[H111Spec]:
    return [
        H111Spec(
            name="rescue_h108_rejected_c62_a072",
            group="rescue_h108",
            max_cells=62,
            max_rows=38,
            max_per_subject=10,
            max_per_target=20,
            q2_cap=0,
            amp=0.72,
            cap=0.27,
            pool_top=96,
            beam_width=72,
            min_boundary_score=0.45,
            min_gap=0.18,
            min_family_count=3,
            max_toxicity=0.66,
            max_bad_weighted_pos=0.006,
            max_bad_max_pos=0.032,
            max_h088_cos=-0.003,
            min_good_margin=0.012,
            route_pred_cap=0.000080,
            h098_pred_cap=0.000075,
            worldview="H110's local toxicity score was useful, but the global solver should rescue high-gap H108 cells that greedy selection skipped",
        ),
        H111Spec(
            name="boundary_kernel_beam_c70_a078",
            group="kernel_beam",
            max_cells=70,
            max_rows=36,
            max_per_subject=16,
            max_per_target=20,
            q2_cap=0,
            amp=0.78,
            cap=0.29,
            pool_top=128,
            beam_width=80,
            min_boundary_score=0.40,
            min_gap=0.14,
            min_family_count=2,
            max_toxicity=0.68,
            max_bad_weighted_pos=0.008,
            max_bad_max_pos=0.040,
            max_h088_cos=-0.002,
            min_good_margin=0.010,
            route_pred_cap=0.000100,
            h098_pred_cap=0.000085,
            worldview="safe assignment is a globally optimized H105/H106/H108/H110 boundary, not H110's greedy kernel release",
        ),
        H111Spec(
            name="boundary_objective_beam_c110_a058",
            group="objective",
            max_cells=110,
            max_rows=68,
            max_per_subject=12,
            max_per_target=30,
            q2_cap=0,
            amp=0.58,
            cap=0.23,
            pool_top=170,
            beam_width=88,
            min_boundary_score=0.34,
            min_gap=0.10,
            min_family_count=2,
            max_toxicity=0.70,
            max_bad_weighted_pos=0.014,
            max_bad_max_pos=0.062,
            max_h088_cos=0.000,
            min_good_margin=0.004,
            route_pred_cap=0.000180,
            h098_pred_cap=0.000100,
            worldview="objective Q3/S assignment is broad, but only a global bad-axis beam can choose the safe subset",
        ),
        H111Spec(
            name="boundary_broad_null_c150_a048",
            group="broad_null",
            max_cells=150,
            max_rows=80,
            max_per_subject=13,
            max_per_target=36,
            q2_cap=6,
            amp=0.48,
            cap=0.20,
            pool_top=220,
            beam_width=96,
            min_boundary_score=0.30,
            min_gap=0.08,
            min_family_count=2,
            max_toxicity=0.72,
            max_bad_weighted_pos=0.016,
            max_bad_max_pos=0.070,
            max_h088_cos=0.000,
            min_good_margin=0.002,
            route_pred_cap=0.000220,
            h098_pred_cap=0.000110,
            worldview="a broad low-toxicity field is possible if assignment is solved globally instead of greedily",
        ),
    ]


def materialize(base_prob: np.ndarray, move_mat: np.ndarray) -> np.ndarray:
    return clip_prob(sigmoid(logit(base_prob) + move_mat))


def route_pred(move_flat: np.ndarray, basis_fit_df: pd.DataFrame, basis_fit_moves: np.ndarray, route_fit: h100mod.RouteBasisFit) -> float:
    return h100mod.predict_candidate_delta(move_flat, basis_fit_df, basis_fit_moves, route_fit)


def h098_pred(move_flat: np.ndarray, cell: pd.DataFrame, h098_fit: h097mod.ResponseFit) -> float:
    return h097mod.predict_candidate_delta(move_flat, cell, h098_fit)


def load_boundary_pool() -> pd.DataFrame:
    pool_path = HITL / "h110_toxicity_gap_assignment_solver_hsjepa" / "h110_toxicity_pool.csv"
    h108_path = HITL / "h108_decoder_jury_assignment_solver_hsjepa" / "h108_selected_cells.csv"
    h109_path = HITL / "h109_decoder_coefficient_equation_solver_hsjepa" / "h109_selected_cells.csv"
    h110_path = HITL / "h110_toxicity_gap_assignment_solver_hsjepa" / "h110_selected_cells.csv"
    if not (pool_path.exists() and h108_path.exists() and h110_path.exists()):
        raise FileNotFoundError("H108/H110 boundary inputs are missing")
    pool = pd.read_csv(pool_path).copy()
    h108 = pd.read_csv(h108_path)
    h110 = pd.read_csv(h110_path)
    h109 = pd.read_csv(h109_path) if h109_path.exists() else pd.DataFrame()

    h108_set = set(h108.loc[h108["candidate_id"].astype(str).eq(H108_ID), "flat_index"].astype(int))
    h110_set = set(h110.loc[h110["candidate_id"].astype(str).eq(H110_ID), "flat_index"].astype(int))
    h109_set = set(h109.loc[h109["candidate_id"].astype(str).eq(H109_ID), "flat_index"].astype(int)) if not h109.empty else set()
    flat = pool["flat_index"].astype(int)
    pool["h111_in_h108"] = flat.isin(h108_set).astype(float)
    pool["h111_in_h110"] = flat.isin(h110_set).astype(float)
    pool["h111_in_h109"] = flat.isin(h109_set).astype(float)
    pool["h111_h108_kept"] = (flat.isin(h108_set & h110_set)).astype(float)
    pool["h111_h108_rejected"] = (flat.isin(h108_set - h110_set)).astype(float)
    pool["h111_h110_added"] = (flat.isin(h110_set - h108_set)).astype(float)
    pool["h111_boundary_score"] = (
        0.34 * pool["h110_benefit_toxicity_gap"].to_numpy(dtype=np.float64)
        + 0.18 * pool["h110_benefit_score"].to_numpy(dtype=np.float64)
        - 0.22 * pool["h110_toxicity_score"].to_numpy(dtype=np.float64)
        + 0.10 * pool["h111_h108_rejected"].to_numpy(dtype=np.float64)
        + 0.08 * pool["h111_h108_kept"].to_numpy(dtype=np.float64)
        + 0.05 * pool["h111_h110_added"].to_numpy(dtype=np.float64)
        + 0.06 * pool["h111_in_h109"].to_numpy(dtype=np.float64)
        + 0.08 * pool["h110_anti_h088"].to_numpy(dtype=np.float64)
        + 0.06 * pool["h110_align_h057"].to_numpy(dtype=np.float64)
        + 0.05 * pool["h057_h088_anti_conflict"].to_numpy(dtype=np.float64)
        + 0.04 * pool["h095_safe_cell_score"].to_numpy(dtype=np.float64)
        + 0.03 * pool["h098_frontier_cell_score"].to_numpy(dtype=np.float64)
        + 0.03 * rank01(pool["h110_vote_weight"].to_numpy(dtype=np.float64), high=True)
        - 0.08 * pool["is_h050_null"].to_numpy(dtype=np.float64)
        - 0.06 * pool["latent_shortcut_energy"].to_numpy(dtype=np.float64)
        - 0.05 * pool["bad_pressure_rank"].to_numpy(dtype=np.float64)
        - 0.04 * pool["h080_bad_same_rank"].to_numpy(dtype=np.float64)
        - 0.04 * pool["target"].astype(str).eq("Q2").astype(float).to_numpy()
    )
    return pool


def group_allowed(row: dict[str, object], spec: H111Spec) -> bool:
    target = str(row["target"])
    if spec.group == "rescue_h108":
        return target != "Q2" and (bool(row["h111_in_h108"]) or bool(row["h111_in_h110"]))
    if spec.group == "kernel_beam":
        return target != "Q2" and (
            bool(row.get("h110_has_h105", False))
            or bool(row.get("h110_has_h106", False))
            or bool(row.get("h110_has_h108", False))
            or bool(row.get("h111_in_h110", False))
        )
    if spec.group == "objective":
        return target in {"Q3", "S1", "S2", "S3", "S4"}
    if spec.group == "broad_null":
        return True
    raise ValueError(spec.group)


def dict_get(items: tuple[tuple[str, int], ...], key: str) -> int:
    return dict(items).get(key, 0)


def dict_inc(items: tuple[tuple[str, int], ...], key: str) -> tuple[tuple[str, int], ...]:
    d = dict(items)
    d[key] = d.get(key, 0) + 1
    return tuple(sorted(d.items()))


def initial_state(shape: tuple[int, int]) -> BeamState:
    return BeamState(
        selected=tuple(),
        move_mat=np.zeros(shape, dtype=np.float64),
        rows=frozenset(),
        subjects=tuple(),
        targets=tuple(),
        q2_count=0,
        score=0.0,
        axis={
            "h102_cum_bad_max_pos": 0.0,
            "h102_cum_bad_weighted_pos": 0.0,
            "h102_cum_h088_axis_cos": 0.0,
            "h102_cum_good_max_cos": 0.0,
            "h102_cum_good_mean_cos": 0.0,
            "h102_cum_good_bad_margin": 0.0,
        },
    )


def state_rank_score(state: BeamState) -> float:
    return (
        state.score
        + 0.18 * max(state.axis["h102_cum_good_bad_margin"], 0.0)
        + 0.06 * max(-state.axis["h102_cum_h088_axis_cos"], 0.0)
        - 0.55 * max(state.axis["h102_cum_bad_weighted_pos"], 0.0)
        - 0.30 * max(state.axis["h102_cum_bad_max_pos"], 0.0)
        - 0.24 * max(state.axis["h102_cum_h088_axis_cos"], 0.0)
        + 0.010 * len(state.selected)
    )


def select_with_beam(
    pool: pd.DataFrame,
    spec: H111Spec,
    base_shape: tuple[int, int],
    bad_axes: pd.DataFrame,
    bad_moves: np.ndarray,
    good_moves: np.ndarray,
) -> tuple[pd.DataFrame, np.ndarray, dict[str, float]]:
    work = pool.copy()
    work["h111_move"] = np.clip(work["h110_raw_mean_move"].to_numpy(dtype=np.float64) * spec.amp, -spec.cap, spec.cap)
    work = work[np.abs(work["h111_move"].to_numpy(dtype=np.float64)) > 1.0e-10]
    work = work[work["h111_boundary_score"].to_numpy(dtype=np.float64) >= spec.min_boundary_score]
    work = work[work["h110_benefit_toxicity_gap"].to_numpy(dtype=np.float64) >= spec.min_gap]
    work = work[work["h110_family_count"].astype(int) >= spec.min_family_count]
    work = work[work["h110_toxicity_score"].to_numpy(dtype=np.float64) <= spec.max_toxicity]
    work = work[work.apply(lambda row: group_allowed(row, spec), axis=1)]
    work = work.sort_values(["h111_boundary_score", "h110_benefit_toxicity_gap"], ascending=[False, False]).head(spec.pool_top).reset_index(drop=True)

    states = [initial_state(base_shape)]
    for idx, rec in enumerate(work.to_dict("records")):
        next_states = states.copy()
        row = int(rec["row"])
        subject = str(rec["subject_id"])
        target = str(rec["target"])
        target_index = int(rec["target_index"])
        for state in states:
            if len(state.selected) >= spec.max_cells:
                continue
            if row not in state.rows and len(state.rows) >= spec.max_rows:
                continue
            if row not in state.rows and dict_get(state.subjects, subject) + 1 > spec.max_per_subject:
                continue
            if dict_get(state.targets, target) >= spec.max_per_target:
                continue
            if target == "Q2" and state.q2_count >= spec.q2_cap:
                continue
            tmp = state.move_mat.copy()
            tmp[row, target_index] = float(rec["h111_move"])
            axis = h102mod.cumulative_axis_metrics(tmp.reshape(-1), bad_axes, bad_moves, good_moves)
            if axis["h102_cum_bad_weighted_pos"] > spec.max_bad_weighted_pos:
                continue
            if axis["h102_cum_bad_max_pos"] > spec.max_bad_max_pos:
                continue
            if axis["h102_cum_h088_axis_cos"] > spec.max_h088_cos:
                continue
            if axis["h102_cum_good_bad_margin"] < spec.min_good_margin:
                continue
            bonus = (
                float(rec["h111_boundary_score"])
                + 0.08 * float(rec["h111_h108_rejected"])
                + 0.04 * float(rec["h111_h108_kept"])
                + 0.03 * float(rec["h111_h110_added"])
                + 0.02 * float(rec["h111_in_h109"])
            )
            next_states.append(
                BeamState(
                    selected=state.selected + (idx,),
                    move_mat=tmp,
                    rows=state.rows | {row},
                    subjects=dict_inc(state.subjects, subject) if row not in state.rows else state.subjects,
                    targets=dict_inc(state.targets, target),
                    q2_count=state.q2_count + int(target == "Q2"),
                    score=state.score + bonus,
                    axis=axis,
                )
            )
        next_states = sorted(next_states, key=state_rank_score, reverse=True)[: spec.beam_width]
        states = next_states

    final_states = [s for s in states if len(s.selected) > 0]
    if not final_states:
        return pd.DataFrame(), np.zeros(base_shape, dtype=np.float64), initial_state(base_shape).axis
    best = sorted(final_states, key=state_rank_score, reverse=True)[0]
    selected = work.iloc[list(best.selected)].copy().sort_values(["row", "target_index"]).reset_index(drop=True)
    selected["h097_move_col"] = "h111_move"
    selected["h111_beam_rank_score"] = state_rank_score(best)
    return selected, best.move_mat, best.axis


def evaluate_candidate(
    candidate_id: str,
    prob: np.ndarray,
    move_mat: np.ndarray,
    selected_cells: pd.DataFrame,
    cell: pd.DataFrame,
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    h098_fit: h097mod.ResponseFit,
    route_fit: h100mod.RouteBasisFit,
    basis_fit_df: pd.DataFrame,
    basis_fit_moves: np.ndarray,
    spec: H111Spec,
    path: Path,
    axis: dict[str, float],
) -> dict[str, object]:
    proxy = h097mod.H097Spec(
        name=spec.name,
        mode="global_boundary_assignment_solver",
        target_group=spec.group,
        k=spec.max_cells,
        alpha=spec.amp,
        cap=spec.cap,
        min_score=spec.min_boundary_score,
        worldview=spec.worldview,
    )
    out = h097mod.evaluate_candidate(candidate_id, prob, move_mat, base_prob, selected_cells, cell, sample, h098_fit, proxy, path)
    out.update(axis)
    out["route_basis_pred_delta_vs_h057"] = route_pred(move_mat.reshape(-1), basis_fit_df, basis_fit_moves, route_fit)
    out["selected_mean_boundary_score"] = float(selected_cells["h111_boundary_score"].mean()) if len(selected_cells) else 0.0
    out["selected_mean_gap"] = float(selected_cells["h110_benefit_toxicity_gap"].mean()) if len(selected_cells) else 0.0
    out["selected_mean_toxicity"] = float(selected_cells["h110_toxicity_score"].mean()) if len(selected_cells) else 0.0
    out["selected_h108_kept_cells"] = int(selected_cells["h111_h108_kept"].sum()) if len(selected_cells) else 0
    out["selected_h108_rejected_cells"] = int(selected_cells["h111_h108_rejected"].sum()) if len(selected_cells) else 0
    out["selected_h110_added_cells"] = int(selected_cells["h111_h110_added"].sum()) if len(selected_cells) else 0
    out["selected_h109_cells"] = int(selected_cells["h111_in_h109"].sum()) if len(selected_cells) else 0
    out["selected_mean_family_count"] = float(selected_cells["h110_family_count"].mean()) if len(selected_cells) else 0.0
    out["selected_mean_vote_weight"] = float(selected_cells["h110_vote_weight"].mean()) if len(selected_cells) else 0.0
    out["h111_information_mass"] = (
        0.50 * min(float(out["selected_cells"]) / 40.0, 1.0)
        + 0.28 * min(float(out["selected_h108_rejected_cells"]) / 12.0, 1.0)
        + 0.12 * min(float(out["changed_rows_vs_h057"]) / 24.0, 1.0)
        + 0.10 * min(float(out["selected_mean_family_count"]) / 4.0, 1.0)
    )
    out["h111_score"] = (
        150.0 * (-float(out["model_pred_delta_vs_h057"]))
        + 115.0 * (-float(out["route_basis_pred_delta_vs_h057"]))
        + 0.18 * float(out["anti_h088_direction_rate"])
        + 0.16 * float(out["h057_positive_align_rate"])
        + 0.14 * float(out["selected_conflict_rate"])
        + 0.12 * max(float(out["selected_mean_gap"]), 0.0)
        + 0.10 * max(float(out["selected_mean_boundary_score"]), 0.0)
        + 0.08 * min(float(out["selected_mean_family_count"]) / 4.0, 1.0)
        + 0.06 * max(float(out["h102_cum_good_bad_margin"]), 0.0)
        + 0.05 * max(-float(out["h102_cum_h088_axis_cos"]), 0.0)
        + 0.10 * float(out["h111_information_mass"])
        + 0.04 * min(float(out["selected_h108_rejected_cells"]) / 12.0, 1.0)
        - 0.18 * float(out["selected_mean_toxicity"])
        - 0.10 * float(float(out["selected_cells"]) < 8.0)
        - 0.60 * max(float(out["h102_cum_bad_weighted_pos"]), 0.0)
        - 0.36 * max(float(out["h102_cum_bad_max_pos"]), 0.0)
        - 0.32 * max(float(out["h102_cum_h088_axis_cos"]), 0.0)
        - 0.24 * max(float(out["max_positive_bad_cosine"]), 0.0)
        - 22.0 * max(float(out["hard_diag_delta_vs_h057"]), 0.0)
        - 10.0 * max(float(out["posterior_delta_vs_h057"]), 0.0)
    )
    return out


def run() -> None:
    cleanup_previous_outputs()
    base = h085mod.load_sub(BASE_FILE)
    sample = base[KEYS].copy()
    base_prob = base[TARGETS].to_numpy(dtype=np.float64)
    cell, h098_fit, route_fit, basis_fit_df, basis_fit_moves, bad_axes, bad_moves, _good_axes, good_moves = h109mod.build_context()
    pool = load_boundary_pool()

    audit_rows = []
    h108 = pool[pool["h111_in_h108"].astype(bool)]
    h110 = pool[pool["h111_in_h110"].astype(bool)]
    for name, mask in {
        "h108_kept": pool["h111_h108_kept"].astype(bool),
        "h108_rejected": pool["h111_h108_rejected"].astype(bool),
        "h110_added": pool["h111_h110_added"].astype(bool),
        "h108_all": pool["h111_in_h108"].astype(bool),
        "h110_all": pool["h111_in_h110"].astype(bool),
    }.items():
        df = pool[mask]
        audit_rows.append(
            {
                "group": name,
                "cells": int(len(df)),
                "mean_boundary_score": float(df["h111_boundary_score"].mean()) if len(df) else 0.0,
                "mean_gap": float(df["h110_benefit_toxicity_gap"].mean()) if len(df) else 0.0,
                "mean_benefit": float(df["h110_benefit_score"].mean()) if len(df) else 0.0,
                "mean_toxicity": float(df["h110_toxicity_score"].mean()) if len(df) else 0.0,
                "mean_bad_pressure": float(df["bad_pressure_rank"].mean()) if len(df) else 0.0,
                "mean_shortcut": float(df["latent_shortcut_energy"].mean()) if len(df) else 0.0,
            }
        )
    boundary_audit = pd.DataFrame(audit_rows)

    candidate_rows = []
    selected_frames = []
    top_frames = []
    for spec in candidate_specs():
        selected_cells, move_mat, axis = select_with_beam(pool, spec, base_prob.shape, bad_axes, bad_moves, good_moves)
        if selected_cells.empty:
            continue
        rpred = route_pred(move_mat.reshape(-1), basis_fit_df, basis_fit_moves, route_fit)
        cpred = h098_pred(move_mat.reshape(-1), cell, h098_fit)
        if rpred > spec.route_pred_cap:
            continue
        if cpred > spec.h098_pred_cap:
            continue
        prob = materialize(base_prob, move_mat)
        if int((np.abs(prob - base_prob) > TOL).sum()) == 0:
            continue
        hash_id = short_hash(prob)
        candidate_id = safe_id(f"h111_{spec.name}_{hash_id}", 128)
        path = OUT / f"submission_{candidate_id}.csv"
        h085mod.write_submission(sample, prob, path)
        metrics = evaluate_candidate(
            candidate_id,
            prob,
            move_mat,
            selected_cells,
            cell,
            sample,
            base_prob,
            h098_fit,
            route_fit,
            basis_fit_df,
            basis_fit_moves,
            spec,
            path,
            axis,
        )
        candidate_rows.append(metrics)
        selected_cells = selected_cells.copy()
        selected_cells.insert(0, "candidate_id", candidate_id)
        selected_frames.append(selected_cells)
        top = pool.sort_values(["h111_boundary_score", "h110_benefit_toxicity_gap"], ascending=[False, False]).head(360).copy()
        top.insert(0, "candidate_id", candidate_id)
        top_frames.append(top)

    candidates = pd.DataFrame(candidate_rows)
    if candidates.empty:
        raise RuntimeError("no H111 candidates")
    candidates = candidates.sort_values(["h111_score", "model_pred_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True)
    selected = candidates.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"submission_h111_boundary_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)

    decision = {
        "decision": "promote_h111_global_boundary_assignment_solver",
        "selected_candidate_id": selected["candidate_id"],
        "root_uploadsafe_path": str(root_path.resolve()),
        "worldview": selected["worldview"],
        "h108_cells": int(len(h108)),
        "h110_cells": int(len(h110)),
        "h108_kept": int(pool["h111_h108_kept"].sum()),
        "h108_rejected": int(pool["h111_h108_rejected"].sum()),
        "h110_added": int(pool["h111_h110_added"].sum()),
        "h098_feature_set": h098_fit.feature_set,
        "h098_alpha": h098_fit.alpha,
        **selected,
        **{f"root_{key}": value for key, value in validation.items()},
    }

    pool.to_csv(OUT / "h111_boundary_pool.csv", index=False)
    boundary_audit.to_csv(OUT / "h111_boundary_audit.csv", index=False)
    candidates.to_csv(OUT / "h111_candidates.csv", index=False)
    pd.concat(selected_frames, ignore_index=True).to_csv(OUT / "h111_selected_cells.csv", index=False)
    pd.concat(top_frames, ignore_index=True).to_csv(OUT / "h111_top_boundary_cells.csv", index=False)
    pd.DataFrame([decision]).to_csv(OUT / "h111_decision.csv", index=False)

    cols = [
        "candidate_id",
        "spec_name",
        "selected_cells",
        "changed_rows_vs_h057",
        "Q1_changed_vs_h057",
        "Q2_changed_vs_h057",
        "Q3_changed_vs_h057",
        "S1_changed_vs_h057",
        "S2_changed_vs_h057",
        "S3_changed_vs_h057",
        "S4_changed_vs_h057",
        "model_pred_delta_vs_h057",
        "route_basis_pred_delta_vs_h057",
        "h102_cum_bad_weighted_pos",
        "h102_cum_h088_axis_cos",
        "h102_cum_good_bad_margin",
        "selected_mean_boundary_score",
        "selected_mean_gap",
        "selected_mean_toxicity",
        "selected_h108_kept_cells",
        "selected_h108_rejected_cells",
        "selected_h110_added_cells",
        "selected_h109_cells",
        "h111_score",
        "file",
    ]
    report = f"""# H111 Global Boundary Assignment Solver HS-JEPA

Question: did H110 find the right local toxicity signal but use the wrong
greedy/global assignment boundary?

Boundary audit:

{md_table(boundary_audit, 10)}

Candidates:

{md_table(candidates[cols], 20)}

Decision:

{md_table(pd.DataFrame([decision]), 1)}

Interpretation rule:

- If H111 improves over H110, the missing module is global assignment over the
  benefit/toxicity field, not another local toxicity score.
- If H110 improves more, the local toxicity-gap greedy boundary was already
  better than H108-rejected rescue.
- If H108 improves more, both H110 and H111 over-modeled toxicity.
- If H109 improves more, public-safe action is a tiny kernel rather than a
  boundary optimization problem.
"""
    (OUT / "h111_report.md").write_text(report, encoding="utf-8")

    print(f"selected={decision['selected_candidate_id']}")
    print(f"root={root_path}")
    print(boundary_audit.to_string(index=False))
    print(candidates[cols].head(10).to_string(index=False))


if __name__ == "__main__":
    run()
