from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

import sys

sys.path.append(str(Path(__file__).resolve().parent))
import sleep_interval_proxy_experiments as sip  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "lifelog_date"]
NIGHT_START = 18 * 60
NIGHT_END = 36 * 60


def safe_array(g: pd.DataFrame, col: str, default: float = np.nan) -> np.ndarray:
    arr = np.full(NIGHT_END - NIGHT_START, default, dtype=float)
    if col not in g:
        return arr
    idx = g["night_minute"].to_numpy(dtype=int) - NIGHT_START
    vals = g[col].to_numpy(dtype=float)
    ok = (idx >= 0) & (idx < len(arr))
    arr[idx[ok]] = vals[ok]
    return arr


def longest_run(mask: np.ndarray) -> tuple[int | None, int | None, int]:
    idx = np.flatnonzero(mask)
    if idx.size == 0:
        return None, None, 0
    best_start = cur_start = int(idx[0])
    best_end = cur_end = int(idx[0]) + 1
    prev = int(idx[0])
    for pos in idx[1:]:
        pos = int(pos)
        if pos == prev + 1:
            cur_end = pos + 1
        else:
            if cur_end - cur_start > best_end - best_start:
                best_start, best_end = cur_start, cur_end
            cur_start, cur_end = pos, pos + 1
        prev = pos
    if cur_end - cur_start > best_end - best_start:
        best_start, best_end = cur_start, cur_end
    return best_start, best_end, best_end - best_start


def build_window_features() -> pd.DataFrame:
    feature_path = OUT / "quiet_window_residual_features.parquet"
    if feature_path.exists():
        return pd.read_parquet(feature_path)
    _, _, all_keys = sip.d.read_labels()
    all_keys = all_keys[KEY].drop_duplicates().sort_values(KEY).reset_index(drop=True)
    minute = sip.build_minute_table()
    grouped = {k: v for k, v in minute.groupby(KEY, sort=False)}
    windows = []
    for lo in [19, 20, 21, 22, 23]:
        for hi in [32, 33, 34, 35, 36]:
            if hi - lo >= 9:
                windows.append((lo * 60, hi * 60))
    rows = []
    minutes = np.arange(NIGHT_START, NIGHT_END)
    for row in all_keys.itertuples(index=False):
        sid = str(row.subject_id)
        day = pd.Timestamp(row.lifelog_date)
        g = grouped.get((row.subject_id, row.lifelog_date), pd.DataFrame())
        screen = safe_array(g, "m_screen_use", 0.0)
        step = safe_array(g, "step", 0.0)
        speed = safe_array(g, "speed", 0.0)
        activity = safe_array(g, "m_activity", 3.0)
        hr = safe_array(g, "hr_mean")
        base_masks = {
            "screen": np.nan_to_num(screen, nan=0.0) <= 0.0,
            "screen_step": (np.nan_to_num(screen, nan=0.0) <= 0.0) & (np.nan_to_num(step, nan=0.0) <= 0.0),
            "screen_step_speed": (
                (np.nan_to_num(screen, nan=0.0) <= 0.0)
                & (np.nan_to_num(step, nan=0.0) <= 0.0)
                & (np.nan_to_num(speed, nan=0.0) <= 0.01)
            ),
            "screen_step_activity": (
                (np.nan_to_num(screen, nan=0.0) <= 0.0)
                & (np.nan_to_num(step, nan=0.0) <= 0.0)
                & np.isin(np.nan_to_num(activity, nan=3.0).round().astype(int), [0, 3])
            ),
        }
        out = {"subject_id": sid, "lifelog_date": day}
        for lo, hi in windows:
            wmask = (minutes >= lo) & (minutes < hi)
            wname = f"w{lo // 60}_{hi // 60}"
            for name, base_mask in base_masks.items():
                mask = base_mask & wmask
                start, end, dur = longest_run(mask)
                prefix = f"quiet_{wname}_{name}"
                out[f"{prefix}_dur"] = float(dur)
                out[f"{prefix}_start"] = np.nan if start is None else float((NIGHT_START + start) / 60.0)
                out[f"{prefix}_end"] = np.nan if end is None else float((NIGHT_START + end) / 60.0)
                if start is None or end is None:
                    out[f"{prefix}_hr_mean"] = np.nan
                    out[f"{prefix}_pre_screen_on"] = np.nan
                    out[f"{prefix}_post_screen_on"] = np.nan
                else:
                    core = np.zeros_like(mask, dtype=bool)
                    core[start:end] = True
                    pre = np.zeros_like(mask, dtype=bool)
                    pre[max(0, start - 120):start] = True
                    post = np.zeros_like(mask, dtype=bool)
                    post[end:min(len(mask), end + 120)] = True
                    out[f"{prefix}_hr_mean"] = float(np.nanmean(hr[core])) if np.isfinite(hr[core]).any() else np.nan
                    out[f"{prefix}_pre_screen_on"] = float(np.nansum(np.nan_to_num(screen[pre], nan=0.0)))
                    out[f"{prefix}_post_screen_on"] = float(np.nansum(np.nan_to_num(screen[post], nan=0.0)))
        rows.append(out)
    features = pd.DataFrame(rows)
    features.to_parquet(feature_path, index=False)
    return features


def corr(a: np.ndarray, b: np.ndarray) -> float:
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 60:
        return np.nan
    aa = a[ok]
    bb = b[ok]
    if np.nanstd(aa) == 0 or np.nanstd(bb) == 0:
        return np.nan
    return float(np.corrcoef(aa, bb)[0, 1])


def main() -> None:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    train = train.sort_values(KEY).reset_index(drop=True)
    base = np.load(OUT / "final_hybrid_0p578_logit_after_subject_final9_strict_oof.npy")
    feat = build_window_features()
    train = train.merge(feat, on=KEY, how="left")
    feature_cols = [c for c in train.columns if c.startswith("quiet_")]
    rows = []
    for target_idx, target in enumerate(TARGETS):
        residual = train[target].to_numpy(dtype=float) - base[:, target_idx]
        centered_residual = residual - pd.Series(residual).groupby(train["subject_id"]).transform("mean").to_numpy()
        for col in feature_cols:
            x = train[col].to_numpy(dtype=float)
            subj_center = x - pd.Series(x).groupby(train["subject_id"]).transform("mean").to_numpy()
            r = corr(subj_center, centered_residual)
            if np.isfinite(r):
                parts = col.split("_")
                rows.append(
                    {
                        "target": target,
                        "feature": col,
                        "window": parts[1],
                        "variant": "_".join(parts[2:-1]),
                        "stat": parts[-1],
                        "corr": r,
                        "abs_corr": abs(r),
                    }
                )
    result = pd.DataFrame(rows).sort_values(["target", "abs_corr"], ascending=[True, False])
    result.to_csv(OUT / "quiet_window_residual_probe.csv", index=False)
    result.groupby("target", group_keys=False).head(20).to_csv(OUT / "quiet_window_residual_probe_top.csv", index=False)
    print(result.groupby("target", group_keys=False).head(8).round(4).to_string(index=False))


if __name__ == "__main__":
    main()
