from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

import current_0p588_subject_relative_q_postprocess as srq
import current_0p591_block_label_postprocess as blp
import deep_dive_analysis as d
import geometry_mask_cv_experiments as geom


OUT = Path(__file__).resolve().parent
TARGETS = d.TARGETS
KEY = d.KEY
BASE_OOF = OUT / "final_hybrid_0p587_subject_relative_qs_oof.npy"
TARGET = "Q2"


def candidate_configs() -> pd.DataFrame:
    results = pd.read_csv(OUT / "current_0p587_subject_relative_resweep_results.csv")
    q2 = results[(results["target"] == TARGET) & (results["delta_vs_base"] < -0.00015)].copy()
    # Keep a wider but still bounded set: the best OOF candidates plus gentler lower-weight variants.
    best = q2.sort_values("blend_loss").head(30)
    gentle = q2[q2["config"].str.contains("_w0.1|_w0.15|_w0.2|_w0.25", regex=True)].sort_values("blend_loss").head(20)
    return pd.concat([best, gentle], ignore_index=True).drop_duplicates(["target", "config"]).reset_index(drop=True)


def repeated_subject_half(train: pd.DataFrame, current: np.ndarray, selected: pd.DataFrame) -> pd.DataFrame:
    y = train[TARGETS].to_numpy(dtype=int)
    subjects = np.array(sorted(train["subject_id"].unique()))
    rng = np.random.default_rng(260939)
    rows = []
    j = TARGETS.index(TARGET)
    for row in selected.itertuples(index=False):
        cfg = srq.parse_config(str(row.config))
        pred = srq.subject_relative(train, current[:, j], cfg)
        for rep in range(2000):
            select_subjects = set(rng.choice(subjects, size=len(subjects) // 2, replace=False))
            hold = ~train["subject_id"].isin(select_subjects).to_numpy()
            base_loss = srq.loss_col(y[hold, j], current[hold, j])
            blend_loss = srq.loss_col(y[hold, j], pred[hold])
            rows.append(
                {
                    "target": TARGET,
                    "config": cfg.name,
                    "rep": rep,
                    "holdout_current": base_loss,
                    "holdout_blend": blend_loss,
                    "holdout_delta": blend_loss - base_loss,
                }
            )
    detail = pd.DataFrame(rows)
    detail.to_csv(OUT / "current_0p587_q2_relative_targeted_subject_detail.csv", index=False)
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
    j = TARGETS.index(TARGET)
    for row in selected.itertuples(index=False):
        cfg = srq.parse_config(str(row.config))
        ys, bases, blends = [], [], []
        for _, val_idx, _ in folds:
            val = train.iloc[val_idx].copy().reset_index(drop=True)
            pred = srq.subject_relative(val, current[val_idx, j], cfg)
            ys.append(train.iloc[val_idx][TARGET].to_numpy(dtype=int))
            bases.append(current[val_idx, j])
            blends.append(pred)
        y = np.concatenate(ys)
        base = np.concatenate(bases)
        blend = np.concatenate(blends)
        rows.append(
            {
                "target": TARGET,
                "config": cfg.name,
                "geometry_base_loss": srq.loss_col(y, base),
                "geometry_blend_loss": srq.loss_col(y, blend),
                "geometry_delta": srq.loss_col(y, blend) - srq.loss_col(y, base),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    train = blp.train_frame()
    sub = blp.sub_frame()
    current = np.load(BASE_OOF)
    selected = candidate_configs()
    selected.to_csv(OUT / "current_0p587_q2_relative_targeted_candidates.csv", index=False)
    split = repeated_subject_half(train, current, selected)
    split.to_csv(OUT / "current_0p587_q2_relative_targeted_subject.csv", index=False)
    geo = geometry_guardrail(train, sub, current, selected)
    geo.to_csv(OUT / "current_0p587_q2_relative_targeted_geometry.csv", index=False)
    merged = selected.merge(split, on=["target", "config"]).merge(geo, on=["target", "config"])
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
    merged = merged.sort_values(["passes_loose", "win_rate", "delta_vs_base"], ascending=[False, False, True])
    merged.to_csv(OUT / "current_0p587_q2_relative_targeted_merged.csv", index=False)
    print(
        merged[
            [
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
        .head(25)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
