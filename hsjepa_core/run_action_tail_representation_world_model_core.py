#!/usr/bin/env python3
"""Action-tail representation world-model experiment for HS-JEPA.

The previous rhythm-conditioned action-health experiment showed a boundary:
readable rhythm/listener representations do not automatically become a safe
row-target action decoder.

This experiment changes the objective instead of adding more features:

    visible human-life context
      -> hidden row-level action-tail representation
      -> row-target action-health decoder

The hidden teacher is built from OG train labels only.  For each row it stores
the gain/tail/health/toxicity field of raw and inverse actions across all
targets.  A split-specific world model predicts that hidden field from visible
context, and the predicted representation is then tested under
subject-heldout, row-block, and chronological action-health stress.

No public LB ledger, prior submission probabilities, or proprietary embedding
APIs are used.  Because the hidden action-tail teacher is label-derived, this
runner is a core-to-decoder bridge, not a pure label-free HS-JEPA core claim.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, mean_absolute_error, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hsjepa_core.run_action_support_world_model_core import target_context_columns  # noqa: E402
from hsjepa_core.run_label_free_transported_listener_responsibility_core import split_folds  # noqa: E402
from hsjepa_core.run_learned_listener_responsibility_pretext_core import (  # noqa: E402
    flatten_cols,
    json_safe,
    subject_relative_context,
)
from hsjepa_core.run_lifelog_core_state_evidence import (  # noqa: E402
    TARGETS,
    catalog_features,
    format_float,
    load_frames,
    markdown_table,
    view_columns,
)
from hsjepa_core.run_rhythm_conditioned_action_health_core import (  # noqa: E402
    add_mode_interactions,
    add_split_features_to_cells,
    row_folds_to_mode_folds,
    split_interface_features,
)
from hsjepa_core.run_tail_safe_expected_utility_core import (  # noqa: E402
    build_mode_tables,
)
from sleep_competition_adapter.target_route_conservation_decoder import build_listener_cells, route_family  # noqa: E402


OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "action_tail_representation_world_model_core"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "ACTION_TAIL_REPRESENTATION_WORLD_MODEL_CORE_KO.md"
RANDOM_SEED = 20260614
NULL_REPEATS = 0
FAST_POLICY_FRACTIONS = [0.01, 0.02, 0.05, 0.10]
FAST_POLICY_SCORE_COLS = [
    "tail_safe_utility",
    "health_weighted_utility",
    "pessimistic_utility",
    "predicted_gain",
]


def clean_name(value: str) -> str:
    return (
        str(value)
        .replace(" ", "_")
        .replace("/", "_")
        .replace("-", "_")
        .replace(".", "_")
        .replace("(", "")
        .replace(")", "")
        .lower()
    )


def finite_frame(frame: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    return frame[cols].replace([np.inf, -np.inf], np.nan)


def component_correlation(y_true: np.ndarray, y_pred: np.ndarray) -> float | None:
    values: list[float] = []
    for idx in range(y_true.shape[1]):
        a = y_true[:, idx]
        b = y_pred[:, idx]
        mask = np.isfinite(a) & np.isfinite(b)
        if mask.sum() < 3 or np.std(a[mask]) <= 1e-12 or np.std(b[mask]) <= 1e-12:
            continue
        values.append(float(np.corrcoef(a[mask], b[mask])[0, 1]))
    if not values:
        return None
    return float(np.mean(values))


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


def action_tail_teacher(modes: pd.DataFrame) -> pd.DataFrame:
    """Build one hidden action-tail vector per row from mode-level outcomes."""

    rows = sorted(modes["row"].astype(int).unique())
    out = pd.DataFrame(index=rows)
    stats = ["effective_gain", "tail_loss", "healthy_action", "toxic_tail"]
    mode_names = {
        "raw_memory_release": "raw",
        "inverse_toxic_memory": "inverse",
    }
    for mode_name, mode_short in mode_names.items():
        mode_part = modes[modes["decoder_action"].eq(mode_name)]
        for target in TARGETS:
            part = mode_part[mode_part["target"].eq(target)].set_index("row")
            for stat in stats:
                col = f"teacher_{mode_short}_{target}_{stat}"
                out[col] = part[stat].reindex(rows).astype(float)

    gain_cols = [col for col in out.columns if col.endswith("_effective_gain")]
    tail_cols = [col for col in out.columns if col.endswith("_tail_loss")]
    toxic_cols = [col for col in out.columns if col.endswith("_toxic_tail")]
    health_cols = [col for col in out.columns if col.endswith("_healthy_action")]
    out["teacher_gain_mean"] = out[gain_cols].mean(axis=1)
    out["teacher_gain_max"] = out[gain_cols].max(axis=1)
    out["teacher_gain_min"] = out[gain_cols].min(axis=1)
    out["teacher_tail_mean"] = out[tail_cols].mean(axis=1)
    out["teacher_tail_max"] = out[tail_cols].max(axis=1)
    out["teacher_toxic_count"] = out[toxic_cols].sum(axis=1)
    out["teacher_health_count"] = out[health_cols].sum(axis=1)
    for target in TARGETS:
        raw_col = f"teacher_raw_{target}_effective_gain"
        inverse_col = f"teacher_inverse_{target}_effective_gain"
        out[f"teacher_{target}_raw_minus_inverse_gain"] = out[raw_col] - out[inverse_col]
        out[f"teacher_{target}_best_gain"] = np.maximum(out[raw_col], out[inverse_col])
    return out.reset_index(drop=True).replace([np.inf, -np.inf], np.nan).fillna(0.0)


def make_pretext_predictor(feature_count: int, train_count: int) -> Any:
    steps: list[Any] = [SimpleImputer(strategy="median"), StandardScaler()]
    if feature_count > 64 and train_count > 16:
        steps.append(PCA(n_components=min(48, feature_count, train_count - 1), random_state=RANDOM_SEED))
    steps.append(Ridge(alpha=18.0))
    return make_pipeline(*steps)


def predict_hidden_tail(
    context: pd.DataFrame,
    teacher: pd.DataFrame,
    folds: list[tuple[np.ndarray, np.ndarray]],
    feature_cols: list[str],
) -> tuple[pd.DataFrame, dict[str, Any]]:
    feature_cols = [col for col in feature_cols if col in context.columns]
    if not feature_cols:
        pred = pd.DataFrame(
            np.tile(teacher.mean(axis=0).to_numpy(dtype=np.float64), (len(teacher), 1)),
            columns=[f"pred_{col}" for col in teacher.columns],
        )
        return pred, {
            "feature_count": 0,
            "teacher_mae": None,
            "teacher_mae_lift_vs_mean": None,
            "component_corr": None,
        }

    y = teacher.to_numpy(dtype=np.float64)
    oof = np.zeros_like(y, dtype=np.float64)
    mean_pred = np.zeros_like(y, dtype=np.float64)
    for fold, (tr, va) in enumerate(folds):
        model = make_pretext_predictor(len(feature_cols), len(tr))
        model.fit(finite_frame(context.iloc[tr], feature_cols), y[tr])
        oof[va] = model.predict(finite_frame(context.iloc[va], feature_cols))
        mean_pred[va] = y[tr].mean(axis=0, keepdims=True)
    pred = pd.DataFrame(oof, columns=[f"pred_{col}" for col in teacher.columns])
    mae = float(mean_absolute_error(y, oof))
    null_mae = float(mean_absolute_error(y, mean_pred))
    return pred, {
        "feature_count": int(len(feature_cols)),
        "teacher_mae": mae,
        "teacher_mean_baseline_mae": null_mae,
        "teacher_mae_lift_vs_mean": null_mae - mae,
        "component_corr": component_correlation(y, oof),
    }


def expand_tail_prediction_to_modes(modes: pd.DataFrame, tail_pred: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    row_idx = modes["row"].to_numpy(dtype=np.int64)
    mode_short = np.where(modes["decoder_action"].eq("raw_memory_release"), "raw", "inverse")
    target_values = modes["target"].astype(str).to_numpy()
    out = pd.DataFrame(index=modes.index)
    cols: list[str] = []

    for stat in ["effective_gain", "tail_loss", "healthy_action", "toxic_tail"]:
        values = np.zeros(len(modes), dtype=np.float64)
        for target in TARGETS:
            for action_short in ["raw", "inverse"]:
                mask = (target_values == target) & (mode_short == action_short)
                source_col = f"pred_teacher_{action_short}_{target}_{stat}"
                if source_col in tail_pred.columns:
                    values[mask] = tail_pred.iloc[row_idx[mask]][source_col].to_numpy(dtype=np.float64)
        out_col = f"pred_action_tail_{stat}"
        out[out_col] = values
        cols.append(out_col)

    for col in [
        "pred_teacher_gain_mean",
        "pred_teacher_gain_max",
        "pred_teacher_gain_min",
        "pred_teacher_tail_mean",
        "pred_teacher_tail_max",
        "pred_teacher_toxic_count",
        "pred_teacher_health_count",
    ]:
        if col in tail_pred.columns:
            out_col = f"row_{col}"
            out[out_col] = tail_pred.iloc[row_idx][col].to_numpy(dtype=np.float64)
            cols.append(out_col)

    out["pred_action_tail_utility"] = (
        out["pred_action_tail_effective_gain"]
        - 1.20 * np.maximum(out["pred_action_tail_tail_loss"], 0.0)
        - 0.08 * np.clip(out["pred_action_tail_toxic_tail"], 0.0, 1.0)
    )
    out["pred_action_tail_health_margin"] = (
        np.clip(out["pred_action_tail_healthy_action"], 0.0, 1.0)
        - np.clip(out["pred_action_tail_toxic_tail"], 0.0, 1.0)
    )
    cols.extend(["pred_action_tail_utility", "pred_action_tail_health_margin"])
    return out.replace([np.inf, -np.inf], np.nan).fillna(0.0), cols


def row_context_sources(
    row_features: pd.DataFrame,
    relative_context: pd.DataFrame,
    residual_cols: dict[str, list[str]],
    gated_cols: dict[str, list[str]],
    global_cols: list[str],
    rhythm_cols: list[str],
) -> dict[str, list[str]]:
    residual_flat = flatten_cols(residual_cols)
    gated_flat = flatten_cols(gated_cols)
    relative_cols = [col for col in relative_context.columns if col in row_features.columns]
    # The split interface is built from transported grammar/rhythm/listener heads.
    # Relative OG context is appended below to keep the target prediction visible-context based.
    sources = {
        "relative_lifelog_context": relative_cols,
        "transport_rhythm_context": sorted(set(global_cols + rhythm_cols)),
        "listener_rhythm_interface": sorted(set(global_cols + rhythm_cols + residual_flat + gated_flat)),
    }
    return {name: [col for col in cols if col in row_features.columns] for name, cols in sources.items()}


def action_base_columns(modes: pd.DataFrame) -> list[str]:
    action_base = [
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
    ]
    route_cols = [col for col in modes.columns if col.startswith("route_family__")]
    return [col for col in target_context_columns() + action_base + route_cols if col in modes.columns]


def support_columns(modes: pd.DataFrame) -> list[str]:
    return [
        col
        for col in [
            "support_score_target_interaction_world_residual_energy",
            "listener_mode_alignment",
            "listener_support_x_mode_rhythm_alignment",
        ]
        if col in modes.columns
    ]


def make_fast_regressor(feature_count: int, train_count: int) -> Any:
    steps: list[Any] = [SimpleImputer(strategy="median"), StandardScaler()]
    if feature_count > 48 and train_count > 16:
        steps.append(PCA(n_components=min(32, feature_count, train_count - 1), random_state=RANDOM_SEED))
    steps.append(Ridge(alpha=10.0))
    return make_pipeline(*steps)


def make_fast_classifier(feature_count: int, train_count: int) -> Any:
    steps: list[Any] = [SimpleImputer(strategy="median"), StandardScaler()]
    if feature_count > 48 and train_count > 16:
        steps.append(PCA(n_components=min(32, feature_count, train_count - 1), random_state=RANDOM_SEED))
    steps.append(LogisticRegression(C=0.35, max_iter=3000, solver="lbfgs"))
    return make_pipeline(*steps)


def fit_fast_split_utility(
    modes: pd.DataFrame,
    features: list[str],
    folds: list[tuple[np.ndarray, np.ndarray]],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    features = [col for col in features if col in modes.columns]
    y_gain = modes["effective_gain"].astype(float).to_numpy()
    y_tail = modes["tail_loss"].astype(float).to_numpy()
    y_health = modes["healthy_action"].astype(int).to_numpy()
    y_toxic = modes["toxic_tail"].astype(int).to_numpy()
    oof_gain = np.zeros(len(modes), dtype=np.float64)
    oof_tail = np.zeros(len(modes), dtype=np.float64)
    oof_health = np.zeros(len(modes), dtype=np.float64)
    oof_toxic = np.zeros(len(modes), dtype=np.float64)

    for tr, va in folds:
        if not features:
            oof_gain[va] = float(y_gain[tr].mean())
            oof_tail[va] = float(y_tail[tr].mean())
            oof_health[va] = float(y_health[tr].mean())
            oof_toxic[va] = float(y_toxic[tr].mean())
            continue
        gain_model = make_fast_regressor(len(features), len(tr))
        tail_model = make_fast_regressor(len(features), len(tr))
        gain_model.fit(finite_frame(modes.iloc[tr], features), y_gain[tr])
        tail_model.fit(finite_frame(modes.iloc[tr], features), y_tail[tr])
        oof_gain[va] = gain_model.predict(finite_frame(modes.iloc[va], features))
        oof_tail[va] = np.maximum(tail_model.predict(finite_frame(modes.iloc[va], features)), 0.0)
        if len(np.unique(y_health[tr])) < 2:
            oof_health[va] = float(y_health[tr].mean())
        else:
            health_model = make_fast_classifier(len(features), len(tr))
            health_model.fit(finite_frame(modes.iloc[tr], features), y_health[tr])
            oof_health[va] = health_model.predict_proba(finite_frame(modes.iloc[va], features))[:, 1]
        if len(np.unique(y_toxic[tr])) < 2:
            oof_toxic[va] = float(y_toxic[tr].mean())
        else:
            toxic_model = make_fast_classifier(len(features), len(tr))
            toxic_model.fit(finite_frame(modes.iloc[tr], features), y_toxic[tr])
            oof_toxic[va] = toxic_model.predict_proba(finite_frame(modes.iloc[va], features))[:, 1]

    scored = modes.copy()
    scored["predicted_gain"] = oof_gain
    scored["predicted_tail_loss"] = oof_tail
    scored["predicted_health_prob"] = oof_health
    scored["predicted_toxic_tail_prob"] = oof_toxic
    scored["tail_safe_utility"] = scored["predicted_gain"] - 1.20 * scored["predicted_tail_loss"] - 0.08 * scored["predicted_toxic_tail_prob"]
    scored["health_weighted_utility"] = scored["predicted_health_prob"] * scored["predicted_gain"] - 1.50 * scored["predicted_toxic_tail_prob"]
    scored["pessimistic_utility"] = scored["predicted_gain"] - 2.00 * scored["predicted_tail_loss"] - 0.20 * scored["predicted_toxic_tail_prob"]
    scored["health_score_only"] = scored["predicted_health_prob"]
    metrics = pd.DataFrame(
        [
            {"metric": "feature_count", "value": len(features)},
            {"metric": "gain_mae", "value": float(mean_absolute_error(y_gain, oof_gain))},
            {"metric": "tail_loss_mae", "value": float(mean_absolute_error(y_tail, oof_tail))},
            {"metric": "health_auc", "value": safe_auc(y_health, oof_health)},
            {"metric": "health_ap", "value": safe_ap(y_health, oof_health)},
            {"metric": "toxic_tail_auc", "value": safe_auc(y_toxic, oof_toxic)},
            {"metric": "toxic_tail_ap", "value": safe_ap(y_toxic, oof_toxic)},
        ]
    )
    return scored, metrics


def fast_policy_readout(scored: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Evaluate a compact set of stress policies without full grid search.

    This runner tests whether the predicted hidden action-tail representation
    is readable under held-out stress.  The exhaustive release policy grid in
    the competition adapter is too slow here and would make the core experiment
    harder to iterate, so we keep a deliberately small readout surface.
    """

    rows: list[dict[str, Any]] = []
    audit_parts: list[pd.DataFrame] = []
    for target in TARGETS:
        target_frame = scored[scored["target"].eq(target)].copy()
        for score_col in FAST_POLICY_SCORE_COLS:
            if score_col not in target_frame.columns:
                continue
            ordered = target_frame.sort_values(score_col, ascending=False)
            for fraction in FAST_POLICY_FRACTIONS:
                take = max(1, int(round(len(ordered) * fraction)))
                selected = ordered.head(take).copy()
                gain_sum = float(selected["effective_gain"].sum()) if len(selected) else 0.0
                positive_rate = float((selected["effective_gain"] > 0).mean()) if len(selected) else np.nan
                accepted = bool(gain_sum > 0.0 and positive_rate >= 0.55 and len(selected) >= 5)
                rows.append(
                    {
                        "target": target,
                        "score_col": score_col,
                        "policy": "top_score",
                        "fraction": fraction,
                        "selected_cells": int(len(selected)),
                        "selected_gain_sum": gain_sum,
                        "selected_mean_gain": float(selected["effective_gain"].mean()) if len(selected) else 0.0,
                        "selected_positive_gain_rate": positive_rate,
                        "active_subjects": int(selected["subject_id"].nunique()) if "subject_id" in selected else 0,
                        "positive_subjects": int(
                            (
                                selected.groupby("subject_id", observed=True)["effective_gain"].sum() > 0
                            ).sum()
                        )
                        if "subject_id" in selected and len(selected)
                        else 0,
                        "negative_subjects": int(
                            (
                                selected.groupby("subject_id", observed=True)["effective_gain"].sum() < 0
                            ).sum()
                        )
                        if "subject_id" in selected and len(selected)
                        else 0,
                        "raw_action_count": int(selected["decoder_action"].eq("raw_memory_release").sum())
                        if len(selected)
                        else 0,
                        "inverse_action_count": int(selected["decoder_action"].eq("inverse_toxic_memory").sum())
                        if len(selected)
                        else 0,
                        "null_gain_mean": 0.0,
                        "null_gain_std": np.nan,
                        "gain_lift_vs_null": gain_sum,
                        "gain_z_vs_null": np.nan,
                        "tail_safe_policy_score": gain_sum * max(positive_rate if np.isfinite(positive_rate) else 0.0, 0.0),
                        "accepted": accepted,
                        "accept_reason": "fast_stress_policy_passed" if accepted else "fast_stress_policy_failed",
                    }
                )
                if accepted:
                    selected = selected.copy()
                    selected["released"] = True
                    selected["policy_score_col"] = score_col
                    selected["policy_fraction"] = fraction
                    audit_parts.append(selected)
    grid = pd.DataFrame(rows)
    if grid.empty:
        return grid, pd.DataFrame()
    chosen = (
        grid.sort_values(
            ["target", "tail_safe_policy_score", "selected_gain_sum"],
            ascending=[True, False, False],
        )
        .groupby("target", observed=True)
        .head(1)
        .reset_index(drop=True)
    )
    if audit_parts:
        audit = pd.concat(audit_parts, ignore_index=True, sort=False)
        accepted_keys = set(
            zip(
                chosen.loc[chosen["accepted"], "target"],
                chosen.loc[chosen["accepted"], "score_col"],
                chosen.loc[chosen["accepted"], "fraction"],
            )
        )
        audit = audit[
            [
                (row.target, row.policy_score_col, row.policy_fraction) in accepted_keys
                for row in audit.itertuples(index=False)
            ]
        ].copy()
    else:
        audit = pd.DataFrame()
    return chosen, audit


def evaluate_tail_source(
    split_name: str,
    source_name: str,
    train_modes: pd.DataFrame,
    tail_cols: list[str],
    mode_folds: list[tuple[np.ndarray, np.ndarray]],
) -> tuple[list[dict[str, Any]], list[pd.DataFrame], list[pd.DataFrame]]:
    base = action_base_columns(train_modes)
    support = support_columns(train_modes)
    feature_sets = {
        "action_only": base,
        "listener_support_baseline": base + support,
        f"{source_name}_tail_representation": base + tail_cols,
        f"{source_name}_tail_plus_listener": base + support + tail_cols,
    }
    rows: list[dict[str, Any]] = []
    chosen_parts: list[pd.DataFrame] = []
    audit_parts: list[pd.DataFrame] = []
    for feature_name, cols in feature_sets.items():
        scored, metrics = fit_fast_split_utility(train_modes, sorted(set(cols)), mode_folds)
        chosen, audit = fast_policy_readout(scored)
        selected = audit[audit["released"]].copy()
        accepted_targets = chosen.loc[chosen["accepted"].eq(True), "target"].astype(str).tolist()
        row = {
            "split": split_name,
            "source": source_name,
            "feature_set": feature_name,
            "feature_count": int(metrics.loc[metrics["metric"].eq("feature_count"), "value"].iloc[0]),
            "health_auc": float(metrics.loc[metrics["metric"].eq("health_auc"), "value"].iloc[0]),
            "health_ap": float(metrics.loc[metrics["metric"].eq("health_ap"), "value"].iloc[0]),
            "toxic_tail_auc": float(metrics.loc[metrics["metric"].eq("toxic_tail_auc"), "value"].iloc[0]),
            "toxic_tail_ap": float(metrics.loc[metrics["metric"].eq("toxic_tail_ap"), "value"].iloc[0]),
            "selected_gain_sum": float(selected["effective_gain"].sum()) if len(selected) else 0.0,
            "selected_cells": int(len(selected)),
            "selected_positive_gain_rate": float((selected["effective_gain"] > 0).mean()) if len(selected) else np.nan,
            "accepted_targets": ",".join(accepted_targets),
            "accepted_target_count": int(len(accepted_targets)),
        }
        rows.append(row)
        chosen = chosen.copy()
        chosen.insert(0, "feature_set", feature_name)
        chosen.insert(0, "source", source_name)
        chosen.insert(0, "split", split_name)
        chosen_parts.append(chosen)
        released = audit[audit["released"]].copy()
        if len(released):
            released["split"] = split_name
            released["source"] = source_name
            released["feature_set"] = feature_name
            keep_cols = [
                "split",
                "source",
                "feature_set",
                "row",
                "metric_row",
                "subject_id",
                "target",
                "decoder_action",
                "effective_gain",
                "predicted_gain",
                "predicted_tail_loss",
                "predicted_health_prob",
                "predicted_toxic_tail_prob",
            ]
            audit_parts.append(released[[col for col in keep_cols if col in released.columns]])
    return rows, chosen_parts, audit_parts


def summarize(results: pd.DataFrame, pretext: pd.DataFrame) -> dict[str, Any]:
    tail_rows = results[results["feature_set"].str.contains("_tail_representation|_tail_plus_listener", regex=True)]
    support_rows = results[results["feature_set"].eq("listener_support_baseline")]
    deltas: list[dict[str, Any]] = []
    for _, row in tail_rows.iterrows():
        support = support_rows[
            support_rows["split"].eq(row["split"]) & support_rows["source"].eq(row["source"])
        ]
        if support.empty:
            continue
        base = support.iloc[0]
        deltas.append(
            {
                "split": row["split"],
                "source": row["source"],
                "feature_set": row["feature_set"],
                "health_auc_delta_vs_listener": float(row["health_auc"] - base["health_auc"]),
                "toxic_tail_auc_delta_vs_listener": float(row["toxic_tail_auc"] - base["toxic_tail_auc"]),
                "selected_gain_delta_vs_listener": float(row["selected_gain_sum"] - base["selected_gain_sum"]),
                "accepted_target_delta_vs_listener": int(row["accepted_target_count"] - base["accepted_target_count"]),
            }
        )
    delta_frame = pd.DataFrame(deltas)
    best_gain = results.sort_values("selected_gain_sum", ascending=False).head(1)
    best_health_delta = (
        None
        if delta_frame.empty
        else delta_frame.sort_values("health_auc_delta_vs_listener", ascending=False).head(1).iloc[0].to_dict()
    )
    best_toxic_delta = (
        None
        if delta_frame.empty
        else delta_frame.sort_values("toxic_tail_auc_delta_vs_listener", ascending=False).head(1).iloc[0].to_dict()
    )
    best_pretext = (
        None
        if pretext.empty
        else pretext.sort_values("teacher_mae_lift_vs_mean", ascending=False).head(1).iloc[0].to_dict()
    )
    accepted_total = int(tail_rows["accepted_target_count"].sum()) if len(tail_rows) else 0
    positive_health = 0 if delta_frame.empty else int((delta_frame["health_auc_delta_vs_listener"] > 0.0).sum())
    positive_toxic = 0 if delta_frame.empty else int((delta_frame["toxic_tail_auc_delta_vs_listener"] > 0.0).sum())
    pretext_lift = (best_pretext or {}).get("teacher_mae_lift_vs_mean") or 0.0
    verdict = "action_tail_representation_world_model_negative"
    if pretext_lift > 0.0 and accepted_total > 0 and positive_health >= 2 and positive_toxic >= 2:
        verdict = "action_tail_representation_world_model_action_bridge_positive"
    elif accepted_total > 0 and pretext_lift <= 0.0:
        verdict = "action_tail_policy_readout_positive_but_pretext_not_readable"
    elif positive_health >= 2 or positive_toxic >= 2:
        verdict = "action_tail_representation_decoder_signal_but_not_release_safe"
    elif pretext_lift > 0.0:
        verdict = "action_tail_representation_world_model_pretext_positive_decoder_negative"
    return {
        "package": "action_tail_representation_world_model_core",
        "status": "action_tail_representation_world_model_core_ready",
        "verdict": verdict,
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "uses_label_as_action_tail_teacher": True,
        "architecture_question": "can_visible_context_predict_hidden_action_tail_representation",
        "accepted_target_count_total": accepted_total,
        "positive_health_delta_count": positive_health,
        "positive_toxic_delta_count": positive_toxic,
        "best_selected_gain_row": None if best_gain.empty else best_gain.iloc[0].to_dict(),
        "best_health_delta_vs_listener": best_health_delta,
        "best_toxic_tail_delta_vs_listener": best_toxic_delta,
        "best_pretext": best_pretext,
        "delta_table": delta_frame.to_dict(orient="records"),
    }


def build_markdown(summary: dict[str, Any], pretext: pd.DataFrame, results: pd.DataFrame, chosen: pd.DataFrame) -> str:
    return f"""# Action-Tail Representation World Model Core

## 한 줄 요약

이 실험은 HS-JEPA의 다음 단계 질문을 검증한다.

```text
visible human-life context
  -> hidden row-level action-tail representation
  -> row-target action-health decoder
```

직전 실험은 rhythm/residual representation이 곧바로 action decoder가 되지 않는다는
negative boundary였다. 이번에는 action-tail 자체를 hidden target으로 만들고,
그 target을 context에서 예측할 수 있는지 본다.

## 사용하지 않은 정보

- public LB ledger: `{summary["uses_public_score_ledger"]}`
- prior submission probabilities: `{summary["uses_prior_submission_probabilities"]}`
- proprietary embedding API: `{summary["uses_proprietary_embedding_api"]}`

## 중요한 경계

- label-derived action-tail teacher 사용: `{summary["uses_label_as_action_tail_teacher"]}`

따라서 이 실험은 pure label-free core claim이 아니다.
정확한 위치는 `HS-JEPA core-to-decoder bridge`다.

## 판정

- verdict: `{summary["verdict"]}`
- accepted target count total: `{summary["accepted_target_count_total"]}`
- positive health delta count: `{summary["positive_health_delta_count"]}`
- positive toxic-tail delta count: `{summary["positive_toxic_delta_count"]}`

best pretext:

```json
{json.dumps(json_safe(summary["best_pretext"]), ensure_ascii=False, indent=2)}
```

best health delta vs listener:

```json
{json.dumps(json_safe(summary["best_health_delta_vs_listener"]), ensure_ascii=False, indent=2)}
```

best toxic-tail delta vs listener:

```json
{json.dumps(json_safe(summary["best_toxic_tail_delta_vs_listener"]), ensure_ascii=False, indent=2)}
```

## Pretext Results

{markdown_table(pretext, ["split", "source", "feature_count", "teacher_mae", "teacher_mean_baseline_mae", "teacher_mae_lift_vs_mean", "component_corr"], max_rows=40)}

## Action-Health Results

{markdown_table(results, ["split", "source", "feature_set", "feature_count", "health_auc", "toxic_tail_auc", "selected_gain_sum", "selected_cells", "accepted_targets"], max_rows=80)}

## Chosen Policies

{markdown_table(chosen, ["split", "source", "feature_set", "target", "accepted", "score_col", "policy", "fraction", "selected_cells", "selected_gain_sum", "selected_positive_gain_rate", "accept_reason"], max_rows=80)}

## 해석

positive이면:

```text
HS-JEPA는 visible context에서 action-tail representation을 예측할 수 있고,
그 representation은 release-grade action-health decoder에 기여한다.
```

negative이면:

```text
action-tail teacher를 만들었더라도 현재 visible context/world-model interface는
release-safe row-target assignment로 번역하기에 부족하다.
```

이번 실험이 중요한 이유는 실패해도 명확하다.
실패하면 다음 결론이 생긴다.

```text
action-tail은 단순히 row-level hidden vector로 만들면 충분하지 않다.
target-route/listener별 structured action-tail teacher가 필요하다.
```
"""


def run() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    PAPER_DOC.parent.mkdir(parents=True, exist_ok=True)
    frame_all, _labels = load_frames()
    train_frame = frame_all[frame_all["split"].eq("train")].reset_index(drop=True)
    catalog = catalog_features(frame_all)
    views = view_columns(catalog)
    context_cols = sorted(set(catalog.raw_numeric + catalog.calendar + catalog.core_state))
    raw_context = train_frame[context_cols].reset_index(drop=True)
    relative_context = subject_relative_context(train_frame, raw_context).reset_index(drop=True)

    base_train_cells, base_test_cells, _priors, _view_metrics = build_listener_cells()
    placeholder = base_test_cells.copy()

    pretext_rows: list[dict[str, Any]] = []
    result_rows: list[dict[str, Any]] = []
    chosen_parts: list[pd.DataFrame] = []
    audit_parts: list[pd.DataFrame] = []
    for split_name in ["subject_heldout", "chronological_holdout", "row_block_holdout"]:
        row_features, residual_cols, gated_cols, global_cols, rhythm_cols = split_interface_features(
            split_name,
            train_frame,
            relative_context,
            views,
        )
        row_features = pd.concat(
            [
                row_features.reset_index(drop=True),
                relative_context.add_prefix("relative_context__").reset_index(drop=True),
            ],
            axis=1,
        )
        relative_prefixed = relative_context.add_prefix("relative_context__")
        train_cells, groups = add_split_features_to_cells(
            base_train_cells,
            row_features,
            residual_cols,
            gated_cols,
            global_cols,
            rhythm_cols,
        )
        train_modes, _test_modes = build_mode_tables(train_cells, placeholder)
        train_modes = add_mode_interactions(train_modes)
        teacher = action_tail_teacher(train_modes)
        row_folds = split_folds(split_name, train_frame)
        mode_folds = row_folds_to_mode_folds(train_modes, row_folds)
        sources = row_context_sources(
            row_features,
            relative_prefixed,
            residual_cols,
            gated_cols,
            global_cols,
            rhythm_cols,
        )
        for source_name, cols in sources.items():
            pred_tail, pretext_metric = predict_hidden_tail(row_features, teacher, row_folds, cols)
            pretext_rows.append({"split": split_name, "source": source_name, **pretext_metric})
            tail_features, tail_cols = expand_tail_prediction_to_modes(train_modes, pred_tail)
            modes_with_tail = pd.concat([train_modes.reset_index(drop=True), tail_features.reset_index(drop=True)], axis=1)
            rows, chosen, audit = evaluate_tail_source(
                split_name,
                source_name,
                modes_with_tail,
                tail_cols,
                mode_folds,
            )
            result_rows.extend(rows)
            chosen_parts.extend(chosen)
            audit_parts.extend(audit)

    pretext = pd.DataFrame(pretext_rows).sort_values(["split", "teacher_mae_lift_vs_mean"], ascending=[True, False])
    results = pd.DataFrame(result_rows).sort_values(["split", "selected_gain_sum"], ascending=[True, False])
    chosen_all = pd.concat(chosen_parts, ignore_index=True, sort=False)
    audit_all = pd.concat(audit_parts, ignore_index=True, sort=False) if audit_parts else pd.DataFrame()
    summary = summarize(results, pretext)

    pretext.to_csv(OUT_DIR / "action_tail_representation_pretext_results.csv", index=False)
    results.to_csv(OUT_DIR / "action_tail_representation_action_health_results.csv", index=False)
    chosen_all.to_csv(OUT_DIR / "action_tail_representation_chosen_policies.csv", index=False)
    audit_all.to_csv(OUT_DIR / "action_tail_representation_release_audit.csv", index=False)
    (OUT_DIR / "action_tail_representation_world_model_summary.json").write_text(
        json.dumps(json_safe(summary), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    doc = build_markdown(summary, pretext, results, chosen_all)
    (OUT_DIR / "ACTION_TAIL_REPRESENTATION_WORLD_MODEL_CORE_KO.md").write_text(doc, encoding="utf-8")
    PAPER_DOC.write_text(doc, encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(json_safe(run()), ensure_ascii=False, indent=2))
