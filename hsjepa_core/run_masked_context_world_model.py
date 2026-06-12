#!/usr/bin/env python3
"""OG-only masked-context world model for the HS-JEPA core.

This is a core-side experiment, not a leaderboard adapter.  It builds an
explicit JEPA-style target representation:

    visible lifelog views -> predicted hidden target-view representation

The output representation is then tested in three public-free ways:

1. Does it predict masked lifelog target views better than a shuffled null?
2. Does it improve grouped train-label probes or nearest-neighbor consistency?
3. Does its residual energy separate toxic cross-subject row-target actions?

The generated submission is an anchor-free diagnostic candidate based only on
the world-model representation and train labels.  It is not tuned to public LB.
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
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import log_loss, r2_score, roc_auc_score
from sklearn.model_selection import GroupKFold, LeaveOneGroupOut
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hsjepa_core.run_lifelog_core_state_evidence import (  # noqa: E402
    TARGETS,
    catalog_features,
    component_correlation,
    finite_matrix,
    format_float,
    load_frames,
    markdown_table,
    safe_auc,
    view_columns,
)


OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "masked_context_world_model"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "MASKED_CONTEXT_WORLD_MODEL_CORE_KO.md"
SAMPLE_SUBMISSION = ROOT / "data" / "ch2026_submission_sample.csv"
ACTION_AUDIT = (
    ROOT
    / "sleep_competition_adapter"
    / "outputs"
    / "cross_subject_surprise_responsibility_veto"
    / "cross_subject_surprise_oof_action_audit.csv"
)
NULL_REPEATS = 24
RANDOM_SEED = 20260613


def short_hash(frame: pd.DataFrame) -> str:
    arr = frame[TARGETS].to_numpy(dtype=np.float64)
    return hashlib.sha256(np.round(arr, 10).tobytes()).hexdigest()[:8]


def rank01(values: np.ndarray) -> np.ndarray:
    series = pd.Series(values, dtype="float64")
    if series.notna().sum() <= 1:
        return np.zeros(len(series), dtype=np.float64)
    return series.rank(method="average", pct=True).fillna(0.5).to_numpy(dtype=np.float64)


def target_transform(frame: pd.DataFrame, cols: list[str], dims: int) -> tuple[np.ndarray, SimpleImputer, StandardScaler, PCA]:
    y_imp = SimpleImputer(strategy="median")
    y_scaler = StandardScaler()
    y_scaled = y_scaler.fit_transform(y_imp.fit_transform(finite_matrix(frame, cols)))
    n_components = max(1, min(dims, y_scaled.shape[1], y_scaled.shape[0] - 1))
    pca = PCA(n_components=n_components, random_state=RANDOM_SEED)
    y_state = pca.fit_transform(y_scaled)
    return y_state, y_imp, y_scaler, pca


def apply_target_transform(
    frame: pd.DataFrame,
    cols: list[str],
    y_imp: SimpleImputer,
    y_scaler: StandardScaler,
    pca: PCA,
) -> np.ndarray:
    y_scaled = y_scaler.transform(y_imp.transform(finite_matrix(frame, cols)))
    return pca.transform(y_scaled)


def fit_predict_ridge(
    train_x: pd.DataFrame,
    train_y: np.ndarray,
    predict_x: pd.DataFrame,
    alpha: float = 18.0,
) -> np.ndarray:
    model = make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(),
        Ridge(alpha=alpha),
    )
    model.fit(train_x, train_y)
    return np.asarray(model.predict(predict_x), dtype=np.float64)


def build_world_model_state(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, list[str], list[str]]:
    """Create OOF train and train-fitted test masked-target representations."""
    views = view_columns(catalog_features(frame))
    if len(views) < 2:
        raise ValueError("at least two semantic views are required")
    all_view_cols = sorted({col for cols in views.values() for col in cols})
    train_idx = frame.index[frame["split"].eq("train")].to_numpy()
    test_idx = frame.index[frame["split"].eq("test")].to_numpy()
    train = frame.loc[train_idx].reset_index(drop=False).rename(columns={"index": "_source_index"})
    test = frame.loc[test_idx].reset_index(drop=False).rename(columns={"index": "_source_index"})
    groups = train["subject_id"].astype(str).to_numpy()
    splitter = GroupKFold(n_splits=max(2, min(5, len(np.unique(groups)))))
    rng = np.random.default_rng(RANDOM_SEED)

    state = frame[["subject_id", "sleep_date", "lifelog_date", "split", "metric_row"]].copy()
    metric_rows: list[dict[str, Any]] = []
    pred_cols: list[str] = []
    energy_cols: list[str] = []

    for target_view, y_cols in views.items():
        x_cols = [col for col in all_view_cols if col not in set(y_cols)]
        if len(x_cols) < 2:
            continue
        dims = 4
        train_y_state, y_imp, y_scaler, pca = target_transform(train, y_cols, dims)
        test_y_state = apply_target_transform(test, y_cols, y_imp, y_scaler, pca)
        n_components = train_y_state.shape[1]
        train_pred = np.zeros_like(train_y_state)
        train_null_pred = np.zeros_like(train_y_state)

        for fold, (tr, va) in enumerate(splitter.split(train, groups=groups)):
            train_pred[va] = fit_predict_ridge(
                finite_matrix(train.iloc[tr], x_cols),
                train_y_state[tr],
                finite_matrix(train.iloc[va], x_cols),
            )
            shuffled = train_y_state[tr].copy()
            rng.shuffle(shuffled, axis=0)
            train_null_pred[va] = fit_predict_ridge(
                finite_matrix(train.iloc[tr], x_cols),
                shuffled,
                finite_matrix(train.iloc[va], x_cols),
            )

        test_pred = fit_predict_ridge(
            finite_matrix(train, x_cols),
            train_y_state,
            finite_matrix(test, x_cols),
        )

        train_resid = train_y_state - train_pred
        test_resid = test_y_state - test_pred
        train_energy = np.sqrt(np.mean(np.square(train_resid), axis=1))
        test_energy = np.sqrt(np.mean(np.square(test_resid), axis=1))

        for comp in range(n_components):
            pred_col = f"wm_pred_{target_view}_c{comp + 1}"
            resid_col = f"wm_resid_{target_view}_c{comp + 1}"
            pred_cols.append(pred_col)
            state.loc[train_idx, pred_col] = train_pred[:, comp]
            state.loc[test_idx, pred_col] = test_pred[:, comp]
            state.loc[train_idx, resid_col] = train_resid[:, comp]
            state.loc[test_idx, resid_col] = test_resid[:, comp]
        energy_col = f"wm_energy_{target_view}"
        rank_col = f"wm_energy_rank_{target_view}"
        energy_cols.extend([energy_col, rank_col])
        state.loc[train_idx, energy_col] = train_energy
        state.loc[test_idx, energy_col] = test_energy
        state.loc[train_idx, rank_col] = rank01(train_energy)
        state.loc[test_idx, rank_col] = rank01(test_energy)

        metric_rows.append(
            {
                "target_view": target_view,
                "context_feature_count": len(x_cols),
                "target_feature_count": len(y_cols),
                "components": n_components,
                "oof_r2": float(r2_score(train_y_state, train_pred, multioutput="variance_weighted")),
                "null_oof_r2": float(r2_score(train_y_state, train_null_pred, multioutput="variance_weighted")),
                "r2_lift_vs_null": float(
                    r2_score(train_y_state, train_pred, multioutput="variance_weighted")
                    - r2_score(train_y_state, train_null_pred, multioutput="variance_weighted")
                ),
                "oof_component_corr": component_correlation(train_y_state, train_pred),
                "null_component_corr": component_correlation(train_y_state, train_null_pred),
                "component_corr_lift_vs_null": component_correlation(train_y_state, train_pred)
                - component_correlation(train_y_state, train_null_pred),
                "train_energy_mean": float(np.mean(train_energy)),
                "test_energy_mean": float(np.mean(test_energy)),
                "uses_public_score": False,
                "uses_train_labels": False,
            }
        )

    state["wm_energy_mean"] = state[[c for c in energy_cols if "_rank_" not in c]].mean(axis=1)
    state["wm_energy_max"] = state[[c for c in energy_cols if "_rank_" not in c]].max(axis=1)
    state["wm_energy_rank_mean"] = state[[c for c in energy_cols if "_rank_" in c]].mean(axis=1)
    state["wm_energy_rank_max"] = state[[c for c in energy_cols if "_rank_" in c]].max(axis=1)
    energy_cols.extend(["wm_energy_mean", "wm_energy_max", "wm_energy_rank_mean", "wm_energy_rank_max"])
    return state, pd.DataFrame(metric_rows), pred_cols, energy_cols


def label_probe(
    frame: pd.DataFrame,
    state: pd.DataFrame,
    pred_cols: list[str],
    energy_cols: list[str],
) -> pd.DataFrame:
    train = frame[frame["split"].eq("train")].reset_index(drop=True)
    state_train = state[state["split"].eq("train")].reset_index(drop=True)
    y_all = train[TARGETS].astype(int)
    groups = train["subject_id"].astype(str).to_numpy()
    splitter = GroupKFold(n_splits=max(2, min(5, len(np.unique(groups)))))
    feature_sets = {
        "prior_only": [],
        "masked_world_predicted_state": pred_cols,
        "masked_world_surprise_energy": energy_cols,
        "masked_world_full_state": pred_cols + energy_cols + [c for c in state_train.columns if c.startswith("wm_resid_")],
    }
    rows: list[dict[str, Any]] = []
    for feature_set, cols in feature_sets.items():
        oof = pd.DataFrame(index=train.index, columns=TARGETS, dtype=float)
        for fold, (tr, va) in enumerate(splitter.split(train, groups=groups)):
            for target in TARGETS:
                y_train = y_all.iloc[tr][target].to_numpy(dtype=int)
                prior = float(np.clip(y_train.mean(), 1e-5, 1 - 1e-5))
                if not cols or len(np.unique(y_train)) < 2:
                    pred = np.full(len(va), prior, dtype=np.float64)
                else:
                    model = make_pipeline(
                        SimpleImputer(strategy="median"),
                        StandardScaler(),
                        LogisticRegression(C=0.2, max_iter=5000, solver="lbfgs"),
                    )
                    model.fit(state_train.iloc[tr][cols], y_train)
                    pred = np.clip(model.predict_proba(state_train.iloc[va][cols])[:, 1], 1e-5, 1 - 1e-5)
                oof.loc[va, target] = pred
        target_losses = []
        target_aucs = []
        for target in TARGETS:
            y = y_all[target].to_numpy(dtype=int)
            p = oof[target].to_numpy(dtype=np.float64)
            loss = float(log_loss(y, p, labels=[0, 1]))
            auc = safe_auc(y, p)
            target_losses.append(loss)
            if auc is not None:
                target_aucs.append(auc)
            rows.append(
                {
                    "test": "grouped_label_probe",
                    "feature_set": feature_set,
                    "target": target,
                    "logloss": loss,
                    "auc": auc,
                    "uses_public_score": False,
                }
            )
        rows.append(
            {
                "test": "grouped_label_probe",
                "feature_set": feature_set,
                "target": "all",
                "logloss": float(np.mean(target_losses)),
                "auc": float(np.nanmean(target_aucs)) if target_aucs else None,
                "uses_public_score": False,
            }
        )
    return pd.DataFrame(rows)


def nearest_neighbor_consistency(
    frame: pd.DataFrame,
    state: pd.DataFrame,
    pred_cols: list[str],
    energy_cols: list[str],
) -> pd.DataFrame:
    train_state = state[state["split"].eq("train")].reset_index(drop=True)
    labels = frame[frame["split"].eq("train")][TARGETS].astype(int).to_numpy()
    reps = {
        "masked_world_predicted_state": pred_cols,
        "masked_world_full_state": pred_cols + energy_cols + [c for c in train_state.columns if c.startswith("wm_resid_")],
    }
    rng = np.random.default_rng(RANDOM_SEED)
    rows: list[dict[str, Any]] = []
    for name, cols in reps.items():
        x = SimpleImputer(strategy="median").fit_transform(train_state[cols])
        x = StandardScaler().fit_transform(x)
        if x.shape[1] > 12:
            x = PCA(n_components=min(12, x.shape[0] - 1), random_state=RANDOM_SEED).fit_transform(x)
        nn = NearestNeighbors(n_neighbors=min(6, len(train_state)), metric="euclidean")
        nn.fit(x)
        _, idx = nn.kneighbors(x)
        idx = idx[:, 1:]
        near_match = []
        random_match = []
        for row in range(len(train_state)):
            near_match.append((labels[idx[row]] == labels[row]).mean(axis=0))
            pool = [i for i in range(len(train_state)) if i != row]
            rnd = rng.choice(pool, size=idx.shape[1], replace=False)
            random_match.append((labels[rnd] == labels[row]).mean(axis=0))
        near = np.vstack(near_match)
        rnd = np.vstack(random_match)
        for target_idx, target in enumerate(TARGETS):
            rows.append(
                {
                    "representation": name,
                    "target": target,
                    "neighbor_match_rate": float(near[:, target_idx].mean()),
                    "random_match_rate": float(rnd[:, target_idx].mean()),
                    "lift": float(near[:, target_idx].mean() - rnd[:, target_idx].mean()),
                    "uses_public_score": False,
                }
            )
        rows.append(
            {
                "representation": name,
                "target": "all",
                "neighbor_match_rate": float(near.mean()),
                "random_match_rate": float(rnd.mean()),
                "lift": float(near.mean() - rnd.mean()),
                "uses_public_score": False,
            }
        )
    return pd.DataFrame(rows)


def grouped_knn_predictions(
    frame: pd.DataFrame,
    state: pd.DataFrame,
    feature_cols: list[str],
    neighbors: int = 17,
) -> tuple[pd.DataFrame, float]:
    train = frame[frame["split"].eq("train")].reset_index(drop=True)
    state_train = state[state["split"].eq("train")].reset_index(drop=True)
    groups = train["subject_id"].astype(str).to_numpy()
    splitter = GroupKFold(n_splits=max(2, min(5, len(np.unique(groups)))))
    y = train[TARGETS].astype(float).to_numpy()
    oof = np.zeros_like(y)
    for tr, va in splitter.split(train, groups=groups):
        imputer = SimpleImputer(strategy="median")
        scaler = StandardScaler()
        x_tr = scaler.fit_transform(imputer.fit_transform(state_train.iloc[tr][feature_cols]))
        x_va = scaler.transform(imputer.transform(state_train.iloc[va][feature_cols]))
        nn = NearestNeighbors(n_neighbors=min(neighbors, len(tr)), metric="euclidean")
        nn.fit(x_tr)
        dist, idx = nn.kneighbors(x_va)
        weights = 1.0 / np.maximum(dist, 1e-6)
        weights = weights / weights.sum(axis=1, keepdims=True)
        fold_pred = np.einsum("ij,ijt->it", weights, y[tr][idx])
        fold_prior = y[tr].mean(axis=0)
        oof[va] = 0.85 * fold_pred + 0.15 * fold_prior
    oof = np.clip(oof, 0.02, 0.98)
    mean_loss = float(np.mean([log_loss(y[:, i], oof[:, i], labels=[0, 1]) for i in range(len(TARGETS))]))
    pred = train[["subject_id", "sleep_date", "lifelog_date"]].copy()
    pred[TARGETS] = oof
    return pred, mean_loss


def build_submission(
    frame: pd.DataFrame,
    state: pd.DataFrame,
    feature_cols: list[str],
    neighbors: int = 17,
) -> pd.DataFrame:
    sample = pd.read_csv(SAMPLE_SUBMISSION)
    train = frame[frame["split"].eq("train")].reset_index(drop=True)
    test = frame[frame["split"].eq("test")].reset_index(drop=True)
    state_train = state[state["split"].eq("train")].reset_index(drop=True)
    state_test = state[state["split"].eq("test")].reset_index(drop=True)
    imputer = SimpleImputer(strategy="median")
    scaler = StandardScaler()
    x_train = scaler.fit_transform(imputer.fit_transform(state_train[feature_cols]))
    x_test = scaler.transform(imputer.transform(state_test[feature_cols]))
    y = train[TARGETS].astype(float).to_numpy()
    nn = NearestNeighbors(n_neighbors=min(neighbors, len(train)), metric="euclidean")
    nn.fit(x_train)
    dist, idx = nn.kneighbors(x_test)
    weights = 1.0 / np.maximum(dist, 1e-6)
    weights = weights / weights.sum(axis=1, keepdims=True)
    pred = np.einsum("ij,ijt->it", weights, y[idx])
    pred = 0.85 * pred + 0.15 * y.mean(axis=0)
    out = sample.copy()
    out[TARGETS] = np.clip(pred, 0.02, 0.98)
    if list(out[["subject_id", "sleep_date", "lifelog_date"]].itertuples(index=False, name=None)) != list(
        test[["subject_id", "sleep_date", "lifelog_date"]].itertuples(index=False, name=None)
    ):
        raise ValueError("test rows do not match sample submission")
    return out


def action_health_probe(state: pd.DataFrame, energy_cols: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    if not ACTION_AUDIT.exists():
        return pd.DataFrame(), pd.DataFrame()
    actions = pd.read_csv(ACTION_AUDIT)
    train_state = state[state["split"].eq("train")].reset_index(drop=True).copy()
    train_state["row"] = train_state["metric_row"].astype(int)
    keep_cols = ["row", "subject_id"] + energy_cols
    audit = actions.merge(train_state[keep_cols], on=["row", "subject_id"], how="left", suffixes=("", "_wm"))
    audit = audit.dropna(subset=["true_gain", "wm_energy_rank_mean"])
    score_cols = [c for c in energy_cols if c in audit.columns]
    rows: list[dict[str, Any]] = []
    for target, part in audit.groupby("target", observed=True):
        for score_col in score_cols:
            if part[score_col].nunique(dropna=True) < 2:
                continue
            median = float(part[score_col].median())
            low = part[part[score_col] <= median]
            high = part[part[score_col] > median]
            for mode, selected in [("low_energy_listener", low), ("high_energy_listener", high), ("all", part)]:
                if selected.empty:
                    continue
                rows.append(
                    {
                        "target": target,
                        "score_col": score_col,
                        "mode": mode,
                        "median": median,
                        "cells": int(len(selected)),
                        "gain_sum": float(selected["true_gain"].sum()),
                        "mean_gain": float(selected["true_gain"].mean()),
                        "positive_gain_rate": float((selected["true_gain"] > 0).mean()),
                    }
                )
    detail = pd.DataFrame(rows)
    if detail.empty:
        return audit, detail

    selected_rules = []
    for target, part in detail[detail["mode"].ne("all")].groupby("target", observed=True):
        best = part.sort_values(["gain_sum", "mean_gain"], ascending=False).iloc[0]
        all_row = detail[(detail["target"].eq(target)) & (detail["score_col"].eq(best["score_col"])) & (detail["mode"].eq("all"))].iloc[0]
        selected_rules.append(
            {
                "target": target,
                "selected_score_col": best["score_col"],
                "selected_mode": best["mode"],
                "selected_cells": int(best["cells"]),
                "selected_gain_sum": float(best["gain_sum"]),
                "all_gain_sum": float(all_row["gain_sum"]),
                "removed_gain_sum": float(all_row["gain_sum"] - best["gain_sum"]),
                "selected_positive_gain_rate": float(best["positive_gain_rate"]),
                "all_positive_gain_rate": float(all_row["positive_gain_rate"]),
            }
        )
    rules = pd.DataFrame(selected_rules)

    if len(audit) >= 12 and audit["subject_id"].nunique() >= 3 and audit["true_gain"].gt(0).nunique():
        features = ["wm_energy_mean", "wm_energy_max", "wm_energy_rank_mean", "wm_energy_rank_max"]
        logo = LeaveOneGroupOut()
        y = audit["true_gain"].gt(0).astype(int).to_numpy()
        score = np.full(len(audit), np.nan)
        for tr, va in logo.split(audit, groups=audit["subject_id"].astype(str)):
            if len(np.unique(y[tr])) < 2:
                continue
            model = make_pipeline(
                SimpleImputer(strategy="median"),
                StandardScaler(),
                LogisticRegression(C=0.4, max_iter=5000, solver="lbfgs"),
            )
            model.fit(audit.iloc[tr][features], y[tr])
            score[va] = model.predict_proba(audit.iloc[va][features])[:, 1]
        valid = np.isfinite(score)
        auc = roc_auc_score(y[valid], score[valid]) if valid.sum() and len(np.unique(y[valid])) > 1 else np.nan
        rules = pd.concat(
            [
                rules,
                pd.DataFrame(
                    [
                        {
                            "target": "all_subject_heldout_classifier",
                            "selected_score_col": "world_model_energy_features",
                            "selected_mode": "leave_one_subject_out_logistic",
                            "selected_cells": int(valid.sum()),
                            "selected_gain_sum": float(audit.loc[valid & (score >= np.nanmedian(score)), "true_gain"].sum()),
                            "all_gain_sum": float(audit.loc[valid, "true_gain"].sum()),
                            "removed_gain_sum": float(
                                audit.loc[valid, "true_gain"].sum()
                                - audit.loc[valid & (score >= np.nanmedian(score)), "true_gain"].sum()
                            ),
                            "selected_positive_gain_rate": float(
                                (audit.loc[valid & (score >= np.nanmedian(score)), "true_gain"] > 0).mean()
                            ),
                            "all_positive_gain_rate": float((audit.loc[valid, "true_gain"] > 0).mean()),
                            "subject_heldout_positive_gain_auc": float(auc) if math.isfinite(auc) else None,
                        }
                    ]
                ),
            ],
            ignore_index=True,
        )
    return audit, detail.merge(rules, how="left", on="target", suffixes=("", "_selected"))


def build_summary(
    view_metrics: pd.DataFrame,
    label_metrics: pd.DataFrame,
    neighbors: pd.DataFrame,
    action_detail: pd.DataFrame,
    knn_oof_logloss: float,
    candidate_file: str,
) -> dict[str, Any]:
    best_view = view_metrics.sort_values("component_corr_lift_vs_null", ascending=False).head(1)
    label_all = label_metrics[label_metrics["target"].eq("all")].sort_values("logloss")
    prior = label_all[label_all["feature_set"].eq("prior_only")]
    world = label_all[label_all["feature_set"].eq("masked_world_full_state")]
    neighbor_all = neighbors[neighbors["target"].eq("all")].sort_values("lift", ascending=False).head(1)
    rules = selected_action_rules(action_detail)
    return {
        "package": "masked_context_world_model_core",
        "status": "core_representation_probe_ready",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "view_count": int(len(view_metrics)),
        "best_masked_view": None if best_view.empty else best_view.iloc[0].to_dict(),
        "label_probe_best": None if label_all.empty else label_all.iloc[0].to_dict(),
        "prior_mean_logloss": None if prior.empty else float(prior["logloss"].iloc[0]),
        "world_full_mean_logloss": None if world.empty else float(world["logloss"].iloc[0]),
        "world_full_delta_vs_prior": None
        if prior.empty or world.empty
        else float(world["logloss"].iloc[0] - prior["logloss"].iloc[0]),
        "world_knn_oof_logloss": knn_oof_logloss,
        "best_neighbor_consistency": None if neighbor_all.empty else neighbor_all.iloc[0].to_dict(),
        "action_health_best_rules": [] if rules.empty else rules.to_dict(orient="records"),
        "candidate_file": candidate_file,
    }


def selected_action_rules(action_detail: pd.DataFrame) -> pd.DataFrame:
    if action_detail.empty or "selected_score_col" not in action_detail.columns:
        return pd.DataFrame()
    cols = [
        "target",
        "selected_score_col",
        "selected_mode",
        "selected_cells",
        "selected_gain_sum",
        "all_gain_sum",
        "removed_gain_sum",
        "selected_positive_gain_rate",
        "all_positive_gain_rate",
    ]
    rules = (
        action_detail.dropna(subset=["selected_score_col"])
        .loc[:, cols]
        .drop_duplicates()
        .sort_values(["removed_gain_sum", "selected_gain_sum"], ascending=[True, False])
    )
    return rules


def build_markdown(
    summary: dict[str, Any],
    view_metrics: pd.DataFrame,
    label_metrics: pd.DataFrame,
    neighbors: pd.DataFrame,
    action_detail: pd.DataFrame,
    candidate_file: str,
) -> str:
    label_all = label_metrics[label_metrics["target"].eq("all")].sort_values("logloss")
    neighbor_all = neighbors[neighbors["target"].eq("all")].sort_values("lift", ascending=False)
    action_rules = selected_action_rules(action_detail)
    best_view = summary.get("best_masked_view") or {}
    return f"""# Masked Context World Model Core

## 한 줄 요약

HS-JEPA core를 더 직접적인 JEPA 형태로 만든 실험이다.

```text
visible lifelog views
  -> predict masked target-view representation
  -> predicted state + residual surprise energy
  -> label/action structure probe
```

이 실험은 competition adapter가 아니라 core representation probe다.

## 사용하지 않은 정보

- public LB ledger: `{summary["uses_public_score_ledger"]}`
- prior submission probability: `{summary["uses_prior_submission_probabilities"]}`
- proprietary embedding API: `{summary["uses_proprietary_embedding_api"]}`

## 왜 이것이 HS-JEPA core인가

이전 adapter 실험들은 `hidden state -> row-target action` 번역에 가까웠다.
이번 실험은 그보다 앞단을 본다.

```text
보이는 생활 context 일부만 보고,
보이지 않는 target-view representation을 예측할 수 있는가?
```

여기서 target은 Q/S label이 아니라 phone, body, app, mobility 같은 semantic lifelog view의 PCA representation이다.
즉 raw value reconstruction이 아니라 view-level latent prediction이다.

## Masked View Prediction 결과

- best target view: `{best_view.get("target_view", "NA")}`
- best component corr lift vs null: `{format_float(best_view.get("component_corr_lift_vs_null"), 6)}`
- best R2 lift vs null: `{format_float(best_view.get("r2_lift_vs_null"), 6)}`

{markdown_table(view_metrics.sort_values("component_corr_lift_vs_null", ascending=False), ["target_view", "context_feature_count", "target_feature_count", "components", "oof_r2", "null_oof_r2", "r2_lift_vs_null", "oof_component_corr", "component_corr_lift_vs_null"], max_rows=12)}

## Grouped Label Probe

이 평가는 label을 학습하지만, representation 자체는 label 없이 만든다.
같은 subject가 train/valid 양쪽에 동시에 들어가지 않도록 GroupKFold로 검증했다.

{markdown_table(label_all, ["feature_set", "logloss", "auc"], max_rows=10)}

요약:

- prior mean logloss: `{format_float(summary.get("prior_mean_logloss"), 6)}`
- masked world full-state mean logloss: `{format_float(summary.get("world_full_mean_logloss"), 6)}`
- delta vs prior: `{format_float(summary.get("world_full_delta_vs_prior"), 6)}`
- world-model KNN OOF logloss: `{format_float(summary.get("world_knn_oof_logloss"), 6)}`

이 결과는 중요한 negative evidence다. Masked world-model representation은 label-free hidden state로는 의미가 있지만,
그 자체를 direct label predictor로 쓰면 prior보다 나쁘다. 따라서 HS-JEPA core를 classifier로 포장하면 안 된다.

## Nearest-Neighbor Label Consistency

좋은 hidden state라면 가까운 row의 target vector가 random row보다 더 비슷해야 한다.

{markdown_table(neighbor_all, ["representation", "neighbor_match_rate", "random_match_rate", "lift"], max_rows=10)}

## Action-Health Diagnostic

이 부분은 core-only가 아니라 adapter diagnostic이다.
cross-subject prototype transport가 만든 OOF action field를 외부 평가 대상으로 두고,
world-model residual energy가 toxic action을 분리하는지 본다.

{markdown_table(action_rules, ["target", "selected_score_col", "selected_mode", "selected_cells", "selected_gain_sum", "all_gain_sum", "removed_gain_sum", "selected_positive_gain_rate", "all_positive_gain_rate"], max_rows=20)}

## Anchor-Free Candidate

world-model state만으로 train nearest-neighbor target probability를 만든 diagnostic submission을 생성했다.

- candidate: `{candidate_file}`

이 후보는 public LB를 맞추기 위한 파일이 아니라, core representation만으로 어디까지 갈 수 있는지 확인하는 anchor-free sensor다.

## 해석

강한 성공 조건은 다음이다.

```text
masked target-view prediction이 null보다 낫고,
그 predicted/residual state가 label consistency와 action toxicity를 동시에 설명한다.
```

실패한다면 HS-JEPA core는 human-state representation으로는 의미가 있지만,
row-target action release에는 별도의 adapter와 diagnostic이 필수라는 결론이 강화된다.
"""


def validate_submission(frame: pd.DataFrame) -> dict[str, Any]:
    problems = []
    if len(frame) != 250:
        problems.append(f"expected 250 rows, got {len(frame)}")
    for col in TARGETS:
        if col not in frame.columns:
            problems.append(f"missing target {col}")
            continue
        values = pd.to_numeric(frame[col], errors="coerce")
        if values.isna().any():
            problems.append(f"{col} contains NaN")
        if ((values < 0) | (values > 1)).any():
            problems.append(f"{col} outside [0,1]")
    return {
        "valid": not problems,
        "problems": problems,
        "rows": int(len(frame)),
        "probability_min": float(frame[TARGETS].min().min()) if all(c in frame for c in TARGETS) else None,
        "probability_max": float(frame[TARGETS].max().max()) if all(c in frame for c in TARGETS) else None,
    }


def run() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frame, _ = load_frames()
    state, view_metrics, pred_cols, energy_cols = build_world_model_state(frame)
    label_metrics = label_probe(frame, state, pred_cols, energy_cols)
    neighbors = nearest_neighbor_consistency(frame, state, pred_cols, energy_cols)
    oof_knn, knn_oof_logloss = grouped_knn_predictions(
        frame,
        state,
        pred_cols + energy_cols + [c for c in state.columns if c.startswith("wm_resid_")],
    )
    action_audit, action_detail = action_health_probe(state, energy_cols)
    candidate = build_submission(
        frame,
        state,
        pred_cols + energy_cols + [c for c in state.columns if c.startswith("wm_resid_")],
    )
    validation = validate_submission(candidate)
    if not validation["valid"]:
        raise ValueError(f"candidate is not upload-safe: {validation['problems']}")
    candidate_file = f"submission_hsjepa_masked_context_world_model_core_{short_hash(candidate)}_uploadsafe.csv"

    summary = build_summary(view_metrics, label_metrics, neighbors, action_detail, knn_oof_logloss, candidate_file)
    summary["validation"] = validation

    state.to_csv(OUT_DIR / "masked_context_world_model_state.csv", index=False)
    view_metrics.to_csv(OUT_DIR / "masked_view_prediction_metrics.csv", index=False)
    label_metrics.to_csv(OUT_DIR / "masked_world_label_probe_metrics.csv", index=False)
    neighbors.to_csv(OUT_DIR / "masked_world_neighbor_consistency.csv", index=False)
    oof_knn.to_csv(OUT_DIR / "masked_world_knn_oof_predictions.csv", index=False)
    action_audit.to_csv(OUT_DIR / "masked_world_action_audit.csv", index=False)
    action_detail.to_csv(OUT_DIR / "masked_world_action_health_rules.csv", index=False)
    selected_action_rules(action_detail).to_csv(OUT_DIR / "masked_world_selected_action_rules.csv", index=False)
    candidate.to_csv(OUT_DIR / candidate_file, index=False)
    candidate.to_csv(ROOT / candidate_file, index=False)
    (OUT_DIR / "masked_context_world_model_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    md = build_markdown(summary, view_metrics, label_metrics, neighbors, action_detail, candidate_file)
    (OUT_DIR / "MASKED_CONTEXT_WORLD_MODEL_CORE_KO.md").write_text(md.rstrip() + "\n", encoding="utf-8")
    PAPER_DOC.write_text(md.rstrip() + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
