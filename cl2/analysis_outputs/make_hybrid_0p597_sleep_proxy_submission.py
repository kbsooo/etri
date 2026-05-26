from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))
import deep_dive_analysis as d  # noqa: E402
import sleep_interval_proxy_experiments as sip  # noqa: E402
import sleep_interval_proxy_model_search as search  # noqa: E402


OUT = Path(__file__).resolve().parent
TARGETS = d.TARGETS
KEY = d.KEY


def main() -> None:
    train, sub = sip.prepare_frames()
    cfg = search.ETConfig("et_leaf6_mf0.8", 420, 6, 0.80, None, 260526 + 6 * 10 + 80)
    proxy_sub = search.fit_predict(train.copy(), sub.copy(), cfg)

    out = pd.read_csv(OUT / "submission_hybrid_0p598_repro.csv", parse_dates=["sleep_date", "lifelog_date"])
    out = out.sort_values(KEY).reset_index(drop=True)
    weights = {"Q1": 0.30, "S1": 0.30}
    for target, weight in weights.items():
        j = TARGETS.index(target)
        out[target] = sip.clip((1.0 - weight) * out[target].to_numpy(dtype=float) + weight * proxy_sub[:, j])
    out[TARGETS] = out[TARGETS].clip(1e-5, 1 - 1e-5)
    out.to_csv(OUT / "submission_hybrid_0p597_sleep_proxy.csv", index=False)

    estimate = pd.read_csv(OUT / "hybrid_0p598_repro_cv_estimate.csv")
    search_results = pd.read_csv(OUT / "sleep_interval_proxy_model_search_results.csv")
    for target in weights:
        row = search_results[search_results["config"].eq(cfg.name) & search_results["target"].eq(target)].iloc[0]
        estimate.loc[estimate["target"].eq(target), "source"] = f"{cfg.name}_w{weights[target]:g}_sleep_proxy"
        estimate.loc[estimate["target"].eq(target), "cv_loss"] = float(row["best_blend_loss"])
    mean_loss = float(estimate[estimate["target"].isin(TARGETS)]["cv_loss"].mean())
    estimate.loc[estimate["target"].eq("mean"), "source"] = "hybrid_0p597_sleep_proxy"
    estimate.loc[estimate["target"].eq("mean"), "cv_loss"] = mean_loss
    estimate.to_csv(OUT / "hybrid_0p597_sleep_proxy_cv_estimate.csv", index=False)

    print(estimate.to_string(index=False))
    print("wrote", OUT / "submission_hybrid_0p597_sleep_proxy.csv", out.shape)


if __name__ == "__main__":
    main()
