#!/usr/bin/env python3
"""H003: HS-JEPA prototype.

Human-State Joint Embedding Predictive Architecture, prototype version.

The important design choice is that the JEPA target is not a raw feature block
or a final label probability.  The target is a human-state representation:
commute pressure, bedtime arousal, routine fragmentation, cash-flow stress,
recovery, measurement confidence, and related episode states.

This script builds a small, reproducible prototype:

1. Build explicit human episode states from existing story features.
2. Predict those states from several context views under grouped OOF splits.
3. Compress the context-predicted states into an HS-JEPA latent.
4. Diagnose geometry, positive-pair behavior, label-block translation, and
   public-sensor alignment.
5. Materialize only tiny E247-anchored candidates and mark them as diagnostic
   unless public-free selector stress says otherwise.
"""

from __future__ import annotations

import hashlib
import sys
import warnings
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import kurtosis, skew
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import log_loss, r2_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
HITL = ROOT / "hitl"
H003 = HITL / "h003_hs_jepa_prototype"
H003.mkdir(parents=True, exist_ok=True)

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

from e288_lifestyle_bundle_jepa_audit import (  # noqa: E402
    KEYS,
    TARGETS,
    base_label_matrix,
    build_context_views,
    clip_prob,
    folds_for,
    groups_for,
    label_cv_loss,
    load_frames,
    md_table,
    shuffled_matrix,
    stable_seed,
)
from e295_episode_state_jepa_audit import build_episode_matrix  # noqa: E402
from e328_ownlatent_lifestyle_state_experiment import load_sub_frame, safe_id, sigmoid  # noqa: E402
from public_anchor_bottleneck_decomposition import load_sub as load_anchor_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402
from e272_public_free_candidate_audit import CURRENT, build_features, evaluate_models, score_candidates  # noqa: E402


RNG_SEED = 20260601 + 3
EPS = 1.0e-12
N_NULL_REPS = 6
LATENT_DIMS = 8
CLUSTERS = 8

E247 = OUT / CURRENT
E256 = OUT / "submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv"
E323 = OUT / "submission_e323_5508f966_uploadsafe.csv"
E368 = OUT / "submission_e368_q2s1rowmask_selected_e368_q2_damp_s1_recover_amp1_06_be814361_uploadsafe.csv"

DEFINITION_OUT = H003 / "h003_episode_definition.csv"
RECON_OUT = H003 / "h003_context_target_reconstruction.csv"
FEATURES_OUT = H003 / "h003_hs_jepa_features.parquet"
GEOMETRY_OUT = H003 / "h003_latent_geometry.csv"
PAIR_OUT = H003 / "h003_positive_pair_diagnostics.csv"
TARGET_OUT = H003 / "h003_target_translation_stress.csv"
NULL_OUT = H003 / "h003_target_translation_nulls.csv"
ROUTE_OUT = H003 / "h003_episode_target_route_stress.csv"
ROUTE_NULL_OUT = H003 / "h003_episode_target_route_nulls.csv"
BOUNDARY_OUT = H003 / "h003_public_sensor_alignment.csv"
CLUSTER_OUT = H003 / "h003_cluster_story_read.csv"
CANDIDATE_OUT = H003 / "h003_candidates.csv"
SCORE_OUT = H003 / "h003_selector_scores.csv"
ANATOMY_OUT = H003 / "h003_candidate_anatomy.csv"
SELECTION_OUT = H003 / "h003_selection.csv"
REPORT_OUT = H003 / "h003_report.md"


def rel(path: Path | None) -> str:
    if path is None:
        return "none"
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def short_hash(frame: pd.DataFrame) -> str:
    arr = np.asarray(frame[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def rank01(values: np.ndarray | pd.Series) -> np.ndarray:
    s = pd.Series(values, dtype="float64").replace([np.inf, -np.inf], np.nan).fillna(0.0)
    if s.nunique(dropna=False) <= 1:
        return np.zeros(len(s), dtype=np.float64)
    return s.rank(method="average", pct=True).to_numpy(dtype=np.float64)


def cohen_d(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    a = a[np.isfinite(a)]
    b = b[np.isfinite(b)]
    if len(a) < 2 or len(b) < 2:
        return 0.0
    pooled = np.sqrt(((len(a) - 1) * np.var(a, ddof=1) + (len(b) - 1) * np.var(b, ddof=1)) / max(len(a) + len(b) - 2, 1))
    if not np.isfinite(pooled) or pooled < EPS:
        return 0.0
    return float((np.mean(a) - np.mean(b)) / pooled)


def cos(a: np.ndarray, b: np.ndarray) -> float:
    aa = np.asarray(a, dtype=np.float64).reshape(-1)
    bb = np.asarray(b, dtype=np.float64).reshape(-1)
    return float(np.sum(aa * bb) / (np.linalg.norm(aa) * np.linalg.norm(bb) + EPS))


def fit_predict_test(x_train: pd.DataFrame, y_train: pd.DataFrame, x_test: pd.DataFrame) -> np.ndarray:
    model = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), Ridge(alpha=10.0))
    model.fit(x_train, y_train)
    return np.asarray(model.predict(x_test), dtype=np.float64)


def oof_predict_state(x_train: pd.DataFrame, y_train: pd.DataFrame, groups: pd.Series) -> np.ndarray:
    pred = np.zeros(y_train.shape, dtype=np.float64)
    for tr_idx, va_idx in folds_for(groups):
        model = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), Ridge(alpha=10.0))
        model.fit(x_train.iloc[tr_idx], y_train.iloc[tr_idx])
        pred[va_idx] = model.predict(x_train.iloc[va_idx])
    return pred


def build_context_target_predictions(
    base: pd.DataFrame,
    raw: pd.DataFrame,
    story_state: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    contexts = build_context_views(base, raw)
    train_mask = base["split"].eq("train").to_numpy()
    train_df = base.loc[train_mask].reset_index(drop=True)
    y_train = story_state.loc[train_mask].reset_index(drop=True)
    rows: list[dict[str, Any]] = []
    pred_parts: list[pd.DataFrame] = []

    for view_id, ctx in contexts.items():
        x_train = ctx.loc[train_mask].reset_index(drop=True)
        x_test = ctx.loc[~train_mask].reset_index(drop=True)
        for split_name in ["subject5", "dateblock5"]:
            groups = groups_for(train_df, split_name).reset_index(drop=True)
            pred_train = oof_predict_state(x_train, y_train, groups)
            pred_test = fit_predict_test(x_train, y_train, x_test)
            pred_all = np.zeros((len(base), y_train.shape[1]), dtype=np.float64)
            pred_all[train_mask] = pred_train
            pred_all[~train_mask] = pred_test
            pred_df = pd.DataFrame(pred_all, columns=[f"hsctx_{view_id}_{split_name}_{c}" for c in y_train.columns])
            pred_parts.append(pred_df)
            r2_vals = r2_score(y_train.to_numpy(dtype=np.float64), pred_train, multioutput="raw_values")
            for i, episode in enumerate(y_train.columns):
                actual = y_train[episode].to_numpy(dtype=np.float64)
                pred = pred_train[:, i]
                corr = float(np.corrcoef(actual, pred)[0, 1]) if np.std(actual) > EPS and np.std(pred) > EPS else 0.0
                rows.append(
                    {
                        "view_id": view_id,
                        "split": split_name,
                        "episode": episode,
                        "context_cols": int(ctx.shape[1]),
                        "r2": float(r2_vals[i]),
                        "corr": corr,
                        "train_pred_mean": float(np.mean(pred)),
                        "test_pred_mean": float(np.mean(pred_test[:, i])),
                        "train_test_pred_z_gap": float((np.mean(pred_test[:, i]) - np.mean(pred)) / (np.std(pred) + EPS)),
                    }
                )

    pred_bundle = pd.concat(pred_parts, axis=1).replace([np.inf, -np.inf], 0.0).fillna(0.0)
    recon = pd.DataFrame(rows).sort_values(["r2", "corr"], ascending=False).reset_index(drop=True)
    return pred_bundle, recon, y_train


def make_hs_latent(base: pd.DataFrame, pred_bundle: pd.DataFrame, story_state: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    train_mask = base["split"].eq("train").to_numpy()
    scaler = make_pipeline(SimpleImputer(strategy="median"), StandardScaler())
    x_train = scaler.fit_transform(pred_bundle.iloc[train_mask])
    x_all = scaler.transform(pred_bundle)
    n_comp = min(LATENT_DIMS, x_train.shape[1], int(train_mask.sum()) - 1)
    pca = PCA(n_components=n_comp, random_state=RNG_SEED)
    train_lat = pca.fit_transform(x_train)
    all_lat = pca.transform(x_all)

    km = KMeans(n_clusters=CLUSTERS, random_state=RNG_SEED, n_init=40)
    km.fit(train_lat[:, : min(6, n_comp)])
    clusters = km.predict(all_lat[:, : min(6, n_comp)])
    dist = km.transform(all_lat[:, : min(6, n_comp)])

    features = base[KEYS + ["split", "dateblock_group", "subject_order", "weekday", "is_weekend", *TARGETS]].copy()
    for i in range(n_comp):
        features[f"hsjepa_pc{i+1}"] = all_lat[:, i]
    features["hsjepa_energy"] = np.sqrt(np.mean(all_lat[:, : min(6, n_comp)] ** 2, axis=1))
    center = all_lat[train_mask, : min(6, n_comp)].mean(axis=0, keepdims=True)
    features["hsjepa_center_distance"] = np.sqrt(np.mean((all_lat[:, : min(6, n_comp)] - center) ** 2, axis=1))
    features["hsjepa_cluster"] = clusters
    features["hsjepa_cluster_distance"] = np.min(dist, axis=1)
    for k in range(CLUSTERS):
        features[f"hsjepa_k{k}"] = (clusters == k).astype(float)

    # Semantic residual energies: is a human-state target predictable from the
    # other views, or is this row a surprising human episode?
    episode_cols = story_state.columns.tolist()
    pred_episode = {}
    for episode in episode_cols:
        cols = [c for c in pred_bundle.columns if c.endswith("_" + episode)]
        pred_episode[episode] = pred_bundle[cols].mean(axis=1)
        features[f"hsjepa_pred_{episode}"] = pred_episode[episode]
        features[f"hsjepa_resid_{episode}"] = story_state[episode].to_numpy(dtype=np.float64) - pred_episode[episode].to_numpy(dtype=np.float64)
    resid_mat = np.column_stack([features[f"hsjepa_resid_{e}"].to_numpy(dtype=np.float64) for e in episode_cols])
    features["hsjepa_surprise"] = np.sqrt(np.mean(resid_mat**2, axis=1))

    svals = np.linalg.svd(train_lat - train_lat.mean(axis=0, keepdims=True), compute_uv=False)
    participation = float((np.sum(svals**2) ** 2) / (np.sum(svals**4) + EPS))
    geometry = pd.DataFrame(
        [
            {
                "latent": "hsjepa",
                "dims": int(n_comp),
                "explained_var_sum": float(np.sum(pca.explained_variance_ratio_)),
                "participation_ratio": participation,
                "anisotropy": float(np.max(svals) / max(np.min(svals), EPS)),
                "train_energy_mean": float(features.loc[train_mask, "hsjepa_energy"].mean()),
                "test_energy_mean": float(features.loc[~train_mask, "hsjepa_energy"].mean()),
                "train_surprise_mean": float(features.loc[train_mask, "hsjepa_surprise"].mean()),
                "test_surprise_mean": float(features.loc[~train_mask, "hsjepa_surprise"].mean()),
                **random_projection_health(train_lat),
            }
        ]
    )
    return features, geometry


def random_projection_health(latent_train: np.ndarray, n_proj: int = 256) -> dict[str, float]:
    rng = np.random.default_rng(RNG_SEED + 100)
    z = np.asarray(latent_train, dtype=np.float64)
    z = (z - z.mean(axis=0, keepdims=True)) / (z.std(axis=0, keepdims=True) + EPS)
    dirs = rng.normal(size=(z.shape[1], n_proj))
    dirs /= np.linalg.norm(dirs, axis=0, keepdims=True) + EPS
    proj = z @ dirs
    proj = (proj - proj.mean(axis=0, keepdims=True)) / (proj.std(axis=0, keepdims=True) + EPS)
    sk = skew(proj, axis=0, bias=False, nan_policy="omit")
    ku = kurtosis(proj, axis=0, fisher=True, bias=False, nan_policy="omit")
    return {
        "slice_abs_skew_mean": float(np.nanmean(np.abs(sk))),
        "slice_abs_excess_kurt_mean": float(np.nanmean(np.abs(ku))),
        "slice_gaussian_penalty": float(np.nanmean(np.abs(sk)) + 0.5 * np.nanmean(np.abs(ku))),
    }


def positive_pair_diagnostics(features: pd.DataFrame) -> pd.DataFrame:
    latent_cols = [c for c in features.columns if c.startswith("hsjepa_pc")]
    rows: list[dict[str, Any]] = []
    for split_value in ["train", "test", "all"]:
        df = features if split_value == "all" else features[features["split"].eq(split_value)]
        pair_a: list[np.ndarray] = []
        pair_b: list[np.ndarray] = []
        diffs: list[np.ndarray] = []
        for _, part in df.sort_values(KEYS).groupby("subject_id"):
            arr = part[latent_cols].to_numpy(dtype=np.float64)
            if len(arr) < 2:
                continue
            pair_a.append(arr[:-1])
            pair_b.append(arr[1:])
            diffs.append(arr[1:] - arr[:-1])
        if not pair_a:
            continue
        a = np.vstack(pair_a)
        b = np.vstack(pair_b)
        d = np.vstack(diffs)
        coord_corr = []
        for j in range(a.shape[1]):
            coord_corr.append(np.corrcoef(a[:, j], b[:, j])[0, 1] if np.std(a[:, j]) > EPS and np.std(b[:, j]) > EPS else 0.0)
        dz = (d - d.mean(axis=0, keepdims=True)) / (d.std(axis=0, keepdims=True) + EPS)
        rows.append(
            {
                "split": split_value,
                "positive_pair_count": int(len(a)),
                "autocorr_mean": float(np.mean(coord_corr)),
                "autocorr_min": float(np.min(coord_corr)),
                "autocorr_max": float(np.max(coord_corr)),
                "increment_abs_skew_mean": float(np.mean(np.abs(skew(dz, axis=0, bias=False, nan_policy="omit")))),
                "increment_abs_excess_kurt_mean": float(np.mean(np.abs(kurtosis(dz, axis=0, fisher=True, bias=False, nan_policy="omit")))),
                "increment_l2_mean": float(np.mean(np.sqrt(np.sum(d**2, axis=1)))),
            }
        )
    return pd.DataFrame(rows)


def shuffled_additive(add_x: pd.DataFrame, mode: str, train_df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    if mode == "row":
        return add_x.iloc[rng.permutation(len(add_x))].reset_index(drop=True)
    groups = groups_for(train_df, "subject5" if mode == "subject" else "dateblock5").reset_index(drop=True)
    shuffled = shuffled_matrix(add_x.to_numpy(dtype=np.float64), mode, groups, rng)
    return pd.DataFrame(shuffled, columns=add_x.columns)


def target_translation_stress(features: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    train = features[features["split"].eq("train")].reset_index(drop=True)
    base_x = base_label_matrix(train)
    latent_cols = [
        c
        for c in train.columns
        if c.startswith("hsjepa_pc")
        or c in {"hsjepa_energy", "hsjepa_center_distance", "hsjepa_cluster_distance", "hsjepa_surprise"}
        or c.startswith("hsjepa_k")
    ]
    latent_x = train[latent_cols].astype(float).reset_index(drop=True)
    rows: list[dict[str, Any]] = []
    null_rows: list[dict[str, Any]] = []
    rng = np.random.default_rng(RNG_SEED + 200)
    for split_name in ["subject5", "dateblock5"]:
        groups = groups_for(train, split_name).reset_index(drop=True)
        x = pd.concat([base_x.reset_index(drop=True), latent_x.reset_index(drop=True)], axis=1)
        for target in TARGETS:
            y = train[target].to_numpy(dtype=int)
            base_loss = label_cv_loss(base_x, y, groups)
            hs_loss = label_cv_loss(x, y, groups)
            delta = hs_loss - base_loss
            null_vals: list[float] = []
            mode_dom: dict[str, float] = {}
            for mode in ["row", "subject", "dateblock"]:
                vals = []
                for rep in range(N_NULL_REPS):
                    nx_lat = shuffled_additive(latent_x, mode, train, rng)
                    nx = pd.concat([base_x.reset_index(drop=True), nx_lat], axis=1)
                    ndelta = label_cv_loss(nx, y, groups) - base_loss
                    vals.append(ndelta)
                    null_rows.append({"split": split_name, "target": target, "mode": mode, "rep": rep, "null_delta": ndelta})
                mode_dom[mode] = float(np.mean(delta < np.asarray(vals, dtype=np.float64)))
                null_vals.extend(vals)
            null_arr = np.asarray(null_vals, dtype=np.float64)
            rows.append(
                {
                    "split": split_name,
                    "target": target,
                    "base_loss": base_loss,
                    "hsjepa_loss": hs_loss,
                    "delta_logloss": delta,
                    "null_best": float(np.min(null_arr)),
                    "null_median": float(np.median(null_arr)),
                    "null_q20": float(np.quantile(null_arr, 0.20)),
                    "dominance": float(np.mean(delta < null_arr)),
                    "row_dominance": mode_dom["row"],
                    "subject_dominance": mode_dom["subject"],
                    "dateblock_dominance": mode_dom["dateblock"],
                    "target_gate": bool(delta < -0.0010 and np.mean(delta < null_arr) >= 0.80 and min(mode_dom.values()) >= 0.50),
                }
            )
    return pd.DataFrame(rows).sort_values(["target_gate", "delta_logloss"], ascending=[False, True]), pd.DataFrame(null_rows)


def episode_target_route_stress(features: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Test the HS-JEPA routing claim one episode and one target at a time.

    The full HS latent can be too broad.  HS-JEPA's paper-worthy version should
    allow sparse semantic routes: e.g. bedtime arousal may translate to S1/S3,
    while cash-flow stress may translate elsewhere.  This stress test is the
    smallest falsifiable version of that routing claim.
    """

    train = features[features["split"].eq("train")].reset_index(drop=True)
    episode_cols = [c for c in train.columns if c.startswith("hsjepa_pred_")]
    base_x = base_label_matrix(train)
    rows: list[dict[str, Any]] = []
    null_rows: list[dict[str, Any]] = []
    rng = np.random.default_rng(RNG_SEED + 300)

    for split_name in ["subject5", "dateblock5"]:
        groups = groups_for(train, split_name).reset_index(drop=True)
        baseline = {target: label_cv_loss(base_x, train[target].to_numpy(dtype=int), groups) for target in TARGETS}
        for episode_col in episode_cols:
            episode = episode_col.replace("hsjepa_pred_", "")
            state = train[[episode_col]].astype(float).reset_index(drop=True)
            for target in TARGETS:
                y = train[target].to_numpy(dtype=int)
                x = pd.concat([base_x.reset_index(drop=True), state], axis=1)
                actual_loss = label_cv_loss(x, y, groups)
                delta = actual_loss - baseline[target]
                null_vals: list[float] = []
                mode_dom: dict[str, float] = {}
                for mode in ["row", "subject", "dateblock"]:
                    vals = []
                    for rep in range(max(3, N_NULL_REPS // 2)):
                        nx_state = shuffled_additive(state, mode, train, rng)
                        nx = pd.concat([base_x.reset_index(drop=True), nx_state], axis=1)
                        ndelta = label_cv_loss(nx, y, groups) - baseline[target]
                        vals.append(ndelta)
                        null_rows.append(
                            {
                                "split": split_name,
                                "episode": episode,
                                "target": target,
                                "mode": mode,
                                "rep": rep,
                                "null_delta": ndelta,
                            }
                        )
                    mode_dom[mode] = float(np.mean(delta < np.asarray(vals, dtype=np.float64)))
                    null_vals.extend(vals)
                null_arr = np.asarray(null_vals, dtype=np.float64)
                rows.append(
                    {
                        "split": split_name,
                        "episode": episode,
                        "target": target,
                        "base_loss": baseline[target],
                        "route_loss": actual_loss,
                        "delta_logloss": delta,
                        "null_best": float(np.min(null_arr)),
                        "null_median": float(np.median(null_arr)),
                        "dominance": float(np.mean(delta < null_arr)),
                        "row_dominance": mode_dom["row"],
                        "subject_dominance": mode_dom["subject"],
                        "dateblock_dominance": mode_dom["dateblock"],
                        "route_gate": bool(
                            delta < -0.0020
                            and np.mean(delta < null_arr) >= 0.82
                            and min(mode_dom.values()) >= 0.50
                        ),
                    }
                )
    return pd.DataFrame(rows).sort_values(["route_gate", "delta_logloss"], ascending=[False, True]), pd.DataFrame(null_rows)


def public_sensor_alignment(features: pd.DataFrame) -> pd.DataFrame:
    test = features[features["split"].eq("test")].sort_values(KEYS).reset_index(drop=True)
    sample = test[KEYS]
    e247 = load_sub_frame(E247, sample)[TARGETS].to_numpy(dtype=np.float64)
    e256 = load_sub_frame(E256, sample)[TARGETS].to_numpy(dtype=np.float64)
    e323 = load_sub_frame(E323, sample)[TARGETS].to_numpy(dtype=np.float64)
    e368 = load_sub_frame(E368, sample)[TARGETS].to_numpy(dtype=np.float64) if E368.exists() else e247.copy()
    l247 = logit(e247)
    l256 = logit(e256)
    l323 = logit(e323)
    l368 = logit(e368)
    e256_q3 = np.abs(l256[:, TARGETS.index("Q3")] - l247[:, TARGETS.index("Q3")])
    e323_l1 = np.sum(np.abs(l323 - l247), axis=1)
    e368_q2s1 = np.abs(l368[:, TARGETS.index("Q2")] - l247[:, TARGETS.index("Q2")]) + np.abs(l368[:, TARGETS.index("S1")] - l247[:, TARGETS.index("S1")])
    masks = {
        "e256_q3_top20": e256_q3 >= np.quantile(e256_q3, 0.80),
        "e323_bad_top20": e323_l1 >= np.quantile(e323_l1, 0.80),
        "e368_q2s1_top20": e368_q2s1 >= np.quantile(e368_q2s1, 0.80),
    }
    cols = [
        c
        for c in test.columns
        if c.startswith("hsjepa_pc")
        or c.startswith("hsjepa_k")
        or c in {"hsjepa_energy", "hsjepa_center_distance", "hsjepa_cluster_distance", "hsjepa_surprise"}
        or c.startswith("hsjepa_pred_")
        or c.startswith("hsjepa_resid_")
    ]
    rows: list[dict[str, Any]] = []
    for col in cols:
        vals = pd.to_numeric(test[col], errors="coerce").fillna(0.0).to_numpy(dtype=np.float64)
        rec: dict[str, Any] = {"feature": col}
        for name, mask in masks.items():
            rec[f"{name}_d"] = cohen_d(vals[mask], vals[~mask])
        rec["max_abs_sensor_d"] = max(abs(float(rec[f"{name}_d"])) for name in masks)
        rows.append(rec)
    return pd.DataFrame(rows).sort_values(["max_abs_sensor_d", "feature"], ascending=[False, True]).reset_index(drop=True)


def fit_label_translator(
    features: pd.DataFrame,
    selected_targets: list[str],
    route_stress: pd.DataFrame,
) -> tuple[pd.DataFrame, np.ndarray]:
    train = features[features["split"].eq("train")].reset_index(drop=True)
    test = features[features["split"].eq("test")].sort_values(KEYS).reset_index(drop=True)
    pred = np.full((len(test), len(TARGETS)), np.nan, dtype=np.float64)
    rows: list[dict[str, Any]] = []
    for target in selected_targets:
        idx = TARGETS.index(target)
        y = train[target].to_numpy(dtype=int)
        target_routes = route_stress[
            route_stress["target"].eq(target)
            & route_stress["route_gate"].astype(bool)
        ].sort_values(["delta_logloss", "dominance"], ascending=[True, False])
        if target_routes.empty:
            target_routes = route_stress[route_stress["target"].eq(target)].sort_values("delta_logloss").head(2)
        route_cols = [f"hsjepa_pred_{episode}" for episode in target_routes["episode"].astype(str).tolist()]
        route_cols = [c for c in dict.fromkeys(route_cols) if c in train.columns]
        core_cols = ["hsjepa_surprise", "hsjepa_center_distance"]
        use_cols = route_cols + [c for c in core_cols if c in train.columns]
        x_train = pd.concat([base_label_matrix(train).reset_index(drop=True), train[use_cols].astype(float).reset_index(drop=True)], axis=1)
        x_test = pd.concat([base_label_matrix(test).reset_index(drop=True), test[use_cols].astype(float).reset_index(drop=True)], axis=1)
        if len(np.unique(y)) < 2:
            pred[:, idx] = float(np.mean(y))
            continue
        model = make_pipeline(
            SimpleImputer(strategy="median"),
            StandardScaler(),
            LogisticRegression(C=0.18, max_iter=1600, solver="lbfgs"),
        )
        model.fit(x_train, y)
        pred[:, idx] = clip_prob(model.predict_proba(x_test)[:, 1])
        rows.append(
            {
                "target": target,
                "route_episodes": ",".join(target_routes["episode"].astype(str).head(4).tolist()),
                "train_rate": float(np.mean(y)),
                "test_pred_mean": float(np.nanmean(pred[:, idx])),
                "test_pred_std": float(np.nanstd(pred[:, idx])),
            }
        )
    return pd.DataFrame(rows), pred


def write_candidate(base: pd.DataFrame, logits: np.ndarray, candidate_id: str) -> Path:
    out = base[KEYS].copy()
    out[TARGETS] = clip_prob(sigmoid(logits))
    path = H003 / f"submission_h003_{safe_id(candidate_id, 80)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def materialize_candidates(features: pd.DataFrame, target_stress: pd.DataFrame, route_stress: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, list[Path]]:
    test = features[features["split"].eq("test")].sort_values(KEYS).reset_index(drop=True)
    base = load_sub_frame(E247, test[KEYS])
    base_prob = base[TARGETS].to_numpy(dtype=np.float64)
    base_logit = logit(base_prob)
    selected = (
        route_stress[route_stress["route_gate"].astype(bool)]
        .groupby("target")
        .agg(best_delta=("delta_logloss", "min"), best_dominance=("dominance", "max"), route_count=("route_gate", "sum"))
        .reset_index()
        .sort_values("best_delta")
    )
    selected_targets = selected["target"].astype(str).tolist()
    if not selected_targets:
        # Keep the prototype inspectable even when strict gates fail: use the
        # top two negative/least-bad targets as diagnostic translators only.
        selected_targets = target_stress.sort_values("delta_logloss")["target"].drop_duplicates().head(2).astype(str).tolist()
        selected["diagnostic_only"] = True
    label_meta, hs_pred = fit_label_translator(features, selected_targets, route_stress)

    paths: list[Path] = []
    rows: list[dict[str, Any]] = []
    latent_energy = rank01(features[features["split"].eq("test")].sort_values(KEYS)["hsjepa_surprise"])
    row_gate = 0.35 + 0.65 * latent_energy
    for candidate_id, weight, cap in [
        ("semantic_tiny", 0.015, 0.018),
        ("semantic_micro", 0.025, 0.030),
        ("semantic_tail_micro", 0.035, 0.035),
    ]:
        logits = base_logit.copy()
        move = np.zeros_like(logits)
        for target in selected_targets:
            idx = TARGETS.index(target)
            if np.isnan(hs_pred[:, idx]).all():
                continue
            raw_move = logit(hs_pred[:, idx]) - base_logit[:, idx]
            gate = row_gate if "tail" in candidate_id else np.ones(len(test), dtype=np.float64)
            target_move = np.clip(weight * gate * raw_move, -cap, cap)
            move[:, idx] = target_move
            logits[:, idx] = base_logit[:, idx] + target_move
        path = write_candidate(base, logits, candidate_id)
        paths.append(path)
        rows.append(
            {
                "candidate_id": candidate_id,
                "file": rel(path),
                "basename": path.name,
                "selected_targets": ",".join(selected_targets),
                "strict_route_count": int(route_stress["route_gate"].sum()) if not route_stress.empty else 0,
                "weight": weight,
                "cap": cap,
                "changed_cells": int(np.sum(np.abs(move) > 1.0e-12)),
                "mean_abs_logit_move": float(np.mean(np.abs(move))),
                "max_abs_logit_move": float(np.max(np.abs(move))),
                "tail_top20_move_share": float(np.sum(np.abs(move)[latent_energy >= np.quantile(latent_energy, 0.80)]) / (np.sum(np.abs(move)) + EPS)),
            }
        )
    return pd.DataFrame(rows), label_meta, paths


def score_new_candidates(paths: list[Path]) -> pd.DataFrame:
    # Use the public-anchor loader here because build_known_and_refs also uses
    # parsed datetime keys.  The e328 helper normalizes dates to strings and
    # would fail strict equality against the parsed reference keys.
    sample = load_anchor_sub(E247)[KEYS]
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    files = [CURRENT] + [rel(path) for path in paths]
    candidates = build_features(files, sample, refs, ref_vecs)
    scores = score_candidates(known, candidates, model_df)
    scores.to_csv(SCORE_OUT, index=False)
    return scores


def candidate_anatomy(paths: list[Path]) -> pd.DataFrame:
    sample = load_sub_frame(E247)[KEYS]
    base = load_sub_frame(E247, sample)
    e323 = load_sub_frame(E323, sample)
    l_base = logit(base[TARGETS].to_numpy(dtype=np.float64))
    bad = logit(e323[TARGETS].to_numpy(dtype=np.float64)) - l_base
    rows = []
    for path in paths:
        cand = load_sub_frame(path, sample)
        move = logit(cand[TARGETS].to_numpy(dtype=np.float64)) - l_base
        rows.append(
            {
                "basename": path.name,
                "cos_with_e323_bad_delta": cos(move, bad),
                "l1_ratio_to_e323_delta": float(np.sum(np.abs(move)) / (np.sum(np.abs(bad)) + EPS)),
                "changed_rows": int(np.any(np.abs(move) > EPS, axis=1).sum()),
                "changed_cells": int((np.abs(move) > EPS).sum()),
                "mean_abs_logit_delta": float(np.mean(np.abs(move))),
                "max_abs_prob_delta": float(np.max(np.abs(cand[TARGETS].to_numpy(dtype=np.float64) - base[TARGETS].to_numpy(dtype=np.float64)))),
            }
        )
    anatomy = pd.DataFrame(rows).sort_values(["l1_ratio_to_e323_delta", "basename"]).reset_index(drop=True)
    anatomy.to_csv(ANATOMY_OUT, index=False)
    return anatomy


def cluster_story_read(features: pd.DataFrame, story_state: pd.DataFrame) -> pd.DataFrame:
    train_mask = features["split"].eq("train").to_numpy()
    train = features.loc[train_mask].reset_index(drop=True)
    stories = story_state.loc[train_mask].reset_index(drop=True)
    rows = []
    for cluster, part in train.groupby("hsjepa_cluster"):
        idx = part.index.to_numpy()
        rest_idx = np.setdiff1d(np.arange(len(train)), idx)
        rec: dict[str, Any] = {
            "cluster": int(cluster),
            "n_train": int(len(part)),
            "dominant_subject": str(part["subject_id"].mode().iloc[0]) if len(part) else "",
        }
        for target in TARGETS:
            rec[f"{target}_rate"] = float(part[target].mean())
        deltas = []
        for col in stories.columns:
            vals = stories[col].to_numpy(dtype=np.float64)
            if len(idx) and len(rest_idx):
                deltas.append((col, float(vals[idx].mean() - vals[rest_idx].mean())))
        rec["top_human_state_delta"] = "; ".join(f"{name}:{value:.2f}" for name, value in sorted(deltas, key=lambda x: abs(x[1]), reverse=True)[:8])
        rows.append(rec)
    return pd.DataFrame(rows).sort_values("n_train", ascending=False).reset_index(drop=True)


def write_report(
    definitions: pd.DataFrame,
    recon: pd.DataFrame,
    geometry: pd.DataFrame,
    pairs: pd.DataFrame,
    target_stress: pd.DataFrame,
    route_stress: pd.DataFrame,
    boundary: pd.DataFrame,
    clusters: pd.DataFrame,
    candidates: pd.DataFrame,
    label_meta: pd.DataFrame,
    scores: pd.DataFrame,
    anatomy: pd.DataFrame,
    selection: pd.DataFrame,
) -> None:
    non_current = scores[~scores["basename"].eq(CURRENT)].copy() if not scores.empty and "basename" in scores.columns else pd.DataFrame()
    promoted = non_current[non_current.get("promotion_decision", pd.Series(dtype=str)).eq("promote_candidate")] if not non_current.empty else pd.DataFrame()
    lines = [
        "# H003 HS-JEPA Prototype",
        "",
        "## Question",
        "",
        "Can Human-State JEPA produce a hidden lifestyle representation that is context-predictable, geometrically healthy, target-block relevant, and safe enough to translate on top of E247?",
        "",
        "## Method",
        "",
        "- JEPA target: explicit human episode states, not raw features and not final probabilities.",
        "- Context views: family JEPA context, raw human context, and hybrid context.",
        "- Masking: semantic view mask by context family and grouped OOF split.",
        "- Latent: PCA of context-predicted episode targets plus residual/surprise diagnostics.",
        "- Safety: LeJEPA-style geometry, adjacent-row positive-pair diagnostics, label/null stress, and public-sensor alignment.",
        "",
        "## Human-State Targets",
        "",
        md_table(definitions[["episode", "human_story", "source", "feature_col", "weight"]], n=80),
        "",
        "## Context -> Human-State Reconstruction",
        "",
        md_table(recon[["view_id", "split", "episode", "r2", "corr", "train_test_pred_z_gap"]].head(35), n=35),
        "",
        "## Latent Geometry",
        "",
        md_table(geometry, n=5),
        "",
        "## Positive-Pair Diagnostics",
        "",
        md_table(pairs, n=10),
        "",
        "## Target Translation Stress",
        "",
        md_table(target_stress[["split", "target", "delta_logloss", "null_median", "dominance", "row_dominance", "subject_dominance", "dateblock_dominance", "target_gate"]], n=20, floatfmt=".9f"),
        "",
        "## Episode Target Routes",
        "",
        "This is the sparse HS-JEPA translation test: one human episode should only affect the targets it can explain under matched nulls.",
        "",
        md_table(route_stress[["split", "episode", "target", "delta_logloss", "null_median", "dominance", "row_dominance", "subject_dominance", "dateblock_dominance", "route_gate"]], n=40, floatfmt=".9f"),
        "",
        "## Public-Sensor Alignment",
        "",
        md_table(boundary.head(25), n=25),
        "",
        "## Cluster Story Read",
        "",
        md_table(clusters, n=12),
        "",
        "## Candidate Translators",
        "",
        md_table(candidates, n=10, floatfmt=".9f"),
        "",
        "## Label Translator Meta",
        "",
        md_table(label_meta, n=10),
        "",
        "## Public-Free Selector Scores",
        "",
        md_table(non_current[["basename", "promotion_decision", "pred_delta_vs_current_mean", "pred_delta_vs_current_p10", "pred_delta_vs_current_p90", "pred_beats_current_rate", "incremental_bad_axis_vs_current"]] if not non_current.empty else non_current, n=10, floatfmt=".9f"),
        "",
        "## Candidate Anatomy",
        "",
        md_table(anatomy, n=10, floatfmt=".9f"),
        "",
        "## Selection",
        "",
        md_table(selection, n=5, floatfmt=".9f"),
        "",
        "## Decision",
        "",
    ]
    target_gate_count = int(target_stress["target_gate"].sum()) if not target_stress.empty else 0
    if len(promoted):
        lines.append("One HS-JEPA candidate passed the strict selector. Promote only the selected uploadsafe file.")
    elif target_gate_count > 0:
        lines.append("HS-JEPA produced target-level signal, but no candidate passed the public-free selector. Treat candidates as diagnostic only until a stronger translator is built.")
    else:
        lines.append("HS-JEPA produced a usable representation prototype, but its current probability translator is not strong enough. Keep the latent and rebuild the translator.")
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- `{rel(FEATURES_OUT)}`",
            f"- `{rel(RECON_OUT)}`",
            f"- `{rel(GEOMETRY_OUT)}`",
            f"- `{rel(PAIR_OUT)}`",
            f"- `{rel(TARGET_OUT)}`",
            f"- `{rel(ROUTE_OUT)}`",
            f"- `{rel(BOUNDARY_OUT)}`",
            f"- `{rel(CANDIDATE_OUT)}`",
            f"- `{rel(SCORE_OUT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    for stale in H003.glob("submission_h003_*.csv"):
        stale.unlink()
    base, raw, _stories, feature_frames = load_frames()
    story_state, definitions = build_episode_matrix(base, feature_frames)
    pred_bundle, recon, _y_train = build_context_target_predictions(base, raw, story_state)
    features, geometry = make_hs_latent(base, pred_bundle, story_state)
    pairs = positive_pair_diagnostics(features)
    target_stress, nulls = target_translation_stress(features)
    route_stress, route_nulls = episode_target_route_stress(features)
    boundary = public_sensor_alignment(features)
    clusters = cluster_story_read(features, story_state)
    candidates, label_meta, paths = materialize_candidates(features, target_stress, route_stress)
    try:
        scores = score_new_candidates(paths)
    except Exception as exc:  # noqa: BLE001
        scores = pd.DataFrame({"error": [f"{type(exc).__name__}: {exc}"]})
        scores.to_csv(SCORE_OUT, index=False)
    anatomy = candidate_anatomy(paths)

    if not scores.empty and "promotion_decision" in scores.columns:
        non_current = scores[~scores["basename"].eq(CURRENT)].copy()
        strict = non_current[non_current["promotion_decision"].eq("promote_candidate")]
        if len(strict):
            selected = strict.iloc[[0]].copy()
            selected_path = H003 / str(selected.iloc[0]["basename"])
            uploadsafe = selected_path.with_name(selected_path.stem + "_uploadsafe.csv")
            if selected_path.exists():
                uploadsafe.write_bytes(selected_path.read_bytes())
            decision = "promote_h003_uploadsafe"
            selected_file = rel(uploadsafe) if uploadsafe.exists() else "none"
        else:
            selected = non_current.head(1).copy()
            decision = "diagnostic_only_no_h003_submission"
            selected_file = "none"
    else:
        selected = pd.DataFrame()
        decision = "diagnostic_only_selector_failed"
        selected_file = "none"
    selection = pd.DataFrame(
        [
            {
                "decision": decision,
                "selected_uploadsafe_file": selected_file,
                "strict_promote_count": int((scores["promotion_decision"].eq("promote_candidate")).sum()) if not scores.empty and "promotion_decision" in scores.columns else 0,
                "target_gate_count": int(target_stress["target_gate"].sum()) if not target_stress.empty else 0,
                "route_gate_count": int(route_stress["route_gate"].sum()) if not route_stress.empty else 0,
                "best_diagnostic_basename": str(selected.iloc[0]["basename"]) if len(selected) and "basename" in selected.columns else "none",
            }
        ]
    )

    definitions.to_csv(DEFINITION_OUT, index=False)
    recon.to_csv(RECON_OUT, index=False)
    features.to_parquet(FEATURES_OUT, index=False)
    geometry.to_csv(GEOMETRY_OUT, index=False)
    pairs.to_csv(PAIR_OUT, index=False)
    target_stress.to_csv(TARGET_OUT, index=False)
    nulls.to_csv(NULL_OUT, index=False)
    route_stress.to_csv(ROUTE_OUT, index=False)
    route_nulls.to_csv(ROUTE_NULL_OUT, index=False)
    boundary.to_csv(BOUNDARY_OUT, index=False)
    clusters.to_csv(CLUSTER_OUT, index=False)
    candidates.to_csv(CANDIDATE_OUT, index=False)
    anatomy.to_csv(ANATOMY_OUT, index=False)
    selection.to_csv(SELECTION_OUT, index=False)
    write_report(definitions, recon, geometry, pairs, target_stress, route_stress, boundary, clusters, candidates, label_meta, scores, anatomy, selection)

    print(f"report={rel(REPORT_OUT)}")
    print(selection.to_string(index=False))
    print("[geometry]")
    print(geometry.round(6).to_string(index=False))
    print("[target_stress]")
    print(target_stress[["split", "target", "delta_logloss", "dominance", "target_gate"]].round(9).head(14).to_string(index=False))
    print("[route_stress]")
    print(route_stress[["split", "episode", "target", "delta_logloss", "dominance", "route_gate"]].round(9).head(12).to_string(index=False))


if __name__ == "__main__":
    main()
