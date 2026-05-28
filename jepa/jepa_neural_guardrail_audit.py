from __future__ import annotations

import sys
from dataclasses import dataclass
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
import geometry_mask_cv_experiments as geom  # noqa: E402


C_GRID = [0.05, 0.20]


@dataclass(frozen=True)
class Op:
    target: str
    feature: str
    mode: str
    c_value: float
    weight: float
    inner_delta: float


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1.0 - 1e-5)


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    pp = clip(p)
    yy = y.astype(float)
    return float(-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp)).mean())


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([loss_col(y[:, j], pred[:, j]) for j in range(len(TARGETS))]))


def choose_inner(inner: pd.DataFrame, base: np.ndarray, target: str, pre: pd.DataFrame) -> tuple[Op | None, pd.DataFrame]:
    y = inner[target].to_numpy(dtype=int)
    j = TARGETS.index(target)
    base_loss = loss_col(y, base[:, j])
    rows = []
    for cand in pre[pre["target"].eq(target)].itertuples(index=False):
        for c_value in C_GRID:
            corrected = broad.oof_corrected(inner, base, target, str(cand.feature), str(cand.mode), c_value)
            losses = [loss_col(y, (1.0 - w) * base[:, j] + w * corrected) for w in broad.GRID]
            best_i = int(np.argmin(losses))
            rows.append(
                {
                    "target": target,
                    "feature": str(cand.feature),
                    "mode": str(cand.mode),
                    "c_value": float(c_value),
                    "weight": float(broad.GRID[best_i]),
                    "base_loss": float(base_loss),
                    "best_loss": float(losses[best_i]),
                    "inner_delta": float(losses[best_i] - base_loss),
                    "corr": float(cand.corr),
                }
            )
    cand_df = pd.DataFrame(rows).sort_values(["inner_delta", "weight"], ascending=[True, False]) if rows else pd.DataFrame()
    if cand_df.empty:
        return None, cand_df
    top = cand_df.iloc[0]
    if float(top["weight"]) <= 0.0 or float(top["inner_delta"]) >= 0.0:
        return None, cand_df
    return (
        Op(
            str(top["target"]),
            str(top["feature"]),
            str(top["mode"]),
            float(top["c_value"]),
            float(top["weight"]),
            float(top["inner_delta"]),
        ),
        cand_df,
    )


def main(top_n: int = 5, repeats: int = 4) -> None:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    sub = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    neural = pd.read_parquet(OUT / "train_neural_jepa_features.parquet")
    df = train[SUB_KEY + TARGETS].merge(neural, on=SUB_KEY, how="left")
    base = clip(np.load(ANALYSIS / "final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy"))
    y_all = df[TARGETS].to_numpy(dtype=int)

    selected_rows = []
    candidate_rows = []
    fold_rows = []
    for tr_idx, val_idx, fold in geom.geometry_folds(train, sub, n_repeats=repeats):
        inner = df.iloc[tr_idx].reset_index(drop=True)
        hold = df.iloc[val_idx].reset_index(drop=True)
        inner_base = base[tr_idx].copy()
        hold_base = base[val_idx].copy()
        cols = broad.finite_numeric_cols(inner)
        pre = broad.prefilter(inner, inner_base, cols, TARGETS, top_n=top_n)
        pred = hold_base.copy()
        for target in TARGETS:
            op, cand_df = choose_inner(inner, inner_base, target, pre)
            if not cand_df.empty:
                cand_df.insert(0, "fold", fold)
                candidate_rows.append(cand_df)
            if op is None:
                continue
            j = TARGETS.index(target)
            corrected = broad.fit_corrected(inner, hold, inner_base, hold_base, op.target, op.feature, op.mode, op.c_value)
            pred[:, j] = clip((1.0 - op.weight) * hold_base[:, j] + op.weight * corrected)
            hold_delta = loss_col(y_all[val_idx, j], pred[:, j]) - loss_col(y_all[val_idx, j], hold_base[:, j])
            selected_rows.append({**op.__dict__, "fold": fold, "holdout_delta": float(hold_delta), "holdout_rows": int(len(val_idx))})
        fold_rows.append(
            {
                "fold": fold,
                "rows": int(len(val_idx)),
                "base_mean": mean_loss(y_all[val_idx], hold_base),
                "candidate_mean": mean_loss(y_all[val_idx], pred),
                "delta_mean": mean_loss(y_all[val_idx], pred) - mean_loss(y_all[val_idx], hold_base),
            }
        )
        print(f"neural nested {fold}: delta={fold_rows[-1]['delta_mean']:.6f}", flush=True)

    selected = pd.DataFrame(selected_rows)
    candidates = pd.concat(candidate_rows, ignore_index=True) if candidate_rows else pd.DataFrame()
    folds = pd.DataFrame(fold_rows)
    selected.to_csv(OUT / "neural_jepa_nested_selected.csv", index=False)
    candidates.to_csv(OUT / "neural_jepa_nested_inner_candidates.csv", index=False)
    folds.to_csv(OUT / "neural_jepa_nested_folds.csv", index=False)
    if selected.empty:
        summary = pd.DataFrame()
    else:
        summary = (
            selected.groupby("target")
            .agg(
                n_selected=("target", "size"),
                inner_delta_mean=("inner_delta", "mean"),
                holdout_delta_mean=("holdout_delta", "mean"),
                holdout_delta_median=("holdout_delta", "median"),
                holdout_win_rate=("holdout_delta", lambda s: float((s < 0).mean())),
            )
            .reset_index()
            .sort_values("holdout_delta_mean")
        )
    summary.to_csv(OUT / "neural_jepa_nested_summary.csv", index=False)
    lines = [
        "# Neural JEPA Nested Guardrail",
        "",
        "## Nested Geometry Folds",
        "",
        folds.to_csv(index=False),
        "",
        "## Nested Target Summary",
        "",
        summary.to_csv(index=False) if not summary.empty else "No selected features.",
    ]
    (OUT / "neural_jepa_guardrail_report.md").write_text("\n".join(lines), encoding="utf-8")
    print(folds.round(9).to_string(index=False))
    print(summary.round(9).to_string(index=False) if not summary.empty else "no selected")


if __name__ == "__main__":
    main()
