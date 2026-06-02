#!/usr/bin/env python3
"""H110: toxicity-gap assignment solver HS-JEPA.

H108 trusted decoder-family agreement. H109 tried coefficient composition and
collapsed to a tiny H105 kernel. H110 separates the two quantities that those
experiments kept mixing:

    benefit:   independent decoders and frontier equations want this cell
    toxicity:  public-bad axes would punish this signed cell action

The solver scores signed row-target cells by benefit minus local toxicity, then
greedily builds a sparse assignment under the same cumulative public/private
bad-axis constraints used by H102-H109.
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
OUT = HITL / "h110_toxicity_gap_assignment_solver_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H109_PATH = HITL / "h109_decoder_coefficient_equation_solver_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h109mod", H109_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H109_PATH}")
h109mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h109mod
SPEC.loader.exec_module(h109mod)

h108mod = h109mod.h108mod
h102mod = h109mod.h102mod
h100mod = h109mod.h100mod
h097mod = h109mod.h097mod
h095mod = h109mod.h095mod
h085mod = h109mod.h085mod

TARGETS = h109mod.TARGETS
KEYS = h109mod.KEYS
BASE_FILE = h109mod.BASE_FILE
TOL = h109mod.TOL


@dataclass(frozen=True)
class H110Spec:
    name: str
    group: str
    max_cells: int
    max_rows: int
    max_per_subject: int
    max_per_target: int
    q2_cap: int
    amp: float
    cap: float
    min_score: float
    min_gap: float
    min_family_count: int
    min_family_consensus: float
    min_vote_weight: float
    max_local_toxicity: float
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
    for path in OUT.glob("submission_h110_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h110_toxgap_*.csv"):
        path.unlink()


def candidate_specs() -> list[H110Spec]:
    return [
        H110Spec(
            name="toxgap_jury_bridge_c82_a070",
            group="jury_bridge",
            max_cells=82,
            max_rows=42,
            max_per_subject=10,
            max_per_target=20,
            q2_cap=0,
            amp=0.70,
            cap=0.27,
            min_score=0.58,
            min_gap=0.18,
            min_family_count=3,
            min_family_consensus=0.58,
            min_vote_weight=2.0,
            max_local_toxicity=0.56,
            max_bad_weighted_pos=0.006,
            max_bad_max_pos=0.032,
            max_h088_cos=-0.003,
            min_good_margin=0.012,
            route_pred_cap=0.000100,
            h098_pred_cap=0.000080,
            worldview="H108 was broad because it mixed benefit and toxicity; keep only non-Q2 jury cells with positive toxicity gap",
        ),
        H110Spec(
            name="toxgap_kernel_release_c64_a085",
            group="kernel_release",
            max_cells=64,
            max_rows=30,
            max_per_subject=16,
            max_per_target=18,
            q2_cap=0,
            amp=0.85,
            cap=0.31,
            min_score=0.54,
            min_gap=0.12,
            min_family_count=2,
            min_family_consensus=0.58,
            min_vote_weight=1.1,
            max_local_toxicity=0.62,
            max_bad_weighted_pos=0.008,
            max_bad_max_pos=0.040,
            max_h088_cos=-0.002,
            min_good_margin=0.010,
            route_pred_cap=0.000100,
            h098_pred_cap=0.000085,
            worldview="H109 over-sharpened the H105 kernel; release nearby low-toxicity kernel cells instead of pure coefficient collapse",
        ),
        H110Spec(
            name="toxgap_objective_field_c120_a060",
            group="objective",
            max_cells=120,
            max_rows=66,
            max_per_subject=11,
            max_per_target=30,
            q2_cap=0,
            amp=0.60,
            cap=0.24,
            min_score=0.49,
            min_gap=0.10,
            min_family_count=2,
            min_family_consensus=0.48,
            min_vote_weight=0.95,
            max_local_toxicity=0.64,
            max_bad_weighted_pos=0.014,
            max_bad_max_pos=0.062,
            max_h088_cos=0.000,
            min_good_margin=0.004,
            route_pred_cap=0.000180,
            h098_pred_cap=0.000100,
            worldview="objective Q3/S cells are action-grade only when local toxicity is lower than decoder benefit",
        ),
        H110Spec(
            name="toxgap_broad_null_c140_a052",
            group="broad_null",
            max_cells=140,
            max_rows=74,
            max_per_subject=12,
            max_per_target=34,
            q2_cap=8,
            amp=0.52,
            cap=0.22,
            min_score=0.50,
            min_gap=0.08,
            min_family_count=2,
            min_family_consensus=0.44,
            min_vote_weight=0.75,
            max_local_toxicity=0.68,
            max_bad_weighted_pos=0.016,
            max_bad_max_pos=0.070,
            max_h088_cos=0.000,
            min_good_margin=0.002,
            route_pred_cap=0.000220,
            h098_pred_cap=0.000110,
            worldview="the hidden public equation is a broad low-toxicity nullspace field, not a tiny kernel",
        ),
        H110Spec(
            name="toxgap_q2_counter_c22_a045",
            group="q2_counter",
            max_cells=22,
            max_rows=22,
            max_per_subject=6,
            max_per_target=22,
            q2_cap=22,
            amp=0.45,
            cap=0.18,
            min_score=0.45,
            min_gap=0.06,
            min_family_count=2,
            min_family_consensus=0.42,
            min_vote_weight=0.55,
            max_local_toxicity=0.70,
            max_bad_weighted_pos=0.008,
            max_bad_max_pos=0.036,
            max_h088_cos=-0.002,
            min_good_margin=0.004,
            route_pred_cap=0.000260,
            h098_pred_cap=0.000090,
            worldview="Q2 can reopen only where the cell is anti-H088 and benefit-toxicity gap is positive",
        ),
    ]


def group_allowed(row: dict[str, object], group: str) -> bool:
    target = str(row["target"])
    if group == "jury_bridge":
        return target != "Q2" and int(row["h110_family_count"]) >= 3
    if group == "kernel_release":
        return target != "Q2" and (
            bool(row.get("h110_has_h105", False))
            or bool(row.get("h110_has_h106", False))
            or bool(row.get("h110_has_h109", False))
        )
    if group == "objective":
        return target in {"Q3", "S1", "S2", "S3", "S4"}
    if group == "broad_null":
        return True
    if group == "q2_counter":
        return target == "Q2" and float(row["h110_anti_h088"]) > 0.5
    raise ValueError(group)


def route_pred(move_flat: np.ndarray, basis_fit_df: pd.DataFrame, basis_fit_moves: np.ndarray, route_fit: h100mod.RouteBasisFit) -> float:
    return h100mod.predict_candidate_delta(move_flat, basis_fit_df, basis_fit_moves, route_fit)


def h098_pred(move_flat: np.ndarray, cell: pd.DataFrame, h098_fit: h097mod.ResponseFit) -> float:
    return h097mod.predict_candidate_delta(move_flat, cell, h098_fit)


def materialize(base_prob: np.ndarray, move_mat: np.ndarray) -> np.ndarray:
    return clip_prob(sigmoid(logit(base_prob) + move_mat))


def load_extended_sources(sample: pd.DataFrame, base_prob: np.ndarray, cell: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray, pd.DataFrame]:
    source, source_moves, jury = h109mod.load_sources(sample, base_prob, cell)
    source = source.copy()
    if "h109_source_weight" not in source.columns:
        source["h109_source_weight"] = source["weight"].astype(float)
    h109_path = ROOT / "submission_h109_coeff_54147083_uploadsafe.csv"
    if h109_path.exists():
        base_logit = logit(base_prob).reshape(-1)
        prob = h085mod.load_sub(h109_path, sample)[TARGETS].to_numpy(dtype=np.float64)
        move = logit(prob).reshape(-1) - base_logit
        if np.linalg.norm(move) > 1.0e-12:
            extra = {
                "family": "h109",
                "candidate_id": "h109_kernel_coeff_focus_c48_t7_54147083",
                "file": h109_path.name,
                "path": str(h109_path.resolve()),
                "weight": 1.38,
                "score_rank": 1.0,
                "score": 1.086708443,
                "route_basis_pred_delta_vs_h057": -0.001861699,
                "model_pred_delta_vs_h057": 0.000015065,
                "selected_cells": 4,
                "changed_rows_vs_h057": 2,
                "h109_source_weight": 1.38,
            }
            source = pd.concat([source, pd.DataFrame([extra])], ignore_index=True)
            source_moves = np.vstack([source_moves, move])
    return source.reset_index(drop=True), source_moves.astype(np.float64), jury


def add_dynamic_votes(jury: pd.DataFrame, source: pd.DataFrame, source_moves: np.ndarray) -> pd.DataFrame:
    weights = source["h109_source_weight"].to_numpy(dtype=np.float64)
    families = sorted(source["family"].astype(str).unique().tolist())
    n = len(jury)
    vote_sum = np.zeros(n, dtype=np.float64)
    vote_abs = np.zeros(n, dtype=np.float64)
    vote_weight = np.zeros(n, dtype=np.float64)
    vote_count = np.zeros(n, dtype=np.float64)
    family_sums = {family: np.zeros(n, dtype=np.float64) for family in families}

    for i, rec in source.reset_index(drop=True).iterrows():
        move = source_moves[i]
        active = np.abs(move) > 1.0e-10
        weight = float(weights[i])
        fam = str(rec["family"])
        vote_sum[active] += weight * move[active]
        vote_abs[active] += weight * np.abs(move[active])
        vote_weight[active] += weight
        vote_count[active] += 1.0
        family_sums[fam][active] += weight * move[active]

    family_mat = np.vstack([family_sums[family] for family in families]).astype(np.float64)
    family_active = np.abs(family_mat) > 1.0e-10
    family_count = family_active.sum(axis=0).astype(float)
    family_abs = np.abs(family_mat).sum(axis=0)
    family_sum = family_mat.sum(axis=0)
    family_consensus = np.abs(family_sum) / (family_abs + 1.0e-12)
    raw_mean = vote_sum / (vote_weight + 1.0e-12)

    out = jury.sort_values("flat_index").reset_index(drop=True).copy()
    out["h110_vote_sum"] = vote_sum
    out["h110_vote_abs"] = vote_abs
    out["h110_vote_weight"] = vote_weight
    out["h110_vote_count"] = vote_count
    out["h110_raw_mean_move"] = raw_mean
    out["h110_vote_consensus"] = np.abs(vote_sum) / (vote_abs + 1.0e-12)
    out["h110_family_count"] = family_count.astype(int)
    out["h110_family_consensus"] = family_consensus
    for family in families:
        arr = family_sums[family]
        out[f"h110_{family}_move"] = arr
        out[f"h110_has_{family}"] = np.abs(arr) > 1.0e-10
    sign = np.sign(raw_mean)
    h088_sign = np.sign(out["h088_logit_move"].to_numpy(dtype=np.float64))
    h057_sign = np.sign(out["h057_positive_logit_move"].to_numpy(dtype=np.float64))
    out["h110_anti_h088"] = (sign * h088_sign < 0).astype(float)
    out["h110_align_h057"] = (
        (sign * h057_sign > 0)
        & (out["h057_positive_weight"].to_numpy(dtype=np.float64) > 0)
    ).astype(float)
    return out


def add_local_toxicity(pool: pd.DataFrame, bad_axes: pd.DataFrame, bad_moves: np.ndarray, good_moves: np.ndarray) -> pd.DataFrame:
    out = pool.copy()
    flat = out["flat_index"].astype(int).to_numpy()
    sign = np.sign(out["h110_raw_mean_move"].to_numpy(dtype=np.float64))
    sign = np.where(sign == 0.0, np.sign(out["h108_raw_mean_move"].to_numpy(dtype=np.float64)), sign)
    bad_norm = np.maximum(np.linalg.norm(bad_moves, axis=1), 1.0e-12)
    good_norm = np.maximum(np.linalg.norm(good_moves, axis=1), 1.0e-12)
    bad_local = sign[:, None] * bad_moves[:, flat].T / bad_norm[None, :]
    good_local = sign[:, None] * good_moves[:, flat].T / good_norm[None, :]
    bad_w = bad_axes["weight"].to_numpy(dtype=np.float64)
    bad_pos = np.maximum(bad_local, 0.0)
    h088_mask = bad_axes["axis_name"].astype(str).eq(h095mod.H088_FILE).to_numpy()
    h088_local = bad_local[:, h088_mask][:, 0] if h088_mask.any() else np.zeros(len(out), dtype=np.float64)

    out["h110_local_bad_weighted_pos"] = (bad_pos * bad_w[None, :]).mean(axis=1)
    out["h110_local_bad_max_pos"] = bad_pos.max(axis=1)
    out["h110_local_h088_cos"] = h088_local
    out["h110_local_good_max"] = good_local.max(axis=1)
    out["h110_local_good_mean"] = good_local.mean(axis=1)
    out["h110_local_good_bad_gap"] = out["h110_local_good_max"] - out["h110_local_bad_weighted_pos"]

    benefit = (
        0.18 * rank01(np.abs(out["h110_raw_mean_move"].to_numpy(dtype=np.float64)), high=True)
        + 0.16 * rank01(out["h110_vote_weight"].to_numpy(dtype=np.float64), high=True)
        + 0.13 * rank01(out["h110_family_count"].to_numpy(dtype=np.float64), high=True)
        + 0.12 * out["h110_family_consensus"].to_numpy(dtype=np.float64)
        + 0.10 * out["h110_anti_h088"].to_numpy(dtype=np.float64)
        + 0.09 * out["h110_align_h057"].to_numpy(dtype=np.float64)
        + 0.08 * out["h057_h088_anti_conflict"].to_numpy(dtype=np.float64)
        + 0.07 * out["h095_safe_cell_score"].to_numpy(dtype=np.float64)
        + 0.06 * out["h098_frontier_cell_score"].to_numpy(dtype=np.float64)
        + 0.05 * out["h108_decoder_jury_score"].to_numpy(dtype=np.float64)
        + 0.04 * rank01(out["h110_local_good_max"].to_numpy(dtype=np.float64), high=True)
    )
    toxicity = (
        0.22 * rank01(out["h110_local_bad_weighted_pos"].to_numpy(dtype=np.float64), high=True)
        + 0.13 * rank01(out["h110_local_bad_max_pos"].to_numpy(dtype=np.float64), high=True)
        + 0.12 * np.maximum(out["h110_local_h088_cos"].to_numpy(dtype=np.float64), 0.0)
        + 0.12 * out["h080_bad_same_rank"].to_numpy(dtype=np.float64)
        + 0.10 * out["is_h050_null"].to_numpy(dtype=np.float64)
        + 0.09 * out["latent_shortcut_energy"].to_numpy(dtype=np.float64)
        + 0.08 * out["bad_pressure_rank"].to_numpy(dtype=np.float64)
        + 0.07 * out["h088_toxicity"].to_numpy(dtype=np.float64)
        + 0.05 * (1.0 - out["h110_family_consensus"].to_numpy(dtype=np.float64))
    )
    out["h110_benefit_score"] = benefit
    out["h110_toxicity_score"] = toxicity
    out["h110_benefit_toxicity_gap"] = benefit - toxicity
    out["h110_assignment_score"] = (
        np.abs(out["h110_raw_mean_move"].to_numpy(dtype=np.float64))
        * (0.65 + np.log1p(out["h110_vote_weight"].to_numpy(dtype=np.float64)))
        * (0.65 + out["h110_benefit_toxicity_gap"].to_numpy(dtype=np.float64))
        * (0.70 + 0.10 * out["h110_family_count"].to_numpy(dtype=np.float64))
    )
    return out


def select_cells(
    pool: pd.DataFrame,
    spec: H110Spec,
    base_shape: tuple[int, int],
    bad_axes: pd.DataFrame,
    bad_moves: np.ndarray,
    good_moves: np.ndarray,
) -> tuple[pd.DataFrame, np.ndarray]:
    work = pool.copy()
    work["h110_move"] = np.clip(work["h110_raw_mean_move"].to_numpy(dtype=np.float64) * spec.amp, -spec.cap, spec.cap)
    work = work[np.abs(work["h110_move"].to_numpy(dtype=np.float64)) > 1.0e-10]
    work = work[work["h110_assignment_score"].to_numpy(dtype=np.float64) >= spec.min_score * 1.0e-3]
    work = work[work["h110_benefit_toxicity_gap"].to_numpy(dtype=np.float64) >= spec.min_gap]
    work = work[work["h110_family_count"].astype(int) >= spec.min_family_count]
    work = work[work["h110_family_consensus"].to_numpy(dtype=np.float64) >= spec.min_family_consensus]
    work = work[work["h110_vote_weight"].to_numpy(dtype=np.float64) >= spec.min_vote_weight]
    work = work[work["h110_toxicity_score"].to_numpy(dtype=np.float64) <= spec.max_local_toxicity]
    work = work[work.apply(lambda row: group_allowed(row, spec.group), axis=1)]
    work = work.sort_values(["h110_benefit_toxicity_gap", "h110_assignment_score"], ascending=[False, False])

    selected_rows = []
    used_rows: set[int] = set()
    subject_counts: dict[str, int] = {}
    target_counts: dict[str, int] = {}
    q2_count = 0
    move_mat = np.zeros(base_shape, dtype=np.float64)

    for rec in work.to_dict("records"):
        if len(selected_rows) >= spec.max_cells:
            break
        row = int(rec["row"])
        subject = str(rec["subject_id"])
        target = str(rec["target"])
        if row not in used_rows and len(used_rows) >= spec.max_rows:
            continue
        if row not in used_rows and subject_counts.get(subject, 0) + 1 > spec.max_per_subject:
            continue
        if target_counts.get(target, 0) >= spec.max_per_target:
            continue
        if target == "Q2" and q2_count >= spec.q2_cap:
            continue

        tmp = move_mat.copy()
        tmp[row, int(rec["target_index"])] = float(rec["h110_move"])
        axis = h102mod.cumulative_axis_metrics(tmp.reshape(-1), bad_axes, bad_moves, good_moves)
        if axis["h102_cum_bad_weighted_pos"] > spec.max_bad_weighted_pos:
            continue
        if axis["h102_cum_bad_max_pos"] > spec.max_bad_max_pos:
            continue
        if axis["h102_cum_h088_axis_cos"] > spec.max_h088_cos:
            continue
        if axis["h102_cum_good_bad_margin"] < spec.min_good_margin:
            continue

        move_mat = tmp
        selected_rows.append(rec)
        if row not in used_rows:
            used_rows.add(row)
            subject_counts[subject] = subject_counts.get(subject, 0) + 1
        target_counts[target] = target_counts.get(target, 0) + 1
        if target == "Q2":
            q2_count += 1

    selected = pd.DataFrame(selected_rows)
    if selected.empty:
        return selected, move_mat
    selected = selected.sort_values(["row", "target_index"]).reset_index(drop=True)
    selected["h097_move_col"] = "h110_move"
    return selected, move_mat


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
    bad_axes: pd.DataFrame,
    bad_moves: np.ndarray,
    good_moves: np.ndarray,
    spec: H110Spec,
    path: Path,
) -> dict[str, object]:
    proxy = h097mod.H097Spec(
        name=spec.name,
        mode="toxicity_gap_assignment_solver",
        target_group=spec.group,
        k=spec.max_cells,
        alpha=spec.amp,
        cap=spec.cap,
        min_score=spec.min_gap,
        worldview=spec.worldview,
    )
    out = h097mod.evaluate_candidate(candidate_id, prob, move_mat, base_prob, selected_cells, cell, sample, h098_fit, proxy, path)
    axis = h102mod.cumulative_axis_metrics(move_mat.reshape(-1), bad_axes, bad_moves, good_moves)
    out.update(axis)
    out["route_basis_pred_delta_vs_h057"] = route_pred(move_mat.reshape(-1), basis_fit_df, basis_fit_moves, route_fit)
    out["selected_mean_benefit"] = float(selected_cells["h110_benefit_score"].mean()) if len(selected_cells) else 0.0
    out["selected_mean_toxicity"] = float(selected_cells["h110_toxicity_score"].mean()) if len(selected_cells) else 0.0
    out["selected_mean_gap"] = float(selected_cells["h110_benefit_toxicity_gap"].mean()) if len(selected_cells) else 0.0
    out["selected_mean_local_bad"] = float(selected_cells["h110_local_bad_weighted_pos"].mean()) if len(selected_cells) else 0.0
    out["selected_mean_local_good"] = float(selected_cells["h110_local_good_max"].mean()) if len(selected_cells) else 0.0
    out["selected_mean_family_count"] = float(selected_cells["h110_family_count"].mean()) if len(selected_cells) else 0.0
    out["selected_mean_family_consensus"] = float(selected_cells["h110_family_consensus"].mean()) if len(selected_cells) else 0.0
    out["selected_mean_vote_weight"] = float(selected_cells["h110_vote_weight"].mean()) if len(selected_cells) else 0.0
    out["selected_h109_cells"] = int(selected_cells["h110_has_h109"].sum()) if "h110_has_h109" in selected_cells.columns else 0
    out["h110_score"] = (
        150.0 * (-float(out["model_pred_delta_vs_h057"]))
        + 115.0 * (-float(out["route_basis_pred_delta_vs_h057"]))
        + 0.20 * float(out["anti_h088_direction_rate"])
        + 0.18 * float(out["h057_positive_align_rate"])
        + 0.16 * float(out["selected_conflict_rate"])
        + 0.16 * max(float(out["selected_mean_gap"]), 0.0)
        + 0.10 * float(out["selected_mean_benefit"])
        + 0.08 * min(float(out["selected_mean_family_count"]) / 4.0, 1.0)
        + 0.08 * float(out["selected_mean_family_consensus"])
        + 0.06 * max(float(out["h102_cum_good_bad_margin"]), 0.0)
        + 0.05 * max(-float(out["h102_cum_h088_axis_cos"]), 0.0)
        - 0.22 * float(out["selected_mean_toxicity"])
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
    cell, h098_fit, route_fit, basis_fit_df, basis_fit_moves, bad_axes, bad_moves, good_axes, good_moves = h109mod.build_context()
    source, source_moves, jury = load_extended_sources(sample, base_prob, cell)
    pool = add_dynamic_votes(jury, source, source_moves)
    pool = add_local_toxicity(pool, bad_axes, bad_moves, good_moves)

    candidate_rows = []
    selected_frames = []
    top_frames = []
    for spec in candidate_specs():
        selected_cells, move_mat = select_cells(pool, spec, base_prob.shape, bad_axes, bad_moves, good_moves)
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
        candidate_id = safe_id(f"h110_{spec.name}_{hash_id}", 128)
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
            bad_axes,
            bad_moves,
            good_moves,
            spec,
            path,
        )
        candidate_rows.append(metrics)
        selected_cells = selected_cells.copy()
        selected_cells.insert(0, "candidate_id", candidate_id)
        selected_frames.append(selected_cells)
        top = pool.sort_values(["h110_benefit_toxicity_gap", "h110_assignment_score"], ascending=[False, False]).head(320).copy()
        top.insert(0, "candidate_id", candidate_id)
        top_frames.append(top)

    candidates = pd.DataFrame(candidate_rows)
    if candidates.empty:
        raise RuntimeError("no H110 candidates")
    candidates = candidates.sort_values(["h110_score", "model_pred_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True)
    selected = candidates.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"submission_h110_toxgap_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)

    decision = {
        "decision": "promote_h110_toxicity_gap_assignment_solver",
        "selected_candidate_id": selected["candidate_id"],
        "root_uploadsafe_path": str(root_path.resolve()),
        "worldview": selected["worldview"],
        "source_candidates": int(len(source)),
        "source_families": ",".join(sorted(source["family"].unique().tolist())),
        "h098_feature_set": h098_fit.feature_set,
        "h098_alpha": h098_fit.alpha,
        **selected,
        **{f"root_{key}": value for key, value in validation.items()},
    }

    source.to_csv(OUT / "h110_source_candidates.csv", index=False)
    pool.to_csv(OUT / "h110_toxicity_pool.csv", index=False)
    candidates.to_csv(OUT / "h110_candidates.csv", index=False)
    pd.concat(selected_frames, ignore_index=True).to_csv(OUT / "h110_selected_cells.csv", index=False)
    pd.concat(top_frames, ignore_index=True).to_csv(OUT / "h110_top_toxicity_gap_cells.csv", index=False)
    bad_axes.to_csv(OUT / "h110_bad_axes.csv", index=False)
    pd.DataFrame([decision]).to_csv(OUT / "h110_decision.csv", index=False)

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
        "selected_mean_benefit",
        "selected_mean_toxicity",
        "selected_mean_gap",
        "selected_mean_family_count",
        "selected_h109_cells",
        "h110_score",
        "file",
    ]
    report = f"""# H110 Toxicity-Gap Assignment Solver HS-JEPA

Question: can HS-JEPA separate row-target benefit from public-action toxicity
before assigning cells?

Source candidates:

{md_table(source[["family", "candidate_id", "h109_source_weight", "route_basis_pred_delta_vs_h057", "model_pred_delta_vs_h057"]], 40)}

Candidates:

{md_table(candidates[cols], 20)}

Decision:

{md_table(pd.DataFrame([decision]), 1)}

Interpretation rule:

- If H110 improves over H108, the missing action decoder is benefit-toxicity
  factorization, not raw decoder-family intersection.
- If H108 improves more, local toxicity scoring over-pruned useful cells.
- If H109 improves more, the true public-safe action remains a tiny kernel.
- If all H108-H110 lose, H103-H109 decoder witnesses are diagnostic only and a
  new public subset sensor is required.
"""
    (OUT / "h110_report.md").write_text(report, encoding="utf-8")

    print(f"selected={decision['selected_candidate_id']}")
    print(f"root={root_path}")
    print(candidates[cols].head(10).to_string(index=False))


if __name__ == "__main__":
    run()
