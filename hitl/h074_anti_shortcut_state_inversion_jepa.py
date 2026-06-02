#!/usr/bin/env python3
"""H074: anti-shortcut state inversion HS-JEPA.

H073 narrowed the human-social layer:

    C_human + C_route -> z_action_health / z_shortcut -> z_assignment

H074 tests the opposite side of the same representation.  Instead of asking
"which cells look good?", it asks whether known public-bad worlds reveal a
negative boundary whose opposite direction is action-grade.

Core target representation:

    bad submissions -> z_shortcut
    cells where bad worlds move opposite to q061 -> z_anti_shortcut
    z_anti_shortcut + action-health -> route assignment -> correction field

This is a big-bet diagnostic.  If it wins, HS-JEPA should treat failed
submissions as contrastive target representations, not merely as vetoes.
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
OUT = HITL / "h074_anti_shortcut_state_inversion_jepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
S_TARGETS = ["S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1.0e-9
TOL = 1.0e-12


def import_module(path: Path, name: str) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


H073MOD = import_module(HITL / "h073_human_action_health_bridge_jepa.py", "h073mod_for_h074")
H071MOD = H073MOD.H071MOD


@dataclass(frozen=True)
class H074Spec:
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
    allowed_routes: tuple[str, ...]


def rank01(values: np.ndarray, high: bool = True) -> np.ndarray:
    values = np.asarray(values, dtype=np.float64)
    if values.size == 0:
        return values
    if np.nanstd(values) < 1.0e-12:
        return np.full_like(values, 0.5, dtype=np.float64)
    return H071MOD.rank01(np.nan_to_num(values, nan=np.nanmedian(values)), high=high)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1.0e-12))


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return H071MOD.md_table(frame, n)


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h074_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h074_antishortcut_inversion_*_uploadsafe.csv"):
        path.unlink()


def safe_stem(name: str) -> str:
    return Path(name).stem.replace(".", "_").replace("-", "_")[:26]


def load_h073_or_rebuild(
    sample: pd.DataFrame,
    latent: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, pd.DataFrame]]:
    """Load H073 cells/routes if present; otherwise rebuild them reproducibly."""

    routes, cells_by_route = H071MOD.build_route_candidates(latent)
    cells_path = H073MOD.OUT / "h073_cell_scores.csv"
    routes_path = H073MOD.OUT / "h073_route_candidates.csv"
    if cells_path.exists() and routes_path.exists():
        cells = pd.read_csv(cells_path)
        h073_routes = pd.read_csv(routes_path)
        score_cols = [
            "flat_index",
            "h073_bridge_cell_score",
            "h073_story_action_energy",
            "story_to_h068_selected_full",
            "story_to_h068_health_full",
            "story_route_to_h068_selected_full",
            "story_route_to_h068_health_full",
            "story_route_to_shortcut_full",
            "story_to_shortcut_full",
        ]
        score_cols = [col for col in score_cols if col in cells.columns]
        score_map = cells[score_cols].copy()
        route_cells = {}
        for route_id, frame in cells_by_route.items():
            route_cells[route_id] = frame.merge(score_map, on="flat_index", how="left").fillna(0.0)
        return cells, h073_routes, route_cells

    scored_latent = H071MOD.add_cell_scores(latent)
    cells, h072_routes, _route_cells = H073MOD.build_cell_frame(sample, scored_latent, routes, cells_by_route)
    cells, _model_metrics, _fold_metrics, _models = H073MOD.add_bridge_predictions(cells)
    h073_routes, h073_cells_by_route = H073MOD.update_route_scores(h072_routes, cells_by_route, cells)
    return cells, h073_routes, h073_cells_by_route


def add_bad_opposition_features(
    cells: pd.DataFrame,
    mats: dict[str, np.ndarray],
    bad_vecs: dict[str, np.ndarray],
) -> pd.DataFrame:
    base_dir = np.sign((H071MOD.logit(mats["q061"]) - H071MOD.logit(mats["h057"])).reshape(-1))
    base_dir = np.where(base_dir == 0, 1.0, base_dir)
    same_sum = np.zeros_like(base_dir, dtype=np.float64)
    opp_sum = np.zeros_like(base_dir, dtype=np.float64)
    same_top = np.zeros_like(base_dir, dtype=np.float64)
    opp_top = np.zeros_like(base_dir, dtype=np.float64)
    per_anchor: dict[str, np.ndarray] = {}

    for name, vec in bad_vecs.items():
        signed = base_dir * np.asarray(vec, dtype=np.float64)
        same = np.maximum(signed, 0.0)
        opp = np.maximum(-signed, 0.0)
        same_sum += same
        opp_sum += opp
        same_top += (same >= np.quantile(same, 0.90)).astype(float)
        opp_top += (opp >= np.quantile(opp, 0.90)).astype(float)
        stem = safe_stem(name)
        per_anchor[f"h074_same_{stem}"] = same
        per_anchor[f"h074_opp_{stem}"] = opp

    denom = max(float(len(bad_vecs)), 1.0)
    same_raw = same_sum / denom
    opp_raw = opp_sum / denom
    same_rate = same_top / denom
    opp_rate = opp_top / denom
    margin_raw = opp_raw - same_raw
    table = pd.DataFrame(
        {
            "flat_index": np.arange(base_dir.size, dtype=int),
            "h074_bad_same_raw": same_raw,
            "h074_bad_opp_raw": opp_raw,
            "h074_bad_margin_raw": margin_raw,
            "h074_bad_same_log": np.log1p(same_raw),
            "h074_bad_opp_log": np.log1p(opp_raw),
            "h074_bad_margin_log": np.log1p(np.maximum(margin_raw, 0.0)),
            "h074_bad_same_rate": same_rate,
            "h074_bad_opp_rate": opp_rate,
            "h074_bad_same_rank": rank01(np.log1p(same_raw)),
            "h074_bad_opp_rank": rank01(np.log1p(opp_raw)),
            "h074_bad_margin_rank": rank01(np.log1p(np.maximum(margin_raw, 0.0))),
            **per_anchor,
        }
    )
    for col in list(table.columns):
        if col.startswith("h074_opp_submission_e216"):
            table["h074_e216_opp_rank"] = rank01(np.log1p(table[col].to_numpy(dtype=float)))
        if col.startswith("h074_opp_submission_e323"):
            table["h074_e323_opp_rank"] = rank01(np.log1p(table[col].to_numpy(dtype=float)))
        if col.startswith("h074_opp_submission_h010"):
            table["h074_h010_opp_rank"] = rank01(np.log1p(table[col].to_numpy(dtype=float)))
    for col in ["h074_e216_opp_rank", "h074_e323_opp_rank", "h074_h010_opp_rank"]:
        if col not in table:
            table[col] = 0.5

    out = cells.merge(table, on="flat_index", how="left", validate="one_to_one").fillna(0.0)
    return compute_h074_cell_score(out)


def compute_h074_cell_score(cells: pd.DataFrame) -> pd.DataFrame:
    out = cells.copy()
    story_shortcut = out.get("story_route_to_shortcut_full", pd.Series(0.5, index=out.index)).to_numpy(dtype=float)
    q2 = (out["target"].astype(str) == "Q2").to_numpy(dtype=float)
    target_s = out["target"].isin(S_TARGETS).to_numpy(dtype=float)

    out["h074_positive_energy"] = (
        0.19 * rank01(out["h073_bridge_cell_score"].to_numpy())
        + 0.17 * rank01(out["h068_cell_health"].to_numpy())
        + 0.14 * rank01(out["public_score"].to_numpy())
        + 0.12 * rank01(out["invariant_score"].to_numpy())
        + 0.10 * rank01(out["cell_assignment_score"].to_numpy())
        + 0.09 * rank01(out["cell_q061_gain"].to_numpy())
        + 0.06 * out["outside_h069_cell"].to_numpy(dtype=float)
        + 0.04 * out["outside_h070_cell"].to_numpy(dtype=float)
        + 0.03 * target_s
    )
    out["h074_negative_space"] = (
        0.33 * out["h074_bad_opp_rank"].to_numpy(dtype=float)
        + 0.17 * out["h074_bad_margin_rank"].to_numpy(dtype=float)
        + 0.10 * out["h074_bad_opp_rate"].to_numpy(dtype=float)
        + 0.06 * out["h074_e216_opp_rank"].to_numpy(dtype=float)
        - 0.23 * out["h074_bad_same_rank"].to_numpy(dtype=float)
        - 0.15 * rank01(out["latent_shortcut_energy"].to_numpy())
        - 0.10 * rank01(story_shortcut)
        - 0.09 * rank01(out["bad_pressure_rank"].to_numpy())
    )
    out["h074_cell_score"] = (
        0.58 * rank01(out["h074_positive_energy"].to_numpy())
        + 0.42 * rank01(out["h074_negative_space"].to_numpy())
        - 0.07 * q2
        - 0.08 * out["h074_bad_same_rate"].to_numpy(dtype=float)
        - 0.12 * out["is_h050_null"].to_numpy(dtype=float)
    )
    out.loc[out["cell_q061_gain"] <= 0, "h074_cell_score"] -= 0.85
    out.loc[out["is_h050_null"] > 0, "h074_cell_score"] -= 0.35
    return out.replace([np.inf, -np.inf], 0.0).fillna(0.0)


def null_feature_shuffle(cells: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    cols = [
        "h074_bad_same_rank",
        "h074_bad_opp_rank",
        "h074_bad_margin_rank",
        "h074_bad_same_rate",
        "h074_bad_opp_rate",
        "h074_e216_opp_rank",
        "h074_e323_opp_rank",
        "h074_h010_opp_rank",
    ]
    out = cells.copy()
    for target in out["target"].astype(str).unique():
        idx = out.index[out["target"].astype(str) == target].to_numpy()
        perm = rng.permutation(idx)
        out.loc[idx, cols] = cells.loc[perm, cols].to_numpy()
    return compute_h074_cell_score(out)


def selection_metrics(cells: pd.DataFrame, score_col: str, top_n: int) -> dict[str, object]:
    valid = cells[(cells["cell_q061_gain"] > 0) & (cells["is_h050_null"] == 0)].copy()
    selected = valid.sort_values(score_col, ascending=False).head(top_n)
    return {
        "top_n": int(top_n),
        "selected_cells": int(len(selected)),
        "selected_rows": int(selected["row"].nunique()),
        "mean_true_opp_rank": float(selected["h074_bad_opp_rank"].mean()),
        "mean_true_same_rank": float(selected["h074_bad_same_rank"].mean()),
        "mean_true_margin_rank": float(selected["h074_bad_margin_rank"].mean()),
        "mean_h073_bridge": float(selected["h073_bridge_cell_score"].mean()),
        "mean_h068_health": float(selected["h068_cell_health"].mean()),
        "mean_public": float(selected["public_score"].mean()),
        "mean_invariant": float(selected["invariant_score"].mean()),
        "mean_shortcut_energy": float(selected["latent_shortcut_energy"].mean()),
        "mean_cell_gain": float(selected["cell_q061_gain"].mean()),
        "q2_cells": int((selected["target"] == "Q2").sum()),
        "h050_null": int(selected["is_h050_null"].sum()),
        "selected_flat": ",".join(map(str, selected["flat_index"].astype(int).tolist())),
    }


def anti_shortcut_null_stress(cells: pd.DataFrame, n_iter: int = 240) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(74074)
    top_n_values = [360, 520, 700]
    real_rows = []
    real_sets: dict[int, set[int]] = {}
    for top_n in top_n_values:
        row = selection_metrics(cells, "h074_cell_score", top_n)
        row.update({"iter": -1, "kind": "real"})
        real_rows.append(row)
        real_sets[top_n] = set(map(int, str(row["selected_flat"]).split(","))) if row["selected_flat"] else set()

    rows = list(real_rows)
    for i in range(n_iter):
        shuffled = null_feature_shuffle(cells, rng)
        for top_n in top_n_values:
            row = selection_metrics(shuffled, "h074_cell_score", top_n)
            selected = set(map(int, str(row["selected_flat"]).split(","))) if row["selected_flat"] else set()
            row.update(
                {
                    "iter": i,
                    "kind": "target_stratified_bad_axis_shuffle",
                    "overlap_with_real": len(selected & real_sets[top_n]) / max(len(real_sets[top_n]), 1),
                }
            )
            rows.append(row)

    stress = pd.DataFrame(rows)
    summary_rows = []
    for top_n in top_n_values:
        real = stress[(stress["iter"] < 0) & (stress["top_n"] == top_n)].iloc[0]
        null = stress[(stress["iter"] >= 0) & (stress["top_n"] == top_n)]
        for metric in [
            "mean_true_opp_rank",
            "mean_true_same_rank",
            "mean_true_margin_rank",
            "mean_h073_bridge",
            "mean_shortcut_energy",
            "mean_cell_gain",
        ]:
            vals = null[metric].to_numpy(dtype=float)
            rv = float(real[metric])
            summary_rows.append(
                {
                    "top_n": int(top_n),
                    "metric": metric,
                    "real": rv,
                    "null_mean": float(np.nanmean(vals)),
                    "null_std": float(np.nanstd(vals)),
                    "null_p95": float(np.nanpercentile(vals, 95)),
                    "z_vs_null": float((rv - np.nanmean(vals)) / (np.nanstd(vals) + EPS)),
                    "p_ge_real": float(np.mean(vals >= rv)),
                }
            )
    return stress.drop(columns=["selected_flat"]), pd.DataFrame(summary_rows)


def merge_h074_scores_into_routes(
    routes: pd.DataFrame,
    cells_by_route: dict[str, pd.DataFrame],
    cells: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    score_cols = [
        "flat_index",
        "h074_cell_score",
        "h074_positive_energy",
        "h074_negative_space",
        "h074_bad_same_rank",
        "h074_bad_opp_rank",
        "h074_bad_margin_rank",
        "h074_e216_opp_rank",
        "h074_bad_same_rate",
        "h074_bad_opp_rate",
    ]
    score_map = cells[score_cols].copy()
    route_rows = []
    out_cells: dict[str, pd.DataFrame] = {}
    for rec in routes.to_dict("records"):
        route_id = str(rec["route_id"])
        if route_id not in cells_by_route:
            continue
        use = cells_by_route[route_id].merge(score_map, on="flat_index", how="left").fillna(0.0)
        out_cells[route_id] = use
        route_rows.append(
            {
                **rec,
                "mean_h074_cell_score": float(use["h074_cell_score"].mean()),
                "sum_h074_cell_score": float(use["h074_cell_score"].sum()),
                "mean_h074_positive_energy": float(use["h074_positive_energy"].mean()),
                "mean_h074_negative_space": float(use["h074_negative_space"].mean()),
                "mean_h074_bad_opp_rank": float(use["h074_bad_opp_rank"].mean()),
                "mean_h074_bad_same_rank": float(use["h074_bad_same_rank"].mean()),
                "mean_h074_bad_margin_rank": float(use["h074_bad_margin_rank"].mean()),
                "mean_h074_e216_opp_rank": float(use["h074_e216_opp_rank"].mean()),
            }
        )
    out = pd.DataFrame(route_rows)
    out["h074_route_score"] = (
        0.31 * rank01(out["sum_h074_cell_score"].to_numpy() / np.sqrt(out["n_cells"].clip(lower=1)))
        + 0.18 * rank01(out["mean_h074_bad_opp_rank"].to_numpy())
        + 0.13 * rank01(out["mean_h074_negative_space"].to_numpy())
        + 0.12 * rank01(out["h073_route_score"].to_numpy() if "h073_route_score" in out else out["assignment_route_score"].to_numpy())
        + 0.10 * rank01(out["assignment_route_score"].to_numpy())
        + 0.07 * rank01(out["mean_public_score"].to_numpy())
        + 0.06 * rank01(out["mean_invariant_score"].to_numpy())
        + 0.05 * rank01(out["outside_h069_cells"].to_numpy())
        - 0.13 * rank01(out["mean_h074_bad_same_rank"].to_numpy())
        - 0.08 * rank01(out["mean_shortcut_energy"].to_numpy())
    )
    out.loc[out["mean_h074_bad_same_rank"] > 0.72, "h074_route_score"] -= 0.10
    out.loc[out["mean_shortcut_energy"] > 0.65, "h074_route_score"] -= 0.08
    return out.sort_values(["h074_route_score", "mean_h074_bad_opp_rank"], ascending=[False, False]).reset_index(drop=True), out_cells


def h074_specs() -> list[H074Spec]:
    all_routes = tuple(H071MOD.ROUTES)
    stage_routes = ("s_stage", "s23_core", "s14_edge", "q3_s_stage", "recovery_route", "nonq2_full")
    row_routes = ("full_state", "nonq2_full", "q3_s_stage", "s_stage", "recovery_route", "q_subjective")
    row_broad_routes = (
        "full_state",
        "nonq2_full",
        "q3_s_stage",
        "s_stage",
        "recovery_route",
        "q_subjective",
        "q2_hardtail",
        "q2_s3_tail",
    )
    return [
        H074Spec("row_broad", 1100, 250, 90, 32, 0.48, 0.30, "outside_h069", 1.0, "logit", row_broad_routes),
        H074Spec("row_broad", 1100, 250, 90, 32, 0.42, 0.30, "outside_h069", 1.0, "logit", row_broad_routes),
        H074Spec("row_broad", 1100, 250, 90, 32, 0.42, 0.30, "anti_shortcut", 1.0, "logit", row_broad_routes),
        H074Spec("negative_space_broad", 1100, 250, 70, 32, 0.42, 0.30, "outside_h069", 1.0, "logit", all_routes),
        H074Spec("negative_space_big", 1080, 235, 52, 26, 0.56, 0.32, "outside_h069", 1.0, "logit", all_routes),
        H074Spec("negative_space_big", 900, 220, 36, 25, 0.60, 0.35, "bad_opposition", 1.0, "logit", all_routes),
        H074Spec("bad_opposition_fullvector", 980, 225, 40, 25, 0.57, 0.33, "outside_h069", 1.0, "logit", row_routes),
        H074Spec("bad_opposition_fullvector", 760, 190, 28, 22, 0.62, 0.36, "bad_opposition", 1.0, "logit", row_routes),
        H074Spec("anti_shortcut_stage", 900, 225, 0, 26, 0.55, 0.31, "anti_shortcut", 1.0, "logit", stage_routes),
        H074Spec("anti_shortcut_stage", 700, 205, 0, 24, 0.62, 0.35, "bad_opposition", 1.0, "logit", stage_routes),
        H074Spec("e216_inverse_stage", 760, 210, 0, 24, 0.54, 0.30, "e216_inverse", 1.0, "logit", stage_routes),
        H074Spec("low_same_route", 720, 205, 24, 24, 0.58, 0.34, "anti_shortcut", 1.0, "logit", all_routes),
    ]


def allowed_by_spec(spec: H074Spec, rec: dict[str, object]) -> bool:
    if spec.allowed_routes and str(rec["route_name"]) not in spec.allowed_routes:
        return False
    if float(rec["h074_route_score"]) < spec.min_route_score:
        return False
    if spec.novelty == "outside_h069":
        return int(rec["outside_h069_cells"]) >= max(1, int(rec["n_cells"]) // 2)
    if spec.novelty == "bad_opposition":
        return float(rec["mean_h074_bad_opp_rank"]) >= 0.62 and float(rec["mean_h074_bad_same_rank"]) <= 0.58
    if spec.novelty == "anti_shortcut":
        return float(rec["mean_h074_bad_same_rank"]) <= 0.48 and float(rec["mean_shortcut_energy"]) <= 0.50
    if spec.novelty == "e216_inverse":
        return float(rec["mean_h074_e216_opp_rank"]) >= 0.62 and float(rec["mean_h074_bad_same_rank"]) <= 0.62
    return True


def select_assignments(
    spec: H074Spec,
    routes: pd.DataFrame,
    cells_by_route: dict[str, pd.DataFrame],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    pool = routes[routes.apply(lambda row: allowed_by_spec(spec, row.to_dict()), axis=1)].copy()
    pool = pool.sort_values(["h074_route_score", "mean_h074_bad_opp_rank", "assignment_route_score"], ascending=False)
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
        cells = cells[cells["h074_cell_score"] >= spec.min_cell_score]
        cells = cells[cells["cell_q061_gain"] > 0]
        cells = cells[cells["is_h050_null"] == 0]
        cells = cells[cells["h074_bad_same_rank"] <= 0.82]
        if spec.novelty in {"bad_opposition", "e216_inverse"}:
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
    spec: H074Spec,
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
    moved = H071MOD.move_toward(h057_prob, q061, spec.alpha, spec.mode)
    for rec in cell_sel.to_dict("records"):
        prob[int(rec["row"]), int(rec["target_index"])] = moved[int(rec["row"]), int(rec["target_index"])]
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
    bad_cos = {f"bad_cos_{safe_stem(name)}": cosine(move_vec, vec) for name, vec in bad_vecs.items()}
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
        "mode": spec.mode,
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
        "mean_h074_route_score": float(route_sel["h074_route_score"].mean()) if len(route_sel) else 0.0,
        "mean_h074_cell_score": float(cell_sel["h074_cell_score"].mean()) if len(cell_sel) else 0.0,
        "mean_h074_negative_space": float(cell_sel["h074_negative_space"].mean()) if len(cell_sel) else 0.0,
        "mean_h074_bad_opp_rank": float(cell_sel["h074_bad_opp_rank"].mean()) if len(cell_sel) else 0.0,
        "mean_h074_bad_same_rank": float(cell_sel["h074_bad_same_rank"].mean()) if len(cell_sel) else 1.0,
        "mean_h074_bad_margin_rank": float(cell_sel["h074_bad_margin_rank"].mean()) if len(cell_sel) else 0.0,
        "mean_h074_e216_opp_rank": float(cell_sel["h074_e216_opp_rank"].mean()) if len(cell_sel) else 0.0,
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
    null_summary: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    rows = []
    probs: dict[str, np.ndarray] = {}
    seen: set[str] = set()
    opp_z = float(null_summary[(null_summary["top_n"] == 520) & (null_summary["metric"] == "mean_true_opp_rank")]["z_vs_null"].iloc[0])
    for spec in h074_specs():
        prob, meta = apply_candidate(spec, sample, mats, routes, cells_by_route, beta, bad_vecs)
        if meta["changed_cells_vs_h057"] < 120 or meta["selected_routes"] < 20:
            continue
        digest = short_hash(prob)
        if digest in seen:
            continue
        seen.add(digest)
        cid = f"h074_{spec.family}_{spec.novelty}_c{spec.max_cells}_r{spec.max_rows}_q2{spec.q2_cap}_{digest}"
        meta["candidate_id"] = cid
        meta["hash"] = digest
        meta["null_opp_z_top520"] = opp_z
        rows.append(meta)
        probs[cid] = prob
    cand = pd.DataFrame(rows)
    if cand.empty:
        raise RuntimeError("no H074 candidates generated")

    cand["action_rank"] = rank01(-cand["public_action_pred_delta_vs_h057"].to_numpy())
    cand["posterior_rank"] = rank01(-cand["posterior_delta_vs_h057"].to_numpy())
    cand["responsibility_rank"] = rank01(-cand["responsibility_weighted_delta_vs_h057"].to_numpy())
    cand["h074_route_rank"] = rank01(cand["mean_h074_route_score"].to_numpy())
    cand["h074_cell_rank"] = rank01(cand["mean_h074_cell_score"].to_numpy())
    cand["opp_rank"] = rank01(cand["mean_h074_bad_opp_rank"].to_numpy())
    cand["margin_rank"] = rank01(cand["mean_h074_bad_margin_rank"].to_numpy())
    cand["same_avoid_rank"] = rank01(-cand["mean_h074_bad_same_rank"].to_numpy())
    cand["shortcut_avoid_rank"] = rank01(-cand["mean_shortcut_energy"].to_numpy())
    cand["bad_avoid_rank"] = rank01(-cand["max_positive_bad_cosine"].to_numpy())
    cand["outside_h069_ratio"] = cand["outside_h069_cells"] / cand["changed_cells_vs_h057"].clip(lower=1)
    cand["q2_risk"] = cand["Q2_changed_vs_h057"] / cand["changed_cells_vs_h057"].clip(lower=1)
    cand["route_diversity"] = cand["route_templates"].map(lambda text: len(str(text).split(";")) if text else 0)
    cand["bigbet_scale_score"] = ((-cand["public_action_pred_delta_vs_h057"] - 0.00085) / 0.00125).clip(0.0, 1.0)
    cand["h074_score"] = (
        0.19 * cand["action_rank"]
        + 0.13 * cand["responsibility_rank"]
        + 0.13 * cand["h074_route_rank"]
        + 0.11 * cand["h074_cell_rank"]
        + 0.11 * cand["opp_rank"]
        + 0.08 * cand["margin_rank"]
        + 0.08 * cand["same_avoid_rank"]
        + 0.07 * cand["outside_h069_ratio"].clip(0, 1)
        + 0.06 * cand["shortcut_avoid_rank"]
        + 0.05 * cand["bigbet_scale_score"]
        + 0.04 * cand["posterior_rank"]
        + 0.03 * cand["bad_avoid_rank"]
        + 0.02 * (cand["route_diversity"] / cand["route_diversity"].clip(lower=1).max()).clip(0, 1)
        - 0.06 * cand["q2_risk"]
        - 0.07 * (cand["h050_null_selected"] > 0).astype(float)
    )
    cand = cand.sort_values(["h074_score", "public_action_pred_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True)
    for _, rec in cand.head(80).iterrows():
        cid = str(rec["candidate_id"])
        path = OUT / f"submission_{cid}.csv"
        H071MOD.write_submission(sample, probs[cid], path)
        cand.loc[cand["candidate_id"].eq(cid), "file"] = path.name
        cand.loc[cand["candidate_id"].eq(cid), "resolved_path"] = str(path.resolve())
    return cand, probs


def validate_submission(path: Path, sample: pd.DataFrame, h057_prob: np.ndarray) -> dict[str, object]:
    return H071MOD.validate_submission(path, sample, h057_prob)


def write_report(
    null_summary: pd.DataFrame,
    routes: pd.DataFrame,
    cand: pd.DataFrame,
    decision: pd.DataFrame,
) -> None:
    report = "\n".join(
        [
            "# H074 Anti-Shortcut State Inversion HS-JEPA",
            "",
            "Question: can known public-bad submissions be used as contrastive target representations, not merely vetoes?",
            "",
            "Design:",
            "",
            "- positive context: H071/H073 route assignment, H068 action-health, H069 public/private factors;",
            "- negative context: known public-bad anchor movement vectors;",
            "- target representation: cells where bad anchors move opposite to the q061 direction (`bad-opposition`);",
            "- decoder: anti-shortcut cell score -> route assignment -> H061 q061 correction;",
            "- stress: target-stratified bad-axis shuffle, H050-null avoidance, bad-anchor cosine.",
            "",
            "Bad-axis shuffle summary:",
            "",
            md_table(null_summary, 30),
            "",
            "Top H074 routes:",
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
                        "h074_route_score",
                        "mean_h074_cell_score",
                        "mean_h074_bad_opp_rank",
                        "mean_h074_bad_same_rank",
                        "mean_h074_e216_opp_rank",
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
            "- If H074 wins by >= 0.001, failed public submissions are contrastive HS-JEPA target representations.",
            "- If H074 is neutral while H071/H073 win, bad worlds are useful vetoes but not positive inverse evidence.",
            "- If H074 loses badly, bad-opposition is a numerical artifact or a bad private/public extrapolation.",
            "",
        ]
    )
    (OUT / "h074_report.md").write_text(report)


def main() -> None:
    cleanup_previous_outputs()
    sample, latent, mats, beta, bad_vecs = H071MOD.load_runtime()
    cells, h073_routes, h073_cells_by_route = load_h073_or_rebuild(sample, latent)
    cells = add_bad_opposition_features(cells, mats, bad_vecs)
    null_stress, null_summary = anti_shortcut_null_stress(cells)
    h074_routes, h074_cells_by_route = merge_h074_scores_into_routes(h073_routes, h073_cells_by_route, cells)
    cand, probs = candidate_sweep(sample, mats, h074_routes, h074_cells_by_route, beta, bad_vecs, null_summary)

    opp_z = float(null_summary[(null_summary["top_n"] == 520) & (null_summary["metric"] == "mean_true_opp_rank")]["z_vs_null"].iloc[0])
    bigbet = cand[
        (cand["max_positive_bad_cosine"] <= 0.0)
        & (cand["h050_null_selected"] == 0)
        & (cand["public_action_pred_delta_vs_h057"] <= -0.00090)
        & (cand["responsibility_weighted_delta_vs_h057"] <= -0.00070)
        & (cand["changed_cells_vs_h057"] >= 600)
        & (cand["mean_h074_bad_same_rank"] <= 0.55)
        & (opp_z >= 2.5)
    ].sort_values(["public_action_pred_delta_vs_h057", "h074_score"], ascending=[True, False])

    if len(bigbet):
        selected = bigbet.iloc[0].copy()
        decision_name = "promote_antishortcut_inversion_bigbet"
        worldview = "known public-bad worlds expose a negative boundary whose opposite direction is action-grade"
    else:
        broad_sensor = cand[
            (cand["max_positive_bad_cosine"] <= 0.0)
            & (cand["h050_null_selected"] == 0)
            & (cand["changed_cells_vs_h057"] >= 500)
            & (cand["responsibility_weighted_delta_vs_h057"] <= -0.00085)
            & (cand["mean_h074_bad_same_rank"] <= 0.40)
        ].sort_values(["public_action_pred_delta_vs_h057", "h074_score"], ascending=[True, False])
        if len(broad_sensor):
            selected = broad_sensor.iloc[0].copy()
            decision_name = "promote_antishortcut_broad_sensor_not_001"
            worldview = "bad-opposition is real and can support a broad clean move, but expected action still misses the 0.001 gate"
        else:
            selected = cand.iloc[0].copy()
            decision_name = "promote_antishortcut_inversion_sensor"
            worldview = "bad-opposition is a diagnostic contrastive representation, not yet a broad action solver"

    selected_file = OUT / str(selected["file"])
    digest = str(selected["hash"])
    root_file = ROOT / f"submission_h074_antishortcut_inversion_{digest}_uploadsafe.csv"
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
                "null_opp_z_top520": opp_z,
                **selected.to_dict(),
                **validation,
            }
        ]
    )

    cells.to_csv(OUT / "h074_cell_scores.csv", index=False)
    null_stress.to_csv(OUT / "h074_bad_axis_null_stress.csv", index=False)
    null_summary.to_csv(OUT / "h074_bad_axis_null_summary.csv", index=False)
    h074_routes.to_csv(OUT / "h074_route_candidates.csv", index=False)
    cand.to_csv(OUT / "h074_candidate_scores.csv", index=False)
    decision.to_csv(OUT / "h074_decision.csv", index=False)
    write_report(null_summary, h074_routes, cand, decision)
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
                "mean_h074_bad_opp_rank",
                "mean_h074_bad_same_rank",
                "null_opp_z_top520",
                "public_action_pred_delta_vs_h057",
                "posterior_delta_vs_h057",
                "responsibility_weighted_delta_vs_h057",
                "route_templates",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
