#!/usr/bin/env python3
"""H122: action-prune equation solver HS-JEPA.

H121 showed that H085's row sensor can partition the H118 assignment field.
The next diagnostic is sharper: maybe the useful operation is not replacing
H118 with H120, but deleting public-toxic H118 cells.

H122 starts from H118 and greedily removes row-target actions whose removal
improves the public/private stress equation.
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
OUT = HITL / "h122_action_prune_equation_solver_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H121_PATH = HITL / "h121_row_sensor_partition_solver_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h121mod", H121_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H121_PATH}")
h121mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h121mod
SPEC.loader.exec_module(h121mod)

h120mod = h121mod.h120mod
h118mod = h121mod.h118mod
h115mod = h121mod.h115mod
h112mod = h121mod.h112mod
h102mod = h121mod.h102mod
h100mod = h121mod.h100mod
h097mod = h121mod.h097mod
h085mod = h121mod.h085mod

TARGETS = h121mod.TARGETS
TOL = h121mod.TOL


@dataclass(frozen=True)
class H122Spec:
    name: str
    condition: str
    max_remove: int
    min_remaining_cells: int
    min_remove_score: float
    min_sensor_rank: float
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
    worldview: str

    @property
    def group(self) -> str:
        return self.condition


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


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h122_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h122_pruneeq_*.csv"):
        path.unlink()


def route_pred(move_flat: np.ndarray, basis_fit_df: pd.DataFrame, basis_fit_moves: np.ndarray, route_fit: h100mod.RouteBasisFit) -> float:
    return h100mod.predict_candidate_delta(move_flat, basis_fit_df, basis_fit_moves, route_fit)


def h098_pred(move_flat: np.ndarray, cell: pd.DataFrame, h098_fit: h097mod.ResponseFit) -> float:
    return h097mod.predict_candidate_delta(move_flat, cell, h098_fit)


def curvature_pred(move_mat: np.ndarray, fit: h115mod.CurvatureFit, pool: pd.DataFrame, bad_axes: pd.DataFrame, bad_moves: np.ndarray, good_moves: np.ndarray, axes: dict[str, object]) -> float:
    return h115mod.predict_curvature(move_mat, fit, pool, bad_axes, bad_moves, good_moves, axes)


def candidate_specs() -> list[H122Spec]:
    common = dict(
        max_cells=80,
        max_rows=55,
        max_per_subject=12,
        max_per_target=24,
        amp=1.0,
        cap=0.24,
        pool_top=250,
        min_score=0.0,
        min_residual_gap=0.0,
        max_residual_toxicity=0.72,
        min_residual_safety=0.30,
        max_bad_weighted_pos=0.001,
        max_bad_max_pos=0.004,
    )
    return [
        H122Spec(
            name="prune_sensor_ge070_balanced",
            condition="sensor_ge",
            max_remove=24,
            min_remaining_cells=30,
            min_remove_score=0.00020,
            min_sensor_rank=0.70,
            max_h088_cos=-0.045,
            min_good_margin=0.120,
            route_pred_cap=-0.000585,
            h098_pred_cap=-0.000025,
            worldview="high H085 row-sensor cells inside H118 are public-toxic and should be pruned, not replaced",
            **common,
        ),
        H122Spec(
            name="prune_sensor_ge085_strict",
            condition="sensor_ge",
            max_remove=20,
            min_remaining_cells=34,
            min_remove_score=0.00020,
            min_sensor_rank=0.85,
            max_h088_cos=-0.045,
            min_good_margin=0.110,
            route_pred_cap=-0.000580,
            h098_pred_cap=-0.000020,
            worldview="only the highest H085 row-sensor cells should be pruned from H118",
            **common,
        ),
        H122Spec(
            name="prune_stage_public_toxic",
            condition="stage",
            max_remove=30,
            min_remaining_cells=20,
            min_remove_score=0.00020,
            min_sensor_rank=0.0,
            max_h088_cos=-0.055,
            min_good_margin=0.120,
            route_pred_cap=-0.000600,
            h098_pred_cap=-0.000015,
            worldview="objective Q/S stage cells carry the public-toxic part of H118 and should be removed",
            **common,
        ),
        H122Spec(
            name="prune_all_route_extreme",
            condition="all",
            max_remove=36,
            min_remaining_cells=14,
            min_remove_score=0.00020,
            min_sensor_rank=0.0,
            max_h088_cos=-0.080,
            min_good_margin=0.160,
            route_pred_cap=-0.000610,
            h098_pred_cap=0.000000,
            worldview="the safe field is the sparse residual core after deleting every public-toxic H118 action",
            **common,
        ),
    ]


def load_selected(path: str, decision_path: str) -> pd.DataFrame:
    selected = pd.read_csv(path)
    decision = pd.read_csv(decision_path)
    candidate_id = str(decision["selected_candidate_id"].iloc[0])
    return selected[selected["candidate_id"].astype(str) == candidate_id].copy()


def evaluate_matrix(
    move_mat: np.ndarray,
    basis_fit_df: pd.DataFrame,
    basis_fit_moves: np.ndarray,
    route_fit: h100mod.RouteBasisFit,
    cell: pd.DataFrame,
    h098_fit: h097mod.ResponseFit,
    fit: h115mod.CurvatureFit,
    pool: pd.DataFrame,
    bad_axes: pd.DataFrame,
    bad_moves: np.ndarray,
    good_moves: np.ndarray,
    axes: dict[str, object],
) -> dict[str, float]:
    flat = move_mat.reshape(-1)
    axis = h102mod.cumulative_axis_metrics(flat, bad_axes, bad_moves, good_moves)
    return {
        "route": route_pred(flat, basis_fit_df, basis_fit_moves, route_fit),
        "h098": h098_pred(flat, cell, h098_fit),
        "curv_marg": curvature_pred(move_mat, fit, pool, bad_axes, bad_moves, good_moves, axes) + 0.0002616634510263019,
        "badw": float(axis["h102_cum_bad_weighted_pos"]),
        "badmax": float(axis["h102_cum_bad_max_pos"]),
        "h088": float(axis["h102_cum_h088_axis_cos"]),
        "margin": float(axis["h102_cum_good_bad_margin"]),
    }


def remove_delta_score(after: dict[str, float], before: dict[str, float]) -> float:
    return (
        330.0 * (-(after["route"] - before["route"]))
        + 180.0 * (-(after["h098"] - before["h098"]))
        + 100.0 * (-(after["curv_marg"] - before["curv_marg"]))
        + 0.15 * (after["margin"] - before["margin"])
        + 0.10 * (-(after["h088"] - before["h088"]))
        - 5.0 * (after["badw"] - before["badw"])
    )


def allowed_cell(row: int, tidx: int, spec: H122Spec, row_rank: dict[int, float]) -> bool:
    target = TARGETS[tidx]
    if spec.condition == "all":
        return True
    if spec.condition == "sensor_ge":
        return row_rank.get(row, 0.0) >= spec.min_sensor_rank
    if spec.condition == "stage":
        return target in {"Q3", "S1", "S2", "S3", "S4"}
    raise ValueError(spec.condition)


def greedy_prune(
    start: np.ndarray,
    spec: H122Spec,
    row_rank: dict[int, float],
    basis_fit_df: pd.DataFrame,
    basis_fit_moves: np.ndarray,
    route_fit: h100mod.RouteBasisFit,
    cell: pd.DataFrame,
    h098_fit: h097mod.ResponseFit,
    fit: h115mod.CurvatureFit,
    pool: pd.DataFrame,
    bad_axes: pd.DataFrame,
    bad_moves: np.ndarray,
    good_moves: np.ndarray,
    axes: dict[str, object],
) -> tuple[np.ndarray, pd.DataFrame]:
    move_mat = start.copy()
    removed = []
    for step in range(spec.max_remove):
        active = list(zip(*np.where(np.abs(move_mat) > 1.0e-12)))
        if len(active) <= spec.min_remaining_cells:
            break
        before = evaluate_matrix(move_mat, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
        best = None
        for row, tidx in active:
            row_i = int(row)
            tidx_i = int(tidx)
            if not allowed_cell(row_i, tidx_i, spec, row_rank):
                continue
            tmp = move_mat.copy()
            removed_move = float(tmp[row_i, tidx_i])
            tmp[row_i, tidx_i] = 0.0
            after = evaluate_matrix(tmp, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
            score = remove_delta_score(after, before)
            if best is None or score > best["remove_score"]:
                best = {
                    "step": step + 1,
                    "row": row_i,
                    "target_index": tidx_i,
                    "target": TARGETS[tidx_i],
                    "removed_move": removed_move,
                    "sensor_rank": row_rank.get(row_i, 0.0),
                    "remove_score": score,
                    **{f"after_{key}": value for key, value in after.items()},
                    **{f"delta_{key}": after[key] - before[key] for key in after},
                }
        if best is None or float(best["remove_score"]) < spec.min_remove_score:
            break
        move_mat[int(best["row"]), int(best["target_index"])] = 0.0
        removed.append(best)
    return move_mat, pd.DataFrame(removed)


def make_selected_cells(move_mat: np.ndarray, h118_sel: pd.DataFrame) -> pd.DataFrame:
    selected = h118_sel.copy()
    selected["row"] = selected["row"].astype(int)
    selected["target_index"] = selected["target_index"].astype(int)
    selected["h122_actual_move"] = [
        float(move_mat[int(row), int(tidx)])
        for row, tidx in zip(selected["row"], selected["target_index"])
    ]
    selected = selected[np.abs(selected["h122_actual_move"].to_numpy(dtype=np.float64)) > 1.0e-12].copy()
    selected["h112_move"] = selected["h122_actual_move"]
    selected["h097_move_col"] = "h112_move"
    selected = selected.sort_values(["row", "target_index"]).reset_index(drop=True)
    return selected


def run() -> None:
    cleanup_previous_outputs()
    pool, _public, sample, base_prob, cell, h098_fit, route_fit, basis_fit_df, basis_fit_moves, bad_axes, bad_moves, good_moves, axes, fit, model_scores, props = h118mod.prepare_context()
    shape = base_prob.shape
    move_h118 = h115mod.load_previous_move(sample, base_prob, "submission_h118_forbiddenveto_*_uploadsafe.csv").reshape(shape)
    h118_sel = load_selected(
        "hitl/h118_forbidden_veto_assignment_hsjepa/h118_selected_cells.csv",
        "hitl/h118_forbidden_veto_assignment_hsjepa/h118_decision.csv",
    )
    row_sensor = pd.read_csv("hitl/h120_toxic_posterior_row_sensor_hsjepa/h120_row_sensor.csv")
    row_rank = dict(zip(row_sensor["row"].astype(int), row_sensor["h120_row_sensor_rank"].astype(float)))
    previous = {
        "h118": move_h118,
        "h121": h115mod.load_previous_move(sample, base_prob, "submission_h121_rowsensorpart_*_uploadsafe.csv"),
        "h120": h115mod.load_previous_move(sample, base_prob, "submission_h120_toxrow_*_uploadsafe.csv"),
        "h115": h115mod.load_previous_move(sample, base_prob, "submission_h115_curvature_*_uploadsafe.csv"),
        "h114": h115mod.load_previous_move(sample, base_prob, "submission_h114_nullspace_*_uploadsafe.csv"),
        "h112": h115mod.load_previous_move(sample, base_prob, "submission_h112_residualtox_*_uploadsafe.csv"),
    }

    candidate_rows = []
    selected_frames = []
    removed_frames = []
    for spec in candidate_specs():
        move_mat, removed = greedy_prune(
            move_h118,
            spec,
            row_rank,
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
        evald = evaluate_matrix(move_mat, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
        if removed.empty:
            continue
        if evald["badw"] > spec.max_bad_weighted_pos or evald["badmax"] > spec.max_bad_max_pos:
            continue
        if evald["h088"] > spec.max_h088_cos or evald["margin"] < spec.min_good_margin:
            continue
        if evald["route"] > spec.route_pred_cap or evald["h098"] > spec.h098_pred_cap:
            continue
        selected = make_selected_cells(move_mat, h118_sel)
        if selected.empty:
            continue
        prob = materialize(base_prob, move_mat)
        if int((np.abs(prob - base_prob) > TOL).sum()) == 0:
            continue
        hash_id = short_hash(prob)
        candidate_id = safe_id(f"h122_{spec.name}_{hash_id}", 128)
        path = OUT / f"submission_{candidate_id}.csv"
        h085mod.write_submission(sample, prob, path)
        axis = h102mod.cumulative_axis_metrics(move_mat.reshape(-1), bad_axes, bad_moves, good_moves)
        diag = {
            "h118_zero_curv": -0.0002616634510263019,
            "h118_curv_pred_delta_vs_h057": evald["curv_marg"] - 0.0002616634510263019,
            "h118_curv_marginal_vs_zero": evald["curv_marg"],
            "h118_mean_forbidden_same": float(selected.get("h117_forbidden_same", pd.Series([0.0])).astype(float).mean()),
            "h118_max_forbidden_same": float(selected.get("h117_forbidden_same", pd.Series([0.0])).astype(float).max()),
            "h118_mean_forbidden_pressure": float(selected.get("h117_forbidden_pressure", pd.Series([0.0])).astype(float).mean()),
            "h118_mean_veto_score": float(selected.get("h118_forbidden_veto_score", pd.Series([1.0])).astype(float).mean()),
            "h118_selected_rows": int(selected["row"].nunique()),
            "h122_removed_cells": int(len(removed)),
            "h122_removed_rows": int(removed["row"].nunique()),
            "h122_removed_mean_sensor_rank": float(removed["sensor_rank"].mean()),
            "h122_removed_mean_score": float(removed["remove_score"].mean()),
            "h122_removed_targets": ";".join(f"{k}:{v}" for k, v in removed["target"].value_counts().to_dict().items()),
        }
        metrics = h118mod.evaluate_candidate(
            candidate_id,
            prob,
            move_mat,
            selected,
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
        metrics["h122_condition"] = spec.condition
        metrics["h122_worldview"] = spec.worldview
        metrics["h122_fit_feature_set"] = fit.feature_set
        metrics["h122_fit_alpha"] = fit.alpha
        metrics["h122_fit_score"] = fit.score
        metrics["h122_score"] = (
            340.0 * (-float(metrics["route_basis_pred_delta_vs_h057"]))
            + 160.0 * (-float(metrics["model_pred_delta_vs_h057"]))
            + 100.0 * (-float(metrics["h118_curv_marginal_vs_zero"]))
            + 0.16 * float(metrics["h102_cum_good_bad_margin"])
            + 0.11 * max(-float(metrics["h102_cum_h088_axis_cos"]), 0.0)
            + 0.12 * float(metrics["selected_mean_residual_safety"])
            + 0.16 * float(metrics["selected_mean_residual_gap"])
            - 0.16 * float(metrics["selected_mean_residual_toxicity"])
            - 0.003 * max(0.0, 24.0 - float(metrics["selected_cells"]))
            - 20.0 * max(float(metrics["hard_diag_delta_vs_h057"]), 0.0)
        )
        candidate_rows.append(metrics)
        selected2 = selected.copy()
        if "candidate_id" in selected2.columns:
            selected2 = selected2.drop(columns=["candidate_id"])
        selected2.insert(0, "candidate_id", candidate_id)
        selected_frames.append(selected2)
        rem2 = removed.copy()
        rem2.insert(0, "candidate_id", candidate_id)
        removed_frames.append(rem2)

    candidates = pd.DataFrame(candidate_rows)
    row_sensor.to_csv(OUT / "h122_row_sensor.csv", index=False)
    model_scores.to_csv(OUT / "h122_curvature_model_scores.csv", index=False)
    if candidates.empty:
        report = """# H122 Action-Prune Equation Solver HS-JEPA

No candidate was promoted.
"""
        (OUT / "h122_report.md").write_text(report, encoding="utf-8")
        print("H122 promoted no candidate")
        return

    candidates = candidates.sort_values(["h122_score", "route_basis_pred_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True)
    selected = candidates.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"submission_h122_pruneeq_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)
    decision = {
        "decision": "promote_h122_action_prune_equation_solver",
        "selected_candidate_id": selected["candidate_id"],
        "root_uploadsafe_path": str(root_path),
        "worldview": selected["h122_worldview"],
        **selected,
        **{f"root_{key}": value for key, value in validation.items()},
    }
    candidates.to_csv(OUT / "h122_candidates.csv", index=False)
    pd.concat(selected_frames, ignore_index=True).to_csv(OUT / "h122_selected_cells.csv", index=False)
    pd.concat(removed_frames, ignore_index=True).to_csv(OUT / "h122_removed_cells.csv", index=False)
    pd.DataFrame([decision]).to_csv(OUT / "h122_decision.csv", index=False)

    cols = [
        "candidate_id",
        "spec_name",
        "h122_condition",
        "selected_cells",
        "changed_rows_vs_h057",
        "Q1_changed_vs_h057",
        "Q2_changed_vs_h057",
        "Q3_changed_vs_h057",
        "S1_changed_vs_h057",
        "S2_changed_vs_h057",
        "S3_changed_vs_h057",
        "S4_changed_vs_h057",
        "model_pred_delta_vs_h057",
        "route_basis_pred_delta_vs_h057",
        "h118_curv_marginal_vs_zero",
        "h102_cum_h088_axis_cos",
        "h102_cum_good_bad_margin",
        "selected_mean_residual_toxicity",
        "selected_mean_residual_safety",
        "selected_mean_residual_gap",
        "h122_removed_cells",
        "h122_removed_rows",
        "h122_removed_mean_sensor_rank",
        "h122_removed_targets",
        "h122_score",
        "file",
    ]
    report = f"""# H122 Action-Prune Equation Solver HS-JEPA

Question: is the safest action operation a replacement, or deletion of
public-toxic cells from H118?

Candidates:

{md_table(candidates[cols], 20)}

Decision:

{md_table(pd.DataFrame([decision]), 1)}

Interpretation rule:

- If H122 improves, the safe assignment field is formed by pruning toxic H118
  actions; H120 is useful mostly as a sensor, not a replacement action.
- If H121 improves more, removed high-sensor rows still need stage replacement.
- If H118 improves more, the pruning equation overfit local stress axes.
"""
    (OUT / "h122_report.md").write_text(report, encoding="utf-8")
    print("H122 selected candidate")
    print(candidates[cols].head(10).to_string(index=False))
    print("\nDecision")
    print(pd.DataFrame([decision])[["decision", "selected_candidate_id", "root_uploadsafe_path", "root_upload_safe"]].to_string(index=False))


if __name__ == "__main__":
    run()
