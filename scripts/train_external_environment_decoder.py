from __future__ import annotations

import argparse
import json
import urllib.parse
import urllib.request
import warnings
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from pandas.errors import PerformanceWarning
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


KEY_COLUMNS = ["subject_id", "sleep_date", "lifelog_date"]
TARGET_COLUMNS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
EPS = 1e-5

WEATHER_DAILY_VARIABLES = [
    "temperature_2m_mean",
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "rain_sum",
    "snowfall_sum",
    "daylight_duration",
    "sunshine_duration",
    "wind_speed_10m_max",
    "shortwave_radiation_sum",
]

AIR_HOURLY_VARIABLES = [
    "pm10",
    "pm2_5",
    "carbon_monoxide",
    "nitrogen_dioxide",
    "sulphur_dioxide",
    "ozone",
    "aerosol_optical_depth",
    "dust",
    "uv_index",
    "uv_index_clear_sky",
]

CITIES = {
    "seoul": (37.5665, 126.9780),
    "daejeon": (36.3504, 127.3845),
    "busan": (35.1796, 129.0756),
    "daegu": (35.8714, 128.6014),
    "gwangju": (35.1595, 126.8526),
    "jeju": (33.4996, 126.5312),
}


@dataclass(frozen=True)
class SourceSpec:
    name: str
    features: list[str]
    c_value: float
    class_weight: str | None


def normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in KEY_COLUMNS:
        out[col] = out[col].astype(str)
    return out


def safe_logit(values: np.ndarray) -> np.ndarray:
    values = np.clip(values.astype(float), EPS, 1.0 - EPS)
    return np.log(values / (1.0 - values))


def prediction_matrix(oof: pd.DataFrame) -> np.ndarray:
    return np.column_stack([oof[f"pred_{target}"].to_numpy(dtype=float) for target in TARGET_COLUMNS])


def submission_matrix(submission: pd.DataFrame) -> np.ndarray:
    return submission[TARGET_COLUMNS].to_numpy(dtype=float)


def score(y: pd.DataFrame, pred: np.ndarray) -> float:
    return float(
        np.mean(
            [
                log_loss(y[target], np.clip(pred[:, i], EPS, 1.0 - EPS), labels=[0, 1])
                for i, target in enumerate(TARGET_COLUMNS)
            ]
        )
    )


def fetch_json(url: str) -> dict[str, object]:
    request = urllib.request.Request(url, headers={"User-Agent": "dacon-etri-external-environment/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_weather_city(city: str, latitude: float, longitude: float, start_date: str, end_date: str, cache_dir: Path) -> pd.DataFrame:
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / f"weather_{city}_{start_date}_{end_date}.csv"
    if cache_path.exists():
        return pd.read_csv(cache_path)
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "daily": ",".join(WEATHER_DAILY_VARIABLES),
        "timezone": "Asia/Seoul",
    }
    url = "https://archive-api.open-meteo.com/v1/archive?" + urllib.parse.urlencode(params)
    payload = fetch_json(url)
    if "daily" not in payload:
        raise RuntimeError(f"Open-Meteo weather response missing daily payload for {city}: {payload}")
    frame = pd.DataFrame(payload["daily"]).rename(columns={"time": "date"})
    frame.insert(0, "city", city)
    frame.to_csv(cache_path, index=False)
    return frame


def fetch_air_city(city: str, latitude: float, longitude: float, start_date: str, end_date: str, cache_dir: Path) -> pd.DataFrame:
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / f"air_{city}_{start_date}_{end_date}.csv"
    if cache_path.exists():
        return pd.read_csv(cache_path)
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": ",".join(AIR_HOURLY_VARIABLES),
        "timezone": "Asia/Seoul",
    }
    url = "https://air-quality-api.open-meteo.com/v1/air-quality?" + urllib.parse.urlencode(params)
    payload = fetch_json(url)
    if "hourly" not in payload:
        raise RuntimeError(f"Open-Meteo air-quality response missing hourly payload for {city}: {payload}")
    hourly = pd.DataFrame(payload["hourly"])
    hourly["date"] = pd.to_datetime(hourly["time"]).dt.strftime("%Y-%m-%d")
    agg = hourly.groupby("date", as_index=False)[AIR_HOURLY_VARIABLES].agg(["mean", "max", "min"])
    agg.columns = ["_".join(part for part in col if part) for col in agg.columns.to_flat_index()]
    agg = agg.rename(columns={"date_": "date"})
    agg.insert(0, "city", city)
    agg.to_csv(cache_path, index=False)
    return agg


def fetch_holidays(years: list[int], cache_dir: Path) -> pd.DataFrame:
    cache_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for year in sorted(set(years)):
        cache_path = cache_dir / f"nager_kr_public_holidays_{year}.json"
        if cache_path.exists():
            payload = json.loads(cache_path.read_text(encoding="utf-8"))
        else:
            url = f"https://date.nager.at/api/v3/PublicHolidays/{year}/KR"
            payload = fetch_json(url)
            cache_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        rows.extend(payload)
    frame = pd.DataFrame(rows)
    if frame.empty or "date" not in frame.columns:
        raise RuntimeError("Nager.Date public holiday response is empty or malformed.")
    frame["date"] = pd.to_datetime(frame["date"]).dt.strftime("%Y-%m-%d")
    return frame.drop_duplicates("date").sort_values("date").reset_index(drop=True)


def load_weather(start_date: str, end_date: str, cache_dir: Path) -> pd.DataFrame:
    return pd.concat(
        [fetch_weather_city(city, lat, lon, start_date, end_date, cache_dir) for city, (lat, lon) in CITIES.items()],
        ignore_index=True,
    )


def load_air(start_date: str, end_date: str, cache_dir: Path) -> pd.DataFrame:
    return pd.concat(
        [fetch_air_city(city, lat, lon, start_date, end_date, cache_dir) for city, (lat, lon) in CITIES.items()],
        ignore_index=True,
    )


def wide_city_daily(long: pd.DataFrame, prefix: str, base_variables: list[str]) -> pd.DataFrame:
    long = long.copy()
    long["date"] = pd.to_datetime(long["date"]).dt.strftime("%Y-%m-%d")
    value_cols = [col for col in long.columns if col not in {"city", "date"}]
    wide = None
    for city in sorted(long["city"].unique()):
        city_frame = long[long["city"].eq(city)][["date", *value_cols]].copy()
        city_frame = city_frame.rename(columns={col: f"{prefix}_{city}_{col}" for col in value_cols})
        wide = city_frame if wide is None else wide.merge(city_frame, on="date", how="outer", validate="one_to_one")
    if wide is None:
        raise RuntimeError(f"No {prefix} rows available to widen.")

    for variable in base_variables:
        city_cols = [col for col in wide.columns if col.startswith(f"{prefix}_") and f"_{variable}" in col]
        if not city_cols:
            continue
        wide[f"{prefix}_kr_mean_{variable}"] = wide[city_cols].mean(axis=1)
        wide[f"{prefix}_kr_std_{variable}"] = wide[city_cols].std(axis=1)
        wide[f"{prefix}_kr_min_{variable}"] = wide[city_cols].min(axis=1)
        wide[f"{prefix}_kr_max_{variable}"] = wide[city_cols].max(axis=1)

    wide = wide.sort_values("date").reset_index(drop=True)
    numeric_cols = [col for col in wide.columns if col != "date"]
    for col in list(numeric_cols):
        wide[f"{col}_lag1"] = wide[col].shift(1)
        wide[f"{col}_delta1"] = wide[col] - wide[col].shift(1)
        wide[f"{col}_dev7"] = wide[col] - wide[col].shift(1).rolling(7, min_periods=3).mean()
    return wide


def holiday_date_features(dates: pd.Series, holidays: pd.DataFrame, prefix: str) -> pd.DataFrame:
    date = pd.to_datetime(dates)
    holiday_dates = pd.to_datetime(holidays["date"]).sort_values().to_numpy(dtype="datetime64[D]")
    day_values = date.to_numpy(dtype="datetime64[D]")
    is_holiday = np.isin(day_values, holiday_dates)
    before = np.isin(day_values + np.timedelta64(1, "D"), holiday_dates)
    after = np.isin(day_values - np.timedelta64(1, "D"), holiday_dates)
    distances = np.abs((day_values[:, None] - holiday_dates[None, :]).astype("timedelta64[D]").astype(int))
    min_abs = distances.min(axis=1).astype(float)
    prev = []
    nxt = []
    for value in day_values:
        deltas = (holiday_dates - value).astype("timedelta64[D]").astype(int)
        prev_delta = deltas[deltas <= 0]
        next_delta = deltas[deltas >= 0]
        prev.append(float(abs(prev_delta.max())) if len(prev_delta) else 99.0)
        nxt.append(float(next_delta.min()) if len(next_delta) else 99.0)
    dow = date.dt.dayofweek
    return pd.DataFrame(
        {
            f"{prefix}_is_public_holiday": is_holiday.astype(float),
            f"{prefix}_is_day_before_public_holiday": before.astype(float),
            f"{prefix}_is_day_after_public_holiday": after.astype(float),
            f"{prefix}_within_2d_public_holiday": (min_abs <= 2).astype(float),
            f"{prefix}_dist_nearest_public_holiday": np.minimum(min_abs, 30.0),
            f"{prefix}_dist_prev_public_holiday": np.minimum(np.asarray(prev), 30.0),
            f"{prefix}_dist_next_public_holiday": np.minimum(np.asarray(nxt), 30.0),
            f"{prefix}_holiday_adjacent_weekend": ((is_holiday | before | after) & dow.isin([4, 5, 6])).astype(float),
        }
    )


def add_panel_calendar_features(frame: pd.DataFrame, all_rows: pd.DataFrame, holidays: pd.DataFrame) -> pd.DataFrame:
    out = frame[KEY_COLUMNS].copy()
    panel = all_rows.merge(frame[KEY_COLUMNS].assign(_row=np.arange(len(frame))), on=KEY_COLUMNS, how="inner", validate="one_to_one")
    panel = panel.sort_values("_row").reset_index(drop=True)
    out["panel_index"] = panel["panel_index"].to_numpy(float)
    out["panel_position"] = panel["panel_position"].to_numpy(float)

    for date_col, prefix in [("lifelog_date", "life"), ("sleep_date", "sleep")]:
        date = pd.to_datetime(out[date_col])
        dow = date.dt.dayofweek.astype(float)
        doy = date.dt.dayofyear.astype(float)
        month = date.dt.month.astype(float)
        week = date.dt.isocalendar().week.astype(float)
        out[f"{prefix}_dow_sin"] = np.sin(2 * np.pi * dow / 7)
        out[f"{prefix}_dow_cos"] = np.cos(2 * np.pi * dow / 7)
        out[f"{prefix}_doy_sin"] = np.sin(2 * np.pi * doy / 366)
        out[f"{prefix}_doy_cos"] = np.cos(2 * np.pi * doy / 366)
        out[f"{prefix}_month_sin"] = np.sin(2 * np.pi * month / 12)
        out[f"{prefix}_month_cos"] = np.cos(2 * np.pi * month / 12)
        out[f"{prefix}_week_sin"] = np.sin(2 * np.pi * week / 53)
        out[f"{prefix}_week_cos"] = np.cos(2 * np.pi * week / 53)
        out[f"{prefix}_is_weekend"] = dow.isin([5, 6]).astype(float)
        out[f"{prefix}_is_monday"] = dow.eq(0).astype(float)
        out[f"{prefix}_is_friday"] = dow.eq(4).astype(float)
        out[f"{prefix}_is_korea_summer_break_prior"] = date.between("2024-07-20", "2024-08-31").astype(float)
        out[f"{prefix}_is_korea_fall_semester_prior"] = date.between("2024-09-01", "2024-11-30").astype(float)
        out[f"{prefix}_is_october_midterm_prior"] = date.between("2024-10-14", "2024-10-25").astype(float)
        out = pd.concat([out, holiday_date_features(out[date_col], holidays, prefix)], axis=1)
    return out


def attach_daily_features(frame: pd.DataFrame, weather: pd.DataFrame, air: pd.DataFrame, all_rows: pd.DataFrame, holidays: pd.DataFrame) -> pd.DataFrame:
    out = add_panel_calendar_features(frame, all_rows, holidays)
    daily = weather.merge(air, on="date", how="outer", validate="one_to_one")
    for date_col, prefix in [("lifelog_date", "life"), ("sleep_date", "sleep")]:
        joined = frame[[date_col]].rename(columns={date_col: "date"}).merge(daily, on="date", how="left", validate="many_to_one")
        missing = int(joined.drop(columns=["date"]).isna().all(axis=1).sum())
        if missing:
            raise ValueError(f"{missing} rows missing external daily environment data for {date_col}")
        for col in joined.columns:
            if col == "date":
                continue
            out[f"{prefix}_{col}"] = joined[col].to_numpy(dtype=float)
    life_cols = [col for col in out.columns if col.startswith("life_weather_") or col.startswith("life_air_")]
    for life_col in life_cols:
        sleep_col = "sleep_" + life_col[len("life_") :]
        if sleep_col in out.columns and not any(life_col.endswith(suffix) for suffix in ["_lag1", "_delta1", "_dev7"]):
            out[f"sleep_minus_life_{life_col[len('life_'):]}"] = out[sleep_col] - out[life_col]
    return out


def make_panel_index(train: pd.DataFrame, sample: pd.DataFrame) -> pd.DataFrame:
    all_rows = pd.concat(
        [
            train[KEY_COLUMNS].assign(_split="train", _row=np.arange(len(train))),
            sample[KEY_COLUMNS].assign(_split="sample", _row=np.arange(len(sample))),
        ],
        ignore_index=True,
    )
    ordered = all_rows.sort_values(["subject_id", "lifelog_date", "sleep_date"]).copy()
    ordered["panel_index"] = ordered.groupby("subject_id").cumcount().astype(float)
    denom = ordered.groupby("subject_id")["panel_index"].transform("max").replace(0.0, 1.0)
    ordered["panel_position"] = ordered["panel_index"] / denom
    return ordered[KEY_COLUMNS + ["panel_index", "panel_position"]]


def add_base_features(
    features_train: pd.DataFrame,
    features_test: pd.DataFrame,
    train: pd.DataFrame,
    sample: pd.DataFrame,
    base_oof_path: str,
    base_submission_path: str,
) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    oof = normalize_keys(pd.read_csv(base_oof_path))
    submission = normalize_keys(pd.read_csv(base_submission_path))
    if not oof[KEY_COLUMNS].equals(train[KEY_COLUMNS]):
        raise ValueError("Base OOF keys do not match train keys")
    if not submission[KEY_COLUMNS].equals(sample[KEY_COLUMNS]):
        raise ValueError("Base submission keys do not match sample keys")
    train_pred = np.clip(prediction_matrix(oof), EPS, 1.0 - EPS)
    test_pred = np.clip(submission_matrix(submission), EPS, 1.0 - EPS)
    cols = []
    for i, target in enumerate(TARGET_COLUMNS):
        for suffix, train_values, test_values in [
            ("prob", train_pred[:, i], test_pred[:, i]),
            ("logit", safe_logit(train_pred[:, i]), safe_logit(test_pred[:, i])),
        ]:
            col = f"base_{target}_{suffix}"
            features_train[col] = train_values
            features_test[col] = test_values
            cols.append(col)
    return features_train, features_test, cols


def make_subject_time_folds(frame: pd.DataFrame, n_folds: int) -> list[tuple[np.ndarray, np.ndarray]]:
    ordered = frame.reset_index(names="_idx").sort_values(["subject_id", "lifelog_date", "sleep_date"])
    val_indices: list[list[int]] = [[] for _ in range(n_folds)]
    for _, group in ordered.groupby("subject_id", sort=False):
        chunks = np.array_split(group["_idx"].to_numpy(), n_folds)
        for fold, chunk in enumerate(chunks):
            val_indices[fold].extend(chunk.tolist())
    all_idx = np.arange(len(frame))
    return [
        (np.setdiff1d(all_idx, np.array(sorted(indices), dtype=int)), np.array(sorted(indices), dtype=int))
        for indices in val_indices
    ]


def train_source(
    spec: SourceSpec,
    features_train: pd.DataFrame,
    features_test: pd.DataFrame,
    labels: pd.DataFrame,
    folds: list[tuple[np.ndarray, np.ndarray]],
    output_dir: Path,
) -> dict[str, object]:
    x_train = features_train[spec.features].to_numpy(dtype=np.float32)
    x_test = features_test[spec.features].to_numpy(dtype=np.float32)
    y = labels[TARGET_COLUMNS].astype(int)
    oof_pred = np.zeros((len(labels), len(TARGET_COLUMNS)), dtype=float)
    test_pred = np.zeros((len(features_test), len(TARGET_COLUMNS)), dtype=float)
    target_scores = {}
    for target_i, target in enumerate(TARGET_COLUMNS):
        target_values = y[target].to_numpy(dtype=int)
        for trn_idx, val_idx in folds:
            if len(np.unique(target_values[trn_idx])) < 2:
                oof_pred[val_idx, target_i] = float(np.mean(target_values[trn_idx]))
                continue
            model = make_pipeline(
                SimpleImputer(strategy="median"),
                StandardScaler(),
                LogisticRegression(
                    C=spec.c_value,
                    class_weight=spec.class_weight,
                    max_iter=3000,
                    solver="lbfgs",
                    random_state=2026,
                ),
            )
            model.fit(x_train[trn_idx], target_values[trn_idx])
            oof_pred[val_idx, target_i] = model.predict_proba(x_train[val_idx])[:, 1]
        full_model = make_pipeline(
            SimpleImputer(strategy="median"),
            StandardScaler(),
            LogisticRegression(
                C=spec.c_value,
                class_weight=spec.class_weight,
                max_iter=3000,
                solver="lbfgs",
                random_state=2026,
            ),
        )
        full_model.fit(x_train, target_values)
        test_pred[:, target_i] = full_model.predict_proba(x_test)[:, 1]
        target_scores[target] = float(log_loss(target_values, np.clip(oof_pred[:, target_i], EPS, 1.0 - EPS), labels=[0, 1]))

    oof_pred = np.clip(oof_pred, EPS, 1.0 - EPS)
    test_pred = np.clip(test_pred, EPS, 1.0 - EPS)
    oof = labels[KEY_COLUMNS + TARGET_COLUMNS].copy()
    submission = features_test[KEY_COLUMNS].copy()
    for i, target in enumerate(TARGET_COLUMNS):
        oof[f"pred_{target}"] = oof_pred[:, i]
        submission[target] = test_pred[:, i]
    oof_path = output_dir / f"oof_{spec.name}.csv"
    submission_path = output_dir / f"submission_{spec.name}.csv"
    oof.to_csv(oof_path, index=False)
    submission.to_csv(submission_path, index=False)
    return {
        "name": spec.name,
        "avg_log_loss": score(y, oof_pred),
        "target_scores": target_scores,
        "n_features": len(spec.features),
        "c_value": spec.c_value,
        "class_weight": spec.class_weight,
        "oof_path": str(oof_path),
        "submission_path": str(submission_path),
    }


def parse_float_list(value: str) -> list[float]:
    return [float(part) for part in value.split(",") if part.strip()]


def main() -> None:
    warnings.filterwarnings("ignore", category=PerformanceWarning)
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    min_date = min(train["lifelog_date"].min(), train["sleep_date"].min(), sample["lifelog_date"].min(), sample["sleep_date"].min())
    max_date = max(train["lifelog_date"].max(), train["sleep_date"].max(), sample["lifelog_date"].max(), sample["sleep_date"].max())
    start_date = (pd.Timestamp(min_date) - pd.Timedelta(days=21)).strftime("%Y-%m-%d")
    end_date = (pd.Timestamp(max_date) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")

    weather = wide_city_daily(load_weather(start_date, end_date, output_dir / "external_cache"), "weather", WEATHER_DAILY_VARIABLES)
    air_base_variables = [f"{name}_{stat}" for name in AIR_HOURLY_VARIABLES for stat in ["mean", "max", "min"]]
    air = wide_city_daily(load_air(start_date, end_date, output_dir / "external_cache"), "air", air_base_variables)
    holidays = fetch_holidays([pd.Timestamp(start_date).year, pd.Timestamp(end_date).year], output_dir / "external_cache")
    weather.to_csv(output_dir / "weather_features_by_date.csv", index=False)
    air.to_csv(output_dir / "air_quality_features_by_date.csv", index=False)
    holidays.to_csv(output_dir / "korea_public_holidays.csv", index=False)

    panel = make_panel_index(train, sample)
    features_train = attach_daily_features(train, weather, air, panel, holidays)
    features_test = attach_daily_features(sample, weather, air, panel, holidays)
    env_cols = [col for col in features_train.columns if col not in KEY_COLUMNS]
    features_train, features_test, base_cols = add_base_features(
        features_train,
        features_test,
        train,
        sample,
        args.base_oof,
        args.base_submission,
    )
    all_feature_cols = [col for col in features_train.columns if col not in KEY_COLUMNS]
    features_train[KEY_COLUMNS + all_feature_cols].to_csv(output_dir / "features_train.csv", index=False)
    features_test[KEY_COLUMNS + all_feature_cols].to_csv(output_dir / "features_test.csv", index=False)
    train[KEY_COLUMNS + TARGET_COLUMNS].to_csv(output_dir / "labels_train.csv", index=False)

    specs: list[SourceSpec] = []
    for c_value in parse_float_list(args.c_values):
        c_tag = str(c_value).replace(".", "p")
        specs.append(SourceSpec(f"environment_only_c{c_tag}", env_cols, c_value, None))
        specs.append(SourceSpec(f"environment_base_c{c_tag}", all_feature_cols, c_value, None))
        specs.append(SourceSpec(f"environment_base_bal_c{c_tag}", all_feature_cols, c_value, "balanced"))

    folds = make_subject_time_folds(train, args.n_folds)
    rows = [train_source(spec, features_train, features_test, train, folds, output_dir) for spec in specs]
    report = pd.DataFrame(rows).sort_values("avg_log_loss").reset_index(drop=True)
    report.to_csv(output_dir / "external_environment_report.csv", index=False)
    (output_dir / "external_environment_report.json").write_text(
        json.dumps(report.to_dict(orient="records"), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    manifest = {
        "external_sources": {
            "weather": "https://archive-api.open-meteo.com/v1/archive",
            "air_quality": "https://air-quality-api.open-meteo.com/v1/air-quality",
            "korea_public_holidays": "https://date.nager.at/api/v3/PublicHolidays/{year}/KR",
        },
        "cities": {city: {"latitude": lat, "longitude": lon} for city, (lat, lon) in CITIES.items()},
        "date_range": {"start": start_date, "end": end_date},
        "weather_daily_variables": WEATHER_DAILY_VARIABLES,
        "air_hourly_variables": AIR_HOURLY_VARIABLES,
        "n_environment_features": len(env_cols),
        "n_base_features": len(base_cols),
        "n_total_features": len(all_feature_cols),
        "base_oof": args.base_oof,
        "base_submission": args.base_submission,
        "design_note": "External data are used only as label-free environmental/calendar covariates; no external ETRI label files are consumed.",
    }
    (output_dir / "feature_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(report[["name", "avg_log_loss", "n_features", "class_weight"]].to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train external environment source decoders over public Korean weather, air quality, and holidays.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--base-oof", default="outputs/master_aggressive_decoder_fast/oof_temporal_master_oof_blend.csv")
    parser.add_argument("--base-submission", default="outputs/master_aggressive_decoder_fast/submission_temporal_master_oof_blend.csv")
    parser.add_argument("--output-dir", default="outputs/external_environment_decoder_v77")
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--c-values", default="0.001,0.003,0.01,0.03")
    return parser.parse_args()


if __name__ == "__main__":
    main()
