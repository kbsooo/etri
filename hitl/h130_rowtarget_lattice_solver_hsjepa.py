#!/usr/bin/env python3
"""H130: row-target lattice equation solver HS-JEPA.

H129 found that toxicity can live inside the H122 sparse core, not only in late
H128 tails.  H130 turns H122/H128/H129 into a small row-target lattice:
each active cell can be off, damped, kept, or switched to a later candidate
move.  The experiment asks whether public/private safety is a per-cell state
assignment problem rather than a single start-field choice.
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
OUT = HITL / "h130_rowtarget_lattice_solver_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H129_PATH = HITL / "h129_toxic_action_eraser_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h129mod_h130", H129_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H129_PATH}")
h129mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h129mod
SPEC.loader.exec_module(h129mod)

h128mod = h129mod.h128mod
h126mod = h129mod.h126mod
h123mod = h129mod.h123mod
h118mod = h129mod.h118mod
h115mod = h129mod.h115mod
h102mod = h129mod.h102mod
h085mod = h129mod.h085mod

TARGETS = h129mod.TARGETS
TOL = h129mod.TOL


@dataclass(frozen=True)
class H130Spec:
    name: str
    group: str
    start_name: str
    support: str
    max_steps: int
    min_step_score: float
    max_cells: int
    max_rows: int
    max_per_subject: int
    max_per_target: int
    amp: float
    cap: float
    pool_top: int
    min_score: float
    min_residual_gap: float
    max_residual_toxicity: float
    min_residual_safety: float
    max_bad_weighted_pos: float
    max_bad_max_pos: float
    max_h088_cos: float
    min_good_margin: float
    route_pred_cap: float
    h098_pred_cap: float
    max_curv_marg: float
    max_h088_hard_cosine: float
    min_component_gain: float
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


def materialize(base_prob: np.ndarray, move_mat: np.ndarray) -> np.ndarray:
    return clip_prob(sigmoid(logit(base_prob) + move_mat))


def rank01(values: np.ndarray, high: bool = True) -> np.ndarray:
    return h085mod.rank01(np.asarray(values, dtype=np.float64), high=high)


def nonzero_keys(move: np.ndarray) -> set[tuple[int, int]]:
    return h126mod.nonzero_keys(move)


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h130_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h130_lattice_*.csv"):
        path.unlink()


def candidate_specs() -> list[H130Spec]:
    common = dict(
        max_cells=40,
        max_rows=34,
        max_per_subject=26,
        max_per_target=22,
        amp=1.0,
        cap=0.30,
        pool_top=260,
        min_score=0.0,
        min_residual_gap=-0.30,
        max_residual_toxicity=0.95,
        min_residual_safety=0.0,
        max_bad_weighted_pos=0.0005,
        max_bad_max_pos=0.0020,
        max_curv_marg=0.000062,
        max_h088_hard_cosine=-0.018,
        min_component_gain=0.00018,
    )
    return [
        H130Spec(
            name="h129_core_plus_h128_value",
            group="core_erase_value_add",
            start_name="h129",
            support="core_plus_value",
            max_steps=10,
            min_step_score=0.00016,
            max_h088_cos=-0.050,
            min_good_margin=0.130,
            route_pred_cap=-0.000605,
            h098_pred_cap=-0.000022,
            worldview="H129's core eraser may be right, but should optionally re-add H128 conflict-value cells if they improve the lattice equation",
            **common,
        ),
        H130Spec(
            name="h128_value_with_core_eraser",
            group="value_erase",
            start_name="h128",
            support="core_plus_value",
            max_steps=12,
            min_step_score=0.00018,
            max_h088_cos=-0.044,
            min_good_margin=0.180,
            route_pred_cap=-0.000690,
            h098_pred_cap=-0.000027,
            worldview="H128's value field can survive only if toxic Q1/Q3 core amplitudes are solved jointly, not after the fact",
            **common,
        ),
        H130Spec(
            name="h122_full_lattice",
            group="support_refit",
            start_name="h122",
            support="all_known",
            max_steps=14,
            min_step_score=0.00016,
            max_h088_cos=-0.052,
            min_good_margin=0.125,
            route_pred_cap=-0.000600,
            h098_pred_cap=-0.000020,
            worldview="the public/private equation is a lattice over all discovered action states, not the H122/H129/H128 handoff order",
            **common,
        ),
        H130Spec(
            name="h129_core_conservative_refit",
            group="core_refit",
            start_name="h129",
            support="core_only",
            max_steps=8,
            min_step_score=0.00015,
            max_h088_cos=-0.060,
            min_good_margin=0.128,
            route_pred_cap=-0.000605,
            h098_pred_cap=-0.000022,
            worldview="if H129 is directionally right, a conservative core-only lattice should refine off/half/full Q1/Q3 decisions",
            **common,
        ),
    ]


def root_submission_paths() -> dict[str, Path]:
    paths = h129mod.root_submission_paths()
    paths["h129"] = ROOT / "submission_h129_toxiceraser_ce1ebc19_uploadsafe.csv"
    return paths


def load_move(name: str, sample: pd.DataFrame, base_prob: np.ndarray) -> np.ndarray:
    path = root_submission_paths()[name]
    if not path.exists():
        raise FileNotFoundError(path)
    return h126mod.load_move_path(path, sample, base_prob).reshape(base_prob.shape)


def known_hashes(sample: pd.DataFrame) -> set[str]:
    hashes: set[str] = set()
    for path in ROOT.glob("submission_h*_uploadsafe.csv"):
        try:
            df = h085mod.load_sub(path, sample)
            hashes.add(short_hash(df[TARGETS].to_numpy(dtype=np.float64)))
        except Exception:
            continue
    return hashes


def build_catalog(scored: pd.DataFrame) -> pd.DataFrame:
    catalog = h129mod.add_toxicity_scores(h129mod.build_catalog(scored))
    for name in ["h122", "h124", "h126", "h127", "h128", "h129"]:
        selected = h129mod.selected_for_source(name)
        if selected.empty:
            continue
        flags = set(zip(selected["row"].astype(int), selected["target_index"].astype(int)))
        catalog[f"h130_in_{name}"] = [
            1.0 if (int(row), int(tidx)) in flags else 0.0
            for row, tidx in zip(catalog["row"].astype(int), catalog["target_index"].astype(int))
        ]
    for name in ["h122", "h124", "h126", "h127", "h128", "h129"]:
        col = f"h130_in_{name}"
        if col not in catalog.columns:
            catalog[col] = 0.0
    return catalog


def evaluate_matrix(move_mat, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes):
    return h129mod.evaluate_matrix(
        move_mat,
        basis_fit_df,
        basis_fit_moves,
        route_fit,
        cell,
        h098_fit,
        fit,
        pool,
        bad_axes,
        bad_moves,
        good_moves,
        axes,
    )


def support_keys(spec: H130Spec, moves: dict[str, np.ndarray]) -> set[tuple[int, int]]:
    core = nonzero_keys(moves["h122"])
    value = nonzero_keys(moves["h128"]) - nonzero_keys(moves["h127"])
    h129 = nonzero_keys(moves["h129"])
    if spec.support == "core_only":
        return set(core)
    if spec.support == "core_plus_value":
        return set(core | h129 | value)
    if spec.support == "all_known":
        keys: set[tuple[int, int]] = set()
        for name in ["h122", "h124", "h126", "h127", "h128", "h129"]:
            keys |= nonzero_keys(moves[name])
        return keys
    raise ValueError(spec.support)


def option_values(row: int, tidx: int, spec: H130Spec, moves: dict[str, np.ndarray]) -> list[tuple[str, float]]:
    vals: list[tuple[str, float]] = [("off", 0.0)]
    for name in ["h122", "h124", "h126", "h127", "h128", "h129"]:
        val = float(moves[name][row, tidx])
        if abs(val) > 1.0e-12:
            vals.append((name, val))
            vals.append((f"{name}_half", 0.5 * val))
            if name in {"h122", "h128"}:
                vals.append((f"{name}_075", 0.75 * val))
    # Preserve order while deduplicating almost identical values.
    out: list[tuple[str, float]] = []
    seen: set[float] = set()
    for label, val in vals:
        key = round(float(val), 12)
        if key in seen:
            continue
        seen.add(key)
        out.append((label, float(val)))
    return out


def check_constraints(move_mat: np.ndarray, evald: dict[str, float], spec: H130Spec) -> bool:
    cells = len(nonzero_keys(move_mat))
    if cells > spec.max_cells:
        return False
    rows = int((np.abs(move_mat).sum(axis=1) > 1.0e-12).sum())
    if rows > spec.max_rows:
        return False
    target_counts = np.count_nonzero(np.abs(move_mat) > 1.0e-12, axis=0)
    if int(target_counts.max()) > spec.max_per_target:
        return False
    if evald["badw"] > spec.max_bad_weighted_pos or evald["badmax"] > spec.max_bad_max_pos:
        return False
    if evald["h088"] > spec.max_h088_cos or evald["margin"] < spec.min_good_margin:
        return False
    if evald["route"] > spec.route_pred_cap or evald["h098"] > spec.h098_pred_cap:
        return False
    if evald["curv_marg"] > spec.max_curv_marg:
        return False
    return True


def step_score(after: dict[str, float], before: dict[str, float], toxic_rank: float, changed_to: float, old: float) -> float:
    removed = abs(changed_to) < abs(old) - 1.0e-12
    added = abs(changed_to) > abs(old) + 1.0e-12
    return (
        280.0 * (-(after["h098"] - before["h098"]))
        + 170.0 * (-(after["curv_marg"] - before["curv_marg"]))
        + 170.0 * max(-(after["route"] - before["route"]), 0.0)
        - 90.0 * max(after["route"] - before["route"], 0.0)
        + 0.24 * (after["margin"] - before["margin"])
        + 0.16 * (-(after["h088"] - before["h088"]))
        - 5.0 * (after["badw"] - before["badw"])
        + (0.0007 * toxic_rank if removed else 0.0)
        - (0.0004 * toxic_rank if added else 0.0)
    )


def lattice_frame(catalog: pd.DataFrame, keys: set[tuple[int, int]]) -> pd.DataFrame:
    frame = catalog[[((int(row), int(tidx)) in keys) for row, tidx in zip(catalog["row"], catalog["target_index"])]].copy()
    if frame.empty:
        return frame
    frame["h130_active_toxic_rank"] = rank01(frame["h129_toxicity_field"].to_numpy(dtype=np.float64), high=True)
    frame["h130_priority"] = (
        0.35 * frame["h130_active_toxic_rank"].to_numpy(dtype=np.float64)
        + 0.20 * frame["h129_toxic_rank"].to_numpy(dtype=np.float64)
        + 0.15 * frame["h130_in_h128"].to_numpy(dtype=np.float64)
        + 0.15 * frame["h130_in_h129"].to_numpy(dtype=np.float64)
        + 0.10 * frame["h057_h088_anti_conflict"].fillna(0.0).to_numpy(dtype=np.float64)
        + 0.05 * frame["h057_h088_same_conflict"].fillna(0.0).to_numpy(dtype=np.float64)
    )
    return frame.sort_values(["h130_priority", "h130_active_toxic_rank"], ascending=[False, False]).reset_index(drop=True)


def coordinate_solve(start: np.ndarray, lattice: pd.DataFrame, spec: H130Spec, moves: dict[str, np.ndarray], basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes) -> tuple[np.ndarray, pd.DataFrame, dict[str, float], dict[str, float]]:
    move_mat = start.copy()
    start_eval = evaluate_matrix(move_mat, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
    operations = []
    touched: set[tuple[int, int]] = set()
    for step in range(spec.max_steps):
        before = evaluate_matrix(move_mat, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
        best = None
        for rec in lattice.head(spec.pool_top).to_dict("records"):
            row = int(rec["row"])
            tidx = int(rec["target_index"])
            key = (row, tidx)
            if key in touched:
                continue
            old = float(move_mat[row, tidx])
            for label, val in option_values(row, tidx, spec, moves):
                if abs(val - old) <= 1.0e-12:
                    continue
                tmp = move_mat.copy()
                tmp[row, tidx] = val
                after = evaluate_matrix(tmp, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
                if not check_constraints(tmp, after, spec):
                    continue
                score = step_score(after, before, float(rec.get("h130_active_toxic_rank", 0.0)), val, old)
                if best is None or score > best["h130_step_score"]:
                    best = {
                        "step": step + 1,
                        "row": row,
                        "target_index": tidx,
                        "target": str(rec["target"]),
                        "subject_id": str(rec.get("subject_id", "")),
                        "sleep_date": str(rec.get("sleep_date", "")),
                        "old_move": old,
                        "new_move": float(val),
                        "state": label,
                        "h130_active_toxic_rank": float(rec.get("h130_active_toxic_rank", 0.0)),
                        "h129_toxicity_field": float(rec.get("h129_toxicity_field", 0.0)),
                        "h112_residual_toxicity": float(rec.get("h112_residual_toxicity", 0.0)),
                        "h112_residual_safety": float(rec.get("h112_residual_safety", 0.0)),
                        "h112_residual_gap": float(rec.get("h112_residual_gap", 0.0)),
                        "h130_step_score": score,
                        **{f"after_{key2}": value for key2, value in after.items()},
                        **{f"delta_{key2}": after[key2] - before[key2] for key2 in after},
                    }
        if best is None or float(best["h130_step_score"]) < spec.min_step_score:
            break
        move_mat[int(best["row"]), int(best["target_index"])] = float(best["new_move"])
        touched.add((int(best["row"]), int(best["target_index"])))
        operations.append(best)
    final_eval = evaluate_matrix(move_mat, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
    return move_mat, pd.DataFrame(operations), start_eval, final_eval


def make_selected(catalog: pd.DataFrame, move_mat: np.ndarray) -> pd.DataFrame:
    keys = nonzero_keys(move_mat)
    selected = catalog[[((int(row), int(tidx)) in keys) for row, tidx in zip(catalog["row"], catalog["target_index"])]].copy()
    selected = selected.sort_values(["row", "target_index"]).drop_duplicates(["row", "target_index"], keep="last").reset_index(drop=True)
    selected["h130_actual_move"] = [
        float(move_mat[int(row), int(tidx)])
        for row, tidx in zip(selected["row"].astype(int), selected["target_index"].astype(int))
    ]
    selected = selected[np.abs(selected["h130_actual_move"].to_numpy(dtype=np.float64)) > 1.0e-12].copy()
    selected["h112_move"] = selected["h130_actual_move"].to_numpy(dtype=np.float64)
    selected["h097_move_col"] = "h112_move"
    return selected.sort_values(["row", "target_index"]).reset_index(drop=True)


def operation_summary(ops: pd.DataFrame) -> dict[str, object]:
    if ops.empty:
        return {
            "h130_ops": 0,
            "h130_off_ops": 0,
            "h130_damp_ops": 0,
            "h130_add_ops": 0,
            "h130_op_targets": "",
            "h130_mean_toxic_rank": 0.0,
            "h130_mean_step_score": 0.0,
        }
    old_abs = np.abs(ops["old_move"].to_numpy(dtype=np.float64))
    new_abs = np.abs(ops["new_move"].to_numpy(dtype=np.float64))
    return {
        "h130_ops": int(len(ops)),
        "h130_off_ops": int(np.isclose(new_abs, 0.0).sum()),
        "h130_damp_ops": int(((new_abs > 1.0e-12) & (new_abs < old_abs - 1.0e-12)).sum()),
        "h130_add_ops": int((new_abs > old_abs + 1.0e-12).sum()),
        "h130_op_targets": ";".join(f"{k}:{v}" for k, v in ops["target"].value_counts().to_dict().items()),
        "h130_mean_toxic_rank": float(ops["h130_active_toxic_rank"].mean()),
        "h130_mean_step_score": float(ops["h130_step_score"].mean()),
    }


def run() -> None:
    cleanup_previous_outputs()
    pool, _public, sample, base_prob, cell, h098_fit, route_fit, basis_fit_df, basis_fit_moves, bad_axes, bad_moves, good_moves, axes, fit, model_scores, props = h118mod.prepare_context()
    scored = h123mod.build_scored_pool(pool, base_prob, fit, bad_axes, bad_moves, good_moves, axes, props)
    catalog = build_catalog(scored)
    moves = {name: load_move(name, sample, base_prob) for name in ["h122", "h124", "h126", "h127", "h128", "h129"]}
    known = known_hashes(sample)
    previous = {
        "h129": moves["h129"].reshape(-1),
        "h128": moves["h128"].reshape(-1),
        "h127": moves["h127"].reshape(-1),
        "h126": moves["h126"].reshape(-1),
        "h124": moves["h124"].reshape(-1),
        "h122": moves["h122"].reshape(-1),
        "h088": load_move("h088", sample, base_prob).reshape(-1),
        "h018": load_move("h018", sample, base_prob).reshape(-1),
    }

    candidate_rows = []
    selected_frames = []
    op_frames = []
    audit_rows = []
    start_rows = []
    for spec in candidate_specs():
        start_move = load_move(spec.start_name, sample, base_prob)
        keys = support_keys(spec, moves)
        lattice = lattice_frame(catalog, keys)
        start_eval = evaluate_matrix(start_move, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
        start_rows.append({"start_name": spec.start_name, "spec_name": spec.name, **start_eval, "start_cells": int((np.abs(start_move) > 1.0e-12).sum()), "lattice_cells": int(len(lattice))})
        audit_rows.append({"spec_name": spec.name, "start_name": spec.start_name, "support": spec.support, "lattice_cells": int(len(lattice)), "lattice_mean_priority": float(lattice["h130_priority"].mean()) if not lattice.empty else 0.0})
        if lattice.empty:
            continue
        move_mat, ops, before, final = coordinate_solve(
            start_move,
            lattice,
            spec,
            moves,
            basis_fit_df,
            basis_fit_moves,
            route_fit,
            cell,
            h098_fit,
            fit,
            pool,
            bad_axes,
            bad_moves,
            good_moves,
            axes,
        )
        if ops.empty:
            continue
        component_gain = (
            280.0 * (-(final["h098"] - before["h098"]))
            + 170.0 * (-(final["curv_marg"] - before["curv_marg"]))
            + 170.0 * max(-(final["route"] - before["route"]), 0.0)
            - 90.0 * max(final["route"] - before["route"], 0.0)
            + 0.24 * (final["margin"] - before["margin"])
            + 0.16 * (-(final["h088"] - before["h088"]))
        )
        audit_rows[-1]["ops"] = int(len(ops))
        audit_rows[-1]["component_gain"] = float(component_gain)
        if component_gain < spec.min_component_gain:
            continue
        prob = materialize(base_prob, move_mat)
        hash_id = short_hash(prob)
        if hash_id in known:
            audit_rows[-1]["duplicate_hash"] = hash_id
            continue
        candidate_id = safe_id(f"h130_{spec.name}_{hash_id}", 128)
        path = OUT / f"submission_{candidate_id}.csv"
        h085mod.write_submission(sample, prob, path)
        selected_cells = make_selected(catalog, move_mat)
        axis = h102mod.cumulative_axis_metrics(move_mat.reshape(-1), bad_axes, bad_moves, good_moves)
        op_diag = operation_summary(ops)
        diag = {
            "h118_zero_curv": -0.0002616634510263019,
            "h118_curv_pred_delta_vs_h057": final["curv_marg"] - 0.0002616634510263019,
            "h118_curv_marginal_vs_zero": final["curv_marg"],
            "h118_mean_forbidden_same": float(selected_cells.get("h117_forbidden_same", pd.Series([0.0])).astype(float).mean()),
            "h118_max_forbidden_same": float(selected_cells.get("h117_forbidden_same", pd.Series([0.0])).astype(float).max()),
            "h118_mean_forbidden_pressure": float(selected_cells.get("h117_forbidden_pressure", pd.Series([0.0])).astype(float).mean()),
            "h118_mean_veto_score": float(selected_cells.get("h118_forbidden_veto_score", pd.Series([1.0])).astype(float).mean()),
            "h118_selected_rows": int(selected_cells["row"].nunique()),
            "h130_start_field": spec.start_name,
            "h130_start_cells": int((np.abs(start_move) > 1.0e-12).sum()),
            "h130_lattice_cells": int(len(lattice)),
            "h130_component_gain": float(component_gain),
            "h130_delta_start_route": float(final["route"] - before["route"]),
            "h130_delta_start_h098": float(final["h098"] - before["h098"]),
            "h130_delta_start_h088": float(final["h088"] - before["h088"]),
            "h130_delta_start_margin": float(final["margin"] - before["margin"]),
            **op_diag,
        }
        metrics = h118mod.evaluate_candidate(
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
            diag,
            previous,
        )
        h088_cos = float(metrics.get("h118_h088_cosine", 0.0))
        if h088_cos > spec.max_h088_hard_cosine:
            continue
        metrics["h130_worldview"] = spec.worldview
        metrics["h130_fit_feature_set"] = fit.feature_set
        metrics["h130_fit_alpha"] = fit.alpha
        metrics["h130_fit_score"] = fit.score
        metrics["h130_score"] = (
            305.0 * (-float(metrics["model_pred_delta_vs_h057"]))
            + 250.0 * (-float(metrics["route_basis_pred_delta_vs_h057"]))
            + 115.0 * (-float(metrics["h118_curv_marginal_vs_zero"]))
            + 0.24 * float(metrics["h102_cum_good_bad_margin"])
            + 0.14 * max(-float(metrics["h102_cum_h088_axis_cos"]), 0.0)
            + 0.13 * float(metrics["selected_mean_residual_safety"])
            + 0.12 * float(metrics["selected_mean_residual_gap"])
            - 0.15 * float(metrics["selected_mean_residual_toxicity"])
            + 1.1 * max(component_gain, 0.0)
            + 0.0015 * float(op_diag["h130_mean_toxic_rank"])
            - 0.012 * max(float(metrics["selected_cells"]) - 36.0, 0.0)
            - 20.0 * max(float(metrics["hard_diag_delta_vs_h057"]), 0.0)
            - 0.8 * max(h088_cos, 0.0)
        )
        candidate_rows.append(metrics)
        selected2 = selected_cells.copy()
        if "candidate_id" in selected2.columns:
            selected2 = selected2.drop(columns=["candidate_id"])
        selected2.insert(0, "candidate_id", candidate_id)
        selected_frames.append(selected2)
        ops2 = ops.copy()
        ops2.insert(0, "candidate_id", candidate_id)
        op_frames.append(ops2)

    audit = pd.DataFrame(audit_rows)
    starts = pd.DataFrame(start_rows)
    candidates = pd.DataFrame(candidate_rows)
    catalog.to_csv(OUT / "h130_catalog.csv", index=False)
    audit.to_csv(OUT / "h130_audit.csv", index=False)
    starts.to_csv(OUT / "h130_start_metrics.csv", index=False)
    model_scores.to_csv(OUT / "h130_curvature_model_scores.csv", index=False)
    if candidates.empty:
        report = f"""# H130 Row-Target Lattice Solver HS-JEPA

No candidate was promoted.

Audit:

{md_table(audit, 20)}

Start metrics:

{md_table(starts, 20)}
"""
        (OUT / "h130_report.md").write_text(report, encoding="utf-8")
        print("H130 promoted no candidate")
        print(audit.to_string(index=False))
        return

    candidates = candidates.sort_values(["h130_score", "h130_component_gain", "model_pred_delta_vs_h057"], ascending=[False, False, True]).reset_index(drop=True)
    selected = candidates.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"submission_h130_lattice_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)
    decision = {
        "decision": "promote_h130_rowtarget_lattice_solver",
        "selected_candidate_id": selected["candidate_id"],
        "root_uploadsafe_path": str(root_path),
        "worldview": selected["h130_worldview"],
        **selected,
        **{f"root_{key}": value for key, value in validation.items()},
    }
    candidates.to_csv(OUT / "h130_candidates.csv", index=False)
    pd.concat(selected_frames, ignore_index=True).to_csv(OUT / "h130_selected_cells.csv", index=False)
    pd.concat(op_frames, ignore_index=True).to_csv(OUT / "h130_operations.csv", index=False)
    pd.DataFrame([decision]).to_csv(OUT / "h130_decision.csv", index=False)

    cols = [
        "candidate_id",
        "spec_name",
        "h130_start_field",
        "selected_cells",
        "changed_rows_vs_h057",
        "Q1_changed_vs_h057",
        "Q2_changed_vs_h057",
        "Q3_changed_vs_h057",
        "S1_changed_vs_h057",
        "S2_changed_vs_h057",
        "S3_changed_vs_h057",
        "S4_changed_vs_h057",
        "h130_ops",
        "h130_off_ops",
        "h130_damp_ops",
        "h130_add_ops",
        "h130_op_targets",
        "h130_delta_start_route",
        "h130_delta_start_h098",
        "h130_delta_start_h088",
        "h130_delta_start_margin",
        "model_pred_delta_vs_h057",
        "route_basis_pred_delta_vs_h057",
        "h102_cum_h088_axis_cos",
        "h102_cum_good_bad_margin",
        "h130_component_gain",
        "h130_score",
        "file",
    ]
    report = f"""# H130 Row-Target Lattice Solver HS-JEPA

Question: can HS-JEPA solve public/private safety as a lattice over
row-target action states instead of choosing one start field?

Audit:

{md_table(audit, 20)}

Start metrics:

{md_table(starts, 20)}

Candidates:

{md_table(candidates[cols], 20)}

Decision:

{md_table(pd.DataFrame([decision]), 1)}

Interpretation rule:

- If H130 improves, HS-JEPA needs a row-target lattice decoder over
  off/damp/keep/add states.
- If H129 improves more, the lattice overfit local sensors and the core eraser
  should remain the simpler toxicity decoder.
- If H128 improves more, value regeneration should not be mixed with core
  erasure yet.
"""
    (OUT / "h130_report.md").write_text(report, encoding="utf-8")
    print("H130 selected candidate")
    print(candidates[cols].head(10).to_string(index=False))
    print("\nDecision")
    print(pd.DataFrame([decision])[["decision", "selected_candidate_id", "root_uploadsafe_path", "root_upload_safe"]].to_string(index=False))


if __name__ == "__main__":
    run()
