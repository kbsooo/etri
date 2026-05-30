#!/usr/bin/env python3
"""E186: antisymmetric repair of the E185 known-LB pair decoder.

E185 found pair-level structural signal, but also found reciprocal orientation
collapse: some models can assign high win probability to both A>B and B>A. This
audit asks whether the signal becomes action-grade after enforcing the minimal
LeJEPA-style geometry constraint:

    score(A, B) = -score(B, A)

No submission is created. If this fails, the pair-structural decoder is a coarse
public-quality classifier, not a branch selector.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

import e185_known_lb_pair_structural_decoder as e185  # noqa: E402


PAIR_FEATURES_IN = OUT / "e185_known_lb_pair_structural_decoder_features.csv"
Z_FEATURES_OUT = OUT / "e186_antisymmetric_pair_decoder_zfeatures.csv"
FILE_LOO_OUT = OUT / "e186_antisymmetric_pair_decoder_file_loo.csv"
PAIR_LOO_OUT = OUT / "e186_antisymmetric_pair_decoder_pair_loo.csv"
SUMMARY_OUT = OUT / "e186_antisymmetric_pair_decoder_summary.csv"
BRANCH_OUT = OUT / "e186_antisymmetric_pair_decoder_pressure_branches.csv"
REPORT_OUT = OUT / "e186_antisymmetric_pair_decoder_report.md"

EPS = 1.0e-12


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


def safe_auc(y: np.ndarray, p: np.ndarray) -> float:
    if len(np.unique(y)) < 2:
        return np.nan
    return float(roc_auc_score(y, p))


def make_model() -> Pipeline:
    return Pipeline(
        [
            ("scale", StandardScaler(with_mean=False)),
            (
                "clf",
                LogisticRegression(max_iter=5000, C=0.25, solver="lbfgs", fit_intercept=False),
            ),
        ]
    )


def feature_cols(features: pd.DataFrame, fs: e185.FeatureSet) -> list[str]:
    return e185.feature_columns(features, fs)


def build_zfeatures(features: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    all_feature_cols = sorted(
        {
            col
            for fs in e185.FEATURE_SETS
            for col in feature_cols(features, fs)
        }
    )
    values = features.copy()
    values[all_feature_cols] = values[all_feature_cols].fillna(0.0)
    for pair_id, part in values.groupby("pair_id"):
        if len(part) != 2:
            continue
        first, second = part.iloc[0], part.iloc[1]
        for row, other in [(first, second), (second, first)]:
            rec: dict[str, Any] = {
                "pair_id": pair_id,
                "new_file": row["new_file"],
                "base_file": row["base_file"],
                "actual_delta": float(row["actual_delta"]),
                "abs_actual_delta": float(row["abs_actual_delta"]),
                "actual_new_better": int(row["actual_new_better"]),
                "frontier_pair": bool(row["frontier_pair"]),
                "micro_pair": bool(row["micro_pair"]),
                "e95_edge_pair": bool(row["e95_edge_pair"]),
            }
            for col in all_feature_cols:
                rec[f"z__{col}"] = float(row[col] - other[col])
            rows.append(rec)
    return pd.DataFrame(rows)


def zcols(zfeatures: pd.DataFrame, fs: e185.FeatureSet) -> list[str]:
    raw_cols = feature_cols(pd.read_csv(PAIR_FEATURES_IN, nrows=5), fs)
    return [f"z__{col}" for col in raw_cols if f"z__{col}" in zfeatures.columns]


def evaluate(rows: list[dict[str, Any]], group_col: str, feature_set: str) -> dict[str, Any]:
    pred = pd.DataFrame(rows)
    y = pred["actual_new_better"].to_numpy(dtype=int)
    p = pred["prob_new_better"].to_numpy(dtype=np.float64)
    out: dict[str, Any] = {
        "feature_set": feature_set,
        "group_col": group_col,
        "n_rows": int(len(pred)),
        "n_groups": int(pred["heldout"].nunique()),
        "accuracy": float(np.mean((p >= 0.5) == y)),
        "auc": safe_auc(y, p),
        "logloss": float(log_loss(y, np.clip(p, EPS, 1.0 - EPS), labels=[0, 1])),
        "brier": float(brier_score_loss(y, np.clip(p, EPS, 1.0 - EPS))),
    }
    for flag, name in [
        ("frontier_pair", "frontier"),
        ("micro_pair", "micro"),
        ("e95_edge_pair", "e95_edge"),
    ]:
        if flag in pred.columns and pred[flag].any():
            yy = pred.loc[pred[flag], "actual_new_better"].to_numpy(dtype=int)
            pp = pred.loc[pred[flag], "prob_new_better"].to_numpy(dtype=np.float64)
            out[f"{name}_n"] = int(len(yy))
            out[f"{name}_accuracy"] = float(np.mean((pp >= 0.5) == yy))
            out[f"{name}_auc"] = safe_auc(yy, pp)
            out[f"{name}_logloss"] = float(log_loss(yy, np.clip(pp, EPS, 1.0 - EPS), labels=[0, 1]))
        else:
            out[f"{name}_n"] = 0
            out[f"{name}_accuracy"] = np.nan
            out[f"{name}_auc"] = np.nan
            out[f"{name}_logloss"] = np.nan
    # By construction and fit_intercept=False, reciprocal MAE is zero up to
    # numerical precision if the same model is evaluated on both orientations.
    recip = []
    for _, part in pred.groupby(["heldout", "pair_id"]):
        if len(part) == 2:
            recip.append(abs(float(part["prob_new_better"].sum()) - 1.0))
    out["reciprocity_mae"] = float(np.mean(recip)) if recip else np.nan
    return out


def file_loo(zfeatures: pd.DataFrame, fs: e185.FeatureSet) -> tuple[pd.DataFrame, dict[str, Any]]:
    cols = zcols(zfeatures, fs)
    rows: list[dict[str, Any]] = []
    for held_file in sorted(set(zfeatures["new_file"]).union(set(zfeatures["base_file"]))):
        test_mask = zfeatures["new_file"].eq(held_file) | zfeatures["base_file"].eq(held_file)
        train = zfeatures.loc[~test_mask].copy()
        test = zfeatures.loc[test_mask].copy()
        if train["actual_new_better"].nunique() < 2 or test.empty:
            continue
        model = make_model()
        model.fit(train[cols], train["actual_new_better"])
        prob = model.predict_proba(test[cols])[:, 1]
        for rec, p in zip(test.to_dict("records"), prob):
            rows.append(
                {
                    "feature_set": fs.name,
                    "heldout": held_file,
                    "pair_id": rec["pair_id"],
                    "new_file": rec["new_file"],
                    "base_file": rec["base_file"],
                    "actual_delta": rec["actual_delta"],
                    "abs_actual_delta": rec["abs_actual_delta"],
                    "actual_new_better": rec["actual_new_better"],
                    "prob_new_better": float(p),
                    "correct": bool((p >= 0.5) == bool(rec["actual_new_better"])),
                    "frontier_pair": bool(rec["frontier_pair"]),
                    "micro_pair": bool(rec["micro_pair"]),
                    "e95_edge_pair": bool(rec["e95_edge_pair"]),
                }
            )
    return pd.DataFrame(rows), evaluate(rows, "file", fs.name)


def pair_loo(zfeatures: pd.DataFrame, fs: e185.FeatureSet) -> tuple[pd.DataFrame, dict[str, Any]]:
    cols = zcols(zfeatures, fs)
    rows: list[dict[str, Any]] = []
    for pair_id in sorted(zfeatures["pair_id"].unique()):
        test_mask = zfeatures["pair_id"].eq(pair_id)
        train = zfeatures.loc[~test_mask].copy()
        test = zfeatures.loc[test_mask].copy()
        if train["actual_new_better"].nunique() < 2 or test.empty:
            continue
        model = make_model()
        model.fit(train[cols], train["actual_new_better"])
        prob = model.predict_proba(test[cols])[:, 1]
        for rec, p in zip(test.to_dict("records"), prob):
            rows.append(
                {
                    "feature_set": fs.name,
                    "heldout": pair_id,
                    "pair_id": rec["pair_id"],
                    "new_file": rec["new_file"],
                    "base_file": rec["base_file"],
                    "actual_delta": rec["actual_delta"],
                    "abs_actual_delta": rec["abs_actual_delta"],
                    "actual_new_better": rec["actual_new_better"],
                    "prob_new_better": float(p),
                    "correct": bool((p >= 0.5) == bool(rec["actual_new_better"])),
                    "frontier_pair": bool(rec["frontier_pair"]),
                    "micro_pair": bool(rec["micro_pair"]),
                    "e95_edge_pair": bool(rec["e95_edge_pair"]),
                }
            )
    return pd.DataFrame(rows), evaluate(rows, "pair", fs.name)


def branch_zrecords() -> pd.DataFrame:
    cells = e185.pressure_branch_frame()
    rows: list[dict[str, Any]] = []
    for (candidate, scenario), part in cells.groupby(["candidate", "scenario"]):
        min_rec: dict[str, Any] = {
            "pair_id": f"{candidate}_{scenario}_min_vs_max",
            "new_file": f"{candidate}_pressure_min",
            "base_file": f"{candidate}_pressure_max",
            "actual_delta": np.nan,
            "abs_actual_delta": np.nan,
            "actual_new_better": np.nan,
            "frontier_pair": False,
            "micro_pair": False,
            "e95_edge_pair": False,
        }
        max_rec = dict(min_rec)
        for set_name in e185.SETS:
            e185.add_set_features(min_rec, part.copy(), set_name, reverse=False)
            e185.add_set_features(max_rec, part.copy(), set_name, reverse=True)
        rec: dict[str, Any] = {
            "candidate": candidate,
            "scenario": scenario,
            "n_diff_cells": int(len(part)),
            "top_targets": ",".join(part.sort_values("swing", ascending=False)["target"].head(4).tolist()),
        }
        for col in sorted(set(min_rec).union(max_rec)):
            if any(col.startswith(prefix) for fs in e185.FEATURE_SETS for prefix in fs.include_prefixes):
                rec[f"z__{col}"] = float(min_rec.get(col, 0.0) or 0.0) - float(max_rec.get(col, 0.0) or 0.0)
        rows.append(rec)
    return pd.DataFrame(rows)


def score_branches(zfeatures: pd.DataFrame, fs: e185.FeatureSet) -> pd.DataFrame:
    cols = zcols(zfeatures, fs)
    model = make_model()
    model.fit(zfeatures[cols], zfeatures["actual_new_better"])
    branches = branch_zrecords()
    prob = model.predict_proba(branches[cols])[:, 1]
    out = branches[["candidate", "scenario", "n_diff_cells", "top_targets"]].copy()
    out.insert(0, "feature_set", fs.name)
    out["prob_pressure_min_public_better"] = prob
    out["prefers_favorable_min"] = out["prob_pressure_min_public_better"] >= 0.5
    return out


def summarize_branches(branches: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (fs, candidate), part in branches.groupby(["feature_set", "candidate"]):
        rows.append(
            {
                "feature_set": fs,
                "candidate": candidate,
                "scenario_count": int(len(part)),
                "prefers_favorable_min_rate": float(part["prefers_favorable_min"].mean()),
                "prob_mean": float(part["prob_pressure_min_public_better"].mean()),
                "prob_min": float(part["prob_pressure_min_public_better"].min()),
                "prob_max": float(part["prob_pressure_min_public_better"].max()),
            }
        )
    return pd.DataFrame(rows)


def write_report(summary: pd.DataFrame, file_pred: pd.DataFrame, pair_pred: pd.DataFrame, branches: pd.DataFrame) -> None:
    best_file = summary[summary["group_col"].eq("file")].sort_values(
        ["e95_edge_accuracy", "frontier_accuracy", "accuracy", "auc"], ascending=False
    ).iloc[0]
    best_pair = summary[summary["group_col"].eq("pair")].sort_values(
        ["e95_edge_accuracy", "frontier_accuracy", "accuracy", "auc"], ascending=False
    ).iloc[0]
    branch_summary = summarize_branches(branches)
    hard_file = file_pred[file_pred["e95_edge_pair"]].copy()
    hard_pair = pair_pred[pair_pred["e95_edge_pair"]].copy()

    cols_summary = [
        "feature_set",
        "group_col",
        "n_rows",
        "n_groups",
        "accuracy",
        "auc",
        "logloss",
        "frontier_n",
        "frontier_accuracy",
        "frontier_auc",
        "micro_n",
        "micro_accuracy",
        "e95_edge_n",
        "e95_edge_accuracy",
        "reciprocity_mae",
    ]
    cols_pred = [
        "feature_set",
        "heldout",
        "new_file",
        "base_file",
        "actual_delta",
        "prob_new_better",
        "correct",
        "frontier_pair",
        "micro_pair",
        "e95_edge_pair",
    ]
    cols_branch = [
        "feature_set",
        "candidate",
        "scenario_count",
        "prefers_favorable_min_rate",
        "prob_mean",
        "prob_min",
        "prob_max",
    ]
    cols_branch_detail = [
        "feature_set",
        "candidate",
        "scenario",
        "prob_pressure_min_public_better",
        "prefers_favorable_min",
        "n_diff_cells",
        "top_targets",
    ]

    report = f"""# E186 Antisymmetric Pair Decoder

## Question

E185 found pair-level public signal but also reciprocal orientation collapse.
Does enforcing `score(A,B)=-score(B,A)` turn that signal into an action-grade
frontier selector?

## Result In One Sentence

The best antisymmetric leave-one-file decoder is `{best_file['feature_set']}`
with overall accuracy `{float(best_file['accuracy']):.3f}`, frontier accuracy
`{float(best_file['frontier_accuracy']):.3f}`, and E95-edge-band accuracy
`{float(best_file['e95_edge_accuracy']):.3f}`. The best leave-one-pair decoder is
`{best_pair['feature_set']}` with E95-edge-band accuracy
`{float(best_pair['e95_edge_accuracy']):.3f}`. Reciprocity is fixed by
construction, so any remaining miss is selector signal, not orientation
geometry.

## Decoder Stress Summary

{md(summary.sort_values(["group_col", "e95_edge_accuracy", "frontier_accuracy", "accuracy"], ascending=[True, False, False, False]), cols_summary, n=20)}

## E95-Edge-Band File-LOO Predictions

{md(hard_file.sort_values(["feature_set", "abs_actual_delta"]), cols_pred, n=80)}

## E95-Edge-Band Pair-LOO Predictions

{md(hard_pair.sort_values(["feature_set", "abs_actual_delta"]), cols_pred, n=80)}

## Pressure-Branch Scores

{md(branch_summary.sort_values(["feature_set", "candidate"]), cols_branch, n=40)}

## Pressure-Branch Detail

{md(branches.sort_values(["feature_set", "candidate", "scenario"]), cols_branch_detail, n=80)}

## Interpretation

- If E186 improves edge-band stress versus E185, the main missing ingredient was
  reciprocal geometry, not raw signal.
- If E186 keeps weak edge-band stress or unstable branch scores, pair-level
  known-LB structure remains too coarse for E176/E154/E144 selection.
- A pressure-branch decision is action-grade only if it is stable across
  feature sets and survives leave-one-file frontier stress.

## Decision

No submission is created. This audit decides whether the next step should be a
geometry-constrained decoder or a different latent target entirely.
"""
    REPORT_OUT.write_text(report, encoding="utf-8")


def run() -> None:
    if not PAIR_FEATURES_IN.exists():
        known = e185.load_known_scores()
        e185.build_oriented_pair_features(known).to_csv(PAIR_FEATURES_IN, index=False)
    features = pd.read_csv(PAIR_FEATURES_IN)
    zfeatures = build_zfeatures(features)
    zfeatures.to_csv(Z_FEATURES_OUT, index=False)

    file_rows: list[pd.DataFrame] = []
    pair_rows: list[pd.DataFrame] = []
    summaries: list[dict[str, Any]] = []
    branch_rows: list[pd.DataFrame] = []
    for fs in e185.FEATURE_SETS:
        f_pred, f_summary = file_loo(zfeatures, fs)
        p_pred, p_summary = pair_loo(zfeatures, fs)
        file_rows.append(f_pred)
        pair_rows.append(p_pred)
        summaries.extend([f_summary, p_summary])
        branch_rows.append(score_branches(zfeatures, fs))

    file_pred = pd.concat(file_rows, ignore_index=True)
    pair_pred = pd.concat(pair_rows, ignore_index=True)
    summary = pd.DataFrame(summaries)
    branches = pd.concat(branch_rows, ignore_index=True)

    file_pred.to_csv(FILE_LOO_OUT, index=False)
    pair_pred.to_csv(PAIR_LOO_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    branches.to_csv(BRANCH_OUT, index=False)
    write_report(summary, file_pred, pair_pred, branches)

    print(Z_FEATURES_OUT)
    print(FILE_LOO_OUT)
    print(PAIR_LOO_OUT)
    print(SUMMARY_OUT)
    print(BRANCH_OUT)
    print(REPORT_OUT)


if __name__ == "__main__":
    run()
