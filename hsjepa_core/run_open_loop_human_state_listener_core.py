#!/usr/bin/env python3
"""Open-loop human-state listener core probe for HS-JEPA.

The previous listener-manifold probe showed that the masked-tail HS-JEPA
representation separates subject-invariant action-health far better than
action geometry.  This script removes the masked-tail teacher and action
probability/magnitude features from the core side.

Question:
    Can OG lifelog human-state context plus a minimal listener identify the
    subject-invariant row-target-action support discovered by the jury?

This is a stricter core probe:

    OG lifelog/social/cohort human-state context
      + target listener
      + raw-vs-inverse action listener
      -> strict subject-invariant jury release support

No public LB ledger, prior submission probabilities, proprietary embedding
APIs, masked-tail teacher scores, or label-informed peer margins are used as
core features.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hsjepa_core.run_action_support_world_model_core import TARGETS, validate_submission  # noqa: E402
from hsjepa_core.run_lifelog_core_state_evidence import format_float, markdown_table  # noqa: E402
from sleep_competition_adapter.target_route_conservation_decoder import SAMPLE_SUBMISSION, short_hash  # noqa: E402


OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "open_loop_human_state_listener_core"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "OPEN_LOOP_HUMAN_STATE_LISTENER_CORE_KO.md"
FEATURE_PATH = ROOT / "team_experiments" / "cohort_hsjepa" / "cohort_human_state_features.csv"
PARENT_OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "masked_view_consensus_tail_core"
JURY_OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "subject_invariant_masked_tail_jury_core"
RANDOM_SEED = 20260613

LABEL_INFORMED_PREFIXES = (
    "peer_margin_",
    "q_group_peer_margin",
    "s_group_peer_margin",
    "target_route_margin",
)
KEY_COLS = {
    "subject_id",
    "sleep_date",
    "lifelog_date",
    "split",
    "metric_row",
    "lifelog_date_str",
}


def safe_auc(y: np.ndarray, score: np.ndarray) -> float | None:
    y = np.asarray(y, dtype=int)
    score = np.asarray(score, dtype=float)
    if len(np.unique(y)) < 2:
        return None
    return float(roc_auc_score(y, score))


def safe_ap(y: np.ndarray, score: np.ndarray) -> float | None:
    y = np.asarray(y, dtype=int)
    score = np.asarray(score, dtype=float)
    if len(np.unique(y)) < 2:
        return None
    return float(average_precision_score(y, score))


def classifier_factory(seed: int) -> Any:
    return make_pipeline(
        SimpleImputer(strategy="median"),
        HistGradientBoostingClassifier(
            learning_rate=0.035,
            max_leaf_nodes=10,
            min_samples_leaf=14,
            l2_regularization=0.30,
            random_state=seed,
        ),
    )


def load_frames() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, float]]:
    parent_train = pd.read_csv(PARENT_OUT_DIR / "masked_view_consensus_full_oof_action_audit.csv")
    parent_test = pd.read_csv(PARENT_OUT_DIR / "masked_view_consensus_test_release_audit.csv")
    strict = pd.read_csv(JURY_OUT_DIR / "subject_invariant_jury_strict_subjectheldout_audit.csv")
    release_laws = pd.read_csv(JURY_OUT_DIR / "subject_invariant_jury_release_laws.csv")
    features = pd.read_csv(FEATURE_PATH)

    keys = ["row", "target", "cell_id", "decoder_action"]
    strict_cols = keys + ["strict_jury_released", "released", "heldout_subject"]
    train = parent_train.merge(
        strict[strict_cols],
        on=keys,
        how="left",
        suffixes=("", "_strict_jury"),
        validate="one_to_one",
    ).copy()
    train["strict_jury_released"] = train["strict_jury_released"].fillna(False).astype(bool)
    train["strict_positive_release"] = (
        train["strict_jury_released"].astype(bool) & train["effective_gain"].astype(float).gt(0.0)
    ).astype(int)
    train["healthy_action"] = train["effective_gain"].astype(float).gt(0.0).astype(int)
    train["toxic_tail_action"] = train["effective_gain"].astype(float).lt(-0.05).astype(int)

    merge_keys = ["subject_id", "sleep_date", "lifelog_date", "metric_row"]
    human_cols = [
        col
        for col in features.columns
        if col not in {"split"}
        and not any(col.startswith(prefix) for prefix in LABEL_INFORMED_PREFIXES)
    ]
    train = train.merge(
        features[features["split"].eq("train")][human_cols],
        on=merge_keys,
        how="left",
        validate="many_to_one",
        suffixes=("", "_human_state"),
    )
    test = parent_test.merge(
        features[features["split"].eq("test")][human_cols],
        on=merge_keys,
        how="left",
        validate="many_to_one",
        suffixes=("", "_human_state"),
    )
    prior_col = "target_prior" if "target_prior" in train.columns else "prior_prob"
    train_priors = train.groupby("target", observed=True)[prior_col].first().astype(float).to_dict()
    return train, test, release_laws, train_priors


def human_feature_families(train: pd.DataFrame, test: pd.DataFrame) -> dict[str, list[str]]:
    numeric = [
        col
        for col in train.columns
        if col in test.columns
        and pd.api.types.is_numeric_dtype(train[col])
        and col not in KEY_COLS
        and col not in TARGETS
        and not any(col.startswith(prefix) for prefix in LABEL_INFORMED_PREFIXES)
    ]
    human_numeric = [
        col
        for col in numeric
        if (
            col.startswith("human_state_latent_")
            or col
            in {
                "dayofweek",
                "is_weekend",
                "dayofmonth",
                "month_start_proximity",
                "month_end",
                "peer_group",
                "dist_to_subject_normal",
                "dist_to_peer_normal",
                "subject_minus_peer_dist",
                "subject_outlier_rank",
                "peer_outlier_rank",
                "cohort_outlier_score",
            }
            or col.startswith("usage_")
            or col.startswith("night_usage_")
            or col.startswith("phone_")
            or col.startswith("screen_")
            or col.startswith("watch_")
            or col.startswith("pedo_")
            or col.startswith("step_")
            or col.startswith("walking_")
            or col.startswith("running_")
            or col.startswith("distance_")
            or col.startswith("calories_")
            or col.startswith("speed_")
            or col.startswith("active_")
            or col.startswith("night_step")
            or col.startswith("hr_")
            or col.startswith("gps_")
            or col.startswith("wifi_")
            or col.startswith("ble_")
            or col.startswith("ambience_")
        )
    ]
    latent = [col for col in human_numeric if col.startswith("human_state_latent_")]
    cohort = [
        col
        for col in [
            "peer_group",
            "dist_to_subject_normal",
            "dist_to_peer_normal",
            "subject_minus_peer_dist",
            "subject_outlier_rank",
            "peer_outlier_rank",
            "cohort_outlier_score",
        ]
        if col in human_numeric
    ]
    social = [
        col
        for col in human_numeric
        if col.startswith("usage_")
        or col.startswith("night_usage_")
        or col in {"dayofweek", "is_weekend", "dayofmonth", "month_start_proximity", "month_end"}
    ]
    target_listener = [col for col in train.columns if col.startswith("target_onehot_") and col in test.columns]
    action_listener = [col for col in ["decoder_raw", "decoder_inverse", "decisive_action"] if col in train.columns and col in test.columns]
    objective_flags = [col for col in ["is_q_target", "is_s_target", "is_q2_q3_s2", "is_objective_tail"] if col in train.columns and col in test.columns]
    minimal_listener = target_listener + objective_flags + action_listener
    action_geometry = [
        col
        for col in [
            "prior_prob",
            "candidate_prob",
            "inverse_prob",
            "action_move",
            "abs_action_move",
            "action_move_rank",
            "action_prob",
            "action_delta",
            "action_abs_delta",
            "decoder_raw",
            "decoder_inverse",
            "decisive_action",
        ]
        if col in numeric
    ]
    return {
        "listener_only": list(dict.fromkeys(minimal_listener)),
        "calendar_social_listener": list(dict.fromkeys(social + minimal_listener)),
        "latent_cohort_listener": list(dict.fromkeys(latent + cohort + minimal_listener)),
        "open_loop_human_state_listener": list(dict.fromkeys(human_numeric + minimal_listener)),
        "action_geometry_only": list(dict.fromkeys(action_geometry)),
    }


def fit_oof_scores(
    train: pd.DataFrame,
    test: pd.DataFrame,
    features: list[str],
    label_col: str,
) -> tuple[np.ndarray, np.ndarray, list[dict[str, Any]]]:
    groups = train["subject_id"].astype(str).to_numpy()
    y = train[label_col].astype(int).to_numpy()
    splitter = GroupKFold(n_splits=max(2, min(5, len(np.unique(groups)))))
    oof = np.zeros(len(train), dtype=np.float64)
    fold_rows: list[dict[str, Any]] = []
    weight = 1.0 + np.minimum(train["effective_gain"].abs().to_numpy(dtype=np.float64) / 0.05, 8.0)
    for fold, (tr, va) in enumerate(splitter.split(train, y, groups=groups)):
        y_tr = y[tr]
        if len(np.unique(y_tr)) < 2 or not features:
            pred = np.full(len(va), float(y_tr.mean()) if len(y_tr) else 0.0)
        else:
            model = classifier_factory(RANDOM_SEED + fold)
            model.fit(train.iloc[tr][features], y_tr, histgradientboostingclassifier__sample_weight=weight[tr])
            pred = model.predict_proba(train.iloc[va][features])[:, 1]
        oof[va] = np.clip(pred, 1e-5, 1.0 - 1e-5)
        fold_rows.append(
            {
                "fold": fold,
                "heldout_subjects": ",".join(sorted(train.iloc[va]["subject_id"].astype(str).unique())),
                "positive_rate": float(y[va].mean()),
                "auc": safe_auc(y[va], oof[va]),
                "ap": safe_ap(y[va], oof[va]),
            }
        )
    if len(np.unique(y)) < 2 or not features:
        test_score = np.full(len(test), float(y.mean()) if len(y) else 0.0)
    else:
        model = classifier_factory(RANDOM_SEED + 97)
        model.fit(train[features], y, histgradientboostingclassifier__sample_weight=weight)
        test_score = model.predict_proba(test[features])[:, 1]
    return np.clip(oof, 1e-5, 1.0 - 1e-5), np.clip(test_score, 1e-5, 1.0 - 1e-5), fold_rows


def evaluate_open_loop(
    train: pd.DataFrame,
    test: pd.DataFrame,
    families: dict[str, list[str]],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, np.ndarray]]:
    metric_rows: list[dict[str, Any]] = []
    target_rows: list[dict[str, Any]] = []
    fold_rows: list[dict[str, Any]] = []
    test_scores: dict[str, np.ndarray] = {}
    label_tasks = {
        "strict_jury_released": "strict_jury_released",
        "strict_positive_release": "strict_positive_release",
        "healthy_action": "healthy_action",
        "toxic_tail_action": "toxic_tail_action",
    }
    for family_name, features in families.items():
        for task_name, label_col in label_tasks.items():
            oof, test_score, folds = fit_oof_scores(train, test, features, label_col)
            score_col = f"score__{family_name}__{task_name}"
            test_scores[score_col] = test_score
            y = train[label_col].astype(int).to_numpy()
            ap = safe_ap(y, oof)
            metric_rows.append(
                {
                    "feature_family": family_name,
                    "label_task": task_name,
                    "feature_count": len(features),
                    "positive_rate": float(y.mean()),
                    "auc": safe_auc(y, oof),
                    "ap": ap,
                    "ap_lift_vs_rate": float(ap - y.mean()) if ap is not None else None,
                }
            )
            for fold in folds:
                fold["feature_family"] = family_name
                fold["label_task"] = task_name
                fold_rows.append(fold)
            for target in TARGETS:
                part = train[train["target"].eq(target)]
                yt = part[label_col].astype(int).to_numpy()
                st = oof[part.index.to_numpy()]
                target_ap = safe_ap(yt, st)
                target_rows.append(
                    {
                        "feature_family": family_name,
                        "label_task": task_name,
                        "target": target,
                        "positive_rate": float(yt.mean()),
                        "auc": safe_auc(yt, st),
                        "ap": target_ap,
                        "ap_lift_vs_rate": float(target_ap - yt.mean()) if target_ap is not None else None,
                    }
                )
    return pd.DataFrame(metric_rows), pd.DataFrame(target_rows), pd.DataFrame(fold_rows), test_scores


def release_candidate(
    sample: pd.DataFrame,
    test: pd.DataFrame,
    release_laws: pd.DataFrame,
    train_priors: dict[str, float],
    test_scores: dict[str, np.ndarray],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    out = sample.copy()
    for target in TARGETS:
        out[target] = float(train_priors[target])
    score_col = "score__open_loop_human_state_listener__strict_jury_released"
    audit = test.copy()
    audit["open_loop_release_score"] = test_scores[score_col]
    released = pd.Series(False, index=audit.index)
    for _, law in release_laws.iterrows():
        if not bool(law["accepted"]):
            continue
        target = str(law["target"])
        part = audit[audit["target"].eq(target)].copy()
        part = part.sort_values(["open_loop_release_score", "decisive_action"], ascending=[False, False])
        part = part.drop_duplicates("cell_id", keep="first").head(int(law["test_budget"]))
        released.loc[part.index] = True
    audit["released"] = released.to_numpy(dtype=bool)
    for _, row in audit[audit["released"]].iterrows():
        out.at[int(row["row"]), str(row["target"])] = float(row["action_prob"])
    out[TARGETS] = out[TARGETS].clip(1e-5, 1.0 - 1e-5)
    return out, audit


def build_markdown(
    summary: dict[str, Any],
    metrics: pd.DataFrame,
    target_metrics: pd.DataFrame,
    fold_metrics: pd.DataFrame,
    release_counts: pd.DataFrame,
) -> str:
    strict = metrics[metrics["label_task"].eq("strict_jury_released")].sort_values("ap_lift_vs_rate", ascending=False)
    strict_targets = target_metrics[target_metrics["label_task"].eq("strict_jury_released")].sort_values(
        ["feature_family", "ap_lift_vs_rate"], ascending=[True, False]
    )
    return f"""# Open-Loop Human-State Listener Core

## 한 줄 요약

masked-tail teacher와 action probability/magnitude를 빼고,
OG lifelog/social/cohort human-state와 minimal listener만으로 subject-invariant
action-health support가 분리되는지 검증했다.

```text
OG human-state context
  + target listener
  + raw/inverse action listener
  -> subject-invariant action-health support
```

## 빠른 판정

이 실험은 HS-JEPA core의 가장 엄격한 쪽 probe다.
성공하면 core representation이 teacher-free/open-loop 상태에서도 action-health의 일부를
읽는다는 뜻이고, 실패하면 현재 strong evidence가 masked-tail teacher에 크게 의존한다는 뜻이다.

## 사용하지 않은 정보

- public LB ledger: `{summary["uses_public_score_ledger"]}`
- prior submission probability: `{summary["uses_prior_submission_probabilities"]}`
- proprietary embedding API: `{summary["uses_proprietary_embedding_api"]}`
- masked-tail teacher score as feature: `{summary["uses_masked_tail_teacher_score"]}`
- label-informed peer margin as feature: `{summary["uses_label_informed_peer_margin"]}`

## Verdict

- verdict: `{summary["verdict"]}`
- open-loop AP lift: `{format_float(summary["open_loop_ap_lift"], 6)}`
- listener-only AP lift: `{format_float(summary["listener_only_ap_lift"], 6)}`
- action-only AP lift: `{format_float(summary["action_only_ap_lift"], 6)}`
- released test cells: `{summary["released_test_cells"]}`
- candidate: `{summary["candidate_file"]}`

## Strict Jury Release Leaderboard

{markdown_table(strict, ["feature_family", "label_task", "feature_count", "positive_rate", "auc", "ap", "ap_lift_vs_rate"], max_rows=20)}

## Target-Level Strict Jury Release Metrics

{markdown_table(strict_targets, ["feature_family", "target", "positive_rate", "auc", "ap", "ap_lift_vs_rate"], max_rows=80)}

## All Label-Task Metrics

{markdown_table(metrics, ["feature_family", "label_task", "feature_count", "positive_rate", "auc", "ap", "ap_lift_vs_rate"], max_rows=80)}

## Fold Stability

{markdown_table(fold_metrics, ["feature_family", "label_task", "fold", "heldout_subjects", "positive_rate", "auc", "ap"], max_rows=80)}

## Release Counts

{markdown_table(release_counts, ["target", "count"], max_rows=20)}

## 해석

좋은 결과:

```text
open-loop human-state listener가 listener-only와 action-only를 이기면,
HS-JEPA core가 teacher 없이도 human-state/action-health support의 일부를 잡는다.
```

나쁜 결과:

```text
open-loop가 약하고 masked-tail representation만 강하면,
현재 HS-JEPA의 release-grade 성과는 아직 teacher/action-tail representation에 의존한다.
논문에서는 open-loop core와 teacher-derived tail field를 분리해서 말해야 한다.
```
"""


def run() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    train, test, release_laws, train_priors = load_frames()
    families = human_feature_families(train, test)
    metrics, target_metrics, fold_metrics, test_scores = evaluate_open_loop(train, test, families)
    sample = pd.read_csv(SAMPLE_SUBMISSION)
    candidate, release_audit = release_candidate(sample, test, release_laws, train_priors, test_scores)
    validation = validate_submission(candidate, sample)
    if not validation["valid"]:
        raise ValueError(f"candidate is not upload-safe: {validation['problems']}")
    candidate_name = f"submission_hsjepa_open_loop_human_state_listener_anchor_free_{short_hash(candidate)}_uploadsafe.csv"
    release_counts = release_audit[release_audit["released"]].groupby("target", observed=True).size().reset_index(name="count")

    strict = metrics[metrics["label_task"].eq("strict_jury_released")].copy()
    get_lift = lambda name: float(strict.loc[strict["feature_family"].eq(name), "ap_lift_vs_rate"].iloc[0])
    open_loop_lift = get_lift("open_loop_human_state_listener")
    listener_lift = get_lift("listener_only")
    action_lift = get_lift("action_geometry_only")
    best = strict.sort_values("ap_lift_vs_rate", ascending=False).iloc[0]
    if open_loop_lift > max(listener_lift, action_lift):
        verdict = "open_loop_human_state_listener_positive"
    elif open_loop_lift > action_lift:
        verdict = "open_loop_human_state_beats_action_but_not_listener_only"
    else:
        verdict = "open_loop_human_state_listener_negative"
    summary = {
        "package": "open_loop_human_state_listener_core",
        "status": "open_loop_human_state_listener_core_ready",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "uses_masked_tail_teacher_score": False,
        "uses_label_informed_peer_margin": False,
        "verdict": verdict,
        "best_strict_jury_family": str(best["feature_family"]),
        "best_strict_jury_ap_lift": float(best["ap_lift_vs_rate"]),
        "open_loop_ap_lift": open_loop_lift,
        "listener_only_ap_lift": listener_lift,
        "action_only_ap_lift": action_lift,
        "released_test_cells": int(release_audit["released"].sum()),
        "release_targets": release_counts["target"].astype(str).tolist() if not release_counts.empty else [],
        "candidate_file": candidate_name,
        "validation": validation,
    }

    metrics.to_csv(OUT_DIR / "open_loop_human_state_listener_metrics.csv", index=False)
    target_metrics.to_csv(OUT_DIR / "open_loop_human_state_listener_target_metrics.csv", index=False)
    fold_metrics.to_csv(OUT_DIR / "open_loop_human_state_listener_fold_metrics.csv", index=False)
    release_audit.to_csv(OUT_DIR / "open_loop_human_state_listener_release_audit.csv", index=False)
    release_counts.to_csv(OUT_DIR / "open_loop_human_state_listener_release_counts.csv", index=False)
    candidate.to_csv(OUT_DIR / candidate_name, index=False)
    candidate.to_csv(ROOT / candidate_name, index=False)
    (OUT_DIR / "open_loop_human_state_listener_core_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    md = build_markdown(summary, metrics, target_metrics, fold_metrics, release_counts)
    (OUT_DIR / "OPEN_LOOP_HUMAN_STATE_LISTENER_CORE_KO.md").write_text(md, encoding="utf-8")
    PAPER_DOC.write_text(md, encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


if __name__ == "__main__":
    run()
