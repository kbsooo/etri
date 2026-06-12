#!/usr/bin/env python3
"""Core student recovery of the masked-view tail teacher.

The strongest positive HS-JEPA evidence so far is the masked-view consensus
tail teacher.  Two stricter variants failed:

    action-free vulnerability gate
    counterfactual direction-only action-health

This experiment asks a different question:

    Can a lightweight HS-JEPA core student recover the teacher's hidden
    action-tail representation without seeing action probabilities,
    action magnitudes, support scores, or public/LB anchors?

The student is allowed a minimal action listener (raw vs inverse and
up/down/no-op direction sign), but not the posterior values that make the
teacher action-aware.  It learns the teacher's masked-view consensus utility as
the hidden target representation, then uses the recovered score for a sparse
row-target action decoder.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, mean_absolute_error, roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hsjepa_core.run_action_support_world_model_core import TARGETS, target_context_columns, validate_submission  # noqa: E402
from hsjepa_core.run_episode_conditioned_relative_tail_core import (  # noqa: E402
    NULL_REPEATS as EPISODE_NULL_REPEATS,
    add_episode_conditioned_targets,
    add_episode_context,
    episode_feature_summary,
)
from hsjepa_core.run_lifelog_core_state_evidence import format_float, markdown_table  # noqa: E402
from hsjepa_core.run_masked_view_consensus_tail_core import (  # noqa: E402
    build_view_feature_sets,
    fit_masked_view_consensus,
    view_disagreement_summary,
)
from hsjepa_core.run_tail_safe_expected_utility_core import (  # noqa: E402
    add_subject_contrastive_scores,
    build_mode_tables,
    choose_mode_indices,
    classifier_factory,
    evaluate_policy,
    regressor_factory,
    utility_feature_columns,
)
from sleep_competition_adapter.target_route_conservation_decoder import (  # noqa: E402
    SAMPLE_SUBMISSION,
    build_listener_cells,
    short_hash,
)


OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "core_student_recovers_masked_tail_teacher"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "CORE_STUDENT_RECOVERS_MASKED_TAIL_TEACHER_KO.md"
RANDOM_SEED = 20260613
NULL_REPEATS = min(10, EPISODE_NULL_REPEATS)


def stable_seed(*parts: object) -> int:
    key = "::".join(map(str, parts)).encode("utf-8")
    return RANDOM_SEED + int(hashlib.sha256(key).hexdigest()[:8], 16) % 1009


def safe_auc(y: np.ndarray | pd.Series, score: np.ndarray | pd.Series) -> float | None:
    y_arr = np.asarray(y, dtype=int)
    score_arr = np.asarray(score, dtype=np.float64)
    mask = np.isfinite(score_arr)
    if mask.sum() == 0 or len(np.unique(y_arr[mask])) < 2:
        return None
    return float(roc_auc_score(y_arr[mask], score_arr[mask]))


def safe_ap(y: np.ndarray | pd.Series, score: np.ndarray | pd.Series) -> float | None:
    y_arr = np.asarray(y, dtype=int)
    score_arr = np.asarray(score, dtype=np.float64)
    mask = np.isfinite(score_arr)
    if mask.sum() == 0 or len(np.unique(y_arr[mask])) < 2:
        return None
    return float(average_precision_score(y_arr[mask], score_arr[mask]))


def add_minimal_action_listener(modes: pd.DataFrame) -> pd.DataFrame:
    out = modes.copy()
    direction = np.sign(out["action_delta"].astype(float).to_numpy())
    out["student_action_raw_listener"] = out["decoder_action"].eq("raw_memory_release").astype(float)
    out["student_action_inverse_listener"] = out["decoder_action"].eq("inverse_toxic_memory").astype(float)
    out["student_direction"] = direction
    out["student_direction_up"] = (direction > 0).astype(float)
    out["student_direction_down"] = (direction < 0).astype(float)
    out["student_direction_noop"] = (direction == 0).astype(float)
    for target in TARGETS:
        onehot = out[f"target_onehot_{target}"].astype(float) if f"target_onehot_{target}" in out else out["target"].eq(target).astype(float)
        out[f"student_direction_x_{target}"] = onehot * out["student_direction"]
    return out


def is_student_feature(col: str) -> bool:
    blocked = {
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
    }
    if col in blocked or col.startswith("support_score_") or col.startswith("mode_alignment__support_score_"):
        return False
    return (
        col in target_context_columns()
        or col.startswith("wm_resid_")
        or col.startswith("wm_energy")
        or col.startswith("target_interaction__")
        or col.startswith("family_interaction__")
        or col.startswith("episode_")
        or col.startswith("route_family__")
        or col.startswith("student_action_")
        or col.startswith("student_direction")
    )


def student_feature_columns(train_modes: pd.DataFrame, test_modes: pd.DataFrame) -> list[str]:
    cols: list[str] = []
    for col in train_modes.columns:
        if col not in test_modes.columns or not is_student_feature(col):
            continue
        if pd.api.types.is_numeric_dtype(train_modes[col]) and pd.api.types.is_numeric_dtype(test_modes[col]):
            cols.append(col)
    return list(dict.fromkeys(cols))


def build_student_view_sets(feature_cols: list[str]) -> dict[str, list[str]]:
    def is_world(col: str) -> bool:
        return col.startswith("wm_resid_") or col.startswith("wm_energy")

    def is_episode(col: str) -> bool:
        return col.startswith("episode_")

    def is_listener_interaction(col: str) -> bool:
        return col.startswith("target_interaction__") or col.startswith("family_interaction__")

    def is_action_listener(col: str) -> bool:
        return col.startswith("student_action_") or col.startswith("student_direction")

    views = {
        "student_full_context": feature_cols,
        "student_mask_world": [col for col in feature_cols if not (is_world(col) or is_listener_interaction(col))],
        "student_mask_episode": [col for col in feature_cols if not is_episode(col)],
        "student_mask_listener_interaction": [col for col in feature_cols if not is_listener_interaction(col)],
        "student_mask_action_listener": [col for col in feature_cols if not is_action_listener(col)],
    }
    return {name: list(dict.fromkeys(cols)) for name, cols in views.items() if len(cols) >= 8}


def add_teacher_labels(train_scored: pd.DataFrame) -> pd.DataFrame:
    out = train_scored.copy()
    out["teacher_tail_utility"] = out["masked_view_consensus_utility"].astype(float)
    out["teacher_pessimistic_utility"] = out["masked_view_consensus_pessimistic_utility"].astype(float)
    out["teacher_health_score"] = out["masked_view_consensus_health_score"].astype(float)
    by_target_threshold = (
        out.groupby("target", observed=True)["teacher_tail_utility"]
        .quantile(0.90)
        .rename("teacher_target_q90")
        .reset_index()
    )
    out = out.merge(by_target_threshold, on="target", how="left")
    out["teacher_top_tail_action"] = out["teacher_tail_utility"].ge(out["teacher_target_q90"]).astype(int)
    out["teacher_recovered_positive"] = out["effective_gain"].gt(0).astype(int)
    return out


def fit_one_student_view(
    train_modes: pd.DataFrame,
    test_modes: pd.DataFrame,
    feature_cols: list[str],
    view_name: str,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    subjects = sorted(train_modes["subject_id"].astype(str).unique())
    y_teacher = train_modes["teacher_tail_utility"].astype(float).to_numpy()
    y_pess = train_modes["teacher_pessimistic_utility"].astype(float).to_numpy()
    y_top = train_modes["teacher_top_tail_action"].astype(int).to_numpy()
    y_real_health = train_modes["teacher_recovered_positive"].astype(int).to_numpy()
    weights = 1.0 + np.minimum(np.abs(y_teacher), 8.0)

    oof_teacher = np.zeros(len(train_modes), dtype=np.float64)
    oof_pess = np.zeros(len(train_modes), dtype=np.float64)
    oof_top = np.zeros(len(train_modes), dtype=np.float64)
    oof_real_health = np.zeros(len(train_modes), dtype=np.float64)

    for subject in subjects:
        tr = train_modes.index[~train_modes["subject_id"].astype(str).eq(subject)].to_numpy()
        va = train_modes.index[train_modes["subject_id"].astype(str).eq(subject)].to_numpy()
        teacher_model = regressor_factory(stable_seed("student-teacher", view_name, subject))
        pess_model = regressor_factory(stable_seed("student-pess", view_name, subject))
        teacher_model.fit(train_modes.iloc[tr][feature_cols], y_teacher[tr], histgradientboostingregressor__sample_weight=weights[tr])
        pess_model.fit(train_modes.iloc[tr][feature_cols], y_pess[tr], histgradientboostingregressor__sample_weight=weights[tr])
        oof_teacher[va] = teacher_model.predict(train_modes.iloc[va][feature_cols])
        oof_pess[va] = pess_model.predict(train_modes.iloc[va][feature_cols])

        if len(np.unique(y_top[tr])) < 2:
            oof_top[va] = float(y_top[tr].mean())
        else:
            top_model = classifier_factory(stable_seed("student-top", view_name, subject))
            top_model.fit(train_modes.iloc[tr][feature_cols], y_top[tr], histgradientboostingclassifier__sample_weight=weights[tr])
            oof_top[va] = top_model.predict_proba(train_modes.iloc[va][feature_cols])[:, 1]

        if len(np.unique(y_real_health[tr])) < 2:
            oof_real_health[va] = float(y_real_health[tr].mean())
        else:
            real_model = classifier_factory(stable_seed("student-real-health", view_name, subject))
            real_model.fit(train_modes.iloc[tr][feature_cols], y_real_health[tr], histgradientboostingclassifier__sample_weight=weights[tr])
            oof_real_health[va] = real_model.predict_proba(train_modes.iloc[va][feature_cols])[:, 1]

    teacher_model = regressor_factory(stable_seed("student-teacher", view_name, "full-test"))
    pess_model = regressor_factory(stable_seed("student-pess", view_name, "full-test"))
    teacher_model.fit(train_modes[feature_cols], y_teacher, histgradientboostingregressor__sample_weight=weights)
    pess_model.fit(train_modes[feature_cols], y_pess, histgradientboostingregressor__sample_weight=weights)
    test_teacher = teacher_model.predict(test_modes[feature_cols])
    test_pess = pess_model.predict(test_modes[feature_cols])

    if len(np.unique(y_top)) < 2:
        test_top = np.full(len(test_modes), float(y_top.mean()), dtype=np.float64)
    else:
        top_model = classifier_factory(stable_seed("student-top", view_name, "full-test"))
        top_model.fit(train_modes[feature_cols], y_top, histgradientboostingclassifier__sample_weight=weights)
        test_top = top_model.predict_proba(test_modes[feature_cols])[:, 1]

    if len(np.unique(y_real_health)) < 2:
        test_real_health = np.full(len(test_modes), float(y_real_health.mean()), dtype=np.float64)
    else:
        real_model = classifier_factory(stable_seed("student-real-health", view_name, "full-test"))
        real_model.fit(train_modes[feature_cols], y_real_health, histgradientboostingclassifier__sample_weight=weights)
        test_real_health = real_model.predict_proba(test_modes[feature_cols])[:, 1]

    train_pred = pd.DataFrame(
        {
            f"student_{view_name}_teacher": oof_teacher,
            f"student_{view_name}_pess": oof_pess,
            f"student_{view_name}_top": oof_top,
            f"student_{view_name}_real_health": oof_real_health,
        },
        index=train_modes.index,
    )
    test_pred = pd.DataFrame(
        {
            f"student_{view_name}_teacher": test_teacher,
            f"student_{view_name}_pess": test_pess,
            f"student_{view_name}_top": test_top,
            f"student_{view_name}_real_health": test_real_health,
        },
        index=test_modes.index,
    )
    metrics = {
        "view": view_name,
        "feature_count": len(feature_cols),
        "teacher_mae": float(mean_absolute_error(y_teacher, oof_teacher)),
        "pessimistic_mae": float(mean_absolute_error(y_pess, oof_pess)),
        "teacher_top_auc": safe_auc(y_top, oof_top),
        "teacher_top_ap": safe_ap(y_top, oof_top),
        "realized_health_auc": safe_auc(y_real_health, oof_real_health),
        "realized_health_ap": safe_ap(y_real_health, oof_real_health),
    }
    return train_pred, test_pred, metrics


def fit_student_consensus(
    train_modes: pd.DataFrame,
    test_modes: pd.DataFrame,
    view_sets: dict[str, list[str]],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train_scored = train_modes.copy()
    test_scored = test_modes.copy()
    metric_rows: list[dict[str, Any]] = []
    for view_name, feature_cols in view_sets.items():
        train_pred, test_pred, metrics = fit_one_student_view(train_modes, test_modes, feature_cols, view_name)
        metric_rows.append(metrics)
        for col in train_pred.columns:
            train_scored[col] = train_pred[col].to_numpy(dtype=np.float64)
            test_scored[col] = test_pred[col].to_numpy(dtype=np.float64)

    teacher_cols = [f"student_{name}_teacher" for name in view_sets]
    pess_cols = [f"student_{name}_pess" for name in view_sets]
    top_cols = [f"student_{name}_top" for name in view_sets]
    health_cols = [f"student_{name}_real_health" for name in view_sets]

    for frame in [train_scored, test_scored]:
        frame["student_teacher_mean"] = frame[teacher_cols].mean(axis=1)
        frame["student_pessimistic_mean"] = frame[pess_cols].mean(axis=1)
        frame["student_teacher_top_mean"] = frame[top_cols].mean(axis=1)
        frame["student_real_health_mean"] = frame[health_cols].mean(axis=1)
        frame["student_teacher_std"] = frame[teacher_cols].std(axis=1, ddof=0)
        frame["student_pessimistic_std"] = frame[pess_cols].std(axis=1, ddof=0)
        frame["student_disagreement"] = frame["student_teacher_std"] + 0.55 * frame["student_pessimistic_std"]
        frame["student_recovered_tail_score"] = (
            frame["student_teacher_mean"]
            + 0.45 * frame["student_pessimistic_mean"]
            + 0.24 * frame["student_teacher_top_mean"]
            + 0.14 * frame["student_real_health_mean"]
            - 0.65 * frame["student_disagreement"]
        )
        frame["student_conservative_tail_score"] = (
            frame["student_pessimistic_mean"]
            + 0.20 * frame["student_teacher_top_mean"]
            - 0.90 * frame["student_disagreement"]
        )

    metric_rows.append(
        {
            "view": "student_consensus",
            "feature_count": sum(len(cols) for cols in view_sets.values()),
            "teacher_mae": float(mean_absolute_error(train_modes["teacher_tail_utility"], train_scored["student_teacher_mean"])),
            "pessimistic_mae": float(mean_absolute_error(train_modes["teacher_pessimistic_utility"], train_scored["student_pessimistic_mean"])),
            "teacher_top_auc": safe_auc(train_modes["teacher_top_tail_action"], train_scored["student_teacher_top_mean"]),
            "teacher_top_ap": safe_ap(train_modes["teacher_top_tail_action"], train_scored["student_teacher_top_mean"]),
            "realized_health_auc": safe_auc(train_modes["teacher_recovered_positive"], train_scored["student_real_health_mean"]),
            "realized_health_ap": safe_ap(train_modes["teacher_recovered_positive"], train_scored["student_real_health_mean"]),
        }
    )
    return train_scored, test_scored, pd.DataFrame(metric_rows)


def policy_grid(modes: pd.DataFrame, null_repeats: int) -> pd.DataFrame:
    score_cols = [
        "student_recovered_tail_score",
        "student_conservative_tail_score",
        "student_teacher_mean",
        "student_pessimistic_mean",
        "student_teacher_top_mean",
    ]
    fractions = [0.01, 0.02, 0.04, 0.06, 0.08, 0.10, 0.14, 0.18]
    rows: list[dict[str, Any]] = []
    for target in TARGETS:
        rows.append(evaluate_policy(modes, target, "student_recovered_tail_score", "hold", 0.0, 0))
        for score_col in score_cols:
            for policy in ["top_all", "top_decisive"]:
                for fraction in fractions:
                    rows.append(evaluate_policy(modes, target, score_col, policy, fraction, null_repeats))
    grid = pd.DataFrame(rows)
    grid["student_policy_score"] = (
        grid["selected_gain_sum"]
        + 0.58 * grid["gain_lift_vs_null"]
        + 0.12 * grid["gain_z_vs_null"].fillna(0.0)
        + 0.22 * grid["positive_subjects"]
        - 0.95 * grid["negative_subjects"]
        + 0.25 * grid["selected_positive_gain_rate"].fillna(0.0)
    )
    return grid


def choose_policies(grid: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for target, part in grid.groupby("target", observed=True):
        hold = part[part["policy"].eq("hold")].iloc[0].to_dict()
        viable = part[
            ~part["policy"].eq("hold")
            & (part["selected_gain_sum"] > 0.0)
            & (part["gain_lift_vs_null"] > 0.0)
            & (part["selected_positive_gain_rate"].fillna(0.0) >= 0.54)
            & (part["negative_subjects"] <= 3)
        ].copy()
        if viable.empty:
            hold["accepted"] = False
            hold["accept_reason"] = "no_core_student_recovery_policy_passed"
            rows.append(hold)
            continue
        row = viable.sort_values(["student_policy_score", "selected_gain_sum"], ascending=False).iloc[0].to_dict()
        row["accepted"] = True
        row["accept_reason"] = "positive_core_student_teacher_recovery"
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
    subject_rows: list[dict[str, Any]] = []
    route_rows: list[dict[str, Any]] = []
    audits: list[pd.DataFrame] = []
    for subject in subjects:
        selector = modes[~modes["subject_id"].astype(str).eq(subject)].copy()
        heldout = modes[modes["subject_id"].astype(str).eq(subject)].copy()
        chosen = choose_policies(policy_grid(selector, null_repeats=8))
        audit = apply_policies(heldout, chosen)
        audit["heldout_subject"] = subject
        audits.append(audit)
        selected = audit[audit["released"]].copy()
        gains = selected["effective_gain"].to_numpy(dtype=np.float64) if len(selected) else np.array([], dtype=np.float64)
        subject_rows.append(
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
    return pd.DataFrame(subject_rows), pd.DataFrame(route_rows), pd.concat(audits, ignore_index=True)


def summarize_nested_targets(nested_audit: pd.DataFrame) -> pd.DataFrame:
    selected = nested_audit[nested_audit["released"]].copy()
    if selected.empty:
        return pd.DataFrame(columns=["target", "selected_cells", "gain_sum", "positive_gain_rate"])
    subject_gain = selected.groupby(["heldout_subject", "target"], observed=True)["effective_gain"].sum().reset_index()
    subject_summary = (
        subject_gain.groupby("target", observed=True)
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
            and positive_subjects >= negative_subjects
            and positive_rate >= 0.52
        )
        row["accepted"] = stable
        row["heldout_accept_rate"] = float(accept_rate.get(target, 0.0))
        row["heldout_gain_sum"] = gain_sum
        row["heldout_positive_subjects"] = positive_subjects
        row["heldout_negative_subjects"] = negative_subjects
        row["heldout_positive_gain_rate"] = positive_rate
        row["accept_reason"] = "core_student_subjectheldout_stable" if stable else "failed_core_student_subjectheldout"
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


def student_disagreement_summary(scored: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for target, part in scored.groupby("target", observed=True):
        rows.append(
            {
                "target": target,
                "mean_student_disagreement": float(part["student_disagreement"].mean()),
                "median_student_disagreement": float(part["student_disagreement"].median()),
                "teacher_score_mean": float(part["teacher_tail_utility"].mean()),
                "student_score_mean": float(part["student_recovered_tail_score"].mean()),
                "realized_gain_mean": float(part["effective_gain"].mean()),
            }
        )
    return pd.DataFrame(rows).sort_values("target")


def build_markdown(
    summary: dict[str, Any],
    teacher_view_metrics: pd.DataFrame,
    student_metrics: pd.DataFrame,
    student_disagreement: pd.DataFrame,
    teacher_disagreement: pd.DataFrame,
    episode_features: pd.DataFrame,
    full_chosen: pd.DataFrame,
    nested_subject_summary: pd.DataFrame,
    nested_target_summary: pd.DataFrame,
    stable: pd.DataFrame,
    policy_board: pd.DataFrame,
) -> str:
    top_policy = policy_board.sort_values(["student_policy_score", "selected_gain_sum"], ascending=False, na_position="last")
    return f"""# Core Student Recovers Masked Tail Teacher

## 한 줄 요약

masked-view consensus tail teacher는 현재 가장 강한 HS-JEPA core-boundary evidence다.
이번 실험은 그 teacher의 hidden action-tail representation을, action probability/magnitude/support score 없이
core student가 복원할 수 있는지 검사한다.

```text
visible human-state context + minimal action listener
  -> recover masked-view teacher hidden tail representation
  -> sparse row-target action assignment
```

## 빠른 판정: 이것은 HS-JEPA인가?

맞다. 정확히는 **HS-JEPA core student가 teacher의 hidden target representation을 예측하는지 보는
distillation-style core-boundary 실험**이다.

JEPA성은 다음 질문에서 나온다.

```text
보이는 human-state context만으로
보이지 않는 masked-view action-tail teacher representation을 복원할 수 있는가?
```

다만 이 실험은 teacher를 target representation으로 사용하므로, 독립적인 core proof가 아니라
`frontier hidden representation recoverability` sensor로 읽어야 한다.

## 사용하지 않은 정보

- public LB ledger: `{summary["uses_public_score_ledger"]}`
- prior submission probability: `{summary["uses_prior_submission_probabilities"]}`
- proprietary embedding API: `{summary["uses_proprietary_embedding_api"]}`
- action probability as student feature: `{summary["uses_action_probability_as_student_feature"]}`
- action magnitude as student feature: `{summary["uses_action_magnitude_as_student_feature"]}`
- support score as student feature: `{summary["uses_support_score_as_student_feature"]}`

## Verdict

- verdict: `{summary["verdict"]}`
- full OOF selected gain: `{format_float(summary["full_oof_gain_sum"], 6)}`
- nested heldout gain: `{format_float(summary["nested_heldout_gain_sum"], 6)}`
- stable targets: `{summary["stable_targets"]}`
- stable OOF gain: `{format_float(summary["stable_oof_gain_sum"], 6)}`
- candidate policy source: `{summary["candidate_policy_source"]}`
- released test cells: `{summary["released_test_cells"]}`

## Teacher Masked-View Metrics

{markdown_table(teacher_view_metrics, ["view", "feature_count", "gain_mae", "tail_mae", "positive_auc", "positive_ap", "toxic_auc", "toxic_ap"], max_rows=16)}

## Student Recovery Metrics

{markdown_table(student_metrics, ["view", "feature_count", "teacher_mae", "pessimistic_mae", "teacher_top_auc", "teacher_top_ap", "realized_health_auc", "realized_health_ap"], max_rows=16)}

## Student Disagreement By Target

{markdown_table(student_disagreement, ["target", "mean_student_disagreement", "median_student_disagreement", "teacher_score_mean", "student_score_mean", "realized_gain_mean"], max_rows=16)}

## Teacher Disagreement By Target

{markdown_table(teacher_disagreement, ["target", "mean_disagreement", "median_disagreement", "mean_abs_gain", "toxic_tail_rate"], max_rows=16)}

## Episode Feature Summary

{markdown_table(episode_features, ["feature", "train_mean", "train_std", "test_mean", "test_std"], max_rows=20)}

## Full OOF Chosen Policies

{markdown_table(full_chosen, ["target", "accepted", "score_col", "policy", "fraction", "selected_cells", "selected_gain_sum", "selected_positive_gain_rate", "positive_subjects", "negative_subjects", "gain_lift_vs_null", "student_policy_score", "accept_reason"], max_rows=20)}

## Nested Subject-Heldout Summary

{markdown_table(nested_subject_summary, ["heldout_subject", "selected_cells", "gain_sum", "mean_gain", "positive_gain_rate", "accepted_targets"], max_rows=20)}

## Nested Target Summary

{markdown_table(nested_target_summary, ["target", "selected_cells", "gain_sum", "mean_gain", "positive_gain_rate", "raw_action_count", "inverse_action_count", "positive_subjects", "negative_subjects"], max_rows=20)}

## Stable Policies Used For Candidate

{markdown_table(stable, ["target", "accepted", "score_col", "policy", "fraction", "heldout_accept_rate", "heldout_gain_sum", "heldout_positive_subjects", "heldout_negative_subjects", "heldout_positive_gain_rate", "accept_reason"], max_rows=20)}

## Policy Board Top Rows

{markdown_table(top_policy, ["target", "score_col", "policy", "fraction", "selected_cells", "selected_gain_sum", "selected_positive_gain_rate", "positive_subjects", "negative_subjects", "gain_lift_vs_null", "gain_z_vs_null", "student_policy_score"], max_rows=32)}

## Anchor-Free Candidate

- candidate: `{summary["candidate_file"]}`
- validation: `{summary["validation"]}`

## 해석

좋은 결과:

```text
core student가 teacher의 hidden action-tail representation을 subject-heldout에서도
release-safe하게 복원하면, HS-JEPA core가 frontier hidden structure를 일부 재발견했다는 증거다.
```

나쁜 결과:

```text
teacher representation 자체는 강하지만 student가 subject-heldout에서 무너지면,
현재 frontier는 core-only representation이 아니라 action-aware masked-view teacher boundary에 의존한다.
```
"""


def run() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    train_cells, test_cells, train_priors, _view_metrics = build_listener_cells()
    train_cells, test_cells, _contrastive_metrics, _contrastive_summary = add_subject_contrastive_scores(train_cells, test_cells)
    train_modes, test_modes = build_mode_tables(train_cells, test_cells)
    train_modes, test_modes, episode_cols = add_episode_context(train_modes, test_modes)
    train_modes = add_episode_conditioned_targets(train_modes)
    train_modes = add_minimal_action_listener(train_modes)
    test_modes = add_minimal_action_listener(test_modes)

    teacher_feature_cols = utility_feature_columns(train_modes, test_modes) + [
        col for col in episode_cols if col in train_modes.columns and col in test_modes.columns
    ]
    teacher_feature_cols = list(dict.fromkeys(teacher_feature_cols))
    teacher_view_sets = build_view_feature_sets(teacher_feature_cols)
    teacher_train, teacher_test, teacher_view_metrics = fit_masked_view_consensus(train_modes, test_modes, teacher_view_sets)
    teacher_train = add_teacher_labels(teacher_train)
    teacher_test["teacher_tail_utility"] = teacher_test["masked_view_consensus_utility"].astype(float)
    teacher_test["teacher_pessimistic_utility"] = teacher_test["masked_view_consensus_pessimistic_utility"].astype(float)
    teacher_test["teacher_health_score"] = teacher_test["masked_view_consensus_health_score"].astype(float)

    feature_cols = student_feature_columns(teacher_train, teacher_test) + [
        col for col in episode_cols if col in teacher_train.columns and col in teacher_test.columns
    ]
    feature_cols = list(dict.fromkeys(feature_cols))
    student_view_sets = build_student_view_sets(feature_cols)
    student_train, student_test, student_metrics = fit_student_consensus(teacher_train, teacher_test, student_view_sets)

    grid = policy_grid(student_train, null_repeats=NULL_REPEATS)
    full_chosen = choose_policies(grid)
    full_audit = apply_policies(student_train, full_chosen)
    nested_subject_summary, nested_route_rows, nested_audit = nested_subject_stress(student_train)
    nested_target_summary = summarize_nested_targets(nested_audit)
    stable = stable_policies(full_chosen, nested_route_rows, nested_target_summary)

    stable_count = int(stable["accepted"].sum()) if "accepted" in stable else 0
    candidate_policy = stable if stable_count > 0 else full_chosen
    candidate_policy_source = "stable_subjectheldout" if stable_count > 0 else "full_oof_sensor"

    sample = pd.read_csv(SAMPLE_SUBMISSION)
    candidate, test_audit = apply_policies_to_test(sample, student_test, candidate_policy, train_priors)
    validation = validate_submission(candidate, sample)
    if not validation["valid"]:
        raise ValueError(f"candidate is not upload-safe: {validation['problems']}")
    candidate_name = f"submission_hsjepa_core_student_recovers_masked_tail_teacher_anchor_free_{short_hash(candidate)}_uploadsafe.csv"

    selected_full = full_audit[full_audit["released"]].copy()
    stable_oof_audit = apply_policies(student_train, stable)
    stable_selected = stable_oof_audit[stable_oof_audit["released"]].copy()
    nested_selected = nested_audit[nested_audit["released"]].copy()
    full_oof_gain = float(selected_full["effective_gain"].sum()) if len(selected_full) else 0.0
    nested_gain = float(nested_selected["effective_gain"].sum()) if len(nested_selected) else 0.0
    stable_oof_gain = float(stable_selected["effective_gain"].sum()) if len(stable_selected) else 0.0
    stable_targets = stable.loc[stable["accepted"].eq(True), "target"].astype(str).tolist() if "accepted" in stable else []
    verdict = (
        "core_student_teacher_recovery_subjectheldout_positive"
        if nested_gain > 0 and stable_count > 0
        else "core_student_teacher_recovery_oof_positive_subjectheldout_fragile"
        if full_oof_gain > 0
        else "core_student_teacher_recovery_negative"
    )

    summary = {
        "package": "core_student_recovers_masked_tail_teacher",
        "status": "core_student_recovers_masked_tail_teacher_ready",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "uses_action_probability_as_student_feature": False,
        "uses_action_magnitude_as_student_feature": False,
        "uses_support_score_as_student_feature": False,
        "teacher": "masked_view_consensus_tail_core",
        "student_view_names": list(student_view_sets.keys()),
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

    candidate.to_csv(OUT_DIR / candidate_name, index=False)
    candidate.to_csv(ROOT / candidate_name, index=False)
    teacher_view_metrics.to_csv(OUT_DIR / "core_student_teacher_view_metrics.csv", index=False)
    student_metrics.to_csv(OUT_DIR / "core_student_recovery_metrics.csv", index=False)
    student_disagreement_summary(student_train).to_csv(OUT_DIR / "core_student_disagreement_by_target.csv", index=False)
    view_disagreement_summary(teacher_train).to_csv(OUT_DIR / "core_student_teacher_disagreement_by_target.csv", index=False)
    episode_feature_summary(train_modes, test_modes, episode_cols).to_csv(OUT_DIR / "core_student_episode_feature_summary.csv", index=False)
    grid.to_csv(OUT_DIR / "core_student_policy_grid.csv", index=False)
    full_chosen.to_csv(OUT_DIR / "core_student_full_chosen_policies.csv", index=False)
    nested_subject_summary.to_csv(OUT_DIR / "core_student_nested_subject_summary.csv", index=False)
    nested_route_rows.to_csv(OUT_DIR / "core_student_nested_route_rows.csv", index=False)
    nested_target_summary.to_csv(OUT_DIR / "core_student_nested_target_summary.csv", index=False)
    stable.to_csv(OUT_DIR / "core_student_stable_policies.csv", index=False)
    full_audit.to_csv(OUT_DIR / "core_student_full_oof_action_audit.csv", index=False)
    test_audit.to_csv(OUT_DIR / "core_student_test_release_audit.csv", index=False)
    (OUT_DIR / "core_student_recovers_masked_tail_teacher_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    doc = build_markdown(
        summary,
        teacher_view_metrics,
        student_metrics,
        student_disagreement_summary(student_train),
        view_disagreement_summary(teacher_train),
        episode_feature_summary(train_modes, test_modes, episode_cols),
        full_chosen,
        nested_subject_summary,
        nested_target_summary,
        stable,
        grid,
    )
    (OUT_DIR / "CORE_STUDENT_RECOVERS_MASKED_TAIL_TEACHER_KO.md").write_text(doc, encoding="utf-8")
    PAPER_DOC.write_text(doc, encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
