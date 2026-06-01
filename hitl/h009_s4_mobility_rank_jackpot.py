#!/usr/bin/env python3
"""H009: jackpot S4 mobility rank-rewrite experiment.

H007/H008 established a sharp contradiction:

    - the HS-JEPA mobility latent is a strong local S4 feature;
    - tiny E247 S4 logit edits are too small to matter.

H009 drops the small-edit assumption.  The big-bet hypothesis is:

    E247's S4 marginal calibration may be roughly right, but its row ordering
    is wrong for a hidden mobility state.

If true, we should preserve E247's probability distribution while reassigning
S4 ranks according to the HS-JEPA mobility latent / latent S4 model.  This can
change many rows without changing the overall prior.  It is risky by design and
is evaluated as a jackpot experiment, not a conservative promotion.
"""

from __future__ import annotations

import hashlib
import sys
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
HITL = ROOT / "hitl"
H009 = HITL / "h009_s4_mobility_rank_jackpot"
H009.mkdir(parents=True, exist_ok=True)

for path in [OUT, HITL]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import h007_s4_mobility_latent_model as h007  # noqa: E402
from e288_lifestyle_bundle_jepa_audit import KEYS, TARGETS, base_label_matrix, groups_for, load_frames, md_table  # noqa: E402
from e272_public_free_candidate_audit import CURRENT, build_features, evaluate_models, score_candidates  # noqa: E402
from e328_ownlatent_lifestyle_state_experiment import safe_id, sigmoid  # noqa: E402
from public_anchor_bottleneck_decomposition import load_sub as load_anchor_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


EPS = 1.0e-12
TARGET = "S4"
TIDX = TARGETS.index(TARGET)
E247 = OUT / CURRENT
H003_TINY = HITL / "h003_hs_jepa_prototype" / "submission_h003_semantic_tiny_11e7aa3b.csv"

LOCAL_OUT = H009 / "h009_local_rank_rewrite_stress.csv"
CANDIDATE_OUT = H009 / "h009_candidates.csv"
SCORE_OUT = H009 / "h009_selector_scores.csv"
ANATOMY_OUT = H009 / "h009_candidate_anatomy.csv"
GATE_OUT = H009 / "h009_gate_scores.csv"
FAMILY_OUT = H009 / "h009_family_summary.csv"
SELECTION_OUT = H009 / "h009_selection.csv"
REPORT_OUT = H009 / "h009_report.md"


@dataclass(frozen=True)
class RewriteSpec:
    candidate_id: str
    family: str
    op: str
    score_signal: str
    strength: float
    group: str = "global"
    k: int = 0
    cap: float = 0.0
    reverse: bool = False


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


def normalize_sample_keys(sample: pd.DataFrame) -> pd.DataFrame:
    out = sample[KEYS].copy()
    for col in ["sleep_date", "lifelog_date"]:
        out[col] = pd.to_datetime(out[col])
    return out.reset_index(drop=True)


def rank01(values: np.ndarray | pd.Series) -> np.ndarray:
    s = pd.Series(values, dtype="float64").replace([np.inf, -np.inf], np.nan).fillna(0.0)
    if s.nunique(dropna=False) <= 1:
        return np.full(len(s), 0.5, dtype=np.float64)
    return s.rank(method="average", pct=True).to_numpy(dtype=np.float64)


def get_state_and_models() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Any], dict[str, np.ndarray]]:
    base, latent, ablation, chosen = h007.get_base_and_h007_state() if hasattr(h007, "get_base_and_h007_state") else _fallback_h007_state()
    # h007 has no public get_base_and_h007_state in older commits, but current
    # H008 already uses equivalent behavior.  Keep a fallback for reruns.
    ablation, _, pred_cache = h007.evaluate_feature_sets(base, latent)
    chosen = h007.choose_model(ablation)
    return base, latent, ablation, chosen, pred_cache


def _fallback_h007_state() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    base, latent, _, _ = h007.build_latent_features()
    ablation, _, _ = h007.evaluate_feature_sets(base, latent)
    chosen = h007.choose_model(ablation)
    return base, latent, ablation, chosen


def full_s4_predictions(base: pd.DataFrame, latent: pd.DataFrame, chosen: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    """Fit the chosen H007 S4 model on full train and predict sorted test rows."""
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
    return base_pred, plus_pred


def signal_frame(
    latent_part: pd.DataFrame,
    base_pred: np.ndarray,
    plus_pred: np.ndarray,
) -> pd.DataFrame:
    delta = logit(plus_pred) - logit(base_pred)
    teacher = latent_part["h005_mobility_teacher_z"].to_numpy(dtype=np.float64)
    teacher_rank = latent_part["h005_mobility_teacher_rank"].to_numpy(dtype=np.float64)
    low_energy = latent_part["jepa_mobility_low_energy"].to_numpy(dtype=np.float64)
    agreement = latent_part["jepa_mobility_agreement"].to_numpy(dtype=np.float64)
    support = latent_part["h005_support_teacher_z"].to_numpy(dtype=np.float64)
    out = pd.DataFrame(
        {
            "plus_prob": plus_pred,
            "base_prob": base_pred,
            "delta_logit": delta,
            "delta_pos": np.maximum(delta, 0.0),
            "teacher_z": teacher,
            "teacher_rank": teacher_rank,
            "low_energy": low_energy,
            "agreement": agreement,
            "support_z": support,
        }
    )
    out["consensus"] = (
        0.30 * rank01(out["plus_prob"])
        + 0.25 * rank01(out["delta_pos"])
        + 0.25 * rank01(out["teacher_rank"])
        + 0.20 * rank01(out["low_energy"])
    )
    out["human_state"] = (
        0.35 * rank01(out["teacher_rank"])
        + 0.25 * rank01(out["support_z"])
        + 0.25 * rank01(out["low_energy"])
        + 0.15 * rank01(out["agreement"])
    )
    out["abs_delta"] = rank01(np.abs(delta))
    return out


def group_values(groups: pd.Series | None, n: int) -> list[np.ndarray]:
    if groups is None:
        return [np.arange(n, dtype=int)]
    out = []
    for _, idx in groups.reset_index(drop=True).groupby(groups.reset_index(drop=True)).groups.items():
        arr = np.asarray(list(idx), dtype=int)
        if len(arr) >= 2:
            out.append(arr)
    return out


def quantile_rewrite(base_prob: np.ndarray, score: np.ndarray, strength: float, groups: pd.Series | None = None, reverse: bool = False) -> np.ndarray:
    base_prob = np.asarray(base_prob, dtype=np.float64)
    score = -np.asarray(score, dtype=np.float64) if reverse else np.asarray(score, dtype=np.float64)
    target = base_prob.copy()
    for idx in group_values(groups, len(base_prob)):
        vals = np.sort(base_prob[idx])
        order = idx[np.argsort(score[idx])]
        target[order] = vals
    return sigmoid((1.0 - strength) * logit(base_prob) + strength * logit(target))


def tail_swap(base_prob: np.ndarray, score: np.ndarray, k: int, strength: float, reverse: bool = False) -> np.ndarray:
    base_prob = np.asarray(base_prob, dtype=np.float64)
    score = -np.asarray(score, dtype=np.float64) if reverse else np.asarray(score, dtype=np.float64)
    k = int(min(max(k, 1), len(score) // 2))
    order = np.argsort(score)
    selected = np.unique(np.r_[order[:k], order[-k:]])
    target = base_prob.copy()
    vals = np.sort(base_prob[selected])
    selected_order = selected[np.argsort(score[selected])]
    target[selected_order] = vals
    out = base_prob.copy()
    out[selected] = sigmoid((1.0 - strength) * logit(base_prob[selected]) + strength * logit(target[selected]))
    return out


def model_blend(base_prob: np.ndarray, plus_prob: np.ndarray, strength: float, cap: float) -> np.ndarray:
    move = np.clip(strength * (logit(plus_prob) - logit(base_prob)), -cap, cap)
    return sigmoid(logit(base_prob) + move)


def apply_spec(
    spec: RewriteSpec,
    base_prob: np.ndarray,
    plus_prob: np.ndarray,
    signals: pd.DataFrame,
    groups: pd.Series | None,
) -> np.ndarray:
    score = signals[spec.score_signal].to_numpy(dtype=np.float64)
    if spec.op == "quantile":
        return quantile_rewrite(base_prob, score, spec.strength, groups, spec.reverse)
    if spec.op == "tail_swap":
        return tail_swap(base_prob, score, spec.k, spec.strength, spec.reverse)
    if spec.op == "model_blend":
        return model_blend(base_prob, plus_prob, spec.strength, spec.cap)
    raise ValueError(spec.op)


def spec_grid() -> list[RewriteSpec]:
    specs: list[RewriteSpec] = []
    signals = ["plus_prob", "delta_pos", "teacher_rank", "consensus", "human_state", "low_energy"]
    for signal in signals:
        for group in ["global", "subject", "dateblock"]:
            for strength in [0.35, 0.60, 0.85, 1.00]:
                specs.append(RewriteSpec(f"qrank_{signal}_{group}_s{strength:g}", f"qrank_{group}", "quantile", signal, strength, group=group))
    for signal in signals:
        for k in [20, 35, 50, 75, 100, 125]:
            for strength in [0.50, 0.75, 1.00]:
                specs.append(RewriteSpec(f"tailswap_{signal}_k{k}_s{strength:g}", "tail_swap", "tail_swap", signal, strength, k=k))
    for strength in [0.10, 0.20, 0.35, 0.50, 0.75, 1.00]:
        for cap in [0.025, 0.050, 0.090, 0.140]:
            specs.append(RewriteSpec(f"modelblend_s{strength:g}_cap{cap:g}", "model_blend", "model_blend", "delta_pos", strength, cap=cap))
    # Matched inversion controls.  If these look good, the story is not trusted.
    for signal in ["consensus", "teacher_rank", "plus_prob"]:
        for strength in [0.60, 1.00]:
            specs.append(RewriteSpec(f"reverse_qrank_{signal}_s{strength:g}", "reverse_control", "quantile", signal, strength, reverse=True))
        for k in [50, 100]:
            specs.append(RewriteSpec(f"reverse_tailswap_{signal}_k{k}", "reverse_control", "tail_swap", signal, 1.0, k=k, reverse=True))
    return specs


def local_stress(base: pd.DataFrame, latent: pd.DataFrame, chosen: dict[str, Any], pred_cache: dict[str, np.ndarray]) -> pd.DataFrame:
    train_mask = base["split"].eq("train").to_numpy()
    train = base.loc[train_mask].reset_index(drop=True)
    latent_train = latent.loc[train_mask].reset_index(drop=True)
    y = train[TARGET].to_numpy(dtype=int)
    rows: list[dict[str, Any]] = []
    specs = spec_grid()
    feature_set = str(chosen["feature_set"])
    c_value = float(chosen["C"])
    for split_name in ["subject5", "dateblock5"]:
        base_pred = pred_cache[f"{feature_set}|C{c_value:g}|{split_name}|base"]
        plus_pred = pred_cache[f"{feature_set}|C{c_value:g}|{split_name}|plus"]
        signals = signal_frame(latent_train, base_pred, plus_pred)
        base_loss = float(log_loss(y, np.clip(base_pred, 1e-6, 1 - 1e-6), labels=[0, 1]))
        for spec in specs:
            groups = None
            if spec.group == "subject":
                groups = groups_for(train, "subject5").reset_index(drop=True)
            elif spec.group == "dateblock":
                groups = groups_for(train, "dateblock5").reset_index(drop=True)
            pred = apply_spec(spec, base_pred, plus_pred, signals, groups)
            loss = float(log_loss(y, np.clip(pred, 1e-6, 1 - 1e-6), labels=[0, 1]))
            rows.append(
                {
                    "candidate_id": spec.candidate_id,
                    "family": spec.family,
                    "op": spec.op,
                    "score_signal": spec.score_signal,
                    "strength": spec.strength,
                    "group": spec.group,
                    "k": spec.k,
                    "cap": spec.cap,
                    "reverse": spec.reverse,
                    "split": split_name,
                    "base_loss": base_loss,
                    "rewrite_loss": loss,
                    "delta_logloss": loss - base_loss,
                    "mean_abs_prob_delta": float(np.mean(np.abs(pred - base_pred))),
                    "max_abs_prob_delta": float(np.max(np.abs(pred - base_pred))),
                    "changed_rows": int(np.sum(np.abs(pred - base_pred) > 1.0e-12)),
                }
            )
    local = pd.DataFrame(rows)
    summary = (
        local.groupby(["candidate_id", "family", "op", "score_signal", "strength", "group", "k", "cap", "reverse"])
        .agg(
            mean_delta=("delta_logloss", "mean"),
            worst_delta=("delta_logloss", "max"),
            best_delta=("delta_logloss", "min"),
            subject5_delta=("delta_logloss", lambda s: float(s.iloc[0])),
            dateblock5_delta=("delta_logloss", lambda s: float(s.iloc[1]) if len(s) > 1 else np.nan),
            max_abs_prob_delta_local=("max_abs_prob_delta", "max"),
            mean_abs_prob_delta_local=("mean_abs_prob_delta", "mean"),
            changed_rows_local=("changed_rows", "max"),
        )
        .reset_index()
    )
    out = local.merge(summary, on=["candidate_id", "family", "op", "score_signal", "strength", "group", "k", "cap", "reverse"], how="left")
    out = out.sort_values(["reverse", "worst_delta", "mean_delta"], ascending=[True, True, True]).reset_index(drop=True)
    out.to_csv(LOCAL_OUT, index=False)
    return out


def select_specs(local: pd.DataFrame, limit: int = 80) -> list[RewriteSpec]:
    summary_cols = ["candidate_id", "family", "op", "score_signal", "strength", "group", "k", "cap", "reverse", "mean_delta", "worst_delta"]
    summary = local[summary_cols].drop_duplicates().copy()
    # Big-bet candidates must improve both local splits unless they are controls.
    robust = summary[(~summary["reverse"]) & (summary["worst_delta"] < 0.0)].sort_values(["worst_delta", "mean_delta"]).head(limit)
    controls = summary[summary["reverse"]].sort_values(["worst_delta", "mean_delta"]).head(8)
    chosen = pd.concat([robust, controls], ignore_index=True)
    specs = []
    for row in chosen.to_dict("records"):
        specs.append(
            RewriteSpec(
                candidate_id=str(row["candidate_id"]),
                family=str(row["family"]),
                op=str(row["op"]),
                score_signal=str(row["score_signal"]),
                strength=float(row["strength"]),
                group=str(row["group"]),
                k=int(row["k"]),
                cap=float(row["cap"]),
                reverse=bool(row["reverse"]),
            )
        )
    return specs


def write_candidate(base_sub: pd.DataFrame, base_prob: np.ndarray, new_s4: np.ndarray, candidate_id: str) -> Path:
    out = base_sub.copy()
    out[TARGET] = np.clip(new_s4, 1e-6, 1.0 - 1e-6)
    path = H009 / f"submission_h009_{safe_id(candidate_id, 110)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def materialize_test(base: pd.DataFrame, latent: pd.DataFrame, chosen: dict[str, Any], specs: list[RewriteSpec]) -> tuple[pd.DataFrame, list[Path]]:
    base_pred, plus_pred = full_s4_predictions(base, latent, chosen)
    train_mask = base["split"].eq("train").to_numpy()
    test = base.loc[~train_mask].sort_values(KEYS).reset_index(drop=True)
    test_idx = base.loc[~train_mask].sort_values(KEYS).index.to_numpy(dtype=int)
    latent_test = latent.loc[test_idx].reset_index(drop=True)
    signals = signal_frame(latent_test, base_pred, plus_pred)
    sample = normalize_sample_keys(test[KEYS])
    base_sub = load_anchor_sub(E247, sample)
    e247_s4 = base_sub[TARGET].to_numpy(dtype=np.float64)
    rows: list[dict[str, Any]] = []
    paths: list[Path] = []
    for spec in specs:
        groups = None
        if spec.group == "subject":
            groups = test["subject_id"].astype(str).reset_index(drop=True)
        elif spec.group == "dateblock":
            groups = test["dateblock_group"].astype(str).reset_index(drop=True)
        # The rewrite is applied to the E247 S4 body, but the ordering signal
        # comes from the independently trained H007 S4 latent model.
        new_s4 = apply_spec(spec, e247_s4, plus_pred, signals, groups)
        path = write_candidate(base_sub, e247_s4, new_s4, spec.candidate_id)
        paths.append(path)
        delta = new_s4 - e247_s4
        rows.append(
            {
                "candidate_id": spec.candidate_id,
                "family": spec.family,
                "op": spec.op,
                "score_signal": spec.score_signal,
                "strength": spec.strength,
                "group": spec.group,
                "k": spec.k,
                "cap": spec.cap,
                "reverse": spec.reverse,
                "file": rel(path),
                "basename": path.name,
                "changed_rows": int(np.sum(np.abs(delta) > 1.0e-12)),
                "changed_cells": int(np.sum(np.abs(delta) > 1.0e-12)),
                "mean_abs_prob_delta": float(np.mean(np.abs(delta))),
                "max_abs_prob_delta": float(np.max(np.abs(delta))),
                "mean_s4_before": float(np.mean(e247_s4)),
                "mean_s4_after": float(np.mean(new_s4)),
                "std_s4_before": float(np.std(e247_s4)),
                "std_s4_after": float(np.std(new_s4)),
            }
        )
    candidates = pd.DataFrame(rows)
    candidates.to_csv(CANDIDATE_OUT, index=False)
    return candidates, paths


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


def build_gate_scores(candidates: pd.DataFrame, local: pd.DataFrame, scores: pd.DataFrame, anatomy: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    local_summary = local[
        [
            "candidate_id",
            "mean_delta",
            "worst_delta",
            "subject5_delta",
            "dateblock5_delta",
            "max_abs_prob_delta_local",
            "changed_rows_local",
        ]
    ].drop_duplicates("candidate_id")
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
    merged = candidates.merge(local_summary, on="candidate_id", how="left")
    merged = merged.merge(scores[[col for col in score_cols if col in scores.columns]], on="basename", how="left")
    anatomy_cols = [
        "basename",
        "changed_rows_vs_current",
        "changed_cells_vs_current",
        "l1_logit_delta_vs_current",
        "max_abs_prob_delta_vs_current",
        "cos_delta_with_h003_tiny",
        "l1_ratio_to_h003_tiny",
    ]
    merged = merged.merge(anatomy[[col for col in anatomy_cols if col in anatomy.columns]], on="basename", how="left")
    merged["local_robust_gate"] = (merged["worst_delta"] < 0.0) & (~merged["reverse"])
    merged["jackpot_shape_gate"] = (
        (merged["changed_cells"] <= 250)
        & (merged["max_abs_prob_delta"] <= 0.20)
        & (merged["mean_s4_after"].sub(merged["mean_s4_before"]).abs() <= 0.015)
    )
    # Jackpot score intentionally values local stress more than known-public
    # selector, because this experiment tests a new world model rather than a
    # small-public-safe edit.
    merged["jackpot_score"] = (
        100.0 * merged["worst_delta"].fillna(9.0)
        + 40.0 * merged["mean_delta"].fillna(9.0)
        + 8.0 * merged["pred_delta_vs_current_p90"].fillna(0.0)
        + 4.0 * merged["pred_delta_vs_current_mean"].fillna(0.0)
        + 0.02 * merged["incremental_bad_axis_vs_current"].abs().fillna(0.0)
        + 0.5 * merged["reverse"].astype(float)
    )
    merged["h009_decision"] = np.select(
        [
            merged["strict_promote_gate"].fillna(False).astype(bool),
            merged["local_robust_gate"] & merged["jackpot_shape_gate"] & (merged["pred_delta_vs_current_p90"] < 0.00005),
            merged["local_robust_gate"] & merged["jackpot_shape_gate"],
            merged["reverse"].astype(bool),
        ],
        [
            "strict_upload_candidate",
            "jackpot_candidate",
            "local_only_high_risk",
            "reverse_control",
        ],
        default="reject",
    )
    gate = merged.sort_values(["h009_decision", "jackpot_score"], ascending=[True, True]).reset_index(drop=True)
    decision_rank = {
        "strict_upload_candidate": 0,
        "jackpot_candidate": 1,
        "local_only_high_risk": 2,
        "reverse_control": 3,
        "reject": 4,
    }
    gate["decision_rank"] = gate["h009_decision"].map(decision_rank).fillna(9).astype(int)
    gate = gate.sort_values(["decision_rank", "jackpot_score"]).reset_index(drop=True)
    gate.to_csv(GATE_OUT, index=False)
    family = (
        gate.groupby("family")
        .agg(
            n=("candidate_id", "count"),
            jackpot=("h009_decision", lambda s: int((s == "jackpot_candidate").sum())),
            local_only=("h009_decision", lambda s: int((s == "local_only_high_risk").sum())),
            best_local_worst=("worst_delta", "min"),
            best_local_mean=("mean_delta", "min"),
            best_selector_mean=("pred_delta_vs_current_mean", "min"),
            best_selector_p90=("pred_delta_vs_current_p90", "min"),
            best_jackpot_score=("jackpot_score", "min"),
        )
        .sort_values(["jackpot", "best_jackpot_score"], ascending=[False, True])
        .reset_index()
    )
    family.to_csv(FAMILY_OUT, index=False)
    return gate, family


def write_selection(gate: pd.DataFrame) -> pd.DataFrame:
    # One primary jackpot candidate plus one matched reverse control for
    # interpretation.  Do not create _uploadsafe because this is not conservative.
    rows = []
    primary = gate[gate["h009_decision"].eq("jackpot_candidate")].head(3)
    controls = gate[gate["h009_decision"].eq("reverse_control")].head(2)
    for rec in pd.concat([primary, controls]).to_dict("records"):
        rows.append(
            {
                "candidate_id": rec["candidate_id"],
                "basename": rec["basename"],
                "file": rec["file"],
                "decision": rec["h009_decision"],
                "jackpot_score": rec["jackpot_score"],
                "worst_delta": rec["worst_delta"],
                "pred_delta_vs_current_mean": rec["pred_delta_vs_current_mean"],
                "pred_delta_vs_current_p90": rec["pred_delta_vs_current_p90"],
            }
        )
    selection = pd.DataFrame(rows)
    selection.to_csv(SELECTION_OUT, index=False)
    return selection


def write_report(
    chosen: dict[str, Any],
    local: pd.DataFrame,
    candidates: pd.DataFrame,
    scores: pd.DataFrame,
    anatomy: pd.DataFrame,
    gate: pd.DataFrame,
    family: pd.DataFrame,
    selection: pd.DataFrame,
) -> None:
    local_cols = [
        "candidate_id",
        "family",
        "op",
        "score_signal",
        "strength",
        "group",
        "k",
        "cap",
        "split",
        "delta_logloss",
        "mean_delta",
        "worst_delta",
        "max_abs_prob_delta_local",
        "changed_rows_local",
    ]
    gate_cols = [
        "candidate_id",
        "h009_decision",
        "family",
        "op",
        "score_signal",
        "strength",
        "group",
        "k",
        "changed_cells",
        "max_abs_prob_delta",
        "mean_s4_before",
        "mean_s4_after",
        "worst_delta",
        "mean_delta",
        "pred_delta_vs_current_mean",
        "pred_delta_vs_current_p90",
        "pred_beats_current_rate",
        "jackpot_score",
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
    jackpot_n = int((gate["h009_decision"] == "jackpot_candidate").sum())
    best = gate.iloc[0]
    lines = [
        "# H009 S4 Mobility Rank Jackpot",
        "",
        "## Question",
        "",
        "What if the S4 mobility latent should not be a tiny correction, but should rewrite the S4 row ordering while preserving E247's marginal calibration?",
        "",
        "## Big-Bet Hypothesis",
        "",
        "E247's S4 probability distribution is treated as the right marginal prior. H009 only changes which rows receive high/low S4 probability, using the HS-JEPA mobility state and latent S4 model.",
        "",
        "This is intentionally not a conservative public-safe edit. It is the test for whether the S4 mobility discovery can become a leaderboard-sized move.",
        "",
        "## Chosen H007 S4 Latent Model",
        "",
        f"- feature_set: `{chosen['feature_set']}`",
        f"- C: `{chosen['C']}`",
        "",
        "## Family Summary",
        "",
        md_table(family, n=30, floatfmt=".9f"),
        "",
        "## Top Local Stress",
        "",
        md_table(local[[col for col in local_cols if col in local.columns]].head(60), n=60, floatfmt=".9f"),
        "",
        "## Jackpot Gate",
        "",
        md_table(gate[[col for col in gate_cols if col in gate.columns]].head(60), n=60, floatfmt=".9f"),
        "",
        "## Selector Scores",
        "",
        md_table(scores[[col for col in score_cols if col in scores.columns]].head(60), n=60, floatfmt=".9f"),
        "",
        "## Movement Anatomy",
        "",
        md_table(anatomy[[col for col in anatomy_cols if col in anatomy.columns]].head(60), n=60, floatfmt=".9f"),
        "",
        "## Selection",
        "",
        md_table(selection, n=10, floatfmt=".9f"),
        "",
        "## Interpretation",
        "",
        f"- candidate submissions materialized: `{len(candidates)}`",
        f"- jackpot candidates: `{jackpot_n}`",
        f"- best candidate: `{best['basename']}` -> `{best['h009_decision']}`",
        "",
    ]
    if jackpot_n:
        lines.append(
            "A rank-rewrite candidate survived both local stress and the jackpot shape gate. This is a real high-risk/high-upside public sensor: if it improves, the hidden-state ordering hypothesis is correct; if it fails, post-hoc S4 rank rewriting is dead."
        )
    else:
        lines.append(
            "No rank-rewrite candidate survived. That would mean the latent is useful only inside a trained model, not as a standalone S4 ordering rewrite."
        )
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- `{rel(LOCAL_OUT)}`",
            f"- `{rel(CANDIDATE_OUT)}`",
            f"- `{rel(SCORE_OUT)}`",
            f"- `{rel(ANATOMY_OUT)}`",
            f"- `{rel(GATE_OUT)}`",
            f"- `{rel(FAMILY_OUT)}`",
            f"- `{rel(SELECTION_OUT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    base, latent, _, chosen, pred_cache = get_state_and_models()
    local = local_stress(base, latent, chosen, pred_cache)
    specs = select_specs(local, limit=80)
    candidates, paths = materialize_test(base, latent, chosen, specs)
    scores = score_new_candidates(paths)
    anatomy = candidate_anatomy(paths)
    gate, family = build_gate_scores(candidates, local, scores, anatomy)
    selection = write_selection(gate)
    write_report(chosen, local, candidates, scores, anatomy, gate, family, selection)

    print(f"report={rel(REPORT_OUT)}")
    print("[chosen]", chosen)
    print("[inventory]", {"specs": len(specs), "jackpot": int((gate["h009_decision"] == "jackpot_candidate").sum())})
    print("[family]")
    print(family.round(9).to_string(index=False))
    print("[top gate]")
    cols = [
        "candidate_id",
        "h009_decision",
        "family",
        "op",
        "score_signal",
        "strength",
        "group",
        "k",
        "changed_cells",
        "max_abs_prob_delta",
        "worst_delta",
        "pred_delta_vs_current_mean",
        "pred_delta_vs_current_p90",
        "jackpot_score",
        "basename",
    ]
    print(gate[cols].head(35).round(9).to_string(index=False))
    if not selection.empty:
        print("[selection]")
        print(selection.to_string(index=False))


if __name__ == "__main__":
    main()
