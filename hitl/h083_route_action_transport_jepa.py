#!/usr/bin/env python3
"""H083: route-action transport HS-JEPA.

H082 treated the source-action field as independent row-target cells. H071
treated row-target placement as discrete route assignment, but before the
source-action field existed.

H083 combines them and makes a different big bet:

    H082's cells are fragments of row-level route states.
    The hidden correction target is route-action transport, not cell top-k.

For each row, a route template is scored from H071 assignment evidence and H082
source-action evidence. The route is then materialized as a coherent target set
using source moves plus a controlled q061 fill for route targets where source
evidence is missing.
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
OUT = HITL / "h083_route_action_transport_jepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
S_TARGETS = ["S1", "S2", "S3", "S4"]
NON_Q2 = [target for target in TARGETS if target != "Q2"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
TOL = 1.0e-12


@dataclass(frozen=True)
class H083Spec:
    name: str
    allowed_routes: tuple[str, ...]
    value_mode: str
    max_routes: int
    max_cells: int
    max_rows: int
    q2_cap: int
    max_per_subject: int
    min_route_action_score: float
    min_source_cells: int
    min_h082_cells: int
    min_family_mean: float
    max_bad_same_mean: float
    novelty: str
    alpha: float
    fill_alpha: float


def import_module(path: Path, name: str) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


H082MOD = import_module(HITL / "h082_source_action_field_jepa.py", "h082mod_for_h083")
H071MOD = H082MOD.H071MOD


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


def write_submission(sample: pd.DataFrame, prob: np.ndarray, path: Path) -> None:
    H071MOD.write_submission(sample, prob, path)


def validate_submission(path: Path, sample: pd.DataFrame, h057_prob: np.ndarray) -> dict[str, object]:
    return H071MOD.validate_submission(path, sample, h057_prob)


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return H071MOD.md_table(frame, n)


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1.0e-12))


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h083_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h083_route_action_*_uploadsafe.csv"):
        path.unlink()


def candidate_specs() -> list[H083Spec]:
    routes = H071MOD.ROUTES
    all_routes = tuple(routes)
    rowvector_routes = ("full_state", "nonq2_full", "q3_s_stage", "q_subjective", "recovery_route")
    objective_routes = ("s_stage", "s23_core", "s14_edge", "q3_s_stage", "recovery_route", "nonq2_full")
    compact_routes = ("q2_s3_tail", "q2_hardtail", "q1q3_subjective", "q3_quality", "s23_core", "s14_edge")
    return [
        H083Spec("all_transport_c920", all_routes, "source_q061_fill", 170, 920, 170, 95, 24, 0.56, 2, 1, 1.20, 0.86, "any", 1.00, 0.70),
        H083Spec("all_transport_amp_c920", all_routes, "source_q061_fill", 170, 920, 170, 95, 24, 0.56, 2, 1, 1.20, 0.86, "any", 1.18, 0.82),
        H083Spec("rowvector_transport_c840", rowvector_routes, "source_q061_fill", 155, 840, 155, 70, 22, 0.58, 2, 1, 1.25, 0.84, "any", 1.05, 0.72),
        H083Spec("source_only_route_c760", all_routes, "source_only", 160, 760, 160, 80, 24, 0.55, 2, 1, 1.15, 0.88, "any", 1.10, 0.00),
        H083Spec("h082row_route_c760", all_routes, "source_q061_fill", 150, 760, 150, 85, 22, 0.54, 1, 2, 1.10, 0.88, "h082_row", 1.05, 0.75),
        H083Spec("outside_h069_route_c760", all_routes, "source_q061_fill", 150, 760, 150, 80, 22, 0.54, 1, 1, 1.10, 0.86, "outside_h069", 1.08, 0.72),
        H083Spec("objective_route_c680", objective_routes, "source_q061_fill", 145, 680, 145, 0, 22, 0.55, 2, 1, 1.15, 0.88, "any", 1.10, 0.70),
        H083Spec("stage_route_c560", ("s_stage", "s23_core", "s14_edge"), "source_q061_fill", 130, 560, 130, 0, 20, 0.54, 1, 1, 1.10, 0.90, "any", 1.12, 0.74),
        H083Spec("compact_exception_c360", compact_routes, "source_q061_fill", 130, 360, 130, 60, 20, 0.52, 1, 1, 0.80, 0.92, "outside_h082", 1.18, 0.82),
        H083Spec("posterior_friendly_c760", all_routes, "source_q061_fill", 155, 760, 155, 80, 22, 0.54, 1, 1, 1.10, 0.86, "posterior_friendly", 1.06, 0.70),
        H083Spec("nonq2_transport_c760", tuple(r for r in all_routes if r not in {"q2_hardtail", "q2_s3_tail", "q_subjective", "full_state"}), "source_q061_fill", 155, 760, 155, 0, 22, 0.54, 1, 1, 1.10, 0.88, "any", 1.08, 0.74),
    ]


def load_runtime() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, np.ndarray], np.ndarray, dict[str, np.ndarray]]:
    sample, latent, mats, beta, bad_vecs = H071MOD.load_runtime()
    table_path = HITL / "h080_invariant_action_core_jepa" / "h080_cell_table.csv"
    if table_path.exists():
        table = pd.read_csv(table_path)
    else:
        table = H082MOD.build_or_load_table(sample, latent, mats, beta, bad_vecs)
    return sample, latent, table.fillna(0.0), mats, beta, bad_vecs


def build_route_action_table(table: pd.DataFrame) -> pd.DataFrame:
    route_path = HITL / "h071_rowtarget_assignment_solver_jepa" / "h071_route_candidates.csv"
    routes = pd.read_csv(route_path)
    h082_path = HITL / "h082_source_action_field_jepa" / "h082_selected_cells.csv"
    h082_cells = pd.read_csv(h082_path) if h082_path.exists() else pd.DataFrame(columns=["row", "target"])
    h082_pairs = set(zip(h082_cells.get("row", pd.Series(dtype=int)).astype(int), h082_cells.get("target", pd.Series(dtype=str)).astype(str)))

    rows = []
    for rec in routes.to_dict("records"):
        target_indices = [int(x) for x in str(rec["target_indices"]).split(",") if str(x) != ""]
        row = int(rec["row"])
        cells = table[(table["row"].astype(int) == row) & (table["target_index"].astype(int).isin(target_indices))].copy()
        if cells.empty:
            continue
        source_cells = int((cells["source_count"] > 0).sum())
        h082_hit = int(sum((row, str(t)) in h082_pairs for t in cells["target"].astype(str)))
        source_action_sum = float(cells["source_action_delta"].sum())
        source_action_mean = float(cells["source_action_delta"].mean())
        source_posterior_sum = float(cells["source_posterior_delta"].sum())
        active_source = cells[cells["source_count"] > 0]
        route_move_abs = float(active_source["source_mean_move"].abs().mean()) if len(active_source) else 0.0
        move_sign = active_source["source_mean_move"].to_numpy(dtype=float) if len(active_source) else np.array([], dtype=float)
        if len(move_sign) <= 1:
            direction_consistency = 0.5
        else:
            direction_consistency = max(float((move_sign > 0).mean()), float((move_sign < 0).mean()))
        rows.append(
            {
                **rec,
                "source_cells": source_cells,
                "h082_cells": h082_hit,
                "h082_row": int(h082_hit > 0),
                "outside_h082_cells": int(len(cells) - h082_hit),
                "route_source_action_sum": source_action_sum,
                "route_source_action_mean": source_action_mean,
                "route_source_posterior_sum": source_posterior_sum,
                "route_source_posterior_mean": float(cells["source_posterior_delta"].mean()),
                "route_source_count_mean": float(cells["source_count"].mean()),
                "route_family_count_mean": float(cells["source_family_count"].mean()),
                "route_source_consensus_mean": float(cells["source_consensus"].mean()),
                "route_bad_same_mean": float(cells["h080_bad_same_rank"].mean()),
                "route_bad_opp_mean": float(cells["h080_bad_opp_rank"].mean()),
                "route_h079_row": float(cells["h079_row"].mean()),
                "route_h080_score_mean": float(cells["h080_cell_score"].mean()),
                "route_move_abs_mean": route_move_abs,
                "route_direction_consistency": direction_consistency,
                "route_h050_null_cells": int(cells["is_h050_null"].sum()),
            }
        )
    out = pd.DataFrame(rows)
    if out.empty:
        raise RuntimeError("no route-action rows")
    out["route_action_score"] = (
        0.24 * rank01(-out["route_source_action_sum"].to_numpy())
        + 0.14 * rank01(out["assignment_route_score"].to_numpy())
        + 0.12 * rank01(out["h082_cells"].to_numpy())
        + 0.10 * rank01(out["source_cells"].to_numpy())
        + 0.09 * rank01(out["route_family_count_mean"].to_numpy())
        + 0.08 * rank01(out["route_move_abs_mean"].to_numpy())
        + 0.07 * rank01(out["outside_h069_cells"].to_numpy())
        + 0.06 * rank01(-out["mean_shortcut_energy"].to_numpy())
        + 0.05 * rank01(out["route_h080_score_mean"].to_numpy())
        + 0.05 * out["route_direction_consistency"].to_numpy(dtype=float)
        - 0.08 * rank01(out["route_bad_same_mean"].to_numpy())
        - 0.10 * (out["route_h050_null_cells"] > 0).astype(float)
    )
    return out.sort_values(["route_action_score", "route_source_action_sum"], ascending=[False, True]).reset_index(drop=True)


def pool_for(route_table: pd.DataFrame, spec: H083Spec) -> pd.DataFrame:
    pool = route_table[
        route_table["route_name"].astype(str).isin(spec.allowed_routes)
        & (route_table["route_action_score"] >= spec.min_route_action_score)
        & (route_table["source_cells"] >= spec.min_source_cells)
        & (route_table["h082_cells"] >= spec.min_h082_cells)
        & (route_table["route_family_count_mean"] >= spec.min_family_mean)
        & (route_table["route_bad_same_mean"] <= spec.max_bad_same_mean)
        & (route_table["route_h050_null_cells"] <= 0)
    ].copy()
    if spec.q2_cap == 0:
        pool = pool[pool["q2_cells"] <= 0].copy()
    if spec.novelty == "h082_row":
        pool = pool[pool["h082_row"] > 0].copy()
    elif spec.novelty == "outside_h082":
        pool = pool[pool["outside_h082_cells"] >= np.maximum(1, pool["n_cells"] // 2)].copy()
    elif spec.novelty == "outside_h069":
        pool = pool[pool["outside_h069_cells"] >= np.maximum(1, pool["n_cells"] // 2)].copy()
    elif spec.novelty == "posterior_friendly":
        pool = pool[pool["route_source_posterior_sum"] < 0].copy()
    elif spec.novelty != "any":
        raise ValueError(spec.novelty)
    return pool.sort_values(["route_action_score", "route_source_action_sum"], ascending=[False, True])


def greedy_select(pool: pd.DataFrame, spec: H083Spec) -> pd.DataFrame:
    selected = []
    rows_seen: set[int] = set()
    subject_counts: dict[str, int] = {}
    total_cells = 0
    q2_cells = 0
    for rec in pool.to_dict("records"):
        row = int(rec["row"])
        subject = str(rec["subject_id"])
        n_cells = int(rec["n_cells"])
        new_q2 = int(rec["q2_cells"])
        if len(selected) >= spec.max_routes:
            break
        if row in rows_seen:
            continue
        if len(rows_seen) >= spec.max_rows:
            break
        if subject_counts.get(subject, 0) >= spec.max_per_subject:
            continue
        if total_cells + n_cells > spec.max_cells:
            continue
        if q2_cells + new_q2 > spec.q2_cap:
            continue
        selected.append(rec)
        rows_seen.add(row)
        subject_counts[subject] = subject_counts.get(subject, 0) + 1
        total_cells += n_cells
        q2_cells += new_q2
    return pd.DataFrame(selected)


def materialize(selected_routes: pd.DataFrame, table: pd.DataFrame, mats: dict[str, np.ndarray], spec: H083Spec) -> tuple[np.ndarray, pd.DataFrame]:
    prob = mats["h057"].copy()
    h057_logit = logit(mats["h057"])
    q061_move = logit(mats["q061"]) - h057_logit
    selected_cells = []
    for rec in selected_routes.to_dict("records"):
        row = int(rec["row"])
        target_indices = [int(x) for x in str(rec["target_indices"]).split(",") if str(x) != ""]
        cells = table[(table["row"].astype(int) == row) & (table["target_index"].astype(int).isin(target_indices))].copy()
        route_active = cells[cells["source_count"] > 0]
        route_mean_move = float(route_active["source_mean_move"].mean()) if len(route_active) else 0.0
        for cell in cells.to_dict("records"):
            tidx = int(cell["target_index"])
            source_move = float(cell["source_mean_move"])
            has_source = float(cell["source_count"]) > 0
            if spec.value_mode == "source_only":
                if not has_source:
                    continue
                move = source_move
            elif spec.value_mode == "source_q061_fill":
                if has_source:
                    move = source_move
                else:
                    move = spec.fill_alpha * float(q061_move[row, tidx])
            elif spec.value_mode == "route_mean_fill":
                move = source_move if has_source else spec.fill_alpha * route_mean_move
            else:
                raise ValueError(spec.value_mode)
            prob[row, tidx] = float(sigmoid(np.array([h057_logit[row, tidx] + spec.alpha * move]))[0])
            selected_cells.append({**cell, **{f"h083_route_{k}": v for k, v in rec.items()}, "h083_has_source": int(has_source), "h083_move": move})
    return clip_prob(prob), pd.DataFrame(selected_cells)


def evaluate(prob: np.ndarray, selected_routes: pd.DataFrame, selected_cells: pd.DataFrame, spec: H083Spec, mats: dict[str, np.ndarray], beta: np.ndarray, bad_vecs: dict[str, np.ndarray]) -> dict[str, object]:
    h057 = mats["h057"]
    q061 = mats["q061"]
    changed = np.abs(prob - h057) > TOL
    x = (bce(prob, q061) - bce(h057, q061)).reshape(-1)
    row_delta = (bce(prob, q061) - bce(h057, q061)).mean(axis=1)
    row_public = (
        pd.read_csv(HITL / "h067_row_responsibility_public_state_jepa" / "h067_row_responsibility.csv")
        .sort_values("row")["public_weight"]
        .to_numpy(dtype=np.float64)
    )
    move_vec = (logit(prob) - logit(h057)).reshape(-1)
    bad_cos = {f"bad_cos_{Path(name).stem[:24]}": cosine(move_vec, vec) for name, vec in bad_vecs.items()}
    max_bad_cos = max([max(v, 0.0) for v in bad_cos.values()] + [0.0])
    target_counts = selected_cells["target"].value_counts().to_dict() if len(selected_cells) else {}
    route_counts = selected_routes["route_name"].value_counts().to_dict() if len(selected_routes) else {}
    meta: dict[str, object] = {
        "candidate_id": "",
        "spec_name": spec.name,
        "value_mode": spec.value_mode,
        "novelty": spec.novelty,
        "alpha": spec.alpha,
        "fill_alpha": spec.fill_alpha,
        "selected_routes": int(len(selected_routes)),
        "selected_cells": int(len(selected_cells)),
        "changed_cells_vs_h057": int(changed.sum()),
        "changed_rows_vs_h057": int(changed.any(axis=1).sum()),
        "filled_cells": int((selected_cells["h083_has_source"] == 0).sum()) if len(selected_cells) else 0,
        "source_cells": int((selected_cells["h083_has_source"] > 0).sum()) if len(selected_cells) else 0,
        "h082_cells": int(selected_routes["h082_cells"].sum()) if len(selected_routes) else 0,
        "outside_h082_cells": int(selected_routes["outside_h082_cells"].sum()) if len(selected_routes) else 0,
        "outside_h069_cells": int(selected_cells["outside_h069_cell"].sum()) if len(selected_cells) else 0,
        "public_action_pred_delta_vs_h057": float(x @ beta),
        "posterior_delta_vs_h057": float(x.mean()),
        "responsibility_weighted_delta_vs_h057": float(np.dot(row_public, row_delta)),
        "max_positive_bad_cosine": max_bad_cos,
        "mean_abs_prob_move_vs_h057": float(np.abs(prob - h057).mean()),
        "max_abs_prob_move_vs_h057": float(np.abs(prob - h057).max()),
        "mean_route_action_score": float(selected_routes["route_action_score"].mean()) if len(selected_routes) else 0.0,
        "mean_assignment_route_score": float(selected_routes["assignment_route_score"].mean()) if len(selected_routes) else 0.0,
        "mean_route_source_action_sum": float(selected_routes["route_source_action_sum"].mean()) if len(selected_routes) else 0.0,
        "sum_route_source_action_sum": float(selected_routes["route_source_action_sum"].sum()) if len(selected_routes) else 0.0,
        "mean_route_source_posterior_sum": float(selected_routes["route_source_posterior_sum"].mean()) if len(selected_routes) else 0.0,
        "mean_family_count": float(selected_routes["route_family_count_mean"].mean()) if len(selected_routes) else 0.0,
        "mean_bad_same": float(selected_routes["route_bad_same_mean"].mean()) if len(selected_routes) else 1.0,
        "selected_subjects": int(selected_routes["subject_id"].nunique()) if len(selected_routes) else 0,
        "selected_rows": ",".join(map(str, sorted(selected_routes["row"].astype(int).unique()))) if len(selected_routes) else "",
        "route_templates": ";".join(f"{k}:{v}" for k, v in sorted(route_counts.items())),
        "target_templates": ";".join(f"{k}:{v}" for k, v in sorted(target_counts.items())),
        **bad_cos,
    }
    for target in TARGETS:
        meta[f"{target}_changed_vs_h057"] = int(changed[:, TARGETS.index(target)].sum())
    return meta


def candidate_sweep(route_table: pd.DataFrame, table: pd.DataFrame, sample: pd.DataFrame, mats: dict[str, np.ndarray], beta: np.ndarray, bad_vecs: dict[str, np.ndarray]) -> tuple[pd.DataFrame, dict[str, np.ndarray], pd.DataFrame, pd.DataFrame]:
    rows = []
    probs: dict[str, np.ndarray] = {}
    route_parts = []
    cell_parts = []
    seen: set[str] = set()
    for spec in candidate_specs():
        pool = pool_for(route_table, spec)
        selected_routes = greedy_select(pool, spec)
        if selected_routes.empty:
            continue
        prob, selected_cells = materialize(selected_routes, table, mats, spec)
        if len(selected_cells) < 120:
            continue
        digest = short_hash(prob)
        if digest in seen:
            continue
        seen.add(digest)
        meta = evaluate(prob, selected_routes, selected_cells, spec, mats, beta, bad_vecs)
        cid = f"h083_{spec.name}_{digest}"
        meta["candidate_id"] = cid
        meta["hash"] = digest
        rows.append(meta)
        probs[cid] = prob
        route_parts.append(selected_routes.assign(candidate_id=cid))
        cell_parts.append(selected_cells.assign(candidate_id=cid))
    cand = pd.DataFrame(rows)
    if cand.empty:
        raise RuntimeError("no H083 candidates generated")
    cand["action_rank"] = rank01(-cand["public_action_pred_delta_vs_h057"].to_numpy())
    cand["posterior_rank"] = rank01(-cand["posterior_delta_vs_h057"].to_numpy())
    cand["responsibility_rank"] = rank01(-cand["responsibility_weighted_delta_vs_h057"].to_numpy())
    cand["bad_avoid_rank"] = rank01(-cand["max_positive_bad_cosine"].to_numpy())
    cand["route_rank"] = rank01(cand["mean_route_action_score"].to_numpy())
    cand["scale_rank"] = rank01(np.minimum(cand["changed_cells_vs_h057"].to_numpy(), 920))
    cand["fill_ratio"] = cand["filled_cells"] / cand["selected_cells"].clip(lower=1)
    cand["h082_ratio"] = cand["h082_cells"] / cand["selected_cells"].clip(lower=1)
    cand["bigbet_score"] = ((-cand["public_action_pred_delta_vs_h057"] - 0.0010) / 0.0060).clip(0.0, 1.0)
    cand["h083_score"] = (
        0.24 * cand["action_rank"]
        + 0.16 * cand["route_rank"]
        + 0.13 * cand["posterior_rank"]
        + 0.11 * cand["responsibility_rank"]
        + 0.10 * cand["scale_rank"]
        + 0.08 * cand["bigbet_score"]
        + 0.07 * cand["bad_avoid_rank"]
        + 0.05 * rank01(cand["outside_h069_cells"].to_numpy())
        + 0.04 * rank01(cand["h082_cells"].to_numpy())
        - 0.07 * (cand["fill_ratio"] > 0.55).astype(float)
        - 0.05 * (cand["max_abs_prob_move_vs_h057"] > 0.28).astype(float)
    )
    cand = cand.sort_values(["h083_score", "public_action_pred_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True)
    for _, rec in cand.iterrows():
        cid = str(rec["candidate_id"])
        path = OUT / f"submission_{cid}.csv"
        write_submission(sample, probs[cid], path)
        cand.loc[cand["candidate_id"].eq(cid), "file"] = path.name
        cand.loc[cand["candidate_id"].eq(cid), "resolved_path"] = str(path.resolve())
    routes = pd.concat(route_parts, ignore_index=True) if route_parts else pd.DataFrame()
    cells = pd.concat(cell_parts, ignore_index=True) if cell_parts else pd.DataFrame()
    return cand, probs, routes, cells


def write_report(route_table: pd.DataFrame, cand: pd.DataFrame, selected_routes: pd.DataFrame, selected_cells: pd.DataFrame, decision: pd.DataFrame) -> None:
    route_cols = [
        "candidate_id",
        "row",
        "subject_id",
        "sleep_date",
        "route_name",
        "targets",
        "route_action_score",
        "route_source_action_sum",
        "route_source_posterior_sum",
        "source_cells",
        "h082_cells",
        "outside_h082_cells",
        "assignment_route_score",
        "route_family_count_mean",
    ]
    cell_cols = [
        "candidate_id",
        "row",
        "subject_id",
        "sleep_date",
        "target",
        "source_count",
        "source_family_count",
        "source_mean_move",
        "source_action_delta",
        "source_posterior_delta",
        "h083_has_source",
        "h083_move",
    ]
    report = [
        "# H083 Route-Action Transport HS-JEPA",
        "",
        "Question: are H082 source-action cells fragments of row-level hidden route states?",
        "",
        "Design:",
        "",
        "- context: H071 route candidates plus H080/H082 source-action cell table;",
        "- target representation: route-action transport field;",
        "- action unit: one route template per row, not independent cells;",
        "- value decoder: source move with optional q061 fill for route targets missing source evidence.",
        "",
        "Route-action table summary:",
        "",
        md_table(
            pd.DataFrame(
                [
                    {
                        "route_candidates": int(len(route_table)),
                        "unique_rows": int(route_table["row"].nunique()),
                        "max_route_action_score": float(route_table["route_action_score"].max()),
                        "top_route": str(route_table.iloc[0]["route_name"]),
                        "top_route_source_action_sum": float(route_table.iloc[0]["route_source_action_sum"]),
                    }
                ]
            )
        ),
        "",
        "Candidates:",
        "",
        md_table(cand, 40),
        "",
        "Selected route sample:",
        "",
        md_table(selected_routes[[c for c in route_cols if c in selected_routes.columns]].head(160), 160) if len(selected_routes) else "(none)",
        "",
        "Selected cell sample:",
        "",
        md_table(selected_cells[[c for c in cell_cols if c in selected_cells.columns]].head(160), 160) if len(selected_cells) else "(none)",
        "",
        "Decision:",
        "",
        md_table(decision),
    ]
    (OUT / "h083_report.md").write_text("\n".join(report))


def main() -> None:
    cleanup_previous_outputs()
    sample, _latent, table, mats, beta, bad_vecs = load_runtime()
    route_table = build_route_action_table(table)
    cand, probs, routes, cells = candidate_sweep(route_table, table, sample, mats, beta, bad_vecs)
    bigbet = cand[
        (cand["public_action_pred_delta_vs_h057"] <= -0.0012)
        & (cand["changed_cells_vs_h057"] >= 250)
        & (cand["posterior_delta_vs_h057"] <= 0.0005)
        & (cand["max_positive_bad_cosine"] <= 0.025)
    ].copy()
    if len(bigbet):
        selected = bigbet.sort_values(["h083_score", "public_action_pred_delta_vs_h057"], ascending=[False, True]).iloc[0]
        decision_name = "promote_route_action_transport_bigbet"
        worldview = "H082 cells are fragments of row-level route-action states"
    else:
        selected = cand.iloc[0]
        decision_name = "promote_route_action_transport_diagnostic"
        worldview = "route-action state is measurable but did not clear every big-bet guardrail"

    selected_id = str(selected["candidate_id"])
    root_file = ROOT / f"submission_h083_route_action_{selected['hash']}_uploadsafe.csv"
    shutil.copy2(Path(str(selected["resolved_path"])), root_file)
    validation = validate_submission(root_file, sample, mats["h057"])
    decision = pd.DataFrame([{**selected.to_dict(), **validation}])
    decision.insert(0, "worldview", worldview)
    decision.insert(0, "root_uploadsafe_path", str(root_file.resolve()))
    decision.insert(0, "selected_resolved_path", str(selected["resolved_path"]))
    decision.insert(0, "selected_file", str(selected["file"]))
    decision.insert(0, "selected_candidate_id", selected_id)
    decision.insert(0, "decision", decision_name)

    cand.to_csv(OUT / "h083_candidate_scores.csv", index=False)
    route_table.to_csv(OUT / "h083_route_action_table.csv", index=False)
    routes.to_csv(OUT / "h083_selected_routes.csv", index=False)
    cells.to_csv(OUT / "h083_selected_cells.csv", index=False)
    decision.to_csv(OUT / "h083_decision.csv", index=False)
    write_report(route_table, cand, routes[routes["candidate_id"].eq(selected_id)].copy(), cells[cells["candidate_id"].eq(selected_id)].copy(), decision)

    print(f"selected={selected_id}")
    print(f"root={root_file}")
    print(decision[["decision", "public_action_pred_delta_vs_h057", "posterior_delta_vs_h057", "responsibility_weighted_delta_vs_h057", "changed_cells_vs_h057", "max_positive_bad_cosine", "upload_safe"]].to_string(index=False))


if __name__ == "__main__":
    main()
