from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))
import block_rate_smoother_experiments as brs  # noqa: E402
import calibration_experiments as cal  # noqa: E402
import deep_dive_analysis as d  # noqa: E402
import meta_feature_experiments as mf  # noqa: E402
import overnight_feature_experiments as ofe  # noqa: E402
import q23_presleep_app_experiments as q23app  # noqa: E402
from q2_soft_app_stack_experiments import APP_CANDIDATE, soft_rate_predict  # noqa: E402


OUT = Path(__file__).resolve().parent
TARGETS = d.TARGETS
KEY = d.KEY


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1 - 1e-5)


def q2_combo_predict(train: pd.DataFrame, sub: pd.DataFrame) -> np.ndarray:
    base = cal.temporal_base(train, sub)[:, TARGETS.index("Q2")]
    store = q23app.build_app_feature_store(pd.concat([train[KEY], sub[KEY]], ignore_index=True))
    app_pred = q23app.fit_candidate(train, sub, store, "Q2", APP_CANDIDATE)
    soft_pred = soft_rate_predict(train, sub)
    return clip(0.60 * base + 0.20 * app_pred + 0.20 * soft_pred)


def block_blend_predict(train: pd.DataFrame, sub: pd.DataFrame) -> np.ndarray:
    cfg = brs.parse_config("s32_a0.9_w10_eq_boost0")
    base = cal.temporal_base(train, sub)
    block = brs.block_smoother(train, sub, cfg)
    return clip(0.65 * base + 0.35 * block)


def main() -> None:
    train_meta, sub_meta = mf.prepare(force_meta=False)
    train_meta = train_meta.sort_values(KEY).reset_index(drop=True)
    sub_meta = sub_meta.sort_values(KEY).reset_index(drop=True)
    train_night, sub_night = ofe.prepare()
    train_night = train_night.sort_values(KEY).reset_index(drop=True)
    sub_night = sub_night.sort_values(KEY).reset_index(drop=True)

    out = pd.read_csv(OUT / "submission_hybrid_overnight_context.csv", parse_dates=["sleep_date", "lifelog_date"])
    out = out.sort_values(KEY).reset_index(drop=True)

    q2 = q2_combo_predict(train_meta, sub_meta)
    block = block_blend_predict(train_night, sub_night)
    overnight_context = ofe.fit_predict(train_night, sub_night, "overnight_context")
    overnight_all = ofe.fit_predict(train_night, sub_night, "overnight_all")

    out["Q2"] = q2
    out["S2"] = clip(0.70 * block[:, TARGETS.index("S2")] + 0.30 * overnight_all[:, TARGETS.index("S2")])
    out["S4"] = clip(0.55 * overnight_context[:, TARGETS.index("S4")] + 0.45 * block[:, TARGETS.index("S4")])

    out.to_csv(OUT / "submission_hybrid_0p599.csv", index=False)

    current = {
        "Q1": 0.625034,
        "Q2": 0.6927101523541841,
        "Q3": 0.6622200100969644,
        "S1": 0.524188,
        "S2": 0.5620673333578604,
        "S3": 0.535248,
        "S4": 0.6329127012137534,
    }
    upgraded = current.copy()
    upgraded.update(
        {
            "Q2": 0.6635717635251487,
            "S2": 0.5597193509033811,
            "S4": 0.6277842740609245,
        }
    )
    rows = []
    for target in TARGETS:
        rows.append(
            {
                "target": target,
                "old_loss": current[target],
                "new_loss": upgraded[target],
                "delta": upgraded[target] - current[target],
            }
        )
    rows.append(
        {
            "target": "mean",
            "old_loss": float(np.mean([current[t] for t in TARGETS])),
            "new_loss": float(np.mean([upgraded[t] for t in TARGETS])),
            "delta": float(np.mean([upgraded[t] - current[t] for t in TARGETS])),
        }
    )
    estimate = pd.DataFrame(rows)
    estimate.to_csv(OUT / "hybrid_0p599_cv_estimate.csv", index=False)

    print("wrote", OUT / "submission_hybrid_0p599.csv")
    print(estimate.round(6).to_string(index=False))
    print("shape", out.shape)
    print("nulls", int(out[TARGETS].isna().sum().sum()))
    print("range", float(out[TARGETS].min().min()), float(out[TARGETS].max().max()))
    print("means")
    print(out[TARGETS].mean().round(6).to_string())


if __name__ == "__main__":
    main()
