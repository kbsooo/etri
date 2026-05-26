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

    q2_weight = 0.20
    q2_idx = TARGETS.index("Q2")
    out["Q2"] = fg.clip((1.0 - q2_weight) * base_repro["Q2"].to_numpy(dtype=float) + q2_weight * proxy_sub[:, q2_idx])
    out[TARGETS] = out[TARGETS].clip(1e-5, 1 - 1e-5)
    out.to_csv(OUT / "submission_hybrid_0p594_sleep_proxy_q2foldsafe.csv", index=False)

    estimate = pd.read_csv(OUT / "hybrid_0p595_sleep_proxy_augmented_cv_estimate.csv")
    q2_results = pd.read_csv(OUT / "sleep_interval_proxy_foldsafe_results.csv")
    q2_row = q2_results[
        q2_results["config"].eq(cfg.name)
        & q2_results["target"].eq("Q2")
        & q2_results["best_weight"].eq(q2_weight)
    ]
    if q2_row.empty:
        q2_loss = float(q2_results[q2_results["config"].eq(cfg.name) & q2_results["target"].eq("Q2")]["best_blend_loss"].iloc[0])
    else:
        q2_loss = float(q2_row["best_blend_loss"].iloc[0])
    estimate.loc[estimate["target"].eq("Q2"), "source"] = f"{cfg.name}_w{q2_weight:g}_refstats_sleep_proxy"
    estimate.loc[estimate["target"].eq("Q2"), "cv_loss"] = q2_loss
    estimate.loc[estimate["target"].eq("mean"), "source"] = "hybrid_0p594_sleep_proxy_q2foldsafe"
    estimate.loc[estimate["target"].eq("mean"), "cv_loss"] = float(
        estimate[estimate["target"].isin(TARGETS)]["cv_loss"].mean()
    )
    estimate.to_csv(OUT / "hybrid_0p594_sleep_proxy_q2foldsafe_cv_estimate.csv", index=False)

    note = pd.DataFrame(
        [
            {
                "target": "Q2",
                "config": cfg.name,
                "weight": q2_weight,
                "subject_block_loss": q2_loss,
                "half_holdout_base": 0.6864564290481324,
                "half_holdout_w0.20": 0.6817937954341492,
                "geometry_best_weight": 0.45,
                "geometry_best_loss": 0.659773,
                "decision": "promote Q2 fold-safe ref-stat sleep proxy",
            }
        ]
    )
    note.to_csv(OUT / "sleep_interval_proxy_q2foldsafe_candidate_note.csv", index=False)
    print(estimate.to_string(index=False))
    print("wrote", OUT / "submission_hybrid_0p594_sleep_proxy_q2foldsafe.csv", out.shape)


if __name__ == "__main__":
    main()
