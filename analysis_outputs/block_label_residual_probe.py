from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

import block_rate_smoother_experiments as brs
import current_0p591_block_label_postprocess as blp
import deep_dive_analysis as d
import geometry_mask_cv_experiments as geom


OUT = Path(__file__).resolve().parent
TARGETS = d.TARGETS
KEY = d.KEY
GRID = np.array([0.0, 0.01, 0.02, 0.03, 0.05, 0.08, 0.10, 0.15, 0.20])


def block_preds(train: pd.DataFrame) -> dict[str, np.ndarray]:
    preds = {}
    for i, cfg in enumerate(brs.configs()):
        cached = OUT / f"current_0p591_block_label_oof_{cfg.name}.npy"
        preds[cfg.name] = np.load(cached) if cached.exists() else brs.oof(train, cfg)
        if i % 50 == 0:
            print(f"[block residual probe] {i}/{len(brs.configs())}", flush=True)
    return preds


def summarize(train: pd.DataFrame, current: np.ndarray, preds: dict[str, np.ndarray]) -> pd.DataFrame:
    y = train[TARGETS].to_numpy(dtype=int)
    rows = []
    for name, block in preds.items():
        for j, target in enumerate(TARGETS):
            base = blp.loss_col(y[:, j], current[:, j])
            block_loss = blp.loss_col(y[:, j], block[:, j])
            for weight in GRID:
                pred = (1.0 - weight) * current[:, j] + weight * block[:, j]
                blend_loss = blp.loss_col(y[:, j], pred)
                rows.append(
                    {
                        "target": target,
                        "config": name,
                        "weight": float(weight),
                        "base_loss": base,
                        "block_loss": block_loss,
                        "blend_loss": blend_loss,
                        "delta_vs_base": blend_loss - base,
                    }
                )
    return pd.DataFrame(rows).sort_values(["target", "blend_loss"])


def repeated_subject_half(train: pd.DataFrame, current: np.ndarray, preds: dict[str, np.ndarray], selected: pd.DataFrame, seed: int, prefix: str) -> pd.DataFrame:
    y = train[TARGETS].to_numpy(dtype=int)
    subjects = np.array(sorted(train["subject_id"].unique()))
    rng = np.random.default_rng(seed)
    rows = []
    for row in selected.itertuples(index=False):
        target = str(row.target)
        config = str(row.config)
        weight = float(row.weight)
        j = TARGETS.index(target)
        block = preds[config][:, j]
        pred = (1.0 - weight) * current[:, j] + weight * block
        for rep in range(1000):
            select_subjects = set(rng.choice(subjects, size=len(subjects) // 2, replace=False))
            hold = ~train["subject_id"].isin(select_subjects).to_numpy()
            base_loss = blp.loss_col(y[hold, j], current[hold, j])
            blend_loss = blp.loss_col(y[hold, j], pred[hold])
            rows.append(
                {
                    "target": target,
                    "config": config,
                    "weight": weight,
                    "rep": rep,
                    "holdout_current": base_loss,
                    "holdout_blend": blend_loss,
                    "holdout_delta": blend_loss - base_loss,
                }
            )
    detail = pd.DataFrame(rows)
    detail.to_csv(OUT / f"{prefix}_subject_detail.csv", index=False)
    return (
        detail.groupby(["target", "config", "weight"])
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
    cfg_map = {cfg.name: cfg for cfg in brs.configs()}
    folds = geom.geometry_folds(train[KEY + ["sleep_date"] + TARGETS], sub[KEY + ["sleep_date"]], n_repeats=10)
    rows = []
    for row in selected.itertuples(index=False):
        target = str(row.target)
        config = str(row.config)
        weight = float(row.weight)
        cfg = cfg_map[config]
        j = TARGETS.index(target)
        ys, bases, blends = [], [], []
        for tr_idx, val_idx, _ in folds:
            ref = train.iloc[tr_idx].copy().reset_index(drop=True)
            val = train.iloc[val_idx].copy().reset_index(drop=True)
            block = brs.block_smoother(ref, val, cfg)[:, j]
            blend = (1.0 - weight) * current[val_idx, j] + weight * block
            ys.append(train.iloc[val_idx][target].to_numpy(dtype=int))
            bases.append(current[val_idx, j])
            blends.append(blend)
        y = np.concatenate(ys)
        base = np.concatenate(bases)
        blend = np.concatenate(blends)
        rows.append(
            {
                "target": target,
                "config": config,
                "weight": weight,
                "geometry_base_loss": blp.loss_col(y, base),
                "geometry_blend_loss": blp.loss_col(y, blend),
                "geometry_delta": blp.loss_col(y, blend) - blp.loss_col(y, base),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-oof", required=True)
    parser.add_argument("--prefix", required=True)
    parser.add_argument("--seed", type=int, default=260952)
    args = parser.parse_args()
    train = blp.train_frame()
    sub = blp.sub_frame()
    current = np.load(args.base_oof)
    preds = block_preds(train)
    result = summarize(train, current, preds)
    result.to_csv(OUT / f"{args.prefix}_results.csv", index=False)
    top = result.groupby("target").head(8)
    top.to_csv(OUT / f"{args.prefix}_top.csv", index=False)
    selected = top[top["delta_vs_base"] < -0.00008].sort_values("delta_vs_base").groupby("target").head(1).reset_index(drop=True)
    selected.to_csv(OUT / f"{args.prefix}_selected.csv", index=False)
    split = repeated_subject_half(train, current, preds, selected, args.seed, args.prefix) if not selected.empty else pd.DataFrame()
    split.to_csv(OUT / f"{args.prefix}_subject.csv", index=False)
    geo = geometry_guardrail(train, sub, current, selected) if not selected.empty else pd.DataFrame()
    geo.to_csv(OUT / f"{args.prefix}_geometry.csv", index=False)
    merged = selected.merge(split, on=["target", "config", "weight"], how="left").merge(geo, on=["target", "config", "weight"], how="left")
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
    merged.to_csv(OUT / f"{args.prefix}_merged.csv", index=False)
    if merged.empty:
        print("no selected configs")
    else:
        print(
            merged[
                [
                    "target",
                    "config",
                    "weight",
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
