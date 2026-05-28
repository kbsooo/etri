from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

import current_0p586_gentle_logit_calibration as glc
import current_0p588_subject_relative_q_postprocess as srq
import current_0p591_block_label_postprocess as blp
import deep_dive_analysis as d
import geometry_mask_cv_experiments as geom


OUT = Path(__file__).resolve().parent
DATA = OUT.parents[0] / "data"
TARGETS = d.TARGETS
KEY = d.KEY


def transform(rows: pd.DataFrame, p: np.ndarray, kind: str, config: str) -> np.ndarray:
    if kind == "subject":
        return srq.subject_relative(rows, p, srq.parse_config(config))
    if kind == "logit":
        return glc.calibrate(p, glc.parse_config(config))
    raise ValueError(kind)


def apply_ops(rows: pd.DataFrame, current: np.ndarray, ops: pd.DataFrame) -> np.ndarray:
    out = current.copy()
    for op in ops.itertuples(index=False):
        target = str(op.target)
        kind = str(op.kind)
        config = str(op.config)
        j = TARGETS.index(target)
        out[:, j] = transform(rows, out[:, j], kind, config)
    return out


def estimate(train: pd.DataFrame, base: np.ndarray, candidate: np.ndarray, ops: pd.DataFrame, out_path: Path) -> pd.DataFrame:
    y = train[TARGETS].to_numpy(dtype=int)
    rows = []
    touched = set(str(op.target) for op in ops.itertuples(index=False))
    last_source = {
        str(op.target): f"{op.kind}_{op.config}"
        for op in ops.itertuples(index=False)
    }
    for j, target in enumerate(TARGETS):
        current_loss = srq.loss_col(y[:, j], base[:, j])
        candidate_loss = srq.loss_col(y[:, j], candidate[:, j])
        rows.append(
            {
                "target": target,
                "current_loss": current_loss,
                "candidate_loss": candidate_loss,
                "delta_vs_current": candidate_loss - current_loss,
                "source": last_source[target] if target in touched else "unchanged",
            }
        )
    df = pd.DataFrame(rows)
    df.loc[len(df)] = {
        "target": "mean",
        "current_loss": float(df["current_loss"].mean()),
        "candidate_loss": float(df["candidate_loss"].mean()),
        "delta_vs_current": float(df["candidate_loss"].mean() - df["current_loss"].mean()),
        "source": "target_mean",
    }
    df.to_csv(out_path, index=False)
    return df


def make_submission(base_sub: Path, ops: pd.DataFrame, sub_out: Path) -> pd.DataFrame:
    sub = blp.sub_frame()
    out = pd.read_csv(base_sub, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    assert out[KEY].equals(sub[KEY])
    out[TARGETS] = apply_ops(sub, out[TARGETS].to_numpy(dtype=float), ops)
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    assert list(out.columns) == list(sample.columns)
    assert out[KEY].equals(sample[KEY])
    assert out[TARGETS].isna().sum().sum() == 0
    assert out.duplicated(KEY).sum() == 0
    assert ((out[TARGETS] >= 0).all().all() and (out[TARGETS] <= 1).all().all())
    out.to_csv(sub_out, index=False)
    return out


def geometry_check(train: pd.DataFrame, sub: pd.DataFrame, base: np.ndarray, ops: pd.DataFrame, out_path: Path) -> pd.DataFrame:
    folds = geom.geometry_folds(train[KEY + ["sleep_date"] + TARGETS], sub[KEY + ["sleep_date"]], n_repeats=10)
    y_all = train[TARGETS].to_numpy(dtype=int)
    rows = []
    for _, val_idx, fold in folds:
        val = train.iloc[val_idx].reset_index(drop=True)
        y = y_all[val_idx]
        b = base[val_idx].copy()
        c = apply_ops(val, b, ops)
        row = {
            "fold": fold,
            "base_mean": float(np.mean([srq.loss_col(y[:, j], b[:, j]) for j in range(len(TARGETS))])),
            "candidate_mean": float(np.mean([srq.loss_col(y[:, j], c[:, j]) for j in range(len(TARGETS))])),
        }
        row["delta_mean"] = row["candidate_mean"] - row["base_mean"]
        for j, target in enumerate(TARGETS):
            row[f"{target}_delta"] = srq.loss_col(y[:, j], c[:, j]) - srq.loss_col(y[:, j], b[:, j])
        rows.append(row)
    df = pd.DataFrame(rows)
    summary = {
        "fold": "summary",
        "base_mean": float(df["base_mean"].mean()),
        "candidate_mean": float(df["candidate_mean"].mean()),
        "delta_mean": float(df["delta_mean"].mean()),
    }
    for target in TARGETS:
        summary[f"{target}_delta"] = float(df[f"{target}_delta"].mean())
    df = pd.concat([df, pd.DataFrame([summary])], ignore_index=True)
    df.to_csv(out_path, index=False)
    return df


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-sub", required=True)
    parser.add_argument("--base-oof", required=True)
    parser.add_argument("--ops", required=True)
    parser.add_argument("--sub-out", required=True)
    parser.add_argument("--oof-out", required=True)
    parser.add_argument("--est-out", required=True)
    parser.add_argument("--geometry-out", required=True)
    args = parser.parse_args()

    train = blp.train_frame()
    sub = blp.sub_frame()
    ops = pd.read_csv(args.ops)
    base = np.load(args.base_oof)
    candidate = apply_ops(train, base, ops)
    np.save(args.oof_out, candidate)
    estimate_df = estimate(train, base, candidate, ops, Path(args.est_out))
    out = make_submission(Path(args.base_sub), ops, Path(args.sub_out))
    geometry = geometry_check(train, sub, base, ops, Path(args.geometry_out))
    print("ops")
    print(ops.to_string(index=False))
    print(estimate_df.round(9).to_string(index=False))
    print("geometry")
    print(geometry.tail(1).round(9).to_string(index=False))
    print("wrote", args.sub_out)
    print("range", float(out[TARGETS].min().min()), float(out[TARGETS].max().max()))


if __name__ == "__main__":
    main()
