from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))
import current_0p586_gentle_logit_calibration as glc  # noqa: E402
import current_0p591_block_label_postprocess as blp  # noqa: E402
import deep_dive_analysis as d  # noqa: E402


OUT = Path(__file__).resolve().parent
DATA = OUT.parents[0] / "data"
KEY = d.KEY
TARGETS = d.TARGETS
BASE_SUB = OUT / "submission_hybrid_0p585_gentle_logit_calibration.csv"
BASE_OOF = OUT / "final_hybrid_0p585_gentle_logit_calibration_oof.npy"
SUB_OUT = OUT / "submission_hybrid_0p584_gentle_logit_residual.csv"
EST_OUT = OUT / "hybrid_0p584_gentle_logit_residual_cv_estimate.csv"
OOF_OUT = OUT / "final_hybrid_0p584_gentle_logit_residual_oof.npy"

SELECTED = {
    "Q1": "scale1.3_shift0_w0.2",
    "Q2": "scale1.15_shift0.08_w0.2",
    "Q3": "scale1.3_shift0_w0.2",
    "S1": "scale1.3_shift0_w0.2",
    "S2": "scale1.15_shift-0.08_w0.2",
    "S3": "scale1.15_shift-0.08_w0.2",
    "S4": "scale1.3_shift0_w0.2",
}


def estimate_candidate(train: pd.DataFrame) -> pd.DataFrame:
    y = train[TARGETS].to_numpy(dtype=int)
    current = np.load(BASE_OOF)
    candidate = current.copy()
    for target, config_name in SELECTED.items():
        j = TARGETS.index(target)
        cfg = glc.parse_config(config_name)
        candidate[:, j] = glc.calibrate(candidate[:, j], cfg)
    np.save(OOF_OUT, candidate)

    rows = []
    for j, target in enumerate(TARGETS):
        current_loss = glc.srq.loss_col(y[:, j], current[:, j])
        candidate_loss = glc.srq.loss_col(y[:, j], candidate[:, j])
        rows.append(
            {
                "target": target,
                "current_loss": current_loss,
                "candidate_loss": candidate_loss,
                "delta_vs_current": candidate_loss - current_loss,
                "source": f"gentle_logit_residual_{SELECTED[target]}",
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


def make_submission(sub: pd.DataFrame) -> pd.DataFrame:
    out = pd.read_csv(BASE_SUB, parse_dates=["sleep_date", "lifelog_date"])
    out = out.sort_values(KEY).reset_index(drop=True)
    sub = sub.sort_values(KEY).reset_index(drop=True)
    assert out[KEY].equals(sub[KEY])
    for target, config_name in SELECTED.items():
        cfg = glc.parse_config(config_name)
        out[target] = glc.calibrate(out[target].to_numpy(dtype=float), cfg)
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
    out = make_submission(sub)
    print(estimate.round(9).to_string(index=False))
    print("wrote", SUB_OUT)
    print("range", float(out[TARGETS].min().min()), float(out[TARGETS].max().max()))


if __name__ == "__main__":
    main()
