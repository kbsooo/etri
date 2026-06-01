#!/usr/bin/env python3
"""H039: failed-translator nullspace HS-JEPA.

H036 found a strong hidden public-world representation.  H037 and H038 then
showed that obvious translators fail: support/ray amplitude and memory
transition actions both move into directions rejected by H024/H025.

H039 treats those failures as supervision rather than dead ends:

    context = H036 public-world pressure + H038 human memory-transition state
    negative target = directions from H036/H037/H038 candidates that looked
                      world-useful but action-unhealthy
    positive hint = the small survivor cone of candidates least disliked by H024
    action = project H036 pressure away from failure axes, optionally through
             the survivor cone, then materialize sparse residual probability
             moves around H012

If this works, the missing translator is approximately a nullspace/survivor-cone
law.  If it fails, the post-H012 decoder is not a linear projection of known
failure directions; it needs a discrete route/private-public model.
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
OUT = HITL / "h039_failed_translator_nullspace_jepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1.0e-6
H012 = "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"
E247 = "submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv"
H012_LB = 0.5681234831


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


def safe_id(text: str, limit: int = 92) -> str:
    keep = []
    for ch in str(text):
        keep.append(ch if ch.isalnum() or ch in "._-" else "_")
    return "".join(keep).strip("_")[:limit].strip("_")


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(prob, 12).tobytes()).hexdigest()[:8]


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


def h036_module(name: str = "h036_for_h039") -> object:
    return import_module(HITL / "h036_global_public_world_solver_jepa.py", name)


def load_sub(name: str | Path, sample: pd.DataFrame | None = None) -> pd.DataFrame:
    h036 = h036_module("h036_for_h039_loader")
    return h036.load_sub(name, sample)


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


def array_from_cells(cells: pd.DataFrame, col: str, n_rows: int, default: float | None = None) -> np.ndarray:
    mat = np.full((n_rows, len(TARGETS)), np.nan, dtype=np.float64)
    for rec in cells[["row", "target_i", col]].to_dict("records"):
        mat[int(rec["row"]), int(rec["target_i"])] = float(rec[col])
    if np.isnan(mat).any():
        if default is None:
            raise ValueError(f"incomplete matrix for {col}")
        mat = np.nan_to_num(mat, nan=default)
    return mat


def load_cell_state(sample: pd.DataFrame, h012_prob: np.ndarray, e247_prob: np.ndarray) -> pd.DataFrame:
    path = HITL / "h038_memory_transition_world_translator_jepa" / "h038_cell_state.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    cells = pd.read_csv(path)
    cells["target_i"] = cells["target"].map({t: i for i, t in enumerate(TARGETS)}).astype(int)
    cells = cells.sort_values(["row", "target_i"]).reset_index(drop=True)
    if len(cells) != len(sample) * len(TARGETS):
        raise ValueError(f"bad cell state size: {len(cells)}")
    z_h012 = logit(h012_prob)
    z_e247 = logit(e247_prob)
    ray = (z_h012 - z_e247).reshape(-1)
    cells["support"] = np.abs(ray) > 1.0e-8
    for col in [
        "world_q_cond",
        "posterior_prob",
        "memory_prob_full",
        "cell_world_score",
        "row_public_prob",
        "transition_exception_score",
        "transition_repair_score",
        "posterior_gain",
        "row_full_reliability_q",
        "memory_alignment",
    ]:
        if col not in cells.columns:
            cells[col] = 0.0
        cells[col] = cells[col].fillna(0.0)
    for col in ["memory_disagrees_h012", "memory_agrees_h012", "world_opposes_memory", "world_agrees_ray"]:
        if col not in cells.columns:
            cells[col] = False
        cells[col] = cells[col].fillna(False).astype(bool)
    cells["flat_idx"] = cells["row"].astype(int) * len(TARGETS) + cells["target_i"].astype(int)
    return cells


def harmonize_candidate_scores() -> pd.DataFrame:
    specs = [
        ("h036", HITL / "h036_global_public_world_solver_jepa" / "h036_candidate_scores.csv"),
        ("h037", HITL / "h037_fixed_point_translator_jepa" / "h037_candidate_scores.csv"),
        ("h038", HITL / "h038_memory_transition_world_translator_jepa" / "h038_candidate_scores.csv"),
    ]
    frames = []
    for source, path in specs:
        if not path.exists():
            continue
        df = pd.read_csv(path)
        df["source_experiment"] = source
        if "world_cell_delta_vs_h012" not in df.columns:
            df["world_cell_delta_vs_h012"] = df.get("world_expected_delta_vs_h012", np.nan)
        if "posterior_delta_vs_h012" not in df.columns:
            df["posterior_delta_vs_h012"] = np.nan
        if "changed_cells_vs_h012" not in df.columns:
            df["changed_cells_vs_h012"] = df.get("changed_cells", np.nan)
        for col in [
            "pre_h012_h024_margin_vs_h012_median",
            "pre_h012_h024_support_better_than_h012",
            "h025_score",
            "mean_abs_logit_move_h012",
            "mean_abs_prob_move_h012",
            "max_abs_prob_move_h012",
            "world_cell_delta_vs_h012",
            "posterior_delta_vs_h012",
        ]:
            if col not in df.columns:
                df[col] = np.nan
        frames.append(df)
    if not frames:
        raise RuntimeError("no candidate score files found")
    cand = pd.concat(frames, ignore_index=True, sort=False)
    cand = cand[cand["resolved_path"].map(lambda p: Path(str(p)).exists())].reset_index(drop=True)
    if cand.empty:
        raise RuntimeError("candidate score rows exist, but no materialized files are present")

    margin = cand["pre_h012_h024_margin_vs_h012_median"].fillna(0.02).to_numpy(dtype=np.float64)
    support = cand["pre_h012_h024_support_better_than_h012"].fillna(0.0).to_numpy(dtype=np.float64)
    h025 = cand["h025_score"].fillna(cand["h025_score"].median()).fillna(0.0).to_numpy(dtype=np.float64)
    world = cand["world_cell_delta_vs_h012"].fillna(0.0).to_numpy(dtype=np.float64)
    mag = cand["mean_abs_logit_move_h012"].fillna(cand["mean_abs_prob_move_h012"]).fillna(0.0).to_numpy(dtype=np.float64)
    cand["badness_weight"] = np.clip(
        0.42 * rank01(margin, high=True)
        + 0.24 * rank01(1.0 - support, high=True)
        + 0.16 * rank01(-world, high=True)
        + 0.10 * rank01(h025, high=True)
        + 0.08 * rank01(mag, high=True),
        0.05,
        1.0,
    )
    cand["world_good_action_bad"] = (world < -0.00005) & (margin > 0.00020) & (support < 0.55)
    cand["h024_survivor_hint"] = (margin <= np.nanquantile(margin, 0.12)) | (support >= 0.40)
    cand["source_candidate_id"] = cand["source_experiment"].astype(str) + ":" + cand["candidate_id"].astype(str)
    cand.to_csv(OUT / "h039_source_candidate_pool.csv", index=False)
    return cand


def load_direction_matrix(
    cand: pd.DataFrame,
    sample: pd.DataFrame,
    h012_prob: np.ndarray,
    weight_col: str,
) -> tuple[np.ndarray, pd.DataFrame]:
    z_h012 = logit(h012_prob)
    rows = []
    meta = []
    for rec in cand.to_dict("records"):
        try:
            prob = load_sub(str(rec["resolved_path"]), sample)[TARGETS].to_numpy(dtype=np.float64)
        except Exception:
            continue
        dz = (logit(prob) - z_h012).reshape(-1)
        norm = float(np.linalg.norm(dz))
        if not np.isfinite(norm) or norm <= 1.0e-10:
            continue
        weight = float(rec.get(weight_col, 1.0))
        rows.append(dz / norm * np.sqrt(max(weight, 1.0e-6)))
        meta.append(
            {
                "source_candidate_id": rec.get("source_candidate_id", ""),
                "source_experiment": rec.get("source_experiment", ""),
                "candidate_id": rec.get("candidate_id", ""),
                "norm": norm,
                "weight": weight,
                "world_cell_delta_vs_h012": rec.get("world_cell_delta_vs_h012", np.nan),
                "pre_h012_h024_margin_vs_h012_median": rec.get("pre_h012_h024_margin_vs_h012_median", np.nan),
                "pre_h012_h024_support_better_than_h012": rec.get("pre_h012_h024_support_better_than_h012", np.nan),
            }
        )
    if not rows:
        raise RuntimeError("empty direction matrix")
    return np.vstack(rows), pd.DataFrame(meta)


def svd_basis(x: np.ndarray, max_k: int) -> tuple[np.ndarray, np.ndarray, pd.DataFrame]:
    k = int(min(max_k, x.shape[0], x.shape[1]))
    u, s, vt = np.linalg.svd(x, full_matrices=False)
    vt = vt[:k].copy()
    s = s[:k].copy()
    denom = float(np.sum(s * s)) if len(s) else 1.0
    diag = pd.DataFrame(
        {
            "pc": np.arange(1, len(s) + 1),
            "singular": s,
            "energy": (s * s) / denom if denom > 0 else np.zeros_like(s),
            "cum_energy": np.cumsum((s * s) / denom) if denom > 0 else np.zeros_like(s),
        }
    )
    return vt, s, diag


def project_remove(vec: np.ndarray, basis: np.ndarray, k: int) -> np.ndarray:
    if basis.size == 0 or k <= 0:
        return vec.copy()
    b = basis[: min(k, len(basis))]
    return vec - b.T @ (b @ vec)


def project_onto(vec: np.ndarray, basis: np.ndarray, k: int) -> np.ndarray:
    if basis.size == 0 or k <= 0:
        return np.zeros_like(vec)
    b = basis[: min(k, len(basis))]
    return b.T @ (b @ vec)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    an = float(np.linalg.norm(a))
    bn = float(np.linalg.norm(b))
    if an <= 1.0e-12 or bn <= 1.0e-12:
        return 0.0
    return float(np.dot(a, b) / (an * bn))


def first_order_gain(step: np.ndarray, h012_prob: np.ndarray, q: np.ndarray, weight: np.ndarray) -> np.ndarray:
    grad = h012_prob - q
    return -grad.reshape(-1) * step * weight.reshape(-1)


def top_mask_from_cells(cells: pd.DataFrame, name: str) -> np.ndarray:
    support = cells["support"].to_numpy(dtype=bool)
    world_score = cells["cell_world_score"].to_numpy(dtype=np.float64)
    transition = cells["transition_exception_score"].to_numpy(dtype=np.float64)
    exception = (
        support
        & cells["memory_disagrees_h012"].to_numpy(dtype=bool)
        & cells["world_opposes_memory"].to_numpy(dtype=bool)
    )
    aligned = support & cells["world_agrees_ray"].to_numpy(dtype=bool)
    if name == "support":
        return support
    if name == "exception":
        return exception
    if name == "aligned_support":
        return aligned
    if name == "world_high_support":
        return support & (world_score >= np.nanquantile(world_score, 0.72))
    if name == "transition_high_support":
        return support & (transition >= np.nanquantile(transition, 0.72))
    if name == "all_world_positive":
        return world_score >= np.nanquantile(world_score, 0.78)
    raise ValueError(name)


def materialize_candidate(
    sample: pd.DataFrame,
    h012_prob: np.ndarray,
    q_world: np.ndarray,
    q_post: np.ndarray,
    q_mem: np.ndarray,
    world_weight: np.ndarray,
    memory_weight: np.ndarray,
    step: np.ndarray,
    selected_flat: np.ndarray,
    candidate_id: str,
    meta: dict[str, object],
) -> dict[str, object]:
    z = logit(h012_prob).reshape(-1)
    move = np.zeros_like(z)
    move[selected_flat] = step[selected_flat]
    prob = sigmoid((z + move).reshape(h012_prob.shape))
    path = OUT / f"submission_h039_{safe_id(candidate_id)}_{short_hash(prob)}.csv"
    write_submission(sample, prob, path)
    changed = np.abs(prob - h012_prob) > 1.0e-12
    row_changed = changed.any(axis=1)
    return {
        "candidate_id": f"h039_{safe_id(candidate_id)}_{short_hash(prob)}",
        "file": path.name,
        "resolved_path": str(path.resolve()),
        "changed_cells_vs_h012": int(changed.sum()),
        "changed_rows_vs_h012": int(row_changed.sum()),
        "mean_abs_prob_move_h012": float(np.mean(np.abs(prob - h012_prob))),
        "max_abs_prob_move_h012": float(np.max(np.abs(prob - h012_prob))),
        "mean_abs_logit_move_h012": float(np.mean(np.abs(move[selected_flat]))) if len(selected_flat) else 0.0,
        "max_abs_logit_move_h012": float(np.max(np.abs(move[selected_flat]))) if len(selected_flat) else 0.0,
        "world_cell_delta_vs_h012": weighted_delta(prob, h012_prob, q_world, world_weight),
        "posterior_delta_vs_h012": weighted_delta(prob, h012_prob, q_post, world_weight),
        "memory_delta_vs_h012": weighted_delta(prob, h012_prob, q_mem, memory_weight),
        **meta,
    }


def generate_candidates(
    sample: pd.DataFrame,
    h012_prob: np.ndarray,
    e247_prob: np.ndarray,
    cells: pd.DataFrame,
    bases: dict[str, np.ndarray],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    n_rows = len(sample)
    q_world = clip_prob(array_from_cells(cells, "world_q_cond", n_rows))
    q_post = clip_prob(array_from_cells(cells, "posterior_prob", n_rows))
    q_mem = clip_prob(array_from_cells(cells, "memory_prob_full", n_rows))
    cell_world = array_from_cells(cells, "cell_world_score", n_rows, 0.0)
    row_public = array_from_cells(cells, "row_public_prob", n_rows, 0.0)
    transition = array_from_cells(cells, "transition_exception_score", n_rows, 0.0)
    repair = array_from_cells(cells, "transition_repair_score", n_rows, 0.0)
    reliability = array_from_cells(cells, "row_full_reliability_q", n_rows, 0.0)

    world_weight = np.clip(
        0.55 * rank01(cell_world.reshape(-1)).reshape(n_rows, len(TARGETS))
        + 0.25 * rank01(transition.reshape(-1)).reshape(n_rows, len(TARGETS))
        + 0.20 * rank01(row_public.reshape(-1)).reshape(n_rows, len(TARGETS)),
        0.0,
        1.0,
    )
    memory_weight = np.clip(
        0.50 * rank01(reliability.reshape(-1)).reshape(n_rows, len(TARGETS))
        + 0.30 * rank01(repair.reshape(-1)).reshape(n_rows, len(TARGETS))
        + 0.20 * rank01(1.0 - np.abs(array_from_cells(cells, "memory_alignment", n_rows, 0.0)).reshape(-1)).reshape(n_rows, len(TARGETS)),
        0.0,
        1.0,
    )

    z_h012 = logit(h012_prob)
    z_e247 = logit(e247_prob)
    z_world = logit(q_world)
    z_post = logit(q_post)
    support = (np.abs(z_h012 - z_e247) > 1.0e-8).reshape(-1)
    ray = (z_h012 - z_e247).reshape(-1)

    source_vectors = {
        "world": (z_world - z_h012).reshape(-1),
        "posterior_world_mix": (0.65 * (z_world - z_h012) + 0.35 * (z_post - z_h012)).reshape(-1),
        "transition_world": ((z_world - z_h012) * (0.35 + 0.65 * transition)).reshape(-1),
    }

    rows = []
    seen: set[str] = set()
    diag_rows = []

    for source_name, vec0 in source_vectors.items():
        for forbid_name in ["world_bad", "all_bad"]:
            forbid_basis = bases[forbid_name]
            for forbid_k in [8, 24]:
                if forbid_k > len(forbid_basis):
                    continue
                removed = project_remove(vec0, forbid_basis, forbid_k)
                for mode, vec in [
                    ("remove_only", removed),
                    ("allow_cone", project_onto(removed, bases["survivor"], 12)),
                    ("double_null", project_remove(removed, bases["all_bad"], min(24, len(bases["all_bad"])))),
                ]:
                    if float(np.linalg.norm(vec)) <= 1.0e-12:
                        continue
                    for mask_name in [
                        "support",
                        "exception",
                        "world_high_support",
                        "transition_high_support",
                    ]:
                        route = top_mask_from_cells(cells, mask_name)
                        gain = first_order_gain(vec, h012_prob, q_world, world_weight)
                        usable = route & (gain > 0.0) & np.isfinite(vec)
                        if not usable.any():
                            continue
                        order = np.argsort(-np.where(usable, gain, -np.inf))
                        usable_count = int(np.isfinite(np.where(usable, gain, -np.inf)[order]).sum())
                        for k_cells in [48, 120, 280]:
                            chosen = order[: min(k_cells, usable_count)]
                            chosen = chosen[np.isfinite(gain[chosen])]
                            if len(chosen) < 8:
                                continue
                            selected_abs = np.abs(vec[chosen])
                            scale_base = float(np.quantile(selected_abs[selected_abs > 0.0], 0.90)) if np.any(selected_abs > 0.0) else 0.0
                            if scale_base <= 1.0e-12:
                                continue
                            for cap in [0.022, 0.060]:
                                step = np.zeros_like(vec)
                                step[chosen] = np.clip(vec[chosen] * (cap / scale_base), -2.0 * cap, 2.0 * cap)
                                # Do not let an unconstrained projection reverse the first-order world direction.
                                keep = gain[chosen] > 0.0
                                chosen2 = chosen[keep]
                                if len(chosen2) < 8:
                                    continue
                                step[np.setdiff1d(chosen, chosen2, assume_unique=False)] = 0.0
                                cid = f"{source_name}_{mode}_{forbid_name}_pc{forbid_k}_{mask_name}_k{len(chosen2)}_cap{cap:g}"
                                digest = hashlib.sha1(np.round(step, 10).tobytes()).hexdigest()[:10]
                                if digest in seen:
                                    continue
                                seen.add(digest)
                                meta = {
                                    "family": f"{source_name}_{mode}",
                                    "source_vector": source_name,
                                    "projection_mode": mode,
                                    "forbid_basis": forbid_name,
                                    "forbid_pcs": forbid_k,
                                    "route_mask": mask_name,
                                    "k": int(len(chosen2)),
                                    "cap": cap,
                                    "cosine_to_world": cosine(step, source_vectors["world"]),
                                    "cosine_to_h012_ray": cosine(step, ray),
                                    "forbidden_cosine": cosine(step, project_onto(step, forbid_basis, forbid_k)),
                                    "first_order_gain_sum": float(np.sum(gain[chosen2])),
                                }
                                rows.append(
                                    materialize_candidate(
                                        sample,
                                        h012_prob,
                                        q_world,
                                        q_post,
                                        q_mem,
                                        world_weight,
                                        memory_weight,
                                        step,
                                        chosen2,
                                        cid,
                                        meta,
                                    )
                                )
                    diag_rows.append(
                        {
                            "source_vector": source_name,
                            "forbid_basis": forbid_name,
                            "forbid_pcs": forbid_k,
                            "removed_norm_ratio": float(np.linalg.norm(removed) / (np.linalg.norm(vec0) + 1.0e-12)),
                            "cosine_removed_to_world": cosine(removed, source_vectors["world"]),
                            "cosine_removed_to_ray": cosine(removed, ray),
                        }
                    )

    candidates = pd.DataFrame(rows)
    if not candidates.empty:
        candidates = candidates.drop_duplicates("resolved_path").reset_index(drop=True)
        if len(candidates) > 520:
            candidates["_internal_rank"] = (
                rank01(candidates["world_cell_delta_vs_h012"], high=False)
                + 0.65 * rank01(candidates["posterior_delta_vs_h012"], high=False)
                + 0.35 * rank01(candidates["forbidden_cosine"], high=False)
                + 0.15 * rank01(candidates["max_abs_prob_move_h012"], high=True)
            )
            candidates = candidates.sort_values("_internal_rank").head(520).drop(columns=["_internal_rank"]).reset_index(drop=True)
    candidates.to_csv(OUT / "h039_generated_candidates.csv", index=False)
    diag = pd.DataFrame(diag_rows).drop_duplicates().reset_index(drop=True)
    diag.to_csv(OUT / "h039_projection_diagnostics.csv", index=False)
    return candidates, diag


def score_candidates(candidates: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if candidates.empty:
        return candidates, pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    h036 = h036_module("h036_for_h039_scoring")
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
    scored["h039_score"] = (
        1.15 * rank01(scored["world_cell_delta_vs_h012"], high=False)
        + 0.75 * rank01(scored["posterior_delta_vs_h012"], high=False)
        + 1.15 * rank01(h024_margin, high=False)
        + 0.65 * rank01(h025_score, high=False)
        + 0.25 * rank01(scored["forbidden_cosine"], high=False)
        - 0.95 * h024_support
        + 0.12 * rank01(scored["max_abs_prob_move_h012"], high=True)
    )
    scored = scored.sort_values(["h039_score", "world_cell_delta_vs_h012", "pre_h012_h024_margin_vs_h012_median"]).reset_index(drop=True)
    return scored, h024_features, h024_models, h025_cells


def run_rowperm(selected_file: str) -> pd.DataFrame:
    h036 = h036_module("h036_for_h039_rowperm")
    return h036.run_rowperm_stress(selected_file)


def decide(scored: pd.DataFrame, rowperm: pd.DataFrame) -> pd.DataFrame:
    if scored.empty:
        return pd.DataFrame([{"decision": "no_candidate", "promote": False, "reason": "no candidates generated"}])
    selected = scored.iloc[0]
    pre_margin = float(selected.get("pre_h012_h024_margin_vs_h012_median", np.nan))
    pre_support = float(selected.get("pre_h012_h024_support_better_than_h012", np.nan))
    world_cell = float(selected.get("world_cell_delta_vs_h012", np.nan))
    posterior = float(selected.get("posterior_delta_vs_h012", np.nan))
    h025 = float(selected.get("h025_score", np.nan))
    rowperm_p = 1.0
    rowperm_real = np.nan
    if not rowperm.empty and "perm_top1200_sum" in rowperm.columns:
        rowperm_real = float(rowperm["real_top1200_sum"].iloc[0])
        rowperm_p = float(np.mean(rowperm["perm_top1200_sum"].to_numpy(dtype=np.float64) >= rowperm_real))
    promote = bool(
        np.isfinite(world_cell)
        and world_cell < -0.00018
        and np.isfinite(posterior)
        and posterior < -0.00006
        and np.isfinite(pre_margin)
        and pre_margin < -0.00010
        and np.isfinite(pre_support)
        and pre_support >= 0.55
        and rowperm_p <= 0.35
    )
    reasons = []
    if not np.isfinite(world_cell) or world_cell >= -0.00018:
        reasons.append("world-cell gain too small")
    if not np.isfinite(posterior) or posterior >= -0.00006:
        reasons.append("posterior gain too small")
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
                "source_vector": selected.get("source_vector", ""),
                "projection_mode": selected.get("projection_mode", ""),
                "forbid_basis": selected.get("forbid_basis", ""),
                "forbid_pcs": selected.get("forbid_pcs", np.nan),
                "route_mask": selected.get("route_mask", ""),
                "world_cell_delta_vs_h012": world_cell,
                "posterior_delta_vs_h012": posterior,
                "pre_h012_h024_margin_vs_h012_median": pre_margin,
                "pre_h012_h024_support_better_than_h012": pre_support,
                "h025_score": h025,
                "rowperm_real_top1200_sum": rowperm_real,
                "rowperm_p_perm_ge_real": rowperm_p,
                "reason": "; ".join(reasons) if reasons else "all promotion gates passed",
            }
        ]
    )


def write_report(
    pool_summary: pd.DataFrame,
    basis_diag: pd.DataFrame,
    proj_diag: pd.DataFrame,
    scored: pd.DataFrame,
    decision: pd.DataFrame,
    rowperm: pd.DataFrame,
) -> None:
    lines = [
        "# H039 Failed-Translator Nullspace HS-JEPA",
        "",
        "## Question",
        "",
        "Can H036 hidden public-world pressure become action-safe if we remove the",
        "principal directions learned from H036/H037/H038 failed translators and",
        "optionally pass the residual through the H024 survivor cone?",
        "",
        "## Source Pool",
        "",
        md_table(pool_summary, 20),
        "",
        "## Basis Diagnostics",
        "",
        md_table(basis_diag, 30),
        "",
        "## Projection Diagnostics",
        "",
        md_table(proj_diag, 30),
        "",
        "## Gate Counts",
        "",
    ]
    if scored.empty:
        gate = pd.DataFrame([{"candidates": 0}])
    else:
        h024_margin = scored.get("pre_h012_h024_margin_vs_h012_median", pd.Series(np.nan, index=scored.index))
        h024_support = scored.get("pre_h012_h024_support_better_than_h012", pd.Series(np.nan, index=scored.index))
        gate = pd.DataFrame(
            [
                {
                    "candidates": len(scored),
                    "world_cell_lt_-0.00018": int((scored["world_cell_delta_vs_h012"] < -0.00018).sum()),
                    "posterior_lt_-0.00006": int((scored["posterior_delta_vs_h012"] < -0.00006).sum()),
                    "h024_margin_negative": int((h024_margin < 0.0).sum()),
                    "h024_margin_lt_-0.00010": int((h024_margin < -0.00010).sum()),
                    "h024_support_ge_0.55": int((h024_support >= 0.55).sum()),
                    "world_and_h024_negative": int(((scored["world_cell_delta_vs_h012"] < -0.00018) & (h024_margin < 0.0)).sum()),
                }
            ]
        )
    lines.extend([md_table(gate, 5), "", "## Top Candidates", ""])
    keep = [
        "candidate_id",
        "family",
        "projection_mode",
        "forbid_basis",
        "forbid_pcs",
        "route_mask",
        "k",
        "cap",
        "changed_cells_vs_h012",
        "world_cell_delta_vs_h012",
        "posterior_delta_vs_h012",
        "pre_h012_h024_margin_vs_h012_median",
        "pre_h012_h024_support_better_than_h012",
        "h025_score",
        "forbidden_cosine",
        "h039_score",
    ]
    lines.append(md_table(scored[[c for c in keep if c in scored.columns]].head(24), 24) if not scored.empty else "_empty_")
    lines.extend(["", "## Row-Permutation Stress", ""])
    if rowperm.empty:
        lines.append("_not run_")
    else:
        p = float(np.mean(rowperm["perm_top1200_sum"].to_numpy(dtype=np.float64) >= float(rowperm["real_top1200_sum"].iloc[0])))
        lines.append(f"- rowperm p(perm >= real): `{p:.9f}`")
        lines.append("")
        lines.append(md_table(rowperm.head(8), 8))
    lines.extend(["", "## Decision", "", md_table(decision, 1), "", "## Interpretation", ""])
    lines.extend(
        [
            "- Passing would mean the post-H012 action decoder is approximately a",
            "  failed-direction nullspace or survivor-cone law.",
            "- Failing means H036/H037/H038 failures are not linearly removable;",
            "  the missing HS-JEPA decoder is likely discrete route/private-public",
            "  structure rather than a linear projection around H012.",
        ]
    )
    (OUT / "h039_report.md").write_text("\n".join(lines) + "\n")


def main() -> None:
    h012 = load_sub(H012)
    sample = h012[KEYS].copy()
    h012_prob = h012[TARGETS].to_numpy(dtype=np.float64)
    e247_prob = load_sub(E247, sample)[TARGETS].to_numpy(dtype=np.float64)
    cells = load_cell_state(sample, h012_prob, e247_prob)

    cand = harmonize_candidate_scores()
    pool_summary = (
        cand.groupby("source_experiment")
        .agg(
            candidates=("candidate_id", "size"),
            materialized=("resolved_path", lambda x: int(sum(Path(str(p)).exists() for p in x))),
            world_good_action_bad=("world_good_action_bad", "sum"),
            survivor_hint=("h024_survivor_hint", "sum"),
            mean_h024_margin=("pre_h012_h024_margin_vs_h012_median", "mean"),
            max_h024_support=("pre_h012_h024_support_better_than_h012", "max"),
        )
        .reset_index()
    )
    pool_summary.to_csv(OUT / "h039_source_pool_summary.csv", index=False)

    all_x, all_meta = load_direction_matrix(cand, sample, h012_prob, "badness_weight")
    world_bad = cand[cand["world_good_action_bad"]].copy()
    if len(world_bad) < 12:
        world_bad = cand.sort_values("world_cell_delta_vs_h012").head(max(12, min(80, len(cand)))).copy()
    world_x, world_meta = load_direction_matrix(world_bad, sample, h012_prob, "badness_weight")
    survivor = cand[cand["h024_survivor_hint"]].copy()
    if len(survivor) < 12:
        survivor = cand.sort_values("pre_h012_h024_margin_vs_h012_median").head(max(12, min(80, len(cand)))).copy()
    survivor_x, survivor_meta = load_direction_matrix(survivor, sample, h012_prob, "badness_weight")

    all_basis, all_s, all_diag = svd_basis(all_x, 64)
    world_basis, world_s, world_diag = svd_basis(world_x, 64)
    survivor_basis, survivor_s, survivor_diag = svd_basis(survivor_x, 48)
    all_meta.to_csv(OUT / "h039_all_direction_meta.csv", index=False)
    world_meta.to_csv(OUT / "h039_world_bad_direction_meta.csv", index=False)
    survivor_meta.to_csv(OUT / "h039_survivor_direction_meta.csv", index=False)
    basis_diag = pd.concat(
        [
            all_diag.assign(basis="all_bad"),
            world_diag.assign(basis="world_bad"),
            survivor_diag.assign(basis="survivor"),
        ],
        ignore_index=True,
    )
    basis_diag.to_csv(OUT / "h039_basis_diagnostics.csv", index=False)

    bases = {"all_bad": all_basis, "world_bad": world_basis, "survivor": survivor_basis}
    candidates, proj_diag = generate_candidates(sample, h012_prob, e247_prob, cells, bases)
    scored, h024_features, h024_models, h025_cells = score_candidates(candidates)
    scored.to_csv(OUT / "h039_candidate_scores.csv", index=False)
    h024_features.to_csv(OUT / "h039_h024_features.csv", index=False)
    h024_models.to_csv(OUT / "h039_h024_model_scores.csv", index=False)
    if not h025_cells.empty:
        h025_cells.to_csv(OUT / "h039_h025_top_cells.csv", index=False)
    rowperm = pd.DataFrame()
    if not scored.empty:
        rowperm = run_rowperm(str(scored.iloc[0]["resolved_path"]))
        rowperm.to_csv(OUT / "h039_selected_h025_rowperm_stress.csv", index=False)
    decision = decide(scored, rowperm)
    decision.to_csv(OUT / "h039_decision.csv", index=False)
    if bool(decision.iloc[0].get("promote", False)):
        selected_path = Path(str(decision.iloc[0]["selected_resolved_path"]))
        root_name = selected_path.name.replace(".csv", "_uploadsafe.csv")
        shutil.copyfile(selected_path, ROOT / root_name)
        decision.loc[0, "promoted_root_file"] = root_name
        decision.to_csv(OUT / "h039_decision.csv", index=False)
    write_report(pool_summary, basis_diag, proj_diag, scored, decision, rowperm)

    print(f"H039 candidates: {len(scored)}")
    if not scored.empty:
        print(f"H039 selected: {scored.iloc[0]['candidate_id']}")
        print(f"H039 selected world cell delta: {float(scored.iloc[0]['world_cell_delta_vs_h012']):.9f}")
        print(f"H039 selected H024 margin: {float(scored.iloc[0].get('pre_h012_h024_margin_vs_h012_median', np.nan)):.9f}")
    print(f"H039 decision: {decision.iloc[0]['decision']} - {decision.iloc[0]['reason']}")


if __name__ == "__main__":
    main()
