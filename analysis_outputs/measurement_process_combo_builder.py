from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

import broad_feature_addon_builder as bfab
import measurement_process_scan as mps


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "lifelog_date"]
SUB_KEY = ["subject_id", "sleep_date", "lifelog_date"]


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1.0 - 1e-5)


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    yy = y.astype(float)
    pp = clip(p)
    return float(-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp)).mean())


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([loss_col(y[:, j], pred[:, j]) for j in range(len(TARGETS))]))


def op(target: str, feature: str, mode: str, c: float, w: float) -> bfab.FeatureOp:
    return bfab.FeatureOp(target, feature, mode, c, w)


Q1_USAGE = op("Q1", "mp__mp_usage_core5h_row_count", "subject_rank", 0.50, 0.45)
Q3_HR = op("Q3", "mp__mp_hr_pre6h_obs_frac_same_weekend_dev", "subject_z", 0.50, 0.45)
S1_WATCH_GAP = op("S1", "mp__mp_watch_gap_sum_night18_36_very_irregular_flag", "global_z", 0.50, 0.45)
S2_WLIGHT_GAP = op("S2", "mp__mp_wlight_all24h_longest_gap_min_same_weekend_dev", "subject_rank", 0.50, 0.45)
S3_USAGE_GAP = op("S3", "mp__mp_usage_cand21_34_p90_gap_min", "subject_rank", 0.50, 0.45)
S4_ACTIVE_COUNT = op("S4", "mp__mp_sensor_active_count_pre6h_same_weekend_dev", "subject_center", 0.50, 0.45)

Q1_USAGE_SOFT = op("Q1", "mp__mp_usage_core5h_row_count", "subject_rank", 0.20, 0.30)
Q3_HR_SOFT = op("Q3", "mp__mp_hr_pre6h_obs_frac_same_weekend_dev", "subject_z", 0.20, 0.30)
S1_WATCH_GAP_SOFT = op("S1", "mp__mp_watch_gap_sum_night18_36_very_irregular_flag", "global_z", 0.20, 0.30)
S2_WLIGHT_GAP_SOFT = op("S2", "mp__mp_wlight_all24h_longest_gap_min_same_weekend_dev", "subject_rank", 0.20, 0.30)
S3_USAGE_GAP_SOFT = op("S3", "mp__mp_usage_cand21_34_p90_gap_min", "subject_rank", 0.20, 0.30)
S4_ACTIVE_COUNT_SOFT = op("S4", "mp__mp_sensor_active_count_pre6h_same_weekend_dev", "subject_center", 0.20, 0.30)


def combo_defs(tag: str) -> dict[str, list[bfab.FeatureOp]]:
    return {
        f"{tag}_q3_hr": [Q3_HR],
        f"{tag}_q1_usage": [Q1_USAGE],
        f"{tag}_s2_wlight_gap": [S2_WLIGHT_GAP],
        f"{tag}_s3_usage_gap": [S3_USAGE_GAP],
        f"{tag}_s4_sensor_count": [S4_ACTIVE_COUNT],
        f"{tag}_usage_q1_s3": [Q1_USAGE, S3_USAGE_GAP],
        f"{tag}_watch_s1_s2_q3": [S1_WATCH_GAP, S2_WLIGHT_GAP, Q3_HR],
        f"{tag}_noq2_noq3": [Q1_USAGE, S1_WATCH_GAP, S2_WLIGHT_GAP, S3_USAGE_GAP, S4_ACTIVE_COUNT],
        f"{tag}_noq2_noq3_soft": [Q1_USAGE_SOFT, S1_WATCH_GAP_SOFT, S2_WLIGHT_GAP_SOFT, S3_USAGE_GAP_SOFT, S4_ACTIVE_COUNT_SOFT],
        f"{tag}_nonq2": [Q1_USAGE, Q3_HR, S1_WATCH_GAP, S2_WLIGHT_GAP, S3_USAGE_GAP, S4_ACTIVE_COUNT],
        f"{tag}_nonq2_soft": [Q1_USAGE_SOFT, Q3_HR_SOFT, S1_WATCH_GAP_SOFT, S2_WLIGHT_GAP_SOFT, S3_USAGE_GAP_SOFT, S4_ACTIVE_COUNT_SOFT],
        f"{tag}_q1_s2_s3_s4": [Q1_USAGE, S2_WLIGHT_GAP, S3_USAGE_GAP, S4_ACTIVE_COUNT],
        f"{tag}_q1_s2_s3_s4_soft": [Q1_USAGE_SOFT, S2_WLIGHT_GAP_SOFT, S3_USAGE_GAP_SOFT, S4_ACTIVE_COUNT_SOFT],
    }


def apply_combo_oof(train_feat: pd.DataFrame, base: np.ndarray, ops: list[bfab.FeatureOp]) -> np.ndarray:
    out = base.copy()
    for item in ops:
        out = bfab.apply_op_oof(train_feat, out, item)
    return clip(out)


def save_submission(
    prefix: str,
    train_feat: pd.DataFrame,
    sub_feat: pd.DataFrame,
    base_oof: np.ndarray,
    base_submission: Path,
    ops: list[bfab.FeatureOp],
) -> Path:
    out = pd.read_csv(base_submission, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    assert out[SUB_KEY].equals(sample[SUB_KEY])
    pred = out[TARGETS].to_numpy(dtype=float)
    ref = base_oof.copy()
    for item in ops:
        pred = bfab.apply_op_fit_predict(train_feat, sub_feat, ref, pred, item)
        ref = bfab.apply_op_fit_predict(train_feat, train_feat, ref, ref, item)
    out[TARGETS] = clip(pred)
    assert out[TARGETS].isna().sum().sum() == 0
    assert out.duplicated(SUB_KEY).sum() == 0
    path = OUT / f"submission_{prefix}.csv"
    out.to_csv(path, index=False)
    return path


def probability_delta_audit(base_submission: Path, candidate_path: Path) -> dict[str, float]:
    base = pd.read_csv(base_submission).sort_values(KEY).reset_index(drop=True)
    cand = pd.read_csv(candidate_path).sort_values(KEY).reset_index(drop=True)
    delta = cand[TARGETS].to_numpy(dtype=float) - base[TARGETS].to_numpy(dtype=float)
    out = {
        "mean_abs_move": float(np.abs(delta).mean()),
        "max_abs_move": float(np.abs(delta).max()),
    }
    for j, target in enumerate(TARGETS):
        out[f"{target}_mean_abs_move"] = float(np.abs(delta[:, j]).mean())
        out[f"{target}_max_abs_move"] = float(np.abs(delta[:, j]).max())
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-oof", type=Path, default=OUT / "final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy")
    parser.add_argument("--base-submission", type=Path, default=OUT / "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv")
    parser.add_argument("--tag", default="mp_stage2")
    args = parser.parse_args()

    train_raw, sub_raw, train_feat, sub_feat = mps.build_frames()
    base = clip(np.load(args.base_oof))
    y = train_raw[TARGETS].to_numpy(dtype=int)
    base_loss = mean_loss(y, base)

    rows = []
    target_rows = []
    audits = []
    combos = combo_defs(args.tag)
    for name, ops in combos.items():
        pred = apply_combo_oof(train_feat, base, ops)
        geom = bfab.geometry_summary(train_raw, sub_raw, train_feat, base, ops)
        row = {
            "combo": name,
            "ops": "; ".join(f"{x.target}:{x.feature}|{x.mode}|c{x.c_value}|w{x.weight}" for x in ops),
            "base_loss": base_loss,
            "candidate_loss": mean_loss(y, pred),
            "delta": mean_loss(y, pred) - base_loss,
        }
        row.update(geom)
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
        np.save(OUT / f"final_{name}_oof.npy", pred)
        path = save_submission(name, train_feat, sub_feat, base, args.base_submission, ops)
        audit = {"combo": name, "submission": path.name}
        audit.update(probability_delta_audit(args.base_submission, path))
        audits.append(audit)

    summary = pd.DataFrame(rows).sort_values(["candidate_loss", "geometry_delta"]).reset_index(drop=True)
    target_df = pd.DataFrame(target_rows)
    audit_df = pd.DataFrame(audits).sort_values("mean_abs_move").reset_index(drop=True)
    summary.to_csv(OUT / f"{args.tag}_combo_summary.csv", index=False)
    target_df.to_csv(OUT / f"{args.tag}_combo_targets.csv", index=False)
    audit_df.to_csv(OUT / f"{args.tag}_combo_submission_audit.csv", index=False)
    print(summary.round(9).to_string(index=False))
    print(target_df.sort_values(["combo", "target"]).round(9).to_string(index=False))
    print(audit_df.round(9).to_string(index=False))


if __name__ == "__main__":
    main()
