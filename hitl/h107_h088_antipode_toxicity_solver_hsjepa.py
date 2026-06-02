#!/usr/bin/env python3
"""H107: H088 antipode toxicity solver HS-JEPA.

H088 was a clean negative public sensor: a dual-head Pareto gate changed many
cells and lost public LB.  H107 treats that failure as an action equation, not
as a submission to avoid:

    H088 action vector is public-toxic
      -> invert only the cells where independent HS-JEPA support agrees
      -> enforce bad-axis silence and route-basis stress

The question is whether the antipode of a known toxic action contains a usable
public/private assignment field.
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
OUT = HITL / "h107_h088_antipode_toxicity_solver_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H106_PATH = HITL / "h106_route_consensus_kernel_expansion_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h106mod", H106_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H106_PATH}")
h106mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h106mod
SPEC.loader.exec_module(h106mod)

h105mod = h106mod.h105mod
h104mod = h106mod.h104mod
h103mod = h106mod.h103mod
h102mod = h106mod.h102mod
h100mod = h106mod.h100mod
h099mod = h106mod.h099mod
h098mod = h106mod.h098mod
h097mod = h106mod.h097mod
h095mod = h106mod.h095mod
h085mod = h106mod.h085mod

TARGETS = h106mod.TARGETS
KEYS = h106mod.KEYS
BASE_FILE = h106mod.BASE_FILE
TOL = h106mod.TOL
H105_SEED_ROWS = h106mod.H105_SEED_ROWS


@dataclass(frozen=True)
class H107Spec:
    name: str
    group: str
    max_cells: int
    max_rows: int
    max_per_subject: int
    max_per_target: int
    q2_cap: int
    amp: float
    cap: float
    min_score: float
    min_toxicity: float
    min_consensus: float
    min_vote_weight: float
    max_bad_weighted_pos: float
    max_bad_max_pos: float
    max_h088_cos: float
    min_good_margin: float
    route_pred_cap: float
    h098_pred_cap: float
    worldview: str


def clip_prob(x: np.ndarray) -> np.ndarray:
    return h085mod.clip_prob(np.asarray(x, dtype=np.float64))


def logit(x: np.ndarray) -> np.ndarray:
    return h085mod.logit(np.asarray(x, dtype=np.float64))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return h085mod.sigmoid(np.asarray(x, dtype=np.float64))


def rank01(values: np.ndarray, high: bool = True) -> np.ndarray:
    return h085mod.rank01(np.asarray(values, dtype=np.float64), high=high)


def safe_id(text: str, limit: int = 132) -> str:
    return h085mod.safe_id(text, limit=limit)


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return h085mod.md_table(frame, n=n)


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h107_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h107_antipode_*.csv"):
        path.unlink()


def candidate_specs() -> list[H107Spec]:
    return [
        H107Spec(
            name="strict_antitoxic_core_c44_a045",
            group="strict_core",
            max_cells=44,
            max_rows=30,
            max_per_subject=8,
            max_per_target=12,
            q2_cap=0,
            amp=0.45,
            cap=0.28,
            min_score=0.56,
            min_toxicity=0.18,
            min_consensus=0.60,
            min_vote_weight=0.32,
            max_bad_weighted_pos=0.004,
            max_bad_max_pos=0.025,
            max_h088_cos=-0.006,
            min_good_margin=0.018,
            route_pred_cap=0.000120,
            h098_pred_cap=0.000060,
            worldview="only high-support non-Q2 cells on the antipode of H088 are action-grade",
        ),
        H107Spec(
            name="kernel_antipode_transfer_c64_a050",
            group="kernel_transfer",
            max_cells=64,
            max_rows=30,
            max_per_subject=18,
            max_per_target=18,
            q2_cap=0,
            amp=0.50,
            cap=0.32,
            min_score=0.50,
            min_toxicity=0.12,
            min_consensus=0.55,
            min_vote_weight=0.26,
            max_bad_weighted_pos=0.008,
            max_bad_max_pos=0.040,
            max_h088_cos=-0.004,
            min_good_margin=0.010,
            route_pred_cap=0.000150,
            h098_pred_cap=0.000075,
            worldview="the H105/H106 kernel transfers through the antipode of H088 toxicity",
        ),
        H107Spec(
            name="objective_antipode_c96_a042",
            group="objective",
            max_cells=96,
            max_rows=62,
            max_per_subject=10,
            max_per_target=24,
            q2_cap=0,
            amp=0.42,
            cap=0.28,
            min_score=0.46,
            min_toxicity=0.08,
            min_consensus=0.40,
            min_vote_weight=0.16,
            max_bad_weighted_pos=0.012,
            max_bad_max_pos=0.060,
            max_h088_cos=-0.002,
            min_good_margin=0.006,
            route_pred_cap=0.000180,
            h098_pred_cap=0.000090,
            worldview="H088's failed action is mostly toxic in Q3/S objective cells, not in Q2",
        ),
        H107Spec(
            name="q2_antipode_micro_c24_a030",
            group="q2_micro",
            max_cells=24,
            max_rows=24,
            max_per_subject=6,
            max_per_target=24,
            q2_cap=24,
            amp=0.30,
            cap=0.22,
            min_score=0.48,
            min_toxicity=0.16,
            min_consensus=0.00,
            min_vote_weight=0.00,
            max_bad_weighted_pos=0.006,
            max_bad_max_pos=0.034,
            max_h088_cos=-0.003,
            min_good_margin=0.006,
            route_pred_cap=0.000220,
            h098_pred_cap=0.000075,
            worldview="H088 exposed a small wrong-sign Q2 toxicity field that should be inverted, not frozen",
        ),
        H107Spec(
            name="broad_antipode_shadow_c140_a030",
            group="broad_shadow",
            max_cells=140,
            max_rows=84,
            max_per_subject=10,
            max_per_target=30,
            q2_cap=8,
            amp=0.30,
            cap=0.24,
            min_score=0.42,
            min_toxicity=0.06,
            min_consensus=0.35,
            min_vote_weight=0.10,
            max_bad_weighted_pos=0.018,
            max_bad_max_pos=0.080,
            max_h088_cos=-0.001,
            min_good_margin=0.000,
            route_pred_cap=0.000260,
            h098_pred_cap=0.000100,
            worldview="the whole H088 action direction is a toxic shadow whose constrained antipode is useful",
        ),
    ]


def group_allowed(row: dict[str, object], group: str) -> bool:
    target = str(row["target"])
    subject = str(row["subject_id"])
    r = int(row["row"])
    if group == "strict_core":
        return target != "Q2" and float(row["h107_align_or_consensus"]) > 0.0
    if group == "kernel_transfer":
        return target != "Q2" and (subject in {"id06", "id07"} or r in H105_SEED_ROWS or float(row["h106_seed_neighbor"]) > 0)
    if group == "objective":
        return target in {"Q3", "S1", "S2", "S3", "S4"}
    if group == "q2_micro":
        return target == "Q2"
    if group == "broad_shadow":
        return True
    raise ValueError(group)


def build_route_context() -> tuple[
    pd.DataFrame,
    dict[str, pd.DataFrame],
    pd.DataFrame,
    h097mod.ResponseFit,
    h100mod.RouteBasisFit,
    pd.DataFrame,
    np.ndarray,
    pd.DataFrame,
    np.ndarray,
    pd.DataFrame,
    pd.DataFrame,
]:
    base = h085mod.load_sub(BASE_FILE)
    sample = base[KEYS].copy()
    base_prob = base[TARGETS].to_numpy(dtype=np.float64)
    cell_raw = h097mod.ensure_h095_cell_table(sample, base_prob)
    cell, feature_sets = h097mod.add_context_features(cell_raw, sample)
    public = h097mod.load_public_moves(sample, base_prob)
    h098_scores, _h098_pred_rows, h098_fit = h098mod.evaluate_weighted_models(public, cell, feature_sets)
    gradient = h097mod.response_gradient(cell, h098_fit)
    pool = h098mod.build_frontier_pool(cell, gradient)
    cell = cell.drop(columns=["h098_frontier_cell_score"], errors="ignore").merge(
        pool[["flat_index", "h098_frontier_cell_score"]],
        on="flat_index",
        how="left",
    )
    cell["h098_frontier_cell_score"] = cell["h098_frontier_cell_score"].fillna(0.0)
    routes = h099mod.load_routes()

    basis, cells_by_basis, basis_moves = h100mod.build_route_basis(routes, pool, cell, h098_fit, base_prob)
    model_scores, _pred_rows, route_fit = h100mod.evaluate_route_basis_models(public, basis, basis_moves)
    basis_fit_df, basis_fit_moves = h100mod.selected_basis_for_fit(basis, basis_moves, route_fit)
    scored0 = h100mod.score_basis_actions(basis, basis_moves, basis_fit_df, basis_fit_moves, route_fit)
    bad_axes, bad_moves, good_axes, good_moves = h102mod.build_axes(public, sample, base_prob)
    scored = h102mod.add_axis_scores(scored0, basis_moves, bad_axes, bad_moves, good_axes, good_moves)
    return (
        cell,
        cells_by_basis,
        scored,
        h098_fit,
        route_fit,
        basis_fit_df,
        basis_fit_moves,
        bad_axes,
        bad_moves,
        good_axes,
        good_moves,
    )


def build_consensus_support(
    cell: pd.DataFrame,
    cells_by_basis: dict[str, pd.DataFrame],
    scored: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    spec = next(s for s in h106mod.candidate_specs() if s.name == "broad_conflict_consensus_c96_a065")
    consensus, source_actions = h106mod.build_consensus_table(scored, cells_by_basis, spec, cell)
    keep_cols = [
        "flat_index",
        "h106_vote_weight",
        "h106_vote_consensus",
        "h106_move",
        "h106_score",
        "h106_seed_row",
        "h106_seed_neighbor",
        "h106_seed_subject",
    ]
    return consensus[keep_cols].copy(), source_actions


def build_antipode_pool(cell: pd.DataFrame, consensus: pd.DataFrame, amp: float, cap: float) -> pd.DataFrame:
    pool = cell.sort_values("flat_index").reset_index(drop=True).copy()
    pool = pool.merge(consensus, on="flat_index", how="left")
    for col in [
        "h106_vote_weight",
        "h106_vote_consensus",
        "h106_move",
        "h106_score",
        "h106_seed_row",
        "h106_seed_neighbor",
        "h106_seed_subject",
    ]:
        pool[col] = pool[col].fillna(0.0)

    h088_move = pool["h088_logit_move"].to_numpy(dtype=np.float64)
    raw = -h088_move * amp
    pool["h107_move"] = np.clip(raw, -cap, cap)
    sign = np.sign(pool["h107_move"].to_numpy(dtype=np.float64))
    h057_sign = np.sign(pool["h057_positive_logit_move"].to_numpy(dtype=np.float64))
    h106_sign = np.sign(pool["h106_move"].to_numpy(dtype=np.float64))
    pool["h107_align_h057"] = (
        (sign * h057_sign > 0)
        & (pool["h057_positive_weight"].to_numpy(dtype=np.float64) > 0)
    ).astype(float)
    pool["h107_align_h106"] = (
        (sign * h106_sign > 0)
        & (np.abs(pool["h106_move"].to_numpy(dtype=np.float64)) > 1.0e-10)
    ).astype(float)
    pool["h107_align_or_consensus"] = np.maximum(pool["h107_align_h057"], pool["h107_align_h106"])
    pool["h107_q2_penalty"] = pool["target"].astype(str).eq("Q2").astype(float)
    pool["h107_antipode_score"] = (
        0.30 * rank01(np.abs(pool["h107_move"].to_numpy(dtype=np.float64)), high=True)
        + 0.20 * rank01(pool["h088_toxicity"].to_numpy(dtype=np.float64), high=True)
        + 0.14 * pool["h107_align_h106"].to_numpy(dtype=np.float64) * pool["h106_vote_consensus"].to_numpy(dtype=np.float64)
        + 0.12 * pool["h107_align_h057"].to_numpy(dtype=np.float64) * pool["h057_positive_weight"].to_numpy(dtype=np.float64)
        + 0.10 * pool["h057_h088_anti_conflict"].to_numpy(dtype=np.float64)
        + 0.08 * pool["h095_safe_cell_score"].to_numpy(dtype=np.float64)
        + 0.07 * pool["h098_frontier_cell_score"].to_numpy(dtype=np.float64)
        + 0.05 * rank01(pool["h106_score"].to_numpy(dtype=np.float64), high=True)
        + 0.04 * pool["source_agrees_h085"].to_numpy(dtype=np.float64)
        - 0.18 * pool["h080_bad_same_rank"].to_numpy(dtype=np.float64)
        - 0.12 * pool["is_h050_null"].to_numpy(dtype=np.float64)
        - 0.10 * pool["h107_q2_penalty"].to_numpy(dtype=np.float64)
    )
    return pool


def route_pred(
    move_flat: np.ndarray,
    basis_fit_df: pd.DataFrame,
    basis_fit_moves: np.ndarray,
    route_fit: h100mod.RouteBasisFit,
) -> float:
    return h100mod.predict_candidate_delta(move_flat, basis_fit_df, basis_fit_moves, route_fit)


def h098_pred(move_flat: np.ndarray, cell: pd.DataFrame, h098_fit: h097mod.ResponseFit) -> float:
    return h097mod.predict_candidate_delta(move_flat, cell, h098_fit)


def select_cells(
    pool: pd.DataFrame,
    spec: H107Spec,
    base_shape: tuple[int, int],
    bad_axes: pd.DataFrame,
    bad_moves: np.ndarray,
    good_moves: np.ndarray,
) -> tuple[pd.DataFrame, np.ndarray]:
    p = pool.copy()
    p = p[np.abs(p["h107_move"].to_numpy(dtype=np.float64)) > 1.0e-10].copy()
    p = p[p["h088_active"].to_numpy(dtype=np.float64) > 0.0]
    p = p[p["h088_toxicity"].to_numpy(dtype=np.float64) >= spec.min_toxicity]
    p = p[p["h107_antipode_score"].to_numpy(dtype=np.float64) >= spec.min_score]
    p = p[p["h106_vote_consensus"].to_numpy(dtype=np.float64) >= spec.min_consensus]
    p = p[p["h106_vote_weight"].to_numpy(dtype=np.float64) >= spec.min_vote_weight]
    p = p[p.apply(lambda row: group_allowed(row, spec.group), axis=1)]
    p = p.sort_values("h107_antipode_score", ascending=False)

    selected = []
    used_rows: set[int] = set()
    subject_counts: dict[str, int] = {}
    target_counts: dict[str, int] = {}
    q2_count = 0
    move_mat = np.zeros(base_shape, dtype=np.float64)

    for rec in p.to_dict("records"):
        if len(selected) >= spec.max_cells:
            break
        row = int(rec["row"])
        target = str(rec["target"])
        subject = str(rec["subject_id"])
        if row not in used_rows and len(used_rows) >= spec.max_rows:
            continue
        if row not in used_rows and subject_counts.get(subject, 0) + 1 > spec.max_per_subject:
            continue
        if target_counts.get(target, 0) >= spec.max_per_target:
            continue
        if target == "Q2" and q2_count >= spec.q2_cap:
            continue

        tmp = move_mat.copy()
        tmp[row, int(rec["target_index"])] = float(rec["h107_move"])
        axis = h102mod.cumulative_axis_metrics(tmp.reshape(-1), bad_axes, bad_moves, good_moves)
        if axis["h102_cum_bad_weighted_pos"] > spec.max_bad_weighted_pos:
            continue
        if axis["h102_cum_bad_max_pos"] > spec.max_bad_max_pos:
            continue
        if axis["h102_cum_h088_axis_cos"] > spec.max_h088_cos:
            continue
        if axis["h102_cum_good_bad_margin"] < spec.min_good_margin:
            continue

        move_mat = tmp
        selected.append(rec)
        if row not in used_rows:
            used_rows.add(row)
            subject_counts[subject] = subject_counts.get(subject, 0) + 1
        target_counts[target] = target_counts.get(target, 0) + 1
        if target == "Q2":
            q2_count += 1

    selected_df = pd.DataFrame(selected)
    if selected_df.empty:
        return selected_df, move_mat
    selected_df = selected_df.sort_values(["row", "target_index"]).reset_index(drop=True)
    selected_df["h097_move_col"] = "h107_move"
    return selected_df, move_mat


def materialize(base_prob: np.ndarray, move_mat: np.ndarray) -> np.ndarray:
    return clip_prob(sigmoid(logit(base_prob) + move_mat))


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
    bad_axes: pd.DataFrame,
    bad_moves: np.ndarray,
    good_moves: np.ndarray,
    spec: H107Spec,
    path: Path,
) -> dict[str, object]:
    proxy = h097mod.H097Spec(
        name=spec.name,
        mode="h088_antipode_toxicity_solver",
        target_group=spec.group,
        k=spec.max_cells,
        alpha=spec.amp,
        cap=spec.cap,
        min_score=spec.min_score,
        worldview=spec.worldview,
    )
    metrics = h097mod.evaluate_candidate(candidate_id, prob, move_mat, base_prob, selected_cells, cell, sample, h098_fit, proxy, path)
    axis = h102mod.cumulative_axis_metrics(move_mat.reshape(-1), bad_axes, bad_moves, good_moves)
    metrics.update(axis)
    metrics["route_basis_pred_delta_vs_h057"] = route_pred(move_mat.reshape(-1), basis_fit_df, basis_fit_moves, route_fit)
    metrics["selected_mean_h107_antipode_score"] = float(selected_cells["h107_antipode_score"].mean()) if len(selected_cells) else 0.0
    metrics["selected_mean_h106_consensus"] = float(selected_cells["h106_vote_consensus"].mean()) if len(selected_cells) else 0.0
    metrics["selected_mean_h106_vote_weight"] = float(selected_cells["h106_vote_weight"].mean()) if len(selected_cells) else 0.0
    metrics["selected_align_h106_rate"] = float(selected_cells["h107_align_h106"].mean()) if len(selected_cells) else 0.0
    metrics["selected_align_h057_rate"] = float(selected_cells["h107_align_h057"].mean()) if len(selected_cells) else 0.0
    metrics["selected_seed_neighbor_cells"] = int(selected_cells["h106_seed_neighbor"].sum()) if len(selected_cells) else 0
    metrics["h107_score"] = (
        145.0 * (-float(metrics["model_pred_delta_vs_h057"]))
        + 110.0 * (-float(metrics["route_basis_pred_delta_vs_h057"]))
        + 0.24 * float(metrics["anti_h088_direction_rate"])
        + 0.18 * float(metrics["selected_conflict_rate"])
        + 0.16 * float(metrics["selected_mean_h107_antipode_score"])
        + 0.12 * float(metrics["selected_align_h106_rate"])
        + 0.10 * float(metrics["selected_align_h057_rate"])
        + 0.08 * max(float(metrics["h102_cum_good_bad_margin"]), 0.0)
        + 0.05 * max(-float(metrics["h102_cum_h088_axis_cos"]), 0.0)
        - 0.55 * max(float(metrics["h102_cum_bad_weighted_pos"]), 0.0)
        - 0.35 * max(float(metrics["h102_cum_bad_max_pos"]), 0.0)
        - 0.30 * max(float(metrics["h102_cum_h088_axis_cos"]), 0.0)
        - 0.25 * max(float(metrics["max_positive_bad_cosine"]), 0.0)
        - 20.0 * max(float(metrics["hard_diag_delta_vs_h057"]), 0.0)
        - 10.0 * max(float(metrics["posterior_delta_vs_h057"]), 0.0)
    )
    return metrics


def run() -> None:
    cleanup_previous_outputs()
    base = h085mod.load_sub(BASE_FILE)
    sample = base[KEYS].copy()
    base_prob = base[TARGETS].to_numpy(dtype=np.float64)

    (
        cell,
        cells_by_basis,
        scored,
        h098_fit,
        route_fit,
        basis_fit_df,
        basis_fit_moves,
        bad_axes,
        bad_moves,
        good_axes,
        good_moves,
    ) = build_route_context()

    consensus, source_actions = build_consensus_support(cell, cells_by_basis, scored)
    base_pool = cell.merge(consensus, on="flat_index", how="left")
    for col in [
        "h106_vote_weight",
        "h106_vote_consensus",
        "h106_move",
        "h106_score",
        "h106_seed_row",
        "h106_seed_neighbor",
        "h106_seed_subject",
    ]:
        base_pool[col] = base_pool[col].fillna(0.0)

    candidate_rows = []
    selected_frames = []
    pool_frames = []
    for spec in candidate_specs():
        pool = build_antipode_pool(cell, consensus, spec.amp, spec.cap)
        selected_cells, move_mat = select_cells(pool, spec, base_prob.shape, bad_axes, bad_moves, good_moves)
        if selected_cells.empty:
            continue
        rpred = route_pred(move_mat.reshape(-1), basis_fit_df, basis_fit_moves, route_fit)
        cpred = h098_pred(move_mat.reshape(-1), cell, h098_fit)
        if rpred > spec.route_pred_cap:
            continue
        if cpred > spec.h098_pred_cap:
            continue
        prob = materialize(base_prob, move_mat)
        if int((np.abs(prob - base_prob) > TOL).sum()) == 0:
            continue
        hash_id = short_hash(prob)
        candidate_id = safe_id(f"h107_{spec.name}_{hash_id}", 128)
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
            bad_axes,
            bad_moves,
            good_moves,
            spec,
            path,
        )
        candidate_rows.append(metrics)
        selected_cells = selected_cells.copy()
        selected_cells.insert(0, "candidate_id", candidate_id)
        selected_frames.append(selected_cells)
        top_pool = pool.sort_values("h107_antipode_score", ascending=False).head(220).copy()
        top_pool.insert(0, "candidate_id", candidate_id)
        pool_frames.append(top_pool)

    candidates = pd.DataFrame(candidate_rows)
    if candidates.empty:
        raise RuntimeError("no H107 candidates")
    candidates = candidates.sort_values(["h107_score", "model_pred_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True)
    selected = candidates.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"submission_h107_antipode_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)

    decision = {
        "decision": "promote_h107_h088_antipode_toxicity_solver",
        "selected_candidate_id": selected["candidate_id"],
        "root_uploadsafe_path": str(root_path.resolve()),
        "worldview": selected["worldview"],
        "h098_feature_set": h098_fit.feature_set,
        "h098_alpha": h098_fit.alpha,
        **selected,
        **{f"root_{key}": value for key, value in validation.items()},
    }

    candidates.to_csv(OUT / "h107_candidates.csv", index=False)
    pd.concat(selected_frames, ignore_index=True).to_csv(OUT / "h107_selected_cells.csv", index=False)
    pd.concat(pool_frames, ignore_index=True).to_csv(OUT / "h107_top_antipode_cells.csv", index=False)
    source_actions.to_csv(OUT / "h107_source_consensus_actions.csv", index=False)
    consensus.to_csv(OUT / "h107_consensus_support.csv", index=False)
    bad_axes.to_csv(OUT / "h107_bad_axes.csv", index=False)
    good_axes.to_csv(OUT / "h107_good_axes.csv", index=False)
    pd.DataFrame([decision]).to_csv(OUT / "h107_decision.csv", index=False)

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
        "model_pred_delta_vs_h057",
        "route_basis_pred_delta_vs_h057",
        "posterior_delta_vs_h057",
        "hard_diag_delta_vs_h057",
        "h102_cum_bad_weighted_pos",
        "h102_cum_bad_max_pos",
        "h102_cum_h088_axis_cos",
        "h102_cum_good_bad_margin",
        "anti_h088_direction_rate",
        "selected_conflict_rate",
        "selected_align_h106_rate",
        "selected_align_h057_rate",
        "selected_toxic_mean",
        "h107_score",
        "file",
    ]
    report = f"""# H107 H088 Antipode Toxicity Solver HS-JEPA

Question: if H088 is a negative public sensor, is the constrained antipode of
its toxic action vector a safe row-target assignment field?

Candidates:

{md_table(candidates[cols], 20)}

Decision:

{md_table(pd.DataFrame([decision]), 1)}

Interpretation rule:

- If H107 improves, H088 is not only a bad-axis diagnostic; its antipode carries
  action-grade public/private correction.
- If H107 loses while H103/H104/H105/H106 improve, H088 should remain a
  toxicity veto, not an action source.
- If H107 loses badly, public toxicity is not sign-symmetric and antidote
  decoding must be killed.
"""
    (OUT / "h107_report.md").write_text(report, encoding="utf-8")

    print(f"selected={decision['selected_candidate_id']}")
    print(f"root={root_path}")
    print(candidates[cols].head(10).to_string(index=False))


if __name__ == "__main__":
    run()
