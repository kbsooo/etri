from __future__ import annotations

from dataclasses import dataclass
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


@dataclass(frozen=True)
class Combo:
    name: str
    ops: list[b1.FeatureOp]
    note: str


def op(target: str, feature: str, mode: str, c_value: float, weight: float) -> b1.FeatureOp:
    return b1.FeatureOp(target, feature, mode, c_value, weight)


def combo_defs() -> list[Combo]:
    q1 = op("Q1", "presleep__presleep_charge_core5h_m_charging_min", "subject_z", 0.50, 0.45)
    q1_soft = op("Q1", "presleep__presleep_charge_core5h_m_charging_min", "subject_z", 0.20, 0.45)
    s1 = op("S1", "presleep__presleep_mlight_core5h_m_light_min", "subject_z", 0.50, 0.45)
    s1_soft = op("S1", "presleep__presleep_mlight_core5h_m_light_min", "subject_z", 0.20, 0.45)
    s4 = op("S4", "presleep__presleep_mlight_pre3h_m_light_sum", "subject_center", 0.50, 0.45)
    s4_z = op("S4", "presleep__presleep_mlight_pre3h_m_light_sum", "subject_z", 0.50, 0.45)
    q3_hr = op("Q3", "presleep__presleep_hr_pre6h_hr_points_count", "subject_z", 0.50, 0.45)
    q3_ble = op("Q3", "deep__ble_morning_unique_max", "subject_rank", 0.20, 0.30)
    q3_amb_next = op("Q3", "prectx__presleep_ambience_core5h_top_is_speech_count_next1", "subject_z", 0.50, 0.45)
    s2_quiet = op("S2", "quiet__quiet_w22_32_screen_step_end", "subject_z", 0.50, 0.45)
    s2_charge = op("S2", "presleep__presleep_charge_pre3h_m_charging_mean", "subject_rank", 0.50, 0.45)
    s3_activity = op("S3", "presleep__presleep_activity_pre1h_m_activity_last", "subject_center", 0.50, 0.45)
    s2_prectx_charge = op("S2", "prectx__presleep_charge_pre3h_m_charging_mean_dprev1", "subject_z", 0.50, 0.45)
    s2_prectx_wlight = op("S2", "prectx__presleep_wlight_pre1h_w_light_min_dprev1", "global_z", 0.50, 0.45)
    s3_prectx_light = op("S3", "prectx__presleep_mlight_pre3h_m_light_max_future2dev", "subject_z", 0.50, 0.45)

    strong_core = [q1, s1, s4]
    soft_core = [q1_soft, s1_soft, s4_z]
    q3_pair = [q3_hr, q3_ble]
    q3_triple_next = [q3_hr, q3_ble, q3_amb_next]
    return [
        Combo("presleep_core_q1_s1_s4", strong_core, "three strongest non-Q3 presleep residuals"),
        Combo("presleep_core_q1_s1_s4_soft", soft_core, "less aggressive c-values / train-sub safer S4 mode"),
        Combo("presleep_core_q1_s1_s4_q3hr", strong_core + [q3_hr], "core plus Q3 HR sampling signal"),
        Combo("presleep_core_q1_s1_s4_q3hr_ble", strong_core + q3_pair, "core plus sequential Q3 HR and BLE residuals"),
        Combo("presleep_core_soft_q3hr_ble", soft_core + q3_pair, "conservative core plus sequential Q3 residuals"),
        Combo("presleep_core_q1_s1_s4_s2quiet_s3act", strong_core + [s2_quiet, s3_activity], "core plus weaker S2/S3 foldsafe signals"),
        Combo("presleep_core_q1_s1_s4_s2charge_s3act", strong_core + [s2_charge, s3_activity], "core plus presleep-only S2/S3 signals"),
        Combo("presleep_core_all_s2quiet_q3hr_ble", strong_core + [s2_quiet, s3_activity] + q3_pair, "largest OOF candidate with quiet S2"),
        Combo("presleep_core_all_s2charge_q3hr_ble", strong_core + [s2_charge, s3_activity] + q3_pair, "largest presleep-heavy candidate"),
        Combo("presleep_core_prectx_s2charge_s3light", strong_core + [s2_prectx_charge, s3_prectx_light], "core plus temporal-context S2 charge and S3 light"),
        Combo("presleep_core_prectx_s2wlight_s3light", strong_core + [s2_prectx_wlight, s3_prectx_light], "core plus temporal-context S2 watch-light and S3 light"),
        Combo("presleep_core_prectx_s2charge_s3light_q3hr_ble", strong_core + [s2_prectx_charge, s3_prectx_light] + q3_pair, "core plus temporal-context S2/S3 and Q3 HR/BLE"),
        Combo("presleep_core_prectx_s2wlight_s3light_q3hr_ble", strong_core + [s2_prectx_wlight, s3_prectx_light] + q3_pair, "core plus temporal-context S2 watch-light/S3 and Q3 HR/BLE"),
        Combo("presleep_core_prectx_s2charge_s3light_q3hr_ble_ambnext", strong_core + [s2_prectx_charge, s3_prectx_light] + q3_triple_next, "aggressive future-context Q3 ambience-next residual added to temporal S2/S3"),
        Combo("presleep_core_prectx_s2wlight_s3light_q3hr_ble_ambnext", strong_core + [s2_prectx_wlight, s3_prectx_light] + q3_triple_next, "aggressive future-context Q3 ambience-next residual added to temporal S2/S3"),
    ]


def apply_combo_oof(train_feat: pd.DataFrame, base_oof: np.ndarray, ops: list[b1.FeatureOp]) -> np.ndarray:
    pred = base_oof.copy()
    for feature_op in ops:
        pred = b1.apply_op_oof(train_feat, pred, feature_op)
    return clip(pred)


def apply_combo_submission(
    train_feat: pd.DataFrame,
    sub_feat: pd.DataFrame,
    base_oof: np.ndarray,
    base_sub: pd.DataFrame,
    ops: list[b1.FeatureOp],
) -> pd.DataFrame:
    pred = base_sub[TARGETS].to_numpy(dtype=float)
    ref = base_oof.copy()
    for feature_op in ops:
        pred = b1.apply_op_fit_predict(train_feat, sub_feat, ref, pred, feature_op)
        ref = b1.apply_op_fit_predict(train_feat, train_feat, ref, ref, feature_op)
    out = base_sub.copy()
    out[TARGETS] = clip(pred)
    return out


def summarize_targets(y: np.ndarray, base_oof: np.ndarray, pred: np.ndarray, combo_name: str) -> list[dict[str, float | str]]:
    rows: list[dict[str, float | str]] = []
    for j, target in enumerate(TARGETS):
        base_loss = loss_col(y[:, j], base_oof[:, j])
        cand_loss = loss_col(y[:, j], pred[:, j])
        rows.append(
            {
                "combo": combo_name,
                "target": target,
                "base_loss": base_loss,
                "candidate_loss": cand_loss,
                "delta": cand_loss - base_loss,
            }
        )
    rows.append(
        {
            "combo": combo_name,
            "target": "mean",
            "base_loss": mean_loss(y, base_oof),
            "candidate_loss": mean_loss(y, pred),
            "delta": mean_loss(y, pred) - mean_loss(y, base_oof),
        }
    )
    return rows


def main() -> None:
    train_raw, sub_raw, train_feat, sub_feat = b1.build_frames()
    y = train_raw[TARGETS].to_numpy(dtype=int)
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    base_oof = clip(np.load(OUT / "final_publicgated_anchor578_stage2_drop_q3_prob_w650_oof.npy"))
    base_sub = pd.read_csv(
        OUT / "submission_publicgated_anchor578_stage2_drop_q3_prob_w650.csv",
        parse_dates=["sleep_date", "lifelog_date"],
    ).sort_values(KEY).reset_index(drop=True)
    assert base_sub[SUB_KEY].equals(sample[SUB_KEY])

    base_loss = mean_loss(y, base_oof)
    rows = []
    target_rows = []
    saved_rows = []
    for combo in combo_defs():
        pred = apply_combo_oof(train_feat, base_oof, combo.ops)
        row = {
            "combo": combo.name,
            "note": combo.note,
            "ops": "; ".join(f"{x.target}:{x.feature}|{x.mode}|c{x.c_value:g}|w{x.weight:g}" for x in combo.ops),
            "base_loss": base_loss,
            "candidate_loss": mean_loss(y, pred),
            "delta": mean_loss(y, pred) - base_loss,
        }
        row.update(b1.geometry_summary(train_raw, sub_raw, train_feat, base_oof, combo.ops))
        rows.append(row)
        target_rows.extend(summarize_targets(y, base_oof, pred, combo.name))
        if row["delta"] <= -0.002 and row["geometry_delta"] <= 0.0:
            prefix = f"publicgated_q3off650_{combo.name}"
            np.save(OUT / f"final_{prefix}_oof.npy", pred)
            pd.DataFrame(summarize_targets(y, base_oof, pred, combo.name)).to_csv(OUT / f"{prefix}_cv_estimate.csv", index=False)
            out = apply_combo_submission(train_feat, sub_feat, base_oof, base_sub, combo.ops)
            assert out[SUB_KEY].equals(sample[SUB_KEY])
            assert out[TARGETS].isna().sum().sum() == 0
            assert out.duplicated(SUB_KEY).sum() == 0
            out.to_csv(OUT / f"submission_{prefix}.csv", index=False)
            saved_rows.append({"combo": combo.name, "file": f"submission_{prefix}.csv", "oof_file": f"final_{prefix}_oof.npy"})

    summary = pd.DataFrame(rows).sort_values(["candidate_loss", "geometry_delta"]).reset_index(drop=True)
    target_df = pd.DataFrame(target_rows)
    saved_df = pd.DataFrame(saved_rows)
    summary.to_csv(OUT / "presleep_multitarget_candidate_summary.csv", index=False)
    target_df.to_csv(OUT / "presleep_multitarget_candidate_targets.csv", index=False)
    saved_df.to_csv(OUT / "presleep_multitarget_saved_candidates.csv", index=False)
    print(summary.round(9).to_string(index=False))
    print(target_df.sort_values(["combo", "target"]).round(9).to_string(index=False))
    print(saved_df.to_string(index=False))


if __name__ == "__main__":
    main()
