#!/usr/bin/env python3
"""H117: forbidden companion-sector inversion HS-JEPA.

H116 found a sharp negative fact:

    all positive Q2 companion-rescue bundles are H088-positive.

H117 turns those failed/suspect bundles into a target representation.  The
decoder no longer tries to submit Q2 companion actions.  It treats that sector
as public-toxic and searches for non-Q2 row-target actions that move opposite
the forbidden companion-sector while satisfying H102/H112/H115 stress.
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
OUT = HITL / "h117_forbidden_companion_sector_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H116_PATH = HITL / "h116_companion_conservation_equation_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h116mod", H116_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H116_PATH}")
h116mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h116mod
SPEC.loader.exec_module(h116mod)

h115mod = h116mod.h115mod
h112mod = h116mod.h112mod
h102mod = h116mod.h102mod
h100mod = h116mod.h100mod
h097mod = h116mod.h097mod
h085mod = h116mod.h085mod

TARGETS = h116mod.TARGETS
KEYS = h116mod.KEYS
BASE_FILE = h116mod.BASE_FILE
TOL = h116mod.TOL


@dataclass(frozen=True)
class H117Spec:
    name: str
    target_mode: str
    max_cells: int
    max_rows: int
    max_per_subject: int
    max_per_target: int
    amp: float
    cap: float
    pool_top: int
    min_forbidden_gap: float
    min_forbidden_opp: float
    max_forbidden_same: float
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


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h117_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h117_forbidden_*.csv"):
        path.unlink()


def materialize(base_prob: np.ndarray, move_mat: np.ndarray) -> np.ndarray:
    return clip_prob(sigmoid(logit(base_prob) + move_mat))


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


def candidate_specs() -> list[H117Spec]:
    return [
        H117Spec(
            name="forbidden_antipode_sparse_c34_a050",
            target_mode="nonq2",
            max_cells=34,
            max_rows=26,
            max_per_subject=7,
            max_per_target=12,
            amp=0.50,
            cap=0.16,
            pool_top=130,
            min_forbidden_gap=0.000010,
            min_forbidden_opp=0.000010,
            max_forbidden_same=0.000003,
            max_curv_marginal=0.000035,
            max_marginal_add=0.000018,
            max_bad_weighted_pos=0.006,
            max_bad_max_pos=0.036,
            max_h088_cos=-0.003,
            min_good_margin=0.004,
            route_pred_cap=0.000140,
            h098_pred_cap=0.000100,
            worldview="safe assignment is the non-Q2 antipode of the H116 forbidden Q2-companion sector",
        ),
        H117Spec(
            name="forbidden_stage_antipode_c46_a042",
            target_mode="stage_q3",
            max_cells=46,
            max_rows=32,
            max_per_subject=8,
            max_per_target=16,
            amp=0.42,
            cap=0.15,
            pool_top=170,
            min_forbidden_gap=0.000006,
            min_forbidden_opp=0.000007,
            max_forbidden_same=0.000004,
            max_curv_marginal=0.000045,
            max_marginal_add=0.000020,
            max_bad_weighted_pos=0.008,
            max_bad_max_pos=0.042,
            max_h088_cos=-0.002,
            min_good_margin=0.003,
            route_pred_cap=0.000160,
            h098_pred_cap=0.000115,
            worldview="the forbidden Q2 sector can be inverted through Q3/S-stage objective targets",
        ),
        H117Spec(
            name="forbidden_subjective_stage_c40_a038",
            target_mode="q1q3_s13",
            max_cells=40,
            max_rows=30,
            max_per_subject=8,
            max_per_target=14,
            amp=0.38,
            cap=0.14,
            pool_top=150,
            min_forbidden_gap=0.000005,
            min_forbidden_opp=0.000006,
            max_forbidden_same=0.000004,
            max_curv_marginal=0.000040,
            max_marginal_add=0.000019,
            max_bad_weighted_pos=0.007,
            max_bad_max_pos=0.040,
            max_h088_cos=-0.002,
            min_good_margin=0.004,
            route_pred_cap=0.000150,
            h098_pred_cap=0.000110,
            worldview="Q2 toxicity can be avoided by moving the subjective/stage companions opposite the forbidden sector",
        ),
        H117Spec(
            name="forbidden_micro_kernel_c22_a060",
            target_mode="nonq2",
            max_cells=22,
            max_rows=18,
            max_per_subject=5,
            max_per_target=9,
            amp=0.60,
            cap=0.14,
            pool_top=90,
            min_forbidden_gap=0.000014,
            min_forbidden_opp=0.000014,
            max_forbidden_same=0.000002,
            max_curv_marginal=0.000030,
            max_marginal_add=0.000016,
            max_bad_weighted_pos=0.005,
            max_bad_max_pos=0.034,
            max_h088_cos=-0.003,
            min_good_margin=0.004,
            route_pred_cap=0.000130,
            h098_pred_cap=0.000095,
            worldview="only a tiny non-Q2 antipode kernel of the forbidden Q2 sector is action-grade",
        ),
    ]


def curvature_pred(move_mat: np.ndarray, fit: h115mod.CurvatureFit, pool: pd.DataFrame, bad_axes: pd.DataFrame, bad_moves: np.ndarray, good_moves: np.ndarray, axes: dict[str, object]) -> float:
    return h115mod.predict_curvature(move_mat, fit, pool, bad_axes, bad_moves, good_moves, axes)


def prepare_context():
    return h116mod.prepare_h116_context()


def build_forbidden_axes(
    props: pd.DataFrame,
    shape: tuple[int, int],
    fit: h115mod.CurvatureFit,
    pool: pd.DataFrame,
    bad_axes: pd.DataFrame,
    bad_moves: np.ndarray,
    good_moves: np.ndarray,
    axes: dict[str, object],
) -> tuple[np.ndarray, np.ndarray, pd.DataFrame]:
    mats = []
    weights = []
    rows = []
    for spec in h116mod.candidate_specs():
        bundle_pool = h116mod.build_bundle_pool(props, spec, shape, fit, pool, bad_axes, bad_moves, good_moves, axes)
        if bundle_pool.empty:
            continue
        for _, rec in bundle_pool.iterrows():
            axis = rec["_axis"]
            if float(rec["q2_rescue_marginal"]) <= 0.0:
                continue
            if float(axis["h102_cum_h088_axis_cos"]) <= 0.0:
                continue
            move = np.asarray(rec["_move_mat"], dtype=np.float64).reshape(-1)
            norm = np.linalg.norm(move)
            if norm < 1.0e-12:
                continue
            weight = (
                1.0
                + 25000.0 * float(rec["q2_rescue_marginal"])
                + 12000.0 * max(-float(rec["full_curv_marginal"]), 0.0)
                + 0.3 * float(rec["bundle_score"])
            )
            mats.append(move / norm)
            weights.append(weight)
            rows.append(
                {
                    "source_spec": spec.name,
                    "bundle_id": rec["bundle_id"],
                    "targets": rec["targets"],
                    "q2_rescue_marginal": float(rec["q2_rescue_marginal"]),
                    "full_curv_marginal": float(rec["full_curv_marginal"]),
                    "h088_cos": float(axis["h102_cum_h088_axis_cos"]),
                    "bad_weighted_pos": float(axis["h102_cum_bad_weighted_pos"]),
                    "weight": weight,
                }
            )
    if not mats:
        raise RuntimeError("no forbidden H116 axes")
    mat = np.vstack(mats)
    w = np.asarray(weights, dtype=np.float64)
    w = w / (np.sum(w) + 1.0e-12)
    audit = pd.DataFrame(rows).sort_values(["q2_rescue_marginal", "h088_cos"], ascending=[False, False]).reset_index(drop=True)
    return mat, w, audit


def annotate_forbidden_scores(props: pd.DataFrame, forbidden_axes: np.ndarray, weights: np.ndarray) -> pd.DataFrame:
    out = h116mod.annotate_cell_scores(props)
    flat = out["flat_index"].astype(int).to_numpy()
    raw_move = out["proposal_move"].to_numpy(dtype=np.float64)
    axis_vals = forbidden_axes[:, flat]
    signed = axis_vals * raw_move[None, :]
    same = (np.maximum(signed, 0.0).T @ weights).astype(np.float64)
    opp = (np.maximum(-signed, 0.0).T @ weights).astype(np.float64)
    out["h117_forbidden_same"] = same
    out["h117_forbidden_opp"] = opp
    out["h117_forbidden_gap"] = opp - same
    out["h117_forbidden_pressure"] = same / (opp + same + 1.0e-12)
    return out


def target_allowed(work: pd.DataFrame, mode: str) -> np.ndarray:
    target = work["target"].astype(str)
    if mode == "nonq2":
        return target.ne("Q2").to_numpy()
    if mode == "stage_q3":
        return target.isin(["Q3", "S1", "S2", "S3", "S4"]).to_numpy()
    if mode == "q1q3_s13":
        return target.isin(["Q1", "Q3", "S1", "S3"]).to_numpy()
    raise ValueError(mode)


def select_cells(
    scored: pd.DataFrame,
    spec: H117Spec,
    shape: tuple[int, int],
    fit: h115mod.CurvatureFit,
    pool: pd.DataFrame,
    bad_axes: pd.DataFrame,
    bad_moves: np.ndarray,
    good_moves: np.ndarray,
    axes: dict[str, object],
) -> tuple[pd.DataFrame, np.ndarray, dict[str, float], dict[str, float]]:
    work = scored[target_allowed(scored, spec.target_mode)].copy()
    work = work[work["h117_forbidden_gap"].to_numpy(dtype=np.float64) >= spec.min_forbidden_gap].copy()
    work = work[work["h117_forbidden_opp"].to_numpy(dtype=np.float64) >= spec.min_forbidden_opp].copy()
    work = work[work["h117_forbidden_same"].to_numpy(dtype=np.float64) <= spec.max_forbidden_same].copy()
    if work.empty:
        return pd.DataFrame(), np.zeros(shape, dtype=np.float64), {}, {}
    work["h117_move"] = np.clip(work["proposal_move"].to_numpy(dtype=np.float64) * spec.amp, -spec.cap, spec.cap)
    work["h117_score"] = (
        0.34 * rank01(work["h117_forbidden_gap"].to_numpy(dtype=np.float64), high=True)
        + 0.20 * rank01(work["h117_forbidden_opp"].to_numpy(dtype=np.float64), high=True)
        + 0.16 * work["h116_cell_score"].to_numpy(dtype=np.float64)
        + 0.12 * rank01(work["h112_residual_safety"].to_numpy(dtype=np.float64), high=True)
        + 0.10 * rank01(work["h112_residual_gap"].to_numpy(dtype=np.float64), high=True)
        + 0.08 * rank01(work["h112_antidote_score"].to_numpy(dtype=np.float64), high=True)
        - 0.20 * rank01(work["h112_residual_toxicity"].to_numpy(dtype=np.float64), high=True)
        - 0.10 * rank01(work["h117_forbidden_same"].to_numpy(dtype=np.float64), high=True)
    )
    work = work.sort_values(["h117_score", "h117_forbidden_gap"], ascending=[False, False])
    work = work.drop_duplicates(["row", "target"], keep="first").head(spec.pool_top).reset_index(drop=True)

    move_mat = np.zeros(shape, dtype=np.float64)
    zero_curv = curvature_pred(move_mat, fit, pool, bad_axes, bad_moves, good_moves, axes)
    curv_now = zero_curv
    selected_idx = []
    selected_rows: set[int] = set()
    selected_flat: set[int] = set()
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
        tmp[row, tidx] = float(rec["h117_move"])
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
            "h117_zero_curv": zero_curv,
            "h117_curv_pred_delta_vs_h057": curv_now,
            "h117_curv_marginal_vs_zero": curv_now - zero_curv,
        }
    selected = work.iloc[selected_idx].copy().sort_values(["row", "target_index"]).reset_index(drop=True)
    selected["h112_move"] = [
        move_mat[int(row), int(tidx)]
        for row, tidx in zip(selected["row"].astype(int), selected["target_index"].astype(int))
    ]
    selected["h097_move_col"] = "h112_move"
    diag = {
        "h117_zero_curv": zero_curv,
        "h117_curv_pred_delta_vs_h057": curv_now,
        "h117_curv_marginal_vs_zero": curv_now - zero_curv,
        "h117_mean_forbidden_gap": float(selected["h117_forbidden_gap"].mean()),
        "h117_mean_forbidden_opp": float(selected["h117_forbidden_opp"].mean()),
        "h117_mean_forbidden_same": float(selected["h117_forbidden_same"].mean()),
        "h117_mean_forbidden_pressure": float(selected["h117_forbidden_pressure"].mean()),
        "h117_selected_rows": int(len(selected_rows)),
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
    spec: H117Spec,
    path: Path,
    axis: dict[str, float],
    diag: dict[str, float],
    previous: dict[str, np.ndarray | None],
) -> dict[str, object]:
    proxy = h112mod.H112Spec(
        name=spec.name,
        group="forbidden_companion_sector",
        max_cells=spec.max_cells,
        max_rows=spec.max_rows,
        max_per_subject=spec.max_per_subject,
        max_per_target=spec.max_per_target,
        q2_cap=0,
        amp=spec.amp,
        cap=spec.cap,
        pool_top=spec.pool_top,
        beam_width=1,
        min_score=spec.min_forbidden_gap,
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
        out[f"h117_{label}_overlap_cells"] = overlap_count(move_flat, prev)
        out[f"h117_{label}_cosine"] = cosine(move_flat, prev)
    out.update(diag)
    out["h117_score"] = (
        160.0 * (-float(out["h117_curv_marginal_vs_zero"]))
        + 115.0 * (-float(out["route_basis_pred_delta_vs_h057"]))
        + 90.0 * (-float(out["model_pred_delta_vs_h057"]))
        + 0.22 * float(out["selected_mean_residual_safety"])
        + 0.16 * float(out["selected_mean_residual_gap"])
        + 0.12 * float(out["selected_mean_antidote_score"])
        + 0.10 * float(out["h117_mean_forbidden_gap"])
        + 0.08 * max(-float(out["h102_cum_h088_axis_cos"]), 0.0)
        - 0.18 * float(out["selected_mean_residual_toxicity"])
        - 0.12 * float(out["h117_mean_forbidden_pressure"])
        - 0.50 * max(float(out["h102_cum_bad_weighted_pos"]), 0.0)
        - 0.30 * max(float(out["h102_cum_bad_max_pos"]), 0.0)
        - 20.0 * max(float(out["hard_diag_delta_vs_h057"]), 0.0)
    )
    return out


def run() -> None:
    cleanup_previous_outputs()
    pool, _public, sample, base_prob, cell, h098_fit, route_fit, basis_fit_df, basis_fit_moves, bad_axes, bad_moves, good_moves, axes, fit, model_scores, props = prepare_context()
    forbidden_axes, forbidden_weights, forbidden_audit = build_forbidden_axes(props, base_prob.shape, fit, pool, bad_axes, bad_moves, good_moves, axes)
    scored = annotate_forbidden_scores(props, forbidden_axes, forbidden_weights)
    previous = {
        "h116_forbidden": None,
        "h115": h115mod.load_previous_move(sample, base_prob, "submission_h115_curvature_*_uploadsafe.csv"),
        "h114": h115mod.load_previous_move(sample, base_prob, "submission_h114_nullspace_*_uploadsafe.csv"),
        "h112": h115mod.load_previous_move(sample, base_prob, "submission_h112_residualtox_*_uploadsafe.csv"),
    }

    candidate_rows = []
    selected_frames = []
    for spec in candidate_specs():
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
        candidate_id = safe_id(f"h117_{spec.name}_{hash_id}", 128)
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
        metrics["h117_fit_feature_set"] = fit.feature_set
        metrics["h117_fit_alpha"] = fit.alpha
        metrics["h117_fit_score"] = fit.score
        metrics["h117_forbidden_axes"] = int(len(forbidden_axes))
        candidate_rows.append(metrics)
        selected2 = selected.copy()
        if "candidate_id" in selected2.columns:
            selected2 = selected2.drop(columns=["candidate_id"])
        selected2.insert(0, "candidate_id", candidate_id)
        selected_frames.append(selected2)

    candidates = pd.DataFrame(candidate_rows)
    forbidden_audit.to_csv(OUT / "h117_forbidden_axes.csv", index=False)
    scored.to_csv(OUT / "h117_scored_proposals.csv", index=False)
    model_scores.to_csv(OUT / "h117_curvature_model_scores.csv", index=False)
    if candidates.empty:
        positive = scored[scored["h117_forbidden_gap"].to_numpy(dtype=np.float64) > 0.0].copy()
        pos_cols = [
            "row",
            "subject_id",
            "target",
            "proposal_move",
            "h117_forbidden_gap",
            "h117_forbidden_opp",
            "h117_forbidden_same",
            "h112_residual_safety",
            "h112_residual_toxicity",
            "proposal_source",
        ]
        positive[pos_cols].sort_values("h117_forbidden_gap", ascending=False).to_csv(OUT / "h117_positive_antipode_cells.csv", index=False)
        report = f"""# H117 Forbidden Companion-Sector Inversion HS-JEPA

No candidate was promoted.

Core finding:

```text
The H116 forbidden companion sector is not practically invertible in the
current proposal space.  Only {len(positive)} of {len(scored)} proposal cells
have positive forbidden-antipode gap, and none can pass H102/H112/H115 stress
as a submission candidate.
```

Forbidden axes:

{md_table(forbidden_audit.head(20), 20)}

Positive antipode cells:

{md_table(positive[pos_cols].sort_values("h117_forbidden_gap", ascending=False), 20)}
"""
        (OUT / "h117_report.md").write_text(report, encoding="utf-8")
        print("H117 promoted no candidate")
        return

    candidates = candidates.sort_values(["h117_score", "h117_curv_marginal_vs_zero"], ascending=[False, True]).reset_index(drop=True)
    selected = candidates.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"submission_h117_forbidden_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)

    decision = {
        "decision": "promote_h117_forbidden_companion_sector",
        "selected_candidate_id": selected["candidate_id"],
        "root_uploadsafe_path": str(root_path.resolve()),
        "worldview": selected["worldview"],
        "selected_fit_feature_set": fit.feature_set,
        "selected_fit_alpha": fit.alpha,
        "selected_fit_score": fit.score,
        **selected,
        **{f"root_{key}": value for key, value in validation.items()},
    }

    candidates.to_csv(OUT / "h117_candidates.csv", index=False)
    pd.concat(selected_frames, ignore_index=True).to_csv(OUT / "h117_selected_cells.csv", index=False)
    pd.DataFrame([decision]).to_csv(OUT / "h117_decision.csv", index=False)

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
        "h117_curv_marginal_vs_zero",
        "h117_mean_forbidden_gap",
        "h117_mean_forbidden_opp",
        "h117_mean_forbidden_same",
        "model_pred_delta_vs_h057",
        "route_basis_pred_delta_vs_h057",
        "h102_cum_bad_weighted_pos",
        "h102_cum_h088_axis_cos",
        "selected_mean_residual_toxicity",
        "selected_mean_residual_safety",
        "h117_h115_overlap_cells",
        "h117_h115_cosine",
        "h117_h114_overlap_cells",
        "h117_h114_cosine",
        "h117_h112_overlap_cells",
        "h117_h112_cosine",
        "h117_score",
        "file",
    ]
    report = f"""# H117 Forbidden Companion-Sector Inversion HS-JEPA

Question: can H116's positive-rescue/H088-positive Q2 companion sector be used
as a forbidden target representation to build a safer non-Q2 assignment?

Forbidden axes:

{md_table(forbidden_audit.head(20), 20)}

Candidates:

{md_table(candidates[cols], 20)}

Decision:

{md_table(pd.DataFrame([decision]), 1)}

Interpretation rule:

- If H117 improves, H116's failed Q2 companion route becomes useful as a
  contrastive toxic target representation.
- If H115 improves and H117 loses, Q2 companion should be treated as a direct
  but high-risk curvature route.
- If H112/H114 beat H117, the forbidden companion sector is diagnostic only and
  residual/nullspace toxicity remains the live action decoder.
"""
    (OUT / "h117_report.md").write_text(report, encoding="utf-8")

    print("H117 selected candidate")
    print(candidates[cols].head(10).to_string(index=False))
    print("\nDecision")
    print(pd.DataFrame([decision])[["decision", "selected_candidate_id", "root_uploadsafe_path", "root_upload_safe"]].to_string(index=False))


if __name__ == "__main__":
    run()
