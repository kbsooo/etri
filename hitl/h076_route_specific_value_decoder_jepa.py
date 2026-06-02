#!/usr/bin/env python3
"""H076: route-specific value decoder HS-JEPA.

H074 showed that known public-bad submissions define a real anti-shortcut
support representation. H075 then tested whether the inverse of those bad
submissions also provides the probability values, and it did not clear the
0.001 action gate.

H076 separates support from value:

    support = H074/H075 anti-shortcut route assignment
    value   = route-specific human-state decoder

This is a big-bet decoder test, not a top-k tweak. If it works, the bottleneck
after H057 is not "where to edit" but "which hidden route law should translate
the selected row-target state into probability movement."
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
OUT = HITL / "h076_route_specific_value_decoder_jepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
S_TARGETS = ["S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
TOL = 1.0e-12
EPS = 1.0e-9


def import_module(path: Path, name: str) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


H075MOD = import_module(HITL / "h075_antibad_transport_decoder_jepa.py", "h075mod_for_h076")
H074MOD = H075MOD.H074MOD
H071MOD = H075MOD.H071MOD


@dataclass(frozen=True)
class H076Spec:
    family: str
    policy: str
    max_cells: int
    max_rows: int
    q2_cap: int
    max_per_subject: int
    min_route_score: float
    min_cell_score: float
    novelty: str
    allowed_routes: tuple[str, ...]


POLICIES: dict[str, dict[str, tuple[str, float]]] = {
    "anti_shortcut_q061_baseline": {
        "default": ("q061", 1.00),
    },
    "q2_tail_stage_soft": {
        "default": ("q061_damp", 0.78),
        "q2_hardtail": ("soft_edge", 0.92),
        "q2_s3_tail": ("soft_edge", 0.88),
        "q_subjective": ("q061", 0.96),
        "q1q3_subjective": ("q061", 0.92),
        "s_stage": ("q061_damp", 0.72),
        "s23_core": ("q061_damp", 0.74),
        "s14_edge": ("q061_damp", 0.68),
        "q3_s_stage": ("q061", 0.90),
        "recovery_route": ("q061", 0.94),
    },
    "objective_stage_edge": {
        "default": ("q061_damp", 0.70),
        "s_stage": ("soft_edge", 0.84),
        "s23_core": ("soft_edge", 0.80),
        "s14_edge": ("soft_edge", 0.78),
        "q3_s_stage": ("q061_amp", 0.92),
        "recovery_route": ("q061_amp", 0.88),
        "nonq2_full": ("q061", 0.82),
        "q2_hardtail": ("q061_damp", 0.45),
        "q2_s3_tail": ("q061_damp", 0.52),
    },
    "recovery_full_vector": {
        "default": ("q061_damp", 0.70),
        "full_state": ("q061_amp", 0.90),
        "nonq2_full": ("q061", 0.95),
        "recovery_route": ("soft_edge", 0.86),
        "q3_s_stage": ("q061", 0.88),
        "s_stage": ("q061_damp", 0.78),
        "q_subjective": ("q061", 0.84),
        "q2_hardtail": ("h075_conservative", 0.82),
        "q2_s3_tail": ("h075_conservative", 0.82),
    },
    "public_private_value_gate": {
        "default": ("beta_gate", 1.00),
        "q2_hardtail": ("beta_gate", 1.10),
        "q2_s3_tail": ("beta_gate", 1.04),
        "s_stage": ("beta_gate", 0.96),
        "s23_core": ("beta_gate", 0.96),
        "s14_edge": ("beta_gate", 0.90),
        "q3_s_stage": ("beta_gate", 1.00),
        "full_state": ("beta_gate", 1.02),
        "nonq2_full": ("beta_gate", 1.00),
        "recovery_route": ("beta_gate", 0.98),
    },
    "public_private_edge_gate": {
        "default": ("beta_soft_edge", 0.92),
        "q2_hardtail": ("beta_soft_edge", 1.02),
        "q2_s3_tail": ("beta_soft_edge", 0.98),
        "s_stage": ("beta_soft_edge", 0.90),
        "s23_core": ("beta_soft_edge", 0.90),
        "s14_edge": ("beta_soft_edge", 0.86),
        "q3_s_stage": ("beta_soft_edge", 0.92),
        "recovery_route": ("beta_soft_edge", 0.92),
        "full_state": ("beta_soft_edge", 0.94),
    },
    "bad_safe_recovery": {
        "default": ("h075_conservative", 0.88),
        "q2_hardtail": ("h075_conservative", 0.78),
        "q2_s3_tail": ("h075_conservative", 0.78),
        "s_stage": ("q061", 0.82),
        "s23_core": ("q061", 0.84),
        "s14_edge": ("q061_damp", 0.72),
        "q3_s_stage": ("q061", 0.88),
        "recovery_route": ("q061_amp", 0.86),
        "full_state": ("q061", 0.84),
    },
}


def rank01(values: np.ndarray, high: bool = True) -> np.ndarray:
    return H071MOD.rank01(np.asarray(values, dtype=np.float64), high=high)


def logit(x: np.ndarray) -> np.ndarray:
    return H071MOD.logit(x)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return H071MOD.sigmoid(x)


def bce(prob: np.ndarray, q: np.ndarray) -> np.ndarray:
    return H071MOD.bce(prob, q)


def clip_prob(x: np.ndarray) -> np.ndarray:
    return H071MOD.clip_prob(x)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1.0e-12))


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return H071MOD.md_table(frame, n)


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h076_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h076_route_value_decoder_*_uploadsafe.csv"):
        path.unlink()


def policy_decoder(policy: str, route_name: str) -> tuple[str, float]:
    mapping = POLICIES[policy]
    return mapping.get(route_name, mapping["default"])


def decoder_delta(
    decoder: str,
    scale: float,
    flat: np.ndarray,
    cell_frame: pd.DataFrame,
    mats: dict[str, np.ndarray],
    beta: np.ndarray,
) -> np.ndarray:
    base_logit = logit(mats["h057"]).reshape(-1)
    q_logit = logit(mats["q061"]).reshape(-1)
    q_delta = q_logit[flat] - base_logit[flat]
    q_dir = np.sign(q_delta)
    q_dir = np.where(q_dir == 0.0, 1.0, q_dir)
    q_abs = np.abs(q_delta)

    if decoder == "q061":
        delta = q_delta
    elif decoder == "q061_damp":
        delta = 0.68 * q_delta
    elif decoder == "q061_amp":
        delta = 1.22 * q_delta
    elif decoder == "h075_conservative":
        delta = cell_frame["h075_conservative_delta"].to_numpy(dtype=np.float64)
    elif decoder == "h075_hybrid":
        delta = cell_frame["h075_hybrid_delta"].to_numpy(dtype=np.float64)
    elif decoder == "soft_edge":
        mag = np.minimum(np.maximum(1.15 * q_abs, 0.42), np.minimum(q_abs + 0.52, 1.95))
        delta = q_dir * mag
    elif decoder == "binary_soft":
        target_prob = np.where(q_dir > 0, 0.82, 0.18)
        delta = logit(target_prob) - base_logit[flat]
    elif decoder == "beta_gate":
        factor = np.where(beta[flat] > 0, 1.18, 0.18)
        delta = q_delta * factor
    elif decoder == "beta_soft_edge":
        mag = np.minimum(np.maximum(1.12 * q_abs, 0.38), np.minimum(q_abs + 0.48, 1.85))
        edge_delta = q_dir * mag
        delta = np.where(beta[flat] > 0, edge_delta, 0.16 * q_delta)
    else:
        raise ValueError(f"unknown H076 decoder: {decoder}")
    return np.asarray(delta, dtype=np.float64) * float(scale)


def augment_routes_for_policy(
    policy: str,
    routes: pd.DataFrame,
    cells_by_route: dict[str, pd.DataFrame],
    mats: dict[str, np.ndarray],
    beta: np.ndarray,
) -> tuple[pd.DataFrame, dict[str, pd.DataFrame], pd.DataFrame]:
    base_prob = mats["h057"].reshape(-1)
    q061 = mats["q061"].reshape(-1)
    base_logit = logit(mats["h057"]).reshape(-1)
    route_cell_frames = []

    for rec in routes.to_dict("records"):
        route_id = str(rec["route_id"])
        if route_id not in cells_by_route:
            continue
        use = cells_by_route[route_id].copy()
        if use.empty:
            continue
        route_name = str(rec["route_name"])
        flat = use["flat_index"].to_numpy(dtype=int)
        decoder, scale = policy_decoder(policy, route_name)
        delta = decoder_delta(decoder, scale, flat, use, mats, beta)
        new_prob = sigmoid(base_logit[flat] + delta)
        bce_delta = H071MOD.bce(new_prob, q061[flat]) - H071MOD.bce(base_prob[flat], q061[flat])
        use["route_id"] = route_id
        use["h076_policy"] = policy
        use["h076_decoder"] = decoder
        use["h076_decoder_scale"] = float(scale)
        use["h076_delta_logit"] = delta
        use["h076_new_prob"] = new_prob
        use["h076_bce_delta"] = bce_delta
        use["h076_value_gain"] = -bce_delta
        use["h076_public_contrib"] = bce_delta * beta[flat]
        use["h076_public_action_gain"] = -use["h076_public_contrib"].to_numpy(dtype=np.float64)
        route_cell_frames.append(use)

    all_cells = pd.concat(route_cell_frames, ignore_index=True)
    all_cells["h076_public_gain_rank"] = rank01(all_cells["h076_public_action_gain"].to_numpy())
    all_cells["h076_value_gain_rank"] = rank01(all_cells["h076_value_gain"].to_numpy())
    all_cells["h076_delta_abs_rank"] = rank01(np.abs(all_cells["h076_delta_logit"].to_numpy()))
    all_cells["h076_cell_score"] = (
        0.24 * all_cells["h076_public_gain_rank"]
        + 0.17 * all_cells["h076_value_gain_rank"]
        + 0.15 * rank01(all_cells["h074_cell_score"].to_numpy())
        + 0.12 * rank01(all_cells["h075_transport_cell_score"].to_numpy())
        + 0.09 * rank01(all_cells["h073_bridge_cell_score"].to_numpy())
        + 0.08 * rank01(all_cells["h068_cell_health"].to_numpy())
        + 0.06 * rank01(all_cells["public_score"].to_numpy())
        + 0.05 * rank01(all_cells["invariant_score"].to_numpy())
        + 0.04 * all_cells["outside_h069_cell"].to_numpy(dtype=float)
        - 0.12 * rank01(all_cells["h074_bad_same_rank"].to_numpy())
        - 0.10 * rank01(all_cells["latent_shortcut_energy"].to_numpy())
        - 0.07 * (all_cells["target"].astype(str) == "Q2").to_numpy(dtype=float)
        - 0.12 * all_cells["is_h050_null"].to_numpy(dtype=float)
    )
    all_cells.loc[all_cells["h076_value_gain"] <= 0, "h076_cell_score"] -= 0.80
    all_cells.loc[all_cells["h076_public_action_gain"] <= 0, "h076_cell_score"] -= 0.35
    all_cells.loc[all_cells["is_h050_null"] > 0, "h076_cell_score"] -= 0.35
    all_cells = all_cells.replace([np.inf, -np.inf], 0.0).fillna(0.0)

    out_cells = {rid: group.copy() for rid, group in all_cells.groupby("route_id", sort=False)}
    rows = []
    for rec in routes.to_dict("records"):
        route_id = str(rec["route_id"])
        if route_id not in out_cells:
            continue
        use = out_cells[route_id]
        rows.append(
            {
                **rec,
                "h076_policy": policy,
                "h076_decoder": str(use["h076_decoder"].iloc[0]),
                "h076_decoder_scale": float(use["h076_decoder_scale"].iloc[0]),
                "sum_h076_public_contrib": float(use["h076_public_contrib"].sum()),
                "sum_h076_value_gain": float(use["h076_value_gain"].sum()),
                "mean_h076_public_action_gain": float(use["h076_public_action_gain"].mean()),
                "mean_h076_value_gain": float(use["h076_value_gain"].mean()),
                "mean_h076_cell_score": float(use["h076_cell_score"].mean()),
                "mean_h076_public_gain_rank": float(use["h076_public_gain_rank"].mean()),
                "mean_h076_value_gain_rank": float(use["h076_value_gain_rank"].mean()),
                "mean_h076_delta_abs_rank": float(use["h076_delta_abs_rank"].mean()),
                "positive_public_cells": int((use["h076_public_action_gain"] > 0).sum()),
            }
        )
    out_routes = pd.DataFrame(rows)
    norm_public = -out_routes["sum_h076_public_contrib"].to_numpy(dtype=np.float64) / np.sqrt(
        out_routes["n_cells"].clip(lower=1).to_numpy(dtype=np.float64)
    )
    norm_value = out_routes["sum_h076_value_gain"].to_numpy(dtype=np.float64) / np.sqrt(
        out_routes["n_cells"].clip(lower=1).to_numpy(dtype=np.float64)
    )
    out_routes["h076_value_action_rank"] = rank01(norm_public)
    out_routes["h076_value_posterior_rank"] = rank01(norm_value)
    out_routes["h076_support_rank"] = (
        0.35 * rank01(out_routes["h074_route_score"].to_numpy())
        + 0.20 * rank01(out_routes["h075_route_score"].to_numpy())
        + 0.15 * rank01(out_routes["assignment_route_score"].to_numpy())
        + 0.12 * rank01(out_routes["mean_h074_bad_opp_rank"].to_numpy())
        + 0.08 * rank01(out_routes["outside_h069_cells"].to_numpy())
        - 0.10 * rank01(out_routes["mean_h074_bad_same_rank"].to_numpy())
    )
    out_routes["h076_route_score"] = (
        0.31 * out_routes["h076_value_action_rank"]
        + 0.17 * out_routes["h076_value_posterior_rank"]
        + 0.16 * out_routes["h076_support_rank"]
        + 0.11 * rank01(out_routes["mean_h076_cell_score"].to_numpy())
        + 0.08 * rank01(out_routes["mean_h076_public_gain_rank"].to_numpy())
        + 0.07 * rank01(out_routes["mean_h074_bad_opp_rank"].to_numpy())
        + 0.05 * rank01(out_routes["mean_h075_transport_alignment"].to_numpy())
        + 0.04 * rank01(out_routes["outside_h069_cells"].to_numpy())
        - 0.08 * rank01(out_routes["mean_h074_bad_same_rank"].to_numpy())
        - 0.07 * rank01(out_routes["mean_shortcut_energy"].to_numpy())
    )
    out_routes.loc[out_routes["sum_h076_public_contrib"] >= 0, "h076_route_score"] -= 0.22
    out_routes.loc[out_routes["sum_h076_value_gain"] <= 0, "h076_route_score"] -= 0.30
    out_routes.loc[out_routes["mean_h074_bad_same_rank"] > 0.70, "h076_route_score"] -= 0.08
    out_routes = out_routes.replace([np.inf, -np.inf], 0.0).fillna(0.0)
    out_routes = out_routes.sort_values(
        ["h076_route_score", "h076_value_action_rank", "h076_support_rank"],
        ascending=False,
    ).reset_index(drop=True)
    return out_routes, out_cells, all_cells


def route_sets() -> dict[str, tuple[str, ...]]:
    all_routes = tuple(H071MOD.ROUTES)
    stage_routes = ("s_stage", "s23_core", "s14_edge", "q3_s_stage", "recovery_route", "nonq2_full")
    q_routes = ("q2_hardtail", "q2_s3_tail", "q3_quality", "q_subjective", "q1q3_subjective")
    row_routes = ("full_state", "nonq2_full", "q3_s_stage", "s_stage", "recovery_route", "q_subjective")
    row_broad = (
        "full_state",
        "nonq2_full",
        "q3_s_stage",
        "s_stage",
        "recovery_route",
        "q_subjective",
        "q2_hardtail",
        "q2_s3_tail",
    )
    return {
        "all": all_routes,
        "stage": stage_routes,
        "q": q_routes,
        "row": row_routes,
        "row_broad": row_broad,
    }


def candidate_specs() -> list[H076Spec]:
    rs = route_sets()
    base = [
        ("route_value_big", 1040, 250, 95, 32, 0.52, 0.34, "value_action", rs["row_broad"]),
        ("route_value_big", 1040, 250, 95, 32, 0.46, 0.32, "outside_h069", rs["row_broad"]),
        ("fullstate_decoder", 920, 230, 64, 28, 0.52, 0.34, "anti_shortcut", rs["row"]),
        ("fullstate_decoder", 920, 230, 64, 28, 0.48, 0.32, "outside_h069", rs["row"]),
        ("objective_decoder", 760, 220, 0, 28, 0.54, 0.34, "value_action", rs["stage"]),
        ("objective_decoder", 760, 220, 0, 28, 0.50, 0.32, "outside_h069", rs["stage"]),
        ("q_route_decoder", 520, 210, 145, 26, 0.50, 0.33, "value_action", rs["q"]),
        ("q_route_decoder", 620, 220, 165, 28, 0.46, 0.31, "bad_opposition", rs["q"]),
        ("wide_assignment_decoder", 1160, 250, 105, 32, 0.48, 0.31, "value_action", rs["all"]),
    ]
    specs: list[H076Spec] = []
    for policy in POLICIES:
        for family, max_cells, max_rows, q2_cap, max_per_subject, min_route, min_cell, novelty, routes in base:
            if policy in {"objective_stage_edge"} and family == "q_route_decoder":
                continue
            if policy in {"q2_tail_stage_soft"} and family == "objective_decoder":
                continue
            specs.append(
                H076Spec(
                    family=family,
                    policy=policy,
                    max_cells=max_cells,
                    max_rows=max_rows,
                    q2_cap=q2_cap,
                    max_per_subject=max_per_subject,
                    min_route_score=min_route,
                    min_cell_score=min_cell,
                    novelty=novelty,
                    allowed_routes=routes,
                )
            )
    return specs


def allowed_by_spec(spec: H076Spec, rec: dict[str, object]) -> bool:
    if spec.allowed_routes and str(rec["route_name"]) not in spec.allowed_routes:
        return False
    if float(rec["h076_route_score"]) < spec.min_route_score:
        return False
    if spec.novelty == "outside_h069":
        return int(rec["outside_h069_cells"]) >= max(1, int(rec["n_cells"]) // 2)
    if spec.novelty == "bad_opposition":
        return float(rec["mean_h074_bad_opp_rank"]) >= 0.62 and float(rec["mean_h074_bad_same_rank"]) <= 0.58
    if spec.novelty == "anti_shortcut":
        return float(rec["mean_h074_bad_same_rank"]) <= 0.50 and float(rec["mean_shortcut_energy"]) <= 0.52
    if spec.novelty == "value_action":
        return float(rec["sum_h076_public_contrib"]) < 0 and float(rec["sum_h076_value_gain"]) > 0
    return True


def select_assignments(
    spec: H076Spec,
    routes: pd.DataFrame,
    cells_by_route: dict[str, pd.DataFrame],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    pool = routes[routes.apply(lambda row: allowed_by_spec(spec, row.to_dict()), axis=1)].copy()
    pool = pool.sort_values(["h076_route_score", "h076_value_action_rank", "h076_support_rank"], ascending=False)
    used_rows: set[int] = set()
    subject_counts: dict[str, int] = {}
    selected_routes = []
    selected_cells = []
    total_cells = 0
    q2_cells = 0
    for rec in pool.to_dict("records"):
        row = int(rec["row"])
        subject = str(rec["subject_id"])
        if row in used_rows:
            continue
        if len(used_rows) >= spec.max_rows:
            break
        if subject_counts.get(subject, 0) >= spec.max_per_subject:
            continue
        cells = cells_by_route[str(rec["route_id"])].copy()
        cells = cells[cells["h076_cell_score"] >= spec.min_cell_score]
        cells = cells[cells["h076_value_gain"] > 0]
        cells = cells[cells["h076_public_action_gain"] > 0]
        cells = cells[cells["cell_q061_gain"] > 0]
        cells = cells[cells["is_h050_null"] == 0]
        cells = cells[cells["h074_bad_same_rank"] <= 0.84]
        if spec.novelty == "bad_opposition":
            cells = cells[cells["h074_bad_opp_rank"] >= 0.52]
        if cells.empty:
            continue
        if total_cells + len(cells) > spec.max_cells:
            continue
        new_q2 = int((cells["target"] == "Q2").sum())
        if q2_cells + new_q2 > spec.q2_cap:
            continue
        selected_routes.append(pd.DataFrame([rec]))
        selected_cells.append(cells)
        used_rows.add(row)
        subject_counts[subject] = subject_counts.get(subject, 0) + 1
        total_cells += int(len(cells))
        q2_cells += new_q2
        if total_cells >= spec.max_cells * 0.96:
            break
    if not selected_routes:
        return pool.iloc[0:0].copy(), pool.iloc[0:0].copy()
    return pd.concat(selected_routes, ignore_index=True), pd.concat(selected_cells, ignore_index=True)


def apply_candidate(
    spec: H076Spec,
    sample: pd.DataFrame,
    mats: dict[str, np.ndarray],
    routes: pd.DataFrame,
    cells_by_route: dict[str, pd.DataFrame],
    beta: np.ndarray,
    bad_vecs: dict[str, np.ndarray],
) -> tuple[np.ndarray, dict[str, object]]:
    route_sel, cell_sel = select_assignments(spec, routes, cells_by_route)
    h057_prob = mats["h057"]
    q061 = mats["q061"]
    prob = h057_prob.copy()
    for rec in cell_sel.to_dict("records"):
        prob[int(rec["row"]), int(rec["target_index"])] = float(rec["h076_new_prob"])
    prob = clip_prob(prob)

    changed = np.abs(prob - h057_prob) > TOL
    x = (bce(prob, q061) - bce(h057_prob, q061)).reshape(-1)
    row_delta = (bce(prob, q061) - bce(h057_prob, q061)).mean(axis=1)
    row_public = (
        pd.read_csv(HITL / "h067_row_responsibility_public_state_jepa" / "h067_row_responsibility.csv")
        .sort_values("row")["public_weight"]
        .to_numpy(dtype=np.float64)
    )
    move_vec = (logit(prob) - logit(h057_prob)).reshape(-1)
    bad_cos = {f"bad_cos_{H074MOD.safe_stem(name)}": cosine(move_vec, vec) for name, vec in bad_vecs.items()}
    max_bad_cos = max([max(value, 0.0) for value in bad_cos.values()] + [0.0])
    route_counts = route_sel["route_name"].value_counts().to_dict() if len(route_sel) else {}
    decoder_counts = cell_sel["h076_decoder"].value_counts().to_dict() if len(cell_sel) else {}
    meta: dict[str, object] = {
        "candidate_id": "",
        "family": spec.family,
        "policy": spec.policy,
        "max_cells": spec.max_cells,
        "max_rows": spec.max_rows,
        "q2_cap": spec.q2_cap,
        "max_per_subject": spec.max_per_subject,
        "min_route_score": spec.min_route_score,
        "min_cell_score": spec.min_cell_score,
        "novelty": spec.novelty,
        "selected_routes": int(len(route_sel)),
        "selected_cells": int(len(cell_sel)),
        "changed_cells_vs_h057": int(changed.sum()),
        "changed_rows_vs_h057": int(changed.any(axis=1).sum()),
        "outside_h070_cells": int(cell_sel["outside_h070_cell"].sum()) if len(cell_sel) else 0,
        "outside_h069_cells": int(cell_sel["outside_h069_cell"].sum()) if len(cell_sel) else 0,
        "h071_route_overlap": int(route_sel.get("h071_selected_route", pd.Series(dtype=float)).sum()) if len(route_sel) else 0,
        "h070_overlap_cells": int(cell_sel["h070_selected_cell"].sum()) if len(cell_sel) else 0,
        "h069_overlap_cells": int(cell_sel["h069_selected_cell"].sum()) if len(cell_sel) else 0,
        "h068_overlap_cells": int(cell_sel["h068_selected_cell"].sum()) if len(cell_sel) else 0,
        "public_action_pred_delta_vs_h057": float(x @ beta),
        "posterior_delta_vs_h057": float(x.mean()),
        "responsibility_weighted_delta_vs_h057": float(np.dot(row_public, row_delta)),
        "max_positive_bad_cosine": max_bad_cos,
        "mean_h076_route_score": float(route_sel["h076_route_score"].mean()) if len(route_sel) else 0.0,
        "mean_h076_cell_score": float(cell_sel["h076_cell_score"].mean()) if len(cell_sel) else 0.0,
        "sum_h076_public_contrib": float(cell_sel["h076_public_contrib"].sum()) if len(cell_sel) else 0.0,
        "sum_h076_value_gain": float(cell_sel["h076_value_gain"].sum()) if len(cell_sel) else 0.0,
        "mean_h076_public_action_gain": float(cell_sel["h076_public_action_gain"].mean()) if len(cell_sel) else 0.0,
        "mean_h076_value_gain": float(cell_sel["h076_value_gain"].mean()) if len(cell_sel) else 0.0,
        "mean_h074_cell_score": float(cell_sel["h074_cell_score"].mean()) if len(cell_sel) else 0.0,
        "mean_h074_bad_opp_rank": float(cell_sel["h074_bad_opp_rank"].mean()) if len(cell_sel) else 0.0,
        "mean_h074_bad_same_rank": float(cell_sel["h074_bad_same_rank"].mean()) if len(cell_sel) else 1.0,
        "mean_h075_transport_alignment": float(cell_sel["h075_transport_alignment"].mean()) if len(cell_sel) else 0.0,
        "mean_h073_bridge_cell_score": float(cell_sel["h073_bridge_cell_score"].mean()) if len(cell_sel) else 0.0,
        "mean_h068_health": float(cell_sel["h068_cell_health"].mean()) if len(cell_sel) else 0.0,
        "mean_public_score": float(cell_sel["public_score"].mean()) if len(cell_sel) else 0.0,
        "mean_invariant_score": float(cell_sel["invariant_score"].mean()) if len(cell_sel) else 0.0,
        "mean_shortcut_energy": float(cell_sel["latent_shortcut_energy"].mean()) if len(cell_sel) else 1.0,
        "mean_abs_prob_move_vs_h057": float(np.abs(prob - h057_prob).mean()),
        "max_abs_prob_move_vs_h057": float(np.abs(prob - h057_prob).max()),
        "h050_null_selected": int(cell_sel["is_h050_null"].sum()) if len(cell_sel) else 0,
        "selected_subjects": int(cell_sel["subject_id"].nunique()) if len(cell_sel) else 0,
        "route_templates": ";".join(f"{k}:{v}" for k, v in sorted(route_counts.items())),
        "decoder_templates": ";".join(f"{k}:{v}" for k, v in sorted(decoder_counts.items())),
        **bad_cos,
    }
    for target in TARGETS:
        meta[f"{target}_changed_vs_h057"] = int(changed[:, TARGETS.index(target)].sum())
    return prob, meta


def candidate_sweep(
    sample: pd.DataFrame,
    mats: dict[str, np.ndarray],
    base_routes: pd.DataFrame,
    base_cells_by_route: dict[str, pd.DataFrame],
    beta: np.ndarray,
    bad_vecs: dict[str, np.ndarray],
) -> tuple[pd.DataFrame, dict[str, np.ndarray], pd.DataFrame, pd.DataFrame]:
    rows = []
    probs: dict[str, np.ndarray] = {}
    seen: set[str] = set()
    route_tables = []
    cell_tables = []
    policy_cache: dict[str, tuple[pd.DataFrame, dict[str, pd.DataFrame], pd.DataFrame]] = {}

    for spec in candidate_specs():
        if spec.policy not in policy_cache:
            policy_cache[spec.policy] = augment_routes_for_policy(
                spec.policy,
                base_routes,
                base_cells_by_route,
                mats,
                beta,
            )
            route_tables.append(policy_cache[spec.policy][0])
            cell_tables.append(policy_cache[spec.policy][2])
        routes, cells_by_route, _all_cells = policy_cache[spec.policy]
        prob, meta = apply_candidate(spec, sample, mats, routes, cells_by_route, beta, bad_vecs)
        if meta["changed_cells_vs_h057"] < 180 or meta["selected_routes"] < 25:
            continue
        digest = short_hash(prob)
        if digest in seen:
            continue
        seen.add(digest)
        cid = (
            f"h076_{spec.family}_{spec.policy}_{spec.novelty}_"
            f"c{spec.max_cells}_r{spec.max_rows}_q2{spec.q2_cap}_{digest}"
        )
        meta["candidate_id"] = cid
        meta["hash"] = digest
        rows.append(meta)
        probs[cid] = prob

    cand = pd.DataFrame(rows)
    if cand.empty:
        raise RuntimeError("no H076 candidates generated")
    cand["action_rank"] = rank01(-cand["public_action_pred_delta_vs_h057"].to_numpy())
    cand["posterior_rank"] = rank01(-cand["posterior_delta_vs_h057"].to_numpy())
    cand["responsibility_rank"] = rank01(-cand["responsibility_weighted_delta_vs_h057"].to_numpy())
    cand["route_rank"] = rank01(cand["mean_h076_route_score"].to_numpy())
    cand["cell_rank"] = rank01(cand["mean_h076_cell_score"].to_numpy())
    cand["public_gain_rank"] = rank01(cand["mean_h076_public_action_gain"].to_numpy())
    cand["value_gain_rank"] = rank01(cand["mean_h076_value_gain"].to_numpy())
    cand["opp_rank"] = rank01(cand["mean_h074_bad_opp_rank"].to_numpy())
    cand["same_avoid_rank"] = rank01(-cand["mean_h074_bad_same_rank"].to_numpy())
    cand["shortcut_avoid_rank"] = rank01(-cand["mean_shortcut_energy"].to_numpy())
    cand["bad_avoid_rank"] = rank01(-cand["max_positive_bad_cosine"].to_numpy())
    cand["outside_h069_ratio"] = cand["outside_h069_cells"] / cand["changed_cells_vs_h057"].clip(lower=1)
    cand["q2_risk"] = cand["Q2_changed_vs_h057"] / cand["changed_cells_vs_h057"].clip(lower=1)
    cand["route_diversity"] = cand["route_templates"].map(lambda text: len(str(text).split(";")) if text else 0)
    cand["bigbet_scale_score"] = ((-cand["public_action_pred_delta_vs_h057"] - 0.00100) / 0.00160).clip(0.0, 1.0)
    cand["h076_score"] = (
        0.20 * cand["action_rank"]
        + 0.13 * cand["responsibility_rank"]
        + 0.12 * cand["route_rank"]
        + 0.10 * cand["cell_rank"]
        + 0.10 * cand["public_gain_rank"]
        + 0.09 * cand["value_gain_rank"]
        + 0.07 * cand["opp_rank"]
        + 0.06 * cand["same_avoid_rank"]
        + 0.05 * cand["outside_h069_ratio"].clip(0, 1)
        + 0.04 * cand["bigbet_scale_score"]
        + 0.04 * cand["posterior_rank"]
        + 0.03 * cand["shortcut_avoid_rank"]
        + 0.03 * cand["bad_avoid_rank"]
        + 0.02 * (cand["route_diversity"] / cand["route_diversity"].clip(lower=1).max()).clip(0, 1)
        - 0.05 * cand["q2_risk"]
        - 0.07 * (cand["h050_null_selected"] > 0).astype(float)
        - 0.05 * (cand["max_abs_prob_move_vs_h057"] > 0.25).astype(float)
    )
    cand = cand.sort_values(["h076_score", "public_action_pred_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True)
    for _, rec in cand.head(120).iterrows():
        cid = str(rec["candidate_id"])
        path = OUT / f"submission_{cid}.csv"
        H071MOD.write_submission(sample, probs[cid], path)
        cand.loc[cand["candidate_id"].eq(cid), "file"] = path.name
        cand.loc[cand["candidate_id"].eq(cid), "resolved_path"] = str(path.resolve())

    all_routes = pd.concat(route_tables, ignore_index=True)
    all_cells = pd.concat(cell_tables, ignore_index=True)
    return cand, probs, all_routes, all_cells


def validate_submission(path: Path, sample: pd.DataFrame, h057_prob: np.ndarray) -> dict[str, object]:
    return H071MOD.validate_submission(path, sample, h057_prob)


def write_report(
    routes: pd.DataFrame,
    cells: pd.DataFrame,
    cand: pd.DataFrame,
    decision: pd.DataFrame,
) -> None:
    report = "\n".join(
        [
            "# H076 Route-Specific Value Decoder HS-JEPA",
            "",
            "Question: is the post-H057 bottleneck value translation rather than support discovery?",
            "",
            "Design:",
            "",
            "- support: H074 anti-shortcut + H075 route assignment;",
            "- value: route-specific human-state decoders, not a single global q061 or inverse-bad movement;",
            "- public/private stress: cell action gain from the refit public-action sensor plus bad-anchor cosine;",
            "- decision gate: candidates must be upload-safe, H050-null-free, and negative under the public-action model.",
            "",
            "Top route-policy rows:",
            "",
            md_table(
                routes[
                    [
                        "h076_policy",
                        "route_id",
                        "row",
                        "route_name",
                        "n_cells",
                        "h076_decoder",
                        "h076_route_score",
                        "sum_h076_public_contrib",
                        "sum_h076_value_gain",
                        "mean_h074_bad_opp_rank",
                        "mean_h074_bad_same_rank",
                        "outside_h069_cells",
                    ]
                ].sort_values("h076_route_score", ascending=False),
                40,
            ),
            "",
            "Policy cell summary:",
            "",
            md_table(
                cells.groupby(["h076_policy", "h076_decoder"], as_index=False)
                .agg(
                    route_cell_instances=("flat_index", "size"),
                    mean_public_action_gain=("h076_public_action_gain", "mean"),
                    mean_value_gain=("h076_value_gain", "mean"),
                    mean_cell_score=("h076_cell_score", "mean"),
                )
                .sort_values("mean_public_action_gain", ascending=False),
                40,
            ),
            "",
            "Top candidates:",
            "",
            md_table(cand.head(50), 50),
            "",
            "Decision:",
            "",
            md_table(decision),
            "",
            "Interpretation rule:",
            "",
            "- If H076 wins by >= 0.001, route-specific value translation is a real HS-JEPA decoder layer.",
            "- If H076 is neutral while H074/H075 support remains coherent, support discovery is not enough and value must be learned from another target representation.",
            "- If public-private gate candidates win but non-gated route policies fail, the hidden law is probably public-subset factorization rather than human route semantics.",
            "",
        ]
    )
    (OUT / "h076_report.md").write_text(report)


def main() -> None:
    cleanup_previous_outputs()
    sample, base_cells, base_routes, base_cells_by_route, mats, beta, bad_vecs = H075MOD.load_h074_runtime()
    cand, probs, all_routes, all_cells = candidate_sweep(
        sample,
        mats,
        base_routes,
        base_cells_by_route,
        beta,
        bad_vecs,
    )

    bigbet = cand[
        (cand["max_positive_bad_cosine"] <= 0.0)
        & (cand["h050_null_selected"] == 0)
        & (cand["public_action_pred_delta_vs_h057"] <= -0.00115)
        & (cand["responsibility_weighted_delta_vs_h057"] <= -0.00085)
        & (cand["changed_cells_vs_h057"] >= 520)
        & (cand["sum_h076_value_gain"] > 0)
        & (cand["max_abs_prob_move_vs_h057"] <= 0.25)
    ].sort_values(["public_action_pred_delta_vs_h057", "h076_score"], ascending=[True, False])

    if len(bigbet):
        selected = bigbet.iloc[0].copy()
        decision_name = "promote_route_value_decoder_bigbet"
        worldview = "support is known, and route-specific value translation is action-grade"
    else:
        sensor = cand[
            (cand["max_positive_bad_cosine"] <= 0.0)
            & (cand["h050_null_selected"] == 0)
            & (cand["public_action_pred_delta_vs_h057"] <= -0.00090)
            & (cand["changed_cells_vs_h057"] >= 450)
            & (cand["sum_h076_value_gain"] > 0)
            & (cand["max_abs_prob_move_vs_h057"] <= 0.28)
        ].sort_values(["public_action_pred_delta_vs_h057", "h076_score"], ascending=[True, False])
        if len(sensor):
            selected = sensor.iloc[0].copy()
            decision_name = "promote_route_value_decoder_sensor"
            worldview = "route-specific value translation improves the sensor but does not clear the big-bet action gate"
        else:
            selected = cand.iloc[0].copy()
            decision_name = "promote_route_value_decoder_diagnostic"
            worldview = "route-specific value translation is diagnostic only; support-value separation remains unresolved"

    selected_file = OUT / str(selected["file"])
    digest = str(selected["hash"])
    root_file = ROOT / f"submission_h076_route_value_decoder_{digest}_uploadsafe.csv"
    shutil.copyfile(selected_file, root_file)
    validation = validate_submission(root_file, sample, mats["h057"])
    if not validation["upload_safe"]:
        raise RuntimeError(f"selected submission is not upload safe: {validation}")

    decision = pd.DataFrame(
        [
            {
                "decision": decision_name,
                "selected_candidate_id": str(selected["candidate_id"]),
                "selected_file": str(selected["file"]),
                "selected_resolved_path": str(selected["resolved_path"]),
                "root_uploadsafe_path": str(root_file.resolve()),
                "worldview": worldview,
                **selected.to_dict(),
                **validation,
            }
        ]
    )

    base_cells.to_csv(OUT / "h076_base_h075_cell_scores.csv", index=False)
    all_cells.to_csv(OUT / "h076_policy_cell_scores.csv", index=False)
    all_routes.to_csv(OUT / "h076_policy_route_candidates.csv", index=False)
    cand.to_csv(OUT / "h076_candidate_scores.csv", index=False)
    decision.to_csv(OUT / "h076_decision.csv", index=False)
    write_report(all_routes, all_cells, cand, decision)
    print(
        decision[
            [
                "selected_candidate_id",
                "root_uploadsafe_path",
                "decision",
                "policy",
                "changed_cells_vs_h057",
                "changed_rows_vs_h057",
                "selected_routes",
                "outside_h069_cells",
                "Q2_changed_vs_h057",
                "public_action_pred_delta_vs_h057",
                "posterior_delta_vs_h057",
                "responsibility_weighted_delta_vs_h057",
                "max_abs_prob_move_vs_h057",
                "route_templates",
                "decoder_templates",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
