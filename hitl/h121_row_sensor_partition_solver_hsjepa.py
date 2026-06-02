#!/usr/bin/env python3
"""H121: row-sensor partition solver HS-JEPA.

H119 rejected H085 posterior as a direct action target.  H120 kept H085 as a
row-level public-sensitive sensor and decoded action through residual stage
assignments.  H121 uses that sensor as a partition variable:

    low toxic-posterior rows  -> keep H118 forbidden-veto assignment
    high toxic-posterior rows -> remove H118 action and use H120 stage bridge

The test is whether public/private action safety is row-regime dependent rather
than a single global assignment rule.
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
OUT = HITL / "h121_row_sensor_partition_solver_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H120_PATH = HITL / "h120_toxic_posterior_row_sensor_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h120mod", H120_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H120_PATH}")
h120mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h120mod
SPEC.loader.exec_module(h120mod)

h118mod = h120mod.h118mod
h115mod = h120mod.h115mod
h112mod = h120mod.h112mod
h102mod = h120mod.h102mod
h100mod = h120mod.h100mod
h097mod = h120mod.h097mod
h085mod = h120mod.h085mod

TARGETS = h120mod.TARGETS
TOL = h120mod.TOL


@dataclass(frozen=True)
class H121Spec:
    name: str
    threshold: float
    mode: str
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
        return self.mode


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
    for path in OUT.glob("submission_h121_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h121_rowsensorpart_*.csv"):
        path.unlink()


def route_pred(move_flat: np.ndarray, basis_fit_df: pd.DataFrame, basis_fit_moves: np.ndarray, route_fit: h100mod.RouteBasisFit) -> float:
    return h100mod.predict_candidate_delta(move_flat, basis_fit_df, basis_fit_moves, route_fit)


def h098_pred(move_flat: np.ndarray, cell: pd.DataFrame, h098_fit: h097mod.ResponseFit) -> float:
    return h097mod.predict_candidate_delta(move_flat, cell, h098_fit)


def curvature_pred(move_mat: np.ndarray, fit: h115mod.CurvatureFit, pool: pd.DataFrame, bad_axes: pd.DataFrame, bad_moves: np.ndarray, good_moves: np.ndarray, axes: dict[str, object]) -> float:
    return h115mod.predict_curvature(move_mat, fit, pool, bad_axes, bad_moves, good_moves, axes)


def candidate_specs() -> list[H121Spec]:
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
        max_residual_toxicity=0.70,
        min_residual_safety=0.40,
        max_bad_weighted_pos=0.001,
        max_bad_max_pos=0.004,
        max_h088_cos=-0.020,
        min_good_margin=0.095,
        route_pred_cap=-0.000540,
        h098_pred_cap=-0.000020,
    )
    return [
        H121Spec(
            name="partition_sensor_ge070",
            threshold=0.70,
            mode="replace_high_sensor_rows",
            worldview="high H085 toxic-posterior rows use H120 stage action; other rows keep H118 forbidden-veto action",
            **common,
        ),
        H121Spec(
            name="partition_sensor_ge085",
            threshold=0.85,
            mode="replace_high_sensor_rows",
            worldview="only the highest H085 toxic-posterior rows override H118 with H120 stage action",
            **common,
        ),
        H121Spec(
            name="partition_h120rows_only",
            threshold=1.01,
            mode="replace_h120_rows",
            min_good_margin=0.070,
            max_h088_cos=-0.003,
            route_pred_cap=-0.000540,
            h098_pred_cap=-0.000010,
            worldview="only rows explicitly selected by H120 are routed to the stage bridge",
            **{k: v for k, v in common.items() if k not in {"min_good_margin", "max_h088_cos", "route_pred_cap", "h098_pred_cap"}},
        ),
        H121Spec(
            name="partition_half_add_new",
            threshold=1.01,
            mode="half_add_new_h120_cells",
            min_good_margin=0.080,
            max_h088_cos=-0.003,
            route_pred_cap=-0.000540,
            h098_pred_cap=-0.000008,
            worldview="H120 new cells are additive weak row-sensor corrections on top of H118",
            **{k: v for k, v in common.items() if k not in {"min_good_margin", "max_h088_cos", "route_pred_cap", "h098_pred_cap"}},
        ),
    ]


def load_selected(path: str, decision_path: str, candidate_col: str = "selected_candidate_id") -> pd.DataFrame:
    selected = pd.read_csv(path)
    decision = pd.read_csv(decision_path)
    candidate_id = str(decision[candidate_col].iloc[0])
    return selected[selected["candidate_id"].astype(str) == candidate_id].copy()


def overlay(base: np.ndarray, add: np.ndarray) -> np.ndarray:
    out = base.copy()
    mask = np.abs(add) > 1.0e-12
    out[mask] = add[mask]
    return out


def replace_high_sensor_rows(base: np.ndarray, add: np.ndarray, rows: set[int]) -> np.ndarray:
    out = base.copy()
    if rows:
        out[list(rows), :] = 0.0
    return overlay(out, add)


def half_add_new(base: np.ndarray, add: np.ndarray) -> np.ndarray:
    out = base.copy()
    mask = (np.abs(base) < 1.0e-12) & (np.abs(add) > 1.0e-12)
    out[mask] = 0.5 * add[mask]
    return out


def make_selected_cells(move_mat: np.ndarray, h118_sel: pd.DataFrame, h120_sel: pd.DataFrame) -> pd.DataFrame:
    frames = []
    for source, df in [("h118_partition_source", h118_sel), ("h120_partition_source", h120_sel)]:
        tmp = df.copy()
        tmp["h121_source"] = source
        frames.append(tmp)
    selected = pd.concat(frames, ignore_index=True)
    selected["row"] = selected["row"].astype(int)
    selected["target_index"] = selected["target_index"].astype(int)
    selected["h121_abs_move"] = [
        abs(float(move_mat[int(row), int(tidx)]))
        for row, tidx in zip(selected["row"], selected["target_index"])
    ]
    selected = selected[selected["h121_abs_move"] > 1.0e-12].copy()
    selected["h121_actual_move"] = [
        float(move_mat[int(row), int(tidx)])
        for row, tidx in zip(selected["row"], selected["target_index"])
    ]
    selected["h112_move"] = selected["h121_actual_move"]
    selected["h097_move_col"] = "h112_move"
    selected = selected.sort_values(["row", "target_index", "h121_source"]).drop_duplicates(["row", "target"], keep="last")
    selected = selected.sort_values(["row", "target_index"]).reset_index(drop=True)
    return selected


def run() -> None:
    cleanup_previous_outputs()
    pool, _public, sample, base_prob, cell, h098_fit, route_fit, basis_fit_df, basis_fit_moves, bad_axes, bad_moves, good_moves, axes, fit, model_scores, props = h118mod.prepare_context()
    shape = base_prob.shape
    move_h118 = h115mod.load_previous_move(sample, base_prob, "submission_h118_forbiddenveto_*_uploadsafe.csv").reshape(shape)
    move_h120 = h115mod.load_previous_move(sample, base_prob, "submission_h120_toxrow_0b84c821_uploadsafe.csv").reshape(shape)
    h118_sel = load_selected(
        "hitl/h118_forbidden_veto_assignment_hsjepa/h118_selected_cells.csv",
        "hitl/h118_forbidden_veto_assignment_hsjepa/h118_decision.csv",
    )
    h120_sel = load_selected(
        "hitl/h120_toxic_posterior_row_sensor_hsjepa/h120_selected_cells.csv",
        "hitl/h120_toxic_posterior_row_sensor_hsjepa/h120_decision.csv",
    )
    row_sensor = pd.read_csv("hitl/h120_toxic_posterior_row_sensor_hsjepa/h120_row_sensor.csv")
    row_rank = dict(zip(row_sensor["row"].astype(int), row_sensor["h120_row_sensor_rank"].astype(float)))
    previous = {
        "h118": move_h118,
        "h120": move_h120,
        "h115": h115mod.load_previous_move(sample, base_prob, "submission_h115_curvature_*_uploadsafe.csv"),
        "h114": h115mod.load_previous_move(sample, base_prob, "submission_h114_nullspace_*_uploadsafe.csv"),
        "h112": h115mod.load_previous_move(sample, base_prob, "submission_h112_residualtox_*_uploadsafe.csv"),
    }

    candidate_rows = []
    selected_frames = []
    for spec in candidate_specs():
        if spec.mode == "replace_high_sensor_rows":
            rows = {r for r, value in row_rank.items() if value >= spec.threshold}
            move_mat = replace_high_sensor_rows(move_h118, move_h120, rows)
        elif spec.mode == "replace_h120_rows":
            rows = set(h120_sel["row"].astype(int))
            move_mat = replace_high_sensor_rows(move_h118, move_h120, rows)
        elif spec.mode == "half_add_new_h120_cells":
            rows = set()
            move_mat = half_add_new(move_h118, move_h120)
        else:
            raise ValueError(spec.mode)

        axis = h102mod.cumulative_axis_metrics(move_mat.reshape(-1), bad_axes, bad_moves, good_moves)
        rpred = route_pred(move_mat.reshape(-1), basis_fit_df, basis_fit_moves, route_fit)
        cpred = h098_pred(move_mat.reshape(-1), cell, h098_fit)
        curv = curvature_pred(move_mat, fit, pool, bad_axes, bad_moves, good_moves, axes)
        if axis["h102_cum_bad_weighted_pos"] > spec.max_bad_weighted_pos:
            continue
        if axis["h102_cum_bad_max_pos"] > spec.max_bad_max_pos:
            continue
        if axis["h102_cum_h088_axis_cos"] > spec.max_h088_cos:
            continue
        if axis["h102_cum_good_bad_margin"] < spec.min_good_margin:
            continue
        if rpred > spec.route_pred_cap or cpred > spec.h098_pred_cap:
            continue

        selected = make_selected_cells(move_mat, h118_sel, h120_sel)
        if selected.empty:
            continue
        prob = materialize(base_prob, move_mat)
        if int((np.abs(prob - base_prob) > TOL).sum()) == 0:
            continue
        hash_id = short_hash(prob)
        candidate_id = safe_id(f"h121_{spec.name}_{hash_id}", 128)
        path = OUT / f"submission_{candidate_id}.csv"
        h085mod.write_submission(sample, prob, path)
        diag = {
            "h118_zero_curv": -0.0002616634510263019,
            "h118_curv_pred_delta_vs_h057": curv,
            "h118_curv_marginal_vs_zero": curv + 0.0002616634510263019,
            "h118_mean_forbidden_same": float(selected.get("h117_forbidden_same", pd.Series([0.0])).astype(float).mean()),
            "h118_max_forbidden_same": float(selected.get("h117_forbidden_same", pd.Series([0.0])).astype(float).max()),
            "h118_mean_forbidden_pressure": float(selected.get("h117_forbidden_pressure", pd.Series([0.0])).astype(float).mean()),
            "h118_mean_veto_score": float(selected.get("h118_forbidden_veto_score", pd.Series([1.0])).astype(float).mean()),
            "h118_selected_rows": int(selected["row"].nunique()),
            "h121_sensor_threshold": spec.threshold,
            "h121_partition_rows": int(len(rows)),
            "h121_removed_h118_rows": int(
                len({int(row) for row in np.where((np.abs(move_h118) > 1.0e-12).any(axis=1))[0]} & set(rows))
            ),
            "h121_removed_h118_cells": int(
                ((np.abs(move_h118) > 1.0e-12) & (np.abs(move_mat) < 1.0e-12)).sum()
            ),
            "h121_h118_cells_kept": int(((np.abs(move_h118) > 1.0e-12) & (np.abs(move_mat) > 1.0e-12)).sum()),
            "h121_h120_cells_used": int(((np.abs(move_h120) > 1.0e-12) & (np.abs(move_mat) > 1.0e-12)).sum()),
            "h121_mean_row_sensor_rank": float(selected.get("h120_row_sensor_rank", pd.Series([0.0])).fillna(0.0).astype(float).mean()),
            "h121_h085_action_align_rate": float(selected.get("h120_h085_action_align", pd.Series([0.0])).fillna(0.0).astype(float).mean()),
            "h121_h085_action_contra_rate": float(selected.get("h120_h085_action_contra", pd.Series([0.0])).fillna(0.0).astype(float).mean()),
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
        metrics["h121_mode"] = spec.mode
        metrics["h121_worldview"] = spec.worldview
        metrics["h121_fit_feature_set"] = fit.feature_set
        metrics["h121_fit_alpha"] = fit.alpha
        metrics["h121_fit_score"] = fit.score
        metrics["h121_score"] = (
            320.0 * (-float(metrics["route_basis_pred_delta_vs_h057"]))
            + 140.0 * (-float(metrics["model_pred_delta_vs_h057"]))
            + 110.0 * (-float(metrics["h118_curv_marginal_vs_zero"]))
            + 0.18 * float(metrics["selected_mean_residual_safety"])
            + 0.20 * float(metrics["selected_mean_residual_gap"])
            + 0.14 * float(metrics["h102_cum_good_bad_margin"])
            + 0.10 * max(-float(metrics["h102_cum_h088_axis_cos"]), 0.0)
            - 0.18 * float(metrics["selected_mean_residual_toxicity"])
            - 0.40 * max(float(metrics["h102_cum_bad_weighted_pos"]), 0.0)
            - 20.0 * max(float(metrics["hard_diag_delta_vs_h057"]), 0.0)
        )
        candidate_rows.append(metrics)
        selected2 = selected.copy()
        if "candidate_id" in selected2.columns:
            selected2 = selected2.drop(columns=["candidate_id"])
        selected2.insert(0, "candidate_id", candidate_id)
        selected_frames.append(selected2)

    candidates = pd.DataFrame(candidate_rows)
    row_sensor.to_csv(OUT / "h121_row_sensor.csv", index=False)
    model_scores.to_csv(OUT / "h121_curvature_model_scores.csv", index=False)
    if candidates.empty:
        report = """# H121 Row-Sensor Partition Solver HS-JEPA

No candidate was promoted.
"""
        (OUT / "h121_report.md").write_text(report, encoding="utf-8")
        print("H121 promoted no candidate")
        return

    candidates = candidates.sort_values(["h121_score", "route_basis_pred_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True)
    selected = candidates.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"submission_h121_rowsensorpart_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)
    decision = {
        "decision": "promote_h121_row_sensor_partition_solver",
        "selected_candidate_id": selected["candidate_id"],
        "root_uploadsafe_path": str(root_path),
        "worldview": selected["h121_worldview"],
        **selected,
        **{f"root_{key}": value for key, value in validation.items()},
    }
    candidates.to_csv(OUT / "h121_candidates.csv", index=False)
    pd.concat(selected_frames, ignore_index=True).to_csv(OUT / "h121_selected_cells.csv", index=False)
    pd.DataFrame([decision]).to_csv(OUT / "h121_decision.csv", index=False)

    cols = [
        "candidate_id",
        "spec_name",
        "h121_mode",
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
        "h102_cum_bad_weighted_pos",
        "h102_cum_h088_axis_cos",
        "h102_cum_good_bad_margin",
        "selected_mean_residual_toxicity",
        "selected_mean_residual_safety",
        "selected_mean_residual_gap",
        "h121_partition_rows",
        "h121_removed_h118_rows",
        "h121_removed_h118_cells",
        "h121_h118_cells_kept",
        "h121_h120_cells_used",
        "h121_score",
        "file",
    ]
    report = f"""# H121 Row-Sensor Partition Solver HS-JEPA

Question: can H120's toxic-posterior row sensor partition H118's large
forbidden-veto assignment into safe and unsafe row regimes?

Candidates:

{md_table(candidates[cols], 20)}

Decision:

{md_table(pd.DataFrame([decision]), 1)}

Interpretation rule:

- If H121 improves, H085's role is a regime partition variable over the action
  solver, not a direct posterior action.
- If H118 improves more, H120's high-sensor rows are not a useful override.
- If H120 improves more, high-sensor stage bridge should replace more of H118.
- If all lose, row-sensor partitioning is still diagnostic but not action-grade.
"""
    (OUT / "h121_report.md").write_text(report, encoding="utf-8")
    print("H121 selected candidate")
    print(candidates[cols].head(10).to_string(index=False))
    print("\nDecision")
    print(pd.DataFrame([decision])[["decision", "selected_candidate_id", "root_uploadsafe_path", "root_upload_safe"]].to_string(index=False))


if __name__ == "__main__":
    run()
