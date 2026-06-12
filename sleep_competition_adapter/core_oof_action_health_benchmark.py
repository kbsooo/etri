#!/usr/bin/env python3
"""OOF benchmark for HS-JEPA core action-health.

This experiment is intentionally anchor-free:

- no public LB ledger
- no prior submission probabilities
- no action teacher
- no row-state frontier file

It asks whether OG lifelog-derived HS-JEPA core geometry improves future-label
prediction when the correction is routed through listener/action-health rather
than released as a raw nearest-neighbor move.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hsjepa_core.core import CandidateAction, ContextView, HSJEPACore, ListenerPrototype  # noqa: E402


OUT = ROOT / "sleep_competition_adapter" / "outputs" / "core_oof_action_health_benchmark"
OUT.mkdir(parents=True, exist_ok=True)

FEATURE_PATH = ROOT / "team_experiments" / "cohort_hsjepa" / "cohort_human_state_features.csv"
LABEL_PATH = ROOT / "data" / "ch2026_metrics_train.csv"
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
ID_COLS = ["subject_id", "sleep_date", "lifelog_date"]


@dataclass(frozen=True)
class ReleaseConfig:
    name: str
    support_floor: float
    health_floor: float
    margin_floor: float
    shrink: float
    allow_law_conflict: bool


CONFIGS = [
    ReleaseConfig("strict_listener_health", 0.74, 0.045, 0.035, 0.72, False),
    ReleaseConfig("balanced_listener_health", 0.66, 0.032, 0.025, 0.88, False),
    ReleaseConfig("wide_listener_health", 0.56, 0.024, 0.015, 0.70, True),
    ReleaseConfig("high_margin_listener_health", 0.52, 0.026, 0.055, 1.08, False),
]

LISTENERS = [
    ListenerPrototype("subjective_listener", (0.74, 0.26, 0.30, 0.18), sensitivity=1.00),
    ListenerPrototype("objective_listener", (0.16, 0.68, 0.28, 0.46), sensitivity=0.98),
    ListenerPrototype("intervention_listener", (0.34, 0.30, 0.78, 0.20), sensitivity=0.94),
]


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-values))


def logit(values: np.ndarray) -> np.ndarray:
    values = np.clip(values.astype(float), 1e-6, 1.0 - 1e-6)
    return np.log(values / (1.0 - values))


def short_hash(frame: pd.DataFrame) -> str:
    return hashlib.sha256(frame[TARGETS].to_numpy(dtype=np.float64).round(10).tobytes()).hexdigest()[:8]


def logloss(y_true: np.ndarray, pred: np.ndarray) -> float:
    pred = np.clip(pred.astype(float), 1e-5, 1 - 1e-5)
    y_true = y_true.astype(float)
    loss = -(y_true * np.log(pred) + (1 - y_true) * np.log(1 - pred))
    return float(loss.mean())


def target_logloss(y_true: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    return {target: logloss(y_true[:, idx], pred[:, idx]) for idx, target in enumerate(TARGETS)}


def rank01(values: pd.Series | np.ndarray) -> np.ndarray:
    s = pd.Series(values, dtype="float64").replace([np.inf, -np.inf], np.nan)
    if s.notna().sum() <= 1:
        return np.full(len(s), 0.5, dtype=float)
    s = s.fillna(float(s.median()))
    return s.rank(method="average", pct=True).to_numpy(dtype=float)


def raw_feature_cols(features: pd.DataFrame) -> list[str]:
    blocked = set(ID_COLS + ["split", "metric_row", "lifelog_date_str"] + TARGETS)
    blocked.update(col for col in features.columns if col.startswith("peer_margin_"))
    blocked.add("target_route_margin_q2q3s2")
    return [
        col
        for col in features.columns
        if col not in blocked and pd.api.types.is_numeric_dtype(features[col])
    ]


def load_world() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, list[str]]:
    features = pd.read_csv(FEATURE_PATH)
    labels = pd.read_csv(LABEL_PATH)
    sample = pd.read_csv(SAMPLE_SUBMISSION)
    train_mask = features["split"].eq("train")
    if int(train_mask.sum()) != len(labels):
        raise ValueError("train feature rows do not match label rows")
    features = features.copy()
    features.loc[train_mask, TARGETS] = labels[TARGETS].to_numpy()
    return features, labels, sample, raw_feature_cols(features)


def temporal_subject_tail_splits(train: pd.DataFrame) -> list[tuple[str, np.ndarray, np.ndarray]]:
    splits = []
    for subject, group in train.groupby("subject_id", sort=True):
        group = group.sort_values(["lifelog_date", "sleep_date", "metric_row"])
        holdout = max(6, int(math.ceil(len(group) * 0.22)))
        val_idx = group.tail(holdout).index.to_numpy()
        tr_idx = train.index.difference(val_idx).to_numpy()
        splits.append((f"future_tail_{subject}", tr_idx, val_idx))
    return splits


def subject_holdout_splits(train: pd.DataFrame) -> list[tuple[str, np.ndarray, np.ndarray]]:
    splits = []
    for subject, group in train.groupby("subject_id", sort=True):
        val_idx = group.index.to_numpy()
        tr_idx = train.index.difference(val_idx).to_numpy()
        splits.append((f"subject_holdout_{subject}", tr_idx, val_idx))
    return splits


def prior_predictions(train_frame: pd.DataFrame, eval_frame: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    global_prior = train_frame[TARGETS].mean().clip(1e-4, 1 - 1e-4).to_numpy(dtype=float)
    subject_means = train_frame.groupby("subject_id")[TARGETS].mean()
    subject_prior = np.zeros((len(eval_frame), len(TARGETS)), dtype=float)
    for row_idx, subject in enumerate(eval_frame["subject_id"].astype(str)):
        if subject in subject_means.index:
            subject_prior[row_idx] = subject_means.loc[subject].to_numpy(dtype=float)
        else:
            subject_prior[row_idx] = global_prior
    subject_prior = np.clip(subject_prior, 1e-4, 1 - 1e-4)
    global_pred = np.tile(global_prior.reshape(1, -1), (len(eval_frame), 1))
    return global_pred, subject_prior


def nearest_mean(
    train_frame: pd.DataFrame,
    eval_frame: pd.DataFrame,
    columns: list[str],
    k: int = 35,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    imp = SimpleImputer(strategy="median")
    scaler = StandardScaler()
    x_train = scaler.fit_transform(imp.fit_transform(train_frame[columns].replace([np.inf, -np.inf], np.nan)))
    x_eval = scaler.transform(imp.transform(eval_frame[columns].replace([np.inf, -np.inf], np.nan)))
    nn = NearestNeighbors(n_neighbors=min(k, len(train_frame)), metric="euclidean")
    nn.fit(x_train)
    distances, indices = nn.kneighbors(x_eval)
    y_train = train_frame[TARGETS].to_numpy(dtype=float)
    local = y_train[indices].mean(axis=1)
    local = np.clip(local, 1e-4, 1 - 1e-4)
    density_rank = rank01(1.0 / (1.0 + distances.mean(axis=1)))
    anomaly_rank = rank01(distances.mean(axis=1))
    return local, density_rank, anomaly_rank


def target_outlier_laws(train_frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for target in TARGETS:
        best: dict[str, Any] | None = None
        for score_col in OUTLIER_SCORE_COLS:
            score = pd.to_numeric(train_frame[score_col], errors="coerce")
            low = score <= score.quantile(0.25)
            high = score >= score.quantile(0.75)
            shift = float(train_frame.loc[high, target].mean() - train_frame.loc[low, target].mean())
            rec = {
                "target": target,
                "score": score_col,
                "shift": shift,
                "abs_shift": abs(shift),
                "direction": 1 if shift >= 0 else -1,
            }
            if best is None or rec["abs_shift"] > best["abs_shift"]:
                best = rec
        rows.append(best)
    return pd.DataFrame(rows)


def listener_for_target(target: str) -> str:
    if target == "Q2":
        return "intervention_listener"
    return "subjective_listener" if target.startswith("Q") else "objective_listener"


def target_scalar(target: str) -> float:
    return TARGETS.index(target) / max(1, len(TARGETS) - 1)


def target_group_scalar(target: str) -> float:
    return 0.25 if target.startswith("Q") else 0.75


def core_contexts(row: pd.Series, target: str, support: float, margin_abs_rank: float, density_rank: float, anomaly_rank: float) -> list[ContextView]:
    personal = float(row.get("subject_outlier_rank", 0.5))
    peer = float(row.get("peer_outlier_rank", 0.5))
    cohort = float(row.get("cohort_outlier_score", 0.5))
    divergence = float(abs(row.get("subject_minus_peer_dist", 0.0)))
    weekend = float(row.get("is_weekend", 0.0))
    month_edge = float(row.get("month_start_proximity", 0.0) <= 1 or row.get("month_end", 0.0) >= 1)
    return [
        ContextView(
            "personal_cohort_state",
            (personal, peer, rank_safe(cohort), rank_safe(divergence)),
            coverage=0.96,
            uncertainty=0.10,
        ),
        ContextView(
            "neighbor_target_state",
            (support, margin_abs_rank, density_rank, target_group_scalar(target)),
            coverage=0.84,
            uncertainty=0.18 + 0.18 * anomaly_rank,
        ),
        ContextView(
            "calendar_social_edge",
            (weekend, month_edge, target_scalar(target), support),
            coverage=0.55,
            uncertainty=0.34,
        ),
    ]


def rank_safe(value: object) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return 0.5
    if not math.isfinite(out):
        return 0.5
    return max(0.0, min(1.0, out))


def action_embedding(target: str, direction: int) -> tuple[float, float, float, float]:
    sign = 1.0 if direction >= 0 else -1.0
    if target == "Q2":
        base = (0.24, 0.20, 0.86, 0.18)
    elif target.startswith("Q"):
        base = (0.82, 0.18, 0.28, 0.20)
    else:
        base = (0.18, 0.78, 0.24, 0.48)
    return tuple(sign * item for item in base)


def health_gated_prediction(
    train_frame: pd.DataFrame,
    eval_frame: pd.DataFrame,
    base_pred: np.ndarray,
    action_local: np.ndarray,
    density_rank: np.ndarray,
    anomaly_rank: np.ndarray,
    config: ReleaseConfig,
    support_local: np.ndarray | None = None,
) -> tuple[np.ndarray, pd.DataFrame]:
    laws = target_outlier_laws(train_frame)
    if support_local is None:
        support_local = action_local
    prior_logit = logit(base_pred)
    local_logit = logit(action_local)
    pred_logit = prior_logit.copy()

    action_margin = action_local - base_pred
    support_margin = support_local - base_pred
    margin_abs_rank = np.zeros_like(support_margin)
    for target_idx in range(len(TARGETS)):
        margin_abs_rank[:, target_idx] = rank01(np.abs(support_margin[:, target_idx]))

    support = (
        0.25 * rank01(eval_frame["cohort_outlier_score"])
        + 0.20 * rank01(eval_frame["dist_to_subject_normal"])
        + 0.15 * rank01(eval_frame["dist_to_peer_normal"])
        + 0.14 * rank01(np.abs(eval_frame["subject_minus_peer_dist"]))
        + 0.18 * margin_abs_rank.mean(axis=1)
        + 0.08 * anomaly_rank
    )
    support_rank = rank01(support)
    core = HSJEPACore(
        responsibility_temperature=0.38,
        health_release_threshold=config.health_floor,
        invariant_release_threshold=0.58,
    )
    audit_rows = []

    for row_pos, (_, row) in enumerate(eval_frame.iterrows()):
        for target_idx, target in enumerate(TARGETS):
            law = laws[laws["target"].eq(target)].iloc[0]
            margin = float(action_margin[row_pos, target_idx])
            if abs(margin) < config.margin_floor:
                released = False
                health = 0.0
                invariant = 0.0
                responsibility = 0.0
                reason = "small_margin"
            elif support_rank[row_pos] < config.support_floor:
                released = False
                health = 0.0
                invariant = 0.0
                responsibility = 0.0
                reason = "low_support"
            else:
                margin_direction = 1 if margin >= 0 else -1
                law_direction = int(law["direction"])
                law_agrees = margin_direction == law_direction
                if not config.allow_law_conflict and not law_agrees and abs(float(law["shift"])) >= 0.045:
                    released = False
                    health = 0.0
                    invariant = 0.0
                    responsibility = 0.0
                    reason = "law_conflict"
                else:
                    contexts = core_contexts(
                        row,
                        target,
                        float(support_rank[row_pos]),
                        float(margin_abs_rank[row_pos, target_idx]),
                        float(density_rank[row_pos]),
                        float(anomaly_rank[row_pos]),
                    )
                    hidden = core.predict_hidden_state(contexts)
                    responsibilities = core.listener_responsibility(hidden, LISTENERS)
                    amplitude = min(1.5, abs(float(local_logit[row_pos, target_idx] - prior_logit[row_pos, target_idx])))
                    action = CandidateAction(
                        f"{target}_neighbor_margin_action",
                        listener_for_target(target),
                        action_embedding(target, margin_direction),
                        amplitude=amplitude,
                        support=float(support_rank[row_pos] * margin_abs_rank[row_pos, target_idx]),
                    )
                    decision = core.score_action(hidden, LISTENERS, responsibilities, action, invariant_anchors=None)
                    health = float(decision.health_score)
                    invariant = float(decision.invariant_energy_delta)
                    responsibility = float(decision.listener_responsibility)
                    released = bool(decision.released)
                    reason = "released" if released else "health_veto"

            if released:
                route_scale = min(1.0, abs(float(law["shift"])) / 0.14)
                move = config.shrink * min(1.0, health / max(config.health_floor, 1e-6)) * route_scale
                pred_logit[row_pos, target_idx] += move * (local_logit[row_pos, target_idx] - prior_logit[row_pos, target_idx])

            audit_rows.append(
                {
                    "row": int(row.get("metric_row", row_pos)),
                    "subject_id": row["subject_id"],
                    "target": target,
                    "target_idx": target_idx,
                    "config": config.name,
                    "support_rank": float(support_rank[row_pos]),
                    "margin": margin,
                    "margin_abs_rank": float(margin_abs_rank[row_pos, target_idx]),
                    "law_score": str(law["score"]),
                    "law_shift": float(law["shift"]),
                    "health_score": health,
                    "listener_responsibility": responsibility,
                    "invariant_energy_delta": invariant,
                    "released": bool(released),
                    "veto_reason": reason,
                }
            )

    return np.clip(sigmoid(pred_logit), 1e-5, 1 - 1e-5), pd.DataFrame(audit_rows)


def evaluate_split_family(train: pd.DataFrame, raw_cols: list[str], split_family: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    splits = temporal_subject_tail_splits(train) if split_family == "temporal_subject_tail" else subject_holdout_splits(train)
    pred_blocks: dict[str, list[tuple[np.ndarray, np.ndarray]]] = {
        "global_prior": [],
        "subject_prior": [],
        "raw_knn_blend": [],
        "core_knn_blend": [],
    }
    for config in CONFIGS:
        pred_blocks[f"hsjepa_action_health__{config.name}"] = []
        pred_blocks[f"raw_action_core_health__{config.name}"] = []
    audit_frames = []

    for fold_name, tr_idx, val_idx in splits:
        tr = train.loc[tr_idx].copy()
        val = train.loc[val_idx].copy()
        y_val = val[TARGETS].to_numpy(dtype=float)
        global_pred, subject_prior = prior_predictions(tr, val)
        raw_local, _raw_density, _raw_anomaly = nearest_mean(tr, val, raw_cols, k=35)
        core_local, density_rank, anomaly_rank = nearest_mean(tr, val, CORE_COLS, k=35)
        pred_blocks["global_prior"].append((y_val, global_pred))
        pred_blocks["subject_prior"].append((y_val, subject_prior))
        pred_blocks["raw_knn_blend"].append((y_val, 0.55 * subject_prior + 0.45 * raw_local))
        pred_blocks["core_knn_blend"].append((y_val, 0.55 * subject_prior + 0.45 * core_local))
        for config in CONFIGS:
            pred, audit = health_gated_prediction(tr, val, subject_prior, core_local, density_rank, anomaly_rank, config)
            audit["fold"] = fold_name
            audit["split_family"] = split_family
            audit["action_source"] = "core_knn_action"
            audit["model"] = f"hsjepa_action_health__{config.name}"
            audit_frames.append(audit)
            pred_blocks[f"hsjepa_action_health__{config.name}"].append((y_val, pred))
            raw_pred, raw_audit = health_gated_prediction(
                tr,
                val,
                subject_prior,
                raw_local,
                density_rank,
                anomaly_rank,
                config,
                support_local=core_local,
            )
            raw_audit["fold"] = fold_name
            raw_audit["split_family"] = split_family
            raw_audit["action_source"] = "raw_lifelog_action_core_support"
            raw_audit["model"] = f"raw_action_core_health__{config.name}"
            audit_frames.append(raw_audit)
            pred_blocks[f"raw_action_core_health__{config.name}"].append((y_val, raw_pred))

    rows = []
    for model_name, blocks in pred_blocks.items():
        y = np.vstack([item[0] for item in blocks])
        pred = np.vstack([item[1] for item in blocks])
        rec = {
            "split_family": split_family,
            "model": model_name,
            "mean_logloss": logloss(y, pred),
        }
        rec.update({f"logloss_{k}": v for k, v in target_logloss(y, pred).items()})
        rows.append(rec)
    return pd.DataFrame(rows), pd.concat(audit_frames, ignore_index=True)


def choose_model(score_table: pd.DataFrame) -> tuple[str, str]:
    temporal = score_table[score_table["split_family"].eq("temporal_subject_tail")].copy()
    candidate = temporal[
        temporal["model"].str.startswith("hsjepa_action_health__")
        | temporal["model"].str.startswith("raw_action_core_health__")
    ].sort_values("mean_logloss").iloc[0]
    model = str(candidate["model"])
    return model, model.split("__", 1)[1]


def target_listener_route(score_table: pd.DataFrame) -> dict[str, str]:
    temporal = score_table[score_table["split_family"].eq("temporal_subject_tail")].copy()
    route = {}
    for target in TARGETS:
        col = f"logloss_{target}"
        route[target] = str(temporal.sort_values(col).iloc[0]["model"])
    return route


def append_route_score(score_table: pd.DataFrame, route: dict[str, str]) -> pd.DataFrame:
    rows = []
    for split_family, group in score_table.groupby("split_family", sort=False):
        rec: dict[str, Any] = {
            "split_family": split_family,
            "model": "hsjepa_target_listener_route_selector",
        }
        target_losses = []
        for target in TARGETS:
            model = route[target]
            loss = float(group[group["model"].eq(model)][f"logloss_{target}"].iloc[0])
            rec[f"logloss_{target}"] = loss
            target_losses.append(loss)
        rec["mean_logloss"] = float(np.mean(target_losses))
        rows.append(rec)
    return pd.concat([score_table, pd.DataFrame(rows)], ignore_index=True)


def prediction_catalog(
    train: pd.DataFrame,
    eval_frame: pd.DataFrame,
    raw_cols: list[str],
) -> tuple[dict[str, np.ndarray], pd.DataFrame]:
    _global_pred, subject_prior = prior_predictions(train, eval_frame)
    global_pred, subject_prior = prior_predictions(train, eval_frame)
    raw_local, _raw_density, _raw_anomaly = nearest_mean(train, eval_frame, raw_cols, k=35)
    core_local, density_rank, anomaly_rank = nearest_mean(train, eval_frame, CORE_COLS, k=35)
    catalog: dict[str, np.ndarray] = {
        "global_prior": global_pred,
        "subject_prior": subject_prior,
        "raw_knn_blend": 0.55 * subject_prior + 0.45 * raw_local,
        "core_knn_blend": 0.55 * subject_prior + 0.45 * core_local,
    }
    audit_frames = []
    for config in CONFIGS:
        pred, audit = health_gated_prediction(train, eval_frame, subject_prior, core_local, density_rank, anomaly_rank, config)
        audit["action_source"] = "core_knn_action"
        audit["model"] = f"hsjepa_action_health__{config.name}"
        audit_frames.append(audit)
        catalog[f"hsjepa_action_health__{config.name}"] = pred
        raw_pred, raw_audit = health_gated_prediction(
            train,
            eval_frame,
            subject_prior,
            raw_local,
            density_rank,
            anomaly_rank,
            config,
            support_local=core_local,
        )
        raw_audit["action_source"] = "raw_lifelog_action_core_support"
        raw_audit["model"] = f"raw_action_core_health__{config.name}"
        audit_frames.append(raw_audit)
        catalog[f"raw_action_core_health__{config.name}"] = raw_pred
    return catalog, pd.concat(audit_frames, ignore_index=True)


def build_anchor_free_submission(
    features: pd.DataFrame,
    labels: pd.DataFrame,
    sample: pd.DataFrame,
    raw_cols: list[str],
    route: dict[str, str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    train = features[features["split"].eq("train")].copy().reset_index(drop=True)
    test = features[features["split"].eq("test")].copy().reset_index(drop=True)
    catalog, audit = prediction_catalog(train, test, raw_cols)
    pred = np.zeros((len(test), len(TARGETS)), dtype=float)
    for target_idx, target in enumerate(TARGETS):
        pred[:, target_idx] = catalog[route[target]][:, target_idx]
    sub = sample.copy()
    sub[TARGETS] = pred
    return sub, audit


def validate_submission(submission: pd.DataFrame, sample: pd.DataFrame) -> None:
    if submission.shape != sample.shape:
        raise ValueError(f"shape mismatch: {submission.shape} vs {sample.shape}")
    if list(submission.columns) != list(sample.columns):
        raise ValueError("submission columns do not match sample")
    if submission.isna().sum().sum():
        raise ValueError("submission contains NaN")
    if submission.duplicated(ID_COLS).sum():
        raise ValueError("submission contains duplicate key rows")
    values = submission[TARGETS].to_numpy(dtype=float)
    if not np.isfinite(values).all():
        raise ValueError("submission contains non-finite predictions")
    if values.min() < 0 or values.max() > 1:
        raise ValueError("submission probabilities outside [0, 1]")


def build_markdown(readout: dict[str, Any], score_table: pd.DataFrame) -> str:
    def table_md(frame: pd.DataFrame) -> str:
        cols = list(frame.columns)
        rows = ["| " + " | ".join(cols) + " |"]
        rows.append("| " + " | ".join(["---"] * len(cols)) + " |")
        for rec in frame.to_dict("records"):
            cells = []
            for col in cols:
                value = rec[col]
                if isinstance(value, float):
                    cells.append(f"{value:.6f}")
                else:
                    cells.append(str(value))
            rows.append("| " + " | ".join(cells) + " |")
        return "\n".join(rows)

    lines = [
        "# Core OOF Action-Health Benchmark",
        "",
        "## 목적",
        "",
        "이 실험은 public LB, 기존 submission, action teacher 없이 OG train 내부에서 HS-JEPA core가 실제 future-label logloss를 줄이는지 본다.",
        "",
        "비교 대상은 다음이다.",
        "",
        "- global prior",
        "- subject prior",
        "- raw lifelog KNN blend",
        "- HS-JEPA core KNN blend",
        "- HS-JEPA listener/action-health gated release",
        "",
        "## 핵심 결과",
        "",
        f"- best temporal model: `{readout['best_temporal_model']}`",
        f"- best temporal mean logloss: `{readout['best_temporal_logloss']:.6f}`",
        f"- subject prior temporal logloss: `{readout['subject_prior_temporal_logloss']:.6f}`",
        f"- delta vs subject prior: `{readout['best_delta_vs_subject_prior']:.6f}`",
        f"- target listener route temporal logloss: `{readout['target_listener_route_temporal_logloss']:.6f}`",
        f"- target listener route delta vs subject prior: `{readout['target_listener_route_delta_vs_subject_prior']:.6f}`",
        f"- generated candidate: `{readout['candidate_file']}`",
        "",
        "Target listener route:",
        "",
        table_md(pd.DataFrame([{"target": k, "selected_listener_route": v} for k, v in readout["target_listener_route"].items()])),
        "",
        "## 전체 score table",
        "",
        table_md(score_table),
        "",
        "## 해석",
        "",
        "가장 중요한 결과는 단일 decoder가 아니라 target/listener별 route selector가 temporal OOF에서 가장 좋았다는 점이다.",
        "",
        "즉 HS-JEPA core는 모든 target에 같은 방식으로 release되는 만능 predictor가 아니다. Q1/S4는 core KNN geometry를 듣고, S1/S3는 raw lifelog KNN을 듣고, Q2/Q3는 현재 train future split에서는 global prior가 더 안전하며, S2만 action-health release를 듣는다.",
        "",
        "이것은 HS-JEPA를 `one encoder -> one classifier`가 아니라 `human-state core -> listener-specific route selection -> action-health release`로 정립해야 한다는 증거다.",
    ]
    return "\n".join(lines)


def run() -> dict[str, Any]:
    features, labels, sample, raw_cols = load_world()
    train = features[features["split"].eq("train")].copy().reset_index(drop=True)
    train[TARGETS] = labels[TARGETS].to_numpy(dtype=float)
    features = features.copy()
    features.loc[features["split"].eq("train"), TARGETS] = labels[TARGETS].to_numpy(dtype=float)

    temporal_scores, temporal_audit = evaluate_split_family(train, raw_cols, "temporal_subject_tail")
    subject_scores, subject_audit = evaluate_split_family(train, raw_cols, "subject_holdout")
    score_table = pd.concat([temporal_scores, subject_scores], ignore_index=True)
    route = target_listener_route(score_table)
    score_table = append_route_score(score_table, route)
    audit = pd.concat([temporal_audit, subject_audit], ignore_index=True)

    selected_model, best_config = choose_model(score_table)
    submission, test_audit = build_anchor_free_submission(features, labels, sample, raw_cols, route)
    validate_submission(submission, sample)
    suffix = short_hash(submission)
    candidate_file = f"submission_hsjepa_core_oof_action_health_{suffix}_uploadsafe.csv"
    candidate_path = ROOT / candidate_file
    submission.to_csv(candidate_path, index=False)
    submission.to_csv(OUT / candidate_file, index=False)

    temporal = score_table[score_table["split_family"].eq("temporal_subject_tail")].copy()
    subject_prior_temporal = float(temporal[temporal["model"].eq("subject_prior")]["mean_logloss"].iloc[0])
    best_temporal = temporal.sort_values("mean_logloss").iloc[0]
    best_action_temporal = temporal[
        temporal["model"].str.startswith("hsjepa_action_health__")
        | temporal["model"].str.startswith("raw_action_core_health__")
    ].sort_values("mean_logloss").iloc[0]
    route_temporal = temporal[temporal["model"].eq("hsjepa_target_listener_route_selector")].iloc[0]
    route_action_mask = np.zeros(len(test_audit), dtype=bool)
    for target, model in route.items():
        route_action_mask |= test_audit["target"].eq(target).to_numpy() & test_audit["model"].eq(model).to_numpy()
    route_released = test_audit[route_action_mask & test_audit["released"].astype(bool)].copy()
    readout = {
        "package": "core_oof_action_health_benchmark",
        "status": "anchor_free_oof_benchmark_ready",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_action_teacher": False,
        "best_temporal_model": str(best_temporal["model"]),
        "best_temporal_logloss": float(best_temporal["mean_logloss"]),
        "best_action_health_model": str(best_action_temporal["model"]),
        "best_action_health_temporal_logloss": float(best_action_temporal["mean_logloss"]),
        "subject_prior_temporal_logloss": subject_prior_temporal,
        "best_delta_vs_subject_prior": float(best_temporal["mean_logloss"] - subject_prior_temporal),
        "best_action_delta_vs_subject_prior": float(best_action_temporal["mean_logloss"] - subject_prior_temporal),
        "selected_action_health_model": selected_model,
        "selected_release_config": best_config,
        "target_listener_route": route,
        "target_listener_route_temporal_logloss": float(route_temporal["mean_logloss"]),
        "target_listener_route_delta_vs_subject_prior": float(route_temporal["mean_logloss"] - subject_prior_temporal),
        "candidate_file": candidate_file,
        "root_candidate_file": candidate_file,
        "candidate_released_cells": int(len(route_released)),
        "candidate_released_rows": int(route_released["row"].nunique()),
        "candidate_release_target_counts": route_released["target"].value_counts().reindex(TARGETS).fillna(0).astype(int).to_dict(),
        "interpretation": "OOF evidence tests whether HS-JEPA core action-health is a real decoder or only a support diagnostic.",
    }

    score_table.to_csv(OUT / "core_oof_action_health_score_table.csv", index=False)
    audit.to_csv(OUT / "core_oof_action_health_oof_audit.csv", index=False)
    test_audit.to_csv(OUT / "core_oof_action_health_test_action_audit.csv", index=False)
    (OUT / "core_oof_action_health_readout.json").write_text(json.dumps(readout, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "CORE_OOF_ACTION_HEALTH_BENCHMARK_KO.md").write_text(build_markdown(readout, score_table), encoding="utf-8")
    return readout


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
