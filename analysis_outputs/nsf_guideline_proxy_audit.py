from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

sys.path.append(str(Path(__file__).resolve().parent))
import deep_dive_analysis as d  # noqa: E402
import geometry_mask_cv_experiments as geom  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
S_TARGETS = ["S1", "S2", "S3", "S4"]
KEY = ["subject_id", "lifelog_date"]
SUB_KEY = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1e-5
GRID = np.array([0.0, 0.02, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30, 0.45, 0.60])

BASE_OOF = "final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy"
BASE_SUB = "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv"


@dataclass(frozen=True)
class ProxyConfig:
    target: str
    family: str
    columns: tuple[str, ...]
    c_value: float
    balanced: bool

    @property
    def name(self) -> str:
        bal = "bal" if self.balanced else "plain"
        c_tag = str(self.c_value).replace(".", "p")
        return f"{self.target}_{self.family}_c{c_tag}_{bal}"


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, EPS, 1.0 - EPS)


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    yy = y.astype(float)
    pp = clip(p)
    return float(-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp)).mean())


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([loss_col(y[:, j], pred[:, j]) for j in range(len(TARGETS))]))


def merge_features() -> pd.DataFrame:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    sub = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    all_rows = pd.concat(
        [
            train[SUB_KEY].assign(split="train"),
            sub[SUB_KEY].assign(split="submission"),
        ],
        ignore_index=True,
    ).sort_values(KEY).reset_index(drop=True)
    out = all_rows.copy()
    for name in [
        "sleep_interval_proxy_features.parquet",
        "sleep_fragmentation_proxy_features.parquet",
        "sleep_dynamics_proxy_features.parquet",
        "quiet_window_residual_features.parquet",
    ]:
        path = OUT / name
        if not path.exists():
            continue
        feat = pd.read_parquet(path)
        keep = [c for c in feat.columns if c not in {"sleep_date", "split"}]
        out = out.merge(feat[keep], on=KEY, how="left")
    return out


def existing(features: pd.DataFrame, cols: list[str]) -> tuple[str, ...]:
    return tuple(c for c in cols if c in features.columns)


def config_defs(features: pd.DataFrame) -> list[ProxyConfig]:
    groups: dict[str, dict[str, list[str]]] = {
        "S1": {
            "tst_duration": [
                "proxy_screen_duration_min",
                "proxy_screen_step_duration_min",
                "proxy_dyn_screen_duration_min",
                "proxy_dyn_screen_step_duration_min",
                "proxy_frag_screen_longest_duration_min",
                "proxy_frag_screen_step_longest_duration_min",
                "quiet_w21_32_screen_step_dur",
                "quiet_w22_32_screen_step_dur",
            ],
            "tst_relative": [
                "proxy_dyn_screen_duration_min_subj_center",
                "proxy_dyn_screen_duration_min_subj_z",
                "proxy_dyn_screen_step_duration_min_subj_center",
                "proxy_dyn_screen_step_duration_min_subj_z",
                "proxy_dyn_screen_step_duration_min_roll3_center_delta",
            ],
        },
        "S2": {
            "efficiency": [
                "proxy_frag_screen_candidate_quiet_frac",
                "proxy_frag_screen_step_candidate_quiet_frac",
                "proxy_frag_screen_step_longest_frac",
                "proxy_screen_screen_on_core_min",
                "proxy_screen_step_screen_on_core_min",
                "proxy_screen_step_step_core_sum",
            ],
            "efficiency_relative": [
                "proxy_dyn_screen_wake_after60_screen_on_core_min_subj_center",
                "proxy_dyn_screen_wake_after60_step_core_sum_subj_center",
                "proxy_dyn_screen_step_wake_after60_screen_on_core_min_subj_center",
                "proxy_dyn_screen_step_wake_after60_step_core_sum_subj_center",
            ],
        },
        "S3": {
            "latency_phase": [
                "proxy_screen_start_hour",
                "proxy_screen_step_start_hour",
                "proxy_dyn_screen_start_hour",
                "proxy_dyn_screen_step_start_hour",
                "quiet_w21_32_screen_step_start",
                "quiet_w22_32_screen_step_start",
                "proxy_screen_step_pre2h_screen_sum",
            ],
            "latency_relative": [
                "proxy_dyn_screen_start_hour_subj_center",
                "proxy_dyn_screen_step_start_hour_subj_center",
                "proxy_dyn_screen_step_start_hour_subj_z",
                "proxy_dyn_screen_step_start_hour_roll3_center_delta",
            ],
        },
        "S4": {
            "waso_fragment": [
                "proxy_frag_screen_fragmentation",
                "proxy_frag_screen_step_fragmentation",
                "proxy_frag_screen_gap_minutes_between_quiet",
                "proxy_frag_screen_step_gap_minutes_between_quiet",
                "proxy_dyn_screen_wake_after120_screen_on_core_min",
                "proxy_dyn_screen_step_wake_after120_screen_on_core_min",
                "proxy_dyn_screen_step_wake_after120_step_core_sum",
                "proxy_dyn_screen_step_wake_after120_active_burst_count",
            ],
            "waso_relative": [
                "proxy_dyn_screen_wake_after120_screen_on_core_min_subj_center",
                "proxy_dyn_screen_wake_after120_step_core_sum_subj_center",
                "proxy_dyn_screen_step_wake_after120_screen_on_core_min_subj_center",
                "proxy_dyn_screen_step_wake_after120_step_core_sum_subj_center",
                "proxy_dyn_screen_step_wake_after120_active_burst_count_subj_center",
            ],
        },
    }
    configs: list[ProxyConfig] = []
    for target, families in groups.items():
        for family, cols in families.items():
            present = existing(features, cols)
            if not present:
                continue
            for c_value in [0.03, 0.10, 0.30]:
                for balanced in [False, True]:
                    configs.append(ProxyConfig(target, family, present, c_value, balanced))
    return configs


def fit_predict(ref: pd.DataFrame, rows: pd.DataFrame, cfg: ProxyConfig) -> np.ndarray:
    y = ref[cfg.target].to_numpy(dtype=int)
    if len(np.unique(y)) < 2:
        return np.full(len(rows), np.clip(y.mean() if len(y) else 0.5, EPS, 1.0 - EPS), dtype=float)
    class_weight = "balanced" if cfg.balanced else None
    model = make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(),
        LogisticRegression(C=cfg.c_value, solver="liblinear", class_weight=class_weight, max_iter=500),
    )
    model.fit(ref[list(cfg.columns)], y)
    return clip(model.predict_proba(rows[list(cfg.columns)])[:, 1])


def oof_proxy(train_feat: pd.DataFrame, cfg: ProxyConfig) -> np.ndarray:
    pred = np.zeros(len(train_feat), dtype=float)
    for tr_idx, val_idx in d.make_folds(train_feat, "subject_blocks"):
        ref = train_feat.iloc[tr_idx].copy().reset_index(drop=True)
        val = train_feat.iloc[val_idx].copy().reset_index(drop=True)
        pred[val_idx] = fit_predict(ref, val, cfg)
    return clip(pred)


def repeated_subject_guard(train: pd.DataFrame, y: np.ndarray, base_col: np.ndarray, proxy_col: np.ndarray, seed: int) -> dict[str, float]:
    subjects = np.array(sorted(train["subject_id"].astype(str).unique()))
    rng = np.random.default_rng(seed)
    deltas: list[float] = []
    weights: list[float] = []
    for _ in range(360):
        picked = set(rng.choice(subjects, size=max(1, len(subjects) // 2), replace=False))
        sel = train["subject_id"].astype(str).isin(picked).to_numpy()
        hold = ~sel
        losses = [loss_col(y[sel], (1.0 - w) * base_col[sel] + w * proxy_col[sel]) for w in GRID]
        best_w = float(GRID[int(np.argmin(losses))])
        candidate = (1.0 - best_w) * base_col + best_w * proxy_col
        deltas.append(loss_col(y[hold], candidate[hold]) - loss_col(y[hold], base_col[hold]))
        weights.append(best_w)
    arr = np.asarray(deltas, dtype=float)
    return {
        "subject_guard_mean_delta": float(arr.mean()),
        "subject_guard_median_delta": float(np.median(arr)),
        "subject_guard_win_rate": float((arr < 0).mean()),
        "subject_guard_p25_delta": float(np.quantile(arr, 0.25)),
        "subject_guard_p75_delta": float(np.quantile(arr, 0.75)),
        "subject_guard_mean_selected_weight": float(np.mean(weights)),
    }


def geometry_delta(
    raw_train: pd.DataFrame,
    raw_sub: pd.DataFrame,
    feat: pd.DataFrame,
    cfg: ProxyConfig,
    weight: float,
    base: np.ndarray,
    target_idx: int,
) -> dict[str, float]:
    y_all = raw_train[TARGETS].to_numpy(dtype=int)
    deltas = []
    n_rows = 0
    for tr_idx, val_idx, _name in geom.geometry_folds(raw_train, raw_sub, n_repeats=8, seed=260526):
        ref = feat.iloc[tr_idx].copy().reset_index(drop=True)
        val = feat.iloc[val_idx].copy().reset_index(drop=True)
        proxy = fit_predict(ref, val, cfg)
        cand = (1.0 - weight) * base[val_idx, target_idx] + weight * proxy
        delta = loss_col(y_all[val_idx, target_idx], cand) - loss_col(y_all[val_idx, target_idx], base[val_idx, target_idx])
        deltas.append(delta)
        n_rows += len(val_idx)
    arr = np.asarray(deltas, dtype=float)
    return {
        "geometry_mean_delta": float(arr.mean()),
        "geometry_median_delta": float(np.median(arr)),
        "geometry_win_rate": float((arr < 0).mean()),
        "geometry_repeats": int(len(arr)),
        "geometry_scored_rows": int(n_rows),
    }


def evaluate_configs() -> tuple[pd.DataFrame, dict[str, np.ndarray], pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    raw_train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    raw_sub = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    feat_all = merge_features().sort_values(KEY).reset_index(drop=True)
    train_feat = feat_all[feat_all["split"].eq("train")].sort_values(KEY).reset_index(drop=True)
    sub_feat = feat_all[feat_all["split"].eq("submission")].sort_values(KEY).reset_index(drop=True)
    assert train_feat[KEY].equals(raw_train[KEY])
    assert sub_feat[KEY].equals(raw_sub[KEY])
    train_feat = train_feat.merge(raw_train[KEY + TARGETS], on=KEY, how="left")

    y = raw_train[TARGETS].to_numpy(dtype=int)
    base = clip(np.load(OUT / BASE_OOF))
    rows = []
    proxy_cache: dict[str, np.ndarray] = {}
    for cfg in config_defs(train_feat):
        target_idx = TARGETS.index(cfg.target)
        proxy = oof_proxy(train_feat, cfg)
        proxy_cache[cfg.name] = proxy
        base_loss = loss_col(y[:, target_idx], base[:, target_idx])
        proxy_loss = loss_col(y[:, target_idx], proxy)
        blend_losses = [loss_col(y[:, target_idx], (1.0 - w) * base[:, target_idx] + w * proxy) for w in GRID]
        best_i = int(np.argmin(blend_losses))
        best_w = float(GRID[best_i])
        row: dict[str, float | str | bool | int] = {
            "config": cfg.name,
            "target": cfg.target,
            "family": cfg.family,
            "columns": "|".join(cfg.columns),
            "n_columns": len(cfg.columns),
            "c_value": cfg.c_value,
            "balanced": cfg.balanced,
            "base_loss": base_loss,
            "proxy_loss": proxy_loss,
            "best_weight": best_w,
            "best_blend_loss": float(blend_losses[best_i]),
            "delta_vs_base": float(blend_losses[best_i] - base_loss),
        }
        if best_w > 0.0 and row["delta_vs_base"] < 0.0:
            row.update(repeated_subject_guard(raw_train, y[:, target_idx], base[:, target_idx], proxy, seed=91823 + len(rows) * 17))
            row.update(geometry_delta(raw_train, raw_sub, train_feat, cfg, best_w, base, target_idx))
        else:
            row.update(
                {
                    "subject_guard_mean_delta": 0.0,
                    "subject_guard_median_delta": 0.0,
                    "subject_guard_win_rate": 0.0,
                    "subject_guard_p25_delta": 0.0,
                    "subject_guard_p75_delta": 0.0,
                    "subject_guard_mean_selected_weight": 0.0,
                    "geometry_mean_delta": 0.0,
                    "geometry_median_delta": 0.0,
                    "geometry_win_rate": 0.0,
                    "geometry_repeats": 0,
                    "geometry_scored_rows": 0,
                }
            )
        row["passes_loose"] = bool(
            row["delta_vs_base"] <= -0.00015
            and row["subject_guard_mean_delta"] < 0.0
            and row["subject_guard_win_rate"] >= 0.56
            and row["geometry_mean_delta"] <= 0.00015
            and row["geometry_win_rate"] >= 0.50
        )
        row["passes_strict"] = bool(
            row["delta_vs_base"] <= -0.00035
            and row["subject_guard_mean_delta"] <= -0.00010
            and row["subject_guard_win_rate"] >= 0.62
            and row["geometry_mean_delta"] <= 0.0
            and row["geometry_win_rate"] >= 0.625
        )
        rows.append(row)
        print(
            f"[nsf] {cfg.name} delta={row['delta_vs_base']:.6f} "
            f"subj={row['subject_guard_mean_delta']:.6f} geom={row['geometry_mean_delta']:.6f}",
            flush=True,
        )
    result = pd.DataFrame(rows).sort_values(
        ["passes_strict", "passes_loose", "delta_vs_base", "geometry_mean_delta"],
        ascending=[False, False, True, True],
    ).reset_index(drop=True)
    return result, proxy_cache, raw_train, train_feat, sub_feat


def build_candidate(
    result: pd.DataFrame,
    proxy_cache: dict[str, np.ndarray],
    raw_train: pd.DataFrame,
    train_feat: pd.DataFrame,
    sub_feat: pd.DataFrame,
) -> None:
    base = clip(np.load(OUT / BASE_OOF))
    base_sub = pd.read_csv(OUT / BASE_SUB, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    pred = base.copy()
    chosen_rows = []
    for target in S_TARGETS:
        eligible = result[(result["target"].eq(target)) & (result["passes_loose"])].copy()
        if eligible.empty:
            continue
        best = eligible.iloc[0]
        cfg_name = str(best["config"])
        w = float(best["best_weight"])
        j = TARGETS.index(target)
        pred[:, j] = clip((1.0 - w) * pred[:, j] + w * proxy_cache[cfg_name])
        chosen_rows.append(best.to_dict())

    if not chosen_rows:
        pd.DataFrame(columns=result.columns).to_csv(OUT / "nsf_guideline_proxy_selected.csv", index=False)
        return

    chosen = pd.DataFrame(chosen_rows)
    chosen.to_csv(OUT / "nsf_guideline_proxy_selected.csv", index=False)
    np.save(OUT / "final_nsf_guideline_proxy_stage2_selected_oof.npy", pred)

    out = base_sub.copy()
    for row in chosen.to_dict("records"):
        cols = str(row["columns"]).split("|")
        cfg = ProxyConfig(
            target=str(row["target"]),
            family=str(row["family"]),
            columns=tuple(cols),
            c_value=float(row["c_value"]),
            balanced=bool(row["balanced"]),
        )
        proxy_sub = fit_predict(train_feat, sub_feat, cfg)
        w = float(row["best_weight"])
        out[str(row["target"])] = clip((1.0 - w) * out[str(row["target"])].to_numpy(dtype=float) + w * proxy_sub)
    out = out.sort_values(SUB_KEY).reset_index(drop=True)
    assert out[SUB_KEY].equals(sample[SUB_KEY])
    assert out[TARGETS].isna().sum().sum() == 0
    assert out.duplicated(SUB_KEY).sum() == 0
    out.to_csv(OUT / "submission_nsf_guideline_proxy_stage2_selected.csv", index=False)


def main() -> None:
    result, proxy_cache, raw_train, train_feat, sub_feat = evaluate_configs()
    result.to_csv(OUT / "nsf_guideline_proxy_audit.csv", index=False)
    result.groupby("target", group_keys=False).head(8).to_csv(OUT / "nsf_guideline_proxy_top_by_target.csv", index=False)
    build_candidate(result, proxy_cache, raw_train, train_feat, sub_feat)
    print(result.head(40).round(6).to_string(index=False))


if __name__ == "__main__":
    main()
