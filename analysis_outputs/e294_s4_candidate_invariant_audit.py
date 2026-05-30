#!/usr/bin/env python3
"""E294: S4 candidate-level invariant audit.

E293 found a cliff:

    null-safe S4 lifestyle edits are too small,
    selector-visible S4 edits are matched-null reproducible.

This script asks whether the *candidate tensor itself* contains an invariant
that distinguishes the real S4 lifestyle placement from its matched
row/subject/dateblock null placements. No public LB is used and no submission
file is created.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

GOVERNOR_IN = OUT / "e293_s4_lownull_governor_summary.csv"
SCORES_IN = OUT / "e293_s4_lownull_scores.csv"
NULL_MAP_IN = OUT / "e293_s4_lownull_null_map.csv"

SUMMARY_OUT = OUT / "e294_s4_candidate_invariant_summary.csv"
CANDIDATE_OUT = OUT / "e294_s4_candidate_invariant_candidate_scores.csv"
PERCENTILE_OUT = OUT / "e294_s4_candidate_invariant_feature_percentiles.csv"
REPORT_OUT = OUT / "e294_s4_candidate_invariant_report.md"


def md_table(frame: pd.DataFrame, n: int = 25, floatfmt: str = ".6f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame.head(n).copy()
    for col in view.columns:
        if pd.api.types.is_float_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else format(float(x), floatfmt))
    view = view.fillna("")
    headers = [str(c) for c in view.columns]
    rows = [[str(v).replace("\n", " ") for v in row] for row in view.to_numpy()]
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    out.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(out)


def required(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"missing required E293 artifact: {path}")
    return pd.read_csv(path)


def build_pair_rows(governor: pd.DataFrame, scores: pd.DataFrame, null_map: pd.DataFrame) -> pd.DataFrame:
    actual = scores[scores["basename"].isin(governor["basename"])].copy()
    actual["source_basename"] = actual["basename"]
    actual["placement_mode"] = "actual"
    actual["rep"] = -1
    actual["is_actual"] = 1

    nulls = scores[scores["basename"].isin(null_map["null_basename"])].merge(
        null_map,
        left_on="basename",
        right_on="null_basename",
        how="inner",
    )
    nulls["placement_mode"] = nulls["mode"].astype(str)
    nulls["is_actual"] = 0

    rows = pd.concat([actual, nulls], ignore_index=True, sort=False)
    return rows.merge(governor.add_prefix("src_"), left_on="source_basename", right_on="src_basename", how="left")


def numeric_feature_sets(rows: pd.DataFrame) -> dict[str, list[str]]:
    excluded = {
        "file",
        "source_path",
        "basename",
        "current_anchor",
        "promotion_decision",
        "source_basename",
        "placement_mode",
        "mode",
        "null_basename",
        "null_path",
        "rep",
        "is_actual",
    }
    numeric = [
        col
        for col in rows.columns
        if col not in excluded
        and not col.startswith("src_")
        and pd.api.types.is_numeric_dtype(rows[col])
    ]
    selector = [
        col
        for col in numeric
        if col.startswith("pred_delta")
        or col
        in {
            "pred_beats_current_rate",
            "incremental_bad_axis_vs_current",
            "bad_axis_abs_load",
            "bad_axis_positive_load",
            "good_axis_load",
            "good_span_residual_ratio",
            "bad_to_good_load_ratio",
            "raw05_a2c8_compat_energy",
        }
    ]
    anchor = [
        col
        for col in numeric
        if col.startswith("move_abs")
        or col.startswith("mean_prob")
        or col.startswith("proj_")
        or col.startswith("cos_")
        or col in {"min_prob", "max_prob", "mean_prob", "prob_span"}
    ]
    s4_local = [
        col
        for col in numeric
        if col.endswith("_S4")
        or col in {"mean_prob_S4", "move_abs_a2c8_S4"}
        or col.startswith("pred_delta")
        or col in {"pred_beats_current_rate", "incremental_bad_axis_vs_current"}
    ]
    return {
        "selector": selector,
        "anchor_geometry": anchor,
        "s4_local": s4_local,
        "all_output": numeric,
    }


def loo_actual_predictions(rows: pd.DataFrame, cols: list[str]) -> np.ndarray:
    pred = np.full(len(rows), np.nan, dtype=np.float64)
    for source in rows["source_basename"].dropna().unique():
        train_mask = rows["source_basename"].ne(source).to_numpy()
        test_mask = rows["source_basename"].eq(source).to_numpy()
        if rows.loc[train_mask, "is_actual"].nunique() < 2:
            continue
        model = make_pipeline(
            SimpleImputer(strategy="median"),
            StandardScaler(),
            LogisticRegression(max_iter=1000, class_weight="balanced", C=0.3, solver="liblinear"),
        )
        model.fit(rows.loc[train_mask, cols], rows.loc[train_mask, "is_actual"])
        pred[test_mask] = model.predict_proba(rows.loc[test_mask, cols])[:, 1]
    return pred


def safe_spearman(a: pd.Series, b: pd.Series) -> float:
    ok = a.notna() & b.notna()
    if int(ok.sum()) < 3 or a[ok].nunique() < 2 or b[ok].nunique() < 2:
        return np.nan
    return float(spearmanr(a[ok], b[ok]).correlation)


def summarize_feature_set(rows: pd.DataFrame, governor: pd.DataFrame, feature_name: str, cols: list[str]) -> tuple[dict[str, Any], pd.DataFrame]:
    pred = loo_actual_predictions(rows, cols)
    valid = ~np.isnan(pred)
    work = rows.loc[valid].copy()
    work["actual_realness"] = pred[valid]
    auc = float(roc_auc_score(work["is_actual"], work["actual_realness"]))

    source_rows: list[dict[str, Any]] = []
    for source, part in work.groupby("source_basename"):
        ordered = part.sort_values("actual_realness", ascending=False).reset_index(drop=True)
        actual_pos = int(np.flatnonzero(ordered["is_actual"].to_numpy() == 1)[0]) + 1
        actual_score = float(ordered.loc[ordered["is_actual"].eq(1), "actual_realness"].iloc[0])
        null_scores = ordered.loc[ordered["is_actual"].eq(0), "actual_realness"].to_numpy(dtype=np.float64)
        source_rows.append(
            {
                "basename": source,
                f"{feature_name}_realness": actual_score,
                f"{feature_name}_rank": actual_pos,
                f"{feature_name}_dominance": float(np.mean(actual_score > null_scores)) if len(null_scores) else np.nan,
            }
        )
    candidate_scores = pd.DataFrame(source_rows)
    merged = governor.merge(candidate_scores, on="basename", how="left")

    outcome_cols = [
        "null_strict_rate",
        "actual_p90",
        "actual_mean",
        "mean_dominance",
        "p90_dominance",
        "selected_rows",
        "selected_null_max_rate",
    ]
    summary: dict[str, Any] = {
        "feature_set": feature_name,
        "n_features": len(cols),
        "row_auc_actual_vs_null": auc,
        "mean_actual_rank": float(merged[f"{feature_name}_rank"].mean()),
        "top1_rate": float((merged[f"{feature_name}_rank"] == 1).mean()),
        "top3_rate": float((merged[f"{feature_name}_rank"] <= 3).mean()),
        "mean_actual_dominance": float(merged[f"{feature_name}_dominance"].mean()),
    }
    for col in outcome_cols:
        summary[f"spearman_realness_vs_{col}"] = safe_spearman(merged[f"{feature_name}_realness"], merged[col])
    return summary, candidate_scores


def actual_feature_percentiles(rows: pd.DataFrame) -> pd.DataFrame:
    checks = [
        ("pred_delta_vs_current_p90", "lower"),
        ("pred_delta_vs_current_mean", "lower"),
        ("pred_delta_vs_current_p10", "lower"),
        ("bad_axis_abs_load", "lower"),
        ("raw05_a2c8_compat_energy", "lower"),
        ("move_abs_a2c8_S4", "higher"),
        ("mean_prob_S4", "higher"),
    ]
    out_rows: list[dict[str, Any]] = []
    for col, direction in checks:
        if col not in rows.columns:
            continue
        vals: list[float] = []
        for _, part in rows.groupby("source_basename"):
            actual = part.loc[part["is_actual"].eq(1), col]
            nulls = part.loc[part["is_actual"].eq(0), col].to_numpy(dtype=np.float64)
            if actual.empty or len(nulls) == 0:
                continue
            aval = float(actual.iloc[0])
            if direction == "lower":
                vals.append(float(np.mean(aval < nulls)))
            else:
                vals.append(float(np.mean(aval > nulls)))
        arr = np.asarray(vals, dtype=np.float64)
        out_rows.append(
            {
                "feature": col,
                "actual_better_direction": direction,
                "mean_actual_better_than_null_rate": float(np.mean(arr)),
                "median_actual_better_than_null_rate": float(np.median(arr)),
                "source_rate_ge_0p8": float(np.mean(arr >= 0.80)),
                "source_rate_le_0p2": float(np.mean(arr <= 0.20)),
            }
        )
    return pd.DataFrame(out_rows).sort_values("mean_actual_better_than_null_rate", ascending=False).reset_index(drop=True)


def make_candidate_decisions(governor: pd.DataFrame, candidate_scores: pd.DataFrame) -> pd.DataFrame:
    out = governor.copy()
    for score in candidate_scores:
        out = out.merge(score, on="basename", how="left")
    if "all_output_realness" in out.columns:
        max_rows = max(float(out["selected_rows"].max()), 1.0)
        out["realness_safety_score"] = (
            out["all_output_realness"]
            - 0.50 * out["selected_null_max_rate"]
            - 0.10 * (out["selected_rows"] / max_rows)
        )
        out["realness_gate_public_free"] = (
            out["old_strict_promote"].astype(bool)
            & (out["all_output_dominance"] >= 0.80)
            & (out["null_strict_rate"] <= 0.10)
            & (out["mean_dominance"] >= 0.70)
            & (out["p90_dominance"] >= 0.80)
        )
    return out.sort_values(
        ["realness_gate_public_free", "realness_safety_score", "actual_p90"],
        ascending=[False, False, True],
    ).reset_index(drop=True)


def write_report(summary: pd.DataFrame, candidate_scores: pd.DataFrame, percentiles: pd.DataFrame) -> None:
    best = summary.sort_values("row_auc_actual_vs_null", ascending=False).iloc[0]
    ready_count = int(candidate_scores.get("realness_gate_public_free", pd.Series(dtype=bool)).fillna(False).sum())
    near = candidate_scores[
        candidate_scores["old_strict_promote"].astype(bool)
        & (candidate_scores["null_strict_rate"] <= 0.55)
    ].sort_values(["null_strict_rate", "actual_p90"])
    top_realness = candidate_scores.sort_values("all_output_realness", ascending=False)
    top_safety = candidate_scores.sort_values("realness_safety_score", ascending=False)
    lines = [
        "# E294 S4 Candidate-Level Invariant Audit",
        "",
        "## Question",
        "",
        "Can the real E293 S4 lifestyle placement be distinguished from matched row/subject/dateblock null placements before spending public LB?",
        "",
        "## Data",
        "",
        f"- E293 candidate sources: `{candidate_scores['basename'].nunique()}`",
        f"- matched null rows: `{int(candidate_scores['null_count'].sum())}`",
        "- public LB used: `0`",
        "",
        "## LOO Actual-vs-Null Distinguishability",
        "",
        md_table(
            summary[
                [
                    "feature_set",
                    "n_features",
                    "row_auc_actual_vs_null",
                    "mean_actual_rank",
                    "top1_rate",
                    "top3_rate",
                    "mean_actual_dominance",
                    "spearman_realness_vs_null_strict_rate",
                    "spearman_realness_vs_actual_p90",
                    "spearman_realness_vs_mean_dominance",
                ]
            ].sort_values("row_auc_actual_vs_null", ascending=False),
            n=10,
        ),
        "",
        "## Feature Percentiles",
        "",
        md_table(percentiles, n=20),
        "",
        "## Top Realness Candidates",
        "",
        md_table(
            top_realness[
                [
                    "basename",
                    "rule",
                    "scale",
                    "selected_rows",
                    "selected_null_max_rate",
                    "actual_p90",
                    "actual_mean",
                    "null_strict_rate",
                    "mean_dominance",
                    "all_output_realness",
                    "all_output_rank",
                    "all_output_dominance",
                    "final_decision",
                ]
            ],
            n=15,
        ),
        "",
        "## Top Safety-Adjusted Realness",
        "",
        md_table(
            top_safety[
                [
                    "basename",
                    "rule",
                    "scale",
                    "selected_rows",
                    "selected_null_max_rate",
                    "actual_p90",
                    "actual_mean",
                    "null_strict_rate",
                    "mean_dominance",
                    "realness_safety_score",
                    "final_decision",
                ]
            ],
            n=15,
        ),
        "",
        "## Near Low-Null Old-Strict Rows",
        "",
        md_table(
            near[
                [
                    "basename",
                    "rule",
                    "scale",
                    "selected_rows",
                    "selected_null_max_rate",
                    "actual_p90",
                    "actual_mean",
                    "null_strict_rate",
                    "p90_dominance",
                    "mean_dominance",
                    "all_output_realness",
                    "all_output_rank",
                    "final_decision",
                ]
            ],
            n=20,
        ),
        "",
        "## Decision",
        "",
    ]
    if ready_count:
        lines.append(f"`{ready_count}` candidate-level invariant rows pass the public-free realness gate. Review before submitting.")
    else:
        lines.append("No E294 candidate is public-free ready. Do not submit E293 S4 low-null files.")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"The best actual-vs-null classifier is `{best['feature_set']}` with AUC `{float(best['row_auc_actual_vs_null']):.6f}` and top3 rate `{float(best['top3_rate']):.6f}`. So the actual placement is visible in output/selector space.",
            "",
            "But that visibility is not a healthy LeJEPA gate. Realness is positively associated with null strict promotion, while the actual placement mainly beats nulls on p90 rather than mean. In plain terms: the model can recognize the designed S4 movement, but the recognizable part is also the part matched nulls can exploit.",
            "",
            "The S4 lifestyle state remains a diagnostic hidden state, not a submission tensor. The next useful experiment must change the target from `actual-vs-null identity` to `selector-visible and null-rare outcome`, or move to a new hidden-state axis with more positive examples.",
            "",
            "## Files",
            "",
            f"- `{SUMMARY_OUT.name}`",
            f"- `{CANDIDATE_OUT.name}`",
            f"- `{PERCENTILE_OUT.name}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    governor = required(GOVERNOR_IN)
    scores = required(SCORES_IN)
    null_map = required(NULL_MAP_IN)
    rows = build_pair_rows(governor, scores, null_map)
    feature_sets = numeric_feature_sets(rows)

    summary_rows: list[dict[str, Any]] = []
    score_parts: list[pd.DataFrame] = []
    for name, cols in feature_sets.items():
        if not cols:
            continue
        summary, candidate_part = summarize_feature_set(rows, governor, name, cols)
        summary_rows.append(summary)
        score_parts.append(candidate_part)

    summary = pd.DataFrame(summary_rows).sort_values("row_auc_actual_vs_null", ascending=False).reset_index(drop=True)
    percentiles = actual_feature_percentiles(rows)
    candidate_scores = make_candidate_decisions(governor, score_parts)

    summary.to_csv(SUMMARY_OUT, index=False)
    candidate_scores.to_csv(CANDIDATE_OUT, index=False)
    percentiles.to_csv(PERCENTILE_OUT, index=False)
    write_report(summary, candidate_scores, percentiles)

    print(f"feature_sets={len(summary)}")
    print(f"best_auc={summary['row_auc_actual_vs_null'].max():.6f}")
    print(f"best_feature_set={summary.iloc[0]['feature_set']}")
    print(f"public_ready={int(candidate_scores['realness_gate_public_free'].sum())}")
    print(f"report={REPORT_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
