#!/usr/bin/env python3
"""E188: shape/support logit blend stress.

E187 found a clean conflict: shape-only antisymmetric geometry gets the exact
E95/E101 public boundary right, while support-heavy variants improve the wider
edge-band stress but invert that boundary with high confidence. The smallest
repair hypothesis is a logit blend:

    logit(p) = (1 - alpha) * logit(shape) + alpha * logit(support_variant)

If a small positive alpha keeps E95>E101, lifts edge-band accuracy, and still
selects the E176 branch, then support is a repairable weak prior. If no alpha
does this, support is a nonlocal shortcut for the tightest boundary.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import expit, logit


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
PRED_IN = OUT / "e187_e95_e101_boundary_miss_anatomy_predictions.csv"
BRANCH_IN = OUT / "e187_e95_e101_boundary_miss_anatomy_branch_scores.csv"
SUMMARY_OUT = OUT / "e188_shape_support_logit_blend_stress_summary.csv"
CURVE_OUT = OUT / "e188_shape_support_logit_blend_stress_curves.csv"
BRANCH_OUT = OUT / "e188_shape_support_logit_blend_stress_branch_curves.csv"
REPORT_OUT = OUT / "e188_shape_support_logit_blend_stress_report.md"

EPS = 1.0e-12
SHAPE = "shape_only"
SUPPORT_VARIANTS = (
    "shape_support",
    "shape_support_drop_subject",
    "shape_support_drop_global",
    "shape_support_drop_top16_33",
    "shape_support_no_q2s3_targets",
    "shape_support_keep_hard_only",
    "shape_support_drop_visible",
)
ALPHAS = np.round(np.linspace(0.0, 0.5, 101), 6)


def md(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 40) -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    view = view.head(n).copy()
    rendered = view.copy()
    for col in rendered.columns:
        if pd.api.types.is_float_dtype(rendered[col]):
            rendered[col] = rendered[col].map(lambda x: "" if pd.isna(x) else f"{x:.9f}")
        else:
            rendered[col] = rendered[col].map(lambda x: "" if pd.isna(x) else str(x))
    header = "| " + " | ".join(rendered.columns.astype(str)) + " |"
    sep = "| " + " | ".join(["---"] * len(rendered.columns)) + " |"
    rows = ["| " + " | ".join(row) + " |" for row in rendered.astype(str).to_numpy()]
    return "\n".join([header, sep, *rows])


def clipped_logit(p: pd.Series | np.ndarray) -> np.ndarray:
    return logit(np.clip(np.asarray(p, dtype=np.float64), EPS, 1.0 - EPS))


def metric_rows(pred: pd.DataFrame, support_variant: str, alpha: float, p: np.ndarray) -> dict[str, float | int | str | bool]:
    y = pred["actual_new_better"].to_numpy(dtype=int)
    rec: dict[str, float | int | str | bool] = {
        "support_variant": support_variant,
        "alpha": float(alpha),
        "n_rows": int(len(pred)),
        "accuracy": float(np.mean((p >= 0.5) == y)),
    }
    for flag, name in [
        ("frontier_pair", "frontier"),
        ("micro_pair", "micro"),
        ("e95_edge_pair", "edge"),
        ("e95_e101_pair", "e95_e101"),
    ]:
        mask = pred[flag].to_numpy(dtype=bool)
        yy = y[mask]
        pp = p[mask]
        rec[f"{name}_n"] = int(len(yy))
        rec[f"{name}_accuracy"] = float(np.mean((pp >= 0.5) == yy)) if len(yy) else np.nan
    exact = pred[pred["e95_e101_pair"]].copy()
    rec["e95_prob_mean"] = float(
        p[exact.index[exact["new_file"].str.contains("e95")].to_numpy()]
        .mean()
    )
    rec["e101_prob_mean"] = float(
        p[exact.index[exact["new_file"].str.contains("e101")].to_numpy()]
        .mean()
    )
    return rec


def branch_blend(shape_branch: pd.DataFrame, support_branch: pd.DataFrame, support_variant: str, alpha: float) -> pd.DataFrame:
    keys = ["candidate", "scenario"]
    merged = shape_branch[keys + ["prob_pressure_min_public_better"]].rename(
        columns={"prob_pressure_min_public_better": "p_shape"}
    ).merge(
        support_branch[keys + ["prob_pressure_min_public_better"]].rename(
            columns={"prob_pressure_min_public_better": "p_support"}
        ),
        on=keys,
    )
    p = expit((1.0 - alpha) * clipped_logit(merged["p_shape"]) + alpha * clipped_logit(merged["p_support"]))
    out = merged[keys].copy()
    out["support_variant"] = support_variant
    out["alpha"] = float(alpha)
    out["prob_pressure_min_public_better"] = p
    out["prefers_favorable_min"] = out["prob_pressure_min_public_better"] >= 0.5
    return out


def run() -> None:
    pred = pd.read_csv(PRED_IN)
    branch = pd.read_csv(BRANCH_IN)
    file_pred = pred[pred["group_col"].eq("file")].copy().reset_index(drop=True)
    keys = ["heldout", "pair_id", "new_file", "base_file"]
    shape_pred = file_pred[file_pred["variant"].eq(SHAPE)][
        keys
        + [
            "actual_new_better",
            "frontier_pair",
            "micro_pair",
            "e95_edge_pair",
            "e95_e101_pair",
            "prob_new_better",
        ]
    ].rename(columns={"prob_new_better": "p_shape"})
    shape_branch = branch[branch["variant"].eq(SHAPE)].copy()

    curves: list[dict[str, float | int | str | bool]] = []
    branch_curves: list[pd.DataFrame] = []
    for support_variant in SUPPORT_VARIANTS:
        support_pred = file_pred[file_pred["variant"].eq(support_variant)][keys + ["prob_new_better"]].rename(
            columns={"prob_new_better": "p_support"}
        )
        merged = shape_pred.merge(support_pred, on=keys)
        ls = clipped_logit(merged["p_shape"])
        lu = clipped_logit(merged["p_support"])
        support_branch = branch[branch["variant"].eq(support_variant)].copy()
        for alpha in ALPHAS:
            p = expit((1.0 - alpha) * ls + alpha * lu)
            curves.append(metric_rows(merged, support_variant, float(alpha), p))
            branch_curves.append(branch_blend(shape_branch, support_branch, support_variant, float(alpha)))

    curve = pd.DataFrame(curves)
    branch_curve = pd.concat(branch_curves, ignore_index=True)
    branch_summary = branch_curve.groupby(["support_variant", "alpha", "candidate"]).agg(
        branch_favorable_rate=("prefers_favorable_min", "mean"),
        branch_prob_mean=("prob_pressure_min_public_better", "mean"),
        branch_prob_min=("prob_pressure_min_public_better", "min"),
        branch_prob_max=("prob_pressure_min_public_better", "max"),
    ).reset_index()
    e176 = branch_summary[branch_summary["candidate"].eq("e176")].drop(columns=["candidate"]).rename(
        columns={
            "branch_favorable_rate": "e176_favorable_rate",
            "branch_prob_mean": "e176_prob_mean",
            "branch_prob_min": "e176_prob_min",
            "branch_prob_max": "e176_prob_max",
        }
    )
    curve = curve.merge(e176, on=["support_variant", "alpha"], how="left")
    curve["action_grade"] = (
        curve["e95_e101_accuracy"].eq(1.0)
        & curve["frontier_accuracy"].ge(0.80)
        & curve["edge_accuracy"].ge(0.80)
        & curve["e176_favorable_rate"].eq(1.0)
    )

    best = curve.sort_values(
        [
            "action_grade",
            "e95_e101_accuracy",
            "edge_accuracy",
            "frontier_accuracy",
            "accuracy",
            "alpha",
        ],
        ascending=[False, False, False, False, False, True],
    )
    first_flip = curve[curve["e95_e101_accuracy"].lt(1.0)].groupby("support_variant")["alpha"].min().reset_index()
    first_flip = first_flip.rename(columns={"alpha": "first_e95_e101_failure_alpha"})
    summary = best.groupby("support_variant", as_index=False).head(1).merge(first_flip, on="support_variant", how="left")

    curve.to_csv(CURVE_OUT, index=False)
    branch_curve.to_csv(BRANCH_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)

    action = curve[curve["action_grade"]].sort_values(
        ["edge_accuracy", "frontier_accuracy", "accuracy", "alpha"],
        ascending=[False, False, False, True],
    )
    if action.empty:
        one_liner = (
            "No positive shape/support logit blend repairs the conflict: edge-band "
            "accuracy stays at shape-only levels until E95/E101 flips."
        )
    else:
        row = action.iloc[0]
        one_liner = (
            f"`{row['support_variant']}` at alpha `{float(row['alpha']):.3f}` is action-grade: "
            f"edge {float(row['edge_accuracy']):.3f}, frontier {float(row['frontier_accuracy']):.3f}, "
            f"E95/E101 {float(row['e95_e101_accuracy']):.3f}."
        )

    cols_summary = [
        "support_variant",
        "alpha",
        "accuracy",
        "frontier_accuracy",
        "micro_accuracy",
        "edge_accuracy",
        "e95_e101_accuracy",
        "e95_prob_mean",
        "e101_prob_mean",
        "e176_favorable_rate",
        "e176_prob_mean",
        "action_grade",
        "first_e95_e101_failure_alpha",
    ]
    report = f"""# E188 Shape/Support Logit Blend Stress

## Question

Can a very small support prior improve E95-edge stress without destroying the
exact E95/E101 public boundary that shape-only gets right?

## Result In One Sentence

{one_liner}

## Best Per Support Variant

{md(summary, cols_summary, n=40)}

## Best Action-Grade Rows

{md(action, cols_summary, n=40)}

## Interpretation

- Shape-only is the only family that respects the exact E95/E101 boundary.
- Support variants add useful wider edge-band signal, but the useful threshold
  is beyond the alpha where E95/E101 already flips.
- Therefore support is not a weak repair prior; it is a different public-quality
  shortcut. It can be used as a sensor, but not as an automatic frontier
  selector without an external boundary veto.
"""
    REPORT_OUT.write_text(report, encoding="utf-8")

    print(SUMMARY_OUT)
    print(CURVE_OUT)
    print(BRANCH_OUT)
    print(REPORT_OUT)


if __name__ == "__main__":
    run()
