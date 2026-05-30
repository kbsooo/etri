#!/usr/bin/env python3
"""E230: public-free support-tail pruning audit for the live E224 JEPA sensor.

E224 is the current JEPA-first public sensor, but E222/E224 still show the
same structural smell that killed E216: expected-good movement with
sub-0.5 hard-label support probability. This audit asks a narrower question:
can we remove or shrink the worst Q3/S4 E224 graft cells using only the
pre-existing public-free prior geometry, while preserving most of the E224
expected body?

The script creates candidate files only for rows that pass a conservative
post-hoc-audit gate. Passing here does not supersede E224 as the first JEPA
public observation because the prune rule is not OOF-learned; it can only
create conditional siblings for after E224 feedback.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, load_sub, logit  # noqa: E402
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402
import e162_branch_readability_flip_thresholds as e162  # noqa: E402
import e222_e211_support_tail_audit as e222  # noqa: E402


E95_FILE = "submission_e95_hardtail_541e3973.csv"
E154_FILE = "submission_e154_s3repair_9f2e2e73.csv"
E224_FILE = "submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv"

SUMMARY_OUT = OUT / "e230_e224_support_tail_prune_audit_summary.csv"
TARGET_OUT = OUT / "e230_e224_support_tail_prune_audit_targets.csv"
SELECTED_OUT = OUT / "e230_e224_support_tail_prune_audit_selected.csv"
TOPCELLS_OUT = OUT / "e230_e224_support_tail_prune_audit_top_cells.csv"
REPORT_OUT = OUT / "e230_e224_support_tail_prune_audit_report.md"

EPS = 1.0e-12


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def load_prob(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    return clip_prob(load_sub(file_name, sample)[TARGETS].to_numpy(dtype=np.float64))


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 30, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return e138.md_table(view.head(n), floatfmt)


def materialize(sample: pd.DataFrame, pred: np.ndarray, variant_id: str) -> str:
    digest = hashlib.sha1(np.round(pred, 10).tobytes()).hexdigest()[:8]
    file_name = f"submission_e230_{variant_id}_{digest}.csv"
    out = sample[KEYS].copy()
    out[TARGETS] = clip_prob(pred)
    out.to_csv(OUT / file_name, index=False)
    return file_name


def variant_specs(cells: pd.DataFrame) -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = []
    q3 = cells[cells["target"].eq("Q3")].copy()
    s4 = cells[cells["target"].eq("S4")].copy()

    def add(name: str, frame: pd.DataFrame, keep_fraction: float, note: str) -> None:
        if frame.empty:
            return
        specs.append(
            {
                "variant_id": name,
                "row_idx": frame["row_idx"].to_numpy(dtype=int),
                "target_idx": frame["target_idx"].to_numpy(dtype=int),
                "keep_fraction": keep_fraction,
                "pruned_cells": int(len(frame)),
                "pruned_q3": int((frame["target"].eq("Q3")).sum()),
                "pruned_s4": int((frame["target"].eq("S4")).sum()),
                "prune_swing": float(frame["swing"].sum()),
                "prune_expected_focus": float(frame["expected_focus"].sum()),
                "prune_adverse_delta": float(frame["adverse_delta"].sum()),
                "prune_support_prob_sw": float(np.average(frame["support_prob_focus"], weights=frame["swing"]))
                if float(frame["swing"].sum()) > EPS
                else np.nan,
                "rule_note": note,
            }
        )

    q3_risk = q3.assign(risk=(0.5 - q3["support_prob_focus"]) * q3["swing"]).sort_values(
        "risk", ascending=False
    )
    q3_swing = q3.sort_values("swing", ascending=False)
    s4_risk = s4.assign(risk=(0.5 - s4["support_prob_focus"]) * s4["swing"]).sort_values(
        "risk", ascending=False
    )
    all_risk = cells.assign(risk=(0.5 - cells["support_prob_focus"]) * cells["swing"]).sort_values(
        "risk", ascending=False
    )

    for k in [1, 3, 5, 8, 13, 21, 34, 55]:
        add(f"q3_risktop{k}_drop", q3_risk.head(k), 0.0, f"drop top {k} Q3 cells by low-support swing risk")
        add(f"q3_risktop{k}_shrink50", q3_risk.head(k), 0.5, f"halve top {k} Q3 cells by low-support swing risk")
    for k in [1, 3, 5, 10, 25]:
        add(f"q3_swingtop{k}_drop", q3_swing.head(k), 0.0, f"drop top {k} Q3 swing cells")
        add(f"q3_swingtop{k}_shrink50", q3_swing.head(k), 0.5, f"halve top {k} Q3 swing cells")

    for thr in [0.42, 0.45, 0.47, 0.50]:
        add(
            f"q3_support_lt_{str(thr).replace('.', 'p')}_drop",
            q3[q3["support_prob_focus"] < thr],
            0.0,
            f"drop Q3 cells with support probability below {thr}",
        )
        add(
            f"q3_support_lt_{str(thr).replace('.', 'p')}_shrink50",
            q3[q3["support_prob_focus"] < thr],
            0.5,
            f"halve Q3 cells with support probability below {thr}",
        )

    add("q3_expected_positive_drop", q3[q3["expected_focus"] > 0], 0.0, "drop Q3 expected-positive cells")
    add(
        "q3_expected_positive_shrink50",
        q3[q3["expected_focus"] > 0],
        0.5,
        "halve Q3 expected-positive cells",
    )
    add(
        "s4_risktop5_shrink50",
        s4_risk.head(5),
        0.5,
        "halve top 5 S4 low-support swing-risk cells",
    )
    add(
        "all_risktop10_shrink50",
        all_risk.head(10),
        0.5,
        "halve top 10 Q3/S4 low-support swing-risk cells",
    )
    add(
        "all_risktop10_drop",
        all_risk.head(10),
        0.0,
        "drop top 10 Q3/S4 low-support swing-risk cells",
    )

    dedup: dict[tuple[str, float, tuple[tuple[int, int], ...]], dict[str, Any]] = {}
    for spec in specs:
        key = (
            str(spec["variant_id"]),
            float(spec["keep_fraction"]),
            tuple(zip(spec["row_idx"].tolist(), spec["target_idx"].tolist())),
        )
        dedup[key] = spec
    return list(dedup.values())


def apply_variant(e224: np.ndarray, anchor: np.ndarray, spec: dict[str, Any]) -> np.ndarray:
    out_logit = logit(e224).copy()
    anchor_logit = logit(anchor)
    rows = spec["row_idx"]
    targets = spec["target_idx"]
    keep = float(spec["keep_fraction"])
    out_logit[rows, targets] = anchor_logit[rows, targets] + keep * (
        logit(e224)[rows, targets] - anchor_logit[rows, targets]
    )
    return clip_prob(sigmoid(out_logit))


def audit_variant(
    sample: pd.DataFrame,
    priors: dict[str, np.ndarray],
    e95: np.ndarray,
    e154: np.ndarray,
    pred: np.ndarray,
    meta: dict[str, Any],
) -> tuple[list[dict[str, Any]], pd.DataFrame]:
    spec = e222.Candidate(
        candidate_id=str(meta["variant_id"]),
        file_name=str(meta["variant_id"]),
        anchor_file=E154_FILE,
        family="e230_e224_support_tail_prune",
        status="generated",
        note=str(meta["rule_note"]),
    )
    rows: list[dict[str, Any]] = []
    target_parts: list[pd.DataFrame] = []
    for pair_kind, base_name, base in [
        ("graft_vs_e154", E154_FILE, e154),
        ("actual_vs_e95", E95_FILE, e95),
    ]:
        rec, tgt, _ = e222.pair_audit(spec, pair_kind, pred, base, base_name, priors, sample)
        rec.update(meta)
        rows.append(rec)
        if not tgt.empty:
            tgt = tgt.copy()
            for key, value in meta.items():
                if key not in {"row_idx", "target_idx"}:
                    tgt[key] = value
            target_parts.append(tgt)
    return rows, pd.concat(target_parts, ignore_index=True) if target_parts else pd.DataFrame()


def add_comparison_metrics(summary: pd.DataFrame, target_df: pd.DataFrame, base_row: pd.Series) -> pd.DataFrame:
    out = e222.add_ranking(summary.copy())
    q3 = target_df[target_df["pair_kind"].eq("graft_vs_e154") & target_df["target"].eq("Q3")][
        ["candidate_id", "top1_over_abs_expected", "adverse_delta", "expected_focus", "support_prob_focus_swing_weighted"]
    ].rename(
        columns={
            "top1_over_abs_expected": "q3_top1_over_abs_expected",
            "adverse_delta": "q3_adverse_delta",
            "expected_focus": "q3_expected_focus",
            "support_prob_focus_swing_weighted": "q3_support_prob_focus_swing_weighted",
        }
    )
    s4 = target_df[target_df["pair_kind"].eq("graft_vs_e154") & target_df["target"].eq("S4")][
        ["candidate_id", "expected_focus", "adverse_delta", "support_prob_focus_swing_weighted"]
    ].rename(
        columns={
            "expected_focus": "s4_expected_focus",
            "adverse_delta": "s4_adverse_delta",
            "support_prob_focus_swing_weighted": "s4_support_prob_focus_swing_weighted",
        }
    )
    out = out.merge(q3, on="candidate_id", how="left").merge(s4, on="candidate_id", how="left")
    graft = out["pair_kind"].eq("graft_vs_e154")
    for col in ["expected_focus", "adverse_delta", "support_prob_focus_swing_weighted", "top1_over_abs_expected"]:
        out[f"{col}_vs_e224"] = out[col] - float(base_row[col])
    out["adverse_reduction_vs_e224"] = float(base_row["adverse_delta"]) - out["adverse_delta"]
    out["expected_loss_vs_e224"] = out["expected_focus"] - float(base_row["expected_focus"])
    out["support_gain_vs_e224"] = out["support_prob_focus_swing_weighted"] - float(
        base_row["support_prob_focus_swing_weighted"]
    )
    out["e230_gate"] = False
    out.loc[graft, "e230_gate"] = (
        (out.loc[graft, "expected_focus"] <= -0.000580)
        & (out.loc[graft, "expected_loss_vs_e224"] <= 0.000045)
        & (out.loc[graft, "adverse_reduction_vs_e224"] >= 0.000120)
        & (out.loc[graft, "support_gain_vs_e224"] >= 0.0020)
        & (out.loc[graft, "q3_adverse_delta"].fillna(9.0) <= 0.00205)
        & (out.loc[graft, "q3_top1_over_abs_expected"].fillna(9.0) <= 0.82)
        & (out.loc[graft, "pruned_cells"] <= 25)
    )
    out["e230_score"] = (
        -out["expected_loss_vs_e224"].fillna(0.0) * 2500.0
        +out["adverse_reduction_vs_e224"].fillna(0.0) * 1400.0
        +out["support_gain_vs_e224"].fillna(0.0) * 0.50
        -np.maximum(out["q3_top1_over_abs_expected"].fillna(9.0) - 0.78, 0.0) * 0.08
        -np.maximum(out["pruned_cells"].fillna(0.0) - 13, 0.0) * 0.001
    )
    return out


def write_report(summary: pd.DataFrame, target_df: pd.DataFrame, selected: pd.DataFrame, top_cells: pd.DataFrame) -> None:
    graft = summary[summary["pair_kind"].eq("graft_vs_e154")].sort_values(
        ["e230_gate", "e230_score"], ascending=[False, False]
    )
    actual = summary[summary["pair_kind"].eq("actual_vs_e95")].sort_values(
        ["e230_gate", "e230_score"], ascending=[False, False]
    )
    target_view = target_df[target_df["pair_kind"].eq("graft_vs_e154")].sort_values(
        ["candidate_id", "target"]
    )
    cols = [
        "candidate_id",
        "variant_id",
        "keep_fraction",
        "pruned_cells",
        "pruned_q3",
        "pruned_s4",
        "expected_focus",
        "expected_loss_vs_e224",
        "adverse_delta",
        "adverse_reduction_vs_e224",
        "support_prob_focus_swing_weighted",
        "support_gain_vs_e224",
        "q3_top1_over_abs_expected",
        "q3_adverse_delta",
        "e230_gate",
        "e230_score",
        "submission_file",
    ]
    target_cols = [
        "candidate_id",
        "target",
        "moved_cells",
        "expected_focus",
        "adverse_delta",
        "support_prob_focus_swing_weighted",
        "top1_over_abs_expected",
    ]
    top_cols = [
        "target",
        "row_idx",
        "subject_id",
        "p_base",
        "p_new",
        "logit_delta",
        "swing",
        "expected_focus",
        "support_prob_focus",
    ]
    lines = [
        "# E230 E224 Support-Tail Prune Audit",
        "",
        "## Question",
        "",
        "Can public-free support-tail geometry prune the fragile part of E224 without destroying the Q3/S4 JEPA body?",
        "",
        "## Graft vs E154",
        "",
        md_table(graft, cols, n=40),
        "",
        "## Actual vs E95",
        "",
        md_table(actual, cols, n=20),
        "",
        "## Target Breakdown",
        "",
        md_table(target_view, target_cols, n=50),
        "",
        "## Original E224 Top Graft Cells",
        "",
        md_table(top_cells.sort_values("swing", ascending=False), top_cols, n=20),
        "",
        "## Selected Conditional Siblings",
        "",
        md_table(selected, cols, n=10),
        "",
        "## Decision",
        "",
    ]
    if selected.empty:
        lines.append(
            "- No support-tail prune passed the E230 conditional-sibling gate. E224 remains the JEPA-first sensor, and pruning is not currently justified before public feedback."
        )
    else:
        best = selected.iloc[0]
        lines.append(
            f"- Best conditional E224 sibling: `{best['submission_file']}` from rule `{best['variant_id']}`."
        )
        lines.append(
            "- This does not replace E224 as the first JEPA public sensor because the prune rule is not OOF-learned. It is a post-E224 attribution sibling if E224 small-loses by Q3 tail."
        )
    lines.append("")
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    priors = e162.prior_arrays(sample)
    e95 = load_prob(E95_FILE, sample)
    e154 = load_prob(E154_FILE, sample)
    e224 = load_prob(E224_FILE, sample)

    base_spec = e222.Candidate(
        candidate_id="e224_original",
        file_name=E224_FILE,
        anchor_file=E154_FILE,
        family="e224_q3_scale_pareto",
        status="baseline",
        note="Current JEPA-first E224 candidate.",
    )
    base_rec, base_tgt, base_top = e222.pair_audit(
        base_spec, "graft_vs_e154", e224, e154, E154_FILE, priors, sample
    )
    base_row = pd.Series(base_rec)
    cells = e222.cell_table(base_spec, "graft_vs_e154", e224, e154, E154_FILE, priors, sample)
    specs = variant_specs(cells)

    summary_rows: list[dict[str, Any]] = []
    target_parts: list[pd.DataFrame] = []
    pred_cache: dict[str, np.ndarray] = {}
    for spec in specs:
        pred = apply_variant(e224, e154, spec)
        pred_cache[str(spec["variant_id"])] = pred
        rows, targets = audit_variant(sample, priors, e95, e154, pred, spec)
        summary_rows.extend(rows)
        if not targets.empty:
            target_parts.append(targets)

    summary = pd.DataFrame(summary_rows)
    target_df = pd.concat(target_parts, ignore_index=True) if target_parts else pd.DataFrame()
    target_df = e222.add_ranking(target_df) if not target_df.empty else pd.DataFrame()
    summary = add_comparison_metrics(summary, target_df, base_row) if not summary.empty else pd.DataFrame()
    selected = summary[
        summary["pair_kind"].eq("graft_vs_e154") & summary["e230_gate"].fillna(False).astype(bool)
    ].sort_values(["e230_score", "expected_focus"], ascending=[False, True]).head(3).copy()
    files: list[str] = []
    for row in selected.itertuples(index=False):
        files.append(materialize(sample, pred_cache[str(row.variant_id)], str(row.variant_id)))
    if not selected.empty:
        selected["submission_file"] = files
        summary = summary.merge(selected[["variant_id", "submission_file"]], on="variant_id", how="left")
    else:
        summary["submission_file"] = ""
        selected["submission_file"] = ""

    summary = summary.sort_values(["pair_kind", "e230_gate", "e230_score"], ascending=[True, False, False])
    target_df = target_df.sort_values(["pair_kind", "candidate_id", "target"]) if not target_df.empty else target_df
    summary.to_csv(SUMMARY_OUT, index=False)
    target_df.to_csv(TARGET_OUT, index=False)
    selected.to_csv(SELECTED_OUT, index=False)
    base_top.to_csv(TOPCELLS_OUT, index=False)
    write_report(summary, target_df, selected, base_top)

    cols = [
        "variant_id",
        "keep_fraction",
        "pruned_cells",
        "expected_focus",
        "expected_loss_vs_e224",
        "adverse_reduction_vs_e224",
        "support_gain_vs_e224",
        "q3_top1_over_abs_expected",
        "q3_adverse_delta",
        "e230_gate",
        "submission_file",
    ]
    print("[E230 selected]")
    print(selected[cols].round(9).to_string(index=False) if not selected.empty else "none")
    print(f"\nwrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
