#!/usr/bin/env python3
"""E254: atlas for the E237/E250 OOF-vs-materialization conflict.

E253 found a sharp contradiction:

- train OOF prefers the E237/E250 shared intersection.
- submission-side materialization rejects the intersection and prefers the union.

This script localizes that contradiction by comparing Q3 cell groups across
train OOF benefit, test hard-tail support/adverse anatomy, and visible
feature-NN/context statistics.

No public LB is used and no submission is created.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, load_sub  # noqa: E402
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402
import e162_branch_readability_flip_thresholds as e162  # noqa: E402
import e222_e211_support_tail_audit as e222  # noqa: E402
import e230_e224_support_tail_prune_audit as e230  # noqa: E402
import e237_cell_decisive_jepa_target as e237  # noqa: E402
import e249_feature_nn1_decisive_oof_audit as e249  # noqa: E402
import e251_e237_e250_cellset_contrast as e251  # noqa: E402
import e253_e237_e250_union_oof_analogue as e253  # noqa: E402


TRAIN_GROUP_OUT = OUT / "e254_e237_e250_conflict_train_group_summary.csv"
TEST_GROUP_OUT = OUT / "e254_e237_e250_conflict_test_group_summary.csv"
SHIFT_OUT = OUT / "e254_e237_e250_conflict_feature_shift.csv"
REPORT_OUT = OUT / "e254_e237_e250_conflict_atlas_report.md"

Q3_IDX = TARGETS.index("Q3")
GROUP_ORDER = ["shared", "e237_only", "e250_only", "union", "none"]


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 40, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return e138.md_table(view.head(n), floatfmt)


def group_label(d237: np.ndarray, d250: np.ndarray) -> np.ndarray:
    out = np.full(len(d237), "none", dtype=object)
    out[d237 & d250] = "shared"
    out[d237 & ~d250] = "e237_only"
    out[~d237 & d250] = "e250_only"
    return out


def add_union_group(df: pd.DataFrame) -> pd.DataFrame:
    union = df[df["group"].isin(["shared", "e237_only", "e250_only"])].copy()
    union["group"] = "union"
    return pd.concat([df, union], ignore_index=True)


def safe_weighted_mean(x: pd.Series, w: pd.Series) -> float:
    ww = w.to_numpy(dtype=np.float64)
    xx = x.to_numpy(dtype=np.float64)
    den = float(np.sum(ww))
    if den <= 0.0:
        return float("nan")
    return float(np.average(xx, weights=ww))


def train_cells() -> pd.DataFrame:
    train_aug, _, feats, _ = e249.build_augmented_frames()
    train_df = train_aug[train_aug["task_name"].isin(e237.CONTROL_TASKS)].reset_index(drop=True)
    p237, _, amp237 = e253.parent_oof(
        train_df,
        feats,
        {
            "source_scope": "all3",
            "view": "latent_no_targetid",
            "model": "hgb_shallow",
            "split": "subject5",
            "target_kind": "risk",
            "tail_q": 0.10,
            "policy": "drop_q3_top25",
        },
    )
    p250, _, amp250 = e253.parent_oof(
        train_df,
        feats,
        {
            "source_scope": "all3",
            "view": "latent_no_targetid_featnn1",
            "model": "hgb_shallow",
            "split": "row5",
            "target_kind": "risk",
            "tail_q": 0.10,
            "policy": "drop_q3_top21",
        },
    )
    q3 = train_df[train_df["task_name"].eq("q3_e224")].copy().reset_index(drop=True)
    q3_idx = train_df.index[train_df["task_name"].eq("q3_e224")].to_numpy(dtype=int)
    d237 = np.asarray(amp237[q3_idx], dtype=np.float64) < 0.05
    d250 = np.asarray(amp250[q3_idx], dtype=np.float64) < 0.05
    q3["group"] = group_label(d237, d250)
    q3["p237_bad"] = p237[q3_idx]
    q3["p250_bad"] = p250[q3_idx]
    q3["pmax_bad"] = np.maximum(q3["p237_bad"], q3["p250_bad"])
    q3["selected_union"] = q3["group"].isin(["shared", "e237_only", "e250_only"])
    return q3


def test_cells() -> tuple[pd.DataFrame, pd.DataFrame]:
    _, sub_aug, _, _ = e249.build_augmented_frames()
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    priors = e162.prior_arrays(sample)
    e154 = e230.load_prob(e237.E154_FILE, sample)
    e224 = e230.load_prob(e237.E224_FILE, sample)
    e237_pred = e251.load_prob(e251.E237_FILE, sample)
    e250_pred = e251.load_prob(e251.E250_FILE, sample)
    rows237 = e251.q3_drop_rows(e237_pred, e224)
    rows250 = e251.q3_drop_rows(e250_pred, e224)
    sub_q3 = sub_aug[sub_aug["task_name"].eq("q3_e224")].sort_values("row_idx").reset_index(drop=True).copy()
    row_idx = sub_q3["row_idx"].to_numpy(dtype=int)
    d237 = np.array([int(r) in rows237 for r in row_idx], dtype=bool)
    d250 = np.array([int(r) in rows250 for r in row_idx], dtype=bool)
    sub_q3["group"] = group_label(d237, d250)
    sub_q3["selected_union"] = sub_q3["group"].isin(["shared", "e237_only", "e250_only"])

    spec = e222.Candidate(
        candidate_id="e224_original",
        file_name=e237.E224_FILE,
        anchor_file=e237.E154_FILE,
        family="e224_q3_scale_pareto",
        status="baseline",
        note="Per-cell E224-vs-E154 anatomy for Q3 group conflict.",
    )
    cells = e222.cell_table(spec, "graft_vs_e154", e224, e154, e237.E154_FILE, priors, sample)
    q3_cells = cells[cells["target"].eq("Q3")].copy()
    q3_cells["group"] = group_label(
        q3_cells["row_idx"].astype(int).isin(rows237).to_numpy(),
        q3_cells["row_idx"].astype(int).isin(rows250).to_numpy(),
    )
    return sub_q3, q3_cells


def train_summary(train_q3: pd.DataFrame) -> pd.DataFrame:
    df = add_union_group(train_q3)
    rows: list[dict[str, Any]] = []
    for group in GROUP_ORDER:
        part = df[df["group"].eq(group)].copy()
        if part.empty:
            continue
        rows.append(
            {
                "group": group,
                "n": int(len(part)),
                "benefit_mean": float(part["benefit"].mean()),
                "benefit_median": float(part["benefit"].median()),
                "benefit_min": float(part["benefit"].min()),
                "benefit_max": float(part["benefit"].max()),
                "benefit_negative_rate": float((part["benefit"] < 0.0).mean()),
                "true_label_mean": float(part["true_label"].mean()),
                "base_prob_mean": float(part["base_prob"].mean()),
                "full_prob_mean": float(part["full_prob"].mean()),
                "abs_logit_step_mean": float(part["abs_logit_step"].mean()),
                "featnn1_dist_mean": float(part["featnn1_dist"].mean()),
                "featnn1_total_smooth_gain_mean": float(part["featnn1_total_smooth_gain"].mean()),
                "featnn1_full_pair_abs_logit_mean": float(part["featnn1_full_pair_abs_logit"].mean()),
                "p237_bad_mean": float(part["p237_bad"].mean()),
                "p250_bad_mean": float(part["p250_bad"].mean()),
                "pmax_bad_mean": float(part["pmax_bad"].mean()),
            }
        )
    return pd.DataFrame(rows)


def test_summary(test_q3: pd.DataFrame, q3_cells: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    context = add_union_group(test_q3)
    anatomy = add_union_group(q3_cells)
    for group in GROUP_ORDER:
        ctx = context[context["group"].eq(group)].copy()
        cells = anatomy[anatomy["group"].eq(group)].copy()
        if ctx.empty and cells.empty:
            continue
        rec: dict[str, Any] = {
            "group": group,
            "n_context": int(len(ctx)),
            "base_prob_mean": float(ctx["base_prob"].mean()) if not ctx.empty else np.nan,
            "full_prob_mean": float(ctx["full_prob"].mean()) if not ctx.empty else np.nan,
            "abs_logit_step_mean": float(ctx["abs_logit_step"].mean()) if not ctx.empty else np.nan,
            "featnn1_dist_mean": float(ctx["featnn1_dist"].mean()) if not ctx.empty else np.nan,
            "featnn1_total_smooth_gain_mean": float(ctx["featnn1_total_smooth_gain"].mean()) if not ctx.empty else np.nan,
            "featnn1_full_pair_abs_logit_mean": float(ctx["featnn1_full_pair_abs_logit"].mean()) if not ctx.empty else np.nan,
            "n_cells": int(len(cells)),
        }
        if cells.empty:
            rec.update(
                {
                    "e224_expected_focus_sum": np.nan,
                    "e224_adverse_sum": np.nan,
                    "support_prob_focus_weighted": np.nan,
                    "top1_over_abs_expected": np.nan,
                    "swing_sum": np.nan,
                }
            )
        else:
            expected = float(cells["expected_focus"].sum())
            swing = cells["swing"].to_numpy(dtype=np.float64)
            rec.update(
                {
                    "e224_expected_focus_sum": expected,
                    "e224_adverse_sum": float(cells["adverse_delta"].sum()),
                    "support_prob_focus_weighted": safe_weighted_mean(cells["support_prob_focus"], cells["swing"]),
                    "top1_over_abs_expected": float(np.max(swing) / max(abs(expected), 1.0e-15)),
                    "swing_sum": float(swing.sum()),
                    "support_delta_sum": float(cells["support_delta"].sum()),
                }
            )
        rows.append(rec)
    return pd.DataFrame(rows)


def feature_shift(train_q3: pd.DataFrame, test_q3: pd.DataFrame) -> pd.DataFrame:
    features = [
        "base_prob",
        "full_prob",
        "prob_gap",
        "logit_step",
        "abs_logit_step",
        "base_margin",
        "full_margin",
        "featnn1_dist",
        "featnn1_base_prob_absdiff",
        "featnn1_full_prob_absdiff",
        "featnn1_logit_step_absdiff",
        "featnn1_total_smooth_gain",
        "featnn1_total_smooth_gain_mean",
        "featnn1_full_pair_abs_logit",
        "featnn1_base_pair_abs_logit",
    ]
    features = [f for f in features if f in train_q3.columns and f in test_q3.columns]
    train_aug = add_union_group(train_q3)
    test_aug = add_union_group(test_q3)
    rows: list[dict[str, Any]] = []
    for group in ["shared", "e237_only", "e250_only", "union"]:
        tr = train_aug[train_aug["group"].eq(group)]
        te = test_aug[test_aug["group"].eq(group)]
        if tr.empty or te.empty:
            continue
        for feat in features:
            pooled = pd.concat([train_q3[feat], test_q3[feat]], ignore_index=True).astype(float)
            scale = float(pooled.std(ddof=0))
            if not np.isfinite(scale) or scale <= 1.0e-12:
                continue
            train_mean = float(tr[feat].mean())
            test_mean = float(te[feat].mean())
            rows.append(
                {
                    "group": group,
                    "feature": feat,
                    "train_mean": train_mean,
                    "test_mean": test_mean,
                    "std_diff_test_minus_train": float((test_mean - train_mean) / scale),
                    "abs_std_diff": abs(float((test_mean - train_mean) / scale)),
                    "train_n": int(len(tr)),
                    "test_n": int(len(te)),
                }
            )
    return pd.DataFrame(rows).sort_values(["abs_std_diff", "group"], ascending=[False, True])


def main() -> None:
    train_q3 = train_cells()
    test_q3, q3_cells = test_cells()
    tr_summary = train_summary(train_q3)
    te_summary = test_summary(test_q3, q3_cells)
    shift = feature_shift(train_q3, test_q3)
    tr_summary.to_csv(TRAIN_GROUP_OUT, index=False)
    te_summary.to_csv(TEST_GROUP_OUT, index=False)
    shift.to_csv(SHIFT_OUT, index=False)

    lines = [
        "# E254 E237/E250 Conflict Atlas",
        "",
        "## Question",
        "",
        "Why does train OOF prefer the E237/E250 shared Q3 intersection while submission-side materialization rejects it and prefers the union?",
        "",
        "## Train OOF Q3 Groups",
        "",
        md_table(tr_summary, n=20),
        "",
        "## Test Q3 Hard-Tail Anatomy",
        "",
        md_table(te_summary, n=20),
        "",
        "## Largest Train/Test Feature Shifts",
        "",
        md_table(shift, n=30),
        "",
        "## Interpretation",
        "",
    ]
    shared_train = tr_summary[tr_summary["group"].eq("shared")].iloc[0]
    shared_test = te_summary[te_summary["group"].eq("shared")].iloc[0]
    union_train = tr_summary[tr_summary["group"].eq("union")].iloc[0]
    union_test = te_summary[te_summary["group"].eq("union")].iloc[0]
    lines.extend(
        [
            f"- Train shared cells are OOF-harmful to keep: benefit_mean `{float(shared_train['benefit_mean']):.9f}` and negative-rate `{float(shared_train['benefit_negative_rate']):.6f}`.",
            f"- Test shared cells look useful to keep under hard-tail priors: E224 expected sum `{float(shared_test['e224_expected_focus_sum']):.9f}` and top1/abs `{float(shared_test['top1_over_abs_expected']):.9f}`.",
            f"- Test union flips the hard-tail anatomy by adding parent-specific cells: E224 expected sum `{float(union_test['e224_expected_focus_sum']):.9f}` versus train union benefit_mean `{float(union_train['benefit_mean']):.9f}`.",
            "- This is a concrete validation-geometry mismatch: overlap/consensus is a good OOF target but a bad public-free hard-tail target.",
        ]
    )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- Do not build an intersection submission despite its OOF strength.",
            "- Do not promote E252 as OOF-certified despite its materialization strength.",
            "- The next useful target is a contrastive head that explicitly separates OOF-harmful consensus cells from test hard-tail-adverse parent-specific cells.",
            "- Public LB is not used and no submission is created.",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("[E254 train summary]")
    print(tr_summary.round(9).to_string(index=False))
    print("\n[E254 test summary]")
    print(te_summary.round(9).to_string(index=False))
    print("\n[E254 top shifts]")
    print(shift.head(20).round(9).to_string(index=False))
    print(f"\nwrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
