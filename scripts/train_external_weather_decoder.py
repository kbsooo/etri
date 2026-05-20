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

DAILY_VARIABLES = [
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


def fetch_city_weather(city: str, latitude: float, longitude: float, start_date: str, end_date: str, cache_dir: Path) -> pd.DataFrame:
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / f"{city}_{start_date}_{end_date}.csv"
    if cache_path.exists():
        return pd.read_csv(cache_path)
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "daily": ",".join(DAILY_VARIABLES),
        "timezone": "Asia/Seoul",
    }
    url = "https://archive-api.open-meteo.com/v1/archive?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=45) as response:
        payload = json.loads(response.read().decode("utf-8"))
    daily = pd.DataFrame(payload["daily"])
    daily = daily.rename(columns={"time": "date"})
    daily.insert(0, "city", city)
    daily.to_csv(cache_path, index=False)
    return daily


def load_weather(start_date: str, end_date: str, cache_dir: Path) -> pd.DataFrame:
    rows = [
        fetch_city_weather(city, lat, lon, start_date, end_date, cache_dir)
        for city, (lat, lon) in CITIES.items()
    ]
    long = pd.concat(rows, ignore_index=True)
    long["date"] = pd.to_datetime(long["date"]).dt.strftime("%Y-%m-%d")
    return long


def weather_wide(weather: pd.DataFrame) -> pd.DataFrame:
    wide = None
    for city in sorted(weather["city"].unique()):
        city_frame = weather[weather["city"].eq(city)].drop(columns=["city"]).copy()
        renamed = {col: f"weather_{city}_{col}" for col in DAILY_VARIABLES}
        city_frame = city_frame.rename(columns=renamed)
        wide = city_frame if wide is None else wide.merge(city_frame, on="date", how="outer", validate="one_to_one")

    assert wide is not None
    for variable in DAILY_VARIABLES:
        cols = [f"weather_{city}_{variable}" for city in sorted(CITIES)]
        wide[f"weather_kr_mean_{variable}"] = wide[cols].mean(axis=1)
        wide[f"weather_kr_std_{variable}"] = wide[cols].std(axis=1)
        wide[f"weather_kr_min_{variable}"] = wide[cols].min(axis=1)
        wide[f"weather_kr_max_{variable}"] = wide[cols].max(axis=1)

    wide = wide.sort_values("date").reset_index(drop=True)
    numeric_cols = [col for col in wide.columns if col != "date"]
    for col in list(numeric_cols):
        wide[f"{col}_lag1"] = wide[col].shift(1)
        wide[f"{col}_delta1"] = wide[col] - wide[col].shift(1)
        rolling = wide[col].shift(1).rolling(7, min_periods=3).mean()
        wide[f"{col}_dev7"] = wide[col] - rolling
    return wide


def add_panel_features(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame[KEY_COLUMNS].copy()
    ordered = out.reset_index(names="_idx").sort_values(["subject_id", "lifelog_date", "sleep_date"])
    ordered["panel_index"] = ordered.groupby("subject_id").cumcount().astype(float)
    denom = ordered.groupby("subject_id")["panel_index"].transform("max").replace(0, 1)
    ordered["panel_position"] = ordered["panel_index"] / denom
    restored = ordered.sort_values("_idx")
    out["panel_index"] = restored["panel_index"].to_numpy(float)
    out["panel_position"] = restored["panel_position"].to_numpy(float)
    date = pd.to_datetime(out["lifelog_date"])
    dow = date.dt.dayofweek.astype(float)
    doy = date.dt.dayofyear.astype(float)
    out["dow_sin"] = np.sin(2 * np.pi * dow / 7)
    out["dow_cos"] = np.cos(2 * np.pi * dow / 7)
    out["doy_sin"] = np.sin(2 * np.pi * doy / 366)
    out["doy_cos"] = np.cos(2 * np.pi * doy / 366)
    out["is_weekend"] = dow.isin([5, 6]).astype(float)
    return out


def attach_weather(frame: pd.DataFrame, weather: pd.DataFrame) -> pd.DataFrame:
    out = add_panel_features(frame)
    for date_col, prefix in [("lifelog_date", "life"), ("sleep_date", "sleep")]:
        joined = frame[[date_col]].rename(columns={date_col: "date"}).merge(weather, on="date", how="left", validate="many_to_one")
        missing = int(joined.drop(columns=["date"]).isna().all(axis=1).sum())
        if missing:
            raise ValueError(f"{missing} rows missing weather for {date_col}")
        for col in joined.columns:
            if col == "date":
                continue
            out[f"{prefix}_{col}"] = joined[col].to_numpy(float)

    life_cols = [col for col in out.columns if col.startswith("life_weather_")]
    for life_col in life_cols:
        sleep_col = "sleep_" + life_col[len("life_") :]
        if sleep_col in out.columns and not any(life_col.endswith(suffix) for suffix in ["_lag1", "_delta1", "_dev7"]):
            out[f"sleep_minus_life_{life_col[len('life_weather_'):]}"] = out[sleep_col] - out[life_col]
    return out


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
                oof_pred[val_idx, target_i] = np.mean(target_values[trn_idx])
                continue
            model = make_pipeline(
                SimpleImputer(strategy="median"),
                StandardScaler(),
                LogisticRegression(
                    C=spec.c_value,
                    class_weight=spec.class_weight,
                    max_iter=2000,
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
                max_iter=2000,
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


def main() -> None:
    warnings.filterwarnings("ignore", category=PerformanceWarning)
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    min_date = min(train["lifelog_date"].min(), train["sleep_date"].min(), sample["lifelog_date"].min(), sample["sleep_date"].min())
    max_date = max(train["lifelog_date"].max(), train["sleep_date"].max(), sample["lifelog_date"].max(), sample["sleep_date"].max())
    start_date = (pd.Timestamp(min_date) - pd.Timedelta(days=14)).strftime("%Y-%m-%d")
    end_date = (pd.Timestamp(max_date) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    weather = weather_wide(load_weather(start_date, end_date, output_dir / "weather_cache"))
    weather.to_csv(output_dir / "weather_features_by_date.csv", index=False)

    features_train = attach_weather(train, weather)
    features_test = attach_weather(sample, weather)
    weather_cols = [col for col in features_train.columns if col not in KEY_COLUMNS]
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
    c_values = [float(value) for value in args.c_values.split(",") if value.strip()]
    for c_value in c_values:
        c_tag = str(c_value).replace(".", "p")
        specs.append(SourceSpec(f"weather_only_c{c_tag}", weather_cols, c_value, None))
        specs.append(SourceSpec(f"weather_base_c{c_tag}", all_feature_cols, c_value, None))
        specs.append(SourceSpec(f"weather_base_bal_c{c_tag}", all_feature_cols, c_value, "balanced"))

    folds = make_subject_time_folds(train, args.n_folds)
    rows = [train_source(spec, features_train, features_test, train, folds, output_dir) for spec in specs]
    report = pd.DataFrame(rows).sort_values("avg_log_loss").reset_index(drop=True)
    report.to_csv(output_dir / "external_weather_report.csv", index=False)
    (output_dir / "external_weather_report.json").write_text(
        json.dumps(report.to_dict(orient="records"), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    manifest = {
        "weather_source": "Open-Meteo Historical Weather API",
        "cities": {city: {"latitude": lat, "longitude": lon} for city, (lat, lon) in CITIES.items()},
        "date_range": {"start": start_date, "end": end_date},
        "daily_variables": DAILY_VARIABLES,
        "n_weather_features": len(weather_cols),
        "n_base_features": len(base_cols),
        "n_total_features": len(all_feature_cols),
        "base_oof": args.base_oof,
        "base_submission": args.base_submission,
    }
    (output_dir / "feature_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(report[["name", "avg_log_loss", "n_features"]].to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train external weather source decoders over public Korean daily weather.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--base-oof", default="outputs/temporal_retrieval_prototype_portfolio/oof_trp_s2tail_w080_q3midtail_w035.csv")
    parser.add_argument("--base-submission", default="outputs/temporal_retrieval_prototype_portfolio/submission_trp_s2tail_w080_q3midtail_w035.csv")
    parser.add_argument("--output-dir", default="outputs/external_weather_decoder")
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--c-values", default="0.003,0.01,0.03,0.1")
    return parser.parse_args()


if __name__ == "__main__":
    main()
