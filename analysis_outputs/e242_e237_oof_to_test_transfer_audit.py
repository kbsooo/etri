#!/usr/bin/env python3
"""E242: OOF-to-test transfer audit for the E237 Q3 decisive-cell branch.

E241 rejected simple residual-PC10 rules as OOF-valid Q3 harmful-row selectors.
The next question is whether E237's learned cell-level policies transfer from
OOF quality to test-side materialization geometry, or whether the selected file
is mostly a product of the public-free graft/actual stress gate.

This is a read-only audit over E237/E240/E241 outputs. It creates no submission.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402


MATERIALIZATION_IN = OUT / "e237_cell_decisive_jepa_target_materialization_scan.csv"
SELECTED_IN = OUT / "e237_cell_decisive_jepa_target_selected.csv"
OOF_IN = OUT / "e237_cell_decisive_jepa_target_oof_scan.csv"
E240_IN = OUT / "e240_e237_residual_rule_ablation_summary.csv"
E241_IN = OUT / "e241_residual_pc10_oof_benefit_validation_scores.csv"

CORR_OUT = OUT / "e242_e237_oof_to_test_transfer_corr.csv"
GATE_OUT = OUT / "e242_e237_oof_to_test_transfer_gate_summary.csv"
RANK_OUT = OUT / "e242_e237_oof_to_test_transfer_rank_audit.csv"
CONFLICT_OUT = OUT / "e242_e237_oof_to_test_transfer_conflicts.csv"
COMPARISON_OUT = OUT / "e242_e237_oof_to_test_transfer_e240_e241_comparison.csv"
REPORT_OUT = OUT / "e242_e237_oof_to_test_transfer_report.md"

EPS = 1.0e-12


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 40, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return e138.md_table(view.head(n), floatfmt)


def rank_corr(a: pd.Series, b: pd.Series) -> float:
    aa = pd.to_numeric(a, errors="coerce")
    bb = pd.to_numeric(b, errors="coerce")
    mask = aa.notna() & bb.notna()
    if int(mask.sum()) < 3:
        return float("nan")
    if float(aa[mask].std(ddof=0)) <= EPS or float(bb[mask].std(ddof=0)) <= EPS:
        return float("nan")
    return float(aa[mask].rank(method="average").corr(bb[mask].rank(method="average")))


def safe_auc(label: pd.Series, score: pd.Series) -> float:
    y = label.astype(int).to_numpy()
    s = pd.to_numeric(score, errors="coerce").to_numpy(dtype=float)
    mask = np.isfinite(s)
    y = y[mask]
    s = s[mask]
    if len(y) == 0 or len(np.unique(y)) < 2:
        return float("nan")
    return float(roc_auc_score(y, s))


def add_directional_scores(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["gate_label"] = out["e237_gate"].astype(bool).astype(int)
    out["oof_gain_vs_full"] = -out["oof_loss_vs_full"].astype(float)
    out["oof_gain_active"] = -out["oof_active_policy_delta"].astype(float)
    out["test_expected_gain_vs_e224"] = -out["expected_loss_vs_e224"].astype(float)
    out["test_actual_gain_vs_e224"] = -out["actual_expected_delta_vs_e224"].astype(float)
    out["q3_top1_safety"] = -out["q3_top1_over_abs_expected"].astype(float)
    out["q3_drop_purity"] = (
        out["q3_dropped_cells"].astype(float)
        / (out["q3_dropped_cells"].astype(float) + out["s4_dropped_cells"].astype(float)).clip(lower=1.0)
    )
    return out


def corr_table(df: pd.DataFrame) -> pd.DataFrame:
    oof_cols = [
        "oof_gain_vs_full",
        "oof_gain_active",
        "oof_tail_auc",
        "oof_subject_win_rate",
        "q3_dropped_cells",
        "s4_dropped_cells",
        "q3_drop_purity",
        "e230_q3_risk_top21_overlap",
        "e230_q3_swing_top25_overlap",
        "e230_q3_expected_positive_overlap",
    ]
    test_cols = [
        "e237_score",
        "test_expected_gain_vs_e224",
        "adverse_reduction_vs_e224",
        "support_gain_vs_e224",
        "test_actual_gain_vs_e224",
        "actual_adverse_reduction_vs_e224",
        "actual_support_gain_vs_e224",
        "q3_top1_safety",
        "gate_label",
    ]
    rows: list[dict[str, Any]] = []
    for left in oof_cols:
        for right in test_cols:
            rows.append(
                {
                    "oof_signal": left,
                    "test_signal": right,
                    "spearman": rank_corr(df[left], df[right]),
                }
            )
    auc_rows = []
    for left in oof_cols:
        auc_rows.append(
            {
                "oof_signal": left,
                "test_signal": "gate_auc",
                "spearman": safe_auc(df["gate_label"], df[left]),
            }
        )
    return pd.concat([pd.DataFrame(rows), pd.DataFrame(auc_rows)], ignore_index=True)


def gate_summary(df: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "oof_gain_vs_full",
        "oof_gain_active",
        "oof_tail_auc",
        "oof_subject_win_rate",
        "test_expected_gain_vs_e224",
        "adverse_reduction_vs_e224",
        "support_gain_vs_e224",
        "test_actual_gain_vs_e224",
        "actual_adverse_reduction_vs_e224",
        "actual_support_gain_vs_e224",
        "q3_top1_over_abs_expected",
        "e230_q3_risk_top21_overlap",
        "e230_q3_swing_top25_overlap",
        "q3_dropped_cells",
        "s4_dropped_cells",
        "e237_score",
    ]
    rows = []
    for label, part in [("gate_false", df[~df["e237_gate"].astype(bool)]), ("gate_true", df[df["e237_gate"].astype(bool)])]:
        row: dict[str, Any] = {"group": label, "n": int(len(part))}
        for col in cols:
            row[col + "_mean"] = float(part[col].mean()) if len(part) else float("nan")
            row[col + "_median"] = float(part[col].median()) if len(part) else float("nan")
        rows.append(row)
    return pd.DataFrame(rows)


def rank_audit(df: pd.DataFrame, selected: pd.DataFrame) -> pd.DataFrame:
    selected_ids = set(selected["candidate_id"].astype(str))
    top_id = str(selected.iloc[0]["candidate_id"]) if len(selected) else ""
    ranking_specs = [
        ("e237_score", False),
        ("oof_gain_vs_full", False),
        ("oof_gain_active", False),
        ("oof_tail_auc", False),
        ("oof_subject_win_rate", False),
        ("test_expected_gain_vs_e224", False),
        ("adverse_reduction_vs_e224", False),
        ("support_gain_vs_e224", False),
        ("test_actual_gain_vs_e224", False),
        ("actual_adverse_reduction_vs_e224", False),
        ("q3_top1_over_abs_expected", True),
    ]
    rows = []
    n = len(df)
    for col, ascending in ranking_specs:
        ordered = df.sort_values(col, ascending=ascending, kind="mergesort").reset_index(drop=True)
        ordered["rank"] = np.arange(1, len(ordered) + 1)
        top_selected = ordered[ordered["candidate_id"].astype(str).isin(selected_ids)].head(1)
        top_file = ordered.iloc[0]
        top237 = ordered[ordered["candidate_id"].astype(str).eq(top_id)]
        rows.append(
            {
                "rank_by": col,
                "ascending": ascending,
                "n_rows": n,
                "best_candidate_id": str(top_file["candidate_id"]),
                "best_is_gate": bool(top_file["e237_gate"]),
                "best_value": float(top_file[col]),
                "first_selected_rank": int(top_selected["rank"].iloc[0]) if len(top_selected) else -1,
                "first_selected_candidate_id": str(top_selected["candidate_id"].iloc[0]) if len(top_selected) else "",
                "first_selected_value": float(top_selected[col].iloc[0]) if len(top_selected) else float("nan"),
                "top_e237_rank": int(top237["rank"].iloc[0]) if len(top237) else -1,
                "top_e237_value": float(top237[col].iloc[0]) if len(top237) else float("nan"),
            }
        )
    return pd.DataFrame(rows)


def conflict_cases(df: pd.DataFrame) -> pd.DataFrame:
    top_oof = (
        df.sort_values("oof_gain_vs_full", ascending=False, kind="mergesort")
        .head(20)
        .assign(conflict_type="oof_strong")
    )
    top_test = (
        df.sort_values("e237_score", ascending=False, kind="mergesort")
        .head(20)
        .assign(conflict_type="test_gate_strong")
    )
    top_expected = (
        df.sort_values("test_expected_gain_vs_e224", ascending=False, kind="mergesort")
        .head(20)
        .assign(conflict_type="expected_strong")
    )
    out = pd.concat([top_oof, top_test, top_expected], ignore_index=True)
    cols = [
        "conflict_type",
        "candidate_id",
        "e237_gate",
        "source_scope",
        "view",
        "model",
        "split",
        "target_kind",
        "tail_q",
        "policy",
        "q3_dropped_cells",
        "s4_dropped_cells",
        "oof_gain_vs_full",
        "oof_tail_auc",
        "oof_subject_win_rate",
        "test_expected_gain_vs_e224",
        "adverse_reduction_vs_e224",
        "support_gain_vs_e224",
        "test_actual_gain_vs_e224",
        "actual_adverse_reduction_vs_e224",
        "e230_q3_risk_top21_overlap",
        "e230_q3_swing_top25_overlap",
        "q3_top1_over_abs_expected",
        "e237_score",
    ]
    return out[cols].drop_duplicates(["conflict_type", "candidate_id"]).reset_index(drop=True)


def e240_e241_comparison(selected: pd.DataFrame) -> pd.DataFrame:
    e240 = pd.read_csv(E240_IN)
    e241 = pd.read_csv(E241_IN)
    top_e237 = selected.iloc[0]
    best_e240 = e240.sort_values("e237_like_score", ascending=False, kind="mergesort").iloc[0]
    pc10_train = e241[(e241["score"].eq("score_pc10")) & (e241["top_frac"].eq(0.10))].iloc[0]
    rows = [
        {
            "item": "E237 top learned selector",
            "source": str(top_e237["candidate_id"]),
            "expected_loss_vs_e224": float(top_e237["expected_loss_vs_e224"]),
            "adverse_reduction_vs_e224": float(top_e237["adverse_reduction_vs_e224"]),
            "support_gain_vs_e224": float(top_e237["support_gain_vs_e224"]),
            "actual_adverse_reduction_vs_e224": float(top_e237["actual_adverse_reduction_vs_e224"]),
            "overlap_e237": 25,
            "overlap_e230_swing25": float(top_e237["e230_q3_swing_top25_overlap"]),
            "oof_or_train_delta": float(top_e237["oof_loss_vs_full"]),
            "oof_or_train_note": "E237 OOF loss_vs_full",
        },
        {
            "item": "E240 best simple selector",
            "source": str(best_e240["selector_id"]),
            "expected_loss_vs_e224": float(best_e240["expected_loss_vs_e224"]),
            "adverse_reduction_vs_e224": float(best_e240["adverse_reduction_vs_e224"]),
            "support_gain_vs_e224": float(best_e240["support_gain_vs_e224"]),
            "actual_adverse_reduction_vs_e224": float(best_e240["actual_adverse_reduction_vs_e224"]),
            "overlap_e237": float(best_e240["overlap_e237"]),
            "overlap_e230_swing25": float(best_e240["overlap_e230_swing25"]),
            "oof_or_train_delta": float(pc10_train["drop_delta_vs_full_per_row"]),
            "oof_or_train_note": "E241 score_pc10 train top10 drop_delta",
        },
    ]
    return pd.DataFrame(rows)


def write_report(
    df: pd.DataFrame,
    corr: pd.DataFrame,
    gate: pd.DataFrame,
    ranks: pd.DataFrame,
    conflicts: pd.DataFrame,
    comparison: pd.DataFrame,
) -> None:
    gate_rate = float(df["e237_gate"].astype(bool).mean())
    gate_n = int(df["e237_gate"].astype(bool).sum())
    n = int(len(df))
    oof_gate_auc = float(corr[(corr["oof_signal"].eq("oof_gain_vs_full")) & (corr["test_signal"].eq("gate_auc"))]["spearman"].iloc[0])
    tail_gate_auc = float(corr[(corr["oof_signal"].eq("oof_tail_auc")) & (corr["test_signal"].eq("gate_auc"))]["spearman"].iloc[0])
    oof_score_corr = float(corr[(corr["oof_signal"].eq("oof_gain_vs_full")) & (corr["test_signal"].eq("e237_score"))]["spearman"].iloc[0])
    top_e237_oof_rank = int(ranks[ranks["rank_by"].eq("oof_gain_vs_full")]["top_e237_rank"].iloc[0])
    top_e237_score_rank = int(ranks[ranks["rank_by"].eq("e237_score")]["top_e237_rank"].iloc[0])
    selected_cols = [
        "rank_by",
        "best_is_gate",
        "best_value",
        "first_selected_rank",
        "top_e237_rank",
        "top_e237_value",
    ]
    corr_view = corr[
        corr["test_signal"].isin(
            ["e237_score", "gate_auc", "test_expected_gain_vs_e224", "adverse_reduction_vs_e224"]
        )
    ].sort_values(["test_signal", "spearman"], ascending=[True, False])
    conflict_cols = [
        "conflict_type",
        "candidate_id",
        "e237_gate",
        "q3_dropped_cells",
        "s4_dropped_cells",
        "oof_gain_vs_full",
        "oof_tail_auc",
        "test_expected_gain_vs_e224",
        "support_gain_vs_e224",
        "e237_score",
    ]
    comparison_cols = [
        "item",
        "source",
        "expected_loss_vs_e224",
        "adverse_reduction_vs_e224",
        "support_gain_vs_e224",
        "actual_adverse_reduction_vs_e224",
        "overlap_e237",
        "overlap_e230_swing25",
        "oof_or_train_delta",
        "oof_or_train_note",
    ]
    lines = [
        "# E242 E237 OOF-to-Test Transfer Audit",
        "",
        "## Question",
        "",
        "Does E237's OOF learned cell policy transfer to test-side materialization geometry, or is the selected file mostly determined by public-free graft/actual stress?",
        "",
        "## Key Numbers",
        "",
        f"- Graft-side materialization rows audited: `{n}`.",
        f"- E237 gate pass rows: `{gate_n}` (`{gate_rate:.6f}`).",
        f"- OOF gain vs E237 score Spearman: `{oof_score_corr:.6f}`.",
        f"- OOF gain gate AUC: `{oof_gate_auc:.6f}`.",
        f"- OOF tail-AUC gate AUC: `{tail_gate_auc:.6f}`.",
        f"- Top E237 file rank by OOF gain: `{top_e237_oof_rank}/{n}`.",
        f"- Top E237 file rank by E237 score: `{top_e237_score_rank}/{n}`.",
        "",
        "## Rank Audit",
        "",
        md_table(ranks, selected_cols, n=20),
        "",
        "## Gate Summary",
        "",
        md_table(gate, n=10),
        "",
        "## OOF/Test Correlation Highlights",
        "",
        md_table(corr_view, n=40),
        "",
        "## Conflict Examples",
        "",
        md_table(conflicts, conflict_cols, n=30),
        "",
        "## E237 vs E240/E241",
        "",
        md_table(comparison, comparison_cols, n=10),
        "",
        "## Decision",
        "",
    ]
    if tail_gate_auc >= 0.85 and oof_gate_auc < 0.60:
        lines.append(
            "- Average OOF loss gain is not a reliable selector, but OOF tail-AUC is strongly aligned with the E237 gate. The transferable object is high-impact Q3 risk-tail discrimination, not mean OOF policy improvement."
        )
    elif oof_gate_auc < 0.60 or abs(oof_score_corr) < 0.20:
        lines.append(
            "- OOF policy quality is not a reliable selector for test materialization quality. E237 should be treated as a public-free stress-selected cell-tail sensor, not as a generally validated learned ranking."
        )
    else:
        lines.append(
            "- OOF policy quality has meaningful transfer to the test materialization gate. E237's learned-cell claim is stronger than a pure graft-stress artifact, but public feedback is still required."
        )
    lines.append(
        "- No submission is created. Do not choose E237 siblings by OOF rank alone; use the pre-registered E237 top file only if the next public question is the learned Q3 decisive-cell world."
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    mat = pd.read_csv(MATERIALIZATION_IN)
    selected = pd.read_csv(SELECTED_IN)
    _ = pd.read_csv(OOF_IN)
    graft = mat[mat["pair_kind"].eq("graft_vs_e154")].copy()
    if graft.empty:
        graft = mat.copy()
    graft = add_directional_scores(graft)
    corr = corr_table(graft)
    gate = gate_summary(graft)
    ranks = rank_audit(graft, selected)
    conflicts = conflict_cases(graft)
    comparison = e240_e241_comparison(selected)
    corr.to_csv(CORR_OUT, index=False)
    gate.to_csv(GATE_OUT, index=False)
    ranks.to_csv(RANK_OUT, index=False)
    conflicts.to_csv(CONFLICT_OUT, index=False)
    comparison.to_csv(COMPARISON_OUT, index=False)
    write_report(graft, corr, gate, ranks, conflicts, comparison)
    print("[E242 summary]")
    print(
        ranks[
            [
                "rank_by",
                "best_is_gate",
                "best_value",
                "first_selected_rank",
                "top_e237_rank",
                "top_e237_value",
            ]
        ].to_string(index=False)
    )
    print("\n[E242 key corr]")
    view = corr[
        corr["test_signal"].isin(["e237_score", "gate_auc"])
        & corr["oof_signal"].isin(["oof_gain_vs_full", "oof_tail_auc", "oof_subject_win_rate"])
    ]
    print(view.sort_values(["test_signal", "oof_signal"]).round(9).to_string(index=False))
    print(f"\nwrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
