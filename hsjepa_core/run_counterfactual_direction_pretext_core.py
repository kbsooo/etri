#!/usr/bin/env python3
"""Counterfactual direction-pretext core probe for HS-JEPA.

The previous signed-direction experiment repaired action translation toxicity,
but its best direction family was action geometry.  That is useful as a
competition adapter, but it is weak as a paper-level HS-JEPA core claim.

This script lifts the raw-vs-inverse choice into a hidden target
representation:

    visible human-state context + target listener
      -> predict counterfactual direction representation
      -> choose raw or inverse only after responsibility is high

The core feature families deliberately exclude action probabilities, action
magnitude, previous submission probabilities, public LB, and label-informed peer
margins.  An action-geometry reference is reported as an adapter boundary, not
as HS-JEPA core evidence.
"""

from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from pandas.errors import PerformanceWarning
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
from hsjepa_core.run_masked_human_state_pretext_listener_core import build_masked_pretext_state  # noqa: E402
from hsjepa_core.run_subject_invariant_listener_responsibility_field_core import (  # noqa: E402
    FEATURE_PATH,
    JURY_OUT_DIR,
    attach_core_features,
    build_cell_frame,
    build_test_cell_frame,
    evaluate as evaluate_responsibility,
    feature_families as responsibility_feature_families,
    human_numeric_columns,
    load_action_frames,
)
from sleep_competition_adapter.target_route_conservation_decoder import SAMPLE_SUBMISSION, short_hash  # noqa: E402


OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "counterfactual_direction_pretext_core"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "COUNTERFACTUAL_DIRECTION_PRETEXT_CORE_KO.md"
RANDOM_SEED = 20260613

warnings.simplefilter("ignore", PerformanceWarning)

CORE_DIRECTION_FAMILIES = [
    "listener_only_direction",
    "human_context_direction",
    "masked_pretext_direction",
    "responsibility_weighted_pretext_direction",
    "human_plus_masked_pretext_direction",
]


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
            l2_regularization=0.32,
            random_state=seed,
        ),
    )


def target_listener_columns(frame: pd.DataFrame) -> list[str]:
    base = [
        "target_prior",
        "target_prior_rank",
        "target_uncertainty",
        "is_q_target",
        "is_s_target",
        "is_q2_q3_s2",
        "is_objective_tail",
    ]
    return [col for col in base if col in frame.columns] + [
        col for col in frame.columns if col.startswith("target_onehot_")
    ]


def prepare_frames() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, str]:
    features = pd.read_csv(FEATURE_PATH)
    pretext_state, _pretext_metrics, pretext_cols, _ = build_masked_pretext_state(features)
    action_train, action_test, _strict = load_action_frames()
    release_laws = pd.read_csv(JURY_OUT_DIR / "subject_invariant_jury_release_laws.csv")

    cell_train = build_cell_frame(action_train)
    cell_test = build_test_cell_frame(action_test)
    cell_train, cell_test, pretext_cols = attach_core_features(cell_train, cell_test, features, pretext_state)

    resp_families = responsibility_feature_families(cell_train, cell_test, pretext_cols)
    resp_metrics, _target_metrics, _fold_metrics, resp_test_scores, resp_oof_scores = evaluate_responsibility(
        cell_train,
        cell_test,
        resp_families,
    )
    primary = resp_metrics[resp_metrics["label_task"].eq("listener_responsible")].copy()
    core_candidates = [
        "human_listener_responsibility",
        "masked_pretext_listener_responsibility",
        "human_plus_masked_pretext_responsibility",
    ]
    responsibility_family = str(
        primary[primary["feature_family"].isin(core_candidates)]
        .sort_values("ap_lift_vs_rate", ascending=False)
        .iloc[0]["feature_family"]
    )
    score_col = f"score__{responsibility_family}__listener_responsible"
    cell_train["responsibility_score"] = resp_oof_scores[score_col]
    cell_test["responsibility_score"] = resp_test_scores[score_col]

    core_cols = list(
        dict.fromkeys(
            human_numeric_columns(cell_train, cell_test)
            + [col for col in pretext_cols if col in cell_train.columns and col in cell_test.columns]
            + ["responsibility_score"]
        )
    )
    merge_cols = list(
        dict.fromkeys(
            [
                "cell_id",
                "listener_responsible",
                "positive_listener_responsible",
                "responsibility_score",
            ]
            + core_cols
        )
    )
    action_train = action_train.merge(
        cell_train[merge_cols],
        on="cell_id",
        how="left",
        validate="many_to_one",
    )
    action_test = action_test.merge(
        cell_test[["cell_id", "responsibility_score"] + [col for col in core_cols if col in cell_test.columns]],
        on="cell_id",
        how="left",
        validate="many_to_one",
    )
    return action_train, action_test, cell_train, release_laws, responsibility_family


def build_counterfactual_cells(actions: pd.DataFrame) -> pd.DataFrame:
    keys = ["cell_id", "row", "metric_row", "subject_id", "sleep_date", "lifelog_date", "target"]
    raw = actions[actions["decoder_raw"].astype(float).eq(1.0)].copy()
    inv = actions[actions["decoder_inverse"].astype(float).eq(1.0)].copy()
    base_cols = keys + [
        "listener_responsible",
        "positive_listener_responsible",
        "target_prior",
        "target_prior_rank",
        "target_uncertainty",
        "is_q_target",
        "is_s_target",
        "is_q2_q3_s2",
        "is_objective_tail",
        "responsibility_score",
    ] + [c for c in actions.columns if c.startswith("target_onehot_")]
    feature_cols = [
        col
        for col in actions.columns
        if (
            col.startswith("human_state_latent_")
            or col.startswith("pretext_")
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
        )
    ]
    base_cols = list(dict.fromkeys([col for col in base_cols + feature_cols if col in raw.columns]))
    raw_value_cols = ["action_prob", "candidate_prob", "inverse_prob", "action_move"]
    if "effective_gain" in raw.columns:
        raw_value_cols = ["effective_gain"] + raw_value_cols
    frame = raw[base_cols + raw_value_cols].rename(
        columns={
            "effective_gain": "raw_gain",
            "action_prob": "raw_action_prob",
            "candidate_prob": "raw_candidate_prob",
            "inverse_prob": "raw_inverse_prob",
            "action_move": "raw_action_move",
        }
    )
    inverse_value_cols = ["action_prob", "candidate_prob", "inverse_prob", "action_move"]
    if "effective_gain" in inv.columns:
        inverse_value_cols = ["effective_gain"] + inverse_value_cols
    inverse_small = inv[keys + inverse_value_cols].rename(
        columns={
            "effective_gain": "inverse_gain",
            "action_prob": "inverse_action_prob",
            "candidate_prob": "inverse_candidate_prob",
            "inverse_prob": "inverse_inverse_prob",
            "action_move": "inverse_action_move",
        }
    )
    frame = frame.merge(inverse_small, on=keys, how="inner", validate="one_to_one")
    if "raw_gain" in frame.columns and "inverse_gain" in frame.columns:
        frame["raw_better"] = frame["raw_gain"].astype(float).gt(frame["inverse_gain"].astype(float)).astype(int)
        frame["signed_gain_margin"] = frame["raw_gain"].astype(float) - frame["inverse_gain"].astype(float)
        frame["best_counterfactual_gain"] = frame[["raw_gain", "inverse_gain"]].max(axis=1)
        frame["both_toxic"] = frame["best_counterfactual_gain"].astype(float).lt(0.0).astype(int)
        frame["direction_confidence"] = frame["signed_gain_margin"].abs()
    return frame.loc[:, ~frame.columns.duplicated()].copy()


def direction_feature_families(train: pd.DataFrame, test: pd.DataFrame) -> dict[str, list[str]]:
    listener = [col for col in target_listener_columns(train) if col in test.columns]
    human = [
        col
        for col in train.columns
        if col in test.columns
        and pd.api.types.is_numeric_dtype(train[col])
        and (
            col.startswith("human_state_latent_")
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
        )
    ]
    pretext = [
        col
        for col in train.columns
        if col in test.columns
        and pd.api.types.is_numeric_dtype(train[col])
        and (col.startswith("pretext_pred_") or col.startswith("pretext_energy_"))
    ]
    responsibility = [col for col in ["responsibility_score"] if col in train.columns and col in test.columns]
    action_geometry = [
        col
        for col in [
            "raw_candidate_prob",
            "raw_inverse_prob",
            "raw_action_move",
            "inverse_candidate_prob",
            "inverse_inverse_prob",
            "inverse_action_move",
        ]
        if col in train.columns and col in test.columns
    ]
    return {
        "listener_only_direction": list(dict.fromkeys(listener)),
        "human_context_direction": list(dict.fromkeys(listener + human)),
        "masked_pretext_direction": list(dict.fromkeys(listener + pretext)),
        "responsibility_weighted_pretext_direction": list(dict.fromkeys(listener + responsibility + pretext)),
        "human_plus_masked_pretext_direction": list(dict.fromkeys(listener + responsibility + human + pretext)),
        "action_geometry_reference": list(dict.fromkeys(listener + action_geometry)),
    }


def fit_oof_scores(
    train: pd.DataFrame,
    test: pd.DataFrame,
    features: list[str],
) -> tuple[np.ndarray, np.ndarray, list[dict[str, Any]]]:
    features = list(dict.fromkeys(features))
    groups = train["subject_id"].astype(str).to_numpy()
    y = train["raw_better"].astype(int).to_numpy()
    weight = 1.0 + np.minimum(train["direction_confidence"].to_numpy(dtype=np.float64) / 0.05, 8.0)
    splitter = GroupKFold(n_splits=max(2, min(5, len(np.unique(groups)))))
    oof = np.zeros(len(train), dtype=np.float64)
    fold_rows: list[dict[str, Any]] = []
    for fold, (tr, va) in enumerate(splitter.split(train, y, groups=groups)):
        y_tr = y[tr]
        if len(np.unique(y_tr)) < 2 or not features:
            pred = np.full(len(va), float(y_tr.mean()) if len(y_tr) else 0.5)
        else:
            model = classifier_factory(RANDOM_SEED + fold)
            model.fit(train.iloc[tr].loc[:, features], y_tr, histgradientboostingclassifier__sample_weight=weight[tr])
            pred = model.predict_proba(train.iloc[va].loc[:, features])[:, 1]
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
        test_score = np.full(len(test), float(y.mean()) if len(y) else 0.5)
    else:
        model = classifier_factory(RANDOM_SEED + 303)
        model.fit(train.loc[:, features], y, histgradientboostingclassifier__sample_weight=weight)
        test_score = model.predict_proba(test.loc[:, features])[:, 1]
    return np.clip(oof, 1e-5, 1.0 - 1e-5), np.clip(test_score, 1e-5, 1.0 - 1e-5), fold_rows


def select_cells_by_release_laws(cells: pd.DataFrame, release_laws: pd.DataFrame, budget_col: str) -> set[int]:
    selected: set[int] = set()
    for _, law in release_laws[release_laws["accepted"].astype(bool)].iterrows():
        target = str(law["target"])
        budget = max(1, int(law[budget_col]))
        part = cells[cells["target"].eq(target)].sort_values("responsibility_score", ascending=False).head(budget)
        selected.update(part["cell_id"].astype(int).tolist())
    return selected


def direction_gain(cells: pd.DataFrame, score: np.ndarray, selected_cell_ids: set[int] | None) -> dict[str, Any]:
    frame = cells.copy()
    frame["direction_score"] = score
    if selected_cell_ids is not None:
        frame = frame[frame["cell_id"].isin(selected_cell_ids)]
    if frame.empty:
        return {
            "cells": 0,
            "gain_sum": 0.0,
            "mean_gain": 0.0,
            "positive_rate": 0.0,
            "raw_rate": 0.0,
            "both_toxic_rate": 0.0,
        }
    choose_raw = frame["direction_score"].astype(float).ge(0.5)
    gain = np.where(choose_raw, frame["raw_gain"].astype(float), frame["inverse_gain"].astype(float))
    return {
        "cells": int(len(frame)),
        "gain_sum": float(np.sum(gain)),
        "mean_gain": float(np.mean(gain)),
        "positive_rate": float(np.mean(gain > 0.0)),
        "raw_rate": float(np.mean(choose_raw)),
        "both_toxic_rate": float(frame["both_toxic"].astype(int).mean()),
    }


def evaluate_direction(
    train_cells: pd.DataFrame,
    test_cells: pd.DataFrame,
    release_laws: pd.DataFrame,
    families: dict[str, list[str]],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, np.ndarray], dict[str, np.ndarray]]:
    y = train_cells["raw_better"].astype(int).to_numpy()
    responsibility_cells = select_cells_by_release_laws(train_cells, release_laws, "heldout_selected_cells")
    oracle_cells = set(train_cells[train_cells["listener_responsible"].astype(int).eq(1)]["cell_id"].astype(int).tolist())
    metric_rows: list[dict[str, Any]] = []
    target_rows: list[dict[str, Any]] = []
    fold_rows: list[dict[str, Any]] = []
    test_scores: dict[str, np.ndarray] = {}
    oof_scores: dict[str, np.ndarray] = {}
    for family_name, features in families.items():
        oof, test_score, folds = fit_oof_scores(train_cells, test_cells, features)
        oof_scores[family_name] = oof
        test_scores[family_name] = test_score
        ap = safe_ap(y, oof)
        all_gain = direction_gain(train_cells, oof, None)
        resp_gain = direction_gain(train_cells, oof, responsibility_cells)
        oracle_gain = direction_gain(train_cells, oof, oracle_cells)
        metric_rows.append(
            {
                "feature_family": family_name,
                "feature_count": len(features),
                "raw_better_rate": float(y.mean()),
                "auc": safe_auc(y, oof),
                "ap": ap,
                "ap_lift_vs_rate": float(ap - y.mean()) if ap is not None else None,
                "all_cells": all_gain["cells"],
                "all_gain_sum": all_gain["gain_sum"],
                "all_positive_rate": all_gain["positive_rate"],
                "all_raw_rate": all_gain["raw_rate"],
                "responsibility_cells": resp_gain["cells"],
                "responsibility_gain_sum": resp_gain["gain_sum"],
                "responsibility_positive_rate": resp_gain["positive_rate"],
                "responsibility_raw_rate": resp_gain["raw_rate"],
                "oracle_cells": oracle_gain["cells"],
                "oracle_gain_sum": oracle_gain["gain_sum"],
                "oracle_positive_rate": oracle_gain["positive_rate"],
            }
        )
        for fold in folds:
            fold["feature_family"] = family_name
            fold_rows.append(fold)
        for target in TARGETS:
            part = train_cells[train_cells["target"].eq(target)]
            idx = part.index.to_numpy()
            target_gain = direction_gain(part, oof[idx], None)
            yt = part["raw_better"].astype(int).to_numpy()
            st = oof[idx]
            target_rows.append(
                {
                    "feature_family": family_name,
                    "target": target,
                    "raw_better_rate": float(yt.mean()),
                    "auc": safe_auc(yt, st),
                    "ap": safe_ap(yt, st),
                    "direction_gain_sum": target_gain["gain_sum"],
                    "direction_positive_rate": target_gain["positive_rate"],
                    "direction_raw_rate": target_gain["raw_rate"],
                }
            )
    return pd.DataFrame(metric_rows), pd.DataFrame(target_rows), pd.DataFrame(fold_rows), test_scores, oof_scores


def baseline_direction_rows(train_cells: pd.DataFrame, release_laws: pd.DataFrame) -> pd.DataFrame:
    responsibility_cells = select_cells_by_release_laws(train_cells, release_laws, "heldout_selected_cells")
    raw_score = np.ones(len(train_cells), dtype=np.float64)
    inverse_score = np.zeros(len(train_cells), dtype=np.float64)
    oracle_score = train_cells["raw_better"].astype(float).to_numpy()
    rows = []
    for name, score in [
        ("always_raw", raw_score),
        ("always_inverse", inverse_score),
        ("oracle_direction", oracle_score),
    ]:
        all_gain = direction_gain(train_cells, score, None)
        resp_gain = direction_gain(train_cells, score, responsibility_cells)
        rows.append(
            {
                "baseline": name,
                "all_gain_sum": all_gain["gain_sum"],
                "all_positive_rate": all_gain["positive_rate"],
                "responsibility_gain_sum": resp_gain["gain_sum"],
                "responsibility_positive_rate": resp_gain["positive_rate"],
                "responsibility_raw_rate": resp_gain["raw_rate"],
            }
        )
    return pd.DataFrame(rows)


def build_candidate(
    sample: pd.DataFrame,
    test_cells: pd.DataFrame,
    release_laws: pd.DataFrame,
    train_priors: dict[str, float],
    test_score: np.ndarray,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    out = sample.copy()
    for target in TARGETS:
        out[target] = float(train_priors[target])
    selected_cell_ids = select_cells_by_release_laws(test_cells, release_laws, "test_budget")
    audit = test_cells.copy()
    audit["direction_score"] = test_score
    audit["released"] = audit["cell_id"].isin(selected_cell_ids)
    audit["selected_action"] = False
    for idx, row in audit[audit["released"]].iterrows():
        choose_raw = float(row["direction_score"]) >= 0.5
        out.at[int(row["row"]), str(row["target"])] = float(
            row["raw_action_prob"] if choose_raw else row["inverse_action_prob"]
        )
        audit.at[idx, "selected_action"] = True
        audit.at[idx, "selected_decoder_action"] = "raw_memory_release" if choose_raw else "inverse_toxic_memory"
    out[TARGETS] = out[TARGETS].clip(1e-5, 1.0 - 1e-5)
    return out, audit


def build_markdown(
    summary: dict[str, Any],
    metrics: pd.DataFrame,
    target_metrics: pd.DataFrame,
    fold_metrics: pd.DataFrame,
    baselines: pd.DataFrame,
    release_counts: pd.DataFrame,
) -> str:
    ranked = metrics.sort_values(["responsibility_gain_sum", "ap_lift_vs_rate"], ascending=[False, False])
    target_ranked = target_metrics.sort_values(["feature_family", "direction_gain_sum"], ascending=[True, False])
    return f"""# Counterfactual Direction Pretext Core

## 한 줄 요약

raw/inverse action 방향 선택을 adapter heuristic으로 두지 않고,
HS-JEPA의 hidden target representation으로 끌어올릴 수 있는지 검증했다.

```text
visible human-state context + target listener
  -> counterfactual direction representation
  -> responsibility-high row-target cell에서 raw 또는 inverse 선택
```

## 왜 필요한가

직전 signed-direction 실험은 action translation 독성을 수리했지만,
best family가 `action_geometry_direction`이었다.
즉 점수 관점에서는 좋아도 논문 관점에서는 pure HS-JEPA core 증거가 약했다.

이번 실험은 같은 문제를 cell-level counterfactual target으로 다시 정의했다.

```text
hidden target = raw gain > inverse gain 인가?
```

core feature는 action probability, action magnitude, previous submission probability, public LB를 쓰지 않는다.
`action_geometry_reference`는 adapter reference로만 보고한다.

## 사용하지 않은 정보

- public LB ledger: `{summary["uses_public_score_ledger"]}`
- prior submission probabilities: `{summary["uses_prior_submission_probabilities"]}`
- proprietary embedding API: `{summary["uses_proprietary_embedding_api"]}`
- action probability as core feature: `{summary["uses_action_probability_as_core_feature"]}`
- label-informed peer margin: `{summary["uses_label_informed_peer_margin"]}`

## Verdict

- verdict: `{summary["verdict"]}`
- responsibility source: `{summary["responsibility_source_family"]}`
- best overall family: `{summary["best_overall_family"]}`
- best core family: `{summary["best_core_family"]}`
- best core AP lift: `{format_float(summary["best_core_ap_lift"], 6)}`
- best core responsibility-gated gain: `{format_float(summary["best_core_responsibility_gain_sum"], 6)}`
- action-geometry reference gain: `{format_float(summary["action_geometry_reference_gain_sum"], 6)}`
- oracle responsibility-gated gain: `{format_float(summary["oracle_responsibility_gain_sum"], 6)}`
- released test cells: `{summary["released_test_cells"]}`
- candidate: `{summary["candidate_file"]}`

## Direction Family Leaderboard

{markdown_table(ranked, ["feature_family", "feature_count", "raw_better_rate", "auc", "ap", "ap_lift_vs_rate", "all_gain_sum", "responsibility_gain_sum", "responsibility_positive_rate", "responsibility_raw_rate"], max_rows=30)}

## Baselines

{markdown_table(baselines, ["baseline", "all_gain_sum", "all_positive_rate", "responsibility_gain_sum", "responsibility_positive_rate", "responsibility_raw_rate"], max_rows=10)}

## Target-Level Direction Metrics

{markdown_table(target_ranked, ["feature_family", "target", "raw_better_rate", "auc", "ap", "direction_gain_sum", "direction_positive_rate", "direction_raw_rate"], max_rows=90)}

## Fold Stability

{markdown_table(fold_metrics, ["feature_family", "fold", "heldout_subjects", "positive_rate", "auc", "ap"], max_rows=90)}

## Release Counts

{markdown_table(release_counts, ["target", "count"], max_rows=20)}

## 해석

좋은 결과:

```text
best core family가 action_geometry_reference에 근접하거나 responsibility-gated gain이 양수면,
HS-JEPA core가 어디를 볼지뿐 아니라 raw/inverse 방향 표현까지 일부 복원한다는 뜻이다.
```

나쁜 결과:

```text
action_geometry_reference만 강하고 core families가 약하면,
현재 HS-JEPA core는 listener responsibility까지는 좋지만 signed direction은 아직 adapter 영역이다.
```
"""


def run() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    action_train, action_test, cell_train, release_laws, responsibility_family = prepare_frames()
    train_cells = build_counterfactual_cells(action_train)
    test_cells = build_counterfactual_cells(action_test)
    families = direction_feature_families(train_cells, test_cells)
    metrics, target_metrics, fold_metrics, test_scores, _oof_scores = evaluate_direction(
        train_cells,
        test_cells,
        release_laws,
        families,
    )
    baselines = baseline_direction_rows(train_cells, release_laws)

    core_metrics = metrics[metrics["feature_family"].isin(CORE_DIRECTION_FAMILIES)].copy()
    best_core = core_metrics.sort_values(["responsibility_gain_sum", "ap_lift_vs_rate"], ascending=[False, False]).iloc[0]
    best_overall = metrics.sort_values(["responsibility_gain_sum", "ap_lift_vs_rate"], ascending=[False, False]).iloc[0]
    action_reference_gain = float(
        metrics.loc[metrics["feature_family"].eq("action_geometry_reference"), "responsibility_gain_sum"].iloc[0]
    )
    oracle_gain = float(baselines.loc[baselines["baseline"].eq("oracle_direction"), "responsibility_gain_sum"].iloc[0])
    train_priors = action_train.groupby("target", observed=True)["target_prior"].first().astype(float).to_dict()
    sample = pd.read_csv(SAMPLE_SUBMISSION)
    candidate, release_audit = build_candidate(
        sample,
        test_cells,
        release_laws,
        train_priors,
        test_scores[str(best_core["feature_family"])],
    )
    validation = validate_submission(candidate, sample)
    if not validation["valid"]:
        raise ValueError(f"candidate is not upload-safe: {validation['problems']}")
    candidate_name = f"submission_hsjepa_counterfactual_direction_pretext_{short_hash(candidate)}_uploadsafe.csv"
    release_counts = (
        release_audit[release_audit["selected_action"]].groupby("target", observed=True).size().reset_index(name="count")
    )
    best_core_gain = float(best_core["responsibility_gain_sum"])
    if best_core_gain > 0.0 and best_core_gain >= 0.5 * action_reference_gain:
        verdict = "counterfactual_direction_pretext_core_positive"
    elif best_core_gain > 0.0:
        verdict = "counterfactual_direction_pretext_core_weak_positive"
    elif action_reference_gain > 0.0:
        verdict = "counterfactual_direction_remains_adapter_boundary"
    else:
        verdict = "counterfactual_direction_pretext_negative"
    summary = {
        "package": "counterfactual_direction_pretext_core",
        "status": "counterfactual_direction_pretext_core_ready",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "uses_action_probability_as_core_feature": False,
        "uses_label_informed_peer_margin": False,
        "verdict": verdict,
        "responsibility_source_family": responsibility_family,
        "best_overall_family": str(best_overall["feature_family"]),
        "best_core_family": str(best_core["feature_family"]),
        "best_core_ap_lift": float(best_core["ap_lift_vs_rate"]),
        "best_core_responsibility_gain_sum": best_core_gain,
        "action_geometry_reference_gain_sum": action_reference_gain,
        "oracle_responsibility_gain_sum": oracle_gain,
        "released_test_cells": int(release_audit["selected_action"].sum()),
        "release_targets": release_counts["target"].astype(str).tolist() if not release_counts.empty else [],
        "candidate_file": candidate_name,
        "validation": validation,
    }

    metrics.to_csv(OUT_DIR / "counterfactual_direction_family_metrics.csv", index=False)
    target_metrics.to_csv(OUT_DIR / "counterfactual_direction_target_metrics.csv", index=False)
    fold_metrics.to_csv(OUT_DIR / "counterfactual_direction_fold_metrics.csv", index=False)
    baselines.to_csv(OUT_DIR / "counterfactual_direction_baselines.csv", index=False)
    release_audit.to_csv(OUT_DIR / "counterfactual_direction_release_audit.csv", index=False)
    release_counts.to_csv(OUT_DIR / "counterfactual_direction_release_counts.csv", index=False)
    candidate.to_csv(OUT_DIR / candidate_name, index=False)
    candidate.to_csv(ROOT / candidate_name, index=False)
    (OUT_DIR / "counterfactual_direction_pretext_core_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    md = build_markdown(summary, metrics, target_metrics, fold_metrics, baselines, release_counts)
    (OUT_DIR / "COUNTERFACTUAL_DIRECTION_PRETEXT_CORE_KO.md").write_text(md, encoding="utf-8")
    PAPER_DOC.write_text(md, encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


if __name__ == "__main__":
    run()
