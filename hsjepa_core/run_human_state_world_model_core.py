#!/usr/bin/env python3
"""End-to-end HS-JEPA Human-State World Model core experiment.

This runner keeps the paper claim clean:

1. Learn a label-free HS-JEPA world-state from OG lifelog views.
2. Freeze that representation.
3. Evaluate it with simple probes under subject-heldout and chronological
   row-heldout splits.
4. Generate an optional downstream probe submission, clearly labeled as an
   adapter output rather than core evidence.
"""

from __future__ import annotations

import hashlib
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
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss, roc_auc_score
from sklearn.model_selection import GroupKFold, StratifiedKFold
from sklearn.neighbors import NearestNeighbors
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


OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "human_state_world_model_core"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "HUMAN_STATE_WORLD_MODEL_CORE_KO.md"
SAMPLE_SUBMISSION = ROOT / "data" / "ch2026_submission_sample.csv"
RANDOM_SEED = 20260613
PROBE_CALIBRATION_SHRINK = 0.10

warnings.filterwarnings("ignore", message="Skipping features without any observed values")


def short_hash(frame: pd.DataFrame) -> str:
    arr = frame[TARGETS].to_numpy(dtype=np.float64)
    return hashlib.sha256(np.round(arr, 10).tobytes()).hexdigest()[:8]


def make_views(frame: pd.DataFrame) -> list[SemanticView]:
    catalog = catalog_features(frame)
    views = view_columns(catalog)
    return [SemanticView(name=name, columns=tuple(cols)) for name, cols in views.items() if len(cols) >= 2]


def state_columns(state: pd.DataFrame) -> dict[str, list[str]]:
    core_cols = [c for c in state.columns if c.startswith("hswm_")]
    pred = [c for c in core_cols if "_pred_" in c or "_future_pred_" in c]
    resid = [c for c in core_cols if "_resid_" in c or "_future_resid_" in c]
    energy = [c for c in core_cols if "energy" in c or c.endswith("_dist")]
    cohort = [c for c in core_cols if "_cohort_" in c or "_subject_" in c]
    return {
        "world_predicted_state": pred,
        "world_surprise_energy": energy,
        "world_full_state": sorted(set(pred + resid + energy + cohort)),
        "world_cohort_state": cohort,
    }


def prefixed_state(state: pd.DataFrame, prefix: str) -> pd.DataFrame:
    return state.rename(columns={c: f"hswm_{prefix}_{c[len('hswm_'):]}" for c in state.columns if c.startswith("hswm_")})


def variant_columns(state: pd.DataFrame, prefix: str) -> dict[str, list[str]]:
    subset = state[[c for c in state.columns if c.startswith(f"hswm_{prefix}_")]].copy()
    return state_columns(subset)


def subject_relative_frame(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    out = frame.copy()
    grouped = out.groupby("subject_id", observed=True)
    for col in columns:
        values = pd.to_numeric(out[col], errors="coerce")
        mean = grouped[col].transform("mean")
        std = grouped[col].transform("std").replace(0.0, np.nan)
        out[col] = ((values - mean) / std).clip(-5, 5)
    return out


def fit_world_variant(
    frame: pd.DataFrame,
    views: list[SemanticView],
    variant_name: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
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


def make_linear_probe(feature_name: str, feature_count: int) -> Any:
    steps: list[Any] = [SimpleImputer(strategy="median"), StandardScaler()]
    if feature_count > 28 or feature_name.startswith("raw_"):
        steps.append(PCA(n_components=min(24, feature_count), random_state=RANDOM_SEED))
    steps.append(LogisticRegression(C=0.28, max_iter=5000, solver="lbfgs"))
    return make_pipeline(*steps)


def evaluate_split(
    train_frame: pd.DataFrame,
    features: pd.DataFrame,
    feature_sets: dict[str, list[str]],
    split_name: str,
    folds: list[tuple[np.ndarray, np.ndarray]],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    y_all = train_frame[TARGETS].astype(int).reset_index(drop=True)
    features = features.reset_index(drop=True)
    metric_rows: list[dict[str, Any]] = []
    prediction_rows: list[dict[str, Any]] = []

    for feature_name, cols in feature_sets.items():
        oof = pd.DataFrame(index=train_frame.index, columns=TARGETS, dtype=float)
        evaluated = np.zeros(len(train_frame), dtype=bool)
        for fold, (tr_idx, va_idx) in enumerate(folds):
            evaluated[va_idx] = True
            for target in TARGETS:
                y_train = y_all.iloc[tr_idx][target].to_numpy(dtype=int)
                y_val = y_all.iloc[va_idx][target].to_numpy(dtype=int)
                prior = float(np.clip(y_train.mean(), 1e-5, 1 - 1e-5))
                if not cols or len(np.unique(y_train)) < 2:
                    pred = np.full(len(va_idx), prior, dtype=np.float64)
                else:
                    model = make_linear_probe(feature_name, len(cols))
                    model.fit(finite_frame(features.iloc[tr_idx], cols), y_train)
                    pred = np.clip(
                        model.predict_proba(finite_frame(features.iloc[va_idx], cols))[:, 1],
                        1e-5,
                        1 - 1e-5,
                    )
                oof.iloc[va_idx, oof.columns.get_loc(target)] = pred
                prediction_rows.extend(
                    {
                        "split": split_name,
                        "feature_set": feature_name,
                        "fold": fold,
                        "row": int(row),
                        "target": target,
                        "y": int(y_val[pos]),
                        "prediction": float(pred[pos]),
                        "fold_prior": prior,
                    }
                    for pos, row in enumerate(va_idx)
                )

        losses = []
        aucs = []
        for target in TARGETS:
            y = y_all.loc[evaluated, target].to_numpy(dtype=int)
            p = oof.loc[evaluated, target].to_numpy(dtype=np.float64)
            loss = float(log_loss(y, p, labels=[0, 1]))
            auc = safe_auc(y, p)
            losses.append(loss)
            if auc is not None:
                aucs.append(auc)
            metric_rows.append(
                {
                    "split": split_name,
                    "feature_set": feature_name,
                    "target": target,
                    "logloss": loss,
                    "auc": auc,
                    "uses_public_score": False,
                    "uses_train_labels": True,
                    "core_representation_frozen": True,
                    "evaluated_rows": int(evaluated.sum()),
                }
            )
        metric_rows.append(
            {
                "split": split_name,
                "feature_set": feature_name,
                "target": "all",
                "logloss": float(np.mean(losses)),
                "auc": float(np.nanmean(aucs)) if aucs else None,
                "uses_public_score": False,
                "uses_train_labels": True,
                "core_representation_frozen": True,
                "evaluated_rows": int(evaluated.sum()),
            }
        )
    return pd.DataFrame(metric_rows), pd.DataFrame(prediction_rows)


def calibrated_probe_metrics(predictions: pd.DataFrame, shrink: float = PROBE_CALIBRATION_SHRINK) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for (split, feature_set), feature_part in predictions.groupby(["split", "feature_set"], observed=True):
        losses = []
        aucs = []
        for target, part in feature_part.groupby("target", observed=True):
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
                    "feature_set": f"{feature_set}_calibrated{int(shrink * 100):02d}",
                    "target": target,
                    "logloss": loss,
                    "auc": auc,
                    "uses_public_score": False,
                    "uses_train_labels": True,
                    "core_representation_frozen": True,
                    "probe_calibration_shrink": shrink,
                    "evaluated_rows": int(len(part)),
                }
            )
        rows.append(
            {
                "split": split,
                "feature_set": f"{feature_set}_calibrated{int(shrink * 100):02d}",
                "target": "all",
                "logloss": float(np.mean(losses)),
                "auc": float(np.nanmean(aucs)) if aucs else None,
                "uses_public_score": False,
                "uses_train_labels": True,
                "core_representation_frozen": True,
                "probe_calibration_shrink": shrink,
                "evaluated_rows": int(feature_part["row"].nunique()),
            }
        )
    return pd.DataFrame(rows)


def subject_folds(train_frame: pd.DataFrame) -> list[tuple[np.ndarray, np.ndarray]]:
    groups = train_frame["subject_id"].astype(str).to_numpy()
    splitter = GroupKFold(n_splits=max(2, min(5, len(np.unique(groups)))))
    return [(tr, va) for tr, va in splitter.split(train_frame, groups=groups)]


def chronological_folds(train_frame: pd.DataFrame) -> list[tuple[np.ndarray, np.ndarray]]:
    ordered = train_frame[["subject_id", "lifelog_date"]].copy()
    ordered["lifelog_date"] = pd.to_datetime(ordered["lifelog_date"], errors="coerce")
    ordered["_row"] = np.arange(len(train_frame))
    val_rows: list[int] = []
    for _, part in ordered.sort_values(["subject_id", "lifelog_date", "_row"]).groupby("subject_id", observed=True):
        cut = max(1, int(math.floor(len(part) * 0.72)))
        val_rows.extend(part.iloc[cut:]["_row"].astype(int).tolist())
    va = np.array(sorted(set(val_rows)), dtype=int)
    tr = np.array([idx for idx in range(len(train_frame)) if idx not in set(va)], dtype=int)
    return [(tr, va)]


def neighbor_consistency(
    train_frame: pd.DataFrame,
    features: pd.DataFrame,
    feature_sets: dict[str, list[str]],
) -> pd.DataFrame:
    y = train_frame[TARGETS].astype(int).to_numpy()
    rng = np.random.default_rng(RANDOM_SEED)
    rows: list[dict[str, Any]] = []
    for feature_name, cols in feature_sets.items():
        if not cols:
            continue
        x = SimpleImputer(strategy="median").fit_transform(finite_frame(features, cols))
        x = StandardScaler().fit_transform(x)
        if x.shape[1] > 24:
            x = PCA(n_components=min(24, x.shape[0] - 1, x.shape[1]), random_state=RANDOM_SEED).fit_transform(x)
        nn = NearestNeighbors(n_neighbors=min(6, len(features)), metric="euclidean")
        nn.fit(x)
        _, idx = nn.kneighbors(x)
        idx = idx[:, 1:]
        near_matches = []
        random_matches = []
        for row in range(len(features)):
            near_matches.append((y[idx[row]] == y[row]).mean(axis=0))
            pool = [item for item in range(len(features)) if item != row]
            rnd = rng.choice(pool, size=idx.shape[1], replace=False)
            random_matches.append((y[rnd] == y[row]).mean(axis=0))
        near = np.vstack(near_matches)
        rnd = np.vstack(random_matches)
        for target_idx, target in enumerate(TARGETS):
            rows.append(
                {
                    "feature_set": feature_name,
                    "target": target,
                    "neighbor_match_rate": float(near[:, target_idx].mean()),
                    "random_match_rate": float(rnd[:, target_idx].mean()),
                    "lift": float(near[:, target_idx].mean() - rnd[:, target_idx].mean()),
                }
            )
        rows.append(
            {
                "feature_set": feature_name,
                "target": "all",
                "neighbor_match_rate": float(near.mean()),
                "random_match_rate": float(rnd.mean()),
                "lift": float(near.mean() - rnd.mean()),
            }
        )
    return pd.DataFrame(rows)


def subject_leakage_probe(train_frame: pd.DataFrame, features: pd.DataFrame, feature_sets: dict[str, list[str]]) -> pd.DataFrame:
    subject = train_frame["subject_id"].astype(str).reset_index(drop=True)
    rows: list[dict[str, Any]] = []
    splitter = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)
    for feature_name, cols in feature_sets.items():
        if not cols:
            continue
        pred = pd.Series(index=train_frame.index, dtype=object)
        for tr, va in splitter.split(features, subject):
            x_train = finite_frame(features.iloc[tr], cols)
            x_val = finite_frame(features.iloc[va], cols)
            model = make_pipeline(
                SimpleImputer(strategy="median"),
                StandardScaler(),
                PCA(n_components=min(20, len(cols)), random_state=RANDOM_SEED),
                LogisticRegression(C=0.25, max_iter=5000, solver="lbfgs"),
            )
            model.fit(x_train, subject.iloc[tr])
            pred.iloc[va] = model.predict(x_val)
        rows.append(
            {
                "feature_set": feature_name,
                "subject_id_accuracy": float(accuracy_score(subject, pred)),
                "chance_accuracy": float(subject.value_counts(normalize=True).max()),
                "leakage_lift_vs_chance": float(accuracy_score(subject, pred) - subject.value_counts(normalize=True).max()),
            }
        )
    return pd.DataFrame(rows)


def build_downstream_probe_submission(
    train_frame: pd.DataFrame,
    test_frame: pd.DataFrame,
    train_features: pd.DataFrame,
    test_features: pd.DataFrame,
    cols: list[str],
) -> pd.DataFrame:
    sample = pd.read_csv(SAMPLE_SUBMISSION)
    out = sample.copy()
    for target in TARGETS:
        y = train_frame[target].astype(int).to_numpy()
        prior = float(np.clip(y.mean(), 1e-5, 1 - 1e-5))
        if len(np.unique(y)) < 2:
            pred = np.full(len(test_frame), prior)
        else:
            model = make_linear_probe("world_model_downstream_probe", len(cols))
            model.fit(finite_frame(train_features, cols), y)
            pred = model.predict_proba(finite_frame(test_features, cols))[:, 1]
            pred = prior + PROBE_CALIBRATION_SHRINK * (pred - prior)
        out[target] = np.clip(pred, 0.02, 0.98)
    expected = list(test_frame[["subject_id", "sleep_date", "lifelog_date"]].itertuples(index=False, name=None))
    actual = list(out[["subject_id", "sleep_date", "lifelog_date"]].itertuples(index=False, name=None))
    if actual != expected:
        raise ValueError("sample submission rows do not match test feature rows")
    return out


def summarize(
    pretext_metrics: pd.DataFrame,
    probe_metrics: pd.DataFrame,
    nn_metrics: pd.DataFrame,
    leakage: pd.DataFrame,
    candidate_file: str,
) -> dict[str, Any]:
    pretext = pretext_metrics.sort_values("component_corr_lift_vs_null", ascending=False)
    subject_all = probe_metrics[(probe_metrics["split"].eq("subject_heldout")) & (probe_metrics["target"].eq("all"))]
    chrono_all = probe_metrics[(probe_metrics["split"].eq("chronological_holdout")) & (probe_metrics["target"].eq("all"))]
    prior_subject = subject_all[subject_all["feature_set"].eq("prior_only")]
    world_subject = subject_all[subject_all["feature_set"].eq("subject_relative_world_model_full_calibrated10")]
    world_subject_uncalibrated = subject_all[subject_all["feature_set"].eq("subject_relative_world_model_full")]
    raw_subject = subject_all[subject_all["feature_set"].eq("raw_lifelog_pca")]
    hybrid_subject = subject_all[subject_all["feature_set"].eq("hybrid_absolute_relative_world_model")]
    best_subject = subject_all.sort_values("logloss").head(1)
    nn_all = nn_metrics[nn_metrics["target"].eq("all")].sort_values("lift", ascending=False)
    return {
        "package": "human_state_world_model_core",
        "status": "human_state_world_model_core_ready",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "uses_label_as_pretext_target": False,
        "core_adapter_boundary": "candidate submission is downstream probe only, not core evidence",
        "best_pretext": None if pretext.empty else pretext.iloc[0].to_dict(),
        "subject_prior_logloss": None if prior_subject.empty else float(prior_subject["logloss"].iloc[0]),
        "subject_raw_pca_logloss": None if raw_subject.empty else float(raw_subject["logloss"].iloc[0]),
        "subject_world_full_logloss": None
        if world_subject_uncalibrated.empty
        else float(world_subject_uncalibrated["logloss"].iloc[0]),
        "subject_world_calibrated_logloss": None if world_subject.empty else float(world_subject["logloss"].iloc[0]),
        "subject_hybrid_world_logloss": None if hybrid_subject.empty else float(hybrid_subject["logloss"].iloc[0]),
        "subject_world_delta_vs_prior": None
        if prior_subject.empty or world_subject.empty
        else float(world_subject["logloss"].iloc[0] - prior_subject["logloss"].iloc[0]),
        "subject_world_delta_vs_raw_pca": None
        if raw_subject.empty or world_subject.empty
        else float(world_subject["logloss"].iloc[0] - raw_subject["logloss"].iloc[0]),
        "subject_best_probe": None if best_subject.empty else best_subject.iloc[0].to_dict(),
        "chronological_best_probe": None if chrono_all.empty else chrono_all.sort_values("logloss").iloc[0].to_dict(),
        "best_neighbor_consistency": None if nn_all.empty else nn_all.iloc[0].to_dict(),
        "subject_leakage": leakage.to_dict(orient="records"),
        "candidate_file": candidate_file,
    }


def build_markdown(
    summary: dict[str, Any],
    pretext_metrics: pd.DataFrame,
    probe_metrics: pd.DataFrame,
    nn_metrics: pd.DataFrame,
    leakage: pd.DataFrame,
    candidate_file: str,
) -> str:
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
    best_pretext = summary.get("best_pretext") or {}
    verdict = "core_positive" if (summary.get("subject_world_delta_vs_prior") or 1.0) < 0 else "core_mixed_or_negative"
    return f"""# Human-State World Model Core

## 한 줄 요약

HS-JEPA를 competition 후처리에서 떼어내고, label 없이 학습되는
Human-State World Model로 직접 구현한 실험이다.

```text
visible human-life context views
  -> predict masked / future / cohort hidden human-state representations
  -> freeze representation
  -> simple downstream probe로만 Q/S label 검증
```

## 판정

- verdict: `{verdict}`
- public LB ledger 사용: `{summary["uses_public_score_ledger"]}`
- prior submission probability 사용: `{summary["uses_prior_submission_probabilities"]}`
- proprietary embedding API 사용: `{summary["uses_proprietary_embedding_api"]}`
- label을 pretext target으로 사용: `{summary["uses_label_as_pretext_target"]}`

## 왜 이것이 HS-JEPA Core인가

이 실험의 학습 목표는 Q1/Q2/Q3/S1/S2/S3/S4를 직접 맞히는 것이 아니다.
수면/활동/앱/모빌리티/캘린더 view 중 일부만 보고, 가려진 다른 view의 latent state와
다음 episode state를 예측한다.

즉 target은 label이 아니라 hidden human-state representation이다.

## Architecture Contract

```text
Human Context Tokenizer
  -> semantic views: calendar, phone, body, app/social, mobility/environment
Context Encoder
  -> available views only
Target Encoder
  -> masked target-view PCA state / future episode state
Predictor
  -> ridge JEPA predictor under subject-heldout OOF
Energy
  -> prediction residual and cohort-normal distance
Frozen Probe
  -> subject-heldout / chronological label probe
```

## Pretext 결과

- best pretext target: `{best_pretext.get("target", "NA")}`
- best component-corr lift vs null: `{format_float(best_pretext.get("component_corr_lift_vs_null"), 6)}`
- best R2 lift vs null: `{format_float(best_pretext.get("r2_lift_vs_null"), 6)}`

{markdown_table(
    pretext_metrics.sort_values("component_corr_lift_vs_null", ascending=False).head(10),
    ["task", "target", "component_corr", "null_component_corr", "component_corr_lift_vs_null", "r2_lift_vs_null"],
)}

## Frozen Subject-Heldout Probe

이 표는 world model representation을 freeze한 뒤, 단순 linear probe만 붙인 결과다.
`_calibrated10`은 fold prior에서 10%만 움직이는 고정 low-trust calibration probe다.
이는 representation ranking 신호와 probability overconfidence를 분리하기 위한 장치이며,
public LB나 submission 결과를 사용하지 않는다.

{markdown_table(subject_all, ["feature_set", "logloss", "auc"])}

## Chronological Row-Heldout Probe

각 subject의 앞쪽 날짜로 학습하고 뒤쪽 날짜를 검증한 결과다.

{markdown_table(chrono_all, ["feature_set", "logloss", "auc"])}

## Nearest-Neighbor State Consistency

{markdown_table(
    nn_metrics[nn_metrics["target"].eq("all")].sort_values("lift", ascending=False),
    ["feature_set", "neighbor_match_rate", "random_match_rate", "lift"],
)}

## Subject Leakage Diagnostic

representation이 human-state가 아니라 subject identity만 외우는지 보기 위한 진단이다.

{markdown_table(
    leakage.sort_values("subject_id_accuracy", ascending=False),
    ["feature_set", "subject_id_accuracy", "chance_accuracy", "leakage_lift_vs_chance"],
)}

## Downstream Probe Candidate

- file: `{candidate_file}`

이 파일은 HS-JEPA core 증거가 아니다.
core representation을 competition label로 번역한 downstream probe candidate일 뿐이다.

## 현재 해석

이 실험이 positive이면 다음 주장이 가능하다.

```text
HS-JEPA core는 label 없이 학습한 human-state world representation만으로도
subject-heldout label manifold를 prior/raw baseline보다 더 선형적으로 만든다.
```

negative이면 다음 경계가 생긴다.

```text
masked/future human-state prediction은 가능하지만,
그 representation이 Q/S label을 일반화 가능하게 만들지는 아직 못했다.
```
"""


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frame, labels = load_frames()
    views = make_views(frame)
    if len(views) < 2:
        raise ValueError("not enough semantic views to train HS-JEPA world model")

    raw_view_cols = sorted({col for view in views for col in view.columns})
    absolute_state, absolute_metrics = fit_world_variant(frame, views, "absolute")
    relative_frame = subject_relative_frame(frame, raw_view_cols)
    relative_state, relative_metrics = fit_world_variant(relative_frame, views, "subject_relative")
    pretext_metrics = pd.concat([absolute_metrics, relative_metrics], ignore_index=True, sort=False)
    state = pd.concat([absolute_state, relative_state], axis=1)
    state = pd.concat(
        [frame[["subject_id", "sleep_date", "lifelog_date", "split", "metric_row"]].reset_index(drop=True), state.reset_index(drop=True)],
        axis=1,
    )

    catalog = catalog_features(frame)
    raw_cols = raw_view_cols
    all_cols = state_columns(state)
    abs_cols = variant_columns(state, "absolute")
    rel_cols = variant_columns(state, "subject_relative")
    combined = pd.concat([frame.reset_index(drop=True), state.drop(columns=["subject_id", "sleep_date", "lifelog_date", "split", "metric_row"])], axis=1)
    feature_sets = {
        "prior_only": [],
        "raw_lifelog_pca": raw_cols,
        "existing_cohort_human_state": catalog.core_state,
        "absolute_world_model_predicted": abs_cols["world_predicted_state"],
        "absolute_world_model_full": abs_cols["world_full_state"],
        "subject_relative_world_model_predicted": rel_cols["world_predicted_state"],
        "subject_relative_world_model_energy": rel_cols["world_surprise_energy"],
        "subject_relative_world_model_full": rel_cols["world_full_state"],
        "hybrid_absolute_relative_world_model": sorted(set(all_cols["world_full_state"])),
        "raw_plus_subject_relative_world_model": sorted(set(raw_cols + rel_cols["world_full_state"])),
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
    probe_metrics = pd.concat(
        [probe_metrics, calibrated_probe_metrics(probe_predictions)],
        ignore_index=True,
        sort=False,
    )
    nn_metrics = neighbor_consistency(train_frame, train_features, feature_sets)
    leakage = subject_leakage_probe(
        train_frame,
        train_features,
        {
            key: value
            for key, value in feature_sets.items()
            if key not in {"prior_only", "raw_plus_subject_relative_world_model"}
        },
    )

    test_mask = frame["split"].eq("test").to_numpy()
    test_frame = frame.loc[test_mask].reset_index(drop=True)
    test_features = combined.loc[test_mask].reset_index(drop=True)
    submission = build_downstream_probe_submission(
        train_frame,
        test_frame,
        train_features,
        test_features,
        rel_cols["world_full_state"],
    )
    candidate_name = f"submission_hsjepa_human_state_world_model_probe_{short_hash(submission)}_uploadsafe.csv"
    candidate_path = ROOT / candidate_name
    submission.to_csv(candidate_path, index=False)
    submission.to_csv(OUT_DIR / candidate_name, index=False)

    summary = summarize(pretext_metrics, probe_metrics, nn_metrics, leakage, candidate_name)

    state.to_csv(OUT_DIR / "human_state_world_model_state.csv", index=False)
    pretext_metrics.to_csv(OUT_DIR / "human_state_world_model_pretext_metrics.csv", index=False)
    probe_metrics.to_csv(OUT_DIR / "human_state_world_model_probe_metrics.csv", index=False)
    probe_predictions.to_csv(OUT_DIR / "human_state_world_model_probe_predictions.csv", index=False)
    nn_metrics.to_csv(OUT_DIR / "human_state_world_model_neighbor_consistency.csv", index=False)
    leakage.to_csv(OUT_DIR / "human_state_world_model_subject_leakage.csv", index=False)
    with (OUT_DIR / "human_state_world_model_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=False)
    markdown = build_markdown(summary, pretext_metrics, probe_metrics, nn_metrics, leakage, candidate_name)
    (OUT_DIR / "HUMAN_STATE_WORLD_MODEL_CORE_KO.md").write_text(markdown, encoding="utf-8")
    PAPER_DOC.write_text(markdown, encoding="utf-8")

    print(
        json.dumps(
            {
                "status": summary["status"],
                "candidate_file": candidate_name,
                "subject_world_delta_vs_prior": summary["subject_world_delta_vs_prior"],
                "subject_world_delta_vs_raw_pca": summary["subject_world_delta_vs_raw_pca"],
                "best_pretext_lift": None
                if summary["best_pretext"] is None
                else summary["best_pretext"]["component_corr_lift_vs_null"],
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
