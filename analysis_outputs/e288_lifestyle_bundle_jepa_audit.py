#!/usr/bin/env python3
"""E288: lifestyle-bundle JEPA audit.

E287 showed that train-supervised q-sleep row actions have signal but fail when
placed onto the current E247 test tensor. This audit moves up one level:

    raw/day context -> hidden human lifestyle story bundle

Instead of submitting another small Q3 edit, we ask whether a multi-story
human/social latent is stable enough to explain labels beyond matched nulls.

No public LB is used and no submission is produced.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from scipy.spatial.distance import jensenshannon
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import log_loss, normalized_mutual_info_score, r2_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]

E262_RAW = OUT / "e262_human_social_day_features.parquet"
E273_FEATURES = OUT / "e273_human_diary_state_jepa_audit_features.parquet"
E280_SUMMARY = OUT / "e280_story_transfer_alignment_summary.csv"
SOCIAL_FEATURES = OUT / "e268_human_social_story_features.parquet"
CASH_FEATURES = OUT / "e270_payday_cashflow_story_features.parquet"

E224 = OUT / "submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv"
E247 = OUT / "submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv"
E256 = OUT / "submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv"

SUMMARY_OUT = OUT / "e288_lifestyle_bundle_jepa_summary.csv"
STORY_OUT = OUT / "e288_lifestyle_bundle_story_recon.csv"
LABEL_OUT = OUT / "e288_lifestyle_bundle_label_stress.csv"
TARGET_OUT = OUT / "e288_lifestyle_bundle_target_detail.csv"
CLUSTER_OUT = OUT / "e288_lifestyle_bundle_cluster_diagnostics.csv"
BOUNDARY_OUT = OUT / "e288_lifestyle_bundle_boundary_alignment.csv"
NULL_OUT = OUT / "e288_lifestyle_bundle_nulls.csv"
REPORT_OUT = OUT / "e288_lifestyle_bundle_jepa_report.md"

RNG_SEED = 20260531 + 288
TOP_STORIES = 28
MAX_RAW_COLS = 260
N_REPS = 12


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def logit(x: np.ndarray) -> np.ndarray:
    p = clip_prob(x)
    return np.log(p / (1.0 - p))


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


def stable_seed(*parts: object) -> int:
    text = "|".join(str(p) for p in parts)
    digest = hashlib.sha1(text.encode("utf-8")).hexdigest()
    return RNG_SEED + int(digest[:8], 16) % 100000


def prep_dates(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in ["sleep_date", "lifelog_date"]:
        if col in out.columns:
            out[col] = pd.to_datetime(out[col]).dt.strftime("%Y-%m-%d")
    return out


def signed_log1p(s: pd.Series) -> pd.Series:
    x = pd.to_numeric(s, errors="coerce").fillna(0.0).astype(float)
    return np.sign(x) * np.log1p(np.abs(x))


def robust_z(s: pd.Series, train_mask: np.ndarray) -> pd.Series:
    x = signed_log1p(s).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    tr = x.iloc[train_mask]
    med = float(tr.median())
    q75 = float(tr.quantile(0.75))
    q25 = float(tr.quantile(0.25))
    scale = (q75 - q25) / 1.349
    if not np.isfinite(scale) or scale < 1.0e-9:
        scale = float(tr.std(ddof=0))
    if not np.isfinite(scale) or scale < 1.0e-9:
        return pd.Series(0.0, index=s.index)
    return ((x - med) / scale).replace([np.inf, -np.inf], 0.0).fillna(0.0)


def load_frames() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, pd.DataFrame]]:
    base = prep_dates(pd.read_parquet(E273_FEATURES)).sort_values(KEYS).reset_index(drop=True)
    raw = prep_dates(pd.read_parquet(E262_RAW)).sort_values(KEYS).reset_index(drop=True)
    stories = pd.read_csv(E280_SUMMARY).copy()
    stories = stories[stories["feature_available"].fillna(False)].copy()
    stories = stories.sort_values("transfer_survival_score", ascending=False).head(TOP_STORIES).reset_index(drop=True)
    feature_frames = {
        "human_social": prep_dates(pd.read_parquet(SOCIAL_FEATURES)).sort_values(KEYS).reset_index(drop=True),
        "cashflow": prep_dates(pd.read_parquet(CASH_FEATURES)).sort_values(KEYS).reset_index(drop=True),
    }
    if not base[KEYS].equals(raw[KEYS]):
        raise RuntimeError("E262 raw features do not align with E273 features")
    for source, frame in feature_frames.items():
        if not base[KEYS].equals(frame[KEYS]):
            raise RuntimeError(f"{source} story features do not align with E273 features")
    return base, raw, stories, feature_frames


def story_score(row: pd.Series, feature_frames: dict[str, pd.DataFrame]) -> pd.Series:
    frame = feature_frames[str(row["source"])]
    story_id = str(row["story_id"])
    candidates = [str(row.get("score_col", "")), f"{story_id}_subj_z", story_id, f"{story_id}_active"]
    for col in candidates:
        if col and col in frame.columns:
            return pd.to_numeric(frame[col], errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(0.0)
    raise RuntimeError(f"missing story score for {story_id}")


def build_story_matrix(base: pd.DataFrame, stories: pd.DataFrame, feature_frames: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame]:
    train_mask = base["split"].eq("train").to_numpy()
    cols: dict[str, pd.Series] = {}
    meta_rows = []
    used_names: set[str] = set()
    for row in stories.itertuples(index=False):
        srow = pd.Series(row._asdict())
        name = str(srow["story_id"])
        safe_name = name
        suffix = 2
        while safe_name in used_names:
            safe_name = f"{name}_{suffix}"
            suffix += 1
        used_names.add(safe_name)
        score = robust_z(story_score(srow, feature_frames), train_mask)
        cols[safe_name] = score.clip(-6.0, 6.0)
        meta_rows.append(
            {
                "story": safe_name,
                "source": srow["source"],
                "mapped_family": srow["mapped_family"],
                "human_story": srow["human_story"],
                "transfer_survival_score": srow["transfer_survival_score"],
                "e280_verdict": srow["e280_verdict"],
            }
        )
    return pd.DataFrame(cols, index=base.index), pd.DataFrame(meta_rows)


def numeric_context(df: pd.DataFrame, train_mask: np.ndarray, max_cols: int | None = None) -> pd.DataFrame:
    blocked = set(KEYS + TARGETS + ["split", "dateblock_group", "subject_id"])
    blocked.update(c for c in df.columns if c.endswith("_date_only"))
    cols = [c for c in df.columns if c not in blocked and pd.api.types.is_numeric_dtype(df[c])]
    series_by_col: dict[str, pd.Series] = {}
    for col in cols:
        x = pd.to_numeric(df[col], errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(0.0)
        if bool((x.iloc[train_mask] >= 0).all()) and float(x.iloc[train_mask].quantile(0.99)) > 10.0:
            x = signed_log1p(x)
        series_by_col[col] = x
    work = pd.DataFrame(series_by_col, index=df.index)
    std = work.iloc[train_mask].std(ddof=0).replace(0, np.nan).dropna()
    keep = std.sort_values(ascending=False).index.tolist()
    if max_cols is not None:
        keep = keep[:max_cols]
    work = work[keep].replace([np.inf, -np.inf], 0.0).fillna(0.0)
    return work


def build_context_views(base: pd.DataFrame, raw: pd.DataFrame) -> dict[str, pd.DataFrame]:
    train_mask = base["split"].eq("train").to_numpy()
    base_ctx = numeric_context(base, train_mask, max_cols=None)
    raw_ctx = numeric_context(raw, train_mask, max_cols=MAX_RAW_COLS)
    hybrid = pd.concat(
        [
            base_ctx.add_prefix("base__"),
            raw_ctx.iloc[:, : min(120, raw_ctx.shape[1])].add_prefix("raw__"),
        ],
        axis=1,
    )
    return {
        "family_jepa_context": base_ctx,
        "raw_human_context": raw_ctx,
        "hybrid_context": hybrid,
    }


def groups_for(df: pd.DataFrame, split_name: str) -> pd.Series:
    if split_name == "subject5":
        return df["subject_id"].astype(str)
    if split_name == "dateblock5":
        return df["dateblock_group"].astype(str)
    raise ValueError(split_name)


def folds_for(groups: pd.Series) -> list[tuple[np.ndarray, np.ndarray]]:
    n_splits = min(5, int(groups.nunique()))
    if n_splits < 2:
        raise RuntimeError("not enough groups for GroupKFold")
    return list(GroupKFold(n_splits=n_splits).split(np.zeros(len(groups)), groups=groups))


def oof_multi_ridge(x: pd.DataFrame, y: pd.DataFrame, groups: pd.Series) -> np.ndarray:
    pred = np.zeros(y.shape, dtype=np.float64)
    for tr_idx, va_idx in folds_for(groups):
        model = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), Ridge(alpha=12.0))
        model.fit(x.iloc[tr_idx], y.iloc[tr_idx])
        pred[va_idx] = model.predict(x.iloc[va_idx])
    return pred


def fit_predict_test(x_train: pd.DataFrame, y_train: pd.DataFrame, x_test: pd.DataFrame) -> np.ndarray:
    model = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), Ridge(alpha=12.0))
    model.fit(x_train, y_train)
    return np.asarray(model.predict(x_test), dtype=np.float64)


def base_label_matrix(df: pd.DataFrame) -> pd.DataFrame:
    pieces = []
    for col in ["weekday", "is_weekend", "subject_order", "lifelog_dom", "lifelog_month", "weekday_sin", "weekday_cos", "dom_sin", "dom_cos"]:
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            pieces.append(pd.to_numeric(df[col], errors="coerce").fillna(0.0).rename(col))
    subj = pd.get_dummies(df["subject_id"].astype(str), prefix="subj", dtype=float)
    return pd.concat(pieces + [subj], axis=1).replace([np.inf, -np.inf], 0.0).fillna(0.0)


def label_cv_loss(x: pd.DataFrame, y: np.ndarray, groups: pd.Series) -> float:
    pred = np.zeros(len(y), dtype=np.float64)
    for tr_idx, va_idx in folds_for(groups):
        y_tr = y[tr_idx]
        if len(np.unique(y_tr)) < 2:
            pred[va_idx] = float(np.mean(y_tr))
            continue
        model = make_pipeline(
            SimpleImputer(strategy="median"),
            StandardScaler(),
            LogisticRegression(C=0.35, max_iter=1200, solver="lbfgs"),
        )
        model.fit(x.iloc[tr_idx], y_tr)
        pred[va_idx] = model.predict_proba(x.iloc[va_idx])[:, 1]
    return float(log_loss(y, clip_prob(pred), labels=[0, 1]))


def shuffled_matrix(values: np.ndarray, mode: str, groups: pd.Series, rng: np.random.Generator) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64)
    if mode == "row":
        return arr[rng.permutation(len(arr))]
    out = arr.copy()
    for _, idx in groups.groupby(groups).groups.items():
        idx_arr = np.asarray(list(idx), dtype=int)
        if len(idx_arr) > 1:
            out[idx_arr] = arr[idx_arr][rng.permutation(len(idx_arr))]
    return out


def make_latent(pred_train: np.ndarray, pred_test: np.ndarray, n_components: int = 6) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, float]]:
    n_components = max(1, min(n_components, pred_train.shape[1], pred_train.shape[0] - 1))
    scaler = StandardScaler()
    z_train = scaler.fit_transform(pred_train)
    z_test = scaler.transform(pred_test)
    pca = PCA(n_components=n_components, random_state=RNG_SEED)
    train_lat = pca.fit_transform(z_train)
    test_lat = pca.transform(z_test)
    svals = np.linalg.svd(train_lat - train_lat.mean(axis=0, keepdims=True), compute_uv=False)
    if len(svals) == 0 or float(np.sum(svals**2)) <= 1.0e-12:
        participation = 0.0
        anisotropy = np.inf
    else:
        participation = float((np.sum(svals**2) ** 2) / np.sum(svals**4))
        anisotropy = float(np.max(svals) / max(np.min(svals), 1.0e-9))
    cols = [f"life_pc{i+1}" for i in range(n_components)]
    diag = {
        "latent_dims": float(n_components),
        "explained_var_sum": float(np.sum(pca.explained_variance_ratio_)),
        "participation_ratio": participation,
        "anisotropy": anisotropy,
    }
    return pd.DataFrame(train_lat, columns=cols), pd.DataFrame(test_lat, columns=cols), diag


def cluster_diagnostics(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    train_lat: pd.DataFrame,
    test_lat: pd.DataFrame,
    view_id: str,
    split_name: str,
) -> tuple[list[dict[str, object]], dict[int, np.ndarray], dict[int, np.ndarray]]:
    rows: list[dict[str, object]] = []
    train_clusters: dict[int, np.ndarray] = {}
    test_clusters: dict[int, np.ndarray] = {}
    for k in [4, 6, 8]:
        if len(train_lat) <= k:
            continue
        km = KMeans(n_clusters=k, random_state=stable_seed(view_id, split_name, k), n_init=20)
        tr = km.fit_predict(train_lat)
        te = km.predict(test_lat)
        train_clusters[k] = tr
        test_clusters[k] = te
        p = np.bincount(tr, minlength=k).astype(float)
        q = np.bincount(te, minlength=k).astype(float)
        p = p / max(p.sum(), 1.0)
        q = q / max(q.sum(), 1.0)
        js = float(jensenshannon(p + 1.0e-9, q + 1.0e-9, base=2.0))
        nmi_subject = float(normalized_mutual_info_score(train_df["subject_id"].astype(str), tr))
        ordered = train_df.assign(cluster=tr).sort_values(["subject_id", "lifelog_date"])
        same = []
        for _, g in ordered.groupby("subject_id"):
            vals = g["cluster"].to_numpy()
            if len(vals) > 1:
                same.extend((vals[1:] == vals[:-1]).astype(float).tolist())
        self_transition = float(np.mean(same)) if same else 0.0
        target_priors = {
            f"{t}_cluster_prior_std": float(train_df.assign(cluster=tr).groupby("cluster")[t].mean().std(ddof=0))
            for t in TARGETS
        }
        rows.append(
            {
                "view_id": view_id,
                "split": split_name,
                "k": k,
                "train_test_js": js,
                "subject_nmi": nmi_subject,
                "self_transition": self_transition,
                **target_priors,
            }
        )
    return rows, train_clusters, test_clusters


def evaluate_label_stress(
    train_df: pd.DataFrame,
    base_x: pd.DataFrame,
    latent_x: pd.DataFrame,
    clusters: dict[int, np.ndarray],
    view_id: str,
    split_name: str,
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    groups = groups_for(train_df, split_name).reset_index(drop=True)
    baseline_losses = {t: label_cv_loss(base_x, train_df[t].to_numpy(dtype=int), groups) for t in TARGETS}
    rows: list[dict[str, object]] = []
    target_rows: list[dict[str, object]] = []
    null_rows: list[dict[str, object]] = []

    reps: dict[str, pd.DataFrame] = {"pc": pd.concat([base_x.reset_index(drop=True), latent_x.reset_index(drop=True)], axis=1)}
    if 6 in clusters:
        cl = pd.get_dummies(pd.Series(clusters[6], name="life_cluster6").astype(str), prefix="life_c6", dtype=float)
        reps["cluster6"] = pd.concat([base_x.reset_index(drop=True), cl.reset_index(drop=True)], axis=1)

    mode_group = {
        "row": groups,
        "subject": groups_for(train_df, "subject5").reset_index(drop=True),
        "dateblock": groups_for(train_df, "dateblock5").reset_index(drop=True),
    }

    for rep_id, x in reps.items():
        deltas = []
        for target in TARGETS:
            y = train_df[target].to_numpy(dtype=int)
            loss = label_cv_loss(x, y, groups)
            delta = loss - baseline_losses[target]
            deltas.append(delta)
            target_rows.append(
                {
                    "view_id": view_id,
                    "split": split_name,
                    "rep": rep_id,
                    "target": target,
                    "base_loss": baseline_losses[target],
                    "rep_loss": loss,
                    "delta_logloss": delta,
                }
            )

        actual_mean = float(np.mean(deltas))
        actual_best = float(np.min(deltas))
        actual_worst = float(np.max(deltas))
        null_vals = []
        rng = np.random.default_rng(stable_seed(view_id, split_name, rep_id, "null"))
        for mode, mgroups in mode_group.items():
            for rep in range(N_REPS):
                if rep_id == "pc":
                    shuffled = shuffled_matrix(latent_x.to_numpy(), mode, mgroups, rng)
                    nx = pd.concat(
                        [base_x.reset_index(drop=True), pd.DataFrame(shuffled, columns=latent_x.columns)],
                        axis=1,
                    )
                else:
                    shuffled_cluster = shuffled_matrix(clusters[6].reshape(-1, 1), mode, mgroups, rng).ravel().astype(int)
                    cl = pd.get_dummies(pd.Series(shuffled_cluster).astype(str), prefix="life_c6", dtype=float)
                    nx = pd.concat([base_x.reset_index(drop=True), cl.reset_index(drop=True)], axis=1)
                    nx = nx.reindex(columns=x.columns, fill_value=0.0)
                losses = []
                for target in TARGETS:
                    y = train_df[target].to_numpy(dtype=int)
                    losses.append(label_cv_loss(nx, y, groups) - baseline_losses[target])
                null_mean = float(np.mean(losses))
                null_vals.append(null_mean)
                null_rows.append(
                    {
                        "view_id": view_id,
                        "split": split_name,
                        "rep": rep_id,
                        "mode": mode,
                        "null_rep": rep,
                        "null_delta_mean": null_mean,
                    }
                )
        null_arr = np.asarray(null_vals, dtype=np.float64)
        rows.append(
            {
                "view_id": view_id,
                "split": split_name,
                "rep": rep_id,
                "actual_delta_mean": actual_mean,
                "actual_delta_best": actual_best,
                "actual_delta_worst": actual_worst,
                "targets_improved": int(np.sum(np.asarray(deltas) < 0.0)),
                "null_q20": float(np.quantile(null_arr, 0.20)),
                "null_median": float(np.median(null_arr)),
                "null_best": float(np.min(null_arr)),
                "dominance": float(np.mean(actual_mean < null_arr)),
                "placebo_adjusted_vs_median": actual_mean - float(np.median(null_arr)),
                "placebo_adjusted_vs_best": actual_mean - float(np.min(null_arr)),
                "label_gate": bool(actual_mean < 0.0 and np.mean(actual_mean < null_arr) >= 0.85 and actual_worst < 0.004),
            }
        )
    return rows, target_rows, null_rows


def load_sub(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    for col in ["sleep_date", "lifelog_date"]:
        df[col] = pd.to_datetime(df[col]).dt.strftime("%Y-%m-%d")
    return df.sort_values(KEYS).reset_index(drop=True)


def boundary_alignment(base: pd.DataFrame, test_lat: pd.DataFrame, test_clusters: dict[int, np.ndarray], view_id: str, split_name: str) -> list[dict[str, object]]:
    if not (E224.exists() and E247.exists() and E256.exists()) or 6 not in test_clusters:
        return []
    e224 = load_sub(E224)
    e247 = load_sub(E247)
    e256 = load_sub(E256)
    test = base[base["split"].eq("test")].reset_index(drop=True)
    if not test[KEYS].equals(e247[KEYS]):
        return []
    d247 = np.abs(logit(e247["Q3"].to_numpy()) - logit(e224["Q3"].to_numpy()))
    d256 = np.abs(logit(e256["Q3"].to_numpy()) - logit(e247["Q3"].to_numpy()))
    c = test_clusters[6]
    rows = []
    for cluster in sorted(np.unique(c)):
        mask = c == cluster
        rows.append(
            {
                "view_id": view_id,
                "split": split_name,
                "cluster6": int(cluster),
                "n_test_rows": int(mask.sum()),
                "e247_q3_changed_rate": float(np.mean(d247[mask] > 1.0e-9)) if mask.any() else 0.0,
                "e256_vs_e247_q3_changed_rate": float(np.mean(d256[mask] > 1.0e-9)) if mask.any() else 0.0,
                "e247_q3_abs_logit_delta_mean": float(np.mean(d247[mask])) if mask.any() else 0.0,
                "e256_vs_e247_q3_abs_logit_delta_mean": float(np.mean(d256[mask])) if mask.any() else 0.0,
                "life_pc1_mean": float(test_lat.loc[mask, "life_pc1"].mean()) if "life_pc1" in test_lat.columns and mask.any() else 0.0,
            }
        )
    return rows


def write_report(
    summary: pd.DataFrame,
    story_recon: pd.DataFrame,
    label_stress: pd.DataFrame,
    target_detail: pd.DataFrame,
    cluster_diag: pd.DataFrame,
    boundary: pd.DataFrame,
    story_meta: pd.DataFrame,
) -> None:
    gates = label_stress[label_stress["label_gate"]].copy()
    lines = [
        "# E288 Lifestyle-Bundle JEPA Audit",
        "",
        "## Question",
        "",
        "Can multiple human/social stories form a hidden lifestyle state that is reconstructable from raw day context and useful for labels beyond matched nulls?",
        "",
        "## Story Bundle",
        "",
        f"- stories used: `{len(story_meta)}`",
        "- selected from E280 by transfer survival score, including mobility/commute, bright light, routine fragmentation, app entropy, heart stress, and cash-flow/payday stories.",
        "",
        md_table(story_meta[["story", "source", "mapped_family", "transfer_survival_score", "e280_verdict"]], n=30),
        "",
        "## Reconstruction Summary",
        "",
        md_table(summary.sort_values(["label_gate_any", "story_r2_mean"], ascending=[False, False]), n=20),
        "",
        "## Story-Level Reconstruction",
        "",
        md_table(story_recon.sort_values("r2", ascending=False), n=30),
        "",
        "## Label Stress",
        "",
        md_table(
            label_stress.sort_values(["label_gate", "actual_delta_mean"], ascending=[False, True])[
                [
                    "view_id",
                    "split",
                    "rep",
                    "actual_delta_mean",
                    "actual_delta_best",
                    "actual_delta_worst",
                    "targets_improved",
                    "null_median",
                    "null_best",
                    "dominance",
                    "label_gate",
                ]
            ],
            n=30,
        ),
        "",
        "## Best Target Deltas",
        "",
        md_table(target_detail.sort_values("delta_logloss"), n=30),
        "",
        "## Cluster Diagnostics",
        "",
        md_table(cluster_diag.sort_values(["train_test_js", "subject_nmi"]), n=30),
        "",
        "## E247/E256 Boundary Alignment",
        "",
        md_table(boundary.sort_values(["view_id", "split", "cluster6"]) if not boundary.empty else boundary, n=30),
        "",
        "## Decision",
        "",
    ]
    if gates.empty:
        lines.append("No lifestyle-bundle latent is submission-ready. Use the best surviving views as diagnostic state/energy only.")
    else:
        lines.append("At least one lifestyle-bundle latent passed the local label gate. It still requires a separate probability-materialization governor before public LB.")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This audit tests a bigger hidden object than a single story. A positive reconstruction score alone is not enough: the latent must also improve label CV and beat row/subject/dateblock shuffles. Failure means the lifestyle bundle may still describe human behavior, but it is not yet a safe probability editor.",
            "",
            "## Files",
            "",
            "- `e288_lifestyle_bundle_jepa_summary.csv`",
            "- `e288_lifestyle_bundle_story_recon.csv`",
            "- `e288_lifestyle_bundle_label_stress.csv`",
            "- `e288_lifestyle_bundle_target_detail.csv`",
            "- `e288_lifestyle_bundle_cluster_diagnostics.csv`",
            "- `e288_lifestyle_bundle_boundary_alignment.csv`",
            "- `e288_lifestyle_bundle_nulls.csv`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n")


def main() -> None:
    base, raw, stories, feature_frames = load_frames()
    story_matrix, story_meta = build_story_matrix(base, stories, feature_frames)
    views = build_context_views(base, raw)

    train_mask = base["split"].eq("train").to_numpy()
    train_df = base.loc[train_mask].reset_index(drop=True)
    test_df = base.loc[~train_mask].reset_index(drop=True)
    base_x = base_label_matrix(train_df).reset_index(drop=True)
    y_story = story_matrix.loc[train_mask].reset_index(drop=True)

    summary_rows: list[dict[str, object]] = []
    story_rows: list[dict[str, object]] = []
    label_rows: list[dict[str, object]] = []
    target_rows: list[dict[str, object]] = []
    null_rows: list[dict[str, object]] = []
    cluster_rows: list[dict[str, object]] = []
    boundary_rows: list[dict[str, object]] = []

    for view_id, context in views.items():
        x_train = context.loc[train_mask].reset_index(drop=True)
        x_test = context.loc[~train_mask].reset_index(drop=True)
        for split_name in ["subject5", "dateblock5"]:
            groups = groups_for(train_df, split_name).reset_index(drop=True)
            pred_train = oof_multi_ridge(x_train, y_story, groups)
            pred_test = fit_predict_test(x_train, y_story, x_test)
            r2_values = r2_score(y_story.to_numpy(), pred_train, multioutput="raw_values")
            r2_values = np.asarray(r2_values, dtype=np.float64)
            for story, r2v in zip(y_story.columns, r2_values):
                corr = 0.0
                yi = y_story[story].to_numpy(dtype=np.float64)
                pi = pred_train[:, list(y_story.columns).index(story)]
                if np.std(yi) > 1.0e-9 and np.std(pi) > 1.0e-9:
                    corr = float(np.corrcoef(yi, pi)[0, 1])
                smeta = story_meta[story_meta["story"].eq(story)].iloc[0].to_dict()
                story_rows.append(
                    {
                        "view_id": view_id,
                        "split": split_name,
                        "story": story,
                        "source": smeta["source"],
                        "mapped_family": smeta["mapped_family"],
                        "r2": float(r2v),
                        "corr": corr,
                    }
                )

            train_lat, test_lat, ldiag = make_latent(pred_train, pred_test)
            crows, train_clusters, test_clusters = cluster_diagnostics(train_df, test_df, train_lat, test_lat, view_id, split_name)
            cluster_rows.extend(crows)
            lrows, trows, nrows = evaluate_label_stress(train_df, base_x, train_lat, train_clusters, view_id, split_name)
            label_rows.extend(lrows)
            target_rows.extend(trows)
            null_rows.extend(nrows)
            boundary_rows.extend(boundary_alignment(base, test_lat, test_clusters, view_id, split_name))

            ldf = pd.DataFrame(lrows)
            summary_rows.append(
                {
                    "view_id": view_id,
                    "split": split_name,
                    "context_cols": int(context.shape[1]),
                    "story_count": int(y_story.shape[1]),
                    "story_r2_mean": float(np.mean(r2_values)),
                    "story_r2_median": float(np.median(r2_values)),
                    "story_r2_min": float(np.min(r2_values)),
                    "story_r2_positive_rate": float(np.mean(r2_values > 0.0)),
                    **ldiag,
                    "best_label_delta_mean": float(ldf["actual_delta_mean"].min()),
                    "label_gate_any": bool(ldf["label_gate"].any()),
                }
            )

    summary = pd.DataFrame(summary_rows)
    story_recon = pd.DataFrame(story_rows)
    label_stress = pd.DataFrame(label_rows)
    target_detail = pd.DataFrame(target_rows)
    nulls = pd.DataFrame(null_rows)
    cluster_diag = pd.DataFrame(cluster_rows)
    boundary = pd.DataFrame(boundary_rows)

    summary.to_csv(SUMMARY_OUT, index=False)
    story_recon.to_csv(STORY_OUT, index=False)
    label_stress.to_csv(LABEL_OUT, index=False)
    target_detail.to_csv(TARGET_OUT, index=False)
    nulls.to_csv(NULL_OUT, index=False)
    cluster_diag.to_csv(CLUSTER_OUT, index=False)
    boundary.to_csv(BOUNDARY_OUT, index=False)
    write_report(summary, story_recon, label_stress, target_detail, cluster_diag, boundary, story_meta)

    print(f"stories={len(story_meta)}")
    print(f"views={len(views)}")
    print(f"label_rows={len(label_stress)}")
    print(f"label_gate_rows={int(label_stress['label_gate'].sum()) if not label_stress.empty else 0}")
    print(f"best_label_delta={label_stress['actual_delta_mean'].min():.9f}" if not label_stress.empty else "best_label_delta=nan")
    print(f"report={REPORT_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
