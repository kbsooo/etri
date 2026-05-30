#!/usr/bin/env python3
"""E265: negative controls for E264 human/social tail JEPA gates.

E264 produced many strict gates. That can mean the lifestyle representation is
real, or it can mean the policy gate is too easy because broad rollback of the
E224 body helps regardless of the scorer. This script compares E264 against
random bad-probability policies with the same E237 policy machinery.
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


RNG = 20260531 + 265

CONTROL_OUT = OUT / "e265_human_social_tail_negative_controls.csv"
SUMMARY_OUT = OUT / "e265_human_social_tail_negative_control_summary.csv"
REPORT_OUT = OUT / "e265_human_social_tail_negative_controls_report.md"
E264_SCAN = OUT / "e264_human_social_tail_jepa_oof_scan.csv"


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 40, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return e138.md_table(view.head(n), floatfmt)


def labels_for_eval(df: pd.DataFrame, source_scope: str, kind: str, q: float) -> tuple[np.ndarray, np.ndarray]:
    thresholds = e237.thresholds_by_task(df.loc[e237.source_mask(df, source_scope)], q)
    return e237.label_with_thresholds(df, thresholds, kind)


def random_controls(train_df: pd.DataFrame, n_seeds: int = 5) -> pd.DataFrame:
    rows = []
    active = e237.active_mask(train_df)
    keep_policies = {
        "drop_global_top50",
        "drop_global_top75",
        "drop_global_top100",
        "drop_global_p10",
        "drop_global_p15",
        "drop_global_p20",
        "drop_q3_top50",
        "drop_q3_p20",
        "drop_s4_top50",
        "drop_s4_p20",
        "drop_each_top25",
    }
    for source_scope in ["q3s4", "all3"]:
        for kind in ["risk", "contrast"]:
            eval_label, eval_mask = labels_for_eval(train_df, source_scope, kind, 0.10)
            for seed in range(n_seeds):
                rng = np.random.default_rng(RNG + seed * 17 + (0 if source_scope == "q3s4" else 10000))
                # Same random value for Q3/S4 of the same day would be a weaker
                # control; here use independent cell noise to make the control
                # intentionally generous.
                bad_prob = rng.random(len(train_df))
                spec = {
                    "view": "random_cell_noise",
                    "n_features": 0,
                    "model": f"rng{seed:03d}",
                    "split": "control",
                    "source_scope": source_scope,
                    "target_kind": kind,
                    "tail_q": 0.10,
                }
                for policy, amp in e237.policy_amplitudes(train_df, bad_prob).items():
                    if policy not in keep_policies:
                        continue
                    rec = e264.evaluate_policy_with_blocks(train_df, spec, bad_prob, eval_label, amp, policy)
                    rec["eval_mask_rate"] = float(np.mean(eval_mask[active]))
                    rows.append(rec)
    return pd.DataFrame(rows)


def summarize(control: pd.DataFrame, e264_scan: pd.DataFrame) -> pd.DataFrame:
    best_e264 = e264_scan.sort_values("loss_vs_full").head(1).copy()
    best_human = e264_scan[e264_scan["view"].str.startswith("human")].sort_values("loss_vs_full").head(1).copy()
    control_strict = control[control["strict_lifestyle_gate"].astype(bool)]
    rows = [
        {
            "section": "e264_all",
            "rows": len(e264_scan),
            "strict_gates": int(e264_scan["strict_lifestyle_gate"].sum()),
            "best_loss_vs_full": float(e264_scan["loss_vs_full"].min()),
            "best_q3_loss_vs_full": float(e264_scan["q3_loss_vs_full"].min()),
            "best_tail_auc": float(e264_scan["tail_auc"].max()),
        },
        {
            "section": "e264_human_only",
            "rows": int(e264_scan["view"].str.startswith("human").sum()),
            "strict_gates": int(e264_scan[e264_scan["view"].str.startswith("human")]["strict_lifestyle_gate"].sum()),
            "best_loss_vs_full": float(best_human["loss_vs_full"].iloc[0]),
            "best_q3_loss_vs_full": float(e264_scan[e264_scan["view"].str.startswith("human")]["q3_loss_vs_full"].min()),
            "best_tail_auc": float(e264_scan[e264_scan["view"].str.startswith("human")]["tail_auc"].max()),
        },
        {
            "section": "random_cell_noise",
            "rows": len(control),
            "strict_gates": int(control["strict_lifestyle_gate"].sum()),
            "best_loss_vs_full": float(control["loss_vs_full"].min()),
            "best_q3_loss_vs_full": float(control["q3_loss_vs_full"].min()),
            "best_tail_auc": float(control["tail_auc"].max()),
        },
    ]
    summary = pd.DataFrame(rows)
    if not control.empty:
        summary["random_p01_loss_vs_full"] = float(control["loss_vs_full"].quantile(0.01))
        summary["random_p05_loss_vs_full"] = float(control["loss_vs_full"].quantile(0.05))
        summary["random_strict_rate"] = float(control["strict_lifestyle_gate"].mean())
        summary["random_strict_best_loss"] = float(control_strict["loss_vs_full"].min()) if not control_strict.empty else np.nan
    summary["best_e264_file_view"] = best_e264["view"].iloc[0]
    return summary


def write_report(control: pd.DataFrame, summary: pd.DataFrame, e264_scan: pd.DataFrame) -> None:
    control_top = control.sort_values("loss_vs_full").head(20)
    e264_top = e264_scan.sort_values("loss_vs_full").head(20)
    strict_rate = float(control["strict_lifestyle_gate"].mean())
    random_best = float(control["loss_vs_full"].min())
    human_best = float(e264_scan[e264_scan["view"].str.startswith("human")]["loss_vs_full"].min())
    verdict = (
        "human_signal_survives_control"
        if human_best < random_best - 1.0e-4 and strict_rate < 0.20
        else "gate_too_easy_or_needs_sharper_control"
    )
    report = f"""# E265 Human/Social Tail Negative Controls

## Question

Did E264 find real lifestyle tail signal, or is the E237 rollback policy gate so easy that random cell scores also pass?

## Headline

- random control rows: `{len(control)}`.
- random strict gate rate: `{strict_rate:.6f}`.
- best random loss_vs_full: `{random_best:.9f}`.
- best E264 human-only loss_vs_full: `{human_best:.9f}`.
- verdict: `{verdict}`.

## Summary

{md_table(summary, None, 10)}

## Best Random Control Rows

{md_table(control_top, ['view','model','source_scope','target_kind','policy','tail_auc','loss_vs_full','q3_loss_vs_full','s4_loss_vs_full','subject_win_rate','dateblock_win_rate','dropped_cells','dropped_q3','dropped_s4','dropped_mean_benefit','strict_lifestyle_gate'], 20)}

## Best E264 Rows For Reference

{md_table(e264_top, ['view','model','split','source_scope','target_kind','policy','tail_auc','loss_vs_full','q3_loss_vs_full','s4_loss_vs_full','subject_win_rate','dateblock_win_rate','dropped_cells','dropped_q3','dropped_s4','dropped_mean_benefit','strict_lifestyle_gate'], 20)}

## Interpretation

If random controls pass frequently, E264's policy-level strict gate is not enough. The lifestyle representation can still be useful, but the next target must be sharper: cell-tail ranking AUC, top-cell overlap, and materialization-side public-free stress, not just broad rollback policy improvement.
"""
    REPORT_OUT.write_text(report, encoding="utf-8")


def main() -> None:
    train_raw, train_long, sub_long, base_feats = e237.build_frames()
    train_aug, _, _ = e264.append_human_context(train_raw, train_long, sub_long, base_feats)
    train_df = train_aug[train_aug["task_name"].isin(e237.CONTROL_TASKS)].reset_index(drop=True)
    control = random_controls(train_df)
    e264_scan = pd.read_csv(E264_SCAN)
    summary = summarize(control, e264_scan)
    control.to_csv(CONTROL_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    write_report(control, summary, e264_scan)
    print(f"wrote {CONTROL_OUT}")
    print(f"wrote {SUMMARY_OUT}")
    print(f"wrote {REPORT_OUT}")


if __name__ == "__main__":
    main()
