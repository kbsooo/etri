from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))
import block_rate_smoother_experiments as brs  # noqa: E402
import deep_dive_analysis as d  # noqa: E402
import geometry_mask_cv_experiments as geom  # noqa: E402


OUT = Path(__file__).resolve().parent
DATA = OUT.parents[0] / "data"
TARGETS = d.TARGETS
KEY = d.KEY
BASE_OOF = OUT / "final_hybrid_0p591_sleep_dynamics_s1_s4_oof.npy"
BASE_SUB = OUT / "submission_hybrid_0p591_sleep_dynamics_s1_s4.csv"


@dataclass(frozen=True)
class Candidate:
    target: str
    config: str
    weight: float


GRID = np.array([0.0, 0.02, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30, 0.45, 0.60])


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1 - 1e-5)


def cfg_by_name() -> dict[str, brs.BlockConfig]:
    return {cfg.name: cfg for cfg in brs.configs()}


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    return brs.log_loss(y.astype(int), clip(p), labels=[0, 1])


def train_frame() -> pd.DataFrame:
    return pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)


def sub_frame() -> pd.DataFrame:
    return pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)


def oof_block_preds(train: pd.DataFrame) -> dict[str, np.ndarray]:
    preds = {}
    for i, cfg in enumerate(brs.configs()):
        preds[cfg.name] = brs.oof(train, cfg)
        if i % 50 == 0:
            print(f"[current block] {i}/{len(brs.configs())}", flush=True)
    return preds


def summarize(train: pd.DataFrame, current: np.ndarray, preds: dict[str, np.ndarray]) -> pd.DataFrame:
    y = train[TARGETS].to_numpy(dtype=int)
    rows = []
    for name, block in preds.items():
        for j, target in enumerate(TARGETS):
            base = loss_col(y[:, j], current[:, j])
            block_loss = loss_col(y[:, j], block[:, j])
            for w in GRID:
                p = (1.0 - w) * current[:, j] + w * block[:, j]
                rows.append(
                    {
                        "target": target,
                        "config": name,
                        "weight": float(w),
                        "base_loss": base,
                        "block_loss": block_loss,
                        "blend_loss": loss_col(y[:, j], p),
                        "delta_vs_base": loss_col(y[:, j], p) - base,
                    }
                )
    out = pd.DataFrame(rows).sort_values(["target", "blend_loss"])
    return out


def repeated_subject_half(train: pd.DataFrame, current: np.ndarray, preds: dict[str, np.ndarray], selected: list[Candidate]) -> pd.DataFrame:
    y = train[TARGETS].to_numpy(dtype=int)
    subjects = np.array(sorted(train["subject_id"].unique()))
    rng = np.random.default_rng(260934)
    rows = []
    for cand in selected:
        j = TARGETS.index(cand.target)
        block = preds[cand.config][:, j]
        p = (1.0 - cand.weight) * current[:, j] + cand.weight * block
        for rep in range(1000):
            select_subjects = set(rng.choice(subjects, size=len(subjects) // 2, replace=False))
            hold = ~train["subject_id"].isin(select_subjects).to_numpy()
            rows.append(
                {
                    "target": cand.target,
                    "config": cand.config,
                    "weight": cand.weight,
                    "rep": rep,
                    "holdout_current": loss_col(y[hold, j], current[hold, j]),
                    "holdout_blend": loss_col(y[hold, j], p[hold]),
                    "holdout_delta": loss_col(y[hold, j], p[hold]) - loss_col(y[hold, j], current[hold, j]),
                }
            )
    detail = pd.DataFrame(rows)
    detail.to_csv(OUT / "current_0p591_block_label_subject_split_detail.csv", index=False)
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
        .sort_values(["target", "mean_delta"])
    )


def geometry_guardrail(train: pd.DataFrame, sub: pd.DataFrame, current: np.ndarray, selected: list[Candidate]) -> pd.DataFrame:
    cfg_map = cfg_by_name()
    folds = geom.geometry_folds(train[KEY + ["sleep_date"] + TARGETS], sub[KEY + ["sleep_date"]], n_repeats=10)
    rows = []
    for cand in selected:
        cfg = cfg_map[cand.config]
        j = TARGETS.index(cand.target)
        ys, bases, blends = [], [], []
        for tr_idx, val_idx, fold_name in folds:
            ref = train.iloc[tr_idx].copy().reset_index(drop=True)
            val = train.iloc[val_idx].copy().reset_index(drop=True)
            block = brs.block_smoother(ref, val, cfg)[:, j]
            blend = (1.0 - cand.weight) * current[val_idx, j] + cand.weight * block
            ys.append(train.iloc[val_idx][cand.target].to_numpy(dtype=int))
            bases.append(current[val_idx, j])
            blends.append(blend)
            print(f"[current block geometry] {cand.target} {fold_name}", flush=True)
        y = np.concatenate(ys)
        base = np.concatenate(bases)
        blend = np.concatenate(blends)
        rows.append(
            {
                "target": cand.target,
                "config": cand.config,
                "weight": cand.weight,
                "base_loss": loss_col(y, base),
                "blend_loss": loss_col(y, blend),
                "delta_vs_base": loss_col(y, blend) - loss_col(y, base),
                "scored_occurrences": int(len(y)),
            }
        )
    return pd.DataFrame(rows).sort_values("delta_vs_base")


def main() -> None:
    train = train_frame()
    sub = sub_frame()
    current = np.load(BASE_OOF)
    preds = oof_block_preds(train)
    for name, pred in preds.items():
        np.save(OUT / f"current_0p591_block_label_oof_{name}.npy", pred)
    result = summarize(train, current, preds)
    result.to_csv(OUT / "current_0p591_block_label_results.csv", index=False)
    top = result.groupby("target").head(8)
    top.to_csv(OUT / "current_0p591_block_label_top.csv", index=False)
    selected = [
        Candidate(str(r.target), str(r.config), float(r.weight))
        for r in top[top["delta_vs_base"] < -0.0005].sort_values("delta_vs_base").groupby("target").head(1).itertuples(index=False)
    ]
    split = repeated_subject_half(train, current, preds, selected) if selected else pd.DataFrame()
    split.to_csv(OUT / "current_0p591_block_label_subject_split.csv", index=False)
    geo = geometry_guardrail(train, sub, current, selected) if selected else pd.DataFrame()
    geo.to_csv(OUT / "current_0p591_block_label_geometry.csv", index=False)
    print(top.round(6).to_string(index=False))
    if not split.empty:
        print("\nSubject split")
        print(split.round(6).to_string(index=False))
    if not geo.empty:
        print("\nGeometry")
        print(geo.round(6).to_string(index=False))


if __name__ == "__main__":
    main()
