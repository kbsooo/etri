#!/usr/bin/env python3
"""E349: target/cell ablation stress for the E347 lifestyle-state move.

Question:
    Is the E347 hidden lifestyle-state action carried by a separable target or
    cell slice, or does it only make sense as the full coupled Q/S movement?

The experiment treats the E347-vs-E247 logit delta as an "action view" over a
learned lifestyle state.  It creates masked/scaled variants of that action and
scores them with the existing public-free selector, public-bad-axis analog
stress, and Q1 dateblock latent specificity controls.

No public LB feedback is used.
"""

from __future__ import annotations

import hashlib
import shutil
import sys
import warnings
from pathlib import Path
from typing import Any, Iterable

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
from public_anchor_bottleneck_decomposition import KEYS, TARGETS, load_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


RNG_SEED = 20260531 + 349
EPS = 1.0e-12
NULL_REPS = 8
Q1_STATE_COL = "rs01_Q1_jepa_resid_dateblock"

E347_UPLOAD = OUT / "submission_e347_stateful_counteraxis_lifestyle_e344_nullsafe_top5_e131968c_uploadsafe.csv"
OBS_AXIS_IN = OUT / "e346_public_analog_observed_axes.csv"

CANDIDATE_OUT = OUT / "e349_e347_target_cell_ablation_candidates.csv"
SCORE_OUT = OUT / "e349_e347_target_cell_ablation_scores.csv"
PUBLIC_ANALOG_OUT = OUT / "e349_e347_target_cell_ablation_public_analog.csv"
REPORT_OUT = OUT / "e349_e347_target_cell_ablation_report.md"
UPLOAD_PREFIX = "submission_e349_lifestate_ablate"


def stable_seed(*parts: object) -> int:
    text = "|".join(map(str, parts))
    return RNG_SEED + int(hashlib.sha1(text.encode("utf-8")).hexdigest()[:8], 16) % 100000


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def short_hash(frame: pd.DataFrame) -> str:
    arr = np.asarray(frame[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def signed_spearman(a: np.ndarray, b: np.ndarray) -> float:
    corr = pd.Series(np.asarray(a, dtype=np.float64)).corr(
        pd.Series(np.asarray(b, dtype=np.float64)),
        method="spearman",
    )
    return 0.0 if not np.isfinite(corr) else float(corr)


def spearman_abs(a: np.ndarray, b: np.ndarray) -> float:
    return abs(signed_spearman(a, b))


def max_view_corr(score: np.ndarray, latent: pd.DataFrame, cols: Iterable[str]) -> tuple[float, str, float]:
    vals: list[tuple[float, str, float]] = []
    for col in cols:
        signed = signed_spearman(score, latent[col].to_numpy(dtype=np.float64))
        vals.append((abs(signed), col, signed))
    if not vals:
        return 0.0, "", 0.0
    vals.sort(key=lambda item: item[0], reverse=True)
    return vals[0]


def top_enrichment_abs(score: np.ndarray, latent: pd.DataFrame, col: str) -> float:
    x = np.asarray(score, dtype=np.float64)
    if np.max(x) <= EPS:
        return 0.0
    k = min(max(16, int(np.ceil(0.20 * len(x)))), len(x) - 1)
    active = np.zeros(len(x), dtype=bool)
    active[np.argsort(-x)[:k]] = True
    arr = latent[col].to_numpy(dtype=np.float64)
    return abs(float(np.mean(arr[active]) - np.mean(arr[~active])))


def movement_entropy(weights: np.ndarray) -> float:
    x = np.abs(np.asarray(weights, dtype=np.float64))
    total = float(x.sum())
    if total <= EPS:
        return 0.0
    p = x / total
    nz = p[p > 0.0]
    return float(-(nz * np.log(nz)).sum() / np.log(len(p))) if len(p) > 1 else 0.0


def target_mask(names: Iterable[str]) -> np.ndarray:
    keep = set(names)
    return np.asarray([target in keep for target in TARGETS], dtype=float)[None, :]


def row_mask_from_score(score: np.ndarray, mode: str) -> np.ndarray:
    x = np.asarray(score, dtype=np.float64)
    if mode == "all":
        return np.ones((len(x), 1), dtype=float)
    if mode.startswith("abs_top"):
        frac = float(mode.replace("abs_top", "")) / 100.0
        thresh = np.quantile(np.abs(x), 1.0 - frac)
        return (np.abs(x) >= thresh).astype(float)[:, None]
    if mode.startswith("pos_top"):
        frac = float(mode.replace("pos_top", "")) / 100.0
        thresh = np.quantile(x, 1.0 - frac)
        return (x >= thresh).astype(float)[:, None]
    if mode.startswith("neg_bot"):
        frac = float(mode.replace("neg_bot", "")) / 100.0
        thresh = np.quantile(x, frac)
        return (x <= thresh).astype(float)[:, None]
    raise ValueError(mode)


def cell_keep_mask(delta: np.ndarray, mode: str) -> np.ndarray:
    if mode == "all":
        return np.ones_like(delta)
    arr = np.asarray(delta, dtype=np.float64)
    if mode.startswith("abs_top"):
        frac = float(mode.replace("abs_top", "")) / 100.0
        nonzero = np.abs(arr[np.abs(arr) > EPS])
        if len(nonzero) == 0:
            return np.zeros_like(arr)
        thresh = np.quantile(nonzero, 1.0 - frac)
        return (np.abs(arr) >= thresh).astype(float)
    if mode == "positive_only":
        return (arr > EPS).astype(float)
    if mode == "negative_only":
        return (arr < -EPS).astype(float)
    raise ValueError(mode)


def target_sets() -> dict[str, list[str]]:
    return {
        "all": TARGETS,
        "q1": ["Q1"],
        "q2": ["Q2"],
        "q3": ["Q3"],
        "s1": ["S1"],
        "s2": ["S2"],
        "s3": ["S3"],
        "s4": ["S4"],
        "q1q2": ["Q1", "Q2"],
        "q1q3": ["Q1", "Q3"],
        "q1q2q3": ["Q1", "Q2", "Q3"],
        "q1q2s1": ["Q1", "Q2", "S1"],
        "q1q2q3s1": ["Q1", "Q2", "Q3", "S1"],
        "q1q2s1s3": ["Q1", "Q2", "S1", "S3"],
        "qonly": ["Q1", "Q2", "Q3"],
        "sonly": ["S1", "S2", "S3", "S4"],
        "noq1": [t for t in TARGETS if t != "Q1"],
        "noq2": [t for t in TARGETS if t != "Q2"],
        "noq3": [t for t in TARGETS if t != "Q3"],
        "nos1": [t for t in TARGETS if t != "S1"],
        "nos3": [t for t in TARGETS if t != "S3"],
    }


def variant_specs(q1_state: np.ndarray, delta: np.ndarray) -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = []
    target_map = target_sets()
    for target_name, targets in target_map.items():
        for scale in [0.50, 0.75, 1.00, 1.15]:
            specs.append(
                {
                    "variant": f"target_{target_name}_s{scale:.2f}",
                    "target_set": target_name,
                    "row_mask": "all",
                    "cell_mask": "all",
                    "sign_mask": "both",
                    "scale": scale,
                    "targets": targets,
                }
            )

    for target_name in ["all", "q1", "q1q2", "q1q2s1", "q1q2q3s1", "qonly"]:
        for row_mode in ["abs_top80", "abs_top60", "abs_top40", "abs_top25", "pos_top40", "neg_bot40"]:
            specs.append(
                {
                    "variant": f"row_{row_mode}_{target_name}",
                    "target_set": target_name,
                    "row_mask": row_mode,
                    "cell_mask": "all",
                    "sign_mask": "both",
                    "scale": 1.00,
                    "targets": target_map[target_name],
                }
            )

    for target_name in ["all", "q1q2", "q1q2s1", "q1q2q3s1", "qonly"]:
        for cell_mode in ["abs_top80", "abs_top65", "abs_top50", "abs_top35", "positive_only", "negative_only"]:
            specs.append(
                {
                    "variant": f"cell_{cell_mode}_{target_name}",
                    "target_set": target_name,
                    "row_mask": "all",
                    "cell_mask": cell_mode,
                    "sign_mask": cell_mode if cell_mode.endswith("_only") else "both",
                    "scale": 1.00,
                    "targets": target_map[target_name],
                }
            )

    movement = np.sqrt(np.mean(delta**2, axis=1))
    for score_name, score in [("q1state", q1_state), ("movement", movement)]:
        for target_name in ["all", "q1q2s1", "qonly"]:
            for frac in ["abs_top60", "abs_top40"]:
                specs.append(
                    {
                        "variant": f"{score_name}_{frac}_{target_name}_s0.90",
                        "target_set": target_name,
                        "row_mask": frac,
                        "cell_mask": "all",
                        "sign_mask": "both",
                        "scale": 0.90,
                        "targets": target_map[target_name],
                        "row_score_override": score_name,
                    }
                )

    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for spec in specs:
        key = spec["variant"]
        if key in seen:
            continue
        seen.add(key)
        out.append(spec)
    return out


def write_submission(base: pd.DataFrame, base_logit: np.ndarray, delta: np.ndarray, spec: dict[str, Any], q1_state: np.ndarray) -> tuple[Path, dict[str, Any]]:
    target_m = target_mask(spec["targets"])
    row_score = q1_state
    if spec.get("row_score_override") == "movement":
        row_score = np.sqrt(np.mean(delta**2, axis=1))
    row_m = row_mask_from_score(row_score, spec["row_mask"])
    cell_m = cell_keep_mask(delta, spec["cell_mask"])
    masked_delta = delta * target_m * row_m * cell_m * float(spec["scale"])
    out = base[KEYS].copy()
    out[TARGETS] = clip_prob(sigmoid(base_logit + masked_delta))
    tag = safe_id(spec["variant"], 72)
    path = OUT / f"{UPLOAD_PREFIX}_{tag}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    meta = {
        **{k: v for k, v in spec.items() if k != "targets"},
        "targets": ",".join(spec["targets"]),
        "file": rel(path),
        "basename": path.name,
        "changed_rows_vs_e247": int((np.abs(masked_delta).sum(axis=1) > EPS).sum()),
        "changed_cells_vs_e247": int((np.abs(masked_delta) > EPS).sum()),
        "move_l1": float(np.abs(masked_delta).sum()),
        "move_l2": float(np.linalg.norm(masked_delta.reshape(-1))),
        "row_entropy": movement_entropy(np.abs(masked_delta).sum(axis=1)),
    }
    for i, target in enumerate(TARGETS):
        meta[f"abs_{target}"] = float(np.abs(masked_delta[:, i]).sum())
    return path, meta


def create_candidates(base: pd.DataFrame, base_logit: np.ndarray, e347: pd.DataFrame, latent: pd.DataFrame) -> pd.DataFrame:
    q1_state = latent[Q1_STATE_COL].to_numpy(dtype=np.float64)
    e347_delta = logit(e347[TARGETS].to_numpy(dtype=np.float64)) - base_logit
    rows: list[dict[str, Any]] = [
        {
            "variant": "canonical_e347",
            "target_set": "all",
            "row_mask": "all",
            "cell_mask": "all",
            "sign_mask": "both",
            "scale": 1.00,
            "targets": ",".join(TARGETS),
            "file": rel(E347_UPLOAD),
            "basename": E347_UPLOAD.name,
            "changed_rows_vs_e247": int((np.abs(e347_delta).sum(axis=1) > EPS).sum()),
            "changed_cells_vs_e247": int((np.abs(e347_delta) > EPS).sum()),
            "move_l1": float(np.abs(e347_delta).sum()),
            "move_l2": float(np.linalg.norm(e347_delta.reshape(-1))),
            "row_entropy": movement_entropy(np.abs(e347_delta).sum(axis=1)),
            **{f"abs_{target}": float(np.abs(e347_delta[:, i]).sum()) for i, target in enumerate(TARGETS)},
        }
    ]
    hashes = {short_hash(e347)}
    for spec in variant_specs(q1_state, e347_delta):
        path, meta = write_submission(base, base_logit, e347_delta, spec, q1_state)
        frame_hash = path.stem.rsplit("_", 1)[-1]
        if frame_hash in hashes:
            path.unlink(missing_ok=True)
            continue
        hashes.add(frame_hash)
        rows.append(meta)
    out = pd.DataFrame(rows).sort_values(["variant", "basename"]).reset_index(drop=True)
    out.to_csv(CANDIDATE_OUT, index=False)
    return out


def specificity_metrics(delta: np.ndarray, latent: pd.DataFrame, state_cols: list[str], residual_cols: list[str], calendar_cols: list[str], seed_key: str) -> dict[str, Any]:
    row_l2 = np.sqrt(np.mean(delta**2, axis=1))
    q1_state = latent[Q1_STATE_COL].to_numpy(dtype=np.float64)
    own_cols = [c for c in state_cols if c not in residual_cols]
    nonq1_cols = [c for c in residual_cols if c != Q1_STATE_COL]

    q1_corr = spearman_abs(row_l2, q1_state)
    q1_signed = signed_spearman(row_l2, q1_state)
    q1_enrich = top_enrichment_abs(row_l2, latent, Q1_STATE_COL)
    own_corr, own_col, _ = max_view_corr(row_l2, latent, own_cols)
    nonq1_corr, nonq1_col, _ = max_view_corr(row_l2, latent, nonq1_cols)
    calendar_corr, calendar_col, _ = max_view_corr(row_l2, latent, calendar_cols)
    target_corrs = {target: spearman_abs(np.abs(delta[:, i]), q1_state) for i, target in enumerate(TARGETS)}
    top_target = max(target_corrs.items(), key=lambda item: item[1])

    rng = np.random.default_rng(stable_seed("specificity", seed_key))
    random_corrs = [spearman_abs(row_l2, rng.normal(size=len(row_l2))) for _ in range(64)]
    perm_corrs = [spearman_abs(row_l2, q1_state[rng.permutation(len(q1_state))]) for _ in range(64)]
    random_p95 = float(np.quantile(random_corrs, 0.95))
    perm_p95 = float(np.quantile(perm_corrs, 0.95))
    negative_control = max(calendar_corr, random_p95, perm_p95)
    broader_control = max(own_corr, nonq1_corr, calendar_corr, random_p95, perm_p95)
    q1_margin = q1_corr - negative_control
    broader_margin = q1_corr - broader_control
    specificity_score = float(
        0.30 * min(max(q1_corr / 0.35, 0.0), 1.0)
        + 0.20 * min(max(q1_enrich / 0.75, 0.0), 1.0)
        + 0.20 * min(max(q1_margin / 0.10, 0.0), 1.0)
        + 0.15 * float(q1_corr >= perm_p95 + 0.03)
        + 0.15 * float(q1_corr >= calendar_corr + 0.03)
    )
    return {
        "q1_state_corr_abs": q1_corr,
        "q1_state_corr_signed": q1_signed,
        "q1_state_enrich_abs": q1_enrich,
        "own_state_corr_abs": own_corr,
        "own_state_corr_col": own_col,
        "nonq1_residual_corr_abs": nonq1_corr,
        "nonq1_residual_corr_col": nonq1_col,
        "calendar_corr_abs": calendar_corr,
        "calendar_corr_col": calendar_col,
        "random_corr_p95": random_p95,
        "permuted_q1_corr_p95": perm_p95,
        "q1_specificity_margin": q1_margin,
        "q1_broader_specificity_margin": broader_margin,
        "q1_specificity_pass": bool(q1_corr >= perm_p95 + 0.03 and q1_corr >= calendar_corr + 0.03),
        "broad_state_not_specific": bool(broader_margin <= 0.02),
        "state_specificity_score": specificity_score,
        "top_target_q1_state": top_target[0],
        "top_target_q1_state_corr_abs": top_target[1],
        **{f"{target}_q1_state_corr_abs": value for target, value in target_corrs.items()},
    }


def score_public_analog(candidates: pd.DataFrame, base: pd.DataFrame, base_logit: np.ndarray) -> pd.DataFrame:
    obs_axes = pd.read_csv(OBS_AXIS_IN)
    axes = axis_records(obs_axes, base, base_logit)
    meta = test_meta(base)
    modes = ["row_perm", "target_perm", "sign_flip", "row_sign", "cell_perm", "subject_perm", "dateblock_perm"]
    rows: list[dict[str, Any]] = []
    null_rows: list[dict[str, Any]] = []
    for rec in candidates.to_dict("records"):
        path = ROOT / str(rec["file"])
        if not path.exists():
            path = OUT / str(rec["basename"])
        pred = load_candidate(path, base[KEYS])
        delta = logit(pred[TARGETS].to_numpy(dtype=np.float64)) - base_logit
        actual = public_analog_metrics(delta, axes)
        rows.append({"basename": rec["basename"], **actual})
        for mode in modes:
            for rep in range(NULL_REPS):
                nd = null_delta(delta, mode, meta, stable_seed(rec["basename"], mode, rep))
                metrics = public_analog_metrics(nd, axes)
                null_rows.append({"basename": rec["basename"], "mode": mode, "rep": rep, **metrics})

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


def combined_scores(candidates: pd.DataFrame, base: pd.DataFrame, base_logit: np.ndarray, latent: pd.DataFrame, state_cols: list[str], residual_cols: list[str], calendar_cols: list[str]) -> pd.DataFrame:
    sample = base[KEYS].copy()
    known, refs, ref_vecs = build_known_and_refs(sample)
    files = [CURRENT] + candidates["file"].astype(str).tolist()
    e272_candidates = build_features(files, sample, refs, ref_vecs)
    model_df = evaluate_models(known)
    selector = score_candidates(known, e272_candidates, model_df)

    public_scores = score_public_analog(candidates, base, base_logit)
    spec_rows: list[dict[str, Any]] = []
    for rec in candidates.to_dict("records"):
        path = ROOT / str(rec["file"])
        if not path.exists():
            path = OUT / str(rec["basename"])
        pred = load_candidate(path, base[KEYS])
        delta = logit(pred[TARGETS].to_numpy(dtype=np.float64)) - base_logit
        spec_rows.append({"basename": rec["basename"], **specificity_metrics(delta, latent, state_cols, residual_cols, calendar_cols, rec["basename"])})
    spec = pd.DataFrame(spec_rows)
    e347_prob = load_candidate(E347_UPLOAD, base[KEYS])[TARGETS].to_numpy(dtype=np.float64)
    diff_rows: list[dict[str, Any]] = []
    for rec in candidates.to_dict("records"):
        path = ROOT / str(rec["file"])
        if not path.exists():
            path = OUT / str(rec["basename"])
        pred = load_candidate(path, base[KEYS])[TARGETS].to_numpy(dtype=np.float64)
        diff = np.abs(pred - e347_prob)
        diff_rows.append(
            {
                "basename": rec["basename"],
                "prob_l1_delta_vs_e347": float(diff.sum()),
                "prob_mean_abs_delta_vs_e347": float(diff.mean()),
                "prob_max_abs_delta_vs_e347": float(diff.max()),
                "changed_cells_vs_e347": int((diff > 1.0e-12).sum()),
                "changed_rows_vs_e347": int((diff.max(axis=1) > 1.0e-12).sum()),
            }
        )
    diff_scores = pd.DataFrame(diff_rows)

    scores = candidates.merge(selector, on="basename", how="left", suffixes=("", "_selector"))
    scores = scores.merge(public_scores, on="basename", how="left", suffixes=("", "_public"))
    scores = scores.merge(spec, on="basename", how="left")
    scores = scores.merge(diff_scores, on="basename", how="left")

    canonical = scores[scores["variant"].eq("canonical_e347")].iloc[0]
    risk_cols = ["poscos_e323", "poscos_e216", "poscos_e267", "poscos_e256"]
    for col in risk_cols:
        if col not in scores:
            scores[col] = 0.0
    scores["direct_bad_poscos_sum"] = scores[risk_cols].fillna(0.0).sum(axis=1)
    scores["selector_not_worse_than_e347"] = scores["pred_delta_vs_current_p90"].fillna(1.0) <= float(canonical["pred_delta_vs_current_p90"]) + 2.0e-7
    scores["risk_not_worse_than_e347"] = scores["public_analog_risk_score"].fillna(9.0) <= float(canonical["public_analog_risk_score"]) + 0.0005
    scores["specificity_not_worse_than_e347"] = scores["q1_specificity_margin"].fillna(-9.0) >= float(canonical["q1_specificity_margin"]) - 0.05
    scores["e349_gate"] = (
        scores["strict_promote_gate"].fillna(False).astype(bool)
        & (scores["pred_delta_vs_current_p90"].fillna(1.0) < -0.00005)
        & (scores["incremental_bad_axis_vs_current"].fillna(9.0).abs() <= 0.015)
        & scores["risk_not_worse_than_e347"]
        & scores["q1_specificity_pass"].fillna(False).astype(bool)
        & (~scores["broad_state_not_specific"].fillna(True).astype(bool))
        & (scores["direct_bad_poscos_sum"].fillna(0.0) <= 1.0e-9)
    )
    scores["e349_replacement_gate"] = (
        scores["e349_gate"]
        & ~scores["variant"].eq("canonical_e347")
        & (scores["prob_l1_delta_vs_e347"].fillna(0.0) >= 0.001)
        & (scores["changed_cells_vs_e347"].fillna(0) >= 100)
        & scores["selector_not_worse_than_e347"]
        & scores["specificity_not_worse_than_e347"]
        & (
            (scores["public_analog_risk_score"] <= float(canonical["public_analog_risk_score"]) - 0.0005)
            | (scores["public_analog_survival_score"] >= float(canonical["public_analog_survival_score"]) + 0.05)
        )
    )
    scores["e349_rank_score"] = (
        2.50 * scores["state_specificity_score"].fillna(0.0)
        + 1.75 * scores["public_analog_survival_score"].fillna(0.0)
        - 12.0 * scores["public_analog_risk_score"].fillna(1.0)
        - 1200.0 * scores["pred_delta_vs_current_p90"].fillna(0.0)
        - 20.0 * scores["incremental_bad_axis_vs_current"].fillna(0.0).abs()
        - 5.0 * scores["direct_bad_poscos_sum"].fillna(0.0)
        + 0.50 * scores["q1_specificity_margin"].fillna(0.0)
        + 0.20 * np.log1p(100.0 * scores["prob_l1_delta_vs_e347"].fillna(0.0))
    )
    return scores.sort_values(
        ["e349_replacement_gate", "e349_gate", "e349_rank_score"],
        ascending=[False, False, False],
    ).reset_index(drop=True)


def materialize_selection(scores: pd.DataFrame) -> Path | None:
    replacement = scores[scores["e349_replacement_gate"].astype(bool)].head(1)
    if replacement.empty:
        return None
    rec = replacement.iloc[0]
    src = ROOT / str(rec["file"])
    if not src.exists():
        src = OUT / str(rec["basename"])
    frame = pd.read_csv(src)
    for target in TARGETS:
        frame[target] = clip_prob(frame[target].to_numpy(dtype=np.float64))
    out = OUT / f"{UPLOAD_PREFIX}_selected_{safe_id(str(rec['variant']), 48)}_{short_hash(frame)}_uploadsafe.csv"
    if src.resolve() != out.resolve():
        frame.to_csv(out, index=False)
    scores.loc[scores["basename"].eq(rec["basename"]), "selected_uploadsafe_file"] = rel(out)
    return out


def write_report(scores: pd.DataFrame, selected_path: Path | None) -> None:
    canonical = scores[scores["variant"].eq("canonical_e347")].head(1)
    replacements = scores[scores["e349_replacement_gate"].astype(bool)].copy()
    gates = scores[scores["e349_gate"].astype(bool)].copy()
    target_summary = (
        scores.groupby("target_set", dropna=False)
        .agg(
            n=("basename", "count"),
            gate_rate=("e349_gate", "mean"),
            repl_rate=("e349_replacement_gate", "mean"),
            best_p90=("pred_delta_vs_current_p90", "min"),
            best_risk=("public_analog_risk_score", "min"),
            best_q1_margin=("q1_specificity_margin", "max"),
            median_q1_corr=("q1_state_corr_abs", "median"),
        )
        .reset_index()
        .sort_values(["repl_rate", "gate_rate", "best_p90"], ascending=[False, False, True])
    )
    top_cols = [
        "variant",
        "target_set",
        "row_mask",
        "cell_mask",
        "scale",
        "e349_replacement_gate",
        "e349_gate",
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
        "prob_l1_delta_vs_e347",
        "selected_uploadsafe_file",
    ]
    top_cols = [c for c in top_cols if c in scores.columns]
    selected_text = rel(selected_path) if selected_path is not None else "none"
    lines = [
        "# E349 E347 Target/Cell Ablation Stress",
        "",
        "## Question",
        "",
        "Can the E347 hidden lifestyle-state movement be improved by keeping only a target, row-state, cell-magnitude, or sign slice?",
        "",
        "## Method",
        "",
        "- Base: E247 public-best submission.",
        "- Action: logit(E347) - logit(E247).",
        "- Variants: target masks, Q1-state row masks, movement row masks, cell-magnitude masks, positive/negative sign masks, and mild scales.",
        "- Stress: E272 public-free selector, E346 public-bad-axis analog, and E348-style Q1 dateblock specificity controls.",
        "- Public LB is not used.",
        "",
        "## Decision",
        "",
        f"- replacement gate pass count: `{int(scores['e349_replacement_gate'].sum())}`",
        f"- general E349 gate pass count: `{int(scores['e349_gate'].sum())}`",
        f"- selected upload-safe replacement: `{selected_text}`",
        "",
    ]
    if selected_path is None:
        lines.extend(
            [
                "No ablated slice beats canonical E347 on the combined gate.",
                "Interpretation: the current E347 action is not just a single-target trick. Its local edge comes from a coupled Q/S movement aligned with the Q1 dateblock lifestyle state while avoiding known public-bad axes.",
            ]
        )
    else:
        lines.extend(
            [
                "A stricter ablated replacement survived the local selector, public-analog, and latent-specificity checks.",
                "This should be treated as the next public-information candidate, not as a guaranteed LB predictor.",
            ]
        )
    lines.extend(
        [
            "",
            "## Canonical E347 Reference",
            "",
            md_table(canonical[top_cols], n=3, floatfmt=".9f"),
            "",
            "## Top Candidates",
            "",
            md_table(scores[top_cols], n=30, floatfmt=".9f"),
            "",
            "## Replacement-Gate Candidates",
            "",
            md_table(replacements[top_cols], n=20, floatfmt=".9f"),
            "",
            "## General-Gate Candidates",
            "",
            md_table(gates[top_cols], n=30, floatfmt=".9f"),
            "",
            "## Target-Set Summary",
            "",
            md_table(target_summary, n=30, floatfmt=".9f"),
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
    latent, state_cols, residual_cols, calendar_cols = load_lifestyle_teacher(sample)
    if Q1_STATE_COL not in latent.columns:
        raise RuntimeError(f"missing latent column: {Q1_STATE_COL}")

    candidates = create_candidates(base, base_logit, e347, latent)
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
                "e349_replacement_gate",
                "e349_gate",
                "pred_delta_vs_current_p90",
                "public_analog_risk_score",
                "q1_specificity_margin",
            ]
        ]
        .head(20)
        .round(9)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
