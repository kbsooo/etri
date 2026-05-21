from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import log_loss
from sklearn.preprocessing import StandardScaler

from train_s2_sleep_retrieval_encoder import (
    EPS,
    KEY_COLUMNS,
    SEED,
    TARGET_COLUMNS,
    dataframe_to_markdown,
    make_subject_time_folds,
    merge_feature_tables,
    normalize_keys,
    safe_logit,
    sigmoid,
)


STATE_CANDIDATES = ["subject_prior", "logreg", "hgb", "rank_pairwise", "prototype", "residual_ridge", "state_mean"]
BLEND_SOURCES = ["logreg", "hgb", "rank_pairwise", "prototype", "residual_ridge", "state_mean"]
BLEND_WEIGHTS = [0.03, 0.05, 0.10, 0.20, 0.35]


@dataclass(frozen=True)
class Preset:
    name: str
    mode: str
    family: str | None = None


def average_log_loss(y_true: pd.DataFrame, pred: np.ndarray) -> tuple[float, dict[str, float]]:
    clipped = np.clip(pred, EPS, 1.0 - EPS)
    per_target = {
        target: float(log_loss(y_true[target].to_numpy(int), clipped[:, i], labels=[0, 1]))
        for i, target in enumerate(TARGET_COLUMNS)
    }
    return float(np.mean(list(per_target.values()))), per_target


def build_presets() -> list[Preset]:
    return [
        Preset("full", "full"),
        Preset("no_raw", "drop", "raw"),
        Preset("no_derivative", "drop", "derivative"),
        Preset("no_ratio", "drop", "ratio"),
        Preset("no_rank", "drop", "rank"),
        Preset("no_missingness", "drop", "missingness"),
        Preset("no_temporal_delta", "drop", "temporal_delta"),
        Preset("no_gps", "drop", "gps"),
        Preset("no_phone", "drop", "phone"),
        Preset("no_sleep", "drop", "sleep"),
        Preset("no_late_pool", "drop", "late_pool"),
        Preset("only_deviation", "only", "deviation"),
        Preset("only_missingness", "only", "missingness"),
        Preset("only_rhythm", "only", "rhythm"),
        Preset("only_cross_modal", "only", "cross_modal"),
    ]


def family_masks(columns: list[str]) -> dict[str, np.ndarray]:
    lower = np.array([c.lower() for c in columns])

    def has_any(tokens: tuple[str, ...]) -> np.ndarray:
        mask = np.zeros(len(columns), dtype=bool)
        for token in tokens:
            mask |= np.char.find(lower, token) >= 0
        return mask

    engineered = has_any(("eng__", "tmp__", "subjdev__"))
    derivative = has_any(("delta", "diff", "abs_", "std", "vol", "accel", "slope", "momentum", "burden", "streak", "decay"))
    temporal_delta = has_any(("tmp__prev", "tmp__roll", "tmp__accel", "tmp__persist", "tmp__recovery", "tmp__shock", "tmp__burden", "tmp__decay"))
    rank = has_any(("rank", "percentile", "extreme", "novelty", "recurrence"))
    ratio = has_any(("ratio", "share", "entropy", "cosine", "balance", "mismatch", "gap__"))
    missingness = has_any(("missing", "gap", "coverage", "row_count", "zero_rate", "normcov", "charging"))
    gps = has_any(("gps", "mobility", "place", "home", "work", "elsewhere", "speed", "stationary", "moving"))
    phone = has_any(("screen", "usage", "app_", "phone", "charging"))
    sleep = has_any(("sleep", "night", "earlyam", "late_night", "latenight", "hr", "step", "pedo", "light", "still"))
    late_pool = has_any(("late", "night", "earlyam", "secondhalf", "tail"))
    deviation = has_any(("subjdev__", "roll3_delta", "roll7_delta", "roll14", "z__", "_z__", "rank_extreme", "state_novelty"))
    rhythm = has_any(("rhythm", "recovery", "circadian", "night", "earlyam", "late_night", "roll3_minus_roll7", "persist"))
    cross_modal = has_any(("mismatch", "sync", "leadlag", "state_transition", "social_phone", "body_phone", "mobility_social"))
    raw = ~engineered
    return {
        "raw": raw,
        "derivative": derivative,
        "temporal_delta": temporal_delta,
        "ratio": ratio,
        "rank": rank,
        "missingness": missingness,
        "gps": gps,
        "phone": phone,
        "sleep": sleep,
        "late_pool": late_pool,
        "deviation": deviation,
        "rhythm": rhythm,
        "cross_modal": cross_modal,
    }


def columns_for_preset(columns: list[str], preset: Preset) -> list[str]:
    masks = family_masks(columns)
    if preset.mode == "full":
        mask = np.ones(len(columns), dtype=bool)
    elif preset.mode == "drop":
        mask = ~masks[preset.family or ""]
    elif preset.mode == "only":
        mask = masks[preset.family or ""]
    else:
        raise ValueError(preset.mode)
    selected = [col for col, keep in zip(columns, mask) if keep]
    if not selected:
        raise ValueError(f"Preset {preset.name} selected no columns")
    return selected


def cap_columns_by_variance(train_x: pd.DataFrame, sample_x: pd.DataFrame, columns: list[str], max_features: int) -> list[str]:
    usable = [
        c
        for c in columns
        if train_x[c].notna().mean() >= 0.05
        and sample_x[c].notna().mean() >= 0.05
        and train_x[c].nunique(dropna=True) > 1
    ]
    if len(usable) <= max_features:
        return usable
    values = pd.concat([train_x[usable], sample_x[usable]], axis=0, ignore_index=True)
    values = values.replace([np.inf, -np.inf], np.nan)
    med = values.median(axis=0, skipna=True)
    filled = values.fillna(med).fillna(0.0)
    scores = filled.var(axis=0).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    keep = scores.sort_values(ascending=False).head(max_features).index.tolist()
    return sorted(keep)


def subject_prior(train_part: pd.DataFrame, eval_part: pd.DataFrame, alpha: float) -> np.ndarray:
    global_rate = train_part[TARGET_COLUMNS].mean()
    sums = train_part.groupby("subject_id")[TARGET_COLUMNS].sum()
    counts = train_part.groupby("subject_id")[TARGET_COLUMNS].count()
    rates = (sums + alpha * global_rate) / (counts + alpha)
    pred = np.zeros((len(eval_part), len(TARGET_COLUMNS)), dtype=float)
    for i, sid in enumerate(eval_part["subject_id"]):
        pred[i] = rates.loc[sid].to_numpy(float) if sid in rates.index else global_rate.to_numpy(float)
    return np.clip(pred, EPS, 1.0 - EPS)


def fit_state_features(
    train_x: pd.DataFrame,
    sample_x: pd.DataFrame,
    train_keys: pd.DataFrame,
    sample_keys: pd.DataFrame,
    fit_idx: np.ndarray,
    eval_idx: np.ndarray | None,
    columns: list[str],
    pca_dim: int,
    n_proto: int,
) -> tuple[np.ndarray, np.ndarray | None, np.ndarray]:
    fit_raw = train_x.iloc[fit_idx][columns].replace([np.inf, -np.inf], np.nan)
    eval_raw = None if eval_idx is None else train_x.iloc[eval_idx][columns].replace([np.inf, -np.inf], np.nan)
    sample_raw = sample_x[columns].replace([np.inf, -np.inf], np.nan)

    imputer = SimpleImputer(strategy="median", keep_empty_features=True)
    scaler = StandardScaler()
    fit_scaled = scaler.fit_transform(imputer.fit_transform(fit_raw))
    eval_scaled = None if eval_raw is None else scaler.transform(imputer.transform(eval_raw))
    sample_scaled = scaler.transform(imputer.transform(sample_raw))

    dim = min(pca_dim, fit_scaled.shape[1], max(1, fit_scaled.shape[0] - 1))
    pca = PCA(n_components=dim, random_state=SEED)
    fit_z = pca.fit_transform(fit_scaled)
    eval_z = None if eval_scaled is None else pca.transform(eval_scaled)
    sample_z = pca.transform(sample_scaled)

    fit_subjects = train_keys.iloc[fit_idx]["subject_id"].to_numpy(str)

    def state_from_z(z: np.ndarray, keys: pd.DataFrame) -> np.ndarray:
        global_mean = fit_z.mean(axis=0)
        global_std = fit_z.std(axis=0) + 1e-6
        dev = np.zeros_like(z)
        rank = np.full_like(z, 0.5)
        for row_i, sid in enumerate(keys["subject_id"].to_numpy(str)):
            prior = fit_z[fit_subjects == sid]
            if len(prior) < 2:
                mean, std = global_mean, global_std
                prior = fit_z
            else:
                mean, std = prior.mean(axis=0), prior.std(axis=0) + 1e-6
            dev[row_i] = (z[row_i] - mean) / std
            rank[row_i] = (prior <= z[row_i]).mean(axis=0)
        return np.concatenate([z, dev, np.abs(dev), rank - 0.5, np.abs(rank - 0.5)], axis=1)

    fit_state = state_from_z(fit_z, train_keys.iloc[fit_idx])
    eval_state = None if eval_z is None else state_from_z(eval_z, train_keys.iloc[eval_idx])
    sample_state = state_from_z(sample_z, sample_keys)

    k = min(n_proto, max(2, len(fit_state) // 25))
    if k >= 2:
        km = KMeans(n_clusters=k, n_init=10, random_state=SEED)
        fit_dist = km.fit_transform(fit_state)
        eval_dist = None if eval_state is None else km.transform(eval_state)
        sample_dist = km.transform(sample_state)

        def soft_membership(dist: np.ndarray) -> np.ndarray:
            scale = np.nanmedian(dist) + 1e-6
            logits = -dist / scale
            logits -= logits.max(axis=1, keepdims=True)
            weights = np.exp(logits)
            return weights / weights.sum(axis=1, keepdims=True)

        fit_state = np.concatenate([fit_state, soft_membership(fit_dist)], axis=1)
        eval_state = None if eval_state is None else np.concatenate([eval_state, soft_membership(eval_dist)], axis=1)
        sample_state = np.concatenate([sample_state, soft_membership(sample_dist)], axis=1)
    return fit_state, eval_state, sample_state


def fit_logreg(x_fit: np.ndarray, y_fit: np.ndarray, x_eval: np.ndarray, x_sample: np.ndarray, c_value: float) -> tuple[np.ndarray, np.ndarray]:
    if len(np.unique(y_fit)) < 2:
        value = float(y_fit[0])
        return np.full(len(x_eval), value), np.full(len(x_sample), value)
    model = LogisticRegression(C=c_value, solver="lbfgs", max_iter=5000, random_state=SEED)
    model.fit(x_fit, y_fit)
    return model.predict_proba(x_eval)[:, 1], model.predict_proba(x_sample)[:, 1]


def fit_hgb(x_fit: np.ndarray, y_fit: np.ndarray, x_eval: np.ndarray, x_sample: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    if len(np.unique(y_fit)) < 2:
        value = float(y_fit[0])
        return np.full(len(x_eval), value), np.full(len(x_sample), value)
    model = HistGradientBoostingClassifier(
        max_iter=80,
        learning_rate=0.035,
        max_leaf_nodes=7,
        min_samples_leaf=18,
        l2_regularization=0.15,
        random_state=SEED,
    )
    model.fit(x_fit, y_fit)
    return model.predict_proba(x_eval)[:, 1], model.predict_proba(x_sample)[:, 1]


def fit_rank_pairwise(
    x_fit: np.ndarray,
    y_fit: np.ndarray,
    x_eval: np.ndarray,
    x_sample: np.ndarray,
    max_pairs: int,
) -> tuple[np.ndarray, np.ndarray]:
    pos = np.flatnonzero(y_fit == 1)
    neg = np.flatnonzero(y_fit == 0)
    if len(pos) == 0 or len(neg) == 0:
        value = float(np.mean(y_fit))
        return np.full(len(x_eval), value), np.full(len(x_sample), value)
    rng = np.random.default_rng(SEED + len(pos) * 17 + len(neg))
    total_pairs = len(pos) * len(neg)
    n_pairs = min(max_pairs, total_pairs)
    pos_pick = rng.choice(pos, n_pairs, replace=n_pairs > len(pos))
    neg_pick = rng.choice(neg, n_pairs, replace=n_pairs > len(neg))
    pair_x = np.vstack([x_fit[pos_pick] - x_fit[neg_pick], x_fit[neg_pick] - x_fit[pos_pick]])
    pair_y = np.concatenate([np.ones(n_pairs), np.zeros(n_pairs)])
    ranker = LogisticRegression(C=0.03, solver="lbfgs", max_iter=3000, random_state=SEED)
    ranker.fit(pair_x, pair_y)
    fit_score = x_fit @ ranker.coef_.ravel()
    eval_score = x_eval @ ranker.coef_.ravel()
    sample_score = x_sample @ ranker.coef_.ravel()
    cal = LogisticRegression(C=0.5, solver="lbfgs", max_iter=3000, random_state=SEED)
    cal.fit(fit_score.reshape(-1, 1), y_fit)
    return cal.predict_proba(eval_score.reshape(-1, 1))[:, 1], cal.predict_proba(sample_score.reshape(-1, 1))[:, 1]


def fit_prototype_label(
    x_fit: np.ndarray,
    y_fit: np.ndarray,
    x_eval: np.ndarray,
    x_sample: np.ndarray,
    k: int,
) -> tuple[np.ndarray, np.ndarray]:
    k = min(k, max(2, len(x_fit) // 20))
    if k < 2:
        value = float(np.mean(y_fit))
        return np.full(len(x_eval), value), np.full(len(x_sample), value)
    km = KMeans(n_clusters=k, n_init=10, random_state=SEED)
    dist_fit = km.fit_transform(x_fit)
    labels = km.labels_
    global_rate = float(np.mean(y_fit))
    rates = np.zeros(k)
    for cluster in range(k):
        idx = labels == cluster
        rates[cluster] = (y_fit[idx].sum() + 8.0 * global_rate) / (idx.sum() + 8.0)

    def pred(dist: np.ndarray) -> np.ndarray:
        scale = np.nanmedian(dist_fit) + 1e-6
        logits = -dist / scale
        logits -= logits.max(axis=1, keepdims=True)
        weights = np.exp(logits)
        weights /= weights.sum(axis=1, keepdims=True)
        return weights @ rates

    return pred(km.transform(x_eval)), pred(km.transform(x_sample))


def fit_residual_ridge(
    x_fit: np.ndarray,
    y_fit: np.ndarray,
    base_fit: np.ndarray,
    base_eval: np.ndarray,
    base_sample: np.ndarray,
    x_eval: np.ndarray,
    x_sample: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    residual = safe_logit((y_fit * 0.98) + 0.01) - safe_logit(base_fit)
    model = Ridge(alpha=50.0)
    model.fit(x_fit, residual)
    return sigmoid(safe_logit(base_eval) + model.predict(x_eval)), sigmoid(safe_logit(base_sample) + model.predict(x_sample))


def run_preset(
    preset: Preset,
    train: pd.DataFrame,
    sample: pd.DataFrame,
    train_x: pd.DataFrame,
    sample_x: pd.DataFrame,
    columns: list[str],
    args: argparse.Namespace,
) -> tuple[dict, dict[str, np.ndarray], dict[str, np.ndarray]]:
    folds = make_subject_time_folds(train, args.n_folds)
    y_df = train[TARGET_COLUMNS].astype(int)
    oof = {name: np.zeros((len(train), len(TARGET_COLUMNS)), dtype=float) for name in STATE_CANDIDATES}
    sample_fold = {name: [] for name in STATE_CANDIDATES}
    fold_rows = []
    for fold_i, fold in enumerate(folds):
        fit_idx, val_idx = fold.train_idx, fold.val_idx
        fit_state, val_state, sample_state = fit_state_features(
            train_x,
            sample_x,
            train[KEY_COLUMNS],
            sample[KEY_COLUMNS],
            fit_idx,
            val_idx,
            columns,
            args.pca_dim,
            args.n_proto,
        )
        if val_state is None:
            raise RuntimeError("validation state missing")
        imputer = SimpleImputer(strategy="median", keep_empty_features=True)
        scaler = StandardScaler()
        fit_s = scaler.fit_transform(imputer.fit_transform(fit_state))
        val_s = scaler.transform(imputer.transform(val_state))
        sample_s = scaler.transform(imputer.transform(sample_state))

        base_fit = subject_prior(train.iloc[fit_idx], train.iloc[fit_idx], args.subject_alpha)
        base_val = subject_prior(train.iloc[fit_idx], train.iloc[val_idx], args.subject_alpha)
        base_sample = subject_prior(train.iloc[fit_idx], sample, args.subject_alpha)
        oof["subject_prior"][val_idx] = base_val
        while len(sample_fold["subject_prior"]) <= fold_i:
            sample_fold["subject_prior"].append(np.zeros((len(sample), len(TARGET_COLUMNS)), dtype=float))
        sample_fold["subject_prior"][fold_i] = base_sample
        y_fit_df = y_df.iloc[fit_idx]
        for target_i, target in enumerate(TARGET_COLUMNS):
            y_fit = y_fit_df[target].to_numpy(int)
            preds = {}
            preds["logreg"] = fit_logreg(fit_s, y_fit, val_s, sample_s, args.logreg_c)
            preds["hgb"] = fit_hgb(fit_s, y_fit, val_s, sample_s)
            preds["rank_pairwise"] = fit_rank_pairwise(fit_s, y_fit, val_s, sample_s, args.max_pairs)
            preds["prototype"] = fit_prototype_label(fit_s, y_fit, val_s, sample_s, args.n_label_proto)
            preds["residual_ridge"] = fit_residual_ridge(
                fit_s,
                y_fit,
                base_fit[:, target_i],
                base_val[:, target_i],
                base_sample[:, target_i],
                val_s,
                sample_s,
            )
            for name, (val_pred, sample_pred) in preds.items():
                oof[name][val_idx, target_i] = np.clip(val_pred, EPS, 1.0 - EPS)
                while len(sample_fold[name]) <= fold_i:
                    sample_fold[name].append(np.zeros((len(sample), len(TARGET_COLUMNS)), dtype=float))
                sample_fold[name][fold_i][:, target_i] = np.clip(sample_pred, EPS, 1.0 - EPS)
        fold_rows.append({"fold": fold_i, "fit_rows": len(fit_idx), "val_rows": len(val_idx), "state_dim": fit_s.shape[1]})

    sample_pred = {name: np.mean(np.stack(sample_fold[name], axis=0), axis=0) for name in STATE_CANDIDATES if name != "state_mean"}
    non_prior_sources = [name for name in sample_pred if name != "subject_prior"]
    oof["state_mean"] = np.mean(np.stack([oof[name] for name in non_prior_sources], axis=0), axis=0)
    sample_pred["state_mean"] = np.mean(np.stack([sample_pred[name] for name in non_prior_sources], axis=0), axis=0)
    for source in BLEND_SOURCES:
        for weight in BLEND_WEIGHTS:
            name = f"prior_logit_blend_{source}_w{int(weight * 100):02d}"
            oof[name] = sigmoid((1.0 - weight) * safe_logit(oof["subject_prior"]) + weight * safe_logit(oof[source]))
            sample_pred[name] = sigmoid(
                (1.0 - weight) * safe_logit(sample_pred["subject_prior"]) + weight * safe_logit(sample_pred[source])
            )
    score_rows = []
    for name in sorted(oof):
        avg, per_target = average_log_loss(y_df, oof[name])
        score_rows.append({"preset": preset.name, "candidate": name, "avg_log_loss": avg, **per_target})
    best_row = min(score_rows, key=lambda row: row["avg_log_loss"])
    return {
        "preset": preset.name,
        "feature_count": len(columns),
        "best_candidate": best_row["candidate"],
        "best_avg_log_loss": best_row["avg_log_loss"],
        "scores": score_rows,
        "folds": fold_rows,
    }, oof, sample_pred


def targetwise_select(y_df: pd.DataFrame, all_oof: dict[str, np.ndarray], all_sample: dict[str, np.ndarray]) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    selected_rows = []
    out_oof = np.zeros((len(y_df), len(TARGET_COLUMNS)), dtype=float)
    out_sample = np.zeros((next(iter(all_sample.values())).shape[0], len(TARGET_COLUMNS)), dtype=float)
    for target_i, target in enumerate(TARGET_COLUMNS):
        best = None
        for name, pred in all_oof.items():
            loss = float(log_loss(y_df[target].to_numpy(int), np.clip(pred[:, target_i], EPS, 1.0 - EPS), labels=[0, 1]))
            if best is None or loss < best["log_loss"]:
                best = {"target": target, "source": name, "log_loss": loss}
        assert best is not None
        selected_rows.append(best)
        out_oof[:, target_i] = all_oof[best["source"]][:, target_i]
        out_sample[:, target_i] = all_sample[best["source"]][:, target_i]
    avg, per_target = average_log_loss(y_df, out_oof)
    selected = pd.DataFrame(selected_rows)
    selected["targetwise_avg_log_loss"] = avg
    selected.attrs["per_target"] = per_target
    return selected, np.clip(out_oof, EPS, 1.0 - EPS), np.clip(out_sample, EPS, 1.0 - EPS)


def write_prediction(path: Path, keys: pd.DataFrame, values: np.ndarray, oof: bool) -> None:
    out = keys[KEY_COLUMNS].copy()
    for i, target in enumerate(TARGET_COLUMNS):
        out[f"pred_{target}" if oof else target] = np.clip(values[:, i], EPS, 1.0 - EPS)
    out.to_csv(path, index=False)


def drift_vs_reference(sample: pd.DataFrame, pred: np.ndarray, ref_path: Path | None) -> dict:
    if ref_path is None or not ref_path.exists():
        return {}
    ref = normalize_keys(pd.read_csv(ref_path))
    merged = sample[KEY_COLUMNS].merge(ref, on=KEY_COLUMNS, how="left", validate="one_to_one")
    if merged[TARGET_COLUMNS].isna().any().any():
        return {"warning": "reference join failed"}
    ref_values = merged[TARGET_COLUMNS].to_numpy(float)
    diff = pred - ref_values
    out = {
        "reference": str(ref_path),
        "mean_abs_drift": float(np.mean(np.abs(diff))),
        "max_abs_drift": float(np.max(np.abs(diff))),
        "corr": float(np.corrcoef(pred.ravel(), ref_values.ravel())[0, 1]),
        "target_mean": {target: float(pred[:, i].mean()) for i, target in enumerate(TARGET_COLUMNS)},
        "target_mean_shift": {target: float(diff[:, i].mean()) for i, target in enumerate(TARGET_COLUMNS)},
    }
    ordered = sample.reset_index(drop=True).copy()
    ordered["_row"] = np.arange(len(ordered))
    ordered["_pos"] = ordered.groupby("subject_id")["_row"].rank(method="first", pct=True)
    bins = pd.cut(ordered["_pos"], bins=[0, 1 / 3, 2 / 3, 1.000001], labels=["early", "mid", "late"], include_lowest=True)
    panel = {}
    for label in ["early", "mid", "late"]:
        idx = bins.astype(str).eq(label).to_numpy()
        if idx.any():
            panel[label] = float(np.mean(np.abs(diff[idx])))
    out["panel_mean_abs_drift"] = panel
    return out


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    train_x, sample_x = merge_feature_tables(train, sample)
    all_cols = train_x.columns.tolist()

    presets = build_presets()
    family_count_rows = []
    masks = family_masks(all_cols)
    for family, mask in masks.items():
        family_count_rows.append({"family": family, "columns": int(mask.sum())})
    pd.DataFrame(family_count_rows).to_csv(output_dir / "feature_family_counts.csv", index=False)

    reports = []
    all_oof: dict[str, np.ndarray] = {}
    all_sample: dict[str, np.ndarray] = {}
    for preset in presets:
        preset_cols = columns_for_preset(all_cols, preset)
        preset_cols = cap_columns_by_variance(train_x, sample_x, preset_cols, args.max_features)
        if len(preset_cols) < args.min_features:
            continue
        report, oof, sample_pred = run_preset(preset, train, sample, train_x, sample_x, preset_cols, args)
        reports.append(report)
        for candidate, pred in oof.items():
            key = f"{preset.name}__{candidate}"
            all_oof[key] = pred
            all_sample[key] = sample_pred[candidate]

    if not reports:
        raise RuntimeError("No preset produced a report")
    score_df = pd.DataFrame([row for report in reports for row in report["scores"]]).sort_values("avg_log_loss")
    preset_df = pd.DataFrame(
        [
            {
                "preset": report["preset"],
                "feature_count": report["feature_count"],
                "best_candidate": report["best_candidate"],
                "best_avg_log_loss": report["best_avg_log_loss"],
            }
            for report in reports
        ]
    ).sort_values("best_avg_log_loss")
    score_df.to_csv(output_dir / "candidate_scores.csv", index=False)
    preset_df.to_csv(output_dir / "preset_scores.csv", index=False)

    best_key = f"{score_df.iloc[0]['preset']}__{score_df.iloc[0]['candidate']}"
    best_oof = all_oof[best_key]
    best_sample = all_sample[best_key]
    selected, tw_oof, tw_sample = targetwise_select(train[TARGET_COLUMNS].astype(int), all_oof, all_sample)
    selected.to_csv(output_dir / "targetwise_selection.csv", index=False)

    write_prediction(output_dir / "oof_pruned_state_best_global.csv", train, best_oof, oof=True)
    write_prediction(output_dir / "submission_pruned_state_best_global.csv", sample, best_sample, oof=False)
    write_prediction(output_dir / "oof_pruned_state_targetwise.csv", train, tw_oof, oof=True)
    write_prediction(output_dir / "submission_pruned_state_targetwise.csv", sample, tw_sample, oof=False)

    best_avg, best_targets = average_log_loss(train[TARGET_COLUMNS].astype(int), best_oof)
    tw_avg, tw_targets = average_log_loss(train[TARGET_COLUMNS].astype(int), tw_oof)
    diagnostics = {
        "best_global_key": best_key,
        "best_global": {"avg_log_loss": best_avg, **best_targets},
        "targetwise": {"avg_log_loss": tw_avg, **tw_targets},
        "targetwise_selection": selected.to_dict(orient="records"),
        "drift_vs_reference_best_global": drift_vs_reference(sample, best_sample, Path(args.reference_submission) if args.reference_submission else None),
        "drift_vs_reference_targetwise": drift_vs_reference(sample, tw_sample, Path(args.reference_submission) if args.reference_submission else None),
        "args": vars(args),
    }
    (output_dir / "report.json").write_text(json.dumps({"reports": reports, "diagnostics": diagnostics}, indent=2), encoding="utf-8")
    lines = [
        "# Pruned State Decoder",
        "",
        "This experiment treats v83 only as a diagnostic reference. Predictions are built from pruned encoder input families plus state decoders.",
        "",
        "## Best Presets",
        "",
        dataframe_to_markdown(preset_df.head(20)),
        "",
        "## Best Candidates",
        "",
        dataframe_to_markdown(score_df.head(30)),
        "",
        "## Target-wise Selection",
        "",
        dataframe_to_markdown(selected),
        "",
        "## Summary",
        "",
        f"- Best global: `{best_key}` avg `{best_avg:.6f}`",
        f"- Target-wise avg: `{tw_avg:.6f}`",
        f"- Best global drift vs reference: `{diagnostics['drift_vs_reference_best_global'].get('mean_abs_drift', float('nan')):.6f}`",
        f"- Target-wise drift vs reference: `{diagnostics['drift_vs_reference_targetwise'].get('mean_abs_drift', float('nan')):.6f}`",
    ]
    (output_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"best_global={best_key} avg={best_avg:.6f}")
    print(f"targetwise avg={tw_avg:.6f}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Feature-family pruning plus state decoder experiment.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--output-dir", default="outputs/pruned_state_decoder_v1")
    parser.add_argument("--reference-submission", default="outputs/v83_repaired_v80/submission_v83_gq015_gs010.csv")
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--max-features", type=int, default=520)
    parser.add_argument("--min-features", type=int, default=20)
    parser.add_argument("--pca-dim", type=int, default=28)
    parser.add_argument("--n-proto", type=int, default=10)
    parser.add_argument("--n-label-proto", type=int, default=12)
    parser.add_argument("--logreg-c", type=float, default=0.03)
    parser.add_argument("--subject-alpha", type=float, default=10.0)
    parser.add_argument("--max-pairs", type=int, default=14000)
    return parser.parse_args()


if __name__ == "__main__":
    main()
