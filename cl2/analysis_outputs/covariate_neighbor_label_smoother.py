from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss

sys.path.append(str(Path(__file__).resolve().parent))
import calibration_experiments as cal  # noqa: E402
import deep_dive_analysis as d  # noqa: E402
import geometry_mask_cv_experiments as geom  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
TARGETS = d.TARGETS
KEY = d.KEY

GRID = np.array([0.0, 0.02, 0.03, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30, 0.45, 0.60])
BASE_OOF = OUT / "final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy"
BASE_SUB = OUT / "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv"


@dataclass(frozen=True)
class NeighborConfig:
    name: str
    group: str
    k: int
    dist_temp: float
    tau: float
    shrink: float
    min_dims: int = 3


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1.0 - 1e-5)


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    yy = y.astype(float)
    pp = clip(p)
    return float(-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp)).mean())


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([log_loss(y[:, j], clip(pred[:, j]), labels=[0, 1]) for j in range(y.shape[1])]))


def per_target_loss(y: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    return {target: loss_col(y[:, j], pred[:, j]) for j, target in enumerate(TARGETS)}


def read_sorted() -> tuple[pd.DataFrame, pd.DataFrame]:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    sub = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    return train.sort_values(KEY).reset_index(drop=True), sub.sort_values(KEY).reset_index(drop=True)


def load_feature_frame(train: pd.DataFrame, sub: pd.DataFrame) -> pd.DataFrame:
    keys = pd.concat([train[KEY], sub[KEY]], ignore_index=True).drop_duplicates(KEY).sort_values(KEY).reset_index(drop=True)
    frame = keys.copy()
    feature_files = [
        OUT / "sleep_interval_proxy_features.parquet",
        OUT / "sleep_fragmentation_proxy_features.parquet",
        OUT / "sleep_dynamics_proxy_features.parquet",
        OUT / "quiet_window_residual_features.parquet",
        OUT / "pre_sleep_relative_features.parquet",
    ]
    drop = set(TARGETS + ["sleep_date", "split", "pre_sleep_start_ts"])
    for path in feature_files:
        block = pd.read_parquet(path)
        cols = [c for c in block.columns if c in KEY or c not in drop]
        block = block[cols].copy()
        dup_cols = [c for c in block.columns if c not in KEY and c in frame.columns]
        if dup_cols:
            block = block.drop(columns=dup_cols)
        frame = frame.merge(block, on=KEY, how="left")
    return frame


def attach_features(rows: pd.DataFrame, features: pd.DataFrame) -> pd.DataFrame:
    out = rows.merge(features, on=KEY, how="left")
    return out.sort_values(KEY).reset_index(drop=True)


def _existing(df: pd.DataFrame, names: list[str]) -> list[str]:
    return [c for c in names if c in df.columns and pd.api.types.is_numeric_dtype(df[c])]


def _contains(df: pd.DataFrame, starts: list[str], tokens: list[str], max_cols: int | None = None) -> list[str]:
    cols: list[str] = []
    for col in df.columns:
        if not any(col.startswith(prefix) for prefix in starts):
            continue
        if any(token in col for token in tokens) and pd.api.types.is_numeric_dtype(df[col]):
            cols.append(col)
    cols = sorted(dict.fromkeys(cols))
    return cols[:max_cols] if max_cols is not None else cols


def feature_groups(df: pd.DataFrame) -> dict[str, list[str]]:
    interval = _existing(
        df,
        [
            "proxy_screen_obs_frac",
            "proxy_step_obs_frac",
            "proxy_hr_obs_frac",
            "proxy_watch_light_obs_frac",
            "proxy_screen_start_hour",
            "proxy_screen_end_hour",
            "proxy_screen_duration_min",
            "proxy_screen_mid_hour",
            "proxy_screen_charge_frac",
            "proxy_screen_hr_mean",
            "proxy_screen_hr_min",
            "proxy_screen_pre2h_screen_sum",
            "proxy_screen_pre2h_step_sum",
            "proxy_screen_pre2h_wlight_mean",
            "proxy_screen_post2h_screen_sum",
            "proxy_screen_post2h_step_sum",
            "proxy_screen_post2h_wlight_mean",
            "proxy_screen_step_start_hour",
            "proxy_screen_step_end_hour",
            "proxy_screen_step_duration_min",
            "proxy_screen_step_mid_hour",
            "proxy_screen_step_charge_frac",
            "proxy_screen_step_hr_mean",
            "proxy_screen_step_hr_min",
            "proxy_screen_step_pre2h_step_sum",
            "proxy_screen_step_pre2h_wlight_mean",
            "proxy_screen_step_post2h_step_sum",
            "proxy_screen_step_post2h_wlight_mean",
        ],
    )
    frag = _existing(
        df,
        [
            "proxy_frag_screen_total_quiet_min",
            "proxy_frag_screen_segment_count",
            "proxy_frag_screen_segment_count_ge30",
            "proxy_frag_screen_longest_duration_min",
            "proxy_frag_screen_mean_segment_duration_min",
            "proxy_frag_screen_longest_frac",
            "proxy_frag_screen_fragmentation",
            "proxy_frag_screen_longest_start_hour",
            "proxy_frag_screen_longest_end_hour",
            "proxy_frag_screen_charge_mean",
            "proxy_frag_screen_hr_mean",
            "proxy_frag_screen_wlight_mean",
            "proxy_frag_screen_active_between_step_sum",
            "proxy_frag_screen_step_total_quiet_min",
            "proxy_frag_screen_step_segment_count",
            "proxy_frag_screen_step_longest_duration_min",
            "proxy_frag_screen_step_fragmentation",
            "proxy_frag_screen_step_charge_mean",
            "proxy_frag_screen_step_hr_mean",
            "proxy_frag_screen_step_wlight_mean",
            "proxy_frag_screen_step_active_between_step_sum",
        ],
    )
    dyn = _existing(
        df,
        [
            "proxy_dyn_screen_duration_min",
            "proxy_dyn_screen_start_hour",
            "proxy_dyn_screen_end_hour",
            "proxy_dyn_screen_mid_hour",
            "proxy_dyn_screen_hr_mean_core",
            "proxy_dyn_screen_hr_min_core",
            "proxy_dyn_screen_hr_drop_pre_to_min",
            "proxy_dyn_screen_hr_drop_candidate_to_min",
            "proxy_dyn_screen_hr_rebound_post_to_min",
            "proxy_dyn_screen_core_late_minus_early",
            "proxy_dyn_screen_wake_after60_screen_on_core_min",
            "proxy_dyn_screen_wake_after60_step_core_sum",
            "proxy_dyn_screen_wake_after120_screen_on_core_min",
            "proxy_dyn_screen_wake_after120_step_core_sum",
            "proxy_dyn_screen_first_activity_after_min",
            "proxy_dyn_screen_first_screen_after_min",
            "proxy_dyn_screen_post120_wlight_mean",
            "proxy_dyn_screen_charge_frac",
            "proxy_dyn_screen_step_duration_min",
            "proxy_dyn_screen_step_start_hour",
            "proxy_dyn_screen_step_end_hour",
            "proxy_dyn_screen_step_hr_mean_core",
            "proxy_dyn_screen_step_hr_min_core",
            "proxy_dyn_screen_step_wake_after120_step_core_sum",
            "proxy_dyn_screen_step_first_activity_after_min",
            "proxy_dyn_screen_step_charge_frac",
        ],
    )
    quiet = _contains(
        df,
        starts=["quiet_w19_32_", "quiet_w20_32_", "quiet_w21_32_", "quiet_w22_32_", "quiet_w20_33_", "quiet_w21_33_"],
        tokens=["_dur", "_start", "_end", "_hr_mean", "_pre_screen_on", "_post_screen_on"],
        max_cols=96,
    )
    presleep = _contains(
        df,
        starts=["presleep_screen_", "presleep_activity_", "presleep_charge_", "presleep_watch_light_", "presleep_mobile_light_"],
        tokens=["pre1h", "pre3h", "pre6h", "core5h", "post2h"],
        max_cols=120,
    )
    groups = {
        "interval": interval,
        "fragment": frag,
        "dynamics": dyn,
        "quiet": quiet,
        "sleep_core": interval + frag + dyn,
        "sleep_quiet": interval + frag + dyn + quiet,
        "presleep": presleep,
        "sleep_presleep": interval + frag + dyn + presleep,
    }
    out: dict[str, list[str]] = {}
    for name, cols in groups.items():
        seen: set[str] = set()
        deduped = []
        for col in cols:
            if col in seen:
                continue
            s = pd.to_numeric(df[col], errors="coerce")
            if s.notna().sum() >= 80 and s.nunique(dropna=True) > 1:
                deduped.append(col)
                seen.add(col)
        if deduped:
            out[name] = deduped
    return out


def subject_prior(ref: pd.DataFrame, rows: pd.DataFrame, shrink: float) -> np.ndarray:
    return cal.subject_prior(ref, rows, shrink)


def _subject_scaled_arrays(ref: pd.DataFrame, rows: pd.DataFrame, cols: list[str]) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    ref_raw = ref[cols].apply(pd.to_numeric, errors="coerce").to_numpy(dtype=float)
    row_raw = rows[cols].apply(pd.to_numeric, errors="coerce").to_numpy(dtype=float)
    ok_any = np.isfinite(ref_raw).sum(axis=0) >= 2
    if not ok_any.any():
        empty_ref = np.zeros((len(ref), 0), dtype=float)
        empty_row = np.zeros((len(rows), 0), dtype=float)
        return empty_ref, empty_row, np.zeros_like(empty_ref, dtype=bool), np.zeros_like(empty_row, dtype=bool)
    ref_raw = ref_raw[:, ok_any]
    row_raw = row_raw[:, ok_any]
    med = np.nanmedian(ref_raw, axis=0)
    q75 = np.nanpercentile(ref_raw, 75, axis=0)
    q25 = np.nanpercentile(ref_raw, 25, axis=0)
    iqr = q75 - q25
    std = np.nanstd(ref_raw, axis=0)
    scale = np.where(np.isfinite(iqr) & (iqr > 1e-9), iqr / 1.349, std)
    usable = np.isfinite(med) & np.isfinite(scale) & (scale > 1e-9)
    if not usable.any():
        empty_ref = np.zeros((len(ref), 0), dtype=float)
        empty_row = np.zeros((len(rows), 0), dtype=float)
        return empty_ref, empty_row, np.zeros_like(empty_ref, dtype=bool), np.zeros_like(empty_row, dtype=bool)
    ref_raw = ref_raw[:, usable]
    row_raw = row_raw[:, usable]
    med = med[usable]
    scale = scale[usable]
    ref_valid = np.isfinite(ref_raw)
    row_valid = np.isfinite(row_raw)
    ref_z = np.where(ref_valid, (ref_raw - med) / scale, 0.0)
    row_z = np.where(row_valid, (row_raw - med) / scale, 0.0)
    return ref_z, row_z, ref_valid, row_valid


def covariate_neighbor_prior(ref: pd.DataFrame, rows: pd.DataFrame, cols: list[str], cfg: NeighborConfig) -> np.ndarray:
    fallback = subject_prior(ref, rows, cfg.shrink)
    pred = fallback.copy()
    row_sids = rows["subject_id"].astype(str).to_numpy()
    row_dates = pd.to_datetime(rows["lifelog_date"]).to_numpy(dtype="datetime64[D]")
    for sid, ref_g in ref.groupby("subject_id", sort=False):
        sid = str(sid)
        row_idx = np.where(row_sids == sid)[0]
        if row_idx.size == 0:
            continue
        ref_g = ref_g.sort_values("lifelog_date").reset_index(drop=True)
        row_g = rows.iloc[row_idx].copy().reset_index(drop=True)
        ref_z, row_z, ref_valid, row_valid = _subject_scaled_arrays(ref_g, row_g, cols)
        if ref_z.shape[1] < cfg.min_dims:
            continue
        valid = row_valid[:, None, :] & ref_valid[None, :, :]
        valid_n = valid.sum(axis=2)
        diff = row_z[:, None, :] - ref_z[None, :, :]
        dist = np.divide((diff * diff * valid).sum(axis=2), valid_n, out=np.full(valid_n.shape, np.inf), where=valid_n > 0)
        dist[valid_n < cfg.min_dims] = np.inf
        if not np.isfinite(dist).any():
            continue
        ref_dates = pd.to_datetime(ref_g["lifelog_date"]).to_numpy(dtype="datetime64[D]")
        gaps = np.abs((row_dates[row_idx, None] - ref_dates[None, :]).astype("timedelta64[D]").astype(float))
        weights = np.exp(-0.5 * dist / (cfg.dist_temp * cfg.dist_temp))
        if cfg.tau > 0 and np.isfinite(cfg.tau):
            weights *= np.exp(-gaps / cfg.tau)
        weights[~np.isfinite(dist)] = 0.0
        labels = ref_g[TARGETS].to_numpy(dtype=float)
        for local_i, global_i in enumerate(row_idx):
            w = weights[local_i]
            if not np.isfinite(w).any() or w.max() <= 0:
                continue
            if cfg.k < len(w):
                keep = np.argpartition(w, -cfg.k)[-cfg.k:]
                mask = np.zeros_like(w, dtype=bool)
                mask[keep] = True
                w = np.where(mask, w, 0.0)
            sum_w = float(w.sum())
            if sum_w <= 1e-12:
                continue
            local = (w[:, None] * labels).sum(axis=0) / sum_w
            eff_n = (sum_w * sum_w) / max(float(np.square(w).sum()), 1e-12)
            pred[global_i] = (eff_n * local + cfg.shrink * fallback[global_i]) / (eff_n + cfg.shrink)
    return clip(pred)


def configs(groups: dict[str, list[str]]) -> list[NeighborConfig]:
    out: list[NeighborConfig] = []
    for group in ["interval", "fragment", "dynamics", "quiet", "sleep_core", "sleep_quiet", "presleep", "sleep_presleep"]:
        if group not in groups:
            continue
        for k in [3, 5, 8]:
            for dist_temp in [0.75, 1.25, 2.0]:
                for tau in [7.0, 21.0, 9999.0]:
                    shrink = 2.0 if group in {"quiet", "sleep_quiet"} else 4.0
                    name = f"knn_{group}_k{k}_dt{dist_temp:g}_tau{tau:g}_sh{shrink:g}"
                    out.append(NeighborConfig(name, group, k, dist_temp, tau, shrink))
    return out


def oof_prior(df: pd.DataFrame, cols: list[str], cfg: NeighborConfig) -> np.ndarray:
    pred = np.zeros((len(df), len(TARGETS)), dtype=float)
    for tr_idx, val_idx in d.make_folds(df, "subject_blocks"):
        ref = df.iloc[tr_idx].copy().reset_index(drop=True)
        val = df.iloc[val_idx].copy().reset_index(drop=True)
        pred[val_idx] = covariate_neighbor_prior(ref, val, cols, cfg)
    return clip(pred)


def repeated_subject_guardrail(
    train: pd.DataFrame,
    y: np.ndarray,
    base: np.ndarray,
    prior: np.ndarray,
    target_idx: int,
    seed: int,
) -> dict[str, float]:
    subjects = np.array(sorted(train["subject_id"].astype(str).unique()))
    rng = np.random.default_rng(seed)
    deltas = []
    weights = []
    for _ in range(260):
        picked = set(rng.choice(subjects, size=max(1, len(subjects) // 2), replace=False))
        sel = train["subject_id"].astype(str).isin(picked).to_numpy()
        hold = ~sel
        best = None
        for w in GRID:
            p = (1.0 - w) * base[:, target_idx] + w * prior[:, target_idx]
            sel_loss = loss_col(y[sel, target_idx], p[sel])
            if best is None or sel_loss < best[0]:
                best = (sel_loss, float(w), p)
        assert best is not None
        hold_base = loss_col(y[hold, target_idx], base[hold, target_idx])
        hold_blend = loss_col(y[hold, target_idx], best[2][hold])
        deltas.append(float(hold_blend - hold_base))
        weights.append(best[1])
    arr = np.asarray(deltas)
    w_arr = np.asarray(weights)
    return {
        "guard_mean_delta": float(arr.mean()),
        "guard_median_delta": float(np.median(arr)),
        "guard_p25_delta": float(np.quantile(arr, 0.25)),
        "guard_p75_delta": float(np.quantile(arr, 0.75)),
        "guard_win_rate": float((arr < 0).mean()),
        "guard_mean_weight": float(w_arr.mean()),
        "guard_zero_weight_rate": float((w_arr == 0.0).mean()),
    }


def geometry_guardrail(train_feat: pd.DataFrame, sub: pd.DataFrame, cols: list[str], cfg: NeighborConfig, target_weights: np.ndarray) -> dict[str, float]:
    folds = geom.geometry_folds(train_feat[KEY + TARGETS], sub, n_repeats=8)
    deltas = []
    target_deltas = {target: [] for target in TARGETS}
    for tr_idx, val_idx, _ in folds:
        ref = train_feat.iloc[tr_idx].copy().reset_index(drop=True)
        val = train_feat.iloc[val_idx].copy().reset_index(drop=True)
        base = cal.temporal_base(ref, val)
        prior = covariate_neighbor_prior(ref, val, cols, cfg)
        pred = base.copy()
        for j, w in enumerate(target_weights):
            pred[:, j] = (1.0 - w) * base[:, j] + w * prior[:, j]
        y_val = val[TARGETS].to_numpy(dtype=int)
        base_loss = mean_loss(y_val, base)
        pred_loss = mean_loss(y_val, pred)
        deltas.append(float(pred_loss - base_loss))
        for j, target in enumerate(TARGETS):
            target_deltas[target].append(loss_col(y_val[:, j], pred[:, j]) - loss_col(y_val[:, j], base[:, j]))
    out = {
        "geom_mean_delta": float(np.mean(deltas)),
        "geom_median_delta": float(np.median(deltas)),
        "geom_win_rate": float((np.asarray(deltas) < 0).mean()),
    }
    for target in TARGETS:
        arr = np.asarray(target_deltas[target])
        out[f"geom_{target}_delta"] = float(arr.mean())
    return out


def scan(args: argparse.Namespace) -> tuple[pd.DataFrame, dict[str, np.ndarray], dict[str, NeighborConfig], dict[str, list[str]], pd.DataFrame, pd.DataFrame]:
    train, sub = read_sorted()
    features = load_feature_frame(train, sub)
    train_feat = attach_features(train, features)
    sub_feat = attach_features(sub, features)
    groups = feature_groups(train_feat)
    base = clip(np.load(args.base_oof))
    y = train_feat[TARGETS].to_numpy(dtype=int)
    cfgs = configs(groups)
    if args.max_configs > 0:
        cfgs = cfgs[: args.max_configs]

    rows = []
    priors: dict[str, np.ndarray] = {}
    cfg_lookup: dict[str, NeighborConfig] = {}
    for i, cfg in enumerate(cfgs):
        prior = oof_prior(train_feat, groups[cfg.group], cfg)
        priors[cfg.name] = prior
        cfg_lookup[cfg.name] = cfg
        target_weights = np.zeros(len(TARGETS), dtype=float)
        row = {
            "model": cfg.name,
            "group": cfg.group,
            "n_features": len(groups[cfg.group]),
            "k": cfg.k,
            "dist_temp": cfg.dist_temp,
            "tau": cfg.tau,
            "shrink": cfg.shrink,
            "base_mean": mean_loss(y, base),
            "prior_mean": mean_loss(y, prior),
        }
        pred = base.copy()
        for j, target in enumerate(TARGETS):
            base_loss = loss_col(y[:, j], base[:, j])
            prior_loss = loss_col(y[:, j], prior[:, j])
            losses = [loss_col(y[:, j], (1.0 - w) * base[:, j] + w * prior[:, j]) for w in GRID]
            best_i = int(np.argmin(losses))
            best_w = float(GRID[best_i])
            target_weights[j] = best_w
            pred[:, j] = (1.0 - best_w) * base[:, j] + best_w * prior[:, j]
            row[f"{target}_base_loss"] = base_loss
            row[f"{target}_prior_loss"] = prior_loss
            row[f"{target}_weight"] = best_w
            row[f"{target}_delta"] = float(losses[best_i] - base_loss)
            if best_w > 0 and losses[best_i] < base_loss:
                guard = repeated_subject_guardrail(train_feat, y, base, prior, j, seed=261111 + 17 * i + j)
            else:
                guard = {
                    "guard_mean_delta": 0.0,
                    "guard_median_delta": 0.0,
                    "guard_p25_delta": 0.0,
                    "guard_p75_delta": 0.0,
                    "guard_win_rate": 0.0,
                    "guard_mean_weight": 0.0,
                    "guard_zero_weight_rate": 1.0,
                }
            for key, value in guard.items():
                row[f"{target}_{key}"] = value
        row["blend_mean"] = mean_loss(y, pred)
        row["blend_delta"] = float(row["blend_mean"] - row["base_mean"])
        row["nonzero_targets"] = ",".join([TARGETS[j] for j, w in enumerate(target_weights) if w > 0])
        row["target_weights"] = ",".join([f"{TARGETS[j]}:{target_weights[j]:g}" for j in range(len(TARGETS)) if target_weights[j] > 0])
        row["passes_loose"] = bool(
            row["blend_delta"] <= -0.0005
            and any(
                row[f"{target}_delta"] <= -0.0005
                and row[f"{target}_guard_mean_delta"] < 0.0
                and row[f"{target}_guard_win_rate"] >= 0.58
                for target in TARGETS
            )
        )
        row["passes_strict"] = bool(
            row["blend_delta"] <= -0.0015
            and all(
                row[f"{target}_weight"] == 0.0
                or (
                    row[f"{target}_delta"] <= -0.0005
                    and row[f"{target}_guard_mean_delta"] <= -0.0001
                    and row[f"{target}_guard_win_rate"] >= 0.62
                )
                for target in TARGETS
            )
        )
        rows.append(row)
        if i % 20 == 0:
            print(f"[knn prior] {i}/{len(cfgs)} {cfg.name} blend_delta={row['blend_delta']:.6f}", flush=True)

    result = pd.DataFrame(rows).sort_values(["passes_strict", "passes_loose", "blend_delta"], ascending=[False, False, True])
    return result, priors, cfg_lookup, groups, train_feat, sub_feat


def make_candidate(
    name: str,
    result: pd.DataFrame,
    priors: dict[str, np.ndarray],
    cfg_lookup: dict[str, NeighborConfig],
    groups: dict[str, list[str]],
    train_feat: pd.DataFrame,
    sub_feat: pd.DataFrame,
    args: argparse.Namespace,
) -> dict[str, object]:
    base_oof = clip(np.load(args.base_oof))
    base_sub_df = pd.read_csv(args.base_submission, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    base_sub = clip(base_sub_df[TARGETS].to_numpy(dtype=float))
    cfg = cfg_lookup[name]
    row = result[result["model"].eq(name)].iloc[0]
    weights = np.asarray([float(row[f"{target}_weight"]) for target in TARGETS], dtype=float)
    sub_prior = covariate_neighbor_prior(train_feat, sub_feat, groups[cfg.group], cfg)
    oof_prior = priors[name]
    oof_pred = base_oof.copy()
    sub_pred = base_sub.copy()
    for j, w in enumerate(weights):
        oof_pred[:, j] = (1.0 - w) * base_oof[:, j] + w * oof_prior[:, j]
        sub_pred[:, j] = (1.0 - w) * base_sub[:, j] + w * sub_prior[:, j]
    out = base_sub_df[["subject_id", "sleep_date", "lifelog_date"]].copy()
    for j, target in enumerate(TARGETS):
        out[target] = clip(sub_pred[:, j])
    suffix = name.replace(".", "p").replace("9999", "inf")
    file_name = f"submission_covknn_stage2_{suffix}.csv"
    oof_name = f"final_covknn_stage2_{suffix}_oof.npy"
    out.to_csv(OUT / file_name, index=False)
    np.save(OUT / oof_name, clip(oof_pred))
    return {
        "model": name,
        "file": file_name,
        "oof_file": oof_name,
        "weights": ",".join([f"{TARGETS[j]}:{weights[j]:g}" for j in range(len(TARGETS)) if weights[j] > 0]),
        "oof_mean": mean_loss(train_feat[TARGETS].to_numpy(dtype=int), oof_pred),
        "distance_abs_mean_vs_stage2": float(np.abs(sub_pred - base_sub).mean()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-oof", type=Path, default=BASE_OOF)
    parser.add_argument("--base-submission", type=Path, default=BASE_SUB)
    parser.add_argument("--prefix", default="covariate_neighbor_stage2")
    parser.add_argument("--max-configs", type=int, default=0)
    parser.add_argument("--top-geometry", type=int, default=8)
    args = parser.parse_args()

    result, priors, cfg_lookup, groups, train_feat, sub_feat = scan(args)
    result.to_csv(OUT / f"{args.prefix}_scan.csv", index=False)
    result.groupby("group", group_keys=False).head(5).to_csv(OUT / f"{args.prefix}_top_by_group.csv", index=False)
    selected = result[result["passes_loose"]].head(max(args.top_geometry, 1)).copy()
    geom_rows = []
    for row in selected.itertuples(index=False):
        cfg = cfg_lookup[str(row.model)]
        weights = np.asarray([float(getattr(row, f"{target}_weight")) for target in TARGETS], dtype=float)
        grow = {"model": str(row.model)}
        grow.update(geometry_guardrail(train_feat, sub_feat[KEY], groups[cfg.group], cfg, weights))
        geom_rows.append(grow)
    geom_df = pd.DataFrame(geom_rows)
    if not geom_df.empty:
        merged = selected.merge(geom_df, on="model", how="left")
        merged.to_csv(OUT / f"{args.prefix}_selected_geometry.csv", index=False)
        candidate_rows = []
        for row in merged.sort_values(["geom_mean_delta", "blend_delta"]).head(3).itertuples(index=False):
            candidate_rows.append(make_candidate(str(row.model), result, priors, cfg_lookup, groups, train_feat, sub_feat, args))
        pd.DataFrame(candidate_rows).to_csv(OUT / f"{args.prefix}_candidate_files.csv", index=False)
    else:
        selected.to_csv(OUT / f"{args.prefix}_selected_geometry.csv", index=False)
        pd.DataFrame().to_csv(OUT / f"{args.prefix}_candidate_files.csv", index=False)

    print(result.head(30).round(6).to_string(index=False))
    print("wrote", OUT / f"{args.prefix}_scan.csv")
    if not geom_df.empty:
        print("\n[geometry]")
        print(geom_df.round(6).to_string(index=False))


if __name__ == "__main__":
    main()
