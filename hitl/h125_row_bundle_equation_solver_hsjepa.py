#!/usr/bin/env python3
"""H125: row-bundle equation solver HS-JEPA.

H124 makes refill safe at the single-cell level.  H125 asks whether public-safe
refill is actually a row/subject bundle: the same hidden human-state episode
may require several target corrections to move together.
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
OUT = HITL / "h125_row_bundle_equation_solver_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H124_PATH = HITL / "h124_dual_sensor_refill_envelope_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h124mod", H124_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H124_PATH}")
h124mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h124mod
SPEC.loader.exec_module(h124mod)

h123mod = h124mod.h123mod
h122mod = h124mod.h122mod
h118mod = h124mod.h118mod
h115mod = h124mod.h115mod
h102mod = h124mod.h102mod
h085mod = h124mod.h085mod

TARGETS = h123mod.TARGETS
TOL = h123mod.TOL


@dataclass(frozen=True)
class H125Spec:
    name: str
    bundle_kind: str
    max_add: int
    max_cells: int
    max_rows: int
    route_pred_cap: float
    h098_pred_cap: float
    max_h088_cos: float
    min_good_margin: float
    max_bad_weighted_pos: float
    max_bad_max_pos: float
    min_bundle_score: float
    worldview: str

    @property
    def group(self) -> str:
        return f"row_bundle_{self.bundle_kind}"

    @property
    def amp(self) -> float:
        return 0.35

    @property
    def cap(self) -> float:
        return 0.14

    @property
    def pool_top(self) -> int:
        return 240

    @property
    def max_per_subject(self) -> int:
        return 16

    @property
    def max_per_target(self) -> int:
        return 18

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
    for path in OUT.glob("submission_h125_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h125_rowbundle_*.csv"):
        path.unlink()


def candidate_specs() -> list[H125Spec]:
    return [
        H125Spec(
            name="id04_s1_bundle_closure",
            bundle_kind="id04_s1",
            max_add=1,
            max_cells=29,
            max_rows=23,
            route_pred_cap=-0.000700,
            h098_pred_cap=-0.000031,
            max_h088_cos=-0.052,
            min_good_margin=0.150,
            max_bad_weighted_pos=0.0005,
            max_bad_max_pos=0.0020,
            min_bundle_score=0.00020,
            worldview="id04 S1 is a hidden row bundle; H124 added two cells but left one safe S1 closure cell",
        ),
        H125Spec(
            name="id06_s2_margin_bundle",
            bundle_kind="id06_s2",
            max_add=4,
            max_cells=32,
            max_rows=26,
            route_pred_cap=-0.000695,
            h098_pred_cap=-0.000031,
            max_h088_cos=-0.040,
            min_good_margin=0.172,
            max_bad_weighted_pos=0.0005,
            max_bad_max_pos=0.0020,
            min_bundle_score=0.00100,
            worldview="id06 S2 cells form a compensating margin bundle after route/H098 refill",
        ),
        H125Spec(
            name="id06_stage_margin_bundle",
            bundle_kind="id06_stage",
            max_add=6,
            max_cells=34,
            max_rows=28,
            route_pred_cap=-0.000690,
            h098_pred_cap=-0.000031,
            max_h088_cos=-0.035,
            min_good_margin=0.180,
            max_bad_weighted_pos=0.0005,
            max_bad_max_pos=0.0020,
            min_bundle_score=0.00150,
            worldview="id06 has a broader S1/S2 margin episode that should move as a stage bundle",
        ),
        H125Spec(
            name="route_tail_plus_margin_bundle",
            bundle_kind="route_tail_margin",
            max_add=5,
            max_cells=33,
            max_rows=27,
            route_pred_cap=-0.000725,
            h098_pred_cap=-0.000026,
            max_h088_cos=-0.045,
            min_good_margin=0.165,
            max_bad_weighted_pos=0.0005,
            max_bad_max_pos=0.0020,
            min_bundle_score=0.00400,
            worldview="H123 route tail and H124 margin bundle are complementary pieces of one public-private equation",
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


def bundle_score(after: dict[str, float], before: dict[str, float]) -> float:
    return (
        330.0 * (-(after["route"] - before["route"]))
        + 250.0 * (-(after["h098"] - before["h098"]))
        + 95.0 * (-(after["curv_marg"] - before["curv_marg"]))
        + 0.18 * (after["margin"] - before["margin"])
        + 0.10 * (-(after["h088"] - before["h088"]))
        - 5.0 * (after["badw"] - before["badw"])
    )


def build_remaining_pool(scored: pd.DataFrame, h124_move: np.ndarray, h122_removed: pd.DataFrame) -> pd.DataFrame:
    active_keys = set(zip(*np.where(np.abs(h124_move) > 1.0e-12)))
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
    work["h125_move"] = np.clip(work["proposal_move"].to_numpy(dtype=np.float64) * 0.35, -0.14, 0.14)
    work = work[np.abs(work["h125_move"].to_numpy(dtype=np.float64)) > 1.0e-8].copy()
    return work.sort_values(["h123_pool_score", "h112_residual_safety"], ascending=[False, False]).drop_duplicates(["row", "target_index"]).reset_index(drop=True)


def spec_pool(work: pd.DataFrame, spec: H125Spec) -> pd.DataFrame:
    if spec.bundle_kind == "id04_s1":
        out = work[(work["subject_id"].astype(str) == "id04") & (work["target"].astype(str) == "S1")].copy()
        return out[out["row"].astype(int).isin([98, 101])].sort_values(["h123_pool_score"], ascending=False).head(spec.max_add)
    if spec.bundle_kind == "id06_s2":
        out = work[(work["subject_id"].astype(str) == "id06") & (work["target"].astype(str) == "S2")].copy()
        return out.sort_values(["h123_pool_score"], ascending=False).head(spec.max_add)
    if spec.bundle_kind == "id06_stage":
        out = work[(work["subject_id"].astype(str) == "id06") & (work["target"].astype(str).isin(["S1", "S2"]))].copy()
        return out.sort_values(["h123_pool_score"], ascending=False).head(spec.max_add)
    if spec.bundle_kind == "route_tail_margin":
        route = work[(work["row"].astype(int) == 164) & (work["target"].astype(str) == "S3")].copy()
        margin = work[(work["subject_id"].astype(str).isin(["id04", "id06"])) & (work["target"].astype(str).isin(["S1", "S2"]))].copy()
        margin = margin.sort_values(["h123_pool_score"], ascending=False).head(max(spec.max_add - len(route), 0))
        return pd.concat([route, margin], ignore_index=True).head(spec.max_add)
    raise ValueError(spec.bundle_kind)


def apply_bundle(start: np.ndarray, bundle: pd.DataFrame, spec: H125Spec, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes) -> tuple[np.ndarray, pd.DataFrame, dict[str, float]]:
    move_mat = start.copy()
    before = evaluate_matrix(move_mat, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
    added = []
    for rec in bundle.to_dict("records"):
        row = int(rec["row"])
        tidx = int(rec["target_index"])
        tmp = move_mat.copy()
        tmp[row, tidx] = float(rec["h125_move"])
        after = evaluate_matrix(tmp, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
        axis_ok = (
            after["badw"] <= spec.max_bad_weighted_pos
            and after["badmax"] <= spec.max_bad_max_pos
            and after["h088"] <= spec.max_h088_cos
            and after["margin"] >= spec.min_good_margin
            and after["route"] <= spec.route_pred_cap
            and after["h098"] <= spec.h098_pred_cap
        )
        if not axis_ok:
            continue
        move_mat = tmp
        added.append(
            {
                "row": row,
                "target_index": tidx,
                "target": str(rec["target"]),
                "subject_id": str(rec["subject_id"]),
                "sleep_date": str(rec["sleep_date"]),
                "h125_move": float(rec["h125_move"]),
                "h123_pool_score": float(rec["h123_pool_score"]),
                "h112_residual_safety": float(rec["h112_residual_safety"]),
                "h112_residual_toxicity": float(rec["h112_residual_toxicity"]),
                "h112_residual_gap": float(rec["h112_residual_gap"]),
                "proposal_source": str(rec["proposal_source"]),
                **{f"after_{key}": value for key, value in after.items()},
                **{f"delta_{key}": after[key] - before[key] for key in after},
            }
        )
    final = evaluate_matrix(move_mat, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
    return move_mat, pd.DataFrame(added), final


def make_selected(h124_selected: pd.DataFrame, scored: pd.DataFrame, added: pd.DataFrame, move_mat: np.ndarray) -> pd.DataFrame:
    core = h124_selected.copy()
    core["h125_component"] = "h124_core"
    core["h125_actual_move"] = [
        float(move_mat[int(row), int(tidx)])
        for row, tidx in zip(core["row"].astype(int), core["target_index"].astype(int))
    ]
    core = core[np.abs(core["h125_actual_move"].to_numpy(dtype=np.float64)) > 1.0e-12].copy()
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
            for row, tidx, move in zip(added["row"], added["target_index"], added["h125_move"])
        }
        add_rows["h125_component"] = "h125_bundle"
        add_rows["h125_actual_move"] = [
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
    combined["h112_move"] = combined["h125_actual_move"].to_numpy(dtype=np.float64)
    combined["h097_move_col"] = "h112_move"
    return combined.sort_values(["row", "target_index"]).reset_index(drop=True)


def run() -> None:
    cleanup_previous_outputs()
    pool, _public, sample, base_prob, cell, h098_fit, route_fit, basis_fit_df, basis_fit_moves, bad_axes, bad_moves, good_moves, axes, fit, model_scores, props = h118mod.prepare_context()
    scored = h123mod.build_scored_pool(pool, base_prob, fit, bad_axes, bad_moves, good_moves, axes, props)
    h122_selected, h122_removed = h123mod.load_selected_h122()
    h124_decision = pd.read_csv(HITL / "h124_dual_sensor_refill_envelope_hsjepa/h124_decision.csv")
    h124_candidate_id = str(h124_decision["selected_candidate_id"].iloc[0])
    h124_selected = pd.read_csv(HITL / "h124_dual_sensor_refill_envelope_hsjepa/h124_selected_cells.csv")
    h124_selected = h124_selected[h124_selected["candidate_id"].astype(str) == h124_candidate_id].copy()
    h124_move = h115mod.load_previous_move(sample, base_prob, "submission_h124_dualsensor_*_uploadsafe.csv").reshape(base_prob.shape)
    work = build_remaining_pool(scored, h124_move, h122_removed)
    start_eval = evaluate_matrix(h124_move, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
    previous = {
        "h124": h124_move,
        "h123": h115mod.load_previous_move(sample, base_prob, "submission_h123_refilleq_*_uploadsafe.csv"),
        "h122": h115mod.load_previous_move(sample, base_prob, "submission_h122_pruneeq_*_uploadsafe.csv"),
        "h121": h115mod.load_previous_move(sample, base_prob, "submission_h121_rowsensorpart_*_uploadsafe.csv"),
        "h118": h115mod.load_previous_move(sample, base_prob, "submission_h118_forbiddenveto_*_uploadsafe.csv"),
    }

    candidate_rows = []
    selected_frames = []
    added_frames = []
    audit_rows = []
    for spec in candidate_specs():
        bundle = spec_pool(work, spec)
        move_mat, added, final = apply_bundle(
            h124_move,
            bundle,
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
        bscore = bundle_score(final, start_eval)
        audit_rows.append({"spec_name": spec.name, "bundle_pool_rows": int(len(bundle)), "added_cells": int(len(added)), "bundle_score": bscore})
        if added.empty or bscore < spec.min_bundle_score:
            continue
        prob = materialize(base_prob, move_mat)
        hash_id = short_hash(prob)
        candidate_id = safe_id(f"h125_{spec.name}_{hash_id}", 128)
        path = OUT / f"submission_{candidate_id}.csv"
        h085mod.write_submission(sample, prob, path)
        selected_cells = make_selected(h124_selected, scored, added, move_mat)
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
            "h125_start_cells": int((np.abs(h124_move) > 1.0e-12).sum()),
            "h125_added_cells": int(len(added)),
            "h125_added_rows": int(added["row"].nunique()),
            "h125_added_mean_score": float(bscore / max(len(added), 1)),
            "h125_added_targets": ";".join(f"{k}:{v}" for k, v in added["target"].value_counts().to_dict().items()),
            "h125_delta_start_route": float(final["route"] - start_eval["route"]),
            "h125_delta_start_h098": float(final["h098"] - start_eval["h098"]),
            "h125_delta_start_h088": float(final["h088"] - start_eval["h088"]),
            "h125_delta_start_margin": float(final["margin"] - start_eval["margin"]),
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
        metrics["h125_worldview"] = spec.worldview
        metrics["h125_fit_feature_set"] = fit.feature_set
        metrics["h125_fit_alpha"] = fit.alpha
        metrics["h125_fit_score"] = fit.score
        metrics["h125_bundle_score"] = bscore
        metrics["h125_score"] = (
            305.0 * (-float(metrics["route_basis_pred_delta_vs_h057"]))
            + 255.0 * (-float(metrics["model_pred_delta_vs_h057"]))
            + 90.0 * (-float(metrics["h118_curv_marginal_vs_zero"]))
            + 0.18 * float(metrics["h102_cum_good_bad_margin"])
            + 0.10 * max(-float(metrics["h102_cum_h088_axis_cos"]), 0.0)
            + 0.08 * float(metrics["selected_mean_residual_safety"])
            + 0.10 * float(metrics["selected_mean_residual_gap"])
            - 0.10 * float(metrics["selected_mean_residual_toxicity"])
            + 0.008 * float(metrics["h125_added_cells"])
            + 2.0 * max(bscore, 0.0)
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
    audit.to_csv(OUT / "h125_bundle_audit.csv", index=False)
    scored.to_csv(OUT / "h125_scored_pool.csv", index=False)
    model_scores.to_csv(OUT / "h125_curvature_model_scores.csv", index=False)
    if candidates.empty:
        report = f"""# H125 Row-Bundle Equation Solver HS-JEPA

No candidate was promoted.

Audit:

{md_table(audit, 20)}
"""
        (OUT / "h125_report.md").write_text(report, encoding="utf-8")
        print("H125 promoted no candidate")
        print(audit.to_string(index=False))
        return

    candidates = candidates.sort_values(["h125_score", "h125_bundle_score"], ascending=[False, False]).reset_index(drop=True)
    selected = candidates.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"submission_h125_rowbundle_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)
    decision = {
        "decision": "promote_h125_row_bundle_equation_solver",
        "selected_candidate_id": selected["candidate_id"],
        "root_uploadsafe_path": str(root_path),
        "worldview": selected["h125_worldview"],
        **selected,
        **{f"root_{key}": value for key, value in validation.items()},
    }
    candidates.to_csv(OUT / "h125_candidates.csv", index=False)
    pd.concat(selected_frames, ignore_index=True).to_csv(OUT / "h125_selected_cells.csv", index=False)
    pd.concat(added_frames, ignore_index=True).to_csv(OUT / "h125_added_cells.csv", index=False)
    pd.DataFrame([decision]).to_csv(OUT / "h125_decision.csv", index=False)

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
        "h125_added_cells",
        "h125_added_targets",
        "h125_delta_start_route",
        "h125_delta_start_h098",
        "h125_delta_start_h088",
        "h125_delta_start_margin",
        "model_pred_delta_vs_h057",
        "route_basis_pred_delta_vs_h057",
        "h102_cum_h088_axis_cos",
        "h102_cum_good_bad_margin",
        "h125_bundle_score",
        "h125_score",
        "file",
    ]
    report = f"""# H125 Row-Bundle Equation Solver HS-JEPA

Question: after H124 dual-sensor refill, should remaining safe cells be added
individually, or only as row/subject bundles that preserve a hidden episode?

Candidates:

{md_table(candidates[cols], 20)}

Decision:

{md_table(pd.DataFrame([decision]), 1)}

Interpretation rule:

- If H125 improves over H124, the safe assignment unit is a row/subject bundle,
  not an isolated cell.
- If H124 improves more, H125 over-completed a bundle and cell-level envelope is
  safer.
- If H123 improves more, route completion matters more than bundle conservation.
"""
    (OUT / "h125_report.md").write_text(report, encoding="utf-8")
    print("H125 selected candidate")
    print(candidates[cols].head(10).to_string(index=False))
    print("\nDecision")
    print(pd.DataFrame([decision])[["decision", "selected_candidate_id", "root_uploadsafe_path", "root_upload_safe"]].to_string(index=False))


if __name__ == "__main__":
    run()
