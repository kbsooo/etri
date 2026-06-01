#!/usr/bin/env python3
"""H010: jackpot mobility-route triad rewrite.

H009 showed that the S4 mobility latent has a real local direction, but a pure
S4 rewrite is still a risky translation.  H010 tests the bigger human-state
claim from H005:

    high mobility / obligation / errand state is not only S4-up.
    It is a route through multiple labels: Q2-up, S1-down, S4-up.

This is deliberately not a tiny E247 edit.  It preserves each target's E247
marginal distribution and rewrites row assignment for whole target routes using
the HS-JEPA mobility latent.  If this survives, the big discovery is a hidden
life-state manifold, not an isolated S4 feature.
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
from sklearn.metrics import log_loss


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
HITL = ROOT / "hitl"
H010 = HITL / "h010_mobility_route_triad_jackpot"
H010.mkdir(parents=True, exist_ok=True)

for path in [OUT, HITL]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import h007_s4_mobility_latent_model as h007  # noqa: E402
from e288_lifestyle_bundle_jepa_audit import KEYS, TARGETS, base_label_matrix, groups_for, md_table  # noqa: E402
from e272_public_free_candidate_audit import CURRENT, build_features, evaluate_models, score_candidates  # noqa: E402
from e328_ownlatent_lifestyle_state_experiment import safe_id, sigmoid  # noqa: E402
from public_anchor_bottleneck_decomposition import load_sub as load_anchor_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


EPS = 1.0e-12
E247 = OUT / CURRENT
LOCAL_OUT = H010 / "h010_local_route_stress.csv"
CANDIDATE_OUT = H010 / "h010_candidates.csv"
SCORE_OUT = H010 / "h010_selector_scores.csv"
ANATOMY_OUT = H010 / "h010_candidate_anatomy.csv"
GATE_OUT = H010 / "h010_gate_scores.csv"
FAMILY_OUT = H010 / "h010_family_summary.csv"
SELECTION_OUT = H010 / "h010_selection.csv"
REPORT_OUT = H010 / "h010_report.md"


ROUTES: dict[str, dict[str, int]] = {
    "mobility_core_q2up_s1down_s4up": {"Q2": 1, "S1": -1, "S4": 1},
    "objective_mobility_s1down_s4up": {"S1": -1, "S4": 1},
    "intervention_mobility_q2up_s4up": {"Q2": 1, "S4": 1},
    "drain_route_q1down_s1down_s4up": {"Q1": -1, "S1": -1, "S4": 1},
    "subjective_intervention_q1down_q2up_s4up": {"Q1": -1, "Q2": 1, "S4": 1},
}


@dataclass(frozen=True)
class RouteSpec:
    candidate_id: str
    route: str
    op: str
    score_signal: str
    strength: float
    group: str = "global"
    k: int = 0
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


def group_values(groups: pd.Series | None, n: int) -> list[np.ndarray]:
    if groups is None:
        return [np.arange(n, dtype=int)]
    out = []
    reset = groups.reset_index(drop=True)
    for _, idx in reset.groupby(reset).groups.items():
        arr = np.asarray(list(idx), dtype=int)
        if len(arr) >= 2:
            out.append(arr)
    return out


def quantile_rewrite(base_prob: np.ndarray, score: np.ndarray, strength: float, groups: pd.Series | None = None) -> np.ndarray:
    base_prob = np.asarray(base_prob, dtype=np.float64)
    score = np.asarray(score, dtype=np.float64)
    target = base_prob.copy()
    for idx in group_values(groups, len(base_prob)):
        vals = np.sort(base_prob[idx])
        order = idx[np.argsort(score[idx])]
        target[order] = vals
    return sigmoid((1.0 - strength) * logit(base_prob) + strength * logit(target))


def tail_rewrite(base_prob: np.ndarray, score: np.ndarray, k: int, strength: float) -> np.ndarray:
    base_prob = np.asarray(base_prob, dtype=np.float64)
    score = np.asarray(score, dtype=np.float64)
    k = int(min(max(k, 1), len(score) // 2))
    order = np.argsort(score)
    selected = np.unique(np.r_[order[:k], order[-k:]])
    target = base_prob.copy()
    vals = np.sort(base_prob[selected])
    target[selected[np.argsort(score[selected])]] = vals
    out = base_prob.copy()
    out[selected] = sigmoid((1.0 - strength) * logit(base_prob[selected]) + strength * logit(target[selected]))
    return out


def get_state() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    base, latent, _, _ = h007.build_latent_features()
    ablation, _, _ = h007.evaluate_feature_sets(base, latent)
    chosen = h007.choose_model(ablation)
    return base, latent, chosen


def human_state_frame(latent_part: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(
        {
            "teacher_rank": latent_part["h005_mobility_teacher_rank"].to_numpy(dtype=np.float64),
            "teacher_z": latent_part["h005_mobility_teacher_z"].to_numpy(dtype=np.float64),
            "support_z": latent_part["h005_support_teacher_z"].to_numpy(dtype=np.float64),
            "low_energy": latent_part["jepa_mobility_low_energy"].to_numpy(dtype=np.float64),
            "agreement": latent_part["jepa_mobility_agreement"].to_numpy(dtype=np.float64),
        }
    )
    out["human_state"] = (
        0.35 * rank01(out["teacher_rank"])
        + 0.25 * rank01(out["support_z"])
        + 0.25 * rank01(out["low_energy"])
        + 0.15 * rank01(out["agreement"])
    )
    return out


def target_predictions(
    base: pd.DataFrame,
    latent: pd.DataFrame,
    chosen: dict[str, Any],
    targets: list[str],
    split_name: str | None,
) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray]]:
    train_mask = base["split"].eq("train").to_numpy()
    train = base.loc[train_mask].reset_index(drop=True)
    y_by_target = {target: train[target].to_numpy(dtype=int) for target in targets}
    base_x_train = base_label_matrix(train).reset_index(drop=True)
    cols = h007.FEATURE_SETS[str(chosen["feature_set"])]
    add_train = latent.loc[train_mask, cols].astype(float).reset_index(drop=True)
    plus_x_train = pd.concat([base_x_train, add_train], axis=1)
    c_value = float(chosen["C"])
    base_pred: dict[str, np.ndarray] = {}
    plus_pred: dict[str, np.ndarray] = {}
    if split_name is None:
        test = base.loc[~train_mask].sort_values(KEYS).reset_index(drop=True)
        test_idx = base.loc[~train_mask].sort_values(KEYS).index.to_numpy(dtype=int)
        base_x_test = base_label_matrix(test).reset_index(drop=True)
        add_test = latent.loc[test_idx, cols].astype(float).reset_index(drop=True)
        plus_x_test = pd.concat([base_x_test, add_test], axis=1)
        for target, y in y_by_target.items():
            base_pred[target] = h007.full_predict_binary(base_x_train, y, base_x_test, c_value)
            plus_pred[target] = h007.full_predict_binary(plus_x_train, y, plus_x_test, c_value)
    else:
        groups = groups_for(train, split_name).reset_index(drop=True)
        for target, y in y_by_target.items():
            base_pred[target] = h007.oof_predict_binary(base_x_train, y, groups, c_value)
            plus_pred[target] = h007.oof_predict_binary(plus_x_train, y, groups, c_value)
    return base_pred, plus_pred


def route_specs() -> list[RouteSpec]:
    specs: list[RouteSpec] = []
    signals = ["human_state", "teacher_rank", "low_energy", "target_plus_prob", "target_delta_pos", "target_delta_abs"]
    for route in ROUTES:
        for signal in signals:
            for group in ["global", "subject", "dateblock"]:
                for strength in [0.25, 0.40, 0.60, 0.85, 1.00]:
                    specs.append(RouteSpec(f"{route}_{signal}_{group}_s{strength:g}", route, "quantile", signal, strength, group=group))
            for k in [25, 50, 80, 120]:
                for strength in [0.50, 0.75, 1.00]:
                    specs.append(RouteSpec(f"{route}_{signal}_tail{k}_s{strength:g}", route, "tail", signal, strength, k=k))
    for route in ["mobility_core_q2up_s1down_s4up", "objective_mobility_s1down_s4up"]:
        for signal in ["human_state", "teacher_rank", "target_plus_prob"]:
            for strength in [0.60, 1.00]:
                specs.append(RouteSpec(f"reverse_{route}_{signal}_s{strength:g}", route, "quantile", signal, strength, reverse=True))
    return specs


def target_score(
    target: str,
    direction: int,
    signal: str,
    state: pd.DataFrame,
    base_pred: dict[str, np.ndarray],
    plus_pred: dict[str, np.ndarray],
    reverse: bool,
) -> np.ndarray:
    if signal == "target_plus_prob":
        score = plus_pred[target]
    elif signal == "target_delta_pos":
        score = np.maximum(logit(plus_pred[target]) - logit(base_pred[target]), 0.0)
    elif signal == "target_delta_abs":
        score = np.abs(logit(plus_pred[target]) - logit(base_pred[target]))
    else:
        score = state[signal].to_numpy(dtype=np.float64)
    signed = np.asarray(score, dtype=np.float64) * float(direction)
    if reverse:
        signed = -signed
    return signed


def apply_route(
    spec: RouteSpec,
    frame: pd.DataFrame,
    state: pd.DataFrame,
    base_pred: dict[str, np.ndarray],
    plus_pred: dict[str, np.ndarray],
    groups: pd.Series | None,
) -> dict[str, np.ndarray]:
    route = ROUTES[spec.route]
    out = {target: np.asarray(pred, dtype=np.float64).copy() for target, pred in base_pred.items()}
    for target, direction in route.items():
        score = target_score(target, direction, spec.score_signal, state, base_pred, plus_pred, spec.reverse)
        if spec.op == "quantile":
            out[target] = quantile_rewrite(base_pred[target], score, spec.strength, groups)
        elif spec.op == "tail":
            out[target] = tail_rewrite(base_pred[target], score, spec.k, spec.strength)
        else:
            raise ValueError(spec.op)
    return out


def route_logloss(y: pd.DataFrame, pred: dict[str, np.ndarray], targets: list[str]) -> float:
    vals = []
    for target in targets:
        vals.append(float(log_loss(y[target].to_numpy(dtype=int), np.clip(pred[target], 1e-6, 1 - 1e-6), labels=[0, 1])))
    return float(np.mean(vals))


def local_stress(base: pd.DataFrame, latent: pd.DataFrame, chosen: dict[str, Any]) -> pd.DataFrame:
    train_mask = base["split"].eq("train").to_numpy()
    train = base.loc[train_mask].reset_index(drop=True)
    latent_train = latent.loc[train_mask].reset_index(drop=True)
    all_targets = sorted({target for route in ROUTES.values() for target in route})
    specs = route_specs()
    rows: list[dict[str, Any]] = []
    for split_name in ["subject5", "dateblock5"]:
        base_pred, plus_pred = target_predictions(base, latent, chosen, all_targets, split_name)
        state = human_state_frame(latent_train)
        for spec in specs:
            groups = None
            if spec.group == "subject":
                groups = groups_for(train, "subject5").reset_index(drop=True)
            elif spec.group == "dateblock":
                groups = groups_for(train, "dateblock5").reset_index(drop=True)
            route_targets = list(ROUTES[spec.route])
            pred = apply_route(spec, train, state, base_pred, plus_pred, groups)
            base_loss = route_logloss(train, base_pred, route_targets)
            rewrite_loss = route_logloss(train, pred, route_targets)
            changed = np.zeros(len(train), dtype=bool)
            max_abs = 0.0
            mean_abs = []
            for target in route_targets:
                diff = np.abs(pred[target] - base_pred[target])
                changed |= diff > EPS
                max_abs = max(max_abs, float(diff.max()))
                mean_abs.append(float(diff.mean()))
            rows.append(
                {
                    "candidate_id": spec.candidate_id,
                    "route": spec.route,
                    "op": spec.op,
                    "score_signal": spec.score_signal,
                    "strength": spec.strength,
                    "group": spec.group,
                    "k": spec.k,
                    "reverse": spec.reverse,
                    "split": split_name,
                    "n_targets": len(route_targets),
                    "targets": ",".join(route_targets),
                    "base_loss": base_loss,
                    "rewrite_loss": rewrite_loss,
                    "delta_logloss": rewrite_loss - base_loss,
                    "changed_rows": int(changed.sum()),
                    "changed_cells": int(sum((np.abs(pred[t] - base_pred[t]) > EPS).sum() for t in route_targets)),
                    "mean_abs_prob_delta": float(np.mean(mean_abs)),
                    "max_abs_prob_delta": max_abs,
                }
            )
    local = pd.DataFrame(rows)
    summary = (
        local.groupby(["candidate_id", "route", "op", "score_signal", "strength", "group", "k", "reverse"])
        .agg(
            mean_delta=("delta_logloss", "mean"),
            worst_delta=("delta_logloss", "max"),
            best_delta=("delta_logloss", "min"),
            subject5_delta=("delta_logloss", lambda s: float(s.iloc[0])),
            dateblock5_delta=("delta_logloss", lambda s: float(s.iloc[1]) if len(s) > 1 else np.nan),
            max_abs_prob_delta_local=("max_abs_prob_delta", "max"),
            changed_rows_local=("changed_rows", "max"),
            changed_cells_local=("changed_cells", "max"),
        )
        .reset_index()
    )
    out = local.merge(summary, on=["candidate_id", "route", "op", "score_signal", "strength", "group", "k", "reverse"], how="left")
    out = out.sort_values(["reverse", "worst_delta", "mean_delta"], ascending=[True, True, True]).reset_index(drop=True)
    out.to_csv(LOCAL_OUT, index=False)
    return out


def select_specs(local: pd.DataFrame, limit: int = 90) -> list[RouteSpec]:
    cols = ["candidate_id", "route", "op", "score_signal", "strength", "group", "k", "reverse", "mean_delta", "worst_delta"]
    summary = local[cols].drop_duplicates().copy()
    robust = summary[(~summary["reverse"]) & (summary["worst_delta"] < 0.0)].sort_values(["worst_delta", "mean_delta"]).head(limit)
    controls = summary[summary["reverse"]].sort_values(["worst_delta", "mean_delta"]).head(8)
    chosen = pd.concat([robust, controls], ignore_index=True)
    specs = []
    for row in chosen.to_dict("records"):
        specs.append(
            RouteSpec(
                candidate_id=str(row["candidate_id"]),
                route=str(row["route"]),
                op=str(row["op"]),
                score_signal=str(row["score_signal"]),
                strength=float(row["strength"]),
                group=str(row["group"]),
                k=int(row["k"]),
                reverse=bool(row["reverse"]),
            )
        )
    return specs


def write_candidate(base_sub: pd.DataFrame, modified: dict[str, np.ndarray], candidate_id: str) -> Path:
    out = base_sub.copy()
    for target, values in modified.items():
        out[target] = np.clip(values, 1e-6, 1.0 - 1e-6)
    path = H010 / f"submission_h010_{safe_id(candidate_id, 120)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def materialize_test(base: pd.DataFrame, latent: pd.DataFrame, chosen: dict[str, Any], specs: list[RouteSpec]) -> tuple[pd.DataFrame, list[Path]]:
    train_mask = base["split"].eq("train").to_numpy()
    test = base.loc[~train_mask].sort_values(KEYS).reset_index(drop=True)
    test_idx = base.loc[~train_mask].sort_values(KEYS).index.to_numpy(dtype=int)
    latent_test = latent.loc[test_idx].reset_index(drop=True)
    all_targets = sorted({target for route in ROUTES.values() for target in route})
    base_pred, plus_pred = target_predictions(base, latent, chosen, all_targets, None)
    state = human_state_frame(latent_test)
    sample = normalize_sample_keys(test[KEYS])
    base_sub = load_anchor_sub(E247, sample)
    e247 = {target: base_sub[target].to_numpy(dtype=np.float64) for target in all_targets}
    rows: list[dict[str, Any]] = []
    paths: list[Path] = []
    for spec in specs:
        groups = None
        if spec.group == "subject":
            groups = test["subject_id"].astype(str).reset_index(drop=True)
        elif spec.group == "dateblock":
            groups = test["dateblock_group"].astype(str).reset_index(drop=True)
        route_targets = list(ROUTES[spec.route])
        rewrite_base = {target: e247[target] for target in all_targets}
        modified = apply_route(spec, test, state, rewrite_base, plus_pred, groups)
        modified = {target: modified[target] for target in route_targets}
        path = write_candidate(base_sub, modified, spec.candidate_id)
        paths.append(path)
        changed = np.zeros(len(test), dtype=bool)
        max_abs = 0.0
        mean_abs = []
        target_means = {}
        for target in route_targets:
            diff = np.abs(modified[target] - e247[target])
            changed |= diff > EPS
            max_abs = max(max_abs, float(diff.max()))
            mean_abs.append(float(diff.mean()))
            target_means[f"mean_{target}_before"] = float(e247[target].mean())
            target_means[f"mean_{target}_after"] = float(modified[target].mean())
        rows.append(
            {
                "candidate_id": spec.candidate_id,
                "route": spec.route,
                "op": spec.op,
                "score_signal": spec.score_signal,
                "strength": spec.strength,
                "group": spec.group,
                "k": spec.k,
                "reverse": spec.reverse,
                "targets": ",".join(route_targets),
                "file": rel(path),
                "basename": path.name,
                "changed_rows": int(changed.sum()),
                "changed_cells": int(sum((np.abs(modified[t] - e247[t]) > EPS).sum() for t in route_targets)),
                "mean_abs_prob_delta": float(np.mean(mean_abs)),
                "max_abs_prob_delta": max_abs,
                **target_means,
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
            "changed_rows_local",
            "changed_cells_local",
            "max_abs_prob_delta_local",
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
        "changed_Q1",
        "changed_Q2",
        "changed_S1",
        "changed_S4",
    ]
    merged = merged.merge(anatomy[[col for col in anatomy_cols if col in anatomy.columns]], on="basename", how="left")
    merged["local_robust_gate"] = (merged["worst_delta"] < 0.0) & (~merged["reverse"])
    merged["jackpot_shape_gate"] = (
        (merged["changed_cells"] <= 750)
        & (merged["max_abs_prob_delta"] <= 0.22)
        & (merged["mean_abs_prob_delta"] >= 0.002)
    )
    merged["jackpot_score"] = (
        110.0 * merged["worst_delta"].fillna(9.0)
        + 55.0 * merged["mean_delta"].fillna(9.0)
        + 5.0 * merged["pred_delta_vs_current_p90"].fillna(0.0)
        + 2.0 * merged["pred_delta_vs_current_mean"].fillna(0.0)
        + 0.015 * merged["incremental_bad_axis_vs_current"].abs().fillna(0.0)
        + 0.6 * merged["reverse"].astype(float)
    )
    merged["h010_decision"] = np.select(
        [
            merged["strict_promote_gate"].fillna(False).astype(bool),
            merged["local_robust_gate"] & merged["jackpot_shape_gate"] & (merged["pred_delta_vs_current_p90"] < 0.00075),
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
    rank = {
        "strict_upload_candidate": 0,
        "jackpot_candidate": 1,
        "local_only_high_risk": 2,
        "reverse_control": 3,
        "reject": 4,
    }
    gate = merged.copy()
    gate["decision_rank"] = gate["h010_decision"].map(rank).fillna(9).astype(int)
    gate = gate.sort_values(["decision_rank", "jackpot_score"]).reset_index(drop=True)
    gate.to_csv(GATE_OUT, index=False)
    family = (
        gate.groupby(["route"])
        .agg(
            n=("candidate_id", "count"),
            jackpot=("h010_decision", lambda s: int((s == "jackpot_candidate").sum())),
            local_only=("h010_decision", lambda s: int((s == "local_only_high_risk").sum())),
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
    rows = []
    primary = gate[gate["h010_decision"].isin(["strict_upload_candidate", "jackpot_candidate"])].head(3)
    if primary.empty:
        primary = gate[gate["h010_decision"].eq("local_only_high_risk")].head(2)
    controls = gate[gate["h010_decision"].eq("reverse_control")].head(2)
    for rec in pd.concat([primary, controls]).to_dict("records"):
        uploadsafe = ""
        if str(rec["h010_decision"]) in {"strict_upload_candidate", "jackpot_candidate", "local_only_high_risk"}:
            src = ROOT / str(rec["file"])
            dst = H010 / f"submission_h010_{safe_id(str(rec['candidate_id']), 82)}_uploadsafe.csv"
            shutil.copyfile(src, dst)
            uploadsafe = rel(dst)
        rows.append(
            {
                "candidate_id": rec["candidate_id"],
                "basename": rec["basename"],
                "file": rec["file"],
                "uploadsafe_file": uploadsafe,
                "decision": rec["h010_decision"],
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
        "route",
        "op",
        "score_signal",
        "strength",
        "group",
        "k",
        "split",
        "targets",
        "delta_logloss",
        "mean_delta",
        "worst_delta",
        "changed_cells_local",
        "max_abs_prob_delta_local",
    ]
    gate_cols = [
        "candidate_id",
        "h010_decision",
        "route",
        "op",
        "score_signal",
        "strength",
        "group",
        "k",
        "targets",
        "changed_cells",
        "max_abs_prob_delta",
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
        "changed_Q1",
        "changed_Q2",
        "changed_S1",
        "changed_S4",
    ]
    jackpot_n = int((gate["h010_decision"] == "jackpot_candidate").sum())
    best = gate.iloc[0]
    lines = [
        "# H010 Mobility Route Triad Jackpot",
        "",
        "## Question",
        "",
        "What if the hidden mobility state is not an S4-only signal, but a multi-target life-state route?",
        "",
        "## Hypothesis",
        "",
        "High mobility / obligation rows should receive a coupled route movement such as Q2-up, S1-down, and S4-up while preserving each target's E247 marginal distribution.",
        "",
        "## Chosen H007 State Model",
        "",
        f"- feature_set: `{chosen['feature_set']}`",
        f"- C: `{chosen['C']}`",
        "",
        "## Route Summary",
        "",
        md_table(family, n=30, floatfmt=".9f"),
        "",
        "## Top Local Stress",
        "",
        md_table(local[[col for col in local_cols if col in local.columns]].head(80), n=80, floatfmt=".9f"),
        "",
        "## Gate",
        "",
        md_table(gate[[col for col in gate_cols if col in gate.columns]].head(80), n=80, floatfmt=".9f"),
        "",
        "## Selector Scores",
        "",
        md_table(scores[[col for col in score_cols if col in scores.columns]].head(80), n=80, floatfmt=".9f"),
        "",
        "## Movement Anatomy",
        "",
        md_table(anatomy[[col for col in anatomy_cols if col in anatomy.columns]].head(80), n=80, floatfmt=".9f"),
        "",
        "## Selection",
        "",
        md_table(selection, n=10, floatfmt=".9f"),
        "",
        "## Interpretation",
        "",
        f"- candidate submissions materialized: `{len(candidates)}`",
        f"- jackpot candidates: `{jackpot_n}`",
        f"- best candidate: `{best['basename']}` -> `{best['h010_decision']}`",
        "",
    ]
    if jackpot_n:
        lines.append("A coupled human-state route survived the local splits and selector tolerance. This is stronger than an S4-only latent: it says the hidden state expresses itself across targets.")
    else:
        lines.append("The coupled route is locally meaningful but did not clear the selector tolerance. If submitted, it is a deliberate public sensor, not a conservative promotion.")
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
    base, latent, chosen = get_state()
    local = local_stress(base, latent, chosen)
    specs = select_specs(local)
    candidates, paths = materialize_test(base, latent, chosen, specs)
    scores = score_new_candidates(paths)
    anatomy = candidate_anatomy(paths)
    gate, family = build_gate_scores(candidates, local, scores, anatomy)
    selection = write_selection(gate)
    write_report(chosen, local, candidates, scores, anatomy, gate, family, selection)

    print(f"report={rel(REPORT_OUT)}")
    print("[chosen]", chosen)
    print("[inventory]", {"specs": len(specs), "jackpot": int((gate["h010_decision"] == "jackpot_candidate").sum())})
    print("[route summary]")
    print(family.round(9).to_string(index=False))
    print("[top gate]")
    cols = [
        "candidate_id",
        "h010_decision",
        "route",
        "op",
        "score_signal",
        "strength",
        "group",
        "k",
        "targets",
        "changed_cells",
        "max_abs_prob_delta",
        "worst_delta",
        "pred_delta_vs_current_mean",
        "pred_delta_vs_current_p90",
        "jackpot_score",
        "basename",
    ]
    print(gate[cols].head(40).round(9).to_string(index=False))
    if not selection.empty:
        print("[selection]")
        print(selection.to_string(index=False))


if __name__ == "__main__":
    main()
