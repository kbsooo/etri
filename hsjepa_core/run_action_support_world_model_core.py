#!/usr/bin/env python3
"""Action-support world model evidence for HS-JEPA core.

This is a public-free core-side experiment.

Question:
    Can a masked-context HS-JEPA world state predict which raw lifelog-memory
    row-target actions will be healthy before the competition adapter releases
    them?

The experiment creates an action-support target from train labels only:

    raw lifelog KNN memory probability vs train-fold prior probability
    -> realized logloss gain for each row-target cell
    -> hidden action-support / action-toxicity representation

Then it asks whether HS-JEPA core representations predict that hidden support
under subject-heldout validation.  The diagnostic submission is anchor-free:
it starts from train priors, not from a leaderboard-tuned submission.
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
from sklearn.decomposition import PCA
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import average_precision_score, log_loss, roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hsjepa_core.run_lifelog_core_state_evidence import (  # noqa: E402
    TARGETS,
    catalog_features,
    finite_matrix,
    format_float,
    load_frames,
    markdown_table,
)
from hsjepa_core.run_masked_context_world_model import build_world_model_state  # noqa: E402


OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "action_support_world_model_core"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "ACTION_SUPPORT_WORLD_MODEL_CORE_KO.md"
SAMPLE_SUBMISSION = ROOT / "data" / "ch2026_submission_sample.csv"
RANDOM_SEED = 20260613
NEIGHBORS = 21
ACTION_MOVE_FLOOR = 0.035
RELEASE_FRACTION = 0.18
INVERSE_SCALE = 0.75


def clip_prob(values: np.ndarray | pd.Series, eps: float = 1e-5) -> np.ndarray:
    return np.clip(np.asarray(values, dtype=np.float64), eps, 1.0 - eps)


def binary_loss(y: np.ndarray, p: np.ndarray) -> np.ndarray:
    y = np.asarray(y, dtype=np.float64)
    p = clip_prob(p)
    return -(y * np.log(p) + (1.0 - y) * np.log(1.0 - p))


def short_hash(frame: pd.DataFrame) -> str:
    return hashlib.sha256(frame[TARGETS].to_numpy(dtype=np.float64).round(10).tobytes()).hexdigest()[:8]


def rank01(values: np.ndarray | pd.Series) -> np.ndarray:
    series = pd.Series(values, dtype="float64").replace([np.inf, -np.inf], np.nan)
    if series.notna().sum() <= 1 or series.nunique(dropna=True) <= 1:
        return np.full(len(series), 0.5, dtype=np.float64)
    return series.rank(method="average", pct=True).fillna(0.5).to_numpy(dtype=np.float64)


def safe_auc(y: np.ndarray, score: np.ndarray) -> float | None:
    y = np.asarray(y, dtype=int)
    score = np.asarray(score, dtype=np.float64)
    mask = np.isfinite(score)
    if mask.sum() == 0 or len(np.unique(y[mask])) < 2:
        return None
    return float(roc_auc_score(y[mask], score[mask]))


def safe_ap(y: np.ndarray, score: np.ndarray) -> float | None:
    y = np.asarray(y, dtype=int)
    score = np.asarray(score, dtype=np.float64)
    mask = np.isfinite(score)
    if mask.sum() == 0 or len(np.unique(y[mask])) < 2:
        return None
    return float(average_precision_score(y[mask], score[mask]))


def target_context_columns() -> list[str]:
    return [
        "target_idx",
        "target_prior",
        "target_prior_rank",
        "target_uncertainty",
        "is_q_target",
        "is_s_target",
        "is_q2_q3_s2",
        "is_objective_tail",
    ] + [f"target_onehot_{target}" for target in TARGETS]


def reduce_features(train_values: pd.DataFrame, apply_values: pd.DataFrame, max_components: int = 18) -> tuple[np.ndarray, np.ndarray]:
    imputer = SimpleImputer(strategy="median")
    scaler = StandardScaler()
    x_train = scaler.fit_transform(imputer.fit_transform(train_values.replace([np.inf, -np.inf], np.nan)))
    x_apply = scaler.transform(imputer.transform(apply_values.replace([np.inf, -np.inf], np.nan)))
    n_components = min(max_components, x_train.shape[1], x_train.shape[0] - 1)
    if n_components >= 2 and x_train.shape[1] > n_components:
        pca = PCA(n_components=n_components, random_state=RANDOM_SEED)
        x_train = pca.fit_transform(x_train)
        x_apply = pca.transform(x_apply)
    return x_train, x_apply


def knn_probability_field(
    train_frame: pd.DataFrame,
    test_frame: pd.DataFrame,
    train_features: pd.DataFrame,
    test_features: pd.DataFrame,
    groups: np.ndarray,
    neighbors: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Create subject-heldout train and train-fitted test KNN action fields."""
    y = train_frame[TARGETS].astype(float).to_numpy()
    splitter = GroupKFold(n_splits=max(2, min(5, len(np.unique(groups)))))
    oof = np.zeros_like(y, dtype=np.float64)
    priors = np.zeros_like(y, dtype=np.float64)
    for tr, va in splitter.split(train_frame, groups=groups):
        x_tr, x_va = reduce_features(train_features.iloc[tr], train_features.iloc[va])
        nn = NearestNeighbors(n_neighbors=min(neighbors, len(tr)), metric="euclidean")
        nn.fit(x_tr)
        dist, idx = nn.kneighbors(x_va)
        weights = 1.0 / np.maximum(dist, 1e-6)
        weights = weights / weights.sum(axis=1, keepdims=True)
        fold_prob = np.einsum("ij,ijt->it", weights, y[tr][idx])
        fold_prior = y[tr].mean(axis=0)
        oof[va] = 0.85 * fold_prob + 0.15 * fold_prior
        priors[va] = fold_prior

    x_train, x_test = reduce_features(train_features, test_features)
    nn = NearestNeighbors(n_neighbors=min(neighbors, len(train_frame)), metric="euclidean")
    nn.fit(x_train)
    dist, idx = nn.kneighbors(x_test)
    weights = 1.0 / np.maximum(dist, 1e-6)
    weights = weights / weights.sum(axis=1, keepdims=True)
    test_prob = np.einsum("ij,ijt->it", weights, y[idx])
    train_prior = y.mean(axis=0)
    test_prob = 0.85 * test_prob + 0.15 * train_prior

    oof_frame = train_frame[["subject_id", "sleep_date", "lifelog_date", "metric_row"]].copy()
    prior_frame = oof_frame.copy()
    test_field = test_frame[["subject_id", "sleep_date", "lifelog_date", "metric_row"]].copy()
    oof_frame[TARGETS] = clip_prob(oof)
    prior_frame[TARGETS] = clip_prob(priors)
    test_field[TARGETS] = clip_prob(test_prob)
    return pd.concat({"candidate": oof_frame, "prior": prior_frame}, names=["field"]).reset_index(level=0), test_field


def make_action_cell_table(
    train_frame: pd.DataFrame,
    oof_field: pd.DataFrame,
    action_name: str,
) -> pd.DataFrame:
    candidate = oof_field[oof_field["field"].eq("candidate")].reset_index(drop=True)
    prior = oof_field[oof_field["field"].eq("prior")].reset_index(drop=True)
    y = train_frame[TARGETS].astype(int).to_numpy()
    cand = candidate[TARGETS].to_numpy(dtype=np.float64)
    base = prior[TARGETS].to_numpy(dtype=np.float64)
    cand_loss = binary_loss(y, cand)
    base_loss = binary_loss(y, base)
    inverse = clip_prob(base - INVERSE_SCALE * (cand - base))
    inverse_loss = binary_loss(y, inverse)
    gain = base_loss - cand_loss
    inverse_gain = base_loss - inverse_loss
    rows: list[dict[str, Any]] = []
    target_priors = train_frame[TARGETS].astype(float).mean().to_dict()
    prior_ranks = pd.Series(target_priors).rank(method="average", pct=True).to_dict()
    for row_idx, row in train_frame.reset_index(drop=True).iterrows():
        for target_idx, target in enumerate(TARGETS):
            move = float(cand[row_idx, target_idx] - base[row_idx, target_idx])
            rows.append(
                {
                    "action_name": action_name,
                    "row": int(row_idx),
                    "metric_row": int(row["metric_row"]),
                    "subject_id": str(row["subject_id"]),
                    "sleep_date": row["sleep_date"],
                    "lifelog_date": row["lifelog_date"],
                    "target": target,
                    "target_idx": target_idx,
                    "target_prior": float(target_priors[target]),
                    "target_prior_rank": float(prior_ranks[target]),
                    "target_uncertainty": float(2.0 * min(target_priors[target], 1.0 - target_priors[target])),
                    "is_q_target": float(target.startswith("Q")),
                    "is_s_target": float(target.startswith("S")),
                    "is_q2_q3_s2": float(target in {"Q2", "Q3", "S2"}),
                    "is_objective_tail": float(target in {"S1", "S3", "S4"}),
                    **{f"target_onehot_{name}": float(name == target) for name in TARGETS},
                    "y": int(y[row_idx, target_idx]),
                    "prior_prob": float(base[row_idx, target_idx]),
                    "candidate_prob": float(cand[row_idx, target_idx]),
                    "inverse_prob": float(inverse[row_idx, target_idx]),
                    "action_move": move,
                    "abs_action_move": abs(move),
                    "realized_gain": float(gain[row_idx, target_idx]),
                    "inverse_realized_gain": float(inverse_gain[row_idx, target_idx]),
                    "positive_gain": int(gain[row_idx, target_idx] > 0.0),
                    "positive_inverse_gain": int(inverse_gain[row_idx, target_idx] > 0.0),
                    "decisive_action": int(abs(move) >= ACTION_MOVE_FLOOR),
                    "positive_decisive_action": int((gain[row_idx, target_idx] > 0.0) and (abs(move) >= ACTION_MOVE_FLOOR)),
                    "toxic_decisive_action": int((gain[row_idx, target_idx] < 0.0) and (abs(move) >= ACTION_MOVE_FLOOR)),
                }
            )
    out = pd.DataFrame(rows)
    out["action_move_rank"] = rank01(out["abs_action_move"])
    return out


def make_test_action_table(test_frame: pd.DataFrame, test_field: pd.DataFrame, train_priors: dict[str, float], action_name: str) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    prior_ranks = pd.Series(train_priors).rank(method="average", pct=True).to_dict()
    field = test_field.reset_index(drop=True)
    for row_idx, row in test_frame.reset_index(drop=True).iterrows():
        for target_idx, target in enumerate(TARGETS):
            prior = float(train_priors[target])
            candidate = float(field.loc[row_idx, target])
            move = candidate - prior
            inverse = float(np.clip(prior - INVERSE_SCALE * move, 1e-5, 1.0 - 1e-5))
            rows.append(
                {
                    "action_name": action_name,
                    "row": int(row_idx),
                    "metric_row": int(row["metric_row"]),
                    "subject_id": str(row["subject_id"]),
                    "sleep_date": row["sleep_date"],
                    "lifelog_date": row["lifelog_date"],
                    "target": target,
                    "target_idx": target_idx,
                    "target_prior": prior,
                    "target_prior_rank": float(prior_ranks[target]),
                    "target_uncertainty": float(2.0 * min(prior, 1.0 - prior)),
                    "is_q_target": float(target.startswith("Q")),
                    "is_s_target": float(target.startswith("S")),
                    "is_q2_q3_s2": float(target in {"Q2", "Q3", "S2"}),
                    "is_objective_tail": float(target in {"S1", "S3", "S4"}),
                    **{f"target_onehot_{name}": float(name == target) for name in TARGETS},
                    "prior_prob": prior,
                    "candidate_prob": candidate,
                    "inverse_prob": inverse,
                    "action_move": move,
                    "abs_action_move": abs(move),
                    "decisive_action": int(abs(move) >= ACTION_MOVE_FLOOR),
                }
            )
    out = pd.DataFrame(rows)
    out["action_move_rank"] = rank01(out["abs_action_move"])
    return out


def append_row_features(cell_table: pd.DataFrame, row_features: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    keep = ["metric_row"] + cols
    return cell_table.merge(row_features[keep], on="metric_row", how="left")


def feature_sets(frame: pd.DataFrame, state: pd.DataFrame, pred_cols: list[str], energy_cols: list[str]) -> dict[str, list[str]]:
    catalog = catalog_features(frame)
    resid_cols = [col for col in state.columns if col.startswith("wm_resid_")]
    core_cols = [col for col in catalog.core_state if col in frame.columns]
    raw_cols = [col for col in catalog.raw_numeric if col in frame.columns]
    target_cols = target_context_columns() + ["action_move_rank", "abs_action_move"]
    return {
        "target_prior_action_only": target_cols,
        "raw_lifelog_context": target_cols + raw_cols,
        "hsjepa_core_cohort_state": target_cols + core_cols,
        "hsjepa_masked_world_predicted": target_cols + pred_cols,
        "hsjepa_masked_world_full": target_cols + pred_cols + energy_cols + resid_cols,
        "hsjepa_core_plus_world": target_cols + core_cols + pred_cols + energy_cols + resid_cols,
    }


def fit_support_models(
    train_cells: pd.DataFrame,
    test_cells: pd.DataFrame,
    feature_map: dict[str, list[str]],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    groups = train_cells["subject_id"].astype(str).to_numpy()
    splitter = GroupKFold(n_splits=max(2, min(5, len(np.unique(groups)))))
    y = train_cells["positive_gain"].astype(int).to_numpy()
    rng = np.random.default_rng(RANDOM_SEED)
    metric_rows: list[dict[str, Any]] = []
    oof_predictions = train_cells[[
        "action_name",
        "row",
        "metric_row",
        "subject_id",
        "target",
        "target_idx",
        "realized_gain",
        "inverse_realized_gain",
        "positive_gain",
        "positive_inverse_gain",
        "decisive_action",
        "action_move",
    ]].copy()
    test_predictions = test_cells[[
        "action_name",
        "row",
        "metric_row",
        "subject_id",
        "target",
        "target_idx",
        "prior_prob",
        "candidate_prob",
        "inverse_prob",
        "action_move",
        "decisive_action",
    ]].copy()

    for feature_name, cols in feature_map.items():
        cols = [col for col in cols if col in train_cells.columns and col in test_cells.columns]
        oof_score = np.zeros(len(train_cells), dtype=np.float64)
        for fold, (tr, va) in enumerate(splitter.split(train_cells, groups=groups)):
            y_tr = y[tr]
            if len(np.unique(y_tr)) < 2:
                oof_score[va] = float(y_tr.mean())
                continue
            model = make_pipeline(
                SimpleImputer(strategy="median"),
                HistGradientBoostingClassifier(
                    learning_rate=0.035,
                    max_leaf_nodes=12,
                    min_samples_leaf=18,
                    l2_regularization=0.18,
                    random_state=RANDOM_SEED + fold,
                ),
            )
            model.fit(train_cells.iloc[tr][cols], y_tr)
            oof_score[va] = model.predict_proba(train_cells.iloc[va][cols])[:, 1]
        oof_predictions[f"support_score_{feature_name}"] = oof_score

        full_model = make_pipeline(
            SimpleImputer(strategy="median"),
            HistGradientBoostingClassifier(
                learning_rate=0.035,
                max_leaf_nodes=12,
                min_samples_leaf=18,
                l2_regularization=0.18,
                random_state=RANDOM_SEED + 999,
            ),
        )
        full_model.fit(train_cells[cols], y)
        test_predictions[f"support_score_{feature_name}"] = full_model.predict_proba(test_cells[cols])[:, 1]

        metric_rows.extend(score_support_predictions(train_cells, oof_score, feature_name, "observed"))
        for repeat in range(32):
            shuffled = oof_score.copy()
            for target in TARGETS:
                idx = np.where(train_cells["target"].eq(target).to_numpy())[0]
                values = shuffled[idx].copy()
                rng.shuffle(values)
                shuffled[idx] = values
            for row in score_support_predictions(train_cells, shuffled, feature_name, f"target_shuffle_null_{repeat:02d}"):
                metric_rows.append(row)

    metrics = pd.DataFrame(metric_rows)
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
    return observed, oof_predictions, test_predictions


def score_support_predictions(cell_table: pd.DataFrame, score: np.ndarray, feature_name: str, null_family: str) -> list[dict[str, Any]]:
    rows = []
    y = cell_table["positive_gain"].astype(int).to_numpy()
    decisive = cell_table["decisive_action"].astype(bool).to_numpy()
    gain = cell_table["realized_gain"].to_numpy(dtype=np.float64)
    inverse_gain = cell_table["inverse_realized_gain"].to_numpy(dtype=np.float64)
    base_rate = float(y.mean())
    auc = safe_auc(y, score)
    ap = safe_ap(y, score)
    for policy_name, decoder_action, fraction, decisive_only, descending in [
        ("top05_all_cells", "raw_memory_release", 0.05, False, True),
        ("top10_all_cells", "raw_memory_release", 0.10, False, True),
        ("top18_all_cells", "raw_memory_release", RELEASE_FRACTION, False, True),
        ("top25_all_cells", "raw_memory_release", 0.25, False, True),
        ("top18_decisive_only", "raw_memory_release", RELEASE_FRACTION, True, True),
        ("low05_inverse_decisive", "inverse_toxic_memory", 0.05, True, False),
        ("low08_inverse_decisive", "inverse_toxic_memory", 0.08, True, False),
        ("low10_inverse_decisive", "inverse_toxic_memory", 0.10, True, False),
        ("low18_inverse_decisive", "inverse_toxic_memory", RELEASE_FRACTION, True, False),
        ("low25_inverse_decisive", "inverse_toxic_memory", 0.25, True, False),
    ]:
        candidate_idx = np.arange(len(cell_table))
        if decisive_only:
            candidate_idx = candidate_idx[decisive[candidate_idx]]
        if len(candidate_idx) == 0:
            continue
        k = max(1, int(round(len(candidate_idx) * fraction)))
        order_key = -score[candidate_idx] if descending else score[candidate_idx]
        order = candidate_idx[np.argsort(order_key, kind="mergesort")[:k]]
        effective_gain = gain if decoder_action == "raw_memory_release" else inverse_gain
        selected_gain = float(effective_gain[order].sum())
        selected_positive_rate = float((effective_gain[order] > 0).mean())
        rows.append(
            {
                "feature_set": feature_name,
                "null_family": null_family,
                "selection_policy": policy_name,
                "decoder_action": decoder_action,
                "release_fraction": fraction,
                "decisive_only": decisive_only,
                "support_auc": auc,
                "support_ap": ap,
                "base_positive_rate": base_rate,
                "selected_cells": int(len(order)),
                "selected_gain_sum": selected_gain,
                "selected_mean_gain": float(effective_gain[order].mean()),
                "selected_positive_gain_rate": selected_positive_rate,
                "all_gain_sum": float(gain.sum()),
                "all_mean_gain": float(gain.mean()),
                "all_positive_gain_rate": float((gain > 0).mean()),
                "uses_public_score_ledger": False,
                "uses_prior_submission_probabilities": False,
            }
        )
    return rows


def choose_release_policy(metrics: pd.DataFrame) -> dict[str, Any]:
    observed = metrics[
        metrics["selection_policy"].isin(
            [
                "top05_all_cells",
                "top10_all_cells",
                "top18_decisive_only",
                "low05_inverse_decisive",
                "low08_inverse_decisive",
                "low10_inverse_decisive",
                "low18_inverse_decisive",
            ]
        )
    ].copy()
    if observed.empty:
        observed = metrics.copy()
    observed["robust_score"] = (
        observed["selected_gain_sum"].fillna(0.0)
        + 0.25 * observed.get("gain_lift_vs_null", 0.0).fillna(0.0)
        + 0.08 * observed.get("gain_z_vs_null", 0.0).fillna(0.0)
        + 0.25 * observed["selected_positive_gain_rate"].fillna(0.0)
    )
    best = observed.sort_values(["robust_score", "selected_gain_sum"], ascending=False).iloc[0].to_dict()
    return best


def build_anchor_free_candidate(
    sample: pd.DataFrame,
    test_cells: pd.DataFrame,
    release_feature_set: str,
    decoder_action: str,
    release_fraction: float,
    train_priors: dict[str, float],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    out = sample.copy()
    for target in TARGETS:
        out[target] = float(train_priors[target])
    score_col = f"support_score_{release_feature_set}"
    selected = np.zeros(len(test_cells), dtype=bool)
    inverse_mode = decoder_action == "inverse_toxic_memory"
    for target, part in test_cells[test_cells["decisive_action"].eq(1)].groupby("target", observed=True):
        if part.empty:
            continue
        k = max(1, int(round(len(part) * release_fraction)))
        order = part.sort_values(score_col, ascending=inverse_mode, kind="mergesort").head(k).index
        selected[order] = True
    audit = test_cells.copy()
    audit["released"] = selected
    audit["decoder_action"] = decoder_action
    for _, row in audit[audit["released"]].iterrows():
        value_col = "inverse_prob" if inverse_mode else "candidate_prob"
        out.at[int(row["row"]), str(row["target"])] = float(row[value_col])
    out[TARGETS] = out[TARGETS].clip(1e-5, 1.0 - 1e-5)
    return out, audit


def validate_submission(frame: pd.DataFrame, sample: pd.DataFrame) -> dict[str, Any]:
    problems = []
    if list(frame.columns) != list(sample.columns):
        problems.append("schema mismatch")
    if len(frame) != len(sample):
        problems.append(f"expected {len(sample)} rows, got {len(frame)}")
    if frame.isna().sum().sum():
        problems.append("NaN found")
    for target in TARGETS:
        values = pd.to_numeric(frame[target], errors="coerce")
        if ((values < 0) | (values > 1)).any():
            problems.append(f"{target} outside [0, 1]")
    return {
        "valid": not problems,
        "problems": problems,
        "rows": int(len(frame)),
        "probability_min": float(frame[TARGETS].min().min()),
        "probability_max": float(frame[TARGETS].max().max()),
    }


def build_markdown(
    summary: dict[str, Any],
    action_field_summary: pd.DataFrame,
    metrics: pd.DataFrame,
    release_policy: dict[str, Any],
    candidate_name: str,
) -> str:
    top_metrics = metrics.sort_values(["robust_score", "selected_gain_sum"], ascending=False) if "robust_score" in metrics else metrics
    return f"""# Action-Support World Model Core

## 한 줄 요약

HS-JEPA core가 단순히 label을 직접 맞히는지 보지 않고,
raw lifelog memory action이 어떤 row-target에서 성공/실패할지를
subject-heldout으로 예측할 수 있는지 검증했다.

```text
visible lifelog context
  -> masked human-state world model
  -> hidden action-support representation prediction
  -> anchor-free sparse correction
```

## 왜 core 실험인가

이 실험은 public LB, 기존 best submission probability, public score ledger를 쓰지 않는다.
action-support target도 public 결과가 아니라 train label에서 만든다.

```text
raw lifelog KNN action vs train-fold prior
  -> realized logloss gain
  -> positive/toxic action-support target
```

그 다음 HS-JEPA world-state가 이 hidden action-support target을 예측하는지 본다.
즉 target은 Q/S label 자체가 아니라, label이 드러내는 **action-health representation**이다.

## 사용하지 않은 정보

- public LB ledger: `{summary["uses_public_score_ledger"]}`
- prior submission probability: `{summary["uses_prior_submission_probabilities"]}`
- proprietary embedding API: `{summary["uses_proprietary_embedding_api"]}`

## Action Field Summary

{markdown_table(action_field_summary, ["action_name", "oof_logloss", "prior_logloss", "delta_vs_prior", "positive_gain_rate", "decisive_cells", "decisive_positive_rate"], max_rows=20)}

## Subject-Heldout Action-Support Prediction

아래 표는 feature set별로 hidden action-support를 예측한 결과다.
`selected_gain_sum`은 해당 feature set이 건강하다고 고른 raw-memory actions를 실제 OOF gain으로 평가한 값이다.

{markdown_table(top_metrics, ["feature_set", "selection_policy", "decoder_action", "release_fraction", "support_auc", "support_ap", "selected_cells", "selected_gain_sum", "selected_positive_gain_rate", "gain_lift_vs_null", "gain_z_vs_null"], max_rows=28)}

## Release Policy

- selected feature set: `{release_policy.get("feature_set")}`
- selected policy: `{release_policy.get("selection_policy")}`
- decoder action: `{release_policy.get("decoder_action")}`
- release fraction: `{format_float(release_policy.get("release_fraction"), 4)}`
- selected gain sum: `{format_float(release_policy.get("selected_gain_sum"), 6)}`
- gain lift vs target-shuffle null: `{format_float(release_policy.get("gain_lift_vs_null"), 6)}`
- gain z vs target-shuffle null: `{format_float(release_policy.get("gain_z_vs_null"), 6)}`
- selected positive gain rate: `{format_float(release_policy.get("selected_positive_gain_rate"), 6)}`

## Anchor-Free Candidate

- candidate: `{candidate_name}`
- validation: `{summary["validation"]}`

이 후보는 leaderboard anchor를 쓰지 않는다.
train prior에서 시작하고, HS-JEPA core가 예측한 action-support에 따라
raw-memory action을 release하거나 toxic action의 반대 방향으로 움직인다.
선택된 decoder가 `inverse_toxic_memory`이면, core가 toxic하다고 본 raw-memory action은 prior 기준 반대 방향으로 움직인다.
점수용 best candidate라기보다 core-only action-support sensor다.

## 해석

성공 조건:

```text
HS-JEPA world-state feature set이 target-prior/action-only baseline보다
더 높은 support AUC/AP와 selected OOF gain을 보여야 한다.
```

실패 조건:

```text
target-prior/action-only baseline이 world-state와 비슷하거나 더 좋다면,
현재 core는 action-health를 읽는 것이 아니라 action magnitude/target prior만 읽는 것이다.
```

현재 가장 중요한 결론:

```text
HS-JEPA core의 가치는 direct label prediction이 아니라,
row-target action을 release하기 전에 action-health/toxicity를 예측하는 데서 검증되어야 한다.
```
"""


def run() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frame, _ = load_frames()
    frame = frame.copy()
    state, view_metrics, pred_cols, energy_cols = build_world_model_state(frame)
    catalog = catalog_features(frame)
    raw_cols = [col for col in catalog.raw_numeric if col in frame.columns]
    resid_cols = [col for col in state.columns if col.startswith("wm_resid_")]

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
    world_cols = pred_cols + energy_cols + resid_cols
    world_oof, world_test_field = knn_probability_field(
        train,
        test,
        finite_matrix(state_train, world_cols),
        finite_matrix(state_test, world_cols),
        groups,
        NEIGHBORS,
    )

    raw_cells = make_action_cell_table(train, raw_oof, "raw_lifelog_memory")
    world_cells = make_action_cell_table(train, world_oof, "masked_world_memory")
    train_cells = raw_cells.copy()
    train_cells = append_row_features(train_cells, train[["metric_row"] + raw_cols], raw_cols)
    state_feature_cols = [
        col
        for col in state.columns
        if col not in {"subject_id", "sleep_date", "lifelog_date", "split", "metric_row"}
    ]
    train_cells = append_row_features(train_cells, state_train[["metric_row"] + state_feature_cols], state_feature_cols)

    train_priors = train[TARGETS].astype(float).mean().to_dict()
    test_cells = make_test_action_table(test, raw_test_field, train_priors, "raw_lifelog_memory")
    test_cells = append_row_features(test_cells, test[["metric_row"] + raw_cols], raw_cols)
    test_cells = append_row_features(test_cells, state_test[["metric_row"] + state_feature_cols], state_feature_cols)

    fsets = feature_sets(frame, state, pred_cols, energy_cols)
    metrics, oof_predictions, test_predictions = fit_support_models(train_cells, test_cells, fsets)
    release_policy = choose_release_policy(metrics)
    metrics = metrics.copy()
    metrics["robust_score"] = (
        metrics["selected_gain_sum"].fillna(0.0)
        + 0.25 * metrics.get("gain_lift_vs_null", 0.0).fillna(0.0)
        + 0.08 * metrics.get("gain_z_vs_null", 0.0).fillna(0.0)
        + 0.25 * metrics["selected_positive_gain_rate"].fillna(0.0)
    )

    sample = pd.read_csv(SAMPLE_SUBMISSION)
    candidate, test_release_audit = build_anchor_free_candidate(
        sample,
        test_predictions,
        str(release_policy["feature_set"]),
        str(release_policy["decoder_action"]),
        float(release_policy.get("release_fraction", RELEASE_FRACTION)),
        train_priors,
    )
    validation = validate_submission(candidate, sample)
    if not validation["valid"]:
        raise ValueError(f"candidate is not upload-safe: {validation['problems']}")
    candidate_name = f"submission_hsjepa_action_support_world_model_anchor_free_{short_hash(candidate)}_uploadsafe.csv"

    action_field_summary = []
    for name, cells in [("raw_lifelog_memory", raw_cells), ("masked_world_memory", world_cells)]:
        y = train[TARGETS].astype(int).to_numpy()
        field = raw_oof if name == "raw_lifelog_memory" else world_oof
        candidate_prob = field[field["field"].eq("candidate")][TARGETS].to_numpy(dtype=np.float64)
        prior_prob = field[field["field"].eq("prior")][TARGETS].to_numpy(dtype=np.float64)
        action_field_summary.append(
            {
                "action_name": name,
                "oof_logloss": float(np.mean([log_loss(y[:, i], candidate_prob[:, i], labels=[0, 1]) for i in range(len(TARGETS))])),
                "prior_logloss": float(np.mean([log_loss(y[:, i], prior_prob[:, i], labels=[0, 1]) for i in range(len(TARGETS))])),
                "delta_vs_prior": float(
                    np.mean([log_loss(y[:, i], candidate_prob[:, i], labels=[0, 1]) for i in range(len(TARGETS))])
                    - np.mean([log_loss(y[:, i], prior_prob[:, i], labels=[0, 1]) for i in range(len(TARGETS))])
                ),
                "positive_gain_rate": float((cells["realized_gain"] > 0).mean()),
                "decisive_cells": int(cells["decisive_action"].sum()),
                "decisive_positive_rate": float(cells.loc[cells["decisive_action"].eq(1), "positive_gain"].mean()),
            }
        )
    action_field_summary_df = pd.DataFrame(action_field_summary)

    summary = {
        "package": "action_support_world_model_core",
        "status": "core_action_support_probe_ready",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "action_support_target": "raw_lifelog_memory_vs_train_fold_prior_realized_gain",
        "release_policy": release_policy,
        "candidate_file": candidate_name,
        "validation": validation,
        "released_test_cells": int(test_release_audit["released"].sum()),
        "view_metric_best_component_corr_lift": float(view_metrics["component_corr_lift_vs_null"].max()),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    view_metrics.to_csv(OUT_DIR / "masked_view_prediction_metrics.csv", index=False)
    state.to_csv(OUT_DIR / "action_support_world_model_state.csv", index=False)
    raw_cells.to_csv(OUT_DIR / "raw_lifelog_memory_oof_action_cells.csv", index=False)
    world_cells.to_csv(OUT_DIR / "masked_world_memory_oof_action_cells.csv", index=False)
    action_field_summary_df.to_csv(OUT_DIR / "action_field_summary.csv", index=False)
    metrics.to_csv(OUT_DIR / "subject_heldout_support_prediction_metrics.csv", index=False)
    oof_predictions.to_csv(OUT_DIR / "subject_heldout_support_oof_predictions.csv", index=False)
    test_predictions.to_csv(OUT_DIR / "test_support_predictions.csv", index=False)
    test_release_audit.to_csv(OUT_DIR / "test_anchor_free_release_audit.csv", index=False)
    candidate.to_csv(OUT_DIR / candidate_name, index=False)
    candidate.to_csv(ROOT / candidate_name, index=False)
    (OUT_DIR / "action_support_world_model_core_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    md = build_markdown(summary, action_field_summary_df, metrics, release_policy, candidate_name)
    (OUT_DIR / "ACTION_SUPPORT_WORLD_MODEL_CORE_KO.md").write_text(md.rstrip() + "\n", encoding="utf-8")
    PAPER_DOC.write_text(md.rstrip() + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
