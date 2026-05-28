from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

import broad_feature_addon_builder as b1


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
TARGETS = b1.TARGETS
KEY = b1.KEY
SUB_KEY = b1.SUB_KEY


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1.0 - 1e-5)


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    yy = y.astype(float)
    pp = clip(p)
    return float(-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp)).mean())


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([loss_col(y[:, j], pred[:, j]) for j in range(len(TARGETS))]))


def main() -> None:
    train_raw, sub_raw, train_feat, sub_feat = b1.build_frames()
    y = train_raw[TARGETS].to_numpy(dtype=int)
    base_oof = clip(np.load(OUT / "final_publicgated_anchor578_stage2_drop_q3_prob_w650_oof.npy"))
    base_sub_file = OUT / "submission_publicgated_anchor578_stage2_drop_q3_prob_w650.csv"
    base_sub = pd.read_csv(base_sub_file, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    assert base_sub[SUB_KEY].equals(sample[SUB_KEY])

    feature = "presleep__presleep_hr_pre6h_hr_points_count"
    rows = []
    target_rows = []
    for c_value in [0.05, 0.10, 0.20, 0.50]:
        for weight in [0.10, 0.15, 0.20, 0.30, 0.45]:
            op = b1.FeatureOp("Q3", feature, "subject_z", c_value, weight)
            pred = b1.apply_op_oof(train_feat, base_oof, op)
            row = {
                "name": f"Q3_presleep_hrpoints_c{c_value:g}_w{weight:g}",
                "feature": feature,
                "c_value": c_value,
                "weight": weight,
                "base_loss": mean_loss(y, base_oof),
                "candidate_loss": mean_loss(y, pred),
                "delta": mean_loss(y, pred) - mean_loss(y, base_oof),
            }
            row.update(b1.geometry_summary(train_raw, sub_raw, train_feat, base_oof, [op]))
            rows.append(row)
            for j, target in enumerate(TARGETS):
                target_rows.append(
                    {
                        "name": row["name"],
                        "target": target,
                        "base_loss": loss_col(y[:, j], base_oof[:, j]),
                        "candidate_loss": loss_col(y[:, j], pred[:, j]),
                        "delta": loss_col(y[:, j], pred[:, j]) - loss_col(y[:, j], base_oof[:, j]),
                    }
                )
            if row["geometry_delta"] <= 0.0 and row["delta"] <= -0.0004:
                sub_pred = base_sub[TARGETS].to_numpy(dtype=float)
                sub_pred = b1.apply_op_fit_predict(train_feat, sub_feat, base_oof, sub_pred, op)
                out = base_sub.copy()
                out[TARGETS] = clip(sub_pred)
                prefix = f"publicgated_q3off650_presleep_hrpoints_c{c_value:g}_w{weight:g}"
                out.to_csv(OUT / f"submission_{prefix}.csv", index=False)
                np.save(OUT / f"final_{prefix}_oof.npy", pred)
                pd.DataFrame(
                    [
                        {
                            "target": target,
                            "base_loss": loss_col(y[:, j], base_oof[:, j]),
                            "candidate_loss": loss_col(y[:, j], pred[:, j]),
                            "delta": loss_col(y[:, j], pred[:, j]) - loss_col(y[:, j], base_oof[:, j]),
                        }
                        for j, target in enumerate(TARGETS)
                    ]
                    + [{"target": "mean", "base_loss": mean_loss(y, base_oof), "candidate_loss": mean_loss(y, pred), "delta": mean_loss(y, pred) - mean_loss(y, base_oof)}]
                ).to_csv(OUT / f"{prefix}_cv_estimate.csv", index=False)
    summary = pd.DataFrame(rows).sort_values(["geometry_delta", "delta"])
    target_df = pd.DataFrame(target_rows)
    summary.to_csv(OUT / "presleep_q3_candidate_summary.csv", index=False)
    target_df.to_csv(OUT / "presleep_q3_candidate_targets.csv", index=False)
    print(summary.round(9).to_string(index=False))
    print(target_df.sort_values(["name", "target"]).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
