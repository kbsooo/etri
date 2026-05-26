from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

import current_0p586_gentle_logit_calibration as glc
import current_0p588_subject_relative_q_postprocess as srq
import geometry_mask_cv_experiments as geom
import quiet_feature_logit_postprocess_probe as qlp


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "lifelog_date"]


@dataclass(frozen=True)
class QuietOp:
    target: str
    feature: str
    c_value: float
    weight: float


@dataclass(frozen=True)
class PostOp:
    kind: str
    target: str
    config: str


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1.0 - 1e-5)


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    yy = y.astype(float)
    pp = clip(p)
    return float(-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp)).mean())


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([loss_col(y[:, j], pred[:, j]) for j in range(len(TARGETS))]))


def load_frames() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train_raw = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    sub_raw = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    quiet = pd.read_parquet(OUT / "quiet_window_residual_features.parquet")
    train_feat = train_raw.merge(quiet, on=KEY, how="left")
    sub_feat = sub_raw.merge(quiet, on=KEY, how="left")
    return train_raw, sub_raw, train_feat, sub_feat


def apply_quiet_oof(train_feat: pd.DataFrame, pred: np.ndarray, op: QuietOp) -> np.ndarray:
    out = pred.copy()
    j = TARGETS.index(op.target)
    corrected = qlp.oof_corrected(train_feat, out, op.target, op.feature, op.c_value)
    out[:, j] = clip((1.0 - op.weight) * out[:, j] + op.weight * corrected)
    return out


def apply_quiet_fit_predict(ref: pd.DataFrame, rows: pd.DataFrame, ref_pred: np.ndarray, row_pred: np.ndarray, op: QuietOp) -> np.ndarray:
    out = row_pred.copy()
    j = TARGETS.index(op.target)
    corrected = qlp.fit_corrected(ref, rows, ref_pred, row_pred, op.target, op.feature, op.c_value)
    out[:, j] = clip((1.0 - op.weight) * out[:, j] + op.weight * corrected)
    return out


def apply_post(rows: pd.DataFrame, pred: np.ndarray, op: PostOp) -> np.ndarray:
    out = pred.copy()
    j = TARGETS.index(op.target)
    if op.kind == "subject":
        out[:, j] = srq.subject_relative(rows, out[:, j], srq.parse_config(op.config))
    elif op.kind == "logit":
        out[:, j] = glc.calibrate(out[:, j], glc.parse_config(op.config))
    else:
        raise ValueError(op.kind)
    return clip(out)


def apply_combo_oof(train_feat: pd.DataFrame, train_raw: pd.DataFrame, base: np.ndarray, quiet_ops: list[QuietOp], post_ops: list[PostOp]) -> np.ndarray:
    out = base.copy()
    for op in quiet_ops:
        out = apply_quiet_oof(train_feat, out, op)
    for op in post_ops:
        out = apply_post(train_raw, out, op)
    return clip(out)


def apply_combo_submission(
    train_feat: pd.DataFrame,
    sub_feat: pd.DataFrame,
    sub_raw: pd.DataFrame,
    base_oof: np.ndarray,
    base_sub: np.ndarray,
    quiet_ops: list[QuietOp],
    post_ops: list[PostOp],
) -> np.ndarray:
    out = base_sub.copy()
    ref = base_oof.copy()
    for op in quiet_ops:
        out = apply_quiet_fit_predict(train_feat, sub_feat, ref, out, op)
        # Keep the reference prediction in the same representation for any later
        # same-target operation; this is full-fit and only used for test-time fitting.
        ref = apply_quiet_fit_predict(train_feat, train_feat, ref, ref, op)
    for op in post_ops:
        out = apply_post(sub_raw, out, op)
    return clip(out)


def geometry_summary(
    train_raw: pd.DataFrame,
    sub_raw: pd.DataFrame,
    train_feat: pd.DataFrame,
    base: np.ndarray,
    quiet_ops: list[QuietOp],
    post_ops: list[PostOp],
) -> dict[str, float]:
    y_all = train_raw[TARGETS].to_numpy(dtype=int)
    rows = []
    for tr_idx, val_idx, fold in geom.geometry_folds(train_raw, sub_raw, n_repeats=10):
        ref_feat = train_feat.iloc[tr_idx].reset_index(drop=True)
        val_feat = train_feat.iloc[val_idx].reset_index(drop=True)
        val_raw = train_raw.iloc[val_idx].reset_index(drop=True)
        ref_pred = base[tr_idx].copy()
        val_pred = base[val_idx].copy()
        for op in quiet_ops:
            val_pred = apply_quiet_fit_predict(ref_feat, val_feat, ref_pred, val_pred, op)
            ref_pred = apply_quiet_fit_predict(ref_feat, ref_feat, ref_pred, ref_pred, op)
        for op in post_ops:
            val_pred = apply_post(val_raw, val_pred, op)
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


def combo_defs() -> dict[str, tuple[list[QuietOp], list[PostOp]]]:
    quiet_s3 = QuietOp("S3", "quiet_w21_32_screen_step_activity_end", 0.50, 0.45)
    subj_q3 = PostOp("subject", "Q3", "rank_logit_p0.75_w0.3")
    subj_s4 = PostOp("subject", "S4", "rank_logit_p0.75_w0.3")
    subj_s1 = PostOp("subject", "S1", "center_shift_p-0.5_w0.1")
    logit_s1 = PostOp("logit", "S1", "scale1.15_shift-0.08_w0.2")
    return {
        "quiet_s3": ([quiet_s3], []),
        "subject_q3_s4": ([], [subj_q3, subj_s4]),
        "quiet_s3_subject_q3_s4": ([quiet_s3], [subj_q3, subj_s4]),
        "quiet_s3_subject_q3_s4_s1": ([quiet_s3], [subj_q3, subj_s4, subj_s1]),
        "quiet_s3_subject_q3_s4_s1_logit_s1": ([quiet_s3], [subj_q3, subj_s4, subj_s1, logit_s1]),
    }


def save_submission(prefix: str, train_feat: pd.DataFrame, sub_feat: pd.DataFrame, train_raw: pd.DataFrame, sub_raw: pd.DataFrame, base_oof: np.ndarray, quiet_ops: list[QuietOp], post_ops: list[PostOp]) -> None:
    base_sub_file = OUT / "submission_hybrid_0p574_quiet_logit_then_second_loose.csv"
    out = pd.read_csv(base_sub_file, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    assert out[["subject_id", "sleep_date", "lifelog_date"]].equals(sample[["subject_id", "sleep_date", "lifelog_date"]])
    pred = apply_combo_submission(train_feat, sub_feat, sub_raw, base_oof, out[TARGETS].to_numpy(dtype=float), quiet_ops, post_ops)
    out[TARGETS] = pred
    assert out[TARGETS].isna().sum().sum() == 0
    assert out.duplicated(["subject_id", "sleep_date", "lifelog_date"]).sum() == 0
    out.to_csv(OUT / f"submission_{prefix}.csv", index=False)


def main() -> None:
    train_raw, sub_raw, train_feat, sub_feat = load_frames()
    y = train_raw[TARGETS].to_numpy(dtype=int)
    base = clip(np.load(OUT / "final_hybrid_0p575_quiet_logit_then_second_loose_foldsafe_oof.npy"))
    base_loss = mean_loss(y, base)
    rows = []
    target_rows = []
    preds: dict[str, np.ndarray] = {}
    for name, (quiet_ops, post_ops) in combo_defs().items():
        pred = apply_combo_oof(train_feat, train_raw, base, quiet_ops, post_ops)
        preds[name] = pred
        summary = {
            "combo": name,
            "base_loss": base_loss,
            "candidate_loss": mean_loss(y, pred),
            "delta": mean_loss(y, pred) - base_loss,
        }
        summary.update(geometry_summary(train_raw, sub_raw, train_feat, base, quiet_ops, post_ops))
        rows.append(summary)
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
    summary_df = pd.DataFrame(rows).sort_values(["candidate_loss", "geometry_delta"])
    target_df = pd.DataFrame(target_rows)
    summary_df.to_csv(OUT / "post_foldsafe_addon_combo_summary.csv", index=False)
    target_df.to_csv(OUT / "post_foldsafe_addon_combo_targets.csv", index=False)
    for row in summary_df.itertuples(index=False):
        if float(row.geometry_delta) <= 0.0:
            name = str(row.combo)
            quiet_ops, post_ops = combo_defs()[name]
            prefix = f"hybrid_0p575_foldsafe_{name}"
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
            save_submission(prefix, train_feat, sub_feat, train_raw, sub_raw, base, quiet_ops, post_ops)
    print(summary_df.round(9).to_string(index=False))
    print(target_df.sort_values(["combo", "target"]).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
