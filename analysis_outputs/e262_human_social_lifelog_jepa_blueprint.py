#!/usr/bin/env python3
"""E262: human/social lifelog hypothesis inventory for JEPA design.

This experiment changes the unit of thought from "tabular feature" to
"human day".  It builds day-level lifestyle proxies from all raw logs and
maps them to falsifiable sleep hypotheses:

- social overstimulation
- routine stability
- workday/commute rhythm
- late cognitive load
- physical fatigue
- sleep-onset / fragmentation risk

It does not create a submission.  The output is a feature/probe atlas that can
become the target/context vocabulary for the next JEPA branch.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import math
import re
from typing import Any, Iterable

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RAW = DATA / "ch2025_data_items"
OUT = ROOT / "analysis_outputs"

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]

FEATURE_OUT = OUT / "e262_human_social_day_features.parquet"
FEATURE_CSV_OUT = OUT / "e262_human_social_day_features_preview.csv"
APP_INV_OUT = OUT / "e262_app_category_inventory.csv"
PROBE_OUT = OUT / "e262_human_social_hypothesis_probe.csv"
REPORT_OUT = OUT / "e262_human_social_lifelog_jepa_blueprint_report.md"


TIME_WINDOWS = {
    "day": (0, 24),
    "morning": (6, 12),
    "afternoon": (12, 18),
    "evening": (18, 22),
    "late": (22, 24),
    "deepnight": (0, 6),
    "presleep": (18, 24),
}

APP_CATEGORY_RULES: list[tuple[str, str]] = [
    ("social_msg", r"카카오톡|메시지|message|messenger|telegram|라인|밴드|instagram|facebook|discord|문자"),
    ("call", r"통화|전화|call|t전화"),
    ("religion_routine", r"성경|bible|교회|성당|찬송|기도|qt|일독"),
    ("search_browser", r"naver|chrome|google|safari|다음|daum|검색|browser|edge"),
    ("shopping", r"쿠팡|롯데on|11번가|g마켓|옥션|쇼핑|올리브영|배민|요기요|마켓컬리|ssg|무신사"),
    ("finance", r"토스|은행|뱅크|카드|pay|페이|증권|보험|하나|국민|신한|우리|농협|카카오뱅크"),
    ("media", r"youtube|유튜브|netflix|티빙|wavve|음악|music|멜론|지니|spotify|영상|tv"),
    ("game", r"게임|game|puzzle|royal|브롤|쿠키런|포켓몬"),
    ("health_walk", r"캐시워크|samsung health|헬스|건강|운동|만보기|fit"),
    ("work_study", r"메일|gmail|office|word|excel|pdf|zoom|teams|slack|class|학교|학습|공부|notion"),
    ("home_utility", r"one ui|홈|설정|시스템|launcher|날씨|시계|갤러리|카메라|calendar|캘린더"),
]

AMBIENCE_RULES: list[tuple[str, str]] = [
    ("speech", r"speech|conversation|narration|monologue"),
    ("music", r"music|song|jingle"),
    ("vehicle", r"vehicle|car|motor|train|subway|bus"),
    ("outside", r"outside|urban|rural|wind|traffic"),
    ("inside_public", r"public space|large room|hall|crowd"),
    ("animal_nature", r"animal|bird|leaves|livestock|wild"),
]


def normalize_app(name: Any) -> str:
    text = str(name).replace("\xa0", " ").strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def categorize_app(name: str) -> str:
    norm = normalize_app(name)
    for category, pattern in APP_CATEGORY_RULES:
        if re.search(pattern, norm, flags=re.IGNORECASE):
            return category
    return "other_app"


def time_window_flags(hour: int) -> list[str]:
    return [name for name, (lo, hi) in TIME_WINDOWS.items() if lo <= hour < hi]


def parse_records(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, float) and np.isnan(value):
        return []
    if isinstance(value, np.ndarray):
        return list(value)
    if isinstance(value, list):
        return value
    return []


def entropy_from_values(values: Iterable[float]) -> float:
    arr = np.asarray([v for v in values if v > 0], dtype=np.float64)
    total = float(arr.sum())
    if total <= 0:
        return 0.0
    p = arr / total
    return float(-(p * np.log(p + 1.0e-12)).sum())


def read_base() -> pd.DataFrame:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    train["split"] = "train"
    sample["split"] = "test"
    base = pd.concat([train[KEYS + TARGETS + ["split"]], sample[KEYS + TARGETS + ["split"]]], ignore_index=True)
    base = base.sort_values(KEYS).reset_index(drop=True)
    base["lifelog_date_only"] = base["lifelog_date"].dt.date
    base["sleep_date_only"] = base["sleep_date"].dt.date
    base["weekday"] = base["lifelog_date"].dt.weekday
    base["is_weekend"] = base["weekday"].isin([5, 6]).astype(float)
    return base


def empty_feature_frame(base: pd.DataFrame) -> pd.DataFrame:
    return base[KEYS + ["lifelog_date_only", "split", "weekday", "is_weekend"] + TARGETS].copy()


def add_usage_features(features: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.read_parquet(RAW / "ch2025_mUsageStats.parquet")
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    rows = []
    app_counter: Counter[tuple[str, str]] = Counter()
    app_time: Counter[tuple[str, str]] = Counter()
    for rec in df.itertuples(index=False):
        subject = rec.subject_id
        ts = rec.timestamp
        date = ts.date()
        hour = int(ts.hour)
        for item in parse_records(rec.m_usage_stats):
            try:
                app_name = normalize_app(item.get("app_name", ""))
                total_time = float(item.get("total_time", 0.0))
            except AttributeError:
                continue
            if not app_name or total_time <= 0:
                continue
            category = categorize_app(app_name)
            app_counter[(app_name, category)] += 1
            app_time[(app_name, category)] += total_time
            for window in time_window_flags(hour):
                rows.append(
                    {
                        "subject_id": subject,
                        "lifelog_date_only": date,
                        "window": window,
                        "category": category,
                        "app_name": app_name,
                        "total_time": total_time,
                    }
                )
    usage = pd.DataFrame(rows)
    if usage.empty:
        return features, pd.DataFrame()

    cat = (
        usage.groupby(["subject_id", "lifelog_date_only", "window", "category"], observed=True)["total_time"]
        .sum()
        .reset_index()
    )
    wide = cat.pivot_table(
        index=["subject_id", "lifelog_date_only"],
        columns=["window", "category"],
        values="total_time",
        fill_value=0.0,
        aggfunc="sum",
    )
    wide.columns = [f"usage_{w}_{c}_time" for w, c in wide.columns]
    wide = wide.reset_index()

    day_app = usage[usage["window"].eq("day")]
    total = day_app.groupby(["subject_id", "lifelog_date_only"])["total_time"].sum().rename("usage_day_total_time")
    entropy = day_app.groupby(["subject_id", "lifelog_date_only"])["total_time"].apply(entropy_from_values).rename("usage_day_app_entropy")
    top_share = (
        day_app.groupby(["subject_id", "lifelog_date_only", "app_name"])["total_time"].sum()
        .groupby(level=[0, 1])
        .apply(lambda s: float(s.max() / max(s.sum(), 1.0e-12)))
        .rename("usage_day_top_app_share")
    )
    extra = pd.concat([total, entropy, top_share], axis=1).reset_index()
    wide = wide.merge(extra, on=["subject_id", "lifelog_date_only"], how="outer").fillna(0.0)

    app_rows = []
    for (app_name, category), count in app_counter.items():
        app_rows.append(
            {
                "app_name": app_name,
                "category": category,
                "event_count": int(count),
                "total_time": float(app_time[(app_name, category)]),
            }
        )
    app_inv = pd.DataFrame(app_rows).sort_values(["total_time", "event_count"], ascending=False).reset_index(drop=True)
    features = features.merge(wide, on=["subject_id", "lifelog_date_only"], how="left")
    return features, app_inv


def numeric_window_agg(path: Path, value_cols: list[str], prefix: str, list_col: str | None = None) -> pd.DataFrame:
    df = pd.read_parquet(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    records = []
    for rec in df.itertuples(index=False):
        subject = rec.subject_id
        ts = rec.timestamp
        hour = int(ts.hour)
        date = ts.date()
        values: dict[str, float] = {}
        if list_col is not None:
            arr = parse_records(getattr(rec, list_col))
            flat = []
            for x in arr:
                try:
                    flat.append(float(x))
                except (TypeError, ValueError):
                    pass
            if flat:
                values[f"{list_col}_mean"] = float(np.mean(flat))
                values[f"{list_col}_min"] = float(np.min(flat))
                values[f"{list_col}_max"] = float(np.max(flat))
                values[f"{list_col}_std"] = float(np.std(flat))
        else:
            for col in value_cols:
                try:
                    values[col] = float(getattr(rec, col))
                except (TypeError, ValueError):
                    continue
        if not values:
            continue
        for window in time_window_flags(hour):
            row = {"subject_id": subject, "lifelog_date_only": date, "window": window}
            row.update(values)
            records.append(row)
    long = pd.DataFrame(records)
    if long.empty:
        return long
    agg_cols = [c for c in long.columns if c not in {"subject_id", "lifelog_date_only", "window"}]
    parts = []
    for col in agg_cols:
        g = long.groupby(["subject_id", "lifelog_date_only", "window"], observed=True)[col].agg(["mean", "max", "min", "std", "sum", "count"])
        g.columns = [f"{prefix}_{col}_{stat}" for stat in g.columns]
        parts.append(g)
    wide = pd.concat(parts, axis=1).reset_index()
    out = wide.pivot_table(index=["subject_id", "lifelog_date_only"], columns="window", values=[c for c in wide.columns if c not in {"subject_id", "lifelog_date_only", "window"}], aggfunc="first")
    out.columns = [f"{metric}_{window}" for metric, window in out.columns]
    return out.reset_index()


def add_numeric_features(features: pd.DataFrame) -> pd.DataFrame:
    specs = [
        ("ch2025_mScreenStatus.parquet", ["m_screen_use"], "screen", None),
        ("ch2025_mACStatus.parquet", ["m_charging"], "charge", None),
        ("ch2025_mLight.parquet", ["m_light"], "mlight", None),
        ("ch2025_wLight.parquet", ["w_light"], "wlight", None),
        ("ch2025_wPedo.parquet", ["step", "distance", "speed", "burned_calories"], "pedo", None),
        ("ch2025_wHr.parquet", [], "hr", "heart_rate"),
    ]
    for file_name, cols, prefix, list_col in specs:
        agg = numeric_window_agg(RAW / file_name, cols, prefix, list_col)
        if agg.empty:
            continue
        features = features.merge(agg, on=["subject_id", "lifelog_date_only"], how="left")
    return features


def add_activity_features(features: pd.DataFrame) -> pd.DataFrame:
    df = pd.read_parquet(RAW / "ch2025_mActivity.parquet")
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    rows = []
    for rec in df.itertuples(index=False):
        for window in time_window_flags(int(rec.timestamp.hour)):
            rows.append(
                {
                    "subject_id": rec.subject_id,
                    "lifelog_date_only": rec.timestamp.date(),
                    "window": window,
                    "activity": str(rec.m_activity),
                    "n": 1.0,
                }
            )
    long = pd.DataFrame(rows)
    wide = long.pivot_table(
        index=["subject_id", "lifelog_date_only"],
        columns=["window", "activity"],
        values="n",
        aggfunc="sum",
        fill_value=0.0,
    )
    wide.columns = [f"activity_{w}_code{a}_count" for w, a in wide.columns]
    wide = wide.reset_index()
    return features.merge(wide, on=["subject_id", "lifelog_date_only"], how="left")


def add_ambience_features(features: pd.DataFrame) -> pd.DataFrame:
    df = pd.read_parquet(RAW / "ch2025_mAmbience.parquet")
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    rows = []
    for rec in df.itertuples(index=False):
        scores = defaultdict(float)
        for item in parse_records(rec.m_ambience):
            if len(item) < 2:
                continue
            label = str(item[0]).lower()
            try:
                score = float(item[1])
            except (TypeError, ValueError):
                continue
            for category, pattern in AMBIENCE_RULES:
                if re.search(pattern, label, flags=re.IGNORECASE):
                    scores[category] += score
        if not scores:
            continue
        for window in time_window_flags(int(rec.timestamp.hour)):
            row = {"subject_id": rec.subject_id, "lifelog_date_only": rec.timestamp.date(), "window": window}
            row.update(scores)
            rows.append(row)
    long = pd.DataFrame(rows).fillna(0.0)
    if long.empty:
        return features
    cats = [c for c in long.columns if c not in {"subject_id", "lifelog_date_only", "window"}]
    agg = long.groupby(["subject_id", "lifelog_date_only", "window"], observed=True)[cats].mean().reset_index()
    wide = agg.pivot_table(index=["subject_id", "lifelog_date_only"], columns="window", values=cats, aggfunc="first")
    wide.columns = [f"ambience_{metric}_{window}" for metric, window in wide.columns]
    return features.merge(wide.reset_index(), on=["subject_id", "lifelog_date_only"], how="left")


def add_scan_features(features: pd.DataFrame) -> pd.DataFrame:
    specs = [
        ("ch2025_mWifi.parquet", "m_wifi", "bssid", "wifi"),
        ("ch2025_mBle.parquet", "m_ble", "address", "ble"),
    ]
    for file_name, col, key, prefix in specs:
        df = pd.read_parquet(RAW / file_name)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        rows = []
        for rec in df.itertuples(index=False):
            items = parse_records(getattr(rec, col))
            ids = []
            rssis = []
            for item in items:
                try:
                    ids.append(str(item.get(key, "")))
                    rssis.append(float(item.get("rssi", np.nan)))
                except AttributeError:
                    continue
            if not ids:
                continue
            vals = {
                f"{prefix}_scan_n": float(len(ids)),
                f"{prefix}_scan_unique_n": float(len(set(ids))),
                f"{prefix}_rssi_mean": float(np.nanmean(rssis)) if rssis else np.nan,
                f"{prefix}_strong_share": float(np.nanmean(np.asarray(rssis) > -70)) if rssis else np.nan,
            }
            for window in time_window_flags(int(rec.timestamp.hour)):
                row = {"subject_id": rec.subject_id, "lifelog_date_only": rec.timestamp.date(), "window": window}
                row.update(vals)
                rows.append(row)
        long = pd.DataFrame(rows)
        if long.empty:
            continue
        val_cols = [c for c in long.columns if c not in {"subject_id", "lifelog_date_only", "window"}]
        agg = long.groupby(["subject_id", "lifelog_date_only", "window"], observed=True)[val_cols].mean().reset_index()
        wide = agg.pivot_table(index=["subject_id", "lifelog_date_only"], columns="window", values=val_cols, aggfunc="first")
        wide.columns = [f"{metric}_{window}" for metric, window in wide.columns]
        features = features.merge(wide.reset_index(), on=["subject_id", "lifelog_date_only"], how="left")
    return features


def add_gps_features(features: pd.DataFrame) -> pd.DataFrame:
    df = pd.read_parquet(RAW / "ch2025_mGps.parquet")
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    rows = []
    for rec in df.itertuples(index=False):
        items = parse_records(rec.m_gps)
        lats, lons, speeds = [], [], []
        for item in items:
            try:
                lats.append(float(item.get("latitude", np.nan)))
                lons.append(float(item.get("longitude", np.nan)))
                speeds.append(float(item.get("speed", np.nan)))
            except AttributeError:
                continue
        if not lats:
            continue
        lat_arr = np.asarray(lats, dtype=np.float64)
        lon_arr = np.asarray(lons, dtype=np.float64)
        speed_arr = np.asarray(speeds, dtype=np.float64)
        cells = {f"{round(a, 4)}:{round(b, 4)}" for a, b in zip(lat_arr, lon_arr)}
        vals = {
            "gps_points_n": float(len(lats)),
            "gps_speed_mean": float(np.nanmean(speed_arr)),
            "gps_speed_max": float(np.nanmax(speed_arr)),
            "gps_lat_range": float(np.nanmax(lat_arr) - np.nanmin(lat_arr)),
            "gps_lon_range": float(np.nanmax(lon_arr) - np.nanmin(lon_arr)),
            "gps_cell_unique_n": float(len(cells)),
        }
        for window in time_window_flags(int(rec.timestamp.hour)):
            row = {"subject_id": rec.subject_id, "lifelog_date_only": rec.timestamp.date(), "window": window}
            row.update(vals)
            rows.append(row)
    long = pd.DataFrame(rows)
    val_cols = [c for c in long.columns if c not in {"subject_id", "lifelog_date_only", "window"}]
    agg = long.groupby(["subject_id", "lifelog_date_only", "window"], observed=True)[val_cols].mean().reset_index()
    wide = agg.pivot_table(index=["subject_id", "lifelog_date_only"], columns="window", values=val_cols, aggfunc="first")
    wide.columns = [f"{metric}_{window}" for metric, window in wide.columns]
    return features.merge(wide.reset_index(), on=["subject_id", "lifelog_date_only"], how="left")


def zscore_by_subject(frame: pd.DataFrame, col: str) -> pd.Series:
    vals = frame[col].fillna(0.0)
    mu = vals.groupby(frame["subject_id"]).transform("mean")
    sd = vals.groupby(frame["subject_id"]).transform("std").replace(0, np.nan)
    return ((vals - mu) / sd).fillna(0.0)


def add_composites(features: pd.DataFrame) -> pd.DataFrame:
    def cols_like(*parts: str) -> list[str]:
        return [c for c in features.columns if all(p in c for p in parts)]

    composite_specs = {
        "human_social_overstim_late": cols_like("usage_late_social_msg") + cols_like("usage_late_call") + cols_like("ambience_speech_late") + cols_like("screen_m_screen_use_mean_late"),
        "human_late_cognitive_load": cols_like("usage_late_search_browser") + cols_like("usage_late_shopping") + cols_like("usage_late_finance") + cols_like("usage_late_work_study") + cols_like("screen_m_screen_use_mean_late"),
        "human_routine_anchor": cols_like("usage_day_religion_routine") + cols_like("usage_presleep_religion_routine") + cols_like("charge_m_charging_mean_presleep"),
        "human_commute_mobility": cols_like("gps_speed_mean_morning") + cols_like("gps_speed_mean_evening") + cols_like("pedo_step_sum_morning") + cols_like("pedo_step_sum_evening") + cols_like("wifi_scan_unique_n_day"),
        "human_physical_fatigue": cols_like("pedo_step_sum_day") + cols_like("pedo_distance_sum_day") + cols_like("hr_heart_rate_mean_mean_day"),
        "human_sleep_onset_risk": cols_like("screen_m_screen_use_mean_late") + cols_like("mlight_m_light_mean_late") + cols_like("wlight_w_light_mean_late") + cols_like("pedo_step_sum_late"),
        "human_public_social_presence": cols_like("ambience_speech_evening") + cols_like("ambience_inside_public_evening") + cols_like("ble_scan_unique_n_evening"),
    }
    for name, cols in composite_specs.items():
        if cols:
            features[name] = features[cols].fillna(0.0).sum(axis=1)
            features[f"{name}_subj_z"] = zscore_by_subject(features, name)
        else:
            features[name] = 0.0
            features[f"{name}_subj_z"] = 0.0
    return features


def feature_inventory(features: pd.DataFrame) -> pd.DataFrame:
    numeric_cols = [c for c in features.columns if c not in set(KEYS + TARGETS + ["split"]) and pd.api.types.is_numeric_dtype(features[c])]
    rows = []
    for col in numeric_cols:
        vals = features[col]
        rows.append(
            {
                "feature": col,
                "non_null_rate": float(vals.notna().mean()),
                "mean": float(vals.fillna(0.0).mean()),
                "std": float(vals.fillna(0.0).std()),
                "train_mean": float(features.loc[features["split"].eq("train"), col].fillna(0.0).mean()),
                "test_mean": float(features.loc[features["split"].eq("test"), col].fillna(0.0).mean()),
            }
        )
    inv = pd.DataFrame(rows)
    inv["abs_train_test_gap_z"] = (inv["train_mean"] - inv["test_mean"]).abs() / inv["std"].replace(0, np.nan)
    return inv.sort_values(["abs_train_test_gap_z", "non_null_rate"], ascending=[False, False]).reset_index(drop=True)


def probe_hypotheses(features: pd.DataFrame) -> pd.DataFrame:
    train = features[features["split"].eq("train")].copy()
    candidate_cols = [
        c
        for c in train.columns
        if c.startswith("human_")
        or c.startswith("usage_late_")
        or c.startswith("usage_presleep_")
        or c.startswith("ambience_")
        or c.startswith("screen_m_screen_use_mean_late")
        or c.startswith("charge_m_charging_mean_presleep")
        or c.startswith("gps_speed_mean_")
        or c.startswith("pedo_step_sum_")
    ]
    rows = []
    for feature in sorted(set(candidate_cols)):
        vals = train[feature].fillna(0.0).astype(float)
        if vals.nunique() < 4:
            continue
        qlo, qhi = vals.quantile(0.25), vals.quantile(0.75)
        low = vals <= qlo
        high = vals >= qhi
        if low.sum() < 10 or high.sum() < 10:
            continue
        subj_z = zscore_by_subject(train, feature)
        for target in TARGETS:
            y = train[target].astype(float)
            low_mean = float(y[low].mean())
            high_mean = float(y[high].mean())
            corr = float(np.corrcoef(subj_z, y)[0, 1]) if subj_z.std() > 1.0e-12 else 0.0
            rows.append(
                {
                    "feature": feature,
                    "target": target,
                    "label_mean_low_q": low_mean,
                    "label_mean_high_q": high_mean,
                    "high_minus_low": high_mean - low_mean,
                    "subject_z_corr": corr,
                    "abs_effect": abs(high_mean - low_mean),
                    "hypothesis_family": family_for_feature(feature),
                }
            )
    out = pd.DataFrame(rows)
    return out.sort_values(["abs_effect", "feature", "target"], ascending=[False, True, True]).reset_index(drop=True)


def family_for_feature(feature: str) -> str:
    if "social" in feature or "call" in feature or "speech" in feature:
        return "social_overstimulation"
    if "religion" in feature or "routine" in feature or "charge" in feature:
        return "routine_stability"
    if "gps" in feature or "wifi" in feature or "commute" in feature:
        return "workday_commute"
    if "shopping" in feature or "finance" in feature or "search" in feature or "cognitive" in feature:
        return "late_cognitive_load"
    if "pedo" in feature or "hr_" in feature or "physical" in feature:
        return "physical_fatigue"
    if "screen" in feature or "light" in feature or "onset" in feature:
        return "sleep_onset_fragmentation"
    return "other_lifestyle"


def report_text(features: pd.DataFrame, app_inv: pd.DataFrame, inv: pd.DataFrame, probe: pd.DataFrame) -> str:
    top_apps = app_inv.head(30)[["app_name", "category", "event_count", "total_time"]]
    top_probe = probe.head(30)
    family_probe = (
        probe.groupby("hypothesis_family", observed=True)
        .agg(max_abs_effect=("abs_effect", "max"), mean_abs_effect_top10=("abs_effect", lambda s: float(s.head(10).mean())))
        .reset_index()
        .sort_values("max_abs_effect", ascending=False)
    )
    inv_view = inv.head(20)
    n_features = len([c for c in features.columns if c not in set(KEYS + TARGETS + ["split"])])
    return f"""# E262 Human/Social Lifelog JEPA Blueprint

## Question

Can the raw lifelog be translated into human lifestyle states before we ask a model to predict sleep labels?

The goal is not to add generic aggregates. The goal is to build JEPA-ready context/target variables that represent social stimulation, routine, commute rhythm, late cognitive load, physical fatigue, and sleep-onset risk.

## Raw Evidence

- Rows covered: `{len(features)}` (`{int(features['split'].eq('train').sum())}` train, `{int(features['split'].eq('test').sum())}` test).
- Subjects: `{features['subject_id'].nunique()}`.
- Generated lifestyle/raw context features: `{n_features}`.
- Raw app usage includes real social/routine apps such as KakaoTalk, calls/messages, search/browser, finance/shopping, health-walk, and religion/routine apps.

## Top App Categories

{to_md(top_apps)}

## Strongest Label-Lift Probes

These are not submission features yet. They are cheap falsification signals for human hypotheses.

{to_md(top_probe)}

## Hypothesis Family Signal

{to_md(family_probe)}

## Largest Train/Test Shift Features

These are potential domain/block signatures and leakage-risk diagnostics.

{to_md(inv_view[['feature', 'non_null_rate', 'train_mean', 'test_mean', 'abs_train_test_gap_z']])}

## JEPA Translation

Good JEPA target design here should avoid raw reconstruction. Candidate context-target pairs:

1. Social-night JEPA:
   - context: non-app sensors, weekday, prior/next day lifestyle state.
   - target: late social/call/speech latent.
   - question: can the world model infer social overstimulation from surrounding behavior?

2. Routine-stability JEPA:
   - context: subject history and day-of-week.
   - target: religion/routine app timing, charging regularity, screen-off stability.
   - question: is sleep quality tied to stable ritual rather than raw phone time?

3. Commute/workday JEPA:
   - context: morning/evening GPS/WiFi/BLE/pedo signatures.
   - target: workday/home-away/commute latent.
   - question: do Q/S labels depend on lifestyle block state more than row features?

4. Sleep-onset JEPA:
   - context: daytime activity and evening app categories.
   - target: late screen/light/movement/charging latent.
   - question: can we predict a hidden bedtime-fragmentation representation?

5. Target-state JEPA:
   - context: all human diary features with block masks.
   - target: Q/S co-occurrence state or E247-like Q3 public-tail energy.
   - question: can social lifestyle state explain the Q3 hard-tail cells that current numeric models only patch?

## Next Validation Gate

- Build OOF folds by subject/date block, not random rows.
- Test whether human lifestyle composites improve Q/S target LogLoss under blockwise CV.
- Test whether latent lifestyle states explain E247/E256 disagreement cells, especially Q3 rows `188`, `96`, `87`, and `138`.
- Reject any feature family that only predicts train/test split or subject identity without target lift inside subject.
"""


def to_md(frame: pd.DataFrame, n: int = 30) -> str:
    if frame.empty:
        return "_empty_"
    view = frame.head(n).copy()
    headers = list(view.columns)
    rows = []
    for _, row in view.iterrows():
        vals = []
        for col in headers:
            value = row[col]
            if isinstance(value, (float, np.floating)):
                vals.append(f"{float(value):.6f}")
            else:
                vals.append(str(value))
        rows.append(vals)
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    out.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(out)


def main() -> None:
    base = read_base()
    features = empty_feature_frame(base)
    features, app_inv = add_usage_features(features)
    features = add_numeric_features(features)
    features = add_activity_features(features)
    features = add_ambience_features(features)
    features = add_scan_features(features)
    features = add_gps_features(features)
    features = add_composites(features)
    features = features.fillna(0.0)

    inv = feature_inventory(features)
    probe = probe_hypotheses(features)

    features.to_parquet(FEATURE_OUT, index=False)
    features.head(50).to_csv(FEATURE_CSV_OUT, index=False)
    app_inv.to_csv(APP_INV_OUT, index=False)
    probe.to_csv(PROBE_OUT, index=False)
    REPORT_OUT.write_text(report_text(features, app_inv, inv, probe), encoding="utf-8")

    print(f"wrote {FEATURE_OUT}")
    print(f"wrote {FEATURE_CSV_OUT}")
    print(f"wrote {APP_INV_OUT}")
    print(f"wrote {PROBE_OUT}")
    print(f"wrote {REPORT_OUT}")


if __name__ == "__main__":
    main()
