#!/usr/bin/env python3
"""H114: toxic-subspace null solver HS-JEPA.

H112 and H113 still start from locally plausible cells and then ask whether the
chosen action is safe.  H114 reverses the order:

    known bad public actions -> toxic subspace
    candidate human-state action -> projection into the toxic nullspace
    nullspace action -> sparse row-target assignment

If the public/private equation really punishes a latent action-toxicity field,
the safe action should not merely avoid a few bad axes after selection.  It
should live in the nullspace of the toxic public subspace before assignment.
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
OUT = HITL / "h114_toxic_subspace_null_solver_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H112_PATH = HITL / "h112_public_residual_toxicity_solver_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h112mod", H112_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H112_PATH}")
h112mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h112mod
SPEC.loader.exec_module(h112mod)

h111mod = h112mod.h111mod
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
class H114Spec:
    name: str
    group: str
    toxic_mode: str
    prior_mode: str
    max_cells: int
    max_rows: int
    max_per_subject: int
    max_per_target: int
    q2_cap: int
    amp: float
    cap: float
    pool_top: int
    bad_penalty: float
    good_push: float
    ridge: float
    min_abs_move: float
    min_score: float
    max_residual_toxicity: float
    min_residual_safety: float
    max_bad_weighted_pos: float
    max_bad_max_pos: float
    max_h088_cos: float
    min_good_margin: float
    route_pred_cap: float
    h098_pred_cap: float
    worldview: str


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
    for path in OUT.glob("submission_h114_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h114_nullspace_*.csv"):
        path.unlink()


def materialize(base_prob: np.ndarray, move_mat: np.ndarray) -> np.ndarray:
    return clip_prob(sigmoid(logit(base_prob) + move_mat))


def route_pred(move_flat: np.ndarray, basis_fit_df: pd.DataFrame, basis_fit_moves: np.ndarray, route_fit: h100mod.RouteBasisFit) -> float:
    return h100mod.predict_candidate_delta(move_flat, basis_fit_df, basis_fit_moves, route_fit)


def h098_pred(move_flat: np.ndarray, cell: pd.DataFrame, h098_fit: h097mod.ResponseFit) -> float:
    return h097mod.predict_candidate_delta(move_flat, cell, h098_fit)


def cosine(a: np.ndarray | None, b: np.ndarray | None) -> float:
    if a is None or b is None:
        return 0.0
    x = np.asarray(a, dtype=np.float64).reshape(-1)
    y = np.asarray(b, dtype=np.float64).reshape(-1)
    return float(np.dot(x, y) / (np.linalg.norm(x) * np.linalg.norm(y) + 1.0e-12))


def overlap_count(a: np.ndarray, b: np.ndarray | None) -> int:
    if b is None:
        return 0
    return int(((np.abs(a.reshape(-1)) > 1.0e-12) & (np.abs(b.reshape(-1)) > 1.0e-12)).sum())


def load_previous_move(sample: pd.DataFrame, base_prob: np.ndarray, pattern: str) -> np.ndarray | None:
    matches = sorted(ROOT.glob(pattern))
    if not matches:
        return None
    prob = h085mod.load_sub(matches[-1], sample)[TARGETS].to_numpy(dtype=np.float64)
    return logit(prob).reshape(-1) - logit(base_prob).reshape(-1)


def candidate_specs() -> list[H114Spec]:
    return [
        H114Spec(
            name="null_residual_h112_core_c58_a072",
            group="h112_core",
            toxic_mode="residual_bad_plus_h102",
            prior_mode="h112_safe",
            max_cells=58,
            max_rows=26,
            max_per_subject=10,
            max_per_target=18,
            q2_cap=0,
            amp=0.72,
            cap=0.26,
            pool_top=150,
            bad_penalty=7.0,
            good_push=0.34,
            ridge=0.09,
            min_abs_move=0.015,
            min_score=0.22,
            max_residual_toxicity=0.66,
            min_residual_safety=0.34,
            max_bad_weighted_pos=0.006,
            max_bad_max_pos=0.034,
            max_h088_cos=-0.004,
            min_good_margin=0.010,
            route_pred_cap=0.000120,
            h098_pred_cap=0.000090,
            worldview="safe action is H112's residual-safe core after projecting away residual-bad and public-bad toxic subspace",
        ),
        H114Spec(
            name="null_publicbad_broad_c96_a052",
            group="broad_nonq2",
            toxic_mode="public_bad_h102",
            prior_mode="h111_boundary",
            max_cells=96,
            max_rows=46,
            max_per_subject=11,
            max_per_target=28,
            q2_cap=0,
            amp=0.52,
            cap=0.20,
            pool_top=230,
            bad_penalty=9.0,
            good_push=0.24,
            ridge=0.10,
            min_abs_move=0.010,
            min_score=0.14,
            max_residual_toxicity=0.70,
            min_residual_safety=0.28,
            max_bad_weighted_pos=0.010,
            max_bad_max_pos=0.050,
            max_h088_cos=-0.002,
            min_good_margin=0.006,
            route_pred_cap=0.000180,
            h098_pred_cap=0.000105,
            worldview="a broad H111-like state can survive only after explicit projection out of all known public-bad axes",
        ),
        H114Spec(
            name="null_h010_e216_antidote_c72_a060",
            group="residual_antidote",
            toxic_mode="h010_e216_lejepa",
            prior_mode="antidote",
            max_cells=72,
            max_rows=34,
            max_per_subject=10,
            max_per_target=22,
            q2_cap=0,
            amp=0.60,
            cap=0.23,
            pool_top=180,
            bad_penalty=8.0,
            good_push=0.42,
            ridge=0.08,
            min_abs_move=0.012,
            min_score=0.18,
            max_residual_toxicity=0.68,
            min_residual_safety=0.30,
            max_bad_weighted_pos=0.008,
            max_bad_max_pos=0.044,
            max_h088_cos=-0.003,
            min_good_margin=0.008,
            route_pred_cap=0.000160,
            h098_pred_cap=0.000100,
            worldview="H010/E216/LeJEPA residual-bad directions define the true toxic subspace; the safe action is their antidote-null component",
        ),
        H114Spec(
            name="null_novel_lowoverlap_c64_a058",
            group="novel_nonq2",
            toxic_mode="residual_bad_plus_h102",
            prior_mode="novel_safe",
            max_cells=64,
            max_rows=36,
            max_per_subject=9,
            max_per_target=20,
            q2_cap=0,
            amp=0.58,
            cap=0.22,
            pool_top=210,
            bad_penalty=10.0,
            good_push=0.18,
            ridge=0.12,
            min_abs_move=0.010,
            min_score=0.12,
            max_residual_toxicity=0.70,
            min_residual_safety=0.26,
            max_bad_weighted_pos=0.008,
            max_bad_max_pos=0.046,
            max_h088_cos=-0.004,
            min_good_margin=0.006,
            route_pred_cap=0.000180,
            h098_pred_cap=0.105e-3,
            worldview="H112 may be too close to the frontier; force a lower-overlap safe nullspace action to test whether hidden toxicity explains the plateau",
        ),
        H114Spec(
            name="null_q2_companion_micro_c26_a032",
            group="q2_companion",
            toxic_mode="residual_bad_plus_h102",
            prior_mode="q2_companion",
            max_cells=26,
            max_rows=16,
            max_per_subject=6,
            max_per_target=14,
            q2_cap=10,
            amp=0.32,
            cap=0.14,
            pool_top=100,
            bad_penalty=12.0,
            good_push=0.20,
            ridge=0.14,
            min_abs_move=0.006,
            min_score=0.04,
            max_residual_toxicity=0.74,
            min_residual_safety=0.22,
            max_bad_weighted_pos=0.006,
            max_bad_max_pos=0.036,
            max_h088_cos=-0.002,
            min_good_margin=0.004,
            route_pred_cap=0.000260,
            h098_pred_cap=0.000110,
            worldview="Q2 can re-enter only as a tiny companion action inside the toxic nullspace",
        ),
    ]


def prepare_context() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, np.ndarray, pd.DataFrame, h097mod.ResponseFit, h100mod.RouteBasisFit, pd.DataFrame, np.ndarray, pd.DataFrame, np.ndarray, pd.DataFrame, pd.DataFrame]:
    base = h085mod.load_sub(BASE_FILE)
    sample = base[KEYS].copy()
    base_prob = base[TARGETS].to_numpy(dtype=np.float64)
    cell, h098_fit, route_fit, basis_fit_df, basis_fit_moves, bad_axes, bad_moves, _good_axes, good_moves = h109mod.build_context()
    public = h097mod.load_public_moves(sample, base_prob)
    residuals = h112mod.load_h098_selected_residuals(public)
    pool = h112mod.annotate_residual_toxicity(h111mod.load_boundary_pool(), public, residuals)
    return pool, public, sample, base_prob, cell, h098_fit, route_fit, basis_fit_df, basis_fit_moves, bad_axes, bad_moves, good_moves, residuals


def allowed_mask(pool: pd.DataFrame, spec: H114Spec) -> np.ndarray:
    target = pool["target"].astype(str)
    score = pool["h112_assignment_score"].to_numpy(dtype=np.float64)
    tox = pool["h112_residual_toxicity"].to_numpy(dtype=np.float64)
    safety = pool["h112_residual_safety"].to_numpy(dtype=np.float64)
    raw = pool["h112_candidate_raw_move"].to_numpy(dtype=np.float64)
    base = (
        (np.abs(raw) > 1.0e-10)
        & (score >= spec.min_score)
        & (tox <= spec.max_residual_toxicity)
        & (safety >= spec.min_residual_safety)
    )
    if spec.group == "h112_core":
        return base & target.ne("Q2").to_numpy() & (
            pool["h112_in_h111_selected"].to_numpy(dtype=np.float64).astype(bool)
            | pool["h111_in_h110"].to_numpy(dtype=np.float64).astype(bool)
        )
    if spec.group == "broad_nonq2":
        return base & target.ne("Q2").to_numpy()
    if spec.group == "residual_antidote":
        return base & target.ne("Q2").to_numpy() & (pool["h112_antidote_score"].to_numpy(dtype=np.float64) >= 0.42)
    if spec.group == "novel_nonq2":
        return base & target.ne("Q2").to_numpy() & (pool["h112_in_h111_selected"].to_numpy(dtype=np.float64) < 0.5)
    if spec.group == "q2_companion":
        return base & target.isin(["Q1", "Q2", "Q3", "S1", "S3"]).to_numpy()
    raise ValueError(spec.group)


def toxic_axis_matrix(
    spec: H114Spec,
    flat: np.ndarray,
    public: pd.DataFrame,
    residuals: pd.DataFrame,
    bad_moves: np.ndarray,
    bad_axes: pd.DataFrame,
) -> tuple[np.ndarray, pd.DataFrame]:
    rows: list[np.ndarray] = []
    meta: list[dict[str, object]] = []

    def add_axis(name: str, source: str, vec: np.ndarray, weight: float) -> None:
        sub = np.asarray(vec, dtype=np.float64).reshape(-1)[flat]
        norm = float(np.linalg.norm(sub))
        if norm <= 1.0e-12 or weight <= 0.0:
            return
        rows.append(np.sqrt(weight) * sub / norm)
        meta.append({"axis_name": name, "axis_source": source, "weight": float(weight), "restricted_norm": norm})

    merged = public.merge(residuals[["file", "residual_bad", "actual_minus_pred"]], on="file", how="left")
    for rec in merged.to_dict("records"):
        name = str(rec["file"])
        move = rec["move_logit"]
        delta = max(float(rec.get("delta_vs_h057", 0.0)), 0.0)
        residual_bad = max(float(rec.get("residual_bad", 0.0)), 0.0)
        if spec.toxic_mode in {"residual_bad_plus_h102", "h010_e216_lejepa"}:
            if spec.toxic_mode == "h010_e216_lejepa" and not any(tag in name.lower() for tag in ["h010", "e216", "lejepa"]):
                continue
            if residual_bad > 0.0:
                add_axis(name, "residual_bad", move, 1.0 + residual_bad / 0.0005)
        if spec.toxic_mode in {"public_bad_h102", "residual_bad_plus_h102"} and delta > 0.0:
            add_axis(name, "public_bad", move, 0.25 + delta / 0.001)

    if spec.toxic_mode in {"public_bad_h102", "residual_bad_plus_h102"}:
        for idx, rec in bad_axes.reset_index(drop=True).iterrows():
            add_axis(str(rec["axis_name"]), "h102_bad_axis", bad_moves[idx], float(rec["weight"]))

    if not rows:
        raise RuntimeError(f"no toxic axes for {spec.name}")
    return np.vstack(rows).astype(np.float64), pd.DataFrame(meta)


def good_axis_matrix(flat: np.ndarray, good_moves: np.ndarray) -> np.ndarray:
    rows = []
    for vec in good_moves:
        sub = np.asarray(vec, dtype=np.float64).reshape(-1)[flat]
        norm = float(np.linalg.norm(sub))
        if norm > 1.0e-12:
            rows.append(sub / norm)
    return np.vstack(rows).astype(np.float64) if rows else np.zeros((0, len(flat)), dtype=np.float64)


def prior_vector(work: pd.DataFrame, spec: H114Spec, good_axes: np.ndarray) -> np.ndarray:
    raw = work["h112_candidate_raw_move"].to_numpy(dtype=np.float64)
    assignment = work["h112_assignment_score"].to_numpy(dtype=np.float64)
    safety = work["h112_residual_safety"].to_numpy(dtype=np.float64)
    gap = work["h112_residual_gap"].to_numpy(dtype=np.float64)
    antidote = work["h112_antidote_score"].to_numpy(dtype=np.float64)
    if spec.prior_mode == "h112_safe":
        mult = 0.52 + 0.34 * rank01(assignment, high=True) + 0.18 * rank01(gap, high=True)
    elif spec.prior_mode == "h111_boundary":
        mult = 0.46 + 0.28 * work["h112_in_h111_selected"].to_numpy(dtype=np.float64) + 0.22 * rank01(assignment, high=True)
    elif spec.prior_mode == "antidote":
        mult = 0.48 + 0.40 * rank01(antidote, high=True) + 0.20 * rank01(safety, high=True)
    elif spec.prior_mode == "novel_safe":
        mult = 0.42 + 0.28 * rank01(safety, high=True) + 0.18 * rank01(gap, high=True)
        mult = mult * (1.0 - 0.45 * work["h112_in_h111_selected"].to_numpy(dtype=np.float64))
    elif spec.prior_mode == "q2_companion":
        q2 = work["target"].astype(str).eq("Q2").astype(float).to_numpy()
        mult = 0.34 + 0.22 * q2 + 0.20 * rank01(safety, high=True)
    else:
        raise ValueError(spec.prior_mode)
    prior = raw * mult
    if good_axes.size:
        good_proj = good_axes.T @ (good_axes @ prior)
        prior = prior + spec.good_push * good_proj
    return prior


def solve_nullspace(work: pd.DataFrame, spec: H114Spec, toxic_axes: np.ndarray, good_axes: np.ndarray) -> np.ndarray:
    prior = prior_vector(work, spec, good_axes)
    n = len(prior)
    bad = toxic_axes.T @ toxic_axes
    rhs = prior.copy()
    if good_axes.size:
        rhs = rhs + spec.good_push * (good_axes.T @ (good_axes @ prior))
    lhs = np.eye(n, dtype=np.float64) * (1.0 + spec.ridge) + spec.bad_penalty * bad
    solved = np.linalg.solve(lhs, rhs)
    scale = float(np.quantile(np.abs(solved), 0.96))
    if scale > 1.0e-12:
        solved = np.tanh(solved / scale) * scale
    return np.clip(solved * spec.amp, -spec.cap, spec.cap)


def select_cells(
    pool: pd.DataFrame,
    spec: H114Spec,
    public: pd.DataFrame,
    residuals: pd.DataFrame,
    bad_axes: pd.DataFrame,
    bad_moves: np.ndarray,
    good_moves: np.ndarray,
    shape: tuple[int, int],
) -> tuple[pd.DataFrame, np.ndarray, dict[str, float], pd.DataFrame, dict[str, float]]:
    work = pool[allowed_mask(pool, spec)].copy()
    work = work.sort_values(["h112_assignment_score", "h112_residual_gap"], ascending=[False, False]).head(spec.pool_top).reset_index(drop=True)
    if work.empty:
        return pd.DataFrame(), np.zeros(shape, dtype=np.float64), h102mod.cumulative_axis_metrics(np.zeros(shape).reshape(-1), bad_axes, bad_moves, good_moves), pd.DataFrame(), {}
    flat = work["flat_index"].astype(int).to_numpy()
    toxic_axes, axis_meta = toxic_axis_matrix(spec, flat, public, residuals, bad_moves, bad_axes)
    good_axes = good_axis_matrix(flat, good_moves)
    solved = solve_nullspace(work, spec, toxic_axes, good_axes)
    toxic_projection_before = float(np.linalg.norm(toxic_axes @ prior_vector(work, spec, good_axes)))
    toxic_projection_after = float(np.linalg.norm(toxic_axes @ solved))
    good_projection_after = float(np.linalg.norm(good_axes @ solved)) if good_axes.size else 0.0
    work["h114_null_move"] = solved
    work["h114_abs_null_move"] = np.abs(solved)
    work["h114_cell_score"] = (
        0.32 * rank01(work["h114_abs_null_move"].to_numpy(dtype=np.float64), high=True)
        + 0.22 * rank01(work["h112_assignment_score"].to_numpy(dtype=np.float64), high=True)
        + 0.18 * rank01(work["h112_residual_safety"].to_numpy(dtype=np.float64), high=True)
        + 0.14 * rank01(work["h112_residual_gap"].to_numpy(dtype=np.float64), high=True)
        + 0.10 * rank01(work["h112_antidote_score"].to_numpy(dtype=np.float64), high=True)
        + 0.06 * work["h111_h108_rejected"].to_numpy(dtype=np.float64)
        - 0.18 * rank01(work["h112_residual_toxicity"].to_numpy(dtype=np.float64), high=True)
        - 0.06 * work["target"].astype(str).eq("Q2").astype(float).to_numpy()
    )
    work = work[np.abs(work["h114_null_move"].to_numpy(dtype=np.float64)) >= spec.min_abs_move]
    work = work.sort_values(["h114_cell_score", "h114_abs_null_move"], ascending=[False, False]).reset_index(drop=True)

    move_mat = np.zeros(shape, dtype=np.float64)
    selected_rows: set[int] = set()
    subject_counts: dict[str, int] = {}
    target_counts: dict[str, int] = {}
    q2_count = 0
    selected_idx: list[int] = []
    axis = h102mod.cumulative_axis_metrics(move_mat.reshape(-1), bad_axes, bad_moves, good_moves)
    for idx, rec in enumerate(work.to_dict("records")):
        if len(selected_idx) >= spec.max_cells:
            break
        row = int(rec["row"])
        subject = str(rec["subject_id"])
        target = str(rec["target"])
        tidx = int(rec["target_index"])
        if row not in selected_rows and len(selected_rows) >= spec.max_rows:
            continue
        if row not in selected_rows and subject_counts.get(subject, 0) + 1 > spec.max_per_subject:
            continue
        if target_counts.get(target, 0) >= spec.max_per_target:
            continue
        if target == "Q2" and q2_count >= spec.q2_cap:
            continue
        tmp = move_mat.copy()
        tmp[row, tidx] = float(rec["h114_null_move"])
        cand_axis = h102mod.cumulative_axis_metrics(tmp.reshape(-1), bad_axes, bad_moves, good_moves)
        if cand_axis["h102_cum_bad_weighted_pos"] > spec.max_bad_weighted_pos:
            continue
        if cand_axis["h102_cum_bad_max_pos"] > spec.max_bad_max_pos:
            continue
        if cand_axis["h102_cum_h088_axis_cos"] > spec.max_h088_cos:
            continue
        if cand_axis["h102_cum_good_bad_margin"] < spec.min_good_margin:
            continue
        move_mat = tmp
        axis = cand_axis
        selected_idx.append(idx)
        if row not in selected_rows:
            selected_rows.add(row)
            subject_counts[subject] = subject_counts.get(subject, 0) + 1
        target_counts[target] = target_counts.get(target, 0) + 1
        q2_count += int(target == "Q2")

    if not selected_idx:
        return pd.DataFrame(), move_mat, axis, axis_meta, {
            "toxic_projection_before": toxic_projection_before,
            "toxic_projection_after": toxic_projection_after,
            "good_projection_after": good_projection_after,
        }
    selected = work.iloc[selected_idx].copy().sort_values(["row", "target_index"]).reset_index(drop=True)
    selected["h112_move"] = selected["h114_null_move"]
    selected["h097_move_col"] = "h112_move"
    diag = {
        "toxic_projection_before": toxic_projection_before,
        "toxic_projection_after": toxic_projection_after,
        "toxic_projection_ratio": toxic_projection_after / max(toxic_projection_before, 1.0e-12),
        "good_projection_after": good_projection_after,
        "toxic_axes": int(len(axis_meta)),
        "work_cells": int(len(work)),
    }
    return selected, move_mat, axis, axis_meta, diag


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
    spec: H114Spec,
    path: Path,
    axis: dict[str, float],
    diag: dict[str, float],
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
        pool_top=spec.pool_top,
        beam_width=1,
        min_score=spec.min_score,
        min_gap=-1.0,
        max_residual_toxicity=spec.max_residual_toxicity,
        min_residual_safety=spec.min_residual_safety,
        min_family_count=1,
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
    for label, prev in previous.items():
        out[f"h114_{label}_overlap_cells"] = overlap_count(move_flat, prev)
        out[f"h114_{label}_cosine"] = cosine(move_flat, prev)
    out.update({f"h114_{key}": value for key, value in diag.items()})
    toxic_ratio = float(out.get("h114_toxic_projection_ratio", 1.0))
    novelty = max(0.0, min(1.0, 1.0 - abs(float(out.get("h114_h112_cosine", 0.0)))))
    out["h114_novelty_vs_h112"] = novelty
    out["h114_null_quality"] = max(0.0, 1.0 - toxic_ratio)
    out["h114_score"] = (
        115.0 * (-float(out["model_pred_delta_vs_h057"]))
        + 95.0 * (-float(out["route_basis_pred_delta_vs_h057"]))
        + 0.20 * float(out["h114_null_quality"])
        + 0.14 * novelty
        + 0.14 * float(out["selected_mean_residual_safety"])
        + 0.10 * float(out["selected_mean_residual_gap"])
        + 0.08 * float(out["selected_mean_antidote_score"])
        + 0.04 * max(-float(out["h102_cum_h088_axis_cos"]), 0.0)
        - 0.18 * float(out["selected_mean_residual_toxicity"])
        - 0.55 * max(float(out["h102_cum_bad_weighted_pos"]), 0.0)
        - 0.28 * max(float(out["h102_cum_bad_max_pos"]), 0.0)
        - 0.16 * max(float(out["h102_cum_h088_axis_cos"]), 0.0)
        - 18.0 * max(float(out["hard_diag_delta_vs_h057"]), 0.0)
    )
    return out


def run() -> None:
    cleanup_previous_outputs()
    pool, public, sample, base_prob, cell, h098_fit, route_fit, basis_fit_df, basis_fit_moves, bad_axes, bad_moves, good_moves, residuals = prepare_context()
    previous = {
        "h113": load_previous_move(sample, base_prob, "submission_h113_rowroute_*_uploadsafe.csv"),
        "h112": load_previous_move(sample, base_prob, "submission_h112_residualtox_*_uploadsafe.csv"),
        "h111": load_previous_move(sample, base_prob, "submission_h111_boundary_*_uploadsafe.csv"),
        "h110": load_previous_move(sample, base_prob, "submission_h110_toxgap_*_uploadsafe.csv"),
    }

    candidate_rows = []
    selected_frames = []
    axis_frames = []
    for spec in candidate_specs():
        selected, move_mat, axis, axis_meta, diag = select_cells(pool, spec, public, residuals, bad_axes, bad_moves, good_moves, base_prob.shape)
        if selected.empty:
            continue
        rpred = route_pred(move_mat.reshape(-1), basis_fit_df, basis_fit_moves, route_fit)
        cpred = h098_pred(move_mat.reshape(-1), cell, h098_fit)
        if rpred > spec.route_pred_cap or cpred > spec.h098_pred_cap:
            continue
        prob = materialize(base_prob, move_mat)
        if int((np.abs(prob - base_prob) > TOL).sum()) == 0:
            continue
        hash_id = short_hash(prob)
        candidate_id = safe_id(f"h114_{spec.name}_{hash_id}", 128)
        path = OUT / f"submission_{candidate_id}.csv"
        h085mod.write_submission(sample, prob, path)
        metrics = evaluate_candidate(
            candidate_id,
            prob,
            move_mat,
            selected,
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
            diag,
            previous,
        )
        candidate_rows.append(metrics)
        selected2 = selected.copy()
        selected2.insert(0, "candidate_id", candidate_id)
        selected_frames.append(selected2)
        axis_meta2 = axis_meta.copy()
        axis_meta2.insert(0, "candidate_id", candidate_id)
        axis_meta2.insert(1, "spec_name", spec.name)
        axis_frames.append(axis_meta2)

    candidates = pd.DataFrame(candidate_rows)
    if candidates.empty:
        raise RuntimeError("no H114 candidates")
    candidates = candidates.sort_values(["h114_score", "route_basis_pred_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True)
    selected = candidates.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"submission_h114_nullspace_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)

    decision = {
        "decision": "promote_h114_toxic_subspace_null_solver",
        "selected_candidate_id": selected["candidate_id"],
        "root_uploadsafe_path": str(root_path.resolve()),
        "known_public_observations": int(len(public)),
        "worldview": selected["worldview"],
        **selected,
        **{f"root_{key}": value for key, value in validation.items()},
    }

    pool.to_csv(OUT / "h114_nullspace_pool.csv", index=False)
    candidates.to_csv(OUT / "h114_candidates.csv", index=False)
    pd.concat(selected_frames, ignore_index=True).to_csv(OUT / "h114_selected_cells.csv", index=False)
    pd.concat(axis_frames, ignore_index=True).to_csv(OUT / "h114_toxic_axes.csv", index=False)
    pd.DataFrame([decision]).to_csv(OUT / "h114_decision.csv", index=False)

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
        "selected_mean_residual_toxicity",
        "selected_mean_residual_safety",
        "selected_mean_residual_gap",
        "selected_h111_cells",
        "selected_h108_rejected_cells",
        "h114_toxic_projection_ratio",
        "h114_null_quality",
        "h114_h112_overlap_cells",
        "h114_h112_cosine",
        "h114_novelty_vs_h112",
        "h114_score",
        "file",
    ]
    report = f"""# H114 Toxic-Subspace Null Solver HS-JEPA

Question: can HS-JEPA separate public-punished action toxicity from safe
assignment by projecting candidate actions into the nullspace of known toxic
public directions before selecting row-target cells?

Candidates:

{md_table(candidates[cols], 20)}

Decision:

{md_table(pd.DataFrame([decision]), 1)}

Interpretation rule:

- If H114 improves over H112/H113, the action decoder should be formulated as a
  toxic-subspace null solver, not a local residual-toxicity selector.
- If H112/H113 improve more, explicit vector nullspace projection discards
  useful signal or overfits the small public observation set.
- If H110/H111 improve more, public-bad axes are useful only as stress tests,
  not as a projection space.
"""
    (OUT / "h114_report.md").write_text(report, encoding="utf-8")

    print("H114 selected candidate")
    print(candidates[cols].head(10).to_string(index=False))
    print("\nDecision")
    print(pd.DataFrame([decision])[["decision", "selected_candidate_id", "root_uploadsafe_path", "root_upload_safe"]].to_string(index=False))


if __name__ == "__main__":
    run()
