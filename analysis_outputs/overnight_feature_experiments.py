from __future__ import annotations

import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import log_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

sys.path.append(str(Path(__file__).resolve().parent))
import calibration_experiments as cal  # noqa: E402
import deep_dive_analysis as d  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ITEMS = DATA / "ch2025_data_items"
OUT = ROOT / "analysis_outputs"
TARGETS = d.TARGETS
KEY = d.KEY


NIGHT_WINDOWS = {
    "overnight": (18, 36),
    "evening": (18, 21),
    "prebed": (21, 24),
    "after_midnight": (24, 36),
    "core_0_6": (24, 30),
    "core_0_8": (24, 32),
    "wake_6_12": (30, 36),
    "sleep_22_10": (22, 34),
}


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1 - 1e-5)


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([log_loss(y[:, j], clip(pred[:, j]), labels=[0, 1]) for j in range(y.shape[1])]))


def per_target_loss(y: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    return {target: log_loss(y[:, j], clip(pred[:, j]), labels=[0, 1]) for j, target in enumerate(TARGETS)}


def add_night_time(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["timestamp"] = pd.to_datetime(out["timestamp"])
    out["hour"] = out["timestamp"].dt.hour
    out["minute_of_day"] = out["hour"] * 60 + out["timestamp"].dt.minute
    base_date = out["timestamp"].dt.normalize()
    out["lifelog_date"] = np.where(out["hour"] < 12, base_date - pd.Timedelta(days=1), base_date)
    out["lifelog_date"] = pd.to_datetime(out["lifelog_date"])
    out["night_hour"] = np.where(out["hour"] < 12, out["hour"] + 24, out["hour"])
    out = out[(out["night_hour"] >= 18) & (out["night_hour"] < 36)].copy()
    return out


def prefix_cols(df: pd.DataFrame, prefix: str) -> pd.DataFrame:
    return df.rename(columns={c: f"{prefix}_{c}" for c in df.columns if c not in KEY})


def quantile_frame(grouped, col: str) -> pd.DataFrame:
    q = grouped[col].quantile([0.1, 0.9]).unstack()
    q.columns = ["q10", "q90"]
    return q


def numeric_night_aggregates(df: pd.DataFrame, value_cols: list[str], prefix: str) -> pd.DataFrame:
    blocks = []
    for win, (lo, hi) in NIGHT_WINDOWS.items():
        part = df[(df["night_hour"] >= lo) & (df["night_hour"] < hi)].copy()
        if part.empty:
            continue
        grouped = part.groupby(KEY)
        for col in value_cols:
            agg = grouped[col].agg(["count", "mean", "std", "min", "max", "sum", "median"])
            agg = agg.join(quantile_frame(grouped, col), how="left")
            tmp = part.assign(
                _is_zero=(part[col].fillna(0) <= 0).astype(float),
                _is_pos=(part[col].fillna(0) > 0).astype(float),
            )
            extra = tmp.groupby(KEY).agg(zero_frac=("_is_zero", "mean"), pos_frac=("_is_pos", "mean"))
            agg = agg.join(extra, how="left")
            blocks.append(prefix_cols(agg.reset_index(), f"night_{prefix}_{col}_{win}").set_index(KEY))
    if not blocks:
        return pd.DataFrame(columns=KEY)
    return pd.concat(blocks, axis=1).reset_index()


def run_features(df: pd.DataFrame, col: str, prefix: str) -> pd.DataFrame:
    rows = []
    part = df[(df["night_hour"] >= 18) & (df["night_hour"] < 36)].sort_values(KEY + ["night_hour", "minute_of_day"])
    for (sid, day), g in part.groupby(KEY, sort=False):
        vals = g[col].to_numpy()
        nh = g["night_hour"].to_numpy(dtype=float)
        transitions = float((vals[1:] != vals[:-1]).sum()) if len(vals) > 1 else 0.0
        active = vals > 0
        longest = 0
        cur = 0
        for v in active:
            cur = cur + 1 if v else 0
            longest = max(longest, cur)
        rows.append(
            {
                "subject_id": sid,
                "lifelog_date": day,
                f"night_{prefix}_transitions": transitions,
                f"night_{prefix}_active_frac": float(active.mean()) if len(active) else np.nan,
                f"night_{prefix}_first_active_hour": float(nh[active][0]) if active.any() else np.nan,
                f"night_{prefix}_last_active_hour": float(nh[active][-1]) if active.any() else np.nan,
                f"night_{prefix}_longest_active_run": float(longest),
                f"night_{prefix}_observations": float(len(vals)),
            }
        )
    return pd.DataFrame(rows)


def heart_rate_night_features() -> pd.DataFrame:
    df = add_night_time(pd.read_parquet(ITEMS / "ch2025_wHr.parquet"))

    def arr_stat(x):
        arr = np.asarray(x, dtype=float)
        if arr.size == 0:
            return (np.nan, np.nan, np.nan, np.nan, 0)
        return (float(np.nanmean(arr)), float(np.nanmin(arr)), float(np.nanmax(arr)), float(np.nanstd(arr)), int(arr.size))

    stats = pd.DataFrame(
        df["heart_rate"].map(arr_stat).tolist(),
        columns=["hr_mean", "hr_min", "hr_max", "hr_std", "hr_points"],
        index=df.index,
    )
    df = pd.concat([df[KEY + ["night_hour"]], stats], axis=1)
    return numeric_night_aggregates(df, ["hr_mean", "hr_min", "hr_max", "hr_std", "hr_points"], "hr")


def simple_numeric_features(file_name: str, cols: list[str], prefix: str) -> pd.DataFrame:
    df = add_night_time(pd.read_parquet(ITEMS / file_name))
    return numeric_night_aggregates(df, cols, prefix)


def wifi_ble_night_features(file_name: str, col: str, prefix: str) -> pd.DataFrame:
    df = add_night_time(pd.read_parquet(ITEMS / file_name))

    def scan_stats(items):
        ids = []
        rssis = []
        classes = []
        for item in items:
            if not isinstance(item, dict):
                continue
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

    stats = pd.DataFrame(
        df[col].map(scan_stats).tolist(),
        columns=["items", "unique_ids", "rssi_mean", "rssi_max", "unique_classes"],
        index=df.index,
    )
    df = pd.concat([df[KEY + ["night_hour"]], stats], axis=1)
    return numeric_night_aggregates(df, list(stats.columns), prefix)


def gps_night_features() -> pd.DataFrame:
    df = add_night_time(pd.read_parquet(ITEMS / "ch2025_mGps.parquet"))

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
    df = pd.concat([df[KEY + ["night_hour"]], rows], axis=1)
    return numeric_night_aggregates(df, list(rows.columns), "gps")


def usage_night_features() -> pd.DataFrame:
    df = add_night_time(pd.read_parquet(ITEMS / "ch2025_mUsageStats.parquet"))
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
    df = pd.concat([df[KEY + ["night_hour"]], rows], axis=1)
    return numeric_night_aggregates(df, list(rows.columns), "usage")


def ambience_night_features() -> pd.DataFrame:
    df = add_night_time(pd.read_parquet(ITEMS / "ch2025_mAmbience.parquet"))
    buckets = ["Speech", "Music", "Vehicle", "Inside", "Outside", "Silence", "Water", "Rain"]

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
        for bucket in buckets:
            out[f"top_is_{bucket.lower()}"] = float(bucket.lower() in lower)
        return out

    rows = pd.DataFrame(df["m_ambience"].map(top_stats).tolist(), index=df.index)
    df = pd.concat([df[KEY + ["night_hour"]], rows], axis=1)
    return numeric_night_aggregates(df, list(rows.columns), "ambience")


def build_overnight_features() -> pd.DataFrame:
    path = OUT / "overnight_sensor_features_v2.parquet"
    if path.exists():
        return pd.read_parquet(path)
    blocks = [
        simple_numeric_features("ch2025_mACStatus.parquet", ["m_charging"], "phone_charge"),
        simple_numeric_features("ch2025_mScreenStatus.parquet", ["m_screen_use"], "phone_screen"),
        simple_numeric_features("ch2025_mActivity.parquet", ["m_activity"], "phone_activity"),
        simple_numeric_features("ch2025_mLight.parquet", ["m_light"], "phone_light"),
        simple_numeric_features("ch2025_wLight.parquet", ["w_light"], "watch_light"),
        simple_numeric_features(
            "ch2025_wPedo.parquet",
            ["step", "step_frequency", "running_step", "walking_step", "distance", "speed", "burned_calories"],
            "watch_pedo",
        ),
        heart_rate_night_features(),
        run_features(add_night_time(pd.read_parquet(ITEMS / "ch2025_mScreenStatus.parquet")), "m_screen_use", "screen"),
        run_features(add_night_time(pd.read_parquet(ITEMS / "ch2025_mACStatus.parquet")), "m_charging", "charging"),
        wifi_ble_night_features("ch2025_mWifi.parquet", "m_wifi", "wifi"),
        wifi_ble_night_features("ch2025_mBle.parquet", "m_ble", "ble"),
        gps_night_features(),
        usage_night_features(),
        ambience_night_features(),
    ]
    out = blocks[0]
    for block in blocks[1:]:
        out = out.merge(block, on=KEY, how="outer")
    out.to_parquet(path, index=False)
    return out


def prepare() -> tuple[pd.DataFrame, pd.DataFrame]:
    train = pd.read_parquet(OUT / "train_deep_features.parquet")
    sub = pd.read_parquet(OUT / "submission_deep_features.parquet")
    night = build_overnight_features()
    night_cols = [c for c in night.columns if c not in KEY]
    train = train.merge(night, on=KEY, how="left")
    sub = sub.merge(night, on=KEY, how="left")
    # Explicit coverage: absence of mapped overnight records is often a sensor state.
    for frame in [train, sub]:
        frame["night_any_feature_present"] = frame[night_cols].notna().any(axis=1).astype(float)
        frame["night_feature_present_frac"] = frame[night_cols].notna().mean(axis=1).astype(float)
    return train, sub


def feature_columns(rows: pd.DataFrame, group: str) -> list[str]:
    excluded = set(TARGETS + KEY + ["sleep_date", "split"])
    base = [c for c in rows.columns if c not in excluded]
    calendar = ["subject_id", "dow", "month", "day", "weekofyear", "subject_day_index", "is_weekend"]
    night = [c for c in base if c.startswith("night_")]
    def unique(cols: list[str]) -> list[str]:
        seen = set()
        out = []
        for col in cols:
            if col in rows.columns and col not in seen:
                out.append(col)
                seen.add(col)
        return out

    if group == "overnight_all":
        return unique(calendar + night + ["night_any_feature_present", "night_feature_present_frac"])
    prefixes = {
        "overnight_watch": ("night_watch_", "night_hr_"),
        "overnight_phone": ("night_phone_", "night_screen_", "night_charging_", "night_usage_"),
        "overnight_motion": ("night_watch_pedo_", "night_phone_activity_"),
        "overnight_light": ("night_watch_light_", "night_phone_light_"),
        "overnight_context": ("night_wifi_", "night_ble_", "night_gps_", "night_usage_", "night_ambience_"),
        "overnight_mobility": ("night_wifi_", "night_ble_", "night_gps_"),
        "overnight_usage_ambience": ("night_usage_", "night_ambience_"),
    }
    if group in prefixes:
        keep = tuple(prefixes[group])
        return unique(calendar + [c for c in night if c.startswith(keep)] + ["night_any_feature_present", "night_feature_present_frac"])
    raise ValueError(group)


def make_pipeline(cols: list[str]) -> tuple[Pipeline, list[str]]:
    cat_cols = [c for c in cols if c in {"subject_id", "dow", "month"}]
    num_cols = [c for c in cols if c not in cat_cols]
    pre = ColumnTransformer(
        [
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
            ("num", SimpleImputer(strategy="median"), num_cols),
        ],
        sparse_threshold=0.2,
    )
    clf = ExtraTreesClassifier(
        n_estimators=240,
        min_samples_leaf=7,
        max_features=0.35,
        random_state=260526,
        n_jobs=-1,
    )
    return Pipeline([("pre", pre), ("clf", clf)]), cols


def proba_matrix(pipe: Pipeline, rows: pd.DataFrame, cols: list[str]) -> np.ndarray:
    probas = pipe.predict_proba(rows[cols])
    out = np.zeros((len(rows), len(TARGETS)), dtype=float)
    classes = pipe.named_steps["clf"].classes_
    for j, proba in enumerate(probas):
        if proba.shape[1] == 1:
            out[:, j] = float(classes[j][0] == 1)
        else:
            out[:, j] = proba[:, list(classes[j]).index(1)]
    return clip(out)


def fit_predict(train_rows: pd.DataFrame, rows: pd.DataFrame, group: str) -> np.ndarray:
    cols = feature_columns(train_rows, group)
    pipe, cols = make_pipeline(cols)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        pipe.fit(train_rows[cols], train_rows[TARGETS])
    return proba_matrix(pipe, rows, cols)


def oof_sensor(train: pd.DataFrame, group: str) -> np.ndarray:
    pred = np.zeros((len(train), len(TARGETS)), dtype=float)
    for fold_id, (tr_idx, val_idx) in enumerate(d.make_folds(train, "subject_blocks")):
        pred[val_idx] = fit_predict(train.iloc[tr_idx].copy(), train.iloc[val_idx].copy(), group)
        print(f"[overnight sensor] group={group} fold={fold_id}", flush=True)
    return clip(pred)


def optimize_blend(y: np.ndarray, base: np.ndarray, sensor: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    grid = np.array([0.0, 0.02, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30, 0.45, 0.60, 0.80, 1.00])
    weights = np.zeros(len(TARGETS), dtype=float)
    pred = base.copy()
    for j in range(len(TARGETS)):
        losses = []
        for w in grid:
            losses.append(log_loss(y[:, j], clip((1.0 - w) * base[:, j] + w * sensor[:, j]), labels=[0, 1]))
        weights[j] = float(grid[int(np.argmin(losses))])
        pred[:, j] = (1.0 - weights[j]) * base[:, j] + weights[j] * sensor[:, j]
    return weights, clip(pred)


def nested_blend(train: pd.DataFrame, group: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    y = train[TARGETS].to_numpy()
    pred_base = np.zeros_like(y, dtype=float)
    pred_sensor = np.zeros_like(y, dtype=float)
    pred_blend = np.zeros_like(y, dtype=float)
    weight_rows = []
    for fold_id, (tr_idx, val_idx) in enumerate(d.make_folds(train, "subject_blocks")):
        outer_train = train.iloc[tr_idx].copy().reset_index(drop=True)
        outer_val = train.iloc[val_idx].copy().reset_index(drop=True)
        inner_folds = d.make_folds(outer_train, "subject_blocks")
        inner_base = cal.base_oof(outer_train, inner_folds)
        inner_sensor = np.zeros_like(inner_base)
        for inner_id, (itr, iva) in enumerate(inner_folds):
            inner_sensor[iva] = fit_predict(outer_train.iloc[itr].copy(), outer_train.iloc[iva].copy(), group)
        weights, _ = optimize_blend(outer_train[TARGETS].to_numpy(), inner_base, inner_sensor)
        base_val = cal.temporal_base(outer_train, outer_val)
        sensor_val = fit_predict(outer_train, outer_val, group)
        pred_base[val_idx] = base_val
        pred_sensor[val_idx] = sensor_val
        pred_blend[val_idx] = clip((1.0 - weights) * base_val + weights * sensor_val)
        row = {"fold": fold_id, "group": group}
        row.update({f"w_{target}": weights[j] for j, target in enumerate(TARGETS)})
        weight_rows.append(row)
        print(f"[overnight nested] group={group} fold={fold_id} weights={weights}", flush=True)

    rows = []
    for name, pred in [("temporal_base", pred_base), ("sensor_only", pred_sensor), ("nested_blend", pred_blend)]:
        row = {"group": group, "model": name, "mean": mean_loss(y, pred)}
        row.update(per_target_loss(y, pred))
        rows.append(row)
    return pd.DataFrame(rows), pd.DataFrame(weight_rows)


def make_submission(train: pd.DataFrame, sub: pd.DataFrame, group: str, weights: pd.Series) -> pd.DataFrame:
    base = cal.temporal_base(train, sub)
    sensor = fit_predict(train, sub, group)
    w = np.asarray([weights[f"w_{target}"] for target in TARGETS], dtype=float)
    pred = clip((1.0 - w) * base + w * sensor)
    best_path = OUT / "submission_best.csv"
    if best_path.exists():
        out = pd.read_csv(best_path)
        best = out[TARGETS].to_numpy(dtype=float)
        # Only replace targets whose nested overnight weight is non-zero and whose
        # nested loss beats the current best target loss. The caller decides the group.
        for j, target in enumerate(TARGETS):
            if w[j] > 0:
                best[:, j] = pred[:, j]
        pred = best
    else:
        out = sub[["subject_id", "sleep_date", "lifelog_date"]].copy()
    for j, target in enumerate(TARGETS):
        out[target] = clip(pred[:, j])
    return out


def main() -> None:
    train, sub = prepare()
    groups = [
        "overnight_all",
        "overnight_watch",
        "overnight_phone",
        "overnight_motion",
        "overnight_light",
        "overnight_context",
        "overnight_mobility",
        "overnight_usage_ambience",
    ]
    all_rows = []
    all_weights = []
    for group in groups:
        print(f"[overnight] group={group}", flush=True)
        result, weights = nested_blend(train, group)
        all_rows.append(result)
        all_weights.append(weights)
    results = pd.concat(all_rows, ignore_index=True).sort_values(["mean", "group", "model"])
    weights = pd.concat(all_weights, ignore_index=True)
    results.to_csv(OUT / "overnight_nested_results.csv", index=False)
    weights.to_csv(OUT / "overnight_nested_weights.csv", index=False)
    print(results.round(6).to_string(index=False))
    print(weights.round(3).to_string(index=False))

    best_blend = results[results["model"].eq("nested_blend")].iloc[0]
    best_group = str(best_blend["group"])
    mean_weights = weights[weights["group"].eq(best_group)].filter(like="w_").mean()
    out = make_submission(train, sub, best_group, mean_weights)
    out.to_csv(OUT / "submission_overnight_blend.csv", index=False)
    print("wrote", OUT / "submission_overnight_blend.csv", "group", best_group)


if __name__ == "__main__":
    main()
