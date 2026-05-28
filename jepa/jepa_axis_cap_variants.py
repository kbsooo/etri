from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "jepa"
ANALYSIS = ROOT / "analysis_outputs"
DATA = ROOT / "data"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "lifelog_date"]
SUB_KEY = ["subject_id", "sleep_date", "lifelog_date"]


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


def projection_ratio(move: np.ndarray, axis: np.ndarray) -> float:
    a = axis.reshape(-1)
    m = move.reshape(-1)
    return float(np.dot(m, a) / max(np.dot(a, a), 1e-12))


def cap_move(move: np.ndarray, bad_axis: np.ndarray, cap: float, scale: float) -> tuple[np.ndarray, float]:
    ratio = projection_ratio(move, bad_axis)
    adjusted = move.copy()
    if ratio > cap:
        adjusted = adjusted - (ratio - cap) * bad_axis
    return scale * adjusted, ratio


def read_sub(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)


def main() -> None:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    y = train[TARGETS].to_numpy(dtype=int)
    base_oof = clip(np.load(ANALYSIS / "final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy"))
    jepa_oof = clip(np.load(OUT / "jepa_selected_oof.npy"))
    ordinal_oof = clip(np.load(ANALYSIS / "final_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75_oof.npy"))

    base_sub = read_sub(ANALYSIS / "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv")
    jepa_sub = read_sub(OUT / "submission_jepa_selected.csv")
    ordinal_sub = read_sub(ANALYSIS / "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv")
    sample = read_sub(DATA / "ch2026_submission_sample.csv")
    assert base_sub[SUB_KEY].equals(sample[SUB_KEY])
    assert jepa_sub[SUB_KEY].equals(sample[SUB_KEY])
    assert ordinal_sub[SUB_KEY].equals(sample[SUB_KEY])

    base_logit_oof = logit(base_oof)
    move_oof = logit(jepa_oof) - base_logit_oof
    bad_oof = logit(ordinal_oof) - base_logit_oof
    base_logit_sub = logit(base_sub[TARGETS].to_numpy(dtype=float))
    move_sub = logit(jepa_sub[TARGETS].to_numpy(dtype=float)) - base_logit_sub
    bad_sub = logit(ordinal_sub[TARGETS].to_numpy(dtype=float)) - base_logit_sub

    rows = []
    for cap in [-0.05, 0.0, 0.05, 0.10]:
        for scale in [0.25, 0.50, 0.75, 1.00]:
            adj_oof, raw_ratio_oof = cap_move(move_oof, bad_oof, cap=cap, scale=scale)
            pred_oof = clip(sigmoid(base_logit_oof + adj_oof))
            adj_sub, raw_ratio_sub = cap_move(move_sub, bad_sub, cap=cap, scale=scale)
            pred_sub = clip(sigmoid(base_logit_sub + adj_sub))
            sub_ratio_after = projection_ratio(logit(pred_sub) - base_logit_sub, bad_sub)
            oof_ratio_after = projection_ratio(logit(pred_oof) - base_logit_oof, bad_oof)
            name = f"submission_jepa_axiscap_cap{str(cap).replace('-', 'm').replace('.', 'p')}_scale{str(scale).replace('.', 'p')}.csv"
            out = base_sub.copy()
            out[TARGETS] = pred_sub
            out.to_csv(OUT / name, index=False)
            rows.append(
                {
                    "file": name,
                    "cap": cap,
                    "scale": scale,
                    "oof_loss": mean_loss(y, pred_oof),
                    "oof_delta_vs_stage2": mean_loss(y, pred_oof) - mean_loss(y, base_oof),
                    "raw_oof_bad_axis_ratio": raw_ratio_oof,
                    "oof_bad_axis_ratio_after": oof_ratio_after,
                    "raw_submission_bad_axis_ratio": raw_ratio_sub,
                    "submission_bad_axis_ratio_after": sub_ratio_after,
                    "submission_mean_abs_delta": float(np.mean(np.abs(pred_sub - base_sub[TARGETS].to_numpy(dtype=float)))),
                }
            )
    summary = pd.DataFrame(rows).sort_values(["cap", "scale"])
    summary.to_csv(OUT / "jepa_axiscap_summary.csv", index=False)
    print(summary.round(9).to_string(index=False))


if __name__ == "__main__":
    main()
