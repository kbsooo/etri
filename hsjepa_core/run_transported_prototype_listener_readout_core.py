#!/usr/bin/env python3
"""HS-JEPA transported-prototype listener readout experiment.

This experiment builds on the cross-subject prototype transport core:

    train subjects/blocks define a subject-relative episode grammar
      -> held-out rows receive transported prototype responsibilities
      -> each Q/S listener chooses which transported grammar view to read

The core target remains label-free.  Labels are used only after the transported
representation is fixed, as frozen low-trust probes that diagnose whether the
representation exposes target-specific listener interfaces.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hsjepa_core.run_cross_subject_prototype_transport_core import (  # noqa: E402
    OUT_DIR as TRANSPORT_OUT_DIR,
    row_block_folds,
    run as run_transport_core,
)
from hsjepa_core.run_human_state_world_model_core import (  # noqa: E402
    PROBE_CALIBRATION_SHRINK,
    calibrated_probe_metrics,
    chronological_folds,
    evaluate_split,
    subject_folds,
    subject_leakage_probe,
)
from hsjepa_core.run_human_state_prototype_grammar_core import PROTOTYPES_PER_VIEW  # noqa: E402
from hsjepa_core.run_lifelog_core_state_evidence import (  # noqa: E402
    TARGETS,
    catalog_features,
    format_float,
    load_frames,
    markdown_table,
    view_columns,
)


OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "transported_prototype_listener_readout_core"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "TRANSPORTED_PROTOTYPE_LISTENER_READOUT_CORE_KO.md"


def json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [json_safe(v) for v in value]
    if isinstance(value, tuple):
        return [json_safe(v) for v in value]
    if isinstance(value, np.ndarray):
        return json_safe(value.tolist())
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        if not np.isfinite(value):
            return None
        return float(value)
    return value


def ensure_transport_outputs() -> None:
    required = [
        TRANSPORT_OUT_DIR / "cross_subject_transport_state_subject_heldout.csv",
        TRANSPORT_OUT_DIR / "cross_subject_transport_state_chronological_holdout.csv",
        TRANSPORT_OUT_DIR / "cross_subject_transport_state_row_block_holdout.csv",
        TRANSPORT_OUT_DIR / "cross_subject_prototype_transport_summary.json",
    ]
    if not all(path.exists() for path in required):
        run_transport_core()


def load_transport_state(split_name: str) -> pd.DataFrame:
    ensure_transport_outputs()
    return pd.read_csv(TRANSPORT_OUT_DIR / f"cross_subject_transport_state_{split_name}.csv")


def transported_feature_sets(views: dict[str, list[str]]) -> tuple[dict[str, list[str]], set[str]]:
    pred_prob = []
    stats = []
    candidate_sets: dict[str, list[str]] = {}
    for view in views:
        view_pred = [f"cspg_pred_{view}_p{proto}" for proto in range(PROTOTYPES_PER_VIEW)]
        view_stats = [
            f"cspg_pred_{view}_confidence",
            f"cspg_pred_{view}_entropy",
            f"cspg_energy_{view}",
            f"cspg_energy_lift_{view}",
        ]
        pred_prob.extend(view_pred)
        stats.extend(view_stats)
        candidate_sets[f"listener_view_{view}_probabilities"] = view_pred
        candidate_sets[f"listener_view_{view}_stats"] = view_stats
        candidate_sets[f"listener_view_{view}_stats_probabilities"] = sorted(set(view_pred + view_stats))

    global_stats = [
        "cspg_energy_mean",
        "cspg_energy_max",
        "cspg_energy_rank_mean",
        "cspg_energy_lift_mean",
        "cspg_confidence_mean",
        "cspg_entropy_mean",
    ]
    feature_sets = {
        "transported_prototype_stats": sorted(set(stats + global_stats)),
        "transported_prototype_probabilities": sorted(set(pred_prob)),
        "transported_prototype_stats_probabilities": sorted(set(pred_prob + stats + global_stats)),
        **candidate_sets,
    }
    candidates = set(candidate_sets)
    return feature_sets, candidates


def split_folds(split_name: str, frame: pd.DataFrame) -> list[tuple[np.ndarray, np.ndarray]]:
    if split_name == "subject_heldout":
        return subject_folds(frame)
    if split_name == "chronological_holdout":
        return chronological_folds(frame)
    if split_name == "row_block_holdout":
        return row_block_folds(frame)
    raise ValueError(f"unknown split: {split_name}")


def evaluate_transport_readout_split(
    split_name: str,
    train_frame: pd.DataFrame,
    state: pd.DataFrame,
    feature_sets: dict[str, list[str]],
    raw_cols: list[str],
    calendar_cols: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    base_feature_sets = {
        "prior_only": [],
        "calendar_rhythm": calendar_cols,
        "raw_lifelog_pca": raw_cols,
        **feature_sets,
    }
    features = pd.concat([train_frame[raw_cols].reset_index(drop=True), state.reset_index(drop=True)], axis=1)
    metrics, predictions = evaluate_split(
        train_frame,
        features,
        base_feature_sets,
        split_name,
        split_folds(split_name, train_frame),
    )
    probe_metrics = pd.concat(
        [
            metrics,
            calibrated_probe_metrics(predictions, shrink=0.05),
            calibrated_probe_metrics(predictions, shrink=0.10),
        ],
        ignore_index=True,
        sort=False,
    )
    leakage = subject_leakage_probe(
        train_frame,
        features,
        {name: cols for name, cols in base_feature_sets.items() if cols},
    )
    leakage.insert(0, "split", split_name)
    return probe_metrics, predictions, leakage


def select_listener_views(calibrated_metrics: pd.DataFrame, candidate_names: set[str]) -> pd.DataFrame:
    subject = calibrated_metrics[
        calibrated_metrics["split"].eq("subject_heldout")
        & calibrated_metrics["target"].isin(TARGETS)
        & calibrated_metrics["feature_set"].isin({f"{name}_calibrated10" for name in candidate_names})
    ].copy()
    rows: list[dict[str, Any]] = []
    for target, part in subject.groupby("target", observed=True):
        ordered = part.sort_values("logloss")
        best = ordered.iloc[0]
        global_part = calibrated_metrics[
            calibrated_metrics["split"].eq("subject_heldout")
            & calibrated_metrics["target"].eq(target)
            & calibrated_metrics["feature_set"].eq("transported_prototype_stats_probabilities_calibrated10")
        ]
        rows.append(
            {
                "target": target,
                "selected_feature_set": str(best["feature_set"]).replace("_calibrated10", ""),
                "selected_logloss": float(best["logloss"]),
                "selected_auc": None if pd.isna(best["auc"]) else float(best["auc"]),
                "global_transport_logloss": None if global_part.empty else float(global_part["logloss"].iloc[0]),
                "delta_vs_global_transport": None if global_part.empty else float(best["logloss"] - global_part["logloss"].iloc[0]),
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
            try:
                from hsjepa_core.run_lifelog_core_state_evidence import safe_auc

                auc = safe_auc(y, pred)
            except Exception:
                auc = None
            losses.append(loss)
            if auc is not None:
                aucs.append(auc)
            rows.append(
                {
                    "split": split,
                    "feature_set": "listener_conditioned_transported_prototype_readout_calibrated10",
                    "target": target,
                    "logloss": loss,
                    "auc": auc,
                    "selected_feature_set": feature_set,
                    "uses_public_score": False,
                    "uses_train_labels": True,
                    "core_representation_frozen": True,
                    "listener_view_selected_from": "subject_heldout_calibrated_probe",
                    "probe_calibration_shrink": shrink,
                    "evaluated_rows": int(len(part)),
                }
            )
        rows.append(
            {
                "split": split,
                "feature_set": "listener_conditioned_transported_prototype_readout_calibrated10",
                "target": "all",
                "logloss": float(np.mean(losses)),
                "auc": float(np.nanmean(aucs)) if aucs else None,
                "selected_feature_set": "target_specific",
                "uses_public_score": False,
                "uses_train_labels": True,
                "core_representation_frozen": True,
                "listener_view_selected_from": "subject_heldout_calibrated_probe",
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
            global_part = target_part[
                target_part["fold"].eq(fold)
                & target_part["feature_set"].eq("transported_prototype_stats_probabilities")
            ]

            def calibrated_loss(part: pd.DataFrame) -> float:
                y = part["y"].to_numpy(dtype=int)
                raw = part["prediction"].to_numpy(dtype=np.float64)
                prior = part["fold_prior"].to_numpy(dtype=np.float64)
                pred = np.clip(prior + shrink * (raw - prior), 1e-5, 1 - 1e-5)
                return float(log_loss(y, pred, labels=[0, 1]))

            selected_loss = calibrated_loss(selected_part)
            global_loss = calibrated_loss(global_part)
            rows.append(
                {
                    "target": target,
                    "selected_feature_set": feature_set,
                    "fold": int(fold),
                    "selected_logloss": selected_loss,
                    "global_transport_logloss": global_loss,
                    "delta_vs_global_transport": selected_loss - global_loss,
                    "wins_global_transport": bool(selected_loss < global_loss),
                }
            )
    return pd.DataFrame(rows)


def summarize(
    probe_metrics: pd.DataFrame,
    selection: pd.DataFrame,
    stability: pd.DataFrame,
    leakage: pd.DataFrame,
) -> dict[str, Any]:
    subject_all = probe_metrics[(probe_metrics["split"].eq("subject_heldout")) & (probe_metrics["target"].eq("all"))]
    row_all = probe_metrics[(probe_metrics["split"].eq("row_block_holdout")) & (probe_metrics["target"].eq("all"))]
    chrono_all = probe_metrics[(probe_metrics["split"].eq("chronological_holdout")) & (probe_metrics["target"].eq("all"))]

    def logloss_for(frame: pd.DataFrame, name: str) -> float | None:
        part = frame[frame["feature_set"].eq(name)]
        return None if part.empty else float(part["logloss"].iloc[0])

    prior = logloss_for(subject_all, "prior_only")
    global_transport = logloss_for(subject_all, "transported_prototype_stats_probabilities_calibrated10")
    listener = logloss_for(subject_all, "listener_conditioned_transported_prototype_readout_calibrated10")
    raw = logloss_for(subject_all, "raw_lifelog_pca_calibrated10")
    row_listener = logloss_for(row_all, "listener_conditioned_transported_prototype_readout_calibrated10")
    row_global = logloss_for(row_all, "transported_prototype_stats_probabilities_calibrated10")
    chrono_listener = logloss_for(chrono_all, "listener_conditioned_transported_prototype_readout_calibrated10")
    chrono_global = logloss_for(chrono_all, "transported_prototype_stats_probabilities_calibrated10")

    stability_summary = (
        stability.groupby(["target", "selected_feature_set"], observed=True)
        .agg(
            mean_delta_vs_global=("delta_vs_global_transport", "mean"),
            win_folds_vs_global=("wins_global_transport", "sum"),
            total_folds=("wins_global_transport", "size"),
        )
        .reset_index()
    )

    route_counts = selection["selected_feature_set"].value_counts().to_dict()
    leak_subject = leakage[leakage["split"].eq("subject_heldout")]
    selected_cols = set(selection["selected_feature_set"])
    selected_leak = leak_subject[leak_subject["feature_set"].isin(selected_cols)].sort_values("subject_id_accuracy")
    global_leak = leak_subject[leak_subject["feature_set"].eq("transported_prototype_stats_probabilities")]
    raw_leak = leak_subject[leak_subject["feature_set"].eq("raw_lifelog_pca")]

    verdict = "transported_listener_readout_negative"
    if listener is not None and prior is not None and listener < prior:
        verdict = "transported_listener_readout_prior_positive"
        if global_transport is not None and listener < global_transport:
            verdict = "transported_listener_readout_global_positive"

    return {
        "package": "transported_prototype_listener_readout_core",
        "status": "transported_prototype_listener_readout_core_ready",
        "verdict": verdict,
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "uses_label_as_pretext_target": False,
        "core_representation": "cross_subject_transported_prototype_grammar",
        "listener_selection_layer": "frozen_probe_diagnostic",
        "subject_prior_logloss": prior,
        "subject_raw_logloss": raw,
        "subject_global_transport_logloss": global_transport,
        "subject_listener_conditioned_logloss": listener,
        "subject_listener_delta_vs_prior": None if listener is None or prior is None else listener - prior,
        "subject_listener_delta_vs_global_transport": None
        if listener is None or global_transport is None
        else listener - global_transport,
        "subject_listener_delta_vs_raw": None if listener is None or raw is None else listener - raw,
        "row_block_listener_logloss": row_listener,
        "row_block_global_transport_logloss": row_global,
        "row_block_listener_delta_vs_global_transport": None
        if row_listener is None or row_global is None
        else row_listener - row_global,
        "chronological_listener_logloss": chrono_listener,
        "chronological_global_transport_logloss": chrono_global,
        "chronological_listener_delta_vs_global_transport": None
        if chrono_listener is None or chrono_global is None
        else chrono_listener - chrono_global,
        "selected_route_counts": {str(key): int(value) for key, value in route_counts.items()},
        "selected_routes": selection.to_dict(orient="records"),
        "selection_stability": stability_summary.to_dict(orient="records"),
        "selection_win_folds_total": int(stability["wins_global_transport"].sum()),
        "selection_folds_total": int(len(stability)),
        "subject_best_probe": None if subject_all.empty else subject_all.sort_values("logloss").iloc[0].to_dict(),
        "row_block_best_probe": None if row_all.empty else row_all.sort_values("logloss").iloc[0].to_dict(),
        "chronological_best_probe": None if chrono_all.empty else chrono_all.sort_values("logloss").iloc[0].to_dict(),
        "selected_route_subject_leakage": selected_leak.to_dict(orient="records"),
        "global_transport_subject_leakage": None if global_leak.empty else global_leak.iloc[0].to_dict(),
        "raw_subject_leakage": None if raw_leak.empty else raw_leak.iloc[0].to_dict(),
    }


def build_markdown(
    summary: dict[str, Any],
    probe_metrics: pd.DataFrame,
    selection: pd.DataFrame,
    leakage: pd.DataFrame,
) -> str:
    subject_all = probe_metrics[(probe_metrics["split"].eq("subject_heldout")) & (probe_metrics["target"].eq("all"))].sort_values("logloss")
    row_all = probe_metrics[(probe_metrics["split"].eq("row_block_holdout")) & (probe_metrics["target"].eq("all"))].sort_values("logloss")
    chrono_all = probe_metrics[(probe_metrics["split"].eq("chronological_holdout")) & (probe_metrics["target"].eq("all"))].sort_values("logloss")
    stability = pd.DataFrame(summary["selection_stability"])
    subject_leak = leakage[leakage["split"].eq("subject_heldout")].sort_values("subject_id_accuracy")
    return f"""# Transported Prototype Listener Readout Core

## 한 줄 요약

Cross-subject transported prototype grammar를 하나의 global latent로 읽지 않고,
Q/S target listener별로 어떤 transported grammar view를 읽어야 하는지 frozen probe로 진단한 실험이다.

```text
train subjects define prototype grammar
  -> held-out rows receive transported prototype responsibilities
  -> target listener chooses a transported prototype view
```

## 판정

- verdict: `{summary["verdict"]}`
- public LB ledger 사용: `{summary["uses_public_score_ledger"]}`
- prior submission probability 사용: `{summary["uses_prior_submission_probabilities"]}`
- proprietary embedding API 사용: `{summary["uses_proprietary_embedding_api"]}`
- label을 pretext target으로 사용: `{summary["uses_label_as_pretext_target"]}`

## 핵심 수치

- subject listener-conditioned logloss: `{format_float(summary["subject_listener_conditioned_logloss"], 6)}`
- subject global transport logloss: `{format_float(summary["subject_global_transport_logloss"], 6)}`
- subject prior logloss: `{format_float(summary["subject_prior_logloss"], 6)}`
- delta vs global transport: `{format_float(summary["subject_listener_delta_vs_global_transport"], 6)}`
- delta vs prior: `{format_float(summary["subject_listener_delta_vs_prior"], 6)}`
- row-block delta vs global transport: `{format_float(summary["row_block_listener_delta_vs_global_transport"], 6)}`
- chronological delta vs global transport: `{format_float(summary["chronological_listener_delta_vs_global_transport"], 6)}`
- selected-route fold wins: `{summary["selection_win_folds_total"]} / {summary["selection_folds_total"]}`

## Target별 Listener View 선택

{markdown_table(selection, ["target", "selected_feature_set", "selected_logloss", "global_transport_logloss", "delta_vs_global_transport"])}

## Fold Stability

{markdown_table(stability, ["target", "selected_feature_set", "mean_delta_vs_global", "win_folds_vs_global", "total_folds"])}

## Subject-Heldout Frozen Probe

{markdown_table(subject_all, ["feature_set", "logloss", "auc"], max_rows=24)}

## Row-Block Frozen Probe

{markdown_table(row_all, ["feature_set", "logloss", "auc"], max_rows=24)}

## Chronological Frozen Probe

{markdown_table(chrono_all, ["feature_set", "logloss", "auc"], max_rows=24)}

## Subject Leakage Diagnostic

{markdown_table(subject_leak, ["feature_set", "subject_id_accuracy", "chance_accuracy", "leakage_lift_vs_chance"], max_rows=24)}

## 해석

positive이면 다음 주장이 강화된다.

```text
HS-JEPA의 transported prototype grammar는 하나의 global latent가 아니라
listener별로 읽어야 하는 human-state grammar interface다.
```

negative이면 다음 경계가 생긴다.

```text
cross-subject grammar transport는 존재하지만,
target별 listener readout은 현재 split에서는 과적합이거나 아직 약하다.
```
"""


def run() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    PAPER_DOC.parent.mkdir(parents=True, exist_ok=True)
    ensure_transport_outputs()

    frame_all, _labels = load_frames()
    train_frame = frame_all[frame_all["split"].eq("train")].reset_index(drop=True)
    catalog = catalog_features(frame_all)
    views = view_columns(catalog)
    transport_sets, candidate_names = transported_feature_sets(views)

    metric_parts: list[pd.DataFrame] = []
    prediction_parts: list[pd.DataFrame] = []
    leakage_parts: list[pd.DataFrame] = []

    for split_name in ["subject_heldout", "chronological_holdout", "row_block_holdout"]:
        state = load_transport_state(split_name)
        metrics, predictions, leakage = evaluate_transport_readout_split(
            split_name,
            train_frame,
            state,
            transport_sets,
            catalog.raw_numeric,
            catalog.calendar,
        )
        metric_parts.append(metrics)
        prediction_parts.append(predictions)
        leakage_parts.append(leakage)

    base_metrics = pd.concat(metric_parts, ignore_index=True, sort=False)
    predictions = pd.concat(prediction_parts, ignore_index=True, sort=False)
    leakage = pd.concat(leakage_parts, ignore_index=True, sort=False)
    calibrated = base_metrics[base_metrics["feature_set"].str.endswith("_calibrated10", na=False)].copy()
    selection = select_listener_views(calibrated, candidate_names)
    selected_metrics = listener_selected_probe_metrics(predictions, selection)
    stability = listener_selection_stability(predictions, selection)
    probe_metrics = pd.concat([base_metrics, selected_metrics], ignore_index=True, sort=False)
    summary = summarize(probe_metrics, selection, stability, leakage)

    probe_metrics.to_csv(OUT_DIR / "transported_prototype_listener_readout_probe_metrics.csv", index=False)
    selection.to_csv(OUT_DIR / "transported_prototype_listener_selection.csv", index=False)
    stability.to_csv(OUT_DIR / "transported_prototype_listener_selection_stability.csv", index=False)
    leakage.to_csv(OUT_DIR / "transported_prototype_listener_subject_leakage.csv", index=False)
    (OUT_DIR / "transported_prototype_listener_readout_summary.json").write_text(
        json.dumps(json_safe(summary), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    doc = build_markdown(summary, probe_metrics, selection, leakage)
    (OUT_DIR / "TRANSPORTED_PROTOTYPE_LISTENER_READOUT_CORE_KO.md").write_text(doc, encoding="utf-8")
    PAPER_DOC.write_text(doc, encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(json_safe(run()), ensure_ascii=False, indent=2))
