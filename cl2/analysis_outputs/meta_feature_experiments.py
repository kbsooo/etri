from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import log_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

sys.path.append(str(Path(__file__).resolve().parent))
import calibration_experiments as cal  # noqa: E402
import deep_dive_analysis as d  # noqa: E402
import sensor_feature_variant_experiments as sfv  # noqa: E402
import sensor_residual_experiments as sr  # noqa: E402


OUT = Path(__file__).resolve().parent
TARGETS = d.TARGETS
KEY = d.KEY

FIXED = {
    "Q2": ("phone", 0.10),
    "Q3": ("mobility", 0.20),
    "S4": ("mobility", 0.10),
}

WINDOWS = ["all", "early", "morning", "afternoon", "evening", "late"]
BASE_EXCLUDE = set(TARGETS + KEY + ["sleep_date", "split"])


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1 - 1e-5)


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([log_loss(y[:, j], clip(pred[:, j]), labels=[0, 1]) for j in range(y.shape[1])]))


def per_target_loss(y: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    return {target: log_loss(y[:, j], clip(pred[:, j]), labels=[0, 1]) for j, target in enumerate(TARGETS)}


def safe_name(text: str) -> str:
    return re.sub(r"[^0-9A-Za-z_]+", "_", text)[:180]


def load_base() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train = sr.add_extra_features(pd.read_parquet(OUT / "train_deep_features.parquet"))
    sub = sr.add_extra_features(pd.read_parquet(OUT / "submission_deep_features.parquet"))
    train["__row_split"] = "train"
    sub["__row_split"] = "submission"
    both = pd.concat([train, sub], ignore_index=True, sort=False)
    return train.drop(columns=["__row_split"]), sub.drop(columns=["__row_split"]), both


def numeric_columns(df: pd.DataFrame) -> list[str]:
    out = []
    for c in df.columns:
        if c in BASE_EXCLUDE or c in {"dow", "month", "__row_split"}:
            continue
        if pd.api.types.is_numeric_dtype(df[c]):
            out.append(c)
    return out


def build_meta_features(force: bool = False) -> pd.DataFrame:
    path = OUT / "meta_sensor_features.parquet"
    if path.exists() and not force:
        return pd.read_parquet(path)

    _, _, both = load_base()
    cols = numeric_columns(both)
    meta = both[KEY].copy()
    X = both[cols].apply(pd.to_numeric, errors="coerce")
    n = len(X)
    new_cols: dict[str, pd.Series | np.ndarray] = {}

    missing_rate = X.isna().mean()
    for c in missing_rate[missing_rate > 0.01].index:
        new_cols[f"meta_miss__{safe_name(c)}"] = X[c].isna().astype(float)

    for prefix, prefix_cols in {
        "phone": [c for c in cols if c.startswith("phone_") or c.startswith("usage_")],
        "mobility": [c for c in cols if c.startswith(("gps_", "loc_", "wifi_", "ble_"))],
        "watch": [c for c in cols if c.startswith(("watch_", "hr_"))],
        "context": [c for c in cols if c.startswith("ambience_")],
        "light": [c for c in cols if "light" in c],
        "coverage": [c for c in cols if any(tok in c for tok in ["rows", "count", "points", "items"])],
    }.items():
        if not prefix_cols:
            continue
        block = X[prefix_cols]
        new_cols[f"meta_group_{prefix}_missing_frac"] = block.isna().mean(axis=1)
        new_cols[f"meta_group_{prefix}_nonnull_frac"] = block.notna().mean(axis=1)
        med = block.median(axis=0)
        std = block.std(axis=0).replace(0, np.nan)
        z = (block - med) / std
        new_cols[f"meta_group_{prefix}_abs_z_mean"] = z.abs().mean(axis=1)
        new_cols[f"meta_group_{prefix}_abs_z_max"] = z.abs().max(axis=1)

    # Nonlinear monotonic transforms for skewed nonnegative sensor counters.
    for c in cols:
        s = X[c]
        if s.notna().sum() < 50:
            continue
        minv = s.min(skipna=True)
        if pd.isna(minv) or minv < 0:
            continue
        skew = s.skew(skipna=True)
        name_hits = any(tok in c for tok in ["sum", "count", "rows", "points", "items", "time", "step", "distance", "calories"])
        if name_hits or (not pd.isna(skew) and abs(float(skew)) > 2.0):
            new_cols[f"meta_log1p__{safe_name(c)}"] = np.log1p(s.clip(lower=0))

    # Per-subject relative scale and within-subject ranks.
    grouped = both.groupby("subject_id", sort=False)
    candidate_cols = [c for c in cols if X[c].notna().sum() >= 120 and X[c].std(skipna=True) > 1e-9]
    for c in candidate_cols:
        s = X[c]
        mean = grouped[c].transform("mean")
        std = grouped[c].transform("std").replace(0, np.nan)
        z = (s - mean) / std
        new_cols[f"meta_subj_z__{safe_name(c)}"] = z
        new_cols[f"meta_subj_rank__{safe_name(c)}"] = grouped[c].rank(pct=True)

    # Window deltas and ratios: "late vs morning", "evening vs morning", etc.
    by_base: dict[str, dict[str, str]] = {}
    for c in cols:
        for win in WINDOWS:
            token = f"_{win}_"
            if token in c:
                base = c.replace(token, "_WIN_")
                by_base.setdefault(base, {})[win] = c
                break
    for base, win_cols in by_base.items():
        pairs = [("late", "morning"), ("late", "all"), ("evening", "morning"), ("early", "late"), ("afternoon", "morning")]
        for a, b in pairs:
            if a not in win_cols or b not in win_cols:
                continue
            ca, cb = win_cols[a], win_cols[b]
            va = X[ca]
            vb = X[cb]
            new_cols[f"meta_delta_{a}_minus_{b}__{safe_name(base)}"] = va - vb
            denom = vb.abs() + 1e-3
            new_cols[f"meta_ratio_{a}_over_{b}__{safe_name(base)}"] = va / denom

    # Domain interactions, standardized to avoid scale dominance.
    interaction_pairs = [
        ("phone_screen_m_screen_use_late_mean", "phone_charge_m_charging_late_mean"),
        ("phone_screen_m_screen_use_late_mean", "phone_light_m_light_late_log_mean"),
        ("phone_screen_m_screen_use_evening_mean", "usage_evening_usage_kw_video_time_sum"),
        ("phone_screen_m_screen_use_late_mean", "usage_late_usage_kw_chat_time_sum"),
        ("phone_activity_late_transitions", "usage_late_time_sum_sum"),
        ("phone_activity_morning_transitions", "phone_light_m_light_morning_sum"),
        ("gps_late_speed_mean", "phone_screen_m_screen_use_late_mean"),
        ("gps_evening_speed_mean", "usage_evening_time_sum_sum"),
        ("loc_late_home_frac", "phone_screen_m_screen_use_late_mean"),
        ("loc_evening_home_frac", "usage_evening_usage_kw_chat_time_sum"),
        ("wifi_late_unique_mean", "ble_late_unique_mean"),
        ("wifi_late_home_id_frac", "ble_late_home_id_frac"),
        ("hr_early_rows", "loc_early_home_frac"),
        ("hr_late_rows", "phone_charge_m_charging_late_mean"),
        ("hr_early_std_mean", "ambience_evening_top_is_outside_sum"),
        ("watch_pedo_step_late_sum", "phone_screen_m_screen_use_late_mean"),
        ("watch_light_w_light_late_log_mean", "phone_screen_m_screen_use_late_mean"),
        ("ambience_late_top_is_speech_sum", "usage_late_usage_kw_call_time_sum"),
        ("ambience_evening_top_is_outside_sum", "loc_evening_home_frac"),
    ]
    for a, b in interaction_pairs:
        if a not in X.columns or b not in X.columns:
            continue
        za = (X[a] - X[a].median()) / (X[a].std() or np.nan)
        zb = (X[b] - X[b].median()) / (X[b].std() or np.nan)
        new_cols[f"meta_inter__{safe_name(a)}__x__{safe_name(b)}"] = za * zb

    meta = pd.concat([meta, pd.DataFrame(new_cols, index=both.index)], axis=1)
    assert len(meta) == n
    meta.to_parquet(path, index=False)
    return meta


def prepare(force_meta: bool = False) -> tuple[pd.DataFrame, pd.DataFrame]:
    train, sub, _ = load_base()
    meta = build_meta_features(force=force_meta)
    train = train.merge(meta, on=KEY, how="left")
    sub = sub.merge(meta, on=KEY, how="left")
    return train, sub


def select_cols(df: pd.DataFrame, group: str) -> list[str]:
    base = ["subject_id", "dow", "month", "day", "weekofyear", "subject_day_index", "is_weekend"]
    tokens = {
        "meta_phone": ("phone_", "usage_", "meta_", "screen", "charge", "activity"),
        "meta_mobility": ("gps_", "loc_", "wifi_", "ble_", "meta_"),
        "meta_watch": ("watch_", "hr_", "meta_"),
        "meta_all": ("meta_", "phone_", "usage_", "gps_", "loc_", "wifi_", "ble_", "watch_", "hr_", "ambience_"),
    }[group]
    cols = []
    for c in df.columns:
        if c in BASE_EXCLUDE:
            continue
        if c in base or any(tok in c for tok in tokens):
            cols.append(c)
    # Avoid letting every meta feature enter narrow groups; keep group-specific meta by token.
    if group == "meta_phone":
        cols = [c for c in cols if c in base or any(tok in c for tok in ["phone", "usage", "screen", "charge", "activity", "light", "group_phone", "group_light", "inter"])]
    elif group == "meta_mobility":
        cols = [c for c in cols if c in base or any(tok in c for tok in ["gps", "loc", "wifi", "ble", "mobility", "home", "group_mobility", "inter"])]
    elif group == "meta_watch":
        cols = [c for c in cols if c in base or any(tok in c for tok in ["watch", "hr", "pedo", "group_watch", "coverage", "inter"])]
    return list(dict.fromkeys(cols))


def make_pipe(cols: list[str]) -> Pipeline:
    cat_cols = [c for c in cols if c in {"subject_id", "dow", "month"}]
    num_cols = [c for c in cols if c not in cat_cols]
    pre = ColumnTransformer(
        [
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
            ("num", SimpleImputer(strategy="median"), num_cols),
        ],
        sparse_threshold=0.2,
    )
    clf = ExtraTreesClassifier(
        n_estimators=220,
        min_samples_leaf=8,
        max_features=0.25,
        random_state=52525,
        n_jobs=-1,
    )
    return Pipeline([("pre", pre), ("clf", clf)])


def fit_predict(train_rows: pd.DataFrame, val_rows: pd.DataFrame, group: str) -> np.ndarray:
    cols = select_cols(train_rows, group)
    pipe = make_pipe(cols)
    pipe.fit(train_rows[cols], train_rows[TARGETS])
    probas = pipe.predict_proba(val_rows[cols])
    pred = np.zeros((len(val_rows), len(TARGETS)), dtype=float)
    for j, proba in enumerate(probas):
        classes = list(pipe.named_steps["clf"].classes_[j])
        pred[:, j] = proba[:, classes.index(1)] if 1 in classes else 0.0
    return clip(pred)


def fixed_blend(base: np.ndarray, phone: np.ndarray, mobility: np.ndarray) -> np.ndarray:
    pred = base.copy()
    for target, (source, weight) in FIXED.items():
        j = TARGETS.index(target)
        sensor = phone if source == "phone" else mobility
        pred[:, j] = (1 - weight) * base[:, j] + weight * sensor[:, j]
    return clip(pred)


def evaluate(train: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    y = train[TARGETS].to_numpy()
    folds = d.make_folds(train, "subject_blocks")
    preds = {
        "temporal_base": np.zeros_like(y, dtype=float),
        "current_missing": np.zeros_like(y, dtype=float),
        "meta_fixed": np.zeros_like(y, dtype=float),
        "meta_all_fixed": np.zeros_like(y, dtype=float),
    }
    sensor_preds = {
        "meta_phone": np.zeros_like(y, dtype=float),
        "meta_mobility": np.zeros_like(y, dtype=float),
        "meta_watch": np.zeros_like(y, dtype=float),
        "meta_all": np.zeros_like(y, dtype=float),
    }
    for fold_id, (tr_idx, val_idx) in enumerate(folds):
        tr = train.iloc[tr_idx].copy().reset_index(drop=True)
        val = train.iloc[val_idx].copy().reset_index(drop=True)
        base = cal.temporal_base(tr, val)
        cur_phone = sfv.fit_sensor_predict_variant(tr, val, "phone", "missing")
        cur_mob = sfv.fit_sensor_predict_variant(tr, val, "mobility", "missing")
        meta_phone = fit_predict(tr, val, "meta_phone")
        meta_mob = fit_predict(tr, val, "meta_mobility")
        meta_watch = fit_predict(tr, val, "meta_watch")
        meta_all = fit_predict(tr, val, "meta_all")
        preds["temporal_base"][val_idx] = base
        preds["current_missing"][val_idx] = fixed_blend(base, cur_phone, cur_mob)
        preds["meta_fixed"][val_idx] = fixed_blend(base, meta_phone, meta_mob)
        preds["meta_all_fixed"][val_idx] = fixed_blend(base, meta_all, meta_all)
        sensor_preds["meta_phone"][val_idx] = meta_phone
        sensor_preds["meta_mobility"][val_idx] = meta_mob
        sensor_preds["meta_watch"][val_idx] = meta_watch
        sensor_preds["meta_all"][val_idx] = meta_all
        print(f"[meta] fold {fold_id}", flush=True)

    rows = []
    for name, pred in preds.items():
        row = {"experiment": "fixed_blend", "model": name, "mean": mean_loss(y, pred)}
        row.update(per_target_loss(y, pred))
        rows.append(row)
    for name, pred in sensor_preds.items():
        row = {"experiment": "sensor_only", "model": name, "mean": mean_loss(y, pred)}
        row.update(per_target_loss(y, pred))
        rows.append(row)
    return pd.DataFrame(rows).sort_values("mean"), {**preds, **sensor_preds}


def make_submission(train: pd.DataFrame, sub: pd.DataFrame, model: str) -> pd.DataFrame:
    base = cal.temporal_base(train, sub)
    if model == "current_missing":
        phone = sfv.fit_sensor_predict_variant(train, sub, "phone", "missing")
        mobility = sfv.fit_sensor_predict_variant(train, sub, "mobility", "missing")
    elif model == "meta_fixed":
        phone = fit_predict(train, sub, "meta_phone")
        mobility = fit_predict(train, sub, "meta_mobility")
    elif model == "meta_all_fixed":
        all_pred = fit_predict(train, sub, "meta_all")
        phone = all_pred
        mobility = all_pred
    else:
        raise ValueError(model)
    pred = fixed_blend(base, phone, mobility)
    out = sub[["subject_id", "sleep_date", "lifelog_date"]].copy()
    for j, target in enumerate(TARGETS):
        out[target] = pred[:, j]
    return out


def main() -> None:
    train, sub = prepare(force_meta=False)
    meta = pd.read_parquet(OUT / "meta_sensor_features.parquet")
    results, _ = evaluate(train)
    results.to_csv(OUT / "meta_feature_results.csv", index=False)
    best = results[results["experiment"] == "fixed_blend"].sort_values("mean").iloc[0]
    best_model = str(best["model"])
    submission = make_submission(train, sub, best_model)
    submission.to_csv(OUT / f"submission_meta_{best_model}.csv", index=False)
    if float(best["mean"]) < 0.6228411063084949:
        submission.to_csv(OUT / "submission_best.csv", index=False)
    summary = {
        "meta_rows": len(meta),
        "meta_columns": int(meta.shape[1] - len(KEY)),
        "best_model": best_model,
        "best_mean": float(best["mean"]),
    }
    pd.DataFrame([summary]).to_csv(OUT / "meta_feature_summary.csv", index=False)
    print("\nMeta feature summary")
    print(pd.DataFrame([summary]).to_string(index=False))
    print("\nMeta feature results")
    print(results.round(5).to_string(index=False))


if __name__ == "__main__":
    main()
