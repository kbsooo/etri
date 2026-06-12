#!/usr/bin/env python3
"""Subject-heldout action-toxicity field for HS-JEPA.

The previous subject-heldout route diagnostic showed that target-route policy
selection is still fragile under subject shift.  This experiment changes the
unit of prediction:

    target route policy -> row-target action health

Each row-target cell gets two possible actions:

    raw_memory_release
    inverse_toxic_memory

The model learns, without public LB or prior submission probabilities, whether
each action is healthy.  Scores are produced in a strict subject-heldout way:
each subject's action-health score is predicted by a model that did not train on
that subject.  A nested heldout policy stress then checks whether the selected
action field is a subject-general law or another OOF artifact.

This is a competition adapter / LeJEPA-style diagnostic.  It is not HS-JEPA
core itself.  The core signal is the masked world-state residual/energy and
listener-conditioned support score used as action-health context.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.pipeline import make_pipeline

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hsjepa_core.run_action_support_world_model_core import TARGETS, target_context_columns, validate_submission  # noqa: E402
from hsjepa_core.run_lifelog_core_state_evidence import format_float, markdown_table  # noqa: E402
from sleep_competition_adapter.target_route_conservation_decoder import (  # noqa: E402
    LISTENER_GLOBAL_GAIN_REFERENCE,
    SAMPLE_SUBMISSION,
    build_listener_cells,
    route_family,
    short_hash,
)


OUT_DIR = ROOT / "sleep_competition_adapter" / "outputs" / "subject_heldout_action_toxicity_field"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "SUBJECT_HELDOUT_ACTION_TOXICITY_FIELD_KO.md"
ROUTE_CONSERVATION_GAIN_REFERENCE = 15.595885092582881
SUBJECT_BALANCED_GAIN_REFERENCE = 10.122798836819854
SUBJECT_HELDOUT_ROUTE_GAIN_REFERENCE = -5.128700246067739
RANDOM_SEED = 20260613
NULL_REPEATS = 24
HELDOUT_NULL_REPEATS = 8


def stable_seed(*parts: object) -> int:
    key = "::".join(map(str, parts)).encode("utf-8")
    return RANDOM_SEED + int(hashlib.sha256(key).hexdigest()[:8], 16) % 1009


def model_factory(seed: int) -> Any:
    return make_pipeline(
        SimpleImputer(strategy="median"),
        HistGradientBoostingClassifier(
            learning_rate=0.032,
            max_leaf_nodes=14,
            min_samples_leaf=18,
            l2_regularization=0.24,
            random_state=seed,
        ),
    )


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


def add_mode_features(cells: pd.DataFrame, mode: str, score_col: str, train: bool) -> pd.DataFrame:
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
    out["score_raw_support"] = out[score_col].astype(float)
    out["score_inverse_support"] = 1.0 - out[score_col].astype(float)
    out["mode_support_alignment"] = np.where(
        out["decoder_action"].eq("raw_memory_release"),
        out["score_raw_support"],
        out["score_inverse_support"],
    )
    out["support_action_delta"] = out["mode_support_alignment"] * out["action_delta"]
    out["support_abs_delta"] = out["mode_support_alignment"] * out["action_abs_delta"]
    out["target_route_family"] = out["target"].map(route_family)
    for family in sorted(out["target_route_family"].dropna().unique()):
        out[f"route_family__{family}"] = out["target_route_family"].eq(family).astype(float)
    if train:
        out["healthy_action"] = out["effective_gain"].gt(0.0).astype(int)
    return out


def build_action_mode_tables(
    train_cells: pd.DataFrame,
    test_cells: pd.DataFrame,
    score_col: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    train_modes = pd.concat(
        [
            add_mode_features(train_cells, "raw_memory_release", score_col, train=True),
            add_mode_features(train_cells, "inverse_toxic_memory", score_col, train=True),
        ],
        ignore_index=True,
    )
    test_modes = pd.concat(
        [
            add_mode_features(test_cells, "raw_memory_release", score_col, train=False),
            add_mode_features(test_cells, "inverse_toxic_memory", score_col, train=False),
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


def toxicity_feature_columns(train_modes: pd.DataFrame, test_modes: pd.DataFrame) -> list[str]:
    base_cols = [
        "prior_prob",
        "candidate_prob",
        "inverse_prob",
        "action_prob",
        "action_move",
        "abs_action_move",
        "action_move_rank",
        "action_delta",
        "action_abs_delta",
        "decisive_action",
        "decoder_raw",
        "decoder_inverse",
        "score_raw_support",
        "score_inverse_support",
        "mode_support_alignment",
        "support_action_delta",
        "support_abs_delta",
    ]
    prefix_cols = [
        col
        for col in train_modes.columns
        if col.startswith("wm_resid_")
        or col.startswith("wm_energy")
        or col.startswith("target_interaction__")
        or col.startswith("family_interaction__")
        or col.startswith("route_family__")
    ]
    cols = target_context_columns() + base_cols + prefix_cols
    return [col for col in cols if col in train_modes.columns and col in test_modes.columns]


def fit_subject_heldout_health_scores(
    train_modes: pd.DataFrame,
    test_modes: pd.DataFrame,
    feature_cols: list[str],
) -> tuple[np.ndarray, np.ndarray]:
    y = train_modes["healthy_action"].astype(int).to_numpy()
    subjects = sorted(train_modes["subject_id"].astype(str).unique())
    oof = np.zeros(len(train_modes), dtype=np.float64)
    for subject in subjects:
        tr = train_modes.index[~train_modes["subject_id"].astype(str).eq(subject)].to_numpy()
        va = train_modes.index[train_modes["subject_id"].astype(str).eq(subject)].to_numpy()
        y_tr = y[tr]
        if len(np.unique(y_tr)) < 2:
            oof[va] = float(y_tr.mean())
            continue
        model = model_factory(stable_seed("subject-heldout-health", subject))
        model.fit(train_modes.iloc[tr][feature_cols], y_tr)
        oof[va] = model.predict_proba(train_modes.iloc[va][feature_cols])[:, 1]

    if len(np.unique(y)) < 2:
        test_score = np.full(len(test_modes), float(y.mean()), dtype=np.float64)
    else:
        model = model_factory(stable_seed("subject-heldout-health", "full-test"))
        model.fit(train_modes[feature_cols], y)
        test_score = model.predict_proba(test_modes[feature_cols])[:, 1]
    return oof, test_score


def choose_mode_indices(
    modes: pd.DataFrame,
    target: str,
    policy: str,
    fraction: float,
    score_col: str = "health_score",
) -> np.ndarray:
    if policy == "hold":
        return np.array([], dtype=int)
    part = modes[modes["target"].eq(target)].copy()
    if "decisive" in policy:
        part = part[part["decisive_action"].eq(1)]
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
    null_repeats: int,
) -> dict[str, Any]:
    selected = choose_mode_indices(modes, target, policy, fraction)
    selected_frame = modes.loc[selected] if len(selected) else modes.iloc[0:0]
    gains = selected_frame["effective_gain"].to_numpy(dtype=np.float64) if len(selected_frame) else np.array([], dtype=np.float64)
    subject_gain = (
        selected_frame.groupby("subject_id", observed=True)["effective_gain"].sum()
        if len(selected_frame)
        else pd.Series(dtype=float)
    )
    rng = np.random.default_rng(stable_seed("toxicity-null", target, policy, fraction))
    null_sums: list[float] = []
    if len(selected):
        part_idx = modes.index[modes["target"].eq(target)].to_numpy()
        original = modes.loc[part_idx, "health_score"].to_numpy(dtype=np.float64)
        for _ in range(null_repeats):
            shuffled = original.copy()
            rng.shuffle(shuffled)
            temp = modes.loc[part_idx].copy()
            temp["health_score"] = shuffled
            temp_selected = choose_mode_indices(temp, target, policy, fraction)
            null_sums.append(float(temp.loc[temp_selected, "effective_gain"].sum()) if len(temp_selected) else 0.0)
    null_mean = float(np.mean(null_sums)) if null_sums else 0.0
    null_std = float(np.std(null_sums, ddof=1)) if len(null_sums) > 1 else np.nan
    gain_sum = float(gains.sum()) if len(gains) else 0.0
    positive_rate = float((gains > 0).mean()) if len(gains) else np.nan
    negative_subjects = int((subject_gain < 0).sum()) if len(subject_gain) else 0
    positive_subjects = int((subject_gain > 0).sum()) if len(subject_gain) else 0
    raw_count = int(selected_frame["decoder_action"].eq("raw_memory_release").sum()) if len(selected_frame) else 0
    inverse_count = int(selected_frame["decoder_action"].eq("inverse_toxic_memory").sum()) if len(selected_frame) else 0
    health_score = (
        gain_sum
        + 0.30 * (gain_sum - null_mean)
        + 0.12 * (0.0 if not np.isfinite(null_std) or null_std == 0 else (gain_sum - null_mean) / null_std)
        + 0.40 * max(positive_rate if np.isfinite(positive_rate) else 0.0, 0.0)
        + 0.25 * positive_subjects
        - 0.75 * negative_subjects
    )
    return {
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
        "action_health_score": health_score,
    }


def policy_grid(modes: pd.DataFrame, null_repeats: int) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    fractions = [0.02, 0.04, 0.06, 0.08, 0.10, 0.14, 0.18, 0.25]
    for target in TARGETS:
        rows.append(evaluate_policy(modes, target, "hold", 0.0, null_repeats=0))
        for fraction in fractions:
            rows.append(evaluate_policy(modes, target, "top_health_all", fraction, null_repeats))
            rows.append(evaluate_policy(modes, target, "top_health_decisive", fraction, null_repeats))
    return pd.DataFrame(rows)


def choose_target_policies(grid: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for target, part in grid.groupby("target", observed=True):
        hold = part[part["policy"].eq("hold")].iloc[0].to_dict()
        viable = part[
            ~part["policy"].eq("hold")
            & (part["selected_gain_sum"] > 0.0)
            & (part["gain_lift_vs_null"] > 0.0)
            & (part["selected_positive_gain_rate"].fillna(0.0) >= 0.58)
            & (part["negative_subjects"] <= 3)
        ].copy()
        if viable.empty:
            hold["accepted"] = False
            hold["accept_reason"] = "no_action_health_policy_passed"
            rows.append(hold)
            continue
        row = viable.sort_values(["action_health_score", "selected_gain_sum"], ascending=False).iloc[0].to_dict()
        row["accepted"] = True
        row["accept_reason"] = "positive_subjectheldout_health_gain"
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
        )
        released.loc[selected] = True
    audit = modes.copy()
    audit["released"] = released.to_numpy()
    audit["effective_gain_released"] = np.where(audit["released"], audit["effective_gain"], 0.0)
    return audit


def run_nested_subject_heldout(modes: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    subjects = sorted(modes["subject_id"].astype(str).unique())
    fold_rows: list[dict[str, Any]] = []
    route_rows: list[dict[str, Any]] = []
    audits: list[pd.DataFrame] = []
    for subject in subjects:
        selector = modes[~modes["subject_id"].astype(str).eq(subject)].copy()
        heldout = modes[modes["subject_id"].astype(str).eq(subject)].copy()
        chosen = choose_target_policies(policy_grid(selector, HELDOUT_NULL_REPEATS))
        audit = apply_policies_to_modes(heldout, chosen)
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
                "held_targets": ",".join(chosen.loc[chosen["accepted"].eq(False), "target"].astype(str).tolist()),
            }
        )
        for _, row in chosen.iterrows():
            target = str(row["target"])
            target_selected = selected[selected["target"].eq(target)]
            route_rows.append(
                {
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


def summarize_targets(audit: pd.DataFrame) -> pd.DataFrame:
    selected = audit[audit["released"]].copy()
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


def route_decision_frequency(route_rows: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for target, part in route_rows.groupby("target", observed=True):
        top = part.groupby(["policy", "fraction"], observed=True).size().reset_index(name="count")
        top = top.sort_values("count", ascending=False).iloc[0]
        rows.append(
            {
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
    return pd.DataFrame(rows).sort_values("target")


def stable_policies_from_nested(full_chosen: pd.DataFrame, route_rows: pd.DataFrame, target_summary: pd.DataFrame) -> pd.DataFrame:
    target_stats = target_summary.set_index("target").to_dict(orient="index")
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
        row["accept_reason"] = "subject_heldout_action_toxicity_stable" if stable else "failed_subject_heldout_action_toxicity"
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
    health_metrics: pd.DataFrame,
    full_chosen: pd.DataFrame,
    fold_summary: pd.DataFrame,
    target_summary: pd.DataFrame,
    route_frequency: pd.DataFrame,
    stable_policies: pd.DataFrame,
) -> str:
    return f"""# HS-JEPA Diagnostic Adapter: Subject-Heldout Action Toxicity Field

## 한 줄 요약

target-route policy를 고르는 대신, row-target-action 자체가 건강한지 예측했다.
각 cell에는 raw release와 inverse-toxic action 후보를 모두 만들고,
HS-JEPA core context가 어떤 action을 믿어야 하는지 subject-heldout으로 검증했다.

```text
masked world-state residual/energy
  -> listener-conditioned action context
  -> subject-heldout action toxicity field
  -> target-specific stable release
```

## 빠른 판정: 이것은 HS-JEPA인가?

**HS-JEPA core 자체는 아니다.**
정확한 위치는 **HS-JEPA competition adapter + LeJEPA-style diagnostic**이다.

```text
HS-JEPA core
  = visible human-life context -> hidden world-state representation

이 문서의 역할
  = 그 representation이 row-target action toxicity를 subject-heldout에서 구분하는지 검증한다.
```

## 사용하지 않은 정보

- public LB ledger: `{summary["uses_public_score_ledger"]}`
- prior submission probability: `{summary["uses_prior_submission_probabilities"]}`
- proprietary embedding API: `{summary["uses_proprietary_embedding_api"]}`

## Verdict

- verdict: `{summary["verdict"]}`
- action-health AUC: `{format_float(summary["action_health_auc"], 6)}`
- action-health AP: `{format_float(summary["action_health_ap"], 6)}`
- nested heldout selected cells: `{summary["nested_heldout_selected_cells"]}`
- nested heldout gain sum: `{format_float(summary["nested_heldout_gain_sum"], 6)}`
- nested positive subjects: `{summary["nested_positive_subjects"]}`
- nested negative subjects: `{summary["nested_negative_subjects"]}`
- stable targets: `{summary["stable_targets"]}`
- stable OOF gain sum: `{format_float(summary["stable_oof_gain_sum"], 6)}`
- released test cells: `{summary["released_test_cells"]}`

## Health Model Metrics

{markdown_table(health_metrics, ["metric", "value"], max_rows=20)}

## Full-OOF Chosen Policies

{markdown_table(full_chosen, ["target", "accepted", "policy", "fraction", "selected_cells", "selected_gain_sum", "selected_positive_gain_rate", "positive_subjects", "negative_subjects", "raw_action_count", "inverse_action_count", "gain_lift_vs_null", "action_health_score", "accept_reason"], max_rows=20)}

## Nested Heldout Subject Summary

{markdown_table(fold_summary, ["heldout_subject", "selected_cells", "gain_sum", "mean_gain", "positive_gain_rate", "accepted_targets", "held_targets"], max_rows=20)}

## Nested Heldout Target Summary

{markdown_table(target_summary, ["target", "selected_cells", "gain_sum", "mean_gain", "positive_gain_rate", "raw_action_count", "inverse_action_count", "positive_subjects", "negative_subjects"], max_rows=20)}

## Route Decision Frequency

{markdown_table(route_frequency, ["target", "heldout_accept_rate", "top_policy", "top_fraction", "top_policy_count", "heldout_gain_sum", "heldout_positive_subjects", "heldout_negative_subjects"], max_rows=20)}

## Stable Policies Used For Candidate

{markdown_table(stable_policies, ["target", "accepted", "policy", "fraction", "heldout_accept_rate", "heldout_gain_sum", "heldout_positive_subjects", "heldout_negative_subjects", "heldout_positive_gain_rate", "accept_reason"], max_rows=20)}

## Anchor-Free Candidate

- candidate: `{summary["candidate_file"]}`
- validation: `{summary["validation"]}`

## 해석

좋은 결과:

```text
subject-heldout action-health score와 nested heldout policy가 모두 양수이면,
HS-JEPA core representation은 route policy보다 더 세밀한 action toxicity field를 가진다.
```

나쁜 결과:

```text
action-health AUC는 양수인데 nested heldout gain이 음수이면,
core representation은 action toxicity를 약하게 읽지만 release-grade decoder가 아직 없다.
```

현재 결론:

```text
이번 결과는 negative/fragile이다.
subject-heldout action-health AUC/AP는 양수라 core representation이 독성 단서를 읽기는 한다.
하지만 nested subject-heldout release gain은 음수이고 stable target은 없다.

따라서 HS-JEPA core representation만으로 action을 release하는 decoder는 아직 부족하다.
논문에서는 core가 hidden action-health geometry를 제공한다는 점과,
release-grade adapter에는 subject-invariant responsibility/assignment가 추가로 필요하다는 점을 함께 주장해야 한다.
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

    y = train_modes["healthy_action"].astype(int).to_numpy()
    health_metrics = pd.DataFrame(
        [
            {"metric": "action_health_auc", "value": safe_auc(y, oof_score)},
            {"metric": "action_health_ap", "value": safe_ap(y, oof_score)},
            {"metric": "action_health_base_rate", "value": float(y.mean())},
            {"metric": "feature_count", "value": float(len(feature_cols))},
            {"metric": "train_action_modes", "value": float(len(train_modes))},
            {"metric": "test_action_modes", "value": float(len(test_modes))},
        ]
    )

    full_grid = policy_grid(train_modes, NULL_REPEATS)
    full_chosen = choose_target_policies(full_grid)
    full_oof_audit = apply_policies_to_modes(train_modes, full_chosen)
    fold_summary, route_rows, nested_audit = run_nested_subject_heldout(train_modes)
    nested_selected = nested_audit[nested_audit["released"]].copy()
    target_summary_frame = summarize_targets(nested_audit)
    route_frequency = route_decision_frequency(route_rows)
    stable_policies = stable_policies_from_nested(full_chosen, route_rows, target_summary_frame)
    stable_oof_audit = apply_policies_to_modes(train_modes, stable_policies)

    sample = pd.read_csv(SAMPLE_SUBMISSION)
    candidate, test_audit = apply_policies_to_test(sample, test_modes, stable_policies, train_priors)
    validation = validate_submission(candidate, sample)
    if not validation["valid"]:
        raise ValueError(f"candidate is not upload-safe: {validation['problems']}")
    candidate_name = f"submission_hsjepa_subject_heldout_action_toxicity_field_anchor_free_{short_hash(candidate)}_uploadsafe.csv"

    nested_gain = float(nested_selected["effective_gain"].sum()) if len(nested_selected) else 0.0
    nested_positive_rate = float((nested_selected["effective_gain"] > 0).mean()) if len(nested_selected) else np.nan
    nested_positive_subjects = int((fold_summary["gain_sum"] > 0).sum())
    nested_negative_subjects = int((fold_summary["gain_sum"] < 0).sum())
    stable_selected = stable_oof_audit[stable_oof_audit["released"]].copy()
    stable_targets = stable_policies.loc[stable_policies["accepted"].eq(True), "target"].astype(str).tolist()
    summary = {
        "package": "subject_heldout_action_toxicity_field",
        "status": "subject_heldout_action_toxicity_field_ready",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "verdict": (
            "subject_heldout_action_toxicity_positive"
            if nested_gain > 0 and nested_positive_subjects > nested_negative_subjects
            else "subject_heldout_action_toxicity_negative_or_fragile"
        ),
        "action_health_auc": safe_auc(y, oof_score),
        "action_health_ap": safe_ap(y, oof_score),
        "action_health_base_rate": float(y.mean()),
        "feature_count": int(len(feature_cols)),
        "full_oof_selected_cells": int(full_oof_audit["released"].sum()),
        "full_oof_gain_sum": float(full_oof_audit["effective_gain_released"].sum()),
        "nested_heldout_selected_cells": int(len(nested_selected)),
        "nested_heldout_gain_sum": nested_gain,
        "nested_heldout_positive_gain_rate": nested_positive_rate,
        "nested_positive_subjects": nested_positive_subjects,
        "nested_negative_subjects": nested_negative_subjects,
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
    health_metrics.to_csv(OUT_DIR / "subject_heldout_action_toxicity_health_metrics.csv", index=False)
    full_grid.to_csv(OUT_DIR / "subject_heldout_action_toxicity_policy_grid.csv", index=False)
    full_chosen.to_csv(OUT_DIR / "subject_heldout_action_toxicity_full_chosen_policies.csv", index=False)
    full_oof_audit[full_oof_audit["released"]].to_csv(
        OUT_DIR / "subject_heldout_action_toxicity_full_selected_actions.csv",
        index=False,
    )
    fold_summary.to_csv(OUT_DIR / "nested_heldout_subject_summary.csv", index=False)
    route_rows.to_csv(OUT_DIR / "nested_heldout_route_decisions.csv", index=False)
    nested_audit[nested_audit["released"]].to_csv(OUT_DIR / "nested_heldout_selected_actions.csv", index=False)
    target_summary_frame.to_csv(OUT_DIR / "nested_heldout_target_summary.csv", index=False)
    route_frequency.to_csv(OUT_DIR / "nested_heldout_route_decision_frequency.csv", index=False)
    stable_policies.to_csv(OUT_DIR / "stable_action_toxicity_policies.csv", index=False)
    stable_oof_audit[stable_oof_audit["released"]].to_csv(OUT_DIR / "stable_action_toxicity_selected_oof_actions.csv", index=False)
    test_audit[test_audit["released"]].to_csv(OUT_DIR / "stable_action_toxicity_selected_test_actions.csv", index=False)
    candidate.to_csv(OUT_DIR / candidate_name, index=False)
    candidate.to_csv(ROOT / candidate_name, index=False)
    (OUT_DIR / "subject_heldout_action_toxicity_field_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    md = build_markdown(summary, health_metrics, full_chosen, fold_summary, target_summary_frame, route_frequency, stable_policies)
    (OUT_DIR / "SUBJECT_HELDOUT_ACTION_TOXICITY_FIELD_KO.md").write_text(md.rstrip() + "\n", encoding="utf-8")
    PAPER_DOC.write_text(md.rstrip() + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
