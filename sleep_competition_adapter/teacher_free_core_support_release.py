#!/usr/bin/env python3
"""Teacher-free core-support release.

This experiment removes action-teacher supervision from the support score.
It uses only OG lifelog-derived HS-JEPA core geometry plus train-label neighbor
statistics, then evaluates whether the resulting row support rediscovers the
known row-state frontier rows. Public LB is not used.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "sleep_competition_adapter" / "outputs" / "teacher_free_core_support_release"
FEATURE_PATH = ROOT / "team_experiments" / "cohort_hsjepa" / "cohort_human_state_features.csv"
LABEL_PATH = ROOT / "data" / "ch2026_metrics_train.csv"
SAMPLE_SUBMISSION = ROOT / "data" / "ch2026_submission_sample.csv"
BASE_STAGE_FILE = ROOT / "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"
FRONTIER_FILE = ROOT / "submission_hsjepa_frontier_silence_positive_path_overshoot_sensor_1e013277_uploadsafe.csv"
ROW_STATE_FILE = ROOT / "submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv"

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
    return np.log(values / (1.0 - values))


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-values))


def rank01(values: pd.Series | np.ndarray) -> np.ndarray:
    series = pd.Series(values, dtype="float64")
    if series.notna().sum() <= 1:
        return np.full(len(series), 0.5, dtype=float)
    return series.rank(method="average", pct=True).fillna(0.5).to_numpy(dtype=float)


def short_hash(frame: pd.DataFrame) -> str:
    return hashlib.sha256(frame[TARGETS].to_numpy(dtype=np.float64).round(10).tobytes()).hexdigest()[:8]


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    features = pd.read_csv(FEATURE_PATH)
    labels = pd.read_csv(LABEL_PATH)
    base = pd.read_csv(BASE_STAGE_FILE)
    frontier = pd.read_csv(FRONTIER_FILE)
    row_state = pd.read_csv(ROW_STATE_FILE)
    sample = pd.read_csv(SAMPLE_SUBMISSION)
    train_mask = features["split"].eq("train")
    if int(train_mask.sum()) != len(labels):
        raise ValueError("feature train rows do not match label rows")
    features = features.copy()
    features.loc[train_mask, TARGETS] = labels[TARGETS].to_numpy()
    return features, labels, base, frontier, row_state, sample


def target_outlier_laws(train_features: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for target in TARGETS:
        best: dict[str, Any] | None = None
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


def build_neighbor_state(train: pd.DataFrame, test: pd.DataFrame, labels: pd.DataFrame) -> pd.DataFrame:
    imputer = SimpleImputer(strategy="median")
    scaler = StandardScaler()
    x_train = scaler.fit_transform(imputer.fit_transform(train[CORE_COLS].replace([np.inf, -np.inf], np.nan)))
    x_test = scaler.transform(imputer.transform(test[CORE_COLS].replace([np.inf, -np.inf], np.nan)))
    k = min(35, len(train))
    nn = NearestNeighbors(n_neighbors=k, metric="euclidean")
    nn.fit(x_train)
    distances, indices = nn.kneighbors(x_test)
    y = labels[TARGETS].astype(float).to_numpy()
    global_prior = y.mean(axis=0)
    local_mean = y[indices].mean(axis=1)
    local_entropy = -(
        np.clip(local_mean, 1e-5, 1 - 1e-5) * np.log(np.clip(local_mean, 1e-5, 1 - 1e-5))
        + np.clip(1 - local_mean, 1e-5, 1 - 1e-5) * np.log(np.clip(1 - local_mean, 1e-5, 1 - 1e-5))
    )
    local_margin = local_mean - global_prior.reshape(1, -1)
    density = 1.0 / (1.0 + distances.mean(axis=1))
    out = pd.DataFrame({
        "row": test["metric_row"].astype(int).to_numpy(),
        "neighbor_distance_mean": distances.mean(axis=1),
        "neighbor_density": density,
        "neighbor_density_rank": rank01(density),
        "neighbor_anomaly_rank": rank01(distances.mean(axis=1)),
        "neighbor_target_entropy_mean": local_entropy.mean(axis=1),
        "neighbor_target_margin_abs_mean": np.abs(local_margin).mean(axis=1),
        "neighbor_target_margin_abs_rank": rank01(np.abs(local_margin).mean(axis=1)),
    })
    for idx, target in enumerate(TARGETS):
        out[f"neighbor_mean_{target}"] = local_mean[:, idx]
        out[f"neighbor_margin_{target}"] = local_margin[:, idx]
        out[f"neighbor_entropy_{target}"] = local_entropy[:, idx]
    return out


def teacher_free_support(test: pd.DataFrame, neighbor: pd.DataFrame) -> pd.DataFrame:
    out = neighbor.copy()
    out["personal_outlier_rank"] = rank01(test["dist_to_subject_normal"])
    out["peer_outlier_rank"] = rank01(test["dist_to_peer_normal"])
    out["cohort_outlier_rank"] = rank01(test["cohort_outlier_score"])
    out["subject_peer_divergence_rank"] = rank01(np.abs(test["subject_minus_peer_dist"]))
    out["calendar_edge_rank"] = rank01(
        pd.to_numeric(test["month_start_proximity"], errors="coerce").fillna(0).to_numpy()
        + pd.to_numeric(test["month_end"], errors="coerce").fillna(0).to_numpy()
        + pd.to_numeric(test["is_weekend"], errors="coerce").fillna(0).to_numpy()
    )
    out["teacher_free_core_support_score"] = (
        0.24 * out["cohort_outlier_rank"]
        + 0.20 * out["personal_outlier_rank"]
        + 0.14 * out["peer_outlier_rank"]
        + 0.14 * out["subject_peer_divergence_rank"]
        + 0.18 * out["neighbor_target_margin_abs_rank"]
        + 0.06 * out["neighbor_anomaly_rank"]
        + 0.04 * out["calendar_edge_rank"]
    )
    out["teacher_free_core_support_rank"] = rank01(out["teacher_free_core_support_score"])
    return out


def frontier_rows(base: pd.DataFrame, reference: pd.DataFrame) -> np.ndarray:
    delta = np.abs(logit(reference[TARGETS].to_numpy(dtype=float)) - logit(base[TARGETS].to_numpy(dtype=float)))
    return delta.max(axis=1) > 1e-4


def evaluate_support(support: pd.DataFrame, base: pd.DataFrame, frontier: pd.DataFrame, row_state: pd.DataFrame) -> pd.DataFrame:
    evaluations = []
    for name, ref in [("frontier_active_silence_rows", frontier), ("row_state_vector_rows", row_state)]:
        y = frontier_rows(base, ref).astype(int)
        score = support["teacher_free_core_support_score"].to_numpy(dtype=float)
        positives = int(y.sum())
        for frac in [0.10, 0.15, 0.18, 0.22, 0.28]:
            k = max(1, int(round(len(score) * frac)))
            selected = np.argsort(-score)[:k]
            evaluations.append({
                "reference": name,
                "top_fraction": frac,
                "k": k,
                "reference_rows": positives,
                "overlap_rows": int(y[selected].sum()),
                "recall": float(y[selected].sum() / positives) if positives else 0.0,
                "precision": float(y[selected].mean()),
                "mean_selected_score": float(score[selected].mean()),
                "mean_not_selected_score": float(np.delete(score, selected).mean()) if k < len(score) else 0.0,
            })
    return pd.DataFrame(evaluations)


def build_candidate(
    test: pd.DataFrame,
    base: pd.DataFrame,
    sample: pd.DataFrame,
    support: pd.DataFrame,
    laws: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    logits = logit(base[TARGETS].to_numpy(dtype=float))
    selected = support["teacher_free_core_support_rank"] >= 0.82
    row_weight = np.clip((support["teacher_free_core_support_rank"].to_numpy(dtype=float) - 0.82) / 0.18, 0, 1)
    action_rows = []
    for target_idx, target in enumerate(TARGETS):
        law = laws[laws["target"].eq(target)].iloc[0]
        score_rank = rank01(test[str(law["score"])])
        margin = support[f"neighbor_margin_{target}"].to_numpy(dtype=float)
        law_direction = int(law["direction"])
        margin_direction = np.sign(margin)
        direction_agrees = (margin_direction == law_direction) | (np.abs(margin) < 0.025)
        route_weight = min(1.0, float(law["abs_shift"]) / 0.16)
        move = 0.34 * law_direction * row_weight * score_rank * route_weight
        move *= np.clip(0.55 + np.abs(margin) * 2.4, 0.55, 1.25)
        if target in {"S1", "S3", "S4"}:
            move *= 0.82
        if target == "Q2":
            move *= 1.18
        mask = selected.to_numpy() & direction_agrees & (np.abs(move) > 0.018)
        logits[mask, target_idx] += move[mask]
        for row in np.where(mask)[0]:
            action_rows.append({
                "row": int(row),
                "subject_id": test.loc[row, "subject_id"],
                "target": target,
                "target_idx": target_idx,
                "teacher_free_core_support_rank": float(support.loc[row, "teacher_free_core_support_rank"]),
                "teacher_free_core_support_score": float(support.loc[row, "teacher_free_core_support_score"]),
                "outlier_score": str(law["score"]),
                "row_outlier_rank": float(score_rank[row]),
                "target_law_shift": float(law["shift"]),
                "neighbor_margin": float(margin[row]),
                "logit_move": float(move[row]),
            })
    out = sample.copy()
    out[TARGETS] = np.clip(sigmoid(logits), 1e-5, 1 - 1e-5)
    return out, pd.DataFrame(action_rows)


def markdown_table(frame: pd.DataFrame, columns: list[str], max_rows: int = 20) -> str:
    if frame.empty:
        return "_No rows._"
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for _, row in frame.loc[:, columns].head(max_rows).iterrows():
        values = []
        for col in columns:
            value = row[col]
            if isinstance(value, float):
                values.append(f"{value:.6f}")
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def build_markdown(readout: dict[str, Any], evaluation: pd.DataFrame, action_audit: pd.DataFrame) -> str:
    return f"""# Teacher-Free Core Support Release

## 목적

이 실험은 기존 action teacher 없이 HS-JEPA core geometry만으로 row-state frontier 일부를 재발견할 수 있는지 본다.

Support score는 다음만 사용한다.

- OG lifelog-derived human-state latent
- personal/cohort outlier score
- train-label nearest-neighbor target margin
- calendar edge signal

Public LB와 action teacher label은 support score 계산에 쓰지 않는다.

## Row-State Frontier 재발견

{markdown_table(evaluation, ["reference", "top_fraction", "k", "reference_rows", "overlap_rows", "recall", "precision"], max_rows=20)}

## 생성된 후보

- `{readout["candidate_file"]}`

base probability prior는 `{readout["base_probability_prior"]}`다. 즉 row-state frontier file을 action anchor로 쓰지 않는다.

핵심 수치:

- changed rows: `{readout["changed_rows"]}`
- changed cells: `{readout["changed_cells"]}`
- mean abs logit move: `{readout["mean_abs_logit_move"]:.6f}`
- max abs logit move: `{readout["max_abs_logit_move"]:.6f}`

Target action counts:

`{readout["target_action_counts"]}`

## 해석

좋아지면 HS-JEPA core가 teacher-free row support와 outlier route만으로도 action-grade correction 일부를 만들 수 있다는 뜻이다.

나빠지면 core geometry는 frontier row를 어느 정도 재발견할 수 있어도, target/listener-specific assignment 없이는 release가 아직 toxic하다는 뜻이다.
"""


def run() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    features, labels, base, frontier, row_state, sample = load_inputs()
    train = features[features["split"].eq("train")].copy().reset_index(drop=True)
    test = features[features["split"].eq("test")].copy().reset_index(drop=True)
    neighbor = build_neighbor_state(train, test, labels)
    support = teacher_free_support(test, neighbor)
    laws = target_outlier_laws(train)
    evaluation = evaluate_support(support, base, frontier, row_state)
    candidate, action_audit = build_candidate(test, base, sample, support, laws)
    file_hash = short_hash(candidate)
    candidate_file = f"submission_hsjepa_teacher_free_core_support_release_{file_hash}_uploadsafe.csv"
    candidate.to_csv(OUT_DIR / candidate_file, index=False)
    candidate.to_csv(ROOT / candidate_file, index=False)
    support.to_csv(OUT_DIR / "teacher_free_core_row_support.csv", index=False)
    laws.to_csv(OUT_DIR / "teacher_free_outlier_target_laws.csv", index=False)
    evaluation.to_csv(OUT_DIR / "teacher_free_frontier_overlap.csv", index=False)
    action_audit.to_csv(OUT_DIR / "teacher_free_core_support_action_audit.csv", index=False)
    readout = {
        "package": "teacher_free_core_support_release",
        "status": "bigbet_candidate_ready",
        "uses_public_score_ledger": False,
        "uses_action_teacher_for_support": False,
        "uses_frontier_file_for_overlap_evaluation_only": True,
        "base_probability_prior": str(BASE_STAGE_FILE.relative_to(ROOT)),
        "candidate_file": candidate_file,
        "root_candidate_file": candidate_file,
        "changed_cells": int(len(action_audit)),
        "changed_rows": int(action_audit["row"].nunique()) if len(action_audit) else 0,
        "mean_abs_logit_move": float(action_audit["logit_move"].abs().mean()) if len(action_audit) else 0.0,
        "max_abs_logit_move": float(action_audit["logit_move"].abs().max()) if len(action_audit) else 0.0,
        "target_action_counts": action_audit["target"].value_counts().to_dict() if len(action_audit) else {},
        "best_overlap": evaluation.sort_values("recall", ascending=False).head(1).to_dict("records")[0],
        "worldview": (
            "HS-JEPA core geometry plus train-label neighbor margins can propose row support "
            "without action-teacher supervision."
        ),
    }
    (OUT_DIR / "teacher_free_core_support_readout.json").write_text(
        json.dumps(readout, indent=2, ensure_ascii=False)
    )
    (OUT_DIR / "TEACHER_FREE_CORE_SUPPORT_RELEASE_KO.md").write_text(
        build_markdown(readout, evaluation, action_audit)
    )
    return readout


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))
