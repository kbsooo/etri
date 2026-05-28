from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

import broad_feature_addon_builder as b1


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "lifelog_date"]
SUB_KEY = ["subject_id", "sleep_date", "lifelog_date"]


@dataclass(frozen=True)
class FeatureOp:
    target: str
    feature: str
    mode: str
    c_value: float
    weight: float


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1.0 - 1e-5)


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    yy = y.astype(float)
    pp = clip(p)
    return float(-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp)).mean())


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([loss_col(y[:, j], pred[:, j]) for j in range(len(TARGETS))]))


def to_b1(op: FeatureOp) -> b1.FeatureOp:
    return b1.FeatureOp(op.target, op.feature, op.mode, op.c_value, op.weight)


def combo_defs() -> dict[str, list[FeatureOp]]:
    q1 = FeatureOp("Q1", "deep__watch_light_w_light_all_log_mean", "subject_center", 0.50, 0.45)
    q3 = FeatureOp("Q3", "deep__ble_morning_unique_max", "subject_rank", 0.20, 0.45)
    s1 = FeatureOp("S1", "deep__ambience_all_hour_mean", "subject_z", 0.50, 0.45)
    s2 = FeatureOp("S2", "deep__phone_light_m_light_late_median", "subject_z", 0.50, 0.45)
    s3 = FeatureOp("S3", "deep__hr_all_rows", "subject_rank", 0.50, 0.45)
    s4 = FeatureOp("S4", "deep__ambience_evening_top_is_outside_mean", "subject_center", 0.50, 0.45)
    return {
        "stage2_q3_s1_s4": [q3, s1, s4],
        "stage2_q3_s1_s2_s3_s4": [q3, s1, s2, s3, s4],
        "stage2_q1_q3_s1_s4": [q1, q3, s1, s4],
        "stage2_q1_q3_s1_s2_s3_s4": [q1, q3, s1, s2, s3, s4],
    }


def apply_combo_oof(train_feat: pd.DataFrame, base: np.ndarray, ops: list[FeatureOp]) -> np.ndarray:
    out = base.copy()
    for op in ops:
        out = b1.apply_op_oof(train_feat, out, to_b1(op))
    return clip(out)


def geometry_summary(train_raw: pd.DataFrame, sub_raw: pd.DataFrame, train_feat: pd.DataFrame, base: np.ndarray, ops: list[FeatureOp]) -> dict[str, float]:
    return b1.geometry_summary(train_raw, sub_raw, train_feat, base, [to_b1(op) for op in ops])


def save_submission(prefix: str, train_feat: pd.DataFrame, sub_feat: pd.DataFrame, base_oof: np.ndarray, ops: list[FeatureOp]) -> None:
    out = pd.read_csv(
        OUT / "submission_hybrid_0p573_foldsafe_broad_q1_calltime_q2_activity.csv",
        parse_dates=["sleep_date", "lifelog_date"],
    ).sort_values(KEY).reset_index(drop=True)
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    assert out[SUB_KEY].equals(sample[SUB_KEY])
    pred = out[TARGETS].to_numpy(dtype=float)
    ref = base_oof.copy()
    for op in ops:
        op1 = to_b1(op)
        pred = b1.apply_op_fit_predict(train_feat, sub_feat, ref, pred, op1)
        ref = b1.apply_op_fit_predict(train_feat, train_feat, ref, ref, op1)
    out[TARGETS] = clip(pred)
    assert out[TARGETS].isna().sum().sum() == 0
    assert out.duplicated(SUB_KEY).sum() == 0
    out.to_csv(OUT / f"submission_{prefix}.csv", index=False)


def main() -> None:
    train_raw, sub_raw, train_feat, sub_feat = b1.build_frames()
    y = train_raw[TARGETS].to_numpy(dtype=int)
    base = clip(np.load(OUT / "final_hybrid_0p573_foldsafe_broad_q1_calltime_q2_activity_oof.npy"))
    base_loss = mean_loss(y, base)
    rows = []
    target_rows = []
    preds: dict[str, np.ndarray] = {}
    for name, ops in combo_defs().items():
        pred = apply_combo_oof(train_feat, base, ops)
        preds[name] = pred
        row = {
            "combo": name,
            "base_loss": base_loss,
            "candidate_loss": mean_loss(y, pred),
            "delta": mean_loss(y, pred) - base_loss,
        }
        row.update(geometry_summary(train_raw, sub_raw, train_feat, base, ops))
        rows.append(row)
        for j, target in enumerate(TARGETS):
            target_rows.append(
                {
                    "combo": name,
                    "target": target,
                    "base_loss": loss_col(y[:, j], base[:, j]),
                    "candidate_loss": loss_col(y[:, j], pred[:, j]),
                    "delta": loss_col(y[:, j], pred[:, j]) - loss_col(y[:, j], base[:, j]),
                }
            )
    summary = pd.DataFrame(rows).sort_values(["candidate_loss", "geometry_delta"])
    target_df = pd.DataFrame(target_rows)
    summary.to_csv(OUT / "broad_stage2_addon_combo_summary.csv", index=False)
    target_df.to_csv(OUT / "broad_stage2_addon_combo_targets.csv", index=False)
    for row in summary.itertuples(index=False):
        if float(row.geometry_delta) <= 0.0:
            name = str(row.combo)
            prefix = f"hybrid_0p567_foldsafe_{name}"
            np.save(OUT / f"final_{prefix}_oof.npy", preds[name])
            pd.DataFrame(
                [
                    {
                        "target": target,
                        "current_loss": loss_col(y[:, j], base[:, j]),
                        "candidate_loss": loss_col(y[:, j], preds[name][:, j]),
                        "delta_vs_current": loss_col(y[:, j], preds[name][:, j]) - loss_col(y[:, j], base[:, j]),
                    }
                    for j, target in enumerate(TARGETS)
                ]
                + [
                    {
                        "target": "mean",
                        "current_loss": base_loss,
                        "candidate_loss": mean_loss(y, preds[name]),
                        "delta_vs_current": mean_loss(y, preds[name]) - base_loss,
                    }
                ]
            ).to_csv(OUT / f"{prefix}_cv_estimate.csv", index=False)
            save_submission(prefix, train_feat, sub_feat, base, combo_defs()[name])
    print(summary.round(9).to_string(index=False))
    print(target_df.sort_values(["combo", "target"]).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
