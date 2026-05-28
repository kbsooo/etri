from __future__ import annotations

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
BASE_OOF = OUT / "final_hybrid_0p586_subject_relative_resweep_q2loose_oof.npy"
GRID = np.array([0.0, 0.01, 0.02, 0.03, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30])


def block_preds(train: pd.DataFrame) -> dict[str, np.ndarray]:
    preds = {}
    for i, cfg in enumerate(brs.configs()):
        cached = OUT / f"current_0p591_block_label_oof_{cfg.name}.npy"
        if cached.exists():
            preds[cfg.name] = np.load(cached)
        else:
            preds[cfg.name] = brs.oof(train, cfg)
        if i % 50 == 0:
            print(f"[0p586 block residual] {i}/{len(brs.configs())}", flush=True)
    return preds


def summarize(train: pd.DataFrame, current: np.ndarray, preds: dict[str, np.ndarray]) -> pd.DataFrame:
    y = train[TARGETS].to_numpy(dtype=int)
    rows = []
    for name, block in preds.items():
        for j, target in enumerate(TARGETS):
            base = blp.loss_col(y[:, j], current[:, j])
            block_loss = blp.loss_col(y[:, j], block[:, j])
            for w in GRID:
                p = (1.0 - w) * current[:, j] + w * block[:, j]
                blend_loss = blp.loss_col(y[:, j], p)
                rows.append(
                    {
                        "target": target,
                        "config": name,
                        "weight": float(w),
                        "base_loss": base,
                        "block_loss": block_loss,
                        "blend_loss": blend_loss,
                        "delta_vs_base": blend_loss - base,
                    }
                )
    return pd.DataFrame(rows).sort_values(["target", "blend_loss"])


def repeated_subject_half(train: pd.DataFrame, current: np.ndarray, preds: dict[str, np.ndarray], selected: pd.DataFrame) -> pd.DataFrame:
    y = train[TARGETS].to_numpy(dtype=int)
    subjects = np.array(sorted(train["subject_id"].unique()))
    rng = np.random.default_rng(260940)
    rows = []
    for row in selected.itertuples(index=False):
        target = str(row.target)
        config = str(row.config)
        weight = float(row.weight)
        j = TARGETS.index(target)
        block = preds[config][:, j]
        p = (1.0 - weight) * current[:, j] + weight * block
        for rep in range(1000):
            select_subjects = set(rng.choice(subjects, size=len(subjects) // 2, replace=False))
            hold = ~train["subject_id"].isin(select_subjects).to_numpy()
            base_loss = blp.loss_col(y[hold, j], current[hold, j])
            blend_loss = blp.loss_col(y[hold, j], p[hold])
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
    detail.to_csv(OUT / "current_0p586_block_label_residual_subject_detail.csv", index=False)
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
                "scored_occurrences": int(len(y)),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    train = blp.train_frame()
    sub = blp.sub_frame()
    current = np.load(BASE_OOF)
    preds = block_preds(train)
    result = summarize(train, current, preds)
    result.to_csv(OUT / "current_0p586_block_label_residual_results.csv", index=False)
    top = result.groupby("target").head(8)
    top.to_csv(OUT / "current_0p586_block_label_residual_top.csv", index=False)
    selected = top[top["delta_vs_base"] < -0.0002].sort_values("delta_vs_base").groupby("target").head(1).reset_index(drop=True)
    selected.to_csv(OUT / "current_0p586_block_label_residual_selected.csv", index=False)
    split = repeated_subject_half(train, current, preds, selected) if not selected.empty else pd.DataFrame()
    split.to_csv(OUT / "current_0p586_block_label_residual_subject.csv", index=False)
    geo = geometry_guardrail(train, sub, current, selected) if not selected.empty else pd.DataFrame()
    geo.to_csv(OUT / "current_0p586_block_label_residual_geometry.csv", index=False)
    merged = selected.merge(split, on=["target", "config", "weight"], how="left").merge(geo, on=["target", "config", "weight"], how="left")
    merged["passes_loose"] = (
        (merged["delta_vs_base"] < 0)
        & (merged["mean_delta"] < 0)
        & (merged["win_rate"] >= 0.60)
        & (merged["geometry_delta"] < 0)
    )
    merged["passes_strict"] = (
        (merged["delta_vs_base"] < -0.0003)
        & (merged["mean_delta"] < -0.0003)
        & (merged["win_rate"] >= 0.65)
        & (merged["geometry_delta"] < -0.0003)
    )
    merged.to_csv(OUT / "current_0p586_block_label_residual_merged.csv", index=False)
    print(top.round(6).to_string(index=False))
    if not merged.empty:
        print("\nMerged")
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
