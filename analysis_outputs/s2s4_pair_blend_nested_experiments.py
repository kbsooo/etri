from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss

sys.path.append(str(Path(__file__).resolve().parent))
import block_rate_smoother_experiments as brs  # noqa: E402
import calibration_experiments as cal  # noqa: E402
import deep_dive_analysis as d  # noqa: E402
import meta_feature_experiments as mf  # noqa: E402
import overnight_feature_experiments as ofe  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
TARGETS = d.TARGETS
KEY = d.KEY
PAIR_TARGETS = ["S2", "S4"]
WEIGHT_GRID = np.array([0.0, 0.10, 0.20, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.70, 0.80, 1.0])
BLOCK_CFG = brs.parse_config("s32_a0.9_w10_eq_boost0")


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1 - 1e-5)


def target_loss(y: np.ndarray, pred: np.ndarray, target: str) -> float:
    return float(log_loss(y[:, TARGETS.index(target)], clip(pred[:, TARGETS.index(target)]), labels=[0, 1]))


def pair_mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([target_loss(y, pred, target) for target in PAIR_TARGETS]))


def all_loss(y: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    return {target: target_loss(y, pred, target) for target in TARGETS}


def block_source(train_rows: pd.DataFrame, rows: pd.DataFrame) -> np.ndarray:
    base = cal.temporal_base(train_rows, rows)
    block = brs.block_smoother(train_rows, rows, BLOCK_CFG)
    return clip(0.65 * base + 0.35 * block)


def source_predict(train_rows: pd.DataFrame, rows: pd.DataFrame) -> dict[str, np.ndarray]:
    return {
        "block": block_source(train_rows, rows),
        "overnight_all": ofe.fit_predict(train_rows, rows, "overnight_all"),
        "overnight_context": ofe.fit_predict(train_rows, rows, "overnight_context"),
    }


def source_oof(rows: pd.DataFrame) -> dict[str, np.ndarray]:
    preds = {name: np.zeros((len(rows), len(TARGETS)), dtype=float) for name in ["block", "overnight_all", "overnight_context"]}
    for fold_id, (tr_idx, val_idx) in enumerate(d.make_folds(rows, "subject_blocks")):
        tr = rows.iloc[tr_idx].copy().reset_index(drop=True)
        val = rows.iloc[val_idx].copy().reset_index(drop=True)
        fold_preds = source_predict(tr, val)
        for name, pred in fold_preds.items():
            preds[name][val_idx] = pred
        print(f"[s2s4 source oof] fold={fold_id}", flush=True)
    return {name: clip(pred) for name, pred in preds.items()}


def apply_pairs(sources: dict[str, np.ndarray], choices: dict[str, tuple[str, str, float]]) -> np.ndarray:
    out = sources["block"].copy()
    for target, (left, right, weight_right) in choices.items():
        j = TARGETS.index(target)
        out[:, j] = (1.0 - weight_right) * sources[left][:, j] + weight_right * sources[right][:, j]
    return clip(out)


def fixed_choices() -> dict[str, tuple[str, str, float]]:
    return {
        "S2": ("block", "overnight_all", 0.30),
        "S4": ("overnight_context", "block", 0.45),
    }


def current_choices() -> dict[str, tuple[str, str, float]]:
    return {
        "S2": ("block", "block", 0.0),
        "S4": ("overnight_context", "overnight_context", 0.0),
    }


def choose_pairs(y: np.ndarray, sources: dict[str, np.ndarray]) -> dict[str, tuple[str, str, float]]:
    choices: dict[str, tuple[str, str, float]] = {}
    source_names = list(sources)
    for target in PAIR_TARGETS:
        j = TARGETS.index(target)
        best = (np.inf, "block", "block", 0.0)
        for left in source_names:
            for right in source_names:
                for weight_right in WEIGHT_GRID:
                    pred = (1.0 - weight_right) * sources[left][:, j] + weight_right * sources[right][:, j]
                    loss = float(log_loss(y[:, j], clip(pred), labels=[0, 1]))
                    if loss < best[0] - 1e-12:
                        best = (loss, left, right, float(weight_right))
        choices[target] = (best[1], best[2], best[3])
    return choices


def nested_experiment(train: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, np.ndarray]]:
    y = train[TARGETS].to_numpy(dtype=int)
    pred_current = np.zeros_like(y, dtype=float)
    pred_fixed = np.zeros_like(y, dtype=float)
    pred_nested = np.zeros_like(y, dtype=float)
    selected_rows = []

    for outer_id, (tr_idx, val_idx) in enumerate(d.make_folds(train, "subject_blocks")):
        outer_train = train.iloc[tr_idx].copy().reset_index(drop=True)
        outer_val = train.iloc[val_idx].copy().reset_index(drop=True)
        inner_sources = source_oof(outer_train)
        choices = choose_pairs(outer_train[TARGETS].to_numpy(dtype=int), inner_sources)
        val_sources = source_predict(outer_train, outer_val)
        pred_current[val_idx] = apply_pairs(val_sources, current_choices())
        pred_fixed[val_idx] = apply_pairs(val_sources, fixed_choices())
        pred_nested[val_idx] = apply_pairs(val_sources, choices)
        for target, (left, right, weight_right) in choices.items():
            selected_rows.append(
                {
                    "outer_fold": outer_id,
                    "target": target,
                    "left": left,
                    "right": right,
                    "weight_right": weight_right,
                    "train_rows": len(outer_train),
                    "val_rows": len(outer_val),
                }
            )
        print(f"[s2s4 nested] outer={outer_id} choices={choices}", flush=True)

    rows = []
    for name, pred in [
        ("current_sources", pred_current),
        ("locked_fixed_pairs", pred_fixed),
        ("nested_pair_selector", pred_nested),
    ]:
        row = {"model": name, "pair_mean": pair_mean_loss(y, pred)}
        row.update({target: target_loss(y, pred, target) for target in PAIR_TARGETS})
        rows.append(row)
    return pd.DataFrame(rows).sort_values("pair_mean"), pd.DataFrame(selected_rows), {
        "current_sources": pred_current,
        "locked_fixed_pairs": pred_fixed,
        "nested_pair_selector": pred_nested,
    }


def make_submission(train: pd.DataFrame, sub: pd.DataFrame) -> pd.DataFrame:
    if (OUT / "submission_hybrid_0p598.csv").exists():
        out = pd.read_csv(OUT / "submission_hybrid_0p598.csv", parse_dates=["sleep_date", "lifelog_date"])
        out = out.sort_values(KEY).reset_index(drop=True)
    else:
        out = sub[["subject_id", "sleep_date", "lifelog_date"] + TARGETS].copy()
    sources = source_predict(train, sub)
    fixed_pred = apply_pairs(sources, fixed_choices())
    for target in PAIR_TARGETS:
        out[target] = fixed_pred[:, TARGETS.index(target)]
    return out


def main() -> None:
    train, sub = ofe.prepare()
    train = train.sort_values(KEY).reset_index(drop=True)
    sub = sub.sort_values(KEY).reset_index(drop=True)
    results, selected, _ = nested_experiment(train)
    results.to_csv(OUT / "s2s4_pair_blend_nested_results.csv", index=False)
    selected.to_csv(OUT / "s2s4_pair_blend_nested_selected.csv", index=False)

    submission = make_submission(train, sub)
    submission.to_csv(OUT / "submission_s2s4_locked_pairs.csv", index=False)

    current = {
        "S2": 0.5620673333578604,
        "S4": 0.6329127012137534,
    }
    fixed = results[results["model"].eq("locked_fixed_pairs")].iloc[0]
    nested = results[results["model"].eq("nested_pair_selector")].iloc[0]
    pre_pair_mean = 0.598973 - (
        (float(fixed["S2"]) - current["S2"]) + (float(fixed["S4"]) - current["S4"])
    ) / len(TARGETS)
    estimate = pd.DataFrame(
        [
            {"target": "S2", "old_loss": current["S2"], "locked_fixed_loss": float(fixed["S2"]), "nested_loss": float(nested["S2"])},
            {"target": "S4", "old_loss": current["S4"], "locked_fixed_loss": float(fixed["S4"]), "nested_loss": float(nested["S4"])},
            {
                "target": "mean_from_pre_pair",
                "old_loss": pre_pair_mean,
                "locked_fixed_loss": 0.598973,
                "nested_loss": pre_pair_mean
                + ((float(nested["S2"]) - current["S2"]) + (float(nested["S4"]) - current["S4"])) / len(TARGETS),
            },
        ]
    )
    estimate.to_csv(OUT / "s2s4_pair_blend_nested_estimate.csv", index=False)

    print("\nS2/S4 pair nested validation")
    print(results.round(6).to_string(index=False))
    print("\nSelected")
    print(selected.to_string(index=False))
    print("\nEstimate vs 0p598 assumptions")
    print(estimate.round(6).to_string(index=False))
    print("submission", OUT / "submission_s2s4_locked_pairs.csv")


if __name__ == "__main__":
    main()
