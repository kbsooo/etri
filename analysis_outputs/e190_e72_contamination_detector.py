#!/usr/bin/env python3
"""E190: filename-free E72 contamination detector stress.

E189 showed that support's useful E95-edge rescues are E72-neighbor rows, while
shape-only owns the exact E95/E101 boundary. This script asks whether that
distinction is only filename identity or whether movement anatomy can detect
"E72 contamination" without using file names as model inputs.

This is a diagnostic experiment, not a submission generator.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, log_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

import e186_antisymmetric_pair_decoder as e186  # noqa: E402


Z_IN = OUT / "e186_antisymmetric_pair_decoder_zfeatures.csv"
ROW_AUDIT_IN = OUT / "e189_shape_support_disagreement_atlas_row_audit.csv"
BRANCH_SCORES_IN = OUT / "e187_e95_e101_boundary_miss_anatomy_branch_scores.csv"

SUMMARY_OUT = OUT / "e190_e72_contamination_detector_summary.csv"
PRED_OUT = OUT / "e190_e72_contamination_detector_oof_predictions.csv"
BRANCH_OUT = OUT / "e190_e72_contamination_detector_branch_scores.csv"
FEATURE_OUT = OUT / "e190_e72_contamination_detector_feature_audit.csv"
REPORT_OUT = OUT / "e190_e72_contamination_detector_report.md"

EPS = 1.0e-12

E72 = "submission_e72_topabs50_q2s3_gate_4e48cba2.csv"
E95 = "submission_e95_hardtail_541e3973.csv"
E101 = "submission_e101_q2s3tail_177569bc.csv"
MIXMIN = "submission_mixmin_0c916bb4.csv"


@dataclass(frozen=True)
class FeatureView:
    name: str
    prefixes: tuple[str, ...]


FEATURE_VIEWS = (
    FeatureView("shape_target_context_abs", ("abs__z__shape_", "abs__z__target_", "abs__z__ctx_")),
    FeatureView("support_abs", ("abs__z__sup_",)),
    FeatureView("shape_target_context_support_abs", ("abs__z__shape_", "abs__z__target_", "abs__z__ctx_", "abs__z__sup_")),
    FeatureView("all_axis_free_abs", ("abs__z__shape_", "abs__z__target_", "abs__z__ctx_", "abs__z__sup_")),
    FeatureView("all_abs", ("abs__z__",)),
)


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


def file_tag(file_name: str) -> str:
    name = file_name.lower()
    if file_name == E95:
        return "e95"
    if file_name == E101:
        return "e101"
    if file_name == E72:
        return "e72"
    if file_name == MIXMIN:
        return "mixmin"
    if "frontier_cvjepa" in name:
        return "a2c8_frontier"
    if "raw_timeline" in name:
        return "raw_jepa"
    if "lejepa" in name:
        return "bad_lejepa"
    if "ordinal" in name:
        return "ordinal"
    if "hybrid_0p578" in name:
        return "hybrid_final9"
    if "hybrid_0p567" in name:
        return "hybrid_stage2"
    if "jepa_latent" in name:
        return "jepa_latent"
    return "other"


def pair_context(new_file: str, base_file: str) -> str:
    return "__".join(sorted([file_tag(new_file), file_tag(base_file)]))


def add_pair_flags(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["new_tag"] = out["new_file"].map(file_tag)
    out["base_tag"] = out["base_file"].map(file_tag)
    out["pair_context"] = [pair_context(n, b) for n, b in zip(out["new_file"], out["base_file"])]
    out["pair_has_e72"] = out["new_file"].eq(E72) | out["base_file"].eq(E72)
    out["pair_has_e95"] = out["new_file"].eq(E95) | out["base_file"].eq(E95)
    out["pair_has_e101"] = out["new_file"].eq(E101) | out["base_file"].eq(E101)
    out["pair_has_mixmin"] = out["new_file"].eq(MIXMIN) | out["base_file"].eq(MIXMIN)
    out["pair_is_e95_e101"] = (
        (out["new_file"].eq(E95) & out["base_file"].eq(E101))
        | (out["new_file"].eq(E101) & out["base_file"].eq(E95))
    )
    out["pair_is_e72_frontier_neighbor"] = out["pair_has_e72"] & (
        out["pair_has_e95"] | out["pair_has_e101"] | out["pair_has_mixmin"]
    )
    return out


def abs_features(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    for col in [c for c in frame.columns if c.startswith("z__")]:
        out[f"abs__{col}"] = pd.to_numeric(frame[col], errors="coerce").fillna(0.0).abs()
    return out


def feature_cols(frame: pd.DataFrame, view: FeatureView) -> list[str]:
    return [c for c in frame.columns if any(c.startswith(prefix) for prefix in view.prefixes)]


def make_model() -> Pipeline:
    return Pipeline(
        [
            ("impute", SimpleImputer(strategy="constant", fill_value=0.0)),
            ("scale", StandardScaler(with_mean=False)),
            (
                "clf",
                LogisticRegression(
                    C=0.25,
                    class_weight="balanced",
                    max_iter=5000,
                    solver="lbfgs",
                ),
            ),
        ]
    )


def safe_auc(y: np.ndarray, p: np.ndarray) -> float:
    if len(np.unique(y)) < 2:
        return np.nan
    return float(roc_auc_score(y, p))


def safe_ap(y: np.ndarray, p: np.ndarray) -> float:
    if len(np.unique(y)) < 2:
        return np.nan
    return float(average_precision_score(y, p))


def topk_recall(y: np.ndarray, p: np.ndarray) -> tuple[float, float]:
    positives = int(y.sum())
    if positives == 0:
        return np.nan, np.nan
    order = np.argsort(-p)[:positives]
    precision = float(y[order].mean())
    recall = float(y[order].sum() / positives)
    return precision, recall


def metric_record(task: str, view: str, split: str, pred: pd.DataFrame) -> dict[str, Any]:
    y = pred["label"].to_numpy(dtype=int)
    p = pred["prob"].to_numpy(dtype=np.float64)
    top_prec, top_rec = topk_recall(y, p)
    out: dict[str, Any] = {
        "task": task,
        "feature_view": view,
        "split": split,
        "n_rows": int(len(pred)),
        "n_pos": int(y.sum()),
        "auc": safe_auc(y, p),
        "avg_precision": safe_ap(y, p),
        "logloss": float(log_loss(y, np.clip(p, EPS, 1.0 - EPS), labels=[0, 1]))
        if len(np.unique(y)) > 1
        else np.nan,
        "topk_precision": top_prec,
        "topk_recall": top_rec,
    }
    if "pair_is_e95_e101" in pred.columns and pred["pair_is_e95_e101"].any():
        out["exact_e95_e101_mean_prob"] = float(pred.loc[pred["pair_is_e95_e101"], "prob"].mean())
    else:
        out["exact_e95_e101_mean_prob"] = np.nan
    return out


def grouped_oof(
    data: pd.DataFrame,
    label_col: str,
    view: FeatureView,
    group_col: str,
    task: str,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    cols = feature_cols(data, view)
    rows: list[dict[str, Any]] = []
    for group in sorted(data[group_col].dropna().unique()):
        test_mask = data[group_col].eq(group)
        train = data.loc[~test_mask].copy()
        test = data.loc[test_mask].copy()
        if train[label_col].nunique() < 2 or test.empty:
            for rec in test.to_dict("records"):
                rows.append(
                    {
                        "task": task,
                        "feature_view": view.name,
                        "split": f"loo_{group_col}",
                        "heldout": group,
                        "pair_id": rec.get("pair_id"),
                        "new_file": rec.get("new_file"),
                        "base_file": rec.get("base_file"),
                        "pair_context": rec.get("pair_context"),
                        "label": int(rec[label_col]),
                        "prob": np.nan,
                        "skipped": True,
                        "pair_is_e72_frontier_neighbor": bool(rec.get("pair_is_e72_frontier_neighbor", False)),
                        "pair_is_e95_e101": bool(rec.get("pair_is_e95_e101", False)),
                    }
                )
            continue
        model = make_model()
        model.fit(train[cols], train[label_col])
        prob = model.predict_proba(test[cols])[:, 1]
        for rec, p in zip(test.to_dict("records"), prob):
            rows.append(
                {
                    "task": task,
                    "feature_view": view.name,
                    "split": f"loo_{group_col}",
                    "heldout": group,
                    "pair_id": rec.get("pair_id"),
                    "new_file": rec.get("new_file"),
                    "base_file": rec.get("base_file"),
                    "pair_context": rec.get("pair_context"),
                    "label": int(rec[label_col]),
                    "prob": float(p),
                    "skipped": False,
                    "pair_is_e72_frontier_neighbor": bool(rec.get("pair_is_e72_frontier_neighbor", False)),
                    "pair_is_e95_e101": bool(rec.get("pair_is_e95_e101", False)),
                }
            )
    pred = pd.DataFrame(rows)
    valid = pred[~pred["skipped"] & pred["prob"].notna()].copy()
    summary = metric_record(task, view.name, f"loo_{group_col}", valid) if not valid.empty else {
        "task": task,
        "feature_view": view.name,
        "split": f"loo_{group_col}",
        "n_rows": 0,
        "n_pos": 0,
        "auc": np.nan,
        "avg_precision": np.nan,
        "logloss": np.nan,
        "topk_precision": np.nan,
        "topk_recall": np.nan,
        "exact_e95_e101_mean_prob": np.nan,
    }
    summary["skipped_rows"] = int(pred["skipped"].sum()) if not pred.empty else 0
    summary["n_groups"] = int(data[group_col].nunique())
    return pred, summary


def any_file_oof(
    data: pd.DataFrame,
    label_col: str,
    view: FeatureView,
    task: str,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    cols = feature_cols(data, view)
    files = sorted(set(data["new_file"]).union(set(data["base_file"])))
    rows: list[dict[str, Any]] = []
    for file_name in files:
        test_mask = data["new_file"].eq(file_name) | data["base_file"].eq(file_name)
        train = data.loc[~test_mask].copy()
        test = data.loc[test_mask].copy()
        if train[label_col].nunique() < 2 or test.empty:
            for rec in test.to_dict("records"):
                rows.append(
                    {
                        "task": task,
                        "feature_view": view.name,
                        "split": "loo_any_file",
                        "heldout": file_name,
                        "pair_id": rec.get("pair_id"),
                        "new_file": rec.get("new_file"),
                        "base_file": rec.get("base_file"),
                        "pair_context": rec.get("pair_context"),
                        "label": int(rec[label_col]),
                        "prob": np.nan,
                        "skipped": True,
                        "pair_is_e72_frontier_neighbor": bool(rec.get("pair_is_e72_frontier_neighbor", False)),
                        "pair_is_e95_e101": bool(rec.get("pair_is_e95_e101", False)),
                    }
                )
            continue
        model = make_model()
        model.fit(train[cols], train[label_col])
        prob = model.predict_proba(test[cols])[:, 1]
        for rec, p in zip(test.to_dict("records"), prob):
            rows.append(
                {
                    "task": task,
                    "feature_view": view.name,
                    "split": "loo_any_file",
                    "heldout": file_name,
                    "pair_id": rec.get("pair_id"),
                    "new_file": rec.get("new_file"),
                    "base_file": rec.get("base_file"),
                    "pair_context": rec.get("pair_context"),
                    "label": int(rec[label_col]),
                    "prob": float(p),
                    "skipped": False,
                    "pair_is_e72_frontier_neighbor": bool(rec.get("pair_is_e72_frontier_neighbor", False)),
                    "pair_is_e95_e101": bool(rec.get("pair_is_e95_e101", False)),
                }
            )
    pred = pd.DataFrame(rows)
    valid = pred[~pred["skipped"] & pred["prob"].notna()].copy()
    summary = metric_record(task, view.name, "loo_any_file", valid) if not valid.empty else {
        "task": task,
        "feature_view": view.name,
        "split": "loo_any_file",
        "n_rows": 0,
        "n_pos": 0,
        "auc": np.nan,
        "avg_precision": np.nan,
        "logloss": np.nan,
        "topk_precision": np.nan,
        "topk_recall": np.nan,
        "exact_e95_e101_mean_prob": np.nan,
    }
    summary["skipped_rows"] = int(pred["skipped"].sum()) if not pred.empty else 0
    summary["n_groups"] = int(len(files))
    summary["skipped_positive_rows"] = int(pred.loc[pred["skipped"], "label"].sum()) if not pred.empty else 0
    return pred, summary


def make_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    z = pd.read_csv(Z_IN)
    z = add_pair_flags(z)
    z = abs_features(z)

    audit = pd.read_csv(ROW_AUDIT_IN)
    primary = audit[audit["support_variant"].eq("shape_support") & audit["e95_edge_pair"]].copy()
    primary["support_needed_label"] = primary["disagreement_class"].eq("support_rescue").astype(int)
    primary = primary[primary["disagreement_class"].isin(["support_rescue", "shape_only_win"])].copy()
    primary = add_pair_flags(primary)
    primary = primary.merge(
        z[["pair_id", "new_file", "base_file"] + [c for c in z.columns if c.startswith("abs__z__")]],
        on=["pair_id", "new_file", "base_file"],
        how="left",
    )
    return z, primary


def feature_audit(data: pd.DataFrame, label_col: str, task: str) -> pd.DataFrame:
    y = data[label_col].to_numpy(dtype=int)
    rows: list[dict[str, Any]] = []
    for col in [c for c in data.columns if c.startswith("abs__z__")]:
        x = pd.to_numeric(data[col], errors="coerce").fillna(0.0).to_numpy(dtype=np.float64)
        if np.std(x) == 0 or len(np.unique(y)) < 2:
            continue
        auc = roc_auc_score(y, x)
        signed_auc = float(auc)
        auc = max(float(auc), float(1.0 - auc))
        rows.append(
            {
                "task": task,
                "feature": col,
                "auc_abs_directionless": auc,
                "signed_auc": signed_auc,
                "positive_mean": float(x[y == 1].mean()) if y.sum() else np.nan,
                "negative_mean": float(x[y == 0].mean()) if (1 - y).sum() else np.nan,
                "mean_diff_pos_minus_neg": float(x[y == 1].mean() - x[y == 0].mean())
                if y.sum() and (1 - y).sum()
                else np.nan,
            }
        )
    return pd.DataFrame(rows).sort_values(["auc_abs_directionless", "feature"], ascending=[False, True])


def fit_full_and_score_branches(train: pd.DataFrame, label_col: str) -> pd.DataFrame:
    branches = e186.branch_zrecords()
    branches = abs_features(branches)
    out_rows: list[pd.DataFrame] = []
    branch_probs = pd.read_csv(BRANCH_SCORES_IN)
    shape_branch = branch_probs[branch_probs["variant"].eq("shape_only")][
        ["candidate", "scenario", "prob_pressure_min_public_better"]
    ].rename(columns={"prob_pressure_min_public_better": "shape_prob"})
    support_branch = branch_probs[branch_probs["variant"].eq("shape_support")][
        ["candidate", "scenario", "prob_pressure_min_public_better"]
    ].rename(columns={"prob_pressure_min_public_better": "support_prob"})

    for view in FEATURE_VIEWS:
        cols = feature_cols(train, view)
        model = make_model()
        model.fit(train[cols], train[label_col])
        score_frame = branches.copy()
        for col in cols:
            if col not in score_frame.columns:
                score_frame[col] = 0.0
        known_prob = model.predict_proba(train[cols])[:, 1]
        non_e72 = known_prob[train[label_col].to_numpy(dtype=int) == 0]
        pos = known_prob[train[label_col].to_numpy(dtype=int) == 1]
        non_e72_p95 = float(np.quantile(non_e72, 0.95)) if len(non_e72) else np.nan
        min_positive = float(pos.min()) if len(pos) else np.nan
        branch_prob = model.predict_proba(score_frame[cols])[:, 1]
        rec = branches[["candidate", "scenario", "n_diff_cells", "top_targets"]].copy()
        rec.insert(0, "feature_view", view.name)
        rec["e72_contam_prob"] = branch_prob
        rec["known_non_e72_p95"] = non_e72_p95
        rec["known_min_positive"] = min_positive
        rec["above_non_e72_p95"] = rec["e72_contam_prob"] >= non_e72_p95
        rec["above_min_positive"] = rec["e72_contam_prob"] >= min_positive
        rec = rec.merge(shape_branch, on=["candidate", "scenario"], how="left")
        rec = rec.merge(support_branch, on=["candidate", "scenario"], how="left")
        rec["support_minus_shape_prob"] = rec["support_prob"] - rec["shape_prob"]
        out_rows.append(rec)
    return pd.concat(out_rows, ignore_index=True)


def write_report(summary: pd.DataFrame, preds: pd.DataFrame, branches: pd.DataFrame, features: pd.DataFrame) -> None:
    e72_summary = summary[summary["task"].eq("e72_frontier_neighbor")].sort_values(
        ["split", "auc", "avg_precision"], ascending=[True, False, False]
    )
    support_summary = summary[summary["task"].eq("support_needed_e95_edge")].sort_values(
        ["split", "auc", "avg_precision"], ascending=[True, False, False]
    )
    branch_view = branches.sort_values(
        ["feature_view", "e72_contam_prob"], ascending=[True, False]
    )
    live_branch = branches.groupby(["feature_view", "candidate"]).agg(
        scenario_count=("scenario", "count"),
        contam_prob_mean=("e72_contam_prob", "mean"),
        contam_prob_max=("e72_contam_prob", "max"),
        above_non_e72_p95_rate=("above_non_e72_p95", "mean"),
        above_min_positive_rate=("above_min_positive", "mean"),
        support_minus_shape_mean=("support_minus_shape_prob", "mean"),
    ).reset_index()

    positive_contexts = (
        preds[
            preds["task"].eq("e72_frontier_neighbor")
            & preds["split"].eq("loo_pair_context")
            & preds["label"].eq(1)
            & preds["prob"].notna()
        ]
        .groupby(["feature_view", "heldout"])
        .agg(n=("label", "size"), mean_prob=("prob", "mean"), min_prob=("prob", "min"), max_prob=("prob", "max"))
        .reset_index()
    )
    exact_fp = (
        preds[
            preds["task"].eq("e72_frontier_neighbor")
            & preds["split"].eq("loo_pair_id")
            & preds["pair_is_e95_e101"]
            & preds["prob"].notna()
        ]
        .groupby("feature_view")
        .agg(exact_e95_e101_mean_prob=("prob", "mean"), exact_e95_e101_max_prob=("prob", "max"))
        .reset_index()
    )

    best_pair = e72_summary[e72_summary["split"].eq("loo_pair_id")].head(1)
    best_pair_line = "none"
    if not best_pair.empty:
        r = best_pair.iloc[0]
        best_pair_line = (
            f"`{r['feature_view']}` pair-LOO AUC `{float(r['auc']):.3f}`, "
            f"AP `{float(r['avg_precision']):.3f}`, top-k recall `{float(r['topk_recall']):.3f}`"
        )
    branch_cols = [
        "feature_view",
        "candidate",
        "scenario_count",
        "contam_prob_mean",
        "contam_prob_max",
        "above_non_e72_p95_rate",
        "above_min_positive_rate",
        "support_minus_shape_mean",
    ]
    summary_cols = [
        "task",
        "feature_view",
        "split",
        "n_rows",
        "n_pos",
        "auc",
        "avg_precision",
        "topk_precision",
        "topk_recall",
        "exact_e95_e101_mean_prob",
        "skipped_rows",
        "skipped_positive_rows",
    ]
    report = f"""# E190 E72 Contamination Detector

## Question

E189 localized support's useful E95-edge wins to E72-neighbor rows. Can a
filename-free movement representation detect that contamination, or was the
support gate just known-file identity?

## Result In One Sentence

Best E72-neighbor detection under pair-LOO is {best_pair_line}, but file-LOO
cannot hold out E72 itself because all positive labels contain E72; therefore
the detector is a diagnostic, not yet a deployable live gate.

## E72-Neighbor Detection Summary

{md(e72_summary, summary_cols, n=40)}

## Support-Needed E95-Edge Summary

{md(support_summary, summary_cols, n=40)}

## Positive Context Holdouts

{md(positive_contexts.sort_values(['feature_view', 'heldout']), n=80)}

## Exact E95/E101 False Positive Check

{md(exact_fp.sort_values('feature_view'), n=40)}

## Live Pressure Branch Contamination Scores

{md(live_branch.sort_values(['feature_view', 'candidate']), branch_cols, n=80)}

## Top Branch Rows

{md(branch_view, ['feature_view', 'candidate', 'scenario', 'e72_contam_prob', 'known_non_e72_p95', 'known_min_positive', 'above_non_e72_p95', 'above_min_positive', 'shape_prob', 'support_prob', 'support_minus_shape_prob', 'top_targets'], n=80)}

## Top Structural Features

{md(features, ['task', 'feature', 'auc_abs_directionless', 'signed_auc', 'positive_mean', 'negative_mean', 'mean_diff_pos_minus_neg'], n=80)}

## Interpretation

- There is movement-shape signal for E72-neighbor contamination under pair and
  non-E72 file holdouts.
- The strongest stress still has a blind spot: if the E72 file itself is held
  out, no positive examples remain. That means this is not a public-free law in
  the strictest sense; it is an E72-observation-derived diagnostic.
- A usable support gate must not only identify E72-neighbor anchors; it must
  keep exact E95/E101 probability low and score live pressure branches with a
  predeclared threshold.

## Decision

No submission is created. Support may be used as an E72-contamination diagnostic
only when a structural score is high and exact E95/E101 false-positive risk is
low. Current live branch scores remain evidence, not a gate.
"""
    REPORT_OUT.write_text(report)


def main() -> None:
    z, support_rows = make_inputs()
    pred_rows: list[pd.DataFrame] = []
    summary_rows: list[dict[str, Any]] = []

    z["e72_neighbor_label"] = z["pair_is_e72_frontier_neighbor"].astype(int)
    for view in FEATURE_VIEWS:
        for group_col in ("pair_id", "pair_context", "new_file", "base_file"):
            pred, summary = grouped_oof(z, "e72_neighbor_label", view, group_col, "e72_frontier_neighbor")
            pred_rows.append(pred)
            summary_rows.append(summary)
        pred, summary = any_file_oof(z, "e72_neighbor_label", view, "e72_frontier_neighbor")
        pred_rows.append(pred)
        summary_rows.append(summary)

    for view in FEATURE_VIEWS:
        for group_col in ("pair_id", "pair_context", "heldout"):
            pred, summary = grouped_oof(
                support_rows,
                "support_needed_label",
                view,
                group_col,
                "support_needed_e95_edge",
            )
            pred_rows.append(pred)
            summary_rows.append(summary)

    predictions = pd.concat(pred_rows, ignore_index=True)
    summary = pd.DataFrame(summary_rows)
    feature_frames = [
        feature_audit(z, "e72_neighbor_label", "e72_frontier_neighbor"),
        feature_audit(support_rows, "support_needed_label", "support_needed_e95_edge"),
    ]
    features = pd.concat(feature_frames, ignore_index=True)
    branches = fit_full_and_score_branches(z, "e72_neighbor_label")

    summary.to_csv(SUMMARY_OUT, index=False)
    predictions.to_csv(PRED_OUT, index=False)
    features.to_csv(FEATURE_OUT, index=False)
    branches.to_csv(BRANCH_OUT, index=False)
    write_report(summary, predictions, branches, features)
    print(f"Wrote {SUMMARY_OUT}")
    print(f"Wrote {PRED_OUT}")
    print(f"Wrote {FEATURE_OUT}")
    print(f"Wrote {BRANCH_OUT}")
    print(f"Wrote {REPORT_OUT}")


if __name__ == "__main__":
    main()
