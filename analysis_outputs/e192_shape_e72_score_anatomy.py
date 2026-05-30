#!/usr/bin/env python3
"""E192: anatomy of the clean shape-only E72 contamination score.

E191 left exactly one deployable-looking diagnostic: the filename-free
`shape_target_context_abs` E72-neighbor score. It was clean on the exact
E95/E101 boundary, but it still raised a mild alarm on some E144 pressure
branches while leaving E176 essentially untouched.

This script asks what that score is actually seeing. It does not create a
submission; it decomposes the score into contributions and nearest-neighbor
evidence so that the next branch decision has a falsifiable worldview behind it.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import sys
from typing import Any

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.metrics.pairwise import cosine_distances
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

import e186_antisymmetric_pair_decoder as e186  # noqa: E402
import e190_e72_contamination_detector as e190  # noqa: E402


SUMMARY_OUT = OUT / "e192_shape_e72_score_anatomy_summary.csv"
ROW_OUT = OUT / "e192_shape_e72_score_anatomy_row_audit.csv"
BRANCH_OUT = OUT / "e192_shape_e72_score_anatomy_branch_audit.csv"
NEAREST_OUT = OUT / "e192_shape_e72_score_anatomy_nearest_audit.csv"
CONTRIB_OUT = OUT / "e192_shape_e72_score_anatomy_contrib_audit.csv"
REPORT_OUT = OUT / "e192_shape_e72_score_anatomy_report.md"

VIEW_NAME = "shape_target_context_abs"
TARGET_RE = re.compile(r"_(Q1|Q2|Q3|S1|S2|S3|S4)_")
EPS = 1.0e-12


@dataclass(frozen=True)
class AnatomyModel:
    model: Pipeline
    cols: list[str]
    imputer: SimpleImputer
    scaler: StandardScaler
    clf: LogisticRegression


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


def make_model() -> Pipeline:
    return Pipeline(
        [
            ("impute", SimpleImputer(strategy="constant", fill_value=0.0)),
            ("scale", StandardScaler(with_mean=False)),
            ("clf", LogisticRegression(C=0.25, max_iter=5000, solver="lbfgs")),
        ]
    )


def load_known() -> pd.DataFrame:
    z, _ = e190.make_inputs()
    z["e72_neighbor_label"] = z["pair_is_e72_frontier_neighbor"].astype(int)
    return z


def view_cols(frame: pd.DataFrame) -> list[str]:
    view = next(v for v in e190.FEATURE_VIEWS if v.name == VIEW_NAME)
    return e190.feature_cols(frame, view)


def fit_anatomy_model(data: pd.DataFrame) -> AnatomyModel:
    cols = view_cols(data)
    model = make_model()
    model.fit(data[cols], data["e72_neighbor_label"])
    return AnatomyModel(
        model=model,
        cols=cols,
        imputer=model.named_steps["impute"],
        scaler=model.named_steps["scale"],
        clf=model.named_steps["clf"],
    )


def ensure_branch_cols(branches: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = branches.copy()
    for col in cols:
        if col not in out.columns:
            out[col] = 0.0
    return out


def transformed(am: AnatomyModel, frame: pd.DataFrame) -> np.ndarray:
    x_imp = am.imputer.transform(frame[am.cols])
    return am.scaler.transform(x_imp)


def predict_prob(am: AnatomyModel, frame: pd.DataFrame) -> np.ndarray:
    return am.model.predict_proba(frame[am.cols])[:, 1]


def feature_family(col: str) -> str:
    if col.startswith("abs__z__shape_"):
        return "shape"
    if col.startswith("abs__z__target_"):
        return "target"
    if col.startswith("abs__z__ctx_"):
        return "context"
    return "other"


def target_family(col: str) -> str:
    match = TARGET_RE.search(col)
    return match.group(1) if match else "no_target"


def contribution_frame(am: AnatomyModel, frame: pd.DataFrame, id_cols: list[str], source: str) -> pd.DataFrame:
    x = transformed(am, frame)
    coef = am.clf.coef_[0]
    contrib = x * coef
    rows: list[dict[str, Any]] = []
    for i, rec in enumerate(frame[id_cols].to_dict("records")):
        vals = contrib[i]
        order_pos = np.argsort(-vals)[:12]
        order_neg = np.argsort(vals)[:8]
        for rank, idx in enumerate(order_pos, start=1):
            rows.append(
                {
                    **rec,
                    "source": source,
                    "direction": "positive",
                    "rank": rank,
                    "feature": am.cols[idx],
                    "family": feature_family(am.cols[idx]),
                    "target_family": target_family(am.cols[idx]),
                    "value_scaled": float(x[i, idx]),
                    "coef": float(coef[idx]),
                    "contribution": float(vals[idx]),
                }
            )
        for rank, idx in enumerate(order_neg, start=1):
            rows.append(
                {
                    **rec,
                    "source": source,
                    "direction": "negative",
                    "rank": rank,
                    "feature": am.cols[idx],
                    "family": feature_family(am.cols[idx]),
                    "target_family": target_family(am.cols[idx]),
                    "value_scaled": float(x[i, idx]),
                    "coef": float(coef[idx]),
                    "contribution": float(vals[idx]),
                }
            )
    return pd.DataFrame(rows)


def group_contributions(am: AnatomyModel, frame: pd.DataFrame, id_cols: list[str]) -> pd.DataFrame:
    x = transformed(am, frame)
    coef = am.clf.coef_[0]
    contrib = x * coef
    rows: list[dict[str, Any]] = []
    families = np.array([feature_family(c) for c in am.cols])
    targets = np.array([target_family(c) for c in am.cols])
    for i, rec in enumerate(frame[id_cols].to_dict("records")):
        vals = contrib[i]
        base = {**rec, "logit_intercept": float(am.clf.intercept_[0]), "logit_sum": float(am.clf.intercept_[0] + vals.sum())}
        for fam in sorted(set(families)):
            mask = families == fam
            base[f"contrib_family_{fam}"] = float(vals[mask].sum())
            base[f"abscontrib_family_{fam}"] = float(np.abs(vals[mask]).sum())
        for tgt in ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4", "no_target"]:
            mask = targets == tgt
            base[f"contrib_target_{tgt}"] = float(vals[mask].sum()) if mask.any() else 0.0
            base[f"abscontrib_target_{tgt}"] = float(np.abs(vals[mask]).sum()) if mask.any() else 0.0
        rows.append(base)
    return pd.DataFrame(rows)


def nearest_known(am: AnatomyModel, known: pd.DataFrame, branches: pd.DataFrame, k: int = 8) -> pd.DataFrame:
    x_known = transformed(am, known)
    x_branch = transformed(am, branches)
    # The score uses non-centered, standardized absolute features; Euclidean
    # distance and cosine ask different questions, so keep both.
    euclid = np.sqrt(((x_branch[:, None, :] - x_known[None, :, :]) ** 2).sum(axis=2))
    cosine = cosine_distances(x_branch, x_known)
    rows: list[dict[str, Any]] = []
    known_probs = predict_prob(am, known)
    for i, branch in branches.iterrows():
        order = np.argsort(euclid[i])[:k]
        for rank, j in enumerate(order, start=1):
            row = known.iloc[j]
            rows.append(
                {
                    "candidate": branch["candidate"],
                    "scenario": branch["scenario"],
                    "branch_prob": float(branch["shape_e72_prob"]),
                    "rank": rank,
                    "euclidean": float(euclid[i, j]),
                    "cosine_distance": float(cosine[i, j]),
                    "known_prob": float(known_probs[j]),
                    "known_label": int(row["e72_neighbor_label"]),
                    "known_pair_context": row["pair_context"],
                    "known_pair_id": row["pair_id"],
                    "known_new_tag": row["new_tag"],
                    "known_base_tag": row["base_tag"],
                    "known_new_file": row["new_file"],
                    "known_base_file": row["base_file"],
                    "known_pair_is_e95_e101": bool(row["pair_is_e95_e101"]),
                    "known_actual_delta": float(row["actual_delta"]),
                }
            )
    return pd.DataFrame(rows)


def branch_summary(branches: pd.DataFrame, known: pd.DataFrame) -> pd.DataFrame:
    neg = known.loc[known["e72_neighbor_label"].eq(0), "shape_e72_prob"]
    pos = known.loc[known["e72_neighbor_label"].eq(1), "shape_e72_prob"]
    non_e72_p95 = float(np.quantile(neg, 0.95))
    non_e72_p99 = float(np.quantile(neg, 0.99))
    min_pos = float(pos.min())
    mean_pos = float(pos.mean())
    rows: list[dict[str, Any]] = []
    for (cand, scenario), part in branches.groupby(["candidate", "scenario"]):
        rec = part.iloc[0]
        rows.append(
            {
                "candidate": cand,
                "scenario": scenario,
                "n_diff_cells": int(rec["n_diff_cells"]),
                "top_targets": rec["top_targets"],
                "shape_e72_prob": float(rec["shape_e72_prob"]),
                "known_non_e72_p95": non_e72_p95,
                "known_non_e72_p99": non_e72_p99,
                "known_min_positive": min_pos,
                "known_mean_positive": mean_pos,
                "above_non_e72_p95": bool(rec["shape_e72_prob"] >= non_e72_p95),
                "above_non_e72_p99": bool(rec["shape_e72_prob"] >= non_e72_p99),
                "above_min_positive": bool(rec["shape_e72_prob"] >= min_pos),
            }
        )
    return pd.DataFrame(rows)


def summarize_known(known: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for name, part in known.groupby("pair_context"):
        rows.append(
            {
                "segment": name,
                "n": int(len(part)),
                "label_rate": float(part["e72_neighbor_label"].mean()),
                "prob_mean": float(part["shape_e72_prob"].mean()),
                "prob_max": float(part["shape_e72_prob"].max()),
                "prob_p95": float(np.quantile(part["shape_e72_prob"], 0.95)),
            }
        )
    special = {
        "exact_e95_e101": known["pair_is_e95_e101"],
        "e72_positive": known["e72_neighbor_label"].eq(1),
        "non_e72": known["e72_neighbor_label"].eq(0),
    }
    for name, mask in special.items():
        part = known.loc[mask]
        rows.append(
            {
                "segment": name,
                "n": int(len(part)),
                "label_rate": float(part["e72_neighbor_label"].mean()) if len(part) else np.nan,
                "prob_mean": float(part["shape_e72_prob"].mean()) if len(part) else np.nan,
                "prob_max": float(part["shape_e72_prob"].max()) if len(part) else np.nan,
                "prob_p95": float(np.quantile(part["shape_e72_prob"], 0.95)) if len(part) else np.nan,
            }
        )
    return pd.DataFrame(rows).sort_values(["prob_max", "prob_mean"], ascending=[False, False])


def write_report(
    summary: pd.DataFrame,
    row_scores: pd.DataFrame,
    branches: pd.DataFrame,
    nearest: pd.DataFrame,
    contrib: pd.DataFrame,
) -> None:
    live = (
        branches.groupby("candidate")
        .agg(
            scenario_count=("scenario", "count"),
            prob_mean=("shape_e72_prob", "mean"),
            prob_max=("shape_e72_prob", "max"),
            above_non_e72_p95_rate=("above_non_e72_p95", "mean"),
            above_non_e72_p99_rate=("above_non_e72_p99", "mean"),
            above_min_positive_rate=("above_min_positive", "mean"),
            n_diff_cells_mean=("n_diff_cells", "mean"),
        )
        .reset_index()
        .sort_values("prob_max", ascending=False)
    )
    branch_nearest = (
        nearest[nearest["rank"].le(3)]
        .groupby(["candidate", "scenario"])
        .agg(
            top3_label_rate=("known_label", "mean"),
            top3_exact_boundary_rate=("known_pair_is_e95_e101", "mean"),
            top3_contexts=("known_pair_context", lambda s: ",".join(s.astype(str).tolist())),
            top1_context=("known_pair_context", "first"),
            top1_label=("known_label", "first"),
            top1_prob=("known_prob", "first"),
            top1_euclidean=("euclidean", "first"),
        )
        .reset_index()
        .sort_values(["candidate", "scenario"])
    )
    branch_groups = branches.sort_values(["shape_e72_prob"], ascending=False)
    top_contrib = contrib[
        contrib["source"].eq("branch") & contrib["direction"].eq("positive") & contrib["rank"].le(5)
    ].sort_values(["candidate", "scenario", "rank"])
    exact = row_scores[row_scores["pair_is_e95_e101"]].copy()
    pos = row_scores[row_scores["e72_neighbor_label"].eq(1)].copy()
    y = row_scores["e72_neighbor_label"].to_numpy(dtype=int)
    p = row_scores["shape_e72_prob"].to_numpy(dtype=np.float64)
    auc = float(roc_auc_score(y, p)) if len(np.unique(y)) == 2 else np.nan
    ap = float(average_precision_score(y, p)) if len(np.unique(y)) == 2 else np.nan

    report = f"""# E192 Shape-Only E72 Score Anatomy

## Question

What does the clean `shape_target_context_abs` E72-neighbor score actually mark:
a deployable contamination motif, a generic tail anomaly, or an E144-specific
pressure artifact?

## Result In One Sentence

The full-data shape score separates known E72-neighbor rows from non-E72 rows
(AUC `{auc:.3f}`, AP `{ap:.3f}`), stays low on the exact E95/E101 boundary, and
keeps E176 far below even the non-E72 p95 threshold; the mild E144 alarm is a
target/shape tail signal rather than a support-gate rescue. Treat the perfect
full-data separation as anatomy only; E191's pair-LOO result is the stress
evidence.

## Known Segment Calibration

{md(summary, ['segment', 'n', 'label_rate', 'prob_mean', 'prob_max', 'prob_p95'], n=80)}

## Live Branch Summary

{md(live, ['candidate', 'scenario_count', 'prob_mean', 'prob_max', 'above_non_e72_p95_rate', 'above_non_e72_p99_rate', 'above_min_positive_rate', 'n_diff_cells_mean'], n=40)}

## Live Branch Detail

{md(branch_groups, ['candidate', 'scenario', 'shape_e72_prob', 'known_non_e72_p95', 'known_non_e72_p99', 'known_min_positive', 'above_non_e72_p95', 'above_non_e72_p99', 'above_min_positive', 'n_diff_cells', 'top_targets', 'contrib_family_shape', 'contrib_family_target', 'contrib_family_context', 'contrib_target_Q1', 'contrib_target_Q2', 'contrib_target_Q3', 'contrib_target_S2'], n=80)}

## Nearest Known Rows

{md(branch_nearest, ['candidate', 'scenario', 'top3_label_rate', 'top3_exact_boundary_rate', 'top3_contexts', 'top1_context', 'top1_label', 'top1_prob', 'top1_euclidean'], n=80)}

## Top Branch Contributions

{md(top_contrib, ['candidate', 'scenario', 'rank', 'feature', 'family', 'target_family', 'value_scaled', 'coef', 'contribution'], n=120)}

## Exact Boundary And Positive Anchors

Exact E95/E101 rows:

{md(exact.sort_values('shape_e72_prob', ascending=False), ['pair_id', 'new_tag', 'base_tag', 'pair_context', 'shape_e72_prob', 'actual_delta'], n=20)}

Known positive rows:

{md(pos.sort_values('shape_e72_prob', ascending=False), ['pair_id', 'new_tag', 'base_tag', 'pair_context', 'shape_e72_prob', 'actual_delta'], n=20)}

## Interpretation

- The clean score is not a support detector. E191 already killed that route,
  and E192 shows the remaining live pressure-branch signal is driven by
  target/shape contribution geometry. Branch context terms are zero in this
  pressure-frame view, so any live alarm must stand without context help.
- E144 crosses the non-E72 p95 in some scenarios, but it does not approach the
  known positive floor. Treat this as tail-risk evidence, not a direct
  contamination proof.
- E176 remains the least E72-like live branch under this score. This supports
  keeping E176 as the next broad shape/prior sensor instead of replacing it
  with an E144/E154 support-repair branch.

## Decision

No submission is created. The next submission sensor remains E176 unless a new
experiment finds a non-support mechanism that explains public sensitivity
better than this shape-safe branch ordering.
"""
    REPORT_OUT.write_text(report, encoding="utf-8")


def main() -> None:
    known = load_known()
    am = fit_anatomy_model(known)
    known["shape_e72_prob"] = predict_prob(am, known)

    branch_features = e186.branch_zrecords()
    branch_features = e190.abs_features(branch_features)
    branch_features = ensure_branch_cols(branch_features, am.cols)
    branch_features["shape_e72_prob"] = predict_prob(am, branch_features)

    b_summary = branch_summary(branch_features, known)
    grouped = group_contributions(am, branch_features, ["candidate", "scenario"])
    branches = b_summary.merge(grouped, on=["candidate", "scenario"], how="left")

    nearest = nearest_known(am, known, branch_features, k=8)
    branch_contrib = contribution_frame(am, branch_features, ["candidate", "scenario"], "branch")
    known_focus = known[known["e72_neighbor_label"].eq(1) | known["pair_is_e95_e101"]].copy()
    known_contrib = contribution_frame(
        am,
        known_focus,
        ["pair_id", "new_file", "base_file", "pair_context", "new_tag", "base_tag"],
        "known_focus",
    )
    contrib = pd.concat([branch_contrib, known_contrib], ignore_index=True)
    summary = summarize_known(known)

    row_cols = [
        "pair_id",
        "new_file",
        "base_file",
        "new_tag",
        "base_tag",
        "pair_context",
        "e72_neighbor_label",
        "pair_is_e95_e101",
        "actual_delta",
        "shape_e72_prob",
    ]
    row_scores = known[row_cols].copy()

    summary.to_csv(SUMMARY_OUT, index=False)
    row_scores.to_csv(ROW_OUT, index=False)
    branches.to_csv(BRANCH_OUT, index=False)
    nearest.to_csv(NEAREST_OUT, index=False)
    contrib.to_csv(CONTRIB_OUT, index=False)
    write_report(summary, row_scores, branches, nearest, contrib)

    print(f"Wrote {SUMMARY_OUT}")
    print(f"Wrote {ROW_OUT}")
    print(f"Wrote {BRANCH_OUT}")
    print(f"Wrote {NEAREST_OUT}")
    print(f"Wrote {CONTRIB_OUT}")
    print(f"Wrote {REPORT_OUT}")


if __name__ == "__main__":
    main()
