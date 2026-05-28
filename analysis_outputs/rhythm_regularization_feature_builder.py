from __future__ import annotations

from pathlib import Path
import warnings

import numpy as np
import pandas as pd
from pandas.errors import PerformanceWarning


warnings.simplefilter("ignore", PerformanceWarning)


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
KEY = ["subject_id", "lifelog_date"]


def _num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")


def _safe_name(col: str) -> str:
    name = col
    for prefix in ["proxy_", "presleep_", "quiet_"]:
        name = name.replace(prefix, "")
    return name.replace("__", "_")


def _circ_diff(a: pd.Series | np.ndarray, b: pd.Series | np.ndarray) -> np.ndarray:
    aa = np.asarray(a, dtype=float) % 24.0
    bb = np.asarray(b, dtype=float) % 24.0
    return ((aa - bb + 12.0) % 24.0) - 12.0


def _group_rolling_prev(df: pd.DataFrame, col: str, window: int) -> pd.Series:
    return df.groupby("subject_id", sort=False)[col].transform(
        lambda x: x.shift(1).rolling(window, min_periods=1).mean()
    )


def _group_rolling_next(df: pd.DataFrame, col: str, window: int) -> pd.Series:
    return df.groupby("subject_id", sort=False)[col].transform(
        lambda x: x.shift(-1).iloc[::-1].rolling(window, min_periods=1).mean().iloc[::-1]
    )


def _subject_quantile(values: pd.Series, subjects: pd.Series, q: float) -> pd.Series:
    return values.groupby(subjects, sort=False).transform(lambda x: x.quantile(q))


def _add_subject_context(out: pd.DataFrame, df: pd.DataFrame, col: str, *, is_hour: bool) -> list[str]:
    raw = _num(df[col])
    if raw.notna().sum() < 20 or raw.nunique(dropna=True) <= 1:
        return []

    subjects = df["subject_id"]
    base = f"rr_{_safe_name(col)}"
    g = raw.groupby(subjects, sort=False)
    med = g.transform("median")
    mean = g.transform("mean")
    std = g.transform("std").replace(0.0, np.nan)
    prev1 = g.shift(1)
    next1 = g.shift(-1)
    prev3 = _group_rolling_prev(pd.concat([df[["subject_id"]], raw.rename(col)], axis=1), col, 3)
    next3 = _group_rolling_next(pd.concat([df[["subject_id"]], raw.rename(col)], axis=1), col, 3)

    if is_hour:
        raw_mod = raw % 24.0
        dev = pd.Series(_circ_diff(raw_mod, med), index=df.index)
        prev1_diff = pd.Series(_circ_diff(raw_mod, prev1), index=df.index)
        next1_diff = pd.Series(_circ_diff(next1, raw_mod), index=df.index)
        prev3_diff = pd.Series(_circ_diff(raw_mod, prev3), index=df.index)
        next3_diff = pd.Series(_circ_diff(next3, raw_mod), index=df.index)
        out[f"{base}_sin"] = np.sin(2.0 * np.pi * raw_mod / 24.0)
        out[f"{base}_cos"] = np.cos(2.0 * np.pi * raw_mod / 24.0)
        out[f"{base}_late_after_24"] = raw - 24.0
    else:
        dev = raw - med
        prev1_diff = raw - prev1
        next1_diff = next1 - raw
        prev3_diff = raw - prev3
        next3_diff = next3 - raw
        out[f"{base}_ratio_to_subj_med"] = raw / med.replace(0.0, np.nan)

    absdev = dev.abs()
    q75_abs = _subject_quantile(absdev, subjects, 0.75)
    q90_abs = _subject_quantile(absdev, subjects, 0.90)
    irregular = (absdev > q75_abs).astype(float)
    very_irregular = (absdev > q90_abs).astype(float)
    prev_irregular = irregular.groupby(subjects, sort=False).shift(1)
    next_irregular = irregular.groupby(subjects, sort=False).shift(-1)

    same_weekend_med = raw.groupby([subjects, df["is_weekend"]], sort=False).transform("median")
    weekend_med = raw.where(df["is_weekend"] == 1).groupby(subjects, sort=False).transform("median")
    weekday_med = raw.where(df["is_weekend"] == 0).groupby(subjects, sort=False).transform("median")
    weekend_shift = weekend_med - weekday_med

    out[f"{base}_dev_subj_med"] = dev
    out[f"{base}_absdev_subj_med"] = absdev
    out[f"{base}_zdev_subj_mean"] = (raw - mean) / std
    out[f"{base}_prev1_delta"] = prev1_diff
    out[f"{base}_next1_delta"] = next1_diff
    out[f"{base}_prev3_delta"] = prev3_diff
    out[f"{base}_next3_delta"] = next3_diff
    out[f"{base}_neighbor_slope"] = (next1_diff - prev1_diff) / 2.0
    out[f"{base}_neighbor_volatility"] = prev1_diff.abs() + next1_diff.abs()
    out[f"{base}_local_reversal"] = np.sign(prev1_diff) * np.sign(next1_diff) * np.minimum(
        prev1_diff.abs(), next1_diff.abs()
    )
    out[f"{base}_same_weekend_dev"] = raw - same_weekend_med
    out[f"{base}_weekend_shift"] = weekend_shift
    out[f"{base}_irregular_flag"] = irregular
    out[f"{base}_very_irregular_flag"] = very_irregular
    out[f"{base}_neighbor_irregular_count"] = irregular + prev_irregular.fillna(0.0) + next_irregular.fillna(0.0)
    out[f"{base}_missing"] = raw.isna().astype(float)
    return [c for c in out.columns if c.startswith(base)]


def _quiet_summaries(df: pd.DataFrame, quiet: pd.DataFrame) -> pd.DataFrame:
    out = df[KEY].copy()
    methods = ["screen", "screen_step", "screen_step_speed", "screen_step_activity"]
    metrics = ["dur", "start", "end", "hr_mean", "pre_screen_on", "post_screen_on"]
    for method in methods:
        method_cols = {m: [c for c in quiet.columns if c.endswith(f"_{method}_{m}")] for m in metrics}
        dur_cols = method_cols["dur"]
        if not dur_cols:
            continue
        dur = quiet[dur_cols].apply(pd.to_numeric, errors="coerce")
        out[f"quiet_{method}_dur_max"] = dur.max(axis=1)
        out[f"quiet_{method}_dur_mean"] = dur.mean(axis=1)
        out[f"quiet_{method}_dur_std"] = dur.std(axis=1)
        out[f"quiet_{method}_dur_p90"] = dur.quantile(0.90, axis=1)
        out[f"quiet_{method}_dur_count"] = dur.notna().sum(axis=1)
        out[f"quiet_{method}_dur_stability"] = out[f"quiet_{method}_dur_mean"] / out[f"quiet_{method}_dur_max"].replace(0.0, np.nan)
        best_idx = dur.to_numpy(dtype=float)
        valid = np.isfinite(best_idx)
        fill = np.where(valid, best_idx, -np.inf)
        arg = fill.argmax(axis=1)
        has_any = valid.any(axis=1)
        out[f"quiet_{method}_best_window_start_grid"] = np.nan
        out[f"quiet_{method}_best_window_end_grid"] = np.nan
        for row_i, col_i in enumerate(arg):
            if not has_any[row_i]:
                continue
            parts = dur_cols[col_i].split("_")
            out.iat[row_i, out.columns.get_loc(f"quiet_{method}_best_window_start_grid")] = float(parts[1][1:])
            out.iat[row_i, out.columns.get_loc(f"quiet_{method}_best_window_end_grid")] = float(parts[2])
        for metric in ["start", "end", "hr_mean", "pre_screen_on", "post_screen_on"]:
            cols = method_cols[metric]
            if len(cols) != len(dur_cols):
                continue
            vals = quiet[cols].apply(pd.to_numeric, errors="coerce").to_numpy(dtype=float)
            picked = np.full(len(out), np.nan)
            for i, j in enumerate(arg):
                if has_any[i]:
                    picked[i] = vals[i, j]
            out[f"quiet_{method}_best_{metric}"] = picked
        out[f"quiet_{method}_pre_post_screen_delta"] = (
            out.get(f"quiet_{method}_best_post_screen_on") - out.get(f"quiet_{method}_best_pre_screen_on")
        )
        out[f"quiet_{method}_best_mid"] = (
            out.get(f"quiet_{method}_best_start") + out.get(f"quiet_{method}_best_end")
        ) / 2.0

    dur_all_cols = [c for c in out.columns if c.endswith("_dur_max")]
    if dur_all_cols:
        out["quiet_any_dur_max"] = out[dur_all_cols].max(axis=1)
        out["quiet_any_dur_mean_of_max"] = out[dur_all_cols].mean(axis=1)
        out["quiet_any_method_spread"] = out[dur_all_cols].max(axis=1) - out[dur_all_cols].min(axis=1)
    return out


def build_features() -> pd.DataFrame:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    sub = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    rows = pd.concat(
        [train[["subject_id", "sleep_date", "lifelog_date"]], sub[["subject_id", "sleep_date", "lifelog_date"]]],
        ignore_index=True,
    ).sort_values(KEY).reset_index(drop=True)

    proxy = pd.read_parquet(OUT / "sleep_interval_proxy_features.parquet")
    quiet_raw = pd.read_parquet(OUT / "quiet_window_residual_features.parquet")
    presleep = pd.read_parquet(OUT / "pre_sleep_relative_features.parquet")
    quiet = _quiet_summaries(rows, quiet_raw)

    df = rows.copy()
    for block in [proxy, quiet, presleep]:
        keep = [c for c in block.columns if c not in {"sleep_date", "split"}]
        df = df.merge(block[keep], on=KEY, how="left")

    out = rows.copy()
    out["rr_dayofweek"] = out["lifelog_date"].dt.dayofweek
    out["rr_is_weekend"] = (out["rr_dayofweek"] >= 5).astype(float)
    out["rr_dow_sin"] = np.sin(2.0 * np.pi * out["rr_dayofweek"] / 7.0)
    out["rr_dow_cos"] = np.cos(2.0 * np.pi * out["rr_dayofweek"] / 7.0)
    out["rr_subject_day_index"] = out.groupby("subject_id", sort=False).cumcount()
    out["rr_subject_day_count"] = out.groupby("subject_id", sort=False)["subject_id"].transform("size")
    out["rr_subject_phase"] = out["rr_subject_day_index"] / (out["rr_subject_day_count"] - 1).replace(0, np.nan)
    out["rr_day_gap_prev"] = out.groupby("subject_id", sort=False)["lifelog_date"].diff().dt.days
    out["rr_day_gap_next"] = -out.groupby("subject_id", sort=False)["lifelog_date"].diff(-1).dt.days

    df["is_weekend"] = out["rr_is_weekend"].astype(int)

    hour_cols = [
        "proxy_screen_start_hour",
        "proxy_screen_end_hour",
        "proxy_screen_mid_hour",
        "proxy_screen_step_start_hour",
        "proxy_screen_step_end_hour",
        "proxy_screen_step_mid_hour",
        "proxy_screen_step_activity_start_hour",
        "proxy_screen_step_activity_end_hour",
        "proxy_screen_step_activity_mid_hour",
        "quiet_screen_best_start",
        "quiet_screen_best_end",
        "quiet_screen_best_mid",
        "quiet_screen_step_best_start",
        "quiet_screen_step_best_end",
        "quiet_screen_step_best_mid",
        "quiet_screen_step_activity_best_start",
        "quiet_screen_step_activity_best_end",
        "quiet_screen_step_activity_best_mid",
    ]
    value_cols = [
        "proxy_screen_duration_min",
        "proxy_screen_step_duration_min",
        "proxy_screen_step_activity_duration_min",
        "proxy_screen_charge_frac",
        "proxy_screen_step_charge_frac",
        "proxy_screen_step_activity_charge_frac",
        "proxy_screen_screen_on_core_min",
        "proxy_screen_step_screen_on_core_min",
        "proxy_screen_step_activity_screen_on_core_min",
        "proxy_screen_step_core_sum",
        "proxy_screen_step_step_core_sum",
        "proxy_screen_step_activity_step_core_sum",
        "proxy_screen_hr_mean",
        "proxy_screen_step_hr_mean",
        "proxy_screen_step_activity_hr_mean",
        "proxy_screen_pre2h_screen_sum",
        "proxy_screen_step_pre2h_screen_sum",
        "proxy_screen_step_activity_pre2h_screen_sum",
        "proxy_screen_step_pre2h_wlight_mean",
        "proxy_screen_step_pre2h_mlight_mean",
        "quiet_screen_dur_max",
        "quiet_screen_dur_stability",
        "quiet_screen_step_dur_max",
        "quiet_screen_step_dur_stability",
        "quiet_screen_step_activity_dur_max",
        "quiet_screen_step_activity_dur_stability",
        "quiet_any_dur_max",
        "quiet_any_method_spread",
        "presleep_charge_core5h_m_charging_min",
        "presleep_charge_core5h_m_charging_mean",
        "presleep_charge_pre3h_m_charging_mean",
        "presleep_mlight_core5h_m_light_min",
        "presleep_mlight_pre3h_m_light_sum",
        "presleep_mlight_pre3h_m_light_max",
        "presleep_mlight_pre3h_m_light_min",
        "presleep_wlight_pre1h_w_light_min",
        "presleep_activity_pre1h_m_activity_last",
        "presleep_hr_pre6h_hr_points_count",
        "presleep_hr_core5h_hr_mean",
        "presleep_ambience_core5h_top_is_speech_count",
        "presleep_ambience_core5h_top_is_inside_count",
        "presleep_ambience_core5h_top_is_silence_count",
    ]

    added: list[str] = []
    for col in hour_cols:
        if col in df.columns:
            added.extend(_add_subject_context(out, df, col, is_hour=True))
    for col in value_cols:
        if col in df.columns:
            added.extend(_add_subject_context(out, df, col, is_hour=False))

    def add_cross(name: str, left: str, right: str, op: str = "prod") -> None:
        if left not in out.columns or right not in out.columns:
            return
        if op == "prod":
            out[name] = out[left] * out[right]
        elif op == "sumabs":
            out[name] = out[left].abs() + out[right].abs()
        elif op == "diff":
            out[name] = out[left] - out[right]

    add_cross(
        "rr_cross_late_start_x_short_quiet",
        "rr_screen_step_start_hour_late_after_24",
        "rr_any_dur_max_dev_subj_med",
        "prod",
    )
    add_cross(
        "rr_cross_start_absdev_plus_light_absdev",
        "rr_screen_step_start_hour_absdev_subj_med",
        "rr_mlight_pre3h_m_light_sum_absdev_subj_med",
        "sumabs",
    )
    add_cross(
        "rr_cross_charge_dev_x_light_min_dev",
        "rr_charge_core5h_m_charging_min_dev_subj_med",
        "rr_mlight_core5h_m_light_min_dev_subj_med",
        "prod",
    )
    add_cross(
        "rr_cross_hr_points_dev_x_quiet_dev",
        "rr_hr_pre6h_hr_points_count_dev_subj_med",
        "rr_any_dur_max_dev_subj_med",
        "prod",
    )
    add_cross(
        "rr_cross_screen_core_dev_x_step_core_dev",
        "rr_screen_step_screen_on_core_min_dev_subj_med",
        "rr_screen_step_step_core_sum_dev_subj_med",
        "prod",
    )
    add_cross(
        "rr_cross_weekend_start_shift_minus_duration_shift",
        "rr_screen_step_start_hour_weekend_shift",
        "rr_screen_step_duration_min_weekend_shift",
        "diff",
    )

    feature_cols = [c for c in out.columns if c.startswith("rr_")]
    out[feature_cols] = out[feature_cols].replace([np.inf, -np.inf], np.nan)
    return out


def main() -> None:
    features = build_features()
    path = OUT / "rhythm_regular_features.parquet"
    features.to_parquet(path, index=False)
    numeric = [c for c in features.columns if c.startswith("rr_")]
    coverage = pd.DataFrame(
        {
            "feature": numeric,
            "non_null": [int(features[c].notna().sum()) for c in numeric],
            "nunique": [int(features[c].nunique(dropna=True)) for c in numeric],
        }
    ).sort_values(["non_null", "nunique"], ascending=[False, False])
    coverage.to_csv(OUT / "rhythm_regular_feature_coverage.csv", index=False)
    print(f"saved {path} shape={features.shape} rr_features={len(numeric)}")
    print(coverage.head(20).to_string(index=False))


if __name__ == "__main__":
    main()
