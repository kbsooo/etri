from __future__ import annotations

import sys
import warnings
from dataclasses import dataclass
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
import current_0p594_cross_target_coherence as cur  # noqa: E402
import deep_dive_analysis as d  # noqa: E402
import geometry_mask_cv_experiments as geom  # noqa: E402
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
    return float(log_loss(y.astype(int), clip(p), labels=[0, 1]))


def safe_array(g: pd.DataFrame, col: str, default: float = np.nan) -> np.ndarray:
    arr = np.full(NIGHT_END - NIGHT_START, default, dtype=float)
    if col not in g:
        return arr
    idx = g["night_minute"].to_numpy(dtype=int) - NIGHT_START
    vals = g[col].to_numpy(dtype=float)
    ok = (idx >= 0) & (idx < len(arr))
    arr[idx[ok]] = vals[ok]
    return arr


def runs(mask: np.ndarray) -> list[tuple[int, int]]:
    idx = np.where(mask)[0]
    if idx.size == 0:
        return []
    out = []
    start = prev = int(idx[0])
    for pos in idx[1:]:
        pos = int(pos)
        if pos == prev + 1:
            prev = pos
            continue
        out.append((start, prev + 1))
        start = prev = pos
    out.append((start, prev + 1))
    return out


def run_stats(mask: np.ndarray, minutes: np.ndarray, prefix: str) -> dict[str, float]:
    rs = runs(mask)
    lengths = np.array([end - start for start, end in rs], dtype=float)
    total = float(lengths.sum()) if lengths.size else 0.0
    longest = float(lengths.max()) if lengths.size else 0.0
    top2 = float(np.sort(lengths)[-2:].sum()) if lengths.size else 0.0
    cand_minutes = float(mask.size)
    span = float(rs[-1][1] - rs[0][0]) if rs else 0.0
    gap = float(span - total) if rs else 0.0
    out = {
        f"{prefix}_total_quiet_min": total,
        f"{prefix}_segment_count": float(len(rs)),
        f"{prefix}_segment_count_ge5": float((lengths >= 5).sum()) if lengths.size else 0.0,
        f"{prefix}_segment_count_ge15": float((lengths >= 15).sum()) if lengths.size else 0.0,
        f"{prefix}_segment_count_ge30": float((lengths >= 30).sum()) if lengths.size else 0.0,
        f"{prefix}_segment_count_ge60": float((lengths >= 60).sum()) if lengths.size else 0.0,
        f"{prefix}_longest_duration_min": longest,
        f"{prefix}_top2_duration_min": top2,
        f"{prefix}_mean_segment_duration_min": float(lengths.mean()) if lengths.size else 0.0,
        f"{prefix}_median_segment_duration_min": float(np.median(lengths)) if lengths.size else 0.0,
        f"{prefix}_longest_frac": longest / total if total > 0 else np.nan,
        f"{prefix}_fragmentation": float(len(rs)) / total if total > 0 else np.nan,
        f"{prefix}_gap_minutes_between_quiet": gap,
        f"{prefix}_span_quiet_frac": total / span if span > 0 else np.nan,
        f"{prefix}_candidate_quiet_frac": total / cand_minutes if cand_minutes > 0 else np.nan,
    }
    if rs:
        first_start, _ = rs[0]
        _, last_end = rs[-1]
        longest_i = int(np.argmax(lengths))
        long_start, long_end = rs[longest_i]
        out[f"{prefix}_first_segment_start_hour"] = float(minutes[first_start] / 60.0)
        out[f"{prefix}_last_segment_end_hour"] = float(minutes[last_end - 1] / 60.0)
        out[f"{prefix}_longest_start_hour"] = float(minutes[long_start] / 60.0)
        out[f"{prefix}_longest_end_hour"] = float(minutes[long_end - 1] / 60.0)
        out[f"{prefix}_longest_mid_hour"] = float((minutes[long_start] + minutes[long_end - 1]) / 120.0)
    else:
        for suffix in ["first_segment_start_hour", "last_segment_end_hour", "longest_start_hour", "longest_end_hour", "longest_mid_hour"]:
            out[f"{prefix}_{suffix}"] = np.nan
    return out


def mean_window(arr: np.ndarray, mask: np.ndarray) -> float:
    vals = arr[mask]
    vals = vals[np.isfinite(vals)]
    return float(vals.mean()) if vals.size else np.nan


def row_features(sid: str, day: pd.Timestamp, g: pd.DataFrame) -> dict[str, float | str | pd.Timestamp]:
    minutes = np.arange(NIGHT_START, NIGHT_END, dtype=float)
    screen = safe_array(g, "m_screen_use")
    step = safe_array(g, "step", 0.0)
    speed = safe_array(g, "speed", 0.0)
    activity = safe_array(g, "m_activity")
    charge = safe_array(g, "m_charging")
    hr = safe_array(g, "hr_mean")
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
    out: dict[str, float | str | pd.Timestamp] = {"subject_id": sid, "lifelog_date": day}
    for name, mask in variants.items():
        prefix = f"proxy_frag_{name}"
        out.update(run_stats(mask[cand], minutes[cand], prefix))
        core = mask
        active_between = cand & ~mask
        out[f"{prefix}_charge_mean"] = mean_window(charge, core)
        out[f"{prefix}_hr_mean"] = mean_window(hr, core)
        out[f"{prefix}_hr_vs_candidate"] = mean_window(hr, core) - mean_window(hr, cand)
        out[f"{prefix}_wlight_mean"] = mean_window(w_light, core)
        out[f"{prefix}_mlight_mean"] = mean_window(m_light, core)
        out[f"{prefix}_active_between_screen_sum"] = float(np.nansum(np.nan_to_num(screen[active_between], nan=0.0)))
        out[f"{prefix}_active_between_step_sum"] = float(np.nansum(np.nan_to_num(step[active_between], nan=0.0)))
    return out


def build_fragmentation_features() -> pd.DataFrame:
    path = OUT / "sleep_fragmentation_proxy_features.parquet"
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
    out = pd.DataFrame(rows)
    out.to_parquet(path, index=False)
    return out


def prepare_frames() -> tuple[pd.DataFrame, pd.DataFrame]:
    train, sub = sip.prepare_frames()
    frag = build_fragmentation_features()
    train = train.merge(frag, on=KEY, how="left").sort_values(KEY).reset_index(drop=True)
    sub = sub.merge(frag, on=KEY, how="left").sort_values(KEY).reset_index(drop=True)
    return train, sub


def feature_columns(rows: pd.DataFrame) -> list[str]:
    excluded = set(TARGETS + KEY + ["sleep_date", "split"])
    return [c for c in rows.columns if c not in excluded]


def make_pipe(cols: list[str], cfg: ETConfig) -> Pipeline:
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
        n_estimators=cfg.n_estimators,
        min_samples_leaf=cfg.min_samples_leaf,
        max_features=cfg.max_features,
        max_depth=cfg.max_depth,
        random_state=cfg.seed,
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


def fit_predict(train_rows: pd.DataFrame, rows: pd.DataFrame, cfg: ETConfig) -> np.ndarray:
    cols = feature_columns(train_rows)
    pipe = make_pipe(cols, cfg)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        pipe.fit(train_rows[cols], train_rows[TARGETS])
    return proba_matrix(pipe, rows, cols)


def configs() -> list[ETConfig]:
    return [
        ETConfig("frag_leaf4_mf0.6_depth10", 520, 4, 0.60, 10, 260901),
        ETConfig("frag_leaf6_mf0.8", 520, 6, 0.80, None, 260902),
        ETConfig("frag_leaf10_mf0.6", 520, 10, 0.60, None, 260903),
        ETConfig("frag_leaf3_mf0.35", 520, 3, 0.35, None, 260904),
    ]


def oof_config(train: pd.DataFrame, cfg: ETConfig) -> np.ndarray:
    rel_cols = fg.relative_source_cols(train)
    pred = np.zeros((len(train), len(TARGETS)), dtype=float)
    for fold_id, (tr_idx, val_idx) in enumerate(d.make_folds(train, "subject_blocks")):
        ref_raw = train.iloc[tr_idx].copy().reset_index(drop=True)
        val_raw = train.iloc[val_idx].copy().reset_index(drop=True)
        ref = fg.add_ref_relative_features(ref_raw, ref_raw, rel_cols)
        val = fg.add_ref_relative_features(val_raw, ref_raw, rel_cols)
        pred[val_idx] = fit_predict(ref, val, cfg)
        print(f"[fragment proxy] {cfg.name} fold={fold_id}", flush=True)
    return clip(pred)


def summarize(train: pd.DataFrame, name: str, proxy: np.ndarray) -> pd.DataFrame:
    current = cur.current_oof()
    y = train[TARGETS].to_numpy(dtype=int)
    grid = np.array([0.0, 0.02, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30, 0.45, 0.60, 0.80, 1.00])
    first_subjects = set(sorted(train["subject_id"].unique())[:5])
    select_mask = train["subject_id"].isin(first_subjects).to_numpy()
    hold_mask = ~select_mask
    rows = []
    for j, target in enumerate(TARGETS):
        base_loss = loss_col(y[:, j], current[:, j])
        losses = [loss_col(y[:, j], (1.0 - w) * current[:, j] + w * proxy[:, j]) for w in grid]
        best_i = int(np.argmin(losses))
        selected = None
        for w in grid:
            p = (1.0 - w) * current[:, j] + w * proxy[:, j]
            sel = loss_col(y[select_mask, j], p[select_mask])
            if selected is None or sel < selected[0]:
                selected = (sel, float(w), p)
        assert selected is not None
        rows.append(
            {
                "config": name,
                "target": target,
                "current_loss": base_loss,
                "proxy_loss": loss_col(y[:, j], proxy[:, j]),
                "best_weight": float(grid[best_i]),
                "best_blend_loss": float(losses[best_i]),
                "delta_vs_current": float(losses[best_i] - base_loss),
                "half_selected_weight": selected[1],
                "half_select_loss": selected[0],
                "half_holdout_current": loss_col(y[hold_mask, j], current[hold_mask, j]),
                "half_holdout_blend": loss_col(y[hold_mask, j], selected[2][hold_mask]),
            }
        )
    return pd.DataFrame(rows)


def geometry_guardrail(train: pd.DataFrame, sub: pd.DataFrame, cfg: ETConfig) -> pd.DataFrame:
    raw_train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    raw_sub = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    raw_train = raw_train.sort_values(KEY).reset_index(drop=True)
    raw_sub = raw_sub.sort_values(KEY).reset_index(drop=True)
    rel_cols = fg.relative_source_cols(train)
    current = cur.current_oof()
    folds = geom.geometry_folds(raw_train, raw_sub, n_repeats=10)
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
        print(f"[fragment geometry] {cfg.name} {fold_name} val={len(val_idx)}", flush=True)
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
    train, sub = prepare_frames()
    all_rows = []
    preds = {}
    for cfg in configs():
        pred = oof_config(train, cfg)
        preds[cfg.name] = pred
        np.save(OUT / f"sleep_fragmentation_proxy_oof_{cfg.name}.npy", pred)
        all_rows.append(summarize(train, cfg.name, pred))
    result = pd.concat(all_rows, ignore_index=True)
    result.to_csv(OUT / "sleep_fragmentation_proxy_results.csv", index=False)
    top = result.sort_values(["target", "best_blend_loss"]).groupby("target").head(5)
    top.to_csv(OUT / "sleep_fragmentation_proxy_top.csv", index=False)
    improved = result[result["delta_vs_current"] < 0].sort_values("delta_vs_current").head(1)
    if improved.empty:
        cfg = configs()[0]
    else:
        cfg = next(c for c in configs() if c.name == str(improved.iloc[0]["config"]))
    geo = geometry_guardrail(train, sub, cfg)
    geo.to_csv(OUT / "sleep_fragmentation_proxy_geometry_grid.csv", index=False)
    print(top.round(6).to_string(index=False))
    print("\nGeometry")
    print(geo[geo["target"].isin(["Q2", "Q3", "S4"])].round(6).to_string(index=False))
    print("wrote", OUT / "sleep_fragmentation_proxy_results.csv")


if __name__ == "__main__":
    main()
