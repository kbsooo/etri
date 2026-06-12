#!/usr/bin/env python3
"""Subject-normalized tail field core for HS-JEPA.

Tail-safe expected utility exposed a sharp failure mode:

    full OOF utility is positive, but subject-heldout S-target tails are toxic.

This experiment changes the target representation rather than the top-k policy.
Instead of predicting absolute realized gain, it predicts a within-subject
tail-normalized gain field:

    action gain relative to this subject/target/action route's own tail scale

The question is whether HS-JEPA residual/energy geometry carries a more
subject-invariant notion of "bad-for-this-human-state" than absolute Log Loss
gain.  No public LB ledger, prior submission probabilities, or proprietary
embedding APIs are used.
"""

from __future__ import annotations

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


OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "subject_normalized_tail_field_core"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "SUBJECT_NORMALIZED_TAIL_FIELD_CORE_KO.md"
RANDOM_SEED = 20260613
NULL_REPEATS = min(16, TAIL_SAFE_NULL_REPEATS)
TAIL_Z_THRESHOLD = -1.0


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


def add_normalized_targets(train_modes: pd.DataFrame) -> pd.DataFrame:
    out = train_modes.copy()
    group_cols = ["subject_id", "target", "decoder_action"]
    grouped = out.groupby(group_cols, observed=True)["effective_gain"]
    center = grouped.transform("median")
    q25 = grouped.transform(lambda x: float(np.quantile(x, 0.25)))
    q75 = grouped.transform(lambda x: float(np.quantile(x, 0.75)))
    scale = (q75 - q25) / 1.349
    fallback_scale = out.groupby(["target", "decoder_action"], observed=True)["effective_gain"].transform(
        lambda x: max(float(np.std(x, ddof=0)), 0.02)
    )
    scale = scale.where(scale.abs().gt(1e-6), fallback_scale).clip(lower=0.02)
    out["subject_tail_center"] = center.astype(float)
    out["subject_tail_scale"] = scale.astype(float)
    out["subject_normalized_gain"] = (out["effective_gain"].astype(float) - out["subject_tail_center"]) / out[
        "subject_tail_scale"
    ]
    out["subject_relative_tail_loss"] = np.maximum(-out["subject_normalized_gain"], 0.0)
    out["subject_relative_toxic_tail"] = out["subject_normalized_gain"].lt(TAIL_Z_THRESHOLD).astype(int)
    out["subject_relative_positive"] = out["subject_normalized_gain"].gt(0.0).astype(int)
    return out


def stable_seed(*parts: object) -> int:
    key = "::".join(map(str, parts))
    return RANDOM_SEED + abs(hash(key)) % 1009


def fit_subject_normalized_models(
    train_modes: pd.DataFrame,
    test_modes: pd.DataFrame,
    feature_cols: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    subjects = sorted(train_modes["subject_id"].astype(str).unique())
    y_norm = train_modes["subject_normalized_gain"].astype(float).to_numpy()
    y_tail = train_modes["subject_relative_tail_loss"].astype(float).to_numpy()
    y_rel_pos = train_modes["subject_relative_positive"].astype(int).to_numpy()
    y_rel_toxic = train_modes["subject_relative_toxic_tail"].astype(int).to_numpy()
    weights = 1.0 + np.minimum(np.abs(y_norm), 6.0)

    oof_norm = np.zeros(len(train_modes), dtype=np.float64)
    oof_tail = np.zeros(len(train_modes), dtype=np.float64)
    oof_pos = np.zeros(len(train_modes), dtype=np.float64)
    oof_toxic = np.zeros(len(train_modes), dtype=np.float64)

    for subject in subjects:
        tr = train_modes.index[~train_modes["subject_id"].astype(str).eq(subject)].to_numpy()
        va = train_modes.index[train_modes["subject_id"].astype(str).eq(subject)].to_numpy()
        norm_model = regressor_factory(stable_seed("subject-normalized-gain", subject))
        tail_model = regressor_factory(stable_seed("subject-normalized-tail", subject))
        norm_model.fit(train_modes.iloc[tr][feature_cols], y_norm[tr], histgradientboostingregressor__sample_weight=weights[tr])
        tail_model.fit(train_modes.iloc[tr][feature_cols], y_tail[tr], histgradientboostingregressor__sample_weight=weights[tr])
        oof_norm[va] = norm_model.predict(train_modes.iloc[va][feature_cols])
        oof_tail[va] = np.maximum(tail_model.predict(train_modes.iloc[va][feature_cols]), 0.0)

        if len(np.unique(y_rel_pos[tr])) < 2:
            oof_pos[va] = float(y_rel_pos[tr].mean())
        else:
            pos_model = classifier_factory(stable_seed("subject-normalized-positive", subject))
            pos_model.fit(train_modes.iloc[tr][feature_cols], y_rel_pos[tr], histgradientboostingclassifier__sample_weight=weights[tr])
            oof_pos[va] = pos_model.predict_proba(train_modes.iloc[va][feature_cols])[:, 1]

        if len(np.unique(y_rel_toxic[tr])) < 2:
            oof_toxic[va] = float(y_rel_toxic[tr].mean())
        else:
            toxic_model = classifier_factory(stable_seed("subject-normalized-toxic", subject))
            toxic_model.fit(train_modes.iloc[tr][feature_cols], y_rel_toxic[tr], histgradientboostingclassifier__sample_weight=weights[tr])
            oof_toxic[va] = toxic_model.predict_proba(train_modes.iloc[va][feature_cols])[:, 1]

    norm_model = regressor_factory(stable_seed("subject-normalized-gain", "full-test"))
    tail_model = regressor_factory(stable_seed("subject-normalized-tail", "full-test"))
    norm_model.fit(train_modes[feature_cols], y_norm, histgradientboostingregressor__sample_weight=weights)
    tail_model.fit(train_modes[feature_cols], y_tail, histgradientboostingregressor__sample_weight=weights)
    test_norm = norm_model.predict(test_modes[feature_cols])
    test_tail = np.maximum(tail_model.predict(test_modes[feature_cols]), 0.0)

    if len(np.unique(y_rel_pos)) < 2:
        test_pos = np.full(len(test_modes), float(y_rel_pos.mean()), dtype=np.float64)
    else:
        pos_model = classifier_factory(stable_seed("subject-normalized-positive", "full-test"))
        pos_model.fit(train_modes[feature_cols], y_rel_pos, histgradientboostingclassifier__sample_weight=weights)
        test_pos = pos_model.predict_proba(test_modes[feature_cols])[:, 1]

    if len(np.unique(y_rel_toxic)) < 2:
        test_toxic = np.full(len(test_modes), float(y_rel_toxic.mean()), dtype=np.float64)
    else:
        toxic_model = classifier_factory(stable_seed("subject-normalized-toxic", "full-test"))
        toxic_model.fit(train_modes[feature_cols], y_rel_toxic, histgradientboostingclassifier__sample_weight=weights)
        test_toxic = toxic_model.predict_proba(test_modes[feature_cols])[:, 1]

    train_scored = train_modes.copy()
    test_scored = test_modes.copy()
    for frame, pred_norm, pred_tail, pred_pos, pred_toxic in [
        (train_scored, oof_norm, oof_tail, oof_pos, oof_toxic),
        (test_scored, test_norm, test_tail, test_pos, test_toxic),
    ]:
        frame["predicted_subject_normalized_gain"] = pred_norm
        frame["predicted_subject_relative_tail_loss"] = pred_tail
        frame["predicted_subject_relative_positive_prob"] = pred_pos
        frame["predicted_subject_relative_toxic_prob"] = pred_toxic
        frame["subject_normalized_utility"] = pred_norm - 0.95 * pred_tail - 0.30 * pred_toxic
        frame["subject_normalized_pessimistic_utility"] = pred_norm - 1.60 * pred_tail - 0.55 * pred_toxic
        frame["subject_relative_health_score"] = pred_pos - pred_toxic

    metric_rows = [
        {"metric": "normalized_gain_mae", "value": float(mean_absolute_error(y_norm, oof_norm))},
        {"metric": "relative_tail_loss_mae", "value": float(mean_absolute_error(y_tail, oof_tail))},
        {"metric": "relative_positive_auc", "value": safe_auc(y_rel_pos, oof_pos)},
        {"metric": "relative_positive_ap", "value": safe_ap(y_rel_pos, oof_pos)},
        {"metric": "relative_toxic_tail_auc", "value": safe_auc(y_rel_toxic, oof_toxic)},
        {"metric": "relative_toxic_tail_ap", "value": safe_ap(y_rel_toxic, oof_toxic)},
        {"metric": "relative_toxic_tail_rate", "value": float(y_rel_toxic.mean())},
        {"metric": "absolute_gain_sum_all_modes", "value": float(train_modes["effective_gain"].sum())},
    ]
    return train_scored, test_scored, pd.DataFrame(metric_rows)


def policy_grid(modes: pd.DataFrame, null_repeats: int) -> pd.DataFrame:
    score_cols = [
        "predicted_subject_normalized_gain",
        "subject_normalized_utility",
        "subject_normalized_pessimistic_utility",
        "subject_relative_health_score",
    ]
    fractions = [0.02, 0.04, 0.06, 0.08, 0.10, 0.14, 0.18, 0.25]
    rows: list[dict[str, Any]] = []
    for target in TARGETS:
        rows.append(evaluate_policy(modes, target, "predicted_subject_normalized_gain", "hold", 0.0, 0))
        for score_col in score_cols:
            for policy in ["top_all", "top_decisive"]:
                for fraction in fractions:
                    rows.append(evaluate_policy(modes, target, score_col, policy, fraction, null_repeats))
    grid = pd.DataFrame(rows)
    grid["subject_normalized_policy_score"] = (
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
            hold["accept_reason"] = "no_subject_normalized_policy_passed"
            rows.append(hold)
            continue
        row = viable.sort_values(["subject_normalized_policy_score", "selected_gain_sum"], ascending=False).iloc[0].to_dict()
        row["accepted"] = True
        row["accept_reason"] = "positive_subject_normalized_tail_policy"
        rows.append(row)
    return pd.DataFrame(rows).sort_values("target")


def apply_policies(modes: pd.DataFrame, chosen: pd.DataFrame) -> pd.DataFrame:
    released = pd.Series(False, index=modes.index)
    for _, row in chosen.iterrows():
        if not bool(row["accepted"]):
            continue
        from hsjepa_core.run_tail_safe_expected_utility_core import choose_mode_indices  # local import avoids exporting policy.

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
        row["accept_reason"] = "subject_normalized_tail_subjectheldout_stable" if stable else "failed_subject_normalized_tail_stress"
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
    from hsjepa_core.run_tail_safe_expected_utility_core import choose_mode_indices

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
) -> str:
    top_policy = policy_board.sort_values(["subject_normalized_policy_score", "selected_gain_sum"], ascending=False, na_position="last")
    return f"""# Subject-Normalized Tail Field Core

## 한 줄 요약

absolute action gain을 바로 예측하지 않고, subject-target-action route 내부의 tail scale로 정규화한
`이 사람 기준으로 나쁜 action인가`를 예측했다.

## 빠른 판정: 이것은 HS-JEPA인가?

부분적으로 맞다. 정확히는 **HS-JEPA core representation을 subject-invariant tail representation으로 재정의하는 core-decoder boundary 실험**이다.

```text
visible human context
  -> hidden action-health / residual-energy representation
  -> subject-normalized tail field
  -> row-target action assignment
```

## 왜 필요한가

Tail-Safe Expected Utility Core는 full OOF utility를 크게 올렸지만,
subject-heldout에서는 S-target tail이 무너지며 negative였다.

이 실험의 가설:

```text
absolute gain은 subject별 tail scale을 섞어 놓기 때문에 subject shift에서 깨진다.
HS-JEPA가 읽어야 할 target representation은 absolute gain이 아니라
subject-normalized badness / relative tail field다.
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

## Relative Tail Model Metrics

{markdown_table(metrics, ["metric", "value"], max_rows=20)}

## Full OOF Chosen Policies

{markdown_table(full_chosen, ["target", "accepted", "score_col", "policy", "fraction", "selected_cells", "selected_gain_sum", "selected_positive_gain_rate", "positive_subjects", "negative_subjects", "gain_lift_vs_null", "subject_normalized_policy_score", "accept_reason"], max_rows=20)}

## Nested Subject-Heldout Summary

{markdown_table(nested_subject_summary, ["heldout_subject", "selected_cells", "gain_sum", "mean_gain", "positive_gain_rate", "accepted_targets"], max_rows=20)}

## Nested Target Summary

{markdown_table(nested_target_summary, ["target", "selected_cells", "gain_sum", "mean_gain", "positive_gain_rate", "raw_action_count", "inverse_action_count", "positive_subjects", "negative_subjects"], max_rows=20)}

## Stable Policies Used For Candidate

{markdown_table(stable, ["target", "accepted", "score_col", "policy", "fraction", "heldout_accept_rate", "heldout_gain_sum", "heldout_positive_subjects", "heldout_negative_subjects", "heldout_positive_gain_rate", "accept_reason"], max_rows=20)}

## Policy Board Top Rows

{markdown_table(top_policy, ["target", "score_col", "policy", "fraction", "selected_cells", "selected_gain_sum", "selected_positive_gain_rate", "positive_subjects", "negative_subjects", "gain_lift_vs_null", "gain_z_vs_null", "subject_normalized_policy_score"], max_rows=32)}

## Anchor-Free Candidate

- candidate: `{summary["candidate_file"]}`
- validation: `{summary["validation"]}`

## 해석

좋은 결과:

```text
subject-normalized tail field가 nested heldout damage를 줄이면,
HS-JEPA의 핵심 target representation은 absolute action utility가 아니라
human-specific relative badness라는 주장이 강해진다.
```

나쁜 결과:

```text
정규화해도 heldout tail이 무너지면,
현재 residual/energy core는 subject-relative tail magnitude를 충분히 표현하지 못한다.
그 경우 다음 문제는 feature 추가가 아니라 sequence/episode-level state target을 다시 정의하는 것이다.
```
"""


def run() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    train_cells, test_cells, train_priors, _view_metrics = build_listener_cells()
    train_cells, test_cells, _contrastive_metrics, _contrastive_summary = add_subject_contrastive_scores(train_cells, test_cells)
    train_modes, test_modes = build_mode_tables(train_cells, test_cells)
    train_modes = add_normalized_targets(train_modes)
    feature_cols = utility_feature_columns(train_modes, test_modes)
    train_scored, test_scored, metrics = fit_subject_normalized_models(train_modes, test_modes, feature_cols)

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
    candidate_name = f"submission_hsjepa_subject_normalized_tail_field_anchor_free_{short_hash(candidate)}_uploadsafe.csv"

    selected_full = full_audit[full_audit["released"]].copy()
    stable_oof_audit = apply_policies(train_scored, stable)
    stable_selected = stable_oof_audit[stable_oof_audit["released"]].copy()
    nested_selected = nested_audit[nested_audit["released"]].copy()
    full_oof_gain = float(selected_full["effective_gain"].sum()) if len(selected_full) else 0.0
    nested_gain = float(nested_selected["effective_gain"].sum()) if len(nested_selected) else 0.0
    stable_oof_gain = float(stable_selected["effective_gain"].sum()) if len(stable_selected) else 0.0
    stable_targets = stable.loc[stable["accepted"].eq(True), "target"].astype(str).tolist() if "accepted" in stable else []
    verdict = (
        "subject_normalized_tail_field_subjectheldout_positive"
        if nested_gain > 0 and stable_count > 0
        else "subject_normalized_tail_field_oof_positive_subjectheldout_fragile"
        if full_oof_gain > 0
        else "subject_normalized_tail_field_negative"
    )

    summary = {
        "package": "subject_normalized_tail_field_core",
        "status": "subject_normalized_tail_field_core_ready",
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

    grid.to_csv(OUT_DIR / "subject_normalized_policy_grid.csv", index=False)
    full_chosen.to_csv(OUT_DIR / "subject_normalized_full_chosen_policies.csv", index=False)
    full_audit.to_csv(OUT_DIR / "subject_normalized_full_oof_action_audit.csv", index=False)
    nested_subject_summary.to_csv(OUT_DIR / "subject_normalized_nested_subject_summary.csv", index=False)
    nested_route_rows.to_csv(OUT_DIR / "subject_normalized_nested_route_rows.csv", index=False)
    nested_target_summary.to_csv(OUT_DIR / "subject_normalized_nested_target_summary.csv", index=False)
    stable.to_csv(OUT_DIR / "subject_normalized_stable_policies.csv", index=False)
    metrics.to_csv(OUT_DIR / "subject_normalized_tail_model_metrics.csv", index=False)
    test_audit.to_csv(OUT_DIR / "subject_normalized_test_release_audit.csv", index=False)
    candidate.to_csv(OUT_DIR / candidate_name, index=False)
    candidate.to_csv(ROOT / candidate_name, index=False)
    (OUT_DIR / "subject_normalized_tail_field_core_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    md = build_markdown(summary, metrics, full_chosen, nested_subject_summary, nested_target_summary, stable, grid)
    (OUT_DIR / "SUBJECT_NORMALIZED_TAIL_FIELD_CORE_KO.md").write_text(md, encoding="utf-8")
    PAPER_DOC.write_text(md, encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


if __name__ == "__main__":
    run()
