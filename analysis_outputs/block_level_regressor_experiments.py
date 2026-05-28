from __future__ import annotations

import sys
import warnings
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.exceptions import ConvergenceWarning
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import log_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

sys.path.append(str(Path(__file__).resolve().parent))
import calibration_experiments as cal  # noqa: E402
import deep_dive_analysis as d  # noqa: E402


OUT = Path(__file__).resolve().parent
TARGETS = d.TARGETS
KEY = d.KEY
EPS = 1e-5


@dataclass(frozen=True)
class RegressorConfig:
    k: int
    alpha: float
    blend: float

    @property
    def name(self) -> str:
        return f"k{self.k}_a{self.alpha:g}_b{self.blend:g}"


CONFIGS = [
    RegressorConfig(k, alpha, blend)
    for k in [8, 30, 80]
    for alpha in [10.0, 50.0, 200.0]
    for blend in [0.15, 0.35, 0.70]
]


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, EPS, 1 - EPS)


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([log_loss(y[:, j], clip(pred[:, j]), labels=[0, 1]) for j in range(y.shape[1])]))


def per_target_loss(y: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    return {target: log_loss(y[:, j], clip(pred[:, j]), labels=[0, 1]) for j, target in enumerate(TARGETS)}


def weighted_rate_logloss(rate: np.ndarray, pred: np.ndarray, weight: np.ndarray) -> float:
    p = clip(pred.astype(float))
    loss = -(rate * np.log(p) + (1.0 - rate) * np.log(1.0 - p))
    return float(np.average(loss, weights=weight))


def sensor_feature_cols(rows: pd.DataFrame) -> list[str]:
    excluded = set(TARGETS + KEY + ["sleep_date", "split", "dow", "month"])
    cols = []
    for col in rows.columns:
        if col in excluded:
            continue
        if not pd.api.types.is_numeric_dtype(rows[col]):
            continue
        # Keep only daily sensor/calendar features from the deep matrix. Target-history
        # features are added explicitly below to avoid accidental fold leakage.
        if col.startswith("hist_"):
            continue
        cols.append(col)
    return cols


def unknown_block_index(ref: pd.DataFrame, rows: pd.DataFrame) -> pd.DataFrame:
    known = ref[KEY].copy()
    known["_kind"] = "known"
    unknown = rows[KEY].copy()
    unknown["_kind"] = "unknown"
    unknown["_row_pos"] = np.arange(len(rows))
    full = pd.concat([known, unknown], ignore_index=True, sort=False).sort_values(KEY).reset_index(drop=True)
    full["_block"] = full.groupby("subject_id")["_kind"].transform(lambda s: s.ne(s.shift()).cumsum())
    return full[full["_kind"].eq("unknown")].copy()


def add_sensor_block_stats(feat: dict[str, float | str], block_rows: pd.DataFrame, cols: list[str]) -> None:
    if not cols:
        return
    arr = block_rows[cols].replace([np.inf, -np.inf], np.nan)
    means = arr.mean(axis=0, skipna=True)
    stds = arr.std(axis=0, skipna=True)
    first = arr.iloc[0]
    last = arr.iloc[-1]
    miss = arr.isna().mean(axis=0)
    for col in cols:
        feat[f"m__{col}"] = float(means[col]) if pd.notna(means[col]) else np.nan
        # std and delta are only informative for multi-row blocks. Keeping them as 0
        # for single-row blocks gives the model an explicit "no within-block variation" state.
        feat[f"s__{col}"] = float(stds[col]) if pd.notna(stds[col]) else 0.0
        if pd.notna(first[col]) and pd.notna(last[col]):
            feat[f"d__{col}"] = float(last[col] - first[col])
        else:
            feat[f"d__{col}"] = np.nan
        feat[f"na__{col}"] = float(miss[col])


def block_features(
    ref: pd.DataFrame,
    rows: pd.DataFrame,
    sensor_cols: list[str],
) -> tuple[pd.DataFrame, dict[int, np.ndarray], np.ndarray]:
    rows = rows.reset_index(drop=True)
    base = cal.temporal_base(ref, rows)
    unknown = unknown_block_index(ref, rows)
    ref_by_subject = {
        sid: g.sort_values("lifelog_date").reset_index(drop=True)
        for sid, g in ref.groupby("subject_id", sort=False)
    }
    subj_min = pd.concat([ref[KEY], rows[KEY]], ignore_index=True).groupby("subject_id")["lifelog_date"].min()
    subj_max = pd.concat([ref[KEY], rows[KEY]], ignore_index=True).groupby("subject_id")["lifelog_date"].max()

    feature_rows: list[dict[str, float | str]] = []
    block_locs: dict[int, np.ndarray] = {}
    block_id = 0
    for (sid, bid), block in unknown.groupby(["subject_id", "_block"], sort=False):
        locs = block["_row_pos"].to_numpy(dtype=int)
        block_rows = rows.iloc[locs].copy()
        start = block_rows["lifelog_date"].min()
        end = block_rows["lifelog_date"].max()
        n = len(block_rows)
        span = max(int((end - start).days) + 1, 1)
        subj_span = max(int((subj_max.loc[sid] - subj_min.loc[sid]).days), 1)
        mid_day = start + (end - start) / 2
        feat: dict[str, float | str] = {
            "block_id": block_id,
            "subject_id_code": float(int(str(sid).replace("id", ""))),
            "n_rows": float(n),
            "span_days": float(span),
            "coverage_density": float(n / span),
            "start_dow": float(start.dayofweek),
            "end_dow": float(end.dayofweek),
            "start_month": float(start.month),
            "mid_subject_frac": float((mid_day - subj_min.loc[sid]).days / subj_span),
            "start_subject_day": float((start - subj_min.loc[sid]).days),
            "end_subject_day": float((end - subj_min.loc[sid]).days),
        }
        for known_sid in sorted(ref["subject_id"].astype(str).unique()):
            feat[f"sid__{known_sid}"] = float(str(sid) == known_sid)

        hist = ref_by_subject.get(sid)
        if hist is None or hist.empty:
            for target in TARGETS:
                feat[f"subj_prior__{target}"] = float(ref[target].mean())
            feat["has_prev"] = 0.0
            feat["has_next"] = 0.0
            feat["prev_gap"] = np.nan
            feat["next_gap"] = np.nan
        else:
            before = hist[hist["lifelog_date"] < start]
            after = hist[hist["lifelog_date"] > end]
            feat["has_prev"] = float(not before.empty)
            feat["has_next"] = float(not after.empty)
            feat["prev_gap"] = float((start - before["lifelog_date"].max()).days) if not before.empty else np.nan
            feat["next_gap"] = float((after["lifelog_date"].min() - end).days) if not after.empty else np.nan
            for target in TARGETS:
                feat[f"subj_prior__{target}"] = float(hist[target].mean())
                feat[f"base_mean__{target}"] = float(base[locs, TARGETS.index(target)].mean())
                feat[f"base_std__{target}"] = float(base[locs, TARGETS.index(target)].std()) if len(locs) > 1 else 0.0
                feat[f"base_delta__{target}"] = float(base[locs[-1], TARGETS.index(target)] - base[locs[0], TARGETS.index(target)])
                if before.empty:
                    feat[f"prev_edge__{target}"] = np.nan
                else:
                    feat[f"prev_edge__{target}"] = float(before.iloc[-1][target])
                if after.empty:
                    feat[f"next_edge__{target}"] = np.nan
                else:
                    feat[f"next_edge__{target}"] = float(after.iloc[0][target])
                if not before.empty and not after.empty:
                    feat[f"edge_same__{target}"] = float(before.iloc[-1][target] == after.iloc[0][target])
                    feat[f"edge_mean__{target}"] = float((before.iloc[-1][target] + after.iloc[0][target]) / 2.0)
                else:
                    feat[f"edge_same__{target}"] = 0.0
                    feat[f"edge_mean__{target}"] = np.nan
                for window in [1, 3, 5, 10]:
                    feat[f"prev_w{window}__{target}"] = (
                        float(before.tail(window)[target].mean()) if not before.empty else np.nan
                    )
                    feat[f"next_w{window}__{target}"] = (
                        float(after.head(window)[target].mean()) if not after.empty else np.nan
                    )
                    if not before.empty and not after.empty:
                        feat[f"around_w{window}__{target}"] = float(
                            pd.concat([before.tail(window)[target], after.head(window)[target]]).mean()
                        )
                    else:
                        feat[f"around_w{window}__{target}"] = np.nan

        add_sensor_block_stats(feat, block_rows, sensor_cols)
        feature_rows.append(feat)
        block_locs[block_id] = locs
        block_id += 1

    features = pd.DataFrame(feature_rows).set_index("block_id", drop=False)
    return features, block_locs, base


def target_rates(rows: pd.DataFrame, block_locs: dict[int, np.ndarray]) -> pd.DataFrame:
    records = []
    for bid, locs in block_locs.items():
        block = rows.reset_index(drop=True).iloc[locs]
        rec = {"block_id": bid, "n_rows": len(block)}
        for target in TARGETS:
            rec[f"rate__{target}"] = float(block[target].mean())
        records.append(rec)
    return pd.DataFrame(records).set_index("block_id", drop=False)


def make_training_blocks(train_rows: pd.DataFrame, sensor_cols: list[str]) -> pd.DataFrame:
    blocks = []
    for inner_fold, (tr_idx, val_idx) in enumerate(d.make_folds(train_rows, "subject_blocks")):
        ref = train_rows.iloc[tr_idx].copy().reset_index(drop=True)
        val = train_rows.iloc[val_idx].copy().reset_index(drop=True)
        feats, locs, _ = block_features(ref, val, sensor_cols)
        rates = target_rates(val, locs)
        merged = feats.join(rates[[f"rate__{t}" for t in TARGETS] + ["n_rows"]], rsuffix="_target")
        merged["inner_fold"] = inner_fold
        blocks.append(merged)
    return pd.concat(blocks, ignore_index=True)


def feature_columns(samples: pd.DataFrame) -> list[str]:
    excluded = {"block_id", "inner_fold", "n_rows_target"} | {f"rate__{t}" for t in TARGETS}
    return [
        col
        for col in samples.columns
        if col not in excluded and pd.api.types.is_numeric_dtype(samples[col])
    ]


def make_model(cfg: RegressorConfig, n_features: int) -> Pipeline:
    k = min(cfg.k, max(n_features, 1))
    return Pipeline(
        [
            ("impute", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
            ("select", SelectKBest(score_func=f_regression, k=k)),
            ("ridge", Ridge(alpha=cfg.alpha)),
        ]
    )


def fit_predict_block(
    samples: pd.DataFrame,
    pred_features: pd.DataFrame,
    target: str,
    cfg: RegressorConfig,
) -> np.ndarray:
    cols = feature_columns(samples)
    model = make_model(cfg, len(cols))
    y = samples[f"rate__{target}"].to_numpy(dtype=float)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        warnings.simplefilter("ignore", category=ConvergenceWarning)
        model.fit(samples[cols], y)
    return clip(model.predict(pred_features[cols]))


def select_configs(samples: pd.DataFrame) -> dict[str, RegressorConfig]:
    cols = feature_columns(samples)
    selected: dict[str, RegressorConfig] = {}
    folds = sorted(samples["inner_fold"].unique())
    for target in TARGETS:
        best_cfg = CONFIGS[0]
        best_loss = np.inf
        for cfg in CONFIGS:
            pred = np.zeros(len(samples), dtype=float)
            for fold in folds:
                tr = samples[samples["inner_fold"] != fold]
                va = samples[samples["inner_fold"] == fold]
                if tr.empty or va.empty:
                    continue
                model = make_model(cfg, len(cols))
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", category=RuntimeWarning)
                    warnings.simplefilter("ignore", category=ConvergenceWarning)
                    model.fit(tr[cols], tr[f"rate__{target}"])
                raw = clip(model.predict(va[cols]))
                base_rate = va[f"base_mean__{target}"].to_numpy(dtype=float)
                pred[va.index.to_numpy()] = clip((1.0 - cfg.blend) * base_rate + cfg.blend * raw)
            rate = samples[f"rate__{target}"].to_numpy(dtype=float)
            weight = samples["n_rows_target"].to_numpy(dtype=float)
            loss = weighted_rate_logloss(rate, pred, weight)
            if loss < best_loss:
                best_loss = loss
                best_cfg = cfg
        selected[target] = best_cfg
    return selected


def nested_oof(train: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray, np.ndarray]:
    sensor_cols = sensor_feature_cols(train)
    y = train[TARGETS].to_numpy()
    pred_base = np.zeros_like(y, dtype=float)
    pred_reg = np.zeros_like(y, dtype=float)
    selected_rows = []

    for fold_id, (tr_idx, val_idx) in enumerate(d.make_folds(train, "subject_blocks")):
        outer_train = train.iloc[tr_idx].copy().reset_index(drop=True)
        outer_val = train.iloc[val_idx].copy().reset_index(drop=True)
        samples = make_training_blocks(outer_train, sensor_cols)
        configs = select_configs(samples)
        pred_feats, block_locs, base_val = block_features(outer_train, outer_val, sensor_cols)
        pred_base[val_idx] = base_val
        for target in TARGETS:
            cfg = configs[target]
            raw_block = fit_predict_block(samples, pred_feats, target, cfg)
            for local_block_idx, locs in block_locs.items():
                raw = raw_block[int(local_block_idx)]
                j = TARGETS.index(target)
                pred_reg[val_idx[locs], j] = clip((1.0 - cfg.blend) * base_val[locs, j] + cfg.blend * raw)
            selected_rows.append({"fold": fold_id, "target": target, "config": cfg.name})
        print(f"[block-reg nested] fold={fold_id} configs={configs}", flush=True)

    rows = []
    for name, pred in [
        ("temporal_base", pred_base),
        ("nested_block_regressor", pred_reg),
        ("s_only_regressor_switch", target_switch(pred_base, pred_reg, ["S1", "S2", "S4"])),
        ("s_all_regressor_switch", target_switch(pred_base, pred_reg, ["S1", "S2", "S3", "S4"])),
    ]:
        row = {"model": name, "mean": mean_loss(y, pred)}
        row.update(per_target_loss(y, pred))
        rows.append(row)
    return pd.DataFrame(rows).sort_values("mean"), pd.DataFrame(selected_rows), pred_base, pred_reg


def target_switch(base: np.ndarray, reg: np.ndarray, targets: list[str]) -> np.ndarray:
    out = base.copy()
    for target in targets:
        j = TARGETS.index(target)
        out[:, j] = reg[:, j]
    return clip(out)


def full_submission(train: pd.DataFrame, sub: pd.DataFrame, switch_targets: list[str]) -> pd.DataFrame:
    sensor_cols = sensor_feature_cols(train)
    samples = make_training_blocks(train, sensor_cols)
    configs = select_configs(samples)
    pred_feats, block_locs, base_sub = block_features(train, sub, sensor_cols)
    reg_sub = base_sub.copy()
    for target in TARGETS:
        cfg = configs[target]
        raw_block = fit_predict_block(samples, pred_feats, target, cfg)
        for local_block_idx, locs in block_locs.items():
            j = TARGETS.index(target)
            raw = raw_block[int(local_block_idx)]
            reg_sub[locs, j] = clip((1.0 - cfg.blend) * base_sub[locs, j] + cfg.blend * raw)

    best_path = OUT / "submission_best.csv"
    if best_path.exists():
        out = pd.read_csv(best_path)
        pred = out[TARGETS].to_numpy(dtype=float)
    else:
        out = sub[["subject_id", "sleep_date", "lifelog_date"]].copy()
        pred = base_sub
    for target in switch_targets:
        pred[:, TARGETS.index(target)] = reg_sub[:, TARGETS.index(target)]
    for j, target in enumerate(TARGETS):
        out[target] = clip(pred[:, j])
    configs_out = pd.DataFrame({"target": list(configs), "config": [cfg.name for cfg in configs.values()]})
    configs_out.to_csv(OUT / "block_level_regressor_full_configs.csv", index=False)
    return out


def main() -> None:
    train = pd.read_parquet(OUT / "train_deep_features.parquet")
    sub = pd.read_parquet(OUT / "submission_deep_features.parquet")
    results, selected, _, _ = nested_oof(train)
    results.to_csv(OUT / "block_level_regressor_nested_results.csv", index=False)
    selected.to_csv(OUT / "block_level_regressor_nested_selected.csv", index=False)
    print(results.round(6).to_string(index=False))
    print(selected.to_string(index=False))
    best_model = str(results.iloc[0]["model"])
    switch = ["S1", "S2", "S4"] if best_model in {"s_only_regressor_switch", "temporal_base"} else ["S1", "S2", "S3", "S4"]
    out = full_submission(train, sub, switch)
    out.to_csv(OUT / "submission_block_level_regressor.csv", index=False)
    print("wrote", OUT / "submission_block_level_regressor.csv", "switch", switch)


if __name__ == "__main__":
    main()
