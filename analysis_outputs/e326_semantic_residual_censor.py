#!/usr/bin/env python3
"""E326: semantic residual censor for E323 ready candidates.

E325 showed that the E323 residual actions are not semantically random:
their touched cells align with human/social story axes such as night-out
mobility, phone-in-bed, bedtime arousal, and social-isolation media.

This script asks the next falsifiable question:

    If those semantic axes are useful rather than merely explanatory, can they
    censor or damp the E323 residual action and improve public-free health?

It creates semantic and anti-semantic variants, scores them with the existing
public-free selector, then stress-tests selected files against row, subject,
dateblock, target-permutation, sign-flip, and Q/S-swap nulls.

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
NULL_DIR = OUT / "e326_semantic_residual_censor_nulls"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e272_public_free_candidate_audit import CURRENT, evaluate_models, score_candidates  # noqa: E402
from e288_lifestyle_bundle_jepa_audit import TARGETS, clip_prob  # noqa: E402
from e289_target_specific_lifestyle_slice_audit import safe_id  # noqa: E402
from e297_episode_state_materializer import align_meta_to_current, feature_rows, sigmoid  # noqa: E402
from e315_human_ready_composition_materializer import cap_delta, md  # noqa: E402
from e321_mode_adversarial_action_health import PROMOTION_THRESHOLDS  # noqa: E402
from e323_null_common_residual_generator import current_frame, load_delta, null_delta, short_hash  # noqa: E402
from e325_e323_semantic_null_attribution import build_semantic_matrix  # noqa: E402
from public_anchor_bottleneck_decomposition import KEYS, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

E324_GOVERNOR = OUT / "e324_e323_ready_highrep_governor_audit.csv"
E325_ATTR = OUT / "e325_e323_semantic_null_attribution.csv"

CANDIDATE_OUT = OUT / "e326_semantic_residual_censor_candidate_audit.csv"
SELECTED_OUT = OUT / "e326_semantic_residual_censor_selected_audit.csv"
GOVERNOR_OUT = OUT / "e326_semantic_residual_censor_governor_audit.csv"
SUMMARY_OUT = OUT / "e326_semantic_residual_censor_summary.csv"
REPORT_OUT = OUT / "e326_semantic_residual_censor_report.md"
NULL_MAP_OUT = OUT / "e326_semantic_residual_censor_null_map.csv"
SCORE_OUT = OUT / "e326_semantic_residual_censor_scores.csv"

QS = [0.50, 0.60, 0.70, 0.80]
SCALES = [0.75, 1.00, 1.25]
POLICIES = ["keep", "damp25", "damp50", "boost125_damp25", "keep_l1", "anti_keep", "anti_damp25"]
SEMANTIC_Z_MIN = 1.75
SEMANTIC_DOM_MIN = 0.95
TOP_FEATURES_PER_TARGET = 8
MAX_NULL_EVAL = 36
PLACEMENT_REPS = 48
TARGET_REPS = 48
ALL_NULL_MODES = ["row", "subject", "dateblock", "target_perm", "sign_flip", "q_s_swap"]
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


def zscore(values: np.ndarray) -> np.ndarray:
    x = np.asarray(values, dtype=np.float64)
    mu = float(np.nanmean(x))
    sd = float(np.nanstd(x, ddof=0))
    if not np.isfinite(sd) or sd < EPS:
        return np.zeros_like(x)
    return np.clip((x - mu) / sd, -8.0, 8.0)


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
    path = OUT / f"submission_e326_semcensor_{safe_id(candidate_id)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def aligned_semantic_test(current: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    base, semantic, feature_meta = build_semantic_matrix()
    test_mask = base["split"].eq("test")
    test = base.loc[test_mask].sort_values(KEYS).reset_index(drop=True)
    semantic_test = semantic.loc[test_mask].sort_index().reset_index(drop=True)
    if not current[KEYS].astype(str).reset_index(drop=True).equals(test[KEYS].astype(str).reset_index(drop=True)):
        raise RuntimeError("semantic test rows do not align with current submission")
    return test, semantic_test, feature_meta


def support_for_candidate(
    basename: str,
    semantic_test: pd.DataFrame,
    attr: pd.DataFrame,
) -> tuple[np.ndarray, pd.DataFrame]:
    rows = attr[
        attr["basename"].eq(basename)
        & attr["signed_z_worst_abs"].ge(SEMANTIC_Z_MIN)
        & attr["signed_worst_mode_dominance"].ge(SEMANTIC_DOM_MIN)
    ].copy()
    if rows.empty:
        return np.zeros((len(semantic_test), len(TARGETS)), dtype=np.float64), rows

    pieces: list[pd.DataFrame] = []
    for target, part in rows.groupby("target", sort=False):
        part = part.sort_values(
            ["signed_z_worst_abs", "signed_worst_mode_dominance", "abs_z_worst_abs"],
            ascending=[False, False, False],
        ).head(TOP_FEATURES_PER_TARGET)
        pieces.append(part)
    selected = pd.concat(pieces, ignore_index=True) if pieces else rows.iloc[0:0].copy()

    support = np.zeros((len(semantic_test), len(TARGETS)), dtype=np.float64)
    for target_idx, target in enumerate(TARGETS):
        part = selected[selected["target"].eq(target)]
        if part.empty:
            continue
        score = np.zeros(len(semantic_test), dtype=np.float64)
        used = 0
        for row in part.itertuples(index=False):
            feature = str(row.feature)
            if feature not in semantic_test.columns:
                continue
            orientation = 1.0 if float(row.actual_signed_weighted_mean) >= 0.0 else -1.0
            weight = float(row.signed_z_worst_abs) * float(row.signed_worst_mode_dominance)
            score += orientation * weight * semantic_test[feature].to_numpy(dtype=np.float64)
            used += 1
        if used:
            support[:, target_idx] = zscore(score)
    return support, selected


def threshold_by_target(alignment: np.ndarray, active: np.ndarray, q: float) -> np.ndarray:
    thresh = np.zeros(len(TARGETS), dtype=np.float64)
    for j in range(len(TARGETS)):
        vals = alignment[active[:, j], j]
        thresh[j] = float(np.quantile(vals, q)) if len(vals) else np.inf
    return thresh


def transform_delta(delta: np.ndarray, support: np.ndarray, q: float, policy: str, scale: float) -> tuple[np.ndarray, dict[str, Any]]:
    active = np.abs(delta) > EPS
    alignment = np.sign(delta) * support
    hi = threshold_by_target(alignment, active, q)
    lo = threshold_by_target(alignment, active, 1.0 - q)
    keep_mask = active & (alignment >= hi.reshape(1, -1))
    anti_mask = active & (alignment <= lo.reshape(1, -1))

    if policy == "keep":
        factors = keep_mask.astype(float)
    elif policy == "damp25":
        factors = np.where(keep_mask, 1.0, 0.25) * active
    elif policy == "damp50":
        factors = np.where(keep_mask, 1.0, 0.50) * active
    elif policy == "boost125_damp25":
        factors = np.where(keep_mask, 1.25, 0.25) * active
    elif policy == "keep_l1":
        factors = keep_mask.astype(float)
    elif policy == "anti_keep":
        factors = anti_mask.astype(float)
    elif policy == "anti_damp25":
        factors = np.where(anti_mask, 1.0, 0.25) * active
    else:
        raise ValueError(policy)

    out = delta * factors
    if policy == "keep_l1":
        for j in range(len(TARGETS)):
            before = float(np.abs(delta[:, j]).sum())
            after = float(np.abs(out[:, j]).sum())
            if before > EPS and after > EPS:
                out[:, j] *= min(1.50, before / after)

    out = cap_delta(out * scale, CAP)
    before_l1 = float(np.abs(delta).sum())
    after_l1 = float(np.abs(out).sum())
    active_alignment = alignment[active]
    kept_alignment = alignment[np.abs(out) > EPS]
    metrics = {
        "semantic_q": q,
        "semantic_policy": policy,
        "semantic_scale": scale,
        "semantic_type": "anti_control" if policy.startswith("anti") else "semantic_censor",
        "semantic_active_cells": int(active.sum()),
        "semantic_kept_cells": int((np.abs(out) > EPS).sum()),
        "semantic_kept_frac": float((np.abs(out) > EPS).sum() / max(active.sum(), 1)),
        "semantic_l1_retained_frac": after_l1 / max(before_l1, EPS),
        "semantic_alignment_mean_active": float(np.mean(active_alignment)) if len(active_alignment) else 0.0,
        "semantic_alignment_mean_kept": float(np.mean(kept_alignment)) if len(kept_alignment) else 0.0,
        "semantic_alignment_p10_kept": float(np.quantile(kept_alignment, 0.10)) if len(kept_alignment) else 0.0,
    }
    return out, metrics


def generate_candidates(
    ready: pd.DataFrame,
    current: pd.DataFrame,
    semantic_test: pd.DataFrame,
    attr: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    rows: list[dict[str, Any]] = []
    delta_map: dict[str, np.ndarray] = {}
    seen_hashes: set[str] = set()

    for _, parent in ready.iterrows():
        parent_base = str(parent["basename"])
        parent_path = OUT / parent_base
        parent_delta = load_delta(parent_path, current)
        support, support_rows = support_for_candidate(parent_base, semantic_test, attr)
        support_targets = sorted(support_rows["target"].drop_duplicates().tolist()) if not support_rows.empty else []
        for q in QS:
            for policy in POLICIES:
                for scale in SCALES:
                    delta, metrics = transform_delta(parent_delta, support, q, policy, scale)
                    if np.max(np.abs(delta)) < EPS:
                        continue
                    candidate_id = f"{parent_base.replace('submission_e323_healthresid_', '')[:56]}__{policy}__q{q:.2f}__s{scale:.2f}"
                    path = write_submission(current, delta, candidate_id)
                    basename = path.name
                    if basename in delta_map or basename in seen_hashes:
                        continue
                    seen_hashes.add(basename)
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
                            "support_target_count": int(len(support_targets)),
                            "support_targets": "|".join(support_targets),
                            "support_feature_count": int(len(support_rows)),
                            **metrics,
                            **describe_delta(delta),
                        }
                    )
    return pd.DataFrame(rows), delta_map


def score_prefilter(candidate_meta: pd.DataFrame, current: pd.DataFrame) -> pd.DataFrame:
    if candidate_meta.empty:
        return candidate_meta
    sample = current[KEYS].copy()
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    paths = [OUT / str(path).split("/")[-1] for path in candidate_meta["basename"]]
    features = feature_rows([OUT / CURRENT, *paths], sample, refs, ref_vecs)
    scores = score_candidates(known, features, model_df).drop_duplicates("basename")
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
            "semantic_type",
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
    semantic_best = (
        prefilter[prefilter["semantic_type"].eq("semantic_censor")]
        .sort_values(["pred_delta_vs_current_p90", "pred_delta_vs_current_mean"])
        .groupby(["parent_basename", "semantic_policy"], as_index=False)
        .head(1)
    )
    anti_best = (
        prefilter[prefilter["semantic_type"].eq("anti_control")]
        .sort_values(["pred_delta_vs_current_p90", "pred_delta_vs_current_mean"])
        .groupby(["parent_basename", "semantic_policy"], as_index=False)
        .head(1)
    )
    selected = pd.concat(
        [
            strict.sort_values(["pred_delta_vs_current_p90", "pred_delta_vs_current_mean"]).head(18),
            info.sort_values(["pred_delta_vs_current_p90", "pred_delta_vs_current_mean"]).head(8),
            semantic_best.head(18),
            anti_best.head(6),
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


def write_null(current: pd.DataFrame, delta: np.ndarray, basename: str, mode: str, rep: int, meta: pd.DataFrame) -> Path:
    out = current.copy()
    nd = cap_delta(null_delta(delta, mode, rep, meta, basename), CAP)
    logits = logit(out[TARGETS].to_numpy(dtype=np.float64)) + nd
    out[TARGETS] = clip_prob(sigmoid(logits))
    NULL_DIR.mkdir(exist_ok=True)
    safe_name = basename[:72].replace("/", "_")
    path = NULL_DIR / f"submission_e326null_{safe_name}_{mode}_r{rep}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def build_nulls(selected: pd.DataFrame, delta_map: dict[str, np.ndarray], current: pd.DataFrame, meta: pd.DataFrame) -> tuple[pd.DataFrame, list[Path]]:
    rows: list[dict[str, Any]] = []
    paths: list[Path] = []
    for _, cand in selected.iterrows():
        basename = str(cand["basename"])
        delta = delta_map[basename]
        for mode in ALL_NULL_MODES:
            if mode in {"row", "subject", "dateblock"}:
                reps = PLACEMENT_REPS
            elif mode == "target_perm":
                reps = TARGET_REPS
            else:
                reps = 1
            for rep in range(reps):
                path = write_null(current, delta, basename, mode, rep, meta)
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
        empty.to_csv(NULL_MAP_OUT, index=False)
        empty.to_csv(GOVERNOR_OUT, index=False)
        return empty, empty

    null_map, null_paths = build_nulls(selected, delta_map, current, meta)
    sample = current[KEYS].copy()
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    candidate_paths = [OUT / b for b in selected["basename"]]
    features = feature_rows([OUT / CURRENT, *candidate_paths, *null_paths], sample, refs, ref_vecs)
    scores = score_candidates(known, features, model_df).drop_duplicates("basename")
    scores.to_csv(SCORE_OUT, index=False)

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
                "final_decision": "public_free_submission_ready" if ready else ("blocked_by_e326_nulls" if old_strict else str(a.get("promotion_decision", "hold"))),
            }
        )
    governor = pd.DataFrame(rows)
    if not governor.empty:
        governor = governor.sort_values(
            [
                "beats_e324_priority_local",
                "public_free_submission_ready",
                "semantic_type",
                "null_strict_rate",
                "actual_p90",
                "mean_dominance",
            ],
            ascending=[False, False, False, True, True, False],
        ).reset_index(drop=True)
    null_map.to_csv(NULL_MAP_OUT, index=False)
    governor.to_csv(GOVERNOR_OUT, index=False)
    return governor, null_map


def write_report(
    candidate_meta: pd.DataFrame,
    prefilter: pd.DataFrame,
    selected: pd.DataFrame,
    governor: pd.DataFrame,
    null_map: pd.DataFrame,
    e324_priority: pd.Series,
) -> None:
    strict = prefilter[prefilter["strict_promote_gate"].astype(bool)] if not prefilter.empty else pd.DataFrame()
    ready = governor[governor["public_free_submission_ready"].astype(bool)] if not governor.empty else pd.DataFrame()
    stronger = governor[governor["beats_e324_priority_local"].astype(bool)] if not governor.empty else pd.DataFrame()
    by_type = (
        governor.groupby("semantic_type", dropna=False)
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
                "slice": "e326_semantic_residual_censor",
                "generated": int(len(candidate_meta)),
                "prefilter_strict": int(len(strict)),
                "null_evaluated": int(len(selected)),
                "null_rows": int(len(null_map)),
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
        "semantic_type",
        "semantic_policy",
        "semantic_q",
        "semantic_scale",
        "semantic_l1_retained_frac",
        "semantic_alignment_mean_kept",
        "support_targets",
        "promotion_decision",
        "pred_delta_vs_current_mean",
        "pred_delta_vs_current_p90",
        "strict_promote_gate",
    ]
    gov_cols = [
        "basename",
        "semantic_type",
        "semantic_policy",
        "semantic_q",
        "semantic_scale",
        "semantic_l1_retained_frac",
        "semantic_alignment_mean_kept",
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
        "# E326 Semantic Residual Censor",
        "",
        "Public LB was not used.",
        "",
        "## Question",
        "",
        "If the E325 human/social axes are not just explanations, then censoring E323 residual cells by those axes should improve local action health more often than anti-semantic controls.",
        "",
        "## Summary",
        "",
        md(summary, n=5),
        "",
        "## Semantic vs Anti-Control",
        "",
        md(by_type, n=10),
        "",
        "## Prefilter Top Rows",
        "",
        md(prefilter[[c for c in pre_cols if c in prefilter.columns]], n=30) if not prefilter.empty else "_empty_",
        "",
        "## Null Governor",
        "",
        md(governor[[c for c in gov_cols if c in governor.columns]], n=50) if not governor.empty else "_empty_",
        "",
        "## Decision",
        "",
    ]
    if len(stronger):
        top = stronger.iloc[0]
        lines.append(
            f"- `{top['basename']}` beats the E324 priority under this local stress. Treat it as a scarce-slot candidate only after one more independent checker, because E326 uses the same selector family as E324."
        )
    elif len(ready):
        top = ready.iloc[0]
        lines.append(
            f"- `{top['basename']}` is public-free ready, but it does not locally dominate the existing E324 priority. Keep E323/E324 priority as the next submission candidate."
        )
    else:
        lines.append(
            "- No semantic-censored variant is public-free ready. Current evidence says E325 semantics are mainly diagnostic/explanatory at this action layer, not a better censoring rule."
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Semantic support is useful only if it survives against matched placement nulls and anti-controls.",
            "- If anti-controls match or beat semantic variants, the human story is probably describing where E323 moved, not providing a causal edit policy.",
            "- This protects public LB slots: a new file needs local readiness plus dominance over the existing E324 priority before it can replace `5508f966`.",
            "",
            "## Outputs",
            "",
            f"- `{CANDIDATE_OUT.relative_to(ROOT)}`",
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
        empty.to_csv(CANDIDATE_OUT, index=False)
        empty.to_csv(SELECTED_OUT, index=False)
        empty.to_csv(GOVERNOR_OUT, index=False)
        empty.to_csv(SUMMARY_OUT, index=False)
        REPORT_OUT.write_text("# E326 Semantic Residual Censor\n\nNo E324 ready candidates found.\n", encoding="utf-8")
        print(f"report={REPORT_OUT.relative_to(ROOT)}")
        return

    test, semantic_test, _feature_meta = aligned_semantic_test(current)
    attr = pd.read_csv(E325_ATTR)
    candidate_meta, delta_map = generate_candidates(ready, current, semantic_test, attr)
    candidate_meta.to_csv(CANDIDATE_OUT, index=False)

    prefilter = score_prefilter(candidate_meta, current)
    selected = select_for_null(prefilter)
    selected.to_csv(SELECTED_OUT, index=False)

    meta = align_meta_to_current(test, current)
    e324_priority = ready.iloc[0]
    governor, null_map = run_governor(selected, delta_map, current, meta, e324_priority)
    write_report(candidate_meta, prefilter, selected, governor, null_map, e324_priority)

    print(f"generated={len(candidate_meta)}")
    print(f"strict_prefilter={int(prefilter['strict_promote_gate'].sum()) if not prefilter.empty else 0}")
    print(f"selected={len(selected)}")
    print(f"null_rows={len(null_map)}")
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
