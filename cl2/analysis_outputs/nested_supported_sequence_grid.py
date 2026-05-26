from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

import current_0p588_subject_relative_q_postprocess as srq
import current_0p591_block_label_postprocess as blp
import deep_dive_analysis as d
import geometry_mask_cv_experiments as geom
import make_manual_residual_sequence as manual


OUT = Path(__file__).resolve().parent
TARGETS = d.TARGETS
KEY = d.KEY


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([srq.loss_col(y[:, j], pred[:, j]) for j in range(len(TARGETS))]))


def build_ops(q2: bool, s1_repeats: int, s3_repeats: int) -> pd.DataFrame:
    rows: list[dict[str, str]] = []
    if q2:
        rows.append({"kind": "subject", "target": "Q2", "config": "center_temp_p0.5_w0.3"})
    if s3_repeats > 0:
        rows.append({"kind": "subject", "target": "S3", "config": "center_temp_p0.5_w0.3"})
    if q2:
        rows.append({"kind": "logit", "target": "Q2", "config": "scale1.3_shift0_w0.2"})
    for i in range(max(s1_repeats, max(0, s3_repeats - 1))):
        if i < s1_repeats:
            rows.append({"kind": "logit", "target": "S1", "config": "scale1_shift-0.12_w0.2"})
        if i + 1 < s3_repeats:
            rows.append({"kind": "subject", "target": "S3", "config": "center_temp_p0.5_w0.3"})
    return pd.DataFrame(rows, columns=["kind", "target", "config"])


def run(base_oof: Path, prefix: str, max_s1: int, max_s3: int, n_repeats: int) -> pd.DataFrame:
    train = blp.train_frame()
    sub = blp.sub_frame()
    base = np.load(base_oof)
    y = train[TARGETS].to_numpy(dtype=int)
    base_mean = mean_loss(y, base)
    folds = geom.geometry_folds(
        train[KEY + ["sleep_date"] + TARGETS],
        sub[KEY + ["sleep_date"]],
        n_repeats=n_repeats,
    )
    rows = []
    for q2 in [False, True]:
        for s1_repeats in range(max_s1 + 1):
            for s3_repeats in range(max_s3 + 1):
                if not q2 and s1_repeats == 0 and s3_repeats == 0:
                    continue
                ops = build_ops(q2, s1_repeats, s3_repeats)
                cand = manual.apply_ops(train, base, ops)
                oof_mean = mean_loss(y, cand)
                fold_deltas = []
                fold_means = []
                for _, val_idx, _ in folds:
                    val = train.iloc[val_idx].reset_index(drop=True)
                    yv = y[val_idx]
                    bv = base[val_idx].copy()
                    cv = manual.apply_ops(val, bv, ops)
                    base_val = mean_loss(yv, bv)
                    cand_val = mean_loss(yv, cv)
                    fold_deltas.append(cand_val - base_val)
                    fold_means.append(cand_val)
                rows.append(
                    {
                        "q2": q2,
                        "s1_repeats": s1_repeats,
                        "s3_repeats": s3_repeats,
                        "n_ops": len(ops),
                        "oof_mean": oof_mean,
                        "oof_delta": oof_mean - base_mean,
                        "geometry_mean": float(np.mean(fold_means)),
                        "geometry_delta": float(np.mean(fold_deltas)),
                        "geometry_win_rate": float((np.asarray(fold_deltas) < 0).mean()),
                    }
                )
    result = pd.DataFrame(rows).sort_values(["oof_mean", "geometry_delta"])
    result.to_csv(OUT / f"{prefix}_grid.csv", index=False)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-oof", required=True)
    parser.add_argument("--prefix", required=True)
    parser.add_argument("--max-s1", type=int, default=8)
    parser.add_argument("--max-s3", type=int, default=18)
    parser.add_argument("--n-repeats", type=int, default=10)
    args = parser.parse_args()
    result = run(Path(args.base_oof), args.prefix, args.max_s1, args.max_s3, args.n_repeats)
    print("top by oof")
    print(result.head(20).round(9).to_string(index=False))
    stable = result[(result["geometry_delta"] < -0.0005) & (result["geometry_win_rate"] >= 0.8)].copy()
    print("top stable")
    print(stable.head(20).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
