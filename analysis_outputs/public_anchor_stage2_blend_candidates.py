from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "sleep_date", "lifelog_date"]


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1.0 - 1e-5)


def logit(p: np.ndarray) -> np.ndarray:
    pp = clip(p)
    return np.log(pp / (1.0 - pp))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    pp = clip(p)
    yy = y.astype(float)
    return float(-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp)).mean())


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([loss_col(y[:, j], pred[:, j]) for j in range(len(TARGETS))]))


def read_submission(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)


def main() -> None:
    anchor_file = OUT / "submission_hybrid_0p578_logit_after_subject_final9_strict.csv"
    stage2_file = OUT / "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv"
    anchor = read_submission(anchor_file)
    stage2 = read_submission(stage2_file)
    assert anchor[KEY].equals(stage2[KEY])

    train = pd.read_csv(ROOT / "data" / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(
        ["subject_id", "lifelog_date"]
    )
    y = train[TARGETS].to_numpy(dtype=int)
    anchor_oof = clip(np.load(OUT / "final_hybrid_0p578_logit_after_subject_final9_strict_oof.npy"))
    stage2_oof = clip(np.load(OUT / "final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy"))

    rows = []
    weights = [0.10, 0.20, 0.35, 0.50, 0.65, 0.75, 0.85, 1.00]
    for mode in ["prob", "logit"]:
        for w in weights:
            if mode == "prob":
                sub_pred = (1.0 - w) * anchor[TARGETS].to_numpy(dtype=float) + w * stage2[TARGETS].to_numpy(dtype=float)
                oof_pred = (1.0 - w) * anchor_oof + w * stage2_oof
            else:
                sub_pred = sigmoid((1.0 - w) * logit(anchor[TARGETS].to_numpy(dtype=float)) + w * logit(stage2[TARGETS].to_numpy(dtype=float)))
                oof_pred = sigmoid((1.0 - w) * logit(anchor_oof) + w * logit(stage2_oof))
            sub_pred = clip(sub_pred)
            oof_pred = clip(oof_pred)
            out = anchor.copy()
            out[TARGETS] = sub_pred
            pct = int(round(w * 100))
            file_name = f"submission_publicblend_anchor578_stage2567_{mode}_w{pct:03d}.csv"
            out.to_csv(OUT / file_name, index=False)
            row = {
                "file": file_name,
                "mode": mode,
                "stage2_weight": float(w),
                "oof_mean_loss": mean_loss(y, oof_pred),
                "submission_min": float(sub_pred.min()),
                "submission_max": float(sub_pred.max()),
                "distance_abs_mean_vs_anchor": float(np.abs(sub_pred - anchor[TARGETS].to_numpy(dtype=float)).mean()),
                "distance_abs_p90_vs_anchor": float(np.quantile(np.abs(sub_pred - anchor[TARGETS].to_numpy(dtype=float)), 0.90)),
                "distance_abs_mean_vs_stage2": float(np.abs(sub_pred - stage2[TARGETS].to_numpy(dtype=float)).mean()),
            }
            for j, target in enumerate(TARGETS):
                row[f"{target}_oof_loss"] = loss_col(y[:, j], oof_pred[:, j])
                row[f"{target}_mean"] = float(sub_pred[:, j].mean())
            rows.append(row)
    summary = pd.DataFrame(rows).sort_values(["mode", "stage2_weight"])
    summary.to_csv(OUT / "public_anchor_stage2_blend_candidates.csv", index=False)
    print(summary.round(8).to_string(index=False))


if __name__ == "__main__":
    main()
