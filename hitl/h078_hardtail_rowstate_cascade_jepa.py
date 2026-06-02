#!/usr/bin/env python3
"""H078: hard-tail row-state cascade HS-JEPA.

H077 tested a sparse contradiction: a few row-target cells where the public
action sensor wants a hard-tail move while q061 says the move is too extreme.

H078 flips one more assumption. Maybe those cells are not independent target
exceptions. Maybe they are visible anchors of a hidden row-level human state
where Q2/S-stage/recovery targets move together.

This is deliberately a big-bet sensor:

    context = H077 hard-tail conflict rows + H076 route/value cells
    target  = row-level correction field, not isolated cells

If it wins, HS-JEPA needs a row-state cascade decoder. If it loses, H077's
conflict should be treated as sparse cell-level evidence, not a whole-day state.
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
H076_OUT = HITL / "h076_route_specific_value_decoder_jepa"
H077_OUT = HITL / "h077_hardtail_conflict_route_jepa"
OUT = HITL / "h078_hardtail_rowstate_cascade_jepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
TOL = 1.0e-12


def import_module(path: Path, name: str) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


H077MOD = import_module(HITL / "h077_hardtail_conflict_route_jepa.py", "h077mod_for_h078")
H076MOD = H077MOD.H076MOD
H071MOD = H077MOD.H071MOD
H074MOD = H077MOD.H074MOD


@dataclass(frozen=True)
class H078Spec:
    name: str
    source_candidate: str
    expansion: str
    max_seed_rows: int
    max_cells: int
    max_per_subject: int
    min_cell_action_gain: float
    min_route_action_gain: float
    max_same_rank: float
    require_outside_h069: bool
    allow_negative_q061: bool
    companion_scale: float


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


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return H071MOD.md_table(frame, n)


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h078_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h078_hardtail_rowstate_*_uploadsafe.csv"):
        path.unlink()


def load_artifacts() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    cell_path = H076_OUT / "h076_policy_cell_scores.csv"
    route_path = H076_OUT / "h076_policy_route_candidates.csv"
    h077_cand_path = H077_OUT / "h077_candidate_scores.csv"
    h077_cell_path = H077_OUT / "h077_selected_cells.csv"
    for path in [cell_path, route_path, h077_cand_path, h077_cell_path]:
        if not path.exists():
            raise FileNotFoundError(path)
    h076_cells = pd.read_csv(cell_path)
    h076_routes = pd.read_csv(route_path)
    if "route_name" not in h076_cells.columns:
        route_names = h076_routes[["h076_policy", "route_id", "route_name"]].drop_duplicates()
        h076_cells = h076_cells.merge(
            route_names,
            on=["h076_policy", "route_id"],
            how="left",
            validate="many_to_one",
        )
    return h076_cells, h076_routes, pd.read_csv(h077_cand_path), pd.read_csv(h077_cell_path)


def candidate_specs() -> list[H078Spec]:
    sources = [
        "h077_conflict_cell_top16_123f6665",
        "h077_conflict_cell_top8_d68f58f3",
        "h077_monster_mixed_top5_38bd8eb7",
        "h077_monster_q2s3_top1_c0698455",
    ]
    specs: list[H078Spec] = []
    for source in sources:
        specs.extend(
            [
                H078Spec(source + "_row_public_companion", source, "row_public_companion", 18, 78, 5, 0.000055, 0.00012, 0.86, False, True, 0.74),
                H078Spec(source + "_route_cascade_soft", source, "route_cascade_soft", 14, 88, 4, 0.000040, 0.00016, 0.84, False, True, 0.92),
                H078Spec(source + "_hybrid_q061_guard", source, "hybrid_q061_guard", 18, 96, 5, 0.000025, 0.00010, 0.82, True, False, 0.68),
                H078Spec(source + "_fullrow_state_probe", source, "fullrow_state_probe", 12, 84, 4, 0.000020, 0.00008, 0.82, True, False, 0.55),
            ]
        )
    return specs


def source_seed_rows(h077_cells: pd.DataFrame, source_candidate: str, limit: int) -> pd.DataFrame:
    src = h077_cells[h077_cells["candidate_id"].astype(str).eq(source_candidate)].copy()
    if src.empty:
        return src
    rows = (
        src.groupby(["row", "subject_id", "sleep_date"], as_index=False)
        .agg(
            seed_cells=("flat_index", "nunique"),
            seed_targets=("target", lambda x: ",".join(sorted(set(map(str, x))))),
            seed_public_gain=("h076_public_action_gain", "sum"),
            seed_conflict_value_loss=("h076_value_gain", lambda x: -float(np.asarray(x, dtype=float).sum())),
            seed_bad_same=("h074_bad_same_rank", "mean"),
            seed_bad_opp=("h074_bad_opp_rank", "mean"),
            seed_shortcut=("latent_shortcut_energy", "mean"),
            seed_outside_h069=("outside_h069_cell", "sum"),
        )
        .sort_values(["seed_public_gain", "seed_cells"], ascending=[False, False])
        .head(limit)
        .reset_index(drop=True)
    )
    rows["seed_row_rank"] = rank01(rows["seed_public_gain"].to_numpy())
    return rows


def best_cells_by_flat(pool: pd.DataFrame, score_col: str) -> pd.DataFrame:
    if pool.empty:
        return pool
    return (
        pool.sort_values([score_col, "h076_public_action_gain", "h076_cell_score"], ascending=False)
        .drop_duplicates("flat_index", keep="first")
        .reset_index(drop=True)
    )


def row_companion_cells(
    h076_cells: pd.DataFrame,
    seed_rows: pd.DataFrame,
    spec: H078Spec,
) -> pd.DataFrame:
    rows = set(seed_rows["row"].astype(int).tolist())
    pool = h076_cells[h076_cells["row"].astype(int).isin(rows)].copy()
    pool = pool[pool["is_h050_null"] == 0]
    pool = pool[pool["h074_bad_same_rank"] <= spec.max_same_rank]
    if spec.require_outside_h069:
        pool = pool[pool["outside_h069_cell"] > 0]

    if spec.expansion == "row_public_companion":
        pool = pool[
            pool["h076_policy"].isin(["q2_tail_stage_soft", "objective_stage_edge", "recovery_full_vector"])
            & (pool["h076_public_action_gain"] >= spec.min_cell_action_gain)
        ].copy()
        pool["h078_cell_pick_score"] = (
            0.40 * rank01(pool["h076_public_action_gain"].to_numpy())
            + 0.17 * rank01(pool["h074_bad_opp_rank"].to_numpy())
            + 0.13 * rank01(pool["outside_h069_cell"].to_numpy())
            + 0.12 * rank01(pool["public_score"].to_numpy())
            + 0.10 * rank01(pool["h073_bridge_cell_score"].to_numpy())
            - 0.16 * rank01(pool["h074_bad_same_rank"].to_numpy())
            - 0.10 * rank01(pool["latent_shortcut_energy"].to_numpy())
        )
        return best_cells_by_flat(pool, "h078_cell_pick_score")

    if spec.expansion == "hybrid_q061_guard":
        pool = pool[
            pool["h076_policy"].isin(["anti_shortcut_q061_baseline", "bad_safe_recovery", "public_private_value_gate"])
            & (pool["h076_public_action_gain"] >= spec.min_cell_action_gain)
            & (pool["h076_value_gain"] > 0)
            & (pool["cell_q061_gain"] > 0)
        ].copy()
        pool["h078_cell_pick_score"] = (
            0.30 * rank01(pool["h076_public_action_gain"].to_numpy())
            + 0.22 * rank01(pool["h076_value_gain"].to_numpy())
            + 0.16 * rank01(pool["h074_cell_score"].to_numpy())
            + 0.10 * rank01(pool["outside_h069_cell"].to_numpy())
            - 0.14 * rank01(pool["h074_bad_same_rank"].to_numpy())
            - 0.10 * rank01(pool["latent_shortcut_energy"].to_numpy())
        )
        return best_cells_by_flat(pool, "h078_cell_pick_score")

    if spec.expansion == "fullrow_state_probe":
        pool = pool[
            pool["h076_policy"].isin(["anti_shortcut_q061_baseline", "public_private_value_gate"])
            & (pool["h076_public_action_gain"] >= spec.min_cell_action_gain)
            & (pool["h076_value_gain"] > 0)
        ].copy()
        pool["h078_cell_pick_score"] = (
            0.24 * rank01(pool["h076_public_action_gain"].to_numpy())
            + 0.21 * rank01(pool["h076_value_gain"].to_numpy())
            + 0.18 * rank01(pool["latent_hsjepa_score"].to_numpy())
            + 0.12 * rank01(pool["public_score"].to_numpy())
            + 0.08 * rank01(pool["invariant_score"].to_numpy())
            - 0.12 * rank01(pool["latent_shortcut_energy"].to_numpy())
        )
        return best_cells_by_flat(pool, "h078_cell_pick_score")

    raise ValueError(f"unsupported companion expansion: {spec.expansion}")


def route_cascade_cells(
    h076_cells: pd.DataFrame,
    h076_routes: pd.DataFrame,
    seed_rows: pd.DataFrame,
    spec: H078Spec,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    allowed_routes = ["q2_s3_tail", "q2_hardtail", "recovery_route", "s_stage", "s23_core", "s14_edge"]
    if spec.expansion == "fullrow_state_probe":
        allowed_routes = ["full_state", "nonq2_full", "q3_s_stage", "recovery_route", "s_stage"]
    elif spec.expansion == "hybrid_q061_guard":
        allowed_routes = ["full_state", "nonq2_full", "q3_s_stage", "recovery_route", "s_stage", "q2_s3_tail", "q2_hardtail"]

    rows = set(seed_rows["row"].astype(int).tolist())
    route_pool = h076_routes[
        h076_routes["row"].astype(int).isin(rows)
        & h076_routes["route_name"].isin(allowed_routes)
        & (h076_routes["sum_h076_public_contrib"] <= -spec.min_route_action_gain)
        & (h076_routes["mean_h074_bad_same_rank"] <= spec.max_same_rank)
    ].copy()
    if spec.require_outside_h069:
        route_pool = route_pool[route_pool["outside_h069_cells"] > 0]
    if not spec.allow_negative_q061:
        route_pool = route_pool[route_pool["sum_h076_value_gain"] > 0]
    if route_pool.empty:
        return route_pool, h076_cells.iloc[0:0].copy()

    route_pool["route_action_gain"] = -route_pool["sum_h076_public_contrib"].to_numpy(dtype=np.float64)
    route_pool["h078_route_pick_score"] = (
        0.36 * rank01(route_pool["route_action_gain"].to_numpy())
        + 0.18 * rank01(route_pool["h076_route_score"].to_numpy())
        + 0.14 * rank01(route_pool["mean_h074_bad_opp_rank"].to_numpy())
        + 0.10 * rank01(route_pool["outside_h069_cells"].to_numpy())
        + 0.08 * rank01(route_pool["human_route_support"].to_numpy())
        - 0.12 * rank01(route_pool["mean_h074_bad_same_rank"].to_numpy())
        - 0.10 * rank01(route_pool["mean_shortcut_energy"].to_numpy())
    )
    route_pool = route_pool.sort_values(["h078_route_pick_score", "route_action_gain"], ascending=False)

    selected_routes = []
    selected_cells = []
    used_rows: set[int] = set()
    used_flat: set[int] = set()
    subject_counts: dict[str, int] = {}
    total_cells = 0
    for rec in route_pool.to_dict("records"):
        row = int(rec["row"])
        subject = str(rec["subject_id"])
        if row in used_rows:
            continue
        if subject_counts.get(subject, 0) >= spec.max_per_subject:
            continue
        cells = h076_cells[
            h076_cells["h076_policy"].astype(str).eq(str(rec["h076_policy"]))
            & h076_cells["route_id"].astype(str).eq(str(rec["route_id"]))
        ].copy()
        cells = cells[cells["is_h050_null"] == 0]
        cells = cells[cells["h074_bad_same_rank"] <= spec.max_same_rank]
        cells = cells[cells["h076_public_action_gain"] >= spec.min_cell_action_gain]
        if spec.require_outside_h069:
            cells = cells[cells["outside_h069_cell"] > 0]
        if not spec.allow_negative_q061:
            cells = cells[(cells["h076_value_gain"] > 0) & (cells["cell_q061_gain"] > 0)]
        cells = cells[~cells["flat_index"].astype(int).isin(used_flat)]
        if cells.empty:
            continue
        if total_cells + len(cells) > spec.max_cells:
            continue
        selected_routes.append(pd.DataFrame([rec]))
        selected_cells.append(cells)
        used_rows.add(row)
        used_flat.update(map(int, cells["flat_index"].tolist()))
        subject_counts[subject] = subject_counts.get(subject, 0) + 1
        total_cells += int(len(cells))
        if total_cells >= spec.max_cells:
            break
    if not selected_routes:
        return route_pool.iloc[0:0].copy(), h076_cells.iloc[0:0].copy()
    return pd.concat(selected_routes, ignore_index=True), pd.concat(selected_cells, ignore_index=True)


def select_cells(
    h076_cells: pd.DataFrame,
    h076_routes: pd.DataFrame,
    h077_cells: pd.DataFrame,
    spec: H078Spec,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    seed_rows = source_seed_rows(h077_cells, spec.source_candidate, spec.max_seed_rows)
    if seed_rows.empty:
        return seed_rows, h076_routes.iloc[0:0].copy(), h076_cells.iloc[0:0].copy()

    if spec.expansion == "route_cascade_soft":
        route_sel, cell_sel = route_cascade_cells(h076_cells, h076_routes, seed_rows, spec)
    elif spec.expansion in {"hybrid_q061_guard", "fullrow_state_probe"}:
        route_sel, route_cells = route_cascade_cells(h076_cells, h076_routes, seed_rows, spec)
        companion = row_companion_cells(h076_cells, seed_rows, spec)
        cell_sel = pd.concat([route_cells, companion], ignore_index=True) if len(route_cells) else companion
        if len(cell_sel):
            cell_sel = best_cells_by_flat(cell_sel, "h078_cell_pick_score" if "h078_cell_pick_score" in cell_sel.columns else "h076_public_action_gain")
    else:
        route_sel = h076_routes.iloc[0:0].copy()
        cell_sel = row_companion_cells(h076_cells, seed_rows, spec)

    if cell_sel.empty:
        return seed_rows, route_sel, cell_sel

    cell_sel = cell_sel.copy()
    seed_map = seed_rows.set_index("row").to_dict("index")
    cell_sel["h078_seed_public_gain"] = cell_sel["row"].astype(int).map(lambda row: float(seed_map[int(row)]["seed_public_gain"]))
    cell_sel["h078_seed_targets"] = cell_sel["row"].astype(int).map(lambda row: str(seed_map[int(row)]["seed_targets"]))
    cell_sel["h078_is_seed_target"] = cell_sel.apply(
        lambda rec: str(rec["target"]) in str(rec["h078_seed_targets"]).split(","),
        axis=1,
    ).astype(float)
    cell_sel["h078_companion_scale"] = np.where(cell_sel["h078_is_seed_target"] > 0, 1.0, spec.companion_scale)
    cell_sel["h078_effective_prob"] = cell_sel["h076_new_prob"].to_numpy(dtype=np.float64)
    # Companions should state the same row condition without overpowering the
    # seed conflict cells. Interpolate in logit space toward the H076 decoder.
    companion_mask = cell_sel["h078_is_seed_target"].to_numpy(dtype=float) <= 0
    if companion_mask.any():
        base = cell_sel.loc[companion_mask, "h057_prob"].to_numpy(dtype=np.float64)
        target = cell_sel.loc[companion_mask, "h076_new_prob"].to_numpy(dtype=np.float64)
        scale = cell_sel.loc[companion_mask, "h078_companion_scale"].to_numpy(dtype=np.float64)
        new_logit = logit(base) + scale * (logit(target) - logit(base))
        cell_sel.loc[companion_mask, "h078_effective_prob"] = sigmoid(new_logit)

    cell_sel = cell_sel.sort_values(
        ["h078_is_seed_target", "h076_public_action_gain", "h078_seed_public_gain"],
        ascending=False,
    )
    cell_sel = best_cells_by_flat(cell_sel, "h076_public_action_gain")
    if len(cell_sel) > spec.max_cells:
        cell_sel = cell_sel.head(spec.max_cells).copy()
    return seed_rows, route_sel, cell_sel


def evaluate_prob(
    prob: np.ndarray,
    sample: pd.DataFrame,
    mats: dict[str, np.ndarray],
    beta: np.ndarray,
    bad_vecs: dict[str, np.ndarray],
    cell_sel: pd.DataFrame,
    route_sel: pd.DataFrame,
    seed_rows: pd.DataFrame,
    spec: H078Spec,
) -> dict[str, object]:
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
    bad_cos = {f"bad_cos_{H074MOD.safe_stem(name)}": cosine(move_vec, vec) for name, vec in bad_vecs.items()}
    max_bad_cos = max([max(value, 0.0) for value in bad_cos.values()] + [0.0])
    route_counts = route_sel["route_name"].value_counts().to_dict() if len(route_sel) else {}
    policy_counts = cell_sel["h076_policy"].value_counts().to_dict() if len(cell_sel) else {}
    target_counts = cell_sel["target"].value_counts().to_dict() if len(cell_sel) else {}
    meta: dict[str, object] = {
        "candidate_id": "",
        "spec_name": spec.name,
        "source_candidate": spec.source_candidate,
        "expansion": spec.expansion,
        "max_seed_rows": spec.max_seed_rows,
        "max_cells": spec.max_cells,
        "max_per_subject": spec.max_per_subject,
        "min_cell_action_gain": spec.min_cell_action_gain,
        "min_route_action_gain": spec.min_route_action_gain,
        "max_same_rank": spec.max_same_rank,
        "require_outside_h069": spec.require_outside_h069,
        "allow_negative_q061": spec.allow_negative_q061,
        "companion_scale": spec.companion_scale,
        "seed_rows": int(len(seed_rows)),
        "selected_routes": int(len(route_sel)),
        "selected_cells": int(len(cell_sel)),
        "changed_cells_vs_h057": int(changed.sum()),
        "changed_rows_vs_h057": int(changed.any(axis=1).sum()),
        "outside_h069_cells": int(cell_sel["outside_h069_cell"].sum()) if len(cell_sel) else 0,
        "outside_h070_cells": int(cell_sel["outside_h070_cell"].sum()) if len(cell_sel) else 0,
        "seed_target_cells": int(cell_sel["h078_is_seed_target"].sum()) if len(cell_sel) else 0,
        "companion_cells": int((1.0 - cell_sel["h078_is_seed_target"]).sum()) if len(cell_sel) else 0,
        "public_action_pred_delta_vs_h057": float(x @ beta),
        "posterior_delta_vs_h057": float(x.mean()),
        "responsibility_weighted_delta_vs_h057": float(np.dot(row_public, row_delta)),
        "max_positive_bad_cosine": max_bad_cos,
        "sum_h076_public_contrib": float(cell_sel["h076_public_contrib"].sum()) if len(cell_sel) else 0.0,
        "sum_h076_value_gain": float(cell_sel["h076_value_gain"].sum()) if len(cell_sel) else 0.0,
        "mean_h076_public_action_gain": float(cell_sel["h076_public_action_gain"].mean()) if len(cell_sel) else 0.0,
        "mean_h076_value_gain": float(cell_sel["h076_value_gain"].mean()) if len(cell_sel) else 0.0,
        "mean_seed_public_gain": float(seed_rows["seed_public_gain"].mean()) if len(seed_rows) else 0.0,
        "mean_h074_bad_opp_rank": float(cell_sel["h074_bad_opp_rank"].mean()) if len(cell_sel) else 0.0,
        "mean_h074_bad_same_rank": float(cell_sel["h074_bad_same_rank"].mean()) if len(cell_sel) else 1.0,
        "mean_shortcut_energy": float(cell_sel["latent_shortcut_energy"].mean()) if len(cell_sel) else 1.0,
        "mean_public_score": float(cell_sel["public_score"].mean()) if len(cell_sel) else 0.0,
        "mean_invariant_score": float(cell_sel["invariant_score"].mean()) if len(cell_sel) else 0.0,
        "mean_private_safe_score": float(cell_sel["private_safe_score"].mean()) if len(cell_sel) else 0.0,
        "mean_abs_prob_move_vs_h057": float(np.abs(prob - h057).mean()),
        "max_abs_prob_move_vs_h057": float(np.abs(prob - h057).max()),
        "h050_null_selected": int(cell_sel["is_h050_null"].sum()) if len(cell_sel) else 0,
        "selected_subjects": int(cell_sel["subject_id"].nunique()) if len(cell_sel) else 0,
        "selected_rows": ",".join(map(str, sorted(set(cell_sel["row"].astype(int).tolist())))) if len(cell_sel) else "",
        "route_templates": ";".join(f"{k}:{v}" for k, v in sorted(route_counts.items())),
        "policy_templates": ";".join(f"{k}:{v}" for k, v in sorted(policy_counts.items())),
        "target_templates": ";".join(f"{k}:{v}" for k, v in sorted(target_counts.items())),
        **bad_cos,
    }
    for target in TARGETS:
        meta[f"{target}_changed_vs_h057"] = int(changed[:, TARGETS.index(target)].sum())
    return meta


def apply_candidate(
    spec: H078Spec,
    sample: pd.DataFrame,
    mats: dict[str, np.ndarray],
    beta: np.ndarray,
    bad_vecs: dict[str, np.ndarray],
    h076_cells: pd.DataFrame,
    h076_routes: pd.DataFrame,
    h077_cells: pd.DataFrame,
) -> tuple[np.ndarray, dict[str, object], pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    seed_rows, route_sel, cell_sel = select_cells(h076_cells, h076_routes, h077_cells, spec)
    prob = mats["h057"].copy()
    for rec in cell_sel.to_dict("records"):
        prob[int(rec["row"]), int(rec["target_index"])] = float(rec["h078_effective_prob"])
    prob = clip_prob(prob)
    meta = evaluate_prob(prob, sample, mats, beta, bad_vecs, cell_sel, route_sel, seed_rows, spec)
    return prob, meta, seed_rows, route_sel, cell_sel


def candidate_sweep(
    sample: pd.DataFrame,
    mats: dict[str, np.ndarray],
    beta: np.ndarray,
    bad_vecs: dict[str, np.ndarray],
    h076_cells: pd.DataFrame,
    h076_routes: pd.DataFrame,
    h077_cells: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, np.ndarray], pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rows = []
    probs: dict[str, np.ndarray] = {}
    seed_rows_all = []
    route_rows_all = []
    cell_rows_all = []
    seen: set[str] = set()
    for spec in candidate_specs():
        prob, meta, seed_rows, route_sel, cell_sel = apply_candidate(
            spec,
            sample,
            mats,
            beta,
            bad_vecs,
            h076_cells,
            h076_routes,
            h077_cells,
        )
        if meta["changed_cells_vs_h057"] <= 0:
            continue
        digest = short_hash(prob)
        if digest in seen:
            continue
        seen.add(digest)
        cid = f"h078_{spec.expansion}_{digest}"
        meta["candidate_id"] = cid
        meta["hash"] = digest
        rows.append(meta)
        probs[cid] = prob
        if len(seed_rows):
            seed_rows_all.append(seed_rows.assign(candidate_id=cid))
        if len(route_sel):
            route_rows_all.append(route_sel.assign(candidate_id=cid))
        if len(cell_sel):
            cell_rows_all.append(cell_sel.assign(candidate_id=cid))

    cand = pd.DataFrame(rows)
    if cand.empty:
        raise RuntimeError("no H078 candidates generated")

    cand["action_rank"] = rank01(-cand["public_action_pred_delta_vs_h057"].to_numpy())
    cand["responsibility_rank"] = rank01(-cand["responsibility_weighted_delta_vs_h057"].to_numpy())
    cand["posterior_rank"] = rank01(-cand["posterior_delta_vs_h057"].to_numpy())
    cand["same_avoid_rank"] = rank01(-cand["mean_h074_bad_same_rank"].to_numpy())
    cand["bad_avoid_rank"] = rank01(-cand["max_positive_bad_cosine"].to_numpy())
    cand["shortcut_avoid_rank"] = rank01(-cand["mean_shortcut_energy"].to_numpy())
    cand["row_state_scale_rank"] = rank01(np.minimum(cand["changed_cells_vs_h057"].to_numpy(), 96))
    cand["companion_ratio"] = cand["companion_cells"] / cand["changed_cells_vs_h057"].clip(lower=1)
    cand["outside_h069_ratio"] = cand["outside_h069_cells"] / cand["changed_cells_vs_h057"].clip(lower=1)
    cand["posterior_violation"] = np.maximum(cand["posterior_delta_vs_h057"].to_numpy(), 0.0)
    cand["h078_score"] = (
        0.28 * cand["action_rank"]
        + 0.14 * cand["responsibility_rank"]
        + 0.11 * cand["same_avoid_rank"]
        + 0.10 * cand["bad_avoid_rank"]
        + 0.10 * cand["shortcut_avoid_rank"]
        + 0.09 * cand["row_state_scale_rank"]
        + 0.07 * cand["companion_ratio"].clip(0, 1)
        + 0.05 * cand["outside_h069_ratio"].clip(0, 1)
        + 0.04 * rank01(cand["mean_private_safe_score"].to_numpy())
        - 0.10 * (cand["h050_null_selected"] > 0).astype(float)
        - 0.08 * (cand["max_abs_prob_move_vs_h057"] > 0.32).astype(float)
        - 0.07 * cand["posterior_violation"].clip(0, 0.005) / 0.005
    )
    cand = cand.sort_values(["h078_score", "public_action_pred_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True)
    for _, rec in cand.iterrows():
        cid = str(rec["candidate_id"])
        path = OUT / f"submission_{cid}.csv"
        H071MOD.write_submission(sample, probs[cid], path)
        cand.loc[cand["candidate_id"].eq(cid), "file"] = path.name
        cand.loc[cand["candidate_id"].eq(cid), "resolved_path"] = str(path.resolve())

    seed_diag = pd.concat(seed_rows_all, ignore_index=True) if seed_rows_all else pd.DataFrame()
    route_diag = pd.concat(route_rows_all, ignore_index=True) if route_rows_all else pd.DataFrame()
    cell_diag = pd.concat(cell_rows_all, ignore_index=True) if cell_rows_all else pd.DataFrame()
    return cand, probs, seed_diag, route_diag, cell_diag


def validate_submission(path: Path, sample: pd.DataFrame, h057_prob: np.ndarray) -> dict[str, object]:
    return H071MOD.validate_submission(path, sample, h057_prob)


def write_report(
    cand: pd.DataFrame,
    seed_diag: pd.DataFrame,
    route_diag: pd.DataFrame,
    cell_diag: pd.DataFrame,
    decision: pd.DataFrame,
) -> None:
    cell_cols = [
        "candidate_id",
        "row",
        "target",
        "route_name",
        "h076_policy",
        "h076_decoder",
        "h078_is_seed_target",
        "h076_public_action_gain",
        "h076_value_gain",
        "h057_prob",
        "h076_new_prob",
        "h078_effective_prob",
        "h074_bad_same_rank",
        "h074_bad_opp_rank",
        "latent_shortcut_energy",
        "outside_h069_cell",
    ]
    route_cols = [
        "candidate_id",
        "h076_policy",
        "route_id",
        "row",
        "subject_id",
        "sleep_date",
        "route_name",
        "targets",
        "n_cells",
        "sum_h076_public_contrib",
        "sum_h076_value_gain",
        "h076_route_score",
        "mean_h074_bad_same_rank",
        "mean_h074_bad_opp_rank",
        "outside_h069_cells",
    ]
    parts = [
        "# H078 Hard-Tail Row-State Cascade HS-JEPA",
        "",
        "Question: are H077 hard-tail cells isolated target exceptions, or visible anchors of a whole-row human state?",
        "",
        "Worldview:",
        "",
        "- H077 found sparse Q2/S-stage/recovery cells that the public-action sensor likes while q061 rejects;",
        "- H078 treats those cells as context and predicts a row-level correction representation;",
        "- if public improves, HS-JEPA should decode hidden state at row/day granularity;",
        "- if public worsens, the hard-tail signal is cell-local and row-state expansion is a false cascade.",
        "",
        "Candidates:",
        "",
        md_table(cand, 30),
        "",
        "Seed rows:",
        "",
        md_table(seed_diag.head(60), 60) if len(seed_diag) else "(none)",
        "",
        "Selected routes:",
        "",
        md_table(route_diag[[c for c in route_cols if c in route_diag.columns]].head(80), 80) if len(route_diag) else "(none)",
        "",
        "Selected cells:",
        "",
        md_table(cell_diag[[c for c in cell_cols if c in cell_diag.columns]].head(120), 120) if len(cell_diag) else "(none)",
        "",
        "Decision:",
        "",
        md_table(decision),
    ]
    (OUT / "h078_report.md").write_text("\n".join(parts))


def main() -> None:
    cleanup_previous_outputs()
    sample, _latent, mats, beta, bad_vecs = H071MOD.load_runtime()
    h076_cells, h076_routes, _h077_cand, h077_cells = load_artifacts()
    cand, probs, seed_diag, route_diag, cell_diag = candidate_sweep(
        sample,
        mats,
        beta,
        bad_vecs,
        h076_cells,
        h076_routes,
        h077_cells,
    )

    bigbet = cand[
        (cand["h050_null_selected"] == 0)
        & (cand["public_action_pred_delta_vs_h057"] <= -0.0020)
        & (cand["changed_cells_vs_h057"].between(24, 110))
        & (cand["companion_cells"] >= 8)
        & (cand["max_positive_bad_cosine"] <= 0.006)
    ].sort_values(["public_action_pred_delta_vs_h057", "h078_score"], ascending=[True, False])
    if len(bigbet):
        selected = bigbet.iloc[0].copy()
        decision_name = "promote_rowstate_cascade_bigbet"
        worldview = "hard-tail conflict cells are anchors of a row-level hidden human state"
    else:
        selected = cand.iloc[0].copy()
        decision_name = "promote_rowstate_cascade_diagnostic"
        worldview = "row-state cascade did not clear the full big-bet gate but is the best falsification sensor"

    selected_file = OUT / str(selected["file"])
    digest = str(selected["hash"])
    root_file = ROOT / f"submission_h078_hardtail_rowstate_{digest}_uploadsafe.csv"
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

    cand.to_csv(OUT / "h078_candidate_scores.csv", index=False)
    seed_diag.to_csv(OUT / "h078_seed_rows.csv", index=False)
    route_diag.to_csv(OUT / "h078_selected_routes.csv", index=False)
    cell_diag.to_csv(OUT / "h078_selected_cells.csv", index=False)
    decision.to_csv(OUT / "h078_decision.csv", index=False)
    write_report(cand, seed_diag, route_diag, cell_diag, decision)
    print(
        decision[
            [
                "selected_candidate_id",
                "root_uploadsafe_path",
                "decision",
                "expansion",
                "changed_cells_vs_h057",
                "changed_rows_vs_h057",
                "seed_rows",
                "companion_cells",
                "public_action_pred_delta_vs_h057",
                "posterior_delta_vs_h057",
                "responsibility_weighted_delta_vs_h057",
                "max_positive_bad_cosine",
                "max_abs_prob_move_vs_h057",
                "selected_rows",
                "target_templates",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
