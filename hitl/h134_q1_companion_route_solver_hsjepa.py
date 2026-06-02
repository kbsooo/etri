#!/usr/bin/env python3
"""H134: Q1 companion-route assignment HS-JEPA.

H133 showed that several Q1 actions look toxic under the public/private
equation, but pure Q1 deletion damaged the good-bad margin.  H134 tests the
next hidden-world hypothesis:

    the Q1 subjective-state residue should be converted into companion
    objective/quality routes, not simply erased.

H088/H018 remain stress diagnostics.  They can reject shortcut actions, but
they are not treated as private action heads.
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
OUT = HITL / "h134_q1_companion_route_solver_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H133_PATH = HITL / "h133_targetsplit_assignment_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h133mod_h134", H133_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H133_PATH}")
h133mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h133mod
SPEC.loader.exec_module(h133mod)

h132mod = h133mod.h132mod
h131mod = h133mod.h131mod
h130mod = h133mod.h130mod
h126mod = h133mod.h126mod
h123mod = h133mod.h123mod
h118mod = h133mod.h118mod
h102mod = h133mod.h102mod
h085mod = h133mod.h085mod

TARGETS = h133mod.TARGETS
TOL = h133mod.TOL


@dataclass(frozen=True)
class H134Spec:
    name: str
    group: str
    start_name: str
    row_source: str
    target_mode: str
    max_steps: int
    min_step_score: float
    min_non_h088_passes: int
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
    min_companion_score: float
    min_proposal_abs: float
    h088_weight: float
    margin_weight: float
    worldview: str


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def safe_id(text: str, limit: int = 132) -> str:
    return h085mod.safe_id(text, limit=limit)


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return h085mod.md_table(frame, n=n)


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h134_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h134_q1companion_*.csv"):
        path.unlink()


def root_submission_paths() -> dict[str, Path]:
    paths = h133mod.root_submission_paths()
    paths["h133"] = ROOT / "submission_h133_targetsplit_0cb376b8_uploadsafe.csv"
    paths["h132"] = ROOT / "submission_h132_bundletox_ee252845_uploadsafe.csv"
    paths["h131"] = ROOT / "submission_h131_dropout_18a917f0_uploadsafe.csv"
    paths["h130"] = ROOT / "submission_h130_lattice_69da8d10_uploadsafe.csv"
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


def nonzero_keys(move: np.ndarray) -> set[tuple[int, int]]:
    return h126mod.nonzero_keys(move)


def candidate_specs() -> list[H134Spec]:
    common = dict(
        max_per_subject=28,
        max_per_target=20,
        amp=1.0,
        cap=0.18,
        pool_top=180,
        min_score=0.0,
        min_residual_gap=-0.55,
        max_residual_toxicity=0.95,
        min_residual_safety=0.24,
        max_bad_weighted_pos=0.0006,
        max_bad_max_pos=0.0022,
        max_curv_marg=0.000066,
        max_h088_hard_cosine=-0.018,
    )
    return [
        H134Spec(
            name="h133_s_companion_margin_repair",
            group="q1_companion_s_margin_repair",
            start_name="h133",
            row_source="h133_q1_changed_rows",
            target_mode="s_companion",
            max_steps=5,
            min_step_score=0.00015,
            min_non_h088_passes=2,
            max_cells=30,
            max_rows=23,
            max_h088_cos=-0.060,
            min_good_margin=0.164,
            route_pred_cap=-0.000625,
            h098_pred_cap=-0.000018,
            min_component_gain=0.00008,
            min_companion_score=0.275,
            min_proposal_abs=0.014,
            h088_weight=0.004,
            margin_weight=0.035,
            worldview="H133's Q1 residue is not erased; it is reassigned into S companion routes that repair margin without obeying H088 as an action head",
            **common,
        ),
        H134Spec(
            name="h133_q3s_companion_assignment",
            group="q1_companion_q3s_assignment",
            start_name="h133",
            row_source="all_q1_bundle_rows",
            target_mode="q3s_companion",
            max_steps=6,
            min_step_score=0.00016,
            min_non_h088_passes=2,
            max_cells=31,
            max_rows=24,
            max_h088_cos=-0.058,
            min_good_margin=0.163,
            route_pred_cap=-0.000620,
            h098_pred_cap=-0.000018,
            min_component_gain=0.00010,
            min_companion_score=0.265,
            min_proposal_abs=0.012,
            h088_weight=0.004,
            margin_weight=0.028,
            worldview="Q1 toxicity is a row-state route-conversion problem; companion routes can include Q3 and objective S state",
            **common,
        ),
        H134Spec(
            name="h132_precompanion_q1state",
            group="q1_companion_before_extra_erase",
            start_name="h132",
            row_source="all_q1_bundle_rows",
            target_mode="q3s_companion",
            max_steps=6,
            min_step_score=0.00016,
            min_non_h088_passes=2,
            max_cells=31,
            max_rows=25,
            max_h088_cos=-0.058,
            min_good_margin=0.170,
            route_pred_cap=-0.000620,
            h098_pred_cap=-0.000018,
            min_component_gain=0.00009,
            min_companion_score=0.265,
            min_proposal_abs=0.012,
            h088_weight=0.003,
            margin_weight=0.026,
            worldview="before trusting H133's extra Q1 erasure, test whether H132 only needed companion conversion rather than more deletion",
            **common,
        ),
        H134Spec(
            name="h133_highconviction_s1s2",
            group="q1_companion_highconviction_s1s2",
            start_name="h133",
            row_source="all_q1_bundle_rows",
            target_mode="s1s2_companion",
            max_steps=4,
            min_step_score=0.00018,
            min_non_h088_passes=2,
            max_cells=29,
            max_rows=23,
            max_h088_cos=-0.060,
            min_good_margin=0.164,
            route_pred_cap=-0.000625,
            h098_pred_cap=-0.000018,
            min_component_gain=0.00007,
            min_companion_score=0.300,
            min_proposal_abs=0.018,
            h088_weight=0.003,
            margin_weight=0.032,
            worldview="the safest conversion field is narrow: Q1 residue should move only into high-confidence S1/S2 objective-state routes",
            **common,
        ),
    ]


def target_allowed(target: str, mode: str) -> bool:
    if mode == "s_companion":
        return target in {"S1", "S2", "S4"}
    if mode == "q3s_companion":
        return target in {"Q3", "S1", "S2", "S4"}
    if mode == "s1s2_companion":
        return target in {"S1", "S2"}
    raise ValueError(mode)


def collect_q1_rows(bundle_rows: pd.DataFrame) -> pd.DataFrame:
    if bundle_rows.empty:
        return bundle_rows.copy()
    rows = bundle_rows[bundle_rows["h133_row_bundle_targets"].astype(str).str.contains("Q1", regex=False)].copy()
    ops_path = HITL / "h133_targetsplit_assignment_hsjepa" / "h133_operations.csv"
    decision_path = HITL / "h133_targetsplit_assignment_hsjepa" / "h133_decision.csv"
    if ops_path.exists() and decision_path.exists():
        ops = pd.read_csv(ops_path)
        decision = pd.read_csv(decision_path)
        selected_id = str(decision["selected_candidate_id"].iloc[0])
        q1_ops = ops[(ops["candidate_id"].astype(str).eq(selected_id)) & (ops["target"].astype(str).eq("Q1"))].copy()
        if not q1_ops.empty:
            q1_summary = q1_ops.groupby("row", as_index=False).agg(
                h134_q1_op_count=("row", "size"),
                h134_q1_op_toxicity=("h133_cell_toxicity", "mean"),
                h134_q1_old_abs=("old_move", lambda x: float(np.mean(np.abs(x)))),
                h134_q1_removed_abs=("old_move", lambda x: float(np.sum(np.abs(x)))),
                h134_q1_state=("state", lambda x: ",".join(map(str, x))),
            )
            rows = rows.merge(q1_summary, on="row", how="left")
    for col in ["h134_q1_op_count", "h134_q1_op_toxicity", "h134_q1_old_abs", "h134_q1_removed_abs"]:
        if col not in rows.columns:
            rows[col] = 0.0
        rows[col] = rows[col].fillna(0.0)
    if "h134_q1_state" not in rows.columns:
        rows["h134_q1_state"] = ""
    rows["h134_q1_changed"] = (rows["h134_q1_op_count"].to_numpy(dtype=np.float64) > 0).astype(float)
    rows["h134_row_conversion_pressure"] = (
        0.34 * rows["h133_row_bundle_contradiction"].to_numpy(dtype=np.float64)
        + 0.20 * rows["h133_row_bundle_witness"].to_numpy(dtype=np.float64)
        + 0.18 * rows["h134_q1_changed"].to_numpy(dtype=np.float64)
        + 0.14 * rows["h134_q1_op_toxicity"].to_numpy(dtype=np.float64)
        + 0.08 * rows["h133_row_bundle_health"].to_numpy(dtype=np.float64)
        - 0.06 * rows["h133_row_bundle_bad_same"].to_numpy(dtype=np.float64)
    )
    return rows.sort_values("h134_row_conversion_pressure", ascending=False).reset_index(drop=True)


def select_rows(rows: pd.DataFrame, spec: H134Spec) -> pd.DataFrame:
    if spec.row_source == "h133_q1_changed_rows":
        return rows[rows["h134_q1_changed"].to_numpy(dtype=np.float64) > 0.0].copy()
    if spec.row_source == "all_q1_bundle_rows":
        return rows.copy()
    raise ValueError(spec.row_source)


def signed_base_proposal(rec: dict[str, object]) -> float:
    cols = [
        "proposal_move",
        "h128_actual_move",
        "h127_actual_move",
        "h126_actual_move",
        "h124_actual_move",
        "h122_actual_move",
        "source_mean_move",
        "h112_candidate_raw_move",
    ]
    vals = []
    for col in cols:
        try:
            val = float(rec.get(col, 0.0))
        except Exception:
            val = 0.0
        if np.isfinite(val) and abs(val) > 1.0e-12:
            vals.append((col, val))
    if not vals:
        return 0.0
    proposal = float(rec.get("proposal_move", 0.0))
    same = [(col, val) for col, val in vals if proposal == 0.0 or np.sign(val) == np.sign(proposal)]
    source = same if same else vals
    return max(source, key=lambda item: abs(item[1]))[1]


def build_cell_pool(catalog: pd.DataFrame, start_move: np.ndarray, q1_rows: pd.DataFrame, spec: H134Spec) -> pd.DataFrame:
    rows = select_rows(q1_rows, spec)
    if rows.empty:
        return catalog.iloc[0:0].copy()
    cand = catalog[catalog["row"].astype(int).isin(set(rows["row"].astype(int)))].copy()
    cand = cand[[target_allowed(str(t), spec.target_mode) for t in cand["target"]]].copy()
    if cand.empty:
        return cand
    cand = cand.merge(rows, on="row", how="left")
    if cand.empty:
        return cand
    cand["h134_start_move"] = [
        float(start_move[int(row), int(tidx)])
        for row, tidx in zip(cand["row"].astype(int), cand["target_index"].astype(int))
    ]
    cand["h134_base_proposal"] = [signed_base_proposal(rec) for rec in cand.to_dict("records")]
    target_bonus = cand["target"].astype(str).map({"S2": 0.060, "S1": 0.045, "Q3": 0.035, "S4": 0.020}).fillna(0.0).to_numpy(dtype=np.float64)
    proposal_abs = np.minimum(np.abs(cand["h134_base_proposal"].to_numpy(dtype=np.float64)) / 0.16, 1.0)
    family = np.minimum(cand.get("source_family_count", pd.Series([0.0] * len(cand))).astype(float).to_numpy(), 3.0) / 3.0
    source_strength = np.minimum(cand.get("h131_source_strength", pd.Series([0.0] * len(cand))).astype(float).to_numpy(), 1.0)
    gap = np.maximum(cand["h112_residual_gap"].to_numpy(dtype=np.float64), 0.0)
    cand["h134_companion_score"] = (
        0.20 * cand["h131_add_evidence"].to_numpy(dtype=np.float64)
        + 0.18 * cand["h112_residual_safety"].to_numpy(dtype=np.float64)
        + 0.17 * cand["h131_residual_health"].to_numpy(dtype=np.float64)
        + 0.13 * gap
        + 0.08 * family
        + 0.06 * source_strength
        + 0.07 * proposal_abs
        + 0.07 * cand["h134_row_conversion_pressure"].to_numpy(dtype=np.float64)
        + target_bonus
        - 0.13 * cand["h112_residual_toxicity"].to_numpy(dtype=np.float64)
        - 0.11 * cand["h131_bad_same_pressure"].to_numpy(dtype=np.float64)
        - 0.09 * cand["h131_shortcut_pressure"].to_numpy(dtype=np.float64)
    )
    cand = cand[
        (cand["h134_companion_score"].to_numpy(dtype=np.float64) >= spec.min_companion_score)
        & (np.abs(cand["h134_base_proposal"].to_numpy(dtype=np.float64)) >= spec.min_proposal_abs)
        & (cand["h112_residual_safety"].to_numpy(dtype=np.float64) >= spec.min_residual_safety)
        & (cand["h112_residual_toxicity"].to_numpy(dtype=np.float64) <= spec.max_residual_toxicity)
    ].copy()
    return cand.sort_values(
        ["h134_companion_score", "h134_row_conversion_pressure", "h112_residual_safety"],
        ascending=[False, False, False],
    ).reset_index(drop=True)


def evaluate_matrix(move_mat, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes):
    return h133mod.evaluate_matrix(
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


def check_constraints(move_mat: np.ndarray, evald: dict[str, float], spec: H134Spec) -> bool:
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


def propose_values(old: float, base_proposal: float, spec: H134Spec) -> list[tuple[str, float]]:
    cap = float(spec.cap)
    base = float(np.clip(base_proposal, -cap, cap))
    values: list[tuple[str, float]] = []
    if abs(old) <= 1.0e-12:
        for frac in [0.25, 0.50, 0.75, 1.00]:
            val = float(np.clip(frac * base, -cap, cap))
            values.append((f"add_{frac:g}", val))
    else:
        for frac in [0.35, 0.60, 0.85]:
            val = float(np.clip(old + frac * (base - old), -cap, cap))
            values.append((f"toward_{frac:g}", val))
        if np.sign(old) == np.sign(base) and abs(base) > abs(old):
            val = float(np.clip(base, -cap, cap))
            values.append(("amplify_to_base", val))
    dedup = []
    seen: set[float] = set()
    for state, val in values:
        rounded = round(val, 12)
        if abs(val - old) <= 1.0e-12 or rounded in seen:
            continue
        seen.add(rounded)
        dedup.append((state, val))
    return dedup


def target_step_score(after: dict[str, float], before: dict[str, float], cell_rec: dict[str, object], spec: H134Spec) -> tuple[float, dict[str, float]]:
    d_route = after["route"] - before["route"]
    d_h098 = after["h098"] - before["h098"]
    d_curv = after["curv_marg"] - before["curv_marg"]
    d_badw = after["badw"] - before["badw"]
    d_badmax = after["badmax"] - before["badmax"]
    d_h088 = after["h088"] - before["h088"]
    d_margin = after["margin"] - before["margin"]
    comp = float(cell_rec["h134_companion_score"])
    pressure = float(cell_rec["h134_row_conversion_pressure"])

    route_view = (
        250.0 * (-d_h098)
        + 170.0 * max(-d_route, 0.0)
        - 110.0 * max(d_route, 0.0)
        + 145.0 * (-d_curv)
        + 0.00072 * comp
        + 0.00015 * pressure
    )
    no_h088_view = (
        225.0 * (-d_h098)
        + 155.0 * max(-d_route, 0.0)
        - 115.0 * max(d_route, 0.0)
        + 130.0 * (-d_curv)
        - 5.0 * max(d_badw, 0.0)
        - 3.0 * max(d_badmax, 0.0)
        + 0.00066 * comp
    )
    margin_view = (
        spec.margin_weight * d_margin
        + 0.00080 * comp
        + 0.00010 * pressure
        - 55.0 * max(d_h098, 0.0)
        - 45.0 * max(d_route, 0.0)
        - 45.0 * max(d_curv, 0.0)
    )
    assignment_view = (
        0.00130 * comp
        + 0.00018 * pressure
        - 70.0 * max(d_h098, 0.0)
        - 55.0 * max(d_route, 0.0)
        - 55.0 * max(d_curv, 0.0)
        - 3.0 * max(d_badw, 0.0)
        - 2.0 * max(d_badmax, 0.0)
    )
    stress_view = (
        spec.h088_weight * (-d_h088)
        + spec.margin_weight * d_margin
        - 4.0 * max(d_badw, 0.0)
        - 2.5 * max(d_badmax, 0.0)
        + 0.00014 * comp
    )
    scores = {
        "h134_route_view_score": float(route_view),
        "h134_no_h088_view_score": float(no_h088_view),
        "h134_margin_view_score": float(margin_view),
        "h134_assignment_view_score": float(assignment_view),
        "h134_stress_view_score": float(stress_view),
    }
    non_h088_keys = ["h134_route_view_score", "h134_no_h088_view_score", "h134_margin_view_score", "h134_assignment_view_score"]
    scores["h134_non_h088_passes"] = float(sum(scores[key] > 0.0 for key in non_h088_keys))
    scores["h134_stress_passes"] = float(sum(value > 0.0 for value in scores.values()))
    aggregate = 0.28 * route_view + 0.26 * no_h088_view + 0.22 * margin_view + 0.18 * assignment_view + 0.06 * stress_view
    scores["h134_step_score"] = float(aggregate)
    return float(aggregate), scores


def coordinate_solve(start: np.ndarray, pool_cells: pd.DataFrame, spec: H134Spec, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes) -> tuple[np.ndarray, pd.DataFrame, dict[str, float], dict[str, float]]:
    move_mat = start.copy()
    start_eval = evaluate_matrix(move_mat, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
    ops = []
    used: set[tuple[int, int]] = set()
    for step in range(spec.max_steps):
        before = evaluate_matrix(move_mat, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
        best = None
        for rec in pool_cells.head(spec.pool_top).to_dict("records"):
            row = int(rec["row"])
            tidx = int(rec["target_index"])
            if (row, tidx) in used:
                continue
            old = float(move_mat[row, tidx])
            base_proposal = float(rec["h134_base_proposal"])
            for state, val in propose_values(old, base_proposal, spec):
                tmp = move_mat.copy()
                tmp[row, tidx] = val
                after = evaluate_matrix(tmp, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
                if not check_constraints(tmp, after, spec):
                    continue
                score, view_scores = target_step_score(after, before, rec, spec)
                if view_scores["h134_non_h088_passes"] < spec.min_non_h088_passes:
                    continue
                if best is None or score > best["h134_step_score"]:
                    best = {
                        "step": step + 1,
                        "row": row,
                        "target_index": tidx,
                        "target": str(rec["target"]),
                        "subject_id": str(rec["subject_id"]),
                        "sleep_date": str(rec["sleep_date"]),
                        "old_move": old,
                        "new_move": float(val),
                        "state": state,
                        "h134_base_proposal": base_proposal,
                        "h134_companion_score": float(rec["h134_companion_score"]),
                        "h134_row_conversion_pressure": float(rec["h134_row_conversion_pressure"]),
                        "h134_q1_changed": float(rec["h134_q1_changed"]),
                        "h134_q1_op_toxicity": float(rec["h134_q1_op_toxicity"]),
                        "h112_residual_safety": float(rec["h112_residual_safety"]),
                        "h112_residual_toxicity": float(rec["h112_residual_toxicity"]),
                        "h112_residual_gap": float(rec["h112_residual_gap"]),
                        "h131_residual_health": float(rec["h131_residual_health"]),
                        "h131_add_evidence": float(rec["h131_add_evidence"]),
                        **view_scores,
                        **{f"after_{key}": value for key, value in after.items()},
                        **{f"delta_{key}": after[key] - before[key] for key in after},
                    }
        if best is None or float(best["h134_step_score"]) < spec.min_step_score:
            break
        move_mat[int(best["row"]), int(best["target_index"])] = float(best["new_move"])
        used.add((int(best["row"]), int(best["target_index"])))
        ops.append(best)
    final_eval = evaluate_matrix(move_mat, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
    return move_mat, pd.DataFrame(ops), start_eval, final_eval


def make_selected(catalog: pd.DataFrame, move_mat: np.ndarray) -> pd.DataFrame:
    selected = h130mod.make_selected(catalog, move_mat)
    if selected.empty:
        return selected
    selected["h134_actual_move"] = selected["h130_actual_move"]
    selected["h112_move"] = selected["h134_actual_move"].to_numpy(dtype=np.float64)
    return selected


def operation_summary(ops: pd.DataFrame) -> dict[str, object]:
    if ops.empty:
        return {
            "h134_ops": 0,
            "h134_add_ops": 0,
            "h134_toward_ops": 0,
            "h134_op_targets": "",
            "h134_mean_companion_score": 0.0,
            "h134_mean_non_h088_passes": 0.0,
            "h134_mean_step_score": 0.0,
        }
    return {
        "h134_ops": int(len(ops)),
        "h134_add_ops": int(ops["state"].astype(str).str.startswith("add_").sum()),
        "h134_toward_ops": int(ops["state"].astype(str).str.startswith("toward_").sum()),
        "h134_op_targets": ";".join(f"{k}:{v}" for k, v in ops["target"].value_counts().to_dict().items()),
        "h134_mean_companion_score": float(ops["h134_companion_score"].mean()),
        "h134_mean_non_h088_passes": float(ops["h134_non_h088_passes"].mean()),
        "h134_mean_step_score": float(ops["h134_step_score"].mean()),
    }


def component_gain(final: dict[str, float], before: dict[str, float], spec: H134Spec) -> float:
    return (
        240.0 * (-(final["h098"] - before["h098"]))
        + 150.0 * (-(final["curv_marg"] - before["curv_marg"]))
        + 130.0 * max(-(final["route"] - before["route"]), 0.0)
        - 90.0 * max(final["route"] - before["route"], 0.0)
        + spec.margin_weight * (final["margin"] - before["margin"])
        + spec.h088_weight * (-(final["h088"] - before["h088"]))
    )


def previous_moves(sample: pd.DataFrame, base_prob: np.ndarray, moves: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    prev = h133mod.previous_moves(sample, base_prob, {name: moves[name] for name in ["h122", "h124", "h126", "h127", "h128", "h129", "h130", "h131", "h132"]})
    prev["h133"] = moves["h133"].reshape(-1)
    return prev


def run() -> None:
    cleanup_previous_outputs()
    pool, _public, sample, base_prob, cell, h098_fit, route_fit, basis_fit_df, basis_fit_moves, bad_axes, bad_moves, good_moves, axes, fit, model_scores, props = h118mod.prepare_context()
    scored = h123mod.build_scored_pool(pool, base_prob, fit, bad_axes, bad_moves, good_moves, axes, props)
    catalog = h132mod.build_catalog(scored)
    moves = {name: load_move(name, sample, base_prob) for name in ["h122", "h124", "h126", "h127", "h128", "h129", "h130", "h131", "h132", "h133"]}
    known = known_hashes(sample)
    previous = previous_moves(sample, base_prob, moves)
    bundle_rows = h133mod.collect_bundle_rows(catalog, moves["h131"])
    q1_rows = collect_q1_rows(bundle_rows)

    candidate_rows = []
    selected_frames = []
    op_frames = []
    audit_rows = []
    start_rows = []
    pool_frames = []
    for spec in candidate_specs():
        start_move = moves[spec.start_name]
        pool_cells = build_cell_pool(catalog, start_move, q1_rows, spec)
        start_eval = evaluate_matrix(start_move, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
        start_rows.append({"start_name": spec.start_name, "spec_name": spec.name, **start_eval, "start_cells": int((np.abs(start_move) > 1.0e-12).sum()), "pool_cells": int(len(pool_cells))})
        audit_rows.append(
            {
                "spec_name": spec.name,
                "start_name": spec.start_name,
                "row_source": spec.row_source,
                "target_mode": spec.target_mode,
                "pool_cells": int(len(pool_cells)),
                "mean_companion_score": float(pool_cells["h134_companion_score"].mean()) if not pool_cells.empty else 0.0,
                "max_companion_score": float(pool_cells["h134_companion_score"].max()) if not pool_cells.empty else 0.0,
            }
        )
        if not pool_cells.empty:
            p2 = pool_cells.copy()
            p2.insert(0, "spec_name", spec.name)
            pool_frames.append(p2)
        if pool_cells.empty:
            continue
        move_mat, ops, before, final = coordinate_solve(
            start_move,
            pool_cells,
            spec,
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
        audit_rows[-1]["ops"] = int(len(ops))
        if ops.empty:
            continue
        gain = component_gain(final, before, spec)
        audit_rows[-1]["component_gain"] = float(gain)
        if gain < spec.min_component_gain:
            audit_rows[-1]["rejected_component_gain"] = float(gain)
            continue
        prob = h130mod.materialize(base_prob, move_mat)
        hash_id = short_hash(prob)
        if hash_id in known:
            audit_rows[-1]["duplicate_hash"] = hash_id
            continue
        candidate_id = safe_id(f"h134_{spec.name}_{hash_id}", 128)
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
            "h134_start_field": spec.start_name,
            "h134_start_cells": int((np.abs(start_move) > 1.0e-12).sum()),
            "h134_pool_cells": int(len(pool_cells)),
            "h134_component_gain": float(gain),
            "h134_delta_start_route": float(final["route"] - before["route"]),
            "h134_delta_start_h098": float(final["h098"] - before["h098"]),
            "h134_delta_start_h088": float(final["h088"] - before["h088"]),
            "h134_delta_start_margin": float(final["margin"] - before["margin"]),
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
            audit_rows[-1]["rejected_h088_hard_cosine"] = h088_cos
            continue
        metrics["h134_worldview"] = spec.worldview
        metrics["h134_fit_feature_set"] = fit.feature_set
        metrics["h134_fit_alpha"] = fit.alpha
        metrics["h134_fit_score"] = fit.score
        metrics["h134_score"] = (
            300.0 * (-float(metrics["model_pred_delta_vs_h057"]))
            + 250.0 * (-float(metrics["route_basis_pred_delta_vs_h057"]))
            + 125.0 * (-float(metrics["h118_curv_marginal_vs_zero"]))
            + 0.14 * float(metrics["h102_cum_good_bad_margin"])
            + 0.05 * max(-float(metrics["h102_cum_h088_axis_cos"]), 0.0)
            + 0.15 * float(metrics["selected_mean_residual_safety"])
            + 0.15 * float(metrics["selected_mean_residual_gap"])
            - 0.17 * float(metrics["selected_mean_residual_toxicity"])
            + 1.2 * max(gain, 0.0)
            + 0.020 * float(op_diag["h134_mean_non_h088_passes"])
            + 0.015 * float(op_diag["h134_mean_companion_score"])
            - 0.010 * max(float(metrics["selected_cells"]) - 32.0, 0.0)
            - 18.0 * max(float(metrics["hard_diag_delta_vs_h057"]), 0.0)
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
    catalog.to_csv(OUT / "h134_catalog.csv", index=False)
    bundle_rows.to_csv(OUT / "h134_bundle_rows.csv", index=False)
    q1_rows.to_csv(OUT / "h134_q1_rows.csv", index=False)
    audit.to_csv(OUT / "h134_audit.csv", index=False)
    starts.to_csv(OUT / "h134_start_metrics.csv", index=False)
    model_scores.to_csv(OUT / "h134_curvature_model_scores.csv", index=False)
    if pool_frames:
        pd.concat(pool_frames, ignore_index=True).to_csv(OUT / "h134_cell_pool.csv", index=False)
    if candidates.empty:
        report = f"""# H134 Q1 Companion-Route Assignment HS-JEPA

No candidate was promoted.

Question: did H133's Q1 deletion damage margin because the subjective-state
residue should be converted into companion Q3/S routes?

Q1 rows:

{md_table(q1_rows, 20)}

Audit:

{md_table(audit, 20)}

Start metrics:

{md_table(starts, 20)}
"""
        (OUT / "h134_report.md").write_text(report, encoding="utf-8")
        print("H134 promoted no candidate")
        print(audit.to_string(index=False))
        return

    candidates = candidates.sort_values(["h134_score", "h134_component_gain", "model_pred_delta_vs_h057"], ascending=[False, False, True]).reset_index(drop=True)
    selected = candidates.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"submission_h134_q1companion_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)
    decision = {
        "decision": "promote_h134_q1_companion_route_assignment",
        "selected_candidate_id": selected["candidate_id"],
        "root_uploadsafe_path": str(root_path.resolve()),
        "worldview": selected["h134_worldview"],
        **selected,
        **{f"root_{key}": value for key, value in validation.items()},
    }
    candidates.to_csv(OUT / "h134_candidates.csv", index=False)
    pd.concat(selected_frames, ignore_index=True).to_csv(OUT / "h134_selected_cells.csv", index=False)
    pd.concat(op_frames, ignore_index=True).to_csv(OUT / "h134_operations.csv", index=False)
    pd.DataFrame([decision]).to_csv(OUT / "h134_decision.csv", index=False)

    cols = [
        "candidate_id",
        "spec_name",
        "h134_start_field",
        "selected_cells",
        "changed_rows_vs_h057",
        "Q1_changed_vs_h057",
        "Q2_changed_vs_h057",
        "Q3_changed_vs_h057",
        "S1_changed_vs_h057",
        "S2_changed_vs_h057",
        "S3_changed_vs_h057",
        "S4_changed_vs_h057",
        "h134_ops",
        "h134_add_ops",
        "h134_toward_ops",
        "h134_op_targets",
        "h134_mean_companion_score",
        "h134_mean_non_h088_passes",
        "h134_delta_start_route",
        "h134_delta_start_h098",
        "h134_delta_start_h088",
        "h134_delta_start_margin",
        "model_pred_delta_vs_h057",
        "route_basis_pred_delta_vs_h057",
        "h102_cum_h088_axis_cos",
        "h102_cum_good_bad_margin",
        "h134_component_gain",
        "h134_score",
        "file",
    ]
    report = f"""# H134 Q1 Companion-Route Assignment HS-JEPA

Question: H133's Q1-only toxicity signature improved route/H088 sensors but
hurt the good-bad margin.  Was the lost Q1 subjective-state residue supposed
to be reassigned into companion Q3/S routes instead of deleted?

Q1 conversion rows:

{md_table(q1_rows, 20)}

Audit:

{md_table(audit, 20)}

Start metrics:

{md_table(starts, 20)}

Candidates:

{md_table(candidates[cols], 20)}

Operations:

{md_table(pd.concat(op_frames, ignore_index=True), 60)}

Decision:

{md_table(pd.DataFrame([decision]), 1)}

Interpretation rule:

- If H134 beats H133 publicly, Q1 toxicity is not pure erasure; HS-JEPA needs a
  conservation-style route decoder that moves human-state mass into companion
  targets.
- If H133 beats H134, the companion conversion field is mostly action-tail
  hallucination and Q1 residue should stay a small target-specific deletion.
- If H132 beats both, H133's extra Q1 changes over-completed the public sensor
  equation.
"""
    (OUT / "h134_report.md").write_text(report, encoding="utf-8")
    print("H134 selected candidate")
    print(candidates[cols].head(10).to_string(index=False))
    print("\nDecision")
    print(pd.DataFrame([decision])[["decision", "selected_candidate_id", "root_uploadsafe_path", "root_upload_safe"]].to_string(index=False))


if __name__ == "__main__":
    run()
