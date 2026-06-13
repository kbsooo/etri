#!/usr/bin/env python3
"""HS-JEPA listener-conditioned route readout diagnostic.

This experiment keeps the HS-JEPA core label-free, then asks a downstream
question with frozen probes:

    do different Q/S listeners read different hidden human-state routes?

The core representation is the route-preserving multi-target bundle:
routine-break, sleep-pressure, and cohort-relative predicted states.  Labels are
used only after the representation is frozen, to select a route readout per
target/listener under subject-heldout validation.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hsjepa_core.human_state_world_model import finite_frame  # noqa: E402
from hsjepa_core.run_human_state_world_model_core import (  # noqa: E402
    PROBE_CALIBRATION_SHRINK,
    calibrated_probe_metrics,
    chronological_folds,
    evaluate_split,
    make_linear_probe,
    make_views,
    subject_folds,
    subject_leakage_probe,
)
from hsjepa_core.run_lifelog_core_state_evidence import (  # noqa: E402
    TARGETS,
    catalog_features,
    format_float,
    load_frames,
    markdown_table,
    safe_auc,
)
from hsjepa_core.run_multi_target_human_state_world_model_core import (  # noqa: E402
    build_multi_target_world_state,
)
from hsjepa_core.run_sleep_pressure_world_model_core import json_safe  # noqa: E402


OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "listener_conditioned_route_readout_core"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "LISTENER_CONDITIONED_ROUTE_READOUT_CORE_KO.md"
SAMPLE_SUBMISSION = ROOT / "data" / "ch2026_submission_sample.csv"


def short_hash(frame: pd.DataFrame) -> str:
    arr = frame[TARGETS].to_numpy(dtype=np.float64)
    return hashlib.sha256(np.round(arr, 10).tobytes()).hexdigest()[:8]


def build_route_feature_sets(colsets: dict[str, list[str]]) -> dict[str, list[str]]:
    routine = colsets["routine_break_predicted"]
    sleep = colsets["sleep_pressure_predicted"]
    cohort = colsets["cohort_relative_predicted"]
    return {
        "routine_break_route": routine,
        "sleep_pressure_route": sleep,
        "cohort_relative_route": cohort,
        "routine_sleep_pair": sorted(set(routine + sleep)),
        "routine_cohort_pair": sorted(set(routine + cohort)),
        "sleep_cohort_pair": sorted(set(sleep + cohort)),
        "multi_target_predicted": colsets["multi_target_predicted"],
    }


def select_listener_routes(calibrated_metrics: pd.DataFrame, candidate_names: set[str]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    subject = calibrated_metrics[
        calibrated_metrics["split"].eq("subject_heldout")
        & calibrated_metrics["target"].isin(TARGETS)
        & calibrated_metrics["feature_set"].isin(candidate_names)
    ].copy()
    for target, part in subject.groupby("target", observed=True):
        ordered = part.sort_values("logloss")
        best = ordered.iloc[0]
        multi = part[part["feature_set"].eq("multi_target_predicted_calibrated10")]
        rows.append(
            {
                "target": target,
                "selected_feature_set": str(best["feature_set"]).replace("_calibrated10", ""),
                "selected_logloss": float(best["logloss"]),
                "selected_auc": None if pd.isna(best["auc"]) else float(best["auc"]),
                "multi_target_logloss": None if multi.empty else float(multi["logloss"].iloc[0]),
                "delta_vs_multi_target": None if multi.empty else float(best["logloss"] - multi["logloss"].iloc[0]),
            }
        )
    return pd.DataFrame(rows)


def listener_selected_probe_metrics(
    predictions: pd.DataFrame,
    selection: pd.DataFrame,
    shrink: float = PROBE_CALIBRATION_SHRINK,
) -> pd.DataFrame:
    selected = dict(zip(selection["target"], selection["selected_feature_set"]))
    rows: list[dict[str, Any]] = []
    for split, split_part in predictions.groupby("split", observed=True):
        losses = []
        aucs = []
        for target in TARGETS:
            feature_set = selected[target]
            part = split_part[
                split_part["target"].eq(target)
                & split_part["feature_set"].eq(feature_set)
            ].copy()
            y = part["y"].to_numpy(dtype=int)
            raw = part["prediction"].to_numpy(dtype=np.float64)
            prior = part["fold_prior"].to_numpy(dtype=np.float64)
            pred = np.clip(prior + shrink * (raw - prior), 1e-5, 1 - 1e-5)
            loss = float(log_loss(y, pred, labels=[0, 1]))
            auc = safe_auc(y, pred)
            losses.append(loss)
            if auc is not None:
                aucs.append(auc)
            rows.append(
                {
                    "split": split,
                    "feature_set": "listener_conditioned_route_readout_calibrated10",
                    "target": target,
                    "logloss": loss,
                    "auc": auc,
                    "selected_feature_set": feature_set,
                    "uses_public_score": False,
                    "uses_train_labels": True,
                    "core_representation_frozen": True,
                    "listener_route_selected_from": "subject_heldout_calibrated_probe",
                    "probe_calibration_shrink": shrink,
                    "evaluated_rows": int(len(part)),
                }
            )
        rows.append(
            {
                "split": split,
                "feature_set": "listener_conditioned_route_readout_calibrated10",
                "target": "all",
                "logloss": float(np.mean(losses)),
                "auc": float(np.nanmean(aucs)) if aucs else None,
                "selected_feature_set": "target_specific",
                "uses_public_score": False,
                "uses_train_labels": True,
                "core_representation_frozen": True,
                "listener_route_selected_from": "subject_heldout_calibrated_probe",
                "probe_calibration_shrink": shrink,
                "evaluated_rows": int(split_part["row"].nunique()),
            }
        )
    return pd.DataFrame(rows)


def listener_selection_stability(
    predictions: pd.DataFrame,
    selection: pd.DataFrame,
    shrink: float = PROBE_CALIBRATION_SHRINK,
) -> pd.DataFrame:
    selected = dict(zip(selection["target"], selection["selected_feature_set"]))
    rows: list[dict[str, Any]] = []
    subject = predictions[predictions["split"].eq("subject_heldout")]
    for target in TARGETS:
        feature_set = selected[target]
        target_part = subject[subject["target"].eq(target)]
        for fold in sorted(target_part["fold"].dropna().unique()):
            selected_part = target_part[
                target_part["fold"].eq(fold)
                & target_part["feature_set"].eq(feature_set)
            ]
            multi_part = target_part[
                target_part["fold"].eq(fold)
                & target_part["feature_set"].eq("multi_target_predicted")
            ]

            def calibrated_loss(part: pd.DataFrame) -> float:
                y = part["y"].to_numpy(dtype=int)
                raw = part["prediction"].to_numpy(dtype=np.float64)
                prior = part["fold_prior"].to_numpy(dtype=np.float64)
                pred = np.clip(prior + shrink * (raw - prior), 1e-5, 1 - 1e-5)
                return float(log_loss(y, pred, labels=[0, 1]))

            selected_loss = calibrated_loss(selected_part)
            multi_loss = calibrated_loss(multi_part)
            rows.append(
                {
                    "target": target,
                    "selected_feature_set": feature_set,
                    "fold": int(fold),
                    "selected_logloss": selected_loss,
                    "multi_target_logloss": multi_loss,
                    "delta_vs_multi_target": selected_loss - multi_loss,
                    "wins_multi_target": bool(selected_loss < multi_loss),
                }
            )
    return pd.DataFrame(rows)


def build_listener_selected_submission(
    train_frame: pd.DataFrame,
    test_frame: pd.DataFrame,
    train_features: pd.DataFrame,
    test_features: pd.DataFrame,
    selected_cols: dict[str, list[str]],
) -> pd.DataFrame:
    out = pd.read_csv(SAMPLE_SUBMISSION)
    for target in TARGETS:
        cols = selected_cols[target]
        y = train_frame[target].astype(int).to_numpy()
        prior = float(np.clip(y.mean(), 1e-5, 1 - 1e-5))
        if len(np.unique(y)) < 2:
            pred = np.full(len(test_frame), prior)
        else:
            model = make_linear_probe(f"listener_selected_{target}", len(cols))
            model.fit(finite_frame(train_features, cols), y)
            raw = model.predict_proba(finite_frame(test_features, cols))[:, 1]
            pred = prior + PROBE_CALIBRATION_SHRINK * (raw - prior)
        out[target] = np.clip(pred, 0.02, 0.98)
    expected = list(test_frame[["subject_id", "sleep_date", "lifelog_date"]].itertuples(index=False, name=None))
    actual = list(out[["subject_id", "sleep_date", "lifelog_date"]].itertuples(index=False, name=None))
    if actual != expected:
        raise ValueError("sample submission rows do not match test feature rows")
    return out


def summarize(
    probe_metrics: pd.DataFrame,
    selection: pd.DataFrame,
    stability: pd.DataFrame,
    leakage: pd.DataFrame,
    candidate_file: str,
) -> dict[str, Any]:
    subject_all = probe_metrics[(probe_metrics["split"].eq("subject_heldout")) & (probe_metrics["target"].eq("all"))]
    chrono_all = probe_metrics[(probe_metrics["split"].eq("chronological_holdout")) & (probe_metrics["target"].eq("all"))]
    prior = subject_all[subject_all["feature_set"].eq("prior_only")]
    multi = subject_all[subject_all["feature_set"].eq("multi_target_predicted_calibrated10")]
    listener = subject_all[subject_all["feature_set"].eq("listener_conditioned_route_readout_calibrated10")]
    best_subject = subject_all.sort_values("logloss").head(1)
    prior_value = None if prior.empty else float(prior["logloss"].iloc[0])
    multi_value = None if multi.empty else float(multi["logloss"].iloc[0])
    listener_value = None if listener.empty else float(listener["logloss"].iloc[0])
    route_counts = selection["selected_feature_set"].value_counts().to_dict()
    stability_summary = (
        stability.groupby(["target", "selected_feature_set"], observed=True)
        .agg(
            mean_delta_vs_multi_target=("delta_vs_multi_target", "mean"),
            win_folds_vs_multi_target=("wins_multi_target", "sum"),
            total_folds=("wins_multi_target", "size"),
        )
        .reset_index()
    )
    return {
        "package": "listener_conditioned_route_readout_core",
        "status": "listener_conditioned_route_readout_core_ready",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "uses_label_as_pretext_target": False,
        "core_representation": "route_preserving_multi_target_predicted_bundle",
        "listener_selection_layer": "frozen_probe_diagnostic",
        "subject_prior_logloss": prior_value,
        "multi_target_predicted_logloss": multi_value,
        "listener_conditioned_logloss": listener_value,
        "listener_conditioned_delta_vs_prior": None if prior_value is None or listener_value is None else listener_value - prior_value,
        "listener_conditioned_delta_vs_multi_target": None if multi_value is None or listener_value is None else listener_value - multi_value,
        "selected_route_counts": {str(key): int(value) for key, value in route_counts.items()},
        "selected_routes": selection.to_dict(orient="records"),
        "selection_stability": stability_summary.to_dict(orient="records"),
        "selection_win_folds_total": int(stability["wins_multi_target"].sum()),
        "selection_folds_total": int(len(stability)),
        "subject_best_probe": None if best_subject.empty else best_subject.iloc[0].to_dict(),
        "chronological_listener_probe": None
        if chrono_all[chrono_all["feature_set"].eq("listener_conditioned_route_readout_calibrated10")].empty
        else chrono_all[chrono_all["feature_set"].eq("listener_conditioned_route_readout_calibrated10")].iloc[0].to_dict(),
        "chronological_best_probe": None if chrono_all.empty else chrono_all.sort_values("logloss").iloc[0].to_dict(),
        "subject_leakage": leakage.to_dict(orient="records"),
        "candidate_file": candidate_file,
    }


def build_markdown(
    summary: dict[str, Any],
    probe_metrics: pd.DataFrame,
    selection: pd.DataFrame,
    stability: pd.DataFrame,
    leakage: pd.DataFrame,
    candidate_file: str,
) -> str:
    listener_delta = summary.get("listener_conditioned_delta_vs_prior")
    multi_delta = summary.get("listener_conditioned_delta_vs_multi_target")
    if listener_delta is not None and listener_delta < 0 and multi_delta is not None and multi_delta < 0:
        verdict = "listener_conditioned_readout_positive"
    elif listener_delta is not None and listener_delta < 0:
        verdict = "listener_readout_positive_but_not_multi_improving"
    else:
        verdict = "listener_readout_negative"
    subject_all = (
        probe_metrics[(probe_metrics["split"].eq("subject_heldout")) & (probe_metrics["target"].eq("all"))]
        .sort_values("logloss")
        .loc[:, ["feature_set", "logloss", "auc"]]
    )
    chrono_all = (
        probe_metrics[(probe_metrics["split"].eq("chronological_holdout")) & (probe_metrics["target"].eq("all"))]
        .sort_values("logloss")
        .loc[:, ["feature_set", "logloss", "auc"]]
    )
    return f"""# Listener-Conditioned Route Readout Core

## 한 줄 요약

HS-JEPA가 만든 route-preserving hidden bundle을 유지한 채,
각 target/listener가 어떤 route subspace를 읽는지 frozen probe로 진단한 실험이다.

```text
visible human-life context
  -> predicted routine-break / sleep-pressure / cohort-relative routes
  -> route-preserving HS-JEPA bundle
  -> target/listener-conditioned frozen readout
```

## 판정

- verdict: `{verdict}`
- public LB ledger 사용: `{summary["uses_public_score_ledger"]}`
- prior submission probability 사용: `{summary["uses_prior_submission_probabilities"]}`
- proprietary embedding API 사용: `{summary["uses_proprietary_embedding_api"]}`
- label을 pretext target으로 사용: `{summary["uses_label_as_pretext_target"]}`
- listener-conditioned delta vs prior: `{format_float(listener_delta, 6)}`
- listener-conditioned delta vs multi-target bundle: `{format_float(multi_delta, 6)}`
- selected route counts: `{summary["selected_route_counts"]}`

## 왜 이것이 HS-JEPA Core와 연결되는가

core는 여전히 label-free다.
Q/S label은 representation을 만든 뒤 frozen linear probe에서만 사용된다.

이 실험이 묻는 질문은 다음이다.

```text
HS-JEPA가 route axes를 보존했을 때,
각 target listener는 같은 route를 읽는가,
아니면 target마다 다른 hidden route를 읽는가?
```

## Target별 선택 route

{markdown_table(
    selection,
    ["target", "selected_feature_set", "selected_logloss", "multi_target_logloss", "delta_vs_multi_target"],
)}

## Fold Stability

선택된 route가 subject-heldout fold별로 multi-target bundle을 얼마나 자주 이기는지 본다.

{markdown_table(
    pd.DataFrame(summary["selection_stability"]),
    ["target", "selected_feature_set", "mean_delta_vs_multi_target", "win_folds_vs_multi_target", "total_folds"],
)}

- total selected-route wins: `{summary["selection_win_folds_total"]} / {summary["selection_folds_total"]}`

## Frozen Subject-Heldout Probe

{markdown_table(subject_all, ["feature_set", "logloss", "auc"])}

## Chronological Row-Heldout Probe

{markdown_table(chrono_all, ["feature_set", "logloss", "auc"])}

## Subject Leakage Diagnostic

{markdown_table(
    leakage.sort_values("subject_id_accuracy", ascending=False),
    ["feature_set", "subject_id_accuracy", "chance_accuracy", "leakage_lift_vs_chance"],
)}

## Downstream Probe Candidate

- file: `{candidate_file}`

이 파일은 core evidence 자체가 아니라, target/listener-specific route readout을 competition label로 번역한 probe candidate다.

## 해석

positive이면:

```text
HS-JEPA route axes는 target/listener별로 다르게 읽혀야 한다.
하나의 global bundle보다 listener-conditioned route readout이 더 좋은 representation interface다.
```

negative이면:

```text
target별 route selection은 현재 validation에서는 과적합이거나 정보 손실이다.
route-preserving bundle 자체를 유지하고, listener-conditioned readout은 더 강한 split/nesting이 필요하다.
```
"""


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frame, _labels = load_frames()
    views = make_views(frame)
    raw_cols = sorted({col for view in views for col in view.columns})
    state, _pretext_metrics, colsets = build_multi_target_world_state(frame)
    route_sets = build_route_feature_sets(colsets)
    state = pd.concat(
        [frame[["subject_id", "sleep_date", "lifelog_date", "split", "metric_row"]].reset_index(drop=True), state.reset_index(drop=True)],
        axis=1,
    )
    catalog = catalog_features(frame)
    combined = pd.concat(
        [frame.reset_index(drop=True), state.drop(columns=["subject_id", "sleep_date", "lifelog_date", "split", "metric_row"])],
        axis=1,
    )
    feature_sets = {
        "prior_only": [],
        "raw_lifelog_pca": raw_cols,
        "existing_cohort_human_state": catalog.core_state,
        **route_sets,
    }

    train_mask = frame["split"].eq("train").to_numpy()
    train_frame = frame.loc[train_mask].reset_index(drop=True)
    train_features = combined.loc[train_mask].reset_index(drop=True)
    subject_metrics, subject_predictions = evaluate_split(
        train_frame,
        train_features,
        feature_sets,
        "subject_heldout",
        subject_folds(train_frame),
    )
    chrono_metrics, chrono_predictions = evaluate_split(
        train_frame,
        train_features,
        feature_sets,
        "chronological_holdout",
        chronological_folds(train_frame),
    )
    probe_metrics = pd.concat([subject_metrics, chrono_metrics], ignore_index=True)
    probe_predictions = pd.concat([subject_predictions, chrono_predictions], ignore_index=True)
    calibrated = calibrated_probe_metrics(probe_predictions)
    selection = select_listener_routes(
        calibrated,
        {f"{name}_calibrated10" for name in route_sets},
    )
    selected_metrics = listener_selected_probe_metrics(probe_predictions, selection)
    stability = listener_selection_stability(probe_predictions, selection)
    probe_metrics = pd.concat([probe_metrics, calibrated, selected_metrics], ignore_index=True, sort=False)
    selected_map = dict(zip(selection["target"], selection["selected_feature_set"]))
    selected_cols = {target: route_sets[selected_map[target]] for target in TARGETS}
    leakage = subject_leakage_probe(
        train_frame,
        train_features,
        {
            "listener_conditioned_selected_routes": sorted(set(col for cols in selected_cols.values() for col in cols)),
            "multi_target_predicted": route_sets["multi_target_predicted"],
            "routine_break_route": route_sets["routine_break_route"],
            "sleep_pressure_route": route_sets["sleep_pressure_route"],
            "cohort_relative_route": route_sets["cohort_relative_route"],
        },
    )

    test_mask = frame["split"].eq("test").to_numpy()
    test_frame = frame.loc[test_mask].reset_index(drop=True)
    test_features = combined.loc[test_mask].reset_index(drop=True)
    submission = build_listener_selected_submission(
        train_frame,
        test_frame,
        train_features,
        test_features,
        selected_cols,
    )
    candidate_name = f"submission_hsjepa_listener_conditioned_route_readout_probe_{short_hash(submission)}_uploadsafe.csv"
    submission.to_csv(ROOT / candidate_name, index=False)
    submission.to_csv(OUT_DIR / candidate_name, index=False)

    summary = summarize(probe_metrics, selection, stability, leakage, candidate_name)
    state.to_csv(OUT_DIR / "listener_conditioned_route_readout_state.csv", index=False)
    probe_metrics.to_csv(OUT_DIR / "listener_conditioned_route_readout_probe_metrics.csv", index=False)
    probe_predictions.to_csv(OUT_DIR / "listener_conditioned_route_readout_probe_predictions.csv", index=False)
    selection.to_csv(OUT_DIR / "listener_conditioned_route_selection.csv", index=False)
    stability.to_csv(OUT_DIR / "listener_conditioned_route_selection_stability.csv", index=False)
    leakage.to_csv(OUT_DIR / "listener_conditioned_route_readout_subject_leakage.csv", index=False)
    with (OUT_DIR / "listener_conditioned_route_readout_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(json_safe(summary), handle, indent=2, ensure_ascii=False)
    markdown = build_markdown(summary, probe_metrics, selection, stability, leakage, candidate_name)
    (OUT_DIR / "LISTENER_CONDITIONED_ROUTE_READOUT_CORE_KO.md").write_text(markdown, encoding="utf-8")
    PAPER_DOC.write_text(markdown, encoding="utf-8")

    print(
        json.dumps(
            {
                "status": summary["status"],
                "candidate_file": candidate_name,
                "listener_conditioned_delta_vs_prior": summary["listener_conditioned_delta_vs_prior"],
                "listener_conditioned_delta_vs_multi_target": summary["listener_conditioned_delta_vs_multi_target"],
                "selected_route_counts": summary["selected_route_counts"],
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
