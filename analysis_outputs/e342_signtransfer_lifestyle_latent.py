#!/usr/bin/env python3
"""E342: sign-transfer hidden lifestyle-state latent coalition.

E340 found a Q1/Q3 lifestyle microstate coalition that is null-healthy but
below selector visibility.  E341 found an independent Q2 sparse residual tail
that also remains below visibility.  This experiment tests whether those two
weak signals are two projections of the same hidden lifestyle state.

JEPA translation:
    context = Q1/Q3 human-social microstate movement plus Q2 residual tail
    target  = a shared hidden lifestyle state, not raw feature reconstruction
    action  = sign-transfer/gated coalition only if the state is public-free
              selector-visible and movement-null resistant

No public LB is used.  E247 is the current anchor; E323/E216 are negative
movement axes used as veto geometry.
"""

from __future__ import annotations

from pathlib import Path
import hashlib
import sys
from typing import Any
import warnings

import numpy as np
import pandas as pd
from scipy.special import expit


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
NULL_DIR = OUT / "e342_signtransfer_nulls"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e272_public_free_candidate_audit import CURRENT, build_features, evaluate_models, score_candidates  # noqa: E402
from e328_ownlatent_lifestyle_state_experiment import load_sub_frame, md_table, safe_id  # noqa: E402
from e337_residual_lifestyle_cluster_state import (  # noqa: E402
    bad_axes,
    cell_bad_veto,
    center_by_target,
    cos,
    target_abs,
)
from public_anchor_bottleneck_decomposition import KEYS, TARGETS, load_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

RNG_SEED = 20260531 + 342
EPS = 1.0e-12
CAP = 0.18
MAX_Q2_SOURCES = 4
MAX_MICRO_SOURCES = 8
MAX_NULL_CANDIDATES = 32
NULL_REPS = 4

Q2_SOURCE_OUT = OUT / "e342_signtransfer_q2_sources.csv"
MICRO_SOURCE_OUT = OUT / "e342_signtransfer_micro_sources.csv"
CANDIDATE_OUT = OUT / "e342_signtransfer_candidates.csv"
SCORE_OUT = OUT / "e342_signtransfer_scores.csv"
ANATOMY_OUT = OUT / "e342_signtransfer_anatomy.csv"
MOVE_NULL_OUT = OUT / "e342_signtransfer_movement_nulls.csv"
REPORT_OUT = OUT / "e342_signtransfer_report.md"


def stable_seed(*parts: object) -> int:
    text = "|".join(map(str, parts))
    return RNG_SEED + int(hashlib.sha1(text.encode("utf-8")).hexdigest()[:8], 16) % 100000


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def locate(path_or_name: object) -> Path | None:
    raw = Path(str(path_or_name))
    candidates: list[Path] = []
    if raw.is_absolute():
        candidates.append(raw)
    else:
        candidates.extend([ROOT / raw, OUT / raw.name, OUT / str(path_or_name)])
    for path in candidates:
        if path.exists():
            return path
    return None


def short_hash(frame: pd.DataFrame) -> str:
    arr = np.asarray(frame[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def load_current() -> pd.DataFrame:
    return load_sub(OUT / CURRENT).sort_values(KEYS).reset_index(drop=True)


def load_delta(path: Path, base: pd.DataFrame, base_logit: np.ndarray) -> np.ndarray:
    cand = load_sub_frame(path, base[KEYS]).sort_values(KEYS).reset_index(drop=True)
    return logit(cand[TARGETS].to_numpy(dtype=np.float64)) - base_logit


def write_candidate(base: pd.DataFrame, base_logit: np.ndarray, delta: np.ndarray, candidate_id: str) -> Path:
    out = base.copy()
    out[TARGETS] = clip_prob(expit(np.clip(base_logit + np.clip(delta, -CAP, CAP), -40.0, 40.0)))
    path = OUT / f"submission_e342_signtransfer_{safe_id(candidate_id, 112)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def entropy(weights: np.ndarray) -> float:
    x = np.abs(np.asarray(weights, dtype=np.float64))
    total = float(x.sum())
    if total <= EPS:
        return 0.0
    p = x / total
    nz = p[p > 0.0]
    return float(-(nz * np.log(nz)).sum() / np.log(len(p))) if len(p) > 1 else 0.0


def source_table(prefix: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    scores = pd.read_csv(OUT / f"{prefix}_scores.csv")
    candidates = pd.read_csv(OUT / f"{prefix}_candidates.csv")
    movement_path = OUT / f"{prefix}_movement_nulls.csv"
    movement = pd.read_csv(movement_path) if movement_path.exists() else pd.DataFrame()
    merged = scores[~scores["basename"].eq(CURRENT)].merge(
        candidates,
        on="basename",
        how="left",
        suffixes=("_score", "_meta"),
    )
    if "file_meta" in merged:
        merged["file"] = merged["file_meta"]
    elif "file_score" in merged:
        merged["file"] = merged["file_score"]
    elif "file" not in merged:
        merged["file"] = merged["basename"].map(lambda x: str(OUT / str(x)))
    if len(movement):
        merged = merged.merge(movement, on="basename", how="left", suffixes=("", "_move"))
    return scores, candidates, merged


def select_q2_sources() -> pd.DataFrame:
    _, _, merged = source_table("e341_sparse_residual_support")
    for col, default in [
        ("actual_p90_dominance", 0.50),
        ("actual_mean_dominance", 0.50),
        ("null_strict_promote_rate", 1.0),
    ]:
        if col not in merged:
            merged[col] = default
        merged[col] = pd.to_numeric(merged[col], errors="coerce").fillna(default)
    pool = merged[
        merged["target"].eq("Q2")
        & (merged["pred_delta_vs_current_mean"] < 0.0)
        & (merged["pred_beats_current_rate"] >= 0.85)
        & (merged["incremental_bad_axis_vs_current"].abs() <= 0.018)
        & (merged["pred_delta_vs_current_p90"] < 0.00001)
        & merged["file"].notna()
    ].copy()
    pool["movement_health"] = (
        0.45 * pool["pred_beats_current_rate"]
        + 0.30 * pool["actual_p90_dominance"]
        + 0.25 * (1.0 - pool["null_strict_promote_rate"].clip(0.0, 1.0))
    )
    pool["visibility_margin"] = -pool["pred_delta_vs_current_p90"]
    pool = pool.sort_values(
        ["visibility_margin", "movement_health", "pred_delta_vs_current_mean"],
        ascending=[False, False, True],
    ).head(MAX_Q2_SOURCES)
    pool.to_csv(Q2_SOURCE_OUT, index=False)
    return pool.reset_index(drop=True)


def select_micro_sources() -> pd.DataFrame:
    _, _, merged = source_table("e340_microstate_coalition")
    for col, default in [
        ("actual_p90_dominance", 0.50),
        ("actual_mean_dominance", 0.50),
        ("null_strict_promote_rate", 1.0),
        ("source_p90_dom_min", 0.50),
        ("source_null_rate_max", 1.0),
    ]:
        if col not in merged:
            merged[col] = default
        merged[col] = pd.to_numeric(merged[col], errors="coerce").fillna(default)
    pool = merged[
        (merged["pred_delta_vs_current_mean"] < 0.0)
        & (merged["pred_delta_vs_current_p90"] < 0.0)
        & (merged["pred_beats_current_rate"] >= 0.90)
        & (merged["incremental_bad_axis_vs_current"].abs() <= 0.015)
        & (merged["source_null_rate_max"] <= 0.05)
        & merged["file"].notna()
    ].copy()
    pool["movement_health"] = (
        0.35 * pool["pred_beats_current_rate"]
        + 0.25 * pool["source_p90_dom_min"]
        + 0.25 * pool["actual_p90_dominance"]
        + 0.15 * (1.0 - pool["null_strict_promote_rate"].clip(0.0, 1.0))
    )
    pool["visibility_margin"] = -pool["pred_delta_vs_current_p90"]
    pool = pool.sort_values(
        ["visibility_margin", "movement_health", "pred_delta_vs_current_mean"],
        ascending=[False, False, True],
    ).head(MAX_MICRO_SOURCES)
    pool.to_csv(MICRO_SOURCE_OUT, index=False)
    return pool.reset_index(drop=True)


def row_gate_from_q2(delta_q2: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    row_abs = np.sum(np.abs(delta_q2), axis=1)
    active = (row_abs > EPS).astype(float)
    scale = float(np.quantile(row_abs[row_abs > EPS], 0.85)) if np.any(row_abs > EPS) else 1.0
    if not np.isfinite(scale) or scale <= EPS:
        scale = 1.0
    soft = np.clip(row_abs / scale, 0.0, 1.0)
    return active.reshape(-1, 1), soft.reshape(-1, 1)


def transform_variants(
    q2_delta: np.ndarray,
    micro_delta: np.ndarray,
    w_q2: float,
    w_micro: float,
    e323_bad: np.ndarray,
    e216_bad: np.ndarray,
) -> dict[str, np.ndarray]:
    q = float(w_q2) * np.asarray(q2_delta, dtype=np.float64)
    m = float(w_micro) * np.asarray(micro_delta, dtype=np.float64)
    hard_gate, soft_gate = row_gate_from_q2(q2_delta)
    variants: dict[str, np.ndarray] = {
        "sum_bad_veto": cell_bad_veto(q + m, e323_bad, e216_bad, strength=0.35),
        "sum_veto_centered": center_by_target(cell_bad_veto(q + m, e323_bad, e216_bad, strength=0.35)),
        "q2tail_micro_soft": q + soft_gate * m,
        "q2tail_joint_soft_veto": cell_bad_veto(soft_gate * (q + m), e323_bad, e216_bad, strength=0.35),
        "q2tail_joint_centered": center_by_target(cell_bad_veto(hard_gate * (q + m), e323_bad, e216_bad, strength=0.35)),
    }
    return {name: val for name, val in variants.items() if float(np.sum(np.abs(val))) > EPS}


def materialize_candidates() -> tuple[pd.DataFrame, list[Path], pd.DataFrame, np.ndarray, np.ndarray, np.ndarray]:
    base = load_current()
    base_logit, e323_bad, e216_bad = bad_axes(base)
    q2_sources = select_q2_sources()
    micro_sources = select_micro_sources()
    if q2_sources.empty or micro_sources.empty:
        pd.DataFrame().to_csv(CANDIDATE_OUT, index=False)
        return pd.DataFrame(), [], base, base_logit, e323_bad, e216_bad

    delta_cache: dict[str, np.ndarray] = {}

    def get_delta(row: dict[str, Any]) -> np.ndarray:
        name = str(row["basename"])
        if name not in delta_cache:
            path = locate(row.get("file", row.get("file_meta", name)))
            if path is None:
                path = locate(name)
            if path is None:
                raise FileNotFoundError(name)
            delta_cache[name] = load_delta(path, base, base_logit)
        return delta_cache[name]

    q2_weights = [0.55, 0.75, 1.00]
    micro_weights = [0.75, 1.00, 1.25]
    rows: list[dict[str, Any]] = []
    paths: list[Path] = []
    for q2_row in q2_sources.to_dict("records"):
        dq2 = get_delta(q2_row)
        q2_active_rows = int((np.sum(np.abs(dq2), axis=1) > EPS).sum())
        for micro_row in micro_sources.to_dict("records"):
            dm = get_delta(micro_row)
            micro_active_rows = int((np.sum(np.abs(dm), axis=1) > EPS).sum())
            overlap_rows = int(((np.sum(np.abs(dq2), axis=1) > EPS) & (np.sum(np.abs(dm), axis=1) > EPS)).sum())
            for wq in q2_weights:
                for wm in micro_weights:
                    variants = transform_variants(dq2, dm, wq, wm, e323_bad, e216_bad)
                    for variant_name, direction in variants.items():
                        if float(np.max(np.abs(direction))) > CAP * 1.80:
                            continue
                        candidate_id = (
                            f"q2_{q2_row['basename'][:18]}__micro_{micro_row['basename'][:18]}"
                            f"__w{wq:.2f}_{wm:.2f}_{variant_name}"
                        )
                        path = write_candidate(base, base_logit, direction, candidate_id)
                        paths.append(path)
                        row_abs = np.sum(np.abs(direction), axis=1)
                        rows.append(
                            {
                                "candidate_id": candidate_id,
                                "file": rel(path),
                                "basename": path.name,
                                "recipe": "q2_micro_signtransfer",
                                "variant": variant_name,
                                "q2_source": q2_row["basename"],
                                "micro_source": micro_row["basename"],
                                "q2_tail_mask": q2_row.get("tail_mask", ""),
                                "q2_topk": q2_row.get("topk", ""),
                                "q2_variant": q2_row.get("variant", ""),
                                "micro_variant": micro_row.get("variant", ""),
                                "q2_weight": float(wq),
                                "micro_weight": float(wm),
                                "q2_source_mean": float(q2_row["pred_delta_vs_current_mean"]),
                                "q2_source_p90": float(q2_row["pred_delta_vs_current_p90"]),
                                "micro_source_mean": float(micro_row["pred_delta_vs_current_mean"]),
                                "micro_source_p90": float(micro_row["pred_delta_vs_current_p90"]),
                                "q2_source_bad_axis": float(q2_row["incremental_bad_axis_vs_current"]),
                                "micro_source_bad_axis": float(micro_row["incremental_bad_axis_vs_current"]),
                                "q2_active_rows": q2_active_rows,
                                "micro_active_rows": micro_active_rows,
                                "source_overlap_rows": overlap_rows,
                                "changed_rows": int(np.any(np.abs(direction) > EPS, axis=1).sum()),
                                "changed_cells": int((np.abs(direction) > EPS).sum()),
                                "row_energy_entropy": entropy(row_abs),
                                "mean_abs_logit_delta": float(np.mean(np.abs(direction))),
                                "max_abs_logit_delta": float(np.max(np.abs(direction))),
                                "l1_logit_delta": float(np.sum(np.abs(direction))),
                                "cos_with_e323_bad": cos(direction, e323_bad),
                                "cos_with_e216_bad": cos(direction, e216_bad),
                                **target_abs(direction),
                            }
                        )
    candidates = pd.DataFrame(rows).drop_duplicates("basename").sort_values(
        ["variant", "q2_weight", "micro_weight", "q2_source", "micro_source"]
    ).reset_index(drop=True)
    keep = set(candidates["basename"])
    paths = [p for p in paths if p.name in keep]
    candidates.to_csv(CANDIDATE_OUT, index=False)
    return candidates, paths, base, base_logit, e323_bad, e216_bad


def score_paths(paths: list[Path]) -> pd.DataFrame:
    if not paths:
        pd.DataFrame().to_csv(SCORE_OUT, index=False)
        return pd.DataFrame()
    sample = load_sub(OUT / CURRENT)[KEYS]
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    features = build_features([CURRENT] + [rel(path) for path in paths], sample, refs, ref_vecs)
    scores = score_candidates(known, features, model_df)
    scores.to_csv(SCORE_OUT, index=False)
    return scores


def anatomy(paths: list[Path], base: pd.DataFrame, base_logit: np.ndarray, e323_bad: np.ndarray, e216_bad: np.ndarray) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for path in paths:
        cand = load_sub_frame(path, base[KEYS])
        delta = logit(cand[TARGETS].to_numpy(dtype=np.float64)) - base_logit
        rows.append(
            {
                "basename": path.name,
                "changed_rows": int(np.any(np.abs(delta) > EPS, axis=1).sum()),
                "changed_cells": int((np.abs(delta) > EPS).sum()),
                "l1_logit_delta": float(np.sum(np.abs(delta))),
                "mean_abs_logit_delta": float(np.mean(np.abs(delta))),
                "max_abs_logit_delta": float(np.max(np.abs(delta))),
                "cos_with_e323_bad": cos(delta, e323_bad),
                "cos_with_e216_bad": cos(delta, e216_bad),
                "signed_bad_overlap": float(np.mean((delta * e323_bad > 0.0) | (delta * e216_bad > 0.0))),
                **target_abs(delta),
            }
        )
    out = pd.DataFrame(rows).sort_values(["cos_with_e323_bad", "l1_logit_delta"]).reset_index(drop=True)
    out.to_csv(ANATOMY_OUT, index=False)
    return out


def test_meta(base: pd.DataFrame) -> pd.DataFrame:
    state = pd.read_parquet(OUT / "e273_human_diary_state_jepa_audit_features.parquet")
    meta_cols = [c for c in ["subject_id", "dateblock_group", "weekday", "is_weekend", "subject_order"] if c in state.columns and c not in KEYS]
    meta = state[state["split"].eq("test")][KEYS + meta_cols].copy()
    for col in ["sleep_date", "lifelog_date"]:
        meta[col] = pd.to_datetime(meta[col]).dt.strftime("%Y-%m-%d")
    keys = base[KEYS].copy()
    for col in ["sleep_date", "lifelog_date"]:
        keys[col] = pd.to_datetime(keys[col]).dt.strftime("%Y-%m-%d")
    aligned = keys.merge(meta, on=KEYS, how="left", validate="one_to_one")
    if aligned[meta_cols].isna().any().any():
        raise RuntimeError("test metadata alignment failed")
    return aligned.reset_index(drop=True)


def permute_within_groups(delta: np.ndarray, groups: pd.Series, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    arr = np.asarray(delta, dtype=np.float64)
    out = arr.copy()
    for _, idx in groups.groupby(groups).groups.items():
        idx_arr = np.asarray(list(idx), dtype=int)
        if len(idx_arr) > 1:
            out[idx_arr] = arr[idx_arr][rng.permutation(len(idx_arr))]
    return out


def null_delta(delta: np.ndarray, mode: str, meta: pd.DataFrame, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    arr = np.asarray(delta, dtype=np.float64).copy()
    if mode == "row_perm":
        return arr[rng.permutation(arr.shape[0]), :]
    if mode == "target_perm":
        return arr[:, rng.permutation(arr.shape[1])]
    if mode == "sign_flip":
        return -arr
    if mode == "row_sign":
        return arr * rng.choice([-1.0, 1.0], size=(arr.shape[0], 1))
    if mode == "cell_perm":
        flat = arr.reshape(-1).copy()
        rng.shuffle(flat)
        return flat.reshape(arr.shape)
    if mode == "subject_perm":
        return permute_within_groups(arr, meta["subject_id"], seed)
    if mode == "dateblock_perm":
        return permute_within_groups(arr, meta["dateblock_group"], seed)
    raise ValueError(mode)


def movement_null_stress(scores: pd.DataFrame, candidates: pd.DataFrame, base: pd.DataFrame, base_logit: np.ndarray) -> pd.DataFrame:
    if scores.empty or candidates.empty:
        pd.DataFrame().to_csv(MOVE_NULL_OUT, index=False)
        return pd.DataFrame()
    non_current = scores[~scores["basename"].eq(CURRENT)].copy()
    joined = non_current.merge(candidates, on="basename", how="left", suffixes=("_score", "_meta"))
    chosen = joined.sort_values(
        ["strict_promote_gate", "info_sensor_gate", "pred_delta_vs_current_p90", "pred_delta_vs_current_mean"],
        ascending=[False, False, True, True],
    ).head(MAX_NULL_CANDIDATES)
    if chosen.empty:
        pd.DataFrame().to_csv(MOVE_NULL_OUT, index=False)
        return pd.DataFrame()
    meta = test_meta(base)
    modes = ["row_perm", "target_perm", "sign_flip", "row_sign", "cell_perm", "subject_perm", "dateblock_perm"]
    null_paths: list[Path] = []
    null_rows: list[dict[str, Any]] = []
    NULL_DIR.mkdir(exist_ok=True)
    for rec in chosen.to_dict("records"):
        path = locate(rec.get("file_meta", rec.get("file_score", rec.get("file", ""))))
        if path is None:
            continue
        cand = load_sub_frame(path, base[KEYS])
        delta = logit(cand[TARGETS].to_numpy(dtype=np.float64)) - base_logit
        for mode in modes:
            for rep in range(NULL_REPS):
                nd = null_delta(delta, mode, meta, stable_seed(rec["basename"], mode, rep))
                out = base.copy()
                out[TARGETS] = clip_prob(expit(np.clip(base_logit + np.clip(nd, -CAP, CAP), -40.0, 40.0)))
                npath = NULL_DIR / f"submission_e342null_{safe_id(Path(rec['basename']).stem, 58)}_{mode}_r{rep}_{short_hash(out)}.csv"
                out.to_csv(npath, index=False)
                null_paths.append(npath)
                null_rows.append({"basename": rec["basename"], "null_basename": npath.name, "mode": mode, "rep": rep})
    if not null_paths:
        pd.DataFrame().to_csv(MOVE_NULL_OUT, index=False)
        return pd.DataFrame()
    sample = load_sub(OUT / CURRENT)[KEYS]
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    null_features = build_features([CURRENT] + [rel(path) for path in null_paths], sample, refs, ref_vecs)
    null_scores = score_candidates(known, null_features, model_df)
    cols = ["basename", "pred_delta_vs_current_mean", "pred_delta_vs_current_p90", "pred_beats_current_rate", "strict_promote_gate"]
    null_map = pd.DataFrame(null_rows).merge(null_scores[cols].rename(columns={"basename": "null_basename"}), on="null_basename", how="left")
    actual = non_current[cols].rename(
        columns={
            "pred_delta_vs_current_mean": "actual_mean",
            "pred_delta_vs_current_p90": "actual_p90",
            "pred_beats_current_rate": "actual_beats_rate",
            "strict_promote_gate": "actual_strict_promote",
        }
    )
    rows: list[dict[str, Any]] = []
    for basename, part in null_map.groupby("basename"):
        act = actual[actual["basename"].eq(basename)]
        if act.empty:
            continue
        a = act.iloc[0]
        rows.append(
            {
                "basename": basename,
                "null_count": int(len(part)),
                "actual_mean": float(a["actual_mean"]),
                "actual_p90": float(a["actual_p90"]),
                "actual_beats_rate": float(a["actual_beats_rate"]),
                "actual_strict_promote": bool(a["actual_strict_promote"]),
                "null_mean_best": float(part["pred_delta_vs_current_mean"].min()),
                "null_mean_median": float(part["pred_delta_vs_current_mean"].median()),
                "null_p90_best": float(part["pred_delta_vs_current_p90"].min()),
                "null_p90_median": float(part["pred_delta_vs_current_p90"].median()),
                "actual_mean_dominance": float(np.mean(float(a["actual_mean"]) < part["pred_delta_vs_current_mean"].to_numpy(dtype=float))),
                "actual_p90_dominance": float(np.mean(float(a["actual_p90"]) < part["pred_delta_vs_current_p90"].to_numpy(dtype=float))),
                "null_strict_promote_rate": float(part["strict_promote_gate"].astype(bool).mean()),
                "mode_count": int(part["mode"].nunique()),
                "strict_null_modes": ",".join(sorted(part.loc[part["strict_promote_gate"].astype(bool), "mode"].unique())),
            }
        )
    out = pd.DataFrame(rows).sort_values(
        ["actual_strict_promote", "actual_p90_dominance", "actual_mean_dominance", "actual_p90"],
        ascending=[False, False, False, True],
    )
    out.to_csv(MOVE_NULL_OUT, index=False)
    return out


def write_report(q2_sources: pd.DataFrame, micro_sources: pd.DataFrame, candidates: pd.DataFrame, scores: pd.DataFrame, anat: pd.DataFrame, nulls: pd.DataFrame) -> None:
    non_current = scores[~scores["basename"].eq(CURRENT)].copy() if len(scores) else pd.DataFrame()
    promoted = non_current[non_current["strict_promote_gate"].astype(bool)] if len(non_current) else pd.DataFrame()
    info = non_current[non_current["info_sensor_gate"].astype(bool)] if len(non_current) else pd.DataFrame()
    null_safe = pd.DataFrame()
    if len(nulls):
        null_safe = nulls[
            (nulls["actual_strict_promote"].astype(bool))
            & (nulls["actual_mean_dominance"] >= 0.70)
            & (nulls["actual_p90_dominance"] >= 0.75)
            & (nulls["null_strict_promote_rate"] <= 0.05)
        ]
    score_cols = [
        "basename",
        "promotion_decision",
        "pred_delta_vs_current_mean",
        "pred_delta_vs_current_p10",
        "pred_delta_vs_current_p90",
        "pred_beats_current_rate",
        "incremental_bad_axis_vs_current",
    ]
    cand_cols = [
        "basename",
        "variant",
        "q2_weight",
        "micro_weight",
        "q2_source_mean",
        "q2_source_p90",
        "micro_source_mean",
        "micro_source_p90",
        "source_overlap_rows",
        "changed_rows",
        "share_Q1",
        "share_Q2",
        "share_Q3",
        "cos_with_e323_bad",
    ]
    lines = [
        "# E342 Sign-Transfer Hidden Lifestyle-State Latent",
        "",
        "## Question",
        "",
        "Are the weak Q2 residual intervention tail and the weak Q1/Q3 human-social microstate coalition two projections of one hidden lifestyle state?",
        "",
        "## Source Selection",
        "",
        "### Q2 Residual-Tail Sources",
        "",
        md_table(q2_sources[["basename", "tail_mask", "topk", "variant", "scale", "pred_delta_vs_current_mean", "pred_delta_vs_current_p90", "pred_beats_current_rate", "incremental_bad_axis_vs_current"]], n=16, floatfmt=".9f")
        if len(q2_sources)
        else "_empty_",
        "",
        "### Q1/Q3 Microstate Sources",
        "",
        md_table(micro_sources[["basename", "recipe", "variant", "q1_weight", "q3_weight", "pred_delta_vs_current_mean", "pred_delta_vs_current_p90", "pred_beats_current_rate", "incremental_bad_axis_vs_current"]], n=20, floatfmt=".9f")
        if len(micro_sources)
        else "_empty_",
        "",
        "## Generated Candidates",
        "",
        f"- generated candidates: `{len(candidates)}`",
        f"- selector-promoted candidates: `{len(promoted)}`",
        f"- information-sensor candidates: `{len(info)}`",
        f"- movement-null-safe promoted candidates: `{len(null_safe)}`",
        "",
        "### Best Selector Scores",
        "",
        md_table(
            non_current.sort_values(
                ["strict_promote_gate", "info_sensor_gate", "pred_delta_vs_current_p90", "pred_delta_vs_current_mean"],
                ascending=[False, False, True, True],
            )[score_cols]
            if len(non_current)
            else non_current,
            n=50,
            floatfmt=".9f",
        ),
        "",
        "### Candidate Anatomy",
        "",
        md_table(candidates[cand_cols].sort_values(["cos_with_e323_bad", "changed_rows"]) if len(candidates) else candidates, n=40, floatfmt=".9f"),
        "",
        "## Movement-Null Stress",
        "",
        md_table(nulls, n=40, floatfmt=".9f"),
        "",
        "## Decision",
        "",
    ]
    if len(null_safe):
        best = null_safe.sort_values(["actual_p90", "actual_mean"]).iloc[0]
        lines.append(f"`{best['basename']}` is the top submission candidate: it clears selector and fresh movement-null gates.")
    elif len(promoted):
        best = promoted.sort_values(["pred_delta_vs_current_p90", "pred_delta_vs_current_mean"]).iloc[0]
        lines.append(f"`{best['basename']}` crosses selector visibility, but no promoted candidate survives movement-null stress. Treat sign-transfer as shortcut-prone.")
    elif len(info):
        best = non_current.sort_values(["pred_delta_vs_current_p90", "pred_delta_vs_current_mean"]).iloc[0]
        if float(best["pred_delta_vs_current_p90"]) < -0.00005:
            lines.append(
                f"Sign-transfer crosses the strict p90 visibility threshold (`{best['pred_delta_vs_current_p90']:.9f}`), "
                f"but remains an information sensor because incremental bad-axis is `{best['incremental_bad_axis_vs_current']:.9f}` above the `0.015` cap."
            )
        else:
            lines.append(f"Sign-transfer remains an information sensor only. Best p90 is `{best['pred_delta_vs_current_p90']:.9f}`, below submission standard but useful as support-axis evidence.")
    else:
        lines.append("Combining Q2 residual tails with Q1/Q3 microstates does not produce a visible shared latent. This weakens the single hidden lifestyle-state hypothesis in this form.")
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- `{Q2_SOURCE_OUT.name}`",
            f"- `{MICRO_SOURCE_OUT.name}`",
            f"- `{CANDIDATE_OUT.name}`",
            f"- `{SCORE_OUT.name}`",
            f"- `{ANATOMY_OUT.name}`",
            f"- `{MOVE_NULL_OUT.name}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    if CANDIDATE_OUT.exists() and SCORE_OUT.exists() and ANATOMY_OUT.exists():
        candidates = pd.read_csv(CANDIDATE_OUT)
        scores = pd.read_csv(SCORE_OUT)
        anat = pd.read_csv(ANATOMY_OUT)
        base = load_current()
        base_logit = logit(base[TARGETS].to_numpy(dtype=np.float64))
    else:
        candidates, paths, base, base_logit, e323_bad, e216_bad = materialize_candidates()
        scores = score_paths(paths)
        anat = anatomy(paths, base, base_logit, e323_bad, e216_bad)
    if MOVE_NULL_OUT.exists():
        nulls = pd.read_csv(MOVE_NULL_OUT)
    else:
        nulls = movement_null_stress(scores, candidates, base, base_logit)
    q2_sources = pd.read_csv(Q2_SOURCE_OUT) if Q2_SOURCE_OUT.exists() else select_q2_sources()
    micro_sources = pd.read_csv(MICRO_SOURCE_OUT) if MICRO_SOURCE_OUT.exists() else select_micro_sources()
    write_report(q2_sources, micro_sources, candidates, scores, anat, nulls)
    print(REPORT_OUT)
    if len(scores):
        non_current = scores[~scores["basename"].eq(CURRENT)].copy()
        cols = ["basename", "promotion_decision", "pred_delta_vs_current_mean", "pred_delta_vs_current_p90", "pred_beats_current_rate", "incremental_bad_axis_vs_current"]
        print(non_current[cols].head(50).round(9).to_string(index=False))
    if len(nulls):
        print("[movement-null]")
        print(nulls.head(30).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
