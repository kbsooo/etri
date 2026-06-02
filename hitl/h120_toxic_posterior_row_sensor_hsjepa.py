#!/usr/bin/env python3
"""H120: toxic-posterior row-sensor HS-JEPA.

H119 showed that directly moving toward the H085 public posterior is not
action-grade: every high-confidence posterior move points into the H088-positive
toxic axis.  H120 changes H085's role.

    H085 posterior gain -> row/context sensor
    H118/H112 residual-veto field -> action solver

The experiment tests whether H085 is useful for locating public-sensitive
rows even when its local target direction is toxic.
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
OUT = HITL / "h120_toxic_posterior_row_sensor_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H119_PATH = HITL / "h119_observation_equation_veto_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h119mod", H119_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H119_PATH}")
h119mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h119mod
SPEC.loader.exec_module(h119mod)

h118mod = h119mod.h118mod
h117mod = h119mod.h117mod
h115mod = h119mod.h115mod
h112mod = h119mod.h112mod
h102mod = h119mod.h102mod
h100mod = h119mod.h100mod
h097mod = h119mod.h097mod
h085mod = h119mod.h085mod

TARGETS = h119mod.TARGETS
TOL = h119mod.TOL


@dataclass(frozen=True)
class H120Spec:
    name: str
    group: str
    max_cells: int
    max_rows: int
    max_per_subject: int
    max_per_target: int
    amp: float
    cap: float
    pool_top: int
    min_row_sensor_rank: float
    min_row_sensor_raw: float
    min_residual_safety: float
    max_residual_toxicity: float
    min_residual_gap: float
    min_h118_score_base: float
    require_h085_contra: bool
    max_h085_action_align_rate: float
    max_curv_marginal: float
    max_marginal_add: float
    max_bad_weighted_pos: float
    max_bad_max_pos: float
    max_h088_cos: float
    min_good_margin: float
    route_pred_cap: float
    h098_pred_cap: float
    worldview: str

    @property
    def min_score(self) -> float:
        return self.min_h118_score_base


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


def rank01(values: np.ndarray, high: bool = True) -> np.ndarray:
    return h085mod.rank01(np.asarray(values, dtype=np.float64), high=high)


def materialize(base_prob: np.ndarray, move_mat: np.ndarray) -> np.ndarray:
    return clip_prob(sigmoid(logit(base_prob) + move_mat))


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h120_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h120_toxrow_*.csv"):
        path.unlink()


def route_pred(move_flat: np.ndarray, basis_fit_df: pd.DataFrame, basis_fit_moves: np.ndarray, route_fit: h100mod.RouteBasisFit) -> float:
    return h100mod.predict_candidate_delta(move_flat, basis_fit_df, basis_fit_moves, route_fit)


def h098_pred(move_flat: np.ndarray, cell: pd.DataFrame, h098_fit: h097mod.ResponseFit) -> float:
    return h097mod.predict_candidate_delta(move_flat, cell, h098_fit)


def curvature_pred(move_mat: np.ndarray, fit: h115mod.CurvatureFit, pool: pd.DataFrame, bad_axes: pd.DataFrame, bad_moves: np.ndarray, good_moves: np.ndarray, axes: dict[str, object]) -> float:
    return h115mod.predict_curvature(move_mat, fit, pool, bad_axes, bad_moves, good_moves, axes)


def candidate_specs() -> list[H120Spec]:
    return [
        H120Spec(
            name="toxrow_contra_core_c48_a052",
            group="contra_core",
            max_cells=48,
            max_rows=28,
            max_per_subject=7,
            max_per_target=15,
            amp=0.52,
            cap=0.18,
            pool_top=180,
            min_row_sensor_rank=0.54,
            min_row_sensor_raw=0.0012,
            min_residual_safety=0.53,
            max_residual_toxicity=0.56,
            min_residual_gap=0.05,
            min_h118_score_base=0.12,
            require_h085_contra=True,
            max_h085_action_align_rate=0.35,
            max_curv_marginal=0.000050,
            max_marginal_add=0.000022,
            max_bad_weighted_pos=0.020,
            max_bad_max_pos=0.080,
            max_h088_cos=0.0,
            min_good_margin=0.0,
            route_pred_cap=0.000130,
            h098_pred_cap=0.000100,
            worldview="H085 locates toxic-public rows; action must be residual-safe and usually opposite to H085's local posterior direction",
        ),
        H120Spec(
            name="toxrow_stage_bridge_c56_a046",
            group="stage_bridge",
            max_cells=56,
            max_rows=34,
            max_per_subject=9,
            max_per_target=17,
            amp=0.46,
            cap=0.17,
            pool_top=210,
            min_row_sensor_rank=0.46,
            min_row_sensor_raw=0.0008,
            min_residual_safety=0.49,
            max_residual_toxicity=0.60,
            min_residual_gap=0.02,
            min_h118_score_base=0.10,
            require_h085_contra=False,
            max_h085_action_align_rate=0.60,
            max_curv_marginal=0.000055,
            max_marginal_add=0.000024,
            max_bad_weighted_pos=0.020,
            max_bad_max_pos=0.080,
            max_h088_cos=0.0,
            min_good_margin=0.0,
            route_pred_cap=0.000160,
            h098_pred_cap=0.000115,
            worldview="public-sensitive rows marked by H085 should be corrected through Q/S stage-balance residual actions",
        ),
        H120Spec(
            name="toxrow_h112_anchor_c40_a058",
            group="h112_anchor",
            max_cells=40,
            max_rows=24,
            max_per_subject=7,
            max_per_target=14,
            amp=0.58,
            cap=0.18,
            pool_top=150,
            min_row_sensor_rank=0.50,
            min_row_sensor_raw=0.0010,
            min_residual_safety=0.56,
            max_residual_toxicity=0.54,
            min_residual_gap=0.08,
            min_h118_score_base=0.14,
            require_h085_contra=False,
            max_h085_action_align_rate=0.50,
            max_curv_marginal=0.000045,
            max_marginal_add=0.000020,
            max_bad_weighted_pos=0.020,
            max_bad_max_pos=0.080,
            max_h088_cos=0.0,
            min_good_margin=0.0,
            route_pred_cap=0.000120,
            h098_pred_cap=0.000095,
            worldview="only H112 residual anchors on H085-public-sensitive rows are action-grade",
        ),
        H120Spec(
            name="toxrow_h114_null_c42_a054",
            group="h114_null",
            max_cells=42,
            max_rows=30,
            max_per_subject=8,
            max_per_target=14,
            amp=0.54,
            cap=0.18,
            pool_top=160,
            min_row_sensor_rank=0.42,
            min_row_sensor_raw=0.0007,
            min_residual_safety=0.50,
            max_residual_toxicity=0.58,
            min_residual_gap=0.03,
            min_h118_score_base=0.10,
            require_h085_contra=False,
            max_h085_action_align_rate=0.58,
            max_curv_marginal=0.000050,
            max_marginal_add=0.000022,
            max_bad_weighted_pos=0.020,
            max_bad_max_pos=0.080,
            max_h088_cos=0.0,
            min_good_margin=0.0,
            route_pred_cap=0.000145,
            h098_pred_cap=0.000105,
            worldview="toxic-posterior rows need toxic-nullspace actions rather than posterior actions",
        ),
        H120Spec(
            name="toxrow_sparse_highsensor_c26_a060",
            group="all_safe",
            max_cells=26,
            max_rows=20,
            max_per_subject=5,
            max_per_target=10,
            amp=0.60,
            cap=0.18,
            pool_top=100,
            min_row_sensor_rank=0.70,
            min_row_sensor_raw=0.0020,
            min_residual_safety=0.52,
            max_residual_toxicity=0.58,
            min_residual_gap=0.04,
            min_h118_score_base=0.12,
            require_h085_contra=False,
            max_h085_action_align_rate=0.50,
            max_curv_marginal=0.000045,
            max_marginal_add=0.000020,
            max_bad_weighted_pos=0.020,
            max_bad_max_pos=0.080,
            max_h088_cos=0.0,
            min_good_margin=0.0,
            route_pred_cap=0.000120,
            h098_pred_cap=0.000095,
            worldview="a sparse set of the strongest H085 row sensors can route residual actions safely",
        ),
    ]


def annotate_toxic_row_sensor(scored: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    out = scored.copy()
    qmove = out["h085_q_move"].to_numpy(dtype=np.float64)
    prop = out["proposal_move"].to_numpy(dtype=np.float64)
    posterior_align = ((np.sign(qmove) * np.sign(prop) > 0) & (np.abs(qmove) > 1.0e-12)).astype(float)
    toxic_mask = (
        out["target"].astype(str).ne("Q2").to_numpy()
        & (out["h117_forbidden_same"].to_numpy(dtype=np.float64) <= 1.0e-12)
        & (out["h117_forbidden_pressure"].to_numpy(dtype=np.float64) <= 0.0)
        & (out["source_agrees_h085"].to_numpy(dtype=np.float64) > 0.5)
        & (out["h085_q_gain"].to_numpy(dtype=np.float64) >= 0.0002)
        & (out["h085_cell_score"].to_numpy(dtype=np.float64) >= 0.35)
        & (posterior_align > 0.5)
    )
    out["h120_h085_action_align"] = posterior_align
    out["h120_h085_action_contra"] = (
        (np.sign(qmove) * np.sign(prop) < 0) & (np.abs(qmove) > 1.0e-12)
    ).astype(float)
    out["h120_toxic_posterior_cell"] = toxic_mask.astype(float)
    out["h120_toxic_cell_weight"] = np.where(
        toxic_mask,
        out["h085_q_gain"].to_numpy(dtype=np.float64)
        * (0.35 + out["h085_cell_score"].to_numpy(dtype=np.float64))
        * (0.5 + out["h088_toxicity"].to_numpy(dtype=np.float64)),
        0.0,
    )
    row = (
        out.groupby("row", as_index=False)
        .agg(
            h120_row_sensor_raw=("h120_toxic_cell_weight", "sum"),
            h120_row_sensor_cells=("h120_toxic_posterior_cell", "sum"),
            h120_row_sensor_max_gain=("h085_q_gain", "max"),
            h120_row_sensor_mean_h088=("h088_toxicity", "mean"),
        )
    )
    row["h120_row_sensor_rank"] = rank01(row["h120_row_sensor_raw"].to_numpy(dtype=np.float64), high=True)
    out = out.merge(row, on="row", how="left")
    for col in ["h120_row_sensor_raw", "h120_row_sensor_cells", "h120_row_sensor_max_gain", "h120_row_sensor_mean_h088", "h120_row_sensor_rank"]:
        out[col] = out[col].fillna(0.0)
    out["h120_sensor_action_score"] = (
        0.25 * out["h118_score_base"].to_numpy(dtype=np.float64)
        + 0.19 * out["h120_row_sensor_rank"].to_numpy(dtype=np.float64)
        + 0.16 * rank01(out["h120_row_sensor_raw"].to_numpy(dtype=np.float64), high=True)
        + 0.14 * rank01(out["h112_residual_safety"].to_numpy(dtype=np.float64), high=True)
        + 0.11 * rank01(out["h112_residual_gap"].to_numpy(dtype=np.float64), high=True)
        + 0.08 * out["h118_forbidden_veto_score"].to_numpy(dtype=np.float64)
        + 0.06 * out["h120_h085_action_contra"].to_numpy(dtype=np.float64)
        - 0.16 * rank01(out["h112_residual_toxicity"].to_numpy(dtype=np.float64), high=True)
        - 0.10 * out["h120_h085_action_align"].to_numpy(dtype=np.float64)
    )
    return out, row.sort_values("h120_row_sensor_raw", ascending=False).reset_index(drop=True)


def target_allowed(work: pd.DataFrame, spec: H120Spec) -> np.ndarray:
    target = work["target"].astype(str)
    src = work["proposal_source"].astype(str)
    base = target.ne("Q2").to_numpy()
    if spec.group == "contra_core":
        return base & work["h120_h085_action_contra"].astype(float).gt(0.5).to_numpy()
    if spec.group == "stage_bridge":
        return target.isin(["Q3", "S1", "S2", "S3", "S4"]).to_numpy()
    if spec.group == "h112_anchor":
        return base & (
            src.str.contains("h112", regex=False).to_numpy()
            | work["h112_in_h111_selected"].astype(float).gt(0.5).to_numpy()
        )
    if spec.group == "h114_null":
        return base & (
            src.str.contains("h114", regex=False).to_numpy()
            | work["h114_null_move"].fillna(0.0).astype(float).abs().gt(1.0e-12).to_numpy()
        )
    if spec.group == "all_safe":
        return base
    raise ValueError(spec.group)


def select_cells(
    scored: pd.DataFrame,
    spec: H120Spec,
    shape: tuple[int, int],
    fit: h115mod.CurvatureFit,
    pool: pd.DataFrame,
    bad_axes: pd.DataFrame,
    bad_moves: np.ndarray,
    good_moves: np.ndarray,
    axes: dict[str, object],
) -> tuple[pd.DataFrame, np.ndarray, dict[str, float], dict[str, float]]:
    work = scored[target_allowed(scored, spec)].copy()
    work = work[work["h117_forbidden_same"].to_numpy(dtype=np.float64) <= 1.0e-12].copy()
    work = work[work["h117_forbidden_pressure"].to_numpy(dtype=np.float64) <= 0.02].copy()
    work = work[work["h120_row_sensor_rank"].to_numpy(dtype=np.float64) >= spec.min_row_sensor_rank].copy()
    work = work[work["h120_row_sensor_raw"].to_numpy(dtype=np.float64) >= spec.min_row_sensor_raw].copy()
    work = work[work["h112_residual_safety"].to_numpy(dtype=np.float64) >= spec.min_residual_safety].copy()
    work = work[work["h112_residual_toxicity"].to_numpy(dtype=np.float64) <= spec.max_residual_toxicity].copy()
    work = work[work["h112_residual_gap"].to_numpy(dtype=np.float64) >= spec.min_residual_gap].copy()
    work = work[work["h118_score_base"].to_numpy(dtype=np.float64) >= spec.min_h118_score_base].copy()
    if spec.require_h085_contra:
        work = work[work["h120_h085_action_contra"].to_numpy(dtype=np.float64) > 0.5].copy()
    if work.empty:
        return pd.DataFrame(), np.zeros(shape, dtype=np.float64), {}, {}

    work["h120_move"] = np.clip(work["proposal_move"].to_numpy(dtype=np.float64) * spec.amp, -spec.cap, spec.cap)
    work = work[np.abs(work["h120_move"].to_numpy(dtype=np.float64)) > 1.0e-12].copy()
    if work.empty:
        return pd.DataFrame(), np.zeros(shape, dtype=np.float64), {}, {}
    work["h120_cell_score"] = (
        0.30 * work["h120_sensor_action_score"].to_numpy(dtype=np.float64)
        + 0.18 * rank01(work["h120_row_sensor_raw"].to_numpy(dtype=np.float64), high=True)
        + 0.15 * rank01(work["h112_residual_safety"].to_numpy(dtype=np.float64), high=True)
        + 0.12 * rank01(work["h112_residual_gap"].to_numpy(dtype=np.float64), high=True)
        + 0.10 * rank01(np.abs(work["h120_move"].to_numpy(dtype=np.float64)), high=True)
        + 0.08 * rank01(work["h112_antidote_score"].to_numpy(dtype=np.float64), high=True)
        + 0.06 * work["h120_h085_action_contra"].to_numpy(dtype=np.float64)
        - 0.18 * rank01(work["h112_residual_toxicity"].to_numpy(dtype=np.float64), high=True)
        - 0.10 * work["h120_h085_action_align"].to_numpy(dtype=np.float64)
    )
    work = work.sort_values(["h120_cell_score", "h120_row_sensor_raw"], ascending=[False, False])
    work = work.drop_duplicates(["row", "target"], keep="first").head(spec.pool_top).reset_index(drop=True)

    move_mat = np.zeros(shape, dtype=np.float64)
    zero_curv = curvature_pred(move_mat, fit, pool, bad_axes, bad_moves, good_moves, axes)
    curv_now = zero_curv
    selected_idx = []
    selected_flat: set[int] = set()
    selected_rows: set[int] = set()
    subject_counts: dict[str, int] = {}
    target_counts: dict[str, int] = {}
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
        if row not in selected_rows and len(selected_rows) >= spec.max_rows:
            continue
        if row not in selected_rows and subject_counts.get(subject, 0) + 1 > spec.max_per_subject:
            continue
        if target_counts.get(target, 0) >= spec.max_per_target:
            continue
        tmp = move_mat.copy()
        tmp[row, tidx] = float(rec["h120_move"])
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
        "h120_mean_row_sensor_raw": float(selected["h120_row_sensor_raw"].mean()),
        "h120_mean_row_sensor_rank": float(selected["h120_row_sensor_rank"].mean()),
        "h120_mean_row_sensor_cells": float(selected["h120_row_sensor_cells"].mean()),
        "h120_h085_action_align_rate": float(selected["h120_h085_action_align"].mean()),
        "h120_h085_action_contra_rate": float(selected["h120_h085_action_contra"].mean()),
        "h120_mean_h085_q_gain": float(selected["h085_q_gain"].mean()),
        "h120_mean_h085_cell_score": float(selected["h085_cell_score"].mean()),
    }
    return selected, move_mat, axis, diag


def run() -> None:
    cleanup_previous_outputs()
    pool, _public, sample, base_prob, cell, h098_fit, route_fit, basis_fit_df, basis_fit_moves, bad_axes, bad_moves, good_moves, axes, fit, model_scores, props = h118mod.prepare_context()
    forbidden_axes, forbidden_weights, forbidden_audit = h117mod.build_forbidden_axes(props, base_prob.shape, fit, pool, bad_axes, bad_moves, good_moves, axes)
    scored_raw = h117mod.annotate_forbidden_scores(props, forbidden_axes, forbidden_weights)
    scored = h119mod.annotate_observation_scores(h118mod.annotate_veto_scores(scored_raw))
    scored, row_sensor = annotate_toxic_row_sensor(scored)
    previous = {
        "h118": h115mod.load_previous_move(sample, base_prob, "submission_h118_forbiddenveto_*_uploadsafe.csv"),
        "h115": h115mod.load_previous_move(sample, base_prob, "submission_h115_curvature_*_uploadsafe.csv"),
        "h114": h115mod.load_previous_move(sample, base_prob, "submission_h114_nullspace_*_uploadsafe.csv"),
        "h113": h115mod.load_previous_move(sample, base_prob, "submission_h113_rowroute_*_uploadsafe.csv"),
        "h112": h115mod.load_previous_move(sample, base_prob, "submission_h112_residualtox_*_uploadsafe.csv"),
        "h107": h115mod.load_previous_move(sample, base_prob, "submission_h107_antipode_*_uploadsafe.csv"),
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
                "row_sensor_rank_pass": int((pre["h120_row_sensor_rank"].to_numpy(dtype=np.float64) >= spec.min_row_sensor_rank).sum()),
                "row_sensor_raw_pass": int((pre["h120_row_sensor_raw"].to_numpy(dtype=np.float64) >= spec.min_row_sensor_raw).sum()),
                "residual_safety_pass": int((pre["h112_residual_safety"].to_numpy(dtype=np.float64) >= spec.min_residual_safety).sum()),
                "residual_toxicity_pass": int((pre["h112_residual_toxicity"].to_numpy(dtype=np.float64) <= spec.max_residual_toxicity).sum()),
                "h118_score_pass": int((pre["h118_score_base"].to_numpy(dtype=np.float64) >= spec.min_h118_score_base).sum()),
            }
        )
        selected, move_mat, axis, diag = select_cells(scored, spec, base_prob.shape, fit, pool, bad_axes, bad_moves, good_moves, axes)
        if selected.empty:
            continue
        rpred = route_pred(move_mat.reshape(-1), basis_fit_df, basis_fit_moves, route_fit)
        cpred = h098_pred(move_mat.reshape(-1), cell, h098_fit)
        if rpred > spec.route_pred_cap or cpred > spec.h098_pred_cap:
            continue
        if diag["h120_h085_action_align_rate"] > spec.max_h085_action_align_rate:
            continue
        prob = materialize(base_prob, move_mat)
        if int((np.abs(prob - base_prob) > TOL).sum()) == 0:
            continue
        hash_id = short_hash(prob)
        candidate_id = safe_id(f"h120_{spec.name}_{hash_id}", 128)
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
        metrics["h120_fit_feature_set"] = fit.feature_set
        metrics["h120_fit_alpha"] = fit.alpha
        metrics["h120_fit_score"] = fit.score
        metrics["h120_forbidden_axes"] = int(len(forbidden_axes))
        metrics["h120_score"] = (
            320.0 * (-float(metrics["route_basis_pred_delta_vs_h057"]))
            + 100.0 * (-float(metrics["model_pred_delta_vs_h057"]))
            + 85.0 * (-float(metrics["h118_curv_marginal_vs_zero"]))
            + 0.004 * float(metrics["selected_cells"])
            + 0.19 * float(metrics["selected_mean_residual_safety"])
            + 0.18 * float(metrics["selected_mean_residual_gap"])
            + 0.18 * float(metrics["h120_mean_row_sensor_rank"])
            + 0.12 * float(metrics["h120_h085_action_contra_rate"])
            + 0.08 * max(-float(metrics["h102_cum_h088_axis_cos"]), 0.0)
            - 0.18 * float(metrics["selected_mean_residual_toxicity"])
            - 0.10 * float(metrics["h120_h085_action_align_rate"])
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
    forbidden_audit.to_csv(OUT / "h120_forbidden_axes.csv", index=False)
    row_sensor.to_csv(OUT / "h120_row_sensor.csv", index=False)
    audit.to_csv(OUT / "h120_filter_audit.csv", index=False)
    scored.to_csv(OUT / "h120_scored_proposals.csv", index=False)
    model_scores.to_csv(OUT / "h120_curvature_model_scores.csv", index=False)

    if candidates.empty:
        report = f"""# H120 Toxic-Posterior Row-Sensor HS-JEPA

No candidate was promoted.

Filter audit:

{md_table(audit, 20)}

Top row sensors:

{md_table(row_sensor.head(20), 20)}
"""
        (OUT / "h120_report.md").write_text(report, encoding="utf-8")
        print("H120 promoted no candidate")
        print(audit.to_string(index=False))
        return

    candidates = candidates.sort_values(["h120_score", "route_basis_pred_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True)
    selected = candidates.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"submission_h120_toxrow_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)
    decision = {
        "decision": "promote_h120_toxic_posterior_row_sensor",
        "selected_candidate_id": selected["candidate_id"],
        "root_uploadsafe_path": str(root_path),
        "worldview": selected["worldview"],
        **selected,
        **{f"root_{key}": value for key, value in validation.items()},
    }

    candidates.to_csv(OUT / "h120_candidates.csv", index=False)
    pd.concat(selected_frames, ignore_index=True).to_csv(OUT / "h120_selected_cells.csv", index=False)
    pd.DataFrame([decision]).to_csv(OUT / "h120_decision.csv", index=False)

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
        "model_pred_delta_vs_h057",
        "route_basis_pred_delta_vs_h057",
        "h118_curv_marginal_vs_zero",
        "h102_cum_bad_weighted_pos",
        "h102_cum_h088_axis_cos",
        "h102_cum_good_bad_margin",
        "selected_mean_residual_toxicity",
        "selected_mean_residual_safety",
        "selected_mean_residual_gap",
        "h120_mean_row_sensor_rank",
        "h120_h085_action_align_rate",
        "h120_h085_action_contra_rate",
        "h120_mean_h085_q_gain",
        "h120_score",
        "file",
    ]
    report = f"""# H120 Toxic-Posterior Row-Sensor HS-JEPA

Question: after H119 failed, can H085 still be useful as a row-level public
sensor if the actual action is decoded by H118/H112 residual safety?

Filter audit:

{md_table(audit, 20)}

Top row sensors:

{md_table(row_sensor.head(20), 20)}

Candidates:

{md_table(candidates[cols], 20)}

Decision:

{md_table(pd.DataFrame([decision]), 1)}

Interpretation rule:

- If H120 improves, H085 is not an action target; it is a row/context sensor.
- If H120 loses while H118 improves, H085 row localization is contaminated and
  action should remain residual/nullspace only.
- If both H118 and H120 lose, the current public/private solver is still using
  the wrong observation equation.
"""
    (OUT / "h120_report.md").write_text(report, encoding="utf-8")

    print("H120 selected candidate")
    print(candidates[cols].head(10).to_string(index=False))
    print("\nDecision")
    print(pd.DataFrame([decision])[["decision", "selected_candidate_id", "root_uploadsafe_path", "root_upload_safe"]].to_string(index=False))


if __name__ == "__main__":
    run()
