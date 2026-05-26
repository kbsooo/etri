from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))
import current_0p591_block_label_postprocess as blp  # noqa: E402
import deep_dive_analysis as d  # noqa: E402
import geometry_mask_cv_experiments as geom  # noqa: E402


OUT = Path(__file__).resolve().parent
DATA = OUT.parents[0] / "data"
TARGETS = d.TARGETS
Q_TARGETS = ["Q1", "Q2", "Q3"]
KEY = d.KEY
BASE_OOF = OUT / "final_hybrid_0p588_block_label_oof.npy"


@dataclass(frozen=True)
class RelConfig:
    mode: str
    param: float
    weight: float

    @property
    def name(self) -> str:
        return f"{self.mode}_p{self.param:g}_w{self.weight:g}"


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1 - 1e-5)


def logit(p: np.ndarray) -> np.ndarray:
    p = clip(p)
    return np.log(p / (1.0 - p))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    return blp.loss_col(y, p)


def configs() -> list[RelConfig]:
    out = []
    for weight in [0.05, 0.08, 0.10, 0.15, 0.20, 0.30]:
        for temp in [0.50, 0.70, 0.85, 1.20, 1.50, 2.00]:
            out.append(RelConfig("center_temp", temp, weight))
        for scale in [0.75, 1.00, 1.50, 2.00, 3.00]:
            out.append(RelConfig("rank_logit", scale, weight))
        for gamma in [-0.50, -0.25, 0.25, 0.50, 0.75, 1.00]:
            out.append(RelConfig("center_shift", gamma, weight))
    return out


def subject_relative(rows: pd.DataFrame, p: np.ndarray, cfg: RelConfig) -> np.ndarray:
    out = p.copy()
    tmp = rows[KEY].reset_index(drop=True).copy()
    z = logit(p)
    tmp["_p"] = p
    tmp["_z"] = z
    for _, g in tmp.groupby("subject_id", sort=False):
        idx = g.index.to_numpy(dtype=int)
        zi = z[idx]
        pi = p[idx]
        if len(idx) <= 1:
            continue
        center = float(np.mean(zi))
        if cfg.mode == "center_temp":
            raw = sigmoid(center + cfg.param * (zi - center))
        elif cfg.mode == "center_shift":
            raw = sigmoid(zi + cfg.param * (zi - center))
        elif cfg.mode == "rank_logit":
            ranks = pd.Series(pi).rank(pct=True).to_numpy(dtype=float)
            raw = sigmoid(center + cfg.param * (ranks - 0.5))
        else:
            raise ValueError(cfg.mode)
        out[idx] = (1.0 - cfg.weight) * pi + cfg.weight * raw
    return clip(out)


def summarize(train: pd.DataFrame, current: np.ndarray) -> pd.DataFrame:
    y = train[TARGETS].to_numpy(dtype=int)
    rows = []
    for target in Q_TARGETS:
        j = TARGETS.index(target)
        base = loss_col(y[:, j], current[:, j])
        for cfg in configs():
            pred = subject_relative(train, current[:, j], cfg)
            rows.append(
                {
                    "target": target,
                    "config": cfg.name,
                    "base_loss": base,
                    "blend_loss": loss_col(y[:, j], pred),
                    "delta_vs_base": loss_col(y[:, j], pred) - base,
                }
            )
    return pd.DataFrame(rows).sort_values(["target", "blend_loss"])


def repeated_subject_half(train: pd.DataFrame, current: np.ndarray, selected: pd.DataFrame) -> pd.DataFrame:
    y = train[TARGETS].to_numpy(dtype=int)
    subjects = np.array(sorted(train["subject_id"].unique()))
    rng = np.random.default_rng(260935)
    rows = []
    for row in selected.itertuples(index=False):
        target = str(row.target)
        cfg = parse_config(str(row.config))
        j = TARGETS.index(target)
        pred = subject_relative(train, current[:, j], cfg)
        for rep in range(1000):
            select_subjects = set(rng.choice(subjects, size=len(subjects) // 2, replace=False))
            hold = ~train["subject_id"].isin(select_subjects).to_numpy()
            rows.append(
                {
                    "target": target,
                    "config": cfg.name,
                    "rep": rep,
                    "holdout_current": loss_col(y[hold, j], current[hold, j]),
                    "holdout_blend": loss_col(y[hold, j], pred[hold]),
                    "holdout_delta": loss_col(y[hold, j], pred[hold]) - loss_col(y[hold, j], current[hold, j]),
                }
            )
    detail = pd.DataFrame(rows)
    detail.to_csv(OUT / "current_0p588_subject_relative_q_subject_split_detail.csv", index=False)
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


def parse_config(name: str) -> RelConfig:
    mode, rest = name.rsplit("_p", 1)
    param_s, weight_s = rest.split("_w")
    return RelConfig(mode, float(param_s), float(weight_s))


def geometry_guardrail(train: pd.DataFrame, sub: pd.DataFrame, current: np.ndarray, selected: pd.DataFrame) -> pd.DataFrame:
    folds = geom.geometry_folds(train[KEY + ["sleep_date"] + TARGETS], sub[KEY + ["sleep_date"]], n_repeats=10)
    rows = []
    for row in selected.itertuples(index=False):
        target = str(row.target)
        cfg = parse_config(str(row.config))
        j = TARGETS.index(target)
        ys, bases, blends = [], [], []
        for _, val_idx, fold_name in folds:
            val = train.iloc[val_idx].copy().reset_index(drop=True)
            pred = subject_relative(val, current[val_idx, j], cfg)
            ys.append(train.iloc[val_idx][target].to_numpy(dtype=int))
            bases.append(current[val_idx, j])
            blends.append(pred)
            print(f"[subject relative geometry] {target} {fold_name}", flush=True)
        y = np.concatenate(ys)
        base = np.concatenate(bases)
        blend = np.concatenate(blends)
        rows.append(
            {
                "target": target,
                "config": cfg.name,
                "base_loss": loss_col(y, base),
                "blend_loss": loss_col(y, blend),
                "delta_vs_base": loss_col(y, blend) - loss_col(y, base),
                "scored_occurrences": int(len(y)),
            }
        )
    return pd.DataFrame(rows).sort_values("delta_vs_base")


def main() -> None:
    train = blp.train_frame()
    sub = blp.sub_frame()
    current = np.load(BASE_OOF)
    result = summarize(train, current)
    result.to_csv(OUT / "current_0p588_subject_relative_q_results.csv", index=False)
    top = result.groupby("target").head(8)
    top.to_csv(OUT / "current_0p588_subject_relative_q_top.csv", index=False)
    selected = top[top["delta_vs_base"] < -0.0003].sort_values("delta_vs_base").groupby("target").head(1)
    split = repeated_subject_half(train, current, selected) if not selected.empty else pd.DataFrame()
    split.to_csv(OUT / "current_0p588_subject_relative_q_subject_split.csv", index=False)
    geo = geometry_guardrail(train, sub, current, selected) if not selected.empty else pd.DataFrame()
    geo.to_csv(OUT / "current_0p588_subject_relative_q_geometry.csv", index=False)
    print(top.round(6).to_string(index=False))
    if not split.empty:
        print("\nSubject split")
        print(split.round(6).to_string(index=False))
    if not geo.empty:
        print("\nGeometry")
        print(geo.round(6).to_string(index=False))


if __name__ == "__main__":
    main()
