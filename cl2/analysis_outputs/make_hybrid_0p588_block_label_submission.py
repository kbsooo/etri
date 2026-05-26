from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))
import block_rate_smoother_experiments as brs  # noqa: E402
import current_0p591_block_label_postprocess as blp  # noqa: E402
import deep_dive_analysis as d  # noqa: E402


OUT = Path(__file__).resolve().parent
DATA = OUT.parents[0] / "data"
KEY = d.KEY
TARGETS = d.TARGETS
BASE_SUB = OUT / "submission_hybrid_0p591_sleep_dynamics_s1_s4.csv"
BASE_OOF = OUT / "final_hybrid_0p591_sleep_dynamics_s1_s4_oof.npy"
SUB_OUT = OUT / "submission_hybrid_0p588_block_label.csv"
EST_OUT = OUT / "hybrid_0p588_block_label_cv_estimate.csv"
OOF_OUT = OUT / "final_hybrid_0p588_block_label_oof.npy"

SELECTED = {
    "Q1": ("s4_a0.9_w1_gap_boost0", 0.05),
    "Q2": ("s32_a0.9_w1_gap_boost0", 0.10),
    "Q3": ("s32_a0.9_w3_eq_boost0", 0.15),
    "S3": ("s4_a0.15_w5_gap_boost0", 0.60),
    "S4": ("s32_a0.9_w10_gap_boost0", 0.45),
}


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1 - 1e-5)


def load_oof_block(config_name: str) -> np.ndarray:
    path = OUT / f"current_0p591_block_label_oof_{config_name}.npy"
    if not path.exists():
        raise FileNotFoundError(path)
    return np.load(path)


def estimate_candidate(train: pd.DataFrame) -> pd.DataFrame:
    y = train[TARGETS].to_numpy(dtype=int)
    current = np.load(BASE_OOF)
    candidate = current.copy()
    for target, (config_name, weight) in SELECTED.items():
        j = TARGETS.index(target)
        block = load_oof_block(config_name)
        candidate[:, j] = (1.0 - weight) * candidate[:, j] + weight * block[:, j]
    candidate = clip(candidate)
    np.save(OOF_OUT, candidate)

    rows = []
    for j, target in enumerate(TARGETS):
        current_loss = blp.loss_col(y[:, j], current[:, j])
        candidate_loss = blp.loss_col(y[:, j], candidate[:, j])
        source = "unchanged"
        if target in SELECTED:
            config_name, weight = SELECTED[target]
            source = f"block_label_{config_name}_w{weight:g}"
        rows.append(
            {
                "target": target,
                "current_loss": current_loss,
                "candidate_loss": candidate_loss,
                "delta_vs_current": candidate_loss - current_loss,
                "source": source,
            }
        )
    estimate = pd.DataFrame(rows)
    estimate.loc[len(estimate)] = {
        "target": "mean",
        "current_loss": float(estimate["current_loss"].mean()),
        "candidate_loss": float(estimate["candidate_loss"].mean()),
        "delta_vs_current": float(estimate["candidate_loss"].mean() - estimate["current_loss"].mean()),
        "source": "target_mean",
    }
    estimate.to_csv(EST_OUT, index=False)
    return estimate


def make_submission(train: pd.DataFrame, sub: pd.DataFrame) -> pd.DataFrame:
    cfg_map = blp.cfg_by_name()
    out = pd.read_csv(BASE_SUB, parse_dates=["sleep_date", "lifelog_date"])
    out = out.sort_values(KEY).reset_index(drop=True)
    sub = sub.sort_values(KEY).reset_index(drop=True)
    for target, (config_name, weight) in SELECTED.items():
        cfg = cfg_map[config_name]
        j = TARGETS.index(target)
        block = brs.block_smoother(train, sub, cfg)[:, j]
        out[target] = clip((1.0 - weight) * out[target].to_numpy(dtype=float) + weight * block)
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    assert list(out.columns) == list(sample.columns)
    assert out[KEY].equals(sample[KEY])
    assert out[TARGETS].isna().sum().sum() == 0
    assert out.duplicated(KEY).sum() == 0
    assert ((out[TARGETS] >= 0).all().all() and (out[TARGETS] <= 1).all().all())
    out.to_csv(SUB_OUT, index=False)
    return out


def main() -> None:
    train = blp.train_frame()
    sub = blp.sub_frame()
    estimate = estimate_candidate(train)
    out = make_submission(train, sub)
    print(estimate.round(9).to_string(index=False))
    print("wrote", SUB_OUT)
    print("range", float(out[TARGETS].min().min()), float(out[TARGETS].max().max()))


if __name__ == "__main__":
    main()
