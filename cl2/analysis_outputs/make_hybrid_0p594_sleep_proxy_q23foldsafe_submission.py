from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))
import deep_dive_analysis as d  # noqa: E402
import sleep_interval_proxy_foldsafe_guardrail as fg  # noqa: E402


OUT = Path(__file__).resolve().parent
TARGETS = d.TARGETS
KEY = d.KEY


def main() -> None:
    train, sub = fg.base_frames()
    train = train.sort_values(KEY).reset_index(drop=True)
    sub = sub.sort_values(KEY).reset_index(drop=True)
    rel_cols = fg.relative_source_cols(train)
    train_aug = fg.add_ref_relative_features(train.copy(), train.copy(), rel_cols)
    sub_aug = fg.add_ref_relative_features(sub.copy(), train.copy(), rel_cols)
    cfg = next(c for c in fg.configs() if c.name == "foldsafe_leaf3_mf0.35")
    proxy_sub = fg.fit_predict(train_aug, sub_aug, cfg)

    out = pd.read_csv(OUT / "submission_hybrid_0p597_sleep_proxy_augmented.csv", parse_dates=["sleep_date", "lifelog_date"])
    base_repro = pd.read_csv(OUT / "submission_hybrid_0p598_repro.csv", parse_dates=["sleep_date", "lifelog_date"])
    out = out.sort_values(KEY).reset_index(drop=True)
    base_repro = base_repro.sort_values(KEY).reset_index(drop=True)

    weights = {"Q2": 0.20, "Q3": 0.10}
    losses = {"Q2": 0.6613165146067912, "Q3": 0.654440253964674}
    for target, weight in weights.items():
        j = TARGETS.index(target)
        out[target] = fg.clip((1.0 - weight) * base_repro[target].to_numpy(dtype=float) + weight * proxy_sub[:, j])
    out[TARGETS] = out[TARGETS].clip(1e-5, 1 - 1e-5)
    out.to_csv(OUT / "submission_hybrid_0p594_sleep_proxy_q23foldsafe.csv", index=False)

    estimate = pd.read_csv(OUT / "hybrid_0p595_sleep_proxy_augmented_cv_estimate.csv")
    for target, weight in weights.items():
        estimate.loc[estimate["target"].eq(target), "source"] = f"{cfg.name}_w{weight:g}_refstats_sleep_proxy"
        estimate.loc[estimate["target"].eq(target), "cv_loss"] = losses[target]
    estimate.loc[estimate["target"].eq("mean"), "source"] = "hybrid_0p594_sleep_proxy_q23foldsafe"
    estimate.loc[estimate["target"].eq("mean"), "cv_loss"] = float(
        estimate[estimate["target"].isin(TARGETS)]["cv_loss"].mean()
    )
    estimate.to_csv(OUT / "hybrid_0p594_sleep_proxy_q23foldsafe_cv_estimate.csv", index=False)

    note = pd.DataFrame(
        [
            {
                "target": "Q2",
                "config": cfg.name,
                "weight": 0.20,
                "subject_block_loss": losses["Q2"],
                "half_holdout_base": 0.6864564290481324,
                "half_holdout_weight_loss": 0.6817937954341492,
                "geometry_weight_loss": 0.663919,
                "decision": "promote",
            },
            {
                "target": "Q3",
                "config": cfg.name,
                "weight": 0.10,
                "subject_block_loss": losses["Q3"],
                "half_holdout_base": 0.6944116161555292,
                "half_holdout_weight_loss": 0.6939264771802403,
                "geometry_weight_loss": 0.654510,
                "decision": "promote low weight only",
            },
        ]
    )
    note.to_csv(OUT / "sleep_interval_proxy_q23foldsafe_candidate_note.csv", index=False)
    print(estimate.to_string(index=False))
    print("wrote", OUT / "submission_hybrid_0p594_sleep_proxy_q23foldsafe.csv", out.shape)


if __name__ == "__main__":
    main()
