#!/usr/bin/env python3
"""E328: own-latent hidden lifestyle-state experiment.

Question:
    Can human/social lifelog views be turned into a reusable hidden lifestyle
    state, and can that state separate the current public-good E247 geometry
    from the public-bad E323 residual movement?

This is a JEPA/data2vec-style experiment in the narrow sense:
    - Build a teacher latent from multi-view lifestyle context.
    - Predict that learned latent from masked context views.
    - Use prediction residuals, density, and cluster geometry as state health.
    - Do not reconstruct raw values.

Public LB is not used as a tuning loop. E323 is used as a resolved negative
sensor/anchor after its public failure.
"""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import log_loss, r2_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import KEYS, TARGETS, load_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402
from e272_public_free_candidate_audit import CURRENT, build_features, evaluate_models, score_candidates  # noqa: E402


RNG_SEED = 20260531 + 328
EPS = 1.0e-12

E262_RAW = OUT / "e262_human_social_day_features.parquet"
E268_SOCIAL = OUT / "e268_human_social_story_features.parquet"
E270_CASH = OUT / "e270_payday_cashflow_story_features.parquet"
E273_STATE = OUT / "e273_human_diary_state_jepa_audit_features.parquet"

E224 = OUT / "submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv"
E247 = OUT / CURRENT
E256 = OUT / "submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv"
E323 = OUT / "submission_e323_5508f966_uploadsafe.csv"

FEATURES_OUT = OUT / "e328_ownlatent_lifestyle_state_features.parquet"
VIEW_OUT = OUT / "e328_ownlatent_lifestyle_state_view_summary.csv"
LABEL_OUT = OUT / "e328_ownlatent_lifestyle_state_label_stress.csv"
TARGET_OUT = OUT / "e328_ownlatent_lifestyle_state_target_detail.csv"
NULL_OUT = OUT / "e328_ownlatent_lifestyle_state_nulls.csv"
BOUNDARY_OUT = OUT / "e328_ownlatent_lifestyle_state_boundary_alignment.csv"
CLUSTER_OUT = OUT / "e328_ownlatent_lifestyle_state_cluster_summary.csv"
CANDIDATE_OUT = OUT / "e328_ownlatent_lifestyle_state_candidates.csv"
SCORE_OUT = OUT / "e328_ownlatent_lifestyle_state_candidate_scores.csv"
ANATOMY_OUT = OUT / "e328_ownlatent_lifestyle_state_candidate_anatomy.csv"
REPORT_OUT = OUT / "e328_ownlatent_lifestyle_state_report.md"

TEACHER_DIMS = 12
OWN_DIMS = 8
NULL_REPS = 5
RAW_MAX_COLS = 160
STORY_MAX_COLS = 180


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def md_table(frame: pd.DataFrame, n: int = 25, floatfmt: str = ".6f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame.head(n).copy()
    for col in view.columns:
        if pd.api.types.is_float_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else format(float(x), floatfmt))
    view = view.fillna("")
    headers = [str(c) for c in view.columns]
    rows = [[str(v).replace("\n", " ") for v in row] for row in view.to_numpy()]
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    out.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(out)


def short_hash(frame: pd.DataFrame) -> str:
    arr = np.asarray(frame[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def safe_id(text: str, limit: int = 96) -> str:
    return "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in str(text))[:limit]


def stable_seed(*parts: object) -> int:
    digest = hashlib.sha1("|".join(map(str, parts)).encode("utf-8")).hexdigest()
    return RNG_SEED + int(digest[:8], 16) % 100000


def normalize_dates(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in ["sleep_date", "lifelog_date"]:
        if col in out.columns:
            out[col] = pd.to_datetime(out[col]).dt.strftime("%Y-%m-%d")
    return out.sort_values(KEYS).reset_index(drop=True)


def require_aligned(base: pd.DataFrame, other: pd.DataFrame, name: str) -> None:
    if not base[KEYS].equals(other[KEYS]):
        raise RuntimeError(f"{name} key mismatch")


def load_frames() -> dict[str, pd.DataFrame]:
    state = normalize_dates(pd.read_parquet(E273_STATE))
    raw = normalize_dates(pd.read_parquet(E262_RAW))
    social = normalize_dates(pd.read_parquet(E268_SOCIAL))
    cash = normalize_dates(pd.read_parquet(E270_CASH))
    for name, frame in [("raw", raw), ("social", social), ("cash", cash)]:
        require_aligned(state, frame, name)
    return {"state": state, "raw": raw, "social": social, "cash": cash}


def train_mask(df: pd.DataFrame) -> np.ndarray:
    return df["split"].eq("train").to_numpy()


def signed_log1p(s: pd.Series) -> pd.Series:
    x = pd.to_numeric(s, errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(0.0).astype(float)
    return np.sign(x) * np.log1p(np.abs(x))


def robust_table(df: pd.DataFrame, cols: list[str], mask: np.ndarray, max_cols: int | None = None) -> pd.DataFrame:
    if not cols:
        return pd.DataFrame(index=df.index)
    series: dict[str, pd.Series] = {}
    for col in cols:
        x = pd.to_numeric(df[col], errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(0.0).astype(float)
        tr = x.iloc[mask]
        if bool((tr >= 0).all()) and float(tr.quantile(0.99)) > 10.0:
            x = signed_log1p(x)
        series[col] = x
    work = pd.DataFrame(series, index=df.index)
    std = work.iloc[mask].std(ddof=0).replace(0, np.nan).dropna()
    keep = std.sort_values(ascending=False).index.tolist()
    if max_cols is not None:
        keep = keep[:max_cols]
    work = work[keep].replace([np.inf, -np.inf], 0.0).fillna(0.0)
    med = work.iloc[mask].median(axis=0)
    q75 = work.iloc[mask].quantile(0.75, axis=0)
    q25 = work.iloc[mask].quantile(0.25, axis=0)
    scale = ((q75 - q25) / 1.349).replace(0, np.nan).fillna(work.iloc[mask].std(ddof=0)).replace(0, 1.0)
    z = ((work - med) / scale).replace([np.inf, -np.inf], 0.0).fillna(0.0).clip(-8.0, 8.0)
    return z


def numeric_cols(df: pd.DataFrame, extra_blocked: Iterable[str] = ()) -> list[str]:
    blocked = set(KEYS + TARGETS + ["split", "dateblock_group", "lifelog_date_only", "sleep_date_only", "lifelog_dt"])
    blocked.update(extra_blocked)
    return [
        c
        for c in df.columns
        if c not in blocked and pd.api.types.is_numeric_dtype(df[c])
    ]


def build_views(frames: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    state = frames["state"]
    mask = train_mask(state)
    family_cols = [
        c
        for c in state.columns
        if (
            (re.match(r"^(social_comm|cognitive_money|media_game|bedtime_phone|mobility_context|physiology_activity|routine_calendar|sensor_measurement)_pc\d+$", c)
             or re.match(r"^(social_comm|cognitive_money|media_game|bedtime_phone|mobility_context|physiology_activity|routine_calendar|sensor_measurement)_energy$", c))
            and pd.api.types.is_numeric_dtype(state[c])
        )
    ]
    jepa_cols = [c for c in state.columns if c.startswith("jepa_resid_") or c.startswith("jepa_prednorm_")]
    calendar_cols = [
        c
        for c in ["weekday", "is_weekend", "subject_order", "lifelog_dom", "lifelog_month", "weekday_sin", "weekday_cos", "dom_sin", "dom_cos", "month_sin", "month_cos"]
        if c in state.columns
    ]
    social_cols = [
        c
        for c in numeric_cols(frames["social"])
        if c.endswith("_subj_z") or c.endswith("_weekend") or c.endswith("_active")
    ]
    cash_cols = [
        c
        for c in numeric_cols(frames["cash"])
        if c.endswith("_subj_z") or c.endswith("_active")
    ]
    raw_cols = [
        c
        for c in numeric_cols(frames["raw"])
        if not c.endswith("_abs_subj_z")
    ]
    views: dict[str, pd.DataFrame] = {
        "family": robust_table(state, family_cols, mask),
        "jepa_resid": robust_table(state, jepa_cols, mask),
        "calendar": robust_table(state, calendar_cols, mask),
        "social_story": robust_table(frames["social"], social_cols, mask, STORY_MAX_COLS).add_prefix("soc__"),
        "cash_story": robust_table(frames["cash"], cash_cols, mask, STORY_MAX_COLS).add_prefix("cash__"),
        "raw_day": robust_table(frames["raw"], raw_cols, mask, RAW_MAX_COLS).add_prefix("raw__"),
    }
    views["story_bundle"] = pd.concat([views["social_story"], views["cash_story"]], axis=1)
    views["family_story"] = pd.concat([views["family"].add_prefix("fam__"), views["story_bundle"]], axis=1)
    views["family_jepa_story"] = pd.concat([views["family"].add_prefix("fam__"), views["jepa_resid"].add_prefix("jr__"), views["story_bundle"]], axis=1)
    views["all_context"] = pd.concat(
        [
            views["family"].add_prefix("fam__"),
            views["jepa_resid"].add_prefix("jr__"),
            views["story_bundle"],
            views["raw_day"],
            views["calendar"].add_prefix("cal__"),
        ],
        axis=1,
    )
    return {k: v.replace([np.inf, -np.inf], 0.0).fillna(0.0) for k, v in views.items()}


def standard_teacher(all_context: pd.DataFrame, mask: np.ndarray) -> tuple[np.ndarray, pd.DataFrame, dict[str, float]]:
    pipe = make_pipeline(SimpleImputer(strategy="median"), StandardScaler())
    z_train = pipe.fit_transform(all_context.iloc[mask])
    z_all = pipe.transform(all_context)
    n_comp = min(TEACHER_DIMS, z_train.shape[1], int(mask.sum()) - 1)
    pca = PCA(n_components=n_comp, random_state=RNG_SEED)
    pca.fit(z_train)
    teacher = pca.transform(z_all)
    svals = np.linalg.svd(teacher[mask] - teacher[mask].mean(axis=0, keepdims=True), compute_uv=False)
    participation = float((np.sum(svals**2) ** 2) / (np.sum(svals**4) + EPS))
    diag = {
        "teacher_dims": float(n_comp),
        "teacher_explained_var_sum": float(np.sum(pca.explained_variance_ratio_)),
        "teacher_participation_ratio": participation,
        "teacher_anisotropy": float(np.max(svals) / max(np.min(svals), 1.0e-9)),
    }
    teacher_df = pd.DataFrame(teacher, columns=[f"teacher_pc{i+1}" for i in range(n_comp)])
    return teacher, teacher_df, diag


def groups_for(df: pd.DataFrame, split_name: str) -> pd.Series:
    if split_name == "subject":
        return df["subject_id"].astype(str)
    if split_name == "dateblock":
        return df["dateblock_group"].astype(str)
    raise ValueError(split_name)


def oof_predict_teacher(x: pd.DataFrame, y: np.ndarray, df: pd.DataFrame, split_name: str) -> tuple[np.ndarray, np.ndarray, float]:
    mask = train_mask(df)
    x_train = x.iloc[mask].reset_index(drop=True)
    y_train = y[mask]
    x_all = x.reset_index(drop=True)
    groups = groups_for(df.loc[mask].reset_index(drop=True), split_name)
    pred_train = np.zeros_like(y_train, dtype=np.float64)
    if x_train.shape[1] == 0:
        pred_train[:] = y_train.mean(axis=0, keepdims=True)
        pred_all = np.repeat(y_train.mean(axis=0, keepdims=True), len(x_all), axis=0)
        return pred_train, pred_all, 0.0
    folds = list(GroupKFold(n_splits=min(5, int(groups.nunique()))).split(x_train, groups=groups))
    for tr_idx, va_idx in folds:
        model = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), Ridge(alpha=8.0))
        model.fit(x_train.iloc[tr_idx], y_train[tr_idx])
        pred_train[va_idx] = model.predict(x_train.iloc[va_idx])
    full = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), Ridge(alpha=8.0))
    full.fit(x_train, y_train)
    pred_all = np.asarray(full.predict(x_all), dtype=np.float64)
    try:
        r2 = float(r2_score(y_train, pred_train, multioutput="variance_weighted"))
    except ValueError:
        r2 = 0.0
    return pred_train, pred_all, r2


def build_own_latent(df: pd.DataFrame, views: dict[str, pd.DataFrame], teacher: np.ndarray) -> tuple[pd.DataFrame, pd.DataFrame]:
    mask = train_mask(df)
    own_parts: list[pd.DataFrame] = []
    summary_rows: list[dict[str, object]] = []
    view_order = ["family", "jepa_resid", "story_bundle", "raw_day", "family_story", "family_jepa_story"]
    for view_id in view_order:
        x = views[view_id]
        for split_name in ["subject", "dateblock"]:
            pred_train, pred_all_full, r2 = oof_predict_teacher(x, teacher, df, split_name)
            pred_all = pred_all_full.copy()
            pred_all[mask] = pred_train
            resid = teacher - pred_all
            cols = {}
            for j in range(min(6, teacher.shape[1])):
                cols[f"ol_{view_id}_{split_name}_pc{j+1}"] = pred_all[:, j]
            cols[f"ol_{view_id}_{split_name}_resid_energy"] = np.sqrt(np.mean(resid**2, axis=1))
            cols[f"ol_{view_id}_{split_name}_pred_energy"] = np.sqrt(np.mean(pred_all[:, : min(6, pred_all.shape[1])] ** 2, axis=1))
            part = pd.DataFrame(cols, index=df.index)
            own_parts.append(part)
            summary_rows.append(
                {
                    "view_id": view_id,
                    "split": split_name,
                    "context_cols": int(x.shape[1]),
                    "teacher_dims": int(teacher.shape[1]),
                    "oof_teacher_r2": r2,
                    "resid_energy_train_mean": float(part.loc[mask, f"ol_{view_id}_{split_name}_resid_energy"].mean()),
                    "resid_energy_test_mean": float(part.loc[~mask, f"ol_{view_id}_{split_name}_resid_energy"].mean()),
                }
            )
    student = pd.concat(own_parts, axis=1).replace([np.inf, -np.inf], 0.0).fillna(0.0)
    pipe = make_pipeline(SimpleImputer(strategy="median"), StandardScaler())
    z_train = pipe.fit_transform(student.iloc[mask])
    z_all = pipe.transform(student)
    n_comp = min(OWN_DIMS, z_train.shape[1], int(mask.sum()) - 1)
    pca = PCA(n_components=n_comp, random_state=RNG_SEED)
    pca.fit(z_train)
    latent = pca.transform(z_all)
    out = df[KEYS + ["split", "dateblock_group", "subject_order", "weekday", "is_weekend", *TARGETS]].copy()
    for j in range(n_comp):
        out[f"ownlife_pc{j+1}"] = latent[:, j]
    out["ownlife_energy"] = np.sqrt(np.mean(latent[:, : min(6, n_comp)] ** 2, axis=1))
    center = np.mean(latent[mask, : min(6, n_comp)], axis=0, keepdims=True)
    out["ownlife_global_distance"] = np.sqrt(np.mean((latent[:, : min(6, n_comp)] - center) ** 2, axis=1))
    resid_cols = [c for c in student.columns if c.endswith("_resid_energy")]
    out["ownlife_student_resid_mean"] = student[resid_cols].mean(axis=1)
    out["ownlife_student_resid_max"] = student[resid_cols].max(axis=1)

    km = KMeans(n_clusters=8, random_state=RNG_SEED, n_init=30)
    km.fit(latent[mask, : min(6, n_comp)])
    clusters = km.predict(latent[:, : min(6, n_comp)])
    out["ownlife_k8"] = clusters
    dist = km.transform(latent[:, : min(6, n_comp)])
    out["ownlife_cluster_distance"] = np.min(dist, axis=1)
    for k in range(8):
        out[f"ownlife_k8_{k}"] = (clusters == k).astype(float)

    svals = np.linalg.svd(latent[mask] - latent[mask].mean(axis=0, keepdims=True), compute_uv=False)
    summary_rows.append(
        {
            "view_id": "own_lifestyle_state",
            "split": "train_geometry",
            "context_cols": int(student.shape[1]),
            "teacher_dims": int(n_comp),
            "oof_teacher_r2": np.nan,
            "resid_energy_train_mean": float(out.loc[mask, "ownlife_student_resid_mean"].mean()),
            "resid_energy_test_mean": float(out.loc[~mask, "ownlife_student_resid_mean"].mean()),
            "explained_var_sum": float(np.sum(pca.explained_variance_ratio_)),
            "participation_ratio": float((np.sum(svals**2) ** 2) / (np.sum(svals**4) + EPS)),
            "anisotropy": float(np.max(svals) / max(np.min(svals), 1.0e-9)),
        }
    )
    return out, pd.DataFrame(summary_rows)


def base_matrix(train: pd.DataFrame) -> pd.DataFrame:
    base_cols = ["subject_order", "weekday", "is_weekend"]
    pieces = [train[[c for c in base_cols if c in train.columns]].astype(float).reset_index(drop=True)]
    subj = pd.get_dummies(train["subject_id"].astype(str), prefix="sid", dtype=float)
    pieces.append(subj.reset_index(drop=True))
    return pd.concat(pieces, axis=1).replace([np.inf, -np.inf], 0.0).fillna(0.0)


def fit_logistic_predict(x_train: pd.DataFrame, y_train: np.ndarray, x_pred: pd.DataFrame) -> np.ndarray:
    if len(np.unique(y_train)) < 2:
        return np.full(len(x_pred), float(np.mean(y_train)), dtype=np.float64)
    model = make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(with_mean=False),
        LogisticRegression(C=0.25, solver="liblinear", max_iter=1200),
    )
    model.fit(x_train, y_train)
    return clip_prob(model.predict_proba(x_pred)[:, 1])


def cv_loss(x: pd.DataFrame, y: np.ndarray, groups: pd.Series) -> float:
    pred = np.zeros(len(y), dtype=np.float64)
    cv = GroupKFold(n_splits=min(5, int(groups.nunique())))
    for tr_idx, va_idx in cv.split(x, y, groups):
        pred[va_idx] = fit_logistic_predict(x.iloc[tr_idx], y[tr_idx], x.iloc[va_idx])
    return float(log_loss(y, clip_prob(pred), labels=[0, 1]))


def shuffled_latent(lat: pd.DataFrame, mode: str, groups: pd.Series, rng: np.random.Generator) -> pd.DataFrame:
    arr = lat.to_numpy(dtype=np.float64)
    if mode == "row":
        return pd.DataFrame(arr[rng.permutation(len(arr))], columns=lat.columns)
    out = arr.copy()
    for _, idx in groups.groupby(groups).groups.items():
        idx_arr = np.asarray(list(idx), dtype=int)
        if len(idx_arr) > 1:
            out[idx_arr] = arr[idx_arr][rng.permutation(len(idx_arr))]
    return pd.DataFrame(out, columns=lat.columns)


def label_stress(features: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train = features[features["split"].eq("train")].reset_index(drop=True)
    latent_cols = [c for c in train.columns if c.startswith("ownlife_") and c != "ownlife_k8"]
    x_base = base_matrix(train)
    x_lat = pd.concat([x_base, train[latent_cols].astype(float).reset_index(drop=True)], axis=1)
    rows: list[dict[str, object]] = []
    target_rows: list[dict[str, object]] = []
    null_rows: list[dict[str, object]] = []
    for split_name, groups in {
        "subject": train["subject_id"].astype(str).reset_index(drop=True),
        "dateblock": train["dateblock_group"].astype(str).reset_index(drop=True),
    }.items():
        deltas = []
        for target in TARGETS:
            y = train[target].astype(int).to_numpy()
            base_loss = cv_loss(x_base, y, groups)
            lat_loss = cv_loss(x_lat, y, groups)
            delta = lat_loss - base_loss
            deltas.append(delta)
            target_rows.append(
                {
                    "split": split_name,
                    "target": target,
                    "base_loss": base_loss,
                    "ownlatent_loss": lat_loss,
                    "delta_logloss": delta,
                }
            )
        actual_mean = float(np.mean(deltas))
        null_vals = []
        for mode, shuffle_groups in {
            "row": groups,
            "subject": train["subject_id"].astype(str).reset_index(drop=True),
            "dateblock": train["dateblock_group"].astype(str).reset_index(drop=True),
        }.items():
            rng = np.random.default_rng(stable_seed("labelnull", split_name, mode))
            for rep in range(NULL_REPS):
                nx_latent = shuffled_latent(train[latent_cols].reset_index(drop=True), mode, shuffle_groups, rng)
                nx = pd.concat([x_base, nx_latent], axis=1)
                losses = []
                for target in TARGETS:
                    y = train[target].astype(int).to_numpy()
                    losses.append(cv_loss(nx, y, groups) - cv_loss(x_base, y, groups))
                null_mean = float(np.mean(losses))
                null_vals.append(null_mean)
                null_rows.append(
                    {
                        "split": split_name,
                        "mode": mode,
                        "rep": rep,
                        "null_delta_mean": null_mean,
                    }
                )
        null_arr = np.asarray(null_vals, dtype=np.float64)
        rows.append(
            {
                "split": split_name,
                "actual_delta_mean": actual_mean,
                "actual_delta_best": float(np.min(deltas)),
                "actual_delta_worst": float(np.max(deltas)),
                "targets_improved": int(np.sum(np.asarray(deltas) < 0.0)),
                "null_best": float(np.min(null_arr)),
                "null_median": float(np.median(null_arr)),
                "null_q20": float(np.quantile(null_arr, 0.20)),
                "dominance": float(np.mean(actual_mean < null_arr)),
                "placebo_adjusted_vs_median": actual_mean - float(np.median(null_arr)),
                "label_gate": bool(actual_mean < 0.0 and np.mean(actual_mean < null_arr) >= 0.85),
            }
        )
    return pd.DataFrame(rows), pd.DataFrame(target_rows), pd.DataFrame(null_rows)


def cohen_d(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    a = a[np.isfinite(a)]
    b = b[np.isfinite(b)]
    if len(a) < 2 or len(b) < 2:
        return 0.0
    pooled = np.sqrt(((len(a) - 1) * np.var(a, ddof=1) + (len(b) - 1) * np.var(b, ddof=1)) / max(len(a) + len(b) - 2, 1))
    if not np.isfinite(pooled) or pooled < 1.0e-12:
        return 0.0
    return float((np.mean(a) - np.mean(b)) / pooled)


def load_sub_frame(path: Path, sample: pd.DataFrame | None = None) -> pd.DataFrame:
    df = normalize_dates(pd.read_csv(path))
    if sample is not None:
        sample_norm = normalize_dates(sample.copy())
        if not df[KEYS].equals(sample_norm[KEYS]):
            raise RuntimeError(f"key mismatch: {path}")
    return df


def load_prob(path: Path, sample: pd.DataFrame) -> np.ndarray:
    return load_sub_frame(path, sample)[TARGETS].to_numpy(dtype=np.float64)


def boundary_alignment(features: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray, np.ndarray]:
    test = features[features["split"].eq("test")].sort_values(KEYS).reset_index(drop=True)
    sample = test[KEYS]
    e224 = load_prob(E224, sample)
    e247 = load_prob(E247, sample)
    e256 = load_prob(E256, sample)
    e323 = load_prob(E323, sample)
    l224 = logit(e224)
    l247 = logit(e247)
    l256 = logit(e256)
    l323 = logit(e323)
    d247 = np.abs(l247[:, 2] - l224[:, 2])
    d256_from224 = np.abs(l256[:, 2] - l224[:, 2])
    e247_only = (d247 > 1.0e-10) & ~(d256_from224 > 1.0e-10)
    e256_only = (d256_from224 > 1.0e-10) & ~(d247 > 1.0e-10)
    neutral = ~(e247_only | e256_only)
    e323_l1 = np.sum(np.abs(l323 - l247), axis=1)
    e323_top20 = e323_l1 >= np.quantile(e323_l1, 0.80)
    cols = [
        c
        for c in test.columns
        if c.startswith("ownlife_pc")
        or c in {
            "ownlife_energy",
            "ownlife_global_distance",
            "ownlife_student_resid_mean",
            "ownlife_student_resid_max",
            "ownlife_cluster_distance",
        }
        or c.startswith("ownlife_k8_")
    ]
    rows = []
    for col in cols:
        vals = pd.to_numeric(test[col], errors="coerce").fillna(0.0).to_numpy(dtype=np.float64)
        rows.append(
            {
                "feature": col,
                "e247_only_d_vs_neutral": cohen_d(vals[e247_only], vals[neutral]),
                "e256_only_d_vs_neutral": cohen_d(vals[e256_only], vals[neutral]),
                "e247_vs_e256_d": cohen_d(vals[e247_only], vals[e256_only]),
                "e323_top20_d_vs_rest": cohen_d(vals[e323_top20], vals[~e323_top20]),
                "mean_e247_only": float(np.mean(vals[e247_only])) if e247_only.any() else np.nan,
                "mean_e256_only": float(np.mean(vals[e256_only])) if e256_only.any() else np.nan,
                "mean_e323_top20": float(np.mean(vals[e323_top20])) if e323_top20.any() else np.nan,
            }
        )
    boundary = pd.DataFrame(rows)
    boundary["abs_boundary_signal"] = boundary[["e247_vs_e256_d", "e323_top20_d_vs_rest"]].abs().max(axis=1)
    boundary = boundary.sort_values(["abs_boundary_signal", "feature"], ascending=[False, True]).reset_index(drop=True)

    cluster_rows = []
    for cluster, part in test.assign(e323_l1=e323_l1, e247_only=e247_only, e256_only=e256_only, e323_top20=e323_top20).groupby("ownlife_k8"):
        cluster_rows.append(
            {
                "cluster": int(cluster),
                "n_test": int(len(part)),
                "e247_only_rate": float(part["e247_only"].mean()),
                "e256_only_rate": float(part["e256_only"].mean()),
                "e323_top20_rate": float(part["e323_top20"].mean()),
                "e323_l1_mean": float(part["e323_l1"].mean()),
                "ownlife_energy_mean": float(part["ownlife_energy"].mean()),
                "top_subject": str(part["subject_id"].mode().iloc[0]) if len(part) else "",
            }
        )
    cluster = pd.DataFrame(cluster_rows).sort_values(["e323_top20_rate", "e247_only_rate"], ascending=[False, False]).reset_index(drop=True)
    return boundary, cluster, l247, l323


def zscore(x: np.ndarray) -> np.ndarray:
    arr = np.asarray(x, dtype=np.float64)
    sd = float(np.nanstd(arr))
    if sd < 1.0e-12:
        return np.zeros_like(arr, dtype=np.float64)
    return (arr - float(np.nanmean(arr))) / sd


def write_submission(base: pd.DataFrame, logits: np.ndarray, candidate_id: str) -> Path:
    out = base.copy()
    out[TARGETS] = clip_prob(sigmoid(logits))
    path = OUT / f"submission_e328_ownlatent_{safe_id(candidate_id)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def candidate_materialization(features: pd.DataFrame, l247: np.ndarray, l323: np.ndarray, cluster: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, list[Path]]:
    test = features[features["split"].eq("test")].sort_values(KEYS).reset_index(drop=True)
    base = load_sub_frame(E247, test[KEYS])
    bad_delta = l323 - l247
    cluster_bad = cluster.set_index("cluster")["e323_top20_rate"].to_dict()
    cluster_rate = test["ownlife_k8"].map(cluster_bad).fillna(0.0).to_numpy(dtype=np.float64)
    latent_risk = (
        0.40 * zscore(test["ownlife_energy"].to_numpy(dtype=np.float64))
        + 0.25 * zscore(test["ownlife_student_resid_mean"].to_numpy(dtype=np.float64))
        + 0.20 * zscore(test["ownlife_cluster_distance"].to_numpy(dtype=np.float64))
        + 0.15 * zscore(cluster_rate)
    )
    gate_tail = sigmoid(1.75 * (latent_risk - np.quantile(latent_risk, 0.70)))
    gate_hard = (latent_risk >= np.quantile(latent_risk, 0.80)).astype(float)
    paths: list[Path] = []
    rows: list[dict[str, object]] = []
    for gate_name, gate in [("softtail", gate_tail), ("hardtop20", gate_hard)]:
        for weight in [0.015, 0.025, 0.04, 0.06]:
            move = -weight * gate[:, None] * bad_delta
            logits = l247 + np.clip(move, -0.10, 0.10)
            candidate_id = f"anti_e323_{gate_name}_w{str(weight).replace('.', 'p')}"
            path = write_submission(base, logits, candidate_id)
            paths.append(path)
            abs_move = np.abs(move)
            top_mask = latent_risk >= np.quantile(latent_risk, 0.80)
            rows.append(
                {
                    "candidate_id": candidate_id,
                    "file": rel(path),
                    "basename": path.name,
                    "gate": gate_name,
                    "weight": weight,
                    "changed_rows": int(np.any(abs_move > 1.0e-12, axis=1).sum()),
                    "changed_cells": int((abs_move > 1.0e-12).sum()),
                    "mean_abs_logit_move": float(abs_move.mean()),
                    "max_abs_logit_move": float(abs_move.max()),
                    "top20_abs_move_share": float(abs_move[top_mask].sum() / (abs_move.sum() + EPS)),
                    "latent_risk_top20_rows": int(top_mask.sum()),
                }
            )
    return pd.DataFrame(rows), base, paths


def score_new_candidates(paths: list[Path]) -> pd.DataFrame:
    sample = load_sub(E247)[KEYS]
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    files = [CURRENT] + [rel(path) for path in paths]
    candidates = build_features(files, sample, refs, ref_vecs)
    scores = score_candidates(known, candidates, model_df)
    scores.to_csv(SCORE_OUT, index=False)
    return scores


def candidate_anatomy(paths: list[Path], base: pd.DataFrame) -> pd.DataFrame:
    current = logit(base[TARGETS].to_numpy(dtype=np.float64))
    e323 = logit(load_sub_frame(E323, base[KEYS])[TARGETS].to_numpy(dtype=np.float64))
    bad = e323 - current
    rows = []
    for path in paths:
        cand = load_sub_frame(path, base[KEYS])
        move = logit(cand[TARGETS].to_numpy(dtype=np.float64)) - current
        denom = float(np.linalg.norm(move) * np.linalg.norm(bad) + EPS)
        rows.append(
            {
                "basename": path.name,
                "cos_with_e323_bad_delta": float(np.sum(move * bad) / denom),
                "l1_ratio_to_e323_delta": float(np.sum(np.abs(move)) / (np.sum(np.abs(bad)) + EPS)),
                "changed_rows": int(np.any(np.abs(move) > 1.0e-12, axis=1).sum()),
                "changed_cells": int((np.abs(move) > 1.0e-12).sum()),
                "mean_abs_logit_delta": float(np.mean(np.abs(move))),
                "max_abs_prob_delta": float(np.max(np.abs(cand[TARGETS].to_numpy(dtype=np.float64) - base[TARGETS].to_numpy(dtype=np.float64)))),
            }
        )
    anatomy = pd.DataFrame(rows).sort_values(["l1_ratio_to_e323_delta", "basename"]).reset_index(drop=True)
    anatomy.to_csv(ANATOMY_OUT, index=False)
    return anatomy


def cluster_story_summary(features: pd.DataFrame, frames: dict[str, pd.DataFrame], cluster: pd.DataFrame) -> pd.DataFrame:
    train = features[features["split"].eq("train")].copy()
    social = frames["social"].loc[features["split"].eq("train")].reset_index(drop=True)
    cash = frames["cash"].loc[features["split"].eq("train")].reset_index(drop=True)
    story_cols = [
        c
        for c in list(social.columns) + list(cash.columns)
        if c.endswith("_subj_z") and c in social.columns.union(cash.columns)
    ]
    story_source = pd.concat(
        [
            social[[c for c in story_cols if c in social.columns]],
            cash[[c for c in story_cols if c in cash.columns]],
        ],
        axis=1,
    )
    story_source = story_source.loc[:, ~story_source.columns.duplicated()]
    rows = []
    for c, part in train.reset_index(drop=True).groupby("ownlife_k8"):
        idx = part.index.to_numpy()
        rest_idx = np.setdiff1d(np.arange(len(train)), idx)
        rec: dict[str, object] = {
            "cluster": int(c),
            "n_train": int(len(idx)),
            "dominant_subject": str(part["subject_id"].mode().iloc[0]) if len(part) else "",
        }
        for target in TARGETS:
            rec[f"{target}_rate"] = float(part[target].mean())
        deltas = []
        for col in story_source.columns:
            vals = pd.to_numeric(story_source[col], errors="coerce").fillna(0.0).to_numpy(dtype=np.float64)
            if len(idx) and len(rest_idx):
                deltas.append((col, float(vals[idx].mean() - vals[rest_idx].mean())))
        top = sorted(deltas, key=lambda x: abs(x[1]), reverse=True)[:8]
        rec["top_story_delta"] = "; ".join(f"{name}:{value:.2f}" for name, value in top)
        rows.append(rec)
    train_cluster = pd.DataFrame(rows)
    return cluster.merge(train_cluster, on="cluster", how="left")


def write_report(
    view_summary: pd.DataFrame,
    label_summary: pd.DataFrame,
    target_detail: pd.DataFrame,
    boundary: pd.DataFrame,
    cluster: pd.DataFrame,
    candidates: pd.DataFrame,
    scores: pd.DataFrame,
    anatomy: pd.DataFrame,
) -> None:
    non_current = scores[~scores["basename"].eq(CURRENT)].copy()
    best = non_current.iloc[0] if len(non_current) else None
    promote = non_current[non_current["promotion_decision"].eq("promote_candidate")]
    lines = [
        "# E328 Own-Latent Lifestyle-State Experiment",
        "",
        "## Question",
        "",
        "Can a learned hidden lifestyle state, built from human/social context and own-latent prediction, explain both labels and the E247/E323 public sensor boundary?",
        "",
        "## JEPA / Own-Latent Construction",
        "",
        "- Teacher: PCA latent from all lifestyle context views, fitted on train days.",
        "- Students: masked context views predict teacher PCs under subject/dateblock OOF splits.",
        "- State: PCA + kmeans on student predictions and residual energies.",
        "- Target is learned latent representation, not raw feature reconstruction.",
        "",
        "## View Predictability",
        "",
        md_table(view_summary.sort_values("oof_teacher_r2", ascending=False), n=20),
        "",
        "## Label Stress",
        "",
        "Negative delta is good. The null columns shuffle the same latent by row/subject/dateblock.",
        "",
        md_table(label_summary, n=10, floatfmt=".9f"),
        "",
        "### Target Detail",
        "",
        md_table(target_detail.sort_values("delta_logloss"), n=16, floatfmt=".9f"),
        "",
        "## Public-Sensor Boundary Alignment",
        "",
        md_table(boundary[["feature", "e247_vs_e256_d", "e323_top20_d_vs_rest", "e247_only_d_vs_neutral", "e256_only_d_vs_neutral", "abs_boundary_signal"]], n=20),
        "",
        "## Lifestyle State Clusters",
        "",
        md_table(cluster, n=12),
        "",
        "## Anti-E323 Candidate Probe",
        "",
        md_table(candidates, n=20, floatfmt=".9f"),
        "",
        "## Public-Free Selector Scores",
        "",
        md_table(non_current[["basename", "promotion_decision", "pred_delta_vs_current_mean", "pred_delta_vs_current_p10", "pred_delta_vs_current_p90", "pred_beats_current_rate", "incremental_bad_axis_vs_current"]], n=20, floatfmt=".9f"),
        "",
        "## Candidate Anatomy",
        "",
        md_table(anatomy, n=20, floatfmt=".9f"),
        "",
        "## Decision",
        "",
    ]
    label_alive = bool((label_summary["actual_delta_mean"] < 0).any())
    e323_signal = float(boundary["e323_top20_d_vs_rest"].abs().max()) if len(boundary) else 0.0
    if best is not None and len(promote):
        lines.append(
            f"One or more anti-E323 gated candidates clear the selector gate. Treat the top file `{best['basename']}` as an information-rich candidate, but remember that it explicitly bets on E323 being a valid negative public sensor."
        )
    elif e323_signal >= 0.8 and label_alive:
        lines.append(
            "The hidden lifestyle state is alive diagnostically: it separates the E323-bad tail and has at least one label-stress win. It is not yet a public-ready candidate because selector promotion did not clear."
        )
    elif e323_signal >= 0.8:
        lines.append(
            "The state mostly serves as an E323-negative anatomy detector, not a label-improving representation. Use it as a censor/gate diagnostic, not as a direct model feature yet."
        )
    else:
        lines.append(
            "This own-latent construction did not find a strong enough lifestyle-state invariant. Do not submit its candidates; rebuild the state target or use a different negative anchor."
        )
    lines.extend(
        [
            "",
            f"- best boundary signal: `{e323_signal:.6f}`",
            f"- any label-stress negative mean: `{label_alive}`",
            f"- strict promote count: `{int(non_current['strict_promote_gate'].sum()) if len(non_current) else 0}`",
            "",
            "## Files",
            "",
            f"- `{FEATURES_OUT.name}`",
            f"- `{VIEW_OUT.name}`",
            f"- `{LABEL_OUT.name}`",
            f"- `{TARGET_OUT.name}`",
            f"- `{BOUNDARY_OUT.name}`",
            f"- `{CLUSTER_OUT.name}`",
            f"- `{CANDIDATE_OUT.name}`",
            f"- `{SCORE_OUT.name}`",
            f"- `{ANATOMY_OUT.name}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    frames = load_frames()
    state = frames["state"]
    views = build_views(frames)
    teacher, teacher_df, teacher_diag = standard_teacher(views["all_context"], train_mask(state))
    own_features, view_summary = build_own_latent(state, views, teacher)
    for key, value in teacher_diag.items():
        view_summary[key] = value if key not in view_summary.columns else view_summary[key].fillna(value)
    label_summary, target_detail, nulls = label_stress(own_features)
    boundary, cluster_test, l247, l323 = boundary_alignment(own_features)
    cluster_full = cluster_story_summary(own_features, frames, cluster_test)
    candidates, base, paths = candidate_materialization(own_features, l247, l323, cluster_test)
    scores = score_new_candidates(paths)
    anatomy = candidate_anatomy(paths, base)

    features_out = pd.concat([own_features.reset_index(drop=True), teacher_df.add_prefix("raw_ownteacher_")], axis=1)
    features_out.to_parquet(FEATURES_OUT, index=False)
    view_summary.to_csv(VIEW_OUT, index=False)
    label_summary.to_csv(LABEL_OUT, index=False)
    target_detail.to_csv(TARGET_OUT, index=False)
    nulls.to_csv(NULL_OUT, index=False)
    boundary.to_csv(BOUNDARY_OUT, index=False)
    cluster_full.to_csv(CLUSTER_OUT, index=False)
    candidates.to_csv(CANDIDATE_OUT, index=False)
    write_report(view_summary, label_summary, target_detail, boundary, cluster_full, candidates, scores, anatomy)

    print(REPORT_OUT)
    print("[label]")
    print(label_summary.round(9).to_string(index=False))
    print("[boundary]")
    print(boundary.head(10).round(6).to_string(index=False))
    print("[scores]")
    print(scores[["basename", "promotion_decision", "pred_delta_vs_current_mean", "pred_delta_vs_current_p10", "pred_delta_vs_current_p90", "pred_beats_current_rate"]].head(12).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
