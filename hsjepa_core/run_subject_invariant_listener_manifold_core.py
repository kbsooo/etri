#!/usr/bin/env python3
"""Subject-invariant listener manifold core probe for HS-JEPA.

The subject-invariant masked-tail jury showed that some row-target-action
releases survive leave-one-subject-out selection.  This script asks a more
representation-level question:

    Is the surviving action-health field separable in HS-JEPA hidden
    representation space, or did a hand-written release law do all the work?

It treats the strict subject-heldout jury release as a hidden target
representation and probes several feature families under GroupKFold by subject:

    action_geometry_only             adapter baseline
    masked_tail_representation       masked-view hidden tail state
    world_episode_minimal_listener   action-probability-free core listener state
    hsjepa_listener_manifold         hidden tail + world/episode + minimal listener
    full_decoder_context             upper-bound adapter context

No public LB ledger, prior submission probabilities, or proprietary embedding
APIs are used.  The generated submission is a diagnostic anchor-free candidate
that releases actions from the learned listener manifold rather than direct
jury vote counts.
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


OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "subject_invariant_listener_manifold_core"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "SUBJECT_INVARIANT_LISTENER_MANIFOLD_CORE_KO.md"
PARENT_OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "masked_view_consensus_tail_core"
JURY_OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "subject_invariant_masked_tail_jury_core"
RANDOM_SEED = 20260613


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
            min_samples_leaf=16,
            l2_regularization=0.28,
            random_state=seed,
        ),
    )


def load_frames() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, float]]:
    parent_train = pd.read_csv(PARENT_OUT_DIR / "masked_view_consensus_full_oof_action_audit.csv")
    parent_test = pd.read_csv(PARENT_OUT_DIR / "masked_view_consensus_test_release_audit.csv")
    strict = pd.read_csv(JURY_OUT_DIR / "subject_invariant_jury_strict_subjectheldout_audit.csv")
    keys = ["row", "target", "cell_id", "decoder_action"]
    strict_cols = keys + ["strict_jury_released", "released", "heldout_subject"]
    train = parent_train.merge(
        strict[strict_cols],
        on=keys,
        how="left",
        suffixes=("", "_strict_jury"),
        validate="one_to_one",
    )
    train["strict_jury_released"] = train["strict_jury_released"].fillna(False).astype(bool)
    train["healthy_action"] = train["effective_gain"].astype(float).gt(0.0).astype(int)
    train["toxic_tail_action"] = train["effective_gain"].astype(float).lt(-0.05).astype(int)
    train["strict_positive_release"] = (
        train["strict_jury_released"].astype(bool) & train["effective_gain"].astype(float).gt(0.0)
    ).astype(int)
    prior_col = "target_prior" if "target_prior" in train.columns else "prior_prob"
    train_priors = train.groupby("target", observed=True)[prior_col].first().astype(float).to_dict()
    release_laws = pd.read_csv(JURY_OUT_DIR / "subject_invariant_jury_release_laws.csv")
    return train, parent_test, release_laws, train_priors


def feature_families(train: pd.DataFrame, test: pd.DataFrame) -> dict[str, list[str]]:
    numeric = [
        col
        for col in train.columns
        if col in test.columns
        and pd.api.types.is_numeric_dtype(train[col])
        and col
        not in {
            "y",
            "realized_gain",
            "inverse_realized_gain",
            "effective_gain",
            "positive_gain",
            "positive_inverse_gain",
            "effective_gain_released",
            "healthy_action",
            "toxic_tail_action",
            "strict_positive_release",
            "strict_jury_released",
            "released",
        }
    ]
    hidden_tail = [
        col
        for col in numeric
        if col.startswith("mv_") or col.startswith("masked_view_")
    ]
    world = [col for col in numeric if col.startswith("wm_")]
    episode = [col for col in numeric if col.startswith("episode_")]
    listener = [
        col
        for col in numeric
        if col.startswith("target_onehot_")
        or col.startswith("route_family__")
        or col in {"decoder_raw", "decoder_inverse", "decisive_action", "is_q_target", "is_s_target"}
    ]
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
            "listener_mode_alignment",
        ]
        if col in numeric
    ]
    hsjepa_listener = list(dict.fromkeys(hidden_tail + world + episode + listener))
    world_episode_minimal = list(dict.fromkeys(world + episode + listener))
    full_decoder = list(dict.fromkeys(hidden_tail + world + episode + listener + action_geometry))
    return {
        "action_geometry_only": action_geometry,
        "masked_tail_representation": hidden_tail,
        "world_episode_minimal_listener": world_episode_minimal,
        "hsjepa_listener_manifold": hsjepa_listener,
        "full_decoder_context": full_decoder,
    }


def fit_oof_scores(
    train: pd.DataFrame,
    test: pd.DataFrame,
    features: list[str],
    label_col: str,
) -> tuple[np.ndarray, np.ndarray, list[dict[str, Any]]]:
    groups = train["subject_id"].astype(str).to_numpy()
    subjects = sorted(np.unique(groups))
    splitter = GroupKFold(n_splits=max(2, min(5, len(subjects))))
    oof = np.zeros(len(train), dtype=np.float64)
    fold_rows: list[dict[str, Any]] = []
    y = train[label_col].astype(int).to_numpy()
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
        model = classifier_factory(RANDOM_SEED + 99)
        model.fit(train[features], y, histgradientboostingclassifier__sample_weight=weight)
        test_score = model.predict_proba(test[features])[:, 1]
    return np.clip(oof, 1e-5, 1.0 - 1e-5), np.clip(test_score, 1e-5, 1.0 - 1e-5), fold_rows


def evaluate_manifolds(
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
            train[f"score__{family_name}__{task_name}"] = oof
            test_scores[f"score__{family_name}__{task_name}"] = test_score
            y = train[label_col].astype(int).to_numpy()
            metric_rows.append(
                {
                    "feature_family": family_name,
                    "label_task": task_name,
                    "feature_count": len(features),
                    "positive_rate": float(y.mean()),
                    "auc": safe_auc(y, oof),
                    "ap": safe_ap(y, oof),
                    "ap_lift_vs_rate": float(safe_ap(y, oof) - y.mean()) if safe_ap(y, oof) is not None else None,
                }
            )
            for fold in folds:
                fold["feature_family"] = family_name
                fold["label_task"] = task_name
                fold_rows.append(fold)
            for target in TARGETS:
                part = train[train["target"].eq(target)]
                yt = part[label_col].astype(int).to_numpy()
                st = part[f"score__{family_name}__{task_name}"].to_numpy(dtype=np.float64)
                target_rows.append(
                    {
                        "feature_family": family_name,
                        "label_task": task_name,
                        "target": target,
                        "positive_rate": float(yt.mean()),
                        "auc": safe_auc(yt, st),
                        "ap": safe_ap(yt, st),
                        "ap_lift_vs_rate": float(safe_ap(yt, st) - yt.mean()) if safe_ap(yt, st) is not None else None,
                    }
                )
    return pd.DataFrame(metric_rows), pd.DataFrame(target_rows), pd.DataFrame(fold_rows), test_scores


def manifold_release_candidate(
    sample: pd.DataFrame,
    test: pd.DataFrame,
    release_laws: pd.DataFrame,
    train_priors: dict[str, float],
    test_scores: dict[str, np.ndarray],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    out = sample.copy()
    for target in TARGETS:
        out[target] = float(train_priors[target])

    score_col = "score__hsjepa_listener_manifold__strict_jury_released"
    audit = test.copy()
    audit["listener_manifold_release_score"] = test_scores[score_col]
    released = pd.Series(False, index=audit.index)
    for _, law in release_laws.iterrows():
        if not bool(law["accepted"]):
            continue
        target = str(law["target"])
        part = audit[audit["target"].eq(target)].copy()
        part = part.sort_values(
            ["listener_manifold_release_score", "masked_view_consensus_utility", "masked_view_disagreement"],
            ascending=[False, False, True],
        )
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
    return f"""# Subject-Invariant Listener Manifold Core

## 한 줄 요약

subject-invariant jury가 고른 action-health가 단순 rule인지, 아니면 HS-JEPA hidden
representation 공간에서 subject를 넘어 분리되는지 검증했다.

```text
HS-JEPA hidden representation
  -> subject-heldout listener/action-health separability probe
  -> learned listener-manifold release score
  -> sparse diagnostic correction
```

## 빠른 판정

이 실험은 HS-JEPA core 자체를 직접 label classifier로 쓰는 실험이 아니다.
정확히는 **core representation이 adapter가 찾은 성공/실패 action-health를 재현 가능한
manifold로 담고 있는지** 확인하는 representation probe다.

## 사용하지 않은 정보

- public LB ledger: `{summary["uses_public_score_ledger"]}`
- prior submission probability: `{summary["uses_prior_submission_probabilities"]}`
- proprietary embedding API: `{summary["uses_proprietary_embedding_api"]}`

## Verdict

- verdict: `{summary["verdict"]}`
- best strict-jury family: `{summary["best_strict_jury_family"]}`
- best strict-jury AP lift: `{format_float(summary["best_strict_jury_ap_lift"], 6)}`
- HS-JEPA listener AP lift: `{format_float(summary["hsjepa_listener_ap_lift"], 6)}`
- action-only AP lift: `{format_float(summary["action_only_ap_lift"], 6)}`
- released test cells: `{summary["released_test_cells"]}`
- candidate: `{summary["candidate_file"]}`

## Strict Jury Release Manifold Leaderboard

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
HS-JEPA listener manifold가 action-only baseline보다 strict jury release를 더 잘
분리하면, hidden human-state representation이 adapter rule의 부산물이 아니라
subject-invariant action-health geometry를 담고 있다는 증거가 된다.
```

나쁜 결과:

```text
action geometry only가 압도적으로 이기면, 현재 성과는 HS-JEPA core보다
competition adapter의 action magnitude/prior geometry에 더 의존한다는 뜻이다.
```
"""


def run() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    train, test, release_laws, train_priors = load_frames()
    families = feature_families(train, test)
    metrics, target_metrics, fold_metrics, test_scores = evaluate_manifolds(train, test, families)
    sample = pd.read_csv(SAMPLE_SUBMISSION)
    candidate, release_audit = manifold_release_candidate(sample, test, release_laws, train_priors, test_scores)
    validation = validate_submission(candidate, sample)
    if not validation["valid"]:
        raise ValueError(f"candidate is not upload-safe: {validation['problems']}")
    candidate_name = f"submission_hsjepa_subject_invariant_listener_manifold_anchor_free_{short_hash(candidate)}_uploadsafe.csv"
    release_counts = release_audit[release_audit["released"]].groupby("target", observed=True).size().reset_index(name="count")

    strict = metrics[metrics["label_task"].eq("strict_jury_released")].copy()
    best = strict.sort_values("ap_lift_vs_rate", ascending=False).iloc[0]
    hsjepa_lift = float(
        strict.loc[strict["feature_family"].eq("hsjepa_listener_manifold"), "ap_lift_vs_rate"].iloc[0]
    )
    action_lift = float(strict.loc[strict["feature_family"].eq("action_geometry_only"), "ap_lift_vs_rate"].iloc[0])
    verdict = (
        "hsjepa_listener_manifold_beats_action_geometry"
        if hsjepa_lift > action_lift
        else "action_geometry_dominates_listener_manifold"
    )

    summary = {
        "package": "subject_invariant_listener_manifold_core",
        "status": "subject_invariant_listener_manifold_core_ready",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "verdict": verdict,
        "best_strict_jury_family": str(best["feature_family"]),
        "best_strict_jury_ap_lift": float(best["ap_lift_vs_rate"]),
        "hsjepa_listener_ap_lift": hsjepa_lift,
        "action_only_ap_lift": action_lift,
        "released_test_cells": int(release_audit["released"].sum()),
        "release_targets": release_counts["target"].astype(str).tolist() if not release_counts.empty else [],
        "candidate_file": candidate_name,
        "validation": validation,
    }

    metrics.to_csv(OUT_DIR / "subject_invariant_listener_manifold_metrics.csv", index=False)
    target_metrics.to_csv(OUT_DIR / "subject_invariant_listener_manifold_target_metrics.csv", index=False)
    fold_metrics.to_csv(OUT_DIR / "subject_invariant_listener_manifold_fold_metrics.csv", index=False)
    release_audit.to_csv(OUT_DIR / "subject_invariant_listener_manifold_release_audit.csv", index=False)
    release_counts.to_csv(OUT_DIR / "subject_invariant_listener_manifold_release_counts.csv", index=False)
    candidate.to_csv(OUT_DIR / candidate_name, index=False)
    candidate.to_csv(ROOT / candidate_name, index=False)
    (OUT_DIR / "subject_invariant_listener_manifold_core_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    md = build_markdown(summary, metrics, target_metrics, fold_metrics, release_counts)
    (OUT_DIR / "SUBJECT_INVARIANT_LISTENER_MANIFOLD_CORE_KO.md").write_text(md, encoding="utf-8")
    PAPER_DOC.write_text(md, encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


if __name__ == "__main__":
    run()
