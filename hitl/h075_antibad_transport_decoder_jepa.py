#!/usr/bin/env python3
"""H075: anti-bad transport decoder HS-JEPA.

H074 showed that public-bad submissions define a real contrastive target
representation (`z_anti_shortcut`), but H074 still materialized selected cells
by moving them toward q061. H075 changes the decoder itself:

    bad submissions -> inverse movement field -> row-route assignment
    -> anti-bad transport probabilities

This is not another H074 threshold sweep. It asks whether failed public worlds
can define both support and value transport, not only a support veto.
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
OUT = HITL / "h075_antibad_transport_decoder_jepa"
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


H074MOD = import_module(HITL / "h074_anti_shortcut_state_inversion_jepa.py", "h074mod_for_h075")
H071MOD = H074MOD.H071MOD


@dataclass(frozen=True)
class H075Spec:
    family: str
    max_cells: int
    max_rows: int
    q2_cap: int
    max_per_subject: int
    min_route_score: float
    min_cell_score: float
    novelty: str
    alpha: float
    transport: str
    allowed_routes: tuple[str, ...]


def rank01(values: np.ndarray, high: bool = True) -> np.ndarray:
    return H071MOD.rank01(np.asarray(values, dtype=np.float64), high=high)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1.0e-12))


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return H071MOD.md_table(frame, n)


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h075_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h075_antibad_transport_*_uploadsafe.csv"):
        path.unlink()


def load_h074_runtime() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, pd.DataFrame], dict[str, np.ndarray], np.ndarray, dict[str, np.ndarray]]:
    sample, latent, mats, beta, bad_vecs = H071MOD.load_runtime()
    cells, h073_routes, h073_cells_by_route = H074MOD.load_h073_or_rebuild(sample, latent)
    cells = H074MOD.add_bad_opposition_features(cells, mats, bad_vecs)
    cells = add_transport_features(cells, mats, bad_vecs)
    h074_routes, h074_cells_by_route = H074MOD.merge_h074_scores_into_routes(h073_routes, h073_cells_by_route, cells)
    h075_routes, h075_cells_by_route = merge_transport_into_routes(h074_routes, h074_cells_by_route, cells)
    return sample, cells, h075_routes, h075_cells_by_route, mats, beta, bad_vecs


def add_transport_features(cells: pd.DataFrame, mats: dict[str, np.ndarray], bad_vecs: dict[str, np.ndarray]) -> pd.DataFrame:
    out = cells.copy()
    h057_logit = H071MOD.logit(mats["h057"]).reshape(-1)
    q061_logit = H071MOD.logit(mats["q061"]).reshape(-1)
    q_delta = q061_logit - h057_logit
    q_dir = np.sign(q_delta)
    q_dir = np.where(q_dir == 0, 1.0, q_dir)
    q_abs = np.abs(q_delta)

    if not bad_vecs:
        bad_mean = np.zeros_like(q_delta)
        bad_median = np.zeros_like(q_delta)
        bad_q75 = np.zeros_like(q_delta)
    else:
        stack = np.vstack([np.asarray(vec, dtype=np.float64) for vec in bad_vecs.values()])
        bad_mean = np.nanmean(stack, axis=0)
        bad_median = np.nanmedian(stack, axis=0)
        bad_q75 = np.nanpercentile(np.abs(stack), 75, axis=0)

    inverse_mean = -bad_mean
    inverse_median = -bad_median
    inverse_align = np.maximum(q_dir * inverse_mean, 0.0)
    inverse_median_align = np.maximum(q_dir * inverse_median, 0.0)
    q_cap = np.maximum(0.22, 1.55 * q_abs + 0.10)
    mag_cap = np.minimum(np.maximum(q_cap, 0.55 * bad_q75 + 0.18), 2.75)

    mirror_delta = q_dir * np.minimum(inverse_align, mag_cap)
    median_delta = q_dir * np.minimum(inverse_median_align, mag_cap)
    hybrid_delta = 0.52 * q_delta + 0.48 * mirror_delta
    conservative_delta = 0.70 * q_delta + 0.30 * mirror_delta
    edge_mag = np.minimum(np.maximum(q_abs, inverse_align), np.minimum(2.20, q_abs + 0.85))
    edge_delta = q_dir * edge_mag

    def gain(delta: np.ndarray) -> np.ndarray:
        before = H071MOD.bce(mats["h057"], mats["q061"]).reshape(-1)
        after = H071MOD.bce(H071MOD.sigmoid(h057_logit + delta).reshape(mats["h057"].shape), mats["q061"]).reshape(-1)
        return before - after

    out["h075_q_delta_abs"] = q_abs[out["flat_index"].to_numpy(dtype=int)]
    out["h075_bad_mean_signed"] = (q_dir * bad_mean)[out["flat_index"].to_numpy(dtype=int)]
    out["h075_inverse_align"] = inverse_align[out["flat_index"].to_numpy(dtype=int)]
    out["h075_mirror_delta"] = mirror_delta[out["flat_index"].to_numpy(dtype=int)]
    out["h075_median_delta"] = median_delta[out["flat_index"].to_numpy(dtype=int)]
    out["h075_hybrid_delta"] = hybrid_delta[out["flat_index"].to_numpy(dtype=int)]
    out["h075_conservative_delta"] = conservative_delta[out["flat_index"].to_numpy(dtype=int)]
    out["h075_edge_delta"] = edge_delta[out["flat_index"].to_numpy(dtype=int)]
    out["h075_mirror_gain"] = gain(mirror_delta)[out["flat_index"].to_numpy(dtype=int)]
    out["h075_hybrid_gain"] = gain(hybrid_delta)[out["flat_index"].to_numpy(dtype=int)]
    out["h075_edge_gain"] = gain(edge_delta)[out["flat_index"].to_numpy(dtype=int)]
    out["h075_transport_alignment"] = rank01(out["h075_inverse_align"].to_numpy())
    out["h075_transport_gain_rank"] = rank01(np.maximum(out["h075_hybrid_gain"].to_numpy(), out["h075_mirror_gain"].to_numpy()))
    out["h075_transport_cell_score"] = (
        0.22 * rank01(out["h074_cell_score"].to_numpy())
        + 0.18 * out["h075_transport_alignment"].to_numpy(dtype=float)
        + 0.15 * out["h075_transport_gain_rank"].to_numpy(dtype=float)
        + 0.13 * rank01(out["h074_bad_opp_rank"].to_numpy())
        + 0.11 * rank01(out["h073_bridge_cell_score"].to_numpy())
        + 0.09 * rank01(out["h068_cell_health"].to_numpy())
        + 0.06 * out["outside_h069_cell"].to_numpy(dtype=float)
        + 0.04 * out["outside_h070_cell"].to_numpy(dtype=float)
        - 0.12 * rank01(out["h074_bad_same_rank"].to_numpy())
        - 0.10 * rank01(out["latent_shortcut_energy"].to_numpy())
        - 0.07 * (out["target"].astype(str) == "Q2").to_numpy(dtype=float)
        - 0.12 * out["is_h050_null"].to_numpy(dtype=float)
    )
    out.loc[out["cell_q061_gain"] <= 0, "h075_transport_cell_score"] -= 0.60
    out.loc[out["h075_inverse_align"] <= 0, "h075_transport_cell_score"] -= 0.50
    out.loc[out["is_h050_null"] > 0, "h075_transport_cell_score"] -= 0.35
    return out.replace([np.inf, -np.inf], 0.0).fillna(0.0)


def merge_transport_into_routes(
    routes: pd.DataFrame,
    cells_by_route: dict[str, pd.DataFrame],
    cells: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    score_cols = [
        "flat_index",
        "h075_transport_cell_score",
        "h075_transport_alignment",
        "h075_transport_gain_rank",
        "h075_inverse_align",
        "h075_mirror_gain",
        "h075_hybrid_gain",
        "h075_edge_gain",
        "h075_q_delta_abs",
        "h075_bad_mean_signed",
        "h075_mirror_delta",
        "h075_median_delta",
        "h075_hybrid_delta",
        "h075_conservative_delta",
        "h075_edge_delta",
    ]
    score_map = cells[score_cols].copy()
    rows = []
    out_cells: dict[str, pd.DataFrame] = {}
    for rec in routes.to_dict("records"):
        route_id = str(rec["route_id"])
        if route_id not in cells_by_route:
            continue
        use = cells_by_route[route_id].merge(score_map, on="flat_index", how="left").fillna(0.0)
        out_cells[route_id] = use
        rows.append(
            {
                **rec,
                "mean_h075_transport_cell_score": float(use["h075_transport_cell_score"].mean()),
                "sum_h075_transport_cell_score": float(use["h075_transport_cell_score"].sum()),
                "mean_h075_transport_alignment": float(use["h075_transport_alignment"].mean()),
                "mean_h075_transport_gain_rank": float(use["h075_transport_gain_rank"].mean()),
                "mean_h075_inverse_align": float(use["h075_inverse_align"].mean()),
                "mean_h075_mirror_gain": float(use["h075_mirror_gain"].mean()),
                "mean_h075_hybrid_gain": float(use["h075_hybrid_gain"].mean()),
                "mean_h075_edge_gain": float(use["h075_edge_gain"].mean()),
            }
        )
    out = pd.DataFrame(rows)
    out["h075_route_score"] = (
        0.22 * rank01(out["sum_h075_transport_cell_score"].to_numpy() / np.sqrt(out["n_cells"].clip(lower=1)))
        + 0.16 * rank01(out["mean_h075_transport_alignment"].to_numpy())
        + 0.13 * rank01(out["mean_h075_transport_gain_rank"].to_numpy())
        + 0.11 * rank01(out["h074_route_score"].to_numpy())
        + 0.10 * rank01(out["assignment_route_score"].to_numpy())
        + 0.09 * rank01(out["mean_h074_bad_opp_rank"].to_numpy())
        + 0.07 * rank01(out["outside_h069_cells"].to_numpy())
        + 0.05 * rank01(out["mean_public_score"].to_numpy())
        - 0.10 * rank01(out["mean_h074_bad_same_rank"].to_numpy())
        - 0.08 * rank01(out["mean_shortcut_energy"].to_numpy())
    )
    out.loc[out["mean_h075_inverse_align"] <= 0, "h075_route_score"] -= 0.30
    out.loc[out["mean_h074_bad_same_rank"] > 0.70, "h075_route_score"] -= 0.10
    out.loc[out["mean_shortcut_energy"] > 0.65, "h075_route_score"] -= 0.08
    return out.sort_values(["h075_route_score", "mean_h075_transport_alignment"], ascending=[False, False]).reset_index(drop=True), out_cells


def h075_specs() -> list[H075Spec]:
    all_routes = tuple(H071MOD.ROUTES)
    stage_routes = ("s_stage", "s23_core", "s14_edge", "q3_s_stage", "recovery_route", "nonq2_full")
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
    specs: list[H075Spec] = []
    base = [
        ("transport_broad", 1120, 250, 95, 32, 0.46, 0.30, "outside_h069", row_broad),
        ("transport_broad", 1120, 250, 95, 32, 0.42, 0.30, "transport_big", row_broad),
        ("anti_bad_field", 980, 235, 62, 28, 0.50, 0.31, "bad_opposition", all_routes),
        ("anti_bad_field", 860, 220, 48, 26, 0.56, 0.34, "bad_opposition", all_routes),
        ("stage_transport", 860, 225, 0, 28, 0.52, 0.31, "transport_big", stage_routes),
        ("stage_transport", 720, 210, 0, 25, 0.58, 0.34, "bad_opposition", stage_routes),
        ("row_state_transport", 920, 225, 52, 28, 0.50, 0.31, "outside_h069", row_routes),
        ("row_state_transport", 760, 210, 38, 25, 0.56, 0.34, "bad_opposition", row_routes),
        ("assignment_transport", 760, 220, 60, 26, 0.48, 0.31, "anti_shortcut", all_routes),
    ]
    for family, max_cells, max_rows, q2_cap, max_per_subject, min_route, min_cell, novelty, routes in base:
        for transport, alpha in [
            ("hybrid", 1.00),
            ("mirror", 0.95),
            ("mirror", 1.15),
            ("conservative", 1.05),
            ("edge", 0.85),
        ]:
            specs.append(
                H075Spec(
                    family=family,
                    max_cells=max_cells,
                    max_rows=max_rows,
                    q2_cap=q2_cap,
                    max_per_subject=max_per_subject,
                    min_route_score=min_route,
                    min_cell_score=min_cell,
                    novelty=novelty,
                    alpha=alpha,
                    transport=transport,
                    allowed_routes=routes,
                )
            )
    return specs


def allowed_by_spec(spec: H075Spec, rec: dict[str, object]) -> bool:
    if spec.allowed_routes and str(rec["route_name"]) not in spec.allowed_routes:
        return False
    if float(rec["h075_route_score"]) < spec.min_route_score:
        return False
    if spec.novelty == "outside_h069":
        return int(rec["outside_h069_cells"]) >= max(1, int(rec["n_cells"]) // 2)
    if spec.novelty == "bad_opposition":
        return float(rec["mean_h074_bad_opp_rank"]) >= 0.62 and float(rec["mean_h074_bad_same_rank"]) <= 0.58
    if spec.novelty == "anti_shortcut":
        return float(rec["mean_h074_bad_same_rank"]) <= 0.50 and float(rec["mean_shortcut_energy"]) <= 0.52
    if spec.novelty == "transport_big":
        return float(rec["mean_h075_transport_alignment"]) >= 0.20 and float(rec["mean_h075_transport_gain_rank"]) >= 0.48
    return True


def select_assignments(
    spec: H075Spec,
    routes: pd.DataFrame,
    cells_by_route: dict[str, pd.DataFrame],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    pool = routes[routes.apply(lambda row: allowed_by_spec(spec, row.to_dict()), axis=1)].copy()
    pool = pool.sort_values(["h075_route_score", "h075_route_score", "assignment_route_score"], ascending=False)
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
        cells = cells[cells["h075_transport_cell_score"] >= spec.min_cell_score]
        cells = cells[cells["h075_inverse_align"] > 0]
        cells = cells[cells["is_h050_null"] == 0]
        cells = cells[cells["h074_bad_same_rank"] <= 0.84]
        if spec.novelty == "bad_opposition":
            cells = cells[cells["h074_bad_opp_rank"] >= 0.52]
        if spec.novelty == "transport_big":
            cells = cells[cells["h075_transport_gain_rank"] >= 0.42]
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


def transport_delta_column(spec: H075Spec) -> str:
    return {
        "mirror": "h075_mirror_delta",
        "hybrid": "h075_hybrid_delta",
        "conservative": "h075_conservative_delta",
        "edge": "h075_edge_delta",
    }.get(spec.transport, "h075_hybrid_delta")


def apply_candidate(
    spec: H075Spec,
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
    base_logit = H071MOD.logit(h057_prob)
    delta_col = transport_delta_column(spec)
    for rec in cell_sel.to_dict("records"):
        row = int(rec["row"])
        target_idx = int(rec["target_index"])
        delta = float(rec[delta_col]) * spec.alpha
        prob[row, target_idx] = H071MOD.sigmoid(base_logit[row, target_idx] + delta)
    prob = H071MOD.clip_prob(prob)

    changed = np.abs(prob - h057_prob) > TOL
    x = (H071MOD.bce(prob, q061) - H071MOD.bce(h057_prob, q061)).reshape(-1)
    row_delta = (H071MOD.bce(prob, q061) - H071MOD.bce(h057_prob, q061)).mean(axis=1)
    row_public = (
        pd.read_csv(HITL / "h067_row_responsibility_public_state_jepa" / "h067_row_responsibility.csv")
        .sort_values("row")["public_weight"]
        .to_numpy(dtype=np.float64)
    )
    move_vec = (H071MOD.logit(prob) - H071MOD.logit(h057_prob)).reshape(-1)
    bad_cos = {f"bad_cos_{H074MOD.safe_stem(name)}": cosine(move_vec, vec) for name, vec in bad_vecs.items()}
    max_bad_cos = max([max(value, 0.0) for value in bad_cos.values()] + [0.0])
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
        "transport": spec.transport,
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
        "h074_overlap_cells": int(cell_sel.get("h074_selected_cell", pd.Series(dtype=float)).sum()) if len(cell_sel) else 0,
        "public_action_pred_delta_vs_h057": float(x @ beta),
        "posterior_delta_vs_h057": float(x.mean()),
        "responsibility_weighted_delta_vs_h057": float(np.dot(row_public, row_delta)),
        "max_positive_bad_cosine": max_bad_cos,
        "mean_h075_route_score": float(route_sel["h075_route_score"].mean()) if len(route_sel) else 0.0,
        "mean_h075_transport_cell_score": float(cell_sel["h075_transport_cell_score"].mean()) if len(cell_sel) else 0.0,
        "mean_h075_transport_alignment": float(cell_sel["h075_transport_alignment"].mean()) if len(cell_sel) else 0.0,
        "mean_h075_transport_gain_rank": float(cell_sel["h075_transport_gain_rank"].mean()) if len(cell_sel) else 0.0,
        "mean_h075_inverse_align": float(cell_sel["h075_inverse_align"].mean()) if len(cell_sel) else 0.0,
        "mean_h075_mirror_gain": float(cell_sel["h075_mirror_gain"].mean()) if len(cell_sel) else 0.0,
        "mean_h075_hybrid_gain": float(cell_sel["h075_hybrid_gain"].mean()) if len(cell_sel) else 0.0,
        "mean_h075_edge_gain": float(cell_sel["h075_edge_gain"].mean()) if len(cell_sel) else 0.0,
        "mean_h074_route_score": float(route_sel["h074_route_score"].mean()) if len(route_sel) else 0.0,
        "mean_h074_cell_score": float(cell_sel["h074_cell_score"].mean()) if len(cell_sel) else 0.0,
        "mean_h074_bad_opp_rank": float(cell_sel["h074_bad_opp_rank"].mean()) if len(cell_sel) else 0.0,
        "mean_h074_bad_same_rank": float(cell_sel["h074_bad_same_rank"].mean()) if len(cell_sel) else 1.0,
        "mean_h073_bridge_cell_score": float(cell_sel["h073_bridge_cell_score"].mean()) if len(cell_sel) else 0.0,
        "mean_h068_health": float(cell_sel["h068_cell_health"].mean()) if len(cell_sel) else 0.0,
        "mean_public_score": float(cell_sel["public_score"].mean()) if len(cell_sel) else 0.0,
        "mean_invariant_score": float(cell_sel["invariant_score"].mean()) if len(cell_sel) else 0.0,
        "mean_shortcut_energy": float(cell_sel["latent_shortcut_energy"].mean()) if len(cell_sel) else 1.0,
        "h050_null_selected": int(cell_sel["is_h050_null"].sum()) if len(cell_sel) else 0,
        "selected_subjects": int(cell_sel["subject_id"].nunique()) if len(cell_sel) else 0,
        "route_templates": ";".join(f"{k}:{v}" for k, v in sorted(route_counts.items())),
        **bad_cos,
    }
    for target in TARGETS:
        meta[f"{target}_changed_vs_h057"] = int(changed[:, TARGETS.index(target)].sum())
    return prob, meta


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
    for spec in h075_specs():
        prob, meta = apply_candidate(spec, sample, mats, routes, cells_by_route, beta, bad_vecs)
        if meta["changed_cells_vs_h057"] < 160 or meta["selected_routes"] < 25:
            continue
        digest = short_hash(prob)
        if digest in seen:
            continue
        seen.add(digest)
        cid = (
            f"h075_{spec.family}_{spec.transport}_{spec.novelty}_"
            f"c{spec.max_cells}_r{spec.max_rows}_q2{spec.q2_cap}_{digest}"
        )
        meta["candidate_id"] = cid
        meta["hash"] = digest
        rows.append(meta)
        probs[cid] = prob
    cand = pd.DataFrame(rows)
    if cand.empty:
        raise RuntimeError("no H075 candidates generated")

    cand["action_rank"] = rank01(-cand["public_action_pred_delta_vs_h057"].to_numpy())
    cand["posterior_rank"] = rank01(-cand["posterior_delta_vs_h057"].to_numpy())
    cand["responsibility_rank"] = rank01(-cand["responsibility_weighted_delta_vs_h057"].to_numpy())
    cand["transport_route_rank"] = rank01(cand["mean_h075_route_score"].to_numpy())
    cand["transport_cell_rank"] = rank01(cand["mean_h075_transport_cell_score"].to_numpy())
    cand["transport_align_rank"] = rank01(cand["mean_h075_transport_alignment"].to_numpy())
    cand["transport_gain_rank"] = rank01(cand["mean_h075_transport_gain_rank"].to_numpy())
    cand["opp_rank"] = rank01(cand["mean_h074_bad_opp_rank"].to_numpy())
    cand["same_avoid_rank"] = rank01(-cand["mean_h074_bad_same_rank"].to_numpy())
    cand["shortcut_avoid_rank"] = rank01(-cand["mean_shortcut_energy"].to_numpy())
    cand["bad_avoid_rank"] = rank01(-cand["max_positive_bad_cosine"].to_numpy())
    cand["outside_h069_ratio"] = cand["outside_h069_cells"] / cand["changed_cells_vs_h057"].clip(lower=1)
    cand["q2_risk"] = cand["Q2_changed_vs_h057"] / cand["changed_cells_vs_h057"].clip(lower=1)
    cand["route_diversity"] = cand["route_templates"].map(lambda text: len(str(text).split(";")) if text else 0)
    cand["bigbet_scale_score"] = ((-cand["public_action_pred_delta_vs_h057"] - 0.00100) / 0.00140).clip(0.0, 1.0)
    cand["h075_score"] = (
        0.18 * cand["action_rank"]
        + 0.13 * cand["responsibility_rank"]
        + 0.12 * cand["transport_route_rank"]
        + 0.11 * cand["transport_cell_rank"]
        + 0.10 * cand["transport_align_rank"]
        + 0.09 * cand["transport_gain_rank"]
        + 0.08 * cand["opp_rank"]
        + 0.07 * cand["same_avoid_rank"]
        + 0.06 * cand["outside_h069_ratio"].clip(0, 1)
        + 0.05 * cand["bigbet_scale_score"]
        + 0.04 * cand["posterior_rank"]
        + 0.03 * cand["shortcut_avoid_rank"]
        + 0.03 * (cand["route_diversity"] / cand["route_diversity"].clip(lower=1).max()).clip(0, 1)
        + 0.02 * cand["bad_avoid_rank"]
        - 0.06 * cand["q2_risk"]
        - 0.07 * (cand["h050_null_selected"] > 0).astype(float)
    )
    cand = cand.sort_values(["h075_score", "public_action_pred_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True)
    for _, rec in cand.head(100).iterrows():
        cid = str(rec["candidate_id"])
        path = OUT / f"submission_{cid}.csv"
        H071MOD.write_submission(sample, probs[cid], path)
        cand.loc[cand["candidate_id"].eq(cid), "file"] = path.name
        cand.loc[cand["candidate_id"].eq(cid), "resolved_path"] = str(path.resolve())
    return cand, probs


def validate_submission(path: Path, sample: pd.DataFrame, h057_prob: np.ndarray) -> dict[str, object]:
    return H071MOD.validate_submission(path, sample, h057_prob)


def write_report(routes: pd.DataFrame, cand: pd.DataFrame, decision: pd.DataFrame) -> None:
    report = "\n".join(
        [
            "# H075 Anti-Bad Transport Decoder HS-JEPA",
            "",
            "Question: can known public-bad submissions define the value transport field, not only the support?",
            "",
            "Design:",
            "",
            "- context: H071 assignment, H073 action-health bridge, H074 anti-shortcut representation;",
            "- target representation: inverse movement vector of known public-bad submissions;",
            "- decoder: route assignment plus anti-bad transport in logit space;",
            "- stress: bad-anchor cosine, H050-null avoidance, q061 posterior/action-health sanity.",
            "",
            "Top H075 routes:",
            "",
            md_table(
                routes[
                    [
                        "route_id",
                        "row",
                        "subject_id",
                        "sleep_date",
                        "route_name",
                        "n_cells",
                        "h075_route_score",
                        "mean_h075_transport_cell_score",
                        "mean_h075_transport_alignment",
                        "mean_h075_transport_gain_rank",
                        "mean_h074_bad_opp_rank",
                        "mean_h074_bad_same_rank",
                        "outside_h069_cells",
                        "mean_shortcut_energy",
                    ]
                ],
                40,
            ),
            "",
            "Top candidates:",
            "",
            md_table(cand.head(40), 40),
            "",
            "Decision:",
            "",
            md_table(decision),
            "",
            "Interpretation rule:",
            "",
            "- If H075 wins by >= 0.001, failed public worlds are value-transport target representations.",
            "- If H075 is neutral but H074/H071 win, anti-shortcut is support-only and transport needs another decoder.",
            "- If H075 loses badly, inverse bad movement is a private/public extrapolation error even though H074 representation was real.",
            "",
        ]
    )
    (OUT / "h075_report.md").write_text(report)


def main() -> None:
    cleanup_previous_outputs()
    sample, cells, routes, cells_by_route, mats, beta, bad_vecs = load_h074_runtime()
    cand, probs = candidate_sweep(sample, mats, routes, cells_by_route, beta, bad_vecs)

    bigbet = cand[
        (cand["max_positive_bad_cosine"] <= 0.0)
        & (cand["h050_null_selected"] == 0)
        & (cand["public_action_pred_delta_vs_h057"] <= -0.00100)
        & (cand["responsibility_weighted_delta_vs_h057"] <= -0.00085)
        & (cand["changed_cells_vs_h057"] >= 520)
        & (cand["mean_h074_bad_same_rank"] <= 0.56)
        & (cand["mean_h075_transport_alignment"] >= 0.52)
    ].sort_values(["public_action_pred_delta_vs_h057", "h075_score"], ascending=[True, False])

    if len(bigbet):
        selected = bigbet.iloc[0].copy()
        decision_name = "promote_antibad_transport_bigbet"
        worldview = "failed public worlds define both anti-shortcut support and value transport"
    else:
        sensor = cand[
            (cand["max_positive_bad_cosine"] <= 0.0)
            & (cand["h050_null_selected"] == 0)
            & (cand["changed_cells_vs_h057"] >= 450)
            & (cand["responsibility_weighted_delta_vs_h057"] <= -0.00075)
            & (cand["mean_h075_transport_alignment"] >= 0.48)
        ].sort_values(["public_action_pred_delta_vs_h057", "h075_score"], ascending=[True, False])
        if len(sensor):
            selected = sensor.iloc[0].copy()
            decision_name = "promote_antibad_transport_sensor"
            worldview = "anti-bad transport is coherent but did not fully clear the 0.001 action gate"
        else:
            selected = cand.iloc[0].copy()
            decision_name = "promote_antibad_transport_diagnostic"
            worldview = "anti-bad transport is a diagnostic decoder, not yet an action-grade candidate"

    selected_file = OUT / str(selected["file"])
    digest = str(selected["hash"])
    root_file = ROOT / f"submission_h075_antibad_transport_{digest}_uploadsafe.csv"
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

    cells.to_csv(OUT / "h075_cell_scores.csv", index=False)
    routes.to_csv(OUT / "h075_route_candidates.csv", index=False)
    cand.to_csv(OUT / "h075_candidate_scores.csv", index=False)
    decision.to_csv(OUT / "h075_decision.csv", index=False)
    write_report(routes, cand, decision)
    print(
        decision[
            [
                "selected_candidate_id",
                "root_uploadsafe_path",
                "changed_cells_vs_h057",
                "changed_rows_vs_h057",
                "selected_routes",
                "outside_h069_cells",
                "Q2_changed_vs_h057",
                "transport",
                "mean_h075_transport_alignment",
                "mean_h075_transport_gain_rank",
                "public_action_pred_delta_vs_h057",
                "posterior_delta_vs_h057",
                "responsibility_weighted_delta_vs_h057",
                "route_templates",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
