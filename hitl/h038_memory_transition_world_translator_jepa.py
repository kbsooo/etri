#!/usr/bin/env python3
"""H038: memory-transition world translator HS-JEPA.

H012 proved that public LB observations can define a hidden public-state
posterior.  H014/H031 added a surprising independent view: same-subject
sleep-state memory is real, but most of H012's gain is carried by cells where
that memory disagrees with H012.  H036 then found a stronger hidden public-world
posterior, while H037 showed that simply moving farther on the H012 ray is not
enough.

H038 asks a more specific question:

    Did H012 win because it detected within-person state transitions where
    subject memory is misleading, and can H036's world pressure be translated
    only through those transition cells/rows?

This is not a memory-compatible pruning experiment.  It treats memory
disagreement as a context signal and tests route-level actions that combine:

    context = H014 subject-state memory + H031 conflict core + H036 public world
    target  = hidden transition/public-exception representation
    action  = route-calibrated q/posterior/memory movement around H012
"""

from __future__ import annotations

from pathlib import Path
import hashlib
import importlib.util
import shutil
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HITL = ROOT / "hitl"
OUT = HITL / "h038_memory_transition_world_translator_jepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1.0e-6
H012 = "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"
H012_LB = 0.5681234831
E247 = "submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv"


def import_module(path: Path, name: str) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def logit(x: np.ndarray) -> np.ndarray:
    p = clip_prob(x)
    return np.log(p / (1.0 - p))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(x, dtype=np.float64)))


def bce(prob: np.ndarray, q: np.ndarray) -> np.ndarray:
    p = clip_prob(prob)
    qq = clip_prob(q)
    return -(qq * np.log(p) + (1.0 - qq) * np.log(1.0 - p))


def rank01(x: np.ndarray | pd.Series, high: bool = True) -> np.ndarray:
    s = pd.Series(np.asarray(x, dtype=np.float64)).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    if s.nunique(dropna=True) <= 1:
        return np.full(len(s), 0.5, dtype=np.float64)
    r = s.rank(method="average", pct=True).to_numpy(dtype=np.float64)
    return r if high else 1.0 - r


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    if frame.empty:
        return "_empty_"
    view = frame.head(n).copy()
    for col in view.columns:
        if pd.api.types.is_float_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else f"{float(x):.9f}")
    view = view.fillna("")
    headers = [str(c) for c in view.columns]
    rows = [[str(v).replace("\n", " ") for v in row] for row in view.to_numpy()]
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    out.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(out)


def safe_id(text: str, limit: int = 92) -> str:
    keep = []
    for ch in str(text):
        keep.append(ch if ch.isalnum() or ch in "._-" else "_")
    return "".join(keep).strip("_")[:limit].strip("_")


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(prob, 12).tobytes()).hexdigest()[:8]


def load_sub(name: str, sample: pd.DataFrame | None = None) -> pd.DataFrame:
    h036 = import_module(HITL / "h036_global_public_world_solver_jepa.py", "h036_h038_loader")
    df = h036.load_sub(name, sample)
    return df


def write_submission(sample: pd.DataFrame, prob: np.ndarray, path: Path) -> None:
    out = sample.copy()
    for i, target in enumerate(TARGETS):
        out[target] = clip_prob(prob[:, i])
    out.to_csv(path, index=False)


def weighted_delta(prob: np.ndarray, base: np.ndarray, q: np.ndarray, weight: np.ndarray) -> float:
    w = np.asarray(weight, dtype=np.float64)
    if w.ndim == 1:
        w = np.repeat(w[:, None], len(TARGETS), axis=1)
    w = np.nan_to_num(w, nan=0.0, posinf=0.0, neginf=0.0)
    w = np.clip(w, 0.0, None)
    if float(w.sum()) <= 1.0e-12:
        w = np.ones_like(base)
    return float(np.sum(w * (bce(prob, q) - bce(base, q))) / np.sum(w))


def flatten_index(row: int, target_i: int) -> int:
    return int(row) * len(TARGETS) + int(target_i)


def load_cell_state(sample: pd.DataFrame, e247_prob: np.ndarray, h012_prob: np.ndarray) -> pd.DataFrame:
    memory = pd.read_csv(HITL / "h014_sleep_state_memory_posterior_audit" / "h014_memory_cells.csv")
    world = pd.read_csv(HITL / "h036_global_public_world_solver_jepa" / "h036_world_posterior_cells.csv")
    h031_path = HITL / "h031_memory_conflict_public_core_jepa" / "h031_cell_state.csv"
    h031 = pd.read_csv(h031_path) if h031_path.exists() else pd.DataFrame()

    cols = ["row", "target", "public_conflict_core_score", "public_conflict_s_route_score", "rollback_cost_score"]
    if not h031.empty:
        memory = memory.merge(h031[[c for c in cols if c in h031.columns]], on=["row", "target"], how="left")
    for col in ["public_conflict_core_score", "public_conflict_s_route_score", "rollback_cost_score"]:
        if col not in memory.columns:
            memory[col] = 0.5
        memory[col] = memory[col].fillna(0.5)

    memory = memory.merge(
        world[["row", "target", "world_q_cond", "row_public_prob", "cell_world_score"]],
        on=["row", "target"],
        how="left",
    )
    memory["target_i"] = memory["target"].map({t: i for i, t in enumerate(TARGETS)}).astype(int)
    memory = memory.sort_values(["row", "target_i"]).reset_index(drop=True)
    if len(memory) != len(sample) * len(TARGETS):
        raise ValueError(f"incomplete cell state: {len(memory)}")

    z_e247 = logit(e247_prob)
    z_h012 = logit(h012_prob)
    memory["e247_prob_check"] = [e247_prob[int(r), int(t)] for r, t in zip(memory["row"], memory["target_i"])]
    memory["h012_prob_check"] = [h012_prob[int(r), int(t)] for r, t in zip(memory["row"], memory["target_i"])]
    memory["ray_logit_delta"] = [z_h012[int(r), int(t)] - z_e247[int(r), int(t)] for r, t in zip(memory["row"], memory["target_i"])]
    for col in [
        "posterior_gain",
        "memory_alignment",
        "memory_alignment_q",
        "row_full_reliability_q",
        "private_safe_score",
        "memory_prob_full",
        "posterior_prob",
        "world_q_cond",
        "row_public_prob",
        "cell_world_score",
    ]:
        if col not in memory.columns:
            memory[col] = 0.0
        memory[col] = memory[col].fillna(0.0)
    for col in ["h012_changed", "memory_agrees_h012", "memory_disagrees_h012"]:
        memory[col] = memory[col].fillna(False).astype(bool)

    z_memory = logit(memory["memory_prob_full"].to_numpy(dtype=np.float64))
    z_world = logit(memory["world_q_cond"].to_numpy(dtype=np.float64))
    z_post = logit(memory["posterior_prob"].to_numpy(dtype=np.float64))
    z_h012_flat = logit(memory["h012_prob_check"].to_numpy(dtype=np.float64))
    ray = memory["ray_logit_delta"].to_numpy(dtype=np.float64)
    support = np.abs(ray) > 1.0e-8

    memory["flat_idx"] = [flatten_index(r, t) for r, t in zip(memory["row"], memory["target_i"])]
    memory["support"] = support
    memory["world_from_h012"] = z_world - z_h012_flat
    memory["memory_from_h012"] = z_memory - z_h012_flat
    memory["posterior_from_h012"] = z_post - z_h012_flat
    memory["world_agrees_ray"] = np.sign(memory["world_from_h012"]) == np.sign(ray)
    memory["world_opposes_memory"] = np.sign(memory["world_from_h012"]) != np.sign(memory["memory_from_h012"])
    changed = memory["h012_changed"].to_numpy(dtype=bool)
    memory["gain_rank"] = 0.0
    memory.loc[changed, "gain_rank"] = rank01(memory.loc[changed, "posterior_gain"])
    memory["world_rank"] = rank01(memory["cell_world_score"])
    memory["row_public_rank"] = rank01(memory["row_public_prob"])
    memory["anti_memory_rank"] = rank01(-memory["memory_alignment"])
    memory["reliability_rank"] = rank01(memory["row_full_reliability_q"])
    memory["private_safe_rank"] = rank01(memory["private_safe_score"])
    memory["abs_ray_rank"] = rank01(np.abs(ray))
    memory["target_S124"] = memory["target"].isin(["S1", "S2", "S4"]).astype(float)
    memory["target_Q2S1S2S4"] = memory["target"].isin(["Q2", "S1", "S2", "S4"]).astype(float)

    memory["transition_exception_score"] = np.clip(
        0.24 * memory["gain_rank"]
        + 0.20 * memory["world_rank"]
        + 0.18 * memory["memory_disagrees_h012"].astype(float)
        + 0.12 * memory["world_opposes_memory"].astype(float)
        + 0.10 * memory["anti_memory_rank"]
        + 0.08 * memory["row_public_rank"]
        + 0.05 * memory["target_S124"]
        + 0.03 * memory["reliability_rank"],
        0.0,
        1.0,
    )
    memory["transition_repair_score"] = np.clip(
        0.22 * memory["world_rank"]
        + 0.20 * memory["memory_agrees_h012"].astype(float)
        + 0.16 * (1.0 - memory["world_agrees_ray"].astype(float))
        + 0.14 * memory["private_safe_rank"]
        + 0.12 * memory["reliability_rank"]
        + 0.10 * memory["rollback_cost_score"]
        + 0.06 * memory["target_Q2S1S2S4"],
        0.0,
        1.0,
    )
    memory["transition_row_score"] = (
        memory.groupby("row")["transition_exception_score"].transform("mean") * 0.45
        + memory.groupby("row")["cell_world_score"].transform("mean").rank(method="average", pct=True) * 0.35
        + memory.groupby("row")["row_public_prob"].transform("max").rank(method="average", pct=True) * 0.20
    )
    memory.to_csv(OUT / "h038_cell_state.csv", index=False)
    return memory


def array_from_cells(cells: pd.DataFrame, col: str, n_rows: int) -> np.ndarray:
    mat = np.full((n_rows, len(TARGETS)), np.nan, dtype=np.float64)
    for rec in cells[["row", "target_i", col]].to_dict("records"):
        mat[int(rec["row"]), int(rec["target_i"])] = float(rec[col])
    if np.isnan(mat).any():
        raise ValueError(f"incomplete matrix for {col}")
    return mat


def target_group_mask(cells: pd.DataFrame, group: str) -> np.ndarray:
    if group == "all":
        return np.ones(len(cells), dtype=bool)
    groups = {
        "S": ["S1", "S2", "S3", "S4"],
        "S124": ["S1", "S2", "S4"],
        "S12": ["S1", "S2"],
        "Q2S124": ["Q2", "S1", "S2", "S4"],
        "Q3S": ["Q3", "S1", "S2", "S3", "S4"],
        "Q2": ["Q2"],
        "S2": ["S2"],
        "S1S2": ["S1", "S2"],
    }
    if group not in groups:
        raise KeyError(group)
    return cells["target"].isin(groups[group]).to_numpy(dtype=bool)


def pick(cells: pd.DataFrame, score_col: str, k: int, group: str, base_mask: np.ndarray) -> np.ndarray:
    mask = target_group_mask(cells, group) & base_mask
    pool = cells[mask].sort_values(score_col, ascending=False).head(k)
    return pool["flat_idx"].to_numpy(dtype=int)


def apply_flat(z: np.ndarray, flat_idx: np.ndarray, target_z: np.ndarray, alpha: float) -> np.ndarray:
    out = z.copy().reshape(-1)
    tgt = target_z.reshape(-1)
    out[flat_idx] = (1.0 - alpha) * out[flat_idx] + alpha * tgt[flat_idx]
    return out.reshape(z.shape)


def make_candidate(
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    prob: np.ndarray,
    candidate_id: str,
    meta: dict[str, object],
    q_world: np.ndarray,
    memory_prob: np.ndarray,
    posterior_prob: np.ndarray,
    world_weight: np.ndarray,
    memory_weight: np.ndarray,
) -> dict[str, object]:
    path = OUT / f"submission_h038_{safe_id(candidate_id)}_{short_hash(prob)}.csv"
    write_submission(sample, prob, path)
    moved = np.abs(logit(prob) - logit(base_prob)) > 1.0e-9
    row_moved = moved.any(axis=1)
    rec = {
        "candidate_id": f"h038_{safe_id(candidate_id)}_{short_hash(prob)}",
        "file": path.name,
        "resolved_path": str(path),
        "changed_cells_vs_h012": int(moved.sum()),
        "changed_rows_vs_h012": int(row_moved.sum()),
        "mean_abs_prob_move_h012": float(np.mean(np.abs(prob - base_prob))),
        "max_abs_prob_move_h012": float(np.max(np.abs(prob - base_prob))),
        "mean_abs_logit_move_h012": float(np.mean(np.abs(logit(prob) - logit(base_prob)))),
        "max_abs_logit_move_h012": float(np.max(np.abs(logit(prob) - logit(base_prob)))),
        "world_cell_delta_vs_h012": weighted_delta(prob, base_prob, q_world, world_weight),
        "world_row_delta_vs_h012": weighted_delta(prob, base_prob, q_world, np.maximum(world_weight.mean(axis=1), 0.0)),
        "memory_delta_vs_h012": weighted_delta(prob, base_prob, memory_prob, memory_weight),
        "posterior_delta_vs_h012": weighted_delta(prob, base_prob, posterior_prob, np.ones_like(base_prob)),
    }
    rec.update(meta)
    return rec


def generate_candidates(
    sample: pd.DataFrame,
    e247_prob: np.ndarray,
    h012_prob: np.ndarray,
    cells: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    n_rows = len(sample)
    q_world = array_from_cells(cells, "world_q_cond", n_rows)
    memory_prob = array_from_cells(cells, "memory_prob_full", n_rows)
    posterior_prob = array_from_cells(cells, "posterior_prob", n_rows)
    world_score = array_from_cells(cells, "cell_world_score", n_rows)
    row_public = array_from_cells(cells, "row_public_prob", n_rows)[:, 0]
    transition_score = array_from_cells(cells, "transition_exception_score", n_rows)
    repair_score = array_from_cells(cells, "transition_repair_score", n_rows)
    reliability = array_from_cells(cells, "row_full_reliability_q", n_rows)

    z_h012 = logit(h012_prob)
    z_q = logit(q_world)
    z_mem = logit(memory_prob)
    z_post = logit(posterior_prob)
    support = np.abs(logit(h012_prob) - logit(e247_prob)) > 1.0e-8
    world_weight = np.clip(0.60 * world_score + 0.25 * transition_score + 0.15 * row_public[:, None], 0.0, None)
    memory_weight = np.clip(0.55 * reliability + 0.45 * repair_score, 0.0, None)

    support_flat = support.reshape(-1)
    exception_mask = (
        cells["h012_changed"].to_numpy(dtype=bool)
        & cells["memory_disagrees_h012"].to_numpy(dtype=bool)
        & cells["world_opposes_memory"].to_numpy(dtype=bool)
    )
    underfit_mask = exception_mask & cells["world_agrees_ray"].to_numpy(dtype=bool)
    repair_mask = (
        cells["h012_changed"].to_numpy(dtype=bool)
        & cells["memory_agrees_h012"].to_numpy(dtype=bool)
        & (~cells["world_agrees_ray"].to_numpy(dtype=bool))
    )
    broad_world_mask = support_flat & (cells["cell_world_score"].to_numpy(dtype=np.float64) >= np.quantile(cells["cell_world_score"], 0.70))

    rows: list[dict[str, object]] = []
    seen: set[str] = set()

    def add_prob(prob: np.ndarray, cid: str, meta: dict[str, object]) -> None:
        digest = short_hash(prob)
        if digest in seen:
            return
        seen.add(digest)
        rows.append(make_candidate(sample, h012_prob, clip_prob(prob), cid, meta, q_world, memory_prob, posterior_prob, world_weight, memory_weight))

    for group in ["all", "S", "S124", "S12", "Q2S124", "Q3S"]:
        for k in [40, 80, 120, 180, 260, 420, 714]:
            idx = pick(cells, "transition_exception_score", k, group, exception_mask)
            if len(idx) == 0:
                continue
            for alpha in [0.025, 0.05, 0.08, 0.12, 0.18]:
                z = apply_flat(z_h012, idx, z_q, alpha)
                add_prob(
                    sigmoid(z),
                    f"exception_qpull_{group}_k{k}_a{alpha:g}",
                    {"family": "exception_qpull", "target_group": group, "k": len(idx), "alpha": alpha},
                )
            for alpha in [0.04, 0.08, 0.14, 0.22]:
                z = apply_flat(z_h012, idx, z_post, alpha)
                add_prob(
                    sigmoid(z),
                    f"exception_postpull_{group}_k{k}_a{alpha:g}",
                    {"family": "exception_postpull", "target_group": group, "k": len(idx), "alpha": alpha},
                )

    for group in ["all", "S124", "Q2S124", "S1S2"]:
        for k in [40, 80, 140, 220, 360]:
            idx = pick(cells, "transition_repair_score", k, group, repair_mask)
            if len(idx) == 0:
                continue
            for alpha in [0.04, 0.08, 0.14, 0.24, 0.38]:
                z = apply_flat(z_h012, idx, z_mem, alpha)
                add_prob(
                    sigmoid(z),
                    f"memory_repair_{group}_k{k}_a{alpha:g}",
                    {"family": "memory_repair", "target_group": group, "k": len(idx), "alpha": alpha},
                )

    # Row-vector transition actions: if H012 is an event detector, row identity
    # should matter more than independent cell rank.  For selected rows, move
    # exception cells toward public-world q and repair cells toward memory.
    row_frame = (
        cells.groupby(["row", "subject_id", "sleep_date", "lifelog_date"])
        .agg(
            row_transition_score=("transition_row_score", "mean"),
            row_public_prob=("row_public_prob", "max"),
            exception_mean=("transition_exception_score", "mean"),
            repair_mean=("transition_repair_score", "mean"),
            changed_cells=("h012_changed", "sum"),
        )
        .reset_index()
    )
    row_frame["row_route_score"] = (
        0.40 * rank01(row_frame["row_transition_score"])
        + 0.30 * rank01(row_frame["row_public_prob"])
        + 0.20 * rank01(row_frame["exception_mean"])
        + 0.10 * rank01(row_frame["changed_cells"])
    )
    for n in [12, 20, 35, 55, 80, 120]:
        chosen_rows = set(row_frame.sort_values("row_route_score", ascending=False).head(n)["row"].astype(int))
        row_mask = cells["row"].isin(chosen_rows).to_numpy(dtype=bool)
        for group in ["all", "S124", "Q2S124", "Q3S"]:
            idx_q = pick(cells, "transition_exception_score", 9999, group, exception_mask & row_mask)
            idx_mem = pick(cells, "transition_repair_score", 9999, group, repair_mask & row_mask)
            if len(idx_q) + len(idx_mem) == 0:
                continue
            for aq, am in [(0.05, 0.00), (0.08, 0.04), (0.12, 0.06), (0.18, 0.08)]:
                z = z_h012.copy()
                if len(idx_q):
                    z = apply_flat(z, idx_q, z_q, aq)
                if len(idx_mem) and am > 0:
                    z = apply_flat(z, idx_mem, z_mem, am)
                add_prob(
                    sigmoid(z),
                    f"row_transition_{group}_r{n}_aq{aq:g}_am{am:g}",
                    {
                        "family": "row_transition",
                        "target_group": group,
                        "k": len(idx_q) + len(idx_mem),
                        "alpha": aq,
                        "mem_alpha": am,
                        "rows_selected": n,
                    },
                )

    # Broad world pressure with transition veto: the H036 celltop action failed
    # because it ignored route/memory context.  Keep only broad-world cells that
    # are also transition exceptions, and explicitly exclude repair cells.
    for group in ["all", "S124", "Q2S124", "Q3S"]:
        gate = broad_world_mask & exception_mask & target_group_mask(cells, group)
        idx = cells[gate].sort_values("cell_world_score", ascending=False).head(520)["flat_idx"].to_numpy(dtype=int)
        for k in [80, 160, 280, 420, len(idx)]:
            sub = idx[: min(k, len(idx))]
            if len(sub) == 0:
                continue
            for alpha in [0.04, 0.075, 0.11, 0.16]:
                z = apply_flat(z_h012, sub, z_q, alpha)
                add_prob(
                    sigmoid(z),
                    f"world_exception_veto_{group}_k{k}_a{alpha:g}",
                    {"family": "world_exception_veto", "target_group": group, "k": len(sub), "alpha": alpha},
                )

    candidates = pd.DataFrame(rows)
    candidates.to_csv(OUT / "h038_generated_candidates.csv", index=False)

    summary_rows = []
    for name, mask in [
        ("support", support_flat),
        ("memory_exception", exception_mask),
        ("underfit_exception", underfit_mask),
        ("memory_repair", repair_mask),
        ("broad_world_exception", broad_world_mask & exception_mask),
    ]:
        part = cells[mask]
        summary_rows.append(
            {
                "region": name,
                "cells": len(part),
                "posterior_gain_sum": float(part["posterior_gain"].sum()) if len(part) else 0.0,
                "cell_world_score_sum": float(part["cell_world_score"].sum()) if len(part) else 0.0,
                "mean_transition_exception_score": float(part["transition_exception_score"].mean()) if len(part) else 0.0,
                "targets": str({t: int((part["target"] == t).sum()) for t in TARGETS}),
            }
        )
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(OUT / "h038_transition_region_summary.csv", index=False)
    row_frame.to_csv(OUT / "h038_row_transition_scores.csv", index=False)
    return candidates, summary


def score_candidates(candidates: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    h036 = import_module(HITL / "h036_global_public_world_solver_jepa.py", "h036_for_h038")
    h024_features, h024_models, h024_preds = h036.h024_score_candidates(candidates)
    scored = candidates.copy()
    if not h024_preds.empty:
        scored = scored.merge(h024_preds, on="resolved_path", how="left")
    h025_scores, h025_cells = h036.h025_score_candidates(scored)
    if not h025_scores.empty:
        keep = [
            "file",
            "h025_score",
            "pred_gain_top1200_sum",
            "pred_gain_mean_moved",
            "pred_positive_rate_moved",
            "ood_abs_delta_rate",
        ]
        scored = scored.merge(h025_scores[[c for c in keep if c in h025_scores.columns]], on="file", how="left")

    h024_margin = scored.get("pre_h012_h024_margin_vs_h012_median", pd.Series(np.nan, index=scored.index)).fillna(0.02)
    h024_support = scored.get("pre_h012_h024_support_better_than_h012", pd.Series(0.0, index=scored.index)).fillna(0.0)
    h025_score = scored.get("h025_score", pd.Series(0.0, index=scored.index)).fillna(0.0)
    scored["h038_score"] = (
        rank01(scored["world_cell_delta_vs_h012"], high=False)
        + 0.75 * rank01(scored["posterior_delta_vs_h012"], high=False)
        + rank01(h024_margin, high=False)
        + 0.60 * rank01(h025_score, high=False)
        - 0.80 * h024_support
        + 0.20 * rank01(scored["max_abs_prob_move_h012"], high=True)
    )
    scored = scored.sort_values(["h038_score", "world_cell_delta_vs_h012", "pre_h012_h024_margin_vs_h012_median"]).reset_index(drop=True)
    return scored, h024_features, h024_models, h025_cells


def run_rowperm(selected_file: str) -> pd.DataFrame:
    h036 = import_module(HITL / "h036_global_public_world_solver_jepa.py", "h036_for_h038_rowperm")
    return h036.run_rowperm_stress(selected_file)


def decide(scored: pd.DataFrame, rowperm: pd.DataFrame) -> pd.DataFrame:
    if scored.empty:
        return pd.DataFrame([{"decision": "no_candidate", "promote": False, "reason": "no candidates generated"}])
    selected = scored.iloc[0]
    pre_margin = float(selected.get("pre_h012_h024_margin_vs_h012_median", np.nan))
    pre_support = float(selected.get("pre_h012_h024_support_better_than_h012", np.nan))
    world_cell = float(selected.get("world_cell_delta_vs_h012", np.nan))
    posterior = float(selected.get("posterior_delta_vs_h012", np.nan))
    memory = float(selected.get("memory_delta_vs_h012", np.nan))
    rowperm_p = 1.0
    rowperm_real = np.nan
    if not rowperm.empty and "perm_top1200_sum" in rowperm.columns:
        rowperm_real = float(rowperm["real_top1200_sum"].iloc[0])
        rowperm_p = float(np.mean(rowperm["perm_top1200_sum"].to_numpy(dtype=np.float64) >= rowperm_real))

    promote = bool(
        np.isfinite(world_cell)
        and world_cell < -0.00020
        and np.isfinite(posterior)
        and posterior < -0.00010
        and np.isfinite(pre_margin)
        and pre_margin < -0.00010
        and np.isfinite(pre_support)
        and pre_support >= 0.55
        and rowperm_p <= 0.35
    )
    reasons = []
    if not np.isfinite(world_cell) or world_cell >= -0.00020:
        reasons.append("world-cell gain too small")
    if not np.isfinite(posterior) or posterior >= -0.00010:
        reasons.append("H012-posterior gain too small")
    if not np.isfinite(pre_margin) or pre_margin >= -0.00010:
        reasons.append("H024 pre-H012 margin not below H012")
    if not np.isfinite(pre_support) or pre_support < 0.55:
        reasons.append("H024 support below 55%")
    if rowperm_p > 0.35:
        reasons.append("H025 row permutation stress weak")
    return pd.DataFrame(
        [
            {
                "decision": "promote" if promote else "do_not_promote",
                "promote": promote,
                "selected_candidate_id": selected["candidate_id"],
                "selected_file": selected["file"],
                "selected_resolved_path": selected["resolved_path"],
                "family": selected.get("family", ""),
                "target_group": selected.get("target_group", ""),
                "world_cell_delta_vs_h012": world_cell,
                "posterior_delta_vs_h012": posterior,
                "memory_delta_vs_h012": memory,
                "pre_h012_h024_margin_vs_h012_median": pre_margin,
                "pre_h012_h024_support_better_than_h012": pre_support,
                "rowperm_real_top1200_sum": rowperm_real,
                "rowperm_p_perm_ge_real": rowperm_p,
                "reason": "; ".join(reasons) if reasons else "all promotion gates passed",
            }
        ]
    )


def write_report(summary: pd.DataFrame, scored: pd.DataFrame, decision: pd.DataFrame, rowperm: pd.DataFrame) -> None:
    lines: list[str] = []
    lines.append("# H038 Memory-Transition World Translator HS-JEPA\n\n")
    lines.append("## Question\n\n")
    lines.append(
        "Did H012 win by detecting within-person state transitions where same-subject memory is misleading, "
        "and can H036 public-world pressure be translated only through those transition cells/rows?\n\n"
    )
    lines.append("## Transition Regions\n\n")
    lines.append(md_table(summary, len(summary)) + "\n\n")
    lines.append("## Gate Counts\n\n")
    h024_margin = scored.get("pre_h012_h024_margin_vs_h012_median", pd.Series(np.nan, index=scored.index))
    h024_support = scored.get("pre_h012_h024_support_better_than_h012", pd.Series(np.nan, index=scored.index))
    gates = pd.DataFrame(
        [
            {
                "candidates": len(scored),
                "world_cell_lt_-0.0002": int((scored["world_cell_delta_vs_h012"] < -0.0002).sum()) if len(scored) else 0,
                "posterior_lt_-0.0001": int((scored["posterior_delta_vs_h012"] < -0.0001).sum()) if len(scored) else 0,
                "h024_margin_negative": int((h024_margin < 0.0).sum()),
                "h024_support_ge_0.55": int((h024_support >= 0.55).sum()),
                "world_and_h024_negative": int(((scored["world_cell_delta_vs_h012"] < -0.0002) & (h024_margin < 0.0)).sum()) if len(scored) else 0,
            }
        ]
    )
    lines.append(md_table(gates, 1) + "\n\n")
    lines.append("## Top Candidates\n\n")
    cols = [
        "candidate_id",
        "family",
        "target_group",
        "k",
        "alpha",
        "changed_cells_vs_h012",
        "world_cell_delta_vs_h012",
        "posterior_delta_vs_h012",
        "memory_delta_vs_h012",
        "pre_h012_h024_pred_public_median",
        "pre_h012_h024_margin_vs_h012_median",
        "pre_h012_h024_support_better_than_h012",
        "h025_score",
        "h038_score",
    ]
    lines.append(md_table(scored[[c for c in cols if c in scored.columns]].head(25), 25) if len(scored) else "_empty_")
    lines.append("\n\n## Row-Permutation Stress\n\n")
    if rowperm.empty:
        lines.append("_empty_\n\n")
    elif "perm_top1200_sum" in rowperm.columns:
        p = float(np.mean(rowperm["perm_top1200_sum"].to_numpy(dtype=np.float64) >= rowperm["real_top1200_sum"].iloc[0]))
        lines.append(f"- rowperm p(perm >= real): `{p:.9f}`\n\n")
        lines.append(md_table(rowperm.head(8), 8) + "\n\n")
    else:
        lines.append(md_table(rowperm, 5) + "\n\n")
    lines.append("## Decision\n\n")
    lines.append(md_table(decision, 1) + "\n\n")
    lines.append("## Interpretation\n\n")
    lines.append(
        "- Passing would mean the post-H012 translator is not H012-ray amplitude, but a memory-transition/public-world route gate.\n"
        "- Failing means subject-state memory remains a strong contrastive diagnosis of H012, but still not an action translator.\n"
    )
    (OUT / "h038_report.md").write_text("".join(lines), encoding="utf-8")


def main() -> None:
    h012 = load_sub(H012)
    sample = h012[KEYS].copy()
    e247 = load_sub(E247, sample)
    h012_prob = h012[TARGETS].to_numpy(dtype=np.float64)
    e247_prob = e247[TARGETS].to_numpy(dtype=np.float64)
    cells = load_cell_state(sample, e247_prob, h012_prob)
    candidates, summary = generate_candidates(sample, e247_prob, h012_prob, cells)
    scored, h024_features, h024_models, h025_cells = score_candidates(candidates)
    scored.to_csv(OUT / "h038_candidate_scores.csv", index=False)
    h024_features.to_csv(OUT / "h038_h024_features.csv", index=False)
    h024_models.to_csv(OUT / "h038_h024_model_scores.csv", index=False)
    if not h025_cells.empty:
        h025_cells.to_csv(OUT / "h038_h025_top_cells.csv", index=False)

    rowperm = pd.DataFrame()
    if not scored.empty:
        rowperm = run_rowperm(str(scored.iloc[0]["resolved_path"]))
        rowperm.to_csv(OUT / "h038_selected_h025_rowperm_stress.csv", index=False)

    decision = decide(scored, rowperm)
    decision.to_csv(OUT / "h038_decision.csv", index=False)
    if bool(decision.iloc[0].get("promote", False)):
        selected_path = Path(str(decision.iloc[0]["selected_resolved_path"]))
        root_name = selected_path.name.replace(".csv", "_uploadsafe.csv")
        shutil.copy2(selected_path, ROOT / root_name)
        decision.loc[0, "promoted_root_file"] = root_name
        decision.to_csv(OUT / "h038_decision.csv", index=False)

    write_report(summary, scored, decision, rowperm)
    print(f"H038 candidates: {len(scored)}")
    if not scored.empty:
        print(f"H038 selected: {scored.iloc[0]['candidate_id']}")
        print(f"H038 selected world cell delta: {float(scored.iloc[0]['world_cell_delta_vs_h012']):.9f}")
    print(f"H038 decision: {decision.iloc[0]['decision']} - {decision.iloc[0]['reason']}")


if __name__ == "__main__":
    main()
