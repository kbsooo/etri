#!/usr/bin/env python3
"""E266: materialization stress for human/social tail JEPA candidates.

E264 showed human_late can predict harmful Q3/S4 tail movement locally. E265
showed broad policy gates are too easy. E266 asks the stricter question:

Do the sharper human/social OOF survivors pass E224/E154 materialization-side
public-free stress: expected focus, adverse capacity, support, Q3 top-cell
concentration, and actual-vs-E95?

If a candidate passes, e237.scan_materializations will create a submission file.
"""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402
import e237_cell_decisive_jepa_target as e237  # noqa: E402
import e264_human_social_tail_jepa_oof as e264  # noqa: E402


E264_SCAN = OUT / "e264_human_social_tail_jepa_oof_scan.csv"
SUMMARY_OUT = OUT / "e266_human_social_tail_materialization_summary.csv"
TARGETS_OUT = OUT / "e266_human_social_tail_materialization_targets.csv"
SELECTED_OUT = OUT / "e266_human_social_tail_materialization_selected.csv"
POOL_OUT = OUT / "e266_human_social_tail_materialization_pool.csv"
REPORT_OUT = OUT / "e266_human_social_tail_materialization_report.md"


SHARP_POLICIES = {
    "drop_global_top10",
    "drop_global_top13",
    "drop_global_top21",
    "drop_global_top25",
    "drop_global_top40",
    "drop_global_top50",
    "drop_global_top75",
    "drop_global_p05",
    "drop_global_p10",
    "drop_q3_top10",
    "drop_q3_top13",
    "drop_q3_top21",
    "drop_q3_top25",
    "drop_q3_top40",
    "drop_q3_top50",
    "drop_q3_p05",
    "drop_q3_p10",
    "drop_s4_top10",
    "drop_s4_top13",
    "drop_s4_top21",
    "drop_s4_top25",
    "drop_s4_top40",
    "drop_s4_top50",
    "drop_s4_p05",
    "drop_s4_p10",
    "drop_each_top10",
    "drop_each_top13",
    "drop_each_top21",
    "drop_each_top25",
}


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 40, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return e138.md_table(view.head(n), floatfmt)


def build_pool(scan: pd.DataFrame) -> pd.DataFrame:
    allowed_views = {
        "human_late",
        "human_core",
        "latent_human_late",
        "latent_human_core",
    }
    pool = scan[
        scan["view"].isin(allowed_views)
        & scan["strict_lifestyle_gate"].astype(bool)
        & scan["policy"].isin(SHARP_POLICIES)
        & (scan["dropped_cells"] <= 90)
        & (scan["loss_vs_full"] <= -0.00025)
    ].copy()
    if pool.empty:
        return pool
    # Keep diverse candidates: best loss, best Q3, best S4, best tail-AUC, and
    # source/view/model/split representatives.
    picks = [
        pool.sort_values("loss_vs_full").head(40),
        pool.sort_values("q3_loss_vs_full").head(25),
        pool.sort_values("s4_loss_vs_full").head(25),
        pool.sort_values("tail_auc", ascending=False).head(25),
        pool.sort_values(["view", "model", "split", "loss_vs_full"]).groupby(["view", "model", "split"]).head(5),
    ]
    out = pd.concat(picks, ignore_index=True).drop_duplicates(
        ["source_scope", "view", "model", "split", "target_kind", "tail_q", "policy"]
    )
    return out.sort_values(["loss_vs_full", "tail_auc"], ascending=[True, False]).head(80)


def write_report(pool: pd.DataFrame, material: pd.DataFrame, targets: pd.DataFrame, selected: pd.DataFrame) -> None:
    graft = material[material["pair_kind"].eq("graft_vs_e154")].copy() if not material.empty else pd.DataFrame()
    graft_top = graft.sort_values("e237_score", ascending=False).head(30) if not graft.empty else pd.DataFrame()
    selected_view = selected.sort_values("e237_score", ascending=False) if not selected.empty else pd.DataFrame()
    gate_count = int(graft["e237_gate"].sum()) if "e237_gate" in graft else 0
    mat_cols = [
        "candidate_id",
        "source_scope",
        "view",
        "model",
        "split",
        "target_kind",
        "tail_q",
        "policy",
        "q3_dropped_cells",
        "s4_dropped_cells",
        "oof_loss_vs_full",
        "oof_tail_auc",
        "expected_loss_vs_e224",
        "adverse_reduction_vs_e224",
        "support_gain_vs_e224",
        "actual_expected_delta_vs_e224",
        "actual_adverse_reduction_vs_e224",
        "actual_support_gain_vs_e224",
        "q3_top1_over_abs_expected",
        "q3_adverse_delta",
        "e230_q3_risk_top21_overlap",
        "e237_gate",
        "e237_score",
        "submission_file",
    ]
    pool_cols = [
        "view",
        "model",
        "split",
        "source_scope",
        "target_kind",
        "policy",
        "tail_auc",
        "loss_vs_full",
        "q3_loss_vs_full",
        "s4_loss_vs_full",
        "subject_win_rate",
        "dateblock_win_rate",
        "dropped_cells",
        "dropped_q3",
        "dropped_s4",
    ]
    target_cols = [
        "candidate_id",
        "target",
        "expected_focus",
        "adverse_delta",
        "support_prob_focus_swing_weighted",
        "top1_over_abs_expected",
    ]
    if not graft.empty:
        best_loss = float(graft["expected_loss_vs_e224"].min())
        best_adverse = float(graft["adverse_reduction_vs_e224"].max())
        best_support = float(graft["support_gain_vs_e224"].max())
    else:
        best_loss = best_adverse = best_support = float("nan")
    report = f"""# E266 Human/Social Tail Materialization Stress

## Question

Can the E264 human/social tail representation become a submission candidate after E265 blocked broad OOF gates?

Only sharper policies are tested. Broad `p15/p20` lifestyle rollbacks are excluded from the pool.

## Headline

- OOF pool rows: `{len(pool)}`.
- materialization rows: `{len(material)}`.
- graft-side E237 gates: `{gate_count}`.
- selected submissions: `{len(selected)}`.
- best expected_loss_vs_e224: `{best_loss:.9f}`.
- best adverse_reduction_vs_e224: `{best_adverse:.9f}`.
- best support_gain_vs_e224: `{best_support:.9f}`.

## Selected

{md_table(selected_view, mat_cols, 20)}

## Best Materialized Graft Rows

{md_table(graft_top, mat_cols, 30)}

## OOF Pool

{md_table(pool, pool_cols, 40)}

## Target Breakdown

{md_table(targets.sort_values(['candidate_id','target']).head(80) if not targets.empty else targets, target_cols, 80)}

## Decision Rule

- If selected submissions are non-empty, the top file is the first lifestyle-conditioned JEPA submission candidate.
- If selected is empty but expected/adverse/support improve separately, the branch remains diagnostic and needs a stricter learned cell target.
- If materialization is broadly adverse, E264 was mainly an OOF/broad-rollback artifact.
"""
    REPORT_OUT.write_text(report, encoding="utf-8")


def main() -> None:
    train_raw, train_long, sub_long, base_feats = e237.build_frames()
    train_aug, sub_aug, feats = e264.append_human_context(train_raw, train_long, sub_long, base_feats)
    train_df = train_aug[train_aug["task_name"].isin(e237.CONTROL_TASKS)].reset_index(drop=True)
    sub_df = sub_aug[sub_aug["task_name"].isin(e237.ACTIVE_TASKS)].reset_index(drop=True)
    scan = pd.read_csv(E264_SCAN)
    pool = build_pool(scan)
    pool.to_csv(POOL_OUT, index=False)
    if pool.empty:
        material = pd.DataFrame()
        targets = pd.DataFrame()
        selected = pd.DataFrame()
    else:
        material, targets, selected = e237.scan_materializations(pool, train_df, sub_df, feats)
    material.to_csv(SUMMARY_OUT, index=False)
    targets.to_csv(TARGETS_OUT, index=False)
    selected.to_csv(SELECTED_OUT, index=False)
    write_report(pool, material, targets, selected)
    print(f"pool={len(pool)} material={len(material)} selected={len(selected)}")
    print(f"wrote {REPORT_OUT}")


if __name__ == "__main__":
    main()
