#!/usr/bin/env python3
"""H123: prune-then-refill equation solver HS-JEPA.

H122 says public-safe action may be subtractive: remove toxic H118 stage
actions.  H123 tests the next question: after pruning, is there a tiny safe
complement that should be refilled, or is the sparse H122 core complete?
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
OUT = HITL / "h123_prune_refill_equation_solver_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H122_PATH = HITL / "h122_action_prune_equation_solver_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h122mod", H122_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H122_PATH}")
h122mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h122mod
SPEC.loader.exec_module(h122mod)

h121mod = h122mod.h121mod
h120mod = h122mod.h120mod
h118mod = h122mod.h118mod
h117mod = h118mod.h117mod
h115mod = h122mod.h115mod
h112mod = h122mod.h112mod
h102mod = h122mod.h102mod
h100mod = h122mod.h100mod
h097mod = h122mod.h097mod
h085mod = h122mod.h085mod

TARGETS = h122mod.TARGETS
TOL = h122mod.TOL


@dataclass(frozen=True)
class H123Spec:
    name: str
    group: str
    max_add: int
    min_add_score: float
    add_condition: str
    amp: float
    cap: float
    pool_top: int
    max_cells: int
    max_rows: int
    max_per_subject: int
    max_per_target: int
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
    require_single_margin_nonnegative: bool
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


def rank01(values: np.ndarray, high: bool = True) -> np.ndarray:
    return h085mod.rank01(np.asarray(values, dtype=np.float64), high=high)


def materialize(base_prob: np.ndarray, move_mat: np.ndarray) -> np.ndarray:
    return clip_prob(sigmoid(logit(base_prob) + move_mat))


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h123_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h123_refilleq_*.csv"):
        path.unlink()


def candidate_specs() -> list[H123Spec]:
    common = dict(
        max_cells=40,
        max_rows=32,
        max_per_subject=10,
        max_per_target=16,
        pool_top=220,
        min_score=0.08,
        min_residual_gap=0.02,
        max_residual_toxicity=0.60,
        min_residual_safety=0.50,
        max_bad_weighted_pos=0.0005,
        max_bad_max_pos=0.0020,
        max_h088_cos=-0.055,
        min_good_margin=0.118,
        h098_pred_cap=-0.000024,
    )
    return [
        H123Spec(
            name="single_route_q3_refill",
            group="prune_refill_q3",
            add_condition="q3",
            max_add=1,
            min_add_score=0.020,
            amp=0.35,
            cap=0.14,
            route_pred_cap=-0.000680,
            require_single_margin_nonnegative=False,
            worldview="after pruning H118 toxicity, a single Q3 route-complement cell completes the safe equation",
            **common,
        ),
        H123Spec(
            name="sparse_route_refill",
            group="prune_refill_sparse",
            add_condition="all_safe",
            max_add=4,
            min_add_score=0.004,
            amp=0.35,
            cap=0.14,
            route_pred_cap=-0.000700,
            require_single_margin_nonnegative=False,
            worldview="H122 core is incomplete; refill only cells that improve the route equation without entering H088 toxicity",
            **common,
        ),
        H123Spec(
            name="margin_stage_refill",
            group="prune_refill_margin_stage",
            add_condition="stage_margin",
            max_add=8,
            min_add_score=0.00015,
            amp=0.35,
            cap=0.14,
            route_pred_cap=-0.000600,
            require_single_margin_nonnegative=True,
            worldview="prune removes stage toxicity, then only margin-positive stage cells can be restored",
            **common,
        ),
        H123Spec(
            name="removed_row_complement",
            group="prune_refill_removed_row",
            add_condition="removed_row_complement",
            max_add=5,
            min_add_score=0.001,
            amp=0.35,
            cap=0.14,
            route_pred_cap=-0.000640,
            require_single_margin_nonnegative=False,
            worldview="rows where H118 was pruned need a different target-route complement, not the removed stage cell",
            **common,
        ),
    ]


def build_scored_pool(pool: pd.DataFrame, base_prob: np.ndarray, fit, bad_axes, bad_moves, good_moves, axes, props: pd.DataFrame) -> pd.DataFrame:
    forbidden_axes, forbidden_weights, _audit = h117mod.build_forbidden_axes(
        props, base_prob.shape, fit, pool, bad_axes, bad_moves, good_moves, axes
    )
    scored_raw = h117mod.annotate_forbidden_scores(props, forbidden_axes, forbidden_weights)
    scored = h118mod.annotate_veto_scores(scored_raw)
    scored["h123_pool_score"] = (
        0.34 * scored["h118_score_base"].to_numpy(dtype=np.float64)
        + 0.22 * rank01(scored["h112_residual_safety"].to_numpy(dtype=np.float64), high=True)
        + 0.16 * rank01(scored["h112_residual_gap"].to_numpy(dtype=np.float64), high=True)
        + 0.10 * rank01(scored["h112_antidote_score"].to_numpy(dtype=np.float64), high=True)
        + 0.08 * rank01(scored["h110_benefit_toxicity_gap"].to_numpy(dtype=np.float64), high=True)
        - 0.18 * rank01(scored["h112_residual_toxicity"].to_numpy(dtype=np.float64), high=True)
        - 0.10 * rank01(scored["latent_shortcut_energy"].to_numpy(dtype=np.float64), high=True)
        - 0.08 * rank01(scored["h117_forbidden_pressure"].to_numpy(dtype=np.float64), high=True)
    )
    return scored


def load_selected_h122() -> tuple[pd.DataFrame, pd.DataFrame]:
    decision = pd.read_csv(HITL / "h122_action_prune_equation_solver_hsjepa/h122_decision.csv")
    candidate_id = str(decision["selected_candidate_id"].iloc[0])
    selected = pd.read_csv(HITL / "h122_action_prune_equation_solver_hsjepa/h122_selected_cells.csv")
    removed = pd.read_csv(HITL / "h122_action_prune_equation_solver_hsjepa/h122_removed_cells.csv")
    selected = selected[selected["candidate_id"].astype(str) == candidate_id].copy()
    removed = removed[removed["candidate_id"].astype(str) == candidate_id].copy()
    return selected, removed


def allowed_addition(rec: dict[str, object], spec: H123Spec, removed_rows: set[int], removed_keys: set[tuple[int, int]], removed_targets_by_row: dict[int, set[int]]) -> bool:
    row = int(rec["row"])
    tidx = int(rec["target_index"])
    target = str(rec["target"])
    if target == "Q2":
        return False
    if (row, tidx) in removed_keys:
        return False
    if spec.add_condition == "q3":
        return target == "Q3"
    if spec.add_condition == "all_safe":
        return True
    if spec.add_condition == "stage_margin":
        return target in {"S1", "S2", "S3", "S4"}
    if spec.add_condition == "removed_row_complement":
        return row in removed_rows and tidx not in removed_targets_by_row.get(row, set())
    raise ValueError(spec.add_condition)


def evaluate_matrix(
    move_mat: np.ndarray,
    basis_fit_df: pd.DataFrame,
    basis_fit_moves: np.ndarray,
    route_fit,
    cell: pd.DataFrame,
    h098_fit,
    fit,
    pool: pd.DataFrame,
    bad_axes: pd.DataFrame,
    bad_moves: np.ndarray,
    good_moves: np.ndarray,
    axes: dict[str, object],
) -> dict[str, float]:
    return h122mod.evaluate_matrix(
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


def add_delta_score(after: dict[str, float], before: dict[str, float]) -> float:
    return (
        360.0 * (-(after["route"] - before["route"]))
        + 230.0 * (-(after["h098"] - before["h098"]))
        + 110.0 * (-(after["curv_marg"] - before["curv_marg"]))
        + 0.12 * (after["margin"] - before["margin"])
        + 0.10 * (-(after["h088"] - before["h088"]))
        - 5.0 * (after["badw"] - before["badw"])
    )


def prepare_add_pool(
    scored: pd.DataFrame,
    spec: H123Spec,
    active_keys: set[tuple[int, int]],
    removed_rows: set[int],
    removed_keys: set[tuple[int, int]],
    removed_targets_by_row: dict[int, set[int]],
) -> pd.DataFrame:
    work = scored.copy()
    work["row"] = work["row"].astype(int)
    work["target_index"] = work["target_index"].astype(int)
    keep = []
    for rec in work.to_dict("records"):
        key = (int(rec["row"]), int(rec["target_index"]))
        keep.append(key not in active_keys and allowed_addition(rec, spec, removed_rows, removed_keys, removed_targets_by_row))
    work = work[np.asarray(keep)].copy()
    work = work[work["h117_forbidden_same"].to_numpy(dtype=np.float64) <= 1.0e-12].copy()
    work = work[work["h112_residual_safety"].to_numpy(dtype=np.float64) >= spec.min_residual_safety].copy()
    work = work[work["h112_residual_toxicity"].to_numpy(dtype=np.float64) <= spec.max_residual_toxicity].copy()
    work = work[work["h112_residual_gap"].to_numpy(dtype=np.float64) >= spec.min_residual_gap].copy()
    work = work[work["h123_pool_score"].to_numpy(dtype=np.float64) >= spec.min_score].copy()
    if work.empty:
        return work
    work["h123_move"] = np.clip(work["proposal_move"].to_numpy(dtype=np.float64) * spec.amp, -spec.cap, spec.cap)
    work = work[np.abs(work["h123_move"].to_numpy(dtype=np.float64)) > 1.0e-8].copy()
    work = work.sort_values(["h123_pool_score", "h112_residual_safety"], ascending=[False, False])
    return work.drop_duplicates(["row", "target_index"], keep="first").head(spec.pool_top).reset_index(drop=True)


def greedy_refill(
    start: np.ndarray,
    work: pd.DataFrame,
    spec: H123Spec,
    basis_fit_df: pd.DataFrame,
    basis_fit_moves: np.ndarray,
    route_fit,
    cell: pd.DataFrame,
    h098_fit,
    fit,
    pool: pd.DataFrame,
    bad_axes: pd.DataFrame,
    bad_moves: np.ndarray,
    good_moves: np.ndarray,
    axes: dict[str, object],
) -> tuple[np.ndarray, pd.DataFrame]:
    move_mat = start.copy()
    added = []
    used: set[tuple[int, int]] = set(zip(*np.where(np.abs(move_mat) > 1.0e-12)))
    selected_rows: set[int] = {int(r) for r in np.where(np.abs(move_mat).sum(axis=1) > 1.0e-12)[0]}
    subject_counts: dict[str, int] = {}
    target_counts: dict[str, int] = {}
    if not work.empty:
        for rec in work.to_dict("records"):
            row = int(rec["row"])
            if row in selected_rows:
                subject_counts[str(rec["subject_id"])] = subject_counts.get(str(rec["subject_id"]), 0) + 1
                break
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
            tmp[row, tidx] = float(rec["h123_move"])
            after = evaluate_matrix(tmp, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
            if after["badw"] > spec.max_bad_weighted_pos or after["badmax"] > spec.max_bad_max_pos:
                continue
            if after["h088"] > spec.max_h088_cos or after["margin"] < spec.min_good_margin:
                continue
            if after["route"] > spec.route_pred_cap or after["h098"] > spec.h098_pred_cap:
                continue
            if spec.require_single_margin_nonnegative and (after["margin"] - before["margin"]) < 0.0:
                continue
            score = add_delta_score(after, before)
            if best is None or score > best["h123_add_score"]:
                best = {
                    "step": step + 1,
                    "row": row,
                    "target_index": tidx,
                    "target": target,
                    "subject_id": subject,
                    "h123_move": float(rec["h123_move"]),
                    "h123_pool_score": float(rec["h123_pool_score"]),
                    "h112_residual_safety": float(rec["h112_residual_safety"]),
                    "h112_residual_toxicity": float(rec["h112_residual_toxicity"]),
                    "h112_residual_gap": float(rec["h112_residual_gap"]),
                    "proposal_source": str(rec["proposal_source"]),
                    "h123_add_score": score,
                    **{f"after_{key2}": value for key2, value in after.items()},
                    **{f"delta_{key2}": after[key2] - before[key2] for key2 in after},
                }
        if best is None or float(best["h123_add_score"]) < spec.min_add_score:
            break
        move_mat[int(best["row"]), int(best["target_index"])] = float(best["h123_move"])
        used.add((int(best["row"]), int(best["target_index"])))
        if int(best["row"]) not in selected_rows:
            selected_rows.add(int(best["row"]))
            subject_counts[str(best["subject_id"])] = subject_counts.get(str(best["subject_id"]), 0) + 1
        target_counts[str(best["target"])] = target_counts.get(str(best["target"]), 0) + 1
        added.append(best)
    return move_mat, pd.DataFrame(added)


def make_selected_cells(h122_selected: pd.DataFrame, added: pd.DataFrame, scored: pd.DataFrame, move_mat: np.ndarray) -> pd.DataFrame:
    core = h122_selected.copy()
    core["h123_component"] = "h122_core"
    core["h123_actual_move"] = [
        float(move_mat[int(row), int(tidx)])
        for row, tidx in zip(core["row"].astype(int), core["target_index"].astype(int))
    ]
    core = core[np.abs(core["h123_actual_move"].to_numpy(dtype=np.float64)) > 1.0e-12].copy()
    if added.empty:
        combined = core.copy()
    else:
        keys = added[["row", "target_index"]].astype(int)
        key_set = set(zip(keys["row"], keys["target_index"]))
        add_rows = scored[
            [
                (int(row), int(tidx)) in key_set
                for row, tidx in zip(scored["row"].astype(int), scored["target_index"].astype(int))
            ]
        ].copy()
        add_rows = add_rows.sort_values(["row", "target_index"]).drop_duplicates(["row", "target_index"], keep="first")
        move_lookup = {
            (int(row), int(tidx)): float(move)
            for row, tidx, move in zip(added["row"], added["target_index"], added["h123_move"])
        }
        add_rows["h123_component"] = "h123_refill"
        add_rows["h123_actual_move"] = [
            move_lookup[(int(row), int(tidx))]
            for row, tidx in zip(add_rows["row"].astype(int), add_rows["target_index"].astype(int))
        ]
        for col in core.columns:
            if col not in add_rows.columns:
                add_rows[col] = np.nan
        for col in add_rows.columns:
            if col not in core.columns:
                core[col] = np.nan
        combined = pd.concat([core[add_rows.columns], add_rows], ignore_index=True)
    combined["h112_move"] = combined["h123_actual_move"].to_numpy(dtype=np.float64)
    combined["h097_move_col"] = "h112_move"
    return combined.sort_values(["row", "target_index"]).reset_index(drop=True)


def run() -> None:
    cleanup_previous_outputs()
    pool, _public, sample, base_prob, cell, h098_fit, route_fit, basis_fit_df, basis_fit_moves, bad_axes, bad_moves, good_moves, axes, fit, model_scores, props = h118mod.prepare_context()
    scored = build_scored_pool(pool, base_prob, fit, bad_axes, bad_moves, good_moves, axes, props)
    h122_selected, h122_removed = load_selected_h122()
    move_h122 = h115mod.load_previous_move(sample, base_prob, "submission_h122_pruneeq_*_uploadsafe.csv").reshape(base_prob.shape)
    active_keys = set(zip(*np.where(np.abs(move_h122) > 1.0e-12)))
    removed_keys = set(zip(h122_removed["row"].astype(int), h122_removed["target_index"].astype(int)))
    removed_rows = {int(x) for x in h122_removed["row"].astype(int).unique()}
    removed_targets_by_row: dict[int, set[int]] = {}
    for row, tidx in zip(h122_removed["row"].astype(int), h122_removed["target_index"].astype(int)):
        removed_targets_by_row.setdefault(int(row), set()).add(int(tidx))
    previous = {
        "h122": move_h122,
        "h121": h115mod.load_previous_move(sample, base_prob, "submission_h121_rowsensorpart_*_uploadsafe.csv"),
        "h120": h115mod.load_previous_move(sample, base_prob, "submission_h120_toxrow_*_uploadsafe.csv"),
        "h118": h115mod.load_previous_move(sample, base_prob, "submission_h118_forbiddenveto_*_uploadsafe.csv"),
        "h112": h115mod.load_previous_move(sample, base_prob, "submission_h112_residualtox_*_uploadsafe.csv"),
    }

    candidate_rows = []
    selected_frames = []
    added_frames = []
    audit_rows = []
    for spec in candidate_specs():
        work = prepare_add_pool(scored, spec, active_keys, removed_rows, removed_keys, removed_targets_by_row)
        audit_rows.append({"spec_name": spec.name, "add_pool_rows": int(len(work)), "condition": spec.add_condition})
        if work.empty:
            continue
        move_mat, added = greedy_refill(
            move_h122,
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
        evald = evaluate_matrix(move_mat, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
        axis = h102mod.cumulative_axis_metrics(move_mat.reshape(-1), bad_axes, bad_moves, good_moves)
        selected_cells = make_selected_cells(h122_selected, added, scored, move_mat)
        prob = materialize(base_prob, move_mat)
        if int((np.abs(prob - base_prob) > TOL).sum()) == 0:
            continue
        hash_id = short_hash(prob)
        candidate_id = safe_id(f"h123_{spec.name}_{hash_id}", 128)
        path = OUT / f"submission_{candidate_id}.csv"
        h085mod.write_submission(sample, prob, path)
        diag = {
            "h118_zero_curv": -0.0002616634510263019,
            "h118_curv_pred_delta_vs_h057": evald["curv_marg"] - 0.0002616634510263019,
            "h118_curv_marginal_vs_zero": evald["curv_marg"],
            "h118_mean_forbidden_same": float(selected_cells.get("h117_forbidden_same", pd.Series([0.0])).astype(float).mean()),
            "h118_max_forbidden_same": float(selected_cells.get("h117_forbidden_same", pd.Series([0.0])).astype(float).max()),
            "h118_mean_forbidden_pressure": float(selected_cells.get("h117_forbidden_pressure", pd.Series([0.0])).astype(float).mean()),
            "h118_mean_veto_score": float(selected_cells.get("h118_forbidden_veto_score", pd.Series([1.0])).astype(float).mean()),
            "h118_selected_rows": int(selected_cells["row"].nunique()),
            "h123_start_cells": int(len(active_keys)),
            "h123_added_cells": int(len(added)),
            "h123_added_rows": int(added["row"].nunique()),
            "h123_added_mean_score": float(added["h123_add_score"].mean()),
            "h123_added_targets": ";".join(f"{k}:{v}" for k, v in added["target"].value_counts().to_dict().items()),
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
        metrics["h123_condition"] = spec.add_condition
        metrics["h123_worldview"] = spec.worldview
        metrics["h123_fit_feature_set"] = fit.feature_set
        metrics["h123_fit_alpha"] = fit.alpha
        metrics["h123_fit_score"] = fit.score
        metrics["h123_score"] = (
            360.0 * (-float(metrics["route_basis_pred_delta_vs_h057"]))
            + 180.0 * (-float(metrics["model_pred_delta_vs_h057"]))
            + 105.0 * (-float(metrics["h118_curv_marginal_vs_zero"]))
            + 0.16 * float(metrics["h102_cum_good_bad_margin"])
            + 0.12 * max(-float(metrics["h102_cum_h088_axis_cos"]), 0.0)
            + 0.10 * float(metrics["selected_mean_residual_safety"])
            + 0.12 * float(metrics["selected_mean_residual_gap"])
            - 0.12 * float(metrics["selected_mean_residual_toxicity"])
            + 0.012 * float(metrics["h123_added_cells"])
            - 20.0 * max(float(metrics["hard_diag_delta_vs_h057"]), 0.0)
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
    audit.to_csv(OUT / "h123_add_pool_audit.csv", index=False)
    scored.to_csv(OUT / "h123_scored_pool.csv", index=False)
    model_scores.to_csv(OUT / "h123_curvature_model_scores.csv", index=False)
    if candidates.empty:
        report = f"""# H123 Prune-Refill Equation Solver HS-JEPA

No candidate was promoted.

Add-pool audit:

{md_table(audit, 20)}
"""
        (OUT / "h123_report.md").write_text(report, encoding="utf-8")
        print("H123 promoted no candidate")
        print(audit.to_string(index=False))
        return

    candidates = candidates.sort_values(["h123_score", "route_basis_pred_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True)
    selected = candidates.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"submission_h123_refilleq_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)
    decision = {
        "decision": "promote_h123_prune_refill_equation_solver",
        "selected_candidate_id": selected["candidate_id"],
        "root_uploadsafe_path": str(root_path),
        "worldview": selected["h123_worldview"],
        **selected,
        **{f"root_{key}": value for key, value in validation.items()},
    }
    candidates.to_csv(OUT / "h123_candidates.csv", index=False)
    pd.concat(selected_frames, ignore_index=True).to_csv(OUT / "h123_selected_cells.csv", index=False)
    pd.concat(added_frames, ignore_index=True).to_csv(OUT / "h123_added_cells.csv", index=False)
    pd.DataFrame([decision]).to_csv(OUT / "h123_decision.csv", index=False)
    cols = [
        "candidate_id",
        "spec_name",
        "h123_condition",
        "selected_cells",
        "changed_rows_vs_h057",
        "Q1_changed_vs_h057",
        "Q2_changed_vs_h057",
        "Q3_changed_vs_h057",
        "S1_changed_vs_h057",
        "S2_changed_vs_h057",
        "S3_changed_vs_h057",
        "S4_changed_vs_h057",
        "h123_added_cells",
        "h123_added_targets",
        "model_pred_delta_vs_h057",
        "route_basis_pred_delta_vs_h057",
        "h118_curv_marginal_vs_zero",
        "h102_cum_h088_axis_cos",
        "h102_cum_good_bad_margin",
        "selected_mean_residual_toxicity",
        "selected_mean_residual_safety",
        "selected_mean_residual_gap",
        "h123_score",
        "file",
    ]
    report = f"""# H123 Prune-Refill Equation Solver HS-JEPA

Question: after H122 removes toxic H118 stage actions, is the safe field
complete, or should a tiny route-safe complement be refilled?

Candidates:

{md_table(candidates[cols], 20)}

Decision:

{md_table(pd.DataFrame([decision]), 1)}

Interpretation rule:

- If H123 improves over H122, pruning is necessary but not sufficient; HS-JEPA
  needs a prune-then-refill action decoder.
- If H122 improves more, the sparse residual core is complete and refill
  actions are still local-stress overfit.
- If H121 improves more, replacement needs to be row-regime based rather than
  route-complement based.
"""
    (OUT / "h123_report.md").write_text(report, encoding="utf-8")
    print("H123 selected candidate")
    print(candidates[cols].head(10).to_string(index=False))
    print("\nDecision")
    print(pd.DataFrame([decision])[["decision", "selected_candidate_id", "root_uploadsafe_path", "root_upload_safe"]].to_string(index=False))


if __name__ == "__main__":
    run()
