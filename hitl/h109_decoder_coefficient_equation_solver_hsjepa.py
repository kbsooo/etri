#!/usr/bin/env python3
"""H109: decoder-coefficient equation solver HS-JEPA.

H108 asked for cell-level agreement among decoder families.  H109 asks a
different question:

    can complete decoder submissions be basis vectors of one public/private
    action equation?

It solves a coefficient equation over H103-H108 source action vectors, projects
or constrains toxic components, then decodes the resulting dense field back
into sparse row-target assignments.
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
OUT = HITL / "h109_decoder_coefficient_equation_solver_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H108_PATH = HITL / "h108_decoder_jury_assignment_solver_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h108mod", H108_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H108_PATH}")
h108mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h108mod
SPEC.loader.exec_module(h108mod)

h107mod = h108mod.h107mod
h106mod = h108mod.h106mod
h105mod = h108mod.h105mod
h104mod = h108mod.h104mod
h103mod = h108mod.h103mod
h102mod = h108mod.h102mod
h100mod = h108mod.h100mod
h099mod = h108mod.h099mod
h098mod = h108mod.h098mod
h097mod = h108mod.h097mod
h095mod = h108mod.h095mod
h085mod = h108mod.h085mod

TARGETS = h108mod.TARGETS
KEYS = h108mod.KEYS
BASE_FILE = h108mod.BASE_FILE
TOL = h108mod.TOL


@dataclass(frozen=True)
class H109Spec:
    name: str
    group: str
    source_families: tuple[str, ...]
    coeffs: tuple[float, ...]
    max_terms: int
    max_cells: int
    max_rows: int
    max_per_subject: int
    max_per_target: int
    q2_cap: int
    field_cap: float
    cell_cap: float
    min_abs_move: float
    min_family_count: int
    min_family_consensus: float
    min_vote_weight: float
    max_bad_weighted_pos: float
    max_bad_max_pos: float
    max_h088_cos: float
    min_good_margin: float
    route_pred_cap: float
    h098_pred_cap: float
    residualize_bad_axes: bool
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
    for path in OUT.glob("submission_h109_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h109_coeff_*.csv"):
        path.unlink()


def candidate_specs() -> list[H109Spec]:
    return [
        H109Spec(
            name="strict_coeff_null_c60_t8_a",
            group="nonq2_strict",
            source_families=("h103", "h104", "h105", "h106", "h108"),
            coeffs=(0.22, 0.34, 0.46, 0.58),
            max_terms=8,
            max_cells=60,
            max_rows=34,
            max_per_subject=8,
            max_per_target=16,
            q2_cap=0,
            field_cap=0.42,
            cell_cap=0.30,
            min_abs_move=0.012,
            min_family_count=3,
            min_family_consensus=0.62,
            min_vote_weight=2.2,
            max_bad_weighted_pos=0.004,
            max_bad_max_pos=0.026,
            max_h088_cos=-0.004,
            min_good_margin=0.016,
            route_pred_cap=0.000120,
            h098_pred_cap=0.000075,
            residualize_bad_axes=False,
            worldview="complete decoder submissions are coefficient terms, but only their non-Q2 high-consensus nullspace cells are action-grade",
        ),
        H109Spec(
            name="residual_coeff_transport_c96_t10",
            group="residual_transport",
            source_families=("h103", "h104", "h105", "h106", "h107", "h108"),
            coeffs=(0.18, 0.30, 0.42, 0.54),
            max_terms=10,
            max_cells=96,
            max_rows=58,
            max_per_subject=10,
            max_per_target=24,
            q2_cap=2,
            field_cap=0.40,
            cell_cap=0.28,
            min_abs_move=0.010,
            min_family_count=2,
            min_family_consensus=0.54,
            min_vote_weight=1.3,
            max_bad_weighted_pos=0.010,
            max_bad_max_pos=0.050,
            max_h088_cos=-0.002,
            min_good_margin=0.008,
            route_pred_cap=0.000160,
            h098_pred_cap=0.000090,
            residualize_bad_axes=True,
            worldview="dense decoder-coefficient intent becomes safe after residualizing bad public axes and decoding back to cells",
        ),
        H109Spec(
            name="kernel_coeff_focus_c48_t7",
            group="kernel_focus",
            source_families=("h105", "h106", "h108"),
            coeffs=(0.30, 0.45, 0.60, 0.75),
            max_terms=7,
            max_cells=48,
            max_rows=24,
            max_per_subject=14,
            max_per_target=14,
            q2_cap=0,
            field_cap=0.46,
            cell_cap=0.32,
            min_abs_move=0.013,
            min_family_count=2,
            min_family_consensus=0.60,
            min_vote_weight=1.0,
            max_bad_weighted_pos=0.006,
            max_bad_max_pos=0.036,
            max_h088_cos=-0.003,
            min_good_margin=0.012,
            route_pred_cap=0.000120,
            h098_pred_cap=0.000080,
            residualize_bad_axes=False,
            worldview="the route-consensus kernel is best recovered as coefficient mixing of H105/H106/H108",
        ),
        H109Spec(
            name="objective_coeff_bridge_c120_t9",
            group="objective",
            source_families=("h103", "h104", "h105", "h106", "h108"),
            coeffs=(0.18, 0.28, 0.38, 0.50),
            max_terms=9,
            max_cells=120,
            max_rows=72,
            max_per_subject=10,
            max_per_target=30,
            q2_cap=0,
            field_cap=0.36,
            cell_cap=0.25,
            min_abs_move=0.009,
            min_family_count=2,
            min_family_consensus=0.48,
            min_vote_weight=0.9,
            max_bad_weighted_pos=0.016,
            max_bad_max_pos=0.070,
            max_h088_cos=0.000,
            min_good_margin=0.004,
            route_pred_cap=0.000220,
            h098_pred_cap=0.000100,
            residualize_bad_axes=True,
            worldview="objective Q3/S cells are the broad coefficient-solvable part of the decoder equation",
        ),
        H109Spec(
            name="q2_coeff_micro_c16_t5",
            group="q2_probe",
            source_families=("h103", "h104", "h108"),
            coeffs=(0.16, 0.24, 0.32, 0.42),
            max_terms=5,
            max_cells=16,
            max_rows=16,
            max_per_subject=5,
            max_per_target=16,
            q2_cap=16,
            field_cap=0.22,
            cell_cap=0.18,
            min_abs_move=0.008,
            min_family_count=2,
            min_family_consensus=0.50,
            min_vote_weight=0.75,
            max_bad_weighted_pos=0.006,
            max_bad_max_pos=0.034,
            max_h088_cos=-0.002,
            min_good_margin=0.004,
            route_pred_cap=0.000240,
            h098_pred_cap=0.000085,
            residualize_bad_axes=False,
            worldview="Q2 should reopen only if coefficient terms agree under a tiny nullspace",
        ),
    ]


def target_allowed(target: str, group: str) -> bool:
    if group in {"nonq2_strict", "kernel_focus"}:
        return target != "Q2"
    if group == "residual_transport":
        return True
    if group == "objective":
        return target in {"Q3", "S1", "S2", "S3", "S4"}
    if group == "q2_probe":
        return target == "Q2"
    raise ValueError(group)


def build_context() -> tuple[
    pd.DataFrame,
    h097mod.ResponseFit,
    h100mod.RouteBasisFit,
    pd.DataFrame,
    np.ndarray,
    pd.DataFrame,
    np.ndarray,
    pd.DataFrame,
    np.ndarray,
    pd.DataFrame,
    np.ndarray,
]:
    (
        cell,
        h098_fit,
        route_fit,
        basis_fit_df,
        basis_fit_moves,
        bad_axes,
        bad_moves,
        good_axes,
        good_moves,
    ) = h108mod.build_context()
    return cell, h098_fit, route_fit, basis_fit_df, basis_fit_moves, bad_axes, bad_moves, good_axes, good_moves


def load_sources(sample: pd.DataFrame, base_prob: np.ndarray, cell: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray, pd.DataFrame]:
    source, source_moves, source_weights = h108mod.load_source_candidates(sample, base_prob)
    source = source.copy()
    source["h109_source_weight"] = source_weights
    h108_path = ROOT / "submission_h108_jury_610a26a0_uploadsafe.csv"
    if h108_path.exists():
        base_logit = logit(base_prob).reshape(-1)
        prob = h085mod.load_sub(h108_path, sample)[TARGETS].to_numpy(dtype=np.float64)
        move = logit(prob).reshape(-1) - base_logit
        extra = {
            "family": "h108",
            "candidate_id": "h108_strict_intersection_c48_a085_610a26a0",
            "file": h108_path.name,
            "path": str(h108_path.resolve()),
            "weight": 1.72,
            "score_rank": 1.0,
            "score": 0.927303690,
            "route_basis_pred_delta_vs_h057": -0.001528316,
            "model_pred_delta_vs_h057": -0.000050438,
            "selected_cells": 47,
            "changed_rows_vs_h057": 27,
            "h109_source_weight": 1.72,
        }
        source = pd.concat([source, pd.DataFrame([extra])], ignore_index=True)
        source_moves = np.vstack([source_moves, move])
    return source.reset_index(drop=True), source_moves.astype(np.float64), h108mod.build_jury_table(
        cell,
        source.iloc[:-1].copy() if len(source) > len(source_moves) else source[source["family"].ne("h108")].copy(),
        source_moves[:-1] if h108_path.exists() else source_moves,
        source["h109_source_weight"].to_numpy(dtype=np.float64)[:-1] if h108_path.exists() else source["h109_source_weight"].to_numpy(dtype=np.float64),
    )


def route_pred(move_flat: np.ndarray, basis_fit_df: pd.DataFrame, basis_fit_moves: np.ndarray, route_fit: h100mod.RouteBasisFit) -> float:
    return h100mod.predict_candidate_delta(move_flat, basis_fit_df, basis_fit_moves, route_fit)


def h098_pred(move_flat: np.ndarray, cell: pd.DataFrame, h098_fit: h097mod.ResponseFit) -> float:
    return h097mod.predict_candidate_delta(move_flat, cell, h098_fit)


def residualize_bad_axes(move: np.ndarray, bad_axes: pd.DataFrame, bad_moves: np.ndarray, strength: float = 0.92) -> np.ndarray:
    out = np.asarray(move, dtype=np.float64).copy()
    bad_w = bad_axes["weight"].to_numpy(dtype=np.float64)
    order = np.argsort(-bad_w)
    for idx in order:
        axis = bad_moves[idx].astype(np.float64)
        denom = float(np.dot(axis, axis) + 1.0e-12)
        coeff = float(np.dot(out, axis) / denom)
        if coeff > 0.0:
            out = out - strength * coeff * axis
    return out


def build_terms(
    source: pd.DataFrame,
    source_moves: np.ndarray,
    spec: H109Spec,
    q2_mask: np.ndarray,
) -> list[dict[str, object]]:
    terms = []
    for i, rec in source.iterrows():
        family = str(rec["family"])
        if family not in spec.source_families:
            continue
        base_move = source_moves[i].copy()
        if spec.group != "q2_probe" and spec.q2_cap == 0:
            base_move[q2_mask] = 0.0
        if spec.group == "q2_probe":
            base_move[~q2_mask] = 0.0
        for coeff in spec.coeffs:
            move = np.clip(base_move * coeff, -spec.field_cap, spec.field_cap)
            if np.linalg.norm(move) <= 1.0e-12:
                continue
            route_component = max(-float(rec["route_basis_pred_delta_vs_h057"]), 0.0)
            model_component = max(-float(rec["model_pred_delta_vs_h057"]), 0.0)
            score = (
                0.58 * float(rec["h109_source_weight"])
                + 145.0 * route_component
                + 260.0 * model_component
                + 0.12 * float(rec["score_rank"])
                + 0.04 * float(family in {"h105", "h108"})
                - 0.03 * float(family == "h107")
                - 0.03 * float(abs(coeff) > 0.58)
            )
            terms.append(
                {
                    "source_index": int(i),
                    "family": family,
                    "candidate_id": str(rec["candidate_id"]),
                    "source_file": str(rec["file"]),
                    "coeff": float(coeff),
                    "term_score": float(score),
                    "move": move,
                }
            )
    return sorted(terms, key=lambda x: float(x["term_score"]), reverse=True)


def coefficient_field(
    terms: list[dict[str, object]],
    spec: H109Spec,
    cell: pd.DataFrame,
    h098_fit: h097mod.ResponseFit,
    route_fit: h100mod.RouteBasisFit,
    basis_fit_df: pd.DataFrame,
    basis_fit_moves: np.ndarray,
    bad_axes: pd.DataFrame,
    bad_moves: np.ndarray,
    good_moves: np.ndarray,
) -> tuple[np.ndarray, pd.DataFrame]:
    move = np.zeros_like(terms[0]["move"], dtype=np.float64) if terms else np.zeros(len(cell), dtype=np.float64)
    selected = []
    best_score = -1.0e9
    for term in terms:
        if len(selected) >= spec.max_terms:
            break
        trial = np.clip(move + np.asarray(term["move"], dtype=np.float64), -spec.field_cap, spec.field_cap)
        if spec.residualize_bad_axes:
            trial = np.clip(residualize_bad_axes(trial, bad_axes, bad_moves), -spec.field_cap, spec.field_cap)
        axis = h102mod.cumulative_axis_metrics(trial, bad_axes, bad_moves, good_moves)
        if axis["h102_cum_bad_weighted_pos"] > spec.max_bad_weighted_pos:
            continue
        if axis["h102_cum_bad_max_pos"] > spec.max_bad_max_pos:
            continue
        if axis["h102_cum_h088_axis_cos"] > spec.max_h088_cos:
            continue
        if axis["h102_cum_good_bad_margin"] < spec.min_good_margin:
            continue
        rpred = route_pred(trial, basis_fit_df, basis_fit_moves, route_fit)
        cpred = h098_pred(trial, cell, h098_fit)
        if rpred > spec.route_pred_cap:
            continue
        if cpred > spec.h098_pred_cap:
            continue
        score = (
            170.0 * (-cpred)
            + 130.0 * (-rpred)
            + 0.11 * max(axis["h102_cum_good_bad_margin"], 0.0)
            + 0.08 * max(-axis["h102_cum_h088_axis_cos"], 0.0)
            - 0.42 * max(axis["h102_cum_bad_weighted_pos"], 0.0)
            - 0.25 * max(axis["h102_cum_bad_max_pos"], 0.0)
            + 0.025 * len(selected)
            + float(term["term_score"])
        )
        if score + 1.0e-9 < best_score and len(selected) >= 2:
            continue
        move = trial
        selected.append({k: v for k, v in term.items() if k != "move"} | axis | {"route_pred": rpred, "h098_pred": cpred, "field_score": score})
        best_score = max(best_score, score)
    return move, pd.DataFrame(selected)


def select_cells_from_field(
    field: np.ndarray,
    jury: pd.DataFrame,
    spec: H109Spec,
    base_shape: tuple[int, int],
    bad_axes: pd.DataFrame,
    bad_moves: np.ndarray,
    good_moves: np.ndarray,
) -> tuple[pd.DataFrame, np.ndarray]:
    pool = jury.sort_values("flat_index").reset_index(drop=True).copy()
    pool["h109_field_move"] = np.clip(field, -spec.cell_cap, spec.cell_cap)
    sign = np.sign(pool["h109_field_move"].to_numpy(dtype=np.float64))
    h088_sign = np.sign(pool["h088_logit_move"].to_numpy(dtype=np.float64))
    h057_sign = np.sign(pool["h057_positive_logit_move"].to_numpy(dtype=np.float64))
    pool["h109_anti_h088"] = (sign * h088_sign < 0).astype(float)
    pool["h109_align_h057"] = (
        (sign * h057_sign > 0)
        & (pool["h057_positive_weight"].to_numpy(dtype=np.float64) > 0)
    ).astype(float)
    pool["h109_cell_score"] = (
        np.abs(pool["h109_field_move"].to_numpy(dtype=np.float64))
        * (0.56 + pool["h108_family_consensus"].to_numpy(dtype=np.float64))
        * (0.46 + np.log1p(pool["h108_vote_weight"].to_numpy(dtype=np.float64)))
        * (
            0.66
            + 0.10 * pool["h108_family_count"].to_numpy(dtype=np.float64)
            + 0.18 * pool["h109_anti_h088"].to_numpy(dtype=np.float64)
            + 0.14 * pool["h109_align_h057"].to_numpy(dtype=np.float64)
            + 0.10 * pool["h057_h088_anti_conflict"].to_numpy(dtype=np.float64)
            + 0.08 * pool["h095_safe_cell_score"].to_numpy(dtype=np.float64)
            + 0.05 * pool["h098_frontier_cell_score"].to_numpy(dtype=np.float64)
            - 0.12 * pool["h080_bad_same_rank"].to_numpy(dtype=np.float64)
            - 0.08 * pool["is_h050_null"].to_numpy(dtype=np.float64)
        )
    )
    pool = pool[np.abs(pool["h109_field_move"].to_numpy(dtype=np.float64)) >= spec.min_abs_move].copy()
    pool = pool[pool["h108_family_count"].astype(int) >= spec.min_family_count]
    pool = pool[pool["h108_family_consensus"].to_numpy(dtype=np.float64) >= spec.min_family_consensus]
    pool = pool[pool["h108_vote_weight"].to_numpy(dtype=np.float64) >= spec.min_vote_weight]
    pool = pool[pool["target"].astype(str).map(lambda t: target_allowed(t, spec.group))]
    pool = pool.sort_values("h109_cell_score", ascending=False)

    selected = []
    used_rows: set[int] = set()
    subject_counts: dict[str, int] = {}
    target_counts: dict[str, int] = {}
    q2_count = 0
    move_mat = np.zeros(base_shape, dtype=np.float64)

    for rec in pool.to_dict("records"):
        if len(selected) >= spec.max_cells:
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
        tmp[row, int(rec["target_index"])] = float(rec["h109_field_move"])
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
        selected.append(rec)
        if row not in used_rows:
            used_rows.add(row)
            subject_counts[subject] = subject_counts.get(subject, 0) + 1
        target_counts[target] = target_counts.get(target, 0) + 1
        if target == "Q2":
            q2_count += 1
    out = pd.DataFrame(selected)
    if out.empty:
        return out, move_mat
    out = out.sort_values(["row", "target_index"]).reset_index(drop=True)
    out["h097_move_col"] = "h109_field_move"
    return out, move_mat


def materialize(base_prob: np.ndarray, move_mat: np.ndarray) -> np.ndarray:
    return clip_prob(sigmoid(logit(base_prob) + move_mat))


def evaluate_candidate(
    candidate_id: str,
    prob: np.ndarray,
    move_mat: np.ndarray,
    field: np.ndarray,
    terms: pd.DataFrame,
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
    spec: H109Spec,
    path: Path,
) -> dict[str, object]:
    proxy = h097mod.H097Spec(
        name=spec.name,
        mode="decoder_coefficient_equation_solver",
        target_group=spec.group,
        k=spec.max_cells,
        alpha=max(spec.coeffs),
        cap=spec.cell_cap,
        min_score=spec.min_abs_move,
        worldview=spec.worldview,
    )
    out = h097mod.evaluate_candidate(candidate_id, prob, move_mat, base_prob, selected_cells, cell, sample, h098_fit, proxy, path)
    axis = h102mod.cumulative_axis_metrics(move_mat.reshape(-1), bad_axes, bad_moves, good_moves)
    field_axis = h102mod.cumulative_axis_metrics(field, bad_axes, bad_moves, good_moves)
    out.update(axis)
    out["field_h102_bad_weighted_pos"] = field_axis["h102_cum_bad_weighted_pos"]
    out["field_h102_h088_axis_cos"] = field_axis["h102_cum_h088_axis_cos"]
    out["field_h102_good_bad_margin"] = field_axis["h102_cum_good_bad_margin"]
    out["route_basis_pred_delta_vs_h057"] = route_pred(move_mat.reshape(-1), basis_fit_df, basis_fit_moves, route_fit)
    out["field_route_basis_pred_delta_vs_h057"] = route_pred(field, basis_fit_df, basis_fit_moves, route_fit)
    out["field_model_pred_delta_vs_h057"] = h098_pred(field, cell, h098_fit)
    out["selected_terms"] = int(len(terms))
    out["selected_term_families"] = ",".join(sorted(terms["family"].astype(str).unique().tolist())) if len(terms) else ""
    out["selected_coeff_sum"] = float(terms["coeff"].sum()) if len(terms) else 0.0
    out["selected_mean_family_count"] = float(selected_cells["h108_family_count"].mean()) if len(selected_cells) else 0.0
    out["selected_mean_family_consensus"] = float(selected_cells["h108_family_consensus"].mean()) if len(selected_cells) else 0.0
    out["selected_mean_vote_weight"] = float(selected_cells["h108_vote_weight"].mean()) if len(selected_cells) else 0.0
    out["selected_mean_h109_cell_score"] = float(selected_cells["h109_cell_score"].mean()) if len(selected_cells) else 0.0
    out["h109_score"] = (
        165.0 * (-float(out["model_pred_delta_vs_h057"]))
        + 125.0 * (-float(out["route_basis_pred_delta_vs_h057"]))
        + 45.0 * (-float(out["field_model_pred_delta_vs_h057"]))
        + 35.0 * (-float(out["field_route_basis_pred_delta_vs_h057"]))
        + 0.20 * float(out["anti_h088_direction_rate"])
        + 0.16 * float(out["h057_positive_align_rate"])
        + 0.14 * float(out["selected_conflict_rate"])
        + 0.10 * min(float(out["selected_mean_family_count"]) / 4.0, 1.0)
        + 0.10 * float(out["selected_mean_family_consensus"])
        + 0.07 * max(float(out["h102_cum_good_bad_margin"]), 0.0)
        + 0.06 * max(-float(out["h102_cum_h088_axis_cos"]), 0.0)
        - 0.56 * max(float(out["h102_cum_bad_weighted_pos"]), 0.0)
        - 0.34 * max(float(out["h102_cum_bad_max_pos"]), 0.0)
        - 0.32 * max(float(out["h102_cum_h088_axis_cos"]), 0.0)
        - 0.25 * max(float(out["max_positive_bad_cosine"]), 0.0)
        - 22.0 * max(float(out["hard_diag_delta_vs_h057"]), 0.0)
        - 10.0 * max(float(out["posterior_delta_vs_h057"]), 0.0)
    )
    return out


def run() -> None:
    cleanup_previous_outputs()
    base = h085mod.load_sub(BASE_FILE)
    sample = base[KEYS].copy()
    base_prob = base[TARGETS].to_numpy(dtype=np.float64)
    cell, h098_fit, route_fit, basis_fit_df, basis_fit_moves, bad_axes, bad_moves, good_axes, good_moves = build_context()
    source, source_moves, jury = load_sources(sample, base_prob, cell)
    q2_mask = np.tile(np.asarray([target == "Q2" for target in TARGETS], dtype=bool), base_prob.shape[0])

    candidate_rows = []
    term_frames = []
    selected_frames = []
    top_frames = []
    for spec in candidate_specs():
        terms = build_terms(source, source_moves, spec, q2_mask)
        if not terms:
            continue
        field, selected_terms = coefficient_field(
            terms,
            spec,
            cell,
            h098_fit,
            route_fit,
            basis_fit_df,
            basis_fit_moves,
            bad_axes,
            bad_moves,
            good_moves,
        )
        if selected_terms.empty:
            continue
        selected_cells, move_mat = select_cells_from_field(field, jury, spec, base_prob.shape, bad_axes, bad_moves, good_moves)
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
        candidate_id = safe_id(f"h109_{spec.name}_{hash_id}", 128)
        path = OUT / f"submission_{candidate_id}.csv"
        h085mod.write_submission(sample, prob, path)
        metrics = evaluate_candidate(
            candidate_id,
            prob,
            move_mat,
            field,
            selected_terms,
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
        selected_terms = selected_terms.copy().rename(columns={"candidate_id": "source_candidate_id"})
        selected_terms.insert(0, "candidate_id", candidate_id)
        term_frames.append(selected_terms)
        selected_cells = selected_cells.copy()
        selected_cells.insert(0, "candidate_id", candidate_id)
        selected_frames.append(selected_cells)
        top = jury.copy()
        top["h109_field_move"] = np.clip(field, -spec.cell_cap, spec.cell_cap)
        top = top.reindex(top["h109_field_move"].abs().sort_values(ascending=False).index).head(260).copy()
        top.insert(0, "candidate_id", candidate_id)
        top_frames.append(top)

    candidates = pd.DataFrame(candidate_rows)
    if candidates.empty:
        raise RuntimeError("no H109 candidates")
    candidates = candidates.sort_values(["h109_score", "model_pred_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True)
    selected = candidates.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"submission_h109_coeff_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)

    decision = {
        "decision": "promote_h109_decoder_coefficient_equation_solver",
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

    source.to_csv(OUT / "h109_source_candidates.csv", index=False)
    jury.to_csv(OUT / "h109_jury_table.csv", index=False)
    candidates.to_csv(OUT / "h109_candidates.csv", index=False)
    pd.concat(term_frames, ignore_index=True).to_csv(OUT / "h109_selected_terms.csv", index=False)
    pd.concat(selected_frames, ignore_index=True).to_csv(OUT / "h109_selected_cells.csv", index=False)
    pd.concat(top_frames, ignore_index=True).to_csv(OUT / "h109_top_field_cells.csv", index=False)
    pd.DataFrame([decision]).to_csv(OUT / "h109_decision.csv", index=False)

    cols = [
        "candidate_id",
        "spec_name",
        "selected_terms",
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
        "field_model_pred_delta_vs_h057",
        "field_route_basis_pred_delta_vs_h057",
        "h102_cum_bad_weighted_pos",
        "h102_cum_h088_axis_cos",
        "h102_cum_good_bad_margin",
        "selected_mean_family_count",
        "selected_mean_family_consensus",
        "h109_score",
        "file",
    ]
    report = f"""# H109 Decoder-Coefficient Equation Solver HS-JEPA

Question: can complete HS-JEPA decoder submissions be solved as coefficient
basis vectors of one public/private row-target equation?

Candidates:

{md_table(candidates[cols], 20)}

Decision:

{md_table(pd.DataFrame([decision]), 1)}

Interpretation rule:

- If H109 improves over H108, the hidden equation is coefficient composition
  and cancellation among decoder branches, not just cell-wise family
  intersection.
- If H108 beats H109, sparse decoder-family agreement is safer than coefficient
  transport.
- If both lose while a single H103-H107 branch wins, the true action law is
  branch-specific.
"""
    (OUT / "h109_report.md").write_text(report, encoding="utf-8")

    print(f"selected={decision['selected_candidate_id']}")
    print(f"root={root_path}")
    print(candidates[cols].head(10).to_string(index=False))


if __name__ == "__main__":
    run()
