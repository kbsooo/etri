#!/usr/bin/env python3
"""E184: public-anchor cell motif as a pressure-branch selector.

E183 showed that visible/subject/flank priors reject the favorable pressure
branch for E176, E154, and E144. The next smallest non-visible question is:

    Do known public transitions contain a metadata motif that can tell whether
    a candidate's support direction is public-compatible, and does that motif
    select the favorable pressure branch?

This is deliberately a diagnostic. It uses known public anchors as sensors, not
as a direct leaderboard optimizer, and it requires leave-one-pair/family stress
before any live branch score is trusted.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

ANCHOR_CELLS_IN = OUT / "e180_known_anchor_decisive_cell_visibility_cells.csv"
PRESSURE_CELLS_IN = OUT / "e183_pressure_world_branch_anatomy_cells.csv"

PAIR_CV_OUT = OUT / "e184_public_anchor_motif_pair_cv.csv"
FAMILY_CV_OUT = OUT / "e184_public_anchor_motif_family_cv.csv"
BRANCH_OUT = OUT / "e184_public_anchor_motif_pressure_branch_scores.csv"
FEATURE_OUT = OUT / "e184_public_anchor_motif_feature_sets.csv"
REPORT_OUT = OUT / "e184_public_anchor_motif_pressure_selector_report.md"

EPS = 1.0e-12


@dataclass(frozen=True)
class FeatureSet:
    name: str
    categorical: tuple[str, ...]
    numeric: tuple[str, ...]
    boolean: tuple[str, ...]

    @property
    def columns(self) -> list[str]:
        return [*self.categorical, *self.numeric, *self.boolean]


CORE_CAT = (
    "target",
    "target_group",
    "context_type",
    "pos_bin",
    "block_len_bin",
    "dow",
)
CORE_NUM = (
    "global_pos",
    "subject_pos",
    "subject_phase",
    "block_n_rows",
    "pos_in_block",
    "pos_frac",
    "edge_distance",
    "prev_gap_pos",
    "next_gap_pos",
    "prev_gap_days",
    "next_gap_days",
    "subject_train_count",
    "min_flank_gap_days",
)
CORE_BOOL = (
    "is_weekend",
    "edge_like",
    "has_prev_train",
    "has_next_train",
    "between_train_runs",
    "context_high",
    "both_flanks",
    "prev_only",
    "next_only",
    "flank_conflict",
    "flank_agree",
)
PUBLIC_AXIS_NUM = (
    "all_safe_density",
    "broad_low_alpha_mass",
    "e101_plausible_mass",
)
PUBLIC_AXIS_BOOL = (
    "e72_active",
    "e101_active",
    "all_veto_null",
)

FEATURE_SETS = [
    FeatureSet("meta_core", CORE_CAT, CORE_NUM, CORE_BOOL),
    FeatureSet("meta_public_axis", CORE_CAT, (*CORE_NUM, *PUBLIC_AXIS_NUM), (*CORE_BOOL, *PUBLIC_AXIS_BOOL)),
    FeatureSet(
        "meta_public_axis_plus_support_label",
        (*CORE_CAT, "support_label"),
        (*CORE_NUM, *PUBLIC_AXIS_NUM),
        (*CORE_BOOL, *PUBLIC_AXIS_BOOL),
    ),
    FeatureSet(
        "meta_public_axis_plus_swing",
        CORE_CAT,
        (*CORE_NUM, *PUBLIC_AXIS_NUM, "log_swing", "swing_rank"),
        (*CORE_BOOL, *PUBLIC_AXIS_BOOL),
    ),
]


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


def normalize_bool(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series.astype(int)
    return series.fillna(False).astype(bool).astype(int)


def prepare_frame(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "swing" in out.columns:
        out["log_swing"] = np.log1p(out["swing"].astype(float) * 1.0e6)
    for fs in FEATURE_SETS:
        for col in fs.categorical:
            if col in out.columns:
                out[col] = out[col].astype("object").where(out[col].notna(), "__missing__").astype(str)
        for col in fs.boolean:
            if col in out.columns:
                out[col] = normalize_bool(out[col])
        for col in fs.numeric:
            if col in out.columns:
                out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def make_pipeline(fs: FeatureSet) -> Pipeline:
    transformers = []
    if fs.categorical:
        transformers.append(
            (
                "cat",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="constant", fill_value="__missing__")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore", min_frequency=2)),
                    ]
                ),
                list(fs.categorical),
            )
        )
    if fs.numeric:
        transformers.append(
            (
                "num",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                list(fs.numeric),
            )
        )
    if fs.boolean:
        transformers.append(
            (
                "bool",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                    ]
                ),
                list(fs.boolean),
            )
        )
    pre = ColumnTransformer(transformers=transformers, remainder="drop")
    clf = LogisticRegression(max_iter=5000, C=0.5, solver="lbfgs")
    return Pipeline([("pre", pre), ("clf", clf)])


def pair_balanced_weights(df: pd.DataFrame, group_col: str) -> np.ndarray:
    swing = df["swing"].astype(float).to_numpy()
    weights = np.zeros(len(df), dtype=float)
    for _, idx in df.groupby(group_col).groups.items():
        loc = np.array(list(idx), dtype=int)
        s = swing[loc]
        denom = float(s.sum())
        if denom <= EPS:
            weights[loc] = 1.0 / max(len(loc), 1)
        else:
            weights[loc] = s / denom
    weights *= df[group_col].nunique()
    return weights


def public_support_labels(anchor: pd.DataFrame) -> pd.DataFrame:
    known = anchor[anchor["actual_direction"].isin(["new_won", "new_lost"])].copy()
    known["public_support_compatible"] = known["actual_direction"].eq("new_won").astype(int)
    # Keep the exact public transition sign as group-level supervision. This is
    # intentionally noisy at cell level; the CV stress decides whether it is usable.
    return known.reset_index(drop=True)


def fit_predict_oof(df: pd.DataFrame, fs: FeatureSet, group_col: str) -> tuple[pd.DataFrame, dict[str, Any]]:
    rows = []
    oof = np.full(len(df), np.nan, dtype=float)
    y = df["public_support_compatible"].to_numpy(dtype=int)
    weights_all = pair_balanced_weights(df, group_col)

    for group_value, test_idx in df.groupby(group_col).groups.items():
        test_pos = np.array(list(test_idx), dtype=int)
        train_mask = np.ones(len(df), dtype=bool)
        train_mask[test_pos] = False
        train = df.loc[train_mask].copy()
        test = df.iloc[test_pos].copy()
        if train["public_support_compatible"].nunique() < 2:
            continue
        pipe = make_pipeline(fs)
        train_w = pair_balanced_weights(train.reset_index(drop=True), group_col)
        pipe.fit(train[fs.columns], train["public_support_compatible"], clf__sample_weight=train_w)
        prob = pipe.predict_proba(test[fs.columns])[:, 1]
        oof[test_pos] = prob
        test_w = weights_all[test_pos]
        actual = int(test["public_support_compatible"].iloc[0])
        motif_score = float(np.average(prob, weights=test_w))
        rows.append(
            {
                "feature_set": fs.name,
                "group_col": group_col,
                "heldout": group_value,
                "actual_support_compatible": actual,
                "n_cells": int(len(test)),
                "motif_score": motif_score,
                "predicted_support_compatible": bool(motif_score >= 0.5),
                "correct": bool((motif_score >= 0.5) == bool(actual)),
                "cell_logloss": float(log_loss(test["public_support_compatible"], prob, labels=[0, 1], sample_weight=test_w)),
                "cell_brier": float(brier_score_loss(test["public_support_compatible"], prob, sample_weight=test_w)),
                "prob_min": float(np.min(prob)),
                "prob_max": float(np.max(prob)),
            }
        )

    valid = np.isfinite(oof)
    metrics: dict[str, Any] = {
        "feature_set": fs.name,
        "group_col": group_col,
        "groups_evaluated": int(len(rows)),
        "cell_count": int(valid.sum()),
    }
    if valid.any() and len(np.unique(y[valid])) == 2:
        metrics["oof_auc"] = float(roc_auc_score(y[valid], oof[valid], sample_weight=weights_all[valid]))
        metrics["oof_logloss"] = float(log_loss(y[valid], oof[valid], labels=[0, 1], sample_weight=weights_all[valid]))
        metrics["oof_brier"] = float(brier_score_loss(y[valid], oof[valid], sample_weight=weights_all[valid]))
    else:
        metrics["oof_auc"] = np.nan
        metrics["oof_logloss"] = np.nan
        metrics["oof_brier"] = np.nan
    rows_df = pd.DataFrame(rows)
    metrics["group_sign_accuracy"] = float(rows_df["correct"].mean()) if not rows_df.empty else np.nan
    if np.isfinite(metrics["oof_auc"]):
        metrics["polarity_best_auc"] = float(max(metrics["oof_auc"], 1.0 - metrics["oof_auc"]))
        metrics["auc_polarity"] = "direct" if metrics["oof_auc"] >= 0.5 else "inverted"
    else:
        metrics["polarity_best_auc"] = np.nan
        metrics["auc_polarity"] = "unknown"
    if np.isfinite(metrics["group_sign_accuracy"]):
        metrics["polarity_best_group_accuracy"] = float(
            max(metrics["group_sign_accuracy"], 1.0 - metrics["group_sign_accuracy"])
        )
        metrics["group_polarity"] = "direct" if metrics["group_sign_accuracy"] >= 0.5 else "inverted"
    else:
        metrics["polarity_best_group_accuracy"] = np.nan
        metrics["group_polarity"] = "unknown"
    return rows_df, metrics


def fit_full_model(df: pd.DataFrame, fs: FeatureSet) -> Pipeline:
    pipe = make_pipeline(fs)
    weights = pair_balanced_weights(df, "pair")
    pipe.fit(df[fs.columns], df["public_support_compatible"], clf__sample_weight=weights)
    return pipe


def branch_scores(pressure: pd.DataFrame, model: Pipeline, fs: FeatureSet) -> pd.DataFrame:
    diff = pressure[pressure["minmax_label_diff"].astype(bool)].copy()
    prob = model.predict_proba(diff[fs.columns])[:, 1]
    diff["motif_prob_support_public"] = prob
    diff["min_branch_prob"] = np.where(diff["min_support"].astype(bool), prob, 1.0 - prob)
    diff["max_branch_prob"] = np.where(diff["max_support"].astype(bool), prob, 1.0 - prob)
    rows = []
    for (candidate, scenario), part in diff.groupby(["candidate", "scenario"], sort=False):
        weights = part["coeff_abs"].astype(float).to_numpy()
        weights = np.where(weights <= EPS, 1.0, weights)
        min_prob = np.clip(part["min_branch_prob"].to_numpy(dtype=float), 1.0e-6, 1.0 - 1.0e-6)
        max_prob = np.clip(part["max_branch_prob"].to_numpy(dtype=float), 1.0e-6, 1.0 - 1.0e-6)
        min_ce = float(-np.average(np.log(min_prob), weights=weights))
        max_ce = float(-np.average(np.log(max_prob), weights=weights))
        rows.append(
            {
                "feature_set": fs.name,
                "candidate": candidate,
                "scenario": scenario,
                "n_diff_cells": int(len(part)),
                "motif_prob_support_public_mean": float(
                    np.average(part["motif_prob_support_public"].to_numpy(dtype=float), weights=weights)
                ),
                "min_branch_prob_mean": float(np.average(min_prob, weights=weights)),
                "max_branch_prob_mean": float(np.average(max_prob, weights=weights)),
                "min_minus_max_ce": float(min_ce - max_ce),
                "motif_prefers_favorable_min": bool(min_ce < max_ce),
                "between_train_runs_rate": float(part["between_train_runs"].astype(bool).mean()),
                "e72_active_rate": float(part["e72_active"].astype(bool).mean()),
                "e101_active_rate": float(part["e101_active"].astype(bool).mean()),
                "top_targets": ",".join(
                    part.groupby("target")["coeff_abs"].sum().sort_values(ascending=False).head(4).index.astype(str)
                ),
            }
        )
    return pd.DataFrame(rows)


def summarize_branch(branch: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (feature_set, candidate), part in branch.groupby(["feature_set", "candidate"], sort=False):
        rows.append(
            {
                "feature_set": feature_set,
                "candidate": candidate,
                "scenario_count": int(len(part)),
                "motif_prefers_min_rate": float(part["motif_prefers_favorable_min"].mean()),
                "min_minus_max_ce_mean": float(part["min_minus_max_ce"].mean()),
                "min_branch_prob_mean": float(part["min_branch_prob_mean"].mean()),
                "max_branch_prob_mean": float(part["max_branch_prob_mean"].mean()),
                "motif_prob_support_public_mean": float(part["motif_prob_support_public_mean"].mean()),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    anchor_raw = pd.read_csv(ANCHOR_CELLS_IN, low_memory=False)
    pressure_raw = pd.read_csv(PRESSURE_CELLS_IN, low_memory=False)
    anchor = prepare_frame(public_support_labels(anchor_raw))
    pressure = prepare_frame(pressure_raw)

    pair_cv_parts = []
    family_cv_parts = []
    metric_rows = []
    branch_parts = []

    for fs in FEATURE_SETS:
        pair_rows, pair_metrics = fit_predict_oof(anchor, fs, "pair")
        family_rows, family_metrics = fit_predict_oof(anchor, fs, "family")
        pair_cv_parts.append(pair_rows)
        family_cv_parts.append(family_rows)
        metric_rows.append(pair_metrics)
        metric_rows.append(family_metrics)

        model = fit_full_model(anchor, fs)
        branch_parts.append(branch_scores(pressure, model, fs))

    pair_cv = pd.concat(pair_cv_parts, ignore_index=True)
    family_cv = pd.concat(family_cv_parts, ignore_index=True)
    metrics = pd.DataFrame(metric_rows)
    branch = pd.concat(branch_parts, ignore_index=True)
    branch_summary = summarize_branch(branch)

    pair_cv.to_csv(PAIR_CV_OUT, index=False)
    family_cv.to_csv(FAMILY_CV_OUT, index=False)
    branch.to_csv(BRANCH_OUT, index=False)
    metrics.to_csv(FEATURE_OUT, index=False)

    pair_metrics = metrics[metrics["group_col"].eq("pair")].copy()
    family_metrics = metrics[metrics["group_col"].eq("family")].copy()
    best_pair = pair_metrics.sort_values(["group_sign_accuracy", "oof_auc"], ascending=False).head(1)
    best_family = family_metrics.sort_values(["group_sign_accuracy", "oof_auc"], ascending=False).head(1)
    best_pair_polar = pair_metrics.sort_values(
        ["polarity_best_group_accuracy", "polarity_best_auc"], ascending=False
    ).head(1)
    if best_pair.empty:
        result_sentence = "No public-anchor motif model could be evaluated."
    else:
        bp = best_pair.iloc[0]
        bf = best_family.iloc[0]
        bpp = best_pair_polar.iloc[0]
        live = branch_summary[branch_summary["feature_set"].eq(bp["feature_set"])]
        branch_patterns = (
            branch_summary.groupby("feature_set")["motif_prefers_min_rate"]
            .mean()
            .map(lambda x: f"{x:.3f}")
            .to_dict()
        )
        result_sentence = (
            f"Direct public-anchor motifs fail: the best direct pair-LOO model `{bp['feature_set']}` has "
            f"sign accuracy `{bp['group_sign_accuracy']:.3f}` and AUC `{bp['oof_auc']:.3f}`. "
            f"The strongest pair signal is polarity-inverted (`{bpp['feature_set']}`, "
            f"best-polarity accuracy `{bpp['polarity_best_group_accuracy']:.3f}`), but family-level "
            f"best direct accuracy/AUC are only `{bf['group_sign_accuracy']:.3f}` / `{bf['oof_auc']:.3f}`. "
            "Live branch preferences are feature-set unstable: "
            + ", ".join(f"{k}={v}" for k, v in branch_patterns.items())
            + ". Under the best direct pair model, candidate rates are "
            + ", ".join(
                f"{r.candidate} `{r.motif_prefers_min_rate:.3f}`"
                for r in live.itertuples(index=False)
            )
            + "."
        )

    report = f"""# E184 Public-Anchor Motif Pressure Selector

## Question

E183 killed visible/subject/flank priors as pressure-branch selectors. This
audit asks whether a non-visible cell motif learned from known public
transitions can select the favorable E182 branch for E176/E154/E144.

This is not a submission generator. If the motif cannot survive leave-one-pair
or leave-one-family stress, its live branch score is treated as diagnostic only.

## Result In One Sentence

{result_sentence}

## CV Metrics

{md(metrics.sort_values(["group_col", "group_sign_accuracy", "oof_auc"], ascending=[True, False, False]))}

## Pair LOO

{md(pair_cv.sort_values(["feature_set", "heldout"]))}

## Family LOO

{md(family_cv.sort_values(["feature_set", "heldout"]))}

## Pressure Branch Summary

{md(branch_summary.sort_values(["feature_set", "candidate"]))}

## Pressure Branch Scenario Details

{md(branch.sort_values(["feature_set", "candidate", "scenario"]))}

## Interpretation

- A usable branch selector must first recover known public transition signs
  when a whole pair or family is held out.
- Feature sets that include `support_label` are intentionally listed as a
  target-prior stress, but they are weaker evidence than support-label-free
  metadata because they can learn label-direction quirks.
- If a feature set has weak LOO/LOFO accuracy, its pressure-branch preference is
  not action-grade even when it selects a live branch.

## Decision

No submission. Use this audit to decide whether the next local step should be a
stronger non-visible decisive-cell representation or a public-feedback decoder
for a chosen worldview.
"""
    REPORT_OUT.write_text(report, encoding="utf-8")

    for path in [PAIR_CV_OUT, FAMILY_CV_OUT, BRANCH_OUT, FEATURE_OUT, REPORT_OUT]:
        print(path)


if __name__ == "__main__":
    main()
