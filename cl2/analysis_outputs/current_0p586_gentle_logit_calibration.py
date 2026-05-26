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
BASE_OOF = OUT / "final_hybrid_0p586_subject_relative_resweep_q2loose_oof.npy"


@dataclass(frozen=True)
class CalConfig:
    scale: float
    shift: float
    weight: float

    @property
    def name(self) -> str:
        return f"scale{self.scale:g}_shift{self.shift:g}_w{self.weight:g}"


def configs() -> list[CalConfig]:
    out = []
    for weight in [0.03, 0.05, 0.08, 0.10, 0.15, 0.20]:
        for scale in [0.75, 0.85, 0.92, 1.08, 1.15, 1.30]:
            out.append(CalConfig(scale, 0.0, weight))
        for shift in [-0.12, -0.08, -0.04, 0.04, 0.08, 0.12]:
            out.append(CalConfig(1.0, shift, weight))
        for scale in [0.85, 1.15]:
            for shift in [-0.08, -0.04, 0.04, 0.08]:
                out.append(CalConfig(scale, shift, weight))
    return out


def calibrate(p: np.ndarray, cfg: CalConfig) -> np.ndarray:
    raw = srq.sigmoid(cfg.scale * srq.logit(p) + cfg.shift)
    return srq.clip((1.0 - cfg.weight) * p + cfg.weight * raw)


def parse_config(name: str) -> CalConfig:
    scale_s, rest = name.removeprefix("scale").split("_shift")
    shift_s, weight_s = rest.split("_w")
    return CalConfig(float(scale_s), float(shift_s), float(weight_s))


def summarize(train: pd.DataFrame, current: np.ndarray) -> pd.DataFrame:
    y = train[TARGETS].to_numpy(dtype=int)
    rows = []
    for target in TARGETS:
        j = TARGETS.index(target)
        base = srq.loss_col(y[:, j], current[:, j])
        for cfg in configs():
            pred = calibrate(current[:, j], cfg)
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
    rng = np.random.default_rng(260941)
    rows = []
    for row in selected.itertuples(index=False):
        target = str(row.target)
        cfg = parse_config(str(row.config))
        j = TARGETS.index(target)
        pred = calibrate(current[:, j], cfg)
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
    detail.to_csv(OUT / "current_0p586_gentle_logit_calibration_subject_detail.csv", index=False)
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
        cfg = parse_config(str(row.config))
        j = TARGETS.index(target)
        ys, bases, blends = [], [], []
        for _, val_idx, _ in folds:
            pred = calibrate(current[val_idx, j], cfg)
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
    result = summarize(train, current)
    result.to_csv(OUT / "current_0p586_gentle_logit_calibration_results.csv", index=False)
    top = result.groupby("target").head(8)
    top.to_csv(OUT / "current_0p586_gentle_logit_calibration_top.csv", index=False)
    selected = top[top["delta_vs_base"] < -0.00008].sort_values("delta_vs_base").groupby("target").head(1).reset_index(drop=True)
    selected.to_csv(OUT / "current_0p586_gentle_logit_calibration_selected.csv", index=False)
    split = repeated_subject_half(train, current, selected) if not selected.empty else pd.DataFrame()
    split.to_csv(OUT / "current_0p586_gentle_logit_calibration_subject.csv", index=False)
    geo = geometry_guardrail(train, sub, current, selected) if not selected.empty else pd.DataFrame()
    geo.to_csv(OUT / "current_0p586_gentle_logit_calibration_geometry.csv", index=False)
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
    merged.to_csv(OUT / "current_0p586_gentle_logit_calibration_merged.csv", index=False)
    print(top.round(6).to_string(index=False))
    if not merged.empty:
        print("\nMerged")
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
