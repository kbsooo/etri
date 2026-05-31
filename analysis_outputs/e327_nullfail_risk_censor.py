#!/usr/bin/env python3
"""E327: null-fail risk censor for E323/E324 residual candidates.

E326 showed that human/social semantic axes are useful diagnostics but do not
replace the E324 priority action.  This experiment asks a sharper action-layer
question:

    What part of an E323 residual candidate is still easy for row/subject/
    dateblock null placements to imitate, and can we remove that part while
    keeping selector-visible edge?

Build nulls and stress nulls are separated.  The risk model is learned only
from build nulls; promotion is judged on fresh stress nulls.

No public LB is used.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
import sys
import warnings

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
BUILD_NULL_DIR = OUT / "e327_nullfail_risk_censor_build_nulls"
STRESS_NULL_DIR = OUT / "e327_nullfail_risk_censor_stress_nulls"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e272_public_free_candidate_audit import CURRENT, evaluate_models, score_candidates  # noqa: E402
from e288_lifestyle_bundle_jepa_audit import TARGETS, clip_prob, load_frames  # noqa: E402
from e289_target_specific_lifestyle_slice_audit import safe_id  # noqa: E402
from e297_episode_state_materializer import align_meta_to_current, feature_rows, sigmoid  # noqa: E402
from e315_human_ready_composition_materializer import cap_delta, md  # noqa: E402
from e321_mode_adversarial_action_health import PROMOTION_THRESHOLDS  # noqa: E402
from e323_null_common_residual_generator import current_frame, load_delta, null_delta, short_hash  # noqa: E402
from public_anchor_bottleneck_decomposition import KEYS, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

E324_GOVERNOR = OUT / "e324_e323_ready_highrep_governor_audit.csv"

CANDIDATE_OUT = OUT / "e327_nullfail_risk_censor_candidate_audit.csv"
PREFILTER_OUT = OUT / "e327_nullfail_risk_censor_prefilter_audit.csv"
SELECTED_OUT = OUT / "e327_nullfail_risk_censor_selected_audit.csv"
GOVERNOR_OUT = OUT / "e327_nullfail_risk_censor_governor_audit.csv"
SUMMARY_OUT = OUT / "e327_nullfail_risk_censor_summary.csv"
REPORT_OUT = OUT / "e327_nullfail_risk_censor_report.md"
BUILD_NULL_MAP_OUT = OUT / "e327_nullfail_risk_censor_build_null_map.csv"
STRESS_NULL_MAP_OUT = OUT / "e327_nullfail_risk_censor_stress_null_map.csv"
BUILD_SCORE_OUT = OUT / "e327_nullfail_risk_censor_build_scores.csv"
STRESS_SCORE_OUT = OUT / "e327_nullfail_risk_censor_stress_scores.csv"

PLACEMENT_MODES = ["row", "subject", "dateblock"]
ALL_NULL_MODES = ["row", "subject", "dateblock", "target_perm", "sign_flip", "q_s_swap"]
BUILD_REPS = 32
STRESS_PLACEMENT_REPS = 48
STRESS_TARGET_REPS = 48
STRESS_REP_OFFSET = 1000
MAX_CANDIDATES = 540
MAX_NULL_EVAL = 40
CAP = 0.35
EPS = 1.0e-12


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def load_ready() -> pd.DataFrame:
    gov = pd.read_csv(E324_GOVERNOR)
    ready = gov[gov["highrep_public_free_submission_ready"].astype(bool)].copy()
    return ready.sort_values(
        ["highrep_null_strict_rate", "highrep_actual_p90", "highrep_mean_dominance"],
        ascending=[True, True, False],
    ).reset_index(drop=True)


def test_meta(current: pd.DataFrame) -> pd.DataFrame:
    base, _, _, _ = load_frames()
    test_df = base.loc[base["split"].eq("test")].reset_index(drop=True)
    return align_meta_to_current(test_df, current)


def describe_delta(delta: np.ndarray, prefix: str = "") -> dict[str, Any]:
    abs_by_target = np.abs(delta).sum(axis=0)
    total = float(abs_by_target.sum())
    out: dict[str, Any] = {
        f"{prefix}nonzero_rows": int(np.any(np.abs(delta) > EPS, axis=1).sum()),
        f"{prefix}nonzero_cells": int(np.sum(np.abs(delta) > EPS)),
        f"{prefix}mean_abs_delta": float(np.mean(np.abs(delta))),
        f"{prefix}max_abs_delta": float(np.max(np.abs(delta))),
        f"{prefix}l1_delta": total,
        f"{prefix}q_abs_share": float(abs_by_target[:3].sum() / max(total, EPS)),
        f"{prefix}s_abs_share": float(abs_by_target[3:].sum() / max(total, EPS)),
    }
    for i, target in enumerate(TARGETS):
        out[f"{prefix}abs_{target}"] = float(abs_by_target[i])
    return out


def write_submission(current: pd.DataFrame, delta: np.ndarray, candidate_id: str) -> Path:
    out = current.copy()
    logits = logit(out[TARGETS].to_numpy(dtype=np.float64)) + cap_delta(delta, CAP)
    out[TARGETS] = clip_prob(sigmoid(logits))
    path = OUT / f"submission_e327_nullrisk_{safe_id(candidate_id)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def write_null(
    current: pd.DataFrame,
    delta: np.ndarray,
    basename: str,
    mode: str,
    rep: int,
    meta: pd.DataFrame,
    null_dir: Path,
    tag: str,
) -> Path:
    out = current.copy()
    nd = cap_delta(null_delta(delta, mode, rep, meta, basename), CAP)
    logits = logit(out[TARGETS].to_numpy(dtype=np.float64)) + nd
    out[TARGETS] = clip_prob(sigmoid(logits))
    null_dir.mkdir(exist_ok=True)
    safe_name = basename[:72].replace("/", "_")
    path = null_dir / f"submission_e327{tag}_{safe_name}_{mode}_r{rep}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def score_paths(paths: list[Path], current: pd.DataFrame) -> pd.DataFrame:
    sample = current[KEYS].copy()
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    features = feature_rows([OUT / CURRENT, *paths], sample, refs, ref_vecs)
    return score_candidates(known, features, model_df).drop_duplicates("basename")


def build_risk_reference(
    parent_base: str,
    parent_delta: np.ndarray,
    current: pd.DataFrame,
    meta: pd.DataFrame,
) -> tuple[dict[str, Any], pd.DataFrame, dict[str, np.ndarray], pd.DataFrame]:
    rows: list[dict[str, Any]] = []
    null_deltas: dict[str, np.ndarray] = {}
    null_paths: list[Path] = []
    for mode in PLACEMENT_MODES:
        for rep in range(BUILD_REPS):
            nd = null_delta(parent_delta, mode, rep, meta, parent_base)
            path = write_null(current, parent_delta, parent_base, mode, rep, meta, BUILD_NULL_DIR, "build")
            null_deltas[path.name] = nd
            null_paths.append(path)
            rows.append(
                {
                    "source_basename": parent_base,
                    "null_basename": path.name,
                    "null_path": rel(path),
                    "mode": mode,
                    "rep": rep,
                }
            )
    null_map = pd.DataFrame(rows)
    scores = score_paths([OUT / parent_base, *null_paths], current)
    scores.to_csv(BUILD_SCORE_OUT, mode="a", index=False, header=not BUILD_SCORE_OUT.exists())

    parent_score = scores[scores["basename"].eq(parent_base)].iloc[0]
    null_scores = scores[scores["basename"].isin(null_map["null_basename"])].merge(
        null_map[["null_basename", "mode", "rep"]],
        left_on="basename",
        right_on="null_basename",
        how="inner",
    )
    p90 = null_scores["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64)
    q25 = float(np.quantile(p90, 0.25)) if len(p90) else 0.0
    bad_mask = null_scores["strict_promote_gate"].astype(bool).to_numpy() | (p90 <= q25)
    if int(bad_mask.sum()) < min(16, len(null_scores)):
        order = np.argsort(p90)[: min(16, len(null_scores))]
        bad_mask = np.zeros(len(null_scores), dtype=bool)
        bad_mask[order] = True
    bad_names = null_scores.loc[bad_mask, "basename"].astype(str).tolist()
    all_stack = np.stack([null_deltas[name] for name in null_scores["basename"].astype(str)], axis=0)
    bad_stack = np.stack([null_deltas[name] for name in bad_names], axis=0) if bad_names else all_stack

    bad_mean = bad_stack.mean(axis=0)
    bad_abs_mean = np.mean(np.abs(bad_stack), axis=0)
    bad_abs_q75 = np.quantile(np.abs(bad_stack), 0.75, axis=0)
    sign_match = np.mean((np.sign(bad_stack) == np.sign(parent_delta)[None, :, :]) & (np.abs(bad_stack) > EPS), axis=0)
    risk = sign_match * np.minimum(2.0, bad_abs_mean / (np.abs(parent_delta) + EPS))
    support = np.abs(parent_delta) - bad_abs_q75
    active = np.abs(parent_delta) > EPS
    ref = {
        "parent_actual_mean": float(parent_score["pred_delta_vs_current_mean"]),
        "parent_actual_p90": float(parent_score["pred_delta_vs_current_p90"]),
        "parent_strict_promote": bool(parent_score["strict_promote_gate"]),
        "build_null_count": int(len(null_scores)),
        "build_bad_null_count": int(len(bad_names)),
        "build_bad_strict_count": int(null_scores.loc[bad_mask, "strict_promote_gate"].astype(bool).sum()),
        "build_bad_p90_threshold": q25,
        "build_bad_null_mean_p90": float(null_scores.loc[bad_mask, "pred_delta_vs_current_p90"].mean()),
        "risk_mean_active": float(np.mean(risk[active])) if np.any(active) else 0.0,
        "risk_p90_active": float(np.quantile(risk[active], 0.90)) if np.any(active) else 0.0,
        "support_mean_active": float(np.mean(support[active])) if np.any(active) else 0.0,
        "support_p10_active": float(np.quantile(support[active], 0.10)) if np.any(active) else 0.0,
        "bad_mean_l1_ratio": float(np.abs(bad_mean).sum() / max(np.abs(parent_delta).sum(), EPS)),
    }
    arrays = {
        "bad_mean": bad_mean,
        "risk": risk,
        "support": support,
        "bad_abs_q75": bad_abs_q75,
    }
    return ref, null_map, arrays, null_scores


def project_out(delta: np.ndarray, basis: np.ndarray, strength: float) -> np.ndarray:
    denom = float(np.sum(basis * basis))
    if denom < EPS:
        return delta.copy()
    coef = float(np.sum(delta * basis) / denom)
    return delta - strength * coef * basis


def target_l1_rescale(out: np.ndarray, original: np.ndarray, max_scale: float) -> np.ndarray:
    scaled = out.copy()
    for j in range(len(TARGETS)):
        before = float(np.abs(original[:, j]).sum())
        after = float(np.abs(scaled[:, j]).sum())
        if before > EPS and after > EPS:
            scaled[:, j] *= min(max_scale, before / after)
    return scaled


def active_quantile(values: np.ndarray, active: np.ndarray, q: float) -> float:
    vals = values[active]
    return float(np.quantile(vals, q)) if len(vals) else np.inf


def transform_delta(
    parent_delta: np.ndarray,
    arrays: dict[str, np.ndarray],
    policy: str,
    q: float,
    strength: float,
    scale: float,
) -> tuple[np.ndarray, dict[str, Any]]:
    active = np.abs(parent_delta) > EPS
    bad_mean = arrays["bad_mean"]
    risk = arrays["risk"]
    support = arrays["support"]
    high_risk = active & (risk >= active_quantile(risk, active, q))
    low_risk = active & (risk <= active_quantile(risk, active, 1.0 - q))
    high_support = active & (support >= active_quantile(support, active, q))

    if policy == "badmean_subtract":
        out = parent_delta - strength * bad_mean
    elif policy == "badmean_subtract_keep_l1":
        out = parent_delta - strength * bad_mean
        out = np.where(high_support, out, 0.0)
        out = target_l1_rescale(out, parent_delta, 1.50)
    elif policy == "support_keep":
        out = np.where(high_support, parent_delta, 0.0)
    elif policy == "support_keep_l1":
        out = np.where(high_support, parent_delta, 0.0)
        out = target_l1_rescale(out, parent_delta, 1.50)
    elif policy == "risk_damp25":
        out = np.where(high_risk, 0.25 * parent_delta, parent_delta)
    elif policy == "risk_damp50":
        out = np.where(high_risk, 0.50 * parent_delta, parent_delta)
    elif policy == "risk_drop":
        out = np.where(high_risk, 0.0, parent_delta)
    elif policy == "risk_low_keep_l1":
        out = np.where(low_risk, parent_delta, 0.0)
        out = target_l1_rescale(out, parent_delta, 1.50)
    elif policy == "orth_badmean":
        out = project_out(parent_delta, bad_mean, strength)
    elif policy == "anti_highrisk_keep":
        out = np.where(high_risk, parent_delta, 0.0)
    elif policy == "anti_badmean_add":
        out = parent_delta + strength * bad_mean
    else:
        raise ValueError(policy)

    out = cap_delta(out * scale, CAP)
    kept = np.abs(out) > EPS
    before_l1 = float(np.abs(parent_delta).sum())
    after_l1 = float(np.abs(out).sum())
    metrics = {
        "risk_policy": policy,
        "risk_q": q,
        "risk_strength": strength,
        "risk_scale": scale,
        "risk_type": "anti_control" if policy.startswith("anti") else "nullfail_censor",
        "risk_active_cells": int(active.sum()),
        "risk_high_cells": int(high_risk.sum()),
        "risk_kept_cells": int(kept.sum()),
        "risk_kept_frac": float(kept.sum() / max(active.sum(), 1)),
        "risk_l1_retained_frac": after_l1 / max(before_l1, EPS),
        "risk_mean_kept": float(np.mean(risk[kept])) if np.any(kept) else 0.0,
        "risk_mean_dropped": float(np.mean(risk[active & ~kept])) if np.any(active & ~kept) else 0.0,
        "support_mean_kept": float(np.mean(support[kept])) if np.any(kept) else 0.0,
        "support_mean_dropped": float(np.mean(support[active & ~kept])) if np.any(active & ~kept) else 0.0,
    }
    return out, metrics


def generate_candidates(current: pd.DataFrame, ready: pd.DataFrame, meta: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, np.ndarray], pd.DataFrame, pd.DataFrame]:
    BUILD_SCORE_OUT.unlink(missing_ok=True)
    rows: list[dict[str, Any]] = []
    delta_map: dict[str, np.ndarray] = {}
    all_null_maps: list[pd.DataFrame] = []
    all_null_scores: list[pd.DataFrame] = []
    policies = [
        "badmean_subtract",
        "badmean_subtract_keep_l1",
        "support_keep",
        "support_keep_l1",
        "risk_damp25",
        "risk_damp50",
        "risk_drop",
        "risk_low_keep_l1",
        "orth_badmean",
        "anti_highrisk_keep",
        "anti_badmean_add",
    ]
    qs = [0.55, 0.65, 0.75, 0.85]
    strengths = [0.50, 1.00, 1.50]
    scales = [0.75, 1.00, 1.25]

    for _, parent in ready.iterrows():
        parent_base = str(parent["basename"])
        parent_delta = load_delta(OUT / parent_base, current)
        ref, null_map, arrays, null_scores = build_risk_reference(parent_base, parent_delta, current, meta)
        all_null_maps.append(null_map)
        all_null_scores.append(null_scores)
        for policy in policies:
            policy_strengths = strengths if policy in {"badmean_subtract", "badmean_subtract_keep_l1", "orth_badmean", "anti_badmean_add"} else [1.0]
            for q in qs:
                for strength in policy_strengths:
                    for scale in scales:
                        delta, metrics = transform_delta(parent_delta, arrays, policy, q, strength, scale)
                        if np.max(np.abs(delta)) < EPS:
                            continue
                        candidate_id = (
                            f"{parent_base.replace('submission_e323_healthresid_', '')[:54]}"
                            f"__{policy}__q{q:.2f}__b{strength:.2f}__s{scale:.2f}"
                        )
                        path = write_submission(current, delta, candidate_id)
                        basename = path.name
                        if basename in delta_map:
                            continue
                        delta_map[basename] = delta
                        rows.append(
                            {
                                "basename": basename,
                                "source_path": rel(path),
                                "parent_basename": parent_base,
                                "parent_source_path": parent.get("source_path", ""),
                                "parent_highrep_actual_mean": float(parent.get("highrep_actual_mean", np.nan)),
                                "parent_highrep_actual_p90": float(parent.get("highrep_actual_p90", np.nan)),
                                "parent_highrep_null_strict_rate": float(parent.get("highrep_null_strict_rate", np.nan)),
                                "parent_highrep_p90_dominance": float(parent.get("highrep_p90_dominance", np.nan)),
                                "parent_highrep_mean_dominance": float(parent.get("highrep_mean_dominance", np.nan)),
                                "parent_highrep_worst_mode_p90_dominance": float(parent.get("highrep_worst_mode_p90_dominance", np.nan)),
                                **ref,
                                **metrics,
                                **describe_delta(delta),
                            }
                        )
                        if len(rows) >= MAX_CANDIDATES:
                            break
                    if len(rows) >= MAX_CANDIDATES:
                        break
                if len(rows) >= MAX_CANDIDATES:
                    break
            if len(rows) >= MAX_CANDIDATES:
                break
    null_map_df = pd.concat(all_null_maps, ignore_index=True) if all_null_maps else pd.DataFrame()
    null_scores_df = pd.concat(all_null_scores, ignore_index=True) if all_null_scores else pd.DataFrame()
    return pd.DataFrame(rows), delta_map, null_map_df, null_scores_df


def score_prefilter(candidate_meta: pd.DataFrame, current: pd.DataFrame) -> pd.DataFrame:
    if candidate_meta.empty:
        return candidate_meta
    paths = [OUT / str(b) for b in candidate_meta["basename"]]
    scores = score_paths(paths, current)
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
        [
            "strict_promote_gate",
            "info_sensor_gate",
            "risk_type",
            "pred_delta_vs_current_p90",
            "pred_delta_vs_current_mean",
        ],
        ascending=[False, False, False, True, True],
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
    censor_best = (
        prefilter[prefilter["risk_type"].eq("nullfail_censor")]
        .sort_values(["pred_delta_vs_current_p90", "pred_delta_vs_current_mean"])
        .groupby(["parent_basename", "risk_policy"], as_index=False)
        .head(1)
    )
    anti_best = (
        prefilter[prefilter["risk_type"].eq("anti_control")]
        .sort_values(["pred_delta_vs_current_p90", "pred_delta_vs_current_mean"])
        .groupby(["parent_basename", "risk_policy"], as_index=False)
        .head(1)
    )
    selected = pd.concat(
        [
            strict.sort_values(["pred_delta_vs_current_p90", "pred_delta_vs_current_mean"]).head(18),
            info.sort_values(["pred_delta_vs_current_p90", "pred_delta_vs_current_mean"]).head(8),
            censor_best.head(20),
            anti_best.head(8),
        ],
        ignore_index=True,
    )
    if selected.empty:
        selected = prefilter.sort_values(["pred_delta_vs_current_p90", "pred_delta_vs_current_mean"]).head(MAX_NULL_EVAL)
    return (
        selected.drop_duplicates("basename")
        .sort_values(["strict_promote_gate", "pred_delta_vs_current_p90", "pred_delta_vs_current_mean"], ascending=[False, True, True])
        .head(MAX_NULL_EVAL)
        .reset_index(drop=True)
    )


def build_stress_nulls(selected: pd.DataFrame, delta_map: dict[str, np.ndarray], current: pd.DataFrame, meta: pd.DataFrame) -> tuple[pd.DataFrame, list[Path]]:
    rows: list[dict[str, Any]] = []
    paths: list[Path] = []
    for _, cand in selected.iterrows():
        basename = str(cand["basename"])
        delta = delta_map[basename]
        for mode in ALL_NULL_MODES:
            if mode in {"row", "subject", "dateblock"}:
                reps = STRESS_PLACEMENT_REPS
            elif mode == "target_perm":
                reps = STRESS_TARGET_REPS
            else:
                reps = 1
            for rep0 in range(reps):
                rep = rep0 + STRESS_REP_OFFSET
                path = write_null(current, delta, basename, mode, rep, meta, STRESS_NULL_DIR, "stress")
                paths.append(path)
                rows.append(
                    {
                        "source_basename": basename,
                        "null_basename": path.name,
                        "null_path": rel(path),
                        "mode": mode,
                        "rep": rep,
                    }
                )
    return pd.DataFrame(rows), paths


def run_governor(
    selected: pd.DataFrame,
    delta_map: dict[str, np.ndarray],
    current: pd.DataFrame,
    meta: pd.DataFrame,
    e324_priority: pd.Series,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if selected.empty:
        empty = pd.DataFrame()
        empty.to_csv(STRESS_NULL_MAP_OUT, index=False)
        empty.to_csv(GOVERNOR_OUT, index=False)
        return empty, empty

    null_map, null_paths = build_stress_nulls(selected, delta_map, current, meta)
    scores = score_paths([*(OUT / b for b in selected["basename"]), *null_paths], current)
    scores.to_csv(STRESS_SCORE_OUT, index=False)

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
            null_map[null_map["source_basename"].eq(basename)][["null_basename", "mode", "rep"]],
            left_on="basename",
            right_on="null_basename",
            how="inner",
        )
        actual_p90 = float(a["pred_delta_vs_current_p90"])
        actual_mean = float(a["pred_delta_vs_current_mean"])
        old_strict = bool(a["strict_promote_gate"])
        p90_vals = these_null["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64)
        mean_vals = these_null["pred_delta_vs_current_mean"].to_numpy(dtype=np.float64)
        null_strict_rate = float(these_null["strict_promote_gate"].astype(bool).mean()) if len(these_null) else 1.0
        p90_dominance = float(np.mean(actual_p90 < p90_vals)) if len(p90_vals) else 0.0
        mean_dominance = float(np.mean(actual_mean < mean_vals)) if len(mean_vals) else 0.0
        mode_doms: dict[str, float] = {}
        mode_strict: dict[str, float] = {}
        mode_counts: dict[str, int] = {}
        for mode, part in these_null.groupby("mode"):
            vals = part["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64)
            mode_doms[f"{mode}_p90_dominance"] = float(np.mean(actual_p90 < vals))
            mode_strict[f"{mode}_null_strict_rate"] = float(part["strict_promote_gate"].astype(bool).mean())
            mode_counts[f"{mode}_count"] = int(len(part))
        worst_mode = float(min(mode_doms.values())) if mode_doms else 0.0
        ready = bool(
            old_strict
            and actual_p90 <= -2.0e-5
            and null_strict_rate <= PROMOTION_THRESHOLDS["null_strict_rate"]
            and p90_dominance >= PROMOTION_THRESHOLDS["p90_dominance"]
            and mean_dominance >= PROMOTION_THRESHOLDS["mean_dominance"]
            and worst_mode >= PROMOTION_THRESHOLDS["worst_mode_p90_dominance"]
        )
        beats_e324_priority = bool(
            ready
            and actual_p90 <= float(e324_priority["highrep_actual_p90"])
            and null_strict_rate <= float(e324_priority["highrep_null_strict_rate"])
            and p90_dominance >= float(e324_priority["highrep_p90_dominance"]) - 0.02
            and mean_dominance >= float(e324_priority["highrep_mean_dominance"]) - 0.02
            and worst_mode >= float(e324_priority["highrep_worst_mode_p90_dominance"])
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
                **mode_strict,
                **mode_counts,
                "public_free_submission_ready": ready,
                "beats_e324_priority_local": beats_e324_priority,
                "final_decision": "public_free_submission_ready" if ready else ("blocked_by_e327_nulls" if old_strict else str(a.get("promotion_decision", "hold"))),
            }
        )
    governor = pd.DataFrame(rows)
    if not governor.empty:
        governor = governor.sort_values(
            [
                "beats_e324_priority_local",
                "public_free_submission_ready",
                "risk_type",
                "null_strict_rate",
                "actual_p90",
                "mean_dominance",
            ],
            ascending=[False, False, False, True, True, False],
        ).reset_index(drop=True)
    null_map.to_csv(STRESS_NULL_MAP_OUT, index=False)
    governor.to_csv(GOVERNOR_OUT, index=False)
    return governor, null_map


def write_report(
    candidate_meta: pd.DataFrame,
    prefilter: pd.DataFrame,
    selected: pd.DataFrame,
    governor: pd.DataFrame,
    build_null_map: pd.DataFrame,
    stress_null_map: pd.DataFrame,
    e324_priority: pd.Series,
) -> None:
    strict = prefilter[prefilter["strict_promote_gate"].astype(bool)] if not prefilter.empty else pd.DataFrame()
    ready = governor[governor["public_free_submission_ready"].astype(bool)] if not governor.empty else pd.DataFrame()
    stronger = governor[governor["beats_e324_priority_local"].astype(bool)] if not governor.empty else pd.DataFrame()
    by_type = (
        governor.groupby("risk_type", dropna=False)
        .agg(
            rows=("basename", "count"),
            ready=("public_free_submission_ready", "sum"),
            best_p90=("actual_p90", "min"),
            best_null_strict=("null_strict_rate", "min"),
            best_worst_mode=("worst_mode_p90_dominance", "max"),
        )
        .reset_index()
        if not governor.empty
        else pd.DataFrame()
    )
    summary = pd.DataFrame(
        [
            {
                "slice": "e327_nullfail_risk_censor",
                "generated": int(len(candidate_meta)),
                "prefilter_strict": int(len(strict)),
                "null_evaluated": int(len(selected)),
                "build_null_rows": int(len(build_null_map)),
                "stress_null_rows": int(len(stress_null_map)),
                "ready": int(len(ready)),
                "beats_e324_priority_local": int(len(stronger)),
                "best_p90": float(governor["actual_p90"].min()) if not governor.empty else np.nan,
                "best_null_strict": float(governor["null_strict_rate"].min()) if not governor.empty else np.nan,
                "best_worst_mode": float(governor["worst_mode_p90_dominance"].max()) if not governor.empty else np.nan,
                "e324_priority_basename": str(e324_priority["basename"]),
                "e324_priority_p90": float(e324_priority["highrep_actual_p90"]),
                "e324_priority_null_strict": float(e324_priority["highrep_null_strict_rate"]),
                "e324_priority_worst_mode": float(e324_priority["highrep_worst_mode_p90_dominance"]),
            }
        ]
    )
    summary.to_csv(SUMMARY_OUT, index=False)

    pre_cols = [
        "basename",
        "risk_type",
        "risk_policy",
        "risk_q",
        "risk_strength",
        "risk_scale",
        "risk_l1_retained_frac",
        "risk_mean_kept",
        "support_mean_kept",
        "promotion_decision",
        "pred_delta_vs_current_mean",
        "pred_delta_vs_current_p90",
        "strict_promote_gate",
    ]
    gov_cols = [
        "basename",
        "risk_type",
        "risk_policy",
        "risk_q",
        "risk_strength",
        "risk_scale",
        "risk_l1_retained_frac",
        "risk_mean_kept",
        "actual_mean",
        "actual_p90",
        "null_strict_rate",
        "p90_dominance",
        "mean_dominance",
        "worst_mode_p90_dominance",
        "public_free_submission_ready",
        "beats_e324_priority_local",
        "final_decision",
    ]
    lines = [
        "# E327 Null-Fail Risk Censor",
        "",
        "Public LB was not used.",
        "",
        "## Question",
        "",
        "Can the remaining E324 risk be reduced by learning which cells are favored by competitive row/subject/dateblock null placements, then censoring that null-fail signature on fresh nulls?",
        "",
        "## Summary",
        "",
        md(summary, n=5),
        "",
        "## Censor vs Anti-Control",
        "",
        md(by_type, n=10),
        "",
        "## Prefilter Top Rows",
        "",
        md(prefilter[[c for c in pre_cols if c in prefilter.columns]], n=30) if not prefilter.empty else "_empty_",
        "",
        "## Fresh Stress Governor",
        "",
        md(governor[[c for c in gov_cols if c in governor.columns]], n=60) if not governor.empty else "_empty_",
        "",
        "## Decision",
        "",
    ]
    if len(stronger):
        top = stronger.iloc[0]
        lines.append(
            f"- `{top['basename']}` beats the E324 priority locally under fresh nulls. Treat it as the new public-free priority only after one independent recheck because E327 still uses the known-public selector family."
        )
    elif len(ready):
        top = ready.iloc[0]
        lines.append(
            f"- `{top['basename']}` is public-free ready, but it does not dominate the existing E324 priority. Keep E324 priority order unchanged."
        )
    else:
        lines.append(
            "- No null-fail risk-censored variant is public-free ready. E324 priority remains the only current stress-surviving candidate."
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- This is a stricter follow-up to E326: the gate is not a human story but the nulls that the local selector itself finds dangerous.",
            "- Build nulls and stress nulls are separated so the censor cannot simply memorize the exact null placements used for judgment.",
            "- A replacement candidate must beat the current E324 priority, not merely be old-selector strict.",
            "",
            "## Outputs",
            "",
            f"- `{CANDIDATE_OUT.relative_to(ROOT)}`",
            f"- `{PREFILTER_OUT.relative_to(ROOT)}`",
            f"- `{SELECTED_OUT.relative_to(ROOT)}`",
            f"- `{GOVERNOR_OUT.relative_to(ROOT)}`",
            f"- `{SUMMARY_OUT.relative_to(ROOT)}`",
            f"- `{REPORT_OUT.relative_to(ROOT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    current = current_frame()
    ready = load_ready()
    if ready.empty:
        empty = pd.DataFrame()
        for path in [CANDIDATE_OUT, PREFILTER_OUT, SELECTED_OUT, GOVERNOR_OUT, SUMMARY_OUT, BUILD_NULL_MAP_OUT, STRESS_NULL_MAP_OUT]:
            empty.to_csv(path, index=False)
        REPORT_OUT.write_text("# E327 Null-Fail Risk Censor\n\nNo E324 ready candidates found.\n", encoding="utf-8")
        print(f"report={REPORT_OUT.relative_to(ROOT)}")
        return

    meta = test_meta(current)
    candidate_meta, delta_map, build_null_map, build_null_scores = generate_candidates(current, ready, meta)
    candidate_meta.to_csv(CANDIDATE_OUT, index=False)
    build_null_map.to_csv(BUILD_NULL_MAP_OUT, index=False)
    build_null_scores.to_csv(BUILD_SCORE_OUT, index=False)

    prefilter = score_prefilter(candidate_meta, current)
    prefilter.to_csv(PREFILTER_OUT, index=False)
    selected = select_for_null(prefilter)
    selected.to_csv(SELECTED_OUT, index=False)

    e324_priority = ready.iloc[0]
    governor, stress_null_map = run_governor(selected, delta_map, current, meta, e324_priority)
    write_report(candidate_meta, prefilter, selected, governor, build_null_map, stress_null_map, e324_priority)

    print(f"generated={len(candidate_meta)}")
    print(f"strict_prefilter={int(prefilter['strict_promote_gate'].sum()) if not prefilter.empty else 0}")
    print(f"selected={len(selected)}")
    print(f"build_null_rows={len(build_null_map)}")
    print(f"stress_null_rows={len(stress_null_map)}")
    print(f"ready={int(governor['public_free_submission_ready'].sum()) if not governor.empty else 0}")
    print(f"beats_e324_priority={int(governor['beats_e324_priority_local'].sum()) if not governor.empty else 0}")
    if not governor.empty:
        top = governor.iloc[0]
        print(f"top={top['basename']}")
        print(f"top_p90={float(top['actual_p90']):.9f}")
        print(f"top_null_strict={float(top['null_strict_rate']):.6f}")
        print(f"top_worst_mode={float(top['worst_mode_p90_dominance']):.6f}")
    print(f"report={REPORT_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
