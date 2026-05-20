from __future__ import annotations

import argparse
import inspect
import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from pandas.errors import PerformanceWarning
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.metrics import log_loss
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


KEY_COLUMNS = ["subject_id", "sleep_date", "lifelog_date"]
TARGET_COLUMNS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
EPS = 1e-5


ANCHOR_SOURCES = {
    "recovery15": (
        "outputs/lb_feedback_recovery_uploads/oof_15_v18_old15_prob_blend.csv",
        "outputs/lb_feedback_recovery_uploads/submission_15_v18_old15_prob_blend.csv",
    ),
    "multi_signal": (
        "outputs/multi_signal_qcount_blend_w015_020_015_015/oof_multi_signal_qcount_blend.csv",
        "outputs/multi_signal_qcount_blend_w015_020_015_015/submission_multi_signal_qcount_blend.csv",
    ),
    "v18_q3tail": (
        "outputs/sample_portfolio_v18_q3tail_w100/oof_sample_support_target_blend.csv",
        "outputs/sample_portfolio_v18_q3tail_w100/submission_sample_support_target_blend.csv",
    ),
    "v27_q3mid": (
        "outputs/sample_portfolio_v27_v25_plus_v17fused_q3mid_w065/oof_sample_support_target_blend.csv",
        "outputs/sample_portfolio_v27_v25_plus_v17fused_q3mid_w065/submission_sample_support_target_blend.csv",
    ),
    "v35e": (
        "outputs/sample_portfolio_v35e_v35b_plus_stack_q2mid_w050_prob/oof_sample_support_target_blend.csv",
        "outputs/sample_portfolio_v35e_v35b_plus_stack_q2mid_w050_prob/submission_sample_support_target_blend.csv",
    ),
    "trp_lgbm": (
        "outputs/temporal_retrieval_prototype_meta/oof_lgbm_temporal_retrieval_prototype_meta.csv",
        "outputs/temporal_retrieval_prototype_meta/submission_lgbm_temporal_retrieval_prototype_meta.csv",
    ),
    "trp_retrieval": (
        "outputs/temporal_retrieval_prototype_meta/oof_retrieval_source.csv",
        "outputs/temporal_retrieval_prototype_meta/submission_retrieval_source.csv",
    ),
    "trp_prototype": (
        "outputs/temporal_retrieval_prototype_meta/oof_prototype_source.csv",
        "outputs/temporal_retrieval_prototype_meta/submission_prototype_source.csv",
    ),
}


LATENT_SOURCES = {
    "diffusion": "outputs/diffusion_encoder/day_latents.parquet",
    "temporal_contrastive": "outputs/temporal_contrastive_encoder_zero_v1/day_latents.parquet",
}


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
    return float(np.mean([log_loss(y[target], pred[:, i], labels=[0, 1]) for i, target in enumerate(TARGET_COLUMNS)]))


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


def add_panel_calendar_features(train: pd.DataFrame, sample: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    all_rows = pd.concat(
        [
            train[KEY_COLUMNS].assign(_split="train", _row=np.arange(len(train))),
            sample[KEY_COLUMNS].assign(_split="test", _row=np.arange(len(sample))),
        ],
        ignore_index=True,
    )
    ordered = all_rows.sort_values(["subject_id", "lifelog_date", "sleep_date"]).copy()
    ordered["panel_index"] = ordered.groupby("subject_id").cumcount().astype(float)
    denom = ordered.groupby("subject_id")["panel_index"].transform("max").replace(0, 1)
    ordered["panel_position"] = ordered["panel_index"] / denom
    restored = ordered.sort_values(["_split", "_row"])

    def build(split: str) -> pd.DataFrame:
        out = restored[restored["_split"].eq(split)].sort_values("_row")[KEY_COLUMNS + ["panel_index", "panel_position"]].reset_index(drop=True)
        date = pd.to_datetime(out["lifelog_date"])
        day_of_year = date.dt.dayofyear.astype(float)
        dow = date.dt.dayofweek.astype(float)
        out["dow_sin"] = np.sin(2 * np.pi * dow / 7)
        out["dow_cos"] = np.cos(2 * np.pi * dow / 7)
        out["is_weekend"] = dow.isin([5, 6]).astype(float)
        out["doy_sin"] = np.sin(2 * np.pi * day_of_year / 366)
        out["doy_cos"] = np.cos(2 * np.pi * day_of_year / 366)
        # South Korea public holidays in the competition date range.
        holiday_dates = {
            "2024-06-06",
            "2024-08-15",
            "2024-09-16",
            "2024-09-17",
            "2024-09-18",
            "2024-10-03",
            "2024-10-09",
        }
        out["is_kr_public_holiday"] = date.dt.strftime("%Y-%m-%d").isin(holiday_dates).astype(float)
        out["near_kr_public_holiday"] = date.apply(
            lambda value: float(
                any(abs((value.normalize() - pd.Timestamp(day)).days) <= 1 for day in holiday_dates)
            )
        )
        subject_codes = out["subject_id"].str.extract(r"(\d+)").fillna(0).astype(int)[0]
        out["subject_code"] = subject_codes.astype(float)
        return out

    return build("train"), build("test")


def align_by_keys(source: pd.DataFrame, keys: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    source = normalize_keys(source)
    keys = normalize_keys(keys)
    merged = keys.merge(source[KEY_COLUMNS + columns], on=KEY_COLUMNS, how="left", validate="one_to_one")
    missing = merged[columns].isna().all(axis=1).sum()
    if missing:
        raise ValueError(f"{missing} rows failed to align by keys")
    return merged[columns]


def add_anchor_features(features_train: pd.DataFrame, features_test: pd.DataFrame, train: pd.DataFrame, sample: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    added: list[str] = []
    for name, (oof_path, sub_path) in ANCHOR_SOURCES.items():
        if not Path(oof_path).exists() or not Path(sub_path).exists():
            continue
        oof = normalize_keys(pd.read_csv(oof_path))
        sub = normalize_keys(pd.read_csv(sub_path))
        if not oof[KEY_COLUMNS].equals(train[KEY_COLUMNS]) or not sub[KEY_COLUMNS].equals(sample[KEY_COLUMNS]):
            continue
        train_pred = np.clip(prediction_matrix(oof), EPS, 1 - EPS)
        test_pred = np.clip(submission_matrix(sub), EPS, 1 - EPS)
        for i, target in enumerate(TARGET_COLUMNS):
            prob_col = f"anchor_{name}_{target}_prob"
            logit_col = f"anchor_{name}_{target}_logit"
            features_train[prob_col] = train_pred[:, i]
            features_test[prob_col] = test_pred[:, i]
            features_train[logit_col] = safe_logit(train_pred[:, i])
            features_test[logit_col] = safe_logit(test_pred[:, i])
            added.extend([prob_col, logit_col])
    return features_train, features_test, added


def add_compressed_parquet_features(
    features_train: pd.DataFrame,
    features_test: pd.DataFrame,
    train: pd.DataFrame,
    sample: pd.DataFrame,
    path: str,
    prefix: str,
    n_components: int,
) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    if not Path(path).exists():
        return features_train, features_test, []
    frame = pd.read_parquet(path)
    frame = normalize_keys(frame)
    numeric_cols = [
        col
        for col in frame.select_dtypes(include=[np.number]).columns
        if col not in TARGET_COLUMNS and not col.startswith("pred_")
    ]
    if not numeric_cols:
        return features_train, features_test, []
    train_raw = align_by_keys(frame, train[KEY_COLUMNS], numeric_cols)
    test_raw = align_by_keys(frame, sample[KEY_COLUMNS], numeric_cols)
    all_raw = pd.concat([train_raw, test_raw], ignore_index=True)
    n_comp = min(n_components, len(numeric_cols), max(1, len(all_raw) - 1))
    pipe = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), PCA(n_components=n_comp, random_state=2026))
    all_comp = pipe.fit_transform(all_raw)
    columns = [f"{prefix}_pc_{i:02d}" for i in range(n_comp)]
    features_train[columns] = all_comp[: len(train)]
    features_test[columns] = all_comp[len(train) :]
    return features_train, features_test, columns


def prepare_features(args: argparse.Namespace) -> None:
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    features_train, features_test = add_panel_calendar_features(train, sample)
    feature_columns = [col for col in features_train.columns if col not in KEY_COLUMNS]

    features_train, features_test, anchor_cols = add_anchor_features(features_train, features_test, train, sample)
    feature_columns.extend(anchor_cols)

    features_train, features_test, master_cols = add_compressed_parquet_features(
        features_train,
        features_test,
        train,
        sample,
        args.master_path,
        "master",
        args.master_pca_components,
    )
    feature_columns.extend(master_cols)

    for latent_name, latent_path in LATENT_SOURCES.items():
        features_train, features_test, latent_cols = add_compressed_parquet_features(
            features_train,
            features_test,
            train,
            sample,
            latent_path,
            latent_name,
            args.latent_pca_components,
        )
        feature_columns.extend(latent_cols)

    features_train[KEY_COLUMNS + feature_columns].to_csv(output_dir / "features_train.csv", index=False)
    features_test[KEY_COLUMNS + feature_columns].to_csv(output_dir / "features_test.csv", index=False)
    train[KEY_COLUMNS + TARGET_COLUMNS].to_csv(output_dir / "labels_train.csv", index=False)
    with (output_dir / "feature_manifest.json").open("w") as f:
        json.dump(
            {
                "n_train": int(len(train)),
                "n_test": int(len(sample)),
                "n_features": int(len(feature_columns)),
                "feature_columns": feature_columns,
                "anchor_sources": sorted(ANCHOR_SOURCES),
                "external_calendar": "South Korea public holidays in 2024-06..2024-11 plus day-of-year/weekend cycles.",
                "external_model": "TabPFN 8.0.3 pretrained tabular foundation model, trained fold-safely as a meta source.",
            },
            f,
            indent=2,
        )
    print(f"prepared features: train={features_train.shape}, test={features_test.shape}, features={len(feature_columns)}")


def make_tabpfn_classifier(device: str, seed: int, n_estimators: int):
    from tabpfn import TabPFNClassifier

    sig = inspect.signature(TabPFNClassifier)
    candidates = {
        "device": device,
        "random_state": seed,
        "n_estimators": n_estimators,
        "ignore_pretraining_limits": True,
        "fit_mode": "low_memory",
    }
    kwargs = {key: value for key, value in candidates.items() if key in sig.parameters}
    return TabPFNClassifier(**kwargs)


def positive_class_probability(model, x: np.ndarray, train_labels: np.ndarray) -> np.ndarray:
    proba = model.predict_proba(x)
    classes = list(getattr(model, "classes_", []))
    if proba.ndim == 1:
        return np.clip(proba.astype(float), EPS, 1 - EPS)
    if 1 in classes:
        idx = classes.index(1)
        return np.clip(proba[:, idx].astype(float), EPS, 1 - EPS)
    return np.full(len(x), float(np.mean(train_labels)), dtype=float)


def train_tabpfn(args: argparse.Namespace) -> None:
    output_dir = Path(args.output_dir)
    feature_path = output_dir / "features_train.csv"
    test_path = output_dir / "features_test.csv"
    label_path = output_dir / "labels_train.csv"
    if not feature_path.exists() or not test_path.exists() or not label_path.exists():
        prepare_features(args)

    train_x_df = normalize_keys(pd.read_csv(feature_path))
    test_x_df = normalize_keys(pd.read_csv(test_path))
    labels = normalize_keys(pd.read_csv(label_path))
    feature_columns = [col for col in train_x_df.columns if col not in KEY_COLUMNS]
    x_train = train_x_df[feature_columns].to_numpy(dtype=np.float32)
    x_test = test_x_df[feature_columns].to_numpy(dtype=np.float32)
    y = labels[TARGET_COLUMNS].astype(int)

    folds = make_subject_time_folds(labels, args.n_folds)
    oof_pred = np.zeros((len(labels), len(TARGET_COLUMNS)), dtype=float)
    test_pred = np.zeros((len(test_x_df), len(TARGET_COLUMNS)), dtype=float)

    for target_idx, target in enumerate(TARGET_COLUMNS):
        target_values = y[target].to_numpy(dtype=int)
        for fold_idx, (trn_idx, val_idx) in enumerate(folds):
            model = make_tabpfn_classifier(args.device, args.seed + 100 * target_idx + fold_idx, args.n_estimators)
            model.fit(x_train[trn_idx], target_values[trn_idx])
            oof_pred[val_idx, target_idx] = positive_class_probability(model, x_train[val_idx], target_values[trn_idx])
        full_model = make_tabpfn_classifier(args.device, args.seed + 1000 + target_idx, args.n_estimators)
        full_model.fit(x_train, target_values)
        test_pred[:, target_idx] = positive_class_probability(full_model, x_test, target_values)
        print(target, log_loss(target_values, np.clip(oof_pred[:, target_idx], EPS, 1 - EPS), labels=[0, 1]))

    oof_pred = np.clip(oof_pred, EPS, 1 - EPS)
    test_pred = np.clip(test_pred, EPS, 1 - EPS)
    oof = labels[KEY_COLUMNS].copy()
    for i, target in enumerate(TARGET_COLUMNS):
        oof[f"pred_{target}"] = oof_pred[:, i]
    submission = test_x_df[KEY_COLUMNS].copy()
    for i, target in enumerate(TARGET_COLUMNS):
        submission[target] = test_pred[:, i]

    oof_path = output_dir / "oof_tabpfn_external_meta.csv"
    sub_path = output_dir / "submission_tabpfn_external_meta.csv"
    report_path = output_dir / "tabpfn_external_report.json"
    oof.to_csv(oof_path, index=False)
    submission.to_csv(sub_path, index=False)
    report = {
        "oof_avg_log_loss": score(y, oof_pred),
        "n_features": int(len(feature_columns)),
        "device": args.device,
        "n_estimators": args.n_estimators,
        "oof_path": str(oof_path),
        "submission_path": str(sub_path),
    }
    with report_path.open("w") as f:
        json.dump(report, f, indent=2)
    print(json.dumps(report, indent=2))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train an external TabPFN meta source on fold-safe ETRI features.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--master-path", default="artifacts/10_master_daily.parquet")
    parser.add_argument("--output-dir", default="outputs/tabpfn_external_meta")
    parser.add_argument("--master-pca-components", type=int, default=48)
    parser.add_argument("--latent-pca-components", type=int, default=24)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--n-estimators", type=int, default=8)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--prepare-only", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    warnings.filterwarnings("ignore", category=PerformanceWarning)
    if args.prepare_only:
        prepare_features(args)
        return
    try:
        train_tabpfn(args)
    except Exception as exc:
        if type(exc).__name__ != "TabPFNLicenseError":
            raise
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        report = {
            "status": "blocked",
            "reason": "TabPFN local pretrained weights require one-time license acceptance/API token.",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "next_step": "Accept the TabPFN license and set TABPFN_TOKEN before rerunning this script.",
        }
        with (output_dir / "tabpfn_external_blocked.json").open("w") as f:
            json.dump(report, f, indent=2)
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
