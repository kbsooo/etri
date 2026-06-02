#!/usr/bin/env python3
"""H132: bundle-toxicity field HS-JEPA.

H131 killed most cell-level erase/damp actions under sensor dropout.  That may
mean erasure is shortcut.  It may also mean toxicity is not a single-cell
property.  H132 tests the latter:

    toxic action is a row-target bundle contradiction

Cells such as row 135 can look individually healthy while the row-level Q1/Q3
or Q/S action vector aligns with public-bad structure.  The decoder therefore
scores bundle-level erasure using non-H088 contradiction evidence, then checks
whether the resulting action is still acceptable under public/private sensors.
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
OUT = HITL / "h132_bundle_toxicity_field_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H131_PATH = HITL / "h131_sensor_dropout_lattice_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h131mod_h132", H131_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H131_PATH}")
h131mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h131mod
SPEC.loader.exec_module(h131mod)

h130mod = h131mod.h130mod
h129mod = h131mod.h129mod
h126mod = h131mod.h126mod
h123mod = h131mod.h123mod
h118mod = h131mod.h118mod
h102mod = h131mod.h102mod
h085mod = h131mod.h085mod

TARGETS = h131mod.TARGETS
TOL = h131mod.TOL


@dataclass(frozen=True)
class H132Spec:
    name: str
    group: str
    start_name: str
    bundle_mode: str
    max_steps: int
    min_step_score: float
    min_bundle_contradiction: float
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
    worldview: str


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def safe_id(text: str, limit: int = 132) -> str:
    return h085mod.safe_id(text, limit=limit)


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return h085mod.md_table(frame, n=n)


def nonzero_keys(move: np.ndarray) -> set[tuple[int, int]]:
    return h126mod.nonzero_keys(move)


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h132_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h132_bundletox_*.csv"):
        path.unlink()


def root_submission_paths() -> dict[str, Path]:
    paths = h131mod.root_submission_paths()
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


def candidate_specs() -> list[H132Spec]:
    common = dict(
        max_per_subject=26,
        max_per_target=18,
        amp=1.0,
        cap=0.30,
        pool_top=180,
        min_score=0.0,
        min_residual_gap=-0.30,
        max_residual_toxicity=0.95,
        min_residual_safety=0.0,
        max_bad_weighted_pos=0.0006,
        max_bad_max_pos=0.0022,
        max_curv_marg=0.000064,
        max_h088_hard_cosine=-0.018,
    )
    return [
        H132Spec(
            name="h131_plus_witness_q1_eraser",
            group="witness_rescued_q1_toxicity",
            start_name="h131",
            bundle_mode="witness_q_core",
            max_steps=4,
            min_step_score=0.00045,
            min_bundle_contradiction=0.34,
            min_non_h088_passes=3,
            max_cells=29,
            max_rows=24,
            max_h088_cos=-0.056,
            min_good_margin=0.160,
            route_pred_cap=-0.000630,
            h098_pred_cap=-0.000020,
            min_component_gain=0.00020,
            worldview="H131 value additions are safe, but a small Q1 toxicity witness from H129/H130 must still be erased",
            **common,
        ),
        H132Spec(
            name="h131_plus_qbundle_eraser",
            group="bundle_toxicity_after_dropout_value",
            start_name="h131",
            bundle_mode="q_core_or_h129",
            max_steps=5,
            min_step_score=0.00032,
            min_bundle_contradiction=0.50,
            min_non_h088_passes=2,
            max_cells=30,
            max_rows=25,
            max_h088_cos=-0.056,
            min_good_margin=0.160,
            route_pred_cap=-0.000630,
            h098_pred_cap=-0.000020,
            min_component_gain=0.00018,
            worldview="H131 found robust value additions; remaining toxicity is a row-level Q bundle contradiction, not a cell scalar",
            **common,
        ),
        H132Spec(
            name="h131_plus_mixed_bundle_eraser",
            group="bundle_toxicity_mixed_qs",
            start_name="h131",
            bundle_mode="mixed_nonq2",
            max_steps=4,
            min_step_score=0.00028,
            min_bundle_contradiction=0.48,
            min_non_h088_passes=2,
            max_cells=30,
            max_rows=25,
            max_h088_cos=-0.056,
            min_good_margin=0.158,
            route_pred_cap=-0.000620,
            h098_pred_cap=-0.000020,
            min_component_gain=0.00014,
            worldview="toxicity can appear as a mixed subjective/objective row-vector, so damping must operate on non-Q2 bundles",
            **common,
        ),
        H132Spec(
            name="h122_bundle_toxicity_only",
            group="bundle_toxicity_without_value_add",
            start_name="h122",
            bundle_mode="q_core_or_h129",
            max_steps=5,
            min_step_score=0.00025,
            min_bundle_contradiction=0.48,
            min_non_h088_passes=2,
            max_cells=24,
            max_rows=19,
            max_h088_cos=-0.056,
            min_good_margin=0.126,
            route_pred_cap=-0.000600,
            h098_pred_cap=-0.000018,
            min_component_gain=0.00012,
            worldview="before accepting H131 value additions, test whether row-bundle toxicity alone explains the H129/H130 erase signal",
            **common,
        ),
        H132Spec(
            name="h130_bundle_deoverfit",
            group="bundle_toxicity_deoverfit_h130",
            start_name="h130",
            bundle_mode="h130_weak_erases",
            max_steps=4,
            min_step_score=0.00022,
            min_bundle_contradiction=0.45,
            min_non_h088_passes=2,
            max_cells=27,
            max_rows=23,
            max_h088_cos=-0.070,
            min_good_margin=0.200,
            route_pred_cap=-0.000625,
            h098_pred_cap=-0.000018,
            min_component_gain=0.00010,
            worldview="if H130's eraser is overfit, bundle de-overfitting should simplify it without destroying route structure",
            **common,
        ),
    ]


def build_catalog(scored: pd.DataFrame) -> pd.DataFrame:
    out = h131mod.build_catalog(scored).copy()
    h129_ops = HITL / "h129_toxic_action_eraser_hsjepa" / "h129_operations.csv"
    h130_ops = HITL / "h130_rowtarget_lattice_solver_hsjepa" / "h130_operations.csv"
    out["h132_h129_erase_witness"] = 0.0
    out["h132_h130_erase_witness"] = 0.0
    out["h132_h130_add_witness"] = 0.0
    if h129_ops.exists():
        ops = pd.read_csv(h129_ops)
        keys = set(zip(ops["row"].astype(int), ops["target_index"].astype(int)))
        out["h132_h129_erase_witness"] = [
            1.0 if (int(row), int(tidx)) in keys else 0.0
            for row, tidx in zip(out["row"].astype(int), out["target_index"].astype(int))
        ]
    if h130_ops.exists():
        ops = pd.read_csv(h130_ops)
        selected = ops[ops["candidate_id"].astype(str).eq("h130_h122_full_lattice_69da8d10")].copy()
        old_abs = np.abs(selected["old_move"].to_numpy(dtype=np.float64))
        new_abs = np.abs(selected["new_move"].to_numpy(dtype=np.float64))
        erase_keys = set(
            zip(
                selected.loc[new_abs < old_abs - 1.0e-12, "row"].astype(int),
                selected.loc[new_abs < old_abs - 1.0e-12, "target_index"].astype(int),
            )
        )
        add_keys = set(
            zip(
                selected.loc[new_abs > old_abs + 1.0e-12, "row"].astype(int),
                selected.loc[new_abs > old_abs + 1.0e-12, "target_index"].astype(int),
            )
        )
        out["h132_h130_erase_witness"] = [
            1.0 if (int(row), int(tidx)) in erase_keys else 0.0
            for row, tidx in zip(out["row"].astype(int), out["target_index"].astype(int))
        ]
        out["h132_h130_add_witness"] = [
            1.0 if (int(row), int(tidx)) in add_keys else 0.0
            for row, tidx in zip(out["row"].astype(int), out["target_index"].astype(int))
        ]
    return out


def evaluate_matrix(move_mat, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes):
    return h131mod.evaluate_matrix(
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


def check_constraints(move_mat: np.ndarray, evald: dict[str, float], spec: H132Spec) -> bool:
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


def bundle_rows(catalog: pd.DataFrame, start_move: np.ndarray, spec: H132Spec) -> pd.DataFrame:
    active_keys = nonzero_keys(start_move)
    active = catalog[
        [((int(row), int(tidx)) in active_keys) for row, tidx in zip(catalog["row"], catalog["target_index"])]
    ].copy()
    active = active[~active["target"].astype(str).eq("Q2")].copy()
    if active.empty:
        return active

    rows = []
    for row, group in active.groupby("row"):
        targets = set(group["target"].astype(str))
        if spec.bundle_mode in {"q_core_or_h129", "witness_q_core"}:
            keep = {"Q1", "Q3"}
            subset = group[group["target"].astype(str).isin(keep)].copy()
            h129_witness = float(group["h132_h129_erase_witness"].max())
            h130_witness = float(group["h132_h130_erase_witness"].max())
            if subset.empty and h129_witness + h130_witness <= 0:
                continue
            if spec.bundle_mode == "witness_q_core" and h129_witness + h130_witness <= 0:
                continue
        elif spec.bundle_mode == "mixed_nonq2":
            subset = group.copy()
            if len(targets) < 2:
                continue
        elif spec.bundle_mode == "h130_weak_erases":
            subset = group[group["h132_h130_erase_witness"].to_numpy(dtype=np.float64) > 0].copy()
            if subset.empty:
                continue
        else:
            raise ValueError(spec.bundle_mode)
        if subset.empty:
            continue
        row_items = []
        for rec in subset.to_dict("records"):
            tidx = int(rec["target_index"])
            old = float(start_move[int(row), tidx])
            if abs(old) <= 1.0e-12:
                continue
            row_items.append((int(row), tidx, old, str(rec["target"])))
        if not row_items:
            continue
        bad_same = float(subset["h131_bad_same_pressure"].mean())
        shortcut = float(subset["h131_shortcut_pressure"].mean())
        health = float(subset["h131_residual_health"].mean())
        erase = float(subset["h131_erase_evidence"].mean())
        toxic = float(subset["h112_residual_toxicity"].mean())
        source = float(subset["h131_source_strength"].mean())
        witness = float(max(subset["h132_h129_erase_witness"].max(), subset["h132_h130_erase_witness"].max()))
        contradiction = float(
            0.30 * min(health, max(bad_same, shortcut))
            + 0.22 * max(bad_same, shortcut)
            + 0.18 * erase
            + 0.12 * toxic
            + 0.12 * witness
            + 0.06 * (1.0 - min(source, 1.0))
        )
        rows.append(
            {
                "row": int(row),
                "subject_id": str(subset["subject_id"].iloc[0]),
                "sleep_date": str(subset["sleep_date"].iloc[0]),
                "bundle_targets": ",".join(sorted({item[3] for item in row_items})),
                "bundle_cells": row_items,
                "bundle_size": len(row_items),
                "h132_bundle_bad_same": bad_same,
                "h132_bundle_shortcut": shortcut,
                "h132_bundle_health": health,
                "h132_bundle_erase_evidence": erase,
                "h132_bundle_toxicity": toxic,
                "h132_bundle_source_strength": source,
                "h132_bundle_witness": witness,
                "h132_bundle_contradiction": contradiction,
            }
        )
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    return out.sort_values(["h132_bundle_contradiction", "h132_bundle_witness"], ascending=[False, False]).reset_index(drop=True)


def apply_bundle(move_mat: np.ndarray, bundle: dict[str, object], mode: str) -> tuple[np.ndarray, str]:
    tmp = move_mat.copy()
    cells = list(bundle["bundle_cells"])
    if mode == "off":
        for row, tidx, _old, _target in cells:
            tmp[int(row), int(tidx)] = 0.0
        return tmp, "off"
    if mode == "half":
        for row, tidx, old, _target in cells:
            tmp[int(row), int(tidx)] = 0.5 * float(old)
        return tmp, "half"
    if mode == "quarter":
        for row, tidx, old, _target in cells:
            tmp[int(row), int(tidx)] = 0.25 * float(old)
        return tmp, "quarter"
    raise ValueError(mode)


def bundle_step_score(after: dict[str, float], before: dict[str, float], bundle: dict[str, object]) -> tuple[float, dict[str, float]]:
    d_route = after["route"] - before["route"]
    d_h098 = after["h098"] - before["h098"]
    d_curv = after["curv_marg"] - before["curv_marg"]
    d_badw = after["badw"] - before["badw"]
    d_badmax = after["badmax"] - before["badmax"]
    d_h088 = after["h088"] - before["h088"]
    d_margin = after["margin"] - before["margin"]
    contradiction = float(bundle["h132_bundle_contradiction"])
    witness = float(bundle["h132_bundle_witness"])
    bonus = 0.00034 * contradiction + 0.00009 * witness

    route_view = (
        210.0 * (-d_h098)
        + 170.0 * max(-d_route, 0.0)
        - 70.0 * max(d_route, 0.0)
        + 140.0 * (-d_curv)
        + bonus
    )
    no_h088_view = (
        190.0 * (-d_h098)
        + 155.0 * max(-d_route, 0.0)
        - 70.0 * max(d_route, 0.0)
        + 120.0 * (-d_curv)
        - 5.0 * d_badw
        - 3.0 * d_badmax
        + bonus
    )
    bundle_view = (
        0.0014 * contradiction
        + 0.00025 * witness
        + 0.00018 * float(bundle["h132_bundle_bad_same"])
        + 0.00018 * float(bundle["h132_bundle_shortcut"])
        - 0.00008 * float(bundle["h132_bundle_source_strength"])
        - 50.0 * max(d_h098, 0.0)
        - 35.0 * max(d_route, 0.0)
    )
    public_stress_view = (
        0.08 * (-d_h088)
        + 0.09 * d_margin
        - 6.0 * d_badw
        - 3.0 * d_badmax
        + 0.55 * bonus
    )
    scores = {
        "h132_route_view_score": float(route_view),
        "h132_no_h088_view_score": float(no_h088_view),
        "h132_bundle_view_score": float(bundle_view),
        "h132_public_stress_view_score": float(public_stress_view),
    }
    scores["h132_non_h088_passes"] = float(sum(scores[key] > 0.0 for key in ["h132_route_view_score", "h132_no_h088_view_score", "h132_bundle_view_score"]))
    scores["h132_stress_passes"] = float(sum(scores[key] > 0.0 for key in ["h132_route_view_score", "h132_no_h088_view_score", "h132_bundle_view_score", "h132_public_stress_view_score"]))
    aggregate = 0.27 * route_view + 0.27 * no_h088_view + 0.26 * bundle_view + 0.20 * public_stress_view
    scores["h132_step_score"] = float(aggregate)
    return float(aggregate), scores


def coordinate_solve(start: np.ndarray, bundles: pd.DataFrame, spec: H132Spec, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes) -> tuple[np.ndarray, pd.DataFrame, dict[str, float], dict[str, float]]:
    move_mat = start.copy()
    start_eval = evaluate_matrix(move_mat, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
    ops = []
    used_rows: set[int] = set()
    for step in range(spec.max_steps):
        before = evaluate_matrix(move_mat, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
        best = None
        for rec in bundles.head(spec.pool_top).to_dict("records"):
            row = int(rec["row"])
            if row in used_rows:
                continue
            if float(rec["h132_bundle_contradiction"]) < spec.min_bundle_contradiction:
                continue
            for mode in ["off", "half", "quarter"]:
                tmp, state = apply_bundle(move_mat, rec, mode)
                if np.allclose(tmp, move_mat, atol=1.0e-12):
                    continue
                after = evaluate_matrix(tmp, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
                if not check_constraints(tmp, after, spec):
                    continue
                score, view_scores = bundle_step_score(after, before, rec)
                if view_scores["h132_non_h088_passes"] < spec.min_non_h088_passes:
                    continue
                if best is None or score > best["h132_step_score"]:
                    best = {
                        "step": step + 1,
                        "row": row,
                        "subject_id": rec["subject_id"],
                        "sleep_date": rec["sleep_date"],
                        "bundle_targets": rec["bundle_targets"],
                        "bundle_size": int(rec["bundle_size"]),
                        "state": state,
                        **{key: rec[key] for key in rec if key.startswith("h132_bundle_")},
                        **view_scores,
                        **{f"after_{key2}": value for key2, value in after.items()},
                        **{f"delta_{key2}": after[key2] - before[key2] for key2 in after},
                    }
        if best is None or float(best["h132_step_score"]) < spec.min_step_score:
            break
        bundle = bundles[bundles["row"].astype(int).eq(int(best["row"]))].iloc[0].to_dict()
        move_mat, _state = apply_bundle(move_mat, bundle, str(best["state"]))
        used_rows.add(int(best["row"]))
        ops.append(best)
    final_eval = evaluate_matrix(move_mat, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
    return move_mat, pd.DataFrame(ops), start_eval, final_eval


def make_selected(catalog: pd.DataFrame, move_mat: np.ndarray) -> pd.DataFrame:
    selected = h130mod.make_selected(catalog, move_mat)
    if selected.empty:
        return selected
    selected["h132_actual_move"] = selected["h130_actual_move"]
    selected["h112_move"] = selected["h132_actual_move"].to_numpy(dtype=np.float64)
    return selected


def operation_summary(ops: pd.DataFrame) -> dict[str, object]:
    if ops.empty:
        return {
            "h132_ops": 0,
            "h132_off_ops": 0,
            "h132_half_ops": 0,
            "h132_quarter_ops": 0,
            "h132_op_targets": "",
            "h132_mean_contradiction": 0.0,
            "h132_mean_non_h088_passes": 0.0,
            "h132_mean_step_score": 0.0,
        }
    return {
        "h132_ops": int(len(ops)),
        "h132_off_ops": int(ops["state"].astype(str).eq("off").sum()),
        "h132_half_ops": int(ops["state"].astype(str).eq("half").sum()),
        "h132_quarter_ops": int(ops["state"].astype(str).eq("quarter").sum()),
        "h132_op_targets": ";".join(f"{k}:{v}" for k, v in ops["bundle_targets"].value_counts().to_dict().items()),
        "h132_mean_contradiction": float(ops["h132_bundle_contradiction"].mean()),
        "h132_mean_non_h088_passes": float(ops["h132_non_h088_passes"].mean()),
        "h132_mean_step_score": float(ops["h132_step_score"].mean()),
    }


def component_gain(final: dict[str, float], before: dict[str, float]) -> float:
    return (
        220.0 * (-(final["h098"] - before["h098"]))
        + 150.0 * (-(final["curv_marg"] - before["curv_marg"]))
        + 145.0 * max(-(final["route"] - before["route"]), 0.0)
        - 75.0 * max(final["route"] - before["route"], 0.0)
        + 0.12 * (final["margin"] - before["margin"])
        + 0.08 * (-(final["h088"] - before["h088"]))
    )


def previous_moves(sample: pd.DataFrame, base_prob: np.ndarray, moves: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    out = {
        name: moves[name].reshape(-1)
        for name in ["h131", "h130", "h129", "h128", "h127", "h126", "h124", "h122"]
    }
    out["h088"] = load_move("h088", sample, base_prob).reshape(-1)
    out["h018"] = load_move("h018", sample, base_prob).reshape(-1)
    return out


def run() -> None:
    cleanup_previous_outputs()
    pool, _public, sample, base_prob, cell, h098_fit, route_fit, basis_fit_df, basis_fit_moves, bad_axes, bad_moves, good_moves, axes, fit, model_scores, props = h118mod.prepare_context()
    scored = h123mod.build_scored_pool(pool, base_prob, fit, bad_axes, bad_moves, good_moves, axes, props)
    catalog = build_catalog(scored)
    moves = {name: load_move(name, sample, base_prob) for name in ["h122", "h124", "h126", "h127", "h128", "h129", "h130", "h131"]}
    known = known_hashes(sample)
    previous = previous_moves(sample, base_prob, moves)

    candidate_rows = []
    selected_frames = []
    op_frames = []
    audit_rows = []
    start_rows = []
    bundle_frames = []
    for spec in candidate_specs():
        start_move = load_move(spec.start_name, sample, base_prob)
        bundles = bundle_rows(catalog, start_move, spec)
        start_eval = evaluate_matrix(start_move, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
        start_rows.append({"start_name": spec.start_name, "spec_name": spec.name, **start_eval, "start_cells": int((np.abs(start_move) > 1.0e-12).sum()), "bundle_rows": int(len(bundles))})
        audit_rows.append(
            {
                "spec_name": spec.name,
                "start_name": spec.start_name,
                "bundle_mode": spec.bundle_mode,
                "bundle_rows": int(len(bundles)),
                "mean_contradiction": float(bundles["h132_bundle_contradiction"].mean()) if not bundles.empty else 0.0,
                "max_contradiction": float(bundles["h132_bundle_contradiction"].max()) if not bundles.empty else 0.0,
            }
        )
        if not bundles.empty:
            b2 = bundles.copy()
            b2.insert(0, "spec_name", spec.name)
            bundle_frames.append(b2.drop(columns=["bundle_cells"]))
        if bundles.empty:
            continue
        move_mat, ops, before, final = coordinate_solve(
            start_move,
            bundles,
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
        gain = component_gain(final, before)
        audit_rows[-1]["component_gain"] = float(gain)
        if gain < spec.min_component_gain:
            audit_rows[-1]["rejected_component_gain"] = float(gain)
            continue
        prob = h130mod.materialize(base_prob, move_mat)
        hash_id = short_hash(prob)
        if hash_id in known:
            audit_rows[-1]["duplicate_hash"] = hash_id
            continue
        candidate_id = safe_id(f"h132_{spec.name}_{hash_id}", 128)
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
            "h132_start_field": spec.start_name,
            "h132_start_cells": int((np.abs(start_move) > 1.0e-12).sum()),
            "h132_bundle_rows": int(len(bundles)),
            "h132_component_gain": float(gain),
            "h132_delta_start_route": float(final["route"] - before["route"]),
            "h132_delta_start_h098": float(final["h098"] - before["h098"]),
            "h132_delta_start_h088": float(final["h088"] - before["h088"]),
            "h132_delta_start_margin": float(final["margin"] - before["margin"]),
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
        metrics["h132_worldview"] = spec.worldview
        metrics["h132_fit_feature_set"] = fit.feature_set
        metrics["h132_fit_alpha"] = fit.alpha
        metrics["h132_fit_score"] = fit.score
        metrics["h132_score"] = (
            305.0 * (-float(metrics["model_pred_delta_vs_h057"]))
            + 250.0 * (-float(metrics["route_basis_pred_delta_vs_h057"]))
            + 115.0 * (-float(metrics["h118_curv_marginal_vs_zero"]))
            + 0.16 * float(metrics["h102_cum_good_bad_margin"])
            + 0.07 * max(-float(metrics["h102_cum_h088_axis_cos"]), 0.0)
            + 0.12 * float(metrics["selected_mean_residual_safety"])
            + 0.12 * float(metrics["selected_mean_residual_gap"])
            - 0.17 * float(metrics["selected_mean_residual_toxicity"])
            + 1.3 * max(gain, 0.0)
            + 0.016 * float(op_diag["h132_mean_non_h088_passes"])
            + 0.010 * float(op_diag["h132_mean_contradiction"])
            - 0.012 * max(float(metrics["selected_cells"]) - 34.0, 0.0)
            - 20.0 * max(float(metrics["hard_diag_delta_vs_h057"]), 0.0)
            - 0.9 * max(h088_cos, 0.0)
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
    catalog.to_csv(OUT / "h132_catalog.csv", index=False)
    audit.to_csv(OUT / "h132_audit.csv", index=False)
    starts.to_csv(OUT / "h132_start_metrics.csv", index=False)
    model_scores.to_csv(OUT / "h132_curvature_model_scores.csv", index=False)
    if bundle_frames:
        pd.concat(bundle_frames, ignore_index=True).to_csv(OUT / "h132_bundles.csv", index=False)
    if candidates.empty:
        report = f"""# H132 Bundle-Toxicity Field HS-JEPA

No candidate was promoted.

Audit:

{md_table(audit, 20)}

Start metrics:

{md_table(starts, 20)}
"""
        (OUT / "h132_report.md").write_text(report, encoding="utf-8")
        print("H132 promoted no candidate")
        print(audit.to_string(index=False))
        return

    candidates = candidates.sort_values(["h132_score", "h132_component_gain", "model_pred_delta_vs_h057"], ascending=[False, False, True]).reset_index(drop=True)
    selected = candidates.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"submission_h132_bundletox_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)
    decision = {
        "decision": "promote_h132_bundle_toxicity_field",
        "selected_candidate_id": selected["candidate_id"],
        "root_uploadsafe_path": str(root_path.resolve()),
        "worldview": selected["h132_worldview"],
        **selected,
        **{f"root_{key}": value for key, value in validation.items()},
    }
    candidates.to_csv(OUT / "h132_candidates.csv", index=False)
    pd.concat(selected_frames, ignore_index=True).to_csv(OUT / "h132_selected_cells.csv", index=False)
    pd.concat(op_frames, ignore_index=True).to_csv(OUT / "h132_operations.csv", index=False)
    pd.DataFrame([decision]).to_csv(OUT / "h132_decision.csv", index=False)

    cols = [
        "candidate_id",
        "spec_name",
        "h132_start_field",
        "selected_cells",
        "changed_rows_vs_h057",
        "Q1_changed_vs_h057",
        "Q2_changed_vs_h057",
        "Q3_changed_vs_h057",
        "S1_changed_vs_h057",
        "S2_changed_vs_h057",
        "S3_changed_vs_h057",
        "S4_changed_vs_h057",
        "h132_ops",
        "h132_off_ops",
        "h132_half_ops",
        "h132_quarter_ops",
        "h132_op_targets",
        "h132_mean_contradiction",
        "h132_mean_non_h088_passes",
        "h132_delta_start_route",
        "h132_delta_start_h098",
        "h132_delta_start_h088",
        "h132_delta_start_margin",
        "model_pred_delta_vs_h057",
        "route_basis_pred_delta_vs_h057",
        "h102_cum_h088_axis_cos",
        "h102_cum_good_bad_margin",
        "h132_component_gain",
        "h132_score",
        "file",
    ]
    report = f"""# H132 Bundle-Toxicity Field HS-JEPA

Question: did H131 reject erase/damp because erasure is H088 shortcut, or
because toxicity is a row-level bundle contradiction rather than a cell scalar?

Audit:

{md_table(audit, 20)}

Start metrics:

{md_table(starts, 20)}

Candidates:

{md_table(candidates[cols], 20)}

Decision:

{md_table(pd.DataFrame([decision]), 1)}

Interpretation rule:

- If H132 improves, HS-JEPA needs a row-bundle toxicity field after
  sensor-dropout value assignment.
- If H131 improves more, the bundle eraser is still H088-shaped shortcut and
  robust value-add should stay separate.
- If H129/H130 improves more, bundle evidence is missing the public-specific
  toxicity signal that H088/margin sensors see.
"""
    (OUT / "h132_report.md").write_text(report, encoding="utf-8")
    print("H132 selected candidate")
    print(candidates[cols].head(10).to_string(index=False))
    print("\nDecision")
    print(pd.DataFrame([decision])[["decision", "selected_candidate_id", "root_uploadsafe_path", "root_upload_safe"]].to_string(index=False))


if __name__ == "__main__":
    run()
