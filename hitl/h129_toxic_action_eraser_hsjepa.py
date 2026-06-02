#!/usr/bin/env python3
"""H129: toxic-action eraser HS-JEPA.

H128 showed that regenerated value can survive only in a narrow H057/H088
conflict bridge.  H129 tests the complementary big bet: the missing
public/private equation may be a toxicity field that erases or attenuates
unsafe row-target actions after assignment, rather than adding new actions.
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
OUT = HITL / "h129_toxic_action_eraser_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H128_PATH = HITL / "h128_frontier_value_regenerator_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h128mod_h129", H128_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H128_PATH}")
h128mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h128mod
SPEC.loader.exec_module(h128mod)

h127mod = h128mod.h127mod
h126mod = h128mod.h126mod
h123mod = h128mod.h123mod
h118mod = h128mod.h118mod
h115mod = h128mod.h115mod
h102mod = h128mod.h102mod
h085mod = h128mod.h085mod

TARGETS = h128mod.TARGETS
TOL = h128mod.TOL


@dataclass(frozen=True)
class H129Spec:
    name: str
    group: str
    start_name: str
    condition: str
    factors: tuple[float, ...]
    max_ops: int
    min_remaining_cells: int
    min_op_score: float
    min_toxic_rank: float
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
    for path in OUT.glob("submission_h129_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h129_toxiceraser_*.csv"):
        path.unlink()


def candidate_specs() -> list[H129Spec]:
    common = dict(
        max_cells=52,
        max_rows=44,
        max_per_subject=28,
        max_per_target=30,
        amp=1.0,
        cap=0.30,
        pool_top=260,
        min_score=0.0,
        min_residual_gap=-0.30,
        max_residual_toxicity=0.90,
        min_residual_safety=0.00,
        max_bad_weighted_pos=0.0005,
        max_bad_max_pos=0.0020,
        max_curv_marg=0.000060,
        max_h088_hard_cosine=-0.020,
        min_component_gain=0.00020,
    )
    return [
        H129Spec(
            name="h128_conflict_erase",
            group="h128_conflict_erase",
            start_name="h128",
            condition="post_h127_or_conflict",
            factors=(0.0, 0.50, -0.25),
            max_ops=10,
            min_remaining_cells=22,
            min_op_score=0.00025,
            min_toxic_rank=0.35,
            max_h088_cos=-0.044,
            min_good_margin=0.180,
            route_pred_cap=-0.000690,
            h098_pred_cap=-0.000027,
            worldview="H128 may have found value but over-assigned S1/S4; erase only toxic conflict-bridge actions that fail public/private safety",
            **common,
        ),
        H129Spec(
            name="h127_tail_erase",
            group="h127_tail_erase",
            start_name="h127",
            condition="post_h122_stage_tail",
            factors=(0.0, 0.50, -0.20),
            max_ops=8,
            min_remaining_cells=20,
            min_op_score=0.00025,
            min_toxic_rank=0.30,
            max_h088_cos=-0.048,
            min_good_margin=0.142,
            route_pred_cap=-0.000690,
            h098_pred_cap=-0.000027,
            worldview="H127's residual-margin stabilizer may be real, but earlier stage-tail completions may still contain toxic over-assignment",
            **common,
        ),
        H129Spec(
            name="h126_amp_erase",
            group="h126_amp_erase",
            start_name="h126",
            condition="post_h122_or_lowgap",
            factors=(0.0, 0.50, 0.75),
            max_ops=8,
            min_remaining_cells=20,
            min_op_score=0.00022,
            min_toxic_rank=0.28,
            max_h088_cos=-0.048,
            min_good_margin=0.135,
            route_pred_cap=-0.000692,
            h098_pred_cap=-0.000027,
            worldview="H126 solved component amplitudes globally, but individual high-toxicity cells may need local damping or removal",
            **common,
        ),
        H129Spec(
            name="h124_refill_veto",
            group="h124_refill_veto",
            start_name="h124",
            condition="post_h122_stage_tail",
            factors=(0.0, 0.50),
            max_ops=6,
            min_remaining_cells=18,
            min_op_score=0.00020,
            min_toxic_rank=0.25,
            max_h088_cos=-0.050,
            min_good_margin=0.130,
            route_pred_cap=-0.000695,
            h098_pred_cap=-0.000027,
            worldview="dual-sensor refill may still over-complete some S/Q stage cells; public-safe assignment may be a smaller subset of H124",
            **common,
        ),
        H129Spec(
            name="h122_core_toxicity",
            group="h122_core_toxicity",
            start_name="h122",
            condition="high_toxic_all",
            factors=(0.0, 0.50),
            max_ops=5,
            min_remaining_cells=18,
            min_op_score=0.00020,
            min_toxic_rank=0.55,
            max_h088_cos=-0.052,
            min_good_margin=0.125,
            route_pred_cap=-0.000600,
            h098_pred_cap=-0.000018,
            worldview="even H122's pruned core may retain a small public-toxic action field; delete only the highest toxicity core cells",
            **common,
        ),
    ]


def root_submission_paths() -> dict[str, Path]:
    return {
        "h128": ROOT / "submission_h128_frontiervalue_a6a6e648_uploadsafe.csv",
        "h127": ROOT / "submission_h127_residbasis_9b7f8d9a_uploadsafe.csv",
        "h126": ROOT / "submission_h126_coeffeq_3fe3eee4_uploadsafe.csv",
        "h125": ROOT / "submission_h125_rowbundle_f3990392_uploadsafe.csv",
        "h124": ROOT / "submission_h124_dualsensor_b8e822c0_uploadsafe.csv",
        "h123": ROOT / "submission_h123_refilleq_8958f688_uploadsafe.csv",
        "h122": ROOT / "submission_h122_pruneeq_0a9edcce_uploadsafe.csv",
        "h118": ROOT / "submission_h118_forbiddenveto_e81167a8_uploadsafe.csv",
        "h088": ROOT / "submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv",
        "h018": ROOT / "submission_h018_hard_label_world_combined_all_k1750_a1_uploadsafe.csv",
    }


def known_hashes(sample: pd.DataFrame) -> set[str]:
    hashes: set[str] = set()
    for path in ROOT.glob("submission_h*_uploadsafe.csv"):
        try:
            df = h085mod.load_sub(path, sample)
            hashes.add(short_hash(df[TARGETS].to_numpy(dtype=np.float64)))
        except Exception:
            continue
    return hashes


def load_move(name: str, sample: pd.DataFrame, base_prob: np.ndarray) -> np.ndarray:
    path = root_submission_paths()[name]
    if not path.exists():
        raise FileNotFoundError(path)
    return h126mod.load_move_path(path, sample, base_prob).reshape(base_prob.shape)


def selected_for_source(name: str) -> pd.DataFrame:
    mapping = {
        "h128": ("h128_frontier_value_regenerator_hsjepa/h128_selected_cells.csv", "h128_frontier_value_regenerator_hsjepa/h128_decision.csv"),
        "h127": ("h127_residual_basis_discovery_hsjepa/h127_selected_cells.csv", "h127_residual_basis_discovery_hsjepa/h127_decision.csv"),
        "h126": ("h126_component_coefficient_equation_hsjepa/h126_selected_cells.csv", "h126_component_coefficient_equation_hsjepa/h126_decision.csv"),
        "h125": ("h125_row_bundle_equation_solver_hsjepa/h125_selected_cells.csv", "h125_row_bundle_equation_solver_hsjepa/h125_decision.csv"),
        "h124": ("h124_dual_sensor_refill_envelope_hsjepa/h124_selected_cells.csv", "h124_dual_sensor_refill_envelope_hsjepa/h124_decision.csv"),
        "h123": ("h123_prune_refill_equation_solver_hsjepa/h123_selected_cells.csv", "h123_prune_refill_equation_solver_hsjepa/h123_decision.csv"),
        "h122": ("h122_action_prune_equation_solver_hsjepa/h122_selected_cells.csv", "h122_action_prune_equation_solver_hsjepa/h122_decision.csv"),
    }
    if name not in mapping:
        return pd.DataFrame()
    selected_rel, decision_rel = mapping[name]
    selected_path = HITL / selected_rel
    decision_path = HITL / decision_rel
    if not selected_path.exists() or not decision_path.exists():
        return pd.DataFrame()
    selected = pd.read_csv(selected_path)
    decision = pd.read_csv(decision_path)
    cid = str(decision["selected_candidate_id"].iloc[0])
    if "candidate_id" in selected.columns:
        selected = selected[selected["candidate_id"].astype(str) == cid].copy()
    selected["row"] = selected["row"].astype(int)
    selected["target_index"] = selected["target_index"].astype(int)
    return selected


def load_h122_core_keys() -> set[tuple[int, int]]:
    sel = selected_for_source("h122")
    if sel.empty:
        return set()
    return set(zip(sel["row"].astype(int), sel["target_index"].astype(int)))


def load_h127_keys() -> set[tuple[int, int]]:
    sel = selected_for_source("h127")
    if sel.empty:
        return set()
    return set(zip(sel["row"].astype(int), sel["target_index"].astype(int)))


def build_catalog(scored: pd.DataFrame) -> pd.DataFrame:
    frames = [scored.copy()]
    for rel in [
        "h122_action_prune_equation_solver_hsjepa/h122_selected_cells.csv",
        "h123_prune_refill_equation_solver_hsjepa/h123_selected_cells.csv",
        "h124_dual_sensor_refill_envelope_hsjepa/h124_selected_cells.csv",
        "h125_row_bundle_equation_solver_hsjepa/h125_selected_cells.csv",
        "h126_component_coefficient_equation_hsjepa/h126_selected_cells.csv",
        "h127_residual_basis_discovery_hsjepa/h127_selected_cells.csv",
        "h128_frontier_value_regenerator_hsjepa/h128_selected_cells.csv",
        "h128_frontier_value_regenerator_hsjepa/h128_value_pool.csv",
    ]:
        path = HITL / rel
        if path.exists():
            frames.append(pd.read_csv(path))
    out = pd.concat(frames, ignore_index=True, sort=False)
    out["row"] = out["row"].astype(int)
    out["target_index"] = out["target_index"].astype(int)
    if "flat_index" not in out.columns:
        out["flat_index"] = out["row"].astype(int) * len(TARGETS) + out["target_index"].astype(int)
    out["flat_index"] = out["flat_index"].astype(int)
    out = out.sort_values(["row", "target_index"]).drop_duplicates(["row", "target_index"], keep="last").reset_index(drop=True)
    return out


def add_row_sensor(catalog: pd.DataFrame) -> pd.DataFrame:
    out = catalog.copy()
    row_sensor_path = HITL / "h120_toxic_posterior_row_sensor_hsjepa/h120_row_sensor.csv"
    if row_sensor_path.exists():
        row_sensor = pd.read_csv(row_sensor_path)
        cols = [c for c in ["row", "h120_row_sensor_raw", "h120_row_sensor_rank", "h120_row_sensor_cells"] if c in row_sensor.columns]
        out = out.merge(row_sensor[cols].drop_duplicates("row"), on="row", how="left")
    for col in ["h120_row_sensor_raw", "h120_row_sensor_rank", "h120_row_sensor_cells"]:
        if col not in out.columns:
            out[col] = 0.0
    out[["h120_row_sensor_raw", "h120_row_sensor_rank", "h120_row_sensor_cells"]] = out[["h120_row_sensor_raw", "h120_row_sensor_rank", "h120_row_sensor_cells"]].fillna(0.0)
    return out


def numeric(frame: pd.DataFrame, col: str, default: float = 0.0) -> np.ndarray:
    if col not in frame.columns:
        return np.full(len(frame), default, dtype=np.float64)
    return pd.to_numeric(frame[col], errors="coerce").fillna(default).to_numpy(dtype=np.float64)


def add_toxicity_scores(catalog: pd.DataFrame) -> pd.DataFrame:
    out = add_row_sensor(catalog)
    for col, default in [
        ("h112_residual_toxicity", 0.50),
        ("h112_residual_safety", 0.50),
        ("h112_residual_gap", 0.00),
        ("h117_forbidden_pressure", 0.00),
        ("h117_forbidden_same", 0.00),
        ("h088_toxicity", 0.50),
        ("latent_shortcut_energy", 0.50),
        ("bad_pressure_rank", 0.50),
        ("h057_h088_same_conflict", 0.00),
        ("h057_h088_anti_conflict", 0.00),
        ("h110_toxicity_score", 0.00),
        ("h110_benefit_toxicity_gap", 0.00),
    ]:
        if col not in out.columns:
            out[col] = default
        out[col] = pd.to_numeric(out[col], errors="coerce").fillna(default)
    out["h129_toxicity_field"] = (
        0.18 * rank01(numeric(out, "h112_residual_toxicity"), high=True)
        + 0.16 * rank01(numeric(out, "h088_toxicity"), high=True)
        + 0.13 * rank01(numeric(out, "h117_forbidden_pressure"), high=True)
        + 0.12 * rank01(numeric(out, "bad_pressure_rank"), high=True)
        + 0.11 * rank01(numeric(out, "latent_shortcut_energy"), high=True)
        + 0.10 * numeric(out, "h120_row_sensor_rank")
        + 0.08 * numeric(out, "h057_h088_same_conflict")
        + 0.06 * rank01(numeric(out, "h110_toxicity_score"), high=True)
        - 0.15 * rank01(numeric(out, "h112_residual_safety"), high=True)
        - 0.12 * rank01(numeric(out, "h112_residual_gap"), high=True)
        - 0.08 * numeric(out, "h057_h088_anti_conflict")
        - 0.06 * rank01(numeric(out, "h110_benefit_toxicity_gap"), high=True)
    )
    out["h129_toxic_rank"] = rank01(out["h129_toxicity_field"].to_numpy(dtype=np.float64), high=True)
    return out


def evaluate_matrix(move_mat, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes):
    return h128mod.evaluate_matrix(
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


def op_score(after: dict[str, float], before: dict[str, float], toxic_rank: float, factor: float) -> float:
    return (
        260.0 * (-(after["h098"] - before["h098"]))
        + 190.0 * (-(after["curv_marg"] - before["curv_marg"]))
        + 160.0 * max(-(after["route"] - before["route"]), 0.0)
        - 95.0 * max(after["route"] - before["route"], 0.0)
        + 0.24 * (after["margin"] - before["margin"])
        + 0.16 * (-(after["h088"] - before["h088"]))
        - 5.0 * (after["badw"] - before["badw"])
        - 3.0 * (after["badmax"] - before["badmax"])
        + 0.0012 * toxic_rank
        + (0.00015 if factor == 0.0 else 0.0)
    )


def target_allowed(rec: dict[str, object], spec: H129Spec, h122_keys: set[tuple[int, int]], h127_keys: set[tuple[int, int]]) -> bool:
    row = int(rec["row"])
    tidx = int(rec["target_index"])
    key = (row, tidx)
    target = str(rec["target"])
    toxic_rank = max(float(rec.get("h129_toxic_rank", 0.0)), float(rec.get("h129_active_toxic_rank", 0.0)))
    if toxic_rank < spec.min_toxic_rank:
        return False
    if spec.condition == "high_toxic_all":
        return True
    if spec.condition == "post_h122_stage_tail":
        return key not in h122_keys and target in {"Q3", "S1", "S2", "S3", "S4"}
    if spec.condition == "post_h122_or_lowgap":
        return key not in h122_keys or float(rec.get("h112_residual_gap", 0.0)) < 0.08
    if spec.condition == "post_h127_or_conflict":
        return key not in h127_keys or float(rec.get("h057_h088_same_conflict", 0.0)) >= 0.5 or float(rec.get("h057_h088_anti_conflict", 0.0)) >= 0.5
    raise ValueError(spec.condition)


def active_frame(catalog: pd.DataFrame, move_mat: np.ndarray, spec: H129Spec, h122_keys: set[tuple[int, int]], h127_keys: set[tuple[int, int]]) -> pd.DataFrame:
    keys = nonzero_keys(move_mat)
    work = catalog[[((int(row), int(tidx)) in keys) for row, tidx in zip(catalog["row"], catalog["target_index"])]].copy()
    if work.empty:
        return work
    work["h129_current_move"] = [
        float(move_mat[int(row), int(tidx)])
        for row, tidx in zip(work["row"].astype(int), work["target_index"].astype(int))
    ]
    work["h129_active_toxic_rank"] = rank01(work["h129_toxicity_field"].to_numpy(dtype=np.float64), high=True)
    keep = [target_allowed(rec, spec, h122_keys, h127_keys) for rec in work.to_dict("records")]
    work = work[np.asarray(keep)].copy()
    return work.sort_values(["h129_toxic_rank", "h129_toxicity_field"], ascending=[False, False]).reset_index(drop=True)


def check_constraints(evald: dict[str, float], spec: H129Spec) -> bool:
    if evald["badw"] > spec.max_bad_weighted_pos or evald["badmax"] > spec.max_bad_max_pos:
        return False
    if evald["h088"] > spec.max_h088_cos or evald["margin"] < spec.min_good_margin:
        return False
    if evald["route"] > spec.route_pred_cap or evald["h098"] > spec.h098_pred_cap:
        return False
    if evald["curv_marg"] > spec.max_curv_marg:
        return False
    return True


def greedy_erase(start: np.ndarray, work: pd.DataFrame, spec: H129Spec, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes) -> tuple[np.ndarray, pd.DataFrame, dict[str, float], dict[str, float]]:
    move_mat = start.copy()
    start_eval = evaluate_matrix(move_mat, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
    ops = []
    operated: set[tuple[int, int]] = set()
    for step in range(spec.max_ops):
        active = nonzero_keys(move_mat)
        if len(active) <= spec.min_remaining_cells:
            break
        before = evaluate_matrix(move_mat, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
        best = None
        for rec in work.head(spec.pool_top).to_dict("records"):
            row = int(rec["row"])
            tidx = int(rec["target_index"])
            key = (row, tidx)
            if key in operated or key not in active:
                continue
            old_move = float(move_mat[row, tidx])
            for factor in spec.factors:
                new_move = old_move * float(factor)
                if abs(new_move - old_move) <= 1.0e-12:
                    continue
                tmp = move_mat.copy()
                tmp[row, tidx] = new_move
                after = evaluate_matrix(tmp, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
                if not check_constraints(after, spec):
                    continue
                score = op_score(after, before, float(rec.get("h129_toxic_rank", 0.0)), float(factor))
                if best is None or score > best["h129_op_score"]:
                    best = {
                        "step": step + 1,
                        "row": row,
                        "target_index": tidx,
                        "target": str(rec["target"]),
                        "subject_id": str(rec.get("subject_id", "")),
                        "sleep_date": str(rec.get("sleep_date", "")),
                        "old_move": old_move,
                        "new_move": new_move,
                        "factor": float(factor),
                        "h129_toxicity_field": float(rec.get("h129_toxicity_field", 0.0)),
                        "h129_toxic_rank": float(rec.get("h129_toxic_rank", 0.0)),
                        "h112_residual_toxicity": float(rec.get("h112_residual_toxicity", 0.0)),
                        "h112_residual_safety": float(rec.get("h112_residual_safety", 0.0)),
                        "h112_residual_gap": float(rec.get("h112_residual_gap", 0.0)),
                        "h129_op_score": score,
                        **{f"after_{key2}": value for key2, value in after.items()},
                        **{f"delta_{key2}": after[key2] - before[key2] for key2 in after},
                    }
        if best is None or float(best["h129_op_score"]) < spec.min_op_score:
            break
        move_mat[int(best["row"]), int(best["target_index"])] = float(best["new_move"])
        operated.add((int(best["row"]), int(best["target_index"])))
        ops.append(best)
    final_eval = evaluate_matrix(move_mat, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
    return move_mat, pd.DataFrame(ops), start_eval, final_eval


def make_selected(catalog: pd.DataFrame, move_mat: np.ndarray) -> pd.DataFrame:
    keys = nonzero_keys(move_mat)
    selected = catalog[[((int(row), int(tidx)) in keys) for row, tidx in zip(catalog["row"], catalog["target_index"])]].copy()
    selected = selected.sort_values(["row", "target_index"]).drop_duplicates(["row", "target_index"], keep="last").reset_index(drop=True)
    selected["h129_actual_move"] = [
        float(move_mat[int(row), int(tidx)])
        for row, tidx in zip(selected["row"].astype(int), selected["target_index"].astype(int))
    ]
    selected = selected[np.abs(selected["h129_actual_move"].to_numpy(dtype=np.float64)) > 1.0e-12].copy()
    selected["h112_move"] = selected["h129_actual_move"].to_numpy(dtype=np.float64)
    selected["h097_move_col"] = "h112_move"
    return selected.sort_values(["row", "target_index"]).reset_index(drop=True)


def operation_summary(ops: pd.DataFrame) -> dict[str, object]:
    if ops.empty:
        return {
            "h129_ops": 0,
            "h129_removed_cells": 0,
            "h129_damped_cells": 0,
            "h129_inverted_cells": 0,
            "h129_op_targets": "",
            "h129_mean_toxic_rank": 0.0,
            "h129_mean_op_score": 0.0,
        }
    factors = ops["factor"].to_numpy(dtype=np.float64)
    return {
        "h129_ops": int(len(ops)),
        "h129_removed_cells": int(np.isclose(factors, 0.0).sum()),
        "h129_damped_cells": int(((factors > 0.0) & (factors < 1.0)).sum()),
        "h129_inverted_cells": int((factors < 0.0).sum()),
        "h129_op_targets": ";".join(f"{k}:{v}" for k, v in ops["target"].value_counts().to_dict().items()),
        "h129_mean_toxic_rank": float(ops["h129_toxic_rank"].mean()),
        "h129_mean_op_score": float(ops["h129_op_score"].mean()),
    }


def run() -> None:
    cleanup_previous_outputs()
    pool, _public, sample, base_prob, cell, h098_fit, route_fit, basis_fit_df, basis_fit_moves, bad_axes, bad_moves, good_moves, axes, fit, model_scores, props = h118mod.prepare_context()
    scored = h123mod.build_scored_pool(pool, base_prob, fit, bad_axes, bad_moves, good_moves, axes, props)
    catalog = add_toxicity_scores(build_catalog(scored))
    h122_keys = load_h122_core_keys()
    h127_keys = load_h127_keys()
    known = known_hashes(sample)
    previous = {
        "h128": load_move("h128", sample, base_prob).reshape(-1),
        "h127": load_move("h127", sample, base_prob).reshape(-1),
        "h126": load_move("h126", sample, base_prob).reshape(-1),
        "h125": load_move("h125", sample, base_prob).reshape(-1),
        "h124": load_move("h124", sample, base_prob).reshape(-1),
        "h122": load_move("h122", sample, base_prob).reshape(-1),
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
        start_eval = evaluate_matrix(start_move, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
        work = active_frame(catalog, start_move, spec, h122_keys, h127_keys)
        start_rows.append({"start_name": spec.start_name, "spec_name": spec.name, **start_eval, "active_cells": int((np.abs(start_move) > 1.0e-12).sum()), "eligible_cells": int(len(work))})
        audit_rows.append({"spec_name": spec.name, "start_name": spec.start_name, "condition": spec.condition, "eligible_cells": int(len(work)), "eligible_mean_toxic_rank": float(work["h129_toxic_rank"].mean()) if not work.empty else 0.0})
        if work.empty:
            continue
        move_mat, ops, before, final = greedy_erase(
            start_move,
            work,
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
        if ops.empty:
            continue
        component_gain = (
            260.0 * (-(final["h098"] - before["h098"]))
            + 190.0 * (-(final["curv_marg"] - before["curv_marg"]))
            + 0.24 * (final["margin"] - before["margin"])
            + 0.16 * (-(final["h088"] - before["h088"]))
            - 95.0 * max(final["route"] - before["route"], 0.0)
            + 160.0 * max(-(final["route"] - before["route"]), 0.0)
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
        candidate_id = safe_id(f"h129_{spec.name}_{hash_id}", 128)
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
            "h129_start_field": spec.start_name,
            "h129_start_cells": int((np.abs(start_move) > 1.0e-12).sum()),
            "h129_component_gain": float(component_gain),
            "h129_delta_start_route": float(final["route"] - before["route"]),
            "h129_delta_start_h098": float(final["h098"] - before["h098"]),
            "h129_delta_start_h088": float(final["h088"] - before["h088"]),
            "h129_delta_start_margin": float(final["margin"] - before["margin"]),
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
        metrics["h129_worldview"] = spec.worldview
        metrics["h129_fit_feature_set"] = fit.feature_set
        metrics["h129_fit_alpha"] = fit.alpha
        metrics["h129_fit_score"] = fit.score
        metrics["h129_score"] = (
            300.0 * (-float(metrics["model_pred_delta_vs_h057"]))
            + 250.0 * (-float(metrics["route_basis_pred_delta_vs_h057"]))
            + 120.0 * (-float(metrics["h118_curv_marginal_vs_zero"]))
            + 0.25 * float(metrics["h102_cum_good_bad_margin"])
            + 0.14 * max(-float(metrics["h102_cum_h088_axis_cos"]), 0.0)
            + 0.13 * float(metrics["selected_mean_residual_safety"])
            + 0.12 * float(metrics["selected_mean_residual_gap"])
            - 0.15 * float(metrics["selected_mean_residual_toxicity"])
            + 1.2 * max(component_gain, 0.0)
            + 0.002 * float(op_diag["h129_mean_toxic_rank"])
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
    catalog.to_csv(OUT / "h129_toxicity_catalog.csv", index=False)
    audit.to_csv(OUT / "h129_audit.csv", index=False)
    starts.to_csv(OUT / "h129_start_metrics.csv", index=False)
    model_scores.to_csv(OUT / "h129_curvature_model_scores.csv", index=False)
    if candidates.empty:
        report = f"""# H129 Toxic-Action Eraser HS-JEPA

No candidate was promoted.

Audit:

{md_table(audit, 20)}

Start metrics:

{md_table(starts, 20)}
"""
        (OUT / "h129_report.md").write_text(report, encoding="utf-8")
        print("H129 promoted no candidate")
        print(audit.to_string(index=False))
        return

    candidates = candidates.sort_values(["h129_score", "h129_component_gain", "model_pred_delta_vs_h057"], ascending=[False, False, True]).reset_index(drop=True)
    selected = candidates.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"submission_h129_toxiceraser_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)
    decision = {
        "decision": "promote_h129_toxic_action_eraser",
        "selected_candidate_id": selected["candidate_id"],
        "root_uploadsafe_path": str(root_path),
        "worldview": selected["h129_worldview"],
        **selected,
        **{f"root_{key}": value for key, value in validation.items()},
    }
    candidates.to_csv(OUT / "h129_candidates.csv", index=False)
    pd.concat(selected_frames, ignore_index=True).to_csv(OUT / "h129_selected_cells.csv", index=False)
    pd.concat(op_frames, ignore_index=True).to_csv(OUT / "h129_operations.csv", index=False)
    pd.DataFrame([decision]).to_csv(OUT / "h129_decision.csv", index=False)

    cols = [
        "candidate_id",
        "spec_name",
        "h129_start_field",
        "selected_cells",
        "changed_rows_vs_h057",
        "Q1_changed_vs_h057",
        "Q2_changed_vs_h057",
        "Q3_changed_vs_h057",
        "S1_changed_vs_h057",
        "S2_changed_vs_h057",
        "S3_changed_vs_h057",
        "S4_changed_vs_h057",
        "h129_ops",
        "h129_removed_cells",
        "h129_damped_cells",
        "h129_inverted_cells",
        "h129_op_targets",
        "h129_delta_start_route",
        "h129_delta_start_h098",
        "h129_delta_start_h088",
        "h129_delta_start_margin",
        "model_pred_delta_vs_h057",
        "route_basis_pred_delta_vs_h057",
        "h102_cum_h088_axis_cos",
        "h102_cum_good_bad_margin",
        "h129_component_gain",
        "h129_score",
        "file",
    ]
    report = f"""# H129 Toxic-Action Eraser HS-JEPA

Question: is the next public/private equation an additive value field, or a
toxicity field that deletes/damps unsafe row-target actions after assignment?

Audit:

{md_table(audit, 20)}

Start metrics:

{md_table(starts, 20)}

Candidates:

{md_table(candidates[cols], 20)}

Decision:

{md_table(pd.DataFrame([decision]), 1)}

Interpretation rule:

- If H129 improves, HS-JEPA should model a public-punished toxicity field after
  row-target assignment; action support and action safety are separate solvers.
- If H128 improves more, conflict-value regeneration is more important than
  erasing assigned actions.
- If H127/H126 improve more, the eraser is over-pruning and the known sparse
  assignment field should stay terminal.
"""
    (OUT / "h129_report.md").write_text(report, encoding="utf-8")
    print("H129 selected candidate")
    print(candidates[cols].head(10).to_string(index=False))
    print("\nDecision")
    print(pd.DataFrame([decision])[["decision", "selected_candidate_id", "root_uploadsafe_path", "root_upload_safe"]].to_string(index=False))


if __name__ == "__main__":
    run()
