#!/usr/bin/env python3
"""H004: HS-JEPA sparse route materializer.

H003 validated the representation but rejected the first probability translator:
it moved every target on every test row and public LB got worse.  H004 keeps the
HS-JEPA latent and changes only the materialization rule.

The claim tested here is narrower:

    a human-state route should move only the target it locally explains,
    and only on a small set of rows where the route translator disagrees with
    the protected E247 body.

No public LB is used for selection.  H003's public miss is recorded as a design
constraint: broad all-target translators are disallowed.
"""

from __future__ import annotations

import hashlib
import sys
import warnings
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
HITL = ROOT / "hitl"
H004 = HITL / "h004_hsjepa_sparse_routes"
H004.mkdir(parents=True, exist_ok=True)

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

from e288_lifestyle_bundle_jepa_audit import (  # noqa: E402
    KEYS,
    TARGETS,
    base_label_matrix,
    clip_prob,
    folds_for,
    groups_for,
    label_cv_loss,
    md_table,
)
from e328_ownlatent_lifestyle_state_experiment import load_sub_frame, safe_id, sigmoid  # noqa: E402
from public_anchor_bottleneck_decomposition import load_sub as load_anchor_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402
from e272_public_free_candidate_audit import CURRENT, build_features, evaluate_models, score_candidates  # noqa: E402


RNG_SEED = 20260601 + 4
EPS = 1.0e-12
N_NULL_REPS = 5

H003 = HITL / "h003_hs_jepa_prototype"
H003_FEATURES = H003 / "h003_hs_jepa_features.parquet"
H003_ROUTE_STRESS = H003 / "h003_episode_target_route_stress.csv"
H003_TINY = H003 / "submission_h003_semantic_tiny_11e7aa3b.csv"

E247 = OUT / CURRENT

BUNDLE_OUT = H004 / "h004_bundle_stress.csv"
NULL_OUT = H004 / "h004_bundle_nulls.csv"
CANDIDATE_OUT = H004 / "h004_candidates.csv"
ROUTE_META_OUT = H004 / "h004_route_translator_meta.csv"
SCORE_OUT = H004 / "h004_selector_scores.csv"
ANATOMY_OUT = H004 / "h004_candidate_anatomy.csv"
GATE_OUT = H004 / "h004_gate_scores.csv"
SELECTION_OUT = H004 / "h004_selection.csv"
REPORT_OUT = H004 / "h004_report.md"


ROUTE_BUNDLES: list[dict[str, Any]] = [
    {
        "bundle": "s3_core",
        "target": "S3",
        "episodes": ["home_recovery", "bedtime_arousal", "social_overload"],
        "story": "recovery/arousal/social overload route into S3 only",
    },
    {
        "bundle": "s3_core_plus",
        "target": "S3",
        "episodes": ["home_recovery", "bedtime_arousal", "social_overload", "cashflow_stress", "routine_fragmentation"],
        "story": "broader S3 route including cashflow and routine fragmentation",
    },
    {
        "bundle": "q2_anchor_home",
        "target": "Q2",
        "episodes": ["routine_anchor_recovery", "home_recovery"],
        "story": "routine/home recovery route into Q2 only",
    },
    {
        "bundle": "q3_badnight",
        "target": "Q3",
        "episodes": ["badnight_aftereffect"],
        "story": "bad-night aftereffect route into Q3 only",
    },
    {
        "bundle": "s2_anchor_badnight",
        "target": "S2",
        "episodes": ["routine_anchor_recovery", "badnight_aftereffect"],
        "story": "routine anchor plus bad-night route into S2 only",
    },
    {
        "bundle": "s4_home_commute",
        "target": "S4",
        "episodes": ["home_recovery", "commute_pressure"],
        "story": "home recovery and commute pressure route into S4 only",
    },
    {
        "bundle": "s1_fragment_arousal",
        "target": "S1",
        "episodes": ["routine_fragmentation", "bedtime_arousal", "routine_anchor_recovery"],
        "story": "fragmentation/arousal route into S1 only",
    },
]


COMBO_SPECS: list[dict[str, Any]] = [
    {
        "candidate_id": "s3_core_top35",
        "routes": ["s3_core"],
        "top_k": 35,
        "weight": 0.020,
        "cap": 0.018,
        "row_mode": "confident_disagree",
    },
    {
        "candidate_id": "s3_core_top50",
        "routes": ["s3_core"],
        "top_k": 50,
        "weight": 0.018,
        "cap": 0.016,
        "row_mode": "confident_disagree",
    },
    {
        "candidate_id": "s3_coreplus_top35",
        "routes": ["s3_core_plus"],
        "top_k": 35,
        "weight": 0.018,
        "cap": 0.016,
        "row_mode": "confident_disagree",
    },
    {
        "candidate_id": "s3_core_tail25",
        "routes": ["s3_core"],
        "top_k": 25,
        "weight": 0.024,
        "cap": 0.018,
        "row_mode": "tail_disagree",
    },
    {
        "candidate_id": "q2_anchor_top30",
        "routes": ["q2_anchor_home"],
        "top_k": 30,
        "weight": 0.016,
        "cap": 0.014,
        "row_mode": "confident_disagree",
    },
    {
        "candidate_id": "q3_badnight_top25",
        "routes": ["q3_badnight"],
        "top_k": 25,
        "weight": 0.018,
        "cap": 0.014,
        "row_mode": "confident_disagree",
    },
    {
        "candidate_id": "s2_anchor_top30",
        "routes": ["s2_anchor_badnight"],
        "top_k": 30,
        "weight": 0.016,
        "cap": 0.014,
        "row_mode": "confident_disagree",
    },
    {
        "candidate_id": "s4_home_top30",
        "routes": ["s4_home_commute"],
        "top_k": 30,
        "weight": 0.016,
        "cap": 0.014,
        "row_mode": "confident_disagree",
    },
    {
        "candidate_id": "s3_q2_micro",
        "routes": ["s3_core", "q2_anchor_home"],
        "top_k": {"S3": 30, "Q2": 18},
        "weight": {"S3": 0.018, "Q2": 0.010},
        "cap": {"S3": 0.015, "Q2": 0.010},
        "row_mode": "confident_disagree",
    },
    {
        "candidate_id": "s3_q3_micro",
        "routes": ["s3_core", "q3_badnight"],
        "top_k": {"S3": 30, "Q3": 18},
        "weight": {"S3": 0.018, "Q3": 0.010},
        "cap": {"S3": 0.015, "Q3": 0.010},
        "row_mode": "confident_disagree",
    },
]


def rel(path: Path | None) -> str:
    if path is None:
        return "none"
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def short_hash(frame: pd.DataFrame) -> str:
    arr = np.asarray(frame[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def rank01(values: np.ndarray | pd.Series) -> np.ndarray:
    s = pd.Series(values, dtype="float64").replace([np.inf, -np.inf], np.nan).fillna(0.0)
    if s.nunique(dropna=False) <= 1:
        return np.full(len(s), 0.5, dtype=np.float64)
    return s.rank(method="average", pct=True).to_numpy(dtype=np.float64)


def target_value(spec_value: Any, target: str) -> float | int:
    if isinstance(spec_value, dict):
        return spec_value[target]
    return spec_value


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    if not H003_FEATURES.exists():
        raise FileNotFoundError(f"run H003 first: {H003_FEATURES}")
    if not H003_ROUTE_STRESS.exists():
        raise FileNotFoundError(f"run H003 first: {H003_ROUTE_STRESS}")
    features = pd.read_parquet(H003_FEATURES)
    routes = pd.read_csv(H003_ROUTE_STRESS)
    return features, routes


def available_cols(episodes: list[str], frame: pd.DataFrame) -> list[str]:
    cols = [f"hsjepa_pred_{episode}" for episode in episodes]
    return [col for col in cols if col in frame.columns]


def shuffled_additive(cols: pd.DataFrame, mode: str, frame: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    out = cols.copy().reset_index(drop=True)
    if mode == "row":
        perm = rng.permutation(len(out))
        return out.iloc[perm].reset_index(drop=True)
    if mode in {"subject", "dateblock"}:
        group_col = "subject_id" if mode == "subject" else "dateblock_group"
        pieces = []
        for _, idx in frame.reset_index().groupby(group_col)["index"]:
            vals = out.iloc[idx.to_numpy()].copy()
            perm = rng.permutation(len(vals))
            vals.iloc[:, :] = vals.iloc[perm].to_numpy()
            pieces.append(vals)
        return pd.concat(pieces).sort_index().reset_index(drop=True)
    raise ValueError(mode)


def bundle_matrix(frame: pd.DataFrame, bundle: dict[str, Any]) -> pd.DataFrame:
    cols = available_cols(list(bundle["episodes"]), frame)
    core = [col for col in ["hsjepa_surprise", "hsjepa_center_distance", "hsjepa_cluster_distance"] if col in frame.columns]
    x = pd.concat(
        [
            base_label_matrix(frame).reset_index(drop=True),
            frame[cols + core].astype(float).reset_index(drop=True),
        ],
        axis=1,
    )
    return x.replace([np.inf, -np.inf], 0.0).fillna(0.0)


def bundle_cv_loss(frame: pd.DataFrame, bundle: dict[str, Any], split_name: str) -> tuple[float, float]:
    train = frame[frame["split"].eq("train")].reset_index(drop=True)
    target = str(bundle["target"])
    groups = groups_for(train, split_name).reset_index(drop=True)
    base_x = base_label_matrix(train).reset_index(drop=True)
    x = bundle_matrix(train, bundle)
    y = train[target].to_numpy(dtype=int)
    base = label_cv_loss(base_x, y, groups)
    loss = label_cv_loss(x, y, groups)
    return base, loss


def bundle_stress(features: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    train = features[features["split"].eq("train")].reset_index(drop=True)
    base_x = base_label_matrix(train).reset_index(drop=True)
    rng = np.random.default_rng(RNG_SEED + 100)
    rows: list[dict[str, Any]] = []
    null_rows: list[dict[str, Any]] = []
    for bundle in ROUTE_BUNDLES:
        target = str(bundle["target"])
        cols = available_cols(list(bundle["episodes"]), train)
        if not cols:
            continue
        for split_name in ["subject5", "dateblock5"]:
            groups = groups_for(train, split_name).reset_index(drop=True)
            y = train[target].to_numpy(dtype=int)
            base_loss = label_cv_loss(base_x, y, groups)
            x = bundle_matrix(train, bundle)
            route_loss = label_cv_loss(x, y, groups)
            delta = route_loss - base_loss
            null_vals: list[float] = []
            mode_dom: dict[str, float] = {}
            route_cols = train[cols].astype(float).reset_index(drop=True)
            core_cols = [col for col in ["hsjepa_surprise", "hsjepa_center_distance", "hsjepa_cluster_distance"] if col in train.columns]
            for mode in ["row", "subject", "dateblock"]:
                vals = []
                for rep in range(N_NULL_REPS):
                    shuf = shuffled_additive(route_cols, mode, train, rng)
                    nx = pd.concat(
                        [
                            base_x,
                            shuf,
                            train[core_cols].astype(float).reset_index(drop=True),
                        ],
                        axis=1,
                    )
                    ndelta = label_cv_loss(nx, y, groups) - base_loss
                    vals.append(ndelta)
                    null_rows.append(
                        {
                            "bundle": bundle["bundle"],
                            "target": target,
                            "split": split_name,
                            "mode": mode,
                            "rep": rep,
                            "null_delta": ndelta,
                        }
                    )
                mode_dom[mode] = float(np.mean(delta < np.asarray(vals, dtype=np.float64)))
                null_vals.extend(vals)
            null_arr = np.asarray(null_vals, dtype=np.float64)
            rows.append(
                {
                    "bundle": bundle["bundle"],
                    "target": target,
                    "episodes": ",".join(bundle["episodes"]),
                    "story": bundle["story"],
                    "split": split_name,
                    "base_loss": base_loss,
                    "route_loss": route_loss,
                    "delta_logloss": delta,
                    "null_median": float(np.median(null_arr)),
                    "dominance": float(np.mean(delta < null_arr)),
                    "row_dominance": mode_dom["row"],
                    "subject_dominance": mode_dom["subject"],
                    "dateblock_dominance": mode_dom["dateblock"],
                    "bundle_gate": bool(delta < -0.0015 and float(np.mean(delta < null_arr)) >= 0.70 and min(mode_dom.values()) >= 0.40),
                }
            )
    return (
        pd.DataFrame(rows).sort_values(["bundle_gate", "delta_logloss"], ascending=[False, True]).reset_index(drop=True),
        pd.DataFrame(null_rows),
    )


def fit_route_predictor(features: pd.DataFrame, bundle: dict[str, Any]) -> tuple[np.ndarray, dict[str, Any]]:
    train = features[features["split"].eq("train")].reset_index(drop=True)
    test = features[features["split"].eq("test")].sort_values(KEYS).reset_index(drop=True)
    target = str(bundle["target"])
    y = train[target].to_numpy(dtype=int)
    x_train = bundle_matrix(train, bundle)
    x_test = bundle_matrix(test, bundle)
    model = make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(),
        LogisticRegression(C=0.12, max_iter=1800, solver="lbfgs"),
    )
    model.fit(x_train, y)
    pred = clip_prob(model.predict_proba(x_test)[:, 1])

    oof = np.zeros(len(train), dtype=np.float64)
    for tr_idx, va_idx in folds_for(groups_for(train, "subject5").reset_index(drop=True)):
        fold_y = y[tr_idx]
        if len(np.unique(fold_y)) < 2:
            oof[va_idx] = float(np.mean(fold_y))
            continue
        fold_model = make_pipeline(
            SimpleImputer(strategy="median"),
            StandardScaler(),
            LogisticRegression(C=0.12, max_iter=1800, solver="lbfgs"),
        )
        fold_model.fit(x_train.iloc[tr_idx], fold_y)
        oof[va_idx] = fold_model.predict_proba(x_train.iloc[va_idx])[:, 1]
    meta = {
        "bundle": bundle["bundle"],
        "target": target,
        "episodes": ",".join(bundle["episodes"]),
        "train_rate": float(np.mean(y)),
        "oof_subject5_loss": float(log_loss(y, clip_prob(oof), labels=[0, 1])),
        "test_pred_mean": float(np.mean(pred)),
        "test_pred_std": float(np.std(pred)),
    }
    return pred, meta


def select_rows(
    raw_move: np.ndarray,
    test: pd.DataFrame,
    top_k: int,
    mode: str,
) -> np.ndarray:
    disagree = rank01(np.abs(raw_move))
    stable = 1.0 - rank01(test["hsjepa_surprise"].to_numpy(dtype=np.float64))
    density = 1.0 - rank01(test["hsjepa_center_distance"].to_numpy(dtype=np.float64))
    if mode == "tail_disagree":
        score = 0.75 * disagree + 0.25 * rank01(test["hsjepa_surprise"].to_numpy(dtype=np.float64))
    elif mode == "confident_disagree":
        score = 0.70 * disagree + 0.20 * stable + 0.10 * density
    else:
        score = disagree
    top_k = int(min(max(top_k, 1), len(score)))
    cutoff = np.partition(score, len(score) - top_k)[len(score) - top_k]
    return score >= cutoff


def write_candidate(base: pd.DataFrame, logits: np.ndarray, candidate_id: str) -> Path:
    out = base[KEYS].copy()
    out[TARGETS] = clip_prob(sigmoid(logits))
    path = H004 / f"submission_h004_{safe_id(candidate_id, 90)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def materialize_candidates(features: pd.DataFrame, bundle_scores: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, list[Path]]:
    test = features[features["split"].eq("test")].sort_values(KEYS).reset_index(drop=True)
    base = load_sub_frame(E247, test[KEYS])
    base_prob = base[TARGETS].to_numpy(dtype=np.float64)
    base_logit = logit(base_prob)
    bundle_lookup = {str(b["bundle"]): b for b in ROUTE_BUNDLES}
    pred_cache: dict[str, np.ndarray] = {}
    meta_rows: list[dict[str, Any]] = []
    for bundle in ROUTE_BUNDLES:
        pred, meta = fit_route_predictor(features, bundle)
        pred_cache[str(bundle["bundle"])] = pred
        meta_rows.append(meta)

    rows: list[dict[str, Any]] = []
    paths: list[Path] = []
    for spec in COMBO_SPECS:
        logits = base_logit.copy()
        move = np.zeros_like(logits)
        route_notes = []
        for route_name in spec["routes"]:
            bundle = bundle_lookup[route_name]
            target = str(bundle["target"])
            target_idx = TARGETS.index(target)
            pred = pred_cache[route_name]
            raw_move = logit(pred) - base_logit[:, target_idx]
            top_k = int(target_value(spec["top_k"], target))
            weight = float(target_value(spec["weight"], target))
            cap = float(target_value(spec["cap"], target))
            row_mask = select_rows(raw_move, test, top_k, str(spec["row_mode"]))
            target_move = np.zeros(len(test), dtype=np.float64)
            target_move[row_mask] = np.clip(weight * raw_move[row_mask], -cap, cap)
            move[:, target_idx] += target_move
            logits[:, target_idx] += target_move
            route_notes.append(f"{route_name}:{target}:k{int(row_mask.sum())}:w{weight:g}:cap{cap:g}")
        path = write_candidate(base, logits, str(spec["candidate_id"]))
        paths.append(path)
        changed_by_target = {target: int((np.abs(move[:, idx]) > EPS).sum()) for idx, target in enumerate(TARGETS)}
        active_targets = [target for target, count in changed_by_target.items() if count > 0]
        route_bundle_delta = bundle_scores[bundle_scores["bundle"].isin(spec["routes"])].groupby("bundle")["delta_logloss"].min().to_dict()
        rows.append(
            {
                "candidate_id": spec["candidate_id"],
                "file": rel(path),
                "basename": path.name,
                "routes": ";".join(route_notes),
                "active_targets": ",".join(active_targets),
                "n_active_targets": len(active_targets),
                "changed_cells": int(np.sum(np.abs(move) > EPS)),
                "changed_rows": int(np.any(np.abs(move) > EPS, axis=1).sum()),
                "mean_abs_logit_move": float(np.mean(np.abs(move))),
                "max_abs_logit_move": float(np.max(np.abs(move))),
                "max_abs_prob_delta": float(np.max(np.abs(sigmoid(logits) - base_prob))),
                "best_bundle_delta": float(min(route_bundle_delta.values())) if route_bundle_delta else np.nan,
                **{f"changed_{target}": changed_by_target[target] for target in TARGETS},
            }
        )
    return pd.DataFrame(rows), pd.DataFrame(meta_rows), paths


def score_new_candidates(paths: list[Path]) -> pd.DataFrame:
    sample = load_anchor_sub(E247)[KEYS]
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    files = [CURRENT] + [rel(path) for path in paths]
    candidates = build_features(files, sample, refs, ref_vecs)
    scores = score_candidates(known, candidates, model_df)
    scores.to_csv(SCORE_OUT, index=False)
    return scores


def candidate_anatomy(paths: list[Path]) -> pd.DataFrame:
    sample = load_sub_frame(E247)[KEYS]
    base = load_sub_frame(E247, sample)
    base_prob = base[TARGETS].to_numpy(dtype=np.float64)
    base_logit = logit(base_prob)
    h003_bad = None
    if H003_TINY.exists():
        h003 = load_sub_frame(H003_TINY, sample)
        h003_bad = logit(h003[TARGETS].to_numpy(dtype=np.float64)) - base_logit
    rows = []
    for path in paths:
        cand = load_sub_frame(path, sample)
        pred = cand[TARGETS].to_numpy(dtype=np.float64)
        move = logit(pred) - base_logit
        rec: dict[str, Any] = {
            "basename": path.name,
            "changed_rows": int(np.any(np.abs(move) > EPS, axis=1).sum()),
            "changed_cells": int((np.abs(move) > EPS).sum()),
            "mean_abs_logit_delta": float(np.mean(np.abs(move))),
            "max_abs_prob_delta": float(np.max(np.abs(pred - base_prob))),
            "h003_alltarget_l1_ratio": float(np.sum(np.abs(move)) / (np.sum(np.abs(h003_bad)) + EPS)) if h003_bad is not None else np.nan,
            "h003_alltarget_cos": float(np.sum(move * h003_bad) / (np.linalg.norm(move) * np.linalg.norm(h003_bad) + EPS)) if h003_bad is not None else np.nan,
        }
        for idx, target in enumerate(TARGETS):
            rec[f"changed_{target}"] = int((np.abs(move[:, idx]) > EPS).sum())
            rec[f"l1_{target}"] = float(np.sum(np.abs(move[:, idx])))
        rows.append(rec)
    anatomy = pd.DataFrame(rows).sort_values(["changed_cells", "basename"]).reset_index(drop=True)
    anatomy.to_csv(ANATOMY_OUT, index=False)
    return anatomy


def choose_candidate(candidates: pd.DataFrame, scores: pd.DataFrame, anatomy: pd.DataFrame) -> pd.DataFrame:
    if scores.empty or "promotion_decision" not in scores.columns:
        selected = candidates.head(0).copy()
        return pd.DataFrame(
            [
                {
                    "decision": "selector_failed",
                    "selected_uploadsafe_file": "none",
                    "selected_basename": "none",
                    "reason": "public-free selector did not return candidate decisions",
                    "strict_promote_count": 0,
                    "info_sensor_count": 0,
                }
            ]
        )
    non_current = scores[~scores["basename"].eq(CURRENT)].copy()
    merged = (
        non_current.merge(candidates, on="basename", how="left", suffixes=("", "_candidate"))
        .merge(anatomy[["basename", "h003_alltarget_l1_ratio", "h003_alltarget_cos"]], on="basename", how="left")
    )
    merged["h004_shape_gate"] = (
        (merged["n_active_targets"] <= 2)
        & (merged["changed_cells"] <= 80)
        & (merged["h003_alltarget_l1_ratio"] <= 0.25)
        & (merged["incremental_bad_axis_vs_current"].abs() <= 0.025)
    )
    merged["h004_strict_gate"] = merged["strict_promote_gate"].astype(bool) & merged["h004_shape_gate"].astype(bool)
    merged["h004_info_gate"] = (
        ~merged["h004_strict_gate"].astype(bool)
        & merged["h004_shape_gate"].astype(bool)
        & (merged["pred_delta_vs_current_mean"] < 0.0)
        & (merged["pred_beats_current_rate"] >= 0.50)
    )
    merged.to_csv(GATE_OUT, index=False)
    ranked = merged.sort_values(
        ["h004_strict_gate", "h004_info_gate", "pred_delta_vs_current_p90", "pred_delta_vs_current_mean", "changed_cells"],
        ascending=[False, False, True, True, True],
    ).reset_index(drop=True)
    if ranked.empty:
        decision = "no_candidates"
        selected_file = "none"
        selected_basename = "none"
        reason = "no H004 candidate rows were generated"
    else:
        best = ranked.iloc[0]
        selected_basename = str(best["basename"])
        selected_path = H004 / selected_basename
        if bool(best["h004_strict_gate"]):
            uploadsafe = selected_path.with_name(selected_path.stem + "_uploadsafe.csv")
            if selected_path.exists():
                uploadsafe.write_bytes(selected_path.read_bytes())
            decision = "promote_h004_uploadsafe"
            selected_file = rel(uploadsafe) if uploadsafe.exists() else "none"
            reason = "strict public-free selector and H004 sparse-shape gates passed"
        elif bool(best["h004_info_gate"]):
            decision = "information_sensor_only"
            selected_file = "none"
            reason = "candidate is sparse and mean-favorable, but not strict enough for scarce public LB"
        else:
            decision = "diagnostic_only_no_h004_submission"
            selected_file = "none"
            reason = "no sparse route candidate cleared local selector gates"
    out = pd.DataFrame(
        [
            {
                "decision": decision,
                "selected_uploadsafe_file": selected_file,
                "selected_basename": selected_basename,
                "reason": reason,
                "strict_promote_count": int(merged["h004_strict_gate"].sum()) if not merged.empty else 0,
                "info_sensor_count": int(merged["h004_info_gate"].sum()) if not merged.empty else 0,
            }
        ]
    )
    out.to_csv(SELECTION_OUT, index=False)
    return out


def write_report(
    bundle_scores: pd.DataFrame,
    route_stress: pd.DataFrame,
    label_meta: pd.DataFrame,
    candidates: pd.DataFrame,
    scores: pd.DataFrame,
    anatomy: pd.DataFrame,
    selection: pd.DataFrame,
) -> None:
    non_current = scores[~scores["basename"].eq(CURRENT)].copy() if not scores.empty and "basename" in scores.columns else pd.DataFrame()
    score_cols = [
        "basename",
        "promotion_decision",
        "pred_delta_vs_current_mean",
        "pred_delta_vs_current_p10",
        "pred_delta_vs_current_p90",
        "pred_beats_current_rate",
        "incremental_bad_axis_vs_current",
    ]
    candidate_cols = [
        "candidate_id",
        "basename",
        "active_targets",
        "changed_cells",
        "changed_rows",
        "mean_abs_logit_move",
        "max_abs_logit_move",
        "max_abs_prob_delta",
        "best_bundle_delta",
    ]
    anatomy_cols = [
        "basename",
        "changed_rows",
        "changed_cells",
        "h003_alltarget_l1_ratio",
        "h003_alltarget_cos",
        "max_abs_prob_delta",
    ]
    route_cols = ["split", "episode", "target", "delta_logloss", "dominance", "route_gate"]
    bundle_cols = ["bundle", "target", "episodes", "split", "delta_logloss", "null_median", "dominance", "bundle_gate"]
    lines = [
        "# H004 HS-JEPA Sparse Routes",
        "",
        "## Question",
        "",
        "Can HS-JEPA become useful when the human-state latent is translated only through sparse episode-to-target routes, instead of the broad H003 all-target translator?",
        "",
        "## H003 Constraint",
        "",
        "- H003 semantic tiny public LB: `0.5763763885`.",
        "- E247 public best anchor: `0.5761589494`.",
        "- Observed delta: `+0.0002174391`, so broad all-target HS-JEPA materialization is rejected.",
        "- H004 therefore limits each candidate to at most two active targets and at most 80 changed cells.",
        "",
        "## H003 Route Evidence Used",
        "",
        md_table(route_stress[route_cols].head(25), n=25, floatfmt=".9f"),
        "",
        "## Bundle Stress",
        "",
        md_table(bundle_scores[bundle_cols], n=20, floatfmt=".9f"),
        "",
        "## Route Translator Meta",
        "",
        md_table(label_meta, n=20, floatfmt=".9f"),
        "",
        "## Candidate Materialization",
        "",
        md_table(candidates[candidate_cols], n=30, floatfmt=".9f"),
        "",
        "## Public-Free Selector Scores",
        "",
        md_table(non_current[score_cols] if not non_current.empty else non_current, n=30, floatfmt=".9f"),
        "",
        "## Anatomy",
        "",
        md_table(anatomy[anatomy_cols], n=30, floatfmt=".9f"),
        "",
        "## Selection",
        "",
        md_table(selection, n=5, floatfmt=".9f"),
        "",
        "## Decision",
        "",
    ]
    decision = str(selection.iloc[0]["decision"]) if len(selection) else "unknown"
    if decision == "promote_h004_uploadsafe":
        lines.append("One sparse HS-JEPA route candidate passed the strict H004 gate. This is a candidate for a scarce public LB submission.")
    elif decision == "information_sensor_only":
        lines.append("H004 produced an information-sensor candidate, but it is not strict enough to call a score candidate.")
    else:
        lines.append("H004 confirms the next shape of the idea, but no candidate should be submitted yet. Keep route signal, improve row/action translator.")
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- `{rel(BUNDLE_OUT)}`",
            f"- `{rel(NULL_OUT)}`",
            f"- `{rel(CANDIDATE_OUT)}`",
            f"- `{rel(ROUTE_META_OUT)}`",
            f"- `{rel(SCORE_OUT)}`",
            f"- `{rel(ANATOMY_OUT)}`",
            f"- `{rel(GATE_OUT)}`",
            f"- `{rel(SELECTION_OUT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    for stale in H004.glob("submission_h004_*.csv"):
        stale.unlink()
    features, route_stress = load_inputs()
    bundle_scores, nulls = bundle_stress(features)
    candidates, label_meta, paths = materialize_candidates(features, bundle_scores)
    scores = score_new_candidates(paths)
    anatomy = candidate_anatomy(paths)
    selection = choose_candidate(candidates, scores, anatomy)

    bundle_scores.to_csv(BUNDLE_OUT, index=False)
    nulls.to_csv(NULL_OUT, index=False)
    candidates.to_csv(CANDIDATE_OUT, index=False)
    label_meta.to_csv(ROUTE_META_OUT, index=False)
    selection.to_csv(SELECTION_OUT, index=False)
    write_report(bundle_scores, route_stress, label_meta, candidates, scores, anatomy, selection)

    print(f"report={rel(REPORT_OUT)}")
    print(selection.to_string(index=False))
    print("[bundle_stress]")
    print(bundle_scores[["bundle", "target", "split", "delta_logloss", "dominance", "bundle_gate"]].round(9).head(14).to_string(index=False))
    print("[candidates]")
    print(candidates[["candidate_id", "basename", "active_targets", "changed_cells", "max_abs_prob_delta"]].round(9).to_string(index=False))
    print("[selector_top]")
    non_current = scores[~scores["basename"].eq(CURRENT)].copy()
    print(non_current[["basename", "promotion_decision", "pred_delta_vs_current_mean", "pred_delta_vs_current_p90", "pred_beats_current_rate"]].round(9).head(12).to_string(index=False))


if __name__ == "__main__":
    main()
