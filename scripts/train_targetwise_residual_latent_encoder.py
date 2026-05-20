from __future__ import annotations

import argparse
import json
import warnings
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cross_decomposition import PLSRegression
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import log_loss
from sklearn.preprocessing import StandardScaler


warnings.filterwarnings("ignore", category=RuntimeWarning, module="sklearn")


KEY_COLUMNS = ["subject_id", "sleep_date", "lifelog_date"]
TARGET_COLUMNS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
EPS = 1e-5


@dataclass(frozen=True)
class ResidualSpec:
    name: str
    alpha: float
    scale: float
    max_delta: float
    target_mode: str
    encoder: str
    components: int


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


def average_log_loss(y_true: pd.DataFrame, pred: np.ndarray) -> tuple[float, dict[str, float]]:
    pred = np.clip(pred, EPS, 1.0 - EPS)
    per_target = {
        target: float(log_loss(y_true[target].to_numpy(), pred[:, i], labels=[0, 1]))
        for i, target in enumerate(TARGET_COLUMNS)
    }
    return float(np.mean(list(per_target.values()))), per_target


def prediction_matrix(oof: pd.DataFrame) -> np.ndarray:
    return np.clip(np.column_stack([oof[f"pred_{target}"].to_numpy(float) for target in TARGET_COLUMNS]), EPS, 1.0 - EPS)


def submission_matrix(submission: pd.DataFrame) -> np.ndarray:
    return np.clip(submission[TARGET_COLUMNS].to_numpy(float), EPS, 1.0 - EPS)


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
    return df[KEY_COLUMNS + cols].rename(columns={col: f"{prefix}__{col}" for col in cols})


def load_latent_table(path: Path, prefix: str) -> pd.DataFrame:
    df = normalize_keys(pd.read_parquet(path))
    assert_unique_keys(df, str(path))
    cols = sorted(col for col in df.columns if col.startswith("z_"))
    if not cols:
        return df[KEY_COLUMNS].copy()
    return df[KEY_COLUMNS + cols].rename(columns={col: f"{prefix}__{col}" for col in cols})


def join_feature_tables(base: pd.DataFrame, tables: list[pd.DataFrame]) -> tuple[pd.DataFrame, list[str]]:
    out = base[KEY_COLUMNS].copy()
    for table in tables:
        cols = [col for col in table.columns if col not in KEY_COLUMNS]
        out = out.merge(table, on=KEY_COLUMNS, how="left", validate="one_to_one")
        if cols and out[cols].isna().all(axis=1).any():
            raise ValueError("Some rows failed feature join")
    feature_cols = [col for col in out.columns if col not in KEY_COLUMNS]
    return out, feature_cols


def make_subject_time_folds(train_df: pd.DataFrame, n_folds: int) -> list[tuple[np.ndarray, np.ndarray]]:
    ordered = train_df.reset_index(names="_idx").sort_values(["subject_id", "lifelog_date", "sleep_date"])
    val_indices: list[list[int]] = [[] for _ in range(n_folds)]
    for _, group in ordered.groupby("subject_id", sort=False):
        chunks = np.array_split(group["_idx"].to_numpy(), n_folds)
        for fold, chunk in enumerate(chunks):
            val_indices[fold].extend(chunk.tolist())
    all_idx = np.arange(len(train_df), dtype=int)
    folds = []
    for indices in val_indices:
        val_idx = np.array(sorted(indices), dtype=int)
        train_idx = np.setdiff1d(all_idx, val_idx, assume_unique=False)
        folds.append((train_idx, val_idx))
    return folds


def parse_float_list(value: str) -> list[float]:
    return [float(part) for part in value.split(",") if part.strip()]


def parse_int_list(value: str) -> list[int]:
    return [int(part) for part in value.split(",") if part.strip()]


def make_specs(args: argparse.Namespace) -> list[ResidualSpec]:
    specs = []
    for encoder in [part.strip() for part in args.encoders.split(",") if part.strip()]:
        for target_mode in [part.strip() for part in args.target_modes.split(",") if part.strip()]:
            for components in parse_int_list(args.components):
                for alpha in parse_float_list(args.alphas):
                    for scale in parse_float_list(args.scales):
                        for max_delta in parse_float_list(args.max_deltas):
                            name = f"{encoder}_{target_mode}_c{components}_a{alpha:g}_s{scale:g}_d{max_delta:g}"
                            specs.append(ResidualSpec(name, alpha, scale, max_delta, target_mode, encoder, components))
    return specs


def preprocess_fit(x: np.ndarray, min_std: float) -> tuple[SimpleImputer, StandardScaler, np.ndarray, np.ndarray]:
    imputer = SimpleImputer(strategy="median", keep_empty_features=True)
    scaler = StandardScaler()
    x_imp = imputer.fit_transform(x)
    x_scaled = scaler.fit_transform(x_imp)
    std = np.nanstd(x_scaled, axis=0)
    keep = np.where(std > min_std)[0]
    if keep.size == 0:
        raise ValueError("No non-constant features")
    x_kept = np.nan_to_num(x_scaled[:, keep], nan=0.0, posinf=0.0, neginf=0.0)
    return imputer, scaler, keep, np.clip(x_kept, -8.0, 8.0).astype(np.float32)


def preprocess_apply(x: np.ndarray, imputer: SimpleImputer, scaler: StandardScaler, keep: np.ndarray) -> np.ndarray:
    out = scaler.transform(imputer.transform(x))[:, keep]
    out = np.nan_to_num(out, nan=0.0, posinf=0.0, neginf=0.0)
    return np.clip(out, -8.0, 8.0).astype(np.float32)


def residual_target(y: np.ndarray, anchor: np.ndarray, mode: str) -> np.ndarray:
    if mode == "logit_hard":
        smooth = 0.04 + 0.92 * y.astype(float)
        return safe_logit(smooth) - safe_logit(anchor)
    if mode == "prob":
        return y.astype(float) - anchor
    if mode == "logit_soft":
        smooth = 0.10 + 0.80 * y.astype(float)
        return safe_logit(smooth) - safe_logit(anchor)
    raise ValueError(f"Unknown target mode: {mode}")


def fit_encoder(
    x_fit: np.ndarray,
    y_fit: np.ndarray,
    x_eval: np.ndarray,
    encoder: str,
    components: int,
    seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    n_components = min(components, x_fit.shape[0] - 1, x_fit.shape[1])
    def clean(values: np.ndarray) -> np.ndarray:
        values = np.nan_to_num(values, nan=0.0, posinf=0.0, neginf=0.0)
        return np.clip(values, -8.0, 8.0).astype(np.float32)

    if encoder == "none" or n_components <= 0:
        return clean(x_fit), clean(x_eval)
    if encoder == "pls":
        model = PLSRegression(n_components=n_components, scale=False, max_iter=1000)
        model.fit(x_fit, y_fit.reshape(-1, 1))
        return clean(model.transform(x_fit)), clean(model.transform(x_eval))
    if encoder == "pca":
        model = PCA(n_components=n_components, random_state=seed, svd_solver="full")
        model.fit(x_fit)
        return clean(model.transform(x_fit)), clean(model.transform(x_eval))
    raise ValueError(f"Unknown encoder: {encoder}")


def fit_predict_residual(
    x_fit_raw: np.ndarray,
    x_eval_raw: np.ndarray,
    y_fit: np.ndarray,
    anchor_fit: np.ndarray,
    spec: ResidualSpec,
    args: argparse.Namespace,
) -> np.ndarray:
    target = residual_target(y_fit, anchor_fit, spec.target_mode)
    x_fit, x_eval = fit_encoder(x_fit_raw, target, x_eval_raw, spec.encoder, spec.components, args.seed)
    model = Ridge(alpha=spec.alpha, solver="svd")
    model.fit(x_fit, target)
    delta = model.predict(x_eval)
    return np.clip(delta, -spec.max_delta, spec.max_delta)


def evaluate_specs(
    train: pd.DataFrame,
    sample: pd.DataFrame,
    train_features: pd.DataFrame,
    sample_features: pd.DataFrame,
    feature_cols: list[str],
    anchor_oof: np.ndarray,
    anchor_submission: np.ndarray,
    specs: list[ResidualSpec],
    args: argparse.Namespace,
) -> tuple[pd.DataFrame, dict[str, np.ndarray], dict[str, np.ndarray]]:
    x_train_all = train_features[feature_cols].replace([np.inf, -np.inf], np.nan).to_numpy(np.float32)
    x_sample_all = sample_features[feature_cols].replace([np.inf, -np.inf], np.nan).to_numpy(np.float32)
    y_all = train[TARGET_COLUMNS].to_numpy(float)
    folds = make_subject_time_folds(train, args.folds)
    oof_by_spec = {spec.name: anchor_oof.copy() for spec in specs}
    sub_by_spec = {}

    for fold_id, (fit_idx, val_idx) in enumerate(folds, start=1):
        imputer, scaler, keep, x_fit = preprocess_fit(x_train_all[fit_idx], args.min_feature_std)
        x_val = preprocess_apply(x_train_all[val_idx], imputer, scaler, keep)
        for spec in specs:
            pred = oof_by_spec[spec.name].copy()
            for target_i in range(len(TARGET_COLUMNS)):
                delta = fit_predict_residual(
                    x_fit,
                    x_val,
                    y_all[fit_idx, target_i],
                    anchor_oof[fit_idx, target_i],
                    spec,
                    args,
                )
                if spec.target_mode == "prob":
                    pred[val_idx, target_i] = np.clip(anchor_oof[val_idx, target_i] + spec.scale * delta, EPS, 1.0 - EPS)
                else:
                    pred[val_idx, target_i] = sigmoid(safe_logit(anchor_oof[val_idx, target_i]) + spec.scale * delta)
            oof_by_spec[spec.name][val_idx] = pred[val_idx]
        print(f"fold={fold_id} complete kept_features={len(keep)}")

    rows = []
    anchor_score, anchor_per_target = average_log_loss(train, anchor_oof)
    rows.append(
        {
            "name": "anchor_noop",
            "encoder": "anchor",
            "target_mode": "noop",
            "components": 0,
            "alpha": 0.0,
            "scale": 0.0,
            "max_delta": 0.0,
            "avg_log_loss": anchor_score,
            **anchor_per_target,
        }
    )
    oof_by_spec["anchor_noop"] = anchor_oof.copy()
    for spec in specs:
        score, per_target = average_log_loss(train, oof_by_spec[spec.name])
        rows.append(
            {
                "name": spec.name,
                "encoder": spec.encoder,
                "target_mode": spec.target_mode,
                "components": spec.components,
                "alpha": spec.alpha,
                "scale": spec.scale,
                "max_delta": spec.max_delta,
                "avg_log_loss": score,
                **per_target,
            }
        )
    scores = pd.DataFrame(rows).sort_values("avg_log_loss", ascending=True).reset_index(drop=True)

    targetwise_names = [str(scores.sort_values(target).iloc[0]["name"]) for target in TARGET_COLUMNS]
    top_names = list(dict.fromkeys([*scores.head(args.full_fit_top_k)["name"].tolist(), *targetwise_names]))
    if "anchor_noop" in top_names:
        sub_by_spec["anchor_noop"] = anchor_submission.copy()
    imputer, scaler, keep, x_fit_full = preprocess_fit(x_train_all, args.min_feature_std)
    x_sample = preprocess_apply(x_sample_all, imputer, scaler, keep)
    spec_by_name = {spec.name: spec for spec in specs}
    for name in top_names:
        if name == "anchor_noop":
            continue
        spec = spec_by_name[name]
        pred = anchor_submission.copy()
        for target_i in range(len(TARGET_COLUMNS)):
            delta = fit_predict_residual(
                x_fit_full,
                x_sample,
                y_all[:, target_i],
                anchor_oof[:, target_i],
                spec,
                args,
            )
            if spec.target_mode == "prob":
                pred[:, target_i] = np.clip(anchor_submission[:, target_i] + spec.scale * delta, EPS, 1.0 - EPS)
            else:
                pred[:, target_i] = sigmoid(safe_logit(anchor_submission[:, target_i]) + spec.scale * delta)
        sub_by_spec[name] = np.clip(pred, EPS, 1.0 - EPS)
    return scores, oof_by_spec, sub_by_spec


def write_prediction_csvs(
    output_dir: Path,
    train: pd.DataFrame,
    sample: pd.DataFrame,
    scores: pd.DataFrame,
    oof_by_spec: dict[str, np.ndarray],
    sub_by_spec: dict[str, np.ndarray],
    args: argparse.Namespace,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    scores.to_csv(output_dir / "candidate_scores.csv", index=False)
    for rank, row in scores.head(args.full_fit_top_k).iterrows():
        name = str(row["name"])
        safe = name.replace(".", "p").replace("-", "m")
        oof_pred = oof_by_spec[name]
        oof = train[KEY_COLUMNS + TARGET_COLUMNS].copy()
        for i, target in enumerate(TARGET_COLUMNS):
            oof[f"pred_{target}"] = oof_pred[:, i]
        oof.to_csv(output_dir / f"oof_rank{rank + 1:02d}_{safe}.csv", index=False)
        if name in sub_by_spec:
            submission = sample[KEY_COLUMNS].copy()
            for i, target in enumerate(TARGET_COLUMNS):
                submission[target] = sub_by_spec[name][:, i]
            submission.to_csv(output_dir / f"submission_rank{rank + 1:02d}_{safe}.csv", index=False)

    selected_rows = []
    targetwise_oof = np.zeros((len(train), len(TARGET_COLUMNS)), dtype=float)
    targetwise_sub = np.zeros((len(sample), len(TARGET_COLUMNS)), dtype=float)
    for target_i, target in enumerate(TARGET_COLUMNS):
        selected = scores.sort_values(target).iloc[0].to_dict()
        name = str(selected["name"])
        selected_rows.append({"target": target, **selected})
        targetwise_oof[:, target_i] = oof_by_spec[name][:, target_i]
        if name not in sub_by_spec:
            raise ValueError(f"Missing full-fit submission for targetwise selected spec: {name}")
        targetwise_sub[:, target_i] = sub_by_spec[name][:, target_i]
    targetwise_score, targetwise_per_target = average_log_loss(train, targetwise_oof)
    selected_df = pd.DataFrame(selected_rows)
    selected_df["targetwise_avg_log_loss"] = targetwise_score
    selected_df.to_csv(output_dir / "targetwise_selection.csv", index=False)
    oof_targetwise = train[KEY_COLUMNS + TARGET_COLUMNS].copy()
    sub_targetwise = sample[KEY_COLUMNS].copy()
    for i, target in enumerate(TARGET_COLUMNS):
        oof_targetwise[f"pred_{target}"] = targetwise_oof[:, i]
        sub_targetwise[target] = targetwise_sub[:, i]
    oof_targetwise.to_csv(output_dir / "oof_targetwise_residual_latent_encoder.csv", index=False)
    sub_targetwise.to_csv(output_dir / "submission_targetwise_residual_latent_encoder.csv", index=False)
    pd.DataFrame([{"name": "targetwise_best", "avg_log_loss": targetwise_score, **targetwise_per_target}]).to_csv(
        output_dir / "targetwise_score.csv", index=False
    )
    report = {
        "best": scores.iloc[0].to_dict(),
        "targetwise": {
            "avg_log_loss": targetwise_score,
            "per_target": targetwise_per_target,
            "selected": selected_rows,
        },
        "top_candidates": scores.head(20).to_dict(orient="records"),
        "args": vars(args),
    }
    (output_dir / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    top_md = dataframe_to_markdown(scores.head(10)[["name", "avg_log_loss", *TARGET_COLUMNS]])
    lines = [
        "# Target-wise residual latent encoder",
        "",
        f"- Best candidate: `{scores.iloc[0]['name']}`",
        f"- Best OOF: `{scores.iloc[0]['avg_log_loss']:.6f}`",
        f"- Target-wise OOF: `{targetwise_score:.6f}`",
        "",
        "## Top candidates",
        "",
        top_md,
        "",
        "## Target-wise selection",
        "",
        dataframe_to_markdown(selected_df[["target", "name", "avg_log_loss", *TARGET_COLUMNS]]),
    ]
    (output_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train target-wise residual specialist encoders on top of a strong anchor prediction.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--anchor-oof", default="outputs/lb_feedback_recovery_uploads/oof_15_v18_old15_prob_blend.csv")
    parser.add_argument("--anchor-submission", default="outputs/lb_feedback_recovery_uploads/submission_15_v18_old15_prob_blend.csv")
    parser.add_argument("--summary-path", default="outputs/encoder_day_pyramid/day_summary_features.parquet")
    parser.add_argument("--master-path", default="artifacts/10_master_daily.parquet")
    parser.add_argument("--ssl-latent-path", default="outputs/encoder_day_pyramid_ssl_v1/day_latents.parquet")
    parser.add_argument("--label-latent-path", default="outputs/label_supervised_tabular_encoder_v1/day_latents_oof_train_full_test.parquet")
    parser.add_argument("--output-dir", default="outputs/targetwise_residual_latent_encoder_v1")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--encoders", default="pls,pca")
    parser.add_argument("--target-modes", default="logit_soft,prob")
    parser.add_argument("--components", default="4,8,16")
    parser.add_argument("--alphas", default="10,30,100,300,1000")
    parser.add_argument("--scales", default="0.03,0.05,0.08,0.1,0.15,0.2,0.3")
    parser.add_argument("--max-deltas", default="0.15,0.25,0.4,0.7")
    parser.add_argument("--min-feature-std", type=float, default=1e-6)
    parser.add_argument("--full-fit-top-k", type=int, default=10)
    parser.add_argument("--seed", type=int, default=2026)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    anchor_oof_frame = normalize_keys(pd.read_csv(args.anchor_oof))
    anchor_submission_frame = normalize_keys(pd.read_csv(args.anchor_submission))
    if not anchor_oof_frame[KEY_COLUMNS].equals(train[KEY_COLUMNS]):
        raise ValueError("Anchor OOF key mismatch")
    if not anchor_submission_frame[KEY_COLUMNS].equals(sample[KEY_COLUMNS]):
        raise ValueError("Anchor submission key mismatch")
    anchor_oof = prediction_matrix(anchor_oof_frame)
    anchor_submission = submission_matrix(anchor_submission_frame)
    tables = [
        load_feature_table(Path(args.summary_path), "pyr"),
        load_feature_table(Path(args.master_path), "master"),
        load_latent_table(Path(args.ssl_latent_path), "ssl"),
    ]
    if args.label_latent_path and Path(args.label_latent_path).exists():
        tables.append(load_latent_table(Path(args.label_latent_path), "label_latent"))
    train_features, feature_cols = join_feature_tables(train, tables)
    sample_features, _ = join_feature_tables(sample, tables)
    specs = make_specs(args)
    scores, oof_by_spec, sub_by_spec = evaluate_specs(
        train=train,
        sample=sample,
        train_features=train_features,
        sample_features=sample_features,
        feature_cols=feature_cols,
        anchor_oof=anchor_oof,
        anchor_submission=anchor_submission,
        specs=specs,
        args=args,
    )
    write_prediction_csvs(output_dir, train, sample, scores, oof_by_spec, sub_by_spec, args)
    print(f"best={scores.iloc[0]['name']} avg_log_loss={scores.iloc[0]['avg_log_loss']:.6f}")
    print(f"saved report: {output_dir / 'report.md'}")


if __name__ == "__main__":
    main()
