#!/usr/bin/env python3
"""H099: route-constrained signed assignment equation HS-JEPA.

H098 learned a frontier-weighted signed public-response equation and correctly
predicted H088 as a bad action.  But H098 still acts at the cell level.  H099
adds the missing discrete object: row-target route assignment.

Question:

    Are H057-positive / H088-negative signed cells safe only when they belong to
    a coherent row-route template?

The decoder selects route actions, not independent cells.  H071 provides route
templates, H098 provides the signed public response, H088 is a negative action
sensor, and H057 is the positive row-state sensor.
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
OUT = HITL / "h099_route_constrained_signed_assignment_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H098_PATH = HITL / "h098_frontier_weighted_action_equation_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h098mod", H098_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H098_PATH}")
h098mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h098mod
SPEC.loader.exec_module(h098mod)

h097mod = h098mod.h097mod
h095mod = h097mod.h095mod
h085mod = h097mod.h085mod
h087mod = h097mod.h087mod

TARGETS = h097mod.TARGETS
KEYS = h097mod.KEYS
BASE_FILE = h097mod.BASE_FILE
BASE_LB = h097mod.BASE_LB
TOL = h097mod.TOL
ROUTE_PATH = HITL / "h071_rowtarget_assignment_solver_jepa" / "h071_route_candidates.csv"


@dataclass(frozen=True)
class H099Spec:
    name: str
    mode: str
    route_group: str
    max_routes: int
    max_cells: int
    max_rows: int
    max_per_subject: int
    q2_cap: int
    alpha: float
    cap: float
    min_route_score: float
    min_cell_score: float
    worldview: str


def clip_prob(x: np.ndarray) -> np.ndarray:
    return h085mod.clip_prob(np.asarray(x, dtype=np.float64))


def logit(x: np.ndarray) -> np.ndarray:
    return h085mod.logit(np.asarray(x, dtype=np.float64))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return h085mod.sigmoid(np.asarray(x, dtype=np.float64))


def bce(prob: np.ndarray, q: np.ndarray) -> np.ndarray:
    return h085mod.bce(np.asarray(prob, dtype=np.float64), np.asarray(q, dtype=np.float64))


def rank01(values: np.ndarray, high: bool = True) -> np.ndarray:
    return h085mod.rank01(np.asarray(values, dtype=np.float64), high=high)


def safe_id(text: str, limit: int = 132) -> str:
    return h085mod.safe_id(text, limit=limit)


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return h085mod.md_table(frame, n=n)


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h099_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h099_route_equation_*_uploadsafe.csv"):
        path.unlink()


def parse_target_indices(value: object) -> list[int]:
    return [int(x) for x in str(value).split(",") if str(x).strip() != ""]


def load_routes() -> pd.DataFrame:
    routes = pd.read_csv(ROUTE_PATH)
    routes["target_indices_list"] = routes["target_indices"].map(parse_target_indices)
    routes["route_targets_set"] = routes["target_indices_list"].map(lambda xs: frozenset(TARGETS[i] for i in xs))
    return routes


def route_group_allowed(route: pd.Series, route_cells: pd.DataFrame, group: str) -> bool:
    target_set = set(route["route_targets_set"])
    route_name = str(route["route_name"])
    if group == "all":
        return True
    if group == "conflict":
        return float(route_cells["h057_h088_anti_conflict"].sum()) > 0
    if group == "full_state":
        return route_name == "full_state"
    if group == "nonq2_full":
        return route_name == "nonq2_full"
    if group == "objective":
        return bool(target_set) and target_set.issubset({"Q3", "S1", "S2", "S3", "S4"})
    if group == "q2_route":
        return "Q2" in target_set
    if group == "tail":
        return "tail" in route_name or "edge" in route_name or float(route_cells["h057_h088_anti_conflict"].sum()) > 0
    raise ValueError(group)


def mode_moves(route_cells: pd.DataFrame, mode: str) -> tuple[np.ndarray, np.ndarray]:
    if mode == "frontier_descent":
        move = route_cells["h097_descent_logit_move"].to_numpy(dtype=np.float64)
        mask = np.abs(move) > 1.0e-10
    elif mode == "counter_h088":
        move = route_cells["h097_counter_h088_move"].to_numpy(dtype=np.float64)
        mask = route_cells["h088_toxicity"].to_numpy(dtype=np.float64) > 0.0
    elif mode == "conflict_invert":
        move = route_cells["h097_conflict_move"].to_numpy(dtype=np.float64)
        mask = route_cells["h057_h088_anti_conflict"].to_numpy(dtype=np.float64) > 0.0
    elif mode == "positive_bridge":
        move = route_cells["h097_positive_move"].to_numpy(dtype=np.float64)
        mask = (
            (route_cells["h057_positive_weight"].to_numpy(dtype=np.float64) > 0)
            & (
                np.sign(route_cells["h097_descent_logit_move"].to_numpy(dtype=np.float64))
                * np.sign(route_cells["h057_positive_logit_move"].to_numpy(dtype=np.float64))
                > 0
            )
        )
    elif mode == "hybrid_route":
        conflict = route_cells["h057_h088_anti_conflict"].to_numpy(dtype=np.float64) > 0
        move = np.where(
            conflict,
            route_cells["h097_conflict_move"].to_numpy(dtype=np.float64),
            route_cells["h097_descent_logit_move"].to_numpy(dtype=np.float64),
        )
        mask = np.abs(move) > 1.0e-10
    else:
        raise ValueError(mode)
    return move, mask


def action_move_matrix(
    base_shape: tuple[int, int],
    selected: pd.DataFrame,
    alpha: float,
    cap: float,
) -> np.ndarray:
    move_mat = np.zeros(base_shape, dtype=np.float64)
    for rec in selected.to_dict("records"):
        row = int(rec["row"])
        tidx = int(rec["target_index"])
        move = float(np.clip(rec["h099_route_move"], -cap, cap) * alpha)
        move_mat[row, tidx] = move
    return move_mat


def materialize_from_move(base_prob: np.ndarray, move_mat: np.ndarray) -> np.ndarray:
    return clip_prob(sigmoid(logit(base_prob) + move_mat))


def route_action_table(
    routes: pd.DataFrame,
    pool: pd.DataFrame,
    cell: pd.DataFrame,
    fit: h097mod.ResponseFit,
    base_prob: np.ndarray,
    spec: H099Spec,
) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    pool_by_key = pool.set_index(["row", "target_index"], drop=False)
    ordered = cell.sort_values("flat_index")
    q097 = ordered["h085_q"].to_numpy(dtype=np.float64).reshape(base_prob.shape)
    qhard = ordered["q_hard"].to_numpy(dtype=np.float64).reshape(base_prob.shape)

    rows: list[dict[str, object]] = []
    cells_by_action: dict[str, pd.DataFrame] = {}
    for route in routes.to_dict("records"):
        row = int(route["row"])
        parts = []
        for tidx in route["target_indices_list"]:
            key = (row, int(tidx))
            if key not in pool_by_key.index:
                continue
            rec = pool_by_key.loc[key]
            if isinstance(rec, pd.DataFrame):
                rec = rec.iloc[0]
            parts.append(rec)
        if not parts:
            continue
        route_cells = pd.DataFrame(parts).reset_index(drop=True)
        route_s = pd.Series(route)
        if not route_group_allowed(route_s, route_cells, spec.route_group):
            continue

        move, mode_mask = mode_moves(route_cells, spec.mode)
        score_mask = route_cells["h098_frontier_cell_score"].to_numpy(dtype=np.float64) >= spec.min_cell_score
        keep = mode_mask & score_mask
        if not np.any(keep):
            continue

        action_cells = route_cells.loc[keep].copy().reset_index(drop=True)
        action_cells["h099_route_move"] = move[keep]
        action_cells["h097_move_col"] = "h099_route_move"
        action_id = safe_id(f"{route['route_id']}_{spec.mode}", 96)
        action_cells["h099_action_id"] = action_id
        action_cells["h099_route_id"] = str(route["route_id"])
        action_cells["h099_route_name"] = str(route["route_name"])
        action_cells["h099_route_targets"] = str(route["targets"])

        move_mat = action_move_matrix(base_prob.shape, action_cells, spec.alpha, spec.cap)
        prob = materialize_from_move(base_prob, move_mat)
        pred_delta = h097mod.predict_candidate_delta(move_mat.reshape(-1), cell, fit)
        posterior_delta = float((bce(prob, q097) - bce(base_prob, q097)).mean())
        hard_delta = float((bce(prob, qhard) - bce(base_prob, qhard)).mean())
        changed = np.abs(move_mat) > 1.0e-12

        sel_move = move_mat.reshape(-1)[action_cells["flat_index"].astype(int).to_numpy()]
        h088_move = action_cells["h088_logit_move"].to_numpy(dtype=np.float64)
        h057_move = action_cells["h057_positive_logit_move"].to_numpy(dtype=np.float64)
        anti_h088 = float((np.sign(sel_move) * np.sign(h088_move) < 0).mean())
        align_h057 = float(
            (
                (np.sign(sel_move) * np.sign(h057_move) > 0)
                & (action_cells["h057_positive_weight"].to_numpy(dtype=np.float64) > 0)
            ).mean()
        )
        target_counts = {
            f"{target}_cells": int((action_cells["target"].astype(str) == target).sum())
            for target in TARGETS
        }
        rows.append(
            {
                "action_id": action_id,
                "route_id": str(route["route_id"]),
                "row": row,
                "subject_id": str(route["subject_id"]),
                "sleep_date": str(route["sleep_date"]),
                "route_name": str(route["route_name"]),
                "route_targets": str(route["targets"]),
                "mode": spec.mode,
                "route_group": spec.route_group,
                "route_n_cells": int(route["n_cells"]),
                "action_cells": int(len(action_cells)),
                "action_q2_cells": int(action_cells["target"].astype(str).eq("Q2").sum()),
                "changed_cells": int(changed.sum()),
                "model_pred_delta_vs_h057": float(pred_delta),
                "posterior_delta_vs_h057": posterior_delta,
                "hard_diag_delta_vs_h057": hard_delta,
                "anti_h088_direction_rate": anti_h088,
                "h057_positive_align_rate": align_h057,
                "selected_conflict_rate": float(action_cells["h057_h088_anti_conflict"].mean()),
                "selected_toxic_mean": float(action_cells["h088_toxicity"].mean()),
                "selected_safe_cell_mean": float(action_cells["h095_safe_cell_score"].mean()),
                "mean_bad_same_rank": float(action_cells["h080_bad_same_rank"].mean()),
                "mean_h098_frontier_cell_score": float(action_cells["h098_frontier_cell_score"].mean()),
                "max_h098_frontier_cell_score": float(action_cells["h098_frontier_cell_score"].max()),
                "assignment_route_score": float(route["assignment_route_score"]),
                "h071_route_score": float(route["route_score"]),
                "h071_route_rank": float(route["route_rank"]),
                "h071_novelty_rank": float(route["novelty_rank"]),
                "h071_shortcut_avoid_rank": float(route["shortcut_avoid_rank"]),
                **target_counts,
            }
        )
        cells_by_action[action_id] = action_cells

    actions = pd.DataFrame(rows)
    if actions.empty:
        return actions, cells_by_action
    actions["h099_route_score"] = (
        0.24 * rank01(-actions["model_pred_delta_vs_h057"].to_numpy(dtype=np.float64), high=True)
        + 0.15 * rank01(actions["mean_h098_frontier_cell_score"].to_numpy(dtype=np.float64), high=True)
        + 0.13 * actions["anti_h088_direction_rate"].to_numpy(dtype=np.float64)
        + 0.13 * actions["h057_positive_align_rate"].to_numpy(dtype=np.float64)
        + 0.12 * actions["selected_conflict_rate"].to_numpy(dtype=np.float64)
        + 0.09 * actions["assignment_route_score"].to_numpy(dtype=np.float64)
        + 0.08 * actions["selected_safe_cell_mean"].to_numpy(dtype=np.float64)
        - 0.12 * actions["mean_bad_same_rank"].to_numpy(dtype=np.float64)
        - 18.0 * np.maximum(actions["hard_diag_delta_vs_h057"].to_numpy(dtype=np.float64), 0.0)
        - 12.0 * np.maximum(actions["posterior_delta_vs_h057"].to_numpy(dtype=np.float64), 0.0)
    )
    return actions.sort_values("h099_route_score", ascending=False).reset_index(drop=True), cells_by_action


def candidate_specs() -> list[H099Spec]:
    return [
        H099Spec(
            name="route_conflict_c72_r28_a052",
            mode="conflict_invert",
            route_group="conflict",
            max_routes=28,
            max_cells=72,
            max_rows=28,
            max_per_subject=7,
            q2_cap=8,
            alpha=0.52,
            cap=0.68,
            min_route_score=0.52,
            min_cell_score=0.30,
            worldview="H098 conflict cells are safe only inside coherent H071 route templates",
        ),
        H099Spec(
            name="route_tail_hybrid_c120_r42_a044",
            mode="hybrid_route",
            route_group="tail",
            max_routes=42,
            max_cells=120,
            max_rows=42,
            max_per_subject=9,
            q2_cap=24,
            alpha=0.44,
            cap=0.58,
            min_route_score=0.50,
            min_cell_score=0.34,
            worldview="tail/edge route assignment separates safe action from H088 action toxicity",
        ),
        H099Spec(
            name="route_objective_descent_c130_r55_a042",
            mode="frontier_descent",
            route_group="objective",
            max_routes=55,
            max_cells=130,
            max_rows=55,
            max_per_subject=10,
            q2_cap=0,
            alpha=0.42,
            cap=0.56,
            min_route_score=0.48,
            min_cell_score=0.36,
            worldview="public-private equation is objective-stage route assignment, not Q2 support expansion",
        ),
        H099Spec(
            name="route_fullstate_descent_c98_r18_a030",
            mode="frontier_descent",
            route_group="full_state",
            max_routes=18,
            max_cells=98,
            max_rows=18,
            max_per_subject=5,
            q2_cap=18,
            alpha=0.30,
            cap=0.44,
            min_route_score=0.48,
            min_cell_score=0.28,
            worldview="H057 row-state signal generalizes as full-state route assignment with low amplitude",
        ),
        H099Spec(
            name="route_q2_counter_c64_r48_a050",
            mode="counter_h088",
            route_group="q2_route",
            max_routes=48,
            max_cells=64,
            max_rows=48,
            max_per_subject=8,
            q2_cap=48,
            alpha=0.50,
            cap=0.62,
            min_route_score=0.50,
            min_cell_score=0.34,
            worldview="Q2 route toxicity is H088 direction-specific and can be inverted safely",
        ),
        H099Spec(
            name="route_nonq2_positive_c96_r28_a038",
            mode="positive_bridge",
            route_group="nonq2_full",
            max_routes=28,
            max_cells=96,
            max_rows=28,
            max_per_subject=7,
            q2_cap=0,
            alpha=0.38,
            cap=0.52,
            min_route_score=0.46,
            min_cell_score=0.26,
            worldview="H057 non-Q2 positive row vector is a route-level teacher when H088 is anti-aligned",
        ),
    ]


def greedy_select_actions(actions: pd.DataFrame, cells_by_action: dict[str, pd.DataFrame], spec: H099Spec) -> tuple[pd.DataFrame, pd.DataFrame]:
    selected_actions = []
    selected_cells = []
    used_rows: set[int] = set()
    subject_counts: dict[str, int] = {}
    cell_count = 0
    q2_count = 0

    for rec in actions.sort_values("h099_route_score", ascending=False).to_dict("records"):
        if float(rec["h099_route_score"]) < spec.min_route_score:
            continue
        row = int(rec["row"])
        subject = str(rec["subject_id"])
        if row in used_rows:
            continue
        if len(selected_actions) >= spec.max_routes or len(used_rows) >= spec.max_rows:
            break
        cells = cells_by_action[str(rec["action_id"])].copy()
        n_cells = int(len(cells))
        n_q2 = int(cells["target"].astype(str).eq("Q2").sum())
        if cell_count + n_cells > spec.max_cells:
            continue
        if q2_count + n_q2 > spec.q2_cap:
            continue
        if subject_counts.get(subject, 0) + 1 > spec.max_per_subject:
            continue
        selected_actions.append(rec)
        selected_cells.append(cells)
        used_rows.add(row)
        subject_counts[subject] = subject_counts.get(subject, 0) + 1
        cell_count += n_cells
        q2_count += n_q2

    if not selected_actions:
        return pd.DataFrame(), pd.DataFrame()
    action_df = pd.DataFrame(selected_actions).reset_index(drop=True)
    cell_df = pd.concat(selected_cells, ignore_index=True)
    cell_df = cell_df.sort_values(["h099_action_id", "flat_index"]).drop_duplicates("flat_index", keep="first").reset_index(drop=True)
    return action_df, cell_df


def evaluate_route_candidate(
    candidate_id: str,
    prob: np.ndarray,
    move_mat: np.ndarray,
    base_prob: np.ndarray,
    selected_cells: pd.DataFrame,
    selected_actions: pd.DataFrame,
    cell: pd.DataFrame,
    sample: pd.DataFrame,
    fit: h097mod.ResponseFit,
    spec: H099Spec,
    path: Path,
) -> dict[str, object]:
    proxy = h097mod.H097Spec(
        name=spec.name,
        mode=spec.mode,
        target_group=spec.route_group,
        k=spec.max_cells,
        alpha=spec.alpha,
        cap=spec.cap,
        min_score=spec.min_cell_score,
        worldview=spec.worldview,
    )
    metrics = h097mod.evaluate_candidate(candidate_id, prob, move_mat, base_prob, selected_cells, cell, sample, fit, proxy, path)
    if selected_actions.empty:
        route_coherence = 0.0
    else:
        route_coherence = float(
            0.40 * selected_actions["assignment_route_score"].mean()
            + 0.25 * selected_actions["h099_route_score"].mean()
            + 0.20 * selected_actions["mean_h098_frontier_cell_score"].mean()
            + 0.15 * selected_actions["selected_conflict_rate"].mean()
        )
    metrics["selected_routes"] = int(len(selected_actions))
    metrics["mean_h099_route_score"] = float(selected_actions["h099_route_score"].mean()) if len(selected_actions) else 0.0
    metrics["mean_assignment_route_score"] = float(selected_actions["assignment_route_score"].mean()) if len(selected_actions) else 0.0
    metrics["mean_route_h098_score"] = float(selected_actions["mean_h098_frontier_cell_score"].mean()) if len(selected_actions) else 0.0
    metrics["route_coherence_score"] = route_coherence
    metrics["route_names"] = ",".join(sorted(selected_actions["route_name"].astype(str).unique().tolist())) if len(selected_actions) else ""
    metrics["h099_score"] = (
        300.0 * (-float(metrics["model_pred_delta_vs_h057"]))
        + 0.24 * route_coherence
        + 0.16 * float(metrics["anti_h088_direction_rate"])
        + 0.15 * float(metrics["h057_positive_align_rate"])
        + 0.13 * float(metrics["selected_conflict_rate"])
        + 0.10 * max(float(metrics["cos_h057_vs_h042_direction"]), 0.0)
        - 0.24 * max(float(metrics["cos_h088_direction"]), 0.0)
        - 0.26 * float(metrics["max_positive_bad_cosine"])
        - 25.0 * max(float(metrics["hard_diag_delta_vs_h057"]), 0.0)
        - 12.0 * max(float(metrics["posterior_delta_vs_h057"]), 0.0)
    )
    return metrics


def run() -> None:
    cleanup_previous_outputs()
    base = h085mod.load_sub(BASE_FILE)
    sample = base[KEYS].copy()
    base_prob = base[TARGETS].to_numpy(dtype=np.float64)
    cell_raw = h097mod.ensure_h095_cell_table(sample, base_prob)
    cell, feature_sets = h097mod.add_context_features(cell_raw, sample)
    public = h097mod.load_public_moves(sample, base_prob)
    model_scores, pred_rows, fit = h098mod.evaluate_weighted_models(public, cell, feature_sets)
    gradient = h097mod.response_gradient(cell, fit)
    pool = h098mod.build_frontier_pool(cell, gradient)
    routes = load_routes()

    candidate_rows = []
    action_frames = []
    selected_action_frames = []
    selected_cell_frames = []
    for spec in candidate_specs():
        actions, cells_by_action = route_action_table(routes, pool, cell, fit, base_prob, spec)
        if actions.empty:
            continue
        actions.insert(0, "spec_name", spec.name)
        action_frames.append(actions)
        selected_actions, selected_cells = greedy_select_actions(actions, cells_by_action, spec)
        if selected_cells.empty:
            continue
        move_mat = action_move_matrix(base_prob.shape, selected_cells, spec.alpha, spec.cap)
        prob = materialize_from_move(base_prob, move_mat)
        if int((np.abs(prob - base_prob) > TOL).sum()) == 0:
            continue
        hash_id = short_hash(prob)
        candidate_id = safe_id(f"h099_{spec.name}_{hash_id}", 128)
        path = OUT / f"submission_{candidate_id}.csv"
        h085mod.write_submission(sample, prob, path)
        metrics = evaluate_route_candidate(candidate_id, prob, move_mat, base_prob, selected_cells, selected_actions, cell, sample, fit, spec, path)
        candidate_rows.append(metrics)
        selected_actions = selected_actions.copy()
        selected_actions.insert(0, "candidate_id", candidate_id)
        selected_action_frames.append(selected_actions)
        selected_cells = selected_cells.copy()
        selected_cells.insert(0, "candidate_id", candidate_id)
        selected_cell_frames.append(selected_cells)

    candidates = pd.DataFrame(candidate_rows)
    if candidates.empty:
        raise RuntimeError("no H099 candidates")
    candidates = candidates.sort_values(["h099_score", "model_pred_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True)
    selected = candidates.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"submission_h099_route_equation_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)

    selected_model_row = model_scores.iloc[0].to_dict()
    decision = {
        "decision": "promote_h099_route_constrained_signed_assignment",
        "selected_candidate_id": selected["candidate_id"],
        "root_uploadsafe_path": str(root_path.resolve()),
        "worldview": selected["worldview"],
        "response_feature_set": fit.feature_set,
        "response_alpha": fit.alpha,
        **{f"response_{k}": v for k, v in selected_model_row.items() if k not in {"feature_set", "alpha"}},
        **selected,
        **{f"root_{key}": value for key, value in validation.items()},
    }

    public_out = public.drop(columns=["move_logit"]).copy()
    public_out["frontier_weight"] = h098mod.frontier_weights(public)
    public_out.to_csv(OUT / "h099_public_moves_weighted.csv", index=False)
    model_scores.to_csv(OUT / "h099_frontier_model_scores.csv", index=False)
    pred_rows.to_csv(OUT / "h099_frontier_loo_predictions.csv", index=False)
    pool.to_csv(OUT / "h099_action_pool.csv", index=False)
    pd.concat(action_frames, ignore_index=True).to_csv(OUT / "h099_route_actions.csv", index=False)
    candidates.to_csv(OUT / "h099_candidates.csv", index=False)
    pd.concat(selected_action_frames, ignore_index=True).to_csv(OUT / "h099_selected_route_actions.csv", index=False)
    pd.concat(selected_cell_frames, ignore_index=True).to_csv(OUT / "h099_selected_cells.csv", index=False)
    pd.DataFrame([decision]).to_csv(OUT / "h099_decision.csv", index=False)

    cols = [
        "candidate_id",
        "spec_name",
        "selected_routes",
        "selected_cells",
        "changed_rows_vs_h057",
        "model_pred_delta_vs_h057",
        "posterior_delta_vs_h057",
        "hard_diag_delta_vs_h057",
        "anti_h088_direction_rate",
        "h057_positive_align_rate",
        "selected_conflict_rate",
        "mean_assignment_route_score",
        "route_coherence_score",
        "cos_h088_direction",
        "cos_h057_vs_h042_direction",
        "max_positive_bad_cosine",
        "h099_score",
        "file",
    ]
    report = f"""# H099 Route-Constrained Signed Assignment Equation HS-JEPA

Question: are the H098 signed conflict cells safe only when decoded as coherent
row-route assignments?

Frontier response model:

{md_table(model_scores.head(12), 12)}

Candidates:

{md_table(candidates[cols], 20)}

Decision:

{md_table(pd.DataFrame([decision]), 1)}

Interpretation rule:

- If H099 improves over H098/H057, HS-JEPA should treat row-target assignment as
  the action decoder.  The hidden state is not just a cell gradient.
- If H099 loses while H098 improves, route constraints are too rigid and the
  signed equation should stay sparse/cell-local.
- If H099 and H098 both lose, H088 still explains action toxicity, but the
  useful public-safe assignment field is not captured by H071 route templates.
"""
    (OUT / "h099_report.md").write_text(report, encoding="utf-8")

    print(f"selected={decision['selected_candidate_id']}")
    print(f"root={root_path}")
    print(candidates[cols].head(10).to_string(index=False))
    print("\nfrontier model")
    print(model_scores.head(8).to_string(index=False))


if __name__ == "__main__":
    run()
