from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))
import current_0p594_cross_target_coherence as cur  # noqa: E402
import deep_dive_analysis as d  # noqa: E402
import sleep_fragmentation_proxy_experiments as frag  # noqa: E402


OUT = Path(__file__).resolve().parent
TARGETS = d.TARGETS
GRID = np.array([0.0, 0.02, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30, 0.45, 0.60, 0.80, 1.00])


def loss(y: np.ndarray, p: np.ndarray) -> float:
    return frag.loss_col(y, p)


def main() -> None:
    train, _ = frag.prepare_frames()
    y = train[TARGETS].to_numpy(dtype=int)
    current = cur.current_oof()
    subjects = np.array(sorted(train["subject_id"].unique()))
    rows = []
    rng = np.random.default_rng(260926)

    for cfg in frag.configs():
        pred_path = OUT / f"sleep_fragmentation_proxy_oof_{cfg.name}.npy"
        proxy = np.load(pred_path)
        for rep in range(250):
            sel_subjects = set(rng.choice(subjects, size=len(subjects) // 2, replace=False))
            sel_mask = train["subject_id"].isin(sel_subjects).to_numpy()
            hold_mask = ~sel_mask
            for j, target in enumerate(TARGETS):
                best = None
                for w in GRID:
                    p = (1.0 - w) * current[:, j] + w * proxy[:, j]
                    sel = loss(y[sel_mask, j], p[sel_mask])
                    if best is None or sel < best[0]:
                        best = (sel, float(w), p)
                assert best is not None
                hold_current = loss(y[hold_mask, j], current[hold_mask, j])
                hold_blend = loss(y[hold_mask, j], best[2][hold_mask])
                rows.append(
                    {
                        "config": cfg.name,
                        "rep": rep,
                        "target": target,
                        "selected_weight": best[1],
                        "select_loss": best[0],
                        "holdout_current": hold_current,
                        "holdout_blend": hold_blend,
                        "holdout_delta": hold_blend - hold_current,
                    }
                )

    detail = pd.DataFrame(rows)
    detail.to_csv(OUT / "sleep_fragmentation_proxy_subject_split_guardrail_detail.csv", index=False)
    summary = (
        detail.groupby(["config", "target"])
        .agg(
            mean_delta=("holdout_delta", "mean"),
            median_delta=("holdout_delta", "median"),
            p25_delta=("holdout_delta", lambda x: float(np.quantile(x, 0.25))),
            p75_delta=("holdout_delta", lambda x: float(np.quantile(x, 0.75))),
            win_rate=("holdout_delta", lambda x: float((x < 0).mean())),
            mean_selected_weight=("selected_weight", "mean"),
            zero_weight_rate=("selected_weight", lambda x: float((x == 0).mean())),
        )
        .reset_index()
        .sort_values(["target", "mean_delta"])
    )
    summary.to_csv(OUT / "sleep_fragmentation_proxy_subject_split_guardrail.csv", index=False)
    print(summary.round(6).to_string(index=False))


if __name__ == "__main__":
    main()
