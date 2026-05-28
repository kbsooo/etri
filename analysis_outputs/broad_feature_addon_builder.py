from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

import broad_single_feature_residual_probe as broad
import geometry_mask_cv_experiments as geom


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


def build_frames() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train_raw = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    sub_raw = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    train = train_raw.copy()
    sub = sub_raw.copy()
    shared = [
        broad.prefixed_frame(OUT / "sleep_interval_proxy_features.parquet", "proxy"),
        broad.prefixed_frame(OUT / "pre_sleep_relative_features.parquet", "presleep"),
        broad.prefixed_frame(OUT / "presleep_temporal_context_features.parquet", "prectx"),
        broad.prefixed_frame(OUT / "quiet_window_residual_features.parquet", "quiet"),
        broad.prefixed_frame(OUT / "wifi_identity_daily_features.csv", "wifi"),
        broad.prefixed_frame(OUT / "ble_identity_daily_features.csv", "ble"),
    ]
    train_blocks = [broad.prefixed_frame(OUT / "train_deep_features.parquet", "deep")] + shared
    sub_blocks = [broad.prefixed_frame(OUT / "submission_deep_features.parquet", "deep")] + shared
    for block in train_blocks:
        train = train.merge(block, on=KEY, how="left")
    for block in sub_blocks:
        sub = sub.merge(block, on=KEY, how="left")
    return train_raw, sub_raw, train.sort_values(KEY).reset_index(drop=True), sub.sort_values(KEY).reset_index(drop=True)


def apply_op_oof(rows: pd.DataFrame, pred: np.ndarray, op: FeatureOp) -> np.ndarray:
    out = pred.copy()
    j = TARGETS.index(op.target)
    corrected = broad.oof_corrected(rows, out, op.target, op.feature, op.mode, op.c_value)
    out[:, j] = clip((1.0 - op.weight) * out[:, j] + op.weight * corrected)
    return out


def apply_op_fit_predict(ref: pd.DataFrame, rows: pd.DataFrame, ref_pred: np.ndarray, row_pred: np.ndarray, op: FeatureOp) -> np.ndarray:
    out = row_pred.copy()
    j = TARGETS.index(op.target)
    corrected = broad.fit_corrected(ref, rows, ref_pred, row_pred, op.target, op.feature, op.mode, op.c_value)
    out[:, j] = clip((1.0 - op.weight) * out[:, j] + op.weight * corrected)
    return out


def combo_defs() -> dict[str, list[FeatureOp]]:
    q1 = FeatureOp("Q1", "deep__usage_late_usage_kw_call_time_max", "subject_center", 0.50, 0.45)
    q2 = FeatureOp("Q2", "deep__phone_activity_morning_transitions", "subject_rank", 0.50, 0.30)
    return {
        "broad_q1_calltime": [q1],
        "broad_q2_activity_transition": [q2],
        "broad_q1_calltime_q2_activity": [q1, q2],
    }


def apply_combo_oof(rows: pd.DataFrame, base: np.ndarray, ops: list[FeatureOp]) -> np.ndarray:
    out = base.copy()
    for op in ops:
        out = apply_op_oof(rows, out, op)
    return clip(out)


def geometry_summary(train_raw: pd.DataFrame, sub_raw: pd.DataFrame, train_feat: pd.DataFrame, base: np.ndarray, ops: list[FeatureOp]) -> dict[str, float]:
    y_all = train_raw[TARGETS].to_numpy(dtype=int)
    rows = []
    for tr_idx, val_idx, fold in geom.geometry_folds(train_raw, sub_raw, n_repeats=10):
        ref = train_feat.iloc[tr_idx].reset_index(drop=True)
        val = train_feat.iloc[val_idx].reset_index(drop=True)
        ref_pred = base[tr_idx].copy()
        val_pred = base[val_idx].copy()
        for op in ops:
            val_pred = apply_op_fit_predict(ref, val, ref_pred, val_pred, op)
            ref_pred = apply_op_fit_predict(ref, ref, ref_pred, ref_pred, op)
        y = y_all[val_idx]
        row = {"fold": fold, "base_mean": mean_loss(y, base[val_idx]), "candidate_mean": mean_loss(y, val_pred)}
        row["delta_mean"] = row["candidate_mean"] - row["base_mean"]
        for j, target in enumerate(TARGETS):
            row[f"{target}_delta"] = loss_col(y[:, j], val_pred[:, j]) - loss_col(y[:, j], base[val_idx, j])
        rows.append(row)
    df = pd.DataFrame(rows)
    summary = {"geometry_delta": float(df["delta_mean"].mean()), "geometry_win_rate": float((df["delta_mean"] < 0).mean())}
    for target in TARGETS:
        summary[f"geometry_{target}_delta"] = float(df[f"{target}_delta"].mean())
    return summary


def save_submission(prefix: str, train_feat: pd.DataFrame, sub_feat: pd.DataFrame, base_oof: np.ndarray, ops: list[FeatureOp]) -> None:
    base_sub_file = OUT / "submission_hybrid_0p575_foldsafe_quiet_s3_subject_q3_s4_s1_logit_s1.csv"
    out = pd.read_csv(base_sub_file, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    assert out[SUB_KEY].equals(sample[SUB_KEY])
    pred = out[TARGETS].to_numpy(dtype=float)
    ref = base_oof.copy()
    for op in ops:
        pred = apply_op_fit_predict(train_feat, sub_feat, ref, pred, op)
        ref = apply_op_fit_predict(train_feat, train_feat, ref, ref, op)
    out[TARGETS] = clip(pred)
    assert out[TARGETS].isna().sum().sum() == 0
    assert out.duplicated(SUB_KEY).sum() == 0
    out.to_csv(OUT / f"submission_{prefix}.csv", index=False)


def main() -> None:
    train_raw, sub_raw, train_feat, sub_feat = build_frames()
    y = train_raw[TARGETS].to_numpy(dtype=int)
    base = clip(np.load(OUT / "final_hybrid_0p575_foldsafe_quiet_s3_subject_q3_s4_s1_logit_s1_oof.npy"))
    base_loss = mean_loss(y, base)
    rows = []
    target_rows = []
    preds = {}
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
    summary.to_csv(OUT / "broad_feature_addon_combo_summary.csv", index=False)
    target_df.to_csv(OUT / "broad_feature_addon_combo_targets.csv", index=False)
    for row in summary.itertuples(index=False):
        if float(row.geometry_delta) <= 0.0:
            name = str(row.combo)
            prefix = f"hybrid_0p573_foldsafe_{name}"
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
