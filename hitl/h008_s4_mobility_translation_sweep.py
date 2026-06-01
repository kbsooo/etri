#!/usr/bin/env python3
"""H008: broad translation sweep for the S4 mobility latent.

H007 made the important discovery: the HS-JEPA mobility latent is a robust S4
feature locally, but tiny direct postprocesses are below public-free selector
resolution.  H008 attacks the remaining bottleneck: the translator from latent
state to E247 submission movement.

We deliberately try many S4-only translators:
    - latent model delta, positive and signed
    - monotone high-mobility up shifts
    - high/low balanced rank moves
    - blend toward the latent S4 model
    - projection away from known public-bad S4 axes

No public LB is used.  The output is a selector-ranked map of which translator
families are promising, not an automatic submission claim.
"""

from __future__ import annotations

import hashlib
import shutil
import sys
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
HITL = ROOT / "hitl"
H008 = HITL / "h008_s4_mobility_translation_sweep"
H008.mkdir(parents=True, exist_ok=True)

for path in [OUT, HITL]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import h007_s4_mobility_latent_model as h007  # noqa: E402
from e288_lifestyle_bundle_jepa_audit import KEYS, TARGETS, base_label_matrix, clip_prob, load_frames, md_table  # noqa: E402
from e272_public_free_candidate_audit import (  # noqa: E402
    CURRENT,
    KNOWN_FAILS,
    build_features,
    evaluate_models,
    score_candidates,
)
from e328_ownlatent_lifestyle_state_experiment import safe_id, sigmoid  # noqa: E402
from public_anchor_bottleneck_decomposition import load_sub as load_anchor_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


EPS = 1.0e-12
TARGET = "S4"
TIDX = TARGETS.index(TARGET)
E247 = OUT / CURRENT
H003_TINY = HITL / "h003_hs_jepa_prototype" / "submission_h003_semantic_tiny_11e7aa3b.csv"

CANDIDATE_OUT = H008 / "h008_candidates.csv"
SCORE_OUT = H008 / "h008_selector_scores.csv"
ANATOMY_OUT = H008 / "h008_candidate_anatomy.csv"
GATE_OUT = H008 / "h008_gate_scores.csv"
FAMILY_OUT = H008 / "h008_family_summary.csv"
SIGNAL_OUT = H008 / "h008_signal_summary.csv"
SELECTION_OUT = H008 / "h008_selection.csv"
REPORT_OUT = H008 / "h008_report.md"


@dataclass(frozen=True)
class CandidateSpec:
    candidate_id: str
    family: str
    raw_signal: str
    select_signal: str
    mode: str
    top_k: int
    scale: float
    cap: float
    project_bad_axis: bool = False


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


def z01(values: np.ndarray | pd.Series) -> np.ndarray:
    x = np.asarray(pd.Series(values, dtype="float64").replace([np.inf, -np.inf], np.nan).fillna(0.0), dtype=np.float64)
    med = float(np.median(x))
    q25 = float(np.quantile(x, 0.25))
    q75 = float(np.quantile(x, 0.75))
    scale = (q75 - q25) / 1.349
    if not np.isfinite(scale) or scale < 1.0e-9:
        scale = float(np.std(x))
    if not np.isfinite(scale) or scale < 1.0e-9:
        return np.zeros(len(x), dtype=np.float64)
    return np.clip((x - med) / scale, -8.0, 8.0)


def normalize_sample_keys(sample: pd.DataFrame) -> pd.DataFrame:
    out = sample[KEYS].copy()
    for col in ["sleep_date", "lifelog_date"]:
        out[col] = pd.to_datetime(out[col])
    return out.reset_index(drop=True)


def get_base_and_h007_state() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    base, _, _, _ = load_frames()
    if h007.LATENT_OUT.exists() and h007.ABLATION_OUT.exists():
        latent = pd.read_parquet(h007.LATENT_OUT)
        ablation = pd.read_csv(h007.ABLATION_OUT)
    else:
        base, latent, _, _ = h007.build_latent_features()
        ablation, _, _ = h007.evaluate_feature_sets(base, latent)
    chosen = h007.choose_model(ablation)
    return base, latent, ablation, chosen


def full_s4_predictions(base: pd.DataFrame, latent: pd.DataFrame, chosen: dict[str, Any]) -> tuple[np.ndarray, np.ndarray, pd.DataFrame]:
    train_mask = base["split"].eq("train").to_numpy()
    train = base.loc[train_mask].reset_index(drop=True)
    test = base.loc[~train_mask].sort_values(KEYS).reset_index(drop=True)
    test_idx = base.loc[~train_mask].sort_values(KEYS).index.to_numpy(dtype=int)
    y = train[TARGET].to_numpy(dtype=int)
    base_x_train = base_label_matrix(train).reset_index(drop=True)
    base_x_test = base_label_matrix(test).reset_index(drop=True)
    cols = h007.FEATURE_SETS[str(chosen["feature_set"])]
    add_train = latent.loc[train_mask, cols].astype(float).reset_index(drop=True)
    add_test = latent.loc[test_idx, cols].astype(float).reset_index(drop=True)
    c_value = float(chosen["C"])
    base_pred = h007.full_predict_binary(base_x_train, y, base_x_test, c_value)
    plus_pred = h007.full_predict_binary(
        pd.concat([base_x_train, add_train], axis=1),
        y,
        pd.concat([base_x_test, add_test], axis=1),
        c_value,
    )
    state_cols = [
        "h005_mobility_teacher_z",
        "h005_mobility_teacher_rank",
        "h005_support_teacher_z",
        "jepa_mobility_pred_z",
        "jepa_mobility_residual_z",
        "jepa_mobility_energy",
        "jepa_mobility_low_energy",
        "jepa_mobility_agreement",
        "mobility_x_weekend",
        "mobility_x_sensor",
        "mobility_x_badnight",
    ]
    state = latent.loc[test_idx, KEYS + [c for c in state_cols if c in latent.columns]].reset_index(drop=True)
    return base_pred, plus_pred, state


def load_bad_s4_basis(sample: pd.DataFrame, base_logit_s4: np.ndarray) -> list[np.ndarray]:
    basis: list[np.ndarray] = []
    for name in [*KNOWN_FAILS, str(H003_TINY)]:
        try:
            path = Path(name)
            if path == H003_TINY and not path.exists():
                continue
            pred = load_anchor_sub(name, sample)[TARGETS].to_numpy(dtype=np.float64)
        except Exception:  # noqa: BLE001
            continue
        move = logit(pred[:, TIDX]) - base_logit_s4
        if float(np.linalg.norm(move)) > 1.0e-9:
            basis.append(move)
    return basis


def project_away(move: np.ndarray, basis: list[np.ndarray]) -> np.ndarray:
    out = np.asarray(move, dtype=np.float64).copy()
    for bad in basis:
        denom = float(np.dot(bad, bad))
        if denom <= EPS:
            continue
        coeff = float(np.dot(out, bad) / denom)
        if coeff > 0.0:
            out = out - coeff * bad
    return out


def build_signals(
    e247_s4_logit: np.ndarray,
    base_pred: np.ndarray,
    plus_pred: np.ndarray,
    state: pd.DataFrame,
) -> tuple[dict[str, np.ndarray], pd.DataFrame]:
    model_delta = logit(plus_pred) - logit(base_pred)
    toward_plus = logit(plus_pred) - e247_s4_logit
    teacher = state["h005_mobility_teacher_z"].to_numpy(dtype=np.float64)
    teacher_rank = state["h005_mobility_teacher_rank"].to_numpy(dtype=np.float64)
    low_energy = state["jepa_mobility_low_energy"].to_numpy(dtype=np.float64)
    agreement = state["jepa_mobility_agreement"].to_numpy(dtype=np.float64)
    energy = state["jepa_mobility_energy"].to_numpy(dtype=np.float64)
    support = state["h005_support_teacher_z"].to_numpy(dtype=np.float64)
    weekend = state.get("mobility_x_weekend", pd.Series(0.0, index=state.index)).to_numpy(dtype=np.float64)
    sensor = state.get("mobility_x_sensor", pd.Series(0.0, index=state.index)).to_numpy(dtype=np.float64)

    consensus_score = (
        0.35 * rank01(np.maximum(model_delta, 0.0))
        + 0.30 * rank01(teacher_rank)
        + 0.25 * rank01(low_energy)
        + 0.10 * rank01(agreement)
    )
    support_score = (
        0.35 * rank01(np.maximum(model_delta, 0.0))
        + 0.30 * rank01(support)
        + 0.20 * rank01(sensor)
        + 0.15 * rank01(teacher_rank)
    )
    highlow_raw = z01(teacher_rank - 0.5)
    balanced_raw = z01(0.45 * teacher + 0.30 * support + 0.25 * low_energy)
    anti_energy_raw = z01(teacher - 0.35 * energy + 0.20 * agreement)

    signals = {
        "model_delta": model_delta,
        "model_delta_pos": np.maximum(model_delta, 0.0),
        "toward_plus": toward_plus,
        "teacher_rank_centered": highlow_raw,
        "balanced_state": balanced_raw,
        "anti_energy_state": anti_energy_raw,
        "weekend_state": z01(teacher + 0.45 * weekend),
        "consensus_score": consensus_score,
        "support_score": support_score,
        "low_energy_score": rank01(low_energy),
        "abs_delta_score": rank01(np.abs(model_delta)),
        "toward_abs_score": rank01(np.abs(toward_plus)),
    }
    rows = []
    for name, values in signals.items():
        arr = np.asarray(values, dtype=np.float64)
        rows.append(
            {
                "signal": name,
                "mean": float(np.mean(arr)),
                "std": float(np.std(arr)),
                "min": float(np.min(arr)),
                "p10": float(np.quantile(arr, 0.10)),
                "median": float(np.median(arr)),
                "p90": float(np.quantile(arr, 0.90)),
                "max": float(np.max(arr)),
                "positive_rate": float(np.mean(arr > 0.0)),
            }
        )
    signal_summary = pd.DataFrame(rows)
    signal_summary.to_csv(SIGNAL_OUT, index=False)
    return signals, signal_summary


def spec_grid() -> list[CandidateSpec]:
    specs: list[CandidateSpec] = []
    for k in [20, 28, 40, 60, 80, 100]:
        for scale, cap in [(0.008, 0.004), (0.012, 0.005), (0.018, 0.008), (0.026, 0.010)]:
            specs.append(CandidateSpec(f"delta_pos_k{k}_s{scale:g}_c{cap:g}", "delta_pos", "model_delta_pos", "consensus_score", "positive", k, scale, cap))
    for k in [40, 60, 80, 100, 130]:
        for scale, cap in [(0.006, 0.004), (0.010, 0.006), (0.016, 0.008), (0.024, 0.010)]:
            specs.append(CandidateSpec(f"delta_signed_k{k}_s{scale:g}_c{cap:g}", "delta_signed", "model_delta", "abs_delta_score", "signed", k, scale, cap))
    for signal in ["teacher_rank_centered", "balanced_state", "anti_energy_state", "weekend_state"]:
        for k in [20, 36, 50, 80, 110]:
            for amp in [0.0035, 0.0050, 0.0070, 0.0090]:
                specs.append(CandidateSpec(f"{signal}_hi_k{k}_a{amp:g}", "state_high", signal, "consensus_score", "positive_constant", k, amp, amp))
    for signal in ["teacher_rank_centered", "balanced_state", "anti_energy_state"]:
        for k in [20, 30, 40, 55]:
            for amp in [0.0035, 0.0050, 0.0070]:
                specs.append(CandidateSpec(f"{signal}_highlow_k{k}_a{amp:g}", "state_highlow", signal, signal, "highlow", k, amp, amp))
    for k in [20, 40, 60, 80]:
        for scale, cap in [(0.006, 0.004), (0.010, 0.006), (0.018, 0.008)]:
            specs.append(CandidateSpec(f"toward_plus_cons_k{k}_s{scale:g}_c{cap:g}", "toward_plus", "toward_plus", "consensus_score", "signed", k, scale, cap))
            specs.append(CandidateSpec(f"toward_plus_abs_k{k}_s{scale:g}_c{cap:g}", "toward_plus", "toward_plus", "toward_abs_score", "signed", k, scale, cap))
    for k in [40, 80, 110]:
        for scale, cap in [(0.010, 0.006), (0.018, 0.008), (0.026, 0.010)]:
            specs.append(CandidateSpec(f"orth_delta_k{k}_s{scale:g}_c{cap:g}", "orthogonalized", "model_delta", "abs_delta_score", "signed", k, scale, cap, True))
            specs.append(CandidateSpec(f"orth_balanced_k{k}_s{scale:g}_c{cap:g}", "orthogonalized", "balanced_state", "consensus_score", "signed", k, scale, cap, True))
    for raw_signal in ["model_delta", "toward_plus", "balanced_state", "anti_energy_state", "teacher_rank_centered"]:
        for scale, cap in [(0.0025, 0.0025), (0.0050, 0.0050), (0.0080, 0.0060), (0.0120, 0.0080)]:
            specs.append(CandidateSpec(f"continuous_{raw_signal}_s{scale:g}_c{cap:g}", "continuous_all", raw_signal, "consensus_score", "continuous", 250, scale, cap))
    for raw_signal in ["model_delta", "balanced_state", "teacher_rank_centered"]:
        for scale, cap in [(0.0050, 0.0050), (0.0100, 0.0060), (0.0160, 0.0080)]:
            specs.append(CandidateSpec(f"orth_continuous_{raw_signal}_s{scale:g}_c{cap:g}", "continuous_orthogonalized", raw_signal, "consensus_score", "continuous", 250, scale, cap, True))
    # Explicit controls: the same best-looking rows in the wrong direction.
    for k in [28, 60, 100]:
        for amp in [0.0050, 0.0080]:
            specs.append(CandidateSpec(f"down_control_k{k}_a{amp:g}", "down_control", "model_delta_pos", "consensus_score", "negative_constant", k, amp, amp))
    return specs


def selected_mask(score: np.ndarray, k: int, high: bool = True) -> np.ndarray:
    score = np.asarray(score, dtype=np.float64)
    k = int(min(max(k, 1), len(score)))
    order = np.argsort(score)
    idx = order[-k:] if high else order[:k]
    mask = np.zeros(len(score), dtype=bool)
    mask[idx] = True
    return mask


def make_move(spec: CandidateSpec, signals: dict[str, np.ndarray], bad_basis: list[np.ndarray]) -> np.ndarray:
    raw = np.asarray(signals[spec.raw_signal], dtype=np.float64).copy()
    score = np.asarray(signals[spec.select_signal], dtype=np.float64).copy()
    move = np.zeros(len(raw), dtype=np.float64)
    if spec.mode == "positive":
        mask = selected_mask(score, spec.top_k, True)
        move[mask] = np.clip(spec.scale * np.maximum(raw[mask], 0.0), 0.0, spec.cap)
    elif spec.mode == "signed":
        mask = selected_mask(score, spec.top_k, True)
        base = raw.copy()
        if spec.project_bad_axis:
            base = project_away(base, bad_basis)
        move[mask] = np.clip(spec.scale * base[mask], -spec.cap, spec.cap)
    elif spec.mode == "positive_constant":
        mask = selected_mask(score, spec.top_k, True)
        move[mask] = spec.cap
    elif spec.mode == "negative_constant":
        mask = selected_mask(score, spec.top_k, True)
        move[mask] = -spec.cap
    elif spec.mode == "highlow":
        high = selected_mask(raw, spec.top_k, True)
        low = selected_mask(raw, spec.top_k, False)
        move[high] = spec.cap
        move[low] = -spec.cap
    elif spec.mode == "continuous":
        base = raw.copy()
        if spec.project_bad_axis:
            base = project_away(base, bad_basis)
        move = np.clip(spec.scale * base, -spec.cap, spec.cap)
    else:
        raise ValueError(spec.mode)
    return move


def write_candidate(base_sub: pd.DataFrame, base_logit: np.ndarray, move_s4: np.ndarray, candidate_id: str) -> Path:
    logits = base_logit.copy()
    logits[:, TIDX] += move_s4
    out = base_sub[KEYS].copy()
    out[TARGETS] = clip_prob(sigmoid(logits))
    path = H008 / f"submission_h008_{safe_id(candidate_id, 110)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def materialize_candidates(
    base: pd.DataFrame,
    base_pred: np.ndarray,
    plus_pred: np.ndarray,
    state: pd.DataFrame,
) -> tuple[pd.DataFrame, list[Path], pd.DataFrame]:
    train_mask = base["split"].eq("train").to_numpy()
    test = base.loc[~train_mask].sort_values(KEYS).reset_index(drop=True)
    sample = normalize_sample_keys(test[KEYS])
    base_sub = load_anchor_sub(E247, sample)
    base_prob = base_sub[TARGETS].to_numpy(dtype=np.float64)
    base_logit = logit(base_prob)
    e247_s4_logit = base_logit[:, TIDX]
    bad_basis = load_bad_s4_basis(sample, e247_s4_logit)
    signals, signal_summary = build_signals(e247_s4_logit, base_pred, plus_pred, state)

    rows: list[dict[str, Any]] = []
    paths: list[Path] = []
    seen_hashes: set[str] = set()
    for spec in spec_grid():
        move_s4 = make_move(spec, signals, bad_basis)
        if float(np.sum(np.abs(move_s4))) <= EPS:
            continue
        logits = base_logit.copy()
        logits[:, TIDX] += move_s4
        arr_hash = hashlib.sha1(np.round(move_s4, 12).tobytes()).hexdigest()[:12]
        if arr_hash in seen_hashes:
            continue
        seen_hashes.add(arr_hash)
        path = write_candidate(base_sub, base_logit, move_s4, spec.candidate_id)
        paths.append(path)
        changed = np.abs(move_s4) > EPS
        rows.append(
            {
                "candidate_id": spec.candidate_id,
                "family": spec.family,
                "raw_signal": spec.raw_signal,
                "select_signal": spec.select_signal,
                "mode": spec.mode,
                "top_k": spec.top_k,
                "scale": spec.scale,
                "cap": spec.cap,
                "project_bad_axis": spec.project_bad_axis,
                "file": rel(path),
                "basename": path.name,
                "changed_rows": int(changed.sum()),
                "changed_cells": int(changed.sum()),
                "mean_abs_logit_move": float(np.mean(np.abs(move_s4))),
                "l1_logit_move": float(np.sum(np.abs(move_s4))),
                "max_abs_logit_move": float(np.max(np.abs(move_s4))),
                "positive_move_rows": int((move_s4 > EPS).sum()),
                "negative_move_rows": int((move_s4 < -EPS).sum()),
                "max_abs_prob_delta": float(np.max(np.abs(sigmoid(logits)[:, TIDX] - base_prob[:, TIDX]))),
                "selected_mobility_rank_mean": float(state.loc[changed, "h005_mobility_teacher_rank"].mean()) if int(changed.sum()) else np.nan,
                "selected_low_energy_mean": float(state.loc[changed, "jepa_mobility_low_energy"].mean()) if int(changed.sum()) else np.nan,
            }
        )
    candidates = pd.DataFrame(rows).sort_values(["family", "l1_logit_move", "candidate_id"]).reset_index(drop=True)
    candidates.to_csv(CANDIDATE_OUT, index=False)
    return candidates, paths, signal_summary


def score_new_candidates(paths: list[Path]) -> pd.DataFrame:
    sample = load_anchor_sub(E247)[KEYS]
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    files = [CURRENT] + [str(path.resolve()) for path in paths]
    candidates = build_features(files, sample, refs, ref_vecs)
    scores = score_candidates(known, candidates, model_df)
    scores.to_csv(SCORE_OUT, index=False)
    return scores


def candidate_anatomy(paths: list[Path]) -> pd.DataFrame:
    sample = load_anchor_sub(E247)[KEYS]
    base = load_anchor_sub(E247, sample)
    base_prob = base[TARGETS].to_numpy(dtype=np.float64)
    base_logit = logit(base_prob)
    h003_move = None
    if H003_TINY.exists():
        h003 = load_anchor_sub(H003_TINY, sample)
        h003_move = logit(h003[TARGETS].to_numpy(dtype=np.float64)) - base_logit
    rows: list[dict[str, Any]] = []
    for path in paths:
        cand = load_anchor_sub(path, sample)
        prob = cand[TARGETS].to_numpy(dtype=np.float64)
        move = logit(prob) - base_logit
        rec: dict[str, Any] = {
            "file": rel(path),
            "basename": path.name,
            "changed_rows_vs_current": int((np.abs(move).max(axis=1) > EPS).sum()),
            "changed_cells_vs_current": int((np.abs(move) > EPS).sum()),
            "mean_abs_logit_delta_vs_current": float(np.mean(np.abs(move))),
            "l1_logit_delta_vs_current": float(np.sum(np.abs(move))),
            "max_abs_logit_delta_vs_current": float(np.max(np.abs(move))),
            "max_abs_prob_delta_vs_current": float(np.max(np.abs(prob - base_prob))),
        }
        for ti, target in enumerate(TARGETS):
            rec[f"changed_{target}"] = int((np.abs(move[:, ti]) > EPS).sum())
        if h003_move is not None:
            denom = float(np.linalg.norm(move) * np.linalg.norm(h003_move) + EPS)
            rec["cos_delta_with_h003_tiny"] = float(np.sum(move * h003_move) / denom)
            rec["l1_ratio_to_h003_tiny"] = float(np.sum(np.abs(move)) / (np.sum(np.abs(h003_move)) + EPS))
        rows.append(rec)
    anatomy = pd.DataFrame(rows).sort_values(["l1_logit_delta_vs_current", "basename"]).reset_index(drop=True)
    anatomy.to_csv(ANATOMY_OUT, index=False)
    return anatomy


def build_gate_scores(candidates: pd.DataFrame, scores: pd.DataFrame, anatomy: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    score_cols = [
        "basename",
        "promotion_decision",
        "pred_delta_vs_current_mean",
        "pred_delta_vs_current_p10",
        "pred_delta_vs_current_p90",
        "pred_beats_current_rate",
        "incremental_bad_axis_vs_current",
        "strict_promote_gate",
        "info_sensor_gate",
        "below_resolution_gate",
        "block_gate",
        "bad_axis_abs_load",
        "mean_abs_move_vs_a2c8",
        "mean_abs_move_vs_raw05",
    ]
    present_score_cols = [col for col in score_cols if col in scores.columns]
    merged = candidates.merge(scores[present_score_cols], on="basename", how="left")
    anatomy_cols = [
        "basename",
        "changed_rows_vs_current",
        "changed_cells_vs_current",
        "l1_logit_delta_vs_current",
        "max_abs_prob_delta_vs_current",
        "cos_delta_with_h003_tiny",
        "l1_ratio_to_h003_tiny",
    ]
    present_anatomy_cols = [col for col in anatomy_cols if col in anatomy.columns]
    merged = merged.merge(anatomy[present_anatomy_cols], on="basename", how="left")
    ratio = merged.get("l1_ratio_to_h003_tiny", pd.Series(0.0, index=merged.index)).fillna(0.0)
    merged["shape_gate_70"] = (
        (merged["changed_cells"] <= 70)
        & (merged["max_abs_prob_delta"] <= 0.0020)
        & (ratio <= 0.25)
        & (merged["incremental_bad_axis_vs_current"].abs() <= 0.020)
    )
    merged["shape_gate_120"] = (
        (merged["changed_cells"] <= 120)
        & (merged["max_abs_prob_delta"] <= 0.0030)
        & (ratio <= 0.35)
        & (merged["incremental_bad_axis_vs_current"].abs() <= 0.030)
    )
    merged["h008_strict_upload_gate"] = merged["shape_gate_70"] & merged["strict_promote_gate"].fillna(False).astype(bool)
    merged["h008_resolution_escape_gate"] = (
        merged["shape_gate_120"]
        & (merged["pred_delta_vs_current_p90"] < -0.00002)
        & (merged["pred_beats_current_rate"] >= 0.80)
        & (merged["pred_delta_vs_current_mean"] < -0.00001)
    )
    merged["h008_info_gate"] = merged["shape_gate_120"] & (
        merged["info_sensor_gate"].fillna(False).astype(bool)
        | (
            (merged["pred_delta_vs_current_mean"] < 0.0)
            & (merged["pred_beats_current_rate"] >= 0.55)
            & (merged["incremental_bad_axis_vs_current"].abs() <= 0.025)
        )
    )
    merged["h008_decision"] = np.select(
        [
            merged["h008_strict_upload_gate"],
            merged["h008_resolution_escape_gate"],
            merged["h008_info_gate"] & ~merged["below_resolution_gate"].fillna(False).astype(bool),
            merged["h008_info_gate"] & merged["below_resolution_gate"].fillna(False).astype(bool),
            merged["shape_gate_120"],
        ],
        [
            "uploadsafe_candidate",
            "resolution_escape_candidate",
            "diagnostic_public_sensor_only",
            "too_small_to_submit",
            "shape_ok_but_selector_rejects",
        ],
        default="reject_shape_or_bad_axis",
    )
    gate = merged.sort_values(
        [
            "h008_strict_upload_gate",
            "h008_resolution_escape_gate",
            "h008_info_gate",
            "pred_delta_vs_current_p90",
            "pred_delta_vs_current_mean",
        ],
        ascending=[False, False, False, True, True],
    ).reset_index(drop=True)
    gate.to_csv(GATE_OUT, index=False)
    family = (
        gate.groupby("family")
        .agg(
            n=("candidate_id", "count"),
            strict=("h008_strict_upload_gate", "sum"),
            resolution_escape=("h008_resolution_escape_gate", "sum"),
            info=("h008_info_gate", "sum"),
            best_mean=("pred_delta_vs_current_mean", "min"),
            best_p90=("pred_delta_vs_current_p90", "min"),
            best_beats=("pred_beats_current_rate", "max"),
            best_bad_axis=("incremental_bad_axis_vs_current", lambda s: float(np.min(np.abs(s)))),
        )
        .sort_values(["strict", "resolution_escape", "info", "best_p90", "best_mean"], ascending=[False, False, False, True, True])
        .reset_index()
    )
    family.to_csv(FAMILY_OUT, index=False)
    return gate, family


def write_selection(gate: pd.DataFrame) -> pd.DataFrame:
    rows = []
    upload = gate[gate["h008_strict_upload_gate"].astype(bool)].copy()
    if upload.empty:
        upload = gate[gate["h008_resolution_escape_gate"].astype(bool)].head(1).copy()
    for rec in upload.to_dict("records"):
        src = ROOT / str(rec["file"])
        if not src.exists():
            src = H008 / str(rec["basename"])
        suffix = "_uploadsafe.csv" if bool(rec.get("h008_strict_upload_gate", False)) else "_resolution_sensor.csv"
        dst = H008 / src.name.replace(".csv", suffix)
        shutil.copyfile(src, dst)
        rows.append(
            {
                "candidate_id": rec["candidate_id"],
                "basename": dst.name,
                "file": rel(dst),
                "decision": rec["h008_decision"],
                "pred_delta_vs_current_mean": rec["pred_delta_vs_current_mean"],
                "pred_delta_vs_current_p90": rec["pred_delta_vs_current_p90"],
                "pred_beats_current_rate": rec["pred_beats_current_rate"],
                "reason": "strict upload if available; otherwise one resolution-escape sensor",
            }
        )
    selection = pd.DataFrame(rows)
    selection.to_csv(SELECTION_OUT, index=False)
    return selection


def write_report(
    chosen: dict[str, Any],
    ablation: pd.DataFrame,
    signal_summary: pd.DataFrame,
    candidates: pd.DataFrame,
    gate: pd.DataFrame,
    family: pd.DataFrame,
    scores: pd.DataFrame,
    anatomy: pd.DataFrame,
    selection: pd.DataFrame,
) -> None:
    abl_cols = [
        "feature_set",
        "C",
        "split",
        "delta_logloss",
        "null_median_delta",
        "null_dominance",
        "mean_delta",
        "worst_delta",
        "min_null_dominance",
    ]
    gate_cols = [
        "candidate_id",
        "family",
        "h008_decision",
        "changed_cells",
        "max_abs_prob_delta",
        "pred_delta_vs_current_mean",
        "pred_delta_vs_current_p10",
        "pred_delta_vs_current_p90",
        "pred_beats_current_rate",
        "incremental_bad_axis_vs_current",
        "shape_gate_70",
        "shape_gate_120",
        "basename",
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
    anatomy_cols = [
        "basename",
        "changed_rows_vs_current",
        "changed_cells_vs_current",
        "l1_logit_delta_vs_current",
        "max_abs_prob_delta_vs_current",
        "cos_delta_with_h003_tiny",
        "l1_ratio_to_h003_tiny",
    ]
    strict_n = int(gate["h008_strict_upload_gate"].sum())
    res_n = int(gate["h008_resolution_escape_gate"].sum())
    info_n = int(gate["h008_info_gate"].sum())
    best = gate.iloc[0]
    lines = [
        "# H008 S4 Mobility Translation Sweep",
        "",
        "## Question",
        "",
        "The S4 mobility latent is locally strong. Which translator from latent state to E247 S4 movement, if any, survives public-free selector stress?",
        "",
        "## Bottleneck Diagnosis",
        "",
        "- Data: the mobility state is real for S4 under subject/dateblock/null stress.",
        "- Objective: local S4 logloss gains are much larger than the safe E247 postprocess edge, so translation/calibration is the bottleneck.",
        "- Model capacity: not the first bottleneck for S4; the latent is already predictive.",
        "- Evaluation: selector sees many positive-mean moves but rejects broad or over-amplified versions by p90/shape.",
        "",
        "## Chosen H007 S4 Latent Model",
        "",
        f"- feature_set: `{chosen['feature_set']}`",
        f"- C: `{chosen['C']}`",
        "",
        "## H007 Local S4 Reminder",
        "",
        md_table(ablation[[col for col in abl_cols if col in ablation.columns]].head(20), n=20, floatfmt=".9f"),
        "",
        "## Signal Summary",
        "",
        md_table(signal_summary, n=30, floatfmt=".9f"),
        "",
        "## Translator Family Summary",
        "",
        md_table(family, n=30, floatfmt=".9f"),
        "",
        "## Top Candidate Gate",
        "",
        md_table(gate[[col for col in gate_cols if col in gate.columns]], n=45, floatfmt=".9f"),
        "",
        "## Selector Scores",
        "",
        md_table(scores[[col for col in score_cols if col in scores.columns]], n=45, floatfmt=".9f"),
        "",
        "## Movement Anatomy",
        "",
        md_table(anatomy[[col for col in anatomy_cols if col in anatomy.columns]], n=45, floatfmt=".9f"),
        "",
        "## Selection",
        "",
        md_table(selection, n=10, floatfmt=".9f"),
        "",
        "## Interpretation",
        "",
        f"- candidates generated: `{len(candidates)}`",
        f"- strict upload candidates: `{strict_n}`",
        f"- resolution-escape candidates: `{res_n}`",
        f"- info-gate candidates: `{info_n}`",
        f"- best selector-ranked candidate: `{best['basename']}` -> `{best['h008_decision']}`",
        "",
    ]
    if strict_n:
        lines.append("At least one translation cleared the original strict selector. This is a real submission candidate.")
    elif res_n:
        lines.append(
            "No original strict candidate appeared, but at least one broader S4-only translator escaped selector resolution with negative p90. Treat it as a scarce diagnostic sensor, not a guaranteed score bet."
        )
    elif info_n:
        lines.append(
            "The sweep confirms the latent direction repeatedly, but all safe movements remain below selector resolution. The next step is integrating the latent before E247 smoothing/stacking rather than post-hoc movement."
        )
    else:
        lines.append(
            "The latent is locally real but every tested E247 translator was rejected. This would shift focus away from postprocess entirely."
        )
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- `{rel(CANDIDATE_OUT)}`",
            f"- `{rel(SCORE_OUT)}`",
            f"- `{rel(ANATOMY_OUT)}`",
            f"- `{rel(GATE_OUT)}`",
            f"- `{rel(FAMILY_OUT)}`",
            f"- `{rel(SIGNAL_OUT)}`",
            f"- `{rel(SELECTION_OUT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    base, latent, ablation, chosen = get_base_and_h007_state()
    base_pred, plus_pred, state = full_s4_predictions(base, latent, chosen)
    candidates, paths, signal_summary = materialize_candidates(base, base_pred, plus_pred, state)
    scores = score_new_candidates(paths)
    anatomy = candidate_anatomy(paths)
    gate, family = build_gate_scores(candidates, scores, anatomy)
    selection = write_selection(gate)
    write_report(chosen, ablation, signal_summary, candidates, gate, family, scores, anatomy, selection)

    print(f"report={rel(REPORT_OUT)}")
    print("[inventory]", {"candidates": len(candidates), "strict": int(gate["h008_strict_upload_gate"].sum()), "resolution": int(gate["h008_resolution_escape_gate"].sum()), "info": int(gate["h008_info_gate"].sum())})
    print("[family]")
    print(family.round(9).to_string(index=False))
    print("[top gate]")
    cols = [
        "candidate_id",
        "family",
        "h008_decision",
        "changed_cells",
        "max_abs_prob_delta",
        "pred_delta_vs_current_mean",
        "pred_delta_vs_current_p90",
        "pred_beats_current_rate",
        "incremental_bad_axis_vs_current",
        "basename",
    ]
    print(gate[cols].head(30).round(9).to_string(index=False))
    if not selection.empty:
        print("[selection]")
        print(selection.to_string(index=False))


if __name__ == "__main__":
    main()
