#!/usr/bin/env python3
"""H084: dark route completion HS-JEPA.

H083 showed that route-action transport is measurable, but its promoted file
still overlaps H082 strongly. H084 tests the sharper complementary claim:

    H082 found visible fragments of route states, but missed dark companion
    cells inside the same hidden row routes.

The base is H082, not H057. We only change cells that H082 did not change, on
rows/routes where H082 already has visible support. This is not a blend tweak:
it asks whether the missing state lives in route-completion cells.
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
OUT = HITL / "h084_dark_route_completion_jepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
S_TARGETS = ["S1", "S2", "S3", "S4"]
TOL = 1.0e-12

H082_ROOT = "submission_h082_source_action_0e565967_uploadsafe.csv"


@dataclass(frozen=True)
class H084Spec:
    name: str
    allowed_routes: tuple[str, ...]
    max_cells: int
    max_rows: int
    q2_cap: int
    max_per_subject: int
    min_route_action_score: float
    min_h082_cells: int
    min_dark_cells: int
    min_family_mean: float
    max_bad_same_mean: float
    novelty: str
    value_mode: str
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


H083MOD = import_module(HITL / "h083_route_action_transport_jepa.py", "h083mod_for_h084")
H071MOD = H083MOD.H071MOD


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
    for path in OUT.glob("submission_h084_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h084_dark_route_*_uploadsafe.csv"):
        path.unlink()


def load_h082(sample: pd.DataFrame) -> np.ndarray:
    path = ROOT / H082_ROOT
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)[TARGETS].to_numpy(dtype=np.float64)


def candidate_specs() -> list[H084Spec]:
    routes = H071MOD.ROUTES
    all_routes = tuple(routes)
    rowvector_routes = ("full_state", "nonq2_full", "q3_s_stage", "q_subjective", "recovery_route")
    objective_routes = ("s_stage", "s23_core", "s14_edge", "q3_s_stage", "recovery_route", "nonq2_full")
    return [
        H084Spec("dark_all_c220", all_routes, 220, 120, 35, 18, 0.54, 2, 1, 1.05, 0.90, "any", "source_q061", 1.00, 0.70),
        H084Spec("dark_all_amp_c260", all_routes, 260, 135, 42, 18, 0.52, 2, 1, 1.00, 0.92, "any", "source_q061", 1.18, 0.82),
        H084Spec("dark_outside_h069_c240", all_routes, 240, 130, 35, 18, 0.52, 2, 1, 1.00, 0.90, "outside_h069", "source_q061", 1.08, 0.76),
        H084Spec("dark_rowvector_c240", rowvector_routes, 240, 120, 25, 18, 0.54, 2, 1, 1.05, 0.90, "any", "source_q061", 1.06, 0.74),
        H084Spec("dark_objective_c220", objective_routes, 220, 120, 0, 18, 0.52, 2, 1, 1.00, 0.92, "any", "source_q061", 1.12, 0.78),
        H084Spec("dark_stage_c180", ("s_stage", "s23_core", "s14_edge"), 180, 110, 0, 16, 0.50, 1, 1, 0.80, 0.94, "any", "source_q061", 1.15, 0.82),
        H084Spec("dark_posterior_c240", all_routes, 240, 125, 35, 18, 0.50, 1, 1, 0.90, 0.92, "posterior_friendly", "source_q061", 1.06, 0.74),
        H084Spec("dark_sourceonly_c240", all_routes, 240, 125, 35, 18, 0.50, 1, 1, 0.90, 0.92, "any", "source_only", 1.12, 0.00),
    ]


def load_runtime() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, np.ndarray], np.ndarray, dict[str, np.ndarray], np.ndarray, np.ndarray]:
    sample, latent, table, mats, beta, bad_vecs = H083MOD.load_runtime()
    h082 = load_h082(sample)
    h082_mask = np.abs(h082 - mats["h057"]) > TOL
    return sample, latent, table, mats, beta, bad_vecs, h082, h082_mask


def build_dark_route_table(table: pd.DataFrame, h082_mask: np.ndarray) -> pd.DataFrame:
    route_table = H083MOD.build_route_action_table(table)
    rows = []
    for rec in route_table.to_dict("records"):
        row = int(rec["row"])
        target_indices = [int(x) for x in str(rec["target_indices"]).split(",") if str(x) != ""]
        dark_indices = [idx for idx in target_indices if not bool(h082_mask[row, idx])]
        if not dark_indices:
            continue
        cells = table[(table["row"].astype(int) == row) & (table["target_index"].astype(int).isin(dark_indices))].copy()
        if cells.empty:
            continue
        rows.append(
            {
                **rec,
                "dark_cells": int(len(cells)),
                "dark_source_cells": int((cells["source_count"] > 0).sum()),
                "dark_q2_cells": int((cells["target"] == "Q2").sum()),
                "dark_source_action_sum": float(cells["source_action_delta"].sum()),
                "dark_source_posterior_sum": float(cells["source_posterior_delta"].sum()),
                "dark_family_count_mean": float(cells["source_family_count"].mean()),
                "dark_bad_same_mean": float(cells["h080_bad_same_rank"].mean()),
                "dark_outside_h069_cells": int(cells["outside_h069_cell"].sum()),
                "dark_target_indices": ",".join(str(i) for i in dark_indices),
            }
        )
    out = pd.DataFrame(rows)
    if out.empty:
        raise RuntimeError("no dark route rows")
    out["dark_route_score"] = (
        0.28 * rank01(-out["dark_source_action_sum"].to_numpy())
        + 0.16 * rank01(out["route_action_score"].to_numpy())
        + 0.12 * rank01(out["h082_cells"].to_numpy())
        + 0.10 * rank01(out["dark_source_cells"].to_numpy())
        + 0.09 * rank01(out["dark_family_count_mean"].to_numpy())
        + 0.08 * rank01(out["dark_outside_h069_cells"].to_numpy())
        + 0.06 * rank01(-out["dark_bad_same_mean"].to_numpy())
        + 0.06 * rank01(-out["mean_shortcut_energy"].to_numpy())
        + 0.05 * rank01(out["assignment_route_score"].to_numpy())
    )
    return out.sort_values(["dark_route_score", "dark_source_action_sum"], ascending=[False, True]).reset_index(drop=True)


def pool_for(dark_table: pd.DataFrame, spec: H084Spec) -> pd.DataFrame:
    pool = dark_table[
        dark_table["route_name"].astype(str).isin(spec.allowed_routes)
        & (dark_table["dark_route_score"] >= spec.min_route_action_score)
        & (dark_table["h082_cells"] >= spec.min_h082_cells)
        & (dark_table["dark_cells"] >= spec.min_dark_cells)
        & (dark_table["dark_family_count_mean"] >= spec.min_family_mean)
        & (dark_table["dark_bad_same_mean"] <= spec.max_bad_same_mean)
        & (dark_table["route_h050_null_cells"] <= 0)
    ].copy()
    if spec.q2_cap == 0:
        pool = pool[pool["dark_q2_cells"] <= 0].copy()
    if spec.novelty == "outside_h069":
        pool = pool[pool["dark_outside_h069_cells"] >= np.maximum(1, pool["dark_cells"] // 2)].copy()
    elif spec.novelty == "posterior_friendly":
        pool = pool[pool["dark_source_posterior_sum"] < 0].copy()
    elif spec.novelty != "any":
        raise ValueError(spec.novelty)
    return pool.sort_values(["dark_route_score", "dark_source_action_sum"], ascending=[False, True])


def greedy_select(pool: pd.DataFrame, spec: H084Spec) -> pd.DataFrame:
    selected = []
    rows_seen: set[int] = set()
    subject_counts: dict[str, int] = {}
    total_cells = 0
    q2_cells = 0
    for rec in pool.to_dict("records"):
        row = int(rec["row"])
        subject = str(rec["subject_id"])
        n_cells = int(rec["dark_cells"])
        new_q2 = int(rec["dark_q2_cells"])
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


def materialize(selected_routes: pd.DataFrame, table: pd.DataFrame, mats: dict[str, np.ndarray], h082: np.ndarray, spec: H084Spec) -> tuple[np.ndarray, pd.DataFrame]:
    prob = h082.copy()
    base_logit = logit(h082)
    h057_logit = logit(mats["h057"])
    q061_move = logit(mats["q061"]) - h057_logit
    selected_cells = []
    for rec in selected_routes.to_dict("records"):
        row = int(rec["row"])
        dark_indices = [int(x) for x in str(rec["dark_target_indices"]).split(",") if str(x) != ""]
        cells = table[(table["row"].astype(int) == row) & (table["target_index"].astype(int).isin(dark_indices))].copy()
        for cell in cells.to_dict("records"):
            tidx = int(cell["target_index"])
            has_source = float(cell["source_count"]) > 0
            if spec.value_mode == "source_only":
                if not has_source:
                    continue
                move = float(cell["source_mean_move"])
            elif spec.value_mode == "source_q061":
                move = float(cell["source_mean_move"]) if has_source else spec.fill_alpha * float(q061_move[row, tidx])
            else:
                raise ValueError(spec.value_mode)
            prob[row, tidx] = float(sigmoid(np.array([base_logit[row, tidx] + spec.alpha * move]))[0])
            selected_cells.append({**cell, **{f"h084_route_{k}": v for k, v in rec.items()}, "h084_has_source": int(has_source), "h084_move": move})
    return clip_prob(prob), pd.DataFrame(selected_cells)


def evaluate(prob: np.ndarray, selected_routes: pd.DataFrame, selected_cells: pd.DataFrame, spec: H084Spec, mats: dict[str, np.ndarray], h082: np.ndarray, beta: np.ndarray, bad_vecs: dict[str, np.ndarray]) -> dict[str, object]:
    h057 = mats["h057"]
    q061 = mats["q061"]
    changed = np.abs(prob - h057) > TOL
    changed_vs_h082 = np.abs(prob - h082) > TOL
    x = (bce(prob, q061) - bce(h057, q061)).reshape(-1)
    x82 = (bce(prob, q061) - bce(h082, q061)).reshape(-1)
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
        "selected_dark_cells": int(len(selected_cells)),
        "changed_cells_vs_h057": int(changed.sum()),
        "changed_rows_vs_h057": int(changed.any(axis=1).sum()),
        "changed_cells_vs_h082": int(changed_vs_h082.sum()),
        "changed_rows_vs_h082": int(changed_vs_h082.any(axis=1).sum()),
        "filled_dark_cells": int((selected_cells["h084_has_source"] == 0).sum()) if len(selected_cells) else 0,
        "source_dark_cells": int((selected_cells["h084_has_source"] > 0).sum()) if len(selected_cells) else 0,
        "public_action_pred_delta_vs_h057": float(x @ beta),
        "public_action_pred_delta_vs_h082": float(x82 @ beta),
        "posterior_delta_vs_h057": float(x.mean()),
        "posterior_delta_vs_h082": float(x82.mean()),
        "responsibility_weighted_delta_vs_h057": float(np.dot(row_public, row_delta)),
        "max_positive_bad_cosine": max_bad_cos,
        "mean_abs_prob_move_vs_h082": float(np.abs(prob - h082).mean()),
        "max_abs_prob_move_vs_h082": float(np.abs(prob - h082).max()),
        "mean_dark_route_score": float(selected_routes["dark_route_score"].mean()) if len(selected_routes) else 0.0,
        "mean_route_action_score": float(selected_routes["route_action_score"].mean()) if len(selected_routes) else 0.0,
        "sum_dark_source_action_sum": float(selected_routes["dark_source_action_sum"].sum()) if len(selected_routes) else 0.0,
        "mean_dark_family_count": float(selected_routes["dark_family_count_mean"].mean()) if len(selected_routes) else 0.0,
        "mean_dark_bad_same": float(selected_routes["dark_bad_same_mean"].mean()) if len(selected_routes) else 1.0,
        "selected_subjects": int(selected_routes["subject_id"].nunique()) if len(selected_routes) else 0,
        "selected_rows": ",".join(map(str, sorted(selected_routes["row"].astype(int).unique()))) if len(selected_routes) else "",
        "route_templates": ";".join(f"{k}:{v}" for k, v in sorted(route_counts.items())),
        "target_templates": ";".join(f"{k}:{v}" for k, v in sorted(target_counts.items())),
        **bad_cos,
    }
    for target in TARGETS:
        meta[f"{target}_changed_vs_h082"] = int(changed_vs_h082[:, TARGETS.index(target)].sum())
        meta[f"{target}_changed_vs_h057"] = int(changed[:, TARGETS.index(target)].sum())
    return meta


def candidate_sweep(dark_table: pd.DataFrame, table: pd.DataFrame, sample: pd.DataFrame, mats: dict[str, np.ndarray], h082: np.ndarray, beta: np.ndarray, bad_vecs: dict[str, np.ndarray]) -> tuple[pd.DataFrame, dict[str, np.ndarray], pd.DataFrame, pd.DataFrame]:
    rows = []
    probs: dict[str, np.ndarray] = {}
    route_parts = []
    cell_parts = []
    seen: set[str] = set()
    for spec in candidate_specs():
        pool = pool_for(dark_table, spec)
        selected_routes = greedy_select(pool, spec)
        if selected_routes.empty:
            continue
        prob, selected_cells = materialize(selected_routes, table, mats, h082, spec)
        if len(selected_cells) < 40:
            continue
        digest = short_hash(prob)
        if digest in seen:
            continue
        seen.add(digest)
        meta = evaluate(prob, selected_routes, selected_cells, spec, mats, h082, beta, bad_vecs)
        cid = f"h084_{spec.name}_{digest}"
        meta["candidate_id"] = cid
        meta["hash"] = digest
        rows.append(meta)
        probs[cid] = prob
        route_parts.append(selected_routes.assign(candidate_id=cid))
        cell_parts.append(selected_cells.assign(candidate_id=cid))
    cand = pd.DataFrame(rows)
    if cand.empty:
        raise RuntimeError("no H084 candidates generated")
    cand["action_rank"] = rank01(-cand["public_action_pred_delta_vs_h082"].to_numpy())
    cand["posterior_rank"] = rank01(-cand["posterior_delta_vs_h082"].to_numpy())
    cand["bad_avoid_rank"] = rank01(-cand["max_positive_bad_cosine"].to_numpy())
    cand["dark_rank"] = rank01(cand["selected_dark_cells"].to_numpy())
    cand["route_rank"] = rank01(cand["mean_dark_route_score"].to_numpy())
    cand["fill_ratio"] = cand["filled_dark_cells"] / cand["selected_dark_cells"].clip(lower=1)
    cand["bigbet_score"] = ((-cand["public_action_pred_delta_vs_h082"] - 0.00035) / 0.0025).clip(0.0, 1.0)
    cand["h084_score"] = (
        0.25 * cand["action_rank"]
        + 0.17 * cand["posterior_rank"]
        + 0.15 * cand["route_rank"]
        + 0.12 * cand["dark_rank"]
        + 0.10 * cand["bigbet_score"]
        + 0.08 * cand["bad_avoid_rank"]
        + 0.06 * rank01(cand["mean_dark_family_count"].to_numpy())
        - 0.08 * (cand["fill_ratio"] > 0.55).astype(float)
        - 0.05 * (cand["max_abs_prob_move_vs_h082"] > 0.22).astype(float)
    )
    cand = cand.sort_values(["h084_score", "public_action_pred_delta_vs_h082"], ascending=[False, True]).reset_index(drop=True)
    for _, rec in cand.iterrows():
        cid = str(rec["candidate_id"])
        path = OUT / f"submission_{cid}.csv"
        write_submission(sample, probs[cid], path)
        cand.loc[cand["candidate_id"].eq(cid), "file"] = path.name
        cand.loc[cand["candidate_id"].eq(cid), "resolved_path"] = str(path.resolve())
    routes = pd.concat(route_parts, ignore_index=True) if route_parts else pd.DataFrame()
    cells = pd.concat(cell_parts, ignore_index=True) if cell_parts else pd.DataFrame()
    return cand, probs, routes, cells


def write_report(dark_table: pd.DataFrame, cand: pd.DataFrame, selected_routes: pd.DataFrame, selected_cells: pd.DataFrame, decision: pd.DataFrame) -> None:
    route_cols = [
        "candidate_id",
        "row",
        "subject_id",
        "sleep_date",
        "route_name",
        "targets",
        "dark_route_score",
        "dark_cells",
        "dark_source_cells",
        "h082_cells",
        "dark_source_action_sum",
        "dark_source_posterior_sum",
        "dark_family_count_mean",
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
        "h084_has_source",
        "h084_move",
    ]
    report = [
        "# H084 Dark Route Completion HS-JEPA",
        "",
        "Question: did H082 find visible fragments but miss hidden route companion cells?",
        "",
        "Design:",
        "",
        "- base: H082;",
        "- select only cells unchanged by H082;",
        "- require visible H082 support in the same route;",
        "- materialize dark companion cells with source move or q061 fill.",
        "",
        "Dark route table summary:",
        "",
        md_table(
            pd.DataFrame(
                [
                    {
                        "dark_routes": int(len(dark_table)),
                        "unique_rows": int(dark_table["row"].nunique()),
                        "max_dark_route_score": float(dark_table["dark_route_score"].max()),
                        "top_route": str(dark_table.iloc[0]["route_name"]),
                        "top_dark_cells": int(dark_table.iloc[0]["dark_cells"]),
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
        md_table(selected_routes[[c for c in route_cols if c in selected_routes.columns]].head(140), 140) if len(selected_routes) else "(none)",
        "",
        "Selected dark cell sample:",
        "",
        md_table(selected_cells[[c for c in cell_cols if c in selected_cells.columns]].head(140), 140) if len(selected_cells) else "(none)",
        "",
        "Decision:",
        "",
        md_table(decision),
    ]
    (OUT / "h084_report.md").write_text("\n".join(report))


def main() -> None:
    cleanup_previous_outputs()
    sample, _latent, table, mats, beta, bad_vecs, h082, h082_mask = load_runtime()
    dark_table = build_dark_route_table(table, h082_mask)
    cand, probs, routes, cells = candidate_sweep(dark_table, table, sample, mats, h082, beta, bad_vecs)
    bigbet = cand[
        (cand["public_action_pred_delta_vs_h082"] <= -0.00025)
        & (cand["changed_cells_vs_h082"] >= 40)
        & (cand["posterior_delta_vs_h082"] <= 0.0002)
        & (cand["max_positive_bad_cosine"] <= 0.030)
    ].copy()
    if len(bigbet):
        selected = bigbet.sort_values(["h084_score", "public_action_pred_delta_vs_h082"], ascending=[False, True]).iloc[0]
        decision_name = "promote_dark_route_completion_bigbet"
        worldview = "H082 visible route fragments need dark companion completion"
    else:
        selected = cand.iloc[0]
        decision_name = "promote_dark_route_completion_diagnostic"
        worldview = "dark route completion is measurable but did not clear every big-bet guardrail"

    selected_id = str(selected["candidate_id"])
    root_file = ROOT / f"submission_h084_dark_route_{selected['hash']}_uploadsafe.csv"
    shutil.copy2(Path(str(selected["resolved_path"])), root_file)
    validation = validate_submission(root_file, sample, mats["h057"])
    decision = pd.DataFrame([{**selected.to_dict(), **validation}])
    decision.insert(0, "worldview", worldview)
    decision.insert(0, "root_uploadsafe_path", str(root_file.resolve()))
    decision.insert(0, "selected_resolved_path", str(selected["resolved_path"]))
    decision.insert(0, "selected_file", str(selected["file"]))
    decision.insert(0, "selected_candidate_id", selected_id)
    decision.insert(0, "decision", decision_name)

    cand.to_csv(OUT / "h084_candidate_scores.csv", index=False)
    dark_table.to_csv(OUT / "h084_dark_route_table.csv", index=False)
    routes.to_csv(OUT / "h084_selected_routes.csv", index=False)
    cells.to_csv(OUT / "h084_selected_cells.csv", index=False)
    decision.to_csv(OUT / "h084_decision.csv", index=False)
    write_report(dark_table, cand, routes[routes["candidate_id"].eq(selected_id)].copy(), cells[cells["candidate_id"].eq(selected_id)].copy(), decision)

    print(f"selected={selected_id}")
    print(f"root={root_file}")
    print(decision[["decision", "public_action_pred_delta_vs_h082", "posterior_delta_vs_h082", "changed_cells_vs_h082", "public_action_pred_delta_vs_h057", "changed_cells_vs_h057", "max_positive_bad_cosine", "upload_safe"]].to_string(index=False))


if __name__ == "__main__":
    main()
