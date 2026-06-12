#!/usr/bin/env python3
"""Subject-invariant listener responsibility field core probe for HS-JEPA.

The masked-pretext experiment showed only a weak improvement over raw
human-state.  This script changes the hidden target representation itself.

Instead of predicting action-level release directly, it first compresses the
strict subject-invariant jury into a row-target field:

    "Does this human-state row require this target listener to intervene?"

This is closer to the HS-JEPA thesis:

    visible human-life context
      + target listener
      -> hidden listener responsibility field
      -> adapter chooses a row-target action only where responsibility is high

The core probe is action-free at the responsibility step.  The optional
submission candidate uses the existing action decoder only after the core has
selected responsible row-target cells.

No public LB ledger, prior submission probabilities, proprietary embedding API,
masked-tail teacher score as feature, or label-informed peer margins are used as
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
from hsjepa_core.run_masked_human_state_pretext_listener_core import (  # noqa: E402
    LABEL_INFORMED_PREFIXES,
    build_masked_pretext_state,
)
from sleep_competition_adapter.target_route_conservation_decoder import SAMPLE_SUBMISSION, short_hash  # noqa: E402


OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "subject_invariant_listener_responsibility_field_core"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "SUBJECT_INVARIANT_LISTENER_RESPONSIBILITY_FIELD_CORE_KO.md"
FEATURE_PATH = ROOT / "team_experiments" / "cohort_hsjepa" / "cohort_human_state_features.csv"
PARENT_OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "masked_view_consensus_tail_core"
JURY_OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "subject_invariant_masked_tail_jury_core"
RANDOM_SEED = 20260613

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


def load_action_frames() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    parent_train = pd.read_csv(PARENT_OUT_DIR / "masked_view_consensus_full_oof_action_audit.csv")
    parent_test = pd.read_csv(PARENT_OUT_DIR / "masked_view_consensus_test_release_audit.csv")
    strict = pd.read_csv(JURY_OUT_DIR / "subject_invariant_jury_strict_subjectheldout_audit.csv")
    keys = ["row", "target", "cell_id", "decoder_action"]
    train = parent_train.merge(
        strict[keys + ["strict_jury_released", "released", "heldout_subject"]],
        on=keys,
        how="left",
        validate="one_to_one",
    ).copy()
    train["strict_jury_released"] = train["strict_jury_released"].fillna(False).astype(bool)
    return train, parent_test.copy(), strict


def build_cell_frame(action_frame: pd.DataFrame) -> pd.DataFrame:
    agg = (
        action_frame.groupby(
            ["row", "metric_row", "subject_id", "sleep_date", "lifelog_date", "target", "cell_id"],
            observed=True,
        )
        .agg(
            listener_responsible=("strict_jury_released", "max"),
            strict_action_count=("strict_jury_released", "sum"),
            max_effective_gain=("effective_gain", "max"),
            target_prior=("target_prior", "first"),
            is_q_target=("is_q_target", "first"),
            is_s_target=("is_s_target", "first"),
            is_q2_q3_s2=("is_q2_q3_s2", "first"),
            is_objective_tail=("is_objective_tail", "first"),
        )
        .reset_index()
    )
    positive = (
        action_frame[action_frame["strict_jury_released"].astype(bool) & action_frame["effective_gain"].astype(float).gt(0.0)]
        .groupby("cell_id", observed=True)
        .size()
    )
    agg["positive_listener_responsible"] = agg["cell_id"].map(positive).fillna(0).astype(int).gt(0).astype(int)
    agg["listener_responsible"] = agg["listener_responsible"].astype(bool).astype(int)
    agg["strict_action_count"] = agg["strict_action_count"].astype(int)
    for target in TARGETS:
        agg[f"target_onehot_{target}"] = agg["target"].eq(target).astype(int)
    return agg


def build_test_cell_frame(action_test: pd.DataFrame) -> pd.DataFrame:
    agg = (
        action_test.groupby(
            ["row", "metric_row", "subject_id", "sleep_date", "lifelog_date", "target", "cell_id"],
            observed=True,
        )
        .agg(
            target_prior=("target_prior", "first"),
            is_q_target=("is_q_target", "first"),
            is_s_target=("is_s_target", "first"),
            is_q2_q3_s2=("is_q2_q3_s2", "first"),
            is_objective_tail=("is_objective_tail", "first"),
        )
        .reset_index()
    )
    for target in TARGETS:
        agg[f"target_onehot_{target}"] = agg["target"].eq(target).astype(int)
    return agg


def attach_core_features(
    cell_train: pd.DataFrame,
    cell_test: pd.DataFrame,
    features: pd.DataFrame,
    pretext_state: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    merge_keys = ["subject_id", "sleep_date", "lifelog_date", "metric_row"]
    human_cols = [
        col
        for col in features.columns
        if col not in {"split"}
        and not any(col.startswith(prefix) for prefix in LABEL_INFORMED_PREFIXES)
    ]
    train = cell_train.merge(
        features[features["split"].eq("train")][human_cols],
        on=merge_keys,
        how="left",
        validate="many_to_one",
    )
    test = cell_test.merge(
        features[features["split"].eq("test")][human_cols],
        on=merge_keys,
        how="left",
        validate="many_to_one",
    )
    train = train.merge(
        pretext_state[pretext_state["split"].eq("train")].drop(columns=["split"]),
        on=merge_keys,
        how="left",
        validate="many_to_one",
    )
    test = test.merge(
        pretext_state[pretext_state["split"].eq("test")].drop(columns=["split"]),
        on=merge_keys,
        how="left",
        validate="many_to_one",
    )
    pretext_cols = [col for col in pretext_state.columns if col.startswith("pretext_")]
    return train, test, pretext_cols


def human_numeric_columns(train: pd.DataFrame, test: pd.DataFrame) -> list[str]:
    numeric = [
        col
        for col in train.columns
        if col in test.columns
        and pd.api.types.is_numeric_dtype(train[col])
        and col not in KEY_COLS
        and col not in TARGETS
        and not any(col.startswith(prefix) for prefix in LABEL_INFORMED_PREFIXES)
    ]
    return [
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


def feature_families(train: pd.DataFrame, test: pd.DataFrame, pretext_cols: list[str]) -> dict[str, list[str]]:
    target_listener = [
        col
        for col in [
            "target_prior",
            "is_q_target",
            "is_s_target",
            "is_q2_q3_s2",
            "is_objective_tail",
        ]
        if col in train.columns and col in test.columns
    ] + [col for col in train.columns if col.startswith("target_onehot_") and col in test.columns]
    human = human_numeric_columns(train, test)
    pretext = [col for col in pretext_cols if col in train.columns and col in test.columns]
    pretext_pred = [col for col in pretext if col.startswith("pretext_pred_")]
    pretext_energy = [col for col in pretext if col.startswith("pretext_energy_")]
    return {
        "listener_only": list(dict.fromkeys(target_listener)),
        "human_listener_responsibility": list(dict.fromkeys(human + target_listener)),
        "masked_pretext_listener_responsibility": list(dict.fromkeys(pretext_pred + pretext_energy + target_listener)),
        "human_plus_masked_pretext_responsibility": list(dict.fromkeys(human + pretext + target_listener)),
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
    for fold, (tr, va) in enumerate(splitter.split(train, y, groups=groups)):
        y_tr = y[tr]
        if len(np.unique(y_tr)) < 2 or not features:
            pred = np.full(len(va), float(y_tr.mean()) if len(y_tr) else 0.0)
        else:
            model = classifier_factory(RANDOM_SEED + fold)
            model.fit(train.iloc[tr][features], y_tr)
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
        model.fit(train[features], y)
        test_score = model.predict_proba(test[features])[:, 1]
    return np.clip(oof, 1e-5, 1.0 - 1e-5), np.clip(test_score, 1e-5, 1.0 - 1e-5), fold_rows


def evaluate(
    cell_train: pd.DataFrame,
    cell_test: pd.DataFrame,
    families: dict[str, list[str]],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, np.ndarray], dict[str, np.ndarray]]:
    metric_rows: list[dict[str, Any]] = []
    target_rows: list[dict[str, Any]] = []
    fold_rows: list[dict[str, Any]] = []
    test_scores: dict[str, np.ndarray] = {}
    oof_scores: dict[str, np.ndarray] = {}
    label_tasks = {
        "listener_responsible": "listener_responsible",
        "positive_listener_responsible": "positive_listener_responsible",
    }
    for family_name, features in families.items():
        for task_name, label_col in label_tasks.items():
            oof, test_score, folds = fit_oof_scores(cell_train, cell_test, features, label_col)
            score_col = f"score__{family_name}__{task_name}"
            test_scores[score_col] = test_score
            oof_scores[score_col] = oof
            y = cell_train[label_col].astype(int).to_numpy()
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
                part = cell_train[cell_train["target"].eq(target)]
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
    return pd.DataFrame(metric_rows), pd.DataFrame(target_rows), pd.DataFrame(fold_rows), test_scores, oof_scores


def simulate_release_gain(
    action_train: pd.DataFrame,
    cell_train: pd.DataFrame,
    release_laws: pd.DataFrame,
    oof_scores: dict[str, np.ndarray],
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    accepted = release_laws[release_laws["accepted"].astype(bool)]
    for score_col, scores in oof_scores.items():
        if not score_col.endswith("__listener_responsible"):
            continue
        family = score_col.split("__")[1]
        cells = cell_train[["cell_id", "target"]].copy()
        cells["responsibility_score"] = scores
        selected_cell_ids: set[int] = set()
        for _, law in accepted.iterrows():
            target = str(law["target"])
            budget = max(1, int(law["heldout_selected_cells"]))
            part = cells[cells["target"].eq(target)].sort_values("responsibility_score", ascending=False).head(budget)
            selected_cell_ids.update(part["cell_id"].astype(int).tolist())
        selected_actions = action_train[action_train["cell_id"].isin(selected_cell_ids)].copy()
        selected_actions = selected_actions.sort_values(
            ["cell_id", "masked_view_consensus_health_score", "decisive_action"],
            ascending=[True, False, False],
        ).drop_duplicates("cell_id", keep="first")
        gains = selected_actions["effective_gain"].astype(float)
        rows.append(
            {
                "feature_family": family,
                "selected_cells": int(len(selected_actions)),
                "realized_gain_sum": float(gains.sum()),
                "mean_realized_gain": float(gains.mean()) if len(gains) else 0.0,
                "positive_gain_rate": float(gains.gt(0).mean()) if len(gains) else 0.0,
                "negative_gain_rate": float(gains.lt(0).mean()) if len(gains) else 0.0,
            }
        )
    return pd.DataFrame(rows).sort_values("realized_gain_sum", ascending=False)


def release_candidate(
    sample: pd.DataFrame,
    action_test: pd.DataFrame,
    cell_test: pd.DataFrame,
    release_laws: pd.DataFrame,
    train_priors: dict[str, float],
    test_scores: dict[str, np.ndarray],
    release_family: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    out = sample.copy()
    for target in TARGETS:
        out[target] = float(train_priors[target])
    score_col = f"score__{release_family}__listener_responsible"
    cells = cell_test.copy()
    cells["responsibility_score"] = test_scores[score_col]
    selected_cell_ids: set[int] = set()
    for _, law in release_laws[release_laws["accepted"].astype(bool)].iterrows():
        target = str(law["target"])
        part = cells[cells["target"].eq(target)].sort_values("responsibility_score", ascending=False)
        part = part.head(int(law["test_budget"]))
        selected_cell_ids.update(part["cell_id"].astype(int).tolist())
    audit = action_test.copy()
    audit = audit.merge(cells[["cell_id", "responsibility_score"]], on="cell_id", how="left", validate="many_to_one")
    audit["released"] = audit["cell_id"].isin(selected_cell_ids)
    selected_actions = audit[audit["released"]].sort_values(
        ["cell_id", "masked_view_consensus_health_score", "decisive_action"],
        ascending=[True, False, False],
    ).drop_duplicates("cell_id", keep="first")
    for _, row in selected_actions.iterrows():
        out.at[int(row["row"]), str(row["target"])] = float(row["action_prob"])
    out[TARGETS] = out[TARGETS].clip(1e-5, 1.0 - 1e-5)
    audit["selected_action"] = audit.index.isin(selected_actions.index)
    return out, audit


def build_markdown(
    summary: dict[str, Any],
    metrics: pd.DataFrame,
    target_metrics: pd.DataFrame,
    fold_metrics: pd.DataFrame,
    release_metrics: pd.DataFrame,
    release_counts: pd.DataFrame,
) -> str:
    primary = metrics[metrics["label_task"].eq("listener_responsible")].sort_values("ap_lift_vs_rate", ascending=False)
    primary_targets = target_metrics[target_metrics["label_task"].eq("listener_responsible")].sort_values(
        ["feature_family", "ap_lift_vs_rate"],
        ascending=[True, False],
    )
    return f"""# Subject-Invariant Listener Responsibility Field Core

## 한 줄 요약

action을 직접 예측하지 않고, 먼저 row-target 단위에서
`이 human-state에서 이 target listener가 개입할 책임이 있는가`를 예측했다.

```text
visible human-life context
  + target listener
  -> hidden listener responsibility field
  -> action decoder only after responsibility is high
```

## 왜 필요한 실험인가

Open-loop raw human-state와 masked-view pretext는 action-level strict release를
listener-only보다 잘 분리하지 못했다. 이 실험은 hidden target 자체를 action에서
listener responsibility field로 바꾼다. HS-JEPA가 인간 상태를 더 잘 표현한다면,
row-target listener responsibility는 단순 target prior/listener-only보다 잘 예측되어야 한다.

## 사용하지 않은 정보

- public LB ledger: `{summary["uses_public_score_ledger"]}`
- prior submission probability: `{summary["uses_prior_submission_probabilities"]}`
- proprietary embedding API: `{summary["uses_proprietary_embedding_api"]}`
- masked-tail teacher score as feature: `{summary["uses_masked_tail_teacher_score"]}`
- label-informed peer margin as feature: `{summary["uses_label_informed_peer_margin"]}`

## Verdict

- verdict: `{summary["verdict"]}`
- best responsibility family: `{summary["best_responsibility_family"]}`
- human responsibility AP lift: `{format_float(summary["human_responsibility_ap_lift"], 6)}`
- listener-only AP lift: `{format_float(summary["listener_only_ap_lift"], 6)}`
- masked-pretext AP lift: `{format_float(summary["masked_pretext_ap_lift"], 6)}`
- human-plus-pretext AP lift: `{format_float(summary["human_plus_pretext_ap_lift"], 6)}`
- action-decoder OOF gain for release family: `{format_float(summary["release_family_oof_gain_sum"], 6)}`
- listener-only action-decoder OOF gain: `{format_float(summary["listener_only_oof_gain_sum"], 6)}`
- released test cells: `{summary["released_test_cells"]}`
- candidate: `{summary["candidate_file"]}`

## Listener Responsibility Leaderboard

{markdown_table(primary, ["feature_family", "label_task", "feature_count", "positive_rate", "auc", "ap", "ap_lift_vs_rate"], max_rows=20)}

## Target-Level Responsibility Metrics

{markdown_table(primary_targets, ["feature_family", "target", "positive_rate", "auc", "ap", "ap_lift_vs_rate"], max_rows=80)}

## Release Simulation With Existing Action Decoder

{markdown_table(release_metrics, ["feature_family", "selected_cells", "realized_gain_sum", "mean_realized_gain", "positive_gain_rate", "negative_gain_rate"], max_rows=20)}

## Fold Stability

{markdown_table(fold_metrics, ["feature_family", "label_task", "fold", "heldout_subjects", "positive_rate", "auc", "ap"], max_rows=80)}

## Release Counts

{markdown_table(release_counts, ["target", "count"], max_rows=20)}

## 해석

좋은 결과:

```text
human-state + listener가 listener-only보다 row-target responsibility를 더 잘 예측하면,
HS-JEPA core가 action probability가 아니라 listener responsibility field를 먼저 복원한다는
논문 주장이 강화된다.
```

나쁜 결과:

```text
cell-level responsibility가 좋아도 action-decoder gain이 낮으면,
core는 "어디를 봐야 하는지"는 알지만 "어떻게 움직여야 하는지" 번역이 아직 toxic하다는 뜻이다.
```
"""


def run() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    features = pd.read_csv(FEATURE_PATH)
    pretext_state, _pretext_metrics, pretext_cols, _ = build_masked_pretext_state(features)
    action_train, action_test, _strict = load_action_frames()
    release_laws = pd.read_csv(JURY_OUT_DIR / "subject_invariant_jury_release_laws.csv")
    cell_train = build_cell_frame(action_train)
    cell_test = build_test_cell_frame(action_test)
    cell_train, cell_test, pretext_cols = attach_core_features(cell_train, cell_test, features, pretext_state)
    families = feature_families(cell_train, cell_test, pretext_cols)
    metrics, target_metrics, fold_metrics, test_scores, oof_scores = evaluate(cell_train, cell_test, families)
    release_metrics = simulate_release_gain(action_train, cell_train, release_laws, oof_scores)

    primary = metrics[metrics["label_task"].eq("listener_responsible")].copy()
    get_lift = lambda name: float(primary.loc[primary["feature_family"].eq(name), "ap_lift_vs_rate"].iloc[0])
    listener_lift = get_lift("listener_only")
    human_lift = get_lift("human_listener_responsibility")
    pretext_lift = get_lift("masked_pretext_listener_responsibility")
    human_plus_lift = get_lift("human_plus_masked_pretext_responsibility")
    best = primary.sort_values("ap_lift_vs_rate", ascending=False).iloc[0]
    core_families = [
        "human_listener_responsibility",
        "masked_pretext_listener_responsibility",
        "human_plus_masked_pretext_responsibility",
    ]
    best_core = primary[primary["feature_family"].isin(core_families)].sort_values(
        "ap_lift_vs_rate",
        ascending=False,
    ).iloc[0]
    release_family = str(best_core["feature_family"])

    train_priors = action_train.groupby("target", observed=True)["target_prior"].first().astype(float).to_dict()
    sample = pd.read_csv(SAMPLE_SUBMISSION)
    candidate, release_audit = release_candidate(
        sample,
        action_test,
        cell_test,
        release_laws,
        train_priors,
        test_scores,
        release_family=release_family,
    )
    validation = validate_submission(candidate, sample)
    if not validation["valid"]:
        raise ValueError(f"candidate is not upload-safe: {validation['problems']}")
    candidate_name = (
        f"submission_hsjepa_subject_invariant_listener_responsibility_field_"
        f"{short_hash(candidate)}_uploadsafe.csv"
    )
    release_counts = (
        release_audit[release_audit["selected_action"]].groupby("target", observed=True).size().reset_index(name="count")
    )
    release_gain = float(
        release_metrics.loc[release_metrics["feature_family"].eq(release_family), "realized_gain_sum"].iloc[0]
    )
    listener_release_gain = float(
        release_metrics.loc[release_metrics["feature_family"].eq("listener_only"), "realized_gain_sum"].iloc[0]
    )
    if float(best_core["ap_lift_vs_rate"]) > listener_lift and release_gain > 0.0:
        verdict = "listener_responsibility_field_positive_release_positive"
    elif float(best_core["ap_lift_vs_rate"]) > listener_lift and release_gain > listener_release_gain:
        verdict = "listener_responsibility_field_positive_action_translation_fragile"
    elif float(best_core["ap_lift_vs_rate"]) > listener_lift:
        verdict = "listener_responsibility_field_positive_but_action_translation_toxic"
    else:
        verdict = "listener_responsibility_core_negative"
    summary = {
        "package": "subject_invariant_listener_responsibility_field_core",
        "status": "subject_invariant_listener_responsibility_field_core_ready",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "uses_masked_tail_teacher_score": False,
        "uses_label_informed_peer_margin": False,
        "verdict": verdict,
        "best_responsibility_family": str(best["feature_family"]),
        "best_responsibility_ap_lift": float(best["ap_lift_vs_rate"]),
        "listener_only_ap_lift": listener_lift,
        "human_responsibility_ap_lift": human_lift,
        "masked_pretext_ap_lift": pretext_lift,
        "human_plus_pretext_ap_lift": human_plus_lift,
        "release_family": release_family,
        "release_family_oof_gain_sum": release_gain,
        "listener_only_oof_gain_sum": listener_release_gain,
        "released_test_cells": int(release_audit["selected_action"].sum()),
        "release_targets": release_counts["target"].astype(str).tolist() if not release_counts.empty else [],
        "candidate_file": candidate_name,
        "validation": validation,
    }

    metrics.to_csv(OUT_DIR / "listener_responsibility_field_metrics.csv", index=False)
    target_metrics.to_csv(OUT_DIR / "listener_responsibility_field_target_metrics.csv", index=False)
    fold_metrics.to_csv(OUT_DIR / "listener_responsibility_field_fold_metrics.csv", index=False)
    release_metrics.to_csv(OUT_DIR / "listener_responsibility_field_release_simulation.csv", index=False)
    release_audit.to_csv(OUT_DIR / "listener_responsibility_field_release_audit.csv", index=False)
    release_counts.to_csv(OUT_DIR / "listener_responsibility_field_release_counts.csv", index=False)
    candidate.to_csv(OUT_DIR / candidate_name, index=False)
    candidate.to_csv(ROOT / candidate_name, index=False)
    (OUT_DIR / "subject_invariant_listener_responsibility_field_core_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    md = build_markdown(summary, metrics, target_metrics, fold_metrics, release_metrics, release_counts)
    (OUT_DIR / "SUBJECT_INVARIANT_LISTENER_RESPONSIBILITY_FIELD_CORE_KO.md").write_text(md, encoding="utf-8")
    PAPER_DOC.write_text(md, encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


if __name__ == "__main__":
    run()
