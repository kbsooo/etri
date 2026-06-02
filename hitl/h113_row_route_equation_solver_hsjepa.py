#!/usr/bin/env python3
"""H113: row-route equation solver HS-JEPA.

H112 projected public-equation residuals onto individual row-target cells.  That
is still a local action decoder.  H113 asks whether the missing public/private
equation is one level higher: a row can only be corrected safely when the right
target route inside that row moves together.

The unit of assignment is therefore a row-target bundle, not a single cell.  A
bundle is a small target route such as Q3+S, objective-stage route, H112 core
route, or H108-rejected antidote route.  The beam solver picks at most one route
per row under the same public-bad-axis stress constraints.
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
OUT = HITL / "h113_row_route_equation_solver_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H112_PATH = HITL / "h112_public_residual_toxicity_solver_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h112mod", H112_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H112_PATH}")
h112mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h112mod
SPEC.loader.exec_module(h112mod)

h111mod = h112mod.h111mod
h110mod = h112mod.h110mod
h109mod = h112mod.h109mod
h102mod = h112mod.h102mod
h100mod = h112mod.h100mod
h097mod = h112mod.h097mod
h085mod = h112mod.h085mod

TARGETS = h112mod.TARGETS
KEYS = h112mod.KEYS
BASE_FILE = h112mod.BASE_FILE
TOL = h112mod.TOL


@dataclass(frozen=True)
class H113Spec:
    name: str
    group: str
    max_cells: int
    max_rows: int
    max_per_subject: int
    max_per_target: int
    q2_cap: int
    amp: float
    cap: float
    bundle_top: int
    beam_width: int
    min_bundle_score: float
    min_bundle_targets: int
    max_bundle_targets: int
    min_gap: float
    max_residual_toxicity: float
    min_residual_safety: float
    max_bad_weighted_pos: float
    max_bad_max_pos: float
    max_h088_cos: float
    min_good_margin: float
    route_pred_cap: float
    h098_pred_cap: float
    min_score: float
    worldview: str


@dataclass
class RowBundle:
    bundle_id: str
    row: int
    subject_id: str
    template: str
    targets: tuple[str, ...]
    flat_indices: tuple[int, ...]
    target_indices: tuple[int, ...]
    moves: tuple[float, ...]
    score: float
    residual_toxicity: float
    residual_safety: float
    residual_gap: float
    antidote_score: float
    h111_rate: float
    h108_rejected_rate: float
    h109_rate: float
    family_count: float


@dataclass
class BeamState:
    selected: tuple[int, ...]
    move_mat: np.ndarray
    rows: frozenset[int]
    subjects: tuple[tuple[str, int], ...]
    targets: tuple[tuple[str, int], ...]
    q2_count: int
    cell_count: int
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
    for path in OUT.glob("submission_h113_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h113_rowroute_*.csv"):
        path.unlink()


def materialize(base_prob: np.ndarray, move_mat: np.ndarray) -> np.ndarray:
    return clip_prob(sigmoid(logit(base_prob) + move_mat))


def route_pred(move_flat: np.ndarray, basis_fit_df: pd.DataFrame, basis_fit_moves: np.ndarray, route_fit: h100mod.RouteBasisFit) -> float:
    return h100mod.predict_candidate_delta(move_flat, basis_fit_df, basis_fit_moves, route_fit)


def h098_pred(move_flat: np.ndarray, cell: pd.DataFrame, h098_fit: h097mod.ResponseFit) -> float:
    return h097mod.predict_candidate_delta(move_flat, cell, h098_fit)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    x = np.asarray(a, dtype=np.float64).reshape(-1)
    y = np.asarray(b, dtype=np.float64).reshape(-1)
    return float(np.dot(x, y) / (np.linalg.norm(x) * np.linalg.norm(y) + 1.0e-12))


def dict_get(items: tuple[tuple[str, int], ...], key: str) -> int:
    return dict(items).get(key, 0)


def dict_add(items: tuple[tuple[str, int], ...], key: str, inc: int = 1) -> tuple[tuple[str, int], ...]:
    d = dict(items)
    d[key] = d.get(key, 0) + inc
    return tuple(sorted(d.items()))


def initial_state(shape: tuple[int, int]) -> BeamState:
    return BeamState(
        selected=tuple(),
        move_mat=np.zeros(shape, dtype=np.float64),
        rows=frozenset(),
        subjects=tuple(),
        targets=tuple(),
        q2_count=0,
        cell_count=0,
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


def candidate_specs() -> list[H113Spec]:
    return [
        H113Spec(
            name="rowroute_h112_core_c48_a058",
            group="h112_core",
            max_cells=48,
            max_rows=22,
            max_per_subject=8,
            max_per_target=16,
            q2_cap=0,
            amp=0.58,
            cap=0.24,
            bundle_top=96,
            beam_width=72,
            min_bundle_score=0.34,
            min_bundle_targets=2,
            max_bundle_targets=4,
            min_gap=-0.08,
            max_residual_toxicity=0.64,
            min_residual_safety=0.36,
            max_bad_weighted_pos=0.006,
            max_bad_max_pos=0.034,
            max_h088_cos=-0.002,
            min_good_margin=0.010,
            route_pred_cap=0.000120,
            h098_pred_cap=0.000090,
            min_score=0.20,
            worldview="H112 was right locally, but only rows where multiple H112 cells form one route are action-grade",
        ),
        H113Spec(
            name="rowroute_antidote_objective_c72_a052",
            group="antidote_objective",
            max_cells=72,
            max_rows=28,
            max_per_subject=9,
            max_per_target=22,
            q2_cap=0,
            amp=0.52,
            cap=0.22,
            bundle_top=130,
            beam_width=88,
            min_bundle_score=0.28,
            min_bundle_targets=2,
            max_bundle_targets=5,
            min_gap=-0.14,
            max_residual_toxicity=0.68,
            min_residual_safety=0.32,
            max_bad_weighted_pos=0.010,
            max_bad_max_pos=0.048,
            max_h088_cos=-0.001,
            min_good_margin=0.006,
            route_pred_cap=0.000160,
            h098_pred_cap=0.000100,
            min_score=0.16,
            worldview="public punishes isolated objective-stage corrections, but Q3/S antidote routes survive as row-level assignments",
        ),
        H113Spec(
            name="rowroute_h108_rejected_bridge_c64_a050",
            group="h108_rejected_bridge",
            max_cells=64,
            max_rows=26,
            max_per_subject=9,
            max_per_target=20,
            q2_cap=0,
            amp=0.50,
            cap=0.21,
            bundle_top=118,
            beam_width=84,
            min_bundle_score=0.30,
            min_bundle_targets=2,
            max_bundle_targets=5,
            min_gap=-0.16,
            max_residual_toxicity=0.68,
            min_residual_safety=0.31,
            max_bad_weighted_pos=0.011,
            max_bad_max_pos=0.050,
            max_h088_cos=0.000,
            min_good_margin=0.005,
            route_pred_cap=0.000170,
            h098_pred_cap=0.000105,
            min_score=0.15,
            worldview="H108-rejected cells were not toxic alone; they need the correct row companions to become public-safe",
        ),
        H113Spec(
            name="rowroute_quality_stage_c60_a055",
            group="quality_stage",
            max_cells=60,
            max_rows=25,
            max_per_subject=9,
            max_per_target=18,
            q2_cap=0,
            amp=0.55,
            cap=0.23,
            bundle_top=118,
            beam_width=84,
            min_bundle_score=0.30,
            min_bundle_targets=2,
            max_bundle_targets=4,
            min_gap=-0.12,
            max_residual_toxicity=0.67,
            min_residual_safety=0.32,
            max_bad_weighted_pos=0.010,
            max_bad_max_pos=0.048,
            max_h088_cos=-0.001,
            min_good_margin=0.006,
            route_pred_cap=0.000160,
            h098_pred_cap=0.000100,
            min_score=0.15,
            worldview="the hidden state is a Q1/Q3 plus selected S quality-stage route, not an S-only objective route",
        ),
        H113Spec(
            name="rowroute_global_state_c92_a042",
            group="global_state",
            max_cells=92,
            max_rows=36,
            max_per_subject=10,
            max_per_target=28,
            q2_cap=2,
            amp=0.42,
            cap=0.18,
            bundle_top=170,
            beam_width=96,
            min_bundle_score=0.24,
            min_bundle_targets=2,
            max_bundle_targets=5,
            min_gap=-0.20,
            max_residual_toxicity=0.70,
            min_residual_safety=0.28,
            max_bad_weighted_pos=0.014,
            max_bad_max_pos=0.066,
            max_h088_cos=0.000,
            min_good_margin=0.002,
            route_pred_cap=0.000220,
            h098_pred_cap=0.000115,
            min_score=0.12,
            worldview="safe assignment is a broad low-amplitude row-state vector, not a sparse cell kernel",
        ),
        H113Spec(
            name="rowroute_q2_companion_micro_c24_a035",
            group="q2_companion",
            max_cells=24,
            max_rows=12,
            max_per_subject=5,
            max_per_target=12,
            q2_cap=12,
            amp=0.35,
            cap=0.15,
            bundle_top=80,
            beam_width=64,
            min_bundle_score=0.20,
            min_bundle_targets=2,
            max_bundle_targets=3,
            min_gap=-0.24,
            max_residual_toxicity=0.72,
            min_residual_safety=0.25,
            max_bad_weighted_pos=0.008,
            max_bad_max_pos=0.040,
            max_h088_cos=-0.001,
            min_good_margin=0.004,
            route_pred_cap=0.000260,
            h098_pred_cap=0.000110,
            min_score=0.08,
            worldview="Q2 is not safe as a target action, but a tiny Q2+quality companion route may explain the intervention state",
        ),
    ]


def mark_h112_selected(pool: pd.DataFrame) -> pd.DataFrame:
    out = pool.copy()
    selected_path = HITL / "h112_public_residual_toxicity_solver_hsjepa" / "h112_selected_cells.csv"
    decision_path = HITL / "h112_public_residual_toxicity_solver_hsjepa" / "h112_decision.csv"
    selected: set[int] = set()
    if selected_path.exists() and decision_path.exists():
        decision = pd.read_csv(decision_path).iloc[0]
        cid = str(decision["selected_candidate_id"])
        selected_df = pd.read_csv(selected_path)
        selected = set(selected_df[selected_df["candidate_id"].astype(str).eq(cid)]["flat_index"].astype(int))
    out["h113_in_h112_selected"] = out["flat_index"].astype(int).isin(selected).astype(float)
    return out


def prepare_pool() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, np.ndarray, h097mod.ResponseFit, h100mod.RouteBasisFit, pd.DataFrame, np.ndarray, pd.DataFrame, np.ndarray]:
    base = h085mod.load_sub(BASE_FILE)
    sample = base[KEYS].copy()
    base_prob = base[TARGETS].to_numpy(dtype=np.float64)
    cell, h098_fit, route_fit, basis_fit_df, basis_fit_moves, bad_axes, bad_moves, _good_axes, good_moves = h109mod.build_context()
    public = h097mod.load_public_moves(sample, base_prob)
    residuals = h112mod.load_h098_selected_residuals(public)
    pool = h112mod.annotate_residual_toxicity(h111mod.load_boundary_pool(), public, residuals)
    pool = mark_h112_selected(pool)
    return pool, public, sample, base, base_prob, h098_fit, route_fit, basis_fit_df, basis_fit_moves, bad_axes, bad_moves, good_moves


def template_mask(group: pd.DataFrame, spec: H113Spec, template: str) -> np.ndarray:
    target = group["target"].astype(str)
    score = group["h112_assignment_score"].to_numpy(dtype=np.float64)
    gap = group["h112_residual_gap"].to_numpy(dtype=np.float64)
    safety = group["h112_residual_safety"].to_numpy(dtype=np.float64)
    tox = group["h112_residual_toxicity"].to_numpy(dtype=np.float64)
    antidote = group["h112_antidote_score"].to_numpy(dtype=np.float64)
    h112_sel = group["h113_in_h112_selected"].to_numpy(dtype=np.float64) > 0
    h111_sel = group["h112_in_h111_selected"].to_numpy(dtype=np.float64) > 0
    h108_rej = group["h111_h108_rejected"].to_numpy(dtype=np.float64) > 0
    base = (
        (score >= spec.min_score)
        & (gap >= spec.min_gap)
        & (safety >= spec.min_residual_safety)
        & (tox <= spec.max_residual_toxicity)
        & (np.abs(group["h112_candidate_raw_move"].to_numpy(dtype=np.float64)) > 1.0e-10)
    )
    if template == "h112_core":
        return base & h112_sel & target.ne("Q2").to_numpy()
    if template == "h111_core":
        return base & h111_sel & target.ne("Q2").to_numpy()
    if template == "objective_antidote":
        return base & target.isin(["Q3", "S1", "S2", "S3", "S4"]).to_numpy() & (antidote >= 0.46)
    if template == "stage_antidote":
        return base & target.isin(["S1", "S2", "S3", "S4"]).to_numpy() & (antidote >= 0.42)
    if template == "quality_stage":
        return base & target.isin(["Q1", "Q3", "S1", "S3", "S4"]).to_numpy()
    if template == "h108_rejected_bridge":
        row_has_rejected = bool(h108_rej.any())
        return base & row_has_rejected & target.ne("Q2").to_numpy() & (h108_rej | h111_sel | (antidote >= 0.42))
    if template == "global_state":
        return base & target.ne("Q2").to_numpy()
    if template == "q2_companion":
        row_has_q2 = bool((base & target.eq("Q2").to_numpy()).any())
        return base & row_has_q2 & (target.isin(["Q1", "Q2", "Q3", "S1", "S3"]).to_numpy())
    raise ValueError(template)


def templates_for_spec(spec: H113Spec) -> list[str]:
    if spec.group == "h112_core":
        return ["h112_core", "h111_core", "quality_stage"]
    if spec.group == "antidote_objective":
        return ["objective_antidote", "stage_antidote", "quality_stage"]
    if spec.group == "h108_rejected_bridge":
        return ["h108_rejected_bridge", "objective_antidote"]
    if spec.group == "quality_stage":
        return ["quality_stage", "h112_core", "objective_antidote"]
    if spec.group == "global_state":
        return ["global_state", "objective_antidote", "quality_stage"]
    if spec.group == "q2_companion":
        return ["q2_companion"]
    raise ValueError(spec.group)


def route_bonus(targets: tuple[str, ...], template: str) -> float:
    tset = set(targets)
    bonus = 0.0
    if "Q2" not in tset:
        bonus += 0.04
    if "Q3" in tset and any(t in tset for t in ["S1", "S2", "S3", "S4"]):
        bonus += 0.10
    if any(t in tset for t in ["Q1", "Q3"]) and any(t in tset for t in ["S1", "S3", "S4"]):
        bonus += 0.08
    if len(tset & {"S1", "S2", "S3", "S4"}) >= 2:
        bonus += 0.05
    if "Q2" in tset:
        bonus -= 0.14
    if template in {"h112_core", "h108_rejected_bridge"}:
        bonus += 0.05
    return bonus


def build_row_bundles(pool: pd.DataFrame, spec: H113Spec) -> list[RowBundle]:
    bundles: list[RowBundle] = []
    for row, group in pool.groupby("row", sort=False):
        group = group.sort_values(["h112_assignment_score", "h112_residual_gap"], ascending=[False, False]).copy()
        for template in templates_for_spec(spec):
            mask = template_mask(group, spec, template)
            sub = group[mask].copy()
            if sub.empty:
                continue
            sub = sub.sort_values(["h112_assignment_score", "h112_antidote_score", "h112_residual_gap"], ascending=[False, False, False])
            sub = sub.head(spec.max_bundle_targets).copy()
            if len(sub) < spec.min_bundle_targets:
                continue
            targets = tuple(sub["target"].astype(str).to_list())
            if len(set(targets)) != len(targets):
                continue
            tox = float(sub["h112_residual_toxicity"].mean())
            safety = float(sub["h112_residual_safety"].mean())
            gap = float(sub["h112_residual_gap"].mean())
            antidote = float(sub["h112_antidote_score"].mean())
            family = float(sub["h110_family_count"].mean())
            h111_rate = float(sub["h112_in_h111_selected"].mean())
            h112_rate = float(sub["h113_in_h112_selected"].mean())
            h108_rate = float(sub["h111_h108_rejected"].mean())
            h109_rate = float(sub["h111_in_h109"].mean())
            raw = sub["h112_candidate_raw_move"].to_numpy(dtype=np.float64)
            sign_coherence = float(abs(np.sum(raw)) / (np.sum(np.abs(raw)) + 1.0e-12))
            score = (
                0.34 * float(sub["h112_assignment_score"].mean())
                + 0.20 * safety
                + 0.18 * gap
                + 0.13 * antidote
                + 0.09 * h111_rate
                + 0.07 * h112_rate
                + 0.05 * h108_rate
                + 0.04 * h109_rate
                + route_bonus(targets, template)
                + 0.025 * min(len(sub), 5)
                - 0.24 * tox
                - 0.04 * sign_coherence
            )
            if score < spec.min_bundle_score:
                continue
            moves = tuple(np.clip(raw * spec.amp, -spec.cap, spec.cap).astype(float))
            bundle_id = safe_id(f"r{int(row):03d}_{template}_{'_'.join(targets)}", 96)
            bundles.append(
                RowBundle(
                    bundle_id=bundle_id,
                    row=int(row),
                    subject_id=str(sub["subject_id"].iloc[0]),
                    template=template,
                    targets=targets,
                    flat_indices=tuple(sub["flat_index"].astype(int).to_list()),
                    target_indices=tuple(sub["target_index"].astype(int).to_list()),
                    moves=moves,
                    score=float(score),
                    residual_toxicity=tox,
                    residual_safety=safety,
                    residual_gap=gap,
                    antidote_score=antidote,
                    h111_rate=h111_rate,
                    h108_rejected_rate=h108_rate,
                    h109_rate=h109_rate,
                    family_count=family,
                )
            )
    bundles = sorted(bundles, key=lambda b: b.score, reverse=True)
    dedup: dict[tuple[int, str, tuple[str, ...]], RowBundle] = {}
    for bundle in bundles:
        key = (bundle.row, bundle.template, bundle.targets)
        if key not in dedup:
            dedup[key] = bundle
    return sorted(dedup.values(), key=lambda b: b.score, reverse=True)[: spec.bundle_top]


def state_rank_score(state: BeamState) -> float:
    return (
        state.score
        + 0.012 * state.cell_count
        + 0.030 * len(state.selected)
        + 0.18 * max(state.axis["h102_cum_good_bad_margin"], 0.0)
        + 0.06 * max(-state.axis["h102_cum_h088_axis_cos"], 0.0)
        - 0.55 * max(state.axis["h102_cum_bad_weighted_pos"], 0.0)
        - 0.30 * max(state.axis["h102_cum_bad_max_pos"], 0.0)
        - 0.22 * max(state.axis["h102_cum_h088_axis_cos"], 0.0)
    )


def target_counts_after(state: BeamState, bundle: RowBundle) -> tuple[tuple[str, int], ...]:
    items = state.targets
    for target in bundle.targets:
        items = dict_add(items, target, 1)
    return items


def select_bundles(
    pool: pd.DataFrame,
    spec: H113Spec,
    shape: tuple[int, int],
    bad_axes: pd.DataFrame,
    bad_moves: np.ndarray,
    good_moves: np.ndarray,
) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray, dict[str, float]]:
    bundles = build_row_bundles(pool, spec)
    states = [initial_state(shape)]
    for idx, bundle in enumerate(bundles):
        next_states = states.copy()
        for state in states:
            if bundle.row in state.rows:
                continue
            if len(state.rows) >= spec.max_rows:
                continue
            if state.cell_count + len(bundle.flat_indices) > spec.max_cells:
                continue
            if dict_get(state.subjects, bundle.subject_id) + 1 > spec.max_per_subject:
                continue
            new_targets = target_counts_after(state, bundle)
            if any(count > spec.max_per_target for _target, count in new_targets):
                continue
            new_q2 = state.q2_count + sum(1 for target in bundle.targets if target == "Q2")
            if new_q2 > spec.q2_cap:
                continue
            tmp = state.move_mat.copy()
            for tidx, move in zip(bundle.target_indices, bundle.moves):
                tmp[bundle.row, tidx] = float(move)
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
                bundle.score
                + 0.08 * bundle.residual_safety
                + 0.05 * bundle.antidote_score
                + 0.04 * bundle.h108_rejected_rate
                + 0.015 * len(bundle.targets)
                - 0.08 * bundle.residual_toxicity
            )
            next_states.append(
                BeamState(
                    selected=state.selected + (idx,),
                    move_mat=tmp,
                    rows=state.rows | {bundle.row},
                    subjects=dict_add(state.subjects, bundle.subject_id, 1),
                    targets=new_targets,
                    q2_count=new_q2,
                    cell_count=state.cell_count + len(bundle.flat_indices),
                    score=state.score + bonus,
                    axis=axis,
                )
            )
        states = sorted(next_states, key=state_rank_score, reverse=True)[: spec.beam_width]
    final = [s for s in states if s.selected]
    if not final:
        empty_axis = initial_state(shape).axis
        return pd.DataFrame(), pd.DataFrame(), np.zeros(shape, dtype=np.float64), empty_axis
    best = sorted(final, key=state_rank_score, reverse=True)[0]
    selected_bundles = [bundles[i] for i in best.selected]
    bundle_rows = pd.DataFrame([bundle.__dict__ for bundle in selected_bundles])
    selected_flat = [flat for bundle in selected_bundles for flat in bundle.flat_indices]
    bundle_map = {flat: bundle for bundle in selected_bundles for flat in bundle.flat_indices}
    selected_cells = pool[pool["flat_index"].astype(int).isin(selected_flat)].copy()
    selected_cells["h113_bundle_id"] = selected_cells["flat_index"].astype(int).map(lambda flat: bundle_map[int(flat)].bundle_id)
    selected_cells["h113_bundle_template"] = selected_cells["flat_index"].astype(int).map(lambda flat: bundle_map[int(flat)].template)
    selected_cells["h113_bundle_score"] = selected_cells["flat_index"].astype(int).map(lambda flat: bundle_map[int(flat)].score)
    selected_cells["h112_move"] = [
        best.move_mat[int(row), int(tidx)]
        for row, tidx in zip(selected_cells["row"].astype(int), selected_cells["target_index"].astype(int))
    ]
    selected_cells["h097_move_col"] = "h112_move"
    selected_cells = selected_cells.sort_values(["row", "target_index"]).reset_index(drop=True)
    return selected_cells, bundle_rows, best.move_mat, best.axis


def load_previous_move(sample: pd.DataFrame, base_prob: np.ndarray, pattern: str) -> np.ndarray | None:
    matches = sorted(ROOT.glob(pattern))
    if not matches:
        return None
    prob = h085mod.load_sub(matches[-1], sample)[TARGETS].to_numpy(dtype=np.float64)
    return logit(prob).reshape(-1) - logit(base_prob).reshape(-1)


def overlap_count(move_a: np.ndarray, move_b: np.ndarray | None) -> int:
    if move_b is None:
        return 0
    return int(((np.abs(move_a.reshape(-1)) > 1.0e-12) & (np.abs(move_b.reshape(-1)) > 1.0e-12)).sum())


def evaluate_candidate(
    candidate_id: str,
    prob: np.ndarray,
    move_mat: np.ndarray,
    selected_cells: pd.DataFrame,
    selected_bundles: pd.DataFrame,
    cell: pd.DataFrame,
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    h098_fit: h097mod.ResponseFit,
    route_fit: h100mod.RouteBasisFit,
    basis_fit_df: pd.DataFrame,
    basis_fit_moves: np.ndarray,
    spec: H113Spec,
    path: Path,
    axis: dict[str, float],
    previous: dict[str, np.ndarray | None],
) -> dict[str, object]:
    proxy = h112mod.H112Spec(
        name=spec.name,
        group=spec.group,
        max_cells=spec.max_cells,
        max_rows=spec.max_rows,
        max_per_subject=spec.max_per_subject,
        max_per_target=spec.max_per_target,
        q2_cap=spec.q2_cap,
        amp=spec.amp,
        cap=spec.cap,
        pool_top=spec.bundle_top,
        beam_width=spec.beam_width,
        min_score=spec.min_score,
        min_gap=spec.min_gap,
        max_residual_toxicity=spec.max_residual_toxicity,
        min_residual_safety=spec.min_residual_safety,
        min_family_count=2,
        max_bad_weighted_pos=spec.max_bad_weighted_pos,
        max_bad_max_pos=spec.max_bad_max_pos,
        max_h088_cos=spec.max_h088_cos,
        min_good_margin=spec.min_good_margin,
        route_pred_cap=spec.route_pred_cap,
        h098_pred_cap=spec.h098_pred_cap,
        worldview=spec.worldview,
    )
    out = h112mod.evaluate_candidate(
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
        proxy,
        path,
        axis,
    )
    move_flat = move_mat.reshape(-1)
    out["h113_bundle_count"] = int(len(selected_bundles))
    out["h113_mean_targets_per_bundle"] = float(len(selected_cells) / max(len(selected_bundles), 1))
    out["h113_unique_templates"] = int(selected_bundles["template"].nunique()) if len(selected_bundles) else 0
    out["h113_mean_bundle_score"] = float(selected_bundles["score"].mean()) if len(selected_bundles) else 0.0
    out["h113_mean_bundle_gap"] = float(selected_bundles["residual_gap"].mean()) if len(selected_bundles) else 0.0
    out["h113_bundle_h108_rejected_rate"] = float(selected_bundles["h108_rejected_rate"].mean()) if len(selected_bundles) else 0.0
    for label, prev in previous.items():
        out[f"h113_{label}_overlap_cells"] = overlap_count(move_flat, prev)
        out[f"h113_{label}_cosine"] = cosine(move_flat, prev) if prev is not None else 0.0
    h112_cos = float(out.get("h113_h112_cosine", 0.0))
    novelty = max(0.0, min(1.0, 1.0 - abs(h112_cos)))
    route_info = min(float(out["h113_bundle_count"]) / 16.0, 1.0) * min(float(out["h113_mean_targets_per_bundle"]) / 3.0, 1.0)
    out["h113_route_information"] = route_info
    out["h113_novelty_vs_h112"] = novelty
    out["h113_score"] = (
        100.0 * (-float(out["model_pred_delta_vs_h057"]))
        + 110.0 * (-float(out["route_basis_pred_delta_vs_h057"]))
        + 0.18 * float(out["selected_mean_residual_gap"])
        + 0.16 * float(out["selected_mean_residual_safety"])
        + 0.14 * float(out["selected_mean_antidote_score"])
        + 0.13 * route_info
        + 0.08 * min(float(out["h113_unique_templates"]) / 3.0, 1.0)
        + 0.06 * novelty
        + 0.04 * max(-float(out["h102_cum_h088_axis_cos"]), 0.0)
        - 0.20 * float(out["selected_mean_residual_toxicity"])
        - 0.55 * max(float(out["h102_cum_bad_weighted_pos"]), 0.0)
        - 0.28 * max(float(out["h102_cum_bad_max_pos"]), 0.0)
        - 0.14 * max(float(out["h102_cum_h088_axis_cos"]), 0.0)
        - 18.0 * max(float(out["hard_diag_delta_vs_h057"]), 0.0)
    )
    return out


def run() -> None:
    cleanup_previous_outputs()
    pool, public, sample, base, base_prob, h098_fit, route_fit, basis_fit_df, basis_fit_moves, bad_axes, bad_moves, good_moves = prepare_pool()
    cell = h109mod.build_context()[0]
    previous = {
        "h112": load_previous_move(sample, base_prob, "submission_h112_residualtox_*_uploadsafe.csv"),
        "h111": load_previous_move(sample, base_prob, "submission_h111_boundary_*_uploadsafe.csv"),
        "h110": load_previous_move(sample, base_prob, "submission_h110_toxgap_*_uploadsafe.csv"),
        "h108": load_previous_move(sample, base_prob, "submission_h108_decoder_jury_*_uploadsafe.csv"),
    }

    bundle_audit_rows = []
    candidate_rows = []
    selected_cell_frames = []
    selected_bundle_frames = []
    all_bundle_frames = []

    for spec in candidate_specs():
        bundles = build_row_bundles(pool, spec)
        bundle_audit_rows.append(
            {
                "spec_name": spec.name,
                "group": spec.group,
                "candidate_bundles": int(len(bundles)),
                "top_bundle_score": float(bundles[0].score) if bundles else 0.0,
                "mean_bundle_score_top20": float(np.mean([b.score for b in bundles[:20]])) if bundles else 0.0,
                "worldview": spec.worldview,
            }
        )
        if bundles:
            all_bundle_frames.append(pd.DataFrame([b.__dict__ for b in bundles]).assign(spec_name=spec.name))
        selected_cells, selected_bundles, move_mat, axis = select_bundles(pool, spec, base_prob.shape, bad_axes, bad_moves, good_moves)
        if selected_cells.empty:
            continue
        rpred = route_pred(move_mat.reshape(-1), basis_fit_df, basis_fit_moves, route_fit)
        cpred = h098_pred(move_mat.reshape(-1), cell, h098_fit)
        if rpred > spec.route_pred_cap or cpred > spec.h098_pred_cap:
            continue
        prob = materialize(base_prob, move_mat)
        if int((np.abs(prob - base_prob) > TOL).sum()) == 0:
            continue
        hash_id = short_hash(prob)
        candidate_id = safe_id(f"h113_{spec.name}_{hash_id}", 128)
        path = OUT / f"submission_{candidate_id}.csv"
        h085mod.write_submission(sample, prob, path)
        metrics = evaluate_candidate(
            candidate_id,
            prob,
            move_mat,
            selected_cells,
            selected_bundles,
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
            previous,
        )
        candidate_rows.append(metrics)
        selected_cells = selected_cells.copy()
        selected_cells.insert(0, "candidate_id", candidate_id)
        selected_cell_frames.append(selected_cells)
        selected_bundles = selected_bundles.copy()
        selected_bundles.insert(0, "candidate_id", candidate_id)
        selected_bundle_frames.append(selected_bundles)

    candidates = pd.DataFrame(candidate_rows)
    if candidates.empty:
        raise RuntimeError("no H113 candidates")
    candidates = candidates.sort_values(["h113_score", "route_basis_pred_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True)
    selected = candidates.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"submission_h113_rowroute_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)

    bundle_audit = pd.DataFrame(bundle_audit_rows)
    decision = {
        "decision": "promote_h113_row_route_equation_solver",
        "selected_candidate_id": selected["candidate_id"],
        "root_uploadsafe_path": str(root_path.resolve()),
        "known_public_observations": int(len(public)),
        "worldview": selected["worldview"],
        **selected,
        **{f"root_{key}": value for key, value in validation.items()},
    }

    pool.to_csv(OUT / "h113_row_route_pool.csv", index=False)
    bundle_audit.to_csv(OUT / "h113_bundle_audit.csv", index=False)
    if all_bundle_frames:
        pd.concat(all_bundle_frames, ignore_index=True).to_csv(OUT / "h113_all_bundles.csv", index=False)
    candidates.to_csv(OUT / "h113_candidates.csv", index=False)
    pd.concat(selected_cell_frames, ignore_index=True).to_csv(OUT / "h113_selected_cells.csv", index=False)
    pd.concat(selected_bundle_frames, ignore_index=True).to_csv(OUT / "h113_selected_bundles.csv", index=False)
    pd.DataFrame([decision]).to_csv(OUT / "h113_decision.csv", index=False)

    cols = [
        "candidate_id",
        "spec_name",
        "selected_cells",
        "changed_rows_vs_h057",
        "h113_bundle_count",
        "h113_mean_targets_per_bundle",
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
        "selected_mean_residual_toxicity",
        "selected_mean_residual_safety",
        "selected_mean_residual_gap",
        "selected_h111_cells",
        "selected_h108_rejected_cells",
        "h113_h112_overlap_cells",
        "h113_h112_cosine",
        "h113_route_information",
        "h113_novelty_vs_h112",
        "h113_score",
        "file",
    ]
    report = f"""# H113 Row-Route Equation Solver HS-JEPA

Question: is the public/private action decoder a row-target assignment equation
rather than a local cell toxicity filter?

Bundle audit:

{md_table(bundle_audit, 20)}

Candidates:

{md_table(candidates[cols], 20)}

Decision:

{md_table(pd.DataFrame([decision]), 1)}

Interpretation rule:

- If H113 improves over H112/H111, H112's cell-level residual toxicity was only
  a projection of a row-route equation.  HS-JEPA needs row-target route
  assignment as the action decoder.
- If H112 wins, the route-bundle layer is an attractive but false abstraction;
  public safety is closer to individual residual-toxic cells.
- If H111 wins, residual toxicity is over-pruning and the global boundary field
  remains the stronger equation.
- If H088-like failures appear again, the bundle solver still cannot separate
  private action-tail from public action-toxicity.
"""
    (OUT / "h113_report.md").write_text(report, encoding="utf-8")

    print("H113 selected candidate")
    print(candidates[cols].head(10).to_string(index=False))
    print("\nDecision")
    print(pd.DataFrame([decision])[["decision", "selected_candidate_id", "root_uploadsafe_path", "root_upload_safe"]].to_string(index=False))


if __name__ == "__main__":
    run()
