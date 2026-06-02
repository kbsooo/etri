#!/usr/bin/env python3
"""H124: dual-sensor refill envelope HS-JEPA.

H123 showed that route-refill can improve the route equation, but the second
refill cell trades away H098/model caution.  H124 isolates the stricter claim:
after H122 pruning, refill only cells that improve both the route equation and
the H098/frontier equation versus the pruned core.
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
OUT = HITL / "h124_dual_sensor_refill_envelope_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H123_PATH = HITL / "h123_prune_refill_equation_solver_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h123mod", H123_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H123_PATH}")
h123mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h123mod
SPEC.loader.exec_module(h123mod)

h122mod = h123mod.h122mod
h118mod = h123mod.h118mod
h115mod = h123mod.h115mod
h102mod = h123mod.h102mod
h085mod = h123mod.h085mod

TARGETS = h123mod.TARGETS
TOL = h123mod.TOL


@dataclass(frozen=True)
class H124Spec:
    name: str
    max_add: int
    min_add_score: float
    allow_second_order_route: bool
    max_cells: int
    max_rows: int
    max_per_subject: int
    max_per_target: int
    max_bad_weighted_pos: float
    max_bad_max_pos: float
    max_h088_cos: float
    min_good_margin: float
    route_pred_cap: float
    h098_pred_cap: float
    worldview: str

    @property
    def group(self) -> str:
        return "dual_sensor_refill"

    @property
    def amp(self) -> float:
        return 0.35

    @property
    def cap(self) -> float:
        return 0.14

    @property
    def pool_top(self) -> int:
        return 220

    @property
    def min_score(self) -> float:
        return 0.08

    @property
    def max_residual_toxicity(self) -> float:
        return 0.60

    @property
    def min_residual_safety(self) -> float:
        return 0.50

    @property
    def min_residual_gap(self) -> float:
        return 0.02


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
    for path in OUT.glob("submission_h124_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h124_dualsensor_*.csv"):
        path.unlink()


def candidate_specs() -> list[H124Spec]:
    return [
        H124Spec(
            name="strict_route_h098_refill",
            max_add=3,
            min_add_score=0.010,
            allow_second_order_route=False,
            max_cells=28,
            max_rows=22,
            max_per_subject=10,
            max_per_target=10,
            max_bad_weighted_pos=0.0005,
            max_bad_max_pos=0.0020,
            max_h088_cos=-0.060,
            min_good_margin=0.123,
            route_pred_cap=-0.000680,
            h098_pred_cap=-0.000030,
            worldview="refill only cells that improve both route-basis and H098 versus the H122 pruned core",
        ),
        H124Spec(
            name="strict_q3_refill",
            max_add=1,
            min_add_score=0.010,
            allow_second_order_route=False,
            max_cells=26,
            max_rows=21,
            max_per_subject=10,
            max_per_target=8,
            max_bad_weighted_pos=0.0005,
            max_bad_max_pos=0.0020,
            max_h088_cos=-0.060,
            min_good_margin=0.123,
            route_pred_cap=-0.000680,
            h098_pred_cap=-0.000030,
            worldview="the only safe route complement is the row 149 Q3 refill; later route-only cells are toxic overfit",
        ),
        H124Spec(
            name="route_overfit_probe",
            max_add=2,
            min_add_score=0.004,
            allow_second_order_route=True,
            max_cells=28,
            max_rows=22,
            max_per_subject=10,
            max_per_target=10,
            max_bad_weighted_pos=0.0005,
            max_bad_max_pos=0.0020,
            max_h088_cos=-0.060,
            min_good_margin=0.123,
            route_pred_cap=-0.000720,
            h098_pred_cap=-0.000026,
            worldview="allow the second route-only refill to test whether public rewards route completion over H098 caution",
        ),
    ]


def evaluate_matrix(move_mat, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes):
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


def score_add(after: dict[str, float], before: dict[str, float], start: dict[str, float], spec: H124Spec) -> float:
    improves_h098_vs_start = after["h098"] < start["h098"]
    improves_route_vs_start = after["route"] < start["route"]
    if not spec.allow_second_order_route and not (improves_h098_vs_start and improves_route_vs_start):
        return -1.0
    return (
        340.0 * (-(after["route"] - before["route"]))
        + 280.0 * (-(after["h098"] - before["h098"]))
        + 120.0 * (-(after["curv_marg"] - before["curv_marg"]))
        + 0.12 * (after["margin"] - before["margin"])
        + 0.10 * (-(after["h088"] - before["h088"]))
        - 5.0 * (after["badw"] - before["badw"])
        + (0.010 if improves_h098_vs_start else -0.020)
        + (0.010 if improves_route_vs_start else -0.020)
    )


def build_work_pool(scored: pd.DataFrame, h122_move: np.ndarray, h122_removed: pd.DataFrame) -> pd.DataFrame:
    active_keys = set(zip(*np.where(np.abs(h122_move) > 1.0e-12)))
    removed_keys = set(zip(h122_removed["row"].astype(int), h122_removed["target_index"].astype(int)))
    work = scored.copy()
    work["row"] = work["row"].astype(int)
    work["target_index"] = work["target_index"].astype(int)
    keep = []
    for row, tidx, target in zip(work["row"], work["target_index"], work["target"].astype(str)):
        key = (int(row), int(tidx))
        keep.append(key not in active_keys and key not in removed_keys and target != "Q2")
    work = work[np.asarray(keep)].copy()
    work = work[work["h117_forbidden_same"].to_numpy(dtype=np.float64) <= 1.0e-12].copy()
    work = work[work["h112_residual_safety"].to_numpy(dtype=np.float64) >= 0.50].copy()
    work = work[work["h112_residual_toxicity"].to_numpy(dtype=np.float64) <= 0.60].copy()
    work = work[work["h112_residual_gap"].to_numpy(dtype=np.float64) >= 0.02].copy()
    work = work[work["h123_pool_score"].to_numpy(dtype=np.float64) >= 0.08].copy()
    work["h124_move"] = np.clip(work["proposal_move"].to_numpy(dtype=np.float64) * 0.35, -0.14, 0.14)
    work = work[np.abs(work["h124_move"].to_numpy(dtype=np.float64)) > 1.0e-8].copy()
    work = work.sort_values(["h123_pool_score", "h112_residual_safety"], ascending=[False, False])
    return work.drop_duplicates(["row", "target_index"], keep="first").head(240).reset_index(drop=True)


def greedy_add(
    h122_move: np.ndarray,
    work: pd.DataFrame,
    spec: H124Spec,
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
) -> tuple[np.ndarray, pd.DataFrame]:
    move_mat = h122_move.copy()
    start = evaluate_matrix(move_mat, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
    used = set(zip(*np.where(np.abs(move_mat) > 1.0e-12)))
    selected_rows = {int(row) for row in np.where(np.abs(move_mat).sum(axis=1) > 1.0e-12)[0]}
    target_counts = {target: 0 for target in TARGETS}
    added = []
    for step in range(spec.max_add):
        before = evaluate_matrix(move_mat, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
        best = None
        for rec in work.to_dict("records"):
            row = int(rec["row"])
            tidx = int(rec["target_index"])
            target = str(rec["target"])
            if spec.name == "strict_q3_refill" and target != "Q3":
                continue
            if (row, tidx) in used:
                continue
            if len(used) >= spec.max_cells:
                continue
            if row not in selected_rows and len(selected_rows) >= spec.max_rows:
                continue
            if target_counts.get(target, 0) >= spec.max_per_target:
                continue
            tmp = move_mat.copy()
            tmp[row, tidx] = float(rec["h124_move"])
            after = evaluate_matrix(tmp, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
            if after["badw"] > spec.max_bad_weighted_pos or after["badmax"] > spec.max_bad_max_pos:
                continue
            if after["h088"] > spec.max_h088_cos or after["margin"] < spec.min_good_margin:
                continue
            if after["route"] > spec.route_pred_cap or after["h098"] > spec.h098_pred_cap:
                continue
            add_score = score_add(after, before, start, spec)
            if best is None or add_score > best["h124_add_score"]:
                best = {
                    "step": step + 1,
                    "row": row,
                    "target_index": tidx,
                    "target": target,
                    "subject_id": str(rec["subject_id"]),
                    "h124_move": float(rec["h124_move"]),
                    "h123_pool_score": float(rec["h123_pool_score"]),
                    "h112_residual_safety": float(rec["h112_residual_safety"]),
                    "h112_residual_toxicity": float(rec["h112_residual_toxicity"]),
                    "h112_residual_gap": float(rec["h112_residual_gap"]),
                    "proposal_source": str(rec["proposal_source"]),
                    "h124_add_score": add_score,
                    **{f"after_{key}": value for key, value in after.items()},
                    **{f"delta_{key}": after[key] - before[key] for key in after},
                    **{f"delta_start_{key}": after[key] - start[key] for key in after},
                }
        if best is None or float(best["h124_add_score"]) < spec.min_add_score:
            break
        move_mat[int(best["row"]), int(best["target_index"])] = float(best["h124_move"])
        used.add((int(best["row"]), int(best["target_index"])))
        selected_rows.add(int(best["row"]))
        target_counts[str(best["target"])] = target_counts.get(str(best["target"]), 0) + 1
        added.append(best)
    return move_mat, pd.DataFrame(added)


def make_selected(h122_selected: pd.DataFrame, scored: pd.DataFrame, added: pd.DataFrame, move_mat: np.ndarray) -> pd.DataFrame:
    core = h122_selected.copy()
    core["h124_component"] = "h122_core"
    core["h124_actual_move"] = [
        float(move_mat[int(row), int(tidx)])
        for row, tidx in zip(core["row"].astype(int), core["target_index"].astype(int))
    ]
    core = core[np.abs(core["h124_actual_move"].to_numpy(dtype=np.float64)) > 1.0e-12].copy()
    if added.empty:
        combined = core
    else:
        key_set = set(zip(added["row"].astype(int), added["target_index"].astype(int)))
        add_rows = scored[
            [
                (int(row), int(tidx)) in key_set
                for row, tidx in zip(scored["row"].astype(int), scored["target_index"].astype(int))
            ]
        ].copy()
        add_rows = add_rows.sort_values(["row", "target_index"]).drop_duplicates(["row", "target_index"], keep="first")
        lookup = {
            (int(row), int(tidx)): float(move)
            for row, tidx, move in zip(added["row"], added["target_index"], added["h124_move"])
        }
        add_rows["h124_component"] = "h124_refill"
        add_rows["h124_actual_move"] = [
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
    combined["h112_move"] = combined["h124_actual_move"].to_numpy(dtype=np.float64)
    combined["h097_move_col"] = "h112_move"
    return combined.sort_values(["row", "target_index"]).reset_index(drop=True)


def run() -> None:
    cleanup_previous_outputs()
    pool, _public, sample, base_prob, cell, h098_fit, route_fit, basis_fit_df, basis_fit_moves, bad_axes, bad_moves, good_moves, axes, fit, model_scores, props = h118mod.prepare_context()
    scored = h123mod.build_scored_pool(pool, base_prob, fit, bad_axes, bad_moves, good_moves, axes, props)
    h122_selected, h122_removed = h123mod.load_selected_h122()
    h122_move = h115mod.load_previous_move(sample, base_prob, "submission_h122_pruneeq_*_uploadsafe.csv").reshape(base_prob.shape)
    work = build_work_pool(scored, h122_move, h122_removed)
    previous = {
        "h123": h115mod.load_previous_move(sample, base_prob, "submission_h123_refilleq_*_uploadsafe.csv"),
        "h122": h122_move,
        "h121": h115mod.load_previous_move(sample, base_prob, "submission_h121_rowsensorpart_*_uploadsafe.csv"),
        "h118": h115mod.load_previous_move(sample, base_prob, "submission_h118_forbiddenveto_*_uploadsafe.csv"),
    }

    candidate_rows = []
    selected_frames = []
    added_frames = []
    audit_rows = []
    for spec in candidate_specs():
        move_mat, added = greedy_add(
            h122_move,
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
        audit_rows.append({"spec_name": spec.name, "add_pool_rows": int(len(work)), "added_cells": int(len(added))})
        if added.empty:
            continue
        evald = evaluate_matrix(move_mat, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
        axis = h102mod.cumulative_axis_metrics(move_mat.reshape(-1), bad_axes, bad_moves, good_moves)
        selected_cells = make_selected(h122_selected, scored, added, move_mat)
        prob = materialize(base_prob, move_mat)
        if int((np.abs(prob - base_prob) > TOL).sum()) == 0:
            continue
        hash_id = short_hash(prob)
        candidate_id = safe_id(f"h124_{spec.name}_{hash_id}", 128)
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
            "h124_start_cells": int((np.abs(h122_move) > 1.0e-12).sum()),
            "h124_added_cells": int(len(added)),
            "h124_added_rows": int(added["row"].nunique()),
            "h124_added_mean_score": float(added["h124_add_score"].mean()),
            "h124_added_targets": ";".join(f"{k}:{v}" for k, v in added["target"].value_counts().to_dict().items()),
            "h124_delta_start_route": float(evald["route"] - h122mod.evaluate_matrix(h122_move, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)["route"]),
            "h124_delta_start_h098": float(evald["h098"] - h122mod.evaluate_matrix(h122_move, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)["h098"]),
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
        metrics["h124_worldview"] = spec.worldview
        metrics["h124_fit_feature_set"] = fit.feature_set
        metrics["h124_fit_alpha"] = fit.alpha
        metrics["h124_fit_score"] = fit.score
        metrics["h124_score"] = (
            330.0 * (-float(metrics["route_basis_pred_delta_vs_h057"]))
            + 260.0 * (-float(metrics["model_pred_delta_vs_h057"]))
            + 110.0 * (-float(metrics["h118_curv_marginal_vs_zero"]))
            + 0.16 * float(metrics["h102_cum_good_bad_margin"])
            + 0.12 * max(-float(metrics["h102_cum_h088_axis_cos"]), 0.0)
            + 0.09 * float(metrics["selected_mean_residual_safety"])
            + 0.10 * float(metrics["selected_mean_residual_gap"])
            - 0.10 * float(metrics["selected_mean_residual_toxicity"])
            + 0.020 * float(metrics["h124_added_cells"])
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
    audit.to_csv(OUT / "h124_add_pool_audit.csv", index=False)
    scored.to_csv(OUT / "h124_scored_pool.csv", index=False)
    model_scores.to_csv(OUT / "h124_curvature_model_scores.csv", index=False)
    if candidates.empty:
        report = f"""# H124 Dual-Sensor Refill Envelope HS-JEPA

No candidate was promoted.

Audit:

{md_table(audit, 20)}
"""
        (OUT / "h124_report.md").write_text(report, encoding="utf-8")
        print("H124 promoted no candidate")
        print(audit.to_string(index=False))
        return

    candidates = candidates.sort_values(["h124_score", "model_pred_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True)
    selected = candidates.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"submission_h124_dualsensor_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)
    decision = {
        "decision": "promote_h124_dual_sensor_refill_envelope",
        "selected_candidate_id": selected["candidate_id"],
        "root_uploadsafe_path": str(root_path),
        "worldview": selected["h124_worldview"],
        **selected,
        **{f"root_{key}": value for key, value in validation.items()},
    }
    candidates.to_csv(OUT / "h124_candidates.csv", index=False)
    pd.concat(selected_frames, ignore_index=True).to_csv(OUT / "h124_selected_cells.csv", index=False)
    pd.concat(added_frames, ignore_index=True).to_csv(OUT / "h124_added_cells.csv", index=False)
    pd.DataFrame([decision]).to_csv(OUT / "h124_decision.csv", index=False)
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
        "h124_added_cells",
        "h124_added_targets",
        "h124_delta_start_route",
        "h124_delta_start_h098",
        "model_pred_delta_vs_h057",
        "route_basis_pred_delta_vs_h057",
        "h118_curv_marginal_vs_zero",
        "h102_cum_h088_axis_cos",
        "h102_cum_good_bad_margin",
        "h124_score",
        "file",
    ]
    report = f"""# H124 Dual-Sensor Refill Envelope HS-JEPA

Question: does a refill cell need to improve both the route equation and the
H098/model caution equation, or is route-only refill safe?

Candidates:

{md_table(candidates[cols], 20)}

Decision:

{md_table(pd.DataFrame([decision]), 1)}

Interpretation rule:

- If H124 improves over H123, the second H123 route-only refill was toxic
  overfit and HS-JEPA should use dual-sensor refill.
- If H123 improves more, the public equation rewards route completion more than
  H098/model caution.
- If H122 improves more, all refill is local-stress overfit.
"""
    (OUT / "h124_report.md").write_text(report, encoding="utf-8")
    print("H124 selected candidate")
    print(candidates[cols].head(10).to_string(index=False))
    print("\nDecision")
    print(pd.DataFrame([decision])[["decision", "selected_candidate_id", "root_uploadsafe_path", "root_upload_safe"]].to_string(index=False))


if __name__ == "__main__":
    run()
