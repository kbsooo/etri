from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))
import deep_dive_analysis as d  # noqa: E402
import geometry_mask_cv_experiments as geom  # noqa: E402
import sleep_interval_proxy_foldsafe_guardrail as fg  # noqa: E402


OUT = Path(__file__).resolve().parent
DATA = OUT.parents[0] / "data"
TARGETS = d.TARGETS
KEY = d.KEY


def main() -> None:
    train, _ = fg.base_frames()
    raw_train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    raw_sub = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    train = train.sort_values(KEY).reset_index(drop=True)
    raw_train = raw_train.sort_values(KEY).reset_index(drop=True)
    raw_sub = raw_sub.sort_values(KEY).reset_index(drop=True)
    cfg = next(c for c in fg.configs() if c.name == "foldsafe_leaf3_mf0.35")
    rel_cols = fg.relative_source_cols(train)
    current = np.load(OUT / "final_hybrid_0p598_repro_oof.npy")
    folds = geom.geometry_folds(raw_train, raw_sub, n_repeats=10)
    ys, bases, proxies = [], [], []
    for _, (tr_idx, val_idx, fold_name) in enumerate(folds):
        ref_raw = train.iloc[tr_idx].copy().reset_index(drop=True)
        val_raw = train.iloc[val_idx].copy().reset_index(drop=True)
        ref = fg.add_ref_relative_features(ref_raw, ref_raw, rel_cols)
        val = fg.add_ref_relative_features(val_raw, ref_raw, rel_cols)
        proxy = fg.fit_predict(ref, val, cfg)
        ys.append(train.iloc[val_idx][TARGETS].to_numpy(dtype=int))
        bases.append(current[val_idx])
        proxies.append(proxy)
        print(f"[foldsafe leaf3 geometry grid] {fold_name} val={len(val_idx)}", flush=True)
    y = np.vstack(ys)
    base = np.vstack(bases)
    proxy = np.vstack(proxies)
    grid = np.array([0.0, 0.02, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30, 0.45, 0.60, 0.80, 1.00])
    rows = []
    for j, target in enumerate(TARGETS):
        base_loss = fg.loss_col(y[:, j], base[:, j])
        for w in grid:
            loss = fg.loss_col(y[:, j], (1.0 - w) * base[:, j] + w * proxy[:, j])
            rows.append(
                {
                    "config": cfg.name,
                    "target": target,
                    "weight": float(w),
                    "loss": loss,
                    "delta_vs_base": loss - base_loss,
                    "base_loss": base_loss,
                    "proxy_loss": fg.loss_col(y[:, j], proxy[:, j]),
                    "scored_occurrences": int(len(y)),
                }
            )
    result = pd.DataFrame(rows)
    result.to_csv(OUT / "sleep_interval_proxy_foldsafe_leaf3_geometry_grid.csv", index=False)
    print(result[result["target"].isin(["Q2", "Q3"])].to_string(index=False))
    print("wrote", OUT / "sleep_interval_proxy_foldsafe_leaf3_geometry_grid.csv")


if __name__ == "__main__":
    main()
