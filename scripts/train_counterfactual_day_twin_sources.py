from __future__ import annotations

import argparse
import json
import warnings
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from pandas.errors import PerformanceWarning
from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


KEY_COLUMNS = ["subject_id", "sleep_date", "lifelog_date"]
TARGET_COLUMNS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
EPS = 1e-5


GROUP_TOKENS = {
    "sleep": [
        "sleep",
        "tst",
        "sol_",
        "awak",
        "eff",
        "longest_block",
    ],
    "phone": [
        "screen",
        "usage",
        "app_",
        "prebed",
        "sns",
        "video",
        "messenger",
        "charging",
    ],
    "mobility": [
        "gps",
        "step",
        "pedo",
        "walk",
        "vehicle",
        "still",
        "home",
        "elsewhere",
        "outings",
        "distance",
        "speed",
        "mob_",
    ],
    "physiology": [
        "hr",
        "rmssd",
        "sdnn",
        "cal_",
    ],
    "light": [
        "light",
        "mlight",
        "wlight",
        "bright",
    ],
    "ambience": [
        "amb",
        "music",
        "speech",
        "silence",
    ],
    "connectivity": [
        "wifi",
        "ble",
        "core_hit",
        "novelty",
    ],
}


@dataclass(frozen=True)
class SourceSpec:
    name: str
    feature_prefixes: tuple[str, ...]
    c_value: float


def normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in KEY_COLUMNS:
        out[col] = out[col].astype(str)
    return out


def safe_logit(values: np.ndarray) -> np.ndarray:
    values = np.clip(values.astype(float), EPS, 1.0 - EPS)
    return np.log(values / (1.0 - values))


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(values, -50.0, 50.0)))


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
    all_idx = np.arange(len(frame), dtype=int)
    return [
        (np.setdiff1d(all_idx, np.array(sorted(indices), dtype=int)), np.array(sorted(indices), dtype=int))
        for indices in val_indices
    ]


def robust_scale_matrix(frame: pd.DataFrame, numeric_cols: list[str]) -> tuple[np.ndarray, dict[str, list[float]]]:
    raw = frame[numeric_cols].copy()
    lo = raw.quantile(0.01)
    hi = raw.quantile(0.99)
    raw = raw.clip(lo, hi, axis=1)
    imputer = SimpleImputer(strategy="median")
    imputed = imputer.fit_transform(raw)
    mean = imputed.mean(axis=0)
    std = imputed.std(axis=0)
    std[std < 1e-6] = 1.0
    x = ((imputed - mean) / std).astype(np.float32)
    return x, {
        "columns": numeric_cols,
        "clip_lo": lo.fillna(0).astype(float).tolist(),
        "clip_hi": hi.fillna(0).astype(float).tolist(),
    }


def subject_center(x: np.ndarray, subjects: np.ndarray) -> np.ndarray:
    out = x.copy()
    for subject in np.unique(subjects):
        idx = np.flatnonzero(subjects == subject)
        out[idx] = out[idx] - np.nanmedian(out[idx], axis=0)
    return out


def compact_context(x: np.ndarray, max_components: int) -> np.ndarray:
    x = np.nan_to_num(x.astype(np.float64), copy=False)
    if x.shape[1] <= max_components:
        return x.astype(np.float32)
    x_centered = x - x.mean(axis=0, keepdims=True)
    _, _, vt = np.linalg.svd(x_centered, full_matrices=False)
    return (x_centered @ vt[:max_components].T).astype(np.float32)


def add_panel_calendar(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame[KEY_COLUMNS].copy()
    ordered = out.reset_index(names="_idx").sort_values(["subject_id", "lifelog_date", "sleep_date"])
    ordered["panel_index"] = ordered.groupby("subject_id").cumcount().astype(float)
    denom = ordered.groupby("subject_id")["panel_index"].transform("max").replace(0.0, 1.0)
    ordered["panel_position"] = ordered["panel_index"] / denom
    restored = ordered.sort_values("_idx")
    out["panel_index"] = restored["panel_index"].to_numpy(float)
    out["panel_position"] = restored["panel_position"].to_numpy(float)
    dates = pd.to_datetime(out["lifelog_date"])
    dow = dates.dt.dayofweek.to_numpy(float)
    doy = dates.dt.dayofyear.to_numpy(float)
    out["dow_sin"] = np.sin(2 * np.pi * dow / 7)
    out["dow_cos"] = np.cos(2 * np.pi * dow / 7)
    out["doy_sin"] = np.sin(2 * np.pi * doy / 366)
    out["doy_cos"] = np.cos(2 * np.pi * doy / 366)
    out["is_weekend"] = np.isin(dow, [5.0, 6.0]).astype(float)
    return out


def add_weather_context(context: pd.DataFrame, weather_path: str) -> pd.DataFrame:
    path = Path(weather_path)
    if not path.exists():
        return context
    weather = pd.read_csv(path)
    if "date" not in weather.columns:
        return context
    weather["date"] = pd.to_datetime(weather["date"]).dt.strftime("%Y-%m-%d")
    keep = [
        col
        for col in weather.columns
        if col == "date"
        or (
            col.startswith("weather_kr_mean_")
            and any(token in col for token in ["temperature", "precipitation", "sunshine", "daylight", "wind"])
        )
        or (col.startswith("weather_kr_std_") and any(token in col for token in ["temperature", "precipitation"]))
    ]
    joined = context[["lifelog_date"]].rename(columns={"lifelog_date": "date"}).merge(
        weather[keep], on="date", how="left", validate="many_to_one"
    )
    for col in keep:
        if col == "date":
            continue
        context[f"ctx_{col}"] = joined[col].to_numpy(float)
    return context


def group_columns(numeric_cols: list[str]) -> dict[str, list[int]]:
    groups: dict[str, list[int]] = {name: [] for name in GROUP_TOKENS}
    used: set[int] = set()
    for i, col in enumerate(numeric_cols):
        lower = col.lower()
        for group, tokens in GROUP_TOKENS.items():
            if any(token in lower for token in tokens):
                groups[group].append(i)
                used.add(i)
                break
    groups["other"] = [i for i in range(len(numeric_cols)) if i not in used]
    return {name: indices for name, indices in groups.items() if indices}


def weighted_average(values: np.ndarray, distances: np.ndarray, indices: np.ndarray) -> np.ndarray:
    if len(indices) == 0:
        return np.zeros(values.shape[1], dtype=np.float32)
    selected_dist = distances[indices]
    weights = 1.0 / (selected_dist + 1e-3)
    weights = weights / weights.sum()
    return (values[indices] * weights[:, None]).sum(axis=0).astype(np.float32)


def nearest_indices(
    distances: np.ndarray,
    allowed: np.ndarray,
    k: int,
) -> np.ndarray:
    idx = np.flatnonzero(allowed)
    if len(idx) == 0:
        return idx
    if len(idx) <= k:
        return idx[np.argsort(distances[idx])]
    part = idx[np.argpartition(distances[idx], k)[:k]]
    return part[np.argsort(distances[part])]


def summarize_residuals(prefix: str, x: np.ndarray, pred: np.ndarray, groups: dict[str, list[int]]) -> pd.DataFrame:
    diff = x - pred
    abs_diff = np.abs(diff)
    out: dict[str, np.ndarray] = {}
    for group, indices in groups.items():
        gdiff = diff[:, indices]
        gabs = abs_diff[:, indices]
        out[f"{prefix}_{group}_mean_diff"] = gdiff.mean(axis=1)
        out[f"{prefix}_{group}_mean_abs"] = gabs.mean(axis=1)
        out[f"{prefix}_{group}_rms"] = np.sqrt((gdiff**2).mean(axis=1))
        out[f"{prefix}_{group}_max_abs"] = gabs.max(axis=1)
        out[f"{prefix}_{group}_q90_abs"] = np.quantile(gabs, 0.90, axis=1)
        out[f"{prefix}_{group}_pos_mean"] = np.maximum(gdiff, 0.0).mean(axis=1)
        out[f"{prefix}_{group}_neg_mean"] = np.minimum(gdiff, 0.0).mean(axis=1)
    global_abs = abs_diff.mean(axis=1)
    out[f"{prefix}_global_mean_abs"] = global_abs
    out[f"{prefix}_global_rms"] = np.sqrt((diff**2).mean(axis=1))
    out[f"{prefix}_global_max_abs"] = abs_diff.max(axis=1)
    return pd.DataFrame(out)


def build_knn_twin_features(
    x: np.ndarray,
    x_centered: np.ndarray,
    subjects: np.ndarray,
    groups: dict[str, list[int]],
    k_same: int,
    k_cross: int,
) -> pd.DataFrame:
    pred = np.zeros_like(x, dtype=np.float32)
    for group, indices in groups.items():
        mask = np.ones(x.shape[1], dtype=bool)
        mask[indices] = False
        context = compact_context(x_centered[:, mask], 32)
        dist = np.sqrt(((context[:, None, :] - context[None, :, :]) ** 2).sum(axis=2))
        np.fill_diagonal(dist, np.inf)
        group_values = x[:, indices]
        for row in range(len(x)):
            same_allowed = subjects == subjects[row]
            same_allowed[row] = False
            cross_allowed = subjects != subjects[row]
            same_idx = nearest_indices(dist[row], same_allowed, k_same)
            cross_idx = nearest_indices(dist[row], cross_allowed, k_cross)
            same_pred = weighted_average(group_values, dist[row], same_idx) if len(same_idx) else None
            cross_pred = weighted_average(group_values, dist[row], cross_idx) if len(cross_idx) else None
            if same_pred is not None and cross_pred is not None:
                group_pred = 0.65 * same_pred + 0.35 * cross_pred
            elif same_pred is not None:
                group_pred = same_pred
            elif cross_pred is not None:
                group_pred = cross_pred
            else:
                group_pred = np.zeros(len(indices), dtype=np.float32)
            pred[row, indices] = group_pred
    return summarize_residuals("knn", x, pred, groups)


def softmax_negative_distance(distances: np.ndarray) -> np.ndarray:
    tau = float(np.median(np.min(distances, axis=1)))
    if not np.isfinite(tau) or tau < 1e-3:
        tau = 1.0
    logits = -distances / tau
    logits = logits - logits.max(axis=1, keepdims=True)
    values = np.exp(logits)
    return values / values.sum(axis=1, keepdims=True)


def build_prototype_features(
    x_centered: np.ndarray,
    subjects: np.ndarray,
    context_meta: np.ndarray,
    groups: dict[str, list[int]],
    n_prototypes: int,
    k_context: int,
) -> pd.DataFrame:
    out: dict[str, np.ndarray] = {}
    meta = compact_context(context_meta, min(24, context_meta.shape[1]))
    meta_dist = np.sqrt(((meta[:, None, :] - meta[None, :, :]) ** 2).sum(axis=2))
    np.fill_diagonal(meta_dist, np.inf)
    for group, indices in groups.items():
        group_x = compact_context(x_centered[:, indices], min(16, len(indices)))
        k = min(n_prototypes, max(2, len(group_x) // 20))
        model = KMeans(n_clusters=k, random_state=2026, n_init=20)
        labels = model.fit_predict(group_x)
        distances = model.transform(group_x)
        weights = softmax_negative_distance(distances)
        expected = np.zeros_like(weights)
        for row in range(len(weights)):
            same = subjects == subjects[row]
            same[row] = False
            cross = subjects != subjects[row]
            same_idx = nearest_indices(meta_dist[row], same, max(2, k_context // 2))
            cross_idx = nearest_indices(meta_dist[row], cross, k_context)
            if len(same_idx) and len(cross_idx):
                expected[row] = 0.55 * weights[same_idx].mean(axis=0) + 0.45 * weights[cross_idx].mean(axis=0)
            elif len(same_idx):
                expected[row] = weights[same_idx].mean(axis=0)
            elif len(cross_idx):
                expected[row] = weights[cross_idx].mean(axis=0)
            else:
                expected[row] = 1.0 / k
        expected = np.clip(expected, 1e-6, 1.0)
        expected = expected / expected.sum(axis=1, keepdims=True)
        weights = np.clip(weights, 1e-6, 1.0)
        weights = weights / weights.sum(axis=1, keepdims=True)
        diff = weights - expected
        out[f"proto_{group}_kl"] = (weights * (np.log(weights) - np.log(expected))).sum(axis=1)
        out[f"proto_{group}_l1"] = np.abs(diff).sum(axis=1)
        out[f"proto_{group}_entropy"] = -(weights * np.log(weights)).sum(axis=1)
        out[f"proto_{group}_nearest_dist"] = distances.min(axis=1)
        out[f"proto_{group}_expected_nearest_weight"] = expected[np.arange(len(expected)), labels]
        for cluster in range(k):
            out[f"proto_{group}_w{cluster:02d}"] = weights[:, cluster]
            out[f"proto_{group}_wdiff{cluster:02d}"] = diff[:, cluster]
    return pd.DataFrame(out)


def build_dae_features(
    x: np.ndarray,
    groups: dict[str, list[int]],
    mask_rate: float,
    augmentations: int,
    max_iter: int,
) -> tuple[pd.DataFrame, dict[str, object]]:
    rng = np.random.default_rng(2026)
    copies = []
    targets = []
    group_values = list(groups.values())
    for _ in range(augmentations):
        masked = x.copy()
        feature_mask = rng.random(masked.shape) < mask_rate
        masked[feature_mask] = 0.0
        for row in range(len(masked)):
            if rng.random() < 0.40:
                group = group_values[int(rng.integers(0, len(group_values)))]
                masked[row, group] = 0.0
        copies.append(masked)
        targets.append(x)
    train_x = np.vstack(copies)
    train_y = np.vstack(targets)
    model = MLPRegressor(
        hidden_layer_sizes=(128, 48, 128),
        activation="relu",
        alpha=0.02,
        batch_size=128,
        learning_rate_init=0.001,
        max_iter=max_iter,
        early_stopping=True,
        validation_fraction=0.15,
        n_iter_no_change=20,
        random_state=2026,
        verbose=False,
    )
    model.fit(train_x, train_y)
    pred = np.zeros_like(x, dtype=np.float32)
    for _, indices in groups.items():
        masked = x.copy()
        masked[:, indices] = 0.0
        recon = model.predict(masked).astype(np.float32)
        pred[:, indices] = recon[:, indices]
    report = {
        "n_iter": int(getattr(model, "n_iter_", -1)),
        "loss": float(getattr(model, "loss_", np.nan)),
        "best_validation_score": float(getattr(model, "best_validation_score_", np.nan)),
        "augmentations": augmentations,
        "mask_rate": mask_rate,
    }
    return summarize_residuals("dae", x, pred, groups), report


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
        prob_col = f"base_{target}_prob"
        logit_col = f"base_{target}_logit"
        features_train[prob_col] = train_pred[:, i]
        features_test[prob_col] = test_pred[:, i]
        features_train[logit_col] = safe_logit(train_pred[:, i])
        features_test[logit_col] = safe_logit(test_pred[:, i])
        cols.extend([prob_col, logit_col])
    return features_train, features_test, cols


def train_source(
    spec: SourceSpec,
    features_train: pd.DataFrame,
    features_test: pd.DataFrame,
    labels: pd.DataFrame,
    folds: list[tuple[np.ndarray, np.ndarray]],
    output_dir: Path,
) -> dict[str, object]:
    selected = [
        col
        for col in features_train.columns
        if col not in KEY_COLUMNS
        and (col.startswith("base_") or any(col.startswith(prefix) for prefix in spec.feature_prefixes))
    ]
    x_train = features_train[selected].to_numpy(dtype=np.float32)
    x_test = features_test[selected].to_numpy(dtype=np.float32)
    y = labels[TARGET_COLUMNS].astype(int)
    oof_pred = np.zeros((len(labels), len(TARGET_COLUMNS)), dtype=float)
    test_pred = np.zeros((len(features_test), len(TARGET_COLUMNS)), dtype=float)
    target_scores = {}
    for target_i, target in enumerate(TARGET_COLUMNS):
        target_values = y[target].to_numpy(dtype=int)
        for trn_idx, val_idx in folds:
            model = make_pipeline(
                SimpleImputer(strategy="median"),
                StandardScaler(),
                LogisticRegression(C=spec.c_value, max_iter=2000, solver="lbfgs", random_state=2026),
            )
            model.fit(x_train[trn_idx], target_values[trn_idx])
            oof_pred[val_idx, target_i] = model.predict_proba(x_train[val_idx])[:, 1]
        full_model = make_pipeline(
            SimpleImputer(strategy="median"),
            StandardScaler(),
            LogisticRegression(C=spec.c_value, max_iter=2000, solver="lbfgs", random_state=2026),
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
        "n_features": len(selected),
        "c_value": spec.c_value,
        "feature_prefixes": list(spec.feature_prefixes),
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
    master = normalize_keys(pd.read_parquet(args.master_path))
    combined = pd.concat([train[KEY_COLUMNS].assign(_split="train"), sample[KEY_COLUMNS].assign(_split="test")], ignore_index=True)
    merged = combined.merge(master, on=KEY_COLUMNS, how="left", validate="one_to_one")
    if merged["role"].isna().any():
        raise ValueError("Some train/sample rows failed to align to master daily features")
    numeric_cols = [
        col
        for col in merged.select_dtypes(include=[np.number]).columns
        if col not in TARGET_COLUMNS and not col.startswith("pred_")
    ]
    keep_cols = [col for col in numeric_cols if float(merged[col].notna().mean()) >= args.min_non_null]
    x, scale_report = robust_scale_matrix(merged, keep_cols)
    subjects = merged["subject_id"].to_numpy(str)
    x_centered = subject_center(x, subjects)
    groups = group_columns(keep_cols)

    context = add_weather_context(add_panel_calendar(merged[KEY_COLUMNS]), args.weather_path)
    context_cols = [col for col in context.select_dtypes(include=[np.number]).columns if col not in TARGET_COLUMNS]
    context_values = SimpleImputer(strategy="median").fit_transform(context[context_cols])
    context_values = StandardScaler().fit_transform(context_values).astype(np.float32)

    features = merged[KEY_COLUMNS].copy()
    knn_features = build_knn_twin_features(x, x_centered, subjects, groups, args.knn_same, args.knn_cross)
    proto_features = build_prototype_features(x_centered, subjects, context_values, groups, args.n_prototypes, args.prototype_context_k)
    dae_features, dae_report = build_dae_features(x, groups, args.dae_mask_rate, args.dae_augmentations, args.dae_max_iter)
    features = pd.concat([features, knn_features, proto_features, dae_features], axis=1)

    features_train = features.iloc[: len(train)].reset_index(drop=True).copy()
    features_test = features.iloc[len(train) :].reset_index(drop=True).copy()
    features_train, features_test, base_cols = add_base_features(
        features_train,
        features_test,
        train,
        sample,
        args.base_oof,
        args.base_submission,
    )
    if not features_train[KEY_COLUMNS].equals(train[KEY_COLUMNS]) or not features_test[KEY_COLUMNS].equals(sample[KEY_COLUMNS]):
        raise ValueError("Feature key order mismatch")

    feature_cols = [col for col in features_train.columns if col not in KEY_COLUMNS]
    features_train[KEY_COLUMNS + feature_cols].to_csv(output_dir / "features_train.csv", index=False)
    features_test[KEY_COLUMNS + feature_cols].to_csv(output_dir / "features_test.csv", index=False)
    train[KEY_COLUMNS + TARGET_COLUMNS].to_csv(output_dir / "labels_train.csv", index=False)

    specs = []
    c_values = [float(value) for value in args.c_values.split(",") if value.strip()]
    for c_value in c_values:
        tag = str(c_value).replace(".", "p")
        specs.extend(
            [
                SourceSpec(f"twin_knn_c{tag}", ("knn_",), c_value),
                SourceSpec(f"twin_proto_c{tag}", ("proto_",), c_value),
                SourceSpec(f"twin_dae_c{tag}", ("dae_",), c_value),
                SourceSpec(f"twin_all_c{tag}", ("knn_", "proto_", "dae_"), c_value),
            ]
        )

    folds = make_subject_time_folds(train, args.n_folds)
    rows = [train_source(spec, features_train, features_test, train, folds, output_dir) for spec in specs]
    report = pd.DataFrame(rows).sort_values("avg_log_loss").reset_index(drop=True)
    report.to_csv(output_dir / "counterfactual_day_twin_report.csv", index=False)
    (output_dir / "counterfactual_day_twin_report.json").write_text(
        json.dumps(report.to_dict(orient="records"), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    manifest = {
        "master_path": args.master_path,
        "base_oof": args.base_oof,
        "base_submission": args.base_submission,
        "n_rows": int(len(merged)),
        "n_numeric_features": int(len(keep_cols)),
        "n_output_features": int(len(feature_cols)),
        "groups": {name: [keep_cols[i] for i in indices] for name, indices in groups.items()},
        "scale": scale_report,
        "dae": dae_report,
        "methods": {
            "knn": "Group-wise masked same-subject/cross-subject normal-day imputation.",
            "prototype": "Group-wise prototype composition vs context-expected prototype mixture.",
            "dae": "Masked denoising autoencoder evaluated with leave-one-group-out reconstruction.",
        },
    }
    (output_dir / "feature_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(report[["name", "avg_log_loss", "n_features"]].to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train counterfactual normal-day twin source bank.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--master-path", default="artifacts/10_master_daily.parquet")
    parser.add_argument("--weather-path", default="outputs/external_weather_decoder/weather_features_by_date.csv")
    parser.add_argument("--base-oof", default="outputs/temporal_retrieval_prototype_portfolio/oof_trp_s2tail_w080_q3midtail_w035.csv")
    parser.add_argument("--base-submission", default="outputs/temporal_retrieval_prototype_portfolio/submission_trp_s2tail_w080_q3midtail_w035.csv")
    parser.add_argument("--output-dir", default="outputs/counterfactual_day_twin_sources")
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--c-values", default="0.003,0.01,0.03")
    parser.add_argument("--min-non-null", type=float, default=0.35)
    parser.add_argument("--knn-same", type=int, default=8)
    parser.add_argument("--knn-cross", type=int, default=24)
    parser.add_argument("--n-prototypes", type=int, default=8)
    parser.add_argument("--prototype-context-k", type=int, default=24)
    parser.add_argument("--dae-mask-rate", type=float, default=0.30)
    parser.add_argument("--dae-augmentations", type=int, default=5)
    parser.add_argument("--dae-max-iter", type=int, default=260)
    return parser.parse_args()


if __name__ == "__main__":
    main()
