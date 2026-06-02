#!/usr/bin/env python3
"""H133: target-split assignment HS-JEPA.

H132 found a small Q1 toxicity witness, but broad row-bundle erasure failed.
This script tests the next equation:

    a human-state row can contain both toxic and safe target routes

So the decoder must not erase the row bundle as a unit.  It must assign each
row-target action to keep, half, quarter, or off while treating H088/H018 as
stress sensors rather than action heads.
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
OUT = HITL / "h133_targetsplit_assignment_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H132_PATH = HITL / "h132_bundle_toxicity_field_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h132mod_h133", H132_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H132_PATH}")
h132mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h132mod
SPEC.loader.exec_module(h132mod)

h131mod = h132mod.h131mod
h130mod = h132mod.h130mod
h126mod = h132mod.h126mod
h123mod = h132mod.h123mod
h118mod = h132mod.h118mod
h102mod = h132mod.h102mod
h085mod = h132mod.h085mod

TARGETS = h132mod.TARGETS
TOL = h132mod.TOL


@dataclass(frozen=True)
class H133Spec:
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
    min_cell_toxicity: float
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
    for path in OUT.glob("submission_h133_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h133_targetsplit_*.csv"):
        path.unlink()


def root_submission_paths() -> dict[str, Path]:
    paths = h132mod.root_submission_paths()
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


def candidate_specs() -> list[H133Spec]:
    common = dict(
        max_per_subject=26,
        max_per_target=18,
        amp=1.0,
        cap=0.30,
        pool_top=120,
        min_score=0.0,
        min_residual_gap=-0.45,
        max_residual_toxicity=0.95,
        min_residual_safety=0.0,
        max_bad_weighted_pos=0.0006,
        max_bad_max_pos=0.0022,
        max_curv_marg=0.000064,
        max_h088_hard_cosine=-0.018,
    )
    return [
        H133Spec(
            name="h132_nonh088_targetsplit",
            group="targetsplit_after_h132",
            start_name="h132",
            row_source="h132_qbundle_rows",
            target_mode="q1q3",
            max_steps=7,
            min_step_score=0.00023,
            min_non_h088_passes=2,
            max_cells=28,
            max_rows=23,
            max_h088_cos=-0.056,
            min_good_margin=0.165,
            route_pred_cap=-0.000630,
            h098_pred_cap=-0.000020,
            min_component_gain=0.00016,
            min_cell_toxicity=0.18,
            h088_weight=0.010,
            margin_weight=0.012,
            worldview="H132 was right about Q1 witness, but row bundles must be split into target-level toxic/safe routes",
            **common,
        ),
        H133Spec(
            name="h131_targetsplit_from_scratch",
            group="targetsplit_from_h131",
            start_name="h131",
            row_source="h132_qbundle_rows",
            target_mode="q1q3",
            max_steps=9,
            min_step_score=0.00024,
            min_non_h088_passes=2,
            max_cells=29,
            max_rows=24,
            max_h088_cos=-0.056,
            min_good_margin=0.150,
            route_pred_cap=-0.000625,
            h098_pred_cap=-0.000020,
            min_component_gain=0.00018,
            min_cell_toxicity=0.18,
            h088_weight=0.010,
            margin_weight=0.012,
            worldview="the Q1 witness and route-safe Q3 erasures should be solved together from H131 without treating H132 as fixed",
            **common,
        ),
        H133Spec(
            name="h132_q1_only_signature",
            group="q1_toxicity_signature",
            start_name="h132",
            row_source="h132_qbundle_rows",
            target_mode="q1",
            max_steps=5,
            min_step_score=0.00020,
            min_non_h088_passes=2,
            max_cells=27,
            max_rows=22,
            max_h088_cos=-0.055,
            min_good_margin=0.163,
            route_pred_cap=-0.000630,
            h098_pred_cap=-0.000020,
            min_component_gain=0.00012,
            min_cell_toxicity=0.16,
            h088_weight=0.006,
            margin_weight=0.008,
            worldview="the toxic field is specifically a Q1 subjective-state residue, not a Q-bundle law",
            **common,
        ),
        H133Spec(
            name="h132_h088_shadow_targetsplit",
            group="shadow_targetsplit_diagnostic",
            start_name="h132",
            row_source="h132_qbundle_rows",
            target_mode="q1q3",
            max_steps=5,
            min_step_score=0.00034,
            min_non_h088_passes=1,
            max_cells=28,
            max_rows=23,
            max_h088_cos=-0.063,
            min_good_margin=0.175,
            route_pred_cap=-0.000620,
            h098_pred_cap=-0.000018,
            min_component_gain=0.00010,
            min_cell_toxicity=0.18,
            h088_weight=0.090,
            margin_weight=0.090,
            worldview="diagnostic only: if this wins locally but not publicly, H088/margin target-split is still a shortcut",
            **common,
        ),
    ]


def collect_bundle_rows(catalog: pd.DataFrame, start_h131: np.ndarray) -> pd.DataFrame:
    frames = []
    for spec in h132mod.candidate_specs():
        if spec.start_name != "h131":
            continue
        if spec.bundle_mode not in {"witness_q_core", "q_core_or_h129", "mixed_nonq2"}:
            continue
        bundles = h132mod.bundle_rows(catalog, start_h131, spec)
        if bundles.empty:
            continue
        frame = bundles.drop(columns=["bundle_cells"]).copy()
        frame.insert(0, "source_bundle_spec", spec.name)
        frames.append(frame)
    if not frames:
        return pd.DataFrame()
    raw = pd.concat(frames, ignore_index=True)
    agg = raw.groupby("row", as_index=False).agg(
        h133_row_bundle_sources=("source_bundle_spec", lambda x: ",".join(sorted(set(map(str, x))))),
        h133_row_bundle_targets=("bundle_targets", lambda x: ",".join(sorted(set(",".join(map(str, x)).split(","))))),
        h133_row_bundle_contradiction=("h132_bundle_contradiction", "max"),
        h133_row_bundle_witness=("h132_bundle_witness", "max"),
        h133_row_bundle_bad_same=("h132_bundle_bad_same", "max"),
        h133_row_bundle_shortcut=("h132_bundle_shortcut", "max"),
        h133_row_bundle_health=("h132_bundle_health", "max"),
        h133_row_bundle_source_strength=("h132_bundle_source_strength", "mean"),
    )
    return agg


def build_cell_pool(catalog: pd.DataFrame, start_move: np.ndarray, bundle_rows: pd.DataFrame, spec: H133Spec) -> pd.DataFrame:
    active = catalog[
        [((int(row), int(tidx)) in nonzero_keys(start_move)) for row, tidx in zip(catalog["row"], catalog["target_index"])]
    ].copy()
    if spec.target_mode == "q1":
        active = active[active["target"].astype(str).eq("Q1")].copy()
    elif spec.target_mode == "q1q3":
        active = active[active["target"].astype(str).isin(["Q1", "Q3"])].copy()
    else:
        raise ValueError(spec.target_mode)
    if bundle_rows.empty or active.empty:
        return active.iloc[0:0].copy()
    active = active.merge(bundle_rows, on="row", how="inner")
    if active.empty:
        return active
    witness = np.maximum(
        active["h132_h129_erase_witness"].to_numpy(dtype=np.float64),
        active["h132_h130_erase_witness"].to_numpy(dtype=np.float64),
    )
    target_q1 = active["target"].astype(str).eq("Q1").to_numpy(dtype=np.float64)
    target_q3 = active["target"].astype(str).eq("Q3").to_numpy(dtype=np.float64)
    source_strength = active.get("h131_source_strength", active.get("source_family_count", pd.Series([0.0] * len(active)))).astype(float).to_numpy()
    active["h133_cell_toxicity"] = (
        0.19 * active["h133_row_bundle_contradiction"].to_numpy(dtype=np.float64)
        + 0.18 * active["h131_erase_evidence"].to_numpy(dtype=np.float64)
        + 0.16 * active["h112_residual_toxicity"].to_numpy(dtype=np.float64)
        + 0.15 * active["h131_bad_same_pressure"].to_numpy(dtype=np.float64)
        + 0.12 * active["h131_shortcut_pressure"].to_numpy(dtype=np.float64)
        + 0.12 * witness
        + 0.05 * target_q1
        - 0.08 * active["h131_add_evidence"].to_numpy(dtype=np.float64)
        - 0.03 * np.minimum(source_strength, 3.0) / 3.0
        - 0.04 * target_q3 * (1.0 - witness)
    )
    active["h133_witness"] = witness
    active["h133_start_move"] = [
        float(start_move[int(row), int(tidx)])
        for row, tidx in zip(active["row"].astype(int), active["target_index"].astype(int))
    ]
    active = active[active["h133_cell_toxicity"].to_numpy(dtype=np.float64) >= spec.min_cell_toxicity].copy()
    return active.sort_values(["h133_cell_toxicity", "h133_witness"], ascending=[False, False]).reset_index(drop=True)


def evaluate_matrix(move_mat, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes):
    return h132mod.evaluate_matrix(
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


def check_constraints(move_mat: np.ndarray, evald: dict[str, float], spec: H133Spec) -> bool:
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


def propose_values(old: float) -> list[tuple[str, float]]:
    return [
        ("off", 0.0),
        ("half", 0.5 * old),
        ("quarter", 0.25 * old),
    ]


def target_step_score(after: dict[str, float], before: dict[str, float], cell_rec: dict[str, object], spec: H133Spec) -> tuple[float, dict[str, float]]:
    d_route = after["route"] - before["route"]
    d_h098 = after["h098"] - before["h098"]
    d_curv = after["curv_marg"] - before["curv_marg"]
    d_badw = after["badw"] - before["badw"]
    d_badmax = after["badmax"] - before["badmax"]
    d_h088 = after["h088"] - before["h088"]
    d_margin = after["margin"] - before["margin"]
    tox = float(cell_rec["h133_cell_toxicity"])
    witness = float(cell_rec["h133_witness"])

    route_view = (
        260.0 * (-d_h098)
        + 190.0 * max(-d_route, 0.0)
        - 95.0 * max(d_route, 0.0)
        + 145.0 * (-d_curv)
        + 0.00072 * tox
        + 0.00012 * witness
    )
    no_h088_view = (
        235.0 * (-d_h098)
        + 165.0 * max(-d_route, 0.0)
        - 100.0 * max(d_route, 0.0)
        + 135.0 * (-d_curv)
        - 5.0 * max(d_badw, 0.0)
        - 3.0 * max(d_badmax, 0.0)
        + 0.00068 * tox
    )
    assignment_view = (
        0.00135 * tox
        + 0.00016 * witness
        - 45.0 * max(d_h098, 0.0)
        - 45.0 * max(d_route, 0.0)
        - 50.0 * max(d_curv, 0.0)
    )
    stress_view = (
        spec.h088_weight * (-d_h088)
        + spec.margin_weight * d_margin
        - 4.0 * max(d_badw, 0.0)
        - 2.5 * max(d_badmax, 0.0)
        + 0.00015 * tox
    )
    scores = {
        "h133_route_view_score": float(route_view),
        "h133_no_h088_view_score": float(no_h088_view),
        "h133_assignment_view_score": float(assignment_view),
        "h133_stress_view_score": float(stress_view),
    }
    scores["h133_non_h088_passes"] = float(sum(scores[key] > 0.0 for key in ["h133_route_view_score", "h133_no_h088_view_score", "h133_assignment_view_score"]))
    scores["h133_stress_passes"] = float(sum(value > 0.0 for value in scores.values()))
    aggregate = 0.32 * route_view + 0.32 * no_h088_view + 0.26 * assignment_view + 0.10 * stress_view
    scores["h133_step_score"] = float(aggregate)
    return float(aggregate), scores


def coordinate_solve(start: np.ndarray, pool_cells: pd.DataFrame, spec: H133Spec, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes) -> tuple[np.ndarray, pd.DataFrame, dict[str, float], dict[str, float]]:
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
            if abs(old) <= 1.0e-12:
                continue
            for state, val in propose_values(old):
                if abs(val - old) <= 1.0e-12:
                    continue
                tmp = move_mat.copy()
                tmp[row, tidx] = val
                after = evaluate_matrix(tmp, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
                if not check_constraints(tmp, after, spec):
                    continue
                score, view_scores = target_step_score(after, before, rec, spec)
                if view_scores["h133_non_h088_passes"] < spec.min_non_h088_passes:
                    continue
                if best is None or score > best["h133_step_score"]:
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
                        "h133_cell_toxicity": float(rec["h133_cell_toxicity"]),
                        "h133_witness": float(rec["h133_witness"]),
                        "h133_row_bundle_contradiction": float(rec["h133_row_bundle_contradiction"]),
                        "h133_row_bundle_sources": str(rec["h133_row_bundle_sources"]),
                        **view_scores,
                        **{f"after_{key}": value for key, value in after.items()},
                        **{f"delta_{key}": after[key] - before[key] for key in after},
                    }
        if best is None or float(best["h133_step_score"]) < spec.min_step_score:
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
    selected["h133_actual_move"] = selected["h130_actual_move"]
    selected["h112_move"] = selected["h133_actual_move"].to_numpy(dtype=np.float64)
    return selected


def operation_summary(ops: pd.DataFrame) -> dict[str, object]:
    if ops.empty:
        return {
            "h133_ops": 0,
            "h133_off_ops": 0,
            "h133_half_ops": 0,
            "h133_quarter_ops": 0,
            "h133_op_targets": "",
            "h133_mean_cell_toxicity": 0.0,
            "h133_mean_non_h088_passes": 0.0,
            "h133_mean_step_score": 0.0,
        }
    return {
        "h133_ops": int(len(ops)),
        "h133_off_ops": int(ops["state"].astype(str).eq("off").sum()),
        "h133_half_ops": int(ops["state"].astype(str).eq("half").sum()),
        "h133_quarter_ops": int(ops["state"].astype(str).eq("quarter").sum()),
        "h133_op_targets": ";".join(f"{k}:{v}" for k, v in ops["target"].value_counts().to_dict().items()),
        "h133_mean_cell_toxicity": float(ops["h133_cell_toxicity"].mean()),
        "h133_mean_non_h088_passes": float(ops["h133_non_h088_passes"].mean()),
        "h133_mean_step_score": float(ops["h133_step_score"].mean()),
    }


def component_gain(final: dict[str, float], before: dict[str, float], spec: H133Spec) -> float:
    return (
        250.0 * (-(final["h098"] - before["h098"]))
        + 160.0 * (-(final["curv_marg"] - before["curv_marg"]))
        + 155.0 * max(-(final["route"] - before["route"]), 0.0)
        - 85.0 * max(final["route"] - before["route"], 0.0)
        + spec.margin_weight * (final["margin"] - before["margin"])
        + spec.h088_weight * (-(final["h088"] - before["h088"]))
    )


def previous_moves(sample: pd.DataFrame, base_prob: np.ndarray, moves: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    out = h132mod.previous_moves(sample, base_prob, {name: moves[name] for name in ["h131", "h130", "h129", "h128", "h127", "h126", "h124", "h122"]})
    out["h132"] = moves["h132"].reshape(-1)
    return out


def run() -> None:
    cleanup_previous_outputs()
    pool, _public, sample, base_prob, cell, h098_fit, route_fit, basis_fit_df, basis_fit_moves, bad_axes, bad_moves, good_moves, axes, fit, model_scores, props = h118mod.prepare_context()
    scored = h123mod.build_scored_pool(pool, base_prob, fit, bad_axes, bad_moves, good_moves, axes, props)
    catalog = h132mod.build_catalog(scored)
    moves = {name: load_move(name, sample, base_prob) for name in ["h122", "h124", "h126", "h127", "h128", "h129", "h130", "h131", "h132"]}
    known = known_hashes(sample)
    previous = previous_moves(sample, base_prob, moves)
    bundle_rows = collect_bundle_rows(catalog, moves["h131"])

    candidate_rows = []
    selected_frames = []
    op_frames = []
    audit_rows = []
    start_rows = []
    pool_frames = []
    for spec in candidate_specs():
        start_move = moves[spec.start_name]
        pool_cells = build_cell_pool(catalog, start_move, bundle_rows, spec)
        start_eval = evaluate_matrix(start_move, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
        start_rows.append({"start_name": spec.start_name, "spec_name": spec.name, **start_eval, "start_cells": int((np.abs(start_move) > 1.0e-12).sum()), "pool_cells": int(len(pool_cells))})
        audit_rows.append(
            {
                "spec_name": spec.name,
                "start_name": spec.start_name,
                "target_mode": spec.target_mode,
                "pool_cells": int(len(pool_cells)),
                "mean_cell_toxicity": float(pool_cells["h133_cell_toxicity"].mean()) if not pool_cells.empty else 0.0,
                "max_cell_toxicity": float(pool_cells["h133_cell_toxicity"].max()) if not pool_cells.empty else 0.0,
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
        candidate_id = safe_id(f"h133_{spec.name}_{hash_id}", 128)
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
            "h133_start_field": spec.start_name,
            "h133_start_cells": int((np.abs(start_move) > 1.0e-12).sum()),
            "h133_pool_cells": int(len(pool_cells)),
            "h133_component_gain": float(gain),
            "h133_delta_start_route": float(final["route"] - before["route"]),
            "h133_delta_start_h098": float(final["h098"] - before["h098"]),
            "h133_delta_start_h088": float(final["h088"] - before["h088"]),
            "h133_delta_start_margin": float(final["margin"] - before["margin"]),
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
        metrics["h133_worldview"] = spec.worldview
        metrics["h133_fit_feature_set"] = fit.feature_set
        metrics["h133_fit_alpha"] = fit.alpha
        metrics["h133_fit_score"] = fit.score
        metrics["h133_score"] = (
            315.0 * (-float(metrics["model_pred_delta_vs_h057"]))
            + 260.0 * (-float(metrics["route_basis_pred_delta_vs_h057"]))
            + 120.0 * (-float(metrics["h118_curv_marginal_vs_zero"]))
            + 0.11 * float(metrics["h102_cum_good_bad_margin"])
            + 0.05 * max(-float(metrics["h102_cum_h088_axis_cos"]), 0.0)
            + 0.14 * float(metrics["selected_mean_residual_safety"])
            + 0.13 * float(metrics["selected_mean_residual_gap"])
            - 0.18 * float(metrics["selected_mean_residual_toxicity"])
            + 1.4 * max(gain, 0.0)
            + 0.018 * float(op_diag["h133_mean_non_h088_passes"])
            + 0.012 * float(op_diag["h133_mean_cell_toxicity"])
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
    catalog.to_csv(OUT / "h133_catalog.csv", index=False)
    bundle_rows.to_csv(OUT / "h133_bundle_rows.csv", index=False)
    audit.to_csv(OUT / "h133_audit.csv", index=False)
    starts.to_csv(OUT / "h133_start_metrics.csv", index=False)
    model_scores.to_csv(OUT / "h133_curvature_model_scores.csv", index=False)
    if pool_frames:
        pd.concat(pool_frames, ignore_index=True).to_csv(OUT / "h133_cell_pool.csv", index=False)
    if candidates.empty:
        report = f"""# H133 Target-Split Assignment HS-JEPA

No candidate was promoted.

Question: did H132 fail broad bundle erasure because toxicity must be assigned
inside each row-target bundle?

Audit:

{md_table(audit, 20)}

Start metrics:

{md_table(starts, 20)}
"""
        (OUT / "h133_report.md").write_text(report, encoding="utf-8")
        print("H133 promoted no candidate")
        print(audit.to_string(index=False))
        return

    candidates["h133_diagnostic_only"] = candidates["spec_name"].astype(str).str.contains("shadow", regex=False)
    candidates = candidates.sort_values(["h133_score", "h133_component_gain", "model_pred_delta_vs_h057"], ascending=[False, False, True]).reset_index(drop=True)
    promote_pool = candidates[~candidates["h133_diagnostic_only"].to_numpy(dtype=bool)].copy()
    if promote_pool.empty:
        promote_pool = candidates.copy()
    selected = promote_pool.sort_values(["h133_score", "h133_component_gain", "model_pred_delta_vs_h057"], ascending=[False, False, True]).iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"submission_h133_targetsplit_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)
    decision = {
        "decision": "promote_h133_targetsplit_assignment",
        "selected_candidate_id": selected["candidate_id"],
        "root_uploadsafe_path": str(root_path.resolve()),
        "worldview": selected["h133_worldview"],
        **selected,
        **{f"root_{key}": value for key, value in validation.items()},
    }
    candidates.to_csv(OUT / "h133_candidates.csv", index=False)
    pd.concat(selected_frames, ignore_index=True).to_csv(OUT / "h133_selected_cells.csv", index=False)
    pd.concat(op_frames, ignore_index=True).to_csv(OUT / "h133_operations.csv", index=False)
    pd.DataFrame([decision]).to_csv(OUT / "h133_decision.csv", index=False)

    cols = [
        "candidate_id",
        "spec_name",
        "h133_start_field",
        "selected_cells",
        "changed_rows_vs_h057",
        "Q1_changed_vs_h057",
        "Q2_changed_vs_h057",
        "Q3_changed_vs_h057",
        "S1_changed_vs_h057",
        "S2_changed_vs_h057",
        "S3_changed_vs_h057",
        "S4_changed_vs_h057",
        "h133_ops",
        "h133_off_ops",
        "h133_half_ops",
        "h133_quarter_ops",
        "h133_op_targets",
        "h133_mean_cell_toxicity",
        "h133_mean_non_h088_passes",
        "h133_delta_start_route",
        "h133_delta_start_h098",
        "h133_delta_start_h088",
        "h133_delta_start_margin",
        "model_pred_delta_vs_h057",
        "route_basis_pred_delta_vs_h057",
        "h102_cum_h088_axis_cos",
        "h102_cum_good_bad_margin",
        "h133_component_gain",
        "h133_score",
        "file",
    ]
    report = f"""# H133 Target-Split Assignment HS-JEPA

Question: H132 found Q1 witness toxicity but broad row-bundle erasure failed.
Was the failure caused by treating a mixed human-state row as an indivisible
bundle instead of assigning toxicity at the row-target level?

Bundle-row sources:

{md_table(bundle_rows, 20)}

Audit:

{md_table(audit, 20)}

Start metrics:

{md_table(starts, 20)}

Candidates:

{md_table(candidates[cols], 20)}

Operations:

{md_table(pd.concat(op_frames, ignore_index=True), 40)}

Decision:

{md_table(pd.DataFrame([decision]), 1)}

Interpretation rule:

- If H133 improves over H132/H131, HS-JEPA needs an intra-row target assignment
  decoder: Q1/Q3 toxicity and route value can coexist inside the same human
  state row.
- If H132 improves more, the extra target-split erasures are over-completion
  and the Q1 witness remains a tiny residue.
- If H131 improves more, even H132's Q1 witness eraser is public-sensor
  shortcut, and the safe assignment field should stay value-add only.
- If the H088-shadow diagnostic wins locally but not publicly, H088/margin
  remain stress sensors only, not action heads.
"""
    (OUT / "h133_report.md").write_text(report, encoding="utf-8")
    print("H133 selected candidate")
    print(candidates[cols].head(10).to_string(index=False))
    print("\nDecision")
    print(pd.DataFrame([decision])[["decision", "selected_candidate_id", "root_uploadsafe_path", "root_upload_safe"]].to_string(index=False))


if __name__ == "__main__":
    run()
