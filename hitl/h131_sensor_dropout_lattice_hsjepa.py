#!/usr/bin/env python3
"""H131: sensor-dropout row-target lattice HS-JEPA.

H130 promoted a row-target lattice solver, but it leaned heavily on the H088
negative action sensor and the good-bad margin.  H131 treats that as a failure
mode to test: an action is promoted only if it survives several stress views in
which one sensor family is weakened.

This is not another local score tweak.  It asks whether HS-JEPA's assignment
decoder can distinguish safe row-target action from H088-shaped toxicity
shortcut.
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
OUT = HITL / "h131_sensor_dropout_lattice_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H130_PATH = HITL / "h130_rowtarget_lattice_solver_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h130mod_h131", H130_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H130_PATH}")
h130mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h130mod
SPEC.loader.exec_module(h130mod)

h129mod = h130mod.h129mod
h126mod = h130mod.h126mod
h123mod = h130mod.h123mod
h118mod = h130mod.h118mod
h102mod = h130mod.h102mod
h085mod = h130mod.h085mod

TARGETS = h130mod.TARGETS
TOL = h130mod.TOL


@dataclass(frozen=True)
class H131Spec:
    name: str
    group: str
    start_name: str
    support: str
    max_steps: int
    min_step_score: float
    min_dropout_pass: int
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
    min_add_evidence: float
    min_erase_evidence: float
    max_add_bad_same: float
    max_add_shortcut: float
    allow_add: bool
    allow_erase: bool
    worldview: str


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def safe_id(text: str, limit: int = 132) -> str:
    return h085mod.safe_id(text, limit=limit)


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return h085mod.md_table(frame, n=n)


def rank01(values: np.ndarray, high: bool = True) -> np.ndarray:
    return h085mod.rank01(np.asarray(values, dtype=np.float64), high=high)


def numeric(frame: pd.DataFrame, col: str, default: float = 0.0) -> np.ndarray:
    if col not in frame.columns:
        return np.full(len(frame), default, dtype=np.float64)
    return pd.to_numeric(frame[col], errors="coerce").fillna(default).to_numpy(dtype=np.float64)


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h131_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h131_dropout_*.csv"):
        path.unlink()


def root_submission_paths() -> dict[str, Path]:
    paths = h130mod.root_submission_paths()
    paths["h130"] = ROOT / "submission_h130_lattice_69da8d10_uploadsafe.csv"
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


def selected_keys_from_h130() -> set[tuple[int, int]]:
    path = HITL / "h130_rowtarget_lattice_solver_hsjepa" / "h130_selected_cells.csv"
    if not path.exists():
        return set()
    frame = pd.read_csv(path)
    frame = frame[frame["candidate_id"].astype(str).eq("h130_h122_full_lattice_69da8d10")]
    return set(zip(frame["row"].astype(int), frame["target_index"].astype(int)))


def candidate_specs() -> list[H131Spec]:
    common = dict(
        max_rows=32,
        max_per_subject=26,
        max_per_target=16,
        amp=1.0,
        cap=0.30,
        pool_top=300,
        min_score=0.0,
        min_residual_gap=-0.30,
        max_residual_toxicity=0.95,
        min_residual_safety=0.0,
        max_bad_weighted_pos=0.0006,
        max_bad_max_pos=0.0022,
        max_curv_marg=0.000060,
        max_h088_hard_cosine=-0.018,
    )
    return [
        H131Spec(
            name="h122_dropout_robust_lattice",
            group="dropout_full_lattice",
            start_name="h122",
            support="all_known",
            max_steps=12,
            min_step_score=0.00022,
            min_dropout_pass=3,
            max_cells=34,
            max_h088_cos=-0.052,
            min_good_margin=0.126,
            route_pred_cap=-0.000600,
            h098_pred_cap=-0.000018,
            min_component_gain=0.00022,
            min_add_evidence=0.46,
            min_erase_evidence=0.43,
            max_add_bad_same=0.58,
            max_add_shortcut=0.70,
            allow_add=True,
            allow_erase=True,
            worldview="safe lattice states survive H088/margin dropout plus residual/forbidden/bad-axis stress",
            **common,
        ),
        H131Spec(
            name="h129_dropout_value_probe",
            group="core_erase_plus_safe_value",
            start_name="h129",
            support="core_plus_value",
            max_steps=8,
            min_step_score=0.00020,
            min_dropout_pass=3,
            max_cells=30,
            max_h088_cos=-0.050,
            min_good_margin=0.130,
            route_pred_cap=-0.000605,
            h098_pred_cap=-0.000022,
            min_component_gain=0.00018,
            min_add_evidence=0.44,
            min_erase_evidence=0.46,
            max_add_bad_same=0.55,
            max_add_shortcut=0.66,
            allow_add=True,
            allow_erase=True,
            worldview="H129 core eraser is kept, but only dropout-robust H128/H127 value cells may be reintroduced",
            **common,
        ),
        H131Spec(
            name="h130_deoverfit_dropout",
            group="h130_sensor_deoverfit",
            start_name="h130",
            support="h130_active",
            max_steps=8,
            min_step_score=0.00016,
            min_dropout_pass=3,
            max_cells=28,
            max_h088_cos=-0.060,
            min_good_margin=0.160,
            route_pred_cap=-0.000625,
            h098_pred_cap=-0.000018,
            min_component_gain=0.00010,
            min_add_evidence=0.50,
            min_erase_evidence=0.38,
            max_add_bad_same=0.50,
            max_add_shortcut=0.62,
            allow_add=False,
            allow_erase=True,
            worldview="if H130 overfit H088/margin, a dropout decoder should delete or damp its weak sensor-only cells",
            **common,
        ),
        H131Spec(
            name="h122_no_h088_route_lattice",
            group="no_h088_route_lattice",
            start_name="h122",
            support="all_known",
            max_steps=10,
            min_step_score=0.00019,
            min_dropout_pass=2,
            max_cells=32,
            max_h088_cos=-0.045,
            min_good_margin=0.120,
            route_pred_cap=-0.000602,
            h098_pred_cap=-0.000019,
            min_component_gain=0.00016,
            min_add_evidence=0.50,
            min_erase_evidence=0.48,
            max_add_bad_same=0.50,
            max_add_shortcut=0.60,
            allow_add=True,
            allow_erase=True,
            worldview="the lattice is real only if a route/H098/forbidden decoder can rediscover it without trusting H088 as the main reward",
            **common,
        ),
    ]


def build_catalog(scored: pd.DataFrame) -> pd.DataFrame:
    out = h130mod.build_catalog(scored).copy()
    h130_keys = selected_keys_from_h130()
    out["h131_in_h130"] = [
        1.0 if (int(row), int(tidx)) in h130_keys else 0.0
        for row, tidx in zip(out["row"].astype(int), out["target_index"].astype(int))
    ]

    same_cols = [
        "h080_bad_same_rank",
        "h112_same_bad_residual",
        "h112_same_e216",
        "h112_same_h010",
        "h112_same_lejepa",
        "h112_same_ordinal",
        "h117_forbidden_pressure",
        "latent_shortcut_energy",
        "bad_pressure_rank",
    ]
    opp_cols = [
        "h080_bad_opp_rank",
        "h112_opp_bad_residual",
        "h112_opp_e216",
        "h112_opp_h010",
        "h112_opp_lejepa",
        "h112_opp_ordinal",
        "h112_antidote_score",
        "h057_h088_anti_conflict",
    ]
    health_cols = [
        "h112_residual_safety",
        "h112_residual_gap",
        "private_safe_score",
        "h095_safe_cell_score",
        "h068_cell_health",
        "h110_benefit_toxicity_gap",
    ]
    source_cols = [
        "source_family_count",
        "source_consensus",
        "source_weight",
        "h108_family_count",
        "h108_vote_consensus",
        "h131_in_h130",
    ]

    same_parts = [rank01(numeric(out, col), high=True) for col in same_cols]
    opp_parts = [rank01(numeric(out, col), high=True) for col in opp_cols]
    health_parts = [rank01(numeric(out, col), high=True) for col in health_cols]
    source_parts = []
    for col in source_cols:
        arr = numeric(out, col)
        if col.endswith("count"):
            arr = np.clip(arr / 4.0, 0.0, 1.0)
        source_parts.append(rank01(arr, high=True))

    out["h131_bad_same_pressure"] = np.mean(np.vstack(same_parts), axis=0)
    out["h131_antidote_pressure"] = np.mean(np.vstack(opp_parts), axis=0)
    out["h131_residual_health"] = np.mean(np.vstack(health_parts), axis=0)
    out["h131_source_strength"] = np.mean(np.vstack(source_parts), axis=0)
    out["h131_shortcut_pressure"] = np.mean(
        np.vstack(
            [
                rank01(numeric(out, "latent_shortcut_energy"), high=True),
                rank01(numeric(out, "bad_pressure_rank"), high=True),
                rank01(numeric(out, "h088_toxicity"), high=True),
                numeric(out, "h057_h088_same_conflict"),
                rank01(numeric(out, "h117_forbidden_pressure"), high=True),
            ]
        ),
        axis=0,
    )
    toxic_rank = rank01(numeric(out, "h129_toxicity_field"), high=True)
    out["h131_erase_evidence"] = np.clip(
        0.36 * out["h131_bad_same_pressure"].to_numpy(dtype=np.float64)
        + 0.26 * out["h131_shortcut_pressure"].to_numpy(dtype=np.float64)
        + 0.18 * toxic_rank
        + 0.12 * rank01(numeric(out, "h112_residual_toxicity"), high=True)
        + 0.08 * numeric(out, "h057_h088_same_conflict")
        - 0.20 * out["h131_residual_health"].to_numpy(dtype=np.float64),
        0.0,
        1.0,
    )
    out["h131_add_evidence"] = np.clip(
        0.32 * out["h131_residual_health"].to_numpy(dtype=np.float64)
        + 0.27 * out["h131_antidote_pressure"].to_numpy(dtype=np.float64)
        + 0.17 * out["h131_source_strength"].to_numpy(dtype=np.float64)
        + 0.10 * numeric(out, "h057_h088_anti_conflict")
        + 0.06 * numeric(out, "h057_h088_same_conflict")
        - 0.27 * out["h131_bad_same_pressure"].to_numpy(dtype=np.float64)
        - 0.20 * out["h131_shortcut_pressure"].to_numpy(dtype=np.float64),
        0.0,
        1.0,
    )
    out["h131_dropout_priority"] = (
        0.35 * np.maximum(out["h131_add_evidence"], out["h131_erase_evidence"])
        + 0.20 * out["h131_source_strength"]
        + 0.18 * out["h131_residual_health"]
        + 0.14 * out["h131_antidote_pressure"]
        + 0.08 * out["h131_in_h130"]
        + 0.05 * numeric(out, "h057_h088_anti_conflict")
    )
    return out


def support_keys(spec: H131Spec, moves: dict[str, np.ndarray]) -> set[tuple[int, int]]:
    if spec.support == "h130_active":
        return nonzero_keys(moves["h130"])
    proxy = h130mod.H130Spec(
        name=spec.name,
        group=spec.group,
        start_name=spec.start_name,
        support="all_known" if spec.support == "all_known" else "core_plus_value",
        max_steps=spec.max_steps,
        min_step_score=spec.min_step_score,
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
        worldview=spec.worldview,
    )
    return h130mod.support_keys(proxy, moves)


def option_values(row: int, tidx: int, moves: dict[str, np.ndarray]) -> list[tuple[str, float]]:
    vals: list[tuple[str, float]] = [("off", 0.0)]
    for name in ["h122", "h124", "h126", "h127", "h128", "h129", "h130"]:
        val = float(moves[name][row, tidx])
        if abs(val) > 1.0e-12:
            vals.append((name, val))
            vals.append((f"{name}_half", 0.5 * val))
            if name in {"h122", "h128", "h130"}:
                vals.append((f"{name}_075", 0.75 * val))
    out: list[tuple[str, float]] = []
    seen: set[float] = set()
    for label, val in vals:
        key = round(float(val), 12)
        if key in seen:
            continue
        seen.add(key)
        out.append((label, float(val)))
    return out


def lattice_frame(catalog: pd.DataFrame, keys: set[tuple[int, int]]) -> pd.DataFrame:
    frame = catalog[
        [((int(row), int(tidx)) in keys) for row, tidx in zip(catalog["row"], catalog["target_index"])]
    ].copy()
    if frame.empty:
        return frame
    return frame.sort_values(["h131_dropout_priority", "h131_source_strength"], ascending=[False, False]).reset_index(drop=True)


def evaluate_matrix(move_mat, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes):
    return h130mod.evaluate_matrix(
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


def check_constraints(move_mat: np.ndarray, evald: dict[str, float], spec: H131Spec) -> bool:
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


def action_kind(old: float, new: float) -> str:
    old_abs = abs(old)
    new_abs = abs(new)
    if new_abs < old_abs - 1.0e-12:
        return "erase"
    if new_abs > old_abs + 1.0e-12:
        return "add"
    return "switch"


def cell_gate(rec: dict[str, object], old: float, new: float, spec: H131Spec) -> tuple[bool, dict[str, float | str]]:
    kind = action_kind(old, new)
    erase_e = float(rec.get("h131_erase_evidence", 0.0))
    add_e = float(rec.get("h131_add_evidence", 0.0))
    bad_same = float(rec.get("h131_bad_same_pressure", 0.0))
    shortcut = float(rec.get("h131_shortcut_pressure", 0.0))
    health = float(rec.get("h131_residual_health", 0.0))
    antidote = float(rec.get("h131_antidote_pressure", 0.0))
    forbidden = float(rec.get("h117_forbidden_pressure", 0.0))
    target = str(rec.get("target", ""))

    if kind == "add":
        votes = int(add_e >= spec.min_add_evidence)
        votes += int(bad_same <= spec.max_add_bad_same)
        votes += int(shortcut <= spec.max_add_shortcut)
        votes += int(forbidden <= 0.05)
        votes += int(health >= 0.45)
        votes += int(antidote >= 0.45)
        ok = (
            spec.allow_add
            and target != "Q2"
            and add_e >= spec.min_add_evidence
            and bad_same <= spec.max_add_bad_same
            and shortcut <= spec.max_add_shortcut
            and votes >= 4
        )
    elif kind == "erase":
        votes = int(erase_e >= spec.min_erase_evidence)
        votes += int(bad_same >= 0.52 or shortcut >= 0.62)
        votes += int(forbidden <= 0.20)
        votes += int(health <= 0.72 or bad_same >= 0.70)
        votes += int(float(rec.get("h112_residual_toxicity", 0.0)) >= 0.40 or shortcut >= 0.62)
        protected = health > 0.78 and bad_same < 0.55 and shortcut < 0.55
        ok = spec.allow_erase and erase_e >= spec.min_erase_evidence and votes >= 3 and not protected
    else:
        votes = 0
        ok = False

    return ok, {
        "h131_action_kind": kind,
        "h131_cell_votes": float(votes),
        "h131_add_evidence": add_e,
        "h131_erase_evidence": erase_e,
        "h131_bad_same_pressure": bad_same,
        "h131_shortcut_pressure": shortcut,
        "h131_residual_health": health,
        "h131_antidote_pressure": antidote,
        "h131_forbidden_pressure": forbidden,
    }


def dropout_score(after: dict[str, float], before: dict[str, float], gate: dict[str, float | str]) -> tuple[float, dict[str, float]]:
    d_route = after["route"] - before["route"]
    d_h098 = after["h098"] - before["h098"]
    d_curv = after["curv_marg"] - before["curv_marg"]
    d_badw = after["badw"] - before["badw"]
    d_badmax = after["badmax"] - before["badmax"]
    d_h088 = after["h088"] - before["h088"]
    d_margin = after["margin"] - before["margin"]
    kind = str(gate["h131_action_kind"])
    evidence = float(gate["h131_add_evidence"] if kind == "add" else gate["h131_erase_evidence"])
    cell_bonus = 0.00024 * evidence + 0.000035 * float(gate["h131_cell_votes"])

    route_view = (
        210.0 * (-d_h098)
        + 165.0 * max(-d_route, 0.0)
        - 80.0 * max(d_route, 0.0)
        + 135.0 * (-d_curv)
        + cell_bonus
    )
    no_h088_view = (
        190.0 * (-d_h098)
        + 150.0 * max(-d_route, 0.0)
        - 80.0 * max(d_route, 0.0)
        + 120.0 * (-d_curv)
        - 5.0 * d_badw
        - 3.0 * d_badmax
        + cell_bonus
    )
    no_route_view = (
        150.0 * (-d_curv)
        + 0.12 * d_margin
        + 0.08 * (-d_h088)
        - 5.0 * d_badw
        - 3.0 * d_badmax
        + 0.65 * cell_bonus
    )
    axis_view = (
        0.07 * (-d_h088)
        + 0.08 * d_margin
        - 7.0 * d_badw
        - 4.0 * d_badmax
        + 0.55 * cell_bonus
    )
    scores = {
        "h131_route_view_score": float(route_view),
        "h131_no_h088_view_score": float(no_h088_view),
        "h131_no_route_view_score": float(no_route_view),
        "h131_axis_view_score": float(axis_view),
    }
    passed = sum(value > 0.0 for value in scores.values())
    aggregate = 0.30 * route_view + 0.28 * no_h088_view + 0.22 * no_route_view + 0.20 * axis_view
    scores["h131_dropout_passes"] = float(passed)
    scores["h131_step_score"] = float(aggregate)
    return float(aggregate), scores


def coordinate_solve(start: np.ndarray, lattice: pd.DataFrame, spec: H131Spec, moves: dict[str, np.ndarray], basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes) -> tuple[np.ndarray, pd.DataFrame, dict[str, float], dict[str, float]]:
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
            for state, val in option_values(row, tidx, moves):
                if abs(val - old) <= 1.0e-12:
                    continue
                ok, gate = cell_gate(rec, old, val, spec)
                if not ok:
                    continue
                tmp = move_mat.copy()
                tmp[row, tidx] = val
                after = evaluate_matrix(tmp, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
                if not check_constraints(tmp, after, spec):
                    continue
                score, view_scores = dropout_score(after, before, gate)
                if view_scores["h131_dropout_passes"] < spec.min_dropout_pass:
                    continue
                if best is None or score > best["h131_step_score"]:
                    best = {
                        "step": step + 1,
                        "row": row,
                        "target_index": tidx,
                        "target": str(rec["target"]),
                        "subject_id": str(rec.get("subject_id", "")),
                        "sleep_date": str(rec.get("sleep_date", "")),
                        "old_move": old,
                        "new_move": float(val),
                        "state": state,
                        **gate,
                        **view_scores,
                        **{f"after_{key2}": value for key2, value in after.items()},
                        **{f"delta_{key2}": after[key2] - before[key2] for key2 in after},
                    }
        if best is None or float(best["h131_step_score"]) < spec.min_step_score:
            break
        move_mat[int(best["row"]), int(best["target_index"])] = float(best["new_move"])
        touched.add((int(best["row"]), int(best["target_index"])))
        operations.append(best)
    final_eval = evaluate_matrix(move_mat, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
    return move_mat, pd.DataFrame(operations), start_eval, final_eval


def make_selected(catalog: pd.DataFrame, move_mat: np.ndarray) -> pd.DataFrame:
    selected = h130mod.make_selected(catalog, move_mat)
    if selected.empty:
        return selected
    selected["h131_actual_move"] = selected["h130_actual_move"]
    selected["h112_move"] = selected["h131_actual_move"].to_numpy(dtype=np.float64)
    return selected


def operation_summary(ops: pd.DataFrame) -> dict[str, object]:
    if ops.empty:
        return {
            "h131_ops": 0,
            "h131_off_ops": 0,
            "h131_damp_ops": 0,
            "h131_add_ops": 0,
            "h131_op_targets": "",
            "h131_mean_dropout_passes": 0.0,
            "h131_mean_step_score": 0.0,
            "h131_mean_add_evidence": 0.0,
            "h131_mean_erase_evidence": 0.0,
        }
    old_abs = np.abs(ops["old_move"].to_numpy(dtype=np.float64))
    new_abs = np.abs(ops["new_move"].to_numpy(dtype=np.float64))
    return {
        "h131_ops": int(len(ops)),
        "h131_off_ops": int(np.isclose(new_abs, 0.0).sum()),
        "h131_damp_ops": int(((new_abs > 1.0e-12) & (new_abs < old_abs - 1.0e-12)).sum()),
        "h131_add_ops": int((new_abs > old_abs + 1.0e-12).sum()),
        "h131_op_targets": ";".join(f"{k}:{v}" for k, v in ops["target"].value_counts().to_dict().items()),
        "h131_mean_dropout_passes": float(ops["h131_dropout_passes"].mean()),
        "h131_mean_step_score": float(ops["h131_step_score"].mean()),
        "h131_mean_add_evidence": float(ops["h131_add_evidence"].mean()),
        "h131_mean_erase_evidence": float(ops["h131_erase_evidence"].mean()),
    }


def previous_moves(sample: pd.DataFrame, base_prob: np.ndarray, moves: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    out = {
        name: moves[name].reshape(-1)
        for name in ["h130", "h129", "h128", "h127", "h126", "h124", "h122"]
    }
    out["h088"] = load_move("h088", sample, base_prob).reshape(-1)
    out["h018"] = load_move("h018", sample, base_prob).reshape(-1)
    return out


def component_gain(final: dict[str, float], before: dict[str, float]) -> float:
    return (
        230.0 * (-(final["h098"] - before["h098"]))
        + 155.0 * (-(final["curv_marg"] - before["curv_marg"]))
        + 145.0 * max(-(final["route"] - before["route"]), 0.0)
        - 75.0 * max(final["route"] - before["route"], 0.0)
        + 0.13 * (final["margin"] - before["margin"])
        + 0.07 * (-(final["h088"] - before["h088"]))
    )


def run() -> None:
    cleanup_previous_outputs()
    pool, _public, sample, base_prob, cell, h098_fit, route_fit, basis_fit_df, basis_fit_moves, bad_axes, bad_moves, good_moves, axes, fit, model_scores, props = h118mod.prepare_context()
    scored = h123mod.build_scored_pool(pool, base_prob, fit, bad_axes, bad_moves, good_moves, axes, props)
    catalog = build_catalog(scored)
    moves = {name: load_move(name, sample, base_prob) for name in ["h122", "h124", "h126", "h127", "h128", "h129", "h130"]}
    known = known_hashes(sample)
    previous = previous_moves(sample, base_prob, moves)

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
        audit = {
            "spec_name": spec.name,
            "start_name": spec.start_name,
            "support": spec.support,
            "lattice_cells": int(len(lattice)),
            "mean_add_evidence": float(lattice["h131_add_evidence"].mean()) if not lattice.empty else 0.0,
            "mean_erase_evidence": float(lattice["h131_erase_evidence"].mean()) if not lattice.empty else 0.0,
        }
        audit_rows.append(audit)
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
        candidate_id = safe_id(f"h131_{spec.name}_{hash_id}", 128)
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
            "h131_start_field": spec.start_name,
            "h131_start_cells": int((np.abs(start_move) > 1.0e-12).sum()),
            "h131_lattice_cells": int(len(lattice)),
            "h131_component_gain": float(gain),
            "h131_delta_start_route": float(final["route"] - before["route"]),
            "h131_delta_start_h098": float(final["h098"] - before["h098"]),
            "h131_delta_start_h088": float(final["h088"] - before["h088"]),
            "h131_delta_start_margin": float(final["margin"] - before["margin"]),
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
        metrics["h131_worldview"] = spec.worldview
        metrics["h131_fit_feature_set"] = fit.feature_set
        metrics["h131_fit_alpha"] = fit.alpha
        metrics["h131_fit_score"] = fit.score
        metrics["h131_score"] = (
            305.0 * (-float(metrics["model_pred_delta_vs_h057"]))
            + 250.0 * (-float(metrics["route_basis_pred_delta_vs_h057"]))
            + 115.0 * (-float(metrics["h118_curv_marginal_vs_zero"]))
            + 0.19 * float(metrics["h102_cum_good_bad_margin"])
            + 0.07 * max(-float(metrics["h102_cum_h088_axis_cos"]), 0.0)
            + 0.13 * float(metrics["selected_mean_residual_safety"])
            + 0.13 * float(metrics["selected_mean_residual_gap"])
            - 0.18 * float(metrics["selected_mean_residual_toxicity"])
            + 1.4 * max(gain, 0.0)
            + 0.018 * float(op_diag["h131_mean_dropout_passes"])
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
    catalog.to_csv(OUT / "h131_catalog.csv", index=False)
    audit.to_csv(OUT / "h131_audit.csv", index=False)
    starts.to_csv(OUT / "h131_start_metrics.csv", index=False)
    model_scores.to_csv(OUT / "h131_curvature_model_scores.csv", index=False)
    if candidates.empty:
        report = f"""# H131 Sensor-Dropout Row-Target Lattice HS-JEPA

No candidate was promoted.

Audit:

{md_table(audit, 20)}

Start metrics:

{md_table(starts, 20)}
"""
        (OUT / "h131_report.md").write_text(report, encoding="utf-8")
        print("H131 promoted no candidate")
        print(audit.to_string(index=False))
        return

    candidates = candidates.sort_values(["h131_score", "h131_component_gain", "model_pred_delta_vs_h057"], ascending=[False, False, True]).reset_index(drop=True)
    selected = candidates.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"submission_h131_dropout_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)
    decision = {
        "decision": "promote_h131_sensor_dropout_lattice",
        "selected_candidate_id": selected["candidate_id"],
        "root_uploadsafe_path": str(root_path.resolve()),
        "worldview": selected["h131_worldview"],
        **selected,
        **{f"root_{key}": value for key, value in validation.items()},
    }
    candidates.to_csv(OUT / "h131_candidates.csv", index=False)
    pd.concat(selected_frames, ignore_index=True).to_csv(OUT / "h131_selected_cells.csv", index=False)
    pd.concat(op_frames, ignore_index=True).to_csv(OUT / "h131_operations.csv", index=False)
    pd.DataFrame([decision]).to_csv(OUT / "h131_decision.csv", index=False)

    cols = [
        "candidate_id",
        "spec_name",
        "h131_start_field",
        "selected_cells",
        "changed_rows_vs_h057",
        "Q1_changed_vs_h057",
        "Q2_changed_vs_h057",
        "Q3_changed_vs_h057",
        "S1_changed_vs_h057",
        "S2_changed_vs_h057",
        "S3_changed_vs_h057",
        "S4_changed_vs_h057",
        "h131_ops",
        "h131_off_ops",
        "h131_damp_ops",
        "h131_add_ops",
        "h131_op_targets",
        "h131_mean_dropout_passes",
        "h131_delta_start_route",
        "h131_delta_start_h098",
        "h131_delta_start_h088",
        "h131_delta_start_margin",
        "model_pred_delta_vs_h057",
        "route_basis_pred_delta_vs_h057",
        "h102_cum_h088_axis_cos",
        "h102_cum_good_bad_margin",
        "h131_component_gain",
        "h131_score",
        "file",
    ]
    report = f"""# H131 Sensor-Dropout Row-Target Lattice HS-JEPA

Question: is H130's row-target lattice a real public/private assignment
equation, or a shortcut that overfits H088 and margin sensors?

Audit:

{md_table(audit, 20)}

Start metrics:

{md_table(starts, 20)}

Candidates:

{md_table(candidates[cols], 20)}

Decision:

{md_table(pd.DataFrame([decision]), 1)}

Interpretation rule:

- If H131 improves publicly, HS-JEPA should include a sensor-dropout action
  decoder: an action is valid only if route, residual, forbidden, and bad-axis
  views agree without leaning on H088 alone.
- If H130/H129 beats H131, the stricter dropout gate discarded real
  public-specific information; H088/margin are not just shortcuts.
- If H131 is much worse, the public-private equation is not yet captured by
  local row-target lattice states and needs a larger assignment solver.
"""
    (OUT / "h131_report.md").write_text(report, encoding="utf-8")
    print("H131 selected candidate")
    print(candidates[cols].head(10).to_string(index=False))
    print("\nDecision")
    print(pd.DataFrame([decision])[["decision", "selected_candidate_id", "root_uploadsafe_path", "root_upload_safe"]].to_string(index=False))


if __name__ == "__main__":
    run()
