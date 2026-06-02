#!/usr/bin/env python3
"""H108: decoder-jury assignment solver HS-JEPA.

H103-H107 each proposed a different action decoder:

- toxic-shadow portfolio;
- toxic-axis residual transport;
- sparse route-consensus kernel;
- route-consensus expansion;
- H088 antipode toxicity inversion.

H108 treats those decoders as independent witnesses.  A row-target action is
trusted only when multiple decoder families point to the same signed cell move,
and the cumulative action stays safe under the public/private bad-axis
equation.
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
OUT = HITL / "h108_decoder_jury_assignment_solver_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H107_PATH = HITL / "h107_h088_antipode_toxicity_solver_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h107mod", H107_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H107_PATH}")
h107mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h107mod
SPEC.loader.exec_module(h107mod)

h106mod = h107mod.h106mod
h105mod = h107mod.h105mod
h104mod = h107mod.h104mod
h103mod = h107mod.h103mod
h102mod = h107mod.h102mod
h100mod = h107mod.h100mod
h099mod = h107mod.h099mod
h098mod = h107mod.h098mod
h097mod = h107mod.h097mod
h095mod = h107mod.h095mod
h085mod = h107mod.h085mod

TARGETS = h107mod.TARGETS
KEYS = h107mod.KEYS
BASE_FILE = h107mod.BASE_FILE
TOL = h107mod.TOL


@dataclass(frozen=True)
class FamilyInfo:
    name: str
    directory: str
    candidates_csv: str
    score_col: str
    base_weight: float


@dataclass(frozen=True)
class H108Spec:
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
    min_family_count: int
    min_family_consensus: float
    min_vote_weight: float
    max_bad_weighted_pos: float
    max_bad_max_pos: float
    max_h088_cos: float
    min_good_margin: float
    route_pred_cap: float
    h098_pred_cap: float
    worldview: str


FAMILIES = [
    FamilyInfo("h103", "h103_toxic_shadow_cancellation_hsjepa", "h103_candidates.csv", "h103_score", 1.05),
    FamilyInfo("h104", "h104_toxic_axis_residual_transport_hsjepa", "h104_candidates.csv", "h104_score", 0.98),
    FamilyInfo("h105", "h105_signed_route_coefficient_solver_hsjepa", "h105_candidates.csv", "h105_score", 1.12),
    FamilyInfo("h106", "h106_route_consensus_kernel_expansion_hsjepa", "h106_candidates.csv", "h106_score", 1.00),
    FamilyInfo("h107", "h107_h088_antipode_toxicity_solver_hsjepa", "h107_candidates.csv", "h107_score", 0.86),
]


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
    for path in OUT.glob("submission_h108_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h108_jury_*.csv"):
        path.unlink()


def candidate_specs() -> list[H108Spec]:
    return [
        H108Spec(
            name="strict_intersection_c48_a085",
            group="strict_intersection",
            max_cells=48,
            max_rows=30,
            max_per_subject=8,
            max_per_target=14,
            q2_cap=0,
            amp=0.85,
            cap=0.30,
            min_score=0.55,
            min_family_count=3,
            min_family_consensus=0.62,
            min_vote_weight=2.50,
            max_bad_weighted_pos=0.005,
            max_bad_max_pos=0.028,
            max_h088_cos=-0.004,
            min_good_margin=0.014,
            route_pred_cap=0.000120,
            h098_pred_cap=0.000070,
            worldview="only non-Q2 cells supported by at least three independent decoder families are action-grade",
        ),
        H108Spec(
            name="portfolio_residual_core_c82_a070",
            group="portfolio_residual",
            max_cells=82,
            max_rows=48,
            max_per_subject=9,
            max_per_target=20,
            q2_cap=2,
            amp=0.70,
            cap=0.28,
            min_score=0.48,
            min_family_count=2,
            min_family_consensus=0.55,
            min_vote_weight=1.80,
            max_bad_weighted_pos=0.010,
            max_bad_max_pos=0.048,
            max_h088_cos=-0.002,
            min_good_margin=0.008,
            route_pred_cap=0.000150,
            h098_pred_cap=0.000085,
            worldview="H103 portfolio and H104 residual transport agree on the true public-safe assignment field",
        ),
        H108Spec(
            name="kernel_jury_transfer_c64_a080",
            group="kernel_jury",
            max_cells=64,
            max_rows=28,
            max_per_subject=16,
            max_per_target=18,
            q2_cap=0,
            amp=0.80,
            cap=0.30,
            min_score=0.50,
            min_family_count=2,
            min_family_consensus=0.60,
            min_vote_weight=1.35,
            max_bad_weighted_pos=0.008,
            max_bad_max_pos=0.040,
            max_h088_cos=-0.003,
            min_good_margin=0.010,
            route_pred_cap=0.000100,
            h098_pred_cap=0.000075,
            worldview="H105/H106 kernel cells become safe only when another decoder family confirms them",
        ),
        H108Spec(
            name="objective_decoder_jury_c110_a060",
            group="objective",
            max_cells=110,
            max_rows=70,
            max_per_subject=10,
            max_per_target=28,
            q2_cap=0,
            amp=0.60,
            cap=0.24,
            min_score=0.43,
            min_family_count=2,
            min_family_consensus=0.48,
            min_vote_weight=1.10,
            max_bad_weighted_pos=0.016,
            max_bad_max_pos=0.070,
            max_h088_cos=0.000,
            min_good_margin=0.004,
            route_pred_cap=0.000220,
            h098_pred_cap=0.000100,
            worldview="objective Q3/S cells are the broad transferable part of the decoder jury",
        ),
        H108Spec(
            name="signed_q2_probe_c18_a045",
            group="q2_probe",
            max_cells=18,
            max_rows=18,
            max_per_subject=5,
            max_per_target=18,
            q2_cap=18,
            amp=0.45,
            cap=0.22,
            min_score=0.45,
            min_family_count=2,
            min_family_consensus=0.50,
            min_vote_weight=0.90,
            max_bad_weighted_pos=0.006,
            max_bad_max_pos=0.034,
            max_h088_cos=-0.002,
            min_good_margin=0.004,
            route_pred_cap=0.000220,
            h098_pred_cap=0.000080,
            worldview="Q2 should reopen only where multiple decoders independently agree on the same sign",
        ),
    ]


def family_allowed(row: dict[str, object], group: str) -> bool:
    target = str(row["target"])
    if group == "strict_intersection":
        return target != "Q2" and int(row["h108_family_count"]) >= 3
    if group == "portfolio_residual":
        return bool(row["h108_has_h103"]) and bool(row["h108_has_h104"])
    if group == "kernel_jury":
        return target != "Q2" and (bool(row["h108_has_h105"]) or bool(row["h108_has_h106"]))
    if group == "objective":
        return target in {"Q3", "S1", "S2", "S3", "S4"}
    if group == "q2_probe":
        return target == "Q2"
    raise ValueError(group)


def load_source_candidates(sample: pd.DataFrame, base_prob: np.ndarray) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    base_logit = logit(base_prob).reshape(-1)
    rows = []
    moves = []
    weights = []
    for family in FAMILIES:
        directory = HITL / family.directory
        cpath = directory / family.candidates_csv
        if not cpath.exists():
            continue
        df = pd.read_csv(cpath).copy()
        if df.empty:
            continue
        score = df[family.score_col].to_numpy(dtype=np.float64) if family.score_col in df.columns else np.zeros(len(df))
        score_rank = rank01(score, high=True)
        route_pred = df["route_basis_pred_delta_vs_h057"].to_numpy(dtype=np.float64) if "route_basis_pred_delta_vs_h057" in df.columns else np.zeros(len(df))
        model_pred = df["model_pred_delta_vs_h057"].to_numpy(dtype=np.float64) if "model_pred_delta_vs_h057" in df.columns else np.zeros(len(df))
        for i, rec in df.iterrows():
            file_name = str(rec["file"])
            path = directory / file_name
            if not path.exists():
                continue
            prob = h085mod.load_sub(path, sample)[TARGETS].to_numpy(dtype=np.float64)
            move = logit(prob).reshape(-1) - base_logit
            if np.linalg.norm(move) <= 1.0e-12:
                continue
            w = family.base_weight * (0.62 + 0.76 * float(score_rank[i]))
            w *= 1.0 + 0.08 * float(route_pred[i] < 0.0) + 0.06 * float(model_pred[i] < 0.0)
            w *= 1.0 - 0.06 * min(float(max(rec.get("Q2_changed_vs_h057", 0), 0)) / 30.0, 1.0)
            rows.append(
                {
                    "family": family.name,
                    "candidate_id": str(rec["candidate_id"]),
                    "file": file_name,
                    "path": str(path.resolve()),
                    "weight": float(w),
                    "score_rank": float(score_rank[i]),
                    "score": float(score[i]) if len(score) else 0.0,
                    "route_basis_pred_delta_vs_h057": float(route_pred[i]),
                    "model_pred_delta_vs_h057": float(model_pred[i]),
                    "selected_cells": int(rec.get("selected_cells", 0)),
                    "changed_rows_vs_h057": int(rec.get("changed_rows_vs_h057", 0)),
                }
            )
            moves.append(move)
            weights.append(w)
    if not rows:
        raise RuntimeError("no H108 source candidates")
    return pd.DataFrame(rows), np.vstack(moves).astype(np.float64), np.asarray(weights, dtype=np.float64)


def build_jury_table(
    cell: pd.DataFrame,
    source: pd.DataFrame,
    source_moves: np.ndarray,
    source_weights: np.ndarray,
) -> pd.DataFrame:
    n = len(cell)
    vote_sum = np.zeros(n, dtype=np.float64)
    vote_abs = np.zeros(n, dtype=np.float64)
    vote_weight = np.zeros(n, dtype=np.float64)
    vote_count = np.zeros(n, dtype=np.float64)
    family_sums: dict[str, np.ndarray] = {family.name: np.zeros(n, dtype=np.float64) for family in FAMILIES}
    family_weights: dict[str, float] = {family.name: family.base_weight for family in FAMILIES}

    for i, rec in source.reset_index(drop=True).iterrows():
        move = source_moves[i]
        active = np.abs(move) > 1.0e-10
        w = float(source_weights[i])
        fam = str(rec["family"])
        vote_sum[active] += w * move[active]
        vote_abs[active] += w * np.abs(move[active])
        vote_weight[active] += w
        vote_count[active] += 1.0
        family_sums[fam][active] += w * move[active]

    family_mat = np.vstack([family_sums[family.name] for family in FAMILIES]).astype(np.float64)
    family_active = np.abs(family_mat) > 1.0e-10
    family_count = family_active.sum(axis=0).astype(float)
    family_abs = np.abs(family_mat).sum(axis=0)
    family_sum = family_mat.sum(axis=0)
    family_consensus = np.abs(family_sum) / (family_abs + 1.0e-12)
    family_signed_count = np.abs(np.sign(family_mat).sum(axis=0)) / np.maximum(family_count, 1.0)
    raw_mean = vote_sum / (vote_weight + 1.0e-12)

    out = cell.sort_values("flat_index").reset_index(drop=True).copy()
    out["h108_vote_sum"] = vote_sum
    out["h108_vote_abs"] = vote_abs
    out["h108_vote_weight"] = vote_weight
    out["h108_vote_count"] = vote_count
    out["h108_raw_mean_move"] = raw_mean
    out["h108_vote_consensus"] = np.abs(vote_sum) / (vote_abs + 1.0e-12)
    out["h108_family_count"] = family_count.astype(int)
    out["h108_family_consensus"] = family_consensus
    out["h108_family_signed_count"] = family_signed_count
    for family in FAMILIES:
        arr = family_sums[family.name]
        out[f"h108_{family.name}_move"] = arr
        out[f"h108_has_{family.name}"] = np.abs(arr) > 1.0e-10
    sign = np.sign(raw_mean)
    h088_sign = np.sign(out["h088_logit_move"].to_numpy(dtype=np.float64))
    h057_sign = np.sign(out["h057_positive_logit_move"].to_numpy(dtype=np.float64))
    out["h108_anti_h088"] = (sign * h088_sign < 0).astype(float)
    out["h108_align_h057"] = (
        (sign * h057_sign > 0)
        & (out["h057_positive_weight"].to_numpy(dtype=np.float64) > 0)
    ).astype(float)
    out["h108_decoder_jury_score"] = (
        rank01(np.abs(raw_mean), high=True) * 0.24
        + rank01(vote_weight, high=True) * 0.17
        + rank01(family_count, high=True) * 0.15
        + family_consensus * 0.12
        + out["h108_anti_h088"].to_numpy(dtype=np.float64) * 0.10
        + out["h108_align_h057"].to_numpy(dtype=np.float64) * 0.08
        + out["h057_h088_anti_conflict"].to_numpy(dtype=np.float64) * 0.07
        + out["h095_safe_cell_score"].to_numpy(dtype=np.float64) * 0.05
        + out["h098_frontier_cell_score"].to_numpy(dtype=np.float64) * 0.04
        - out["h080_bad_same_rank"].to_numpy(dtype=np.float64) * 0.10
        - out["is_h050_null"].to_numpy(dtype=np.float64) * 0.06
        - out["target"].astype(str).eq("Q2").astype(float) * 0.06
    )
    return out


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
        _cells_by_basis,
        _scored,
        h098_fit,
        route_fit,
        basis_fit_df,
        basis_fit_moves,
        bad_axes,
        bad_moves,
        good_axes,
        good_moves,
    ) = h107mod.build_route_context()
    return cell, h098_fit, route_fit, basis_fit_df, basis_fit_moves, bad_axes, bad_moves, good_axes, good_moves


def route_pred(move_flat: np.ndarray, basis_fit_df: pd.DataFrame, basis_fit_moves: np.ndarray, route_fit: h100mod.RouteBasisFit) -> float:
    return h100mod.predict_candidate_delta(move_flat, basis_fit_df, basis_fit_moves, route_fit)


def h098_pred(move_flat: np.ndarray, cell: pd.DataFrame, h098_fit: h097mod.ResponseFit) -> float:
    return h097mod.predict_candidate_delta(move_flat, cell, h098_fit)


def select_cells(
    jury: pd.DataFrame,
    spec: H108Spec,
    base_shape: tuple[int, int],
    bad_axes: pd.DataFrame,
    bad_moves: np.ndarray,
    good_moves: np.ndarray,
) -> tuple[pd.DataFrame, np.ndarray]:
    pool = jury.copy()
    pool["h108_move"] = np.clip(pool["h108_raw_mean_move"].to_numpy(dtype=np.float64) * spec.amp, -spec.cap, spec.cap)
    pool["h108_spec_score"] = (
        np.abs(pool["h108_move"].to_numpy(dtype=np.float64))
        * (0.55 + pool["h108_family_consensus"].to_numpy(dtype=np.float64))
        * (0.55 + np.log1p(pool["h108_vote_weight"].to_numpy(dtype=np.float64)))
        * (
            0.62
            + 0.09 * pool["h108_family_count"].to_numpy(dtype=np.float64)
            + 0.18 * pool["h108_anti_h088"].to_numpy(dtype=np.float64)
            + 0.14 * pool["h108_align_h057"].to_numpy(dtype=np.float64)
            + 0.12 * pool["h057_h088_anti_conflict"].to_numpy(dtype=np.float64)
            + 0.08 * pool["h095_safe_cell_score"].to_numpy(dtype=np.float64)
            + 0.06 * pool["h098_frontier_cell_score"].to_numpy(dtype=np.float64)
            - 0.12 * pool["h080_bad_same_rank"].to_numpy(dtype=np.float64)
            - 0.08 * pool["is_h050_null"].to_numpy(dtype=np.float64)
        )
    )
    pool = pool[np.abs(pool["h108_move"].to_numpy(dtype=np.float64)) > 1.0e-10].copy()
    pool = pool[pool["h108_decoder_jury_score"].to_numpy(dtype=np.float64) >= spec.min_score]
    pool = pool[pool["h108_family_count"].astype(int) >= spec.min_family_count]
    pool = pool[pool["h108_family_consensus"].to_numpy(dtype=np.float64) >= spec.min_family_consensus]
    pool = pool[pool["h108_vote_weight"].to_numpy(dtype=np.float64) >= spec.min_vote_weight]
    pool = pool[pool.apply(lambda row: family_allowed(row, spec.group), axis=1)]
    pool = pool.sort_values("h108_spec_score", ascending=False)

    selected_rows = []
    used_rows: set[int] = set()
    subject_counts: dict[str, int] = {}
    target_counts: dict[str, int] = {}
    q2_count = 0
    move_mat = np.zeros(base_shape, dtype=np.float64)

    for rec in pool.to_dict("records"):
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
        tmp[row, int(rec["target_index"])] = float(rec["h108_move"])
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
    selected["h097_move_col"] = "h108_move"
    return selected, move_mat


def materialize(base_prob: np.ndarray, move_mat: np.ndarray) -> np.ndarray:
    return clip_prob(sigmoid(logit(base_prob) + move_mat))


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
    spec: H108Spec,
    path: Path,
) -> dict[str, object]:
    proxy = h097mod.H097Spec(
        name=spec.name,
        mode="decoder_jury_assignment_solver",
        target_group=spec.group,
        k=spec.max_cells,
        alpha=spec.amp,
        cap=spec.cap,
        min_score=spec.min_score,
        worldview=spec.worldview,
    )
    out = h097mod.evaluate_candidate(candidate_id, prob, move_mat, base_prob, selected_cells, cell, sample, h098_fit, proxy, path)
    axis = h102mod.cumulative_axis_metrics(move_mat.reshape(-1), bad_axes, bad_moves, good_moves)
    out.update(axis)
    out["route_basis_pred_delta_vs_h057"] = route_pred(move_mat.reshape(-1), basis_fit_df, basis_fit_moves, route_fit)
    out["selected_mean_family_count"] = float(selected_cells["h108_family_count"].mean()) if len(selected_cells) else 0.0
    out["selected_mean_family_consensus"] = float(selected_cells["h108_family_consensus"].mean()) if len(selected_cells) else 0.0
    out["selected_mean_vote_weight"] = float(selected_cells["h108_vote_weight"].mean()) if len(selected_cells) else 0.0
    out["selected_mean_jury_score"] = float(selected_cells["h108_decoder_jury_score"].mean()) if len(selected_cells) else 0.0
    for family in FAMILIES:
        out[f"selected_{family.name}_cells"] = int(selected_cells[f"h108_has_{family.name}"].sum()) if len(selected_cells) else 0
    out["h108_score"] = (
        150.0 * (-float(out["model_pred_delta_vs_h057"]))
        + 115.0 * (-float(out["route_basis_pred_delta_vs_h057"]))
        + 0.20 * float(out["anti_h088_direction_rate"])
        + 0.16 * float(out["h057_positive_align_rate"])
        + 0.14 * float(out["selected_conflict_rate"])
        + 0.12 * float(out["selected_mean_family_consensus"])
        + 0.10 * min(float(out["selected_mean_family_count"]) / 4.0, 1.0)
        + 0.08 * float(out["selected_mean_jury_score"])
        + 0.08 * max(float(out["h102_cum_good_bad_margin"]), 0.0)
        + 0.06 * max(-float(out["h102_cum_h088_axis_cos"]), 0.0)
        - 0.60 * max(float(out["h102_cum_bad_weighted_pos"]), 0.0)
        - 0.38 * max(float(out["h102_cum_bad_max_pos"]), 0.0)
        - 0.34 * max(float(out["h102_cum_h088_axis_cos"]), 0.0)
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
    ) = build_context()
    source, source_moves, source_weights = load_source_candidates(sample, base_prob)
    jury = build_jury_table(cell, source, source_moves, source_weights)

    candidate_rows = []
    selected_frames = []
    top_frames = []
    for spec in candidate_specs():
        selected_cells, move_mat = select_cells(jury, spec, base_prob.shape, bad_axes, bad_moves, good_moves)
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
        candidate_id = safe_id(f"h108_{spec.name}_{hash_id}", 128)
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
        top = jury.sort_values("h108_decoder_jury_score", ascending=False).head(260).copy()
        top.insert(0, "candidate_id", candidate_id)
        top_frames.append(top)

    candidates = pd.DataFrame(candidate_rows)
    if candidates.empty:
        raise RuntimeError("no H108 candidates")
    candidates = candidates.sort_values(["h108_score", "model_pred_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True)
    selected = candidates.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"submission_h108_jury_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)

    decision = {
        "decision": "promote_h108_decoder_jury_assignment_solver",
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

    source.to_csv(OUT / "h108_source_candidates.csv", index=False)
    jury.to_csv(OUT / "h108_jury_table.csv", index=False)
    candidates.to_csv(OUT / "h108_candidates.csv", index=False)
    pd.concat(selected_frames, ignore_index=True).to_csv(OUT / "h108_selected_cells.csv", index=False)
    pd.concat(top_frames, ignore_index=True).to_csv(OUT / "h108_top_jury_cells.csv", index=False)
    bad_axes.to_csv(OUT / "h108_bad_axes.csv", index=False)
    pd.DataFrame([decision]).to_csv(OUT / "h108_decision.csv", index=False)

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
        "anti_h088_direction_rate",
        "h057_positive_align_rate",
        "selected_mean_family_count",
        "selected_mean_family_consensus",
        "selected_mean_vote_weight",
        "h108_score",
        "file",
    ]
    report = f"""# H108 Decoder-Jury Assignment Solver HS-JEPA

Question: is the action-grade row-target field the intersection of independent
HS-JEPA decoders rather than any single decoder family?

Source candidates:

{md_table(source[["family", "candidate_id", "weight", "score_rank", "route_basis_pred_delta_vs_h057", "model_pred_delta_vs_h057"]], 40)}

Candidates:

{md_table(candidates[cols], 20)}

Decision:

{md_table(pd.DataFrame([decision]), 1)}

Interpretation rule:

- If H108 improves over the individual H103-H107 branches, decoder-family
  consensus is closer to the hidden public/private assignment law than any
  single decoder.
- If H108 loses while one branch wins, the action equation is branch-specific
  and consensus averaging destroys useful structure.
- If all H103-H108 lose, the current solver basis is diagnostic only and the
  next breakthrough must identify a new public subset sensor.
"""
    (OUT / "h108_report.md").write_text(report, encoding="utf-8")

    print(f"selected={decision['selected_candidate_id']}")
    print(f"root={root_path}")
    print(candidates[cols].head(10).to_string(index=False))


if __name__ == "__main__":
    run()
