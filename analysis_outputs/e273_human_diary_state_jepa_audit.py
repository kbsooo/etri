#!/usr/bin/env python3
"""E273: human diary state JEPA audit.

E269/E271 showed that individual social/cash-flow boundary probes are too
small to spend public LB. This experiment steps back and asks for a larger
hidden object:

Can all raw lifelog-derived human diary views be compressed into subject/block
lifestyle states, and do JEPA-style context-to-family residual energies explain
labels or the E247/E256 boundary under local stress?

No submission is created. The output is a promotion/diagnostic audit.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import adjusted_rand_score, log_loss, normalized_mutual_info_score, r2_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "analysis_outputs"

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]

HUMAN_PATH = OUT / "e262_human_social_day_features.parquet"
STORY_PATH = OUT / "e268_human_social_story_features.parquet"
CASH_PATH = OUT / "e270_payday_cashflow_story_features.parquet"

E247 = OUT / "submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv"
E256 = OUT / "submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv"
E267 = OUT / "submission_e267_humansocial_tail_balanced_2936100f.csv"
E224 = OUT / "submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv"

STATE_FEATURES_OUT = OUT / "e273_human_diary_state_jepa_audit_features.parquet"
FAMILY_OUT = OUT / "e273_human_diary_state_jepa_audit_family_summary.csv"
CV_OUT = OUT / "e273_human_diary_state_jepa_audit_cv.csv"
LABEL_OUT = OUT / "e273_human_diary_state_jepa_audit_label_lift.csv"
BOUNDARY_OUT = OUT / "e273_human_diary_state_jepa_audit_boundary.csv"
CLUSTER_OUT = OUT / "e273_human_diary_state_jepa_audit_clusters.csv"
REPORT_OUT = OUT / "e273_human_diary_state_jepa_audit_report.md"

RNG = 20260531 + 273


@dataclass(frozen=True)
class FamilySpec:
    name: str
    pattern: str
    story: str
    max_cols: int = 120


FAMILIES = [
    FamilySpec("social_comm", r"social_msg|call|speech|late_msg_call|presleep_msg_drag|public_social|social_isolation", "messaging, calls, speech, and passive social isolation"),
    FamilySpec("cognitive_money", r"finance|shopping|search_browser|work_study|late_search|cash|pay|bill|monthstart|money", "search, work, shopping, finance, and monthly cash-flow rumination"),
    FamilySpec("media_game", r"media|game|music|app_entropy|top_app_share|single_app|usage_day_total", "media, games, music, and attention entropy"),
    FamilySpec("bedtime_phone", r"screen|charge|mlight|wlight|phone_in_bed|deepnight_phone|bright_light|quiet_dark|sleep_onset|fragment", "bed phone use, charging, light, and sleep-onset fragmentation"),
    FamilySpec("mobility_context", r"gps|wifi|ble|ambience_inside_public|ambience_outside|ambience_vehicle|commute|night_out|outdoor|vehicle_noise|home_stability", "home/away, commute, public context, and environmental motion"),
    FamilySpec("physiology_activity", r"pedo|hr_|heart|physical|fatigue|low_hr|overtraining|sedentary", "steps, physical load, heart rate, and recovery/arousal"),
    FamilySpec("routine_calendar", r"religion|routine|ritual|weekday|weekend|is_weekend|home_stability|charge_bed_anchor", "ritual, weekend/workday rhythm, and stable routine"),
    FamilySpec("sensor_measurement", r"sensor_sparse|high_sensor|_count_|points_n|scan_n|wear", "device availability, sensor density, and measurement state"),
]


def md_table(frame: pd.DataFrame, n: int = 30, floatfmt: str = ".6f") -> str:
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


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def logit(x: np.ndarray) -> np.ndarray:
    p = clip_prob(x)
    return np.log(p / (1.0 - p))


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


def load_sub(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    for col in ["sleep_date", "lifelog_date"]:
        df[col] = pd.to_datetime(df[col]).dt.strftime("%Y-%m-%d")
    return df.sort_values(KEYS).reset_index(drop=True)


def normalize_dates(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in ["sleep_date", "lifelog_date"]:
        if col in out.columns:
            out[col] = pd.to_datetime(out[col]).dt.strftime("%Y-%m-%d")
    return out


def load_diary_frame() -> pd.DataFrame:
    human = normalize_dates(pd.read_parquet(HUMAN_PATH)).sort_values(KEYS).reset_index(drop=True)
    story = normalize_dates(pd.read_parquet(STORY_PATH)).sort_values(KEYS).reset_index(drop=True)
    cash = normalize_dates(pd.read_parquet(CASH_PATH)).sort_values(KEYS).reset_index(drop=True)
    base_cols = set(human.columns)

    keep_story = [
        c
        for c in story.columns
        if c in KEYS
        or (
            c not in base_cols
            and pd.api.types.is_numeric_dtype(story[c])
            and (c.endswith("_subj_z") or c.endswith("_weekend"))
        )
    ]
    occupied_cols = base_cols | (set(keep_story) - set(KEYS))
    keep_cash = [
        c
        for c in cash.columns
        if c in KEYS
        or (
            c not in occupied_cols
            and pd.api.types.is_numeric_dtype(cash[c])
            and (c.endswith("_subj_z") or c.endswith("_active"))
        )
    ]
    df = human.merge(story[keep_story], on=KEYS, how="left", validate="one_to_one")
    df = df.merge(cash[keep_cash], on=KEYS, how="left", validate="one_to_one")
    df["lifelog_dt"] = pd.to_datetime(df["lifelog_date"])
    df["subject_order"] = df.groupby("subject_id").cumcount().astype(int)
    df["dateblock_group"] = df["subject_id"].astype(str) + "_b" + (df["subject_order"] // 7).astype(str)
    df["lifelog_dom"] = df["lifelog_dt"].dt.day.astype(int)
    df["lifelog_month"] = df["lifelog_dt"].dt.month.astype(int)
    df["weekday_sin"] = np.sin(2.0 * np.pi * df["weekday"].astype(float) / 7.0)
    df["weekday_cos"] = np.cos(2.0 * np.pi * df["weekday"].astype(float) / 7.0)
    df["dom_sin"] = np.sin(2.0 * np.pi * df["lifelog_dom"].astype(float) / 31.0)
    df["dom_cos"] = np.cos(2.0 * np.pi * df["lifelog_dom"].astype(float) / 31.0)
    df["month_sin"] = np.sin(2.0 * np.pi * df["lifelog_month"].astype(float) / 12.0)
    df["month_cos"] = np.cos(2.0 * np.pi * df["lifelog_month"].astype(float) / 12.0)
    return df


def candidate_numeric_cols(df: pd.DataFrame) -> list[str]:
    meta = set(KEYS + TARGETS + [
        "lifelog_date_only",
        "sleep_date_only",
        "lifelog_dt",
        "split",
        "dateblock_group",
    ])
    cols = [
        c
        for c in df.columns
        if c not in meta
        and pd.api.types.is_numeric_dtype(df[c])
        and not c.endswith("_abs_subj_z")
    ]
    return cols


def family_columns(df: pd.DataFrame) -> dict[str, list[str]]:
    numeric = candidate_numeric_cols(df)
    out: dict[str, list[str]] = {}
    for spec in FAMILIES:
        pat = re.compile(spec.pattern, flags=re.IGNORECASE)
        cols = [c for c in numeric if pat.search(c)]
        out[spec.name] = sorted(set(cols))
    return out


def robust_feature_matrix(df: pd.DataFrame, cols: list[str], train_mask: np.ndarray, max_cols: int) -> tuple[np.ndarray, list[str]]:
    if not cols:
        return np.empty((len(df), 0), dtype=np.float64), []
    series_by_col: dict[str, pd.Series] = {}
    for col in cols:
        x = pd.to_numeric(df[col], errors="coerce").fillna(0.0).astype(float)
        tr = x.iloc[train_mask]
        if bool((tr >= 0).all()) and float(tr.quantile(0.99)) > 10.0:
            x = np.log1p(x)
        series_by_col[col] = x
    work = pd.DataFrame(series_by_col, index=df.index)
    tr_work = work.iloc[train_mask]
    std = tr_work.std(ddof=0).replace(0, np.nan)
    keep = std[std.notna()].sort_values(ascending=False).head(max_cols).index.tolist()
    work = work[keep].copy()
    med = work.iloc[train_mask].median(axis=0)
    q75 = work.iloc[train_mask].quantile(0.75, axis=0)
    q25 = work.iloc[train_mask].quantile(0.25, axis=0)
    scale = ((q75 - q25) / 1.349).replace(0, np.nan).fillna(work.iloc[train_mask].std(ddof=0)).replace(0, 1.0)
    z = ((work - med) / scale).replace([np.inf, -np.inf], 0.0).fillna(0.0)
    z = z.clip(-8.0, 8.0)
    return z.to_numpy(dtype=np.float64), keep


def build_family_embeddings(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, list[str]]]:
    train_mask = df["split"].eq("train").to_numpy()
    fam_cols = family_columns(df)
    meta_cols = list(dict.fromkeys(KEYS + [
        "split",
        "dateblock_group",
        "subject_order",
        "weekday",
        "is_weekend",
        "lifelog_dom",
        "lifelog_month",
        "weekday_sin",
        "weekday_cos",
        "dom_sin",
        "dom_cos",
        "month_sin",
        "month_cos",
        *TARGETS,
    ]))
    feature = df[meta_cols].copy()
    summary_rows: list[dict[str, object]] = []
    selected_cols: dict[str, list[str]] = {}
    for spec in FAMILIES:
        x, used = robust_feature_matrix(df, fam_cols.get(spec.name, []), train_mask, spec.max_cols)
        selected_cols[spec.name] = used
        if x.shape[1] == 0:
            summary_rows.append({"family": spec.name, "n_cols": 0, "n_pcs": 0, "story": spec.story})
            continue
        n_comp = int(min(4, x.shape[1], max(int(train_mask.sum()) - 1, 1)))
        pca = PCA(n_components=n_comp, random_state=RNG)
        pca.fit(x[train_mask])
        comps = pca.transform(x)
        for j in range(n_comp):
            feature[f"{spec.name}_pc{j + 1}"] = comps[:, j]
        feature[f"{spec.name}_energy"] = np.sqrt(np.mean(comps[:, :n_comp] ** 2, axis=1))
        summary_rows.append(
            {
                "family": spec.name,
                "n_cols": len(used),
                "n_pcs": n_comp,
                "explained_var_sum": float(np.sum(pca.explained_variance_ratio_)),
                "pc1_var": float(pca.explained_variance_ratio_[0]) if n_comp else 0.0,
                "story": spec.story,
                "top_cols": ",".join(used[:20]),
            }
        )
    return feature, pd.DataFrame(summary_rows), selected_cols


def group_oof_ridge(x: np.ndarray, y: np.ndarray, groups: np.ndarray) -> tuple[np.ndarray, float]:
    uniq = np.unique(groups)
    pred = np.zeros_like(y, dtype=np.float64)
    if len(uniq) < 2 or x.shape[1] == 0:
        pred[:] = y.mean(axis=0, keepdims=True)
        return pred, 0.0
    cv = GroupKFold(n_splits=min(5, len(uniq)))
    for tr_idx, va_idx in cv.split(x, groups=groups):
        model = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), Ridge(alpha=3.0))
        model.fit(x[tr_idx], y[tr_idx])
        pred[va_idx] = model.predict(x[va_idx])
    try:
        r2 = float(r2_score(y, pred, multioutput="variance_weighted"))
    except ValueError:
        r2 = 0.0
    return pred, r2


def add_jepa_residual_energy(features: pd.DataFrame, family_summary: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    out = features.copy()
    pc_cols_by_family: dict[str, list[str]] = {}
    for family in family_summary["family"].astype(str):
        cols = [c for c in out.columns if c.startswith(f"{family}_pc")]
        if cols:
            pc_cols_by_family[family] = cols
    rows: list[dict[str, object]] = []
    for family, target_cols in pc_cols_by_family.items():
        context_cols = [c for fam, cols in pc_cols_by_family.items() if fam != family for c in cols]
        x = out[context_cols].to_numpy(dtype=np.float64)
        y = out[target_cols].to_numpy(dtype=np.float64)
        for split_name, group_col in [("subject", "subject_id"), ("dateblock", "dateblock_group")]:
            pred, r2 = group_oof_ridge(x, y, out[group_col].astype(str).to_numpy())
            resid = y - pred
            out[f"jepa_resid_{split_name}_{family}"] = np.sqrt(np.mean(resid**2, axis=1))
            out[f"jepa_prednorm_{split_name}_{family}"] = np.sqrt(np.mean(pred**2, axis=1))
            rows.append(
                {
                    "family": family,
                    "split": split_name,
                    "context_cols": len(context_cols),
                    "target_dim": len(target_cols),
                    "oof_r2": r2,
                    "resid_mean": float(out[f"jepa_resid_{split_name}_{family}"].mean()),
                    "resid_train_mean": float(out.loc[out["split"].eq("train"), f"jepa_resid_{split_name}_{family}"].mean()),
                    "resid_test_mean": float(out.loc[out["split"].eq("test"), f"jepa_resid_{split_name}_{family}"].mean()),
                }
            )
    return out, pd.DataFrame(rows)


def add_global_state_and_clusters(features: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    out = features.copy()
    train_mask = out["split"].eq("train").to_numpy()
    state_cols = [
        c
        for c in out.columns
        if re.match(r".+_pc\d+$", c)
        or c.endswith("_energy")
        or c.startswith("jepa_resid_")
        or c.startswith("jepa_prednorm_")
    ]
    x = out[state_cols].to_numpy(dtype=np.float64)
    pipe = make_pipeline(SimpleImputer(strategy="median"), StandardScaler())
    pipe.fit(x[train_mask])
    z = pipe.transform(x)
    n_comp = min(10, z.shape[1], int(train_mask.sum()) - 1)
    pca = PCA(n_components=n_comp, random_state=RNG)
    pca.fit(z[train_mask])
    latent = pca.transform(z)
    for j in range(n_comp):
        out[f"diary_state_pc{j + 1}"] = latent[:, j]
    out["diary_state_energy"] = np.sqrt(np.mean(latent[:, : min(6, n_comp)] ** 2, axis=1))

    cluster_rows: list[dict[str, object]] = []
    for k in [4, 6, 8, 10]:
        model = KMeans(n_clusters=k, random_state=RNG + k, n_init=30)
        model.fit(latent[train_mask, : min(8, n_comp)])
        labels = model.predict(latent[:, : min(8, n_comp)])
        out[f"diary_state_k{k}"] = labels
        for c in range(k):
            out[f"diary_state_k{k}_{c}"] = (labels == c).astype(float)
        cluster_rows.append(
            {
                "k": k,
                "subject_nmi": normalized_mutual_info_score(out["subject_id"].astype(str), labels),
                "subject_ari": adjusted_rand_score(out["subject_id"].astype(str), labels),
                "test_cluster_entropy": entropy(np.bincount(labels[out["split"].eq("test")], minlength=k)),
                "train_cluster_entropy": entropy(np.bincount(labels[out["split"].eq("train")], minlength=k)),
                "self_transition_rate": self_transition_rate(out, labels),
                "pca_explained_var_first8": float(np.sum(pca.explained_variance_ratio_[: min(8, len(pca.explained_variance_ratio_))])),
            }
        )
    return out, pd.DataFrame(cluster_rows)


def entropy(counts: np.ndarray) -> float:
    arr = np.asarray(counts, dtype=np.float64)
    total = float(arr.sum())
    if total <= 0:
        return 0.0
    p = arr[arr > 0] / total
    return float(-(p * np.log(p + 1.0e-12)).sum())


def self_transition_rate(df: pd.DataFrame, labels: np.ndarray) -> float:
    ok = total = 0
    tmp = df[["subject_id", "lifelog_date"]].copy()
    tmp["_label"] = labels
    for _, group in tmp.sort_values(["subject_id", "lifelog_date"]).groupby("subject_id", sort=False):
        vals = group["_label"].to_numpy()
        if len(vals) < 2:
            continue
        total += len(vals) - 1
        ok += int(np.sum(vals[1:] == vals[:-1]))
    return float(ok / total) if total else 0.0


def cv_logloss_table(features: pd.DataFrame) -> pd.DataFrame:
    train = features[features["split"].eq("train")].copy().reset_index(drop=True)
    state_cols = [
        c
        for c in train.columns
        if c.startswith("diary_state_pc")
        or c.startswith("diary_state_energy")
        or c.startswith("jepa_resid_")
        or c.startswith("jepa_prednorm_")
        or c.startswith("diary_state_k8_")
    ]
    baseline_cols = ["weekday_sin", "weekday_cos", "is_weekend", "subject_order", "dom_sin", "dom_cos", "month_sin", "month_cos"]
    subject_dummies = pd.get_dummies(train["subject_id"].astype(str), prefix="sid", dtype=float)
    x_base = pd.concat([train[baseline_cols].astype(float), subject_dummies], axis=1)
    x_state = pd.concat([x_base, train[state_cols].astype(float)], axis=1)

    rows: list[dict[str, object]] = []
    split_defs = {
        "subject5": train["subject_id"].astype(str).to_numpy(),
        "dateblock5": train["dateblock_group"].astype(str).to_numpy(),
    }
    for split_name, groups in split_defs.items():
        n_splits = min(5, len(np.unique(groups)))
        cv = GroupKFold(n_splits=n_splits)
        for target in TARGETS:
            y = train[target].astype(int).to_numpy()
            pred_base = np.zeros(len(train), dtype=np.float64)
            pred_state = np.zeros(len(train), dtype=np.float64)
            for tr_idx, va_idx in cv.split(x_base, y, groups):
                pred_base[va_idx] = fit_logistic_predict(x_base.iloc[tr_idx], y[tr_idx], x_base.iloc[va_idx])
                pred_state[va_idx] = fit_logistic_predict(x_state.iloc[tr_idx], y[tr_idx], x_state.iloc[va_idx])
            loss_base = log_loss(y, clip_prob(pred_base), labels=[0, 1])
            loss_state = log_loss(y, clip_prob(pred_state), labels=[0, 1])
            rows.append(
                {
                    "split": split_name,
                    "target": target,
                    "loss_base": loss_base,
                    "loss_state": loss_state,
                    "delta_logloss": loss_state - loss_base,
                    "state_feature_count": len(state_cols),
                }
            )
    return pd.DataFrame(rows).sort_values(["delta_logloss", "split", "target"]).reset_index(drop=True)


def fit_logistic_predict(x_train: pd.DataFrame, y_train: np.ndarray, x_pred: pd.DataFrame) -> np.ndarray:
    if len(np.unique(y_train)) < 2:
        return np.full(len(x_pred), float(np.mean(y_train)), dtype=np.float64)
    model = make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(with_mean=False),
        LogisticRegression(C=0.25, solver="liblinear", max_iter=1000),
    )
    model.fit(x_train, y_train)
    return clip_prob(model.predict_proba(x_pred)[:, 1])


def label_lift(features: pd.DataFrame) -> pd.DataFrame:
    train = features[features["split"].eq("train")].copy()
    cols = [
        c
        for c in train.columns
        if c.startswith("diary_state_pc")
        or c.startswith("diary_state_energy")
        or c.startswith("jepa_resid_")
        or c.startswith("jepa_prednorm_")
        or c.endswith("_energy")
    ]
    rows: list[dict[str, object]] = []
    for col in cols:
        vals = pd.to_numeric(train[col], errors="coerce").fillna(0.0)
        if vals.nunique() < 5:
            continue
        lo = vals <= vals.quantile(0.25)
        hi = vals >= vals.quantile(0.75)
        if int(lo.sum()) < 12 or int(hi.sum()) < 12:
            continue
        for target in TARGETS:
            y = train[target].astype(float)
            rows.append(
                {
                    "feature": col,
                    "target": target,
                    "high_minus_low": float(y[hi].mean() - y[lo].mean()),
                    "abs_effect": float(abs(y[hi].mean() - y[lo].mean())),
                    "high_n": int(hi.sum()),
                    "low_n": int(lo.sum()),
                }
            )
    return pd.DataFrame(rows).sort_values(["abs_effect", "feature"], ascending=[False, True]).reset_index(drop=True)


def boundary_alignment(features: pd.DataFrame) -> pd.DataFrame:
    sample = features[features["split"].eq("test")].sort_values(KEYS).reset_index(drop=True)
    e247 = load_sub(E247)
    e256 = load_sub(E256)
    e224 = load_sub(E224)
    e267 = load_sub(E267)
    if not sample[KEYS].equals(e247[KEYS]):
        raise RuntimeError("test keys do not align with E247")
    l247 = logit(e247["Q3"].to_numpy())
    l256 = logit(e256["Q3"].to_numpy())
    l224 = logit(e224["Q3"].to_numpy())
    d247 = l247 - l224
    d256 = l256 - l224
    e247_only = (np.abs(d247) > 1.0e-10) & ~(np.abs(d256) > 1.0e-10)
    e256_only = (np.abs(d256) > 1.0e-10) & ~(np.abs(d247) > 1.0e-10)
    e267_move = np.abs(logit(e267[TARGETS].to_numpy()) - logit(e247[TARGETS].to_numpy())).max(axis=1) > 1.0e-12
    neutral = ~(e247_only | e256_only)
    cols = [
        c
        for c in sample.columns
        if c.startswith("diary_state_")
        or c.startswith("jepa_resid_")
        or c.startswith("jepa_prednorm_")
        or c.endswith("_energy")
    ]
    rows: list[dict[str, object]] = []
    for col in cols:
        vals = pd.to_numeric(sample[col], errors="coerce").fillna(0.0).to_numpy(dtype=np.float64)
        rows.append(
            {
                "feature": col,
                "e247_only_d_vs_neutral": cohen_d(vals[e247_only], vals[neutral]),
                "e256_only_d_vs_neutral": cohen_d(vals[e256_only], vals[neutral]),
                "e247_vs_e256_d": cohen_d(vals[e247_only], vals[e256_only]),
                "e267_moved_d_vs_neutral": cohen_d(vals[e267_move], vals[~e267_move]),
                "mean_e247_only": float(np.mean(vals[e247_only])) if e247_only.any() else np.nan,
                "mean_e256_only": float(np.mean(vals[e256_only])) if e256_only.any() else np.nan,
            }
        )
    out = pd.DataFrame(rows)
    out["abs_boundary_signal"] = out["e247_vs_e256_d"].abs()
    return out.sort_values(["abs_boundary_signal", "feature"], ascending=[False, True]).reset_index(drop=True)


def cluster_summary(features: pd.DataFrame, source: pd.DataFrame) -> pd.DataFrame:
    story_cols = [
        c
        for c in source.columns
        if c.endswith("_subj_z")
        and pd.api.types.is_numeric_dtype(source[c])
        and not c.endswith("_abs_subj_z")
    ]
    rows: list[dict[str, object]] = []
    labels = features["diary_state_k8"].astype(int).to_numpy()
    for cluster in sorted(np.unique(labels)):
        mask = labels == cluster
        train_mask = mask & features["split"].eq("train").to_numpy()
        test_mask = mask & features["split"].eq("test").to_numpy()
        rest = ~mask
        rec: dict[str, object] = {
            "cluster": int(cluster),
            "n_all": int(mask.sum()),
            "n_train": int(train_mask.sum()),
            "n_test": int(test_mask.sum()),
            "test_share": float(test_mask.sum() / max(mask.sum(), 1)),
            "dominant_subject": str(features.loc[mask, "subject_id"].mode().iloc[0]) if mask.any() else "",
        }
        for target in TARGETS:
            if train_mask.sum() > 0:
                rec[f"{target}_rate"] = float(features.loc[train_mask, target].mean())
        deltas = []
        for col in story_cols:
            vals = pd.to_numeric(source[col], errors="coerce").fillna(0.0).to_numpy(dtype=np.float64)
            deltas.append((col, float(np.mean(vals[mask]) - np.mean(vals[rest])) if rest.any() else 0.0))
        top = sorted(deltas, key=lambda x: abs(x[1]), reverse=True)[:8]
        rec["top_story_delta"] = "; ".join(f"{name}:{value:.2f}" for name, value in top)
        rows.append(rec)
    return pd.DataFrame(rows).sort_values(["n_all"], ascending=False).reset_index(drop=True)


def write_report(
    family_summary: pd.DataFrame,
    jepa_summary: pd.DataFrame,
    cluster_health: pd.DataFrame,
    cv: pd.DataFrame,
    lift: pd.DataFrame,
    boundary: pd.DataFrame,
    clusters: pd.DataFrame,
) -> None:
    cv_best = cv.sort_values("delta_logloss").head(10)
    cv_worst = cv.sort_values("delta_logloss", ascending=False).head(8)
    split_summary = (
        cv.groupby("split")["delta_logloss"]
        .agg(["mean", "min", "max"])
        .reset_index()
        .sort_values("mean")
    )
    target_summary = (
        cv.groupby("target")["delta_logloss"]
        .agg(["mean", "min", "max"])
        .reset_index()
        .sort_values("mean")
    )
    jepa_rank = jepa_summary.sort_values("oof_r2", ascending=False)
    lines = [
        "# E273 Human Diary State JEPA Audit",
        "",
        "## Question",
        "",
        "Can raw lifelog, social stories, and cash-flow stories form a larger hidden lifestyle state that is useful beyond tiny E247-boundary cell surgery?",
        "",
        "## Inputs",
        "",
        "- E262 raw day-level human/social features.",
        "- E268 explicit human story scores.",
        "- E270 payday/cash-flow story scores.",
        "- E247/E256/E267/E224 candidate geometry for boundary diagnostics.",
        "",
        "## Family Representations",
        "",
        md_table(family_summary[["family", "n_cols", "n_pcs", "explained_var_sum", "pc1_var", "story"]], n=20),
        "",
        "## JEPA Context -> Target Family Predictability",
        "",
        md_table(jepa_rank[["family", "split", "target_dim", "context_cols", "oof_r2", "resid_train_mean", "resid_test_mean"]], n=20),
        "",
        "Read: high OOF R2 means a family is predictable from the rest of the diary; high residual energy means a day violates the learned human-state expectation.",
        "",
        "## Cluster Health",
        "",
        md_table(cluster_health, n=20),
        "",
        "## Blocked CV Summary",
        "",
        "Diary-state features are added to a calendar/subject-order/subject-id baseline. Negative delta is good.",
        "",
        "### By Split",
        "",
        md_table(split_summary, n=10, floatfmt=".9f"),
        "",
        "### By Target",
        "",
        md_table(target_summary, n=10, floatfmt=".9f"),
        "",
        "### Best Target/Split Rows",
        "",
        md_table(cv_best, n=12, floatfmt=".9f"),
        "",
        "### Worst Target/Split Rows",
        "",
        md_table(cv_worst, n=12, floatfmt=".9f"),
        "",
        "## Strong Label Lifts",
        "",
        md_table(lift[["feature", "target", "high_minus_low", "abs_effect", "high_n", "low_n"]], n=25),
        "",
        "## E247/E256 Boundary Alignment",
        "",
        md_table(boundary[["feature", "e247_only_d_vs_neutral", "e256_only_d_vs_neutral", "e247_vs_e256_d", "e267_moved_d_vs_neutral", "abs_boundary_signal"]], n=25),
        "",
        "## Cluster Stories",
        "",
        md_table(clusters, n=12),
        "",
        "## Decision",
        "",
    ]
    date_mean = float(split_summary.loc[split_summary["split"].eq("dateblock5"), "mean"].iloc[0])
    subject_mean = float(split_summary.loc[split_summary["split"].eq("subject5"), "mean"].iloc[0])
    best_delta = float(cv["delta_logloss"].min())
    if date_mean < -0.001 and subject_mean <= 0.002:
        decision = "The lifestyle-state representation is alive as a larger hidden structure. It is not a submission yet, but it deserves a materialization experiment that changes more than 1e-5-scale boundary cells."
    elif best_delta < -0.006 and date_mean < 0.001:
        decision = "The signal is target/split-specific. Use it only for the targets with strong blocked CV wins; do not broad-blend it."
    else:
        decision = "The current diary-state construction is diagnostic rather than action-grade. It explains some labels and boundary cells but does not improve blocked CV enough to justify a submission."
    lines.extend([
        decision,
        "",
        f"- best target/split delta: `{best_delta:.9f}`",
        f"- dateblock mean delta: `{date_mean:.9f}`",
        f"- subject mean delta: `{subject_mean:.9f}`",
        "",
        "Next action: if alive, materialize only a larger target-specific candidate that passes E272 public-free promotion; otherwise rebuild the state representation with sharper subject/block priors.",
        "",
        "## Files",
        "",
        f"- `{STATE_FEATURES_OUT.name}`",
        f"- `{FAMILY_OUT.name}`",
        f"- `{CV_OUT.name}`",
        f"- `{LABEL_OUT.name}`",
        f"- `{BOUNDARY_OUT.name}`",
        f"- `{CLUSTER_OUT.name}`",
    ])
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    diary = load_diary_frame()
    family_features, family_summary, _ = build_family_embeddings(diary)
    state_features, jepa_summary = add_jepa_residual_energy(family_features, family_summary)
    state_features, cluster_health = add_global_state_and_clusters(state_features)
    cv = cv_logloss_table(state_features)
    lift = label_lift(state_features)
    boundary = boundary_alignment(state_features)
    clusters = cluster_summary(state_features, diary)

    state_features.to_parquet(STATE_FEATURES_OUT, index=False)
    pd.concat([family_summary.assign(section="family"), jepa_summary.assign(section="jepa")], ignore_index=True, sort=False).to_csv(FAMILY_OUT, index=False)
    cv.to_csv(CV_OUT, index=False)
    lift.to_csv(LABEL_OUT, index=False)
    boundary.to_csv(BOUNDARY_OUT, index=False)
    clusters.to_csv(CLUSTER_OUT, index=False)
    write_report(family_summary, jepa_summary, cluster_health, cv, lift, boundary, clusters)

    print(REPORT_OUT)
    print("[cv best]")
    print(cv.head(12).round(9).to_string(index=False))
    print("[boundary best]")
    print(boundary.head(12).round(6).to_string(index=False))


if __name__ == "__main__":
    main()
