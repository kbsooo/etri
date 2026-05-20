from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.preprocessing import StandardScaler


KEY_COLUMNS = ["subject_id", "sleep_date", "lifelog_date"]
Q_TARGETS = ["Q1", "Q2", "Q3"]
S_TARGETS = ["S1", "S2", "S3", "S4"]
TARGET_COLUMNS = Q_TARGETS + S_TARGETS
EPS = 1e-5


Q_CORE_COLUMNS = [
    "mlight_night_h_bright",
    "mlight_night_max",
    "mlight_mean",
    "mlight_max",
    "mlight_h_bright",
    "wlight_h_bright",
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
    "prebed_sns_sec",
    "prebed_video_sec",
    "prebed_messenger_sec",
    "prebed_os_launcher_sec",
    "app_sns_sec",
    "app_video_sec",
    "app_messenger_sec",
    "amb_night_silence",
    "amb_vehicle",
    "amb_music",
    "amb_speech",
    "longest_block_min",
    "tst_min",
    "sleep_eff",
    "sol_proxy_min",
    "n_awakenings",
    "night_hr_mean",
    "night_rmssd",
    "night_sdnn",
    "hr_mean",
    "rmssd_mean",
    "sdnn_mean",
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
class RankerSpec:
    name: str
    feature_set: str
    c_value: float


def normalize_key_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in KEY_COLUMNS:
        out[col] = out[col].astype(str)
    return out


def assert_unique_keys(df: pd.DataFrame, name: str) -> None:
    duplicates = int(df.duplicated(KEY_COLUMNS).sum())
    if duplicates:
        raise ValueError(f"{name} has duplicated key rows: {duplicates}")


def parse_float_list(value: str) -> list[float]:
    return [float(part) for part in value.split(",") if part.strip()]


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(values, -40.0, 40.0)))


def safe_logit(values: np.ndarray) -> np.ndarray:
    values = np.clip(values, EPS, 1.0 - EPS)
    return np.log(values / (1.0 - values))


def solve_intercept(scores: np.ndarray, target_mean: float) -> float:
    target_mean = float(np.clip(target_mean, EPS, 1.0 - EPS))
    if len(scores) == 0:
        return float(safe_logit(np.array([target_mean]))[0])
    lo, hi = -25.0, 25.0
    for _ in range(80):
        mid = (lo + hi) / 2.0
        mean = float(sigmoid(scores + mid).mean())
        if mean < target_mean:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def average_log_loss(y_true: pd.DataFrame, pred: np.ndarray, targets: list[str]) -> tuple[float, dict[str, float]]:
    clipped = np.clip(pred, EPS, 1.0 - EPS)
    per_target = {
        target: float(log_loss(y_true[target].to_numpy(), clipped[:, i], labels=[0, 1]))
        for i, target in enumerate(targets)
    }
    return float(np.mean(list(per_target.values()))), per_target


def load_joined_frames(args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame]:
    train = normalize_key_columns(pd.read_csv(args.train_path))
    sample = normalize_key_columns(pd.read_csv(args.sample_path))
    master = normalize_key_columns(pd.read_parquet(args.master_path))
    for name, df in [("train", train), ("sample", sample), ("master", master)]:
        missing = sorted(set(KEY_COLUMNS) - set(df.columns))
        if missing:
            raise ValueError(f"{name} is missing key columns: {missing}")
        assert_unique_keys(df, name)

    master_feature_cols = [col for col in master.columns if col not in TARGET_COLUMNS + ["role"]]
    train_joined = train.merge(master[master_feature_cols], on=KEY_COLUMNS, how="left", validate="one_to_one")
    test_joined = sample[KEY_COLUMNS].merge(master[master_feature_cols], on=KEY_COLUMNS, how="left", validate="one_to_one")
    if train_joined["date"].isna().any() or test_joined["date"].isna().any():
        raise ValueError("Some rows failed to join with master features")

    latent_path = Path(args.latent_path)
    if latent_path.exists():
        latents = normalize_key_columns(pd.read_parquet(latent_path))
        assert_unique_keys(latents, "latents")
        latent_cols = [col for col in latents.columns if col.startswith("z_")]
        latent_features = latents[KEY_COLUMNS + latent_cols].rename(columns={col: f"latent__{col}" for col in latent_cols})
        train_joined = train_joined.merge(latent_features, on=KEY_COLUMNS, how="left", validate="one_to_one")
        test_joined = test_joined.merge(latent_features, on=KEY_COLUMNS, how="left", validate="one_to_one")
    return train_joined, test_joined


def add_date_features(all_df: pd.DataFrame) -> pd.DataFrame:
    out = all_df.copy()
    lifelog_dt = pd.to_datetime(out["lifelog_date"])
    sleep_dt = pd.to_datetime(out["sleep_date"])
    out["weekday"] = lifelog_dt.dt.weekday.astype(float)
    out["is_weekend"] = lifelog_dt.dt.weekday.isin([5, 6]).astype(float)
    out["weekday_sin"] = np.sin(2.0 * np.pi * out["weekday"] / 7.0)
    out["weekday_cos"] = np.cos(2.0 * np.pi * out["weekday"] / 7.0)
    out["sleep_weekday"] = sleep_dt.dt.weekday.astype(float)
    out["sleep_weekday_sin"] = np.sin(2.0 * np.pi * out["sleep_weekday"] / 7.0)
    out["sleep_weekday_cos"] = np.cos(2.0 * np.pi * out["sleep_weekday"] / 7.0)
    ordered = out.sort_values(["subject_id", "lifelog_date", "sleep_date"]).copy()
    ordered["day_index_subject"] = ordered.groupby("subject_id").cumcount().astype(float)
    max_idx = ordered.groupby("subject_id")["day_index_subject"].transform("max").replace(0.0, 1.0)
    ordered["day_position_subject"] = ordered["day_index_subject"] / max_idx
    return ordered.sort_index()


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

    base_numeric = [
        col
        for col in all_df.columns
        if col not in KEY_COLUMNS + TARGET_COLUMNS + ["date", "_split", "_row"]
        and pd.api.types.is_numeric_dtype(all_df[col])
    ]
    base_numeric = sorted(dict.fromkeys(base_numeric))

    new_blocks: list[pd.DataFrame] = []
    missing_cols = []
    for col in base_numeric:
        miss_rate = float(all_df[col].isna().mean())
        if 0.0 < miss_rate < 1.0:
            missing_cols.append(f"miss__{col}")
            new_blocks.append(pd.DataFrame({f"miss__{col}": all_df[col].isna().astype(float)}))

    log_cols = []
    for col in base_numeric:
        values = pd.to_numeric(all_df[col], errors="coerce")
        finite = values[np.isfinite(values)]
        if len(finite) and finite.min() >= 0 and finite.quantile(0.95) > 10:
            log_cols.append(f"log1p__{col}")
            new_blocks.append(pd.DataFrame({f"log1p__{col}": np.log1p(values)}))

    grouped = all_df.groupby("subject_id", sort=False)
    transductive_source = [
        col
        for col in base_numeric
        if not col.startswith("latent__")
        and col not in {"weekday", "sleep_weekday", "day_index_subject", "day_position_subject"}
    ]
    centered_cols = []
    rank_cols = []
    for col in transductive_source:
        values = pd.to_numeric(all_df[col], errors="coerce")
        centered = f"sub_center__{col}"
        ranked = f"sub_rank__{col}"
        centered_cols.append(centered)
        rank_cols.append(ranked)
        new_blocks.append(
            pd.DataFrame(
                {
                    centered: values - grouped[col].transform("mean"),
                    ranked: grouped[col].rank(method="average", pct=True),
                }
            )
        )

    interactions = {}
    for name, left, right in [
        ("ix_q_light_home", "mlight_night_h_bright", "gps_home_ratio"),
        ("ix_q_light_screen", "mlight_night_h_bright", "day_screen_on_ratio"),
        ("ix_q_outings_home", "outings", "gps_home_ratio"),
        ("ix_q_prebed_sns_light", "prebed_sns_sec", "mlight_night_h_bright"),
        ("ix_q_video_light", "prebed_video_sec", "mlight_night_h_bright"),
        ("ix_q_coherence_outings", "agree_rate", "outings"),
        ("ix_q_hr_home", "night_hr_mean", "gps_home_ratio"),
    ]:
        if left in all_df.columns and right in all_df.columns:
            interactions[name] = pd.to_numeric(all_df[left], errors="coerce") * pd.to_numeric(all_df[right], errors="coerce")
    interaction_cols = sorted(interactions)
    if interactions:
        new_blocks.append(pd.DataFrame(interactions))

    if new_blocks:
        all_df = pd.concat([all_df, *new_blocks], axis=1).copy()

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
    q_core_existing = [col for col in Q_CORE_COLUMNS if col in all_df.columns]
    q_core_aug = []
    for col in q_core_existing:
        q_core_aug.extend([col, f"sub_center__{col}", f"sub_rank__{col}", f"miss__{col}", f"log1p__{col}"])
    q_core_aug = [col for col in dict.fromkeys(q_core_aug) if col in all_df.columns]

    rankdev_cols = sorted(dict.fromkeys(q_core_aug + interaction_cols + time_cols))
    all_rankdev_cols = sorted(dict.fromkeys(base_numeric + missing_cols + log_cols + centered_cols + rank_cols + interaction_cols + time_cols))
    feature_sets = {
        "q_core": rankdev_cols,
        "q_core_latent": sorted(dict.fromkeys(rankdev_cols + latent_cols)),
        "all_rankdev": all_rankdev_cols,
    }
    if latent_cols:
        feature_sets["all_rankdev_latent"] = sorted(dict.fromkeys(all_rankdev_cols + latent_cols))

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


def build_pairwise_training_data(
    x_scaled: np.ndarray,
    train_df: pd.DataFrame,
    train_idx: np.ndarray,
    target: str,
) -> tuple[np.ndarray, np.ndarray]:
    pair_x = []
    pair_y = []
    frame = train_df.iloc[train_idx].copy()
    frame["_pos"] = train_idx
    for _, group in frame.groupby("subject_id", sort=False):
        positives = group.loc[group[target].astype(int) == 1, "_pos"].to_numpy(dtype=int)
        negatives = group.loc[group[target].astype(int) == 0, "_pos"].to_numpy(dtype=int)
        if len(positives) == 0 or len(negatives) == 0:
            continue
        diffs = x_scaled[positives][:, None, :] - x_scaled[negatives][None, :, :]
        diffs = diffs.reshape(-1, x_scaled.shape[1])
        pair_x.append(diffs)
        pair_y.append(np.ones(len(diffs), dtype=int))
        pair_x.append(-diffs)
        pair_y.append(np.zeros(len(diffs), dtype=int))
    if not pair_x:
        return np.zeros((0, x_scaled.shape[1]), dtype=np.float32), np.zeros(0, dtype=int)
    return np.vstack(pair_x).astype(np.float32), np.concatenate(pair_y)


def fit_ranker_scores(
    train_df: pd.DataFrame,
    eval_df: pd.DataFrame,
    feature_cols: list[str],
    train_idx: np.ndarray,
    eval_idx: np.ndarray,
    c_value: float,
    targets: list[str],
) -> np.ndarray:
    x_train_raw = train_df[feature_cols].to_numpy(dtype=np.float64)
    x_eval_raw = eval_df[feature_cols].to_numpy(dtype=np.float64)
    x_train_raw[~np.isfinite(x_train_raw)] = np.nan
    x_eval_raw[~np.isfinite(x_eval_raw)] = np.nan

    imputer = SimpleImputer(strategy="median", keep_empty_features=True)
    scaler = StandardScaler()
    x_train_scaled = scaler.fit_transform(imputer.fit_transform(x_train_raw[train_idx]))
    x_all_scaled = scaler.transform(imputer.transform(x_train_raw))
    x_eval_scaled = scaler.transform(imputer.transform(x_eval_raw))

    scores = np.zeros((len(eval_idx) if eval_df is train_df else len(eval_df), len(targets)), dtype=float)
    for target_i, target in enumerate(targets):
        pair_x, pair_y = build_pairwise_training_data(x_all_scaled, train_df, train_idx, target)
        if len(np.unique(pair_y)) < 2:
            continue
        model = LogisticRegression(C=c_value, solver="liblinear", max_iter=1000, random_state=2026)
        model.fit(pair_x, pair_y)
        coef = model.coef_.reshape(-1)
        if eval_df is train_df:
            scores[:, target_i] = x_all_scaled[eval_idx] @ coef
        else:
            scores[:, target_i] = x_eval_scaled @ coef
    return scores


def oof_ranker_scores(
    train_df: pd.DataFrame,
    feature_cols: list[str],
    folds: list[tuple[np.ndarray, np.ndarray]],
    c_value: float,
) -> np.ndarray:
    raw_scores = np.zeros((len(train_df), len(Q_TARGETS)), dtype=float)
    for train_idx, val_idx in folds:
        raw_scores[val_idx] = fit_ranker_scores(train_df, train_df, feature_cols, train_idx, val_idx, c_value, Q_TARGETS)
    return raw_scores


def test_ranker_scores(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    feature_cols: list[str],
    c_value: float,
) -> np.ndarray:
    train_idx = np.arange(len(train_df))
    return fit_ranker_scores(train_df, test_df, feature_cols, train_idx, np.arange(len(test_df)), c_value, Q_TARGETS)


def compute_subject_rate(
    train_part: pd.DataFrame,
    subject: str,
    target: str,
    alpha: float,
    mode: str,
) -> float:
    subject_rows = train_part[train_part["subject_id"] == subject]
    global_rate = float(train_part[target].mean())
    subject_rate = float(subject_rows[target].mean()) if len(subject_rows) else global_rate
    smoothed = (float(subject_rows[target].sum()) + alpha * global_rate) / (len(subject_rows) + alpha) if len(subject_rows) else global_rate
    if mode == "subject":
        return smoothed
    if mode == "half":
        return 0.5
    if mode == "half_subject_50":
        return 0.5 * 0.5 + 0.5 * smoothed
    if mode == "half_subject_75":
        return 0.25 * 0.5 + 0.75 * smoothed
    if mode == "global":
        return global_rate
    raise ValueError(f"Unknown mean mode: {mode}")


def calibrate_scores_for_eval(
    raw_scores: np.ndarray,
    train_part: pd.DataFrame,
    eval_part: pd.DataFrame,
    alpha: float,
    beta: float,
    mean_mode: str,
) -> np.ndarray:
    pred = np.zeros_like(raw_scores, dtype=float)
    eval_reset = eval_part.reset_index(drop=True)
    for target_i, target in enumerate(Q_TARGETS):
        for subject, group in eval_reset.reset_index().groupby("subject_id", sort=False):
            idx = group["index"].to_numpy(dtype=int)
            local = raw_scores[idx, target_i]
            std = float(np.nanstd(local))
            if np.isfinite(std) and std > 1e-8:
                score = beta * ((local - float(np.nanmean(local))) / std)
            else:
                score = np.zeros(len(idx), dtype=float)
            target_mean = compute_subject_rate(train_part, str(subject), target, alpha, mean_mode)
            intercept = solve_intercept(score, target_mean)
            pred[idx, target_i] = sigmoid(score + intercept)
    return np.clip(pred, EPS, 1.0 - EPS)


def calibrate_oof_scores(
    raw_scores: np.ndarray,
    train_df: pd.DataFrame,
    folds: list[tuple[np.ndarray, np.ndarray]],
    alpha: float,
    beta: float,
    mean_mode: str,
) -> np.ndarray:
    pred = np.zeros_like(raw_scores, dtype=float)
    for train_idx, val_idx in folds:
        pred[val_idx] = calibrate_scores_for_eval(
            raw_scores[val_idx],
            train_df.iloc[train_idx],
            train_df.iloc[val_idx],
            alpha,
            beta,
            mean_mode,
        )
    return np.clip(pred, EPS, 1.0 - EPS)


def calibrate_test_scores(
    raw_scores: np.ndarray,
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    alpha: float,
    beta: float,
    mean_mode: str,
) -> np.ndarray:
    return calibrate_scores_for_eval(raw_scores, train_df, test_df, alpha, beta, mean_mode)


def q_subject_prior(train_part: pd.DataFrame, eval_part: pd.DataFrame, alpha: float, mean_mode: str) -> np.ndarray:
    pred = np.zeros((len(eval_part), len(Q_TARGETS)), dtype=float)
    for row_i, subject in enumerate(eval_part["subject_id"].astype(str)):
        for target_i, target in enumerate(Q_TARGETS):
            pred[row_i, target_i] = compute_subject_rate(train_part, subject, target, alpha, mean_mode)
    return np.clip(pred, EPS, 1.0 - EPS)


def oof_q_subject_prior(train_df: pd.DataFrame, folds: list[tuple[np.ndarray, np.ndarray]], alpha: float, mean_mode: str) -> np.ndarray:
    pred = np.zeros((len(train_df), len(Q_TARGETS)), dtype=float)
    for train_idx, val_idx in folds:
        pred[val_idx] = q_subject_prior(train_df.iloc[train_idx], train_df.iloc[val_idx], alpha, mean_mode)
    return pred


def evaluate_rankers(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    feature_sets: dict[str, list[str]],
    folds: list[tuple[np.ndarray, np.ndarray]],
    args: argparse.Namespace,
) -> tuple[pd.DataFrame, dict[str, np.ndarray], dict[str, np.ndarray]]:
    rows = []
    oof_cache: dict[str, np.ndarray] = {}
    test_cache: dict[str, np.ndarray] = {}
    y_q = train_df[Q_TARGETS]

    alphas = parse_float_list(args.alphas)
    betas = parse_float_list(args.betas)
    mean_modes = [part for part in args.mean_modes.split(",") if part]

    for alpha in alphas:
        for mean_mode in mean_modes:
            name = f"prior_{mean_mode}_a{alpha:g}"
            oof = oof_q_subject_prior(train_df, folds, alpha, mean_mode)
            test = q_subject_prior(train_df, test_df, alpha, mean_mode)
            oof_cache[name] = oof
            test_cache[name] = test
            avg, per_target = average_log_loss(y_q, oof, Q_TARGETS)
            rows.append({"name": name, "kind": "prior", "feature_set": "", "c_value": math.nan, "alpha": alpha, "beta": math.nan, "mean_mode": mean_mode, "blend_weight": math.nan, "q_avg_log_loss": avg, **per_target})

    feature_set_names = [name for name in args.feature_sets.split(",") if name in feature_sets]
    c_values = parse_float_list(args.c_values)
    spec_total = len(feature_set_names) * len(c_values)
    spec_i = 0
    for feature_set in feature_set_names:
        for c_value in c_values:
            spec_i += 1
            raw_name = f"rankraw_{feature_set}_C{c_value:g}"
            print(f"[{spec_i}/{spec_total}] fitting {raw_name} ({len(feature_sets[feature_set])} features)")
            raw_oof = oof_ranker_scores(train_df, feature_sets[feature_set], folds, c_value)
            raw_test = test_ranker_scores(train_df, test_df, feature_sets[feature_set], c_value)
            for alpha in alphas:
                for beta in betas:
                    for mean_mode in mean_modes:
                        name = f"rankcal_{feature_set}_C{c_value:g}_b{beta:g}_{mean_mode}_a{alpha:g}"
                        oof = calibrate_oof_scores(raw_oof, train_df, folds, alpha, beta, mean_mode)
                        test = calibrate_test_scores(raw_test, train_df, test_df, alpha, beta, mean_mode)
                        oof_cache[name] = oof
                        test_cache[name] = test
                        avg, per_target = average_log_loss(y_q, oof, Q_TARGETS)
                        rows.append(
                            {
                                "name": name,
                                "kind": "rankcal",
                                "feature_set": feature_set,
                                "c_value": c_value,
                                "alpha": alpha,
                                "beta": beta,
                                "mean_mode": mean_mode,
                                "blend_weight": math.nan,
                                "q_avg_log_loss": avg,
                                **per_target,
                            }
                        )

    baseline_oof_path = Path(args.baseline_oof_path)
    baseline_sub_path = Path(args.baseline_submission_path)
    if baseline_oof_path.exists() and baseline_sub_path.exists():
        baseline_oof_df = normalize_key_columns(pd.read_csv(baseline_oof_path))
        baseline_sub_df = normalize_key_columns(pd.read_csv(baseline_sub_path))
        baseline_oof = np.column_stack([baseline_oof_df[f"pred_{target}"].to_numpy(dtype=float) for target in Q_TARGETS])
        baseline_test = baseline_sub_df[Q_TARGETS].to_numpy(dtype=float)
        oof_cache["baseline_q"] = np.clip(baseline_oof, EPS, 1.0 - EPS)
        test_cache["baseline_q"] = np.clip(baseline_test, EPS, 1.0 - EPS)
        avg, per_target = average_log_loss(y_q, oof_cache["baseline_q"], Q_TARGETS)
        rows.append({"name": "baseline_q", "kind": "baseline", "feature_set": "", "c_value": math.nan, "alpha": math.nan, "beta": math.nan, "mean_mode": "", "blend_weight": 1.0, "q_avg_log_loss": avg, **per_target})

        blend_sources = [name for name in list(oof_cache) if name.startswith("rankcal_")]
        for source in blend_sources:
            for weight in parse_float_list(args.baseline_blend_weights):
                name = f"blend_baseline_w{weight:g}_{source}"
                oof = np.clip(weight * oof_cache["baseline_q"] + (1.0 - weight) * oof_cache[source], EPS, 1.0 - EPS)
                test = np.clip(weight * test_cache["baseline_q"] + (1.0 - weight) * test_cache[source], EPS, 1.0 - EPS)
                oof_cache[name] = oof
                test_cache[name] = test
                avg, per_target = average_log_loss(y_q, oof, Q_TARGETS)
                rows.append(
                    {
                        "name": name,
                        "kind": "blend",
                        "feature_set": "",
                        "c_value": math.nan,
                        "alpha": math.nan,
                        "beta": math.nan,
                        "mean_mode": "",
                        "blend_weight": weight,
                        "q_avg_log_loss": avg,
                        **per_target,
                    }
                )

    scores = pd.DataFrame(rows).sort_values("q_avg_log_loss", ascending=True).reset_index(drop=True)
    return scores, oof_cache, test_cache


def build_targetwise_q(
    scores: pd.DataFrame,
    oof_cache: dict[str, np.ndarray],
    test_cache: dict[str, np.ndarray],
    train_df: pd.DataFrame,
) -> tuple[pd.DataFrame, np.ndarray, np.ndarray, dict[str, float]]:
    selected_rows = []
    oof = np.zeros((len(train_df), len(Q_TARGETS)), dtype=float)
    test = None
    for target_i, target in enumerate(Q_TARGETS):
        row = scores.sort_values(target).iloc[0].to_dict()
        selected_rows.append({"target": target, **row})
        oof[:, target_i] = oof_cache[str(row["name"])][:, target_i]
        if test is None:
            test = np.zeros_like(test_cache[str(row["name"])])
        test[:, target_i] = test_cache[str(row["name"])][:, target_i]
    assert test is not None
    avg, per_target = average_log_loss(train_df[Q_TARGETS], oof, Q_TARGETS)
    selected = pd.DataFrame(selected_rows)
    selected["targetwise_q_avg_log_loss"] = avg
    return selected, np.clip(oof, EPS, 1.0 - EPS), np.clip(test, EPS, 1.0 - EPS), {"q_avg_log_loss": avg, **per_target}


def build_full_outputs(
    args: argparse.Namespace,
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    q_oof: np.ndarray,
    q_test: np.ndarray,
    output_dir: Path,
) -> dict[str, float]:
    baseline_oof = normalize_key_columns(pd.read_csv(args.baseline_oof_path))
    baseline_sub = normalize_key_columns(pd.read_csv(args.baseline_submission_path))
    full_oof = train_df[KEY_COLUMNS + TARGET_COLUMNS].copy()
    full_pred = np.zeros((len(train_df), len(TARGET_COLUMNS)), dtype=float)
    full_pred[:, : len(Q_TARGETS)] = q_oof
    for s_i, target in enumerate(S_TARGETS, start=len(Q_TARGETS)):
        full_pred[:, s_i] = baseline_oof[f"pred_{target}"].to_numpy(dtype=float)
    for target_i, target in enumerate(TARGET_COLUMNS):
        full_oof[f"pred_{target}"] = np.clip(full_pred[:, target_i], EPS, 1.0 - EPS)
    full_oof.to_csv(output_dir / "oof_q_ranker_with_baseline_s.csv", index=False)

    sample = pd.read_csv(args.sample_path)
    submission = sample.copy()
    for target_i, target in enumerate(Q_TARGETS):
        submission[target] = q_test[:, target_i]
    for target in S_TARGETS:
        submission[target] = baseline_sub[target].to_numpy(dtype=float)
    submission.to_csv(output_dir / "submission_q_ranker_with_baseline_s.csv", index=False)

    full_avg, full_per_target = average_log_loss(train_df[TARGET_COLUMNS], full_pred, TARGET_COLUMNS)
    return {"avg_log_loss": full_avg, **full_per_target}


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


def write_outputs(
    output_dir: Path,
    args: argparse.Namespace,
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    feature_sets: dict[str, list[str]],
    scores: pd.DataFrame,
    selected: pd.DataFrame,
    q_score: dict[str, float],
    full_score: dict[str, float],
    q_oof: np.ndarray,
    q_test: np.ndarray,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    scores.to_csv(output_dir / "candidate_scores.csv", index=False)
    selected.to_csv(output_dir / "targetwise_q_selection.csv", index=False)
    pd.DataFrame([q_score]).to_csv(output_dir / "targetwise_q_score.csv", index=False)
    pd.DataFrame([full_score]).to_csv(output_dir / "full_score_with_baseline_s.csv", index=False)

    q_oof_df = train_df[KEY_COLUMNS + Q_TARGETS].copy()
    for target_i, target in enumerate(Q_TARGETS):
        q_oof_df[f"pred_{target}"] = q_oof[:, target_i]
    q_oof_df.to_csv(output_dir / "oof_q_ranker_targetwise.csv", index=False)

    q_sub = pd.read_csv(args.sample_path)
    for target_i, target in enumerate(Q_TARGETS):
        q_sub[target] = q_test[:, target_i]
    q_sub.to_csv(output_dir / "submission_q_ranker_only.csv", index=False)

    report = {
        "metric": "Average binary log loss",
        "q_targets": Q_TARGETS,
        "full_targets": TARGET_COLUMNS,
        "train_rows": int(len(train_df)),
        "test_rows": int(len(test_df)),
        "feature_set_sizes": {name: len(cols) for name, cols in feature_sets.items()},
        "top_candidates": scores.head(30).to_dict(orient="records"),
        "targetwise_q_selection": selected.to_dict(orient="records"),
        "targetwise_q_score": q_score,
        "full_score_with_baseline_s": full_score,
        "args": vars(args),
    }
    (output_dir / "q_ranker_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Q ranker decoder report",
        "",
        f"- Train rows: {len(train_df)}",
        f"- Test rows: {len(test_df)}",
        f"- Best single Q CV: {scores.iloc[0]['q_avg_log_loss']:.6f} (`{scores.iloc[0]['name']}`)",
        f"- Target-wise Q CV: {q_score['q_avg_log_loss']:.6f}",
        f"- Full CV with baseline S: {full_score['avg_log_loss']:.6f}",
        "",
        "## Top Q candidates",
        "",
        dataframe_to_markdown(scores.head(15)[["name", "kind", "q_avg_log_loss", *Q_TARGETS]]),
        "",
        "## Target-wise Q selection",
        "",
        dataframe_to_markdown(selected[["target", "name", "kind", "q_avg_log_loss", *Q_TARGETS]]),
        "",
        "## Full score with baseline S",
        "",
        dataframe_to_markdown(pd.DataFrame([full_score])[["avg_log_loss", *TARGET_COLUMNS]]),
        "",
        "## Feature set sizes",
        "",
    ]
    for name, cols in feature_sets.items():
        lines.append(f"- {name}: {len(cols)}")
    lines.append("")
    (output_dir / "q_ranker_report.md").write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train Q1-Q3 within-subject pairwise ranker decoder.")
    parser.add_argument("--master-path", default="artifacts/10_master_daily.parquet")
    parser.add_argument("--latent-path", default="outputs/diffusion_encoder/day_latents.parquet")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--baseline-oof-path", default="outputs/latent_decoder/oof_targetwise_temporal_blend.csv")
    parser.add_argument("--baseline-submission-path", default="outputs/latent_decoder/submission_latent_decoder_targetwise_temporal.csv")
    parser.add_argument("--output-dir", default="outputs/q_ranker_decoder")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--feature-sets", default="q_core,q_core_latent,all_rankdev")
    parser.add_argument("--c-values", default="0.01,0.03,0.1,0.3")
    parser.add_argument("--alphas", default="2,5,10,20,50")
    parser.add_argument("--betas", default="0,0.25,0.5,0.75,1,1.5,2,3")
    parser.add_argument("--mean-modes", default="subject,half,half_subject_50,half_subject_75")
    parser.add_argument("--baseline-blend-weights", default="0.25,0.5,0.75")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    train_df, test_df = load_joined_frames(args)
    train_df, test_df, feature_sets = add_engineered_features(train_df, test_df)
    folds = make_subject_time_folds(train_df, args.folds)
    scores, oof_cache, test_cache = evaluate_rankers(train_df, test_df, feature_sets, folds, args)
    selected, q_oof, q_test, q_score = build_targetwise_q(scores, oof_cache, test_cache, train_df)
    full_score = build_full_outputs(args, train_df, test_df, q_oof, q_test, output_dir)
    write_outputs(output_dir, args, train_df, test_df, feature_sets, scores, selected, q_score, full_score, q_oof, q_test)
    print(f"best_single_q={scores.iloc[0]['name']} q_avg={scores.iloc[0]['q_avg_log_loss']:.6f}")
    print(f"targetwise_q_avg={q_score['q_avg_log_loss']:.6f}")
    print(f"full_avg_with_baseline_s={full_score['avg_log_loss']:.6f}")
    print(f"saved report: {output_dir / 'q_ranker_report.md'}")


if __name__ == "__main__":
    main()
