from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

import broad_feature_addon_builder as b1
import broad_single_feature_residual_probe as broad
import broad_stage2_addon_builder as stage2


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]


def stage2_ops() -> list[stage2.FeatureOp]:
    return stage2.combo_defs()["stage2_q1_q3_s1_s2_s3_s4"]


def finite_stats(values: np.ndarray) -> dict[str, float]:
    vals = np.asarray(values, dtype=float)
    finite = vals[np.isfinite(vals)]
    row: dict[str, float] = {
        "n": float(len(vals)),
        "missing": float(len(vals) - len(finite)),
        "missing_rate": float((len(vals) - len(finite)) / max(len(vals), 1)),
    }
    if len(finite) == 0:
        for key in ["mean", "std", "min", "p01", "p05", "p10", "p25", "p50", "p75", "p90", "p95", "p99", "max"]:
            row[key] = np.nan
        return row
    row.update(
        {
            "mean": float(np.mean(finite)),
            "std": float(np.std(finite, ddof=1)) if len(finite) > 1 else 0.0,
            "min": float(np.min(finite)),
            "p01": float(np.quantile(finite, 0.01)),
            "p05": float(np.quantile(finite, 0.05)),
            "p10": float(np.quantile(finite, 0.10)),
            "p25": float(np.quantile(finite, 0.25)),
            "p50": float(np.quantile(finite, 0.50)),
            "p75": float(np.quantile(finite, 0.75)),
            "p90": float(np.quantile(finite, 0.90)),
            "p95": float(np.quantile(finite, 0.95)),
            "p99": float(np.quantile(finite, 0.99)),
            "max": float(np.max(finite)),
        }
    )
    return row


def prefixed(prefix: str, stats: dict[str, float]) -> dict[str, float]:
    return {f"{prefix}_{k}": v for k, v in stats.items()}


def shift_row(train_values: np.ndarray, sub_values: np.ndarray) -> dict[str, float]:
    tr = np.asarray(train_values, dtype=float)
    su = np.asarray(sub_values, dtype=float)
    tr_f = tr[np.isfinite(tr)]
    su_f = su[np.isfinite(su)]
    if len(tr_f) == 0 or len(su_f) == 0:
        return {
            "mean_shift_z": np.nan,
            "std_ratio": np.nan,
            "p50_shift_z": np.nan,
            "p90_shift_z": np.nan,
            "sub_below_train_min_rate": np.nan,
            "sub_above_train_max_rate": np.nan,
            "sub_outside_train_range_rate": np.nan,
        }
    tr_std = float(np.std(tr_f, ddof=1)) if len(tr_f) > 1 else 0.0
    denom = tr_std if np.isfinite(tr_std) and tr_std > 1e-12 else 1.0
    below = float((su_f < np.min(tr_f)).mean())
    above = float((su_f > np.max(tr_f)).mean())
    return {
        "mean_shift_z": float((np.mean(su_f) - np.mean(tr_f)) / denom),
        "std_ratio": float((np.std(su_f, ddof=1) if len(su_f) > 1 else 0.0) / denom),
        "p50_shift_z": float((np.quantile(su_f, 0.50) - np.quantile(tr_f, 0.50)) / denom),
        "p90_shift_z": float((np.quantile(su_f, 0.90) - np.quantile(tr_f, 0.90)) / denom),
        "sub_below_train_min_rate": below,
        "sub_above_train_max_rate": above,
        "sub_outside_train_range_rate": below + above,
    }


def feature_shift_audit(train_feat: pd.DataFrame, sub_feat: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for op in stage2_ops():
        raw_train = pd.to_numeric(train_feat[op.feature], errors="coerce").to_numpy(dtype=float)
        raw_sub = pd.to_numeric(sub_feat[op.feature], errors="coerce").to_numpy(dtype=float)
        z_train, z_sub = broad.transform_pair(train_feat, sub_feat, op.feature, op.mode)
        row = {
            "target": op.target,
            "feature": op.feature,
            "mode": op.mode,
            "c_value": op.c_value,
            "weight": op.weight,
        }
        row.update(prefixed("raw_train", finite_stats(raw_train)))
        row.update(prefixed("raw_sub", finite_stats(raw_sub)))
        row.update(prefixed("raw", shift_row(raw_train, raw_sub)))
        row.update(prefixed("mode_train", finite_stats(z_train)))
        row.update(prefixed("mode_sub", finite_stats(z_sub)))
        row.update(prefixed("mode", shift_row(z_train, z_sub)))
        rows.append(row)
    return pd.DataFrame(rows)


def probability_delta_audit(train_raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    base_sub = pd.read_csv(OUT / "submission_hybrid_0p573_foldsafe_broad_q1_calltime_q2_activity.csv")
    cand_sub = pd.read_csv(OUT / "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv")
    base_oof = b1.clip(np.load(OUT / "final_hybrid_0p573_foldsafe_broad_q1_calltime_q2_activity_oof.npy"))
    cand_oof = b1.clip(np.load(OUT / "final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy"))
    y = train_raw[TARGETS].to_numpy(dtype=int)

    sub_rows = []
    oof_rows = []
    for j, target in enumerate(TARGETS):
        sub_delta = cand_sub[target].to_numpy(dtype=float) - base_sub[target].to_numpy(dtype=float)
        oof_delta = cand_oof[:, j] - base_oof[:, j]
        sub_rows.append(
            {
                "target": target,
                "submission_base_mean": float(base_sub[target].mean()),
                "submission_candidate_mean": float(cand_sub[target].mean()),
                "submission_mean_delta": float(sub_delta.mean()),
                "submission_abs_delta_mean": float(np.abs(sub_delta).mean()),
                "submission_abs_delta_p90": float(np.quantile(np.abs(sub_delta), 0.90)),
                "submission_abs_delta_max": float(np.abs(sub_delta).max()),
                "submission_delta_p10": float(np.quantile(sub_delta, 0.10)),
                "submission_delta_p50": float(np.quantile(sub_delta, 0.50)),
                "submission_delta_p90": float(np.quantile(sub_delta, 0.90)),
            }
        )
        oof_rows.append(
            {
                "target": target,
                "oof_base_loss": b1.loss_col(y[:, j], base_oof[:, j]),
                "oof_candidate_loss": b1.loss_col(y[:, j], cand_oof[:, j]),
                "oof_loss_delta": b1.loss_col(y[:, j], cand_oof[:, j]) - b1.loss_col(y[:, j], base_oof[:, j]),
                "oof_base_mean": float(base_oof[:, j].mean()),
                "oof_candidate_mean": float(cand_oof[:, j].mean()),
                "oof_mean_delta": float(oof_delta.mean()),
                "oof_abs_delta_mean": float(np.abs(oof_delta).mean()),
                "oof_abs_delta_p90": float(np.quantile(np.abs(oof_delta), 0.90)),
                "oof_abs_delta_max": float(np.abs(oof_delta).max()),
            }
        )
    return pd.DataFrame(sub_rows), pd.DataFrame(oof_rows)


def main() -> None:
    train_raw, _sub_raw, train_feat, sub_feat = b1.build_frames()
    shift = feature_shift_audit(train_feat, sub_feat)
    shift.to_csv(OUT / "broad_stage2_feature_shift_audit.csv", index=False)
    sub_delta, oof_delta = probability_delta_audit(train_raw)
    sub_delta.to_csv(OUT / "broad_stage2_submission_probability_delta_audit.csv", index=False)
    oof_delta.to_csv(OUT / "broad_stage2_oof_probability_delta_audit.csv", index=False)

    display_cols = [
        "target",
        "feature",
        "mode",
        "raw_mean_shift_z",
        "raw_std_ratio",
        "raw_sub_outside_train_range_rate",
        "mode_mean_shift_z",
        "mode_std_ratio",
        "mode_sub_outside_train_range_rate",
    ]
    print("\nfeature shift")
    print(shift[display_cols].round(6).to_string(index=False))
    print("\nsubmission probability deltas")
    print(sub_delta.round(6).to_string(index=False))
    print("\noof probability/loss deltas")
    print(oof_delta.round(6).to_string(index=False))


if __name__ == "__main__":
    main()
