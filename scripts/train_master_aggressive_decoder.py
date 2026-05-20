from __future__ import annotations

import argparse
import json
import math
import warnings
from dataclasses import dataclass
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd
from pandas.errors import PerformanceWarning
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.preprocessing import StandardScaler


KEY_COLUMNS = ["subject_id", "sleep_date", "lifelog_date"]
TARGET_COLUMNS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
EPS = 1e-5

warnings.filterwarnings("ignore", category=PerformanceWarning)
warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn")


FINDING_CORE_COLUMNS = [
    "mlight_night_h_bright",
    "mlight_night_max",
    "mlight_mean",
    "mlight_max",
    "mlight_h_bright",
    "wlight_h_bright",
    "longest_block_min",
    "tst_min",
    "sleep_eff",
    "sol_proxy_min",
    "n_awakenings",
    "n_awakenings_long",
    "night_hr_mean",
    "night_rmssd",
    "night_sdnn",
    "hr_mean",
    "rmssd_mean",
    "sdnn_mean",
    "gps_home_ratio",
    "gps_elsewhere_ratio",
    "wifi_novelty_ratio",
    "wifi_core_hit",
    "ble_novelty_ratio",
    "ble_core_hit",
    "outings",
    "mob_stationary_min",
    "mob_vehicle_min",
    "mob_walk_min",
    "agree_rate",
    "only_act_rate",
    "only_ped_rate",
    "amb_night_silence",
    "amb_vehicle",
    "amb_music",
    "amb_speech",
    "prebed_sns_sec",
    "prebed_video_sec",
    "prebed_messenger_sec",
    "prebed_os_launcher_sec",
    "app_sns_sec",
    "app_video_sec",
    "app_messenger_sec",
    "z_abs_mean",
    "z_abs_night",
    "z_abs_lateNight",
    "z_night_hr_mean",
    "z_lateNight_hr_mean",
    "z_night_step_sum",
    "z_night_gps_speed_mean",
    "z_earlyAM_step_sum",
    "z_PM_hr_mean",
]


@dataclass(frozen=True)
class ModelSpec:
    name: str
    kind: str
    feature_set: str
    params: dict


def normalize_key_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in KEY_COLUMNS:
        out[col] = out[col].astype(str)
    return out


def assert_unique_keys(df: pd.DataFrame, name: str) -> None:
    duplicates = int(df.duplicated(KEY_COLUMNS).sum())
    if duplicates:
        raise ValueError(f"{name} has {duplicates} duplicated key rows")


def safe_logit(values: np.ndarray) -> np.ndarray:
    values = np.clip(values, EPS, 1.0 - EPS)
    return np.log(values / (1.0 - values))


def sigmoid(values: np.ndarray) -> np.ndarray:
    values = np.clip(values, -40.0, 40.0)
    return 1.0 / (1.0 + np.exp(-values))


def average_log_loss(y_true: pd.DataFrame, pred: np.ndarray) -> tuple[float, dict[str, float]]:
    clipped = np.clip(pred, EPS, 1.0 - EPS)
    per_target = {
        target: float(log_loss(y_true[target].to_numpy(), clipped[:, i], labels=[0, 1]))
        for i, target in enumerate(TARGET_COLUMNS)
    }
    return float(np.mean(list(per_target.values()))), per_target


def load_frames(args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame]:
    master = normalize_key_columns(pd.read_parquet(args.master_path))
    train = normalize_key_columns(pd.read_csv(args.train_path))
    sample = normalize_key_columns(pd.read_csv(args.sample_path))
    for name, df in [("master", master), ("train", train), ("sample", sample)]:
        missing = sorted(set(KEY_COLUMNS) - set(df.columns))
        if missing:
            raise ValueError(f"{name} is missing key columns: {missing}")
        assert_unique_keys(df, name)

    feature_cols = [col for col in master.columns if col not in TARGET_COLUMNS + ["role"]]
    train_joined = train.merge(master[feature_cols], on=KEY_COLUMNS, how="left", validate="one_to_one")
    test_joined = sample[KEY_COLUMNS].merge(master[feature_cols], on=KEY_COLUMNS, how="left", validate="one_to_one")
    if train_joined[["date"]].isna().any().any() or test_joined[["date"]].isna().any().any():
        raise ValueError("Some rows failed to join with master features")

    latent_path = Path(args.latent_path)
    if latent_path.exists():
        latents = normalize_key_columns(pd.read_parquet(latent_path))
        assert_unique_keys(latents, "latents")
        latent_cols = [col for col in latents.columns if col.startswith("z_")]
        renamed = {col: f"latent__{col}" for col in latent_cols}
        latent_features = latents[KEY_COLUMNS + latent_cols].rename(columns=renamed)
        train_joined = train_joined.merge(latent_features, on=KEY_COLUMNS, how="left", validate="one_to_one")
        test_joined = test_joined.merge(latent_features, on=KEY_COLUMNS, how="left", validate="one_to_one")
    return train_joined, test_joined


def add_date_features(all_df: pd.DataFrame) -> pd.DataFrame:
    out = all_df.copy()
    sleep_dt = pd.to_datetime(out["sleep_date"])
    life_dt = pd.to_datetime(out["lifelog_date"])
    out["weekday"] = life_dt.dt.weekday.astype(float)
    out["is_weekend"] = life_dt.dt.weekday.isin([5, 6]).astype(float)
    out["weekday_sin"] = np.sin(2.0 * np.pi * out["weekday"] / 7.0)
    out["weekday_cos"] = np.cos(2.0 * np.pi * out["weekday"] / 7.0)
    out["sleep_weekday"] = sleep_dt.dt.weekday.astype(float)
    out["sleep_weekday_sin"] = np.sin(2.0 * np.pi * out["sleep_weekday"] / 7.0)
    out["sleep_weekday_cos"] = np.cos(2.0 * np.pi * out["sleep_weekday"] / 7.0)
    out["date_ord"] = life_dt.map(pd.Timestamp.toordinal).astype(float)
    out["sleep_date_ord"] = sleep_dt.map(pd.Timestamp.toordinal).astype(float)
    ordered = out.sort_values(["subject_id", "lifelog_date", "sleep_date"]).copy()
    ordered["day_index_subject"] = ordered.groupby("subject_id").cumcount().astype(float)
    max_idx = ordered.groupby("subject_id")["day_index_subject"].transform("max").replace(0.0, 1.0)
    ordered["day_position_subject"] = ordered["day_index_subject"] / max_idx
    return ordered.sort_index()


def add_interactions(all_df: pd.DataFrame) -> list[str]:
    specs = {
        "ix_outings_home": ("outings", "gps_home_ratio"),
        "ix_outings_elsewhere": ("outings", "gps_elsewhere_ratio"),
        "ix_prebed_sns_light": ("prebed_sns_sec", "mlight_night_h_bright"),
        "ix_prebed_video_awake": ("prebed_video_sec", "n_awakenings"),
        "ix_tst_eff": ("tst_min", "sleep_eff"),
        "ix_light_screen_sleep": ("mlight_night_h_bright", "longest_block_min"),
        "ix_coherence_activity": ("agree_rate", "outings"),
        "ix_night_hr_sleep_eff": ("night_hr_mean", "sleep_eff"),
        "ix_home_light": ("gps_home_ratio", "mlight_mean"),
        "ix_sns_eff": ("prebed_sns_sec", "sleep_eff"),
    }
    made = []
    for name, (left, right) in specs.items():
        if left in all_df.columns and right in all_df.columns:
            all_df[name] = pd.to_numeric(all_df[left], errors="coerce") * pd.to_numeric(all_df[right], errors="coerce")
            made.append(name)
    return made


def add_engineered_features(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, list[str]]]:
    all_df = pd.concat(
        [
            train_df.assign(_split="train", _row=np.arange(len(train_df))),
            test_df.assign(_split="test", _row=np.arange(len(test_df))),
        ],
        ignore_index=True,
    )
    all_df = add_date_features(all_df)

    subject_dummies = pd.get_dummies(all_df["subject_id"], prefix="subject", dtype=float)
    all_df = pd.concat([all_df, subject_dummies], axis=1)
    subject_cols = subject_dummies.columns.tolist()

    base_numeric_cols = [
        col
        for col in all_df.columns
        if col not in KEY_COLUMNS + TARGET_COLUMNS + ["date", "_split", "_row"]
        and pd.api.types.is_numeric_dtype(all_df[col])
    ]
    base_numeric_cols = sorted(dict.fromkeys(base_numeric_cols))

    missing_cols = []
    for col in base_numeric_cols:
        miss_rate = float(all_df[col].isna().mean())
        if 0.0 < miss_rate < 1.0:
            miss_col = f"miss__{col}"
            all_df[miss_col] = all_df[col].isna().astype(float)
            missing_cols.append(miss_col)

    log_cols = []
    for col in base_numeric_cols:
        values = pd.to_numeric(all_df[col], errors="coerce")
        finite = values[np.isfinite(values)]
        if len(finite) and finite.min() >= 0 and finite.quantile(0.95) > 10:
            log_col = f"log1p__{col}"
            all_df[log_col] = np.log1p(values)
            log_cols.append(log_col)

    interaction_cols = add_interactions(all_df)

    transductive_source_cols = [
        col
        for col in base_numeric_cols
        if col not in subject_cols
        and not col.startswith("latent__")
        and col not in ["weekday", "sleep_weekday", "date_ord", "sleep_date_ord"]
    ]
    centered_cols = []
    rank_cols = []
    grouped = all_df.groupby("subject_id", sort=False)
    for col in transductive_source_cols:
        values = pd.to_numeric(all_df[col], errors="coerce")
        center_col = f"sub_center__{col}"
        all_df[center_col] = values - grouped[col].transform("mean")
        centered_cols.append(center_col)

        rank_col = f"sub_rank__{col}"
        all_df[rank_col] = grouped[col].rank(method="average", pct=True)
        rank_cols.append(rank_col)

    time_cols = [
        "weekday",
        "is_weekend",
        "weekday_sin",
        "weekday_cos",
        "sleep_weekday",
        "sleep_weekday_sin",
        "sleep_weekday_cos",
        "day_index_subject",
        "day_position_subject",
    ]
    latent_cols = sorted(col for col in all_df.columns if col.startswith("latent__z_"))
    finding_cols = [col for col in FINDING_CORE_COLUMNS if col in all_df.columns]
    finding_aug_cols = []
    for col in finding_cols:
        finding_aug_cols.extend([col, f"sub_center__{col}", f"sub_rank__{col}", f"miss__{col}", f"log1p__{col}"])
    finding_aug_cols = [col for col in dict.fromkeys(finding_aug_cols) if col in all_df.columns]

    all_numeric = [
        col
        for col in all_df.columns
        if col not in KEY_COLUMNS + TARGET_COLUMNS + ["date", "_split", "_row"]
        and pd.api.types.is_numeric_dtype(all_df[col])
    ]
    all_numeric = sorted(dict.fromkeys(all_numeric))
    no_subject_cols = [col for col in all_numeric if not col.startswith("subject_")]
    rankdev_cols = sorted(dict.fromkeys(base_numeric_cols + log_cols + missing_cols + centered_cols + rank_cols + interaction_cols + time_cols + subject_cols))

    feature_sets = {
        "finding_core": sorted(dict.fromkeys(finding_aug_cols + interaction_cols + time_cols + subject_cols)),
        "master_raw": sorted(dict.fromkeys(base_numeric_cols + log_cols + missing_cols + interaction_cols + time_cols + subject_cols)),
        "master_rankdev": rankdev_cols,
        "no_subject_rankdev": sorted(dict.fromkeys([col for col in rankdev_cols if col not in subject_cols])),
        "all_numeric": all_numeric,
        "no_subject_all": no_subject_cols,
    }
    if latent_cols:
        feature_sets["latent"] = latent_cols + time_cols + subject_cols
        feature_sets["latent_master_rankdev"] = sorted(dict.fromkeys(latent_cols + rankdev_cols))

    train_out = all_df[all_df["_split"] == "train"].sort_values("_row").drop(columns=["_split", "_row"]).reset_index(drop=True)
    test_out = all_df[all_df["_split"] == "test"].sort_values("_row").drop(columns=["_split", "_row"]).reset_index(drop=True)
    return train_out, test_out, feature_sets


def make_subject_time_folds(train_df: pd.DataFrame, n_folds: int) -> list[tuple[np.ndarray, np.ndarray]]:
    val_indices: list[list[int]] = [[] for _ in range(n_folds)]
    ordered = train_df.reset_index(names="_idx").sort_values(["subject_id", "lifelog_date", "sleep_date"])
    for _, group in ordered.groupby("subject_id", sort=False):
        chunks = np.array_split(group["_idx"].to_numpy(), n_folds)
        for fold, chunk in enumerate(chunks):
            val_indices[fold].extend(chunk.tolist())

    all_indices = np.arange(len(train_df))
    folds = []
    for fold_indices in val_indices:
        val_idx = np.array(sorted(fold_indices), dtype=int)
        train_idx = np.setdiff1d(all_indices, val_idx, assume_unique=False)
        folds.append((train_idx, val_idx))
    return folds


def subject_prior_predictions(train_part: pd.DataFrame, eval_part: pd.DataFrame, alpha: float) -> np.ndarray:
    global_rate = train_part[TARGET_COLUMNS].mean()
    subject_sum = train_part.groupby("subject_id")[TARGET_COLUMNS].sum()
    subject_count = train_part.groupby("subject_id")[TARGET_COLUMNS].count()
    subject_rate = (subject_sum + alpha * global_rate) / (subject_count + alpha)
    pred = np.zeros((len(eval_part), len(TARGET_COLUMNS)), dtype=float)
    for row_i, subject in enumerate(eval_part["subject_id"]):
        if subject in subject_rate.index:
            pred[row_i] = subject_rate.loc[subject, TARGET_COLUMNS].to_numpy(dtype=float)
        else:
            pred[row_i] = global_rate.to_numpy(dtype=float)
    return np.clip(pred, EPS, 1.0 - EPS)


def oof_subject_prior(train_df: pd.DataFrame, folds: list[tuple[np.ndarray, np.ndarray]], alpha: float) -> np.ndarray:
    pred = np.zeros((len(train_df), len(TARGET_COLUMNS)), dtype=float)
    for train_idx, val_idx in folds:
        pred[val_idx] = subject_prior_predictions(train_df.iloc[train_idx], train_df.iloc[val_idx], alpha)
    return pred


def fit_target_logreg(x_train: np.ndarray, y_train: np.ndarray, params: dict) -> LogisticRegression | float:
    classes = np.unique(y_train)
    if len(classes) < 2:
        return float(classes[0])
    model = LogisticRegression(
        C=float(params["C"]),
        solver="lbfgs",
        max_iter=5000,
        class_weight=params.get("class_weight"),
    )
    model.fit(x_train, y_train)
    return model


def model_predict_proba(model: LogisticRegression | lgb.LGBMClassifier | float, x_eval: np.ndarray | pd.DataFrame) -> np.ndarray:
    if isinstance(model, float):
        return np.full(len(x_eval), model, dtype=float)
    return model.predict_proba(x_eval)[:, 1]


def oof_logreg(
    train_df: pd.DataFrame,
    feature_cols: list[str],
    folds: list[tuple[np.ndarray, np.ndarray]],
    params: dict,
) -> np.ndarray:
    pred = np.zeros((len(train_df), len(TARGET_COLUMNS)), dtype=float)
    x_all = train_df[feature_cols].to_numpy(dtype=np.float64).copy()
    x_all[~np.isfinite(x_all)] = np.nan
    y_all = train_df[TARGET_COLUMNS].astype(int).reset_index(drop=True)
    for train_idx, val_idx in folds:
        imputer = SimpleImputer(strategy="median", keep_empty_features=True)
        scaler = StandardScaler()
        x_train = scaler.fit_transform(imputer.fit_transform(x_all[train_idx]))
        x_val = scaler.transform(imputer.transform(x_all[val_idx]))
        for target_i, target in enumerate(TARGET_COLUMNS):
            model = fit_target_logreg(x_train, y_all.loc[train_idx, target].to_numpy(), params)
            pred[val_idx, target_i] = model_predict_proba(model, x_val)
    return np.clip(pred, EPS, 1.0 - EPS)


def fit_full_logreg_predict(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    feature_cols: list[str],
    params: dict,
) -> np.ndarray:
    x_train = train_df[feature_cols].to_numpy(dtype=np.float64).copy()
    x_test = test_df[feature_cols].to_numpy(dtype=np.float64).copy()
    x_train[~np.isfinite(x_train)] = np.nan
    x_test[~np.isfinite(x_test)] = np.nan
    imputer = SimpleImputer(strategy="median", keep_empty_features=True)
    scaler = StandardScaler()
    x_train_scaled = scaler.fit_transform(imputer.fit_transform(x_train))
    x_test_scaled = scaler.transform(imputer.transform(x_test))
    pred = np.zeros((len(test_df), len(TARGET_COLUMNS)), dtype=float)
    y_all = train_df[TARGET_COLUMNS].astype(int)
    for target_i, target in enumerate(TARGET_COLUMNS):
        model = fit_target_logreg(x_train_scaled, y_all[target].to_numpy(), params)
        pred[:, target_i] = model_predict_proba(model, x_test_scaled)
    return np.clip(pred, EPS, 1.0 - EPS)


def fit_target_lgbm(x_train: pd.DataFrame, y_train: np.ndarray, params: dict) -> lgb.LGBMClassifier | float:
    classes = np.unique(y_train)
    if len(classes) < 2:
        return float(classes[0])
    model = lgb.LGBMClassifier(**params)
    model.fit(x_train, y_train)
    return model


def oof_lgbm(
    train_df: pd.DataFrame,
    feature_cols: list[str],
    folds: list[tuple[np.ndarray, np.ndarray]],
    params: dict,
) -> np.ndarray:
    pred = np.zeros((len(train_df), len(TARGET_COLUMNS)), dtype=float)
    x_all = train_df[feature_cols].replace([np.inf, -np.inf], np.nan)
    y_all = train_df[TARGET_COLUMNS].astype(int).reset_index(drop=True)
    for train_idx, val_idx in folds:
        x_train = x_all.iloc[train_idx]
        x_val = x_all.iloc[val_idx]
        for target_i, target in enumerate(TARGET_COLUMNS):
            model = fit_target_lgbm(x_train, y_all.loc[train_idx, target].to_numpy(), params)
            pred[val_idx, target_i] = model_predict_proba(model, x_val)
    return np.clip(pred, EPS, 1.0 - EPS)


def fit_full_lgbm_predict(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    feature_cols: list[str],
    params: dict,
) -> np.ndarray:
    x_train = train_df[feature_cols].replace([np.inf, -np.inf], np.nan)
    x_test = test_df[feature_cols].replace([np.inf, -np.inf], np.nan)
    pred = np.zeros((len(test_df), len(TARGET_COLUMNS)), dtype=float)
    y_all = train_df[TARGET_COLUMNS].astype(int)
    for target_i, target in enumerate(TARGET_COLUMNS):
        model = fit_target_lgbm(x_train, y_all[target].to_numpy(), params)
        pred[:, target_i] = model_predict_proba(model, x_test)
    return np.clip(pred, EPS, 1.0 - EPS)


def solve_intercept(scores: np.ndarray, target_mean: float) -> float:
    target_mean = float(np.clip(target_mean, EPS, 1.0 - EPS))
    if len(scores) == 0:
        return safe_logit(np.array([target_mean]))[0]
    lo, hi = -25.0, 25.0
    for _ in range(80):
        mid = (lo + hi) / 2.0
        mean = float(sigmoid(scores + mid).mean())
        if mean < target_mean:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def subject_rates(train_part: pd.DataFrame, alpha: float) -> pd.DataFrame:
    global_rate = train_part[TARGET_COLUMNS].mean()
    subject_sum = train_part.groupby("subject_id")[TARGET_COLUMNS].sum()
    subject_count = train_part.groupby("subject_id")[TARGET_COLUMNS].count()
    return (subject_sum + alpha * global_rate) / (subject_count + alpha)


def subject_rank_recalibrate(
    base_pred: np.ndarray,
    eval_df: pd.DataFrame,
    rate_table: pd.DataFrame,
    fallback_rate: pd.Series,
    beta: float,
) -> np.ndarray:
    out = np.zeros_like(base_pred, dtype=float)
    logits = safe_logit(base_pred)
    for target_i, target in enumerate(TARGET_COLUMNS):
        for subject, group in eval_df.reset_index().groupby("subject_id", sort=False):
            idx = group["index"].to_numpy()
            local = logits[idx, target_i]
            finite = np.isfinite(local)
            if finite.sum() >= 2:
                mean = float(np.nanmean(local))
                std = float(np.nanstd(local))
                if std > 1e-8:
                    score = beta * ((local - mean) / std)
                else:
                    score = np.zeros_like(local)
            else:
                score = np.zeros_like(local)
            if subject in rate_table.index:
                target_mean = float(rate_table.loc[subject, target])
            else:
                target_mean = float(fallback_rate[target])
            intercept = solve_intercept(score, target_mean)
            out[idx, target_i] = sigmoid(score + intercept)
    return np.clip(out, EPS, 1.0 - EPS)


def oof_rank_recalibrate(
    base_pred: np.ndarray,
    train_df: pd.DataFrame,
    folds: list[tuple[np.ndarray, np.ndarray]],
    alpha: float,
    beta: float,
) -> np.ndarray:
    out = np.zeros_like(base_pred, dtype=float)
    for train_idx, val_idx in folds:
        part = train_df.iloc[train_idx]
        eval_part = train_df.iloc[val_idx].reset_index(drop=True)
        rates = subject_rates(part, alpha)
        fallback = part[TARGET_COLUMNS].mean()
        out[val_idx] = subject_rank_recalibrate(base_pred[val_idx], eval_part, rates, fallback, beta)
    return np.clip(out, EPS, 1.0 - EPS)


def test_rank_recalibrate(
    base_pred: np.ndarray,
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    alpha: float,
    beta: float,
) -> np.ndarray:
    return subject_rank_recalibrate(
        base_pred,
        test_df.reset_index(drop=True),
        subject_rates(train_df, alpha),
        train_df[TARGET_COLUMNS].mean(),
        beta,
    )


def make_model_specs(feature_sets: dict[str, list[str]], args: argparse.Namespace) -> list[ModelSpec]:
    specs: list[ModelSpec] = []
    selected_feature_sets = [name for name in args.feature_sets.split(",") if name in feature_sets]
    for feature_set in selected_feature_sets:
        for c_value in [float(v) for v in args.c_values.split(",") if v]:
            specs.append(ModelSpec(f"logreg_{feature_set}_C{c_value:g}", "logreg", feature_set, {"C": c_value}))
    lgbm_params = [
        {
            "n_estimators": 60,
            "learning_rate": 0.035,
            "num_leaves": 3,
            "max_depth": 2,
            "min_child_samples": 28,
            "subsample": 0.85,
            "subsample_freq": 1,
            "colsample_bytree": 0.65,
            "reg_alpha": 0.2,
            "reg_lambda": 12.0,
            "min_split_gain": 0.0,
            "objective": "binary",
            "verbosity": -1,
            "random_state": args.seed,
        },
        {
            "n_estimators": 90,
            "learning_rate": 0.025,
            "num_leaves": 5,
            "max_depth": 3,
            "min_child_samples": 20,
            "subsample": 0.8,
            "subsample_freq": 1,
            "colsample_bytree": 0.55,
            "reg_alpha": 0.5,
            "reg_lambda": 18.0,
            "min_split_gain": 0.01,
            "objective": "binary",
            "verbosity": -1,
            "random_state": args.seed + 17,
        },
    ]
    lgbm_feature_sets = [name for name in selected_feature_sets if name in {"finding_core", "master_raw", "master_rankdev", "no_subject_rankdev", "latent_master_rankdev"}]
    for feature_set in lgbm_feature_sets:
        for i, params in enumerate(lgbm_params, start=1):
            specs.append(ModelSpec(f"lgbm{i}_{feature_set}", "lgbm", feature_set, params))
    return specs


def fit_oof_model(
    spec: ModelSpec,
    train_df: pd.DataFrame,
    feature_sets: dict[str, list[str]],
    folds: list[tuple[np.ndarray, np.ndarray]],
) -> np.ndarray:
    cols = feature_sets[spec.feature_set]
    if spec.kind == "logreg":
        return oof_logreg(train_df, cols, folds, spec.params)
    if spec.kind == "lgbm":
        return oof_lgbm(train_df, cols, folds, spec.params)
    raise ValueError(f"Unknown model kind: {spec.kind}")


def fit_test_model(
    spec: ModelSpec,
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    feature_sets: dict[str, list[str]],
) -> np.ndarray:
    cols = feature_sets[spec.feature_set]
    if spec.kind == "logreg":
        return fit_full_logreg_predict(train_df, test_df, cols, spec.params)
    if spec.kind == "lgbm":
        return fit_full_lgbm_predict(train_df, test_df, cols, spec.params)
    raise ValueError(f"Unknown model kind: {spec.kind}")


def evaluate(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    feature_sets: dict[str, list[str]],
    folds: list[tuple[np.ndarray, np.ndarray]],
    args: argparse.Namespace,
) -> tuple[pd.DataFrame, dict[str, np.ndarray], dict[str, np.ndarray]]:
    y_true = train_df[TARGET_COLUMNS]
    scores = []
    oof_cache: dict[str, np.ndarray] = {}
    test_cache: dict[str, np.ndarray] = {}

    for alpha in [float(v) for v in args.prior_alphas.split(",") if v]:
        name = f"subject_prior_a{alpha:g}"
        oof = oof_subject_prior(train_df, folds, alpha)
        test = subject_prior_predictions(train_df, test_df, alpha)
        oof_cache[name] = oof
        test_cache[name] = test
        score, per_target = average_log_loss(y_true, oof)
        scores.append({"name": name, "kind": "prior", "base_model": "", "alpha": alpha, "beta": math.nan, "weight": math.nan, "avg_log_loss": score, **per_target})

    model_specs = make_model_specs(feature_sets, args)
    blend_weights = [float(v) for v in args.blend_weights.split(",") if v]
    rank_betas = [float(v) for v in args.rank_betas.split(",") if v]
    rank_alphas = [float(v) for v in args.rank_alphas.split(",") if v]
    prior_alphas = [float(v) for v in args.prior_alphas.split(",") if v]

    for spec_i, spec in enumerate(model_specs, start=1):
        print(f"[{spec_i}/{len(model_specs)}] fitting {spec.name} ({len(feature_sets[spec.feature_set])} features)")
        oof = fit_oof_model(spec, train_df, feature_sets, folds)
        test = fit_test_model(spec, train_df, test_df, feature_sets)
        oof_cache[spec.name] = oof
        test_cache[spec.name] = test
        score, per_target = average_log_loss(y_true, oof)
        scores.append({"name": spec.name, "kind": spec.kind, "base_model": spec.name, "feature_set": spec.feature_set, "alpha": math.nan, "beta": math.nan, "weight": 1.0, "avg_log_loss": score, **per_target})

        for alpha in prior_alphas:
            prior_name = f"subject_prior_a{alpha:g}"
            prior_oof = oof_cache[prior_name]
            prior_test = test_cache[prior_name]
            for weight in blend_weights:
                name = f"blend_w{weight:g}_{spec.name}_a{alpha:g}"
                blend_oof = np.clip(weight * oof + (1.0 - weight) * prior_oof, EPS, 1.0 - EPS)
                blend_test = np.clip(weight * test + (1.0 - weight) * prior_test, EPS, 1.0 - EPS)
                oof_cache[name] = blend_oof
                test_cache[name] = blend_test
                score, per_target = average_log_loss(y_true, blend_oof)
                scores.append({"name": name, "kind": "blend", "base_model": spec.name, "feature_set": spec.feature_set, "alpha": alpha, "beta": math.nan, "weight": weight, "avg_log_loss": score, **per_target})

        for alpha in rank_alphas:
            for beta in rank_betas:
                name = f"rankcal_b{beta:g}_{spec.name}_a{alpha:g}"
                rank_oof = oof_rank_recalibrate(oof, train_df, folds, alpha, beta)
                rank_test = test_rank_recalibrate(test, train_df, test_df, alpha, beta)
                oof_cache[name] = rank_oof
                test_cache[name] = rank_test
                score, per_target = average_log_loss(y_true, rank_oof)
                scores.append({"name": name, "kind": "rankcal", "base_model": spec.name, "feature_set": spec.feature_set, "alpha": alpha, "beta": beta, "weight": math.nan, "avg_log_loss": score, **per_target})

    scores_df = pd.DataFrame(scores).sort_values("avg_log_loss", ascending=True).reset_index(drop=True)
    return scores_df, oof_cache, test_cache


def build_targetwise_outputs(
    train_df: pd.DataFrame,
    sample_path: Path,
    scores: pd.DataFrame,
    oof_cache: dict[str, np.ndarray],
    test_cache: dict[str, np.ndarray],
    output_dir: Path,
) -> tuple[pd.DataFrame, np.ndarray, np.ndarray, dict[str, float]]:
    y_true = train_df[TARGET_COLUMNS]
    selected_rows = []
    oof_targetwise = np.zeros((len(train_df), len(TARGET_COLUMNS)), dtype=float)
    test_targetwise = None
    for target_i, target in enumerate(TARGET_COLUMNS):
        row = scores.sort_values(target).iloc[0].to_dict()
        selected_rows.append({"target": target, **row})
        oof_targetwise[:, target_i] = oof_cache[str(row["name"])][:, target_i]
        if test_targetwise is None:
            test_targetwise = np.zeros_like(test_cache[str(row["name"])])
        test_targetwise[:, target_i] = test_cache[str(row["name"])][:, target_i]

    assert test_targetwise is not None
    oof_targetwise = np.clip(oof_targetwise, EPS, 1.0 - EPS)
    test_targetwise = np.clip(test_targetwise, EPS, 1.0 - EPS)
    avg, per_target = average_log_loss(y_true, oof_targetwise)
    selected = pd.DataFrame(selected_rows)
    selected["targetwise_avg_log_loss"] = avg
    selected.to_csv(output_dir / "targetwise_selection.csv", index=False)

    oof_df = train_df[KEY_COLUMNS + TARGET_COLUMNS].copy()
    for target_i, target in enumerate(TARGET_COLUMNS):
        oof_df[f"pred_{target}"] = oof_targetwise[:, target_i]
    oof_df.to_csv(output_dir / "oof_targetwise.csv", index=False)

    sample = pd.read_csv(sample_path)
    submission = sample.copy()
    for target_i, target in enumerate(TARGET_COLUMNS):
        submission[target] = test_targetwise[:, target_i]
    submission.to_csv(output_dir / "submission_master_aggressive_targetwise.csv", index=False)
    pd.DataFrame([{"name": "targetwise_best", "avg_log_loss": avg, **per_target}]).to_csv(output_dir / "targetwise_score.csv", index=False)
    return selected, oof_targetwise, test_targetwise, {"avg_log_loss": avg, **per_target}


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    display = df.copy()
    for col in display.columns:
        if pd.api.types.is_float_dtype(display[col]):
            display[col] = display[col].map(lambda value: "" if pd.isna(value) else f"{value:.6f}")
        else:
            display[col] = display[col].map(lambda value: "" if pd.isna(value) else str(value))
    header = "| " + " | ".join(display.columns) + " |"
    separator = "| " + " | ".join(["---"] * len(display.columns)) + " |"
    rows = ["| " + " | ".join(row) + " |" for row in display.astype(str).to_numpy()]
    return "\n".join([header, separator, *rows])


def write_report(
    output_dir: Path,
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    feature_sets: dict[str, list[str]],
    scores: pd.DataFrame,
    targetwise_selection: pd.DataFrame,
    targetwise_score: dict[str, float],
    test_pred: np.ndarray,
    args: argparse.Namespace,
) -> None:
    report = {
        "metric": "Average Log-Loss",
        "train_rows": int(len(train_df)),
        "test_rows": int(len(test_df)),
        "feature_set_sizes": {name: len(cols) for name, cols in feature_sets.items()},
        "top_candidates": scores.head(30).to_dict(orient="records"),
        "targetwise_score": targetwise_score,
        "targetwise_selection": targetwise_selection.to_dict(orient="records"),
        "targetwise_prediction_summary": {
            target: {
                "min": float(test_pred[:, i].min()),
                "mean": float(test_pred[:, i].mean()),
                "max": float(test_pred[:, i].max()),
            }
            for i, target in enumerate(TARGET_COLUMNS)
        },
        "args": vars(args),
    }
    (output_dir / "master_aggressive_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    top_cols = ["name", "kind", "avg_log_loss", *TARGET_COLUMNS]
    lines = [
        "# Master aggressive decoder report",
        "",
        f"- Train rows: {len(train_df)}",
        f"- Test rows: {len(test_df)}",
        f"- Best global CV: {scores.iloc[0]['avg_log_loss']:.6f} (`{scores.iloc[0]['name']}`)",
        f"- Target-wise CV: {targetwise_score['avg_log_loss']:.6f}",
        "",
        "## Top candidates",
        "",
        dataframe_to_markdown(scores.head(12)[top_cols]),
        "",
        "## Target-wise selection",
        "",
        dataframe_to_markdown(targetwise_selection[["target", "name", "kind", "avg_log_loss", *TARGET_COLUMNS]]),
        "",
        "## Feature set sizes",
        "",
    ]
    for name, cols in feature_sets.items():
        lines.append(f"- {name}: {len(cols)}")
    lines.append("")
    (output_dir / "master_aggressive_report.md").write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Aggressive decoder over master daily lifelog features.")
    parser.add_argument("--master-path", default="artifacts/10_master_daily.parquet")
    parser.add_argument("--latent-path", default="outputs/diffusion_encoder/day_latents.parquet")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--output-dir", default="outputs/master_aggressive_decoder")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--feature-sets", default="finding_core,master_raw,master_rankdev,no_subject_rankdev,latent,latent_master_rankdev")
    parser.add_argument("--c-values", default="0.01,0.03,0.1,0.3")
    parser.add_argument("--prior-alphas", default="2,5,10,20,50,100")
    parser.add_argument("--blend-weights", default="0.05,0.1,0.2,0.3,0.4,0.5,0.65,0.8")
    parser.add_argument("--rank-alphas", default="2,5,10,20,50")
    parser.add_argument("--rank-betas", default="0,0.15,0.3,0.5,0.75,1,1.5,2")
    parser.add_argument("--seed", type=int, default=2026)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    train_df, test_df = load_frames(args)
    train_df, test_df, feature_sets = add_engineered_features(train_df, test_df)
    folds = make_subject_time_folds(train_df, args.folds)
    scores, oof_cache, test_cache = evaluate(train_df, test_df, feature_sets, folds, args)
    scores.to_csv(output_dir / "candidate_scores.csv", index=False)

    best_name = str(scores.iloc[0]["name"])
    best_oof = oof_cache[best_name]
    best_test = test_cache[best_name]
    best_oof_df = train_df[KEY_COLUMNS + TARGET_COLUMNS].copy()
    for target_i, target in enumerate(TARGET_COLUMNS):
        best_oof_df[f"pred_{target}"] = best_oof[:, target_i]
    best_oof_df.to_csv(output_dir / "oof_best.csv", index=False)

    sample = pd.read_csv(args.sample_path)
    best_submission = sample.copy()
    for target_i, target in enumerate(TARGET_COLUMNS):
        best_submission[target] = best_test[:, target_i]
    best_submission.to_csv(output_dir / "submission_master_aggressive_best.csv", index=False)

    targetwise_selection, _, targetwise_test, targetwise_score = build_targetwise_outputs(
        train_df=train_df,
        sample_path=Path(args.sample_path),
        scores=scores,
        oof_cache=oof_cache,
        test_cache=test_cache,
        output_dir=output_dir,
    )
    write_report(output_dir, train_df, test_df, feature_sets, scores, targetwise_selection, targetwise_score, targetwise_test, args)

    print(f"best={best_name} avg_log_loss={scores.iloc[0]['avg_log_loss']:.6f}")
    print(f"targetwise_avg_log_loss={targetwise_score['avg_log_loss']:.6f}")
    print(f"saved report: {output_dir / 'master_aggressive_report.md'}")
    print(f"saved submission: {output_dir / 'submission_master_aggressive_targetwise.csv'}")


if __name__ == "__main__":
    main()
