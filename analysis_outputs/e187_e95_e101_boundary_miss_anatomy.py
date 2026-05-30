#!/usr/bin/env python3
"""E187: anatomy of the E95/E101 miss in the antisymmetric pair decoder.

E186 made pair probabilities reciprocal and selected the E176 pressure branch,
but the support-heavy variants still misread the most important known boundary:
E95 is slightly better than E101 on public LB. This audit asks whether that miss
is caused by a removable feature family shortcut or by the same support geometry
that made E176 look attractive.

No submission is created. The output is a decision record for whether the
known-LB pair decoder is an action-grade selector or only a coarse sensor.
"""

from __future__ import annotations

from dataclasses import dataclass
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
import e186_antisymmetric_pair_decoder as e186  # noqa: E402


Z_FEATURES_IN = OUT / "e186_antisymmetric_pair_decoder_zfeatures.csv"
PAIR_FEATURES_IN = OUT / "e185_known_lb_pair_structural_decoder_features.csv"
SUMMARY_OUT = OUT / "e187_e95_e101_boundary_miss_anatomy_summary.csv"
PRED_OUT = OUT / "e187_e95_e101_boundary_miss_anatomy_predictions.csv"
CONTRIB_OUT = OUT / "e187_e95_e101_boundary_miss_anatomy_contributions.csv"
BRANCH_OUT = OUT / "e187_e95_e101_boundary_miss_anatomy_branch_scores.csv"
REPORT_OUT = OUT / "e187_e95_e101_boundary_miss_anatomy_report.md"

EPS = 1.0e-12
E95 = "submission_e95_hardtail_541e3973.csv"
E101 = "submission_e101_q2s3tail_177569bc.csv"
E176 = "e176"


@dataclass(frozen=True)
class Variant:
    name: str
    include_prefixes: tuple[str, ...]
    exclude_contains: tuple[str, ...] = ()


BASE_PREFIXES = ("z__shape_", "z__target_", "z__ctx_")
SUP_PREFIXES = BASE_PREFIXES + ("z__sup_",)
AXIS_PREFIXES = BASE_PREFIXES + ("z__axis_",)
FULL_PREFIXES = BASE_PREFIXES + ("z__sup_", "z__axis_")

VARIANTS = (
    Variant("shape_only", BASE_PREFIXES),
    Variant("shape_axis_no_support", AXIS_PREFIXES),
    Variant("shape_support", SUP_PREFIXES),
    Variant("shape_support_public_axis", FULL_PREFIXES),
    Variant("shape_support_drop_global", SUP_PREFIXES, ("_global_",)),
    Variant("shape_support_drop_subject", SUP_PREFIXES, ("_subject_",)),
    Variant("shape_support_drop_nearest", SUP_PREFIXES, ("_nearest_",)),
    Variant("shape_support_drop_focus", SUP_PREFIXES, ("_focus_",)),
    Variant("shape_support_drop_flank", SUP_PREFIXES, ("_flank_",)),
    Variant("shape_support_drop_visible", SUP_PREFIXES, ("_visible_",)),
    Variant("shape_support_drop_prior_split", SUP_PREFIXES, ("prior_split",)),
    Variant("shape_support_drop_top1", SUP_PREFIXES, ("z__sup_top1_", "z__shape_top1_", "z__target_top1_", "z__ctx_top1_")),
    Variant("shape_support_drop_top16_33", SUP_PREFIXES, ("z__sup_top16_", "z__sup_top33_")),
    Variant("shape_support_drop_between", SUP_PREFIXES, ("_between_",)),
    Variant("shape_support_keep_mean_only", SUP_PREFIXES, ("_hard_rate", "_swing", "prior_split", "range_mean")),
    Variant("shape_support_keep_hard_only", SUP_PREFIXES, ("_mean", "_swing", "prior_split", "range_mean")),
    Variant("shape_support_no_q2s3_targets", SUP_PREFIXES, ("_Q2_", "_S3_")),
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


def make_model() -> Pipeline:
    return Pipeline(
        [
            ("scale", StandardScaler(with_mean=False)),
            ("clf", LogisticRegression(max_iter=5000, C=0.25, solver="lbfgs", fit_intercept=False)),
        ]
    )


def safe_auc(y: np.ndarray, p: np.ndarray) -> float:
    if len(np.unique(y)) < 2:
        return np.nan
    return float(roc_auc_score(y, p))


def variant_cols(frame: pd.DataFrame, variant: Variant) -> list[str]:
    cols = [
        c
        for c in frame.columns
        if any(c.startswith(prefix) for prefix in variant.include_prefixes)
        and not any(token in c for token in variant.exclude_contains)
        and pd.api.types.is_numeric_dtype(frame[c])
    ]
    return sorted(cols)


def is_e95_e101_pair(frame: pd.DataFrame) -> pd.Series:
    return (
        (frame["new_file"].eq(E95) & frame["base_file"].eq(E101))
        | (frame["new_file"].eq(E101) & frame["base_file"].eq(E95))
    )


def family_of(col: str) -> str:
    if col.startswith("z__shape_"):
        return "shape"
    if col.startswith("z__target_"):
        return "target"
    if col.startswith("z__ctx_"):
        return "context"
    if col.startswith("z__axis_"):
        if "_e101_" in col or "e101_" in col:
            return "axis_e101"
        if "_e72_" in col or "e72_" in col:
            return "axis_e72"
        return "axis_other"
    if col.startswith("z__sup_"):
        for name in ("global", "subject", "nearest", "focus", "flank", "visible"):
            if f"_{name}_" in col:
                return f"support_{name}"
        if "prior_split" in col:
            return "support_prior_split"
        if "all_prior" in col:
            return "support_all_prior"
        if "range_mean" in col:
            return "support_range"
        return "support_other"
    return "other"


def evaluate(pred: pd.DataFrame, group_col: str, variant: Variant) -> dict[str, Any]:
    y = pred["actual_new_better"].to_numpy(dtype=int)
    p = pred["prob_new_better"].to_numpy(dtype=np.float64)
    out: dict[str, Any] = {
        "variant": variant.name,
        "group_col": group_col,
        "n_cols": int(pred["n_cols"].max()) if "n_cols" in pred else np.nan,
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
        ("e95_e101_pair", "e95_e101"),
    ]:
        if flag in pred.columns and pred[flag].any():
            part = pred.loc[pred[flag]]
            yy = part["actual_new_better"].to_numpy(dtype=int)
            pp = part["prob_new_better"].to_numpy(dtype=np.float64)
            out[f"{name}_n"] = int(len(part))
            out[f"{name}_accuracy"] = float(np.mean((pp >= 0.5) == yy))
            out[f"{name}_auc"] = safe_auc(yy, pp)
            out[f"{name}_logloss"] = float(log_loss(yy, np.clip(pp, EPS, 1.0 - EPS), labels=[0, 1]))
            if name == "e95_e101":
                e95_rows = part[part["new_file"].eq(E95)]
                e101_rows = part[part["new_file"].eq(E101)]
                out["e95_prob_mean"] = float(e95_rows["prob_new_better"].mean()) if not e95_rows.empty else np.nan
                out["e101_prob_mean"] = float(e101_rows["prob_new_better"].mean()) if not e101_rows.empty else np.nan
        else:
            out[f"{name}_n"] = 0
            out[f"{name}_accuracy"] = np.nan
            out[f"{name}_auc"] = np.nan
            out[f"{name}_logloss"] = np.nan
    return out


def predict_file_loo(zfeatures: pd.DataFrame, variant: Variant) -> pd.DataFrame:
    cols = variant_cols(zfeatures, variant)
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
                    "variant": variant.name,
                    "group_col": "file",
                    "heldout": held_file,
                    "n_cols": len(cols),
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
                    "e95_e101_pair": bool({rec["new_file"], rec["base_file"]} == {E95, E101}),
                }
            )
    return pd.DataFrame(rows)


def predict_pair_loo(zfeatures: pd.DataFrame, variant: Variant) -> pd.DataFrame:
    cols = variant_cols(zfeatures, variant)
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
                    "variant": variant.name,
                    "group_col": "pair",
                    "heldout": pair_id,
                    "n_cols": len(cols),
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
                    "e95_e101_pair": bool({rec["new_file"], rec["base_file"]} == {E95, E101}),
                }
            )
    return pd.DataFrame(rows)


def branch_scores(zfeatures: pd.DataFrame, variant: Variant) -> pd.DataFrame:
    cols = variant_cols(zfeatures, variant)
    model = make_model()
    model.fit(zfeatures[cols], zfeatures["actual_new_better"])
    branches = e186.branch_zrecords()
    for col in cols:
        if col not in branches.columns:
            branches[col] = 0.0
    prob = model.predict_proba(branches[cols])[:, 1]
    out = branches[["candidate", "scenario", "n_diff_cells", "top_targets"]].copy()
    out.insert(0, "variant", variant.name)
    out["n_cols"] = len(cols)
    out["prob_pressure_min_public_better"] = prob
    out["prefers_favorable_min"] = out["prob_pressure_min_public_better"] >= 0.5
    return out


def model_contributions(zfeatures: pd.DataFrame, variant: Variant, heldout: str, group_col: str) -> pd.DataFrame:
    cols = variant_cols(zfeatures, variant)
    if group_col == "file":
        test_mask = zfeatures["new_file"].eq(heldout) | zfeatures["base_file"].eq(heldout)
    elif group_col == "pair":
        test_mask = zfeatures["pair_id"].eq(heldout)
    else:
        raise ValueError(group_col)
    train = zfeatures.loc[~test_mask].copy()
    test = zfeatures.loc[test_mask & is_e95_e101_pair(zfeatures)].copy()
    if train["actual_new_better"].nunique() < 2 or test.empty:
        return pd.DataFrame()
    model = make_model()
    model.fit(train[cols], train["actual_new_better"])
    scaler: StandardScaler = model.named_steps["scale"]
    clf: LogisticRegression = model.named_steps["clf"]
    scale = np.where(scaler.scale_ == 0.0, 1.0, scaler.scale_)
    coef = clf.coef_[0]
    rows: list[dict[str, Any]] = []
    for rec in test.to_dict("records"):
        x = np.array([float(rec.get(col, 0.0) or 0.0) for col in cols], dtype=np.float64)
        x_scaled = x / scale
        raw_contrib = x_scaled * coef
        prob = float(model.predict_proba(pd.DataFrame([rec])[cols])[:, 1][0])
        for col, value, c in zip(cols, x, raw_contrib):
            rows.append(
                {
                    "variant": variant.name,
                    "group_col": group_col,
                    "heldout": heldout,
                    "new_file": rec["new_file"],
                    "base_file": rec["base_file"],
                    "actual_new_better": rec["actual_new_better"],
                    "prob_new_better": prob,
                    "feature": col,
                    "family": family_of(col),
                    "raw_value": value,
                    "contribution": float(c),
                    "abs_contribution": float(abs(c)),
                }
            )
    return pd.DataFrame(rows)


def family_contribution_summary(contrib: pd.DataFrame) -> pd.DataFrame:
    if contrib.empty:
        return pd.DataFrame()
    rows = []
    keys = ["variant", "group_col", "heldout", "new_file", "base_file", "family"]
    for key, part in contrib.groupby(keys):
        rec = dict(zip(keys, key, strict=True))
        rec["family_contribution"] = float(part["contribution"].sum())
        rec["family_abs_contribution"] = float(part["abs_contribution"].sum())
        rec["top_feature"] = str(part.sort_values("abs_contribution", ascending=False).iloc[0]["feature"])
        rec["top_feature_contribution"] = float(
            part.sort_values("abs_contribution", ascending=False).iloc[0]["contribution"]
        )
        rows.append(rec)
    return pd.DataFrame(rows)


def summarize_branches(branches: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (variant, candidate), part in branches.groupby(["variant", "candidate"]):
        rows.append(
            {
                "variant": variant,
                "candidate": candidate,
                "prefers_favorable_min_rate": float(part["prefers_favorable_min"].mean()),
                "prob_mean": float(part["prob_pressure_min_public_better"].mean()),
                "prob_min": float(part["prob_pressure_min_public_better"].min()),
                "prob_max": float(part["prob_pressure_min_public_better"].max()),
            }
        )
    return pd.DataFrame(rows)


def attach_branch_summary(summary: pd.DataFrame, branches: pd.DataFrame) -> pd.DataFrame:
    branch_summary = summarize_branches(branches)
    e176 = branch_summary[branch_summary["candidate"].eq(E176)][
        ["variant", "prefers_favorable_min_rate", "prob_mean", "prob_min", "prob_max"]
    ].rename(
        columns={
            "prefers_favorable_min_rate": "e176_favorable_rate",
            "prob_mean": "e176_prob_mean",
            "prob_min": "e176_prob_min",
            "prob_max": "e176_prob_max",
        }
    )
    out = summary.merge(e176, on="variant", how="left")
    out["action_grade_boundary_branch"] = (
        out["group_col"].eq("file")
        & out["e95_e101_accuracy"].eq(1.0)
        & out["e95_edge_accuracy"].ge(0.80)
        & out["frontier_accuracy"].ge(0.80)
        & out["e176_favorable_rate"].eq(1.0)
    )
    return out


def build_inputs() -> pd.DataFrame:
    if not PAIR_FEATURES_IN.exists():
        known = e185.load_known_scores()
        e185.build_oriented_pair_features(known).to_csv(PAIR_FEATURES_IN, index=False)
    if Z_FEATURES_IN.exists():
        return pd.read_csv(Z_FEATURES_IN)
    features = pd.read_csv(PAIR_FEATURES_IN)
    zfeatures = e186.build_zfeatures(features)
    zfeatures.to_csv(Z_FEATURES_IN, index=False)
    return zfeatures


def write_report(
    summary: pd.DataFrame,
    predictions: pd.DataFrame,
    branches: pd.DataFrame,
    family_contrib: pd.DataFrame,
) -> None:
    file_summary = summary[summary["group_col"].eq("file")].sort_values(
        [
            "action_grade_boundary_branch",
            "e95_e101_accuracy",
            "e176_favorable_rate",
            "e95_edge_accuracy",
            "frontier_accuracy",
            "accuracy",
        ],
        ascending=[False, False, False, False, False, False],
    )
    pair_summary = summary[summary["group_col"].eq("pair")].sort_values(
        [
            "e95_e101_accuracy",
            "e95_edge_accuracy",
            "frontier_accuracy",
            "accuracy",
        ],
        ascending=False,
    )
    boundary = predictions[predictions["e95_e101_pair"]].sort_values(
        ["group_col", "variant", "heldout", "new_file"]
    )
    branch_summary = summarize_branches(branches).sort_values(["variant", "candidate"])
    contrib_focus = family_contrib[
        family_contrib["variant"].isin(["shape_only", "shape_support", "shape_support_public_axis"])
        & family_contrib["new_file"].eq(E95)
    ].sort_values(["variant", "group_col", "heldout", "family_abs_contribution"], ascending=[True, True, True, False])

    cols_summary = [
        "variant",
        "group_col",
        "n_cols",
        "accuracy",
        "auc",
        "logloss",
        "frontier_accuracy",
        "micro_accuracy",
        "e95_edge_accuracy",
        "e95_e101_accuracy",
        "e95_prob_mean",
        "e101_prob_mean",
        "e176_favorable_rate",
        "e176_prob_mean",
        "action_grade_boundary_branch",
    ]
    cols_boundary = [
        "variant",
        "group_col",
        "heldout",
        "new_file",
        "base_file",
        "actual_delta",
        "prob_new_better",
        "correct",
    ]
    cols_branch = [
        "variant",
        "candidate",
        "prefers_favorable_min_rate",
        "prob_mean",
        "prob_min",
        "prob_max",
    ]
    cols_contrib = [
        "variant",
        "group_col",
        "heldout",
        "new_file",
        "base_file",
        "family",
        "family_contribution",
        "family_abs_contribution",
        "top_feature",
        "top_feature_contribution",
    ]

    action = summary[summary["action_grade_boundary_branch"] & summary["group_col"].eq("file")]
    if action.empty:
        one_liner = (
            "No file-LOO variant simultaneously fixes the E95/E101 boundary, keeps "
            "frontier stress above 0.80, and preserves the E176 branch."
        )
    else:
        best = action.sort_values(["frontier_accuracy", "e95_edge_accuracy", "accuracy"], ascending=False).iloc[0]
        one_liner = (
            f"`{best['variant']}` is the only action-grade repair candidate under this audit: "
            f"E95/E101 accuracy {float(best['e95_e101_accuracy']):.3f}, "
            f"frontier accuracy {float(best['frontier_accuracy']):.3f}, "
            f"E176 favorable rate {float(best['e176_favorable_rate']):.3f}."
        )

    report = f"""# E187 E95/E101 Boundary Miss Anatomy

## Question

E186 repaired reciprocal geometry and made E176 look attractive, but the known
public sensor now says E101 (`0.576300366`) is still slightly worse than E95
(`0.5762913298`). Is the E95/E101 miss caused by a removable feature-family
shortcut, or by the same support structure that powers the E176 branch?

## Result In One Sentence

{one_liner}

## File-LOO Variant Stress

{md(file_summary, cols_summary, n=60)}

## Pair-LOO Variant Stress

{md(pair_summary, cols_summary, n=60)}

## Exact E95/E101 Boundary Predictions

{md(boundary, cols_boundary, n=120)}

## Pressure-Branch Summary

{md(branch_summary, cols_branch, n=80)}

## E95-over-E101 Family Contributions

{md(contrib_focus, cols_contrib, n=120)}

## Interpretation

- If shape-only fixes E95/E101 while support variants miss it, support priors are
  not pure label signal; they carry a frontier-quality shortcut that can invert
  the tightest boundary.
- If a support ablation both fixes E95/E101 and still selects E176, then the
  shortcut is removable and the branch selector can be repaired.
- If no ablation survives both tests, the known-LB pair decoder should stay a
  sensor for hypotheses, not an automatic selector for submissions.

## Decision

Use `action_grade_boundary_branch` as the local decision flag. A false flag
means the next public-facing submission should not be chosen by this decoder
alone; it needs an orthogonal cell/target stress rationale.
"""
    REPORT_OUT.write_text(report, encoding="utf-8")


def run() -> None:
    zfeatures = build_inputs()
    all_predictions: list[pd.DataFrame] = []
    summary_rows: list[dict[str, Any]] = []
    branch_rows: list[pd.DataFrame] = []
    contrib_rows: list[pd.DataFrame] = []

    e95_pair_id = zfeatures.loc[is_e95_e101_pair(zfeatures), "pair_id"].iloc[0]
    contribution_variants = {
        "shape_only",
        "shape_axis_no_support",
        "shape_support",
        "shape_support_public_axis",
        "shape_support_drop_global",
        "shape_support_drop_subject",
        "shape_support_drop_nearest",
        "shape_support_drop_visible",
    }

    for variant in VARIANTS:
        f_pred = predict_file_loo(zfeatures, variant)
        p_pred = predict_pair_loo(zfeatures, variant)
        all_predictions.extend([f_pred, p_pred])
        summary_rows.append(evaluate(f_pred, "file", variant))
        summary_rows.append(evaluate(p_pred, "pair", variant))
        branch_rows.append(branch_scores(zfeatures, variant))
        if variant.name in contribution_variants:
            for heldout in (E95, E101):
                contrib_rows.append(model_contributions(zfeatures, variant, heldout, "file"))
            contrib_rows.append(model_contributions(zfeatures, variant, e95_pair_id, "pair"))

    predictions = pd.concat(all_predictions, ignore_index=True)
    branches = pd.concat(branch_rows, ignore_index=True)
    contrib = pd.concat([c for c in contrib_rows if not c.empty], ignore_index=True)
    family_contrib = family_contribution_summary(contrib)
    summary = attach_branch_summary(pd.DataFrame(summary_rows), branches)

    summary.to_csv(SUMMARY_OUT, index=False)
    predictions.to_csv(PRED_OUT, index=False)
    family_contrib.to_csv(CONTRIB_OUT, index=False)
    branches.to_csv(BRANCH_OUT, index=False)
    write_report(summary, predictions, branches, family_contrib)

    print(SUMMARY_OUT)
    print(PRED_OUT)
    print(CONTRIB_OUT)
    print(BRANCH_OUT)
    print(REPORT_OUT)


if __name__ == "__main__":
    run()
