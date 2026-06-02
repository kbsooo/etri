#!/usr/bin/env python3
"""H118: forbidden-sector veto assignment HS-JEPA.

H117 showed that the H116 forbidden Q2-companion sector is not invertible in
the current proposal space.  H118 uses the same representation differently:
not as a target to invert, but as a veto field.

Allowed action:
    non-Q2 residual/nullspace proposals
    with near-zero same-direction exposure to H116 forbidden sector
    under H102/H112/H115 public/private stress.
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
OUT = HITL / "h118_forbidden_veto_assignment_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H117_PATH = HITL / "h117_forbidden_companion_sector_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h117mod", H117_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H117_PATH}")
h117mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h117mod
SPEC.loader.exec_module(h117mod)

h116mod = h117mod.h116mod
h115mod = h117mod.h115mod
h112mod = h117mod.h112mod
h102mod = h117mod.h102mod
h100mod = h117mod.h100mod
h097mod = h117mod.h097mod
h085mod = h117mod.h085mod

TARGETS = h117mod.TARGETS
KEYS = h117mod.KEYS
BASE_FILE = h117mod.BASE_FILE
TOL = h117mod.TOL


@dataclass(frozen=True)
class H118Spec:
    name: str
    group: str
    max_cells: int
    max_rows: int
    max_per_subject: int
    max_per_target: int
    amp: float
    cap: float
    pool_top: int
    max_forbidden_same: float
    max_forbidden_pressure: float
    min_residual_safety: float
    max_residual_toxicity: float
    min_residual_gap: float
    min_score: float
    max_curv_marginal: float
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
    for path in OUT.glob("submission_h118_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h118_forbiddenveto_*.csv"):
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


def candidate_specs() -> list[H118Spec]:
    return [
        H118Spec(
            name="veto_h112_core_c44_a050",
            group="h112_core",
            max_cells=44,
            max_rows=28,
            max_per_subject=8,
            max_per_target=15,
            amp=0.50,
            cap=0.18,
            pool_top=160,
            max_forbidden_same=1.0e-12,
            max_forbidden_pressure=0.02,
            min_residual_safety=0.54,
            max_residual_toxicity=0.55,
            min_residual_gap=0.05,
            min_score=0.16,
            max_curv_marginal=0.000040,
            max_marginal_add=0.000018,
            max_bad_weighted_pos=0.006,
            max_bad_max_pos=0.038,
            max_h088_cos=-0.004,
            min_good_margin=0.006,
            route_pred_cap=0.000120,
            h098_pred_cap=0.000090,
            worldview="H112 residual-safe cells are action-grade only after H116 forbidden-sector veto",
        ),
        H118Spec(
            name="veto_h114_null_c36_a055",
            group="h114_null",
            max_cells=36,
            max_rows=30,
            max_per_subject=7,
            max_per_target=13,
            amp=0.55,
            cap=0.18,
            pool_top=150,
            max_forbidden_same=1.0e-12,
            max_forbidden_pressure=0.02,
            min_residual_safety=0.50,
            max_residual_toxicity=0.58,
            min_residual_gap=0.03,
            min_score=0.10,
            max_curv_marginal=0.000045,
            max_marginal_add=0.000020,
            max_bad_weighted_pos=0.007,
            max_bad_max_pos=0.040,
            max_h088_cos=-0.004,
            min_good_margin=0.004,
            route_pred_cap=0.000150,
            h098_pred_cap=0.000110,
            worldview="H114 nullspace cells become safer when the forbidden Q2 companion sector is a hard veto",
        ),
        H118Spec(
            name="veto_antidote_c52_a046",
            group="antidote",
            max_cells=52,
            max_rows=34,
            max_per_subject=9,
            max_per_target=18,
            amp=0.46,
            cap=0.17,
            pool_top=190,
            max_forbidden_same=1.0e-12,
            max_forbidden_pressure=0.02,
            min_residual_safety=0.50,
            max_residual_toxicity=0.60,
            min_residual_gap=0.02,
            min_score=0.12,
            max_curv_marginal=0.000050,
            max_marginal_add=0.000022,
            max_bad_weighted_pos=0.008,
            max_bad_max_pos=0.044,
            max_h088_cos=-0.003,
            min_good_margin=0.003,
            route_pred_cap=0.000160,
            h098_pred_cap=0.000115,
            worldview="H010/E216/LeJEPA antidote cells are safe if they avoid the forbidden companion sector",
        ),
        H118Spec(
            name="veto_stage_balance_c48_a042",
            group="stage_balance",
            max_cells=48,
            max_rows=34,
            max_per_subject=9,
            max_per_target=16,
            amp=0.42,
            cap=0.16,
            pool_top=180,
            max_forbidden_same=1.0e-12,
            max_forbidden_pressure=0.02,
            min_residual_safety=0.48,
            max_residual_toxicity=0.62,
            min_residual_gap=0.00,
            min_score=0.08,
            max_curv_marginal=0.000050,
            max_marginal_add=0.000022,
            max_bad_weighted_pos=0.008,
            max_bad_max_pos=0.044,
            max_h088_cos=-0.002,
            min_good_margin=0.003,
            route_pred_cap=0.000170,
            h098_pred_cap=0.000120,
            worldview="safe assignment is a non-Q2 Q3/S-stage balance outside the forbidden Q2 sector",
        ),
    ]


def prepare_context():
    return h117mod.prepare_context()


def curvature_pred(move_mat: np.ndarray, fit: h115mod.CurvatureFit, pool: pd.DataFrame, bad_axes: pd.DataFrame, bad_moves: np.ndarray, good_moves: np.ndarray, axes: dict[str, object]) -> float:
    return h115mod.predict_curvature(move_mat, fit, pool, bad_axes, bad_moves, good_moves, axes)


def target_allowed(work: pd.DataFrame, group: str) -> np.ndarray:
    target = work["target"].astype(str)
    src = work["proposal_source"].astype(str)
    base = target.ne("Q2").to_numpy()
    if group == "h112_core":
        return base & (
            src.str.contains("h112", regex=False).to_numpy()
            | work["h112_in_h111_selected"].astype(float).gt(0.5).to_numpy()
        )
    if group == "h114_null":
        return base & (
            src.str.contains("h114", regex=False).to_numpy()
            | work["h114_null_move"].fillna(0.0).astype(float).abs().gt(1.0e-12).to_numpy()
        )
    if group == "antidote":
        return base & (
            work["h112_antidote_score"].astype(float).ge(0.62).to_numpy()
            | src.str.contains("h010_e216|antidote", regex=True).to_numpy()
        )
    if group == "stage_balance":
        return target.isin(["Q3", "S1", "S2", "S3", "S4"]).to_numpy()
    raise ValueError(group)


def annotate_veto_scores(scored: pd.DataFrame) -> pd.DataFrame:
    out = scored.copy()
    out["h118_forbidden_veto_score"] = 1.0 - np.minimum(out["h117_forbidden_pressure"].to_numpy(dtype=np.float64), 1.0)
    out["h118_score_base"] = (
        0.26 * out["h116_cell_score"].to_numpy(dtype=np.float64)
        + 0.22 * rank01(out["h112_residual_safety"].to_numpy(dtype=np.float64), high=True)
        + 0.17 * rank01(out["h112_residual_gap"].to_numpy(dtype=np.float64), high=True)
        + 0.14 * rank01(out["h112_antidote_score"].to_numpy(dtype=np.float64), high=True)
        + 0.10 * rank01(out["h110_benefit_toxicity_gap"].to_numpy(dtype=np.float64), high=True)
        + 0.09 * out["h118_forbidden_veto_score"].to_numpy(dtype=np.float64)
        + 0.04 * out["h112_in_h111_selected"].to_numpy(dtype=np.float64)
        - 0.18 * rank01(out["h112_residual_toxicity"].to_numpy(dtype=np.float64), high=True)
        - 0.10 * rank01(out["latent_shortcut_energy"].to_numpy(dtype=np.float64), high=True)
        - 0.08 * rank01(out["h117_forbidden_same"].to_numpy(dtype=np.float64), high=True)
    )
    return out


def select_cells(
    scored: pd.DataFrame,
    spec: H118Spec,
    shape: tuple[int, int],
    fit: h115mod.CurvatureFit,
    pool: pd.DataFrame,
    bad_axes: pd.DataFrame,
    bad_moves: np.ndarray,
    good_moves: np.ndarray,
    axes: dict[str, object],
) -> tuple[pd.DataFrame, np.ndarray, dict[str, float], dict[str, float]]:
    work = scored[target_allowed(scored, spec.group)].copy()
    work = work[work["h117_forbidden_same"].to_numpy(dtype=np.float64) <= spec.max_forbidden_same].copy()
    work = work[work["h117_forbidden_pressure"].to_numpy(dtype=np.float64) <= spec.max_forbidden_pressure].copy()
    work = work[work["h112_residual_safety"].to_numpy(dtype=np.float64) >= spec.min_residual_safety].copy()
    work = work[work["h112_residual_toxicity"].to_numpy(dtype=np.float64) <= spec.max_residual_toxicity].copy()
    work = work[work["h112_residual_gap"].to_numpy(dtype=np.float64) >= spec.min_residual_gap].copy()
    work = work[work["h118_score_base"].to_numpy(dtype=np.float64) >= spec.min_score].copy()
    if work.empty:
        return pd.DataFrame(), np.zeros(shape, dtype=np.float64), {}, {}
    work["h118_move"] = np.clip(work["proposal_move"].to_numpy(dtype=np.float64) * spec.amp, -spec.cap, spec.cap)
    work["h118_score"] = (
        0.36 * work["h118_score_base"].to_numpy(dtype=np.float64)
        + 0.18 * rank01(work["h112_residual_safety"].to_numpy(dtype=np.float64), high=True)
        + 0.14 * rank01(work["h112_residual_gap"].to_numpy(dtype=np.float64), high=True)
        + 0.12 * rank01(np.abs(work["h118_move"].to_numpy(dtype=np.float64)), high=True)
        + 0.10 * rank01(work["h112_antidote_score"].to_numpy(dtype=np.float64), high=True)
        - 0.18 * rank01(work["h112_residual_toxicity"].to_numpy(dtype=np.float64), high=True)
    )
    work = work.sort_values(["h118_score", "h112_residual_safety"], ascending=[False, False])
    work = work.drop_duplicates(["row", "target"], keep="first").head(spec.pool_top).reset_index(drop=True)

    move_mat = np.zeros(shape, dtype=np.float64)
    zero_curv = curvature_pred(move_mat, fit, pool, bad_axes, bad_moves, good_moves, axes)
    curv_now = zero_curv
    selected_idx = []
    selected_flat: set[int] = set()
    selected_rows: set[int] = set()
    subject_counts: dict[str, int] = {}
    target_counts: dict[str, int] = {}
    axis = h102mod.cumulative_axis_metrics(move_mat.reshape(-1), bad_axes, bad_moves, good_moves)
    for idx, rec in enumerate(work.to_dict("records")):
        flat = int(rec["flat_index"])
        if flat in selected_flat:
            continue
        if len(selected_idx) >= spec.max_cells:
            break
        row = int(rec["row"])
        subject = str(rec["subject_id"])
        target = str(rec["target"])
        tidx = int(rec["target_index"])
        if row not in selected_rows and len(selected_rows) >= spec.max_rows:
            continue
        if row not in selected_rows and subject_counts.get(subject, 0) + 1 > spec.max_per_subject:
            continue
        if target_counts.get(target, 0) >= spec.max_per_target:
            continue
        tmp = move_mat.copy()
        tmp[row, tidx] = float(rec["h118_move"])
        next_axis = h102mod.cumulative_axis_metrics(tmp.reshape(-1), bad_axes, bad_moves, good_moves)
        if next_axis["h102_cum_bad_weighted_pos"] > spec.max_bad_weighted_pos:
            continue
        if next_axis["h102_cum_bad_max_pos"] > spec.max_bad_max_pos:
            continue
        if next_axis["h102_cum_h088_axis_cos"] > spec.max_h088_cos:
            continue
        if next_axis["h102_cum_good_bad_margin"] < spec.min_good_margin:
            continue
        curv_next = curvature_pred(tmp, fit, pool, bad_axes, bad_moves, good_moves, axes)
        if curv_next - zero_curv > spec.max_curv_marginal:
            continue
        if selected_idx and (curv_next - curv_now) > spec.max_marginal_add:
            continue
        move_mat = tmp
        curv_now = curv_next
        axis = next_axis
        selected_idx.append(idx)
        selected_flat.add(flat)
        if row not in selected_rows:
            selected_rows.add(row)
            subject_counts[subject] = subject_counts.get(subject, 0) + 1
        target_counts[target] = target_counts.get(target, 0) + 1
    if not selected_idx:
        return pd.DataFrame(), move_mat, axis, {
            "h118_zero_curv": zero_curv,
            "h118_curv_pred_delta_vs_h057": curv_now,
            "h118_curv_marginal_vs_zero": curv_now - zero_curv,
        }
    selected = work.iloc[selected_idx].copy().sort_values(["row", "target_index"]).reset_index(drop=True)
    selected["h112_move"] = [
        move_mat[int(row), int(tidx)]
        for row, tidx in zip(selected["row"].astype(int), selected["target_index"].astype(int))
    ]
    selected["h097_move_col"] = "h112_move"
    diag = {
        "h118_zero_curv": zero_curv,
        "h118_curv_pred_delta_vs_h057": curv_now,
        "h118_curv_marginal_vs_zero": curv_now - zero_curv,
        "h118_mean_forbidden_same": float(selected["h117_forbidden_same"].mean()),
        "h118_max_forbidden_same": float(selected["h117_forbidden_same"].max()),
        "h118_mean_forbidden_pressure": float(selected["h117_forbidden_pressure"].mean()),
        "h118_mean_veto_score": float(selected["h118_forbidden_veto_score"].mean()),
        "h118_selected_rows": int(len(selected_rows)),
    }
    return selected, move_mat, axis, diag


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
    spec: H118Spec,
    path: Path,
    axis: dict[str, float],
    diag: dict[str, float],
    previous: dict[str, np.ndarray | None],
) -> dict[str, object]:
    proxy = h112mod.H112Spec(
        name=spec.name,
        group=f"forbidden_veto_{spec.group}",
        max_cells=spec.max_cells,
        max_rows=spec.max_rows,
        max_per_subject=spec.max_per_subject,
        max_per_target=spec.max_per_target,
        q2_cap=0,
        amp=spec.amp,
        cap=spec.cap,
        pool_top=spec.pool_top,
        beam_width=1,
        min_score=spec.min_score,
        min_gap=spec.min_residual_gap,
        max_residual_toxicity=spec.max_residual_toxicity,
        min_residual_safety=spec.min_residual_safety,
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
        out[f"h118_{label}_overlap_cells"] = overlap_count(move_flat, prev)
        out[f"h118_{label}_cosine"] = cosine(move_flat, prev)
    out.update(diag)
    out["h118_score"] = (
        150.0 * (-float(out["h118_curv_marginal_vs_zero"]))
        + 115.0 * (-float(out["route_basis_pred_delta_vs_h057"]))
        + 90.0 * (-float(out["model_pred_delta_vs_h057"]))
        + 0.22 * float(out["selected_mean_residual_safety"])
        + 0.18 * float(out["selected_mean_residual_gap"])
        + 0.12 * float(out["selected_mean_antidote_score"])
        + 0.10 * float(out["h118_mean_veto_score"])
        + 0.08 * max(-float(out["h102_cum_h088_axis_cos"]), 0.0)
        - 0.20 * float(out["selected_mean_residual_toxicity"])
        - 0.12 * float(out["h118_mean_forbidden_pressure"])
        - 0.50 * max(float(out["h102_cum_bad_weighted_pos"]), 0.0)
        - 0.30 * max(float(out["h102_cum_bad_max_pos"]), 0.0)
        - 20.0 * max(float(out["hard_diag_delta_vs_h057"]), 0.0)
    )
    return out


def run() -> None:
    cleanup_previous_outputs()
    pool, _public, sample, base_prob, cell, h098_fit, route_fit, basis_fit_df, basis_fit_moves, bad_axes, bad_moves, good_moves, axes, fit, model_scores, props = prepare_context()
    forbidden_axes, forbidden_weights, forbidden_audit = h117mod.build_forbidden_axes(props, base_prob.shape, fit, pool, bad_axes, bad_moves, good_moves, axes)
    scored_raw = h117mod.annotate_forbidden_scores(props, forbidden_axes, forbidden_weights)
    scored = annotate_veto_scores(scored_raw)
    previous = {
        "h115": h115mod.load_previous_move(sample, base_prob, "submission_h115_curvature_*_uploadsafe.csv"),
        "h114": h115mod.load_previous_move(sample, base_prob, "submission_h114_nullspace_*_uploadsafe.csv"),
        "h113": h115mod.load_previous_move(sample, base_prob, "submission_h113_rowroute_*_uploadsafe.csv"),
        "h112": h115mod.load_previous_move(sample, base_prob, "submission_h112_residualtox_*_uploadsafe.csv"),
    }

    audit_rows = []
    candidate_rows = []
    selected_frames = []
    for spec in candidate_specs():
        pre = scored[target_allowed(scored, spec.group)].copy()
        audit_rows.append(
            {
                "spec_name": spec.name,
                "prefilter_rows": int(len(pre)),
                "forbidden_same_pass": int((pre["h117_forbidden_same"].to_numpy(dtype=np.float64) <= spec.max_forbidden_same).sum()),
                "residual_safety_pass": int((pre["h112_residual_safety"].to_numpy(dtype=np.float64) >= spec.min_residual_safety).sum()),
                "residual_toxicity_pass": int((pre["h112_residual_toxicity"].to_numpy(dtype=np.float64) <= spec.max_residual_toxicity).sum()),
            }
        )
        selected, move_mat, axis, diag = select_cells(scored, spec, base_prob.shape, fit, pool, bad_axes, bad_moves, good_moves, axes)
        if selected.empty:
            continue
        rpred = route_pred(move_mat.reshape(-1), basis_fit_df, basis_fit_moves, route_fit)
        cpred = h098_pred(move_mat.reshape(-1), cell, h098_fit)
        if rpred > spec.route_pred_cap or cpred > spec.h098_pred_cap:
            continue
        prob = materialize(base_prob, move_mat)
        if int((np.abs(prob - base_prob) > TOL).sum()) == 0:
            continue
        hash_id = short_hash(prob)
        candidate_id = safe_id(f"h118_{spec.name}_{hash_id}", 128)
        path = OUT / f"submission_{candidate_id}.csv"
        h085mod.write_submission(sample, prob, path)
        metrics = evaluate_candidate(
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
        metrics["h118_fit_feature_set"] = fit.feature_set
        metrics["h118_fit_alpha"] = fit.alpha
        metrics["h118_fit_score"] = fit.score
        metrics["h118_forbidden_axes"] = int(len(forbidden_axes))
        candidate_rows.append(metrics)
        selected2 = selected.copy()
        if "candidate_id" in selected2.columns:
            selected2 = selected2.drop(columns=["candidate_id"])
        selected2.insert(0, "candidate_id", candidate_id)
        selected_frames.append(selected2)

    audit = pd.DataFrame(audit_rows)
    candidates = pd.DataFrame(candidate_rows)
    forbidden_audit.to_csv(OUT / "h118_forbidden_axes.csv", index=False)
    audit.to_csv(OUT / "h118_filter_audit.csv", index=False)
    scored.to_csv(OUT / "h118_scored_proposals.csv", index=False)
    model_scores.to_csv(OUT / "h118_curvature_model_scores.csv", index=False)
    if candidates.empty:
        report = f"""# H118 Forbidden-Sector Veto Assignment HS-JEPA

No candidate was promoted.

Filter audit:

{md_table(audit, 20)}
"""
        (OUT / "h118_report.md").write_text(report, encoding="utf-8")
        print("H118 promoted no candidate")
        print(audit.to_string(index=False))
        return

    candidates = candidates.sort_values(["h118_score", "h118_curv_marginal_vs_zero"], ascending=[False, True]).reset_index(drop=True)
    selected = candidates.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"submission_h118_forbiddenveto_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)

    decision = {
        "decision": "promote_h118_forbidden_veto_assignment",
        "selected_candidate_id": selected["candidate_id"],
        "root_uploadsafe_path": str(root_path.resolve()),
        "worldview": selected["worldview"],
        "selected_fit_feature_set": fit.feature_set,
        "selected_fit_alpha": fit.alpha,
        "selected_fit_score": fit.score,
        **selected,
        **{f"root_{key}": value for key, value in validation.items()},
    }

    candidates.to_csv(OUT / "h118_candidates.csv", index=False)
    pd.concat(selected_frames, ignore_index=True).to_csv(OUT / "h118_selected_cells.csv", index=False)
    pd.DataFrame([decision]).to_csv(OUT / "h118_decision.csv", index=False)

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
        "h118_curv_marginal_vs_zero",
        "model_pred_delta_vs_h057",
        "route_basis_pred_delta_vs_h057",
        "h102_cum_bad_weighted_pos",
        "h102_cum_h088_axis_cos",
        "selected_mean_residual_toxicity",
        "selected_mean_residual_safety",
        "h118_mean_forbidden_same",
        "h118_mean_forbidden_pressure",
        "h118_h115_overlap_cells",
        "h118_h115_cosine",
        "h118_h114_overlap_cells",
        "h118_h114_cosine",
        "h118_h112_overlap_cells",
        "h118_h112_cosine",
        "h118_score",
        "file",
    ]
    report = f"""# H118 Forbidden-Sector Veto Assignment HS-JEPA

Question: can H116's forbidden Q2-companion sector be used as a veto while
non-Q2 residual/nullspace proposals supply the actual safe assignment?

Filter audit:

{md_table(audit, 20)}

Candidates:

{md_table(candidates[cols], 20)}

Decision:

{md_table(pd.DataFrame([decision]), 1)}

Interpretation rule:

- If H118 improves, H116/H117 were useful because the forbidden sector is a
  veto representation, not an action target.
- If H118 loses while H112/H114 improve, the veto over-filtered useful cells
  or the selected residual/nullspace action is still underidentified.
- If H115 wins while H118 loses, Q2 companion was a narrow direct exception
  rather than a sector to veto.
"""
    (OUT / "h118_report.md").write_text(report, encoding="utf-8")

    print("H118 selected candidate")
    print(candidates[cols].head(10).to_string(index=False))
    print("\nDecision")
    print(pd.DataFrame([decision])[["decision", "selected_candidate_id", "root_uploadsafe_path", "root_upload_safe"]].to_string(index=False))


if __name__ == "__main__":
    run()
