from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))
import calibration_experiments as cal  # noqa: E402
import deep_dive_analysis as d  # noqa: E402
import overnight_feature_experiments as ov  # noqa: E402


OUT = Path(__file__).resolve().parent
TARGETS = d.TARGETS


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1 - 1e-5)


def blend_prediction(train: pd.DataFrame, sub: pd.DataFrame, group: str) -> np.ndarray:
    weights = pd.read_csv(OUT / "overnight_nested_weights.csv")
    mean_weights = weights[weights["group"].eq(group)].filter(like="w_").mean()
    w = np.asarray([mean_weights[f"w_{target}"] for target in TARGETS], dtype=float)
    base = cal.temporal_base(train, sub)
    sensor = ov.fit_predict(train, sub, group)
    return clip((1.0 - w) * base + w * sensor)


def main() -> None:
    train, sub = ov.prepare()
    tiny = pd.read_csv(OUT / "submission_best.csv")
    block = pd.read_csv(OUT / "submission_block_target_switch.csv")

    overnight = pd.read_csv(OUT / "overnight_nested_results.csv")
    source_losses: dict[str, pd.Series] = {
        "tiny_watch": pd.read_csv(OUT / "tiny_watch_cap_nested_results.csv")
        .set_index("model")
        .loc["nested_tiny_watch", TARGETS]
        .astype(float),
        "block_fixed": pd.read_csv(OUT / "block_target_switch_fixed_cfg_estimate.csv")
        .set_index("target")
        .loc[TARGETS, "fixed_block_loss"]
        .astype(float),
    }
    for _, row in overnight.iterrows():
        if row["model"] in {"nested_blend", "sensor_only"}:
            source_losses[f"{row['group']}_{row['model']}"] = row[TARGETS].astype(float)

    loss_frame = pd.DataFrame(source_losses)
    best_source = loss_frame.idxmin(axis=1)
    best_loss = loss_frame.min(axis=1)

    prediction_cache: dict[str, pd.DataFrame] = {
        "tiny_watch": tiny.copy(),
        "block_fixed": block.copy(),
    }

    def prediction_for(source: str) -> pd.DataFrame:
        if source in prediction_cache:
            return prediction_cache[source]
        if source.endswith("_sensor_only"):
            group = source.removesuffix("_sensor_only")
            pred = ov.fit_predict(train, sub, group)
        elif source.endswith("_nested_blend"):
            group = source.removesuffix("_nested_blend")
            pred = blend_prediction(train, sub, group)
        else:
            raise ValueError(source)
        frame = sub[["subject_id", "sleep_date", "lifelog_date"]].copy()
        for j, target in enumerate(TARGETS):
            frame[target] = pred[:, j]
        prediction_cache[source] = frame
        return frame

    out = tiny.copy()
    for target in TARGETS:
        src = str(best_source[target])
        out[target] = prediction_for(src)[target].to_numpy(dtype=float)
    for target in TARGETS:
        out[target] = clip(out[target].to_numpy(dtype=float))
    estimate = pd.DataFrame(
        [
            {"target": target, "source": str(best_source[target]), "cv_loss": float(best_loss[target])}
            for target in TARGETS
        ]
    )
    estimate.loc[len(estimate)] = {"target": "mean", "source": "hybrid", "cv_loss": estimate["cv_loss"].mean()}
    out.to_csv(OUT / "submission_hybrid_overnight_v2.csv", index=False)
    estimate.to_csv(OUT / "hybrid_overnight_v2_cv_estimate.csv", index=False)

    print("wrote", OUT / "submission_hybrid_overnight_v2.csv")
    print(estimate.to_string(index=False))
    print("range", float(out[TARGETS].min().min()), float(out[TARGETS].max().max()))
    print("means")
    print(out[TARGETS].mean().round(5).to_string())


if __name__ == "__main__":
    main()
