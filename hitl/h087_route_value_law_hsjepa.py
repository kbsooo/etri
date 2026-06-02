#!/usr/bin/env python3
"""H087: route-conditioned value-law HS-JEPA decoder.

H071 treated the problem as row-target route assignment.  H082 found a broad
source-action field.  H018 showed that public equations admit binary hard-label
worlds.  H086 then weakened the idea that the missing factor is a sharp public
responsibility vector.

H087 asks a different question:

    If the support/route is roughly known, is the missing hidden state the
    route-specific value law used to translate each route into probabilities?

The candidate is intentionally a big bet: for each route, the decoder can move
toward H085 posterior q, H082 source-action movement, H018 hard-world q, or
bridges among them.  A win would mean HS-JEPA should decode hidden human-state
routes with route-conditioned value laws rather than a single global correction
field.
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
OUT = HITL / "h087_route_value_law_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H085_PATH = HITL / "h085_augmented_public_equation_jepa.py"
SPEC = importlib.util.spec_from_file_location("h085mod", H085_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H085_PATH}")
h085mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h085mod
SPEC.loader.exec_module(h085mod)

TARGETS = h085mod.TARGETS
KEYS = h085mod.KEYS
EPS = h085mod.EPS
TOL = h085mod.TOL
BASE_FILE = h085mod.BASE_FILE
BASE_LB = h085mod.BASE_LB
BAD_ANCHORS = h085mod.BAD_ANCHORS


@dataclass(frozen=True)
class CandidateSpec:
    name: str
    target_group: str
    value_modes: tuple[str, ...]
    max_routes: int
    max_cells: int
    max_rows: int
    q2_cap: int
    max_per_subject: int
    min_action_score: float
    alpha: float
    cap: float
    novelty_bonus: str


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


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def safe_id(text: str, limit: int = 132) -> str:
    return h085mod.safe_id(text, limit=limit)


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return h085mod.md_table(frame, n=n)


def load_required_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h087_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h087_route_value_law_*_uploadsafe.csv"):
        path.unlink()


def target_allowed(targets: list[str], group: str) -> bool:
    target_set = set(targets)
    if group == "all":
        return True
    if group == "nonq2":
        return "Q2" not in target_set
    if group == "objective":
        return bool(target_set) and target_set.issubset({"Q3", "S1", "S2", "S3", "S4"})
    if group == "stage":
        return bool(target_set) and target_set.issubset({"S1", "S2", "S3", "S4"})
    if group == "q_route":
        return bool(target_set & {"Q1", "Q2", "Q3"}) and len(target_set & {"S1", "S2", "S3", "S4"}) <= 1
    raise ValueError(group)


def value_mode_move(cell: pd.DataFrame, mode: str) -> np.ndarray:
    h085_move = cell["h085_q_move"].to_numpy(dtype=np.float64)
    source_move = cell["source_mean_move"].fillna(0.0).to_numpy(dtype=np.float64)
    hard_move = cell["hard_logit_move"].fillna(0.0).to_numpy(dtype=np.float64)
    q061_move = logit(cell["q061"].to_numpy(dtype=np.float64)) - logit(cell["h057_prob"].to_numpy(dtype=np.float64))

    sign_hs = np.sign(h085_move) * np.sign(source_move)
    sign_hh = np.sign(h085_move) * np.sign(hard_move)
    sign_sh = np.sign(source_move) * np.sign(hard_move)

    if mode == "h085_q":
        move = h085_move
    elif mode == "source_mean":
        move = source_move
    elif mode == "hard_q":
        move = hard_move
    elif mode == "q061":
        move = q061_move
    elif mode == "q_source_bridge":
        move = np.where(sign_hs > 0, 0.55 * h085_move + 0.45 * source_move, 0.35 * h085_move)
    elif mode == "hard_source_bridge":
        move = np.where(sign_sh > 0, 0.58 * hard_move + 0.42 * source_move, 0.30 * hard_move)
    elif mode == "h085_hard_bridge":
        move = np.where(sign_hh > 0, 0.55 * h085_move + 0.45 * hard_move, 0.40 * h085_move)
    elif mode == "triad_consensus":
        signs = np.sign(np.vstack([h085_move, source_move, hard_move]))
        consensus = np.abs(signs.sum(axis=0))
        move = np.where(consensus >= 2.0, 0.40 * h085_move + 0.30 * source_move + 0.30 * hard_move, 0.25 * h085_move)
    elif mode == "hard_binary_edge":
        best_y = cell["best_world_y"].fillna(-1).to_numpy(dtype=np.float64)
        hard_conf = cell["confidence"].fillna(0.0).to_numpy(dtype=np.float64)
        agree = (best_y >= 0.0) & (hard_conf >= 0.70) & (sign_hh > 0)
        move = np.where(agree, 1.20 * hard_move, 0.20 * hard_move)
    else:
        raise ValueError(mode)
    return np.asarray(move, dtype=np.float64)


def action_metrics(cell: pd.DataFrame, raw_move: np.ndarray, alpha: float, cap: float) -> dict[str, float | np.ndarray]:
    base = cell["h057_prob"].to_numpy(dtype=np.float64)
    q085 = cell["h085_q"].to_numpy(dtype=np.float64)
    qhard = cell["q_hard"].to_numpy(dtype=np.float64)
    source = cell["source_mean_move"].fillna(0.0).to_numpy(dtype=np.float64)
    source_delta = cell["source_action_delta"].fillna(0.0).to_numpy(dtype=np.float64)
    resp = cell["h086_resp_weight"].fillna(1.0 / (250 * 7)).to_numpy(dtype=np.float64)

    move = np.clip(np.asarray(raw_move, dtype=np.float64) * alpha, -cap, cap)
    new_prob = sigmoid(logit(base) + move)
    posterior_delta = bce(new_prob, q085) - bce(base, q085)
    hard_delta = bce(new_prob, qhard) - bce(base, qhard)

    ratio = np.minimum(np.abs(move) / (np.abs(source) + 1.0e-6), 2.5)
    sign_agree = (np.sign(move) * np.sign(source) > 0).astype(np.float64)
    source_proxy = np.where(sign_agree > 0, source_delta * ratio, np.abs(source_delta) * ratio)
    source_proxy = np.where(np.abs(source) > 1.0e-10, source_proxy, 0.0)

    return {
        "move": move,
        "new_prob": new_prob,
        "posterior_delta_sum": float(posterior_delta.sum()),
        "posterior_delta_mean": float(posterior_delta.mean()) if len(posterior_delta) else 0.0,
        "hard_delta_sum": float(hard_delta.sum()),
        "hard_delta_mean": float(hard_delta.mean()) if len(hard_delta) else 0.0,
        "source_proxy_sum": float(source_proxy.sum()),
        "resp_delta_sum": float((posterior_delta * resp).sum()),
        "mean_abs_move": float(np.abs(move).mean()) if len(move) else 0.0,
        "max_abs_move": float(np.abs(move).max()) if len(move) else 0.0,
        "source_agree_rate": float(sign_agree.mean()) if len(sign_agree) else 0.0,
    }


def build_cell_table() -> pd.DataFrame:
    cell = load_required_csv(HITL / "h085_augmented_public_equation_jepa" / "h085_cell_table.csv")
    hard = load_required_csv(HITL / "h018_hard_label_world_jepa" / "h018_cell_hard_posterior.csv")
    resp = load_required_csv(HITL / "h086_public_responsibility_hsjepa" / "h086_cell_responsibility.csv")

    hard_cols = [
        "row",
        "target",
        "q_hard",
        "best_world_y",
        "confidence",
        "hard_gain",
        "combined_score",
        "hard_logit_delta",
        "binary_shock",
    ]
    cell = cell.merge(hard[hard_cols], on=["row", "target"], how="left")
    resp_cols = [
        "row",
        "target",
        "h086_resp_weight",
        "h086_resp_lift",
        "h086_resp_rank",
        "h086_equation_alignment",
        "h086_resp_action_score",
    ]
    cell = cell.merge(resp[resp_cols], on=["row", "target"], how="left")

    cell["q_hard"] = cell["q_hard"].fillna(cell["h085_q"])
    cell["best_world_y"] = cell["best_world_y"].fillna((cell["q_hard"] >= 0.5).astype(int))
    cell["confidence"] = cell["confidence"].fillna(np.maximum(cell["q_hard"], 1.0 - cell["q_hard"]))
    cell["hard_logit_move"] = logit(cell["q_hard"].to_numpy(dtype=np.float64)) - logit(cell["h057_prob"].to_numpy(dtype=np.float64))
    cell["hard_logit_move"] = np.clip(cell["hard_logit_move"].to_numpy(dtype=np.float64), -2.5, 2.5)
    cell["hard_gain_h057"] = bce(cell["h057_prob"].to_numpy(dtype=np.float64), cell["q_hard"].to_numpy(dtype=np.float64)) - bce(
        sigmoid(logit(cell["h057_prob"].to_numpy(dtype=np.float64)) + cell["hard_logit_move"].to_numpy(dtype=np.float64)),
        cell["q_hard"].to_numpy(dtype=np.float64),
    )
    cell["h086_resp_weight"] = cell["h086_resp_weight"].fillna(1.0 / len(cell))
    cell["h086_resp_lift"] = cell["h086_resp_lift"].fillna(1.0)
    cell["h086_resp_action_score"] = cell["h086_resp_action_score"].fillna(0.5)
    cell["source_mean_move"] = cell["source_mean_move"].fillna(0.0)
    cell["source_action_delta"] = cell["source_action_delta"].fillna(0.0)
    cell["source_agrees_h085"] = cell["source_agrees_h085"].fillna(0.0)
    return cell.sort_values(["row", "target_index"]).reset_index(drop=True)


def build_route_actions(cell: pd.DataFrame) -> pd.DataFrame:
    routes = load_required_csv(HITL / "h071_rowtarget_assignment_solver_jepa" / "h071_route_candidates.csv")
    modes = [
        "h085_q",
        "source_mean",
        "hard_q",
        "q061",
        "q_source_bridge",
        "hard_source_bridge",
        "h085_hard_bridge",
        "triad_consensus",
        "hard_binary_edge",
    ]

    rows: list[dict[str, object]] = []
    by_row = {int(r): g.copy() for r, g in cell.groupby("row", sort=False)}
    for route in routes.to_dict("records"):
        row = int(route["row"])
        targets = [str(t) for t in str(route["targets"]).split(",") if str(t)]
        route_cell = by_row[row]
        route_cell = route_cell[route_cell["target"].isin(targets)].copy()
        if route_cell.empty:
            continue
        for mode in modes:
            raw_move = value_mode_move(route_cell, mode)
            if np.max(np.abs(raw_move)) < 1.0e-10:
                continue
            metrics = action_metrics(route_cell, raw_move, alpha=1.0, cap=2.2)
            rows.append(
                {
                    "route_id": str(route["route_id"]),
                    "row": row,
                    "subject_id": str(route["subject_id"]),
                    "sleep_date": str(route["sleep_date"]),
                    "route_name": str(route["route_name"]),
                    "targets": ",".join(targets),
                    "target_group_key": "".join("1" if t in targets else "0" for t in TARGETS),
                    "n_cells": int(len(route_cell)),
                    "q2_cells": int((route_cell["target"] == "Q2").sum()),
                    "s_cells": int(route_cell["target"].isin(["S1", "S2", "S3", "S4"]).sum()),
                    "value_mode": mode,
                    "route_score": float(route.get("route_score", 0.0)),
                    "assignment_route_score": float(route.get("assignment_route_score", 0.0)),
                    "outside_h069_cells": int(route.get("outside_h069_cells", 0)),
                    "outside_h070_cells": int(route.get("outside_h070_cells", 0)),
                    "mean_shortcut_energy": float(route.get("mean_shortcut_energy", 0.0)),
                    "mean_public_score": float(route.get("mean_public_score", 0.0)),
                    "mean_invariant_score": float(route.get("mean_invariant_score", 0.0)),
                    "mean_h085_score": float(route_cell["h085_cell_score"].mean()),
                    "mean_h082_cell": float(route_cell["h082_cell"].mean()),
                    "mean_h076_hit": float(route_cell["hit_h076"].mean()),
                    "mean_h071_hit": float(route_cell["hit_h071"].mean()),
                    "mean_hard_confidence": float(route_cell["confidence"].mean()),
                    "mean_hard_combined": float(route_cell["combined_score"].fillna(0.0).mean()),
                    "mean_resp_action": float(route_cell["h086_resp_action_score"].mean()),
                    "mean_resp_lift": float(route_cell["h086_resp_lift"].mean()),
                    "source_agrees_h085_rate": float(route_cell["source_agrees_h085"].mean()),
                    "mean_bad_same_rank": float(route_cell["h080_bad_same_rank"].mean()),
                    "posterior_delta_sum": float(metrics["posterior_delta_sum"]),
                    "hard_delta_sum": float(metrics["hard_delta_sum"]),
                    "source_proxy_sum": float(metrics["source_proxy_sum"]),
                    "resp_delta_sum": float(metrics["resp_delta_sum"]),
                    "mean_abs_move": float(metrics["mean_abs_move"]),
                    "max_abs_move": float(metrics["max_abs_move"]),
                    "source_agree_rate": float(metrics["source_agree_rate"]),
                }
            )

    out = pd.DataFrame(rows)
    if out.empty:
        raise RuntimeError("no route actions")

    out["posterior_gain_rank"] = rank01(-out["posterior_delta_sum"].to_numpy(dtype=np.float64), high=True)
    out["hard_gain_rank"] = rank01(-out["hard_delta_sum"].to_numpy(dtype=np.float64), high=True)
    out["source_gain_rank"] = rank01(-out["source_proxy_sum"].to_numpy(dtype=np.float64), high=True)
    out["resp_gain_rank"] = rank01(-out["resp_delta_sum"].to_numpy(dtype=np.float64), high=True)
    out["assignment_rank"] = rank01(out["assignment_route_score"].to_numpy(dtype=np.float64), high=True)
    out["route_score_rank"] = rank01(out["route_score"].to_numpy(dtype=np.float64), high=True)
    out["outside_rank"] = rank01(out["outside_h069_cells"].to_numpy(dtype=np.float64), high=True)
    out["shortcut_avoid_rank"] = rank01(out["mean_shortcut_energy"].to_numpy(dtype=np.float64), high=False)
    out["bad_avoid_rank"] = rank01(out["mean_bad_same_rank"].to_numpy(dtype=np.float64), high=False)
    out["h082_rank"] = rank01(out["mean_h082_cell"].to_numpy(dtype=np.float64), high=True)
    out["hard_conf_rank"] = rank01(out["mean_hard_confidence"].to_numpy(dtype=np.float64), high=True)
    out["scale_rank"] = rank01(out["n_cells"].to_numpy(dtype=np.float64), high=True)

    mode_bonus = {
        "triad_consensus": 0.060,
        "q_source_bridge": 0.050,
        "hard_source_bridge": 0.050,
        "h085_hard_bridge": 0.040,
        "source_mean": 0.030,
        "hard_binary_edge": 0.030,
        "hard_q": 0.020,
        "h085_q": 0.010,
        "q061": 0.000,
    }
    out["mode_bonus"] = out["value_mode"].map(mode_bonus).fillna(0.0)
    out["value_law_score"] = (
        0.24 * out["posterior_gain_rank"]
        + 0.20 * out["source_gain_rank"]
        + 0.16 * out["hard_gain_rank"]
        + 0.09 * out["resp_gain_rank"]
        + 0.10 * out["assignment_rank"]
        + 0.07 * out["h082_rank"]
        + 0.06 * out["outside_rank"]
        + 0.05 * out["bad_avoid_rank"]
        + 0.03 * out["scale_rank"]
        + out["mode_bonus"]
        - 0.08 * (out["mean_bad_same_rank"].clip(0, 1) > 0.72).astype(float)
    )
    return out.sort_values("value_law_score", ascending=False).reset_index(drop=True)


def candidate_specs() -> list[CandidateSpec]:
    return [
        CandidateSpec(
            name="route_value_all_c980_r180_q95",
            target_group="all",
            value_modes=("triad_consensus", "q_source_bridge", "hard_source_bridge", "h085_hard_bridge", "source_mean", "hard_q"),
            max_routes=180,
            max_cells=980,
            max_rows=180,
            q2_cap=95,
            max_per_subject=30,
            min_action_score=0.625,
            alpha=1.05,
            cap=1.80,
            novelty_bonus="broad_route_value",
        ),
        CandidateSpec(
            name="route_value_hard_source_c900_r170_q85",
            target_group="all",
            value_modes=("hard_source_bridge", "triad_consensus", "hard_binary_edge", "hard_q"),
            max_routes=170,
            max_cells=900,
            max_rows=170,
            q2_cap=85,
            max_per_subject=28,
            min_action_score=0.600,
            alpha=1.10,
            cap=2.00,
            novelty_bonus="hard_world_route",
        ),
        CandidateSpec(
            name="route_value_private_nonq2_c820_r170",
            target_group="nonq2",
            value_modes=("triad_consensus", "q_source_bridge", "hard_source_bridge", "h085_hard_bridge", "source_mean"),
            max_routes=170,
            max_cells=820,
            max_rows=170,
            q2_cap=0,
            max_per_subject=28,
            min_action_score=0.595,
            alpha=1.08,
            cap=1.75,
            novelty_bonus="private_nonq2_value",
        ),
        CandidateSpec(
            name="route_value_objective_c780_r165",
            target_group="objective",
            value_modes=("triad_consensus", "q_source_bridge", "source_mean", "h085_hard_bridge"),
            max_routes=165,
            max_cells=780,
            max_rows=165,
            q2_cap=0,
            max_per_subject=28,
            min_action_score=0.585,
            alpha=1.10,
            cap=1.65,
            novelty_bonus="objective_value_route",
        ),
        CandidateSpec(
            name="route_value_q_route_c420_r150_q110",
            target_group="q_route",
            value_modes=("h085_hard_bridge", "hard_source_bridge", "triad_consensus", "hard_binary_edge", "h085_q"),
            max_routes=150,
            max_cells=420,
            max_rows=150,
            q2_cap=110,
            max_per_subject=24,
            min_action_score=0.575,
            alpha=1.15,
            cap=2.05,
            novelty_bonus="q_value_route",
        ),
        CandidateSpec(
            name="route_value_aggressive_c1200_r205_q125",
            target_group="all",
            value_modes=("triad_consensus", "q_source_bridge", "hard_source_bridge", "h085_hard_bridge", "source_mean", "hard_q", "h085_q"),
            max_routes=205,
            max_cells=1200,
            max_rows=205,
            q2_cap=125,
            max_per_subject=34,
            min_action_score=0.555,
            alpha=1.20,
            cap=2.10,
            novelty_bonus="aggressive_value_law",
        ),
    ]


def select_route_actions(actions: pd.DataFrame, spec: CandidateSpec) -> pd.DataFrame:
    selected = []
    used_rows: set[int] = set()
    used_routes: set[str] = set()
    subject_counts: dict[str, int] = {}
    n_cells = 0
    q2_cells = 0
    candidates = actions[
        actions["value_mode"].isin(spec.value_modes)
        & (actions["value_law_score"] >= spec.min_action_score)
    ].copy()

    for rec in candidates.sort_values("value_law_score", ascending=False).to_dict("records"):
        row = int(rec["row"])
        route_id = str(rec["route_id"])
        subject = str(rec["subject_id"])
        targets = [t for t in str(rec["targets"]).split(",") if t]
        if not target_allowed(targets, spec.target_group):
            continue
        if row in used_rows or route_id in used_routes:
            continue
        if len(selected) >= spec.max_routes:
            break
        if len(used_rows) >= spec.max_rows:
            break
        if n_cells + int(rec["n_cells"]) > spec.max_cells:
            continue
        if q2_cells + int(rec["q2_cells"]) > spec.q2_cap:
            continue
        if subject_counts.get(subject, 0) >= spec.max_per_subject:
            continue
        selected.append(rec)
        used_rows.add(row)
        used_routes.add(route_id)
        subject_counts[subject] = subject_counts.get(subject, 0) + 1
        n_cells += int(rec["n_cells"])
        q2_cells += int(rec["q2_cells"])

    return pd.DataFrame(selected)


def materialize_candidate(
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    cell: pd.DataFrame,
    selected_actions: pd.DataFrame,
    spec: CandidateSpec,
) -> tuple[np.ndarray, pd.DataFrame]:
    prob = base_prob.copy()
    cell_index = {(int(r.row), str(r.target)): int(r.flat_index) for r in cell.itertuples(index=False)}
    cell_lookup = cell.set_index(["row", "target"], drop=False)
    selected_cells: list[dict[str, object]] = []

    for action in selected_actions.to_dict("records"):
        row = int(action["row"])
        targets = [t for t in str(action["targets"]).split(",") if t]
        route_cell = cell_lookup.loc[(row, targets), :].copy() if len(targets) > 1 else cell_lookup.loc[[(row, targets[0])], :].copy()
        raw_move = value_mode_move(route_cell, str(action["value_mode"]))
        metrics = action_metrics(route_cell, raw_move, alpha=spec.alpha, cap=spec.cap)
        moves = np.asarray(metrics["move"], dtype=np.float64)
        for idx, target in enumerate(route_cell["target"].tolist()):
            flat = cell_index[(row, target)]
            target_idx = int(route_cell.iloc[idx]["target_index"])
            old = float(base_prob[row, target_idx])
            new = float(sigmoid(logit(np.array([old])) + np.array([moves[idx]]))[0])
            prob[row, target_idx] = new
            selected_cells.append(
                {
                    "row": row,
                    "subject_id": str(action["subject_id"]),
                    "sleep_date": str(action["sleep_date"]),
                    "route_id": str(action["route_id"]),
                    "route_name": str(action["route_name"]),
                    "target": target,
                    "target_index": target_idx,
                    "flat_index": flat,
                    "value_mode": str(action["value_mode"]),
                    "applied_logit_move": float(moves[idx]),
                    "old_prob": old,
                    "new_prob": new,
                    "prob_delta": new - old,
                    "h085_q": float(route_cell.iloc[idx]["h085_q"]),
                    "q_hard": float(route_cell.iloc[idx]["q_hard"]),
                    "source_mean_move": float(route_cell.iloc[idx]["source_mean_move"]),
                    "source_action_delta": float(route_cell.iloc[idx]["source_action_delta"]),
                    "h082_cell": float(route_cell.iloc[idx]["h082_cell"]),
                    "h086_resp_weight": float(route_cell.iloc[idx]["h086_resp_weight"]),
                    "h080_bad_same_rank": float(route_cell.iloc[idx]["h080_bad_same_rank"]),
                    "value_law_score": float(action["value_law_score"]),
                }
            )
    selected_cells_df = pd.DataFrame(selected_cells)
    return clip_prob(prob), selected_cells_df


def bad_anchor_cosines(delta: np.ndarray, sample: pd.DataFrame, base_prob: np.ndarray) -> dict[str, float]:
    flat_delta = delta.reshape(-1)
    out: dict[str, float] = {}
    dnorm = float(np.linalg.norm(flat_delta))
    if dnorm <= 0.0:
        return {f"bad_cos_{safe_id(name, 24)}": 0.0 for name in BAD_ANCHORS}
    for name in BAD_ANCHORS:
        path = h085mod.locate(name)
        if path is None:
            continue
        try:
            bad = h085mod.load_sub(path, sample)
        except Exception:
            continue
        bad_delta = bad[TARGETS].to_numpy(dtype=np.float64) - base_prob
        bflat = bad_delta.reshape(-1)
        denom = dnorm * float(np.linalg.norm(bflat))
        cos = 0.0 if denom <= 0 else float(np.dot(flat_delta, bflat) / denom)
        out[f"bad_cos_{safe_id(name, 24)}"] = cos
    return out


def evaluate_candidate(
    candidate_id: str,
    prob: np.ndarray,
    base_prob: np.ndarray,
    selected_actions: pd.DataFrame,
    selected_cells: pd.DataFrame,
    cell: pd.DataFrame,
    sample: pd.DataFrame,
    spec: CandidateSpec,
    path: Path,
) -> dict[str, object]:
    q085 = cell.sort_values("flat_index")["h085_q"].to_numpy(dtype=np.float64).reshape(base_prob.shape)
    qhard = cell.sort_values("flat_index")["q_hard"].to_numpy(dtype=np.float64).reshape(base_prob.shape)
    resp = cell.sort_values("flat_index")["h086_resp_weight"].to_numpy(dtype=np.float64).reshape(base_prob.shape)
    posterior_delta = float((bce(prob, q085) - bce(base_prob, q085)).mean())
    hard_delta = float((bce(prob, qhard) - bce(base_prob, qhard)).mean())
    resp_delta = float(((bce(prob, q085) - bce(base_prob, q085)) * resp).sum())

    if selected_cells.empty:
        source_proxy_delta = 0.0
        source_agree_rate = 0.0
        h082_ratio = 0.0
        mean_bad_same = 0.0
        route_templates = ""
    else:
        source = selected_cells["source_mean_move"].to_numpy(dtype=np.float64)
        move = selected_cells["applied_logit_move"].to_numpy(dtype=np.float64)
        source_delta = selected_cells["source_action_delta"].to_numpy(dtype=np.float64)
        ratio = np.minimum(np.abs(move) / (np.abs(source) + 1.0e-6), 2.5)
        agree = (np.sign(move) * np.sign(source) > 0).astype(float)
        proxy = np.where(agree > 0, source_delta * ratio, np.abs(source_delta) * ratio)
        proxy = np.where(np.abs(source) > 1.0e-10, proxy, 0.0)
        source_proxy_delta = float(proxy.sum() / base_prob.size)
        source_agree_rate = float(agree.mean())
        h082_ratio = float(selected_cells["h082_cell"].mean())
        mean_bad_same = float(selected_cells["h080_bad_same_rank"].mean())
        route_templates = ";".join(
            f"{k}:{v}" for k, v in selected_actions["route_name"].value_counts().sort_index().items()
        )

    target_counts = {
        f"{target}_changed_vs_h057": int((np.abs(prob[:, i] - base_prob[:, i]) > TOL).sum())
        for i, target in enumerate(TARGETS)
    }
    bad_cos = bad_anchor_cosines(prob - base_prob, sample, base_prob)
    max_positive_bad = max([0.0] + [v for v in bad_cos.values() if v > 0])
    validation = h085mod.validate_submission(path, sample, base_prob)

    scale = len(selected_cells) / base_prob.size if base_prob.size else 0.0
    score = (
        380.0 * (-posterior_delta)
        + 185.0 * (-hard_delta)
        + 220.0 * (-source_proxy_delta)
        + 120.0 * (-resp_delta)
        + 0.16 * source_agree_rate
        + 0.13 * h082_ratio
        + 0.10 * min(scale / 0.55, 1.0)
        - 0.35 * max_positive_bad
        - 0.10 * max(mean_bad_same - 0.55, 0.0)
    )

    out: dict[str, object] = {
        "candidate_id": candidate_id,
        "spec_name": spec.name,
        "target_group": spec.target_group,
        "value_modes": ",".join(spec.value_modes),
        "novelty_bonus": spec.novelty_bonus,
        "alpha": spec.alpha,
        "cap": spec.cap,
        "selected_routes": int(len(selected_actions)),
        "selected_cells": int(len(selected_cells)),
        "changed_cells_vs_h057": int((np.abs(prob - base_prob) > TOL).sum()),
        "changed_rows_vs_h057": int((np.abs(prob - base_prob) > TOL).any(axis=1).sum()),
        "q2_cells": int(target_counts.get("Q2_changed_vs_h057", 0)),
        "posterior_delta_vs_h057": posterior_delta,
        "hard_delta_vs_h057": hard_delta,
        "source_proxy_delta_vs_h057": source_proxy_delta,
        "responsibility_weighted_delta_vs_h057": resp_delta,
        "max_positive_bad_cosine": float(max_positive_bad),
        "source_agree_rate": source_agree_rate,
        "h082_ratio": h082_ratio,
        "mean_bad_same_rank": mean_bad_same,
        "mean_abs_prob_move_vs_h057": float(np.abs(prob - base_prob).mean()),
        "max_abs_prob_move_vs_h057": float(np.abs(prob - base_prob).max()),
        "selected_subjects": int(selected_actions["subject_id"].nunique()) if not selected_actions.empty else 0,
        "selected_rows": ",".join(map(str, sorted(selected_actions["row"].astype(int).tolist()))) if not selected_actions.empty else "",
        "route_templates": route_templates,
        "h087_score": score,
        "file": path.name,
        "resolved_path": str(path.resolve()),
    }
    out.update(target_counts)
    out.update(bad_cos)
    out.update(validation)
    return out


def run() -> None:
    cleanup_previous_outputs()
    sample = pd.read_csv(ROOT / "data" / "ch2026_submission_sample.csv", parse_dates=KEYS)
    sample = sample.sort_values(KEYS).reset_index(drop=True)
    base = h085mod.load_sub(BASE_FILE, sample)
    base_prob = base[TARGETS].to_numpy(dtype=np.float64)

    cell = build_cell_table()
    route_actions = build_route_actions(cell)
    route_actions.to_csv(OUT / "h087_route_value_actions.csv", index=False)

    candidate_rows: list[dict[str, object]] = []
    all_selected_actions: list[pd.DataFrame] = []
    all_selected_cells: list[pd.DataFrame] = []
    for spec in candidate_specs():
        selected_actions = select_route_actions(route_actions, spec)
        if selected_actions.empty:
            continue
        prob, selected_cells = materialize_candidate(sample, base_prob, cell, selected_actions, spec)
        hash_id = short_hash(prob)
        candidate_id = safe_id(f"h087_{spec.name}_{hash_id}", 128)
        path = OUT / f"submission_{candidate_id}.csv"
        h085mod.write_submission(sample, prob, path)
        metrics = evaluate_candidate(candidate_id, prob, base_prob, selected_actions, selected_cells, cell, sample, spec, path)
        candidate_rows.append(metrics)
        selected_actions = selected_actions.copy()
        selected_actions.insert(0, "candidate_id", candidate_id)
        selected_cells = selected_cells.copy()
        selected_cells.insert(0, "candidate_id", candidate_id)
        all_selected_actions.append(selected_actions)
        all_selected_cells.append(selected_cells)

    candidates = pd.DataFrame(candidate_rows)
    if candidates.empty:
        raise RuntimeError("no candidates")
    candidates = candidates.sort_values("h087_score", ascending=False).reset_index(drop=True)
    candidates.to_csv(OUT / "h087_candidates.csv", index=False)
    pd.concat(all_selected_actions, ignore_index=True).to_csv(OUT / "h087_selected_route_actions.csv", index=False)
    pd.concat(all_selected_cells, ignore_index=True).to_csv(OUT / "h087_selected_cells.csv", index=False)

    decision = candidates.iloc[0].to_dict()
    selected_path = Path(str(decision["resolved_path"]))
    root_path = ROOT / f"submission_h087_route_value_law_{decision['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)
    decision.update({"root_uploadsafe_path": str(root_path.resolve()), **{f"root_{k}": v for k, v in validation.items()}})
    pd.DataFrame([decision]).to_csv(OUT / "h087_decision.csv", index=False)

    top_actions = route_actions.head(40)[
        [
            "route_id",
            "row",
            "subject_id",
            "sleep_date",
            "route_name",
            "targets",
            "value_mode",
            "value_law_score",
            "posterior_delta_sum",
            "hard_delta_sum",
            "source_proxy_sum",
            "assignment_route_score",
            "mean_h082_cell",
            "mean_bad_same_rank",
        ]
    ]
    report = f"""# H087 Route-Conditioned Value-Law HS-JEPA

Question: if row-target support is roughly known, is the missing hidden state
the route-specific value law that translates each human-state route into
probabilities?

Worldview:

- H086 weakened sharp public-responsibility weighting, so H087 does not bet on
  a tiny public subset.
- H071 supplies row-target routes.
- H082 supplies action-health/source movement.
- H018 supplies binary hard-label public worlds.
- The decoder chooses a value law per route: H085 posterior, H082 source,
  H018 hard-world, or bridges among them.

Decision:

| decision | selected_candidate_id | root_uploadsafe_path | worldview |
| --- | --- | --- | --- |
| promote_route_conditioned_value_law_bigbet | {decision['candidate_id']} | {decision['root_uploadsafe_path']} | route support is not enough; HS-JEPA needs route-conditioned value-law decoding |

Candidates:

{md_table(candidates.drop(columns=[c for c in candidates.columns if c.startswith('bad_cos_')], errors='ignore'), n=20)}

Top Route-Value Actions:

{md_table(top_actions, n=40)}

Interpretation rule:

- If H087 improves by >= 0.001 vs H057, route-conditioned value-law decoding
  becomes a core HS-JEPA component.
- If H087 is near H057, route assignment/action support is real but value-law
  translation remains unresolved.
- If H087 loses badly, H018/H082/H085 value laws are mutually incompatible and
  should not be combined route-wise without a stronger private-state constraint.
"""
    (OUT / "h087_report.md").write_text(report, encoding="utf-8")

    print(f"selected={decision['candidate_id']}")
    print(f"root={root_path}")
    print(candidates.head(6).to_string(index=False))


if __name__ == "__main__":
    run()
