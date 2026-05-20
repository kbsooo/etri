from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler


KEY_COLUMNS = ["subject_id", "sleep_date", "lifelog_date"]
TARGET_COLUMNS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
EPS = 1e-5


@dataclass(frozen=True)
class LogRegSpec:
    name: str
    feature_set: str
    c_value: float


def average_log_loss(y_true: pd.DataFrame, pred: np.ndarray) -> tuple[float, dict[str, float]]:
    clipped = np.clip(pred, EPS, 1.0 - EPS)
    per_target = {
        target: float(log_loss(y_true[target].to_numpy(), clipped[:, i], labels=[0, 1]))
        for i, target in enumerate(TARGET_COLUMNS)
    }
    return float(np.mean(list(per_target.values()))), per_target


def assert_unique_keys(df: pd.DataFrame, name: str) -> None:
    dupes = df.duplicated(KEY_COLUMNS).sum()
    if dupes:
        raise ValueError(f"{name} has {dupes} duplicated key rows")


def normalize_key_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in KEY_COLUMNS:
        out[col] = out[col].astype(str)
    return out


def load_joined_frames(
    latent_path: Path,
    train_path: Path,
    sample_path: Path,
    extra_feature_path: Path | None,
) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    latents = normalize_key_columns(pd.read_parquet(latent_path))
    train = normalize_key_columns(pd.read_csv(train_path))
    sample = normalize_key_columns(pd.read_csv(sample_path))
    for name, df in [("latents", latents), ("train", train), ("sample", sample)]:
        missing = sorted(set(KEY_COLUMNS) - set(df.columns))
        if missing:
            raise ValueError(f"{name} is missing key columns: {missing}")
        assert_unique_keys(df, name)

    z_cols = sorted(col for col in latents.columns if col.startswith("z_"))
    if not z_cols:
        raise ValueError(f"No latent columns found in {latent_path}")

    latent_feature_cols = KEY_COLUMNS + ["weekday", "is_weekend", "day_index_subject"] + z_cols
    missing_feature_cols = sorted(set(latent_feature_cols) - set(latents.columns))
    if missing_feature_cols:
        raise ValueError(f"Latent table is missing feature columns: {missing_feature_cols}")

    latent_features = latents[latent_feature_cols].copy()
    train_joined = train.merge(latent_features, on=KEY_COLUMNS, how="left", validate="one_to_one")
    test_joined = sample[KEY_COLUMNS].merge(latent_features, on=KEY_COLUMNS, how="left", validate="one_to_one")
    if train_joined[z_cols].isna().any().any():
        raise ValueError("Some train rows failed to join with latent features")
    if test_joined[z_cols].isna().any().any():
        raise ValueError("Some test rows failed to join with latent features")
    extra_cols: list[str] = []
    if extra_feature_path is not None and extra_feature_path.exists():
        extra = normalize_key_columns(pd.read_parquet(extra_feature_path))
        assert_unique_keys(extra, "extra_features")
        numeric_cols = [
            col
            for col in extra.columns
            if col not in KEY_COLUMNS + TARGET_COLUMNS + ["split", "dow", "is_weekend", "subject_ord", "day_index_subject"]
            and pd.api.types.is_numeric_dtype(extra[col])
        ]
        extra_cols = [f"agg__{col}" for col in numeric_cols]
        extra_features = extra[KEY_COLUMNS + numeric_cols].rename(columns=dict(zip(numeric_cols, extra_cols)))
        train_joined = train_joined.merge(extra_features, on=KEY_COLUMNS, how="left", validate="one_to_one")
        test_joined = test_joined.merge(extra_features, on=KEY_COLUMNS, how="left", validate="one_to_one")
        if train_joined[extra_cols].isna().all(axis=1).any():
            raise ValueError("Some train rows failed to join with extra aggregate features")
        if test_joined[extra_cols].isna().all(axis=1).any():
            raise ValueError("Some test rows failed to join with extra aggregate features")
    return train_joined, test_joined, extra_cols


def add_engineered_features(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    extra_cols: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, list[str]]]:
    all_df = pd.concat(
        [
            train_df.assign(_split="train", _row=np.arange(len(train_df))),
            test_df.assign(_split="test", _row=np.arange(len(test_df))),
        ],
        axis=0,
        ignore_index=True,
    )
    z_cols = sorted(col for col in all_df.columns if col.startswith("z_"))
    subject_means = all_df.groupby("subject_id")[z_cols].transform("mean")
    z_dev_cols = [f"{col}_dev" for col in z_cols]
    z_dev_df = all_df[z_cols].sub(subject_means).set_axis(z_dev_cols, axis=1)

    all_df["weekday_sin"] = np.sin(2.0 * np.pi * all_df["weekday"].astype(float) / 7.0)
    all_df["weekday_cos"] = np.cos(2.0 * np.pi * all_df["weekday"].astype(float) / 7.0)
    max_day = all_df.groupby("subject_id")["day_index_subject"].transform("max").replace(0, 1)
    all_df["day_position"] = all_df["day_index_subject"].astype(float) / max_day.astype(float)

    subject_dummy_df = pd.get_dummies(all_df["subject_id"], prefix="subject", dtype=float)
    subject_dummy_df = subject_dummy_df.reindex(sorted(subject_dummy_df.columns), axis=1)
    subject_cols = subject_dummy_df.columns.tolist()
    all_df = pd.concat([all_df, z_dev_df, subject_dummy_df], axis=1).copy()

    time_cols = ["weekday_sin", "weekday_cos", "is_weekend", "day_index_subject", "day_position"]
    feature_sets = {
        "latent": z_cols,
        "latent_dev": z_cols + z_dev_cols,
        "latent_meta": z_cols + z_dev_cols + time_cols + subject_cols,
        "meta_only": time_cols + subject_cols,
    }
    if extra_cols:
        feature_sets.update(
            {
                "agg": extra_cols,
                "latent_agg": z_cols + extra_cols,
                "latent_meta_agg": z_cols + z_dev_cols + time_cols + subject_cols + extra_cols,
            }
        )

    train_out = all_df[all_df["_split"] == "train"].sort_values("_row").drop(columns=["_split", "_row"]).reset_index(drop=True)
    test_out = all_df[all_df["_split"] == "test"].sort_values("_row").drop(columns=["_split", "_row"]).reset_index(drop=True)
    return train_out, test_out, feature_sets


def make_subject_time_folds(train_df: pd.DataFrame, n_folds: int) -> list[tuple[np.ndarray, np.ndarray]]:
    if n_folds < 2:
        raise ValueError("--folds must be at least 2")
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


def predict_constant(train_y: pd.DataFrame, rows: int) -> np.ndarray:
    means = train_y[TARGET_COLUMNS].mean().clip(EPS, 1.0 - EPS).to_numpy(dtype=float)
    return np.tile(means, (rows, 1))


def subject_prior_predictions(
    train_part: pd.DataFrame,
    eval_part: pd.DataFrame,
    alpha: float,
) -> np.ndarray:
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


def oof_global_prior(train_df: pd.DataFrame, folds: list[tuple[np.ndarray, np.ndarray]]) -> np.ndarray:
    pred = np.zeros((len(train_df), len(TARGET_COLUMNS)), dtype=float)
    for train_idx, val_idx in folds:
        pred[val_idx] = predict_constant(train_df.iloc[train_idx], len(val_idx))
    return pred


def fit_target_logreg(x_train: np.ndarray, y_train: np.ndarray, c_value: float) -> LogisticRegression | float:
    classes = np.unique(y_train)
    if len(classes) < 2:
        return float(classes[0])
    model = LogisticRegression(C=c_value, solver="lbfgs", max_iter=5000)
    model.fit(x_train, y_train)
    return model


def model_predict_proba(model: LogisticRegression | float, x_eval: np.ndarray) -> np.ndarray:
    if isinstance(model, float):
        return np.full(x_eval.shape[0], model, dtype=float)
    return model.predict_proba(x_eval)[:, 1]


def oof_logreg(
    train_df: pd.DataFrame,
    feature_cols: list[str],
    folds: list[tuple[np.ndarray, np.ndarray]],
    c_value: float,
) -> np.ndarray:
    pred = np.zeros((len(train_df), len(TARGET_COLUMNS)), dtype=float)
    x_all = train_df[feature_cols].to_numpy(dtype=np.float32).copy()
    x_all[~np.isfinite(x_all)] = np.nan
    y_all = train_df[TARGET_COLUMNS].astype(int).reset_index(drop=True)
    for train_idx, val_idx in folds:
        imputer = SimpleImputer(strategy="median", keep_empty_features=True)
        scaler = StandardScaler()
        x_train = imputer.fit_transform(x_all[train_idx])
        x_val = imputer.transform(x_all[val_idx])
        x_train = scaler.fit_transform(x_train)
        x_val = scaler.transform(x_val)
        for target_i, target in enumerate(TARGET_COLUMNS):
            model = fit_target_logreg(x_train, y_all.loc[train_idx, target].to_numpy(), c_value)
            pred[val_idx, target_i] = model_predict_proba(model, x_val)
    return np.clip(pred, EPS, 1.0 - EPS)


def fit_full_logreg_predict(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    feature_cols: list[str],
    c_value: float,
) -> np.ndarray:
    x_train = train_df[feature_cols].to_numpy(dtype=np.float32).copy()
    x_test = test_df[feature_cols].to_numpy(dtype=np.float32).copy()
    x_train[~np.isfinite(x_train)] = np.nan
    x_test[~np.isfinite(x_test)] = np.nan
    imputer = SimpleImputer(strategy="median", keep_empty_features=True)
    scaler = StandardScaler()
    x_train_imputed = imputer.fit_transform(x_train)
    x_test_imputed = imputer.transform(x_test)
    x_train_scaled = scaler.fit_transform(x_train_imputed)
    x_test_scaled = scaler.transform(x_test_imputed)
    pred = np.zeros((len(test_df), len(TARGET_COLUMNS)), dtype=float)
    for target_i, target in enumerate(TARGET_COLUMNS):
        model = fit_target_logreg(x_train_scaled, train_df[target].astype(int).to_numpy(), c_value)
        pred[:, target_i] = model_predict_proba(model, x_test_scaled)
    return np.clip(pred, EPS, 1.0 - EPS)


def evaluate_candidates(
    train_df: pd.DataFrame,
    feature_sets: dict[str, list[str]],
    folds: list[tuple[np.ndarray, np.ndarray]],
    c_values: list[float],
    prior_alphas: list[float],
    blend_weights: list[float],
) -> tuple[pd.DataFrame, dict[str, np.ndarray], dict]:
    y_true = train_df[TARGET_COLUMNS]
    oof_predictions: dict[str, np.ndarray] = {}
    rows = []

    global_pred = oof_global_prior(train_df, folds)
    oof_predictions["global_prior"] = global_pred
    score, per_target = average_log_loss(y_true, global_pred)
    rows.append({"name": "global_prior", "kind": "prior", "feature_set": "", "c_value": np.nan, "alpha": np.nan, "weight": np.nan, "avg_log_loss": score, **per_target})

    prior_names = []
    for alpha in prior_alphas:
        name = f"subject_prior_a{alpha:g}"
        prior_pred = oof_subject_prior(train_df, folds, alpha)
        oof_predictions[name] = prior_pred
        prior_names.append(name)
        score, per_target = average_log_loss(y_true, prior_pred)
        rows.append({"name": name, "kind": "prior", "feature_set": "", "c_value": np.nan, "alpha": alpha, "weight": np.nan, "avg_log_loss": score, **per_target})

    model_names = []
    for feature_set, feature_cols in feature_sets.items():
        for c_value in c_values:
            name = f"logreg_{feature_set}_C{c_value:g}"
            pred = oof_logreg(train_df, feature_cols, folds, c_value)
            oof_predictions[name] = pred
            model_names.append(name)
            score, per_target = average_log_loss(y_true, pred)
            rows.append({"name": name, "kind": "model", "feature_set": feature_set, "c_value": c_value, "alpha": np.nan, "weight": 1.0, "avg_log_loss": score, **per_target})

    for model_name in model_names:
        model_pred = oof_predictions[model_name]
        model_parts = model_name.split("_C")
        feature_set = model_parts[0].replace("logreg_", "")
        c_value = float(model_parts[1])
        for prior_name in prior_names:
            alpha = float(prior_name.split("_a")[1])
            prior_pred = oof_predictions[prior_name]
            for weight in blend_weights:
                blended = weight * model_pred + (1.0 - weight) * prior_pred
                score, per_target = average_log_loss(y_true, blended)
                name = f"blend_w{weight:g}_{model_name}_{prior_name}"
                rows.append({"name": name, "kind": "blend", "feature_set": feature_set, "c_value": c_value, "alpha": alpha, "weight": weight, "avg_log_loss": score, **per_target})

    scores = pd.DataFrame(rows).sort_values("avg_log_loss", ascending=True).reset_index(drop=True)
    best = scores.iloc[0].to_dict()
    return scores, oof_predictions, best


def build_submission(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    feature_sets: dict[str, list[str]],
    best: dict,
    sample_path: Path,
) -> tuple[pd.DataFrame, np.ndarray]:
    sample = pd.read_csv(sample_path)
    if best["kind"] == "prior":
        if best["name"] == "global_prior":
            test_pred = predict_constant(train_df, len(test_df))
        else:
            test_pred = subject_prior_predictions(train_df, test_df, float(best["alpha"]))
    elif best["kind"] == "model":
        test_pred = fit_full_logreg_predict(train_df, test_df, feature_sets[str(best["feature_set"])], float(best["c_value"]))
    elif best["kind"] == "blend":
        model_pred = fit_full_logreg_predict(train_df, test_df, feature_sets[str(best["feature_set"])], float(best["c_value"]))
        prior_pred = subject_prior_predictions(train_df, test_df, float(best["alpha"]))
        test_pred = float(best["weight"]) * model_pred + (1.0 - float(best["weight"])) * prior_pred
    else:
        raise ValueError(f"Unknown best candidate kind: {best['kind']}")

    test_pred = np.clip(test_pred, EPS, 1.0 - EPS)
    submission = sample.copy()
    for target_i, target in enumerate(TARGET_COLUMNS):
        submission[target] = test_pred[:, target_i]
    return submission, test_pred


def candidate_predictions(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    feature_sets: dict[str, list[str]],
    candidate: dict,
) -> np.ndarray:
    kind = candidate["kind"]
    if kind == "prior":
        if candidate["name"] == "global_prior":
            return predict_constant(train_df, len(test_df))
        return subject_prior_predictions(train_df, test_df, float(candidate["alpha"]))
    if kind == "model":
        return fit_full_logreg_predict(train_df, test_df, feature_sets[str(candidate["feature_set"])], float(candidate["c_value"]))
    if kind == "blend":
        model_pred = fit_full_logreg_predict(train_df, test_df, feature_sets[str(candidate["feature_set"])], float(candidate["c_value"]))
        prior_pred = subject_prior_predictions(train_df, test_df, float(candidate["alpha"]))
        return np.clip(float(candidate["weight"]) * model_pred + (1.0 - float(candidate["weight"])) * prior_pred, EPS, 1.0 - EPS)
    raise ValueError(f"Unknown candidate kind: {kind}")


def candidate_oof_predictions(candidate: dict, oof_predictions: dict[str, np.ndarray]) -> np.ndarray:
    kind = candidate["kind"]
    name = candidate["name"]
    if kind in {"prior", "model"}:
        return oof_predictions[name]
    if kind == "blend":
        model_name = f"logreg_{candidate['feature_set']}_C{float(candidate['c_value']):g}"
        prior_name = f"subject_prior_a{float(candidate['alpha']):g}"
        return np.clip(
            float(candidate["weight"]) * oof_predictions[model_name]
            + (1.0 - float(candidate["weight"])) * oof_predictions[prior_name],
            EPS,
            1.0 - EPS,
        )
    raise ValueError(f"Unknown candidate kind: {kind}")


def build_targetwise_outputs(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    scores: pd.DataFrame,
    oof_predictions: dict[str, np.ndarray],
    feature_sets: dict[str, list[str]],
    sample_path: Path,
    output_dir: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray, np.ndarray]:
    y_true = train_df[TARGET_COLUMNS]
    selected_rows = []
    oof_targetwise = np.zeros((len(train_df), len(TARGET_COLUMNS)), dtype=float)
    test_targetwise = np.zeros((len(test_df), len(TARGET_COLUMNS)), dtype=float)

    test_cache: dict[str, np.ndarray] = {}
    for target_i, target in enumerate(TARGET_COLUMNS):
        candidate = scores.sort_values(target).iloc[0].to_dict()
        selected_rows.append({"target": target, **candidate})
        oof_targetwise[:, target_i] = candidate_oof_predictions(candidate, oof_predictions)[:, target_i]
        if candidate["name"] not in test_cache:
            test_cache[candidate["name"]] = candidate_predictions(train_df, test_df, feature_sets, candidate)
        test_targetwise[:, target_i] = test_cache[candidate["name"]][:, target_i]

    oof_targetwise = np.clip(oof_targetwise, EPS, 1.0 - EPS)
    test_targetwise = np.clip(test_targetwise, EPS, 1.0 - EPS)
    score, per_target = average_log_loss(y_true, oof_targetwise)

    selected = pd.DataFrame(selected_rows)
    selected["targetwise_avg_log_loss"] = score
    selected.to_csv(output_dir / "targetwise_selection.csv", index=False)

    oof_df = train_df[KEY_COLUMNS + TARGET_COLUMNS].copy()
    for target_i, target in enumerate(TARGET_COLUMNS):
        oof_df[f"pred_{target}"] = oof_targetwise[:, target_i]
    oof_df.to_csv(output_dir / "oof_targetwise.csv", index=False)

    sample = pd.read_csv(sample_path)
    submission = sample.copy()
    for target_i, target in enumerate(TARGET_COLUMNS):
        submission[target] = test_targetwise[:, target_i]
    submission.to_csv(output_dir / "submission_latent_decoder_targetwise.csv", index=False)

    score_row = {"name": "targetwise_best", "kind": "targetwise", "avg_log_loss": score, **per_target}
    pd.DataFrame([score_row]).to_csv(output_dir / "targetwise_score.csv", index=False)
    return selected, oof_df, test_targetwise, np.array([[score]])


def write_report(
    output_dir: Path,
    train_df: pd.DataFrame,
    scores: pd.DataFrame,
    best: dict,
    targetwise_selection: pd.DataFrame,
    feature_sets: dict[str, list[str]],
    folds: list[tuple[np.ndarray, np.ndarray]],
    test_pred: np.ndarray,
    targetwise_pred: np.ndarray,
    args: argparse.Namespace,
) -> None:
    fold_sizes = [{"fold": i, "train_rows": int(len(tr)), "valid_rows": int(len(va))} for i, (tr, va) in enumerate(folds, start=1)]
    report = {
        "metric": "Average Log-Loss",
        "targets": TARGET_COLUMNS,
        "train_rows": int(len(train_df)),
        "test_rows": int(len(test_pred)),
        "folds": fold_sizes,
        "best": best,
        "targetwise": {
            "avg_log_loss": float(targetwise_selection["targetwise_avg_log_loss"].iloc[0]),
            "selected": targetwise_selection.to_dict(orient="records"),
        },
        "top_candidates": scores.head(20).to_dict(orient="records"),
        "feature_set_sizes": {name: len(cols) for name, cols in feature_sets.items()},
        "prediction_summary": {
            target: {
                "min": float(test_pred[:, i].min()),
                "mean": float(test_pred[:, i].mean()),
                "max": float(test_pred[:, i].max()),
            }
            for i, target in enumerate(TARGET_COLUMNS)
        },
        "targetwise_prediction_summary": {
            target: {
                "min": float(targetwise_pred[:, i].min()),
                "mean": float(targetwise_pred[:, i].mean()),
                "max": float(targetwise_pred[:, i].max()),
            }
            for i, target in enumerate(TARGET_COLUMNS)
        },
        "args": vars(args),
    }
    (output_dir / "decoder_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    top = scores.head(10)[["name", "kind", "avg_log_loss", *TARGET_COLUMNS]]
    fold_sizes_df = pd.DataFrame(fold_sizes)
    lines = [
        "# Latent decoder report",
        "",
        f"- Metric: Average Log-Loss",
        f"- Train rows: {len(train_df)}",
        f"- Test rows: {len(test_pred)}",
        f"- Best candidate: `{best['name']}`",
        f"- Best CV average log-loss: {best['avg_log_loss']:.6f}",
        f"- Target-wise CV average log-loss: {targetwise_selection['targetwise_avg_log_loss'].iloc[0]:.6f}",
        "",
        "## Top candidates",
        "",
        dataframe_to_markdown(top),
        "",
        "## Feature set sizes",
        "",
    ]
    for name, cols in feature_sets.items():
        lines.append(f"- {name}: {len(cols)}")
    targetwise_cols = ["target", "name", "kind", "avg_log_loss", *TARGET_COLUMNS]
    lines.extend(
        [
            "",
            "## Target-wise selection",
            "",
            dataframe_to_markdown(targetwise_selection[targetwise_cols]),
            "",
            "## Fold sizes",
            "",
            dataframe_to_markdown(fold_sizes_df),
            "",
        ]
    )
    (output_dir / "decoder_report.md").write_text("\n".join(lines), encoding="utf-8")


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


def parse_float_list(value: str) -> list[float]:
    return [float(part) for part in value.split(",") if part.strip()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train supervised decoders on diffusion day latents.")
    parser.add_argument("--latent-path", default="outputs/diffusion_encoder/day_latents.parquet")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--extra-feature-path", default="outputs/data_probe/all_subject_day_features.parquet")
    parser.add_argument("--output-dir", default="outputs/latent_decoder")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--c-values", default="0.03,0.1,0.3,1.0,3.0")
    parser.add_argument("--prior-alphas", default="2,5,10,20,50,100")
    parser.add_argument("--blend-weights", default="0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    extra_feature_path = Path(args.extra_feature_path) if args.extra_feature_path else None
    train_df, test_df, extra_cols = load_joined_frames(
        Path(args.latent_path),
        Path(args.train_path),
        Path(args.sample_path),
        extra_feature_path,
    )
    train_df, test_df, feature_sets = add_engineered_features(train_df, test_df, extra_cols)
    folds = make_subject_time_folds(train_df, args.folds)
    scores, oof_predictions, best = evaluate_candidates(
        train_df=train_df,
        feature_sets=feature_sets,
        folds=folds,
        c_values=parse_float_list(args.c_values),
        prior_alphas=parse_float_list(args.prior_alphas),
        blend_weights=parse_float_list(args.blend_weights),
    )
    scores.to_csv(output_dir / "candidate_scores.csv", index=False)

    best_oof = None
    if best["kind"] == "prior":
        best_oof = oof_predictions[best["name"]]
    elif best["kind"] == "model":
        best_oof = oof_predictions[best["name"]]
    elif best["kind"] == "blend":
        model_name = f"logreg_{best['feature_set']}_C{best['c_value']:g}"
        prior_name = f"subject_prior_a{best['alpha']:g}"
        best_oof = float(best["weight"]) * oof_predictions[model_name] + (1.0 - float(best["weight"])) * oof_predictions[prior_name]
    if best_oof is not None:
        oof_df = train_df[KEY_COLUMNS + TARGET_COLUMNS].copy()
        for target_i, target in enumerate(TARGET_COLUMNS):
            oof_df[f"pred_{target}"] = np.clip(best_oof[:, target_i], EPS, 1.0 - EPS)
        oof_df.to_csv(output_dir / "oof_best.csv", index=False)

    submission, test_pred = build_submission(train_df, test_df, feature_sets, best, Path(args.sample_path))
    submission.to_csv(output_dir / "submission_latent_decoder.csv", index=False)
    targetwise_selection, _, targetwise_pred, _ = build_targetwise_outputs(
        train_df=train_df,
        test_df=test_df,
        scores=scores,
        oof_predictions=oof_predictions,
        feature_sets=feature_sets,
        sample_path=Path(args.sample_path),
        output_dir=output_dir,
    )
    write_report(output_dir, train_df, scores, best, targetwise_selection, feature_sets, folds, test_pred, targetwise_pred, args)

    print(f"best={best['name']} avg_log_loss={best['avg_log_loss']:.6f}")
    print(f"saved scores: {output_dir / 'candidate_scores.csv'}")
    print(f"saved oof: {output_dir / 'oof_best.csv'}")
    print(f"saved submission: {output_dir / 'submission_latent_decoder.csv'}")
    print(f"saved targetwise submission: {output_dir / 'submission_latent_decoder_targetwise.csv'}")
    print(f"saved report: {output_dir / 'decoder_report.md'}")


if __name__ == "__main__":
    main()
