#!/usr/bin/env python3
"""Masked-view consensus tail core for HS-JEPA.

Episode-conditioned relative tails reduced subject-heldout damage, but the
release remained fragile.  This experiment asks a stricter JEPA/LeJEPA question:

    Does the hidden action-tail representation survive meaningful context masks?

Instead of trusting one full-context decoder, it predicts the same
episode-conditioned relative tail field from multiple context views:

    full context
    context without world residual/energy
    context without episode sequence features
    context without listener/support features

Actions are released only when the predicted hidden tail field is useful and
low-disagreement across views.  No public LB ledger, prior submission
probabilities, or proprietary embedding APIs are used.
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
from hsjepa_core.run_episode_conditioned_relative_tail_core import (  # noqa: E402
    NULL_REPEATS as EPISODE_NULL_REPEATS,
    add_episode_conditioned_targets,
    add_episode_context,
    episode_feature_summary,
)
from hsjepa_core.run_lifelog_core_state_evidence import format_float, markdown_table  # noqa: E402
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


OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "masked_view_consensus_tail_core"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "MASKED_VIEW_CONSENSUS_TAIL_CORE_KO.md"
RANDOM_SEED = 20260613
NULL_REPEATS = min(10, EPISODE_NULL_REPEATS)


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


def is_world_residual_col(col: str) -> bool:
    return col.startswith("wm_resid_") or col.startswith("wm_energy")


def is_episode_col(col: str) -> bool:
    return col.startswith("episode_")


def is_listener_support_col(col: str) -> bool:
    return (
        col.startswith("support_score_")
        or col.startswith("mode_alignment__support_score_")
        or col.startswith("target_interaction__")
        or col.startswith("family_interaction__")
        or col == "listener_mode_alignment"
    )


def build_view_feature_sets(feature_cols: list[str]) -> dict[str, list[str]]:
    view_specs: dict[str, list[str]] = {
        "full_context": feature_cols,
        "mask_world_residual": [col for col in feature_cols if not is_world_residual_col(col)],
        "mask_episode_context": [col for col in feature_cols if not is_episode_col(col)],
        "mask_listener_support": [col for col in feature_cols if not is_listener_support_col(col)],
    }
    return {name: list(dict.fromkeys(cols)) for name, cols in view_specs.items() if len(cols) >= 8}


def fit_one_view(
    train_modes: pd.DataFrame,
    test_modes: pd.DataFrame,
    feature_cols: list[str],
    view_name: str,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
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

        gain_model = regressor_factory(stable_seed("masked-view-gain", view_name, subject))
        tail_model = regressor_factory(stable_seed("masked-view-tail", view_name, subject))
        gain_model.fit(train_modes.iloc[tr][feature_cols], y_gain[tr], histgradientboostingregressor__sample_weight=weights[tr])
        tail_model.fit(train_modes.iloc[tr][feature_cols], y_tail[tr], histgradientboostingregressor__sample_weight=weights[tr])
        oof_gain[va] = gain_model.predict(train_modes.iloc[va][feature_cols])
        oof_tail[va] = np.maximum(tail_model.predict(train_modes.iloc[va][feature_cols]), 0.0)

        if len(np.unique(y_pos[tr])) < 2:
            oof_pos[va] = float(y_pos[tr].mean())
        else:
            pos_model = classifier_factory(stable_seed("masked-view-positive", view_name, subject))
            pos_model.fit(train_modes.iloc[tr][feature_cols], y_pos[tr], histgradientboostingclassifier__sample_weight=weights[tr])
            oof_pos[va] = pos_model.predict_proba(train_modes.iloc[va][feature_cols])[:, 1]

        if len(np.unique(y_toxic[tr])) < 2:
            oof_toxic[va] = float(y_toxic[tr].mean())
        else:
            toxic_model = classifier_factory(stable_seed("masked-view-toxic", view_name, subject))
            toxic_model.fit(train_modes.iloc[tr][feature_cols], y_toxic[tr], histgradientboostingclassifier__sample_weight=weights[tr])
            oof_toxic[va] = toxic_model.predict_proba(train_modes.iloc[va][feature_cols])[:, 1]

    gain_model = regressor_factory(stable_seed("masked-view-gain", view_name, "full-test"))
    tail_model = regressor_factory(stable_seed("masked-view-tail", view_name, "full-test"))
    gain_model.fit(train_modes[feature_cols], y_gain, histgradientboostingregressor__sample_weight=weights)
    tail_model.fit(train_modes[feature_cols], y_tail, histgradientboostingregressor__sample_weight=weights)
    test_gain = gain_model.predict(test_modes[feature_cols])
    test_tail = np.maximum(tail_model.predict(test_modes[feature_cols]), 0.0)

    if len(np.unique(y_pos)) < 2:
        test_pos = np.full(len(test_modes), float(y_pos.mean()), dtype=np.float64)
    else:
        pos_model = classifier_factory(stable_seed("masked-view-positive", view_name, "full-test"))
        pos_model.fit(train_modes[feature_cols], y_pos, histgradientboostingclassifier__sample_weight=weights)
        test_pos = pos_model.predict_proba(test_modes[feature_cols])[:, 1]

    if len(np.unique(y_toxic)) < 2:
        test_toxic = np.full(len(test_modes), float(y_toxic.mean()), dtype=np.float64)
    else:
        toxic_model = classifier_factory(stable_seed("masked-view-toxic", view_name, "full-test"))
        toxic_model.fit(train_modes[feature_cols], y_toxic, histgradientboostingclassifier__sample_weight=weights)
        test_toxic = toxic_model.predict_proba(test_modes[feature_cols])[:, 1]

    train_pred = pd.DataFrame(
        {
            f"mv_{view_name}_gain": oof_gain,
            f"mv_{view_name}_tail": oof_tail,
            f"mv_{view_name}_positive": oof_pos,
            f"mv_{view_name}_toxic": oof_toxic,
        },
        index=train_modes.index,
    )
    test_pred = pd.DataFrame(
        {
            f"mv_{view_name}_gain": test_gain,
            f"mv_{view_name}_tail": test_tail,
            f"mv_{view_name}_positive": test_pos,
            f"mv_{view_name}_toxic": test_toxic,
        },
        index=test_modes.index,
    )
    metrics = {
        "view": view_name,
        "feature_count": len(feature_cols),
        "gain_mae": float(mean_absolute_error(y_gain, oof_gain)),
        "tail_mae": float(mean_absolute_error(y_tail, oof_tail)),
        "positive_auc": safe_auc(y_pos, oof_pos),
        "positive_ap": safe_ap(y_pos, oof_pos),
        "toxic_auc": safe_auc(y_toxic, oof_toxic),
        "toxic_ap": safe_ap(y_toxic, oof_toxic),
    }
    return train_pred, test_pred, metrics


def fit_masked_view_consensus(
    train_modes: pd.DataFrame,
    test_modes: pd.DataFrame,
    view_feature_sets: dict[str, list[str]],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train_scored = train_modes.copy()
    test_scored = test_modes.copy()
    metric_rows: list[dict[str, Any]] = []
    for view_name, feature_cols in view_feature_sets.items():
        train_pred, test_pred, metrics = fit_one_view(train_modes, test_modes, feature_cols, view_name)
        metric_rows.append(metrics)
        for col in train_pred.columns:
            train_scored[col] = train_pred[col].to_numpy(dtype=np.float64)
            test_scored[col] = test_pred[col].to_numpy(dtype=np.float64)

    gain_cols = [f"mv_{name}_gain" for name in view_feature_sets]
    tail_cols = [f"mv_{name}_tail" for name in view_feature_sets]
    pos_cols = [f"mv_{name}_positive" for name in view_feature_sets]
    toxic_cols = [f"mv_{name}_toxic" for name in view_feature_sets]

    for frame in [train_scored, test_scored]:
        frame["masked_view_gain_mean"] = frame[gain_cols].mean(axis=1)
        frame["masked_view_tail_mean"] = frame[tail_cols].mean(axis=1)
        frame["masked_view_positive_mean"] = frame[pos_cols].mean(axis=1)
        frame["masked_view_toxic_mean"] = frame[toxic_cols].mean(axis=1)
        frame["masked_view_gain_std"] = frame[gain_cols].std(axis=1, ddof=0)
        frame["masked_view_tail_std"] = frame[tail_cols].std(axis=1, ddof=0)
        frame["masked_view_toxic_std"] = frame[toxic_cols].std(axis=1, ddof=0)
        frame["masked_view_disagreement"] = (
            frame["masked_view_gain_std"].abs()
            + 0.65 * frame["masked_view_tail_std"].abs()
            + 0.45 * frame["masked_view_toxic_std"].abs()
        )
        frame["masked_view_consensus_utility"] = (
            frame["masked_view_gain_mean"]
            - 0.95 * frame["masked_view_tail_mean"]
            - 0.30 * frame["masked_view_toxic_mean"]
            - 0.45 * frame["masked_view_disagreement"]
        )
        frame["masked_view_consensus_pessimistic_utility"] = (
            frame["masked_view_gain_mean"]
            - 1.65 * frame["masked_view_tail_mean"]
            - 0.55 * frame["masked_view_toxic_mean"]
            - 0.80 * frame["masked_view_disagreement"]
        )
        frame["masked_view_consensus_health_score"] = (
            frame["masked_view_positive_mean"]
            - frame["masked_view_toxic_mean"]
            - 0.35 * frame["masked_view_disagreement"]
        )

    metric_rows.extend(
        [
            {
                "view": "consensus",
                "feature_count": sum(len(cols) for cols in view_feature_sets.values()),
                "gain_mae": float(mean_absolute_error(train_modes["episode_conditioned_gain"], train_scored["masked_view_gain_mean"])),
                "tail_mae": float(mean_absolute_error(train_modes["episode_relative_tail_loss"], train_scored["masked_view_tail_mean"])),
                "positive_auc": safe_auc(train_modes["episode_relative_positive"], train_scored["masked_view_positive_mean"]),
                "positive_ap": safe_ap(train_modes["episode_relative_positive"], train_scored["masked_view_positive_mean"]),
                "toxic_auc": safe_auc(train_modes["episode_relative_toxic_tail"], train_scored["masked_view_toxic_mean"]),
                "toxic_ap": safe_ap(train_modes["episode_relative_toxic_tail"], train_scored["masked_view_toxic_mean"]),
            }
        ]
    )
    return train_scored, test_scored, pd.DataFrame(metric_rows)


def policy_grid(modes: pd.DataFrame, null_repeats: int) -> pd.DataFrame:
    score_cols = [
        "masked_view_gain_mean",
        "masked_view_consensus_utility",
        "masked_view_consensus_pessimistic_utility",
        "masked_view_consensus_health_score",
    ]
    rows: list[dict[str, Any]] = []
    fractions = [0.02, 0.04, 0.06, 0.08, 0.10, 0.14, 0.18, 0.25]
    for target in TARGETS:
        rows.append(evaluate_policy(modes, target, "masked_view_gain_mean", "hold", 0.0, 0))
        for score_col in score_cols:
            for policy in ["top_all", "top_decisive"]:
                for fraction in fractions:
                    rows.append(evaluate_policy(modes, target, score_col, policy, fraction, null_repeats))
    grid = pd.DataFrame(rows)
    grid["masked_view_policy_score"] = (
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
            hold["accept_reason"] = "no_masked_view_consensus_policy_passed"
            rows.append(hold)
            continue
        row = viable.sort_values(["masked_view_policy_score", "selected_gain_sum"], ascending=False).iloc[0].to_dict()
        row["accepted"] = True
        row["accept_reason"] = "positive_masked_view_consensus_policy"
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
        row["accept_reason"] = "masked_view_consensus_subjectheldout_stable" if stable else "failed_masked_view_consensus_stress"
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


def view_disagreement_summary(scored: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for target, part in scored.groupby("target", observed=True):
        rows.append(
            {
                "target": target,
                "mean_disagreement": float(part["masked_view_disagreement"].mean()),
                "median_disagreement": float(part["masked_view_disagreement"].median()),
                "mean_abs_gain": float(part["effective_gain"].abs().mean()) if "effective_gain" in part else np.nan,
                "toxic_tail_rate": float(part["episode_relative_toxic_tail"].mean()) if "episode_relative_toxic_tail" in part else np.nan,
            }
        )
    return pd.DataFrame(rows).sort_values("target")


def build_markdown(
    summary: dict[str, Any],
    view_metrics: pd.DataFrame,
    disagreement: pd.DataFrame,
    episode_features: pd.DataFrame,
    full_chosen: pd.DataFrame,
    nested_subject_summary: pd.DataFrame,
    nested_target_summary: pd.DataFrame,
    stable: pd.DataFrame,
    policy_board: pd.DataFrame,
) -> str:
    top_policy = policy_board.sort_values(["masked_view_policy_score", "selected_gain_sum"], ascending=False, na_position="last")
    return f"""# Masked-View Consensus Tail Core

## 한 줄 요약

HS-JEPA가 예측한 hidden tail representation이 진짜 구조라면, 일부 context view를 가려도
비슷한 결론을 내야 한다. 그래서 여러 masked view가 동의하는 row-target-action만 release한다.

```text
visible human context views
  -> predict the same hidden episode-conditioned tail representation
  -> penalize view disagreement
  -> row-target action assignment
```

## 빠른 판정: 이것은 HS-JEPA인가?

맞다. 정확히는 **HS-JEPA core target representation의 masked-view invariance를 검사하는 core-decoder boundary 실험**이다.

JEPA성은 다음 질문에서 나온다.

```text
서로 다른 visible context mask들이 같은 hidden action-tail representation을 예측하는가?
```

LeJEPA성은 다음 질문에서 나온다.

```text
좋아 보이는 action score가 특정 view shortcut/collapse가 아니라는 것을
view disagreement penalty로 확인할 수 있는가?
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

## View Metrics

{markdown_table(view_metrics, ["view", "feature_count", "gain_mae", "tail_mae", "positive_auc", "positive_ap", "toxic_auc", "toxic_ap"], max_rows=16)}

## View Disagreement By Target

{markdown_table(disagreement, ["target", "mean_disagreement", "median_disagreement", "mean_abs_gain", "toxic_tail_rate"], max_rows=16)}

## Episode Feature Summary

{markdown_table(episode_features, ["feature", "train_mean", "train_std", "test_mean", "test_std"], max_rows=20)}

## Full OOF Chosen Policies

{markdown_table(full_chosen, ["target", "accepted", "score_col", "policy", "fraction", "selected_cells", "selected_gain_sum", "selected_positive_gain_rate", "positive_subjects", "negative_subjects", "gain_lift_vs_null", "masked_view_policy_score", "accept_reason"], max_rows=20)}

## Nested Subject-Heldout Summary

{markdown_table(nested_subject_summary, ["heldout_subject", "selected_cells", "gain_sum", "mean_gain", "positive_gain_rate", "accepted_targets"], max_rows=20)}

## Nested Target Summary

{markdown_table(nested_target_summary, ["target", "selected_cells", "gain_sum", "mean_gain", "positive_gain_rate", "raw_action_count", "inverse_action_count", "positive_subjects", "negative_subjects"], max_rows=20)}

## Stable Policies Used For Candidate

{markdown_table(stable, ["target", "accepted", "score_col", "policy", "fraction", "heldout_accept_rate", "heldout_gain_sum", "heldout_positive_subjects", "heldout_negative_subjects", "heldout_positive_gain_rate", "accept_reason"], max_rows=20)}

## Policy Board Top Rows

{markdown_table(top_policy, ["target", "score_col", "policy", "fraction", "selected_cells", "selected_gain_sum", "selected_positive_gain_rate", "positive_subjects", "negative_subjects", "gain_lift_vs_null", "gain_z_vs_null", "masked_view_policy_score"], max_rows=32)}

## Anchor-Free Candidate

- candidate: `{summary["candidate_file"]}`
- validation: `{summary["validation"]}`

## 해석

좋은 결과:

```text
masked-view consensus가 nested damage를 줄이면,
HS-JEPA의 hidden action-tail representation은 single-view shortcut보다
view-invariant human-state signal에 가까워진다.
```

나쁜 결과:

```text
consensus가 나빠지면 현재 hidden tail signal은 masked-view invariant하지 않다.
그 경우 HS-JEPA core는 아직 representation 학습이 아니라 adapter-specific sensor에 가깝다.
```
"""


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
    view_feature_sets = build_view_feature_sets(feature_cols)
    train_scored, test_scored, view_metrics = fit_masked_view_consensus(train_modes, test_modes, view_feature_sets)

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
    candidate_name = f"submission_hsjepa_masked_view_consensus_tail_anchor_free_{short_hash(candidate)}_uploadsafe.csv"

    selected_full = full_audit[full_audit["released"]].copy()
    stable_oof_audit = apply_policies(train_scored, stable)
    stable_selected = stable_oof_audit[stable_oof_audit["released"]].copy()
    nested_selected = nested_audit[nested_audit["released"]].copy()
    full_oof_gain = float(selected_full["effective_gain"].sum()) if len(selected_full) else 0.0
    nested_gain = float(nested_selected["effective_gain"].sum()) if len(nested_selected) else 0.0
    stable_oof_gain = float(stable_selected["effective_gain"].sum()) if len(stable_selected) else 0.0
    stable_targets = stable.loc[stable["accepted"].eq(True), "target"].astype(str).tolist() if "accepted" in stable else []
    verdict = (
        "masked_view_consensus_tail_subjectheldout_positive"
        if nested_gain > 0 and stable_count > 0
        else "masked_view_consensus_tail_oof_positive_subjectheldout_fragile"
        if full_oof_gain > 0
        else "masked_view_consensus_tail_negative"
    )

    summary = {
        "package": "masked_view_consensus_tail_core",
        "status": "masked_view_consensus_tail_core_ready",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "view_names": list(view_feature_sets.keys()),
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
    disagreement = view_disagreement_summary(train_scored)
    grid.to_csv(OUT_DIR / "masked_view_consensus_policy_grid.csv", index=False)
    full_chosen.to_csv(OUT_DIR / "masked_view_consensus_full_chosen_policies.csv", index=False)
    full_audit.to_csv(OUT_DIR / "masked_view_consensus_full_oof_action_audit.csv", index=False)
    nested_subject_summary.to_csv(OUT_DIR / "masked_view_consensus_nested_subject_summary.csv", index=False)
    nested_route_rows.to_csv(OUT_DIR / "masked_view_consensus_nested_route_rows.csv", index=False)
    nested_target_summary.to_csv(OUT_DIR / "masked_view_consensus_nested_target_summary.csv", index=False)
    stable.to_csv(OUT_DIR / "masked_view_consensus_stable_policies.csv", index=False)
    view_metrics.to_csv(OUT_DIR / "masked_view_consensus_view_metrics.csv", index=False)
    disagreement.to_csv(OUT_DIR / "masked_view_consensus_disagreement_by_target.csv", index=False)
    efs.to_csv(OUT_DIR / "masked_view_consensus_episode_feature_summary.csv", index=False)
    test_audit.to_csv(OUT_DIR / "masked_view_consensus_test_release_audit.csv", index=False)
    candidate.to_csv(OUT_DIR / candidate_name, index=False)
    candidate.to_csv(ROOT / candidate_name, index=False)
    (OUT_DIR / "masked_view_consensus_tail_core_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    md = build_markdown(
        summary,
        view_metrics,
        disagreement,
        efs,
        full_chosen,
        nested_subject_summary,
        nested_target_summary,
        stable,
        grid,
    )
    (OUT_DIR / "MASKED_VIEW_CONSENSUS_TAIL_CORE_KO.md").write_text(md, encoding="utf-8")
    PAPER_DOC.write_text(md, encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


if __name__ == "__main__":
    run()
