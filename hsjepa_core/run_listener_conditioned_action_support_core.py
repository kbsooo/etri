#!/usr/bin/env python3
"""Listener-conditioned action-support core stress for HS-JEPA.

This public-free experiment follows from the view-invariance stress:

* HS-JEPA residual/energy world state is stronger than target/action-only
  shortcuts for action support.
* Target-blind world state is not enough.

So this script tests the architecture claim directly:

    visible human context
      -> masked world-state residual/energy
      -> listener-conditioned action-support prediction
      -> anchor-free row-target correction sensor

The action-support target is built only from train labels:

    raw lifelog KNN action vs train-fold prior
    -> realized OOF logloss gain
    -> positive/toxic action-support target

No public LB ledger, previous submission probabilities, or proprietary
embedding APIs are used.
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
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hsjepa_core.run_action_support_world_model_core import (  # noqa: E402
    NEIGHBORS,
    RANDOM_SEED,
    TARGETS,
    append_row_features,
    choose_release_policy,
    fit_support_models,
    knn_probability_field,
    make_action_cell_table,
    make_test_action_table,
    score_support_predictions,
    target_context_columns,
    validate_submission,
)
from hsjepa_core.run_lifelog_core_state_evidence import (  # noqa: E402
    catalog_features,
    finite_matrix,
    format_float,
    load_frames,
    markdown_table,
)
from hsjepa_core.run_masked_context_world_model import build_world_model_state  # noqa: E402


OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "listener_conditioned_action_support_core"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "LISTENER_CONDITIONED_ACTION_SUPPORT_CORE_KO.md"
SAMPLE_SUBMISSION = ROOT / "data" / "ch2026_submission_sample.csv"
NULL_REPEATS = 32


def short_hash(frame: pd.DataFrame) -> str:
    return hashlib.sha256(frame[TARGETS].to_numpy(dtype=np.float64).round(10).tobytes()).hexdigest()[:8]


def stable_seed(*parts: object) -> int:
    key = "::".join(map(str, parts)).encode("utf-8")
    return RANDOM_SEED + int(hashlib.sha256(key).hexdigest()[:8], 16) % 1009


def state_feature_columns(state: pd.DataFrame) -> dict[str, list[str]]:
    pred = [col for col in state.columns if col.startswith("wm_pred_")]
    resid = [col for col in state.columns if col.startswith("wm_resid_")]
    energy = [col for col in state.columns if col.startswith("wm_energy")]
    return {
        "pred": pred,
        "resid": resid,
        "energy": energy,
        "resid_energy": resid + energy,
        "full": pred + resid + energy,
    }


def add_listener_interactions(
    train_cells: pd.DataFrame,
    test_cells: pd.DataFrame,
    base_cols: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, list[str]]]:
    train_parts = []
    test_parts = []
    interaction_groups = {
        "family_interaction": ["is_q_target", "is_s_target", "is_q2_q3_s2", "is_objective_tail"],
        "target_interaction": [f"target_onehot_{target}" for target in TARGETS],
    }
    out_cols: dict[str, list[str]] = {}
    for group_name, gates in interaction_groups.items():
        cols: list[str] = []
        for gate in gates:
            if gate not in train_cells.columns:
                continue
            train_gate = train_cells[gate].astype(float).to_numpy()
            test_gate = test_cells[gate].astype(float).to_numpy()
            for col in base_cols:
                new_col = f"{group_name}__{gate}__{col}"
                train_parts.append(pd.Series(train_gate * train_cells[col].astype(float).to_numpy(), name=new_col))
                test_parts.append(pd.Series(test_gate * test_cells[col].astype(float).to_numpy(), name=new_col))
                cols.append(new_col)
        out_cols[group_name] = cols
    train_interactions = pd.concat(train_parts, axis=1) if train_parts else pd.DataFrame(index=train_cells.index)
    test_interactions = pd.concat(test_parts, axis=1) if test_parts else pd.DataFrame(index=test_cells.index)
    train = pd.concat([train_cells.reset_index(drop=True), train_interactions.reset_index(drop=True)], axis=1)
    test = pd.concat([test_cells.reset_index(drop=True), test_interactions.reset_index(drop=True)], axis=1)
    return train, test, out_cols


def model_factory(seed: int) -> Any:
    return make_pipeline(
        SimpleImputer(strategy="median"),
        HistGradientBoostingClassifier(
            learning_rate=0.035,
            max_leaf_nodes=10,
            min_samples_leaf=14,
            l2_regularization=0.22,
            random_state=seed,
        ),
    )


def fit_partition_listener_scores(
    train_cells: pd.DataFrame,
    test_cells: pd.DataFrame,
    cols: list[str],
    partition_col: str,
    feature_name: str,
) -> tuple[np.ndarray, np.ndarray]:
    groups = train_cells["subject_id"].astype(str).to_numpy()
    y = train_cells["positive_gain"].astype(int).to_numpy()
    oof = np.full(len(train_cells), np.nan, dtype=np.float64)
    test_score = np.full(len(test_cells), np.nan, dtype=np.float64)
    for part_name, part_index in train_cells.groupby(partition_col, observed=True).groups.items():
        part_idx = np.asarray(list(part_index), dtype=int)
        if len(part_idx) < 40:
            continue
        part_groups = groups[part_idx]
        splitter = GroupKFold(n_splits=max(2, min(5, len(np.unique(part_groups)))))
        for fold, (tr_rel, va_rel) in enumerate(splitter.split(train_cells.iloc[part_idx], groups=part_groups)):
            tr = part_idx[tr_rel]
            va = part_idx[va_rel]
            y_tr = y[tr]
            if len(np.unique(y_tr)) < 2:
                oof[va] = float(y_tr.mean())
                continue
            model = model_factory(stable_seed(feature_name, part_name, fold))
            model.fit(train_cells.iloc[tr][cols], y_tr)
            oof[va] = model.predict_proba(train_cells.iloc[va][cols])[:, 1]
        test_idx = test_cells.index[test_cells[partition_col].eq(part_name)].to_numpy()
        if len(test_idx) == 0 or len(np.unique(y[part_idx])) < 2:
            continue
        model = model_factory(stable_seed(feature_name, part_name, "test"))
        model.fit(train_cells.iloc[part_idx][cols], y[part_idx])
        test_score[test_idx] = model.predict_proba(test_cells.iloc[test_idx][cols])[:, 1]

    fallback = float(np.nanmean(oof)) if np.isfinite(oof).any() else float(y.mean())
    oof = np.where(np.isfinite(oof), oof, fallback)
    test_score = np.where(np.isfinite(test_score), test_score, fallback)
    return oof, test_score


def fit_target_heldout_transfer_score(
    train_cells: pd.DataFrame,
    test_cells: pd.DataFrame,
    cols: list[str],
    feature_name: str,
) -> tuple[np.ndarray, np.ndarray]:
    y = train_cells["positive_gain"].astype(int).to_numpy()
    oof = np.zeros(len(train_cells), dtype=np.float64)
    for target in TARGETS:
        train_idx = train_cells.index[~train_cells["target"].eq(target)].to_numpy()
        valid_idx = train_cells.index[train_cells["target"].eq(target)].to_numpy()
        y_tr = y[train_idx]
        if len(np.unique(y_tr)) < 2:
            oof[valid_idx] = float(y_tr.mean())
            continue
        model = model_factory(stable_seed(feature_name, target))
        model.fit(train_cells.iloc[train_idx][cols], y_tr)
        oof[valid_idx] = model.predict_proba(train_cells.iloc[valid_idx][cols])[:, 1]

    test_score_acc = np.zeros(len(test_cells), dtype=np.float64)
    model_count = 0
    for target in TARGETS:
        train_idx = train_cells.index[~train_cells["target"].eq(target)].to_numpy()
        y_tr = y[train_idx]
        if len(np.unique(y_tr)) < 2:
            continue
        model = model_factory(stable_seed(feature_name, target, "test"))
        model.fit(train_cells.iloc[train_idx][cols], y_tr)
        test_score_acc += model.predict_proba(test_cells[cols])[:, 1]
        model_count += 1
    if model_count == 0:
        test_score = np.full(len(test_cells), float(y.mean()), dtype=np.float64)
    else:
        test_score = test_score_acc / model_count
    return oof, test_score


def score_with_null(train_cells: pd.DataFrame, score_map: dict[str, np.ndarray]) -> pd.DataFrame:
    rng = np.random.default_rng(RANDOM_SEED + 404)
    rows: list[dict[str, Any]] = []
    for feature_name, score in score_map.items():
        rows.extend(score_support_predictions(train_cells, score, feature_name, "observed"))
        for repeat in range(NULL_REPEATS):
            shuffled = np.asarray(score, dtype=np.float64).copy()
            for target in TARGETS:
                idx = np.where(train_cells["target"].eq(target).to_numpy())[0]
                values = shuffled[idx].copy()
                rng.shuffle(values)
                shuffled[idx] = values
            rows.extend(score_support_predictions(train_cells, shuffled, feature_name, f"target_shuffle_null_{repeat:02d}"))
    metrics = pd.DataFrame(rows)
    observed = metrics[metrics["null_family"].eq("observed")].copy()
    null = metrics[metrics["null_family"].ne("observed")].copy()
    if not null.empty:
        null_summary = (
            null.groupby(["feature_set", "selection_policy", "decoder_action"], observed=True)
            .agg(null_gain_mean=("selected_gain_sum", "mean"), null_gain_std=("selected_gain_sum", "std"))
            .reset_index()
        )
        observed = observed.merge(null_summary, on=["feature_set", "selection_policy", "decoder_action"], how="left")
        observed["gain_lift_vs_null"] = observed["selected_gain_sum"] - observed["null_gain_mean"]
        observed["gain_z_vs_null"] = (
            observed["selected_gain_sum"] - observed["null_gain_mean"]
        ) / observed["null_gain_std"].replace(0, np.nan)
    return observed


def add_robust_score(metrics: pd.DataFrame) -> pd.DataFrame:
    out = metrics.copy()
    out["robust_score"] = (
        out["selected_gain_sum"].fillna(0.0)
        + 0.25 * out.get("gain_lift_vs_null", 0.0).fillna(0.0)
        + 0.08 * out.get("gain_z_vs_null", 0.0).fillna(0.0)
        + 0.25 * out["selected_positive_gain_rate"].fillna(0.0)
    )
    return out


def summarize_listener_family(metrics: pd.DataFrame) -> pd.DataFrame:
    observed = metrics[metrics["null_family"].eq("observed")].copy()
    rows: list[dict[str, Any]] = []
    for feature_set, part in observed.groupby("feature_set", observed=True):
        best = part.sort_values(["robust_score", "selected_gain_sum"], ascending=False).iloc[0]
        if feature_set.startswith("per_target_"):
            listener_family = "per_target"
        elif feature_set.startswith("per_family_"):
            listener_family = "per_family"
        elif feature_set.startswith("target_heldout_"):
            listener_family = "target_heldout_transfer"
        elif "interaction" in feature_set:
            listener_family = "explicit_interaction"
        elif "target_blind" in feature_set:
            listener_family = "target_blind"
        else:
            listener_family = "global_or_baseline"
        rows.append(
            {
                "feature_set": feature_set,
                "listener_family": listener_family,
                "best_policy": best["selection_policy"],
                "best_decoder_action": best["decoder_action"],
                "support_auc": best["support_auc"],
                "support_ap": best["support_ap"],
                "selected_cells": int(best["selected_cells"]),
                "selected_gain_sum": float(best["selected_gain_sum"]),
                "selected_positive_gain_rate": float(best["selected_positive_gain_rate"]),
                "gain_lift_vs_null": float(best.get("gain_lift_vs_null", np.nan)),
                "gain_z_vs_null": float(best.get("gain_z_vs_null", np.nan)),
                "robust_score": float(best["robust_score"]),
            }
        )
    return pd.DataFrame(rows).sort_values(["robust_score", "selected_gain_sum"], ascending=False)


def select_policy_indices(cells: pd.DataFrame, score_col: str, policy: dict[str, Any]) -> np.ndarray:
    score = cells[score_col].to_numpy(dtype=np.float64)
    fraction = float(policy["release_fraction"])
    selection_policy = str(policy["selection_policy"])
    decisive_only = bool(policy["decisive_only"])
    descending = not selection_policy.startswith("low")
    idx = cells.index.to_numpy()
    if decisive_only:
        idx = idx[cells.loc[idx, "decisive_action"].eq(1).to_numpy()]
    if len(idx) == 0:
        return np.array([], dtype=int)
    k = max(1, int(round(len(idx) * fraction)))
    order_key = -score[idx] if descending else score[idx]
    return idx[np.argsort(order_key, kind="mergesort")[:k]]


def target_gain_table(train_cells: pd.DataFrame, score_col: str, policy: dict[str, Any]) -> pd.DataFrame:
    decoder = str(policy["decoder_action"])
    selected = select_policy_indices(train_cells, score_col, policy)
    gain_col = "realized_gain" if decoder == "raw_memory_release" else "inverse_realized_gain"
    rows = []
    selected_frame = train_cells.loc[selected].copy()
    for target, part in selected_frame.groupby("target", observed=True):
        gains = part[gain_col].to_numpy(dtype=np.float64)
        rows.append(
            {
                "target": target,
                "selected_cells": int(len(part)),
                "selected_gain_sum": float(gains.sum()),
                "selected_mean_gain": float(gains.mean()),
                "selected_positive_gain_rate": float((gains > 0).mean()),
            }
        )
    return pd.DataFrame(rows)


def build_policy_matched_candidate(
    sample: pd.DataFrame,
    test_cells: pd.DataFrame,
    score_col: str,
    policy: dict[str, Any],
    train_priors: dict[str, float],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    out = sample.copy()
    for target in TARGETS:
        out[target] = float(train_priors[target])
    selected = np.zeros(len(test_cells), dtype=bool)
    selected_indices = select_policy_indices(test_cells, score_col, policy)
    selected[selected_indices] = True
    decoder = str(policy["decoder_action"])
    value_col = "candidate_prob" if decoder == "raw_memory_release" else "inverse_prob"
    audit = test_cells.copy()
    audit["released"] = selected
    audit["decoder_action"] = decoder
    audit["selection_policy"] = str(policy["selection_policy"])
    for _, row in audit[audit["released"]].iterrows():
        out.at[int(row["row"]), str(row["target"])] = float(row[value_col])
    out[TARGETS] = out[TARGETS].clip(1e-5, 1.0 - 1e-5)
    return out, audit


def verdict(summary_table: pd.DataFrame) -> str:
    baseline = summary_table[summary_table["feature_set"].eq("target_action_only")]
    global_world = summary_table[summary_table["feature_set"].eq("global_world_residual_energy")]
    best_listener = summary_table[summary_table["listener_family"].isin(["per_target", "explicit_interaction"])]
    heldout = summary_table[summary_table["listener_family"].eq("target_heldout_transfer")]
    if baseline.empty or global_world.empty or best_listener.empty:
        return "missing_required_comparison"
    baseline_gain = float(baseline.iloc[0]["selected_gain_sum"])
    global_gain = float(global_world.iloc[0]["selected_gain_sum"])
    listener_gain = float(best_listener.iloc[0]["selected_gain_sum"])
    heldout_gain = float(heldout.iloc[0]["selected_gain_sum"]) if not heldout.empty else np.nan
    if listener_gain > global_gain + 1.0 and heldout_gain > baseline_gain:
        return "listener_conditioning_positive_with_target_transfer_support"
    if listener_gain > global_gain + 1.0:
        return "listener_conditioning_positive_but_target_transfer_unproven"
    if global_gain > baseline_gain + 2.0:
        return "global_world_state_positive_listener_conditioning_not_needed"
    return "listener_conditioning_not_stronger_than_baseline"


def build_markdown(
    summary: dict[str, Any],
    listener_summary: pd.DataFrame,
    metrics: pd.DataFrame,
    target_table: pd.DataFrame,
) -> str:
    top_metrics = metrics[metrics["null_family"].eq("observed")].sort_values(
        ["robust_score", "selected_gain_sum"], ascending=False
    )
    return f"""# Listener-Conditioned Action-Support Core

## 한 줄 요약

target-blind world state가 약했던 이유를 검증하기 위해,
HS-JEPA world-state residual/energy를 listener-conditioned action-support predictor로 바꿨다.

```text
visible human context
  -> masked world-state residual/energy
  -> target/family listener-conditioned support prediction
  -> anchor-free row-target correction sensor
```

## 왜 core 실험인가

이 실험은 public LB, 기존 best submission probability, public score ledger를 쓰지 않는다.
action-support target은 train label에서만 만든다.

```text
raw lifelog KNN action vs train-fold prior
  -> realized logloss gain
  -> positive/toxic action-support target
```

이전 stress에서 target-blind world state는 target/action baseline보다 낫지만 positive gain까지는 못 갔다.
이번 실험은 그 병목이 `listener가 없는 decoder` 때문인지 확인한다.

## 사용하지 않은 정보

- public LB ledger: `{summary["uses_public_score_ledger"]}`
- prior submission probability: `{summary["uses_prior_submission_probabilities"]}`
- proprietary embedding API: `{summary["uses_proprietary_embedding_api"]}`

## Verdict

- verdict: `{summary["verdict"]}`
- selected feature set: `{summary["release_policy"]["feature_set"]}`
- selected policy: `{summary["release_policy"]["selection_policy"]}`
- selected decoder: `{summary["release_policy"]["decoder_action"]}`
- selected gain sum: `{format_float(summary["release_policy"]["selected_gain_sum"], 6)}`
- gain lift vs target-shuffle null: `{format_float(summary["release_policy"].get("gain_lift_vs_null"), 6)}`
- gain z vs target-shuffle null: `{format_float(summary["release_policy"].get("gain_z_vs_null"), 6)}`
- released test cells: `{summary["released_test_cells"]}`

## Listener Summary

{markdown_table(listener_summary, ["feature_set", "listener_family", "best_policy", "best_decoder_action", "support_auc", "support_ap", "selected_cells", "selected_gain_sum", "selected_positive_gain_rate", "gain_lift_vs_null", "gain_z_vs_null", "robust_score"], max_rows=40)}

## Target Gain For Selected Listener

{markdown_table(target_table, ["target", "selected_cells", "selected_gain_sum", "selected_mean_gain", "selected_positive_gain_rate"], max_rows=20)}

## Full Metric Leaderboard

{markdown_table(top_metrics, ["feature_set", "selection_policy", "decoder_action", "release_fraction", "support_auc", "support_ap", "selected_cells", "selected_gain_sum", "selected_positive_gain_rate", "gain_lift_vs_null", "gain_z_vs_null", "robust_score"], max_rows=36)}

## Anchor-Free Candidate

- candidate: `{summary["candidate_file"]}`
- validation: `{summary["validation"]}`

이 후보는 leaderboard anchor를 쓰지 않는다.
train prior에서 시작하고, selected listener-conditioned support model이 release-worthy라고 판단한
raw-memory row-target action을 decoder에 따라 release하거나 inverse-toxic 방향으로 움직인다.

## 해석

성공 조건:

```text
listener-conditioned world-state predictor가 target/action-only baseline과
global world-state baseline을 모두 이기고, target-heldout transfer가 baseline보다 나쁘지 않아야 한다.
```

실패 조건:

```text
per-target listener만 좋아지고 target-heldout transfer가 무너지면,
이 신호는 general HS-JEPA listener가 아니라 target-specific memorization일 수 있다.
```

현재 결론:

```text
HS-JEPA core는 target-free decoder가 아니라 listener-conditioned action-support world model로 정립해야 한다.
```
"""


def run() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frame, _ = load_frames()
    frame = frame.copy()
    state, view_metrics, _pred_cols, _energy_cols = build_world_model_state(frame)
    catalog = catalog_features(frame)
    raw_cols = [col for col in catalog.raw_numeric if col in frame.columns]

    train = frame[frame["split"].eq("train")].reset_index(drop=True)
    test = frame[frame["split"].eq("test")].reset_index(drop=True)
    state_train = state[state["split"].eq("train")].reset_index(drop=True)
    state_test = state[state["split"].eq("test")].reset_index(drop=True)
    groups = train["subject_id"].astype(str).to_numpy()

    raw_oof, raw_test_field = knn_probability_field(
        train,
        test,
        finite_matrix(train, raw_cols),
        finite_matrix(test, raw_cols),
        groups,
        NEIGHBORS,
    )
    raw_cells = make_action_cell_table(train, raw_oof, "raw_lifelog_memory")
    train_cells = raw_cells.copy()

    sfc = state_feature_columns(state)
    state_cols = sorted(set(sfc["full"]))
    train_cells = append_row_features(train_cells, state_train[["metric_row"] + state_cols], state_cols)
    train_cells["target_family"] = np.where(train_cells["target"].str.startswith("Q"), "Q", "S")
    train_cells.loc[train_cells["target"].isin(["Q2", "Q3", "S2"]), "target_family"] = "Q2Q3S2"
    train_cells.loc[train_cells["target"].isin(["S1", "S3", "S4"]), "target_family"] = "objective_tail"

    train_priors = train[TARGETS].astype(float).mean().to_dict()
    test_cells = make_test_action_table(test, raw_test_field, train_priors, "raw_lifelog_memory")
    test_cells = append_row_features(test_cells, state_test[["metric_row"] + state_cols], state_cols)
    test_cells["target_family"] = np.where(test_cells["target"].str.startswith("Q"), "Q", "S")
    test_cells.loc[test_cells["target"].isin(["Q2", "Q3", "S2"]), "target_family"] = "Q2Q3S2"
    test_cells.loc[test_cells["target"].isin(["S1", "S3", "S4"]), "target_family"] = "objective_tail"

    action_cols = ["action_move", "abs_action_move", "action_move_rank"]
    target_cols = target_context_columns()
    world_cols = sfc["resid_energy"]
    train_cells, test_cells, interaction_cols = add_listener_interactions(train_cells, test_cells, world_cols)

    global_feature_map = {
        "target_action_only": target_cols + action_cols,
        "target_blind_world_residual_energy": action_cols + world_cols,
        "global_world_residual_energy": target_cols + action_cols + world_cols,
        "family_interaction_world_residual_energy": target_cols
        + action_cols
        + world_cols
        + interaction_cols["family_interaction"],
        "target_interaction_world_residual_energy": target_cols
        + action_cols
        + world_cols
        + interaction_cols["target_interaction"],
    }
    global_metrics, global_oof, global_test = fit_support_models(train_cells, test_cells, global_feature_map)
    global_metrics = add_robust_score(global_metrics)

    custom_scores: dict[str, np.ndarray] = {}
    custom_test_scores: dict[str, np.ndarray] = {}
    listener_cols = action_cols + world_cols
    for partition_col, prefix in [("target", "per_target"), ("target_family", "per_family")]:
        oof_score, test_score = fit_partition_listener_scores(
            train_cells,
            test_cells,
            listener_cols,
            partition_col,
            f"{prefix}_world_residual_energy",
        )
        custom_scores[f"{prefix}_world_residual_energy"] = oof_score
        custom_test_scores[f"{prefix}_world_residual_energy"] = test_score

    transfer_cols = target_cols + action_cols + world_cols
    oof_transfer, test_transfer = fit_target_heldout_transfer_score(
        train_cells,
        test_cells,
        transfer_cols,
        "target_heldout_world_residual_energy",
    )
    custom_scores["target_heldout_world_residual_energy"] = oof_transfer
    custom_test_scores["target_heldout_world_residual_energy"] = test_transfer

    custom_metrics = add_robust_score(score_with_null(train_cells, custom_scores))
    metrics = pd.concat([global_metrics, custom_metrics], ignore_index=True, sort=False)
    metrics = add_robust_score(metrics)

    oof_predictions = global_oof.copy()
    test_predictions = global_test.copy()
    for name, score in custom_scores.items():
        oof_predictions[f"support_score_{name}"] = score
    for name, score in custom_test_scores.items():
        test_predictions[f"support_score_{name}"] = score

    release_policy = choose_release_policy(metrics)
    listener_summary = summarize_listener_family(metrics)

    release_feature = str(release_policy["feature_set"])
    score_col = f"support_score_{release_feature}"
    target_table = target_gain_table(oof_predictions, score_col, release_policy)

    sample = pd.read_csv(SAMPLE_SUBMISSION)
    candidate, test_release_audit = build_policy_matched_candidate(
        sample,
        test_predictions,
        score_col,
        release_policy,
        train_priors,
    )
    validation = validate_submission(candidate, sample)
    if not validation["valid"]:
        raise ValueError(f"candidate is not upload-safe: {validation['problems']}")
    candidate_name = f"submission_hsjepa_listener_conditioned_action_support_anchor_free_{short_hash(candidate)}_uploadsafe.csv"

    summary = {
        "package": "listener_conditioned_action_support_core",
        "status": "listener_conditioned_core_stress_ready",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "action_support_target": "raw_lifelog_memory_vs_train_fold_prior_realized_gain",
        "verdict": verdict(listener_summary),
        "release_policy": release_policy,
        "candidate_file": candidate_name,
        "validation": validation,
        "released_test_cells": int(test_release_audit["released"].sum()),
        "best_masked_view_component_corr_lift": float(view_metrics["component_corr_lift_vs_null"].max()),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(OUT_DIR / "listener_conditioned_support_prediction_metrics.csv", index=False)
    listener_summary.to_csv(OUT_DIR / "listener_conditioned_feature_summary.csv", index=False)
    target_table.to_csv(OUT_DIR / "listener_conditioned_target_gain.csv", index=False)
    oof_predictions.to_csv(OUT_DIR / "listener_conditioned_oof_support_predictions.csv", index=False)
    test_predictions.to_csv(OUT_DIR / "listener_conditioned_test_support_predictions.csv", index=False)
    test_release_audit.to_csv(OUT_DIR / "listener_conditioned_test_release_audit.csv", index=False)
    candidate.to_csv(OUT_DIR / candidate_name, index=False)
    candidate.to_csv(ROOT / candidate_name, index=False)
    (OUT_DIR / "listener_conditioned_action_support_core_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    md = build_markdown(summary, listener_summary, metrics, target_table)
    (OUT_DIR / "LISTENER_CONDITIONED_ACTION_SUPPORT_CORE_KO.md").write_text(md.rstrip() + "\n", encoding="utf-8")
    PAPER_DOC.write_text(md.rstrip() + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
