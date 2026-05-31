#!/usr/bin/env python3
"""E344: counter-axis support for sign-transfer lifestyle latent.

E342 found a selector-visible hidden lifestyle-state coalition:
Q2 inverse residual tail + Q1/Q3 microstate sign-transfer.  The blocker was
not visibility, but too much incremental bad-axis load.  E343 tried to clean
the signal by projection and lost most of the p90 edge.

This experiment asks a different question:

    Is there an independent counter-axis that can reduce the bad-axis load
    while preserving the E342 lifestyle-state visibility?

JEPA translation:
    context = E342 visible hidden state
    target  = a counter-state learned from prior local experiments whose
              movement is anti-bad-axis but not used as a public submission
    action  = small logit-space composition, accepted only if it passes the
              E272 selector and movement-null stress

No public LB is used.
"""

from __future__ import annotations

from pathlib import Path
import hashlib
import shutil
import sys
from typing import Any
import warnings

import numpy as np
import pandas as pd
from scipy.special import expit


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
NULL_DIR = OUT / "e344_counter_axis_nulls"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e272_public_free_candidate_audit import CURRENT, build_features, evaluate_models, score_candidates  # noqa: E402
from e328_ownlatent_lifestyle_state_experiment import load_sub_frame, md_table, safe_id  # noqa: E402
from e337_residual_lifestyle_cluster_state import bad_axes, cell_bad_veto, center_by_target, cos, target_abs  # noqa: E402
from public_anchor_bottleneck_decomposition import KEYS, TARGETS, load_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

RNG_SEED = 20260531 + 344
EPS = 1.0e-12
CAP = 0.18
MAX_E342_SOURCES = 8
MAX_COUNTER_SOURCES = 14
MAX_NULL_CANDIDATES = 32
NULL_REPS = 4

E342_SOURCE_OUT = OUT / "e344_counter_axis_e342_sources.csv"
COUNTER_SOURCE_OUT = OUT / "e344_counter_axis_counter_sources.csv"
CANDIDATE_OUT = OUT / "e344_counter_axis_candidates.csv"
SCORE_OUT = OUT / "e344_counter_axis_scores.csv"
ANATOMY_OUT = OUT / "e344_counter_axis_anatomy.csv"
MOVE_NULL_OUT = OUT / "e344_counter_axis_movement_nulls.csv"
REPORT_OUT = OUT / "e344_counter_axis_report.md"


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
    path = OUT / f"submission_e344_counteraxis_{safe_id(candidate_id, 112)}_{short_hash(out)}.csv"
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


def resolve_file_column(df: pd.DataFrame) -> pd.Series:
    for col in ["file", "source_path", "file_meta", "file_score"]:
        if col in df.columns:
            return df[col].astype(str)
    return df["basename"].map(lambda x: str(OUT / str(x)))


def select_e342_sources() -> pd.DataFrame:
    scores = pd.read_csv(OUT / "e342_signtransfer_scores.csv").drop_duplicates("basename", keep="first")
    candidates = pd.read_csv(OUT / "e342_signtransfer_candidates.csv")
    null_path = OUT / "e342_signtransfer_movement_nulls.csv"
    nulls = pd.read_csv(null_path) if null_path.exists() else pd.DataFrame()
    merged = scores[~scores["basename"].eq(CURRENT)].merge(candidates, on="basename", how="left", suffixes=("_score", "_meta"))
    if "file_meta" in merged:
        merged["file"] = merged["file_meta"]
    elif "file_score" in merged:
        merged["file"] = merged["file_score"]
    else:
        merged["file"] = resolve_file_column(merged)
    if len(nulls):
        merged = merged.merge(nulls, on="basename", how="left", suffixes=("", "_null"))
    for col, default in [
        ("actual_p90_dominance", 0.50),
        ("actual_mean_dominance", 0.50),
        ("null_strict_promote_rate", 1.0),
    ]:
        if col not in merged:
            merged[col] = default
        merged[col] = pd.to_numeric(merged[col], errors="coerce").fillna(default)
    pool = merged[
        (merged["pred_delta_vs_current_p90"] < -0.000050)
        & (merged["pred_beats_current_rate"] >= 0.95)
        & (merged["incremental_bad_axis_vs_current"] > 0.015)
        & (merged["incremental_bad_axis_vs_current"] <= 0.025)
        & (merged["actual_p90_dominance"] >= 0.85)
        & (merged["null_strict_promote_rate"] <= 0.05)
        & merged["file"].notna()
    ].copy()
    pool["source_path_exists"] = pool["file"].map(lambda x: locate(x) is not None)
    pool = pool[pool["source_path_exists"]].copy()
    pool["visibility_margin"] = -pool["pred_delta_vs_current_p90"]
    pool["bad_excess"] = pool["incremental_bad_axis_vs_current"] - 0.015
    pool["source_rank_score"] = pool["visibility_margin"] / (pool["bad_excess"].clip(lower=0.0005))
    pool = pool.sort_values(
        ["source_rank_score", "visibility_margin", "pred_delta_vs_current_mean"],
        ascending=[False, False, True],
    ).head(MAX_E342_SOURCES)
    pool.to_csv(E342_SOURCE_OUT, index=False)
    return pool.reset_index(drop=True)


def iter_score_tables() -> pd.DataFrame:
    rows: list[pd.DataFrame] = []
    wanted = {
        "basename",
        "file",
        "source_path",
        "pred_delta_vs_current_mean",
        "pred_delta_vs_current_p90",
        "pred_beats_current_rate",
        "incremental_bad_axis_vs_current",
        "strict_promote_gate",
        "info_sensor_gate",
        "promotion_decision",
    }
    for path in OUT.glob("*_scores.csv"):
        if path.name.startswith(("e342_", "e343_", "e344_")):
            continue
        try:
            df = pd.read_csv(path, usecols=lambda c: c in wanted)
        except Exception:
            continue
        required = {"basename", "pred_delta_vs_current_mean", "pred_delta_vs_current_p90", "pred_beats_current_rate", "incremental_bad_axis_vs_current"}
        if not required.issubset(df.columns):
            continue
        df = df[~df["basename"].eq(CURRENT)].copy()
        if df.empty:
            continue
        df["score_file"] = path.name
        df["file"] = resolve_file_column(df)
        rows.append(df)
    if not rows:
        return pd.DataFrame()
    out = pd.concat(rows, ignore_index=True)
    out = out.drop_duplicates("basename", keep="first").reset_index(drop=True)
    return out


def select_counter_sources() -> pd.DataFrame:
    all_scores = iter_score_tables()
    if all_scores.empty:
        all_scores.to_csv(COUNTER_SOURCE_OUT, index=False)
        return all_scores
    pool = all_scores[
        (all_scores["incremental_bad_axis_vs_current"] < -0.001)
        & (all_scores["incremental_bad_axis_vs_current"] >= -0.050)
        & (all_scores["pred_delta_vs_current_p90"] < 0.000050)
        & (all_scores["pred_delta_vs_current_mean"] < 0.000100)
        & (all_scores["pred_beats_current_rate"] >= 0.65)
        & all_scores["file"].notna()
    ].copy()
    pool["source_path_exists"] = pool["file"].map(lambda x: locate(x) is not None)
    pool = pool[pool["source_path_exists"]].copy()
    pool["family"] = pool["score_file"].str.replace("_scores.csv", "", regex=False)
    pool["counter_strength"] = -pool["incremental_bad_axis_vs_current"]
    pool["p90_health"] = -pool["pred_delta_vs_current_p90"]
    pool["risk_penalty"] = pool["counter_strength"].clip(lower=0.0) * (pool["pred_delta_vs_current_p90"] < -0.001).astype(float)
    pool["counter_rank_score"] = pool["counter_strength"] + 0.20 * pool["pred_beats_current_rate"] + 50.0 * pool["p90_health"] - 0.25 * pool["risk_penalty"]
    ranked = pool.sort_values(
        ["counter_rank_score", "pred_beats_current_rate", "pred_delta_vs_current_p90"],
        ascending=[False, False, True],
    )
    # Keep a few per family so one old failed generator cannot define the
    # entire counter-space.  The counter is support evidence, not the thesis.
    diversified = ranked.groupby("family", group_keys=False).head(4)
    diversified = diversified.sort_values(
        ["counter_rank_score", "pred_beats_current_rate", "pred_delta_vs_current_p90"],
        ascending=[False, False, True],
    ).head(MAX_COUNTER_SOURCES)
    diversified.to_csv(COUNTER_SOURCE_OUT, index=False)
    return diversified.reset_index(drop=True)


def counter_variants(source: np.ndarray, counter: np.ndarray, weight: float, e323_bad: np.ndarray, e216_bad: np.ndarray) -> dict[str, np.ndarray]:
    patch = float(weight) * np.asarray(counter, dtype=np.float64)
    q2_keep = patch.copy()
    q2_idx = TARGETS.index("Q2")
    q2_keep[:, q2_idx] = 0.0
    bad_mask = ((source * e323_bad) > 0.0) | ((source * e216_bad) > 0.0)
    source_active = np.sum(np.abs(source), axis=1, keepdims=True) > EPS
    variants = {
        "add": source + patch,
        "cellveto": cell_bad_veto(source + patch, e323_bad, e216_bad, strength=0.25),
        "centered": center_by_target(cell_bad_veto(source + patch, e323_bad, e216_bad, strength=0.25)),
        "badcell_patch": source + patch * bad_mask,
        "preserve_q2": source + q2_keep,
        "source_rows_only": source + patch * source_active,
    }
    return {name: val for name, val in variants.items() if float(np.sum(np.abs(val))) > EPS}


def materialize_candidates() -> tuple[pd.DataFrame, list[Path], pd.DataFrame, np.ndarray, np.ndarray, np.ndarray]:
    base = load_current()
    base_logit, e323_bad, e216_bad = bad_axes(base)
    e342_sources = select_e342_sources()
    counters = select_counter_sources()
    if e342_sources.empty or counters.empty:
        pd.DataFrame().to_csv(CANDIDATE_OUT, index=False)
        return pd.DataFrame(), [], base, base_logit, e323_bad, e216_bad

    delta_cache: dict[str, np.ndarray] = {}

    def get_delta(rec: dict[str, Any]) -> np.ndarray:
        name = str(rec["basename"])
        if name not in delta_cache:
            path = locate(rec.get("file", name))
            if path is None:
                raise FileNotFoundError(name)
            delta_cache[name] = load_delta(path, base, base_logit)
        return delta_cache[name]

    weights = [0.04, 0.07, 0.10, 0.14, 0.20]
    rows: list[dict[str, Any]] = []
    paths: list[Path] = []
    for src in e342_sources.to_dict("records"):
        src_delta = get_delta(src)
        src_bad = float(src["incremental_bad_axis_vs_current"])
        src_rows = np.sum(np.abs(src_delta), axis=1) > EPS
        for counter in counters.to_dict("records"):
            counter_delta = get_delta(counter)
            counter_rows = np.sum(np.abs(counter_delta), axis=1) > EPS
            overlap_rows = int((src_rows & counter_rows).sum())
            for weight in weights:
                for variant, direction in counter_variants(src_delta, counter_delta, weight, e323_bad, e216_bad).items():
                    if float(np.max(np.abs(direction))) > CAP * 1.80:
                        continue
                    candidate_id = (
                        f"e342_{Path(src['basename']).stem[:34]}"
                        f"__ctr_{Path(counter['basename']).stem[:34]}"
                        f"__w{weight:.2f}_{variant}"
                    )
                    path = write_candidate(base, base_logit, direction, candidate_id)
                    paths.append(path)
                    row_abs = np.sum(np.abs(direction), axis=1)
                    rows.append(
                        {
                            "candidate_id": candidate_id,
                            "file": rel(path),
                            "basename": path.name,
                            "recipe": "e342_visible_plus_counter_axis",
                            "variant": variant,
                            "counter_weight": float(weight),
                            "e342_source": src["basename"],
                            "counter_source": counter["basename"],
                            "counter_family": counter["family"],
                            "e342_source_mean": float(src["pred_delta_vs_current_mean"]),
                            "e342_source_p90": float(src["pred_delta_vs_current_p90"]),
                            "e342_source_bad_axis": src_bad,
                            "e342_source_null_p90_dom": float(src.get("actual_p90_dominance", np.nan)),
                            "counter_source_mean": float(counter["pred_delta_vs_current_mean"]),
                            "counter_source_p90": float(counter["pred_delta_vs_current_p90"]),
                            "counter_source_bad_axis": float(counter["incremental_bad_axis_vs_current"]),
                            "expected_bad_axis_linear": src_bad + weight * float(counter["incremental_bad_axis_vs_current"]),
                            "source_active_rows": int(src_rows.sum()),
                            "counter_active_rows": int(counter_rows.sum()),
                            "source_counter_overlap_rows": overlap_rows,
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
        ["expected_bad_axis_linear", "e342_source_p90", "counter_family", "counter_weight"]
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
    scores = scores.drop_duplicates("basename", keep="first").reset_index(drop=True)
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
                npath = NULL_DIR / f"submission_e344null_{safe_id(Path(rec['basename']).stem, 58)}_{mode}_r{rep}_{short_hash(out)}.csv"
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


def write_report(e342_sources: pd.DataFrame, counters: pd.DataFrame, candidates: pd.DataFrame, scores: pd.DataFrame, anat: pd.DataFrame, nulls: pd.DataFrame) -> None:
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
        "counter_weight",
        "counter_family",
        "e342_source_p90",
        "e342_source_bad_axis",
        "counter_source_p90",
        "counter_source_bad_axis",
        "expected_bad_axis_linear",
        "source_counter_overlap_rows",
        "share_Q1",
        "share_Q2",
        "share_Q3",
        "share_S1",
        "share_S3",
    ]
    lines = [
        "# E344 Counter-Axis Sign-Transfer Latent",
        "",
        "## Question",
        "",
        "Can the E342 selector-visible hidden lifestyle-state signal keep its p90 edge if we add only a small independent counter-axis that reduces public-bad geometry?",
        "",
        "## E342 Source Near-Misses",
        "",
        f"- E342 sources: `{len(e342_sources)}`",
        "",
        md_table(
            e342_sources[["basename", "pred_delta_vs_current_mean", "pred_delta_vs_current_p90", "pred_beats_current_rate", "incremental_bad_axis_vs_current", "actual_p90_dominance", "null_strict_promote_rate"]]
            if len(e342_sources)
            else e342_sources,
            n=20,
            floatfmt=".9f",
        ),
        "",
        "## Counter Sources",
        "",
        f"- counter sources: `{len(counters)}`",
        "",
        md_table(
            counters[["basename", "family", "pred_delta_vs_current_mean", "pred_delta_vs_current_p90", "pred_beats_current_rate", "incremental_bad_axis_vs_current", "promotion_decision"]]
            if len(counters)
            else counters,
            n=30,
            floatfmt=".9f",
        ),
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
        md_table(candidates[cand_cols], n=40, floatfmt=".9f") if len(candidates) else "_empty_",
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
        src_path = locate(best["basename"])
        uploadsafe = ""
        if src_path is not None:
            tag = str(best["basename"]).replace(".csv", "").split("_")[-1]
            upload_path = OUT / f"submission_e344_counteraxis_lifestyle_{tag}_uploadsafe.csv"
            shutil.copyfile(src_path, upload_path)
            uploadsafe = f" Use `{rel(upload_path)}` for upload-safe submission."
        lines.append(f"`{best['basename']}` is a submission candidate: it keeps selector visibility, clears bad-axis, and survives movement-null stress.{uploadsafe}")
    elif len(promoted):
        lines.append("Counter-axis composition creates selector-promoted files, but none survive movement-null stress. The support axis is still too shortcut-prone.")
    elif len(info):
        best = non_current.sort_values(["pred_delta_vs_current_p90", "pred_delta_vs_current_mean"]).iloc[0]
        lines.append(
            f"Counter-axis composition remains information-sensor only. Best p90 is `{best['pred_delta_vs_current_p90']:.9f}` "
            f"with bad-axis `{best['incremental_bad_axis_vs_current']:.9f}`. This means independent counter support did not yet make E342 submission-safe."
        )
    else:
        lines.append("No visible E342+counter latent survived selector stress. This weakens the separable-counter-axis hypothesis.")
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- `{E342_SOURCE_OUT.name}`",
            f"- `{COUNTER_SOURCE_OUT.name}`",
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
        scores = pd.read_csv(SCORE_OUT).drop_duplicates("basename", keep="first").reset_index(drop=True)
        scores.to_csv(SCORE_OUT, index=False)
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
    e342_sources = pd.read_csv(E342_SOURCE_OUT) if E342_SOURCE_OUT.exists() else select_e342_sources()
    counters = pd.read_csv(COUNTER_SOURCE_OUT) if COUNTER_SOURCE_OUT.exists() else select_counter_sources()
    write_report(e342_sources, counters, candidates, scores, anat, nulls)
    print(REPORT_OUT)
    if len(scores):
        non_current = scores[~scores["basename"].eq(CURRENT)].copy()
        cols = ["basename", "promotion_decision", "pred_delta_vs_current_mean", "pred_delta_vs_current_p90", "pred_beats_current_rate", "incremental_bad_axis_vs_current"]
        ordered = non_current.sort_values(
            ["strict_promote_gate", "info_sensor_gate", "pred_delta_vs_current_p90"],
            ascending=[False, False, True],
        )
        print(ordered[cols].head(60).round(9).to_string(index=False))
    if len(nulls):
        print("[movement-null]")
        print(nulls.head(30).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
