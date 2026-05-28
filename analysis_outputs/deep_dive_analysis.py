from __future__ import annotations

import json
import math
import warnings
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import entropy
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.model_selection import KFold, GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ITEMS = DATA / "ch2025_data_items"
OUT = ROOT / "analysis_outputs"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "lifelog_date"]

WINDOWS = {
    "all": (0, 24),
    "early": (0, 6),
    "morning": (6, 12),
    "afternoon": (12, 18),
    "evening": (18, 24),
    "late": (21, 24),
}


def read_labels() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    sub = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    train["split"] = "train"
    sub["split"] = "submission"
    all_keys = pd.concat(
        [train[KEY + ["sleep_date", "split"]], sub[KEY + ["sleep_date", "split"]]],
        ignore_index=True,
    ).sort_values(KEY)
    return train, sub, all_keys


def add_time_cols(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["lifelog_date"] = df["timestamp"].dt.normalize()
    df["hour"] = df["timestamp"].dt.hour
    df["minute_of_day"] = df["hour"] * 60 + df["timestamp"].dt.minute
    return df


def prefix_cols(df: pd.DataFrame, prefix: str) -> pd.DataFrame:
    return df.rename(columns={c: f"{prefix}_{c}" for c in df.columns if c not in KEY})


def numeric_aggregates(df: pd.DataFrame, value_cols: list[str], prefix: str) -> pd.DataFrame:
    blocks: list[pd.DataFrame] = []
    for win, (lo, hi) in WINDOWS.items():
        part = df[(df["hour"] >= lo) & (df["hour"] < hi)]
        if part.empty:
            continue
        for col in value_cols:
            agg = part.groupby(KEY)[col].agg(["count", "mean", "std", "min", "max", "sum", "median"])
            q = part.groupby(KEY)[col].quantile([0.1, 0.9]).unstack()
            q.columns = ["q10", "q90"]
            agg = agg.join(q, how="left")
            if col in {"m_light", "w_light"}:
                tmp = part.assign(
                    logv=np.log1p(part[col].clip(lower=0)),
                    zero=(part[col] <= 0).astype(float),
                    high=(part[col] > part[col].quantile(0.95)).astype(float),
                )
                extra = tmp.groupby(KEY).agg(log_mean=("logv", "mean"), zero_frac=("zero", "mean"), high_frac=("high", "mean"))
                agg = agg.join(extra, how="left")
            blocks.append(prefix_cols(agg.reset_index(), f"{prefix}_{col}_{win}").set_index(KEY))
    return pd.concat(blocks, axis=1).reset_index()


def binary_run_features(df: pd.DataFrame, col: str, prefix: str) -> pd.DataFrame:
    rows = []
    for (sid, day), g in df.sort_values("minute_of_day").groupby(KEY):
        vals = g[col].to_numpy()
        mins = g["minute_of_day"].to_numpy()
        on = vals == 1
        transitions = int(np.sum(vals[1:] != vals[:-1])) if len(vals) > 1 else 0
        if on.any():
            first_on = int(mins[on][0])
            last_on = int(mins[on][-1])
            longest = 0
            cur = 0
            for v in on:
                cur = cur + 1 if v else 0
                longest = max(longest, cur)
        else:
            first_on = -1
            last_on = -1
            longest = 0
        rows.append(
            {
                "subject_id": sid,
                "lifelog_date": day,
                f"{prefix}_transitions": transitions,
                f"{prefix}_first_on_min": first_on,
                f"{prefix}_last_on_min": last_on,
                f"{prefix}_longest_on_run": longest,
                f"{prefix}_observed_minutes": len(vals),
            }
        )
    return pd.DataFrame(rows)


def activity_features() -> pd.DataFrame:
    df = add_time_cols(pd.read_parquet(ITEMS / "ch2025_mActivity.parquet"))
    base = numeric_aggregates(df, ["m_activity"], "phone_activity")
    blocks = [base.set_index(KEY)]
    for win, (lo, hi) in WINDOWS.items():
        part = df[(df["hour"] >= lo) & (df["hour"] < hi)].copy()
        if part.empty:
            continue
        for v in sorted(df["m_activity"].unique()):
            part[f"v_{v}"] = (part["m_activity"] == v).astype(float)
        vals = [f"v_{v}" for v in sorted(df["m_activity"].unique())]
        frac = part.groupby(KEY)[vals].mean()
        frac = frac.rename(columns={c: f"phone_activity_{win}_frac_{c[2:]}" for c in frac.columns})
        ent = part.groupby(KEY)["m_activity"].value_counts(normalize=True).rename("p").reset_index()
        ent = ent.groupby(KEY)["p"].apply(lambda x: float(entropy(x))).rename(f"phone_activity_{win}_entropy")
        trans = (
            part.sort_values(KEY + ["minute_of_day"])
            .groupby(KEY)["m_activity"]
            .apply(lambda s: float((s.to_numpy()[1:] != s.to_numpy()[:-1]).sum()) if len(s) > 1 else 0.0)
            .rename(f"phone_activity_{win}_transitions")
        )
        blocks.extend([frac, ent, trans])
    return pd.concat(blocks, axis=1).reset_index()


def heart_rate_features() -> pd.DataFrame:
    df = add_time_cols(pd.read_parquet(ITEMS / "ch2025_wHr.parquet"))

    def arr_stat(x):
        arr = np.asarray(x, dtype=float)
        if arr.size == 0:
            return (np.nan, np.nan, np.nan, np.nan, 0)
        return (float(np.nanmean(arr)), float(np.nanmin(arr)), float(np.nanmax(arr)), float(np.nanstd(arr)), int(arr.size))

    stats = df["heart_rate"].map(arr_stat)
    stat_df = pd.DataFrame(stats.tolist(), columns=["hr_mean", "hr_min", "hr_max", "hr_std", "hr_points"], index=df.index)
    df = pd.concat([df[KEY + ["hour"]], stat_df], axis=1)
    blocks = []
    for win, (lo, hi) in WINDOWS.items():
        part = df[(df["hour"] >= lo) & (df["hour"] < hi)]
        if part.empty:
            continue
        agg = part.groupby(KEY).agg(
            rows=("hr_points", "count"),
            points=("hr_points", "sum"),
            mean=("hr_mean", "mean"),
            min=("hr_min", "min"),
            max=("hr_max", "max"),
            std_mean=("hr_std", "mean"),
            row_mean_std=("hr_mean", "std"),
        )
        blocks.append(prefix_cols(agg.reset_index(), f"hr_{win}").set_index(KEY))
    return pd.concat(blocks, axis=1).reset_index()


def nested_len_features(file_name: str, col: str, prefix: str) -> pd.DataFrame:
    df = add_time_cols(pd.read_parquet(ITEMS / file_name))
    df["list_len"] = df[col].map(lambda x: len(x) if hasattr(x, "__len__") else np.nan)
    blocks = []
    for win, (lo, hi) in WINDOWS.items():
        part = df[(df["hour"] >= lo) & (df["hour"] < hi)]
        if part.empty:
            continue
        agg = part.groupby(KEY)["list_len"].agg(["count", "mean", "std", "min", "max", "sum"])
        blocks.append(prefix_cols(agg.reset_index(), f"{prefix}_{win}").set_index(KEY))
    return pd.concat(blocks, axis=1).reset_index()


def wifi_ble_features(file_name: str, col: str, prefix: str) -> pd.DataFrame:
    df = add_time_cols(pd.read_parquet(ITEMS / file_name))

    def scan_stats(items):
        ids = []
        rssis = []
        classes = []
        for item in items:
            if isinstance(item, dict):
                ids.append(item.get("bssid") or item.get("address"))
                if item.get("rssi") is not None:
                    rssis.append(float(item["rssi"]))
                if item.get("device_class") is not None:
                    classes.append(str(item["device_class"]))
        return (
            len([x for x in ids if x]),
            len(set([x for x in ids if x])),
            np.nan if not rssis else float(np.mean(rssis)),
            np.nan if not rssis else float(np.max(rssis)),
            len(set(classes)),
        )

    stats = df[col].map(scan_stats)
    stat_df = pd.DataFrame(
        stats.tolist(),
        columns=["items", "unique_ids", "rssi_mean", "rssi_max", "unique_classes"],
        index=df.index,
    )
    df = pd.concat([df[KEY + ["hour"]], stat_df], axis=1)
    blocks = []
    for win, (lo, hi) in WINDOWS.items():
        part = df[(df["hour"] >= lo) & (df["hour"] < hi)]
        if part.empty:
            continue
        agg = part.groupby(KEY).agg(
            rows=("items", "count"),
            items_sum=("items", "sum"),
            items_mean=("items", "mean"),
            unique_mean=("unique_ids", "mean"),
            unique_max=("unique_ids", "max"),
            rssi_mean=("rssi_mean", "mean"),
            rssi_max=("rssi_max", "max"),
            class_mean=("unique_classes", "mean"),
        )
        blocks.append(prefix_cols(agg.reset_index(), f"{prefix}_{win}").set_index(KEY))
    return pd.concat(blocks, axis=1).reset_index()


def usage_features() -> pd.DataFrame:
    df = add_time_cols(pd.read_parquet(ITEMS / "ch2025_mUsageStats.parquet"))
    keywords = {
        "chat": ["카카오톡", "메시지", "Messenger", "LINE", "WhatsApp", "Telegram"],
        "call": ["전화", "통화"],
        "search": ["NAVER", "Chrome", "Google", "삼성 인터넷", "Safari"],
        "video": ["YouTube", "Netflix", "TikTok", "동영상"],
        "music": ["Music", "멜론", "Spotify", "YouTube Music"],
        "finance": ["토스", "KB", "카카오뱅크", "뱅크", "증권"],
        "home": ["One UI 홈", "Launcher"],
    }

    def stats(items):
        apps = []
        times = []
        bucket = {f"usage_kw_{k}_time": 0.0 for k in keywords}
        for item in items:
            if not isinstance(item, dict):
                continue
            app = str(item.get("app_name", ""))
            total = float(item.get("total_time") or 0.0)
            apps.append(app)
            times.append(total)
            for name, keys in keywords.items():
                if any(k.lower() in app.lower() for k in keys):
                    bucket[f"usage_kw_{name}_time"] += total
        out = {
            "apps": len(set(apps)),
            "items": len(apps),
            "time_sum": float(sum(times)),
            "time_max": float(max(times)) if times else 0.0,
        }
        out.update(bucket)
        return out

    rows = pd.DataFrame(df["m_usage_stats"].map(stats).tolist(), index=df.index)
    df = pd.concat([df[KEY + ["hour"]], rows], axis=1)
    blocks = []
    agg_cols = list(rows.columns)
    for win, (lo, hi) in WINDOWS.items():
        part = df[(df["hour"] >= lo) & (df["hour"] < hi)]
        if part.empty:
            continue
        agg = part.groupby(KEY)[agg_cols].agg(["count", "mean", "sum", "max"])
        agg.columns = [f"{a}_{b}" for a, b in agg.columns]
        blocks.append(prefix_cols(agg.reset_index(), f"usage_{win}").set_index(KEY))
    return pd.concat(blocks, axis=1).reset_index()


def ambience_features() -> pd.DataFrame:
    df = add_time_cols(pd.read_parquet(ITEMS / "ch2025_mAmbience.parquet"))
    buckets = ["Speech", "Music", "Vehicle", "Inside", "Outside", "Silence", "Animal", "Water", "Rain"]

    def top_stats(items):
        best_label = ""
        best_prob = -1.0
        for pair in items:
            try:
                label = str(pair[0])
                prob = float(pair[1])
            except Exception:
                continue
            if prob > best_prob:
                best_label = label
                best_prob = prob
        out = {"top_prob": np.nan if best_prob < 0 else best_prob}
        lower = best_label.lower()
        for b in buckets:
            out[f"top_is_{b.lower()}"] = float(b.lower() in lower)
        return out

    rows = pd.DataFrame(df["m_ambience"].map(top_stats).tolist(), index=df.index)
    df = pd.concat([df[KEY + ["hour"]], rows], axis=1)
    blocks = []
    for win, (lo, hi) in WINDOWS.items():
        part = df[(df["hour"] >= lo) & (df["hour"] < hi)]
        if part.empty:
            continue
        agg = part.groupby(KEY).agg(["count", "mean", "sum", "max"])
        agg.columns = [f"{a}_{b}" for a, b in agg.columns]
        blocks.append(prefix_cols(agg.reset_index(), f"ambience_{win}").set_index(KEY))
    return pd.concat(blocks, axis=1).reset_index()


def gps_features() -> pd.DataFrame:
    df = add_time_cols(pd.read_parquet(ITEMS / "ch2025_mGps.parquet"))

    def stats(items):
        speeds = []
        lats = []
        lons = []
        alts = []
        for item in items:
            if not isinstance(item, dict):
                continue
            if item.get("speed") is not None:
                speeds.append(float(item["speed"]))
            if item.get("latitude") is not None:
                lats.append(float(item["latitude"]))
            if item.get("longitude") is not None:
                lons.append(float(item["longitude"]))
            if item.get("altitude") is not None:
                alts.append(float(item["altitude"]))
        return (
            len(speeds),
            np.nan if not speeds else float(np.mean(speeds)),
            np.nan if not speeds else float(np.max(speeds)),
            np.nan if len(lats) < 2 else float(np.std(lats)),
            np.nan if len(lons) < 2 else float(np.std(lons)),
            np.nan if not alts else float(np.mean(alts)),
        )

    rows = pd.DataFrame(
        df["m_gps"].map(stats).tolist(),
        columns=["points", "speed_mean", "speed_max", "lat_std", "lon_std", "alt_mean"],
        index=df.index,
    )
    df = pd.concat([df[KEY + ["hour"]], rows], axis=1)
    blocks = []
    for win, (lo, hi) in WINDOWS.items():
        part = df[(df["hour"] >= lo) & (df["hour"] < hi)]
        if part.empty:
            continue
        agg = part.groupby(KEY).agg(
            rows=("points", "count"),
            points=("points", "sum"),
            speed_mean=("speed_mean", "mean"),
            speed_max=("speed_max", "max"),
            lat_std_mean=("lat_std", "mean"),
            lon_std_mean=("lon_std", "mean"),
            alt_mean=("alt_mean", "mean"),
        )
        blocks.append(prefix_cols(agg.reset_index(), f"gps_{win}").set_index(KEY))
    return pd.concat(blocks, axis=1).reset_index()


def build_sensor_features() -> pd.DataFrame:
    blocks = [
        numeric_aggregates(add_time_cols(pd.read_parquet(ITEMS / "ch2025_mACStatus.parquet")), ["m_charging"], "phone_charge"),
        numeric_aggregates(add_time_cols(pd.read_parquet(ITEMS / "ch2025_mScreenStatus.parquet")), ["m_screen_use"], "phone_screen"),
        numeric_aggregates(add_time_cols(pd.read_parquet(ITEMS / "ch2025_mLight.parquet")), ["m_light"], "phone_light"),
        numeric_aggregates(add_time_cols(pd.read_parquet(ITEMS / "ch2025_wLight.parquet")), ["w_light"], "watch_light"),
        numeric_aggregates(
            add_time_cols(pd.read_parquet(ITEMS / "ch2025_wPedo.parquet")),
            ["step", "step_frequency", "distance", "speed", "burned_calories"],
            "watch_pedo",
        ),
        activity_features(),
        heart_rate_features(),
        wifi_ble_features("ch2025_mWifi.parquet", "m_wifi", "wifi"),
        wifi_ble_features("ch2025_mBle.parquet", "m_ble", "ble"),
        usage_features(),
        ambience_features(),
        gps_features(),
        nested_len_features("ch2025_mAmbience.parquet", "m_ambience", "ambience_len"),
    ]
    out = blocks[0]
    for block in blocks[1:]:
        out = out.merge(block, on=KEY, how="outer")
    return out


def calendar_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df[KEY + ["sleep_date", "split"]].copy()
    out["dow"] = out["lifelog_date"].dt.dayofweek.astype(str)
    out["month"] = out["lifelog_date"].dt.month.astype(str)
    out["day"] = out["lifelog_date"].dt.day
    out["weekofyear"] = out["lifelog_date"].dt.isocalendar().week.astype(int)
    min_day = out.groupby("subject_id")["lifelog_date"].transform("min")
    out["subject_day_index"] = (out["lifelog_date"] - min_day).dt.days
    out["is_weekend"] = out["lifelog_date"].dt.dayofweek.isin([5, 6]).astype(int)
    return out


def build_base_matrix() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train, sub, all_keys = read_labels()
    feature_path = OUT / "deep_sensor_features.parquet"
    if feature_path.exists():
        sensor = pd.read_parquet(feature_path)
    else:
        sensor = build_sensor_features()
        sensor.to_parquet(feature_path, index=False)
    cal = calendar_features(all_keys)
    full = cal.merge(sensor, on=KEY, how="left")
    train_full = train.merge(full.drop(columns=["sleep_date", "split"]), on=KEY, how="left")
    sub_full = sub.merge(full.drop(columns=["sleep_date", "split"]), on=KEY, how="left")
    return train_full, sub_full, full


def make_folds(train: pd.DataFrame, kind: str, n_splits: int = 5) -> list[tuple[np.ndarray, np.ndarray]]:
    idx = np.arange(len(train))
    if kind == "random":
        return list(KFold(n_splits=n_splits, shuffle=True, random_state=42).split(idx))
    if kind == "group_subject":
        return list(GroupKFold(n_splits=n_splits).split(idx, groups=train["subject_id"]))
    if kind == "subject_blocks":
        folds = [[] for _ in range(n_splits)]
        for _, g in train.sort_values(["subject_id", "lifelog_date"]).groupby("subject_id"):
            locs = g.index.to_numpy()
            for fold, part in enumerate(np.array_split(locs, n_splits)):
                folds[fold].extend(part.tolist())
        out = []
        for val_ids in folds:
            val = np.array(sorted(val_ids))
            tr = np.setdiff1d(idx, val)
            out.append((tr, val))
        return out
    raise ValueError(kind)


def multilabel_logloss(y_true: pd.DataFrame | np.ndarray, y_pred: np.ndarray) -> float:
    y_arr = np.asarray(y_true)
    losses = []
    for j in range(y_arr.shape[1]):
        losses.append(log_loss(y_arr[:, j], np.clip(y_pred[:, j], 1e-5, 1 - 1e-5), labels=[0, 1]))
    return float(np.mean(losses))


def subject_prior_oof(train: pd.DataFrame, folds: list[tuple[np.ndarray, np.ndarray]], shrink: float = 8.0) -> np.ndarray:
    pred = np.zeros((len(train), len(TARGETS)))
    for tr_idx, val_idx in folds:
        tr = train.iloc[tr_idx]
        global_mean = tr[TARGETS].mean()
        subj_sum = tr.groupby("subject_id")[TARGETS].sum()
        subj_n = tr.groupby("subject_id").size()
        for row_pos in val_idx:
            sid = train.iloc[row_pos]["subject_id"]
            if sid in subj_sum.index:
                p = (subj_sum.loc[sid] + shrink * global_mean) / (subj_n.loc[sid] + shrink)
            else:
                p = global_mean
            pred[row_pos, :] = p.to_numpy(dtype=float)
    return np.clip(pred, 1e-4, 1 - 1e-4)


def temporal_label_features_for_fold(train: pd.DataFrame, ref: pd.DataFrame, target_rows: pd.DataFrame) -> pd.DataFrame:
    feats = target_rows[KEY].copy().reset_index(drop=True)
    for target in TARGETS:
        vals = []
        for _, row in target_rows.iterrows():
            sid = row["subject_id"]
            day = row["lifelog_date"]
            hist = ref[ref["subject_id"] == sid][["lifelog_date", target]].sort_values("lifelog_date")
            hist = hist[hist["lifelog_date"] != day]
            if hist.empty:
                vals.append({
                    f"hist_{target}_nearest": np.nan,
                    f"hist_{target}_nearest_dist": np.nan,
                    f"hist_{target}_prev": np.nan,
                    f"hist_{target}_prev_dist": np.nan,
                    f"hist_{target}_next": np.nan,
                    f"hist_{target}_next_dist": np.nan,
                    f"hist_{target}_near3_mean": np.nan,
                    f"hist_{target}_near5_mean": np.nan,
                })
                continue
            dist = (hist["lifelog_date"] - day).dt.days
            adist = dist.abs()
            order = np.argsort(adist.to_numpy())
            nearest = hist.iloc[order[0]]
            prev = hist[hist["lifelog_date"] < day]
            next_ = hist[hist["lifelog_date"] > day]
            near3 = hist.iloc[order[: min(3, len(order))]][target].mean()
            near5 = hist.iloc[order[: min(5, len(order))]][target].mean()
            vals.append({
                f"hist_{target}_nearest": nearest[target],
                f"hist_{target}_nearest_dist": int(adist.iloc[order[0]]),
                f"hist_{target}_prev": np.nan if prev.empty else prev.iloc[-1][target],
                f"hist_{target}_prev_dist": np.nan if prev.empty else int((day - prev.iloc[-1]["lifelog_date"]).days),
                f"hist_{target}_next": np.nan if next_.empty else next_.iloc[0][target],
                f"hist_{target}_next_dist": np.nan if next_.empty else int((next_.iloc[0]["lifelog_date"] - day).days),
                f"hist_{target}_near3_mean": near3,
                f"hist_{target}_near5_mean": near5,
            })
        feats = pd.concat([feats, pd.DataFrame(vals)], axis=1)
    return feats.drop(columns=KEY)


def temporal_label_oof(train: pd.DataFrame, folds: list[tuple[np.ndarray, np.ndarray]], shrink: float = 0.35) -> np.ndarray:
    pred = np.zeros((len(train), len(TARGETS)))
    for tr_idx, val_idx in folds:
        ref = train.iloc[tr_idx].copy()
        target_rows = train.iloc[val_idx].copy()
        subj_pred = subject_prior_oof(train.iloc[np.r_[tr_idx, val_idx]].reset_index(drop=True), [(np.arange(len(tr_idx)), np.arange(len(tr_idx), len(tr_idx) + len(val_idx)))])
        subj_pred = subj_pred[len(tr_idx):]
        hist = temporal_label_features_for_fold(train, ref, target_rows)
        for j, target in enumerate(TARGETS):
            cols = [
                f"hist_{target}_nearest",
                f"hist_{target}_prev",
                f"hist_{target}_next",
                f"hist_{target}_near3_mean",
                f"hist_{target}_near5_mean",
            ]
            dcols = [
                f"hist_{target}_nearest_dist",
                f"hist_{target}_prev_dist",
                f"hist_{target}_next_dist",
            ]
            local = hist[cols].mean(axis=1, skipna=True).to_numpy(dtype=float)
            dist = hist[dcols].min(axis=1, skipna=True).fillna(30).to_numpy(dtype=float)
            w = np.exp(-dist / 10.0) * shrink
            local = np.where(np.isnan(local), subj_pred[:, j], local)
            pred[val_idx, j] = (1 - w) * subj_pred[:, j] + w * local
    return np.clip(pred, 1e-4, 1 - 1e-4)


def add_temporal_history_features(train_part: pd.DataFrame, rows: pd.DataFrame) -> pd.DataFrame:
    hist = temporal_label_features_for_fold(train_part, train_part, rows)
    return pd.concat([rows.reset_index(drop=True), hist.reset_index(drop=True)], axis=1)


def model_oof(train: pd.DataFrame, folds: list[tuple[np.ndarray, np.ndarray]], feature_set: str, model_name: str) -> np.ndarray:
    base_exclude = set(TARGETS + ["sleep_date", "split"])
    if feature_set == "calendar_subject":
        cols = ["subject_id", "dow", "month", "day", "weekofyear", "subject_day_index", "is_weekend"]
    elif feature_set == "sensor":
        cols = [c for c in train.columns if c not in base_exclude and c not in KEY]
    elif feature_set == "sensor_history":
        cols = [c for c in train.columns if c not in base_exclude and c not in KEY]
    else:
        raise ValueError(feature_set)

    pred = np.zeros((len(train), len(TARGETS)))
    for tr_idx, val_idx in folds:
        tr = train.iloc[tr_idx].copy()
        val = train.iloc[val_idx].copy()
        if feature_set == "sensor_history":
            tr = add_temporal_history_features(tr, tr)
            val = add_temporal_history_features(tr, val)
            cols = [c for c in tr.columns if c not in base_exclude and c not in KEY]
        cat_cols = [c for c in cols if c in {"subject_id", "dow", "month"}]
        num_cols = [c for c in cols if c not in cat_cols]
        pre = ColumnTransformer(
            [
                ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
                ("num", Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), num_cols),
            ],
            sparse_threshold=0.1,
        )
        for j, target in enumerate(TARGETS):
            if model_name == "logreg":
                clf = LogisticRegression(max_iter=2000, C=0.2, solver="liblinear")
                pipe = Pipeline([("pre", pre), ("clf", clf)])
            elif model_name == "hgb":
                pipe = Pipeline(
                    [
                        ("pre", pre),
                        ("clf", HistGradientBoostingClassifier(max_iter=35, learning_rate=0.04, l2_regularization=1.0, random_state=100 + j)),
                    ]
                )
            elif model_name == "extratrees":
                pipe = Pipeline(
                    [
                        ("pre", pre),
                        (
                            "clf",
                            ExtraTreesClassifier(
                                n_estimators=120,
                                min_samples_leaf=10,
                                max_features=0.35,
                                random_state=200 + j,
                                n_jobs=1,
                            ),
                        ),
                    ]
                )
            else:
                raise ValueError(model_name)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                pipe.fit(tr[cols], tr[target])
            pred[val_idx, j] = pipe.predict_proba(val[cols])[:, 1]
    return np.clip(pred, 1e-4, 1 - 1e-4)


def target_signal_tables(train: pd.DataFrame) -> dict[str, pd.DataFrame]:
    rows = []
    feature_cols = [c for c in train.columns if c not in TARGETS + KEY + ["sleep_date", "split", "dow", "month"]]
    numeric = train[feature_cols].apply(pd.to_numeric, errors="coerce")
    centered = numeric.copy()
    for c in numeric.columns:
        centered[c] = numeric[c] - numeric.groupby(train["subject_id"])[c].transform("mean")
    for target in TARGETS:
        y = train[target] - train.groupby("subject_id")[target].transform("mean")
        for c in numeric.columns:
            if centered[c].notna().sum() < 50 or centered[c].std(skipna=True) == 0:
                continue
            r = centered[c].corr(y)
            if pd.notna(r):
                rows.append({"target": target, "feature": c, "subject_centered_corr": r, "abs_corr": abs(r)})
    corr = pd.DataFrame(rows).sort_values(["target", "abs_corr"], ascending=[True, False])

    subj = train.groupby("subject_id")[TARGETS].agg(["mean", "count"])
    subj.columns = [f"{a}_{b}" for a, b in subj.columns]
    return {"correlations": corr, "subject_target_rates": subj.reset_index()}


def split_and_autocorr_tables(train: pd.DataFrame, sub: pd.DataFrame) -> dict[str, pd.DataFrame]:
    chronology = []
    full = pd.concat(
        [train[KEY].assign(split="train"), sub[KEY].assign(split="submission")],
        ignore_index=True,
    ).sort_values(KEY)
    for sid, g in full.groupby("subject_id"):
        sequence = "".join("T" if x == "train" else "S" for x in g["split"])
        runs = []
        last = None
        n = 0
        for ch in sequence:
            if ch != last and last is not None:
                runs.append(f"{last}{n}")
                n = 0
            last = ch
            n += 1
        if last is not None:
            runs.append(f"{last}{n}")
        tr = g[g["split"] == "train"]["lifelog_date"]
        ss = g[g["split"] == "submission"]["lifelog_date"]
        chronology.append(
            {
                "subject_id": sid,
                "train_n": len(tr),
                "sub_n": len(ss),
                "train_min": tr.min(),
                "train_max": tr.max(),
                "sub_min": ss.min(),
                "sub_max": ss.max(),
                "sub_before_or_on_train_max": int((ss <= tr.max()).sum()),
                "train_after_or_on_sub_min": int((tr >= ss.min()).sum()),
                "runs": " ".join(runs),
            }
        )

    auto_rows = []
    for target in TARGETS:
        for sid, g in train.sort_values("lifelog_date").groupby("subject_id"):
            vals = g[target].to_numpy()
            if len(vals) < 5:
                continue
            for lag in [1, 2, 3, 5]:
                if len(vals) > lag and np.std(vals[:-lag]) > 0 and np.std(vals[lag:]) > 0:
                    r = np.corrcoef(vals[:-lag], vals[lag:])[0, 1]
                    same = np.mean(vals[:-lag] == vals[lag:])
                    auto_rows.append({"target": target, "subject_id": sid, "lag": lag, "corr": r, "same_rate": same})
    return {"chronology": pd.DataFrame(chronology), "target_autocorr": pd.DataFrame(auto_rows)}


def run_cv_experiments(train: pd.DataFrame) -> pd.DataFrame:
    rows = []
    y = train[TARGETS]
    for fold_kind in ["random", "subject_blocks", "group_subject"]:
        print(f"[cv] fold={fold_kind}", flush=True)
        folds = make_folds(train, fold_kind)
        global_pred = np.zeros((len(train), len(TARGETS)))
        for tr_idx, val_idx in folds:
            p = train.iloc[tr_idx][TARGETS].mean().to_numpy(dtype=float)
            global_pred[val_idx, :] = p
        rows.append({"fold": fold_kind, "features": "global_prior", "model": "mean", "logloss": multilabel_logloss(y, global_pred)})

        subj = subject_prior_oof(train, folds)
        rows.append({"fold": fold_kind, "features": "subject_prior", "model": "smoothed_mean", "logloss": multilabel_logloss(y, subj)})

        if fold_kind != "group_subject":
            print(f"[cv] fold={fold_kind} features=subject_temporal_target_history", flush=True)
            hist = temporal_label_oof(train, folds)
            rows.append({"fold": fold_kind, "features": "subject_temporal_target_history", "model": "kernel_mean", "logloss": multilabel_logloss(y, hist)})

        plan = [
            ("calendar_subject", "logreg"),
            ("sensor", "logreg"),
            ("sensor", "extratrees"),
        ]
        if fold_kind == "random":
            plan.append(("sensor", "hgb"))
        for feature_set, model in plan:
                print(f"[cv] fold={fold_kind} features={feature_set} model={model}", flush=True)
                pred = model_oof(train, folds, feature_set, model)
                rows.append({"fold": fold_kind, "features": feature_set, "model": model, "logloss": multilabel_logloss(y, pred)})
        if fold_kind != "group_subject":
            for model in ["logreg"]:
                print(f"[cv] fold={fold_kind} features=sensor_plus_history model={model}", flush=True)
                pred = model_oof(train, folds, "sensor_history", model)
                rows.append({"fold": fold_kind, "features": "sensor_plus_history", "model": model, "logloss": multilabel_logloss(y, pred)})
    return pd.DataFrame(rows).sort_values(["fold", "logloss"])


def write_report(
    train: pd.DataFrame,
    sub: pd.DataFrame,
    full: pd.DataFrame,
    cv: pd.DataFrame,
    signal: dict[str, pd.DataFrame],
    split: dict[str, pd.DataFrame],
) -> None:
    missing = train.drop(columns=TARGETS + ["sleep_date"]).isna().mean().sort_values(ascending=False).head(30)
    target_rates = train[TARGETS].mean().to_dict()
    cv_best = cv.groupby("fold").head(5)
    corr_top = signal["correlations"].groupby("target").head(8)
    auto = split["target_autocorr"].groupby(["target", "lag"]).agg(corr_mean=("corr", "mean"), same_rate_mean=("same_rate", "mean")).reset_index()
    report = [
        "# Deep Dive Findings",
        "",
        "## Inventory",
        f"- Train rows: {len(train)}, submission rows: {len(sub)}, feature rows: {len(full)}, feature columns: {train.shape[1] - len(TARGETS) - 3}",
        f"- Overall train positive rates: {json.dumps({k: round(float(v), 3) for k, v in target_rates.items()}, ensure_ascii=False)}",
        f"- Top missing feature rates: {json.dumps({k: round(float(v), 3) for k, v in missing.to_dict().items()}, ensure_ascii=False)}",
        "",
        "## Best CV Rows",
        "```",
        cv_best.to_string(index=False),
        "```",
        "",
        "## Split Chronology",
        "```",
        split["chronology"].to_string(index=False),
        "```",
        "",
        "## Target Autocorrelation",
        "```",
        auto.round(3).to_string(index=False),
        "```",
        "",
        "## Top Subject-Centered Feature Correlations",
        "```",
        corr_top[["target", "feature", "subject_centered_corr"]].round(3).to_string(index=False),
        "```",
    ]
    (OUT / "deep_dive_findings.md").write_text("\n".join(report), encoding="utf-8")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    train, sub, full = build_base_matrix()
    train.to_parquet(OUT / "train_deep_features.parquet", index=False)
    sub.to_parquet(OUT / "submission_deep_features.parquet", index=False)
    full.to_parquet(OUT / "all_keys_deep_features.parquet", index=False)

    signal = target_signal_tables(train)
    signal["correlations"].to_csv(OUT / "target_feature_correlations.csv", index=False)
    signal["subject_target_rates"].to_csv(OUT / "subject_target_rates.csv", index=False)

    split = split_and_autocorr_tables(train, sub)
    split["chronology"].to_csv(OUT / "split_chronology.csv", index=False)
    split["target_autocorr"].to_csv(OUT / "target_autocorr.csv", index=False)

    cv_path = OUT / "cv_logloss_results.csv"
    if cv_path.exists():
        cv = pd.read_csv(cv_path)
    else:
        cv = run_cv_experiments(train)
        cv.to_csv(cv_path, index=False)
    write_report(train, sub, full, cv, signal, split)
    print(cv.to_string(index=False))
    print(f"\nWrote analysis artifacts to {OUT}")


if __name__ == "__main__":
    main()
