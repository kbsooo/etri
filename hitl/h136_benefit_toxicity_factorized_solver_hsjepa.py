#!/usr/bin/env python3
"""H136: benefit-toxicity factorized row-target equation solver HS-JEPA.

H135 showed that coherent row-vector moves can improve the route equation, but
the same vector also drags H088/margin toxicity.  H136 does not ask whether the
route-heavy action is bigger.  It asks whether the public/private equation can
separate the route benefit field from the toxicity shadow field.

Hypothesis:

    The next public-safe assignment is not the highest route-gain row-vector;
    it is the Pareto knee where H132/H135 route benefit survives after explicit
    toxicity accounting.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import importlib.util
import itertools
import shutil
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HITL = ROOT / "hitl"
OUT = HITL / "h136_benefit_toxicity_factorized_solver_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H135_PATH = HITL / "h135_rowvector_conservation_solver_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h135mod_h136", H135_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H135_PATH}")
h135mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h135mod
SPEC.loader.exec_module(h135mod)

h134mod = h135mod.h134mod
h133mod = h135mod.h133mod
h132mod = h135mod.h132mod
h130mod = h135mod.h130mod
h126mod = h135mod.h126mod
h123mod = h135mod.h123mod
h118mod = h135mod.h118mod
h102mod = h135mod.h102mod
h085mod = h135mod.h085mod

TARGETS = h135mod.TARGETS
TOL = h134mod.TOL


@dataclass(frozen=True)
class H136Spec:
    name: str
    group: str
    start_name: str
    row_source: str
    target_mode: str
    max_bundle_size: int
    frac_values: tuple[float, ...]
    max_combo_bundles: int
    max_combo_pool: int
    keep_top: int
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
    min_companion_score: float
    min_proposal_abs: float
    min_bundle_score: float
    min_factor_score: float
    min_benefit_toxicity_ratio: float
    h088_weight: float
    margin_weight: float
    worldview: str


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def safe_id(text: str, limit: int = 132) -> str:
    return h085mod.safe_id(text, limit=limit)


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return h085mod.md_table(frame, n=n)


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h136_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h136_factorized_*.csv"):
        path.unlink()


def root_submission_paths() -> dict[str, Path]:
    paths = h135mod.root_submission_paths()
    paths["h135"] = ROOT / "submission_h135_rowvector_c86ff9aa_uploadsafe.csv"
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


def candidate_specs() -> list[H136Spec]:
    common = dict(
        start_name="h132",
        row_source="all_q1_bundle_rows",
        target_mode="q3s_companion",
        max_bundle_size=2,
        max_per_subject=30,
        max_per_target=22,
        amp=1.0,
        cap=0.20,
        pool_top=180,
        min_score=0.0,
        min_residual_gap=-0.58,
        max_residual_toxicity=0.98,
        min_residual_safety=0.24,
        max_bad_weighted_pos=0.0006,
        max_bad_max_pos=0.0022,
        max_curv_marg=0.000068,
        min_companion_score=0.265,
        min_proposal_abs=0.012,
        h088_weight=0.0020,
        margin_weight=0.020,
    )
    return [
        H136Spec(
            name="h132_factorized_shadow_clip",
            group="benefit_toxicity_shadow_clip",
            frac_values=(0.25, 0.35, 0.60),
            max_combo_bundles=3,
            max_combo_pool=26,
            keep_top=8,
            max_cells=33,
            max_rows=25,
            max_h088_cos=-0.060,
            min_good_margin=0.160,
            route_pred_cap=-0.000635,
            h098_pred_cap=-0.000018,
            max_h088_hard_cosine=-0.018,
            min_component_gain=0.00025,
            min_bundle_score=0.46,
            min_factor_score=0.0018,
            min_benefit_toxicity_ratio=1.05,
            worldview="route benefit is real, but H135 overdrives toxic shadow; clip at the benefit/toxicity Pareto knee",
            **common,
        ),
        H136Spec(
            name="h132_factorized_margin_knee",
            group="benefit_toxicity_margin_knee",
            frac_values=(0.25, 0.35, 0.50),
            max_combo_bundles=3,
            max_combo_pool=24,
            keep_top=8,
            max_cells=32,
            max_rows=24,
            max_h088_cos=-0.062,
            min_good_margin=0.164,
            route_pred_cap=-0.000630,
            h098_pred_cap=-0.000018,
            max_h088_hard_cosine=-0.018,
            min_component_gain=0.00018,
            min_bundle_score=0.45,
            min_factor_score=0.0013,
            min_benefit_toxicity_ratio=1.20,
            worldview="public equation prefers a margin-preserving row-vector assignment over H135's route-heavy completion",
            **common,
        ),
        H136Spec(
            name="h132_factorized_route_pareto",
            group="benefit_toxicity_route_pareto",
            frac_values=(0.35, 0.50, 0.60),
            max_combo_bundles=3,
            max_combo_pool=28,
            keep_top=8,
            max_cells=33,
            max_rows=25,
            max_h088_cos=-0.057,
            min_good_margin=0.156,
            route_pred_cap=-0.000650,
            h098_pred_cap=-0.000018,
            max_h088_hard_cosine=-0.018,
            min_component_gain=0.00032,
            min_bundle_score=0.47,
            min_factor_score=0.0020,
            min_benefit_toxicity_ratio=0.85,
            worldview="test whether H135's route-heavy field remains valid after removing dominated toxic completions",
            **common,
        ),
    ]


def proxy_h135_spec(spec: H136Spec) -> h135mod.H135Spec:
    return h135mod.H135Spec(
        name=f"proxy_{spec.name}",
        group=spec.group,
        start_name=spec.start_name,
        row_source=spec.row_source,
        target_mode=spec.target_mode,
        max_bundle_size=spec.max_bundle_size,
        frac_values=spec.frac_values,
        max_steps=spec.max_combo_bundles,
        min_step_score=0.0,
        min_non_h088_passes=0,
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
        min_companion_score=spec.min_companion_score,
        min_proposal_abs=spec.min_proposal_abs,
        min_bundle_score=spec.min_bundle_score,
        h088_weight=spec.h088_weight,
        margin_weight=spec.margin_weight,
        worldview=spec.worldview,
    )


def evaluate_matrix(move_mat, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes):
    return h135mod.evaluate_matrix(
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


def check_constraints(move_mat: np.ndarray, evald: dict[str, float], spec: H136Spec) -> bool:
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


def component_gain(final: dict[str, float], before: dict[str, float], spec: H136Spec) -> float:
    return (
        245.0 * (-(final["h098"] - before["h098"]))
        + 160.0 * (-(final["curv_marg"] - before["curv_marg"]))
        + 150.0 * max(-(final["route"] - before["route"]), 0.0)
        - 90.0 * max(final["route"] - before["route"], 0.0)
        + spec.margin_weight * (final["margin"] - before["margin"])
        + spec.h088_weight * (-(final["h088"] - before["h088"]))
    )


def factor_scores(final: dict[str, float], before: dict[str, float], bundles: list[dict[str, object]], spec: H136Spec) -> dict[str, float]:
    d_route = float(final["route"] - before["route"])
    d_h098 = float(final["h098"] - before["h098"])
    d_curv = float(final["curv_marg"] - before["curv_marg"])
    d_h088 = float(final["h088"] - before["h088"])
    d_margin = float(final["margin"] - before["margin"])
    d_badw = float(final["badw"] - before["badw"])
    d_badmax = float(final["badmax"] - before["badmax"])
    bundle_score = float(np.mean([float(b["h135_bundle_score"]) for b in bundles])) if bundles else 0.0
    bundle_size = float(sum(int(b["bundle_size"]) for b in bundles))
    route_benefit = (
        260.0 * max(-d_h098, 0.0)
        + 210.0 * max(-d_route, 0.0)
        + 150.0 * max(-d_curv, 0.0)
        + 0.0010 * bundle_score
        + 0.00010 * bundle_size
    )
    toxicity_shadow = (
        260.0 * max(d_h098, 0.0)
        + 110.0 * max(d_route, 0.0)
        + 80.0 * max(d_curv, 0.0)
        + 0.42 * max(d_h088, 0.0)
        + 0.32 * max(-d_margin, 0.0)
        + 5.0 * max(d_badw, 0.0)
        + 3.0 * max(d_badmax, 0.0)
    )
    conservation = (
        0.00115 * bundle_score
        + 0.00014 * bundle_size
        + 0.030 * max(final["margin"] - spec.min_good_margin, 0.0)
        + 0.004 * max(spec.max_h088_cos - final["h088"], 0.0)
    )
    factor_score = route_benefit + conservation - toxicity_shadow
    ratio = route_benefit / (toxicity_shadow + 1.0e-9)
    return {
        "h136_delta_route": d_route,
        "h136_delta_h098": d_h098,
        "h136_delta_curv_marg": d_curv,
        "h136_delta_h088": d_h088,
        "h136_delta_margin": d_margin,
        "h136_route_benefit": float(route_benefit),
        "h136_toxicity_shadow": float(toxicity_shadow),
        "h136_conservation_credit": float(conservation),
        "h136_factor_score": float(factor_score),
        "h136_benefit_toxicity_ratio": float(ratio),
        "h136_mean_bundle_score": bundle_score,
        "h136_bundle_size_total": bundle_size,
    }


def combo_key(combo: tuple[dict[str, object], ...]) -> str:
    return "|".join(str(b["bundle_id"]) for b in combo)


def enumerate_combos(bundle_pool: pd.DataFrame, spec: H136Spec) -> list[tuple[dict[str, object], ...]]:
    records = bundle_pool.head(spec.max_combo_pool).to_dict("records")
    combos: list[tuple[dict[str, object], ...]] = []
    for size in range(1, spec.max_combo_bundles + 1):
        for combo in itertools.combinations(records, size):
            rows = [int(b["row"]) for b in combo]
            if len(set(rows)) != len(rows):
                continue
            combos.append(combo)
    return combos


def flatten_combo_ops(candidate_id: str, combo: tuple[dict[str, object], ...], start: np.ndarray, final: dict[str, float], before: dict[str, float]) -> pd.DataFrame:
    rows = []
    step_move = start.copy()
    step_before = before
    for step, bundle in enumerate(combo, start=1):
        step_after_move = h135mod.apply_bundle(step_move, bundle)
        # The detailed route delta is computed later in the main loop where the
        # evaluator state is available; here we keep cell-level provenance.
        for op in bundle["ops"]:
            rows.append(
                {
                    "candidate_id": candidate_id,
                    "step": step,
                    "bundle_id": str(bundle["bundle_id"]),
                    "bundle_targets": str(bundle["targets"]),
                    "bundle_frac": float(bundle["frac"]),
                    "bundle_size": int(bundle["bundle_size"]),
                    "row": int(op["row"]),
                    "target_index": int(op["target_index"]),
                    "target": str(op["target"]),
                    "subject_id": str(op["subject_id"]),
                    "sleep_date": str(op["sleep_date"]),
                    "old_move": float(op["old_move"]),
                    "new_move": float(op["new_move"]),
                    "state": str(op["state"]),
                    "h134_base_proposal": float(op["h134_base_proposal"]),
                    "h134_companion_score": float(op["h134_companion_score"]),
                    "h135_bundle_score": float(bundle["h135_bundle_score"]),
                    "h136_final_delta_route": float(final["route"] - before["route"]),
                    "h136_final_delta_h098": float(final["h098"] - before["h098"]),
                    "h136_final_delta_h088": float(final["h088"] - before["h088"]),
                    "h136_final_delta_margin": float(final["margin"] - before["margin"]),
                }
            )
        step_move = step_after_move
        step_before = step_before
    return pd.DataFrame(rows)


def make_selected(catalog: pd.DataFrame, move_mat: np.ndarray) -> pd.DataFrame:
    selected = h130mod.make_selected(catalog, move_mat)
    if selected.empty:
        return selected
    selected["h136_actual_move"] = selected["h130_actual_move"]
    selected["h112_move"] = selected["h136_actual_move"].to_numpy(dtype=np.float64)
    return selected


def previous_moves(sample: pd.DataFrame, base_prob: np.ndarray, moves: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    prev = h135mod.previous_moves(
        sample,
        base_prob,
        {name: moves[name] for name in ["h122", "h124", "h126", "h127", "h128", "h129", "h130", "h131", "h132", "h133", "h134"]},
    )
    prev["h135"] = moves["h135"].reshape(-1)
    return prev


def run() -> None:
    cleanup_previous_outputs()
    pool, _public, sample, base_prob, cell, h098_fit, route_fit, basis_fit_df, basis_fit_moves, bad_axes, bad_moves, good_moves, axes, fit, model_scores, props = h118mod.prepare_context()
    scored = h123mod.build_scored_pool(pool, base_prob, fit, bad_axes, bad_moves, good_moves, axes, props)
    catalog = h132mod.build_catalog(scored)
    moves = {name: load_move(name, sample, base_prob) for name in ["h122", "h124", "h126", "h127", "h128", "h129", "h130", "h131", "h132", "h133", "h134", "h135"]}
    known = known_hashes(sample)
    previous = previous_moves(sample, base_prob, moves)
    bundle_rows = h133mod.collect_bundle_rows(catalog, moves["h131"])
    q1_rows = h134mod.collect_q1_rows(bundle_rows)

    audit_rows = []
    start_rows = []
    all_combo_rows = []
    candidate_rows = []
    selected_frames = []
    op_frames = []
    cell_pool_frames = []
    bundle_pool_frames = []
    emitted_hashes: set[str] = set()
    for spec in candidate_specs():
        start_move = moves[spec.start_name]
        cell_pool, bundle_pool = h135mod.build_bundle_pool(catalog, start_move, q1_rows, proxy_h135_spec(spec))
        start_eval = evaluate_matrix(start_move, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
        start_rows.append({"start_name": spec.start_name, "spec_name": spec.name, **start_eval, "start_cells": int((np.abs(start_move) > 1.0e-12).sum()), "cell_pool": int(len(cell_pool)), "bundle_pool": int(len(bundle_pool))})
        audit_rows.append(
            {
                "spec_name": spec.name,
                "start_name": spec.start_name,
                "frac_values": ",".join(map(str, spec.frac_values)),
                "cell_pool": int(len(cell_pool)),
                "bundle_pool": int(len(bundle_pool)),
                "max_combo_pool": spec.max_combo_pool,
                "max_combo_bundles": spec.max_combo_bundles,
            }
        )
        if not cell_pool.empty:
            cp = cell_pool.copy()
            cp.insert(0, "spec_name", spec.name)
            cell_pool_frames.append(cp)
        if not bundle_pool.empty:
            bp = bundle_pool.drop(columns=["ops"]).copy()
            bp.insert(0, "spec_name", spec.name)
            bundle_pool_frames.append(bp)
        if bundle_pool.empty:
            continue
        evaluated = []
        for combo in enumerate_combos(bundle_pool, spec):
            move_mat = start_move.copy()
            for bundle in combo:
                move_mat = h135mod.apply_bundle(move_mat, bundle)
            if np.allclose(move_mat, start_move):
                continue
            final_eval = evaluate_matrix(move_mat, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
            if not check_constraints(move_mat, final_eval, spec):
                continue
            scores = factor_scores(final_eval, start_eval, list(combo), spec)
            if scores["h136_factor_score"] < spec.min_factor_score:
                continue
            if scores["h136_benefit_toxicity_ratio"] < spec.min_benefit_toxicity_ratio:
                continue
            gain = component_gain(final_eval, start_eval, spec)
            if gain < spec.min_component_gain:
                continue
            rec = {
                "spec_name": spec.name,
                "combo_key": combo_key(combo),
                "combo_bundles": len(combo),
                "combo_rows": ",".join(str(int(b["row"])) for b in combo),
                "combo_targets": ";".join(str(b["targets"]) for b in combo),
                "combo_fracs": ",".join(str(float(b["frac"])) for b in combo),
                "combo_mean_bundle_score": float(np.mean([float(b["h135_bundle_score"]) for b in combo])),
                "h136_component_gain": float(gain),
                **scores,
                **{f"final_{key}": value for key, value in final_eval.items()},
                "combo": combo,
                "move_mat": move_mat,
                "final_eval": final_eval,
            }
            rec["h136_combo_score"] = (
                1.00 * rec["h136_factor_score"]
                + 0.35 * rec["h136_component_gain"]
                + 0.00075 * rec["h136_benefit_toxicity_ratio"]
                + 0.025 * max(final_eval["margin"] - spec.min_good_margin, 0.0)
                + 0.003 * max(spec.max_h088_cos - final_eval["h088"], 0.0)
            )
            evaluated.append(rec)
        if not evaluated:
            audit_rows[-1]["promotable_combos"] = 0
            continue
        evaluated = sorted(evaluated, key=lambda x: x["h136_combo_score"], reverse=True)
        audit_rows[-1]["promotable_combos"] = int(len(evaluated))
        for rec in evaluated[: max(spec.keep_top, 1)]:
            combo = rec["combo"]
            move_mat = rec["move_mat"]
            prob = h130mod.materialize(base_prob, move_mat)
            if int((np.abs(prob - base_prob) > TOL).sum()) == 0:
                continue
            hash_id = short_hash(prob)
            rec_public = {k: v for k, v in rec.items() if k not in {"combo", "move_mat", "final_eval"}}
            rec_public["hash_id"] = hash_id
            all_combo_rows.append(rec_public)
            if hash_id in known or hash_id in emitted_hashes:
                continue
            emitted_hashes.add(hash_id)
            candidate_id = safe_id(f"h136_{spec.name}_{hash_id}", 128)
            path = OUT / f"submission_{candidate_id}.csv"
            h085mod.write_submission(sample, prob, path)
            selected_cells = make_selected(catalog, move_mat)
            axis = h102mod.cumulative_axis_metrics(move_mat.reshape(-1), bad_axes, bad_moves, good_moves)
            final_eval = rec["final_eval"]
            diag = {
                "h118_zero_curv": -0.0002616634510263019,
                "h118_curv_pred_delta_vs_h057": final_eval["curv_marg"] - 0.0002616634510263019,
                "h118_curv_marginal_vs_zero": final_eval["curv_marg"],
                "h118_mean_forbidden_same": float(selected_cells.get("h117_forbidden_same", pd.Series([0.0])).astype(float).mean()),
                "h118_max_forbidden_same": float(selected_cells.get("h117_forbidden_same", pd.Series([0.0])).astype(float).max()),
                "h118_mean_forbidden_pressure": float(selected_cells.get("h117_forbidden_pressure", pd.Series([0.0])).astype(float).mean()),
                "h118_mean_veto_score": float(selected_cells.get("h118_forbidden_veto_score", pd.Series([1.0])).astype(float).mean()),
                "h118_selected_rows": int(selected_cells["row"].nunique()),
                "h136_start_field": spec.start_name,
                "h136_cell_pool": int(len(cell_pool)),
                "h136_bundle_pool": int(len(bundle_pool)),
                "h136_combo_key": rec["combo_key"],
                "h136_combo_bundles": int(rec["combo_bundles"]),
                "h136_combo_rows": rec["combo_rows"],
                "h136_combo_targets": rec["combo_targets"],
                "h136_combo_fracs": rec["combo_fracs"],
                "h136_component_gain": float(rec["h136_component_gain"]),
                **{k: v for k, v in rec.items() if k.startswith("h136_")},
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
            metrics["h136_worldview"] = spec.worldview
            metrics["h136_fit_feature_set"] = fit.feature_set
            metrics["h136_fit_alpha"] = fit.alpha
            metrics["h136_fit_score"] = fit.score
            metrics["h136_score"] = (
                310.0 * (-float(metrics["model_pred_delta_vs_h057"]))
                + 280.0 * (-float(metrics["route_basis_pred_delta_vs_h057"]))
                + 125.0 * (-float(metrics["h118_curv_marginal_vs_zero"]))
                + 0.13 * float(metrics["h102_cum_good_bad_margin"])
                + 0.055 * max(-float(metrics["h102_cum_h088_axis_cos"]), 0.0)
                + 0.14 * float(metrics["selected_mean_residual_safety"])
                + 0.12 * float(metrics["selected_mean_residual_gap"])
                - 0.16 * float(metrics["selected_mean_residual_toxicity"])
                + 0.90 * float(metrics["h136_factor_score"])
                + 0.55 * float(metrics["h136_component_gain"])
                + 0.0010 * float(metrics["h136_benefit_toxicity_ratio"])
                - 18.0 * max(float(metrics["hard_diag_delta_vs_h057"]), 0.0)
                - 0.7 * max(h088_cos, 0.0)
            )
            candidate_rows.append(metrics)
            selected2 = selected_cells.copy()
            if "candidate_id" in selected2.columns:
                selected2 = selected2.drop(columns=["candidate_id"])
            selected2.insert(0, "candidate_id", candidate_id)
            selected_frames.append(selected2)
            op_frames.append(flatten_combo_ops(candidate_id, combo, start_move, final_eval, start_eval))

    audit = pd.DataFrame(audit_rows)
    starts = pd.DataFrame(start_rows)
    combos = pd.DataFrame(all_combo_rows)
    candidates = pd.DataFrame(candidate_rows)
    catalog.to_csv(OUT / "h136_catalog.csv", index=False)
    bundle_rows.to_csv(OUT / "h136_bundle_rows.csv", index=False)
    q1_rows.to_csv(OUT / "h136_q1_rows.csv", index=False)
    audit.to_csv(OUT / "h136_audit.csv", index=False)
    starts.to_csv(OUT / "h136_start_metrics.csv", index=False)
    model_scores.to_csv(OUT / "h136_curvature_model_scores.csv", index=False)
    if cell_pool_frames:
        pd.concat(cell_pool_frames, ignore_index=True).to_csv(OUT / "h136_cell_pool.csv", index=False)
    if bundle_pool_frames:
        pd.concat(bundle_pool_frames, ignore_index=True).to_csv(OUT / "h136_bundle_pool.csv", index=False)
    if not combos.empty:
        combos.to_csv(OUT / "h136_combo_scores.csv", index=False)
    if candidates.empty:
        report = f"""# H136 Benefit-Toxicity Factorized Solver HS-JEPA

No candidate was promoted.

Question: can H135's route benefit be separated from its toxicity shadow?

Audit:

{md_table(audit, 20)}

Start metrics:

{md_table(starts, 20)}

Promotable non-duplicate combo scores:

{md_table(combos.sort_values("h136_combo_score", ascending=False) if not combos.empty else combos, 30)}
"""
        (OUT / "h136_report.md").write_text(report, encoding="utf-8")
        print("H136 promoted no candidate")
        print(audit.to_string(index=False))
        return

    candidates = candidates.sort_values(["h136_score", "h136_factor_score", "model_pred_delta_vs_h057"], ascending=[False, False, True]).reset_index(drop=True)
    selected = candidates.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"submission_h136_factorized_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)
    decision = {
        "decision": "promote_h136_benefit_toxicity_factorized_solver",
        "selected_candidate_id": selected["candidate_id"],
        "root_uploadsafe_path": str(root_path.resolve()),
        "worldview": selected["h136_worldview"],
        **selected,
        **{f"root_{key}": value for key, value in validation.items()},
    }
    candidates.to_csv(OUT / "h136_candidates.csv", index=False)
    pd.concat(selected_frames, ignore_index=True).to_csv(OUT / "h136_selected_cells.csv", index=False)
    pd.concat(op_frames, ignore_index=True).to_csv(OUT / "h136_operations.csv", index=False)
    pd.DataFrame([decision]).to_csv(OUT / "h136_decision.csv", index=False)

    cols = [
        "candidate_id",
        "spec_name",
        "h136_start_field",
        "selected_cells",
        "changed_rows_vs_h057",
        "Q1_changed_vs_h057",
        "Q2_changed_vs_h057",
        "Q3_changed_vs_h057",
        "S1_changed_vs_h057",
        "S2_changed_vs_h057",
        "S3_changed_vs_h057",
        "S4_changed_vs_h057",
        "h136_combo_bundles",
        "h136_combo_rows",
        "h136_combo_targets",
        "h136_combo_fracs",
        "h136_delta_route",
        "h136_delta_h098",
        "h136_delta_h088",
        "h136_delta_margin",
        "h136_route_benefit",
        "h136_toxicity_shadow",
        "h136_benefit_toxicity_ratio",
        "model_pred_delta_vs_h057",
        "route_basis_pred_delta_vs_h057",
        "h102_cum_h088_axis_cos",
        "h102_cum_good_bad_margin",
        "h136_factor_score",
        "h136_score",
        "file",
    ]
    report = f"""# H136 Benefit-Toxicity Factorized Solver HS-JEPA

Question: H135 proved row-vector route benefit, but did it also include a
toxicity shadow that public punishes? H136 evaluates row-target bundles as a
benefit/toxicity equation instead of greedily maximizing route gain.

Audit:

{md_table(audit, 20)}

Start metrics:

{md_table(starts, 20)}

Top factorized combo scores:

{md_table(combos.sort_values("h136_combo_score", ascending=False) if not combos.empty else combos, 40)}

Candidates:

{md_table(candidates[cols], 30)}

Operations:

{md_table(pd.concat(op_frames, ignore_index=True), 80)}

Decision:

{md_table(pd.DataFrame([decision]), 1)}

Interpretation rule:

- If H136 beats H135 publicly, the public equation is not simply route-heavy;
  it rewards toxicity-clipped row-target assignment.
- If H135 beats H136, the route benefit dominates the toxicity shadow and H136
  was too conservative.
- If both lose to H132/H134, companion row-vector decoding is diagnostic, not
  action-grade.
"""
    (OUT / "h136_report.md").write_text(report, encoding="utf-8")
    print("H136 selected candidate")
    print(candidates[cols].head(10).to_string(index=False))
    print("\nDecision")
    print(pd.DataFrame([decision])[["decision", "selected_candidate_id", "root_uploadsafe_path", "root_upload_safe"]].to_string(index=False))


if __name__ == "__main__":
    run()
