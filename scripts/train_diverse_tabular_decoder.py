from __future__ import annotations

import argparse
import json
import re
import warnings
from dataclasses import dataclass
from pathlib import Path

import catboost as cb
import lightgbm as lgb
import numpy as np
import pandas as pd
import xgboost as xgb
from pandas.errors import PerformanceWarning
from sklearn.metrics import log_loss


KEY_COLUMNS = ["subject_id", "sleep_date", "lifelog_date"]
TARGET_COLUMNS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
EPS = 1e-5

warnings.filterwarnings("ignore", category=PerformanceWarning)


@dataclass(frozen=True)
class ModelSpec:
    name: str
    kind: str
    feature_set: str
    params: dict


def normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in KEY_COLUMNS:
        out[col] = out[col].astype(str)
    return out


def assert_unique_keys(df: pd.DataFrame, name: str) -> None:
    duplicates = int(df.duplicated(KEY_COLUMNS).sum())
    if duplicates:
        raise ValueError(f"{name} has duplicated key rows: {duplicates}")


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]+", "_", value).strip("_")


def average_log_loss(y_true: pd.DataFrame, pred: np.ndarray) -> tuple[float, dict[str, float]]:
    clipped = np.clip(pred, EPS, 1.0 - EPS)
    per_target = {
        target: float(log_loss(y_true[target].to_numpy(), clipped[:, i], labels=[0, 1]))
        for i, target in enumerate(TARGET_COLUMNS)
    }
    return float(np.mean(list(per_target.values()))), per_target


def make_subject_time_folds(train_df: pd.DataFrame, n_folds: int) -> list[tuple[np.ndarray, np.ndarray]]:
    ordered = train_df.reset_index(names="_idx").sort_values(["subject_id", "lifelog_date", "sleep_date"])
    val_indices: list[list[int]] = [[] for _ in range(n_folds)]
    for _, group in ordered.groupby("subject_id", sort=False):
        chunks = np.array_split(group["_idx"].to_numpy(), n_folds)
        for fold, chunk in enumerate(chunks):
            val_indices[fold].extend(chunk.tolist())
    all_indices = np.arange(len(train_df))
    folds = []
    for indices in val_indices:
        val_idx = np.array(sorted(indices), dtype=int)
        train_idx = np.setdiff1d(all_indices, val_idx, assume_unique=False)
        folds.append((train_idx, val_idx))
    return folds


def load_frames(args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame]:
    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    features = normalize_keys(pd.read_parquet(args.feature_path))
    for name, frame in [("train", train), ("sample", sample), ("features", features)]:
        assert_unique_keys(frame, name)

    drop_cols = set(TARGET_COLUMNS + ["role", "split", "is_labeled"])
    feature_cols = [col for col in features.columns if col not in drop_cols]
    train_joined = train.merge(features[feature_cols], on=KEY_COLUMNS, how="left", validate="one_to_one")
    test_joined = sample[KEY_COLUMNS].merge(features[feature_cols], on=KEY_COLUMNS, how="left", validate="one_to_one")
    if train_joined.isna().all(axis=1).any() or test_joined.isna().all(axis=1).any():
        raise ValueError("Some rows failed to join with aggregate features")

    for latent_item in [part for part in args.latent_paths.split(",") if part.strip()]:
        latent_path = Path(latent_item)
        if not latent_path.exists():
            continue
        latents = normalize_keys(pd.read_parquet(latent_path))
        assert_unique_keys(latents, str(latent_path))
        prefix = safe_name(latent_path.parent.name)
        z_cols = [col for col in latents.columns if col.startswith("z_")]
        renamed = {col: f"{prefix}__{col}" for col in z_cols}
        latent_features = latents[KEY_COLUMNS + z_cols].rename(columns=renamed)
        train_joined = train_joined.merge(latent_features, on=KEY_COLUMNS, how="left", validate="one_to_one")
        test_joined = test_joined.merge(latent_features, on=KEY_COLUMNS, how="left", validate="one_to_one")

    return train_joined, test_joined


def add_engineered_features(train_df: pd.DataFrame, test_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, list[str]]]:
    all_df = pd.concat(
        [
            train_df.assign(_split="train", _row=np.arange(len(train_df))),
            test_df.assign(_split="test", _row=np.arange(len(test_df))),
        ],
        ignore_index=True,
    )
    life_dt = pd.to_datetime(all_df["lifelog_date"])
    sleep_dt = pd.to_datetime(all_df["sleep_date"])
    all_df["weekday"] = life_dt.dt.weekday.astype(float)
    all_df["weekday_sin"] = np.sin(2 * np.pi * all_df["weekday"] / 7.0)
    all_df["weekday_cos"] = np.cos(2 * np.pi * all_df["weekday"] / 7.0)
    all_df["sleep_weekday"] = sleep_dt.dt.weekday.astype(float)
    all_df["sleep_weekday_sin"] = np.sin(2 * np.pi * all_df["sleep_weekday"] / 7.0)
    all_df["sleep_weekday_cos"] = np.cos(2 * np.pi * all_df["sleep_weekday"] / 7.0)
    all_df["date_ord"] = life_dt.map(pd.Timestamp.toordinal).astype(float)
    ordered = all_df.sort_values(["subject_id", "lifelog_date", "sleep_date"]).copy()
    ordered["panel_index"] = ordered.groupby("subject_id").cumcount().astype(float)
    panel_max = ordered.groupby("subject_id")["panel_index"].transform("max").replace(0.0, 1.0)
    ordered["panel_position"] = ordered["panel_index"] / panel_max
    all_df = ordered.sort_index()

    subject_dummies = pd.get_dummies(all_df["subject_id"], prefix="subject", dtype=float)
    subject_dummies = subject_dummies.reindex(sorted(subject_dummies.columns), axis=1)
    subject_cols = subject_dummies.columns.tolist()
    all_df = pd.concat([all_df, subject_dummies], axis=1)

    base_numeric = [
        col
        for col in all_df.columns
        if col not in KEY_COLUMNS + TARGET_COLUMNS + ["date", "_split", "_row"]
        and pd.api.types.is_numeric_dtype(all_df[col])
    ]
    base_numeric = sorted(dict.fromkeys(base_numeric))
    latent_cols = [col for col in base_numeric if "__z_" in col]
    time_cols = [
        "weekday",
        "weekday_sin",
        "weekday_cos",
        "sleep_weekday",
        "sleep_weekday_sin",
        "sleep_weekday_cos",
        "date_ord",
        "panel_index",
        "panel_position",
    ]

    missing_cols = []
    log_cols = []
    for col in base_numeric:
        values = pd.to_numeric(all_df[col], errors="coerce")
        miss_rate = float(values.isna().mean())
        if 0.0 < miss_rate < 1.0:
            miss_col = f"miss__{col}"
            all_df[miss_col] = values.isna().astype(float)
            missing_cols.append(miss_col)
        finite = values[np.isfinite(values)]
        if len(finite) and finite.min() >= 0 and finite.quantile(0.95) > 10:
            log_col = f"log1p__{col}"
            all_df[log_col] = np.log1p(values)
            log_cols.append(log_col)

    grouped = all_df.groupby("subject_id", sort=False)
    center_cols = []
    rank_cols = []
    for col in [c for c in base_numeric if c not in subject_cols and c not in time_cols]:
        values = pd.to_numeric(all_df[col], errors="coerce")
        center_col = f"sub_center__{col}"
        rank_col = f"sub_rank__{col}"
        all_df[center_col] = values - grouped[col].transform("mean")
        all_df[rank_col] = grouped[col].rank(method="average", pct=True)
        center_cols.append(center_col)
        rank_cols.append(rank_col)

    feature_sets = {
        "raw": sorted(dict.fromkeys(base_numeric + subject_cols + time_cols)),
        "rankdev": sorted(dict.fromkeys(base_numeric + log_cols + missing_cols + center_cols + rank_cols + subject_cols + time_cols)),
        "nosubject_rankdev": sorted(dict.fromkeys(base_numeric + log_cols + missing_cols + center_cols + rank_cols + time_cols)),
        "latent": sorted(dict.fromkeys(latent_cols + subject_cols + time_cols)),
        "latent_rankdev": sorted(dict.fromkeys(latent_cols + [c for c in center_cols + rank_cols if "__z_" in c] + subject_cols + time_cols)),
    }

    train_out = all_df[all_df["_split"] == "train"].sort_values("_row").drop(columns=["_split", "_row"]).reset_index(drop=True)
    test_out = all_df[all_df["_split"] == "test"].sort_values("_row").drop(columns=["_split", "_row"]).reset_index(drop=True)
    return train_out, test_out, feature_sets


def make_specs(args: argparse.Namespace, feature_sets: dict[str, list[str]]) -> list[ModelSpec]:
    selected_sets = [name for name in args.feature_sets.split(",") if name in feature_sets]
    specs: list[ModelSpec] = []
    lgbm_params = {
        "n_estimators": 120,
        "learning_rate": 0.035,
        "num_leaves": 7,
        "max_depth": 3,
        "min_child_samples": 24,
        "subsample": 0.8,
        "subsample_freq": 1,
        "colsample_bytree": 0.55,
        "reg_alpha": 0.5,
        "reg_lambda": 15.0,
        "objective": "binary",
        "verbosity": -1,
        "random_state": args.seed,
        "n_jobs": args.n_jobs,
    }
    xgb_params = {
        "n_estimators": 120,
        "learning_rate": 0.035,
        "max_depth": 2,
        "min_child_weight": 12,
        "subsample": 0.8,
        "colsample_bytree": 0.55,
        "reg_alpha": 0.5,
        "reg_lambda": 15.0,
        "objective": "binary:logistic",
        "eval_metric": "logloss",
        "tree_method": "hist",
        "random_state": args.seed + 11,
        "n_jobs": args.n_jobs,
    }
    cat_params = {
        "iterations": 160,
        "depth": 3,
        "learning_rate": 0.035,
        "l2_leaf_reg": 12.0,
        "loss_function": "Logloss",
        "eval_metric": "Logloss",
        "random_seed": args.seed + 23,
        "allow_writing_files": False,
        "verbose": False,
    }
    for feature_set in selected_sets:
        specs.append(ModelSpec(f"lgbm_{feature_set}", "lgbm", feature_set, dict(lgbm_params)))
        specs.append(ModelSpec(f"xgb_{feature_set}", "xgb", feature_set, dict(xgb_params)))
        specs.append(ModelSpec(f"cat_{feature_set}", "cat", feature_set, dict(cat_params)))
    return specs


def fit_constant(y_train: np.ndarray) -> float | None:
    unique = np.unique(y_train)
    if len(unique) == 1:
        return float(unique[0])
    return None


def fit_predict_one(kind: str, params: dict, x_train: pd.DataFrame, y_train: np.ndarray, x_eval: pd.DataFrame) -> np.ndarray:
    constant = fit_constant(y_train)
    if constant is not None:
        return np.full(len(x_eval), constant, dtype=float)
    if kind == "lgbm":
        model = lgb.LGBMClassifier(**params)
    elif kind == "xgb":
        model = xgb.XGBClassifier(**params)
    elif kind == "cat":
        model = cb.CatBoostClassifier(**params)
    else:
        raise ValueError(f"Unsupported model kind: {kind}")
    model.fit(x_train, y_train)
    return model.predict_proba(x_eval)[:, 1]


def clean_feature_frame(frame: pd.DataFrame) -> pd.DataFrame:
    return frame.replace([np.inf, -np.inf], np.nan).astype(np.float32)


def fit_oof_and_test(
    spec: ModelSpec,
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    feature_sets: dict[str, list[str]],
    folds: list[tuple[np.ndarray, np.ndarray]],
) -> tuple[np.ndarray, np.ndarray]:
    cols = feature_sets[spec.feature_set]
    x_all = clean_feature_frame(train_df[cols])
    x_test = clean_feature_frame(test_df[cols])
    y_all = train_df[TARGET_COLUMNS].astype(int).reset_index(drop=True)
    oof = np.zeros((len(train_df), len(TARGET_COLUMNS)), dtype=float)
    test = np.zeros((len(test_df), len(TARGET_COLUMNS)), dtype=float)
    for train_idx, val_idx in folds:
        x_train = x_all.iloc[train_idx]
        x_val = x_all.iloc[val_idx]
        for target_i, target in enumerate(TARGET_COLUMNS):
            oof[val_idx, target_i] = fit_predict_one(
                spec.kind,
                spec.params,
                x_train,
                y_all.loc[train_idx, target].to_numpy(),
                x_val,
            )
    for target_i, target in enumerate(TARGET_COLUMNS):
        test[:, target_i] = fit_predict_one(spec.kind, spec.params, x_all, y_all[target].to_numpy(), x_test)
    return np.clip(oof, EPS, 1.0 - EPS), np.clip(test, EPS, 1.0 - EPS)


def write_prediction_files(
    output_dir: Path,
    train_df: pd.DataFrame,
    sample_path: str,
    name: str,
    oof: np.ndarray,
    test: np.ndarray,
) -> tuple[Path, Path]:
    oof_df = train_df[KEY_COLUMNS + TARGET_COLUMNS].copy()
    for target_i, target in enumerate(TARGET_COLUMNS):
        oof_df[f"pred_{target}"] = oof[:, target_i]
    oof_path = output_dir / f"oof_{name}.csv"
    oof_df.to_csv(oof_path, index=False)

    submission = pd.read_csv(sample_path)
    for target_i, target in enumerate(TARGET_COLUMNS):
        submission[target] = test[:, target_i]
    submission_path = output_dir / f"submission_{name}.csv"
    submission.to_csv(submission_path, index=False)
    return oof_path, submission_path


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    train_df, test_df = load_frames(args)
    train_df, test_df, feature_sets = add_engineered_features(train_df, test_df)
    folds = make_subject_time_folds(train_df, args.folds)
    specs = make_specs(args, feature_sets)
    y_true = train_df[TARGET_COLUMNS]

    scores = []
    manifest = []
    for spec_i, spec in enumerate(specs, start=1):
        print(f"[{spec_i}/{len(specs)}] {spec.name} ({len(feature_sets[spec.feature_set])} features)")
        oof, test = fit_oof_and_test(spec, train_df, test_df, feature_sets, folds)
        avg, per_target = average_log_loss(y_true, oof)
        oof_path, submission_path = write_prediction_files(output_dir, train_df, args.sample_path, spec.name, oof, test)
        scores.append({"name": spec.name, "kind": spec.kind, "feature_set": spec.feature_set, "avg_log_loss": avg, **per_target})
        manifest.append(
            {
                "name": spec.name,
                "kind": spec.kind,
                "feature_set": spec.feature_set,
                "n_features": len(feature_sets[spec.feature_set]),
                "oof_path": str(oof_path),
                "submission_path": str(submission_path),
            }
        )

    scores_df = pd.DataFrame(scores).sort_values("avg_log_loss")
    manifest_df = pd.DataFrame(manifest)
    scores_df.to_csv(output_dir / "candidate_scores.csv", index=False)
    manifest_df.to_csv(output_dir / "candidate_manifest.csv", index=False)
    report = {
        "feature_set_sizes": {name: len(cols) for name, cols in feature_sets.items()},
        "top_candidates": scores_df.head(20).to_dict(orient="records"),
        "args": vars(args),
    }
    (output_dir / "diverse_tabular_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(scores_df.head(12).to_string(index=False))
    print(f"saved: {output_dir / 'candidate_manifest.csv'}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Diverse GBDT decoder over aggregate daily features and diffusion latents.")
    parser.add_argument("--feature-path", default="outputs/data_probe/all_subject_day_features.parquet")
    parser.add_argument("--latent-paths", default="outputs/diffusion_encoder/day_latents.parquet,outputs/diffusion_encoder_id_long/day_latents.parquet,outputs/diffusion_encoder_subjectless_long/day_latents.parquet")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--output-dir", default="outputs/diverse_tabular_decoder")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--feature-sets", default="raw,rankdev,latent,latent_rankdev")
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--n-jobs", type=int, default=4)
    return parser.parse_args()


if __name__ == "__main__":
    main()
