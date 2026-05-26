from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))
import deep_dive_analysis as d  # noqa: E402
import sleep_dynamics_proxy_experiments as dyn  # noqa: E402
import sleep_interval_proxy_foldsafe_guardrail as fg  # noqa: E402


OUT = Path(__file__).resolve().parent
DATA = OUT.parents[0] / "data"
KEY = d.KEY
TARGETS = d.TARGETS
BASE_SUB = OUT / "submission_hybrid_0p592_sleep_fragment_s1_q3.csv"
BASE_OOF = OUT / "final_hybrid_0p592_sleep_fragment_s1_q3_oof.npy"
SUB_OUT = OUT / "submission_hybrid_0p591_sleep_dynamics_s1_s4.csv"
EST_OUT = OUT / "hybrid_0p591_sleep_dynamics_s1_s4_cv_estimate.csv"
OOF_OUT = OUT / "final_hybrid_0p591_sleep_dynamics_s1_s4_oof.npy"

S1_CFG = "dyn_leaf6_mf0.8"
S1_WEIGHT = 0.30
S4_CFG = "dyn_leaf3_mf0.35"
S4_WEIGHT = 0.08


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1 - 1e-5)


def full_dynamic_prediction(train: pd.DataFrame, sub: pd.DataFrame, cfg_name: str) -> np.ndarray:
    cfg = next(cfg for cfg in dyn.configs() if cfg.name == cfg_name)
    rel_cols = dyn.relative_source_cols(train)
    ref = fg.add_ref_relative_features(train.copy().reset_index(drop=True), train.copy().reset_index(drop=True), rel_cols)
    sub_rel = fg.add_ref_relative_features(sub.copy().reset_index(drop=True), train.copy().reset_index(drop=True), rel_cols)
    return dyn.fit_predict(ref, sub_rel, cfg)


def main() -> None:
    train, sub = dyn.prepare_frames()
    y = train[TARGETS].to_numpy(dtype=int)
    current = np.load(BASE_OOF)
    candidate = current.copy()

    s1_j = TARGETS.index("S1")
    s4_j = TARGETS.index("S4")
    s1_oof = np.load(OUT / f"sleep_dynamics_proxy_oof_{S1_CFG}.npy")
    s4_oof = np.load(OUT / f"sleep_dynamics_proxy_oof_{S4_CFG}.npy")
    candidate[:, s1_j] = (1.0 - S1_WEIGHT) * candidate[:, s1_j] + S1_WEIGHT * s1_oof[:, s1_j]
    candidate[:, s4_j] = (1.0 - S4_WEIGHT) * candidate[:, s4_j] + S4_WEIGHT * s4_oof[:, s4_j]
    candidate = clip(candidate)
    np.save(OOF_OUT, candidate)

    rows = []
    for j, target in enumerate(TARGETS):
        current_loss = dyn.loss_col(y[:, j], current[:, j])
        candidate_loss = dyn.loss_col(y[:, j], candidate[:, j])
        rows.append(
            {
                "target": target,
                "current_loss": current_loss,
                "candidate_loss": candidate_loss,
                "delta_vs_current": candidate_loss - current_loss,
                "source": "dynamic_s1_leaf6_w0.30" if target == "S1" else "dynamic_s4_leaf3_w0.08" if target == "S4" else "unchanged",
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

    s1_sub = full_dynamic_prediction(train, sub, S1_CFG)
    s4_sub = full_dynamic_prediction(train, sub, S4_CFG)
    dyn_sub = sub[KEY].copy()
    dyn_sub["S1_dynamic"] = s1_sub[:, s1_j]
    dyn_sub["S4_dynamic"] = s4_sub[:, s4_j]

    out = pd.read_csv(BASE_SUB, parse_dates=["sleep_date", "lifelog_date"])
    out = out.merge(dyn_sub, on=KEY, how="left", validate="one_to_one")
    out["S1"] = clip((1.0 - S1_WEIGHT) * out["S1"].to_numpy() + S1_WEIGHT * out["S1_dynamic"].to_numpy())
    out["S4"] = clip((1.0 - S4_WEIGHT) * out["S4"].to_numpy() + S4_WEIGHT * out["S4_dynamic"].to_numpy())
    out = out.drop(columns=["S1_dynamic", "S4_dynamic"])

    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    assert list(out.columns) == list(sample.columns)
    assert out[KEY].equals(sample[KEY])
    assert out[TARGETS].isna().sum().sum() == 0
    assert out.duplicated(KEY).sum() == 0
    assert ((out[TARGETS] >= 0).all().all() and (out[TARGETS] <= 1).all().all())
    out.to_csv(SUB_OUT, index=False)

    print(estimate.round(9).to_string(index=False))
    print("wrote", SUB_OUT)
    print("range", float(out[TARGETS].min().min()), float(out[TARGETS].max().max()))


if __name__ == "__main__":
    main()
