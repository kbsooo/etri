#!/usr/bin/env python3
"""View-invariance stress test for HS-JEPA action-support world state.

This is a public-free core-side stress experiment.

The previous action-support world model showed that HS-JEPA masked world
state can identify toxic raw-memory row-target actions and sometimes invert
them profitably.  This script asks a stricter question:

    Is that action-support signal a target/action shortcut, a single-view
    artifact, or a more stable hidden human-state representation?

It rebuilds the train-only action-support target, then compares:

* target/action-only support baselines
* target-blind world-state support
* single-view world-state listeners
* leave-one-view-out world-state listeners
* full masked world-state support

The generated candidate is anchor-free and starts from train priors.  It is a
diagnostic sensor, not a leaderboard-tuned release.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hsjepa_core.run_action_support_world_model_core import (  # noqa: E402
    NEIGHBORS,
    OUT_DIR as WORLD_OUT_DIR,
    TARGETS,
    append_row_features,
    build_anchor_free_candidate,
    choose_release_policy,
    fit_support_models,
    knn_probability_field,
    make_action_cell_table,
    make_test_action_table,
    reduce_features,
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


OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "action_support_view_invariance_core"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "ACTION_SUPPORT_VIEW_INVARIANCE_CORE_KO.md"
SAMPLE_SUBMISSION = ROOT / "data" / "ch2026_submission_sample.csv"


def short_hash(frame: pd.DataFrame) -> str:
    return hashlib.sha256(frame[TARGETS].to_numpy(dtype=np.float64).round(10).tobytes()).hexdigest()[:8]


def world_view_names(state: pd.DataFrame) -> list[str]:
    views = set()
    for col in state.columns:
        if col.startswith("wm_pred_"):
            body = col.removeprefix("wm_pred_")
            views.add(body.rsplit("_c", 1)[0])
    return sorted(views)


def view_columns(state: pd.DataFrame, view: str) -> list[str]:
    prefixes = [
        f"wm_pred_{view}_",
        f"wm_resid_{view}_",
        f"wm_energy_{view}",
        f"wm_energy_rank_{view}",
    ]
    return [col for col in state.columns if any(col.startswith(prefix) for prefix in prefixes)]


def all_world_columns(state: pd.DataFrame) -> dict[str, list[str]]:
    pred_cols = [col for col in state.columns if col.startswith("wm_pred_")]
    resid_cols = [col for col in state.columns if col.startswith("wm_resid_")]
    energy_cols = [col for col in state.columns if col.startswith("wm_energy")]
    return {
        "pred": pred_cols,
        "resid": resid_cols,
        "energy": energy_cols,
        "full": pred_cols + resid_cols + energy_cols,
    }


def make_feature_map(state: pd.DataFrame) -> dict[str, list[str]]:
    cols = all_world_columns(state)
    target_cols = target_context_columns()
    action_cols = ["abs_action_move", "action_move_rank"]
    family_cols = [
        "is_q_target",
        "is_s_target",
        "is_q2_q3_s2",
        "is_objective_tail",
        "target_uncertainty",
    ]
    feature_map: dict[str, list[str]] = {
        "target_action_only": target_cols + action_cols,
        "target_blind_world_full": action_cols + cols["full"],
        "target_family_world_full": action_cols + family_cols + cols["full"],
        "world_predicted_only": target_cols + action_cols + cols["pred"],
        "world_residual_energy": target_cols + action_cols + cols["resid"] + cols["energy"],
        "world_energy_only": target_cols + action_cols + cols["energy"],
        "world_full_all_views": target_cols + action_cols + cols["full"],
    }
    views = world_view_names(state)
    for view in views:
        vcols = view_columns(state, view)
        feature_map[f"single_view_{view}"] = target_cols + action_cols + vcols
        leaveout_cols = [col for col in cols["full"] if col not in set(vcols)]
        feature_map[f"leaveout_view_{view}"] = target_cols + action_cols + leaveout_cols
    return feature_map


def add_robust_score(metrics: pd.DataFrame) -> pd.DataFrame:
    out = metrics.copy()
    out["robust_score"] = (
        out["selected_gain_sum"].fillna(0.0)
        + 0.25 * out.get("gain_lift_vs_null", 0.0).fillna(0.0)
        + 0.08 * out.get("gain_z_vs_null", 0.0).fillna(0.0)
        + 0.25 * out["selected_positive_gain_rate"].fillna(0.0)
    )
    return out


def summarize_feature_families(metrics: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    observed = metrics[metrics["null_family"].eq("observed")].copy()
    for feature_set, part in observed.groupby("feature_set", observed=True):
        best = part.sort_values(["robust_score", "selected_gain_sum"], ascending=False).iloc[0]
        if feature_set.startswith("single_view_"):
            family = "single_view"
            view = feature_set.removeprefix("single_view_")
        elif feature_set.startswith("leaveout_view_"):
            family = "leaveout_view"
            view = feature_set.removeprefix("leaveout_view_")
        elif "target_blind" in feature_set:
            family = "target_blind"
            view = "all"
        elif "target_family" in feature_set:
            family = "target_family"
            view = "all"
        elif "world" in feature_set:
            family = "world_all"
            view = "all"
        else:
            family = "baseline"
            view = "none"
        rows.append(
            {
                "feature_set": feature_set,
                "family": family,
                "view": view,
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


def stress_verdict(feature_summary: pd.DataFrame) -> str:
    baseline = feature_summary[feature_summary["feature_set"].eq("target_action_only")]
    all_world = feature_summary[feature_summary["feature_set"].eq("world_full_all_views")]
    target_blind = feature_summary[feature_summary["feature_set"].eq("target_blind_world_full")]
    if baseline.empty or all_world.empty:
        return "missing_baseline"
    baseline_gain = float(baseline.iloc[0]["selected_gain_sum"])
    all_gain = float(all_world.iloc[0]["selected_gain_sum"])
    blind_gain = float(target_blind.iloc[0]["selected_gain_sum"]) if not target_blind.empty else np.nan
    if all_gain > baseline_gain + 2.0 and blind_gain > 0.0:
        return "world_state_signal_survives_target_blind_positive_stress"
    if all_gain > baseline_gain + 2.0 and blind_gain > baseline_gain:
        return "world_state_signal_positive_target_blind_weakly_survives"
    if all_gain > baseline_gain + 2.0:
        return "world_state_signal_positive_but_target_conditioned"
    return "world_state_signal_not_stronger_than_target_action_baseline"


def build_markdown(summary: dict[str, Any], feature_summary: pd.DataFrame, metrics: pd.DataFrame) -> str:
    top_metrics = metrics[metrics["null_family"].eq("observed")].sort_values(
        ["robust_score", "selected_gain_sum"], ascending=False
    )
    single_views = feature_summary[feature_summary["family"].eq("single_view")]
    leaveouts = feature_summary[feature_summary["family"].eq("leaveout_view")]
    return f"""# Action-Support View Invariance Core

## 한 줄 요약

HS-JEPA action-support 신호가 target/action shortcut인지,
특정 lifelog view 하나의 우연한 artifact인지,
아니면 masked human-state world representation에서 나온 안정적인 신호인지 stress했다.

```text
raw-memory action support target
  -> target-blind / single-view / leave-one-view-out support predictors
  -> release / inverse-toxic action pocket stability
```

## 왜 core stress인가

이 실험은 public LB, 기존 best submission probability, public score ledger를 쓰지 않는다.
action-support target은 train label에서만 만든다.

```text
raw lifelog KNN action vs train-fold prior
  -> realized logloss gain
  -> positive/toxic action-support target
```

차이는 feature set이다. target/action-only baseline, target-blind world state,
single-view world state, leave-one-view-out world state를 같은 subject-heldout stress에 넣었다.

## 사용하지 않은 정보

- public LB ledger: `{summary["uses_public_score_ledger"]}`
- prior submission probability: `{summary["uses_prior_submission_probabilities"]}`
- proprietary embedding API: `{summary["uses_proprietary_embedding_api"]}`

## Core Stress Verdict

- verdict: `{summary["verdict"]}`
- selected feature set: `{summary["release_policy"]["feature_set"]}`
- selected policy: `{summary["release_policy"]["selection_policy"]}`
- selected decoder: `{summary["release_policy"]["decoder_action"]}`
- selected gain sum: `{format_float(summary["release_policy"]["selected_gain_sum"], 6)}`
- gain lift vs target-shuffle null: `{format_float(summary["release_policy"].get("gain_lift_vs_null"), 6)}`
- gain z vs target-shuffle null: `{format_float(summary["release_policy"].get("gain_z_vs_null"), 6)}`
- released test cells: `{summary["released_test_cells"]}`

## Feature Family Summary

{markdown_table(feature_summary, ["feature_set", "family", "view", "best_policy", "best_decoder_action", "support_auc", "support_ap", "selected_cells", "selected_gain_sum", "selected_positive_gain_rate", "gain_lift_vs_null", "gain_z_vs_null", "robust_score"], max_rows=40)}

## Single View Listeners

{markdown_table(single_views, ["feature_set", "view", "best_policy", "selected_gain_sum", "selected_positive_gain_rate", "gain_lift_vs_null", "gain_z_vs_null", "robust_score"], max_rows=20)}

## Leave-One-View-Out Stress

{markdown_table(leaveouts, ["feature_set", "view", "best_policy", "selected_gain_sum", "selected_positive_gain_rate", "gain_lift_vs_null", "gain_z_vs_null", "robust_score"], max_rows=20)}

## Full Metric Leaderboard

{markdown_table(top_metrics, ["feature_set", "selection_policy", "decoder_action", "release_fraction", "support_auc", "support_ap", "selected_cells", "selected_gain_sum", "selected_positive_gain_rate", "gain_lift_vs_null", "gain_z_vs_null", "robust_score"], max_rows=32)}

## Anchor-Free Candidate

- candidate: `{summary["candidate_file"]}`
- validation: `{summary["validation"]}`

이 후보는 leaderboard anchor를 쓰지 않는다.
train prior에서 시작하고, selected view-invariance support model이 release-worthy라고 본
raw-memory action을 decoder에 따라 그대로 release하거나, inverse-toxic decoder이면
prior 기준 반대 방향으로 움직인다.

## 해석

성공 조건:

```text
world-state feature set이 target/action-only baseline보다 더 높은 selected gain과
null lift를 보이고, target-blind 또는 leave-one-view stress에서도 완전히 무너지지 않아야 한다.
```

실패 조건:

```text
target/action-only baseline이 world-state와 같거나 더 좋으면,
현재 신호는 HS-JEPA representation이 아니라 action magnitude/target prior shortcut이다.
```

현재 결론:

```text
HS-JEPA core는 direct classifier가 아니라 action-support world model이어야 하며,
이 stress는 그 신호가 어느 lifelog view와 target route에 의존하는지 분해한다.
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

    state_feature_cols = [
        col
        for col in state.columns
        if col not in {"subject_id", "sleep_date", "lifelog_date", "split", "metric_row"}
    ]
    train_cells = append_row_features(train_cells, state_train[["metric_row"] + state_feature_cols], state_feature_cols)

    train_priors = train[TARGETS].astype(float).mean().to_dict()
    test_cells = make_test_action_table(test, raw_test_field, train_priors, "raw_lifelog_memory")
    test_cells = append_row_features(test_cells, state_test[["metric_row"] + state_feature_cols], state_feature_cols)

    metrics, oof_predictions, test_predictions = fit_support_models(train_cells, test_cells, make_feature_map(state))
    metrics = add_robust_score(metrics)
    release_policy = choose_release_policy(metrics)
    feature_summary = summarize_feature_families(metrics)
    verdict = stress_verdict(feature_summary)

    sample = pd.read_csv(SAMPLE_SUBMISSION)
    candidate, test_release_audit = build_anchor_free_candidate(
        sample,
        test_predictions,
        str(release_policy["feature_set"]),
        str(release_policy["decoder_action"]),
        float(release_policy["release_fraction"]),
        train_priors,
    )
    validation = validate_submission(candidate, sample)
    if not validation["valid"]:
        raise ValueError(f"candidate is not upload-safe: {validation['problems']}")
    candidate_name = f"submission_hsjepa_action_support_view_invariance_anchor_free_{short_hash(candidate)}_uploadsafe.csv"

    summary = {
        "package": "action_support_view_invariance_core",
        "status": "core_view_invariance_stress_ready",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "action_support_target": "raw_lifelog_memory_vs_train_fold_prior_realized_gain",
        "verdict": verdict,
        "release_policy": release_policy,
        "candidate_file": candidate_name,
        "validation": validation,
        "released_test_cells": int(test_release_audit["released"].sum()),
        "best_masked_view_component_corr_lift": float(view_metrics["component_corr_lift_vs_null"].max()),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(OUT_DIR / "view_invariance_support_prediction_metrics.csv", index=False)
    feature_summary.to_csv(OUT_DIR / "view_invariance_feature_summary.csv", index=False)
    oof_predictions.to_csv(OUT_DIR / "view_invariance_oof_support_predictions.csv", index=False)
    test_predictions.to_csv(OUT_DIR / "view_invariance_test_support_predictions.csv", index=False)
    test_release_audit.to_csv(OUT_DIR / "view_invariance_test_release_audit.csv", index=False)
    candidate.to_csv(OUT_DIR / candidate_name, index=False)
    candidate.to_csv(ROOT / candidate_name, index=False)
    (OUT_DIR / "action_support_view_invariance_core_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    md = build_markdown(summary, feature_summary, metrics)
    (OUT_DIR / "ACTION_SUPPORT_VIEW_INVARIANCE_CORE_KO.md").write_text(md.rstrip() + "\n", encoding="utf-8")
    PAPER_DOC.write_text(md.rstrip() + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
