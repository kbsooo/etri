from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cross_decomposition import PLSRegression
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.metrics import log_loss
from sklearn.preprocessing import StandardScaler


KEY_COLUMNS = ["subject_id", "sleep_date", "lifelog_date"]
TARGET_COLUMNS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
EPS = 1e-5


def normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in KEY_COLUMNS:
        out[col] = out[col].astype(str)
    return out


def assert_unique_keys(df: pd.DataFrame, name: str) -> None:
    dupes = df.duplicated(KEY_COLUMNS).sum()
    if dupes:
        raise ValueError(f"{name} has duplicated key rows: {dupes}")


def safe_logit(values: np.ndarray) -> np.ndarray:
    values = np.clip(values.astype(float), EPS, 1.0 - EPS)
    return np.log(values / (1.0 - values))


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(values, -50.0, 50.0)))


def subject_prior_prob(train_part: pd.DataFrame, eval_part: pd.DataFrame, alpha: float) -> np.ndarray:
    global_rate = train_part[TARGET_COLUMNS].mean().clip(EPS, 1.0 - EPS)
    subject_sum = train_part.groupby("subject_id")[TARGET_COLUMNS].sum()
    subject_count = train_part.groupby("subject_id")[TARGET_COLUMNS].count()
    subject_rate = (subject_sum + alpha * global_rate) / (subject_count + alpha)
    pred = np.zeros((len(eval_part), len(TARGET_COLUMNS)), dtype=np.float32)
    global_values = global_rate.to_numpy(np.float32)
    for row_i, subject in enumerate(eval_part["subject_id"].astype(str)):
        if subject in subject_rate.index:
            pred[row_i] = subject_rate.loc[subject, TARGET_COLUMNS].to_numpy(np.float32)
        else:
            pred[row_i] = global_values
    return np.clip(pred, EPS, 1.0 - EPS)


def make_subject_time_folds(train_df: pd.DataFrame, n_folds: int) -> list[tuple[np.ndarray, np.ndarray]]:
    ordered = train_df.reset_index(names="_idx").sort_values(["subject_id", "lifelog_date", "sleep_date"])
    val_indices: list[list[int]] = [[] for _ in range(n_folds)]
    for _, group in ordered.groupby("subject_id", sort=False):
        chunks = np.array_split(group["_idx"].to_numpy(), n_folds)
        for fold, chunk in enumerate(chunks):
            val_indices[fold].extend(chunk.tolist())
    all_idx = np.arange(len(train_df), dtype=np.int64)
    folds = []
    for indices in val_indices:
        val_idx = np.array(sorted(indices), dtype=np.int64)
        train_idx = np.setdiff1d(all_idx, val_idx, assume_unique=False)
        folds.append((train_idx, val_idx))
    return folds


def numeric_feature_columns(df: pd.DataFrame) -> list[str]:
    banned = set(KEY_COLUMNS + TARGET_COLUMNS + ["split", "role", "date", "is_labeled"])
    return [
        col
        for col in df.columns
        if col not in banned
        and not col.startswith("pred_")
        and pd.api.types.is_numeric_dtype(df[col])
    ]


def load_feature_table(path: Path, prefix: str) -> pd.DataFrame:
    df = normalize_keys(pd.read_parquet(path))
    assert_unique_keys(df, str(path))
    cols = numeric_feature_columns(df)
    rename = {col: f"{prefix}__{col}" for col in cols}
    return df[KEY_COLUMNS + cols].rename(columns=rename)


def load_teacher_predictions(oof_path: str, submission_path: str, train: pd.DataFrame, sample: pd.DataFrame) -> tuple[np.ndarray | None, np.ndarray | None]:
    if not oof_path or not submission_path:
        return None, None
    oof = normalize_keys(pd.read_csv(oof_path))
    submission = normalize_keys(pd.read_csv(submission_path))
    if not oof[KEY_COLUMNS].equals(train[KEY_COLUMNS]):
        raise ValueError(f"Teacher OOF keys do not match train keys: {oof_path}")
    if not submission[KEY_COLUMNS].equals(sample[KEY_COLUMNS]):
        raise ValueError(f"Teacher submission keys do not match sample keys: {submission_path}")
    return (
        np.clip(np.column_stack([oof[f"pred_{target}"].to_numpy(float) for target in TARGET_COLUMNS]), EPS, 1.0 - EPS),
        np.clip(submission[TARGET_COLUMNS].to_numpy(float), EPS, 1.0 - EPS),
    )


def load_latents(path: Path, prefix: str) -> pd.DataFrame:
    df = normalize_keys(pd.read_parquet(path))
    assert_unique_keys(df, str(path))
    z_cols = sorted(col for col in df.columns if col.startswith("z_"))
    return df[KEY_COLUMNS + z_cols].rename(columns={col: f"{prefix}__{col}" for col in z_cols})


def join_features(train: pd.DataFrame, sample: pd.DataFrame, tables: list[pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    train_features = train[KEY_COLUMNS].copy()
    sample_features = sample[KEY_COLUMNS].copy()
    for table in tables:
        feature_cols = [col for col in table.columns if col not in KEY_COLUMNS]
        train_features = train_features.merge(table, on=KEY_COLUMNS, how="left", validate="one_to_one")
        sample_features = sample_features.merge(table, on=KEY_COLUMNS, how="left", validate="one_to_one")
        if train_features[feature_cols].isna().all(axis=1).any():
            raise ValueError("Some train rows failed feature join")
        if sample_features[feature_cols].isna().all(axis=1).any():
            raise ValueError("Some sample rows failed feature join")
    feature_cols = [col for col in train_features.columns if col not in KEY_COLUMNS]
    return train_features, sample_features, feature_cols


def fit_transformers(x_train: np.ndarray, args: argparse.Namespace) -> tuple[SimpleImputer, StandardScaler, np.ndarray]:
    imputer = SimpleImputer(strategy="median", keep_empty_features=True)
    scaler = StandardScaler()
    x_imp = imputer.fit_transform(x_train)
    x_scaled = scaler.fit_transform(x_imp)
    std = np.nanstd(x_scaled, axis=0)
    keep = np.where(std > args.min_feature_std)[0]
    if keep.size == 0:
        raise ValueError("No non-constant features after preprocessing")
    return imputer, scaler, keep


def apply_transformers(x: np.ndarray, imputer: SimpleImputer, scaler: StandardScaler, keep: np.ndarray) -> np.ndarray:
    out = imputer.transform(x)
    out = scaler.transform(out)
    return out[:, keep]


def make_targets(y: np.ndarray, prior: np.ndarray, teacher: np.ndarray | None, mode: str) -> np.ndarray:
    if mode == "label":
        return y.astype(np.float32)
    if mode == "label_logit_residual":
        hard = np.clip(0.08 + 0.84 * y.astype(float), EPS, 1.0 - EPS)
        return (safe_logit(hard) - safe_logit(prior)).astype(np.float32)
    if mode == "label_prob_residual":
        return (y.astype(float) - prior).astype(np.float32)
    if mode == "teacher_logit_residual":
        if teacher is None:
            return (y.astype(float) - prior).astype(np.float32)
        return (safe_logit(teacher) - safe_logit(prior)).astype(np.float32)
    raise ValueError(f"Unknown target mode: {mode}")


def fit_encoder_block(
    x_fit: np.ndarray,
    y_fit: np.ndarray,
    x_eval: np.ndarray,
    prefix: str,
    args: argparse.Namespace,
) -> tuple[np.ndarray, list[str]]:
    blocks: list[np.ndarray] = []
    names: list[str] = []
    n_pls = min(args.pls_components, x_fit.shape[0] - 1, x_fit.shape[1])
    if n_pls > 0:
        pls = PLSRegression(n_components=n_pls, scale=False, max_iter=1000)
        pls.fit(x_fit, y_fit)
        z = pls.transform(x_eval).astype(np.float32)
        blocks.append(z)
        names.extend([f"{prefix}_pls_{i:02d}" for i in range(z.shape[1])])
    n_pca = min(args.pca_components, x_fit.shape[0] - 1, x_fit.shape[1])
    if n_pca > 0:
        pca = PCA(n_components=n_pca, svd_solver="randomized", random_state=args.seed)
        pca.fit(x_fit)
        z = pca.transform(x_eval).astype(np.float32)
        blocks.append(z)
        names.extend([f"{prefix}_pca_{i:02d}" for i in range(z.shape[1])])
    if not blocks:
        return np.zeros((x_eval.shape[0], 0), dtype=np.float32), []
    return np.concatenate(blocks, axis=1), names


def fold_latents(
    train_features: pd.DataFrame,
    sample_features: pd.DataFrame,
    feature_cols: list[str],
    train: pd.DataFrame,
    sample: pd.DataFrame,
    teacher_train: np.ndarray | None,
    teacher_sample: np.ndarray | None,
    args: argparse.Namespace,
) -> tuple[np.ndarray, np.ndarray, list[dict[str, float]], list[str]]:
    x_train_all = train_features[feature_cols].replace([np.inf, -np.inf], np.nan).to_numpy(np.float32)
    x_sample_all = sample_features[feature_cols].replace([np.inf, -np.inf], np.nan).to_numpy(np.float32)
    y = train[TARGET_COLUMNS].to_numpy(np.float32)
    folds = make_subject_time_folds(train, args.folds)
    target_modes = [part.strip() for part in args.target_modes.split(",") if part.strip()]
    oof_latents: np.ndarray | None = None
    feature_names: list[str] | None = None
    rows: list[dict[str, float]] = []
    for fold_id, (fit_idx, val_idx) in enumerate(folds, start=1):
        prior_fit = subject_prior_prob(train.iloc[fit_idx], train.iloc[fit_idx], args.prior_alpha)
        imputer, scaler, keep = fit_transformers(x_train_all[fit_idx], args)
        x_fit = apply_transformers(x_train_all[fit_idx], imputer, scaler, keep)
        x_val = apply_transformers(x_train_all[val_idx], imputer, scaler, keep)
        fold_blocks = []
        fold_names = []
        for mode in target_modes:
            target = make_targets(y[fit_idx], prior_fit, teacher_train[fit_idx] if teacher_train is not None else None, mode)
            block, names = fit_encoder_block(x_fit, target, x_val, mode, args)
            fold_blocks.append(block)
            fold_names.extend(names)
        fold_latent = np.concatenate(fold_blocks, axis=1).astype(np.float32)
        if oof_latents is None:
            oof_latents = np.zeros((len(train), fold_latent.shape[1]), dtype=np.float32)
            feature_names = fold_names
        if fold_latent.shape[1] != oof_latents.shape[1]:
            raise ValueError("Fold latent dimension changed")
        oof_latents[val_idx] = fold_latent

        # A rough direct diagnostic: fit tiny least-squares in latent space on fold train encoded by same encoder.
        rows.append({"fold": fold_id, "valid_rows": float(len(val_idx)), "latent_dim": float(fold_latent.shape[1]), "kept_features": float(len(keep))})

    prior_full = subject_prior_prob(train, train, args.prior_alpha)
    imputer, scaler, keep = fit_transformers(x_train_all, args)
    x_fit = apply_transformers(x_train_all, imputer, scaler, keep)
    x_sample = apply_transformers(x_sample_all, imputer, scaler, keep)
    full_blocks = []
    full_names = []
    for mode in target_modes:
        target = make_targets(y, prior_full, teacher_train, mode)
        block, names = fit_encoder_block(x_fit, target, x_sample, mode, args)
        full_blocks.append(block)
        full_names.extend(names)
    sample_latents = np.concatenate(full_blocks, axis=1).astype(np.float32)
    if feature_names is None:
        feature_names = full_names
    return oof_latents, sample_latents, rows, feature_names


def write_latent_table(path: Path, train: pd.DataFrame, sample: pd.DataFrame, train_latents: np.ndarray, sample_latents: np.ndarray, names: list[str]) -> None:
    train_lat = pd.DataFrame(train_latents, columns=[f"z_{i:03d}" for i in range(train_latents.shape[1])])
    sample_lat = pd.DataFrame(sample_latents, columns=[f"z_{i:03d}" for i in range(sample_latents.shape[1])])
    train_base = add_time_metadata(train)
    sample_base = add_time_metadata(sample)
    train_out = pd.concat([train_base.reset_index(drop=True), train_lat], axis=1)
    sample_out = pd.concat([sample_base.reset_index(drop=True), sample_lat], axis=1)
    out = pd.concat([train_out, sample_out], ignore_index=True)
    out.to_parquet(path, index=False)
    pd.DataFrame({"column": [f"z_{i:03d}" for i in range(len(names))], "source": names}).to_csv(path.with_name("latent_manifest.csv"), index=False)


def add_time_metadata(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    lifelog = pd.to_datetime(out["lifelog_date"])
    out["weekday"] = lifelog.dt.dayofweek.astype(int)
    out["is_weekend"] = out["weekday"].isin([5, 6]).astype(int)
    first = out.groupby("subject_id")["lifelog_date"].transform("min")
    out["day_index_subject"] = (pd.to_datetime(out["lifelog_date"]) - pd.to_datetime(first)).dt.days.astype(int)
    return out


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build fold-safe label-supervised tabular encoder latents from all engineered day features.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--summary-path", default="outputs/encoder_day_pyramid/day_summary_features.parquet")
    parser.add_argument("--master-path", default="artifacts/10_master_daily.parquet")
    parser.add_argument("--ssl-latent-path", default="outputs/encoder_day_pyramid_ssl_v1/day_latents.parquet")
    parser.add_argument("--teacher-oof", default="")
    parser.add_argument("--teacher-submission", default="")
    parser.add_argument("--output-dir", default="outputs/label_supervised_tabular_encoder_v1")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--prior-alpha", type=float, default=10.0)
    parser.add_argument("--pls-components", type=int, default=16)
    parser.add_argument("--pca-components", type=int, default=16)
    parser.add_argument("--min-feature-std", type=float, default=1e-6)
    parser.add_argument("--target-modes", default="label,label_prob_residual,label_logit_residual,teacher_logit_residual")
    parser.add_argument("--seed", type=int, default=2026)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    tables = [
        load_feature_table(Path(args.summary_path), "pyr"),
        load_feature_table(Path(args.master_path), "master"),
        load_latents(Path(args.ssl_latent_path), "ssl"),
    ]
    train_features, sample_features, feature_cols = join_features(train, sample, tables)
    teacher_train, teacher_sample = load_teacher_predictions(args.teacher_oof, args.teacher_submission, train, sample)
    train_latents, sample_latents, fold_rows, latent_names = fold_latents(
        train_features,
        sample_features,
        feature_cols,
        train,
        sample,
        teacher_train,
        teacher_sample,
        args,
    )
    latent_path = output_dir / "day_latents_oof_train_full_test.parquet"
    write_latent_table(latent_path, train, sample, train_latents, sample_latents, latent_names)
    report = {
        "rows": {"train": int(len(train)), "sample": int(len(sample))},
        "raw_features": int(len(feature_cols)),
        "latent_dim": int(train_latents.shape[1]),
        "folds": fold_rows,
        "latent_path": str(latent_path),
        "args": vars(args),
    }
    (output_dir / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    (output_dir / "report.md").write_text(
        "\n".join(
            [
                "# Label-supervised tabular encoder",
                "",
                f"- raw features: `{len(feature_cols)}`",
                f"- latent dim: `{train_latents.shape[1]}`",
                f"- latent path: `{latent_path}`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
