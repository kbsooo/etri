#!/usr/bin/env python3
"""E350: compact hidden lifestyle-state plateau stress.

Question:
    Is the E349 compact Q1/Q2/Q3/S1 lifestyle-state slice a real local basin,
    or just one lucky cell-threshold point?

The experiment keeps the public-best E247 base and treats the E347-vs-E247
logit delta as a JEPA-style action view over a hidden lifestyle state.  It
then scans nearby cell thresholds, mild scales, and optional S3-tail restoration
without using public LB feedback.
"""

from __future__ import annotations

import hashlib
import shutil
import sys
import warnings
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

warnings.filterwarnings("ignore", message="An input array is constant")

from e272_public_free_candidate_audit import (  # noqa: E402
    CURRENT,
    build_features,
    evaluate_models,
    score_candidates,
)
from e328_ownlatent_lifestyle_state_experiment import md_table, safe_id  # noqa: E402
from e346_counteraxis_public_analog_audit import (  # noqa: E402
    axis_records,
    null_delta,
    public_analog_metrics,
    test_meta,
)
from e347_lifestyle_state_candidate_reaudit import (  # noqa: E402
    load_candidate,
    load_lifestyle_teacher,
    normalize_dates,
)
from e349_e347_target_cell_ablation_stress import (  # noqa: E402
    Q1_STATE_COL,
    cell_keep_mask,
    clip_prob,
    movement_entropy,
    short_hash,
    sigmoid,
    specificity_metrics,
    target_mask,
)
from public_anchor_bottleneck_decomposition import KEYS, TARGETS, load_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


RNG_SEED = 20260531 + 350
EPS = 1.0e-12
NULL_REPS = 8

E347_UPLOAD = OUT / "submission_e347_stateful_counteraxis_lifestyle_e344_nullsafe_top5_e131968c_uploadsafe.csv"
E349_UPLOAD = OUT / "submission_e349_lifestate_ablate_selected_cell_abs_top65_q1q2q3s1_93c55c92_uploadsafe.csv"
OBS_AXIS_IN = OUT / "e346_public_analog_observed_axes.csv"

CANDIDATE_OUT = OUT / "e350_compact_state_plateau_candidates.csv"
SCORE_OUT = OUT / "e350_compact_state_plateau_scores.csv"
PUBLIC_ANALOG_OUT = OUT / "e350_compact_state_plateau_public_analog.csv"
REPORT_OUT = OUT / "e350_compact_state_plateau_report.md"
UPLOAD_PREFIX = "submission_e350_compactplateau"

PRIMARY_TARGETS = ["Q1", "Q2", "Q3", "S1"]
S3_TARGET = ["S3"]


def stable_seed(*parts: object) -> int:
    text = "|".join(map(str, parts))
    return RNG_SEED + int(hashlib.sha1(text.encode("utf-8")).hexdigest()[:8], 16) % 100000


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def locate(path_or_name: object) -> Path:
    raw = Path(str(path_or_name))
    candidates = [raw] if raw.is_absolute() else [ROOT / raw, OUT / raw.name, OUT / str(path_or_name)]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError(str(path_or_name))


def target_abs(delta: np.ndarray) -> dict[str, float]:
    return {f"abs_{target}": float(np.abs(delta[:, i]).sum()) for i, target in enumerate(TARGETS)}


def candidate_meta(spec: dict[str, Any], path: Path, masked_delta: np.ndarray) -> dict[str, Any]:
    return {
        **{k: v for k, v in spec.items() if k != "targets"},
        "targets": ",".join(spec["targets"]),
        "file": rel(path),
        "basename": path.name,
        "changed_rows_vs_e247": int((np.abs(masked_delta).sum(axis=1) > EPS).sum()),
        "changed_cells_vs_e247": int((np.abs(masked_delta) > EPS).sum()),
        "move_l1": float(np.abs(masked_delta).sum()),
        "move_l2": float(np.linalg.norm(masked_delta.reshape(-1))),
        "row_entropy": movement_entropy(np.abs(masked_delta).sum(axis=1)),
        **target_abs(masked_delta),
    }


def write_candidate(base: pd.DataFrame, base_logit: np.ndarray, masked_delta: np.ndarray, spec: dict[str, Any]) -> tuple[Path, dict[str, Any]]:
    out = base[KEYS].copy()
    out[TARGETS] = clip_prob(sigmoid(base_logit + masked_delta))
    tag = safe_id(str(spec["variant"]), 80)
    path = OUT / f"{UPLOAD_PREFIX}_{tag}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path, candidate_meta(spec, path, masked_delta)


def reference_row(name: str, path: Path, base: pd.DataFrame, base_logit: np.ndarray, target_set: str, threshold_frac: float, scale: float, s3_alpha: float) -> dict[str, Any]:
    frame = load_candidate(path, base[KEYS])
    delta = logit(frame[TARGETS].to_numpy(dtype=np.float64)) - base_logit
    spec = {
        "variant": name,
        "target_set": target_set,
        "row_mask": "all",
        "cell_mask": "reference",
        "sign_mask": "both",
        "scale": scale,
        "threshold_frac": threshold_frac,
        "s3_alpha": s3_alpha,
        "targets": TARGETS,
    }
    return candidate_meta(spec, path, delta)


def build_delta(e347_delta: np.ndarray, threshold_frac: float, scale: float, s3_alpha: float, family: str) -> tuple[np.ndarray, list[str]]:
    cell_mode = f"abs_top{int(threshold_frac)}"
    cell_m = cell_keep_mask(e347_delta, cell_mode)
    if family == "compact_s3tail":
        primary = e347_delta * target_mask(PRIMARY_TARGETS) * cell_m * float(scale)
        s3 = e347_delta * target_mask(S3_TARGET) * cell_m * float(s3_alpha)
        return primary + s3, PRIMARY_TARGETS + (S3_TARGET if s3_alpha > 0 else [])
    if family == "compact_no_s3":
        return e347_delta * target_mask(PRIMARY_TARGETS) * cell_m * float(scale), PRIMARY_TARGETS
    if family == "all":
        return e347_delta * cell_m * float(scale), TARGETS
    if family == "nos3":
        keep = [target for target in TARGETS if target != "S3"]
        return e347_delta * target_mask(keep) * cell_m * float(scale), keep
    if family == "qonly":
        keep = ["Q1", "Q2", "Q3"]
        return e347_delta * target_mask(keep) * cell_m * float(scale), keep
    raise ValueError(family)


def variant_specs() -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = []
    thresholds = [90, 85, 80, 75, 70, 65, 60, 55, 50, 45, 40, 35]
    scales = [0.99, 0.995, 1.00, 1.005, 1.01]
    s3_alphas = [0.00, 0.25, 0.50, 0.75, 1.00]
    for threshold in thresholds:
        for scale in scales:
            for alpha in s3_alphas:
                specs.append(
                    {
                        "variant": f"compact_t{threshold}_s{scale:.3f}_s3a{alpha:.2f}",
                        "target_set": "compact_s3tail",
                        "row_mask": "all",
                        "cell_mask": f"abs_top{threshold}",
                        "sign_mask": "both",
                        "scale": scale,
                        "threshold_frac": float(threshold),
                        "s3_alpha": alpha,
                        "family": "compact_s3tail",
                    }
                )

    for family in ["compact_no_s3", "all", "nos3", "qonly"]:
        for threshold in [85, 80, 75, 70, 65, 60, 50, 40]:
            specs.append(
                {
                    "variant": f"control_{family}_t{threshold}",
                    "target_set": family,
                    "row_mask": "all",
                    "cell_mask": f"abs_top{threshold}",
                    "sign_mask": "both",
                    "scale": 1.00,
                    "threshold_frac": float(threshold),
                    "s3_alpha": 0.0 if family != "all" else 1.0,
                    "family": family,
                }
            )
    return specs


def create_candidates(base: pd.DataFrame, base_logit: np.ndarray, e347: pd.DataFrame, e349: pd.DataFrame) -> pd.DataFrame:
    e347_delta = logit(e347[TARGETS].to_numpy(dtype=np.float64)) - base_logit
    rows: list[dict[str, Any]] = [
        reference_row("canonical_e347", E347_UPLOAD, base, base_logit, "all", 100.0, 1.0, 1.0),
        reference_row("canonical_e349", E349_UPLOAD, base, base_logit, "compact_s3tail", 65.0, 1.0, 0.0),
    ]
    hashes = {short_hash(e347), short_hash(e349)}
    for spec in variant_specs():
        delta, targets = build_delta(e347_delta, spec["threshold_frac"], spec["scale"], spec["s3_alpha"], spec["family"])
        spec = {**spec, "targets": targets}
        path, meta = write_candidate(base, base_logit, delta, spec)
        frame_hash = path.stem.rsplit("_", 1)[-1]
        if frame_hash in hashes:
            path.unlink(missing_ok=True)
            continue
        hashes.add(frame_hash)
        rows.append(meta)
    out = pd.DataFrame(rows).sort_values(["target_set", "threshold_frac", "scale", "s3_alpha", "variant"]).reset_index(drop=True)
    out.to_csv(CANDIDATE_OUT, index=False)
    return out


def score_public_analog(candidates: pd.DataFrame, base: pd.DataFrame, base_logit: np.ndarray) -> pd.DataFrame:
    obs_axes = pd.read_csv(OBS_AXIS_IN)
    axes = axis_records(obs_axes, base, base_logit)
    meta = test_meta(base)
    modes = ["row_perm", "target_perm", "sign_flip", "row_sign", "cell_perm", "subject_perm", "dateblock_perm"]
    rows: list[dict[str, Any]] = []
    null_rows: list[dict[str, Any]] = []
    for rec in candidates.to_dict("records"):
        path = locate(rec["file"])
        pred = load_candidate(path, base[KEYS])
        delta = logit(pred[TARGETS].to_numpy(dtype=np.float64)) - base_logit
        rows.append({"basename": rec["basename"], **public_analog_metrics(delta, axes)})
        for mode in modes:
            for rep in range(NULL_REPS):
                nd = null_delta(delta, mode, meta, stable_seed(rec["basename"], mode, rep))
                null_rows.append({"basename": rec["basename"], "mode": mode, "rep": rep, **public_analog_metrics(nd, axes)})

    scores = pd.DataFrame(rows)
    nulls = pd.DataFrame(null_rows)
    risk_cols = [
        "public_loss_weighted_pos_cos",
        "severe_loss_weighted_pos_cos",
        "max_severe_pos_cos",
        "poscos_e323",
        "poscos_e216",
        "poscos_e267",
        "poscos_e256",
    ]
    for col in risk_cols:
        if col not in scores:
            scores[col] = 0.0
        if col not in nulls:
            nulls[col] = 0.0
    agg_rows: list[dict[str, Any]] = []
    for rec in scores.to_dict("records"):
        part = nulls[nulls["basename"].eq(rec["basename"])]
        item: dict[str, Any] = {"basename": rec["basename"]}
        for col in risk_cols:
            item[f"{col}_null_p90"] = float(part[col].quantile(0.90))
            item[f"{col}_dominance_lower_is_better"] = float(np.mean(float(rec[col]) < part[col].to_numpy(dtype=float)))
        agg_rows.append(item)
    agg = pd.DataFrame(agg_rows)
    scores = scores.merge(agg, on="basename", how="left")
    dominance_cols = [c for c in scores.columns if c.endswith("_dominance_lower_is_better")]
    scores["public_analog_survival_score"] = scores[dominance_cols].fillna(0.0).mean(axis=1)
    scores["public_analog_risk_score"] = (
        scores["public_loss_weighted_pos_cos"].fillna(0.0)
        + scores["severe_loss_weighted_pos_cos"].fillna(0.0)
        + scores["max_severe_pos_cos"].fillna(0.0)
        + scores.get("poscos_e323", 0.0)
        + scores.get("poscos_e216", 0.0)
    )
    scores.to_csv(PUBLIC_ANALOG_OUT, index=False)
    return scores


def add_plateau_metrics(scores: pd.DataFrame) -> pd.DataFrame:
    out = scores.copy()
    canonical_e347 = out[out["variant"].eq("canonical_e347")].iloc[0]
    canonical_e349 = out[out["variant"].eq("canonical_e349")].iloc[0]
    risk_cols = ["poscos_e323", "poscos_e216", "poscos_e267", "poscos_e256"]
    for col in risk_cols:
        if col not in out:
            out[col] = 0.0
    out["direct_bad_poscos_sum"] = out[risk_cols].fillna(0.0).sum(axis=1)
    out["selector_not_worse_than_e347"] = out["pred_delta_vs_current_p90"].fillna(1.0) <= float(canonical_e347["pred_delta_vs_current_p90"]) + 2.0e-7
    out["risk_not_worse_than_e347"] = out["public_analog_risk_score"].fillna(9.0) <= float(canonical_e347["public_analog_risk_score"]) + 0.0005
    out["specificity_not_worse_than_e347"] = out["q1_specificity_margin"].fillna(-9.0) >= float(canonical_e347["q1_specificity_margin"]) - 0.05
    out["risk_not_worse_than_e349"] = out["public_analog_risk_score"].fillna(9.0) <= float(canonical_e349["public_analog_risk_score"]) + 0.0005
    out["selector_not_worse_than_e349"] = out["pred_delta_vs_current_p90"].fillna(1.0) <= float(canonical_e349["pred_delta_vs_current_p90"]) + 2.0e-7
    out["specificity_not_worse_than_e349"] = out["q1_specificity_margin"].fillna(-9.0) >= float(canonical_e349["q1_specificity_margin"]) - 0.05
    out["e350_local_gate"] = (
        out["strict_promote_gate"].fillna(False).astype(bool)
        & (out["pred_delta_vs_current_p90"].fillna(1.0) < -0.00005)
        & (out["incremental_bad_axis_vs_current"].fillna(9.0).abs() <= 0.015)
        & out["risk_not_worse_than_e347"]
        & out["q1_specificity_pass"].fillna(False).astype(bool)
        & (~out["broad_state_not_specific"].fillna(True).astype(bool))
        & (out["direct_bad_poscos_sum"].fillna(0.0) <= 1.0e-9)
    )

    primary = out["target_set"].eq("compact_s3tail")
    generated = primary & ~out["variant"].isin(["canonical_e347", "canonical_e349"])
    support_cols = {
        "same_threshold_scale_support": [],
        "same_alpha_threshold_support": [],
        "near_threshold_support": [],
        "alpha_support": [],
    }
    for rec in out.to_dict("records"):
        if rec["target_set"] != "compact_s3tail":
            for values in support_cols.values():
                values.append(0)
            continue
        t = float(rec.get("threshold_frac", -999.0))
        s = float(rec.get("scale", -999.0))
        a = float(rec.get("s3_alpha", -999.0))
        pool = out[primary & generated & out["e350_local_gate"]]
        same_threshold = pool[np.isclose(pool["threshold_frac"].astype(float), t)]
        same_alpha = pool[np.isclose(pool["s3_alpha"].astype(float), a)]
        near_threshold = same_alpha[(same_alpha["threshold_frac"].astype(float) - t).abs() <= 10.0]
        same_alpha_threshold = same_alpha[np.isclose(same_alpha["scale"].astype(float), s)]
        alpha_near = pool[
            np.isclose(pool["threshold_frac"].astype(float), t)
            & np.isclose(pool["scale"].astype(float), s)
        ]
        support_cols["same_threshold_scale_support"].append(int(same_threshold["scale"].nunique()))
        support_cols["same_alpha_threshold_support"].append(int(same_alpha_threshold["threshold_frac"].nunique()))
        support_cols["near_threshold_support"].append(int(len(near_threshold)))
        support_cols["alpha_support"].append(int(alpha_near["s3_alpha"].nunique()))
    for col, values in support_cols.items():
        out[col] = values
    out["plateau_support_score"] = (
        out["same_threshold_scale_support"].fillna(0)
        + out["same_alpha_threshold_support"].fillna(0)
        + out["near_threshold_support"].fillna(0)
        + out["alpha_support"].fillna(0)
    )

    out["e350_plateau_gate"] = (
        out["e350_local_gate"]
        & generated
        & (out["prob_l1_delta_vs_e347"].fillna(0.0) >= 0.001)
        & (out["changed_cells_vs_e347"].fillna(0) >= 100)
        & out["selector_not_worse_than_e347"]
        & out["specificity_not_worse_than_e347"]
        & out["risk_not_worse_than_e349"]
        & (out["same_threshold_scale_support"].fillna(0) >= 2)
        & (out["near_threshold_support"].fillna(0) >= 4)
        & (out["alpha_support"].fillna(0) >= 2)
    )
    out["e350_rank_score"] = (
        0.28 * out["plateau_support_score"].fillna(0.0)
        + 2.50 * out["state_specificity_score"].fillna(0.0)
        + 1.75 * out["public_analog_survival_score"].fillna(0.0)
        - 12.0 * out["public_analog_risk_score"].fillna(1.0)
        - 1200.0 * out["pred_delta_vs_current_p90"].fillna(0.0)
        - 20.0 * out["incremental_bad_axis_vs_current"].fillna(0.0).abs()
        - 5.0 * out["direct_bad_poscos_sum"].fillna(0.0)
        + 0.50 * out["q1_specificity_margin"].fillna(0.0)
        + 0.15 * np.log1p(100.0 * out["prob_l1_delta_vs_e347"].fillna(0.0))
    )
    return out.sort_values(
        ["e350_plateau_gate", "e350_local_gate", "e350_rank_score"],
        ascending=[False, False, False],
    ).reset_index(drop=True)


def combined_scores(candidates: pd.DataFrame, base: pd.DataFrame, base_logit: np.ndarray, latent: pd.DataFrame, state_cols: list[str], residual_cols: list[str], calendar_cols: list[str]) -> pd.DataFrame:
    sample = base[KEYS].copy()
    known, refs, ref_vecs = build_known_and_refs(sample)
    files = [CURRENT] + candidates["file"].astype(str).tolist()
    e272_candidates = build_features(files, sample, refs, ref_vecs)
    model_df = evaluate_models(known)
    selector = score_candidates(known, e272_candidates, model_df)

    public_scores = score_public_analog(candidates, base, base_logit)
    spec_rows: list[dict[str, Any]] = []
    e347_prob = load_candidate(E347_UPLOAD, base[KEYS])[TARGETS].to_numpy(dtype=np.float64)
    e349_prob = load_candidate(E349_UPLOAD, base[KEYS])[TARGETS].to_numpy(dtype=np.float64)
    diff_rows: list[dict[str, Any]] = []
    for rec in candidates.to_dict("records"):
        path = locate(rec["file"])
        pred = load_candidate(path, base[KEYS])
        pred_prob = pred[TARGETS].to_numpy(dtype=np.float64)
        delta = logit(pred_prob) - base_logit
        spec_rows.append({"basename": rec["basename"], **specificity_metrics(delta, latent, state_cols, residual_cols, calendar_cols, rec["basename"])})
        diff347 = np.abs(pred_prob - e347_prob)
        diff349 = np.abs(pred_prob - e349_prob)
        diff_rows.append(
            {
                "basename": rec["basename"],
                "prob_l1_delta_vs_e347": float(diff347.sum()),
                "prob_mean_abs_delta_vs_e347": float(diff347.mean()),
                "prob_max_abs_delta_vs_e347": float(diff347.max()),
                "changed_cells_vs_e347": int((diff347 > 1.0e-12).sum()),
                "changed_rows_vs_e347": int((diff347.max(axis=1) > 1.0e-12).sum()),
                "prob_l1_delta_vs_e349": float(diff349.sum()),
                "prob_mean_abs_delta_vs_e349": float(diff349.mean()),
                "prob_max_abs_delta_vs_e349": float(diff349.max()),
                "changed_cells_vs_e349": int((diff349 > 1.0e-12).sum()),
                "changed_rows_vs_e349": int((diff349.max(axis=1) > 1.0e-12).sum()),
            }
        )

    scores = candidates.merge(selector, on="basename", how="left", suffixes=("", "_selector"))
    scores = scores.merge(public_scores, on="basename", how="left", suffixes=("", "_public"))
    scores = scores.merge(pd.DataFrame(spec_rows), on="basename", how="left")
    scores = scores.merge(pd.DataFrame(diff_rows), on="basename", how="left")
    return add_plateau_metrics(scores)


def materialize_selection(scores: pd.DataFrame) -> Path | None:
    selected = scores[scores["e350_plateau_gate"].astype(bool)].head(1)
    if selected.empty:
        return None
    rec = selected.iloc[0]
    src = locate(rec["file"])
    frame = pd.read_csv(src)
    for target in TARGETS:
        frame[target] = clip_prob(frame[target].to_numpy(dtype=np.float64))
    out = OUT / f"{UPLOAD_PREFIX}_selected_{safe_id(str(rec['variant']), 56)}_{short_hash(frame)}_uploadsafe.csv"
    if src.resolve() != out.resolve():
        frame.to_csv(out, index=False)
    scores.loc[scores["basename"].eq(rec["basename"]), "selected_uploadsafe_file"] = rel(out)
    return out


def write_report(scores: pd.DataFrame, selected_path: Path | None) -> None:
    canonical = scores[scores["variant"].isin(["canonical_e347", "canonical_e349"])].copy()
    plateau = scores[scores["e350_plateau_gate"].astype(bool)].copy()
    local = scores[scores["e350_local_gate"].astype(bool)].copy()
    top_cols = [
        "variant",
        "target_set",
        "threshold_frac",
        "scale",
        "s3_alpha",
        "e350_plateau_gate",
        "e350_local_gate",
        "plateau_support_score",
        "same_threshold_scale_support",
        "near_threshold_support",
        "alpha_support",
        "pred_delta_vs_current_mean",
        "pred_delta_vs_current_p90",
        "pred_beats_current_rate",
        "incremental_bad_axis_vs_current",
        "public_analog_survival_score",
        "public_analog_risk_score",
        "direct_bad_poscos_sum",
        "q1_state_corr_abs",
        "q1_specificity_margin",
        "q1_broader_specificity_margin",
        "top_target_q1_state",
        "changed_cells_vs_e247",
        "changed_cells_vs_e347",
        "changed_cells_vs_e349",
        "prob_l1_delta_vs_e347",
        "prob_l1_delta_vs_e349",
        "selected_uploadsafe_file",
    ]
    top_cols = [c for c in top_cols if c in scores.columns]
    summary = (
        scores.groupby(["target_set", "s3_alpha"], dropna=False)
        .agg(
            n=("basename", "count"),
            local_gate_rate=("e350_local_gate", "mean"),
            plateau_gate_rate=("e350_plateau_gate", "mean"),
            best_p90=("pred_delta_vs_current_p90", "min"),
            best_risk=("public_analog_risk_score", "min"),
            best_q1_margin=("q1_specificity_margin", "max"),
            median_support=("plateau_support_score", "median"),
        )
        .reset_index()
        .sort_values(["plateau_gate_rate", "local_gate_rate", "best_p90"], ascending=[False, False, True])
    )
    selected_text = rel(selected_path) if selected_path is not None else "none"
    lines = [
        "# E350 Compact Hidden Lifestyle-State Plateau Stress",
        "",
        "## Question",
        "",
        "Is the E349 Q1/Q2/Q3/S1 compact lifestyle-state candidate a stable basin, or a one-threshold accident?",
        "",
        "## Method",
        "",
        "- Base: E247 public-best submission.",
        "- Action: logit(E347) - logit(E247).",
        "- View: compact Q1/Q2/Q3/S1 lifestyle-state movement with optional S3-tail restoration.",
        "- Stress: E272 public-free selector, E346 public-bad-axis analog, Q1 dateblock latent specificity, and local threshold/scale/S3-alpha plateau support.",
        "- Public LB is not used.",
        "",
        "## Decision",
        "",
        f"- candidates tested: `{len(scores)}`",
        f"- local gate pass count: `{int(scores['e350_local_gate'].sum())}`",
        f"- plateau gate pass count: `{int(scores['e350_plateau_gate'].sum())}`",
        f"- selected upload-safe candidate: `{selected_text}`",
        "",
    ]
    if selected_path is None:
        lines.extend(
            [
                "No neighboring compact-state variant passed the plateau gate.",
                "Interpretation: E349 may still be useful, but this scan does not justify moving away from it without a new state view.",
            ]
        )
    else:
        lines.extend(
            [
                "A neighboring compact-state variant passed local stress and plateau support.",
                "Interpretation: the Q1/Q2/Q3/S1 lifestyle-state action is not a single exact-threshold artifact; the S3-tail/scale neighborhood now has a testable next candidate.",
            ]
        )
    lines.extend(
        [
            "",
            "## References",
            "",
            md_table(canonical[top_cols], n=5, floatfmt=".9f"),
            "",
            "## Top Candidates",
            "",
            md_table(scores[top_cols], n=40, floatfmt=".9f"),
            "",
            "## Plateau-Gate Candidates",
            "",
            md_table(plateau[top_cols], n=40, floatfmt=".9f"),
            "",
            "## Local-Gate Candidates",
            "",
            md_table(local[top_cols], n=60, floatfmt=".9f"),
            "",
            "## Target/S3-Alpha Summary",
            "",
            md_table(summary, n=60, floatfmt=".9f"),
            "",
            "## Files",
            "",
            f"- `{rel(CANDIDATE_OUT)}`",
            f"- `{rel(SCORE_OUT)}`",
            f"- `{rel(PUBLIC_ANALOG_OUT)}`",
            f"- `{rel(REPORT_OUT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    base = load_sub(OUT / CURRENT).sort_values(KEYS).reset_index(drop=True)
    sample = normalize_dates(base[KEYS].copy())
    base_logit = logit(base[TARGETS].to_numpy(dtype=np.float64))
    e347 = load_candidate(E347_UPLOAD, sample)
    e349 = load_candidate(E349_UPLOAD, sample)
    latent, state_cols, residual_cols, calendar_cols = load_lifestyle_teacher(sample)
    if Q1_STATE_COL not in latent.columns:
        raise RuntimeError(f"missing latent column: {Q1_STATE_COL}")

    candidates = create_candidates(base, base_logit, e347, e349)
    scores = combined_scores(candidates, base, base_logit, latent, state_cols, residual_cols, calendar_cols)
    scores["selected_uploadsafe_file"] = ""
    selected_path = materialize_selection(scores)
    scores.to_csv(SCORE_OUT, index=False)
    write_report(scores, selected_path)

    print(f"wrote {rel(CANDIDATE_OUT)} {candidates.shape}")
    print(f"wrote {rel(PUBLIC_ANALOG_OUT)}")
    print(f"wrote {rel(SCORE_OUT)} {scores.shape}")
    print(f"wrote {rel(REPORT_OUT)}")
    print(f"selected {rel(selected_path) if selected_path else 'none'}")
    print(
        scores[
            [
                "variant",
                "target_set",
                "threshold_frac",
                "scale",
                "s3_alpha",
                "e350_plateau_gate",
                "e350_local_gate",
                "plateau_support_score",
                "pred_delta_vs_current_p90",
                "public_analog_risk_score",
                "q1_specificity_margin",
            ]
        ]
        .head(25)
        .round(9)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
