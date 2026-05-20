from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


KEY_COLUMNS = ["subject_id", "sleep_date", "lifelog_date"]
TARGET_COLUMNS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
EPS = 1e-5


CORE_COLUMNS = [
    "mlight_night_h_bright",
    "mlight_night_max",
    "mlight_mean",
    "mlight_max",
    "wlight_h_bright",
    "day_screen_on_ratio",
    "longest_block_min",
    "tst_min",
    "sleep_eff",
    "sol_proxy_min",
    "n_awakenings",
    "n_awakenings_long",
    "night_hr_mean",
    "night_rmssd",
    "night_sdnn",
    "gps_home_ratio",
    "gps_elsewhere_ratio",
    "gps_cluster_count",
    "gps_distance_km",
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
]


@dataclass(frozen=True)
class ModelSpec:
    name: str
    kind: str
    feature_set: str
    value: float
    weight_mode: str


@dataclass(frozen=True)
class Window:
    name: str
    lo: float
    hi: float


def normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in KEY_COLUMNS:
        out[col] = out[col].astype(str)
    return out


def parse_float_list(value: str) -> list[float]:
    return [float(part) for part in value.split(",") if part.strip()]


def parse_str_list(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def parse_windows(value: str) -> list[Window]:
    windows: list[Window] = []
    for item in value.split(","):
        if not item.strip():
            continue
        name, lo, hi = item.split(":")
        windows.append(Window(name, float(lo), float(hi)))
    return windows


def safe_logit(values: np.ndarray) -> np.ndarray:
    values = np.clip(values, EPS, 1.0 - EPS)
    return np.log(values / (1.0 - values))


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(values, -50.0, 50.0)))


def blend_values(base: np.ndarray, source: np.ndarray, weight: float, mode: str) -> np.ndarray:
    if mode == "prob":
        out = base + weight * (source - base)
    elif mode == "logit":
        out = sigmoid(safe_logit(base) + weight * (safe_logit(source) - safe_logit(base)))
    else:
        raise ValueError(f"Unknown blend mode: {mode}")
    return np.clip(out, EPS, 1.0 - EPS)


def prediction_matrix(oof: pd.DataFrame) -> np.ndarray:
    cols = [f"pred_{target}" for target in TARGET_COLUMNS]
    missing = sorted(set(cols) - set(oof.columns))
    if missing:
        raise ValueError(f"OOF file missing prediction columns: {missing}")
    return np.clip(oof[cols].to_numpy(dtype=float), EPS, 1.0 - EPS)


def submission_matrix(submission: pd.DataFrame) -> np.ndarray:
    missing = sorted(set(TARGET_COLUMNS) - set(submission.columns))
    if missing:
        raise ValueError(f"Submission file missing target columns: {missing}")
    return np.clip(submission[TARGET_COLUMNS].to_numpy(dtype=float), EPS, 1.0 - EPS)


def make_subject_time_folds(frame: pd.DataFrame, n_folds: int) -> list[tuple[np.ndarray, np.ndarray]]:
    ordered = frame.reset_index(names="_idx").sort_values(["subject_id", "lifelog_date", "sleep_date"])
    val_indices: list[list[int]] = [[] for _ in range(n_folds)]
    for _, group in ordered.groupby("subject_id", sort=False):
        chunks = np.array_split(group["_idx"].to_numpy(), n_folds)
        for fold, chunk in enumerate(chunks):
            val_indices[fold].extend(chunk.tolist())
    all_idx = np.arange(len(frame), dtype=int)
    folds = []
    for indices in val_indices:
        val_idx = np.array(sorted(indices), dtype=int)
        train_idx = np.setdiff1d(all_idx, val_idx, assume_unique=False)
        folds.append((train_idx, val_idx))
    return folds


def add_panel_position(train: pd.DataFrame, sample: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    all_rows = pd.concat(
        [
            train[KEY_COLUMNS].assign(_split="train", _row=np.arange(len(train))),
            sample[KEY_COLUMNS].assign(_split="sample", _row=np.arange(len(sample))),
        ],
        ignore_index=True,
    )
    all_rows = all_rows.sort_values(["subject_id", "lifelog_date", "sleep_date"]).copy()
    all_rows["panel_index"] = all_rows.groupby("subject_id").cumcount().astype(float)
    denom = all_rows.groupby("subject_id")["panel_index"].transform("max").replace(0.0, 1.0)
    all_rows["panel_position"] = all_rows["panel_index"] / denom
    train_pos = all_rows[all_rows["_split"].eq("train")].sort_values("_row")[["panel_index", "panel_position"]].reset_index(drop=True)
    sample_pos = all_rows[all_rows["_split"].eq("sample")].sort_values("_row")[["panel_index", "panel_position"]].reset_index(drop=True)
    train_out = train.reset_index(drop=True).copy()
    sample_out = sample.reset_index(drop=True).copy()
    train_out[["panel_index", "panel_position"]] = train_pos
    sample_out[["panel_index", "panel_position"]] = sample_pos
    return train_out, sample_out


def position_bins(value: str) -> np.ndarray:
    bins = np.asarray(parse_float_list(value), dtype=float)
    if len(bins) < 2:
        raise ValueError("At least two position bins are required")
    bins[-1] = bins[-1] + 1e-6
    return bins


def sample_position_weights(train: pd.DataFrame, sample: pd.DataFrame, bins: np.ndarray) -> np.ndarray:
    train_bin = np.digitize(train["panel_position"].to_numpy(dtype=float), bins) - 1
    sample_bin = np.digitize(sample["panel_position"].to_numpy(dtype=float), bins) - 1
    n_bins = len(bins) - 1
    train_frac = np.bincount(train_bin, minlength=n_bins).astype(float) / max(len(train_bin), 1)
    sample_frac = np.bincount(sample_bin, minlength=n_bins).astype(float) / max(len(sample_bin), 1)
    ratio = np.divide(sample_frac, train_frac, out=np.zeros(n_bins, dtype=float), where=train_frac > 0)
    weights = ratio[train_bin]
    if float(weights.mean()) > 0:
        weights = weights / float(weights.mean())
    return np.clip(weights, 0.0, 12.0)


def sample_support_mask(frame: pd.DataFrame, sample: pd.DataFrame, bins: np.ndarray) -> np.ndarray:
    frame_bin = np.digitize(frame["panel_position"].to_numpy(dtype=float), bins) - 1
    sample_bin = np.digitize(sample["panel_position"].to_numpy(dtype=float), bins) - 1
    sample_counts = np.bincount(sample_bin, minlength=len(bins) - 1)
    return (sample_counts > 0)[frame_bin]


def build_fit_weights(train: pd.DataFrame, sample: pd.DataFrame, bins: np.ndarray, mode: str) -> np.ndarray:
    base = np.ones(len(train), dtype=float)
    sample_w = sample_position_weights(train, sample, bins)
    pos = train["panel_position"].to_numpy(dtype=float)
    supported = sample_support_mask(train, sample, bins)
    if mode == "uniform":
        weights = base
    elif mode == "sample":
        weights = sample_w
    elif mode == "support":
        weights = np.where(supported, 2.5, 0.4)
    elif mode == "tail3":
        weights = sample_w * np.where(pos >= 0.8, 3.0, 1.0)
    elif mode == "tail5":
        weights = sample_w * np.where(pos >= 0.8, 5.0, 1.0)
    elif mode == "midtail":
        weights = np.where(pos >= (1.0 / 3.0), sample_w + 0.5, 0.25)
    else:
        raise ValueError(f"Unknown weight mode: {mode}")
    if float(weights.mean()) > 0:
        weights = weights / float(weights.mean())
    return np.clip(weights, 0.05, 20.0)


def load_base_predictions(args: argparse.Namespace, train: pd.DataFrame, sample: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    oof = normalize_keys(pd.read_csv(args.base_oof))
    submission = normalize_keys(pd.read_csv(args.base_submission))
    if not oof[KEY_COLUMNS].equals(train[KEY_COLUMNS]):
        raise ValueError("Base OOF keys do not match train keys")
    if not submission[KEY_COLUMNS].equals(sample[KEY_COLUMNS]):
        raise ValueError("Base submission keys do not match sample keys")
    return prediction_matrix(oof), submission_matrix(submission)


def load_joined(args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray, np.ndarray]:
    train_raw = normalize_keys(pd.read_csv(args.train_path))
    sample_raw = normalize_keys(pd.read_csv(args.sample_path))
    train_raw, sample_raw = add_panel_position(train_raw, sample_raw)

    master = normalize_keys(pd.read_parquet(args.master_path))
    keep = [col for col in master.columns if col not in TARGET_COLUMNS + ["role"]]
    train_x = train_raw.merge(master[keep], on=KEY_COLUMNS, how="left", validate="one_to_one")
    test_x = sample_raw[KEY_COLUMNS].merge(master[keep], on=KEY_COLUMNS, how="left", validate="one_to_one")
    if train_x["date"].isna().any() or test_x["date"].isna().any():
        raise ValueError("Some rows failed to join with master features")

    latent_path = Path(args.latent_path)
    if latent_path.exists():
        latents = normalize_keys(pd.read_parquet(latent_path))
        latent_cols = [col for col in latents.columns if col.startswith("z_")]
        latent_features = latents[KEY_COLUMNS + latent_cols].rename(columns={col: f"latent__{col}" for col in latent_cols})
        train_x = train_x.merge(latent_features, on=KEY_COLUMNS, how="left", validate="one_to_one")
        test_x = test_x.merge(latent_features, on=KEY_COLUMNS, how="left", validate="one_to_one")

    base_oof, base_test = load_base_predictions(args, train_raw, sample_raw)
    train_x, test_x = add_engineered_features(train_x, test_x, base_oof, base_test)
    return train_x, test_x, base_oof, base_test


def add_engineered_features(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    base_oof: np.ndarray,
    base_test: np.ndarray,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    all_df = pd.concat(
        [
            train_df.assign(_split="train", _row=np.arange(len(train_df))),
            test_df.assign(_split="test", _row=np.arange(len(test_df))),
        ],
        ignore_index=True,
    )
    lifelog_date = pd.to_datetime(all_df["lifelog_date"])
    sleep_date = pd.to_datetime(all_df["sleep_date"])
    all_df["weekday"] = lifelog_date.dt.weekday.astype(float)
    all_df["is_weekend"] = lifelog_date.dt.weekday.isin([5, 6]).astype(float)
    all_df["weekday_sin"] = np.sin(2.0 * np.pi * all_df["weekday"] / 7.0)
    all_df["weekday_cos"] = np.cos(2.0 * np.pi * all_df["weekday"] / 7.0)
    all_df["sleep_weekday"] = sleep_date.dt.weekday.astype(float)
    all_df["sleep_weekday_sin"] = np.sin(2.0 * np.pi * all_df["sleep_weekday"] / 7.0)
    all_df["sleep_weekday_cos"] = np.cos(2.0 * np.pi * all_df["sleep_weekday"] / 7.0)
    all_df["date_ord"] = lifelog_date.map(pd.Timestamp.toordinal).astype(float)

    pred_all = np.vstack([base_oof, base_test])
    for target_i, target in enumerate(TARGET_COLUMNS):
        pred = np.clip(pred_all[:, target_i], EPS, 1.0 - EPS)
        all_df[f"base_pred_{target}"] = pred
        all_df[f"base_logit_{target}"] = safe_logit(pred)

    numeric_source = [
        col
        for col in all_df.columns
        if col not in KEY_COLUMNS + TARGET_COLUMNS + ["date", "sleep_onset", "wake_time", "_split", "_row"]
        and pd.api.types.is_numeric_dtype(all_df[col])
    ]
    numeric_source = sorted(dict.fromkeys(numeric_source))
    grouped = all_df.groupby("subject_id", sort=False)

    blocks: list[pd.DataFrame] = []
    missing_cols = {}
    log_cols = {}
    centered_cols = {}
    rank_cols = {}
    for col in numeric_source:
        values = pd.to_numeric(all_df[col], errors="coerce")
        miss_rate = float(values.isna().mean())
        if 0.0 < miss_rate < 1.0:
            missing_cols[f"miss__{col}"] = values.isna().astype(float)
        finite = values[np.isfinite(values)]
        if len(finite) and finite.min() >= 0 and finite.quantile(0.95) > 10:
            log_cols[f"log1p__{col}"] = np.log1p(values)
        if not col.startswith("base_") and col not in {
            "weekday",
            "is_weekend",
            "weekday_sin",
            "weekday_cos",
            "sleep_weekday",
            "sleep_weekday_sin",
            "sleep_weekday_cos",
            "date_ord",
            "panel_index",
            "panel_position",
        }:
            centered_cols[f"sub_center__{col}"] = values - grouped[col].transform("mean")
            rank_cols[f"sub_rank__{col}"] = grouped[col].rank(method="average", pct=True)
    for block in [missing_cols, log_cols, centered_cols, rank_cols]:
        if block:
            blocks.append(pd.DataFrame(block, index=all_df.index))

    trajectory_source = []
    for col in numeric_source:
        if col.startswith("base_logit_") or col in CORE_COLUMNS or col.startswith("latent__z_"):
            trajectory_source.append(col)
    trajectory_source = sorted(dict.fromkeys(trajectory_source))
    if trajectory_source:
        ordered = all_df.sort_values(["subject_id", "lifelog_date", "sleep_date"]).copy()
        grouped_ordered = ordered.groupby("subject_id", sort=False)
        trajectory_cols = {}
        for col in trajectory_source:
            values = pd.to_numeric(ordered[col], errors="coerce")
            prev_values = grouped_ordered[col].shift(1)
            next_values = grouped_ordered[col].shift(-1)
            roll3 = (
                grouped_ordered[col]
                .rolling(window=3, min_periods=1)
                .mean()
                .reset_index(level=0, drop=True)
            )
            trajectory_cols[f"traj_prev__{col}"] = prev_values
            trajectory_cols[f"traj_next__{col}"] = next_values
            trajectory_cols[f"traj_delta_prev__{col}"] = values - prev_values
            trajectory_cols[f"traj_delta_next__{col}"] = next_values - values
            trajectory_cols[f"traj_roll3_dev__{col}"] = values - roll3
        trajectory_df = pd.DataFrame(trajectory_cols, index=ordered.index).sort_index()
        blocks.append(trajectory_df)

    interactions = {}
    for name, left, right in [
        ("ix_light_home", "mlight_night_h_bright", "gps_home_ratio"),
        ("ix_light_screen", "mlight_night_h_bright", "day_screen_on_ratio"),
        ("ix_outings_home", "outings", "gps_home_ratio"),
        ("ix_prebed_sns_light", "prebed_sns_sec", "mlight_night_h_bright"),
        ("ix_video_light", "prebed_video_sec", "mlight_night_h_bright"),
        ("ix_hr_home", "night_hr_mean", "gps_home_ratio"),
        ("ix_steps_home", "z_night_step_sum", "gps_home_ratio"),
    ]:
        if left in all_df.columns and right in all_df.columns:
            interactions[name] = pd.to_numeric(all_df[left], errors="coerce") * pd.to_numeric(all_df[right], errors="coerce")
    if interactions:
        blocks.append(pd.DataFrame(interactions, index=all_df.index))

    if blocks:
        all_df = pd.concat([all_df, *blocks], axis=1).copy()

    train_out = all_df[all_df["_split"].eq("train")].sort_values("_row").drop(columns=["_split", "_row"]).reset_index(drop=True)
    test_out = all_df[all_df["_split"].eq("test")].sort_values("_row").drop(columns=["_split", "_row"]).reset_index(drop=True)
    return train_out, test_out


def feature_sets(frame: pd.DataFrame) -> dict[str, tuple[list[str], list[str]]]:
    blocked = set(KEY_COLUMNS + TARGET_COLUMNS + ["date", "sleep_onset", "wake_time"])
    numeric_cols = [
        col
        for col in frame.columns
        if col not in blocked and pd.api.types.is_numeric_dtype(frame[col])
    ]
    base_cols = [col for col in numeric_cols if col.startswith("base_")]
    time_cols = [
        "weekday",
        "is_weekend",
        "weekday_sin",
        "weekday_cos",
        "sleep_weekday",
        "sleep_weekday_sin",
        "sleep_weekday_cos",
        "date_ord",
        "panel_index",
        "panel_position",
    ]
    time_cols = [col for col in time_cols if col in frame.columns]
    latent_cols = [col for col in numeric_cols if col.startswith("latent__")]
    trajectory_cols = [col for col in numeric_cols if col.startswith("traj_")]
    rankdev_cols = [col for col in numeric_cols if col.startswith(("sub_center__", "sub_rank__", "miss__", "log1p__"))]
    core_cols = []
    for col in CORE_COLUMNS:
        core_cols.extend([col, f"miss__{col}", f"log1p__{col}", f"sub_center__{col}", f"sub_rank__{col}"])
    core_cols = [col for col in dict.fromkeys(core_cols) if col in frame.columns]
    interaction_cols = [col for col in numeric_cols if col.startswith("ix_")]
    sets = {
        "base_pos": (sorted(dict.fromkeys(base_cols + time_cols)), ["subject_id"]),
        "core": (sorted(dict.fromkeys(base_cols + core_cols + interaction_cols + time_cols)), ["subject_id"]),
        "temporal_core": (sorted(dict.fromkeys(base_cols + core_cols + trajectory_cols + interaction_cols + time_cols)), ["subject_id"]),
        "rankdev": (sorted(dict.fromkeys(base_cols + rankdev_cols + interaction_cols + time_cols)), ["subject_id"]),
        "temporal_rankdev": (sorted(dict.fromkeys(base_cols + rankdev_cols + trajectory_cols + interaction_cols + time_cols)), ["subject_id"]),
        "nosubject_rankdev": (sorted(dict.fromkeys(base_cols + rankdev_cols + interaction_cols + time_cols)), []),
    }
    if latent_cols:
        sets["latent_core"] = (sorted(dict.fromkeys(base_cols + latent_cols + core_cols + interaction_cols + time_cols)), ["subject_id"])
        sets["latent_temporal_core"] = (
            sorted(dict.fromkeys(base_cols + latent_cols + core_cols + trajectory_cols + interaction_cols + time_cols)),
            ["subject_id"],
        )
        sets["latent_rankdev"] = (sorted(dict.fromkeys(base_cols + latent_cols + rankdev_cols + interaction_cols + time_cols)), ["subject_id"])
        sets["latent_temporal_rankdev"] = (
            sorted(dict.fromkeys(base_cols + latent_cols + rankdev_cols + trajectory_cols + interaction_cols + time_cols)),
            ["subject_id"],
        )
    return sets


def make_ohe() -> OneHotEncoder:
    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        return OneHotEncoder(handle_unknown="ignore", sparse=False)


def make_model(spec: ModelSpec, numeric_cols: list[str], categorical_cols: list[str]) -> Pipeline:
    steps = [
        ("num", make_pipeline(SimpleImputer(strategy="median", keep_empty_features=True), StandardScaler()), numeric_cols),
    ]
    if categorical_cols:
        steps.append(("cat", make_ohe(), categorical_cols))
    preprocessor = ColumnTransformer(steps, remainder="drop")
    if spec.kind == "logreg":
        model = LogisticRegression(C=spec.value, solver="lbfgs", max_iter=5000, random_state=2026)
    elif spec.kind == "hgb":
        model = HistGradientBoostingClassifier(
            max_iter=90,
            learning_rate=0.025,
            max_leaf_nodes=7,
            min_samples_leaf=12,
            l2_regularization=spec.value,
            random_state=2026,
        )
    else:
        raise ValueError(f"Unknown model kind: {spec.kind}")
    return make_pipeline(preprocessor, model)


def fit_predict(
    model: Pipeline,
    train_x: pd.DataFrame,
    y: np.ndarray,
    eval_x: pd.DataFrame,
    sample_weight: np.ndarray,
) -> np.ndarray:
    classes = np.unique(y)
    if len(classes) < 2:
        return np.full(len(eval_x), float(classes[0]), dtype=float)
    model.fit(train_x, y, **{f"{model.steps[-1][0]}__sample_weight": sample_weight})
    return model.predict_proba(eval_x)[:, 1]


def train_model_oof_test(
    train_x: pd.DataFrame,
    test_x: pd.DataFrame,
    folds: list[tuple[np.ndarray, np.ndarray]],
    spec: ModelSpec,
    sets: dict[str, tuple[list[str], list[str]]],
    sample: pd.DataFrame,
    bins: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    numeric_cols, categorical_cols = sets[spec.feature_set]
    oof = np.zeros((len(train_x), len(TARGET_COLUMNS)), dtype=float)
    test = np.zeros((len(test_x), len(TARGET_COLUMNS)), dtype=float)
    y = train_x[TARGET_COLUMNS].astype(int).reset_index(drop=True)
    full_weights = build_fit_weights(train_x, sample, bins, spec.weight_mode)
    for target_i, target in enumerate(TARGET_COLUMNS):
        for train_idx, val_idx in folds:
            model = make_model(spec, numeric_cols, categorical_cols)
            oof[val_idx, target_i] = fit_predict(
                model,
                train_x.iloc[train_idx],
                y.loc[train_idx, target].to_numpy(),
                train_x.iloc[val_idx],
                full_weights[train_idx],
            )
        full_model = make_model(spec, numeric_cols, categorical_cols)
        test[:, target_i] = fit_predict(full_model, train_x, y[target].to_numpy(), test_x, full_weights)
    return np.clip(oof, EPS, 1.0 - EPS), np.clip(test, EPS, 1.0 - EPS)


def row_losses(y_arr: np.ndarray, pred: np.ndarray) -> np.ndarray:
    pred = np.clip(pred, EPS, 1.0 - EPS)
    return -(y_arr * np.log(pred) + (1.0 - y_arr) * np.log1p(-pred)).mean(axis=1)


def average_loss(y: pd.DataFrame, pred: np.ndarray) -> tuple[float, dict[str, float]]:
    per_target = {
        target: float(log_loss(y[target].to_numpy(), np.clip(pred[:, target_i], EPS, 1.0 - EPS), labels=[0, 1]))
        for target_i, target in enumerate(TARGET_COLUMNS)
    }
    return float(np.mean(list(per_target.values()))), per_target


def weighted_bootstrap(diff: np.ndarray, weights: np.ndarray, seed: int, n_bootstrap: int) -> dict[str, float]:
    weights = np.clip(weights.astype(float), 0.0, None)
    if weights.sum() <= 0:
        weights = np.ones_like(weights)
    prob = weights / weights.sum()
    rng = np.random.default_rng(seed)
    values = np.empty(n_bootstrap, dtype=float)
    for i in range(n_bootstrap):
        idx = rng.choice(len(diff), size=len(diff), replace=True, p=prob)
        values[i] = float(diff[idx].mean())
    return {
        "p025": float(np.quantile(values, 0.025)),
        "p500": float(np.quantile(values, 0.500)),
        "p975": float(np.quantile(values, 0.975)),
    }


def score_candidate_windows(
    train_x: pd.DataFrame,
    sample_x: pd.DataFrame,
    base_oof: np.ndarray,
    source_oof: np.ndarray,
    windows: list[Window],
    weights_to_try: list[float],
    sample_weights: np.ndarray,
    support: np.ndarray,
    mode: str,
    seed: int,
    bootstrap: int,
    source_name: str,
) -> list[dict[str, float | int | str]]:
    y_arr = train_x[TARGET_COLUMNS].to_numpy(dtype=float)
    base_loss = row_losses(y_arr, base_oof)
    rows: list[dict[str, float | int | str]] = []
    positions = train_x["panel_position"].to_numpy(dtype=float)
    for window in windows:
        in_window = (positions >= window.lo) & (positions < window.hi)
        mask = support & in_window
        if not bool(mask.any()):
            continue
        for target_i, target in enumerate(TARGET_COLUMNS):
            for blend_weight in weights_to_try:
                final = base_oof.copy()
                blended = blend_values(base_oof[:, target_i], source_oof[:, target_i], blend_weight, mode)
                final[mask, target_i] = blended[mask]
                cand_loss = row_losses(y_arr, final)
                diff = base_loss - cand_loss
                boot = weighted_bootstrap(diff, sample_weights, seed, bootstrap)
                target_base = log_loss(y_arr[:, target_i], base_oof[:, target_i], labels=[0, 1])
                target_cand = log_loss(y_arr[:, target_i], final[:, target_i], labels=[0, 1])
                weighted_target_base = log_loss(y_arr[:, target_i], base_oof[:, target_i], labels=[0, 1], sample_weight=sample_weights)
                weighted_target_cand = log_loss(y_arr[:, target_i], final[:, target_i], labels=[0, 1], sample_weight=sample_weights)
                row: dict[str, float | int | str] = {
                    "source": source_name,
                    "target": target,
                    "window": window.name,
                    "blend_weight": float(blend_weight),
                    "applied_rows": int(mask.sum()),
                    "uniform_improvement": float(diff.mean()),
                    "weighted_improvement": float(np.average(diff, weights=sample_weights)),
                    "weighted_p025": boot["p025"],
                    "weighted_p500": boot["p500"],
                    "weighted_p975": boot["p975"],
                    "target_delta": float(target_base - target_cand),
                    "weighted_target_delta": float(weighted_target_base - weighted_target_cand),
                }
                for block_name, lo, hi in [("mid", 1 / 3, 2 / 3), ("late", 2 / 3, 1.01), ("tail20", 0.8, 1.01)]:
                    idx = np.flatnonzero((positions >= lo) & (positions < hi))
                    row[f"{block_name}_delta"] = float(diff[idx].mean()) if len(idx) else 0.0
                rows.append(row)
    return rows


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    if df.empty:
        return "_empty_"
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


def write_candidate_files(
    output_dir: Path,
    train_x: pd.DataFrame,
    sample_path: str,
    spec_name: str,
    oof_pred: np.ndarray,
    test_pred: np.ndarray,
) -> tuple[Path, Path]:
    safe_name = spec_name.replace("/", "_")
    oof_df = train_x[KEY_COLUMNS + TARGET_COLUMNS].copy()
    for target_i, target in enumerate(TARGET_COLUMNS):
        oof_df[f"pred_{target}"] = oof_pred[:, target_i]
    oof_path = output_dir / "sources" / f"oof_{safe_name}.csv"
    oof_path.parent.mkdir(parents=True, exist_ok=True)
    oof_df.to_csv(oof_path, index=False)

    submission = normalize_keys(pd.read_csv(sample_path))
    for target_i, target in enumerate(TARGET_COLUMNS):
        submission[target] = test_pred[:, target_i]
    sub_path = output_dir / "sources" / f"submission_{safe_name}.csv"
    submission.to_csv(sub_path, index=False)
    return oof_path, sub_path


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    train_x, test_x, base_oof, _base_test = load_joined(args)
    folds = make_subject_time_folds(train_x, args.folds)
    sets = feature_sets(train_x)
    selected_sets = [name for name in parse_str_list(args.feature_sets) if name in sets]
    bins = position_bins(args.position_bins)
    sample_with_pos = normalize_keys(pd.read_csv(args.sample_path))
    _, sample_with_pos = add_panel_position(train_x[KEY_COLUMNS], sample_with_pos)
    support = sample_support_mask(train_x, sample_with_pos, bins)
    sample_weights = sample_position_weights(train_x, sample_with_pos, bins)
    windows = parse_windows(args.windows)
    weights_to_try = parse_float_list(args.blend_weights)

    specs: list[ModelSpec] = []
    for feature_set in selected_sets:
        for weight_mode in parse_str_list(args.weight_modes):
            for c_value in parse_float_list(args.logreg_cs):
                specs.append(ModelSpec(f"logreg_{feature_set}_{weight_mode}_C{c_value:g}", "logreg", feature_set, c_value, weight_mode))
            for l2_value in parse_float_list(args.hgb_l2s):
                specs.append(ModelSpec(f"hgb_{feature_set}_{weight_mode}_l2{l2_value:g}", "hgb", feature_set, l2_value, weight_mode))

    y = train_x[TARGET_COLUMNS]
    base_avg, base_targets = average_loss(y, base_oof)
    all_scores = []
    candidate_rows = []
    source_paths = []
    for spec_i, spec in enumerate(specs, start=1):
        numeric_count = len(sets[spec.feature_set][0])
        print(f"[{spec_i}/{len(specs)}] {spec.name} ({numeric_count} numeric)")
        model_oof, model_test = train_model_oof_test(train_x, test_x, folds, spec, sets, sample_with_pos, bins)
        model_avg, model_targets = average_loss(y, model_oof)
        oof_path, sub_path = write_candidate_files(output_dir, train_x, args.sample_path, spec.name, model_oof, model_test)
        source_paths.append({"source": spec.name, "oof_path": str(oof_path), "submission_path": str(sub_path)})
        candidate_rows.append(
            {
                "source": spec.name,
                "kind": spec.kind,
                "feature_set": spec.feature_set,
                "value": spec.value,
                "weight_mode": spec.weight_mode,
                "raw_avg_log_loss": model_avg,
                "raw_delta_vs_base": base_avg - model_avg,
                **{f"raw_{target}": model_targets[target] for target in TARGET_COLUMNS},
                **{f"base_{target}": base_targets[target] for target in TARGET_COLUMNS},
            }
        )
        all_scores.extend(
            score_candidate_windows(
                train_x=train_x,
                sample_x=test_x,
                base_oof=base_oof,
                source_oof=model_oof,
                windows=windows,
                weights_to_try=weights_to_try,
                sample_weights=sample_weights,
                support=support,
                mode=args.mode,
                seed=args.seed,
                bootstrap=args.bootstrap,
                source_name=spec.name,
            )
        )

    candidates = pd.DataFrame(candidate_rows).sort_values("raw_avg_log_loss").reset_index(drop=True)
    scores = pd.DataFrame(all_scores).sort_values(["weighted_p025", "weighted_improvement"], ascending=[False, False]).reset_index(drop=True)
    candidates.to_csv(output_dir / "position_weighted_decoder_candidates.csv", index=False)
    scores.to_csv(output_dir / "position_weighted_window_scores.csv", index=False)
    pd.DataFrame(source_paths).to_csv(output_dir / "source_paths.csv", index=False)

    report = {
        "base_avg_log_loss": base_avg,
        "base_targets": base_targets,
        "feature_set_sizes": {name: len(cols) for name, (cols, _) in sets.items()},
        "source_paths": source_paths,
        "top_raw_candidates": candidates.head(20).to_dict(orient="records"),
        "top_window_scores": scores.head(40).to_dict(orient="records"),
        "args": vars(args),
    }
    (output_dir / "position_weighted_tail_decoder_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    lines = [
        "# Position-weighted Tail Decoder Report",
        "",
        f"- Base avg logloss: `{base_avg:.6f}`",
        f"- Candidates trained: `{len(candidates)}`",
        f"- Sample-supported train rows: `{int(support.sum())}` / `{len(support)}`",
        "",
        "## Top Raw Candidates",
        "",
        dataframe_to_markdown(candidates.head(12)),
        "",
        "## Top Window Scores",
        "",
        dataframe_to_markdown(scores.head(20)),
        "",
    ]
    (output_dir / "position_weighted_tail_decoder_report.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"base={base_avg:.6f} candidates={len(candidates)}")
    print(scores.head(args.print_top).to_string(index=False))
    print(f"saved: {output_dir / 'position_weighted_window_scores.csv'}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train sample-position weighted raw/latent decoders and score supported windows.")
    parser.add_argument("--master-path", default="artifacts/10_master_daily.parquet")
    parser.add_argument("--latent-path", default="outputs/diffusion_encoder_id_long/day_latents.parquet")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--base-oof", required=True)
    parser.add_argument("--base-submission", required=True)
    parser.add_argument("--output-dir", default="outputs/position_weighted_tail_decoder")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--feature-sets", default="core,latent_core,nosubject_rankdev")
    parser.add_argument("--weight-modes", default="sample,tail3,midtail")
    parser.add_argument("--logreg-cs", default="0.003,0.01,0.03")
    parser.add_argument("--hgb-l2s", default="")
    parser.add_argument("--blend-weights", default="1.0,0.8,0.65,0.5,0.3")
    parser.add_argument("--mode", default="logit", choices=["prob", "logit"])
    parser.add_argument("--windows", default="mid:0.3333333333:0.6666666667,tail:0.8:1.000001,mid_tail:0.3333333333:1.000001")
    parser.add_argument("--position-bins", default="0,0.3333333333,0.6666666667,0.8,1.0")
    parser.add_argument("--bootstrap", type=int, default=500)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--print-top", type=int, default=30)
    return parser.parse_args()


if __name__ == "__main__":
    main()
