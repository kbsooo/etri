#!/usr/bin/env python3
"""H119: observation-equation veto HS-JEPA.

H085 learned a hidden public label/posterior field, but direct materialization
can be action-toxic.  H118 learned that the Q2 companion sector is useful as a
veto rather than as an action target.  H119 combines those two claims:

    public-equation posterior gain
    + forbidden-sector veto
    + residual toxicity / H088 / curvature stress
    -> row-target safe assignment

This is an action-grade decoder test.  The candidate should not merely move
toward a plausible hidden state; it must also avoid the action sectors that
public observations punish.
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
OUT = HITL / "h119_observation_equation_veto_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H118_PATH = HITL / "h118_forbidden_veto_assignment_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h118mod", H118_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H118_PATH}")
h118mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h118mod
SPEC.loader.exec_module(h118mod)

h117mod = h118mod.h117mod
h115mod = h118mod.h115mod
h112mod = h118mod.h112mod
h102mod = h118mod.h102mod
h100mod = h118mod.h100mod
h097mod = h118mod.h097mod
h085mod = h118mod.h085mod

TARGETS = h118mod.TARGETS
KEYS = h118mod.KEYS
BASE_FILE = h118mod.BASE_FILE
TOL = h118mod.TOL


@dataclass(frozen=True)
class H119Spec:
    name: str
    group: str
    move_mode: str
    max_cells: int
    max_rows: int
    max_per_subject: int
    max_per_target: int
    q2_cap: int
    amp: float
    cap: float
    pool_top: int
    max_forbidden_same: float
    max_forbidden_pressure: float
    min_residual_safety: float
    max_residual_toxicity: float
    min_residual_gap: float
    min_h085_q_gain: float
    min_h085_cell_score: float
    require_source_agree: bool
    min_h057_positive_weight: float
    min_score: float
    max_curv_marginal: float
    max_marginal_add: float
    max_bad_weighted_pos: float
    max_bad_max_pos: float
    max_h088_cos: float
    min_good_margin: float
    route_pred_cap: float
    h098_pred_cap: float
    worldview: str


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def safe_id(text: str, limit: int = 132) -> str:
    return h085mod.safe_id(text, limit=limit)


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return h085mod.md_table(frame, n=n)


def logit(x: np.ndarray) -> np.ndarray:
    return h085mod.logit(np.asarray(x, dtype=np.float64))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return h085mod.sigmoid(np.asarray(x, dtype=np.float64))


def clip_prob(x: np.ndarray) -> np.ndarray:
    return h085mod.clip_prob(np.asarray(x, dtype=np.float64))


def bce(prob: np.ndarray, q: np.ndarray) -> np.ndarray:
    return h085mod.bce(np.asarray(prob, dtype=np.float64), np.asarray(q, dtype=np.float64))


def rank01(values: np.ndarray, high: bool = True) -> np.ndarray:
    return h085mod.rank01(np.asarray(values, dtype=np.float64), high=high)


def materialize(base_prob: np.ndarray, move_mat: np.ndarray) -> np.ndarray:
    return clip_prob(sigmoid(logit(base_prob) + move_mat))


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h119_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h119_obseqveto_*_uploadsafe.csv"):
        path.unlink()


def route_pred(move_flat: np.ndarray, basis_fit_df: pd.DataFrame, basis_fit_moves: np.ndarray, route_fit: h100mod.RouteBasisFit) -> float:
    return h100mod.predict_candidate_delta(move_flat, basis_fit_df, basis_fit_moves, route_fit)


def h098_pred(move_flat: np.ndarray, cell: pd.DataFrame, h098_fit: h097mod.ResponseFit) -> float:
    return h097mod.predict_candidate_delta(move_flat, cell, h098_fit)


def curvature_pred(move_mat: np.ndarray, fit: h115mod.CurvatureFit, pool: pd.DataFrame, bad_axes: pd.DataFrame, bad_moves: np.ndarray, good_moves: np.ndarray, axes: dict[str, object]) -> float:
    return h115mod.predict_curvature(move_mat, fit, pool, bad_axes, bad_moves, good_moves, axes)


def candidate_specs() -> list[H119Spec]:
    return [
        H119Spec(
            name="obseq_sourceagree_nonq2_c64_a050",
            group="nonq2",
            move_mode="posterior_blend",
            max_cells=64,
            max_rows=40,
            max_per_subject=9,
            max_per_target=18,
            q2_cap=0,
            amp=0.50,
            cap=0.16,
            pool_top=240,
            max_forbidden_same=1.0e-12,
            max_forbidden_pressure=0.0,
            min_residual_safety=0.48,
            max_residual_toxicity=0.62,
            min_residual_gap=-0.01,
            min_h085_q_gain=0.00020,
            min_h085_cell_score=0.40,
            require_source_agree=True,
            min_h057_positive_weight=0.0,
            min_score=0.18,
            max_curv_marginal=0.000060,
            max_marginal_add=0.000024,
            max_bad_weighted_pos=0.008,
            max_bad_max_pos=0.044,
            max_h088_cos=-0.003,
            min_good_margin=0.003,
            route_pred_cap=0.000150,
            h098_pred_cap=0.000110,
            worldview="H085 public posterior is useful only where source agreement and forbidden-sector veto both hold",
        ),
        H119Spec(
            name="obseq_rowstate_anchor_c72_a044",
            group="h057_anchor",
            move_mode="posterior_conservative",
            max_cells=72,
            max_rows=28,
            max_per_subject=8,
            max_per_target=17,
            q2_cap=0,
            amp=0.44,
            cap=0.14,
            pool_top=260,
            max_forbidden_same=1.0e-12,
            max_forbidden_pressure=0.0,
            min_residual_safety=0.46,
            max_residual_toxicity=0.64,
            min_residual_gap=-0.02,
            min_h085_q_gain=0.00008,
            min_h085_cell_score=0.30,
            require_source_agree=True,
            min_h057_positive_weight=0.02,
            min_score=0.14,
            max_curv_marginal=0.000065,
            max_marginal_add=0.000026,
            max_bad_weighted_pos=0.009,
            max_bad_max_pos=0.046,
            max_h088_cos=-0.002,
            min_good_margin=0.002,
            route_pred_cap=0.000160,
            h098_pred_cap=0.000115,
            worldview="H057 positive row-state is safe when the H085 posterior move is constrained to already-positive anchor rows",
        ),
        H119Spec(
            name="obseq_stage_balance_c58_a054",
            group="stage",
            move_mode="posterior_blend",
            max_cells=58,
            max_rows=38,
            max_per_subject=9,
            max_per_target=18,
            q2_cap=0,
            amp=0.54,
            cap=0.17,
            pool_top=220,
            max_forbidden_same=1.0e-12,
            max_forbidden_pressure=0.0,
            min_residual_safety=0.50,
            max_residual_toxicity=0.60,
            min_residual_gap=0.00,
            min_h085_q_gain=0.00018,
            min_h085_cell_score=0.38,
            require_source_agree=True,
            min_h057_positive_weight=0.0,
            min_score=0.17,
            max_curv_marginal=0.000055,
            max_marginal_add=0.000022,
            max_bad_weighted_pos=0.008,
            max_bad_max_pos=0.044,
            max_h088_cos=-0.003,
            min_good_margin=0.003,
            route_pred_cap=0.000145,
            h098_pred_cap=0.000105,
            worldview="the safe assignment field is the Q3/S-stage part of the H085 posterior after forbidden-sector veto",
        ),
        H119Spec(
            name="obseq_highgain_sparse_c34_a048",
            group="nonq2",
            move_mode="posterior",
            max_cells=34,
            max_rows=30,
            max_per_subject=6,
            max_per_target=12,
            q2_cap=0,
            amp=0.48,
            cap=0.18,
            pool_top=140,
            max_forbidden_same=1.0e-12,
            max_forbidden_pressure=0.0,
            min_residual_safety=0.48,
            max_residual_toxicity=0.66,
            min_residual_gap=-0.03,
            min_h085_q_gain=0.00110,
            min_h085_cell_score=0.58,
            require_source_agree=True,
            min_h057_positive_weight=0.0,
            min_score=0.20,
            max_curv_marginal=0.000070,
            max_marginal_add=0.000028,
            max_bad_weighted_pos=0.007,
            max_bad_max_pos=0.040,
            max_h088_cos=-0.003,
            min_good_margin=0.003,
            route_pred_cap=0.000130,
            h098_pred_cap=0.000100,
            worldview="only the highest-confidence H085 posterior cells survive as action-grade corrections",
        ),
        H119Spec(
            name="obseq_q2_exception_c10_a030",
            group="q2",
            move_mode="posterior_conservative",
            max_cells=10,
            max_rows=10,
            max_per_subject=4,
            max_per_target=10,
            q2_cap=10,
            amp=0.30,
            cap=0.10,
            pool_top=80,
            max_forbidden_same=1.0e-12,
            max_forbidden_pressure=0.0,
            min_residual_safety=0.55,
            max_residual_toxicity=0.52,
            min_residual_gap=0.02,
            min_h085_q_gain=0.00035,
            min_h085_cell_score=0.50,
            require_source_agree=True,
            min_h057_positive_weight=0.0,
            min_score=0.16,
            max_curv_marginal=0.000020,
            max_marginal_add=0.000010,
            max_bad_weighted_pos=0.004,
            max_bad_max_pos=0.030,
            max_h088_cos=-0.004,
            min_good_margin=0.004,
            route_pred_cap=0.000060,
            h098_pred_cap=0.000060,
            worldview="Q2 may re-enter only as a tiny posterior-confirmed exception outside the forbidden sector",
        ),
    ]


def target_allowed(work: pd.DataFrame, spec: H119Spec) -> np.ndarray:
    target = work["target"].astype(str)
    if spec.group == "nonq2":
        return target.ne("Q2").to_numpy()
    if spec.group == "stage":
        return target.isin(["Q3", "S1", "S2", "S3", "S4"]).to_numpy()
    if spec.group == "h057_anchor":
        return target.ne("Q2").to_numpy() & work["h057_positive_weight"].astype(float).ge(spec.min_h057_positive_weight).to_numpy()
    if spec.group == "q2":
        return target.eq("Q2").to_numpy()
    raise ValueError(spec.group)


def proposal_move(work: pd.DataFrame, spec: H119Spec) -> np.ndarray:
    prop = work["proposal_move"].to_numpy(dtype=np.float64)
    qmove = work["h085_q_move"].to_numpy(dtype=np.float64)
    if spec.move_mode == "posterior":
        raw = qmove
    elif spec.move_mode == "posterior_blend":
        raw = 0.55 * qmove + 0.45 * prop
    elif spec.move_mode == "posterior_conservative":
        raw = np.sign(qmove) * np.minimum(np.abs(qmove), np.maximum(np.abs(prop), 0.04))
    else:
        raise ValueError(spec.move_mode)
    return np.clip(raw * spec.amp, -spec.cap, spec.cap)


def cell_q_delta(base_p: np.ndarray, q: np.ndarray, move: np.ndarray) -> np.ndarray:
    new_p = clip_prob(sigmoid(logit(base_p) + move))
    return bce(new_p, q) - bce(base_p, q)


def annotate_observation_scores(scored: pd.DataFrame) -> pd.DataFrame:
    out = scored.copy()
    prop = out["proposal_move"].to_numpy(dtype=np.float64)
    qmove = out["h085_q_move"].to_numpy(dtype=np.float64)
    out["h119_h085_align"] = ((np.sign(prop) * np.sign(qmove) > 0) | (np.abs(qmove) < 1.0e-12)).astype(float)
    out["h119_obseq_base_score"] = (
        0.26 * rank01(out["h085_q_gain"].to_numpy(dtype=np.float64), high=True)
        + 0.20 * out["h085_cell_score"].to_numpy(dtype=np.float64)
        + 0.13 * out["source_agrees_h085"].to_numpy(dtype=np.float64)
        + 0.13 * rank01(out["h112_residual_safety"].to_numpy(dtype=np.float64), high=True)
        + 0.10 * rank01(out["h112_residual_gap"].to_numpy(dtype=np.float64), high=True)
        + 0.08 * out["h118_forbidden_veto_score"].to_numpy(dtype=np.float64)
        + 0.06 * out["h119_h085_align"].to_numpy(dtype=np.float64)
        + 0.05 * out["h112_in_h111_selected"].to_numpy(dtype=np.float64)
        - 0.16 * rank01(out["h112_residual_toxicity"].to_numpy(dtype=np.float64), high=True)
        - 0.12 * rank01(out["latent_shortcut_energy"].to_numpy(dtype=np.float64), high=True)
        - 0.08 * rank01(out["h117_forbidden_same"].to_numpy(dtype=np.float64), high=True)
    )
    return out


def select_cells(
    scored: pd.DataFrame,
    spec: H119Spec,
    shape: tuple[int, int],
    fit: h115mod.CurvatureFit,
    pool: pd.DataFrame,
    bad_axes: pd.DataFrame,
    bad_moves: np.ndarray,
    good_moves: np.ndarray,
    axes: dict[str, object],
) -> tuple[pd.DataFrame, np.ndarray, dict[str, float], dict[str, float]]:
    work = scored[target_allowed(scored, spec)].copy()
    work = work[work["h117_forbidden_same"].to_numpy(dtype=np.float64) <= spec.max_forbidden_same].copy()
    work = work[work["h117_forbidden_pressure"].to_numpy(dtype=np.float64) <= spec.max_forbidden_pressure].copy()
    work = work[work["h112_residual_safety"].to_numpy(dtype=np.float64) >= spec.min_residual_safety].copy()
    work = work[work["h112_residual_toxicity"].to_numpy(dtype=np.float64) <= spec.max_residual_toxicity].copy()
    work = work[work["h112_residual_gap"].to_numpy(dtype=np.float64) >= spec.min_residual_gap].copy()
    work = work[work["h085_q_gain"].to_numpy(dtype=np.float64) >= spec.min_h085_q_gain].copy()
    work = work[work["h085_cell_score"].to_numpy(dtype=np.float64) >= spec.min_h085_cell_score].copy()
    if spec.require_source_agree:
        work = work[work["source_agrees_h085"].to_numpy(dtype=np.float64) > 0.5].copy()
    work = work[work["h119_h085_align"].to_numpy(dtype=np.float64) > 0.5].copy()
    work = work[work["h119_obseq_base_score"].to_numpy(dtype=np.float64) >= spec.min_score].copy()
    if work.empty:
        return pd.DataFrame(), np.zeros(shape, dtype=np.float64), {}, {}

    move = proposal_move(work, spec)
    q_delta = cell_q_delta(
        work["h057_prob"].to_numpy(dtype=np.float64),
        work["h085_q"].to_numpy(dtype=np.float64),
        move,
    )
    work["h119_move"] = move
    work["h119_cell_q_delta"] = q_delta
    work = work[work["h119_cell_q_delta"].to_numpy(dtype=np.float64) < 0.0].copy()
    if work.empty:
        return pd.DataFrame(), np.zeros(shape, dtype=np.float64), {}, {}

    work["h119_cell_score"] = (
        0.30 * work["h119_obseq_base_score"].to_numpy(dtype=np.float64)
        + 0.22 * rank01(-work["h119_cell_q_delta"].to_numpy(dtype=np.float64), high=True)
        + 0.14 * rank01(work["h085_q_gain"].to_numpy(dtype=np.float64), high=True)
        + 0.12 * rank01(work["h112_residual_safety"].to_numpy(dtype=np.float64), high=True)
        + 0.09 * rank01(work["h112_residual_gap"].to_numpy(dtype=np.float64), high=True)
        + 0.08 * rank01(np.abs(work["h119_move"].to_numpy(dtype=np.float64)), high=True)
        - 0.16 * rank01(work["h112_residual_toxicity"].to_numpy(dtype=np.float64), high=True)
    )
    work = work.sort_values(["h119_cell_score", "h085_q_gain"], ascending=[False, False])
    work = work.drop_duplicates(["row", "target"], keep="first").head(spec.pool_top).reset_index(drop=True)

    move_mat = np.zeros(shape, dtype=np.float64)
    zero_curv = curvature_pred(move_mat, fit, pool, bad_axes, bad_moves, good_moves, axes)
    curv_now = zero_curv
    selected_idx = []
    selected_flat: set[int] = set()
    selected_rows: set[int] = set()
    subject_counts: dict[str, int] = {}
    target_counts: dict[str, int] = {}
    q2_count = 0
    axis = h102mod.cumulative_axis_metrics(move_mat.reshape(-1), bad_axes, bad_moves, good_moves)
    for idx, rec in enumerate(work.to_dict("records")):
        flat = int(rec["flat_index"])
        if flat in selected_flat:
            continue
        if len(selected_idx) >= spec.max_cells:
            break
        row = int(rec["row"])
        subject = str(rec["subject_id"])
        target = str(rec["target"])
        tidx = int(rec["target_index"])
        if target == "Q2" and q2_count >= spec.q2_cap:
            continue
        if row not in selected_rows and len(selected_rows) >= spec.max_rows:
            continue
        if row not in selected_rows and subject_counts.get(subject, 0) + 1 > spec.max_per_subject:
            continue
        if target_counts.get(target, 0) >= spec.max_per_target:
            continue
        tmp = move_mat.copy()
        tmp[row, tidx] = float(rec["h119_move"])
        next_axis = h102mod.cumulative_axis_metrics(tmp.reshape(-1), bad_axes, bad_moves, good_moves)
        if next_axis["h102_cum_bad_weighted_pos"] > spec.max_bad_weighted_pos:
            continue
        if next_axis["h102_cum_bad_max_pos"] > spec.max_bad_max_pos:
            continue
        if next_axis["h102_cum_h088_axis_cos"] > spec.max_h088_cos:
            continue
        if next_axis["h102_cum_good_bad_margin"] < spec.min_good_margin:
            continue
        curv_next = curvature_pred(tmp, fit, pool, bad_axes, bad_moves, good_moves, axes)
        if curv_next - zero_curv > spec.max_curv_marginal:
            continue
        if selected_idx and (curv_next - curv_now) > spec.max_marginal_add:
            continue
        move_mat = tmp
        curv_now = curv_next
        axis = next_axis
        selected_idx.append(idx)
        selected_flat.add(flat)
        if row not in selected_rows:
            selected_rows.add(row)
            subject_counts[subject] = subject_counts.get(subject, 0) + 1
        target_counts[target] = target_counts.get(target, 0) + 1
        if target == "Q2":
            q2_count += 1

    if not selected_idx:
        return pd.DataFrame(), move_mat, axis, {
            "h118_zero_curv": zero_curv,
            "h118_curv_pred_delta_vs_h057": curv_now,
            "h118_curv_marginal_vs_zero": curv_now - zero_curv,
        }

    selected = work.iloc[selected_idx].copy().sort_values(["row", "target_index"]).reset_index(drop=True)
    selected["h112_move"] = [
        move_mat[int(row), int(tidx)]
        for row, tidx in zip(selected["row"].astype(int), selected["target_index"].astype(int))
    ]
    selected["h097_move_col"] = "h112_move"
    diag = {
        "h118_zero_curv": zero_curv,
        "h118_curv_pred_delta_vs_h057": curv_now,
        "h118_curv_marginal_vs_zero": curv_now - zero_curv,
        "h118_mean_forbidden_same": float(selected["h117_forbidden_same"].mean()),
        "h118_max_forbidden_same": float(selected["h117_forbidden_same"].max()),
        "h118_mean_forbidden_pressure": float(selected["h117_forbidden_pressure"].mean()),
        "h118_mean_veto_score": float(selected["h118_forbidden_veto_score"].mean()),
        "h118_selected_rows": int(len(selected_rows)),
        "h119_selected_q2_cells": int((selected["target"].astype(str) == "Q2").sum()),
        "h119_mean_cell_q_delta": float(selected["h119_cell_q_delta"].mean()),
        "h119_sum_cell_q_delta": float(selected["h119_cell_q_delta"].sum()),
        "h119_mean_h085_q_gain": float(selected["h085_q_gain"].mean()),
        "h119_mean_h085_cell_score": float(selected["h085_cell_score"].mean()),
        "h119_source_agree_rate": float(selected["source_agrees_h085"].mean()),
        "h119_h085_align_rate": float(selected["h119_h085_align"].mean()),
    }
    return selected, move_mat, axis, diag


def run() -> None:
    cleanup_previous_outputs()
    pool, _public, sample, base_prob, cell, h098_fit, route_fit, basis_fit_df, basis_fit_moves, bad_axes, bad_moves, good_moves, axes, fit, model_scores, props = h118mod.prepare_context()
    forbidden_axes, forbidden_weights, forbidden_audit = h117mod.build_forbidden_axes(props, base_prob.shape, fit, pool, bad_axes, bad_moves, good_moves, axes)
    scored_raw = h117mod.annotate_forbidden_scores(props, forbidden_axes, forbidden_weights)
    scored = annotate_observation_scores(h118mod.annotate_veto_scores(scored_raw))
    previous = {
        "h118": h115mod.load_previous_move(sample, base_prob, "submission_h118_forbiddenveto_*_uploadsafe.csv"),
        "h115": h115mod.load_previous_move(sample, base_prob, "submission_h115_curvature_*_uploadsafe.csv"),
        "h114": h115mod.load_previous_move(sample, base_prob, "submission_h114_nullspace_*_uploadsafe.csv"),
        "h113": h115mod.load_previous_move(sample, base_prob, "submission_h113_rowroute_*_uploadsafe.csv"),
        "h112": h115mod.load_previous_move(sample, base_prob, "submission_h112_residualtox_*_uploadsafe.csv"),
    }

    audit_rows = []
    candidate_rows = []
    selected_frames = []
    for spec in candidate_specs():
        pre = scored[target_allowed(scored, spec)].copy()
        audit_rows.append(
            {
                "spec_name": spec.name,
                "prefilter_rows": int(len(pre)),
                "forbidden_same_pass": int((pre["h117_forbidden_same"].to_numpy(dtype=np.float64) <= spec.max_forbidden_same).sum()),
                "h085_gain_pass": int((pre["h085_q_gain"].to_numpy(dtype=np.float64) >= spec.min_h085_q_gain).sum()),
                "h085_score_pass": int((pre["h085_cell_score"].to_numpy(dtype=np.float64) >= spec.min_h085_cell_score).sum()),
                "source_agree_pass": int((pre["source_agrees_h085"].to_numpy(dtype=np.float64) > 0.5).sum()),
                "residual_safety_pass": int((pre["h112_residual_safety"].to_numpy(dtype=np.float64) >= spec.min_residual_safety).sum()),
                "residual_toxicity_pass": int((pre["h112_residual_toxicity"].to_numpy(dtype=np.float64) <= spec.max_residual_toxicity).sum()),
            }
        )
        selected, move_mat, axis, diag = select_cells(scored, spec, base_prob.shape, fit, pool, bad_axes, bad_moves, good_moves, axes)
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
        candidate_id = safe_id(f"h119_{spec.name}_{hash_id}", 128)
        path = OUT / f"submission_{candidate_id}.csv"
        h085mod.write_submission(sample, prob, path)
        metrics = h118mod.evaluate_candidate(
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
        metrics["h119_fit_feature_set"] = fit.feature_set
        metrics["h119_fit_alpha"] = fit.alpha
        metrics["h119_fit_score"] = fit.score
        metrics["h119_forbidden_axes"] = int(len(forbidden_axes))
        metrics["h119_score"] = (
            210.0 * (-float(metrics["posterior_delta_vs_h057"]))
            + 150.0 * (-float(metrics["h118_curv_marginal_vs_zero"]))
            + 115.0 * (-float(metrics["route_basis_pred_delta_vs_h057"]))
            + 90.0 * (-float(metrics["model_pred_delta_vs_h057"]))
            + 0.20 * float(metrics["h119_mean_h085_cell_score"])
            + 0.16 * float(metrics["h119_source_agree_rate"])
            + 0.14 * float(metrics["selected_mean_residual_safety"])
            + 0.12 * float(metrics["selected_mean_residual_gap"])
            + 0.08 * max(-float(metrics["h102_cum_h088_axis_cos"]), 0.0)
            - 0.20 * float(metrics["selected_mean_residual_toxicity"])
            - 0.14 * float(metrics["h119_selected_q2_cells"])
            - 0.50 * max(float(metrics["h102_cum_bad_weighted_pos"]), 0.0)
            - 20.0 * max(float(metrics["hard_diag_delta_vs_h057"]), 0.0)
        )
        candidate_rows.append(metrics)
        selected2 = selected.copy()
        if "candidate_id" in selected2.columns:
            selected2 = selected2.drop(columns=["candidate_id"])
        selected2.insert(0, "candidate_id", candidate_id)
        selected_frames.append(selected2)

    audit = pd.DataFrame(audit_rows)
    candidates = pd.DataFrame(candidate_rows)
    forbidden_audit.to_csv(OUT / "h119_forbidden_axes.csv", index=False)
    audit.to_csv(OUT / "h119_filter_audit.csv", index=False)
    scored.to_csv(OUT / "h119_scored_proposals.csv", index=False)
    model_scores.to_csv(OUT / "h119_curvature_model_scores.csv", index=False)

    if candidates.empty:
        report = f"""# H119 Observation-Equation Veto HS-JEPA

No candidate was promoted.

Filter audit:

{md_table(audit, 20)}
"""
        (OUT / "h119_report.md").write_text(report, encoding="utf-8")
        print("H119 promoted no candidate")
        print(audit.to_string(index=False))
        return

    candidates = candidates.sort_values(["h119_score", "posterior_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True)
    selected = candidates.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"submission_h119_obseqveto_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)

    decision = {
        "decision": "promote_h119_observation_equation_veto",
        "selected_candidate_id": selected["candidate_id"],
        "root_uploadsafe_path": str(root_path.resolve()),
        "worldview": selected["worldview"],
        "selected_fit_feature_set": fit.feature_set,
        "selected_fit_alpha": fit.alpha,
        "selected_fit_score": fit.score,
        **selected,
        **{f"root_{key}": value for key, value in validation.items()},
    }

    candidates.to_csv(OUT / "h119_candidates.csv", index=False)
    pd.concat(selected_frames, ignore_index=True).to_csv(OUT / "h119_selected_cells.csv", index=False)
    pd.DataFrame([decision]).to_csv(OUT / "h119_decision.csv", index=False)

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
        "posterior_delta_vs_h057",
        "h119_mean_cell_q_delta",
        "h119_mean_h085_q_gain",
        "h119_mean_h085_cell_score",
        "h119_source_agree_rate",
        "h118_curv_marginal_vs_zero",
        "model_pred_delta_vs_h057",
        "route_basis_pred_delta_vs_h057",
        "h102_cum_bad_weighted_pos",
        "h102_cum_h088_axis_cos",
        "selected_mean_residual_toxicity",
        "selected_mean_residual_safety",
        "h118_mean_forbidden_same",
        "h118_mean_forbidden_pressure",
        "h118_h118_overlap_cells",
        "h118_h118_cosine",
        "h118_h115_overlap_cells",
        "h118_h115_cosine",
        "h118_h112_overlap_cells",
        "h118_h112_cosine",
        "h119_score",
        "file",
    ]
    report = f"""# H119 Observation-Equation Veto HS-JEPA

Question: can the H085 public-equation posterior become action-grade if it is
decoded only through H118's forbidden-sector veto and H102/H115 stress?

Filter audit:

{md_table(audit, 20)}

Candidates:

{md_table(candidates[cols], 20)}

Decision:

{md_table(pd.DataFrame([decision]), 1)}

Interpretation rule:

- If H119 improves, H085's hidden public-state posterior was real but needed an
  action-to-observation safety solver.
- If H119 loses while H118 improves, posterior gain is still contaminated and
  the safer assignment field should remain residual/nullspace based.
- If H119 and H118 both lose, forbidden-sector veto is diagnostic only and not
  sufficient for action decoding.
- If the tiny Q2 exception candidate wins later, Q2 needs a separate exception
  solver rather than a global veto.
"""
    (OUT / "h119_report.md").write_text(report, encoding="utf-8")

    print("H119 selected candidate")
    print(candidates[cols].head(10).to_string(index=False))
    print("\nDecision")
    print(pd.DataFrame([decision])[["decision", "selected_candidate_id", "root_uploadsafe_path", "root_upload_safe"]].to_string(index=False))


if __name__ == "__main__":
    run()
