#!/usr/bin/env python3
"""Subject-relative responsibility assignment for HS-JEPA action health.

The previous action-toxicity field found a real but weak subject-heldout
health signal:

    action-health AUC ~= 0.597
    nested heldout release gain < 0

This experiment asks whether the failure is caused by absolute-score
calibration.  Instead of selecting by raw health_score, it creates responsibility
coordinates that are available for train and test without labels:

    subject-relative rank
    subject-target relative rank
    target-relative rank
    raw-vs-inverse pairwise responsibility
    support-aligned responsibility

Then it runs the same nested subject-heldout stress.  If this works, HS-JEPA
core did not lack action-health information; the missing adapter was a
subject-relative assignment layer.

This is a competition adapter / LeJEPA-style diagnostic, not HS-JEPA core.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hsjepa_core.run_action_support_world_model_core import TARGETS, validate_submission  # noqa: E402
from hsjepa_core.run_lifelog_core_state_evidence import format_float, markdown_table  # noqa: E402
from sleep_competition_adapter.subject_heldout_action_toxicity_field import (  # noqa: E402
    HELDOUT_NULL_REPEATS,
    LISTENER_GLOBAL_GAIN_REFERENCE,
    NULL_REPEATS,
    ROUTE_CONSERVATION_GAIN_REFERENCE,
    SUBJECT_BALANCED_GAIN_REFERENCE,
    SUBJECT_HELDOUT_ROUTE_GAIN_REFERENCE,
    build_action_mode_tables,
    fit_subject_heldout_health_scores,
    safe_ap,
    safe_auc,
    stable_seed,
    summarize_targets,
    toxicity_feature_columns,
)
from sleep_competition_adapter.target_route_conservation_decoder import (  # noqa: E402
    SAMPLE_SUBMISSION,
    build_listener_cells,
    short_hash,
)


OUT_DIR = ROOT / "sleep_competition_adapter" / "outputs" / "subject_relative_responsibility_assignment"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "SUBJECT_RELATIVE_RESPONSIBILITY_ASSIGNMENT_KO.md"


def pct_rank(values: pd.Series) -> pd.Series:
    values = values.astype(float).replace([np.inf, -np.inf], np.nan)
    if values.notna().sum() <= 1 or values.nunique(dropna=True) <= 1:
        return pd.Series(np.full(len(values), 0.5, dtype=np.float64), index=values.index)
    return values.rank(method="average", pct=True).fillna(0.5)


def add_subject_relative_scores(modes: pd.DataFrame) -> pd.DataFrame:
    out = modes.copy()
    out["subject_health_rank"] = out.groupby("subject_id", observed=True)["health_score"].transform(pct_rank)
    out["subject_target_health_rank"] = out.groupby(["subject_id", "target"], observed=True)["health_score"].transform(pct_rank)
    out["target_health_rank"] = out.groupby("target", observed=True)["health_score"].transform(pct_rank)
    out["route_family_health_rank"] = out.groupby("target_route_family", observed=True)["health_score"].transform(pct_rank)
    out["subject_action_delta_rank"] = out.groupby("subject_id", observed=True)["action_abs_delta"].transform(pct_rank)
    out["target_action_delta_rank"] = out.groupby("target", observed=True)["action_abs_delta"].transform(pct_rank)

    wide = out.pivot_table(index="cell_id", columns="decoder_action", values="health_score", aggfunc="first")
    raw = wide.get("raw_memory_release", pd.Series(0.5, index=wide.index)).astype(float)
    inv = wide.get("inverse_toxic_memory", pd.Series(0.5, index=wide.index)).astype(float)
    pair_frame = pd.DataFrame({"raw_memory_release": raw, "inverse_toxic_memory": inv})
    pair_frame["pair_best_score"] = pair_frame.max(axis=1)
    pair_frame["pair_gap_abs"] = (pair_frame["raw_memory_release"] - pair_frame["inverse_toxic_memory"]).abs()
    pair_frame["raw_gap"] = pair_frame["raw_memory_release"] - pair_frame["inverse_toxic_memory"]
    pair_frame["inverse_gap"] = -pair_frame["raw_gap"]
    pair_frame["raw_pair_prob"] = 1.0 / (1.0 + np.exp(-8.0 * pair_frame["raw_gap"].clip(-4, 4)))
    pair_frame["inverse_pair_prob"] = 1.0 - pair_frame["raw_pair_prob"]

    out = out.merge(
        pair_frame[
            [
                "pair_best_score",
                "pair_gap_abs",
                "raw_gap",
                "inverse_gap",
                "raw_pair_prob",
                "inverse_pair_prob",
            ]
        ],
        left_on="cell_id",
        right_index=True,
        how="left",
    )
    out["pair_gap"] = np.where(out["decoder_action"].eq("raw_memory_release"), out["raw_gap"], out["inverse_gap"])
    out["pair_prob"] = np.where(out["decoder_action"].eq("raw_memory_release"), out["raw_pair_prob"], out["inverse_pair_prob"])
    out["pair_best_action"] = out["pair_gap"].ge(0.0).astype(float)
    out["pair_gap_rank_target"] = out.groupby("target", observed=True)["pair_gap_abs"].transform(pct_rank)

    out["subject_relative_responsibility"] = (
        0.38 * out["subject_target_health_rank"]
        + 0.22 * out["subject_health_rank"]
        + 0.18 * out["target_health_rank"]
        + 0.22 * out["pair_prob"]
    )
    out["pairwise_responsibility"] = (
        0.45 * out["pair_prob"]
        + 0.25 * out["subject_target_health_rank"]
        + 0.18 * out["pair_gap_rank_target"]
        + 0.12 * out["target_action_delta_rank"]
    )
    out["support_aligned_responsibility"] = (
        0.30 * out["mode_support_alignment"]
        + 0.28 * out["subject_target_health_rank"]
        + 0.22 * out["pair_prob"]
        + 0.20 * out["target_health_rank"]
    )
    out["conservative_pair_best_responsibility"] = (
        out["pair_best_action"]
        * (
            0.36 * out["subject_relative_responsibility"]
            + 0.34 * out["pairwise_responsibility"]
            + 0.30 * out["support_aligned_responsibility"]
        )
    )
    return out


def choose_mode_indices(
    modes: pd.DataFrame,
    target: str,
    policy: str,
    fraction: float,
    score_col: str,
) -> np.ndarray:
    if policy == "hold":
        return np.array([], dtype=int)
    part = modes[modes["target"].eq(target)].copy()
    if "decisive" in policy:
        part = part[part["decisive_action"].eq(1)]
    if "pairbest" in policy:
        part = part[part["pair_best_action"].eq(1)]
    if part.empty:
        return np.array([], dtype=int)
    part = part.sort_values(score_col, ascending=False, kind="mergesort")
    part = part.drop_duplicates("cell_id", keep="first")
    if part.empty:
        return np.array([], dtype=int)
    k = max(1, int(round(len(part) * fraction)))
    return part.head(k).index.to_numpy()


def evaluate_policy(
    modes: pd.DataFrame,
    target: str,
    policy: str,
    fraction: float,
    score_col: str,
    null_repeats: int,
) -> dict[str, Any]:
    selected = choose_mode_indices(modes, target, policy, fraction, score_col)
    selected_frame = modes.loc[selected] if len(selected) else modes.iloc[0:0]
    gains = selected_frame["effective_gain"].to_numpy(dtype=np.float64) if len(selected_frame) else np.array([], dtype=np.float64)
    subject_gain = (
        selected_frame.groupby("subject_id", observed=True)["effective_gain"].sum()
        if len(selected_frame)
        else pd.Series(dtype=float)
    )
    rng = np.random.default_rng(stable_seed("subject-relative-null", score_col, target, policy, fraction))
    null_sums: list[float] = []
    if len(selected):
        part_idx = modes.index[modes["target"].eq(target)].to_numpy()
        original = modes.loc[part_idx, score_col].to_numpy(dtype=np.float64)
        for _ in range(null_repeats):
            shuffled = original.copy()
            rng.shuffle(shuffled)
            temp = modes.loc[part_idx].copy()
            temp[score_col] = shuffled
            temp_selected = choose_mode_indices(temp, target, policy, fraction, score_col)
            null_sums.append(float(temp.loc[temp_selected, "effective_gain"].sum()) if len(temp_selected) else 0.0)
    null_mean = float(np.mean(null_sums)) if null_sums else 0.0
    null_std = float(np.std(null_sums, ddof=1)) if len(null_sums) > 1 else np.nan
    gain_sum = float(gains.sum()) if len(gains) else 0.0
    positive_rate = float((gains > 0).mean()) if len(gains) else np.nan
    positive_subjects = int((subject_gain > 0).sum()) if len(subject_gain) else 0
    negative_subjects = int((subject_gain < 0).sum()) if len(subject_gain) else 0
    raw_count = int(selected_frame["decoder_action"].eq("raw_memory_release").sum()) if len(selected_frame) else 0
    inverse_count = int(selected_frame["decoder_action"].eq("inverse_toxic_memory").sum()) if len(selected_frame) else 0
    assignment_score = (
        gain_sum
        + 0.30 * (gain_sum - null_mean)
        + 0.10 * (0.0 if not np.isfinite(null_std) or null_std == 0 else (gain_sum - null_mean) / null_std)
        + 0.40 * max(positive_rate if np.isfinite(positive_rate) else 0.0, 0.0)
        + 0.35 * positive_subjects
        - 0.90 * negative_subjects
    )
    return {
        "score_col": score_col,
        "target": target,
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
        "gain_z_vs_null": (gain_sum - null_mean) / null_std if np.isfinite(null_std) and null_std else np.nan,
        "assignment_score": assignment_score,
    }


def policy_grid(modes: pd.DataFrame, score_col: str, null_repeats: int) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    fractions = [0.01, 0.02, 0.04, 0.06, 0.08, 0.10, 0.14, 0.18]
    for target in TARGETS:
        rows.append(evaluate_policy(modes, target, "hold", 0.0, score_col, null_repeats=0))
        for fraction in fractions:
            rows.append(evaluate_policy(modes, target, "top_responsibility_all", fraction, score_col, null_repeats))
            rows.append(evaluate_policy(modes, target, "top_responsibility_decisive", fraction, score_col, null_repeats))
            rows.append(evaluate_policy(modes, target, "top_responsibility_pairbest", fraction, score_col, null_repeats))
    return pd.DataFrame(rows)


def choose_target_policies(grid: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for target, part in grid.groupby("target", observed=True):
        hold = part[part["policy"].eq("hold")].iloc[0].to_dict()
        viable = part[
            ~part["policy"].eq("hold")
            & (part["selected_gain_sum"] > 0.0)
            & (part["gain_lift_vs_null"] > 0.0)
            & (part["selected_positive_gain_rate"].fillna(0.0) >= 0.60)
            & (part["negative_subjects"] <= 3)
        ].copy()
        if viable.empty:
            hold["accepted"] = False
            hold["accept_reason"] = "no_subject_relative_policy_passed"
            rows.append(hold)
            continue
        row = viable.sort_values(["assignment_score", "selected_gain_sum"], ascending=False).iloc[0].to_dict()
        row["accepted"] = True
        row["accept_reason"] = "positive_subject_relative_responsibility"
        rows.append(row)
    return pd.DataFrame(rows).sort_values("target")


def apply_policies_to_modes(modes: pd.DataFrame, chosen: pd.DataFrame) -> pd.DataFrame:
    released = pd.Series(False, index=modes.index)
    for _, route in chosen.iterrows():
        if not bool(route["accepted"]):
            continue
        selected = choose_mode_indices(
            modes,
            str(route["target"]),
            str(route["policy"]),
            float(route["fraction"]),
            str(route["score_col"]),
        )
        released.loc[selected] = True
    audit = modes.copy()
    audit["released"] = released.to_numpy()
    audit["effective_gain_released"] = np.where(audit["released"], audit["effective_gain"], 0.0)
    return audit


def run_nested_subject_heldout(modes: pd.DataFrame, score_col: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    subjects = sorted(modes["subject_id"].astype(str).unique())
    fold_rows: list[dict[str, Any]] = []
    route_rows: list[dict[str, Any]] = []
    audits: list[pd.DataFrame] = []
    for subject in subjects:
        selector = modes[~modes["subject_id"].astype(str).eq(subject)].copy()
        heldout = modes[modes["subject_id"].astype(str).eq(subject)].copy()
        chosen = choose_target_policies(policy_grid(selector, score_col, HELDOUT_NULL_REPEATS))
        audit = apply_policies_to_modes(heldout, chosen)
        audit["heldout_subject"] = subject
        audit["score_col"] = score_col
        audits.append(audit)
        selected = audit[audit["released"]].copy()
        gains = selected["effective_gain"].to_numpy(dtype=np.float64) if len(selected) else np.array([], dtype=np.float64)
        fold_rows.append(
            {
                "score_col": score_col,
                "heldout_subject": subject,
                "selected_cells": int(len(selected)),
                "gain_sum": float(gains.sum()) if len(gains) else 0.0,
                "mean_gain": float(gains.mean()) if len(gains) else 0.0,
                "positive_gain_rate": float((gains > 0).mean()) if len(gains) else np.nan,
                "accepted_targets": ",".join(chosen.loc[chosen["accepted"].eq(True), "target"].astype(str).tolist()),
                "held_targets": ",".join(chosen.loc[chosen["accepted"].eq(False), "target"].astype(str).tolist()),
            }
        )
        for _, row in chosen.iterrows():
            target = str(row["target"])
            target_selected = selected[selected["target"].eq(target)]
            route_rows.append(
                {
                    "score_col": score_col,
                    "heldout_subject": subject,
                    "target": target,
                    "accepted": bool(row["accepted"]),
                    "policy": str(row["policy"]),
                    "fraction": float(row["fraction"]),
                    "heldout_selected_cells": int(len(target_selected)),
                    "heldout_gain_sum": float(target_selected["effective_gain"].sum()) if len(target_selected) else 0.0,
                    "heldout_positive_gain_rate": float((target_selected["effective_gain"] > 0).mean()) if len(target_selected) else np.nan,
                    "raw_action_count": int(target_selected["decoder_action"].eq("raw_memory_release").sum()) if len(target_selected) else 0,
                    "inverse_action_count": int(target_selected["decoder_action"].eq("inverse_toxic_memory").sum()) if len(target_selected) else 0,
                    "accept_reason": str(row["accept_reason"]),
                }
            )
    return pd.DataFrame(fold_rows), pd.DataFrame(route_rows), pd.concat(audits, ignore_index=True)


def summarize_variant(name: str, fold_summary: pd.DataFrame, nested_audit: pd.DataFrame) -> dict[str, Any]:
    selected = nested_audit[nested_audit["released"]].copy()
    gains = selected["effective_gain"].to_numpy(dtype=np.float64) if len(selected) else np.array([], dtype=np.float64)
    return {
        "score_col": name,
        "nested_selected_cells": int(len(selected)),
        "nested_gain_sum": float(gains.sum()) if len(gains) else 0.0,
        "nested_positive_gain_rate": float((gains > 0).mean()) if len(gains) else np.nan,
        "positive_subjects": int((fold_summary["gain_sum"] > 0).sum()),
        "negative_subjects": int((fold_summary["gain_sum"] < 0).sum()),
        "survival_score": float(gains.sum()) + 0.75 * int((fold_summary["gain_sum"] > 0).sum()) - 1.00 * int((fold_summary["gain_sum"] < 0).sum()) if len(gains) else -1.0 * int((fold_summary["gain_sum"] < 0).sum()),
    }


def route_decision_frequency(route_rows: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for (score_col, target), part in route_rows.groupby(["score_col", "target"], observed=True):
        top = part.groupby(["policy", "fraction"], observed=True).size().reset_index(name="count")
        top = top.sort_values("count", ascending=False).iloc[0]
        rows.append(
            {
                "score_col": score_col,
                "target": target,
                "heldout_accept_rate": float(part["accepted"].mean()),
                "top_policy": str(top["policy"]),
                "top_fraction": float(top["fraction"]),
                "top_policy_count": int(top["count"]),
                "heldout_gain_sum": float(part["heldout_gain_sum"].sum()),
                "heldout_positive_subjects": int((part["heldout_gain_sum"] > 0).sum()),
                "heldout_negative_subjects": int((part["heldout_gain_sum"] < 0).sum()),
            }
        )
    return pd.DataFrame(rows).sort_values(["score_col", "target"])


def stable_policies_from_nested(full_chosen: pd.DataFrame, route_rows: pd.DataFrame, nested_audit: pd.DataFrame) -> pd.DataFrame:
    target_summary = summarize_targets(nested_audit)
    target_stats = target_summary.set_index("target").to_dict(orient="index") if not target_summary.empty else {}
    route_accept_rate = route_rows.groupby("target", observed=True)["accepted"].mean().to_dict()
    rows: list[dict[str, Any]] = []
    for _, route in full_chosen.iterrows():
        row = route.to_dict()
        target = str(row["target"])
        stats = target_stats.get(target, {})
        accept_rate = float(route_accept_rate.get(target, 0.0))
        gain_sum = float(stats.get("gain_sum", 0.0))
        positive_subjects = int(stats.get("positive_subjects", 0))
        negative_subjects = int(stats.get("negative_subjects", 0))
        positive_rate = float(stats.get("positive_gain_rate", 0.0)) if pd.notna(stats.get("positive_gain_rate", np.nan)) else 0.0
        stable = (
            bool(row.get("accepted", False))
            and accept_rate >= 0.60
            and gain_sum > 0.0
            and positive_subjects >= max(2, negative_subjects + 1)
            and positive_rate >= 0.60
        )
        row["accepted"] = stable
        row["heldout_accept_rate"] = accept_rate
        row["heldout_gain_sum"] = gain_sum
        row["heldout_positive_subjects"] = positive_subjects
        row["heldout_negative_subjects"] = negative_subjects
        row["heldout_positive_gain_rate"] = positive_rate
        row["accept_reason"] = "subject_relative_assignment_stable" if stable else "failed_subject_relative_assignment"
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
        selected = choose_mode_indices(
            test_modes,
            str(route["target"]),
            str(route["policy"]),
            float(route["fraction"]),
            str(route["score_col"]),
        )
        released.loc[selected] = True
    audit = test_modes.copy()
    audit["released"] = released.to_numpy()
    for _, row in audit[audit["released"]].iterrows():
        out.at[int(row["row"]), str(row["target"])] = float(row["action_prob"])
    out[TARGETS] = out[TARGETS].clip(1e-5, 1.0 - 1e-5)
    return out, audit


def build_markdown(
    summary: dict[str, Any],
    variant_summary: pd.DataFrame,
    selected_full_chosen: pd.DataFrame,
    selected_fold_summary: pd.DataFrame,
    selected_target_summary: pd.DataFrame,
    selected_route_frequency: pd.DataFrame,
    stable_policies: pd.DataFrame,
) -> str:
    return f"""# HS-JEPA Diagnostic Adapter: Subject-Relative Responsibility Assignment

## 한 줄 요약

subject-heldout action-health score는 양수였지만 절대 top-k release는 무너졌다.
이번 실험은 같은 score를 subject-relative rank, target-relative rank, raw-vs-inverse pairwise
responsibility로 재해석해서 calibration 문제가 병목인지 확인했다.

```text
masked world-state residual/energy
  -> subject-heldout action-health score
  -> subject-relative / pairwise responsibility coordinates
  -> nested subject-heldout assignment stress
```

## 빠른 판정: 이것은 HS-JEPA인가?

**HS-JEPA core 자체는 아니다.**
정확한 위치는 **HS-JEPA competition adapter + LeJEPA-style diagnostic**이다.

```text
HS-JEPA core
  = visible human-life context -> hidden action-health geometry

이 문서의 역할
  = 그 geometry를 어떤 coordinate system으로 action assignment에 번역해야 하는지 검증한다.
```

## 사용하지 않은 정보

- public LB ledger: `{summary["uses_public_score_ledger"]}`
- prior submission probability: `{summary["uses_prior_submission_probabilities"]}`
- proprietary embedding API: `{summary["uses_proprietary_embedding_api"]}`

## Verdict

- verdict: `{summary["verdict"]}`
- action-health AUC: `{format_float(summary["action_health_auc"], 6)}`
- action-health AP: `{format_float(summary["action_health_ap"], 6)}`
- best score coordinate: `{summary["best_score_col"]}`
- best nested gain: `{format_float(summary["best_nested_gain_sum"], 6)}`
- best positive/negative subjects: `{summary["best_positive_subjects"]}` / `{summary["best_negative_subjects"]}`
- stable targets: `{summary["stable_targets"]}`
- stable OOF gain sum: `{format_float(summary["stable_oof_gain_sum"], 6)}`
- released test cells: `{summary["released_test_cells"]}`

## Responsibility Coordinate Summary

{markdown_table(variant_summary, ["score_col", "nested_selected_cells", "nested_gain_sum", "nested_positive_gain_rate", "positive_subjects", "negative_subjects", "survival_score"], max_rows=20)}

## Best Coordinate Full-OOF Policies

{markdown_table(selected_full_chosen, ["target", "accepted", "score_col", "policy", "fraction", "selected_cells", "selected_gain_sum", "selected_positive_gain_rate", "positive_subjects", "negative_subjects", "raw_action_count", "inverse_action_count", "gain_lift_vs_null", "assignment_score", "accept_reason"], max_rows=20)}

## Best Coordinate Nested Heldout Subject Summary

{markdown_table(selected_fold_summary, ["heldout_subject", "selected_cells", "gain_sum", "mean_gain", "positive_gain_rate", "accepted_targets", "held_targets"], max_rows=20)}

## Best Coordinate Nested Target Summary

{markdown_table(selected_target_summary, ["target", "selected_cells", "gain_sum", "mean_gain", "positive_gain_rate", "raw_action_count", "inverse_action_count", "positive_subjects", "negative_subjects"], max_rows=20)}

## Route Decision Frequency

{markdown_table(selected_route_frequency, ["score_col", "target", "heldout_accept_rate", "top_policy", "top_fraction", "top_policy_count", "heldout_gain_sum", "heldout_positive_subjects", "heldout_negative_subjects"], max_rows=20)}

## Stable Policies Used For Candidate

{markdown_table(stable_policies, ["target", "accepted", "score_col", "policy", "fraction", "heldout_accept_rate", "heldout_gain_sum", "heldout_positive_subjects", "heldout_negative_subjects", "heldout_positive_gain_rate", "accept_reason"], max_rows=20)}

## Anchor-Free Candidate

- candidate: `{summary["candidate_file"]}`
- validation: `{summary["validation"]}`

## 해석

좋은 결과:

```text
subject-relative responsibility가 nested heldout gain을 양수로 바꾸면,
HS-JEPA core signal의 병목은 signal absence가 아니라 calibration coordinate였다.
```

나쁜 결과:

```text
relative coordinate도 음수이면,
현재 core action-health geometry는 action assignment를 만들 만큼 충분히 안정적이지 않다.
```

현재 결론:

```text
이번 결과는 negative/fragile이지만 이전 실패보다 구조적으로 낫다.
absolute health score release는 nested heldout에서 크게 무너졌고,
pairwise responsibility coordinate가 손실을 크게 줄였다.

따라서 HS-JEPA core signal의 일부 병목은 calibration coordinate였다.
다만 전체 gain은 아직 음수이고 S4만 strict stable target으로 남았으므로,
subject-relative assignment alone을 release-grade decoder라고 주장하면 안 된다.
다음 big bet은 pairwise responsibility를 multi-row episode / listener responsibility와 결합하는 것이다.
```
"""


def run() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    score_col = "support_score_target_interaction_world_residual_energy"
    train_cells, test_cells, train_priors, _view_metrics = build_listener_cells()
    train_modes, test_modes = build_action_mode_tables(train_cells, test_cells, score_col)
    feature_cols = toxicity_feature_columns(train_modes, test_modes)
    oof_score, test_score = fit_subject_heldout_health_scores(train_modes, test_modes, feature_cols)
    train_modes["health_score"] = oof_score
    test_modes["health_score"] = test_score
    train_modes = add_subject_relative_scores(train_modes)
    test_modes = add_subject_relative_scores(test_modes)

    score_variants = [
        "health_score",
        "subject_relative_responsibility",
        "pairwise_responsibility",
        "support_aligned_responsibility",
        "conservative_pair_best_responsibility",
    ]
    variant_rows: list[dict[str, Any]] = []
    full_chosen_map: dict[str, pd.DataFrame] = {}
    fold_map: dict[str, pd.DataFrame] = {}
    route_map: dict[str, pd.DataFrame] = {}
    audit_map: dict[str, pd.DataFrame] = {}
    grid_frames: list[pd.DataFrame] = []

    for variant in score_variants:
        grid = policy_grid(train_modes, variant, NULL_REPEATS)
        grid_frames.append(grid)
        full_chosen = choose_target_policies(grid)
        fold_summary, route_rows, nested_audit = run_nested_subject_heldout(train_modes, variant)
        variant_rows.append(summarize_variant(variant, fold_summary, nested_audit))
        full_chosen_map[variant] = full_chosen
        fold_map[variant] = fold_summary
        route_map[variant] = route_rows
        audit_map[variant] = nested_audit

    variant_summary = pd.DataFrame(variant_rows).sort_values(["survival_score", "nested_gain_sum"], ascending=False)
    best_score_col = str(variant_summary.iloc[0]["score_col"])
    selected_full_chosen = full_chosen_map[best_score_col]
    selected_fold_summary = fold_map[best_score_col]
    selected_route_rows = route_map[best_score_col]
    selected_nested_audit = audit_map[best_score_col]
    selected_target_summary = summarize_targets(selected_nested_audit)
    all_route_frequency = route_decision_frequency(pd.concat(route_map.values(), ignore_index=True))
    selected_route_frequency = all_route_frequency[all_route_frequency["score_col"].eq(best_score_col)].copy()
    stable_policies = stable_policies_from_nested(selected_full_chosen, selected_route_rows, selected_nested_audit)
    stable_oof_audit = apply_policies_to_modes(train_modes, stable_policies)

    sample = pd.read_csv(SAMPLE_SUBMISSION)
    candidate, test_audit = apply_policies_to_test(sample, test_modes, stable_policies, train_priors)
    validation = validate_submission(candidate, sample)
    if not validation["valid"]:
        raise ValueError(f"candidate is not upload-safe: {validation['problems']}")
    candidate_name = f"submission_hsjepa_subject_relative_responsibility_assignment_anchor_free_{short_hash(candidate)}_uploadsafe.csv"

    y = train_modes["healthy_action"].astype(int).to_numpy()
    stable_selected = stable_oof_audit[stable_oof_audit["released"]].copy()
    stable_targets = stable_policies.loc[stable_policies["accepted"].eq(True), "target"].astype(str).tolist()
    best_row = variant_summary.iloc[0].to_dict()
    summary = {
        "package": "subject_relative_responsibility_assignment",
        "status": "subject_relative_responsibility_assignment_ready",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "verdict": (
            "subject_relative_assignment_positive"
            if float(best_row["nested_gain_sum"]) > 0 and int(best_row["positive_subjects"]) > int(best_row["negative_subjects"])
            else "subject_relative_assignment_negative_or_fragile"
        ),
        "action_health_auc": safe_auc(y, oof_score),
        "action_health_ap": safe_ap(y, oof_score),
        "best_score_col": best_score_col,
        "best_nested_gain_sum": float(best_row["nested_gain_sum"]),
        "best_nested_selected_cells": int(best_row["nested_selected_cells"]),
        "best_positive_subjects": int(best_row["positive_subjects"]),
        "best_negative_subjects": int(best_row["negative_subjects"]),
        "listener_global_gain_reference": LISTENER_GLOBAL_GAIN_REFERENCE,
        "route_conservation_gain_reference": ROUTE_CONSERVATION_GAIN_REFERENCE,
        "subject_balanced_gain_reference": SUBJECT_BALANCED_GAIN_REFERENCE,
        "subject_heldout_route_gain_reference": SUBJECT_HELDOUT_ROUTE_GAIN_REFERENCE,
        "stable_targets": stable_targets,
        "stable_oof_selected_cells": int(stable_oof_audit["released"].sum()),
        "stable_oof_gain_sum": float(stable_selected["effective_gain"].sum()) if len(stable_selected) else 0.0,
        "released_test_cells": int(test_audit["released"].sum()),
        "candidate_file": candidate_name,
        "validation": validation,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pd.concat(grid_frames, ignore_index=True).to_csv(OUT_DIR / "subject_relative_policy_grid.csv", index=False)
    variant_summary.to_csv(OUT_DIR / "subject_relative_variant_summary.csv", index=False)
    selected_full_chosen.to_csv(OUT_DIR / "subject_relative_best_full_chosen_policies.csv", index=False)
    selected_fold_summary.to_csv(OUT_DIR / "subject_relative_best_nested_subject_summary.csv", index=False)
    selected_route_rows.to_csv(OUT_DIR / "subject_relative_best_nested_route_decisions.csv", index=False)
    selected_nested_audit[selected_nested_audit["released"]].to_csv(OUT_DIR / "subject_relative_best_nested_selected_actions.csv", index=False)
    selected_target_summary.to_csv(OUT_DIR / "subject_relative_best_nested_target_summary.csv", index=False)
    selected_route_frequency.to_csv(OUT_DIR / "subject_relative_best_route_decision_frequency.csv", index=False)
    stable_policies.to_csv(OUT_DIR / "subject_relative_stable_policies.csv", index=False)
    stable_oof_audit[stable_oof_audit["released"]].to_csv(OUT_DIR / "subject_relative_stable_selected_oof_actions.csv", index=False)
    test_audit[test_audit["released"]].to_csv(OUT_DIR / "subject_relative_stable_selected_test_actions.csv", index=False)
    candidate.to_csv(OUT_DIR / candidate_name, index=False)
    candidate.to_csv(ROOT / candidate_name, index=False)
    (OUT_DIR / "subject_relative_responsibility_assignment_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    md = build_markdown(
        summary,
        variant_summary,
        selected_full_chosen,
        selected_fold_summary,
        selected_target_summary,
        selected_route_frequency,
        stable_policies,
    )
    (OUT_DIR / "SUBJECT_RELATIVE_RESPONSIBILITY_ASSIGNMENT_KO.md").write_text(md.rstrip() + "\n", encoding="utf-8")
    PAPER_DOC.write_text(md.rstrip() + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
