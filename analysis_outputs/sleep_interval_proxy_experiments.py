from __future__ import annotations

import sys
import warnings
from functools import reduce
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
import deep_dive_analysis as d  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ITEMS = DATA / "ch2025_data_items"
OUT = ROOT / "analysis_outputs"
TARGETS = d.TARGETS
KEY = d.KEY
NIGHT_START = 18 * 60
NIGHT_END = 36 * 60
CAND_START = 21 * 60
CAND_END = 34 * 60


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1 - 1e-5)


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    return float(log_loss(y.astype(int), clip(p), labels=[0, 1]))


def add_night_min(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["timestamp"] = pd.to_datetime(out["timestamp"])
    hour = out["timestamp"].dt.hour
    minute = out["timestamp"].dt.minute
    base = out["timestamp"].dt.normalize()
    out["lifelog_date"] = np.where(hour < 12, base - pd.Timedelta(days=1), base)
    out["lifelog_date"] = pd.to_datetime(out["lifelog_date"])
    out["night_minute"] = np.where(hour < 12, (hour + 24) * 60 + minute, hour * 60 + minute).astype(int)
    return out[(out["night_minute"] >= NIGHT_START) & (out["night_minute"] < NIGHT_END)].copy()


def minute_numeric(file_name: str, cols: list[str], agg: str = "mean") -> pd.DataFrame:
    df = add_night_min(pd.read_parquet(ITEMS / file_name))
    grouped = df.groupby(KEY + ["night_minute"], as_index=False)[cols]
    if agg == "sum":
        return grouped.sum()
    return grouped.mean()


def minute_hr() -> pd.DataFrame:
    df = add_night_min(pd.read_parquet(ITEMS / "ch2025_wHr.parquet"))

    def stats(x):
        arr = np.asarray(x, dtype=float)
        if arr.size == 0:
            return (np.nan, np.nan, np.nan, 0.0)
        return (float(np.nanmean(arr)), float(np.nanmin(arr)), float(np.nanstd(arr)), float(arr.size))

    rows = pd.DataFrame(df["heart_rate"].map(stats).tolist(), columns=["hr_mean", "hr_min", "hr_std", "hr_points"])
    df = pd.concat([df[KEY + ["night_minute"]].reset_index(drop=True), rows], axis=1)
    return df.groupby(KEY + ["night_minute"], as_index=False).mean()


def build_minute_table() -> pd.DataFrame:
    blocks = [
        minute_numeric("ch2025_mScreenStatus.parquet", ["m_screen_use"]),
        minute_numeric("ch2025_mACStatus.parquet", ["m_charging"]),
        minute_numeric("ch2025_mActivity.parquet", ["m_activity"]),
        minute_numeric("ch2025_wPedo.parquet", ["step", "speed", "distance", "burned_calories"], agg="sum"),
        minute_numeric("ch2025_wLight.parquet", ["w_light"]),
        minute_numeric("ch2025_mLight.parquet", ["m_light"]),
        minute_hr(),
    ]
    return reduce(lambda left, right: left.merge(right, on=KEY + ["night_minute"], how="outer"), blocks)


def longest_run(mask: np.ndarray, minutes: np.ndarray) -> tuple[float, float, float]:
    idx = np.where(mask)[0]
    if idx.size == 0:
        return (np.nan, np.nan, 0.0)
    best_start = int(idx[0])
    best_end = int(idx[0])
    cur_start = int(idx[0])
    prev = int(idx[0])
    for pos in idx[1:]:
        pos = int(pos)
        if pos == prev + 1:
            prev = pos
            continue
        if prev - cur_start > best_end - best_start:
            best_start, best_end = cur_start, prev
        cur_start = prev = pos
    if prev - cur_start > best_end - best_start:
        best_start, best_end = cur_start, prev
    start = float(minutes[best_start])
    end = float(minutes[best_end] + 1)
    return (start, end, end - start)


def window_stats(arr: np.ndarray, minutes: np.ndarray, lo: float, hi: float, prefix: str) -> dict[str, float]:
    mask = (minutes >= lo) & (minutes < hi)
    vals = arr[mask]
    vals = vals[~np.isnan(vals)]
    if vals.size == 0:
        return {
            f"{prefix}_mean": np.nan,
            f"{prefix}_sum": np.nan,
            f"{prefix}_max": np.nan,
            f"{prefix}_obs": 0.0,
        }
    return {
        f"{prefix}_mean": float(np.mean(vals)),
        f"{prefix}_sum": float(np.sum(vals)),
        f"{prefix}_max": float(np.max(vals)),
        f"{prefix}_obs": float(vals.size),
    }


def safe_array(g: pd.DataFrame, col: str, default: float = np.nan) -> np.ndarray:
    arr = np.full(NIGHT_END - NIGHT_START, default, dtype=float)
    if col not in g:
        return arr
    idx = g["night_minute"].to_numpy(dtype=int) - NIGHT_START
    vals = g[col].to_numpy(dtype=float)
    ok = (idx >= 0) & (idx < len(arr))
    arr[idx[ok]] = vals[ok]
    return arr


def row_features(sid: str, day: pd.Timestamp, g: pd.DataFrame) -> dict[str, float | str | pd.Timestamp]:
    minutes = np.arange(NIGHT_START, NIGHT_END, dtype=float)
    screen = safe_array(g, "m_screen_use")
    charge = safe_array(g, "m_charging")
    activity = safe_array(g, "m_activity")
    step = safe_array(g, "step", 0.0)
    speed = safe_array(g, "speed", 0.0)
    w_light = safe_array(g, "w_light")
    m_light = safe_array(g, "m_light")
    hr_mean = safe_array(g, "hr_mean")
    hr_min = safe_array(g, "hr_min")

    screen_off = np.nan_to_num(screen, nan=0.0) <= 0.0
    no_steps = np.nan_to_num(step, nan=0.0) <= 0.0
    low_speed = np.nan_to_num(speed, nan=0.0) <= 0.01
    activity_stillish = np.isin(np.nan_to_num(activity, nan=3.0).round().astype(int), [0, 3])
    cand = (minutes >= CAND_START) & (minutes < CAND_END)
    variants = {
        "screen": screen_off & cand,
        "screen_step": screen_off & no_steps & cand,
        "screen_step_speed": screen_off & no_steps & low_speed & cand,
        "screen_step_activity": screen_off & no_steps & activity_stillish & cand,
    }
    out: dict[str, float | str | pd.Timestamp] = {"subject_id": sid, "lifelog_date": day}
    out["proxy_screen_obs_frac"] = float(np.isfinite(screen).mean())
    out["proxy_step_obs_frac"] = float(np.isfinite(step).mean())
    out["proxy_hr_obs_frac"] = float(np.isfinite(hr_mean).mean())
    out["proxy_watch_light_obs_frac"] = float(np.isfinite(w_light).mean())

    active_screen = np.where((np.nan_to_num(screen, nan=0.0) > 0) & cand)[0]
    out["proxy_last_screen_on_candidate_hour"] = (
        float(minutes[active_screen[-1]] / 60.0) if active_screen.size else np.nan
    )
    out["proxy_first_screen_on_candidate_hour"] = (
        float(minutes[active_screen[0]] / 60.0) if active_screen.size else np.nan
    )
    out["proxy_screen_on_candidate_minutes"] = float(active_screen.size)
    out["proxy_step_candidate_sum"] = float(np.nansum(step[cand]))
    out["proxy_light_candidate_mean"] = float(np.nanmean(w_light[cand])) if np.isfinite(w_light[cand]).any() else np.nan

    for name, mask in variants.items():
        start, end, duration = longest_run(mask, minutes)
        out[f"proxy_{name}_start_hour"] = start / 60.0 if np.isfinite(start) else np.nan
        out[f"proxy_{name}_end_hour"] = end / 60.0 if np.isfinite(end) else np.nan
        out[f"proxy_{name}_duration_min"] = duration
        out[f"proxy_{name}_mid_hour"] = (start + end) / 120.0 if np.isfinite(start) else np.nan
        if np.isfinite(start):
            pre_lo = max(NIGHT_START, start - 120)
            post_hi = min(NIGHT_END, end + 120)
            core = (minutes >= start) & (minutes < end)
            out[f"proxy_{name}_charge_frac"] = float(np.nanmean(np.nan_to_num(charge[core], nan=0.0))) if core.any() else np.nan
            out[f"proxy_{name}_screen_on_core_min"] = float(np.nansum(np.nan_to_num(screen[core], nan=0.0)))
            out[f"proxy_{name}_step_core_sum"] = float(np.nansum(step[core]))
            out[f"proxy_{name}_hr_mean"] = float(np.nanmean(hr_mean[core])) if np.isfinite(hr_mean[core]).any() else np.nan
            out[f"proxy_{name}_hr_min"] = float(np.nanmin(hr_min[core])) if np.isfinite(hr_min[core]).any() else np.nan
            out.update(window_stats(screen, minutes, pre_lo, start, f"proxy_{name}_pre2h_screen"))
            out.update(window_stats(step, minutes, pre_lo, start, f"proxy_{name}_pre2h_step"))
            out.update(window_stats(w_light, minutes, pre_lo, start, f"proxy_{name}_pre2h_wlight"))
            out.update(window_stats(m_light, minutes, pre_lo, start, f"proxy_{name}_pre2h_mlight"))
            out.update(window_stats(screen, minutes, end, post_hi, f"proxy_{name}_post2h_screen"))
            out.update(window_stats(step, minutes, end, post_hi, f"proxy_{name}_post2h_step"))
            out.update(window_stats(w_light, minutes, end, post_hi, f"proxy_{name}_post2h_wlight"))
            out[f"proxy_{name}_duration_x_charge"] = float(duration * out[f"proxy_{name}_charge_frac"])
            out[f"proxy_{name}_late_start_excess"] = float(max(0.0, start - 24 * 60.0))
        else:
            for suffix in [
                "charge_frac",
                "screen_on_core_min",
                "step_core_sum",
                "hr_mean",
                "hr_min",
                "duration_x_charge",
                "late_start_excess",
            ]:
                out[f"proxy_{name}_{suffix}"] = np.nan
    return out


def build_proxy_features() -> pd.DataFrame:
    path = OUT / "sleep_interval_proxy_features.parquet"
    if path.exists():
        return pd.read_parquet(path)
    train, sub, all_keys = d.read_labels()
    all_keys = all_keys[KEY].drop_duplicates().sort_values(KEY).reset_index(drop=True)
    minute = build_minute_table()
    grouped = {k: v for k, v in minute.groupby(KEY, sort=False)}
    rows = []
    for row in all_keys.itertuples(index=False):
        key = (row.subject_id, row.lifelog_date)
        rows.append(row_features(str(row.subject_id), pd.Timestamp(row.lifelog_date), grouped.get(key, pd.DataFrame())))
    out = pd.DataFrame(rows)
    out.to_parquet(path, index=False)
    return out


def prepare_frames() -> tuple[pd.DataFrame, pd.DataFrame]:
    train = pd.read_parquet(OUT / "train_deep_features.parquet")
    sub = pd.read_parquet(OUT / "submission_deep_features.parquet")
    proxy = build_proxy_features()
    train = train[KEY + ["sleep_date", "split", "dow", "month", "day", "weekofyear", "subject_day_index", "is_weekend"] + TARGETS]
    sub = sub[KEY + ["sleep_date", "split", "dow", "month", "day", "weekofyear", "subject_day_index", "is_weekend"]]
    train = train.merge(proxy, on=KEY, how="left").sort_values(KEY).reset_index(drop=True)
    sub = sub.merge(proxy, on=KEY, how="left").sort_values(KEY).reset_index(drop=True)
    return train, sub


def feature_columns(rows: pd.DataFrame) -> list[str]:
    excluded = set(TARGETS + KEY + ["sleep_date", "split"])
    cols = [c for c in rows.columns if c not in excluded]
    return cols


def make_pipe(cols: list[str]) -> Pipeline:
    cat = [c for c in cols if c in {"subject_id", "dow", "month"}]
    num = [c for c in cols if c not in cat]
    pre = ColumnTransformer(
        [
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat),
            ("num", SimpleImputer(strategy="median"), num),
        ],
        sparse_threshold=0.2,
    )
    clf = ExtraTreesClassifier(
        n_estimators=320,
        min_samples_leaf=6,
        max_features=0.45,
        random_state=260526,
        n_jobs=-1,
    )
    return Pipeline([("pre", pre), ("clf", clf)])


def proba_matrix(pipe: Pipeline, rows: pd.DataFrame, cols: list[str]) -> np.ndarray:
    probas = pipe.predict_proba(rows[cols])
    classes = pipe.named_steps["clf"].classes_
    out = np.zeros((len(rows), len(TARGETS)), dtype=float)
    for j, proba in enumerate(probas):
        if proba.shape[1] == 1:
            out[:, j] = float(classes[j][0] == 1)
        else:
            out[:, j] = proba[:, list(classes[j]).index(1)]
    return clip(out)


def fit_predict(train_rows: pd.DataFrame, rows: pd.DataFrame) -> np.ndarray:
    cols = feature_columns(train_rows)
    pipe = make_pipe(cols)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        pipe.fit(train_rows[cols], train_rows[TARGETS])
    return proba_matrix(pipe, rows, cols)


def oof_proxy(train: pd.DataFrame) -> np.ndarray:
    pred = np.zeros((len(train), len(TARGETS)), dtype=float)
    for fold_id, (tr_idx, val_idx) in enumerate(d.make_folds(train, "subject_blocks")):
        pred[val_idx] = fit_predict(train.iloc[tr_idx].copy(), train.iloc[val_idx].copy())
        print(f"[sleep proxy] fold={fold_id}", flush=True)
    return clip(pred)


def evaluate(train: pd.DataFrame, proxy_pred: np.ndarray) -> tuple[pd.DataFrame, pd.DataFrame]:
    current = np.load(OUT / "final_hybrid_0p598_repro_oof.npy")
    y = train[TARGETS].to_numpy(dtype=int)
    grid = np.array([0.0, 0.02, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30, 0.45, 0.60, 0.80, 1.00])
    rows = []
    select_rows = []
    first_subjects = set(sorted(train["subject_id"].unique())[:5])
    select_mask = train["subject_id"].isin(first_subjects).to_numpy()
    hold_mask = ~select_mask
    for j, target in enumerate(TARGETS):
        base_loss = loss_col(y[:, j], current[:, j])
        proxy_loss = loss_col(y[:, j], proxy_pred[:, j])
        losses = []
        for w in grid:
            p = (1.0 - w) * current[:, j] + w * proxy_pred[:, j]
            losses.append(loss_col(y[:, j], p))
        best_i = int(np.argmin(losses))
        best_w = float(grid[best_i])
        best_loss = float(losses[best_i])
        sel_best = None
        for w in grid:
            p = (1.0 - w) * current[:, j] + w * proxy_pred[:, j]
            sel_loss = loss_col(y[select_mask, j], p[select_mask])
            if sel_best is None or sel_loss < sel_best[0]:
                sel_best = (sel_loss, float(w), p)
        assert sel_best is not None
        rows.append(
            {
                "target": target,
                "current_loss": base_loss,
                "proxy_loss": proxy_loss,
                "best_blend_weight": best_w,
                "best_blend_loss": best_loss,
                "delta_vs_current": best_loss - base_loss,
            }
        )
        select_rows.append(
            {
                "target": target,
                "selected_weight": sel_best[1],
                "select_loss": sel_best[0],
                "holdout_current_loss": loss_col(y[hold_mask, j], current[hold_mask, j]),
                "holdout_proxyblend_loss": loss_col(y[hold_mask, j], sel_best[2][hold_mask]),
            }
        )
    return pd.DataFrame(rows), pd.DataFrame(select_rows)


def make_submission(train: pd.DataFrame, sub: pd.DataFrame, summary: pd.DataFrame) -> pd.DataFrame:
    base = pd.read_csv(OUT / "submission_hybrid_0p598_repro.csv", parse_dates=["sleep_date", "lifelog_date"])
    base = base.sort_values(KEY).reset_index(drop=True)
    proxy_sub = fit_predict(train.copy(), sub.copy())
    for row in summary.itertuples(index=False):
        if float(row.delta_vs_current) < -0.002 and float(row.best_blend_weight) > 0:
            j = TARGETS.index(str(row.target))
            w = float(row.best_blend_weight)
            base[str(row.target)] = clip((1.0 - w) * base[str(row.target)].to_numpy(dtype=float) + w * proxy_sub[:, j])
    base[TARGETS] = base[TARGETS].clip(1e-5, 1 - 1e-5)
    base.to_csv(OUT / "submission_hybrid_0p598_sleep_proxy.csv", index=False)
    return base


def main() -> None:
    train, sub = prepare_frames()
    proxy_pred = oof_proxy(train)
    np.save(OUT / "sleep_interval_proxy_oof.npy", proxy_pred)
    summary, guardrail = evaluate(train, proxy_pred)
    summary.to_csv(OUT / "sleep_interval_proxy_results.csv", index=False)
    guardrail.to_csv(OUT / "sleep_interval_proxy_half_subject_holdout.csv", index=False)
    out = make_submission(train, sub, summary)
    print(summary.round(6).to_string(index=False))
    print("\nHalf-subject guardrail")
    print(guardrail.round(6).to_string(index=False))
    print("wrote", OUT / "submission_hybrid_0p598_sleep_proxy.csv", out.shape)


if __name__ == "__main__":
    main()
