from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss

sys.path.append(str(Path(__file__).resolve().parent))
import deep_dive_analysis as d  # noqa: E402
import geometry_mask_cv_experiments as geom  # noqa: E402
import sleep_interval_proxy_augmented_experiments as aug  # noqa: E402


OUT = Path(__file__).resolve().parent
DATA = OUT.parents[0] / "data"
TARGETS = d.TARGETS
KEY = d.KEY


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1 - 1e-5)


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    return float(log_loss(y.astype(int), clip(p), labels=[0, 1]))


def main() -> None:
    train, _ = aug.prepare_frames()
    raw_train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    sub = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    train = train.sort_values(KEY).reset_index(drop=True)
    raw_train = raw_train.sort_values(KEY).reset_index(drop=True)
    sub = sub.sort_values(KEY).reset_index(drop=True)
    cfg = aug.ETConfig("aug_leaf10_mf0.6", 520, 10, 0.60, None, 260705)
    current = np.load(OUT / "final_hybrid_0p598_repro_oof.npy")
    folds = geom.geometry_folds(raw_train, sub, n_repeats=10)
    ys = []
    bases = []
    proxies = []
    for tr_idx, val_idx, fold_name in folds:
        ref = train.iloc[tr_idx].copy().reset_index(drop=True)
        val = train.iloc[val_idx].copy().reset_index(drop=True)
        proxy = aug.fit_predict(ref, val, cfg)
        ys.append(train.iloc[val_idx][TARGETS].to_numpy(dtype=int))
        bases.append(current[val_idx])
        proxies.append(proxy)
        print(f"[aug sleep proxy geometry] {fold_name} val={len(val_idx)}", flush=True)
    y = np.vstack(ys)
    base = np.vstack(bases)
    proxy = np.vstack(proxies)
    grid = np.array([0.0, 0.02, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30, 0.45, 0.60, 0.80, 1.00])
    rows = []
    for j, target in enumerate(TARGETS):
        losses = [loss_col(y[:, j], (1.0 - w) * base[:, j] + w * proxy[:, j]) for w in grid]
        best_i = int(np.argmin(losses))
        rows.append(
            {
                "target": target,
                "base_loss": loss_col(y[:, j], base[:, j]),
                "proxy_loss": loss_col(y[:, j], proxy[:, j]),
                "best_weight": float(grid[best_i]),
                "best_blend_loss": float(losses[best_i]),
                "delta_vs_base": float(losses[best_i] - loss_col(y[:, j], base[:, j])),
                "scored_occurrences": int(len(y)),
            }
        )
    result = pd.DataFrame(rows)
    result.to_csv(OUT / "sleep_interval_proxy_augmented_geometry_cv_results.csv", index=False)
    print(result.round(6).to_string(index=False))
    print("wrote", OUT / "sleep_interval_proxy_augmented_geometry_cv_results.csv")


if __name__ == "__main__":
    main()
