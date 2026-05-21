from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


KEY_COLUMNS = ["subject_id", "lifelog_date"]
TARGET_KEYS = ["subject_id", "sleep_date", "lifelog_date"]
ROLL_WINDOWS = [3, 7, 14, 28]
APP_CATEGORIES = [
    "browser",
    "call",
    "camera",
    "finance",
    "game",
    "health",
    "messenger",
    "music",
    "navigation",
    "news",
    "os_launcher",
    "other",
    "productivity",
    "reading",
    "religion",
    "shopping",
    "sns",
    "video",
]
GROUPS = {
    "social": ["call", "messenger", "sns"],
    "passive": ["video", "music", "news", "game", "reading"],
    "utility": ["browser", "finance", "health", "navigation", "productivity", "shopping"],
    "system": ["os_launcher", "other"],
    "private": ["camera", "religion"],
}


def normalize_rows(path: str) -> pd.DataFrame:
    frame = pd.read_csv(path).copy()
    frame["subject_id"] = frame["subject_id"].astype(str)
    frame["sleep_date"] = pd.to_datetime(frame["sleep_date"]).dt.strftime("%Y-%m-%d")
    frame["lifelog_date"] = pd.to_datetime(frame["lifelog_date"]).dt.strftime("%Y-%m-%d")
    return frame[TARGET_KEYS]


def load_rows(train_path: str, sample_path: str) -> pd.DataFrame:
    return pd.concat([normalize_rows(train_path), normalize_rows(sample_path)], ignore_index=True).drop_duplicates()


def safe_div(numer: pd.Series | np.ndarray | float, denom: pd.Series | np.ndarray | float) -> pd.Series:
    return pd.Series(numer, copy=False).astype(float) / (pd.Series(denom, copy=False).astype(float) + 1e-6)


def entropy_matrix(values: np.ndarray) -> np.ndarray:
    values = np.clip(np.nan_to_num(values.astype(float), nan=0.0), 0.0, None)
    total = values.sum(axis=1, keepdims=True) + 1e-12
    prob = values / total
    return -(prob * np.log(prob + 1e-12)).sum(axis=1)


def jsd_rows(values: np.ndarray, baseline: np.ndarray) -> np.ndarray:
    values = np.clip(np.nan_to_num(values.astype(float), nan=0.0), 0.0, None)
    baseline = np.clip(np.nan_to_num(baseline.astype(float), nan=0.0), 0.0, None)
    values = values / (values.sum(axis=1, keepdims=True) + 1e-12)
    baseline = baseline / (baseline.sum(axis=1, keepdims=True) + 1e-12)
    mix = 0.5 * (values + baseline)
    kl_a = (values * (np.log(values + 1e-12) - np.log(mix + 1e-12))).sum(axis=1)
    kl_b = (baseline * (np.log(baseline + 1e-12) - np.log(mix + 1e-12))).sum(axis=1)
    return 0.5 * (kl_a + kl_b)


def count_starts(flags: np.ndarray) -> int:
    flags = flags.astype(bool)
    if len(flags) == 0:
        return 0
    return int((flags & ~np.r_[False, flags[:-1]]).sum())


def longest_run(flags: np.ndarray) -> int:
    best = 0
    cur = 0
    for flag in flags.astype(bool):
        cur = cur + 1 if flag else 0
        best = max(best, cur)
    return int(best)


def burstiness(start_indices: np.ndarray) -> float:
    if len(start_indices) < 3:
        return 0.0
    gaps = np.diff(start_indices).astype(float)
    mu = float(gaps.mean())
    sigma = float(gaps.std())
    return float((sigma - mu) / (sigma + mu + 1e-6))


def add_app_tables(rows: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    out = rows.copy()
    daily = pd.read_parquet(args.app_daily).copy()
    daily["subject_id"] = daily["subject_id"].astype(str)
    daily["lifelog_date"] = pd.to_datetime(daily["date"]).dt.strftime("%Y-%m-%d")
    daily_cols = [f"app_{cat}_sec" for cat in APP_CATEGORIES if f"app_{cat}_sec" in daily]
    out = out.merge(daily[KEY_COLUMNS + daily_cols], on=KEY_COLUMNS, how="left")

    prebed = pd.read_parquet(args.app_prebed).copy()
    prebed["subject_id"] = prebed["subject_id"].astype(str)
    prebed["sleep_date"] = pd.to_datetime(prebed["sleep_date"]).dt.strftime("%Y-%m-%d")
    pre_cols = [f"prebed_{cat}_sec" for cat in APP_CATEGORIES if f"prebed_{cat}_sec" in prebed]
    out = out.merge(prebed[["subject_id", "sleep_date"] + pre_cols], on=["subject_id", "sleep_date"], how="left")
    out[daily_cols + pre_cols] = out[daily_cols + pre_cols].fillna(0.0)
    return out


def add_app_profile_features(frame: pd.DataFrame) -> pd.DataFrame:
    additions: dict[str, pd.Series | np.ndarray] = {}
    daily_cols = [f"app_{cat}_sec" for cat in APP_CATEGORIES if f"app_{cat}_sec" in frame]
    pre_cols = [f"prebed_{cat}_sec" for cat in APP_CATEGORIES if f"prebed_{cat}_sec" in frame]
    daily_x = frame[daily_cols].to_numpy(float) if daily_cols else np.zeros((len(frame), 0))
    pre_x = frame[pre_cols].to_numpy(float) if pre_cols else np.zeros((len(frame), 0))

    additions["z_di_app_total_sec"] = daily_x.sum(axis=1) if daily_x.size else np.zeros(len(frame))
    additions["z_di_prebed_total_sec"] = pre_x.sum(axis=1) if pre_x.size else np.zeros(len(frame))
    additions["z_di_app_entropy"] = entropy_matrix(daily_x) if daily_x.size else np.zeros(len(frame))
    additions["z_di_prebed_entropy"] = entropy_matrix(pre_x) if pre_x.size else np.zeros(len(frame))
    daily_prop = daily_x / (daily_x.sum(axis=1, keepdims=True) + 1e-6) if daily_x.size else daily_x
    pre_prop = pre_x / (pre_x.sum(axis=1, keepdims=True) + 1e-6) if pre_x.size else pre_x
    additions["z_di_app_hhi"] = (daily_prop**2).sum(axis=1) if daily_x.size else np.zeros(len(frame))
    additions["z_di_prebed_hhi"] = (pre_prop**2).sum(axis=1) if pre_x.size else np.zeros(len(frame))
    additions["z_di_app_top1_share"] = daily_prop.max(axis=1) if daily_x.size else np.zeros(len(frame))
    additions["z_di_prebed_top1_share"] = pre_prop.max(axis=1) if pre_x.size else np.zeros(len(frame))

    for group, cats in GROUPS.items():
        daily_group = [f"app_{cat}_sec" for cat in cats if f"app_{cat}_sec" in frame]
        pre_group = [f"prebed_{cat}_sec" for cat in cats if f"prebed_{cat}_sec" in frame]
        additions[f"z_di_app_{group}_sec"] = frame[daily_group].sum(axis=1) if daily_group else 0.0
        additions[f"z_di_prebed_{group}_sec"] = frame[pre_group].sum(axis=1) if pre_group else 0.0

    app_total = pd.Series(additions["z_di_app_total_sec"], index=frame.index)
    pre_total = pd.Series(additions["z_di_prebed_total_sec"], index=frame.index)
    for group in GROUPS:
        app_group = pd.Series(additions[f"z_di_app_{group}_sec"], index=frame.index)
        pre_group = pd.Series(additions[f"z_di_prebed_{group}_sec"], index=frame.index)
        additions[f"z_di_app_{group}_share"] = safe_div(app_group, app_total).to_numpy()
        additions[f"z_di_prebed_{group}_share"] = safe_div(pre_group, pre_total).to_numpy()

    additions["z_di_passive_over_social"] = safe_div(
        additions["z_di_app_passive_sec"], pd.Series(additions["z_di_app_social_sec"]) + 60.0
    ).to_numpy()
    additions["z_di_prebed_passive_over_social"] = safe_div(
        additions["z_di_prebed_passive_sec"], pd.Series(additions["z_di_prebed_social_sec"]) + 60.0
    ).to_numpy()
    additions["z_di_isolation_balance"] = (
        pd.Series(additions["z_di_app_passive_share"]) - pd.Series(additions["z_di_app_social_share"])
    ).to_numpy()
    additions["z_di_prebed_isolation_balance"] = (
        pd.Series(additions["z_di_prebed_passive_share"]) - pd.Series(additions["z_di_prebed_social_share"])
    ).to_numpy()

    prof = pd.DataFrame({"subject_id": frame["subject_id"].to_numpy()})
    if daily_x.size:
        subject_baseline = (
            pd.DataFrame(daily_prop, columns=daily_cols)
            .assign(subject_id=frame["subject_id"].to_numpy())
            .groupby("subject_id")[daily_cols]
            .median()
        )
        base = prof["subject_id"].map(lambda s: subject_baseline.loc[s].to_numpy(float)).to_list()
        additions["z_di_app_profile_jsd"] = jsd_rows(daily_prop, np.vstack(base))
    if pre_x.size:
        subject_baseline = (
            pd.DataFrame(pre_prop, columns=pre_cols)
            .assign(subject_id=frame["subject_id"].to_numpy())
            .groupby("subject_id")[pre_cols]
            .median()
        )
        base = prof["subject_id"].map(lambda s: subject_baseline.loc[s].to_numpy(float)).to_list()
        additions["z_di_prebed_profile_jsd"] = jsd_rows(pre_prop, np.vstack(base))

    return pd.concat([frame, pd.DataFrame(additions, index=frame.index)], axis=1)


def add_phone_fragmentation(rows: pd.DataFrame, grid_path: str) -> pd.DataFrame:
    grid = pd.read_parquet(grid_path).copy()
    grid["subject_id"] = grid["subject_id"].astype(str)
    grid["lifelog_date"] = pd.to_datetime(grid["date"]).dt.strftime("%Y-%m-%d")
    records = []
    for (subject, date), part in grid.groupby(["subject_id", "lifelog_date"], sort=True):
        part = part.sort_values("tok")
        phone = np.nan_to_num(part.get("ev_phone_active", pd.Series(dtype=float)).to_numpy(float), nan=0.0) > 0.5
        moving = np.nan_to_num(part.get("ev_moving", pd.Series(dtype=float)).to_numpy(float), nan=0.0) > 0.5
        usage = np.nan_to_num(part.get("usage_total", pd.Series(dtype=float)).to_numpy(float), nan=0.0)
        screen = np.nan_to_num(part.get("screen_mean", pd.Series(dtype=float)).to_numpy(float), nan=0.0)
        starts = np.flatnonzero(phone & ~np.r_[False, phone[:-1]]) if len(phone) else np.array([], dtype=int)
        short = phone & (usage <= np.nanpercentile(usage[usage > 0], 35) if np.any(usage > 0) else False)
        night = np.isin(part["tok"].to_numpy(int), list(range(0, 12)) + list(range(42, 48)))
        evening = part["tok"].between(34, 43).to_numpy(bool)
        row = {
            "subject_id": subject,
            "lifelog_date": date,
            "z_di_phone_active_ratio": float(phone.mean()) if len(phone) else 0.0,
            "z_di_phone_start_count": float(count_starts(phone)),
            "z_di_phone_longest_run": float(longest_run(phone)),
            "z_di_phone_burstiness": burstiness(starts),
            "z_di_short_check_ratio": float(short.mean()) if len(short) else 0.0,
            "z_di_screen_without_usage_ratio": float(((screen > 0) & (usage <= 0)).mean()) if len(screen) else 0.0,
            "z_di_phone_still_ratio": float((phone & ~moving).mean()) if len(phone) else 0.0,
            "z_di_phone_move_ratio": float((phone & moving).mean()) if len(phone) else 0.0,
            "z_di_night_phone_ratio": float(phone[night].mean()) if night.any() else 0.0,
            "z_di_evening_phone_ratio": float(phone[evening].mean()) if evening.any() else 0.0,
            "z_di_night_usage_share": float(usage[night].sum() / (usage.sum() + 1e-6)) if len(usage) else 0.0,
            "z_di_evening_usage_share": float(usage[evening].sum() / (usage.sum() + 1e-6)) if len(usage) else 0.0,
        }
        records.append(row)
    daily = pd.DataFrame(records)
    return rows.merge(daily, on=KEY_COLUMNS, how="left")


def add_subject_stats(frame: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    additions = {}
    for col in cols:
        center = frame.groupby("subject_id")[col].transform("median")
        mad = frame.groupby("subject_id")[col].transform(lambda s: np.nanmedian(np.abs(s - np.nanmedian(s))))
        iqr = frame.groupby("subject_id")[col].transform(lambda s: np.nanpercentile(s, 75) - np.nanpercentile(s, 25))
        std = frame.groupby("subject_id")[col].transform("std").fillna(0.0)
        scale = pd.concat([mad, iqr / 1.349, std / 1.4826, pd.Series(1.0, index=frame.index)], axis=1).max(axis=1)
        additions[f"{col}_subdev"] = frame[col] - center
        additions[f"{col}_subrz"] = ((frame[col] - center) / scale).clip(-20.0, 20.0)
        additions[f"{col}_subpct"] = frame.groupby("subject_id")[col].rank(pct=True).fillna(0.5)
    return pd.concat([frame, pd.DataFrame(additions, index=frame.index)], axis=1)


def add_rolling(frame: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    frame = frame.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True)
    additions = {}
    for window in ROLL_WINDOWS:
        for col in cols:
            shifted = frame.groupby("subject_id")[col].shift(1)
            roll = shifted.groupby(frame["subject_id"]).rolling(window, min_periods=2).mean().reset_index(level=0, drop=True)
            additions[f"{col}_past{window}_delta"] = (frame[col] - roll).fillna(0.0)
            log_ratio = np.log1p(np.clip(frame[col].to_numpy(float), 0.0, None)) - np.log1p(
                np.clip(roll.fillna(0.0).to_numpy(float), 0.0, None)
            )
            additions[f"{col}_past{window}_log_ratio"] = np.clip(np.nan_to_num(log_ratio, nan=0.0), -20.0, 20.0)
    return pd.concat([frame, pd.DataFrame(additions, index=frame.index)], axis=1)


def build_features(args: argparse.Namespace) -> pd.DataFrame:
    rows = load_rows(args.train_path, args.sample_path)
    features = add_app_tables(rows, args)
    features = add_app_profile_features(features)
    features = add_phone_fragmentation(features, args.grid_path)
    base_cols = [
        c
        for c in features.columns
        if c.startswith("z_di_") and pd.api.types.is_numeric_dtype(features[c])
    ]
    features[base_cols] = features[base_cols].fillna(0.0).replace([np.inf, -np.inf], 0.0)
    stats_cols = [
        c
        for c in base_cols
        if any(
            key in c
            for key in [
                "social",
                "passive",
                "isolation",
                "profile_jsd",
                "entropy",
                "hhi",
                "phone",
                "short_check",
                "night",
                "evening",
            ]
        )
    ]
    features = add_subject_stats(features, stats_cols)
    rolling_cols = [
        c
        for c in [
            "z_di_app_social_sec",
            "z_di_app_passive_sec",
            "z_di_app_social_share",
            "z_di_app_passive_share",
            "z_di_passive_over_social",
            "z_di_isolation_balance",
            "z_di_app_profile_jsd",
            "z_di_app_entropy",
            "z_di_phone_start_count",
            "z_di_phone_burstiness",
            "z_di_night_phone_ratio",
            "z_di_evening_usage_share",
            "z_di_prebed_passive_over_social",
            "z_di_prebed_isolation_balance",
        ]
        if c in features
    ]
    features = add_rolling(features, rolling_cols)
    keep_cols = KEY_COLUMNS + sorted(
        [c for c in features.columns if c.startswith("z_di_") and pd.api.types.is_numeric_dtype(features[c])]
    )
    return features[keep_cols].sort_values(KEY_COLUMNS).fillna(0.0).replace([np.inf, -np.inf], 0.0)


def dataframe_to_markdown(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "_No rows._"
    cols = frame.columns.tolist()
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in frame.iterrows():
        vals = []
        for col in cols:
            value = row[col]
            vals.append(f"{value:.6f}" if isinstance(value, float) else str(value))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def run(args: argparse.Namespace) -> None:
    features = build_features(args)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    features.to_parquet(output, index=False)
    feature_cols = [c for c in features.columns if c not in KEY_COLUMNS]
    coverage = pd.DataFrame(
        {
            "feature": feature_cols,
            "mean": [float(features[c].mean()) for c in feature_cols],
            "std": [float(features[c].std()) for c in feature_cols],
        }
    )
    report = {
        "output": str(output),
        "rows": int(len(features)),
        "feature_count": int(len(feature_cols)),
        "hypotheses": [
            "Q2/Q3 may reflect digital isolation: social communication drops while passive media rises.",
            "Sleep targets may respond to pre-bed passive consumption and short phone-check fragmentation.",
            "App profile divergence from a subject's usual category mix may capture unusual mental state without labels.",
        ],
    }
    output.with_suffix(".report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    md = [
        "# Digital Isolation Latents",
        "",
        "## Purpose",
        "",
        "Encode app-category composition, social-vs-passive imbalance, app-profile shift, and phone-check fragmentation as a separate digital mental-state family.",
        "",
        f"- Output: `{output}`",
        f"- Rows: `{len(features)}`",
        f"- Feature count: `{len(feature_cols)}`",
        "",
        "## Feature Summary",
        "",
        dataframe_to_markdown(coverage.head(50)),
    ]
    output.with_suffix(".report.md").write_text("\n".join(md), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build digital isolation and app profile shift latent features.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--app-daily", default="artifacts/09_app_categories_daily.parquet")
    parser.add_argument("--app-prebed", default="artifacts/09_app_prebed_categories.parquet")
    parser.add_argument("--grid-path", default="artifacts/multires_30min_event_hybrid_grid.parquet")
    parser.add_argument("--output", default="artifacts/domain_digital_isolation_v1.parquet")
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
