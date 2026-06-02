#!/usr/bin/env python3
"""H126: component-coefficient equation solver HS-JEPA.

H122-H125 treated row-target actions as selected cells.  H126 treats the same
actions as basis components and solves their coefficients.  The question is
whether public/private safety lives in the action support, or in the amplitude
equation across already discovered components.
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
OUT = HITL / "h126_component_coefficient_equation_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H125_PATH = HITL / "h125_row_bundle_equation_solver_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h125mod", H125_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H125_PATH}")
h125mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h125mod
SPEC.loader.exec_module(h125mod)

h124mod = h125mod.h124mod
h123mod = h125mod.h123mod
h122mod = h125mod.h122mod
h118mod = h125mod.h118mod
h115mod = h125mod.h115mod
h102mod = h125mod.h102mod
h085mod = h125mod.h085mod

TARGETS = h125mod.TARGETS
TOL = h125mod.TOL


@dataclass(frozen=True)
class H126Spec:
    name: str
    group: str
    core: float
    q3: float
    s3: float
    s1_margin: float
    closure: float
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
    min_public_private_margin_gain: float
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


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h126_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h126_coeffeq_*.csv"):
        path.unlink()


def load_move_path(path: Path, sample: pd.DataFrame, base_prob: np.ndarray) -> np.ndarray:
    df = h085mod.load_sub(path, sample)
    prob = df[TARGETS].to_numpy(dtype=np.float64)
    return (logit(prob) - logit(base_prob)).reshape(base_prob.shape)


def load_selected_all() -> pd.DataFrame:
    frames = []
    for rel in [
        "h122_action_prune_equation_solver_hsjepa/h122_selected_cells.csv",
        "h123_prune_refill_equation_solver_hsjepa/h123_selected_cells.csv",
        "h124_dual_sensor_refill_envelope_hsjepa/h124_selected_cells.csv",
        "h125_row_bundle_equation_solver_hsjepa/h125_selected_cells.csv",
    ]:
        path = HITL / rel
        if path.exists():
            frames.append(pd.read_csv(path))
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True)
    out["row"] = out["row"].astype(int)
    out["target_index"] = out["target_index"].astype(int)
    return out.sort_values(["row", "target_index"]).drop_duplicates(["row", "target_index"], keep="last").reset_index(drop=True)


def nonzero_keys(move: np.ndarray) -> set[tuple[int, int]]:
    rows, cols = np.where(np.abs(move) > 1.0e-12)
    return {(int(row), int(col)) for row, col in zip(rows, cols)}


def component_summary(components: dict[str, np.ndarray]) -> pd.DataFrame:
    rows = []
    for name, move in components.items():
        keys = nonzero_keys(move)
        target_counts = {target: 0 for target in TARGETS}
        for _row, tidx in keys:
            target_counts[TARGETS[tidx]] += 1
        rows.append(
            {
                "component": name,
                "cells": int(len(keys)),
                "rows": int(len({row for row, _tidx in keys})),
                "l1": float(np.abs(move).sum()),
                "l2": float(np.linalg.norm(move.reshape(-1))),
                **{f"{target}_cells": int(target_counts[target]) for target in TARGETS},
            }
        )
    return pd.DataFrame(rows)


def candidate_specs() -> list[H126Spec]:
    common = dict(
        max_cells=34,
        max_rows=28,
        max_per_subject=18,
        max_per_target=18,
        amp=1.0,
        cap=0.25,
        pool_top=260,
        min_score=0.08,
        min_residual_gap=0.02,
        max_residual_toxicity=0.62,
        min_residual_safety=0.48,
        max_bad_weighted_pos=0.0005,
        max_bad_max_pos=0.0020,
        max_curv_marg=0.000048,
        max_h088_hard_cosine=-0.040,
        min_public_private_margin_gain=0.020,
    )
    return [
        H126Spec(
            name="h124_basis_replay",
            group="coeff_replay",
            core=1.00,
            q3=1.00,
            s3=0.00,
            s1_margin=1.00,
            closure=0.00,
            max_h088_cos=-0.052,
            min_good_margin=0.142,
            route_pred_cap=-0.000695,
            h098_pred_cap=-0.000030,
            worldview="H124 is the safe coefficient equation: prune core + Q3 route + S1 margin, no S3 tail/closure",
            **common,
        ),
        H126Spec(
            name="h125_closure_soft",
            group="coeff_soft_closure",
            core=1.00,
            q3=1.00,
            s3=0.00,
            s1_margin=1.00,
            closure=0.50,
            max_h088_cos=-0.050,
            min_good_margin=0.148,
            route_pred_cap=-0.000695,
            h098_pred_cap=-0.000030,
            worldview="row-bundle closure is real but should be softened because full closure may over-complete H124",
            **common,
        ),
        H126Spec(
            name="h125_closure_full",
            group="coeff_full_closure",
            core=1.00,
            q3=1.00,
            s3=0.00,
            s1_margin=1.00,
            closure=1.00,
            max_h088_cos=-0.050,
            min_good_margin=0.152,
            route_pred_cap=-0.000695,
            h098_pred_cap=-0.000031,
            worldview="H125 is the full safe equation: H124 plus id04 S1 closure",
            **common,
        ),
        H126Spec(
            name="route_tail_quarantine",
            group="coeff_route_tail",
            core=1.00,
            q3=1.00,
            s3=0.35,
            s1_margin=1.00,
            closure=0.00,
            max_h088_cos=-0.052,
            min_good_margin=0.142,
            route_pred_cap=-0.000710,
            h098_pred_cap=-0.000028,
            worldview="S3 route tail has some true route signal, but must be quarantined below full H123 amplitude",
            **common,
        ),
        H126Spec(
            name="core_cautious_margin_strong",
            group="coeff_core_margin",
            core=0.92,
            q3=1.05,
            s3=0.00,
            s1_margin=1.15,
            closure=0.50,
            max_h088_cos=-0.048,
            min_good_margin=0.150,
            route_pred_cap=-0.000685,
            h098_pred_cap=-0.000030,
            worldview="public-safe field is a slightly weaker prune core with stronger S1 margin compensation",
            **common,
        ),
        H126Spec(
            name="core_strong_no_tail",
            group="coeff_core_strong",
            core=1.08,
            q3=0.90,
            s3=0.00,
            s1_margin=0.90,
            closure=0.00,
            max_h088_cos=-0.058,
            min_good_margin=0.132,
            route_pred_cap=-0.000690,
            h098_pred_cap=-0.000026,
            worldview="the real signal is mostly toxic-prune core; refills are only small compensation",
            **common,
        ),
        H126Spec(
            name="core_soft_all_refill",
            group="coeff_soft_all_refill",
            core=0.88,
            q3=1.20,
            s3=0.25,
            s1_margin=1.10,
            closure=0.40,
            max_h088_cos=-0.045,
            min_good_margin=0.145,
            route_pred_cap=-0.000695,
            h098_pred_cap=-0.000029,
            worldview="H122 over-prunes; a softer core plus multiple small route/margin refills is safer",
            **common,
        ),
        H126Spec(
            name="s1_margin_only_refill",
            group="coeff_s1_only",
            core=1.00,
            q3=0.00,
            s3=0.00,
            s1_margin=1.20,
            closure=0.60,
            max_h088_cos=-0.050,
            min_good_margin=0.150,
            route_pred_cap=-0.000600,
            h098_pred_cap=-0.000030,
            worldview="Q3 refill is a route shortcut; only S1 margin/closure represent public-safe human-state compensation",
            **common,
        ),
    ]


def build_selected_cells(selected_pool: pd.DataFrame, move_mat: np.ndarray, component_name: dict[tuple[int, int], str]) -> pd.DataFrame:
    active = nonzero_keys(move_mat)
    if not active:
        return pd.DataFrame()
    rows = []
    pool_lookup = {
        (int(row), int(tidx)): rec
        for rec, row, tidx in zip(selected_pool.to_dict("records"), selected_pool["row"], selected_pool["target_index"])
    }
    for row, tidx in sorted(active):
        rec = dict(pool_lookup.get((row, tidx), {}))
        rec["row"] = row
        rec["target_index"] = tidx
        rec["target"] = TARGETS[tidx]
        rec["h126_component"] = component_name.get((row, tidx), "mixed_component")
        rec["h126_actual_move"] = float(move_mat[row, tidx])
        rows.append(rec)
    out = pd.DataFrame(rows)
    out["h112_move"] = out["h126_actual_move"].to_numpy(dtype=np.float64)
    out["h097_move_col"] = "h112_move"
    return out.sort_values(["row", "target_index"]).reset_index(drop=True)


def component_labels(components: dict[str, np.ndarray], weights: dict[str, float]) -> dict[tuple[int, int], str]:
    labels: dict[tuple[int, int], str] = {}
    for name, move in components.items():
        if abs(weights.get(name, 0.0)) <= 1.0e-12:
            continue
        for key in nonzero_keys(move):
            if key in labels:
                labels[key] = f"{labels[key]}+{name}"
            else:
                labels[key] = name
    return labels


def coeff_move(components: dict[str, np.ndarray], spec: H126Spec) -> tuple[np.ndarray, dict[str, float]]:
    weights = {
        "core": spec.core,
        "q3_refill": spec.q3,
        "s3_tail": spec.s3,
        "s1_margin": spec.s1_margin,
        "id04_closure": spec.closure,
    }
    out = np.zeros_like(next(iter(components.values())))
    for name, weight in weights.items():
        out = out + float(weight) * components[name]
    return out, weights


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


def run() -> None:
    cleanup_previous_outputs()
    pool, _public, sample, base_prob, cell, h098_fit, route_fit, basis_fit_df, basis_fit_moves, bad_axes, bad_moves, good_moves, axes, fit, model_scores, props = h118mod.prepare_context()
    selected_pool = load_selected_all()

    h122 = load_move_path(ROOT / "submission_h122_pruneeq_0a9edcce_uploadsafe.csv", sample, base_prob)
    h123_q3 = load_move_path(HITL / "h123_prune_refill_equation_solver_hsjepa/submission_h123_single_route_q3_refill_05356288.csv", sample, base_prob)
    h123_sparse = load_move_path(HITL / "h123_prune_refill_equation_solver_hsjepa/submission_h123_sparse_route_refill_8958f688.csv", sample, base_prob)
    h124 = load_move_path(ROOT / "submission_h124_dualsensor_b8e822c0_uploadsafe.csv", sample, base_prob)
    h125 = load_move_path(ROOT / "submission_h125_rowbundle_f3990392_uploadsafe.csv", sample, base_prob)

    components = {
        "core": h122,
        "q3_refill": h123_q3 - h122,
        "s3_tail": h123_sparse - h123_q3,
        "s1_margin": h124 - h123_q3,
        "id04_closure": h125 - h124,
    }
    comp_report = component_summary(components)
    comp_report.to_csv(OUT / "h126_component_summary.csv", index=False)
    model_scores.to_csv(OUT / "h126_curvature_model_scores.csv", index=False)

    baseline_eval = {
        "h122": evaluate_matrix(h122, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes),
        "h123_q3": evaluate_matrix(h123_q3, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes),
        "h123_sparse": evaluate_matrix(h123_sparse, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes),
        "h124": evaluate_matrix(h124, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes),
        "h125": evaluate_matrix(h125, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes),
    }
    pd.DataFrame([{"baseline": name, **vals} for name, vals in baseline_eval.items()]).to_csv(OUT / "h126_baseline_equation_metrics.csv", index=False)
    baseline_hashes = {
        short_hash(materialize(base_prob, move))
        for move in [h122, h123_q3, h123_sparse, h124, h125]
    }

    previous = {
        "h125": h125.reshape(-1),
        "h124": h124.reshape(-1),
        "h123": h123_sparse.reshape(-1),
        "h122": h122.reshape(-1),
        "h088": h115mod.load_previous_move(sample, base_prob, "submission_h088_*_uploadsafe.csv"),
        "h057": h115mod.load_previous_move(sample, base_prob, "submission_h057_*_uploadsafe.csv"),
    }

    candidate_rows = []
    selected_frames = []
    for spec in candidate_specs():
        move_mat, weights = coeff_move(components, spec)
        active = nonzero_keys(move_mat)
        target_counts = {target: 0 for target in TARGETS}
        for _row, tidx in active:
            target_counts[TARGETS[tidx]] += 1
        if len(active) > spec.max_cells:
            continue
        if len({row for row, _tidx in active}) > spec.max_rows:
            continue
        if any(count > spec.max_per_target for count in target_counts.values()):
            continue
        evald = evaluate_matrix(move_mat, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
        if evald["badw"] > spec.max_bad_weighted_pos or evald["badmax"] > spec.max_bad_max_pos:
            continue
        if evald["h088"] > spec.max_h088_cos or evald["margin"] < spec.min_good_margin:
            continue
        if evald["route"] > spec.route_pred_cap or evald["h098"] > spec.h098_pred_cap:
            continue
        if evald["curv_marg"] > spec.max_curv_marg:
            continue
        if evald["margin"] - baseline_eval["h122"]["margin"] < spec.min_public_private_margin_gain:
            continue

        prob = materialize(base_prob, move_mat)
        if int((np.abs(prob - base_prob) > TOL).sum()) == 0:
            continue
        hash_id = short_hash(prob)
        candidate_id = safe_id(f"h126_{spec.name}_{hash_id}", 128)
        path = OUT / f"submission_{candidate_id}.csv"
        h085mod.write_submission(sample, prob, path)
        axis = h102mod.cumulative_axis_metrics(move_mat.reshape(-1), bad_axes, bad_moves, good_moves)
        labels = component_labels(components, weights)
        selected_cells = build_selected_cells(selected_pool, move_mat, labels)
        diag = {
            "h118_zero_curv": -0.0002616634510263019,
            "h118_curv_pred_delta_vs_h057": evald["curv_marg"] - 0.0002616634510263019,
            "h118_curv_marginal_vs_zero": evald["curv_marg"],
            "h118_mean_forbidden_same": float(selected_cells.get("h117_forbidden_same", pd.Series([0.0])).astype(float).mean()),
            "h118_max_forbidden_same": float(selected_cells.get("h117_forbidden_same", pd.Series([0.0])).astype(float).max()),
            "h118_mean_forbidden_pressure": float(selected_cells.get("h117_forbidden_pressure", pd.Series([0.0])).astype(float).mean()),
            "h118_mean_veto_score": float(selected_cells.get("h118_forbidden_veto_score", pd.Series([1.0])).astype(float).mean()),
            "h118_selected_rows": int(selected_cells["row"].nunique()),
            "h126_core_coeff": spec.core,
            "h126_q3_coeff": spec.q3,
            "h126_s3_coeff": spec.s3,
            "h126_s1_margin_coeff": spec.s1_margin,
            "h126_closure_coeff": spec.closure,
            "h126_margin_gain_vs_h122": float(evald["margin"] - baseline_eval["h122"]["margin"]),
            "h126_route_gain_vs_h122": float(evald["route"] - baseline_eval["h122"]["route"]),
            "h126_h098_gain_vs_h122": float(evald["h098"] - baseline_eval["h122"]["h098"]),
            "h126_h088_shift_vs_h122": float(evald["h088"] - baseline_eval["h122"]["h088"]),
            "h126_component_cells": ";".join(
                f"{row.component}:{int(row.cells)}" for row in comp_report.itertuples(index=False)
            ),
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
        metrics["h126_group"] = spec.group
        metrics["h126_worldview"] = spec.worldview
        metrics["h126_fit_feature_set"] = fit.feature_set
        metrics["h126_fit_alpha"] = fit.alpha
        metrics["h126_fit_score"] = fit.score
        metrics["h126_coeff_vector"] = f"core={spec.core};q3={spec.q3};s3={spec.s3};s1={spec.s1_margin};closure={spec.closure}"
        metrics["h126_duplicate_baseline"] = bool(hash_id in baseline_hashes)
        metrics["h126_score"] = (
            315.0 * (-float(metrics["route_basis_pred_delta_vs_h057"]))
            + 255.0 * (-float(metrics["model_pred_delta_vs_h057"]))
            + 100.0 * (-float(metrics["h118_curv_marginal_vs_zero"]))
            + 0.20 * float(metrics["h102_cum_good_bad_margin"])
            + 0.10 * max(-float(metrics["h102_cum_h088_axis_cos"]), 0.0)
            + 0.10 * float(metrics["selected_mean_residual_safety"])
            + 0.12 * float(metrics["selected_mean_residual_gap"])
            - 0.12 * float(metrics["selected_mean_residual_toxicity"])
            - 0.020 * max(float(metrics["selected_cells"]) - 28.0, 0.0)
            - 20.0 * max(float(metrics["hard_diag_delta_vs_h057"]), 0.0)
            - 0.8 * max(h088_cos, 0.0)
        )
        candidate_rows.append(metrics)
        selected2 = selected_cells.copy()
        if "candidate_id" in selected2.columns:
            selected2 = selected2.drop(columns=["candidate_id"])
        selected2.insert(0, "candidate_id", candidate_id)
        selected_frames.append(selected2)

    candidates = pd.DataFrame(candidate_rows)
    if candidates.empty:
        report = f"""# H126 Component-Coefficient Equation Solver HS-JEPA

No candidate was promoted.

Component basis:

{md_table(comp_report, 20)}

Baseline equation metrics:

{md_table(pd.DataFrame([{"baseline": name, **vals} for name, vals in baseline_eval.items()]), 20)}
"""
        (OUT / "h126_report.md").write_text(report, encoding="utf-8")
        print("H126 promoted no candidate")
        print(comp_report.to_string(index=False))
        return

    candidates = candidates.sort_values(["h126_duplicate_baseline", "h126_score", "route_basis_pred_delta_vs_h057"], ascending=[True, False, True]).reset_index(drop=True)
    selected = candidates.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"submission_h126_coeffeq_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)
    decision = {
        "decision": "promote_h126_component_coefficient_equation_solver",
        "selected_candidate_id": selected["candidate_id"],
        "root_uploadsafe_path": str(root_path),
        "worldview": selected["h126_worldview"],
        **selected,
        **{f"root_{key}": value for key, value in validation.items()},
    }

    candidates.to_csv(OUT / "h126_candidates.csv", index=False)
    pd.concat(selected_frames, ignore_index=True).to_csv(OUT / "h126_selected_cells.csv", index=False)
    pd.DataFrame([decision]).to_csv(OUT / "h126_decision.csv", index=False)

    cols = [
        "candidate_id",
        "spec_name",
        "h126_coeff_vector",
        "h126_duplicate_baseline",
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
        "h126_margin_gain_vs_h122",
        "h126_route_gain_vs_h122",
        "h118_h088_cosine",
        "h126_score",
        "file",
    ]
    report = f"""# H126 Component-Coefficient Equation Solver HS-JEPA

Question: is public/private action safety determined by selected row-target
support, or by coefficients over the discovered action basis?

Component basis:

{md_table(comp_report, 20)}

Baseline equation metrics:

{md_table(pd.DataFrame([{"baseline": name, **vals} for name, vals in baseline_eval.items()]), 20)}

Candidates:

{md_table(candidates[cols], 20)}

Decision:

{md_table(pd.DataFrame([decision]), 1)}

Interpretation rule:

- If H126 improves, the hidden action field is an equation over components, not
  a discrete selected-cell set.
- If H124/H125 stay better, action support matters more than coefficient
  solving; H126 coefficient freedom is mostly local stress overfit.
- If route-tail variants improve, S3 tail was underweighted by previous
  diagnostics and should be brought back as a quarantined private/public route.
"""
    (OUT / "h126_report.md").write_text(report, encoding="utf-8")
    print("H126 selected candidate")
    print(candidates[cols].head(10).to_string(index=False))
    print("\nDecision")
    print(pd.DataFrame([decision])[["decision", "selected_candidate_id", "root_uploadsafe_path", "root_upload_safe"]].to_string(index=False))


if __name__ == "__main__":
    run()
