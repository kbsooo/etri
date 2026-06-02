#!/usr/bin/env python3
"""H127: residual basis discovery HS-JEPA.

H126 showed coefficient solving inside the H122-H125 basis is too narrow.  H127
searches outside that active support for a new public/private-safe action basis.
It starts from the H126 soft-closure field, excludes the H122-pruned toxic
sector, and greedily adds only residual cells that improve the route/H098
equation while preserving H088/bad-axis safety.
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
OUT = HITL / "h127_residual_basis_discovery_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H126_PATH = HITL / "h126_component_coefficient_equation_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h126mod", H126_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H126_PATH}")
h126mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h126mod
SPEC.loader.exec_module(h126mod)

h125mod = h126mod.h125mod
h123mod = h126mod.h123mod
h122mod = h126mod.h122mod
h118mod = h126mod.h118mod
h115mod = h126mod.h115mod
h102mod = h126mod.h102mod
h085mod = h126mod.h085mod

TARGETS = h126mod.TARGETS
TOL = h126mod.TOL


@dataclass(frozen=True)
class H127Spec:
    name: str
    group: str
    add_condition: str
    add_amp: float
    add_cap: float
    max_add: int
    min_add_score: float
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


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h127_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h127_residbasis_*.csv"):
        path.unlink()


def nonzero_keys(move: np.ndarray) -> set[tuple[int, int]]:
    return h126mod.nonzero_keys(move)


def evaluate_matrix(move_mat, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes):
    return h126mod.evaluate_matrix(
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


def candidate_specs() -> list[H127Spec]:
    common = dict(
        max_cells=38,
        max_rows=32,
        max_per_subject=20,
        max_per_target=20,
        amp=1.0,
        cap=0.25,
        pool_top=320,
        min_score=0.0,
        min_residual_gap=0.20,
        max_residual_toxicity=0.50,
        min_residual_safety=0.58,
        max_bad_weighted_pos=0.0005,
        max_bad_max_pos=0.0020,
        max_curv_marg=0.000055,
        max_h088_hard_cosine=-0.030,
        min_component_gain=0.00020,
    )
    return [
        H127Spec(
            name="objective_residual_newbasis",
            group="residual_objective",
            add_condition="objective",
            add_amp=0.28,
            add_cap=0.09,
            max_add=8,
            min_add_score=0.00080,
            max_h088_cos=-0.048,
            min_good_margin=0.145,
            route_pred_cap=-0.000700,
            h098_pred_cap=-0.000030,
            worldview="a missing objective S/Q3 residual basis exists outside the H122-H126 support, but only if it improves both route and toxicity stress",
            **common,
        ),
        H127Spec(
            name="subjective_q_residual_newbasis",
            group="residual_q",
            add_condition="q_subjective",
            add_amp=0.24,
            add_cap=0.08,
            max_add=6,
            min_add_score=0.00060,
            max_h088_cos=-0.045,
            min_good_margin=0.142,
            route_pred_cap=-0.000700,
            h098_pred_cap=-0.000031,
            worldview="Q1/Q3 residual cells represent a subjective human-state basis missing from the objective prune/refill path",
            **common,
        ),
        H127Spec(
            name="anti_h088_residual_newbasis",
            group="residual_antih088",
            add_condition="anti_h088",
            add_amp=0.32,
            add_cap=0.10,
            max_add=8,
            min_add_score=0.00075,
            max_h088_cos=-0.055,
            min_good_margin=0.145,
            route_pred_cap=-0.000700,
            h098_pred_cap=-0.000030,
            worldview="the next safe basis should be outside H126 but explicitly anti-H088 and H057-aligned",
            **common,
        ),
        H127Spec(
            name="null_antidote_residual_newbasis",
            group="residual_antidote",
            add_condition="null_antidote",
            add_amp=0.25,
            add_cap=0.08,
            max_add=7,
            min_add_score=0.00070,
            max_h088_cos=-0.050,
            min_good_margin=0.145,
            route_pred_cap=-0.000700,
            h098_pred_cap=-0.000030,
            worldview="H114/H112 antidote-null cells contain a new safe basis after known toxic components are removed",
            **common,
        ),
        H127Spec(
            name="episode_neighbor_residual_newbasis",
            group="residual_episode",
            add_condition="episode_neighbor",
            add_amp=0.25,
            add_cap=0.08,
            max_add=8,
            min_add_score=0.00055,
            max_h088_cos=-0.045,
            min_good_margin=0.145,
            route_pred_cap=-0.000700,
            h098_pred_cap=-0.000030,
            worldview="safe action basis is an episode-neighbor extension around current rows, not isolated global top cells",
            **common,
        ),
    ]


def load_h126_selected() -> pd.DataFrame:
    decision = pd.read_csv(HITL / "h126_component_coefficient_equation_hsjepa/h126_decision.csv")
    cid = str(decision["selected_candidate_id"].iloc[0])
    selected = pd.read_csv(HITL / "h126_component_coefficient_equation_hsjepa/h126_selected_cells.csv")
    return selected[selected["candidate_id"].astype(str) == cid].copy()


def load_h122_removed() -> pd.DataFrame:
    decision = pd.read_csv(HITL / "h122_action_prune_equation_solver_hsjepa/h122_decision.csv")
    cid = str(decision["selected_candidate_id"].iloc[0])
    removed = pd.read_csv(HITL / "h122_action_prune_equation_solver_hsjepa/h122_removed_cells.csv")
    return removed[removed["candidate_id"].astype(str) == cid].copy()


def annotate_residual_pool(scored: pd.DataFrame, start_move: np.ndarray, removed: pd.DataFrame, h126_rows: set[int]) -> pd.DataFrame:
    active = nonzero_keys(start_move)
    removed_keys = set(zip(removed["row"].astype(int), removed["target_index"].astype(int)))
    work = scored.copy()
    work["row"] = work["row"].astype(int)
    work["target_index"] = work["target_index"].astype(int)
    keep = []
    for row, tidx, target in zip(work["row"], work["target_index"], work["target"].astype(str)):
        key = (int(row), int(tidx))
        keep.append(key not in active and key not in removed_keys and target != "Q2")
    work = work[np.asarray(keep)].copy()
    if work.empty:
        return work

    for col in [
        "h110_benefit_toxicity_gap",
        "h098_frontier_cell_score",
        "h095_safe_cell_score",
        "h112_antidote_score",
        "h085_cell_score",
        "h068_cell_health",
        "h080_bad_opp_rank",
        "h088_toxicity",
        "latent_shortcut_energy",
        "bad_pressure_rank",
        "h117_forbidden_pressure",
    ]:
        if col not in work.columns:
            work[col] = 0.0

    work["h127_near_h126_row"] = [1.0 if int(row) in h126_rows or int(row) - 1 in h126_rows or int(row) + 1 in h126_rows else 0.0 for row in work["row"]]
    work["h127_safe_score"] = (
        0.18 * rank01(work["h123_pool_score"].to_numpy(dtype=np.float64), high=True)
        + 0.16 * rank01(work["h112_residual_safety"].to_numpy(dtype=np.float64), high=True)
        + 0.14 * rank01(work["h112_residual_gap"].to_numpy(dtype=np.float64), high=True)
        + 0.12 * rank01(work["h110_benefit_toxicity_gap"].to_numpy(dtype=np.float64), high=True)
        + 0.10 * rank01(work["h098_frontier_cell_score"].to_numpy(dtype=np.float64), high=True)
        + 0.09 * rank01(work["h095_safe_cell_score"].to_numpy(dtype=np.float64), high=True)
        + 0.08 * rank01(work["h112_antidote_score"].to_numpy(dtype=np.float64), high=True)
        + 0.07 * work["h127_near_h126_row"].to_numpy(dtype=np.float64)
        + 0.06 * rank01(work["h080_bad_opp_rank"].to_numpy(dtype=np.float64), high=True)
        - 0.15 * rank01(work["h112_residual_toxicity"].to_numpy(dtype=np.float64), high=True)
        - 0.12 * rank01(work["latent_shortcut_energy"].to_numpy(dtype=np.float64), high=True)
        - 0.10 * rank01(work["bad_pressure_rank"].to_numpy(dtype=np.float64), high=True)
        - 0.10 * rank01(work["h088_toxicity"].to_numpy(dtype=np.float64), high=True)
        - 0.08 * rank01(work["h117_forbidden_pressure"].to_numpy(dtype=np.float64), high=True)
    )
    work["h127_abs_proposal_move"] = np.abs(work["proposal_move"].to_numpy(dtype=np.float64))
    return work.sort_values(["h127_safe_score", "h112_residual_safety"], ascending=[False, False]).reset_index(drop=True)


def allowed(rec: dict[str, object], spec: H127Spec) -> bool:
    target = str(rec["target"])
    source = str(rec.get("proposal_source", ""))
    if spec.add_condition == "objective":
        return target in {"Q3", "S1", "S2", "S4"}
    if spec.add_condition == "q_subjective":
        return target in {"Q1", "Q3"}
    if spec.add_condition == "anti_h088":
        return bool(float(rec.get("h110_anti_h088", 0.0)) >= 0.5 or float(rec.get("h108_anti_h088", 0.0)) >= 0.5 or float(rec.get("h057_h088_anti_conflict", 0.0)) >= 0.5)
    if spec.add_condition == "null_antidote":
        return "h114" in source or float(rec.get("h112_antidote_score", 0.0)) >= 0.78 or abs(float(rec.get("h114_null_move", 0.0))) > 1.0e-12
    if spec.add_condition == "episode_neighbor":
        return float(rec.get("h127_near_h126_row", 0.0)) >= 0.5
    raise ValueError(spec.add_condition)


def prepare_work(pool: pd.DataFrame, spec: H127Spec) -> pd.DataFrame:
    work = pool.copy()
    keep = [allowed(rec, spec) for rec in work.to_dict("records")]
    work = work[np.asarray(keep)].copy()
    if work.empty:
        return work
    work = work[work["h117_forbidden_same"].to_numpy(dtype=np.float64) <= 1.0e-12].copy()
    work = work[work["h117_forbidden_pressure"].to_numpy(dtype=np.float64) <= 1.0e-12].copy()
    work = work[work["h112_residual_safety"].to_numpy(dtype=np.float64) >= spec.min_residual_safety].copy()
    work = work[work["h112_residual_toxicity"].to_numpy(dtype=np.float64) <= spec.max_residual_toxicity].copy()
    work = work[work["h112_residual_gap"].to_numpy(dtype=np.float64) >= spec.min_residual_gap].copy()
    work = work[work["h127_safe_score"].to_numpy(dtype=np.float64) >= spec.min_score].copy()
    if work.empty:
        return work
    work["h127_move"] = np.clip(work["proposal_move"].to_numpy(dtype=np.float64) * spec.add_amp, -spec.add_cap, spec.add_cap)
    work = work[np.abs(work["h127_move"].to_numpy(dtype=np.float64)) > 1.0e-8].copy()
    work = work.sort_values(["h127_safe_score", "h112_residual_safety"], ascending=[False, False])
    return work.drop_duplicates(["row", "target_index"], keep="first").head(spec.pool_top).reset_index(drop=True)


def add_score(after: dict[str, float], before: dict[str, float]) -> float:
    return (
        360.0 * (-(after["route"] - before["route"]))
        + 280.0 * (-(after["h098"] - before["h098"]))
        + 115.0 * (-(after["curv_marg"] - before["curv_marg"]))
        + 0.18 * (after["margin"] - before["margin"])
        + 0.14 * (-(after["h088"] - before["h088"]))
        - 5.0 * (after["badw"] - before["badw"])
    )


def greedy_add(start: np.ndarray, work: pd.DataFrame, spec: H127Spec, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes) -> tuple[np.ndarray, pd.DataFrame, dict[str, float], dict[str, float]]:
    move_mat = start.copy()
    start_eval = evaluate_matrix(move_mat, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
    added = []
    used = nonzero_keys(move_mat)
    selected_rows: set[int] = {int(row) for row in np.where(np.abs(move_mat).sum(axis=1) > 1.0e-12)[0]}
    subject_counts: dict[str, int] = {}
    target_counts: dict[str, int] = {target: 0 for target in TARGETS}
    for row, tidx in used:
        target_counts[TARGETS[tidx]] += 1
    for step in range(spec.max_add):
        before = evaluate_matrix(move_mat, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
        best = None
        for rec in work.to_dict("records"):
            row = int(rec["row"])
            tidx = int(rec["target_index"])
            key = (row, tidx)
            if key in used:
                continue
            target = str(rec["target"])
            subject = str(rec["subject_id"])
            if len(used) >= spec.max_cells:
                continue
            if row not in selected_rows and len(selected_rows) >= spec.max_rows:
                continue
            if row not in selected_rows and subject_counts.get(subject, 0) + 1 > spec.max_per_subject:
                continue
            if target_counts.get(target, 0) >= spec.max_per_target:
                continue
            tmp = move_mat.copy()
            tmp[row, tidx] = float(rec["h127_move"])
            after = evaluate_matrix(tmp, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
            if after["badw"] > spec.max_bad_weighted_pos or after["badmax"] > spec.max_bad_max_pos:
                continue
            if after["h088"] > spec.max_h088_cos or after["margin"] < spec.min_good_margin:
                continue
            if after["route"] > spec.route_pred_cap or after["h098"] > spec.h098_pred_cap:
                continue
            if after["curv_marg"] > spec.max_curv_marg:
                continue
            score = add_score(after, before)
            if best is None or score > best["h127_add_score"]:
                best = {
                    "step": step + 1,
                    "row": row,
                    "target_index": tidx,
                    "target": target,
                    "subject_id": subject,
                    "sleep_date": str(rec["sleep_date"]),
                    "h127_move": float(rec["h127_move"]),
                    "h127_safe_score": float(rec["h127_safe_score"]),
                    "h112_residual_safety": float(rec["h112_residual_safety"]),
                    "h112_residual_toxicity": float(rec["h112_residual_toxicity"]),
                    "h112_residual_gap": float(rec["h112_residual_gap"]),
                    "proposal_source": str(rec.get("proposal_source", "")),
                    "h127_add_score": score,
                    **{f"after_{key2}": value for key2, value in after.items()},
                    **{f"delta_{key2}": after[key2] - before[key2] for key2 in after},
                }
        if best is None or float(best["h127_add_score"]) < spec.min_add_score:
            break
        move_mat[int(best["row"]), int(best["target_index"])] = float(best["h127_move"])
        used.add((int(best["row"]), int(best["target_index"])))
        if int(best["row"]) not in selected_rows:
            selected_rows.add(int(best["row"]))
            subject_counts[str(best["subject_id"])] = subject_counts.get(str(best["subject_id"]), 0) + 1
        target_counts[str(best["target"])] = target_counts.get(str(best["target"]), 0) + 1
        added.append(best)
    final_eval = evaluate_matrix(move_mat, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
    return move_mat, pd.DataFrame(added), start_eval, final_eval


def make_selected(base_selected: pd.DataFrame, residual_pool: pd.DataFrame, added: pd.DataFrame, move_mat: np.ndarray) -> pd.DataFrame:
    core = base_selected.copy()
    core["h127_component"] = core.get("h126_component", "h126_soft_base")
    core["h127_actual_move"] = [
        float(move_mat[int(row), int(tidx)])
        for row, tidx in zip(core["row"].astype(int), core["target_index"].astype(int))
    ]
    core = core[np.abs(core["h127_actual_move"].to_numpy(dtype=np.float64)) > 1.0e-12].copy()
    if added.empty:
        combined = core
    else:
        key_set = set(zip(added["row"].astype(int), added["target_index"].astype(int)))
        add_rows = residual_pool[
            [
                (int(row), int(tidx)) in key_set
                for row, tidx in zip(residual_pool["row"].astype(int), residual_pool["target_index"].astype(int))
            ]
        ].copy()
        add_rows = add_rows.sort_values(["row", "target_index"]).drop_duplicates(["row", "target_index"], keep="first")
        lookup = {
            (int(row), int(tidx)): float(move)
            for row, tidx, move in zip(added["row"], added["target_index"], added["h127_move"])
        }
        add_rows["h127_component"] = "h127_residual_basis"
        add_rows["h127_actual_move"] = [
            lookup[(int(row), int(tidx))]
            for row, tidx in zip(add_rows["row"].astype(int), add_rows["target_index"].astype(int))
        ]
        for col in core.columns:
            if col not in add_rows.columns:
                add_rows[col] = np.nan
        for col in add_rows.columns:
            if col not in core.columns:
                core[col] = np.nan
        combined = pd.concat([core[add_rows.columns], add_rows], ignore_index=True)
    combined["h112_move"] = combined["h127_actual_move"].to_numpy(dtype=np.float64)
    combined["h097_move_col"] = "h112_move"
    return combined.sort_values(["row", "target_index"]).reset_index(drop=True)


def run() -> None:
    cleanup_previous_outputs()
    pool, _public, sample, base_prob, cell, h098_fit, route_fit, basis_fit_df, basis_fit_moves, bad_axes, bad_moves, good_moves, axes, fit, model_scores, props = h118mod.prepare_context()
    scored = h123mod.build_scored_pool(pool, base_prob, fit, bad_axes, bad_moves, good_moves, axes, props)
    base_selected = load_h126_selected()
    removed = load_h122_removed()
    start_path = ROOT / "submission_h126_coeffeq_3fe3eee4_uploadsafe.csv"
    start_move = h126mod.load_move_path(start_path, sample, base_prob)
    h126_rows = {int(row) for row in np.where(np.abs(start_move).sum(axis=1) > 1.0e-12)[0]}
    residual_pool = annotate_residual_pool(scored, start_move, removed, h126_rows)

    start_eval = evaluate_matrix(start_move, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
    previous = {
        "h126": start_move.reshape(-1),
        "h125": h126mod.load_move_path(ROOT / "submission_h125_rowbundle_f3990392_uploadsafe.csv", sample, base_prob).reshape(-1),
        "h124": h126mod.load_move_path(ROOT / "submission_h124_dualsensor_b8e822c0_uploadsafe.csv", sample, base_prob).reshape(-1),
        "h122": h126mod.load_move_path(ROOT / "submission_h122_pruneeq_0a9edcce_uploadsafe.csv", sample, base_prob).reshape(-1),
        "h088": h115mod.load_previous_move(sample, base_prob, "submission_h088_*_uploadsafe.csv"),
    }

    candidate_rows = []
    selected_frames = []
    added_frames = []
    audit_rows = []
    for spec in candidate_specs():
        work = prepare_work(residual_pool, spec)
        audit_rows.append({"spec_name": spec.name, "condition": spec.add_condition, "pool_rows": int(len(work))})
        if work.empty:
            continue
        move_mat, added, before, final = greedy_add(
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
        if added.empty:
            continue
        component_gain = (
            360.0 * (-(final["route"] - start_eval["route"]))
            + 280.0 * (-(final["h098"] - start_eval["h098"]))
            + 0.18 * (final["margin"] - start_eval["margin"])
            + 0.14 * (-(final["h088"] - start_eval["h088"]))
        )
        audit_rows[-1]["added_cells"] = int(len(added))
        audit_rows[-1]["component_gain"] = float(component_gain)
        if component_gain < spec.min_component_gain:
            continue
        prob = materialize(base_prob, move_mat)
        if int((np.abs(prob - base_prob) > TOL).sum()) == 0:
            continue
        hash_id = short_hash(prob)
        candidate_id = safe_id(f"h127_{spec.name}_{hash_id}", 128)
        path = OUT / f"submission_{candidate_id}.csv"
        h085mod.write_submission(sample, prob, path)
        selected_cells = make_selected(base_selected, residual_pool, added, move_mat)
        axis = h102mod.cumulative_axis_metrics(move_mat.reshape(-1), bad_axes, bad_moves, good_moves)
        diag = {
            "h118_zero_curv": -0.0002616634510263019,
            "h118_curv_pred_delta_vs_h057": final["curv_marg"] - 0.0002616634510263019,
            "h118_curv_marginal_vs_zero": final["curv_marg"],
            "h118_mean_forbidden_same": float(selected_cells.get("h117_forbidden_same", pd.Series([0.0])).astype(float).mean()),
            "h118_max_forbidden_same": float(selected_cells.get("h117_forbidden_same", pd.Series([0.0])).astype(float).max()),
            "h118_mean_forbidden_pressure": float(selected_cells.get("h117_forbidden_pressure", pd.Series([0.0])).astype(float).mean()),
            "h118_mean_veto_score": float(selected_cells.get("h118_forbidden_veto_score", pd.Series([1.0])).astype(float).mean()),
            "h118_selected_rows": int(selected_cells["row"].nunique()),
            "h127_start_cells": int((np.abs(start_move) > 1.0e-12).sum()),
            "h127_added_cells": int(len(added)),
            "h127_added_rows": int(added["row"].nunique()),
            "h127_added_targets": ";".join(f"{k}:{v}" for k, v in added["target"].value_counts().to_dict().items()),
            "h127_component_gain": float(component_gain),
            "h127_delta_start_route": float(final["route"] - start_eval["route"]),
            "h127_delta_start_h098": float(final["h098"] - start_eval["h098"]),
            "h127_delta_start_h088": float(final["h088"] - start_eval["h088"]),
            "h127_delta_start_margin": float(final["margin"] - start_eval["margin"]),
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
        metrics["h127_worldview"] = spec.worldview
        metrics["h127_fit_feature_set"] = fit.feature_set
        metrics["h127_fit_alpha"] = fit.alpha
        metrics["h127_fit_score"] = fit.score
        metrics["h127_score"] = (
            320.0 * (-float(metrics["route_basis_pred_delta_vs_h057"]))
            + 285.0 * (-float(metrics["model_pred_delta_vs_h057"]))
            + 95.0 * (-float(metrics["h118_curv_marginal_vs_zero"]))
            + 0.18 * float(metrics["h102_cum_good_bad_margin"])
            + 0.12 * max(-float(metrics["h102_cum_h088_axis_cos"]), 0.0)
            + 0.12 * float(metrics["selected_mean_residual_safety"])
            + 0.13 * float(metrics["selected_mean_residual_gap"])
            - 0.13 * float(metrics["selected_mean_residual_toxicity"])
            + 1.5 * max(component_gain, 0.0)
            - 0.015 * max(float(metrics["selected_cells"]) - 32.0, 0.0)
            - 20.0 * max(float(metrics["hard_diag_delta_vs_h057"]), 0.0)
            - 0.8 * max(h088_cos, 0.0)
        )
        candidate_rows.append(metrics)
        selected2 = selected_cells.copy()
        if "candidate_id" in selected2.columns:
            selected2 = selected2.drop(columns=["candidate_id"])
        selected2.insert(0, "candidate_id", candidate_id)
        selected_frames.append(selected2)
        added2 = added.copy()
        added2.insert(0, "candidate_id", candidate_id)
        added_frames.append(added2)

    audit = pd.DataFrame(audit_rows)
    candidates = pd.DataFrame(candidate_rows)
    residual_pool.to_csv(OUT / "h127_residual_pool.csv", index=False)
    audit.to_csv(OUT / "h127_audit.csv", index=False)
    model_scores.to_csv(OUT / "h127_curvature_model_scores.csv", index=False)
    pd.DataFrame([{"baseline": "h126_soft", **start_eval}]).to_csv(OUT / "h127_start_metrics.csv", index=False)
    if candidates.empty:
        report = f"""# H127 Residual Basis Discovery HS-JEPA

No candidate was promoted.

Audit:

{md_table(audit, 20)}

Start metrics:

{md_table(pd.DataFrame([{"baseline": "h126_soft", **start_eval}]), 5)}
"""
        (OUT / "h127_report.md").write_text(report, encoding="utf-8")
        print("H127 promoted no candidate")
        print(audit.to_string(index=False))
        return

    candidates = candidates.sort_values(["h127_score", "h127_component_gain", "route_basis_pred_delta_vs_h057"], ascending=[False, False, True]).reset_index(drop=True)
    selected = candidates.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"submission_h127_residbasis_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)
    decision = {
        "decision": "promote_h127_residual_basis_discovery",
        "selected_candidate_id": selected["candidate_id"],
        "root_uploadsafe_path": str(root_path),
        "worldview": selected["h127_worldview"],
        **selected,
        **{f"root_{key}": value for key, value in validation.items()},
    }
    candidates.to_csv(OUT / "h127_candidates.csv", index=False)
    pd.concat(selected_frames, ignore_index=True).to_csv(OUT / "h127_selected_cells.csv", index=False)
    pd.concat(added_frames, ignore_index=True).to_csv(OUT / "h127_added_cells.csv", index=False)
    pd.DataFrame([decision]).to_csv(OUT / "h127_decision.csv", index=False)

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
        "h127_added_cells",
        "h127_added_targets",
        "h127_delta_start_route",
        "h127_delta_start_h098",
        "h127_delta_start_h088",
        "h127_delta_start_margin",
        "model_pred_delta_vs_h057",
        "route_basis_pred_delta_vs_h057",
        "h102_cum_h088_axis_cos",
        "h102_cum_good_bad_margin",
        "h127_component_gain",
        "h127_score",
        "file",
    ]
    report = f"""# H127 Residual Basis Discovery HS-JEPA

Question: after H126 proves coefficient solving is too narrow, does a new
safe action basis exist outside the current support and outside the H122-pruned
toxic sector?

Audit:

{md_table(audit, 20)}

Start metrics:

{md_table(pd.DataFrame([{"baseline": "h126_soft", **start_eval}]), 5)}

Candidates:

{md_table(candidates[cols], 20)}

Decision:

{md_table(pd.DataFrame([decision]), 1)}

Interpretation rule:

- If H127 improves, H126 was missing an orthogonal residual action component.
- If H126/H125/H124 improve more, residual basis discovery is still finding
  local stress artifacts, and the next big bet must change the proposal
  generator rather than mine the same residual pool.
- If no H127 candidate improves or survives, the current residual pool is
  diagnostic only after H122 pruning.
"""
    (OUT / "h127_report.md").write_text(report, encoding="utf-8")
    print("H127 selected candidate")
    print(candidates[cols].head(10).to_string(index=False))
    print("\nDecision")
    print(pd.DataFrame([decision])[["decision", "selected_candidate_id", "root_uploadsafe_path", "root_upload_safe"]].to_string(index=False))


if __name__ == "__main__":
    run()
