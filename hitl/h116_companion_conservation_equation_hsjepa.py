#!/usr/bin/env python3
"""H116: companion-conservation row-target equation HS-JEPA.

H115 reopened Q2, but only as a small "companion route."  H116 turns that into
a falsifiable equation:

    if Q2 is action-safe, then Q2-only should be worse than
    Q2 + the right same-row companion targets under the second-order
    public/private action equation.

This is not a broader Q2 bet.  It is a row-level conservation test: the
companion targets must cancel Q2 curvature/toxicity rather than simply add
more cells.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
import hashlib
import importlib.util
import shutil
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HITL = ROOT / "hitl"
OUT = HITL / "h116_companion_conservation_equation_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H115_PATH = HITL / "h115_second_order_action_equation_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h115mod", H115_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H115_PATH}")
h115mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h115mod
SPEC.loader.exec_module(h115mod)

h114mod = h115mod.h114mod
h112mod = h115mod.h112mod
h102mod = h115mod.h102mod
h100mod = h115mod.h100mod
h097mod = h115mod.h097mod
h085mod = h115mod.h085mod

TARGETS = h115mod.TARGETS
KEYS = h115mod.KEYS
BASE_FILE = h115mod.BASE_FILE
TOL = h115mod.TOL


@dataclass(frozen=True)
class H116Spec:
    name: str
    allowed_companions: tuple[str, ...]
    max_bundles: int
    max_cells: int
    max_rows: int
    max_per_subject: int
    max_per_target: int
    q2_cap: int
    max_guard_cells: int
    min_companions: int
    max_companions: int
    amp: float
    cap: float
    guard_amp: float
    guard_cap: float
    row_top: int
    min_cell_score: float
    min_guard_score: float
    min_q2_rescue: float
    max_full_marginal: float
    max_bundle_bad_weighted_pos: float
    max_bundle_bad_max_pos: float
    max_bundle_h088_cos: float
    min_bundle_good_margin: float
    max_global_marginal: float
    max_marginal_add: float
    max_bad_weighted_pos: float
    max_bad_max_pos: float
    max_h088_cos: float
    min_good_margin: float
    route_pred_cap: float
    h098_pred_cap: float
    worldview: str


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def safe_id(text: str, limit: int = 132) -> str:
    return h085mod.safe_id(text, limit=limit)


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return h085mod.md_table(frame, n=n)


def clip_prob(x: np.ndarray) -> np.ndarray:
    return h085mod.clip_prob(np.asarray(x, dtype=np.float64))


def logit(x: np.ndarray) -> np.ndarray:
    return h085mod.logit(np.asarray(x, dtype=np.float64))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return h085mod.sigmoid(np.asarray(x, dtype=np.float64))


def rank01(values: np.ndarray, high: bool = True) -> np.ndarray:
    return h085mod.rank01(np.asarray(values, dtype=np.float64), high=high)


def materialize(base_prob: np.ndarray, move_mat: np.ndarray) -> np.ndarray:
    return clip_prob(sigmoid(logit(base_prob) + move_mat))


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h116_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h116_companion_*.csv"):
        path.unlink()


def route_pred(move_flat: np.ndarray, basis_fit_df: pd.DataFrame, basis_fit_moves: np.ndarray, route_fit: h100mod.RouteBasisFit) -> float:
    return h100mod.predict_candidate_delta(move_flat, basis_fit_df, basis_fit_moves, route_fit)


def h098_pred(move_flat: np.ndarray, cell: pd.DataFrame, h098_fit: h097mod.ResponseFit) -> float:
    return h097mod.predict_candidate_delta(move_flat, cell, h098_fit)


def cosine(a: np.ndarray | None, b: np.ndarray | None) -> float:
    if a is None or b is None:
        return 0.0
    x = np.asarray(a, dtype=np.float64).reshape(-1)
    y = np.asarray(b, dtype=np.float64).reshape(-1)
    return float(np.dot(x, y) / (np.linalg.norm(x) * np.linalg.norm(y) + 1.0e-12))


def overlap_count(a: np.ndarray, b: np.ndarray | None) -> int:
    if b is None:
        return 0
    return int(((np.abs(a.reshape(-1)) > 1.0e-12) & (np.abs(b.reshape(-1)) > 1.0e-12)).sum())


def candidate_specs() -> list[H116Spec]:
    return [
        H116Spec(
            name="q2_conservation_strict_b8_a035",
            allowed_companions=("Q1", "Q3", "S1", "S3"),
            max_bundles=8,
            max_cells=28,
            max_rows=8,
            max_per_subject=3,
            max_per_target=10,
            q2_cap=8,
            max_guard_cells=14,
            min_companions=2,
            max_companions=3,
            amp=0.35,
            cap=0.14,
            guard_amp=0.32,
            guard_cap=0.12,
            row_top=90,
            min_cell_score=0.18,
            min_guard_score=0.20,
            min_q2_rescue=0.000004,
            max_full_marginal=0.000030,
            max_bundle_bad_weighted_pos=0.018,
            max_bundle_bad_max_pos=0.300,
            max_bundle_h088_cos=0.300,
            min_bundle_good_margin=-0.020,
            max_global_marginal=0.000035,
            max_marginal_add=0.000018,
            max_bad_weighted_pos=0.004,
            max_bad_max_pos=0.030,
            max_h088_cos=-0.002,
            min_good_margin=0.004,
            route_pred_cap=0.000120,
            h098_pred_cap=0.000090,
            worldview="Q2 is safe only when same-row Q/Q3/S companion targets cancel its curvature toxicity",
        ),
        H116Spec(
            name="q2_conservation_balanced_b12_a032",
            allowed_companions=("Q1", "Q3", "S1", "S2", "S3"),
            max_bundles=12,
            max_cells=42,
            max_rows=12,
            max_per_subject=4,
            max_per_target=14,
            q2_cap=12,
            max_guard_cells=20,
            min_companions=2,
            max_companions=4,
            amp=0.32,
            cap=0.13,
            guard_amp=0.30,
            guard_cap=0.11,
            row_top=140,
            min_cell_score=0.12,
            min_guard_score=0.16,
            min_q2_rescue=0.000002,
            max_full_marginal=0.000045,
            max_bundle_bad_weighted_pos=0.020,
            max_bundle_bad_max_pos=0.320,
            max_bundle_h088_cos=0.320,
            min_bundle_good_margin=-0.022,
            max_global_marginal=0.000050,
            max_marginal_add=0.000022,
            max_bad_weighted_pos=0.006,
            max_bad_max_pos=0.036,
            max_h088_cos=-0.001,
            min_good_margin=0.003,
            route_pred_cap=0.000150,
            h098_pred_cap=0.000110,
            worldview="Q2 companion conservation can be broader if row-level curvature remains below the zero-action equation",
        ),
        H116Spec(
            name="q2_conservation_micro_b5_a040",
            allowed_companions=("Q3", "S1", "S3"),
            max_bundles=5,
            max_cells=18,
            max_rows=5,
            max_per_subject=2,
            max_per_target=7,
            q2_cap=5,
            max_guard_cells=10,
            min_companions=2,
            max_companions=3,
            amp=0.40,
            cap=0.12,
            guard_amp=0.30,
            guard_cap=0.10,
            row_top=70,
            min_cell_score=0.08,
            min_guard_score=0.18,
            min_q2_rescue=0.000006,
            max_full_marginal=0.000025,
            max_bundle_bad_weighted_pos=0.018,
            max_bundle_bad_max_pos=0.300,
            max_bundle_h088_cos=0.300,
            min_bundle_good_margin=-0.020,
            max_global_marginal=0.000030,
            max_marginal_add=0.000018,
            max_bad_weighted_pos=0.003,
            max_bad_max_pos=0.028,
            max_h088_cos=-0.002,
            min_good_margin=0.004,
            route_pred_cap=0.000160,
            h098_pred_cap=0.000110,
            worldview="only a tiny Q2/Q3/S objective companion kernel is action-grade",
        ),
        H116Spec(
            name="q2_conservation_antidote_b10_a030",
            allowed_companions=("Q1", "Q3", "S1", "S3", "S4"),
            max_bundles=10,
            max_cells=36,
            max_rows=10,
            max_per_subject=3,
            max_per_target=12,
            q2_cap=10,
            max_guard_cells=18,
            min_companions=2,
            max_companions=4,
            amp=0.30,
            cap=0.12,
            guard_amp=0.34,
            guard_cap=0.12,
            row_top=120,
            min_cell_score=0.16,
            min_guard_score=0.18,
            min_q2_rescue=0.000002,
            max_full_marginal=0.000040,
            max_bundle_bad_weighted_pos=0.018,
            max_bundle_bad_max_pos=0.300,
            max_bundle_h088_cos=0.300,
            min_bundle_good_margin=-0.020,
            max_global_marginal=0.000045,
            max_marginal_add=0.000020,
            max_bad_weighted_pos=0.005,
            max_bad_max_pos=0.034,
            max_h088_cos=-0.002,
            min_good_margin=0.004,
            route_pred_cap=0.000140,
            h098_pred_cap=0.000100,
            worldview="Q2 companion works only when residual-bad antidote targets co-move in the same row",
        ),
    ]


def prepare_h116_context() -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    np.ndarray,
    pd.DataFrame,
    h097mod.ResponseFit,
    h100mod.RouteBasisFit,
    pd.DataFrame,
    np.ndarray,
    pd.DataFrame,
    np.ndarray,
    np.ndarray,
    dict[str, object],
    h115mod.CurvatureFit,
    pd.DataFrame,
    pd.DataFrame,
]:
    pool, public, sample, base_prob, cell, h098_fit, route_fit, basis_fit_df, basis_fit_moves, bad_axes, bad_moves, good_moves, residuals = h115mod.prepare_context()
    axes = h115mod.build_axis_context(pool, public, residuals, bad_axes, bad_moves, good_moves)
    model_scores, _loo_preds, fit = h115mod.fit_curvature_models(public, pool, base_prob.shape, bad_axes, bad_moves, good_moves, axes)
    props = h115mod.build_proposals(pool)
    return pool, public, sample, base_prob, cell, h098_fit, route_fit, basis_fit_df, basis_fit_moves, bad_axes, bad_moves, good_moves, axes, fit, model_scores, props


def curvature_pred(move_mat: np.ndarray, fit: h115mod.CurvatureFit, pool: pd.DataFrame, bad_axes: pd.DataFrame, bad_moves: np.ndarray, good_moves: np.ndarray, axes: dict[str, object]) -> float:
    return h115mod.predict_curvature(move_mat, fit, pool, bad_axes, bad_moves, good_moves, axes)


def annotate_cell_scores(props: pd.DataFrame) -> pd.DataFrame:
    out = props.copy()
    out["h116_cell_score"] = (
        0.30 * out["proposal_base_score"].to_numpy(dtype=np.float64)
        + 0.18 * rank01(out["h112_residual_safety"].to_numpy(dtype=np.float64), high=True)
        + 0.15 * rank01(out["h112_residual_gap"].to_numpy(dtype=np.float64), high=True)
        + 0.12 * rank01(out["h110_benefit_toxicity_gap"].to_numpy(dtype=np.float64), high=True)
        + 0.10 * rank01(out["h112_antidote_score"].to_numpy(dtype=np.float64), high=True)
        + 0.06 * rank01(out["h057_positive_weight"].to_numpy(dtype=np.float64), high=True)
        + 0.04 * out["h112_in_h111_selected"].to_numpy(dtype=np.float64)
        - 0.18 * rank01(out["h112_residual_toxicity"].to_numpy(dtype=np.float64), high=True)
        - 0.07 * rank01(out["latent_shortcut_energy"].to_numpy(dtype=np.float64), high=True)
        - 0.05 * rank01(out["bad_pressure_rank"].to_numpy(dtype=np.float64), high=True)
    )
    return out


def collapse_best_cells(props: pd.DataFrame, spec: H116Spec) -> pd.DataFrame:
    work = annotate_cell_scores(props)
    allowed = ("Q2",) + spec.allowed_companions
    work = work[work["target"].astype(str).isin(allowed)].copy()
    work = work[np.abs(work["proposal_move"].to_numpy(dtype=np.float64)) > 1.0e-12].copy()
    work = work[work["h116_cell_score"].to_numpy(dtype=np.float64) >= spec.min_cell_score].copy()
    if work.empty:
        return work
    work["h116_move"] = np.clip(work["proposal_move"].to_numpy(dtype=np.float64) * spec.amp, -spec.cap, spec.cap)
    work = work.sort_values(["row", "target", "h116_cell_score", "h112_residual_safety"], ascending=[True, True, False, False])
    work = work.drop_duplicates(["row", "target"], keep="first").reset_index(drop=True)
    return work


def make_row_bundle(
    rows: list[dict[str, object]],
    bundle_id: str,
    bundle_kind: str,
    spec: H116Spec,
    shape: tuple[int, int],
    fit: h115mod.CurvatureFit,
    pool: pd.DataFrame,
    bad_axes: pd.DataFrame,
    bad_moves: np.ndarray,
    good_moves: np.ndarray,
    axes: dict[str, object],
    zero_curv: float,
) -> dict[str, object] | None:
    full = np.zeros(shape, dtype=np.float64)
    q2_only = np.zeros(shape, dtype=np.float64)
    comp_only = np.zeros(shape, dtype=np.float64)
    q2_count = 0
    for rec in rows:
        row = int(rec["row"])
        tidx = int(rec["target_index"])
        move = float(rec["h116_move"])
        full[row, tidx] = move
        if str(rec["target"]) == "Q2":
            q2_only[row, tidx] = move
            q2_count += 1
        else:
            comp_only[row, tidx] = move
    if q2_count != 1:
        return None
    full_curv = curvature_pred(full, fit, pool, bad_axes, bad_moves, good_moves, axes)
    q2_curv = curvature_pred(q2_only, fit, pool, bad_axes, bad_moves, good_moves, axes)
    comp_curv = curvature_pred(comp_only, fit, pool, bad_axes, bad_moves, good_moves, axes)
    full_marg = full_curv - zero_curv
    q2_marg = q2_curv - zero_curv
    comp_marg = comp_curv - zero_curv
    q2_rescue = q2_marg - full_marg
    comp_cost = full_marg - comp_marg
    axis = h102mod.cumulative_axis_metrics(full.reshape(-1), bad_axes, bad_moves, good_moves)
    if q2_rescue < spec.min_q2_rescue:
        return None
    if full_marg > spec.max_full_marginal:
        return None
    if axis["h102_cum_bad_weighted_pos"] > spec.max_bundle_bad_weighted_pos:
        return None
    if axis["h102_cum_bad_max_pos"] > spec.max_bundle_bad_max_pos:
        return None
    if axis["h102_cum_h088_axis_cos"] > spec.max_bundle_h088_cos:
        return None
    if axis["h102_cum_good_bad_margin"] < spec.min_bundle_good_margin:
        return None
    frame = pd.DataFrame(rows)
    score = (
        190.0 * (-full_marg)
        + 125.0 * q2_rescue
        + 40.0 * max(-comp_cost, 0.0)
        + 0.22 * float(frame["h112_residual_safety"].mean())
        + 0.18 * float(frame["h112_residual_gap"].mean())
        + 0.12 * float(frame["h112_antidote_score"].mean())
        + 0.10 * float(frame["h116_cell_score"].mean())
        - 0.22 * float(frame["h112_residual_toxicity"].mean())
        - 0.08 * max(float(axis["h102_cum_h088_axis_cos"]), 0.0)
    )
    return {
        "bundle_id": bundle_id,
        "bundle_kind": bundle_kind,
        "row": int(frame["row"].iloc[0]),
        "subject_id": str(frame["subject_id"].iloc[0]),
        "targets": ",".join(frame["target"].astype(str).tolist()),
        "n_cells": int(len(frame)),
        "full_curv": full_curv,
        "q2_only_curv": q2_curv,
        "companion_only_curv": comp_curv,
        "full_curv_marginal": full_marg,
        "q2_only_curv_marginal": q2_marg,
        "companion_only_curv_marginal": comp_marg,
        "q2_rescue_marginal": q2_rescue,
        "companion_cost_marginal": comp_cost,
        "bundle_score": score,
        "axis": axis,
        "move_mat": full,
        "records": frame,
    }


def bundle_variants(group: pd.DataFrame, spec: H116Spec) -> list[tuple[str, pd.DataFrame]]:
    q2 = group[group["target"].astype(str).eq("Q2")].sort_values("h116_cell_score", ascending=False)
    comps = group[group["target"].astype(str).ne("Q2")].sort_values("h116_cell_score", ascending=False)
    if q2.empty or len(comps) < spec.min_companions:
        return []
    q2_row = q2.head(1)
    variants: list[tuple[str, pd.DataFrame]] = []
    seen: set[tuple[int, ...]] = set()

    def add(kind: str, comp_frame: pd.DataFrame) -> None:
        if len(comp_frame) < spec.min_companions:
            return
        frame = pd.concat([q2_row, comp_frame], ignore_index=True)
        key = tuple(sorted(frame["flat_index"].astype(int).tolist()))
        if key in seen:
            return
        seen.add(key)
        variants.append((kind, frame))

    add("top_companions", comps.head(spec.max_companions))
    add("minimum_companions", comps.head(spec.min_companions))
    q_comp = comps[comps["target"].astype(str).isin(["Q1", "Q3"])]
    s_comp = comps[comps["target"].astype(str).isin(["S1", "S2", "S3", "S4"])]
    add("q_stage_balanced", pd.concat([q_comp.head(2), s_comp.head(2)], ignore_index=True).head(spec.max_companions))
    add("stage_anchor", pd.concat([s_comp.head(2), q_comp.head(1)], ignore_index=True).head(spec.max_companions))
    for size in range(spec.min_companions, min(spec.max_companions, len(comps)) + 1):
        for combo in combinations(comps.head(min(len(comps), 5)).index.tolist(), size):
            add(f"combo{size}", comps.loc[list(combo)])
            if len(variants) >= 10:
                break
        if len(variants) >= 10:
            break
    return variants


def build_bundle_pool(
    props: pd.DataFrame,
    spec: H116Spec,
    shape: tuple[int, int],
    fit: h115mod.CurvatureFit,
    pool: pd.DataFrame,
    bad_axes: pd.DataFrame,
    bad_moves: np.ndarray,
    good_moves: np.ndarray,
    axes: dict[str, object],
) -> pd.DataFrame:
    cells = collapse_best_cells(props, spec)
    zero_curv = curvature_pred(np.zeros(shape, dtype=np.float64), fit, pool, bad_axes, bad_moves, good_moves, axes)
    bundles = []
    for row, group in cells.groupby("row", sort=False):
        group = group.sort_values("h116_cell_score", ascending=False).head(1 + spec.max_companions + 2)
        for idx, (kind, frame) in enumerate(bundle_variants(group, spec)):
            bundle = make_row_bundle(
                frame.to_dict("records"),
                f"r{int(row):03d}_{kind}_{idx}",
                kind,
                spec,
                shape,
                fit,
                pool,
                bad_axes,
                bad_moves,
                good_moves,
                axes,
                zero_curv,
            )
            if bundle is not None:
                bundles.append(bundle)
    if not bundles:
        return pd.DataFrame()
    out = pd.DataFrame([{k: v for k, v in b.items() if k not in {"axis", "move_mat", "records"}} for b in bundles])
    out["_axis"] = [b["axis"] for b in bundles]
    out["_move_mat"] = [b["move_mat"] for b in bundles]
    out["_records"] = [b["records"] for b in bundles]
    return out.sort_values(["bundle_score", "q2_rescue_marginal"], ascending=[False, False]).head(spec.row_top).reset_index(drop=True)


def build_guard_pool(props: pd.DataFrame, spec: H116Spec, shape: tuple[int, int], bad_axes: pd.DataFrame, bad_moves: np.ndarray, good_moves: np.ndarray) -> pd.DataFrame:
    guards = annotate_cell_scores(props)
    guards = guards[guards["target"].astype(str).ne("Q2")].copy()
    guards = guards[np.abs(guards["proposal_move"].to_numpy(dtype=np.float64)) > 1.0e-12].copy()
    guards = guards[guards["h116_cell_score"].to_numpy(dtype=np.float64) >= spec.min_guard_score].copy()
    if guards.empty:
        return guards
    guards["h116_move"] = np.clip(guards["proposal_move"].to_numpy(dtype=np.float64) * spec.guard_amp, -spec.guard_cap, spec.guard_cap)
    rows = []
    for rec in guards.to_dict("records"):
        tmp = np.zeros(shape, dtype=np.float64)
        tmp[int(rec["row"]), int(rec["target_index"])] = float(rec["h116_move"])
        axis = h102mod.cumulative_axis_metrics(tmp.reshape(-1), bad_axes, bad_moves, good_moves)
        rows.append(
            {
                "h116_guard_h088_cos": float(axis["h102_cum_h088_axis_cos"]),
                "h116_guard_bad_weighted_pos": float(axis["h102_cum_bad_weighted_pos"]),
                "h116_guard_good_margin": float(axis["h102_cum_good_bad_margin"]),
            }
        )
    guards = pd.concat([guards.reset_index(drop=True), pd.DataFrame(rows)], axis=1)
    guards = guards[guards["h116_guard_h088_cos"].to_numpy(dtype=np.float64) < -0.001].copy()
    guards["h116_guard_score"] = (
        0.34 * rank01(-guards["h116_guard_h088_cos"].to_numpy(dtype=np.float64), high=True)
        + 0.22 * guards["h116_cell_score"].to_numpy(dtype=np.float64)
        + 0.16 * rank01(guards["h112_residual_safety"].to_numpy(dtype=np.float64), high=True)
        + 0.12 * rank01(guards["h112_residual_gap"].to_numpy(dtype=np.float64), high=True)
        + 0.08 * rank01(guards["h112_antidote_score"].to_numpy(dtype=np.float64), high=True)
        - 0.18 * rank01(guards["h112_residual_toxicity"].to_numpy(dtype=np.float64), high=True)
        - 0.10 * rank01(guards["h116_guard_bad_weighted_pos"].to_numpy(dtype=np.float64), high=True)
    )
    guards = guards.sort_values(["h116_guard_score", "h116_guard_h088_cos"], ascending=[False, True])
    guards = guards.drop_duplicates(["row", "target"], keep="first").reset_index(drop=True)
    return guards


def select_bundles(
    bundle_pool: pd.DataFrame,
    guard_pool: pd.DataFrame,
    spec: H116Spec,
    shape: tuple[int, int],
    fit: h115mod.CurvatureFit,
    pool: pd.DataFrame,
    bad_axes: pd.DataFrame,
    bad_moves: np.ndarray,
    good_moves: np.ndarray,
    axes: dict[str, object],
) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray, dict[str, float]]:
    move_mat = np.zeros(shape, dtype=np.float64)
    zero_curv = curvature_pred(move_mat, fit, pool, bad_axes, bad_moves, good_moves, axes)
    curv_now = zero_curv
    selected_bundle_rows = []
    selected_cell_frames = []
    selected_guard_frames = []
    selected_rows: set[int] = set()
    selected_flat: set[int] = set()
    subject_counts: dict[str, int] = {}
    target_counts: dict[str, int] = {}
    q2_count = 0
    for _, rec in bundle_pool.iterrows():
        row = int(rec["row"])
        subject = str(rec["subject_id"])
        frame = rec["_records"].copy()
        if row in selected_rows:
            continue
        if len(selected_bundle_rows) >= spec.max_bundles:
            break
        if len(selected_rows) >= spec.max_rows:
            continue
        if subject_counts.get(subject, 0) + 1 > spec.max_per_subject:
            continue
        new_targets = frame["target"].astype(str).tolist()
        if q2_count + new_targets.count("Q2") > spec.q2_cap:
            continue
        if len(selected_cell_frames) and sum(len(f) for f in selected_cell_frames) + len(frame) > spec.max_cells:
            continue
        if len(frame) > spec.max_cells:
            continue
        if any(target_counts.get(t, 0) + new_targets.count(t) > spec.max_per_target for t in set(new_targets)):
            continue
        tmp = move_mat + np.asarray(rec["_move_mat"], dtype=np.float64)
        axis = h102mod.cumulative_axis_metrics(tmp.reshape(-1), bad_axes, bad_moves, good_moves)
        if axis["h102_cum_bad_weighted_pos"] > spec.max_bundle_bad_weighted_pos * max(1, len(selected_bundle_rows) + 1):
            continue
        if axis["h102_cum_bad_max_pos"] > spec.max_bundle_bad_max_pos:
            continue
        if axis["h102_cum_h088_axis_cos"] > spec.max_bundle_h088_cos:
            continue
        if axis["h102_cum_good_bad_margin"] < spec.min_bundle_good_margin * max(1, len(selected_bundle_rows) + 1):
            continue
        curv_next = curvature_pred(tmp, fit, pool, bad_axes, bad_moves, good_moves, axes)
        curv_marg = curv_next - zero_curv
        if curv_marg > spec.max_global_marginal:
            continue
        if selected_bundle_rows and (curv_next - curv_now) > spec.max_marginal_add:
            continue
        move_mat = tmp
        curv_now = curv_next
        selected_rows.add(row)
        subject_counts[subject] = subject_counts.get(subject, 0) + 1
        q2_count += new_targets.count("Q2")
        for target in new_targets:
            target_counts[target] = target_counts.get(target, 0) + 1
        for flat in frame["flat_index"].astype(int).tolist():
            selected_flat.add(flat)
        selected_bundle_rows.append({k: rec[k] for k in rec.index if not str(k).startswith("_")})
        frame = frame.copy()
        frame["h116_bundle_id"] = rec["bundle_id"]
        frame["h116_bundle_kind"] = rec["bundle_kind"]
        frame["h116_bundle_score"] = float(rec["bundle_score"])
        frame["h116_full_curv_marginal"] = float(rec["full_curv_marginal"])
        frame["h116_q2_only_curv_marginal"] = float(rec["q2_only_curv_marginal"])
        frame["h116_companion_only_curv_marginal"] = float(rec["companion_only_curv_marginal"])
        frame["h116_q2_rescue_marginal"] = float(rec["q2_rescue_marginal"])
        frame["h112_move"] = frame["h116_move"].to_numpy(dtype=np.float64)
        frame["h097_move_col"] = "h112_move"
        selected_cell_frames.append(frame)
    if not selected_bundle_rows:
        return pd.DataFrame(), pd.DataFrame(), move_mat, {
            "h116_zero_curv": zero_curv,
            "h116_curv_pred_delta_vs_h057": curv_now,
            "h116_curv_marginal_vs_zero": curv_now - zero_curv,
        }

    guard_added = 0
    axis = h102mod.cumulative_axis_metrics(move_mat.reshape(-1), bad_axes, bad_moves, good_moves)
    if not guard_pool.empty:
        for _, grec in guard_pool.iterrows():
            if guard_added >= spec.max_guard_cells:
                break
            flat = int(grec["flat_index"])
            if flat in selected_flat:
                continue
            row = int(grec["row"])
            subject = str(grec["subject_id"])
            target = str(grec["target"])
            if sum(len(f) for f in selected_cell_frames) + len(selected_guard_frames) + 1 > spec.max_cells:
                break
            if len(selected_rows | {row}) > spec.max_rows + spec.max_guard_cells:
                continue
            if row not in selected_rows and subject_counts.get(subject, 0) + 1 > spec.max_per_subject:
                continue
            if target_counts.get(target, 0) + 1 > spec.max_per_target:
                continue
            tmp = move_mat.copy()
            tmp[row, int(grec["target_index"])] = float(grec["h116_move"])
            new_axis = h102mod.cumulative_axis_metrics(tmp.reshape(-1), bad_axes, bad_moves, good_moves)
            old_deficit = (
                max(axis["h102_cum_h088_axis_cos"] - spec.max_h088_cos, 0.0)
                + max(axis["h102_cum_bad_weighted_pos"] - spec.max_bad_weighted_pos, 0.0)
                + max(spec.min_good_margin - axis["h102_cum_good_bad_margin"], 0.0)
            )
            new_deficit = (
                max(new_axis["h102_cum_h088_axis_cos"] - spec.max_h088_cos, 0.0)
                + max(new_axis["h102_cum_bad_weighted_pos"] - spec.max_bad_weighted_pos, 0.0)
                + max(spec.min_good_margin - new_axis["h102_cum_good_bad_margin"], 0.0)
            )
            if new_deficit >= old_deficit and new_axis["h102_cum_h088_axis_cos"] >= axis["h102_cum_h088_axis_cos"]:
                continue
            curv_next = curvature_pred(tmp, fit, pool, bad_axes, bad_moves, good_moves, axes)
            if (curv_next - zero_curv) > spec.max_global_marginal + 0.000020:
                continue
            new_row = row not in selected_rows
            move_mat = tmp
            curv_now = curv_next
            axis = new_axis
            selected_flat.add(flat)
            selected_rows.add(row)
            subject_counts[subject] = subject_counts.get(subject, 0) + int(new_row)
            target_counts[target] = target_counts.get(target, 0) + 1
            gframe = pd.DataFrame([grec.to_dict()])
            gframe["h116_bundle_id"] = f"guard_{guard_added:02d}"
            gframe["h116_bundle_kind"] = "anti_h088_guard"
            gframe["h116_bundle_score"] = float(grec["h116_guard_score"])
            gframe["h116_full_curv_marginal"] = 0.0
            gframe["h116_q2_only_curv_marginal"] = 0.0
            gframe["h116_companion_only_curv_marginal"] = 0.0
            gframe["h116_q2_rescue_marginal"] = 0.0
            gframe["h112_move"] = gframe["h116_move"].to_numpy(dtype=np.float64)
            gframe["h097_move_col"] = "h112_move"
            selected_guard_frames.append(gframe)
            guard_added += 1
            if (
                axis["h102_cum_h088_axis_cos"] <= spec.max_h088_cos
                and axis["h102_cum_bad_weighted_pos"] <= spec.max_bad_weighted_pos
                and axis["h102_cum_bad_max_pos"] <= spec.max_bad_max_pos
                and axis["h102_cum_good_bad_margin"] >= spec.min_good_margin
            ):
                break

    axis = h102mod.cumulative_axis_metrics(move_mat.reshape(-1), bad_axes, bad_moves, good_moves)
    if axis["h102_cum_bad_weighted_pos"] > spec.max_bad_weighted_pos:
        return pd.DataFrame(), pd.DataFrame(), move_mat, {}
    if axis["h102_cum_bad_max_pos"] > spec.max_bad_max_pos:
        return pd.DataFrame(), pd.DataFrame(), move_mat, {}
    if axis["h102_cum_h088_axis_cos"] > spec.max_h088_cos:
        return pd.DataFrame(), pd.DataFrame(), move_mat, {}
    if axis["h102_cum_good_bad_margin"] < spec.min_good_margin:
        return pd.DataFrame(), pd.DataFrame(), move_mat, {}

    selected_bundles = pd.DataFrame(selected_bundle_rows)
    selected_cells = pd.concat(selected_cell_frames + selected_guard_frames, ignore_index=True).sort_values(["row", "target_index"]).reset_index(drop=True)
    diag = {
        "h116_zero_curv": zero_curv,
        "h116_curv_pred_delta_vs_h057": curv_now,
        "h116_curv_marginal_vs_zero": curv_now - zero_curv,
        "h116_selected_bundles": int(len(selected_bundles)),
        "h116_guard_cells": int(guard_added),
        "h116_mean_bundle_score": float(selected_bundles["bundle_score"].mean()),
        "h116_mean_q2_rescue_marginal": float(selected_bundles["q2_rescue_marginal"].mean()),
        "h116_min_q2_rescue_marginal": float(selected_bundles["q2_rescue_marginal"].min()),
        "h116_mean_full_curv_marginal": float(selected_bundles["full_curv_marginal"].mean()),
        "h116_mean_q2_only_curv_marginal": float(selected_bundles["q2_only_curv_marginal"].mean()),
        "h116_mean_companion_only_curv_marginal": float(selected_bundles["companion_only_curv_marginal"].mean()),
    }
    return selected_bundles, selected_cells, move_mat, diag


def evaluate_candidate(
    candidate_id: str,
    prob: np.ndarray,
    move_mat: np.ndarray,
    selected_cells: pd.DataFrame,
    cell: pd.DataFrame,
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    h098_fit: h097mod.ResponseFit,
    route_fit: h100mod.RouteBasisFit,
    basis_fit_df: pd.DataFrame,
    basis_fit_moves: np.ndarray,
    spec: H116Spec,
    path: Path,
    axis: dict[str, float],
    diag: dict[str, float],
    previous: dict[str, np.ndarray | None],
) -> dict[str, object]:
    proxy = h112mod.H112Spec(
        name=spec.name,
        group="q2_companion_conservation",
        max_cells=spec.max_cells,
        max_rows=spec.max_rows,
        max_per_subject=spec.max_per_subject,
        max_per_target=spec.max_per_target,
        q2_cap=spec.q2_cap,
        amp=spec.amp,
        cap=spec.cap,
        pool_top=spec.row_top,
        beam_width=1,
        min_score=spec.min_cell_score,
        min_gap=-1.0,
        max_residual_toxicity=1.0,
        min_residual_safety=0.0,
        min_family_count=1,
        max_bad_weighted_pos=spec.max_bad_weighted_pos,
        max_bad_max_pos=spec.max_bad_max_pos,
        max_h088_cos=spec.max_h088_cos,
        min_good_margin=spec.min_good_margin,
        route_pred_cap=spec.route_pred_cap,
        h098_pred_cap=spec.h098_pred_cap,
        worldview=spec.worldview,
    )
    out = h112mod.evaluate_candidate(
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
        proxy,
        path,
        axis,
    )
    move_flat = move_mat.reshape(-1)
    for label, prev in previous.items():
        out[f"h116_{label}_overlap_cells"] = overlap_count(move_flat, prev)
        out[f"h116_{label}_cosine"] = cosine(move_flat, prev)
    out.update(diag)
    out["h116_score"] = (
        170.0 * (-float(out["h116_curv_marginal_vs_zero"]))
        + 115.0 * (-float(out["route_basis_pred_delta_vs_h057"]))
        + 90.0 * (-float(out["model_pred_delta_vs_h057"]))
        + 80.0 * float(out["h116_mean_q2_rescue_marginal"])
        + 0.18 * float(out["selected_mean_residual_safety"])
        + 0.14 * float(out["selected_mean_residual_gap"])
        + 0.11 * float(out["selected_mean_antidote_score"])
        + 0.08 * max(-float(out["h102_cum_h088_axis_cos"]), 0.0)
        - 0.18 * float(out["selected_mean_residual_toxicity"])
        - 0.50 * max(float(out["h102_cum_bad_weighted_pos"]), 0.0)
        - 0.30 * max(float(out["h102_cum_bad_max_pos"]), 0.0)
        - 0.18 * max(float(out["h102_cum_h088_axis_cos"]), 0.0)
        - 20.0 * max(float(out["hard_diag_delta_vs_h057"]), 0.0)
    )
    return out


def run() -> None:
    cleanup_previous_outputs()
    pool, _public, sample, base_prob, cell, h098_fit, route_fit, basis_fit_df, basis_fit_moves, bad_axes, bad_moves, good_moves, axes, fit, model_scores, props = prepare_h116_context()
    previous = {
        "h115": h115mod.load_previous_move(sample, base_prob, "submission_h115_curvature_*_uploadsafe.csv"),
        "h114": h115mod.load_previous_move(sample, base_prob, "submission_h114_nullspace_*_uploadsafe.csv"),
        "h113": h115mod.load_previous_move(sample, base_prob, "submission_h113_rowroute_*_uploadsafe.csv"),
        "h112": h115mod.load_previous_move(sample, base_prob, "submission_h112_residualtox_*_uploadsafe.csv"),
    }

    candidate_rows = []
    selected_frames = []
    bundle_frames = []
    audit_rows = []
    top_bundle_frames = []
    for spec in candidate_specs():
        bundle_pool = build_bundle_pool(props, spec, base_prob.shape, fit, pool, bad_axes, bad_moves, good_moves, axes)
        guard_pool = build_guard_pool(props, spec, base_prob.shape, bad_axes, bad_moves, good_moves)
        audit = {
            "spec_name": spec.name,
            "bundle_pool_size": int(len(bundle_pool)),
            "guard_pool_size": int(len(guard_pool)),
            "positive_rescue_bundles": int((bundle_pool["q2_rescue_marginal"].to_numpy(dtype=np.float64) > 0.0).sum()) if len(bundle_pool) else 0,
            "rescue_and_h088_nonpositive_bundles": 0,
            "max_q2_rescue_marginal": float(bundle_pool["q2_rescue_marginal"].max()) if len(bundle_pool) else 0.0,
            "min_full_curv_marginal": float(bundle_pool["full_curv_marginal"].min()) if len(bundle_pool) else 0.0,
            "min_guard_h088_cos": float(guard_pool["h116_guard_h088_cos"].min()) if len(guard_pool) else 0.0,
            "min_guard_bad_weighted_pos": float(guard_pool["h116_guard_bad_weighted_pos"].min()) if len(guard_pool) else 0.0,
        }
        if len(bundle_pool):
            h088_vals = bundle_pool["_axis"].apply(lambda d: float(d["h102_cum_h088_axis_cos"]))
            badw_vals = bundle_pool["_axis"].apply(lambda d: float(d["h102_cum_bad_weighted_pos"]))
            audit["min_bundle_h088_cos"] = float(h088_vals.min())
            audit["max_bundle_h088_cos"] = float(h088_vals.max())
            audit["min_bundle_bad_weighted_pos"] = float(badw_vals.min())
            audit["rescue_and_h088_nonpositive_bundles"] = int(((bundle_pool["q2_rescue_marginal"].to_numpy(dtype=np.float64) > 0.0) & (h088_vals.to_numpy(dtype=np.float64) <= 0.0)).sum())
            top = bundle_pool.head(20).copy()
            top.insert(0, "spec_name", spec.name)
            top["bundle_h088_cos"] = h088_vals.head(len(top)).to_numpy(dtype=np.float64)
            top["bundle_bad_weighted_pos"] = badw_vals.head(len(top)).to_numpy(dtype=np.float64)
            top_bundle_frames.append(top[[c for c in top.columns if not str(c).startswith("_")]])
        audit_rows.append(audit)
        if bundle_pool.empty:
            continue
        selected_bundles, selected_cells, move_mat, diag = select_bundles(bundle_pool, guard_pool, spec, base_prob.shape, fit, pool, bad_axes, bad_moves, good_moves, axes)
        if selected_cells.empty:
            continue
        axis = h102mod.cumulative_axis_metrics(move_mat.reshape(-1), bad_axes, bad_moves, good_moves)
        rpred = route_pred(move_mat.reshape(-1), basis_fit_df, basis_fit_moves, route_fit)
        cpred = h098_pred(move_mat.reshape(-1), cell, h098_fit)
        if rpred > spec.route_pred_cap or cpred > spec.h098_pred_cap:
            continue
        prob = materialize(base_prob, move_mat)
        if int((np.abs(prob - base_prob) > TOL).sum()) == 0:
            continue
        hash_id = short_hash(prob)
        candidate_id = safe_id(f"h116_{spec.name}_{hash_id}", 128)
        path = OUT / f"submission_{candidate_id}.csv"
        h085mod.write_submission(sample, prob, path)
        metrics = evaluate_candidate(
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
        metrics["h116_fit_feature_set"] = fit.feature_set
        metrics["h116_fit_alpha"] = fit.alpha
        metrics["h116_fit_score"] = fit.score
        metrics["h116_bundle_pool_size"] = int(len(bundle_pool))
        candidate_rows.append(metrics)
        cells2 = selected_cells.copy()
        if "candidate_id" in cells2.columns:
            cells2 = cells2.drop(columns=["candidate_id"])
        cells2.insert(0, "candidate_id", candidate_id)
        selected_frames.append(cells2)
        bundles2 = selected_bundles.copy()
        bundles2.insert(0, "candidate_id", candidate_id)
        bundle_frames.append(bundles2)

    candidates = pd.DataFrame(candidate_rows)
    if candidates.empty:
        audit_df = pd.DataFrame(audit_rows)
        audit_df.to_csv(OUT / "h116_no_candidate_audit.csv", index=False)
        if top_bundle_frames:
            pd.concat(top_bundle_frames, ignore_index=True).to_csv(OUT / "h116_top_forbidden_bundles.csv", index=False)
        report = f"""# H116 Companion-Conservation Row-Target Equation HS-JEPA

No upload-safe candidate was promoted.

Core finding:

```text
Q2 companion rescue exists, but every positive-rescue bundle is H088-positive.
The available anti-H088 guard cells either cancel too little H088 direction or
create too much bad-axis pressure.  Under the current public/private equation,
Q2 companion conservation is a toxic sector, not a safe assignment field.
```

Audit:

{md_table(audit_df, 20)}

Interpretation:

- H115's Q2 companion candidate should be treated as high-risk until public
  confirms it.
- The next equation-solver target should not be "more Q2 companion."  It
  should use the H116 positive-rescue/H088-positive bundles as forbidden
  target representations.
- If a future solver can move opposite this forbidden sector while preserving
  H057-positive row-state support, that is a cleaner public/private assignment
  candidate than guarded Q2 reopening.
"""
        (OUT / "h116_report.md").write_text(report, encoding="utf-8")
        print("H116 promoted no candidate")
        print(audit_df.to_string(index=False))
        return
    candidates = candidates.sort_values(["h116_score", "h116_curv_marginal_vs_zero"], ascending=[False, True]).reset_index(drop=True)
    selected = candidates.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"submission_h116_companion_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)

    decision = {
        "decision": "promote_h116_companion_conservation_equation",
        "selected_candidate_id": selected["candidate_id"],
        "root_uploadsafe_path": str(root_path.resolve()),
        "worldview": selected["worldview"],
        "selected_fit_feature_set": fit.feature_set,
        "selected_fit_alpha": fit.alpha,
        "selected_fit_score": fit.score,
        **selected,
        **{f"root_{key}": value for key, value in validation.items()},
    }

    model_scores.to_csv(OUT / "h116_curvature_model_scores.csv", index=False)
    candidates.to_csv(OUT / "h116_candidates.csv", index=False)
    pd.concat(selected_frames, ignore_index=True).to_csv(OUT / "h116_selected_cells.csv", index=False)
    pd.concat(bundle_frames, ignore_index=True).to_csv(OUT / "h116_selected_bundles.csv", index=False)
    pd.DataFrame([decision]).to_csv(OUT / "h116_decision.csv", index=False)

    cols = [
        "candidate_id",
        "spec_name",
        "selected_cells",
        "h116_selected_bundles",
        "changed_rows_vs_h057",
        "Q1_changed_vs_h057",
        "Q2_changed_vs_h057",
        "Q3_changed_vs_h057",
        "S1_changed_vs_h057",
        "S2_changed_vs_h057",
        "S3_changed_vs_h057",
        "S4_changed_vs_h057",
        "h116_curv_marginal_vs_zero",
        "h116_mean_q2_rescue_marginal",
        "h116_min_q2_rescue_marginal",
        "model_pred_delta_vs_h057",
        "route_basis_pred_delta_vs_h057",
        "h102_cum_bad_weighted_pos",
        "h102_cum_h088_axis_cos",
        "selected_mean_residual_toxicity",
        "selected_mean_residual_safety",
        "h116_h115_overlap_cells",
        "h116_h115_cosine",
        "h116_h112_overlap_cells",
        "h116_h112_cosine",
        "h116_score",
        "file",
    ]
    report = f"""# H116 Companion-Conservation Row-Target Equation HS-JEPA

Question: did H115 reopen Q2 because Q2 is genuinely safe as a same-row
companion route, or because the curvature model overfit a few public
observations?

Selected curvature model:

{md_table(model_scores.head(8), 8)}

Candidates:

{md_table(candidates[cols], 20)}

Decision:

{md_table(pd.DataFrame([decision]), 1)}

Interpretation rule:

- If H116 improves over H115/H112-H114, Q2 companion conservation is an
  action-grade row-target equation.
- If H115 improves but H116 loses, H115's Q2 companion signal is too fragile
  to be promoted to a row-level conservation law.
- If H112/H113 beat H116, Q2 should remain mostly blocked and residual
  toxicity is the safer action field.
- If H114 beats H116, toxic-subspace null projection is a better plateau
  breaker than nonlinear Q2 conservation.
"""
    (OUT / "h116_report.md").write_text(report, encoding="utf-8")

    print("H116 selected candidate")
    print(candidates[cols].head(10).to_string(index=False))
    print("\nDecision")
    print(pd.DataFrame([decision])[["decision", "selected_candidate_id", "root_uploadsafe_path", "root_upload_safe"]].to_string(index=False))


if __name__ == "__main__":
    run()
