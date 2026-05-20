from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import ks_2samp, spearmanr
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.feature_selection import mutual_info_classif
from sklearn.impute import SimpleImputer
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler


DATA_DIR = Path("data")
ITEM_DIR = DATA_DIR / "ch2025_data_items"
OUT_DIR = Path("outputs/data_probe")
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, float) and math.isnan(value):
        return []
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, list):
        return value
    return []


def _entropy_from_counts(values: pd.Series) -> float:
    counts = values.value_counts(dropna=True)
    if counts.empty:
        return np.nan
    p = counts.to_numpy(dtype=float)
    p = p / p.sum()
    return float(-(p * np.log2(p + 1e-12)).sum())


def _daypart(hour: pd.Series) -> pd.Series:
    return pd.cut(
        hour,
        bins=[-1, 5, 11, 17, 21, 23],
        labels=["late_night", "morning", "afternoon", "evening", "night"],
    ).astype(str)


def _base_rows() -> pd.DataFrame:
    train = pd.read_csv(DATA_DIR / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    test = pd.read_csv(DATA_DIR / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    train["split"] = "train"
    test["split"] = "test"
    rows = pd.concat([train, test], ignore_index=True)
    rows["lifelog_date"] = rows["lifelog_date"].dt.date
    rows["sleep_date"] = rows["sleep_date"].dt.date
    rows["dow"] = pd.to_datetime(rows["lifelog_date"]).dt.dayofweek
    rows["is_weekend"] = rows["dow"].isin([5, 6]).astype(int)
    rows["subject_ord"] = rows["subject_id"].str.replace("id", "", regex=False).astype(int)
    first_date = rows.groupby("subject_id")["lifelog_date"].transform("min")
    rows["day_index_subject"] = (
        pd.to_datetime(rows["lifelog_date"]) - pd.to_datetime(first_date)
    ).dt.days.astype(int)
    return rows


def _merge_feature(base: pd.DataFrame, feat: pd.DataFrame) -> pd.DataFrame:
    return base.merge(feat, on=["subject_id", "lifelog_date"], how="left")


def scalar_time_features(file_name: str, value_cols: list[str], prefix: str) -> pd.DataFrame:
    df = pd.read_parquet(ITEM_DIR / file_name)
    df["lifelog_date"] = df["timestamp"].dt.date
    df["hour"] = df["timestamp"].dt.hour
    df["daypart"] = _daypart(df["hour"])
    group = df.groupby(["subject_id", "lifelog_date"], sort=False)
    out = group.size().rename(f"{prefix}_rows").reset_index()
    out[f"{prefix}_active_hours"] = group["hour"].nunique().to_numpy()
    out[f"{prefix}_hour_entropy"] = group["hour"].agg(_entropy_from_counts).to_numpy()
    for col in value_cols:
        ag = group[col].agg(["mean", "std", "min", "max", "median", "sum"])
        ag.columns = [f"{prefix}_{col}_{c}" for c in ag.columns]
        out = out.merge(ag.reset_index(), on=["subject_id", "lifelog_date"], how="left")
        for part in ["late_night", "morning", "afternoon", "evening", "night"]:
            part_mean = (
                df.loc[df["daypart"] == part]
                .groupby(["subject_id", "lifelog_date"])[col]
                .mean()
                .rename(f"{prefix}_{col}_{part}_mean")
                .reset_index()
            )
            out = out.merge(part_mean, on=["subject_id", "lifelog_date"], how="left")
    return out


def activity_features() -> pd.DataFrame:
    df = pd.read_parquet(ITEM_DIR / "ch2025_mActivity.parquet")
    df["lifelog_date"] = df["timestamp"].dt.date
    group = df.groupby(["subject_id", "lifelog_date"], sort=False)
    out = group.size().rename("mActivity_rows").reset_index()
    mode = group["m_activity"].agg(lambda s: s.mode().iloc[0] if not s.mode().empty else np.nan)
    out = out.merge(mode.rename("mActivity_mode").reset_index(), on=["subject_id", "lifelog_date"], how="left")
    counts = pd.crosstab([df["subject_id"], df["lifelog_date"]], df["m_activity"])
    counts.columns = [f"mActivity_class_{c}_cnt" for c in counts.columns]
    counts = counts.reset_index()
    out = out.merge(counts, on=["subject_id", "lifelog_date"], how="left")
    class_cols = [c for c in out.columns if c.startswith("mActivity_class_")]
    denom = out["mActivity_rows"].replace(0, np.nan)
    for col in class_cols:
        out[col.replace("_cnt", "_rate")] = out[col] / denom
    return out


def ambience_features(top_n: int = 25) -> pd.DataFrame:
    df = pd.read_parquet(ITEM_DIR / "ch2025_mAmbience.parquet")
    df["lifelog_date"] = df["timestamp"].dt.date
    rows = []
    label_totals: dict[str, int] = {}
    for row in df[["subject_id", "lifelog_date", "m_ambience"]].itertuples(index=False):
        items = _as_list(row.m_ambience)
        probs = []
        top_label = None
        top_prob = np.nan
        for item in items:
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                label, prob = str(item[0]), float(item[1])
                label_totals[label] = label_totals.get(label, 0) + 1
                probs.append(prob)
                if top_label is None:
                    top_label = label
                    top_prob = prob
        rows.append((row.subject_id, row.lifelog_date, len(items), top_label, top_prob, float(np.sum(probs)) if probs else np.nan))
    long = pd.DataFrame(rows, columns=["subject_id", "lifelog_date", "n_labels", "top_label", "top_prob", "prob_sum"])
    group = long.groupby(["subject_id", "lifelog_date"], sort=False)
    out = group.size().rename("mAmbience_rows").reset_index()
    for col in ["n_labels", "top_prob", "prob_sum"]:
        ag = group[col].agg(["mean", "std", "max"])
        ag.columns = [f"mAmbience_{col}_{c}" for c in ag.columns]
        out = out.merge(ag.reset_index(), on=["subject_id", "lifelog_date"], how="left")
    out["mAmbience_top_label_entropy"] = group["top_label"].agg(_entropy_from_counts).to_numpy()
    top_labels = sorted(label_totals, key=label_totals.get, reverse=True)[:top_n]
    for label in top_labels:
        part = (
            long.assign(hit=(long["top_label"] == label).astype(int))
            .groupby(["subject_id", "lifelog_date"])["hit"]
            .mean()
            .rename("mAmbience_top_" + "".join(ch if ch.isalnum() else "_" for ch in label)[:40] + "_rate")
            .reset_index()
        )
        out = out.merge(part, on=["subject_id", "lifelog_date"], how="left")
    return out


def list_device_features(file_name: str, list_col: str, id_key: str, prefix: str) -> pd.DataFrame:
    df = pd.read_parquet(ITEM_DIR / file_name)
    df["lifelog_date"] = df["timestamp"].dt.date
    rows = []
    for row in df[["subject_id", "lifelog_date", list_col]].itertuples(index=False):
        items = _as_list(getattr(row, list_col))
        ids = []
        rssis = []
        classes = []
        for item in items:
            if isinstance(item, dict):
                if id_key in item:
                    ids.append(str(item[id_key]))
                if "rssi" in item and item["rssi"] is not None:
                    rssis.append(float(item["rssi"]))
                if "device_class" in item:
                    classes.append(str(item["device_class"]))
        rows.append(
            (
                row.subject_id,
                row.lifelog_date,
                len(items),
                len(set(ids)),
                len(set(classes)),
                np.mean(rssis) if rssis else np.nan,
                np.max(rssis) if rssis else np.nan,
                np.min(rssis) if rssis else np.nan,
            )
        )
    long = pd.DataFrame(
        rows,
        columns=[
            "subject_id",
            "lifelog_date",
            f"{prefix}_scan_count",
            f"{prefix}_unique_count",
            f"{prefix}_class_unique_count",
            f"{prefix}_rssi_mean",
            f"{prefix}_rssi_max",
            f"{prefix}_rssi_min",
        ],
    )
    group = long.groupby(["subject_id", "lifelog_date"], sort=False)
    out = group.size().rename(f"{prefix}_rows").reset_index()
    for col in long.columns[2:]:
        ag = group[col].agg(["mean", "std", "max", "sum"])
        ag.columns = [f"{col}_{c}" for c in ag.columns]
        out = out.merge(ag.reset_index(), on=["subject_id", "lifelog_date"], how="left")
    return out


def gps_features() -> pd.DataFrame:
    df = pd.read_parquet(ITEM_DIR / "ch2025_mGps.parquet")
    df["lifelog_date"] = df["timestamp"].dt.date
    rows = []
    for row in df[["subject_id", "lifelog_date", "m_gps"]].itertuples(index=False):
        items = [x for x in _as_list(row.m_gps) if isinstance(x, dict)]
        speeds = [float(x["speed"]) for x in items if x.get("speed") is not None]
        lats = [float(x["latitude"]) for x in items if x.get("latitude") is not None]
        lons = [float(x["longitude"]) for x in items if x.get("longitude") is not None]
        alts = [float(x["altitude"]) for x in items if x.get("altitude") is not None]
        rows.append(
            (
                row.subject_id,
                row.lifelog_date,
                len(items),
                np.mean(speeds) if speeds else np.nan,
                np.max(speeds) if speeds else np.nan,
                np.std(speeds) if speeds else np.nan,
                np.std(lats) if lats else np.nan,
                np.std(lons) if lons else np.nan,
                np.mean(alts) if alts else np.nan,
                np.std(alts) if alts else np.nan,
            )
        )
    long = pd.DataFrame(
        rows,
        columns=[
            "subject_id",
            "lifelog_date",
            "gps_points",
            "gps_speed_mean",
            "gps_speed_max",
            "gps_speed_std",
            "gps_lat_std",
            "gps_lon_std",
            "gps_alt_mean",
            "gps_alt_std",
        ],
    )
    group = long.groupby(["subject_id", "lifelog_date"], sort=False)
    out = group.size().rename("mGps_rows").reset_index()
    for col in long.columns[2:]:
        ag = group[col].agg(["mean", "std", "max", "sum"])
        ag.columns = [f"{col}_{c}" for c in ag.columns]
        out = out.merge(ag.reset_index(), on=["subject_id", "lifelog_date"], how="left")
    return out


def usage_features(top_n: int = 30) -> pd.DataFrame:
    df = pd.read_parquet(ITEM_DIR / "ch2025_mUsageStats.parquet")
    df["lifelog_date"] = df["timestamp"].dt.date
    rows = []
    app_totals: dict[str, int] = {}
    for row in df[["subject_id", "lifelog_date", "m_usage_stats"]].itertuples(index=False):
        items = [x for x in _as_list(row.m_usage_stats) if isinstance(x, dict)]
        apps = [str(x.get("app_name", "")).strip() for x in items if x.get("app_name") is not None]
        times = [float(x.get("total_time", 0.0)) for x in items if x.get("total_time") is not None]
        for app in apps:
            if app:
                app_totals[app] = app_totals.get(app, 0) + 1
        rows.append((row.subject_id, row.lifelog_date, len(items), len(set(apps)), np.sum(times), np.max(times) if times else np.nan))
    long = pd.DataFrame(rows, columns=["subject_id", "lifelog_date", "app_events", "unique_apps", "app_total_time", "app_max_time"])
    group = long.groupby(["subject_id", "lifelog_date"], sort=False)
    out = group.size().rename("mUsage_rows").reset_index()
    for col in long.columns[2:]:
        ag = group[col].agg(["mean", "std", "max", "sum"])
        ag.columns = [f"mUsage_{col}_{c}" for c in ag.columns]
        out = out.merge(ag.reset_index(), on=["subject_id", "lifelog_date"], how="left")
    top_apps = sorted(app_totals, key=app_totals.get, reverse=True)[:top_n]
    for app in top_apps:
        safe = "".join(ch if ch.isalnum() else "_" for ch in app)[:40]
        hits = []
        for row in df[["subject_id", "lifelog_date", "m_usage_stats"]].itertuples(index=False):
            items = [x for x in _as_list(row.m_usage_stats) if isinstance(x, dict)]
            hit = any(str(x.get("app_name", "")).strip() == app for x in items)
            hits.append((row.subject_id, row.lifelog_date, int(hit)))
        part = pd.DataFrame(hits, columns=["subject_id", "lifelog_date", "hit"])
        part = part.groupby(["subject_id", "lifelog_date"])["hit"].mean().rename(f"mUsage_app_{safe}_rate").reset_index()
        out = out.merge(part, on=["subject_id", "lifelog_date"], how="left")
    return out


def hr_features() -> pd.DataFrame:
    df = pd.read_parquet(ITEM_DIR / "ch2025_wHr.parquet")
    df["lifelog_date"] = df["timestamp"].dt.date
    rows = []
    for row in df[["subject_id", "lifelog_date", "heart_rate"]].itertuples(index=False):
        vals = [float(x) for x in _as_list(row.heart_rate) if x is not None]
        rows.append(
            (
                row.subject_id,
                row.lifelog_date,
                len(vals),
                np.mean(vals) if vals else np.nan,
                np.std(vals) if vals else np.nan,
                np.min(vals) if vals else np.nan,
                np.max(vals) if vals else np.nan,
                np.percentile(vals, 10) if vals else np.nan,
                np.percentile(vals, 90) if vals else np.nan,
            )
        )
    long = pd.DataFrame(
        rows,
        columns=["subject_id", "lifelog_date", "hr_points", "hr_mean", "hr_std", "hr_min", "hr_max", "hr_p10", "hr_p90"],
    )
    group = long.groupby(["subject_id", "lifelog_date"], sort=False)
    out = group.size().rename("wHr_rows").reset_index()
    for col in long.columns[2:]:
        ag = group[col].agg(["mean", "std", "min", "max"])
        ag.columns = [f"{col}_{c}" for c in ag.columns]
        out = out.merge(ag.reset_index(), on=["subject_id", "lifelog_date"], how="left")
    return out


def build_features() -> pd.DataFrame:
    rows = _base_rows()
    features = [
        scalar_time_features("ch2025_mACStatus.parquet", ["m_charging"], "mAC"),
        activity_features(),
        ambience_features(),
        list_device_features("ch2025_mBle.parquet", "m_ble", "address", "mBle"),
        gps_features(),
        scalar_time_features("ch2025_mLight.parquet", ["m_light"], "mLight"),
        scalar_time_features("ch2025_mScreenStatus.parquet", ["m_screen_use"], "mScreen"),
        usage_features(),
        list_device_features("ch2025_mWifi.parquet", "m_wifi", "bssid", "mWifi"),
        hr_features(),
        scalar_time_features("ch2025_wLight.parquet", ["w_light"], "wLight"),
        scalar_time_features(
            "ch2025_wPedo.parquet",
            ["step", "step_frequency", "running_step", "walking_step", "distance", "speed", "burned_calories"],
            "wPedo",
        ),
    ]
    out = rows
    for feat in features:
        out = _merge_feature(out, feat)
    return out


def coverage_report(df: pd.DataFrame) -> pd.DataFrame:
    row_cols = [c for c in df.columns if c.endswith("_rows")]
    records = []
    for col in row_cols:
        modality = col[:-5]
        for split, part in df.groupby("split"):
            records.append(
                {
                    "modality": modality,
                    "split": split,
                    "n_rows": len(part),
                    "available_days": int(part[col].notna().sum()),
                    "availability_rate": float(part[col].notna().mean()),
                    "median_events": float(part[col].median(skipna=True)) if part[col].notna().any() else np.nan,
                    "mean_events": float(part[col].mean(skipna=True)) if part[col].notna().any() else np.nan,
                }
            )
    return pd.DataFrame(records).sort_values(["modality", "split"])


def label_report(df: pd.DataFrame) -> dict[str, Any]:
    train = df[df["split"] == "train"].copy()
    out: dict[str, Any] = {}
    out["target_rates"] = {t: float(train[t].mean()) for t in TARGETS}
    out["subject_target_rates"] = (
        train.groupby("subject_id")[TARGETS].mean().round(4).reset_index().to_dict(orient="records")
    )
    out["target_spearman"] = train[TARGETS].corr(method="spearman").round(4).to_dict()
    return out


def shift_report(df: pd.DataFrame) -> pd.DataFrame:
    feature_cols = _feature_cols(df)
    records = []
    train = df[df["split"] == "train"]
    test = df[df["split"] == "test"]
    for col in feature_cols:
        x = train[col].dropna().to_numpy(dtype=float)
        y = test[col].dropna().to_numpy(dtype=float)
        if len(x) < 10 or len(y) < 10:
            continue
        pooled = np.nanstd(np.r_[x, y])
        smd = (np.nanmean(y) - np.nanmean(x)) / pooled if pooled > 0 else 0.0
        ks = ks_2samp(x, y)
        records.append(
            {
                "feature": col,
                "train_mean": float(np.nanmean(x)),
                "test_mean": float(np.nanmean(y)),
                "smd_test_minus_train": float(smd),
                "ks_stat": float(ks.statistic),
                "ks_pvalue": float(ks.pvalue),
                "train_missing": float(train[col].isna().mean()),
                "test_missing": float(test[col].isna().mean()),
            }
        )
    return pd.DataFrame(records).sort_values(["ks_stat", "smd_test_minus_train"], ascending=[False, False]).head(60)


def _feature_cols(df: pd.DataFrame) -> list[str]:
    blocked = set(KEYS + TARGETS + ["split"])
    return [c for c in df.columns if c not in blocked and pd.api.types.is_numeric_dtype(df[c])]


def association_report(df: pd.DataFrame) -> pd.DataFrame:
    train = df[df["split"] == "train"].copy()
    feature_cols = _feature_cols(train)
    x = train[feature_cols]
    keep = x.notna().mean() >= 0.75
    feature_cols = keep[keep].index.tolist()
    imp = SimpleImputer(strategy="median")
    x_imp = pd.DataFrame(imp.fit_transform(train[feature_cols]), columns=feature_cols)
    records = []
    for target in TARGETS:
        y = train[target].astype(int).to_numpy()
        mi = mutual_info_classif(x_imp, y, random_state=42, discrete_features=False)
        for col, mi_val in zip(feature_cols, mi):
            corr = spearmanr(x_imp[col], y).correlation
            records.append({"target": target, "feature": col, "mi": float(mi_val), "spearman": float(corr) if corr == corr else np.nan})
    res = pd.DataFrame(records)
    return (
        res.assign(abs_spearman=res["spearman"].abs())
        .sort_values(["target", "mi", "abs_spearman"], ascending=[True, False, False])
        .groupby("target")
        .head(12)
        .reset_index(drop=True)
    )


def cluster_report(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    feature_cols = _feature_cols(df)
    missing_ok = df[feature_cols].notna().mean() >= 0.65
    feature_cols = missing_ok[missing_ok].index.tolist()
    x = SimpleImputer(strategy="median").fit_transform(df[feature_cols])
    x = StandardScaler().fit_transform(x)
    pca = PCA(n_components=min(12, x.shape[1]), random_state=42)
    z = pca.fit_transform(x)
    best = None
    rows = []
    for k in range(3, 9):
        labels = KMeans(n_clusters=k, random_state=42, n_init=20).fit_predict(z)
        sil = silhouette_score(z, labels)
        rows.append({"k": k, "silhouette": float(sil)})
        if best is None or sil > best[0]:
            best = (sil, k, labels)
    assert best is not None
    df2 = df[KEYS + ["split"] + TARGETS].copy()
    df2["cluster"] = best[2]
    cluster = (
        df2.groupby(["cluster", "split"])
        .agg(n=("subject_id", "size"), subjects=("subject_id", "nunique"))
        .reset_index()
    )
    train_rates = df2[df2["split"] == "train"].groupby("cluster")[TARGETS].mean().round(4).reset_index()
    cluster = cluster.merge(train_rates, on="cluster", how="left")
    pca_info = pd.DataFrame(
        {
            "component": [f"pc{i+1}" for i in range(len(pca.explained_variance_ratio_))],
            "explained_variance_ratio": pca.explained_variance_ratio_,
        }
    )
    pca_info["cumulative"] = pca_info["explained_variance_ratio"].cumsum()
    return pd.DataFrame(rows), cluster


def sensor_relationship_report(df: pd.DataFrame) -> pd.DataFrame:
    feature_cols = _feature_cols(df)
    row_cols = [c for c in feature_cols if c.endswith("_rows")]
    selected = row_cols + [
        c for c in feature_cols if any(key in c for key in ["screen_use_mean", "charging_mean", "step_sum", "hr_mean_mean", "gps_speed_mean_mean", "unique_count_mean", "app_total_time_sum", "light_mean"])
    ]
    selected = list(dict.fromkeys([c for c in selected if c in df.columns]))
    x = df[selected].copy()
    corr = x.corr(method="spearman", min_periods=80)
    records = []
    for i, a in enumerate(selected):
        for b in selected[i + 1 :]:
            val = corr.loc[a, b]
            if pd.notna(val):
                records.append({"feature_a": a, "feature_b": b, "spearman": float(val), "abs_spearman": abs(float(val))})
    return pd.DataFrame(records).sort_values("abs_spearman", ascending=False).head(80)


def markdown_table(frame: pd.DataFrame, max_rows: int | None = None) -> str:
    if frame.empty:
        return "_empty_"
    view = frame.head(max_rows).copy() if max_rows is not None else frame.copy()
    for col in view.columns:
        if pd.api.types.is_float_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else f"{x:.4g}")
        else:
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else str(x))
    cols = [str(c) for c in view.columns]
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for row in view.itertuples(index=False):
        lines.append("| " + " | ".join(str(x).replace("\n", " ") for x in row) + " |")
    return "\n".join(lines)


def write_report(
    df: pd.DataFrame,
    coverage: pd.DataFrame,
    labels: dict[str, Any],
    shift: pd.DataFrame,
    assoc: pd.DataFrame,
    sil: pd.DataFrame,
    clusters: pd.DataFrame,
    sensor_rel: pd.DataFrame,
) -> None:
    lines = []
    lines.append("# All-data utilization probe")
    lines.append("")
    lines.append("This is an EDA artifact, not a model-training report.")
    lines.append("")
    lines.append("## Inventory")
    lines.append(f"- Rows: {len(df)} total = {(df['split'] == 'train').sum()} train + {(df['split'] == 'test').sum()} test/unlabeled target rows")
    lines.append(f"- Subjects: {df['subject_id'].nunique()}")
    lines.append(f"- Numeric feature candidates created for all rows: {len(_feature_cols(df))}")
    lines.append("")
    lines.append("## Target rates")
    for target, rate in labels["target_rates"].items():
        lines.append(f"- {target}: {rate:.3f}")
    lines.append("")
    lines.append("## Most useful all-data routes")
    lines.extend(
        [
            "1. Build the sensor representation on all 700 subject-days, then train only the final supervised head on the 450 labeled days.",
            "2. Use all 700 rows for transductive preprocessing: feature vocabularies, robust scaling, PCA/clusters, missingness profiles, and train-test shift diagnostics.",
            "3. Convert each modality into self-supervised targets before using labels: next-hour activity/screen/charging prediction, masked sensor reconstruction, and cross-modal reconstruction.",
            "4. Use the 250 test rows as unlabeled distribution anchors for semi-supervised consistency or conservative pseudo-labeling, but keep pseudo labels gated by CV stability.",
            "5. Treat each subject as a short longitudinal panel: learn subject routines from every available lifelog day, then predict deviations from each person's own baseline.",
        ]
    )
    lines.append("")
    lines.append("## Coverage by modality")
    lines.append(markdown_table(coverage))
    lines.append("")
    lines.append("## Top train-test shifts")
    lines.append(markdown_table(shift, max_rows=20))
    lines.append("")
    lines.append("## Top feature-label associations")
    lines.append(markdown_table(assoc))
    lines.append("")
    lines.append("## Unsupervised clusters")
    lines.append("Silhouette by k:")
    lines.append(markdown_table(sil))
    lines.append("")
    lines.append("Cluster composition and train label rates:")
    lines.append(markdown_table(clusters))
    lines.append("")
    lines.append("## Strong sensor relationships")
    lines.append(markdown_table(sensor_rel, max_rows=30))
    lines.append("")
    lines.append("## Cautions")
    lines.extend(
        [
            "- Do not use test labels; submission_sample target zeros are placeholders.",
            "- Subject-level statistics can leak if computed with labels or fold-held rows. Unsupervised sensor-only statistics across all 700 rows are acceptable for transductive exploration but should be explicitly separated from supervised CV.",
            "- The target rows overlap in calendar time across train/test by subject, so validation must be temporal or grouped temporal, not random-only.",
        ]
    )
    (OUT_DIR / "all_data_probe_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = build_features()
    df.to_parquet(OUT_DIR / "all_subject_day_features.parquet", index=False)
    df.head(20).to_csv(OUT_DIR / "feature_preview.csv", index=False)

    coverage = coverage_report(df)
    labels = label_report(df)
    shift = shift_report(df)
    assoc = association_report(df)
    sil, clusters = cluster_report(df)
    sensor_rel = sensor_relationship_report(df)

    coverage.to_csv(OUT_DIR / "coverage_by_modality.csv", index=False)
    shift.to_csv(OUT_DIR / "train_test_shift_top.csv", index=False)
    assoc.to_csv(OUT_DIR / "feature_label_associations_top.csv", index=False)
    sil.to_csv(OUT_DIR / "cluster_silhouette.csv", index=False)
    clusters.to_csv(OUT_DIR / "cluster_summary.csv", index=False)
    sensor_rel.to_csv(OUT_DIR / "sensor_relationships_top.csv", index=False)
    (OUT_DIR / "label_summary.json").write_text(json.dumps(labels, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(df, coverage, labels, shift, assoc, sil, clusters, sensor_rel)

    print(f"wrote {OUT_DIR / 'all_data_probe_report.md'}")
    print(f"feature table shape: {df.shape}")
    print(f"numeric feature count: {len(_feature_cols(df))}")


if __name__ == "__main__":
    main()
