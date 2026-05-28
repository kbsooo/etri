from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss

sys.path.append(str(Path(__file__).resolve().parent))
import calibration_experiments as cal  # noqa: E402
import deep_dive_analysis as d  # noqa: E402
import geometry_mask_cv_experiments as geom  # noqa: E402
import q_rate_shift_postprocess as qrs  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "analysis_outputs"
TARGETS = d.TARGETS
Q_TARGETS = ["Q1", "Q2", "Q3"]
KEY = d.KEY


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1 - 1e-5)


def logloss_col(y: np.ndarray, p: np.ndarray) -> float:
    return float(log_loss(y, clip(p), labels=[0, 1]))


def evaluate_geometry_rate_shift(train: pd.DataFrame, sub: pd.DataFrame) -> pd.DataFrame:
    folds = geom.geometry_folds(train, sub, n_repeats=10)
    y = train[TARGETS].to_numpy(dtype=int)
    saved_oof = np.load(OUT / "final_hybrid_0p598_repro_oof.npy")

    rows = []
    pred_store: dict[tuple[str, str, str], np.ndarray] = {}
    for base_name in ["temporal_base", "saved_oof_proxy"]:
        for target in Q_TARGETS:
            pred_store[(base_name, target, "base")] = np.zeros(len(train), dtype=float)
            for cfg in qrs.configs(target):
                pred_store[(base_name, target, cfg.name)] = np.zeros(len(train), dtype=float)

    covered = np.zeros(len(train), dtype=bool)
    for tr_idx, val_idx, fold_name in folds:
        ref = train.iloc[tr_idx].copy().reset_index(drop=True)
        val = train.iloc[val_idx].copy().reset_index(drop=True)
        temporal = cal.temporal_base(ref, val)
        base_map = {
            "temporal_base": temporal,
            # This is an impure proxy, but it tests whether the postprocess also
            # helps the exact current 0.598 prediction geometry.
            "saved_oof_proxy": saved_oof[val_idx],
        }
        for base_name, base_pred in base_map.items():
            for target in Q_TARGETS:
                j = TARGETS.index(target)
                pred_store[(base_name, target, "base")][val_idx] = base_pred[:, j]
                for cfg in qrs.configs(target):
                    shifted = qrs.apply_fold_shift(ref, val, base_pred[:, j], target, cfg)
                    pred_store[(base_name, target, cfg.name)][val_idx] = shifted
        covered[val_idx] = True
        print(f"[q-rate geometry] {fold_name} val={len(val_idx)}", flush=True)

    for base_name in ["temporal_base", "saved_oof_proxy"]:
        for target in Q_TARGETS:
            j = TARGETS.index(target)
            base_loss = logloss_col(y[covered, j], pred_store[(base_name, target, "base")][covered])
            rows.append(
                {
                    "base": base_name,
                    "target": target,
                    "model": "base",
                    "config": "none",
                    "loss": base_loss,
                    "delta_vs_base": 0.0,
                    "covered_rows": int(covered.sum()),
                }
            )
            for cfg in qrs.configs(target):
                loss = logloss_col(y[covered, j], pred_store[(base_name, target, cfg.name)][covered])
                rows.append(
                    {
                        "base": base_name,
                        "target": target,
                        "model": "rate_logit_shift",
                        "config": cfg.name,
                        "loss": loss,
                        "delta_vs_base": loss - base_loss,
                        "covered_rows": int(covered.sum()),
                    }
                )
    return pd.DataFrame(rows).sort_values(["base", "target", "loss"])


def main() -> None:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    sub = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    train = train.sort_values(KEY).reset_index(drop=True)
    sub = sub.sort_values(KEY).reset_index(drop=True)
    result = evaluate_geometry_rate_shift(train, sub)
    result.to_csv(OUT / "q_rate_shift_geometry_cv_results.csv", index=False)
    best = result.groupby(["base", "target"], as_index=False).head(8)
    best.to_csv(OUT / "q_rate_shift_geometry_cv_top.csv", index=False)
    print(best.round(6).to_string(index=False))
    print("wrote", OUT / "q_rate_shift_geometry_cv_results.csv")


if __name__ == "__main__":
    main()
