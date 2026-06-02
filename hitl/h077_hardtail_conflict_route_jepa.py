#!/usr/bin/env python3
"""H077: hard-tail conflict route HS-JEPA.

H076 found a sharper contradiction than expected. The strongest route-level
public-action gains came from route cells where the q061 pseudo target says the
move is too extreme (`h076_value_gain < 0`), but the public-action sensor says
the move is valuable.

H077 deliberately tests that contradiction:

    public-action sensor wants hard-tail over-shoot
    q061 posterior says over-shoot is wrong

If H077 wins, the next HS-JEPA layer is not q061 decoding but a target-route
tail law. If it loses, the q061 posterior filter is a necessary guardrail and
the monster-route public-action signal is overfit.
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
OUT = HITL / "h077_hardtail_conflict_route_jepa"
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


H076MOD = import_module(HITL / "h076_route_specific_value_decoder_jepa.py", "h076mod_for_h077")
H071MOD = H076MOD.H071MOD
H074MOD = H076MOD.H074MOD


@dataclass(frozen=True)
class H077Spec:
    name: str
    selector: str
    max_routes: int
    max_cells: int
    allowed_policies: tuple[str, ...]
    allowed_routes: tuple[str, ...]
    min_public_action_gain: float
    max_same_rank: float
    require_outside_h069: bool


def rank01(values: np.ndarray, high: bool = True) -> np.ndarray:
    return H071MOD.rank01(np.asarray(values, dtype=np.float64), high=high)


def logit(x: np.ndarray) -> np.ndarray:
    return H071MOD.logit(x)


def bce(prob: np.ndarray, q: np.ndarray) -> np.ndarray:
    return H071MOD.bce(prob, q)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1.0e-12))


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return H071MOD.md_table(frame, n)


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h077_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h077_hardtail_conflict_*_uploadsafe.csv"):
        path.unlink()


def load_h076_artifacts() -> tuple[pd.DataFrame, pd.DataFrame]:
    cell_path = H076_OUT / "h076_policy_cell_scores.csv"
    route_path = H076_OUT / "h076_policy_route_candidates.csv"
    if not cell_path.exists() or not route_path.exists():
        raise FileNotFoundError("Run H076 before H077; missing H076 policy artifacts.")
    cells = pd.read_csv(cell_path)
    routes = pd.read_csv(route_path)
    if "route_name" not in cells.columns:
        route_names = routes[["h076_policy", "route_id", "route_name"]].drop_duplicates()
        cells = cells.merge(route_names, on=["h076_policy", "route_id"], how="left", validate="many_to_one")
    return cells, routes


def conflict_specs() -> list[H077Spec]:
    q2_routes = ("q2_s3_tail", "q2_hardtail")
    stage_routes = ("s_stage", "s23_core", "s14_edge", "recovery_route")
    mixed_routes = q2_routes + stage_routes
    return [
        H077Spec("monster_q2s3_top1", "route", 1, 4, ("q2_tail_stage_soft",), ("q2_s3_tail",), 0.00020, 0.84, False),
        H077Spec("monster_q2_tail_top3", "route", 3, 8, ("q2_tail_stage_soft",), q2_routes, 0.00016, 0.84, False),
        H077Spec("monster_q2_tail_top5", "route", 5, 12, ("q2_tail_stage_soft",), q2_routes, 0.00012, 0.84, False),
        H077Spec("monster_stage_top3", "route", 3, 12, ("objective_stage_edge", "recovery_full_vector"), stage_routes, 0.00016, 0.84, False),
        H077Spec("monster_stage_top6", "route", 6, 24, ("objective_stage_edge", "recovery_full_vector"), stage_routes, 0.00010, 0.84, False),
        H077Spec(
            "monster_mixed_top5",
            "route",
            5,
            18,
            ("q2_tail_stage_soft", "objective_stage_edge", "recovery_full_vector"),
            mixed_routes,
            0.00012,
            0.84,
            False,
        ),
        H077Spec(
            "monster_mixed_outside_top8",
            "route",
            8,
            28,
            ("q2_tail_stage_soft", "objective_stage_edge", "recovery_full_vector"),
            mixed_routes,
            0.00007,
            0.84,
            True,
        ),
        H077Spec(
            "conflict_cell_top8",
            "cell",
            999,
            8,
            ("q2_tail_stage_soft", "objective_stage_edge", "recovery_full_vector"),
            mixed_routes,
            0.00010,
            0.84,
            False,
        ),
        H077Spec(
            "conflict_cell_top16",
            "cell",
            999,
            16,
            ("q2_tail_stage_soft", "objective_stage_edge", "recovery_full_vector"),
            mixed_routes,
            0.00006,
            0.84,
            False,
        ),
        H077Spec(
            "conflict_cell_outside_top24",
            "cell",
            999,
            24,
            ("q2_tail_stage_soft", "objective_stage_edge", "recovery_full_vector"),
            mixed_routes,
            0.00004,
            0.84,
            True,
        ),
    ]


def conflict_pool(cells: pd.DataFrame, routes: pd.DataFrame, spec: H077Spec) -> tuple[pd.DataFrame, pd.DataFrame]:
    route_cols = [
        "h076_policy",
        "route_id",
        "row",
        "subject_id",
        "sleep_date",
        "route_name",
        "n_cells",
        "targets",
        "sum_h076_public_contrib",
        "sum_h076_value_gain",
        "h076_route_score",
        "mean_h074_bad_opp_rank",
        "mean_h074_bad_same_rank",
        "outside_h069_cells",
        "mean_shortcut_energy",
    ]
    route_pool = routes[
        routes["h076_policy"].isin(spec.allowed_policies)
        & routes["route_name"].isin(spec.allowed_routes)
        & (routes["sum_h076_public_contrib"] < -spec.min_public_action_gain)
        & (routes["sum_h076_value_gain"] < 0)
        & (routes["mean_h074_bad_same_rank"] <= spec.max_same_rank)
    ][route_cols].copy()
    if spec.require_outside_h069:
        route_pool = route_pool[route_pool["outside_h069_cells"] > 0]
    route_pool = route_pool.sort_values("sum_h076_public_contrib")

    cell_pool = cells[
        cells["h076_policy"].isin(spec.allowed_policies)
        & cells["route_name"].isin(spec.allowed_routes)
        & (cells["h076_public_action_gain"] > spec.min_public_action_gain)
        & (cells["h076_value_gain"] < 0)
        & (cells["h074_bad_same_rank"] <= spec.max_same_rank)
        & (cells["is_h050_null"] == 0)
    ].copy()
    if spec.require_outside_h069:
        cell_pool = cell_pool[cell_pool["outside_h069_cell"] > 0]
    cell_pool = cell_pool.sort_values("h076_public_contrib")
    return route_pool, cell_pool


def select_cells(cells: pd.DataFrame, routes: pd.DataFrame, spec: H077Spec) -> tuple[pd.DataFrame, pd.DataFrame]:
    route_pool, cell_pool = conflict_pool(cells, routes, spec)
    if spec.selector == "cell":
        selected_cells = []
        used_flat: set[int] = set()
        for rec in cell_pool.to_dict("records"):
            flat = int(rec["flat_index"])
            if flat in used_flat:
                continue
            selected_cells.append(pd.DataFrame([rec]))
            used_flat.add(flat)
            if len(used_flat) >= spec.max_cells:
                break
        if not selected_cells:
            return route_pool.iloc[0:0].copy(), cell_pool.iloc[0:0].copy()
        cell_sel = pd.concat(selected_cells, ignore_index=True)
        route_sel = route_pool[route_pool["route_id"].isin(cell_sel["route_id"].astype(str).unique())].copy()
        return route_sel, cell_sel

    selected_routes = []
    selected_cells = []
    used_rows: set[int] = set()
    used_flat: set[int] = set()
    total_cells = 0
    for rec in route_pool.to_dict("records"):
        row = int(rec["row"])
        route_id = str(rec["route_id"])
        if row in used_rows:
            continue
        use = cell_pool[cell_pool["route_id"].astype(str).eq(route_id)].copy()
        use = use[~use["flat_index"].astype(int).isin(used_flat)]
        if use.empty:
            continue
        if total_cells + len(use) > spec.max_cells:
            continue
        selected_routes.append(pd.DataFrame([rec]))
        selected_cells.append(use)
        used_rows.add(row)
        used_flat.update(map(int, use["flat_index"].tolist()))
        total_cells += len(use)
        if len(selected_routes) >= spec.max_routes:
            break
    if not selected_routes:
        return route_pool.iloc[0:0].copy(), cell_pool.iloc[0:0].copy()
    return pd.concat(selected_routes, ignore_index=True), pd.concat(selected_cells, ignore_index=True)


def apply_candidate(
    spec: H077Spec,
    sample: pd.DataFrame,
    mats: dict[str, np.ndarray],
    beta: np.ndarray,
    bad_vecs: dict[str, np.ndarray],
    cells: pd.DataFrame,
    routes: pd.DataFrame,
) -> tuple[np.ndarray, dict[str, object], pd.DataFrame, pd.DataFrame]:
    route_sel, cell_sel = select_cells(cells, routes, spec)
    h057_prob = mats["h057"]
    q061 = mats["q061"]
    prob = h057_prob.copy()
    for rec in cell_sel.to_dict("records"):
        prob[int(rec["row"]), int(rec["target_index"])] = float(rec["h076_new_prob"])
    prob = H071MOD.clip_prob(prob)
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
    meta: dict[str, object] = {
        "candidate_id": "",
        "spec_name": spec.name,
        "selector": spec.selector,
        "max_routes": spec.max_routes,
        "max_cells": spec.max_cells,
        "allowed_policies": ";".join(spec.allowed_policies),
        "allowed_routes": ";".join(spec.allowed_routes),
        "min_public_action_gain": spec.min_public_action_gain,
        "max_same_rank": spec.max_same_rank,
        "require_outside_h069": spec.require_outside_h069,
        "selected_routes": int(len(route_sel)),
        "selected_cells": int(len(cell_sel)),
        "changed_cells_vs_h057": int(changed.sum()),
        "changed_rows_vs_h057": int(changed.any(axis=1).sum()),
        "outside_h069_cells": int(cell_sel["outside_h069_cell"].sum()) if len(cell_sel) else 0,
        "Q2_changed_vs_h057": int(changed[:, TARGETS.index("Q2")].sum()),
        "public_action_pred_delta_vs_h057": float(x @ beta),
        "posterior_delta_vs_h057": float(x.mean()),
        "responsibility_weighted_delta_vs_h057": float(np.dot(row_public, row_delta)),
        "max_positive_bad_cosine": max_bad_cos,
        "sum_conflict_public_contrib": float(cell_sel["h076_public_contrib"].sum()) if len(cell_sel) else 0.0,
        "sum_q061_value_gain": float(cell_sel["h076_value_gain"].sum()) if len(cell_sel) else 0.0,
        "mean_conflict_public_action_gain": float(cell_sel["h076_public_action_gain"].mean()) if len(cell_sel) else 0.0,
        "mean_h074_bad_opp_rank": float(cell_sel["h074_bad_opp_rank"].mean()) if len(cell_sel) else 0.0,
        "mean_h074_bad_same_rank": float(cell_sel["h074_bad_same_rank"].mean()) if len(cell_sel) else 1.0,
        "mean_shortcut_energy": float(cell_sel["latent_shortcut_energy"].mean()) if len(cell_sel) else 1.0,
        "mean_abs_prob_move_vs_h057": float(np.abs(prob - h057_prob).mean()),
        "max_abs_prob_move_vs_h057": float(np.abs(prob - h057_prob).max()),
        "h050_null_selected": int(cell_sel["is_h050_null"].sum()) if len(cell_sel) else 0,
        "selected_rows": ",".join(map(str, sorted(set(cell_sel["row"].astype(int).tolist())))) if len(cell_sel) else "",
        "route_templates": ";".join(f"{k}:{v}" for k, v in sorted(route_counts.items())),
        **bad_cos,
    }
    for target in TARGETS:
        meta[f"{target}_changed_vs_h057"] = int(changed[:, TARGETS.index(target)].sum())
    return prob, meta, route_sel, cell_sel


def candidate_sweep(
    sample: pd.DataFrame,
    mats: dict[str, np.ndarray],
    beta: np.ndarray,
    bad_vecs: dict[str, np.ndarray],
    cells: pd.DataFrame,
    routes: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, np.ndarray], pd.DataFrame, pd.DataFrame]:
    rows = []
    probs: dict[str, np.ndarray] = {}
    route_rows = []
    cell_rows = []
    seen: set[str] = set()
    for spec in conflict_specs():
        prob, meta, route_sel, cell_sel = apply_candidate(spec, sample, mats, beta, bad_vecs, cells, routes)
        if meta["changed_cells_vs_h057"] <= 0:
            continue
        digest = short_hash(prob)
        if digest in seen:
            continue
        seen.add(digest)
        cid = f"h077_{spec.name}_{digest}"
        meta["candidate_id"] = cid
        meta["hash"] = digest
        rows.append(meta)
        probs[cid] = prob
        if len(route_sel):
            route_rows.append(route_sel.assign(candidate_id=cid))
        if len(cell_sel):
            cell_rows.append(cell_sel.assign(candidate_id=cid))

    cand = pd.DataFrame(rows)
    if cand.empty:
        raise RuntimeError("no H077 candidates generated")
    cand["action_rank"] = rank01(-cand["public_action_pred_delta_vs_h057"].to_numpy())
    cand["responsibility_rank"] = rank01(-cand["responsibility_weighted_delta_vs_h057"].to_numpy())
    cand["conflict_gain_rank"] = rank01(-cand["sum_conflict_public_contrib"].to_numpy())
    cand["same_avoid_rank"] = rank01(-cand["mean_h074_bad_same_rank"].to_numpy())
    cand["bad_avoid_rank"] = rank01(-cand["max_positive_bad_cosine"].to_numpy())
    cand["scale_rank"] = rank01(np.minimum(cand["changed_cells_vs_h057"].to_numpy(), 24))
    cand["posterior_violation"] = np.maximum(cand["posterior_delta_vs_h057"].to_numpy(), 0.0)
    cand["h077_score"] = (
        0.30 * cand["action_rank"]
        + 0.18 * cand["conflict_gain_rank"]
        + 0.14 * cand["responsibility_rank"]
        + 0.10 * cand["same_avoid_rank"]
        + 0.08 * cand["bad_avoid_rank"]
        + 0.07 * cand["scale_rank"]
        + 0.06 * (cand["outside_h069_cells"] / cand["changed_cells_vs_h057"].clip(lower=1)).clip(0, 1)
        - 0.08 * (cand["h050_null_selected"] > 0).astype(float)
        - 0.08 * (cand["max_abs_prob_move_vs_h057"] > 0.30).astype(float)
    )
    cand = cand.sort_values(["h077_score", "public_action_pred_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True)
    for _, rec in cand.iterrows():
        cid = str(rec["candidate_id"])
        path = OUT / f"submission_{cid}.csv"
        H071MOD.write_submission(sample, probs[cid], path)
        cand.loc[cand["candidate_id"].eq(cid), "file"] = path.name
        cand.loc[cand["candidate_id"].eq(cid), "resolved_path"] = str(path.resolve())
    route_diag = pd.concat(route_rows, ignore_index=True) if route_rows else pd.DataFrame()
    cell_diag = pd.concat(cell_rows, ignore_index=True) if cell_rows else pd.DataFrame()
    return cand, probs, route_diag, cell_diag


def validate_submission(path: Path, sample: pd.DataFrame, h057_prob: np.ndarray) -> dict[str, object]:
    return H071MOD.validate_submission(path, sample, h057_prob)


def write_report(cand: pd.DataFrame, route_diag: pd.DataFrame, cell_diag: pd.DataFrame, decision: pd.DataFrame) -> None:
    parts = [
        "# H077 Hard-Tail Conflict Route HS-JEPA",
        "",
        "Question: should HS-JEPA trust a public-action hard-tail conflict even when q061 posterior calls it an overshoot?",
        "",
        "Design:",
        "",
        "- source: H076 route-policy cells with positive public-action gain and negative q061 value gain;",
        "- action unit: single monster route, top route cluster, or top conflicting cells;",
        "- risk control: H050-null filter, bad-anchor cosine, same-bad rank, upload validation;",
        "- interpretation: public improvement means q061 is too soft for a hidden tail route; public loss means the public-action sensor overfit a sparse route.",
        "",
        "Candidates:",
        "",
        md_table(cand, 30),
        "",
        "Selected route diagnostics:",
        "",
        md_table(route_diag.head(40), 40) if len(route_diag) else "(none)",
        "",
        "Selected cell diagnostics:",
        "",
        md_table(
            cell_diag[
                [
                    "candidate_id",
                    "h076_policy",
                    "route_id",
                    "row",
                    "target",
                    "h076_decoder",
                    "h076_public_contrib",
                    "h076_value_gain",
                    "h076_new_prob",
                    "h074_bad_opp_rank",
                    "h074_bad_same_rank",
                    "outside_h069_cell",
                ]
            ].head(60),
            60,
        )
        if len(cell_diag)
        else "(none)",
        "",
        "Decision:",
        "",
        md_table(decision),
    ]
    (OUT / "h077_report.md").write_text("\n".join(parts))


def main() -> None:
    cleanup_previous_outputs()
    sample, _latent, mats, beta, bad_vecs = H071MOD.load_runtime()
    cells, routes = load_h076_artifacts()
    cand, probs, route_diag, cell_diag = candidate_sweep(sample, mats, beta, bad_vecs, cells, routes)

    bigbet = cand[
        (cand["max_positive_bad_cosine"] <= 0.0)
        & (cand["h050_null_selected"] == 0)
        & (cand["public_action_pred_delta_vs_h057"] <= -0.00075)
        & (cand["changed_cells_vs_h057"] <= 16)
    ].sort_values(["public_action_pred_delta_vs_h057", "h077_score"], ascending=[True, False])
    if len(bigbet):
        selected = bigbet.iloc[0].copy()
        decision_name = "promote_hardtail_conflict_monster_bigbet"
        worldview = "public-like subset contains a sparse hard-tail route that q061 under-shoots"
    else:
        selected = cand.iloc[0].copy()
        decision_name = "promote_hardtail_conflict_diagnostic"
        worldview = "hard-tail conflict is observable but did not meet the sparse big-bet gate"

    selected_file = OUT / str(selected["file"])
    digest = str(selected["hash"])
    root_file = ROOT / f"submission_h077_hardtail_conflict_{digest}_uploadsafe.csv"
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

    cand.to_csv(OUT / "h077_candidate_scores.csv", index=False)
    route_diag.to_csv(OUT / "h077_selected_routes.csv", index=False)
    cell_diag.to_csv(OUT / "h077_selected_cells.csv", index=False)
    decision.to_csv(OUT / "h077_decision.csv", index=False)
    write_report(cand, route_diag, cell_diag, decision)
    print(
        decision[
            [
                "selected_candidate_id",
                "root_uploadsafe_path",
                "decision",
                "changed_cells_vs_h057",
                "changed_rows_vs_h057",
                "selected_routes",
                "Q2_changed_vs_h057",
                "public_action_pred_delta_vs_h057",
                "posterior_delta_vs_h057",
                "responsibility_weighted_delta_vs_h057",
                "sum_q061_value_gain",
                "max_abs_prob_move_vs_h057",
                "selected_rows",
                "route_templates",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
