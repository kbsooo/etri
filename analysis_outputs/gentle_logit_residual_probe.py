from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

import current_0p586_gentle_logit_calibration as glc
import current_0p591_block_label_postprocess as blp
import deep_dive_analysis as d
import geometry_mask_cv_experiments as geom


OUT = Path(__file__).resolve().parent
TARGETS = d.TARGETS
KEY = d.KEY


def summarize(train: pd.DataFrame, current: np.ndarray) -> pd.DataFrame:
    y = train[TARGETS].to_numpy(dtype=int)
    rows = []
    for target in TARGETS:
        j = TARGETS.index(target)
        base = glc.srq.loss_col(y[:, j], current[:, j])
        for cfg in glc.configs():
            pred = glc.calibrate(current[:, j], cfg)
            blend_loss = glc.srq.loss_col(y[:, j], pred)
            rows.append(
                {
                    "target": target,
                    "config": cfg.name,
                    "base_loss": base,
                    "blend_loss": blend_loss,
                    "delta_vs_base": blend_loss - base,
                }
            )
    return pd.DataFrame(rows).sort_values(["target", "blend_loss"])


def repeated_subject_half(train: pd.DataFrame, current: np.ndarray, selected: pd.DataFrame, seed: int, prefix: str) -> pd.DataFrame:
    y = train[TARGETS].to_numpy(dtype=int)
    subjects = np.array(sorted(train["subject_id"].unique()))
    rng = np.random.default_rng(seed)
    rows = []
    for row in selected.itertuples(index=False):
        target = str(row.target)
        cfg = glc.parse_config(str(row.config))
        j = TARGETS.index(target)
        pred = glc.calibrate(current[:, j], cfg)
        for rep in range(1000):
            select_subjects = set(rng.choice(subjects, size=len(subjects) // 2, replace=False))
            hold = ~train["subject_id"].isin(select_subjects).to_numpy()
            base_loss = glc.srq.loss_col(y[hold, j], current[hold, j])
            blend_loss = glc.srq.loss_col(y[hold, j], pred[hold])
            rows.append(
                {
                    "target": target,
                    "config": cfg.name,
                    "rep": rep,
                    "holdout_current": base_loss,
                    "holdout_blend": blend_loss,
                    "holdout_delta": blend_loss - base_loss,
                }
            )
    detail = pd.DataFrame(rows)
    detail.to_csv(OUT / f"{prefix}_subject_detail.csv", index=False)
    return (
        detail.groupby(["target", "config"])
        .agg(
            mean_delta=("holdout_delta", "mean"),
            median_delta=("holdout_delta", "median"),
            p25_delta=("holdout_delta", lambda x: float(np.quantile(x, 0.25))),
            p75_delta=("holdout_delta", lambda x: float(np.quantile(x, 0.75))),
            win_rate=("holdout_delta", lambda x: float((x < 0).mean())),
        )
        .reset_index()
    )


def geometry_guardrail(train: pd.DataFrame, sub: pd.DataFrame, current: np.ndarray, selected: pd.DataFrame) -> pd.DataFrame:
    folds = geom.geometry_folds(train[KEY + ["sleep_date"] + TARGETS], sub[KEY + ["sleep_date"]], n_repeats=10)
    rows = []
    for row in selected.itertuples(index=False):
        target = str(row.target)
        cfg = glc.parse_config(str(row.config))
        j = TARGETS.index(target)
        ys, bases, blends = [], [], []
        for _, val_idx, _ in folds:
            pred = glc.calibrate(current[val_idx, j], cfg)
            ys.append(train.iloc[val_idx][target].to_numpy(dtype=int))
            bases.append(current[val_idx, j])
            blends.append(pred)
        y = np.concatenate(ys)
        base = np.concatenate(bases)
        blend = np.concatenate(blends)
        rows.append(
            {
                "target": target,
                "config": cfg.name,
                "geometry_base_loss": glc.srq.loss_col(y, base),
                "geometry_blend_loss": glc.srq.loss_col(y, blend),
                "geometry_delta": glc.srq.loss_col(y, blend) - glc.srq.loss_col(y, base),
            }
        )
    return pd.DataFrame(rows)


def run(base_oof: Path, prefix: str, seed: int) -> pd.DataFrame:
    train = blp.train_frame()
    sub = blp.sub_frame()
    current = np.load(base_oof)
    result = summarize(train, current)
    result.to_csv(OUT / f"{prefix}_results.csv", index=False)
    top = result.groupby("target").head(8)
    top.to_csv(OUT / f"{prefix}_top.csv", index=False)
    selected = top[top["delta_vs_base"] < -0.00008].sort_values("delta_vs_base").groupby("target").head(1).reset_index(drop=True)
    selected.to_csv(OUT / f"{prefix}_selected.csv", index=False)
    split = repeated_subject_half(train, current, selected, seed, prefix) if not selected.empty else pd.DataFrame()
    split.to_csv(OUT / f"{prefix}_subject.csv", index=False)
    geo = geometry_guardrail(train, sub, current, selected) if not selected.empty else pd.DataFrame()
    geo.to_csv(OUT / f"{prefix}_geometry.csv", index=False)
    merged = selected.merge(split, on=["target", "config"], how="left").merge(geo, on=["target", "config"], how="left")
    if not merged.empty:
        merged["passes_loose"] = (
            (merged["delta_vs_base"] < 0)
            & (merged["mean_delta"] < 0)
            & (merged["win_rate"] >= 0.60)
            & (merged["geometry_delta"] < 0)
        )
        merged["passes_strict"] = (
            (merged["delta_vs_base"] < -0.0002)
            & (merged["mean_delta"] < -0.0002)
            & (merged["win_rate"] >= 0.65)
            & (merged["geometry_delta"] < -0.0002)
        )
    merged.to_csv(OUT / f"{prefix}_merged.csv", index=False)
    return merged


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-oof", required=True)
    parser.add_argument("--prefix", required=True)
    parser.add_argument("--seed", type=int, default=260943)
    args = parser.parse_args()
    merged = run(Path(args.base_oof), args.prefix, args.seed)
    if merged.empty:
        print("no selected configs")
        return
    print(
        merged[
            [
                "target",
                "config",
                "delta_vs_base",
                "mean_delta",
                "win_rate",
                "geometry_delta",
                "passes_loose",
                "passes_strict",
            ]
        ]
        .round(6)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
