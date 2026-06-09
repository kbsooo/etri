#!/usr/bin/env python3
"""Big Bet 2: Cohort-Autobiographical Atlas HS-JEPA.

World model:
    A test day is not independent. It is a hidden state in the same subject's
    personal trajectory. The useful target representation is therefore a
    personal memory posterior, but it should be translated only when peer-cohort
    anomaly signals say the row-target action is meaningful.

This is the cohort-included final idea. It does not use closed-source
embeddings. It starts from the official train/sample CSV plus the open
sensor-derived human-state feature table. If that table is absent, the script
regenerates it with the team cohort-HS-JEPA feature builder.
"""

from __future__ import annotations

from pathlib import Path
import hashlib
import shutil
import subprocess
import sys

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.metrics import log_loss
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "hsjepa_big_bets" / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

KEYS = ["subject_id", "sleep_date", "lifelog_date"]
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
EPS = 1.0e-6
FEATURE_FILE = ROOT / "team_experiments" / "cohort_hsjepa" / "cohort_human_state_features.csv"
FEATURE_BUILDER = ROOT / "team_experiments" / "cohort_hsjepa" / "cohort_hsjepa_experiment.py"
BASE_FILE = ROOT / "submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv"


TARGET_CONFIGS = {
    "Q1": ("latent_calendar", 17, 1.75, 1.20, 6.0),
    "Q2": ("latent_calendar", 17, 0.75, 1.20, 1.5),
    "Q3": ("latent_calendar", 9, 1.25, 1.20, 3.0),
    "S1": ("raw_pca", 5, 1.75, 0.70, 6.0),
    "S2": ("raw_plus_latent", 9, 0.35, 0.70, 6.0),
    "S3": ("latent_calendar", 17, 0.35, 0.70, 6.0),
    "S4": ("latent8", 31, 0.35, 0.35, 6.0),
}


def clip_prob(values: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(values, dtype=np.float64), EPS, 1.0 - EPS)


def logit(values: np.ndarray) -> np.ndarray:
    p = clip_prob(values)
    return np.log(p / (1.0 - p))


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(values, dtype=np.float64)))


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def rank01(values: np.ndarray, high: bool = True) -> np.ndarray:
    s = pd.Series(np.asarray(values, dtype=np.float64)).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    if s.nunique(dropna=True) <= 1:
        return np.full(len(s), 0.5, dtype=np.float64)
    r = s.rank(method="average", pct=True).to_numpy(dtype=np.float64)
    return r if high else 1.0 - r


def ensure_feature_table() -> None:
    if FEATURE_FILE.exists():
        return
    if not FEATURE_BUILDER.exists():
        raise FileNotFoundError(f"missing feature table and builder: {FEATURE_FILE}")
    subprocess.run([sys.executable, str(FEATURE_BUILDER)], check=True, cwd=str(ROOT))


def load_inputs():
    ensure_feature_table()
    features = pd.read_csv(FEATURE_FILE, parse_dates=["sleep_date", "lifelog_date"])
    train = pd.read_csv(ROOT / "data" / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = pd.read_csv(ROOT / "data" / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    base = pd.read_csv(BASE_FILE, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEYS).reset_index(drop=True)
    sample_sorted = sample.sort_values(KEYS).reset_index(drop=True)
    if not (base[KEYS].astype(str).to_numpy() == sample_sorted[KEYS].astype(str).to_numpy()).all():
        raise RuntimeError("base submission is not aligned with official sample")

    train_feat = (
        features[features["split"].eq("train")]
        .merge(train[KEYS + TARGETS], on=KEYS, how="left")
        .sort_values("metric_row")
        .reset_index(drop=True)
    )
    test_feat = features[features["split"].eq("test")].sort_values("metric_row").reset_index(drop=True)
    return train, sample_sorted, base, features, train_feat, test_feat


def numeric_views(features: pd.DataFrame) -> dict[str, list[str]]:
    num_cols = [c for c in features.columns if pd.api.types.is_numeric_dtype(features[c])]
    exclude = {"metric_row", "peer_group"} | {
        c for c in num_cols if c.startswith("peer_margin_") or c.startswith("target_route_margin")
    }
    latent = [c for c in num_cols if c.startswith("human_state_latent_")]
    raw = [
        c
        for c in num_cols
        if c not in exclude
        and not c.startswith("human_state_latent_")
        and not c.startswith("dist_to_")
        and c not in ["subject_outlier_rank", "peer_outlier_rank", "cohort_outlier_score", "subject_minus_peer_dist"]
    ]
    return {
        "latent8": latent,
        "latent_calendar": latent + ["dayofweek", "is_weekend", "dayofmonth", "month_start_proximity", "month_end"],
        "raw_pca": raw,
        "raw_plus_latent": raw + latent,
    }


def fit_view_transforms(train_feat: pd.DataFrame, test_feat: pd.DataFrame, views: dict[str, list[str]]):
    transforms: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for view, cols in views.items():
        imputer = SimpleImputer(strategy="median")
        scaler = StandardScaler()
        x_train = scaler.fit_transform(imputer.fit_transform(train_feat[cols]))
        x_test = scaler.transform(imputer.transform(test_feat[cols]))
        if len(cols) > 20:
            n_components = min(24, x_train.shape[1], x_train.shape[0] - 1)
            pca = PCA(n_components=n_components, random_state=42)
            x_train = pca.fit_transform(x_train)
            x_test = pca.transform(x_test)
        transforms[view] = (x_train, x_test)
    return transforms


def weighted_memory(
    target_index: int,
    x_query: np.ndarray,
    query_subject: str,
    query_date: np.datetime64,
    train_subjects: np.ndarray,
    train_dates: np.ndarray,
    x_train: np.ndarray,
    y_train: np.ndarray,
    prior: np.ndarray,
    k: int,
    alpha: float,
    time_weight: float,
    shrink: float,
    exclude_index: int | None = None,
) -> tuple[float, float, float]:
    mask = train_subjects == query_subject
    if exclude_index is not None:
        mask[exclude_index] = False
    idx = np.flatnonzero(mask)
    if len(idx) == 0:
        return float(prior[target_index]), float("nan"), 0.0

    diff = x_train[idx] - x_query
    latent_dist = np.sqrt((diff * diff).sum(axis=1))
    time_dist = np.abs(train_dates[idx] - query_date).astype(np.float64) / 14.0
    score = latent_dist + time_weight * time_dist
    order = np.argsort(score)[: min(k, len(idx))]
    nn = idx[order]
    local_score = score[order]
    weights = np.exp(-alpha * local_score)
    if weights.sum() <= 0:
        weights = np.ones_like(weights)

    q = float((weights * y_train[nn, target_index]).sum() / (weights.sum() + 1.0e-12))
    subject_mean = float(y_train[idx, target_index].mean())
    eff_n = float((weights.sum() ** 2) / (np.square(weights).sum() + 1.0e-12))
    lam = min(1.0, eff_n / (eff_n + shrink))
    q = lam * q + (1.0 - lam) * (0.65 * subject_mean + 0.35 * float(prior[target_index]))
    return float(np.clip(q, 1.0e-5, 1.0 - 1.0e-5)), float(local_score[0]), eff_n


def subject_mean_cv(y: np.ndarray, subjects: np.ndarray) -> dict[str, float]:
    prior = y.mean(axis=0)
    pred = np.zeros_like(y, dtype=np.float64)
    for i, subject in enumerate(subjects):
        idx = np.flatnonzero(subjects == subject)
        others = idx[idx != i]
        subject_mean = y[others].mean(axis=0) if len(others) else prior
        pred[i] = 0.70 * subject_mean + 0.30 * prior
    return {target: float(log_loss(y[:, j], clip_prob(pred[:, j]), labels=[0, 1])) for j, target in enumerate(TARGETS)}


def memory_train_loo(train_feat: pd.DataFrame, transforms, y: np.ndarray) -> tuple[pd.DataFrame, np.ndarray]:
    subjects = train_feat["subject_id"].astype(str).to_numpy()
    dates = pd.to_datetime(train_feat["lifelog_date"]).to_numpy("datetime64[D]")
    prior = y.mean(axis=0)
    pred = np.zeros_like(y, dtype=np.float64)
    detail_rows = []
    for target_index, target in enumerate(TARGETS):
        view, k, alpha, time_weight, shrink = TARGET_CONFIGS[target]
        x_train, _ = transforms[view]
        for i in range(len(train_feat)):
            q, nearest_dist, eff_n = weighted_memory(
                target_index,
                x_train[i],
                subjects[i],
                dates[i],
                subjects.copy(),
                dates,
                x_train,
                y,
                prior,
                k,
                alpha,
                time_weight,
                shrink,
                exclude_index=i,
            )
            pred[i, target_index] = q
            detail_rows.append(
                {
                    "row": i,
                    "subject_id": subjects[i],
                    "target": target,
                    "posterior": q,
                    "nearest_distance": nearest_dist,
                    "effective_neighbors": eff_n,
                }
            )
    return pd.DataFrame(detail_rows), pred


def memory_test_posterior(train_feat: pd.DataFrame, test_feat: pd.DataFrame, transforms, y: np.ndarray) -> tuple[np.ndarray, pd.DataFrame]:
    train_subjects = train_feat["subject_id"].astype(str).to_numpy()
    test_subjects = test_feat["subject_id"].astype(str).to_numpy()
    train_dates = pd.to_datetime(train_feat["lifelog_date"]).to_numpy("datetime64[D]")
    test_dates = pd.to_datetime(test_feat["lifelog_date"]).to_numpy("datetime64[D]")
    prior = y.mean(axis=0)
    posterior = np.zeros((len(test_feat), len(TARGETS)), dtype=np.float64)
    rows = []
    for target_index, target in enumerate(TARGETS):
        view, k, alpha, time_weight, shrink = TARGET_CONFIGS[target]
        x_train, x_test = transforms[view]
        for i in range(len(test_feat)):
            q, nearest_dist, eff_n = weighted_memory(
                target_index,
                x_test[i],
                test_subjects[i],
                test_dates[i],
                train_subjects,
                train_dates,
                x_train,
                y,
                prior,
                k,
                alpha,
                time_weight,
                shrink,
            )
            posterior[i, target_index] = q
            rows.append(
                {
                    "row": i,
                    "subject_id": test_subjects[i],
                    "sleep_date": test_feat.loc[i, "sleep_date"],
                    "lifelog_date": test_feat.loc[i, "lifelog_date"],
                    "target": target,
                    "memory_posterior": q,
                    "nearest_distance": nearest_dist,
                    "effective_neighbors": eff_n,
                    "view": view,
                    "k": k,
                    "alpha": alpha,
                    "time_weight": time_weight,
                    "shrink": shrink,
                }
            )
    return posterior, pd.DataFrame(rows)


def target_reliability(memory_cv: dict[str, float], subject_cv: dict[str, float]) -> dict[str, float]:
    rel = {}
    for target in TARGETS:
        gain = subject_cv[target] - memory_cv[target]
        rel[target] = float(np.clip(0.25 + gain / 0.07, 0.25, 1.0))
    return rel


def candidate_cells(
    base_prob: np.ndarray,
    memory_prob: np.ndarray,
    test_feat: pd.DataFrame,
    reliability: dict[str, float],
) -> pd.DataFrame:
    base_logit = logit(base_prob)
    memory_logit = logit(memory_prob)
    memory_delta = memory_logit - base_logit
    cohort_rank = rank01(test_feat["cohort_outlier_score"].to_numpy(dtype=np.float64), high=True)
    subject_outlier = rank01(test_feat["dist_to_subject_normal"].to_numpy(dtype=np.float64), high=True)
    peer_outlier = rank01(test_feat["dist_to_peer_normal"].to_numpy(dtype=np.float64), high=True)
    cohort_weight = {"Q1": 0.25, "Q2": 0.80, "Q3": 0.80, "S1": 0.55, "S2": 0.90, "S3": 0.50, "S4": 0.25}

    rows = []
    for row in range(len(test_feat)):
        for target_index, target in enumerate(TARGETS):
            margin_col = f"peer_margin_{target}"
            peer_margin = float(test_feat.loc[row, margin_col]) if margin_col in test_feat.columns and pd.notna(test_feat.loc[row, margin_col]) else 0.0
            delta = float(memory_delta[row, target_index])
            peer_agree = abs(peer_margin) < 0.15 or np.sign(peer_margin) == np.sign(delta)
            rows.append(
                {
                    "row": row,
                    "subject_id": test_feat.loc[row, "subject_id"],
                    "sleep_date": test_feat.loc[row, "sleep_date"],
                    "lifelog_date": test_feat.loc[row, "lifelog_date"],
                    "target": target,
                    "target_index": target_index,
                    "base_prob": float(base_prob[row, target_index]),
                    "memory_prob": float(memory_prob[row, target_index]),
                    "memory_logit_delta": delta,
                    "abs_delta": abs(delta),
                    "peer_margin": peer_margin,
                    "peer_agree": bool(peer_agree),
                    "cohort_outlier_rank": float(cohort_rank[row]),
                    "subject_outlier_rank2": float(subject_outlier[row]),
                    "peer_outlier_rank2": float(peer_outlier[row]),
                    "cohort_weight": float(cohort_weight[target]),
                    "target_reliability": float(reliability[target]),
                }
            )
    cells = pd.DataFrame(rows)
    cells["abs_delta_rank"] = cells.groupby("target")["abs_delta"].rank(method="average", pct=True)
    cells["peer_abs_rank"] = cells.groupby("target")["peer_margin"].transform(lambda s: s.abs().rank(method="average", pct=True))
    cells["score"] = (
        cells["target_reliability"] * (0.70 * cells["abs_delta_rank"] + 0.30 * np.minimum(1.0, cells["abs_delta"] / 1.20))
        + cells["cohort_weight"]
        * (
            0.35 * cells["cohort_outlier_rank"]
            + 0.25 * cells["subject_outlier_rank2"]
            + 0.25 * cells["peer_outlier_rank2"]
            + 0.15 * cells["peer_abs_rank"]
        )
        + np.where(cells["peer_agree"], 0.55, -0.55)
        + np.where(cells["target"].isin(["Q2", "Q3", "S1", "S2", "S3"]), 0.18, -0.05)
    )
    return cells.sort_values("score", ascending=False).reset_index(drop=True)


def materialize_variant(
    name: str,
    cells: pd.DataFrame,
    base_prob: np.ndarray,
    topn: int,
    amp: float,
    cap: float,
    targets: set[str],
) -> tuple[pd.DataFrame, np.ndarray]:
    base_logit = logit(base_prob)
    pool = cells[cells["target"].isin(targets)].copy()
    selected_rows: list[dict[str, object]] = []
    per_target: dict[str, int] = {}
    per_row: dict[int, int] = {}
    per_subject: dict[str, int] = {}
    target_limits = {"Q1": 30, "Q2": 90, "Q3": 85, "S1": 90, "S2": 95, "S3": 95, "S4": 35}
    for rec in pool.to_dict("records"):
        if len(selected_rows) >= topn:
            break
        row = int(rec["row"])
        target = str(rec["target"])
        subject = str(rec["subject_id"])
        if float(rec["abs_delta"]) < 0.08:
            continue
        if per_target.get(target, 0) >= target_limits[target]:
            continue
        if per_row.get(row, 0) >= 5:
            continue
        if per_subject.get(subject, 0) >= 95:
            continue
        selected_rows.append(rec)
        per_target[target] = per_target.get(target, 0) + 1
        per_row[row] = per_row.get(row, 0) + 1
        per_subject[subject] = per_subject.get(subject, 0) + 1

    selected = pd.DataFrame(selected_rows)
    new_prob = base_prob.copy()
    if not selected.empty:
        for rec in selected.to_dict("records"):
            row = int(rec["row"])
            target_index = int(rec["target_index"])
            step = float(np.clip(float(rec["memory_logit_delta"]) * amp, -cap, cap))
            new_prob[row, target_index] = sigmoid(base_logit[row, target_index] + step)
        selected["variant"] = name
        selected["amp"] = amp
        selected["cap"] = cap
        selected["new_prob"] = [new_prob[int(r["row"]), int(r["target_index"])] for r in selected.to_dict("records")]
    return selected, clip_prob(new_prob)


def cosine_to_known(base_prob: np.ndarray, prob: np.ndarray) -> dict[str, float]:
    out = {}
    move = (logit(prob) - logit(base_prob)).reshape(-1)
    for label, path in {
        "h088": ROOT / "submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv",
        "h149": ROOT / "submission_h149_bundle_listener_route_d8e1d789_uploadsafe.csv",
        "h150": ROOT / "submission_h150_robust_bundle_listener_5e12f9bd_uploadsafe.csv",
    }.items():
        if not path.exists():
            out[f"cosine_{label}"] = 0.0
            continue
        known = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEYS).reset_index(drop=True)
        known_move = (logit(known[TARGETS].to_numpy(dtype=np.float64)) - logit(base_prob)).reshape(-1)
        denom = float(np.linalg.norm(move) * np.linalg.norm(known_move))
        out[f"cosine_{label}"] = float(np.dot(move, known_move) / denom) if denom > 1.0e-12 else 0.0
    return out


def write_submission(sample: pd.DataFrame, prob: np.ndarray, stem: str) -> tuple[Path, Path]:
    hash_id = short_hash(prob)
    local_path = OUT / f"{stem}_{hash_id}.csv"
    root_path = ROOT / f"{stem}_{hash_id}_uploadsafe.csv"
    sub = sample.copy()
    sub[TARGETS] = clip_prob(prob)
    sub.to_csv(local_path, index=False)
    shutil.copyfile(local_path, root_path)
    return local_path, root_path


def main() -> None:
    train, sample, base, features, train_feat, test_feat = load_inputs()
    views = numeric_views(features)
    transforms = fit_view_transforms(train_feat, test_feat, views)
    y = train_feat[TARGETS].to_numpy(dtype=np.float64)
    subject_cv = subject_mean_cv(y, train_feat["subject_id"].astype(str).to_numpy())
    memory_detail, memory_loo = memory_train_loo(train_feat, transforms, y)
    memory_cv = {target: float(log_loss(y[:, j], clip_prob(memory_loo[:, j]), labels=[0, 1])) for j, target in enumerate(TARGETS)}
    reliability = target_reliability(memory_cv, subject_cv)

    cv_rows = []
    for target in TARGETS:
        cv_rows.append(
            {
                "target": target,
                "subject_mean_logloss": subject_cv[target],
                "autobiographical_memory_logloss": memory_cv[target],
                "memory_gain": subject_cv[target] - memory_cv[target],
                "target_reliability": reliability[target],
                "config": TARGET_CONFIGS[target],
            }
        )
    cv = pd.DataFrame(cv_rows)
    cv.to_csv(OUT / "bigbet2_cohort_autobiographical_atlas_cv.csv", index=False)
    memory_detail.to_csv(OUT / "bigbet2_cohort_autobiographical_train_memory_detail.csv", index=False)

    memory_prob, memory_test = memory_test_posterior(train_feat, test_feat, transforms, y)
    memory_test.to_csv(OUT / "bigbet2_cohort_autobiographical_test_memory_posterior.csv", index=False)
    base_prob = base[TARGETS].to_numpy(dtype=np.float64)
    cells = candidate_cells(base_prob, memory_prob, test_feat, reliability)
    cells.to_csv(OUT / "bigbet2_cohort_autobiographical_atlas_cell_scores.csv", index=False)

    variants = [
        ("cohort_memory_balanced", 360, 0.38, 0.85, {"Q2", "Q3", "S1", "S2", "S3"}),
        ("cohort_memory_stage_heavy", 430, 0.48, 1.05, {"Q2", "Q3", "S1", "S2", "S3"}),
        ("cohort_memory_jackpot", 520, 0.55, 1.15, set(TARGETS)),
    ]
    result_rows = []
    selected_frames = []
    probs = {}
    for name, topn, amp, cap, targets in variants:
        selected, prob = materialize_variant(name, cells, base_prob, topn, amp, cap, targets)
        probs[name] = prob
        move = (logit(prob) - logit(base_prob)).reshape(-1)
        result_rows.append(
            {
                "variant": name,
                "selected_cells": int(len(selected)),
                "selected_rows": int(selected["row"].nunique()) if not selected.empty else 0,
                "move_l1": float(np.abs(move).sum()),
                "move_l2": float(np.linalg.norm(move)),
                "target_mix": selected["target"].value_counts().to_dict() if not selected.empty else {},
                **cosine_to_known(base_prob, prob),
            }
        )
        selected_frames.append(selected)
    results = pd.DataFrame(result_rows)
    results.to_csv(OUT / "bigbet2_cohort_autobiographical_atlas_results.csv", index=False)
    pd.concat(selected_frames, ignore_index=True).to_csv(OUT / "bigbet2_cohort_autobiographical_atlas_selected_cells.csv", index=False)

    promoted = "cohort_memory_stage_heavy"
    local_path, root_path = write_submission(sample, probs[promoted], "submission_bigbet2_cohort_autobiographical_atlas")
    decision = {
        "promoted_variant": promoted,
        "local_submission": str(local_path.resolve()),
        "root_submission": str(root_path.resolve()),
        "world_model": "test rows are hidden states in a subject autobiography, translated only when peer-cohort anomaly agrees",
        "kill_criterion": "if public worsens, same-subject memory is real locally but unsafe as a public/private row-target action decoder",
        "rows": len(sample),
        "keys_match_sample": True,
        "min_prob": float(probs[promoted].min()),
        "max_prob": float(probs[promoted].max()),
    }
    pd.DataFrame([decision]).to_csv(OUT / "bigbet2_cohort_autobiographical_atlas_decision.csv", index=False)
    print(pd.DataFrame([decision]).to_string(index=False))
    print(cv.to_string(index=False))
    print(results.to_string(index=False))


if __name__ == "__main__":
    main()
