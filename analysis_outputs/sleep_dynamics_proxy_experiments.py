from __future__ import annotations

import sys
import warnings
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))
import deep_dive_analysis as d  # noqa: E402
import geometry_mask_cv_experiments as geom  # noqa: E402
import sleep_fragmentation_proxy_experiments as frag  # noqa: E402
import sleep_interval_proxy_experiments as sip  # noqa: E402
import sleep_interval_proxy_foldsafe_guardrail as fg  # noqa: E402


OUT = Path(__file__).resolve().parent
DATA = OUT.parents[0] / "data"
TARGETS = d.TARGETS
KEY = d.KEY
NIGHT_START = sip.NIGHT_START
NIGHT_END = sip.NIGHT_END
CAND_START = sip.CAND_START
CAND_END = sip.CAND_END
BASE_OOF = OUT / "final_hybrid_0p592_sleep_fragment_s1_q3_oof.npy"


@dataclass(frozen=True)
class ETConfig:
    name: str
    n_estimators: int
    min_samples_leaf: int
    max_features: float
    max_depth: int | None
    seed: int


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1 - 1e-5)


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    return frag.loss_col(y, p)


def safe_array(g: pd.DataFrame, col: str, default: float = np.nan) -> np.ndarray:
    return frag.safe_array(g, col, default)


def finite_mean(arr: np.ndarray, mask: np.ndarray) -> float:
    vals = arr[mask]
    vals = vals[np.isfinite(vals)]
    return float(vals.mean()) if vals.size else np.nan


def finite_min(arr: np.ndarray, mask: np.ndarray) -> float:
    vals = arr[mask]
    vals = vals[np.isfinite(vals)]
    return float(vals.min()) if vals.size else np.nan


def finite_sum(arr: np.ndarray, mask: np.ndarray) -> float:
    vals = arr[mask]
    vals = vals[np.isfinite(vals)]
    return float(vals.sum()) if vals.size else np.nan


def burst_count(mask: np.ndarray) -> float:
    return float(len(frag.runs(mask)))


def first_after(minutes: np.ndarray, mask: np.ndarray, start: int) -> float:
    idx = np.where(mask & (np.arange(mask.size) >= start))[0]
    if idx.size == 0:
        return np.nan
    return float(minutes[idx[0]] - minutes[start])


def longest_bounds(mask: np.ndarray) -> tuple[int | None, int | None]:
    rs = frag.runs(mask)
    if not rs:
        return None, None
    lengths = np.array([end - start for start, end in rs], dtype=float)
    return rs[int(np.argmax(lengths))]


def row_features(sid: str, day: pd.Timestamp, g: pd.DataFrame) -> dict[str, float | str | pd.Timestamp]:
    minutes = np.arange(NIGHT_START, NIGHT_END, dtype=float)
    screen = safe_array(g, "m_screen_use")
    step = safe_array(g, "step", 0.0)
    speed = safe_array(g, "speed", 0.0)
    activity = safe_array(g, "m_activity")
    charge = safe_array(g, "m_charging")
    hr_mean = safe_array(g, "hr_mean")
    hr_min = safe_array(g, "hr_min")
    hr_points = safe_array(g, "hr_points", 0.0)
    w_light = safe_array(g, "w_light")
    m_light = safe_array(g, "m_light")

    screen_off = np.nan_to_num(screen, nan=0.0) <= 0.0
    no_steps = np.nan_to_num(step, nan=0.0) <= 0.0
    low_speed = np.nan_to_num(speed, nan=0.0) <= 0.01
    stillish = np.isin(np.nan_to_num(activity, nan=3.0).round().astype(int), [0, 3])
    cand = (minutes >= CAND_START) & (minutes < CAND_END)
    variants = {
        "screen": screen_off & cand,
        "screen_step": screen_off & no_steps & cand,
        "screen_step_speed": screen_off & no_steps & low_speed & cand,
        "screen_step_activity": screen_off & no_steps & stillish & cand,
    }
    active = cand & ((np.nan_to_num(screen, nan=0.0) > 0) | (np.nan_to_num(step, nan=0.0) > 0) | (np.nan_to_num(speed, nan=0.0) > 0.01))
    out: dict[str, float | str | pd.Timestamp] = {"subject_id": sid, "lifelog_date": day}

    for name, mask in variants.items():
        prefix = f"proxy_dyn_{name}"
        start, end = longest_bounds(mask)
        if start is None or end is None:
            for suffix in [
                "duration_min",
                "start_hour",
                "end_hour",
                "mid_hour",
                "hr_mean_core",
                "hr_min_core",
                "hr_mean_pre120",
                "hr_mean_post120",
                "hr_drop_pre_to_min",
                "hr_drop_candidate_to_min",
                "hr_rebound_post_to_min",
                "hr_core_late_minus_early",
                "hr_points_core",
                "wake_after60_screen_on_core_min",
                "wake_after60_step_core_sum",
                "wake_after60_active_burst_count",
                "wake_after120_screen_on_core_min",
                "wake_after120_step_core_sum",
                "wake_after120_active_burst_count",
                "first_activity_after_min",
                "first_screen_after_min",
                "first_step_after_min",
                "post120_wlight_mean",
                "post120_mlight_mean",
                "charge_frac",
            ]:
                out[f"{prefix}_{suffix}"] = np.nan
            continue

        core = np.zeros_like(cand, dtype=bool)
        core[start:end] = True
        pre120 = (np.arange(len(minutes)) >= max(0, start - 120)) & (np.arange(len(minutes)) < start)
        post120 = (np.arange(len(minutes)) >= end) & (np.arange(len(minutes)) < min(len(minutes), end + 120))
        post60 = (np.arange(len(minutes)) >= end) & (np.arange(len(minutes)) < min(len(minutes), end + 60))
        first30 = (np.arange(len(minutes)) >= start) & (np.arange(len(minutes)) < min(end, start + 30))
        last30 = (np.arange(len(minutes)) >= max(start, end - 30)) & (np.arange(len(minutes)) < end)
        duration = float(end - start)
        active_post60 = active & post60
        active_post120 = active & post120
        screen_post60 = post60 & (np.nan_to_num(screen, nan=0.0) > 0)
        screen_post120 = post120 & (np.nan_to_num(screen, nan=0.0) > 0)
        step_post60 = post60 & (np.nan_to_num(step, nan=0.0) > 0)
        step_post120 = post120 & (np.nan_to_num(step, nan=0.0) > 0)

        hr_pre = finite_mean(hr_mean, pre120)
        hr_candidate = finite_mean(hr_mean, cand)
        hr_core_mean = finite_mean(hr_mean, core)
        hr_core_min = finite_min(hr_min, core)
        hr_post = finite_mean(hr_mean, post120)
        out[f"{prefix}_duration_min"] = duration
        out[f"{prefix}_start_hour"] = float(minutes[start] / 60.0)
        out[f"{prefix}_end_hour"] = float(minutes[end - 1] / 60.0)
        out[f"{prefix}_mid_hour"] = float((minutes[start] + minutes[end - 1]) / 120.0)
        out[f"{prefix}_hr_mean_core"] = hr_core_mean
        out[f"{prefix}_hr_min_core"] = hr_core_min
        out[f"{prefix}_hr_mean_pre120"] = hr_pre
        out[f"{prefix}_hr_mean_post120"] = hr_post
        out[f"{prefix}_hr_drop_pre_to_min"] = hr_pre - hr_core_min if np.isfinite(hr_pre) and np.isfinite(hr_core_min) else np.nan
        out[f"{prefix}_hr_drop_candidate_to_min"] = hr_candidate - hr_core_min if np.isfinite(hr_candidate) and np.isfinite(hr_core_min) else np.nan
        out[f"{prefix}_hr_rebound_post_to_min"] = hr_post - hr_core_min if np.isfinite(hr_post) and np.isfinite(hr_core_min) else np.nan
        out[f"{prefix}_hr_core_late_minus_early"] = finite_mean(hr_mean, last30) - finite_mean(hr_mean, first30)
        out[f"{prefix}_hr_points_core"] = finite_sum(hr_points, core)
        out[f"{prefix}_wake_after60_screen_on_core_min"] = float(screen_post60.sum())
        out[f"{prefix}_wake_after60_step_core_sum"] = finite_sum(step, post60)
        out[f"{prefix}_wake_after60_active_burst_count"] = burst_count(active_post60)
        out[f"{prefix}_wake_after120_screen_on_core_min"] = float(screen_post120.sum())
        out[f"{prefix}_wake_after120_step_core_sum"] = finite_sum(step, post120)
        out[f"{prefix}_wake_after120_active_burst_count"] = burst_count(active_post120)
        out[f"{prefix}_first_activity_after_min"] = first_after(minutes, active, end)
        out[f"{prefix}_first_screen_after_min"] = first_after(minutes, np.nan_to_num(screen, nan=0.0) > 0, end)
        out[f"{prefix}_first_step_after_min"] = first_after(minutes, np.nan_to_num(step, nan=0.0) > 0, end)
        out[f"{prefix}_post120_wlight_mean"] = finite_mean(w_light, post120)
        out[f"{prefix}_post120_mlight_mean"] = finite_mean(m_light, post120)
        out[f"{prefix}_charge_frac"] = finite_mean(charge, core)
    return out


def add_regularities(base: pd.DataFrame) -> pd.DataFrame:
    out = base.sort_values(KEY).reset_index(drop=True).copy()
    cols = [
        col
        for col in out.columns
        if col.startswith("proxy_dyn_")
        and out[col].dtype.kind in "if"
        and any(key in col for key in ["duration_min", "start_hour", "end_hour", "hr_drop", "hr_rebound", "wake_after", "first_activity_after"])
    ]
    sorted_out = out.sort_values(KEY)
    additions: dict[str, pd.Series] = {}
    for col in cols:
        grp = sorted_out.groupby("subject_id", sort=False)[col]
        mean = grp.transform("mean")
        std = grp.transform("std").replace(0, np.nan)
        additions[f"{col}_subj_center"] = sorted_out[col] - mean
        additions[f"{col}_subj_z"] = (sorted_out[col] - mean) / std
        additions[f"{col}_subj_rank"] = grp.rank(pct=True)
        prev = grp.shift(1)
        nxt = grp.shift(-1)
        roll = grp.rolling(3, min_periods=1, center=True).mean().reset_index(level=0, drop=True)
        additions[f"{col}_prev_delta"] = sorted_out[col] - prev
        additions[f"{col}_next_delta"] = nxt - sorted_out[col]
        additions[f"{col}_neighbor_delta"] = sorted_out[col] - (prev + nxt) / 2.0
        additions[f"{col}_roll3_center_delta"] = sorted_out[col] - roll
    if additions:
        out = pd.concat([out, pd.DataFrame(additions, index=out.index)], axis=1)
    return out.copy()


def build_dynamic_features() -> pd.DataFrame:
    path = OUT / "sleep_dynamics_proxy_features.parquet"
    if path.exists():
        return pd.read_parquet(path)
    _, _, all_keys = d.read_labels()
    all_keys = all_keys[KEY].drop_duplicates().sort_values(KEY).reset_index(drop=True)
    minute = sip.build_minute_table()
    grouped = {k: v for k, v in minute.groupby(KEY, sort=False)}
    rows = []
    for row in all_keys.itertuples(index=False):
        key = (row.subject_id, row.lifelog_date)
        rows.append(row_features(str(row.subject_id), pd.Timestamp(row.lifelog_date), grouped.get(key, pd.DataFrame())))
    out = add_regularities(pd.DataFrame(rows))
    out.to_parquet(path, index=False)
    return out


def prepare_frames() -> tuple[pd.DataFrame, pd.DataFrame]:
    train, sub = frag.prepare_frames()
    dyn = build_dynamic_features()
    train = train.merge(dyn, on=KEY, how="left").sort_values(KEY).reset_index(drop=True)
    sub = sub.merge(dyn, on=KEY, how="left").sort_values(KEY).reset_index(drop=True)
    return train, sub


def feature_columns(rows: pd.DataFrame) -> list[str]:
    excluded = set(TARGETS + KEY + ["sleep_date", "split"])
    return [c for c in rows.columns if c not in excluded]


def configs() -> list[ETConfig]:
    return [
        ETConfig("dyn_leaf4_mf0.6_depth10", 560, 4, 0.60, 10, 260928),
        ETConfig("dyn_leaf6_mf0.8", 560, 6, 0.80, None, 260929),
        ETConfig("dyn_leaf10_mf0.6", 560, 10, 0.60, None, 260930),
        ETConfig("dyn_leaf3_mf0.35", 560, 3, 0.35, None, 260931),
    ]


def fit_predict(train_rows: pd.DataFrame, rows: pd.DataFrame, cfg: ETConfig) -> np.ndarray:
    cols = feature_columns(train_rows)
    pipe = frag.make_pipe(cols, frag.ETConfig(cfg.name, cfg.n_estimators, cfg.min_samples_leaf, cfg.max_features, cfg.max_depth, cfg.seed))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        pipe.fit(train_rows[cols], train_rows[TARGETS])
    return frag.proba_matrix(pipe, rows, cols)


def relative_source_cols(rows: pd.DataFrame) -> list[str]:
    base = fg.relative_source_cols(rows)
    dyn = [c for c in rows.columns if c.startswith("proxy_dyn_") and rows[c].dtype.kind in "if" and not any(x in c for x in ["neighbor", "prev_", "next_", "roll3"])]
    return sorted(set(base + dyn))


def oof_config(train: pd.DataFrame, cfg: ETConfig) -> np.ndarray:
    rel_cols = relative_source_cols(train)
    pred = np.zeros((len(train), len(TARGETS)), dtype=float)
    for fold_id, (tr_idx, val_idx) in enumerate(d.make_folds(train, "subject_blocks")):
        ref_raw = train.iloc[tr_idx].copy().reset_index(drop=True)
        val_raw = train.iloc[val_idx].copy().reset_index(drop=True)
        ref = fg.add_ref_relative_features(ref_raw, ref_raw, rel_cols)
        val = fg.add_ref_relative_features(val_raw, ref_raw, rel_cols)
        pred[val_idx] = fit_predict(ref, val, cfg)
        print(f"[dynamic proxy] {cfg.name} fold={fold_id}", flush=True)
    return clip(pred)


def summarize(train: pd.DataFrame, name: str, proxy: np.ndarray) -> pd.DataFrame:
    current = np.load(BASE_OOF)
    y = train[TARGETS].to_numpy(dtype=int)
    grid = np.array([0.0, 0.02, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30, 0.45, 0.60, 0.80, 1.00])
    rows = []
    for j, target in enumerate(TARGETS):
        base_loss = loss_col(y[:, j], current[:, j])
        losses = [loss_col(y[:, j], (1.0 - w) * current[:, j] + w * proxy[:, j]) for w in grid]
        best_i = int(np.argmin(losses))
        rows.append(
            {
                "config": name,
                "target": target,
                "current_loss": base_loss,
                "proxy_loss": loss_col(y[:, j], proxy[:, j]),
                "best_weight": float(grid[best_i]),
                "best_blend_loss": float(losses[best_i]),
                "delta_vs_current": float(losses[best_i] - base_loss),
            }
        )
    return pd.DataFrame(rows)


def subject_split_guardrail(train: pd.DataFrame, preds: dict[str, np.ndarray]) -> pd.DataFrame:
    current = np.load(BASE_OOF)
    y = train[TARGETS].to_numpy(dtype=int)
    subjects = np.array(sorted(train["subject_id"].unique()))
    grid = np.array([0.0, 0.02, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30, 0.45, 0.60, 0.80, 1.00])
    rng = np.random.default_rng(260932)
    rows = []
    for name, proxy in preds.items():
        for rep in range(160):
            sel_subjects = set(rng.choice(subjects, size=len(subjects) // 2, replace=False))
            sel_mask = train["subject_id"].isin(sel_subjects).to_numpy()
            hold_mask = ~sel_mask
            for j, target in enumerate(TARGETS):
                best = None
                for w in grid:
                    p = (1.0 - w) * current[:, j] + w * proxy[:, j]
                    sel = loss_col(y[sel_mask, j], p[sel_mask])
                    if best is None or sel < best[0]:
                        best = (sel, float(w), p)
                assert best is not None
                hold_current = loss_col(y[hold_mask, j], current[hold_mask, j])
                hold_blend = loss_col(y[hold_mask, j], best[2][hold_mask])
                rows.append(
                    {
                        "config": name,
                        "rep": rep,
                        "target": target,
                        "selected_weight": best[1],
                        "holdout_current": hold_current,
                        "holdout_blend": hold_blend,
                        "holdout_delta": hold_blend - hold_current,
                    }
                )
    detail = pd.DataFrame(rows)
    detail.to_csv(OUT / "sleep_dynamics_proxy_subject_split_guardrail_detail.csv", index=False)
    return (
        detail.groupby(["config", "target"])
        .agg(
            mean_delta=("holdout_delta", "mean"),
            median_delta=("holdout_delta", "median"),
            p25_delta=("holdout_delta", lambda x: float(np.quantile(x, 0.25))),
            p75_delta=("holdout_delta", lambda x: float(np.quantile(x, 0.75))),
            win_rate=("holdout_delta", lambda x: float((x < 0).mean())),
            mean_selected_weight=("selected_weight", "mean"),
            zero_weight_rate=("selected_weight", lambda x: float((x == 0).mean())),
        )
        .reset_index()
        .sort_values(["target", "mean_delta"])
    )


def geometry_guardrail(train: pd.DataFrame, cfg: ETConfig) -> pd.DataFrame:
    raw_train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    raw_sub = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    rel_cols = relative_source_cols(train)
    current = np.load(BASE_OOF)
    folds = geom.geometry_folds(raw_train, raw_sub, n_repeats=8)
    ys, bases, proxies = [], [], []
    for tr_idx, val_idx, fold_name in folds:
        ref_raw = train.iloc[tr_idx].copy().reset_index(drop=True)
        val_raw = train.iloc[val_idx].copy().reset_index(drop=True)
        ref = fg.add_ref_relative_features(ref_raw, ref_raw, rel_cols)
        val = fg.add_ref_relative_features(val_raw, ref_raw, rel_cols)
        proxy = fit_predict(ref, val, cfg)
        ys.append(train.iloc[val_idx][TARGETS].to_numpy(dtype=int))
        bases.append(current[val_idx])
        proxies.append(proxy)
        print(f"[dynamic geometry] {cfg.name} {fold_name} val={len(val_idx)}", flush=True)
    y = np.vstack(ys)
    base = np.vstack(bases)
    proxy = np.vstack(proxies)
    grid = np.array([0.0, 0.02, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30, 0.45, 0.60, 0.80, 1.00])
    rows = []
    for j, target in enumerate(TARGETS):
        base_loss = loss_col(y[:, j], base[:, j])
        for w in grid:
            loss = loss_col(y[:, j], (1.0 - w) * base[:, j] + w * proxy[:, j])
            rows.append(
                {
                    "config": cfg.name,
                    "target": target,
                    "weight": float(w),
                    "loss": loss,
                    "delta_vs_base": loss - base_loss,
                    "base_loss": base_loss,
                    "proxy_loss": loss_col(y[:, j], proxy[:, j]),
                    "scored_occurrences": int(len(y)),
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    train, _ = prepare_frames()
    all_rows = []
    preds = {}
    for cfg in configs():
        pred = oof_config(train, cfg)
        preds[cfg.name] = pred
        np.save(OUT / f"sleep_dynamics_proxy_oof_{cfg.name}.npy", pred)
        all_rows.append(summarize(train, cfg.name, pred))
    result = pd.concat(all_rows, ignore_index=True)
    result.to_csv(OUT / "sleep_dynamics_proxy_results.csv", index=False)
    top = result.sort_values(["target", "best_blend_loss"]).groupby("target").head(4)
    top.to_csv(OUT / "sleep_dynamics_proxy_top.csv", index=False)
    split = subject_split_guardrail(train, preds)
    split.to_csv(OUT / "sleep_dynamics_proxy_subject_split_guardrail.csv", index=False)
    improved = result[result["delta_vs_current"] < -0.0005].sort_values("delta_vs_current")
    geo_frames = []
    for cfg_name in improved["config"].drop_duplicates().head(2):
        cfg = next(c for c in configs() if c.name == cfg_name)
        geo_frames.append(geometry_guardrail(train, cfg))
    if geo_frames:
        geo = pd.concat(geo_frames, ignore_index=True)
        geo.to_csv(OUT / "sleep_dynamics_proxy_geometry_grid.csv", index=False)
    print(top.round(6).to_string(index=False))
    print("\nSubject split")
    print(split.groupby("target").head(3).round(6).to_string(index=False))
    if geo_frames:
        print("\nGeometry")
        print(geo.sort_values(["target", "loss"]).groupby("target").head(3).round(6).to_string(index=False))


if __name__ == "__main__":
    main()
