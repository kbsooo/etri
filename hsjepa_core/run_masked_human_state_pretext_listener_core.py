#!/usr/bin/env python3
"""Masked human-state pretext listener core probe for HS-JEPA.

Open-loop raw human-state features were better than action geometry, but weaker
than a listener-only baseline.  This script tests the next HS-JEPA hypothesis:

    The problem is not the absence of human-state signal.
    The problem is giving raw human-state features directly to the decoder.

We therefore build a JEPA-style pretext representation before the action-health
probe:

    visible lifelog views
      -> predict masked human-state view representation
      -> predicted/residual/surprise state
      -> minimal listener-conditioned action-health support

No public LB ledger, prior submission probabilities, proprietary embedding APIs,
masked-tail teacher score as feature, or label-informed peer margins are used as
core features.  The strict subject-invariant jury is used only as the probe
target, not as an input feature.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import average_precision_score, r2_score, roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hsjepa_core.run_action_support_world_model_core import TARGETS, validate_submission  # noqa: E402
from hsjepa_core.run_lifelog_core_state_evidence import (  # noqa: E402
    catalog_features,
    component_correlation,
    finite_matrix,
    format_float,
    markdown_table,
    rank01,
    view_columns,
)
from sleep_competition_adapter.target_route_conservation_decoder import SAMPLE_SUBMISSION, short_hash  # noqa: E402


OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "masked_human_state_pretext_listener_core"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "MASKED_HUMAN_STATE_PRETEXT_LISTENER_CORE_KO.md"
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


def target_transform(
    frame: pd.DataFrame,
    cols: list[str],
    dims: int,
) -> tuple[np.ndarray, SimpleImputer, StandardScaler, PCA]:
    y_imp = SimpleImputer(strategy="median")
    y_scaler = StandardScaler()
    y_scaled = y_scaler.fit_transform(y_imp.fit_transform(finite_matrix(frame, cols)))
    n_components = max(1, min(dims, y_scaled.shape[1], y_scaled.shape[0] - 1))
    pca = PCA(n_components=n_components, random_state=RANDOM_SEED)
    y_state = pca.fit_transform(y_scaled)
    return y_state, y_imp, y_scaler, pca


def apply_target_transform(
    frame: pd.DataFrame,
    cols: list[str],
    y_imp: SimpleImputer,
    y_scaler: StandardScaler,
    pca: PCA,
) -> np.ndarray:
    y_scaled = y_scaler.transform(y_imp.transform(finite_matrix(frame, cols)))
    return pca.transform(y_scaled)


def fit_predict_ridge(train_x: pd.DataFrame, train_y: np.ndarray, predict_x: pd.DataFrame) -> np.ndarray:
    model = make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(),
        Ridge(alpha=18.0),
    )
    model.fit(train_x, train_y)
    return np.asarray(model.predict(predict_x), dtype=np.float64)


def build_masked_pretext_state(features: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, list[str], list[str]]:
    """Build OOF train and train-fitted test masked-view human-state representation."""
    clean = features[
        [
            col
            for col in features.columns
            if not any(col.startswith(prefix) for prefix in LABEL_INFORMED_PREFIXES)
        ]
    ].copy()
    catalog = catalog_features(clean)
    views = view_columns(catalog)
    all_view_cols = sorted({col for cols in views.values() for col in cols})
    train = clean[clean["split"].eq("train")].reset_index(drop=True)
    test = clean[clean["split"].eq("test")].reset_index(drop=True)
    groups = train["subject_id"].astype(str).to_numpy()
    splitter = GroupKFold(n_splits=max(2, min(5, len(np.unique(groups)))))

    train_state = train[["subject_id", "sleep_date", "lifelog_date", "metric_row"]].copy()
    test_state = test[["subject_id", "sleep_date", "lifelog_date", "metric_row"]].copy()
    pretext_rows: list[dict[str, Any]] = []
    state_cols: list[str] = []
    energy_cols: list[str] = []

    for target_view, y_cols in views.items():
        x_cols = [col for col in all_view_cols if col not in set(y_cols)]
        if len(x_cols) < 2:
            continue
        y_state, y_imp, y_scaler, pca = target_transform(train, y_cols, dims=4)
        test_y_state = apply_target_transform(test, y_cols, y_imp, y_scaler, pca)
        train_pred = np.zeros_like(y_state)
        for fold, (tr, va) in enumerate(splitter.split(train, groups=groups)):
            train_pred[va] = fit_predict_ridge(
                finite_matrix(train.iloc[tr], x_cols),
                y_state[tr],
                finite_matrix(train.iloc[va], x_cols),
            )
        test_pred = fit_predict_ridge(finite_matrix(train, x_cols), y_state, finite_matrix(test, x_cols))
        train_resid = y_state - train_pred
        test_resid = test_y_state - test_pred
        train_energy = np.sqrt(np.mean(np.square(train_resid), axis=1))
        test_energy = np.sqrt(np.mean(np.square(test_resid), axis=1))

        for comp in range(y_state.shape[1]):
            pred_col = f"pretext_pred_{target_view}_c{comp + 1}"
            resid_col = f"pretext_resid_{target_view}_c{comp + 1}"
            state_cols.extend([pred_col, resid_col])
            train_state[pred_col] = train_pred[:, comp]
            test_state[pred_col] = test_pred[:, comp]
            train_state[resid_col] = train_resid[:, comp]
            test_state[resid_col] = test_resid[:, comp]
        energy_col = f"pretext_energy_{target_view}"
        rank_col = f"pretext_energy_rank_{target_view}"
        energy_cols.extend([energy_col, rank_col])
        train_state[energy_col] = train_energy
        test_state[energy_col] = test_energy
        train_state[rank_col] = rank01(train_energy)
        test_state[rank_col] = rank01(test_energy)
        pretext_rows.append(
            {
                "target_view": target_view,
                "context_feature_count": len(x_cols),
                "target_feature_count": len(y_cols),
                "components": int(y_state.shape[1]),
                "oof_r2": float(r2_score(y_state, train_pred, multioutput="variance_weighted")),
                "oof_component_corr": component_correlation(y_state, train_pred),
                "train_energy_mean": float(np.mean(train_energy)),
                "test_energy_mean": float(np.mean(test_energy)),
                "uses_public_score": False,
                "uses_train_labels": False,
                "uses_label_informed_features": False,
            }
        )

    raw_energy = [col for col in energy_cols if "_rank_" not in col]
    rank_energy = [col for col in energy_cols if "_rank_" in col]
    train_state["pretext_energy_mean"] = train_state[raw_energy].mean(axis=1)
    test_state["pretext_energy_mean"] = test_state[raw_energy].mean(axis=1)
    train_state["pretext_energy_max"] = train_state[raw_energy].max(axis=1)
    test_state["pretext_energy_max"] = test_state[raw_energy].max(axis=1)
    train_state["pretext_energy_rank_mean"] = train_state[rank_energy].mean(axis=1)
    test_state["pretext_energy_rank_mean"] = test_state[rank_energy].mean(axis=1)
    train_state["pretext_energy_rank_max"] = train_state[rank_energy].max(axis=1)
    test_state["pretext_energy_rank_max"] = test_state[rank_energy].max(axis=1)
    state_cols.extend(
        energy_cols
        + [
            "pretext_energy_mean",
            "pretext_energy_max",
            "pretext_energy_rank_mean",
            "pretext_energy_rank_max",
        ]
    )
    state = pd.concat(
        [
            train_state.assign(split="train"),
            test_state.assign(split="test"),
        ],
        ignore_index=True,
    )
    return state, pd.DataFrame(pretext_rows), state_cols, energy_cols


def load_frames() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, float], pd.DataFrame, list[str]]:
    parent_train = pd.read_csv(PARENT_OUT_DIR / "masked_view_consensus_full_oof_action_audit.csv")
    parent_test = pd.read_csv(PARENT_OUT_DIR / "masked_view_consensus_test_release_audit.csv")
    strict = pd.read_csv(JURY_OUT_DIR / "subject_invariant_jury_strict_subjectheldout_audit.csv")
    release_laws = pd.read_csv(JURY_OUT_DIR / "subject_invariant_jury_release_laws.csv")
    features = pd.read_csv(FEATURE_PATH)
    pretext_state, pretext_metrics, pretext_cols, _energy_cols = build_masked_pretext_state(features)

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
    prior_col = "target_prior" if "target_prior" in train.columns else "prior_prob"
    train_priors = train.groupby("target", observed=True)[prior_col].first().astype(float).to_dict()
    return train, test, release_laws, train_priors, pretext_metrics, pretext_cols


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
    human_numeric = human_numeric_columns(train, test)
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
        if col in train.columns and col in test.columns
    ]
    pretext_pred = [col for col in pretext_cols if col.startswith("pretext_pred_")]
    pretext_resid = [col for col in pretext_cols if col.startswith("pretext_resid_")]
    pretext_energy = [col for col in pretext_cols if col.startswith("pretext_energy_")]
    return {
        "listener_only": list(dict.fromkeys(minimal_listener)),
        "action_geometry_only": list(dict.fromkeys(action_geometry)),
        "open_loop_human_state_listener": list(dict.fromkeys(human_numeric + minimal_listener)),
        "masked_pretext_prediction_listener": list(dict.fromkeys(pretext_pred + pretext_energy + minimal_listener)),
        "masked_pretext_residual_listener": list(dict.fromkeys(pretext_resid + pretext_energy + minimal_listener)),
        "masked_pretext_full_listener": list(dict.fromkeys(pretext_cols + minimal_listener)),
        "human_plus_masked_pretext_listener": list(dict.fromkeys(human_numeric + pretext_cols + minimal_listener)),
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


def evaluate(
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
    release_family: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    out = sample.copy()
    for target in TARGETS:
        out[target] = float(train_priors[target])
    score_col = f"score__{release_family}__strict_jury_released"
    audit = test.copy()
    audit["masked_pretext_release_score"] = test_scores[score_col]
    released = pd.Series(False, index=audit.index)
    for _, law in release_laws.iterrows():
        if not bool(law["accepted"]):
            continue
        target = str(law["target"])
        part = audit[audit["target"].eq(target)].copy()
        part = part.sort_values(["masked_pretext_release_score", "decisive_action"], ascending=[False, False])
        part = part.drop_duplicates("cell_id", keep="first").head(int(law["test_budget"]))
        released.loc[part.index] = True
    audit["released"] = released.to_numpy(dtype=bool)
    for _, row in audit[audit["released"]].iterrows():
        out.at[int(row["row"]), str(row["target"])] = float(row["action_prob"])
    out[TARGETS] = out[TARGETS].clip(1e-5, 1.0 - 1e-5)
    return out, audit


def build_markdown(
    summary: dict[str, Any],
    pretext_metrics: pd.DataFrame,
    metrics: pd.DataFrame,
    target_metrics: pd.DataFrame,
    fold_metrics: pd.DataFrame,
    release_counts: pd.DataFrame,
) -> str:
    strict = metrics[metrics["label_task"].eq("strict_jury_released")].sort_values("ap_lift_vs_rate", ascending=False)
    strict_targets = target_metrics[target_metrics["label_task"].eq("strict_jury_released")].sort_values(
        ["feature_family", "ap_lift_vs_rate"],
        ascending=[True, False],
    )
    return f"""# Masked Human-State Pretext Listener Core

## 한 줄 요약

raw human-state feature를 그대로 decoder에 넣지 않고, 먼저 JEPA-style masked-view
pretext representation을 만든 뒤 subject-invariant action-health support를 읽는지 검증했다.

```text
visible lifelog views
  -> predict masked human-state view representation
  -> predicted/residual/surprise state
  -> listener-conditioned action-health support
```

## 왜 필요한 실험인가

`Open-Loop Human-State Listener Core`는 raw OG human-state가 action-only보다 낫지만
listener-only를 이기지 못한다는 경계 결과였다. 이 실험은 그 실패가
human-state 자체의 부재 때문인지, 아니면 representation화하지 않은 raw feature decoder 때문인지
반증한다.

## 사용하지 않은 정보

- public LB ledger: `{summary["uses_public_score_ledger"]}`
- prior submission probability: `{summary["uses_prior_submission_probabilities"]}`
- proprietary embedding API: `{summary["uses_proprietary_embedding_api"]}`
- masked-tail teacher score as feature: `{summary["uses_masked_tail_teacher_score"]}`
- label-informed peer margin as feature: `{summary["uses_label_informed_peer_margin"]}`

## Verdict

- verdict: `{summary["verdict"]}`
- best strict-jury family: `{summary["best_strict_jury_family"]}`
- masked-pretext AP lift: `{format_float(summary["masked_pretext_ap_lift"], 6)}`
- open-loop AP lift: `{format_float(summary["open_loop_ap_lift"], 6)}`
- listener-only AP lift: `{format_float(summary["listener_only_ap_lift"], 6)}`
- action-only AP lift: `{format_float(summary["action_only_ap_lift"], 6)}`
- release family: `{summary["release_family"]}`
- released test cells: `{summary["released_test_cells"]}`
- candidate: `{summary["candidate_file"]}`

## Masked-View Pretext Metrics

{markdown_table(pretext_metrics, ["target_view", "context_feature_count", "target_feature_count", "components", "oof_r2", "oof_component_corr", "train_energy_mean", "test_energy_mean"], max_rows=20)}

## Strict Jury Release Leaderboard

{markdown_table(strict, ["feature_family", "label_task", "feature_count", "positive_rate", "auc", "ap", "ap_lift_vs_rate"], max_rows=30)}

## Target-Level Strict Jury Release Metrics

{markdown_table(strict_targets, ["feature_family", "target", "positive_rate", "auc", "ap", "ap_lift_vs_rate"], max_rows=100)}

## Fold Stability

{markdown_table(fold_metrics, ["feature_family", "label_task", "fold", "heldout_subjects", "positive_rate", "auc", "ap"], max_rows=100)}

## Release Counts

{markdown_table(release_counts, ["target", "count"], max_rows=20)}

## 해석

좋은 결과:

```text
masked pretext state가 listener-only/open-loop raw human-state를 넘으면,
HS-JEPA core의 핵심은 raw feature가 아니라 masked human-state world model이라는 주장이 강화된다.
```

나쁜 결과:

```text
masked pretext state도 listener-only를 못 넘으면,
현재 core-only representation은 아직 subject-invariant action-health를 독립적으로 복원하지 못한다.
그 경우 strong evidence는 hidden-tail/listener manifold 쪽에 남는다.
```
"""


def run() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    train, test, release_laws, train_priors, pretext_metrics, pretext_cols = load_frames()
    families = feature_families(train, test, pretext_cols)
    metrics, target_metrics, fold_metrics, test_scores = evaluate(train, test, families)

    strict = metrics[metrics["label_task"].eq("strict_jury_released")].copy()
    get_lift = lambda name: float(strict.loc[strict["feature_family"].eq(name), "ap_lift_vs_rate"].iloc[0])
    masked_family_candidates = [
        "masked_pretext_full_listener",
        "masked_pretext_residual_listener",
        "masked_pretext_prediction_listener",
        "human_plus_masked_pretext_listener",
    ]
    masked_best = strict[strict["feature_family"].isin(masked_family_candidates)].sort_values(
        "ap_lift_vs_rate",
        ascending=False,
    ).iloc[0]
    masked_lift = float(masked_best["ap_lift_vs_rate"])
    open_loop_lift = get_lift("open_loop_human_state_listener")
    listener_lift = get_lift("listener_only")
    action_lift = get_lift("action_geometry_only")
    best = strict.sort_values("ap_lift_vs_rate", ascending=False).iloc[0]
    if masked_lift > max(listener_lift, open_loop_lift, action_lift):
        verdict = "masked_pretext_human_state_positive"
    elif masked_lift > open_loop_lift:
        verdict = "masked_pretext_improves_raw_human_state_but_not_listener_only"
    elif masked_lift > action_lift:
        verdict = "masked_pretext_beats_action_but_not_raw_open_loop"
    else:
        verdict = "masked_pretext_human_state_negative"

    release_family = str(masked_best["feature_family"])
    sample = pd.read_csv(SAMPLE_SUBMISSION)
    candidate, release_audit = release_candidate(
        sample,
        test,
        release_laws,
        train_priors,
        test_scores,
        release_family=release_family,
    )
    validation = validate_submission(candidate, sample)
    if not validation["valid"]:
        raise ValueError(f"candidate is not upload-safe: {validation['problems']}")
    candidate_name = f"submission_hsjepa_masked_human_state_pretext_listener_anchor_free_{short_hash(candidate)}_uploadsafe.csv"
    release_counts = release_audit[release_audit["released"]].groupby("target", observed=True).size().reset_index(name="count")
    summary = {
        "package": "masked_human_state_pretext_listener_core",
        "status": "masked_human_state_pretext_listener_core_ready",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "uses_masked_tail_teacher_score": False,
        "uses_label_informed_peer_margin": False,
        "verdict": verdict,
        "best_strict_jury_family": str(best["feature_family"]),
        "best_strict_jury_ap_lift": float(best["ap_lift_vs_rate"]),
        "best_masked_pretext_family": str(masked_best["feature_family"]),
        "masked_pretext_ap_lift": masked_lift,
        "open_loop_ap_lift": open_loop_lift,
        "listener_only_ap_lift": listener_lift,
        "action_only_ap_lift": action_lift,
        "release_family": release_family,
        "released_test_cells": int(release_audit["released"].sum()),
        "release_targets": release_counts["target"].astype(str).tolist() if not release_counts.empty else [],
        "candidate_file": candidate_name,
        "validation": validation,
    }

    pretext_metrics.to_csv(OUT_DIR / "masked_human_state_pretext_metrics.csv", index=False)
    metrics.to_csv(OUT_DIR / "masked_human_state_pretext_listener_metrics.csv", index=False)
    target_metrics.to_csv(OUT_DIR / "masked_human_state_pretext_listener_target_metrics.csv", index=False)
    fold_metrics.to_csv(OUT_DIR / "masked_human_state_pretext_listener_fold_metrics.csv", index=False)
    release_audit.to_csv(OUT_DIR / "masked_human_state_pretext_listener_release_audit.csv", index=False)
    release_counts.to_csv(OUT_DIR / "masked_human_state_pretext_listener_release_counts.csv", index=False)
    candidate.to_csv(OUT_DIR / candidate_name, index=False)
    candidate.to_csv(ROOT / candidate_name, index=False)
    (OUT_DIR / "masked_human_state_pretext_listener_core_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    md = build_markdown(summary, pretext_metrics, metrics, target_metrics, fold_metrics, release_counts)
    (OUT_DIR / "MASKED_HUMAN_STATE_PRETEXT_LISTENER_CORE_KO.md").write_text(md, encoding="utf-8")
    PAPER_DOC.write_text(md, encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


if __name__ == "__main__":
    run()
