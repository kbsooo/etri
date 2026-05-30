#!/usr/bin/env python3
"""E191: boundary-aware E72 contamination scoring.

E190 found a useful filename-free E72-neighbor signal, but support-rich views
also treated the exact E95/E101 frontier boundary as E72-like. This script asks
the next smallest question:

    If exact E95/E101 is made an explicit hard negative, can support features
    become usable again without losing E72-neighbor recall?

No submission is created. The output is a gate/diagnostic audit.
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
import e190_e72_contamination_detector as e190  # noqa: E402


SUMMARY_OUT = OUT / "e191_boundary_aware_e72_score_summary.csv"
OOF_OUT = OUT / "e191_boundary_aware_e72_score_oof_audit.csv"
BRANCH_OUT = OUT / "e191_boundary_aware_e72_score_branch_audit.csv"
REPORT_OUT = OUT / "e191_boundary_aware_e72_score_report.md"

EPS = 1.0e-12


@dataclass(frozen=True)
class ScoreSpec:
    name: str
    kind: str
    hard_weight: float = 1.0
    other_weight: float = 1.0
    c: float = 0.25


SPECS = (
    ScoreSpec("plain_logit_c025", "weighted_logit", hard_weight=1.0, other_weight=1.0, c=0.25),
    ScoreSpec("hardneg4_other1_c025", "weighted_logit", hard_weight=4.0, other_weight=1.0, c=0.25),
    ScoreSpec("hardneg8_other025_c025", "weighted_logit", hard_weight=8.0, other_weight=0.25, c=0.25),
    ScoreSpec("prototype_pos_vs_boundary", "prototype"),
)

ACTIVE_VIEW_NAMES = {
    "shape_target_context_abs",
    "support_abs",
    "shape_target_context_support_abs",
    "all_abs",
}


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


def safe_ap(y: np.ndarray, p: np.ndarray) -> float:
    if len(np.unique(y)) < 2:
        return np.nan
    return float(average_precision_score(y, p))


def topk_metrics(y: np.ndarray, p: np.ndarray) -> tuple[float, float]:
    positives = int(y.sum())
    if positives == 0:
        return np.nan, np.nan
    top = np.argsort(-p)[:positives]
    return float(y[top].mean()), float(y[top].sum() / positives)


def make_weighted_model(c: float) -> Pipeline:
    return Pipeline(
        [
            ("impute", SimpleImputer(strategy="constant", fill_value=0.0)),
            ("scale", StandardScaler(with_mean=False)),
            ("clf", LogisticRegression(C=c, max_iter=5000, solver="lbfgs")),
        ]
    )


def sample_weights(frame: pd.DataFrame, spec: ScoreSpec) -> np.ndarray:
    weights = np.full(len(frame), spec.other_weight, dtype=np.float64)
    hard = frame["pair_is_e95_e101"].to_numpy(dtype=bool)
    pos = frame["e72_neighbor_label"].to_numpy(dtype=bool)
    weights[hard] = spec.hard_weight
    weights[pos] = 1.0
    return weights


def weighted_logit_fit_predict(
    train: pd.DataFrame,
    test: pd.DataFrame,
    cols: list[str],
    spec: ScoreSpec,
) -> np.ndarray:
    model = make_weighted_model(spec.c)
    model.fit(train[cols], train["e72_neighbor_label"], clf__sample_weight=sample_weights(train, spec))
    return model.predict_proba(test[cols])[:, 1]


def prototype_train_score(
    train: pd.DataFrame,
    test: pd.DataFrame,
    cols: list[str],
) -> np.ndarray:
    """Distance score: close to E72 positives and far from exact-boundary hard negatives."""
    imputer = SimpleImputer(strategy="constant", fill_value=0.0)
    scaler = StandardScaler()
    x_train = scaler.fit_transform(imputer.fit_transform(train[cols]))
    x_test = scaler.transform(imputer.transform(test[cols]))
    y = train["e72_neighbor_label"].to_numpy(dtype=bool)
    hard = train["pair_is_e95_e101"].to_numpy(dtype=bool)
    neg = ~y
    if y.sum() == 0 or hard.sum() == 0:
        raise ValueError("prototype needs both E72 positives and exact-boundary hard negatives")
    pos_centroid = x_train[y].mean(axis=0)
    hard_centroid = x_train[hard].mean(axis=0)
    neg_centroid = x_train[neg].mean(axis=0)

    def raw_score(x: np.ndarray) -> np.ndarray:
        d_pos = np.linalg.norm(x - pos_centroid, axis=1)
        d_hard = np.linalg.norm(x - hard_centroid, axis=1)
        d_neg = np.linalg.norm(x - neg_centroid, axis=1)
        return 0.75 * (d_hard - d_pos) + 0.25 * (d_neg - d_pos)

    train_score = raw_score(x_train)
    test_score = raw_score(x_test)
    cal = LogisticRegression(C=0.5, max_iter=5000, solver="lbfgs")
    cal.fit(train_score.reshape(-1, 1), train["e72_neighbor_label"], sample_weight=sample_weights(train, SPECS[0]))
    return cal.predict_proba(test_score.reshape(-1, 1))[:, 1]


def score_oof(data: pd.DataFrame, view: e190.FeatureView, spec: ScoreSpec, group_col: str) -> pd.DataFrame:
    cols = e190.feature_cols(data, view)
    rows: list[dict[str, Any]] = []
    for group in sorted(data[group_col].dropna().unique()):
        test_mask = data[group_col].eq(group)
        train = data.loc[~test_mask].copy()
        test = data.loc[test_mask].copy()
        can_fit = train["e72_neighbor_label"].nunique() == 2
        if spec.kind == "prototype":
            can_fit = can_fit and bool(train["pair_is_e95_e101"].any())
        if not can_fit or test.empty:
            for rec in test.to_dict("records"):
                rows.append(
                    {
                        "feature_view": view.name,
                        "score_spec": spec.name,
                        "split": f"loo_{group_col}",
                        "heldout": group,
                        "pair_id": rec["pair_id"],
                        "new_file": rec["new_file"],
                        "base_file": rec["base_file"],
                        "pair_context": rec["pair_context"],
                        "label": int(rec["e72_neighbor_label"]),
                        "pair_is_e95_e101": bool(rec["pair_is_e95_e101"]),
                        "pair_is_e72_frontier_neighbor": bool(rec["pair_is_e72_frontier_neighbor"]),
                        "prob": np.nan,
                        "skipped": True,
                    }
                )
            continue
        if spec.kind == "prototype":
            prob = prototype_train_score(train, test, cols)
        else:
            prob = weighted_logit_fit_predict(train, test, cols, spec)
        for rec, p in zip(test.to_dict("records"), prob):
            rows.append(
                {
                    "feature_view": view.name,
                    "score_spec": spec.name,
                    "split": f"loo_{group_col}",
                    "heldout": group,
                    "pair_id": rec["pair_id"],
                    "new_file": rec["new_file"],
                    "base_file": rec["base_file"],
                    "pair_context": rec["pair_context"],
                    "label": int(rec["e72_neighbor_label"]),
                    "pair_is_e95_e101": bool(rec["pair_is_e95_e101"]),
                    "pair_is_e72_frontier_neighbor": bool(rec["pair_is_e72_frontier_neighbor"]),
                    "prob": float(p),
                    "skipped": False,
                }
            )
    return pd.DataFrame(rows)


def score_any_file_oof(data: pd.DataFrame, view: e190.FeatureView, spec: ScoreSpec) -> pd.DataFrame:
    cols = e190.feature_cols(data, view)
    files = sorted(set(data["new_file"]).union(set(data["base_file"])))
    rows: list[dict[str, Any]] = []
    for file_name in files:
        test_mask = data["new_file"].eq(file_name) | data["base_file"].eq(file_name)
        train = data.loc[~test_mask].copy()
        test = data.loc[test_mask].copy()
        can_fit = train["e72_neighbor_label"].nunique() == 2
        if spec.kind == "prototype":
            can_fit = can_fit and bool(train["pair_is_e95_e101"].any())
        if not can_fit or test.empty:
            for rec in test.to_dict("records"):
                rows.append(
                    {
                        "feature_view": view.name,
                        "score_spec": spec.name,
                        "split": "loo_any_file",
                        "heldout": file_name,
                        "pair_id": rec["pair_id"],
                        "new_file": rec["new_file"],
                        "base_file": rec["base_file"],
                        "pair_context": rec["pair_context"],
                        "label": int(rec["e72_neighbor_label"]),
                        "pair_is_e95_e101": bool(rec["pair_is_e95_e101"]),
                        "pair_is_e72_frontier_neighbor": bool(rec["pair_is_e72_frontier_neighbor"]),
                        "prob": np.nan,
                        "skipped": True,
                    }
                )
            continue
        if spec.kind == "prototype":
            prob = prototype_train_score(train, test, cols)
        else:
            prob = weighted_logit_fit_predict(train, test, cols, spec)
        for rec, p in zip(test.to_dict("records"), prob):
            rows.append(
                {
                    "feature_view": view.name,
                    "score_spec": spec.name,
                    "split": "loo_any_file",
                    "heldout": file_name,
                    "pair_id": rec["pair_id"],
                    "new_file": rec["new_file"],
                    "base_file": rec["base_file"],
                    "pair_context": rec["pair_context"],
                    "label": int(rec["e72_neighbor_label"]),
                    "pair_is_e95_e101": bool(rec["pair_is_e95_e101"]),
                    "pair_is_e72_frontier_neighbor": bool(rec["pair_is_e72_frontier_neighbor"]),
                    "prob": float(p),
                    "skipped": False,
                }
            )
    return pd.DataFrame(rows)


def summarize(pred: pd.DataFrame) -> dict[str, Any]:
    valid = pred[~pred["skipped"] & pred["prob"].notna()].copy()
    out: dict[str, Any] = {
        "feature_view": pred["feature_view"].iloc[0],
        "score_spec": pred["score_spec"].iloc[0],
        "split": pred["split"].iloc[0],
        "n_rows": int(len(valid)),
        "n_pos": int(valid["label"].sum()) if not valid.empty else 0,
        "skipped_rows": int(pred["skipped"].sum()),
        "skipped_positive_rows": int(pred.loc[pred["skipped"], "label"].sum()),
    }
    if valid.empty:
        out.update(
            {
                "auc": np.nan,
                "avg_precision": np.nan,
                "logloss": np.nan,
                "topk_precision": np.nan,
                "topk_recall": np.nan,
                "exact_e95_e101_mean_prob": np.nan,
                "exact_e95_e101_max_prob": np.nan,
                "e72_positive_min_prob": np.nan,
                "e72_positive_mean_prob": np.nan,
                "non_e72_p95_prob": np.nan,
            }
        )
        return out
    y = valid["label"].to_numpy(dtype=int)
    p = valid["prob"].to_numpy(dtype=np.float64)
    top_prec, top_rec = topk_metrics(y, p)
    out.update(
        {
            "auc": safe_auc(y, p),
            "avg_precision": safe_ap(y, p),
            "logloss": float(log_loss(y, np.clip(p, EPS, 1.0 - EPS), labels=[0, 1]))
            if len(np.unique(y)) > 1
            else np.nan,
            "topk_precision": top_prec,
            "topk_recall": top_rec,
            "exact_e95_e101_mean_prob": float(valid.loc[valid["pair_is_e95_e101"], "prob"].mean())
            if valid["pair_is_e95_e101"].any()
            else np.nan,
            "exact_e95_e101_max_prob": float(valid.loc[valid["pair_is_e95_e101"], "prob"].max())
            if valid["pair_is_e95_e101"].any()
            else np.nan,
            "e72_positive_min_prob": float(valid.loc[valid["label"].eq(1), "prob"].min()) if y.sum() else np.nan,
            "e72_positive_mean_prob": float(valid.loc[valid["label"].eq(1), "prob"].mean()) if y.sum() else np.nan,
            "non_e72_p95_prob": float(np.quantile(valid.loc[valid["label"].eq(0), "prob"], 0.95))
            if (1 - y).sum()
            else np.nan,
        }
    )
    out["boundary_clean_gate"] = bool(
        out["topk_recall"] >= 2.0 / 3.0
        and out["exact_e95_e101_mean_prob"] <= 0.20
        and out["exact_e95_e101_max_prob"] <= 0.30
    )
    return out


def fit_full_and_score_branches(data: pd.DataFrame, candidates: pd.DataFrame) -> pd.DataFrame:
    branches = e186.branch_zrecords()
    branches = e190.abs_features(branches)
    rows: list[pd.DataFrame] = []
    for rec in candidates.to_dict("records"):
        view = next(v for v in e190.FEATURE_VIEWS if v.name == rec["feature_view"])
        spec = next(s for s in SPECS if s.name == rec["score_spec"])
        cols = e190.feature_cols(data, view)
        score_frame = branches.copy()
        for col in cols:
            if col not in score_frame.columns:
                score_frame[col] = 0.0
        if spec.kind == "prototype":
            prob = prototype_train_score(data, score_frame, cols)
            known_prob = prototype_train_score(data, data, cols)
        else:
            model = make_weighted_model(spec.c)
            model.fit(data[cols], data["e72_neighbor_label"], clf__sample_weight=sample_weights(data, spec))
            prob = model.predict_proba(score_frame[cols])[:, 1]
            known_prob = model.predict_proba(data[cols])[:, 1]
        neg_prob = known_prob[data["e72_neighbor_label"].to_numpy(dtype=int) == 0]
        pos_prob = known_prob[data["e72_neighbor_label"].to_numpy(dtype=int) == 1]
        out = branches[["candidate", "scenario", "n_diff_cells", "top_targets"]].copy()
        out.insert(0, "score_spec", spec.name)
        out.insert(0, "feature_view", view.name)
        out["e72_boundary_aware_prob"] = prob
        out["known_non_e72_p95"] = float(np.quantile(neg_prob, 0.95)) if len(neg_prob) else np.nan
        out["known_min_positive"] = float(pos_prob.min()) if len(pos_prob) else np.nan
        out["above_non_e72_p95"] = out["e72_boundary_aware_prob"] >= out["known_non_e72_p95"]
        out["above_min_positive"] = out["e72_boundary_aware_prob"] >= out["known_min_positive"]
        rows.append(out)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def write_report(summary: pd.DataFrame, oof: pd.DataFrame, branches: pd.DataFrame) -> None:
    sort_cols = ["boundary_clean_gate", "split", "feature_view", "score_spec"]
    summary_view = summary.sort_values(sort_cols, ascending=[False, True, True, True]).copy()
    pair_clean = summary[
        summary["split"].eq("loo_pair_id")
        & summary["boundary_clean_gate"].fillna(False)
    ].copy()
    support_clean = pair_clean[pair_clean["feature_view"].str.contains("support|all", regex=True)].copy()
    branch_summary = pd.DataFrame()
    if not branches.empty:
        branch_summary = (
            branches.groupby(["feature_view", "score_spec", "candidate"])
            .agg(
                scenario_count=("scenario", "count"),
                contam_prob_mean=("e72_boundary_aware_prob", "mean"),
                contam_prob_max=("e72_boundary_aware_prob", "max"),
                above_non_e72_p95_rate=("above_non_e72_p95", "mean"),
                above_min_positive_rate=("above_min_positive", "mean"),
            )
            .reset_index()
            .sort_values(["feature_view", "score_spec", "candidate"])
        )
    positive_contexts = (
        oof[
            oof["split"].eq("loo_pair_context")
            & oof["label"].eq(1)
            & oof["prob"].notna()
        ]
        .groupby(["feature_view", "score_spec", "heldout"])
        .agg(n=("label", "size"), mean_prob=("prob", "mean"), min_prob=("prob", "min"))
        .reset_index()
        .sort_values(["feature_view", "score_spec", "heldout"])
    )
    best_pair = summary[
        summary["split"].eq("loo_pair_id")
    ].sort_values(
        ["boundary_clean_gate", "topk_recall", "exact_e95_e101_mean_prob", "avg_precision"],
        ascending=[False, False, True, False],
    ).head(1)
    if best_pair.empty:
        best_line = "none"
    else:
        r = best_pair.iloc[0]
        best_line = (
            f"`{r['feature_view']}` / `{r['score_spec']}` with top-k recall "
            f"`{float(r['topk_recall']):.3f}` and exact E95/E101 mean "
            f"`{float(r['exact_e95_e101_mean_prob']):.3f}`"
        )
    support_sentence = (
        "No support-containing pair-LOO row passes the clean boundary gate; explicit hard-negative weighting "
        "does not rehabilitate support as a live gate."
        if support_clean.empty
        else f"`{len(support_clean)}` support-containing pair-LOO rows pass the clean boundary gate; they still need live-branch sanity checks."
    )
    report = f"""# E191 Boundary-Aware E72 Score

## Question

Can exact E95/E101 be used as an explicit hard negative so that E72-neighbor
contamination remains detectable while support-heavy false positives disappear?

## Result In One Sentence

Best pair-LOO boundary-aware row is {best_line}. {support_sentence}

## Summary

{md(summary_view, ['feature_view', 'score_spec', 'split', 'n_rows', 'n_pos', 'auc', 'avg_precision', 'topk_precision', 'topk_recall', 'exact_e95_e101_mean_prob', 'exact_e95_e101_max_prob', 'e72_positive_min_prob', 'non_e72_p95_prob', 'boundary_clean_gate', 'skipped_rows', 'skipped_positive_rows'], n=120)}

## Pair-LOO Clean Boundary Rows

{md(pair_clean.sort_values(['feature_view', 'score_spec']), ['feature_view', 'score_spec', 'auc', 'avg_precision', 'topk_precision', 'topk_recall', 'exact_e95_e101_mean_prob', 'exact_e95_e101_max_prob', 'e72_positive_min_prob', 'non_e72_p95_prob'], n=80)}

## Positive Context Holdouts

{md(positive_contexts, n=120)}

## Live Branch Scores

{md(branch_summary, ['feature_view', 'score_spec', 'candidate', 'scenario_count', 'contam_prob_mean', 'contam_prob_max', 'above_non_e72_p95_rate', 'above_min_positive_rate'], n=120)}

## Interpretation

- Passing pair-LOO is necessary but not sufficient, because all E72-positive
  examples still share one anchor file.
- If support-containing clean rows exist only by aggressively downweighting
  non-boundary negatives, they are narrow contrastive diagnostics rather than
  deployable gates.
- A deployable support gate still needs E72-heldout or one-class calibration;
  this experiment only tests whether the exact E95/E101 false positive can be
  controlled at all.

## Decision

No submission is created. Use this as an E72/support diagnostic only.
"""
    REPORT_OUT.write_text(report)


def main() -> None:
    z, _ = e190.make_inputs()
    z["e72_neighbor_label"] = z["pair_is_e72_frontier_neighbor"].astype(int)
    all_oof: list[pd.DataFrame] = []
    all_summary: list[dict[str, Any]] = []
    active_views = [view for view in e190.FEATURE_VIEWS if view.name in ACTIVE_VIEW_NAMES]
    for view in active_views:
        for spec in SPECS:
            for group_col in ("pair_id", "pair_context"):
                pred = score_oof(z, view, spec, group_col)
                all_oof.append(pred)
                all_summary.append(summarize(pred))
    oof = pd.concat(all_oof, ignore_index=True)
    summary = pd.DataFrame(all_summary)
    pair_candidates = summary[
        summary["split"].eq("loo_pair_id")
        & summary["boundary_clean_gate"].fillna(False)
    ][["feature_view", "score_spec"]].drop_duplicates()
    # Any-file LOO is expensive and mostly repeats E190's one-positive-file
    # blind spot. Run it only for rows that already pass the pair-level boundary
    # gate, because only those rows could plausibly become a support diagnostic.
    for rec in pair_candidates.to_dict("records"):
        view = next(v for v in active_views if v.name == rec["feature_view"])
        spec = next(s for s in SPECS if s.name == rec["score_spec"])
        pred = score_any_file_oof(z, view, spec)
        all_oof.append(pred)
        all_summary.append(summarize(pred))
    oof = pd.concat(all_oof, ignore_index=True)
    summary = pd.DataFrame(all_summary)
    branches = fit_full_and_score_branches(z, pair_candidates)
    summary.to_csv(SUMMARY_OUT, index=False)
    oof.to_csv(OOF_OUT, index=False)
    branches.to_csv(BRANCH_OUT, index=False)
    write_report(summary, oof, branches)
    print(f"Wrote {SUMMARY_OUT}")
    print(f"Wrote {OOF_OUT}")
    print(f"Wrote {BRANCH_OUT}")
    print(f"Wrote {REPORT_OUT}")


if __name__ == "__main__":
    main()
