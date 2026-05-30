#!/usr/bin/env python3
"""E250: materialization stress for E249 feature-NN1 decisive-cell policies.

E249 found that feature-NN1 context can improve OOF loss when used inside the
E237 decisive-cell target, but the best rows are broad Q3 drops with weak
tail-AUC. This script applies the same E237 graft-vs-E154 and actual-vs-E95
stress gate before any submission is considered.

Submission files are only kept if a candidate passes the E237 public-free gate.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import KEYS, TARGETS  # noqa: E402
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402
import e237_cell_decisive_jepa_target as e237  # noqa: E402
import e249_feature_nn1_decisive_oof_audit as e249  # noqa: E402


OOF_IN = OUT / "e249_feature_nn1_decisive_oof_scan.csv"
MATERIAL_SUMMARY_OUT = OUT / "e250_feature_nn1_decisive_materialization_summary.csv"
TARGET_SUMMARY_OUT = OUT / "e250_feature_nn1_decisive_materialization_target_summary.csv"
SELECTED_SUMMARY_OUT = OUT / "e250_feature_nn1_decisive_materialization_selected_summary.csv"
REPORT_OUT = OUT / "e250_feature_nn1_decisive_materialization_report.md"


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 40, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return e138.md_table(view.head(n), floatfmt)


def safe_name(text: str, limit: int = 88) -> str:
    return "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in text)[:limit]


def rename_selected_submissions(selected: pd.DataFrame) -> pd.DataFrame:
    out = selected.copy()
    if out.empty:
        return out
    for idx, row in out.iterrows():
        old_name = str(row.get("submission_file", ""))
        old_path = OUT / old_name
        if not old_name or not old_path.exists():
            continue
        sub = pd.read_csv(old_path)
        pred = np.clip(sub[TARGETS].to_numpy(dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)
        digest = hashlib.sha1(np.round(pred, 10).tobytes()).hexdigest()[:8]
        new_name = f"submission_e250_featnn1_decisive_{safe_name(str(row['candidate_id']))}_{digest}.csv"
        new_path = OUT / new_name
        final = sub[KEYS].copy()
        final[TARGETS] = pred
        final.to_csv(new_path, index=False)
        old_path.unlink(missing_ok=True)
        out.loc[idx, "submission_file"] = new_name
    return out


def write_report(material: pd.DataFrame, targets: pd.DataFrame, selected: pd.DataFrame) -> None:
    graft = material[material["pair_kind"].eq("graft_vs_e154")].copy()
    gate = graft[graft["e237_gate"].astype(bool)].sort_values("e237_score", ascending=False)
    top_score = graft.sort_values("e237_score", ascending=False)
    top_oof = graft.sort_values("oof_loss_vs_full")
    q3_only = graft[(graft["q3_dropped_cells"] > 0) & (graft["s4_dropped_cells"] == 0)].sort_values(
        "e237_score", ascending=False
    )
    cols = [
        "candidate_id",
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
        "q3_top1_over_abs_expected",
        "actual_expected_delta_vs_e224",
        "actual_adverse_reduction_vs_e224",
        "e237_gate",
        "e237_score",
    ]
    selected_cols = [*cols, "submission_file"]
    lines = [
        "# E250 Feature-NN1 Decisive Materialization Stress",
        "",
        "## Question",
        "",
        "Do E249's OOF-improved feature-NN1 decisive policies survive the same E237 graft/actual public-free stress gate?",
        "",
        "## Headline",
        "",
        f"- Materialized rows audited: `{len(graft)}` graft rows.",
        f"- E237-gate pass count: `{len(gate)}`.",
        f"- Selected submission files kept: `{len(selected)}`.",
        "",
        "## Gate-Passing Rows",
        "",
        md_table(gate, cols, n=20),
        "",
        "## Top By E237 Score",
        "",
        md_table(top_score, cols, n=20),
        "",
        "## Top By OOF Loss",
        "",
        md_table(top_oof, cols, n=20),
        "",
        "## Q3-Only Top Rows",
        "",
        md_table(q3_only, cols, n=20),
        "",
        "## Selected Files",
        "",
        md_table(selected, selected_cols, n=20),
        "",
        "## Decision",
        "",
    ]
    if selected.empty:
        lines.append(
            "- E249's OOF gain does not survive materialization stress. Feature-NN1 context helps local OOF policy search, but the current public-free gate rejects it as a submission lane."
        )
    else:
        lines.append(
            "- At least one E249 policy survives the E237 stress gate. Treat any selected file as a feature-NN1 decisive-cell public sensor, not as a sibling sweep."
        )
    lines.append("- Public LB is not used.")
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    if not OOF_IN.exists():
        e249.main()
    oof = pd.read_csv(OOF_IN)
    train_aug, sub_aug, feats, _ = e249.build_augmented_frames()
    train_df = train_aug[train_aug["task_name"].isin(e237.CONTROL_TASKS)].reset_index(drop=True)
    sub_df = sub_aug[sub_aug["task_name"].isin(e237.CONTROL_TASKS)].reset_index(drop=True)
    material, targets, selected = e237.scan_materializations(oof, train_df, sub_df, feats)
    selected = rename_selected_submissions(selected)
    material.to_csv(MATERIAL_SUMMARY_OUT, index=False)
    targets.to_csv(TARGET_SUMMARY_OUT, index=False)
    selected.to_csv(SELECTED_SUMMARY_OUT, index=False)
    write_report(material, targets, selected)
    graft = material[material["pair_kind"].eq("graft_vs_e154")].copy()
    print("[E250 gate summary]")
    print(f"graft rows: {len(graft)}")
    print(f"gate pass: {int(graft['e237_gate'].astype(bool).sum()) if not graft.empty else 0}")
    print(f"selected files: {len(selected)}")
    print("\n[E250 top by score]")
    if not graft.empty:
        print(
            graft.sort_values("e237_score", ascending=False)
            [[
                "candidate_id",
                "policy",
                "q3_dropped_cells",
                "s4_dropped_cells",
                "oof_loss_vs_full",
                "oof_tail_auc",
                "expected_loss_vs_e224",
                "adverse_reduction_vs_e224",
                "support_gain_vs_e224",
                "q3_top1_over_abs_expected",
                "actual_expected_delta_vs_e224",
                "actual_adverse_reduction_vs_e224",
                "e237_gate",
                "e237_score",
            ]]
            .head(12)
            .round(9)
            .to_string(index=False)
        )
    print(f"\nwrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
