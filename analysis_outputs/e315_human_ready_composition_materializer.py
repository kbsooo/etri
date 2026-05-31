#!/usr/bin/env python3
"""E315: human-readiness composition materializer.

E313 found a useful split:

    human diary signatures predict readiness distance well,
    but geometry still blocks null-common submission risk.

E314 tested individual scalar lifts and rejected them. E315 tests the
unanswered branch: can multiple human-ready safe seeds compose into a
different action geometry, instead of simply amplifying one seed?

No public LB is used.
"""

from __future__ import annotations

from pathlib import Path
import hashlib
import sys
from typing import Any
import warnings

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
NULL_DIR = OUT / "e315_human_ready_composition_nulls"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e272_public_free_candidate_audit import CURRENT, evaluate_models, score_candidates  # noqa: E402
from e288_lifestyle_bundle_jepa_audit import TARGETS, clip_prob, load_frames, stable_seed  # noqa: E402
from e289_target_specific_lifestyle_slice_audit import safe_id  # noqa: E402
from e297_episode_state_materializer import align_meta_to_current, feature_rows, sigmoid  # noqa: E402
from public_anchor_bottleneck_decomposition import KEYS, load_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

READINESS = OUT / "e313_human_action_signature_readiness_readout.csv"
CANDIDATE_OUT = OUT / "e315_human_ready_composition_candidates.csv"
SELECTED_OUT = OUT / "e315_human_ready_composition_selected.csv"
GOVERNOR_OUT = OUT / "e315_human_ready_composition_governor.csv"
SCORE_OUT = OUT / "e315_human_ready_composition_scores.csv"
NULL_MAP_OUT = OUT / "e315_human_ready_composition_null_map.csv"
REPORT_OUT = OUT / "e315_human_ready_composition_report.md"

MAX_CANDIDATES = 720
MAX_NULL_EVAL = 72
N_NULL_REPS = 5
CAP = 0.35


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def md(frame: pd.DataFrame, n: int = 30, floatfmt: str = ".9f") -> str:
    if frame is None or frame.empty:
        return "_empty_"
    out = frame.head(n).copy()
    out.attrs = {}
    for col in out.select_dtypes(include=[np.floating]).columns:
        out[col] = out[col].map(lambda x: "" if pd.isna(x) else f"{x:{floatfmt}}")
    out = out.fillna("").astype(str)
    header = "| " + " | ".join(out.columns) + " |"
    sep = "| " + " | ".join(["---"] * len(out.columns)) + " |"
    rows = ["| " + " | ".join(row) + " |" for row in out.to_numpy()]
    return "\n".join([header, sep, *rows])


def short_hash(frame: pd.DataFrame) -> str:
    arr = np.asarray(frame[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def current_frame() -> pd.DataFrame:
    return load_sub(OUT / CURRENT).sort_values(KEYS).reset_index(drop=True)


def sorted_sub(path: Path) -> pd.DataFrame:
    return load_sub(path).sort_values(KEYS).reset_index(drop=True)


def candidate_paths() -> dict[str, Path]:
    paths: dict[str, Path] = {}
    for path in sorted(OUT.rglob("submission*.csv"), key=lambda p: (len(str(p)), str(p))):
        paths.setdefault(path.name, path)
    return paths


def load_delta(path: Path, current: pd.DataFrame) -> np.ndarray:
    sub = sorted_sub(path)
    if not sub[KEYS].equals(current[KEYS]):
        raise ValueError(f"key mismatch: {path}")
    return logit(sub[TARGETS].to_numpy(dtype=np.float64)) - logit(current[TARGETS].to_numpy(dtype=np.float64))


def cap_delta(delta: np.ndarray, cap: float = CAP) -> np.ndarray:
    return np.clip(np.asarray(delta, dtype=np.float64), -cap, cap)


def top_rows(delta: np.ndarray, k: int) -> np.ndarray:
    if k <= 0 or k >= len(delta):
        return delta.copy()
    score = np.max(np.abs(delta), axis=1)
    idx = np.argsort(score)[::-1][:k]
    out = np.zeros_like(delta)
    out[idx] = delta[idx]
    return out


def top_cells(delta: np.ndarray, k: int) -> np.ndarray:
    if k <= 0 or k >= delta.size:
        return delta.copy()
    flat = np.abs(delta).ravel()
    idx = np.argsort(flat)[::-1][:k]
    out = np.zeros_like(delta).ravel()
    out[idx] = delta.ravel()[idx]
    return out.reshape(delta.shape)


def normalize_delta(delta: np.ndarray, norm: str) -> np.ndarray:
    values = np.asarray(delta, dtype=np.float64)
    if norm == "max":
        denom = np.max(np.abs(values))
    elif norm == "l1":
        denom = np.sum(np.abs(values))
    else:
        denom = 1.0
    if denom <= 1e-12:
        return np.zeros_like(values)
    return values / denom


def target_balance(delta: np.ndarray) -> np.ndarray:
    values = np.asarray(delta, dtype=np.float64).copy()
    col_l1 = np.sum(np.abs(values), axis=0)
    positive = col_l1[col_l1 > 1e-12]
    if len(positive) == 0:
        return np.zeros_like(values)
    target = float(np.median(positive))
    scale = np.zeros_like(col_l1)
    mask = col_l1 > 1e-12
    scale[mask] = np.minimum(2.5, target / col_l1[mask])
    return values * scale.reshape(1, -1)


def signed_consensus(delta_list: list[np.ndarray], min_votes: int = 2) -> np.ndarray:
    if not delta_list:
        return np.zeros((0, 0))
    stack = np.stack(delta_list, axis=0)
    signs = np.sign(stack) * (np.abs(stack) > 1e-12)
    votes = np.sum(signs, axis=0)
    support = np.sum(np.abs(signs), axis=0)
    base = np.mean(stack, axis=0)
    mask = (support >= min_votes) & (np.abs(votes) >= min_votes)
    return np.where(mask, base, 0.0)


def row_consensus(delta_list: list[np.ndarray], min_support: int = 2) -> np.ndarray:
    if not delta_list:
        return np.zeros((0, 0))
    stack = np.stack(delta_list, axis=0)
    row_support = np.sum(np.any(np.abs(stack) > 1e-12, axis=2), axis=0)
    base = np.mean(stack, axis=0)
    return np.where(row_support.reshape(-1, 1) >= min_support, base, 0.0)


def flat_cosine(a: np.ndarray, b: np.ndarray) -> float:
    av = np.ravel(a)
    bv = np.ravel(b)
    denom = float(np.linalg.norm(av) * np.linalg.norm(bv))
    if denom <= 1e-12:
        return 0.0
    return float(np.dot(av, bv) / denom)


def write_submission(current: pd.DataFrame, delta: np.ndarray, candidate_id: str) -> Path:
    out = current.copy()
    logits = logit(out[TARGETS].to_numpy(dtype=np.float64)) + cap_delta(delta)
    out[TARGETS] = clip_prob(sigmoid(logits))
    path = OUT / f"submission_e315_humancomp_{safe_id(candidate_id)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def seed_table(current: pd.DataFrame) -> pd.DataFrame:
    paths = candidate_paths()
    read = pd.read_csv(READINESS)
    read["source_path_exists"] = read["basename"].map(lambda b: str(b) in paths)
    safe = read[
        read["source_path_exists"].astype(bool)
        & read["null_rare"].astype(bool)
        & ~read["null_common"].astype(bool)
        & ~read["selector_visible"].astype(bool)
        & read["failure_mode"].astype(str).str.contains("safe_but_too_small", na=False)
    ].copy()
    safe["actual_p90_neg"] = safe["actual_p90"].fillna(1.0).lt(0)
    safe = safe.sort_values(
        ["pred_ready__human_signature", "actual_p90_neg", "actual_p90", "readiness_distance"],
        ascending=[True, False, True, True],
    ).reset_index(drop=True)
    deltas: list[np.ndarray] = []
    rows: list[dict[str, Any]] = []
    for rank, (_, row) in enumerate(safe.head(180).iterrows(), start=1):
        path = paths[str(row["basename"])]
        delta = load_delta(path, current)
        row_abs = np.abs(delta).sum(axis=1)
        rows.append(
            {
                **row.to_dict(),
                "seed_rank": rank,
                "seed_abs_l1": float(np.sum(np.abs(delta))),
                "seed_max_abs": float(np.max(np.abs(delta))),
                "seed_changed_rows": int(np.sum(row_abs > 1e-12)),
                "seed_changed_cells": int(np.sum(np.abs(delta) > 1e-12)),
            }
        )
        deltas.append(delta)
    out = pd.DataFrame(rows)
    out.attrs["deltas"] = deltas
    return out


def add_candidate(
    rows: list[dict[str, Any]],
    delta_map: dict[str, np.ndarray],
    current: pd.DataFrame,
    candidate_id: str,
    delta: np.ndarray,
    recipe: str,
    source_note: str,
    seed_names: list[str],
    weight: float,
) -> None:
    if len(rows) >= MAX_CANDIDATES:
        return
    delta = cap_delta(delta)
    if np.max(np.abs(delta)) < 1.0e-12:
        return
    path = write_submission(current, delta, candidate_id)
    basename = path.name
    if basename in delta_map:
        return
    delta_map[basename] = delta
    nonzero_rows = int(np.any(np.abs(delta) > 1.0e-12, axis=1).sum())
    nonzero_cells = int(np.sum(np.abs(delta) > 1.0e-12))
    abs_by_target = np.abs(delta).sum(axis=0)
    rows.append(
        {
            "basename": basename,
            "source_path": rel(path),
            "recipe": recipe,
            "source_note": source_note,
            "seed_count": len(seed_names),
            "seed_basenames": "|".join(seed_names[:12]),
            "weight": weight,
            "nonzero_rows": nonzero_rows,
            "nonzero_cells": nonzero_cells,
            "mean_abs_delta": float(np.mean(np.abs(delta))),
            "max_abs_delta": float(np.max(np.abs(delta))),
            "l1_delta": float(np.sum(np.abs(delta))),
            "signed_delta_sum": float(np.sum(delta)),
            "q_abs_share": float(abs_by_target[:3].sum() / max(abs_by_target.sum(), 1e-12)),
            "s_abs_share": float(abs_by_target[3:].sum() / max(abs_by_target.sum(), 1e-12)),
            **{f"abs_{t}": float(abs_by_target[i]) for i, t in enumerate(TARGETS)},
        }
    )


def generate_candidates(current: pd.DataFrame, seeds: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    deltas = list(seeds.attrs["deltas"])
    rows: list[dict[str, Any]] = []
    delta_map: dict[str, np.ndarray] = {}
    if seeds.empty:
        return pd.DataFrame(), delta_map

    recipe_limits = {
        "family_consensus": 180,
        "target_consensus": 150,
        "ranked_negative_stack": 120,
        "orthogonal_story_stack": 150,
        "target_balanced_story_stack": 120,
    }
    recipe_counts: dict[str, int] = {k: 0 for k in recipe_limits}

    def addc(candidate_id: str, delta: np.ndarray, recipe: str, source_note: str, seed_names: list[str], weight: float) -> None:
        if recipe_counts.get(recipe, 0) >= recipe_limits.get(recipe, MAX_CANDIDATES):
            return
        before = len(rows)
        add_candidate(rows, delta_map, current, candidate_id, delta, recipe, source_note, seed_names, weight)
        if len(rows) > before:
            recipe_counts[recipe] = recipe_counts.get(recipe, 0) + 1

    seed_meta = seeds.copy()
    dom_targets: list[str] = []
    for i in seed_meta.index:
        abs_by_target = np.abs(deltas[i]).sum(axis=0)
        dom_targets.append(TARGETS[int(np.argmax(abs_by_target))] if abs_by_target.sum() > 1e-12 else "none")
    seed_meta["dominant_target"] = dom_targets
    seed_meta["neg_edge"] = seed_meta["actual_p90"].fillna(1.0).lt(0)

    # 1. Group consensus: repeated human-ready patterns inside the same human
    # story/source should survive better than one amplified seed if the story is real.
    for group_col in ["family", "experiment", "target_norm"]:
        for group, part in seed_meta.head(150).groupby(group_col, dropna=False):
            part = part.sort_values(["pred_ready__human_signature", "actual_p90"]).head(10)
            if len(part) < 2:
                continue
            idxs = part.index.to_list()
            seed_names = part["basename"].astype(str).tolist()
            dlist = [deltas[i] for i in idxs]
            bases = {
                "l1mean": np.sum([normalize_delta(d, "l1") for d in dlist], axis=0) / np.sqrt(len(dlist)),
                "maxmean": np.mean([normalize_delta(d, "max") for d in dlist], axis=0),
                "vote2": signed_consensus(dlist, min_votes=2),
                "row2": row_consensus(dlist, min_support=2),
                "tbal": target_balance(np.mean([normalize_delta(d, "max") for d in dlist], axis=0)),
            }
            recipe = "family_consensus" if group_col in {"family", "experiment"} else "target_consensus"
            for base_name, base_delta in bases.items():
                if np.max(np.abs(base_delta)) <= 1e-12:
                    continue
                for keep_cells in [24, 48, 96, 160, 0]:
                    shaped = top_cells(base_delta, keep_cells) if keep_cells else base_delta
                    for weight in [0.75, 1.5, 3.0, 5.0, 8.0, 12.0]:
                        addc(
                            f"{group_col}_{safe_id(str(group))}_{base_name}_c{keep_cells or 'all'}_w{weight:.2f}",
                            shaped * weight,
                            recipe,
                            f"quota-reserved consensus over human-ready seeds grouped by {group_col}",
                            seed_names,
                            weight,
                        )
                        if len(rows) >= MAX_CANDIDATES:
                            return pd.DataFrame(rows), delta_map

    # 2. Negative-edge stacks: combine only seeds that already point in the
    # current-selector-helpful direction, but use normalized shapes so no single
    # tiny seed is merely amplified.
    neg = seed_meta[seed_meta["neg_edge"].astype(bool)].head(120)
    for n in [2, 3, 4, 6, 8, 12, 16, 24]:
        part = neg.head(n)
        if len(part) < 2:
            continue
        idxs = part.index.to_list()
        seed_names = part["basename"].astype(str).tolist()
        base_variants = {
            "l1avg": np.sum([normalize_delta(deltas[i], "l1") for i in idxs], axis=0) / np.sqrt(len(idxs)),
            "maxavg": np.mean([normalize_delta(deltas[i], "max") for i in idxs], axis=0),
            "vote2": signed_consensus([deltas[i] for i in idxs], min_votes=2),
            "tbal": target_balance(np.mean([normalize_delta(deltas[i], "max") for i in idxs], axis=0)),
        }
        for base_name, base_delta in base_variants.items():
            if np.max(np.abs(base_delta)) <= 1e-12:
                continue
            for keep_cells in [24, 48, 96, 160, 0]:
                shaped = top_cells(base_delta, keep_cells) if keep_cells else base_delta
                for weight in [1.0, 2.0, 4.0, 7.0, 10.0]:
                    addc(
                        f"neg_top{n}_{base_name}_c{keep_cells or 'all'}_w{weight:.2f}",
                        shaped * weight,
                        "ranked_negative_stack",
                        "stack negative-edge human-ready seeds with normalized contribution",
                        seed_names,
                        weight,
                    )
                    if len(rows) >= MAX_CANDIDATES:
                        return pd.DataFrame(rows), delta_map

    # 3. Orthogonal story stacks: force multiple different human stories/source
    # families into the same candidate while avoiding high cosine overlap.
    pool = seed_meta.head(140).copy()
    for start in range(min(24, len(pool))):
        chosen = [int(pool.index[start])]
        used_families = {str(pool.iloc[start]["family"])}
        for _, cand in pool.iterrows():
            idx = int(cand.name)
            if idx in chosen:
                continue
            fam = str(cand["family"])
            max_cos = max(abs(flat_cosine(deltas[idx], deltas[j])) for j in chosen)
            if fam in used_families and len(used_families) < 4:
                continue
            if max_cos <= 0.20 or len(chosen) < 3:
                chosen.append(idx)
                used_families.add(fam)
            if len(chosen) >= 10:
                break
        if len(chosen) < 3:
            continue
        for n in [3, 5, 8, len(chosen)]:
            idxs = chosen[:n]
            if len(idxs) < 3:
                continue
            seed_names = seed_meta.loc[idxs, "basename"].astype(str).tolist()
            base_variants = {
                "maxavg": np.mean([normalize_delta(deltas[i], "max") for i in idxs], axis=0),
                "l1sum": np.sum([normalize_delta(deltas[i], "l1") for i in idxs], axis=0) / np.sqrt(len(idxs)),
                "row2": row_consensus([deltas[i] for i in idxs], min_support=2),
                "tbal": target_balance(np.mean([normalize_delta(deltas[i], "max") for i in idxs], axis=0)),
            }
            for base_name, base_delta in base_variants.items():
                if np.max(np.abs(base_delta)) <= 1e-12:
                    continue
                for keep_cells in [32, 64, 128, 0]:
                    shaped = top_cells(base_delta, keep_cells) if keep_cells else base_delta
                    for weight in [1.5, 3.0, 5.0, 8.0]:
                        addc(
                            f"orth_s{start}_n{n}_{base_name}_c{keep_cells or 'all'}_w{weight:.2f}",
                            shaped * weight,
                            "orthogonal_story_stack",
                            "compose different human-ready stories with low delta cosine overlap",
                            seed_names,
                            weight,
                        )
                        if len(rows) >= MAX_CANDIDATES:
                            return pd.DataFrame(rows), delta_map

    # 4. Target-balanced story stacks: one best seed per dominant target and
    # story family. This explicitly tests whether hidden lifestyle state needs a
    # multi-target diary rather than a Q3-only or S-only action.
    for fam, fam_part in seed_meta.head(160).groupby("family", dropna=False):
        picks = (
            fam_part.sort_values(["pred_ready__human_signature", "actual_p90"])
            .groupby("dominant_target", as_index=False)
            .head(1)
        )
        if len(picks) < 2:
            continue
        for target_set, part in [
            ("all", picks),
            ("q", picks[picks["dominant_target"].isin(TARGETS[:3])]),
            ("s", picks[picks["dominant_target"].isin(TARGETS[3:])]),
            ("qs", picks.groupby(picks["dominant_target"].isin(TARGETS[:3]), as_index=False).head(2)),
        ]:
            if len(part) < 2:
                continue
            idxs = part.index.to_list()
            seed_names = part["basename"].astype(str).tolist()
            base = target_balance(np.sum([normalize_delta(deltas[i], "max") for i in idxs], axis=0) / len(idxs))
            for keep_cells in [24, 48, 96, 0]:
                shaped = top_cells(base, keep_cells) if keep_cells else base
                for weight in [1.5, 3.0, 5.0, 8.0, 12.0]:
                    addc(
                        f"tbstory_{safe_id(str(fam))}_{target_set}_c{keep_cells or 'all'}_w{weight:.2f}",
                        shaped * weight,
                        "target_balanced_story_stack",
                        "balance one human-ready seed per target within a story family",
                        seed_names,
                        weight,
                    )
                    if len(rows) >= MAX_CANDIDATES:
                        return pd.DataFrame(rows), delta_map

    return pd.DataFrame(rows), delta_map


def score_prefilter(candidate_meta: pd.DataFrame, current: pd.DataFrame) -> pd.DataFrame:
    if candidate_meta.empty:
        return candidate_meta
    candidate_meta = candidate_meta.drop_duplicates("basename").reset_index(drop=True)
    sample = current[KEYS].copy()
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    paths = [OUT / b for b in candidate_meta["basename"]]
    features = feature_rows([OUT / CURRENT, *paths], sample, refs, ref_vecs)
    scores = score_candidates(known, features, model_df)
    scores = scores.drop_duplicates("basename")
    score_cols = [
        "basename",
        "promotion_decision",
        "strict_promote_gate",
        "info_sensor_gate",
        "pred_delta_vs_current_mean",
        "pred_delta_vs_current_p10",
        "pred_delta_vs_current_p90",
        "pred_beats_current_rate",
        "incremental_bad_axis_vs_current",
    ]
    merged = candidate_meta.merge(scores[score_cols], on="basename", how="left")
    return merged.sort_values(
        ["strict_promote_gate", "info_sensor_gate", "pred_delta_vs_current_p90", "pred_delta_vs_current_mean"],
        ascending=[False, False, True, True],
    ).reset_index(drop=True)


def select_for_null(prefilter: pd.DataFrame) -> pd.DataFrame:
    if prefilter.empty:
        return prefilter
    strict = prefilter[prefilter["strict_promote_gate"].astype(bool)].copy()
    info = prefilter[
        (~prefilter["strict_promote_gate"].astype(bool))
        & prefilter["info_sensor_gate"].astype(bool)
        & prefilter["pred_delta_vs_current_p90"].lt(-2.0e-5)
    ].copy()
    recipe_best = (
        prefilter.sort_values(["pred_delta_vs_current_p90", "pred_delta_vs_current_mean"])
        .groupby("recipe", as_index=False)
        .head(6)
    )
    selected = pd.concat(
        [
            strict.sort_values(["pred_delta_vs_current_p90", "pred_delta_vs_current_mean"]).head(MAX_NULL_EVAL // 2),
            info.sort_values(["pred_delta_vs_current_p90", "pred_delta_vs_current_mean"]).head(MAX_NULL_EVAL // 4),
            recipe_best,
        ],
        ignore_index=True,
    )
    if selected.empty:
        selected = prefilter.sort_values(["pred_delta_vs_current_p90", "pred_delta_vs_current_mean"]).head(MAX_NULL_EVAL)
    return selected.drop_duplicates("basename").head(MAX_NULL_EVAL).reset_index(drop=True)


def shuffle_rows(delta: np.ndarray, mode: str, meta: pd.DataFrame, seed_parts: tuple[Any, ...]) -> np.ndarray:
    rng = np.random.default_rng(stable_seed("e315shuffle", *map(str, seed_parts)))
    values = np.asarray(delta, dtype=np.float64)
    out = values.copy()
    if mode == "row":
        return values[rng.permutation(len(values))]
    if mode in {"subject", "dateblock"}:
        group_col = "subject_id" if mode == "subject" else "dateblock_group"
        for _, idx in meta.groupby(group_col).indices.items():
            idx_arr = np.asarray(idx, dtype=int)
            if len(idx_arr) > 1:
                out[idx_arr] = values[idx_arr][rng.permutation(len(idx_arr))]
        return out
    raise ValueError(mode)


def null_delta(delta: np.ndarray, mode: str, rep: int, meta: pd.DataFrame, basename: str) -> np.ndarray:
    if mode in {"row", "subject", "dateblock"}:
        return shuffle_rows(delta, mode, meta, (basename, mode, rep))
    if mode == "sign_flip":
        return -delta
    if mode == "target_perm":
        rng = np.random.default_rng(stable_seed("e315targetperm", basename, rep))
        perm = rng.permutation(len(TARGETS))
        return delta[:, perm]
    if mode == "q_s_swap":
        out = np.zeros_like(delta)
        out[:, :3] = delta[:, [3, 4, 5]]
        out[:, 3:6] = delta[:, :3]
        out[:, 6] = delta[:, 6]
        return out
    raise ValueError(mode)


def write_null(current: pd.DataFrame, delta: np.ndarray, basename: str, mode: str, rep: int, meta: pd.DataFrame) -> Path:
    out = current.copy()
    nd = cap_delta(null_delta(delta, mode, rep, meta, basename))
    logits = logit(out[TARGETS].to_numpy(dtype=np.float64)) + nd
    out[TARGETS] = clip_prob(sigmoid(logits))
    NULL_DIR.mkdir(exist_ok=True)
    path = NULL_DIR / f"submission_e315null_{basename[:64]}_{mode}_r{rep}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def run_governor(selected: pd.DataFrame, delta_map: dict[str, np.ndarray], current: pd.DataFrame, meta: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if selected.empty:
        return selected, pd.DataFrame(), pd.DataFrame()
    null_rows: list[dict[str, Any]] = []
    null_paths: list[Path] = []
    modes = ["row", "subject", "dateblock", "target_perm", "sign_flip", "q_s_swap"]
    for _, row in selected.iterrows():
        basename = str(row["basename"])
        delta = delta_map[basename]
        for mode in modes:
            reps = N_NULL_REPS if mode in {"row", "subject", "dateblock", "target_perm"} else 1
            for rep in range(reps):
                path = write_null(current, delta, basename, mode, rep, meta)
                null_paths.append(path)
                null_rows.append(
                    {
                        "source_basename": basename,
                        "null_basename": path.name,
                        "null_path": rel(path),
                        "mode": mode,
                        "rep": rep,
                    }
                )
    null_map = pd.DataFrame(null_rows)
    sample = current[KEYS].copy()
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    paths = [OUT / b for b in selected["basename"]]
    features = feature_rows([OUT / CURRENT, *paths, *null_paths], sample, refs, ref_vecs)
    scores = score_candidates(known, features, model_df)
    scores.to_csv(SCORE_OUT, index=False)
    null_map.to_csv(NULL_MAP_OUT, index=False)
    candidate_score = scores[scores["basename"].isin(selected["basename"])].copy()
    null_scores = scores[scores["basename"].isin(null_map["null_basename"])].copy()
    rows: list[dict[str, Any]] = []
    for _, cand in selected.iterrows():
        basename = str(cand["basename"])
        actual = candidate_score[candidate_score["basename"].eq(basename)]
        if actual.empty:
            continue
        a = actual.iloc[0]
        these_null = null_scores.merge(
            null_map[null_map["source_basename"].eq(basename)][["null_basename", "mode"]],
            left_on="basename",
            right_on="null_basename",
            how="inner",
        )
        p90_vals = these_null["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64)
        mean_vals = these_null["pred_delta_vs_current_mean"].to_numpy(dtype=np.float64)
        actual_p90 = float(a["pred_delta_vs_current_p90"])
        actual_mean = float(a["pred_delta_vs_current_mean"])
        old_strict = bool(a.get("strict_promote_gate", False))
        null_strict_rate = float(these_null["strict_promote_gate"].astype(bool).mean()) if len(these_null) else 1.0
        p90_dominance = float(np.mean(actual_p90 < p90_vals)) if len(p90_vals) else 0.0
        mean_dominance = float(np.mean(actual_mean < mean_vals)) if len(mean_vals) else 0.0
        mode_doms = {}
        for mode, part in these_null.groupby("mode"):
            vals = part["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64)
            mode_doms[f"{mode}_p90_dominance"] = float(np.mean(actual_p90 < vals))
        worst_mode = float(min(mode_doms.values())) if mode_doms else 0.0
        ready = bool(
            old_strict
            and actual_p90 <= -2.0e-5
            and null_strict_rate <= 0.10
            and p90_dominance >= 0.80
            and mean_dominance >= 0.70
            and worst_mode >= 0.55
        )
        rows.append(
            {
                **cand.to_dict(),
                "old_promotion_decision": a.get("promotion_decision", ""),
                "old_strict_promote": old_strict,
                "actual_mean": actual_mean,
                "actual_p10": float(a["pred_delta_vs_current_p10"]),
                "actual_p90": actual_p90,
                "actual_beats_current_rate": float(a["pred_beats_current_rate"]),
                "incremental_bad_axis_vs_current": float(a["incremental_bad_axis_vs_current"]),
                "null_count": int(len(these_null)),
                "null_strict_rate": null_strict_rate,
                "p90_dominance": p90_dominance,
                "mean_dominance": mean_dominance,
                "worst_mode_p90_dominance": worst_mode,
                **mode_doms,
                "public_free_submission_ready": ready,
                "final_decision": "public_free_submission_ready" if ready else ("blocked_by_human_ready_composition_nulls" if old_strict else str(a.get("promotion_decision", "hold"))),
            }
        )
    governor = pd.DataFrame(rows)
    if not governor.empty:
        governor = governor.sort_values(
            ["public_free_submission_ready", "old_strict_promote", "null_strict_rate", "actual_p90", "mean_dominance"],
            ascending=[False, False, True, True, False],
        ).reset_index(drop=True)
    return selected, null_map, governor


def write_report(seeds: pd.DataFrame, prefilter: pd.DataFrame, selected: pd.DataFrame, governor: pd.DataFrame) -> None:
    ready = governor[governor["public_free_submission_ready"].astype(bool)] if not governor.empty else pd.DataFrame()
    recipe_pref = (
        prefilter.groupby("recipe", dropna=False)
        .agg(
            generated=("basename", "count"),
            old_strict=("strict_promote_gate", "sum"),
            info=("info_sensor_gate", "sum"),
            best_p90=("pred_delta_vs_current_p90", "min"),
            best_mean=("pred_delta_vs_current_mean", "min"),
            median_l1=("l1_delta", "median"),
        )
        .reset_index()
        .sort_values(["old_strict", "best_p90"], ascending=[False, True])
        if not prefilter.empty
        else pd.DataFrame()
    )
    recipe_gov = (
        governor.groupby("recipe", dropna=False)
        .agg(
            evaluated=("basename", "count"),
            old_strict=("old_strict_promote", "sum"),
            ready=("public_free_submission_ready", "sum"),
            best_p90=("actual_p90", "min"),
            best_null_strict=("null_strict_rate", "min"),
            best_worst_mode=("worst_mode_p90_dominance", "max"),
        )
        .reset_index()
        .sort_values(["ready", "old_strict", "best_null_strict", "best_p90"], ascending=[False, False, True, True])
        if not governor.empty
        else pd.DataFrame()
    )
    show_cols = [
        "basename",
        "recipe",
        "seed_count",
        "nonzero_rows",
        "nonzero_cells",
        "l1_delta",
        "actual_mean",
        "actual_p90",
        "null_strict_rate",
        "p90_dominance",
        "mean_dominance",
        "worst_mode_p90_dominance",
        "final_decision",
    ]
    seed_cols = [
        "experiment",
        "basename",
        "family",
        "target_norm",
        "actual_p90",
        "null_strict_rate",
        "readiness_distance",
        "pred_ready__human_signature",
        "pred_ready__geometry_only",
        "seed_abs_l1",
        "seed_changed_rows",
        "failure_mode",
    ]
    lines = [
        "# E315 Human-Readiness Composition Materializer",
        "",
        "Public LB는 사용하지 않았다. E314가 남긴 공백인 non-single human-ready composition을 검증했다. 단일 seed lift는 금지하고, family/target consensus, negative-edge stack, orthogonal story stack, target-balanced story stack만 생성했다.",
        "",
        "Question: 여러 human/social seed가 같은 숨은 생활 상태를 바라본다면, 조합된 action geometry는 단일 seed amplitude와 달리 matched null을 이길 수 있는가?",
        "",
        "## Seed Pool",
        "",
        f"- safe human-ready seeds loaded: `{len(seeds)}`",
        "",
        md(seeds[[c for c in seed_cols if c in seeds.columns]], n=30),
        "",
        "## Prefilter",
        "",
        f"- generated candidates: `{len(prefilter)}`",
        f"- old strict candidates: `{int(prefilter['strict_promote_gate'].sum()) if not prefilter.empty else 0}`",
        f"- info candidates: `{int(prefilter['info_sensor_gate'].sum()) if not prefilter.empty else 0}`",
        f"- null-evaluated candidates: `{len(selected)}`",
        "",
        md(recipe_pref, n=20),
        "",
        "## Matched Null Governor",
        "",
        f"- public-free ready candidates: `{len(ready)}`",
        "",
        md(recipe_gov, n=20),
        "",
        md(governor[[c for c in show_cols if c in governor.columns]] if not governor.empty else governor, n=60),
        "",
        "## Decision",
        "",
    ]
    if len(ready):
        top = ready.iloc[0]
        lines.append(f"`{top['basename']}` is public-free ready. Submit only as a scarce-slot test of the H315 human-readiness composition world.")
    else:
        lines.extend(
            [
                "- No E315 human-readiness composition is public-free ready.",
                "- If generated compositions become old-strict but null-common, human-readiness composition still falls into the current action-geometry cliff.",
                "- If null-rare compositions remain below selector resolution, the next action needs a different target-level materializer rather than broader stacking.",
            ]
        )
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            f"- `{CANDIDATE_OUT.relative_to(ROOT)}`",
            f"- `{SELECTED_OUT.relative_to(ROOT)}`",
            f"- `{GOVERNOR_OUT.relative_to(ROOT)}`",
            f"- `{SCORE_OUT.relative_to(ROOT)}`",
            f"- `{NULL_MAP_OUT.relative_to(ROOT)}`",
            f"- `{REPORT_OUT.relative_to(ROOT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    current = current_frame()
    base, _, _, _ = load_frames()
    test_df = base.loc[base["split"].eq("test")].reset_index(drop=True)
    meta = align_meta_to_current(test_df, current)
    seeds = seed_table(current)
    candidate_meta, delta_map = generate_candidates(current, seeds)
    prefilter = score_prefilter(candidate_meta, current) if not candidate_meta.empty else pd.DataFrame()
    selected = select_for_null(prefilter) if not prefilter.empty else pd.DataFrame()
    selected, nulls, governor = run_governor(selected, delta_map, current, meta) if not selected.empty else (selected, pd.DataFrame(), pd.DataFrame())
    prefilter.to_csv(CANDIDATE_OUT, index=False)
    selected.to_csv(SELECTED_OUT, index=False)
    governor.to_csv(GOVERNOR_OUT, index=False)
    if not nulls.empty:
        nulls.to_csv(NULL_MAP_OUT, index=False)
    write_report(seeds, prefilter, selected, governor)
    print(f"seeds={len(seeds)}")
    print(f"generated_candidates={len(prefilter)}")
    print(f"old_strict={int(prefilter['strict_promote_gate'].sum()) if not prefilter.empty else 0}")
    print(f"null_evaluated={len(selected)}")
    print(f"public_ready={int(governor['public_free_submission_ready'].sum()) if not governor.empty else 0}")
    if not governor.empty:
        print(f"best_actual_p90={governor['actual_p90'].min():.9f}")
        print(f"best_null_strict={governor['null_strict_rate'].min():.6f}")
    print(f"report={rel(REPORT_OUT)}")


if __name__ == "__main__":
    main()
