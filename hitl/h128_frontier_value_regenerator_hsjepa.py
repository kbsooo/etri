#!/usr/bin/env python3
"""H128: frontier-value regenerated proposal HS-JEPA.

H127 found that mining the existing residual proposal pool only adds one
margin-stabilizing cell.  H128 changes the proposal generator itself: H098's
frontier signed action equation supplies the value/move direction, while H127's
public/private toxicity gate supplies the admissible support.
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
OUT = HITL / "h128_frontier_value_regenerator_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H127_PATH = HITL / "h127_residual_basis_discovery_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h127mod", H127_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H127_PATH}")
h127mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h127mod
SPEC.loader.exec_module(h127mod)

H098_PATH = HITL / "h098_frontier_weighted_action_equation_hsjepa.py"
SPEC2 = importlib.util.spec_from_file_location("h098mod_h128", H098_PATH)
if SPEC2 is None or SPEC2.loader is None:
    raise RuntimeError(f"cannot import {H098_PATH}")
h098mod = importlib.util.module_from_spec(SPEC2)
sys.modules[SPEC2.name] = h098mod
SPEC2.loader.exec_module(h098mod)

h126mod = h127mod.h126mod
h123mod = h127mod.h123mod
h122mod = h127mod.h122mod
h118mod = h127mod.h118mod
h115mod = h127mod.h115mod
h102mod = h127mod.h102mod
h085mod = h127mod.h085mod

TARGETS = h127mod.TARGETS
TOL = h127mod.TOL


@dataclass(frozen=True)
class H128Spec:
    name: str
    group: str
    move_mode: str
    target_condition: str
    alpha: float
    cap: float
    max_add: int
    min_add_score: float
    max_cells: int
    max_rows: int
    max_per_subject: int
    max_per_target: int
    amp: float
    pool_top: int
    min_value_score: float
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

    @property
    def min_score(self) -> float:
        return self.min_value_score


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
    for path in OUT.glob("submission_h128_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h128_frontiervalue_*.csv"):
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


def candidate_specs() -> list[H128Spec]:
    common = dict(
        max_cells=48,
        max_rows=40,
        max_per_subject=24,
        max_per_target=24,
        amp=1.0,
        pool_top=380,
        min_value_score=0.20,
        min_residual_gap=0.12,
        max_residual_toxicity=0.58,
        min_residual_safety=0.52,
        max_bad_weighted_pos=0.0005,
        max_bad_max_pos=0.0020,
        max_curv_marg=0.000070,
        max_h088_hard_cosine=-0.020,
        min_component_gain=0.00020,
    )
    return [
        H128Spec(
            name="frontier_descent_margin",
            group="frontier_descent",
            move_mode="descent",
            target_condition="nonq2",
            alpha=0.035,
            cap=0.055,
            max_add=12,
            min_add_score=0.00040,
            max_h088_cos=-0.040,
            min_good_margin=0.148,
            route_pred_cap=-0.000670,
            h098_pred_cap=-0.000031,
            worldview="regenerate residual proposals from H098 frontier descent, but admit them only as margin-safe non-Q2 actions",
            **common,
        ),
        H128Spec(
            name="counter_h088_margin",
            group="counter_h088",
            move_mode="counter_h088",
            target_condition="h088_toxic",
            alpha=0.030,
            cap=0.050,
            max_add=14,
            min_add_score=0.00035,
            max_h088_cos=-0.045,
            min_good_margin=0.148,
            route_pred_cap=-0.000665,
            h098_pred_cap=-0.000031,
            worldview="H088 is not an action head, but its toxic direction can regenerate value when filtered through H127 safety",
            **common,
        ),
        H128Spec(
            name="conflict_bridge_margin",
            group="conflict_bridge",
            move_mode="conflict",
            target_condition="anti_conflict_or_neighbor",
            alpha=0.040,
            cap=0.060,
            max_add=12,
            min_add_score=0.00035,
            max_h088_cos=-0.042,
            min_good_margin=0.148,
            route_pred_cap=-0.000665,
            h098_pred_cap=-0.000031,
            worldview="H057/H088 conflict geometry supplies regenerated value only near already safe episode rows",
            **common,
        ),
        H128Spec(
            name="hybrid_frontier_counter",
            group="hybrid",
            move_mode="hybrid",
            target_condition="nonq2",
            alpha=0.032,
            cap=0.052,
            max_add=16,
            min_add_score=0.00035,
            max_h088_cos=-0.040,
            min_good_margin=0.150,
            route_pred_cap=-0.000660,
            h098_pred_cap=-0.000031,
            worldview="blend frontier descent with counter-H088 value to produce a new proposal generator under toxicity gates",
            **common,
        ),
        H128Spec(
            name="episode_s2_margin_regen",
            group="episode_s2",
            move_mode="hybrid",
            target_condition="episode_s_stage",
            alpha=0.040,
            cap=0.060,
            max_add=10,
            min_add_score=0.00035,
            max_h088_cos=-0.038,
            min_good_margin=0.150,
            route_pred_cap=-0.000660,
            h098_pred_cap=-0.000031,
            worldview="H127's row-144 S2 result points to a small episode-stage regenerated value family",
            **common,
        ),
    ]


def load_action_pool() -> pd.DataFrame:
    path = HITL / "h098_frontier_weighted_action_equation_hsjepa/h098_action_pool.csv"
    if path.exists():
        return pd.read_csv(path)
    base = h098mod.h085mod.load_sub(h098mod.BASE_FILE)
    sample = base[h098mod.KEYS].copy()
    base_prob = base[h098mod.TARGETS].to_numpy(dtype=np.float64)
    cell_raw = h098mod.h097mod.ensure_h095_cell_table(sample, base_prob)
    cell, feature_sets = h098mod.h097mod.add_context_features(cell_raw, sample)
    public = h098mod.h097mod.load_public_moves(sample, base_prob)
    _scores, _preds, fit = h098mod.evaluate_weighted_models(public, cell, feature_sets)
    gradient = h098mod.h097mod.response_gradient(cell, fit)
    return h098mod.build_frontier_pool(cell, gradient)


def load_start(sample: pd.DataFrame, base_prob: np.ndarray) -> tuple[np.ndarray, pd.DataFrame, str]:
    h127_path = ROOT / "submission_h127_residbasis_9b7f8d9a_uploadsafe.csv"
    if h127_path.exists():
        selected = pd.read_csv(HITL / "h127_residual_basis_discovery_hsjepa/h127_selected_cells.csv")
        decision = pd.read_csv(HITL / "h127_residual_basis_discovery_hsjepa/h127_decision.csv")
        cid = str(decision["selected_candidate_id"].iloc[0])
        return h126mod.load_move_path(h127_path, sample, base_prob), selected[selected["candidate_id"].astype(str) == cid].copy(), "h127"
    h126_path = ROOT / "submission_h126_coeffeq_3fe3eee4_uploadsafe.csv"
    selected = pd.read_csv(HITL / "h126_component_coefficient_equation_hsjepa/h126_selected_cells.csv")
    decision = pd.read_csv(HITL / "h126_component_coefficient_equation_hsjepa/h126_decision.csv")
    cid = str(decision["selected_candidate_id"].iloc[0])
    return h126mod.load_move_path(h126_path, sample, base_prob), selected[selected["candidate_id"].astype(str) == cid].copy(), "h126"


def build_value_pool(scored_pool: pd.DataFrame, action_pool: pd.DataFrame, start_move: np.ndarray, removed: pd.DataFrame, h127_rows: set[int]) -> pd.DataFrame:
    active = nonzero_keys(start_move)
    removed_keys = set(zip(removed["row"].astype(int), removed["target_index"].astype(int)))
    safe = scored_pool.copy()
    safe["flat_index"] = safe["flat_index"].astype(int)
    safe["row"] = safe["row"].astype(int)
    safe["target_index"] = safe["target_index"].astype(int)
    keep = []
    for row, tidx, target in zip(safe["row"], safe["target_index"], safe["target"].astype(str)):
        key = (int(row), int(tidx))
        keep.append(key not in active and key not in removed_keys and target != "Q2")
    safe = safe[np.asarray(keep)].copy()

    cols = [
        "flat_index",
        "h097_gradient",
        "h097_descent_logit_move",
        "h097_counter_h088_move",
        "h097_conflict_move",
        "h097_positive_move",
        "h098_frontier_cell_score",
    ]
    extra = action_pool[[c for c in cols if c in action_pool.columns]].drop_duplicates("flat_index")
    out = safe.merge(extra, on="flat_index", how="left", suffixes=("", "_h098"))
    for col in [
        "h097_gradient",
        "h097_descent_logit_move",
        "h097_counter_h088_move",
        "h097_conflict_move",
        "h097_positive_move",
        "h098_frontier_cell_score_h098",
    ]:
        if col not in out.columns:
            out[col] = 0.0
    if "h098_frontier_cell_score_h098" in out.columns:
        out["h128_frontier_score"] = out["h098_frontier_cell_score_h098"].fillna(out.get("h098_frontier_cell_score", 0.0))
    else:
        out["h128_frontier_score"] = out.get("h098_frontier_cell_score", 0.0)
    out["h128_near_h127_row"] = [1.0 if int(row) in h127_rows or int(row) - 1 in h127_rows or int(row) + 1 in h127_rows else 0.0 for row in out["row"]]
    out["h128_value_score"] = (
        0.18 * rank01(out["h128_frontier_score"].to_numpy(dtype=np.float64), high=True)
        + 0.14 * rank01(np.abs(out["h097_gradient"].to_numpy(dtype=np.float64)), high=True)
        + 0.13 * rank01(out["h112_residual_safety"].to_numpy(dtype=np.float64), high=True)
        + 0.12 * rank01(out["h112_residual_gap"].to_numpy(dtype=np.float64), high=True)
        + 0.10 * rank01(out["h110_benefit_toxicity_gap"].to_numpy(dtype=np.float64), high=True)
        + 0.10 * rank01(out["h098_frontier_cell_score"].to_numpy(dtype=np.float64), high=True)
        + 0.08 * out["h128_near_h127_row"].to_numpy(dtype=np.float64)
        + 0.07 * rank01(out["h095_safe_cell_score"].to_numpy(dtype=np.float64), high=True)
        - 0.14 * rank01(out["h112_residual_toxicity"].to_numpy(dtype=np.float64), high=True)
        - 0.12 * rank01(out["latent_shortcut_energy"].to_numpy(dtype=np.float64), high=True)
        - 0.10 * rank01(out["bad_pressure_rank"].to_numpy(dtype=np.float64), high=True)
        - 0.08 * rank01(out["h117_forbidden_pressure"].to_numpy(dtype=np.float64), high=True)
    )
    return out.sort_values(["h128_value_score", "h112_residual_safety"], ascending=[False, False]).reset_index(drop=True)


def target_allowed(rec: dict[str, object], spec: H128Spec) -> bool:
    target = str(rec["target"])
    if spec.target_condition == "nonq2":
        return target != "Q2"
    if spec.target_condition == "h088_toxic":
        return target != "Q2" and float(rec.get("h088_toxicity", 0.0)) >= 0.45
    if spec.target_condition == "anti_conflict_or_neighbor":
        return target != "Q2" and (
            float(rec.get("h057_h088_anti_conflict", 0.0)) >= 0.5
            or float(rec.get("h128_near_h127_row", 0.0)) >= 0.5
        )
    if spec.target_condition == "episode_s_stage":
        return target in {"S1", "S2", "S3", "S4"} and float(rec.get("h128_near_h127_row", 0.0)) >= 0.5
    raise ValueError(spec.target_condition)


def move_value(rec: dict[str, object], spec: H128Spec) -> float:
    if spec.move_mode == "descent":
        raw = float(rec.get("h097_descent_logit_move", 0.0))
    elif spec.move_mode == "counter_h088":
        raw = float(rec.get("h097_counter_h088_move", 0.0))
    elif spec.move_mode == "conflict":
        raw = float(rec.get("h097_conflict_move", 0.0))
    elif spec.move_mode == "hybrid":
        raw = (
            0.48 * float(rec.get("h097_descent_logit_move", 0.0))
            + 0.34 * float(rec.get("h097_counter_h088_move", 0.0))
            + 0.18 * float(rec.get("h097_conflict_move", 0.0))
        )
    else:
        raise ValueError(spec.move_mode)
    return float(np.clip(raw * spec.alpha, -spec.cap, spec.cap))


def prepare_work(value_pool: pd.DataFrame, spec: H128Spec) -> pd.DataFrame:
    work = value_pool.copy()
    keep = [target_allowed(rec, spec) for rec in work.to_dict("records")]
    work = work[np.asarray(keep)].copy()
    if work.empty:
        return work
    work = work[work["h117_forbidden_same"].to_numpy(dtype=np.float64) <= 1.0e-12].copy()
    work = work[work["h117_forbidden_pressure"].to_numpy(dtype=np.float64) <= 1.0e-12].copy()
    work = work[work["h112_residual_safety"].to_numpy(dtype=np.float64) >= spec.min_residual_safety].copy()
    work = work[work["h112_residual_toxicity"].to_numpy(dtype=np.float64) <= spec.max_residual_toxicity].copy()
    work = work[work["h112_residual_gap"].to_numpy(dtype=np.float64) >= spec.min_residual_gap].copy()
    work = work[work["h128_value_score"].to_numpy(dtype=np.float64) >= spec.min_value_score].copy()
    if work.empty:
        return work
    work["h128_move"] = [move_value(rec, spec) for rec in work.to_dict("records")]
    work = work[np.abs(work["h128_move"].to_numpy(dtype=np.float64)) > 1.0e-8].copy()
    return work.sort_values(["h128_value_score", "h112_residual_safety"], ascending=[False, False]).drop_duplicates(["row", "target_index"], keep="first").head(spec.pool_top).reset_index(drop=True)


def add_score(after: dict[str, float], before: dict[str, float]) -> float:
    return (
        285.0 * (-(after["h098"] - before["h098"]))
        + 130.0 * (-(after["curv_marg"] - before["curv_marg"]))
        + 0.22 * (after["margin"] - before["margin"])
        + 0.14 * (-(after["h088"] - before["h088"]))
        + 120.0 * max(-(after["route"] - before["route"]), 0.0)
        - 75.0 * max(after["route"] - before["route"], 0.0)
        - 5.0 * (after["badw"] - before["badw"])
    )


def greedy_add(start: np.ndarray, work: pd.DataFrame, spec: H128Spec, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes) -> tuple[np.ndarray, pd.DataFrame, dict[str, float], dict[str, float]]:
    move_mat = start.copy()
    start_eval = evaluate_matrix(move_mat, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
    added = []
    used = nonzero_keys(move_mat)
    selected_rows: set[int] = {int(row) for row in np.where(np.abs(move_mat).sum(axis=1) > 1.0e-12)[0]}
    target_counts = {target: 0 for target in TARGETS}
    for _row, tidx in used:
        target_counts[TARGETS[tidx]] += 1
    subject_counts: dict[str, int] = {}
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
            tmp[row, tidx] = float(rec["h128_move"])
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
            if best is None or score > best["h128_add_score"]:
                best = {
                    "step": step + 1,
                    "row": row,
                    "target_index": tidx,
                    "target": target,
                    "subject_id": subject,
                    "sleep_date": str(rec["sleep_date"]),
                    "h128_move": float(rec["h128_move"]),
                    "h128_value_score": float(rec["h128_value_score"]),
                    "h128_frontier_score": float(rec.get("h128_frontier_score", 0.0)),
                    "h112_residual_safety": float(rec["h112_residual_safety"]),
                    "h112_residual_toxicity": float(rec["h112_residual_toxicity"]),
                    "h112_residual_gap": float(rec["h112_residual_gap"]),
                    "proposal_source": str(rec.get("proposal_source", "")),
                    "h128_add_score": score,
                    **{f"after_{key2}": value for key2, value in after.items()},
                    **{f"delta_{key2}": after[key2] - before[key2] for key2 in after},
                }
        if best is None or float(best["h128_add_score"]) < spec.min_add_score:
            break
        move_mat[int(best["row"]), int(best["target_index"])] = float(best["h128_move"])
        used.add((int(best["row"]), int(best["target_index"])))
        if int(best["row"]) not in selected_rows:
            selected_rows.add(int(best["row"]))
            subject_counts[str(best["subject_id"])] = subject_counts.get(str(best["subject_id"]), 0) + 1
        target_counts[str(best["target"])] = target_counts.get(str(best["target"]), 0) + 1
        added.append(best)
    final_eval = evaluate_matrix(move_mat, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
    return move_mat, pd.DataFrame(added), start_eval, final_eval


def make_selected(base_selected: pd.DataFrame, value_pool: pd.DataFrame, added: pd.DataFrame, move_mat: np.ndarray) -> pd.DataFrame:
    core = base_selected.copy()
    core["h128_component"] = core.get("h127_component", core.get("h126_component", "start_field"))
    core["h128_actual_move"] = [
        float(move_mat[int(row), int(tidx)])
        for row, tidx in zip(core["row"].astype(int), core["target_index"].astype(int))
    ]
    core = core[np.abs(core["h128_actual_move"].to_numpy(dtype=np.float64)) > 1.0e-12].copy()
    if added.empty:
        combined = core
    else:
        key_set = set(zip(added["row"].astype(int), added["target_index"].astype(int)))
        add_rows = value_pool[
            [
                (int(row), int(tidx)) in key_set
                for row, tidx in zip(value_pool["row"].astype(int), value_pool["target_index"].astype(int))
            ]
        ].copy()
        add_rows = add_rows.sort_values(["row", "target_index"]).drop_duplicates(["row", "target_index"], keep="first")
        lookup = {
            (int(row), int(tidx)): float(move)
            for row, tidx, move in zip(added["row"], added["target_index"], added["h128_move"])
        }
        add_rows["h128_component"] = "h128_frontier_value"
        add_rows["h128_actual_move"] = [
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
    combined["h112_move"] = combined["h128_actual_move"].to_numpy(dtype=np.float64)
    combined["h097_move_col"] = "h112_move"
    return combined.sort_values(["row", "target_index"]).reset_index(drop=True)


def run() -> None:
    cleanup_previous_outputs()
    pool, _public, sample, base_prob, cell, h098_fit, route_fit, basis_fit_df, basis_fit_moves, bad_axes, bad_moves, good_moves, axes, fit, model_scores, props = h118mod.prepare_context()
    scored = h123mod.build_scored_pool(pool, base_prob, fit, bad_axes, bad_moves, good_moves, axes, props)
    start_move, base_selected, start_name = load_start(sample, base_prob)
    removed = h127mod.load_h122_removed()
    action_pool = load_action_pool()
    start_rows = {int(row) for row in np.where(np.abs(start_move).sum(axis=1) > 1.0e-12)[0]}
    value_pool = build_value_pool(scored, action_pool, start_move, removed, start_rows)
    start_eval = evaluate_matrix(start_move, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
    previous = {
        "h127": start_move.reshape(-1),
        "h126": h126mod.load_move_path(ROOT / "submission_h126_coeffeq_3fe3eee4_uploadsafe.csv", sample, base_prob).reshape(-1),
        "h125": h126mod.load_move_path(ROOT / "submission_h125_rowbundle_f3990392_uploadsafe.csv", sample, base_prob).reshape(-1),
        "h124": h126mod.load_move_path(ROOT / "submission_h124_dualsensor_b8e822c0_uploadsafe.csv", sample, base_prob).reshape(-1),
        "h088": h115mod.load_previous_move(sample, base_prob, "submission_h088_*_uploadsafe.csv"),
    }

    candidate_rows = []
    selected_frames = []
    added_frames = []
    audit_rows = []
    for spec in candidate_specs():
        work = prepare_work(value_pool, spec)
        audit_rows.append({"spec_name": spec.name, "move_mode": spec.move_mode, "condition": spec.target_condition, "pool_rows": int(len(work))})
        if work.empty:
            continue
        move_mat, added, _before, final = greedy_add(
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
            285.0 * (-(final["h098"] - start_eval["h098"]))
            + 0.22 * (final["margin"] - start_eval["margin"])
            + 0.14 * (-(final["h088"] - start_eval["h088"]))
            - 75.0 * max(final["route"] - start_eval["route"], 0.0)
            + 120.0 * max(-(final["route"] - start_eval["route"]), 0.0)
        )
        audit_rows[-1]["added_cells"] = int(len(added))
        audit_rows[-1]["component_gain"] = float(component_gain)
        if component_gain < spec.min_component_gain:
            continue
        prob = materialize(base_prob, move_mat)
        hash_id = short_hash(prob)
        candidate_id = safe_id(f"h128_{spec.name}_{hash_id}", 128)
        path = OUT / f"submission_{candidate_id}.csv"
        h085mod.write_submission(sample, prob, path)
        selected_cells = make_selected(base_selected, value_pool, added, move_mat)
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
            "h128_start_field": start_name,
            "h128_start_cells": int((np.abs(start_move) > 1.0e-12).sum()),
            "h128_added_cells": int(len(added)),
            "h128_added_rows": int(added["row"].nunique()),
            "h128_added_targets": ";".join(f"{k}:{v}" for k, v in added["target"].value_counts().to_dict().items()),
            "h128_component_gain": float(component_gain),
            "h128_delta_start_route": float(final["route"] - start_eval["route"]),
            "h128_delta_start_h098": float(final["h098"] - start_eval["h098"]),
            "h128_delta_start_h088": float(final["h088"] - start_eval["h088"]),
            "h128_delta_start_margin": float(final["margin"] - start_eval["margin"]),
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
        metrics["h128_worldview"] = spec.worldview
        metrics["h128_fit_feature_set"] = fit.feature_set
        metrics["h128_fit_alpha"] = fit.alpha
        metrics["h128_fit_score"] = fit.score
        metrics["h128_score"] = (
            290.0 * (-float(metrics["model_pred_delta_vs_h057"]))
            + 240.0 * (-float(metrics["route_basis_pred_delta_vs_h057"]))
            + 90.0 * (-float(metrics["h118_curv_marginal_vs_zero"]))
            + 0.22 * float(metrics["h102_cum_good_bad_margin"])
            + 0.12 * max(-float(metrics["h102_cum_h088_axis_cos"]), 0.0)
            + 0.12 * float(metrics["selected_mean_residual_safety"])
            + 0.13 * float(metrics["selected_mean_residual_gap"])
            - 0.13 * float(metrics["selected_mean_residual_toxicity"])
            + 1.5 * max(component_gain, 0.0)
            - 0.010 * max(float(metrics["selected_cells"]) - 36.0, 0.0)
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
    value_pool.to_csv(OUT / "h128_value_pool.csv", index=False)
    audit.to_csv(OUT / "h128_audit.csv", index=False)
    model_scores.to_csv(OUT / "h128_curvature_model_scores.csv", index=False)
    pd.DataFrame([{"baseline": start_name, **start_eval}]).to_csv(OUT / "h128_start_metrics.csv", index=False)
    if candidates.empty:
        report = f"""# H128 Frontier-Value Regenerator HS-JEPA

No candidate was promoted.

Audit:

{md_table(audit, 20)}

Start metrics:

{md_table(pd.DataFrame([{"baseline": start_name, **start_eval}]), 5)}
"""
        (OUT / "h128_report.md").write_text(report, encoding="utf-8")
        print("H128 promoted no candidate")
        print(audit.to_string(index=False))
        return

    candidates = candidates.sort_values(["h128_score", "h128_component_gain", "model_pred_delta_vs_h057"], ascending=[False, False, True]).reset_index(drop=True)
    selected = candidates.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"submission_h128_frontiervalue_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)
    decision = {
        "decision": "promote_h128_frontier_value_regenerator",
        "selected_candidate_id": selected["candidate_id"],
        "root_uploadsafe_path": str(root_path),
        "worldview": selected["h128_worldview"],
        **selected,
        **{f"root_{key}": value for key, value in validation.items()},
    }
    candidates.to_csv(OUT / "h128_candidates.csv", index=False)
    pd.concat(selected_frames, ignore_index=True).to_csv(OUT / "h128_selected_cells.csv", index=False)
    pd.concat(added_frames, ignore_index=True).to_csv(OUT / "h128_added_cells.csv", index=False)
    pd.DataFrame([decision]).to_csv(OUT / "h128_decision.csv", index=False)

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
        "h128_added_cells",
        "h128_added_targets",
        "h128_delta_start_route",
        "h128_delta_start_h098",
        "h128_delta_start_h088",
        "h128_delta_start_margin",
        "model_pred_delta_vs_h057",
        "route_basis_pred_delta_vs_h057",
        "h102_cum_h088_axis_cos",
        "h102_cum_good_bad_margin",
        "h128_component_gain",
        "h128_score",
        "file",
    ]
    report = f"""# H128 Frontier-Value Regenerator HS-JEPA

Question: can the proposal generator be changed by using H098 frontier value
directions while keeping H127's public/private toxicity gate?

Audit:

{md_table(audit, 20)}

Start metrics:

{md_table(pd.DataFrame([{"baseline": start_name, **start_eval}]), 5)}

Candidates:

{md_table(candidates[cols], 20)}

Decision:

{md_table(pd.DataFrame([decision]), 1)}

Interpretation rule:

- If H128 improves, the missing object after H127 is value regeneration, not
  support mining.
- If H127/H126 remain better, H098 frontier value is not action-grade even
  under H127 toxicity gates.
- If H128 loses badly, H098 should stay a diagnostic response equation rather
  than a proposal generator.
"""
    (OUT / "h128_report.md").write_text(report, encoding="utf-8")
    print("H128 selected candidate")
    print(candidates[cols].head(10).to_string(index=False))
    print("\nDecision")
    print(pd.DataFrame([decision])[["decision", "selected_candidate_id", "root_uploadsafe_path", "root_upload_safe"]].to_string(index=False))


if __name__ == "__main__":
    run()
