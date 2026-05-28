from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss

sys.path.append(str(Path(__file__).resolve().parent))
import calibration_experiments as cal  # noqa: E402
import deep_dive_analysis as d  # noqa: E402
import overnight_feature_experiments as ofe  # noqa: E402
import overnight_legacy_repro as legacy  # noqa: E402
import meta_feature_experiments as mf  # noqa: E402
import q23_presleep_app_experiments as q23app  # noqa: E402
import q2_soft_app_stack_experiments as q2exp  # noqa: E402
import q3_soft_app_experiments as q3exp  # noqa: E402
import s2s4_pair_blend_nested_experiments as s2s4  # noqa: E402


OUT = Path(__file__).resolve().parent
TARGETS = d.TARGETS
KEY = d.KEY


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1 - 1e-5)


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([log_loss(y[:, j], clip(pred[:, j]), labels=[0, 1]) for j in range(len(TARGETS))]))


def per_target_loss(y: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    return {target: float(log_loss(y[:, j], clip(pred[:, j]), labels=[0, 1])) for j, target in enumerate(TARGETS)}


def legacy_strict_blend_oof(train: pd.DataFrame, group: str) -> tuple[np.ndarray, np.ndarray]:
    y = train[TARGETS].to_numpy()
    sensor_oof = np.zeros_like(y, dtype=float)
    blend_oof = np.zeros_like(y, dtype=float)
    for fold_id, (tr_idx, val_idx) in enumerate(d.make_folds(train, "subject_blocks")):
        outer_train = train.iloc[tr_idx].copy().reset_index(drop=True)
        outer_val = train.iloc[val_idx].copy().reset_index(drop=True)
        inner_folds = d.make_folds(outer_train, "subject_blocks")
        inner_base = cal.base_oof(outer_train, inner_folds)
        inner_sensor = np.zeros_like(inner_base)
        for itr, iva in inner_folds:
            inner_sensor[iva] = legacy.fit_predict_legacy(
                outer_train.iloc[itr].copy(),
                outer_train.iloc[iva].copy(),
                group,
            )
        weights, _ = ofe.optimize_blend(outer_train[TARGETS].to_numpy(), inner_base, inner_sensor)
        base_val = cal.temporal_base(outer_train, outer_val)
        sensor_val = legacy.fit_predict_legacy(outer_train, outer_val, group)
        sensor_oof[val_idx] = sensor_val
        blend_oof[val_idx] = clip((1.0 - weights) * base_val + weights * sensor_val)
        print(f"[final oof legacy] group={group} fold={fold_id}", flush=True)
    return clip(sensor_oof), clip(blend_oof)


def q2_combo_oof(train: pd.DataFrame, store: q23app.AppFeatureStore) -> np.ndarray:
    return q2exp.first_level_oof(train, store)["combo_q2"].to_numpy(dtype=float)


def q3_fixed_oof(train: pd.DataFrame, store: q23app.AppFeatureStore) -> np.ndarray:
    pred = np.zeros(len(train), dtype=float)
    combo = {"app": "logreg_c0.03", "wa": 0.10, "r": 0.50, "shrink": 1.0, "ws": 0.10}
    for tr_idx, val_idx in d.make_folds(train, "subject_blocks"):
        tr = train.iloc[tr_idx].copy().reset_index(drop=True)
        val = train.iloc[val_idx].copy().reset_index(drop=True)
        pred[val_idx] = q3exp.predict_combo(tr, val, store, combo)
    return clip(pred)


def s2s4_fixed_oof(train: pd.DataFrame) -> np.ndarray:
    pred = np.zeros((len(train), len(TARGETS)), dtype=float)
    for fold_id, (tr_idx, val_idx) in enumerate(d.make_folds(train, "subject_blocks")):
        tr = train.iloc[tr_idx].copy().reset_index(drop=True)
        val = train.iloc[val_idx].copy().reset_index(drop=True)
        sources = s2s4.source_predict(tr, val)
        pred[val_idx] = s2s4.apply_pairs(sources, s2s4.fixed_choices())
        print(f"[final oof s2s4] fold={fold_id}", flush=True)
    return clip(pred)


def final_oof() -> tuple[pd.DataFrame, np.ndarray]:
    train_legacy, sub_legacy = legacy.prepare_legacy()
    train_legacy = train_legacy.sort_values(KEY).reset_index(drop=True)
    sub_legacy = sub_legacy.sort_values(KEY).reset_index(drop=True)
    train_meta, sub_meta = mf.prepare(force_meta=False)
    train_meta = train_meta.sort_values(KEY).reset_index(drop=True)
    sub_meta = sub_meta.sort_values(KEY).reset_index(drop=True)
    if not train_meta[KEY].equals(train_legacy[KEY]) or not sub_meta[KEY].equals(sub_legacy[KEY]):
        raise ValueError("meta and legacy keys differ")
    train = train_meta
    sub = sub_meta
    all_keys = pd.concat([train_meta[KEY], sub_meta[KEY]], ignore_index=True)
    store = q23app.build_app_feature_store(all_keys)
    phone_sensor, phone_blend = legacy_strict_blend_oof(train_legacy, "overnight_phone")
    _, all_blend = legacy_strict_blend_oof(train_legacy, "overnight_all")
    pair = s2s4_fixed_oof(s2s4.ofe.prepare()[0].sort_values(KEY).reset_index(drop=True))

    pred = np.zeros((len(train), len(TARGETS)), dtype=float)
    pred[:, TARGETS.index("Q1")] = phone_sensor[:, TARGETS.index("Q1")]
    pred[:, TARGETS.index("Q2")] = q2_combo_oof(train, store)
    pred[:, TARGETS.index("Q3")] = q3_fixed_oof(train, store)
    pred[:, TARGETS.index("S1")] = phone_blend[:, TARGETS.index("S1")]
    pred[:, TARGETS.index("S2")] = pair[:, TARGETS.index("S2")]
    pred[:, TARGETS.index("S3")] = all_blend[:, TARGETS.index("S3")]
    pred[:, TARGETS.index("S4")] = pair[:, TARGETS.index("S4")]
    return train, clip(pred)


def block_average_oof(train: pd.DataFrame, pred: np.ndarray, strength: float) -> np.ndarray:
    out = pred.copy()
    sorted_train = train.sort_values(["subject_id", "lifelog_date"]).copy()
    for _, val_idx in d.make_folds(train, "subject_blocks"):
        val_set = set(int(x) for x in val_idx)
        val_rows = sorted_train[sorted_train.index.isin(val_set)].copy()
        val_rows["subject_pos"] = val_rows.groupby("subject_id").cumcount()
        for _, g in val_rows.groupby("subject_id", sort=False):
            idx = g.index.to_numpy(dtype=int)
            block_mean = pred[idx].mean(axis=0)
            out[idx] = (1.0 - strength) * pred[idx] + strength * block_mean
    return clip(out)


def submission_block_average(path_in: Path, path_out: Path, strength: float) -> pd.DataFrame:
    sub = pd.read_csv(path_in, parse_dates=["sleep_date", "lifelog_date"])
    out = sub.copy()
    all_keys = sub[["subject_id", "sleep_date", "lifelog_date"]].copy()
    all_keys["split"] = "submission"
    # Every contiguous submission segment in the file is one hidden block because
    # train rows are absent. Use date gaps to avoid merging separated blocks.
    for sid, g in sub.sort_values(["subject_id", "lifelog_date"]).groupby("subject_id", sort=False):
        g = g.copy()
        gap_break = g["lifelog_date"].diff().dt.days.fillna(1).ne(1).cumsum()
        for _, block in g.groupby(gap_break):
            idx = block.index.to_numpy(dtype=int)
            block_mean = sub.loc[idx, TARGETS].to_numpy(dtype=float).mean(axis=0)
            out.loc[idx, TARGETS] = (1.0 - strength) * sub.loc[idx, TARGETS].to_numpy(dtype=float) + strength * block_mean
    out[TARGETS] = out[TARGETS].clip(1e-5, 1 - 1e-5)
    out.to_csv(path_out, index=False)
    return out


def main() -> None:
    train, pred = final_oof()
    y = train[TARGETS].to_numpy(dtype=int)
    np.save(OUT / "final_hybrid_0p598_repro_oof.npy", pred)
    rows = []
    for strength in [0.0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.45, 0.60, 0.80, 1.0]:
        p = block_average_oof(train, pred, strength)
        row = {"strength": strength, "mean": mean_loss(y, p)}
        row.update(per_target_loss(y, p))
        rows.append(row)
    result = pd.DataFrame(rows).sort_values("mean")
    result.to_csv(OUT / "final_hybrid_block_average_oof_results.csv", index=False)
    best_strength = float(result.iloc[0]["strength"])
    submission_block_average(
        OUT / "submission_hybrid_0p598_repro.csv",
        OUT / "submission_hybrid_0p598_blockavg.csv",
        best_strength,
    )
    print(result.round(6).to_string(index=False))
    print("best_strength", best_strength)
    print("wrote", OUT / "submission_hybrid_0p598_blockavg.csv")


if __name__ == "__main__":
    main()
