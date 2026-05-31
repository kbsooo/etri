#!/usr/bin/env python3
"""E335: Q1 action-health latent generator.

E331-E334 established a split diagnosis:

    hidden Q1 lifestyle state: real
    scalar probability action: not healthy enough

This experiment changes the target.  Instead of asking whether Q1 label loss
improves, it learns a same-level "action-health" latent from previous Q1
candidate tensors:

    context  = candidate geometry + moved-row lifestyle signature
    target   = selector visibility + p90 safety + movement-null dominance

Then it uses the learned health rank to build small consensus/projection
variants from the safest Q1 near misses.  No public LB is used.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys
from typing import Any
import warnings

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold, LeaveOneGroupOut
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
NULL_DIR = OUT / "e335_q1_action_health_nulls"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e272_public_free_candidate_audit import CURRENT, build_features, evaluate_models, score_candidates  # noqa: E402
from e328_ownlatent_lifestyle_state_experiment import E247, E323, clip_prob, load_sub_frame, md_table, safe_id, sigmoid  # noqa: E402
from e332_q1_tail_translator_stress import build_q1_state  # noqa: E402
from public_anchor_bottleneck_decomposition import KEYS, TARGETS, load_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

RNG_SEED = 20260531 + 335
EPS = 1.0e-12
CAP = 0.42
MAX_SOURCE = 14
MAX_GENERATED = 96
MOVEMENT_NULL_REPS = 10

ARCHIVE_OUT = OUT / "e335_q1_action_health_archive.csv"
SIGNATURE_OUT = OUT / "e335_q1_action_health_signatures.csv"
CV_OUT = OUT / "e335_q1_action_health_cv.csv"
CANDIDATE_OUT = OUT / "e335_q1_action_health_candidates.csv"
SCORE_OUT = OUT / "e335_q1_action_health_candidate_scores.csv"
ANATOMY_OUT = OUT / "e335_q1_action_health_candidate_anatomy.csv"
MOVE_NULL_OUT = OUT / "e335_q1_action_health_movement_nulls.csv"
REPORT_OUT = OUT / "e335_q1_action_health_report.md"

EXPERIMENTS = [
    {
        "exp": "E332",
        "candidates": OUT / "e332_q1_tail_translator_candidates.csv",
        "scores": OUT / "e332_q1_tail_translator_candidate_scores.csv",
        "anatomy": OUT / "e332_q1_tail_translator_candidate_anatomy.csv",
        "movement": OUT / "e332_q1_tail_translator_movement_nulls.csv",
    },
    {
        "exp": "E333",
        "candidates": OUT / "e333_q1_contrastive_action_candidates.csv",
        "scores": OUT / "e333_q1_contrastive_action_candidate_scores.csv",
        "anatomy": OUT / "e333_q1_contrastive_action_candidate_anatomy.csv",
        "movement": OUT / "e333_q1_contrastive_action_movement_nulls.csv",
    },
    {
        "exp": "E334",
        "candidates": OUT / "e334_q1_tail_row_censor_candidates.csv",
        "scores": OUT / "e334_q1_tail_row_censor_candidate_scores.csv",
        "anatomy": OUT / "e334_q1_tail_row_censor_candidate_anatomy.csv",
        "movement": OUT / "e334_q1_tail_row_censor_movement_nulls.csv",
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


def locate(path_or_name: str) -> Path | None:
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


def short_hash(frame: pd.DataFrame) -> str:
    arr = np.asarray(frame[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def safe_spearman(a: np.ndarray | pd.Series, b: np.ndarray | pd.Series) -> float:
    x = pd.Series(a, dtype="float64")
    y = pd.Series(b, dtype="float64")
    mask = x.notna() & y.notna()
    if int(mask.sum()) < 4:
        return np.nan
    x = x[mask]
    y = y[mask]
    if x.nunique() < 2 or y.nunique() < 2:
        return np.nan
    val = spearmanr(x, y).correlation
    return float(val) if np.isfinite(val) else np.nan


def load_current() -> pd.DataFrame:
    return load_sub(OUT / CURRENT).sort_values(KEYS).reset_index(drop=True)


def candidate_delta(path: Path, current: pd.DataFrame) -> np.ndarray:
    cand = load_sub_frame(path, current[KEYS]).sort_values(KEYS).reset_index(drop=True)
    if not normalize_key_dates(cand[KEYS]).equals(normalize_key_dates(current[KEYS])):
        raise ValueError(f"key mismatch: {path}")
    return logit(cand[TARGETS].to_numpy(dtype=np.float64)) - logit(current[TARGETS].to_numpy(dtype=np.float64))


def normalize_key_dates(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in ["sleep_date", "lifelog_date"]:
        if col in out:
            out[col] = pd.to_datetime(out[col]).dt.strftime("%Y-%m-%d")
    return out


def test_meta_aligned(current: pd.DataFrame) -> pd.DataFrame:
    state = build_q1_state()
    meta = state["test"].copy()
    key_frame = normalize_key_dates(current[KEYS].copy())
    meta_norm = normalize_key_dates(meta)
    aligned = key_frame.merge(meta_norm, on=KEYS, how="left", validate="one_to_one")
    if aligned["subject_id"].isna().any() or aligned["dateblock_group"].isna().any():
        raise RuntimeError("E335 test metadata does not align with current")
    return aligned.reset_index(drop=True)


def compute_health(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    # Neutral movement-null defaults keep the full archive usable while making
    # candidates with real movement-null stress more informative.
    for col, default in [
        ("actual_mean_dominance", 0.50),
        ("actual_p90_dominance", 0.50),
        ("null_strict_promote_rate", 0.0),
    ]:
        if col not in out:
            out[col] = default
        out[col] = pd.to_numeric(out[col], errors="coerce").fillna(default)
    if "cos_with_e323_bad_delta" not in out:
        out["cos_with_e323_bad_delta"] = 0.0
    out["cos_with_e323_bad_delta"] = pd.to_numeric(out["cos_with_e323_bad_delta"], errors="coerce").fillna(0.0)
    out["incremental_bad_axis_vs_current"] = pd.to_numeric(out["incremental_bad_axis_vs_current"], errors="coerce").fillna(0.0)
    out["pred_delta_vs_current_mean"] = pd.to_numeric(out["pred_delta_vs_current_mean"], errors="coerce")
    out["pred_delta_vs_current_p90"] = pd.to_numeric(out["pred_delta_vs_current_p90"], errors="coerce")
    out["pred_beats_current_rate"] = pd.to_numeric(out["pred_beats_current_rate"], errors="coerce").fillna(0.0)

    def rank_good(values: pd.Series, ascending: bool = True) -> pd.Series:
        return values.rank(pct=True, ascending=ascending).fillna(0.5)

    out["rank_mean_gain"] = rank_good(out["pred_delta_vs_current_mean"], ascending=False)
    out["rank_p90_gain"] = rank_good(out["pred_delta_vs_current_p90"], ascending=False)
    out["rank_beats"] = rank_good(out["pred_beats_current_rate"], ascending=True)
    out["rank_null_mean"] = rank_good(out["actual_mean_dominance"], ascending=True)
    out["rank_null_p90"] = rank_good(out["actual_p90_dominance"], ascending=True)
    out["rank_bad_axis"] = rank_good(out["incremental_bad_axis_vs_current"].abs(), ascending=False)
    out["rank_e323_safe"] = rank_good(out["cos_with_e323_bad_delta"].clip(lower=0.0), ascending=False)
    penalty = (
        0.18 * (out["pred_delta_vs_current_p90"] > 0.0).astype(float)
        + 0.12 * (out["pred_delta_vs_current_mean"] > 0.0).astype(float)
        + 0.10 * (out["pred_beats_current_rate"] < 0.55).astype(float)
        + 0.10 * (out["actual_mean_dominance"] < 0.45).astype(float)
        + 0.10 * (out["actual_p90_dominance"] < 0.60).astype(float)
    )
    out["action_health_score"] = (
        0.23 * out["rank_p90_gain"]
        + 0.18 * out["rank_mean_gain"]
        + 0.14 * out["rank_beats"]
        + 0.19 * out["rank_null_p90"]
        + 0.12 * out["rank_null_mean"]
        + 0.08 * out["rank_bad_axis"]
        + 0.06 * out["rank_e323_safe"]
        - penalty
    )
    out["action_health_score"] = out["action_health_score"].clip(-1.0, 1.0)
    out["ready_proxy"] = (
        (out["pred_delta_vs_current_mean"] < 0.0)
        & (out["pred_delta_vs_current_p90"] < 0.00005)
        & (out["pred_beats_current_rate"] >= 0.65)
        & (out["actual_p90_dominance"] >= 0.65)
        & (out["cos_with_e323_bad_delta"] <= 0.05)
    )
    return out


def load_archive() -> pd.DataFrame:
    rows: list[pd.DataFrame] = []
    for cfg in EXPERIMENTS:
        cand = pd.read_csv(cfg["candidates"])
        scores = pd.read_csv(cfg["scores"])
        scores = scores[~scores["basename"].eq(CURRENT)].copy()
        anatomy = pd.read_csv(cfg["anatomy"]) if cfg["anatomy"].exists() else pd.DataFrame()
        movement = pd.read_csv(cfg["movement"]) if cfg["movement"].exists() else pd.DataFrame()
        merged = cand.merge(scores, on="basename", how="inner", suffixes=("_meta", ""))
        if len(anatomy):
            merged = merged.merge(anatomy, on="basename", how="left", suffixes=("", "_anat"))
        if len(movement):
            merged = merged.merge(movement, on="basename", how="left", suffixes=("", "_move"))
        merged["has_movement_null"] = merged.get("actual_p90_dominance", pd.Series(np.nan, index=merged.index)).notna()
        merged["exp"] = cfg["exp"]
        if "file_meta" in merged:
            merged["candidate_path"] = merged["file_meta"]
        elif "file" in merged:
            merged["candidate_path"] = merged["file"]
        else:
            merged["candidate_path"] = merged["source_path"]
        rows.append(merged)
    archive = pd.concat(rows, ignore_index=True, sort=False)
    archive = compute_health(archive)
    return archive


def weighted_stats(values: np.ndarray, weights: np.ndarray) -> tuple[float, float]:
    mask = np.isfinite(values) & np.isfinite(weights) & (np.abs(weights) > EPS)
    if int(mask.sum()) == 0:
        return np.nan, np.nan
    w = np.abs(weights[mask])
    x = values[mask]
    mean = float(np.average(x, weights=w))
    var = float(np.average((x - mean) ** 2, weights=w))
    return mean, float(np.sqrt(max(var, 0.0)))


def entropy_from_groups(keys: pd.Series, weights: np.ndarray) -> float:
    w = np.abs(np.asarray(weights, dtype=np.float64))
    if float(w.sum()) <= EPS:
        return 0.0
    df = pd.DataFrame({"key": keys.astype(str).to_numpy(), "w": w})
    p = df.groupby("key")["w"].sum().to_numpy(dtype=np.float64)
    p = p / max(float(p.sum()), EPS)
    return float(-(p * np.log(p + EPS)).sum() / np.log(max(len(p), 2)))


def candidate_signatures(archive: pd.DataFrame) -> pd.DataFrame:
    state = build_q1_state()
    current = load_current()
    test = test_meta_aligned(current)
    base_q1 = current["Q1"].to_numpy(dtype=np.float64)
    pred_map = normalize_key_dates(state["test"][KEYS].copy())
    pred_map["pred_test"] = np.asarray(state["pred_test"], dtype=np.float64)
    pred_test = normalize_key_dates(current[KEYS].copy()).merge(pred_map, on=KEYS, how="left", validate="one_to_one")["pred_test"].to_numpy(dtype=np.float64)

    preferred_cols = [
        "weekday",
        "is_weekend",
        "lifelog_dom",
        "lifelog_month",
        "social_comm_energy",
        "cognitive_money_energy",
        "media_game_energy",
        "bedtime_phone_energy",
        "mobility_context_energy",
        "physiology_activity_energy",
        "routine_calendar_energy",
        "sensor_measurement_energy",
        "diary_state_energy",
        "diary_state_pc1",
        "diary_state_pc2",
        "diary_state_pc3",
        "diary_state_pc4",
        "diary_state_pc5",
        "jepa_resid_dateblock_social_comm",
        "jepa_resid_dateblock_cognitive_money",
        "jepa_resid_dateblock_media_game",
        "jepa_resid_dateblock_bedtime_phone",
        "jepa_resid_dateblock_mobility_context",
        "jepa_resid_dateblock_physiology_activity",
        "jepa_resid_dateblock_routine_calendar",
        "jepa_resid_dateblock_sensor_measurement",
    ]
    numeric_cols = [c for c in preferred_cols if c in test.columns and pd.api.types.is_numeric_dtype(test[c])]

    rows: list[dict[str, Any]] = []
    for _, rec in archive.iterrows():
        path = locate(str(rec["candidate_path"]))
        if path is None:
            continue
        try:
            delta = candidate_delta(path, current)
        except Exception:
            continue
        q1 = delta[:, TARGETS.index("Q1")]
        weights = np.abs(q1)
        signed = q1.copy()
        changed = weights > EPS
        item: dict[str, Any] = {
            "basename": rec["basename"],
            "sig_q1_abs_sum": float(weights.sum()),
            "sig_q1_signed_sum": float(signed.sum()),
            "sig_q1_negative_share": float(np.mean(q1[changed] < 0.0)) if np.any(changed) else 0.0,
            "sig_q1_changed_rows": int(changed.sum()),
            "sig_q1_max_abs": float(weights.max()) if len(weights) else 0.0,
            "sig_subject_entropy": entropy_from_groups(test["subject_id"], q1),
            "sig_dateblock_entropy": entropy_from_groups(test["dateblock_group"], q1),
        }
        for name, arr in [("latent_pred", pred_test), ("base_q1", base_q1)]:
            mean, std = weighted_stats(np.asarray(arr, dtype=np.float64), q1)
            item[f"sig_{name}_wmean"] = mean
            item[f"sig_{name}_wstd"] = std
        for col in numeric_cols:
            mean, std = weighted_stats(pd.to_numeric(test[col], errors="coerce").to_numpy(dtype=np.float64), q1)
            item[f"sig_{col}_wmean"] = mean
            item[f"sig_{col}_wstd"] = std
        rows.append(item)
    sig = pd.DataFrame(rows)
    sig.to_csv(SIGNATURE_OUT, index=False)
    return sig


def feature_columns(df: pd.DataFrame) -> tuple[list[str], list[str]]:
    blocked = {
        "action_health_score",
        "ready_proxy",
        "basename",
        "file",
        "file_meta",
        "source_path",
        "candidate_path",
        "current_anchor",
        "promotion_decision",
        "strict_promote_gate",
        "info_sensor_gate",
        "below_resolution_gate",
        "block_gate",
        "actual_strict_promote",
    }
    numeric: list[str] = []
    for col in df.columns:
        if col in blocked:
            continue
        if col.startswith("rank_"):
            continue
        if pd.api.types.is_numeric_dtype(df[col]):
            numeric.append(col)
    cat = [c for c in ["exp", "target", "policy", "style", "family", "background", "rho_name", "mask_name"] if c in df.columns]
    return numeric, cat


def regressor(kind: str, numeric: list[str], cat: list[str]):
    transformers: list[tuple[str, Any, list[str]]] = []
    if numeric:
        transformers.append(("num", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), numeric))
    if cat:
        transformers.append(
            (
                "cat",
                make_pipeline(SimpleImputer(strategy="most_frequent"), OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
                cat,
            )
        )
    pre = ColumnTransformer(transformers, remainder="drop")
    if kind == "ridge":
        model = Ridge(alpha=8.0)
    elif kind == "trees":
        model = ExtraTreesRegressor(n_estimators=256, max_depth=5, min_samples_leaf=4, random_state=RNG_SEED)
    else:
        raise ValueError(kind)
    return make_pipeline(pre, model)


def evaluate_action_health_latent(archive: pd.DataFrame) -> pd.DataFrame:
    numeric, cat = feature_columns(archive)
    y = archive["action_health_score"].to_numpy(dtype=np.float64)
    rows: list[dict[str, Any]] = []

    def top_overlap(valid_idx: np.ndarray, pred_values: np.ndarray, true_values: np.ndarray) -> float:
        k = max(1, int(0.2 * len(valid_idx)))
        pred_top = set(np.asarray(valid_idx)[np.argsort(-pred_values)[:k]].tolist())
        true_top = set(np.asarray(valid_idx)[np.argsort(-true_values)[:k]].tolist())
        return float(len(pred_top.intersection(true_top)) / k)

    family = archive.get("family", pd.Series("unknown", index=archive.index)).astype("object").where(
        lambda s: s.notna(), "unknown"
    )
    for group_name, groups in [
        ("leave_experiment", archive["exp"].astype(str)),
        ("leave_family", archive["exp"].astype(str) + ":" + family.astype(str)),
    ]:
        groups = pd.Series(groups, index=archive.index).fillna("unknown").astype(str)
        unique = groups.nunique()
        if unique < 2:
            continue
        splitter = LeaveOneGroupOut() if unique <= 12 else GroupKFold(n_splits=min(6, unique))
        for kind in ["ridge", "trees"]:
            pred = np.full(len(archive), np.nan, dtype=np.float64)
            fold_rows = []
            for fold, (tr, va) in enumerate(splitter.split(archive, y, groups)):
                if len(np.unique(np.round(y[tr], 8))) < 2:
                    continue
                model = regressor(kind, numeric, cat)
                model.fit(archive.iloc[tr], y[tr])
                pred[va] = model.predict(archive.iloc[va])
                fold_rows.append(
                    {
                        "eval": group_name,
                        "model": kind,
                        "fold": fold,
                        "holdout": ",".join(sorted(set(groups.iloc[va].astype(str)))),
                        "n_train": int(len(tr)),
                        "n_valid": int(len(va)),
                        "spearman": safe_spearman(y[va], pred[va]),
                        "top20_overlap": top_overlap(np.asarray(va), pred[va], y[va]),
                    }
                )
            rows.extend(fold_rows)
            valid = np.where(np.isfinite(pred))[0]
            rows.append(
                {
                    "eval": group_name,
                    "model": kind,
                    "fold": -1,
                    "holdout": "ALL",
                    "n_train": int(len(valid)),
                    "n_valid": int(len(valid)),
                    "spearman": safe_spearman(y[valid], pred[valid]) if len(valid) else np.nan,
                    "top20_overlap": top_overlap(valid, pred[valid], y[valid]) if len(valid) else np.nan,
                }
            )
    cv = pd.DataFrame(rows)
    cv.to_csv(CV_OUT, index=False)
    return cv


def fit_health_model(archive: pd.DataFrame):
    numeric, cat = feature_columns(archive)
    model = regressor("trees", numeric, cat)
    model.fit(archive, archive["action_health_score"].to_numpy(dtype=np.float64))
    return model


def write_submission(current: pd.DataFrame, delta: np.ndarray, candidate_id: str) -> Path:
    out = current.copy()
    logits = logit(out[TARGETS].to_numpy(dtype=np.float64)) + np.clip(delta, -CAP, CAP)
    out[TARGETS] = clip_prob(sigmoid(logits))
    path = OUT / f"submission_e335_q1health_{safe_id(candidate_id)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def source_pool(archive: pd.DataFrame, current: pd.DataFrame) -> list[dict[str, Any]]:
    pool = archive.copy()
    pool = pool[
        pool["pred_delta_vs_current_mean"].lt(0.00005)
        & pool["pred_delta_vs_current_p90"].lt(0.00020)
        & pool["cos_with_e323_bad_delta"].fillna(0.0).le(0.08)
    ].copy()
    pool = pool.sort_values(["action_health_score", "pred_delta_vs_current_p90", "pred_delta_vs_current_mean"], ascending=[False, True, True])
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for _, rec in pool.iterrows():
        if len(out) >= MAX_SOURCE:
            break
        path = locate(str(rec["candidate_path"]))
        if path is None or path.name in seen:
            continue
        try:
            delta = candidate_delta(path, current)
        except Exception:
            continue
        if np.max(np.abs(delta)) <= EPS:
            continue
        seen.add(path.name)
        out.append({"rec": rec, "path": path, "delta": delta})
    return out


def project_out_bad(delta: np.ndarray, bad: np.ndarray, strength: float) -> np.ndarray:
    denom = float(np.sum(bad * bad))
    if denom <= EPS:
        return delta.copy()
    coef = float(np.sum(delta * bad) / denom)
    return delta - strength * coef * bad


def generate_candidates(archive: pd.DataFrame) -> tuple[pd.DataFrame, list[Path], pd.DataFrame]:
    current = load_current()
    e323 = load_sub_frame(E323, current[KEYS]).sort_values(KEYS).reset_index(drop=True)
    bad = logit(e323[TARGETS].to_numpy(dtype=np.float64)) - logit(current[TARGETS].to_numpy(dtype=np.float64))
    sources = source_pool(archive, current)
    rows: list[dict[str, Any]] = []
    paths: list[Path] = []
    generated: dict[str, np.ndarray] = {}

    def add(delta: np.ndarray, candidate_id: str, recipe: str, src_names: list[str], extra: dict[str, Any] | None = None) -> None:
        if len(rows) >= MAX_GENERATED:
            return
        if np.max(np.abs(delta)) <= EPS:
            return
        tmp = current.copy()
        tmp[TARGETS] = clip_prob(sigmoid(logit(tmp[TARGETS].to_numpy(dtype=np.float64)) + np.clip(delta, -CAP, CAP)))
        h = short_hash(tmp)
        if h in generated:
            return
        generated[h] = delta
        path = write_submission(current, delta, candidate_id)
        paths.append(path)
        rows.append(
            {
                "candidate_id": candidate_id,
                "file": rel(path),
                "basename": path.name,
                "recipe": recipe,
                "source_count": len(src_names),
                "source_basenames": ";".join(src_names[:8]),
                "changed_rows": int(np.any(np.abs(delta) > EPS, axis=1).sum()),
                "changed_cells": int((np.abs(delta) > EPS).sum()),
                "mean_abs_logit_move": float(np.mean(np.abs(delta))),
                "max_abs_logit_move": float(np.max(np.abs(delta))),
                "q1_abs_sum": float(np.abs(delta[:, TARGETS.index("Q1")]).sum()),
                "q_abs_share": float(np.abs(delta[:, :3]).sum() / max(float(np.abs(delta).sum()), EPS)),
                "s_abs_share": float(np.abs(delta[:, 3:]).sum() / max(float(np.abs(delta).sum()), EPS)),
                **(extra or {}),
            }
        )

    if not sources:
        pd.DataFrame(rows).to_csv(CANDIDATE_OUT, index=False)
        return pd.DataFrame(rows), paths, current

    weights = np.asarray([max(float(s["rec"]["action_health_score"]), 0.02) for s in sources], dtype=np.float64)
    weights = weights / max(float(weights.sum()), EPS)
    deltas = np.stack([s["delta"] for s in sources], axis=0)
    names = [Path(str(s["path"])).name for s in sources]

    for topk in [2, 3, 5, 8, min(len(sources), MAX_SOURCE)]:
        if topk < 2:
            continue
        w = weights[:topk] / max(float(weights[:topk].sum()), EPS)
        avg = np.tensordot(w, deltas[:topk], axes=(0, 0))
        for scale in [0.45, 0.65, 0.85, 1.05]:
            add(scale * avg, f"weightedavg_top{topk}_s{scale:.2f}", "weighted_average", names[:topk], {"topk": topk, "scale": scale, "bad_project": 0.0})
            add(project_out_bad(scale * avg, bad, 0.75), f"weightedavg_top{topk}_badproj075_s{scale:.2f}", "weighted_average_badproj", names[:topk], {"topk": topk, "scale": scale, "bad_project": 0.75})

    q1_idx = TARGETS.index("Q1")
    signed_q1 = deltas[:, :, q1_idx]
    sign_agree = np.mean(signed_q1 < 0.0, axis=0)
    q1_weighted = np.tensordot(weights, signed_q1, axes=(0, 0))
    q1_abs = np.abs(q1_weighted)
    for agree_cut in [0.55, 0.70, 0.85]:
        for q in [0.45, 0.60, 0.75, 0.88]:
            threshold = float(np.quantile(q1_abs, q))
            row_mask = (q1_abs >= threshold) & (sign_agree >= agree_cut)
            if int(row_mask.sum()) < 3:
                continue
            base = np.zeros_like(deltas[0])
            base[row_mask, q1_idx] = q1_weighted[row_mask]
            for scale in [0.60, 0.85, 1.10, 1.35]:
                add(scale * base, f"rowconsensus_a{agree_cut:.2f}_q{q:.2f}_s{scale:.2f}", "row_consensus", names, {"agree_cut": agree_cut, "row_q": q, "scale": scale, "rows": int(row_mask.sum())})

    # Tail-only anti-risk: keep rows where the weighted action is negative but
    # not an extreme single-source spike. This targets p90 safety over mean.
    dispersion = np.std(signed_q1, axis=0)
    for disp_q in [0.50, 0.65, 0.80]:
        disp_thr = float(np.quantile(dispersion, disp_q))
        row_mask = (q1_weighted < 0.0) & (dispersion <= disp_thr) & (q1_abs >= np.quantile(q1_abs, 0.50))
        if int(row_mask.sum()) < 3:
            continue
        base = np.zeros_like(deltas[0])
        base[row_mask, q1_idx] = q1_weighted[row_mask]
        for scale in [0.75, 1.00, 1.25]:
            add(scale * base, f"lowdisp_consensus_dq{disp_q:.2f}_s{scale:.2f}", "lowdisp_consensus", names, {"disp_q": disp_q, "scale": scale, "rows": int(row_mask.sum())})

    out = pd.DataFrame(rows)
    out.to_csv(CANDIDATE_OUT, index=False)
    return out, paths, current


def score_generated(paths: list[Path]) -> pd.DataFrame:
    if not paths:
        pd.DataFrame().to_csv(SCORE_OUT, index=False)
        return pd.DataFrame()
    sample = load_sub(E247)[KEYS]
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    files = [CURRENT] + [rel(path) for path in paths]
    candidates = build_features(files, sample, refs, ref_vecs)
    scores = score_candidates(known, candidates, model_df)
    scores.to_csv(SCORE_OUT, index=False)
    return scores


def candidate_anatomy(paths: list[Path], current: pd.DataFrame) -> pd.DataFrame:
    if not paths:
        pd.DataFrame().to_csv(ANATOMY_OUT, index=False)
        return pd.DataFrame()
    current_logits = logit(current[TARGETS].to_numpy(dtype=np.float64))
    e323 = load_sub_frame(E323, current[KEYS]).sort_values(KEYS).reset_index(drop=True)
    bad = logit(e323[TARGETS].to_numpy(dtype=np.float64)) - current_logits
    rows = []
    for path in paths:
        cand = load_sub_frame(path, current[KEYS]).sort_values(KEYS).reset_index(drop=True)
        move = logit(cand[TARGETS].to_numpy(dtype=np.float64)) - current_logits
        rows.append(
            {
                "basename": path.name,
                "changed_rows": int(np.any(np.abs(move) > EPS, axis=1).sum()),
                "changed_cells": int((np.abs(move) > EPS).sum()),
                "mean_abs_logit_delta": float(np.mean(np.abs(move))),
                "max_abs_prob_delta": float(np.max(np.abs(cand[TARGETS].to_numpy(dtype=np.float64) - current[TARGETS].to_numpy(dtype=np.float64)))),
                "cos_with_e323_bad_delta": float(np.sum(move * bad) / (np.linalg.norm(move) * np.linalg.norm(bad) + EPS)),
                "l1_ratio_to_e323_delta": float(np.sum(np.abs(move)) / (np.sum(np.abs(bad)) + EPS)),
            }
        )
    out = pd.DataFrame(rows).sort_values(["cos_with_e323_bad_delta", "l1_ratio_to_e323_delta"]).reset_index(drop=True)
    out.to_csv(ANATOMY_OUT, index=False)
    return out


def aligned_test_meta(current: pd.DataFrame) -> pd.DataFrame:
    return test_meta_aligned(current)[KEYS + ["dateblock_group"]].copy()


def write_movement_null(path: Path, current: pd.DataFrame, meta: pd.DataFrame, mode: str, rep: int) -> Path:
    rng = np.random.default_rng(stable_seed("move_null", path.name, mode, rep))
    current_logits = logit(current[TARGETS].to_numpy(dtype=np.float64))
    delta = candidate_delta(path, current)
    shuffled = np.zeros_like(delta)
    if mode == "row":
        shuffled = delta[rng.permutation(len(delta))]
    elif mode == "subject":
        for _, idx in meta.groupby("subject_id").indices.items():
            idx_arr = np.asarray(idx, dtype=int)
            shuffled[idx_arr] = delta[idx_arr][rng.permutation(len(idx_arr))]
    elif mode == "dateblock":
        for _, idx in meta.groupby("dateblock_group").indices.items():
            idx_arr = np.asarray(idx, dtype=int)
            shuffled[idx_arr] = delta[idx_arr][rng.permutation(len(idx_arr))]
    else:
        raise ValueError(mode)
    out = current.copy()
    out[TARGETS] = clip_prob(sigmoid(current_logits + shuffled))
    NULL_DIR.mkdir(exist_ok=True)
    npath = NULL_DIR / f"submission_e335null_{path.stem.replace('submission_', '')[:82]}_{mode}_r{rep}_{short_hash(out)}.csv"
    out.to_csv(npath, index=False)
    return npath


def movement_null_stress(paths: list[Path], current: pd.DataFrame, scores: pd.DataFrame) -> pd.DataFrame:
    if not paths or scores.empty:
        pd.DataFrame().to_csv(MOVE_NULL_OUT, index=False)
        return pd.DataFrame()
    non_current = scores[~scores["basename"].eq(CURRENT)].copy()
    chosen = non_current.sort_values(
        ["strict_promote_gate", "info_sensor_gate", "pred_delta_vs_current_p90", "pred_delta_vs_current_mean"],
        ascending=[False, False, True, True],
    ).head(20)
    path_by_name = {p.name: p for p in paths}
    meta = aligned_test_meta(current)
    null_paths: list[Path] = []
    null_map: list[dict[str, Any]] = []
    for _, rec in chosen.iterrows():
        path = path_by_name.get(str(rec["basename"]))
        if path is None:
            continue
        for mode in ["row", "subject", "dateblock"]:
            for rep in range(MOVEMENT_NULL_REPS):
                npath = write_movement_null(path, current, meta, mode, rep)
                null_paths.append(npath)
                null_map.append({"basename": path.name, "null_basename": npath.name, "mode": mode, "rep": rep})
    if not null_paths:
        pd.DataFrame().to_csv(MOVE_NULL_OUT, index=False)
        return pd.DataFrame()
    sample = load_sub(E247)[KEYS]
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    null_candidates = build_features([CURRENT] + [rel(p) for p in null_paths], sample, refs, ref_vecs)
    null_scores = score_candidates(known, null_candidates, model_df)
    cols = ["basename", "pred_delta_vs_current_mean", "pred_delta_vs_current_p90", "pred_beats_current_rate", "strict_promote_gate"]
    map_df = pd.DataFrame(null_map).merge(null_scores[cols].rename(columns={"basename": "null_basename"}), on="null_basename", how="left")
    actual = non_current[cols].rename(
        columns={
            "pred_delta_vs_current_mean": "actual_mean",
            "pred_delta_vs_current_p90": "actual_p90",
            "pred_beats_current_rate": "actual_beats_rate",
            "strict_promote_gate": "actual_strict_promote",
        }
    )
    rows = []
    for basename, part in map_df.groupby("basename"):
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
            }
        )
    out = pd.DataFrame(rows).sort_values(["actual_strict_promote", "actual_p90_dominance", "actual_p90"], ascending=[False, False, True]).reset_index(drop=True)
    out.to_csv(MOVE_NULL_OUT, index=False)
    return out


def write_report(archive: pd.DataFrame, cv: pd.DataFrame, candidates: pd.DataFrame, scores: pd.DataFrame, anatomy: pd.DataFrame, move_null: pd.DataFrame) -> None:
    non_current = scores[~scores["basename"].eq(CURRENT)].copy() if len(scores) else pd.DataFrame()
    scored = non_current.merge(candidates, on="basename", how="left") if len(non_current) and len(candidates) else pd.DataFrame()
    promoted = scored[scored["strict_promote_gate"].astype(bool)] if len(scored) else pd.DataFrame()
    e323_safe_names = set(anatomy[anatomy["cos_with_e323_bad_delta"] <= 0.05]["basename"]) if len(anatomy) else set()
    safe_promoted = promoted[promoted["basename"].isin(e323_safe_names)] if len(promoted) else pd.DataFrame()
    move_safe = pd.DataFrame()
    if len(safe_promoted) and len(move_null):
        move_safe = safe_promoted.merge(move_null, on="basename", how="inner")
        move_safe = move_safe[
            (move_safe["actual_p90_dominance"] >= 0.80)
            & (move_safe["actual_mean_dominance"] >= 0.65)
            & (move_safe["null_strict_promote_rate"] <= 0.10)
        ]

    cv_all = cv[cv["holdout"].eq("ALL")].copy() if len(cv) else pd.DataFrame()
    lines = [
        "# E335 Q1 Action-Health Latent Generator",
        "",
        "## Question",
        "",
        "Can the missing Q1 object be learned as an action-health latent rather than another label-loss latent?",
        "",
        "## Archive",
        "",
        f"- archive rows: `{len(archive)}`",
        f"- ready proxy rows: `{int(archive['ready_proxy'].sum())}`",
        f"- movement-null-labelled rows: `{int(archive.get('has_movement_null', pd.Series(False, index=archive.index)).sum())}`",
        "",
        md_table(
            archive.sort_values(["action_health_score", "pred_delta_vs_current_p90"], ascending=[False, True])[
                [
                    "exp",
                    "basename",
                    "action_health_score",
                    "pred_delta_vs_current_mean",
                    "pred_delta_vs_current_p90",
                    "pred_beats_current_rate",
                    "actual_mean_dominance",
                    "actual_p90_dominance",
                    "cos_with_e323_bad_delta",
                    "promotion_decision",
                ]
            ],
            n=30,
            floatfmt=".9f",
        ),
        "",
        "## Action-Health Predictability",
        "",
        md_table(cv_all, n=20, floatfmt=".6f") if len(cv_all) else "_no CV rows_",
        "",
        "## Generated Candidates",
        "",
        md_table(candidates, n=40, floatfmt=".9f") if len(candidates) else "_none_",
        "",
        "## Public-Free Selector Scores",
        "",
    ]
    if len(scored):
        lines.append(
            md_table(
                scored[
                    [
                        "basename",
                        "recipe",
                        "source_count",
                        "pred_delta_vs_current_mean",
                        "pred_delta_vs_current_p10",
                        "pred_delta_vs_current_p90",
                        "pred_beats_current_rate",
                        "incremental_bad_axis_vs_current",
                        "promotion_decision",
                    ]
                ],
                n=50,
                floatfmt=".9f",
            )
        )
    else:
        lines.append("_no candidates_")
    lines.extend(["", "## E323 Anatomy", "", md_table(anatomy, n=40, floatfmt=".9f") if len(anatomy) else "_none_"])
    lines.extend(["", "## Movement-Null Stress", "", md_table(move_null, n=40, floatfmt=".9f") if len(move_null) else "_none_"])
    lines.extend(["", "## Decision", ""])
    if len(move_safe):
        best = move_safe.sort_values(["actual_p90", "actual_mean"]).iloc[0]
        lines.append(
            f"`{best['basename']}` clears selector, E323-negative, and movement-null gates. This is the next submission candidate."
        )
    else:
        lines.append(
            "No generated file clears selector + E323 + movement-null gates. E335 therefore supports the bottleneck diagnosis: Q1 hidden lifestyle state is detectable, but the current archive does not contain enough action-health information to make a public-grade tensor."
        )
    lines.extend(
        [
            "",
            f"- generated candidates: `{len(candidates)}`",
            f"- selector-promoted candidates: `{int(non_current['strict_promote_gate'].sum()) if len(non_current) else 0}`",
            f"- selector+E323-safe candidates: `{len(safe_promoted)}`",
            f"- selector+E323+movement-null-safe candidates: `{len(move_safe)}`",
            "",
            "## Files",
            "",
            f"- `{ARCHIVE_OUT.name}`",
            f"- `{SIGNATURE_OUT.name}`",
            f"- `{CV_OUT.name}`",
            f"- `{CANDIDATE_OUT.name}`",
            f"- `{SCORE_OUT.name}`",
            f"- `{ANATOMY_OUT.name}`",
            f"- `{MOVE_NULL_OUT.name}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    archive = load_archive()
    sig = candidate_signatures(archive)
    archive = archive.merge(sig, on="basename", how="left")
    archive.to_csv(ARCHIVE_OUT, index=False)
    cv = evaluate_action_health_latent(archive)
    candidates, paths, current = generate_candidates(archive)
    scores = score_generated(paths)
    anatomy = candidate_anatomy(paths, current)
    move_null = movement_null_stress(paths, current, scores)
    write_report(archive, cv, candidates, scores, anatomy, move_null)
    print(REPORT_OUT)
    if len(cv):
        print(cv[cv["holdout"].eq("ALL")].round(6).to_string(index=False))
    if len(scores):
        view = scores[~scores["basename"].eq(CURRENT)]
        print(view[["basename", "promotion_decision", "pred_delta_vs_current_mean", "pred_delta_vs_current_p90", "pred_beats_current_rate"]].head(30).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
