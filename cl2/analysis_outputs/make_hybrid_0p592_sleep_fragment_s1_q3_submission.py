from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))
import current_0p594_cross_target_coherence as cur  # noqa: E402
import deep_dive_analysis as d  # noqa: E402
import sleep_fragmentation_proxy_experiments as frag  # noqa: E402
import sleep_interval_proxy_foldsafe_guardrail as fg  # noqa: E402


OUT = Path(__file__).resolve().parent
DATA = OUT.parents[0] / "data"
KEY = d.KEY
TARGETS = d.TARGETS
BASE_SUB = OUT / "submission_hybrid_0p594_sleep_proxy_q23foldsafe.csv"
SUB_OUT = OUT / "submission_hybrid_0p592_sleep_fragment_s1_q3.csv"
EST_OUT = OUT / "hybrid_0p592_sleep_fragment_s1_q3_cv_estimate.csv"
OOF_OUT = OUT / "final_hybrid_0p592_sleep_fragment_s1_q3_oof.npy"

S1_CFG = "frag_leaf4_mf0.6_depth10"
S1_WEIGHT = 0.60
Q3_CFG = "frag_leaf3_mf0.35"
Q3_WEIGHT = 0.30


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1 - 1e-5)


def full_fragment_prediction(train: pd.DataFrame, sub: pd.DataFrame, cfg_name: str) -> np.ndarray:
    cfg = next(cfg for cfg in frag.configs() if cfg.name == cfg_name)
    rel_cols = fg.relative_source_cols(train)
    ref = fg.add_ref_relative_features(train.copy().reset_index(drop=True), train.copy().reset_index(drop=True), rel_cols)
    sub_rel = fg.add_ref_relative_features(sub.copy().reset_index(drop=True), train.copy().reset_index(drop=True), rel_cols)
    return frag.fit_predict(ref, sub_rel, cfg)


def main() -> None:
    train, sub = frag.prepare_frames()
    y = train[TARGETS].to_numpy(dtype=int)
    current = cur.current_oof()
    candidate = current.copy()

    s1_j = TARGETS.index("S1")
    q3_j = TARGETS.index("Q3")
    s1_oof = np.load(OUT / f"sleep_fragmentation_proxy_oof_{S1_CFG}.npy")
    q3_oof = np.load(OUT / f"sleep_fragmentation_proxy_oof_{Q3_CFG}.npy")
    candidate[:, s1_j] = (1.0 - S1_WEIGHT) * candidate[:, s1_j] + S1_WEIGHT * s1_oof[:, s1_j]
    candidate[:, q3_j] = (1.0 - Q3_WEIGHT) * candidate[:, q3_j] + Q3_WEIGHT * q3_oof[:, q3_j]
    candidate = clip(candidate)
    np.save(OOF_OUT, candidate)

    rows = []
    for j, target in enumerate(TARGETS):
        current_loss = frag.loss_col(y[:, j], current[:, j])
        candidate_loss = frag.loss_col(y[:, j], candidate[:, j])
        rows.append(
            {
                "target": target,
                "current_loss": current_loss,
                "candidate_loss": candidate_loss,
                "delta_vs_current": candidate_loss - current_loss,
                "source": "fragment_s1_leaf4_w0.60" if target == "S1" else "fragment_q3_leaf3_w0.30" if target == "Q3" else "unchanged",
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

    s1_sub = full_fragment_prediction(train, sub, S1_CFG)
    q3_sub = full_fragment_prediction(train, sub, Q3_CFG)
    frag_sub = sub[KEY].copy()
    frag_sub["S1_fragment"] = s1_sub[:, s1_j]
    frag_sub["Q3_fragment"] = q3_sub[:, q3_j]

    out = pd.read_csv(BASE_SUB, parse_dates=["sleep_date", "lifelog_date"])
    out = out.merge(frag_sub, on=KEY, how="left", validate="one_to_one")
    out["S1"] = clip((1.0 - S1_WEIGHT) * out["S1"].to_numpy() + S1_WEIGHT * out["S1_fragment"].to_numpy())
    out["Q3"] = clip((1.0 - Q3_WEIGHT) * out["Q3"].to_numpy() + Q3_WEIGHT * out["Q3_fragment"].to_numpy())
    out = out.drop(columns=["S1_fragment", "Q3_fragment"])

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
