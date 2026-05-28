from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "jepa"
ANALYSIS = ROOT / "analysis_outputs"
DATA = ROOT / "data"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "lifelog_date"]
SUB_KEY = ["subject_id", "sleep_date", "lifelog_date"]

sys.path.insert(0, str(ANALYSIS))
import broad_single_feature_residual_probe as broad  # noqa: E402


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1.0 - 1e-5)


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    pp = clip(p)
    yy = y.astype(float)
    return float(-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp)).mean())


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([loss_col(y[:, j], pred[:, j]) for j in range(len(TARGETS))]))


def main() -> None:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    sub = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    jtr = pd.read_parquet(OUT / "train_jepa_features.parquet")
    jsu = pd.read_parquet(OUT / "submission_jepa_features.parquet")
    train_df = train[SUB_KEY + TARGETS].merge(jtr, on=SUB_KEY, how="left")
    sub_df = sub[SUB_KEY].merge(jsu, on=SUB_KEY, how="left")
    base = clip(np.load(ANALYSIS / "final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy"))
    base_sub = pd.read_csv(ANALYSIS / "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    assert base_sub[SUB_KEY].equals(sub[SUB_KEY])
    y = train[TARGETS].to_numpy(dtype=int)
    j = TARGETS.index("Q2")
    base_q2 = loss_col(y[:, j], base[:, j])

    nested = pd.read_csv(OUT / "jepa_nested_selected.csv")
    q2 = nested[nested["target"].eq("Q2")].copy()
    unique = q2[["feature", "mode", "c_value", "weight"]].drop_duplicates().reset_index(drop=True)
    corrected_map: dict[str, np.ndarray] = {}
    corrected_sub_map: dict[str, np.ndarray] = {}
    rows = []
    for idx, row in unique.iterrows():
        feature = str(row["feature"])
        mode = str(row["mode"])
        c_value = float(row["c_value"])
        default_weight = float(row["weight"])
        key = f"q2_nested_{idx:02d}"
        corrected = broad.oof_corrected(train_df, base, "Q2", feature, mode, c_value)
        corrected_map[key] = corrected
        corrected_sub_map[key] = broad.fit_corrected(train_df, sub_df, base, base_sub[TARGETS].to_numpy(dtype=float), "Q2", feature, mode, c_value)
        losses = [loss_col(y[:, j], (1.0 - w) * base[:, j] + w * corrected) for w in broad.GRID]
        best_i = int(np.argmin(losses))
        guard = broad.repeated_subject_guardrail(train_df, y, base, corrected, j)
        rows.append(
            {
                "name": key,
                "feature": feature,
                "mode": mode,
                "c_value": c_value,
                "nested_count": int(((q2["feature"] == feature) & (q2["mode"] == mode)).sum()),
                "nested_holdout_delta_mean": float(q2[(q2["feature"] == feature) & (q2["mode"] == mode)]["holdout_delta"].mean()),
                "default_weight": default_weight,
                "best_weight": float(broad.GRID[best_i]),
                "base_loss": base_q2,
                "best_loss": float(losses[best_i]),
                "delta_vs_base": float(losses[best_i] - base_q2),
                **guard,
            }
        )

    # Consensus target: average corrected probabilities from nested-selected Q2 ops.
    if corrected_map:
        avg_corr = np.mean(np.column_stack(list(corrected_map.values())), axis=1)
        losses = [loss_col(y[:, j], (1.0 - w) * base[:, j] + w * avg_corr) for w in broad.GRID]
        best_i = int(np.argmin(losses))
        rows.append(
            {
                "name": "q2_nested_consensus_avg",
                "feature": ";".join(unique["feature"].astype(str)),
                "mode": "avg",
                "c_value": -1.0,
                "nested_count": int(len(q2)),
                "nested_holdout_delta_mean": float(q2["holdout_delta"].mean()),
                "default_weight": 0.45,
                "best_weight": float(broad.GRID[best_i]),
                "base_loss": base_q2,
                "best_loss": float(losses[best_i]),
                "delta_vs_base": float(losses[best_i] - base_q2),
                "mean_delta": np.nan,
                "median_delta": np.nan,
                "p25_delta": np.nan,
                "p75_delta": np.nan,
                "win_rate": np.nan,
                "mean_selected_weight": np.nan,
                "zero_weight_rate": np.nan,
            }
        )
    summary = pd.DataFrame(rows).sort_values(["delta_vs_base", "nested_holdout_delta_mean"])
    summary.to_csv(OUT / "jepa_nested_q2_probe_summary.csv", index=False)

    # Save best full-OOF Q2 probe if it improves at all.
    if not summary.empty and float(summary.iloc[0]["best_weight"]) > 0:
        best = summary.iloc[0]
        pred = base.copy()
        if best["name"] == "q2_nested_consensus_avg":
            corr = np.mean(np.column_stack(list(corrected_map.values())), axis=1)
            corr_sub = np.mean(np.column_stack(list(corrected_sub_map.values())), axis=1)
        else:
            corr = corrected_map[str(best["name"])]
            corr_sub = corrected_sub_map[str(best["name"])]
        w = float(best["best_weight"])
        pred[:, j] = clip((1.0 - w) * pred[:, j] + w * corr)
        np.save(OUT / "jepa_nested_q2_probe_oof.npy", pred)
        out = base_sub.copy()
        arr = out[TARGETS].to_numpy(dtype=float).copy()
        arr[:, j] = clip((1.0 - w) * arr[:, j] + w * corr_sub)
        out[TARGETS] = arr
        out.to_csv(OUT / "submission_jepa_nested_q2_probe.csv", index=False)
        cv_rows = []
        for k, target in enumerate(TARGETS):
            cv_rows.append(
                {
                    "target": target,
                    "base_loss": loss_col(y[:, k], base[:, k]),
                    "candidate_loss": loss_col(y[:, k], pred[:, k]),
                    "delta_vs_base": loss_col(y[:, k], pred[:, k]) - loss_col(y[:, k], base[:, k]),
                }
            )
        cv_rows.append({"target": "mean", "base_loss": mean_loss(y, base), "candidate_loss": mean_loss(y, pred), "delta_vs_base": mean_loss(y, pred) - mean_loss(y, base)})
        pd.DataFrame(cv_rows).to_csv(OUT / "jepa_nested_q2_probe_cv_estimate.csv", index=False)
    print(summary.round(9).to_string(index=False))


if __name__ == "__main__":
    main()
