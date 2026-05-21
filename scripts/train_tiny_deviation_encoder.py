from __future__ import annotations

import argparse
import json
import warnings
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import log_loss
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from train_hourly_transformer_encoder import dataframe_to_markdown, targetwise_prediction
from train_pruned_state_decoder import average_log_loss, drift_vs_reference, subject_prior, write_prediction
from train_s2_sleep_retrieval_encoder import EPS, KEY_COLUMNS, TARGET_COLUMNS, make_subject_time_folds, normalize_keys


WINDOWS = {
    "all": (0, 24),
    "night": (0, 6),
    "morning": (6, 12),
    "afternoon": (12, 18),
    "evening": (18, 24),
}


def attach_day_window(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["lifelog_date"] = pd.to_datetime(out["timestamp"]).dt.strftime("%Y-%m-%d")
    hour = pd.to_datetime(out["timestamp"]).dt.hour
    labels = np.full(len(out), "all", dtype=object)
    out["_hour"] = hour.to_numpy(int)
    return out


def safe_std(values: pd.Series) -> float:
    return float(values.std(ddof=0))


def flatten_numeric_list(values: Iterable[object]) -> list[float]:
    out: list[float] = []
    for item in values:
        if isinstance(item, (list, tuple, np.ndarray)):
            out.extend(float(x) for x in item if pd.notna(x))
    return out


def list_dict_values(values: Iterable[object], key: str) -> list[float]:
    out: list[float] = []
    for item in values:
        if not isinstance(item, (list, tuple, np.ndarray)):
            continue
        for part in item:
            if isinstance(part, dict) and key in part and pd.notna(part[key]):
                out.append(float(part[key]))
    return out


def count_list_items(values: Iterable[object]) -> int:
    total = 0
    for item in values:
        if isinstance(item, (list, tuple, np.ndarray)):
            total += len(item)
    return int(total)


def unique_dict_values(values: Iterable[object], key: str) -> int:
    seen = set()
    for item in values:
        if not isinstance(item, (list, tuple, np.ndarray)):
            continue
        for part in item:
            if isinstance(part, dict) and key in part:
                seen.add(str(part[key]))
    return len(seen)


def ambience_scores(values: Iterable[object], token: str) -> tuple[float, float]:
    sums = []
    maxes = []
    token = token.lower()
    for item in values:
        score_sum = 0.0
        score_max = 0.0
        if isinstance(item, (list, tuple, np.ndarray)):
            for part in item:
                if isinstance(part, (list, tuple)) and len(part) >= 2 and token in str(part[0]).lower():
                    score = float(part[1])
                    score_sum += score
                    score_max = max(score_max, score)
        sums.append(score_sum)
        maxes.append(score_max)
    if not sums:
        return 0.0, 0.0
    return float(np.mean(sums)), float(np.max(maxes))


def usage_values(values: Iterable[object]) -> tuple[int, float, float, float]:
    app_count = 0
    total = 0.0
    max_time = 0.0
    active_rows = 0
    for item in values:
        row_total = 0.0
        if isinstance(item, (list, tuple, np.ndarray)):
            for part in item:
                if isinstance(part, dict):
                    app_count += 1
                    value = float(part.get("total_time", 0.0) or 0.0)
                    row_total += value
                    max_time = max(max_time, value)
        if row_total > 0:
            active_rows += 1
        total += row_total
    return int(app_count), float(total), float(max_time), float(active_rows)


def aggregate_group(group: pd.DataFrame, kind: str, value_cols: list[str]) -> dict[str, float]:
    row: dict[str, float] = {"records": float(len(group))}
    if kind == "scalar":
        for col in value_cols:
            values = pd.to_numeric(group[col], errors="coerce")
            row[f"{col}_mean"] = float(values.mean()) if values.notna().any() else np.nan
            row[f"{col}_std"] = safe_std(values.dropna()) if values.notna().any() else np.nan
            row[f"{col}_sum"] = float(values.sum()) if values.notna().any() else np.nan
            row[f"{col}_max"] = float(values.max()) if values.notna().any() else np.nan
            row[f"{col}_nonzero_ratio"] = float((values.fillna(0) != 0).mean()) if len(values) else 0.0
    elif kind == "hr":
        vals = flatten_numeric_list(group[value_cols[0]])
        arr = np.asarray(vals, dtype=float)
        row.update({"hr_points": float(len(arr)), "hr_mean": np.nan, "hr_std": np.nan, "hr_min": np.nan, "hr_max": np.nan})
        if len(arr):
            row.update({"hr_mean": float(arr.mean()), "hr_std": float(arr.std()), "hr_min": float(arr.min()), "hr_max": float(arr.max())})
    elif kind == "gps":
        for key in ("speed", "altitude", "latitude", "longitude"):
            arr = np.asarray(list_dict_values(group[value_cols[0]], key), dtype=float)
            row[f"gps_{key}_points"] = float(len(arr))
            row[f"gps_{key}_mean"] = float(arr.mean()) if len(arr) else np.nan
            row[f"gps_{key}_std"] = float(arr.std()) if len(arr) else np.nan
            row[f"gps_{key}_max"] = float(arr.max()) if len(arr) else np.nan
            row[f"gps_{key}_range"] = float(arr.max() - arr.min()) if len(arr) else np.nan
        speed = np.asarray(list_dict_values(group[value_cols[0]], "speed"), dtype=float)
        row["gps_moving_ratio"] = float((speed > 0.5).mean()) if len(speed) else np.nan
    elif kind == "radio":
        col = value_cols[0]
        id_key = "bssid" if col == "m_wifi" else "address"
        rssi = np.asarray(list_dict_values(group[col], "rssi"), dtype=float)
        row[f"{col}_items"] = float(count_list_items(group[col]))
        row[f"{col}_unique"] = float(unique_dict_values(group[col], id_key))
        row[f"{col}_rssi_mean"] = float(rssi.mean()) if len(rssi) else np.nan
        row[f"{col}_rssi_max"] = float(rssi.max()) if len(rssi) else np.nan
        row[f"{col}_rssi_std"] = float(rssi.std()) if len(rssi) else np.nan
    elif kind == "usage":
        app_count, total, max_time, active_rows = usage_values(group[value_cols[0]])
        row["usage_app_count"] = float(app_count)
        row["usage_total_time"] = total
        row["usage_max_time"] = max_time
        row["usage_active_rows"] = active_rows
    elif kind == "ambience":
        row["ambience_rows"] = float(len(group))
        for token in ("music", "speech", "vehicle", "outside", "inside", "silence"):
            mean_sum, max_score = ambience_scores(group[value_cols[0]], token)
            row[f"ambience_{token}_mean_sum"] = mean_sum
            row[f"ambience_{token}_max"] = max_score
    return row


def aggregate_file(path: Path) -> pd.DataFrame:
    df = attach_day_window(pd.read_parquet(path))
    stem = path.stem.replace("ch2025_", "")
    object_cols = [c for c in df.columns if c not in {"subject_id", "timestamp", "lifelog_date", "_hour"} and df[c].dtype == "object"]
    value_cols = [c for c in df.columns if c not in {"subject_id", "timestamp", "lifelog_date", "_hour"}]
    if stem == "wHr":
        kind = "hr"
    elif stem == "mGps":
        kind = "gps"
    elif stem in {"mWifi", "mBle"}:
        kind = "radio"
    elif stem == "mUsageStats":
        kind = "usage"
    elif stem == "mAmbience":
        kind = "ambience"
    else:
        kind = "scalar"
    value_cols = object_cols if kind != "scalar" else value_cols

    frames = []
    for window_name, (start, end) in WINDOWS.items():
        part = df if window_name == "all" else df[(df["_hour"] >= start) & (df["_hour"] < end)]
        rows = []
        for (subject, date), group in part.groupby(["subject_id", "lifelog_date"], sort=False):
            agg = aggregate_group(group, kind, value_cols)
            rows.append({"subject_id": subject, "lifelog_date": date, **{f"{stem}_{window_name}_{k}": v for k, v in agg.items()}})
        frames.append(pd.DataFrame(rows))
    out = frames[0]
    for frame in frames[1:]:
        out = out.merge(frame, on=["subject_id", "lifelog_date"], how="outer")
    return out


def build_daily_features(keys: pd.DataFrame, data_dir: Path, cache_path: Path, force: bool) -> pd.DataFrame:
    if cache_path.exists() and not force:
        cached = pd.read_parquet(cache_path).copy()
        for col in ("subject_id", "lifelog_date"):
            cached[col] = cached[col].astype(str)
        cached = cached.drop(columns=[col for col in ("sleep_date",) if col in cached.columns])
        return keys.merge(cached, on=["subject_id", "lifelog_date"], how="left")
    merged = keys[["subject_id", "lifelog_date"]].drop_duplicates().copy()
    for path in sorted(data_dir.glob("*.parquet")):
        print(f"[tiny] aggregating {path.name}", flush=True)
        features = aggregate_file(path)
        merged = merged.merge(features, on=["subject_id", "lifelog_date"], how="left")
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    merged.to_parquet(cache_path, index=False)
    return keys.merge(merged, on=["subject_id", "lifelog_date"], how="left")


def add_calendar_features(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    date = pd.to_datetime(out["lifelog_date"])
    out["cal_weekday"] = date.dt.weekday.astype(float)
    out["cal_is_weekend"] = (date.dt.weekday >= 5).astype(float)
    out["cal_day_index"] = (date - date.min()).dt.days.astype(float)
    subject_codes = {subject: i for i, subject in enumerate(sorted(out["subject_id"].unique()))}
    out["subject_code"] = out["subject_id"].map(subject_codes).astype(float)
    return out


def subject_relative(
    x_all: np.ndarray,
    x_sample: np.ndarray,
    train_subjects: np.ndarray,
    sample_subjects: np.ndarray,
    fit_idx: np.ndarray,
    eval_idx: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    x_fit = x_all[fit_idx]
    x_eval = x_all[eval_idx]
    fit_subjects = train_subjects[fit_idx]
    eval_subjects = train_subjects[eval_idx]
    fit_out = np.zeros((len(fit_idx), x_all.shape[1] * 3), dtype=float)
    eval_out = np.zeros((len(eval_idx), x_all.shape[1] * 3), dtype=float)
    sample_out = np.zeros((len(x_sample), x_all.shape[1] * 3), dtype=float)
    global_mean = np.nanmean(x_fit, axis=0, keepdims=True)
    global_std = np.nanstd(x_fit, axis=0, keepdims=True) + 1e-6
    for subject in sorted(set(train_subjects.tolist()) | set(sample_subjects.tolist())):
        fit_mask = fit_subjects == subject
        basis = x_fit[fit_mask] if fit_mask.any() else x_fit
        mean = np.nanmean(basis, axis=0, keepdims=True)
        std = np.nanstd(basis, axis=0, keepdims=True) + 1e-6
        if not np.isfinite(mean).all():
            mean = global_mean
        if not np.isfinite(std).all():
            std = global_std
        for target, source, mask in (
            (fit_out, x_fit, fit_mask),
            (eval_out, x_eval, eval_subjects == subject),
            (sample_out, x_sample, sample_subjects == subject),
        ):
            if not mask.any():
                continue
            raw = source[mask]
            delta = raw - mean
            z = delta / std
            ratio = delta / (np.abs(mean) + 1.0)
            target[mask] = np.concatenate([delta, z, ratio], axis=1)
    return fit_out, eval_out, sample_out


def model_predict(
    family: str,
    x_fit: np.ndarray,
    y_fit: np.ndarray,
    x_eval: np.ndarray,
    x_sample: np.ndarray,
    prior_fit: np.ndarray,
    prior_eval: np.ndarray,
    prior_sample: np.ndarray,
    select_k: int,
    blend: float,
    c_value: float,
    alpha: float,
) -> tuple[np.ndarray, np.ndarray]:
    k = min(select_k, x_fit.shape[1])
    if family == "logreg":
        if len(np.unique(y_fit)) < 2:
            pred_eval = np.full(len(x_eval), float(y_fit[0]))
            pred_sample = np.full(len(x_sample), float(y_fit[0]))
        else:
            pipe = make_pipeline(
                SimpleImputer(strategy="median"),
                StandardScaler(),
                SelectKBest(f_classif, k=k),
                LogisticRegression(C=c_value, solver="lbfgs", max_iter=5000, random_state=2026),
            )
            pipe.fit(x_fit, y_fit)
            pred_eval = pipe.predict_proba(x_eval)[:, 1]
            pred_sample = pipe.predict_proba(x_sample)[:, 1]
        return (1.0 - blend) * prior_eval + blend * pred_eval, (1.0 - blend) * prior_sample + blend * pred_sample
    if family == "ridge":
        pipe = make_pipeline(
            SimpleImputer(strategy="median"),
            StandardScaler(),
            SelectKBest(f_classif, k=k),
            Ridge(alpha=alpha, solver="lsqr", random_state=2026),
        )
        pipe.fit(x_fit, y_fit.astype(float) - prior_fit)
        return prior_eval + blend * pipe.predict(x_eval), prior_sample + blend * pipe.predict(x_sample)
    raise ValueError(f"Unknown family: {family}")


def run(args: argparse.Namespace) -> None:
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    all_keys = pd.concat([train[KEY_COLUMNS], sample[KEY_COLUMNS]], ignore_index=True)
    all_features = build_daily_features(all_keys, Path(args.data_dir), Path(args.cache_path), args.force_rebuild_cache)
    all_features = add_calendar_features(all_features)
    train_features = all_features.iloc[: len(train)].reset_index(drop=True)
    sample_features = all_features.iloc[len(train) :].reset_index(drop=True)
    numeric_candidates = [c for c in train_features.select_dtypes(include=[np.number]).columns if c not in KEY_COLUMNS + TARGET_COLUMNS]
    feature_cols = []
    for col in numeric_candidates:
        values = train_features[col].to_numpy(float)
        if np.isfinite(values).sum() == 0:
            continue
        if np.nanstd(values) <= 1e-12:
            continue
        feature_cols.append(col)
    x_all = train_features[feature_cols].to_numpy(float)
    x_sample = sample_features[feature_cols].to_numpy(float)
    train_subjects = train["subject_id"].astype(str).to_numpy(object)
    sample_subjects = sample["subject_id"].astype(str).to_numpy(object)
    folds = make_subject_time_folds(train, args.n_folds)

    specs = []
    for mode in args.feature_modes:
        for family in args.families:
            for k in args.select_k:
                for blend in args.blends:
                    if family == "logreg":
                        for c in args.c_values:
                            specs.append((mode, family, k, blend, c, args.ridge_alphas[0], f"{mode}__logreg_k{k}_c{c:g}_b{blend:g}"))
                    else:
                        for alpha in args.ridge_alphas:
                            specs.append((mode, family, k, blend, args.c_values[0], alpha, f"{mode}__ridge_k{k}_a{alpha:g}_b{blend:g}"))

    predictions = {name: np.zeros((len(train), len(TARGET_COLUMNS))) for *_, name in specs}
    sample_folds = {name: [] for *_, name in specs}
    fold_rows = []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        warnings.simplefilter("ignore", UserWarning)
        for fold_i, fold in enumerate(folds, 1):
            prior_fit_all = subject_prior(train.iloc[fold.train_idx], train.iloc[fold.train_idx], args.prior_alpha)
            prior_eval_all = subject_prior(train.iloc[fold.train_idx], train.iloc[fold.val_idx], args.prior_alpha)
            prior_sample_all = subject_prior(train.iloc[fold.train_idx], sample, args.prior_alpha)
            rel_fit, rel_eval, rel_sample = subject_relative(x_all, x_sample, train_subjects, sample_subjects, fold.train_idx, fold.val_idx)
            raw_fit, raw_eval, raw_sample = x_all[fold.train_idx], x_all[fold.val_idx], x_sample
            mode_cache = {
                "raw": (raw_fit, raw_eval, raw_sample),
                "deviation": (rel_fit, rel_eval, rel_sample),
                "raw_plus_deviation": (
                    np.concatenate([raw_fit, rel_fit], axis=1),
                    np.concatenate([raw_eval, rel_eval], axis=1),
                    np.concatenate([raw_sample, rel_sample], axis=1),
                ),
            }
            fold_sample = {name: np.zeros((len(sample), len(TARGET_COLUMNS))) for *_, name in specs}
            for target_i, target in enumerate(TARGET_COLUMNS):
                y_fit = train.iloc[fold.train_idx][target].to_numpy(int)
                y_eval = train.iloc[fold.val_idx][target].to_numpy(int)
                for mode, family, k, blend, c, alpha, name in specs:
                    x_fit, x_eval, x_s = mode_cache[mode]
                    pred_eval, pred_sample = model_predict(
                        family,
                        x_fit,
                        y_fit,
                        x_eval,
                        x_s,
                        prior_fit_all[:, target_i],
                        prior_eval_all[:, target_i],
                        prior_sample_all[:, target_i],
                        k,
                        blend,
                        c,
                        alpha,
                    )
                    pred_eval = np.clip(pred_eval, EPS, 1.0 - EPS)
                    pred_sample = np.clip(pred_sample, EPS, 1.0 - EPS)
                    predictions[name][fold.val_idx, target_i] = pred_eval
                    fold_sample[name][:, target_i] = pred_sample
                    fold_rows.append({"fold": fold_i, "target": target, "source": name, "loss": float(log_loss(y_eval, pred_eval, labels=[0, 1]))})
            for name, pred in fold_sample.items():
                sample_folds[name].append(pred)

    sample_predictions = {name: np.clip(np.mean(parts, axis=0), EPS, 1.0 - EPS) for name, parts in sample_folds.items()}
    score_rows = []
    for name, pred in predictions.items():
        pred = np.clip(pred, EPS, 1.0 - EPS)
        predictions[name] = pred
        avg, per = average_log_loss(train[TARGET_COLUMNS], pred)
        drift = drift_vs_reference(sample, sample_predictions[name], Path(args.reference_submission) if args.reference_submission else None)
        score_rows.append({"source": name, "avg_log_loss": avg, "drift_vs_reference": drift.get("mean_abs_drift"), **per})
    score_df = pd.DataFrame(score_rows).sort_values("avg_log_loss").reset_index(drop=True)
    target_oof, target_sample, target_sources, target_losses = targetwise_prediction(score_df, predictions, sample_predictions, train)
    target_avg, target_per = average_log_loss(train[TARGET_COLUMNS], target_oof)
    target_drift = drift_vs_reference(sample, target_sample, Path(args.reference_submission) if args.reference_submission else None)
    best_global = str(score_df.iloc[0]["source"])
    global_avg, global_per = average_log_loss(train[TARGET_COLUMNS], predictions[best_global])
    global_drift = drift_vs_reference(sample, sample_predictions[best_global], Path(args.reference_submission) if args.reference_submission else None)
    if target_avg <= global_avg:
        best_name = "targetwise"
        best_oof, best_sample, best_avg, best_per, best_drift = target_oof, target_sample, target_avg, target_per, target_drift
    else:
        best_name = best_global
        best_oof, best_sample, best_avg, best_per, best_drift = predictions[best_global], sample_predictions[best_global], global_avg, global_per, global_drift

    score_df.to_csv(output_dir / "tiny_deviation_scores.csv", index=False)
    pd.DataFrame(fold_rows).to_csv(output_dir / "tiny_deviation_fold_losses.csv", index=False)
    pd.DataFrame([{"target": target, "source": source, "loss": target_losses[target]} for target, source in target_sources.items()]).to_csv(output_dir / "targetwise_selection.csv", index=False)
    pd.DataFrame({"feature": feature_cols}).to_csv(output_dir / "feature_columns.csv", index=False)
    write_prediction(output_dir / "oof_tiny_deviation_best.csv", train, best_oof, oof=True)
    write_prediction(output_dir / "submission_tiny_deviation_best.csv", sample, best_sample, oof=False)
    report = {
        "best_source": best_name,
        "best_avg_log_loss": float(best_avg),
        "best_per_target": {target: float(best_per[target]) for target in TARGET_COLUMNS},
        "best_drift_vs_reference": best_drift,
        "best_global_source": best_global,
        "best_global_avg_log_loss": float(global_avg),
        "best_global_drift_vs_reference": global_drift,
        "targetwise_avg_log_loss": float(target_avg),
        "targetwise_drift_vs_reference": target_drift,
        "targetwise_sources": target_sources,
        "targetwise_source_losses": target_losses,
        "n_base_features": len(feature_cols),
        "n_candidates": len(specs),
    }
    (output_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    md = [
        "# Tiny Deviation Encoder v1",
        "",
        "## Goal",
        "",
        "Restart from the smallest useful representation: daily/window aggregates from raw lifelog logs, fold-local subject-relative deviations, and tiny linear decoders. No Transformer, diffusion, HGB, retrieval, or prediction teacher is used.",
        "",
        "## Result",
        "",
        f"- Best source: `{best_name}`",
        f"- OOF avg logloss: `{best_avg:.6f}`",
        f"- Drift vs v83 reference: `{best_drift.get('mean_abs_drift', float('nan')):.6f}`",
        f"- Base aggregate features: `{len(feature_cols)}`",
        "",
        "## Top Scores",
        "",
        dataframe_to_markdown(score_df.head(20)),
        "",
        "## Target-Wise Selection",
        "",
        f"- Target-wise avg logloss: `{target_avg:.6f}`",
        f"- Target-wise drift vs v83: `{target_drift.get('mean_abs_drift', float('nan')):.6f}`",
        "",
        dataframe_to_markdown(pd.DataFrame([{"target": target, "source": source, "loss": target_losses[target]} for target, source in target_sources.items()])),
        "",
        "## Decision",
        "",
        "This establishes the small-model floor for the subject-relative hypothesis. If it is close to the deep channel-patch branch, the next work should simplify the encoder; if it is much weaker, the deep latent is adding real nonlinear structure.",
    ]
    (output_dir / "report.md").write_text("\n".join(md), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train tiny subject-relative daily deviation baselines from raw lifelog logs.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--data-dir", default="data/ch2025_data_items")
    parser.add_argument("--cache-path", default="outputs/tiny_deviation_encoder_v1/daily_window_features.parquet")
    parser.add_argument("--reference-submission", default="outputs/v83_repaired_v80/submission_v83_gq015_gs010.csv")
    parser.add_argument("--output-dir", default="outputs/tiny_deviation_encoder_v1")
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--prior-alpha", type=float, default=8.0)
    parser.add_argument("--feature-modes", nargs="+", default=["raw", "deviation", "raw_plus_deviation"])
    parser.add_argument("--families", nargs="+", choices=["ridge", "logreg"], default=["ridge", "logreg"])
    parser.add_argument("--select-k", type=int, nargs="+", default=[20, 50, 100, 200])
    parser.add_argument("--blends", type=float, nargs="+", default=[0.05, 0.1, 0.2, 0.35])
    parser.add_argument("--c-values", type=float, nargs="+", default=[0.03, 0.1, 0.3])
    parser.add_argument("--ridge-alphas", type=float, nargs="+", default=[5.0, 20.0, 80.0])
    parser.add_argument("--force-rebuild-cache", action="store_true")
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
