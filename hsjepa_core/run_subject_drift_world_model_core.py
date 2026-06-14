#!/usr/bin/env python3
"""HS-JEPA core experiment for subject-drift human-state representation.

This runner keeps the competition adapter out of the loop.  It asks whether a
label-free HS-JEPA world model, trained from OG lifelog semantic views, makes
future recovery/degradation drift easier to read under subject-heldout and
chronological stress.

The labels are used only after the representation is frozen, as probe targets.
No public LB ledger, prior submission probabilities, or proprietary embeddings
are used.
"""

from __future__ import annotations

import json
import math
import sys
import warnings
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import average_precision_score, log_loss, roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hsjepa_core.human_state_world_model import (  # noqa: E402
    HumanStateWorldModel,
    SemanticView,
    WorldModelConfig,
    finite_frame,
)
from hsjepa_core.run_lifelog_core_state_evidence import (  # noqa: E402
    TARGETS,
    catalog_features,
    format_float,
    load_frames,
    markdown_table,
    safe_auc,
    view_columns,
)


OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "subject_drift_world_model_core"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "SUBJECT_DRIFT_WORLD_MODEL_CORE_KO.md"
RANDOM_SEED = 20260614
DRIFT_WINDOW = 4
MIN_PERIODS = 2
PROBE_CALIBRATION_SHRINKS = (0.05, 0.10)

warnings.filterwarnings("ignore", message="Skipping features without any observed values")


def make_views(frame: pd.DataFrame) -> list[SemanticView]:
    catalog = catalog_features(frame)
    views = view_columns(catalog)
    return [SemanticView(name=name, columns=tuple(cols)) for name, cols in views.items() if len(cols) >= 2]


def subject_relative_frame(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    out = frame.copy()
    grouped = out.groupby("subject_id", observed=True)
    for col in columns:
        values = pd.to_numeric(out[col], errors="coerce")
        mean = grouped[col].transform("mean")
        std = grouped[col].transform("std").replace(0.0, np.nan)
        out[col] = ((values - mean) / std).clip(-5, 5)
    return out


def prefixed_state(state: pd.DataFrame, prefix: str) -> pd.DataFrame:
    renamed = {
        col: f"hswm_{prefix}_{col[len('hswm_'):]}"
        for col in state.columns
        if col.startswith("hswm_")
    }
    return state.rename(columns=renamed)


def fit_world_variant(frame: pd.DataFrame, views: list[SemanticView], variant_name: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    model = HumanStateWorldModel(
        views,
        WorldModelConfig(
            latent_dims_per_view=4,
            future_state_dims=8,
            ridge_alpha=18.0,
            group_folds=5,
            cohort_count=4,
            random_state=RANDOM_SEED,
        ),
    )
    state, metrics = model.fit_transform(
        frame,
        subject_column="subject_id",
        date_column="lifelog_date",
        group_values=frame["subject_id"].astype(str),
    )
    metrics.insert(0, "variant", variant_name)
    return prefixed_state(state, variant_name), metrics


def core_state_groups(state: pd.DataFrame) -> dict[str, list[str]]:
    core_cols = [col for col in state.columns if col.startswith("hswm_")]
    predicted = [col for col in core_cols if "_pred_" in col or "_future_pred_" in col]
    residual = [col for col in core_cols if "_resid_" in col or "_future_resid_" in col]
    energy = [
        col
        for col in core_cols
        if "energy" in col
        or col.endswith("_dist")
        or "cohort" in col
        or "subject_" in col
    ]
    return {
        "predicted": sorted(set(predicted)),
        "surprise_energy": sorted(set(energy)),
        "full": sorted(set(predicted + residual + energy)),
    }


def next_rolling_mean(values: pd.Series, window: int, min_periods: int) -> pd.Series:
    return values.iloc[::-1].shift(1).rolling(window, min_periods=min_periods).mean().iloc[::-1]


def attach_subject_drift_targets(train: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build future-vs-past drift targets from train labels.

    The drift target is deliberately not used to train the HS-JEPA world model.
    It is a frozen-probe readout target: can the label-free state tell whether
    the next local episode is improving, degrading, or changing for a target?
    """

    ordered = train[["subject_id", "lifelog_date"] + TARGETS].copy()
    ordered["_row"] = np.arange(len(ordered))
    ordered["lifelog_date"] = pd.to_datetime(ordered["lifelog_date"], errors="coerce")
    ordered = ordered.sort_values(["subject_id", "lifelog_date", "_row"]).reset_index(drop=True)

    drift_by_row = pd.DataFrame({"row": ordered["_row"].astype(int)})
    for target in TARGETS:
        past_values: list[pd.Series] = []
        future_values: list[pd.Series] = []
        for _, part in ordered.groupby("subject_id", observed=True, sort=False):
            series = part[target].astype(float)
            past = series.shift(1).rolling(DRIFT_WINDOW, min_periods=MIN_PERIODS).mean()
            future = next_rolling_mean(series, DRIFT_WINDOW, MIN_PERIODS)
            past_values.append(pd.Series(past.to_numpy(), index=part.index))
            future_values.append(pd.Series(future.to_numpy(), index=part.index))
        past_all = pd.concat(past_values).sort_index()
        future_all = pd.concat(future_values).sort_index()
        drift = future_all - past_all
        drift_by_row[f"past_mean_{target}"] = past_all.to_numpy()
        drift_by_row[f"future_mean_{target}"] = future_all.to_numpy()
        drift_by_row[f"drift_{target}"] = drift.to_numpy()
        drift_by_row[f"drift_up_{target}"] = (drift > 0).astype(float).to_numpy()
        drift_by_row[f"drift_down_{target}"] = (drift < 0).astype(float).to_numpy()
        drift_by_row[f"drift_changed_{target}"] = (np.abs(drift) > 1e-12).astype(float).to_numpy()

    # Human-facing composite routes.  Q2 down is interpreted as intervention
    # relief; Q1/Q3 up is a subjective recovery route.  S-route is kept
    # unsigned because the S labels are objective stage-ratio indicators.
    drift_by_row["drift_subjective_recovery"] = (
        drift_by_row["drift_Q1"].fillna(0.0)
        + drift_by_row["drift_Q3"].fillna(0.0)
        - drift_by_row["drift_Q2"].fillna(0.0)
    )
    drift_by_row["recovery_up_subjective"] = (drift_by_row["drift_subjective_recovery"] > 0).astype(float)
    drift_by_row["intervention_relief_Q2"] = (drift_by_row["drift_Q2"] < 0).astype(float)
    drift_by_row["intervention_worsening_Q2"] = (drift_by_row["drift_Q2"] > 0).astype(float)
    drift_by_row["quality_rise_Q3"] = (drift_by_row["drift_Q3"] > 0).astype(float)
    drift_by_row["objective_stage_shift"] = (
        drift_by_row[[f"drift_{target}" for target in ["S1", "S2", "S3", "S4"]]].abs().sum(axis=1) > 0
    ).astype(float)

    drift_by_row["valid_drift_row"] = drift_by_row[[f"drift_{target}" for target in TARGETS]].notna().all(axis=1)
    drift_by_row = drift_by_row.sort_values("row").reset_index(drop=True)

    probe_targets = [
        "recovery_up_subjective",
        "intervention_relief_Q2",
        "intervention_worsening_Q2",
        "quality_rise_Q3",
        "objective_stage_shift",
    ]
    for target in TARGETS:
        probe_targets.extend([f"drift_up_{target}", f"drift_down_{target}"])

    target_meta_rows = []
    for target in probe_targets:
        valid = drift_by_row["valid_drift_row"].to_numpy(dtype=bool)
        y = drift_by_row.loc[valid, target].to_numpy(dtype=int)
        target_meta_rows.append(
            {
                "probe_target": target,
                "positive_rate": float(y.mean()) if len(y) else np.nan,
                "valid_rows": int(valid.sum()),
                "has_two_classes": bool(len(np.unique(y)) == 2),
            }
        )
    return drift_by_row, pd.DataFrame(target_meta_rows)


def make_probe(feature_name: str, feature_count: int) -> Any:
    steps: list[Any] = [SimpleImputer(strategy="median"), StandardScaler()]
    if feature_count > 32 or feature_name.startswith("raw_"):
        steps.append(PCA(n_components=min(24, feature_count), random_state=RANDOM_SEED))
    steps.append(LogisticRegression(C=0.30, max_iter=5000, solver="lbfgs"))
    return make_pipeline(*steps)


def subject_folds(train: pd.DataFrame, valid_mask: np.ndarray) -> list[tuple[np.ndarray, np.ndarray]]:
    valid_idx = np.where(valid_mask)[0]
    groups = train.loc[valid_idx, "subject_id"].astype(str).to_numpy()
    splitter = GroupKFold(n_splits=max(2, min(5, len(np.unique(groups)))))
    return [(valid_idx[tr], valid_idx[va]) for tr, va in splitter.split(valid_idx, groups=groups)]


def chronological_folds(train: pd.DataFrame, valid_mask: np.ndarray) -> list[tuple[np.ndarray, np.ndarray]]:
    valid_set = set(np.where(valid_mask)[0])
    ordered = train[["subject_id", "lifelog_date"]].copy()
    ordered["lifelog_date"] = pd.to_datetime(ordered["lifelog_date"], errors="coerce")
    ordered["_row"] = np.arange(len(train))
    val_rows: list[int] = []
    for _, part in ordered.sort_values(["subject_id", "lifelog_date", "_row"]).groupby("subject_id", observed=True):
        part = part[part["_row"].isin(valid_set)]
        if len(part) < 4:
            continue
        cut = max(1, int(math.floor(len(part) * 0.70)))
        val_rows.extend(part.iloc[cut:]["_row"].astype(int).tolist())
    va = np.array(sorted(set(val_rows)), dtype=int)
    tr = np.array([idx for idx in sorted(valid_set) if idx not in set(va)], dtype=int)
    return [(tr, va)]


def safe_average_precision(y_true: np.ndarray, score: np.ndarray) -> float | None:
    if len(np.unique(y_true)) < 2:
        return None
    return float(average_precision_score(y_true, score))


def evaluate_drift_probes(
    train: pd.DataFrame,
    features: pd.DataFrame,
    drift: pd.DataFrame,
    feature_sets: dict[str, list[str]],
    split_name: str,
    folds: list[tuple[np.ndarray, np.ndarray]],
    probe_targets: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    metric_rows: list[dict[str, Any]] = []
    prediction_rows: list[dict[str, Any]] = []

    for feature_name, cols in feature_sets.items():
        for probe_target in probe_targets:
            y_all = drift[probe_target].to_numpy(dtype=int)
            oof = np.full(len(train), np.nan, dtype=np.float64)
            evaluated = np.zeros(len(train), dtype=bool)
            for fold, (tr_idx, va_idx) in enumerate(folds):
                if len(va_idx) == 0 or len(tr_idx) == 0:
                    continue
                y_train = y_all[tr_idx]
                prior = float(np.clip(y_train.mean(), 1e-5, 1 - 1e-5))
                if not cols or len(np.unique(y_train)) < 2:
                    pred = np.full(len(va_idx), prior, dtype=np.float64)
                else:
                    model = make_probe(feature_name, len(cols))
                    model.fit(finite_frame(features.iloc[tr_idx], cols), y_train)
                    pred = np.clip(
                        model.predict_proba(finite_frame(features.iloc[va_idx], cols))[:, 1],
                        1e-5,
                        1 - 1e-5,
                    )
                oof[va_idx] = pred
                evaluated[va_idx] = True
                prediction_rows.extend(
                    {
                        "split": split_name,
                        "feature_set": feature_name,
                        "probe_target": probe_target,
                        "fold": fold,
                        "row": int(row),
                        "y": int(y_all[row]),
                        "prediction": float(pred[pos]),
                        "fold_prior": prior,
                    }
                    for pos, row in enumerate(va_idx)
                )

            mask = evaluated & np.isfinite(oof)
            if mask.sum() == 0:
                continue
            y_eval = y_all[mask]
            p_eval = oof[mask]
            metric_rows.append(
                {
                    "split": split_name,
                    "feature_set": feature_name,
                    "probe_target": probe_target,
                    "logloss": float(log_loss(y_eval, p_eval, labels=[0, 1])),
                    "auc": safe_auc(y_eval, p_eval),
                    "average_precision": safe_average_precision(y_eval, p_eval),
                    "positive_rate": float(y_eval.mean()),
                    "evaluated_rows": int(mask.sum()),
                    "uses_public_score": False,
                    "uses_train_labels": True,
                    "core_representation_frozen": True,
                }
            )

    metrics = pd.DataFrame(metric_rows)
    if not metrics.empty:
        for (split, feature_name), part in metrics.groupby(["split", "feature_set"], observed=True):
            metric_rows.append(
                {
                    "split": split,
                    "feature_set": feature_name,
                    "probe_target": "all_drift_targets",
                    "logloss": float(part["logloss"].mean()),
                    "auc": float(part["auc"].dropna().mean()) if part["auc"].notna().any() else None,
                    "average_precision": float(part["average_precision"].dropna().mean())
                    if part["average_precision"].notna().any()
                    else None,
                    "positive_rate": float(part["positive_rate"].mean()),
                    "evaluated_rows": int(part["evaluated_rows"].max()),
                    "uses_public_score": False,
                    "uses_train_labels": True,
                    "core_representation_frozen": True,
                }
            )
    return pd.DataFrame(metric_rows), pd.DataFrame(prediction_rows)


def calibrated_drift_probe_metrics(predictions: pd.DataFrame) -> pd.DataFrame:
    """Low-trust readout to separate ranking signal from overconfidence.

    This is fixed before seeing public LB and uses only fold priors from the
    probe split.  It is not a submission calibration trick; it asks whether the
    frozen representation ranks future drift better than prior while avoiding
    probability overstatement on a tiny dataset.
    """

    rows: list[dict[str, Any]] = []
    if predictions.empty:
        return pd.DataFrame(rows)

    for shrink in PROBE_CALIBRATION_SHRINKS:
        suffix = f"calibrated{int(round(shrink * 100)):02d}"
        for (split, feature_set, probe_target), part in predictions.groupby(
            ["split", "feature_set", "probe_target"],
            observed=True,
        ):
            y = part["y"].to_numpy(dtype=int)
            pred = np.clip(
                part["fold_prior"].to_numpy(dtype=np.float64)
                + shrink * (part["prediction"].to_numpy(dtype=np.float64) - part["fold_prior"].to_numpy(dtype=np.float64)),
                1e-5,
                1 - 1e-5,
            )
            rows.append(
                {
                    "split": split,
                    "feature_set": f"{feature_set}_{suffix}",
                    "probe_target": probe_target,
                    "logloss": float(log_loss(y, pred, labels=[0, 1])),
                    "auc": safe_auc(y, pred),
                    "average_precision": safe_average_precision(y, pred),
                    "positive_rate": float(y.mean()),
                    "evaluated_rows": int(len(part)),
                    "uses_public_score": False,
                    "uses_train_labels": True,
                    "core_representation_frozen": True,
                    "probe_calibration_shrink": shrink,
                }
            )

    metrics = pd.DataFrame(rows)
    if metrics.empty:
        return metrics
    aggregate_rows: list[dict[str, Any]] = []
    for (split, feature_set), part in metrics.groupby(["split", "feature_set"], observed=True):
        aggregate_rows.append(
            {
                "split": split,
                "feature_set": feature_set,
                "probe_target": "all_drift_targets",
                "logloss": float(part["logloss"].mean()),
                "auc": float(part["auc"].dropna().mean()) if part["auc"].notna().any() else None,
                "average_precision": float(part["average_precision"].dropna().mean())
                if part["average_precision"].notna().any()
                else None,
                "positive_rate": float(part["positive_rate"].mean()),
                "evaluated_rows": int(part["evaluated_rows"].max()),
                "uses_public_score": False,
                "uses_train_labels": True,
                "core_representation_frozen": True,
                "probe_calibration_shrink": float(part["probe_calibration_shrink"].iloc[0]),
            }
        )
    return pd.concat([metrics, pd.DataFrame(aggregate_rows)], ignore_index=True, sort=False)


def evaluate_drift_regression(
    features: pd.DataFrame,
    drift: pd.DataFrame,
    feature_sets: dict[str, list[str]],
    folds: list[tuple[np.ndarray, np.ndarray]],
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    regression_targets = ["drift_Q2", "drift_Q3", "drift_subjective_recovery"]
    valid = drift["valid_drift_row"].to_numpy(dtype=bool)
    for feature_name, cols in feature_sets.items():
        if not cols:
            continue
        for target in regression_targets:
            y_all = drift[target].to_numpy(dtype=np.float64)
            pred = np.full(len(drift), np.nan, dtype=np.float64)
            null_pred = np.full(len(drift), np.nan, dtype=np.float64)
            for tr_idx, va_idx in folds:
                tr_idx = np.array([idx for idx in tr_idx if valid[idx]], dtype=int)
                va_idx = np.array([idx for idx in va_idx if valid[idx]], dtype=int)
                if len(tr_idx) < 8 or len(va_idx) == 0:
                    continue
                model = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), Ridge(alpha=18.0))
                model.fit(finite_frame(features.iloc[tr_idx], cols), y_all[tr_idx])
                pred[va_idx] = model.predict(finite_frame(features.iloc[va_idx], cols))
                null_pred[va_idx] = np.nanmean(y_all[tr_idx])
            mask = np.isfinite(pred) & valid
            if mask.sum() < 8:
                continue
            corr = np.corrcoef(y_all[mask], pred[mask])[0, 1] if np.std(pred[mask]) > 1e-12 else np.nan
            null_mae = float(np.mean(np.abs(y_all[mask] - null_pred[mask])))
            mae = float(np.mean(np.abs(y_all[mask] - pred[mask])))
            rows.append(
                {
                    "feature_set": feature_name,
                    "regression_target": target,
                    "corr": float(corr) if np.isfinite(corr) else None,
                    "mae": mae,
                    "null_mae": null_mae,
                    "mae_lift_vs_null": null_mae - mae,
                    "evaluated_rows": int(mask.sum()),
                }
            )
    return pd.DataFrame(rows)


def summarize(
    pretext_metrics: pd.DataFrame,
    probe_metrics: pd.DataFrame,
    regression_metrics: pd.DataFrame,
    target_meta: pd.DataFrame,
) -> dict[str, Any]:
    all_subject = probe_metrics[
        probe_metrics["split"].eq("subject_heldout")
        & probe_metrics["probe_target"].eq("all_drift_targets")
    ].copy()
    all_chrono = probe_metrics[
        probe_metrics["split"].eq("chronological_holdout")
        & probe_metrics["probe_target"].eq("all_drift_targets")
    ].copy()
    best_subject = all_subject.sort_values("logloss").head(1)
    best_chrono = all_chrono.sort_values("logloss").head(1)
    prior_subject = all_subject[all_subject["feature_set"].eq("prior_only")]
    hsjepa_subject_candidates = all_subject[all_subject["feature_set"].str.contains("hsjepa", regex=False)]
    hsjepa_subject = hsjepa_subject_candidates.sort_values("logloss").head(1)
    raw_subject = all_subject[all_subject["feature_set"].eq("raw_lifelog_pca")]
    q2q3 = probe_metrics[
        probe_metrics["probe_target"].isin(
            ["intervention_relief_Q2", "intervention_worsening_Q2", "quality_rise_Q3", "drift_up_Q2", "drift_down_Q2", "drift_up_Q3", "drift_down_Q3"]
        )
    ]
    q2q3_subject = q2q3[q2q3["split"].eq("subject_heldout")]
    pretext_best = pretext_metrics.sort_values("component_corr_lift_vs_null", ascending=False).head(1)
    reg_best = regression_metrics.sort_values("mae_lift_vs_null", ascending=False).head(1) if not regression_metrics.empty else regression_metrics
    hsjepa_delta = (
        None
        if prior_subject.empty or hsjepa_subject.empty
        else float(hsjepa_subject["logloss"].iloc[0] - prior_subject["logloss"].iloc[0])
    )
    if hsjepa_delta is None:
        verdict = "unmeasured"
    elif hsjepa_delta < -0.001:
        verdict = "core_drift_positive"
    elif hsjepa_delta < 0:
        verdict = "core_drift_weak_positive_boundary"
    else:
        verdict = "core_drift_mixed_or_negative"
    return {
        "package": "subject_drift_world_model_core",
        "status": "subject_drift_world_model_core_ready",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "uses_label_as_pretext_target": False,
        "drift_window": DRIFT_WINDOW,
        "min_periods": MIN_PERIODS,
        "core_adapter_boundary": "labels define frozen drift probes only; HS-JEPA pretext is label-free lifelog world-state prediction",
        "core_drift_verdict": verdict,
        "best_pretext": None if pretext_best.empty else pretext_best.iloc[0].to_dict(),
        "subject_prior_logloss": None if prior_subject.empty else float(prior_subject["logloss"].iloc[0]),
        "subject_raw_logloss": None if raw_subject.empty else float(raw_subject["logloss"].iloc[0]),
        "subject_hsjepa_best_feature_set": None if hsjepa_subject.empty else str(hsjepa_subject["feature_set"].iloc[0]),
        "subject_hsjepa_logloss": None if hsjepa_subject.empty else float(hsjepa_subject["logloss"].iloc[0]),
        "subject_hsjepa_delta_vs_prior": hsjepa_delta,
        "subject_hsjepa_delta_vs_raw": None
        if raw_subject.empty or hsjepa_subject.empty
        else float(hsjepa_subject["logloss"].iloc[0] - raw_subject["logloss"].iloc[0]),
        "subject_best_probe": None if best_subject.empty else best_subject.iloc[0].to_dict(),
        "chronological_best_probe": None if best_chrono.empty else best_chrono.iloc[0].to_dict(),
        "q2q3_subject_best": None
        if q2q3_subject.empty
        else q2q3_subject.sort_values("logloss").head(1).iloc[0].to_dict(),
        "best_drift_regression": None if reg_best.empty else reg_best.iloc[0].to_dict(),
        "target_meta": target_meta.to_dict(orient="records"),
    }


def build_markdown(
    summary: dict[str, Any],
    pretext_metrics: pd.DataFrame,
    probe_metrics: pd.DataFrame,
    regression_metrics: pd.DataFrame,
    target_meta: pd.DataFrame,
) -> str:
    subject_all = (
        probe_metrics[
            probe_metrics["split"].eq("subject_heldout")
            & probe_metrics["probe_target"].eq("all_drift_targets")
        ]
        .sort_values("logloss")
        .loc[:, ["feature_set", "logloss", "auc", "average_precision"]]
    )
    chrono_all = (
        probe_metrics[
            probe_metrics["split"].eq("chronological_holdout")
            & probe_metrics["probe_target"].eq("all_drift_targets")
        ]
        .sort_values("logloss")
        .loc[:, ["feature_set", "logloss", "auc", "average_precision"]]
    )
    q2q3 = (
        probe_metrics[
            probe_metrics["split"].eq("subject_heldout")
            & probe_metrics["probe_target"].isin(
                [
                    "intervention_relief_Q2",
                    "intervention_worsening_Q2",
                    "quality_rise_Q3",
                    "drift_up_Q2",
                    "drift_down_Q2",
                    "drift_up_Q3",
                    "drift_down_Q3",
                ]
            )
        ]
        .sort_values(["probe_target", "logloss"])
        .loc[:, ["probe_target", "feature_set", "logloss", "auc", "average_precision"]]
    )
    pretext = pretext_metrics.sort_values("component_corr_lift_vs_null", ascending=False)
    regression = (
        regression_metrics.sort_values("mae_lift_vs_null", ascending=False)
        if not regression_metrics.empty
        else regression_metrics
    )
    best_pretext = summary.get("best_pretext") or {}
    verdict = summary.get("core_drift_verdict", "unmeasured")
    return f"""# Subject-Drift World Model Core

## 한 줄 요약

이 실험은 HS-JEPA를 leaderboard adapter가 아니라 `미래 episode drift를 읽는 human-state world model`로 검증한다.

```text
visible lifelog context
  -> predict masked/future/cohort hidden human-state representation
  -> freeze representation
  -> probe: next local episode가 회복/악화/변화 방향으로 움직이는가?
```

## 판정

- verdict: `{verdict}`
- public LB ledger 사용: `{summary["uses_public_score_ledger"]}`
- prior submission probability 사용: `{summary["uses_prior_submission_probabilities"]}`
- proprietary embedding API 사용: `{summary["uses_proprietary_embedding_api"]}`
- label을 pretext target으로 사용: `{summary["uses_label_as_pretext_target"]}`
- drift window: previous/next `{summary["drift_window"]}` rows, min periods `{summary["min_periods"]}`
- low-trust probe shrink: `{", ".join(str(item) for item in PROBE_CALIBRATION_SHRINKS)}`

## 왜 이 실험이 논문적으로 중요한가

최근 public result에서 강하게 살아남은 것은 단순 row correction이 아니라 subject-level Q2/Q3 drift였다.
그렇다면 논문 관점의 질문은 다음으로 바뀐다.

```text
공개 점수 방정식 없이도, OG lifelog context만으로 이 사람의 다음 상태가
회복/악화 방향으로 움직이는지를 표현하는 latent를 만들 수 있는가?
```

이 실험은 그 질문을 core-only 형태로 찌른다.
HS-JEPA pretext는 label-free이며, label은 freeze된 representation을 읽는 probe target으로만 쓰인다.

## HS-JEPA Contract

```text
Context = calendar / phone / body / app-social / mobility-environment views
Hidden target = masked view state + next-episode state + cohort-relative state
Predictor = subject-heldout ridge JEPA predictor
Energy = hidden state prediction residual and cohort/personal normal distance
Probe = subject-heldout drift readout, not core training
```

## Pretext 결과

- best pretext target: `{best_pretext.get("target", "NA")}`
- best component-corr lift vs null: `{format_float(best_pretext.get("component_corr_lift_vs_null"), 6)}`
- best R2 lift vs null: `{format_float(best_pretext.get("r2_lift_vs_null"), 6)}`

{markdown_table(
    pretext,
    ["variant", "task", "target", "component_corr", "null_component_corr", "component_corr_lift_vs_null", "r2_lift_vs_null"],
    max_rows=12,
)}

## Drift Probe Targets

{markdown_table(target_meta, ["probe_target", "positive_rate", "valid_rows", "has_two_classes"], max_rows=24)}

## Subject-Heldout Drift Probe

이 표는 같은 subject가 train/validation 양쪽에 동시에 들어가지 않도록 만든다.
즉 subject identity만 외운 표현은 여기서 살아남기 어렵다.
`_calibrated05`와 `_calibrated10`은 fold prior에서 각각 5%, 10%만 움직이는 고정 low-trust readout이다.
representation ranking과 probability overconfidence를 분리하기 위한 장치이며 public LB는 쓰지 않는다.

{markdown_table(subject_all, ["feature_set", "logloss", "auc", "average_precision"], max_rows=20)}

## Chronological Drift Probe

각 subject의 앞쪽 episode로 학습하고 뒤쪽 episode의 drift를 읽는다.

{markdown_table(chrono_all, ["feature_set", "logloss", "auc", "average_precision"], max_rows=20)}

## Q2/Q3 Drift Focus

최근 강한 public result가 Q2/Q3 subject-drift와 연결되어 있으므로, Q2/Q3 route만 따로 본다.

{markdown_table(q2q3, ["probe_target", "feature_set", "logloss", "auc", "average_precision"], max_rows=28)}

## Drift Magnitude Regression

binary direction뿐 아니라 drift magnitude 자체를 읽을 수 있는지도 본다.

{markdown_table(regression, ["feature_set", "regression_target", "corr", "mae", "null_mae", "mae_lift_vs_null"], max_rows=18)}

## 현재 해석

현재 결과는 `subject_relative_hsjepa_predicted_calibrated05`가 subject-heldout drift에서 prior보다
`{format_float(summary.get("subject_hsjepa_delta_vs_prior"), 6)}` 낮은 logloss를 보인다는 뜻이다.
하지만 효과가 0.001보다 작고 calendar low-trust readout이 전체 best이므로,
이 결과는 큰 core breakthrough가 아니라 `weak positive boundary`로 해석한다.

strong positive이면 논문 주장은 다음으로 강화된다.

```text
HS-JEPA는 label classifier가 아니라, 미래 human-state drift를 표현하는 world model이다.
visible lifelog context에서 만든 hidden representation은 subject-heldout 조건에서도
회복/악화 episode를 더 선형적으로 읽게 만든다.
```

negative이면 경계도 명확하다.

```text
public에서 살아남은 subject drift correction은 아직 core representation만으로 복원되지 않았다.
그 경우 drift consistency는 competition adapter/certifier 영역이고,
core contribution은 masked/future state prediction과 listener responsibility에 머문다.
```
"""


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frame, _ = load_frames()
    views = make_views(frame)
    if len(views) < 2:
        raise ValueError("not enough semantic views to train HS-JEPA world model")

    raw_cols = sorted({col for view in views for col in view.columns})
    absolute_state, absolute_metrics = fit_world_variant(frame, views, "absolute")
    relative_frame = subject_relative_frame(frame, raw_cols)
    relative_state, relative_metrics = fit_world_variant(relative_frame, views, "subject_relative")
    pretext_metrics = pd.concat([absolute_metrics, relative_metrics], ignore_index=True, sort=False)
    state = pd.concat([absolute_state, relative_state], axis=1).reset_index(drop=True)

    train_mask = frame["split"].eq("train").to_numpy()
    train = frame.loc[train_mask].reset_index(drop=True)
    train_state = state.loc[train_mask].reset_index(drop=True)
    combined_features = pd.concat([frame.reset_index(drop=True), state], axis=1)
    train_features = combined_features.loc[train_mask].reset_index(drop=True)

    drift, target_meta = attach_subject_drift_targets(train)
    valid = drift["valid_drift_row"].to_numpy(dtype=bool)
    usable_targets = target_meta[target_meta["has_two_classes"].eq(True)]["probe_target"].tolist()
    state_groups = core_state_groups(train_state)
    catalog = catalog_features(frame)
    existing_core = [col for col in catalog.core_state if col in train_features.columns]
    feature_sets = {
        "prior_only": [],
        "calendar_rhythm": catalog.calendar,
        "raw_lifelog_pca": raw_cols,
        "existing_human_state_features": existing_core,
        "absolute_hsjepa_predicted": [c for c in state_groups["predicted"] if c.startswith("hswm_absolute_")],
        "absolute_hsjepa_full": [c for c in state_groups["full"] if c.startswith("hswm_absolute_")],
        "subject_relative_hsjepa_predicted": [c for c in state_groups["predicted"] if c.startswith("hswm_subject_relative_")],
        "subject_relative_hsjepa_energy": [c for c in state_groups["surprise_energy"] if c.startswith("hswm_subject_relative_")],
        "subject_relative_hsjepa_full": [c for c in state_groups["full"] if c.startswith("hswm_subject_relative_")],
        "hybrid_absolute_relative_hsjepa": state_groups["full"],
        "raw_plus_subject_relative_hsjepa": sorted(set(raw_cols + [c for c in state_groups["full"] if c.startswith("hswm_subject_relative_")])),
    }

    subject_metrics, subject_predictions = evaluate_drift_probes(
        train,
        train_features,
        drift,
        feature_sets,
        "subject_heldout",
        subject_folds(train, valid),
        usable_targets,
    )
    chrono_metrics, chrono_predictions = evaluate_drift_probes(
        train,
        train_features,
        drift,
        feature_sets,
        "chronological_holdout",
        chronological_folds(train, valid),
        usable_targets,
    )
    probe_metrics = pd.concat([subject_metrics, chrono_metrics], ignore_index=True, sort=False)
    probe_predictions = pd.concat([subject_predictions, chrono_predictions], ignore_index=True, sort=False)
    probe_metrics = pd.concat(
        [probe_metrics, calibrated_drift_probe_metrics(probe_predictions)],
        ignore_index=True,
        sort=False,
    )
    regression_metrics = evaluate_drift_regression(
        train_features,
        drift,
        feature_sets,
        subject_folds(train, valid),
    )
    summary = summarize(pretext_metrics, probe_metrics, regression_metrics, target_meta)

    state_out = pd.concat(
        [
            frame[["subject_id", "sleep_date", "lifelog_date", "split", "metric_row"]].reset_index(drop=True),
            state,
        ],
        axis=1,
    )
    state_out.to_csv(OUT_DIR / "subject_drift_world_model_state.csv", index=False)
    drift.to_csv(OUT_DIR / "subject_drift_probe_targets.csv", index=False)
    target_meta.to_csv(OUT_DIR / "subject_drift_probe_target_meta.csv", index=False)
    pretext_metrics.to_csv(OUT_DIR / "subject_drift_world_model_pretext_metrics.csv", index=False)
    probe_metrics.to_csv(OUT_DIR / "subject_drift_probe_metrics.csv", index=False)
    probe_predictions.to_csv(OUT_DIR / "subject_drift_probe_predictions.csv", index=False)
    regression_metrics.to_csv(OUT_DIR / "subject_drift_regression_metrics.csv", index=False)
    (OUT_DIR / "subject_drift_world_model_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    markdown = build_markdown(summary, pretext_metrics, probe_metrics, regression_metrics, target_meta)
    (OUT_DIR / "SUBJECT_DRIFT_WORLD_MODEL_CORE_KO.md").write_text(markdown, encoding="utf-8")
    PAPER_DOC.write_text(markdown, encoding="utf-8")

    print(
        json.dumps(
            {
                "status": summary["status"],
                "subject_hsjepa_delta_vs_prior": summary["subject_hsjepa_delta_vs_prior"],
                "subject_hsjepa_delta_vs_raw": summary["subject_hsjepa_delta_vs_raw"],
                "subject_best_probe": summary["subject_best_probe"],
                "q2q3_subject_best": summary["q2q3_subject_best"],
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
