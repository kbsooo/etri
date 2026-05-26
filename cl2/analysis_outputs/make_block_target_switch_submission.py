from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))
import block_rate_smoother_experiments as brs  # noqa: E402
import calibration_experiments as cal  # noqa: E402
import deep_dive_analysis as d  # noqa: E402


OUT = Path(__file__).resolve().parent
TARGETS = d.TARGETS


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1 - 1e-5)


def main() -> None:
    train = pd.read_parquet(OUT / "train_deep_features.parquet")
    sub = pd.read_parquet(OUT / "submission_deep_features.parquet")
    tiny = pd.read_csv(OUT / "submission_best.csv")

    cfg = brs.parse_config("s32_a0.9_w10_eq_boost0")
    blend = 0.35
    temporal = cal.temporal_base(train, sub)
    block = brs.block_smoother(train, sub, cfg)
    block_blend = clip((1.0 - blend) * temporal + blend * block)

    out = tiny.copy()
    for target in ["S1", "S2", "S4"]:
        out[target] = block_blend[:, TARGETS.index(target)]
    out.to_csv(OUT / "submission_block_target_switch.csv", index=False)

    tiny_cv = pd.read_csv(OUT / "tiny_watch_cap_nested_results.csv").set_index("model").loc["nested_tiny_watch", TARGETS]
    block_cv = pd.read_csv(OUT / "block_rate_smoother_nested_results.csv").set_index("model").loc["nested_block_blend", TARGETS]
    chosen = pd.concat([tiny_cv.rename("tiny_watch"), block_cv.rename("block_smoother")], axis=1)
    chosen["selected_source"] = ["block_smoother" if t in {"S1", "S2", "S4"} else "tiny_watch" for t in TARGETS]
    chosen["selected_loss"] = [
        chosen.loc[t, "block_smoother"] if t in {"S1", "S2", "S4"} else chosen.loc[t, "tiny_watch"]
        for t in TARGETS
    ]
    chosen.loc["mean"] = [np.nan, np.nan, "target_switch", float(chosen["selected_loss"].mean())]
    chosen.to_csv(OUT / "block_target_switch_cv_estimate.csv")

    grid = pd.read_csv(OUT / "block_rate_smoother_results.csv")
    fixed = grid[
        (grid["model"] == "tiny_watch_block_blend_0.35")
        & (grid["config"] == "s32_a0.9_w10_eq_boost0")
    ]
    if not fixed.empty:
        fixed_losses = fixed.iloc[0][TARGETS]
        fixed_chosen = tiny_cv.copy()
        for target in ["S1", "S2", "S4"]:
            fixed_chosen[target] = fixed_losses[target]
        pd.DataFrame(
            {
                "target": TARGETS,
                "tiny_watch_loss": tiny_cv.to_numpy(dtype=float),
                "fixed_block_loss": fixed_losses.to_numpy(dtype=float),
                "selected_loss": fixed_chosen.to_numpy(dtype=float),
                "selected_source": ["block_smoother" if t in {"S1", "S2", "S4"} else "tiny_watch" for t in TARGETS],
            }
        ).to_csv(OUT / "block_target_switch_fixed_cfg_estimate.csv", index=False)
        print("fixed_cfg_target_switch_mean", float(fixed_chosen.mean()))

    print("wrote", OUT / "submission_block_target_switch.csv")
    print(chosen.to_string())
    print("probability range", float(out[TARGETS].min().min()), float(out[TARGETS].max().max()))


if __name__ == "__main__":
    main()
