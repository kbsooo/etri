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
import sleep_interval_proxy_experiments as sip  # noqa: E402
import sleep_interval_proxy_model_search as search  # noqa: E402


OUT = Path(__file__).resolve().parent
DATA = OUT.parents[0] / "data"
TARGETS = d.TARGETS
KEY = d.KEY


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1 - 1e-5)


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    return float(log_loss(y.astype(int), clip(p), labels=[0, 1]))


def evaluate() -> pd.DataFrame:
    train, _ = sip.prepare_frames()
    raw_train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    sub = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    raw_train = raw_train.sort_values(KEY).reset_index(drop=True)
    sub = sub.sort_values(KEY).reset_index(drop=True)
    train = train.sort_values(KEY).reset_index(drop=True)
    cfg = search.ETConfig("et_leaf6_mf0.8", 420, 6, 0.80, None, 260526 + 6 * 10 + 80)
    saved_current = np.load(OUT / "final_hybrid_0p598_repro_oof.npy")
    folds = geom.geometry_folds(raw_train, sub, n_repeats=10)
    records = {base: {"y": [], "base": [], "proxy": []} for base in ["saved_oof_proxy", "temporal_base"]}
    for tr_idx, val_idx, fold_name in folds:
        ref = train.iloc[tr_idx].copy().reset_index(drop=True)
        val = train.iloc[val_idx].copy().reset_index(drop=True)
        proxy = search.fit_predict(ref, val, cfg)
        temporal = cal.temporal_base(raw_train.iloc[tr_idx].copy().reset_index(drop=True), raw_train.iloc[val_idx].copy().reset_index(drop=True))
        y = train.iloc[val_idx][TARGETS].to_numpy(dtype=int)
        records["saved_oof_proxy"]["y"].append(y)
        records["saved_oof_proxy"]["base"].append(saved_current[val_idx])
        records["saved_oof_proxy"]["proxy"].append(proxy)
        records["temporal_base"]["y"].append(y)
        records["temporal_base"]["base"].append(temporal)
        records["temporal_base"]["proxy"].append(proxy)
        print(f"[sleep proxy geometry] {fold_name} val={len(val_idx)}", flush=True)

    grid = np.array([0.0, 0.02, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30, 0.45, 0.60, 0.80, 1.00])
    rows = []
    for base_name, vals in records.items():
        y = np.vstack(vals["y"])
        base = np.vstack(vals["base"])
        proxy = np.vstack(vals["proxy"])
        for j, target in enumerate(TARGETS):
            base_loss = loss_col(y[:, j], base[:, j])
            proxy_loss = loss_col(y[:, j], proxy[:, j])
            losses = []
            for w in grid:
                losses.append(loss_col(y[:, j], (1.0 - w) * base[:, j] + w * proxy[:, j]))
            best_i = int(np.argmin(losses))
            rows.append(
                {
                    "base": base_name,
                    "target": target,
                    "base_loss": base_loss,
                    "proxy_loss": proxy_loss,
                    "best_weight": float(grid[best_i]),
                    "best_blend_loss": float(losses[best_i]),
                    "delta_vs_base": float(losses[best_i] - base_loss),
                    "scored_occurrences": int(len(y)),
                }
            )
    return pd.DataFrame(rows).sort_values(["base", "target"])


def main() -> None:
    result = evaluate()
    result.to_csv(OUT / "sleep_interval_proxy_geometry_cv_results.csv", index=False)
    print(result.round(6).to_string(index=False))
    print("wrote", OUT / "sleep_interval_proxy_geometry_cv_results.csv")


if __name__ == "__main__":
    main()
