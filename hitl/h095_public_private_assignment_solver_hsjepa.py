#!/usr/bin/env python3
"""H095: public/private row-target assignment equation solver HS-JEPA.

H088 gave a useful negative sensor: forcing H085 posterior and H018 hard-world
to be jointly Pareto-safe looked locally coherent, but public LB punished it.

H095 therefore changes the role of H088.  H018 is no longer an action target,
and H088 is treated as an observed toxic action field.  The decoder asks:

    Which row-target route actions remain safe under the refit public equation
    after penalizing directions that H088 showed public dislikes?

This is a row-target assignment/equation solver rather than a stronger context
encoder.  It uses H057 as the positive base signal, H088 as the negative action
sensor, and H018 only as a stress diagnostic.
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
OUT = HITL / "h095_public_private_assignment_solver_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H087_PATH = HITL / "h087_route_value_law_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h087mod", H087_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H087_PATH}")
h087mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h087mod
SPEC.loader.exec_module(h087mod)

h085mod = h087mod.h085mod

TARGETS = h087mod.TARGETS
KEYS = h087mod.KEYS
EPS = h087mod.EPS
TOL = h087mod.TOL
BASE_FILE = h087mod.BASE_FILE

H042_FILE = "submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv"
H050_FILE = "submission_h050_target_route_phase_b140216b_uploadsafe.csv"
H088_FILE = "submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv"


@dataclass(frozen=True)
class H095Spec:
    name: str
    target_group: str
    value_modes: tuple[str, ...]
    max_routes: int
    max_cells: int
    max_rows: int
    q2_cap: int
    max_per_subject: int
    min_action_score: float
    max_toxic_mean: float
    alpha: float
    cap: float
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


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def safe_id(text: str, limit: int = 132) -> str:
    return h085mod.safe_id(text, limit=limit)


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return h085mod.md_table(frame, n=n)


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h095_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h095_assignment_solver_*_uploadsafe.csv"):
        path.unlink()


def load_optional_prob(name: str, sample: pd.DataFrame) -> np.ndarray | None:
    path = h085mod.locate(name)
    if path is None:
        return None
    try:
        return h085mod.load_sub(path, sample)[TARGETS].to_numpy(dtype=np.float64)
    except Exception:
        return None


def refit_public_equation(sample: pd.DataFrame, base_prob: np.ndarray) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray]:
    known = h085mod.public_observations(sample)
    pred_by_file = {
        str(rec["file"]): h085mod.load_sub(str(rec["file"]), sample)[TARGETS].to_numpy(dtype=np.float64)
        for rec in known.to_dict("records")
    }
    equations, a, d0_rows, b = h085mod.build_equation_system(known, pred_by_file, base_prob)
    priors = h085mod.make_priors(known, pred_by_file, base_prob, sample)
    configs, full_qs = h085mod.evaluate_configs(equations, a, d0_rows, b, priors)
    selected_key = str(configs.iloc[0]["posterior_key"])
    q_prob = full_qs[selected_key].reshape(base_prob.shape)
    return known, configs, q_prob


def merge_diagnostic_heads(cell: pd.DataFrame) -> pd.DataFrame:
    hard = pd.read_csv(HITL / "h018_hard_label_world_jepa" / "h018_cell_hard_posterior.csv")
    resp = pd.read_csv(HITL / "h086_public_responsibility_hsjepa" / "h086_cell_responsibility.csv")

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
    resp_cols = [
        "row",
        "target",
        "h086_resp_weight",
        "h086_resp_lift",
        "h086_resp_rank",
        "h086_equation_alignment",
        "h086_resp_action_score",
    ]
    out = cell.merge(hard[hard_cols], on=["row", "target"], how="left")
    out = out.merge(resp[resp_cols], on=["row", "target"], how="left")
    out["q_hard"] = out["q_hard"].fillna(out["h085_q"])
    out["best_world_y"] = out["best_world_y"].fillna((out["q_hard"] >= 0.5).astype(int))
    out["confidence"] = out["confidence"].fillna(np.maximum(out["q_hard"], 1.0 - out["q_hard"]))
    out["hard_logit_move"] = logit(out["q_hard"].to_numpy(dtype=np.float64)) - logit(out["h057_prob"].to_numpy(dtype=np.float64))
    out["hard_logit_move"] = np.clip(out["hard_logit_move"].to_numpy(dtype=np.float64), -2.5, 2.5)
    out["hard_diag_gain"] = bce(out["h057_prob"].to_numpy(dtype=np.float64), out["q_hard"].to_numpy(dtype=np.float64)) - bce(
        sigmoid(logit(out["h057_prob"].to_numpy(dtype=np.float64)) + out["hard_logit_move"].to_numpy(dtype=np.float64)),
        out["q_hard"].to_numpy(dtype=np.float64),
    )
    out["h086_resp_weight"] = out["h086_resp_weight"].fillna(1.0 / len(out))
    out["h086_resp_lift"] = out["h086_resp_lift"].fillna(1.0)
    out["h086_resp_action_score"] = out["h086_resp_action_score"].fillna(0.5)
    out["source_mean_move"] = out["source_mean_move"].fillna(0.0)
    out["source_action_delta"] = out["source_action_delta"].fillna(0.0)
    out["source_agrees_h085"] = out["source_agrees_h085"].fillna(0.0)
    return out


def add_h088_toxicity(
    cell: pd.DataFrame,
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    q_prob: np.ndarray,
) -> pd.DataFrame:
    out = cell.sort_values(["row", "target_index"]).reset_index(drop=True).copy()
    h088_prob = load_optional_prob(H088_FILE, sample)
    if h088_prob is None:
        raise FileNotFoundError(H088_FILE)
    h042_prob = load_optional_prob(H042_FILE, sample)
    h050_prob = load_optional_prob(H050_FILE, sample)

    base_flat = base_prob.reshape(-1)
    q_flat = q_prob.reshape(-1)
    h088_flat = h088_prob.reshape(-1)
    h088_move = (logit(h088_prob) - logit(base_prob)).reshape(-1)
    h088_active = (np.abs(h088_flat - base_flat) > TOL).astype(float)
    h088_q_delta = bce(h088_flat, q_flat) - bce(base_flat, q_flat)
    h088_bad = np.maximum(h088_q_delta, 0.0) * h088_active
    out["h088_prob"] = h088_flat
    out["h088_logit_move"] = h088_move
    out["h088_active"] = h088_active
    out["h088_q_delta"] = h088_q_delta
    out["h088_q_bad"] = h088_bad
    out["h088_bad_rank"] = rank01(h088_bad, high=True)
    out["h088_move_abs_rank"] = rank01(np.abs(h088_move) * h088_active, high=True)
    out["h088_toxicity"] = h088_active * (
        0.55 * out["h088_bad_rank"].to_numpy(dtype=np.float64)
        + 0.30 * out["h088_move_abs_rank"].to_numpy(dtype=np.float64)
        + 0.15 * rank01(np.abs(h088_q_delta) * h088_active, high=True)
    )

    pos_weights: list[np.ndarray] = []
    pos_moves: list[np.ndarray] = []
    for anchor_prob in [h042_prob, h050_prob]:
        if anchor_prob is None:
            continue
        anchor_flat = anchor_prob.reshape(-1)
        active = (np.abs(base_flat - anchor_flat) > TOL).astype(float)
        pos_move = (logit(base_prob) - logit(anchor_prob)).reshape(-1)
        gain = bce(anchor_flat, q_flat) - bce(base_flat, q_flat)
        weight = active * (
            0.52 * rank01(np.maximum(gain, 0.0), high=True)
            + 0.33 * rank01(np.abs(pos_move) * active, high=True)
            + 0.15 * active
        )
        pos_weights.append(weight)
        pos_moves.append(pos_move)

    if pos_weights:
        pos_weight = np.maximum.reduce(pos_weights)
        pos_move = np.mean(np.vstack(pos_moves), axis=0)
    else:
        pos_weight = np.zeros_like(base_flat)
        pos_move = np.zeros_like(base_flat)
    out["h057_positive_weight"] = pos_weight
    out["h057_positive_logit_move"] = pos_move
    out["h095_safe_cell_score"] = (
        0.25 * rank01(out["h085_q_gain"].to_numpy(dtype=np.float64), high=True)
        + 0.15 * rank01(out["h085_abs_q_move"].to_numpy(dtype=np.float64), high=True)
        + 0.12 * out["public_score"].to_numpy(dtype=np.float64)
        + 0.12 * out["invariant_score"].to_numpy(dtype=np.float64)
        + 0.10 * out["source_agrees_h085"].to_numpy(dtype=np.float64)
        + 0.08 * out["h082_cell"].to_numpy(dtype=np.float64)
        + 0.08 * out["h057_positive_weight"].to_numpy(dtype=np.float64)
        + 0.05 * out["outside_h069_cell"].to_numpy(dtype=np.float64)
        - 0.26 * out["h088_toxicity"].to_numpy(dtype=np.float64)
        - 0.12 * out["h080_bad_same_rank"].to_numpy(dtype=np.float64)
        - 0.08 * rank01(out["latent_shortcut_energy"].to_numpy(dtype=np.float64), high=True)
        - 0.14 * out["is_h050_null"].to_numpy(dtype=np.float64)
    )
    return out


def build_h095_cell_table(sample: pd.DataFrame, base_prob: np.ndarray) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, np.ndarray]:
    known, configs, q_prob = refit_public_equation(sample, base_prob)
    cell_table, _row_table = h085mod.add_support_tables(sample, base_prob, q_prob)
    cell_table = merge_diagnostic_heads(cell_table)
    cell_table = add_h088_toxicity(cell_table, sample, base_prob, q_prob)
    cell_table.to_csv(OUT / "h095_cell_toxicity_table.csv", index=False)
    return known, configs, cell_table, q_prob


def action_extra_metrics(route_cell: pd.DataFrame, raw_move: np.ndarray) -> dict[str, float]:
    move = np.clip(np.asarray(raw_move, dtype=np.float64), -2.2, 2.2)
    h088_move = route_cell["h088_logit_move"].to_numpy(dtype=np.float64)
    h088_tox = route_cell["h088_toxicity"].to_numpy(dtype=np.float64)
    h088_active = route_cell["h088_active"].to_numpy(dtype=np.float64)
    pos_move = route_cell["h057_positive_logit_move"].to_numpy(dtype=np.float64)
    pos_weight = route_cell["h057_positive_weight"].to_numpy(dtype=np.float64)

    same_toxic = ((np.sign(move) * np.sign(h088_move)) > 0).astype(float) * h088_active
    anti_toxic = ((np.sign(move) * np.sign(h088_move)) < 0).astype(float) * h088_active
    tox_ratio = np.minimum(np.abs(move) / (np.abs(h088_move) + 1.0e-6), 2.5)
    toxic_sum = float(np.sum(same_toxic * h088_tox * tox_ratio))
    anti_sum = float(np.sum(anti_toxic * h088_tox * tox_ratio))

    same_pos = ((np.sign(move) * np.sign(pos_move)) > 0).astype(float)
    opp_pos = ((np.sign(move) * np.sign(pos_move)) < 0).astype(float)
    pos_ratio = np.minimum(np.abs(move) / (np.abs(pos_move) + 1.0e-6), 2.5)
    h057_pos_sum = float(np.sum(same_pos * pos_weight * pos_ratio))
    h057_opp_sum = float(np.sum(opp_pos * pos_weight * pos_ratio))

    return {
        "toxicity_sum": toxic_sum,
        "toxicity_mean": toxic_sum / max(len(route_cell), 1),
        "anti_h088_sum": anti_sum,
        "h057_positive_sum": h057_pos_sum,
        "h057_positive_opp_sum": h057_opp_sum,
        "h088_active_rate": float(h088_active.mean()) if len(route_cell) else 0.0,
        "h057_positive_rate": float((pos_weight > 0).mean()) if len(route_cell) else 0.0,
        "mean_h095_safe_cell": float(route_cell["h095_safe_cell_score"].mean()) if len(route_cell) else 0.0,
        "mean_h088_toxicity": float(route_cell["h088_toxicity"].mean()) if len(route_cell) else 0.0,
        "mean_h057_positive_weight": float(route_cell["h057_positive_weight"].mean()) if len(route_cell) else 0.0,
    }


def build_assignment_actions(cell: pd.DataFrame) -> pd.DataFrame:
    actions = h087mod.build_route_actions(cell)
    by_row = {int(row): group.copy() for row, group in cell.groupby("row", sort=False)}
    rows = []
    for rec in actions.to_dict("records"):
        row = int(rec["row"])
        targets = [target for target in str(rec["targets"]).split(",") if target]
        route_cell = by_row[row]
        route_cell = route_cell[route_cell["target"].isin(targets)].copy()
        if route_cell.empty:
            continue
        raw_move = h087mod.value_mode_move(route_cell, str(rec["value_mode"]))
        extra = action_extra_metrics(route_cell, raw_move)
        rows.append({**rec, **extra})

    out = pd.DataFrame(rows)
    out["h095_posterior_rank"] = rank01(-out["posterior_delta_sum"].to_numpy(dtype=np.float64), high=True)
    out["h095_source_rank"] = rank01(-out["source_proxy_sum"].to_numpy(dtype=np.float64), high=True)
    out["h095_hard_diag_rank"] = rank01(-out["hard_delta_sum"].to_numpy(dtype=np.float64), high=True)
    out["h095_assignment_rank"] = rank01(out["assignment_route_score"].to_numpy(dtype=np.float64), high=True)
    out["h095_h082_rank"] = rank01(out["mean_h082_cell"].to_numpy(dtype=np.float64), high=True)
    out["h095_safe_cell_rank"] = rank01(out["mean_h095_safe_cell"].to_numpy(dtype=np.float64), high=True)
    out["h095_h057_pos_rank"] = rank01(out["h057_positive_sum"].to_numpy(dtype=np.float64), high=True)
    out["h095_anti_h088_rank"] = rank01(out["anti_h088_sum"].to_numpy(dtype=np.float64), high=True)
    out["h095_toxic_rank"] = rank01(out["toxicity_sum"].to_numpy(dtype=np.float64), high=True)
    out["h095_pos_opp_rank"] = rank01(out["h057_positive_opp_sum"].to_numpy(dtype=np.float64), high=True)
    out["h095_bad_avoid_rank"] = rank01(out["mean_bad_same_rank"].to_numpy(dtype=np.float64), high=False)
    mode_bonus = {
        "q_source_bridge": 0.060,
        "triad_consensus": 0.050,
        "source_mean": 0.045,
        "h085_q": 0.035,
        "h085_hard_bridge": 0.025,
        "q061": 0.018,
        "hard_source_bridge": 0.012,
        "hard_q": 0.000,
        "hard_binary_edge": -0.020,
    }
    out["h095_mode_bonus"] = out["value_mode"].map(mode_bonus).fillna(0.0)
    out["h095_action_score"] = (
        0.28 * out["h095_posterior_rank"]
        + 0.15 * out["h095_source_rank"]
        + 0.12 * out["h095_assignment_rank"]
        + 0.10 * out["h095_safe_cell_rank"]
        + 0.09 * out["h095_h057_pos_rank"]
        + 0.08 * out["h095_h082_rank"]
        + 0.05 * out["h095_anti_h088_rank"]
        + 0.05 * out["h095_bad_avoid_rank"]
        + 0.04 * out["scale_rank"]
        + 0.03 * out["h095_hard_diag_rank"]
        + out["h095_mode_bonus"]
        - 0.34 * out["h095_toxic_rank"]
        - 0.08 * out["h095_pos_opp_rank"]
        - 0.08 * (out["toxicity_mean"] > 0.22).astype(float)
        - 0.07 * (out["mean_bad_same_rank"] > 0.72).astype(float)
    )
    return out.sort_values("h095_action_score", ascending=False).reset_index(drop=True)


def target_allowed(targets: list[str], group: str) -> bool:
    return h087mod.target_allowed(targets, group)


def candidate_specs() -> list[H095Spec]:
    return [
        H095Spec(
            name="equation_safe_all_c860_r180_q85",
            target_group="all",
            value_modes=("q_source_bridge", "triad_consensus", "source_mean", "h085_q", "h085_hard_bridge"),
            max_routes=180,
            max_cells=860,
            max_rows=180,
            q2_cap=85,
            max_per_subject=28,
            min_action_score=0.520,
            max_toxic_mean=0.180,
            alpha=1.00,
            cap=1.65,
            worldview="H057-positive equation actions survive only after H088-toxic directions are vetoed",
        ),
        H095Spec(
            name="anti_h088_nonq2_c680_r165",
            target_group="nonq2",
            value_modes=("q_source_bridge", "triad_consensus", "source_mean", "h085_q"),
            max_routes=165,
            max_cells=680,
            max_rows=165,
            q2_cap=0,
            max_per_subject=26,
            min_action_score=0.505,
            max_toxic_mean=0.145,
            alpha=1.08,
            cap=1.60,
            worldview="public-safe private body state is non-Q2 and must actively avoid H088 directions",
        ),
        H095Spec(
            name="q2_reopen_toxic_veto_c360_r145_q120",
            target_group="q_route",
            value_modes=("q_source_bridge", "h085_q", "triad_consensus", "h085_hard_bridge"),
            max_routes=145,
            max_cells=360,
            max_rows=145,
            q2_cap=120,
            max_per_subject=22,
            min_action_score=0.490,
            max_toxic_mean=0.160,
            alpha=1.12,
            cap=1.85,
            worldview="Q2 is not closed; it is only closed for H088-toxic directions",
        ),
        H095Spec(
            name="h057_positive_route_c520_r135_q45",
            target_group="all",
            value_modes=("q_source_bridge", "triad_consensus", "source_mean"),
            max_routes=135,
            max_cells=520,
            max_rows=135,
            q2_cap=45,
            max_per_subject=22,
            min_action_score=0.500,
            max_toxic_mean=0.125,
            alpha=1.05,
            cap=1.55,
            worldview="reuse the H057/H042 positive route basin but not the H088 action law",
        ),
        H095Spec(
            name="aggressive_assignment_c1180_r220_q110",
            target_group="all",
            value_modes=("q_source_bridge", "triad_consensus", "source_mean", "h085_q", "h085_hard_bridge", "q061"),
            max_routes=220,
            max_cells=1180,
            max_rows=220,
            q2_cap=110,
            max_per_subject=34,
            min_action_score=0.470,
            max_toxic_mean=0.240,
            alpha=1.15,
            cap=1.95,
            worldview="large public/private assignment field beats H057 if toxic action is separated correctly",
        ),
    ]


def select_actions(actions: pd.DataFrame, spec: H095Spec) -> pd.DataFrame:
    selected = []
    used_rows: set[int] = set()
    subject_counts: dict[str, int] = {}
    n_cells = 0
    q2_cells = 0
    pool = actions[
        actions["value_mode"].isin(spec.value_modes)
        & (actions["h095_action_score"] >= spec.min_action_score)
        & (actions["toxicity_mean"] <= spec.max_toxic_mean)
    ].sort_values("h095_action_score", ascending=False)

    for rec in pool.to_dict("records"):
        row = int(rec["row"])
        subject = str(rec["subject_id"])
        targets = [target for target in str(rec["targets"]).split(",") if target]
        if not target_allowed(targets, spec.target_group):
            continue
        if row in used_rows:
            continue
        if len(selected) >= spec.max_routes or len(used_rows) >= spec.max_rows:
            break
        if n_cells + int(rec["n_cells"]) > spec.max_cells:
            continue
        if q2_cells + int(rec["q2_cells"]) > spec.q2_cap:
            continue
        if subject_counts.get(subject, 0) >= spec.max_per_subject:
            continue
        selected.append(rec)
        used_rows.add(row)
        subject_counts[subject] = subject_counts.get(subject, 0) + 1
        n_cells += int(rec["n_cells"])
        q2_cells += int(rec["q2_cells"])
    return pd.DataFrame(selected)


def materialize_candidate(
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    cell: pd.DataFrame,
    selected_actions: pd.DataFrame,
    spec: H095Spec,
) -> tuple[np.ndarray, pd.DataFrame]:
    prob = base_prob.copy()
    selected_cells: list[dict[str, object]] = []
    by_row = {int(row): group.copy() for row, group in cell.groupby("row", sort=False)}

    for action in selected_actions.to_dict("records"):
        row = int(action["row"])
        targets = [target for target in str(action["targets"]).split(",") if target]
        route_cell = by_row[row]
        route_cell = route_cell[route_cell["target"].isin(targets)].copy().sort_values("target_index")
        raw_move = h087mod.value_mode_move(route_cell, str(action["value_mode"]))
        move = np.clip(raw_move * spec.alpha, -spec.cap, spec.cap)
        for idx, rec in enumerate(route_cell.to_dict("records")):
            target_idx = int(rec["target_index"])
            old = float(base_prob[row, target_idx])
            new = float(sigmoid(logit(np.array([old])) + np.array([move[idx]]))[0])
            prob[row, target_idx] = new
            selected_cells.append(
                {
                    "row": row,
                    "subject_id": str(action["subject_id"]),
                    "sleep_date": str(action["sleep_date"]),
                    "route_id": str(action["route_id"]),
                    "route_name": str(action["route_name"]),
                    "target": str(rec["target"]),
                    "target_index": target_idx,
                    "flat_index": int(rec["flat_index"]),
                    "value_mode": str(action["value_mode"]),
                    "applied_logit_move": float(move[idx]),
                    "old_prob": old,
                    "new_prob": new,
                    "prob_delta": new - old,
                    "h095_q": float(rec["h085_q"]),
                    "q_hard": float(rec["q_hard"]),
                    "source_mean_move": float(rec["source_mean_move"]),
                    "source_action_delta": float(rec["source_action_delta"]),
                    "h088_toxicity": float(rec["h088_toxicity"]),
                    "h088_logit_move": float(rec["h088_logit_move"]),
                    "h057_positive_weight": float(rec["h057_positive_weight"]),
                    "h057_positive_logit_move": float(rec["h057_positive_logit_move"]),
                    "h095_safe_cell_score": float(rec["h095_safe_cell_score"]),
                    "h082_cell": float(rec["h082_cell"]),
                    "h086_resp_weight": float(rec["h086_resp_weight"]),
                    "h080_bad_same_rank": float(rec["h080_bad_same_rank"]),
                    "h095_action_score": float(action["h095_action_score"]),
                    "toxicity_sum": float(action["toxicity_sum"]),
                    "h057_positive_sum": float(action["h057_positive_sum"]),
                }
            )
    return clip_prob(prob), pd.DataFrame(selected_cells)


def bad_anchor_cosines(delta: np.ndarray, sample: pd.DataFrame, base_prob: np.ndarray) -> dict[str, float]:
    return h087mod.bad_anchor_cosines(delta, sample, base_prob)


def evaluate_candidate(
    candidate_id: str,
    prob: np.ndarray,
    base_prob: np.ndarray,
    selected_actions: pd.DataFrame,
    selected_cells: pd.DataFrame,
    cell: pd.DataFrame,
    sample: pd.DataFrame,
    spec: H095Spec,
    path: Path,
) -> dict[str, object]:
    ordered = cell.sort_values("flat_index")
    q095 = ordered["h085_q"].to_numpy(dtype=np.float64).reshape(base_prob.shape)
    qhard = ordered["q_hard"].to_numpy(dtype=np.float64).reshape(base_prob.shape)
    resp = ordered["h086_resp_weight"].to_numpy(dtype=np.float64).reshape(base_prob.shape)
    diff = np.abs(prob - base_prob) > TOL
    posterior_delta = float((bce(prob, q095) - bce(base_prob, q095)).mean())
    hard_delta = float((bce(prob, qhard) - bce(base_prob, qhard)).mean())
    resp_delta = float(((bce(prob, q095) - bce(base_prob, q095)) * resp).sum())

    if selected_cells.empty:
        toxic_mean = 0.0
        toxic_same_rate = 0.0
        h057_pos_mean = 0.0
        h057_pos_align_rate = 0.0
        source_proxy = 0.0
        source_agree_rate = 0.0
        safe_cell_mean = 0.0
        mean_bad_same = 0.0
        h082_ratio = 0.0
        route_templates = ""
    else:
        move = selected_cells["applied_logit_move"].to_numpy(dtype=np.float64)
        source = selected_cells["source_mean_move"].to_numpy(dtype=np.float64)
        source_delta = selected_cells["source_action_delta"].to_numpy(dtype=np.float64)
        ratio = np.minimum(np.abs(move) / (np.abs(source) + 1.0e-6), 2.5)
        agree = (np.sign(move) * np.sign(source) > 0).astype(float)
        proxy = np.where(agree > 0, source_delta * ratio, np.abs(source_delta) * ratio)
        proxy = np.where(np.abs(source) > 1.0e-10, proxy, 0.0)
        source_proxy = float(proxy.sum() / base_prob.size)
        source_agree_rate = float(agree.mean())

        h088_move = selected_cells["h088_logit_move"].to_numpy(dtype=np.float64)
        toxic_same = (np.sign(move) * np.sign(h088_move) > 0).astype(float) * (np.abs(h088_move) > 1.0e-10)
        pos_move = selected_cells["h057_positive_logit_move"].to_numpy(dtype=np.float64)
        pos_align = (np.sign(move) * np.sign(pos_move) > 0).astype(float) * (
            selected_cells["h057_positive_weight"].to_numpy(dtype=np.float64) > 0
        )
        toxic_mean = float(selected_cells["h088_toxicity"].mean())
        toxic_same_rate = float(toxic_same.mean())
        h057_pos_mean = float(selected_cells["h057_positive_weight"].mean())
        h057_pos_align_rate = float(pos_align.mean())
        safe_cell_mean = float(selected_cells["h095_safe_cell_score"].mean())
        mean_bad_same = float(selected_cells["h080_bad_same_rank"].mean())
        h082_ratio = float(selected_cells["h082_cell"].mean())
        route_templates = ";".join(
            f"{k}:{v}" for k, v in selected_actions["route_name"].value_counts().sort_index().items()
        )

    per_target = {
        f"{target}_changed_vs_h057": int(diff[:, i].sum())
        for i, target in enumerate(TARGETS)
    }
    bad_cos = bad_anchor_cosines(prob - base_prob, sample, base_prob)
    max_positive_bad = max([0.0] + [v for v in bad_cos.values() if v > 0])
    validation = h085mod.validate_submission(path, sample, base_prob)

    scale = len(selected_cells) / base_prob.size if base_prob.size else 0.0
    h095_score = (
        470.0 * (-posterior_delta)
        + 160.0 * (-source_proxy)
        + 80.0 * (-resp_delta)
        + 0.18 * safe_cell_mean
        + 0.12 * h057_pos_align_rate
        + 0.10 * h082_ratio
        + 0.08 * min(scale / 0.55, 1.0)
        - 0.62 * toxic_mean
        - 0.22 * toxic_same_rate
        - 0.16 * max(mean_bad_same - 0.58, 0.0)
        - 0.35 * max_positive_bad
        - 30.0 * max(hard_delta, 0.0)
    )

    out: dict[str, object] = {
        "candidate_id": candidate_id,
        "spec_name": spec.name,
        "target_group": spec.target_group,
        "value_modes": ",".join(spec.value_modes),
        "worldview": spec.worldview,
        "alpha": spec.alpha,
        "cap": spec.cap,
        "selected_routes": int(len(selected_actions)),
        "selected_cells": int(len(selected_cells)),
        "changed_cells_vs_h057": int(diff.sum()),
        "changed_rows_vs_h057": int(diff.any(axis=1).sum()),
        "q2_cells": int(per_target.get("Q2_changed_vs_h057", 0)),
        "posterior_delta_vs_h057": posterior_delta,
        "hard_diag_delta_vs_h057": hard_delta,
        "source_proxy_delta_vs_h057": source_proxy,
        "responsibility_weighted_delta_vs_h057": resp_delta,
        "toxic_mean_selected": toxic_mean,
        "toxic_same_direction_rate": toxic_same_rate,
        "h057_positive_mean_selected": h057_pos_mean,
        "h057_positive_align_rate": h057_pos_align_rate,
        "mean_h095_safe_cell_score": safe_cell_mean,
        "source_agree_rate": source_agree_rate,
        "h082_ratio": h082_ratio,
        "mean_bad_same_rank": mean_bad_same,
        "max_positive_bad_cosine": float(max_positive_bad),
        "mean_abs_prob_move_vs_h057": float(np.abs(prob - base_prob).mean()),
        "max_abs_prob_move_vs_h057": float(np.abs(prob - base_prob).max()),
        "selected_subjects": int(selected_actions["subject_id"].nunique()) if not selected_actions.empty else 0,
        "selected_rows": ",".join(map(str, sorted(selected_actions["row"].astype(int).tolist()))) if not selected_actions.empty else "",
        "route_templates": route_templates,
        "h095_score": h095_score,
        "file": path.name,
        "resolved_path": str(path.resolve()),
    }
    out.update(per_target)
    out.update(bad_cos)
    out.update(validation)
    return out


def run() -> None:
    cleanup_previous_outputs()
    base = h085mod.load_sub(BASE_FILE)
    sample = base[KEYS].copy()
    base_prob = base[TARGETS].to_numpy(dtype=np.float64)

    known, configs, cell, q_prob = build_h095_cell_table(sample, base_prob)
    route_actions = build_assignment_actions(cell)
    route_actions.to_csv(OUT / "h095_route_actions.csv", index=False)

    candidate_rows = []
    selected_action_frames = []
    selected_cell_frames = []
    for spec in candidate_specs():
        selected_actions = select_actions(route_actions, spec)
        if selected_actions.empty:
            continue
        prob, selected_cells = materialize_candidate(sample, base_prob, cell, selected_actions, spec)
        if int((np.abs(prob - base_prob) > TOL).sum()) == 0:
            continue
        hash_id = short_hash(prob)
        candidate_id = safe_id(f"h095_{spec.name}_{hash_id}", 128)
        path = OUT / f"submission_{candidate_id}.csv"
        h085mod.write_submission(sample, prob, path)
        metrics = evaluate_candidate(candidate_id, prob, base_prob, selected_actions, selected_cells, cell, sample, spec, path)
        candidate_rows.append(metrics)
        selected_actions = selected_actions.copy()
        selected_actions.insert(0, "candidate_id", candidate_id)
        selected_cells = selected_cells.copy()
        selected_cells.insert(0, "candidate_id", candidate_id)
        selected_action_frames.append(selected_actions)
        selected_cell_frames.append(selected_cells)

    candidates = pd.DataFrame(candidate_rows)
    if candidates.empty:
        raise RuntimeError("no H095 candidates")
    candidates = candidates.sort_values(["h095_score", "posterior_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True)

    selected = candidates.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"submission_h095_assignment_solver_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)
    decision = {
        "decision": "promote_h095_public_private_assignment_solver",
        "selected_candidate_id": selected["candidate_id"],
        "root_uploadsafe_path": str(root_path.resolve()),
        "worldview": selected["worldview"],
        "posterior_key": str(configs.iloc[0]["posterior_key"]),
        "posterior_loo_mae": float(configs.iloc[0]["loo_mae"]),
        **selected,
        **{f"root_{key}": value for key, value in validation.items()},
    }

    known.to_csv(OUT / "h095_known_public_observations.csv", index=False)
    configs.to_csv(OUT / "h095_posterior_configs.csv", index=False)
    candidates.to_csv(OUT / "h095_candidates.csv", index=False)
    pd.concat(selected_action_frames, ignore_index=True).to_csv(OUT / "h095_selected_route_actions.csv", index=False)
    pd.concat(selected_cell_frames, ignore_index=True).to_csv(OUT / "h095_selected_cells.csv", index=False)
    pd.DataFrame([decision]).to_csv(OUT / "h095_decision.csv", index=False)

    cols = [
        "candidate_id",
        "spec_name",
        "changed_cells_vs_h057",
        "changed_rows_vs_h057",
        "q2_cells",
        "posterior_delta_vs_h057",
        "hard_diag_delta_vs_h057",
        "source_proxy_delta_vs_h057",
        "toxic_mean_selected",
        "toxic_same_direction_rate",
        "h057_positive_align_rate",
        "mean_h095_safe_cell_score",
        "max_positive_bad_cosine",
        "h095_score",
        "file",
    ]
    route_cols = [
        "route_id",
        "row",
        "subject_id",
        "sleep_date",
        "route_name",
        "targets",
        "value_mode",
        "h095_action_score",
        "posterior_delta_sum",
        "source_proxy_sum",
        "toxicity_sum",
        "toxicity_mean",
        "h057_positive_sum",
        "h057_positive_opp_sum",
        "mean_h095_safe_cell",
        "mean_h088_toxicity",
        "mean_bad_same_rank",
    ]
    report = f"""# H095 Public/Private Assignment Equation Solver HS-JEPA

Question: can H057's positive row-state signal and H088's negative action
signal be explained by one row-target assignment equation?

Design:

- refit the H085 public equation after including H088 as a negative sensor;
- decode row-target route actions from the refit posterior;
- penalize actions whose direction matches H088's toxic direction;
- use H057-vs-H042/H050 as positive route compatibility, not as direct replay;
- keep H018 hard-world as a diagnostic stress head only.

Known public observations:

{md_table(known, 30)}

Posterior configs:

{md_table(configs.head(10), 10)}

Candidates:

{md_table(candidates[cols], 20)}

Top route actions:

{md_table(route_actions[route_cols].head(50), 50)}

Decision:

{md_table(pd.DataFrame([decision]), 1)}

Interpretation rule:

- If H095 beats H057, public/private action toxicity is the missing HS-JEPA
  decoder layer.
- If H095 is around H012 but below H057, toxicity separation is real but the
  assignment field is still too weak.
- If H095 loses like H088, H088 is not a localized toxic field; it is a broader
  public-subset/collapse diagnostic.
"""
    (OUT / "h095_report.md").write_text(report, encoding="utf-8")

    print(f"selected={decision['selected_candidate_id']}")
    print(f"root={root_path}")
    print(candidates[cols].head(8).to_string(index=False))


if __name__ == "__main__":
    run()
