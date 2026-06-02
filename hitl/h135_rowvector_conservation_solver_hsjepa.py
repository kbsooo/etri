#!/usr/bin/env python3
"""H135: row-vector conservation HS-JEPA.

H134 proved that Q1 companion conversion can survive from H132, but its greedy
cell-wise decoder missed an important clue: row 164's S1+S4 vector is stronger
than either cell alone under the route equation.  H135 therefore treats a row's
Q3/S companion set as an atomic action bundle.

Hypothesis:

    public/private safety is not a scalar cell property.  Some human-state
    residues become safe only when the same row's target vector is moved as a
    coherent route-conservation field.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import importlib.util
import itertools
import shutil
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HITL = ROOT / "hitl"
OUT = HITL / "h135_rowvector_conservation_solver_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H134_PATH = HITL / "h134_q1_companion_route_solver_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h134mod_h135", H134_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H134_PATH}")
h134mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h134mod
SPEC.loader.exec_module(h134mod)

h133mod = h134mod.h133mod
h132mod = h134mod.h132mod
h130mod = h134mod.h130mod
h126mod = h134mod.h126mod
h123mod = h134mod.h123mod
h118mod = h134mod.h118mod
h102mod = h134mod.h102mod
h085mod = h134mod.h085mod

TARGETS = h134mod.TARGETS


@dataclass(frozen=True)
class H135Spec:
    name: str
    group: str
    start_name: str
    row_source: str
    target_mode: str
    max_bundle_size: int
    frac_values: tuple[float, ...]
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
    min_bundle_score: float
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
    for path in OUT.glob("submission_h135_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h135_rowvector_*.csv"):
        path.unlink()


def root_submission_paths() -> dict[str, Path]:
    paths = h134mod.root_submission_paths()
    paths["h134"] = ROOT / "submission_h134_q1companion_ac53dd2e_uploadsafe.csv"
    paths["h133"] = ROOT / "submission_h133_targetsplit_0cb376b8_uploadsafe.csv"
    paths["h132"] = ROOT / "submission_h132_bundletox_ee252845_uploadsafe.csv"
    paths["h131"] = ROOT / "submission_h131_dropout_18a917f0_uploadsafe.csv"
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


def candidate_specs() -> list[H135Spec]:
    common = dict(
        max_per_subject=30,
        max_per_target=22,
        amp=1.0,
        cap=0.20,
        pool_top=160,
        min_score=0.0,
        min_residual_gap=-0.58,
        max_residual_toxicity=0.98,
        min_residual_safety=0.24,
        max_bad_weighted_pos=0.0006,
        max_bad_max_pos=0.0022,
        max_curv_marg=0.000068,
        max_h088_hard_cosine=-0.018,
    )
    return [
        H135Spec(
            name="h132_rowvector_margin_guard",
            group="rowvector_conservation_margin_guard",
            start_name="h132",
            row_source="all_q1_bundle_rows",
            target_mode="q3s_companion",
            max_bundle_size=2,
            frac_values=(0.25, 0.35),
            max_steps=4,
            min_step_score=0.00022,
            min_non_h088_passes=3,
            max_cells=32,
            max_rows=24,
            max_h088_cos=-0.060,
            min_good_margin=0.166,
            route_pred_cap=-0.000625,
            h098_pred_cap=-0.000018,
            min_component_gain=0.00020,
            min_companion_score=0.275,
            min_proposal_abs=0.012,
            min_bundle_score=0.47,
            h088_weight=0.0025,
            margin_weight=0.030,
            worldview="Q1 residue should be conserved as small row-vector Q3/S bundles while keeping the H132 safety margin alive",
            **common,
        ),
        H135Spec(
            name="h132_rowvector_route_heavy",
            group="rowvector_conservation_route_heavy",
            start_name="h132",
            row_source="all_q1_bundle_rows",
            target_mode="q3s_companion",
            max_bundle_size=2,
            frac_values=(0.35, 0.60),
            max_steps=4,
            min_step_score=0.00026,
            min_non_h088_passes=2,
            max_cells=33,
            max_rows=25,
            max_h088_cos=-0.056,
            min_good_margin=0.157,
            route_pred_cap=-0.000650,
            h098_pred_cap=-0.000018,
            min_component_gain=0.00035,
            min_companion_score=0.275,
            min_proposal_abs=0.012,
            min_bundle_score=0.48,
            h088_weight=0.0015,
            margin_weight=0.012,
            worldview="big bet: the public equation rewards coherent row-vector route improvement more than it punishes margin loss",
            **common,
        ),
        H135Spec(
            name="h134_rowvector_completion",
            group="rowvector_conservation_after_h134",
            start_name="h134",
            row_source="all_q1_bundle_rows",
            target_mode="q3s_companion",
            max_bundle_size=2,
            frac_values=(0.25, 0.35),
            max_steps=3,
            min_step_score=0.00020,
            min_non_h088_passes=3,
            max_cells=32,
            max_rows=24,
            max_h088_cos=-0.058,
            min_good_margin=0.163,
            route_pred_cap=-0.000625,
            h098_pred_cap=-0.000018,
            min_component_gain=0.00018,
            min_companion_score=0.275,
            min_proposal_abs=0.012,
            min_bundle_score=0.46,
            h088_weight=0.0020,
            margin_weight=0.024,
            worldview="H134 found seed companion cells; finish the missing same-row vector components instead of adding new Q1 deletions",
            **common,
        ),
    ]


def target_allowed(target: str, mode: str) -> bool:
    return h134mod.target_allowed(target, mode)


def proxy_h134_spec(spec: H135Spec) -> h134mod.H134Spec:
    return h134mod.H134Spec(
        name=f"proxy_{spec.name}",
        group=spec.group,
        start_name=spec.start_name,
        row_source=spec.row_source,
        target_mode=spec.target_mode,
        max_steps=spec.max_steps,
        min_step_score=spec.min_step_score,
        min_non_h088_passes=spec.min_non_h088_passes,
        max_cells=spec.max_cells,
        max_rows=spec.max_rows,
        max_per_subject=spec.max_per_subject,
        max_per_target=spec.max_per_target,
        amp=spec.amp,
        cap=spec.cap,
        pool_top=spec.pool_top,
        min_score=spec.min_score,
        min_residual_gap=spec.min_residual_gap,
        max_residual_toxicity=spec.max_residual_toxicity,
        min_residual_safety=spec.min_residual_safety,
        max_bad_weighted_pos=spec.max_bad_weighted_pos,
        max_bad_max_pos=spec.max_bad_max_pos,
        max_h088_cos=spec.max_h088_cos,
        min_good_margin=spec.min_good_margin,
        route_pred_cap=spec.route_pred_cap,
        h098_pred_cap=spec.h098_pred_cap,
        max_curv_marg=spec.max_curv_marg,
        max_h088_hard_cosine=spec.max_h088_hard_cosine,
        min_component_gain=spec.min_component_gain,
        min_companion_score=spec.min_companion_score,
        min_proposal_abs=spec.min_proposal_abs,
        h088_weight=spec.h088_weight,
        margin_weight=spec.margin_weight,
        worldview=spec.worldview,
    )


def choose_value(old: float, base_proposal: float, frac: float, spec: H135Spec) -> tuple[str, float] | None:
    vals = h134mod.propose_values(old, base_proposal, proxy_h134_spec(spec))
    if not vals:
        return None
    if abs(old) <= 1.0e-12:
        target = f"add_{frac:g}"
    elif frac <= 0.35:
        target = "toward_0.35"
    elif frac <= 0.60:
        target = "toward_0.6"
    else:
        target = "toward_0.85"
    for state, val in vals:
        if state == target:
            return state, float(val)
    return vals[0][0], float(vals[0][1])


def synergy_bonus(targets: tuple[str, ...]) -> float:
    st = set(targets)
    bonus = 0.0
    if {"S1", "S4"}.issubset(st):
        bonus += 0.090
    if {"Q3", "S4"}.issubset(st):
        bonus += 0.060
    if {"Q3", "S2"}.issubset(st):
        bonus += 0.045
    if {"S1", "S2"}.issubset(st):
        bonus += 0.035
    if len(st) >= 3:
        bonus -= 0.025
    return bonus


def build_bundle_pool(catalog: pd.DataFrame, start_move: np.ndarray, q1_rows: pd.DataFrame, spec: H135Spec) -> tuple[pd.DataFrame, pd.DataFrame]:
    cell_pool = h134mod.build_cell_pool(catalog, start_move, q1_rows, proxy_h134_spec(spec))
    if cell_pool.empty:
        return cell_pool, pd.DataFrame()
    rows = []
    for row, grp in cell_pool.groupby("row"):
        grp = grp.sort_values("h134_companion_score", ascending=False).head(5)
        recs = grp.to_dict("records")
        for size in range(1, min(spec.max_bundle_size, len(recs)) + 1):
            for combo in itertools.combinations(recs, size):
                targets = tuple(str(rec["target"]) for rec in combo)
                for frac in spec.frac_values:
                    ops = []
                    for rec in combo:
                        old = float(start_move[int(rec["row"]), int(rec["target_index"])])
                        picked = choose_value(old, float(rec["h134_base_proposal"]), float(frac), spec)
                        if picked is None:
                            break
                        state, val = picked
                        ops.append(
                            {
                                "row": int(rec["row"]),
                                "target_index": int(rec["target_index"]),
                                "target": str(rec["target"]),
                                "subject_id": str(rec["subject_id"]),
                                "sleep_date": str(rec["sleep_date"]),
                                "old_move": old,
                                "new_move": float(val),
                                "state": state,
                                "h134_base_proposal": float(rec["h134_base_proposal"]),
                                "h134_companion_score": float(rec["h134_companion_score"]),
                                "h134_row_conversion_pressure": float(rec["h134_row_conversion_pressure"]),
                                "h112_residual_safety": float(rec["h112_residual_safety"]),
                                "h112_residual_toxicity": float(rec["h112_residual_toxicity"]),
                                "h112_residual_gap": float(rec["h112_residual_gap"]),
                                "h131_residual_health": float(rec["h131_residual_health"]),
                                "h131_add_evidence": float(rec["h131_add_evidence"]),
                            }
                        )
                    if len(ops) != size:
                        continue
                    bundle_score = (
                        float(np.mean([op["h134_companion_score"] for op in ops]))
                        + 0.11 * float(np.mean([op["h134_row_conversion_pressure"] for op in ops]))
                        + 0.07 * min(size, 3)
                        + synergy_bonus(targets)
                        - 0.06 * float(np.mean([op["h112_residual_toxicity"] for op in ops]))
                    )
                    if bundle_score < spec.min_bundle_score:
                        continue
                    bundle_id = f"r{int(row)}_{''.join(targets)}_f{str(frac).replace('.', 'p')}"
                    rows.append(
                        {
                            "bundle_id": bundle_id,
                            "row": int(row),
                            "bundle_size": int(size),
                            "frac": float(frac),
                            "targets": ",".join(targets),
                            "ops": ops,
                            "h135_bundle_score": float(bundle_score),
                            "h135_mean_companion_score": float(np.mean([op["h134_companion_score"] for op in ops])),
                            "h135_mean_safety": float(np.mean([op["h112_residual_safety"] for op in ops])),
                            "h135_mean_toxicity": float(np.mean([op["h112_residual_toxicity"] for op in ops])),
                            "h135_mean_gap": float(np.mean([op["h112_residual_gap"] for op in ops])),
                            "h135_row_conversion_pressure": float(np.mean([op["h134_row_conversion_pressure"] for op in ops])),
                        }
                    )
    bundle_pool = pd.DataFrame(rows)
    if bundle_pool.empty:
        return cell_pool, bundle_pool
    bundle_pool = bundle_pool.sort_values(
        ["h135_bundle_score", "h135_row_conversion_pressure", "bundle_size"],
        ascending=[False, False, False],
    ).reset_index(drop=True)
    return cell_pool, bundle_pool


def evaluate_matrix(move_mat, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes):
    return h134mod.evaluate_matrix(
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


def check_constraints(move_mat: np.ndarray, evald: dict[str, float], spec: H135Spec) -> bool:
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


def bundle_step_score(after: dict[str, float], before: dict[str, float], bundle: dict[str, object], spec: H135Spec) -> tuple[float, dict[str, float]]:
    d_route = after["route"] - before["route"]
    d_h098 = after["h098"] - before["h098"]
    d_curv = after["curv_marg"] - before["curv_marg"]
    d_badw = after["badw"] - before["badw"]
    d_badmax = after["badmax"] - before["badmax"]
    d_h088 = after["h088"] - before["h088"]
    d_margin = after["margin"] - before["margin"]
    bscore = float(bundle["h135_bundle_score"])
    size = float(bundle["bundle_size"])

    route_view = (
        250.0 * (-d_h098)
        + 185.0 * max(-d_route, 0.0)
        - 110.0 * max(d_route, 0.0)
        + 145.0 * (-d_curv)
        + 0.00072 * bscore
        + 0.00006 * size
    )
    no_h088_view = (
        230.0 * (-d_h098)
        + 165.0 * max(-d_route, 0.0)
        - 115.0 * max(d_route, 0.0)
        + 130.0 * (-d_curv)
        - 5.0 * max(d_badw, 0.0)
        - 3.0 * max(d_badmax, 0.0)
        + 0.00064 * bscore
    )
    conservation_view = (
        0.00125 * bscore
        + 0.00012 * size
        - 55.0 * max(d_h098, 0.0)
        - 52.0 * max(d_route, 0.0)
        - 50.0 * max(d_curv, 0.0)
    )
    margin_view = (
        spec.margin_weight * d_margin
        + 0.00055 * bscore
        - 35.0 * max(d_h098, 0.0)
        - 28.0 * max(d_route, 0.0)
    )
    stress_view = (
        spec.h088_weight * (-d_h088)
        + spec.margin_weight * d_margin
        - 4.0 * max(d_badw, 0.0)
        - 2.5 * max(d_badmax, 0.0)
        + 0.00012 * bscore
    )
    scores = {
        "h135_route_view_score": float(route_view),
        "h135_no_h088_view_score": float(no_h088_view),
        "h135_conservation_view_score": float(conservation_view),
        "h135_margin_view_score": float(margin_view),
        "h135_stress_view_score": float(stress_view),
    }
    non_h088 = ["h135_route_view_score", "h135_no_h088_view_score", "h135_conservation_view_score", "h135_margin_view_score"]
    scores["h135_non_h088_passes"] = float(sum(scores[key] > 0.0 for key in non_h088))
    scores["h135_stress_passes"] = float(sum(value > 0.0 for value in scores.values()))
    aggregate = 0.28 * route_view + 0.24 * no_h088_view + 0.24 * conservation_view + 0.16 * margin_view + 0.08 * stress_view
    scores["h135_step_score"] = float(aggregate)
    return float(aggregate), scores


def apply_bundle(move_mat: np.ndarray, bundle: dict[str, object]) -> np.ndarray:
    out = move_mat.copy()
    for op in bundle["ops"]:
        out[int(op["row"]), int(op["target_index"])] = float(op["new_move"])
    return out


def coordinate_solve(start: np.ndarray, bundle_pool: pd.DataFrame, spec: H135Spec, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes) -> tuple[np.ndarray, pd.DataFrame, dict[str, float], dict[str, float]]:
    move_mat = start.copy()
    start_eval = evaluate_matrix(move_mat, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
    ops = []
    used_rows: set[int] = set()
    for step in range(spec.max_steps):
        before = evaluate_matrix(move_mat, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
        best = None
        for bundle in bundle_pool.head(spec.pool_top).to_dict("records"):
            row = int(bundle["row"])
            if row in used_rows:
                continue
            tmp = apply_bundle(move_mat, bundle)
            if np.allclose(tmp, move_mat):
                continue
            after = evaluate_matrix(tmp, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
            if not check_constraints(tmp, after, spec):
                continue
            score, view_scores = bundle_step_score(after, before, bundle, spec)
            if view_scores["h135_non_h088_passes"] < spec.min_non_h088_passes:
                continue
            if best is None or score > best["h135_step_score"]:
                best = {
                    "step": step + 1,
                    "bundle_id": str(bundle["bundle_id"]),
                    "row": row,
                    "bundle_size": int(bundle["bundle_size"]),
                    "frac": float(bundle["frac"]),
                    "targets": str(bundle["targets"]),
                    "h135_bundle_score": float(bundle["h135_bundle_score"]),
                    "h135_mean_companion_score": float(bundle["h135_mean_companion_score"]),
                    "h135_mean_safety": float(bundle["h135_mean_safety"]),
                    "h135_mean_toxicity": float(bundle["h135_mean_toxicity"]),
                    "h135_mean_gap": float(bundle["h135_mean_gap"]),
                    "h135_row_conversion_pressure": float(bundle["h135_row_conversion_pressure"]),
                    "ops": bundle["ops"],
                    **view_scores,
                    **{f"after_{key}": value for key, value in after.items()},
                    **{f"delta_{key}": after[key] - before[key] for key in after},
                }
        if best is None or float(best["h135_step_score"]) < spec.min_step_score:
            break
        move_mat = apply_bundle(move_mat, best)
        used_rows.add(int(best["row"]))
        ops.append(best)
    final_eval = evaluate_matrix(move_mat, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
    return move_mat, pd.DataFrame(ops), start_eval, final_eval


def flatten_ops(bundle_ops: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for rec in bundle_ops.to_dict("records"):
        for op in rec["ops"]:
            rows.append(
                {
                    "step": int(rec["step"]),
                    "bundle_id": str(rec["bundle_id"]),
                    "bundle_targets": str(rec["targets"]),
                    "bundle_frac": float(rec["frac"]),
                    "bundle_size": int(rec["bundle_size"]),
                    "row": int(op["row"]),
                    "target_index": int(op["target_index"]),
                    "target": str(op["target"]),
                    "subject_id": str(op["subject_id"]),
                    "sleep_date": str(op["sleep_date"]),
                    "old_move": float(op["old_move"]),
                    "new_move": float(op["new_move"]),
                    "state": str(op["state"]),
                    "h134_base_proposal": float(op["h134_base_proposal"]),
                    "h134_companion_score": float(op["h134_companion_score"]),
                    "h135_bundle_score": float(rec["h135_bundle_score"]),
                    "h135_step_score": float(rec["h135_step_score"]),
                    "delta_route": float(rec["delta_route"]),
                    "delta_h098": float(rec["delta_h098"]),
                    "delta_h088": float(rec["delta_h088"]),
                    "delta_margin": float(rec["delta_margin"]),
                }
            )
    return pd.DataFrame(rows)


def make_selected(catalog: pd.DataFrame, move_mat: np.ndarray) -> pd.DataFrame:
    selected = h130mod.make_selected(catalog, move_mat)
    if selected.empty:
        return selected
    selected["h135_actual_move"] = selected["h130_actual_move"]
    selected["h112_move"] = selected["h135_actual_move"].to_numpy(dtype=np.float64)
    return selected


def operation_summary(flat_ops: pd.DataFrame, bundle_ops: pd.DataFrame) -> dict[str, object]:
    if flat_ops.empty:
        return {
            "h135_bundles": 0,
            "h135_ops": 0,
            "h135_op_targets": "",
            "h135_mean_bundle_score": 0.0,
            "h135_mean_non_h088_passes": 0.0,
            "h135_mean_step_score": 0.0,
        }
    return {
        "h135_bundles": int(len(bundle_ops)),
        "h135_ops": int(len(flat_ops)),
        "h135_op_targets": ";".join(f"{k}:{v}" for k, v in flat_ops["target"].value_counts().to_dict().items()),
        "h135_mean_bundle_score": float(bundle_ops["h135_bundle_score"].mean()),
        "h135_mean_non_h088_passes": float(bundle_ops["h135_non_h088_passes"].mean()),
        "h135_mean_step_score": float(bundle_ops["h135_step_score"].mean()),
    }


def component_gain(final: dict[str, float], before: dict[str, float], spec: H135Spec) -> float:
    return (
        240.0 * (-(final["h098"] - before["h098"]))
        + 155.0 * (-(final["curv_marg"] - before["curv_marg"]))
        + 145.0 * max(-(final["route"] - before["route"]), 0.0)
        - 90.0 * max(final["route"] - before["route"], 0.0)
        + spec.margin_weight * (final["margin"] - before["margin"])
        + spec.h088_weight * (-(final["h088"] - before["h088"]))
    )


def previous_moves(sample: pd.DataFrame, base_prob: np.ndarray, moves: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    prev = h134mod.previous_moves(sample, base_prob, {name: moves[name] for name in ["h122", "h124", "h126", "h127", "h128", "h129", "h130", "h131", "h132", "h133"]})
    prev["h134"] = moves["h134"].reshape(-1)
    return prev


def run() -> None:
    cleanup_previous_outputs()
    pool, _public, sample, base_prob, cell, h098_fit, route_fit, basis_fit_df, basis_fit_moves, bad_axes, bad_moves, good_moves, axes, fit, model_scores, props = h118mod.prepare_context()
    scored = h123mod.build_scored_pool(pool, base_prob, fit, bad_axes, bad_moves, good_moves, axes, props)
    catalog = h132mod.build_catalog(scored)
    moves = {name: load_move(name, sample, base_prob) for name in ["h122", "h124", "h126", "h127", "h128", "h129", "h130", "h131", "h132", "h133", "h134"]}
    known = known_hashes(sample)
    previous = previous_moves(sample, base_prob, moves)
    bundle_rows = h133mod.collect_bundle_rows(catalog, moves["h131"])
    q1_rows = h134mod.collect_q1_rows(bundle_rows)

    candidate_rows = []
    selected_frames = []
    flat_op_frames = []
    bundle_op_frames = []
    audit_rows = []
    start_rows = []
    cell_pool_frames = []
    bundle_pool_frames = []
    for spec in candidate_specs():
        start_move = moves[spec.start_name]
        cell_pool, bundle_pool = build_bundle_pool(catalog, start_move, q1_rows, spec)
        start_eval = evaluate_matrix(start_move, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
        start_rows.append({"start_name": spec.start_name, "spec_name": spec.name, **start_eval, "start_cells": int((np.abs(start_move) > 1.0e-12).sum()), "cell_pool": int(len(cell_pool)), "bundle_pool": int(len(bundle_pool))})
        audit_rows.append(
            {
                "spec_name": spec.name,
                "start_name": spec.start_name,
                "target_mode": spec.target_mode,
                "max_bundle_size": spec.max_bundle_size,
                "cell_pool": int(len(cell_pool)),
                "bundle_pool": int(len(bundle_pool)),
                "mean_bundle_score": float(bundle_pool["h135_bundle_score"].mean()) if not bundle_pool.empty else 0.0,
                "max_bundle_score": float(bundle_pool["h135_bundle_score"].max()) if not bundle_pool.empty else 0.0,
            }
        )
        if not cell_pool.empty:
            cp = cell_pool.copy()
            cp.insert(0, "spec_name", spec.name)
            cell_pool_frames.append(cp)
        if not bundle_pool.empty:
            bp = bundle_pool.drop(columns=["ops"]).copy()
            bp.insert(0, "spec_name", spec.name)
            bundle_pool_frames.append(bp)
        if bundle_pool.empty:
            continue
        move_mat, bundle_ops, before, final = coordinate_solve(
            start_move,
            bundle_pool,
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
        audit_rows[-1]["bundles"] = int(len(bundle_ops))
        if bundle_ops.empty:
            continue
        flat_ops = flatten_ops(bundle_ops)
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
        candidate_id = safe_id(f"h135_{spec.name}_{hash_id}", 128)
        path = OUT / f"submission_{candidate_id}.csv"
        h085mod.write_submission(sample, prob, path)
        selected_cells = make_selected(catalog, move_mat)
        axis = h102mod.cumulative_axis_metrics(move_mat.reshape(-1), bad_axes, bad_moves, good_moves)
        op_diag = operation_summary(flat_ops, bundle_ops)
        diag = {
            "h118_zero_curv": -0.0002616634510263019,
            "h118_curv_pred_delta_vs_h057": final["curv_marg"] - 0.0002616634510263019,
            "h118_curv_marginal_vs_zero": final["curv_marg"],
            "h118_mean_forbidden_same": float(selected_cells.get("h117_forbidden_same", pd.Series([0.0])).astype(float).mean()),
            "h118_max_forbidden_same": float(selected_cells.get("h117_forbidden_same", pd.Series([0.0])).astype(float).max()),
            "h118_mean_forbidden_pressure": float(selected_cells.get("h117_forbidden_pressure", pd.Series([0.0])).astype(float).mean()),
            "h118_mean_veto_score": float(selected_cells.get("h118_forbidden_veto_score", pd.Series([1.0])).astype(float).mean()),
            "h118_selected_rows": int(selected_cells["row"].nunique()),
            "h135_start_field": spec.start_name,
            "h135_start_cells": int((np.abs(start_move) > 1.0e-12).sum()),
            "h135_cell_pool": int(len(cell_pool)),
            "h135_bundle_pool": int(len(bundle_pool)),
            "h135_component_gain": float(gain),
            "h135_delta_start_route": float(final["route"] - before["route"]),
            "h135_delta_start_h098": float(final["h098"] - before["h098"]),
            "h135_delta_start_h088": float(final["h088"] - before["h088"]),
            "h135_delta_start_margin": float(final["margin"] - before["margin"]),
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
        metrics["h135_worldview"] = spec.worldview
        metrics["h135_fit_feature_set"] = fit.feature_set
        metrics["h135_fit_alpha"] = fit.alpha
        metrics["h135_fit_score"] = fit.score
        metrics["h135_score"] = (
            305.0 * (-float(metrics["model_pred_delta_vs_h057"]))
            + 270.0 * (-float(metrics["route_basis_pred_delta_vs_h057"]))
            + 125.0 * (-float(metrics["h118_curv_marginal_vs_zero"]))
            + 0.10 * float(metrics["h102_cum_good_bad_margin"])
            + 0.04 * max(-float(metrics["h102_cum_h088_axis_cos"]), 0.0)
            + 0.13 * float(metrics["selected_mean_residual_safety"])
            + 0.12 * float(metrics["selected_mean_residual_gap"])
            - 0.16 * float(metrics["selected_mean_residual_toxicity"])
            + 1.3 * max(gain, 0.0)
            + 0.020 * float(op_diag["h135_mean_non_h088_passes"])
            + 0.018 * float(op_diag["h135_mean_bundle_score"])
            - 0.010 * max(float(metrics["selected_cells"]) - 34.0, 0.0)
            - 18.0 * max(float(metrics["hard_diag_delta_vs_h057"]), 0.0)
            - 0.8 * max(h088_cos, 0.0)
        )
        candidate_rows.append(metrics)
        selected2 = selected_cells.copy()
        if "candidate_id" in selected2.columns:
            selected2 = selected2.drop(columns=["candidate_id"])
        selected2.insert(0, "candidate_id", candidate_id)
        selected_frames.append(selected2)
        flat2 = flat_ops.copy()
        flat2.insert(0, "candidate_id", candidate_id)
        flat_op_frames.append(flat2)
        bundle2 = bundle_ops.drop(columns=["ops"]).copy()
        bundle2.insert(0, "candidate_id", candidate_id)
        bundle_op_frames.append(bundle2)

    audit = pd.DataFrame(audit_rows)
    starts = pd.DataFrame(start_rows)
    candidates = pd.DataFrame(candidate_rows)
    catalog.to_csv(OUT / "h135_catalog.csv", index=False)
    bundle_rows.to_csv(OUT / "h135_bundle_rows.csv", index=False)
    q1_rows.to_csv(OUT / "h135_q1_rows.csv", index=False)
    audit.to_csv(OUT / "h135_audit.csv", index=False)
    starts.to_csv(OUT / "h135_start_metrics.csv", index=False)
    model_scores.to_csv(OUT / "h135_curvature_model_scores.csv", index=False)
    if cell_pool_frames:
        pd.concat(cell_pool_frames, ignore_index=True).to_csv(OUT / "h135_cell_pool.csv", index=False)
    if bundle_pool_frames:
        pd.concat(bundle_pool_frames, ignore_index=True).to_csv(OUT / "h135_bundle_pool.csv", index=False)
    if candidates.empty:
        report = f"""# H135 Row-Vector Conservation HS-JEPA

No candidate was promoted.

Question: are Q1 companion actions safe only when decoded as same-row Q3/S
vectors rather than independent cells?

Audit:

{md_table(audit, 20)}

Start metrics:

{md_table(starts, 20)}
"""
        (OUT / "h135_report.md").write_text(report, encoding="utf-8")
        print("H135 promoted no candidate")
        print(audit.to_string(index=False))
        return

    candidates = candidates.sort_values(["h135_score", "h135_component_gain", "model_pred_delta_vs_h057"], ascending=[False, False, True]).reset_index(drop=True)
    selected = candidates.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"submission_h135_rowvector_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)
    decision = {
        "decision": "promote_h135_rowvector_conservation",
        "selected_candidate_id": selected["candidate_id"],
        "root_uploadsafe_path": str(root_path.resolve()),
        "worldview": selected["h135_worldview"],
        **selected,
        **{f"root_{key}": value for key, value in validation.items()},
    }
    candidates.to_csv(OUT / "h135_candidates.csv", index=False)
    pd.concat(selected_frames, ignore_index=True).to_csv(OUT / "h135_selected_cells.csv", index=False)
    pd.concat(flat_op_frames, ignore_index=True).to_csv(OUT / "h135_operations.csv", index=False)
    pd.concat(bundle_op_frames, ignore_index=True).to_csv(OUT / "h135_bundle_operations.csv", index=False)
    pd.DataFrame([decision]).to_csv(OUT / "h135_decision.csv", index=False)

    cols = [
        "candidate_id",
        "spec_name",
        "h135_start_field",
        "selected_cells",
        "changed_rows_vs_h057",
        "Q1_changed_vs_h057",
        "Q2_changed_vs_h057",
        "Q3_changed_vs_h057",
        "S1_changed_vs_h057",
        "S2_changed_vs_h057",
        "S3_changed_vs_h057",
        "S4_changed_vs_h057",
        "h135_bundles",
        "h135_ops",
        "h135_op_targets",
        "h135_mean_bundle_score",
        "h135_mean_non_h088_passes",
        "h135_delta_start_route",
        "h135_delta_start_h098",
        "h135_delta_start_h088",
        "h135_delta_start_margin",
        "model_pred_delta_vs_h057",
        "route_basis_pred_delta_vs_h057",
        "h102_cum_h088_axis_cos",
        "h102_cum_good_bad_margin",
        "h135_component_gain",
        "h135_score",
        "file",
    ]
    report = f"""# H135 Row-Vector Conservation HS-JEPA

Question: H134 found Q1 companion conversion, but a diagnostic sweep showed
that row 164's S1+S4 vector is stronger than either cell alone.  Is public
safety assigned to coherent row-target vectors rather than independent cells?

Audit:

{md_table(audit, 20)}

Start metrics:

{md_table(starts, 20)}

Candidates:

{md_table(candidates[cols], 20)}

Bundle operations:

{md_table(pd.concat(bundle_op_frames, ignore_index=True), 40)}

Cell operations:

{md_table(pd.concat(flat_op_frames, ignore_index=True), 80)}

Decision:

{md_table(pd.DataFrame([decision]), 1)}

Interpretation rule:

- If H135 beats H134/H132 publicly, HS-JEPA needs a row-vector conservation
  decoder: public-safe action is assigned to target bundles, not cells.
- If H134 wins more, vector completion overfits route sensors and the
  conservation field should stay sparse/cell-level.
- If H132 wins more, companion conservation itself is not action-grade.
"""
    (OUT / "h135_report.md").write_text(report, encoding="utf-8")
    print("H135 selected candidate")
    print(candidates[cols].head(10).to_string(index=False))
    print("\nDecision")
    print(pd.DataFrame([decision])[["decision", "selected_candidate_id", "root_uploadsafe_path", "root_upload_safe"]].to_string(index=False))


if __name__ == "__main__":
    run()
