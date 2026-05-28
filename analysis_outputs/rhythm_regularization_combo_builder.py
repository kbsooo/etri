from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

import broad_feature_addon_builder as bfab
import rhythm_regularization_scan as rscan


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


Q3_HR_STRICT = op(
    "Q3",
    "rhythm__rr_hr_pre6h_hr_points_count_same_weekend_dev",
    "subject_z",
    0.50,
    0.45,
)
Q3_HR_MED = op(
    "Q3",
    "rhythm__rr_hr_pre6h_hr_points_count_same_weekend_dev",
    "subject_z",
    0.20,
    0.45,
)
Q3_HR_SOFT = op(
    "Q3",
    "rhythm__rr_hr_pre6h_hr_points_count_same_weekend_dev",
    "subject_z",
    0.20,
    0.30,
)
S1_LIGHT_STRICT = op(
    "S1",
    "rhythm__rr_mlight_core5h_m_light_min_dev_subj_med",
    "subject_z",
    0.50,
    0.45,
)
S1_LIGHT_MED = op(
    "S1",
    "rhythm__rr_mlight_core5h_m_light_min_dev_subj_med",
    "subject_z",
    0.20,
    0.45,
)
S1_LIGHT_SOFT = op(
    "S1",
    "rhythm__rr_mlight_core5h_m_light_min_dev_subj_med",
    "subject_z",
    0.20,
    0.30,
)
S4_LIGHT_STRICT = op(
    "S4",
    "rhythm__rr_mlight_pre3h_m_light_sum_same_weekend_dev",
    "subject_center",
    0.50,
    0.45,
)
S4_LIGHT_MED = op(
    "S4",
    "rhythm__rr_mlight_pre3h_m_light_sum_same_weekend_dev",
    "subject_center",
    0.20,
    0.45,
)
S4_LIGHT_SOFT = op(
    "S4",
    "rhythm__rr_mlight_pre3h_m_light_sum_same_weekend_dev",
    "subject_center",
    0.20,
    0.30,
)
Q1_CHARGE_STRICT = op(
    "Q1",
    "rhythm__rr_charge_core5h_m_charging_min_zdev_subj_mean",
    "subject_z",
    0.50,
    0.45,
)
Q1_CHARGE_MED = op(
    "Q1",
    "rhythm__rr_charge_core5h_m_charging_min_zdev_subj_mean",
    "subject_z",
    0.20,
    0.45,
)
Q1_CHARGE_SOFT = op(
    "Q1",
    "rhythm__rr_charge_core5h_m_charging_min_zdev_subj_mean",
    "subject_z",
    0.20,
    0.30,
)
S2_CHARGE_STRICT = op(
    "S2",
    "rhythm__rr_charge_pre3h_m_charging_mean_prev1_delta",
    "subject_z",
    0.50,
    0.45,
)
S2_CHARGE_MED = op(
    "S2",
    "rhythm__rr_charge_pre3h_m_charging_mean_prev1_delta",
    "subject_z",
    0.20,
    0.45,
)
S2_CHARGE_SOFT = op(
    "S2",
    "rhythm__rr_charge_pre3h_m_charging_mean_prev1_delta",
    "subject_z",
    0.20,
    0.30,
)
S3_LIGHT_STRICT = op(
    "S3",
    "rhythm__rr_mlight_pre3h_m_light_max_next3_delta",
    "subject_z",
    0.50,
    0.45,
)
S3_LIGHT_MED = op(
    "S3",
    "rhythm__rr_mlight_pre3h_m_light_max_next3_delta",
    "subject_z",
    0.20,
    0.45,
)
S3_LIGHT_SOFT = op(
    "S3",
    "rhythm__rr_mlight_pre3h_m_light_max_next3_delta",
    "subject_z",
    0.20,
    0.30,
)


def combo_defs(tag: str) -> dict[str, list[bfab.FeatureOp]]:
    return {
        f"{tag}_q3_hr_irregular": [Q3_HR_STRICT],
        f"{tag}_s1_light_min": [S1_LIGHT_STRICT],
        f"{tag}_s4_light_sum": [S4_LIGHT_STRICT],
        f"{tag}_q3_s1": [Q3_HR_MED, S1_LIGHT_MED],
        f"{tag}_q3_s1_s4": [Q3_HR_MED, S1_LIGHT_MED, S4_LIGHT_MED],
        f"{tag}_q3_s1_s4_strict": [Q3_HR_STRICT, S1_LIGHT_STRICT, S4_LIGHT_STRICT],
        f"{tag}_q3_s1_s4_soft": [Q3_HR_SOFT, S1_LIGHT_SOFT, S4_LIGHT_SOFT],
        f"{tag}_q3_s1_s4_mixed": [Q3_HR_STRICT, S1_LIGHT_MED, S4_LIGHT_MED],
        f"{tag}_q1_s2_s3": [Q1_CHARGE_MED, S2_CHARGE_MED, S3_LIGHT_MED],
        f"{tag}_q1_s2_s3_soft": [Q1_CHARGE_SOFT, S2_CHARGE_SOFT, S3_LIGHT_SOFT],
        f"{tag}_nonq2": [Q1_CHARGE_MED, Q3_HR_MED, S1_LIGHT_MED, S2_CHARGE_MED, S3_LIGHT_MED, S4_LIGHT_MED],
        f"{tag}_nonq2_soft": [Q1_CHARGE_SOFT, Q3_HR_SOFT, S1_LIGHT_SOFT, S2_CHARGE_SOFT, S3_LIGHT_SOFT, S4_LIGHT_SOFT],
        f"{tag}_nonq2_strict": [
            Q1_CHARGE_STRICT,
            Q3_HR_STRICT,
            S1_LIGHT_STRICT,
            S2_CHARGE_STRICT,
            S3_LIGHT_STRICT,
            S4_LIGHT_STRICT,
        ],
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


def probability_delta_audit(prefix: str, base_submission: Path, candidate_path: Path) -> dict[str, float]:
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
    parser.add_argument("--tag", default="rhythm_stage2")
    args = parser.parse_args()

    base_oof_path = args.base_oof
    base_submission = args.base_submission
    train_raw, sub_raw, train_feat, sub_feat = rscan.build_frames()
    base = clip(np.load(base_oof_path))
    y = train_raw[TARGETS].to_numpy(dtype=int)
    base_loss = mean_loss(y, base)

    rows = []
    target_rows = []
    saved_rows = []
    preds: dict[str, np.ndarray] = {}
    combos = combo_defs(args.tag)
    for name, ops in combos.items():
        pred = apply_combo_oof(train_feat, base, ops)
        preds[name] = pred
        geom = bfab.geometry_summary(train_raw, sub_raw, train_feat, base, ops)
        row = {
            "combo": name,
            "ops": "; ".join(f"{x.target}:{x.feature}|{x.mode}|c{x.c_value}|w{x.weight}" for x in ops),
            "base_loss": base_loss,
            "candidate_loss": mean_loss(y, pred),
            "delta": mean_loss(y, pred) - base_loss,
        }
        row.update(geom)
        row["passes_geometry"] = bool(row["geometry_delta"] < 0.0)
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
    targets = pd.DataFrame(target_rows)
    summary.to_csv(OUT / f"{args.tag}_combo_summary.csv", index=False)
    targets.to_csv(OUT / f"{args.tag}_combo_targets.csv", index=False)

    for row in summary.itertuples(index=False):
        if not bool(row.passes_geometry):
            continue
        name = str(row.combo)
        np.save(OUT / f"final_{name}_oof.npy", preds[name])
        path = save_submission(name, train_feat, sub_feat, base, base_submission, combos[name])
        audit = probability_delta_audit(name, base_submission, path)
        saved_rows.append({"combo": name, "submission": path.name, **audit})
    pd.DataFrame(saved_rows).to_csv(OUT / f"{args.tag}_combo_submission_audit.csv", index=False)

    print(summary.round(9).to_string(index=False))
    print(targets.sort_values(["combo", "target"]).round(9).to_string(index=False))
    if saved_rows:
        print(pd.DataFrame(saved_rows).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
