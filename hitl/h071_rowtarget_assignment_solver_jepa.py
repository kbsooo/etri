#!/usr/bin/env python3
"""H071: discrete row-target assignment solver HS-JEPA.

H070 proved that a smooth HS-JEPA latent can predict hidden public/action
representations, but it still behaved like a top-score selector. H071 changes
the action unit again:

    row context -> route template assignment -> row-target correction support

Each row can receive one discrete target route such as S-stage, full non-Q2,
Q2/S3 hardtail, Q+objective, or full-state. The solver then selects a support
set of route assignments under target, subject, shortcut, and action-health
constraints.

This tests the current bottleneck directly: if the true hidden law is exact
row-target placement, a continuous latent score is the wrong final decoder.
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
OUT = HITL / "h071_rowtarget_assignment_solver_jepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
S_TARGETS = ["S1", "S2", "S3", "S4"]
NON_Q2 = [target for target in TARGETS if target != "Q2"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1.0e-6
TOL = 1.0e-12

H057 = "submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv"
H070_ROOT = "submission_h070_full_hsjepa_9e4a9602_uploadsafe.csv"

BAD_ANCHORS = [
    "submission_h010_objective_s1s4_v2_uploadsafe.csv",
    "submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv",
    "submission_e323_5508f966_uploadsafe.csv",
    "gpt_pro_pack/q2s1_hidden_state_translation/submissions/submission_e323_5508f966_uploadsafe.csv",
    "jepa/submission_jepa_latent_q2_w0p45.csv",
    "jepa/submission_jepa_latent_residual_probe.csv",
    "jepa/submission_lejepa_targetwise_strict_best_scale0p5.csv",
    "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv",
]


@dataclass(frozen=True)
class AssignmentSpec:
    family: str
    max_cells: int
    max_rows: int
    q2_cap: int
    max_per_subject: int
    min_route_score: float
    min_cell_score: float
    novelty: str
    alpha: float
    mode: str


def import_module(path: Path, name: str) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


H070MOD = import_module(HITL / "h070_full_hsjepa_joint_decoder.py", "h070mod_for_h071")
H069MOD = H070MOD.H069MOD


def locate(name: str | Path) -> Path | None:
    return H070MOD.locate(name)


def load_sub(name: str | Path, sample: pd.DataFrame | None = None) -> pd.DataFrame:
    return H070MOD.load_sub(name, sample)


def clip_prob(x: np.ndarray) -> np.ndarray:
    return H070MOD.clip_prob(x)


def logit(x: np.ndarray) -> np.ndarray:
    return H070MOD.logit(x)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return H070MOD.sigmoid(x)


def bce(prob: np.ndarray, q: np.ndarray) -> np.ndarray:
    return H070MOD.bce(prob, q)


def rank01(values: np.ndarray, high: bool = True) -> np.ndarray:
    return H070MOD.rank01(values, high)


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return H070MOD.md_table(frame, n)


def write_submission(sample: pd.DataFrame, prob: np.ndarray, path: Path) -> None:
    H070MOD.write_submission(sample, prob, path)


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def move_toward(base: np.ndarray, target: np.ndarray, alpha: float, mode: str) -> np.ndarray:
    return H070MOD.move_toward(base, target, alpha, mode)


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h071_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h071_rowtarget_assignment_*_uploadsafe.csv"):
        path.unlink()


def as_prob_matrix(name: str, sample: pd.DataFrame) -> np.ndarray | None:
    path = locate(name)
    if path is None:
        return None
    try:
        return load_sub(path, sample)[TARGETS].to_numpy(dtype=np.float64)
    except Exception:
        return None


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1.0e-12))


def load_runtime() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, np.ndarray], np.ndarray, dict[str, np.ndarray]]:
    sample, _factors, mats = H070MOD.load_base_frames()
    latent = pd.read_csv(HITL / "h070_full_hsjepa_joint_decoder" / "h070_latent_table.csv")
    latent = latent.sort_values(["row", "target_index"]).reset_index(drop=True)
    h070 = as_prob_matrix(H070_ROOT, sample)
    if h070 is None:
        raise FileNotFoundError(H070_ROOT)
    latent["h070_selected_cell"] = (np.abs(h070 - mats["h057"]) > TOL).reshape(-1).astype(float)
    latent["outside_h070_cell"] = 1.0 - latent["h070_selected_cell"]
    beta, _fit, _model_table = H069MOD.refit_h068_beta(sample, mats["h057"], mats["q061"])
    bad_vecs: dict[str, np.ndarray] = {}
    for name in BAD_ANCHORS:
        prob = as_prob_matrix(name, sample)
        if prob is not None:
            bad_vecs[name] = (logit(prob) - logit(mats["h057"])).reshape(-1)
    return sample, latent.fillna(0.0), mats, beta, bad_vecs


ROUTES: dict[str, tuple[str, ...]] = {
    "q2_hardtail": ("Q2",),
    "q3_quality": ("Q3",),
    "q_subjective": ("Q1", "Q2", "Q3"),
    "q1q3_subjective": ("Q1", "Q3"),
    "s_stage": ("S1", "S2", "S3", "S4"),
    "s23_core": ("S2", "S3"),
    "s14_edge": ("S1", "S4"),
    "q3_s_stage": ("Q3", "S1", "S2", "S3", "S4"),
    "q2_s3_tail": ("Q2", "S3"),
    "recovery_route": ("Q1", "S2", "S3", "S4"),
    "nonq2_full": ("Q1", "Q3", "S1", "S2", "S3", "S4"),
    "full_state": ("Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"),
}

FAMILY_ROUTES: dict[str, tuple[str, ...]] = {
    "assignment_core": tuple(ROUTES),
    "assignment_big": tuple(ROUTES),
    "outside_h070": tuple(ROUTES),
    "objective_state": ("s_stage", "s23_core", "s14_edge", "q3_s_stage", "recovery_route", "nonq2_full"),
    "q_route": ("q2_hardtail", "q3_quality", "q_subjective", "q1q3_subjective", "q2_s3_tail"),
    "rowvector_state": ("q_subjective", "q3_s_stage", "nonq2_full", "full_state"),
    "anti_shortcut_assignment": tuple(ROUTES),
}


def add_cell_scores(latent: pd.DataFrame) -> pd.DataFrame:
    out = latent.copy()
    out["score_latent_rank"] = rank01(out["latent_hsjepa_score"].to_numpy())
    out["score_context_rank"] = rank01(out["latent_context_energy"].to_numpy())
    out["score_action_rank"] = rank01(out["h068_cell_health"].to_numpy())
    out["score_public_rank"] = rank01(out["public_score"].to_numpy())
    out["score_private_rank"] = rank01(out["private_safe_score"].to_numpy())
    out["score_invariant_rank"] = rank01(out["invariant_score"].to_numpy())
    out["score_gain_rank"] = rank01(out["cell_q061_gain"].to_numpy())
    out["score_shortcut_rank"] = rank01(out["latent_shortcut_energy"].to_numpy())
    out["score_bad_rank"] = rank01(out["bad_pressure_rank"].to_numpy())
    out["target_q2_penalty"] = (out["target"] == "Q2").astype(float)
    out["target_s_bonus"] = out["target"].isin(S_TARGETS).astype(float)
    out["cell_assignment_score"] = (
        0.20 * out["score_latent_rank"]
        + 0.15 * out["score_context_rank"]
        + 0.15 * out["score_action_rank"]
        + 0.13 * out["score_public_rank"]
        + 0.12 * out["score_private_rank"]
        + 0.10 * out["score_invariant_rank"]
        + 0.08 * out["score_gain_rank"]
        + 0.05 * out["outside_h070_cell"]
        + 0.04 * out["outside_h069_cell"]
        + 0.03 * out["target_s_bonus"]
        - 0.17 * out["score_shortcut_rank"]
        - 0.13 * out["score_bad_rank"]
        - 0.10 * out["is_h050_null"].astype(float)
        - 0.05 * out["target_q2_penalty"]
    )
    out.loc[out["cell_q061_gain"] <= 0, "cell_assignment_score"] -= 0.80
    out.loc[out["is_h050_null"] > 0, "cell_assignment_score"] -= 0.40
    return out


def route_coherence(cells: pd.DataFrame, route_name: str) -> float:
    direction = cells["direction_to_q061"].to_numpy(dtype=float)
    if len(direction) <= 1:
        direction_consistency = 0.5
    else:
        direction_consistency = max(float((direction > 0).mean()), float((direction < 0).mean()))
    story_direct = float(cells["story_route_direct"].mean()) if "story_route_direct" in cells else 0.5
    low_shortcut = 1.0 - float(cells["latent_shortcut_energy"].mean())
    route_bonus = {
        "s_stage": 0.08,
        "q3_s_stage": 0.05,
        "nonq2_full": 0.04,
        "full_state": -0.02,
        "q2_hardtail": -0.03,
        "q2_s3_tail": 0.00,
    }.get(route_name, 0.02)
    return 0.20 * direction_consistency + 0.14 * story_direct + 0.16 * low_shortcut + route_bonus


def build_route_candidates(latent: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    scored = add_cell_scores(latent)
    rows = []
    cells_by_route: dict[str, pd.DataFrame] = {}
    target_to_ix = {target: i for i, target in enumerate(TARGETS)}
    for row, group in scored.groupby("row", sort=True):
        group = group.sort_values("target_index")
        for route_name, targets in ROUTES.items():
            use = group[group["target"].isin(targets)].copy()
            use = use[(use["cell_q061_gain"] > 0) & (use["is_h050_null"] == 0)]
            if use.empty:
                continue
            route_id = f"r{int(row):03d}_{route_name}"
            q2_cells = int((use["target"] == "Q2").sum())
            route_targets = tuple(str(t) for t in use["target"].tolist())
            route_score_sum = float(use["cell_assignment_score"].sum())
            route_score_mean = float(use["cell_assignment_score"].mean())
            route_score = (
                route_score_sum / np.sqrt(len(use))
                + route_coherence(use, route_name)
                + 0.18 * float(use["public_score"].mean())
                + 0.12 * float(use["invariant_score"].mean())
                - 0.18 * float(use["shortcut_score"].mean())
            )
            if route_name == "full_state" and len(use) < 5:
                route_score -= 0.40
            if route_name in {"q2_hardtail", "q2_s3_tail"}:
                route_score -= 0.06 * q2_cells
            rows.append(
                {
                    "route_id": route_id,
                    "row": int(row),
                    "subject_id": str(use.iloc[0]["subject_id"]),
                    "sleep_date": str(use.iloc[0]["sleep_date"]),
                    "route_name": route_name,
                    "targets": ",".join(route_targets),
                    "n_cells": int(len(use)),
                    "q2_cells": q2_cells,
                    "s_cells": int(use["target"].isin(S_TARGETS).sum()),
                    "route_score": route_score,
                    "route_score_sum": route_score_sum,
                    "route_score_mean": route_score_mean,
                    "mean_latent_hsjepa_score": float(use["latent_hsjepa_score"].mean()),
                    "mean_context_energy": float(use["latent_context_energy"].mean()),
                    "mean_shortcut_energy": float(use["latent_shortcut_energy"].mean()),
                    "mean_public_score": float(use["public_score"].mean()),
                    "mean_invariant_score": float(use["invariant_score"].mean()),
                    "mean_cell_gain": float(use["cell_q061_gain"].mean()),
                    "sum_cell_gain": float(use["cell_q061_gain"].sum()),
                    "outside_h070_cells": int(use["outside_h070_cell"].sum()),
                    "outside_h069_cells": int(use["outside_h069_cell"].sum()),
                    "h068_overlap_cells": int(use["h068_selected_cell"].sum()),
                    "h069_overlap_cells": int(use["h069_selected_cell"].sum()),
                    "target_mask": "".join("1" if target in route_targets else "0" for target in TARGETS),
                    "target_indices": ",".join(str(target_to_ix[t]) for t in route_targets),
                }
            )
            cells_by_route[route_id] = use
    route_df = pd.DataFrame(rows)
    route_df["route_rank"] = rank01(route_df["route_score"].to_numpy())
    route_df["novelty_rank"] = rank01(route_df["outside_h070_cells"].to_numpy() + route_df["outside_h069_cells"].to_numpy())
    route_df["shortcut_avoid_rank"] = rank01(-route_df["mean_shortcut_energy"].to_numpy())
    route_df["assignment_route_score"] = (
        0.58 * route_df["route_rank"]
        + 0.16 * route_df["novelty_rank"]
        + 0.13 * route_df["shortcut_avoid_rank"]
        + 0.08 * rank01(route_df["sum_cell_gain"].to_numpy())
        + 0.05 * rank01(route_df["mean_public_score"].to_numpy())
    )
    return route_df.sort_values("assignment_route_score", ascending=False).reset_index(drop=True), cells_by_route


def spec_route_allowed(spec: AssignmentSpec, route_name: str) -> bool:
    return route_name in FAMILY_ROUTES[spec.family]


def select_assignments(
    spec: AssignmentSpec,
    routes: pd.DataFrame,
    cells_by_route: dict[str, pd.DataFrame],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    pool = routes[routes["route_name"].map(lambda name: spec_route_allowed(spec, str(name)))].copy()
    pool = pool[pool["assignment_route_score"] >= spec.min_route_score]
    if spec.novelty == "outside_h070":
        pool = pool[pool["outside_h070_cells"] >= np.maximum(1, pool["n_cells"] // 2)]
    elif spec.novelty == "outside_h069":
        pool = pool[pool["outside_h069_cells"] >= np.maximum(1, pool["n_cells"] // 2)]
    elif spec.novelty == "anti_shortcut":
        pool = pool[pool["mean_shortcut_energy"] <= 0.45]
    elif spec.novelty == "core":
        pool = pool[pool["mean_public_score"] >= 0.55]
    pool = pool.sort_values(["assignment_route_score", "route_score"], ascending=False)

    used_rows: set[int] = set()
    subject_counts: dict[str, int] = {}
    target_counts = {target: 0 for target in TARGETS}
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
        cells = cells[cells["cell_assignment_score"] >= spec.min_cell_score]
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
        for target in cells["target"].astype(str):
            target_counts[target] += 1
        if total_cells >= spec.max_cells * 0.96:
            break
    if not selected_routes:
        return pool.iloc[0:0].copy(), pool.iloc[0:0].copy()
    route_sel = pd.concat(selected_routes, ignore_index=True)
    cell_sel = pd.concat(selected_cells, ignore_index=True)
    return route_sel, cell_sel


def apply_candidate(
    spec: AssignmentSpec,
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
    moved = move_toward(h057_prob, q061, spec.alpha, spec.mode)
    for rec in cell_sel.to_dict("records"):
        prob[int(rec["row"]), int(rec["target_index"])] = moved[int(rec["row"]), int(rec["target_index"])]
    changed = np.abs(prob - h057_prob) > TOL
    x = (bce(prob, q061) - bce(h057_prob, q061)).reshape(-1)
    row_delta = (bce(prob, q061) - bce(h057_prob, q061)).mean(axis=1)
    row_public = (
        pd.read_csv(HITL / "h067_row_responsibility_public_state_jepa" / "h067_row_responsibility.csv")
        .sort_values("row")["public_weight"]
        .to_numpy(dtype=np.float64)
    )
    move_vec = (logit(prob) - logit(h057_prob)).reshape(-1)
    bad_cos = {f"bad_cos_{Path(name).stem[:18]}": cosine(move_vec, vec) for name, vec in bad_vecs.items()}
    max_bad_cos = max([max(value, 0.0) for value in bad_cos.values()] + [0.0])
    selected_rows = sorted(set(cell_sel["row"].astype(int).tolist())) if len(cell_sel) else []
    route_counts = route_sel["route_name"].value_counts().to_dict() if len(route_sel) else {}
    meta: dict[str, object] = {
        "candidate_id": "",
        "family": spec.family,
        "max_cells": spec.max_cells,
        "max_rows": spec.max_rows,
        "q2_cap": spec.q2_cap,
        "max_per_subject": spec.max_per_subject,
        "min_route_score": spec.min_route_score,
        "min_cell_score": spec.min_cell_score,
        "novelty": spec.novelty,
        "alpha": spec.alpha,
        "mode": spec.mode,
        "selected_routes": int(len(route_sel)),
        "selected_cells": int(len(cell_sel)),
        "changed_cells_vs_h057": int(changed.sum()),
        "changed_rows_vs_h057": int(changed.any(axis=1).sum()),
        "outside_h070_cells": int(cell_sel["outside_h070_cell"].sum()) if len(cell_sel) else 0,
        "outside_h069_cells": int(cell_sel["outside_h069_cell"].sum()) if len(cell_sel) else 0,
        "h070_overlap_cells": int(cell_sel["h070_selected_cell"].sum()) if len(cell_sel) else 0,
        "h069_overlap_cells": int(cell_sel["h069_selected_cell"].sum()) if len(cell_sel) else 0,
        "h068_overlap_cells": int(cell_sel["h068_selected_cell"].sum()) if len(cell_sel) else 0,
        "public_action_pred_delta_vs_h057": float(x @ beta),
        "posterior_delta_vs_h057": float(x.mean()),
        "responsibility_weighted_delta_vs_h057": float(np.dot(row_public, row_delta)),
        "max_positive_bad_cosine": max_bad_cos,
        "mean_assignment_route_score": float(route_sel["assignment_route_score"].mean()) if len(route_sel) else 0.0,
        "mean_route_score": float(route_sel["route_score"].mean()) if len(route_sel) else 0.0,
        "mean_cell_assignment_score": float(cell_sel["cell_assignment_score"].mean()) if len(cell_sel) else 0.0,
        "mean_latent_hsjepa_score": float(cell_sel["latent_hsjepa_score"].mean()) if len(cell_sel) else 0.0,
        "mean_latent_shortcut_energy": float(cell_sel["latent_shortcut_energy"].mean()) if len(cell_sel) else 1.0,
        "mean_public_score": float(cell_sel["public_score"].mean()) if len(cell_sel) else 0.0,
        "mean_invariant_score": float(cell_sel["invariant_score"].mean()) if len(cell_sel) else 0.0,
        "h050_null_selected": int(cell_sel["is_h050_null"].sum()) if len(cell_sel) else 0,
        "selected_subjects": int(cell_sel["subject_id"].nunique()) if len(cell_sel) else 0,
        "selected_rows": ",".join(map(str, selected_rows)),
        "route_templates": ";".join(f"{k}:{v}" for k, v in sorted(route_counts.items())),
        **bad_cos,
    }
    for target in TARGETS:
        meta[f"{target}_changed_vs_h057"] = int(changed[:, TARGETS.index(target)].sum())
    return clip_prob(prob), meta


def candidate_specs() -> list[AssignmentSpec]:
    specs = []
    for family in [
        "assignment_core",
        "assignment_big",
        "outside_h070",
        "objective_state",
        "q_route",
        "rowvector_state",
        "anti_shortcut_assignment",
    ]:
        if family in {"assignment_big", "rowvector_state"}:
            budgets = [680, 820]
            rows = [185, 210]
        elif family == "objective_state":
            budgets = [520, 700]
            rows = [170, 210]
        elif family == "q_route":
            budgets = [260, 420]
            rows = [150, 190]
        else:
            budgets = [480, 640]
            rows = [170, 205]
        for max_cells in budgets:
            for max_rows in rows:
                for novelty in ["core", "outside_h070", "outside_h069", "anti_shortcut"]:
                    q2_cap = 0 if family == "objective_state" else (72 if family in {"assignment_big", "rowvector_state"} else 52)
                    specs.append(
                        AssignmentSpec(
                            family=family,
                            max_cells=max_cells,
                            max_rows=max_rows,
                            q2_cap=q2_cap,
                            max_per_subject=24,
                            min_route_score=0.48 if family != "q_route" else 0.44,
                            min_cell_score=0.38 if family != "assignment_big" else 0.34,
                            novelty=novelty,
                            alpha=1.0,
                            mode="logit",
                        )
                    )
    return specs


def candidate_sweep(
    sample: pd.DataFrame,
    mats: dict[str, np.ndarray],
    routes: pd.DataFrame,
    cells_by_route: dict[str, pd.DataFrame],
    beta: np.ndarray,
    bad_vecs: dict[str, np.ndarray],
) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    rows = []
    probs: dict[str, np.ndarray] = {}
    seen: set[str] = set()
    for spec in candidate_specs():
        prob, meta = apply_candidate(spec, sample, mats, routes, cells_by_route, beta, bad_vecs)
        if meta["changed_cells_vs_h057"] < 140:
            continue
        if meta["selected_routes"] < 30:
            continue
        digest = short_hash(prob)
        if digest in seen:
            continue
        seen.add(digest)
        cid = (
            f"h071_{spec.family}_{spec.novelty}_c{spec.max_cells}_r{spec.max_rows}_"
            f"q2{spec.q2_cap}_{digest}"
        )
        meta["candidate_id"] = cid
        meta["hash"] = digest
        rows.append(meta)
        probs[cid] = prob
    cand = pd.DataFrame(rows)
    if cand.empty:
        raise RuntimeError("no H071 candidates generated")
    cand["action_rank"] = rank01(-cand["public_action_pred_delta_vs_h057"].to_numpy())
    cand["posterior_rank"] = rank01(-cand["posterior_delta_vs_h057"].to_numpy())
    cand["responsibility_rank"] = rank01(-cand["responsibility_weighted_delta_vs_h057"].to_numpy())
    cand["assignment_rank"] = rank01(cand["mean_assignment_route_score"].to_numpy())
    cand["cell_score_rank"] = rank01(cand["mean_cell_assignment_score"].to_numpy())
    cand["shortcut_avoid_rank"] = rank01(-cand["mean_latent_shortcut_energy"].to_numpy())
    cand["bad_avoid_rank"] = rank01(-cand["max_positive_bad_cosine"].to_numpy())
    cand["outside_h070_ratio"] = cand["outside_h070_cells"] / cand["changed_cells_vs_h057"].clip(lower=1)
    cand["outside_h069_ratio"] = cand["outside_h069_cells"] / cand["changed_cells_vs_h057"].clip(lower=1)
    cand["q2_risk"] = cand["Q2_changed_vs_h057"] / cand["changed_cells_vs_h057"].clip(lower=1)
    cand["route_diversity"] = cand["route_templates"].map(lambda text: len(str(text).split(";")) if text else 0)
    cand["bigbet_scale_score"] = ((-cand["public_action_pred_delta_vs_h057"] - 0.00070) / 0.00120).clip(0.0, 1.0)
    cand["h071_score"] = (
        0.22 * cand["action_rank"]
        + 0.14 * cand["assignment_rank"]
        + 0.12 * cand["responsibility_rank"]
        + 0.11 * cand["outside_h070_ratio"].clip(0, 1)
        + 0.10 * cand["outside_h069_ratio"].clip(0, 1)
        + 0.10 * cand["shortcut_avoid_rank"]
        + 0.08 * cand["bigbet_scale_score"]
        + 0.07 * cand["cell_score_rank"]
        + 0.04 * cand["posterior_rank"]
        + 0.03 * (cand["route_diversity"] / cand["route_diversity"].clip(lower=1).max()).clip(0, 1)
        + 0.03 * cand["bad_avoid_rank"]
        - 0.06 * cand["q2_risk"]
        - 0.06 * (cand["h050_null_selected"] > 0).astype(float)
    )
    cand = cand.sort_values(["h071_score", "public_action_pred_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True)
    for _, rec in cand.head(120).iterrows():
        cid = str(rec["candidate_id"])
        path = OUT / f"submission_{cid}.csv"
        write_submission(sample, probs[cid], path)
        cand.loc[cand["candidate_id"].eq(cid), "file"] = path.name
        cand.loc[cand["candidate_id"].eq(cid), "resolved_path"] = str(path.resolve())
    return cand, probs


def validate_submission(path: Path, sample: pd.DataFrame, h057_prob: np.ndarray) -> dict[str, object]:
    df = pd.read_csv(path)
    lhs = df[KEYS].copy()
    rhs = sample[KEYS].copy()
    for col in ["sleep_date", "lifelog_date"]:
        lhs[col] = pd.to_datetime(lhs[col]).dt.strftime("%Y-%m-%d")
        rhs[col] = pd.to_datetime(rhs[col]).dt.strftime("%Y-%m-%d")
    target = df[TARGETS].to_numpy(dtype=np.float64)
    changed = np.abs(target - h057_prob) > TOL
    return {
        "path": str(path.resolve()),
        "rows": int(len(df)),
        "keys_match": bool(lhs.equals(rhs.reset_index(drop=True))),
        "duplicate_keys": int(df.duplicated(KEYS).sum()),
        "nan_cells": int(np.isnan(target).sum()),
        "min_prob": float(np.nanmin(target)),
        "max_prob": float(np.nanmax(target)),
        "changed_cells_vs_h057_validation": int(changed.sum()),
        "upload_safe": bool(
            lhs.equals(rhs.reset_index(drop=True))
            and int(df.duplicated(KEYS).sum()) == 0
            and int(np.isnan(target).sum()) == 0
            and float(np.nanmin(target)) >= 0.0
            and float(np.nanmax(target)) <= 1.0
        ),
    }


def assignment_diagnostics(routes: pd.DataFrame, cand: pd.DataFrame) -> pd.DataFrame:
    action_leader = cand.sort_values("public_action_pred_delta_vs_h057").iloc[0]
    return pd.DataFrame(
        [
            {
                "route_candidates": int(len(routes)),
                "unique_rows_with_routes": int(routes["row"].nunique()),
                "max_route_score": float(routes["route_score"].max()),
                "top_route_name": str(routes.iloc[0]["route_name"]),
                "candidates": int(len(cand)),
                "best_survival_candidate": str(cand.iloc[0]["candidate_id"]),
                "best_survival_pred_delta": float(cand.iloc[0]["public_action_pred_delta_vs_h057"]),
                "action_leader_candidate": str(action_leader["candidate_id"]),
                "action_leader_pred_delta": float(action_leader["public_action_pred_delta_vs_h057"]),
                "action_leader_outside_h070_cells": int(action_leader["outside_h070_cells"]),
                "action_leader_changed_cells": int(action_leader["changed_cells_vs_h057"]),
            }
        ]
    )


def write_report(routes: pd.DataFrame, cand: pd.DataFrame, decision: pd.DataFrame, diag: pd.DataFrame) -> None:
    report = "\n".join(
        [
            "# H071 Row-Target Assignment Solver HS-JEPA",
            "",
            "Question: is the post-H070 bottleneck smooth latent scoring, or exact",
            "row-target route assignment?",
            "",
            "Design:",
            "",
            "- base: H057 public frontier;",
            "- context: H070 latent, H069 public/private factors, H068 action-health;",
            "- action unit: one route template per selected row;",
            "- target representation: discrete row-target support, then logit move toward H061 q061;",
            "- route templates: Q routes, S-stage routes, Q3+S objective routes, non-Q2 full-vector, full-state;",
            "- stress: bad-anchor cosine, H050-null avoidance, H070/H069 novelty, target quotas.",
            "",
            "Assignment diagnostics:",
            "",
            md_table(diag),
            "",
            "Top route candidates:",
            "",
            md_table(
                routes[
                    [
                        "route_id",
                        "row",
                        "subject_id",
                        "sleep_date",
                        "route_name",
                        "targets",
                        "n_cells",
                        "assignment_route_score",
                        "route_score",
                        "outside_h070_cells",
                        "outside_h069_cells",
                        "mean_shortcut_energy",
                    ]
                ],
                40,
            ),
            "",
            "Top candidates:",
            "",
            md_table(cand.head(35), 35),
            "",
            "Decision:",
            "",
            md_table(decision),
            "",
            "Interpretation rule:",
            "",
            "- If H071 improves by >= 0.001, exact row-target assignment becomes the main HS-JEPA decoder.",
            "- If H071 is neutral while H070 is better, smooth latent scoring is sufficient and assignment overconstrained it.",
            "- If H071 loses badly, current route templates are wrong or H070/H069 energies are not action-grade.",
            "",
        ]
    )
    (OUT / "h071_report.md").write_text(report)


def main() -> None:
    cleanup_previous_outputs()
    sample, latent, mats, beta, bad_vecs = load_runtime()
    routes, cells_by_route = build_route_candidates(latent)
    cand, probs = candidate_sweep(sample, mats, routes, cells_by_route, beta, bad_vecs)
    diag = assignment_diagnostics(routes, cand)

    bigbet = cand[
        (cand["max_positive_bad_cosine"] <= 0.0)
        & (cand["h050_null_selected"] == 0)
        & (cand["public_action_pred_delta_vs_h057"] <= -0.00090)
        & (cand["responsibility_weighted_delta_vs_h057"] <= -0.00075)
        & (cand["changed_cells_vs_h057"] >= 650)
    ].sort_values(["public_action_pred_delta_vs_h057", "h071_score"], ascending=[True, False])

    if len(bigbet):
        selected = bigbet.iloc[0].copy()
        decision_name = "promote_rowtarget_assignment_bigbet"
        worldview = (
            "the hidden state is a broad row-target route assignment field; "
            "public/private action survives outside H069/H070 supports"
        )
    else:
        selected = cand.iloc[0].copy()
        decision_name = "promote_rowtarget_assignment_sensor"
        worldview = "the hidden state is an exact row-target route assignment, not a smooth latent threshold"

    selected_file = OUT / str(selected["file"])
    digest = str(selected["hash"])
    root_file = ROOT / f"submission_h071_rowtarget_assignment_{digest}_uploadsafe.csv"
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

    routes.to_csv(OUT / "h071_route_candidates.csv", index=False)
    cand.to_csv(OUT / "h071_candidate_scores.csv", index=False)
    decision.to_csv(OUT / "h071_decision.csv", index=False)
    diag.to_csv(OUT / "h071_assignment_diagnostics.csv", index=False)
    write_report(routes, cand, decision, diag)
    print(
        decision[
            [
                "selected_candidate_id",
                "root_uploadsafe_path",
                "changed_cells_vs_h057",
                "changed_rows_vs_h057",
                "selected_routes",
                "outside_h070_cells",
                "outside_h069_cells",
                "Q2_changed_vs_h057",
                "public_action_pred_delta_vs_h057",
                "posterior_delta_vs_h057",
                "mean_assignment_route_score",
                "route_templates",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
