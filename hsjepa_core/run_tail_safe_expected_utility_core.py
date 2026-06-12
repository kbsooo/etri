#!/usr/bin/env python3
"""Tail-safe expected-utility decoder core for HS-JEPA.

This public-free experiment follows a concrete failure mode:

    action-health AUC can improve while Log Loss utility gets worse.

HS-JEPA residual energy and subject-contrastive scores may rank "healthy"
actions, but Log Loss is dominated by negative tails.  This script therefore
learns three subject-heldout quantities for each row-target-action mode:

    expected_gain      = E[prior_loss - action_loss]
    predicted_tail     = E[max(-gain, 0)]
    toxic_tail_prob    = P[gain < -0.05]

It then releases actions by a tail-safe utility score rather than by health
probability alone.

No public LB ledger, prior submission probabilities, or proprietary embedding
APIs are used.  The action targets are constructed from OG train labels only.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import average_precision_score, mean_absolute_error, roc_auc_score
from sklearn.pipeline import make_pipeline

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hsjepa_core.run_action_support_world_model_core import TARGETS, target_context_columns, validate_submission  # noqa: E402
from hsjepa_core.run_lifelog_core_state_evidence import format_float, markdown_table  # noqa: E402
from hsjepa_core.run_subject_contrastive_action_support_core import fit_subject_contrastive_scores  # noqa: E402
from sleep_competition_adapter.target_route_conservation_decoder import (  # noqa: E402
    SAMPLE_SUBMISSION,
    build_listener_cells,
    route_family,
    short_hash,
)


OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "tail_safe_expected_utility_core"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "TAIL_SAFE_EXPECTED_UTILITY_CORE_KO.md"
RANDOM_SEED = 20260613
NULL_REPEATS = 24
TOXIC_TAIL_THRESHOLD = -0.05


def stable_seed(*parts: object) -> int:
    key = "::".join(map(str, parts)).encode("utf-8")
    return RANDOM_SEED + int(hashlib.sha256(key).hexdigest()[:8], 16) % 1009


def safe_auc(y: np.ndarray, score: np.ndarray) -> float | None:
    y = np.asarray(y, dtype=int)
    score = np.asarray(score, dtype=np.float64)
    mask = np.isfinite(score)
    if mask.sum() == 0 or len(np.unique(y[mask])) < 2:
        return None
    return float(roc_auc_score(y[mask], score[mask]))


def safe_ap(y: np.ndarray, score: np.ndarray) -> float | None:
    y = np.asarray(y, dtype=int)
    score = np.asarray(score, dtype=np.float64)
    mask = np.isfinite(score)
    if mask.sum() == 0 or len(np.unique(y[mask])) < 2:
        return None
    return float(average_precision_score(y[mask], score[mask]))


def regressor_factory(seed: int) -> Any:
    return make_pipeline(
        SimpleImputer(strategy="median"),
        HistGradientBoostingRegressor(
            learning_rate=0.035,
            max_leaf_nodes=14,
            min_samples_leaf=18,
            l2_regularization=0.18,
            random_state=seed,
        ),
    )


def classifier_factory(seed: int) -> Any:
    return make_pipeline(
        SimpleImputer(strategy="median"),
        HistGradientBoostingClassifier(
            learning_rate=0.032,
            max_leaf_nodes=14,
            min_samples_leaf=18,
            l2_regularization=0.22,
            random_state=seed,
        ),
    )


def add_subject_contrastive_scores(
    train_cells: pd.DataFrame,
    test_cells: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    resid_cols = [
        col
        for col in train_cells.columns
        if (col.startswith("wm_resid_") or col.startswith("wm_energy"))
        and col in test_cells.columns
    ]
    metrics, oof_predictions, test_predictions, score_summary = fit_subject_contrastive_scores(
        train_cells,
        test_cells,
        {"world_residual_energy_pair": resid_cols},
    )
    train = train_cells.copy()
    test = test_cells.copy()
    for col in oof_predictions.columns:
        if col.startswith("support_score_"):
            train[col] = oof_predictions[col].to_numpy(dtype=np.float64)
    for col in test_predictions.columns:
        if col.startswith("support_score_"):
            test[col] = test_predictions[col].to_numpy(dtype=np.float64)
    return train, test, metrics, score_summary


def add_mode_features(cells: pd.DataFrame, mode: str, train: bool) -> pd.DataFrame:
    out = cells.copy()
    out["cell_id"] = cells.index.to_numpy(dtype=np.int64)
    out["decoder_action"] = mode
    out["decoder_raw"] = float(mode == "raw_memory_release")
    out["decoder_inverse"] = float(mode == "inverse_toxic_memory")
    if mode == "raw_memory_release":
        out["action_prob"] = out["candidate_prob"].astype(float)
        if train:
            out["effective_gain"] = out["realized_gain"].astype(float)
    else:
        out["action_prob"] = out["inverse_prob"].astype(float)
        if train:
            out["effective_gain"] = out["inverse_realized_gain"].astype(float)
    out["action_delta"] = out["action_prob"].astype(float) - out["prior_prob"].astype(float)
    out["action_abs_delta"] = out["action_delta"].abs()
    out["target_route_family"] = out["target"].map(route_family)

    listener_score = "support_score_target_interaction_world_residual_energy"
    if listener_score in out.columns:
        out["listener_mode_alignment"] = np.where(
            out["decoder_action"].eq("raw_memory_release"),
            out[listener_score].astype(float),
            1.0 - out[listener_score].astype(float),
        )
    for col in [
        "support_score_binary_preference__world_residual_energy_pair",
        "support_score_tail_weighted_preference__world_residual_energy_pair",
    ]:
        if col in out.columns:
            out[f"mode_alignment__{col}"] = np.where(
                out["decoder_action"].eq("raw_memory_release"),
                out[col].astype(float),
                1.0 - out[col].astype(float),
            )

    for family in sorted(out["target_route_family"].dropna().unique()):
        out[f"route_family__{family}"] = out["target_route_family"].eq(family).astype(float)
    if train:
        out["healthy_action"] = out["effective_gain"].gt(0.0).astype(int)
        out["toxic_tail"] = out["effective_gain"].lt(TOXIC_TAIL_THRESHOLD).astype(int)
        out["tail_loss"] = np.maximum(-out["effective_gain"].astype(float), 0.0)
        out["gain_abs_weight"] = 1.0 + np.minimum(out["effective_gain"].abs() / 0.05, 8.0)
    return out


def build_mode_tables(train_cells: pd.DataFrame, test_cells: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    train_modes = pd.concat(
        [
            add_mode_features(train_cells, "raw_memory_release", train=True),
            add_mode_features(train_cells, "inverse_toxic_memory", train=True),
        ],
        ignore_index=True,
    )
    test_modes = pd.concat(
        [
            add_mode_features(test_cells, "raw_memory_release", train=False),
            add_mode_features(test_cells, "inverse_toxic_memory", train=False),
        ],
        ignore_index=True,
    )
    for col in sorted(set(train_modes.columns) - set(test_modes.columns)):
        if col.startswith("route_family__"):
            test_modes[col] = 0.0
    for col in sorted(set(test_modes.columns) - set(train_modes.columns)):
        if col.startswith("route_family__"):
            train_modes[col] = 0.0
    return train_modes, test_modes


def utility_feature_columns(train_modes: pd.DataFrame, test_modes: pd.DataFrame) -> list[str]:
    base_cols = [
        "prior_prob",
        "candidate_prob",
        "inverse_prob",
        "action_prob",
        "action_move",
        "abs_action_move",
        "action_move_rank",
        "decisive_action",
        "action_delta",
        "action_abs_delta",
        "decoder_raw",
        "decoder_inverse",
        "listener_mode_alignment",
    ]
    prefix_cols = [
        col
        for col in train_modes.columns
        if col.startswith("wm_resid_")
        or col.startswith("wm_energy")
        or col.startswith("target_interaction__")
        or col.startswith("family_interaction__")
        or col.startswith("route_family__")
        or col.startswith("support_score_")
        or col.startswith("mode_alignment__support_score_")
    ]
    cols = target_context_columns() + base_cols + prefix_cols
    return [col for col in cols if col in train_modes.columns and col in test_modes.columns]


def fit_subject_heldout_utility_models(
    train_modes: pd.DataFrame,
    test_modes: pd.DataFrame,
    feature_cols: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    subjects = sorted(train_modes["subject_id"].astype(str).unique())
    y_gain = train_modes["effective_gain"].astype(float).to_numpy()
    y_tail_loss = train_modes["tail_loss"].astype(float).to_numpy()
    y_health = train_modes["healthy_action"].astype(int).to_numpy()
    y_toxic = train_modes["toxic_tail"].astype(int).to_numpy()
    weights = train_modes["gain_abs_weight"].astype(float).to_numpy()

    oof_gain = np.zeros(len(train_modes), dtype=np.float64)
    oof_tail_loss = np.zeros(len(train_modes), dtype=np.float64)
    oof_health = np.zeros(len(train_modes), dtype=np.float64)
    oof_toxic = np.zeros(len(train_modes), dtype=np.float64)

    for subject in subjects:
        tr = train_modes.index[~train_modes["subject_id"].astype(str).eq(subject)].to_numpy()
        va = train_modes.index[train_modes["subject_id"].astype(str).eq(subject)].to_numpy()
        gain_model = regressor_factory(stable_seed("tail-safe-gain", subject))
        tail_model = regressor_factory(stable_seed("tail-safe-tail-loss", subject))
        gain_model.fit(train_modes.iloc[tr][feature_cols], y_gain[tr], histgradientboostingregressor__sample_weight=weights[tr])
        tail_model.fit(train_modes.iloc[tr][feature_cols], y_tail_loss[tr], histgradientboostingregressor__sample_weight=weights[tr])
        oof_gain[va] = gain_model.predict(train_modes.iloc[va][feature_cols])
        oof_tail_loss[va] = np.maximum(tail_model.predict(train_modes.iloc[va][feature_cols]), 0.0)

        if len(np.unique(y_health[tr])) < 2:
            oof_health[va] = float(y_health[tr].mean())
        else:
            health_model = classifier_factory(stable_seed("tail-safe-health", subject))
            health_model.fit(train_modes.iloc[tr][feature_cols], y_health[tr])
            oof_health[va] = health_model.predict_proba(train_modes.iloc[va][feature_cols])[:, 1]

        if len(np.unique(y_toxic[tr])) < 2:
            oof_toxic[va] = float(y_toxic[tr].mean())
        else:
            toxic_model = classifier_factory(stable_seed("tail-safe-toxic", subject))
            toxic_model.fit(train_modes.iloc[tr][feature_cols], y_toxic[tr], histgradientboostingclassifier__sample_weight=weights[tr])
            oof_toxic[va] = toxic_model.predict_proba(train_modes.iloc[va][feature_cols])[:, 1]

    test_gain_model = regressor_factory(stable_seed("tail-safe-gain", "full-test"))
    test_tail_model = regressor_factory(stable_seed("tail-safe-tail-loss", "full-test"))
    test_gain_model.fit(train_modes[feature_cols], y_gain, histgradientboostingregressor__sample_weight=weights)
    test_tail_model.fit(train_modes[feature_cols], y_tail_loss, histgradientboostingregressor__sample_weight=weights)
    test_gain = test_gain_model.predict(test_modes[feature_cols])
    test_tail_loss = np.maximum(test_tail_model.predict(test_modes[feature_cols]), 0.0)

    if len(np.unique(y_health)) < 2:
        test_health = np.full(len(test_modes), float(y_health.mean()), dtype=np.float64)
    else:
        health_model = classifier_factory(stable_seed("tail-safe-health", "full-test"))
        health_model.fit(train_modes[feature_cols], y_health)
        test_health = health_model.predict_proba(test_modes[feature_cols])[:, 1]

    if len(np.unique(y_toxic)) < 2:
        test_toxic = np.full(len(test_modes), float(y_toxic.mean()), dtype=np.float64)
    else:
        toxic_model = classifier_factory(stable_seed("tail-safe-toxic", "full-test"))
        toxic_model.fit(train_modes[feature_cols], y_toxic, histgradientboostingclassifier__sample_weight=weights)
        test_toxic = toxic_model.predict_proba(test_modes[feature_cols])[:, 1]

    train_scored = train_modes.copy()
    test_scored = test_modes.copy()
    for frame, pred_gain, pred_tail, pred_health, pred_toxic in [
        (train_scored, oof_gain, oof_tail_loss, oof_health, oof_toxic),
        (test_scored, test_gain, test_tail_loss, test_health, test_toxic),
    ]:
        frame["predicted_gain"] = pred_gain
        frame["predicted_tail_loss"] = pred_tail
        frame["predicted_health_prob"] = pred_health
        frame["predicted_toxic_tail_prob"] = pred_toxic
        frame["tail_safe_utility"] = frame["predicted_gain"] - 1.20 * frame["predicted_tail_loss"] - 0.08 * frame["predicted_toxic_tail_prob"]
        frame["health_weighted_utility"] = frame["predicted_health_prob"] * frame["predicted_gain"] - 1.50 * frame["predicted_toxic_tail_prob"]
        frame["pessimistic_utility"] = frame["predicted_gain"] - 2.00 * frame["predicted_tail_loss"] - 0.20 * frame["predicted_toxic_tail_prob"]
        frame["health_score_only"] = frame["predicted_health_prob"]

    metric_rows = [
        {"metric": "gain_mae", "value": float(mean_absolute_error(y_gain, oof_gain))},
        {"metric": "tail_loss_mae", "value": float(mean_absolute_error(y_tail_loss, oof_tail_loss))},
        {"metric": "health_auc", "value": safe_auc(y_health, oof_health)},
        {"metric": "health_ap", "value": safe_ap(y_health, oof_health)},
        {"metric": "toxic_tail_auc", "value": safe_auc(y_toxic, oof_toxic)},
        {"metric": "toxic_tail_ap", "value": safe_ap(y_toxic, oof_toxic)},
        {"metric": "realized_gain_sum_all_modes", "value": float(y_gain.sum())},
        {"metric": "positive_action_rate", "value": float(y_health.mean())},
        {"metric": "toxic_tail_rate", "value": float(y_toxic.mean())},
    ]
    return train_scored, test_scored, pd.DataFrame(metric_rows)


def choose_mode_indices(modes: pd.DataFrame, target: str, score_col: str, policy: str, fraction: float) -> np.ndarray:
    if policy == "hold":
        return np.array([], dtype=int)
    part = modes[modes["target"].eq(target)].copy()
    if "decisive" in policy:
        part = part[part["decisive_action"].eq(1)]
    if part.empty:
        return np.array([], dtype=int)
    part = part.sort_values(score_col, ascending=False, kind="mergesort")
    part = part.drop_duplicates("cell_id", keep="first")
    k = max(1, int(round(len(part) * fraction)))
    return part.head(k).index.to_numpy(dtype=int)


def evaluate_policy(modes: pd.DataFrame, target: str, score_col: str, policy: str, fraction: float, null_repeats: int) -> dict[str, Any]:
    selected = choose_mode_indices(modes, target, score_col, policy, fraction)
    selected_frame = modes.loc[selected] if len(selected) else modes.iloc[0:0]
    gains = selected_frame["effective_gain"].to_numpy(dtype=np.float64) if len(selected_frame) else np.array([], dtype=np.float64)
    subject_gain = (
        selected_frame.groupby("subject_id", observed=True)["effective_gain"].sum()
        if len(selected_frame)
        else pd.Series(dtype=float)
    )
    rng = np.random.default_rng(stable_seed("tail-safe-null", target, score_col, policy, fraction))
    null_sums: list[float] = []
    if len(selected):
        part_idx = modes.index[modes["target"].eq(target)].to_numpy()
        original = modes.loc[part_idx, score_col].to_numpy(dtype=np.float64)
        for _ in range(null_repeats):
            shuffled = original.copy()
            rng.shuffle(shuffled)
            temp = modes.loc[part_idx].copy()
            temp[score_col] = shuffled
            temp_selected = choose_mode_indices(temp, target, score_col, policy, fraction)
            null_sums.append(float(temp.loc[temp_selected, "effective_gain"].sum()) if len(temp_selected) else 0.0)
    null_mean = float(np.mean(null_sums)) if null_sums else 0.0
    null_std = float(np.std(null_sums, ddof=1)) if len(null_sums) > 1 else np.nan
    gain_sum = float(gains.sum()) if len(gains) else 0.0
    positive_rate = float((gains > 0).mean()) if len(gains) else np.nan
    positive_subjects = int((subject_gain > 0).sum()) if len(subject_gain) else 0
    negative_subjects = int((subject_gain < 0).sum()) if len(subject_gain) else 0
    raw_count = int(selected_frame["decoder_action"].eq("raw_memory_release").sum()) if len(selected_frame) else 0
    inverse_count = int(selected_frame["decoder_action"].eq("inverse_toxic_memory").sum()) if len(selected_frame) else 0
    z = (gain_sum - null_mean) / null_std if np.isfinite(null_std) and null_std else np.nan
    utility_score = (
        gain_sum
        + 0.35 * (gain_sum - null_mean)
        + 0.10 * (0.0 if not np.isfinite(z) else z)
        + 0.35 * max(positive_rate if np.isfinite(positive_rate) else 0.0, 0.0)
        + 0.20 * positive_subjects
        - 0.75 * negative_subjects
    )
    return {
        "target": target,
        "score_col": score_col,
        "policy": policy,
        "fraction": fraction,
        "selected_cells": int(len(selected_frame)),
        "selected_gain_sum": gain_sum,
        "selected_mean_gain": float(gains.mean()) if len(gains) else 0.0,
        "selected_positive_gain_rate": positive_rate,
        "active_subjects": int(len(subject_gain)),
        "positive_subjects": positive_subjects,
        "negative_subjects": negative_subjects,
        "raw_action_count": raw_count,
        "inverse_action_count": inverse_count,
        "null_gain_mean": null_mean,
        "null_gain_std": null_std,
        "gain_lift_vs_null": gain_sum - null_mean,
        "gain_z_vs_null": z,
        "tail_safe_policy_score": utility_score,
    }


def policy_grid(modes: pd.DataFrame, null_repeats: int) -> pd.DataFrame:
    score_cols = [
        "predicted_gain",
        "tail_safe_utility",
        "health_weighted_utility",
        "pessimistic_utility",
        "health_score_only",
    ]
    policies = ["top_all", "top_decisive"]
    fractions = [0.02, 0.04, 0.06, 0.08, 0.10, 0.14, 0.18, 0.25]
    rows: list[dict[str, Any]] = []
    for target in TARGETS:
        rows.append(evaluate_policy(modes, target, "predicted_gain", "hold", 0.0, 0))
        for score_col in score_cols:
            for fraction in fractions:
                for policy in policies:
                    rows.append(evaluate_policy(modes, target, score_col, policy, fraction, null_repeats))
    return pd.DataFrame(rows)


def choose_target_policies(grid: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for target, part in grid.groupby("target", observed=True):
        hold = part[part["policy"].eq("hold")].iloc[0].to_dict()
        viable = part[
            ~part["policy"].eq("hold")
            & (part["selected_gain_sum"] > 0.0)
            & (part["gain_lift_vs_null"] > 0.0)
            & (part["selected_positive_gain_rate"].fillna(0.0) >= 0.56)
            & (part["negative_subjects"] <= 4)
        ].copy()
        if viable.empty:
            hold["accepted"] = False
            hold["accept_reason"] = "no_tail_safe_policy_passed"
            rows.append(hold)
            continue
        row = viable.sort_values(["tail_safe_policy_score", "selected_gain_sum"], ascending=False).iloc[0].to_dict()
        row["accepted"] = True
        row["accept_reason"] = "positive_expected_utility_tail_safe"
        rows.append(row)
    return pd.DataFrame(rows).sort_values("target")


def apply_policies(modes: pd.DataFrame, chosen: pd.DataFrame) -> pd.DataFrame:
    released = pd.Series(False, index=modes.index)
    for _, row in chosen.iterrows():
        if not bool(row["accepted"]):
            continue
        idx = choose_mode_indices(modes, str(row["target"]), str(row["score_col"]), str(row["policy"]), float(row["fraction"]))
        released.loc[idx] = True
    audit = modes.copy()
    audit["released"] = released.to_numpy()
    audit["effective_gain_released"] = np.where(audit["released"], audit["effective_gain"], 0.0) if "effective_gain" in audit else 0.0
    return audit


def nested_subject_stress(modes: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    subjects = sorted(modes["subject_id"].astype(str).unique())
    fold_rows: list[dict[str, Any]] = []
    route_rows: list[dict[str, Any]] = []
    audits: list[pd.DataFrame] = []
    for subject in subjects:
        selector = modes[~modes["subject_id"].astype(str).eq(subject)].copy()
        heldout = modes[modes["subject_id"].astype(str).eq(subject)].copy()
        chosen = choose_target_policies(policy_grid(selector, null_repeats=8))
        audit = apply_policies(heldout, chosen)
        audit["heldout_subject"] = subject
        audits.append(audit)
        selected = audit[audit["released"]].copy()
        gains = selected["effective_gain"].to_numpy(dtype=np.float64) if len(selected) else np.array([], dtype=np.float64)
        fold_rows.append(
            {
                "heldout_subject": subject,
                "selected_cells": int(len(selected)),
                "gain_sum": float(gains.sum()) if len(gains) else 0.0,
                "mean_gain": float(gains.mean()) if len(gains) else 0.0,
                "positive_gain_rate": float((gains > 0).mean()) if len(gains) else np.nan,
                "accepted_targets": ",".join(chosen.loc[chosen["accepted"].eq(True), "target"].astype(str).tolist()),
            }
        )
        for _, route in chosen.iterrows():
            target_selected = selected[selected["target"].eq(route["target"])]
            route_rows.append(
                {
                    "heldout_subject": subject,
                    "target": str(route["target"]),
                    "accepted": bool(route["accepted"]),
                    "score_col": str(route["score_col"]),
                    "policy": str(route["policy"]),
                    "fraction": float(route["fraction"]),
                    "heldout_selected_cells": int(len(target_selected)),
                    "heldout_gain_sum": float(target_selected["effective_gain"].sum()) if len(target_selected) else 0.0,
                    "heldout_positive_gain_rate": float((target_selected["effective_gain"] > 0).mean()) if len(target_selected) else np.nan,
                    "raw_action_count": int(target_selected["decoder_action"].eq("raw_memory_release").sum()) if len(target_selected) else 0,
                    "inverse_action_count": int(target_selected["decoder_action"].eq("inverse_toxic_memory").sum()) if len(target_selected) else 0,
                }
            )
    return pd.DataFrame(fold_rows), pd.DataFrame(route_rows), pd.concat(audits, ignore_index=True)


def summarize_nested_targets(nested_audit: pd.DataFrame) -> pd.DataFrame:
    selected = nested_audit[nested_audit["released"]].copy()
    if selected.empty:
        return pd.DataFrame(columns=["target", "selected_cells", "gain_sum", "positive_gain_rate"])
    by_subject = selected.groupby(["heldout_subject", "target"], observed=True)["effective_gain"].sum().reset_index()
    subject_summary = (
        by_subject.groupby("target", observed=True)
        .agg(
            positive_subjects=("effective_gain", lambda x: int((x > 0).sum())),
            negative_subjects=("effective_gain", lambda x: int((x < 0).sum())),
        )
        .reset_index()
    )
    target_summary = (
        selected.groupby("target", observed=True)
        .agg(
            selected_cells=("effective_gain", "size"),
            gain_sum=("effective_gain", "sum"),
            mean_gain=("effective_gain", "mean"),
            positive_gain_rate=("effective_gain", lambda x: float((x > 0).mean())),
            raw_action_count=("decoder_raw", "sum"),
            inverse_action_count=("decoder_inverse", "sum"),
        )
        .reset_index()
    )
    return target_summary.merge(subject_summary, on="target", how="left").sort_values("target")


def stable_policies(full_chosen: pd.DataFrame, route_rows: pd.DataFrame, target_summary: pd.DataFrame) -> pd.DataFrame:
    stats = target_summary.set_index("target").to_dict(orient="index") if not target_summary.empty else {}
    accept_rate = route_rows.groupby("target", observed=True)["accepted"].mean().to_dict()
    rows: list[dict[str, Any]] = []
    for _, route in full_chosen.iterrows():
        row = route.to_dict()
        target = str(row["target"])
        target_stats = stats.get(target, {})
        gain_sum = float(target_stats.get("gain_sum", 0.0))
        positive_subjects = int(target_stats.get("positive_subjects", 0))
        negative_subjects = int(target_stats.get("negative_subjects", 0))
        positive_rate = float(target_stats.get("positive_gain_rate", 0.0)) if pd.notna(target_stats.get("positive_gain_rate", np.nan)) else 0.0
        stable = (
            bool(row.get("accepted", False))
            and float(accept_rate.get(target, 0.0)) >= 0.50
            and gain_sum > 0.0
            and positive_subjects >= max(2, negative_subjects)
            and positive_rate >= 0.56
        )
        row["accepted"] = stable
        row["heldout_accept_rate"] = float(accept_rate.get(target, 0.0))
        row["heldout_gain_sum"] = gain_sum
        row["heldout_positive_subjects"] = positive_subjects
        row["heldout_negative_subjects"] = negative_subjects
        row["heldout_positive_gain_rate"] = positive_rate
        row["accept_reason"] = "tail_safe_subjectheldout_stable" if stable else "failed_tail_safe_subjectheldout"
        if not stable:
            row["policy"] = "hold"
            row["fraction"] = 0.0
            row["selected_cells"] = 0
        rows.append(row)
    return pd.DataFrame(rows).sort_values("target")


def apply_policies_to_test(
    sample: pd.DataFrame,
    test_modes: pd.DataFrame,
    chosen: pd.DataFrame,
    train_priors: dict[str, float],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    out = sample.copy()
    for target in TARGETS:
        out[target] = float(train_priors[target])
    released = pd.Series(False, index=test_modes.index)
    for _, route in chosen.iterrows():
        if not bool(route["accepted"]):
            continue
        idx = choose_mode_indices(test_modes, str(route["target"]), str(route["score_col"]), str(route["policy"]), float(route["fraction"]))
        released.loc[idx] = True
    audit = test_modes.copy()
    audit["released"] = released.to_numpy()
    for _, row in audit[audit["released"]].iterrows():
        out.at[int(row["row"]), str(row["target"])] = float(row["action_prob"])
    out[TARGETS] = out[TARGETS].clip(1e-5, 1.0 - 1e-5)
    return out, audit


def build_markdown(
    summary: dict[str, Any],
    utility_metrics: pd.DataFrame,
    full_chosen: pd.DataFrame,
    nested_subject_summary: pd.DataFrame,
    nested_target_summary: pd.DataFrame,
    stable: pd.DataFrame,
    policy_board: pd.DataFrame,
    contrastive_summary: pd.DataFrame,
) -> str:
    top_policy = policy_board.sort_values(["tail_safe_policy_score", "selected_gain_sum"], ascending=False)
    return f"""# Tail-Safe Expected Utility Core

## 한 줄 요약

HS-JEPA core score를 `건강한 action 확률`로 쓰지 않고,
Log Loss 관점의 expected gain과 negative-tail risk를 직접 예측해
tail-safe utility decoder로 바꿨다.

## 빠른 판정: 이것은 HS-JEPA인가?

부분적으로 맞다. 정확히는 **HS-JEPA core와 competition adapter 사이의 decoder-boundary 실험**이다.

```text
HS-JEPA core question
  = visible human context -> hidden human-state/action-health representation prediction

이 문서의 question
  = predicted hidden action-health geometry -> Log Loss expected utility / tail-risk action
```

따라서 이 문서를 HS-JEPA 본체로 소개하면 JEPA 느낌이 흐려진다.
논문에서는 masked-context world model과 subject-contrastive action-support core를 먼저 설명하고,
이 실험은 `core representation을 Log Loss action으로 안전하게 번역하려면 tail-safe utility decoder가 필요하다`
는 증거로 배치해야 한다.

```text
masked world-state residual/energy
  -> listener + subject-contrastive support context
  -> expected gain / tail loss / toxic-tail probability
  -> tail-safe row-target-action assignment
```

## 왜 필요한가

이전 subject-contrastive 실험에서 중요한 모순이 나왔다.

```text
shortcut/action-only score는 AUC가 높아도 selected Log Loss gain이 음수였다.
world residual-energy score만 약한 positive utility를 냈다.
```

즉 HS-JEPA core를 증명하려면 AUC가 아니라 utility를 봐야 한다.
이 실험은 action-health를 sign classification이 아니라 expected utility problem으로 재정의한다.

## 사용하지 않은 정보

- public LB ledger: `{summary["uses_public_score_ledger"]}`
- prior submission probability: `{summary["uses_prior_submission_probabilities"]}`
- proprietary embedding API: `{summary["uses_proprietary_embedding_api"]}`

## Verdict

- verdict: `{summary["verdict"]}`
- full OOF selected gain: `{format_float(summary["full_oof_gain_sum"], 6)}`
- nested heldout gain: `{format_float(summary["nested_heldout_gain_sum"], 6)}`
- stable targets: `{summary["stable_targets"]}`
- stable OOF gain: `{format_float(summary["stable_oof_gain_sum"], 6)}`
- candidate policy source: `{summary["candidate_policy_source"]}`
- released test cells: `{summary["released_test_cells"]}`

## Utility Model Metrics

{markdown_table(utility_metrics, ["metric", "value"], max_rows=20)}

## Subject-Contrastive Score Summary

{markdown_table(contrastive_summary, ["feature_set", "base_feature_set", "pairwise_weight_mode", "support_auc", "support_ap", "score_mean", "score_std"], max_rows=20)}

## Full OOF Chosen Policies

{markdown_table(full_chosen, ["target", "accepted", "score_col", "policy", "fraction", "selected_cells", "selected_gain_sum", "selected_positive_gain_rate", "positive_subjects", "negative_subjects", "raw_action_count", "inverse_action_count", "gain_lift_vs_null", "tail_safe_policy_score", "accept_reason"], max_rows=20)}

## Nested Subject-Heldout Summary

{markdown_table(nested_subject_summary, ["heldout_subject", "selected_cells", "gain_sum", "mean_gain", "positive_gain_rate", "accepted_targets"], max_rows=20)}

## Nested Target Summary

{markdown_table(nested_target_summary, ["target", "selected_cells", "gain_sum", "mean_gain", "positive_gain_rate", "raw_action_count", "inverse_action_count", "positive_subjects", "negative_subjects"], max_rows=20)}

## Stable Policies Used For Candidate

{markdown_table(stable, ["target", "accepted", "score_col", "policy", "fraction", "heldout_accept_rate", "heldout_gain_sum", "heldout_positive_subjects", "heldout_negative_subjects", "heldout_positive_gain_rate", "accept_reason"], max_rows=20)}

## Policy Board Top Rows

{markdown_table(top_policy, ["target", "score_col", "policy", "fraction", "selected_cells", "selected_gain_sum", "selected_positive_gain_rate", "positive_subjects", "negative_subjects", "gain_lift_vs_null", "gain_z_vs_null", "tail_safe_policy_score"], max_rows=32)}

## Anchor-Free Candidate

- candidate: `{summary["candidate_file"]}`
- validation: `{summary["validation"]}`

## 해석

좋은 결과:

```text
tail-safe expected utility가 health probability보다 좋은 full/nested gain을 만들면,
HS-JEPA core의 병목은 representation 부재가 아니라 objective/decoder mismatch였다는 뜻이다.
```

나쁜 결과:

```text
expected utility와 tail risk를 직접 예측해도 nested heldout에서 무너지면,
현재 core representation은 action toxicity sign을 약하게 읽지만
tail magnitude까지 subject-general하게 읽지는 못한다.
```
"""


def run() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    train_cells, test_cells, train_priors, _view_metrics = build_listener_cells()
    train_cells, test_cells, contrastive_metrics, contrastive_summary = add_subject_contrastive_scores(train_cells, test_cells)
    train_modes, test_modes = build_mode_tables(train_cells, test_cells)
    feature_cols = utility_feature_columns(train_modes, test_modes)
    train_scored, test_scored, utility_metrics = fit_subject_heldout_utility_models(train_modes, test_modes, feature_cols)

    grid = policy_grid(train_scored, null_repeats=NULL_REPEATS)
    full_chosen = choose_target_policies(grid)
    full_audit = apply_policies(train_scored, full_chosen)
    nested_subject_summary, nested_route_rows, nested_audit = nested_subject_stress(train_scored)
    nested_target_summary = summarize_nested_targets(nested_audit)
    stable = stable_policies(full_chosen, nested_route_rows, nested_target_summary)

    stable_count = int(stable["accepted"].sum()) if "accepted" in stable else 0
    candidate_policy = stable if stable_count > 0 else full_chosen
    candidate_policy_source = "stable_subjectheldout" if stable_count > 0 else "full_oof_sensor"

    sample = pd.read_csv(SAMPLE_SUBMISSION)
    candidate, test_audit = apply_policies_to_test(sample, test_scored, candidate_policy, train_priors)
    validation = validate_submission(candidate, sample)
    if not validation["valid"]:
        raise ValueError(f"candidate is not upload-safe: {validation['problems']}")
    candidate_name = f"submission_hsjepa_tail_safe_expected_utility_core_anchor_free_{short_hash(candidate)}_uploadsafe.csv"

    selected_full = full_audit[full_audit["released"]].copy()
    selected_stable_oof = apply_policies(train_scored, stable)
    stable_selected = selected_stable_oof[selected_stable_oof["released"]].copy()
    nested_selected = nested_audit[nested_audit["released"]].copy()
    full_oof_gain = float(selected_full["effective_gain"].sum()) if len(selected_full) else 0.0
    nested_gain = float(nested_selected["effective_gain"].sum()) if len(nested_selected) else 0.0
    stable_oof_gain = float(stable_selected["effective_gain"].sum()) if len(stable_selected) else 0.0
    stable_targets = stable.loc[stable["accepted"].eq(True), "target"].astype(str).tolist() if "accepted" in stable else []
    verdict = (
        "tail_safe_expected_utility_subjectheldout_positive"
        if nested_gain > 0 and stable_count > 0
        else "tail_safe_expected_utility_oof_positive_subjectheldout_fragile"
        if full_oof_gain > 0
        else "tail_safe_expected_utility_negative"
    )

    summary = {
        "package": "tail_safe_expected_utility_core",
        "status": "tail_safe_expected_utility_core_ready",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "verdict": verdict,
        "full_oof_gain_sum": full_oof_gain,
        "full_oof_selected_cells": int(len(selected_full)),
        "nested_heldout_gain_sum": nested_gain,
        "nested_heldout_selected_cells": int(len(nested_selected)),
        "stable_targets": stable_targets,
        "stable_oof_gain_sum": stable_oof_gain,
        "stable_oof_selected_cells": int(len(stable_selected)),
        "candidate_policy_source": candidate_policy_source,
        "released_test_cells": int(test_audit["released"].sum()),
        "candidate_file": candidate_name,
        "validation": validation,
    }

    grid.to_csv(OUT_DIR / "tail_safe_policy_grid.csv", index=False)
    full_chosen.to_csv(OUT_DIR / "tail_safe_full_chosen_policies.csv", index=False)
    full_audit.to_csv(OUT_DIR / "tail_safe_full_oof_action_audit.csv", index=False)
    nested_subject_summary.to_csv(OUT_DIR / "tail_safe_nested_subject_summary.csv", index=False)
    nested_route_rows.to_csv(OUT_DIR / "tail_safe_nested_route_rows.csv", index=False)
    nested_target_summary.to_csv(OUT_DIR / "tail_safe_nested_target_summary.csv", index=False)
    stable.to_csv(OUT_DIR / "tail_safe_stable_policies.csv", index=False)
    utility_metrics.to_csv(OUT_DIR / "tail_safe_utility_model_metrics.csv", index=False)
    contrastive_metrics.to_csv(OUT_DIR / "tail_safe_subject_contrastive_policy_metrics.csv", index=False)
    contrastive_summary.to_csv(OUT_DIR / "tail_safe_subject_contrastive_score_summary.csv", index=False)
    train_scored.to_csv(OUT_DIR / "tail_safe_train_action_modes.csv", index=False)
    test_scored.to_csv(OUT_DIR / "tail_safe_test_action_modes.csv", index=False)
    test_audit.to_csv(OUT_DIR / "tail_safe_test_release_audit.csv", index=False)
    candidate.to_csv(OUT_DIR / candidate_name, index=False)
    candidate.to_csv(ROOT / candidate_name, index=False)
    (OUT_DIR / "tail_safe_expected_utility_core_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    md = build_markdown(
        summary,
        utility_metrics,
        full_chosen,
        nested_subject_summary,
        nested_target_summary,
        stable,
        grid,
        contrastive_summary,
    )
    (OUT_DIR / "TAIL_SAFE_EXPECTED_UTILITY_CORE_KO.md").write_text(md, encoding="utf-8")
    PAPER_DOC.write_text(md, encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


if __name__ == "__main__":
    run()
