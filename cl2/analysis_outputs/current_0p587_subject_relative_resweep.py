from __future__ import annotations

from dataclasses import dataclass
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


@dataclass(frozen=True)
class RelConfig:
    mode: str
    param: float
    weight: float

    @property
    def name(self) -> str:
        return f"{self.mode}_p{self.param:g}_w{self.weight:g}"


def configs() -> list[RelConfig]:
    out: list[RelConfig] = []
    weights = [0.02, 0.03, 0.05, 0.08, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40]
    for weight in weights:
        for temp in [0.25, 0.35, 0.50, 0.65, 0.80, 0.90, 1.10, 1.25, 1.50, 1.75, 2.00, 2.50, 3.00]:
            out.append(RelConfig("center_temp", temp, weight))
        for scale in [0.35, 0.50, 0.65, 0.75, 0.90, 1.00, 1.25, 1.50, 2.00, 2.50, 3.00]:
            out.append(RelConfig("rank_logit", scale, weight))
        for gamma in [-0.75, -0.60, -0.50, -0.35, -0.25, -0.15, 0.15, 0.25, 0.35, 0.50, 0.75, 1.00, 1.50]:
            out.append(RelConfig("center_shift", gamma, weight))
    return out


def to_srq_config(cfg: RelConfig) -> srq.RelConfig:
    return srq.RelConfig(cfg.mode, cfg.param, cfg.weight)


def summarize(train: pd.DataFrame, current: np.ndarray) -> pd.DataFrame:
    y = train[TARGETS].to_numpy(dtype=int)
    rows = []
    cfgs = configs()
    for target in TARGETS:
        j = TARGETS.index(target)
        base = srq.loss_col(y[:, j], current[:, j])
        for cfg in cfgs:
            pred = srq.subject_relative(train, current[:, j], to_srq_config(cfg))
            blend_loss = srq.loss_col(y[:, j], pred)
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


def repeated_subject_half(train: pd.DataFrame, current: np.ndarray, selected: pd.DataFrame) -> pd.DataFrame:
    y = train[TARGETS].to_numpy(dtype=int)
    subjects = np.array(sorted(train["subject_id"].unique()))
    rng = np.random.default_rng(260937)
    rows = []
    for row in selected.itertuples(index=False):
        target = str(row.target)
        cfg = srq.parse_config(str(row.config))
        j = TARGETS.index(target)
        pred = srq.subject_relative(train, current[:, j], cfg)
        for rep in range(1000):
            select_subjects = set(rng.choice(subjects, size=len(subjects) // 2, replace=False))
            hold = ~train["subject_id"].isin(select_subjects).to_numpy()
            base_loss = srq.loss_col(y[hold, j], current[hold, j])
            blend_loss = srq.loss_col(y[hold, j], pred[hold])
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
    detail.to_csv(OUT / "current_0p587_subject_relative_resweep_subject_split_detail.csv", index=False)
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
        .sort_values(["target", "mean_delta"])
    )


def geometry_guardrail(train: pd.DataFrame, sub: pd.DataFrame, current: np.ndarray, selected: pd.DataFrame) -> pd.DataFrame:
    folds = geom.geometry_folds(train[KEY + ["sleep_date"] + TARGETS], sub[KEY + ["sleep_date"]], n_repeats=10)
    rows = []
    for row in selected.itertuples(index=False):
        target = str(row.target)
        cfg = srq.parse_config(str(row.config))
        j = TARGETS.index(target)
        ys, bases, blends = [], [], []
        for _, val_idx, fold_name in folds:
            val = train.iloc[val_idx].copy().reset_index(drop=True)
            pred = srq.subject_relative(val, current[val_idx, j], cfg)
            ys.append(train.iloc[val_idx][target].to_numpy(dtype=int))
            bases.append(current[val_idx, j])
            blends.append(pred)
            print(f"[0p587 rel resweep geometry] {target} {fold_name}", flush=True)
        y = np.concatenate(ys)
        base = np.concatenate(bases)
        blend = np.concatenate(blends)
        rows.append(
            {
                "target": target,
                "config": cfg.name,
                "base_loss": srq.loss_col(y, base),
                "blend_loss": srq.loss_col(y, blend),
                "delta_vs_base": srq.loss_col(y, blend) - srq.loss_col(y, base),
                "scored_occurrences": int(len(y)),
            }
        )
    return pd.DataFrame(rows).sort_values("delta_vs_base")


def main() -> None:
    train = blp.train_frame()
    sub = blp.sub_frame()
    current = np.load(BASE_OOF)
    result = summarize(train, current)
    result.to_csv(OUT / "current_0p587_subject_relative_resweep_results.csv", index=False)
    top = result.groupby("target").head(10)
    top.to_csv(OUT / "current_0p587_subject_relative_resweep_top.csv", index=False)
    selected = top[top["delta_vs_base"] < -0.00012].sort_values("delta_vs_base").groupby("target").head(1)
    selected.to_csv(OUT / "current_0p587_subject_relative_resweep_selected.csv", index=False)
    split = repeated_subject_half(train, current, selected) if not selected.empty else pd.DataFrame()
    split.to_csv(OUT / "current_0p587_subject_relative_resweep_subject_split.csv", index=False)
    geo = geometry_guardrail(train, sub, current, selected) if not selected.empty else pd.DataFrame()
    geo.to_csv(OUT / "current_0p587_subject_relative_resweep_geometry.csv", index=False)
    print(top.round(6).to_string(index=False))
    if not selected.empty:
        print("\nSelected")
        print(selected.round(6).to_string(index=False))
    if not split.empty:
        print("\nSubject split")
        print(split.round(6).to_string(index=False))
    if not geo.empty:
        print("\nGeometry")
        print(geo.round(6).to_string(index=False))


if __name__ == "__main__":
    main()
