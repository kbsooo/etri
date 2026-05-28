from __future__ import annotations

import argparse
import itertools
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))
import geometry_mask_cv_experiments as geom  # noqa: E402
import q23_sequence_bridge_experiments as q23  # noqa: E402
import quiet_feature_logit_postprocess_probe as qlp  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "sleep_date", "lifelog_date"]
SORT_KEY = ["subject_id", "lifelog_date"]


@dataclass(frozen=True)
class TargetOp:
    target: str
    cfg: q23.BridgeConfig

    @property
    def name(self) -> str:
        return f"{self.target}__{self.cfg.name}"


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1.0 - 1e-5)


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    yy = y.astype(float)
    pp = clip(p)
    return float(-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp)).mean())


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([loss_col(y[:, j], pred[:, j]) for j in range(len(TARGETS))]))


def config_grid() -> list[q23.BridgeConfig]:
    # Deliberately smaller than the original Q2/Q3 grid. These are weak residual
    # bridges around the family that was at least plausible in the older q23 scan.
    return [
        q23.BridgeConfig(alpha, global_weight, stay_boost, prior_shrink, bridge_weight)
        for alpha, global_weight, stay_boost, prior_shrink, bridge_weight in itertools.product(
            [0.2, 0.5, 1.0, 2.0],
            [0.5, 1.5, 4.0],
            [1.0, 1.5],
            [16.0, 32.0],
            [0.03, 0.05, 0.08, 0.10, 0.15, 0.20, 0.35],
        )
    ]


def apply_target_op(ref: pd.DataFrame, rows: pd.DataFrame, pred: np.ndarray, op: TargetOp) -> np.ndarray:
    out = pred.copy()
    j = TARGETS.index(op.target)
    out[:, j] = q23.bridge_predict(ref, rows, pred[:, j].copy(), op.target, op.cfg)
    return clip(out)


def fixed_outer(
    train: pd.DataFrame,
    sub: pd.DataFrame,
    base: np.ndarray,
    targets: list[str],
    repeats: int,
    prefix: str,
) -> pd.DataFrame:
    y = train[TARGETS].to_numpy(dtype=int)
    rows = []
    cfgs = config_grid()
    for target in targets:
        j = TARGETS.index(target)
        for cfg_i, cfg in enumerate(cfgs):
            deltas = []
            for tr_idx, val_idx, _fold in geom.geometry_folds(train, sub, n_repeats=repeats):
                ref = train.iloc[tr_idx].reset_index(drop=True)
                val = train.iloc[val_idx].reset_index(drop=True)
                pred_col = q23.bridge_predict(ref, val, base[val_idx, j].copy(), target, cfg)
                deltas.append(loss_col(y[val_idx, j], pred_col) - loss_col(y[val_idx, j], base[val_idx, j]))
            row = {
                "target": target,
                "config": cfg.name,
                "alpha": cfg.alpha,
                "global_weight": cfg.global_weight,
                "stay_boost": cfg.stay_boost,
                "prior_shrink": cfg.prior_shrink,
                "bridge_weight": cfg.bridge_weight,
                "target_delta_mean": float(np.mean(deltas)),
                "target_delta_median": float(np.median(deltas)),
                "target_win_rate": float((np.asarray(deltas) < 0.0).mean()),
                "mean_delta_if_only_target": float(np.mean(deltas) / len(TARGETS)),
            }
            rows.append(row)
        print(f"[fixed bridge] target={target} configs={len(cfgs)}", flush=True)
    out = pd.DataFrame(rows).sort_values(["target_delta_mean", "target_win_rate"], ascending=[True, False])
    out.to_csv(OUT / f"{prefix}_fixed_outer.csv", index=False)
    return out


def oof_op(rows: pd.DataFrame, base: np.ndarray, op: TargetOp) -> np.ndarray:
    out = base.copy()
    j = TARGETS.index(op.target)
    for tr_idx, val_idx in qlp.make_subject_blocks(rows.reset_index(drop=True)):
        ref = rows.iloc[tr_idx].reset_index(drop=True)
        val = rows.iloc[val_idx].reset_index(drop=True)
        out[val_idx, j] = q23.bridge_predict(ref, val, base[val_idx, j].copy(), op.target, op.cfg)
    return clip(out)


def selected_ops(result: pd.DataFrame) -> list[TargetOp]:
    ops: list[TargetOp] = []
    for target, g in result.groupby("target", sort=False):
        top = g.sort_values(["target_delta_mean", "target_win_rate"], ascending=[True, False]).iloc[0]
        if float(top["target_delta_mean"]) < -0.0015 and float(top["target_win_rate"]) >= 0.75:
            cfg = q23.BridgeConfig(
                float(top["alpha"]),
                float(top["global_weight"]),
                float(top["stay_boost"]),
                float(top["prior_shrink"]),
                float(top["bridge_weight"]),
            )
            ops.append(TargetOp(str(target), cfg))
    return ops


def save_candidate(prefix: str, train: pd.DataFrame, base: np.ndarray, base_submission: Path, ops: list[TargetOp]) -> str:
    if not ops:
        return ""
    pred_oof = base.copy()
    for op in ops:
        pred_oof = oof_op(train, pred_oof, op)
    y = train[TARGETS].to_numpy(dtype=int)
    oof_name = "_".join(op.name for op in ops)
    np.save(OUT / f"final_{prefix}_{oof_name}_oof.npy", pred_oof)
    cv_rows = [
        {
            "target": target,
            "base_loss": loss_col(y[:, j], base[:, j]),
            "candidate_loss": loss_col(y[:, j], pred_oof[:, j]),
            "delta": loss_col(y[:, j], pred_oof[:, j]) - loss_col(y[:, j], base[:, j]),
        }
        for j, target in enumerate(TARGETS)
    ]
    cv_rows.append({"target": "mean", "base_loss": mean_loss(y, base), "candidate_loss": mean_loss(y, pred_oof), "delta": mean_loss(y, pred_oof) - mean_loss(y, base)})
    pd.DataFrame(cv_rows).to_csv(OUT / f"{prefix}_{oof_name}_cv_estimate.csv", index=False)

    sub = pd.read_csv(base_submission, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    assert sub[KEY].equals(sample[KEY])
    pred_sub = sub[TARGETS].to_numpy(dtype=float)
    for op in ops:
        pred_sub = apply_target_op(train.reset_index(drop=True), sub.reset_index(drop=True), pred_sub, op)
    out = sub.copy()
    out[TARGETS] = clip(pred_sub)
    assert out[TARGETS].isna().sum().sum() == 0
    assert out.duplicated(KEY).sum() == 0
    file_path = OUT / f"submission_{prefix}_{oof_name}.csv"
    out.to_csv(file_path, index=False)
    pd.DataFrame([{"target": op.target, "config": op.cfg.name} for op in ops]).to_csv(OUT / f"{prefix}_{oof_name}_ops.csv", index=False)
    return str(file_path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-oof", type=Path, required=True)
    parser.add_argument("--base-submission", type=Path, required=True)
    parser.add_argument("--prefix", required=True)
    parser.add_argument("--targets", default="Q1,Q2,Q3,S1,S2,S3,S4")
    parser.add_argument("--outer-repeats", type=int, default=8)
    args = parser.parse_args()

    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(SORT_KEY).reset_index(drop=True)
    sub = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(SORT_KEY).reset_index(drop=True)
    base = clip(np.load(args.base_oof))
    targets = [t for t in args.targets.split(",") if t]
    result = fixed_outer(train, sub, base, targets, args.outer_repeats, args.prefix)
    ops = selected_ops(result)
    submission = save_candidate(args.prefix, train, base, args.base_submission, ops)
    summary = pd.DataFrame(
        [
            {
                "n_selected_ops": len(ops),
                "selected_ops": ";".join(op.name for op in ops),
                "submission": submission,
                "best_target_delta_mean": float(result.iloc[0]["target_delta_mean"]),
                "best_target": str(result.iloc[0]["target"]),
                "best_config": str(result.iloc[0]["config"]),
            }
        ]
    )
    summary.to_csv(OUT / f"{args.prefix}_summary.csv", index=False)
    result.groupby("target", group_keys=False).head(10).to_csv(OUT / f"{args.prefix}_top_by_target.csv", index=False)
    print("\n[summary]")
    print(summary.round(9).to_string(index=False))
    print("\n[top by target]")
    print(result.groupby("target", group_keys=False).head(5).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
