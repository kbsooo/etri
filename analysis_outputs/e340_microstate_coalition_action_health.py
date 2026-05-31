#!/usr/bin/env python3
"""E340: microstate coalition action-health test.

E335, E338, and E339 all found the same shape of evidence:

    hidden lifestyle micro-state: plausible and often null-dominant
    single probability action: too small to submit

This experiment asks whether that is merely a selector-resolution problem.
Instead of scaling one state harder, it combines different safe-invisible
micro-states, mainly Q1 action-health tails and Q3/dateblock episode sensors.

JEPA translation for this table:

    context = candidate geometry + source family + movement-null health
    target  = action-health / selector visibility representation
    action  = coalition of independent hidden lifestyle-state sensors

No public LB is used.  A public candidate must pass the E272 selector and a
fresh movement-null stress that includes row, target, sign, subject, and
dateblock placement nulls.
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
from scipy.stats import spearmanr
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
NULL_DIR = OUT / "e340_microstate_nulls"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e272_public_free_candidate_audit import CURRENT, build_features, evaluate_models, score_candidates  # noqa: E402
from e328_ownlatent_lifestyle_state_experiment import load_sub_frame, md_table, safe_id  # noqa: E402
from e331_residual_state_localization import train_test_state  # noqa: E402
from e337_residual_lifestyle_cluster_state import (  # noqa: E402
    bad_axes,
    cell_bad_veto,
    center_by_target,
    cos,
    short_hash,
    target_abs,
)
from public_anchor_bottleneck_decomposition import KEYS, TARGETS, load_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

RNG_SEED = 20260531 + 340
EPS = 1.0e-12
CAP = 0.16
MAX_Q1_SOURCES = 7
MAX_Q3_SOURCES = 14
MAX_NULL_CANDIDATES = 24
NULL_REPS = 4

SOURCE_OUT = OUT / "e340_microstate_coalition_sources.csv"
LATENT_DIAG_OUT = OUT / "e340_microstate_action_health_latent_diag.csv"
CANDIDATE_OUT = OUT / "e340_microstate_coalition_candidates.csv"
SCORE_OUT = OUT / "e340_microstate_coalition_scores.csv"
ANATOMY_OUT = OUT / "e340_microstate_coalition_anatomy.csv"
MOVE_NULL_OUT = OUT / "e340_microstate_coalition_movement_nulls.csv"
REPORT_OUT = OUT / "e340_microstate_coalition_report.md"

ARCHIVES = [
    {
        "exp": "E335",
        "family_hint": "Q1_action_health_tail",
        "target_hint": "Q1",
        "candidates": OUT / "e335_q1_action_health_candidates.csv",
        "scores": OUT / "e335_q1_action_health_candidate_scores.csv",
        "anatomy": OUT / "e335_q1_action_health_candidate_anatomy.csv",
        "movement": OUT / "e335_q1_action_health_movement_nulls.csv",
    },
    {
        "exp": "E338",
        "family_hint": "Q3_episode_local",
        "target_hint": "Q3",
        "candidates": OUT / "e338_cluster_local_episode_candidates.csv",
        "scores": OUT / "e338_cluster_local_episode_scores.csv",
        "anatomy": OUT / "e338_cluster_local_episode_anatomy.csv",
        "movement": OUT / "e338_cluster_local_episode_movement_nulls.csv",
    },
    {
        "exp": "E339",
        "family_hint": "Q3_episode_amplifier",
        "target_hint": "Q3",
        "candidates": OUT / "e339_q3_episode_gate_amplifier_candidates.csv",
        "scores": OUT / "e339_q3_episode_gate_amplifier_scores.csv",
        "anatomy": OUT / "e339_q3_episode_gate_amplifier_anatomy.csv",
        "movement": OUT / "e339_q3_episode_gate_amplifier_movement_nulls.csv",
    },
]


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
    candidates = []
    if raw.is_absolute():
        candidates.append(raw)
    else:
        candidates.append(ROOT / raw)
        candidates.append(OUT / raw.name)
        candidates.append(OUT / str(path_or_name))
    for path in candidates:
        if path.exists():
            return path
    return None


def load_current() -> pd.DataFrame:
    return load_sub(OUT / CURRENT).sort_values(KEYS).reset_index(drop=True)


def safe_spearman(a: pd.Series | np.ndarray, b: pd.Series | np.ndarray) -> float:
    x = pd.Series(a, dtype="float64")
    y = pd.Series(b, dtype="float64")
    mask = x.notna() & y.notna()
    if int(mask.sum()) < 5:
        return np.nan
    x = x[mask]
    y = y[mask]
    if x.nunique() < 2 or y.nunique() < 2:
        return np.nan
    val = spearmanr(x, y).correlation
    return float(val) if np.isfinite(val) else np.nan


def normalize_archive_frame(cfg: dict[str, Any]) -> pd.DataFrame:
    cand = pd.read_csv(cfg["candidates"])
    scores = pd.read_csv(cfg["scores"])
    scores = scores[~scores["basename"].eq(CURRENT)].copy()
    anatomy = pd.read_csv(cfg["anatomy"]) if cfg["anatomy"].exists() else pd.DataFrame()
    movement = pd.read_csv(cfg["movement"]) if cfg["movement"].exists() else pd.DataFrame()

    merged = scores.merge(cand, on="basename", how="left", suffixes=("", "_cand"))
    if len(anatomy):
        merged = merged.merge(anatomy, on="basename", how="left", suffixes=("", "_anat"))
    if len(movement):
        merged = merged.merge(movement, on="basename", how="left", suffixes=("", "_move"))

    merged["exp"] = cfg["exp"]
    merged["family_hint"] = cfg["family_hint"]
    merged["target_hint"] = cfg["target_hint"]
    if "file_cand" in merged:
        merged["candidate_path"] = merged["file_cand"]
    elif "file" in merged:
        merged["candidate_path"] = merged["file"]
    else:
        merged["candidate_path"] = ""
    merged["path_exists"] = merged["candidate_path"].map(lambda p: locate(p) is not None)

    for col, default in [
        ("actual_mean_dominance", 0.50),
        ("actual_p90_dominance", 0.50),
        ("null_strict_promote_rate", 1.0),
        ("pred_delta_vs_current_mean", np.nan),
        ("pred_delta_vs_current_p90", np.nan),
        ("pred_beats_current_rate", 0.0),
        ("incremental_bad_axis_vs_current", 0.0),
        ("mean_abs_logit_delta", np.nan),
        ("max_abs_logit_delta", np.nan),
        ("l1_logit_delta", np.nan),
    ]:
        if col not in merged:
            merged[col] = default
        merged[col] = pd.to_numeric(merged[col], errors="coerce").fillna(default)

    for target in TARGETS:
        share_col = f"share_{target}"
        abs_col = f"abs_{target}"
        if share_col not in merged:
            merged[share_col] = 0.0
        if abs_col not in merged:
            merged[abs_col] = 0.0
        merged[share_col] = pd.to_numeric(merged[share_col], errors="coerce").fillna(0.0)
        merged[abs_col] = pd.to_numeric(merged[abs_col], errors="coerce").fillna(0.0)

    merged["has_fresh_null"] = merged["actual_p90_dominance"].notna() & (merged["null_strict_promote_rate"] <= 1.0)
    merged["visibility_margin"] = -merged["pred_delta_vs_current_p90"]
    merged["mean_margin"] = -merged["pred_delta_vs_current_mean"]
    merged["bad_axis_penalty"] = merged["incremental_bad_axis_vs_current"].abs()
    merged["null_health"] = (
        0.45 * merged["actual_p90_dominance"]
        + 0.30 * merged["actual_mean_dominance"]
        + 0.25 * (1.0 - merged["null_strict_promote_rate"].clip(0.0, 1.0))
    )
    merged["action_health_score"] = (
        4500.0 * merged["visibility_margin"].clip(-0.00005, 0.00020)
        + 1400.0 * merged["mean_margin"].clip(-0.00010, 0.00040)
        + 0.55 * merged["pred_beats_current_rate"]
        + 0.55 * merged["null_health"]
        - 8.0 * merged["bad_axis_penalty"].clip(0.0, 0.08)
    )
    merged["safe_invisible_source"] = (
        merged["path_exists"]
        & (merged["pred_delta_vs_current_mean"] < 0.0)
        & (merged["pred_beats_current_rate"] >= 0.86)
        & (merged["pred_delta_vs_current_p90"] < 0.00002)
        & (merged["actual_p90_dominance"] >= 0.80)
        & (merged["null_strict_promote_rate"] <= 0.05)
        & (merged["bad_axis_penalty"] <= 0.015)
    )
    return merged


def build_archive() -> pd.DataFrame:
    frames = [normalize_archive_frame(cfg) for cfg in ARCHIVES]
    archive = pd.concat(frames, ignore_index=True, sort=False)
    archive = archive[archive["path_exists"]].copy()
    archive = archive.sort_values(
        ["safe_invisible_source", "action_health_score", "visibility_margin"],
        ascending=[False, False, False],
    ).reset_index(drop=True)
    archive.to_csv(SOURCE_OUT, index=False)
    return archive


def action_health_latent_diagnostic(archive: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    feature_num = [
        "pred_delta_vs_current_mean",
        "pred_delta_vs_current_p90",
        "pred_beats_current_rate",
        "incremental_bad_axis_vs_current",
        "mean_abs_logit_delta",
        "max_abs_logit_delta",
        "l1_logit_delta",
        *[f"share_{t}" for t in TARGETS],
        *[f"abs_{t}" for t in TARGETS],
    ]
    feature_num = [c for c in feature_num if c in archive.columns]
    feature_cat = [c for c in ["exp", "family_hint", "target_hint", "family", "config", "mode", "transform", "recipe"] if c in archive.columns]
    if len(archive) < 12 or archive["exp"].nunique() < 2:
        pd.DataFrame().to_csv(LATENT_DIAG_OUT, index=False)
        return pd.DataFrame()

    groups = archive["exp"].astype(str).to_numpy()
    n_splits = min(3, archive["exp"].nunique())
    cv = GroupKFold(n_splits=n_splits)
    targets = ["visibility_margin", "action_health_score", "null_health"]

    transformers: list[tuple[str, Any, list[str]]] = []
    if feature_num:
        transformers.append(("num", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), feature_num))
    if feature_cat:
        transformers.append(
            (
                "cat",
                make_pipeline(SimpleImputer(strategy="most_frequent"), OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
                feature_cat,
            )
        )

    for target in targets:
        y = archive[target].astype(float).to_numpy()
        for model_name, estimator in [
            ("ridge", Ridge(alpha=5.0)),
            ("extratrees", ExtraTreesRegressor(n_estimators=240, min_samples_leaf=3, random_state=RNG_SEED, n_jobs=-1)),
        ]:
            oof = np.full(len(archive), np.nan, dtype=float)
            for tr, va in cv.split(archive, groups=groups):
                model = make_pipeline(ColumnTransformer(transformers, remainder="drop"), estimator)
                model.fit(archive.iloc[tr][feature_num + feature_cat], y[tr])
                oof[va] = model.predict(archive.iloc[va][feature_num + feature_cat])
            rows.append(
                {
                    "target": target,
                    "model": model_name,
                    "rows": int(len(archive)),
                    "groups": int(archive["exp"].nunique()),
                    "oof_spearman": safe_spearman(y, oof),
                    "oof_mae": float(np.nanmean(np.abs(oof - y))),
                    "target_mean": float(np.nanmean(y)),
                    "target_std": float(np.nanstd(y)),
                }
            )
    out = pd.DataFrame(rows).sort_values(["target", "oof_spearman"], ascending=[True, False]).reset_index(drop=True)
    out.to_csv(LATENT_DIAG_OUT, index=False)
    return out


def source_pools(archive: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    base = archive[archive["safe_invisible_source"]].copy()
    if base.empty:
        base = archive[
            (archive["pred_delta_vs_current_mean"] < 0.0)
            & (archive["pred_beats_current_rate"] >= 0.85)
            & (archive["bad_axis_penalty"] <= 0.018)
        ].copy()
    q1 = base[base["target_hint"].eq("Q1")].sort_values(
        ["actual_p90_dominance", "visibility_margin", "action_health_score"],
        ascending=[False, False, False],
    )
    q3 = base[base["target_hint"].eq("Q3")].sort_values(
        ["actual_p90_dominance", "visibility_margin", "action_health_score"],
        ascending=[False, False, False],
    )
    return q1.head(MAX_Q1_SOURCES).reset_index(drop=True), q3.head(MAX_Q3_SOURCES).reset_index(drop=True)


def load_delta(path: Path, base: pd.DataFrame, base_logit: np.ndarray) -> np.ndarray:
    cand = load_sub_frame(path, base[KEYS]).sort_values(KEYS).reset_index(drop=True)
    return logit(cand[TARGETS].to_numpy(dtype=np.float64)) - base_logit


def write_candidate(base: pd.DataFrame, base_logit: np.ndarray, delta: np.ndarray, candidate_id: str) -> Path:
    out = base.copy()
    out[TARGETS] = expit(np.clip(base_logit + np.clip(delta, -CAP, CAP), -40.0, 40.0))
    path = OUT / f"submission_e340_{safe_id(candidate_id, 112)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def materialize_candidates(archive: pd.DataFrame, base: pd.DataFrame) -> tuple[pd.DataFrame, list[Path], np.ndarray, np.ndarray, np.ndarray]:
    q1, q3 = source_pools(archive)
    base_logit, e323_bad, e216_bad = bad_axes(base)
    if q1.empty or q3.empty:
        pd.DataFrame().to_csv(CANDIDATE_OUT, index=False)
        return pd.DataFrame(), [], base_logit, e323_bad, e216_bad

    delta_cache: dict[str, np.ndarray] = {}

    def get_delta(row: pd.Series) -> np.ndarray:
        key = str(row["basename"])
        if key not in delta_cache:
            path = locate(row["candidate_path"])
            if path is None:
                raise FileNotFoundError(str(row["candidate_path"]))
            delta_cache[key] = load_delta(path, base, base_logit)
        return delta_cache[key]

    q1_weights = [0.75, 1.00, 1.25, 1.50]
    q3_weights = [1.00, 1.50, 2.00, 2.60, 3.20]
    variants = {
        "raw": lambda d: d,
        "bad_veto": lambda d: cell_bad_veto(d, e323_bad, e216_bad, strength=0.35),
        "target_centered": center_by_target,
        "veto_centered": lambda d: center_by_target(cell_bad_veto(d, e323_bad, e216_bad, strength=0.35)),
    }

    rows: list[dict[str, Any]] = []
    paths: list[Path] = []
    for q1_row in q1.to_dict("records"):
        d1 = get_delta(pd.Series(q1_row))
        for q3_row in q3.to_dict("records"):
            d3 = get_delta(pd.Series(q3_row))
            for w1 in q1_weights:
                for w3 in q3_weights:
                    raw = float(w1) * d1 + float(w3) * d3
                    for variant_name, transform in variants.items():
                        direction = transform(raw)
                        if np.sum(np.abs(direction)) <= EPS:
                            continue
                        candidate_id = f"q1_{q1_row['exp']}_{q1_row['basename'][:18]}__q3_{q3_row['exp']}_{q3_row['basename'][:18]}__w{w1:.2f}_{w3:.2f}_{variant_name}"
                        path = write_candidate(base, base_logit, direction, candidate_id)
                        paths.append(path)
                        rows.append(
                            {
                                "candidate_id": candidate_id,
                                "file": rel(path),
                                "basename": path.name,
                                "recipe": "q1_q3_microstate_pair",
                                "variant": variant_name,
                                "q1_source": q1_row["basename"],
                                "q3_source": q3_row["basename"],
                                "q1_weight": float(w1),
                                "q3_weight": float(w3),
                                "source_health_mean": float(np.mean([q1_row["action_health_score"], q3_row["action_health_score"]])),
                                "source_p90_dom_min": float(min(q1_row["actual_p90_dominance"], q3_row["actual_p90_dominance"])),
                                "source_null_rate_max": float(max(q1_row["null_strict_promote_rate"], q3_row["null_strict_promote_rate"])),
                                "changed_rows": int(np.any(np.abs(direction) > EPS, axis=1).sum()),
                                "changed_cells": int((np.abs(direction) > EPS).sum()),
                                "mean_abs_logit_delta": float(np.mean(np.abs(direction))),
                                "max_abs_logit_delta": float(np.max(np.abs(direction))),
                                "l1_logit_delta": float(np.sum(np.abs(direction))),
                                "cos_with_e323_bad": cos(direction, e323_bad),
                                "cos_with_e216_bad": cos(direction, e216_bad),
                                **target_abs(direction),
                            }
                        )

    # A small set of Q1 + two independent Q3 sensor coalitions tests whether
    # multiple Q3 episodes provide visibility without over-scaling one source.
    q3_top = q3.head(5).to_dict("records")
    for q1_row in q1.head(4).to_dict("records"):
        d1 = get_delta(pd.Series(q1_row))
        for i in range(len(q3_top)):
            for j in range(i + 1, len(q3_top)):
                d3a = get_delta(pd.Series(q3_top[i]))
                d3b = get_delta(pd.Series(q3_top[j]))
                for w1, w3 in [(1.0, 1.2), (1.25, 1.5), (1.5, 1.8)]:
                    raw = float(w1) * d1 + float(w3) * (d3a + d3b) / 2.0
                    direction = center_by_target(cell_bad_veto(raw, e323_bad, e216_bad, strength=0.35))
                    if np.sum(np.abs(direction)) <= EPS:
                        continue
                    candidate_id = f"triad_{q1_row['basename'][:18]}__{q3_top[i]['basename'][:14]}__{q3_top[j]['basename'][:14]}__w{w1:.2f}_{w3:.2f}"
                    path = write_candidate(base, base_logit, direction, candidate_id)
                    paths.append(path)
                    rows.append(
                        {
                            "candidate_id": candidate_id,
                            "file": rel(path),
                            "basename": path.name,
                            "recipe": "q1_q3_q3_microstate_triad",
                            "variant": "veto_centered",
                            "q1_source": q1_row["basename"],
                            "q3_source": q3_top[i]["basename"] + " || " + q3_top[j]["basename"],
                            "q1_weight": float(w1),
                            "q3_weight": float(w3),
                            "source_health_mean": float(np.mean([q1_row["action_health_score"], q3_top[i]["action_health_score"], q3_top[j]["action_health_score"]])),
                            "source_p90_dom_min": float(min(q1_row["actual_p90_dominance"], q3_top[i]["actual_p90_dominance"], q3_top[j]["actual_p90_dominance"])),
                            "source_null_rate_max": float(max(q1_row["null_strict_promote_rate"], q3_top[i]["null_strict_promote_rate"], q3_top[j]["null_strict_promote_rate"])),
                            "changed_rows": int(np.any(np.abs(direction) > EPS, axis=1).sum()),
                            "changed_cells": int((np.abs(direction) > EPS).sum()),
                            "mean_abs_logit_delta": float(np.mean(np.abs(direction))),
                            "max_abs_logit_delta": float(np.max(np.abs(direction))),
                            "l1_logit_delta": float(np.sum(np.abs(direction))),
                            "cos_with_e323_bad": cos(direction, e323_bad),
                            "cos_with_e216_bad": cos(direction, e216_bad),
                            **target_abs(direction),
                        }
                    )

    out = pd.DataFrame(rows).drop_duplicates("basename").sort_values(["recipe", "variant", "q1_weight", "q3_weight"]).reset_index(drop=True)
    paths = [locate(p) for p in out["file"]]
    paths = [p for p in paths if p is not None]
    out.to_csv(CANDIDATE_OUT, index=False)
    return out, paths, base_logit, e323_bad, e216_bad


def score_paths(paths: list[Path]) -> pd.DataFrame:
    if not paths:
        pd.DataFrame().to_csv(SCORE_OUT, index=False)
        return pd.DataFrame()
    sample = load_sub(OUT / CURRENT)[KEYS]
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    features = build_features([CURRENT] + [rel(p) for p in paths], sample, refs, ref_vecs)
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
                **target_abs(delta),
            }
        )
    out = pd.DataFrame(rows).sort_values(["cos_with_e323_bad", "l1_logit_delta"]).reset_index(drop=True)
    out.to_csv(ANATOMY_OUT, index=False)
    return out


def test_meta(base: pd.DataFrame) -> pd.DataFrame:
    _train, test, *_ = train_test_state()
    extra_cols = [c for c in ["subject_id", "dateblock_group"] if c not in KEYS]
    meta = test[KEYS + extra_cols].copy().reset_index(drop=True)
    key = base[KEYS].copy().reset_index(drop=True)
    for col in ["sleep_date", "lifelog_date"]:
        if col in key:
            key[col] = pd.to_datetime(key[col]).dt.strftime("%Y-%m-%d")
            meta[col] = pd.to_datetime(meta[col]).dt.strftime("%Y-%m-%d")
    aligned = key.merge(meta, on=KEYS, how="left", validate="one_to_one")
    if aligned[["subject_id", "dateblock_group"]].isna().any().any():
        raise RuntimeError("test metadata alignment failed")
    return aligned


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
                nd = null_delta(delta, mode, meta, stable_seed("null", rec["basename"], mode, rep))
                out = base.copy()
                out[TARGETS] = expit(np.clip(base_logit + np.clip(nd, -CAP, CAP), -40.0, 40.0))
                npth = NULL_DIR / f"submission_e340null_{safe_id(Path(rec['basename']).stem, 58)}_{mode}_r{rep}_{short_hash(out)}.csv"
                out.to_csv(npth, index=False)
                null_paths.append(npth)
                null_rows.append({"basename": rec["basename"], "null_basename": npth.name, "mode": mode, "rep": rep})
    if not null_paths:
        pd.DataFrame().to_csv(MOVE_NULL_OUT, index=False)
        return pd.DataFrame()
    sample = load_sub(OUT / CURRENT)[KEYS]
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    null_features = build_features([CURRENT] + [rel(p) for p in null_paths], sample, refs, ref_vecs)
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


def write_report(archive: pd.DataFrame, diag: pd.DataFrame, candidates: pd.DataFrame, scores: pd.DataFrame, anat: pd.DataFrame, nulls: pd.DataFrame) -> None:
    q1, q3 = source_pools(archive)
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
    score_view_cols = [
        "basename",
        "promotion_decision",
        "pred_delta_vs_current_mean",
        "pred_delta_vs_current_p10",
        "pred_delta_vs_current_p90",
        "pred_beats_current_rate",
        "incremental_bad_axis_vs_current",
    ]
    candidate_view_cols = [
        "basename",
        "recipe",
        "variant",
        "q1_weight",
        "q3_weight",
        "source_health_mean",
        "source_p90_dom_min",
        "source_null_rate_max",
        "cos_with_e323_bad",
        "cos_with_e216_bad",
        "share_Q1",
        "share_Q3",
    ]
    lines = [
        "# E340 Microstate Coalition Action-Health",
        "",
        "## Question",
        "",
        "Can individually safe-but-invisible hidden lifestyle micro-states become selector-visible when combined across targets, without collapsing into movement-null-common action?",
        "",
        "## Source Archive",
        "",
        f"- archive rows: `{len(archive)}`",
        f"- safe-invisible source rows: `{int(archive['safe_invisible_source'].sum())}`",
        f"- selected Q1 sources: `{len(q1)}`",
        f"- selected Q3 sources: `{len(q3)}`",
        "",
        "### Selected Q1 Sources",
        "",
        md_table(q1[["basename", "exp", "action_health_score", "pred_delta_vs_current_mean", "pred_delta_vs_current_p90", "actual_p90_dominance", "null_strict_promote_rate"]], n=12),
        "",
        "### Selected Q3 Sources",
        "",
        md_table(q3[["basename", "exp", "action_health_score", "pred_delta_vs_current_mean", "pred_delta_vs_current_p90", "actual_p90_dominance", "null_strict_promote_rate"]], n=18),
        "",
        "## Action-Health Latent Diagnostic",
        "",
        md_table(diag, n=20),
        "",
        "## Generated Coalition Candidates",
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
            )[score_view_cols]
            if len(non_current)
            else non_current,
            n=40,
        ),
        "",
        "### Candidate Anatomy",
        "",
        md_table(candidates[candidate_view_cols].sort_values(["source_p90_dom_min", "source_health_mean"], ascending=[False, False]) if len(candidates) else candidates, n=30),
        "",
        "## Movement-Null Stress",
        "",
        md_table(nulls, n=30),
        "",
        "## Decision",
        "",
    ]
    if len(null_safe):
        lines.append("At least one microstate coalition clears selector and fresh movement-null gates. Treat the top null-safe promoted file as a submission candidate after manual public-risk review.")
    elif len(promoted):
        lines.append("Microstate coalitions can cross selector visibility, but none survive fresh movement-null gates. Do not submit yet; the coalition is still shortcut-prone.")
    elif len(info):
        lines.append("Microstate coalitions remain information sensors only. The safe-invisible basin is not solved by combining Q1 and Q3 lifestyle states.")
    else:
        lines.append("No coalition candidate survives beyond below-resolution behavior. This strongly weakens the idea that multiple safe micro-states alone solve the visibility bottleneck.")
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- `{SOURCE_OUT.name}`",
            f"- `{LATENT_DIAG_OUT.name}`",
            f"- `{CANDIDATE_OUT.name}`",
            f"- `{SCORE_OUT.name}`",
            f"- `{ANATOMY_OUT.name}`",
            f"- `{MOVE_NULL_OUT.name}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    archive = build_archive()
    diag = action_health_latent_diagnostic(archive)
    base = load_current()
    base_logit, e323_bad, e216_bad = bad_axes(base)
    if CANDIDATE_OUT.exists() and SCORE_OUT.exists() and ANATOMY_OUT.exists():
        candidates = pd.read_csv(CANDIDATE_OUT)
        scores = pd.read_csv(SCORE_OUT)
        anat = pd.read_csv(ANATOMY_OUT)
    else:
        candidates, paths, base_logit, e323_bad, e216_bad = materialize_candidates(archive, base)
        scores = score_paths(paths)
        anat = anatomy(paths, base, base_logit, e323_bad, e216_bad)
    if MOVE_NULL_OUT.exists():
        nulls = pd.read_csv(MOVE_NULL_OUT)
    else:
        nulls = movement_null_stress(scores, candidates, base, base_logit)
    write_report(archive, diag, candidates, scores, anat, nulls)
    print(REPORT_OUT)
    if len(scores):
        non_current = scores[~scores["basename"].eq(CURRENT)].copy()
        cols = ["basename", "promotion_decision", "pred_delta_vs_current_mean", "pred_delta_vs_current_p90", "pred_beats_current_rate"]
        print(non_current[cols].head(40).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
