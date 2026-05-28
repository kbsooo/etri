from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))
import overnight_feature_experiments as ov  # noqa: E402


OUT = Path(__file__).resolve().parent
TARGETS = ov.TARGETS


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1 - 1e-5)


def main() -> None:
    train, sub = ov.prepare()
    base = pd.read_csv(OUT / "submission_hybrid_overnight_block.csv")
    context_sensor = ov.fit_predict(train, sub, "overnight_context")
    out = base.copy()
    out["S4"] = context_sensor[:, TARGETS.index("S4")]
    out[TARGETS] = out[TARGETS].clip(1e-5, 1 - 1e-5)
    out.to_csv(OUT / "submission_hybrid_overnight_context.csv", index=False)

    estimate = pd.read_csv(OUT / "hybrid_overnight_block_cv_estimate.csv")
    estimate = estimate[estimate["target"].isin(TARGETS)].copy()
    estimate.loc[estimate["target"].eq("S4"), "source"] = "overnight_context_sensor_only"
    estimate.loc[estimate["target"].eq("S4"), "cv_loss"] = 0.632913
    estimate.loc[len(estimate)] = {"target": "mean", "source": "hybrid_context_upgrade", "cv_loss": estimate["cv_loss"].mean()}
    estimate.to_csv(OUT / "hybrid_overnight_context_cv_estimate.csv", index=False)
    print("wrote", OUT / "submission_hybrid_overnight_context.csv")
    print(estimate.to_string(index=False))
    print("range", float(out[TARGETS].min().min()), float(out[TARGETS].max().max()))


if __name__ == "__main__":
    main()
