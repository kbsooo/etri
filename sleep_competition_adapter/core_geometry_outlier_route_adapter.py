#!/usr/bin/env python3
"""Core-geometry outlier-route adapter.

This is a high-risk HS-JEPA adapter experiment. It starts from the current
frontier probability field only as a calibrated probability prior, then uses
public-free core-state geometry to propose row support and train-label outlier
shifts to choose target directions.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "sleep_competition_adapter" / "outputs" / "core_geometry_outlier_route_adapter"
FEATURE_PATH = ROOT / "team_experiments" / "cohort_hsjepa" / "cohort_human_state_features.csv"
LABEL_PATH = ROOT / "data" / "ch2026_metrics_train.csv"
TEACHER_CELL_PATH = ROOT / "sleep_competition_adapter" / "outputs" / "og_only_assignment_teacher_ranked_cells.csv"
BASE_SUBMISSION = ROOT / "submission_hsjepa_frontier_silence_positive_path_overshoot_sensor_1e013277_uploadsafe.csv"
SAMPLE_SUBMISSION = ROOT / "data" / "ch2026_submission_sample.csv"

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
CORE_COLS = [
    "human_state_latent_0",
    "human_state_latent_1",
    "human_state_latent_2",
    "human_state_latent_3",
    "human_state_latent_4",
    "human_state_latent_5",
    "human_state_latent_6",
    "human_state_latent_7",
    "peer_group",
    "dist_to_subject_normal",
    "dist_to_peer_normal",
    "subject_minus_peer_dist",
    "subject_outlier_rank",
    "peer_outlier_rank",
    "cohort_outlier_score",
]
OUTLIER_SCORE_COLS = ["dist_to_subject_normal", "dist_to_peer_normal", "cohort_outlier_score"]


def logit(values: np.ndarray) -> np.ndarray:
    values = np.clip(values.astype(float), 1e-6, 1 - 1e-6)
    return np.log(values / (1 - values))


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-values))


def rank01(values: np.ndarray | pd.Series) -> np.ndarray:
    series = pd.Series(values, dtype="float64")
    if series.notna().sum() <= 1:
        return np.zeros(len(series), dtype=float)
    return series.rank(method="average", pct=True).fillna(0.5).to_numpy(dtype=float)


def short_hash(frame: pd.DataFrame) -> str:
    arr = np.asarray(frame[TARGETS], dtype=np.float64)
    return hashlib.sha256(arr.round(10).tobytes()).hexdigest()[:8]


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    features = pd.read_csv(FEATURE_PATH)
    labels = pd.read_csv(LABEL_PATH)
    base = pd.read_csv(BASE_SUBMISSION)
    sample = pd.read_csv(SAMPLE_SUBMISSION)
    if list(base.columns) != list(sample.columns):
        raise ValueError("base submission schema does not match sample schema")
    train_mask = features["split"].eq("train")
    if int(train_mask.sum()) != len(labels):
        raise ValueError("feature train rows do not match label rows")
    features = features.copy()
    features.loc[train_mask, TARGETS] = labels[TARGETS].to_numpy()
    return features, labels, base, sample


def row_teacher_labels(test_features: pd.DataFrame) -> pd.DataFrame:
    cells = pd.read_csv(TEACHER_CELL_PATH)
    labels = (
        cells.groupby(["teacher", "row"], observed=True)["teacher_row_has_action"]
        .max()
        .reset_index()
    )
    out = pd.DataFrame({"row": test_features["metric_row"].astype(int).to_numpy()})
    for teacher in sorted(labels["teacher"].unique()):
        mapping = labels[labels["teacher"].eq(teacher)].set_index("row")["teacher_row_has_action"]
        out[f"teacher_support_{teacher}"] = out["row"].map(mapping).fillna(0).astype(int)
    return out


def fit_cross_teacher_support(test_features: pd.DataFrame, teacher_labels: pd.DataFrame) -> pd.DataFrame:
    teacher_cols = [col for col in teacher_labels.columns if col.startswith("teacher_support_")]
    if len(teacher_cols) < 2:
        raise ValueError("at least two teacher support columns are required")
    x = test_features[CORE_COLS].replace([np.inf, -np.inf], np.nan)
    scores = []
    for teacher_col in teacher_cols:
        y = teacher_labels[teacher_col].to_numpy(dtype=int)
        model = make_pipeline(
            SimpleImputer(strategy="median"),
            StandardScaler(),
            HistGradientBoostingClassifier(
                learning_rate=0.04,
                max_leaf_nodes=8,
                l2_regularization=0.25,
                random_state=20260612,
            ),
        )
        model.fit(x, y)
        scores.append(model.predict_proba(x)[:, 1])
    score_arr = np.vstack(scores)
    out = teacher_labels.copy()
    out["core_cross_teacher_support"] = score_arr.mean(axis=0)
    out["core_teacher_disagreement"] = score_arr.std(axis=0)
    out["core_support_rank"] = rank01(out["core_cross_teacher_support"])
    return out


def target_outlier_laws(train_features: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for target in TARGETS:
        best = None
        for score_col in OUTLIER_SCORE_COLS:
            score = pd.to_numeric(train_features[score_col], errors="coerce")
            low = score <= score.quantile(0.25)
            high = score >= score.quantile(0.75)
            low_rate = float(train_features.loc[low, target].mean())
            high_rate = float(train_features.loc[high, target].mean())
            shift = high_rate - low_rate
            record = {
                "target": target,
                "score": score_col,
                "low_rate": low_rate,
                "high_rate": high_rate,
                "shift": shift,
                "abs_shift": abs(shift),
                "direction": 1 if shift >= 0 else -1,
            }
            if best is None or record["abs_shift"] > best["abs_shift"]:
                best = record
        rows.append(best)
    return pd.DataFrame(rows)


def build_candidate(
    features: pd.DataFrame,
    base: pd.DataFrame,
    support: pd.DataFrame,
    laws: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    test = features[features["split"].eq("test")].copy().reset_index(drop=True)
    pred = base.copy()
    logits = logit(pred[TARGETS].to_numpy(dtype=float))
    selected_rows = support["core_support_rank"] >= support["core_support_rank"].quantile(0.72)
    row_weight = np.clip((support["core_support_rank"].to_numpy() - 0.72) / 0.28, 0, 1)
    row_weight *= np.clip(1.0 - support["core_teacher_disagreement"].to_numpy(), 0.35, 1.0)

    action_rows = []
    for target_idx, target in enumerate(TARGETS):
        law = laws[laws["target"].eq(target)].iloc[0]
        score_rank = rank01(test[str(law["score"])])
        target_weight = min(1.0, float(law["abs_shift"]) / 0.16)
        move = 0.28 * int(law["direction"]) * row_weight * score_rank * target_weight
        if target in {"S1", "S3", "S4"}:
            move *= 0.80
        if target == "Q2":
            move *= 1.15
        mask = selected_rows.to_numpy() & (np.abs(move) > 0.015)
        logits[mask, target_idx] += move[mask]
        for row in np.where(mask)[0]:
            action_rows.append(
                {
                    "row": int(row),
                    "subject_id": test.loc[row, "subject_id"],
                    "target": target,
                    "target_idx": target_idx,
                    "outlier_score": str(law["score"]),
                    "law_shift": float(law["shift"]),
                    "core_support_rank": float(support.loc[row, "core_support_rank"]),
                    "core_teacher_disagreement": float(support.loc[row, "core_teacher_disagreement"]),
                    "row_outlier_rank": float(score_rank[row]),
                    "logit_move": float(move[row]),
                }
            )

    pred[TARGETS] = np.clip(sigmoid(logits), 1e-5, 1 - 1e-5)
    return pred, pd.DataFrame(action_rows)


def uploadsafe_copy(pred: pd.DataFrame, sample: pd.DataFrame) -> pd.DataFrame:
    out = sample.copy()
    out[TARGETS] = pred[TARGETS].to_numpy(dtype=float)
    return out


def run() -> dict[str, object]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    features, _, base, sample = load_inputs()
    test = features[features["split"].eq("test")].copy().reset_index(drop=True)
    train = features[features["split"].eq("train")].copy().reset_index(drop=True)
    teachers = row_teacher_labels(test)
    support = fit_cross_teacher_support(test, teachers)
    laws = target_outlier_laws(train)
    pred, audit = build_candidate(features, base, support, laws)
    upload = uploadsafe_copy(pred, sample)
    file_hash = short_hash(upload)
    submission_name = f"submission_hsjepa_core_geometry_outlier_route_bigbet_{file_hash}_uploadsafe.csv"
    output_path = OUT_DIR / submission_name
    root_path = ROOT / submission_name
    upload.to_csv(output_path, index=False)
    upload.to_csv(root_path, index=False)
    support.to_csv(OUT_DIR / "core_geometry_row_support.csv", index=False)
    laws.to_csv(OUT_DIR / "train_outlier_target_laws.csv", index=False)
    audit.to_csv(OUT_DIR / "core_geometry_outlier_route_action_audit.csv", index=False)

    readout = {
        "package": "core_geometry_outlier_route_adapter",
        "status": "bigbet_candidate_ready",
        "uses_public_score_ledger": False,
        "base_probability_prior": str(BASE_SUBMISSION.relative_to(ROOT)),
        "feature_source": str(FEATURE_PATH.relative_to(ROOT)),
        "submission_file": submission_name,
        "root_submission_file": submission_name,
        "changed_cells": int(len(audit)),
        "changed_rows": int(audit["row"].nunique()) if len(audit) else 0,
        "mean_abs_logit_move": float(audit["logit_move"].abs().mean()) if len(audit) else 0.0,
        "max_abs_logit_move": float(audit["logit_move"].abs().max()) if len(audit) else 0.0,
        "target_action_counts": audit["target"].value_counts().to_dict() if len(audit) else {},
        "worldview": (
            "Core-state geometry can identify row support; target direction should follow "
            "train-observed personal/cohort outlier laws rather than public-score equations."
        ),
        "failure_interpretation": (
            "If this fails, core geometry is useful as support diagnostic but not yet "
            "action-grade without listener-specific target routing."
        ),
    }
    (OUT_DIR / "core_geometry_outlier_route_readout.json").write_text(
        json.dumps(readout, indent=2, ensure_ascii=False)
    )
    (OUT_DIR / "CORE_GEOMETRY_OUTLIER_ROUTE_ADAPTER_KO.md").write_text(
        f"""# Core Geometry Outlier-Route Adapter

## 목적

`lifelog_core_state_evidence`에서 core-state geometry가 row-action support를 강하게 재발견한다는 결과가 나왔다.
이 adapter는 그 결과를 실제 submission action으로 번역하는 high-risk big-bet이다.

## 세계관

```text
core-state geometry가 고른 row는 action support를 받을 가능성이 높다.
target 방향은 public equation이 아니라 train에서 관측된 personal/cohort outlier law를 따른다.
```

## 생성 파일

- `{submission_name}`
- `sleep_competition_adapter/outputs/core_geometry_outlier_route_adapter/core_geometry_row_support.csv`
- `sleep_competition_adapter/outputs/core_geometry_outlier_route_adapter/train_outlier_target_laws.csv`
- `sleep_competition_adapter/outputs/core_geometry_outlier_route_adapter/core_geometry_outlier_route_action_audit.csv`

## 핵심 수치

- changed rows: `{readout["changed_rows"]}`
- changed cells: `{readout["changed_cells"]}`
- mean abs logit move: `{readout["mean_abs_logit_move"]:.6f}`
- max abs logit move: `{readout["max_abs_logit_move"]:.6f}`
- target action counts: `{readout["target_action_counts"]}`

## 해석

이 후보는 보수형 개선 후보가 아니다. 좋아지면 HS-JEPA core geometry가 public-free row support뿐 아니라 target outlier-route action으로도 번역 가능하다는 뜻이다.

나빠지면 core geometry는 support diagnostic으로는 강하지만, target-specific listener route 없이는 action-grade가 아니라는 뜻이다.
"""
    )
    return readout


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))
