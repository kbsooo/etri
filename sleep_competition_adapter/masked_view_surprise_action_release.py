#!/usr/bin/env python3
"""Masked-view surprise energy release for HS-JEPA.

This experiment is meant to be a paper-facing bridge between the reusable
HS-JEPA core and the sleep-competition adapter.

Core question:
    If one lifelog view is hidden, can the remaining views predict its latent
    representation?  When that prediction fails, does the residual energy mark
    a meaningful human-state episode?

Adapter question:
    Can that JEPA-style residual energy select row-target actions without
    looking at public LB or previous action-teacher labels?
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "sleep_competition_adapter" / "outputs" / "masked_view_surprise_action_release"
FEATURE_PATH = ROOT / "team_experiments" / "cohort_hsjepa" / "cohort_human_state_features.csv"
FEATURE_BUILDER = ROOT / "team_experiments" / "cohort_hsjepa" / "cohort_hsjepa_experiment.py"
LABEL_PATH = ROOT / "data" / "ch2026_metrics_train.csv"
SAMPLE_SUBMISSION = ROOT / "data" / "ch2026_submission_sample.csv"

PROBABILITY_PRIOR_FILE = ROOT / "submission_hsjepa_frontier_silence_positive_path_overshoot_sensor_1e013277_uploadsafe.csv"
FRONTIER_BASE_FILE = ROOT / "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"
FRONTIER_REFERENCE_FILES = {
    "row_state_vector_frontier": ROOT / "submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv",
    "frontier_active_silence": PROBABILITY_PRIOR_FILE,
}

KEYS = ["subject_id", "sleep_date", "lifelog_date"]
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY_COLS = set(KEYS + ["split", "metric_row", "lifelog_date_str", "sleep_date_str"])
LABEL_INFORMED_PREFIXES = (
    "peer_margin_",
    "q_group_peer_margin",
    "s_group_peer_margin",
    "target_route_margin",
)
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


@dataclass(frozen=True)
class FeatureCatalog:
    raw_numeric: list[str]
    core_state: list[str]
    label_informed: list[str]


def logit(values: np.ndarray) -> np.ndarray:
    p = np.clip(np.asarray(values, dtype=np.float64), 1e-6, 1 - 1e-6)
    return np.log(p / (1.0 - p))


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(values, dtype=np.float64)))


def rank01(values: Iterable[float]) -> np.ndarray:
    series = pd.Series(values, dtype="float64").replace([np.inf, -np.inf], np.nan)
    if series.notna().sum() <= 1 or series.nunique(dropna=True) <= 1:
        return np.full(len(series), 0.5, dtype=np.float64)
    return series.rank(method="average", pct=True).fillna(0.5).to_numpy(dtype=np.float64)


def zscore_from_train(train_values: np.ndarray, values: np.ndarray) -> np.ndarray:
    train_values = np.asarray(train_values, dtype=np.float64)
    values = np.asarray(values, dtype=np.float64)
    mean = float(np.nanmean(train_values))
    std = float(np.nanstd(train_values))
    if not np.isfinite(std) or std <= 1e-9:
        return np.zeros_like(values, dtype=np.float64)
    return (values - mean) / std


def short_hash(frame: pd.DataFrame) -> str:
    return hashlib.sha256(frame[TARGETS].to_numpy(dtype=np.float64).round(10).tobytes()).hexdigest()[:8]


def ensure_feature_table() -> None:
    if FEATURE_PATH.exists():
        return
    subprocess.run(["python3", str(FEATURE_BUILDER)], cwd=ROOT, check=True)


def read_submission(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"])
    return frame.sort_values(KEYS).reset_index(drop=True)


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ensure_feature_table()
    features = pd.read_csv(FEATURE_PATH, parse_dates=["sleep_date", "lifelog_date"])
    labels = pd.read_csv(LABEL_PATH, parse_dates=["sleep_date", "lifelog_date"])
    sample = read_submission(SAMPLE_SUBMISSION)
    prior = read_submission(PROBABILITY_PRIOR_FILE)
    train_mask = features["split"].eq("train")
    if int(train_mask.sum()) != len(labels):
        raise ValueError("feature train rows do not match label rows")
    features = features.copy()
    features.loc[train_mask, TARGETS] = labels[TARGETS].to_numpy()
    return features, labels, sample, prior


def catalog_features(frame: pd.DataFrame) -> FeatureCatalog:
    numeric_cols = [
        col
        for col in frame.columns
        if pd.api.types.is_numeric_dtype(frame[col])
        and col not in KEY_COLS
        and col not in TARGETS
    ]
    label_informed = [col for col in numeric_cols if col.startswith(LABEL_INFORMED_PREFIXES)]
    core_state = [col for col in CORE_COLS if col in numeric_cols]
    raw_numeric = [
        col
        for col in numeric_cols
        if col not in set(core_state)
        and col not in set(label_informed)
    ]
    return FeatureCatalog(raw_numeric=raw_numeric, core_state=core_state, label_informed=label_informed)


def finite_matrix(frame: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    return frame[cols].replace([np.inf, -np.inf], np.nan)


def view_columns(catalog: FeatureCatalog) -> dict[str, list[str]]:
    prefixes = {
        "calendar_rhythm": (
            "dayofweek",
            "is_weekend",
            "dayofmonth",
            "month_start_proximity",
            "month_end",
        ),
        "phone_device": (
            "phone_charging_",
            "screen_use_",
            "phone_activity_",
            "phone_light_",
            "watch_light_",
        ),
        "body_sleep_activity": (
            "pedo_",
            "step_",
            "walking_",
            "running_",
            "distance_",
            "calories_",
            "speed_",
            "active_",
            "night_step_",
            "hr_",
        ),
        "app_social_context": ("usage_", "night_usage_"),
        "mobility_environment": ("gps_", "wifi_", "ble_", "ambience_"),
    }
    raw = set(catalog.raw_numeric)
    views: dict[str, list[str]] = {}
    for name, pref in prefixes.items():
        cols = [col for col in catalog.raw_numeric if col in pref or col.startswith(pref)]
        cols = [col for col in cols if col in raw]
        if len(cols) >= 2:
            views[name] = cols
    return views


def fit_view_predictor(
    train_frame: pd.DataFrame,
    apply_frame: pd.DataFrame,
    x_cols: list[str],
    y_cols: list[str],
) -> np.ndarray:
    x_imputer = SimpleImputer(strategy="median")
    x_scaler = StandardScaler()
    x_train = x_scaler.fit_transform(x_imputer.fit_transform(finite_matrix(train_frame, x_cols)))
    x_apply = x_scaler.transform(x_imputer.transform(finite_matrix(apply_frame, x_cols)))

    y_imputer = SimpleImputer(strategy="median")
    y_scaler = StandardScaler()
    y_train_scaled = y_scaler.fit_transform(y_imputer.fit_transform(finite_matrix(train_frame, y_cols)))
    y_apply_scaled = y_scaler.transform(y_imputer.transform(finite_matrix(apply_frame, y_cols)))
    dims = max(1, min(4, y_train_scaled.shape[1], y_train_scaled.shape[0] - 1))
    pca = PCA(n_components=dims, random_state=20260613)
    y_train = pca.fit_transform(y_train_scaled)
    y_apply = pca.transform(y_apply_scaled)

    model = Ridge(alpha=12.0)
    model.fit(x_train, y_train)
    pred = model.predict(x_apply)
    return np.sqrt(np.mean((pred - y_apply) ** 2, axis=1))


def masked_view_surprise_energy(frame: pd.DataFrame, catalog: FeatureCatalog) -> tuple[pd.DataFrame, pd.DataFrame]:
    views = view_columns(catalog)
    all_view_cols = sorted({col for cols in views.values() for col in cols})
    train = frame[frame["split"].eq("train")].copy().reset_index(drop=True)
    test = frame[frame["split"].eq("test")].copy().reset_index(drop=True)
    groups = train["subject_id"].astype(str).to_numpy()
    n_splits = max(2, min(5, len(np.unique(groups))))
    splitter = GroupKFold(n_splits=n_splits)

    train_energy = pd.DataFrame({"metric_row": train["metric_row"].astype(int).to_numpy()})
    test_energy = pd.DataFrame({"metric_row": test["metric_row"].astype(int).to_numpy()})
    view_rows: list[dict[str, Any]] = []

    for target_view, y_cols in views.items():
        x_cols = [col for col in all_view_cols if col not in set(y_cols)]
        if len(x_cols) < 2:
            continue
        oof = np.zeros(len(train), dtype=np.float64)
        for tr_idx, va_idx in splitter.split(train, groups=groups):
            oof[va_idx] = fit_view_predictor(
                train.iloc[tr_idx],
                train.iloc[va_idx],
                x_cols,
                y_cols,
            )
        test_residual = fit_view_predictor(train, test, x_cols, y_cols)
        train_energy[f"surprise_{target_view}"] = oof
        test_energy[f"surprise_{target_view}"] = test_residual
        train_energy[f"surprise_{target_view}_rank"] = rank01(oof)
        test_energy[f"surprise_{target_view}_rank"] = rank01(test_residual)
        view_rows.append(
            {
                "target_view": target_view,
                "context_feature_count": len(x_cols),
                "target_feature_count": len(y_cols),
                "train_mean_residual": float(np.mean(oof)),
                "test_mean_residual": float(np.mean(test_residual)),
                "test_minus_train_mean": float(np.mean(test_residual) - np.mean(oof)),
                "test_top_quartile_cut": float(np.quantile(test_residual, 0.75)),
            }
        )

    energy_cols = [col for col in train_energy.columns if col.startswith("surprise_") and not col.endswith("_rank")]
    train_z = np.column_stack([
        zscore_from_train(train_energy[col].to_numpy(), train_energy[col].to_numpy())
        for col in energy_cols
    ])
    test_z = np.column_stack([
        zscore_from_train(train_energy[col].to_numpy(), test_energy[col].to_numpy())
        for col in energy_cols
    ])
    train_energy["masked_surprise_energy_mean"] = train_z.mean(axis=1)
    train_energy["masked_surprise_energy_max"] = train_z.max(axis=1)
    train_energy["masked_surprise_energy_disagreement"] = train_z.std(axis=1)
    test_energy["masked_surprise_energy_mean"] = test_z.mean(axis=1)
    test_energy["masked_surprise_energy_max"] = test_z.max(axis=1)
    test_energy["masked_surprise_energy_disagreement"] = test_z.std(axis=1)
    for col in [
        "masked_surprise_energy_mean",
        "masked_surprise_energy_max",
        "masked_surprise_energy_disagreement",
    ]:
        train_energy[f"{col}_rank"] = rank01(train_energy[col])
        test_energy[f"{col}_rank"] = rank01(test_energy[col])

    return pd.concat([train_energy, test_energy], keys=["train", "test"], names=["split_key"]).reset_index(level=0), pd.DataFrame(view_rows)


def target_surprise_laws(features: pd.DataFrame, energy: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    train = features[features["split"].eq("train")].copy().reset_index(drop=True)
    train_energy = energy[energy["split_key"].eq("train")].copy().reset_index(drop=True)
    score_cols = [
        col
        for col in train_energy.columns
        if col.startswith("surprise_") and col.endswith("_rank")
    ] + [
        "masked_surprise_energy_mean_rank",
        "masked_surprise_energy_max_rank",
        "masked_surprise_energy_disagreement_rank",
    ]
    score_cols = sorted(set([col for col in score_cols if col in train_energy.columns]))
    rows: list[dict[str, Any]] = []
    best_rows: list[dict[str, Any]] = []
    for target in TARGETS:
        best: dict[str, Any] | None = None
        for score_col in score_cols:
            score = pd.to_numeric(train_energy[score_col], errors="coerce")
            low = score <= score.quantile(0.25)
            high = score >= score.quantile(0.75)
            low_rate = float(train.loc[low, target].mean())
            high_rate = float(train.loc[high, target].mean())
            shift = high_rate - low_rate
            record = {
                "target": target,
                "surprise_score": score_col,
                "low_rate": low_rate,
                "high_rate": high_rate,
                "shift": shift,
                "abs_shift": abs(shift),
                "direction": 1 if shift >= 0 else -1,
            }
            rows.append(record)
            if best is None or record["abs_shift"] > best["abs_shift"]:
                best = record
        if best is not None:
            best_rows.append(best)
    return pd.DataFrame(best_rows), pd.DataFrame(rows)


def build_neighbor_margins(features: pd.DataFrame, labels: pd.DataFrame) -> pd.DataFrame:
    train = features[features["split"].eq("train")].copy().reset_index(drop=True)
    test = features[features["split"].eq("test")].copy().reset_index(drop=True)
    imputer = SimpleImputer(strategy="median")
    scaler = StandardScaler()
    x_train = scaler.fit_transform(imputer.fit_transform(finite_matrix(train, CORE_COLS)))
    x_test = scaler.transform(imputer.transform(finite_matrix(test, CORE_COLS)))
    k = min(35, len(train))
    nn = NearestNeighbors(n_neighbors=k, metric="euclidean")
    nn.fit(x_train)
    distances, indices = nn.kneighbors(x_test)
    y = labels[TARGETS].astype(float).to_numpy()
    local_mean = y[indices].mean(axis=1)
    global_prior = y.mean(axis=0)
    out = pd.DataFrame({
        "metric_row": test["metric_row"].astype(int).to_numpy(),
        "neighbor_distance_mean": distances.mean(axis=1),
        "neighbor_density_rank": rank01(1.0 / (1.0 + distances.mean(axis=1))),
    })
    for idx, target in enumerate(TARGETS):
        out[f"neighbor_mean_{target}"] = local_mean[:, idx]
        out[f"neighbor_margin_{target}"] = local_mean[:, idx] - global_prior[idx]
    return out


def frontier_active_rows(base: pd.DataFrame, ref: pd.DataFrame) -> np.ndarray:
    delta = np.abs(logit(ref[TARGETS].to_numpy(dtype=float)) - logit(base[TARGETS].to_numpy(dtype=float)))
    return (delta.max(axis=1) > 1e-4).astype(int)


def evaluate_frontier_overlap(test_energy: pd.DataFrame) -> pd.DataFrame:
    base = read_submission(FRONTIER_BASE_FILE)
    score = test_energy["masked_surprise_energy_mean_rank"].to_numpy(dtype=float)
    rows: list[dict[str, Any]] = []
    for name, path in FRONTIER_REFERENCE_FILES.items():
        if not path.exists():
            continue
        ref = read_submission(path)
        y = frontier_active_rows(base, ref)
        positives = int(y.sum())
        random_precision = float(positives / len(score)) if len(score) else 0.0
        for frac in [0.10, 0.15, 0.20, 0.25, 0.30]:
            k = max(1, int(round(len(score) * frac)))
            selected = np.argsort(-score)[:k]
            recall = float(y[selected].sum() / positives) if positives else 0.0
            precision = float(y[selected].mean())
            rows.append(
                {
                    "reference": name,
                    "top_fraction": frac,
                    "k": k,
                    "reference_rows": positives,
                    "overlap_rows": int(y[selected].sum()),
                    "recall": recall,
                    "random_recall_expectation": frac,
                    "recall_lift_vs_random": recall - frac,
                    "precision": precision,
                    "random_precision_expectation": random_precision,
                    "precision_lift_vs_random": precision - random_precision,
                    "mean_selected_surprise_rank": float(score[selected].mean()),
                }
            )
    return pd.DataFrame(rows)


def validate_submission(candidate: pd.DataFrame, sample: pd.DataFrame) -> dict[str, Any]:
    problems = []
    if list(candidate.columns) != list(sample.columns):
        problems.append("columns differ from sample submission")
    if len(candidate) != len(sample):
        problems.append("row count differs from sample submission")
    if candidate[KEYS].astype(str).to_numpy().tolist() != sample[KEYS].astype(str).to_numpy().tolist():
        problems.append("key rows differ from sample submission")
    values = candidate[TARGETS].to_numpy(dtype=float)
    if not np.isfinite(values).all():
        problems.append("non-finite probabilities")
    if values.min() < 0 or values.max() > 1:
        problems.append("probabilities outside [0, 1]")
    return {
        "valid": not problems,
        "problems": problems,
        "rows": int(len(candidate)),
        "probability_min": float(np.nanmin(values)),
        "probability_max": float(np.nanmax(values)),
    }


def build_candidate(
    features: pd.DataFrame,
    labels: pd.DataFrame,
    sample: pd.DataFrame,
    prior: pd.DataFrame,
    energy: pd.DataFrame,
    laws: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    test = features[features["split"].eq("test")].copy().reset_index(drop=True)
    test_energy = energy[energy["split_key"].eq("test")].copy().reset_index(drop=True)
    neighbor = build_neighbor_margins(features, labels)
    logits = logit(prior[TARGETS].to_numpy(dtype=float))
    support_rank = test_energy["masked_surprise_energy_mean_rank"].to_numpy(dtype=float)
    row_weight = np.clip((support_rank - 0.74) / 0.26, 0, 1)
    law_map = laws.set_index("target").to_dict("index")
    proposals: list[dict[str, Any]] = []

    for target_idx, target in enumerate(TARGETS):
        law = law_map[target]
        score_col = str(law["surprise_score"])
        target_rank = test_energy[score_col].to_numpy(dtype=float)
        margin = neighbor[f"neighbor_margin_{target}"].to_numpy(dtype=float)
        direction = int(law["direction"])
        direction_agrees = (np.sign(margin) == direction) | (np.abs(margin) < 0.025)
        route_weight = min(1.25, max(0.20, float(law["abs_shift"]) / 0.13))
        base_move = 0.44 * direction * row_weight * target_rank * route_weight
        base_move *= np.clip(0.55 + np.abs(margin) * 2.7, 0.55, 1.35)
        mask = (support_rank >= 0.74) & (target_rank >= 0.68) & direction_agrees & (np.abs(base_move) >= 0.020)
        for row in np.where(mask)[0]:
            proposals.append(
                {
                    "row": int(row),
                    "subject_id": test.loc[row, "subject_id"],
                    "target": target,
                    "target_idx": target_idx,
                    "surprise_score": score_col,
                    "masked_surprise_energy_mean_rank": float(support_rank[row]),
                    "target_surprise_rank": float(target_rank[row]),
                    "target_law_shift": float(law["shift"]),
                    "neighbor_margin": float(margin[row]),
                    "logit_move": float(base_move[row]),
                    "proposal_score": float(
                        support_rank[row]
                        * target_rank[row]
                        * route_weight
                        * (1.0 + min(1.0, abs(margin[row]) * 4.0))
                    ),
                }
            )

    proposal_df = pd.DataFrame(proposals)
    if not proposal_df.empty:
        target_caps = {"Q1": 45, "Q2": 90, "Q3": 70, "S1": 60, "S2": 90, "S3": 55, "S4": 65}
        selected_parts = []
        for target, cap in target_caps.items():
            part = proposal_df[proposal_df["target"].eq(target)].sort_values("proposal_score", ascending=False).head(cap)
            selected_parts.append(part)
        selected = pd.concat(selected_parts, ignore_index=True).sort_values("proposal_score", ascending=False)
        kept = []
        row_counts: dict[int, int] = {}
        for _, record in selected.iterrows():
            row = int(record["row"])
            if row_counts.get(row, 0) >= 4:
                continue
            kept.append(record)
            row_counts[row] = row_counts.get(row, 0) + 1
            if len(kept) >= 440:
                break
        action_audit = pd.DataFrame(kept)
    else:
        action_audit = proposal_df

    for _, record in action_audit.iterrows():
        logits[int(record["row"]), int(record["target_idx"])] += float(record["logit_move"])

    candidate = sample.copy()
    candidate[TARGETS] = np.clip(sigmoid(logits), 1e-5, 1 - 1e-5)
    return candidate, action_audit


def markdown_table(frame: pd.DataFrame, columns: list[str], max_rows: int = 20) -> str:
    if frame.empty:
        return "_No rows._"
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for _, row in frame.loc[:, columns].head(max_rows).iterrows():
        vals = []
        for col in columns:
            value = row[col]
            if isinstance(value, float):
                vals.append(f"{value:.6f}")
            else:
                vals.append(str(value))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def build_markdown(
    readout: dict[str, Any],
    view_metrics: pd.DataFrame,
    laws: pd.DataFrame,
    law_detail: pd.DataFrame,
    overlap: pd.DataFrame,
    action_audit: pd.DataFrame,
) -> str:
    top_detail = law_detail.sort_values("abs_shift", ascending=False).head(18)
    return f"""# Masked View Surprise Action Release

## 한 줄 요약

이 실험은 HS-JEPA core를 더 JEPA답게 해석한다. label을 바로 예측하지 않고, 보이는 생활 view로 가려진 생활 view representation을 예측한 뒤, 예측이 깨지는 residual energy를 hidden human-state episode로 사용한다.

## JEPA Mapping

| JEPA 구성요소 | 이 실험에서의 의미 |
| --- | --- |
| context | calendar, phone/device, body/sleep/activity, app/social, mobility/environment 중 target view를 제외한 나머지 view |
| target representation | 가려진 view의 PCA latent representation |
| predictor | context view들에서 target view latent를 예측하는 ridge predictor |
| energy | 예측 latent와 실제 target-view latent 사이의 residual norm |
| action decoder | surprise energy가 큰 row에서만 target prevalence law와 neighbor margin이 동의하는 action release |
| anti-shortcut check | public score/action teacher 없이 target shift와 frontier overlap을 사후 평가 |

## 사용하지 않은 정보

- public LB ledger: `{readout["uses_public_score_ledger"]}`
- action teacher for support: `{readout["uses_action_teacher_for_support"]}`
- proprietary embedding API: `{readout["uses_proprietary_embedding_api"]}`

후보 파일의 probability prior는 `{readout["probability_prior_file"]}`를 사용한다. 단, row/target 선택은 이 prior와의 차이가 아니라 masked-view surprise energy로 정한다.

## View Prediction Residual

주의: train residual은 subject-heldout OOF residual이고 test residual은 train-fit predictor residual이다. 따라서 절대값을 직접 비교하기보다 row ranking과 target shift를 본다.

{markdown_table(view_metrics, ["target_view", "context_feature_count", "target_feature_count", "train_mean_residual", "test_mean_residual", "test_minus_train_mean"])}

## Target Surprise Laws

각 target마다 train set에서 surprise 상위 25%와 하위 25%의 prevalence 차이가 가장 큰 score를 골랐다.

{markdown_table(laws.sort_values("abs_shift", ascending=False), ["target", "surprise_score", "low_rate", "high_rate", "shift", "abs_shift"])}

상세 top shifts:

{markdown_table(top_detail, ["target", "surprise_score", "low_rate", "high_rate", "shift", "abs_shift"], max_rows=18)}

## Frontier Row 재발견

frontier 파일은 support score 계산에 쓰지 않고, 사후 overlap 평가에만 쓴다.

{markdown_table(overlap, ["reference", "top_fraction", "k", "reference_rows", "overlap_rows", "recall", "precision", "mean_selected_surprise_rank"], max_rows=20)}

Random baseline 대비:

{markdown_table(overlap, ["reference", "top_fraction", "recall_lift_vs_random", "precision_lift_vs_random"], max_rows=20)}

## 생성된 후보

- candidate: `{readout["candidate_file"]}`
- changed rows: `{readout["changed_rows"]}`
- changed cells: `{readout["changed_cells"]}`
- mean abs logit move: `{readout["mean_abs_logit_move"]:.6f}`
- max abs logit move: `{readout["max_abs_logit_move"]:.6f}`
- validation: `{readout["validation"]}`

Target action counts:

`{readout["target_action_counts"]}`

## 해석

이 실험이 성공하면 HS-JEPA core의 contribution은 더 분명해진다.

```text
생활 로그의 부분 context로 다른 view의 latent representation을 예측하고,
그 예측이 깨지는 residual energy가 row-target action support를 설명한다.
```

즉 HS-JEPA는 단순히 대회 label을 맞히는 classifier가 아니라, 인간 생활 상태의 predictability break를 찾아 action-health decoder에 넘기는 architecture가 된다.

실패하면 죽는 주장은 다음이다.

```text
masked-view surprise energy만으로는 action-grade row-target release를 만들 수 있다.
```

현재 local evidence에서 frontier overlap lift는 크지 않고, 더 강한 증거는 Q3/Q2/S3 target prevalence shift다. 따라서 이 후보는 점수 미세조정보다 "masked-view predictability break가 label/action route와 연결되는가"를 확인하는 센서에 가깝다.

실패하더라도 core thesis 전체가 죽지는 않는다. 그 경우에는 surprise energy가 support 후보는 설명하지만, listener responsibility / toxicity veto가 별도 모듈로 필요하다는 결론이 강화된다.
"""


def run() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    features, labels, sample, prior = load_inputs()
    catalog = catalog_features(features)
    energy, view_metrics = masked_view_surprise_energy(features, catalog)
    laws, law_detail = target_surprise_laws(features, energy)
    test_energy = energy[energy["split_key"].eq("test")].copy().reset_index(drop=True)
    overlap = evaluate_frontier_overlap(test_energy)
    candidate, action_audit = build_candidate(features, labels, sample, prior, energy, laws)
    validation = validate_submission(candidate, sample)
    if not validation["valid"]:
        raise ValueError(f"candidate is not upload-safe: {validation['problems']}")

    file_hash = short_hash(candidate)
    candidate_file = f"submission_hsjepa_masked_view_surprise_action_release_{file_hash}_uploadsafe.csv"
    candidate.to_csv(OUT_DIR / candidate_file, index=False)
    candidate.to_csv(ROOT / candidate_file, index=False)
    energy.to_csv(OUT_DIR / "masked_view_surprise_energy.csv", index=False)
    view_metrics.to_csv(OUT_DIR / "masked_view_prediction_residuals.csv", index=False)
    laws.to_csv(OUT_DIR / "masked_view_target_surprise_laws.csv", index=False)
    law_detail.to_csv(OUT_DIR / "masked_view_target_surprise_law_detail.csv", index=False)
    overlap.to_csv(OUT_DIR / "masked_view_frontier_overlap.csv", index=False)
    action_audit.to_csv(OUT_DIR / "masked_view_surprise_action_audit.csv", index=False)

    readout = {
        "package": "masked_view_surprise_action_release",
        "status": "bigbet_candidate_ready",
        "uses_public_score_ledger": False,
        "uses_action_teacher_for_support": False,
        "uses_proprietary_embedding_api": False,
        "feature_source": str(FEATURE_PATH.relative_to(ROOT)),
        "probability_prior_file": str(PROBABILITY_PRIOR_FILE.relative_to(ROOT)),
        "candidate_file": candidate_file,
        "changed_cells": int(len(action_audit)),
        "changed_rows": int(action_audit["row"].nunique()) if len(action_audit) else 0,
        "mean_abs_logit_move": float(action_audit["logit_move"].abs().mean()) if len(action_audit) else 0.0,
        "max_abs_logit_move": float(action_audit["logit_move"].abs().max()) if len(action_audit) else 0.0,
        "target_action_counts": action_audit["target"].value_counts().to_dict() if len(action_audit) else {},
        "best_frontier_overlap": (
            {}
            if overlap.empty
            else overlap.sort_values(["recall", "precision"], ascending=False).head(1).to_dict("records")[0]
        ),
        "strongest_target_surprise_law": (
            {}
            if laws.empty
            else laws.sort_values("abs_shift", ascending=False).head(1).to_dict("records")[0]
        ),
        "validation": validation,
        "worldview": (
            "HS-JEPA masked context prediction residual energy marks hidden human-state "
            "episodes; only rows where surprise, target law, and neighbor margin agree "
            "should receive row-target action."
        ),
    }
    (OUT_DIR / "masked_view_surprise_action_release_readout.json").write_text(
        json.dumps(readout, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    md = build_markdown(readout, view_metrics, laws, law_detail, overlap, action_audit)
    (OUT_DIR / "MASKED_VIEW_SURPRISE_ACTION_RELEASE_KO.md").write_text(md + "\n", encoding="utf-8")
    (ROOT / "paper_hsjepa_core" / "MASKED_VIEW_SURPRISE_ACTION_RELEASE_KO.md").write_text(md + "\n", encoding="utf-8")
    return readout


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
