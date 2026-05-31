#!/usr/bin/env python3
"""E323: null-common residual generator.

E322 showed that E321 can preselect visible E319 candidates, but the selected
files are still too common under row/subject/dateblock nulls.  E323 changes the
action layer instead of ranking the same finished files:

For each E322 near miss, estimate the row/subject/dateblock-null common logit
movement, then generate residual/censored actions that keep the part of the
movement least reproducible by placement nulls.

No public LB is used.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
import hashlib
import sys
import warnings

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
NULL_DIR = OUT / "e323_null_common_residual_nulls"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e272_public_free_candidate_audit import CURRENT, evaluate_models, score_candidates  # noqa: E402
from e288_lifestyle_bundle_jepa_audit import TARGETS, clip_prob, load_frames, stable_seed  # noqa: E402
from e289_target_specific_lifestyle_slice_audit import safe_id  # noqa: E402
from e297_episode_state_materializer import align_meta_to_current, feature_rows, sigmoid  # noqa: E402
from e315_human_ready_composition_materializer import cap_delta, md, top_cells  # noqa: E402
from e321_mode_adversarial_action_health import PROMOTION_THRESHOLDS  # noqa: E402
from e322_adversarial_preselector_nullcheck import (  # noqa: E402
    fit_health_preselector,
    feature_table,
    load_candidate_meta,
)
from public_anchor_bottleneck_decomposition import KEYS, load_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

E322_GOVERNOR = OUT / "e322_adversarial_preselector_governor_audit.csv"

CANDIDATE_OUT = OUT / "e323_null_common_residual_candidate_audit.csv"
PREFILTER_OUT = OUT / "e323_null_common_residual_prefilter_audit.csv"
OOF_OUT = OUT / "e323_null_common_residual_preselector_oof_audit.csv"
SELECTED_OUT = OUT / "e323_null_common_residual_selected_audit.csv"
GOVERNOR_OUT = OUT / "e323_null_common_residual_governor_audit.csv"
SUMMARY_OUT = OUT / "e323_null_common_residual_summary.csv"
REPORT_OUT = OUT / "e323_null_common_residual_report.md"
NULL_MAP_OUT = OUT / "e323_null_common_residual_null_map.csv"

PLACEMENT_MODES = ["row", "subject", "dateblock"]
ALL_NULL_MODES = ["row", "subject", "dateblock", "target_perm", "sign_flip", "q_s_swap"]
SOURCE_COUNT = 14
REF_NULL_REPS = 8
GOVERNOR_NULL_REPS = 5
MAX_CANDIDATES = 420
MAX_NULL_EVAL = 44
CAP = 0.35
EPS = 1.0e-12


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def short_hash(frame: pd.DataFrame) -> str:
    arr = np.asarray(frame[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def current_frame() -> pd.DataFrame:
    return load_sub(OUT / CURRENT).sort_values(KEYS).reset_index(drop=True)


def load_delta(path: Path, current: pd.DataFrame) -> np.ndarray:
    sub = load_sub(path).sort_values(KEYS).reset_index(drop=True)
    if not sub[KEYS].equals(current[KEYS]):
        raise ValueError(f"key mismatch: {path}")
    return logit(sub[TARGETS].to_numpy(dtype=np.float64)) - logit(current[TARGETS].to_numpy(dtype=np.float64))


def write_submission(current: pd.DataFrame, delta: np.ndarray, candidate_id: str) -> Path:
    out = current.copy()
    logits = logit(out[TARGETS].to_numpy(dtype=np.float64)) + cap_delta(delta, CAP)
    out[TARGETS] = clip_prob(sigmoid(logits))
    path = OUT / f"submission_e323_healthresid_{safe_id(candidate_id)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def describe_delta(delta: np.ndarray) -> dict[str, Any]:
    abs_by_target = np.abs(delta).sum(axis=0)
    total = float(abs_by_target.sum())
    return {
        "nonzero_rows": int(np.any(np.abs(delta) > EPS, axis=1).sum()),
        "nonzero_cells": int(np.sum(np.abs(delta) > EPS)),
        "mean_abs_delta": float(np.mean(np.abs(delta))),
        "max_abs_delta": float(np.max(np.abs(delta))),
        "l1_delta": total,
        "signed_delta_sum": float(np.sum(delta)),
        "q_abs_share": float(abs_by_target[:3].sum() / max(total, EPS)),
        "s_abs_share": float(abs_by_target[3:].sum() / max(total, EPS)),
        **{f"abs_{t}": float(abs_by_target[i]) for i, t in enumerate(TARGETS)},
    }


def shuffle_rows(delta: np.ndarray, mode: str, meta: pd.DataFrame, seed_parts: tuple[Any, ...]) -> np.ndarray:
    rng = np.random.default_rng(stable_seed("e323shuffle", *map(str, seed_parts)))
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
        rng = np.random.default_rng(stable_seed("e323targetperm", basename, rep))
        return delta[:, rng.permutation(len(TARGETS))]
    if mode == "q_s_swap":
        out = np.zeros_like(delta)
        out[:, :3] = delta[:, [3, 4, 5]]
        out[:, 3:6] = delta[:, :3]
        out[:, 6] = delta[:, 6]
        return out
    raise ValueError(mode)


def placement_null_stack(delta: np.ndarray, meta: pd.DataFrame, basename: str, reps: int = REF_NULL_REPS) -> np.ndarray:
    values: list[np.ndarray] = []
    for mode in PLACEMENT_MODES:
        for rep in range(reps):
            values.append(null_delta(delta, mode, rep, meta, basename))
    return np.stack(values, axis=0)


def cell_unique_mask(delta: np.ndarray, stack: np.ndarray, q: float) -> np.ndarray:
    threshold = np.quantile(np.abs(stack), q, axis=0)
    sign_common = np.mean(np.sign(stack) == np.sign(delta)[None, :, :], axis=0)
    score = np.abs(delta) - threshold - 0.05 * sign_common * np.abs(delta)
    return score > np.quantile(score, 0.75)


def project_out(delta: np.ndarray, basis: np.ndarray, strength: float) -> np.ndarray:
    denom = float(np.sum(basis * basis))
    if denom < EPS:
        return delta.copy()
    coef = float(np.sum(delta * basis) / denom)
    return delta - strength * coef * basis


def source_near_misses() -> pd.DataFrame:
    gov = pd.read_csv(E322_GOVERNOR)
    gov = gov[gov["fresh_old_strict_promote"].astype(bool)].copy()
    gov["near_miss_score"] = (
        gov["fresh_actual_p90"].rank(pct=True, ascending=True)
        + gov["fresh_null_strict_rate"].rank(pct=True, ascending=True)
        - gov["fresh_worst_mode_p90_dominance"].rank(pct=True, ascending=False)
    )
    gov = gov.sort_values(
        [
            "fresh_null_strict_rate",
            "fresh_worst_mode_p90_dominance",
            "fresh_actual_p90",
        ],
        ascending=[True, False, True],
    )
    return gov.head(SOURCE_COUNT).reset_index(drop=True)


def add_candidate(
    rows: list[dict[str, Any]],
    delta_map: dict[str, np.ndarray],
    current: pd.DataFrame,
    source: pd.Series,
    delta: np.ndarray,
    recipe: str,
    variant: str,
    weight: float,
    keep: int | str,
    extra: dict[str, Any] | None = None,
) -> None:
    if len(rows) >= MAX_CANDIDATES:
        return
    delta = cap_delta(delta * weight, CAP)
    if np.max(np.abs(delta)) < EPS:
        return
    source_base = str(source["basename"])
    candidate_id = f"{recipe}__src_{source_base.replace('submission_e319_modespec_', '')[:44]}__{variant}__k{keep}__w{weight:.2f}"
    path = write_submission(current, delta, candidate_id)
    basename = path.name
    if basename in delta_map:
        return
    delta_map[basename] = delta
    mode_mix = source.get("selected_mode_mix", "")
    rows.append(
        {
            "basename": basename,
            "source_path": rel(path),
            "parent_basename": source_base,
            "recipe": recipe,
            "policy": str(source.get("policy", "")),
            "group_key": str(source.get("group_key", "")),
            "base_variant": variant,
            "source_count": int(source.get("meta_source_count", source.get("source_count", 1))),
            "source_basenames": source_base,
            "selected_mode_mix": mode_mix,
            "weight": weight,
            "oracle_control": False,
            "parent_fresh_null_strict_rate": float(source.get("fresh_null_strict_rate", np.nan)),
            "parent_fresh_actual_p90": float(source.get("fresh_actual_p90", np.nan)),
            "parent_fresh_worst_mode_p90_dominance": float(source.get("fresh_worst_mode_p90_dominance", np.nan)),
            **describe_delta(delta),
            **(extra or {}),
        }
    )


def generate_candidates(current: pd.DataFrame, meta: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    sources = source_near_misses()
    rows: list[dict[str, Any]] = []
    delta_map: dict[str, np.ndarray] = {}

    for _, source in sources.iterrows():
        source_base = str(source["basename"])
        delta = load_delta(OUT / source_base, current)
        stack = placement_null_stack(delta, meta, source_base, reps=REF_NULL_REPS)
        null_mean = stack.mean(axis=0)
        null_median = np.median(stack, axis=0)
        centered = delta - null_mean
        med_centered = delta - null_median
        projected = project_out(delta, null_mean, 1.0)
        unique75 = delta * cell_unique_mask(delta, stack, 0.75)
        unique90 = delta * cell_unique_mask(delta, stack, 0.90)

        variants: dict[str, np.ndarray] = {}
        for lam in [0.50, 0.75, 1.00, 1.25, 1.50]:
            variants[f"meanresid_l{lam:.2f}"] = delta - lam * null_mean
        for lam in [0.75, 1.00, 1.25]:
            variants[f"medianresid_l{lam:.2f}"] = delta - lam * null_median
        variants["orth_nullmean"] = projected
        variants["centered_only"] = centered
        variants["medcenter_only"] = med_centered
        variants["unique_q75"] = unique75
        variants["unique_q90"] = unique90
        variants["unique_q75_centered"] = centered * (np.abs(unique75) > EPS)
        variants["unique_q90_centered"] = centered * (np.abs(unique90) > EPS)

        for variant, base in variants.items():
            keep_grid: list[int | str] = [32, 64, 128, "all"]
            if variant.startswith("unique"):
                keep_grid = [32, 64, "all"]
            for keep in keep_grid:
                shaped = top_cells(base, int(keep)) if isinstance(keep, int) else base
                for weight in [0.50, 0.75, 1.00, 1.25, 1.50]:
                    if "meanresid_l1.50" in variant and weight > 1.25:
                        continue
                    add_candidate(
                        rows,
                        delta_map,
                        current,
                        source,
                        shaped,
                        "null_common_residual",
                        variant,
                        weight,
                        keep,
                        {
                            "ref_null_reps": REF_NULL_REPS,
                            "ref_null_abs_mean": float(np.mean(np.abs(stack))),
                            "ref_centered_abs_mean": float(np.mean(np.abs(centered))),
                            "ref_unique75_cells": int(np.sum(np.abs(unique75) > EPS)),
                            "ref_unique90_cells": int(np.sum(np.abs(unique90) > EPS)),
                        },
                    )
                    if len(rows) >= MAX_CANDIDATES:
                        break
                if len(rows) >= MAX_CANDIDATES:
                    break
            if len(rows) >= MAX_CANDIDATES:
                break
        if len(rows) >= MAX_CANDIDATES:
            break
    return pd.DataFrame(rows), delta_map


def score_generated(candidates: pd.DataFrame, current: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    sample = current[KEYS].copy()
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    # E322's health preselector is trained on the governed E319 rows.  Include
    # the E319 universe as anchors, then return predictions only for E323 files.
    e319 = load_candidate_meta()
    generated = candidates.copy()
    generated["previously_null_evaluated"] = False
    combined = pd.concat([e319, generated], ignore_index=True, sort=False).drop_duplicates("basename")
    paths = [OUT / CURRENT, *[OUT / b for b in combined["basename"]]]
    features = feature_rows(paths, sample, refs, ref_vecs)
    scores = score_candidates(known, features, model_df).drop_duplicates("basename")
    feature_df, num_cols, cat_cols = feature_table(combined, scores)
    scored, oof = fit_health_preselector(feature_df, num_cols, cat_cols)
    generated_scores = scored[scored["basename"].isin(generated["basename"])].reset_index(drop=True)
    extra_cols = [
        c
        for c in [
            "basename",
            "source_path",
            "parent_basename",
            "parent_fresh_null_strict_rate",
            "parent_fresh_actual_p90",
            "parent_fresh_worst_mode_p90_dominance",
            "ref_null_reps",
            "ref_null_abs_mean",
            "ref_centered_abs_mean",
            "ref_unique75_cells",
            "ref_unique90_cells",
        ]
        if c in generated.columns
    ]
    generated_scores = generated_scores.merge(
        generated[extra_cols].drop_duplicates("basename"),
        on="basename",
        how="left",
        suffixes=("", "_src"),
    )
    return generated_scores, oof, model_df


def select_for_governor(scored: pd.DataFrame) -> pd.DataFrame:
    pool = scored[
        scored["old_strict_promote"].astype(bool)
        & scored["actual_p90"].le(-2.0e-5)
    ].copy()
    if pool.empty:
        pool = scored.copy()
    pool["selection_rank_score"] = (
        pool["actual_p90"].rank(pct=True, ascending=True)
        + pool["pred_null_strict_rate"].rank(pct=True, ascending=True)
        - pool["pred_worst_placement_dominance"].rank(pct=True, ascending=False)
        - pool["pred_adversarial_health"].rank(pct=True, ascending=False)
    )
    frames = [
        pool.sort_values("selection_rank_score").head(20).assign(selection_reason="rank_score"),
        pool.sort_values(["pred_null_strict_rate", "actual_p90"]).groupby("parent_basename", as_index=False).head(2).assign(selection_reason="parent_best"),
        pool.sort_values(["pred_ready_score", "actual_p90"], ascending=[False, True]).groupby("base_variant", as_index=False).head(2).assign(selection_reason="variant_best"),
    ]
    selected = pd.concat(frames, ignore_index=True).drop_duplicates("basename")
    selected = selected.sort_values(
        ["selection_rank_score", "pred_null_strict_rate", "actual_p90"],
        ascending=[True, True, True],
    ).head(MAX_NULL_EVAL)
    return selected.reset_index(drop=True)


def write_null(current: pd.DataFrame, delta: np.ndarray, basename: str, mode: str, rep: int, meta: pd.DataFrame) -> Path:
    out = current.copy()
    nd = cap_delta(null_delta(delta, mode, rep, meta, basename), CAP)
    logits = logit(out[TARGETS].to_numpy(dtype=np.float64)) + nd
    out[TARGETS] = clip_prob(sigmoid(logits))
    NULL_DIR.mkdir(exist_ok=True)
    safe_name = basename[:72].replace("/", "_")
    path = NULL_DIR / f"submission_e323null_{safe_name}_{mode}_r{rep}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def run_governor(
    selected: pd.DataFrame,
    delta_map: dict[str, np.ndarray],
    current: pd.DataFrame,
    meta: pd.DataFrame,
    model_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if selected.empty:
        return pd.DataFrame(), pd.DataFrame()
    sample = current[KEYS].copy()
    known, refs, ref_vecs = build_known_and_refs(sample)
    null_rows: list[dict[str, Any]] = []
    null_paths: list[Path] = []
    for _, row in selected.iterrows():
        basename = str(row["basename"])
        delta = delta_map[basename]
        for mode in ALL_NULL_MODES:
            reps = GOVERNOR_NULL_REPS if mode in {"row", "subject", "dateblock", "target_perm"} else 1
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
    paths = [OUT / b for b in selected["basename"]]
    features = feature_rows([OUT / CURRENT, *paths, *null_paths], sample, refs, ref_vecs)
    scores = score_candidates(known, features, model_df)
    cand_scores = scores[scores["basename"].isin(selected["basename"])].copy()
    null_scores = scores[scores["basename"].isin(null_map["null_basename"])].copy()

    rows: list[dict[str, Any]] = []
    for _, cand in selected.iterrows():
        basename = str(cand["basename"])
        actual = cand_scores[cand_scores["basename"].eq(basename)]
        if actual.empty:
            continue
        a = actual.iloc[0]
        these_null = null_scores.merge(
            null_map[null_map["source_basename"].eq(basename)][["null_basename", "mode"]],
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
        for mode, part in these_null.groupby("mode"):
            vals = part["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64)
            mode_doms[f"{mode}_p90_dominance"] = float(np.mean(actual_p90 < vals))
        worst_mode = float(min(mode_doms.values())) if mode_doms else 0.0
        ready = bool(
            old_strict
            and actual_p90 <= -2.0e-5
            and null_strict_rate <= PROMOTION_THRESHOLDS["null_strict_rate"]
            and p90_dominance >= PROMOTION_THRESHOLDS["p90_dominance"]
            and mean_dominance >= PROMOTION_THRESHOLDS["mean_dominance"]
            and worst_mode >= PROMOTION_THRESHOLDS["worst_mode_p90_dominance"]
        )
        rows.append(
            {
                **cand.to_dict(),
                "fresh_old_strict_promote": old_strict,
                "fresh_actual_mean": actual_mean,
                "fresh_actual_p10": float(a["pred_delta_vs_current_p10"]),
                "fresh_actual_p90": actual_p90,
                "fresh_actual_beats_current_rate": float(a["pred_beats_current_rate"]),
                "fresh_null_count": int(len(these_null)),
                "fresh_null_strict_rate": null_strict_rate,
                "fresh_p90_dominance": p90_dominance,
                "fresh_mean_dominance": mean_dominance,
                "fresh_worst_mode_p90_dominance": worst_mode,
                **{f"fresh_{k}": v for k, v in mode_doms.items()},
                "fresh_public_free_submission_ready": ready,
                "fresh_final_decision": "public_free_submission_ready" if ready else "blocked_by_e323_nulls",
            }
        )
    governor = pd.DataFrame(rows)
    if not governor.empty:
        governor = governor.sort_values(
            [
                "fresh_public_free_submission_ready",
                "fresh_old_strict_promote",
                "fresh_null_strict_rate",
                "fresh_actual_p90",
                "fresh_mean_dominance",
            ],
            ascending=[False, False, True, True, False],
        ).reset_index(drop=True)
    return null_map, governor


def write_report(candidates: pd.DataFrame, prefilter: pd.DataFrame, oof: pd.DataFrame, selected: pd.DataFrame, governor: pd.DataFrame) -> None:
    ready = governor[governor["fresh_public_free_submission_ready"].astype(bool)] if not governor.empty else pd.DataFrame()
    summary = pd.DataFrame(
        [
            {
                "slice": "generated",
                "rows": int(len(candidates)),
                "old_strict": np.nan,
                "best_p90": np.nan,
                "best_null_strict": np.nan,
                "ready": np.nan,
            },
            {
                "slice": "prefilter",
                "rows": int(len(prefilter)),
                "old_strict": int(prefilter["old_strict_promote"].sum()) if not prefilter.empty else 0,
                "best_p90": float(prefilter["actual_p90"].min()) if not prefilter.empty else np.nan,
                "best_pred_null_strict": float(prefilter["pred_null_strict_rate"].min()) if not prefilter.empty else np.nan,
                "best_pred_health": float(prefilter["pred_adversarial_health"].max()) if not prefilter.empty else np.nan,
            },
            {
                "slice": "selected",
                "rows": int(len(selected)),
                "old_strict": int(selected["old_strict_promote"].sum()) if not selected.empty else 0,
                "best_p90": float(selected["actual_p90"].min()) if not selected.empty else np.nan,
                "best_pred_null_strict": float(selected["pred_null_strict_rate"].min()) if not selected.empty else np.nan,
                "best_pred_health": float(selected["pred_adversarial_health"].max()) if not selected.empty else np.nan,
            },
            {
                "slice": "fresh_governor",
                "rows": int(len(governor)),
                "old_strict": int(governor["fresh_old_strict_promote"].sum()) if not governor.empty else 0,
                "best_p90": float(governor["fresh_actual_p90"].min()) if not governor.empty else np.nan,
                "best_null_strict": float(governor["fresh_null_strict_rate"].min()) if not governor.empty else np.nan,
                "best_worst_mode": float(governor["fresh_worst_mode_p90_dominance"].max()) if not governor.empty else np.nan,
                "ready": int(governor["fresh_public_free_submission_ready"].sum()) if not governor.empty else 0,
            },
        ]
    )
    summary.to_csv(SUMMARY_OUT, index=False)
    top_cols = [
        "basename",
        "parent_basename",
        "base_variant",
        "weight",
        "actual_p90",
        "pred_null_strict_rate",
        "pred_worst_placement_dominance",
        "pred_adversarial_health",
    ]
    gov_cols = [
        "basename",
        "parent_basename",
        "base_variant",
        "weight",
        "fresh_actual_p90",
        "fresh_null_strict_rate",
        "fresh_p90_dominance",
        "fresh_mean_dominance",
        "fresh_worst_mode_p90_dominance",
        "fresh_public_free_submission_ready",
        "fresh_final_decision",
    ]
    lines = [
        "# E323 Null-Common Residual Generator",
        "",
        "Public LB was not used.",
        "",
        "## Question",
        "",
        "If E322 near misses fail because their movement is null-common, does subtracting or censoring row/subject/dateblock-common movement create a visible and null-rare action?",
        "",
        "## Summary",
        "",
        md(summary, n=10),
        "",
        "## Preselector OOF",
        "",
        md(oof, n=20),
        "",
        "## Selected For Fresh Null",
        "",
        md(selected[[c for c in top_cols if c in selected.columns]], n=30),
        "",
        "## Fresh Governor",
        "",
        md(governor[[c for c in gov_cols if c in governor.columns]] if not governor.empty else governor, n=40),
        "",
        "## Decision",
        "",
    ]
    if len(ready):
        lines.append(f"- `{ready.iloc[0]['basename']}` passed E323 public-free governance. Review private risk before any public use.")
    else:
        lines.extend(
            [
                "- E323 did not produce a public-free candidate.",
                "- This rejects the simplest null-common residualization/censoring generator.",
                "- If the hidden placement law exists, it is not recovered by subtracting the average row/subject/dateblock null movement from E322 near misses.",
            ]
        )
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            f"- `{CANDIDATE_OUT.relative_to(ROOT)}`",
            f"- `{PREFILTER_OUT.relative_to(ROOT)}`",
            f"- `{OOF_OUT.relative_to(ROOT)}`",
            f"- `{SELECTED_OUT.relative_to(ROOT)}`",
            f"- `{GOVERNOR_OUT.relative_to(ROOT)}`",
            f"- `{SUMMARY_OUT.relative_to(ROOT)}`",
            f"- `{REPORT_OUT.relative_to(ROOT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    current = current_frame()
    base, _, _, _ = load_frames()
    test_df = base.loc[base["split"].eq("test")].reset_index(drop=True)
    meta = align_meta_to_current(test_df, current)
    candidates, delta_map = generate_candidates(current, meta)
    candidates.to_csv(CANDIDATE_OUT, index=False)
    prefilter, oof, model_df = score_generated(candidates, current)
    selected = select_for_governor(prefilter)
    null_map, governor = run_governor(selected, delta_map, current, meta, model_df)
    prefilter.to_csv(PREFILTER_OUT, index=False)
    oof.to_csv(OOF_OUT, index=False)
    selected.to_csv(SELECTED_OUT, index=False)
    null_map.to_csv(NULL_MAP_OUT, index=False)
    governor.to_csv(GOVERNOR_OUT, index=False)
    write_report(candidates, prefilter, oof, selected, governor)
    return candidates, prefilter, governor


def main() -> None:
    candidates, prefilter, governor = run()
    ready_count = int(governor["fresh_public_free_submission_ready"].sum()) if not governor.empty else 0
    print(f"generated={len(candidates)}")
    print(f"old_strict={int(prefilter['old_strict_promote'].sum()) if not prefilter.empty else 0}")
    print(f"selected_for_null={len(governor)}")
    print(f"fresh_ready={ready_count}")
    if not governor.empty:
        print(f"best_fresh_p90={governor['fresh_actual_p90'].min():.9f}")
        print(f"best_null_strict={governor['fresh_null_strict_rate'].min():.6f}")
        print(f"best_worst_mode={governor['fresh_worst_mode_p90_dominance'].max():.6f}")
    print(f"report={REPORT_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
