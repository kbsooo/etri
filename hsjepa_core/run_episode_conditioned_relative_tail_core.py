#!/usr/bin/env python3
"""Episode-conditioned relative-tail core for HS-JEPA.

Subject-normalized tail fields reduced the subject-heldout damage, but still
left a negative nested gain.  This experiment asks a sharper JEPA-style question:

    Is "bad for this subject" still too coarse?
    Do we need "bad for this subject in this episode state"?

The script constructs an unsupervised row episode score from HS-JEPA residual
energy, action pressure, and subject-local sequence position.  It then changes
the hidden target representation from subject-normalized gain to
episode-conditioned relative gain:

    gain relative to subject + target + action + episode-bin tail scale

No public LB ledger, prior submission probabilities, or proprietary embedding
APIs are used.
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

from hsjepa_core.run_action_support_world_model_core import TARGETS, validate_submission  # noqa: E402
from hsjepa_core.run_lifelog_core_state_evidence import format_float, markdown_table  # noqa: E402
from hsjepa_core.run_tail_safe_expected_utility_core import (  # noqa: E402
    NULL_REPEATS as TAIL_SAFE_NULL_REPEATS,
    add_subject_contrastive_scores,
    build_mode_tables,
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


OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "episode_conditioned_relative_tail_core"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "EPISODE_CONDITIONED_RELATIVE_TAIL_CORE_KO.md"
RANDOM_SEED = 20260613
NULL_REPEATS = min(12, TAIL_SAFE_NULL_REPEATS)
TAIL_Z_THRESHOLD = -1.0


def stable_seed(*parts: object) -> int:
    key = "::".join(map(str, parts)).encode("utf-8")
    return RANDOM_SEED + int(hashlib.sha256(key).hexdigest()[:8], 16) % 1009


def rank01(values: pd.Series | np.ndarray) -> np.ndarray:
    series = pd.Series(values, dtype="float64").replace([np.inf, -np.inf], np.nan)
    if series.notna().sum() <= 1 or series.nunique(dropna=True) <= 1:
        return np.full(len(series), 0.5, dtype=np.float64)
    return series.rank(method="average", pct=True).fillna(0.5).to_numpy(dtype=np.float64)


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


def add_episode_context(train_modes: pd.DataFrame, test_modes: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    """Attach unsupervised episode/sequence context to train and test mode rows."""

    def build_row_context(modes: pd.DataFrame) -> pd.DataFrame:
        rows = modes.drop_duplicates("row").copy()
        energy_cols = [col for col in rows.columns if col.startswith("wm_energy")]
        resid_cols = [col for col in rows.columns if col.startswith("wm_resid_")]
        support_cols = [col for col in rows.columns if col.startswith("support_score_")]
        rows["episode_energy_mean"] = rows[energy_cols].mean(axis=1) if energy_cols else 0.0
        rows["episode_energy_max"] = rows[energy_cols].max(axis=1) if energy_cols else 0.0
        rows["episode_resid_abs_mean"] = rows[resid_cols].abs().mean(axis=1) if resid_cols else 0.0
        rows["episode_support_mean"] = rows[support_cols].mean(axis=1) if support_cols else 0.5
        rows["episode_action_pressure_mean"] = modes.groupby("row", observed=True)["abs_action_move"].mean().reindex(rows["row"]).to_numpy()
        rows["episode_action_pressure_max"] = modes.groupby("row", observed=True)["abs_action_move"].max().reindex(rows["row"]).to_numpy()
        rows["sleep_date_ts"] = pd.to_datetime(rows["sleep_date"], errors="coerce")
        rows = rows.sort_values(["subject_id", "sleep_date_ts", "row"], kind="mergesort")
        rows["episode_subject_row_index"] = rows.groupby("subject_id", observed=True).cumcount()
        rows["episode_subject_row_count"] = rows.groupby("subject_id", observed=True)["row"].transform("size").clip(lower=1)
        rows["episode_subject_row_pct"] = rows["episode_subject_row_index"] / (rows["episode_subject_row_count"] - 1).clip(lower=1)
        rows["episode_weekday"] = rows["sleep_date_ts"].dt.dayofweek.fillna(0).astype(int)
        rows["episode_weekend"] = rows["episode_weekday"].isin([5, 6]).astype(float)
        rows["episode_month_end"] = rows["sleep_date_ts"].dt.is_month_end.fillna(False).astype(float)

        for col in [
            "episode_energy_mean",
            "episode_energy_max",
            "episode_resid_abs_mean",
            "episode_support_mean",
            "episode_action_pressure_mean",
            "episode_action_pressure_max",
        ]:
            group = rows.groupby("subject_id", observed=True)[col]
            center = group.transform("median")
            scale = group.transform(lambda x: max(float(np.std(x, ddof=0)), 1e-6))
            rows[f"{col}_subject_z"] = ((rows[col] - center) / scale).clip(-6, 6)
            rows[f"{col}_subject_rank"] = group.transform(lambda x: pd.Series(rank01(x), index=x.index)).astype(float)
            rows[f"{col}_delta_prev"] = group.transform(lambda x: x - x.shift(1)).fillna(0.0)
            rows[f"{col}_delta_next"] = group.transform(lambda x: x.shift(-1) - x).fillna(0.0)

        z_cols = [
            "episode_energy_mean_subject_z",
            "episode_energy_max_subject_z",
            "episode_resid_abs_mean_subject_z",
            "episode_action_pressure_mean_subject_z",
            "episode_action_pressure_max_subject_z",
        ]
        rows["episode_reset_pressure"] = rows[z_cols].clip(lower=0.0).mean(axis=1)
        rows["episode_quiet_pressure"] = (-rows[z_cols]).clip(lower=0.0).mean(axis=1)
        rows["episode_transition_pressure"] = rows[[col for col in rows.columns if col.endswith("_delta_prev") or col.endswith("_delta_next")]].abs().mean(axis=1)
        rows["episode_context_score"] = (
            0.45 * rank01(rows["episode_reset_pressure"])
            + 0.25 * rank01(rows["episode_transition_pressure"])
            + 0.20 * rank01(rows["episode_action_pressure_max"])
            + 0.10 * rows["episode_weekend"].astype(float)
        )
        rows["episode_bin"] = pd.cut(
            rows["episode_context_score"].rank(method="average", pct=True),
            bins=[-0.001, 0.34, 0.67, 1.001],
            labels=["episode_low", "episode_mid", "episode_high"],
        ).astype(str)
        keep = ["row", "episode_bin"] + [
            col
            for col in rows.columns
            if col.startswith("episode_") and col not in {"episode_bin", "episode_subject_row_count"}
        ]
        return rows[keep].copy()

    train_context = build_row_context(train_modes)
    test_context = build_row_context(test_modes)
    train = train_modes.merge(train_context, on="row", how="left")
    test = test_modes.merge(test_context, on="row", how="left")
    for frame in [train, test]:
        for label in ["episode_low", "episode_mid", "episode_high"]:
            frame[f"episode_bin__{label}"] = frame["episode_bin"].eq(label).astype(float)
    episode_cols = [
        col
        for col in train.columns
        if col.startswith("episode_") and col in test.columns and col != "episode_bin"
    ]
    return train, test, episode_cols


def add_episode_conditioned_targets(train_modes: pd.DataFrame) -> pd.DataFrame:
    out = train_modes.copy()
    base_group = ["subject_id", "target", "decoder_action"]
    episode_group = ["subject_id", "target", "decoder_action", "episode_bin"]

    base_center = out.groupby(base_group, observed=True)["effective_gain"].transform("median")
    base_q25 = out.groupby(base_group, observed=True)["effective_gain"].transform(lambda x: float(np.quantile(x, 0.25)))
    base_q75 = out.groupby(base_group, observed=True)["effective_gain"].transform(lambda x: float(np.quantile(x, 0.75)))
    base_scale = ((base_q75 - base_q25) / 1.349).clip(lower=0.02)

    episode_count = out.groupby(episode_group, observed=True)["effective_gain"].transform("size")
    episode_center = out.groupby(episode_group, observed=True)["effective_gain"].transform("median")
    episode_q25 = out.groupby(episode_group, observed=True)["effective_gain"].transform(lambda x: float(np.quantile(x, 0.25)))
    episode_q75 = out.groupby(episode_group, observed=True)["effective_gain"].transform(lambda x: float(np.quantile(x, 0.75)))
    episode_scale = ((episode_q75 - episode_q25) / 1.349).clip(lower=0.02)

    use_episode = episode_count.ge(4)
    out["episode_tail_center"] = episode_center.where(use_episode, base_center).astype(float)
    out["episode_tail_scale"] = episode_scale.where(use_episode, base_scale).astype(float)
    out["episode_tail_group_count"] = episode_count.astype(float)
    out["episode_conditioned_gain"] = (out["effective_gain"].astype(float) - out["episode_tail_center"]) / out[
        "episode_tail_scale"
    ]
    out["episode_relative_tail_loss"] = np.maximum(-out["episode_conditioned_gain"], 0.0)
    out["episode_relative_toxic_tail"] = out["episode_conditioned_gain"].lt(TAIL_Z_THRESHOLD).astype(int)
    out["episode_relative_positive"] = out["episode_conditioned_gain"].gt(0.0).astype(int)
    return out


def fit_episode_conditioned_models(
    train_modes: pd.DataFrame,
    test_modes: pd.DataFrame,
    feature_cols: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    subjects = sorted(train_modes["subject_id"].astype(str).unique())
    y_gain = train_modes["episode_conditioned_gain"].astype(float).to_numpy()
    y_tail = train_modes["episode_relative_tail_loss"].astype(float).to_numpy()
    y_pos = train_modes["episode_relative_positive"].astype(int).to_numpy()
    y_toxic = train_modes["episode_relative_toxic_tail"].astype(int).to_numpy()
    weights = 1.0 + np.minimum(np.abs(y_gain), 6.0)

    oof_gain = np.zeros(len(train_modes), dtype=np.float64)
    oof_tail = np.zeros(len(train_modes), dtype=np.float64)
    oof_pos = np.zeros(len(train_modes), dtype=np.float64)
    oof_toxic = np.zeros(len(train_modes), dtype=np.float64)

    for subject in subjects:
        tr = train_modes.index[~train_modes["subject_id"].astype(str).eq(subject)].to_numpy()
        va = train_modes.index[train_modes["subject_id"].astype(str).eq(subject)].to_numpy()
        gain_model = regressor_factory(stable_seed("episode-conditioned-gain", subject))
        tail_model = regressor_factory(stable_seed("episode-conditioned-tail", subject))
        gain_model.fit(train_modes.iloc[tr][feature_cols], y_gain[tr], histgradientboostingregressor__sample_weight=weights[tr])
        tail_model.fit(train_modes.iloc[tr][feature_cols], y_tail[tr], histgradientboostingregressor__sample_weight=weights[tr])
        oof_gain[va] = gain_model.predict(train_modes.iloc[va][feature_cols])
        oof_tail[va] = np.maximum(tail_model.predict(train_modes.iloc[va][feature_cols]), 0.0)

        if len(np.unique(y_pos[tr])) < 2:
            oof_pos[va] = float(y_pos[tr].mean())
        else:
            pos_model = classifier_factory(stable_seed("episode-conditioned-positive", subject))
            pos_model.fit(train_modes.iloc[tr][feature_cols], y_pos[tr], histgradientboostingclassifier__sample_weight=weights[tr])
            oof_pos[va] = pos_model.predict_proba(train_modes.iloc[va][feature_cols])[:, 1]

        if len(np.unique(y_toxic[tr])) < 2:
            oof_toxic[va] = float(y_toxic[tr].mean())
        else:
            toxic_model = classifier_factory(stable_seed("episode-conditioned-toxic", subject))
            toxic_model.fit(train_modes.iloc[tr][feature_cols], y_toxic[tr], histgradientboostingclassifier__sample_weight=weights[tr])
            oof_toxic[va] = toxic_model.predict_proba(train_modes.iloc[va][feature_cols])[:, 1]

    gain_model = regressor_factory(stable_seed("episode-conditioned-gain", "full-test"))
    tail_model = regressor_factory(stable_seed("episode-conditioned-tail", "full-test"))
    gain_model.fit(train_modes[feature_cols], y_gain, histgradientboostingregressor__sample_weight=weights)
    tail_model.fit(train_modes[feature_cols], y_tail, histgradientboostingregressor__sample_weight=weights)
    test_gain = gain_model.predict(test_modes[feature_cols])
    test_tail = np.maximum(tail_model.predict(test_modes[feature_cols]), 0.0)

    if len(np.unique(y_pos)) < 2:
        test_pos = np.full(len(test_modes), float(y_pos.mean()), dtype=np.float64)
    else:
        pos_model = classifier_factory(stable_seed("episode-conditioned-positive", "full-test"))
        pos_model.fit(train_modes[feature_cols], y_pos, histgradientboostingclassifier__sample_weight=weights)
        test_pos = pos_model.predict_proba(test_modes[feature_cols])[:, 1]

    if len(np.unique(y_toxic)) < 2:
        test_toxic = np.full(len(test_modes), float(y_toxic.mean()), dtype=np.float64)
    else:
        toxic_model = classifier_factory(stable_seed("episode-conditioned-toxic", "full-test"))
        toxic_model.fit(train_modes[feature_cols], y_toxic, histgradientboostingclassifier__sample_weight=weights)
        test_toxic = toxic_model.predict_proba(test_modes[feature_cols])[:, 1]

    train_scored = train_modes.copy()
    test_scored = test_modes.copy()
    for frame, pred_gain, pred_tail, pred_pos, pred_toxic in [
        (train_scored, oof_gain, oof_tail, oof_pos, oof_toxic),
        (test_scored, test_gain, test_tail, test_pos, test_toxic),
    ]:
        frame["predicted_episode_conditioned_gain"] = pred_gain
        frame["predicted_episode_relative_tail_loss"] = pred_tail
        frame["predicted_episode_positive_prob"] = pred_pos
        frame["predicted_episode_toxic_prob"] = pred_toxic
        frame["episode_conditioned_utility"] = pred_gain - 0.95 * pred_tail - 0.30 * pred_toxic
        frame["episode_conditioned_pessimistic_utility"] = pred_gain - 1.65 * pred_tail - 0.55 * pred_toxic
        frame["episode_relative_health_score"] = pred_pos - pred_toxic

    metric_rows = [
        {"metric": "episode_conditioned_gain_mae", "value": float(mean_absolute_error(y_gain, oof_gain))},
        {"metric": "episode_tail_loss_mae", "value": float(mean_absolute_error(y_tail, oof_tail))},
        {"metric": "episode_positive_auc", "value": safe_auc(y_pos, oof_pos)},
        {"metric": "episode_positive_ap", "value": safe_ap(y_pos, oof_pos)},
        {"metric": "episode_toxic_tail_auc", "value": safe_auc(y_toxic, oof_toxic)},
        {"metric": "episode_toxic_tail_ap", "value": safe_ap(y_toxic, oof_toxic)},
        {"metric": "episode_toxic_tail_rate", "value": float(y_toxic.mean())},
        {"metric": "absolute_gain_sum_all_modes", "value": float(train_modes["effective_gain"].sum())},
    ]
    return train_scored, test_scored, pd.DataFrame(metric_rows)


def policy_grid(modes: pd.DataFrame, null_repeats: int) -> pd.DataFrame:
    score_cols = [
        "predicted_episode_conditioned_gain",
        "episode_conditioned_utility",
        "episode_conditioned_pessimistic_utility",
        "episode_relative_health_score",
    ]
    rows: list[dict[str, Any]] = []
    fractions = [0.02, 0.04, 0.06, 0.08, 0.10, 0.14, 0.18, 0.25]
    for target in TARGETS:
        rows.append(evaluate_policy(modes, target, "predicted_episode_conditioned_gain", "hold", 0.0, 0))
        for score_col in score_cols:
            for policy in ["top_all", "top_decisive"]:
                for fraction in fractions:
                    rows.append(evaluate_policy(modes, target, score_col, policy, fraction, null_repeats))
    grid = pd.DataFrame(rows)
    grid["episode_conditioned_policy_score"] = (
        grid["selected_gain_sum"]
        + 0.55 * grid["gain_lift_vs_null"]
        + 0.12 * grid["gain_z_vs_null"].fillna(0.0)
        + 0.20 * grid["positive_subjects"]
        - 0.85 * grid["negative_subjects"]
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
            & (part["negative_subjects"] <= 4)
        ].copy()
        if viable.empty:
            hold["accepted"] = False
            hold["accept_reason"] = "no_episode_conditioned_policy_passed"
            rows.append(hold)
            continue
        row = viable.sort_values(["episode_conditioned_policy_score", "selected_gain_sum"], ascending=False).iloc[0].to_dict()
        row["accepted"] = True
        row["accept_reason"] = "positive_episode_conditioned_tail_policy"
        rows.append(row)
    return pd.DataFrame(rows).sort_values("target")


def apply_policies(modes: pd.DataFrame, chosen: pd.DataFrame) -> pd.DataFrame:
    from hsjepa_core.run_tail_safe_expected_utility_core import choose_mode_indices

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
        row["accept_reason"] = "episode_conditioned_tail_subjectheldout_stable" if stable else "failed_episode_conditioned_tail_stress"
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
    from hsjepa_core.run_tail_safe_expected_utility_core import choose_mode_indices

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
    metrics: pd.DataFrame,
    full_chosen: pd.DataFrame,
    nested_subject_summary: pd.DataFrame,
    nested_target_summary: pd.DataFrame,
    stable: pd.DataFrame,
    policy_board: pd.DataFrame,
    episode_feature_summary: pd.DataFrame,
) -> str:
    top_policy = policy_board.sort_values(["episode_conditioned_policy_score", "selected_gain_sum"], ascending=False, na_position="last")
    return f"""# Episode-Conditioned Relative Tail Core

## 한 줄 요약

subject-relative badness도 아직 거칠다고 보고, row episode state별 tail scale로 다시 정규화했다.

```text
HS-JEPA residual/energy + sequence episode context
  -> episode-conditioned relative badness
  -> row-target action assignment
```

## 빠른 판정: 이것은 HS-JEPA인가?

부분적으로 맞다. 정확히는 **HS-JEPA core target representation을 episode-conditioned tail field로 재정의하는 core-decoder boundary 실험**이다.

JEPA성은 다음 질문에서 나온다.

```text
보이는 생활 context와 row sequence context만으로
보이지 않는 episode-specific action-tail representation을 예측할 수 있는가?
```

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

## Episode Feature Summary

{markdown_table(episode_feature_summary, ["feature", "train_mean", "train_std", "test_mean", "test_std"], max_rows=24)}

## Episode Tail Model Metrics

{markdown_table(metrics, ["metric", "value"], max_rows=20)}

## Full OOF Chosen Policies

{markdown_table(full_chosen, ["target", "accepted", "score_col", "policy", "fraction", "selected_cells", "selected_gain_sum", "selected_positive_gain_rate", "positive_subjects", "negative_subjects", "gain_lift_vs_null", "episode_conditioned_policy_score", "accept_reason"], max_rows=20)}

## Nested Subject-Heldout Summary

{markdown_table(nested_subject_summary, ["heldout_subject", "selected_cells", "gain_sum", "mean_gain", "positive_gain_rate", "accepted_targets"], max_rows=20)}

## Nested Target Summary

{markdown_table(nested_target_summary, ["target", "selected_cells", "gain_sum", "mean_gain", "positive_gain_rate", "raw_action_count", "inverse_action_count", "positive_subjects", "negative_subjects"], max_rows=20)}

## Stable Policies Used For Candidate

{markdown_table(stable, ["target", "accepted", "score_col", "policy", "fraction", "heldout_accept_rate", "heldout_gain_sum", "heldout_positive_subjects", "heldout_negative_subjects", "heldout_positive_gain_rate", "accept_reason"], max_rows=20)}

## Policy Board Top Rows

{markdown_table(top_policy, ["target", "score_col", "policy", "fraction", "selected_cells", "selected_gain_sum", "selected_positive_gain_rate", "positive_subjects", "negative_subjects", "gain_lift_vs_null", "gain_z_vs_null", "episode_conditioned_policy_score"], max_rows=32)}

## Anchor-Free Candidate

- candidate: `{summary["candidate_file"]}`
- validation: `{summary["validation"]}`

## 해석

좋은 결과:

```text
episode-conditioned tail field가 subject-normalized tail field보다 nested damage를 줄이면,
HS-JEPA의 target representation은 human-relative일 뿐 아니라 episode-relative여야 한다.
```

나쁜 결과:

```text
episode conditioning이 오히려 나빠지면,
현재 row sequence/episode features는 subject-heldout에서 shortcut으로 작동한다.
그 경우 episode는 direct feature가 아니라 action-space constraint나 diagnostic으로만 써야 한다.
```
"""


def episode_feature_summary(train_modes: pd.DataFrame, test_modes: pd.DataFrame, episode_cols: list[str]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for col in episode_cols:
        if col.startswith("episode_bin__") or col in {"episode_subject_row_index", "episode_weekday"}:
            continue
        train_values = pd.to_numeric(train_modes[col], errors="coerce")
        test_values = pd.to_numeric(test_modes[col], errors="coerce")
        rows.append(
            {
                "feature": col,
                "train_mean": float(train_values.mean()),
                "train_std": float(train_values.std(ddof=0)),
                "test_mean": float(test_values.mean()),
                "test_std": float(test_values.std(ddof=0)),
            }
        )
    return pd.DataFrame(rows).sort_values("feature").head(32)


def run() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    train_cells, test_cells, train_priors, _view_metrics = build_listener_cells()
    train_cells, test_cells, _contrastive_metrics, _contrastive_summary = add_subject_contrastive_scores(train_cells, test_cells)
    train_modes, test_modes = build_mode_tables(train_cells, test_cells)
    train_modes, test_modes, episode_cols = add_episode_context(train_modes, test_modes)
    train_modes = add_episode_conditioned_targets(train_modes)
    feature_cols = utility_feature_columns(train_modes, test_modes) + [
        col for col in episode_cols if col in train_modes.columns and col in test_modes.columns
    ]
    feature_cols = list(dict.fromkeys(feature_cols))
    train_scored, test_scored, metrics = fit_episode_conditioned_models(train_modes, test_modes, feature_cols)

    grid = policy_grid(train_scored, null_repeats=NULL_REPEATS)
    full_chosen = choose_policies(grid)
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
    candidate_name = f"submission_hsjepa_episode_conditioned_relative_tail_anchor_free_{short_hash(candidate)}_uploadsafe.csv"

    selected_full = full_audit[full_audit["released"]].copy()
    stable_oof_audit = apply_policies(train_scored, stable)
    stable_selected = stable_oof_audit[stable_oof_audit["released"]].copy()
    nested_selected = nested_audit[nested_audit["released"]].copy()
    full_oof_gain = float(selected_full["effective_gain"].sum()) if len(selected_full) else 0.0
    nested_gain = float(nested_selected["effective_gain"].sum()) if len(nested_selected) else 0.0
    stable_oof_gain = float(stable_selected["effective_gain"].sum()) if len(stable_selected) else 0.0
    stable_targets = stable.loc[stable["accepted"].eq(True), "target"].astype(str).tolist() if "accepted" in stable else []
    verdict = (
        "episode_conditioned_relative_tail_subjectheldout_positive"
        if nested_gain > 0 and stable_count > 0
        else "episode_conditioned_relative_tail_oof_positive_subjectheldout_fragile"
        if full_oof_gain > 0
        else "episode_conditioned_relative_tail_negative"
    )

    summary = {
        "package": "episode_conditioned_relative_tail_core",
        "status": "episode_conditioned_relative_tail_core_ready",
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

    efs = episode_feature_summary(train_scored, test_scored, episode_cols)
    grid.to_csv(OUT_DIR / "episode_conditioned_policy_grid.csv", index=False)
    full_chosen.to_csv(OUT_DIR / "episode_conditioned_full_chosen_policies.csv", index=False)
    full_audit.to_csv(OUT_DIR / "episode_conditioned_full_oof_action_audit.csv", index=False)
    nested_subject_summary.to_csv(OUT_DIR / "episode_conditioned_nested_subject_summary.csv", index=False)
    nested_route_rows.to_csv(OUT_DIR / "episode_conditioned_nested_route_rows.csv", index=False)
    nested_target_summary.to_csv(OUT_DIR / "episode_conditioned_nested_target_summary.csv", index=False)
    stable.to_csv(OUT_DIR / "episode_conditioned_stable_policies.csv", index=False)
    metrics.to_csv(OUT_DIR / "episode_conditioned_tail_model_metrics.csv", index=False)
    efs.to_csv(OUT_DIR / "episode_conditioned_feature_summary.csv", index=False)
    test_audit.to_csv(OUT_DIR / "episode_conditioned_test_release_audit.csv", index=False)
    candidate.to_csv(OUT_DIR / candidate_name, index=False)
    candidate.to_csv(ROOT / candidate_name, index=False)
    (OUT_DIR / "episode_conditioned_relative_tail_core_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    md = build_markdown(summary, metrics, full_chosen, nested_subject_summary, nested_target_summary, stable, grid, efs)
    (OUT_DIR / "EPISODE_CONDITIONED_RELATIVE_TAIL_CORE_KO.md").write_text(md, encoding="utf-8")
    PAPER_DOC.write_text(md, encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


if __name__ == "__main__":
    run()
