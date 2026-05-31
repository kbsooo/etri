#!/usr/bin/env python3
"""E369: public-free Q2/S1 lifestyle-transfer audit.

Question:
    E368 found a Q2/S1 cell action that beats direct-public and null controls
    under public-observation jackknife.  Does that action also line up with a
    train-side hidden lifestyle state, without using public LB as the teacher?

JEPA/data2vec translation:
    context = lifestyle views already built from app/social/cash/raw/calendar
              and masked-view JEPA residuals
    target  = train-side subject/calendar residual states for Q2 and S1
    audit   = compare the public-free residual state projected onto test rows
              against the E368 Q2/S1 gate and actual selected cell movement

This script intentionally does not create a new submission.  It is a validity
check for whether E368 is backed by a transferable hidden lifestyle state.
"""

from __future__ import annotations

import hashlib
import sys
import warnings
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import log_loss, r2_score
from sklearn.model_selection import GroupKFold
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

from e328_ownlatent_lifestyle_state_experiment import (  # noqa: E402
    E247,
    E323,
    build_views,
    clip_prob,
    load_frames,
    load_sub_frame,
    md_table,
    normalize_dates,
    require_aligned,
)
from e330_target_residual_lifestyle_latent import (  # noqa: E402
    base_label_matrix_all,
    cv_logloss,
    fit_logistic_predict,
    fit_ridge_full_predict,
    groups_for,
    oof_proba,
    oof_ridge_scalar,
    safe_spearman,
)
from e357_public_survival_contrast_latent import KEY, TARGETS  # noqa: E402
from public_anchor_bottleneck_decomposition import logit  # noqa: E402


RNG_SEED = 20260531 + 369
TARGET_FOCUS = ["Q2", "S1"]
VIEW_IDS = ["family", "jepa_resid", "story_bundle", "raw_day", "family_story", "family_jepa_story"]
GROUP_SPLITS = ["subject", "dateblock"]
KNN_KS = [8, 16, 32]
CLUSTERS = [6, 8, 10, 12]
NULL_REPS = 160
EPS = 1.0e-12

E365_SELECTION = OUT / "e365_public_like_jackknife_selection.csv"
E368_SELECTION = OUT / "e368_q2s1_rowmask_cellaction_selection.csv"
E368_ROWMASK = OUT / "e368_q2s1_rowmask_cellaction_rows.csv"

SUMMARY_OUT = OUT / "e369_q2s1_lifestyle_transfer_summary.csv"
LOCAL_OUT = OUT / "e369_q2s1_lifestyle_transfer_local_residual.csv"
KNN_OUT = OUT / "e369_q2s1_lifestyle_transfer_knn.csv"
CLUSTER_OUT = OUT / "e369_q2s1_lifestyle_transfer_clusters.csv"
NULL_OUT = OUT / "e369_q2s1_lifestyle_transfer_nulls.csv"
MOVEMENT_OUT = OUT / "e369_q2s1_lifestyle_transfer_movement.csv"
DECISION_OUT = OUT / "e369_q2s1_lifestyle_transfer_decision.csv"
REPORT_OUT = OUT / "e369_q2s1_lifestyle_transfer_report.md"


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def stable_seed(*parts: object) -> int:
    payload = "|".join(map(str, parts)).encode("utf-8")
    return RNG_SEED + int(hashlib.sha1(payload).hexdigest()[:8], 16) % 100000


def rank01(values: np.ndarray | pd.Series) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64)
    arr = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0)
    if len(arr) <= 1:
        return np.zeros_like(arr)
    order = pd.Series(arr).rank(method="average").to_numpy(dtype=np.float64) - 1.0
    denom = float(len(arr) - 1)
    return order / denom if denom > 0 else np.zeros_like(arr)


def z01(values: np.ndarray | pd.Series) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64)
    arr = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0)
    sd = float(np.std(arr))
    if not np.isfinite(sd) or sd < EPS:
        return np.zeros_like(arr)
    return (arr - float(np.mean(arr))) / sd


def tail_lift(score: np.ndarray, gate: np.ndarray, q: float = 0.80) -> float:
    score = np.asarray(score, dtype=np.float64)
    gate = np.asarray(gate, dtype=np.float64)
    if len(score) < 5 or np.nanstd(score) < EPS or np.nanstd(gate) < EPS:
        return 0.0
    cut = float(np.quantile(gate, q))
    high = score[gate >= cut]
    rest = score[gate < cut]
    if len(high) == 0 or len(rest) == 0:
        return 0.0
    return float(np.nanmean(high) - np.nanmean(rest))


def null_p95(metric_values: list[float]) -> float:
    vals = np.asarray(metric_values, dtype=np.float64)
    vals = np.abs(vals[np.isfinite(vals)])
    if len(vals) == 0:
        return 0.0
    return float(np.quantile(vals, 0.95))


def support_from_null(actual: float, p95: float, min_abs: float = 0.08) -> bool:
    return bool(abs(float(actual)) > max(float(p95), min_abs))


def load_selected_paths() -> tuple[Path, Path]:
    e365 = Path(str(pd.read_csv(E365_SELECTION).iloc[0]["selected_uploadsafe_file"]))
    e368 = Path(str(pd.read_csv(E368_SELECTION).iloc[0]["selected_uploadsafe_file"]))
    if not e365.is_absolute():
        e365 = ROOT / e365
    if not e368.is_absolute():
        e368 = ROOT / e368
    if not e365.exists():
        raise FileNotFoundError(e365)
    if not e368.exists():
        raise FileNotFoundError(e368)
    return e365, e368


def load_e368_gate(test_keys: pd.DataFrame) -> pd.DataFrame:
    rowmask = normalize_dates(pd.read_csv(E368_ROWMASK)).sort_values(KEY).reset_index(drop=True)
    sample = normalize_dates(test_keys.copy()).sort_values(KEY).reset_index(drop=True)
    require_aligned(sample, rowmask[KEY], "e368_rowmask")
    out = sample.copy()
    out["q2_gate_pred"] = rank01(rowmask["pred_public_validity_Q2"])
    out["s1_gate_pred"] = rank01(rowmask["pred_public_validity_S1"])
    out["q2_gate_direct_sensor"] = rank01(rowmask["public_validity_Q2"])
    out["s1_gate_direct_sensor"] = rank01(rowmask["public_validity_S1"])
    out["bad_gate_pred"] = rank01(rowmask["pred_bad_rank"])
    out["row_validity_pred"] = rank01(rowmask["pred_public_row_validity"])
    return out


def as_model_frame(view: pd.DataFrame) -> pd.DataFrame:
    return view.replace([np.inf, -np.inf], 0.0).fillna(0.0).reset_index(drop=True)


def fit_base_context_residuals(
    train: pd.DataFrame,
    test: pd.DataFrame,
    views: dict[str, pd.DataFrame],
    train_mask: np.ndarray,
) -> tuple[pd.DataFrame, dict[tuple[str, str, str], dict[str, Any]]]:
    base_x_train, base_x_test = base_label_matrix_all(train, test)
    train_views = {k: as_model_frame(v.loc[train_mask]) for k, v in views.items() if k in VIEW_IDS}
    test_views = {k: as_model_frame(v.loc[~train_mask]) for k, v in views.items() if k in VIEW_IDS}

    rows: list[dict[str, Any]] = []
    pred_store: dict[tuple[str, str, str], dict[str, Any]] = {}
    for split_name in GROUP_SPLITS:
        groups = groups_for(train, split_name).reset_index(drop=True)
        if int(groups.nunique()) < 3:
            continue
        for target in TARGET_FOCUS:
            y = train[target].astype(int).to_numpy()
            base_oof = oof_proba(base_x_train, y, groups)
            base_loss = cv_logloss(base_x_train, y, groups)
            teacher = y.astype(float) - base_oof
            for view_id in VIEW_IDS:
                x_train = train_views[view_id]
                x_test = test_views[view_id]
                pred_oof, _full_train, r2 = oof_ridge_scalar(x_train, teacher, groups)
                pred_test = fit_ridge_full_predict(x_train, teacher, x_test)
                pred_store[(target, view_id, split_name)] = {
                    "train_score": pred_oof,
                    "test_score": pred_test,
                    "teacher": teacher,
                    "base_oof": base_oof,
                    "groups": groups,
                }
                aug_x = pd.concat([base_x_train.reset_index(drop=True), pd.Series(pred_oof, name="lifestyle_resid_state")], axis=1)
                aug_loss = cv_logloss(aug_x, y, groups)
                rows.append(
                    {
                        "target": target,
                        "view_id": view_id,
                        "split": split_name,
                        "method": "masked_residual_student",
                        "base_logloss": float(base_loss),
                        "aug_logloss": float(aug_loss),
                        "logloss_delta": float(aug_loss - base_loss),
                        "teacher_r2": float(r2),
                        "teacher_spearman": safe_spearman(teacher, pred_oof),
                    }
                )
    return pd.DataFrame(rows), pred_store


def scaler_fit(train_x: pd.DataFrame, test_x: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    train_x = as_model_frame(train_x)
    test_x = as_model_frame(test_x)
    train_x, test_x = train_x.align(test_x, join="outer", axis=1, fill_value=0.0)
    pipe = make_pipeline(SimpleImputer(strategy="median"), StandardScaler())
    xtr = pipe.fit_transform(train_x)
    xte = pipe.transform(test_x)
    return np.asarray(xtr, dtype=np.float64), np.asarray(xte, dtype=np.float64)


def build_knn_scores(
    train: pd.DataFrame,
    views: dict[str, pd.DataFrame],
    train_mask: np.ndarray,
    pred_store: dict[tuple[str, str, str], dict[str, Any]],
) -> tuple[pd.DataFrame, dict[tuple[str, str, str, int], np.ndarray]]:
    rows: list[dict[str, Any]] = []
    score_store: dict[tuple[str, str, str, int], np.ndarray] = {}
    for target in TARGET_FOCUS:
        for split_name in GROUP_SPLITS:
            for view_id in VIEW_IDS:
                key = (target, view_id, split_name)
                if key not in pred_store:
                    continue
                train_score = np.asarray(pred_store[key]["teacher"], dtype=np.float64)
                xtr, xte = scaler_fit(views[view_id].loc[train_mask], views[view_id].loc[~train_mask])
                max_k = min(max(KNN_KS), len(xtr))
                nn = NearestNeighbors(n_neighbors=max_k, metric="euclidean")
                nn.fit(xtr)
                dist, idx = nn.kneighbors(xte, return_distance=True)
                for k in KNN_KS:
                    kk = min(k, max_k)
                    local = train_score[idx[:, :kk]].mean(axis=1)
                    score_store[(target, view_id, split_name, k)] = local
                    rows.append(
                        {
                            "target": target,
                            "view_id": view_id,
                            "split": split_name,
                            "method": f"knn{k}_train_residual",
                            "mean_neighbor_dist": float(np.mean(dist[:, :kk])),
                            "std_score": float(np.std(local)),
                        }
                    )
    return pd.DataFrame(rows), score_store


def build_cluster_scores(
    train: pd.DataFrame,
    views: dict[str, pd.DataFrame],
    train_mask: np.ndarray,
    pred_store: dict[tuple[str, str, str], dict[str, Any]],
) -> tuple[pd.DataFrame, dict[tuple[str, str, str, int], np.ndarray]]:
    rows: list[dict[str, Any]] = []
    score_store: dict[tuple[str, str, str, int], np.ndarray] = {}
    for target in TARGET_FOCUS:
        for split_name in GROUP_SPLITS:
            for view_id in VIEW_IDS:
                key = (target, view_id, split_name)
                if key not in pred_store:
                    continue
                teacher = np.asarray(pred_store[key]["teacher"], dtype=np.float64)
                xtr, xte = scaler_fit(views[view_id].loc[train_mask], views[view_id].loc[~train_mask])
                xall = np.vstack([xtr, xte])
                for n_clusters in CLUSTERS:
                    km = KMeans(n_clusters=n_clusters, n_init=12, random_state=stable_seed("cluster", target, split_name, view_id, n_clusters))
                    labels = km.fit_predict(xall)
                    tr_lab = labels[: len(xtr)]
                    te_lab = labels[len(xtr) :]
                    prior: dict[int, float] = {}
                    counts: dict[int, int] = {}
                    for lab in range(n_clusters):
                        mask = tr_lab == lab
                        counts[lab] = int(mask.sum())
                        prior[lab] = float(np.mean(teacher[mask])) if counts[lab] else float(np.mean(teacher))
                    local = np.asarray([prior[int(lab)] for lab in te_lab], dtype=np.float64)
                    score_store[(target, view_id, split_name, n_clusters)] = local
                    rows.append(
                        {
                            "target": target,
                            "view_id": view_id,
                            "split": split_name,
                            "method": f"kmeans{n_clusters}_train_residual",
                            "min_train_cluster_count": int(min(counts.values())),
                            "max_train_cluster_count": int(max(counts.values())),
                            "std_score": float(np.std(local)),
                        }
                    )
    return pd.DataFrame(rows), score_store


def collect_alignment_rows(
    gate: pd.DataFrame,
    movement: pd.DataFrame,
    local_summary: pd.DataFrame,
    pred_store: dict[tuple[str, str, str], dict[str, Any]],
    knn_store: dict[tuple[str, str, str, int], np.ndarray],
    cluster_store: dict[tuple[str, str, str, int], np.ndarray],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[dict[str, Any]] = []
    null_rows: list[dict[str, Any]] = []

    target_gate_col = {"Q2": "q2_gate_pred", "S1": "s1_gate_pred"}
    target_delta_col = {"Q2": "q2_logit_delta_e368_vs_e365", "S1": "s1_logit_delta_e368_vs_e365"}
    target_absdelta_col = {"Q2": "q2_abs_logit_delta", "S1": "s1_abs_logit_delta"}

    def add_metric(
        target: str,
        view_id: str,
        split_name: str,
        method: str,
        score: np.ndarray,
        extra: dict[str, Any] | None = None,
    ) -> None:
        score = np.asarray(score, dtype=np.float64)
        gate_vec = gate[target_gate_col[target]].to_numpy(dtype=np.float64)
        signed_delta = movement[target_delta_col[target]].to_numpy(dtype=np.float64)
        abs_delta = movement[target_absdelta_col[target]].to_numpy(dtype=np.float64)
        rec = {
            "target": target,
            "view_id": view_id,
            "split": split_name,
            "method": method,
            "score_std": float(np.std(score)),
            "gate_spearman": safe_spearman(score, gate_vec),
            "abs_delta_spearman": safe_spearman(score, abs_delta),
            "signed_delta_spearman": safe_spearman(score, signed_delta),
            "gate_top20_lift": tail_lift(score, gate_vec),
            "abs_delta_top20_lift": tail_lift(score, abs_delta),
        }
        if extra:
            # Keep the alignment method label; the local residual table also
            # has target/view/split/method columns that are only provenance.
            rec.update({k: v for k, v in extra.items() if k not in rec})

        rng = np.random.default_rng(stable_seed("align-null", target, view_id, split_name, method))
        null_gate = []
        null_abs = []
        null_signed = []
        for rep in range(NULL_REPS):
            perm_gate = gate_vec[rng.permutation(len(gate_vec))]
            perm_abs = abs_delta[rng.permutation(len(abs_delta))]
            perm_signed = signed_delta[rng.permutation(len(signed_delta))]
            ng = safe_spearman(score, perm_gate)
            na = safe_spearman(score, perm_abs)
            ns = safe_spearman(score, perm_signed)
            null_gate.append(ng)
            null_abs.append(na)
            null_signed.append(ns)
            null_rows.append(
                {
                    "target": target,
                    "view_id": view_id,
                    "split": split_name,
                    "method": method,
                    "rep": rep,
                    "gate_spearman_null": ng,
                    "abs_delta_spearman_null": na,
                    "signed_delta_spearman_null": ns,
                }
            )
        rec["gate_null_abs_p95"] = null_p95(null_gate)
        rec["abs_delta_null_abs_p95"] = null_p95(null_abs)
        rec["signed_delta_null_abs_p95"] = null_p95(null_signed)
        rec["gate_support"] = support_from_null(rec["gate_spearman"], rec["gate_null_abs_p95"])
        rec["abs_delta_support"] = support_from_null(rec["abs_delta_spearman"], rec["abs_delta_null_abs_p95"])
        rec["signed_delta_support"] = support_from_null(rec["signed_delta_spearman"], rec["signed_delta_null_abs_p95"])
        rec["any_transfer_support"] = bool(rec["gate_support"] or rec["abs_delta_support"] or rec["signed_delta_support"])
        rows.append(rec)

    local_lookup = {
        (str(r.target), str(r.view_id), str(r.split)): r._asdict()
        for r in local_summary.itertuples(index=False)
    }
    for (target, view_id, split_name), pack in pred_store.items():
        extra = local_lookup.get((target, view_id, split_name), {})
        add_metric(target, view_id, split_name, "masked_residual_student_test", pack["test_score"], extra)
    for (target, view_id, split_name, k), score in knn_store.items():
        add_metric(target, view_id, split_name, f"knn{k}_train_residual", score)
    for (target, view_id, split_name, n_clusters), score in cluster_store.items():
        add_metric(target, view_id, split_name, f"kmeans{n_clusters}_train_residual", score)

    out = pd.DataFrame(rows)
    nulls = pd.DataFrame(null_rows)
    out = out.sort_values(
        ["target", "any_transfer_support", "gate_support", "abs_delta_support", "gate_spearman"],
        ascending=[True, False, False, False, False],
    ).reset_index(drop=True)
    return out, nulls


def movement_audit(test: pd.DataFrame, gate: pd.DataFrame) -> pd.DataFrame:
    e365_path, e368_path = load_selected_paths()
    sample = test[KEY].sort_values(KEY).reset_index(drop=True)
    e365 = load_sub_frame(e365_path, sample)
    e368 = load_sub_frame(e368_path, sample)
    e247 = load_sub_frame(E247, sample)
    e323 = load_sub_frame(E323, sample)
    l365 = logit(e365[TARGETS].to_numpy(dtype=np.float64))
    l368 = logit(e368[TARGETS].to_numpy(dtype=np.float64))
    l247 = logit(e247[TARGETS].to_numpy(dtype=np.float64))
    l323 = logit(e323[TARGETS].to_numpy(dtype=np.float64))
    move = l368 - l365
    bad365 = l323 - l365
    bad247 = l323 - l247
    denom365 = float(np.linalg.norm(move) * np.linalg.norm(bad365) + EPS)
    denom247 = float(np.linalg.norm(move) * np.linalg.norm(bad247) + EPS)

    rows = []
    flat = move.reshape(-1)
    rows.append(
        {
            "scope": "all_targets",
            "changed_rows": int(np.any(np.abs(move) > 1.0e-12, axis=1).sum()),
            "changed_cells": int((np.abs(move) > 1.0e-12).sum()),
            "mean_abs_logit_delta": float(np.mean(np.abs(move))),
            "max_abs_logit_delta": float(np.max(np.abs(move))),
            "signed_sum": float(np.sum(flat)),
            "cos_e323_bad_vs_e365": float(np.sum(move * bad365) / denom365),
            "cos_e323_bad_vs_e247": float(np.sum(move * bad247) / denom247),
        }
    )
    out = gate[KEY].copy()
    for target in TARGETS:
        idx = TARGETS.index(target)
        delta = move[:, idx]
        out[f"{target.lower()}_logit_delta_e368_vs_e365"] = delta
        out[f"{target.lower()}_abs_logit_delta"] = np.abs(delta)
        rows.append(
            {
                "scope": target,
                "changed_rows": int((np.abs(delta) > 1.0e-12).sum()),
                "changed_cells": int((np.abs(delta) > 1.0e-12).sum()),
                "mean_abs_logit_delta": float(np.mean(np.abs(delta))),
                "max_abs_logit_delta": float(np.max(np.abs(delta))),
                "signed_sum": float(np.sum(delta)),
                "cos_e323_bad_vs_e365": float(
                    np.sum(delta * bad365[:, idx]) / (np.linalg.norm(delta) * np.linalg.norm(bad365[:, idx]) + EPS)
                ),
                "cos_e323_bad_vs_e247": float(
                    np.sum(delta * bad247[:, idx]) / (np.linalg.norm(delta) * np.linalg.norm(bad247[:, idx]) + EPS)
                ),
                "gate_spearman": safe_spearman(delta, gate[f"{target.lower()}_gate_pred"]) if target in TARGET_FOCUS else np.nan,
                "abs_gate_spearman": safe_spearman(np.abs(delta), gate[f"{target.lower()}_gate_pred"]) if target in TARGET_FOCUS else np.nan,
            }
        )
    pd.DataFrame(rows).to_csv(MOVEMENT_OUT, index=False)
    return out


def decide(summary: pd.DataFrame, movement_summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    all_bad_cos = float(movement_summary.loc[movement_summary["scope"].eq("all_targets"), "cos_e323_bad_vs_e365"].iloc[0])
    q2_bad_cos = float(movement_summary.loc[movement_summary["scope"].eq("Q2"), "cos_e323_bad_vs_e365"].iloc[0])
    q2_bad_cos_e247 = float(movement_summary.loc[movement_summary["scope"].eq("Q2"), "cos_e323_bad_vs_e247"].iloc[0])
    s1_bad_cos = float(movement_summary.loc[movement_summary["scope"].eq("S1"), "cos_e323_bad_vs_e365"].iloc[0])
    target_risk_note = (
        "Q2-only movement is E323-like versus E365, but it is not E323-like versus E247 and the all-target movement is near orthogonal."
        if q2_bad_cos > 0.30 and q2_bad_cos_e247 <= 0.03 and all_bad_cos <= 0.03
        else "No focused Q2/S1 E323-axis warning."
    )
    for target in TARGET_FOCUS:
        target_rows = summary[summary["target"].eq(target)].copy()
        strong = target_rows[target_rows["any_transfer_support"]].copy()
        student = strong[strong["method"].eq("masked_residual_student_test")]
        knn = strong[strong["method"].str.startswith("knn")]
        cluster = strong[strong["method"].str.startswith("kmeans")]
        best_gate = float(target_rows["gate_spearman"].abs().max()) if len(target_rows) else 0.0
        best_abs = float(target_rows["abs_delta_spearman"].abs().max()) if len(target_rows) else 0.0
        rows.append(
            {
                "target": target,
                "supporting_rows": int(len(strong)),
                "student_support_rows": int(len(student)),
                "knn_support_rows": int(len(knn)),
                "cluster_support_rows": int(len(cluster)),
                "best_abs_gate_spearman": best_gate,
                "best_abs_delta_spearman": best_abs,
                "target_decision": (
                    "strong_public_free_transfer"
                    if len(student) >= 1 and (len(knn) + len(cluster)) >= 1
                    else "weak_public_free_transfer"
                    if len(strong) >= 2
                    else "no_public_free_transfer"
                ),
            }
        )
    q2 = next(r for r in rows if r["target"] == "Q2")
    s1 = next(r for r in rows if r["target"] == "S1")
    if q2["target_decision"] == "strong_public_free_transfer" and s1["target_decision"] != "no_public_free_transfer" and all_bad_cos <= 0.03:
        global_decision = "support_e368_hidden_lifestyle_state"
        reason = "Q2 has independent public-free lifestyle transfer and S1 is not dead; E368 movement is not E323-like."
    elif q2["target_decision"] != "no_public_free_transfer" and all_bad_cos <= 0.03:
        global_decision = "weak_support_keep_e368_candidate"
        reason = "Train-side lifestyle state partially explains E368 movement, but support is not broad enough to promote a new derived submission."
    elif all_bad_cos > 0.03:
        global_decision = "red_flag_e368_bad_axis"
        reason = "E368 movement aligns too much with the known E323 bad axis under this audit."
    else:
        global_decision = "no_transfer_support_keep_as_public_sensor_only"
        reason = "E368 may still be a public-sensor discovery, but train-side hidden lifestyle state did not explain it."

    out = pd.DataFrame(rows)
    out["global_decision"] = global_decision
    out["reason"] = reason
    out["all_target_cos_e323_bad_vs_e365"] = all_bad_cos
    out["q2_cos_e323_bad_vs_e365"] = q2_bad_cos
    out["q2_cos_e323_bad_vs_e247"] = q2_bad_cos_e247
    out["s1_cos_e323_bad_vs_e365"] = s1_bad_cos
    out["target_risk_note"] = target_risk_note
    out.to_csv(DECISION_OUT, index=False)
    return out


def write_report(
    local: pd.DataFrame,
    knn: pd.DataFrame,
    cluster: pd.DataFrame,
    summary: pd.DataFrame,
    movement_summary: pd.DataFrame,
    decision: pd.DataFrame,
) -> None:
    top = summary.sort_values(
        ["any_transfer_support", "gate_support", "abs_delta_support", "target", "gate_spearman"],
        ascending=[False, False, False, True, False],
    )
    lines = [
        "# E369 Q2/S1 Lifestyle-Transfer Audit",
        "",
        "## Question",
        "",
        "Does the E368 Q2/S1 cell action correspond to a hidden lifestyle state that can be learned from train labels and context views, without using public LB as the teacher?",
        "",
        "## Construction",
        "",
        "- Base: subject/calendar model for Q2 and S1.",
        "- Teacher: train residual after the base model.",
        "- Context: family, JEPA residual, social/cash/raw story bundles, and combined lifestyle views.",
        "- Tests: masked residual student, kNN residual analogy, and cluster residual analogy.",
        "- Null: each alignment is compared against 160 permuted test-gate/movement controls.",
        "",
        "## Decision",
        "",
        md_table(decision, n=10, floatfmt=".9f"),
        "",
        "## E368 Movement Audit",
        "",
        md_table(movement_summary, n=12, floatfmt=".9f"),
        "",
        "Movement-risk nuance: all-target E368-vs-E365 movement is almost orthogonal to the E323 bad axis, but the Q2-only slice has a high E323 cosine versus E365. Because the same Q2 slice is not E323-like versus E247 and the move is very small, this is a monitored amplitude risk rather than a veto.",
        "",
        "## Top Transfer Alignments",
        "",
        md_table(top, n=40, floatfmt=".9f"),
        "",
        "## Local Residual Students",
        "",
        md_table(local.sort_values(["target", "logloss_delta", "teacher_spearman"]), n=30, floatfmt=".9f"),
        "",
        "## kNN Residual Probes",
        "",
        md_table(knn.sort_values(["target", "std_score"], ascending=[True, False]), n=30, floatfmt=".9f"),
        "",
        "## Cluster Residual Probes",
        "",
        md_table(cluster.sort_values(["target", "std_score"], ascending=[True, False]), n=30, floatfmt=".9f"),
        "",
        "## Interpretation",
        "",
    ]
    global_decision = str(decision["global_decision"].iloc[0])
    if global_decision == "support_e368_hidden_lifestyle_state":
        lines.append(
            "E368 is no longer only a public-sensor artifact: at least part of its Q2/S1 movement is recoverable from train-side lifestyle residual structure. Keep E368 as the current information-rich submission candidate."
        )
    elif global_decision == "weak_support_keep_e368_candidate":
        lines.append(
            "The hidden lifestyle-state story is partially alive, mostly as a Q2 transfer signal. This is not enough to create a new E369 submission, but it reduces the risk that E368 is pure public-LB geometry."
        )
    elif global_decision == "red_flag_e368_bad_axis":
        lines.append(
            "The public-free transfer signal is contaminated by E323-like movement. Hold E368 unless a later audit neutralizes that axis."
        )
    else:
        lines.append(
            "The train-side lifestyle-state hypothesis did not explain E368. Treat E368 as a public-sensor observation only, not as a validated hidden lifestyle latent."
        )
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- `{SUMMARY_OUT.name}`",
            f"- `{LOCAL_OUT.name}`",
            f"- `{KNN_OUT.name}`",
            f"- `{CLUSTER_OUT.name}`",
            f"- `{NULL_OUT.name}`",
            f"- `{MOVEMENT_OUT.name}`",
            f"- `{DECISION_OUT.name}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    frames = load_frames()
    state = frames["state"].copy()
    views = build_views(frames)
    train_mask = state["split"].eq("train").to_numpy()
    train = state.loc[train_mask].reset_index(drop=True)
    test = state.loc[~train_mask].sort_values(KEY).reset_index(drop=True)

    for name, view in views.items():
        require_aligned(state, normalize_dates(pd.concat([state[KEY], view], axis=1)), f"view_{name}")

    gate = load_e368_gate(test[KEY])
    movement = movement_audit(test, gate)
    movement_summary = pd.read_csv(MOVEMENT_OUT)

    local, pred_store = fit_base_context_residuals(train, test, views, train_mask)
    knn, knn_store = build_knn_scores(train, views, train_mask, pred_store)
    cluster, cluster_store = build_cluster_scores(train, views, train_mask, pred_store)
    summary, nulls = collect_alignment_rows(gate, movement, local, pred_store, knn_store, cluster_store)
    decision = decide(summary, movement_summary)

    local.to_csv(LOCAL_OUT, index=False)
    knn.to_csv(KNN_OUT, index=False)
    cluster.to_csv(CLUSTER_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    nulls.to_csv(NULL_OUT, index=False)
    write_report(local, knn, cluster, summary, movement_summary, decision)

    print(f"decision={decision['global_decision'].iloc[0]}")
    print(f"reason={decision['reason'].iloc[0]}")
    print(f"support rows by target={decision[['target','supporting_rows','target_decision']].to_dict(orient='records')}")
    print(f"top alignments={summary.head(8)[['target','view_id','split','method','gate_spearman','abs_delta_spearman','any_transfer_support']].to_dict(orient='records')}")
    print(f"report={rel(REPORT_OUT)}")


if __name__ == "__main__":
    main()
